# DXMT public Metal atomic repair: actual compiler verification

Probe source commit:64c8b43a3ef763d10725ec7959b430253e5dc4cc,
branchfix/metal-atomic-20261024, base dab7f562086485ab5df274e09cbaef7f72bc5d9d.
Run:https://github.com/R347H4CK3R/madeira-cod-test/actions/runs/40072320821
Job120808236223 completed successfully.

Toolchain:Xcode27.2 build27B48, Apple Metal32023.922(metalfe32023.922.4).
Pinned DXMT35a4db11bd1bda380c5176a3bc6c1878f7192101 is unchanged.
All shader commands use Metal3.1 and air64-apple-macos14.0, matching pinned Meson.

The complete original air_tessellation.metal reproduces the actual error:
private __metal_atomic_fetch_add_explicit expects5arguments but receives4.
The external one-call patch selects public atomic_fetch_add_explicit on the
same threadgroup int pointer cast to threadgroup atomic_int, operand1,
memory_order_relaxed. All three complete shaders compile after that patch:
air_msad,air_samplepos,air_tessellation. Their actual AIR files and generated
headers are in the verified artifact.

Installed Apple metal_atomic header lines2004–2006 shows the public threadgroup
overload forwards T(operand),int(order),__METAL_MEMORY_SCOPE_THREADGROUP__,
__METAL_MEMORY_FLAGS_NONE__ to the underlying compiler intrinsic. This is the
same explicit threadgroup scope requested by the old private call.

Actual emitted AIR IR(scope-probe.ll lines8–16) is:

```
%2 = tail call i32 @air.atomic.local.add.s.i32(i32 addrspace(3)* nocapture %0, i32 1, i32 0, i32 1, i1 true)
ret i32 %2
...
%3 = tail call i32 @air.atomic.local.add.s.i32(i32 addrspace(3)* nocapture %0, i32 1, i32 0, i32 1, i1 true)
store i32 %3, i32 addrspace(1)* %1, align 4
```

This confirms signed32-bit storage, unchanged threadgroup address-space3
pointer, add1, relaxed order0, threadgroup scope1. The helper returns the exact
atomic result and the probe kernel stores that result without adjustment.
Together with public fetch_add's old-value contract, the returned allocation
index is preserved. An independent agent reviewed this actual IR/header evidence
and verified all AIR checksums; no blocker was found.

Artifact12552085815,126104bytes,
SHA256afae7b3a02948484a1738e3c68b070181f146e490e7d57277417c6906eae5b06.
Verified/extracted directory:/workspace/ci-current/metal-atomic-evidence.
Full log:/workspace/ci-current/metal-probe-120808236223.log.

Only the probe branch was committed/pushed. Root/host worktrees were untouched.
build/ci/build-ios.sh is byte-identical to base, SHA256
da405ff9c50aaf112d834d7a9129b8137e82aa70fdd6670dc17339166863beb9,
so the completed LLVM checkpoint key remains valid. The build adapter records
actual DXMT patch provenance to build/ci-output/dxmt-build.patch.

This verifies source/compiler behavior. No GPU execution or iOS/COD launch was
performed, and full native app linking/packaging is still the integration gate.
