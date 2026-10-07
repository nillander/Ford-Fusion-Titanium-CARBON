"""Read only NFSC minidump exception/register metadata and executable code.

No dump content is copied to the repo; minidumps can contain unrelated user data.
"""
import json
import struct
import sys
from pathlib import Path
from capstone import Cs, CS_ARCH_X86, CS_MODE_32


def diagnose(path):
    data = path.read_bytes()
    assert data[:4] == b'MDMP'
    count, directory = struct.unpack_from('<II', data, 8)
    streams = {k: (size, rva) for k, size, rva in
               (struct.unpack_from('<III', data, directory + i * 12) for i in range(count))}
    _, ex = streams[6]
    code = struct.unpack_from('<I', data, ex + 8)[0]
    address = struct.unpack_from('<Q', data, ex + 24)[0]
    params = struct.unpack_from('<2Q', data, ex + 40)
    size, ctx = struct.unpack_from('<II', data, ex + 160)
    regs = dict(zip(('edi', 'esi', 'ebx', 'edx', 'ecx', 'eax', 'ebp', 'eip'),
                    struct.unpack_from('<8I', data, ctx + 156)))
    regs['esp'] = struct.unpack_from('<I', data, ctx + 196)[0]
    ranges = []
    if 5 in streams:
        _, pos = streams[5]
        n = struct.unpack_from('<I', data, pos)[0]
        for i in range(n):
            start, length, offset = struct.unpack_from('<QII', data, pos + 4 + i * 16)
            ranges.append((start, length, offset))
    if 9 in streams:
        _, pos = streams[9]
        n, offset = struct.unpack_from('<QQ', data, pos)
        for i in range(n):
            start, length = struct.unpack_from('<QQ', data, pos + 16 + i * 16)
            ranges.append((start, length, offset))
            offset += length

    def read(addr, length):
        for start, size, off in ranges:
            if start <= addr and addr + length <= start + size:
                return data[off + addr-start:off + addr-start+length]
        return b''

    instructions = []
    for ins in Cs(CS_ARCH_X86, CS_MODE_32).disasm(read(address-32, 96), address-32):
        instructions.append(f'{ins.address:08X}: {ins.mnemonic} {ins.op_str}')
    pointers = {name: read(value, 32).hex() for name, value in regs.items()
                if name in ('eax', 'ecx', 'edx', 'esi', 'edi')}
    stack = read(regs['esp'], 128)
    return {'dump': path.name, 'exception': f'{code:08X}', 'address': f'{address:08X}',
            'access_type': params[0], 'fault_address': f'{params[1]:08X}',
            'registers': {k: f'{v:08X}' for k,v in regs.items()},
            'instructions': instructions, 'register_pointers': pointers,
            'stack_words': [f'{n:08X}' for n in struct.unpack('<' + 'I'*(len(stack)//4), stack)]}


if __name__ == '__main__':
    print(json.dumps(diagnose(Path(sys.argv[1])), indent=2))
