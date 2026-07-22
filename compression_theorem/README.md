# compression_theorem/

A self‑contained theorem note deriving a **general compression obstruction for
multiplier‑invariant Legendre pairs**, together with its **Gaussian‑period
refinement** for non‑surjective images, and machine‑checked verification scripts.

It generalizes the length‑333 (Hadamard order 668) mod‑3 / mod‑37 calculation into
standalone theorems that (i) hold for arbitrary odd length `L` and a fixed odd
prime `p | L`, (ii) forbid **new fixed‑symmetry classes** at many other lengths,
and (iii) isolate exactly which part of the `L=333` study is forced by a general
obstruction (the rest is *not settled by these obstructions* — no irreducibility
claim).

**Terminology.** The theorems forbid **fixed‑symmetry classes** — pairs
`(length, image K_p)` for which no `H`‑invariant Legendre pair exists. They do
**not** exclude *lengths*: an LP of that length may still exist with a
smaller‑image (or trivial) multiplier group.

## Read this first
- **`theorem_note.md`** — the deliverable: definitions, Lemmas 2.1–2.2,
  Theorems A/B/C, Proposition D, the CM dichotomy (with the `p=13,f=4`
  counterexample), corollaries, the `L=333` consequence, an attribution section
  (**established prior art vs. potentially new**), and a bibliography.

## Results at a glance
- **Theorem A** (surjective image `K_p=(ℤ/p)^×`): if `2L+2` is not a sum of two
  squares, the surjecting class is forbidden. *(A synthesis of established
  compression + sum‑of‑two‑squares machinery — not claimed as new; see below.)*
- **Theorem B** (`−1∈K_p`, index `f`): `2L+2` must be a sum of two squares in the
  totally real order `𝒪_{𝕂_f}`. `f=1` ⇒ Theorem A.
- **Theorem C** (`p≡1 mod 4`, index‑2 image `QR(p)`): the explicit integer system
  (R)+(S). It *extends the symmetry reach, not the numerical regime*. **Exhaustive
  census (all `p≡1 mod4 | odd L≤1200`): 428 classes, of which 139 are forbidden**
  (116 distinct lengths, primes up to 373), reaching **open** lengths (e.g. 185).
- **Proposition D** (`p≡3 mod 4`, index‑2): the norm identity `2L+2=N(α)+N(β)` is
  **exact**; its *solvability* is a **finite‑census** fact (797 cases, 0
  infeasible, incl. `p=3`), **not** a universal theorem.
- **CM dichotomy is `f=2`‑specific:** the “permissive/rational‑norm” conclusion
  holds only for `f=2` imaginary. For `f≥4` with `−1∉K` the relative norm lands in
  a nontrivial real subfield and is generally irrational — explicit counterexample
  `p=13, f=4`: `|Ã(k)|² = 10±2√13 ∈ ℚ(√13)`, minimal polynomial `t²−20t+48`.
- Reproduces the closed‑form kills of the `L=333` study exactly (ids 25,26,27,29,
  via **vendored, hashed** metadata) and leaves the rest unsettled by A/C.

## Reproduce
```bash
cd compression_theorem
bash scripts/run_all.sh        # runs all checks, writes certificates/*.json + manifest.sha256
```
Requirements: Python 3 with `sympy` and `numpy`.

## Files
```
theorem_note.md                          the theorem note (main deliverable)
data/lp333_classification_metadata.json  vendored L=333 metadata (provenance + source sha256)
scripts/cyclo.py                         exact arithmetic in Q(zeta_L) mod Phi_L
scripts/verify_core.py                   V1–V5: exact identities & collapses
scripts/norm_form_obstruction.py         Theorem B/C mechanism, CM counterexample,
                                         EXHAUSTIVE Theorem C census, Prop D census
scripts/l333_consequences.py             L=333 derivation from vendored metadata
scripts/families.py                      infinite forbidden families, density, simultaneous
scripts/check_note_claims.py             asserts numeric and attribution claims (44 checks)
scripts/run_all.sh                       one-shot driver
certificates/*.json                      machine-readable outputs
manifest.sha256                          artifact hashes (note, data, scripts, certificates)
```

## Exactness / honesty
- All asserted algebraic equalities are checked **exactly** (integer arithmetic or
  reduction modulo the cyclotomic polynomial `Φ_L`); no floating point is used for
  any equality claim.
- Census numbers are **exhaustive** over the stated ranges: Theorem C = 139
  forbidden of 428 classes (`L≤1200`); Proposition D = 0 infeasible of 797 cases
  (`L≤1500`), reported as a finite‑census fact only.
- **Self‑contained for rerunning this note:** the only external input (the `L=333`
  subgroup metadata) is vendored in `data/` with its source path and sha256.
  Independent regeneration of that metadata uses the separate
  `lp333/code/classify.py` package.
- **Attribution (resolved by a prior‑art review).** The **compression +
  sum‑of‑two‑squares** machinery underlying **Theorem A is established prior art**
  — compression is Đoković–Kotsireas [DK15]; the sum‑of‑two‑squares condition in
  the compression context appears in [KK21], [KKB+23], [KGG25] (“Legendre pairs
  under compression”, ISSAC 2025) and [KKW25] (“Quaternary Legendre pairs II”,
  Discrete Math. 2025, which also uses Galois theory for cyclotomic fields on the
  PSD test). **Theorem A is therefore presented as a synthesis / general
  formulation, not as new.** The closest‑titled multiplier paper [GK02] (Util.
  Math. 61, 2002; Zbl 1001.05031) is, per its zbMATH review, a small‑length
  *construction/search* strategy, **not** a compression/norm‑form nonexistence
  theorem. **Potentially new (pending a broader specialist review):** the
  fixed‑field formulation of **Theorem B** and the real‑quadratic index‑2
  obstruction **Theorem C**; these are labelled *potentially new*, not asserted as
  priority, since Galois–cyclotomic PSD conditions are already in use ([KKW25]).
```
