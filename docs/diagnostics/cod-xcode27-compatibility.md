# StikJIT compatibility verified with the official Xcode 27 runner

The production Madeira JIT helper successfully typechecked against the unchanged tracked StikJIT framework in [run 40066625182](https://github.com/R347H4CK3R/madeira-cod-test/actions/runs/40066625182), job [120791139498](https://github.com/R347H4CK3R/madeira-cod-test/actions/runs/40066625182/job/120791139498), source `c75e273eeb7561991cd977088cd7d336d4aad225`. This is compiler compatibility evidence, not an app build, IPA, or device execution result.

## Actual compiler and SDK

- Runner label: `xcode-27`.
- Selected developer directory: `/Applications/Xcode_27.2_Release_Candidate.app/Contents/Developer`.
- Xcode: **27.2**, build **27B48**.
- Apple Swift: **6.4.2**, `swiftlang-6.4.2.1.9 clang-2100.4.1.1`.
- iPhoneOS SDK: **27.2**, build **24B113**.
- Compilation target: `arm64-apple-ios26.0`.

The recorded `swiftc-exit-code.txt` contains `0`. The real helper sources were `app/MadeiraJITHelper/MadeiraJITHelper.swift` and `app/Madeira/JITBuiltInMessages.swift`; the physical-device conditional imported the actual tracked StikJIT framework. The effective helper settings were Swift language mode 5, application-extension restrictions enabled, DEBUG enabled, no OTHER_SWIFT_FLAGS, and the default Objective-C interoperability mode. The log contains the actual compiler command and no compiler errors.

All 10 recorded framework file SHA256 values are identical to the first probe, which failed with Swift 6.2.4 on the highest installed Xcode 26.3. StikJIT's interfaces still identify Apple Swift 6.4. Selecting the matching official runner resolves that observed import failure without changing StikJIT.

## Retrieved evidence

- [GitHub diagnostic artifact 12549148035](https://github.com/R347H4CK3R/madeira-cod-test/actions/runs/40066625182/artifacts/12549148035): 12,180 bytes.
- ZIP SHA256, verified against GitHub's artifact digest: `914e3b58051ba5e5ebb4d606538661cddc653803fdf5736881662d9dbd25538f`.
- Downloaded with the GitHub connector and `tools.download_file`, then extracted to `/workspace/ios-toolchain-probe-40066625182/`.
- Full decoded job log: `/workspace/ios-toolchain-probe-40066625182-job.log`.
- Key files: `inputs.log`, `stikjit-typecheck.log`, `swiftc-command.txt`, `swiftc-exit-code.txt`, and `effective-swift-settings.json` in that extracted directory.

## Review of the subsequent full build

[Run 40067316290](https://github.com/R347H4CK3R/madeira-cod-test/actions/runs/40067316290) uses source `8af4d2771cb8ff3a14d6bbe22806d4567544f906`. Read-only source inspection confirms its build job selects `xcode-27` and uses explicit Bash run shells, which GitHub invokes with `-e -o pipefail`; `build/ci/build-ios.sh` also enables `set -euo pipefail`. Its StikJIT framework and both helper sources are unchanged from the passing probe.

At review time, build job `120793171864` was compiling media libraries after passing Xcode selection, toolchain setup, and cache restoration. Linux host-check job `120793171756` had failed at `swift-actions/setup-swift@v2`, before running host checks, with the actual diagnostic `Version "6.2.3" is not available`. That separate setup failure does not invalidate the Apple compiler evidence and needs correction before claiming the full workflow passes.

No repository files, application sources, framework files, or workflows were modified during this evidence retrieval and review.
