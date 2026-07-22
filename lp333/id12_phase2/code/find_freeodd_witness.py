#!/usr/bin/env python3
"""
Free-odd witness for the weak 9-compression relaxation (column sums treated as
free odd integers): atilde,btilde with odd entries in [-37,37], row sums +-1,
PAF_atilde(s)+PAF_btilde(s) = -74 for s=1..8 (squared norm 594 is then forced).

A witness proves the relaxation is FEASIBLE, so the families id0 (trivial group)
and id1 (order 2) -- whose column-sum value set is ALL odd integers -- are
genuinely NOT closed by the 9-compression, as opposed to merely undecided.

This script (1) verifies the CANONICAL witness (identical to the constant
embedded in general_verifier.py) deterministically, and (2) INDEPENDENTLY
confirms feasibility with CP-SAT (which may return any valid witness).  It writes
the deterministic canonical witness to results/freeodd_relaxation_witness.json.
"""
import json
import os

# Canonical witness (must match general_verifier.FREE_ODD_WITNESS).
CANONICAL = ([-21, 1, 5, 1, 1, 5, 5, 1, 3],
             [-3, 5, -1, -3, 1, -3, 3, -1, 1])


def paf(v, s):
    return sum(v[j] * v[(j + s) % 9] for j in range(9))


def verify(a, b):
    return (all(x % 2 for x in a + b) and sum(a) in (-1, 1) and sum(b) in (-1, 1)
            and sum(x * x for x in a) + sum(x * x for x in b) == 594
            and all(paf(a, s) + paf(b, s) == -74 for s in range(1, 9)))


def cpsat_confirm(time_s=120):
    try:
        from ortools.sat.python import cp_model
    except Exception as e:
        return {"engine": "cp-sat", "error": str(e)}
    m = cp_model.CpModel()
    odd = [v for v in range(-37, 38) if v % 2]
    dom = cp_model.Domain.FromValues(odd)
    A = [m.NewIntVarFromDomain(dom, f"a{j}") for j in range(9)]
    B = [m.NewIntVarFromDomain(dom, f"b{j}") for j in range(9)]
    sa = m.NewIntVar(-333, 333, ""); m.Add(sa == sum(A)); m.AddAllowedAssignments([sa], [[-1], [1]])
    sb = m.NewIntVar(-333, 333, ""); m.Add(sb == sum(B)); m.AddAllowedAssignments([sb], [[-1], [1]])

    def pe(V, s):
        t = []
        for j in range(9):
            p = m.NewIntVar(-1369, 1369, ""); m.AddMultiplicationEquality(p, [V[j], V[(j + s) % 9]]); t.append(p)
        return sum(t)
    for s in range(1, 9):
        m.Add(pe(A, s) + pe(B, s) == -74)
    sqs = []
    for X in (A, B):
        for j in range(9):
            q = m.NewIntVar(0, 1369, ""); m.AddMultiplicationEquality(q, [X[j], X[j]]); sqs.append(q)
    m.Add(sum(sqs) == 594)
    sol = cp_model.CpSolver(); sol.parameters.max_time_in_seconds = time_s
    sol.parameters.num_search_workers = 8
    st = sol.Solve(m)
    r = {"engine": "cp-sat", "status": sol.StatusName(st)}
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        a = [sol.Value(A[j]) for j in range(9)]; b = [sol.Value(B[j]) for j in range(9)]
        r.update(found_some_witness=True, atilde=a, btilde=b, verified=verify(a, b))
    return r


def main():
    a, b = CANONICAL
    ok = verify(a, b)
    print("canonical free-odd witness verified:", ok, "->", a, b)
    assert ok, "canonical witness invalid"
    out = {"status": "OPTIMAL", "feasible": True,
           "atilde": a, "btilde": b, "rowsums": [sum(a), sum(b)],
           "squared_norm": sum(x * x for x in a) + sum(x * x for x in b),
           "PAFsum": [paf(a, s) + paf(b, s) for s in range(1, 9)],
           "verified": ok,
           "note": "Deterministic canonical witness (matches "
                   "general_verifier.FREE_ODD_WITNESS). Proves the free-odd "
                   "9-compression relaxation is feasible; id0/id1 NOT closed."}
    import sys
    if "--cpsat" in sys.argv:
        out["cpsat_independent_confirmation"] = cpsat_confirm()
        print("cp-sat independent confirmation:", out["cpsat_independent_confirmation"].get("status"))
    outp = os.path.join(os.path.dirname(__file__), "..", "results",
                        "freeodd_relaxation_witness.json")
    json.dump(out, open(outp, "w"), indent=2)
    print("wrote", outp)


if __name__ == "__main__":
    main()
