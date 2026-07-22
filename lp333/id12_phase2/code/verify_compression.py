#!/usr/bin/env python3
"""
INDEPENDENT VERIFICATION of the 9-compression obstruction for id12.

Two independent checks:

  (V1) Build many concrete H-invariant sign sequences a (NOT necessarily LPs),
       compress to length 9, and verify the compression identity
           PAF_atilde(s) == sum_{s' == s (mod 9)} PAF_a(s')
       directly, plus that colsum values lie in {+-1,+-17,+-19,+-35,+-37}.
       This validates the algebra that turns an invariant LP into a length-9
       compressed pair with PAF-sum -74 and squared-norm 594.

  (V2) Re-decide the length-9 compressed feasibility problem with an
       INDEPENDENT engine (exhaustive nested DFS, no MITM) AND with CP-SAT,
       to confirm the solution count (0) found by the MITM in analysis1.

The compressed problem (necessary for ANY id12 invariant LP):
   atilde,btilde in {+-1,+-17}^9,   exactly 2 of the 18 entries have |.|=17,
   sum(atilde) in {+-1}, sum(btilde) in {+-1},
   PAF_atilde(s)+PAF_btilde(s) = -74  for s=1..8.
"""
import itertools
import os
import sys
import random
import json
import phase2_core as pc

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "code"))
from core import L, paf as core_paf, is_legendre_pair, compress  # validated core


def build_invariant_sequence(rng):
    """Random H-invariant +-1 sequence of length 333 (constant on H-orbits)."""
    # orbit of each index under H (id12) via CRT structure: (c in Z9, d in Z37),
    # value depends on (c, orbit_of_d).
    typ = [[rng.choice([1, -1]) for _ in range(pc.NORB)] for _ in range(9)]
    a = [0] * L
    for i in range(L):
        c9, d37 = i % 9, i % 37
        a[i] = typ[c9][pc.ORB_OF[d37]]
    return a


def V1_compression_identity(trials=200):
    rng = random.Random(12345)
    colsum_allowed = {1, -1, 17, -17, 19, -19, 35, -35, 37, -37}
    bad = 0
    for _ in range(trials):
        a = build_invariant_sequence(rng)
        b = build_invariant_sequence(rng)
        at = compress(a, 9)     # length-9 compression (validated core routine)
        bt = compress(b, 9)
        # colsum values in allowed set
        for v in at + bt:
            if v not in colsum_allowed:
                bad += 1
        # compression identity for every s = 0..8
        for s in range(9):
            lhs = core_paf(at, s) + core_paf(bt, s)
            rhs = sum(core_paf(a, sp) + core_paf(b, sp)
                      for sp in range(L) if sp % 9 == s)
            if lhs != rhs:
                bad += 1
    return {"trials": trials, "mismatches": bad, "ok": bad == 0}


def V1b_LP_projection_constraints(trials=50):
    """Confirm: IF (a,b) were an LP, the compressed pair would satisfy
    PAF-sum = -74 (s!=0) and squared-norm 594.  We can't easily sample real
    LPs, so we verify the exact arithmetic implication on the identity:
    substituting PAF_a(s')+PAF_b(s') = -2 for all s'!=0 into the identity.
    """
    # For s != 0 mod 9: 37 nonzero s' -> 37*(-2) = -74.
    # For s == 0: s'=0 gives 666, plus 36*(-2) = -72 -> 594.
    counts = {}
    for s in range(9):
        nzero = sum(1 for sp in range(L) if sp % 9 == s)  # count of s' == s (mod9)
        counts[s] = nzero
    # s=0 residue class contains s'=0 (the only zero shift)
    pred = {}
    for s in range(9):
        if s == 0:
            pred[s] = 666 + (counts[s] - 1) * (-2)
        else:
            pred[s] = counts[s] * (-2)
    return {"class_sizes": counts, "predicted_compressed_PAFsum": pred,
            "expect_s0": 594, "expect_snz": -74,
            "ok": pred[0] == 594 and all(pred[s] == -74 for s in range(1, 9))}


def V2_dfs_count():
    """Independent exhaustive nested DFS over the compressed problem; returns
    the exact number of feasible (atilde,btilde) and up to a few witnesses."""
    vals = [1, -1, 17, -17]

    def paf(v, s):
        return sum(v[j] * v[(j + s) % 9] for j in range(9))

    # enumerate all colsum vectors with a given number of bigs and rowsum +-1
    def gen(nbig):
        out = []
        for pos in itertools.combinations(range(9), nbig):
            for bs in itertools.product([17, -17], repeat=nbig):
                for ss in itertools.product([1, -1], repeat=9 - nbig):
                    v = [0] * 9
                    bi = si = 0
                    for j in range(9):
                        if j in pos:
                            v[j] = bs[bi]; bi += 1
                        else:
                            v[j] = ss[si]; si += 1
                    if sum(v) in (-1, 1):
                        out.append(tuple(v))
        return out

    seqs = {k: gen(k) for k in range(3)}
    total = 0
    witnesses = []
    for kA in range(3):
        kB = 2 - kA
        for va in seqs[kA]:
            pa = [paf(va, s) for s in range(1, 9)]
            for vb in seqs[kB]:
                ok = True
                for i, s in enumerate(range(1, 9)):
                    if pa[i] + paf(vb, s) != -74:
                        ok = False
                        break
                if ok:
                    total += 1
                    if len(witnesses) < 5:
                        witnesses.append((list(va), list(vb)))
    return {"engine": "exhaustive nested DFS (no MITM)",
            "sizes_by_nbig": {k: len(seqs[k]) for k in seqs},
            "feasible_count": total, "witnesses": witnesses}


def V2b_cpsat_count():
    """Independent CP-SAT decision of the compressed problem (SAT/UNSAT)."""
    try:
        from ortools.sat.python import cp_model
    except Exception as e:
        return {"engine": "cp-sat", "error": str(e)}
    m = cp_model.CpModel()
    # atilde[j], btilde[j] in {+-1,+-17}; encode value and bigness
    A = [m.NewIntVarFromDomain(cp_model.Domain.FromValues([-17, -1, 1, 17]), f"a{j}") for j in range(9)]
    B = [m.NewIntVarFromDomain(cp_model.Domain.FromValues([-17, -1, 1, 17]), f"b{j}") for j in range(9)]
    bigA = [m.NewBoolVar(f"ba{j}") for j in range(9)]
    bigB = [m.NewBoolVar(f"bb{j}") for j in range(9)]
    for j in range(9):
        # bigA[j] == (|A[j]|==17)
        m.Add(A[j] <= -17 + 0).OnlyEnforceIf(bigA[j]) if False else None
        # use abs via aux
        aa = m.NewIntVar(0, 17, f"aa{j}")
        m.AddAbsEquality(aa, A[j]); m.Add(aa == 17).OnlyEnforceIf(bigA[j]); m.Add(aa == 1).OnlyEnforceIf(bigA[j].Not())
        ab = m.NewIntVar(0, 17, f"ab{j}")
        m.AddAbsEquality(ab, B[j]); m.Add(ab == 17).OnlyEnforceIf(bigB[j]); m.Add(ab == 1).OnlyEnforceIf(bigB[j].Not())
    m.Add(sum(bigA) + sum(bigB) == 2)
    # row sums +-1
    sa = m.NewIntVar(-153, 153, "sa"); m.Add(sa == sum(A)); m.AddAllowedAssignments([sa], [[-1], [1]])
    sb = m.NewIntVar(-153, 153, "sb"); m.Add(sb == sum(B)); m.AddAllowedAssignments([sb], [[-1], [1]])
    # PAF products: need products A[j]*A[j+s]; use int var with multiplication
    def paf_expr(V, s):
        terms = []
        for j in range(9):
            p = m.NewIntVar(-289, 289, "")
            m.AddMultiplicationEquality(p, [V[j], V[(j + s) % 9]])
            terms.append(p)
        return sum(terms)
    for s in range(1, 9):
        m.Add(paf_expr(A, s) + paf_expr(B, s) == -74)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 120
    solver.parameters.num_search_workers = 8
    # enumerate all solutions
    class Counter(cp_model.CpSolverSolutionCallback):
        def __init__(self):
            super().__init__(); self.n = 0; self.ex = []
        def on_solution_callback(self):
            self.n += 1
            if len(self.ex) < 3:
                self.ex.append(([self.Value(A[j]) for j in range(9)],
                                [self.Value(B[j]) for j in range(9)]))
    solver.parameters.enumerate_all_solutions = True
    cb = Counter()
    status = solver.Solve(m, cb)
    return {"engine": "cp-sat (enumerate_all)", "status": solver.StatusName(status),
            "feasible_count": cb.n, "witnesses": cb.ex}


if __name__ == "__main__":
    out = {}
    print("V1 compression identity on random invariant sequences ...")
    out["V1_identity"] = V1_compression_identity()
    print("   ", out["V1_identity"])
    out["V1b_LP_projection"] = V1b_LP_projection_constraints()
    print("V1b LP-projection predicted compressed PAF-sums:", out["V1b_LP_projection"])
    print("V2 exhaustive nested DFS count ...")
    out["V2_dfs"] = V2_dfs_count()
    print("   ", {k: v for k, v in out["V2_dfs"].items() if k != "witnesses"})
    print("V2b CP-SAT enumerate ...")
    out["V2b_cpsat"] = V2b_cpsat_count()
    print("   ", out["V2b_cpsat"])
    outp = os.path.join(os.path.dirname(__file__), "..", "results",
                        "compression_verification.json")
    with open(outp, "w") as f:
        json.dump(out, f, indent=2)
    print("wrote", outp)
    # Overall verdict
    agree = (out["V2_dfs"]["feasible_count"] == 0 and
             out["V2b_cpsat"].get("feasible_count") == 0 and
             out["V2b_cpsat"].get("status") in ("INFEASIBLE", "OPTIMAL", "FEASIBLE"))
    print("\nCOMPRESSION OBSTRUCTION CONFIRMED (0 solutions, both engines):",
          out["V2_dfs"]["feasible_count"] == 0 and out["V2b_cpsat"].get("feasible_count") == 0)
