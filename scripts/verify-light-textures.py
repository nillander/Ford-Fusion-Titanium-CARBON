"""Validate official light-state hashes and exact DDS pixels after export."""
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]

def bh(name):
    n=0xffffffff
    for c in name.encode('ascii'):n=(n*33+c)&0xffffffff
    return f'{n:08X}'

def main():
    audit=json.loads((ROOT/'docs/carbon2018-lighttexture-audit.json').read_text())
    exported={t['hash']:t for t in audit['textures']}
    expected={bh(p.stem):p for p in (ROOT/'work/carbon2018-texture-aliases').glob('*.dds')}
    assert audit['passed'] and len(expected)==18 and set(expected)==set(exported)
    for key,source in expected.items():
        decoded=ROOT/'work/carbon2018-lighttextures-decoded'/(key+'.dds')
        assert np.array_equal(np.asarray(Image.open(source)),np.asarray(Image.open(decoded))),source.name
    geometry=ROOT/'work/carbon2018-stage-lighttextures/GEOMETRY.BIN'
    assert geometry.read_bytes()==(ROOT/'work/carbon2018-stage-integrated/GEOMETRY.BIN').read_bytes()
    files=[]
    for name in ['GEOMETRY.BIN','TEXTURES.BIN']:
        p=ROOT/'work/carbon2018-stage-lighttextures'/name
        files.append({'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest().upper()})
    report={'passed':True,'textures':18,'all_dds_pixels_identical':True,'geometry_unchanged':True,
            'light_state_aliases':{k:p.stem for k,p in expected.items() if '_KIT00_' in p.stem},
            'files':files,'status':'OFF atlases also used for ON aliases; appearance and illumination require game QA'}
    (ROOT/'docs/carbon2018-stage-lighttextures-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: all 18 hashes and DDS pixels; geometry unchanged')

if __name__=='__main__':main()
