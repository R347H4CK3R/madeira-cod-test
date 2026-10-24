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


def main():
    source = subprocess.check_output(['git', '-C', str(ROOT / 'FEX'), 'show', 'HEAD:' + SOURCE], text=True)
    with tempfile.TemporaryDirectory(prefix='madeira-fex-diagnostics-') as folder:
        directory = Path(folder)
        result, _ = compile_program(directory, 'unpatched-native', program(source, False))
        assert result.returncode != 0, 'unpatched native unexpectedly compiled'
        assert 'IosFfsBypassLog' in result.stderr and 'IosCbEntryLog' in result.stderr, result.stderr
        print('RED: pinned native diagnostic code reproduces undeclared counters')
        assert PATCH.is_file(), f'missing native diagnostic patch: {PATCH}'
        original = directory / SOURCE
        original.parent.mkdir(parents=True)
        original.write_text(source)
        subprocess.run(['git', '-C', str(directory), 'apply', '--check', str(PATCH)], check=True)
        subprocess.run(['git', '-C', str(directory), 'apply', str(PATCH)], check=True)
        patched = original.read_text()
        for name, producer in [('patched-native', False), ('patched-ios-producer', True)]:
            result, executable = compile_program(directory, name, program(patched, producer))
            assert result.returncode == 0, result.stderr
            subprocess.run([str(executable)], check=True)
            print('GREEN: ' + name)


if __name__ == '__main__':
    main()
