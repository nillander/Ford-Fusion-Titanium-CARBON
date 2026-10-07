"""Recover MW vertex color/alpha after OBJ compilation, preserving other bytes.

Requires decoded Carbon solids and a matching inventory. Output is CIP/RAWW
for CarToolkit normalization; never writes the installed game.
"""
import argparse
import hashlib
import importlib.util
import json
import struct
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]

def chunks(data, start, end):
    while start < end:
        kind, size = struct.unpack_from('<II', data, start)
        stop = start+8+size
        if stop > end:
            raise ValueError('Invalid chunk extent')
        yield kind, start+8, stop
        start = stop

def descendants(data, start, end):
    for kind,a,b in chunks(data,start,end):
        yield kind,a,b
        if kind & 0x80000000:
            yield from descendants(data,a,b)

def main():
    cli = argparse.ArgumentParser()
    cli.add_argument('input', type=Path)
    cli.add_argument('inventory', type=Path)
    cli.add_argument('solids', type=Path)
    cli.add_argument('output', type=Path)
    args = cli.parse_args()
    original = args.input.read_bytes()
    catalogue = json.loads(args.inventory.read_text())[0]
    if hashlib.sha256(original).hexdigest().upper() != catalogue['sha256']:
        raise ValueError('Inventory hash differs')
    spec = importlib.util.spec_from_file_location('mwgeo', ROOT.parent/'fusion-mw2005/scripts/lente-vidros-capo/mwgeo.py')
    mwgeo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mwgeo)
    source_file = next(p for p in (ROOT/'reference/mw-v28/Fusion2018_AWD_MW2005').rglob('GEOMETRY.BIN') if 'ADDONS' not in p.parts)
    source = {p['hash']: p for p in mwgeo.load(source_file)}
    modified, reports = [], []
    for entry in catalogue['streaming']:
        data = bytearray((args.solids/(entry['hash']+'.bin')).read_bytes())
        p = source[int(entry['hash'],16)]
        vertices = p['vbs'][0]
        lookup = {}
        for v in vertices:
            key = tuple(np.round(np.concatenate([v['p'],v['uv']]).astype('float64'),5))
            lookup.setdefault(key,set()).add(int(v['c']))
        allchunks = list(descendants(data,0,len(data)))
        groups = next((a,b) for k,a,b in allchunks if k==0x134b02)
        a,b = groups
        a = (a+15)&~15
        streams = []
        for off in range(a,b,144):
            effect = struct.unpack_from('<H',data,off+48)[0]
            count = struct.unpack_from('<I',data,off+64)[0]
            if not streams or effect != streams[-1][0]:
                streams.append([effect,count])
            else:
                streams[-1][1] += count
        buffers = [(a,b) for k,a,b in allchunks if k==0x134b01]
        if len(buffers)!=len(streams):
            raise ValueError('Unexpected stream count')
        changed = matched = 0
        for (a,b),(effect,count) in zip(buffers,streams):
            a=(a+15)&~15
            if (b-a)%count:
                raise ValueError('Invalid vertex stride')
            stride=(b-a)//count
            if effect==4:
                color_offset, uv_offset = 24,28
            elif effect in (5,25):
                color_offset, uv_offset = 20,12
            else:
                raise ValueError(f'Unsupported effect {effect}')
            for off in range(a,b,stride):
                position=struct.unpack_from('<3f',data,off)
                uv=struct.unpack_from('<2f',data,off+uv_offset)
                key=tuple(np.round(position+uv,5))
                colors=lookup.get(key)
                if not colors:
                    # Float rounding can cross a cell boundary. Compare actual
                    # coordinates, never guess transparency from a nearby part.
                    delta=np.max(np.abs(vertices['p']-position),axis=1)
                    mask=(delta<=0.000002)&(np.max(np.abs(vertices['uv']-uv),axis=1)<=0.000002)
                    colors=set(map(int,vertices['c'][mask]))
                if len(colors)!=1:
                    raise ValueError(f'No unambiguous source color: {p["name"]}, {position}, {uv}, {colors}')
                color=next(iter(colors))
                old=struct.unpack_from('<I',data,off+color_offset)[0]
                struct.pack_into('<I',data,off+color_offset,color)
                changed += old!=color
                matched += 1
        reports.append({'part':p['name'],'matched_vertices':matched,'changed_colors':changed})
        modified.append(data)
    output=bytearray(original[:min(e['offset'] for e in catalogue['streaming'])])
    table=[]
    def find_table(start,end):
        for k,a,b in chunks(original,start,end):
            if k==0x134004:
                table.extend(range(a,b,24))
                return
            if k in (0x80134000,0x80134001):
                find_table(a,b)
            if table:
                return
    find_table(0,len(original))
    if len(table)!=len(modified):
        raise ValueError('Catalogue length differs')
    for off,solid in zip(table,modified):
        output.extend(b'\0'*(-len(output)%128))
        position=len(output)
        blob=b'RAWW\x01\x10\x00\x00'+struct.pack('<II',len(solid),len(solid)+16)+solid
        packed=struct.pack('<6I',0x55441122,len(solid),len(blob)+24,0,0,0)+blob
        output.extend(packed)
        struct.pack_into('<III',output,off+4,position,len(packed),len(solid))
    struct.pack_into('<I',output,4,len(output)-8)
    if args.output.resolve()==args.input.resolve():
        raise ValueError('Output must be separate')
    args.output.write_bytes(output)
    report={'source_sha256':hashlib.sha256(source_file.read_bytes()).hexdigest().upper(),
            'input_sha256':catalogue['sha256'],'output_sha256':hashlib.sha256(output).hexdigest().upper(),
            'parts':reports,'changed_colors':sum(r['changed_colors'] for r in reports),
            'status':'colors restored; CarToolkit reexport and visual test pending'}
    (ROOT/'docs/carbon2018-color-restoration.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'Restored {report["changed_colors"]} colors across {len(reports)} solids')

if __name__=='__main__':
    main()
