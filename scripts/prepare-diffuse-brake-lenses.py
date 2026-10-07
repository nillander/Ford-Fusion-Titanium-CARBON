"""Restore the MW-approved diffuse rear lens material in integrated Carbon lamps."""
import hashlib
import importlib.util
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('lens', ROOT/'scripts/prepare-carbon-lenses.py')
lens = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lens)

def main():
    original = (ROOT/'work/carbon2018-stage-integrated/GEOMETRY.BIN').read_bytes()
    inventory = json.loads((ROOT/'docs/carbon2018-stage-integrated-inventory.json').read_text())[0]
    assert hashlib.sha256(original).hexdigest().upper() == inventory['sha256']
    names = {p['hash']: p['name'] for p in json.loads((ROOT/'docs/carbon2018-stage-integrated-audit.json').read_text())}
    donor = next(p for p in json.loads((ROOT/'docs/carbon-mesh-audit.json').read_text())
                 if p['name'] == 'MUSTANGGT_KIT00_REAR_BUMPER_BADGING_SET_A')
    raw_donor = (ROOT/'work/carbon-solids/MUSTANGGT'/(donor['hash']+'.bin')).read_bytes()
    a, b = next((a, b) for k, a, b in lens.colors.descendants(raw_donor, 0, len(raw_donor)) if k == 0x134013)
    diffuse_material = raw_donor[a:a+4]
    assert struct.unpack('<I', diffuse_material)[0] == 0x0FEDEE40
    solids, changes = [], []
    for entry in inventory['streaming']:
        data = bytearray((ROOT/'work/carbon2018-stage-integrated-solids/carbon2018-stage-integrated'/(entry['hash']+'.bin')).read_bytes())
        if names[entry['hash']] in {f'MUSTANGGT_KIT00_RIGHT_BRAKELIGHT_{lod}' for lod in 'ABCD'}:
            a, b = next((a, b) for k, a, b in lens.colors.descendants(data, 0, len(data)) if k == 0x134013)
            assert b-a == 16
            data[a+8:a+12] = diffuse_material
            g, end = lens.aligned_chunk(data, 0x134b02)
            assert end-g == 288
            struct.pack_into('<I', data, g+144+56, 0x4180)
            changes.append(names[entry['hash']])
        solids.append(data)
    assert len(changes) == 4
    output = bytearray(original[:min(e['offset'] for e in inventory['streaming'])])
    table = []
    def visit(a, b):
        for k, s, e in lens.colors.chunks(original, a, b):
            if k == 0x134004:
                table.extend(range(s, e, 24)); return
            if k in (0x80134000, 0x80134001): visit(s, e)
            if table: return
    visit(0, len(original))
    assert len(table) == len(solids) == 186
    for off, solid in zip(table, solids):
        output.extend(b'\0'*(-len(output)%128)); start = len(output)
        blob = b'RAWW\x01\x10\x00\x00'+struct.pack('<II',len(solid),len(solid)+16)+solid
        packed = struct.pack('<6I',0x55441122,len(solid),len(blob)+24,0,0,0)+blob
        output.extend(packed)
        struct.pack_into('<III',output,off+4,start,len(packed),len(solid))
    struct.pack_into('<I', output, 4, len(output)-8)
    (ROOT/'work/carbon-compiler/geometry-diffuse-brake.bin').write_bytes(output)
    print('Prepared four diffuse rear lens groups; 182 other solids unchanged')

if __name__ == '__main__':
    main()
