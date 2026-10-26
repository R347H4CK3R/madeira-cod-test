# Prebuilt Nyxian compiler inventory — 0.11.4

Recorded 2026-10-25 from successful GitHub Actions inspection run 40265524087.

## Verified official release
https://github.com/emexlab/Nyxian/releases/tag/0.11.4
- Nyxian.ipa: 111250101 bytes
- Payload/Nyxian.app/Frameworks/CoreCompiler.framework/CoreCompiler: 185478184 bytes uncompressed
- Payload/Nyxian.app/Frameworks/MobileDevelopmentKit.framework/MobileDevelopmentKit: 117312 bytes uncompressed
- Payload/Nyxian.app/Frameworks/OpenSSL.framework/OpenSSL and compiler-owned nested Swift support libraries
- Frameworks directory: ~204 MB unpacked
- Shared directory: ~41 MB unpacked; includes Shared/swift.zip, templates and runtime resources
- MobileDevelopmentKit links to @rpath/CoreCompiler.framework/CoreCompiler
- CoreCompiler also links to multiple @rpath/lib_CompilerSwift*.dylib shipped inside its own Frameworks subdirectory

## Integration implications
- Do not copy a single CoreCompiler binary; include nested dylibs, dependency frameworks, linker/SDK runtime resources, and correct rpaths/signature handling.
- Need to determine whether Nyxian's SDK bootstrap can be embedded/distributed, and preserve upstream AGPL/EPSL/MIT + dependency license terms.
- Prebuilt IPA does not prove CoreCompiler can start in LocalCoder's process or that its APIs are safe without its parent Nyxian lifecycle.
- Need independent on-device Swift, Objective-C, and link-to-Mach-O acceptance tests. Unsigned IPA packaging alone is not proof.

## Verification artifact
https://github.com/R347H4CK3R/madeira-cod-test/actions/runs/40265524087

## Current delivery status
Standalone LocalCoder release remains small and does not contain this toolchain. No validated integrated native compiler IPA yet.
