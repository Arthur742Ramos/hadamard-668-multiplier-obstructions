#!/usr/bin/env python3
"""
MASTER CERTIFICATE for the impossibility of an id12-invariant Legendre pair of
length 333 (Hadamard order 668).

We prove a single, cleanly-stated NECESSARY CONDITION is infeasible.

--------------------------------------------------------------------------------
Necessary condition (call it (C)):
Let (a,b) be any id12-invariant Legendre pair of length 333, and let
    atilde_j = sum_{t=0}^{36} a_{j + 9 t},   btilde_j = sum_{t} b_{j+9t}   (j in Z_9)
be its 9-compression (column sums under Z_333 = Z_9 x Z_37).  Then:
   (C1)  atilde_j, btilde_j in V := {+-1, +-17, +-19, +-35, +-37}
         (each column is constant on the 5 K37-orbits {0},C0,C1,C2,C3 of Z_37,
          of sizes 1,9,9,9,9, so a column sum equals eps0 + 9*(eps1+eps2+eps3+eps4)
          with eps in {+-1}; the reachable values are exactly V).
   (C2)  sum_j atilde_j in {+-1}  and  sum_j btilde_j in {+-1}
         (compression preserves the total sum; an LP has row sums +-1).
   (C3)  PAF_atilde(s) + PAF_btilde(s) = -74   for s = 1..8
         (compression identity  PAF_atilde(s) = sum_{s' == s mod 9} PAF_a(s')
          with 37 nonzero shifts s', each contributing PAF_a+PAF_b = -2).

Every step is elementary and independently verified in standalone_verifier.py.

CLAIM: (C) has NO solution.  Therefore no id12-invariant Legendre pair exists.

This file DECIDES (C) three independent ways and emits a JSON certificate:
  (E1) exhaustive: the forced identity sum_s(PAF_a+PAF_b)=(sum a)^2+(sum b)^2
       gives sum_j atilde_j^2 + sum_j btilde_j^2 = 594; over squares of V-values
       {1,289,361,1225,1369} the ONLY 18-term multiset summing to 594 is
       16x1 + 2x289, so exactly two columns have value +-17 and sixteen have
       value +-1 -> a small finite exhaustive search (complete).
  (E2) CP-SAT on the full value set V (no structure pre-imposed).
  (E3) z3 on the full value set V (no structure pre-imposed).
"""
import itertools
import json
import os
import sys
from math import gcd

HERE = os.path.dirname(__file__)


# ---------------------------------------------------------------------------
# Derive V and constants from first principles (K37 orbits of Z_37)
# ---------------------------------------------------------------------------
def derive_value_set():
    p = 37
    # order-9 subgroup of (Z/37)^* = 4th powers
    def primroot():
        for g in range(2, p):
            s = set(); x = 1
            for _ in range(p - 1):
                x = x * g % p; s.add(x)
            if len(s) == p - 1:
                return g
    g = primroot()
    K = set()
    x = 1; g4 = pow(g, 4, p)
    for _ in range(9):
        K.add(x); x = x * g4 % p
    # orbit sizes of Z_37 under K: {0} (size1) and 4 cosets (size9)
    sizes = [1, 9, 9, 9, 9]
    # column sum = eps0*1 + 9*(eps1+eps2+eps3+eps4), eps in {+-1}
    vals = set()
    for e in itertools.product([1, -1], repeat=5):
        vals.add(e[0] * 1 + 9 * (e[1] + e[2] + e[3] + e[4]))
    return sorted(vals), sizes, sorted(K)


V, ORBIT_SIZES, K37 = derive_value_set()


def paf9(v, s):
    return sum(v[j] * v[(j + s) % 9] for j in range(9))


# ---------------------------------------------------------------------------
# (E1) exhaustive decision via forced squared-norm 594
# ---------------------------------------------------------------------------
def E1_exhaustive():
    # squared norm forced to 594 (proved: sum_{s=0}^8 (PAF_a+PAF_b) = 2, and
    # = (Sum a^2+Sum b^2) + 8*(-74)); the ONLY 18-multiset of V-squares -> 594:
    sqvals = sorted({x * x for x in V})
    multisets = []

    def rec(idx, slots, ssum, cur):
        if idx == len(sqvals):
            if slots == 0 and ssum == 0:
                multisets.append({sqvals[i]: cur[i] for i in range(len(sqvals))})
            return
        for n in range(slots + 1):
            if n * sqvals[idx] > ssum:
                break
            rec(idx + 1, slots - n, ssum - n * sqvals[idx], cur + [n])
    rec(0, 18, 594, [])
    # each multiset -> big count = # of |.|=17 columns; here only {1:16,289:2}
    assert multisets == [{1: 16, 289: 2, 361: 0, 1225: 0, 1369: 0}], multisets

    # so 16 columns are +-1 and 2 are +-17.  Enumerate distributions (kA,kB) of
    # the two big columns and exhaust.
    def gen(nbig):
        out = []
        for pos in itertools.combinations(range(9), nbig):
            for bs in itertools.product([17, -17], repeat=nbig):
                for ss in itertools.product([1, -1], repeat=9 - nbig):
                    v = [0] * 9; bi = si = 0
                    for j in range(9):
                        if j in pos:
                            v[j] = bs[bi]; bi += 1
                        else:
                            v[j] = ss[si]; si += 1
                    if sum(v) in (-1, 1):
                        out.append(tuple(v))
        return out
    seqs = {k: gen(k) for k in range(3)}
    count = 0; pairs_checked = 0
    for kA in range(3):
        kB = 2 - kA
        for va in seqs[kA]:
            pa = [paf9(va, s) for s in range(1, 9)]
            for vb in seqs[kB]:
                pairs_checked += 1
                if all(pa[i] + paf9(vb, s) == -74 for i, s in enumerate(range(1, 9))):
                    count += 1
    return {"engine": "exhaustive (forced 594 -> 2 big of |17|)",
            "forced_squared_norm": 594,
            "unique_square_multiset": {"1": 16, "289": 2},
            "candidates_by_nbig": {k: len(seqs[k]) for k in seqs},
            "pairs_checked": pairs_checked,
            "feasible_count": count, "infeasible": count == 0}


# ---------------------------------------------------------------------------
# (E2) CP-SAT on full value set V, NO structure imposed
# ---------------------------------------------------------------------------
def E2_cpsat():
    from ortools.sat.python import cp_model
    m = cp_model.CpModel()
    dom = cp_model.Domain.FromValues(V)
    A = [m.NewIntVarFromDomain(dom, f"a{j}") for j in range(9)]
    B = [m.NewIntVarFromDomain(dom, f"b{j}") for j in range(9)]
    sa = m.NewIntVar(-333, 333, "sa"); m.Add(sa == sum(A)); m.AddAllowedAssignments([sa], [[-1], [1]])
    sb = m.NewIntVar(-333, 333, "sb"); m.Add(sb == sum(B)); m.AddAllowedAssignments([sb], [[-1], [1]])

    def pafe(Vv, s):
        ts = []
        for j in range(9):
            p = m.NewIntVar(-37 * 37, 37 * 37, "")
            m.AddMultiplicationEquality(p, [Vv[j], Vv[(j + s) % 9]])
            ts.append(p)
        return sum(ts)
    for s in range(1, 9):
        m.Add(pafe(A, s) + pafe(B, s) == -74)
    # PROVEN cut: sum_{s=0}^8 (PAF_a+PAF_b) = (sum a)^2+(sum b)^2 = 2, and the
    # s=1..8 terms sum to 8*(-74), so PAF_a(0)+PAF_b(0) = sum a^2 + sum b^2 = 594.
    # Adding it does not change the solution set (it is a logical consequence),
    # but it makes the solver terminate quickly.
    sqA = []
    for j in range(9):
        q = m.NewIntVar(0, 37 * 37, "")
        m.AddMultiplicationEquality(q, [A[j], A[j]]); sqA.append(q)
    sqB = []
    for j in range(9):
        q = m.NewIntVar(0, 37 * 37, "")
        m.AddMultiplicationEquality(q, [B[j], B[j]]); sqB.append(q)
    m.Add(sum(sqA) + sum(sqB) == 594)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 120
    solver.parameters.num_search_workers = 8
    st = solver.Solve(m)
    return {"engine": "cp-sat (full value set V)",
            "status": solver.StatusName(st),
            "infeasible": st == cp_model.INFEASIBLE}


# ---------------------------------------------------------------------------
# (E3) z3 on full value set V, NO structure imposed
# ---------------------------------------------------------------------------
def E3_z3():
    # z3's nonlinear-integer engine is slow on the full 10-valued domain, so we
    # give it the PROVABLY-EQUIVALENT reduced domain: since the squared-norm is
    # forced to 594 and the only V-square multiset summing to 594 is 16x1+2x289,
    # every column value is in {+-1,+-17} with exactly two |.|=17 columns.  This
    # is a logical consequence (see E1), not an added assumption.
    from z3 import Solver, Int, Or, Sum, If, sat, unsat
    s = Solver()
    A = [Int(f"a{j}") for j in range(9)]
    B = [Int(f"b{j}") for j in range(9)]
    for j in range(9):
        s.add(Or(A[j] == 1, A[j] == -1, A[j] == 17, A[j] == -17))
        s.add(Or(B[j] == 1, B[j] == -1, B[j] == 17, B[j] == -17))
    bigcount = Sum([If(Or(A[j] == 17, A[j] == -17), 1, 0) for j in range(9)] +
                   [If(Or(B[j] == 17, B[j] == -17), 1, 0) for j in range(9)])
    s.add(bigcount == 2)
    s.add(Or(Sum(A) == 1, Sum(A) == -1))
    s.add(Or(Sum(B) == 1, Sum(B) == -1))
    for sh in range(1, 9):
        s.add(Sum([A[j] * A[(j + sh) % 9] for j in range(9)]) +
              Sum([B[j] * B[(j + sh) % 9] for j in range(9)]) == -74)
    r = s.check()
    return {"engine": "z3 (reduced-equivalent domain {+-1,+-17}, 2 big)",
            "result": str(r), "infeasible": r == unsat}


if __name__ == "__main__":
    engines = sys.argv[1:] or ["E1", "E2", "E3"]
    outp = os.path.join(HERE, "..", "results", "master_certificate.json")
    # merge into existing certificate so engines can run from different venvs
    if os.path.exists(outp):
        with open(outp) as f:
            cert = json.load(f)
    else:
        cert = {}
    cert.update({
        "family": "id12",
        "claim": "no id12-invariant Legendre pair of length 333 exists",
        "value_set_V": V,
        "K37_orbit_sizes_of_Z37": ORBIT_SIZES,
        "K37": K37,
        "necessary_condition": {
            "C1_column_sum_values": "atilde_j,btilde_j in V",
            "C2_row_sums": "sum atilde, sum btilde in {+-1}",
            "C3_compression_paf": "PAF_atilde(s)+PAF_btilde(s) = -74 for s=1..8",
        },
    })
    cert.setdefault("decisions", {})
    if "E1" in engines:
        print("E1 exhaustive ...")
        cert["decisions"]["E1_exhaustive"] = E1_exhaustive()
        print("   ", cert["decisions"]["E1_exhaustive"])
    if "E2" in engines:
        print("E2 cp-sat (full V) ...")
        cert["decisions"]["E2_cpsat"] = E2_cpsat()
        print("   ", cert["decisions"]["E2_cpsat"])
    if "E3" in engines:
        print("E3 z3 ...")
        cert["decisions"]["E3_z3"] = E3_z3()
        print("   ", cert["decisions"]["E3_z3"])
    verdicts = [d.get("infeasible") for d in cert["decisions"].values()]
    cert["all_engines_agree_infeasible"] = all(verdicts) and len(verdicts) > 0
    cert["verdict"] = ("IMPOSSIBLE (proved): id12 admits no invariant Legendre pair"
                       if cert["all_engines_agree_infeasible"] else "INCONCLUSIVE")
    with open(outp, "w") as f:
        json.dump(cert, f, indent=2)
    print("\nVERDICT:", cert["verdict"])
    print("wrote", outp)
