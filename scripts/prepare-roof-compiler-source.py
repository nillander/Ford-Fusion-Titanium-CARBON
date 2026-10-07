"""Prepare a full nfscgc source with native KIT00_ROOF and ROOF_SCOOP.

The approved car is not modified. The roof uses the existing tiny hidden
placeholder shape; its attachment follows the official replaced Mustang part.
"""
import json
import importlib.util
import math
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    src = ROOT / 'work/carbon2018-source-axes'
    dst = ROOT / 'work/carbon2018-source-roof'
    shutil.copytree(src, dst, dirs_exist_ok=True)
    # Same surface estimate used by the approved spoiler adjustment workflow.
    spec = importlib.util.spec_from_file_location('roof', ROOT / 'scripts/prepare-spoiler-roof.py')
    roof = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(roof)
    height, angle = roof.fusion_roof()
    position = [roof.ROOF_X, 0.0, round(height - 0.01, 5)]
    text = (src / 'mpoints.txt').read_text().replace('# eof', '')
    parts = []
    for i, lod in enumerate('ABCD'):
        part = f'KIT00_ROOF_{lod}'
        template = (src / f'KIT00_SPOILER_{lod}.obj').read_text()
        # These are actual compiler geometry parts, not appended binary clones.
        (dst / f'{part}.obj').write_text(template.replace(f'KIT00_SPOILER_{lod}', part), encoding='ascii')
        mount = f'_ROOF_SCOOP{i:02d}'
        x, y, z = -position[1], position[0], position[2]
        e = 0.001
        (dst / f'ROOF_SCOOP{i:02d}.obj').write_text(
            f'g {mount}\nv {x-e} {y-e} {z}\nv {x+e} {y-e} {z}\nv {x} {y+e} {z}\n'
            'vt 0 0\nvt 1 0\nvt 0.5 1\nvn 0 0 1\nf 1/1/1 2/2/1 3/3/1\n', encoding='ascii')
        text += f'{mount}\t\t0.0 0.0 0.0\t\t%_{part}\n'
        parts.append('MUSTANGGT_' + part)
    (dst / 'mpoints.txt').write_text(text + '# eof\n', encoding='ascii')
    # nfscgc reads these auxiliary files from its executable working directory.
    compiler = ROOT / 'work/carbon-compiler'
    backup = compiler / 'before-roof'
    backup.mkdir(exist_ok=True)
    for name in ('mpoints.txt', 'link.txt', 'matlist.txt', 'geometry.bin'):
        if (compiler / name).exists() and not (backup / name).exists():
            shutil.copy2(compiler / name, backup / name)
        if name != 'geometry.bin':
            shutil.copy2(dst / name, compiler / name)
    report = {'source': dst.relative_to(ROOT).as_posix(), 'new_parts': parts,
              'position': position, 'tilt_degrees': math.degrees(angle),
              'donor': 'MUSTANGGT_KIT00_ROOF_A..D', 'existing_parts': 186,
              'expected_parts': 190, 'status': 'compiler input; not installable'}
    (ROOT / 'docs/carbon2018-roof-compiler-plan.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
