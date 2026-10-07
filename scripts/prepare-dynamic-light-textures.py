"""Use the official Mustang's dynamic diffuse texture slots for eight main lights."""
import hashlib
import importlib.util
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('lens',ROOT/'scripts/prepare-carbon-lenses.py')
lens = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lens)

def main():
    stage = ROOT/'work/carbon2018-stage-diffuse-brake'
    original = (stage/'GEOMETRY.BIN').read_bytes()
    inv = json.loads((ROOT/'docs/carbon2018-stage-diffuse-brake-inventory.json').read_text())[0]
    assert hashlib.sha256(original).hexdigest().upper() == inv['sha256']
    names = {p['hash']:p['name'] for p in json.loads((ROOT/'docs/carbon2018-stage-diffuse-brake-audit.json').read_text())}
    donors = {p['name']:p for p in json.loads((ROOT/'docs/carbon-mesh-audit.json').read_text())}
    expected = ROOT/'work/carbon2018-dynamic-expected'
    expected.mkdir(exist_ok=True)
    solids, changes = [], []
    for entry in inv['streaming']:
        name = names[entry['hash']]
        data = bytearray((ROOT/'work/carbon2018-stage-diffuse-brake-solids/carbon2018-stage-diffuse-brake'/(entry['hash']+'.bin')).read_bytes())
        family = next((f for f in ['HEADLIGHT','BRAKELIGHT'] if name in
                       {f'MUSTANGGT_KIT00_RIGHT_{f}_{lod}' for lod in 'ABCD'}),None)
        if family:
            donor = donors[f'MUSTANGGT_KIT00_RIGHT_{family}_A']
            raw = (ROOT/'work/carbon-solids/MUSTANGGT'/(donor['hash']+'.bin')).read_bytes()
            da, db = next((a,b) for k,a,b in lens.colors.descendants(raw,0,len(raw)) if k == 0x134012)
            slot = 1 if family == 'HEADLIGHT' else 0
            dynamic = raw[da+slot*8:da+slot*8+4]
            assert struct.unpack('<I',dynamic)[0] == {'HEADLIGHT':0xF68EF19F,'BRAKELIGHT':0x02B52399}[family]
            a,b = next((a,b) for k,a,b in lens.colors.descendants(data,0,len(data)) if k == 0x134012)
            assert b-a == 8
            data[a:a+4] = dynamic
            changes.append({'part':name,'dynamic_texture':f'{struct.unpack("<I",dynamic)[0]:08X}',
                            'donor':donor['name']})
        (expected/(entry['hash']+'.bin')).write_bytes(data)
        solids.append(data)
    assert len(changes) == 8
    output = bytearray(original[:min(e['offset'] for e in inv['streaming'])])
    table=[]
    def visit(a,b):
        for k,s,e in lens.colors.chunks(original,a,b):
            if k == 0x134004: table.extend(range(s,e,24)); return
            if k in (0x80134000,0x80134001): visit(s,e)
            if table:return
    visit(0,len(original))
    assert len(table) == len(solids) == 186
    for off,solid in zip(table,solids):
        output.extend(b'\0'*(-len(output)%128));start=len(output)
        blob=b'RAWW\x01\x10\x00\x00'+struct.pack('<II',len(solid),len(solid)+16)+solid
        packed=struct.pack('<6I',0x55441122,len(solid),len(blob)+24,0,0,0)+blob
        output.extend(packed);struct.pack_into('<III',output,off+4,start,len(packed),len(solid))
    struct.pack_into('<I',output,4,len(output)-8)
    (ROOT/'work/carbon-compiler/geometry-dynamic-lights.bin').write_bytes(output)
    (ROOT/'docs/carbon2018-dynamic-lights-plan.json').write_text(json.dumps(changes,indent=2)+'\n')
    print('Prepared 8 official dynamic texture slots; 178 other solids unchanged')

if __name__ == '__main__':main()
