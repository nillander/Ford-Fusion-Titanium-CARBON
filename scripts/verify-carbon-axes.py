"""Gate the corrected 2018 staging for a reversible experimental in-game test."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(name):
    return json.loads((ROOT / 'docs' / name).read_text())


def main():
    mesh = read('carbon2018-stage-axes-audit.json')
    markers = read('carbon2018-stage-axes-markers.json')
    expected = read('carbon2018-mountpoints.json')['mounts']
    matrices = read('carbon2018-marker-matrix-remap.json')['markers']
    source = read('carbon2018-source-report.json')['parts']
    assert len(mesh) == 186 and len({m['hash'] for m in mesh}) == 186
    assert {m['name']: m['triangles'] for m in mesh} == {m['name']: m['triangles'] for m in source}
    maximum = max(sum(m['indices'] for m in s['materials']) for s in mesh)
    assert maximum <= 65535
    body = next(m for m in mesh if m['name'] == 'MUSTANGGT_KIT00_BODY_A')
    assert all(abs(x-y) < .01 for x,y in zip(body['min'], [-2.364096,-1.0413111,-.04379161]))
    assert all(abs(x-y) < .01 for x,y in zip(body['max'], [2.368057,1.0387574,1.2634124]))
    rear = next(m for m in mesh if m['name'] == 'MUSTANGGT_KIT00_RIGHT_BRAKELIGHT_GLASS_A')
    assert rear['max'][0] < 0
    tire = next(m for m in mesh if m['name'] == 'MUSTANGGT_KIT00_FRONT_TIRE_A')
    assert tire['max'][1]-tire['min'][1] < tire['max'][0]-tire['min'][0]
    assert sum(map(len, markers.values())) == len(expected) == len(matrices) == 165
    for p in expected:
        candidates = [m for m in markers.get('MUSTANGGT_'+p['part'], []) if m['name'] == p['marker']]
        assert any(max(abs(x-y) for x,y in zip(m['position'],p['carbon_position'])) <= .001 for m in candidates), p
    for p in matrices:
        assert any(m['hash'] == p['hash'] and max(abs(x-y) for x,y in zip(m['matrix'],p['matrix'])) <= .0001
                   for m in markers.get(p['part'], [])), p
    files = []
    for name in ['GEOMETRY.BIN', 'TEXTURES.BIN']:
        p = ROOT / 'work/carbon2018-stage-axes' / name
        files.append({'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size,
                      'sha256': hashlib.sha256(p.read_bytes()).hexdigest().upper()})
    assert files[1]['sha256'] == next(f['sha256'] for f in read('carbon2018-stage-verification.json')['files'] if f['path'].endswith('TEXTURES.BIN'))
    report = {'passed': True, 'solids': len(mesh), 'markers': len(expected), 'max_indices': maximum,
              'orientation': 'Carbon: front +X, left +Y', 'positions_tolerance_m': .001,
              'official_donor_matrix_remap_matches': True, 'files': files,
              'status': 'approved for reversible experimental test; full slot compatibility and visual QA pending'}
    (ROOT/'docs/carbon2018-stage-axes-verification.json').write_text(json.dumps(report, indent=2)+'\n')
    print('PASS: 186 meshes, corrected orientation, 165 marker positions/matrices, texture hash unchanged')


if __name__ == '__main__':
    main()
