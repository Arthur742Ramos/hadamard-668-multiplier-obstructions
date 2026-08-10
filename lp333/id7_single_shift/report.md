# A single-shift orbit obstruction for multiplier ID 7

## Theorem

No Legendre pair `A,B in {+1,-1}^333` has both rows fixed by

```text
H = <73,112> = {1,73,112,184,223,295}.
```

This excludes common-multiplier classification family ID 7.

## Elementary proof

Under `Z/333Z = Z/9Z x Z/37Z`, the subgroup has the direct-product image

```text
H = {1,4,7} x {+1,-1}.
```

The shift `111` has CRT coordinates `(3,0)`. The points `x` and `x+111` lie in
the same `H`-orbit exactly when some `(u,epsilon) in H` satisfies

```text
u*x9 = x9+3 (mod 9),    epsilon*x37 = x37 (mod 37).
```

Choose `epsilon=+1`. If `x9` is 1 modulo 3, `u=4` works; if `x9` is 2 modulo
3, `u=7` works. When `x9` is 0 modulo 3, no `u in {1,4,7}` works. Thus exactly
six of the nine mod-9 classes, with all 37 mod-37 classes, give forced-equal
terms:

```text
#{x : Hx = H(x+111)} = 6*37 = 222.
```

For any `H`-invariant sign sequence `X`, those 222 terms contribute `+1` to
`PAF_X(111)` and each of the remaining 111 terms contributes at least `-1`.
Consequently

```text
PAF_X(111) >= 222-111 = 111.
```

If both rows of a pair are `H`-invariant, their combined PAF at shift 111 is
at least 222, contradicting the Legendre-pair requirement that it equal `-2`.

## Independent exact strengthening

The repository verifier also constructs the full multiplication-orbit map and
minimizes the shift-111 quadratic form component by component. The 111
unforced terms form one weight-1 triangle and 18 weight-2 triangles. Their
combined minimum is `-37`, so the exact one-row minimum is

```text
min PAF_X(111) = 222-37 = 185.
```

This strengthening is not needed for the elementary contradiction; it is kept
as an independent structural check.

## Verification

Run from the repository root:

```bash
python3 lp333/id7_single_shift/code/standalone_verifier.py
```

The dependency-free checker derives ID 7 from its generators, verifies its CRT
image and orbit signature, obtains the 222 count both from explicit multiplier
witnesses and from an independently constructed orbit map, proves the exact
minimum 185, and includes a mutation control that disables the obstruction.

## Provenance and attribution

The elementary 222-term single-shift observation was shared for expert review
in an AI-assisted research note coordinated by **Dennison Bertram**, who
explicitly did not claim personal derivation, priority, or novelty. This module
independently rederived and checked the observation before integration. The
exact-minimum strengthening and certificate packaging were added during the
repository integration.

## Classification consequence

The common-multiplier classification now contains 25 impossible groups. The
open IDs are `0,1,3,4,5`; no order-6 family remains open.

## Scope

This is a symmetry-class exclusion. It does not prove unrestricted
nonexistence of a length-333 Legendre pair or a Hadamard matrix of order 668.
