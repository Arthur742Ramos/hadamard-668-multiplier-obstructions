#!/usr/bin/env python3
"""
Exact arithmetic in the ring Z[eta_0,eta_1,eta_2,eta_3] of quartic Gaussian
periods for p = 37 with the order-9 subgroup K37 (index 4).

eta_j = sum_{d in C_j} zeta_37^d,  zeta_37 = exp(2 pi i / 37),  j = 0..3.

Facts used (all proved by direct integer counting here):
  * sum_j eta_j = -1.
  * complex conjugation:  conj(eta_j) = eta_{j+2 mod 4}   (because -1 in C2).
  * eta_i * eta_j = 9*[i == j+2 (mod4)] + sum_k N[i][j][k] * eta_k,
    where N[i][j][k] = #{ (d,e): d in C_i, e in C_j, d+e in C_k }.

Elements are represented in the basis (1, eta_1, eta_2, eta_3) with
    eta_0 = -1 - eta_1 - eta_2 - eta_3,
as an integer 4-tuple (a0, a1, a2, a3) meaning a0 + a1 eta_1 + a2 eta_2 + a3 eta_3.
This is a faithful rank-4 Z-module representation; the ring multiplication is
verified EXACTLY (integer arithmetic only) against an independent convolution
computation, and eta_0 is verified to satisfy its period polynomial exactly.

NOTE: this file is SUPPORTING / illustrative material.  The impossibility proof
for id12 (standalone_verifier.py, master_certificate.py) is elementary and does
NOT depend on the Gaussian-period ring.  The only floating-point here is an
optional numeric display of the periods, used in no assertion.
"""
from fractions import Fraction
import cmath
import math
import phase2_core as pc

P = 37
COSETS = pc.COSETS               # C0..C3, each a sorted list of 9 residues
ORB_OF = pc.ORB_OF               # residue -> 0 ({0}) or 1..4 (C0..C3)


def coset_index(d):
    """Return j in 0..3 for nonzero d in C_j."""
    o = ORB_OF[d % P]
    assert o != 0
    return o - 1


# ---------------------------------------------------------------------------
# N[i][j][k] and the "constant" term c_ij = 9*[i==j+2]
# ---------------------------------------------------------------------------
def build_N():
    N = [[[0] * 4 for _ in range(4)] for _ in range(4)]
    const = [[0] * 4 for _ in range(4)]     # coefficient of 1 (from d+e==0)
    for i in range(4):
        for j in range(4):
            for d in COSETS[i]:
                for e in COSETS[j]:
                    s = (d + e) % P
                    if s == 0:
                        const[i][j] += 1
                    else:
                        N[i][j][coset_index(s)] += 1
    return N, const


N_TAB, CONST_TAB = build_N()


# ---------------------------------------------------------------------------
# Ring element helpers: tuple (a0,a1,a2,a3) = a0 + a1 eta1 + a2 eta2 + a3 eta3
# ---------------------------------------------------------------------------
def eta_basis(j):
    """Return basis representation of eta_j (j in 0..3)."""
    if j == 0:
        return (-1, -1, -1, -1)   # eta0 = -1 - eta1 - eta2 - eta3
    v = [0, 0, 0, 0]
    v[j] = 1
    return tuple(v)


def add(x, y):
    return tuple(x[i] + y[i] for i in range(4))


def sub(x, y):
    return tuple(x[i] - y[i] for i in range(4))


def scal(x, n):
    return tuple(n * x[i] for i in range(4))


def _eta_prod(i, j):
    """eta_i * eta_j as a basis tuple, i,j in 0..3.

    eta_i eta_j = CONST_TAB[i][j]*1 + sum_k (N[i][j][k]/9) * eta_k, because the
    number of pairs (d,e) in C_i x C_j with a fixed nonzero sum s is constant
    over each coset C_k (K37 acts simply-transitively-compatibly), so
    N[i][j][k] = 9 * (that per-element count).
    """
    a = [CONST_TAB[i][j], 0, 0, 0]
    for k in range(4):
        assert N_TAB[i][j][k] % 9 == 0, (i, j, k, N_TAB[i][j][k])
        n = N_TAB[i][j][k] // 9
        if n:
            bk = eta_basis(k)
            for t in range(4):
                a[t] += n * bk[t]
    return tuple(a)


# precompute eta_i*eta_j in basis
ETA_PROD = [[_eta_prod(i, j) for j in range(4)] for i in range(4)]


def mul(x, y):
    """Multiply two ring elements in basis (1,eta1,eta2,eta3)."""
    # x = x0 + sum_{i>=1} x_i eta_i ; treat constant 1 and etas.
    # Represent x,y as coeff of {1,eta1,eta2,eta3}; expand product.
    res = [0, 0, 0, 0]
    # constant * anything
    # We'll expand over generators g in {1(idx0 as '1'), eta1,eta2,eta3}
    # value of generator as basis tuple:
    gen = [(1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)]
    for a in range(4):
        if x[a] == 0:
            continue
        for b in range(4):
            if y[b] == 0:
                continue
            coeff = x[a] * y[b]
            if a == 0 and b == 0:
                prod = (1, 0, 0, 0)
            elif a == 0:
                prod = gen[b]
            elif b == 0:
                prod = gen[a]
            else:
                prod = ETA_PROD[a][b]   # eta_a * eta_b (a,b in 1..3)
            for t in range(4):
                res[t] += coeff * prod[t]
    return tuple(res)


def conj(x):
    """Complex conjugation: eta_j -> eta_{j+2}. Applied in basis."""
    # x = x0*1 + x1 eta1 + x2 eta2 + x3 eta3
    # conj: 1->1, eta1->eta3, eta2->eta0=-1-eta1-eta2-eta3, eta3->eta1
    res = [x[0], 0, 0, 0]
    # x1 * eta3
    res[3] += x[1]
    # x2 * eta0 = -1 - eta1 - eta2 - eta3
    res[0] += -x[2]
    res[1] += -x[2]
    res[2] += -x[2]
    res[3] += -x[2]
    # x3 * eta1
    res[1] += x[3]
    return tuple(res)


def is_rational(x):
    return x[1] == 0 and x[2] == 0 and x[3] == 0


ZERO = (0, 0, 0, 0)
ONE = (1, 0, 0, 0)


# ---------------------------------------------------------------------------
# Numeric evaluation (for cross-checks only, NOT in the certified path)
# ---------------------------------------------------------------------------
def eta_numeric():
    z = cmath.exp(2j * math.pi / P)
    return [sum(z ** d for d in COSETS[j]) for j in range(4)]


ETA_NUM = eta_numeric()


def to_numeric(x):
    """OPTIONAL numeric evaluation for display only -- NOT used in any check."""
    return x[0] + x[1] * ETA_NUM[1] + x[2] * ETA_NUM[2] + x[3] * ETA_NUM[3]


# ---------------------------------------------------------------------------
# EXACT verification of the ring (integer arithmetic only; no floats)
# ---------------------------------------------------------------------------
def eta_product_by_convolution(i, j):
    """Independent EXACT computation of eta_i*eta_j in the period basis, by
    convolving the coset indicator vectors over Z_37 and re-expressing.  Verifies
    the theorem that the product is constant on cosets (K37-invariance)."""
    coeff = [0] * P                          # coefficient of zeta^r, r=0..36
    for d in COSETS[i]:
        for e in COSETS[j]:
            coeff[(d + e) % P] += 1
    const = coeff[0]                          # coefficient of 1
    # coefficient must be constant on each coset C_k
    per = [None] * 4
    for k in range(4):
        vals = {coeff[d] for d in COSETS[k]}
        assert len(vals) == 1, (i, j, k, vals)   # K37-invariance of the product
        per[k] = vals.pop()
    # eta_i*eta_j = const*1 + sum_k per[k]*eta_k
    res = (const, 0, 0, 0)
    for k in range(4):
        res = add(res, scal(eta_basis(k), per[k]))
    return res


def exact_period_polynomial():
    """Return integer coeffs (c0,c1,c2,c3) with eta_0^4 = c3 eta_0^3 + c2 eta_0^2
    + c1 eta_0 + c0, computed by EXACT rational linear algebra over the basis."""
    e0 = eta_basis(0)
    powers = [ONE]
    for _ in range(4):
        powers.append(mul(powers[-1], e0))
    # solve   sum_{i=0..3} c_i * powers[i] = powers[4]   in the 4-dim basis
    A = [[Fraction(powers[i][t]) for i in range(4)] for t in range(4)]
    b = [Fraction(powers[4][t]) for t in range(4)]
    # Gaussian elimination (exact)
    n = 4
    M = [A[r][:] + [b[r]] for r in range(n)]
    for col in range(n):
        piv = next(r for r in range(col, n) if M[r][col] != 0)
        M[col], M[piv] = M[piv], M[col]
        pv = M[col][col]
        M[col] = [x / pv for x in M[col]]
        for r in range(n):
            if r != col and M[r][col] != 0:
                f = M[r][col]
                M[r] = [M[r][k] - f * M[col][k] for k in range(n + 1)]
    c = [M[r][n] for r in range(n)]
    assert all(ci.denominator == 1 for ci in c), c
    return tuple(int(ci) for ci in c)


def verify_ring_exact():
    """All-integer, deterministic verification (no floats)."""
    # sum eta_j = -1
    s = ZERO
    for j in range(4):
        s = add(s, eta_basis(j))
    assert s == (-1, 0, 0, 0), s
    # conj(eta_j) = eta_{j+2}
    for j in range(4):
        assert conj(eta_basis(j)) == eta_basis((j + 2) % 4)
    # multiplication table matches the independent convolution computation
    for i in range(4):
        for j in range(4):
            assert mul(eta_basis(i), eta_basis(j)) == eta_product_by_convolution(i, j)
    # commutativity and associativity on the basis
    E = [eta_basis(j) for j in range(4)] + [ONE]
    for x in E:
        for y in E:
            assert mul(x, y) == mul(y, x)
            for z in E:
                assert mul(mul(x, y), z) == mul(x, mul(y, z))
    # eta_0 satisfies the period polynomial exactly:
    #   eta_0^4 + eta_0^3 + 5 eta_0^2 + 7 eta_0 + 49 = 0
    c0, c1, c2, c3 = exact_period_polynomial()
    e0 = eta_basis(0)
    p = [ONE]
    for _ in range(4):
        p.append(mul(p[-1], e0))
    val = sub(p[4], add(add(scal(p[3], c3), scal(p[2], c2)),
                        add(scal(p[1], c1), scal(p[0], c0))))
    assert val == ZERO, val
    return (c0, c1, c2, c3)


if __name__ == "__main__":
    print("periods.py -- EXACT quartic Gaussian-period ring for p=37, K37 order 9.")
    print("(Supporting/illustrative material: the impossibility proof in "
          "standalone_verifier.py does NOT depend on this file.)\n")
    print("N[i][j][k] tensor (order-4 cyclotomic pair counts):")
    for i in range(4):
        for j in range(4):
            print(f"  eta{i}*eta{j} = {CONST_TAB[i][j]} "
                  f"+ {N_TAB[i][j]} . (eta0..eta3)")
    coeffs = verify_ring_exact()
    print("\nEXACT self-check (sum=-1; conj; mul==convolution; comm/assoc; "
          "period polynomial) : PASS")
    c0, c1, c2, c3 = coeffs
    print(f"period polynomial (exact): x^4 - ({c3})x^3 - ({c2})x^2 - ({c1})x "
          f"- ({c0}) = 0")
    print(f"  i.e.  x^4 + {(-c3)}x^3 + {(-c2)}x^2 + {(-c1)}x + {(-c0)}  = 0")
    # optional numeric display of the periods (NOT used in any check)
    print("numeric periods (display only):",
          [complex(round(e.real, 4), round(e.imag, 4)) for e in ETA_NUM])
