#!/usr/bin/env python3
"""Create or check immutable source/data/checker pins for proof_phase2."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


PHASE = Path(__file__).resolve().parent
PIN_FILE = PHASE / "dependency_pins.json"
PINNED_PATHS = (
    ("../code/core.py", "orbit primitives used by the primary implementation"),
    ("../code/search_common.py", "subgroup-record loader used by the primary implementation"),
    ("../results/subgroup_classification.json", "multiplier subgroup data"),
    ("tools/drat-trim/drat-trim.c", "pinned independent DRAT checker source"),
)


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            hasher.update(block)
    return hasher.hexdigest()


def canonical_digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def build_pins() -> dict:
    manifest = json.loads((PHASE / "manifest.json").read_text(encoding="utf-8"))
    files = []
    for relative, role in PINNED_PATHS:
        path = (PHASE / relative).resolve()
        files.append(
            {
                "path": relative,
                "role": role,
                "bytes": path.stat().st_size,
                "sha256": digest(path),
            }
        )
    classification = json.loads(
        ((PHASE / "../results/subgroup_classification.json").resolve()).read_text(
            encoding="utf-8"
        )
    )
    by_id = {int(record["id"]): record for record in classification["subgroups"]}
    subgroup_records = [
        {
            "id": int(record["subgroup_id"]),
            "canonical_sha256": canonical_digest(by_id[int(record["subgroup_id"])]),
        }
        for record in manifest["records"]
    ]
    return {
        "format": "lp333-proof-phase2-dependency-pins-v1",
        "files": files,
        "subgroup_records": subgroup_records,
    }


def check_pins(pins: dict) -> list[str]:
    errors = []
    for item in pins["files"]:
        path = (PHASE / item["path"]).resolve()
        if not path.is_file():
            errors.append(f"missing: {item['path']}")
        elif digest(path) != item["sha256"]:
            errors.append(f"hash mismatch: {item['path']}")
    classification = json.loads(
        ((PHASE / "../results/subgroup_classification.json").resolve()).read_text(
            encoding="utf-8"
        )
    )
    by_id = {int(record["id"]): record for record in classification["subgroups"]}
    for item in pins["subgroup_records"]:
        record = by_id.get(int(item["id"]))
        if record is None:
            errors.append(f"missing subgroup record: {item['id']}")
        elif canonical_digest(record) != item["canonical_sha256"]:
            errors.append(f"subgroup record mismatch: {item['id']}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        pins = json.loads(PIN_FILE.read_text(encoding="utf-8"))
        errors = check_pins(pins)
        print(json.dumps({"result": "PASS" if not errors else "FAIL", "errors": errors}))
        return 0 if not errors else 1
    pins = build_pins()
    PIN_FILE.write_text(json.dumps(pins, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"result": "PASS", "pinned_files": len(pins["files"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
