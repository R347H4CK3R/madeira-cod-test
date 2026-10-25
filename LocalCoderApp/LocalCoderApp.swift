import SwiftUI
import WebKit
import FoundationModels

@main struct LocalCoderApp: App {
    var body: some Scene { WindowGroup { ContentView().preferredColorScheme(.dark) } }
}
@MainActor @Observable final class LocalEngine {
    var prompt = ""
    var messages: [String] = []
    var busy = false
    var status = ""
    private var session: LanguageModelSession?
    func send() async {
        let value = prompt.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !value.isEmpty && !busy else { return }
        guard SystemLanguageModel.default.isAvailable else { status = "Apple on-device model unavailable. Check Apple Intelligence settings."; return }
        prompt = ""
        messages.append("You: " + value)
        busy = true
        defer { busy = false }
        do {
            if session == nil { session = LanguageModelSession(instructions: "Assist with programming. You cannot execute code locally; use the Windows tab for commands and builds.") }
            let reply = try await session!.respond(to: value)
            messages.append("Local AI: " + reply.content)
            status = ""
        } catch { status = error.localizedDescription }
    }
}
struct ContentView: View {
    @State private var engine = LocalEngine()
    var body: some View {
        TabView {
            NavigationStack {
                VStack {
                    ScrollView { LazyVStack(alignment: .leading, spacing: 14) { ForEach(engine.messages.indices, id: \.self) { i in Text(engine.messages[i]).textSelection(.enabled).frame(maxWidth: .infinity, alignment: .leading) } }.padding() }
                    if !engine.status.isEmpty { Text(engine.status).font(.caption).foregroundStyle(.orange) }
                    if engine.busy { ProgressView() }
                    HStack {
                        TextField("Ask about code", text: $engine.prompt, axis: .vertical)
                        Button("Send") { Task { await engine.send() } }.disabled(engine.busy)
                    }.padding()
                }.navigationTitle("Local AI")
            }.tabItem { Label("Local", systemImage: "cpu") }
            NavigationStack {
                RemoteView(url: URL(string: "https://gaminglaptop.tail54e01b.ts.net")!)
                    .navigationTitle("Windows Code")
            }.tabItem { Label("Windows", systemImage: "laptopcomputer") }
        }
    }
}
struct RemoteView: UIViewRepresentable {
    let url: URL
    func makeUIView(context: Context) -> WKWebView {
        let view = WKWebView()
        view.load(URLRequest(url: url))
        return view
    }
    func updateUIView(_ uiView: WKWebView, context: Context) {}
}
