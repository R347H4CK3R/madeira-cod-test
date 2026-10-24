#!/usr/bin/env python3
"""Synthetic Burn/CAB/PE fixtures; no Microsoft code or runnable binaries.

Regression: opening a Burn EXE with 7-Zip extracts its UX cabinet only.
The runtime payload is in a separate, metadata-addressed attached cabinet.
"""
import hashlib
import importlib.util
from pathlib import Path
import shutil
import struct
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('stage_vcruntime', ROOT / 'build/ci/stage-vcruntime.py')
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)


def cabinet(files):
    """A real single-folder, uncompressed CAB, per Microsoft's MSCAB format."""
    table = bytearray()
    contents = bytearray()
    for name, data in files.items():
        table += struct.pack('<IIHHHH', len(data), len(contents), 0, 0, 0, 0x20)
        table += name.encode('ascii') + b'\0'
        contents += data
    start = 44 + len(table)
    size = start + 8 + len(contents)
    header = struct.pack('<4sIIIII BBHHHHH', b'MSCF', 0, size, 0, 44, 0,
                         3, 1, 1, len(files), 0, 0, 0)
    folder = struct.pack('<IHH', start, 1, 0)
    block = struct.pack('<IHH', 0, len(contents), len(contents)) + contents
    return header + folder + table + block


def runtime_pe(name, marker=0, machine=0x8664, certificate=True):
    data = bytearray(0x400)
    data[:2] = b'MZ'
    struct.pack_into('<I', data, 0x3c, 0x80)
    data[0x80:0x84] = b'PE\0\0'
    struct.pack_into('<H', data, 0x84, machine)
    struct.pack_into('<H', data, 0x98, 0x20b)
    if certificate:
        struct.pack_into('<II', data, 0x98 + 112 + 4 * 8, 0x3f0, 16)
    key = 'OriginalFilename\0'.encode('utf-16le')
    data[0x200:0x200 + len(key)] = key
    start = (0x200 + len(key) + 3) & ~3
    encoded = (name + '\0').encode('utf-16le')
    data[start:start + len(encoded)] = encoded
    data[0x300] = marker
    return bytes(data)


def bundle(attached=None, signed_engine=True, decoy=None):
    ux = cabinet({'bootstrap.txt': b'UX only'})
    data = bytearray(0x1000)
    data[:2] = b'MZ'
    struct.pack_into('<I', data, 0x3c, 0x80)
    data[0x80:0x84] = b'PE\0\0'
    struct.pack_into('<HHIIIHH', data, 0x84, 0x14c, 2, 0, 0, 0, 0xe0, 2)
    struct.pack_into('<H', data, 0x98, 0x10b)
    struct.pack_into('<II', data, 0x98 + 32, 0x1000, 0x200)
    struct.pack_into('<II', data, 0x98 + 56, 0x3000, 0x200)
    struct.pack_into('<I', data, 0x98 + 92, 16)
    struct.pack_into('<8sIIIIIIHHI', data, 0x178, b'.text', 0x100, 0x1000, 0x100, 0x200, 0, 0, 0, 0, 0)
    struct.pack_into('<8sIIIIIIHHI', data, 0x1a0, b'.wixburn', 0xd00, 0x2000, 0xd00, 0x300, 0, 0, 0, 0, 0)
    data += ux
    original_offset = original_size = 0
    if signed_engine:
        data += bytes(0x3000 - len(data))
        if decoy:
            data[0x2000:0x2000 + len(decoy)] = decoy
        original_offset, original_size = 0x3000, 16
        data += b'engine-signature'
    struct.pack_into('<II16sIIIIIIII', data, 0x300, 0x00f14300, 2, bytes(16),
                     0x1000, 0, original_offset, original_size, 1,
                     2 if attached else 1, len(ux), len(attached or b''))
    if attached:
        data += attached
    # The current whole-bundle certificate is AFTER the attached container.
    struct.pack_into('<II', data, 0x98 + 96 + 4 * 8, len(data), 16)
    data += b'bundle-signature'
    return bytes(data), ux


class BurnMetadata(unittest.TestCase):
    def spans(self, data):
        parser = getattr(runtime, 'burn_containers', None)
        self.assertIsNotNone(parser, 'Burn metadata must locate the attached CAB, not leave its bytes in the PE overlay')
        return parser(data)

    def test_signed_engine_boundary_skips_signature_and_ignores_decoy_cab(self):
        attached = cabinet({'payload': b'actual attached payload'})
        decoy = cabinet({'payload': b'decoy in engine bytes'})
        data, ux = bundle(attached, decoy=decoy)
        spans = self.spans(data)
        self.assertEqual([(s['name'], s['offset'], s['size']) for s in spans],
                         [('ux', 0x1000, len(ux)), ('attached', 0x3010, len(attached))])
        self.assertEqual(data[spans[1]['offset']:spans[1]['offset'] + spans[1]['size']], attached)

    def test_unsigned_engine_boundary_follows_ux(self):
        attached = cabinet({'payload': b'actual attached payload'})
        data, ux = bundle(attached, signed_engine=False)
        self.assertEqual(self.spans(data)[1]['offset'], 0x1000 + len(ux))

    def test_ux_only_bundle_does_not_invent_attached_container(self):
        data, _ = bundle()
        self.assertEqual([s['name'] for s in self.spans(data)], ['ux'])

    def test_rejects_truncated_attached_payload(self):
        data, _ = bundle(cabinet({'payload': b'actual attached payload'}))
        with self.assertRaisesRegex(ValueError, 'container|bounds|truncat'):
            self.spans(data[:0x3015])

    def test_rejects_cab_size_inconsistent_with_burn_metadata(self):
        data, _ = bundle(cabinet({'payload': b'attached'}))
        data = bytearray(data)
        struct.pack_into('<I', data, 0x3010 + 8, 36)
        with self.assertRaisesRegex(ValueError, 'CAB|cabinet|size'):
            self.spans(data)

    def test_rejects_unsupported_header_and_overlapping_signature(self):
        original, _ = bundle(cabinet({'payload': b'attached'}))
        for offset, value in ((0x304, 3), (0x328, 2), (0x32c, 3), (0x320, 0x400)):
            with self.subTest(offset=offset):
                data = bytearray(original)
                struct.pack_into('<I', data, offset, value)
                with self.assertRaises(ValueError):
                    self.spans(data)


@unittest.skipUnless(shutil.which('7zz'), '7zz is required for the real CAB extraction regression')
class Extraction(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def extract(self, data):
        installer = self.root / 'installer.exe'
        installer.write_bytes(data)
        destination = self.root / 'runtime'
        report = runtime.extract(installer, destination)
        return destination, report

    def test_extracts_unmodified_core_from_attached_nested_cab(self):
        originals = {name: runtime_pe(name) for name in runtime.CORE}
        nested = cabinet({f'fil{i}': data for i, data in enumerate(originals.values())})
        data, _ = bundle(cabinet({'a0': nested}))
        destination, report = self.extract(data)
        self.assertEqual(set(report), {'msvcp140.dll', 'vcruntime140.dll', 'vcruntime140_1.dll'})
        for name, original in originals.items():
            self.assertEqual((destination / name).read_bytes(), original)
            self.assertEqual(report[name], hashlib.sha256(original).hexdigest())

    def test_rejects_missing_core_in_ux_only_bundle(self):
        data, _ = bundle()
        with self.assertRaisesRegex(ValueError, 'Missing Microsoft x64 runtime inputs'):
            self.extract(data)

    def test_rejects_conflicting_same_name_payloads(self):
        first = cabinet({'fil1': runtime_pe('msvcp140.dll', marker=1)})
        second = cabinet({'fil2': runtime_pe('msvcp140.dll', marker=2)})
        data, _ = bundle(cabinet({'a0': first, 'a1': second}))
        with self.assertRaisesRegex(ValueError, 'different signed binaries named msvcp140.dll'):
            self.extract(data)


class RuntimeValidation(unittest.TestCase):
    def test_rejects_wrong_machine_or_missing_certificate_payload(self):
        self.assertFalse(runtime.signed_x64(runtime_pe('msvcp140.dll', machine=0xaa64)))
        self.assertFalse(runtime.signed_x64(runtime_pe('msvcp140.dll', certificate=False)))


if __name__ == '__main__':
    unittest.main()
