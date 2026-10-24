# Cancelled macOS run 40064483490: actual log evidence

Repository: R347H4CK3R/madeira-cod-test; source 7c4771a512f83c46b09434df7c37c836dc3085df.
Build job 120784751069 was cancelled after the LLVM cache save, during DXMT.
Full decoded log: build-120784751069.log (1,224,830 characters).

Outer build stages used `/bin/bash -e {0}`, without pipefail. The `script | tee`
pipeline masked two child failures. Step conclusions alone are not build proof.

Actual successful evidence:

- FFmpeg/GnuTLS/FreeType builds completed; FreeType archive path printed at05:06:40.
- Complete native and ARM64EC Wine headers generated; execution reached native compilation.
- ntdll unix: 37 succeeded,0 failed; archive2,068,040bytes.
- wineserver: full base sources compiled, patched objects replaced, all-object
  collision-symbol rename completed; archive1,285,680bytes.
- win32u unix:46 succeeded,0 failed; real FreeType merged; archive3,483,752bytes.
- Patched ARM64EC ntdll: stripped1,179,648 + pad393,216 =1,572,864bytes;
  SizeOfImage1,245,184 +0x50000. DLL copy/pad completed.
- Locked Rust pairing release build completed; libmadeira_rppairing.a staged.
- LLVM host tablegen and73 iOS static libraries linked. All34 libraries named
  in pinned dxmt/src/airconv/meson.build's llvm_deps occur in successful static
  link lines. iOS link command confirms arm64, SDK26.2 and deployment17.0.

First actual failure: FEX CMake configure05:10:57. Default TUNE_CPU=native calls
Linux /proc/cpuinfo detection; packaging/pkg_resources imports fail, leaving an
empty AARCH64_CPU and CMake string(STRIP) missing its input. A second detector
raises FileNotFoundError /proc/cpuinfo. No FEX archives were built. Minimal
source-preserving correction: configure with TUNE_ARCH=generic,TUNE_CPU=none;
this bypasses both unsuitable native Linux CPU probes. No FEX source edits.

Second actual failure: LLVM all-target build05:32:56 links extra tools/lto
libLTO.dylib with ELF-only `-Wl,-z,defs`; Apple ld rejects `-z`. Required static
libs already linked. `LLVM_INCLUDE_TOOLS=OFF` is the correct CMake boundary;
LLVM_BUILD_TOOLS=OFF alone still generates tools targets. Source confirmed from
LLVM15.0.7 CMakeLists627/1144. INCLUDE_EXAMPLES=OFF also excludes unwanted
example targets. Partial cache must not be treated as a completed all build.

LLVM checkpoint saved (433,016,698bytes compressed):

`madeira-llvm15-macOS-ARM64-23C57-81e3099a88332315cf7f7377d4ef106ce79cb39befcf1c6a2ecd3904e1d03da4-8dfdcc7b7`

SDK build23C57, runnerARM64, LLVM15.0.7 source8dfdcc7b7; iOS minimum17.0.
Parent decides whether to reuse these genuine older-SDK static libraries with
newer Xcode after architecture/platform/input validation.

Third incomplete stage: DXMT airconv_context object FAILED05:34:09. Other
airconv/converter/winemetal/native objects compiled successfully before the
cancellation. Error details are in artifact build/dxmt-ios/obj/airconv_context.err;
not included verbatim in full job log. Local artifact inspection confirms the
exact error is missing air_msad.h at airconv_context.cpp29. Pinned Meson source
generates air_msad/air_samplepos/air_tessellation AIR bitcode with Metal3.1,
air64-apple-macos14.0, then xxd headers. The handwritten iOS script omitted that
generation. Approved fix now adds the exact generator chain before C++ compile;
no DXMT source/gitlink edits. No combined DXMT archive was produced in this run.

Build evidence artifact12549572926,207,502bytes,
SHA25609a624990c3a409548e6c4ad3ebd6f54aee53cd7805a87cc9ccbc5111f9d7b0b.
Direct HTTP download of its signed file host is policy-blocked403. Parent
materialized the connector's Sediment-backed file reference through the normal
download_file tool, verified the checksum and extracted it at
/workspace/ci-current/evidence. This resolves artifact access without changing
the cloud network policy.

Dock/Microsoft runtime extraction/final app/package were not reached.
Independent parent probe confirms selected Xcode26.3/Swift6.2.4 cannot import
the pinned Swift6.4 StikJIT framework. A newer toolchain is required.
