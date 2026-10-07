"""Gate lens/decal staging with exact decoded-byte comparisons."""
import hashlib
import importlib.util
import json
import struct
from pathlib import Path
from inventory_geometry import inventory

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('colors',ROOT/'scripts/restore-carbon-vertex-colors.py')
colors=importlib.util.module_from_spec(spec)
spec.loader.exec_module(colors)

def main():
    intermediate=ROOT/'work/carbon-compiler/geometry-lenses.bin'
    data=intermediate.read_bytes()
    catalogue=inventory(intermediate,True,ROOT/'work/unused')
    plan=json.loads((ROOT/'docs/carbon2018-lens-adaptation.json').read_text())
    assert hashlib.sha256(data).hexdigest().upper()==plan['output_sha256']
    changes={r['hash']:r for r in plan['parts']}
    newroot=ROOT/'work/carbon2018-stage-lenses-solids/carbon2018-stage-lenses'
    oldroot=ROOT/'work/carbon2018-stage-colors-solids/carbon2018-stage-colors'
    for e in catalogue['streaming']:
        raw=bytearray(data[e['offset']+40:e['offset']+40+e['bytes']])
        actual=(newroot/(e['hash']+'.bin')).read_bytes()
        if e['hash'] in changes and 'donor' in changes[e['hash']]:
            # CarToolkit clears the donor header's runtime flag 0x40 on export.
            # Permit this one documented normalization; material flags survive.
            a,b=next((a,b) for k,a,b in colors.descendants(raw,0,len(raw)) if k==0x134011)
            a=(a+15)&~15
            assert struct.unpack_from('<H',raw,a+14)[0]==0x40
            assert struct.unpack_from('<H',actual,a+14)[0]==0
            struct.pack_into('<H',raw,a+14,0)
        assert raw==actual, ('Reexport differs',e['hash'])
        if e['hash'] not in changes:
            assert actual==(oldroot/(e['hash']+'.bin')).read_bytes(),e['hash']
        elif changes[e['hash']].get('decal_hidden'):
            a,b=next((a,b) for k,a,b in colors.descendants(actual,0,len(actual)) if k==0x134b03)
            a=(a+15)&~15
            assert not any(actual[a:b]),e['hash']
    old={r['hash']:r for r in json.loads((ROOT/'docs/carbon2018-stage-colors-audit.json').read_text())}
    new=json.loads((ROOT/'docs/carbon2018-stage-lenses-audit.json').read_text())
    assert len(new)==186 and len(changes)==34
    for r in new:
        previous=old[r['hash']]
        assert all(r[k]==previous[k] for k in ('name','vertices','triangles','min','max','morphTargets'))
        if 'GLASS' in r['name'] and ('HEADLIGHT' in r['name'] or 'BRAKELIGHT' in r['name']):
            assert r['materials'][0]['Flags']==0x14180
    files=[]
    for name in ['GEOMETRY.BIN','TEXTURES.BIN']:
        path=ROOT/'work/carbon2018-stage-lenses'/name
        files.append({'path':path.relative_to(ROOT).as_posix(),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest().upper()})
    assert (ROOT/files[1]['path']).read_bytes()==(ROOT/'work/carbon2018-stage-colors/TEXTURES.BIN').read_bytes()
    report={'passed':True,'solids':186,'lens_settings_from_official_donor':8,'hidden_decal_solids':26,
            'other_solids_byte_identical':152,'files':files,'status':'experimental lens test; all four lens categories require in-game confirmation'}
    (ROOT/'docs/carbon2018-stage-lenses-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: 8 donor lens settings, 26 hidden decals, 152 solids unchanged, textures unchanged')

if __name__=='__main__':main()
