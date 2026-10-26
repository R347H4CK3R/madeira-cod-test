# PocketForge — iOS App Workbench

PocketForge is an experimental iPhone application for on-device AI-assisted app authoring, diagnostic logs, IPA inspection, limited metadata repair, and temporary HTML/JavaScript app previews.

## Installation

1. Download the **PocketForge-unsigned.ipa** artifact from a successful GitHub Actions run.
2. Sign the IPA using a compatible iOS sideloading/signing method and a provisioning profile that allows the app identifier **dev.pocketforge.studio**.
3. Install on an iPhone running iOS 26 or later. The new bundle identifier is separate from LocalCoder and does not automatically migrate its sandbox data.
4. Local AI requires availability of Apple's Foundation Models on the actual phone; iOS version alone does not guarantee support.

## Use

### AI Chat
Send programming questions to the on-device model. The attachment (+) menu accepts logs, source and IPA archives. The App Build menu can generate SwiftUI source as an editable ZIP, or create a **runnable HTML5 web app** for a temporary in-app preview. The Swift project ZIP is *source*, not a compiled executable.

### Temporary Run
In **Create App**, edit HTML/JavaScript and select **Run temporarily**. The preview uses a nonpersistent WKWebView data store; its browser cookies and web storage are not retained. Generated source/project exports and temporary imported files may remain in the app's temporary file storage until system cleanup. The preview cannot run native iOS Mach-O binaries or imported IPAs.

### Create unsigned IPA
In **Create App**, select **Build unsigned IPA** to package HTML/JavaScript in a precompiled WebKit shell. Export the IPA via the share sheet, then sign it separately for installation.

### Repair
Import an IPA or ZIP, diagnostic log, and/or describe the problem. **Find source automatically** scans the archive for source or project metadata. Public repository search produces unverified candidates, not proven matches. **Analyze compiled binary evidence** extracts bounded file/resource inventory and printable strings.

**Auto-diagnose, repair & export when possible** supports narrowly scoped metadata repair (missing display name). Otherwise it can generate a distinct starter WebKit app, **not** a functional recreation of the imported app. The original archive remains unchanged.

### Native / SDK
Native tab generates/exports editable Swift or Objective-C projects. SDK tab provides an iPhoneOS SDK import/probe UI, but Nyxian compile/link jobs and on-iPhone native executable execution are **not operational or verified**.

## Build

This source uses XcodeGen (`project.yml`), ZIPFoundation, SwiftUI, WebKit, and a GitHub Actions macOS runner with Xcode 26. The workflow `.github/workflows/localcoder-build.yml` compiles PocketForge and WebShell, fetches Nyxian v0.11.4 frameworks, then packages an unsigned IPA. Review upstream license obligations before redistributing Nyxian framework binaries.

With XcodeGen installed, run `xcodegen generate` followed by `xcodebuild -project PocketForge.xcodeproj -scheme PocketForge -sdk iphoneos -destination 'generic/platform=iOS' CODE_SIGNING_ALLOWED=NO build`. To produce an IPA use the full GitHub workflow.

## Limitations

- No universal decompiler can restore the exact original Swift or Objective-C source, comments, or application behavior from a compiled IPA.
- Full automatic recreation of missing gameplay, interfaces, network dependencies, and native behavior is not implemented.
- iOS code-signing, entitlements and sandboxing prevent arbitrary native IPA execution inside another ordinary app.
- The local AI model may not be available on all iPhones.
- An unsigned IPA cannot normally be installed without signing.
- A successful GitHub IPA archive build does not imply successful operation on a physical iPhone.

## Identity

- Display name: PocketForge
- Main bundle ID: `dev.pocketforge.studio`
- WebShell bundle ID: `dev.pocketforge.webshell`
- Existing source directory names `LocalCoderApp/` and `WebShell/` remain for compatibility.

## Troubleshooting

If a file can't be selected, test the UIKit Files import control and report its error. If source generation says the local model is unavailable, verify supported Apple Intelligence/Foundation Models. For crashes, import a full diagnostic log and matching IPA in **Repair**. If metadata repair reports 'display name already exists', the diagnosis is not a match for that repair; do not treat a replacement WebKit starter as a repaired original executable.
