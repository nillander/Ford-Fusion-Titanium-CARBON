"""Aerofólios e entrada de ar do teto do Fusion 2018 no MUSTANGGT (sem GUI).

1. Aerofólios flutuando (relato do usuário, 07/10 11:36). Medição com os modelos do
   próprio jogo (CARS/SPOILER, CARS/SPOILER_AS2) sobre a tampa do Fusion:
   - família SPOILER (comuns + AutoSculpt): pés ~2 cm acima da tampa;
   - SPOILER_AS2 (AutoSculpt 26–29, ponto SPOILER2): 8–9 cm acima. O SPOILER2 herdou
     do Mustang +5,6 cm porque lá esses aerofólios apoiam no ducktail de fábrica
     (KIT00_SPOILER até z 0,986), que o Fusion não tem.
   Ajuste: SPOILER −2,3 cm e SPOILER2 −8,7 cm em BASE_A..E (só a translação Z).
2. Entrada de ar do teto: o Carbon monta ROOF_SCOOP a partir da peça KIT00_ROOF,
   que o Fusion não tem (teto faz parte da carroceria). Acrescenta KIT00_ROOF_A..D
   clonados do MUSTANGGT oficial, invisíveis (índices zerados, como os DECAL ocultos
   pelo Codex), com ROOF_SCOOP no teto do Fusion: x 0,10, 1 cm abaixo da superfície
   (mesma relação do doador) e inclinação do teto do Fusion nesse ponto.
Base: work/carbon2018-stage-brakelight-lens (aprovado no jogo pelo usuário).

ROOF_MODE=none (padrão): só aerofólios. ROOF_MODE=roof: + KIT00_ROOF_A..D ocultos —
TRAVOU o jogo ao visualizar o carro (07/10 11:43). ROOF_MODE=roof+as: + ROOF_T0/T1 ocultos
(hipótese: o AutoSculpt do teto exige as zonas T0/T1 quando KIT00_ROOF existe).
"""
import hashlib, json, math, shutil, struct, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import jdlz

SRC = ROOT / 'work/carbon2018-stage-brakelight-lens'
SRC_SHA = 'DBAB50ED464FC9F2974697A5703850BA5CF182DF45E8CCA28119B5667B502B37'
import os
MODE = os.environ.get('ROOF_MODE', 'none')  # none | roof | roof+as
DST = ROOT / {'none': 'work/carbon2018-stage-spoiler', 'roof': 'work/carbon2018-stage-spoiler-roof', 'roof+as': 'work/carbon2018-stage-spoiler-roof-as'}[MODE]
DZ = {'SPOILER': -0.023, 'SPOILER2': -0.087}
ROOF_X = 0.10

def bh(s):
    h = 0xFFFFFFFF
    for ch in s.encode():
        h = (h * 33 + ch) & 0xFFFFFFFF
    return h

def chunks(d, a, b):
    while a + 8 <= b:
        k, s = struct.unpack_from('<II', d, a)
        yield k, a + 8, a + 8 + s
        a += 8 + s

def find(d, kind, a=0, b=None):
    b = len(d) if b is None else b
    for k, s, e in chunks(d, a, b):
        if k == kind: return s, e
        if k & 0x80000000:
            r = find(d, kind, s, e)
            if r: return r

def marker_records(d):
    s, e = find(d, 0x13401A)
    size = e - s
    pad = next(k for k in range(16) if (size - k) % 80 == 0 and all(x in (0, 0x11) for x in d[s:s + k]))
    return [s + pad + i * 80 for i in range((size - pad) // 80)]

def pad(out):
    g = (-len(out)) % 128
    if g < 8: g += 128
    out += struct.pack('<II', 0, g - 8) + b'\0' * (g - 8)

def fusion_roof():
    v = np.array([list(map(float, l.split()[1:4])) for n in ('BASE_A', 'KIT00_BODY_A')
                  for l in open(ROOT / f'work/carbon2018-source/{n}.obj') if l.startswith('v ')])
    def z(x):
        m = (abs(v[:, 0] - x) < 0.02) & (abs(v[:, 1]) < 0.05)
        return float(v[m][:, 2].max())
    zc = z(ROOF_X)
    slope = (z(ROOF_X + 0.08) - z(ROOF_X - 0.08)) / 0.16
    return zc, math.atan(-slope)  # ângulo positivo = frente mais baixa (como o doador)

def main():
    geo = (SRC / 'GEOMETRY.BIN').read_bytes()
    assert hashlib.sha256(geo).hexdigest().upper() == SRC_SHA
    audit = {a['hash']: a['name'] for a in json.loads((ROOT / 'docs/carbon2018-stage-dynamic-lights-audit.json').read_text())}
    donor = {a['name']: a for a in json.loads((ROOT / 'docs/carbon-mesh-audit.json').read_text())}
    ta, tb = find(geo, 0x134004)
    entries = [struct.unpack_from('<6I', geo, p) for p in range(ta, tb, 24)]
    report = {'spoiler_markers': [], 'roof_parts': []}
    blocks = {}
    for h, off, packed, un, fl, z in entries:
        blk = geo[off:off + packed]
        name = audit['%08X' % h]
        if name in {f'MUSTANGGT_BASE_{l}' for l in 'ABCDE'}:
            s = bytearray(jdlz.decompress(blk[24:]))
            for r in marker_records(s):
                mh = struct.unpack_from('<I', s, r)[0]
                for mname, dz in DZ.items():
                    if mh == bh(mname):
                        zo = struct.unpack_from('<f', s, r + 16 + 14 * 4)[0]
                        struct.pack_into('<f', s, r + 16 + 14 * 4, zo + dz)
                        report['spoiler_markers'].append({'part': name, 'marker': mname, 'z_before': round(zo, 5), 'z_after': round(zo + dz, 5)})
            s = bytes(s); c = jdlz.compress(s); assert jdlz.decompress(c) == s
            blk = struct.pack('<6I', 0x55441122, len(s), len(c) + 24, 0, 0, 0) + c
        blocks[h] = (blk, un, fl)
    assert len(report['spoiler_markers']) == 10
    zc, ang = fusion_roof()
    roof_pos = (ROOF_X, 0.0, round(zc - 0.01, 5))
    roof_names = [] if MODE == 'none' else [f'MUSTANGGT_KIT00_ROOF_{l}' for l in 'ABCD']
    if MODE == 'roof+as':
        roof_names += [f'MUSTANGGT_KIT00_ROOF_{t}_{l}' for t in ('T0', 'T1') for l in 'ABCD']
    for n in roof_names:
        h = int(donor[n]['hash'], 16)
        assert h not in blocks
        s = bytearray((ROOT / 'work/carbon-solids/MUSTANGGT' / (donor[n]['hash'] + '.bin')).read_bytes())
        ia, ib = find(s, 0x134B03); ia = (ia + 15) & ~15
        s[ia:ib] = b'\0' * (ib - ia)
        moved = 0
        donor_scoop = (0.08543, 0.0, 1.18652)
        for r in marker_records(s):
            mh = struct.unpack_from('<I', s, r)[0]
            if mh == bh('ROOF_SCOOP') or (('_T0_' in n or '_T1_' in n) and mh in (0x45D8B27B, 0x45D8B27C)):
                old = struct.unpack_from('<16f', s, r + 16)
                pos = [roof_pos[i] + old[12 + i] - donor_scoop[i] for i in range(3)]
                c_, s_ = math.cos(ang), math.sin(ang)
                m = [c_, 0, -s_, 0, 0, 1, 0, 0, s_, 0, c_, 0, pos[0], pos[1], pos[2], 1]
                struct.pack_into('<16f', s, r + 16, *m); moved += 1
        assert moved == 2, (n, moved)
        s = bytes(s); c = jdlz.compress(s); assert jdlz.decompress(c) == s
        blocks[h] = (struct.pack('<6I', 0x55441122, len(s), len(c) + 24, 0, 0, 0) + c, len(s), 0x200)
        report['roof_parts'].append({'part': n, 'hash': '%08X' % h, 'source': 'MUSTANGGT oficial (work/carbon-solids)',
                                     'indices_zeroed': ib - ia, 'roof_scoop': roof_pos, 'tilt_deg': round(math.degrees(ang), 2)})
    order = sorted(blocks)
    n = len(order)
    # Cabeçalho: chunk zero vazio + 0x80134001 { 0x134002, 0x134003, 0x134004 }.
    h2a, h2b = find(geo, 0x134002)
    h2 = bytearray(geo[h2a:h2b]); assert struct.unpack_from('<I', h2, 12)[0] == 186
    struct.pack_into('<I', h2, 12, n)
    l3 = b''.join(struct.pack('<II', h, 0) for h in order)
    l4 = bytearray(24 * n)
    body = struct.pack('<II', 0x134002, len(h2)) + h2 + struct.pack('<II', 0x134003, len(l3)) + l3 + \
           struct.pack('<II', 0x134004, len(l4)) + l4
    out = bytearray(struct.pack('<II', 0x80134000, 0) + struct.pack('<II', 0, 0) +
                    struct.pack('<II', 0x80134001, len(body)) + body)
    t4 = len(out) - len(l4)
    pad(out)
    for i, h in enumerate(order):
        blk, un, fl = blocks[h]
        off = len(out); out += blk; pad(out)
        struct.pack_into('<6I', out, t4 + i * 24, h, off, len(blk), un, fl, 0)
    struct.pack_into('<I', out, 4, len(out) - 8)
    DST.mkdir(exist_ok=True)
    (DST / 'GEOMETRY.BIN').write_bytes(out)
    shutil.copyfile(SRC / 'TEXTURES.BIN', DST / 'TEXTURES.BIN')

    # Verificação relendo o arquivo gravado.
    d = (DST / 'GEOMETRY.BIN').read_bytes()
    a, b = find(d, 0x134004)
    seen, same = 0, 0
    old = {e[0]: geo[e[1]:e[1] + e[2]] for e in entries}
    for p in range(a, b, 24):
        h, off, packed, un, fl, z = struct.unpack_from('<6I', d, p)
        blk = d[off:off + packed]
        assert off % 128 == 0 and struct.unpack_from('<I', blk, 0)[0] == 0x55441122
        sol = jdlz.decompress(blk[24:]); assert len(sol) == un
        if h in old and blk == old[h]: same += 1
        seen += 1
    assert seen == 186 + len(roof_names) and same == 181, (seen, same)
    assert d[8:16] == geo[8:16] and find(d, 0x134002)[1] - find(d, 0x134002)[0] == 144
    files = [{'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size,
              'sha256': hashlib.sha256(p.read_bytes()).hexdigest().upper()} for p in (DST / 'GEOMETRY.BIN', DST / 'TEXTURES.BIN')]
    report.update({'passed': True, 'solids': 186 + len(roof_names), 'mode': MODE, 'unchanged_blocks_bytewise': same, 'base': SRC_SHA,
                   'files': files, 'textures_unchanged': True,
                   'status': 'spoiler heights + hidden KIT00_ROOF for roof scoop; game QA pending'})
    (ROOT / ('docs/' + DST.name.replace('carbon2018-stage-', 'carbon2018-stage-') + '-verification.json')).write_text(json.dumps(report, indent=2) + '\n')
    print('PASS', MODE, files[0]['sha256'][:16], len(d), 'bytes;', seen, 'sólidos;', same, 'blocos idênticos')

if __name__ == '__main__':
    main()
