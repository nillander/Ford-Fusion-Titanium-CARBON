"""Replace only official Carbon MUSTANGGT secondary-logo pixels with Fusion art.

Preserve the Carbon texture header/hash/format and all other FRONTB1 resources.
Convert the existing MW v2.8 DXT3 logo to the donor's ARGB8888 pixel encoding.
Requires Pillow; does not change the game installation.
"""
import hashlib
import io
import json
import shutil
import struct
from pathlib import Path

from PIL import Image
import jdlz

ROOT = Path(__file__).resolve().parents[1]
GAME = Path('D:/Program Files (x86)/Electronic Arts/Need for Speed Carbon')


def sha(data):
    return hashlib.sha256(data).hexdigest().upper()


def chunks(data, a=0, b=None):
    b = len(data) if b is None else b
    while a+8 <= b:
        kind, size = struct.unpack_from('<II', data, a)
        assert a+8+size <= b
        yield kind, a+8, a+8+size
        if kind & 0x80000000:
            yield from chunks(data, a+8, a+8+size)
        a += 8+size
    assert a == b


def first(data, kind):
    return next((a,b) for k,a,b in chunks(data) if k == kind)


def main():
    backup = ROOT / 'work/frontend-before-logo-2018'
    dst = ROOT / 'work/frontend2018-logo'
    backup.mkdir(exist_ok=True)
    dst.mkdir(exist_ok=True)
    for name in ('FRONTB1.BUN','FrontB1.lzc'):
        if not (backup / name).exists():
            shutil.copyfile(GAME / 'FRONTEND' / name, backup / name)
    original = (backup / 'FRONTB1.BUN').read_bytes()
    assert jdlz.decompress((backup / 'FrontB1.lzc').read_bytes()) == original
    headers, end = first(original, 0x33310004)
    p, index = headers, 0
    target = None
    while p < end:
        length = original[p+88]
        name = original[p+89:p+89+length].rstrip(b'\0').decode('ascii')
        if name == 'SECONDARY_LOGO_MUSTANGGT':
            assert target is None
            target = (p,index)
        p += 89+length
        index += 1
    assert p == end and index == 264 and target
    p, index = target
    target_hash, _, placement, _, size = struct.unpack_from('<5I', original, p+12)
    width, height = struct.unpack_from('<2H', original, p+40)
    dds, _ = first(original, 0x33310005)
    assert struct.unpack_from('<I', original, dds+index*24+12)[0] == 21
    assert (width,height,size,original[p+50]) == (256,64,65536,1)
    source = next((ROOT / 'reference/mw-v28/Fusion2018_AWD_MW2005').rglob('SECONDARYLOGO.BIN'))
    mw = source.read_bytes()
    header, _ = first(mw, 0x33310004)
    offset = struct.unpack_from('<I', mw, header+48)[0]
    mw_size = struct.unpack_from('<I', mw, header+56)[0]
    assert struct.unpack_from('<2H', mw, header+68) == (width,height)
    a, _ = first(mw, 0x33320002)
    mw_base = (a+127)//128*128
    pixels = mw[mw_base+offset:mw_base+offset+mw_size]
    assert len(pixels) == 16384
    dds_header = bytearray(128)
    dds_header[:4] = b'DDS '
    struct.pack_into('<7I',dds_header,4,124,0x81007,height,width,len(pixels),0,1)
    struct.pack_into('<II4s',dds_header,76,32,4,b'DXT3')
    struct.pack_into('<I',dds_header,108,0x1000)
    image = Image.open(io.BytesIO(dds_header+pixels)).convert('RGBA')
    converted = image.tobytes('raw','BGRA')
    a, b = first(original, 0x33320002)
    start = a+0x78+placement
    stop = start+size
    assert stop <= b and len(converted) == size
    result = original[:start]+converted+original[stop:]
    assert len(result) == len(original) and result[:start] == original[:start] and result[stop:] == original[stop:]
    (dst / 'FRONTB1.BUN').write_bytes(result)
    print('Compressing frontend...', flush=True)
    packed = jdlz.normalize_for_game(jdlz.compress(result), repair=False)
    assert jdlz.decompress(packed) == result
    (dst / 'FrontB1.lzc').write_bytes(packed)
    image.save(dst / 'Fusion-secondarylogo.png')
    report = {'passed': False, 'binary_scope_passed': True, 'texture': 'SECONDARY_LOGO_MUSTANGGT',
              'hash': f'{target_hash:08X}', 'dimensions': [width,height], 'format': 'ARGB8888 (21)',
              'source': source.relative_to(ROOT).as_posix(), 'source_sha256': sha(mw),
              'only_changed_bun_range': [start,stop], 'other_frontend_bytes_identical': True,
              'game_validation': 'pending',
              'files': [{'name':name,'path':(dst/name).relative_to(ROOT).as_posix(),
                         'sha256':sha((dst/name).read_bytes()),'backup_sha256':sha((backup/name).read_bytes())}
                        for name in ('FRONTB1.BUN','FrontB1.lzc')]}
    (ROOT / 'docs/carbon2018-frontend-logo-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Pixel scope passed; independent texture read still required.')


if __name__ == '__main__':
    main()
