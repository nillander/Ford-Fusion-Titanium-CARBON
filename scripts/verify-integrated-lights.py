"""Gate integrated lights without permitting unrelated geometry changes."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('lens',ROOT/'scripts/prepare-carbon-lenses.py')
lens=importlib.util.module_from_spec(spec)
spec.loader.exec_module(lens)

def main():
    audit=json.loads((ROOT/'docs/carbon2018-stage-integrated-audit.json').read_text())
    plan={p['part']:p for p in json.loads((ROOT/'docs/carbon2018-integrated-lights-plan.json').read_text())}
    old=ROOT/'work/carbon2018-stage-lenses-solids/carbon2018-stage-lenses'
    new=ROOT/'work/carbon2018-stage-integrated-solids/carbon2018-stage-integrated'
    assert len(audit)==186 and len({p['hash'] for p in audit})==186
    unchanged=0
    hidden=0
    for p in audit:
        raw=(new/(p['hash']+'.bin')).read_bytes()
        if p['name'] in plan:
            assert sum(m['indices'] for m in p['materials'])==plan[p['name']]['indices']<=65535
            assert len(p['materials'])==2 and p['materials'][1]['Flags']==0x14180
        elif any(s in p['name'] for s in ['_HEADLIGHT_GLASS_','_BRAKELIGHT_GLASS_']):
            a,b=lens.aligned_chunk(raw,0x134b03)
            assert not any(raw[a:b]);hidden+=1
        else:
            assert raw==(old/(p['hash']+'.bin')).read_bytes(),p['name']
            unchanged+=1
    assert unchanged==170 and hidden==8
    files=[]
    for name in ['GEOMETRY.BIN','TEXTURES.BIN']:
        p=ROOT/'work/carbon2018-stage-integrated'/name
        files.append({'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest().upper()})
    assert (ROOT/files[1]['path']).read_bytes()==(ROOT/'work/carbon2018-stage-lenses/TEXTURES.BIN').read_bytes()
    report={'passed':True,'solids':186,'integrated_main_lights':8,'hidden_separate_lenses':8,
            'unchanged_solids':170,'files':files,'status':'experimental integrated-light test; visual confirmation pending'}
    (ROOT/'docs/carbon2018-stage-integrated-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: 8 integrated lights, 8 duplicate lens parts hidden; 170 other solids and textures unchanged')

if __name__=='__main__':main()
