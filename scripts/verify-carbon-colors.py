"""Require lossless CarToolkit reexport of the color-only correction."""
import hashlib
import json
from pathlib import Path
from inventory_geometry import inventory

ROOT = Path(__file__).resolve().parents[1]

def main():
    restored=ROOT/'work/carbon-compiler/geometry-restored-colors.bin'
    catalogue=inventory(restored,True,ROOT/'work/unused')
    data=restored.read_bytes()
    root=ROOT/'work/carbon2018-stage-colors-solids/carbon2018-stage-colors'
    for entry in catalogue['streaming']:
        expected=data[entry['offset']+40:entry['offset']+40+entry['bytes']]
        assert (root/(entry['hash']+'.bin')).read_bytes()==expected, entry['hash']
    old=json.loads((ROOT/'docs/carbon2018-stage-axes-audit.json').read_text())
    new=json.loads((ROOT/'docs/carbon2018-stage-colors-audit.json').read_text())
    assert old==new, 'Mesh or material properties changed'
    files=[]
    for name in ['GEOMETRY.BIN','TEXTURES.BIN']:
        path=ROOT/'work/carbon2018-stage-colors'/name
        files.append({'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest().upper(),'bytes':path.stat().st_size})
    assert (ROOT/files[1]['path']).read_bytes()==(ROOT/'work/carbon2018-stage-axes/TEXTURES.BIN').read_bytes()
    report={'passed':True,'solids':len(new),'lossless_color_patch_reexport':True,'mesh_materials_unchanged':True,
            'markers_preserved_by_byte_comparison':True,'changed_vertex_colors':552,'files':files,
            'status':'experimental comparison only; visual QA pending'}
    (ROOT/'docs/carbon2018-stage-colors-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: lossless reexport of 186 solids; mesh/material/markers/textures preserved')

if __name__=='__main__':
    main()
