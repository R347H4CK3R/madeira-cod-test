#!/usr/bin/env python3
"""Extract unmodified Microsoft x64 runtime DLLs from the official redist.

Burn's .wixburn metadata locates its UX and attached cabinets independently;
7-Zip's automatic EXE opening sees only the first cabinet. Nested MSI/cabinet
payloads may use internal file identifiers. OriginalFilename in the PE version
resource restores their shipped names. DLL bytes are never rewritten.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile

NAMES = set('''concrt140.dll msvcp140.dll msvcp140_1.dll msvcp140_2.dll
msvcp140_atomic_wait.dll msvcp140_codecvt_ids.dll vcamp140.dll vccorlib140.dll
vcomp140.dll vcruntime140.dll vcruntime140_1.dll vcruntime140_threads.dll'''.split())
CORE = {'vcruntime140.dll', 'vcruntime140_1.dll', 'msvcp140.dll'}


def burn_containers(data):
    """Locate WiX 3 Burn v2 CABs using the PE section's declared boundaries.

    Format/engine-signature rules are defined by WiX's BurnCommon.Initialize:
    https://github.com/wixtoolset/wix3/blob/develop/src/tools/wix/BurnCommon.cs
    A signed engine ends AFTER its original signature. The current whole-bundle
    signature may follow the attached CAB and is not the attached CAB's offset.
    """
    def require_range(offset, size, label):
        if offset < 0 or size < 0 or offset > len(data) or size > len(data) - offset:
            raise ValueError(f'Truncated Burn {label}: range {offset}+{size} is out of bounds')

    def u16(offset):
        require_range(offset, 2, 'header')
        return struct.unpack_from('<H', data, offset)[0]

    def u32(offset):
        require_range(offset, 4, 'header')
        return struct.unpack_from('<I', data, offset)[0]

    require_range(0, 64, 'DOS header')
    if data[:2] != b'MZ':
        raise ValueError('Burn installer has no DOS MZ header')
    pe = u32(0x3c)
    require_range(pe, 24, 'PE header')
    if data[pe:pe + 4] != b'PE\0\0':
        raise ValueError('Burn installer has no PE header')
    sections, optional_size = u16(pe + 6), u16(pe + 20)
    optional = pe + 24
    require_range(optional, optional_size, 'optional header')
    directory_offset = {0x10b: 96, 0x20b: 112}.get(u16(optional))
    if directory_offset is None or optional_size < directory_offset + 16 * 8:
        raise ValueError('Unsupported or truncated Burn PE optional header')
    signature_offset, signature_size = u32(optional + directory_offset + 32), u32(optional + directory_offset + 36)
    if bool(signature_offset) != bool(signature_size):
        raise ValueError('Inconsistent Burn bundle signature range')
    require_range(signature_offset, signature_size, 'bundle signature')
    section_table = optional + optional_size
    require_range(section_table, sections * 40, 'section table')
    raw_end = section_table + sections * 40
    burn_sections = []
    for index in range(sections):
        section = section_table + index * 40
        size, offset = u32(section + 16), u32(section + 20)
        if size:
            require_range(offset, size, 'PE section')
            raw_end = max(raw_end, offset + size)
        if data[section:section + 8] == b'.wixburn':
            if size < 56:
                raise ValueError('Truncated .wixburn section')
            burn_sections.append(offset)
    if len(burn_sections) != 1:
        raise ValueError('Burn installer must contain exactly one .wixburn section')
    burn = burn_sections[0]
    if u32(burn) != 0x00f14300 or u32(burn + 4) != 2 or u32(burn + 40) != 1:
        raise ValueError('Unsupported Burn metadata magic, version or CAB format')
    stub, original_offset, original_size = u32(burn + 24), u32(burn + 32), u32(burn + 36)
    count, ux_size, attached_size = u32(burn + 44), u32(burn + 48), u32(burn + 52)
    if count not in (1, 2) or not ux_size or (count == 2) != bool(attached_size):
        raise ValueError('Unsupported Burn container count or sizes')
    if stub < raw_end:
        raise ValueError('Burn UX container overlaps the PE sections')
    require_range(stub, ux_size, 'UX container')
    ux_end = stub + ux_size
    if bool(original_offset) != bool(original_size):
        raise ValueError('Inconsistent Burn original engine signature range')
    if original_offset:
        if original_offset < ux_end:
            raise ValueError('Burn original engine signature overlaps the UX container')
        require_range(original_offset, original_size, 'original engine signature')
    engine_end = original_offset + original_size if original_offset else ux_end
    spans = [('ux', stub, ux_size)]
    if count == 2:
        spans.append(('attached', engine_end, attached_size))
    result = []
    for name, offset, size in spans:
        require_range(offset, size, f'{name} container')
        if size < 36 or data[offset:offset + 4] != b'MSCF' or u32(offset + 8) != size:
            raise ValueError(f'Burn {name} CAB header/size does not match its container metadata')
        result.append({'name': name, 'offset': offset, 'size': size,
                       'sha256': hashlib.sha256(data[offset:offset + size]).hexdigest()})
    return result


def signed_x64(data):
    try:
        pe = struct.unpack_from('<I', data, 0x3c)[0]
        if data[:2] != b'MZ' or data[pe:pe+4] != b'PE\0\0':
            return False
        if struct.unpack_from('<H', data, pe+4)[0] != 0x8664:
            return False
        if struct.unpack_from('<H', data, pe+24)[0] != 0x20b:
            return False
        off, size = struct.unpack_from('<II', data, pe+24+112+4*8)
        return size >= 8 and off > 0 and off+size <= len(data)
    except struct.error:
        return False


def original_name(data):
    key = 'OriginalFilename\0'.encode('utf-16le')
    start = data.find(key)
    if start < 0:
        return None
    start = (start+len(key)+3) & ~3
    end = start
    while end+1 < len(data) and data[end:end+2] != b'\0\0':
        end += 2
    try:
        return data[start:end].decode('utf-16le').lower()
    except UnicodeDecodeError:
        return None


def validate_folder(destination):
    result = {}
    for path in destination.iterdir() if destination.is_dir() else []:
        if path.name.lower() not in NAMES:
            continue
        data = path.read_bytes()
        if not signed_x64(data):
            raise ValueError(f'Not an intact signed x64 Microsoft runtime: {path}')
        result[path.name.lower()] = hashlib.sha256(data).hexdigest()
    if missing := CORE-result.keys():
        raise ValueError('Missing Microsoft x64 runtime inputs: '+', '.join(sorted(missing)))
    return result


def extract(installer, destination):
    executable = shutil.which('7zz')
    if not executable:
        raise ValueError('7zz is required to extract VC_redist.x64.exe')
    destination.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='madeira-vcredist-') as folder:
        root = Path(folder)

        def unpack(path, target):
            subprocess.run([executable, 'x', '-y', str(path.resolve()), '-o'+str(target)], check=True)

        data = installer.read_bytes()
        seen = set()
        for container in burn_containers(data):
            print('Burn container: ' + json.dumps(container, sort_keys=True), flush=True)
            path = root / (container['name'] + '.cab')
            start = container['offset']
            path.write_bytes(data[start:start + container['size']])
            seen.add(container['sha256'])
            unpack(path, root / container['name'])
        for _ in range(6):
            containers = []
            for path in root.rglob('*'):
                if not path.is_file():
                    continue
                with path.open('rb') as file:
                    magic = file.read(8)
                if not (magic.startswith(b'MSCF') or magic == bytes.fromhex('d0cf11e0a1b11ae1')):
                    continue
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                if digest not in seen:
                    seen.add(digest)
                    containers.append((path, root/('payload-'+digest)))
            if not containers:
                break
            for path, target in containers:
                unpack(path, target)

        candidates = {}
        for path in root.rglob('*'):
            if not path.is_file():
                continue
            with path.open('rb') as file:
                if file.read(2) != b'MZ':
                    continue
            data = path.read_bytes()
            if not signed_x64(data):
                continue
            name = path.name.lower()
            if name not in NAMES:
                name = original_name(data)
            if name not in NAMES:
                continue
            digest = hashlib.sha256(data).hexdigest()
            if name in candidates and candidates[name][0] != digest:
                raise ValueError(f'Redist contains different signed binaries named {name}; select the intended version explicitly')
            candidates[name] = digest, path
        for name, (_, path) in candidates.items():
            shutil.copyfile(path, destination/name)
    return validate_folder(destination)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path)
    parser.add_argument('--installer', type=Path)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = extract(args.installer, args.destination) if args.installer else validate_folder(args.destination)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'VC runtime input failure: {error}\n')
    args.report.write_text(json.dumps(result, indent=2)+'\n')
    print('Staged unmodified Microsoft x64 runtime DLLs: '+', '.join(sorted(result)))


if __name__ == '__main__':
    main()
