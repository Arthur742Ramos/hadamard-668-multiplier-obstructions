#!/usr/bin/env python3
"""
Specialized exact model for families with TRIVIAL image mod 9 (r9 = 1), i.e. H
acts only on the Z_37 coordinate of Z_333 = Z_9 x Z_37 via K37 = image of H in
(Z/37)^*.  Such a sequence a is a K37-invariant function in the second
coordinate: for each column c in Z_9 the length-37 vector a_c(d)=a(c,d) is
constant on K37-orbits of Z_37.  There are  T = 2^(#K37-orbits)  distinct column
types.

Key identity (shift s=(s9,s37) under CRT):
    PAF_a(s9,s37) = sum_{c in Z_9} CC(a_c, a_{c+s9}; s37),
    CC(u,v;t) = sum_{d in Z_37} u(d) v(d+t),
and CC(u,v;t) is constant on K37-orbits of t.  The nonzero length-333 shift
orbits are (s9, class37) != (0,0), giving one PAF equation each:
    sum_c CC[A[c]][A[c+s9]][class] + sum_c CC[B[c]][B[c+s9]][class] = -2.
Row sums:  sum_c colsum(A[c]) in {+1,-1}.  This is an exact model over 9+9 small
integer variables; CP-SAT decides it exactly (UNSAT = proof; SAT verified).
"""
import json
import os
import sys
import time
from ortools.sat.python import cp_model

sys.path.insert(0, os.path.dirname(__file__))
from core import L, is_legendre_pair, reduce_subgroup
from search_common import subgroup_by_id
from necessary_conditions import k_orbits


def build_columns(H):
    K = reduce_subgroup(H, 37)
    assert reduce_subgroup(H, 9) == frozenset({1}), "family is not trivial mod 9"
    orbs = k_orbits(K, 37)                       # [{0}, O1, O2, ...]
    norb = len(orbs)
    cls_of = [0] * 37
    for oi, o in enumerate(orbs):
        for d in o:
            cls_of[d] = oi
    T = 1 << norb                                # number of column types
    # column vector for each type: bit oi (of type index) = value on orbit oi (0->+1,1->-1)
    col = []
    for t in range(T):
        vec = [0] * 37
        for d in range(37):
            bit = (t >> cls_of[d]) & 1
            vec[d] = -1 if bit else 1
        col.append(vec)
    colsum = [sum(v) for v in col]
    # shift classes for the length-37 second coordinate = K37-orbits of Z_37
    # class 0 = {0}; nonzero classes 1..norb-1 with representative reps[c]
    reps = [orbs[oi][0] for oi in range(norb)]   # reps[0]=0
    # CC table: CC[t1][t2][cls] = sum_d col[t1][d]*col[t2][(d+reps[cls])%37]
    CC = [[[0] * norb for _ in range(T)] for _ in range(T)]
    for t1 in range(T):
        c1 = col[t1]
        for t2 in range(T):
            c2 = col[t2]
            for cl in range(norb):
                sh = reps[cl]
                CC[t1][t2][cl] = sum(c1[d] * c2[(d + sh) % 37] for d in range(37))
    return {"K37_order": len(K), "norb": norb, "T": T, "col": col,
            "colsum": colsum, "CC": CC, "reps": reps}


def solve(sid, max_seconds=600, workers=8, symbreak=True):
    H, rec = subgroup_by_id(sid)
    cd = build_columns(H)
    T = cd["T"]; norb = cd["norb"]; CC = cd["CC"]; colsum = cd["colsum"]
    m = cp_model.CpModel()
    A = [m.NewIntVar(0, T - 1, f"A{c}") for c in range(9)]
    B = [m.NewIntVar(0, T - 1, f"B{c}") for c in range(9)]

    # flatten CC per class into 1-D tables indexed by 32*t1+t2 for AddElement
    def cc_flat(cl):
        return [CC[t1][t2][cl] for t1 in range(T) for t2 in range(T)]
    cc_tables = [cc_flat(cl) for cl in range(norb)]

    def pair_index(x, y):
        idx = m.NewIntVar(0, T * T - 1, "")
        m.Add(idx == T * x + y)
        return idx

    # PAF equations for every nonzero shift orbit (s9, class) != (0,0)
    for s9 in range(9):
        for cl in range(norb):
            if s9 == 0 and cl == 0:
                continue
            terms = []
            for seqvars in (A, B):
                for c in range(9):
                    idx = pair_index(seqvars[c], seqvars[(c + s9) % 9])
                    val = m.NewIntVar(-37, 37, "")
                    m.AddElement(idx, cc_tables[cl], val)
                    terms.append(val)
            m.Add(sum(terms) == -2)

    # row sums in {+1,-1}
    for seqvars in (A, B):
        svals = []
        for c in range(9):
            sv = m.NewIntVar(min(colsum), max(colsum), "")
            m.AddElement(seqvars[c], colsum, sv)
            svals.append(sv)
        tot = m.NewIntVar(-333, 333, "")
        m.Add(tot == sum(svals))
        m.AddAllowedAssignments([tot], [[-1], [1]])

    if symbreak:
        # cyclic-9 column rotation (whole-sequence shift) canonicalization: (A,B) <= rot_k(A,B)
        def add_lex(X, Y):
            n = len(X)
            eq = m.NewBoolVar(""); m.Add(eq == 1)
            for i in range(n):
                m.Add(X[i] <= Y[i]).OnlyEnforceIf(eq)
                ne = m.NewBoolVar(""); sm = m.NewBoolVar("")
                m.Add(X[i] == Y[i]).OnlyEnforceIf(sm)
                m.Add(X[i] != Y[i]).OnlyEnforceIf(sm.Not())
                m.AddBoolAnd([eq, sm]).OnlyEnforceIf(ne)
                m.AddBoolOr([eq.Not(), sm.Not()]).OnlyEnforceIf(ne.Not())
                eq = ne
        for k in range(1, 9):
            rotA = [A[(c + k) % 9] for c in range(9)]
            rotB = [B[(c + k) % 9] for c in range(9)]
            add_lex(A + B, rotA + rotB)
        # swap
        add_lex(A + B, B + A)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = max_seconds
    solver.parameters.num_search_workers = workers
    t0 = time.time(); status = solver.Solve(m); dt = time.time() - t0
    out = {"id": sid, "order": len(H), "model": "column-type (Z9 x Z37 factored)",
           "K37_order": cd["K37_order"], "num_column_types": T,
           "seconds": round(dt, 2), "status": solver.StatusName(status),
           "symmetry_breaking": symbreak}
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        Av = [solver.Value(A[c]) for c in range(9)]
        Bv = [solver.Value(B[c]) for c in range(9)]
        col = cd["col"]
        # reconstruct full length-333 sequences via CRT: index i <-> (i%9, i%37)
        a = [0] * L; b = [0] * L
        for i in range(L):
            c9, d37 = i % 9, i % 37
            a[i] = col[Av[c9]][d37]
            b[i] = col[Bv[c9]][d37]
        ok, msg = is_legendre_pair(a, b)
        out.update({"sat": True, "verified_legendre_pair": ok, "verify_msg": msg,
                    "A_types": Av, "B_types": Bv})
        if ok:
            out["a_sequence"] = a; out["b_sequence"] = b
    elif status == cp_model.INFEASIBLE:
        out.update({"sat": False, "verified_no_invariant_LP": True})
    else:
        out["sat"] = None
    return out


if __name__ == "__main__":
    ids = [int(x) for x in sys.argv[1:]] or [20]
    tsec = float(os.environ.get("CPS_T", "300"))
    workers = int(os.environ.get("CPS_W", "8"))
    for sid in ids:
        r = solve(sid, max_seconds=tsec, workers=workers)
        print(f"id={r['id']:>2} order={r['order']:>3} T={r['num_column_types']:>4} "
              f"K37={r['K37_order']:>2} status={r['status']:>10} t={r['seconds']:>7}s "
              f"sat={r.get('sat')}", flush=True)
