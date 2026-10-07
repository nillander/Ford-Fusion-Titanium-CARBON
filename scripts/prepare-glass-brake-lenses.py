"""Lente traseira: troca DULLPLASTIC por um light material oficial, mantendo o vínculo dinâmico.

LENS_VARIANT=glass  -> BRAKELIGHTGLASS/0x14180. TRAVOU O JOGO (07/10 11:27): no MUSTANGGT
  oficial BRAKELIGHTGLASS só aparece com a textura BRAKELIGHT_GLASS_RIGHT (01F40B32),
  não com BRAKELIGHT_RIGHT (02B52399). Não instalar.
LENS_VARIANT=brakelight (padrão) -> BRAKELIGHT/0x4180, par oficial do corpo da lanterna.


Contexto (07/10, Claude): no teste `diffuse-brake` o grupo externo das lanternas
(KIT00_RIGHT_BRAKELIGHT_A..D, material 1) passou para DULLPLASTIC/0x4180 enquanto o
problema real ainda era o vínculo da textura. O vínculo dinâmico (dynamic-lights)
resolveu o vermelho, mas a lente ficou com plástico fosco: escura. Esta etapa restaura
só esse grupo à configuração do vidro oficial (BRAKELIGHTGLASS, 0x14180), a mesma que
o farol do Fusion já usa com sucesso. Textura, malha, UV e os outros 182 sólidos
ficam idênticos.

Sem GUI: os quatro sólidos são recomprimidos em JDLZ (scripts/jdlz.py) e o
GEOMETRY.BIN é remontado no layout do CarToolkit (blocos 0x55441122 alinhados a 128,
padding id 0). Os outros 182 blocos são copiados byte a byte.
"""
import hashlib, json, shutil, struct, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import jdlz

SRC = ROOT / 'work/carbon2018-stage-dynamic-lights'
SRC_SHA = '8158464702D4B7805844C60E392121ABF72356E41AC4AA905725578CEC2FB4EE'
import os
VARIANT = os.environ.get('LENS_VARIANT', 'brakelight')
DST = ROOT / ('work/carbon2018-stage-glass-lens' if VARIANT == 'glass' else 'work/carbon2018-stage-brakelight-lens')
PARTS = {f'MUSTANGGT_KIT00_RIGHT_BRAKELIGHT_{l}' for l in 'ABCD'}

def bin_hash(s):
    h = 0xFFFFFFFF
    for ch in s.encode():
        h = (h * 33 + ch) & 0xFFFFFFFF
    return h

DULL = bin_hash('DULLPLASTIC')
GLASS = bin_hash('BRAKELIGHTGLASS') if VARIANT == 'glass' else bin_hash('BRAKELIGHT')
FLAGS = 0x14180 if VARIANT == 'glass' else 0x4180

def chunks(d, a, b):
    while a + 8 <= b:
        k, s = struct.unpack_from('<II', d, a)
        yield k, a + 8, a + 8 + s
        a += 8 + s

def find(d, kind):
    def rec(a, b):
        for k, s, e in chunks(d, a, b):
            if k == kind:
                return s, e
            if k & 0x80000000:
                r = rec(s, e)
                if r: return r
    return rec(0, len(d))

def aligned(d, kind):
    a, b = find(d, kind)
    return (a + 15) & ~15, b

def patch(solid):
    d = bytearray(solid)
    a, b = find(d, 0x134013)
    lm = list(struct.unpack_from('<%dI' % ((b - a) // 4), d, a))
    assert lm[2] == DULL and len(lm) == 4, lm
    struct.pack_into('<I', d, a + 8, GLASS)
    g, end = aligned(d, 0x134B02)
    assert end - g == 288
    assert struct.unpack_from('<I', d, g + 144 + 56)[0] == 0x4180
    struct.pack_into('<I', d, g + 144 + 56, FLAGS)
    return bytes(d)

def pad(out):
    g = (-len(out)) % 128
    if g < 8: g += 128
    out += struct.pack('<II', 0, g - 8) + b'\0' * (g - 8)

def main():
    geo = (SRC / 'GEOMETRY.BIN').read_bytes()
    assert hashlib.sha256(geo).hexdigest().upper() == SRC_SHA
    audit = {a['hash']: a['name'] for a in json.loads((ROOT / 'docs/carbon2018-stage-dynamic-lights-audit.json').read_text())}
    ta, tb = find(geo, 0x134004)
    entries = [list(struct.unpack_from('<6I', geo, p)) for p in range(ta, tb, 24)]
    assert len(entries) == 186
    first = min(e[1] for e in entries)
    out = bytearray(geo[:first])
    changes, blocks = [], []
    for e in entries:
        h, off, packed, unpacked = e[:4]
        block = geo[off:off + packed]
        name = audit['%08X' % h]
        if name in PARTS:
            solid = jdlz.decompress(block[24:])
            new = patch(solid)
            comp = jdlz.compress(new)
            assert jdlz.decompress(comp) == new
            block = struct.pack('<6I', 0x55441122, len(new), len(comp) + 24, 0, 0, 0) + comp
            changes.append({'part': name, 'hash': '%08X' % h, 'light_material': 'DULLPLASTIC -> ' + ('BRAKELIGHTGLASS' if VARIANT == 'glass' else 'BRAKELIGHT'),
                            'material_1_flags': '0x4180 -> 0x%X' % FLAGS,
                            'solid_before_sha256': hashlib.sha256(solid).hexdigest().upper(),
                            'solid_after_sha256': hashlib.sha256(new).hexdigest().upper()})
        blocks.append((e, block))
    assert len(changes) == 4
    for i, (e, block) in enumerate(blocks):
        assert len(out) % 128 == 0
        e[1], e[2] = len(out), len(block)
        out += block
        pad(out)
    for i, (e, _) in enumerate(blocks):
        struct.pack_into('<6I', out, ta + i * 24, *e)
    struct.pack_into('<I', out, 4, len(out) - 8)
    DST.mkdir(exist_ok=True)
    (DST / 'GEOMETRY.BIN').write_bytes(out)
    shutil.copyfile(SRC / 'TEXTURES.BIN', DST / 'TEXTURES.BIN')

    # Verificação independente: reler o arquivo gravado.
    d = (DST / 'GEOMETRY.BIN').read_bytes()
    ta2, tb2 = find(d, 0x134004)
    assert (ta2, tb2) == (ta, tb) and d[:4] == geo[:4] and d[8:ta] == geo[8:ta] and d[tb:first] == geo[tb:first]
    orig = {struct.unpack_from('<I', geo, p)[0]: struct.unpack_from('<6I', geo, p) for p in range(ta, tb, 24)}
    same = 0
    for p in range(ta2, tb2, 24):
        h, off, packed, unpacked, fl, z = struct.unpack_from('<6I', d, p)
        o = orig[h]
        assert (unpacked, fl, z) == (o[3], o[4], o[5]) and off % 128 == 0
        blk = d[off:off + packed]
        if audit['%08X' % h] in PARTS:
            sol = jdlz.decompress(blk[24:])
            ref = jdlz.decompress(geo[o[1]:o[1] + o[2]][24:])
            diff = [i for i in range(len(sol)) if sol[i] != ref[i]]
            assert len(sol) == len(ref) and len(diff) <= 8, diff
        else:
            assert blk == geo[o[1]:o[1] + o[2]]
            same += 1
    assert same == 182 and len(d) % 128 == 0 and struct.unpack_from('<I', d, 4)[0] == len(d) - 8
    files = [{'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size,
              'sha256': hashlib.sha256(p.read_bytes()).hexdigest().upper()} for p in (DST / 'GEOMETRY.BIN', DST / 'TEXTURES.BIN')]
    report = {'passed': True, 'solids': 186, 'changed_solids': 4, 'unchanged_blocks_bytewise': same,
              'textures_unchanged': True, 'base': 'work/carbon2018-stage-dynamic-lights (' + SRC_SHA + ')',
              'changes': changes, 'files': files,
              'method': 'JDLZ recompress (scripts/jdlz.py) + CarToolkit-compatible layout; no GUI',
              'status': 'rear lens glass material test; game QA pending'}
    (ROOT / ('docs/carbon2018-stage-glass-lens-verification.json' if VARIANT == 'glass' else 'docs/carbon2018-stage-brakelight-lens-verification.json')).write_text(json.dumps(report, indent=2) + '\n')
    print('PASS', files[0]['sha256'], len(d), 'bytes;', same, 'blocks identical; 4 lens solids patched')

if __name__ == '__main__':
    main()
