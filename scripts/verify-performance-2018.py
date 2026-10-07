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
    first_candidate = Path('work/global2018-performance-first/main/attributes.bin')
    previous_hash = None
    if first_candidate.exists():
        previous_hash = hashlib.sha256(first_candidate.read_bytes()).hexdigest().upper()
        first_gate = json.loads(Path('docs/carbon2018-performance-first-verification.json').read_text(encoding='utf-8'))
        assert previous_hash == first_gate['attributes_sha256'] and first_gate['status'] == 'passed'
    report = {
        'status': 'passed', 'nodes_checked': len(baseline), 'blobs_checked': len(blobs),
        'changed_nodes': differences, 'rollback_semantically_identical': True,
        'frontend': {'Cost': 50000, 'manufacturer': 2, 'UnlockedAt': 11},
        'camaro_camaron_other_nodes_unchanged': True,
        'game_validation': 'pending',
        'attributes_sha256': hashlib.sha256(Path('work/global2018-performance/main/attributes.bin').read_bytes()).hexdigest().upper(),
        'backup_attributes_sha256': hashlib.sha256(Path('work/global-before-integration-2018/attributes.bin').read_bytes()).hexdigest().upper(),
        'previous_candidate_attributes_sha256': previous_hash,
    }
    Path('docs/carbon2018-performance-verification.json').write_text(json.dumps(report, indent=2)+'\n')
    print(f"PASS: {len(baseline)} nodes, {len(blobs)} blobs; {len(differences)} scoped nodes changed; rollback exact.")


if __name__ == '__main__':
    main()
