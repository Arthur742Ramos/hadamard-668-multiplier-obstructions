#!/usr/bin/env python3
"""Validate PAF-from-orbits against direct PAF, and the H-orbit reduction of
shifts; then a reference meet-in-the-middle exact search (small r)."""
import itertools
import os
import random
from core import L, orbits_on_ZL, paf
from search_common import subgroup_by_id, build_spec, paf_from_orbits


def expand(spec, xvals):
    idx = spec["idx"]
    return [xvals[idx[i]] for i in range(L)]


def validate_spec(sid, trials=200):
    H, rec = subgroup_by_id(sid)
    spec = build_spec(H)
    r = spec["r"]
    random.seed(12345 + sid)
    for _ in range(trials):
        x = [random.choice((-1, 1)) for _ in range(r)]
        seq = expand(spec, x)
        # H-invariance of seq
        for u in list(H)[:5]:
            for i in random.sample(range(L), 5):
                assert seq[i] == seq[(u * i) % L]
        for m, s in enumerate(spec["reps"]):
            ref = paf(seq, s)
            got = paf_from_orbits(spec, x, m)
            assert ref == got, (sid, s, ref, got)
            # PAF invariance under H on shifts
            for u in list(H)[:3]:
                assert paf(seq, (u * s) % L) == ref
    return spec


def mitm_python(sid, verbose=True):
    """Exact search: enumerate a-orbit-assignments with row sum +/-1 and
    a_0 = +1; match PAF profiles p with complement (-2)-p (dict).  Returns a
    solution (x,y) or None, plus stats.  Exhaustive over 2^(r-1)."""
    H, rec = subgroup_by_id(sid)
    spec = build_spec(H)
    r = spec["r"]
    sizes = spec["sizes"]
    nreps = spec["num_reps"]
    seen = {}          # profile tuple -> x tuple
    enumerated = 0
    rowsum_ok = 0
    target = tuple(-2 for _ in range(nreps))
    # enumerate x[1..r-1] in {+/-1}, x[0]=+1
    for bits in itertools.product((1, -1), repeat=r - 1):
        x = (1,) + bits
        enumerated += 1
        rs = sum(sizes[q] * x[q] for q in range(r))
        if rs not in (-1, 1):
            continue
        rowsum_ok += 1
        prof = tuple(paf_from_orbits(spec, x, m) for m in range(nreps))
        comp = tuple(target[m] - prof[m] for m in range(nreps))
        if comp in seen:
            return {"sat": True, "x": list(seen[comp]), "y": list(x),
                    "spec": spec, "enumerated": enumerated,
                    "rowsum_ok": rowsum_ok, "distinct_profiles": len(seen)}
        if comp == prof:
            return {"sat": True, "x": list(x), "y": list(x),
                    "spec": spec, "enumerated": enumerated,
                    "rowsum_ok": rowsum_ok, "distinct_profiles": len(seen)}
        if prof not in seen:
            seen[prof] = x
    return {"sat": False, "spec": spec, "enumerated": enumerated,
            "rowsum_ok": rowsum_ok, "distinct_profiles": len(seen)}


if __name__ == "__main__":
    import sys
    # validate on several small families
    for sid in [28, 24, 21, 22]:
        spec = validate_spec(sid, trials=80)
        print(f"[validate] id={sid} r={spec['r']} num_reps={spec['num_reps']} OK")
    # run python MITM on the smallest family as a demo
    sid = int(sys.argv[1]) if len(sys.argv) > 1 else 28
    res = mitm_python(sid)
    print(f"[mitm_py] id={sid} sat={res['sat']} enumerated={res['enumerated']} "
          f"rowsum_ok={res['rowsum_ok']} distinct_profiles={res['distinct_profiles']}")
