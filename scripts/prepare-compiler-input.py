"""Gera a entrada do nfscgc (ModTools 1.1) a partir de work/carbon2018-source,
compensando a orientação do compilador e adicionando pontos de montagem.

Achado (07/10): o nfscgc grava (x', y') = (y, -x) — espera a frente do carro em +Y
e o lado esquerdo em -X. A primeira compilação saiu girada 90° (Carbon: X frente,
Y esquerda, Z cima). Aqui os OBJ são pré-girados com (x, y, z) -> (-y, x, z),
em posições e normais, para que a saída fique no sistema Carbon. Rotação pura:
não espelha, não altera ordem dos vértices nem enrolamento das faces.

Pontos de montagem: posições do GEOMETRY.BIN MW v2.8 (docs/mw2018-markers.json),
lados normalizados para a convenção Carbon (LEFT = +Y, como no MUSTANGGT oficial),
anexos às mesmas peças do doador oficial (docs/mustanggt-stock-markers.json),
rotações conforme o exemplo do autor (bugatti_source/geometry/mpoints.txt).
Cada ponto vira um OBJ mínimo (triângulo de 2 mm centrado na posição).

Uso: python scripts/prepare-compiler-input.py [origem] [destino]
"""
import json, re, shutil, sys
from pathlib import Path

SRC = Path(sys.argv[1] if len(sys.argv) > 1 else 'work/carbon2018-source')
DST = Path(sys.argv[2] if len(sys.argv) > 2 else 'work/carbon2018-source-axes')
MW = json.load(open('docs/mw2018-markers.json'))
STOCK = json.load(open('docs/mustanggt-stock-markers.json'))

def to_compiler(x, y, z):
    return -y, x, z

def rotate_obj(src, dst):
    with open(src, encoding='ascii') as f, open(dst, 'w', encoding='ascii', newline='\n') as out:
        for line in f:
            if line.startswith('v ') or line.startswith('vn '):
                tag, a, b, c = line.split()
                x, y, z = to_compiler(float(a), float(b), float(c))
                out.write(f'{tag} {x:.9g} {y:.9g} {z:.9g}\n')
            else:
                out.write(line)

# Rotações (graus x y z) do exemplo do autor para o mesmo compilador.
ROT = {'HEADLIGHT': (0, 90, 0), 'BRAKELIGHT': (0, -90, 0), 'REVERSE': (0, -90, 0),
       'EXHAUST': (0, -90, 0), 'LICENSEPLATE': (0, -80, 0), 'SPOILER': (0, 0, 0),
       'SPOILER2': (0, 0, 0), 'FRONT_BRAKE': (0, 0, 0), 'ROOF_SCOOP': (0, 0, 0)}

def rot_for(name):
    for k in ('HEADLIGHT', 'BRAKELIGHT', 'REVERSE', 'EXHAUST', 'LICENSEPLATE', 'SPOILER2', 'FRONT_BRAKE'):
        if k in name: return ROT[k]
    return ROT.get(name, (0, 0, 0))

def side(name, y):
    base = re.sub(r'^(LEFT|RIGHT)_', '', name)
    if base == name: return name
    return ('LEFT_' if y > 0 else 'RIGHT_') + base

def main():
    if DST.exists(): shutil.rmtree(DST)
    DST.mkdir(parents=True)
    parts = []
    for p in sorted(SRC.iterdir()):
        if p.suffix.lower() == '.obj':
            rotate_obj(p, DST / p.name); parts.append(p.stem)
        elif p.is_dir():
            shutil.copytree(p, DST / p.name)
        elif p.name not in ('mpoints.txt',):
            shutil.copy2(p, DST / p.name)
    have = set(parts)
    mw = MW['MUSTANGGT_BASE_A']
    pts = {}
    for m in mw:
        n = side(m['name'], m['position'][1])
        pts.setdefault(n, []).append(m['position'])
    # SPOILER2: mesmo deslocamento relativo ao SPOILER que no doador oficial.
    sb = {m['name']: m['position'] for m in STOCK['MUSTANGGT_BASE_A']}
    if 'SPOILER' in pts and 'SPOILER2' in sb and 'SPOILER' in sb:
        s = pts['SPOILER'][0]
        pts['SPOILER2'] = [[round(s[i] + sb['SPOILER2'][i] - sb['SPOILER'][i], 5) for i in range(3)]]
    exhaust = pts.pop('LEFT_EXHAUST', []) + pts.pop('RIGHT_EXHAUST', [])
    front_brake = [m['position'] for m in STOCK['MUSTANGGT_KIT00_FRONT_TIRE_A'] if m['name'] == 'FRONT_BRAKE']
    roof_scoop = pts.pop('ROOF_SCOOP', [])
    centre = pts.pop('CENTRE_BRAKELIGHT', [])
    # Anexos iguais aos do doador oficial, para as peças que existem no Fusion.
    plan = []  # (mount, posição, peça)
    lods = 'ABCDE'
    for n in ('LEFT_HEADLIGHT', 'RIGHT_HEADLIGHT', 'LEFT_BRAKELIGHT', 'RIGHT_BRAKELIGHT',
              'LEFT_REVERSE', 'RIGHT_REVERSE', 'SPOILER', 'SPOILER2'):
        for pos in pts.get(n, []):
            for l in lods:
                if f'BASE_{l}' in have: plan.append((n, pos, f'BASE_{l}'))
    for kit in sorted({re.sub(r'_[A-E]$', '', p) for p in have if re.fullmatch(r'KIT\d\d_BODY_[A-E]', p)}):
        for l in lods:
            part = f'{kit}_{l}'
            if part not in have: continue
            for pos in exhaust: plan.append(('EXHAUST', pos, part))
            for n in ('LEFT_REVERSE', 'RIGHT_REVERSE'):
                for pos in pts.get(n, []): plan.append((n, pos, part))
    for l in lods:
        if f'KIT00_FRONT_TIRE_{l}' in have:
            for pos in front_brake: plan.append(('FRONT_BRAKE', pos, f'KIT00_FRONT_TIRE_{l}'))
    lines = ['# mount point\t\t\trotations: x, y, z\tgeometry part name',
             '# Gerado por scripts/prepare-compiler-input.py; ver docs/MOUNT-POINTS-2018.md']
    count = {}
    report = []
    for n, pos, part in plan:
        i = count.get(n, 0); count[n] = i + 1
        mp = f'_{n}{i:02d}'
        obj = DST / f'{n}{i:02d}.obj'
        x, y, z = to_compiler(*pos); e = 0.001
        obj.write_text(f'g {n}{i:02d}\nv {x - e:.6f} {y - e:.6f} {z:.6f}\nv {x + e:.6f} {y - e:.6f} {z:.6f}\n'
                       f'v {x:.6f} {y + e:.6f} {z:.6f}\nf 1 2 3\n', encoding='ascii')
        rx, ry, rz = rot_for(n)
        lines.append(f'{mp}\t\t{rx:.1f} {ry:.1f} {rz:.1f}\t\t%_{part}')
        report.append({'mount': mp, 'marker': n, 'carbon_position': pos, 'part': part, 'rotation': [rx, ry, rz]})
    lines.append('# eof')
    (DST / 'mpoints.txt').write_text('\n'.join(lines) + '\n', encoding='ascii')
    skipped = {'CENTRE_BRAKELIGHT': centre, 'ROOF_SCOOP (Fusion não tem KIT00_ROOF)': roof_scoop,
               'LICENSEPLATE (MW sem marcador; Fusion sem REAR_BUMPER)': []}
    json.dump({'source': str(SRC), 'output': str(DST), 'axis_fix': '(x,y,z)->(-y,x,z)',
               'mounts': report, 'not_mapped': skipped}, open('docs/carbon2018-mountpoints.json', 'w'), indent=1)
    print(len(parts), 'OBJ girados;', len(report), 'pontos de montagem;', DST)

if __name__ == '__main__':
    main()
