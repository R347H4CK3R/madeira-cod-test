# Architecture decision: build LocalCoder on Nyxian, not the reverse

## Rationale
The user's non-negotiable feature is completely offline iPhone-native compilation of Swift and Objective-C into unsigned iOS apps. Nyxian already implements and ships a compiler, SDK management, Mach-O linker, extension/runtime services, and an iPhone-native IDE. Porting one large toolchain into LocalCoder is higher risk than integrating LocalCoder's chat, IPA inspection, and web-template builder into a Nyxian-based product.

## Primary path
1. Fork/build pinned emexlab/Nyxian sources with recursive LLVM-On-iOS and TrollStore/libroot dependencies; retain applicable licenses/notices.
2. Validate standalone Nyxian build and its CoreCompiler.framework + MobileDevelopmentKit.framework + resources.
3. Add LocalCoder's offline AI chat and IPA diagnostics as native screens inside the Nyxian host; do not replace its working project/execution lifecycle.
4. Preserve Nyxian compiler's SDK bootstrap; require first-time download if SDK cannot be legally bundled; operate offline thereafter.
5. Use existing Nyxian compile/link APIs and project model. Disable any signing step in the user's unsigned IPA export path.
6. Test, **on iPhone**, HelloWorld C, Objective-C UIKit, Swift, and SwiftUI; inspect Mach-O arm64 and IPA Payload/ structure.
7. Only ship as integrated when the compiled executable and diagnostics for these smoke tests work. Report unsupported project features individually rather than claiming unlimited support.

## Fallback
If upstream Nyxian fails to compile or its SDK has redistribution restrictions, offer the standalone Nyxian app to handle native compilation and keep LocalCoder for offline AI/source/IPA workflows. This is *not* a one-app solution and must be disclosed.

## Present state
Original Nyxian source build GitHub Actions run: 40256566844, compiler step ongoing at last check. This plan is not an integrated compiler or successful on-device smoke test.
