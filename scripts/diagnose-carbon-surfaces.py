"""Compare source triangles/material names without changing game assets."""
import importlib.util
import itertools
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('mwgeo', ROOT.parent/'fusion-mw2005/scripts/lente-vidros-capo/mwgeo.py')
mwgeo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mwgeo)

def bh(text):
    value = 0xffffffff
    for c in text.encode('ascii'):
        value = (value*33+c) & 0xffffffff
    return value

def main():
    names = {bh(n.strip()): n.strip() for n in (ROOT/'tools/vendor/carbon-modtools/NFS Carbon ModTools v1.1/bin/materials.txt').read_text().splitlines()}
    parts = mwgeo.load(next(p for p in (ROOT/'reference/mw-v28/Fusion2018_AWD_MW2005').rglob('GEOMETRY.BIN') if 'ADDONS' not in p.parts))
    material_report = {}
    triangles = {}
    for p in parts:
        offset = 0
        keys = set()
        for g in p['groups']:
            count = g['tris']*3
            indices = p['idx'][offset:offset+count]
            shader = p['sh'][g['sh']]
            key = f'{shader:08X}'
            rec = material_report.setdefault(key, {'name': names.get(shader), 'triangles': 0, 'colors': set(), 'texture_slots': set()})
            rec['triangles'] += g['tris']
            rec['colors'].update(f'{int(c):08X}' for c in np.unique(p['vbs'][0]['c'][indices]))
            rec['texture_slots'].add(tuple(f'{p["tex"][i]:08X}' for i in g['tex']))
            if p['name'].endswith('_A') and ('_BASE_' in p['name'] or '_KIT00_' in p['name']):
                xyz = np.round(p['vbs'][0]['p'][indices].reshape(-1,3,3), 5)
                keys.update(tuple(sorted(tuple(v) for v in tri)) for tri in xyz)
            offset += count
        if keys:
            triangles[p['name']] = keys
    overlaps = []
    for (a, x), (b, y) in itertools.combinations(triangles.items(), 2):
        common = len(x & y)
        if common:
            overlaps.append({'a': a, 'b': b, 'identical_triangles_10um': common, 'a_triangles': len(x), 'b_triangles': len(y)})
    for rec in material_report.values():
        rec['colors'] = sorted(rec['colors'])
        rec['texture_slots'] = sorted(rec['texture_slots'])
    report = {'materials': material_report, 'source_overlaps': sorted(overlaps, key=lambda r: -r['identical_triangles_10um']), 'scope': 'source evidence only; overlap does not prove simultaneous rendering'}
    (ROOT/'docs/carbon2018-surface-diagnosis.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({'materials': {k: {'name': v['name'], 'colors': len(v['colors']), 'texture_sets': len(v['texture_slots'])} for k,v in material_report.items()}, 'overlaps': report['source_overlaps'][:15]}, indent=2))

if __name__ == '__main__':
    main()
