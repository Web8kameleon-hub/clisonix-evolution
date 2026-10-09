#!/usr/bin/env python3
import json
import pathlib
import sys
from typing import Dict, List


def parse_vcd(path: pathlib.Path):
    id_meta: Dict[str, Dict[str, str]] = {}
    seen0: Dict[str, bool] = {}
    seen1: Dict[str, bool] = {}

    in_definitions = True

    with path.open("r", encoding="utf-8", errors="ignore") as fh:
        for raw in fh:
            line = raw.strip()
            if not line:
                continue

            if in_definitions:
                if line.startswith("$var"):
                    parts = line.split()
                    if len(parts) >= 5:
                        width = parts[2]
                        ident = parts[3]
                        name = parts[4]
                        id_meta[ident] = {"width": width, "name": name}
                        seen0[ident] = False
                        seen1[ident] = False
                elif line.startswith("$enddefinitions"):
                    in_definitions = False
                continue

            if line[0] in ("0", "1"):
                value = line[0]
                ident = line[1:]
                if ident in id_meta and id_meta[ident]["width"] == "1":
                    if value == "0":
                        seen0[ident] = True
                    else:
                        seen1[ident] = True

    scalar = [ident for ident, meta in id_meta.items() if meta["width"] == "1"]
    toggle = [ident for ident in scalar if seen0.get(ident) and seen1.get(ident)]

    ratio = (len(toggle) / len(scalar) * 100.0) if scalar else 0.0

    return {
        "file": str(path),
        "scalar_signals": len(scalar),
        "toggled_signals": len(toggle),
        "toggle_coverage_percent": round(ratio, 2),
    }


def main(argv: List[str]) -> int:
    if len(argv) < 2:
        print("usage: coverage_report.py <vcd files...>")
        return 2

    reports = []
    for p in argv[1:]:
        path = pathlib.Path(p)
        if not path.exists():
            print(f"missing vcd: {path}")
            return 2
        reports.append(parse_vcd(path))

    all_scalars = sum(item["scalar_signals"] for item in reports)
    all_toggled = sum(item["toggled_signals"] for item in reports)
    overall = round((all_toggled / all_scalars * 100.0), 2) if all_scalars else 0.0

    summary = {
        "overall": {
            "scalar_signals": all_scalars,
            "toggled_signals": all_toggled,
            "toggle_coverage_percent": overall,
        },
        "files": reports,
    }

    print(json.dumps(summary, indent=2))

    out_dir = pathlib.Path("out")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "coverage-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
