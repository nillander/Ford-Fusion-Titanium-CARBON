"""Empacota a release do Fusion Carbon a partir dos BIN aprovados no jogo.

Uso: python scripts/package_release.py v1.2 local/release-v1.2
Confere os BIN contra os hashes aprovados e contra os instalados no jogo (se a
pasta do jogo estiver acessível), monta Fusion2018_AWD_NFSC.zip e os SHA256SUMS.
"""
import datetime, hashlib, json, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPROVED = {  # aparência/direção aprovada; potência BMW +20% por pedido posterior
    'GEOMETRY.BIN': ('work/carbon2018-stage-exhaust/GEOMETRY.BIN',
                     '4C8CFDF9CEAC10DB58278A2CCA0243C43F4E0A560239AFCA821D36A898E9F65C'),
    'TEXTURES.BIN': ('work/carbon2018-stage-exhaust/TEXTURES.BIN',
                     '8989A7E4502F92B2D2828E817AD8B7F3ACB0D46A4227B6275CA013EA3651E3AC'),
}
GAME = Path('D:/Program Files (x86)/Electronic Arts/Need for Speed Carbon')
DATE = (2026, 10, 7, 12, 0, 0)
PKG = 'Fusion2018_AWD_NFSC'

def sha(b): return hashlib.sha256(b).hexdigest().upper()

def main(version, outdir):
    out = ROOT / outdir; out.mkdir(parents=True, exist_ok=True)
    src = ROOT / 'release/pacote'
    files = {}
    manifest = []
    def add(path, source, digest, allowed):
        data = (ROOT / source).read_bytes()
        assert sha(data) == digest, path
        files[path] = data
        manifest.append({'path':path,'sha256':digest,'allowed_before':sorted(set(allowed))})
    for name, (path, digest) in APPROVED.items():
        allowed = [sha((ROOT / 'reference/carbon-stock/MUSTANGGT' / name).read_bytes())]
        for stage in ('carbon2018-stage-spoiler','carbon2018-stage-roof'):
            p = ROOT / 'work' / stage / name
            if p.exists(): allowed.append(sha(p.read_bytes()))
        add(f'CARS/MUSTANGGT/{name}',path,digest,allowed)
    performance = json.loads((ROOT / 'docs/carbon2018-performance-verification.json').read_text())
    assert not performance.get('racer_weight_comparison_checked'), 'Current staging is the post-v1.2 comparison; do not relabel it as v1.2.'
    assert performance['status'] == 'passed' and performance['rollback_semantically_identical']
    add('GLOBAL/attributes.bin','work/global2018-performance/main/attributes.bin',performance['attributes_sha256'],
        [performance[k] for k in ('backup_attributes_sha256','previous_candidate_attributes_sha256',
                                  'second_candidate_attributes_sha256','approved_handling_attributes_sha256')])
    logo = json.loads((ROOT / 'docs/carbon2018-frontend-logo-verification.json').read_text())
    assert logo['passed'] and logo['game_validation'].startswith('user confirmed')
    for file in logo['files']:
        add('FRONTEND/'+file['name'],file['path'],file['sha256'],[file['backup_sha256']])
    names = json.loads((ROOT / 'docs/carbon2018-frontend-name-verification.json').read_text())
    assert names['status'] == 'passed'
    for file in names['files']:
        add('LANGUAGES/'+file['file'],'work/languages2018-name/'+file['file'],file['after_sha256'],[file['before_sha256']])
    assert len(manifest) == 22
    for file in manifest:
        assert sha((GAME / file['path']).read_bytes()) == file['sha256'], 'Installed differs: '+file['path']
    content = json.dumps({'version':version,'files':manifest},indent=2)+'\n'
    (src / 'arquivos-v1.2.json').write_text(content)
    for p in (ROOT / 'release/vlt').glob('*'):
        if p.is_file(): files['VLT/'+p.name] = p.read_bytes()
    for p in sorted(src.rglob('*')):
        if p.is_file():
            rel = p.relative_to(src).as_posix()
            if p.name.startswith('NOTAS-') and p.name != f'NOTAS-{version}.md': continue
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
