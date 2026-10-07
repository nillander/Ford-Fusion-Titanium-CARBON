"""Preserve official MUSTANGGT marker matrices in a decoded nfscgc output.

Keep Fusion marker names and translations; use the corresponding donor part,
falling back to the official BASE_A, KIT00_BODY_A or FRONT_TIRE_A family.
Repack decoded solids as CIP/RAWW. The separate output still requires CarToolkit
normalization and independent audit.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path


def chunks(data, start, end):
    while start < end:
        if start + 8 > end:
            raise ValueError('Truncated chunk header')
        kind, size = struct.unpack_from('<II', data, start)
        stop = start + 8 + size
        if stop > end:
            raise ValueError('Chunk exceeds container')
        yield kind, start + 8, stop
        start = stop


def main():
    cli = argparse.ArgumentParser()
    cli.add_argument('input', type=Path)
    cli.add_argument('output', type=Path)
    cli.add_argument('--inventory', type=Path, default=Path('docs/carbon2018-axes-compiled-inventory.json'))
    cli.add_argument('--solids-root', type=Path, default=Path('work/carbon2018-axes-compiled-solids/carbon-compiler'))
    args = cli.parse_args()
    if args.input.resolve() == args.output.resolve():
        raise ValueError('Use a separate output file')
    donor = json.loads(Path('docs/mustanggt-stock-markers.json').read_text())
    original = args.input.read_bytes()
    catalogue = json.loads(args.inventory.read_text())[0]
    if hashlib.sha256(original).hexdigest().upper() != catalogue['sha256']:
        raise ValueError('Compiled input differs from inventory')
    data = bytearray()
    records = []

    def walk(start, end):
        for kind, payload, stop in chunks(data, start, end):
            if kind == 0x80134010:
                children = list(chunks(data, payload, stop))
                header = next((a, b) for k, a, b in children if k == 0x134011)
                name_start = ((header[0] + 15) & ~15) + 160
                name = data[name_start:data.index(0, name_start, header[1])].decode('ascii')
                for k, a, b in children:
                    if k != 0x13401A:
                        continue
                    pad = next((n for n in range(16) if (b-a-n)>0 and
                                (b-a-n)%80 == 0 and all(v in (0, 0x11) for v in data[a:a+n])), None)
                    if pad is None:
                        raise ValueError('Invalid marker extent')
                    for offset in range(a+pad, b, 80):
                        key = f'{struct.unpack_from("<I", data, offset)[0]:08X}'
                        source_part = name
                        choices = [m for m in donor.get(source_part, []) if m['hash'] == key]
                        if not choices:
                            family = 'BASE_A' if '_BASE_' in name else 'KIT00_FRONT_TIRE_A' if '_FRONT_TIRE_' in name else 'KIT00_BODY_A'
                            source_part = 'MUSTANGGT_' + family
                            choices = [m for m in donor.get(source_part, []) if m['hash'] == key]
                        if not choices:
                            raise ValueError(f'No official matrix for {name}/{key}')
                        # Repeated exhaust markers can be matched to the nearest side.
                        position = struct.unpack_from('<3f', data, offset+64)
                        source = min(choices, key=lambda m: sum((x-y)**2 for x,y in zip(m['position'], position)))
                        struct.pack_into('<12f', data, offset+16, *source['matrix'][:12])
                        records.append({'part': name, 'marker': source['name'], 'hash': key,
                                        'donor_part': source_part, 'position': position,
                                        'matrix': list(source['matrix'][:12]) + list(position) + [1.0]})
            elif kind in (0x80134000, 0x80134001):
                walk(payload, stop)

    solids = []
    for entry in catalogue['streaming']:
        data = bytearray((args.solids_root / (entry['hash'] + '.bin')).read_bytes())
        if len(data) != entry['bytes']:
            raise ValueError('Decoded solid size mismatch')
        walk(0, len(data))
        solids.append((entry, data))
    if len(records) != 165:
        raise ValueError(f'Expected 165 markers, found {len(records)}')
    # Preserve the compiler catalogue, replacing only streaming extents and sizes.
    # Keep CIP streaming with lossless RAWW blobs for CarToolkit input.
    output = bytearray(original[:min(e['offset'] for e in catalogue['streaming'])])
    table_offsets = []
    def find_table(start, end):
        for kind, payload, stop in chunks(original, start, end):
            if kind == 0x134004:
                table_offsets.extend(range(payload, stop, 24))
            elif kind in (0x80134000, 0x80134001):
                find_table(payload, stop)
            if table_offsets:
                return
    find_table(0, len(original))
    if len(table_offsets) != len(solids):
        raise ValueError('Streaming table size mismatch')
    for table_offset, (entry, solid) in zip(table_offsets, solids):
        output.extend(b'\0' * (-len(output) % 128))
        offset = len(output)
        blob = b'RAWW\x01\x10\x00\x00' + struct.pack('<II', len(solid), len(solid)+16) + solid
        packed = struct.pack('<6I', 0x55441122, len(solid), len(blob)+24, 0, 0, 0) + blob
        output.extend(packed)
        struct.pack_into('<III', output, table_offset+4, offset, len(packed), len(solid))
    struct.pack_into('<I', output, 4, len(output)-8)
    args.output.write_bytes(output)
    Path('docs/carbon2018-marker-matrix-remap.json').write_text(json.dumps({
        'input': str(args.input), 'output': str(args.output),
        'sha256': hashlib.sha256(output).hexdigest().upper(), 'markers': records,
        'status': 'official donor matrices applied; reexport/audit required'}, indent=2)+'\n')
    print(f'Applied {len(records)} official marker matrices; Fusion translations preserved')


if __name__ == '__main__':
    main()
