# LocalCoder native compiler integration — verified scope

Date: 2026-10-25

## Upstream candidate
- https://github.com/emexlab/Nyxian
- Native compiler APIs: `Frameworks/CoreCompiler/Tools/Compiler/CCSwiftCompiler.h` exposes `CCSwiftCompilerJobExecute`, `CCCompiler.h` exposes `CCCompilerJobExecute`.
- SDK API: `Frameworks/CoreCompiler/Tools/CCSDK.h` exposes `CCSDKCreateWithDirectoryURL`.
- Upstream submodule `LLVM-On-iOS` and additional runtime frameworks are required.
- Inspect per-file MIT headers, upstream LICENSES, and dependency license notices before bundling.

## Must pass before enabling native Compile button
1. Build CoreCompiler, Clang/LLVM, Swift frontend and Mach-O linker for arm64 iOS using compatible frameworks.
2. Bundle licensed iOS SDK resources and include third-party notices.
3. Run offline on a physical iPhone; compile C and Objective-C smoke-test objects and link a basic unsigned .app.
4. Run offline Swift and SwiftUI smoke builds. Swift support is NOT established just because a header exports CCSwiftCompilerJobExecute.
5. Check resulting binary architecture and bundle executable / Info.plist, then assemble Payload/… .app and archive.
6. Ensure diagnostics are returned to UI, no success reported on failed compile, and source project stays unchanged on failure.
7. No signing functionality required; output unsigned IPAs.

## Current status
- LocalCoder's offline WebKit template-based HTML-to-IPA builder: implemented.
- LocalCoder native Swift / Objective-C source archive exporter: implemented.
- Nyxian compiler binaries integrated: NO.
- Native compiler SDK bundled: NO.
- iPhone-native Swift or Objective-C compilation tested: NO.
- Working all-native unsigned IPA builder: NOT YET.

This document describes acceptance criteria, not a verified native build.
