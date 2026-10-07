"""Align Carbon EXHAUST markers with the midpoint of the Fusion's chrome tips.

Only marker Z translations change; geometry, materials, marker matrices and
the official MUSTANGGT catalogue are preserved. Requires NumPy.
"""
import hashlib
import importlib.util
import json
import shutil
import struct
from pathlib import Path

import numpy as np
import jdlz
from dump_position_markers import names_table

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('roof', ROOT / 'scripts/consolidate-roof-compile.py')
roof = importlib.util.module_from_spec(spec)
spec.loader.exec_module(roof)


def sha(data):
    return hashlib.sha256(data).hexdigest().upper()


def main():
    src = ROOT / 'work/carbon2018-stage-roof'
    dst = ROOT / 'work/carbon2018-stage-exhaust'
    dst.mkdir(exist_ok=True)
    data = (src / 'GEOMETRY.BIN').read_bytes()
    assert sha(data) == 'DE8EE10F8DDA430076D15CAD4DA796398B5BC85DC2EC9D33B4B6B1F94967680E'
    # BASE_A chrome mesh has the visible exhaust tips. Select their rear region,
    # excluding wheels/body; derive height from actual min/max, not the screenshot.
    vertices = []
    indices = set()
    material = ''
    for line in (ROOT / 'work/carbon2018-source/BASE_A.obj').read_text().splitlines():
        if line.startswith('v '):
            vertices.append(list(map(float, line.split()[1:4])))
        elif line.startswith('usemtl '):
            material = line[7:]
        elif line.startswith('f ') and material == 'M_0FEDEE40_5A00E244':
            indices.update(int(item.split('/')[0])-1 for item in line.split()[1:])
    vertices = np.array(vertices)[sorted(indices)]
    tips = vertices[(vertices[:, 0] < -2.2) & (abs(vertices[:, 1]) > .52) &
                    (abs(vertices[:, 1]) < .76) & (vertices[:, 2] < .4)]
    assert len(tips) > 100
    z = float((tips[:, 2].min() + tips[:, 2].max()) / 2)
    assert .16 < z < .2
    table, entries = roof.entries(data)
    out = bytearray(data[:min(e[1] for e in entries)])
    changed = []
    marker_names = names_table(str(ROOT / 'work/carbon-compiler/mp.txt'))
    decoded_dir = ROOT / 'work/carbon2018-exhaust-solids'
    decoded_dir.mkdir(exist_ok=True)
    for i, entry in enumerate(entries):
        original = roof.decode(data, entry)
        solid = bytearray(original)
        permitted = set()
        markers = []
        if roof.sr.find(solid, 0x13401A):
            for r in roof.sr.marker_records(solid):
                if marker_names.get(struct.unpack_from('<I', solid, r)[0]) == 'EXHAUST':
                    before = struct.unpack_from('<3f', solid, r+64)
                    assert abs(before[2] - .135) < 1e-6
                    struct.pack_into('<f', solid, r+72, z)
                    permitted.update(range(r+72, r+76))
                    markers.append({'before': before, 'after': struct.unpack_from('<3f', solid, r+64)})
        assert all(a == b or p in permitted for p, (a, b) in enumerate(zip(original, solid)))
        if markers:
            assert len(markers) == 2
            packed = jdlz.normalize_for_game(jdlz.compress(solid), repair=False)
            assert jdlz.decompress(packed) == solid
            block = struct.pack('<6I', 0x55441122, len(solid), len(packed)+24, 0, 0, 0)+packed
            changed.append({'solid': f'{entry[0]:08X}', 'markers': markers})
            print('EXHAUST', f'{entry[0]:08X}', flush=True)
        else:
            block = data[entry[1]:entry[1]+entry[2]]
        entry[1:4] = len(out), len(block), len(solid)
        out += block
        roof.sr.pad(out)
        struct.pack_into('<6I', out, table+i*24, *entry)
        (decoded_dir / f'{entry[0]:08X}.bin').write_bytes(solid)
    assert len(entries) == 190 and len(changed) == 30
    struct.pack_into('<I', out, 4, len(out)-8)
    (dst / 'GEOMETRY.BIN').write_bytes(out)
    shutil.copyfile(src / 'TEXTURES.BIN', dst / 'TEXTURES.BIN')
    # Read the final catalogue again; every decompressed record must match staging.
    _, final = roof.entries(out)
    assert [e[0] for e in entries] == [e[0] for e in final]
    for e in final:
        assert roof.decode(out, e) == (decoded_dir / f'{e[0]:08X}.bin').read_bytes()
        jdlz.normalize_for_game(out[e[1]+24:e[1]+e[2]], repair=False)
    report = {'passed': False, 'binary_scope_passed': True, 'solids': 190,
              'unchanged_solids': 160, 'changed_markers': 60,
              'tip_bounds': [tips.min(0).tolist(), tips.max(0).tolist()],
              'marker_z': z, 'changes': changed, 'game_validation': 'pending',
              'carbon_decoder_end_flags_validated': True,
              'files': [{'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size,
                         'sha256': sha(p.read_bytes())} for p in sorted(dst.glob('*.BIN'))]}
    (ROOT / 'docs/carbon2018-stage-exhaust-verification.json').write_text(json.dumps(report, indent=2)+'\n')
    print('Binary scope passed; independent mesh read still required.', z)


if __name__ == '__main__':
    main()
