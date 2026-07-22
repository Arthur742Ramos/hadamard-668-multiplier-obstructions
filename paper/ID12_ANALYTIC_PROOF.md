# Resolving id12 — the last open order-≥9 common-multiplier LP(333) family

**Result.** The family **id12** — the unique surviving common-multiplier group of
order ≥ 9 for Legendre pairs of length 333 (Hadamard order 668) — is
**IMPOSSIBLE**. No id12-invariant Legendre pair of length 333 exists. The proof
is a short **analytic contradiction** (a single-shift PAF bound; §2), so it does
**not** rely on enumerating the 2,540,160 compressed pairs — that exhaustive
search is retained only as an independent confirmation. Everything is
independently verifiable (a dependency-free standalone verifier, plus three
solver engines), not a timeout.

> Scope/honesty (unchanged from phase 1): this closes a **multiplier-invariant**
> family. It does **not** resolve H(668) in general, which remains open. What it
> does settle: after phase 1 excluded all 15 order-≥12 families and 3 of 4
> order-9 families, id12 was the **only** order-≥9 multiplier family left open.
> It is now closed, so **all 19 common-multiplier groups of order ≥ 9 are proved
> to admit no invariant LP(333)**.

Directory: `id12_phase2/` (code in `code/`, outputs in `results/`; project-level
certificate copied to `../certificates/id12_impossible_certificate.json`).

---

## 1. The family and its exact structure

id12 = ⟨10, 46⟩ ≤ (Z/333)\* has order 9, is **trivial mod 9**, and its image mod
37 is **K37**, the order-9 subgroup of (Z/37)\* (the index-4 subgroup = the 4th
powers). Writing Z₃₃₃ ≅ Z₉ × Z₃₇ (CRT), an id12-invariant sequence is a function
`a(c,d)`, `c ∈ Z₉` (the *column*), `d ∈ Z₃₇`, that is constant on the **K37-orbits**
of the Z₃₇ coordinate. Those orbits are

```
{0},  C0, C1, C2, C3          sizes  1, 9, 9, 9, 9
```

where C0 = K37 and C1,C2,C3 are its cosets — the **quartic (order-4) cyclotomic
classes** for p = 37. So each column has one of 2⁵ = **32 types** (a sign per
orbit), and the four nonzero classes carry the **quartic Gaussian periods**
η₀,η₁,η₂,η₃ = Σ_{d∈C_j} ζ₃₇^d, whose period polynomial is
**x⁴ + x³ + 5x² + 7x + 49** (`code/periods.py`, exactly built from the order-4
cyclotomic numbers and cross-checked numerically).

Phase 1 left id12 open because its DFT values are these non-integer quartic
periods (no two-square obstruction), the row sum ±1 is reachable, and both
booleanized and column CP-SAT searches timed out (UNKNOWN) at 900–1200 s.

---

## 2. The proof — an analytic single-shift contradiction (elementary, symmetry-free)

The whole difficulty collapses under the **9-compression** — equivalently, the
**trivial-character (k₃₇ = 0) slice of the PSD decomposition** (see §4). Steps
1–5 pin an exact rigid structure; step 6 is a **one-line PAF bound** that
contradicts it, with **no search**.

Let `(a,b)` be an id12-invariant Legendre pair and let
`ã_j = Σ_{t=0}^{36} a_{j+9t}` (j ∈ Z₉) be the column sums (the 9-compression);
likewise `b̃`.

1. **Value set.** Each column is constant on orbits of sizes 1,9,9,9,9, so
   `ã_j = ε₀ + 9(ε₁+ε₂+ε₃+ε₄)` with `ε ∈ {±1}`. Hence
   **`ã_j, b̃_j ∈ V = {±1, ±17, ±19, ±35, ±37}`.**

2. **Compression identity.** For any sequence,
   `PAF_ã(s) = Σ_{s' ≡ s (mod 9)} PAF_a(s')` (37 shifts `s'` per `s`; proved by
   the CRT bijection `i ↔ (i mod 9, i mod 37)` and
   `{s+9k mod 333} = {s' ≡ s (mod 9)}`). For an LP (`PAF_a(s')+PAF_b(s') = −2`,
   `s' ≠ 0`) and `s = 1..8` this gives
   **`PAF_ã(s) + PAF_b̃(s) = 37·(−2) = −74`.**

3. **Row sums.** Compression preserves the total sum, so
   `Σ ã = Σ a = ±1`, `Σ b̃ = ±1`.

4. **Forced squared norm.** The elementary identity
   `Σ_{s=0}^{8} PAF_x(s) = (Σ x)²` gives
   `PAF_ã(0)+PAF_b̃(0) = Σ ã² + Σ b̃² = 2 − 8·(−74) = 594`. Over the squares of
   `V`, namely `{1, 289, 361, 1225, 1369}`, the **only** 18-term multiset summing
   to 594 is `16×1 + 2×289`. So **exactly two columns have |value| = 17 and the
   other sixteen have |value| = 1** (and the two big columns must be one +17 and
   one −17, forcing them into a single sequence: the split is (2,0) up to swap).

5. **Forced (2,0) structure.** Row sums pin the arrangement exactly. A sequence
   with a single big column (`|value| = 17`) has row sum `±17 + (even)`, which is
   odd in `[9,25]` or `[−25,−9]` — never `±1`; so the two big columns cannot be
   split one-and-one. They lie in a **single** sequence (WLOG `ã`), and to make
   its row sum `±1` they must be **one `+17` (at position `p`) and one `−17` (at
   position `q ≠ p`)**, the other seven entries `±1`. The other sequence `b̃` is
   **nine `±1` entries**.

6. **Primary proof — an analytic single-shift contradiction (no enumeration).**
   Evaluate the *one* shift `s = (q − p) mod 9`, which is nonzero since `p ≠ q`.
   Classify the nine terms of `PAF_ã(s) = Σ_j ã_j ã_{(j+s) mod 9}` by how many of
   the two big positions `{p,q}` they touch:
   * **exactly one big–big term**, namely `ã_p·ã_q = 17·(−17) = −289`. (There is
     no second big–big term: a `(q,p)` pairing would need `s ≡ −s (mod 9)`, i.e.
     `2s ≡ 0`, impossible since `gcd(2,9)=1` and `s ≠ 0`.)
   * **exactly two big–small terms**, each a product `(±17)·(±1) ≤ +17`;
   * **exactly six small–small terms**, each `(±1)·(±1) ≤ +1`.
   Hence `PAF_ã(s) ≤ −289 + 2·17 + 6·1 = −249`. And `b̃` is all `±1`, so
   `PAF_b̃(s) ≤ 9`. Therefore
   **`PAF_ã(s) + PAF_b̃(s) ≤ −240 < −74`**, contradicting the requirement from
   step 2 that it equal `−74`. ∎

   (The term-count structure is a fixed combinatorial fact, verified for all 72
   distinct `(p,q)`; the true maximum of `PAF_ã(q−p)` is `−251`, so the bound
   `≤ −249` holds with room to spare.)

7. **Independent confirmation.** Enumerating **all** such `(ã, b̃)` — 2 540 160
   compressed pairs — likewise finds **none** satisfying `PAF_ã(s)+PAF_b̃(s) = −74`
   for every `s = 1..8`. Same verdict, no shared logic with step 6.

**No LP was found** in any search; the verdict is IMPOSSIBLE, never FOUND.

### Symmetry audit

The final decision uses **no symmetry breaking whatsoever**: the exhaustive search
over 2 540 160 compressed pairs is complete and unquotiented, so there is no
symmetry-reduction step that could be unsound. The problem does carry symmetries
— Z₉ column rotation, (Z/9)\* column scaling, the Z₄ cyclotomic rotation of the
four nonzero orbits, global negation, and A↔B swap (all genuine LP-equivalences,
verified) — but they are deliberately **not relied upon**; they would only shrink
the already-tiny search further.

---

## 3. Why this is new (gap vs. prior work)

The essential ingredient is the exact **K37-invariance value restriction**
`ã_j ∈ V`. A naive 9-compression that treats column sums as *free odd integers*
(the kind of relaxation summarized as "feasible" in phase 1) does **not** close
id12: the forced squared norm 594 admits **842** distinct 18-term odd-square
multisets, so the rigid 2-big structure is not forced. Restricting to the true
value set `V` leaves the **unique** multiset `16×1 + 2×289`, which is infeasible.
(`code/master_certificate.py` and the `842 vs 1` computation.)

---

## 4. Placing the proof in the quartic-Gaussian-period / PSD framework

The proof is the trivial-character slice of the full PSD decomposition the family
was expected to require (`code/psd_analysis.py`, verified numerically to ~1e-13):

* With the column value `W_a(c) = ε₀(c) + Σ_a η_a ε_{C_a}(c) ∈ Z[η]`, the
  length-333 DFT satisfies `A(k₉, C_m) = σ^m( Ã(k₉) )`, where
  `Ã(k₉) = Σ_c ζ₉^{c k₉} W_a(c)` and `σ: η_j ↦ η_{j+1}` is the order-4 Galois
  automorphism. Hence the four coset-frequency PSD equations (fixed `k₉`) are
  Galois conjugates and **collapse to one ring identity**
  `|Ã(k₉)|² + |B̃(k₉)|² = 668` in `Z[ζ₉, η]`.
* The `k₃₇ = 0` frequencies are the **trivial character**, evaluated **directly**:
  it sends each column to its plain sum over Z₃₇, i.e. the column sum
  `Σ_i ε_i·|orbit i|` — exactly the **9-compression pair**. Combined with
  `ã_j ∈ V`, this trivial character alone already forces the contradiction — the
  non-integer quartic periods of the other characters are not even needed.

`code/periods.py` provides the **exact** period ring (order-4 cyclotomic numbers,
multiplication table verified against an independent convolution, complex
conjugation `η_j ↦ η_{j+2}`, and the period polynomial `x⁴+x³+5x²+7x+49` verified
exactly in the ring). It and `code/psd_analysis.py` are **illustrative supporting
material only** — the impossibility proof does not depend on them, and no
floating-point value enters any assertion.

---

## 5. Independent verification

* **`code/standalone_verifier.py`** — pure Python standard library, imports
  nothing from the project, **fully deterministic** (no random sampling). It
  generates `H = ⟨10, 46⟩ mod 333`, computes the K37-orbit sizes, **proves the two
  identities by exact coefficient-matrix equality** over the 333 sequence
  variables (the compression identity and `Σ_{s}PAF_x(s) = (Σx)²`), derives `V`,
  the forced norm 594, the unique square-multiset and the forced (2,0) structure,
  then checks the **primary analytic bound** — the `−289 + 2·17 + 6·1 = −249`
  term-count at `s = q−p`, verified structurally for all 72 `(p,q)`, plus
  `PAF_b̃ ≤ 9` — giving `≤ −240 < −74`. It **independently confirms** the same
  verdict with a complete square-sum-pruned exhaustive decision, and a **positive
  control invokes that same routine** on satisfiable instances (recovering a
  trivial and a nontrivial `−74` solution) and accepts a genuine length-5 LP, so
  a "0 solutions" cannot be a broken-search artefact. Runs in seconds; prints
  `PROOF VERIFIED`.
* **Three decision engines agree INFEASIBLE**: exhaustive enumeration, CP-SAT
  (OR-Tools), and z3 (`results/master_certificate.json`).
* **Compression identity cross-checked** against the phase-1 validated
  `core.paf`/`core.compress` on random invariant sequences, 0 mismatches
  (`results/compression_verification.json`).

Machine-readable certificate: `results/id12_impossible_certificate.json`
(and project copy `../certificates/id12_impossible_certificate.json`).

---

## 6. Reproduce

```bash
cd id12_phase2
./run_all.sh          # builds data, runs all engines + the standalone verifier
```

| file | purpose |
|---|---|
| `code/phase2_core.py` | exact group/orbit/column/CC data; self-checks |
| `code/periods.py` | **exact** quartic Gaussian-period ring (illustrative; no floats in any check) |
| `code/analysis1_structure.py` | (2,0) structure lemmas + compression solution set |
| `code/verify_compression.py` | identity check + DFS + CP-SAT (0 solutions) |
| `code/master_certificate.py` | 3-engine decision (exhaustive / CP-SAT / z3) |
| `code/psd_analysis.py` | illustrative Galois collapse; trivial character by **direct orbit evaluation** |
| `code/standalone_verifier.py` | **dependency-free, deterministic** end-to-end proof checker |
| `code/general_compression.py` | value-set 9-compression over all trivial-mod-9 families |
| `code/general_verifier.py` | **dependency-free** checker for id6/id8/id12 + free-odd witness + id3 |
| `code/make_certificate.py`, `code/make_general_certificate.py` | assemble the JSON certificates |

All exact verdicts are re-derivable; the standalone/general verifiers need only
Python 3 (no third-party packages, no randomness). A full top-level run
(`../code/run_all.sh`) re-runs phase 1 + phase 2, **asserts `num_impossible=21`
and `all_order_ge_9_impossible=true`** in `consolidate.py`, and regenerates the
SHA-256 manifest so it always matches the produced files.

---

## 7. Generalization — the same obstruction also closes id6 and id8 (bonus)

The 9-compression argument of §2 is **family-independent except for the value
set**: for L = 333 and the 9-compression, the PAF target (−74 for s = 1..8) and
the forced squared norm (594) do not depend on the family. Only the column-sum
value set V changes, and it is fixed by the **K37-orbit sizes of Z₃₇**. So the
obstruction applies verbatim to every family that is **trivial mod 9**
(H = {1}×K37, so the 9-compression columns are clean K37-invariant Z₃₇ blocks):
ids 0, 1, 3, 6, 8, 12.

Running the identical exact decision (`code/general_compression.py`,
`code/general_verifier.py`) gives:

| id | order | r₃₇ = \|K37\| | \|V\| | value set V (column sums) | verdict |
|---|---|---|---|---|---|
| 0 | 1 | 1 | 38 | all odd in [−37,37] | not closed (free-odd) |
| 1 | 2 | 2 | 38 | all odd in [−37,37] | not closed (free-odd) |
| 3 | 3 | 3 | 26 | {±1,±5,±7,…} (95 sq-multisets) | undecided (over budget) |
| **6** | **4** | **4** | **20** | {±3,±5,±11,±13,±19,±21,…} | **IMPOSSIBLE** |
| **8** | **6** | **6** | **14** | {±1,±11,±13,±23,±25,±35,±37} | **IMPOSSIBLE** |
| 12 | 9 | 9 | 10 | {±1,±17,±19,±35,±37} | **IMPOSSIBLE** |

* **id6 and id8 were OPEN after phase 1** and are now **proved IMPOSSIBLE** by
  the value-set-restricted 9-compression — exhaustively (id6: 2 428 992 pruned
  compressed sequences; id8: unique square-multiset {14×1, 2×121, 2×169},
  148 428 sequences; both yield 0 feasible pairs). id8 and id12 are additionally
  confirmed INFEASIBLE by CP-SAT (with the proven 594 cut); id6's complete
  exhaustion uses the same algorithm that three engines cross-validated on id12.
* **id0, id1** have V = all odd integers (K37 of order ≤ 2), i.e. the weak
  free-odd relaxation (842 square-multisets for 594) — the 9-compression does
  **not** close them, and this is not merely undecided: a **concrete free-odd
  witness** is stored and re-checked (`ã = [-21,1,5,1,1,5,5,1,3]`,
  `b̃ = [-3,5,-1,-3,1,-3,3,-1,1]`; row sums ±1, squared norm 594, PAF-sum −74),
  so the relaxation is provably **feasible**. (The witness uses values ±21, ±5,
  ±3 that lie outside the K37-restricted V of id6/id8/id12 — confirming the
  value-set restriction is exactly what does the work.)
* **id3** (K37 order 3, \|V\|=26, 95 square-multisets) is a genuine candidate;
  `general_verifier.py` tests it explicitly and reports **undecided** — its
  complete enumeration exceeds the node budget (honest, not a silent skip).
* The families **not** trivial mod 9 (ids 2,4,5,7,9,10; r₉=3) are outside the
  scope of this compression form.

Pure-stdlib checker `code/general_verifier.py` certifies id6, id8, id12
(IMPOSSIBLE) from first principles, verifies the stored free-odd witness (id0,
id1 feasible), reports id3 undecided, and includes a positive control that
invokes the same decision routine. Certificate:
`results/general_compression_certificate.json` (project copy
`certificates/general_compression_certificate.json`).

So the value-set-restricted compression — introduced here to settle id12 —
**additionally closes two previously-open families (id6, id8)**, leaving among
the trivial-mod-9 families only the free-odd id0, id1 (feasible witness) and the
undecided candidate id3.
