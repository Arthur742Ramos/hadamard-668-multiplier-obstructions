# A mod-8 obstruction for common-multiplier IDs 9 and 10

## Theorem

No Legendre pair `A,B in {+1,-1}^333` is fixed under coordinate
multiplication by either classification subgroup below:

```text
H9  = <73,85>  = {1,73,85,211,232,286},
H10 = <73,121> = {1,73,121,175,196,322}.
```

## Proof

Fix one invariant sequence `x`. Global multiplication by `-1` preserves its
periodic autocorrelation and allows the normalization `x(0,0)=1`. Under the
CRT identification `Z/333Z = Z/9Z x Z/37Z`, write its entries as `x(r,c)`.
Define the length-9 compression by

```text
Y_r = sum_{c in Z/37Z} x(r,c).
```

Summing the Legendre equations over all 333 shifts gives

```text
(sum A)^2+(sum B)^2 = 2*333+332*(-2) = 2.
```

Each integer row sum equals `+1` or `-1`. Write the row sum of `x` as `rho`.
The common image
`{1,4,7}` modulo 9 forces

```text
Y = (alpha,mu,nu,beta,mu,nu,gamma,mu,nu),
rho = alpha+beta+gamma+3mu+3nu.                 (1)
```

Because 73 belongs to both groups and has CRT coordinates `(1,-1)`,
invariance gives `x(r,c)=x(r,-c)`.

For each `c in Z/37Z`, put

```text
Z_c = sum_{r in Z/9Z} x(r,c).
```

On the `c=0` fiber, let `d3,d6` denote the signs at rows 3 and 6. Use `u`
for the common sign on `{1,4,7}` and `v` for the common sign on
`{2,5,8}`. Thus

```text
Z_0 = 1+d3+d6+3u+3v.                           (2)
```

The common image `{1,10,11,26,27,36}` modulo 37 partitions the 36 nonzero
columns into six orbits of size six, and invariance makes `Z_c` constant on
each orbit. Naming these odd values `t1,...,t6` gives

```text
rho-Z_0 = 6(t1+...+t6) = 0 (mod 12).            (3)
```

Since `|rho-Z_0| <= 10`, divisibility by 12 in (3) forces `Z_0=rho`.
Equation (2) becomes

```text
3(u+v) = rho-1-d3-d6.
```

The intersection `{-6,0,6} ∩ [-4,2] = {0}` forces `v=-u`.

Pairing each nonzero column `c` with `-c` gives

```text
mu = u+2S_mu = u (mod 4),
nu = v+2S_nu = v (mod 4),
```

where `S_mu` and `S_nu` are even sums of 18 signs. Combining these
congruences with `v=-u` gives

```text
T = 0 (mod 4).                                  (4)
```

Each of `mu` and `nu` sums 37 signs and is odd. Expanding the pattern in (1)
gives

```text
PAF_Y(1)
  = (alpha+beta+gamma)(mu+nu)+3mu*nu
  = rho*T-3T^2+3mu*nu.                         (5)
```

Set `nu=T-mu`. Since `T` is divisible by 4 and both `rho` and `mu` are odd,

```text
mu*nu = mu(T-mu) = T-1 (mod 8),
rho*T-3T^2 = T (mod 8).
```

Substitution into (5) gives

```text
PAF_Y(1) = T+3(T-1) = 4T-3 = 5 (mod 8).         (6)
```

For the pair, (6) conflicts with the compression identity at shift 1, which
sums the 37 original shifts congruent to 1 modulo 9:

```text
2 ≡ 5+5 ≡ PAF_YA(1)+PAF_YB(1) = 37*(-2) = -74 ≡ 6 (mod 8).
```

## Independent proof

[Issue #3](https://github.com/Arthur742Ramos/hadamard-668-multiplier-obstructions/issues/3),
opened by hypnopump, gives a separate mod-24 proof at shift 111 and includes a
Lean 4 formalization of the exclusions.

## Verification

Run the dependency-free checker from the repository root:

```bash
python3 lp333/id9_id10_mod8/code/standalone_verifier.py
```

The script derives each subgroup and its orbit signature from the generators.
It records the six admissible local patterns after exhaustive enumeration,
then tests full-length compression on deterministic invariant assignments.

As a dependency control, the checker repeats the residue calculation with row
sums `+3` and `-3`, obtaining the set `{1,5}` and an available pair residue 6.

## Classification consequence

The classification now contains 23 impossible groups, with open IDs
`0,1,2,3,4,5,7`. Within order six, the open case is ID 7.

## Scope

The theorem applies to Legendre pairs fixed by `H9` or `H10`. Unrestricted
length-333 pairs and the Hadamard order-668 question remain open.
