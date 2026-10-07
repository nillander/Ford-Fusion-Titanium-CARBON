"""Regression cases for Carbon's terminal control-byte reads."""
import random
import struct
import unittest
import jdlz


class CarbonJdlzTests(unittest.TestCase):
    def test_roundtrip_and_game_boundaries(self):
        rng = random.Random(42)
        cases = [bytes(rng.randrange(256) for _ in range(n))
                 for n in (0, 1, 7, 8, 9, 15, 16, 17, 64, 255)]
        cases += [b'a' * n for n in (16, 64, 4099)] + [bytes(range(256)) * 4]
        for data in cases:
            for compressor in (jdlz.compress, jdlz.compress_optimal):
                with self.subTest(length=len(data), compressor=compressor.__name__):
                    encoded = compressor(data)
                    self.assertEqual(jdlz.decompress(encoded), data)
                    self.assertEqual(jdlz.normalize_for_game(encoded, repair=False), encoded)

    def test_missing_literal_group_flag(self):
        data = b'abcdefgh'
        encoded = bytearray(jdlz._emit(data, [None] * 8))
        encoded.pop()  # The old emitter discarded the required terminal flag.
        struct.pack_into('<I', encoded, 12, len(encoded))
        self.assertEqual(jdlz.decompress(encoded), data)  # Old validator misses it.
        with self.assertRaisesRegex(ValueError, 'terminal control flag'):
            jdlz.normalize_for_game(encoded, repair=False)
        fixed = jdlz.normalize_for_game(encoded)
        self.assertEqual(jdlz.decompress(fixed), data)
        jdlz.normalize_for_game(fixed, repair=False)

    def test_missing_match_group_flag(self):
        data = b'a' * 25
        encoded = bytearray(jdlz._emit(data, [None] + [(1, 3)] * 8))
        encoded.pop()
        struct.pack_into('<I', encoded, 12, len(encoded))
        self.assertEqual(jdlz.decompress(encoded), data)
        with self.assertRaisesRegex(ValueError, 'terminal control flag'):
            jdlz.normalize_for_game(encoded, repair=False)
        jdlz.normalize_for_game(jdlz.normalize_for_game(encoded), repair=False)


if __name__ == '__main__':
    unittest.main()
