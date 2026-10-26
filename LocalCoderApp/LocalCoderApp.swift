import SwiftUI
import WebKit
import FoundationModels
import ZIPFoundation
import UniformTypeIdentifiers

@main struct LocalCoderApp: App {
    var body: some Scene { WindowGroup { MainScreen().preferredColorScheme(.dark) } }
}
@MainActor @Observable final class Brain {
    var prompt = ""
    var lines: [String] = []
    var error = ""
    var busy = false
    private var session: LanguageModelSession?
    func send() async {
        let value = prompt.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !value.isEmpty && !busy else { return }
        guard SystemLanguageModel.default.isAvailable else { error = "Apple on-device model unavailable. Enable Apple Intelligence."; return }
        prompt = ""
        lines.append("You: " + value)
        busy = true
        defer { busy = false }
        do {
            if session == nil {
                session = LanguageModelSession(instructions: "You are an iOS programming assistant. Help diagnose Swift, Xcode, app and IPA problems. You cannot compile native Swift iOS applications directly on a normal iPhone. Archive inspection is local, but source-code changes need an actual builder. Never claim you ran tests or signed code.")
            }
            let answer = try await session!.respond(to: value)
            lines.append("AI: " + answer.content)
            error = ""
        } catch { self.error = error.localizedDescription }
    }
}
@MainActor @Observable final class ArchiveInspector {
    var report = "Choose an IPA from Files to inspect its structure locally."
    var filename = ""
    func inspect(_ url: URL) {
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
    var body: some View {
        TabView {
            NavigationStack {
                VStack {
                    ScrollView { LazyVStack(alignment: .leading, spacing: 12) {
                        ForEach(brain.lines.indices, id: \.self) { index in Text(brain.lines[index]).textSelection(.enabled).frame(maxWidth: .infinity, alignment: .leading) }
                    }.padding() }
                    if !brain.error.isEmpty { Text(brain.error).foregroundStyle(.orange).font(.caption) }
                    if brain.busy { ProgressView() }
                    HStack {
                        TextField("Describe an app or paste an error", text: $brain.prompt, axis: .vertical)
                        Button("Send") { Task { await brain.send() } }.disabled(brain.busy)
                    }.padding()
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
                .fileImporter(isPresented: $importFile, allowedContentTypes: [.zip, .data], allowsMultipleSelection: false) { result in
                    if case .success(let files) = result, let url = files.first { inspector.inspect(url) }
                    if case .failure(let error) = result { inspector.report = error.localizedDescription }
                }
            }.tabItem { Label("Inspect", systemImage: "archivebox") }
            SourceEditorView().tabItem { Label("Source", systemImage: "chevron.left.forwardslash.chevron.right") }
            NativeCompilerView().tabItem { Label("Native", systemImage: "curlybraces") }
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
