# Official Microsoft runtime input extraction repair

Work is isolated in `/workspace/madeira-runtime-inputs`, branch `fix/runtime-inputs-20261024` based on `b7edf6a`. The long native iOS build is not cancelled or modified by this probe. No installer or Microsoft DLL binaries are uploaded as diagnostics.

## Actual failures and evidence

1. [40069162517](https://github.com/R347H4CK3R/madeira-cod-test/actions/runs/40069162517): workflow schema error, job environment used unavailable `runner` context. Moved temporary-directory assignment into the first shell step using `RUNNER_TEMP` and `GITHUB_ENV`. Actionlint reproduced and then cleared this error.
2. [40069435656](https://github.com/R347H4CK3R/madeira-cod-test/actions/runs/40069435656): Ubuntu `7zip` did not supply the required `7zz`. Corrected dependency to `7zip-standalone`; subsequent actual runner resolves and runs `7zz` 23.01. Official Ubuntu provider: https://manpages.ubuntu.com/manpages/noble/man1/7zz.1.html . Download/extraction had not run at this failure.
3. [40069910875](https://github.com/R347H4CK3R/madeira-cod-test/actions/runs/40069910875): real official installer downloaded successfully, but automatic EXE extraction opened only its first Burn UX CAB and ignored the attached payload. Missing all three core runtime DLLs.
4. [40070479795](https://github.com/R347H4CK3R/madeira-cod-test/actions/runs/40070479795), probe `3a6c3ab`: metadata-based Burn boundaries successfully extract the real UX, attached CAB, and nested payloads. The existing duplicate gate then rejects two distinct `vcruntime140_1.dll` payloads.
5. [40070747326](https://github.com/R347H4CK3R/madeira-cod-test/actions/runs/40070747326), diagnostics-only `2815b41`: establishes the duplicate is the ARM64EC variant, which also reports Machine AMD64, alongside the pure x64 variant. Both have version 14.44.35211.0. Duplicate rejection remains active.
6. [40070941050](https://github.com/R347H4CK3R/madeira-cod-test/actions/runs/40070941050), `f4b018d`: pure AMD64 selection repair: **completed SUCCESS**. Official download, all 16 focused checks with no skips, production extraction, separate production folder validation, and PE inventory all passed. Exactly 12 pure x64 DLLs were staged, including all three core files; the ARM64EC collision was rejected by its nonzero CHPE pointer. The extracted DLL hashes match the eligible source candidate hashes in the same log.

The actual official installer is 25,635,768 bytes, SHA256 `cc0ff0eb1dc3f5188ae6300faef32bf5beeba4bdd6e8e445a9184072096b713b`, obtained by the runner from `https://aka.ms/vs/17/release/vc_redist.x64.exe` using HTTPS-only curl redirects. This is the resolved version at execution time, not a permanent version pin.

## Burn boundaries and architecture proof

The real `.wixburn` v2 metadata declares:

| Container | Offset | Bytes | SHA256 |
| --- | ---: | ---: | --- |
| UX | 479744 | 195988 | `2f57cf2cd504bd100c9222bb123b9c3a40802cca73e89ca05c97885d91be3a78` |
| attached | 686152 | 24939223 | `468f1264d50b9e3b9d309ab9e13c02ff379fd95a2837383bf65c9616583013d6` |

The attached CAB begins after the original engine signature, independently of the current whole-bundle signature at the end. Parsing follows WiX's published structure and validates bounded PE sections, metadata, exact CAB lengths, and signature ranges; it does not scan blindly for CAB magic. Sources:

- https://github.com/wixtoolset/wix3/blob/develop/src/tools/wix/BurnCommon.cs
- https://github.com/wixtoolset/wix3/blob/develop/src/tools/wix/BurnReader.cs
- https://github.com/wixtoolset/wix3/blob/develop/src/tools/wix/BurnWriter.cs

The actual manifest explicitly associates ARM64 payloads with `Arm64_Check = "ARM64"`, while minimum/additional x64 packages use `(VersionNT64) AND NOT (Arm64_Check = "ARM64")`.

| Actual candidate | Machine | CHPEMetadataPointer | Bytes | SHA256 |
| --- | --- | --- | ---: | --- |
| `vcruntime140_1.dll_arm64` | `0x8664` | `0x18000a468` (metadata version 2) | 53320 | `42b5f76f1f0ae03c93fc4c107adf83c5f14e86032474860032cfe672d0836546` |
| `vcruntime140_1.dll_amd64` | `0x8664` | `0` | 49792 | `1f2d41c4aa5db0bc33ebf7b66d72943a817d7ce6cbe880502a9403823633093f` |

All twelve actual pure x64 candidates have load-config size 320 and CHPE pointer zero. Microsoft documents that the x64 installer includes both architectures and that ARM64EC DLLs may report AMD64 Machine:

- https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist
- https://learn.microsoft.com/en-us/windows/arm/arm64ec#identifying-arm64ec-binaries-and-apps
- Official SDK structure defines `IMAGE_LOAD_CONFIG_DIRECTORY64.CHPEMetadataPointer` at offset 200, ending at 208: https://github.com/microsoft/win32metadata/blob/main/generation/WinSDK/RecompiledIdlHeaders/um/winnt.h

The repair rejects any nonzero CHPE pointer for these pure x64 guest inputs; it does not pick the first/newest duplicate. Malformed load-config ranges fail closed, consistent absent/older structures remain supported, and conflicts among eligible same-name DLLs still fail. Certificate payload bounds are checked; cryptographic Authenticode verification is not performed. DLL bytes are copied unchanged.

## Verification

The Burn regression was RED against automatic EXE extraction, then GREEN after the metadata repair. Architecture regressions were RED before the pure-x64 gate: hybrid collision, acceptance of hybrid-only folders, and malformed load configurations. The current GREEN suite runs 16 checks with no skips when actual 7zz is on PATH, including real synthetic CAB extraction and byte-for-byte comparison. These fixtures contain no Microsoft code.

```
cd /workspace/madeira-runtime-inputs
PYTHONDONTWRITEBYTECODE=1 PATH=/workspace/.tools/7zip2301:$PATH python3 tests/host/test-stage-vcruntime.py
PYTHONDONTWRITEBYTECODE=1 python3 tests/host/test-validate-ipa.py
/workspace/.tools/actionlint/actionlint -shellcheck= -pyflakes= -ignore '^label "xcode-27" is unknown\.' .github/workflows/*.yml
```

Observed local results: 16 extraction/architecture checks, 23 IPA-validator checks, and semantic workflow lint pass. Actionlint is official rhysd v1.7.7. The only ignored warning is the documented new `xcode-27` runner label (actions/runner-images#14404). The runtime-input workflow explicitly executes the otherwise non-discovered `test-stage-vcruntime.py`; both helper and test changes trigger it on the main fix-branch pattern and the isolated probe branch.

Full decoded evidence logs are `/workspace/ci-runtime-preflight-40069910875.log`, `/workspace/ci-runtime-probe-40070479795.log`, and `/workspace/ci-runtime-probe-40070747326.log`. GitHub artifact metadata/digests may be reported as GitHub-provided values; ambiguous FileService references have not been materialized or claimed as locally hash-verified ZIPs. This input validation is not an IPA build, device run, COD launch, or gameplay result.

## Successful real installer inventory

All files below report AMD64, an in-bounds certificate payload, and zero CHPE metadata pointer in the source candidate log. The observed version is 14.44.35211.0. Cryptographic Authenticode verification was not performed.

| Filename | Bytes | SHA256 |
| --- | ---: | --- |
| `concrt140.dll` | 324208 | `2405355f0a58067b258f8df33c327e3a3d716eaac5a3a5aebb757842d85bd376` |
| `msvcp140.dll` | 557728 | `0f885b509a685d2bbfa652fed26b5fb31d88fbdab0a978c641d1c7b8aa460aa9` |
| `msvcp140_1.dll` | 35952 | `bfad5aef4c63a669e3c140655cdfdf395b6c979b400a447bd5dcb65ed8826c3d` |
| `msvcp140_2.dll` | 280200 | `3ea06f0ee098b4823cb79599df3780e7f23cce52c19aac31d2a0d47efe33a5e9` |
| `msvcp140_atomic_wait.dll` | 50304 | `640b2aefced484d0368eea5bdd06addd0658a3a70a49256e560d6923b404a479` |
| `msvcp140_codecvt_ids.dll` | 31872 | `f2069a52880ec885ee7f0511186100eb7fada0411a2b4948fafea7735b878a18` |
| `vcamp140.dll` | 418944 | `52af68f35476bd03d7b97752b01bef358ffdda568d150057d6ce809f77c4f704` |
| `vccorlib140.dll` | 352384 | `19839407c3fdbc824e5bce189bf68ddf8097f12ec28b757797ffa0415c144ddd` |
| `vcomp140.dll` | 193152 | `55aba23cdcd6484fbb06f4155b8ca75adfce7a881f10afd0c49457165e677164` |
| `vcruntime140.dll` | 124544 | `d5e4d9a3e835fa679450145d6a7d94e36573a509317111904d9b3712c30d9066` |
| `vcruntime140_1.dll` | 49792 | `1f2d41c4aa5db0bc33ebf7b66d72943a817d7ce6cbe880502a9403823633093f` |
| `vcruntime140_threads.dll` | 38528 | `219915cf20822f34d5e7c1fdd4e21ae7f3396881096c51036225fb8f84b47afa` |

Successful full log: `/workspace/ci-runtime-probe-40070941050.log`; parsed actual inventory: `/workspace/ci-runtime-probe-40070941050-inventory.json`. Diagnostic artifact 12551591054 is 19,397 bytes; GitHub-provided archive digest is `sha256:5e6af7166722d8730249689cc7c5f6379db0483eb060637145ad1852fa6a2120`. This digest is API evidence, not a claim of local archive verification.

Independent read-only review of `f4b018d` found no concrete P1/P2 issue and independently reran all 16 checks with 7zz, no skips. The isolated worktree remains separate; root coordinates integration of commits `3a6c3ab`, `2815b41`, and `f4b018d`.
