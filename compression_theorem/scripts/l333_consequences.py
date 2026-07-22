#!/usr/bin/env python3
"""
l333_consequences.py -- derive the L=333 consequences PURELY from the general
theorems, using the VENDORED, self-contained metadata in
  data/lp333_classification_metadata.json
(provenance + source sha256 recorded there).  Cross-checks Theorem A's mod-37
kills against that metadata's killed_ids.

Language note: the theorems FORBID fixed-symmetry classes (H-invariant LPs with a
given image mod p); they do not "exclude lengths".  Families not settled by these
obstructions are simply "not settled by Theorems A/C" -- we make no claim that
they are irreducibly computational (other closed obstructions may exist).
"""
import json
import os
from math import isqrt

import sympy as sp

HERE = os.path.dirname(__file__)
META = os.path.join(HERE, "..", "data", "lp333_classification_metadata.json")


def sos2(n):
    if n == 0:
        return True
    for q, e in sp.factorint(n).items():
        if q % 4 == 3 and e % 2 == 1:
            return False
    return True


def theoremC_feasible(L, p):
    assert p % 4 == 1
    N = 2 * L + 2
    c = (p - 1) // 4
    A2 = isqrt(N // max(c, 1)) + 1
    for a2 in range(-A2, A2 + 1):
        for b2 in range(-A2, A2 + 1):
            if c * (a2 * a2 + b2 * b2) > N:
                continue
            rem = N - c * (a2 * a2 + b2 * b2)
            t = a2 * a2 + b2 * b2
            a1b = isqrt(rem)
            for a1 in range(-a1b, a1b + 1):
                r2 = rem - a1 * a1
                b1s = isqrt(r2)
                if b1s * b1s != r2:
                    continue
                for b1 in (b1s, -b1s):
                    if 2 * a1 * a2 + 2 * b1 * b2 == t:
                        return True
    return False


def main():
    meta = json.load(open(META))
    subs = meta["subgroups"]
    assert len(subs) == 30
    L, N = 333, 668
    assert not sos2(N)

    forbidden_A_p3, forbidden_A_p37, left = [], [], []
    per_family = []
    for s in subs:
        i = s["id"]
        img3 = sorted(set(u % 3 for u in s["reduction_mod9"]))
        m37 = s["reduction_mod37_order"]
        full37 = s["mod37_full_reduction"]
        verdict, method = "not settled by Theorems A/C", "needs other methods"
        if img3 == [1, 2]:                                   # surjects onto (Z/3)^*
            verdict, method = "FORBIDDEN class", "Theorem A (surjective mod 3)"
            forbidden_A_p3.append(i)
        elif full37:                                         # surjects onto (Z/37)^*
            verdict, method = "FORBIDDEN class", "Theorem A (surjective mod 37)"
            forbidden_A_p37.append(i)
        elif m37 == 18:                                      # image = QR(37), index 2
            if not theoremC_feasible(L, 37):
                verdict, method = "FORBIDDEN class", "Theorem C (real index-2 mod 37)"
            else:
                verdict = "not settled by Theorems A/C"
                method = ("image=QR(37): Theorem C does NOT fire "
                          "(668 is a sum of two squares in O_{Q(sqrt37)})")
                left.append(i)
        else:
            left.append(i)
        per_family.append({"id": i, "order": s["order"], "img_mod3": img3,
                           "mod37_order": m37, "verdict": verdict, "method": method})

    study_killed = set(meta["summary_killed_ids"])
    assert set(forbidden_A_p37) == study_killed, (forbidden_A_p37, study_killed)
    qr37_ids = [s["id"] for s in subs if s["reduction_mod37_order"] == 18]

    result = {
        "L": L, "hadamard_order": N, "N_is_sos2": sos2(N),
        "metadata_provenance": meta["_provenance"],
        "theoremA_mod3": {
            "effect": ("(Z/3)^* has order 2; Theorem A(p=3) forbids every class whose "
                       "image mod 3 is (Z/3)^* since 668 is not a sum of two squares. "
                       "The surviving classes have image mod 3 = {1}, i.e. H lies in "
                       "the order-108 kernel -- the reason the classification enumerates "
                       "subgroups of that kernel."),
            "kernel_order": 108},
        "theoremA_mod37": {"forbidden_ids": sorted(forbidden_A_p37),
                           "vendored_killed_ids": sorted(study_killed),
                           "agree": set(forbidden_A_p37) == study_killed},
        "theoremC_mod37_real_index2": {
            "qr37_family_ids": qr37_ids,
            "668_is_sum_of_two_squares_in_O_Qsqrt37": theoremC_feasible(L, 37),
            "forbidden_by_C": [],
            "note": ("37 = 1 (mod 4): image QR(37) is the REAL quadratic case "
                     "(Theorem C).  668 IS a sum of two squares in O_{Q(sqrt37)}, so "
                     "Theorem C does NOT fire; the image-QR(37) classes are left "
                     "unsettled by Theorems A/C (the prior study settled them by "
                     "meet-in-the-middle).")},
        "boundary": {
            "forbidden_by_theorems_here": sorted(forbidden_A_p3 + forbidden_A_p37),
            "not_settled_by_theorems_here": sorted(left),
            "comment": ("Theorems A/C forbid exactly the 4 surjecting-mod-37 classes "
                        "(ids 25,26,27,29) and are the source of the mod-3 reduction "
                        "to the order-108 kernel.  The remaining classes are not "
                        "settled by these obstructions -- we do NOT claim they are "
                        "irreducibly computational.")},
        "per_family": per_family,
    }
    outp = os.path.join(HERE, "..", "certificates", "l333_consequences.json")
    json.dump(result, open(outp, "w"), indent=2)

    print("L = 333, Hadamard order 668 (not a sum of two squares).")
    print(f"Theorem A (p=37) forbids ids {sorted(forbidden_A_p37)} == vendored "
          f"killed_ids {sorted(study_killed)}: {set(forbidden_A_p37)==study_killed}")
    print(f"Image-QR(37) family ids {qr37_ids}: Theorem C fires? "
          f"{not theoremC_feasible(L,37)} (668 is SOS2 in O_Q(sqrt37) -> not forbidden).")
    print(f"Metadata vendored from source sha256 "
          f"{meta['_provenance']['source_sha256'][:16]}...")
    print("wrote", os.path.relpath(outp))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
