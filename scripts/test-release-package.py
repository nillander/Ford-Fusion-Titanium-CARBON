"""Exercise the released installer in Windows PowerShell 5.1 on a mock game.

Validate ZIP hashes, install/reinstall/restore, and reject an unknown mod before
any game file changes. Keep the mock under work/ for inspection; never use game.
"""
import hashlib
import json
import shutil
import subprocess
import uuid
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PS = r'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest().upper()


def main():
    archive = ROOT / 'local/release-v1.3/Fusion2018_AWD_NFSC.zip'
    folder = ROOT / 'work' / ('release-v13-check-'+uuid.uuid4().hex)
    folder.mkdir()
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        z.extractall(folder)
    package = folder / 'Fusion2018_AWD_NFSC'
    for line in (package / 'SHA256SUMS.txt').read_text().splitlines():
        digest,path = line.split('  ',1)
        assert sha(package / path) == digest
    manifest = json.loads((package / 'arquivos.json').read_text())
    game = folder / 'game'
    game.mkdir()
    (game / 'NFSC.exe').write_bytes(b'mock; never execute')
    sources = {
        'CARS/MUSTANGGT/GEOMETRY.BIN': ROOT / 'reference/carbon-stock/MUSTANGGT/GEOMETRY.BIN',
        'CARS/MUSTANGGT/TEXTURES.BIN': ROOT / 'reference/carbon-stock/MUSTANGGT/TEXTURES.BIN',
        'GLOBAL/attributes.bin': ROOT / 'work/global-before-integration-2018/attributes.bin',
        **{'FRONTEND/'+name: ROOT / 'work/frontend-before-logo-2018' / name for name in ('FRONTB1.BUN','FrontB1.lzc')},
        **{'LANGUAGES/'+file['file']: ROOT / 'work/languages-before-integration-2018' / file['file']
           for file in json.loads((ROOT / 'docs/carbon2018-frontend-name-verification.json').read_text())['files']}}
    for name,source in sources.items():
        target = game / name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,target)
    original = {name:sha(game/name) for name in sources}
    def snapshot():
        return {name:sha(game/name) for name in sources}
    def run(action, success=True):
        result = subprocess.run([PS,'-NoProfile','-ExecutionPolicy','Bypass','-File',str(package/'instalar.ps1'),
                                 '-GamePath',str(game),'-Action',action],capture_output=True)
        assert (result.returncode == 0) == success, result.stdout.decode(errors='replace')+result.stderr.decode(errors='replace')
    # Unknown destination is refused before creating backups or copying any file.
    unknown = game / 'GLOBAL/attributes.bin'
    unknown.write_bytes(unknown.read_bytes()+b'other mod')
    before = snapshot()
    run('Install',False)
    assert snapshot() == before and not (game/'Fusion2018_v1.3_backup').exists()
    shutil.copyfile(sources['GLOBAL/attributes.bin'],unknown)
    run('Install')
    expected = {file['path']:file['sha256'] for file in manifest['files']}
    assert snapshot() == expected
    run('Install')
    assert snapshot() == expected
    run('Restore')
    assert snapshot() == original
    # Corrupt archive asset is also refused with no destination changes.
    target = package/'CARS/MUSTANGGT/TEXTURES.BIN'
    asset = target.read_bytes()
    target.write_bytes(asset+b'corrupt')
    run('Install',False)
    assert snapshot() == original
    target.write_bytes(asset)
    # Upgrade from the published v1.2 must restore that exact prior installation.
    game = folder / 'game-upgrade'
    game.mkdir()
    (game / 'NFSC.exe').write_bytes(b'mock; never execute')
    with zipfile.ZipFile(ROOT/'local/release-v1.2/Fusion2018_AWD_NFSC.zip') as old:
        for name in sources:
            destination = game/name
            destination.parent.mkdir(parents=True,exist_ok=True)
            destination.write_bytes(old.read('Fusion2018_AWD_NFSC/'+name))
    old_backup = game/'Fusion2018_v1.2_backup'
    old_backup.mkdir()
    (old_backup/'preservar.txt').write_bytes(b'previous backup sentinel')
    previous = snapshot()
    run('Install')
    assert snapshot() == expected
    run('Restore')
    assert snapshot() == previous
    assert (old_backup/'preservar.txt').read_bytes() == b'previous backup sentinel'
    report = {'passed':True,'archive_sha256':sha(archive),'files_checked':len(expected),
              'upgrade_v1_2_restore_passed':True,'previous_backup_preserved':True,
              'windows_powershell_5_1':True,'zip_checksums_passed':True,
              'install_reinstall_restore_passed':True,'unknown_mod_preflight_no_changes':True,
              'corrupt_package_preflight_no_changes':True,'mock_directory':str(folder)}
    (ROOT/'docs/release-v1.3-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: ZIP hashes; 22 files; Windows PowerShell install/reinstall/restore; unknown/corrupt preflight.')


if __name__ == '__main__':
    main()
