#!/usr/bin/env python3
"""
verify_core.py  --  Exact verification of the compression / DFT facts underlying
the multiplier-compression obstruction theorem (Theorem A) and its Gaussian-
period refinement (Theorem B).

Exactness:
  * Cyclotomic identities are checked EXACTLY by reducing modulo Phi_L(x)
    (see cyclo.py).  No floating point is used for any asserted equality.
  * The PSD identity for genuine Legendre pairs is verified through the exact
    integer autocorrelation identity
        |A(k)|^2 + |B(k)|^2 = sum_d (PAF_a+PAF_b)(d) * zeta^{dk}.

Verifications (positive controls):
  (V1) Genuine Legendre pairs (a,b), L in {3,5,7,9,11,13}: the defining relation
       PAF_a(s)+PAF_b(s) = -2 (s != 0) holds, hence |A(k)|^2+|B(k)|^2 = 2L+2 for
       all k != 0 (proved exactly via the autocorrelation identity).
  (V2) Djokovic-Kotsireas compression/DFT identity  A(k * L/p) = A_tilde(k),
       exact mod Phi_L, over the genuine LPs for every prime p | L.
  (V3) SURJECTIVE COLLAPSE (Theorem A hypothesis): H-invariant sequence with
       image of H mod p equal to (Z/p)^* => p-compression is (t0, c, ..., c)
       and A_tilde(k) = t0 - c is a rational integer for all k != 0 (mod p).
       Verified exactly mod Phi_p.
  (V4) Number facts: 2L+2 not SOS2 <=> L+1 not SOS2 <=> some q=3 (mod 4) divides
       L+1 to an odd power.  Verified over a range and for 668/334.
  (V5) GAUSSIAN-PERIOD COLLAPSE (Theorem B hypothesis): p = 3 (mod 4), H-invariant
       sequence with image of H mod p equal to the index-2 subgroup QR(p); then
       the p-compression is constant on QR and on QNR, A_tilde(1) = alpha lies in
       Z[eta] = O_{Q(sqrt(-p))}, |A_tilde(k)|^2 = N(alpha) is the SAME rational
       integer for every k != 0, and it equals the value of the principal norm
       form  x^2 - x y + ((p+1)/4) y^2.  Verified exactly.

Exit status 0 == all assertions passed.
"""
import itertools
import json
import os
import random
import sys
from math import gcd, isqrt

import sympy as sp

from cyclo import Cyclo


# ------------------------- combinatorial primitives -------------------------
def paf(seq, s):
    L = len(seq)
    return sum(seq[i] * seq[(i + s) % L] for i in range(L))


def paf_vector(seq):
    L = len(seq)
    return tuple(paf(seq, s) for s in range(1, L))


def is_legendre_pair(a, b):
    L = len(a)
    if sum(a) not in (-1, 1) or sum(b) not in (-1, 1):
        return False
    return all(paf(a, s) + paf(b, s) == -2 for s in range(1, L))


def find_one_lp(L):
    """One Legendre pair of length L via a PAF-vector dictionary (fast)."""
    by_vec = {}
    seqs = []
    for bits in itertools.product((1, -1), repeat=L - 1):
        s = (1,) + bits
        if sum(s) in (-1, 1):
            seqs.append(s)
    for s in seqs:
        by_vec.setdefault(paf_vector(s), s)
    for a in seqs:
        need = tuple(-2 - v for v in paf_vector(a))
        if need in by_vec:
            return list(a), list(by_vec[need])
    return None


def compress(seq, m):
    n = len(seq) // m
    return [sum(seq[j + t * m] for t in range(n)) for j in range(m)]


def units(mod):
    return [u for u in range(1, mod) if gcd(u, mod) == 1]


def cyclic_group(u, mod):
    s, c = {1}, u % mod
    while c != 1:
        s.add(c)
        c = (c * u) % mod
    return sorted(s)


def is_sum_of_two_squares(n):
    x0 = 0
    while x0 * x0 <= n:
        y2 = n - x0 * x0
        y = isqrt(y2)
        if y * y == y2:
            return True
        x0 += 1
    return False


def sos2_by_factorization(n):
    if n == 0:
        return True
    for q, e in sp.factorint(n).items():
        if q % 4 == 3 and e % 2 == 1:
            return False
    return True


def make_invariant_sequence(H, L, rng):
    val = {}
    for x0 in range(L):
        if x0 in val:
            continue
        orb = set()
        stack = [x0]
        while stack:
            y = stack.pop()
            if y in orb:
                continue
            orb.add(y)
            for h in H:
                stack.append((h * y) % L)
        v = rng.choice((1, -1))
        for y in orb:
            val[y] = v
    return [val[i] for i in range(L)]


def quad_residues(p):
    return sorted({(t * t) % p for t in range(1, p)})


# ------------------------------- the checks --------------------------------
def main():
    report = {"V1": [], "V2": [], "V3": [], "V4": {}, "V5": []}
    rng = random.Random(20260722)

    # ---- V4 ----------------------------------------------------------------
    for n in range(1, 2000):
        assert is_sum_of_two_squares(n) == sos2_by_factorization(n), n
    for n in range(1, 1000):
        assert sos2_by_factorization(2 * n) == sos2_by_factorization(n), n
    assert not sos2_by_factorization(668) and not sos2_by_factorization(334)
    report["V4"] = {"checked_range": 2000, "668_sos2": False, "334_sos2": False,
                    "2n_iff_n_verified": True}
    print("[V4] SOS2 facts OK (range 2000; 668,334 not SOS2; 2n<=>n).")

    # ---- V1 + V2 -----------------------------------------------------------
    for L in [3, 5, 7, 9, 11, 13]:
        primes = sorted(set(sp.primefactors(L)))
        lp = find_one_lp(L)
        assert lp is not None, f"no LP at L={L}"
        a, b = lp
        assert is_legendre_pair(a, b)
        target = 2 * L + 2

        # V1: exact PSD identity via autocorrelation.
        for k in range(1, L):
            coeffs = {}
            for d in range(L):
                pad = L if d == 0 else paf(a, d)
                pbd = L if d == 0 else paf(b, d)
                coeffs[(d * k) % L] = coeffs.get((d * k) % L, 0) + (pad + pbd)
            red = Cyclo.reduce(coeffs, L)
            assert Cyclo.equals_integer(red, target, L), (L, k)
        report["V1"].append({"L": L, "psd_identity_exact": True, "target": target})

        # V2: compression DFT identity, exact mod Phi_L.
        for p in primes:
            n = L // p
            at = compress(a, p)
            for k in range(1, p):
                lhs = Cyclo.dft_poly(a, (k * n) % L, L)      # A(k L/p) in zeta_L
                coeffs = {}
                for j, s in enumerate(at):
                    e = (n * j * k) % L
                    coeffs[e] = coeffs.get(e, 0) + s
                rhs = Cyclo.reduce(coeffs, L)
                assert Cyclo.polys_equal(lhs, rhs), (L, p, k)
        report["V2"].append({"L": L, "primes": primes, "compression_dft_ok": True})
        print(f"[V1,V2] L={L}: exact PSD identity + compression DFT identity OK "
              f"(primes {primes}).")

    # ---- V3: surjective collapse ------------------------------------------
    v3_cases = [(333, 37), (333, 3), (45, 5), (45, 3), (63, 7), (63, 3),
                (55, 11), (55, 5), (21, 7), (21, 3), (117, 3), (185, 5)]
    for (L, p) in v3_cases:
        prim = next(u for u in units(L) if len(cyclic_group(u % p, p)) == p - 1)
        H = cyclic_group(prim, L)
        assert sorted(set(h % p for h in H)) == units(p), (L, p)
        seq = make_invariant_sequence(H, L, rng)
        at = compress(seq, p)
        assert len(set(at[1:])) == 1, (L, p, at)   # constant on nonzero residues
        t0, c = at[0], at[1]
        for k in range(1, p):
            coeffs = {}
            for j, s in enumerate(at):
                coeffs[(j * k) % p] = coeffs.get((j * k) % p, 0) + s
            red = Cyclo.reduce(coeffs, p)
            assert Cyclo.equals_integer(red, t0 - c, p), (L, p, k)
        report["V3"].append({"L": L, "p": p, "prim_root_lift": prim,
                             "A_tilde_const_int": int(t0 - c)})
        print(f"[V3] L={L}, p={p}: A_tilde(k) = {t0 - c} in Z for all k!=0. OK.")

    # ---- V5: Gaussian-period (index-2, imaginary quadratic) collapse -------
    v5_cases = [(21, 7), (55, 11), (69, 23), (33, 11), (63, 7)]
    for (L, p) in v5_cases:
        if p % 4 != 3:
            continue
        QR = set(quad_residues(p))
        g0 = next(t for t in range(2, p) if len(cyclic_group(t, p)) == p - 1)
        genQR = (g0 * g0) % p
        prim = next((u for u in units(L)
                     if set(cyclic_group(u % p, p)) == QR), None)
        if prim is None:
            prim = next(u for u in units(L) if u % p == genQR)
        H = cyclic_group(prim, L)
        img = set(h % p for h in H)
        assert img == QR, (L, p, sorted(img), sorted(QR))
        seq = make_invariant_sequence(H, L, rng)
        at = compress(seq, p)
        QNR = set(range(1, p)) - QR
        assert len(set(at[j] for j in QR)) == 1
        assert len(set(at[j] for j in QNR)) == 1
        u0 = at[min(QR)]
        u1 = at[min(QNR)]
        t0 = at[0]
        norms = []
        for k in range(1, p):
            coeffs = {}
            for d in range(p):
                pad = sum(at[i] * at[(i + d) % p] for i in range(p))
                coeffs[(d * k) % p] = coeffs.get((d * k) % p, 0) + pad
            red = Cyclo.reduce(coeffs, p)
            assert red.is_ground, (L, p, k, "PSD not a rational integer")
            norms.append(int(red.coeffs()[0]) if red.coeffs() else 0)
        assert len(set(norms)) == 1, (L, p, norms)
        Nalpha = norms[0]
        re = t0 - sp.Rational(u0 + u1, 2)
        im = sp.Rational(u0 - u1, 2) * sp.sqrt(p)
        Nclosed = sp.nsimplify(re**2 + im**2)
        assert sp.simplify(Nclosed - Nalpha) == 0, (L, p, Nclosed, Nalpha)
        X, Y = t0 - u1, u0 - u1
        form = X * X - X * Y + sp.Rational(p + 1, 4) * Y * Y
        assert sp.simplify(form - Nalpha) == 0, (L, p, form, Nalpha)
        report["V5"].append({"L": L, "p": p, "field": f"Q(sqrt(-{p}))",
                             "N_alpha_constant": Nalpha,
                             "matches_principal_form": True})
        print(f"[V5] L={L}, p={p}: index-2 collapse -> |A_tilde(k)|^2 = N(alpha) "
              f"= {Nalpha} (constant; principal form of disc -{p}). OK.")

    print("\nALL CORE VERIFICATIONS PASSED.")
    outp = os.path.join(os.path.dirname(__file__), "..", "certificates",
                        "core_verification.json")
    with open(outp, "w") as f:
        json.dump(report, f, indent=2)
    print("wrote", os.path.relpath(outp))
    return 0


if __name__ == "__main__":
    sys.exit(main())
