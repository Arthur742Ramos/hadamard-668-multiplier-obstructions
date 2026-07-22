#!/usr/bin/env python3
"""
Phase-2 exact core for the sole open common-multiplier family id12 of LP(333).

Family id12:  H = <10, 46> <= (Z/333)^*, order 9.
  * trivial mod 9  (image of H in (Z/9)^* is {1})
  * image mod 37 is K37 = the unique order-9 subgroup of (Z/37)^*.

Because 333 = 9 * 37 and H is trivial mod 9 and K37 mod 37, under the CRT
isomorphism Z_333 ~= Z_9 x Z_37 an H-invariant sequence a is:
    a(c, d)   c in Z_9 (the "column"),  d in Z_37,
and for each fixed column c the length-37 vector a(c, .) is constant on the
K37-orbits of Z_37.  The K37-orbits of Z_37 are:
    {0}  and  four cyclotomic classes C0,C1,C2,C3 (cosets of K37 in (Z/37)^*),
each of size 9.  So each column has one of 2^5 = 32 "types" (a sign per orbit).

This module builds ALL exact integer data used by the search:
  * K37 and the four cyclotomic cosets (C0 = K37 itself);
  * the orbit index of every d in Z_37;
  * per-type column vectors col[t] in {+1,-1}^37 and their column sums;
  * the exact correlation table CC[t1][t2][cl] and cyclotomic tensor M[i][j][cl];
  * the exact quartic Gaussian periods and the period polynomial.

Everything is exact integer arithmetic (no floats in the certified path).
"""
from math import gcd
from fractions import Fraction
from itertools import product
import json

P = 37
NCOL = 9          # columns in Z_9
NORB = 5          # {0}, C0, C1, C2, C3
NTYPE = 32        # 2^5

# ---------------------------------------------------------------------------
# The group H (id12) and its reductions
# ---------------------------------------------------------------------------
H_ELEMENTS = [1, 10, 46, 100, 118, 127, 145, 181, 271]   # order 9, <10,46>


def check_H():
    L = 333
    S = set(H_ELEMENTS)
    assert len(S) == 9
    # closed under multiplication mod 333
    for a in S:
        for b in S:
            assert (a * b) % L in S
        assert gcd(a, L) == 1
    # trivial mod 9
    assert {a % 9 for a in S} == {1}, {a % 9 for a in S}
    # order-9 subgroup mod 37
    K = {a % 37 for a in S}
    assert len(K) == 9
    return K


# ---------------------------------------------------------------------------
# (Z/37)^* is cyclic of order 36.  K37 = unique order-9 subgroup = 4th powers.
# The four cosets of K37 are the cyclotomic classes of order e=4.
# ---------------------------------------------------------------------------
def primitive_root(p=P):
    for g in range(2, p):
        seen = set()
        x = 1
        for _ in range(p - 1):
            x = (x * g) % p
            seen.add(x)
        if len(seen) == p - 1:
            return g
    raise RuntimeError


def build_cosets():
    g = primitive_root(P)                      # generator of (Z/37)^*
    # K37 = <g^4> (order 9).  Cosets C_j = g^j * K37, j = 0..3.
    K = set()
    x = 1
    g4 = pow(g, 4, P)
    for _ in range(9):
        K.add(x)
        x = (x * g4) % P
    assert K == check_H(), (sorted(K), sorted(check_H()))
    cosets = []
    for j in range(4):
        gj = pow(g, j, P)
        cosets.append(sorted((gj * k) % P for k in K))
    # sanity: cosets partition {1..36}
    allc = set()
    for c in cosets:
        allc |= set(c)
    assert allc == set(range(1, P))
    assert all(len(c) == 9 for c in cosets)
    return g, sorted(K), cosets


G_PRIMROOT, K37, COSETS = build_cosets()

# orbit index of each residue d in Z_37:  0 -> orbit 0 ({0}); C_j -> orbit j+1
ORB_OF = [None] * P
ORB_OF[0] = 0
for j, c in enumerate(COSETS):
    for d in c:
        ORB_OF[d] = j + 1
assert all(o is not None for o in ORB_OF)

# representative shift for each orbit class (class 0 uses rep 0)
REPS = [0] + [COSETS[j][0] for j in range(4)]     # length 5


# ---------------------------------------------------------------------------
# Column types.  Bit i (i=0..4) is the sign on orbit i (0 -> +1, 1 -> -1).
# ---------------------------------------------------------------------------
def type_signs(t):
    """Return (eps0, eps1, eps2, eps3, eps4) in {+1,-1} for type t in 0..31."""
    return tuple(-1 if (t >> i) & 1 else 1 for i in range(NORB))


def col_vector(t):
    eps = type_signs(t)
    return [eps[ORB_OF[d]] for d in range(P)]


COL = [col_vector(t) for t in range(NTYPE)]
COLSUM = [sum(v) for v in COL]


# ---------------------------------------------------------------------------
# Correlation table.  CC[t1][t2][cl] = sum_d col[t1][d]*col[t2][(d+rep_cl)%37].
# Cyclotomic tensor M[i][j][cl] = #{ d in orbit i : (d+rep_cl)%37 in orbit j }.
# ---------------------------------------------------------------------------
def build_M():
    M = [[[0] * NORB for _ in range(NORB)] for _ in range(NORB)]
    for cl in range(NORB):
        sh = REPS[cl]
        for d in range(P):
            i = ORB_OF[d]
            j = ORB_OF[(d + sh) % P]
            M[i][j][cl] += 1
    return M


M_TENSOR = build_M()


def build_CC():
    CC = [[[0] * NORB for _ in range(NTYPE)] for _ in range(NTYPE)]
    for t1 in range(NTYPE):
        c1 = COL[t1]
        for t2 in range(NTYPE):
            c2 = COL[t2]
            for cl in range(NORB):
                sh = REPS[cl]
                CC[t1][t2][cl] = sum(c1[d] * c2[(d + sh) % P] for d in range(P))
    return CC


CC_TABLE = build_CC()


def cc_from_M(t1, t2, cl):
    """Cross-check CC via M and the type signs."""
    e1 = type_signs(t1)
    e2 = type_signs(t2)
    return sum(e1[i] * e2[j] * M_TENSOR[i][j][cl]
               for i in range(NORB) for j in range(NORB))


# ---------------------------------------------------------------------------
# Column-sum classification (the 9-compression structure).
# colsum(t) = eps0*1 + 9*(eps1+eps2+eps3+eps4).
# ---------------------------------------------------------------------------
def classify_types():
    small, big, excluded = [], [], []
    for t in range(NTYPE):
        cs = COLSUM[t]
        if abs(cs) == 1:
            small.append(t)
        elif abs(cs) == 17:
            big.append(t)
        else:
            excluded.append(t)
    return small, big, excluded


if __name__ == "__main__":
    K = check_H()
    print("primitive root mod 37:", G_PRIMROOT)
    print("K37 (order-9 subgroup):", K37)
    for j, c in enumerate(COSETS):
        print(f"  coset C{j}:", c)
    print("-1 mod 37 is in orbit-class:", ORB_OF[36], "(expect a cyclotomic class)")
    print("REPS:", REPS)

    # Cross-check CC == cc_from_M everywhere
    bad = 0
    for t1 in range(NTYPE):
        for t2 in range(NTYPE):
            for cl in range(NORB):
                if CC_TABLE[t1][t2][cl] != cc_from_M(t1, t2, cl):
                    bad += 1
    print("CC vs M cross-check mismatches:", bad)
    assert bad == 0

    # Column-sum values available
    vals = sorted(set(COLSUM))
    print("distinct column sums:", vals)

    small, big, excluded = classify_types()
    print(f"#small(|sum|=1): {len(small)}   #big(|sum|=17): {len(big)}   "
          f"#excluded: {len(excluded)}")
    print("small types:", small, "sums:", [COLSUM[t] for t in small])
    print("big types:", big, "sums:", [COLSUM[t] for t in big])
    print("excluded sums:", sorted({COLSUM[t] for t in excluded}))

    # Print cyclotomic tensor M for nonzero classes (the classical order-4
    # cyclotomic numbers restricted to nonzero orbits).
    print("\nCyclotomic tensor M[i][j][cl] for nonzero i,j,cl "
          "(i,j,cl in 1..4 = C0..C3):")
    for cl in range(1, NORB):
        print(f" shift class C{cl-1} (rep {REPS[cl]}):")
        for i in range(1, NORB):
            print("   ", [M_TENSOR[i][j][cl] for j in range(1, NORB)])

    # Sanity: total sum of col[t] autocorrelation identity etc.
    print("\nAutocorrelation of a couple types (CC[t][t][cl]):")
    for t in [0, 1, small[0], big[0]]:
        print(f"  type {t} signs {type_signs(t)} colsum {COLSUM[t]}: "
              f"{[CC_TABLE[t][t][cl] for cl in range(NORB)]}")
