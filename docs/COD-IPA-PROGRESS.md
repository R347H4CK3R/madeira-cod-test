# COD HQ test IPA progress — 2026-10-24

Status: the next full build is ready with separately verified runtime-input, Metal and Linux-toolchain repairs. Previous strict Xcode27 run40069910949 built Wine, patched ARM64EC ntdll, FEX, pairing and LLVM; LLVM's completed cache is saved. No new IPA has been built or validated yet. COD startup remains untested in a new build. Earlier sections preserve historical snapshots; the final update records current results.

## Source and preservation

- Fork: R347H4CK3R/madeira. New working branch: fix/cod-1938090-ipa-20261024.
- Base: 4537c7ad9931c5b6d5993346a675e8665aed845a, from fix/cod-1938090-uctrbase-launch-diagnostics.
- Existing cloud checkout was clean. Existing Windows checkouts were inspected without changes. Main and old builds remain intact.
- Pinned FEX: 26859e184ad90f0e811d7f8bbd943a4b1573a2c3; Wine: 4f5b19718f4de88ecc5cb0dc08b119497a67ba8f; DXMT: 35a4db11bd1bda380c5176a3bc6c1878f7192101; Dock: 3cadfbea700e4da4b04e331dd7ef1ba633dfacef.
- Full recursive manifest: diagnostics/cod-ipa-submodules.txt. Recursive initialization succeeds for the pinned base.
- Upstream main at audit: e3a88fddb8daed1f5ac28a45dcb4663d65192629, 524 commits ahead / 1 fork-only commit. Upstream fetch exposed unreachable historical submodule objects (FEX 22337c8d..., Wine 0511f7e7...); this did not change the pinned working tree. No blanket upstream merge.
- FEX/AGENTS.md prohibits AI-generated code contributions. The later diagnostic repair section records the explicit user-authorized override for two proven local build defects; no upstream contribution is made.

## Hardware and toolchain compatibility

Observed GamingLaptop differs from the supplied Windows 10 Pro description: Windows 11 Home 10.0.26300, AMD Ryzen 5 6600H (6 cores/12 threads), virtualization enabled and hypervisor active, 16 GB RAM. AMD Radeon driver 32.0.21045.16010. C: approximately 510 GB total / 55 GB free at audit.

Git 2.55 and Python 3.13.15 are installed. Visual Studio Build Tools 2022 17.14.41 supplies MSVC 14.44 and bundled LLVM/CMake/Ninja outside PATH. WSL is not installed; Rust, Docker and gh are not on PATH. Git Credential Manager recognizes the user's GitHub account. The connected GitHub repository reports push/admin permissions. Credentials were used only through the existing broker for GitHub authentication; no credential values were printed or persisted. No security settings or unrelated applications were changed.

The cloud workspace is Debian 13 x86-64, five virtual CPUs, about 17 GiB RAM and 30 GiB free disk initially. Git, Python, GCC/make, Docker CLI and Rust 1.94.0 are available; Swift and Xcode are absent. Native iOS builds must use a macOS/Xcode runner. Windows and Linux checks cannot validate iOS runtime execution.

## Evidence and crash investigation

The actual supplied log is held outside Git (it can contain personal paths). It identifies iPhone17,4, iOS 27.2 build 24B115. The log shows StikJIT/Wine initialization and an attempted Randgrid prerequisite followed by 0xc000001d; the installer failure is not recorded as success.

The original Madeira-0.1.3.ipa is now identified in Drive (145,554,426 bytes), but cannot be materialized through the executor's 32 MiB transfer limit. The Madeira-COD-Debug folder is a source checkout, not an extracted app. Four smaller DLLs retrieved from that folder exactly equal the tracked files.

Binary evidence is now concrete: the Drive ARM64EC ntdll contains the exact logged caller instruction at RVA0x323b0, inside MODULE_InitDLL, calling the indirect-call thunk. The installed COD folder's x64 ucrtbase.dll (version10.0.22000.832, SHA256 a73bd7d75f368ab2fe949dcddbb25cd5d5975ff9091761a01b98f5e26de543ee) matches the logged image size0x111000, entrypoint0x15e30 and all32 logged instruction bytes. This corroborates native execution of the game's x64 CRT during FEX bootstrap, before emulator state exists. The source patch isolates the translator's dependency path to sysx64;system32 and rebuilds the ARM64EC ntdll in CI. It preserves ordinary application path ordering; later bare-name imports normally reuse the native CRT already loaded during bootstrap. Four behavioral cases pass; the unpatched bootstrap cases fail. Full iPhone file identity and device confirmation remain outstanding. See diagnostics/cod-runtime-investigation.md.

Official Activision and Steam sources establish a separate RICOCHET kernel-driver requirement for app1938090. Madeira/Wine does not supply a Windows kernel. Fixing the bootstrap failure does not establish gameplay compatibility; no anti-cheat or prerequisite bypass is implemented. See diagnostics/cod-platform-limitations.md.

The FEX guard-page mprotect message, reduced JIT pool, missing memory entitlements and x18 warnings are not independently established root causes. No memory/security/entitlement bypass is proposed. No anti-cheat, DRM, entitlement or kernel-driver bypass is authorized or implemented.

## Build investigation and implementation

All 66 existing fork Actions runs failed; none published an artifact. Three runs have no jobs (invalid workflow); 63 have failed build jobs. Recent failures occur before Xcode, including missing generated Wine IDL headers. The troubleshooting branch only supplies a presence audit, not a build workflow. The complete failure inventory is diagnostics/cod-ci-audit-2026-10-24.md and diagnostics/cod-ci-failed-runs.json.

Work underway: reconstruct native dependency archives, compile Debug arm64 iOS app on macOS, validate the actual bundle, package Madeira-COD-Fix-Test.ipa, upload build/test logs and real artifacts. Do not substitute empty archives, dummy binaries or a repackaged old IPA.

IPA validation tests pass 23 synthetic fixture cases covering real executable sections/entrypoints, CPU/iOS device platform, PE structure and CHPE metadata, valid Wine prefix registries, required native/EC DLLs, the JIT extension/framework, Metal converter, VC core runtimes, staged-resource hashes, unsafe paths and duplicate entries. Fixtures exercise the validator only; they are never delivered as an IPA. Structural checks do not prove code signing or successful execution.

## Tests and blockers

Baseline: 28/48 host check scripts exit 0 and 20 exit 1. Seventeen fail because Swift is unavailable; steam-library needs Python 3.14 compression.zstd; wma-decoder needs configured Wine headers; swap-coverage has a pre-existing expectation failure (coverage banner not printed at tier start). The pairing Rust suite passes all five tests. Two successful check scripts include optional omissions: Swift/C BOM agreement and a real MP3 fixture. Root, FEX, Wine, DXMT and Dock git fsck checks all pass. The pinned submodule working trees and indices match the gitlinks. Missing Swift and generated Wine headers cause explicit host test failures; these are not reported as passes. No connected iPhone test interface or macOS development computer has been established. No new IPA, checksum or download URL exists yet.

## Commits and current build blocker

- 3f351fe: scoped emulator bootstrap dependency path, behavioral test, full staged build workflow.
- c56c21a: 64-bit host configure, official VC runtime extraction, registered workflow filename.
- 3b05801: strict IPA validation, source-resource hashes, archive architecture checks and actual freshly built crypto inputs.

Supported Actions enable operations both returned HTTP204, but dispatch still returns HTTP422: "Actions has been disabled for this repository." Repository setting enabled=true, workflow active, branch/source readable and token repo/workflow scopes verified. No run exists. This is not a compilation failure. Exact account/service reason remains hidden; no billing cause has been established. Full evidence and GitHub request IDs: diagnostics/cod-actions-rejection.md.

Final local suite: 30/50 check scripts exit0, 20 baseline failures remain (17 Swift absent, Python compression.zstd absent, configured Wine headers absent, swap-coverage expectation mismatch). Pairing Rust tests5/5 pass. New tests: bootstrap4/4 and IPA validator23/23. Shell syntax, converter source hashes and diff checks pass. These do not validate native iOS compilation or device behavior. Machine-readable results: diagnostics/cod-host-results.json.

## Active build in the independent source copy

The user requested a new fork. GitHub returned the existing fork instead of creating a second same-account fork. The separate, explicitly labeled source repository https://github.com/R347H4CK3R/madeira-cod-test was created without modifying the old fork/main. It preserves the tested source history and pinned submodules; GitHub reports fork=false.

An owner-authenticated workflow update at 7c4771a512f83c46b09434df7c37c836dc3085df registered workflow394835476 and triggered real run40064483490:
https://github.com/R347H4CK3R/madeira-cod-test/actions/runs/40064483490

The macOS job passed recursive checkout and began Xcode/build preparation. The Ubuntu host-check job passed checkout/Python setup and began the full suite. No duplicate manual dispatch was sent. The original repository's execution rejection is unchanged; the new successful run shows that this account can execute Actions, but does not explain the old repository's hidden service state. Further build/compiler results and artifacts remain pending.

## Next steps

Finish build recipe and review; run macOS CI; inspect failures and retest; match original IPA's ucrtbase and ntdll against log; implement a regression-tested dispatch correction only if confirmed; validate/package/download real output. Update this record with actual commits, runs, test totals, signing state and hashes.

## Corrected toolchain build and test inventory

The first native run40064483490 was canceled after checkpointing when a separate compiler probe established StikJIT incompatibility on macOS15's latest Xcode26.3/Swift6.2.4. Its actual logs also exposed errors hidden by the initial tee pipelines: FEX ran Linux-only native CPU probes; LLVM attempted an unneeded libLTO dylib with ELF linker flags; DXMT lacked generated AIR headers. Actual Wine native archives, rebuilt patched ntdll, and Rust pairing did build; FEX did not. Earlier green step markers were insufficient proof. Details: diagnostics/cod-native-build-first-run.md.

The corrected full build is run40067316290 at source8af4d2771cb8ff3a14d6bbe22806d4567544f906:
https://github.com/R347H4CK3R/madeira-cod-test/actions/runs/40067316290

It uses official xcode-27, strict Bash failure propagation, generic FEX compilation without editing FEX, static-only LLVM configuration, and source-generated DXMT AIR headers. Old partial LLVM cache is not reused. Media/crypto/fonts completed under the new toolchain; remaining native stages and packaging are pending.

The actual helper/compiler probe40066625182 passed with Xcode27.2RC(27B48), Swift6.4.2, SDK27.2(24B113), all tracked StikJIT hashes unchanged. See diagnostics/cod-xcode27-compatibility.md.

Prepared local Linux validation runs48/48 applicable checks successfully, with2 explicit Apple-only exclusions recorded in the inventory. Those2 scripts independently passed on strict macOS run40065715371 (22JIT and27Cloud checks). A separate verbose Steam-download interruption diagnostic timed out300s; later complete suite passed, so the intermittent timeout is retained as unresolved. Latest full CI's Linux job failed before running tests because setup-swift@v2 rejected the available vendor version6.2.3; a direct checksum-pinned vendor install is being prepared in an independent test workflow. No host success is claimed for that failed CI setup.

No connected iPhone USB interface was detected. Device launch/gameplay remains untested; no new IPA or download/hash exists yet. No original game assets, signing credentials, or pairing secrets were copied.

## FEX native diagnostics repair

The strict Xcode27 run40067316290 stopped at the pinned FEX source's unguarded references to ARM64EC-only diagnostic counters. The CPU-probe configure correction worked; native Wine and patched PE ntdll completed under strict failure propagation. A two-line FEX_IOS_HOST guard patch now matches the existing guarded declarations, without enabling Windows-only frontend hooks or substituting counters. The unchanged FEX gitlink plus local build patch are recorded separately. Unpatched extracted production code fails native compilation; patched native and active-producer diagnostics pass, with independent review. The specific local build patch is authorized under the user's explicit FEX/source-repair task; it overrides the upstream AGENTS contribution guideline for this user-fork build only, and is not an upstream contribution.

Standalone Linux CI run40067923452 succeeded with checksum-verified Swift6.2.3 and prepared Wine headers:48/48 selected checks,50 discovered,2 named Mac delegations. Uploaded ZIP checksum and every log/JSON exit verified. The main workflow now calls that same reusable test workflow. The new FEX regression increases the next discovered inventory by one and still requires a full native FEX compile. No IPA exists yet.

## Latest strict build and input preflight

Run40068582962 at c2345d31ed1cbdab0f07601f09812e9df768eaf7 completed its called Linux job successfully:49/49 selected scripts passed,51 discovered,2 explicit Apple delegations. Full logs and artifact hashes were verified. The native build compiled the first FEX guard repair, but stopped at Arm64.cpp's unguarded Windows-only VirtualQuery diagnostic. The narrow patch now keeps that query under _WIN32 and reports genuine existing size/address/misalignment fields on native builds. CASPAL atomics and opcode handling are unchanged. Extracted production-source regressions reproduce the original compiler error, pass after patching, and verify identical Windows output. Independent review found no blockers; the full native build remains required.

The independent Microsoft-runtime preflight40069435656 failed before download because Ubuntu's 7zip package supplies7z, while the production helper requires7zz. This is a dependency failure, not evidence of an extraction-algorithm defect. Its dependency is being corrected to the official standalone7zz package; actual Microsoft extraction remains unverified until the next run.

Local focused verification also passes all4 bootstrap behavioral cases and all23 IPA-validator fixtures. These fixtures are not an application build. No IPA, signing success, device launch, or Call of Duty startup success is claimed.

The corrected input dependency passed in run40069910875, and Microsoft's official installer downloaded successfully (25,635,768 bytes; SHA256 cc0ff0eb1dc3f5188ae6300faef32bf5beeba4bdd6e8e445a9184072096b713b). Actual extraction then exposed a separate defect:7-Zip opens the first cabinet but leaves the appended Burn payload unprocessed, so core DLLs are missing. The extractor repair is being developed and exercised on an isolated input-check branch while the native build proceeds. No missing runtime is replaced with a placeholder.

Run40069910949 subsequently passed the real FEX source build and all required archive guards, then pairing; the corrected LLVM build is in progress. Its called Linux job finished48/49: the sole failure is the previously intermittent Steam-library interruption phase timing out300s, after its units phase passed under AddressSanitizer. The artifact ZIP SHA256 was verified locally against GitHub, and the full traceback was inspected. A minimal host-only FoundationNetworking cancellation reproduction is under investigation; no authentication or download assertions have been weakened.

The isolated extractor probe40070941050 at f4b018df28bc0beffd8159485e3ddf8bb67d44cf completed successfully. It parses WiX Burn's declared container boundaries and rejects ARM64EC candidates using CHPE metadata even when their PE Machine reports AMD64. Actual extraction and separate folder validation staged12 unchanged pure x64 DLLs, including all3 core files; all16 focused regressions passed without skips. The same helper/test changes are integrated locally for the next main build. Independent review found no concrete P1/P2 issue. Full evidence and hashes: [runtime extraction report](diagnostics/cod-runtime-inputs-repair.md), [actual inventory](diagnostics/cod-runtime-inputs-inventory.json). This is input validation, not an IPA or device result.

The graphics failure is the pinned shader's four-argument private __metal_atomic_fetch_add_explicit call; Metal27B47 expects five arguments. Both other embedded AIR shaders compile. The toolchain component download succeeded. A public threadgroup atomic fetch-add replacement is being checked with the actual Metal compiler, without changing the verified LLVM build script/cache key.

The host interruption stall reproduces in a minimal FoundationNetworking cancellation test with downloader/authentication/install code removed. Official swift-corelibs-foundation issue5412 and PR5417 identify the matching response-completion lock inversion and its workQueue.sync-to-async repair. Stable Swift6.4.1 contains that fix. Its vendor archive signature was verified; the unchanged minimal test passes under6.4.1 and stalls under6.2.3. The full unchanged host suite is being checked before a CI toolchain update. No test assertion or production Steam behavior is weakened. The next application and JIT helper are marked build5, keeping version0.1.3 and their existing identifiers.

Both remaining isolated probes are now verified successful. Linux run40072036246 at0447f4a0bb17de22da3fa0d9acd5d540540037a3 used a cold-cache checksum-pinned Swift6.4.1 install and passed49/49 checks,51 discovered,2 named Apple delegations. All6 Steam-library ASan phases passed in19.513s. Its66,528-byte artifact SHA2564e10a02e8a6ebed1cdc765dbe84e5c038f475f5726b6b6822cc918106658f69b was verified locally. Tests, timeouts, authentication and downloader code were not changed for this repair.

Metal run40072320821 at64c8b43a3ef763d10725ec7959b430253e5dc4cc reproduced the original full-shader error, compiled all3 patched shaders, and emitted actual AIR IR. Installed Apple headers and the IR confirm the original32-bit threadgroup relaxed fetch-add and returned old index. Independent review found no blocker. The one-call source patch plus idempotent build adapter are integrated; LLVM's build script/cache key stays unchanged. [Actual Metal compiler evidence](diagnostics/cod-metal-atomic-verification.md). These probes establish input/compiler/test behavior; the full app link and actual IPA packaging still must pass.
