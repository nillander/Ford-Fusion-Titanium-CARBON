"""Combine a full roof compile with the 186 approved v1.0 solids.

prepare emits CarToolkit input using the compiler catalogue. finish uses the
normalized catalogue and only its native roof blocks, keeping every approved
solid byte-identical after decompression. No corrections are inferred anew.
"""
import hashlib
import importlib.util
import json
import math
import shutil
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import jdlz
spec = importlib.util.spec_from_file_location('sr', ROOT / 'scripts/prepare-spoiler-roof.py')
sr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sr)
APPROVED = ROOT / 'work/carbon2018-stage-spoiler/GEOMETRY.BIN'
PLAN = json.loads((ROOT / 'docs/carbon2018-roof-compiler-plan.json').read_text())
ROOFS = {sr.bh(n) for n in PLAN['new_parts']}


def entries(data):
    a, b = sr.find(data, 0x134004)
    return a, [list(struct.unpack_from('<6I', data, p)) for p in range(a, b, 24)]


def decode(data, e):
    return jdlz.decompress(data[e[1] + 24:e[1] + e[2]])


def approved():
    data = APPROVED.read_bytes()
    assert hashlib.sha256(data).hexdigest().upper() == 'AE4BB255576689D0668AAB54B677F8D3393AE74C5A15700AB2176FDC89B647B2'
    _, es = entries(data)
    assert len(es) == 186
    return data, {e[0]: e for e in es}


def prepare():
    original, old = approved()
    compiled = (ROOT / 'work/carbon-compiler/geometry.bin').read_bytes()
    table, es = entries(compiled)
    assert {e[0] for e in es} == set(old) | ROOFS | {0}
    out = bytearray(compiled[:min(e[1] for e in es)])
    for i, e in enumerate(es):
        if e[0] in old:
            solid = decode(original, old[e[0]])
        else:
            solid = bytearray((ROOT / 'work/carbon2018-roof-compiled-solids/carbon-compiler' / f'{e[0]:08X}.bin').read_bytes())
            if e[0] in ROOFS:
                records = sr.marker_records(solid)
                assert len(records) == 1
                r = records[0]
                assert struct.unpack_from('<I', solid, r)[0] == sr.bh('ROOF_SCOOP')
                angle = math.radians(PLAN['tilt_degrees'])
                c, s = math.cos(angle), math.sin(angle)
                matrix = [c, 0, -s, 0, 0, 1, 0, 0, s, 0, c, 0, *PLAN['position'], 1]
                struct.pack_into('<16f', solid, r + 16, *matrix)
        out += b'\0' * (-len(out) % 128)
        offset = len(out)
        blob = b'RAWW\x01\x10\0\0' + struct.pack('<II', len(solid), len(solid) + 16) + solid
        block = struct.pack('<6I', 0x55441122, len(solid), len(blob) + 24, 0, 0, 0) + blob
        out += block
        e[1:4] = offset, len(block), len(solid)
        struct.pack_into('<6I', out, table + i * 24, *e)
    struct.pack_into('<I', out, 4, len(out) - 8)
    target = ROOT / 'work/carbon-compiler/geometry-roof-consolidated.bin'
    target.write_bytes(out)
    print('Prepared compiler catalogue with 190 real solids + sentinel:', target)


def finish():
    original, old = approved()
    folder = ROOT / 'work/carbon2018-stage-roof'
    normalized = (ROOT / 'work/carbon2018-roof-normalized/GEOMETRY.BIN').read_bytes()
    table, es = entries(normalized)
    assert {e[0] for e in es} == set(old) | ROOFS and len(es) == 190
    out = bytearray(normalized[:min(e[1] for e in es)])
    recompressed = 0
    repaired_flags = 0
    added_flag_bytes = 0
    for i, e in enumerate(es):
        if e[0] in old:
            prev = old[e[0]]
            block = original[prev[1]:prev[1] + prev[2]]
            e[3:] = prev[3:]
            solid = decode(original, prev)
            cache = ROOT / 'work/jdlz-cache' / (hashlib.sha256(solid).hexdigest() + '.jdlz')
            if cache.exists() and cache.stat().st_size + 24 < len(block):
                comp = cache.read_bytes()
                assert jdlz.decompress(comp) == solid
                block = struct.pack('<6I', 0x55441122, len(solid), len(comp) + 24, 0, 0, 0) + comp
                recompressed += 1
        else:
            block = normalized[e[1]:e[1] + e[2]]
        comp = block[24:]
        fixed = jdlz.normalize_for_game(comp)
        if fixed != comp:
            repaired_flags += 1
            added_flag_bytes += len(fixed) - len(comp)
            block = struct.pack('<6I', 0x55441122, e[3], len(fixed) + 24, 0, 0, 0) + fixed
        offset = len(out)
        assert offset % 128 == 0
        out += block
        sr.pad(out)
        e[1:3] = offset, len(block)
        struct.pack_into('<6I', out, table + i * 24, *e)
    struct.pack_into('<I', out, 4, len(out) - 8)
    assert len(out) <= len(original), (len(out), len(original))
    folder.mkdir(exist_ok=True)
    (folder / 'GEOMETRY.BIN').write_bytes(out)
    shutil.copy2(APPROVED.parent / 'TEXTURES.BIN', folder / 'TEXTURES.BIN')
    written = (folder / 'GEOMETRY.BIN').read_bytes()
    _, check = entries(written)
    for e in check:
        assert len(decode(written, e)) == e[3]
        if e[0] in old:
            assert decode(written, e) == decode(original, old[e[0]])
        else:
            solid = decode(written, e)
            recs = sr.marker_records(solid)
            assert len(recs) == 1
            r = recs[0]
            assert struct.unpack_from('<I', solid, r)[0] == sr.bh('ROOF_SCOOP')
            got = struct.unpack_from('<3f', solid, r + 64)
            assert all(abs(a-b) < 1e-5 for a,b in zip(got, PLAN['position']))
    files = [{'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size,
              'sha256': hashlib.sha256(p.read_bytes()).hexdigest().upper()}
             for p in (folder / 'GEOMETRY.BIN', folder / 'TEXTURES.BIN')]
    report = {'passed': True, 'solids': 190, 'unchanged_existing_solids': 186,
              'losslessly_recompressed_blocks': recompressed,
              'repaired_terminal_flag_streams': repaired_flags,
              'added_terminal_flag_bytes': added_flag_bytes,
              'carbon_decoder_end_flags_validated': True,
              'full_compile': True, 'roof': PLAN, 'size_limit': len(original),
              'files': files, 'status': 'structural comparison passed; independent mesh audit and game QA required'}
    (ROOT / 'docs/carbon2018-stage-roof-verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    {'prepare': prepare, 'finish': finish}[sys.argv[1]]()
