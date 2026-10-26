import SwiftUI

@main
struct MadeiraApp: App {
    @State private var showingDiagnostics = false
    var body: some Scene {
        WindowGroup {
            ContentView()
                .overlay(alignment: .topTrailing) {
                    Button("Diagnostics") { showingDiagnostics = true }
                        .font(.caption2).padding(6)
                        .background(.regularMaterial, in: Capsule())
                        .padding(8)
                }
                .sheet(isPresented: $showingDiagnostics) { MadeiraDiagnosticsSettings() }
                .modifier(ClaimGamepadEvents())
                .onAppear {
                    GamepadInput.shared.start()
                    HardwareInput.shared.start()
                    JITNetworkShortcut.shared.restoreLeftover()   // also starts its network path monitor
                }
                // madeira://jit-network/...: the Madeira JIT shortcut returning (JITNetwork.swift).
                .onOpenURL { url in JITNetworkShortcut.shared.handle(url) }
        }
    }
}


/// Explicit opt-in. GitHub fine-grained token needs Issues: Read and write
/// permission on R347H4CK3R/madeira-cod-test only. Never add a token to source.
private struct MadeiraDiagnosticsSettings: View {
    @State private var token = ""
    @State private var enabled = CrashTelemetry.shared.enabled
    @State private var status = ""
    var body: some View {
        NavigationStack {
            Form {
                Section("Pre-crash diagnostics") {
                    Toggle("Upload sanitized events to GitHub Issue #1", isOn: $enabled)
                        .onChange(of: enabled) { _, value in
                            CrashTelemetry.shared.setEnabled(value)
                        }
                    Text("Uploads are opt-in. Only fixed error codes and counts are sent, not complete game logs or account data. Events are also saved on device.")
                        .font(.footnote)
                    SecureField("Fine-grained GitHub token (Issues: write)", text: $token)
                        .textInputAutocapitalization(.never)
                        .autocorrectionDisabled()
                    Button("Save token securely") {
                        status = CrashTelemetry.shared.saveToken(token) ? "Token saved in device Keychain." : "Token could not be saved."
                        token = ""
                    }
                    Button("Submit queued events") { CrashTelemetry.shared.uploadNow(); status = "Submission requested if enabled and events are queued." }
                    Button("Disable and remove token", role: .destructive) {
                        CrashTelemetry.shared.clearToken(); enabled = false; token = ""
                        status = "Telemetry disabled and token removed."
                    }
                    Text(status).font(.footnote)
                }
            }
            .navigationTitle("Diagnostics")
        }
    }
}
