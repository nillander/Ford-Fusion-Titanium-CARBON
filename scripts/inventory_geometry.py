"""Read chunk headers/catalogues only; does not decompress or validate meshes.

Layouts: local NFS-ModTools Common/Geometry/{Carbon,MostWanted}Solid*Reader.cs.
"""
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def inventory(path):
    data = path.read_bytes()
    carbon = "carbon-stock" in path.parts
    result = {"path": path.relative_to(ROOT).as_posix(),
              "sha256": hashlib.sha256(data).hexdigest().upper(),
              "declared_count": None, "streaming": [], "readable_headers": []}

    def chunks(start, end):
        while start < end:
            if start + 8 > end:
                raise ValueError(f"Truncated chunk at {start:X}: {path}")
            kind, size = struct.unpack_from("<II", data, start)
            payload, stop = start + 8, start + 8 + size
            if stop > end:
                raise ValueError(f"Chunk exceeds container at {start:X}: {path}")
            yield kind, payload, stop
            start = stop

    def walk(start, end):
        for kind, payload, stop in chunks(start, end):
            if kind == 0x134002:
                result["declared_count"] = struct.unpack_from("<I", data, payload + 12)[0]
            elif kind == 0x134004:
                if (stop - payload) % 24:
                    raise ValueError("Invalid streaming table size")
                for p in range(payload, stop, 24):
                    key, offset, packed, size, flags, _ = struct.unpack_from("<6I", data, p)
                    if offset + packed > len(data):
                        raise ValueError("Streaming object exceeds file")
                    result["streaming"].append({"hash": f"{key:08X}", "offset": offset,
                                                "packed_bytes": packed, "bytes": size,
                                                "compressed": packed != size, "flags": flags})
            elif kind == 0x134011:
                aligned = (payload + 15) & ~15
                if aligned + 160 >= stop:
                    raise ValueError("Truncated solid header")
                name_end = data.index(b"\0", aligned + 160, stop)
                name = data[aligned + 160:name_end].decode("ascii")
                key = struct.unpack_from("<I", data, aligned + 16)[0]
                result["readable_headers"].append({"name": name, "hash": f"{key:08X}"})
            elif kind in (0x80134000, 0x80134001, 0x80134010, 0x80134100):
                walk(payload, stop)
                if carbon and result["streaming"]:
                    return  # Remaining Carbon bytes are streamed/CIP data, not chunks.

    walk(0, len(data))
    if carbon:
        for entry in result["streaming"]:
            if not entry["compressed"]:
                walk(entry["offset"], entry["offset"] + entry["bytes"])
    names = [r["name"] for r in result["readable_headers"]]
    if len(names) != len(set(names)):
        raise ValueError(f"Duplicate solid names: {path}")
    result["compressed_count"] = sum(r["compressed"] for r in result["streaming"])
    result["named_count"] = len(names)
    catalogue_count = len(result["streaming"]) if carbon else len(names)
    if result["declared_count"] != catalogue_count:
        raise ValueError(f"Catalogue count disagrees with header: {path}")
    catalogue_hashes = [r["hash"] for r in result["streaming"]] if carbon else [
        r["hash"] for r in result["readable_headers"]]
    if len(catalogue_hashes) != len(set(catalogue_hashes)):
        raise ValueError(f"Duplicate catalogue hashes: {path}")
    result["mesh_validation"] = "not performed"
    return result


def main():
    paths = sorted((ROOT / "reference/carbon-stock").glob("*/GEOMETRY.BIN"))
    paths += sorted(p for p in (ROOT / "reference/mw-v28").rglob("GEOMETRY.BIN")
                    if "ADDONS" not in p.parts)
    if len(paths) != 4:
        raise ValueError("Expected two Carbon donors and two MW source geometries")
    report = [inventory(p) for p in paths]
    output = ROOT / "docs/geometry-inventory.json"
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for item in report:
        print(f"{item['path']}: declared={item['declared_count']}, "
              f"named={item['named_count']}, compressed={item['compressed_count']}")


if __name__ == "__main__":
    main()
