"""Replace only eight main light solids; retain body and official mount matrices."""
import hashlib
import importlib.util
import json
import struct
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('lens',ROOT/'scripts/prepare-carbon-lenses.py')
lens=importlib.util.module_from_spec(spec)
spec.loader.exec_module(lens)

def main():
    original=(ROOT/'work/carbon2018-stage-lenses/GEOMETRY.BIN').read_bytes()
    catalog=json.loads((ROOT/'docs/carbon2018-stage-lenses-inventory.json').read_text())[0]
    assert hashlib.sha256(original).hexdigest().upper()==catalog['sha256']
    plan=json.loads((ROOT/'docs/carbon2018-integrated-lights-plan.json').read_text())
    names={p['part'] for p in plan}
    audit={p['hash']:p['name'] for p in json.loads((ROOT/'docs/carbon2018-stage-lenses-audit.json').read_text())}
    donor={p['name']:p for p in json.loads((ROOT/'docs/carbon-mesh-audit.json').read_text())}
    parts=[]
    for entry in catalog['streaming']:
        key=entry['hash'];name=audit[key]
        if name in names:
            data=bytearray((ROOT/'work/integrated-light-solids/carbon-compiler'/(key+'.bin')).read_bytes())
            start,end=lens.aligned_chunk(data,0x134b02)
            assert end-start==288
            # nfscgc stores triangle counts in NumVerts for multi-material OBJ.
            # Infer exact contiguous vertex ranges from the emitted indices,
            # validating against the actual 48-byte CarShader stream.
            ia,ib=lens.aligned_chunk(data,0x134b03)
            index_offset=ia
            vertex_total=0
            for group in range(start,end,144):
                count=struct.unpack_from('<I',data,group+96)[0]*3
                values=struct.unpack_from(f'<{count}H',data,index_offset)
                assert min(values)==vertex_total
                n=max(values)-min(values)+1
                struct.pack_into('<I',data,group+64,n)
                vertex_total+=n
                index_offset+=count*2
            va,vb=lens.aligned_chunk(data,0x134b01)
            assert vb-va==vertex_total*48 and index_offset==ib
            # The second shading group is the newly appended lens.
            struct.pack_into('<I',data,start+144+56,0x14180)
            dname=name.rsplit('_',1)[0]+'_GLASS_A'
            d=(ROOT/'work/carbon-solids/MUSTANGGT'/(donor[dname]['hash']+'.bin')).read_bytes()
            lm,end=next((a,b) for k,a,b in lens.colors.descendants(data,0,len(data)) if k==0x134013)
            dlm,_=next((a,b) for k,a,b in lens.colors.descendants(d,0,len(d)) if k==0x134013)
            assert end-lm==16
            data[lm+8:lm+12]=d[dlm:dlm+4]
            descriptor,_=lens.aligned_chunk(data,0x134900)
            struct.pack_into('<I',data,descriptor+12,0x14180)
            struct.pack_into('<I',data,descriptor+24,1)
        else:
            data=bytearray((ROOT/'work/carbon2018-stage-lenses-solids/carbon2018-stage-lenses'/(key+'.bin')).read_bytes())
            if any(s in name for s in ['_HEADLIGHT_GLASS_','_BRAKELIGHT_GLASS_']):
                a,b=lens.aligned_chunk(data,0x134b03)
                data[a:b]=b'\0'*(b-a)
        parts.append(data)
    output=bytearray(original[:min(e['offset'] for e in catalog['streaming'])])
    table=[]
    def find(a,b):
        for k,s,e in lens.colors.chunks(original,a,b):
            if k==0x134004:table.extend(range(s,e,24));return
            if k in (0x80134000,0x80134001):find(s,e)
            if table:return
    find(0,len(original))
    assert len(table)==len(parts)==186
    for off,solid in zip(table,parts):
        output.extend(b'\0'*(-len(output)%128));start=len(output)
        blob=b'RAWW\x01\x10\x00\x00'+struct.pack('<II',len(solid),len(solid)+16)+solid
        packed=struct.pack('<6I',0x55441122,len(solid),len(blob)+24,0,0,0)+blob
        output.extend(packed)
        struct.pack_into('<III',output,off+4,start,len(packed),len(solid))
    struct.pack_into('<I',output,4,len(output)-8)
    (ROOT/'work/carbon-compiler/geometry-integrated-lights.bin').write_bytes(output)
    print('Merged eight main lights; separate lens solids hidden; 170 other solids preserved')

if __name__=='__main__':main()
