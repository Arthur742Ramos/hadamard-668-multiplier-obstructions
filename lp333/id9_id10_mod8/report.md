# A mod-8 obstruction for common-multiplier IDs 9 and 10

## Theorem

Let `A,B in {+1,-1}^333` be a Legendre pair. Neither of the following
subgroups can fix both sequences under coordinate multiplication:

```text
H9  = <73,85>  = {1,73,85,211,232,286},
H10 = <73,121> = {1,73,121,175,196,322}.
```

Thus common-multiplier subgroup IDs 9 and 10 in the classification are
impossible.

## Proof

It is enough to consider one normalized invariant sequence `x`, with
`x(0)=1` and row sum `rho in {+1,-1}`. Identify
`Z/333Z = Z/9Z x Z/37Z`, write its entries as `x(r,c)`, and let `Y` be its
length-9 compression.

The image of either subgroup modulo 9 is `{1,4,7}`. Consequently

```text
Y = (alpha,mu,nu,beta,mu,nu,gamma,mu,nu),
rho = alpha+beta+gamma+3mu+3nu.                 (1)
```

Both subgroups contain `73`, whose CRT coordinates are `(1,-1)` because
`73 = 1 (mod 9)` and `73 = -1 (mod 37)`. Invariance therefore gives
`x(r,c)=x(r,-c)`.

On the `c=0` fiber, let `d3,d6` be the signs at rows 3 and 6, and let `u,v`
be the common signs on row orbits `{1,4,7}` and `{2,5,8}`. The compressed
value of this fiber is

```text
Z0 = 1+d3+d6+3u+3v.                            (2)
```

The 36 nonzero mod-37 columns form six size-six cosets under either
subgroup. The column sum is constant on each coset and is odd, since it is a
sum of nine signs. Hence

```text
rho-Z0 = 6(t1+...+t6) = 0 (mod 12).             (3)
```

Since `Z0` is between `-9` and `9`, while `rho` is `+1` or `-1`, (3) forces
`Z0=rho`. Substituting in (2) gives

```text
3(u+v) = rho-1-d3-d6.
```

The left side belongs to `{-6,0,6}` and the right side lies in `[-4,2]`, so
`v=-u`.

Pair the 36 nonzero columns by `c <-> -c`. In a row from `{1,4,7}` this
gives `mu=u (mod 4)`; similarly, `nu=v (mod 4)`. Therefore

```text
T := mu+nu = 0 (mod 4).                         (4)
```

Both `mu` and `nu` are odd. Directly from (1),

```text
PAF_Y(1)
  = (alpha+beta+gamma)(mu+nu)+3mu*nu
  = rho*T-3T^2+3mu*nu.                         (5)
```

If `T=0 (mod 8)`, then `nu=-mu (mod 8)` and `mu*nu=-1 (mod 8)`, so (5) is
`5 (mod 8)`. If `T=4 (mod 8)`, then `mu*nu=3 (mod 8)` and `rho*T=4 (mod 8)`,
so (5) is again `5 (mod 8)`. Every normalized invariant sequence therefore
satisfies

```text
PAF_Y(1) = 5 (mod 8).                           (6)
```

For a Legendre pair, the compression identity sums the 37 original nonzero
shifts congruent to 1 modulo 9:

```text
PAF_YA(1)+PAF_YB(1) = 37*(-2) = -74 = 6 (mod 8).
```

Equation (6) instead makes the left side `5+5=2 (mod 8)`, a contradiction.

## Verification

The dependency-free checker regenerates both subgroups and their orbit
signatures, exhausts the local residue argument, checks the final
compression contradiction, and runs deterministic full-orbit controls:

```bash
python3 lp333/id9_id10_mod8/code/standalone_verifier.py
```

Expected final line:

```text
PROOF VERIFIED: IDs 9 and 10 are impossible (fixed common multipliers)
```

As a mutation control, the checker replaces the load-bearing row sums
`{+1,-1}` by `{+3,-3}`. The single-sequence residue set then becomes `{1,5}`
and pair residue 6 becomes possible, so the contradiction correctly
disappears.

## Classification consequence and scope

Together with the 21 exclusions already in this repository, the theorem
raises the fixed-common-multiplier classification to 23 of 30 impossible,
leaving IDs `0,1,2,3,4,5,7` open. ID 7 is the only remaining order-six case.

This result is only about the specified fixed common multipliers. It neither
excludes an unrestricted Legendre pair of length 333 nor decides whether a
real Hadamard matrix of order 668 exists.
