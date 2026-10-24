# Madeira COD test IPA delivery

A genuine Xcode Debug iOS application was built and structurally validated. Call of Duty launch and gameplay remain untested.

- Download: https://github.com/R347H4CK3R/madeira-cod-test/actions/runs/40136648223/artifacts/12577861712
- Successful Actions run: https://github.com/R347H4CK3R/madeira-cod-test/actions/runs/40136648223
- Exact build source: c477bb93db0120490d4cee382702227dd9d76061
- File inside the artifact ZIP: Madeira-COD-Fix-Test.ipa
- Version0.1.3, build5; ARM64 iOS device executable.
- IPA size:84,876,269bytes (80.94MiB).
- IPA SHA256:f375a8c4d1088df0f9e89fb914874a59b9bb7a93d3959aa4305fb1eb93dc2f89
- Artifact ZIP size:83,745,288bytes; SHA256:207de29ea360ea6edae415abb075e59e024a171384f560a65fa5f84a4590f769.
- Artifact expiry:2026-11-07. A GitHub login may be required for the Actions download.

The IPA was also downloaded through the authorized laptop's normal GitHub credential broker into Downloads/Madeira COD Test c477bb9 78899427. Credentials stayed in memory and were not forwarded to the artifact storage redirect. The artifact ZIP and extracted IPA were independently hashed on Windows; both match the values above. No previous build or personal file was overwritten.

## Build and validation evidence

Both jobs in the final run completed successfully. Xcode emitted BUILD SUCCEEDED. Native stages built Wine, patched ARM64EC ntdll, FEX, pairing, complete DXMT/graphics and Dock, using the completed SDK-matched LLVM/media caches. All20 linked static archive checks report ARM64.

The final IPA validator checked ZIP integrity and paths, the application and helper Mach-O images, StikJIT and Metal converter dylibs, Wine/ARM64EC runtime PE files, all12 Microsoft x64 runtimes, the actual prefix registries/system32 tree, NLS data and bundle identities. All28 selected staged-source resource hashes match; no optional VC runtime is missing. Full report: [actual IPA validation JSON](cod-ipa-validation.json).

Independent Windows inspection of the downloaded IPA found383 entries and verified ARM64 iOS device Mach-O headers/load commands and executable segments for all5 important native images: Madeira, Madeira.debug.dylib, MadeiraJITHelper, StikJIT and libmetalirconverter. This includes the actual application code in Xcode's Debug companion dylib, not just the executable launcher.

Final Linux CI ran49/49 selected check scripts successfully, with51 discovered and2 explicitly delegated Apple scripts. The FEX regression reproduces the three original diagnostic failures, then verifies patched native/producer variants. The two Apple scripts previously passed their22JIT-network and27Steam-Cloud cases on the unchanged relevant source. The separate real-installer probe passed16 extraction/architecture checks; the IPA-validator suite passed23 fixtures; pairing Rust tests passed5. Actual Windows generated-batch status validation also passed. The optional staged ARM64EC Dockhost service-connection and real-MP3 fixture remain untested. No test failure remains in the final CI run; historical failures are preserved in earlier reports.

Final build evidence artifact12577621895:480,597bytes, SHA256ff3348a4a8b8c32633d0682a29f7d1983c3f4523db2cbc1e1002cfde323d2afc. Final host artifact12576991339:66,228bytes, SHA256b6ef3c7eabc97b7c1e11e323e2a0e4de8b857705a27bbf9211557c6ded19bbb8. Both diagnostic archives were downloaded into the cloud workspace, their hashes checked and reports inspected. Xcode result artifact12577526940 is also retained by Actions.

## Changes and runtime status

The loader patch scopes translator-bootstrap dependencies to the native sysx64/system32 path so the application's x64 ucrtbase cannot run natively before FEX is ready. Behavioral tests cover both native search locations, missing-native failure and ordinary application-local ordering. Exact crash bytes and the MODULE_InitDLL caller support this correction, but the original full iPhone IPA identity and on-device confirmation remain outstanding: [runtime investigation](cod-runtime-investigation.md).

Build repairs include complete Wine headers/base wineserver, compatible Xcode27/StikJIT tooling, generic FEX build tuning, narrowly guarded unavailable diagnostics, static-only LLVM, generated AIR headers with a public Metal atomic call, real Burn payload extraction with pure-x64 CHPE filtering, checksum-pinned Swift6.4.1 host CI, strict failure propagation and actual IPA/resource validation. StikJIT, Steam authentication and game entitlement behavior were preserved. No proprietary game installation was copied into the IPA, no prerequisites were falsely marked installed, and no anti-cheat or DRM bypass was implemented.

The bundle is unsigned: actual codesign diagnostics say code object is not signed at all. It requires compatible signing/provisioning before sideloading, including its helper extension and embedded dylibs/framework. The artifact includes Requested-entitlements.plist and UNSIGNED.txt; requested entitlements are not Apple-granted entitlements. Bundle identifier remains com.willfaust.madeora.

Compilation and structural validation do not demonstrate a device launch. No new iPhone, JIT, Call of Duty startup or GPU execution test was performed. Call of Duty app1938090's required RICOCHET Windows kernel-driver capability remains a material Madeira/iOS incompatibility: [platform limitations and official sources](cod-platform-limitations.md). The build is delivered for testing the early loader correction; gameplay success is not claimed.
