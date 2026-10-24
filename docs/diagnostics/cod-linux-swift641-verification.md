# Linux host cancellation fix — verified Swift 6.4.1

The unchanged Linux suite passes in real CI: **49/49 selected checks**, with **51 discovered** and the same two explicit macOS delegations (`check-jit-network.py`, `check-steam-cloud.py`). Steam library completed every interruption/resume/update/uninstall phase under AddressSanitizer in **19.513 seconds**. No production code, test assertion, request/resource timeout, phase threshold, or authentication/download behavior changed.

Swift 6.2.3's bundled FoundationNetworking contains the cancellation/response-completion deadlock documented in [issue 5412](https://github.com/swiftlang/swift-corelibs-foundation/issues/5412) and fixed by [PR 5417](https://github.com/swiftlang/swift-corelibs-foundation/pull/5417). Swift 6.4.1 includes that fix. In the identical frozen reproduction, both versions passed normal and mixed-status controls; 6.2.3's cancellation processes timed out twice, while 6.4.1 completed all 16 cancellation rounds. Source, fixture, compiler flags, task count and timeouts were held fixed.

The official Ubuntu 24.04 x86_64 archive was verified using the trusted Swift 6.x vendor key **52BB7E3DE28A71BE22EC05FFEF80A866B47A981F** before computing SHA-256:

`7d246c7114077ad01dba4ad897628446ada4c489d6c7dbcf39ae3f25cbe17e8b`

Probe [run 40072036246](https://github.com/R347H4CK3R/madeira-cod-test/actions/runs/40072036246), source **0447f4a0bb17de22da3fa0d9acd5d540540037a3**, passed actual cold-cache official installation, checksum, Swift 6.4.1/Foundation verification, Wine headers, all checks, and artifact upload. Only the Linux workflow version/URL/hash/cache/banner and exact probe branch trigger changed; no native CI run was triggered by the probe.

Artifact **12551477778**, 66,528 bytes, was downloaded through the supported Sediment tool. Its independently computed SHA-256 matches GitHub:

`4e10a02e8a6ebed1cdc765dbe84e5c038f475f5726b6b6822cc918106658f69b`

Primary evidence:

- CI inventory/raw exits: `/workspace/swift641-ci-validation/ci-artifact/results.json`; all per-check logs in that directory.
- Complete CI stdout/metadata: `/workspace/swift641-ci-validation/ci-full.log`, `ci-metadata.json`.
- Signature status: `/workspace/swift-host-641/verification/archive-signature.status`; manifest `verified-manifest.json` in the same directory.
- Frozen comparison: `/workspace/steam-library-root-cause-minimal/COMPARISON.txt` and versioned comparison logs.
- Source/release research: `/workspace/swift-cancellation-official-research.md`.
- Complete validation: `/workspace/swift641-ci-validation/verification.md`.

Earlier 6.2.3 interruption timeouts remain preserved as baseline failures. Existing optional Windows batch execution and real-MP3 fixture omissions are still explicit in their check logs. Host success is separate from native IPA packaging/device validation.
