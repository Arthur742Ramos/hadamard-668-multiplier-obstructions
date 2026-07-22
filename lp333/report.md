# Common-multiplier-invariant Legendre pairs of length 333 — exact search toward H(668)

Scope: length **L = 333 = 3² · 37**. A Legendre pair (LP) of length L yields a
Hadamard matrix of order **2L + 2 = 668** (the smallest order for which the
Hadamard conjecture is currently open). This report is the *common-multiplier
(multiplier-invariant) route*: we look only for LPs whose two sequences are
constant on the orbits of a multiplier group H ≤ (Z/333)^*. Proving a family
impossible means **no LP with that symmetry exists**; it does **not** settle
H(668) (see "Scope and honesty" below). All results here are exact finite
computations with machine-readable certificates.

Directory: `lp333/` (code in `code/`, raw outputs in `results/`, certificates in
`certificates/`). Reproduce end-to-end with `code/run_all.sh`.

---

## 1. Setup and equivalences (exact integer facts)

For a, b ∈ {+1,−1}^L with PAF_x(s) = Σ_i x_i x_{(i+s) mod L}, (a,b) is a Legendre
pair iff

>  PAF_a(s) + PAF_b(s) = −2  for all s = 1,…,L−1,   and  Σa, Σb ∈ {+1,−1}.

Equivalently (finite Fourier dual), with A(k)=Σ_i a_i ω^{ik}, ω = e^{2πi/L}:

>  |A(k)|² + |B(k)|² = 2L+2 = 668  for every k = 1,…,L−1,  and (Σa)²+(Σb)² = 2.

The row-sum fact (Σa)²+(Σb)²=2 forces both row sums to be ±1; this uses only
that 1²+1²=2 is the sole representation with odd summands.

**Multiplier invariance.** H ≤ (Z/333)^* acts on Z_333 by multiplication. An
H-invariant sequence is constant on H-orbits. Two exact symmetries follow and
are used throughout:

* A(k) = A(hk) for h ∈ H (DFT constant on frequency orbits), so the PSD
  condition is **one equation per nonzero H-orbit of frequencies**.
* PAF_a(s) = PAF_a(hs) for h ∈ H, so the PAF condition is **one equation per
  nonzero H-orbit of shifts**.

Both are proved in `code/core.py` / validated numerically in
`code/validate_and_refsearch.py` (PAF-from-orbits equals direct PAF, and PAF is
constant on shift orbits, over random invariant sequences).

**Core number-theoretic fact.** 668 = 2²·167 with 167 prime, 167 ≡ 3 (mod 4)
to an odd power ⇒ **668 is not a sum of two integer squares**. (Also 668 = 4·167,
167 ≡ 7 (mod 8) ⇒ not a sum of three squares.) Verified in code.

---

## 2. Two proved compression obstructions

Certificates: `certificates/obstruction_certificates.json`
(generator `code/obstructions.py`).

### 2.1 mod-3 obstruction (reproves prior result) — PROVED

If H contains a unit u ≡ 2 (mod 3), then on the 3-compression
ã_j = Σ_t a_{j+3t} (j ∈ Z₃) the map j ↦ uj = −j swaps classes 1,2, forcing
ã₁ = ã₂ (and b̃₁ = b̃₂). Then Ã(1) = ã₀ + ã₁(ω+ω²) = ã₀ − ã₁ is a **rational
integer**, likewise B̃(1), and the PSD identity gives
Ã(1)² + B̃(1)² = |A(111)|²+|B(111)|² = 668 — a sum of two integer squares equal
to 668: **impossible**. Hence every viable H lies in
ker((Z/333)^* → (Z/3)^*), the **order-108** subgroup of units ≡ 1 (mod 3).

### 2.2 mod-37 obstruction (new) — PROVED

If H reduces **onto** the full group (Z/37)^* (order 36), then H acts on Z₃₇
with exactly two orbits {0} and {1,…,36}. The 37-compression ã_j = Σ_t a_{j+37t}
is therefore ã = (ã₀, c, c, …, c) (36 equal entries), so for every k ≢ 0 (mod 37)

>  Ã(k) = ã₀ + c·Σ_{j=1}^{36} ζ^{jk} = ã₀ − c   (a rational integer),

and Ã(k) = A(9k). The PSD identity at the nonzero frequency 9k gives
(ã₀−c)² + (b̃₀−d)² = |A(9k)|²+|B(9k)|² = 668 — again two integer squares summing
to 668: **impossible**. The orbit collapse {1,36} is verified for each such H.

Families killed: the 4 subgroups that surject onto (Z/37)^* — ids **25, 26, 27,
29** (orders 36, 36, 36, 108).

> Remark (why 37 does not give more): for H whose image mod 37 is a *proper*
> subgroup K, the Gaussian periods Σ_{j∈K-orbit} ζ^{jk} are irrational, so
> Ã(k) is not an integer and no two-square obstruction follows. Those families
> are settled by exact search instead (§4).

> Remark (why mod-9 gives no analogous closed obstruction): since H ⊆ units ≡ 1
> (mod 3), its image mod 9 is contained in the order-3 subgroup {1,4,7}. This
> subgroup fixes the quadratic subfield Q(√−3) of Q(ζ₉), so the 9-compression's
> DFT values Ã(k) lie in the **Eisenstein integers** and |Ã(k)|² is an Eisenstein
> *norm* — but the constraint is a *sum of two* Eisenstein norms equal to 668,
> which is not obstructed (unlike a single norm; 668 is not itself an Eisenstein
> norm because 167 ≡ 2 mod 3 to an odd power). The full mod-9 image (Z/9)^* would
> be needed to collapse the compression to integers, and that is impossible here
> because it contains elements ≡ 2 mod 3 already excluded by §2.1. Hence mod-9
> contributes only the (feasible) compression *relaxation* used in §4, not a kill.

---

## 3. Classification of the compatible subgroup lattice

`code/classify.py` → `results/subgroup_classification.json`.

(Z/333)^* ≅ Z/6 × Z/36 has order 216. The mod-3 kernel U₁ (units ≡ 1 mod 3) has
order 108 and structure Z/3 × Z/36 ≅ Z/4 × Z/3 × Z/9. Its subgroup lattice has
**exactly 30 subgroups** (join-closure of cyclic subgroups; abelian ⇒ all normal,
so "distinct subgroup" = "conjugacy class"). For each we record the reductions
mod 9 and mod 37, the multiplication orbits on Z_333, and the orbit signature.

* 4 of the 30 surject onto (Z/37)^* ⇒ killed by §2.2.
* The other 26 require exact search; the number of orbits r (= number of ±1
  variables per sequence) ranges from 10 (killed) up to 333 (trivial group).

Orbit data (sizes, index map, per-shift PAF coefficient matrices) is built in
`code/search_common.py` and validated in `code/validate_and_refsearch.py`.

---

## 4. Exact finite searches (per family)

Every impossible verdict below is an **exact, exhaustive** decision with a
machine-readable record. Closed-form, modular-DP, and MITM cases have directly
checkable certificates; CP-SAT cases have deterministic model/result records
rather than standalone proof traces. Three interchangeable exact engines were used and
cross-validated against each other on shared families (all agree):

**(A) Meet-in-the-middle over orbit values** (`code/mitm.cpp`, driver
`code/run_mitm.py`). Variables = one ±1 per H-orbit (a₀=b₀=+1 fixes the global
sign). Using PAF_a(s)=const_s+Σ W_s[Q,Q'] x_Q x_{Q'} (exact integers), enumerate
all 2^{r−1} sign patterns by Gray code, keep row-sum-±1 profiles, and match a
profile p against its complement (−2)−p. Exhaustive; feasible for r ≤ 27.

**(B) CP-SAT booleanized PAF** (`code/cpsat_search.py`, and
`code/cpsat_search2.py` with sound multiplier+swap symmetry breaking). x=1−2z,
x_Q x_{Q'} = 1−2·(z_Q XOR z_{Q'}); PAF equalities and row sums become linear
constraints; CP-SAT decides exactly (INFEASIBLE = proof; any model is verified).

**(C) Column-type model** for families trivial mod 9 (`code/column_cpsat.py`),
exploiting Z_333 ≅ Z₉ × Z₃₇ and PAF_a(s₉,s₃₇) = Σ_c CC(a_c, a_{c+s₉}; s₃₇).

**(D) Cheap necessary conditions** (`code/necessary_conditions.py`): the exact
**row-sum modular obstruction** (is Σ|O|x_O = ±1 reachable? witness modulus if
not) and the 37-/9-compression relaxations (PAF-sum = −18 resp. −74).

### Headline results

* **Row-sum obstruction.** For families reducing onto the order-12 subgroup of
  (Z/37)^* (ids 16, 17, 18, 24) the row sum Σ|O|x_O is ≡ {3,5,…,21} (mod 24),
  never ±1. **Impossible** — witness modulus 24, exhaustive modular DP.
* **Meet-in-the-middle exhaustion** proves impossible: id 28 (order 54, r=15),
  id 23 (order 27, r=25), ids 20/21/22 (order 18, r=27/23/23), id 24 (order 36;
  also row-sum). Enumeration counts recorded in `results/mitm/`.
* **CP-SAT** proves impossible: ids 11, 13, 14 (order 9), id 15 (order 12),
  id 19 (order 18). id 11 (r=65) closes in 0.01 s with symmetry breaking.

### Per-family verdict (all 30 families)

| id | \|H\| | r | mod9 | mod37 | status | method |
|---|---|---|---|---|---|---|
| 0 | 1 | 333 | 1 | 1 | OPEN | not exhausted |
| 1 | 2 | 171 | 1 | 2 | OPEN | not exhausted |
| 2 | 3 | 185 | 3 | 1 | OPEN | not exhausted |
| 3 | 3 | 117 | 1 | 3 | OPEN | not exhausted |
| 4 | 3 | 113 | 3 | 3 | OPEN | not exhausted |
| 5 | 3 | 113 | 3 | 3 | OPEN | not exhausted |
| 6 | 4 | 90 | 1 | 4 | **IMPOSSIBLE** | 9-compression (K37 value-set), phase 2 |
| 7 | 6 | 95 | 3 | 2 | OPEN | not exhausted |
| 8 | 6 | 63 | 1 | 6 | **IMPOSSIBLE** | 9-compression (K37 value-set), phase 2 |
| 9 | 6 | 59 | 3 | 6 | OPEN | not exhausted |
| 10 | 6 | 59 | 3 | 6 | OPEN | not exhausted |
| 11 | 9 | 65 | 3 | 3 | **IMPOSSIBLE** | exact CP-SAT |
| 12 | 9 | 45 | 1 | 9 | **IMPOSSIBLE** | 9-compression (K37 value-set), phase 2 |
| 13 | 9 | 41 | 3 | 9 | **IMPOSSIBLE** | exact CP-SAT |
| 14 | 9 | 41 | 3 | 9 | **IMPOSSIBLE** | exact CP-SAT |
| 15 | 12 | 50 | 3 | 4 | **IMPOSSIBLE** | exact CP-SAT |
| 16 | 12 | 36 | 1 | 12 | **IMPOSSIBLE** | row-sum (mod 24) |
| 17 | 12 | 32 | 3 | 12 | **IMPOSSIBLE** | row-sum (mod 24) |
| 18 | 12 | 32 | 3 | 12 | **IMPOSSIBLE** | row-sum (mod 24) |
| 19 | 18 | 35 | 3 | 6 | **IMPOSSIBLE** | exact CP-SAT |
| 20 | 18 | 27 | 1 | 18 | **IMPOSSIBLE** | meet-in-the-middle |
| 21 | 18 | 23 | 3 | 18 | **IMPOSSIBLE** | meet-in-the-middle |
| 22 | 18 | 23 | 3 | 18 | **IMPOSSIBLE** | meet-in-the-middle |
| 23 | 27 | 25 | 3 | 9 | **IMPOSSIBLE** | meet-in-the-middle |
| 24 | 36 | 20 | 3 | 12 | **IMPOSSIBLE** | row-sum (mod 24) + MITM |
| 25 | 36 | 18 | 1 | 36 | **IMPOSSIBLE** | mod-37 obstruction |
| 26 | 36 | 14 | 3 | 36 | **IMPOSSIBLE** | mod-37 obstruction |
| 27 | 36 | 14 | 3 | 36 | **IMPOSSIBLE** | mod-37 obstruction |
| 28 | 54 | 15 | 3 | 18 | **IMPOSSIBLE** | meet-in-the-middle |
| 29 | 108 | 10 | 3 | 36 | **IMPOSSIBLE** | mod-37 obstruction |

Master machine-readable file: `results/master_status.json` (per family: status,
label proved/heuristic, method, certificate pointer, and the exact counts).

---

## 5. What is proved

* **Every multiplier group H of order ≥ 9 (all 19 such families, of the 30)
  admits no H-invariant Legendre pair of length 333.** Proved exactly, no
  heuristics. (Phase 1 closed all 15 order-≥12 families and the order-9 ids 11,
  13, 14; **phase 2 closed the last order-9 family, id 12** — see
  `id12_phase2/report.md`.)
* **Phase 2's method (a value-set-restricted 9-compression) additionally closed
  two previously-open lower-order families: id 6 (order 4) and id 8 (order 6).**
  In total **21 of the 30 families are now IMPOSSIBLE**; the 9 still OPEN are
  ids 0,1,2,3,4,5,7,9,10 (orders 1,2,3,3,3,3,6,6,6).
* No invariant Legendre pair was found in any exhausted family (all verdicts are
  IMPOSSIBLE, never FOUND). Had one been found, the two ±1 sequences and full
  PAF/PSD verification would be saved under `results/` — none were produced.

All "IMPOSSIBLE" labels are **proved** (exhaustive finite search or a closed-form
obstruction). No "IMPOSSIBLE" label is heuristic.

The exact verifier `is_legendre_pair` was validated with a positive control
(it accepts genuine Legendre pairs of lengths 5 and 7, cross-checked by an
independent PAF recomputation) and a negative control (it rejects a non-pair),
so a real invariant LP would be reported as FOUND and confirmed, never missed
or spuriously accepted.

### id 12 (phase 2) — the last order-≥9 family, now closed

id 12 is trivial mod 9 and equals the order-9 subgroup K37 of (Z/37)\*, so its
DFT values are quartic Gaussian periods and no two-square obstruction applies —
which is why phase 1 left it OPEN. It is nevertheless **IMPOSSIBLE**, by an
elementary exact argument on its **9-compression** (column sums under
Z₃₃₃ ≅ Z₉ × Z₃₇):

* K37-invariance forces every column sum into
  **V = {±1, ±17, ±19, ±35, ±37}** (`ε₀ + 9·Σε`).
* The compression identity plus the LP condition give
  `PAF_ã(s)+PAF_b̃(s) = −74` (s = 1..8), row sums ±1, and (via
  `Σ_{s}PAF = (Σ)²`) a forced squared norm 594. Over V-squares the **unique**
  18-term multiset summing to 594 is `16×1 + 2×289`, i.e. exactly two columns
  have |sum| = 17 and sixteen have |sum| = 1. Row sums then force the **(2,0)**
  shape: one sequence carries `+17` (position p) and `−17` (position q≠p) plus
  seven ±1, the other is nine ±1.
* **Analytic contradiction (no enumeration).** At the single shift `s = q−p`
  (nonzero), `PAF_ã(s)` splits into one big–big term `17·(−17) = −289`, two
  big–small terms (`≤ +17` each) and six small–small terms (`≤ +1` each), so
  `PAF_ã(s) ≤ −249`; with `PAF_b̃(s) ≤ 9` this gives
  `PAF_ã(s)+PAF_b̃(s) ≤ −240 < −74`, contradicting the required `−74`.
* Independently confirmed by exhausting all 2 540 160 compressed pairs (0
  solutions) and by CP-SAT and z3.

The proof is a short analytic argument checked by a **dependency-free standalone
verifier** (with positive controls). The novel ingredient over phase 1 is the
exact **K37 value-set restriction** `ã_j ∈ V`: a free-odd 9-compression admits
842 square-multisets for 594 and does not close id 12 (a concrete free-odd
witness makes it feasible); restricting to V leaves the unique infeasible one.
Full write-up, code and certificate: `id12_phase2/` (certificate
`certificates/id12_impossible_certificate.json`).

---

## 6. Remaining open cases (labeled OPEN, not exhausted)

* **ids 0,1,2,3,4,5,7,9,10** (orders 1,2,3,3,3,3,6,6,6): the weakest-invariance
  families, r = 59…333. These exceed exhaustive MITM and did not close under
  CP-SAT within budget. The value-set 9-compression of phase 2 does **not** close
  them: ids 0,1 have a free-odd column-sum value set; id3 is a trivial-mod-9
  candidate whose exhaustive enumeration exceeds budget (undecided); and ids
  2,4,5,7,9,10 are not trivial mod 9, so that compression form does not apply.
  A decision needs a larger SAT/CP effort or a further structural obstruction.

> Phase 2 (value-set-restricted 9-compression) proved **id 6 (order 4), id 8
> (order 6), and id 12 (order 9)** IMPOSSIBLE; id 6 and id 8 had been OPEN. The
> order-≥9 frontier is fully closed and two lower-order families fell as well —
> see §5 and `id12_phase2/`.

---

## 7. Scope and honesty

* These results concern **multiplier-invariant** LPs only. Proving a family
  impossible does **not** prove that no length-333 LP exists, and therefore does
  **not** resolve H(668), which remains open. This matches the external state of
  the art (`../order668_search_log.md`; SageMath still lists 668 as unknown).
* We did **not** search the full 668×668 matrix (as instructed).
* Solver package `ortools` (CP-SAT) was installed in a local venv
  (`lp333/.venv`); `pysat` was already present. C++ MITM uses the system
  compiler. All exact verdicts are independently re-verifiable.

## 8. Reproducibility

```
code/core.py                 group, orbits, PAF/compression primitives
code/classify.py             -> results/subgroup_classification.json
code/obstructions.py         -> certificates/obstruction_certificates.json
code/necessary_conditions.py -> results/necessary_conditions.json  (row-sum, 37-comp)
code/search_common.py        family PAF spec builder
code/validate_and_refsearch.py  spec validation + Python reference MITM
code/mitm.cpp / run_mitm.py  -> results/mitm/*.json  (exact MITM)
code/cpsat_search.py, cpsat_search2.py, column_cpsat.py  exact CP-SAT engines
code/consolidate.py          -> results/master_status.json
code/run_all.sh              one-shot driver
```

Every impossible family carries reproducible evidence: an orbit-collapse proof
(`obstruction_certificates.json`), a witness modulus + exhaustive modular DP
(`necessary_conditions.json`), an exhaustive MITM enumeration count
(`results/mitm/idN.json`), or a CP-SAT INFEASIBLE record
(`results/cpsat/idN*.json`), all indexed by `results/master_status.json`.
