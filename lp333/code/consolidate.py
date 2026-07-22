#!/usr/bin/env python3
"""Consolidate every family's verdict into a master status + certificate JSON.

Reads the classification and all result artifacts and assigns each of the 30
subgroup families exactly one status with a labeled method:
  IMPOSSIBLE (proved)  -- with the exact method and certificate pointer
  OPEN (not exhausted) -- search did not terminate within budget
  FOUND (verified LP)  -- an actual invariant Legendre pair (would be a Hadamard 668)
"""
import json
import os
import glob

HERE = os.path.dirname(__file__)
RES = os.path.join(HERE, "..", "results")
CERT = os.path.join(HERE, "..", "certificates")


def load(p, default=None):
    try:
        with open(p) as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def main():
    cls = load(os.path.join(RES, "subgroup_classification.json"))
    subs = {r["id"]: r for r in cls["subgroups"]}
    nc = {r["id"]: r for r in load(os.path.join(RES, "necessary_conditions.json"), [])}

    # gather cpsat + column results (prefer terminal verdicts)
    cpsat = {}
    for p in glob.glob(os.path.join(RES, "cpsat", "*.json")):
        d = load(p)
        if not d or "id" not in d:
            continue
        sid = d["id"]
        # keep the most informative (INFEASIBLE/FEASIBLE over UNKNOWN)
        prev = cpsat.get(sid)
        rank = {"INFEASIBLE": 3, "OPTIMAL": 3, "FEASIBLE": 3, "UNKNOWN": 1}
        if prev is None or rank.get(d["status"], 0) >= rank.get(prev["status"], 0):
            cpsat[sid] = d
    mitm = {}
    for p in glob.glob(os.path.join(RES, "mitm", "*.json")):
        d = load(p)
        if d:
            mitm[d["id"]] = d

    status = {}
    for sid, rec in subs.items():
        entry = {
            "id": sid, "order": rec["order"], "r": rec["num_orbits"],
            "reduction_mod9_order": rec["structure"]["reduction_mod9_order"],
            "reduction_mod37_order": rec["structure"]["reduction_mod37_order"],
            "orbit_signature": rec["orbit_signature"],
            "generators": rec["generators"],
        }
        # priority of verdicts
        if rec["killed_by_mod37_obstruction"]:
            entry.update(status="IMPOSSIBLE", label="proved",
                         method="mod37_full_reduction_obstruction",
                         certificate="certificates/obstruction_certificates.json")
        elif nc.get(sid, {}).get("killed_by_rowsum"):
            entry.update(status="IMPOSSIBLE", label="proved",
                         method="rowsum_modular_obstruction",
                         rowsum_witness_modulus=nc[sid]["rowsum_witness_modulus"],
                         certificate="results/necessary_conditions.json")
        elif sid in mitm and mitm[sid]["sat"] is False:
            entry.update(status="IMPOSSIBLE", label="proved",
                         method="exact_meet_in_the_middle",
                         enumerated=mitm[sid]["enumerated"],
                         rowsum_valid=mitm[sid]["rowsum_ok"],
                         certificate=f"results/mitm/id{sid}.json")
        elif sid in cpsat and cpsat[sid].get("sat") is False:
            entry.update(status="IMPOSSIBLE", label="proved",
                         method="exact_CP_SAT_" + (
                             "column_model" if cpsat[sid].get("model", "").startswith("column")
                             else "booleanized"),
                         certificate=f"results/cpsat/{os.path.basename(_find(sid))}"
                         if _find(sid) else None)
        elif sid in cpsat and cpsat[sid].get("sat") is True and cpsat[sid].get("verified_legendre_pair"):
            entry.update(status="FOUND", label="verified_LP",
                         method="exact_CP_SAT",
                         certificate=f"results/cpsat/id{sid}.json")
        else:
            entry.update(status="OPEN", label="not_exhausted",
                         method="search_incomplete_within_budget")
        status[sid] = entry

    # ---- PHASE 2 overrides (value-set-restricted 9-compression obstruction) ----
    # These families are proved IMPOSSIBLE in phase 2 and MUST take precedence so
    # a fresh consolidation never regresses them to OPEN.
    p2 = load(os.path.join(HERE, "..", "id12_phase2", "results",
                           "general_compression_certificate.json"))
    if p2 is None:
        raise SystemExit("ERROR: phase-2 certificate missing "
                         "(id12_phase2/results/general_compression_certificate.json); "
                         "run id12_phase2/run_all.sh first.")
    phase2_closed = p2.get("closed_impossible", [])
    assert sorted(phase2_closed) == [6, 8, 12], phase2_closed
    for sid in phase2_closed:
        status[sid].update(
            status="IMPOSSIBLE", label="proved",
            method="phase2_value_set_9_compression_obstruction",
            certificate="id12_phase2/results/general_compression_certificate.json"
            if sid != 12 else
            "id12_phase2/results/id12_impossible_certificate.json",
            phase2=True)

    # summary
    by_status = {}
    for e in status.values():
        by_status.setdefault(e["status"], []).append(e["id"])
    order_ge = lambda k: sorted(e["id"] for e in status.values()
                                if e["order"] >= k and e["status"] == "IMPOSSIBLE")
    summary = {
        "total_families": len(status),
        "killed_by_mod37_full_reduction": sorted(
            e["id"] for e in status.values() if e["method"] == "mod37_full_reduction_obstruction"),
        "impossible_ids": sorted(by_status.get("IMPOSSIBLE", [])),
        "open_ids": sorted(by_status.get("OPEN", [])),
        "found_ids": sorted(by_status.get("FOUND", [])),
        "num_impossible": len(by_status.get("IMPOSSIBLE", [])),
        "num_open": len(by_status.get("OPEN", [])),
        "num_found": len(by_status.get("FOUND", [])),
        "all_order_ge_12_impossible": all(
            e["status"] == "IMPOSSIBLE" for e in status.values() if e["order"] >= 12),
        "all_order_ge_9_impossible": all(
            e["status"] == "IMPOSSIBLE" for e in status.values() if e["order"] >= 9),
        "impossible_orders_min": min((e["order"] for e in status.values()
                                      if e["status"] == "IMPOSSIBLE"), default=None),
        "open_orders_max": max((e["order"] for e in status.values()
                                if e["status"] == "OPEN"), default=None),
    }
    out = {"summary": summary, "families": [status[i] for i in sorted(status)]}

    # ---- hard invariants: a full run must not regress the phase-2 closures ----
    assert summary["num_impossible"] == 21, \
        f"expected 21 IMPOSSIBLE, got {summary['num_impossible']}"
    assert summary["all_order_ge_9_impossible"] is True, \
        "some order>=9 family is not IMPOSSIBLE"
    assert summary["all_order_ge_12_impossible"] is True
    assert set(summary["open_ids"]) == {0, 1, 2, 3, 4, 5, 7, 9, 10}, summary["open_ids"]
    for sid in (6, 8, 12):
        assert status[sid]["status"] == "IMPOSSIBLE", sid

    with open(os.path.join(RES, "master_status.json"), "w") as f:
        json.dump(out, f, indent=2)

    # console
    print(f"{'id':>3} {'|H|':>4} {'r':>4} {'r9':>3} {'r37':>4} {'status':>11} {'method'}")
    for i in sorted(status):
        e = status[i]
        print(f"{i:>3} {e['order']:>4} {e['r']:>4} {e['reduction_mod9_order']:>3} "
              f"{e['reduction_mod37_order']:>4} {e['status']:>11} {e['method']}")
    print("\nSUMMARY:", json.dumps(summary, indent=2))
    print("\nASSERTIONS PASSED: num_impossible=21, all_order_ge_9_impossible=true")


def _find(sid):
    for name in (f"id{sid}_column.json", f"id{sid}_long.json", f"id{sid}_symbreak.json", f"id{sid}.json"):
        p = os.path.join(RES, "cpsat", name)
        if os.path.exists(p):
            return p
    return None


if __name__ == "__main__":
    main()
