#!/usr/bin/env python3
"""
Structural analysis of id12 (Phase 2), step 1.

Establishes and certifies:
  (L1) The 9-compression squared-norm identity forces EXACTLY 2 "big" columns
       (|colsum|=17) and 16 "small" columns (|colsum|=1) among the 18 columns.
  (L2) The per-sequence row-sum = +-1 forces the big columns to split (2,0):
       one sequence has one +17 and one -17 big column plus 7 small; the other
       sequence is all-small.  The (1,1) split is impossible.
  (S)  The COMPLETE solution set of the length-9 compression relaxation
       (column-sum vectors), used to bound big-column placement.

All exact integer arithmetic.
"""
import json
import os
import itertools
import phase2_core as pc

OUT = os.path.join(os.path.dirname(__file__), "..", "results")
os.makedirs(OUT, exist_ok=True)


def lemma_L1_L2():
    """Certify the (2,0) big/small structure by exhaustive reasoning over the
    per-column colsum values (which are fully determined by type)."""
    colsum_vals = sorted(set(pc.COLSUM))
    # (L1) only multiset of 18 squares summing to 594 is 16*(1)+2*(289)
    squares = {}
    from itertools import combinations_with_replacement
    sols = []

    def rec(vals, idx, slots, ssum, cur):
        if idx == len(vals):
            if slots == 0 and ssum == 0:
                sols.append(dict(cur))
            return
        v = vals[idx]
        for n in range(slots + 1):
            if n * v > ssum:
                break
            rec(vals, idx + 1, slots - n, ssum - n * v, cur + [(v, n)])
    sqvals = sorted({c * c for c in colsum_vals})
    rec(sqvals, 0, 18, 594, [])
    L1_solutions = [{k: v for k, v in s.items() if v} for s in sols]
    assert L1_solutions == [{1: 16, 289: 2}], L1_solutions

    # (L2) per sequence row sum parity: a sequence with k big columns (|sum|=17)
    # and (9-k) small (|sum|=1) has row sum = (sum of k values +-17) +
    # (sum of 9-k values +-1).  Determine which k in {0,1,2} can yield +-1, and
    # what big-sign multiset is required.
    per_seq = {}
    for k in range(0, 3):
        reachable = set()
        big_signmultisets = set()
        # big contributions: each +-17 ; small: each +-1
        for bigs in itertools.product([17, -17], repeat=k):
            for smalls in itertools.product([1, -1], repeat=9 - k):
                rs = sum(bigs) + sum(smalls)
                if rs in (-1, 1):
                    reachable.add(rs)
                    big_signmultisets.add(tuple(sorted(bigs)))
        per_seq[k] = {"rowsum_pm1_reachable": bool(reachable),
                      "big_sign_multisets": sorted(big_signmultisets)}
    # With exactly 2 big total, the distribution over (A,B) is (2,0),(1,1),(0,2).
    # Feasible iff each sequence's big-count allows row sum +-1.
    feasible_splits = []
    for kA in range(3):
        kB = 2 - kA
        if per_seq[kA]["rowsum_pm1_reachable"] and per_seq[kB]["rowsum_pm1_reachable"]:
            feasible_splits.append((kA, kB))
    return {
        "L1_multiset_solutions_squares_to_594": L1_solutions,
        "L1_conclusion": "exactly 2 columns have |colsum|=17, 16 have |colsum|=1",
        "per_seq_rowsum_analysis": {str(k): per_seq[k] for k in per_seq},
        "feasible_big_splits_(kA,kB)": feasible_splits,
        "L2_conclusion": ("only (2,0)/(0,2) feasible; each big pair must be "
                          "one +17 and one -17; (1,1) impossible"),
    }


def compression_solution_set():
    """Enumerate ALL length-9 compressed column-sum pairs (atilde, btilde) with
    entries in {+-1,+-17}, exactly 2 entries of |.|=17 across both, per-sequence
    row sums +-1, and PAF_atilde(s)+PAF_btilde(s) = -74 for s=1..8.

    (This is the exact 9-compression relaxation; every genuine invariant LP of
    this family projects to one of these.)  We return the count and a few stats,
    plus whether all solutions obey the (2,0) split (cross-check of L2).
    """
    vals = [1, -1, 17, -17]

    def paf(v, s):
        return sum(v[j] * v[(j + s) % 9] for j in range(9))

    # enumerate one sequence's colsum vector with 0,1, or 2 bigs
    def gen_seq(nbig):
        # positions of bigs
        for pos in itertools.combinations(range(9), nbig):
            for bigsigns in itertools.product([17, -17], repeat=nbig):
                for smallsigns in itertools.product([1, -1], repeat=9 - nbig):
                    v = [0] * 9
                    si = 0
                    bi = 0
                    for j in range(9):
                        if j in pos:
                            v[j] = bigsigns[bi]; bi += 1
                        else:
                            v[j] = smallsigns[si]; si += 1
                    if sum(v) in (-1, 1):
                        yield tuple(v)

    # Build MITM: total bigs must be exactly 2.
    # For each split (kA,kB) in {(0,2),(1,1),(2,0)}, match PAF profiles to -74.
    target = [-74] * 8
    solutions = 0
    split_counts = {}
    examples = []
    # Precompute B-side profiles per nbig
    seqs_by_big = {k: list(gen_seq(k)) for k in range(3)}
    profiles_by_big = {}
    for k in range(3):
        prof = {}
        for v in seqs_by_big[k]:
            p = tuple(paf(v, s) for s in range(1, 9))
            prof.setdefault(p, []).append(v)
        profiles_by_big[k] = prof

    for kA in range(3):
        kB = 2 - kA
        cntsplit = 0
        for va in seqs_by_big[kA]:
            pa = tuple(paf(va, s) for s in range(1, 9))
            need = tuple(target[i] - pa[i] for i in range(8))
            if need in profiles_by_big[kB]:
                matches = profiles_by_big[kB][need]
                cntsplit += len(matches)
                if len(examples) < 6:
                    examples.append({"kA": kA, "kB": kB, "atilde": list(va),
                                     "btilde": list(matches[0])})
        split_counts[f"{kA},{kB}"] = cntsplit
        solutions += cntsplit
    return {
        "total_compression_solutions": solutions,
        "by_split_(kA,kB)": split_counts,
        "examples": examples,
        "note": ("row-sum split respects L2 iff (1,1) count == 0"),
    }


if __name__ == "__main__":
    res = {}
    res["structure_lemmas"] = lemma_L1_L2()
    print("=== L1/L2 structural lemmas ===")
    print(json.dumps(res["structure_lemmas"], indent=2))
    print("\n=== compression relaxation solution set ===")
    cs = compression_solution_set()
    res["compression_solution_set"] = cs
    print(json.dumps({k: v for k, v in cs.items() if k != "examples"}, indent=2))
    print("examples:", json.dumps(cs["examples"][:3], indent=2))
    with open(os.path.join(OUT, "structure_analysis.json"), "w") as f:
        json.dump(res, f, indent=2)
    print("\nwrote results/structure_analysis.json")
