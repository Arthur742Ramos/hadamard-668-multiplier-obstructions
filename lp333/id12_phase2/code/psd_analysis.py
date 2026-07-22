#!/usr/bin/env python3
"""
Gaussian-period / DFT-PSD analysis for id12 -- ILLUSTRATIVE SUPPORTING MATERIAL.

This file merely PLACES the elementary 9-compression impossibility proof inside
the quartic-Gaussian-period PSD picture.  It is NOT part of the proof: the
certified argument (standalone_verifier.py, master_certificate.py) is purely
elementary and integer.  The Galois-collapse check below uses floating-point
DFTs and is an illustration only, not a certificate.

Setup.  a(c,d), c in Z_9, d in Z_37, constant on the K37-orbits of d.  Its
length-333 DFT factors as
    A(k9,k37) = sum_c zeta9^{c k9} * Ahat_c(k37),
    Ahat_c(k37) = sum_d a(c,d) zeta37^{d k37}.
For k37 in the cyclotomic coset C_m, Ahat_c(k37) = eps0(c) + sum_{a=0..3} eta_{a+m} eps_{Ca}(c),
so with the column "value" W_a(c) = eps0(c) + sum_a eta_a eps_{Ca}(c) in Z[eta],
    A(k9, C_m) = sigma^m( Atil(k9) ),   Atil(k9) = sum_c zeta9^{c k9} W_a(c),
where sigma: eta_j -> eta_{j+1} is the order-4 Galois automorphism.  Hence the 4
coset-frequencies (fixed k9) are Galois conjugates and the PSD condition
    |A(k9,C_m)|^2 + |B(k9,C_m)|^2 = 668   (all m)
collapses to a SINGLE ring identity  |Atil(k9)|^2 + |Btil(k9)|^2 = 668.

The k37=0 (trivial-character) frequencies are the DIRECT orbit evaluation: the
trivial character sends a(c,.) to its plain sum over Z_37, i.e. the column sum
  colsum(c) = sum_{orbit i} eps_i(c) * |orbit i|   (orbit sizes 1,9,9,9,9),
so A(k9,0) = sum_c zeta9^{c k9} colsum(c) is the length-9 DFT of the column sums.
THIS trivial-character slice, together with the K37 value-set restriction, is
exactly the elementary 9-compression obstruction that proves id12 impossible.

The Galois collapse and DFT factorization are illustrated numerically below.
"""
import cmath
import math
import random
import json
import os
import phase2_core as pc
import periods as pr

P = 37


def numeric_dft_full(a):
    """A(k) = sum_i a_i w^{ik}, w=exp(2pi i/333), returned for all k."""
    L = 333
    w = cmath.exp(2j * math.pi / L)
    return [sum(a[i] * w ** ((i * k) % L) for i in range(L)) for k in range(L)]


def build_invariant(rng):
    typ = [[rng.choice([1, -1]) for _ in range(pc.NORB)] for _ in range(9)]
    a = [0] * 333
    for i in range(333):
        a[i] = typ[i % 9][pc.ORB_OF[i % 37]]
    return a, typ


def col_values_in_ring(typ):
    """W(c) in Z[eta] basis (a0,a1,a2,a3) for each column c, from its 5 signs.
    W(c) = eps0 + eps_{C0} eta0 + eps_{C1} eta1 + eps_{C2} eta2 + eps_{C3} eta3.
    (orbit index: 0={0}->eps0 (rational), 1..4 -> C0..C3 -> eta0..eta3)"""
    W = []
    for c in range(9):
        e = typ[c]                       # e[0]=eps0, e[1..4]=eps on C0..C3
        val = (e[0], 0, 0, 0)            # eps0 * 1
        for a in range(4):
            val = pr.add(val, pr.scal(pr.eta_basis(a), e[1 + a]))
        W.append(val)
    return W


def sigma(x, times=1):
    """Apply eta_j -> eta_{j+1} `times` times to ring element x (basis form)."""
    for _ in range(times % 4):
        # x = x0 + x1 eta1 + x2 eta2 + x3 eta3 ; sigma(eta_j)=eta_{j+1}
        # eta0->eta1, eta1->eta2, eta2->eta3, eta3->eta0 = -1-eta1-eta2-eta3
        x0, x1, x2, x3 = x
        res = [x0, 0, 0, 0]
        res[2] += x1                       # x1 eta1 -> x1 eta2
        res[3] += x2                       # x2 eta2 -> x2 eta3
        # x3 eta3 -> x3 eta0 = x3(-1-eta1-eta2-eta3)
        res[0] += -x3; res[1] += -x3; res[2] += -x3; res[3] += -x3
        x = tuple(res)
    return x


def verify_galois_collapse2(trials=60):
    """Correct symbolic-numeric check: build Atil(k9) as sum_c z9^{ck9} W(c)
    keeping W(c) in Z[eta] and z9^{ck9} as complex scalar; then A(k9,C_m) equals
    the value obtained by replacing each eta_j by eta_{j+m} (=sigma^m) and
    evaluating.  We verify against the direct length-333 DFT."""
    rng = random.Random(7)
    z9 = cmath.exp(2j * math.pi / 9)
    coset_rep = [pc.COSETS[m][0] for m in range(4)]
    # precompute CRT index for (k9, coset_rep[m])
    def crt(k9, k37):
        for kk in range(333):
            if kk % 9 == k9 % 9 and kk % 37 == k37:
                return kk
    maxerr = 0.0
    for _ in range(trials):
        a, typ = build_invariant(rng)
        A = numeric_dft_full(a)
        W = col_values_in_ring(typ)
        for k9 in range(9):
            # coeff of each period in Atil(k9): Atil = sum_c z9^{ck9} W(c)
            # keep as 4 complex coeffs c0 + c1 eta1 + c2 eta2 + c3 eta3
            coeff = [0j, 0j, 0j, 0j]
            for c in range(9):
                s = z9 ** ((c * k9) % 9)
                for t in range(4):
                    coeff[t] += s * W[c][t]
            for m in range(4):
                # sigma^m on the ring element (coeff over basis 1,eta1,eta2,eta3)
                el = (coeff[0], coeff[1], coeff[2], coeff[3])
                el_m = sigma(el, m)
                val = (el_m[0]
                       + el_m[1] * pr.ETA_NUM[1]
                       + el_m[2] * pr.ETA_NUM[2]
                       + el_m[3] * pr.ETA_NUM[3])
                k = crt(k9, coset_rep[m])
                maxerr = max(maxerr, abs(A[k] - val))
    return {"trials": trials, "max_abs_error": maxerr,
            "numeric_illustration_ok": maxerr < 1e-6,
            "note": "NUMERIC ILLUSTRATION ONLY (floating-point DFT); not a "
                    "certificate. Shows A(k9,C_m)=sigma^m(Atil(k9)), so the 4 "
                    "coset PSD equations per k9 collapse to one ring equation."}


def compression_is_trivial_character():
    """Show the 9-compression = the k37=0 (trivial-character) PSD slice, by
    DIRECT orbit evaluation: the trivial character sends a column to its plain
    sum over Z_37, which equals sum_{orbit i} eps_i * |orbit i|.  We verify this
    against the direct column-vector sum (no ring specialization)."""
    # orbit sizes of Z_37 under K37 (sizes 1,9,9,9,9), indexed by ORB_OF
    orbit_size = [0] * pc.NORB
    for d in range(pc.P):
        orbit_size[pc.ORB_OF[d]] += 1
    ok = True
    for t in range(pc.NTYPE):
        e = pc.type_signs(t)
        # direct trivial-character value = sum over orbits of eps_i * |orbit i|
        colsum_direct = sum(e[i] * orbit_size[i] for i in range(pc.NORB))
        # and the plain sum of the length-37 column vector
        colsum_vector = sum(pc.COL[t])
        ok &= (colsum_direct == colsum_vector == pc.COLSUM[t])
    return {"orbit_sizes": orbit_size,
            "direct_orbit_evaluation_matches_column_sum": ok,
            "conclusion": "k37=0 slice = 9-compression pair (column sums by "
                          "direct orbit evaluation); with atilde_j in V this is "
                          "the elementary obstruction."}


if __name__ == "__main__":
    out = {}
    print("psd_analysis.py -- ILLUSTRATIVE supporting material (not a certificate).")
    print("Galois collapse A(k9,C_m)=sigma^m(Atil(k9)) NUMERIC illustration ...")
    out["galois_collapse_numeric_illustration"] = verify_galois_collapse2()
    print("   ", out["galois_collapse_numeric_illustration"])
    out["compression_trivial_char"] = compression_is_trivial_character()
    print("   compression = trivial character (direct orbit evaluation):",
          out["compression_trivial_char"]["direct_orbit_evaluation_matches_column_sum"])
    out["period_polynomial_exact"] = "x^4 + x^3 + 5x^2 + 7x + 49 (see periods.py)"
    outp = os.path.join(os.path.dirname(__file__), "..", "results",
                        "psd_analysis.json")
    json.dump(out, open(outp, "w"), indent=2)
    print("wrote", outp)
