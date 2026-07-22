#!/usr/bin/env python3
"""
Classify every subgroup H <= (Z/333)^* that is compatible with the mod-3
obstruction (H <= kernel of reduction mod 3, order 108), record its reductions,
the mod-37 obstruction status, and its orbit structure on Z_333.
Writes lp333/results/subgroup_classification.json
"""
import json
import os
from collections import Counter
from core import (L, KERNEL3, all_subgroups, orbits_on_ZL, orbit_signature,
                  reduce_subgroup, surjects_onto, units, mult_order)

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "..", "results", "subgroup_classification.json")


def group_structure(H, mod=L):
    """Invariant factors via reductions to the two prime-power components."""
    p9 = sorted(reduce_subgroup(H, 9))
    p37 = sorted(reduce_subgroup(H, 37))
    return {
        "order": len(H),
        "reduction_mod9": p9,
        "reduction_mod9_order": len(p9),
        "reduction_mod37_order": len(p37),
        "reduction_mod37": p37,
    }


def canonical_gens(H, mod=L):
    """A small generating set (for reproducibility)."""
    from core import generated_subgroup
    elems = sorted(H)
    gens = []
    cur = frozenset({1})
    for u in elems:
        if u in cur:
            continue
        gens.append(u)
        cur = generated_subgroup(gens, mod)
        if len(cur) == len(H):
            break
    return gens


def main():
    subs = list(all_subgroups(KERNEL3, L))
    # order by (order, then reduction sizes) for a stable presentation
    records = []
    for H in subs:
        orbs = orbits_on_ZL(H, L)
        sig = orbit_signature(orbs)
        nonzero_orbits = [o for o in orbs if o != [0]]
        st = group_structure(H)
        surj37 = surjects_onto(H, 37)
        surj9 = reduce_subgroup(H, 9) == frozenset(units(9))  # can never be true
        rec = {
            "order": len(H),
            "generators": canonical_gens(H),
            "structure": st,
            "num_orbits": len(orbs),
            "num_nonzero_orbits": len(nonzero_orbits),
            "orbit_signature": [list(t) for t in sig],
            "mod37_full_reduction": surj37,
            "mod9_full_reduction": surj9,
            "killed_by_mod37_obstruction": surj37,
        }
        records.append((H, rec))

    records.sort(key=lambda r: (r[1]["order"],
                                r[1]["structure"]["reduction_mod37_order"],
                                r[1]["structure"]["reduction_mod9_order"]))

    out = []
    for idx, (H, rec) in enumerate(records):
        rec["id"] = idx
        rec["elements"] = sorted(H)
        out.append(rec)

    # Summary tallies
    killed = [r for r in out if r["killed_by_mod37_obstruction"]]
    surviving = [r for r in out if not r["killed_by_mod37_obstruction"]]
    summary = {
        "L": L,
        "hadamard_order": 668,
        "num_units_mod333": 216,
        "num_kernel_mod3": len(KERNEL3),
        "num_subgroups_of_kernel_mod3": len(out),
        "num_killed_by_mod37": len(killed),
        "num_surviving": len(surviving),
        "killed_ids": [r["id"] for r in killed],
        "surviving_ids": [r["id"] for r in surviving],
        "surviving_orbit_counts": {r["id"]: r["num_orbits"] for r in surviving},
    }

    payload = {"summary": summary, "subgroups": out}
    with open(OUT, "w") as f:
        json.dump(payload, f, indent=2)

    # Console table
    print(f"{'id':>3} {'|H|':>4} {'r9':>3} {'r37':>4} {'#orb':>5} {'#nz':>5} "
          f"{'mod37KILL':>9}  sig")
    for r in out:
        st = r["structure"]
        print(f"{r['id']:>3} {r['order']:>4} {st['reduction_mod9_order']:>3} "
              f"{st['reduction_mod37_order']:>4} {r['num_orbits']:>5} "
              f"{r['num_nonzero_orbits']:>5} {str(r['killed_by_mod37_obstruction']):>9}  "
              f"{r['orbit_signature']}")
    print()
    print("SUMMARY:", json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
