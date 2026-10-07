"""Prepare a scoped Carbon language patch; never write to the game.

Carbon chunk layout/encryption documented by nlgxzef/Labrune (File.cs,
LanguageChunk.cs). Keep all existing strings/data, append one replacement and
redirect only the CARNAME_FORD_MUSTANGGT record. Preserve XOR encryption.
"""
import hashlib
import json
import struct
from pathlib import Path

TARGET = 0x1CC69F99
NAME = b'Ford Fusion Titanium AWD'
GAME = Path('D:/Program Files (x86)/Electronic Arts/Need for Speed Carbon')


def decode(raw):
    data = bytearray(raw)
    encrypted = data[0] == 0x6B
    if encrypted:
        for index in range(len(data)-1, 0, -1):
            data[index] ^= data[index-1]
        data[0] ^= 0x6B
    return data, encrypted


def encode(data, encrypted):
    if not encrypted:
        return bytes(data)
    output = bytearray(data)
    output[0] ^= 0x6B
    for index in range(1, len(output)):
        output[index] ^= output[index-1]
    return bytes(output)


def parse(data):
    chunks = []
    offset = 0
    while offset < len(data):
        kind, size = struct.unpack_from('<II', data, offset)
        end = offset + 8 + size
        assert end <= len(data)
        payload = data[offset+8:end]
        strings = {}
        if kind == 0x39000:
            count, records, text = struct.unpack_from('<III', payload)
            assert records >= 12 and text >= records + count*8 and text <= size
            for index in range(count):
                key, position = struct.unpack_from('<II', payload, records+index*8)
                start = text + position
                assert start < size and key not in strings
                strings[key] = bytes(payload[start:payload.index(0, start)])
        chunks.append((offset, end, kind, payload, strings))
        offset = end
    assert offset == len(data)
    return chunks


def patch(raw):
    data, encrypted = decode(raw)
    chunks = parse(data)
    selected = [chunk for chunk in chunks if TARGET in chunk[4]]
    assert len(selected) == 1
    offset, end, kind, payload, strings = selected[0]
    count, records, text = struct.unpack_from('<III', payload)
    target_index = next(i for i in range(count) if struct.unpack_from('<I', payload, records+i*8)[0] == TARGET)
    new_payload = bytearray(payload)
    struct.pack_into('<I', new_payload, records+target_index*8+4, len(payload)-text)
    new_payload.extend(NAME+b'\0')
    new_payload.extend(b'\0'*((-len(new_payload))%4))
    result = encode(data[:offset]+struct.pack('<II', kind, len(new_payload))+new_payload+data[end:], encrypted)
    checked, checked_encryption = decode(result)
    after = parse(checked)
    assert checked_encryption == encrypted and len(chunks) == len(after)
    for previous, current in zip(chunks, after):
        assert previous[2] == current[2]
        expected = dict(previous[4])
        if TARGET in expected:
            expected[TARGET] = NAME
            assert current[4] == expected
            # Apart from the one pointer, original chunk bytes stay identical.
            prefix = bytearray(current[3][:len(payload)])
            struct.pack_into('<I', prefix, records+target_index*8+4,
                             struct.unpack_from('<I', payload, records+target_index*8+4)[0])
            assert prefix == payload
        else:
            assert previous[3] == current[3]
    return result, strings[TARGET], len(strings), encrypted


def main():
    backup = Path('work/languages-before-integration-2018')
    output = Path('work/languages2018-name')
    backup.mkdir(parents=True, exist_ok=True)
    output.mkdir(parents=True, exist_ok=True)
    files = []
    for source in sorted((GAME/'LANGUAGES').glob('*_Frontend.bin')):
        if source.name.startswith('Labels_'):
            continue
        raw = source.read_bytes()
        saved = backup/source.name
        if saved.exists():
            assert saved.read_bytes() == raw, f'Language changed after backup: {source}'
        else:
            saved.write_bytes(raw)
        candidate, before, count, encrypted = patch(raw)
        (output/source.name).write_bytes(candidate)
        files.append({'file': source.name, 'strings_checked': count, 'encrypted': encrypted,
                      'before': before.decode('latin1'), 'after': NAME.decode(),
                      'before_sha256': hashlib.sha256(raw).hexdigest().upper(),
                      'after_sha256': hashlib.sha256(candidate).hexdigest().upper()})
    assert any(item['file']=='English_Frontend.bin' for item in files)
    Path('docs/carbon2018-frontend-name-verification.json').write_text(json.dumps({
        'status':'passed', 'target_hash':'1CC69F99', 'target_label':'CARNAME_FORD_MUSTANGGT',
        'only_record_changed':True, 'game_validation':'pending', 'installed':False,
        'source_format':'https://github.com/nlgxzef/Labrune', 'files': files,
    },indent=2)+'\n')
    print(f'Prepared {len(files)} language files; only one record changed per file; game untouched.')


if __name__=='__main__':
    main()
