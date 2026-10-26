import SwiftUI
import WebKit
import FoundationModels
import ZIPFoundation
import UniformTypeIdentifiers
import UIKit

@main struct LocalCoderApp: App {
    var body: some Scene { WindowGroup { MainScreen().preferredColorScheme(.dark) } }
}
@MainActor @Observable final class Brain {
    var prompt = ""
    var lines: [String] = []
    var error = ""
    var busy = false
    var attachments = AttachmentStore()
    private var session: LanguageModelSession?
    func send() async {
        let value = prompt.trimmingCharacters(in: .whitespacesAndNewlines)
        guard (!value.isEmpty || !attachments.items.isEmpty) && !busy else { return }
        guard SystemLanguageModel.default.isAvailable else { error = "Apple on-device model unavailable. Enable Apple Intelligence."; return }
        let attachmentNames = attachments.items.map(\.name)
        let attachmentContext = attachments.consumeContext()
        prompt = ""
        lines.append("You: " + value + (attachmentNames.isEmpty ? "" : "\nAttachments: " + attachmentNames.joined(separator: ", ")))
        busy = true
        defer { busy = false }
        do {
            if session == nil {
                session = LanguageModelSession(instructions: "You are an iOS programming assistant. Help diagnose Swift, Xcode, app and IPA problems. You cannot compile native Swift iOS applications directly on a normal iPhone. Archive inspection is local, but source-code changes need an actual builder. Never claim you ran tests or signed code.")
            }
            let answer = try await session!.respond(to: value + (attachmentContext.isEmpty ? "" : "\n\nAttached file context:\n" + String(attachmentContext.prefix(35000))))
            lines.append("AI: " + answer.content)
            error = ""
        } catch { self.error = error.localizedDescription }
    }
}
@MainActor @Observable final class ArchiveInspector {
    var report = "Choose an IPA from Files to inspect its structure locally."
    var filename = ""
    func inspect(_ url: URL) {
        guard ["ipa", "zip"].contains(url.pathExtension.lowercased()) else { report = "Select an IPA or ZIP file."; return }
        let access = url.startAccessingSecurityScopedResource()
        defer { if access { url.stopAccessingSecurityScopedResource() } }
        do {
            let destination = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString + ".ipa")
            try FileManager.default.copyItem(at: url, to: destination)
            defer { try? FileManager.default.removeItem(at: destination) }
            let archive = try Archive(url: destination, accessMode: .read)
            let entries = Array(archive)
            let apps = entries.filter { $0.path.hasPrefix("Payload/") && $0.path.hasSuffix(".app/Info.plist") }
            let binaries = entries.filter { $0.path.hasSuffix("/_CodeSignature/CodeResources") }
            let frameworks = entries.filter { $0.path.contains(".app/Frameworks/") && $0.path.hasSuffix(".framework/") }
            var lines = ["Archive: \(url.lastPathComponent)", "Entries: \(entries.count)", "App manifests: \(apps.count)", "Code signature resources: \(binaries.count)", "Embedded frameworks: \(frameworks.count)"]
            if let entry = apps.first {
                var data = Data()
                _ = try archive.extract(entry, consumer: { data.append($0) })
                if let plist = try PropertyListSerialization.propertyList(from: data, format: nil) as? [String: Any] {
                    for key in ["CFBundleIdentifier","CFBundleDisplayName","CFBundleExecutable","CFBundleShortVersionString","MinimumOSVersion"] {
                        lines.append("\(key): \(plist[key] ?? "missing")")
                    }
                }
            } else { lines.append("WARNING: No Payload/*.app/Info.plist found.") }
            if binaries.isEmpty { lines.append("Unsigned or signature files absent; installation requires signing.") }
            lines.append("Inspecting does not rebuild a native binary. Editing compiled executable code requires source/toolchain and produces a signature-invalidating change.")
            filename = url.lastPathComponent
            report = lines.joined(separator: "\n")
        } catch { report = "Inspection failed: \(error.localizedDescription)" }
    }
}
struct MainScreen: View {
    @State private var brain = Brain()
    @State private var inspector = ArchiveInspector()
    @State private var importFile = false
    @State private var importChatAttachment = false
    var body: some View {
        TabView {
            NavigationStack {
                VStack {
                    ScrollView { LazyVStack(alignment: .leading, spacing: 12) {
                        ForEach(brain.lines.indices, id: \.self) { index in Text(brain.lines[index]).textSelection(.enabled).frame(maxWidth: .infinity, alignment: .leading) }
                    }.padding() }.scrollDismissesKeyboard(.interactively)
                    if !brain.error.isEmpty { Text(brain.error).foregroundStyle(.orange).font(.caption) }
                    if brain.busy { ProgressView() }
                    if !brain.attachments.items.isEmpty {
                        ScrollView(.horizontal) {
                            HStack {
                                ForEach(brain.attachments.items) { item in
                                    HStack(spacing: 5) {
                                        Image(systemName: "paperclip")
                                        Text(item.name).lineLimit(1)
                                        Button { brain.attachments.remove(item.id) } label: { Image(systemName: "xmark.circle.fill") }
                                    }.font(.caption).padding(8).background(.gray.opacity(0.2)).clipShape(Capsule())
                                }
                            }
                        }.padding(.horizontal)
                    }
                    if !brain.attachments.error.isEmpty { Text(brain.attachments.error).font(.caption).foregroundStyle(.orange) }
                    HStack {
                        Menu {
                            Button("Choose from Files", systemImage: "folder") { importChatAttachment = true }
                        } label: { Image(systemName:"plus.circle.fill").font(.title2).accessibilityLabel("Add attachment") }
                        TextField("Describe an app or paste an error", text: $brain.prompt, axis: .vertical)
                        Button("Send") { Task { await brain.send() } }.disabled(brain.busy)
                    }.padding()
                    .sheet(isPresented: $importChatAttachment) {
                        UnrestrictedFilePicker(onPick: { url in
                            importChatAttachment = false
                            brain.attachments.add(url)
                        }, onFailure: { message in
                            importChatAttachment = false
                            brain.attachments.error = message
                        })
                    }
                }.navigationTitle("LocalCoder AI")
            }.tabItem { Label("AI Chat", systemImage: "bubble.left.and.bubble.right") }
            NavigationStack {
                ScrollView {
                    VStack(alignment: .leading, spacing: 16) {
                        Text("Diagnose an IPA offline").font(.title2).bold()
                        Button("Import IPA or ZIP") { importFile = true }.buttonStyle(.borderedProminent)
                        Text(inspector.report).font(.system(.footnote, design: .monospaced)).textSelection(.enabled)
                        ShareLink(item: inspector.report) { Label("Share diagnosis", systemImage: "square.and.arrow.up") }
                    }.padding()
                }.navigationTitle("IPA Inspector")
                .sheet(isPresented: $importFile) {
                    UnrestrictedFilePicker(onPick: { url in
                        importFile = false
                        inspector.inspect(url)
                    }, onFailure: { message in
                        importFile = false
                        inspector.report = message
                    })
                }
            }.tabItem { Label("Inspect", systemImage: "archivebox") }
            RepairView().tabItem { Label("Repair", systemImage: "wrench.and.screwdriver") }
            SourceEditorView().tabItem { Label("Source", systemImage: "chevron.left.forwardslash.chevron.right") }
            NativeCompilerView().tabItem { Label("Native", systemImage: "curlybraces") }
            SDKManagementView().tabItem { Label("SDK", systemImage: "externaldrive") }
            WebAppBuilderView().tabItem { Label("Create App", systemImage: "hammer") }
            BuildLocalView().tabItem { Label("Pack IPA", systemImage: "shippingbox") }
            FreeToolsView().tabItem { Label("Tools", systemImage: "square.grid.2x2") }
        }
    }
}
struct EmbeddedBrowser: UIViewRepresentable {
    let url: URL
    func makeUIView(context: Context) -> WKWebView { let view = WKWebView(); view.load(URLRequest(url: url)); return view }
    func updateUIView(_ webView: WKWebView, context: Context) {}
}
