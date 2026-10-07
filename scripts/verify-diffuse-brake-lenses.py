"""Permit only four rear lens material/flag edits after CarToolkit export."""
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
    audit = json.loads((ROOT/'docs/carbon2018-stage-diffuse-brake-audit.json').read_text())
    old = ROOT/'work/carbon2018-stage-integrated-solids/carbon2018-stage-integrated'
    new = ROOT/'work/carbon2018-stage-diffuse-brake-solids/carbon2018-stage-diffuse-brake'
    targets = {f'MUSTANGGT_KIT00_RIGHT_BRAKELIGHT_{lod}' for lod in 'ABCD'}
    assert len(audit) == 186 and len({p['hash'] for p in audit}) == 186
    changed = []
    for p in audit:
        before = bytearray((old/(p['hash']+'.bin')).read_bytes())
        after = (new/(p['hash']+'.bin')).read_bytes()
        if p['name'] in targets:
            a, b = next((a,b) for k,a,b in lens.colors.descendants(before,0,len(before)) if k == 0x134013)
            struct.pack_into('<I',before,a+8,0x0FEDEE40)
            g, end = lens.aligned_chunk(before,0x134b02)
            struct.pack_into('<I',before,g+144+56,0x4180)
            assert len(p['materials']) == 2 and p['materials'][1]['Flags'] == 0x4180
            changed.append(p['name'])
        assert before == after, p['name']
    assert set(changed) == targets
    stage = ROOT/'work/carbon2018-stage-diffuse-brake'
    assert (stage/'TEXTURES.BIN').read_bytes() == (ROOT/'work/carbon2018-stage-opaque-brake/TEXTURES.BIN').read_bytes()
    files = [{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,
              'sha256':hashlib.sha256(p.read_bytes()).hexdigest().upper()}
             for p in [stage/'GEOMETRY.BIN',stage/'TEXTURES.BIN']]
    report = {'passed':True,'solids':186,'diffuse_rear_lenses':changed,'unchanged_solids':182,
              'textures_unchanged':True,'files':files,'status':'diffuse material comparison; game QA pending'}
    (ROOT/'docs/carbon2018-stage-diffuse-brake-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: only four rear lens material/flag edits; 182 solids and textures unchanged')

if __name__ == '__main__':
    main()
