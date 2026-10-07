"""Leitor somente-leitura de VPAK do NFS Carbon (attributes.bin, FE_ATTRIB.bin, gameplay.bin).

Uso: python scripts/vlt_dump.py <arquivo VPAK> [--json saida.json]
Lista coleções (classe, nome, pai) com nomes resolvidos pelo bloco StrE e pelo
hash VLT (Jenkins lookup2, initval 0xABCDEF00). Não escreve nada no jogo.
Formato de chunks baseado em OpenNFSTools/VLTEdit (VLTFile.cs, CARBON).
"""
import json, struct, sys

M = 0xFFFFFFFF

def _mix(a, b, c):
    a = (a - b - c) & M; a ^= c >> 13
    b = (b - c - a) & M; b ^= (a << 8) & M
    c = (c - a - b) & M; c ^= b >> 13
    a = (a - b - c) & M; a ^= c >> 12
    b = (b - c - a) & M; b ^= (a << 16) & M
    c = (c - a - b) & M; c ^= b >> 5
    a = (a - b - c) & M; a ^= c >> 3
    b = (b - c - a) & M; b ^= (a << 10) & M
    c = (c - a - b) & M; c ^= b >> 15
    return a, b, c

def vlt_hash(s, init=0xABCDEF00):
    k = s.encode('ascii') if isinstance(s, str) else s
    a = b = 0x9E3779B9; c = init; n = len(k); i = 0; rem = n
    while rem >= 12:
        a = (a + struct.unpack_from('<I', k, i)[0]) & M
        b = (b + struct.unpack_from('<I', k, i + 4)[0]) & M
        c = (c + struct.unpack_from('<I', k, i + 8)[0]) & M
        a, b, c = _mix(a, b, c); i += 12; rem -= 12
    c = (c + n) & M
    t = k[i:] + b'\0' * 12
    if rem > 10: c = (c + (t[10] << 24)) & M
    if rem > 9:  c = (c + (t[9] << 16)) & M
    if rem > 8:  c = (c + (t[8] << 8)) & M
    if rem > 7:  b = (b + (t[7] << 24)) & M
    if rem > 6:  b = (b + (t[6] << 16)) & M
    if rem > 5:  b = (b + (t[5] << 8)) & M
    if rem > 4:  b = (b + t[4]) & M
    if rem > 3:  a = (a + (t[3] << 24)) & M
    if rem > 2:  a = (a + (t[2] << 16)) & M
    if rem > 1:  a = (a + (t[1] << 8)) & M
    if rem > 0:  a = (a + t[0]) & M
    return _mix(a, b, c)[2]

def chunks(d):
    o = 0
    while o + 8 <= len(d):
        cid, ln = struct.unpack_from('<4sI', d, o)
        if ln < 8: break
        yield cid[::-1].decode('latin1'), o + 8, ln - 8
        o += ln

def read_vpak(path):
    d = open(path, 'rb').read()
    assert d[:4] == b'VPAK', 'não é VPAK'
    count, names_off = struct.unpack_from('<II', d, 4)
    vaults = []
    for i in range(count):
        e = 0x10 + i * 0x14
        name_off, bin_size, vlt_size, bin_off, vlt_off = struct.unpack_from('<5I', d, e)
        name = d[names_off + name_off:d.index(b'\0', names_off + name_off)].decode()
        vaults.append((name, d[bin_off:bin_off + bin_size], d[vlt_off:vlt_off + vlt_size]))
    return vaults

def parse_vault(name, binb, vltb, names):
    for cid, o, ln in chunks(binb):
        if cid == 'StrE':
            for s in binb[o:o + ln].split(b'\0'):
                if s:
                    try: t = s.decode('ascii')
                    except UnicodeDecodeError: continue
                    names.setdefault(vlt_hash(t), t)
    exp = None
    for cid, o, ln in chunks(vltb):
        if cid == 'ExpN': exp = (o, ln)
    out = {'vault': name, 'classes': [], 'collections': []}
    if not exp: return out
    o, _ = exp
    n = struct.unpack_from('<I', vltb, o)[0]
    for i in range(n):
        _id, typ, ln, off = struct.unpack_from('<4I', vltb, o + 4 + i * 16)
        if typ == 0x5e970cbc:
            h, ncoll, nfields = struct.unpack_from('<III', vltb, off)
            out['classes'].append({'hash': h, 'collections': ncoll, 'fields': nfields})
        elif typ == 0x8e112eb7:
            h, cls, par, nopt, _n1, _n2 = struct.unpack_from('<6I', vltb, off)
            cnt, tot = struct.unpack_from('<hh', vltb, off + 24)
            p = off + 28 + 4 + tot * 4
            opt = []
            for j in range(nopt):
                fh, _ptr, f1, f2 = struct.unpack_from('<IIhh', vltb, p + j * 12)
                opt.append(fh)
            out['collections'].append({'hash': h, 'class': cls, 'parent': par,
                                        'layout_fields': cnt, 'optional_fields': opt})
    return out

def main():
    path = sys.argv[1]
    extra = []
    if '--names' in sys.argv:
        extra = open(sys.argv[sys.argv.index('--names') + 1]).read().split()
    names = {}
    for w in extra: names.setdefault(vlt_hash(w), w)
    res = [parse_vault(n, b, v, names) for n, b, v in read_vpak(path)]
    nm = lambda h: names.get(h, '0x%08X' % h)
    for r in res:
        for c in r['classes']: c['name'] = nm(c['hash'])
        for c in r['collections']:
            c['name'] = nm(c['hash']); c['class_name'] = nm(c['class'])
            c['parent_name'] = nm(c['parent']) if c['parent'] else ''
            c['optional_field_names'] = [nm(f) for f in c.pop('optional_fields')]
    if '--json' in sys.argv:
        json.dump(res, open(sys.argv[sys.argv.index('--json') + 1], 'w'), indent=1)
    for r in res:
        print('vault', r['vault'], len(r['classes']), 'classes', len(r['collections']), 'collections')

if __name__ == '__main__':
    main()
