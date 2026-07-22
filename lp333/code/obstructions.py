#!/usr/bin/env python3
"""
Rigorous obstruction certificates for common-multiplier-invariant Legendre pairs
of length 333.  Two proven obstructions, each reduced to the single fact that
668 = 2^2 * 167 is NOT a sum of two integer squares (167 is a prime = 3 mod 4
occurring to an odd power).

MOD-3 OBSTRUCTION (reproves prior result, in the orbit language).
  If H contains a unit u with u = 2 (mod 3), then on the mod-3 compression
  (m=3, n=111)  a~_j = sum_{t} a_{j+3t}  the map j -> u j = -j (mod 3) is a
  symmetry, forcing a~_1 = a~_2 and b~_1 = b~_2.  Then
      A~(1) = a~_0 + a~_1(w+w^2) = a~_0 - a~_1   (w = cube root of unity)
  is a rational INTEGER, and likewise B~(1).  The PSD identity gives
      A~(1)^2 + B~(1)^2 = |A(111)|^2 + |B(111)|^2 = 668,
  a sum of two integer squares equal to 668: impossible.
  Hence every viable H lies in ker((Z/333)^* -> (Z/3)^*), order 108.

MOD-37 OBSTRUCTION (new here).
  If H reduces ONTO the full group (Z/37)^* (order 36), then H acts on Z_37 with
  exactly two orbits {0} and {1,...,36}.  On the mod-37 compression (m=37, n=9)
  a~ is H-invariant, hence a~ = (a~_0, c, c, ..., c) (36 equal entries).  For any
  k != 0 (mod 37),
      A~(k) = a~_0 + c * sum_{j=1}^{36} zeta^{jk} = a~_0 - c        (integer),
  and A~(k) = A(9k).  The PSD identity for the nonzero frequency 9k gives
      (a~_0 - c)^2 + (b~_0 - d)^2 = |A(9k)|^2 + |B(9k)|^2 = 668,
  again a sum of two integer squares equal to 668: impossible.
  Hence every H that surjects onto (Z/37)^* admits no invariant Legendre pair.

Both arguments are exact and finite.  This module verifies the structural claims
(orbit collapse) computationally for the concrete subgroups and emits a JSON
certificate.
"""
import json
import os
import math
from core import (L, KERNEL3, all_subgroups, orbits_on_ZL, reduce_subgroup,
                  units, surjects_onto)

HERE = os.path.dirname(__file__)
OUT = os.path.join(HERE, "..", "certificates", "obstruction_certificates.json")


def is_sum_of_two_squares(n):
    x = 0
    while x * x <= n:
        y2 = n - x * x
        y = math.isqrt(y2)
        if y * y == y2:
            return True, (x, y)
        x += 1
    return False, None


def main():
    two_sq, _ = is_sum_of_two_squares(668)
    assert two_sq is False, "668 unexpectedly a sum of two squares"

    cert = {
        "length": L,
        "hadamard_order": 668,
        "core_fact": {
            "statement": "668 = 2^2 * 167 is NOT a sum of two integer squares",
            "reason": "167 is prime and 167 = 3 (mod 4) occurs to an odd power",
            "verified_no_two_square_representation": True,
        },
        "mod3_obstruction": {},
        "mod37_obstruction": {},
    }

    # --- MOD-3: show that any unit == 2 mod 3 collapses the mod-3 compression ---
    # Structural check: the order-2 element that is 1 mod 111-part but -1 mod 3.
    u = None
    for cand in units(L):
        if cand % 3 == 2:
            u = cand
            break
    # Verify the compression symmetry a~_1 = a~_2 is forced by j -> u j on Z_3.
    # (u acts on residues mod 3 as multiplication by 2 = -1.)
    perm3 = {j: (u * j) % 3 for j in range(3)}
    cert["mod3_obstruction"] = {
        "example_unit_2_mod3": u,
        "action_on_Z3": perm3,               # {0:0, 1:2, 2:1}  swaps classes 1,2
        "forces": "a~_1 = a~_2, b~_1 = b~_2, so A~(1),B~(1) are integers",
        "resulting_equation": "A~(1)^2 + B~(1)^2 = 668",
        "conclusion": "impossible; hence H <= ker(reduce mod 3), order 108",
        "kernel_order": len(KERNEL3),
    }
    assert perm3 == {0: 0, 1: 2, 2: 1}

    # --- MOD-37: verify orbit collapse for every subgroup that surjects onto (Z/37)^* ---
    subs = list(all_subgroups(KERNEL3, L))
    killed = []
    for H in subs:
        if not surjects_onto(H, 37):
            continue
        # H acts on Z_37; verify orbits are exactly {0} and {1..36}.
        seen = [False] * 37
        orbs37 = []
        for x in range(37):
            if seen[x]:
                continue
            orb = set()
            stack = [x]
            while stack:
                y = stack.pop()
                if y in orb:
                    continue
                orb.add(y)
                for h in H:
                    seen_val = (h * y) % 37
                    if seen_val not in orb:
                        stack.append(seen_val)
            for y in orb:
                seen[y] = True
            orbs37.append(sorted(orb))
        orbs37.sort(key=lambda o: (len(o), o[0]))
        sizes = [len(o) for o in orbs37]
        collapses = (sizes == [1, 36])
        # also: the nonzero frequency 9k for k=1..36 covers all multiples of 9
        killed.append({
            "generators_min": sorted(H)[:6],
            "order": len(H),
            "reduction_mod37_order": len(reduce_subgroup(H, 37)),
            "orbits_on_Z37_sizes": sizes,
            "compression_constant_on_nonzero_residues": collapses,
            "resulting_equation": "(a~_0 - c)^2 + (b~_0 - d)^2 = 668",
            "conclusion": "impossible",
        })
        assert collapses, "surjecting subgroup did not collapse mod-37 compression"

    cert["mod37_obstruction"] = {
        "criterion": "H reduces ONTO (Z/37)^* (order 36)",
        "num_families_killed": len(killed),
        "families": killed,
    }

    with open(OUT, "w") as f:
        json.dump(cert, f, indent=2)
    print("MOD-3: forced H <= kernel order", len(KERNEL3))
    print("MOD-37: killed families (surject onto (Z/37)^*):", len(killed))
    for k in killed:
        print("   order", k["order"], "orbits on Z37:", k["orbits_on_Z37_sizes"],
              "-> impossible" if k["compression_constant_on_nonzero_residues"] else "??")
    print("wrote", os.path.relpath(OUT))


if __name__ == "__main__":
    main()
