"""Empacota a release do Fusion Carbon a partir dos BIN aprovados no jogo.

Uso: python scripts/package_release.py v1.0 local/release-v1.0
Confere os BIN contra os hashes aprovados e contra os instalados no jogo (se a
pasta do jogo estiver acessível), monta Fusion2018_AWD_NFSC.zip e os SHA256SUMS.
"""
import datetime, hashlib, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPROVED = {  # aprovados pelo usuário no jogo em 07/10/2026 11:51
    'GEOMETRY.BIN': ('work/carbon2018-stage-spoiler/GEOMETRY.BIN',
                     'AE4BB255576689D0668AAB54B677F8D3393AE74C5A15700AB2176FDC89B647B2'),
    'TEXTURES.BIN': ('work/carbon2018-stage-spoiler/TEXTURES.BIN',
                     '8989A7E4502F92B2D2828E817AD8B7F3ACB0D46A4227B6275CA013EA3651E3AC'),
}
GAME = Path.home() / 'mnt/Need for Speed Carbon/CARS/MUSTANGGT'
DATE = (2026, 10, 7, 12, 0, 0)
PKG = 'Fusion2018_AWD_NFSC'

def sha(b): return hashlib.sha256(b).hexdigest().upper()

def main(version, outdir):
    out = ROOT / outdir; out.mkdir(parents=True, exist_ok=True)
    src = ROOT / 'release/pacote'
    files = {}
    for name, (path, digest) in APPROVED.items():
        data = (ROOT / path).read_bytes()
        assert sha(data) == digest, (name, sha(data))
        if (GAME / name).exists():
            assert sha((GAME / name).read_bytes()) == digest, f'{name} instalado difere do aprovado'
        files[f'CARS/MUSTANGGT/{name}'] = data
    for p in sorted(src.rglob('*')):
        if p.is_file():
            rel = p.relative_to(src).as_posix()
            data = p.read_bytes()
            if p.suffix.lower() == '.bat':
                data = data.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')
            files[rel] = data
    assert f'NOTAS-{version}.md' in files and 'instalar.bat' in files
    sums = ''.join(f'{sha(d)}  {n}\n' for n, d in sorted(files.items()) if n != 'SHA256SUMS.txt')
    files['SHA256SUMS.txt'] = sums.encode()
    zpath = out / f'{PKG}.zip'
    with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        dirs = sorted({'/'.join(n.split('/')[:i]) for n in files for i in range(1, n.count('/') + 1)})
        for d in [''] + dirs:
            zi = zipfile.ZipInfo(f'{PKG}/{d}/'.replace('//', '/'), DATE); zi.external_attr = 0o40755 << 16 | 0x10
            z.writestr(zi, b'')
        for n, d in sorted(files.items()):
            zi = zipfile.ZipInfo(f'{PKG}/{n}', DATE); zi.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(zi, d)
    with zipfile.ZipFile(zpath) as z:
        assert z.testzip() is None
        for n, d in files.items():
            assert z.read(f'{PKG}/{n}') == d
    (out / 'SHA256SUMS.txt').write_text(f'{sha(zpath.read_bytes())}  {zpath.name}\n', encoding='ascii')
    (out / 'SHA256SUMS-conteudo.txt').write_text(
        ''.join(f'{sha(d)}  {PKG}/{n}\n' for n, d in sorted(files.items())), encoding='ascii')
    print(zpath, zpath.stat().st_size, 'bytes', sha(zpath.read_bytes()))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
