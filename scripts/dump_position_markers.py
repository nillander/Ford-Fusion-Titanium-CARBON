"""Extrai position markers (chunk 0x13401A, 80 bytes cada) de sólidos Carbon
já descomprimidos (work/carbon-solids/<SLOT>/<hash>.bin ou staging).

Uso: python scripts/dump_position_markers.py <pasta de sólidos> <audit.json> <saida.json>
Somente leitura. Nomes dos marcadores resolvidos por bin hash (h*33+c, init 0xFFFFFFFF)
a partir de work/carbon-compiler/mp.txt e de uma lista extra embutida.
"""
import json, os, struct, sys

def bin_hash(s):
    h = 0xFFFFFFFF
    for ch in s.encode():
        h = (h * 33 + ch) & 0xFFFFFFFF
    return h

EXTRA = ('CENTRE_BRAKELIGHT COPLIGHTBLUE COPLIGHTRED COPLIGHTWHITE FRONT_BRAKE HOOD '
         'LEFT_BRAKELIGHT LEFT_EXHAUST LEFT_HEADLIGHT LEFT_REVERSE LEFT_SIDE_MIRROR '
         'RIGHT_BRAKELIGHT RIGHT_HEADLIGHT RIGHT_REVERSE RIGHT_SIDE_MIRROR ROOF_SCOOP '
         'SPOILER SPOILER2 TRUNK EXHAUST EXHAUST_AS LICENSEPLATE RIGHT_EXHAUST CENTRE_EXHAUST '
         'FRONT_LEFT_WHEEL FRONT_RIGHT_WHEEL REAR_LEFT_WHEEL REAR_RIGHT_WHEEL REAR_BRAKE '
         'LEFT_BRAKELIGHT_GLOW RIGHT_BRAKELIGHT_GLOW DRIVER SPOILER_AS SPOILER_AS2 '
         'HOOD_SCOOP ROOF INTERIOR STEERING_WHEEL SPOILER_HATCH SPOILER_PORSCHES SPOILER_CARRERA').split()

def names_table(mp_path):
    names = set(EXTRA)
    manual = {}
    if os.path.exists(mp_path):
        for line in open(mp_path, encoding='latin1'):
            p = line.split()
            if len(p) >= 2 and not line.startswith('#'):
                if p[0].lower().startswith('0x'):
                    manual[int(p[0], 16)] = p[1]
                else:
                    names.add(p[-1])
    table = {bin_hash(n): n for n in names}
    table.update(manual)
    return table

def markers(data):
    out = []
    i = 0
    pat = struct.pack('<I', 0x13401A)
    while True:
        i = data.find(pat, i)
        if i < 0: break
        size = struct.unpack_from('<I', data, i + 4)[0]
        start = i + 8
        pad = next((k for k in range(16) if (size - k) > 0 and (size - k) % 80 == 0
                    and all(b in (0, 0x11) for b in data[start:start + k])), None)
        p = start + (pad or 0)
        body = size - (pad or 0)
        if pad is not None and start + size <= len(data):
            for k in range(body // 80):
                o = p + k * 80
                h, ip, fp, fl = struct.unpack_from('<IifI', data, o)
                m = struct.unpack_from('<16f', data, o + 16)
                out.append({'hash': '%08X' % h, 'iparam': ip, 'fparam': fp, 'flags': fl,
                            'position': [round(m[12], 5), round(m[13], 5), round(m[14], 5)],
                            'matrix': [round(v, 5) for v in m]})
            i = start + size
        else:
            i += 4
    return out

def main():
    root, audit, dst = sys.argv[1:4]
    byhash = {a['hash'].upper(): a['name'] for a in json.load(open(audit))}
    table = names_table('work/carbon-compiler/mp.txt')
    res = {}
    for fn in sorted(os.listdir(root)):
        if not fn.lower().endswith('.bin'): continue
        ms = markers(open(os.path.join(root, fn), 'rb').read())
        if not ms: continue
        for m in ms:
            m['name'] = table.get(int(m['hash'], 16), '')
        res[byhash.get(fn[:-4].upper(), fn[:-4])] = ms
    json.dump(res, open(dst, 'w'), indent=1)
    print(len(res), 'sólidos com marcadores;', sum(len(v) for v in res.values()), 'marcadores')

if __name__ == '__main__':
    main()
