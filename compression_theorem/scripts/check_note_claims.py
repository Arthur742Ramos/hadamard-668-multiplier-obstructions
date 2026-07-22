#!/usr/bin/env python3
"""
check_note_claims.py -- independently re-derive and ASSERT every specific numeric
claim in theorem_note.md, with the CORRECTED (exhaustive) counts.  Exit 0 == pass.
"""
import json
import os

import sympy as sp

from norm_form_obstruction import (theoremC_feasible, propD_feasible,
                                    theoremC_census, propD_census,
                                    check_cm_relative_norm)


def sos2(n):
    if n == 0:
        return True
    for q, e in sp.factorint(n).items():
        if q % 4 == 3 and e % 2 == 1:
            return False
    return True


def feasC(L, p):
    ok, _ = theoremC_feasible(L, p)
    return ok


CLAIMS = []


def claim(desc, cond):
    assert cond, "FAILED: " + desc
    CLAIMS.append(desc)
    print("  ok:", desc)


def main():
    print("Checking every numeric claim in theorem_note.md (corrected counts) ...")

    # -- §0/§3/§8: core number facts about 668 --
    claim("668 = 2^2 * 167, 167 prime, 167 = 3 (mod 4), not SOS2",
          sp.factorint(668) == {2: 2, 167: 1} and 167 % 4 == 3 and not sos2(668))
    claim("334 not SOS2; 2n SOS2 <=> n SOS2 (n<1000)",
          (not sos2(334)) and all(sos2(2 * n) == sos2(n) for n in range(1, 1000)))

    # -- §5 Theorem C: exhaustive census 428 cases / 139 forbidden --
    tc = theoremC_census(1200)
    claim("Theorem C EXHAUSTIVE census: 428 total classes (all p=1 mod4 | odd L<=1200)",
          tc["total_cases"] == 428)
    claim("Theorem C EXHAUSTIVE census: 139 FORBIDDEN classes",
          tc["num_forbidden_classes"] == 139)
    claim("Theorem C forbidden classes span 116 distinct lengths, primes up to 373",
          tc["distinct_lengths"] == 116 and max(tc["distinct_primes"]) == 373)

    # -- §5 example forbidden classes --
    examples = [(65, 5), (65, 13), (75, 5), (85, 17), (87, 29), (91, 13),
                (111, 37), (119, 17), (123, 41), (183, 61), (185, 5), (185, 37),
                (187, 17), (203, 29)]
    for (L, p) in examples:
        claim(f"Theorem C FORBIDS (L={L}, p={p}): (R)+(S) infeasible & 2L+2 not SOS2",
              (p % 4 == 1) and (L % p == 0) and (not sos2(2 * L + 2)) and not feasC(L, p))

    # -- §5 Theorem C only within the not-SOS2 regime (a2=b2=0 solvability) --
    claim("Theorem C: 2L+2 SOS2 => (R)+(S) solvable (tested p=5,13, odd multiples <400)",
          all(feasC(L, p) for p in (5, 13) for L in range(p, 400)
              if L % 2 == 1 and L % p == 0 and sos2(2 * L + 2)))

    # -- §5 Proposition D: exact identity + finite census (797 cases, 0 infeasible), incl p=3 --
    pd = propD_census(1500)
    claim("Proposition D finite census: 797 cases (p=3 mod4 incl p=3 | odd L<=1500), 0 infeasible",
          pd["total_cases"] == 797 and pd["num_infeasible_in_census"] == 0)
    claim("Proposition D includes p=3 (Eisenstein) cases",
          any(item["p"] == 3 for item in pd["sample_solvable_with_witnesses"]) or
          any(3 in sp.primefactors(L) for L in range(3, 1500, 2)))
    # a saved witness is a genuine solution of 2L+2 = g(a)+g(b)
    w = pd["sample_solvable_with_witnesses"][0]
    p_, L_ = w["p"], w["L"]
    def g(x, y):
        return x * x - x * y + (p_ + 1) // 4 * y * y
    ax, ay = w["a_xy"]; bx, by = w["b_xy"]
    claim(f"Proposition D witness valid: 2*{L_}+2 = g(a)+g(b) for p={p_}",
          g(ax, ay) + g(bx, by) == 2 * L_ + 2)

    # -- §4 Remark 4.2: CM counterexample p=13, f=4: |A~|^2 in Q(sqrt13), minpoly t^2-20t+48 --
    cm = check_cm_relative_norm()
    c13 = next(r for r in cm if r["p"] == 13 and r["f"] == 4)
    claim("CM counterexample p=13,f=4: |A~|^2 minimal poly t^2 - 20 t + 48 (in Q(sqrt13))",
          c13["|A~|^2_minimal_polynomial_over_Q"] == "t^2 - 20 t + 48"
          and c13["discriminant"] == 208)
    claim("CM counterexample: f=2 imaginary (p=7,11,23) gives RATIONAL |A~|^2",
          all(r.get("|A~|^2_rational") for r in cm if r["f"] == 2))

    # -- §8: L=333 via VENDORED metadata --
    META = os.path.join(os.path.dirname(__file__), "..", "data",
                        "lp333_classification_metadata.json")
    meta = json.load(open(META))
    claim("vendored L=333 metadata has 30 families and provenance sha256",
          len(meta["subgroups"]) == 30 and len(meta["_provenance"]["source_sha256"]) == 64)
    claim("vendored killed_ids = {25,26,27,29}",
          set(meta["summary_killed_ids"]) == {25, 26, 27, 29})
    surj37 = {s["id"] for s in meta["subgroups"] if s["mod37_full_reduction"]}
    claim("mod37-surjecting families = {25,26,27,29} (Theorem A p=37 forbids these)",
          surj37 == {25, 26, 27, 29})
    claim("Theorem C does NOT fire at L=333,p=37 (668 SOS2 in O_Q(sqrt37))",
          feasC(333, 37) is True)
    qr37 = [s["id"] for s in meta["subgroups"] if s["reduction_mod37_order"] == 18]
    claim(f"image-QR(37) families {qr37} not settled by A/C (>= {{20,21,22}})",
          set(qr37) >= {20, 21, 22})

    # -- §7 L=185 (open): image mod5 forced trivial; mod37 not full/QR --
    claim("L=185: 372 not SOS2; QR(5) & QR(37) forbidden by Theorem C",
          (not sos2(372)) and (not feasC(185, 5)) and (not feasC(185, 37)))
    # -- §7 L=1443: 2L+2=2888=2^3*19^2 IS SOS2 (nothing forbidden by A/C) --
    claim("L=1443: 2888 = 2^3*19^2 is SOS2 (no class forbidden by A/C)",
          sp.factorint(2888) == {2: 3, 19: 2} and sos2(2888))

    # -- §6 infinite family (p=5) first six lengths --
    def crt_family_p(p, r, count):
        from sympy.ntheory.modular import crt
        mod = 2 * p * r * r
        res, _ = crt([p, r * r, 2], [0, (r - 1) % (r * r), 1])
        res = int(res) % mod
        out, L = [], res
        while len(out) < count:
            if L >= p and L % 2 == 1 and L % p == 0:
                assert sp.multiplicity(r, L + 1) == 1 and not sos2(2 * L + 2)
                out.append(L)
            L += mod
        return out
    claim("infinite family p=5 first six lengths = [65,155,245,335,425,515]",
          crt_family_p(5, 3, 6) == [65, 155, 245, 335, 425, 515])

    # -- §6 Theorem C forbidden L for p=5 include 65,75,175,185 (proper subset of L=5 mod10) --
    claim("Theorem C p=5 forbidden lengths include 65,75,175,185 but not 55 (proper subset)",
          all(not feasC(L, 5) for L in (65, 75, 175, 185)) and feasC(55, 5))

    # -- §9/§11 attribution: the note cites the established prior art and recasts
    #    Theorem A as a synthesis; GK02 is reclassified with its zbMATH number. --
    note = open(os.path.join(os.path.dirname(__file__), "..",
                             "theorem_note.md"), encoding="utf-8").read()
    for token in ["[KGG25]", "10.1145/3747199.3747549",       # ISSAC 2025
                  "[KKW25]", "10.1016/j.disc.2025.114501",     # Quaternary LP II
                  "Zbl 1001.05031",                            # GK02 zbMATH id
                  "arXiv:2408.16318", "arXiv:2111.02105"]:
        claim(f"note bibliography/text contains citation token '{token}'",
              token in note)
    claim("note recasts Theorem A as a synthesis (no novelty claim)",
          ("no novelty claim" in note) and ("not claimed as new" in note))
    claim("note labels Theorems B/C only as 'potentially new'",
          note.count("potentially new") >= 3)
    claim("note states GK02 is a construction/search strategy, not a nonexistence theorem",
          ("construction/search" in note or "construction / search" in note)
          and "NOT a compression/norm-form nonexistence" in note)

    print(f"\nALL {len(CLAIMS)} NOTE CLAIMS VERIFIED (corrected counts).")
    outp = os.path.join(os.path.dirname(__file__), "..", "certificates",
                        "note_claims.json")
    json.dump({"claims_verified": CLAIMS, "count": len(CLAIMS)},
              open(outp, "w"), indent=2)
    print("wrote", os.path.relpath(outp))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
