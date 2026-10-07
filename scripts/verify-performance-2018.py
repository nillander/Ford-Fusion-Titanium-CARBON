"""Audit all unpacked VLT nodes against the planned changes and rollback."""
import hashlib
import json
import struct
from pathlib import Path

import yaml


def normalized(value):
    if isinstance(value, float):
        return struct.unpack('<f', struct.pack('<f', value))[0]
    if isinstance(value, list):
        return [normalized(item) for item in value]
    if isinstance(value, dict):
        return {key: normalized(item) for key, item in value.items()}
    return value


def database(path):
    nodes = {}
    blobs = {}
    for file in path.rglob('*'):
        if not file.is_file() or file.name == 'info.yml':
            continue
        relative = file.relative_to(path).as_posix()
        if file.suffix == '.yml':
            for row in yaml.safe_load(file.read_text(encoding='utf-8')):
                key = (relative, str(row['Name']))
                assert key not in nodes, key
                nodes[key] = normalized(row)
        else:
            blobs[relative] = hashlib.sha256(file.read_bytes()).hexdigest()
    return nodes, blobs


def main():
    baseline, blobs = database(Path('work/vlt-baseline-yaml'))
    candidate, candidate_blobs = database(Path('work/vlt-performance-yaml'))
    rollback, rollback_blobs = database(Path('work/vlt-rollback-yaml'))
    upgrade_path = Path('work/vlt-performance-upgrade-check-yaml')
    upgrade_checked = False
    if upgrade_path.exists():
        upgraded, upgraded_blobs = database(upgrade_path)
        assert upgraded == candidate and upgraded_blobs == candidate_blobs, 'Import over previous candidate differs'
        upgrade_checked = True
    assert baseline.keys() == candidate.keys() == rollback.keys(), 'Node set changed'
    assert blobs == candidate_blobs == rollback_blobs, 'Blob content changed'
    plan = json.loads(Path('docs/carbon2018-performance-plan.json').read_text(encoding='utf-8'))
    expected = {}
    for change in plan['changes']:
        key = (f"main/attributes/db/{change['class']}.yml", change['node'])
        expected.setdefault(key, {})[change['field']] = normalized(change['after'])
    differences = []
    for key, original in baseline.items():
        assert rollback[key] == original, f'Rollback changed {key}'
        approved = normalized(original)
        approved['Data'] = dict(original['Data'], **expected.get(key, {}))
        assert candidate[key] == approved, f'Unexpected change or missing planned value: {key}'
        if candidate[key] != original:
            differences.append({'file': key[0], 'node': key[1], 'fields': list(expected[key])})
    fe = candidate[('main/fe_attrib/frontend/frontend.yml', 'mustanggt')]['Data']
    assert fe['Cost'] == 50000 and fe['manufacturer'] == 2 and fe['UnlockedAt'] == 11
    bmw = baseline[('main/attributes/db/engine.yml','bmwm3gtre46')]['Data']
    for node in ('mustanggt','mustanggt_top'):
        engine = candidate[('main/attributes/db/engine.yml',node)]['Data']
        assert engine['TORQUE']['Data'] == [normalized(v*1.2) for v in bmw['TORQUE']['Data']]
        assert engine['MAX_RPM'] == bmw['MAX_RPM'] and engine['RED_LINE'] == bmw['RED_LINE']
    racer = plan.get('racer_weight_comparison', {})
    if racer.get('enabled'):
        pv = candidate[('main/attributes/db/pvehicle.yml','mustanggt')]['Data']
        ref_pv = baseline[('main/attributes/db/pvehicle.yml','bmwm3gtre46')]['Data']
        assert pv['MASS'] == ref_pv['MASS'] == 1100
        assert pv['TENSOR_SCALE'] == ref_pv['TENSOR_SCALE']
        ref_transmission = baseline[('main/attributes/db/transmission.yml','bmwm3gtre46')]['Data']
        for node in ('mustanggt','mustanggt_top'):
            transmission = candidate[('main/attributes/db/transmission.yml',node)]['Data']
            assert transmission['FINAL_GEAR'] == ref_transmission['FINAL_GEAR']
            assert transmission['TORQUE_SPLIT'] == 0.5
            assert candidate[('main/attributes/db/engine.yml',node)]['Data']['FLYWHEEL_MASS'] == bmw['FLYWHEEL_MASS']
    previous_release = Path('work/global2018-performance-v1.2/main/attributes.bin')
    release_hash = None
    if previous_release.exists():
        release_hash = hashlib.sha256(previous_release.read_bytes()).hexdigest().upper()
        release_gate = json.loads(Path('docs/carbon2018-performance-v1.2-verification.json').read_text())
        assert release_hash == release_gate['attributes_sha256'] and release_gate['status'] == 'passed'
    lightweight = Path('work/global2018-performance-lightweight/main/attributes.bin')
    lightweight_hash = None
    if lightweight.exists():
        lightweight_hash = hashlib.sha256(lightweight.read_bytes()).hexdigest().upper()
        lightweight_gate = json.loads(Path('docs/carbon2018-performance-lightweight-verification.json').read_text())
        assert lightweight_hash == lightweight_gate['attributes_sha256'] and lightweight_gate['status'] == 'passed'
    if plan.get('racing_class_override'):
        pv = candidate[('main/attributes/db/pvehicle.yml','mustanggt')]
        assert pv['ParentName'] == 'muscle'
        assert pv['Data']['RacingClass'] == 'kRaceCar_Class'+plan['racing_class_override']
        assert 'RacingClass' not in rollback[('main/attributes/db/pvehicle.yml','mustanggt')]['Data']
    first_candidate = Path('work/global2018-performance-first/main/attributes.bin')
    previous_hash = None
    if first_candidate.exists():
        previous_hash = hashlib.sha256(first_candidate.read_bytes()).hexdigest().upper()
        first_gate = json.loads(Path('docs/carbon2018-performance-first-verification.json').read_text(encoding='utf-8'))
        assert previous_hash == first_gate['attributes_sha256'] and first_gate['status'] == 'passed'
    second_candidate = Path('work/global2018-performance-second/main/attributes.bin')
    second_hash = None
    if second_candidate.exists():
        second_hash = hashlib.sha256(second_candidate.read_bytes()).hexdigest().upper()
        second_gate = json.loads(Path('docs/carbon2018-performance-second-verification.json').read_text())
        assert second_hash == second_gate['attributes_sha256'] and second_gate['status'] == 'passed'
    report = {
        'status': 'passed', 'nodes_checked': len(baseline), 'blobs_checked': len(blobs),
        'changed_nodes': differences, 'rollback_semantically_identical': True,
        'frontend': {'Cost': 50000, 'manufacturer': 2, 'UnlockedAt': 11},
        'camaro_camaron_other_nodes_unchanged': True,
        'game_validation': 'pending',
        'power_reference_checked': 'bmwm3gtre46 torque x1.20; same MAX_RPM/RED_LINE; base/top',
        'approved_handling_attributes_sha256': '547C601A5517A487AA02ED6F45D0AB9B2CA7FC3CB085D090A3AC270F858B7C06',
        'import_over_previous_candidate_semantically_identical': upgrade_checked,
        'import_comparison_source': 'v1.2' if racer.get('enabled') else 'second candidate',
        'attributes_sha256': hashlib.sha256(Path('work/global2018-performance/main/attributes.bin').read_bytes()).hexdigest().upper(),
        'previous_release_attributes_sha256': release_hash,
        'previous_lightweight_attributes_sha256': lightweight_hash,
        'racing_class_override': plan.get('racing_class_override'),
        'racer_weight_comparison_checked': bool(racer.get('enabled')),
        'backup_attributes_sha256': hashlib.sha256(Path('work/global-before-integration-2018/attributes.bin').read_bytes()).hexdigest().upper(),
        'previous_candidate_attributes_sha256': previous_hash,
        'second_candidate_attributes_sha256': second_hash,
    }
    Path('docs/carbon2018-performance-verification.json').write_text(json.dumps(report, indent=2)+'\n')
    print(f"PASS: {len(baseline)} nodes, {len(blobs)} blobs; {len(differences)} scoped nodes changed; rollback exact.")


if __name__ == '__main__':
    main()
