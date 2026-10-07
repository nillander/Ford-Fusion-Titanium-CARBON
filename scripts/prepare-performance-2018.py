"""Generate scoped Carbon ModScripts from MW v2.8 values and an Attribulator dump.

Requires PyYAML. Does not write into the game. No MW byte offsets are reused.
"""
import argparse
import copy
import hashlib
import json
import re
import struct
from pathlib import Path

import yaml


def parse_mwps(path):
    node = field = None
    values = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        match = re.match(r"## Node: (\w+)/.*?/([^/]+)$", line)
        if match:
            node = (match[1], match[2])
            field = None
            continue
        match = re.match(r"## (\w+)(?:\[\d+\])?(?:;|$)", line)
        if match:
            field = match[1]
        match = re.match(r"patch\s+(float|int16)\s+bin:\S+\s+(\S+)", line)
        if match and node and field:
            values.setdefault(node, {}).setdefault(field, []).append(float(match[2]))
    return values


def leaves(value, path=""):
    if isinstance(value, dict) and "Capacity" in value:
        for index, item in enumerate(value["Data"]):
            yield from leaves(item, f"{path}[{index}]")
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from leaves(item, f"{path} {key}")
    else:
        yield path, value


def f32(value):
    return struct.unpack("<f", struct.pack("<f", value))[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, default=Path("work/vlt-baseline-yaml"))
    parser.add_argument("--steering-range-scale", type=float, default=1.15)
    args = parser.parse_args()
    source = next(Path("reference/mw-v28/Fusion2018_AWD_MW2005").rglob("ATTRIBUTES.MWPS"))
    parsed = parse_mwps(source)
    engine_rows = yaml.safe_load((args.baseline / 'main/attributes/db/engine.yml').read_text())
    bmw = next(row for row in engine_rows if row['Name'] == 'bmwm3gtre46')['Data']
    changed = []
    commands = ["game C", "# Fusion 2018: MW v2.8 handling, AWD; preserve Carbon price/unlock/visual mounts."]
    rollback = ["game C", "# Restore only the fields changed by Fusion2018-performance.nfsms."]
    allowed = {"pvehicle", "engine", "chassis", "transmission", "tires", "brakes"}
    for (cls, node), fields in parsed.items():
        if cls not in allowed:
            continue
        assert node in {"mustanggt", "mustanggt_top"}, (cls, node)
        rows = yaml.safe_load((args.baseline / "main/attributes/db" / f"{cls}.yml").read_text(encoding='utf-8'))
        row = next(item for item in rows if item["Name"] == node)
        if cls == 'engine':
            # BMW playable pvehicle points to bmwm3gtre46, not unused bmwm3gtr.
            # Same RPM domain + every torque control point x1.20 scales the
            # engine power curve by 20%; does not promise 20% vehicle speed.
            fields['TORQUE'] = [v * 1.2 for v in bmw['TORQUE']['Data']]
            for field in ('MAX_RPM', 'RED_LINE', 'IDLE'):
                fields[field] = [bmw[field]]
        if cls == "tires":
            # Angle-only revision failed in game, including at low speed.
            # Compare less axle locking and neutral grip, retaining the donor's
            # yaw-control curve rather than assuming MW's curve transfers well.
            fields["STEERING"] = [1.1]
            fields["STEERING_RANGE"] = [v * args.steering_range_scale for v in row["Data"]["STEERING_RANGE"]["Data"]]
            fields["YAW_CONTROL"] = row["Data"]["YAW_CONTROL"]["Data"][:]
            fields["YAW_SPEED"] = [0.3]
            for grip in ("STATIC_GRIP", "DYNAMIC_GRIP"):
                front = fields[grip][0]
                fields[grip] = [front, front]
        for field, values in fields.items():
            # MW's count is the GEAR_RATIO array count, not a Carbon field.
            # Keep approved visual height and all ecar mount/body settings.
            if field in {"GEAR_COUNT", "RIDE_HEIGHT"}:
                continue
            old = row["Data"][field]
            target = copy.deepcopy(old)
            if cls == "transmission" and field == "TORQUE_SPLIT":
                values = [0.5]  # User decision: symmetric AWD.
            if cls == "transmission" and field == "DIFFERENTIAL":
                values = [0.35, 0.5, 0.5]  # Comparison: less front/rear/centre locking.
            if isinstance(old, dict) and "Capacity" in old:
                if field == "GEAR_RATIO":
                    values = values[:int(fields["GEAR_COUNT"][0])]
                assert len(values) == len(old["Data"]), (cls, node, field)
                target["Data"] = [f32(v) for v in values]
            elif isinstance(old, dict):
                assert len(values) == len(old), (cls, node, field)
                target = dict(zip(old, map(f32, values)))
            else:
                assert len(values) == 1, (cls, node, field)
                target = f32(values[0])
            old_leaves = dict(leaves(old, field))
            for path, value in leaves(target, field):
                previous = old_leaves[path]
                # Explicitly write even baseline-equal values: importing over
                # earlier candidates must reset STEERING/YAW_CONTROL as well.
                commands.append(f"update_field {cls} {node} {path} {value:.9g}")
                rollback.append(f"update_field {cls} {node} {path} {previous:.9g}")
            if old != target:
                changed.append({"class": cls, "node": node, "field": field, "before": old, "after": target})
    output = Path("release/vlt")
    output.mkdir(parents=True, exist_ok=True)
    (output / "Fusion2018-performance.nfsms").write_text("\n".join(commands) + "\n")
    (output / "Fusion2018-performance-rollback.nfsms").write_text("\n".join(rollback) + "\n")
    report = {
        "source": source.as_posix(), "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "traction": "AWD, TORQUE_SPLIT=0.5 at base and top, user confirmed 2026-10-07",
        "cost": "preserve Carbon MUSTANGGT 50000, user confirmed 2026-10-07",
        "power_reference": {"engine": "bmwm3gtre46", "factor": 1.2,
                            "reference_torque": bmw['TORQUE']['Data'],
                            "MAX_RPM": bmw['MAX_RPM'], "RED_LINE": bmw['RED_LINE'],
                            "scope": "mustanggt and mustanggt_top; engine curve, without induction/nitrous"},
        "steering_revision": {"STEERING": 1.1, "STEERING_RANGE_scale": args.steering_range_scale,
                              "YAW_CONTROL": "original Carbon MUSTANGGT base/top", "YAW_SPEED": 0.3,
                              "DIFFERENTIAL": [0.35, 0.5, 0.5], "grip": "equal front/rear, MW front value",
                              "reason": "Third handling candidate confirmed good by user 2026-10-07; retained for power adjustment."},
        "excluded": ["frontend cost/unlock", "ecar visual mounts", "chassis RIDE_HEIGHT", "audio", "induction", "nos", "Carbon-only drift fields"],
        "changes": changed,
    }
    Path("docs/carbon2018-performance-plan.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"{len(changed)} fields, {len(commands)-2} leaf updates; scripts generated, game untouched.")


if __name__ == "__main__":
    main()
