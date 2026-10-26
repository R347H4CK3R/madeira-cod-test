import SwiftUI
import ZIPFoundation

@MainActor @Observable final class WebAppBuilder {
    var html = "<!doctype html><html><head><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"></head><body><h1>Hello iPhone!</h1><button onclick=\"alert('Working')\">Tap</button></body></html>"
    var appName = "MyOfflineApp"
    var bundleID = "com.example.offlineapp"
    var status = "This bundles HTML and JavaScript into a precompiled iOS shell. No native code compilation occurs on the phone."
    var output: URL?
    var showingPreview = false
    func exportIPA() {
        do {
            guard let templateZip = Bundle.main.url(forResource: "OfflineTemplate", withExtension: "zip") else {
                status = "Offline executable template is missing."
                return
            }
            let allowed = CharacterSet(charactersIn: "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-")
            guard bundleID.split(separator: ".").count >= 2, bundleID.unicodeScalars.allSatisfy({allowed.contains($0)}) else {
                status = "Invalid bundle identifier."
                return
            }
            let fm = FileManager.default
            let root = fm.temporaryDirectory.appendingPathComponent(UUID().uuidString, isDirectory:true)
            defer { try? fm.removeItem(at:root) }
            try fm.createDirectory(at:root,withIntermediateDirectories:true)
            try fm.unzipItem(at:templateZip,to:root)
            let app = root.appendingPathComponent("Payload/OfflineApp.app")
            let manifest = app.appendingPathComponent("Info.plist")
            guard let plist = NSMutableDictionary(contentsOf:manifest),
                  let executable = plist["CFBundleExecutable"] as? String,
                  fm.fileExists(atPath:app.appendingPathComponent(executable).path) else {
                status = "Template is invalid: missing executable or manifest."
                return
            }
            plist["CFBundleIdentifier"] = bundleID
            plist["CFBundleDisplayName"] = appName
            guard plist.write(to:manifest,atomically:true) else { throw CocoaError(.fileWriteUnknown) }
            let page = app.appendingPathComponent("index.html")
            try fm.createDirectory(at:page.deletingLastPathComponent(),withIntermediateDirectories:true)
            try html.write(to:page,atomically:true,encoding:.utf8)
            let signature = app.appendingPathComponent("_CodeSignature")
            if fm.fileExists(atPath:signature.path) { try fm.removeItem(at:signature) }
            let outputURL = fm.temporaryDirectory.appendingPathComponent("LocalCoder-"+UUID().uuidString+".ipa")
            try fm.zipItem(at:root.appendingPathComponent("Payload"),to:outputURL,shouldKeepParent:true)
            output = outputURL
            status = "Created an unsigned IPA on this iPhone. Uses a precompiled WebKit executable; HTML/JavaScript is editable."
        } catch { status = "Packaging failed: \(error.localizedDescription)" }
    }
}
struct WebAppBuilderView: View {
    @State private var builder = WebAppBuilder()
    var body: some View {
        NavigationStack {
            VStack(alignment:.leading,spacing:8) {
                TextField("App name",text:$builder.appName).textFieldStyle(.roundedBorder)
                TextField("Bundle identifier",text:$builder.bundleID).textFieldStyle(.roundedBorder).textInputAutocapitalization(.never)
                Text("HTML / JavaScript").font(.headline)
                TextEditor(text:$builder.html).font(.system(size:12,design:.monospaced)).autocorrectionDisabled().textInputAutocapitalization(.never)
                Text(builder.status).font(.caption).foregroundStyle(.secondary)
                HStack {
                    Button("Run temporarily") { builder.showingPreview = true }.buttonStyle(.bordered)
                    Button("Build unsigned IPA") { builder.exportIPA() }.buttonStyle(.borderedProminent)
                    if let output=builder.output { ShareLink(item:output) { Label("Export",systemImage:"square.and.arrow.up") } }
                }
            }.padding().navigationTitle("PocketForge Builder")
            .sheet(isPresented:$builder.showingPreview) { EphemeralAppPreview(html:builder.html) }
        }
    }
}
