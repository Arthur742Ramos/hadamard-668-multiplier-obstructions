#!/usr/bin/env python3
"""mod-9 compression relaxation (rigorous necessary condition).

The mod-9 compression a~_j = sum_{t=0}^{36} a_{j+9t} (j in Z_9) has entries that
are ODD integers in [-37,37], is invariant under K9 = image of H in (Z/9)^*, has
row sum sum_j a~_j = +/-1, and satisfies
    PAF_{a~}(s) + PAF_{b~}(s) = -74   for s = 1..8
(from |A~(k)|^2+|B~(k)|^2 = |A(37k)|^2+|B(37k)|^2 = 668, and (2 - 668)/9 = -74).
Per-K9-orbit values are treated as free odd integers (a relaxation); infeasibility
kills the family.  Only run when the number of K9-orbits keeps enumeration finite.
"""
import json
import os
import sys
import itertools
sys.path.insert(0, os.path.dirname(__file__))
from core import L, reduce_subgroup
from search_common import load_classification, subgroup_by_id
from necessary_conditions import k_orbits


def compress9_feasible(H, cap=3_000_000):
    K = reduce_subgroup(H, 9)
    orbs = k_orbits(K, 9)
    norb = len(orbs)
    idx = [0] * 9
    for oi, o in enumerate(orbs):
        for j in o:
            idx[j] = oi
    sizes = [len(o) for o in orbs]
    nz = [oi for oi in range(norb) if orbs[oi] != [0]]
    reps = [orbs[oi][0] for oi in nz]

    def pafc(v, s):
        return sum(v[idx[j]] * v[idx[(j + s) % 9]] for j in range(9))

    odd = list(range(-37, 38, 2))          # 19 values
    est = len(odd) ** norb
    if est > cap:
        return {"feasible": None, "reason": f"enum {est} > cap", "num_orbits": norb,
                "orbit_sizes": sizes, "K9_order": len(K)}
    target = [-74] * len(reps)
    seen = {}
    feasible = False
    for combo in itertools.product(odd, repeat=norb):
        rs = sum(sizes[oi] * combo[oi] for oi in range(norb))
        if rs not in (-1, 1):
            continue
        prof = tuple(pafc(combo, s) for s in reps)
        comp = tuple(target[i] - prof[i] for i in range(len(reps)))
        if comp in seen or comp == prof:
            feasible = True
            break
        if prof not in seen:
            seen[prof] = combo
    return {"feasible": feasible, "num_orbits": norb, "orbit_sizes": sizes,
            "K9_order": len(K), "profiles": len(seen)}


def main():
    cls = load_classification()
    surviving = [r for r in cls["subgroups"] if not r["killed_by_mod37_obstruction"]]
    out = []
    print(f"{'id':>3} {'|H|':>4} {'r':>4} {'r9':>3} {'c9orb':>6} {'c9feas':>8}")
    for rec in surviving:
        sid = rec["id"]
        H = frozenset(rec["elements"])
        r9 = rec["structure"]["reduction_mod9_order"]
        c9 = compress9_feasible(H)
        out.append({"id": sid, "order": rec["order"], "r": rec["num_orbits"],
                    "reduction_mod9_order": r9, "compress9": c9})
        print(f"{sid:>3} {rec['order']:>4} {rec['num_orbits']:>4} {r9:>3} "
              f"{c9['num_orbits']:>6} {str(c9['feasible']):>8}")
    with open(os.path.join(os.path.dirname(__file__), "..", "results",
                           "compress9.json"), "w") as f:
        json.dump(out, f, indent=2)
    killed = [r["id"] for r in out if r["compress9"]["feasible"] is False]
    print("\nKILLED by 9-compression relaxation:", killed)


if __name__ == "__main__":
    main()
