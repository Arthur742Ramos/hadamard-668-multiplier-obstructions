#!/usr/bin/env python3
"""
CP-SAT model WITH sound symmetry breaking for the invariant Legendre-pair search.

Symmetries of a solution pair (a,b) (as orbit-value vectors, a_0=b_0=+1 fixed):
  * multiplier u in (Z/333)^*: relabels the H-orbits by the permutation
    pi_u(orbit(x)) = orbit(u x)  (H is normal, so this permutes orbits and fixes {0});
    it sends (a,b) -> (a o pi_u^{-1}, b o pi_u^{-1});
  * swap: (a,b) -> (b,a).
Because the lex-minimum of each symmetry orbit satisfies  V <=_lex g(V)  for every
group element g, adding  V <=_lex g(V)  for a set of GENERATORS g is SOUND
(never turns SAT into UNSAT); it only prunes symmetric duplicates.  V is the
concatenation (za_0..za_{r-1}, zb_0..zb_{r-1}).
"""
import json
import os
import sys
import time
from math import gcd
from ortools.sat.python import cp_model

sys.path.insert(0, os.path.dirname(__file__))
from core import L, is_legendre_pair, orbits_on_ZL
from search_common import subgroup_by_id, build_spec

HERE = os.path.dirname(__file__)
OUTDIR = os.path.join(HERE, "..", "results", "cpsat")


def add_lex_leq(model, X, Y):
    """Enforce X <=_lex Y for equal-length lists of 0/1 vars (X[0] most significant)."""
    n = len(X)
    # eq_prefix[i] = all of X[0..i-1]==Y[0..i-1]
    eq = model.NewBoolVar("lex_eq0")
    model.Add(eq == 1)
    for i in range(n):
        # if eq (prefix equal so far): X[i] <= Y[i]
        model.Add(X[i] <= Y[i]).OnlyEnforceIf(eq)
        neq = model.NewBoolVar(f"lex_eq_{i+1}")
        # neq = eq AND (X[i]==Y[i])
        same = model.NewBoolVar(f"lex_same_{i}")
        model.Add(X[i] == Y[i]).OnlyEnforceIf(same)
        model.Add(X[i] != Y[i]).OnlyEnforceIf(same.Not())
        model.AddBoolAnd([eq, same]).OnlyEnforceIf(neq)
        model.AddBoolOr([eq.Not(), same.Not()]).OnlyEnforceIf(neq.Not())
        eq = neq


def orbit_perm(H, orbs, u):
    """Permutation of orbit indices induced by multiplication by unit u."""
    idx = [0] * L
    for oi, o in enumerate(orbs):
        for i in o:
            idx[i] = oi
    perm = [0] * len(orbs)
    for oi, o in enumerate(orbs):
        x = o[0]
        perm[oi] = idx[(u * x) % L]
    return perm


def gens_units333():
    # u1 == 2 mod 9, 1 mod 37 ; u2 == 1 mod 9, 2 mod 37   (2 is a primitive root mod 9 and mod 37)
    def crt(a9, a37):
        for x in range(L):
            if x % 9 == a9 and x % 37 == a37:
                return x
    return [crt(2, 1), crt(1, 2)]


def build_model(spec, H, orbs, symbreak=True):
    r = spec["r"]; sizes = spec["sizes"]; W = spec["W"]; const = spec["const"]; reps = spec["reps"]
    m = cp_model.CpModel()
    za = [m.NewBoolVar(f"za{q}") for q in range(r)]
    zb = [m.NewBoolVar(f"zb{q}") for q in range(r)]
    m.Add(za[0] == 0); m.Add(zb[0] == 0)

    used = set()
    for mm in range(len(reps)):
        Wm = W[mm]
        for q in range(r):
            for q2 in range(q + 1, r):
                if Wm[q][q2] != 0:
                    used.add((q, q2))
    wa, wb = {}, {}
    def mkxor(zv, q, q2, nm):
        w = m.NewBoolVar(nm)
        m.Add(w <= zv[q] + zv[q2]); m.Add(w >= zv[q] - zv[q2])
        m.Add(w >= zv[q2] - zv[q]); m.Add(w <= 2 - zv[q] - zv[q2])
        return w
    for (q, q2) in used:
        wa[(q, q2)] = mkxor(za, q, q2, f"wa_{q}_{q2}")
        wb[(q, q2)] = mkxor(zb, q, q2, f"wb_{q}_{q2}")

    for mm in range(len(reps)):
        Wm = W[mm]
        K = const[mm] + sum(Wm[q][q2] for q in range(r) for q2 in range(q + 1, r))
        terms = []
        for (q, q2), wv in wa.items():
            if Wm[q][q2]:
                terms.append(Wm[q][q2] * wv)
        for (q, q2), wv in wb.items():
            if Wm[q][q2]:
                terms.append(Wm[q][q2] * wv)
        m.Add(sum(terms) == K + 1)

    m.Add(sum(sizes[q] * za[q] for q in range(r)) >= 166)
    m.Add(sum(sizes[q] * za[q] for q in range(r)) <= 167)
    m.Add(sum(sizes[q] * zb[q] for q in range(r)) >= 166)
    m.Add(sum(sizes[q] * zb[q] for q in range(r)) <= 167)

    if symbreak:
        V = za + zb
        # swap symmetry: (za,zb) <=_lex (zb,za)
        add_lex_leq(m, za + zb, zb + za)
        # multiplier symmetry: V <=_lex permuted V for generators
        for u in gens_units333():
            perm = orbit_perm(H, orbs, u)  # perm[oi] = image orbit of oi
            # relabeled solution a'(oi) = a(perm^{-1}(oi)); as position permutation on V
            inv = [0] * len(perm)
            for i, p in enumerate(perm):
                inv[p] = i
            Va = [za[inv[q]] for q in range(r)]
            Vb = [zb[inv[q]] for q in range(r)]
            add_lex_leq(m, za + zb, Va + Vb)
    return m, za, zb


def solve_family(sid, max_seconds=300, workers=8, symbreak=True):
    H, rec = subgroup_by_id(sid)
    spec = build_spec(H)
    orbs = orbits_on_ZL(H, L)
    model, za, zb = build_model(spec, H, orbs, symbreak=symbreak)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = max_seconds
    solver.parameters.num_search_workers = workers
    t0 = time.time(); status = solver.Solve(model); dt = time.time() - t0
    out = {"id": sid, "order": len(H), "r": spec["r"], "num_reps": spec["num_reps"],
           "seconds": round(dt, 2), "status": solver.StatusName(status),
           "symmetry_breaking": symbreak,
           "method": "exact CP-SAT (booleanized PAF) with multiplier+swap symmetry breaking"}
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        idx = spec["idx"]
        xa = [1 - 2 * solver.Value(za[q]) for q in range(spec["r"])]
        xb = [1 - 2 * solver.Value(zb[q]) for q in range(spec["r"])]
        a = [xa[idx[i]] for i in range(L)]; b = [xb[idx[i]] for i in range(L)]
        ok, msg = is_legendre_pair(a, b)
        out.update({"sat": True, "verified_legendre_pair": ok, "verify_msg": msg,
                    "a_orbit_values": xa, "b_orbit_values": xb})
        if ok:
            out["a_sequence"] = a; out["b_sequence"] = b
    elif status == cp_model.INFEASIBLE:
        out.update({"sat": False, "verified_no_invariant_LP": True})
    else:
        out["sat"] = None
    return out


if __name__ == "__main__":
    ids = [int(x) for x in sys.argv[1:]] or [21]
    tsec = float(os.environ.get("CPS_T", "120")); workers = int(os.environ.get("CPS_W", "8"))
    os.makedirs(OUTDIR, exist_ok=True)
    for sid in ids:
        res = solve_family(sid, max_seconds=tsec, workers=workers)
        with open(os.path.join(OUTDIR, f"id{sid}_symbreak.json"), "w") as handle:
            json.dump(res, handle, indent=2)
            handle.write("\n")
        print(f"id={res['id']:>2} order={res['order']:>3} r={res['r']:>3} "
              f"status={res['status']:>10} t={res['seconds']:>7}s sat={res.get('sat')}",
              flush=True)
