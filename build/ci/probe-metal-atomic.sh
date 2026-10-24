#!/bin/bash
# Real Metal compiler regression for the pinned DXMT tessellation shader.
set -euo pipefail
R="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$R"
OUT="$R/build/metal-atomic-probe"
DXMT="$R/dxmt"
PATCH="$R/build/patches/dxmt-metal-public-atomic.patch"
mkdir -p "$OUT"

xcodebuild -version | tee "$OUT/xcode.txt"
git rev-parse HEAD > "$OUT/source-revision.txt"
git -C "$DXMT" rev-parse HEAD > "$OUT/dxmt-revision.txt"
git -C "$DXMT" diff --exit-code
if ! xcrun -sdk macosx metal --version > "$OUT/metal-version.txt" 2>&1; then
    xcodebuild -downloadComponent MetalToolchain
    xcrun -sdk macosx metal --version > "$OUT/metal-version.txt" 2>&1
fi
cat "$OUT/metal-version.txt"

TESS="$DXMT/src/airconv/shaders/air_tessellation.metal"
FLAGS=(-sdk macosx metal -std=metal3.1 --target=air64-apple-macos14.0)
if xcrun "${FLAGS[@]}" -o "$OUT/original.air" -c "$TESS" > "$OUT/original.log" 2>&1; then
    echo "Original private four-argument builtin unexpectedly compiled" >&2
    exit 1
fi
python3 - "$OUT/original.log" <<'PY'
from pathlib import Path
import sys
text = Path(sys.argv[1]).read_text()
assert '__metal_atomic_fetch_add_explicit' in text, text
assert 'too few arguments' in text and 'expected 5, have 4' in text, text
print('RED: full original shader reproduces private builtin arity failure')
PY

git -C "$DXMT" apply --check "$PATCH"
git -C "$DXMT" apply "$PATCH"
git -C "$DXMT" diff > "$OUT/dxmt-build.patch"
for shader in air_msad air_samplepos air_tessellation; do
    xcrun "${FLAGS[@]}" -o "$OUT/$shader.air" -c "$DXMT/src/airconv/shaders/$shader.metal"
    xxd -n "$shader" -i "$OUT/$shader.air" "$OUT/$shader.h"
    test -s "$OUT/$shader.air"
    test -s "$OUT/$shader.h"
    echo "GREEN: full $shader Metal3.1/macOS14 shader compiled"
done

# Compile the actual patched function into a kernel that stores its return
# value. Keep textual AIR IR for verification of address space/order/scope and
# the returned index. This is compiler evidence, not a GPU execution test.
python3 - "$TESS" "$OUT/scope-probe.metal" <<'PY'
from pathlib import Path
import sys
source = Path(sys.argv[1]).read_text()
start = source.index('int\nget_next_index(threadgroup int *out_count)')
function = source[start:source.index('\n}', start)+2]
Path(sys.argv[2]).write_text('#include <metal_stdlib>\nusing namespace metal;\n' + function + '''
kernel void scope_probe(threadgroup int *counter [[threadgroup(0)]], device int *result [[buffer(0)]]) {
    result[0] = get_next_index(counter);
}
''')
PY
xcrun "${FLAGS[@]}" -O2 -S -emit-llvm -o "$OUT/scope-probe.ll" "$OUT/scope-probe.metal"
test -s "$OUT/scope-probe.ll"
python3 - "$OUT/scope-probe.ll" <<'PY'
from pathlib import Path
import sys
text = Path(sys.argv[1]).read_text()
lines = [line for line in text.splitlines() if 'atomic' in line or 'addrspace(3)' in line or 'store i32' in line]
assert lines, 'No atomic/address-space IR emitted'
print('Actual compiler AIR IR for scope/return-value review:')
print('\n'.join(lines))
PY

# Capture relevant installed SDK declarations when available, without copying
# the complete SDK. The emitted IR above remains the direct compiler evidence.
if xcrun -sdk macosx metal -print-resource-dir > "$OUT/resource-dir.txt" 2> "$OUT/resource-dir.err"; then
python3 - "$OUT/resource-dir.txt" "$OUT/atomic-header-excerpts.txt" <<'PY'
from pathlib import Path
import sys
resource = Path(Path(sys.argv[1]).read_text().strip())
root = resource.parents[2]
excerpts = []
for path in root.rglob('metal_atomic*'):
    if not path.is_file():
        continue
    lines = path.read_text(errors='replace').splitlines()
    selected = set()
    for i, line in enumerate(lines):
        if 'atomic_fetch_add_explicit' in line or '__METAL_MEMORY_SCOPE_THREADGROUP__' in line:
            selected.update(range(max(0, i-4), min(len(lines), i+8)))
    if selected:
        excerpts.append(str(path) + '\n' + '\n'.join(f'{i+1}: {lines[i]}' for i in sorted(selected)))
Path(sys.argv[2]).write_text('\n\n'.join(excerpts))
print(f'Captured relevant atomic declarations from {len(excerpts)} installed headers')
PY
fi
shasum -a 256 "$OUT"/*.air > "$OUT/air-sha256.txt"
echo 'Metal compiler probe complete; GPU execution was not performed.'
