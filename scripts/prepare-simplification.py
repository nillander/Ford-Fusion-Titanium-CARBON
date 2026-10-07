"""Stage attribute-preserving simplification jobs for Carbon's 16-bit index-count limit."""
import importlib.util
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("mwgeo", ROOT.parent / "fusion-mw2005/scripts/lente-vidros-capo/mwgeo.py")
parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parser)
source = next((ROOT / "reference/mw-v28/Fusion2018_AWD_MW2005").rglob("GEOMETRY.BIN"))
destination = ROOT / "work/simplification2018"
destination.mkdir(parents=True, exist_ok=True)
jobs = []
for part in parser.load(source):
    if len(part["idx"]) <= 65535:
        continue
    if len(part["vbs"]) != 1:
        raise ValueError("Multi-stream source unsupported")
    vertices = part["vbs"][0]
    prefix = part["name"]
    vertices["p"].astype("<f4").tofile(destination / (prefix + ".positions.bin"))
    attrs = np.column_stack((vertices["n"], vertices["uv"]))
    attrs.astype("<f4").tofile(destination / (prefix + ".attributes.bin"))
    part["idx"].astype("<u4").tofile(destination / (prefix + ".indices.bin"))
    jobs.append({"name": prefix, "vertices": len(vertices), "indices": len(part["idx"]),
                 "groups": [g["tris"] * 3 for g in part["groups"]]})
(destination / "jobs.json").write_text(json.dumps(jobs, indent=2) + "\n")
print(f"Prepared {len(jobs)} over-limit meshes; approved MW inputs unchanged.")
