"""Verify only eight texture-table hashes differ from the previous game test."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('lens',ROOT/'scripts/prepare-carbon-lenses.py')
lens = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lens)

def main():
    audit=json.loads((ROOT/'docs/carbon2018-stage-dynamic-lights-audit.json').read_text())
    plan={p['part']:p for p in json.loads((ROOT/'docs/carbon2018-dynamic-lights-plan.json').read_text())}
    assert len(audit)==186 and len({p['hash'] for p in audit})==186 and len(plan)==8
    old=ROOT/'work/carbon2018-stage-diffuse-brake-solids/carbon2018-stage-diffuse-brake'
    new=ROOT/'work/carbon2018-stage-dynamic-lights-solids/carbon2018-stage-dynamic-lights'
    for p in audit:
        before=bytearray((old/(p['hash']+'.bin')).read_bytes())
        if p['name'] in plan:
            a,b=next((a,b) for k,a,b in lens.colors.descendants(before,0,len(before)) if k==0x134012)
            before[a:a+4]=int(plan[p['name']]['dynamic_texture'],16).to_bytes(4,'little')
            assert all(m['diffuse']==plan[p['name']]['dynamic_texture'] for m in p['materials'])
        assert before==(new/(p['hash']+'.bin')).read_bytes(),p['name']
    stage=ROOT/'work/carbon2018-stage-dynamic-lights'
    assert (stage/'TEXTURES.BIN').read_bytes()==(ROOT/'work/carbon2018-stage-diffuse-brake/TEXTURES.BIN').read_bytes()
    files=[{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,
            'sha256':hashlib.sha256(p.read_bytes()).hexdigest().upper()}
           for p in [stage/'GEOMETRY.BIN',stage/'TEXTURES.BIN']]
    report={'passed':True,'solids':186,'dynamic_light_parts':8,'unchanged_solids':178,
            'textures_unchanged':True,'files':files,'status':'official dynamic texture comparison; game QA pending'}
    (ROOT/'docs/carbon2018-stage-dynamic-lights-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: only 8 dynamic texture hashes changed; all vertex/index/material bytes preserved')

if __name__=='__main__':main()
