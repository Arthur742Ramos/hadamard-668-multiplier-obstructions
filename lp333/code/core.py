#!/usr/bin/env python3
"""
Core group / orbit / compression machinery for common-multiplier-invariant
Legendre pairs of length L = 333 = 9 * 37  (Hadamard order 2L+2 = 668).

Definitions (all exact, integer arithmetic):

A Legendre pair (LP) of length L is a pair of sequences a, b in {+1,-1}^L with
    PAF_a(s) + PAF_b(s) = -2   for all s = 1, ..., L-1,
where PAF_x(s) = sum_i x_i x_{(i+s) mod L}.  Equivalently, with A(k)=sum_i a_i w^{ik}
(w = exp(2 pi i / L)), the power spectral density condition is
    |A(k)|^2 + |B(k)|^2 = 2L+2 = 668   for all k = 1, ..., L-1,
and the DC terms satisfy (sum a)^2 + (sum b)^2 = 2, i.e. both row sums are +/-1.

A common multiplier group H <= (Z/L)^* acts on Z_L by multiplication.  An
H-invariant LP has a_i = a_{u i mod L} and b_i = b_{u i mod L} for every u in H,
so a and b are constant on the H-orbits of Z_L.
"""
from math import gcd
import itertools

L = 333
MOD9 = 9
MOD37 = 37
N = 2 * L + 2  # 668


# ----------------------------------------------------------------------------
# Units and the mod-3 kernel
# ----------------------------------------------------------------------------
def units(mod=L):
    return [u for u in range(1, mod) if gcd(u, mod) == 1]


UNITS = units(L)                       # (Z/333)^*, order 216
KERNEL3 = [u for u in UNITS if u % 3 == 1]  # units == 1 mod 3, order 108


def mult_order(u, mod=L):
    c, o = u % mod, 1
    while c != 1:
        c = (c * u) % mod
        o += 1
    return o


# ----------------------------------------------------------------------------
# Cyclic subgroup and subgroup-lattice enumeration (abelian group => join-closed
# closure of the cyclic subgroups is the whole lattice).
# ----------------------------------------------------------------------------
def cyclic_subgroup(u, mod=L):
    s, c = set(), 1
    while True:
        s.add(c)
        c = (c * u) % mod
        if c == 1:
            break
    return frozenset(s)


def generated_subgroup(gens, mod=L):
    """Closure of {gens} under multiplication mod `mod` (always contains 1)."""
    s = {1}
    frontier = [1]
    gl = list(gens)
    while frontier:
        x = frontier.pop()
        for g in gl:
            y = (x * g) % mod
            if y not in s:
                s.add(y)
                frontier.append(y)
    return frozenset(s)


def all_subgroups(elements, mod=L):
    """All subgroups of the abelian group `elements` (a subgroup of (Z/mod)^*).

    Computed as the join-closure of the cyclic subgroups: every subgroup is the
    join (product) of the cyclic subgroups of its elements, so repeatedly taking
    products of pairs of already-found subgroups yields the entire lattice.
    """
    cyc = set()
    for u in elements:
        cyc.add(cyclic_subgroup(u, mod))
    subs = set(cyc)
    subs.add(frozenset({1}))
    changed = True
    while changed:
        changed = False
        cur = list(subs)
        for i in range(len(cur)):
            for j in range(i, len(cur)):
                joined = generated_subgroup(cur[i] | cur[j], mod)
                if joined not in subs:
                    subs.add(joined)
                    changed = True
    return subs


# ----------------------------------------------------------------------------
# Orbits of H on Z_L (multiplication action, includes non-units and 0)
# ----------------------------------------------------------------------------
def orbits_on_ZL(H, mod=L):
    seen = [False] * mod
    orbs = []
    Hl = list(H)
    for x in range(mod):
        if seen[x]:
            continue
        orb = set()
        stack = [x]
        while stack:
            y = stack.pop()
            if y in orb:
                continue
            orb.add(y)
            for h in Hl:
                z = (h * y) % mod
                if z not in orb:
                    stack.append(z)
        for y in orb:
            seen[y] = True
        orbs.append(sorted(orb))
    orbs.sort(key=lambda o: (len(o), o[0]))
    return orbs


def orbit_signature(orbs):
    from collections import Counter
    return tuple(sorted(Counter(len(o) for o in orbs).items()))


# ----------------------------------------------------------------------------
# Reductions of a subgroup
# ----------------------------------------------------------------------------
def reduce_subgroup(H, mod):
    return frozenset((u % mod) for u in H)


def surjects_onto(H, mod):
    """Does H reduce onto the full (Z/mod)^*?"""
    target = set(units(mod))
    return reduce_subgroup(H, mod) == frozenset(target)


# ----------------------------------------------------------------------------
# Exact PAF / PSD for concrete +/-1 sequences
# ----------------------------------------------------------------------------
def paf(seq, s):
    L_ = len(seq)
    return sum(seq[i] * seq[(i + s) % L_] for i in range(L_))


def is_legendre_pair(a, b):
    """Exact check: PAF_a(s)+PAF_b(s) = -2 for all s=1..L-1 and row sums +/-1."""
    L_ = len(a)
    if len(b) != L_:
        return False, "length mismatch"
    if sum(a) not in (-1, 1) or sum(b) not in (-1, 1):
        return False, "row sums not +/-1"
    for s in range(1, L_):
        if paf(a, s) + paf(b, s) != -2:
            return False, f"PAF fails at shift {s}"
    return True, "ok"


# ----------------------------------------------------------------------------
# m-compression:  compressed_j = sum_{t} x_{j + t*m},  j = 0..m-1
# Uses that DFT_L(x) at frequency n*k equals DFT_m(compressed) at k  (n=L/m).
# ----------------------------------------------------------------------------
def compress(seq, m):
    n = len(seq) // m
    return [sum(seq[j + t * m] for t in range(n)) for j in range(m)]


if __name__ == "__main__":
    print("L =", L, " units:", len(UNITS), " kernel(mod3):", len(KERNEL3))
    assert len(UNITS) == 216 and len(KERNEL3) == 108
    subs = all_subgroups(KERNEL3, L)
    print("subgroups of kernel(mod3):", len(subs))
    # sanity: orders divide 108
    from collections import Counter
    print("order multiset:", sorted(Counter(len(s) for s in subs).items()))
