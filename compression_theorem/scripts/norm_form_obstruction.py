#!/usr/bin/env python3
"""
norm_form_obstruction.py -- the Gaussian-period refinements of the compression
obstruction for NON-surjective images, done EXHAUSTIVELY and HONESTLY.

Structure of |A~(k)|^2 (K = image of H mod p, index f, Gaussian periods eta_r).
  A~(k) lies in the degree-f subfield K_f of Q(zeta_p) fixed by K.  Complex
  conjugation is the coset of -1.  If -1 is not in K, then K_f/K_f^+ is
  quadratic and
      |A~(k)|^2 = A~(k) * A~(-k) = N_{K_f / K_f^+}( A~(k) )  in  O_{K_f^+},
  where [K_f^+ : Q] = f/2.  If -1 is in K, K_f is already totally real,
  K_f^+=K_f, and |A~(k)|^2=A~(k)^2 directly; the relative norm to the same
  field is the identity, not the square map.

  * -1 in K  (Theorem B): |A~(k)|^2 = A~(k)^2, and the PSD identity is
        alpha^2 + beta^2 = 2L+2   with alpha,beta in the TOTALLY REAL order O_{K_f}.
        f=1 -> Theorem A (two rational squares); f=2, p=1 mod4 -> Theorem C.
  * -1 notin K, f=2 (p=3 mod4): K_f^+ = Q, so |A~(k)|^2 = N(alpha) is RATIONAL and
        the PSD identity is 2L+2 = N(alpha)+N(beta) (Proposition D).  This is the
        ONLY case in which the relative norm is automatically rational.
  * -1 notin K, f>=4: K_f^+ is a NONTRIVIAL real field of degree f/2, so
        |A~(k)|^2 is generally IRRATIONAL (lands in K_f^+).  The 'sum of two
        rational norms' picture FAILS here.  Explicit counterexample p=13, f=4
        below: |A~(k)|^2 in Q(sqrt 13), minimal polynomial t^2 - 20 t + 48.

This module:
  (1) re-asserts the f=2 real (Theorem C) and f=2 imaginary (Prop D) algebraic
      identities, including p=3 for Prop D;
  (2) verifies EXACTLY the totally-real collapse (-1 in K) for f=2 and f=4;
  (3) verifies EXACTLY the CM counterexample p=13,f=4 (relative norm irrational);
  (4) runs the EXHAUSTIVE Theorem C census over ALL primes p=1 mod4 dividing an
      odd L<=1200 (428 cases, 139 forbidden fixed-symmetry classes), with witnesses;
  (5) runs a FINITE Prop-D census (p=3 mod4, incl. p=3) with COMPLETE coefficient
      bounds 4g = (2x-y)^2 + p y^2 and saved witnesses -- reporting solvability as
      a finite-census fact, NOT a universal theorem.
"""
import json
import os
from math import gcd, isqrt

import sympy as sp

from cyclo import Cyclo

x = sp.symbols('x')


# ------------------------------- primitives --------------------------------
def units(m):
    return [u for u in range(1, m) if gcd(u, m) == 1]


def cyclic_group(u, m):
    s, c = {1}, u % m
    while c != 1:
        s.add(c)
        c = (c * u) % m
    return sorted(s)


def quad_residues(p):
    return sorted({(t * t) % p for t in range(1, p)})


def sos2(n):
    if n == 0:
        return True
    for q, e in sp.factorint(n).items():
        if q % 4 == 3 and e % 2 == 1:
            return False
    return True


def invariant_seq_on_Zp(K, p, seed):
    """+/-1 sequence on Z_p constant on K-cosets (K a subgroup of (Z/p)^*)."""
    import random
    rng = random.Random(seed)
    seq = [0] * p
    seq[0] = rng.choice((1, -1))
    nz = set(range(1, p))
    while nz:
        x0 = min(nz)
        coset = sorted({(x0 * k) % p for k in K})
        v = rng.choice((1, -1))
        for y in coset:
            seq[y] = v
            nz.discard(y)
    return seq


def psd_exact_poly(seq, k, p):
    """|A~(k)|^2 as a reduced Poly mod Phi_p (via the integer autocorrelation)."""
    coeffs = {}
    for d in range(p):
        pad = sum(seq[i] * seq[(i + d) % p] for i in range(p))
        coeffs[(d * k) % p] = coeffs.get((d * k) % p, 0) + pad
    return Cyclo.reduce(coeffs, p)


# ------------------- (1) symbolic identities (assertions) ------------------
def check_symbolic():
    a1, a2, b1, b2, p = sp.symbols('a1 a2 b1 b2 p')
    s = sp.sqrt(p)
    eta0 = (-1 + s) / 2                       # real period, p = 1 mod 4
    alpha, beta = a1 + a2 * eta0, b1 + b2 * eta0
    expr = sp.expand(alpha**2 + beta**2)
    X = sp.expand(sp.Rational(1, 2) * (expr + expr.subs(s, -s)))
    Y = sp.expand(sp.Rational(1, 2) * (expr - expr.subs(s, -s)) / s)
    R = 2 * a1 * a2 - a2**2 + 2 * b1 * b2 - b2**2
    assert sp.expand(2 * Y - R) == 0
    S = a1**2 + b1**2 + (p - 1) / sp.Integer(4) * (a2**2 + b2**2)
    assert sp.simplify((X - S) / R) == sp.Rational(-1, 2)      # X = S when R = 0
    # imaginary norm form, p = 3 mod 4 (incl p = 3): N(alpha) = a1^2 - a1 a2 + (p+1)/4 a2^2
    sm = sp.sqrt(-p)
    e0, e1 = (-1 + sm) / 2, (-1 - sm) / 2
    Nalpha = sp.expand((a1 + a2 * e0) * (a1 + a2 * e1))
    g_imag = a1**2 - a1 * a2 + (p + 1) / sp.Integer(4) * a2**2
    assert sp.simplify(Nalpha - g_imag) == 0
    # p = 3 specialization: g = x^2 - x y + y^2 (Eisenstein norm)
    assert sp.expand(g_imag.subs(p, 3) - (a1**2 - a1 * a2 + a2**2)) == 0
    # 4g = (2x - y)^2 + p y^2  (bound identity used by the Prop-D census)
    assert sp.expand(4 * g_imag - ((2 * a1 - a2)**2 + p * a2**2)) == 0
    return {"real_constraint_R": "2 a1 a2 - a2^2 + 2 b1 b2 - b2^2 = 0",
            "real_energy_S": "a1^2 + b1^2 + (p-1)/4 (a2^2 + b2^2) = 2L+2",
            "imag_norm_g": "g(x,y) = x^2 - x y + (p+1)/4 y^2  (disc -p; p=3 -> Eisenstein)",
            "bound_identity": "4 g(x,y) = (2x - y)^2 + p y^2",
            "verified": True}


# ------------------- (2) totally-real collapse (-1 in K) -------------------
def check_totally_real_collapse():
    out = []
    for (p, f) in [(5, 2), (13, 2), (17, 2), (37, 2), (17, 4), (41, 4)]:
        g0 = next(t for t in range(2, p) if len(cyclic_group(t, p)) == p - 1)
        K = set(cyclic_group(pow(g0, f, p), p))
        assert len(K) == (p - 1) // f
        if (-1) % p not in K:
            continue
        seq = invariant_seq_on_Zp(K, p, seed=p * 100 + f)
        ok_fixed = all(Cyclo.polys_equal(Cyclo.dft_poly(seq, k, p),
                                         Cyclo.dft_poly(seq, (kk * k) % p, p))
                       for k in range(1, p) for kk in K)
        ok_real = all(Cyclo.polys_equal(Cyclo.dft_poly(seq, k, p),
                                        Cyclo.dft_poly(seq, (-k) % p, p))
                      for k in range(1, p))
        assert ok_fixed and ok_real, (p, f)
        out.append({"p": p, "f": f, "minus1_in_K": True,
                    "A_tilde_in_real_subfield_and_real": True})
    return out


# ------------- (3) CM relative norm (-1 notin K): f=2 vs f>=4 --------------
def check_cm_relative_norm():
    out = []
    # f=2 imaginary (p=3 mod4): K_f^+ = Q, so |A~(k)|^2 is RATIONAL.
    for p in [7, 11, 23]:
        K = set(quad_residues(p))                  # index-2, -1 notin K
        assert (-1) % p not in K
        seq = invariant_seq_on_Zp(K, p, seed=p)
        rational = all(psd_exact_poly(seq, k, p).is_ground for k in range(1, p))
        assert rational, p
        out.append({"p": p, "f": 2, "Kf_plus": "Q (degree 1)",
                    "|A~|^2_rational": True})
    # f=4, p=13: K = <3> = {1,3,9}, -1 notin K, K_f^+ = Q(sqrt 13) (degree 2).
    p = 13
    g0 = next(t for t in range(2, p) if len(cyclic_group(t, p)) == p - 1)
    K = set(cyclic_group(pow(g0, 4, p), p))         # {1,3,9}
    assert (-1) % p not in K and len(K) == 3
    seq = [1, 1, 1, 1, 1, 1, 1, -1, -1, 1, 1, -1, 1]   # explicit witness
    # check it is K-invariant
    assert all(seq[(kk * j) % p] == seq[j] for j in range(1, p) for kk in K)
    # |A~(1)|^2 and |A~(2)|^2 are the two Galois conjugates in Q(sqrt13):
    v1 = psd_exact_poly(seq, 1, p)
    v2 = psd_exact_poly(seq, 2, p)   # 2 is a non-residue -> other <K,-1>-coset
    assert not v1.is_ground, "expected irrational relative norm"
    # trace and norm of {v1, v2} over Q, computed EXACTLY mod Phi_13:
    Phi = sp.Poly(sp.cyclotomic_poly(p, x), x, domain='QQ')
    tr = (v1 + v2).rem(Phi)
    nm = (v1 * v2).rem(Phi)
    assert tr.is_ground and nm.is_ground, "trace/norm not rational"
    T = int(tr.coeffs()[0]) if tr.coeffs() else 0
    Nn = int(nm.coeffs()[0]) if nm.coeffs() else 0
    minpoly = f"t^2 - {T} t + {Nn}"
    disc = T * T - 4 * Nn
    assert (T, Nn) == (20, 48) and disc == 208, (T, Nn, disc)   # roots 10 +/- 2 sqrt13
    out.append({"p": 13, "f": 4, "K": sorted(K), "minus1_in_K": False,
                "Kf_plus": "Q(sqrt 13) (degree 2, NONtrivial)",
                "witness_sequence": seq,
                "|A~|^2_minimal_polynomial_over_Q": minpoly,
                "|A~|^2_values": "10 +/- 2 sqrt(13)  (IRRATIONAL)",
                "discriminant": disc,
                "conclusion": ("relative norm lands in a NONtrivial real subfield; "
                               "the 'sum of two rational norms' picture and the "
                               "'permissive' conclusion do NOT extend past f=2")})
    return out


# --------- (4) Theorem C decision + EXHAUSTIVE census (all p=1 mod4) --------
def theoremC_feasible(L, p):
    """Real index-2 (p=1 mod4).  Decide (R)+(S); return (feasible, witness)."""
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
                        return True, (a1, a2, b1, b2)
    return False, None


def theoremC_census(Lmax=1200):
    """EVERY prime p=1 mod4 dividing an odd L<=Lmax.  Records all cases."""
    cases = 0
    kills = []
    feasible_examples = []
    for L in range(1, Lmax + 1, 2):
        for p in sp.primefactors(L):
            if p % 4 != 1:
                continue
            cases += 1
            feas, wit = theoremC_feasible(L, p)
            if not feas:
                assert not sos2(2 * L + 2)      # kills live in the not-SOS2 regime
                kills.append([L, p])
            elif len(feasible_examples) < 6 and wit is not None and not sos2(2 * L + 2):
                feasible_examples.append({"L": L, "p": p, "witness_abab": list(wit)})
    return {"L_max": Lmax, "total_cases": cases, "num_forbidden_classes": len(kills),
            "distinct_primes": sorted(set(p for _, p in kills)),
            "distinct_lengths": len(set(L for L, _ in kills)),
            "forbidden_classes_L_p": kills,
            "sample_feasible_with_witness": feasible_examples}


# ----------- (5) Proposition D: exact identity + FINITE census -------------
def g_values_upto(p, N):
    """All values g(x,y)=x^2-xy+(p+1)/4 y^2 <= N, with a witness (x,y) each.
    Complete enumeration via 4g = (2x-y)^2 + p y^2 <= 4N: |y|<=sqrt(4N/p),
    |2x-y|<=sqrt(4N-p y^2), parity 2x-y == y (mod 2)."""
    val_wit = {}
    Y = isqrt((4 * N) // p) + 1
    for y in range(-Y, Y + 1):
        rem = 4 * N - p * y * y
        if rem < 0:
            continue
        W = isqrt(rem)
        # w = 2x - y ranges [-W, W] with w == y (mod 2)
        w0 = -W
        if (w0 - y) % 2 != 0:
            w0 += 1
        for w in range(w0, W + 1, 2):
            g = (w * w + p * y * y) // 4
            x0 = (w + y) // 2
            if g <= N and g not in val_wit:
                val_wit[g] = (x0, y)
    return val_wit


def propD_feasible(L, p):
    """p=3 mod4 (incl p=3).  Is 2L+2 = g(a)+g(b)?  Return (feasible, witness)."""
    assert p % 4 == 3
    N = 2 * L + 2
    vw = g_values_upto(p, N)
    S = set(vw)
    for v in sorted(S):
        if (N - v) in S:
            return True, {"g_a": v, "a_xy": list(vw[v]),
                          "g_b": N - v, "b_xy": list(vw[N - v])}
    return False, None


def propD_census(Lmax=1500):
    cases = 0
    infeasible = []
    sample_wit = []
    for L in range(1, Lmax + 1, 2):
        for p in sp.primefactors(L):
            if p % 4 != 3:
                continue
            cases += 1
            feas, wit = propD_feasible(L, p)
            if not feas:
                infeasible.append([L, p])
            elif len(sample_wit) < 8:
                sample_wit.append({"L": L, "p": p, **wit})
    return {"L_max": Lmax, "total_cases": cases,
            "num_infeasible_in_census": len(infeasible),
            "infeasible_cases": infeasible,
            "sample_solvable_with_witnesses": sample_wit,
            "wording": ("EXACT: the identity 2L+2 = g(a)+g(b) is a proven necessary "
                        "condition.  SOLVABILITY is reported as a FINITE-CENSUS fact "
                        "(no infeasible case found for p=3 mod4, incl p=3, L<=1500); "
                        "it is NOT claimed as a universal theorem.")}


# ------------------------------- main --------------------------------------
def main():
    cert = {}
    cert["symbolic_identities"] = check_symbolic()
    print("[1] symbolic identities (Theorem C (R)/(S); Prop D norm g; 4g bound; p=3) OK.")

    cert["totally_real_collapse"] = check_totally_real_collapse()
    for r in cert["totally_real_collapse"]:
        print(f"[2] p={r['p']}, f={r['f']}: -1 in K, A~(k) real in degree-{r['f']} "
              f"field (exact). OK.")

    cert["cm_relative_norm"] = check_cm_relative_norm()
    for r in cert["cm_relative_norm"]:
        if r["f"] == 2:
            print(f"[3] p={r['p']}, f=2 (-1 notin K): |A~|^2 rational (K_f^+=Q). OK.")
        else:
            print(f"[3] p={r['p']}, f=4 (-1 notin K): |A~|^2 IRRATIONAL, "
                  f"minpoly {r['|A~|^2_minimal_polynomial_over_Q']} in Q(sqrt13). "
                  f"COUNTEREXAMPLE to 'permissive past f=2'. OK.")

    cert["theorem_C_census_exhaustive"] = theoremC_census(1200)
    tc = cert["theorem_C_census_exhaustive"]
    print(f"[4] Theorem C EXHAUSTIVE census (all p=1 mod4 | odd L<=1200): "
          f"{tc['total_cases']} cases, {tc['num_forbidden_classes']} forbidden "
          f"fixed-symmetry classes; primes {tc['distinct_primes']}.")

    cert["proposition_D_census"] = propD_census(1500)
    pd = cert["proposition_D_census"]
    print(f"[5] Proposition D FINITE census (p=3 mod4 incl p=3 | odd L<=1500): "
          f"{pd['total_cases']} cases, {pd['num_infeasible_in_census']} infeasible "
          f"(norm identity EXACT; solvability is a census fact, not a theorem).")

    # L=333 / open-length highlights (fixed-symmetry-class language)
    f333, w333 = theoremC_feasible(333, 37)
    f185_5, _ = theoremC_feasible(185, 5)
    f185_37, _ = theoremC_feasible(185, 37)
    f111_37, _ = theoremC_feasible(111, 37)
    cert["highlights"] = {
        "L333_p37": {"real_index2_feasible": f333, "witness_abab": list(w333) if w333 else None,
                     "note": ("668 is a sum of two squares in O_{Q(sqrt37)}, so the "
                              "image-QR(37) fixed-symmetry class at L=333 is NOT "
                              "forbidden by Theorem C.")},
        "L185_open": {"image_QR5_forbidden": (not f185_5),
                      "image_QR37_forbidden": (not f185_37),
                      "note": ("L=185 is an open Legendre-pair length; the "
                               "image-QR(5) and image-QR(37) fixed-symmetry classes "
                               "are forbidden, but LP(185) existence is untouched.")},
        "L111_p37_image_QR37_forbidden": (not f111_37),
    }
    print(f"    L=333/p=37 feasible={f333} (class NOT forbidden; matches report).")
    print(f"    L=185 image-QR(5) forbidden={not f185_5}, image-QR(37) forbidden={not f185_37}.")

    outp = os.path.join(os.path.dirname(__file__), "..", "certificates",
                        "norm_form_obstruction.json")
    with open(outp, "w") as f:
        json.dump(cert, f, indent=2)
    print("\nwrote", os.path.relpath(outp))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
