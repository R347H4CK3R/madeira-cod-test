import Foundation
import ZIPFoundation

enum SourceDiscovery {
    static func inspect(_ url: URL) -> String {
        do {
            let archive = try Archive(url:url, accessMode:.read)
            let entries = Array(archive)
            let code = entries.filter { e in
                let p = e.path.lowercased()
                return p.hasSuffix(".swift") || p.hasSuffix(".m") || p.hasSuffix(".mm") || p.hasSuffix(".h") || p.hasSuffix(".c") || p.hasSuffix(".cpp")
            }
            let metadata = entries.filter { e in
                let p = e.path.lowercased()
                return p.hasSuffix(".git/config") || p.hasSuffix("package.swift") || p.hasSuffix("project.pbxproj") || p.hasSuffix("readme.md")
            }
            var lines = ["Source candidates in archive: \(code.count)"]
            lines += code.prefix(30).map { "• " + $0.path }
            if !metadata.isEmpty { lines += ["Project metadata:"] + metadata.prefix(15).map { "• " + $0.path } }
            if code.isEmpty {
                lines.append("No original source found inside the IPA. Executable machine code cannot reliably reconstruct its original source.")
                lines.append("Next: look for a verified matching source repository using bundle identifier, version, and executable UUID. Never assume a similarly named public repository is the correct source.")
            } else {
                lines.append("Candidates only: confirm they match the installed executable before applying changes.")
            }
            return lines.joined(separator:"\n")
        } catch { return "Source scan failed: \(error.localizedDescription)" }
    }
}
