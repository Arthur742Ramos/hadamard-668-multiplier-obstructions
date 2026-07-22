#!/usr/bin/env python3
"""
Exact CP-SAT model for common-multiplier-invariant Legendre pairs of length 333.

Boolean za_Q, zb_Q encode orbit values  x = 1 - 2 z  in {+1,-1}.
For each unordered orbit pair {Q,Q'} a boolean w^a_{QQ'} = za_Q XOR za_Q' gives
    x_Q x_{Q'} = 1 - 2 w^a_{QQ'}.
Then PAF_a(m) = const_m + sum_{Q<Q'} W_m[Q,Q'](1 - 2 w^a_{QQ'}) = K_m - 2 S^a_m,
with K_m = const_m + sum_{Q<Q'} W_m[Q,Q'] and S^a_m = sum W_m w^a.
The Legendre condition PAF_a(m)+PAF_b(m) = -2 becomes the linear constraint
    sum_{Q<Q'} W_m[Q,Q'] (w^a_{QQ'} + w^b_{QQ'}) = K_m + 1     (for every rep m),
and the row sums give  sum_Q size_Q z_Q in {166,167}  (since sum size_Q = 333).
za_0 = zb_0 = 0 fixes a_0=b_0=+1 (kills the global-sign symmetry).

CP-SAT is a complete exact solver: UNSAT is a proof; any SAT model is verified
exactly against the full length-333 PAF definition before acceptance.
"""
import json
import os
import sys
import time
from ortools.sat.python import cp_model

sys.path.insert(0, os.path.dirname(__file__))
from core import L, is_legendre_pair
from search_common import subgroup_by_id, build_spec

HERE = os.path.dirname(__file__)


def build_model(spec, break_ab=True):
    r = spec["r"]
    sizes = spec["sizes"]
    W = spec["W"]
    const = spec["const"]
    reps = spec["reps"]
    m = cp_model.CpModel()

    za = [m.NewBoolVar(f"za{q}") for q in range(r)]
    zb = [m.NewBoolVar(f"zb{q}") for q in range(r)]
    m.Add(za[0] == 0)
    m.Add(zb[0] == 0)

    # pair XOR vars, created lazily only for pairs used by some rep
    used = [[False] * r for _ in range(r)]
    for mm in range(len(reps)):
        Wm = W[mm]
        for q in range(r):
            for q2 in range(q + 1, r):
                if Wm[q][q2] != 0:
                    used[q][q2] = True

    wa = {}
    wb = {}

    def make_xor(zv, q, q2, name):
        w = m.NewBoolVar(name)
        # w = z_q XOR z_q2
        m.Add(w <= zv[q] + zv[q2])
        m.Add(w >= zv[q] - zv[q2])
        m.Add(w >= zv[q2] - zv[q])
        m.Add(w <= 2 - zv[q] - zv[q2])
        return w

    for q in range(r):
        for q2 in range(q + 1, r):
            if used[q][q2]:
                wa[(q, q2)] = make_xor(za, q, q2, f"wa_{q}_{q2}")
                wb[(q, q2)] = make_xor(zb, q, q2, f"wb_{q}_{q2}")

    # PAF equalities
    for mm, s in enumerate(reps):
        Wm = W[mm]
        K = const[mm] + sum(Wm[q][q2] for q in range(r) for q2 in range(q + 1, r))
        terms = []
        for (q, q2), wv in wa.items():
            c = Wm[q][q2]
            if c:
                terms.append(c * wv)
        for (q, q2), wv in wb.items():
            c = Wm[q][q2]
            if c:
                terms.append(c * wv)
        m.Add(sum(terms) == K + 1)

    # row sums in {166,167}
    m.Add(sum(sizes[q] * za[q] for q in range(r)) >= 166)
    m.Add(sum(sizes[q] * za[q] for q in range(r)) <= 167)
    m.Add(sum(sizes[q] * zb[q] for q in range(r)) >= 166)
    m.Add(sum(sizes[q] * zb[q] for q in range(r)) <= 167)

    return m, za, zb


def solve_family(sid, max_seconds=300, workers=8):
    H, rec = subgroup_by_id(sid)
    spec = build_spec(H)
    model, za, zb = build_model(spec)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = max_seconds
    solver.parameters.num_search_workers = workers
    t0 = time.time()
    status = solver.Solve(model)
    dt = time.time() - t0
    sname = solver.StatusName(status)
    out = {"id": sid, "order": len(H), "r": spec["r"], "num_reps": spec["num_reps"],
           "seconds": round(dt, 2), "status": sname,
           "method": "exact CP-SAT (booleanized PAF system)"}
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        idx = spec["idx"]
        xa = [1 - 2 * solver.Value(za[q]) for q in range(spec["r"])]
        xb = [1 - 2 * solver.Value(zb[q]) for q in range(spec["r"])]
        a = [xa[idx[i]] for i in range(L)]
        b = [xb[idx[i]] for i in range(L)]
        ok, msg = is_legendre_pair(a, b)
        out["sat"] = True
        out["verified_legendre_pair"] = ok
        out["verify_msg"] = msg
        out["a_orbit_values"] = xa
        out["b_orbit_values"] = xb
        if ok:
            out["a_sequence"] = a
            out["b_sequence"] = b
    elif status == cp_model.INFEASIBLE:
        out["sat"] = False
        out["verified_no_invariant_LP"] = True
    else:
        out["sat"] = None  # unknown (timeout)
    return out


if __name__ == "__main__":
    ids = [int(x) for x in sys.argv[1:]] or [28]
    for sid in ids:
        res = solve_family(sid, max_seconds=float(os.environ.get("CPS_T", "120")))
        print(f"id={res['id']:>2} order={res['order']:>3} r={res['r']:>3} "
              f"status={res['status']:>10} t={res['seconds']:>7}s "
              f"sat={res.get('sat')}")
