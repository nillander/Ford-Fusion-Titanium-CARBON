"""Independent reader gates for the exhaust-marker and frontend-logo candidates."""
import hashlib
import importlib.util
import json
import struct
import subprocess
from pathlib import Path

import jdlz
from dump_position_markers import names_table

ROOT = Path(__file__).resolve().parents[1]


def main():
    spec = importlib.util.spec_from_file_location('roof', ROOT / 'scripts/consolidate-roof-compile.py')
    roof = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(roof)
    original = (ROOT / 'work/carbon2018-stage-roof/GEOMETRY.BIN').read_bytes()
    candidate = (ROOT / 'work/carbon2018-stage-exhaust/GEOMETRY.BIN').read_bytes()
    old = {e[0]: roof.decode(original,e) for e in roof.entries(original)[1]}
    new = {e[0]: roof.decode(candidate,e) for e in roof.entries(candidate)[1]}
    assert old.keys() == new.keys() and len(new) == 190
    names = names_table(str(ROOT / 'work/carbon-compiler/mp.txt'))
    gate = json.loads((ROOT / 'docs/carbon2018-stage-exhaust-verification.json').read_text())
    changes = 0
    for key, data in new.items():
        expected = bytearray(old[key])
        if roof.sr.find(expected,0x13401A):
            for p in roof.sr.marker_records(expected):
                if names.get(struct.unpack_from('<I',expected,p)[0]) == 'EXHAUST':
                    struct.pack_into('<f',expected,p+72,gate['marker_z'])
                    changes += 1
        assert data == expected
        assert (ROOT / f'work/carbon2018-exhaust-solids/{key:08X}.bin').read_bytes() == data
    assert changes == 60
    logo_gate = json.loads((ROOT / 'docs/carbon2018-frontend-logo-verification.json').read_text())
    before = (ROOT / 'work/frontend-before-logo-2018/FRONTB1.BUN').read_bytes()
    after = (ROOT / 'work/frontend2018-logo/FRONTB1.BUN').read_bytes()
    a,b = logo_gate['only_changed_bun_range']
    assert len(before) == len(after) and after[:a] == before[:a] and after[b:] == before[b:]
    packed = (ROOT / 'work/frontend2018-logo/FrontB1.lzc').read_bytes()
    assert jdlz.normalize_for_game(packed,repair=False) == packed and jdlz.decompress(packed) == after
    for report in (gate,logo_gate):
        for file in report['files']:
            assert hashlib.sha256((ROOT / file['path']).read_bytes()).hexdigest().upper() == file['sha256']
    audits = [
        ('scripts/validate-carbon-solids.ps1', ['-InputRoot','work/carbon2018-exhaust-solids'],
         'docs/carbon2018-stage-exhaust-audit.json', 'docs/carbon2018-stage-exhaust-verification.json', gate),
        ('scripts/validate-carbon-textures.ps1', ['-InputFile','work/frontend2018-logo/FRONTB1.BUN','-MaxNameLength','100','-AllowArgb8888'],
         'docs/carbon2018-frontend-logo-texture-audit.json', 'docs/carbon2018-frontend-logo-verification.json', logo_gate)]
    for script,args,audit,path,report in audits:
        subprocess.run(['pwsh','-NoProfile','-File',script,*args,'-OutputFile',audit],cwd=ROOT,check=True)
        report['passed'] = True
        report['independent_audit'] = {'passed':True,'file':audit}
        (ROOT / path).write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: 60 EXHAUST translations only; one frontend pixel range only; independent readers passed.')


if __name__ == '__main__':
    main()
