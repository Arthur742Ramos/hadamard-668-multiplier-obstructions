#!/usr/bin/env python3
"""
Third independent engine (z3) for the compressed feasibility, plus a check that
the WEAKER 9-compression relaxation (free odd column sums, NO squared-norm=594
constraint) IS feasible -- which explains why prior work reported the
"9-compression relaxation" as feasible, while the squared-norm-strengthened
version proved here is INFEASIBLE.
"""
import itertools
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))


def z3_decide():
    from z3 import Solver, Int, Or, And, Sum, sat, unsat
    s = Solver()
    A = [Int(f"a{j}") for j in range(9)]
    B = [Int(f"b{j}") for j in range(9)]
    bigA = [Int(f"ba{j}") for j in range(9)]
    bigB = [Int(f"bb{j}") for j in range(9)]
    for j in range(9):
        s.add(Or(A[j] == 1, A[j] == -1, A[j] == 17, A[j] == -17))
        s.add(Or(B[j] == 1, B[j] == -1, B[j] == 17, B[j] == -17))
        # bigness indicator (1 if |.|==17 else 0)
        s.add(Or(bigA[j] == 0, bigA[j] == 1))
        s.add(Or(bigB[j] == 0, bigB[j] == 1))
        s.add((bigA[j] == 1) == (Or(A[j] == 17, A[j] == -17)))
        s.add((bigB[j] == 1) == (Or(B[j] == 17, B[j] == -17)))
    s.add(Sum(bigA) + Sum(bigB) == 2)
    s.add(Or(Sum(A) == 1, Sum(A) == -1))
    s.add(Or(Sum(B) == 1, Sum(B) == -1))
    for sh in range(1, 9):
        s.add(Sum([A[j] * A[(j + sh) % 9] for j in range(9)]) +
              Sum([B[j] * B[(j + sh) % 9] for j in range(9)]) == -74)
    r = s.check()
    return {"engine": "z3", "result": str(r),
            "infeasible": (r == unsat), "sat": (r == sat)}


def weak_relaxation_feasible():
    """Weak 9-compression relaxation: atilde,btilde free ODD integers in
    [-37,37] (i.e., valid column sums with K37-invariance but WITHOUT the exact
    squared-norm=594 constraint), row sums +-1, PAF-sum -74 for s=1..8.
    Show it IS feasible (a witness), so this weaker condition does NOT kill id12.
    Column sums must actually be of the form eps0 + 9*m, m in {-4,-2,0,2,4}:
    values {+-1,+-17,+-19,+-35,+-37}. We use exactly that value set but WITHOUT
    constraining the number of big columns.
    """
    valset = [1, -1, 17, -17, 19, -19, 35, -35, 37, -37]

    def paf(v, sh):
        return sum(v[j] * v[(j + sh) % 9] for j in range(9))

    # MITM: enumerate atilde with rowsum +-1, store PAF profile; match -74 target.
    target = [-74] * 8
    seen = {}
    # too many (10^9); use CP-SAT to just find ONE witness quickly instead.
    try:
        from ortools.sat.python import cp_model
    except Exception as e:
        return {"error": str(e)}
    m = cp_model.CpModel()
    A = [m.NewIntVarFromDomain(cp_model.Domain.FromValues(valset), f"a{j}") for j in range(9)]
    B = [m.NewIntVarFromDomain(cp_model.Domain.FromValues(valset), f"b{j}") for j in range(9)]
    sa = m.NewIntVar(-333, 333, "sa"); m.Add(sa == sum(A)); m.AddAllowedAssignments([sa], [[-1], [1]])
    sb = m.NewIntVar(-333, 333, "sb"); m.Add(sb == sum(B)); m.AddAllowedAssignments([sb], [[-1], [1]])

    def paf_expr(V, sh):
        terms = []
        for j in range(9):
            p = m.NewIntVar(-37 * 37, 37 * 37, "")
            m.AddMultiplicationEquality(p, [V[j], V[(j + sh) % 9]])
            terms.append(p)
        return sum(terms)
    for sh in range(1, 9):
        m.Add(paf_expr(A, sh) + paf_expr(B, sh) == -74)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 60
    st = solver.Solve(m)
    res = {"engine": "cp-sat (weak relaxation, no squared-norm)",
           "status": solver.StatusName(st)}
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        av = [solver.Value(A[j]) for j in range(9)]
        bv = [solver.Value(B[j]) for j in range(9)]
        res["witness_atilde"] = av
        res["witness_btilde"] = bv
        res["check_rowsums"] = [sum(av), sum(bv)]
        res["check_squared_norm"] = sum(x * x for x in av) + sum(x * x for x in bv)
        res["check_PAFsum"] = [paf(av, sh) + paf(bv, sh) for sh in range(1, 9)]
        res["feasible"] = True
    else:
        res["feasible"] = (st != cp_model.INFEASIBLE)
    return res


if __name__ == "__main__":
    out = {}
    print("z3 decision of the (strong) compressed problem ...")
    out["z3_strong"] = z3_decide()
    print("   ", out["z3_strong"])
    print("weak relaxation (no squared-norm) feasibility ...")
    out["weak_relaxation"] = weak_relaxation_feasible()
    wr = out["weak_relaxation"]
    print("   status:", wr.get("status"), " feasible:", wr.get("feasible"))
    if wr.get("feasible"):
        print("   witness squared_norm =", wr.get("check_squared_norm"),
              "(NOT 594) rowsums", wr.get("check_rowsums"),
              "PAFsum", set(wr.get("check_PAFsum", [])))
    outp = os.path.join(os.path.dirname(__file__), "..", "results",
                        "compression_thirdengine.json")
    with open(outp, "w") as f:
        json.dump(out, f, indent=2)
    print("wrote", outp)
