#!/usr/bin/env python3
"""
Build the exact H-invariant PAF search specification for a subgroup H.

For an H-invariant sequence a (constant on H-orbits of Z_333) with orbit values
x_Q in {+1,-1}, and any shift s,
    PAF_a(s) = sum_i a_i a_{(i+s) mod L}
             = sum_{Q,Q'} M_s[Q,Q'] x_Q x_{Q'}
             = const_s + sum_{Q<Q'} W_s[Q,Q'] x_Q x_{Q'},
where M_s[Q,Q'] = #{ i : orbit(i)=Q, orbit((i+s)%L)=Q' },
      const_s   = sum_Q M_s[Q,Q]   (diagonal; x_Q^2 = 1),
      W_s[Q,Q'] = M_s[Q,Q'] + M_s[Q',Q]   (Q<Q').

Because PAF_a(s) = PAF_a(u s) for u in H, we only need one representative shift s
per nonzero H-orbit.  The invariant Legendre-pair condition is exactly
    PAF_a(s_O) + PAF_b(s_O) = -2   for every nonzero orbit O,
    sum_Q |Q| x_Q = +/-1  and  sum_Q |Q| y_Q = +/-1   (row sums).
This is equivalent (Fourier dual) to |A(k)|^2+|B(k)|^2 = 668 for all k != 0.
"""
import json
import os
from core import L, KERNEL3, all_subgroups, orbits_on_ZL

HERE = os.path.dirname(__file__)


def load_classification():
    p = os.path.join(HERE, "..", "results", "subgroup_classification.json")
    with open(p) as f:
        return json.load(f)


def subgroup_by_id(sid):
    cls = load_classification()
    rec = next(r for r in cls["subgroups"] if r["id"] == sid)
    return frozenset(rec["elements"]), rec


def build_spec(H):
    orbs = orbits_on_ZL(H, L)
    r = len(orbs)
    idx = [0] * L
    for qi, o in enumerate(orbs):
        for i in o:
            idx[i] = qi
    sizes = [len(o) for o in orbs]
    # orbit 0 must be {0}
    assert orbs[0] == [0], orbs[0]

    nonzero = [qi for qi in range(r) if qi != 0]
    reps = [orbs[qi][0] for qi in nonzero]  # representative shift per nonzero orbit

    # Build W_s and const_s for each representative shift
    W = []          # list over reps of r*r symmetric int matrix (diag 0)
    const = []      # list over reps
    for s in reps:
        M = [[0] * r for _ in range(r)]
        for i in range(L):
            M[idx[i]][idx[(i + s) % L]] += 1
        c = sum(M[q][q] for q in range(r))
        Wm = [[0] * r for _ in range(r)]
        for q in range(r):
            for q2 in range(q + 1, r):
                Wm[q][q2] = M[q][q2] + M[q2][q]
                Wm[q2][q] = Wm[q][q2]
        W.append(Wm)
        const.append(c)
    return {
        "r": r,
        "sizes": sizes,
        "reps": reps,
        "num_reps": len(reps),
        "const": const,
        "W": W,
        "orbits": orbs,
        "idx": idx,
    }


def write_spec_text(spec, path):
    """Compact text spec for the C++ solver."""
    r = spec["r"]
    nreps = spec["num_reps"]
    lines = []
    lines.append(f"{r} {nreps}")
    lines.append(" ".join(map(str, spec["sizes"])))
    lines.append(" ".join(map(str, spec["const"])))
    for m in range(nreps):
        Wm = spec["W"][m]
        # upper triangle row-major (q<q')
        flat = []
        for q in range(r):
            for q2 in range(q + 1, r):
                flat.append(Wm[q][q2])
        lines.append(" ".join(map(str, flat)))
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


def paf_from_orbits(spec, xvals, m):
    """Reference PAF_a(reps[m]) from orbit values xvals (list of +/-1)."""
    r = spec["r"]
    Wm = spec["W"][m]
    tot = spec["const"][m]
    for q in range(r):
        for q2 in range(q + 1, r):
            tot += Wm[q][q2] * xvals[q] * xvals[q2]
    return tot


if __name__ == "__main__":
    import sys
    sid = int(sys.argv[1]) if len(sys.argv) > 1 else 28
    H, rec = subgroup_by_id(sid)
    spec = build_spec(H)
    print(f"id={sid} order={len(H)} r={spec['r']} num_reps={spec['num_reps']}")
    print("orbit sizes:", spec["sizes"])
    print("reps:", spec["reps"])
