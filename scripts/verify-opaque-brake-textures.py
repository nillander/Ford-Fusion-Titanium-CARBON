"""Gate the DXT1 comparison: identical geometry, hashes and RGB pixels."""
import hashlib
import importlib.util
import json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('light', ROOT/'scripts/verify-light-textures.py')
light = importlib.util.module_from_spec(spec)
spec.loader.exec_module(light)

def main():
    audit = json.loads((ROOT/'docs/carbon2018-opaque-brake-texture-audit.json').read_text())
    records = {t['hash']: t for t in audit['textures']}
    sources = {light.bh(p.stem): p for p in (ROOT/'work/carbon2018-texture-aliases').glob('*.dds')}
    assert audit['passed'] and len(records) == 18 and records.keys() == sources.keys()
    changed = []
    for key, path in sources.items():
        exported = ROOT/'work/carbon2018-opaque-brake-decoded'/(key+'.dds')
        before, after = Image.open(path), Image.open(exported)
        if 'BRAKE' in path.stem:
            assert records[key]['Format'] == 0x31545844
            assert np.array_equal(np.asarray(before.convert('RGB')), np.asarray(after.convert('RGB')))
            changed.append(path.stem)
        else:
            assert np.array_equal(np.asarray(before), np.asarray(after))
    assert len(changed) == 5
    geometry = ROOT/'work/carbon2018-stage-opaque-brake/GEOMETRY.BIN'
    assert geometry.read_bytes() == (ROOT/'work/carbon2018-stage-lighttextures/GEOMETRY.BIN').read_bytes()
    files = []
    for name in ['GEOMETRY.BIN', 'TEXTURES.BIN']:
        p = geometry.parent/name
        files.append({'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size,
                      'sha256': hashlib.sha256(p.read_bytes()).hexdigest().upper()})
    report = {'passed': True, 'textures': 18, 'geometry_unchanged': True,
              'opaque_brake_atlases': changed, 'all_rgb_pixels_identical': True,
              'files': files, 'status': 'DXT1 appearance comparison; game QA pending'}
    (ROOT/'docs/carbon2018-stage-opaque-brake-verification.json').write_text(json.dumps(report, indent=2)+'\n')
    print('PASS: 5 DXT1 brake atlases, 13 unchanged textures, identical geometry')

if __name__ == '__main__':
    main()
