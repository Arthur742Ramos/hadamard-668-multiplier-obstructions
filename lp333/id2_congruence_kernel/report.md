# A congruence-kernel obstruction for multiplier ID 2

## Theorem

No Legendre pair `A,B in {+1,-1}^333` has even one row fixed by

```text
K = <112> = {1,112,223}
  = ker((Z/333Z)^x -> (Z/111Z)^x).
```

In particular, classification family ID 2, which requires both rows to be
fixed by `K`, is impossible.

## Proof

Write every index uniquely as `n = r + 111t`, where `0 <= r < 111` and
`t in Z/3Z`. For a sign sequence `X`, call the three entries with fixed `r`
a fibre, and let `mu(X)` be the number of monochromatic fibres.

The contribution of one fibre to `PAF_X(111)` is the sum of its three cyclic
adjacent products. It is `3` for a monochromatic fibre and `-1` for any other
sign pattern. Hence

```text
PAF_X(111) = 3*mu(X) - (111-mu(X)) = 4*mu(X)-111.
```

The Legendre equation at shift 111 now gives

```text
-2 = PAF_A(111)+PAF_B(111)
   = 4*(mu(A)+mu(B))-222,
```

so `mu(A)+mu(B)=55`.

Multiplication by `112=1+111` acts within the fibre over `r` by

```text
t -> t+r (mod 3).
```

For each of the 74 residues `r` not divisible by 3 this action is a 3-cycle.
An invariant row must therefore be constant on all 74 of those fibres, so it
has `mu(X) >= 74`. This contradicts the required two-row total 55. The
argument needs invariance of only one row.

## Verification

Run from the repository root:

```bash
python3 lp333/id2_congruence_kernel/code/standalone_verifier.py
```

The dependency-free checker derives the subgroup and quotient kernel, verifies
the multiplier action on all 111 fibres, exhausts all eight local sign
patterns, and checks every nonnegative fibre-count solution of the shift-111
Legendre equation. It writes
`results/obstruction_certificate.json` deterministically.

## Provenance and independent corroboration

The fibre-count obstruction was contributed in
[issue #2](https://github.com/Arthur742Ramos/hadamard-668-multiplier-obstructions/issues/2)
by Claude, an AI research partner working with Patrick White. This repository
module independently rederives their proof sketch in its certificate format.

Benedek “Ben” Blackthorn independently obtained the obstruction and proved a
broader prime-square theorem, including affine symmetries, with a Lean 4
formalization. That work is archived as
[doi:10.5281/zenodo.21779001](https://doi.org/10.5281/zenodo.21779001).

## Classification consequence

The common-multiplier classification now contains 24 impossible groups. The
open IDs are `0,1,3,4,5,7`.

## Scope

This is a symmetry-class exclusion. It does not prove unrestricted
nonexistence of a length-333 Legendre pair or a Hadamard matrix of order 668.
