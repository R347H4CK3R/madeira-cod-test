# Real CI host validation

The `host-checks` job **failed correctly: 43 of 50 check scripts passed; 7 failed**. All 50 completed and produced logs. No failures were skipped or converted to successful runner results. The initial CI evidence collection modified no repository files. The later authorized test-only corrections and their local verification are recorded below; the historical CI result remains unchanged.

## Run and evidence

- Repository: `R347H4CK3R/madeira-cod-test`.
- Run: https://github.com/R347H4CK3R/madeira-cod-test/actions/runs/40064483490
- Job: https://github.com/R347H4CK3R/madeira-cod-test/actions/runs/40064483490/job/120784750933
- Head: `7c4771a512f83c46b09434df7c37c836dc3085df`, branch `fix/cod-1938090-ipa-20261024`.
- Runner: GitHub-hosted Ubuntu 24.04.5, image `ubuntu-24.04` version `20261012.334.1`; Python 3.14.8.
- Suite: started 2026-10-24 05:00:54 UTC, finished 05:04:07 UTC; approximately 193 seconds.
- Checkout and Python setup succeeded. `Run every host check` failed. Host diagnostic artifact upload succeeded.
- Full decoded job log: `/workspace/ci-host-job-full.log` (67,440 characters).
- Job/artifact metadata: `/workspace/ci-host-run-metadata.json`.
- Extracted artifact: `/workspace/ci-host-artifact/`, including `results.json` and all 50 check logs.
- Downloaded ZIP: `/workspace/attachments/78c79f5b-eb7c-4356-bd6d-84e6a7720195/Madeira-COD-host-checks.zip`.
- Artifact `12548688045`, `Madeira-COD-host-checks`, 53,220 bytes. Verified ZIP SHA-256 matches GitHub's digest: `b2347d2b01fc5b403b9433876445f6626e6a2062e063c2ccacd2ed62e3cb084a`.

## Task-related regressions

`check-arm64ec-bootstrap.py`: all four cases passed against the pinned production loader plus the temporary patch: native sysx64 CRT before local x64 CRT, native system32 fallback, fail safely when native CRT is absent, preserve ordinary application local-first search.

`test-validate-ipa.py`: all **23 tests passed**. Its fixtures test archive validation; these are not an actual app build or device run.

The previous cloud baseline's 17 Swift-launch failures did not recur as missing-compiler failures. CI has a usable Swift toolchain. Python's missing `compression.zstd` error did not recur with Python 3.14.8. `check-cfg-early-docs.py` now ran and passed its Swift/C BOM agreement case.

## Seven failures

| Check | Exact failure | Classification | What is established |
| --- | --- | --- | --- |
| `check-dock-contract.py` | `FAIL: madeira-dock is pinned at 0c5bbd1` | Stale test pin assertion | Test hardcodes `0c5bbd1a854c4c63c47e074b72954aba5b36919d`; the actual recorded gitlink is `3cadfbea700e4da4b04e331dd7ef1ba633dfacef`. All compiled Dock contract/AddressSanitizer cases passed. |
| `check-jit-network.py` | `error: no such module 'Darwin'` | Host-platform mismatch | Source assertions passed; its generated Swift harness explicitly imports Darwin and cannot compile on Linux. No loopback runtime tests ran. |
| `check-steam-cloud.py` | `error: no such module 'CryptoKit'` | Host-module prerequisite/platform mismatch | Source assertions passed; generated harness imports CryptoKit, absent from this Linux toolchain. No cloud comparison runtime cases ran. |
| `check-steam-games.py` | `FAIL: config.launch is read in Steam's numeric order...` | Fixture escaping expectation mismatch | Actual output has one backslash in `Bin64\Game.exe`; fixture's expected value has two. All subsequent launch selection/path safety cases passed. |
| `check-steam-library.py` | Undefined `lzma_alone_decoder`, `lzma_code`, `lzma_end`; linker exit 1 | Unresolved host liblzma linkage | C shims compiled; Swift executable did not link. The retained log cannot distinguish missing library, library selection, or Swift driver link ordering. No download/decoder runtime cases ran. |
| `check-swap-coverage.py` | `coverage line printed at tier start` | Existing default/expected-header mismatch | C harness reports `0 failures`; Python expects blocks header after unsetting the coverage variable, while production defaults to classic. Same failure as baseline. |
| `check-wma-decoder.py` | `SKIP-FAIL: .../wine/build-macos/include/config.h is missing` | Missing configured Wine headers | Script returns 1. Production WMA harness compilation/decoding was not reached. Same prerequisite failure as baseline. |

### Why the Steam-games assertion is a fixture mismatch

`tests/host/check-steam-games.py` stores its Swift harness in a raw Python string. In the VDF fixture at line 352, the Swift literal has four backslash characters before `Game.exe`: Swift produces two in the VDF. The production VDF parser (`app/Madeira/SwiftSteam/Library/SteamLibraryFetcher.swift`, lines 305–307) explicitly unescapes a backslash pair to one. The expected Swift array at line 363 also has four source backslashes and therefore expects two after parsing. The CI array contains one, exactly matching that parser rule. The report does not identify a production parsing defect; this conclusion was checked independently by another agent.

### What is still unknown about liblzma

The test invokes Swift with `-Xlinker -llzma`, but prints only the final 6,000 characters of compiler stderr on failure. Thus, even earlier library-search diagnostics may have been discarded. The C shim declares the minimal liblzma ABI itself and does not include liblzma headers, so its successful compilation proves neither the installed library nor header availability. Before claiming a dependency or ordering fix, collect untruncated `swiftc -v` output and the selected liblzma path/exported symbols. Installing development packages is a reasonable preparation step but is not a proven resolution for this observed link failure.

## Platform and preparation tradeoffs

Moving the entire suite to macOS is **not an evidence-based fix**. It supplies Darwin and CryptoKit, but several existing harnesses are explicitly Linux-oriented:

- Dock contract, Dock installers, Steam games, and Steam library generate unconditional `import Glibc`.
- Dock components and Steam library hardcode `/usr/include/zlib.h`, which is not the modern macOS SDK header location.
- Swap coverage includes `<linux/falloc.h>` and uses `MAP_FIXED_NOREPLACE`.
- Steam library unconditionally generates CommonCrypto/Compression stand-ins and links `-lcrypto -llzma -lz`; merely running on macOS does not switch it to native framework/module handling.

Placing all tests after the macOS build's `Generate complete Wine header sets` step would reuse configured headers and make the two Apple-module tests available, but would expose the Linux harness failures above. A failing test step would also stop later IPA build/package steps. The existing independent host job lets compilation continue while retaining a red test result and its evidence.

A narrower arrangement can keep Linux-oriented checks on Ubuntu and execute the Darwin/CryptoKit checks on macOS, with an explicit complete check inventory and aggregate failure status. That requires runner/workflow changes; none were made in this follow-up. It should not silently omit any failed check or use `continue-on-error` to report success.

For WMA on Linux, prepare a native Wine build configured from the pinned source, generate `include/all`, and point `MADEIRA_WINE_BUILD` at it. The WMA script then automatically builds the required host FFmpeg from the tracked tarball unless `MADEIRA_HOST_FFMPEG` points at a suitable existing build. WMA does not require the ARM64EC cross-header set or the full iOS setup. The native subset of the recipe is `../configure --enable-win64 --without-x --disable-tests --enable-winegstreamer` plus `make -jN include/all`; the full `build/ci/build-ios.sh headers` function also performs a separate ARM64EC configure and the script defaults JOBS through macOS `sysctl`, so it should not be invoked unchanged as a presumed portable host-setup script.

## Coverage limits retained in successful checks

- `check-dock-installers.py`: `SKIP: cmd.exe not reachable; batch flow checked textually only`. Its other compiled checks passed; actual Windows batch execution was not covered.
- `check-wg-parser.py`: `SKIP: no real MP3 available (set MADEIRA_TEST_MP3)`. Its other cases passed; the optional real-MP3 case did not run.
- These are existing internal branches in scripts that return zero, not checks skipped by the unified runner. The logs retain them. A claim that every possible runtime case passed would be false.
- AddressSanitizer linker export warnings appeared in Swift logs; successful executable runs followed them. They are not the failure reason for Dock contract or Steam games.

## Complete check results

| Check | Exit | Seconds | Log in `/workspace/ci-host-artifact/` |
| --- | ---: | ---: | --- |
| `check-arm64ec-bootstrap.py` | 0 | 1.568 | `check-arm64ec-bootstrap.log` |
| `check-audio-downmix.py` | 0 | 1.192 | `check-audio-downmix.log` |
| `check-audio-wow64.py` | 0 | 0.107 | `check-audio-wow64.log` |
| `check-cfg-early-docs.py` | 0 | 32.152 | `check-cfg-early-docs.log` |
| `check-config-catalog.py` | 0 | 7.133 | `check-config-catalog.log` |
| `check-control-presets.py` | 0 | 2.015 | `check-control-presets.log` |
| `check-d3d9-splitlock.py` | 0 | 2.539 | `check-d3d9-splitlock.log` |
| `check-d9-upload-commit.py` | 0 | 0.709 | `check-d9-upload-commit.log` |
| `check-dock-components.py` | 0 | 1.164 | `check-dock-components.log` |
| `check-dock-contract.py` | 1 | 3.175 | `check-dock-contract.log` |
| `check-dock-gdi-section.py` | 0 | 0.092 | `check-dock-gdi-section.log` |
| `check-dock-installers.py` | 0 | 2.668 | `check-dock-installers.log` |
| `check-dock-path.py` | 0 | 0.314 | `check-dock-path.log` |
| `check-dock-report.py` | 0 | 0.432 | `check-dock-report.log` |
| `check-dock-start-screen.py` | 0 | 1.454 | `check-dock-start-screen.log` |
| `check-fastsync.py` | 0 | 37.468 | `check-fastsync.log` |
| `check-filtering-cap.py` | 0 | 0.87 | `check-filtering-cap.log` |
| `check-frontend.py` | 0 | 2.528 | `check-frontend.log` |
| `check-gamepad.py` | 0 | 0.126 | `check-gamepad.log` |
| `check-hardware-input.py` | 0 | 0.758 | `check-hardware-input.log` |
| `check-image-retire.py` | 0 | 0.184 | `check-image-retire.log` |
| `check-jit-method.py` | 0 | 0.128 | `check-jit-method.log` |
| `check-jit-network.py` | 1 | 1.033 | `check-jit-network.log` |
| `check-jit-pairing.py` | 0 | 36.387 | `check-jit-pairing.log` |
| `check-launch-routing.py` | 0 | 0.143 | `check-launch-routing.log` |
| `check-lazy-windows.py` | 0 | 3.29 | `check-lazy-windows.log` |
| `check-library-api.py` | 0 | 0.699 | `check-library-api.log` |
| `check-library-sections.py` | 0 | 0.023 | `check-library-sections.log` |
| `check-nav-keys.py` | 0 | 0.071 | `check-nav-keys.log` |
| `check-nsi-network.py` | 0 | 1.673 | `check-nsi-network.log` |
| `check-onboarding.py` | 0 | 0.632 | `check-onboarding.log` |
| `check-readonly-link.py` | 0 | 0.136 | `check-readonly-link.log` |
| `check-runtime-settings.py` | 0 | 1.229 | `check-runtime-settings.log` |
| `check-scene-batching.py` | 0 | 0.618 | `check-scene-batching.log` |
| `check-section-abort.py` | 0 | 0.252 | `check-section-abort.log` |
| `check-small-va-band.py` | 0 | 0.161 | `check-small-va-band.log` |
| `check-steam-cloud.py` | 1 | 0.315 | `check-steam-cloud.log` |
| `check-steam-games.py` | 1 | 3.268 | `check-steam-games.log` |
| `check-steam-library.py` | 1 | 12.833 | `check-steam-library.log` |
| `check-steam-signin-native.py` | 0 | 4.563 | `check-steam-signin-native.log` |
| `check-swap-coverage.py` | 1 | 0.377 | `check-swap-coverage.log` |
| `check-touch-gamepad.py` | 0 | 0.428 | `check-touch-gamepad.log` |
| `check-unixlib-binder.py` | 0 | 0.111 | `check-unixlib-binder.log` |
| `check-wg-parser.py` | 0 | 23.602 | `check-wg-parser.log` |
| `check-win32u-zero-bits.py` | 0 | 0.106 | `check-win32u-zero-bits.log` |
| `check-wma-decoder.py` | 1 | 0.036 | `check-wma-decoder.log` |
| `check-wow-context.py` | 0 | 0.061 | `check-wow-context.log` |
| `check-wow-cpu-area.py` | 0 | 0.216 | `check-wow-cpu-area.log` |
| `check-wow-sweep.py` | 0 | 0.785 | `check-wow-sweep.log` |
| `test-validate-ipa.py` | 0 | 0.699 | `test-validate-ipa.log` |

## Subsequent authorized test-only corrections

After this CI report was delivered, the root agent authorized three narrowly scoped harness corrections. Local full Dock contract/AddressSanitizer, Steam games/AddressSanitizer, and swap tests now pass. Complete local suite: **46/50 pass, 4 environment/platform failures, exit 1** under Swift 6.2.3/Python3.12.14. This does not change the historical CI failure result above. Exact diff and RED/GREEN evidence: `/workspace/host-harness-fixes/verification.md`, `test-only.patch`, and associated logs; full new suite `/workspace/validation-swift-full/`.

## Prepared-dependency full-suite result

A fresh full 50-check run with Python 3.14.7, official Swift 6.2.3, local liblzma development files, generated native Wine headers and real host FFmpeg completed: **48 passed, 2 failed, runner exit 1**. All 50 per-check logs exist under `/workspace/validation-prepared-full/`. The only failures are `check-jit-network.py` (`Darwin` unavailable on Linux) and `check-steam-cloud.py` (`CryptoKit` unavailable on Linux). The other 48 returned zero; no runner failures were suppressed.

All three authorized test corrections pass in this complete run. SteamLibrary ran all phases (units, interruption, resume, update, uninstall and licensed-depot refusal) under AddressSanitizer and returned zero in 26.426s. WMA returned zero with both parameter-search settings and random-byte concealment. Successful scripts still explicitly omit actual Windows cmd.exe batch execution and a real MP3 fixture.

Environment for reproduction:

```bash
SWIFTC=/workspace/swift-host/swift-6.2.3-RELEASE-ubuntu24.04/usr/bin/swiftc \
PATH=/workspace/swift-host/swift-6.2.3-RELEASE-ubuntu24.04/usr/bin:/workspace/.cargo/bin:$PATH \
LIBRARY_PATH=/workspace/lzma-host/root/usr/lib/x86_64-linux-gnu \
MADEIRA_WINE_BUILD=/workspace/wine-host-tests/build \
PYTHON_CPU_COUNT=4 \
RUSTUP_HOME=/workspace/.rustup CARGO_HOME=/workspace/.cargo \
CARGO_TARGET_DIR=/workspace/.madeira-target \
/workspace/python-host/cpython-3.14.7-linux-x86_64-gnu/bin/python3.14 \
  tests/host/run-checks.py --output-dir /workspace/validation-prepared-full
```

`PYTHON_CPU_COUNT=4` bounds host FFmpeg make parallelism; it does not omit test cases. Native header configuration and the exact verified development-library packages are documented by the environment agent in `/workspace/wine-host-tests-status.md`, `/workspace/lzma-host-install.md`, `/workspace/python-host-install.md`, and `/workspace/swift-host-install.md`.

### Separate diagnostic failure retained

The standalone SteamLibrary diagnostic run used an external SWIFTC wrapper that added compiler `-v` and linker `-t`; it made no source changes. Full compiler output proves it selected `/workspace/lzma-host/root/usr/lib/x86_64-linux-gnu/liblzma.so`. That run passed its unit phase under ASan but timedout in the interrupt phase after 300 seconds, exit 1. The later full suite run passed all these same phases in 26.426s. These are separate observations; the successful full suite does not resolve or erase the standalone stall. Passive inspection established that files had been downloaded and one HTTP handler was awaiting request bytes; no Python State.lock deadlock or exact Swift cancellation/networking cause was proven. No unrelated production or harness fix was attempted. Evidence: `steam-library-lzma-green.log` / `.exit` (the historical filename predates its nonzero outcome) and `diagnostics/swiftc-full.stdout` / `.stderr` in `/workspace/host-harness-fixes/`.

The earlier dependency RED is separately preserved: `diagnostics/red-swiftc-full.stderr` shows `cannot find -llzma`; runtime `.so.5` exports thethree required symbols. With the verified development files, thefull suite links and exercisesreal LZMA decode. CI's originally truncated linker log remains insufficient to prove its exact library selection; explicit CI dependency setup is justified preparation, not a claimed retrospective diagnosis of that discarded output.

## Explicit delegation runner and complete diagnostics

The root agent subsequently authorized two additional test-only edits:

- `tests/host/run-checks.py`: optional repeat `--exclude NAME` records checks delegated to another job. With no exclusions, it still selects every discovered check and the required IPA validator. Unknown names, attempts to exclude `test-validate-ipa.py`, and selection of no host checks are errors (exit 2). JSON now records `discovered_total` and sorted, deduplicated `excluded` names separately from the selected checks and their summary. Exclusions never appear as successful check results.
- `tests/host/check-steam-library.py`: failed compiler invocations now retain complete stderr, replacing the 6,000-character tail that concealed early linker messages. No app or runtime behavior changed.

Seven selection fixtures first failed on the old runner and then all passed. The original three runner fixtures also pass. A diagnostic regression using a compiler error longer than 6,000 characters first failed against the original branch, then passed with the complete first and last errors retained. All **11 fixture tests** were independently rerun and passed; the reviewer found no actionable correctness or scope issues. Evidence is `runner-exclusions-{red,green}.log`, `steam-library-diagnostics-{red,green}.log`, and the test scripts in `/workspace/host-harness-fixes/`.

A real prepared-dependency run of the final runner completed on 2026-10-24 at 05:27:49 UTC:

```bash
python3 tests/host/run-checks.py --output-dir /workspace/validation-delegated-full \
  --exclude check-jit-network.py --exclude check-steam-cloud.py
```

Its JSON records **50 discovered**, exactly those **2 explicitly delegated** names, **48 executed / 48 passed / 0 failed**, and runner **exit 0**. Every selected check has a log, and neither delegated check is mislabeled as a pass. Full artifact: `/workspace/validation-delegated-full/`; invocation output/exit: `delegated-full-suite.log` and `.exit` in the fixes directory. The same prepared dependency environment listed above was used, with bytecode generation disabled.

The default full-inventory run before adding selection remains preserved: 48/50 pass with the two unsupported Linux module checks returning failure. The standalone diagnostic interruption timeout remains unresolved and is not erased by either successful Steam library suite run. The root agent coordinates the two Apple checks in their separate strict macOS job. This agent did not modify any workflow, commit, or push.

Final source ownership is five test/runner files: the initial three harness corrections, `run-checks.py`, and the one-line Steam library diagnostic change. Exact patch: `/workspace/host-harness-fixes/final-test-changes.patch`.
