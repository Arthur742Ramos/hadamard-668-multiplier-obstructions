# Exact analysis of Eliahou's 64-modular order-668 construction

## Scope

This directory reconstructs the explicit 64-modular matrix from:

Shalom Eliahou, *A 64-modular Hadamard matrix of order 668*,
Australasian Journal of Combinatorics 93 (2025), 422-428.

The modular matrix is not treated as a real Hadamard matrix. Every full
668-by-668 check uses integer arithmetic.

## Reconstructed reduced data

The published run lengths expand to two sequences `s,q` of length 167:

```text
q runs: 83,2,81,1
s runs: 4^5 (2,1,1)^5 (1,5) 4^4 (2,1,1)^6
        4^4 (3) (1,2,1)^5 (3) 4^4 (3) (1,2,1)^5
```

Runs alternate signs starting with `+1`. The Goethals-Seidel quadruple is

```text
(s, s', s*q, (s*q)')
```

where `'` negates positions 85 through 167 and `*` is pointwise product.
The reconstruction reproduces all 13 published aperiodic defects:

```text
lag:   4    8    12   16   26  30   34   38   42   46   50   54   58
def: -512  384  -256  128  -64 128 -192  256 -320  256 -192  128  -64
```

The full exact Gram check found:

- all 222,778 off-diagonal products divisible by 64;
- 8,684 nonzero off-diagonal products;
- maximum absolute product 512;
- therefore 64-modular and not a real Hadamard matrix.

## Base-sequence equivalence

Split `s=X||Y` and `s*q=Z||W`, with lengths `(84,83,84,83)`. For lags
1 through 83, the full quadruple's aperiodic defect is exactly twice

```text
c_X(k)+c_Y(k)+c_Z(k)+c_W(k).
```

For larger lags it cancels identically. Thus an exact lift in this special form
is exactly a base sequence `BS(84,83)`.

The modular seed has base row sums `(-2,3,0,-1)`, whose squared total is 14.
An exact base sequence requires squared total 334. Row sums alone permit a
profile at Hamming distance 8, namely `(-18,3,0,-1)`, so the DC equation by
itself does **not** justify a large-distance claim.

## Rigorous exact-lift distance bound

At lag 4 the combined base autocorrelation is `-256`. One base-sign flip can
change at most two lag-4 products, each by magnitude 2. Therefore `r` flips can
change this defect by at most `4r`. Reaching zero requires

```text
4r >= 256,
```

so every exact `BS(84,83)` lift differs from this modular seed in at least
**64 base signs**.

This bound is analytic. It does not depend on a solver.

Exact CP-SAT searches at distance 64 used the equality consequences of the
lag-4 bound (every flip has two negative incident lag-4 edges and no two flips
are lag-4 adjacent). Both searches remained `UNKNOWN`:

- all 13 currently defective lags;
- all 83 exact base-sequence equations.

Therefore no claim is made about existence or nonexistence at distance 64.

## Attempted 128-modular lift

A special-form 128-modular matrix requires every combined base aperiodic
correlation to be divisible by 64. The seed fails at exactly five lags:

```text
26,34,42,50,58.
```

At lag 58 the base defect is `-32`. Lag-58 pairs form a matching within each
base sequence, so one sign flip changes at most one product, by magnitude 2.
Reaching the nearest multiple of 64 therefore requires at least **16 flips**.

At exactly 16 flips there are only two tight lag-58 targets, 0 and -64.
Complete CP-SAT models for both branches returned `INFEASIBLE`. Consequently,
within this special-form base-sequence family, every 128-modular lift differs
from the seed in at least **17 base signs**. This last step is a reproducible
exact solver result, not a standalone proof trace.

An unrestricted 30-minute CP-SAT optimization found no 128-modular candidate
and returned `UNKNOWN`; this timeout is not evidence of global nonexistence.

## Switching no-go

Signed row/column permutations conjugate the Gram matrix by a signed
permutation and preserve the multiset of absolute off-diagonal Gram entries.
Because this matrix has 8,684 nonzero off-diagonal pairs, switching,
permuting, or negating rows/columns cannot turn it into an exact Hadamard
matrix.

## Artifacts

- `reconstruct_eliahou.py` and `eliahou64_certificate.json`
- `eliahou64_sequences.json`
- `mod64_full_verification.json` and `exact_full_rejection.json`
- `search_local_exact_lift.py` and `local_lift_r8/`
- `search_radius8_cpsat.py` and `radius8_cpsat_result.json`
- `search_distance64_cpsat.py`, `distance64_defects.json`,
  `distance64_all83.json`
- `search_mod128_cpsat.py`, `mod128_search_result.json`,
  `mod128_radius16_to0.json`, `mod128_radius16_to_minus64.json`

All searches operate on 334 base-sequence signs, not 446,224 matrix entries.
