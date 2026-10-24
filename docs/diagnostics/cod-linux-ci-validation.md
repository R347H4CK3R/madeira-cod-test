# Successful Linux CI validation — run 40067923452

**Verified: all 48 selected Linux checks passed in real CI, with 0 failures.** The runner discovered 50 checks and explicitly recorded the two checks delegated to macOS. No selected check was omitted, relabeled as skipped, or converted from failure to success.

## Run and downloaded evidence

- Repository: `R347H4CK3R/madeira-cod-test`.
- Source: `50a27b789c378fbe4bf4e3424f5877d39b076141`.
- Run: https://github.com/R347H4CK3R/madeira-cod-test/actions/runs/40067923452
- Job: https://github.com/R347H4CK3R/madeira-cod-test/actions/runs/40067923452/job/120794962526
- Job `linux-host-checks`, ID `120794962526`: completed **success**. All setup, dependency, test, and artifact-upload steps concluded success.
- Runner verified itself as Ubuntu 24.04 x86_64; Python version in results is 3.14.8.
- Test execution: 2026-10-24 05:55:10 to 05:58:14 UTC, approximately 184.5 seconds.
- Full decoded job stdout/stderr: `/workspace/ci-linux-40067923452-full.log` (216,554 characters).
- Job/artifact metadata: `/workspace/ci-linux-40067923452-metadata.json`.
- Artifact ID `12550640583`, name `Madeira-COD-host-checks`, size **66,080 bytes**; downloaded through the GitHub connector and Sediment file tool, below the 32 MiB limit.
- Downloaded ZIP: `/workspace/attachments/864e9332-480e-4fba-91e7-bea177c5e476/Madeira-COD-host-checks-40067923452.zip`.
- ZIP SHA-256 independently computed and matched to GitHub's artifact digest: `324a45930d91d095e2cdea4544944d74b55ec7716f084cc20da6371ff65ed3ed`.
- Extracted artifact: `/workspace/ci-linux-40067923452-artifact/`.

## Inventory and failure handling

`results.json` records:

```json
{
  "discovered_total": 50,
  "excluded": ["check-jit-network.py", "check-steam-cloud.py"],
  "summary": {"total": 48, "passed": 48, "failed": 0}
}
```

The complete selected filename list was independently compared with the `tests/host/check-*.py` files plus required `test-validate-ipa.py` at this exact source revision, minus the two recorded exclusions. The lists match in order, contain 48 unique checks, and every selected check has a log. All 48 raw JSON exit codes and corresponding log footers are zero. Job stdout independently ends with `48/48 checks passed; 0 failed.`

The committed workflow enables Bash `set -euo pipefail`, has no `continue-on-error` or `|| true`, and records both delegation names before executing checks. GitHub reports the test step itself as successful. The exclusions are not counted as passing checks. The two Apple checks previously passed in strict macOS CI run `40065715371`, job `120788419817`, as recorded separately in `/workspace/ci-host-validation.md`.

## Compiler and dependency preparation

- The initial Swift cache lookup missed. CI downloaded the official Swift 6.2.3 Ubuntu 24.04 archive and its pinned SHA-256 verification printed `madeira-swift623.tar.gz: OK`.
- Actual compiler output: `Swift version 6.2.3 (swift-6.2.3-RELEASE)`, target `x86_64-unknown-linux-gnu`.
- The Foundation program compiled and printed `Swift Foundation smoke test passed`.
- The verified compiler prefix was then cached using the Linux/X64/checksum key. No unsupported setup-action version catalog was used.
- Host dependencies installed successfully, including `bison`, `flex`, and `liblzma-dev` (Ubuntu package `5.6.1+really5.4.5-1ubuntu0.4`).
- Native Wine configuration with `--without-mingw`, `--without-x`, and `--without-freetype` completed. `make -j2 include/all` built the generated headers successfully; `MADEIRA_WINE_BUILD` pointed at that build for the checks.
- Full setup evidence is retained in `runner-platform.log`, `swift-install.log`, `swift-version.log`, `swift-smoke-compile.log`, `swift-smoke-run.log`, `host-dependencies.log`, `wine-configure.log`, and `wine-headers.log` inside the artifact. Wine configuration's optional subsystem warnings do not indicate failure of this header preparation.

## Substantive runtime/regression results

- ARM64EC bootstrap regression: all four cases passed against the patched production loader, including local x64 CRT avoidance during bootstrap and preserved ordinary local-first application search.
- IPA validator: all 23 regression tests passed.
- Dock contract, Steam games, and swap coverage corrected harnesses passed.
- Steam library: all six phases (units, interruption, resume, update, uninstall, and licensed-depot refusal) ran clean under AddressSanitizer; exit 0, 18.861 seconds.
- WMA: parameter search on and off each reported `PASS: 0 failure(s)`, including random-byte concealment; exit 0, 24.056 seconds.

Two existing optional omissions remain visible within successful scripts: Dock installers did not execute `cmd.exe` batch flow because it was not reachable, and the parser test had no optional real-MP3 fixture. These were not script omissions or converted runner failures; they limit claims about those individual optional cases.

The earlier standalone verbose Steam-library diagnostic interruption timeout remains recorded as unresolved. This successful CI execution supplies a separate passing result and does not establish the cause of that intermittent stall.

This validation applies to the exact source revision above. The subsequently planned FEX guard regression may expand the inventory to 51 discovered / 49 Linux checks; that new case was not present in this run and is not claimed as tested here. Host-test success does not establish an IPA artifact or repair the separate native build's FEX source-guard failure. No source changes, commits, dispatches, or CI retries were performed by this agent during this verification.

## Complete selected check results

| Check | Exit | Seconds |
| --- | ---: | ---: |
| `check-arm64ec-bootstrap.py` | 0 | 0.128 |
| `check-audio-downmix.py` | 0 | 0.563 |
| `check-audio-wow64.py` | 0 | 0.109 |
| `check-cfg-early-docs.py` | 0 | 0.486 |
| `check-config-catalog.py` | 0 | 7.1 |
| `check-control-presets.py` | 0 | 1.394 |
| `check-d3d9-splitlock.py` | 0 | 1.539 |
| `check-d9-upload-commit.py` | 0 | 0.808 |
| `check-dock-components.py` | 0 | 0.962 |
| `check-dock-contract.py` | 0 | 1.391 |
| `check-dock-gdi-section.py` | 0 | 0.079 |
| `check-dock-installers.py` | 0 | 2.58 |
| `check-dock-path.py` | 0 | 0.316 |
| `check-dock-report.py` | 0 | 0.749 |
| `check-dock-start-screen.py` | 0 | 1.938 |
| `check-fastsync.py` | 0 | 37.628 |
| `check-filtering-cap.py` | 0 | 0.807 |
| `check-frontend.py` | 0 | 1.603 |
| `check-gamepad.py` | 0 | 0.125 |
| `check-hardware-input.py` | 0 | 0.892 |
| `check-image-retire.py` | 0 | 0.16 |
| `check-jit-method.py` | 0 | 0.074 |
| `check-jit-pairing.py` | 0 | 34.818 |
| `check-launch-routing.py` | 0 | 0.144 |
| `check-lazy-windows.py` | 0 | 3.295 |
| `check-library-api.py` | 0 | 1.158 |
| `check-library-sections.py` | 0 | 0.023 |
| `check-nav-keys.py` | 0 | 0.07 |
| `check-nsi-network.py` | 0 | 1.671 |
| `check-onboarding.py` | 0 | 0.696 |
| `check-readonly-link.py` | 0 | 0.137 |
| `check-runtime-settings.py` | 0 | 1.272 |
| `check-scene-batching.py` | 0 | 0.594 |
| `check-section-abort.py` | 0 | 0.273 |
| `check-small-va-band.py` | 0 | 0.148 |
| `check-steam-games.py` | 0 | 3.302 |
| `check-steam-library.py` | 0 | 18.861 |
| `check-steam-signin-native.py` | 0 | 2.131 |
| `check-swap-coverage.py` | 0 | 0.243 |
| `check-touch-gamepad.py` | 0 | 0.478 |
| `check-unixlib-binder.py` | 0 | 0.109 |
| `check-wg-parser.py` | 0 | 27.744 |
| `check-win32u-zero-bits.py` | 0 | 0.099 |
| `check-wma-decoder.py` | 0 | 24.056 |
| `check-wow-context.py` | 0 | 0.058 |
| `check-wow-cpu-area.py` | 0 | 0.207 |
| `check-wow-sweep.py` | 0 | 0.702 |
| `test-validate-ipa.py` | 0 | 0.746 |
