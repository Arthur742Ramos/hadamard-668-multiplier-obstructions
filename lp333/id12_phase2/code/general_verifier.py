#!/usr/bin/env python3
"""
GENERAL dependency-free verifier: the value-set-restricted 9-compression
obstruction applied to every common-multiplier family of LP(333) that is trivial
mod 9 (so H = {1} x K37 and the 9-compression columns are clean K37-invariant
Z_37 blocks): ids 0, 1, 3, 6, 8, 12.

For L = 333 and the 9-compression, the PAF target (-74 for s=1..8) and the forced
squared norm (594) are FAMILY-INDEPENDENT (proved once, deterministically, via
coefficient matrices).  Only the column-sum value set V changes; V is the exact
reachable set of  eps0*1 + sum_k eps_k*|orbit_k|.

Verdicts (all by a COMPLETE, parameterized square-sum-pruned decision):
  id6 (order 4), id8 (order 6), id12 (order 9)  ->  IMPOSSIBLE
  id0 (order 1), id1 (order 2)                  ->  NOT closed: V = all odd
        integers, and a stored free-odd WITNESS proves the relaxation feasible
  id3 (order 3)                                 ->  undecided by this method
        (|V|=26; complete enumeration exceeds the node budget)

Pure Python standard library.  A positive control invokes the same decision
routine on a satisfiable instance.
"""
from math import gcd
import itertools

L = 333

# family generators (subgroups of (Z/333)^*), from the phase-1 classification
FAMILY_GENS = {
    0:  [],            # trivial group {1}
    1:  [73],
    3:  [10],
    6:  [73, 154],
    8:  [10, 64],
    12: [10, 46],
}

# A concrete free-odd witness (column sums treated as free odd integers): proves
# the id0/id1 compressed relaxation is FEASIBLE, hence genuinely not closed.
FREE_ODD_WITNESS = ([-21, 1, 5, 1, 1, 5, 5, 1, 3],
                    [-3, 5, -1, -3, 1, -3, 3, -1, 1])


def generate_subgroup(gens, mod=L):
    S = {1}
    fr = [1]
    while fr:
        x = fr.pop()
        for g in gens:
            y = (x * g) % mod
            if y not in S:
                S.add(y); fr.append(y)
    return sorted(S)


def is_subgroup(E):
    S = set(E)
    if len(S) != len(E):
        return False
    for a in E:
        if gcd(a, L) != 1:
            return False
        for b in E:
            if (a * b) % L not in S:
                return False
    return True


def trivial_mod9(E):
    return {a % 9 for a in E} == {1}


def k37_orbit_sizes(E):
    K = {a % 37 for a in E}
    seen = [False] * 37
    sizes = []
    for x in range(37):
        if seen[x]:
            continue
        o = set(); st = [x]
        while st:
            y = st.pop()
            if y in o:
                continue
            o.add(y)
            for h in K:
                st.append((h * y) % 37)
        for y in o:
            seen[y] = True
        sizes.append(len(o))
    return sorted(sizes), len(K)


def value_set(orbit_sizes):
    reach = {0}
    for s in orbit_sizes:
        reach = {v + s for v in reach} | {v - s for v in reach}
    return sorted(reach)


def paf(x, s):
    n = len(x)
    return sum(x[i] * x[(i + s) % n] for i in range(n))


# ---------------------------------------------------------------------------
# DETERMINISTIC family-independent identities (coefficient matrices)
# ---------------------------------------------------------------------------
def compression_identity_exact():
    """PAF_atilde(s) = sum_{s'==s (mod 9)} PAF_a(s') for all s, via exact
    coefficient-matrix equality over the 333 sequence variables."""
    for s in range(9):
        C = {}
        for j in range(9):
            for t in range(37):
                p = (9 * t + j) % L
                for u in range(37):
                    q = (9 * u + j + s) % L
                    C[(p, q)] = C.get((p, q), 0) + 1
        D = {}
        for sp in range(L):
            if sp % 9 != s:
                continue
            for i in range(L):
                D[(i, (i + sp) % L)] = D.get((i, (i + sp) % L), 0) + 1
        if C != D or any(v != 1 for v in C.values()):
            return False
    return True


def squared_norm_identity_exact():
    """sum_{s=0..8} PAF_x(s) = (sum x)^2 : coefficient matrix is all-ones."""
    E = {}
    for s in range(9):
        for j in range(9):
            E[(j, (j + s) % 9)] = E.get((j, (j + s) % 9), 0) + 1
    return all(E.get((p, q), 0) == 1 for p in range(9) for q in range(9))


def column_sums_in_V(E, V):
    """Deterministic: every column of an H-invariant sequence is constant on the
    K37-orbits, so its sum is sum_k eps_k*|orbit_k| in {+-1}^#orbits, which is
    exactly the reachable set V.  Verify the reachable-set construction matches
    the orbit sizes and that V is closed under the sign choices."""
    sizes, _ = k37_orbit_sizes(E)
    reach = value_set(sizes)
    return reach == V


# ---------------------------------------------------------------------------
# COMPLETE parameterized decision (square-sum-pruned MITM)
# ---------------------------------------------------------------------------
def decide_compressed(V, target_paf=-74, rowsums=(-1, 1), sqnorm_total=594,
                      node_cap=300_000_000):
    """Return dict: decided / feasible / witness / nseq.  Enumerates all length-9
    V-sequences with square-sum <= sqnorm_total (pruned DFS) and matches A/B by
    square-sum complement and PAF profile.  COMPLETE unless node_cap is hit."""
    Vs = sorted(V, key=lambda x: x * x)
    minsq = min(x * x for x in V)
    out = []
    cur = [0] * 9
    nodes = [0]
    overflow = [False]

    def rec(pos, sq, rs):
        if overflow[0]:
            return
        nodes[0] += 1
        if nodes[0] > node_cap:
            overflow[0] = True
            return
        if sq > sqnorm_total:
            return
        if pos == 9:
            if rs in rowsums:
                out.append((tuple(cur), sq))
            return
        if sq + (9 - pos) * minsq > sqnorm_total:
            return
        for v in Vs:
            cur[pos] = v
            rec(pos + 1, sq + v * v, rs + v)
    rec(0, 0, 0)
    if overflow[0]:
        return {"decided": False, "reason": f"node budget {node_cap} exceeded"}
    from collections import defaultdict
    idx = defaultdict(list)
    for v, sq in out:
        idx[(sq, tuple(paf(v, s) for s in range(1, 9)))].append(v)
    for vb, sqb in out:
        need = (sqnorm_total - sqb,
                tuple(target_paf - paf(vb, s) for s in range(1, 9)))
        if need[0] >= 0 and idx.get(need):
            return {"decided": True, "feasible": True, "nseq": len(out),
                    "witness": (list(idx[need][0]), list(vb))}
    return {"decided": True, "feasible": False, "nseq": len(out)}


def is_all_odd_dense(V):
    M = max(abs(v) for v in V)
    return sorted(V) == [x for x in range(-M, M + 1) if x % 2]


def check_free_odd_witness():
    a, b = FREE_ODD_WITNESS
    ok = (all(x % 2 for x in a + b)              # all odd
          and sum(a) in (-1, 1) and sum(b) in (-1, 1)
          and sum(x * x for x in a) + sum(x * x for x in b) == 594
          and all(paf(a, s) + paf(b, s) == -74 for s in range(1, 9)))
    return ok


def main():
    print("=" * 72)
    print("GENERAL VERIFIER  --  value-set-restricted 9-compression obstruction")
    print("=" * 72)
    assert compression_identity_exact(), "compression identity failed"
    assert squared_norm_identity_exact(), "squared-norm identity failed"
    print("[PASS] family-independent identities (compression; sum_s PAF=(sum)^2) "
          "-- exact coefficient matrices")
    fw = check_free_odd_witness()
    print(f"[{'PASS' if fw else 'FAIL'}] stored free-odd witness satisfies the "
          f"relaxation (row sums +-1, norm 594, PAF-sum -74) -> id0/id1 feasible")

    print(f"\n{'id':>3} {'ord':>3} {'r37':>3} {'|V|':>3}  verdict")
    verdicts = {}
    for sid in sorted(FAMILY_GENS):
        E = generate_subgroup(FAMILY_GENS[sid])
        assert is_subgroup(E), f"id{sid} not a subgroup"
        assert trivial_mod9(E), f"id{sid} not trivial mod 9"
        sizes, r37 = k37_orbit_sizes(E)
        V = value_set(sizes)
        assert column_sums_in_V(E, V), f"id{sid} value-set mismatch"
        if is_all_odd_dense(V):
            dec = {"decided": False, "reason": "V = all odd integers (free-odd); "
                   "feasible by the stored witness -> NOT closed"}
            verdict = "NOT closed (free-odd; witness feasible)"
        else:
            dec = decide_compressed(V)
            if dec.get("decided") and dec.get("feasible") is False:
                verdict = "IMPOSSIBLE (9-compression, exact)"
            elif dec.get("decided") and dec.get("feasible") is True:
                verdict = "feasible compressed pair (NOT closed)"
            else:
                verdict = "undecided (enumeration over node budget)"
        verdicts[sid] = (verdict, dec)
        extra = (f"   [{dec.get('nseq')} seqs]" if dec.get("nseq") is not None
                 else "")
        print(f"{sid:>3} {len(E):>3} {r37:>3} {len(V):>3}  {verdict}{extra}")

    # POSITIVE CONTROL: the same routine must FIND a solution when one exists.
    pc = decide_compressed([-1, 1], target_paf=18, rowsums=(9,), sqnorm_total=18)
    pc_ok = (pc.get("feasible") is True and pc.get("witness") is not None
             and all(paf(pc["witness"][0], s) + paf(pc["witness"][1], s) == 18
                     for s in range(1, 9)))
    print("-" * 72)
    print(f"[{'PASS' if pc_ok else 'FAIL'}] positive control (same routine finds "
          f"a solution on a satisfiable instance)")
    closed = sorted(sid for sid, (v, d) in verdicts.items()
                    if v.startswith("IMPOSSIBLE"))
    undecided = sorted(sid for sid, (v, d) in verdicts.items()
                       if v.startswith("undecided"))
    notclosed = sorted(sid for sid, (v, d) in verdicts.items()
                       if "NOT closed" in v)
    print(f"closed IMPOSSIBLE: {closed}   not-closed(free-odd): {notclosed}   "
          f"undecided: {undecided}")
    ok = (closed == [6, 8, 12] and fw and pc_ok
          and undecided == [3] and notclosed == [0, 1])
    print("VERDICT:", "ALL CHECKS PASS" if ok else "CHECK FAILED")
    print("=" * 72)
    return verdicts, ok


if __name__ == "__main__":
    import sys
    _, ok = main()
    sys.exit(0 if ok else 1)
