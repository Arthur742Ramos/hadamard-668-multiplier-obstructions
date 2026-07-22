#!/usr/bin/env python3
"""
families.py -- corollaries of the compression theorems, stated as FORBIDDEN
FIXED-SYMMETRY CLASSES (H-invariant Legendre pairs with a prescribed image mod p),
NOT as excluded lengths:
  (A) INFINITE families of forbidden (length, surjecting-symmetry) classes, with a
      rigorous CRT/Dirichlet construction (Theorem A) plus a verified batch.
  (B) SIMULTANEOUS per-prime image restrictions for composite L: at each prime
      p | L the admissible image of a multiplier group is constrained, all at once.
  (C) the density statement: for a density-1 set of odd multiples of a fixed prime
      p, the class 'H surjects onto (Z/p)^*' is forbidden.

A forbidden class means: no H-invariant Legendre pair of that length with that
image exists.  It does NOT mean the length has no Legendre pair at all.
Everything printed is checked exactly; a machine-readable certificate is written.
"""
import json
import os
from math import gcd, isqrt

import sympy as sp


def sos2(n):
    if n == 0:
        return True
    for q, e in sp.factorint(n).items():
        if q % 4 == 3 and e % 2 == 1:
            return False
    return True


def units(m):
    return [u for u in range(1, m) if gcd(u, m) == 1]


def cyclic_group(u, m):
    s, c = {1}, u % m
    while c != 1:
        s.add(c)
        c = (c * u) % m
    return sorted(s)


def has_primitive_root_lift(L, p):
    """Does (Z/L)^* contain a unit whose image mod p is a primitive root
    (i.e. surjects onto (Z/p)^*)?  Always true by CRT surjectivity; we exhibit one."""
    for u in units(L):
        if len(cyclic_group(u % p, p)) == p - 1:
            return u
    return None


def theoremC_real_index2_feasible(L, p):
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


def smallest_r_3mod4_coprime(p):
    r = 3
    while True:
        if r % 4 == 3 and (2 * p) % r != 0 and sp.isprime(r):
            return r
        r += 1


def crt_infinite_family(p, count=12):
    """Theorem A infinite family for fixed prime p:
    choose r = 3 (mod 4) prime, r doesn't divide 2p.  Solve
        L = 0 (mod p),  L = r-1 (mod r^2),  L = 1 (mod 2).
    Then L is odd, p | L, and v_r(L+1) = 1 (odd) so L+1 (hence 2L+2) is NOT a
    sum of two squares.  The solutions form an AP with common difference 2 p r^2,
    hence are infinite.  We emit the first `count` and VERIFY each."""
    r = smallest_r_3mod4_coprime(p)
    mod = 2 * p * r * r
    # find base residue via CRT
    from sympy.ntheory.modular import crt
    res, m = crt([p, r * r, 2], [0, (r - 1) % (r * r), 1])
    res = int(res) % mod
    fam = []
    L = res if res > 0 else res + mod
    # ensure L >= p and grow
    while len([f for f in fam]) < count:
        if L >= p and L % 2 == 1 and L % p == 0:
            assert sp.multiplicity(r, L + 1) == 1        # v_r(L+1) = 1
            assert not sos2(2 * L + 2)
            u = has_primitive_root_lift(L, p)
            assert u is not None
            fam.append({"L": L, "2L+2": 2 * L + 2, "r": r,
                        "v_r(L+1)": 1, "not_sos2": True,
                        "surjective_H_generator_mod{}".format(L): u})
        L += mod
    return {"p": p, "r_used": r, "common_difference": mod,
            "construction": ("L = 0 (mod p), L = r-1 (mod r^2), L odd; "
                             "v_r(L+1)=1 so 2L+2 not a sum of two squares; "
                             "infinitely many such L (an arithmetic progression)."),
            "examples": fam}


def simultaneous_restrictions(L):
    """For composite odd L, list per-prime admissible images of a multiplier
    group under the theorems.  For each prime p | L:
      - Theorem A kills image = (Z/p)^*  iff 2L+2 not SOS2;
      - Theorem C kills image = QR(p) (p=1 mod4) iff the (R)+(S) system is
        infeasible;
      - Proposition B (p=3 mod4, image=QR) gives no closed kill.
    The 'surviving images' are those not excluded."""
    N = 2 * L + 2
    out = {"L": L, "2L+2": N, "N_sos2": sos2(N), "primes": {}}
    for p in sorted(sp.primefactors(L)):
        pm1 = p - 1
        info = {"p": p, "p_mod4": p % 4}
        # image = full (Z/p)^*
        info["full_image_killed_by_A"] = (not sos2(N))
        # image = QR(p), index 2 (exists as a subgroup of (Z/p)^*)
        if p == 2:
            info["qr_case"] = "n/a"
        elif p % 4 == 1:
            info["qr_image_killed_by_C"] = (not theoremC_real_index2_feasible(L, p))
            info["qr_case"] = "real quadratic Q(sqrt %d) (Theorem C)" % p
        else:
            info["qr_image_killed_by_C"] = False
            info["qr_case"] = "imaginary Q(sqrt -%d): Proposition B non-obstructive" % p
        out["primes"][p] = info
    return out


def main():
    cert = {}

    # (A) infinite families for several primes
    cert["infinite_families_theoremA"] = [crt_infinite_family(p)
                                          for p in [3, 5, 7, 11, 13, 37]]
    print("== Infinite families of FORBIDDEN surjecting-symmetry classes "
          "(Theorem A) ==")
    for fam in cert["infinite_families_theoremA"]:
        Ls = [e["L"] for e in fam["examples"][:6]]
        print(f" p={fam['p']:3d}: r={fam['r_used']}, first lengths L = {Ls} ... "
              f"(AP diff {fam['common_difference']}, infinite); the class "
              f"'H surjects onto (Z/{fam['p']})^*' is forbidden for each")

    # (C) density: for a density-1 set of lengths the surjecting class is forbidden
    dens = {}
    for p in [3, 5, 7, 13, 37]:
        odd_mults = [L for L in range(p, 4001, 1) if L % 2 == 1 and L % p == 0]
        forb = [L for L in odd_mults if not sos2(2 * L + 2)]
        dens[p] = {"odd_multiples_of_p_upto_4000": len(odd_mults),
                   "surjecting_class_forbidden": len(forb),
                   "fraction": round(len(forb) / len(odd_mults), 4)}
    cert["density_theoremA"] = {
        "statement": ("For each fixed prime p, the odd multiples L of p with "
                      "2L+2 not a sum of two squares have natural density 1 "
                      "among odd multiples of p (Landau-Ramanujan: sums of two "
                      "squares have density 0).  For each such L the fixed-symmetry "
                      "class 'H surjects onto (Z/p)^*' is FORBIDDEN.  This forbids "
                      "symmetry classes, not lengths: an LP of length L may still "
                      "exist with a smaller-image (or trivial) multiplier group."),
        "empirical_note": ("empirical fractions up to 4000 are a finite-range "
                           "under-estimate that tends to 1 like 1 - O(1/sqrt(log X))"),
        "empirical": dens}
    print("\n== Density of lengths where the surjecting class is forbidden "
          "(empirical, up to 4000; -> 1 asymptotically) ==")
    for p, d in dens.items():
        print(f" p={p:3d}: {d['surjecting_class_forbidden']}/"
              f"{d['odd_multiples_of_p_upto_4000']} = {d['fraction']}")

    # (B) simultaneous per-prime image restrictions (including open length 185)
    Ls = [185, 333, 111, 55, 65, 1443, 555]
    cert["simultaneous_restrictions"] = [simultaneous_restrictions(L) for L in Ls]
    print("\n== Simultaneous per-prime FORBIDDEN images (composite L) ==")
    for r in cert["simultaneous_restrictions"]:
        L = r["L"]
        parts = []
        for p, info in r["primes"].items():
            tag = []
            if info.get("full_image_killed_by_A"):
                tag.append("full:forbidden(A)")
            if info.get("qr_image_killed_by_C"):
                tag.append("QR:forbidden(C)")
            parts.append(f"p={p}[{','.join(tag) if tag else 'none forbidden by A/C'}]")
        print(f" L={L:5d} (2L+2={r['2L+2']}, sos2={r['N_sos2']}): " + "; ".join(parts))

    cert["spotlight_L185"] = simultaneous_restrictions(185)

    outp = os.path.join(os.path.dirname(__file__), "..", "certificates",
                        "families.json")
    with open(outp, "w") as f:
        json.dump(cert, f, indent=2)
    print("\nwrote", os.path.relpath(outp))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
