"""JDLZ (EA BlackBox) em Python: descompressão e compressão.

Porte direto de OpenNFSTools/LibNFS/Compression/JDLZ.cs (compressor de "zombie28",
encode.ru). Usado para regravar sólidos individuais em GEOMETRY.BIN sem GUI.
"""
import struct

HEADER = 16

def decompress(src):
    if src[:4] != b'JDLZ' or src[4] != 2:
        raise ValueError('not JDLZ')
    n = struct.unpack_from('<I', src, 8)[0]
    out = bytearray(n)
    f1 = f2 = 1
    i, o = HEADER, 0
    L = len(src)
    while i < L and o < n:
        if f1 == 1:
            f1 = src[i] | 0x100; i += 1
        if f2 == 1:
            f2 = src[i] | 0x100; i += 1
        if f1 & 1:
            if f2 & 1:
                length = (src[i + 1] | ((src[i] & 0xF0) << 4)) + 3
                t = (src[i] & 0x0F) + 1
            else:
                t = (src[i + 1] | ((src[i] & 0xE0) << 3)) + 17
                length = (src[i] & 0x1F) + 3
            i += 2
            for k in range(length):
                out[o + k] = out[o + k - t]
            o += length
            f2 >>= 1
        else:
            if o < n:
                out[o] = src[i]; o += 1; i += 1
        f1 >>= 1
    return bytes(out)

def compress(data, hash_size=0x2000, max_depth=16):
    MIN = 3
    n = len(data)
    out = bytearray(n + (n + 7) // 8 + HEADER + 1)
    hash_pos = [0] * hash_size
    chain = [0] * max(n, 1)
    out[0:16] = b'JDLZ\x02\x10\x00\x00' + struct.pack('<I', n) + b'\0\0\0\0'
    o = 16
    f1pos = o; o += 1
    f2pos = o; o += 1
    f1bit = 2; f2bit = 1; f1 = 0; f2 = 0
    i = 0
    out[o] = data[i]; o += 1; i += 1
    left = n - 1
    while left > 0:
        best_len = MIN - 1; best_dist = 0
        if left >= MIN:
            h = (-0x1A1 * (data[i] ^ ((data[i + 1] ^ (data[i + 2] << 4)) << 4))) & (hash_size - 1)
            mpos = hash_pos[h]; hash_pos[h] = i; chain[i] = mpos
            prev = i
            for _ in range(max_depth):
                dist = i - mpos
                if dist > 2064 or mpos >= prev:
                    break
                limit = 4098 if dist <= 16 else 34
                maxlen = left if left < limit else limit
                if best_len >= maxlen:
                    break
                ml = 0
                while ml < maxlen and data[i + ml] == data[mpos + ml]:
                    ml += 1
                if ml > best_len:
                    best_len = ml; best_dist = dist
                prev = mpos; mpos = chain[mpos]
        if best_len >= MIN:
            f1 |= f1bit
            i += best_len; left -= best_len
            best_len -= MIN
            if best_dist < 17:
                f2 |= f2bit
                out[o] = ((best_dist - 1) | ((best_len >> 4) & 0xF0)) & 0xFF
                out[o + 1] = best_len & 0xFF
            else:
                best_dist -= 17
                out[o] = (best_len | ((best_dist >> 3) & 0xE0)) & 0xFF
                out[o + 1] = best_dist & 0xFF
            o += 2
            f2bit = (f2bit << 1) & 0xFF
        else:
            out[o] = data[i]; o += 1; i += 1; left -= 1
        f1bit = (f1bit << 1) & 0xFF
        if f1bit == 0:
            out[f1pos] = f1; f1 = 0; f1pos = o; o += 1; f1bit = 1
        if f2bit == 0:
            out[f2pos] = f2; f2 = 0; f2pos = o; o += 1; f2bit = 1
    if f2bit > 1:
        out[f2pos] = f2
    elif f2pos == o - 1:
        o = f2pos
    if f1bit > 1:
        out[f1pos] = f1
    elif f1pos == o - 1:
        o = f1pos
    struct.pack_into('<I', out, 12, o)
    return bytes(out[:o])
