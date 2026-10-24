#!/usr/bin/env python3
"""Compile the pinned FEX diagnostic blocks with native and iOS producer guards.

The fixture uses the actual counter declarations and reporting code from Core.cpp.
Unpatched native compilation must reproduce the undeclared-counter failure. The
external patch must repair native compilation while preserving producer reports.
"""
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
SOURCE = 'FEXCore/Source/Interface/Core/Core.cpp'
ARM64_SOURCE = 'FEXCore/Source/Utils/ArchHelpers/Arm64.cpp'
PATCH = ROOT / 'build/patches/fex-native-diagnostic-guards.patch'


def diagnostic_code(source):
    declarations = source.split('#ifdef FEX_IOS_HOST\n#ifdef ARCHITECTURE_arm64ec\n', 1)[1]
    declarations = '#ifdef FEX_IOS_HOST\n#ifdef ARCHITECTURE_arm64ec\n' + declarations.split('\n#ifdef FEX_IOS_HOST\n/* ml648:', 1)[0]
    reports = source.split('  /* iOS-Madeira ml304 (task #51): REPORT CallbackPtr', 1)[1]
    reports = '  /* iOS-Madeira ml304 (task #51): REPORT CallbackPtr' + reports.split('  /* iOS-Madeira: refuse to compile obviously-invalid guest RIPs.', 1)[0]
    return declarations, reports


def program(source, producer):
    declarations, reports = diagnostic_code(source)
    prelude = '''#include <cstdint>
#include <cassert>
#include <cstring>
static unsigned ffs_reports, callback_reports;
namespace LogMan::Msg {
template<class... Args> void EFmt(const char* format, Args...) {
    if (std::strncmp(format, "[ffs-bypass]", 12) == 0) ++ffs_reports;
    else if (std::strncmp(format, "[cb-entry]", 10) == 0) ++callback_reports;
    else assert(false);
}
}
'''
    if producer:
        prelude = '#define FEX_IOS_HOST 1\n#define ARCHITECTURE_arm64ec 1\n' + prelude
    body = prelude + declarations + '\nstatic void report() {\n' + reports + '\n}\n'
    if not producer:
        return body + 'int main() { report(); assert(ffs_reports == 0 && callback_reports == 0); }\n'
    return body + '''extern "C" {
uint64_t IosCbEntryLog[8] {};
uint64_t IosFfsBypassLog[4] {};
}
int main() {
    report();
    assert(ffs_reports == 0 && callback_reports == 0);
    IosFfsBypassLog[0] = 1; IosFfsBypassLog[1] = 0x1234;
    IosCbEntryLog[6] = 1;
    report();
    assert(ffs_reports == 1 && callback_reports == 1);
    report();
    assert(ffs_reports == 1 && callback_reports == 1);
    IosFfsBypassLog[2] = 2; IosFfsBypassLog[3] = 0x5678;
    IosCbEntryLog[6] = 2;
    report();
    assert(ffs_reports == 2 && callback_reports == 2);
}
'''


def compile_program(directory, name, text):
    source, executable = directory / (name + '.cpp'), directory / name
    source.write_text(text)
    compiler = shutil.which('clang++') or shutil.which('c++')
    if not compiler:
        raise SystemExit('A C++ compiler is required')
    result = subprocess.run([compiler, '-std=c++20', '-O0', str(source), '-o', str(executable)], capture_output=True, text=True)
    return result, executable


def caspal_diagnostic(source):
    start = source.index('static void IosLogUnimplementedCASPAL(')
    return source[start:source.index('\n}\n', start) + 3]


def caspal_program(source, windows):
    prelude = '''#include <cstdint>
#include <cstddef>
#include <cassert>
#include <cstring>
#include <tuple>
#include <iostream>
static unsigned messages, queries;
static unsigned query_type = 1;
static bool query_succeeds = true;
'''
    if windows:
        prelude += '''#define _WIN32 1
using LPCVOID = const void*;
constexpr unsigned MEM_IMAGE = 1, MEM_MAPPED = 2, MEM_PRIVATE = 3;
struct MEMORY_BASIC_INFORMATION {
    void* BaseAddress; uint64_t RegionSize; unsigned Protect, Type, State;
};
static std::size_t VirtualQuery(LPCVOID address, MEMORY_BASIC_INFORMATION* info, std::size_t size) {
    assert(address == reinterpret_cast<LPCVOID>(0x1235));
    assert(size == sizeof(*info)); ++queries;
    if (!query_succeeds) return 0;
    *info = {reinterpret_cast<void*>(0x1200), 0x1000, 4, query_type, 0x1000};
    return sizeof(*info);
}
'''
    prelude += '''namespace LogMan::Msg {
template<class... Args> void EFmt(const char* format, Args... args) {
    ++messages;
    auto values = std::tuple(args...);
    assert(std::get<0>(values) == 1 && std::get<1>(values) == 7);
    assert(std::get<2>(values) == 0x1235 && std::get<3>(values) == 5);
    assert(std::strcmp(std::get<4>(values), "yes") == 0);
#ifdef _WIN32
    static_assert(sizeof...(Args) == 10);
    assert(std::strstr(format, "region base="));
    assert(std::get<5>(values) == (query_succeeds ? reinterpret_cast<void*>(0x1200) : nullptr));
    assert(std::get<6>(values) == (query_succeeds ? 0x1000 : 0));
    assert(std::get<7>(values) == (query_succeeds ? 4 : 0));
    const char* type = !query_succeeds ? "?" : query_type == MEM_IMAGE ? "MEM_IMAGE" : query_type == MEM_MAPPED ? "MEM_MAPPED" : "MEM_PRIVATE";
    assert(std::strcmp(std::get<8>(values), type) == 0);
    assert(std::get<9>(values) == (query_succeeds ? 0x1000 : 0));
#else
    static_assert(sizeof...(Args) == 5);
    assert(!std::strstr(format, "region base="));
#endif
    std::cout << format; ((std::cout << '|' << args), ...); std::cout << '\\n';
}
}
'''
    return prelude + caspal_diagnostic(source) + '''int main() {
    uint64_t registers[32] {};
    registers[7] = 0x1230;
    IosLogUnimplementedCASPAL(1, registers, 7);
    registers[7] = 0x1235;
    IosLogUnimplementedCASPAL(0, registers, 7);
    assert(messages == 0 && queries == 0);
    IosLogUnimplementedCASPAL(1, registers, 7);
    query_type = 2; IosLogUnimplementedCASPAL(1, registers, 7);
    query_type = 3; IosLogUnimplementedCASPAL(1, registers, 7);
    query_succeeds = false; IosLogUnimplementedCASPAL(1, registers, 7);
    for (unsigned i = 0; i < 10; ++i) IosLogUnimplementedCASPAL(1, registers, 7);
    assert(messages == 8);
#ifdef _WIN32
    assert(queries == 8);
#else
    assert(queries == 0);
#endif
}
'''


def snapshot_code(source):
    start = source.index('/* iOS-Madeira ml622: mirror of rpmalloc')
    declarations = source[start:source.index('#include <condition_variable>', start)]
    start = source.index('      /* iOS-Madeira ml622: drain the rpmalloc')
    end = source.index('\n    }\n  }\n\n  /* iOS-Madeira 2026-05-14', start)
    return declarations, source[start:end]


def snapshot_program(source, apple):
    declarations, report = snapshot_code(source)
    prelude = '''#include <cassert>
#include <iostream>
static unsigned reports;
namespace LogMan::Msg {
template<class... Args> void EFmt(const char* format, Args... args) {
    ++reports;
    std::cout << format; ((std::cout << '|' << args), ...); std::cout << '\\n';
}
}
'''
    if apple:
        # Define after standard headers: only the extracted production guard
        # changes, not the host compiler's standard-library platform choice.
        prelude += '#define __APPLE__ 1\n'
    body = prelude + declarations + '\nstatic void report() {\n' + report + '\n}\n'
    if apple:
        return body + 'int main() { report(); assert(reports == 0); }\n'
    return body + '''extern "C" int rpm_cas_snapshot_take(rpm_cas_snapshot* out) {
    static unsigned calls;
    if (calls++ != 0) return 0;
    *out = {};
    out->which_loop = 2; out->page_addr = 0x1234;
    out->block_count = 16; out->block_index = 3;
    out->fail_changed = 5; out->fail_unchanged = 7;
    return 1;
}
int main() { report(); report(); assert(reports == 1); }
'''


def main():
    source = subprocess.check_output(['git', '-C', str(ROOT / 'FEX'), 'show', 'HEAD:' + SOURCE], text=True)
    arm64_source = subprocess.check_output(['git', '-C', str(ROOT / 'FEX'), 'show', 'HEAD:' + ARM64_SOURCE], text=True)
    with tempfile.TemporaryDirectory(prefix='madeira-fex-diagnostics-') as folder:
        directory = Path(folder)
        result, _ = compile_program(directory, 'unpatched-native', program(source, False))
        assert result.returncode != 0, 'unpatched native unexpectedly compiled'
        assert 'IosFfsBypassLog' in result.stderr and 'IosCbEntryLog' in result.stderr, result.stderr
        print('RED: pinned native diagnostic code reproduces undeclared counters')
        result, _ = compile_program(directory, 'unpatched-native-caspal', caspal_program(arm64_source, False))
        assert result.returncode != 0, 'unpatched native CASPAL diagnostic unexpectedly compiled'
        assert 'MEMORY_BASIC_INFORMATION' in result.stderr, result.stderr
        print('RED: pinned native CASPAL diagnostic reproduces Windows-only type failure')
        result, _ = compile_program(directory, 'unpatched-apple-snapshot', snapshot_program(source, True))
        assert result.returncode != 0, 'unpatched Apple snapshot unexpectedly linked'
        assert 'rpm_cas_snapshot_take' in result.stderr, result.stderr
        print('RED: pinned Apple snapshot diagnostic reproduces missing allocator symbol')
        assert PATCH.is_file(), f'missing native diagnostic patch: {PATCH}'
        original = directory / SOURCE
        original.parent.mkdir(parents=True)
        original.write_text(source)
        original_arm64 = directory / ARM64_SOURCE
        original_arm64.parent.mkdir(parents=True, exist_ok=True)
        original_arm64.write_text(arm64_source)
        subprocess.run(['git', '-C', str(directory), 'apply', '--check', str(PATCH)], check=True)
        subprocess.run(['git', '-C', str(directory), 'apply', str(PATCH)], check=True)
        patched = original.read_text()
        for name, producer in [('patched-native', False), ('patched-ios-producer', True)]:
            result, executable = compile_program(directory, name, program(patched, producer))
            assert result.returncode == 0, result.stderr
            subprocess.run([str(executable)], check=True)
            print('GREEN: ' + name)
        patched_arm64 = original_arm64.read_text()
        assert patched_arm64.replace(caspal_diagnostic(patched_arm64), caspal_diagnostic(arm64_source)) == arm64_source, 'CASPAL atomics/opcode handling outside the diagnostic changed'
        windows_outputs = []
        for name, text in [('unpatched-windows-caspal', caspal_program(arm64_source, True)),
                           ('patched-native-caspal', caspal_program(patched_arm64, False)),
                           ('patched-windows-caspal', caspal_program(patched_arm64, True))]:
            result, executable = compile_program(directory, name, text)
            assert result.returncode == 0, result.stderr
            output = subprocess.check_output([str(executable)], text=True)
            if 'windows' in name:
                windows_outputs.append(output)
            print('GREEN: ' + name)
        assert windows_outputs[0] == windows_outputs[1], 'Windows query/report behavior changed'
        print('GREEN: Windows reports preserved; CASPAL atomic/opcode code untouched')
        snapshot_outputs = []
        for name, text in [('unpatched-allocator-snapshot', snapshot_program(source, False)),
                           ('patched-apple-snapshot', snapshot_program(patched, True)),
                           ('patched-allocator-snapshot', snapshot_program(patched, False))]:
            result, executable = compile_program(directory, name, text)
            assert result.returncode == 0, result.stderr
            output = subprocess.check_output([str(executable)], text=True)
            if 'allocator' in name:
                snapshot_outputs.append(output)
            print('GREEN: ' + name)
        assert snapshot_outputs[0] == snapshot_outputs[1], 'Enabled allocator snapshot reporting changed'
        print('GREEN: Apple links without rpmalloc; enabled allocator reports preserved')


if __name__ == '__main__':
    main()
