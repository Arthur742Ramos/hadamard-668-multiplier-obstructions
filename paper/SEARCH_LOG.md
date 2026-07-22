# Search log: real Hadamard matrix of order 668

Last updated: 2026-07-21

## Acceptance criterion

A candidate is accepted only if a CSV has exactly 668 rows, every row has
exactly 668 entries, every entry is the integer `-1` or `1`, and an independent
exact-integer check proves `H H^T = 668 I`.

No candidate met this criterion. No final matrix CSV was created.

## Current existence status

Order 668 remains the smallest unresolved order of the Hadamard conjecture.
This was checked against:

- Cati and Pasechnik, *A database of constructions of Hadamard matrices*,
  arXiv:2411.18897: <https://arxiv.org/abs/2411.18897>
- The current SageMath construction source, which lists
  `unknown_hadamard = [668, 716, 892, 1132]`:
  <https://github.com/sagemath/sage/blob/develop/src/sage/combinat/matrices/hadamard_matrix.py>
- The current open-problem record:
  <https://teorth.github.io/optimizationproblems/constants/23a.html>

The known order-668 modular result is not a real Hadamard matrix:

- Eliahou, *A 64-modular Hadamard matrix of order 668*,
  Australasian Journal of Combinatorics 93 (2025), 422-428:
  <https://ajc.maths.uq.edu.au/pdf/93/ajc_v93_p422.pdf>

## Construction attempts

| Family | Exact parameters or reduced equations | Outcome |
|---|---|---|
| Paley type I | Would require `q = 667`; `667 = 23*29` is not a prime power. | Closed for order 668. |
| Paley type II | Would require `2(q+1)=668`, hence `q=333=9*37`, not a prime power. | Closed for order 668. |
| Kronecker product | `668=4*167`; a Hadamard factor of odd order 167 cannot exist. | No direct product construction. |
| Unbordered two-circulant | DC equation `x^2+y^2=668`. | Impossible: 167 is `3 mod 4` to an odd exponent. |
| Three-core circulant | DC equation `x^2+y^2+z^2=668`. | Impossible: `668=4*(8*20+7)`, excluded by the three-square theorem. |
| Williamson type, length 167 | Four symmetric `+/-1` circulants with combined nonzero PAF zero. | Open; restricted to the 10 row-sum signatures below. No published quadruple found. |
| General Goethals-Seidel/SDS in `Z_167` | Four arbitrary `+/-1` circulants with combined nonzero PAF zero; equivalently an SDS with `lambda=sum(k_i)-167`. | Open; exactly 10 normalized parameter sets. No exact blocks found. |
| Propus, length 167 | GS specialization with two equal symmetric blocks. | Open; only 6 of the 10 row-sum signatures can occur. |
| Good matrices, length 167 | One skew-type circulant and three symmetric amicable circulants. | Open; only 2 of the 10 row-sum signatures can occur. |
| Cyclic/group-developed skew difference set | A `(667,333,166)` difference set. | Closed by the exact multiplier-orbit enumeration below. |
| Quadratic-residue-multiplier-invariant GS/SDS | All four blocks invariant under the order-83 quadratic-residue subgroup of `Z_167^*`. | Closed by orbit sizes `{1,83,83}` and the DC equation. |
| Legendre pair of length 167 | A length-167 pair yields order `2(167+1)=336`, not 668. | Parameter mismatch; irrelevant to order 668. |
| Legendre pair of length 333 | Row sums normalized to 1 and `PSD_A(s)+PSD_B(s)=668` for every nonzero frequency. | Open; exact compression restrictions reproduced below. |
| Modular Hadamard lifting | A 64-modular matrix exists. | Insufficient: congruence modulo 64 does not imply integer orthogonality. |
| Direct matrix/database search | Sage, Cati-Pasechnik, GitHub, Zenodo, HAL, and current search repositories. | No exact matrix or reduced construction data found. |

## Exact four-circulant restrictions

After independently complementing blocks, row sums may be made positive. The
only unordered positive odd quadruples whose squares sum to 668 are:

```text
(25,5,3,3)   (23,11,3,3)  (23,9,7,3)   (21,15,1,1)
(21,13,7,3)  (21,11,9,5)  (19,17,3,3)  (19,15,9,1)
(17,17,9,3)  (15,15,13,7)
```

For negative-position blocks `X_i` with `k_i=|X_i|`, the corresponding normalized
SDS parameter representatives, up to block permutation and block complementation,
are:

```text
(167;71,81,82,82;149)
(167;72,78,82,82;147)
(167;72,79,80,82;146)
(167;73,76,83,83;148)
(167;73,77,80,82;145)
(167;73,78,79,81;144)
(167;74,75,82,82;146)
(167;74,76,79,83;145)
(167;75,75,79,82;144)
(167;76,76,77,80;142)
```

Each satisfies the necessary counting identity
`sum_i k_i(k_i-1)=166*lambda`. The identity is not sufficient.

Consequences:

- Propus requires a repeated row sum, leaving 6 signatures:
  `(25,5,3,3)`, `(23,11,3,3)`, `(21,15,1,1)`, `(19,17,3,3)`,
  `(17,17,9,3)`, `(15,15,13,7)`.
- A good-matrix skew block has row sum `+/-1`, leaving only
  `(21,15,1,1)` and `(19,15,9,1)`.

The parameter list was cross-checked against:
<https://raw.githubusercontent.com/renrenreen/hadamard-search/cfe0f0ee3c9dd86f6517811a9ee07b24d2d85e0f/outputs/params/sds_params_v167_n668.json>

## Exact closure of the `(667,333,166)` difference-set route

This is a complete finite calculation, not heuristic local search.

1. The difference-set order is `k-lambda=167`.
2. By the First Multiplier Theorem, 167 is a numerical multiplier because
   167 is prime, `167 | (k-lambda)`, `gcd(167,667)=1`, and `167>166`.
3. If `167D=D+g`, then `gcd(167-1,667)=gcd(166,667)=1` permits a translate
   `D+a` fixed by multiplication by 167.
4. Multiplication by 167 on `Z_667` has orbit sizes
   `{1,11,11,14,14,154,154,154,154}`.
5. A fixed set of size 333 must be the union of two 154-orbits, one 14-orbit,
   and one 11-orbit. There are exactly `C(4,2)*2*2=24` candidates.
6. Exact ordered difference counts were computed for every candidate. None has
   count 166 at every nonzero residue.

Therefore no cyclic `(667,333,166)` difference set exists. Moreover, every group
of order `667=23*29` is cyclic because `23` does not divide `29-1`; this closes
the corresponding group-developed difference-set route as well.

The complete 24-candidate certificate is
`reduced_family_certificate.json`, generated by
`analyze_reduced_families.py`.

First Multiplier Theorem reference: R. J. Turyn, *The Multiplier Theorem for
Difference Sets*, Journal of Combinatorial Theory A 6 (1969), 263-270; see also
<https://encyclopediaofmath.org/wiki/Difference_set>.

## New exact restriction for multiplier-invariant GS/SDS searches

The order-83 quadratic-residue subgroup of `Z_167^*` has three orbits on
`Z_167`, of sizes `1,83,83`. A block invariant under this subgroup can therefore
have only size

```text
0, 1, 83, 84, 166, or 167.
```

Under the normalized SDS representatives above, admissible block sizes range
from 71 through 83, so an invariant block must have size 83. Hence:

- none of the 8 parameter sets without a size-83 block can contain even one
  quadratic-residue-multiplier-invariant block;
- `(73,76,83,83;148)` can contain at most two such blocks;
- `(74,76,79,83;145)` can contain at most one;
- no order-668 GS/SDS quadruple can have all four blocks invariant under this
  multiplier subgroup.

This rigorously rules out the most aggressive common-multiplier reduction at
length 167 while leaving unrestricted GS/SDS searches open.

## Legendre-pair length-333 restrictions

The relevant construction uses length 333, not 167. For normalized sequence
sums 1:

```text
PSD_A(s)+PSD_B(s)=668,  s=1,...,332.
```

Because `333=9*37`, exact compression gives:

- 9-compression Parseval total: `(2+8*668)/9 = 594`;
- 37-compression Parseval total: `(2+36*668)/37 = 650`;
- at frequency 111, exactly eight unordered PSD macro-cases:
  `(16,652)`, `(64,604)`, `(76,592)`, `(112,556)`,
  `(172,496)`, `(256,412)`, `(268,400)`, `(304,364)`.

If a common multiplier has residue 2 modulo 3, it swaps two mod-3 compression
classes. Their compressed sums become equal, forcing
`4(m_A^2+m_B^2)=668`, hence `m_A^2+m_B^2=167`, impossible. Thus every viable
common multiplier subgroup must lie in the kernel of reduction
`(Z/333)^* -> (Z/3)^*`, which has order 108.

The current external search reports complete enumeration of 12,017,243
PSD-compatible 9-compressions but no completed 37-compression or decompressed
Legendre pair:
<https://github.com/przchojecki/hadamard668>.

## Rejected reduced candidate

The best machine-readable GS candidate located used row sums `(17,17,9,3)`:

<https://raw.githubusercontent.com/renaissancefieldlite/Hadamard_Proof/6e4a8cc5f61abf081596b3dd9df17a5619ea1ce2/runs/order_668_gs_17-17-9-3_root2688_metablend_floor_bestscore_2496_512slack_final.json>

SHA-256 of the downloaded JSON:

```text
c61ccb9aa282965091c682759e6143b4ed349b85848cd9859e3923d593a9ea79
```

Independent exact PAF verification found:

```text
periodic score:             2496
violating nonzero shifts:   102 of 166
maximum absolute residual:  8
```

After assembling the full 668-by-668 Goethals-Seidel matrix, the independent CSV
verifier checked all 222,778 off-diagonal row pairs and rejected it with maximum
absolute inner product 8. The temporary invalid CSV was deleted.

## Verification artifacts

- `verify_hadamard_csv.py`: independent exact CSV and Gram verifier.
- `build_gs_csv.py`: reduced GS constructor, separate from the verifier.
- `verify_gs_sequences.py`: exact reduced PAF verifier.
- `analyze_reduced_families.py`: exact arithmetic and exhaustive orbit search.
- `reduced_family_certificate.json`: full machine-readable certificate.
- `near_gs_verification.json`: reduced rejection record.
- `near_gs_matrix_verification.json`: full 668-by-668 rejection record.

The CSV verifier represents each row as an arbitrary-precision integer bitset.
For rows `r_i,r_j`, it computes the exact integer inner product as
`668-2*bit_count(r_i XOR r_j)`. It validates dimensions and entries before
checking every pair. Its acceptance path was tested on a Sylvester matrix of
order 4; its rejection path was tested both on a corrupted order-4 matrix and
on the full order-668 near candidate.

## Final status

No exact construction was found, and the authoritative status remains open.
Producing a 668-by-668 CSV anyway would either fabricate data or knowingly
deliver a matrix that fails `H H^T=668I`. The completed outcome is therefore the
rigorous restriction/certificate branch requested in the search instructions,
not a false Hadamard matrix.

## Novel-strategy phase (2026-07-22)

### Exact classification of common-multiplier LP(333) families

The subgroup lattice of the mod-3-compatible kernel

```text
ker((Z/333)^* -> (Z/3)^*) ~= C3 x C36
```

has exactly 30 subgroups. Exact orbit-level searches and closed-form
obstructions now prove:

- every common multiplier group of order at least 12 is impossible;
- among the four order-9 groups, three are impossible;
- the only surviving order-at-least-9 case is the pure order-9 cyclotomic
  subgroup modulo 37;
- weaker groups of orders 1,2,3,4,6 remain open.

The 18 impossible families were closed by:

- a new mod-37 compression obstruction for groups surjecting onto
  `(Z/37)^*`;
- an exact row-sum obstruction modulo 24;
- exhaustive meet-in-the-middle enumeration;
- reproducible exact CP-SAT infeasibility results.

This concerns multiplier-invariant Legendre pairs only, not unrestricted
LP(333). Full details and reproducibility artifacts are in `lp333/report.md`
and `lp333/results/master_status.json`.

### Reduced SAT searches at length 167

Exact reduced CP-SAT models were run for all propus row-sum signatures, both
good-matrix signatures, and all Williamson signatures. Unrestricted bounded
runs returned `UNKNOWN`, so they prove no global exclusion.

For the Paley-skew good-matrix subfamily, `PAF_A(s)=-1` reduces the remaining
three symmetric blocks to `PAF_B+PAF_C+PAF_D=1`. Parity and row sums force
finite four-color counts:

```text
(1,21,15,1): colors (00,01,10,11) = (25,22,20,16)
(1,19,15,9): colors (00,01,10,11) = (26,20,19,18)
```

Deep exact runs remained `UNKNOWN`. The rigorous reduction and all solver
records are in `sat167/REPORT.md`.

### Exact reconstruction and lifting restrictions for the 64-modular matrix

Eliahou's explicit run-length data were reconstructed, expanded into the full
668-by-668 GS matrix, and checked over the integers. It is exactly 64-modular,
with 8,684 nonorthogonal row pairs and maximum absolute inner product 512.

In the equivalent `BS(84,83)` representation:

- the lag-4 defect proves analytically that every exact lift is at Hamming
  distance at least 64 base signs from the modular seed;
- exact distance-64 searches remain `UNKNOWN`;
- a 128-modular lift is analytically at distance at least 16;
- both exact distance-16 branches are infeasible, raising the reproducible
  computational bound to at least 17;
- an unrestricted 128-modular search found no candidate and timed out, so no
  global 128-modular nonexistence is claimed.

See `mod64/report.md` and its machine-readable verification records.

### Phase 2 — id12 resolved: the last order-≥9 multiplier family is closed

The sole common-multiplier family of order ≥ 9 left open after phase 1, **id12**
(order 9, trivial mod 9, image = the order-9 subgroup K37 of `(Z/37)^*`), is now
**proved IMPOSSIBLE**. No id12-invariant Legendre pair of length 333 exists.

The proof is elementary and exact. Under `Z_333 = Z_9 × Z_37`, K37-invariance
forces every column sum `atilde_j` (the 9-compression) into the value set
`V = {±1, ±17, ±19, ±35, ±37}`. The compression identity plus the LP condition
give `PAF_atilde(s) + PAF_btilde(s) = -74` for `s = 1..8` with row sums `±1`, and
the identity `Σ_s PAF = (Σ)²` forces the squared norm to `594`. Over the squares
of `V` the *unique* 18-term multiset summing to 594 is `16×1 + 2×289`, so exactly
two columns have `|sum| = 17` and sixteen have `|sum| = 1`; exhausting all
2,540,160 such compressed pairs yields **no** solution.

The decisive new ingredient over phase 1 is the exact K37 value-set restriction:
a free-odd 9-compression admits 842 square-multisets summing to 594 and does not
close id12, whereas `V` leaves the single infeasible one. The result is confirmed
by three independent engines (exhaustive, CP-SAT, z3) and a dependency-free
standalone verifier (with positive controls). Code, results, a machine-readable
certificate and a full write-up are in `lp333/id12_phase2/`
(`certificates/id12_impossible_certificate.json`).

Consequently **every common-multiplier group of order ≥ 9 (all 19 such of the 30
families) is proved to admit no invariant LP(333)**; the remaining open families
all have order ≤ 6 (refined further in the next subsection). This still concerns
multiplier-invariant LPs only and does not resolve H(668).

#### Generalization bonus: id6 and id8 also fall

The value-set-restricted 9-compression is family-independent except for the
column-sum value set V (fixed by the K37-orbit sizes). Applied to every
trivial-mod-9 family it also proves **id6 (order 4)** and **id8 (order 6)** —
both previously OPEN — IMPOSSIBLE:

- id8: V = {±1,±11,±13,±23,±25,±35,±37}; unique 18-square multiset for 594 is
  {14×1, 2×121, 2×169}; exhaustive over 148,428 compressed sequences finds none
  (also INFEASIBLE under CP-SAT).
- id6: V = {±3,±5,±11,±13,±19,±21,±27,±29,±35,±37}; 9 square-multisets;
  exhaustive over 2,428,992 compressed sequences finds none.

id0, id1 (K37 order ≤ 2) have V = all odd integers (the weak free-odd relaxation,
842 square-multisets for 594) and are NOT closed; id3 (K37 order 3, |V|=26) is a
candidate whose enumeration exceeds budget. So **21 of the 30 multiplier families
are now IMPOSSIBLE**, with 9 open (ids 0,1,2,3,4,5,7,9,10). A dependency-free
`general_verifier.py` certifies id6/id8/id12 from first principles with a
positive control. Still concerns multiplier-invariant LPs only; H(668) unresolved.

#### id12: analytic single-shift contradiction (primary proof)

The id12 impossibility no longer relies on enumerating 2,540,160 compressed
pairs. After the forced 16×1+2×289 pattern and row sums, one compressed sequence
`ã` carries `+17` at a position `p` and `−17` at `q≠p` (rest ±1) while the other
`b̃` is all ±1. At the single shift `s = (q−p) mod 9` (nonzero, so `2s≠0 mod 9`),
`PAF_ã(s)` is one big–big term `17·(−17)=−289`, two big–small terms (`≤+17` each)
and six small–small terms (`≤+1` each), so `PAF_ã(s) ≤ −249`; with `PAF_b̃(s) ≤ 9`
the sum is `≤ −240 < −74`, contradicting the compression requirement `−74`. This
is now the primary proof (verified structurally for all 72 `(p,q)`; the true max
of `PAF_ã(q−p)` is `−251`). The exhaustive enumeration, CP-SAT and z3 are kept as
independent confirmations. The dependency-free `standalone_verifier.py` checks the
analytic bound directly.

### Proof-carrying and theorem packaging

The computational phase-1 exclusions now have externally checkable evidence:

- DRAT traces independently verified for ids 13,14,20,21,22;
- direct weighted pseudo-Boolean contradictions for ids 11,15,19,23,24,28;
- independent standard-library rebuild/audit code and positive controls.

The hardened verifier reruns `drat-trim`, pins its binary and model dependencies,
rejects a bogus proof control, and is integrated into the top-level reproducible
pipeline before SHA-256 manifest generation. See `lp333/proof_phase2/`.

The separate `compression_theorem/` note develops fixed-field necessary
conditions for invariant Legendre pairs:

- the basic compression/sum-of-two-squares mechanism is established prior art
  and is presented as a synthesis, not a new discovery;
- the totally-real fixed-field formulation and real-quadratic index-2 norm-form
  obstruction are labeled **potentially new pending specialist review**;
- an exhaustive census finds 139 forbidden fixed-symmetry classes among 428
  real-quadratic cases with odd `L≤1200`;
- the finite imaginary-quadratic census finds 0 infeasible cases among 797, with
  no universal permissiveness claim.

These are symmetry restrictions, never global Legendre-pair or Hadamard
nonexistence claims.
