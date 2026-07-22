#!/usr/bin/env python3
"""Regenerate LP(333) DIMACS hashes from the independent orbit/PB encoder."""

from __future__ import annotations

import json
from pathlib import Path

from lp333_cnf import build_lp333_model, dimacs_sha256


PHASE = Path(__file__).resolve().parent


def main() -> int:
    manifest = json.loads((PHASE / "manifest.json").read_text(encoding="utf-8"))
    results = []
    for record in manifest["records"]:
        model, _ = build_lp333_model(record["subgroup_id"])
        base_hash = dimacs_sha256(model.builder)
        proof_hash = dimacs_sha256(model.builder, split_unit_clauses=True)
        if base_hash != record["cnf_sha256"]:
            raise AssertionError(f"id {record['subgroup_id']}: base CNF hash mismatch")
        if proof_hash != record["proof_cnf_sha256"]:
            raise AssertionError(f"id {record['subgroup_id']}: proof CNF hash mismatch")
        results.append(
            {
                "id": record["subgroup_id"],
                "base_cnf_sha256": base_hash,
                "proof_cnf_sha256": proof_hash,
                "result": "PASS",
            }
        )
    payload = {
        "kind": "independent-orbit-PB-regeneration-hash-audit",
        "records": results,
        "result": "PASS",
    }
    (PHASE / "audits" / "independent_rebuild_audit.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
