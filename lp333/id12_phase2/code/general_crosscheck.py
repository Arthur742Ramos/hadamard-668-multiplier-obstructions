#!/usr/bin/env python3
"""
Independent CP-SAT / z3 cross-checks of the value-set-restricted 9-compression
obstruction for the trivial-mod-9 families id6, id8, id12 (and confirmation that
id0, id1 are NOT closed by it).  Parameterized by the family's column-sum value
set V.  Uses the PROVEN cut squared-norm = 594.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "code"))
import general_compression as gc
from search_common import subgroup_by_id
from core import reduce_subgroup


def cpsat_decide(V):
    from ortools.sat.python import cp_model
    m = cp_model.CpModel()
    dom = cp_model.Domain.FromValues(V)
    A = [m.NewIntVarFromDomain(dom, f"a{j}") for j in range(9)]
    B = [m.NewIntVarFromDomain(dom, f"b{j}") for j in range(9)]
    sa = m.NewIntVar(-9 * 37, 9 * 37, "sa"); m.Add(sa == sum(A)); m.AddAllowedAssignments([sa], [[-1], [1]])
    sb = m.NewIntVar(-9 * 37, 9 * 37, "sb"); m.Add(sb == sum(B)); m.AddAllowedAssignments([sb], [[-1], [1]])

    def paf(Vv, s):
        ts = []
        for j in range(9):
            p = m.NewIntVar(-37 * 37, 37 * 37, "")
            m.AddMultiplicationEquality(p, [Vv[j], Vv[(j + s) % 9]]); ts.append(p)
        return sum(ts)
    for s in range(1, 9):
        m.Add(paf(A, s) + paf(B, s) == -74)
    sq = []
    for X in (A, B):
        for j in range(9):
            q = m.NewIntVar(0, 37 * 37, ""); m.AddMultiplicationEquality(q, [X[j], X[j]]); sq.append(q)
    m.Add(sum(sq) == 594)
    solver = cp_model.CpSolver(); solver.parameters.max_time_in_seconds = 120
    solver.parameters.num_search_workers = 8
    st = solver.Solve(m)
    return {"status": solver.StatusName(st), "infeasible": st == cp_model.INFEASIBLE}


def z3_decide(V):
    from z3 import Solver, Int, Or, Sum, unsat
    s = Solver()
    A = [Int(f"a{j}") for j in range(9)]; B = [Int(f"b{j}") for j in range(9)]
    for j in range(9):
        s.add(Or(*[A[j] == v for v in V])); s.add(Or(*[B[j] == v for v in V]))
    s.add(Or(Sum(A) == 1, Sum(A) == -1)); s.add(Or(Sum(B) == 1, Sum(B) == -1))
    for sh in range(1, 9):
        s.add(Sum([A[j] * A[(j + sh) % 9] for j in range(9)]) +
              Sum([B[j] * B[(j + sh) % 9] for j in range(9)]) == -74)
    s.add(Sum([A[j] * A[j] for j in range(9)]) + Sum([B[j] * B[j] for j in range(9)]) == 594)
    r = s.check()
    return {"result": str(r), "infeasible": r == unsat}


if __name__ == "__main__":
    engine = sys.argv[1] if len(sys.argv) > 1 else "cpsat"
    ids = [int(x) for x in sys.argv[2:]] or [6, 8, 12]
    out = {}
    for sid in ids:
        H, _ = subgroup_by_id(sid)
        assert len(reduce_subgroup(H, 9)) == 1, f"id{sid} not trivial mod 9"
        sizes, r37 = gc.k37_orbit_sizes(H)
        V = gc.value_set(sizes)
        rec = {"order": len(H), "r37": r37, "V_size": len(V)}
        if engine == "cpsat":
            rec["cpsat"] = cpsat_decide(V)
        else:
            rec["z3"] = z3_decide(V)
        out[f"id{sid}"] = rec
        print(f"id{sid}: order={len(H)} r37={r37} |V|={len(V)} -> {rec.get(engine)}")
    outp = os.path.join(os.path.dirname(__file__), "..", "results",
                        f"general_crosscheck_{engine}.json")
    json.dump(out, open(outp, "w"), indent=2)
    print("wrote", outp)
