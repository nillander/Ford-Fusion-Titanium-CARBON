"""Use official MUSTANGGT lens settings and hide inherited decal surfaces.

Keep Fusion positions, UVs, topology and texture atlases. Decal solids remain
addressable but their triangles become degenerate, removing Mustang lettering.
Produces separate CIP/RAWW input for CarToolkit, never writes the game.
"""
import hashlib
import importlib.util
import json
import struct
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('colors',ROOT/'scripts/restore-carbon-vertex-colors.py')
colors=importlib.util.module_from_spec(spec)
spec.loader.exec_module(colors)

def aligned_chunk(data,kind):
    a,b=next((a,b) for k,a,b in colors.descendants(data,0,len(data)) if k==kind)
    return (a+15)&~15,b

def main():
    input_file=ROOT/'work/carbon2018-stage-colors/GEOMETRY.BIN'
    original=input_file.read_bytes()
    inventory=json.loads((ROOT/'docs/carbon2018-stage-colors-inventory.json').read_text())[0]
    assert hashlib.sha256(original).hexdigest().upper()==inventory['sha256']
    audit={r['hash']:r for r in json.loads((ROOT/'docs/carbon2018-stage-colors-audit.json').read_text())}
    donors={r['name']:r for r in json.loads((ROOT/'docs/carbon-mesh-audit.json').read_text()) if r['name'].startswith('MUSTANGGT_')}
    solids=[]
    records=[]
    for entry in inventory['streaming']:
        key=entry['hash']
        name=audit[key]['name']
        before=(ROOT/'work/carbon2018-stage-colors-solids/carbon2018-stage-colors'/(key+'.bin')).read_bytes()
        data=bytearray(before)
        changes={}
        if '_HEADLIGHT_GLASS_' in name or '_BRAKELIGHT_GLASS_' in name:
            donor_name=name if name in donors else name.rsplit('_',1)[0]+'_A'
            donor=(ROOT/'work/carbon-solids/MUSTANGGT'/(donors[donor_name]['hash']+'.bin')).read_bytes()
            h,_=aligned_chunk(data,0x134011)
            dh,_=aligned_chunk(donor,0x134011)
            data[h+14:h+16]=donor[dh+14:dh+16]
            g,end=aligned_chunk(data,0x134b02)
            dg,_=aligned_chunk(donor,0x134b02)
            assert (end-g)==144 and len(donors[donor_name]['materials'])==1
            assert struct.unpack_from('<H',data,g+48)[0]==struct.unpack_from('<H',donor,dg+48)[0]==4
            flags=struct.unpack_from('<I',donor,dg+56)[0]
            struct.pack_into('<I',data,g+56,flags)
            descriptor,_=aligned_chunk(data,0x134900)
            struct.pack_into('<I',data,descriptor+12,flags)
            lm,_=next((a,b) for k,a,b in colors.descendants(data,0,len(data)) if k==0x134013)
            dlm,_=next((a,b) for k,a,b in colors.descendants(donor,0,len(donor)) if k==0x134013)
            data[lm:lm+4]=donor[dlm:dlm+4]
            changes={'donor':donor_name,'flags':f'{flags:08X}', 'light_material':f'{struct.unpack_from("<I",data,lm)[0]:08X}'}
        if '_DECAL_' in name:
            a,b=aligned_chunk(data,0x134b03)
            data[a:b]=b'\0'*(b-a)
            changes={'decal_hidden':True,'triangles':audit[key]['triangles'],'method':'degenerate indices; solid retained'}
        if changes:
            records.append({'part':name,'hash':key,'before_sha256':hashlib.sha256(before).hexdigest().upper(),
                            'after_sha256':hashlib.sha256(data).hexdigest().upper(),**changes})
        solids.append(data)
    output=bytearray(original[:min(e['offset'] for e in inventory['streaming'])])
    table=[]
    def find_table(a,b):
        for k,s,e in colors.chunks(original,a,b):
            if k==0x134004:
                table.extend(range(s,e,24));return
            if k in (0x80134000,0x80134001):
                find_table(s,e)
            if table:return
    find_table(0,len(original))
    assert len(table)==len(solids)==186
    for offset,solid in zip(table,solids):
        output.extend(b'\0'*(-len(output)%128))
        start=len(output)
        blob=b'RAWW\x01\x10\x00\x00'+struct.pack('<II',len(solid),len(solid)+16)+solid
        packed=struct.pack('<6I',0x55441122,len(solid),len(blob)+24,0,0,0)+blob
        output.extend(packed)
        struct.pack_into('<III',output,offset+4,start,len(packed),len(solid))
    struct.pack_into('<I',output,4,len(output)-8)
    destination=ROOT/'work/carbon-compiler/geometry-lenses.bin'
    destination.write_bytes(output)
    report={'input_sha256':inventory['sha256'],'output_sha256':hashlib.sha256(output).hexdigest().upper(),
            'lens_solids':sum('donor' in r for r in records),'hidden_decal_solids':sum('decal_hidden' in r for r in records),
            'parts':records,'status':'official material settings applied; visual test pending'}
    (ROOT/'docs/carbon2018-lens-adaptation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'Adapted {report["lens_solids"]} lens solids; hid {report["hidden_decal_solids"]} decal solids')

if __name__=='__main__':main()
