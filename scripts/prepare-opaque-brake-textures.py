"""Prepare a reversible DXT1 comparison, preserving brake atlas RGB exactly."""
import shutil
import struct
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]

def main():
    source = ROOT / 'work/carbon2018-texture-aliases'
    target = ROOT / 'work/carbon2018-opaque-brake-textures'
    target.mkdir(exist_ok=True)
    changed = []
    for path in source.glob('*.dds'):
        destination = target / path.name
        if 'BRAKE' not in path.stem:
            shutil.copyfile(path, destination)
            continue
        raw = path.read_bytes()
        assert raw[:4] == b'DDS ' and raw[84:88] == b'DXT3'
        assert struct.unpack_from('<I', raw, 28)[0] in (0, 1)
        header = bytearray(raw[:128])
        header[84:88] = b'DXT1'
        struct.pack_into('<I', header, 20, (len(raw)-128)//2)
        blocks = bytearray()
        for offset in range(128, len(raw), 16):
            a, b, indices = struct.unpack_from('<HHI', raw, offset+8)
            if a < b:
                a, b = b, a
                indices ^= 0x55555555
            elif a == b:
                indices = 0
            blocks.extend(struct.pack('<HHI', a, b, indices))
        destination.write_bytes(header+blocks)
        before = np.asarray(Image.open(path).convert('RGB'))
        after = np.asarray(Image.open(destination).convert('RGB'))
        assert np.array_equal(before, after), path.name
        changed.append(path.name)
    assert len(changed) == 5
    print('PASS: 5 brake atlases converted to DXT1; every RGB pixel unchanged')

if __name__ == '__main__':
    main()
