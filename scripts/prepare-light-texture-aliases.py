"""Preserve source atlases and provide official full-name Carbon light states."""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main():
    source = ROOT/'work/carbon2018-source-axes/texture'
    target = ROOT/'work/carbon2018-texture-aliases'
    target.mkdir(exist_ok=True)
    originals = list(source.glob('*.dds'))
    assert len(originals) == 10
    for path in originals:
        shutil.copyfile(path, target/path.name)
    for family, short in [('HEADLIGHT','HEAD'),('BRAKELIGHT','BRAKE')]:
        atlas = source/f'MUSTANGGT_{short}_OFF.dds'
        assert atlas.exists()
        for state in ['OFF','ON','GLASS_OFF','GLASS_ON']:
            shutil.copyfile(atlas,target/f'MUSTANGGT_KIT00_{family}_{state}.dds')
    assert len(list(target.glob('*.dds'))) == 18
    print('Prepared 18 DDS; ON duplicates OFF for appearance testing only')

if __name__ == '__main__':main()
