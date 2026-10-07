"""Export the approved MW meshes to OBJ for nfsu360's Carbon compiler.

Uses the project's MW parser; compiler input is staging, not an installable port.
The slot donor remains the corresponding official Carbon vehicle.
"""
import argparse
import csv
import importlib.util
import json
import re
import shutil
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
MW = ROOT.parent / "fusion-mw2005"


def bh(name):
    value = 0xFFFFFFFF
    for byte in name.encode("ascii"):
        value = (value * 33 + byte) & 0xFFFFFFFF
    return value


def names_from_files(paths):
    names = {}
    for path in paths:
        for raw in re.findall(rb"[A-Z][A-Z0-9_]{2,80}\x00", path.read_bytes()):
            name = raw[:-1].decode("ascii")
            names.setdefault(bh(name), name)
    return names


def main():
    cli = argparse.ArgumentParser()
    cli.add_argument("--indices-directory", type=Path, help="Optional validated simplification outputs")
    args = cli.parse_args()
    spec = importlib.util.spec_from_file_location("mwgeo", MW / "scripts/lente-vidros-capo/mwgeo.py")
    parser = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parser)
    source = next(p for p in (ROOT / "reference/mw-v28/Fusion2018_AWD_MW2005").rglob("GEOMETRY.BIN")
                  if "ADDONS" not in p.parts)
    parts = parser.load(source)
    stock = json.loads((ROOT / "docs/geometry-inventory.json").read_text())
    donor = next(s for s in stock if s["path"].startswith("reference/carbon-stock/MUSTANGGT/"))
    mw_names = {p["name"] for p in parts}
    donor_names = {p["name"] for p in donor["readable_headers"]}
    with (ROOT / "docs/mustanggt-part-map.csv").open("w", newline="", encoding="utf-8") as out:
        writer = csv.writer(out)
        writer.writerow(["carbon_official_part", "mw_exact_part", "classification", "status"])
        for name in sorted(donor_names):
            category = "autosculpt" if re.search(r"_T\d+_|_AS_", name) else "damage" if "DAMAGE" in name else "standard"
            writer.writerow([name, name if name in mw_names else "", category,
                             "needs adaptation" if name not in mw_names else "export source available"])
    stage = ROOT / "work/carbon2018-source"
    stage.mkdir(parents=True, exist_ok=True)
    texture_metadata = json.loads((ROOT / "work/mw2018-textures.json").read_text())["textures"]
    known = names_from_files(list((ROOT / "reference/carbon-global-before").glob("*")) +
                             list((ROOT / "reference/carbon-stock/MUSTANGGT").glob("*.BIN")) +
                             list(Path('D:/Program Files (x86)/Electronic Arts/Need For Speed Most Wanted Black Edition/GLOBAL').glob('*.BUN')))
    for candidate in ["SOLIDGREY", "LICENSEPLATE", "DRIVER_PLAYER", "DRIVER_CUTOUT", "ROTOR4",
                      "WINDOW_FRONT", "WINDOW_REAR", "WINDOW_LEFT", "WINDOW_RIGHT", "TIRE_STYLE01",
                      "WINDOW_LEFT_FRONT", "WINDOW_LEFT_REAR", "WINDOW_RIGHT_FRONT", "WINDOW_RIGHT_REAR"]:
        known[bh(candidate)] = candidate
    texture_folder = stage / "texture"
    texture_folder.mkdir(exist_ok=True)
    texture_map = {}
    for texture in texture_metadata:
        name = texture["Name"]
        # MW name fields truncate the long light names while retaining the full-name hash.
        if name == "MUSTANGGT_KIT00_BRAKELI": name = "MUSTANGGT_BRAKE_OFF"
        if name == "MUSTANGGT_KIT00_HEADLIG": name = "MUSTANGGT_HEAD_OFF"
        if len(name) > 23: raise ValueError("Texture name exceeds project limit")
        known[texture["TexHash"]] = name
        texture_map[f"{texture['TexHash']:08X}"] = {"name": name, "new_hash": f"{bh(name):08X}"}
        shutil.copyfile(ROOT / "work/mw2018-dds" / f"{texture['TexHash']:08X}.dds", texture_folder / (name + ".dds"))
    used_textures = {p["tex"][g["tex"][0]] for p in parts for g in p["groups"] if g["tris"]}
    unknown = sorted(f"{h:08X}" for h in used_textures if h not in known)
    (stage / "texture-remap.json").write_text(json.dumps(texture_map, indent=2) + "\n")
    if unknown:
        (stage / "unresolved-textures.json").write_text(json.dumps(unknown, indent=2) + "\n")
        # Preserve exact shared hashes in the compiler format; validate output before installing.
        for value in unknown:
            known[int(value, 16)] = "0x" + value
    materials = {}
    summaries = []
    for part in parts:
        if len(part["vbs"]) != 1:
            raise ValueError("Unsupported multi-stream MW solid: " + part["name"])
        vertices = part["vbs"][0]
        if len(vertices) > 65535 or not np.isfinite(vertices["p"]).all() or not np.isfinite(vertices["n"]).all():
            raise ValueError("Invalid vertices: " + part["name"])
        if max(part["idx"], default=0) >= len(vertices): raise ValueError("Invalid MW index")
        # Leave the slot prefix to the compiler's car selector.
        name = part["name"].removeprefix("MUSTANGGT_")
        with (stage / (name + ".obj")).open("w", encoding="ascii", newline="\n") as out:
            out.write(f"g {name}\n")
            for vertex in vertices:
                out.write("v {:.9g} {:.9g} {:.9g}\n".format(*vertex["p"]))
            for vertex in vertices:
                out.write("vt {:.9g} {:.9g}\n".format(*vertex["uv"]))
            for vertex in vertices:
                out.write("vn {:.9g} {:.9g} {:.9g}\n".format(*vertex["n"]))
            offset = 0
            exported_indices = 0
            for group_index, group in enumerate(part["groups"]):
                count = group["tris"] * 3
                shader = part["sh"][group["sh"]]
                texture = part["tex"][group["tex"][0]]
                material = f"M_{shader:08X}_{texture:08X}"
                materials[material] = (shader, known[texture])
                out.write(f"usemtl {material}\ns 1\n")
                selected = part["idx"][offset:offset + count]
                simplified = args.indices_directory / f"{part['name']}.{group_index}.bin" if args.indices_directory else None
                if simplified and simplified.exists():
                    selected = np.fromfile(simplified, dtype="<u4")
                    if len(selected) % 3 or len(selected) > count or max(selected, default=0) >= len(vertices):
                        raise ValueError("Invalid simplified indices")
                    # Collapses retain original vertices and attributes; faces may join former neighbours.
                    if not set(map(int, selected)).issubset(set(map(int, part["idx"][offset:offset + count]))):
                        raise ValueError("Simplification crossed material boundary")
                exported_indices += len(selected)
                for face in selected.reshape(-1,3):
                    out.write("f " + " ".join(f"{int(i)+1}/{int(i)+1}/{int(i)+1}" for i in face) + "\n")
                offset += count
            if offset != len(part["idx"]): raise ValueError("Index accounting mismatch")
        summaries.append({"name": part["name"], "vertices": len(vertices), "triangles": exported_indices // 3, "original_triangles": offset // 3})
    (stage / "matlist.txt").write_text("\n".join(f"{name}\t0x{shader:08X}\t{texture}"
                                               for name,(shader,texture) in sorted(materials.items())) + "\n")
    (stage / "link.txt").write_text("# Explicit MW LOD meshes already exported; donor adaptation pending.\n")
    (stage / "mpoints.txt").write_text("# Official Carbon mount-point adaptation pending.\n")
    report = {"source": source.relative_to(ROOT).as_posix(), "official_donor": donor["path"],
              "source_parts": len(parts), "donor_parts": len(donor_names),
              "exact_matches": len(mw_names & donor_names), "missing_exact": len(donor_names - mw_names),
              "materials": len(materials), "shared_texture_hashes_without_names": unknown, "parts": summaries,
              "simplification_indices": str(args.indices_directory) if args.indices_directory else None,
              "status": "compiler input only; donor compatibility adaptation pending"}
    (ROOT / "docs/carbon2018-source-report.json").write_text(json.dumps(report, indent=2)+"\n")
    print(f"Prepared {len(parts)} Fusion OBJ meshes; {len(materials)} materials; "
          f"{report['exact_matches']}/{len(donor_names)} exact donor part matches.")


if __name__ == "__main__":
    main()
