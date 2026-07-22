#!/usr/bin/env python3
"""
Cheap, rigorous necessary conditions applied to every surviving subgroup family.

(1) ROW-SUM obstruction.  For an H-invariant sequence a the row sum is
        R = sum_O |O| * x_O    (x_O in {+1,-1}).
    A Legendre pair needs R = +/-1.  We test, exactly, whether R = +/-1 is even
    reachable, using a modular-DP over residues (finds a witness modulus m for
    which +/-1 mod m is unreachable) plus a direct reachable-set computation.
    If unreachable, the family admits no invariant LP (certificate: witness m).

(2) 37-COMPRESSION relaxation.  The mod-37 compression a~_j = sum_t a_{j+37 t}
    (j in Z_37) has entries that are ODD integers in [-9,9], is invariant under
    K37 = image of H in (Z/37)^*, has row sum sum_j a~_j = +/-1, and satisfies
        PAF_{a~}(s) + PAF_{b~}(s) = -18   for s = 1..36
    (derived from |A~(k)|^2+|B~(k)|^2 = |A(9k)|^2+|B(9k)|^2 = 668).  Treating the
    per-K37-orbit values as free odd integers is a relaxation; infeasibility of
    the relaxed compressed pair kills the family.

Both are exact finite computations.
"""
import json
import os
import itertools
from math import gcd
from core import (L, KERNEL3, all_subgroups, orbits_on_ZL, reduce_subgroup)
from search_common import subgroup_by_id, load_classification

HERE = os.path.dirname(__file__)


def rowsum_reachable(sizes):
    """Exact: is sum_q sizes[q]*(+/-1) == +/-1 reachable? Return (reachable, witness_modulus)."""
    # witness modulus search (fast certificate of UNreachability)
    witness = None
    for m in range(2, 2 * sum(sizes) + 1):
        cur = {0}
        for s in sizes:
            nxt = set()
            sm = s % m
            for v in cur:
                nxt.add((v + sm) % m)
                nxt.add((v - sm) % m)
            cur = nxt
        if (1 % m) not in cur and ((-1) % m) not in cur:
            witness = m
            return False, witness
        if m > 400:
            break
    # exact reachable set of actual values (bounded DP)
    cur = {0}
    for s in sizes:
        nxt = set()
        for v in cur:
            nxt.add(v + s)
            nxt.add(v - s)
        cur = nxt
    reachable = (1 in cur) or (-1 in cur)
    return reachable, witness


def k_orbits(K, mod):
    seen = [False] * mod
    orbs = []
    for x in range(mod):
        if seen[x]:
            continue
        orb = set()
        stack = [x]
        while stack:
            y = stack.pop()
            if y in orb:
                continue
            orb.add(y)
            for h in K:
                z = (h * y) % mod
                if z not in orb:
                    stack.append(z)
        for y in orb:
            seen[y] = True
        orbs.append(sorted(orb))
    orbs.sort(key=lambda o: (len(o), o[0]))
    return orbs


def compress37_feasible(H, max_enum=6_000_000):
    """Relaxed feasibility of the K37-invariant 37-compression pair.
    Returns dict with feasible flag and stats, or 'skipped' if too large."""
    K = reduce_subgroup(H, 37)
    orbs = k_orbits(K, 37)                 # orbits of Z_37 under K37
    norb = len(orbs)
    idx = [0] * 37
    for oi, o in enumerate(orbs):
        for j in o:
            idx[j] = oi
    sizes = [len(o) for o in orbs]
    # nonzero shift orbits (reps) for PAF condition on Z_37
    nz = [oi for oi in range(norb) if orbs[oi] != [0]]
    reps = [orbs[oi][0] for oi in nz]
    # PAF coeff for compressed length-37 sequence given orbit values v (odd in [-9,9])
    # PAF_{a~}(s) = sum_j a~_j a~_{(j+s)%37}; a~_j = v[idx[j]]
    # Precompute count matrices
    def paf_comp(v, s):
        return sum(v[idx[j]] * v[idx[(j + s) % 37]] for j in range(37))
    odd_vals = [-9, -7, -5, -3, -1, 1, 3, 5, 7, 9]
    est = len(odd_vals) ** norb
    if est > max_enum:
        return {"feasible": None, "reason": f"enum {est} > cap", "num_orbits": norb,
                "orbit_sizes": sizes}
    # enumerate v, filter row sum +/-1, store PAF profile; MITM complement -18
    target = [-18] * len(reps)
    seen = {}
    feasible = False
    example = None
    for combo in itertools.product(odd_vals, repeat=norb):
        rs = sum(sizes[oi] * combo[oi] for oi in range(norb))
        if rs not in (-1, 1):
            continue
        prof = tuple(paf_comp(combo, s) for s in reps)
        comp = tuple(target[i] - prof[i] for i in range(len(reps)))
        if comp in seen:
            feasible = True
            example = (seen[comp], combo)
            break
        if comp == prof:
            feasible = True
            example = (combo, combo)
            break
        if prof not in seen:
            seen[prof] = combo
    return {"feasible": feasible, "num_orbits": norb, "orbit_sizes": sizes,
            "K37_order": len(K), "profiles": len(seen),
            "example": example if feasible else None}


def main():
    cls = load_classification()
    surviving = [r for r in cls["subgroups"] if not r["killed_by_mod37_obstruction"]]
    out = []
    print(f"{'id':>3} {'|H|':>4} {'r':>4} {'rowsumOK':>8} {'witM':>5} "
          f"{'c37feas':>8} {'c37orb':>6}")
    for rec in surviving:
        sid = rec["id"]
        H = frozenset(rec["elements"])
        orbs = orbits_on_ZL(H, L)
        sizes = [len(o) for o in orbs]
        reach, wit = rowsum_reachable(sizes)
        c37 = compress37_feasible(H)
        row = {
            "id": sid, "order": rec["order"], "r": rec["num_orbits"],
            "rowsum_reachable": reach, "rowsum_witness_modulus": wit,
            "killed_by_rowsum": (not reach),
            "compress37": c37,
        }
        out.append(row)
        print(f"{sid:>3} {rec['order']:>4} {rec['num_orbits']:>4} "
              f"{str(reach):>8} {str(wit):>5} {str(c37['feasible']):>8} "
              f"{c37['num_orbits']:>6}")
    with open(os.path.join(HERE, "..", "results", "necessary_conditions.json"), "w") as f:
        json.dump(out, f, indent=2)
    killed_rs = [r["id"] for r in out if r["killed_by_rowsum"]]
    killed_c37 = [r["id"] for r in out if r["compress37"]["feasible"] is False]
    print("\nKILLED by row-sum:", killed_rs)
    print("KILLED by 37-compression relaxation:", killed_c37)


if __name__ == "__main__":
    main()
