#!/usr/bin/env python3
"""Driver: build spec -> run C++ MITM -> exactly verify any SAT solution."""
import json
import os
import subprocess
import sys
import time
from core import L, is_legendre_pair
from search_common import subgroup_by_id, build_spec, write_spec_text

HERE = os.path.dirname(__file__)
BIN = os.path.join(HERE, "mitm")
RESDIR = os.path.join(HERE, "..", "results")
MITMDIR = os.path.join(RESDIR, "mitm")


def ensure_built():
    src = os.path.join(HERE, "mitm.cpp")
    if (not os.path.exists(BIN)) or os.path.getmtime(src) > os.path.getmtime(BIN):
        subprocess.run(["c++", "-O3", "-march=native", "-std=c++17", src, "-o", BIN],
                       check=True)


def expand(spec, xvals):
    idx = spec["idx"]
    return [xvals[idx[i]] for i in range(L)]


def run_family(sid, timeout=None):
    ensure_built()
    H, rec = subgroup_by_id(sid)
    spec = build_spec(H)
    specpath = os.path.join(RESDIR, f"spec_id{sid}.txt")
    write_spec_text(spec, specpath)
    t0 = time.time()
    proc = subprocess.run([BIN, specpath], capture_output=True, text=True,
                          timeout=timeout)
    dt = time.time() - t0
    out = json.loads(proc.stdout)
    result = {
        "id": sid, "order": len(H), "generators": rec["generators"],
        "r": spec["r"], "num_reps": spec["num_reps"],
        "reduction_mod9_order": rec["structure"]["reduction_mod9_order"],
        "reduction_mod37_order": rec["structure"]["reduction_mod37_order"],
        "orbit_signature": rec["orbit_signature"],
        "seconds": round(dt, 3),
        "enumerated": out["enumerated"],
        "rowsum_ok": out["rowsum_ok"],
        "distinct_profiles": out["distinct_profiles"],
        "sat": out["sat"],
        "method": "exact meet-in-the-middle over 2^(r-1) orbit assignments (a_0=b_0=+1)",
    }
    if out["sat"]:
        a = expand(spec, out["a"])
        b = expand(spec, out["b"])
        ok, msg = is_legendre_pair(a, b)
        result["verified_legendre_pair"] = ok
        result["verify_msg"] = msg
        result["a_orbit_values"] = out["a"]
        result["b_orbit_values"] = out["b"]
        if ok:
            result["a_sequence"] = a
            result["b_sequence"] = b
    else:
        result["verified_no_invariant_LP"] = True
    return result


if __name__ == "__main__":
    ids = [int(x) for x in sys.argv[1:]] or [28]
    os.makedirs(MITMDIR, exist_ok=True)
    for sid in ids:
        res = run_family(sid)
        with open(os.path.join(MITMDIR, f"id{sid}.json"), "w") as handle:
            json.dump(res, handle, indent=2)
            handle.write("\n")
        tag = ("SAT (verified LP=%s)" % res.get("verified_legendre_pair")
               if res["sat"] else "UNSAT (no invariant LP)")
        print(f"id={sid:>2} order={res['order']:>3} r={res['r']:>2} "
              f"reps={res['num_reps']:>2} t={res['seconds']:>7}s "
              f"rowsum_ok={res['rowsum_ok']:>9} {tag}")
