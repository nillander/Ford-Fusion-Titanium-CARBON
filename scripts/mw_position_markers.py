"""Extrai position markers de um GEOMETRY.BIN MW (não comprimido), por sólido.
Uso: python scripts/mw_position_markers.py <GEOMETRY.BIN MW> <saida.json>"""
import json, re, struct, sys
sys.path.insert(0, __file__.rsplit('/', 1)[0] if '/' in __file__ else '.')
from dump_position_markers import markers, names_table

def main(path, dst):
    d = open(path, 'rb').read()
    t = names_table('work/carbon-compiler/mp.txt')
    pat = struct.pack('<I', 0x134011)
    idx = [m.start() for m in re.finditer(re.escape(pat), d)]
    res = {}
    for k, i in enumerate(idx):
        seg = d[i:idx[k + 1] if k + 1 < len(idx) else len(d)]
        m = re.search(rb'(?:MUSTANGGT|COBALTSS|CAMARO)_[A-Z0-9_]+', d[i:i + 0x140])
        name = m.group().decode() if m else '%X' % i
        ms = markers(seg)
        for x in ms:
            x['name'] = t.get(int(x['hash'], 16), '')
        if ms:
            res[name] = ms
    json.dump(res, open(dst, 'w'), indent=1)
    print(len(idx), 'sólidos;', len(res), 'com marcadores;', sum(len(v) for v in res.values()), 'marcadores')

if __name__ == '__main__':
    main(*sys.argv[1:3])
