# macOS platform host validation — 2026-10-24

**Authoritative result: SUCCESS.** [Strict run40065715371](https://github.com/R347H4CK3R/madeira-cod-test/actions/runs/40065715371), job120788419817, commit `09a7e152130d9c551f0f527e68dafd53f264d5b1`, branch `fix/cod-1938090-ipa-20261024`, completed at2026-10-24T05:18:58Z.

The workflow `.github/workflows/cod-platform-checks.yml` explicitly sets `defaults.run.shell: bash`. Actual logs show `/bin/bash --noprofile --norc -e -o pipefail {0}` for both test pipelines, so `tee` cannot conceal a nonzero Python exit. Both test steps and artifact upload completed with success. No test failure or skip was present.

Runner/compiler: `macos-15`, Apple Swift6.1.2 (`swiftlang-6.1.2.1.2 clang-1700.0.13.5`), target `arm64-apple-macosx15.0`.

| Check | Actual stdout | Meaning |
|---|---|---|
| `tests/host/check-jit-network.py` |22 PASS lines, ALL PASS | Source wiring checks plus compilation/execution of production Darwin LoopbackProbe: listening/closed socket behavior, route interface detection, VPN gating, LocalDevVPN address classification |
| `tests/host/check-steam-cloud.py` |27 PASS lines, ALL PASS | Source guards plus compiled production Swift/CryptoKit cloud comparison and planning logic: one/two-sided conflicts, missing/deleted save semantics, reset-prefix protection, SteamID path substitution and SHA comparison over synthetic files |

Artifact: [Madeira-macOS-host-checks](https://github.com/R347H4CK3R/madeira-cod-test/actions/runs/40065715371/artifacts/12549561045), ID12549561045,2216bytes, not expired, retention until2026-11-07T05:18:52Z, GitHub digest `sha256:dbbef78395c0e7af9a273a8889d56ed124c775121fb47253a403ae137055bfbd`. Contains configured `build/platform-host-results` output (Swift version and the two logs). Connector download returned a reusable ZIP file reference (`file_00000000369081f79b6c81f7ba9acc91`); direct materialization of that signed storage URL in this workspace was denied by its network proxy403. Therefore archive content/hash were not independently inspected locally; the test output and explicit strict shell were inspected in the complete decoded GitHub job log.

Full strict job stdout is saved at `/workspace/ci-platform-strict-job.log`; first-revision stdout at `/workspace/ci-platform-previous-job.log`.

Prior run [40065638782](https://github.com/R347H4CK3R/madeira-cod-test/actions/runs/40065638782) also actually printed22 JIT PASS,27 Cloud PASS and ALL PASS for each, with no FAIL. Its unspecified shell used `/bin/bash -e {0}` without pipefail, so it is supplementary evidence; the strict run above is authoritative.

These are host tests. They do not establish iPhone JIT attachment, real Steam Cloud network behavior, the main IPA build result, COD launch, or gameplay. Main IPA workflow40064483490 is independently monitored by the build agent.

## Strict stdout assertions

```text
PASS: JITNetwork.swift is built by the Xcode project
PASS: the check targets lockdownd through LocalDevVPN's loopback (10.7.0.1:62078, StikDebug's address)
PASS: Enable JIT checks the loopback before any JIT method
PASS: the shortcut runs only when the loopback does not answer and the shortcut is turned on
PASS: a JIT attempt that fails after the shortcut ran puts back what it changed
PASS: "start" asks for the cellular step only without Wi-Fi, and records the "done" it owes before it runs
PASS: "done" disconnects LocalDevVPN when no VPN was on, restores the one the shortcut kept, and leaves VPNs alone when LocalDevVPN was already on or "start" did not report
PASS: the shortcut needs no file (no iCloud Drive or folder to set up)
PASS: Madeira neither logs nor keeps the VPN's name (the shortcut keeps the VPN itself)
PASS: Madeira JIT.shortcut is a signed export (AEA1 with a signing certificate chain)
PASS: Madeira JIT.shortcut is copied into the app
PASS: the file's name is the shortcut's name Madeira runs (Shortcuts names an import after its file)
PASS: the shortcut is offered on iOS 27 or later only (it uses Store Content)
PASS: setup offers it on its own page after any of the three JIT guides, so the guides fit on one screen
PASS: setup's page and Settings › JIT add it from its iCloud link (straight to Add Shortcut), and Madeira's copy through the share sheet with no connection
PASS: the iCloud link and the bundled file are kept as one shortcut
PASS: setup no longer says the pairing file is in Documents
PASS: a listening port connects in 0.5 ms (connected via lo0 127.0.0.1)
PASS: the route check names the interface traffic leaves by (lo0), and lo0 is not a VPN
PASS: a listener that accepts, reached other than through a VPN, does not count, and is never connected to (0.2 ms, routed via lo0, not a VPN)
PASS: a closed port fails at once (0.4 ms, Connection refused via lo0)
PASS: LocalDevVPN is told from another VPN by its tunnel address: utun5 10.7.1.1 is LocalDevVPN; utun5 172.19.0.1 (a VPN carrying all traffic) and en0 are not
ALL PASS

PASS: Steam Cloud is on unless turned off (env.MADEIRA_STEAM_CLOUD = 0)
PASS: Play on a game not checked yet in this app run syncs it first, without asking
PASS: an upload fetches the cloud's copy of every file it replaces before the batch opens
PASS: the cloud's copies go to the backup's cloud/ folder
PASS: backups are in Documents (Files › Madeira › Steam Cloud Backups)
PASS: keeping this device's side leaves a missing save missing instead of uploading nothing
PASS: changed on this device only: uploaded
PASS: changed in the cloud only: downloaded
PASS: changed on both sides: a choice
PASS: different with no record: a choice
PASS: new in the cloud: downloaded
PASS: new on this device: uploaded
PASS: deleted in the cloud: not sent back
PASS: identical on both sides: recorded, replacing any mark
PASS: synced before and missing here: a choice, not ignored
PASS:   and the record is marked missing
PASS:   still a choice while marked
PASS:   the mark is not rewritten
PASS: (no mark: a fresh save would go up unasked)
PASS: a save that reappears after it went missing: a choice, never uploaded unasked
PASS:   also when the cloud moved on
PASS: left missing by choice: not asked again
PASS:   the cloud's copy changed since: downloaded (nothing here to lose)
PASS:   a new save of that name later: a choice
PASS: a device-only save in a {64BitSteamID} folder is found
PASS:   its cloud name has the ID filled in (%GameInstall%savedata/76561198000000001/data_0.sav)
PASS:   and once the cloud lists it under that name, the two are the same file
ALL PASS
```
