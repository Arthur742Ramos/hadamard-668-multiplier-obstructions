# A compression obstruction for multiplier‑invariant Legendre pairs, and its Gaussian‑period refinement

**A self‑contained theorem note.**
Working directory: `compression_theorem/`.  All numeric claims are reproduced
exactly by the scripts in `scripts/` and recorded in `certificates/`; run
`scripts/run_all.sh`.

---

## 0. Summary of results

Let `L` be odd and let a *Legendre pair* (LP) of length `L` be a pair
`a,b ∈ {±1}^L` whose periodic autocorrelations satisfy
`PAF_a(s)+PAF_b(s) = −2` for `s = 1,…,L−1`; equivalently, writing
`A(k)=Σ_i a_i ω^{ik}` with `ω=e^{2πi/L}`, the power‑spectral‑density (PSD)
identity

> **(PSD)**  `|A(k)|² + |B(k)|² = 2L+2`  for every `k = 1,…,L−1`.

An LP of length `L` yields a Hadamard matrix of order `2L+2` (Fletcher–Gysin–Seberry
[FGS01]). Fix a subgroup `H ≤ (ℤ/L)^×` acting on `ℤ_L` by multiplication and call
`(a,b)` **`H`‑invariant** if `a_i=a_{ui}` and `b_i=b_{ui}` for all `u∈H` (the
sequences are constant on `H`‑orbits). This is the object of every
multiplier‑invariant / subgroup‑invariant LP search.

Let `K_p` denote the image of `H` under reduction `(ℤ/L)^× → (ℤ/p)^×`, for a
**fixed odd prime** `p | L`. Throughout, a *forbidden fixed‑symmetry class* means:
no `H`‑invariant LP of the stated length with the stated image `K_p` exists. This
forbids `(length, symmetry)` classes, **not lengths** — an LP of that length may
still exist with a smaller‑image (or trivial) multiplier group. This note proves:

* **Theorem A (surjective compression obstruction).** If `K_p = (ℤ/p)^×` for some
  odd prime `p | L` and `2L+2` is **not** a sum of two integer squares, then no
  `H`‑invariant LP of length `L` exists.  Here `2L+2` is not a sum of two squares
  iff `L+1` is not, iff some prime `q ≡ 3 (mod 4)` divides `L+1` to an odd power.

* **Theorem B (totally‑real compression obstruction).** More generally, if
  `−1 ∈ K_p` (some multiplier is `≡ −1 mod p`) and `K_p` has index `f`, let
  `𝕂_f ⊂ ℚ(ζ_p)` be the degree‑`f` totally real subfield fixed by `K_p` and `𝒪`
  its ring of integers.  Then `2L+2` must be a **sum of two squares in `𝒪`**
  (`2L+2 = α²+β²`, `α,β∈𝒪`).  `f=1` is Theorem A.

* **Theorem C (real‑quadratic index‑2 refinement, `f=2`).** For `p ≡ 1 (mod 4)`
  and `K_p = QR(p)` (the quadratic residues, the unique index‑2 subgroup),
  Theorem B becomes the explicit integer system

  > **(R)** `2a₁a₂ − a₂² + 2b₁b₂ − b₂² = 0`,  **(S)** `a₁²+b₁²+ (p−1)/4·(a₂²+b₂²) = 2L+2`.

  If **(R)+(S)** has no integer solution, no such LP exists.  This *extends the
  reach of the obstruction to smaller (index‑2) symmetry groups*; it does **not**
  extend the numerical regime — every Theorem‑C exclusion already has `2L+2` not a
  sum of two squares (so Theorem A already forbids the *full*‑image class), and
  Theorem C additionally forbids the *index‑2* class. An **exhaustive** census over
  **every** prime `p ≡ 1 (mod 4)` dividing an odd `L ≤ 1200` finds **428** such
  classes, of which **139** are forbidden (across 116 distinct lengths, primes up
  to `373`), including genuinely open Legendre‑pair lengths (`L=185`). (Unlike
  Theorem A, a clean unconditional infinitude proof is left open; see §6/§10.)

* **Proposition D (imaginary index‑2: exact identity, census‑permissive).** For
  `p ≡ 3 (mod 4)` and `K_p = QR(p)` (`−1 ∉ K_p`, `f=2`), the identity
  `2L+2 = N(α)+N(β)` with `α,β ∈ 𝒪_{ℚ(√−p)}` (a sum of two norms; principal form
  of discriminant `−p`, including the Eisenstein case `p=3`) is an **exact,
  proven** necessary condition. Its *solvability* is reported as a **finite‑census
  fact** — no infeasible case for `p ≡ 3 (mod 4)`, `L ≤ 1500` (797 cases) — **not**
  a universal theorem. The dichotomy is: `−1 ∈ K_p` gives the (restrictive)
  totally‑real sum‑of‑two‑squares condition; `−1 ∉ K_p` with `f = 2` gives this
  (census‑permissive) rational sum‑of‑two‑norms condition. **The permissive side is
  special to `f = 2`:** for `f ≥ 4` with `−1 ∉ K_p` the quantity `|Ã(k)|²` is a
  relative norm landing in a *nontrivial* maximal real subfield `𝕂_f^+` and is
  generally **irrational** — e.g. `p=13, f=4` gives `|Ã(k)|² ∈ ℚ(√13)` with
  minimal polynomial `t²−20t+48` — so no rational sum‑of‑two‑norms picture applies
  and the case is *not* known to be permissive (left open).

* **Corollaries.** Infinite families of forbidden surjecting‑symmetry classes with
  an explicit Dirichlet construction (§6); for a density‑1 set of lengths the
  surjecting class is forbidden (§6); simultaneous per‑prime forbidden images for
  composite `L` (§7); and the complete consequence for `L = 333` (§8), where the
  theorems reproduce *exactly* the closed‑form kills of the prior `L=333` study
  and leave the remaining classes unsettled *by these obstructions* (not
  claimed irreducibly computational). The `L=333` metadata is vendored and hashed
  in `data/` for self‑containment.

**What is established vs. potentially new (see §9).** The compression/DFT identity
is Đoković–Kotsireas [DK15], and the **compression + sum‑of‑two‑squares**
machinery is established prior art: it is used for length `ℓ≡0 (mod 5)` in
[KKB+23], studied directly in [KGG25] (“Legendre pairs under compression”), and in
the quaternary setting [KKW25] explicitly notes that the compression construction
requires the analogous integer to be a sum of two squares (and uses Galois theory
for cyclotomic fields to sharpen the PSD test). The LP/PSD formalism is [FGS01];
the `p=3` instance is folklore used *constructively* in [KK21]. Accordingly:

* **Theorem A is a clean synthesis / general formulation** of this established
  machinery (compression to a prime `p`, orbit collapse, the two‑square
  condition). We make **no novelty claim** for it; it is stated for completeness
  and as the base case of Theorem B.
* **Potentially new (pending broader review):** (i) the fixed‑field formulation of
  Theorem B — `2L+2` as a sum of two squares in the totally‑real order `𝒪_{𝕂_f}`,
  organised by the `−1∈K_p` / `−1∉K_p` (real vs. CM) dichotomy; (ii) **Theorem C**,
  the real‑quadratic index‑2 obstruction (the explicit `(R)+(S)` system) forbidding
  the proper `QR(p)` class that Theorem A cannot touch (within the same numerical
  regime); (iii) the resulting corollaries and the `L=333` boundary. The
  closest‑titled multiplier paper [GK02] is a small‑length *construction/search*
  strategy (zbMATH review; Zbl 1001.05031), **not** a compression/norm‑form
  nonexistence theorem, so it is not prior art for Theorems B–C; but since Galois–
  cyclotomic PSD conditions are already in use ([KKW25]), we label B–C only as
  *potentially new pending a broader specialist review*.

---

## 1. Setup, conventions, and invariance

Throughout `L` is a fixed odd integer, `ω = e^{2πi/L}`, and for `x∈ℂ^L`,
`X(k)=Σ_{i=0}^{L−1} x_i ω^{ik}`, `PSD_x(k)=|X(k)|²`.  Indices are mod `L`.

**Definition 1.1 (Legendre pair).** `a,b∈{±1}^L` form a Legendre pair if
`PAF_a(s)+PAF_b(s) = −2` for `s=1,…,L−1`, where `PAF_x(s)=Σ_i x_i x_{i+s}`.
By Wiener–Khinchin, `PSD_x(k) = Σ_{s} PAF_x(s) ω^{sk}` with `PAF_x(0)=L`, so the
autocorrelation condition is equivalent to **(PSD)**: for `k≠0`,
`|A(k)|²+|B(k)|² = Σ_s(PAF_a+PAF_b)(s)ω^{sk} = 2L + (−2)·Σ_{s≠0}ω^{sk} = 2L+2`,
using `Σ_{s=0}^{L−1}ω^{sk}=0`.  (This equivalence is verified exactly for genuine
LPs of lengths `3,5,7,9,11,13` in `scripts/verify_core.py`, check **V1**.)

**Invariances / normalizations.** The quantity used below is only the
nonzero‑frequency identity **(PSD)**. It is invariant under all standard LP
equivalences, so *signs and normalizations are immaterial to the obstruction*:

* `a ↦ −a` (`A↦−A`), `b ↦ −b`, and the swap `a ↔ b` — leave `|A|²,|B|²` and their
  sum unchanged;
* cyclic shift `a_i ↦ a_{i+c}` sends `A(k) ↦ ω^{ck}A(k)`, so `|A(k)|` is
  unchanged;
* decimation `a_i ↦ a_{ui}` (`u∈(ℤ/L)^×`) permutes the frequencies `k ↦ u^{-1}k`,
  permuting the identities **(PSD)** among themselves.

In particular the row‑sum normalization `Σa,Σb∈{±1}` (i.e. the `k=0` term) is
**not used** anywhere in the argument; only the defining PSD identity at nonzero
frequencies is used.

**Definition 1.2 (`H`‑invariance).** For `H ≤ (ℤ/L)^×`, `(a,b)` is `H`‑invariant
if `a_i=a_{ui}, b_i=b_{ui}` for all `u∈H, i∈ℤ_L` (constant on `H`‑orbits).  This
is preserved by `a↦−a`, `b↦−b`, `a↔b`.  (A *multiplier with translate*
`a_{ti}=a_{i+c}` is discussed in Remark 3.4; the theorems are stated for the
fixed/invariant case, which is exactly what invariant LP searches enumerate.)

---

## 2. The compression lemmas

**Lemma 2.1 (compression–DFT identity; [DK15]).** Let `d | L`, `n=L/d`, and for
`x∈ℂ^L` define the `d`‑compression `x̃∈ℂ^d` by `x̃_j = Σ_{t=0}^{n−1} x_{j+td}`
(`j∈ℤ_d`).  Then, with `X̃(k)=Σ_{j=0}^{d−1} x̃_j ζ_d^{jk}` (`ζ_d=e^{2πi/d}`),

> `X(kn) = X̃(k)`  for all `k`.

*Proof.* Write `i=j+td`, `0≤j<d`, `0≤t<n`. Then
`ω^{i·kn} = ω^{(j+td)kn} = ω^{jkn}·ω^{tkL} = ω^{jkn}`, and `ω^{jkn}=e^{2πi jkn/L}
= e^{2πi jk/d}=ζ_d^{jk}`.  Summing, `X(kn)=Σ_j ζ_d^{jk} Σ_t x_{j+td} = Σ_j x̃_j
ζ_d^{jk}=X̃(k)`. ∎

Taking `d=p` prime and `k=1,…,p−1` (so `kn ≢ 0 mod L`), Lemma 2.1 turns **(PSD)**
into a condition on the length‑`p` compression: for `k=1,…,p−1`,

> **(PSD‑p)**  `|Ã(k)|² + |B̃(k)|² = 2L+2`.

(Lemma 2.1 is verified exactly, mod `Φ_L`, over genuine LPs in `verify_core.py`,
check **V2**.)

**Lemma 2.2 (invariance descends).** If `x` is `H`‑invariant and `p|L`, then the
`p`‑compression `x̃` is `K_p`‑invariant, where `K_p = {u mod p : u∈H}` is the
image of `H` in `(ℤ/p)^×`; i.e. `x̃_{v j}=x̃_j` for all `v∈K_p`.

*Proof.* Let `u∈H`, `v=u mod p`. Since `u` is a unit mod `L`, `i↦ui` permutes
`ℤ_L`, and `ui ≡ vj (mod p) ⇔ i ≡ j (mod p)` (as `u` is a unit mod `p`). Hence
`x̃_{vj}=Σ_{i≡vj(p)} x_i = Σ_{i≡vj(p)} x_{u^{-1}·ui}`; re‑indexing `i'=u^{-1}i`
and using `x`‑invariance `x_{ui'}=x_{i'}`, this equals `Σ_{i'≡j(p)} x_{i'}
= x̃_j`. ∎

Thus `x̃` is constant on the `K_p`‑orbits of `ℤ_p`. On the nonzero residues
`{1,…,p−1}`, `K_p` acts as a subgroup of the cyclic group `(ℤ/p)^×`, with orbits
the cosets of `K_p`.

---

## 3. Theorem A — the surjective obstruction

**Theorem A.** *Let `L` be odd, `p|L` a fixed odd prime, and `H ≤ (ℤ/L)^×` with
`K_p=(ℤ/p)^×` (i.e. `H` surjects onto `(ℤ/p)^×`).  If `(a,b)` is an `H`‑invariant
Legendre pair of length `L`, then `2L+2 = Ã(1)² + B̃(1)²` with `Ã(1),B̃(1)∈ℤ`.
Consequently, if `2L+2` is not a sum of two integer squares, no `H`‑invariant
Legendre pair of length `L` exists.*

*Proof.* By Lemma 2.2 the `p`‑compression `ã` is `(ℤ/p)^×`‑invariant. The full
multiplicative group acts transitively on `{1,…,p−1}`, so `ã` takes a single
value `c` on all nonzero residues: `ã=(ã_0,c,c,…,c)`. For `k=1,…,p−1`,

> `Ã(k)=ã_0 + c·Σ_{j=1}^{p−1}ζ_p^{jk} = ã_0 + c·(−1) = ã_0 − c ∈ ℤ`,

using `Σ_{j=0}^{p−1}ζ_p^{jk}=0`.  Likewise `B̃(k)=b̃_0−d∈ℤ`.  By Lemma 2.1 with
`k=1`, `Ã(1)=A(L/p)` and `B̃(1)=B(L/p)`, and `L/p ≢ 0 (mod L)`, so **(PSD)** gives
`(ã_0−c)² + (b̃_0−d)² = |A(L/p)|²+|B(L/p)|² = 2L+2`.  If `2L+2` is not a sum of two
squares this is impossible. ∎

**Remark 3.1 (the number‑theoretic condition).** `2L+2 = 2(L+1)`. Since a
positive integer is a sum of two squares iff every prime `≡3 (mod 4)` divides it
to an even power, and `2n` is a sum of two squares iff `n` is (from
`2n=(x+y)²+(x−y)²`), we have

> `2L+2` is **not** a sum of two squares ⇔ `L+1` is not ⇔ some prime
> `q ≡ 3 (mod 4)` divides `L+1` to an **odd** power.

(Verified over `n<2000` and for `668,334` in `verify_core.py`, check **V4**.)

**Remark 3.2 (`p=2` is vacuous; Theorem A synthesises established machinery).**
`L` is odd so `2∤L`. For `p=3`, `(ℤ/3)^×={1,2}` and surjectivity means `H`
contains a unit `≡ 2 ≡ −1 (mod 3)`; Theorem A recovers the classical *“a
multiplier `≡ −1 mod 3` is impossible when `2L+2` is not a sum of two squares.”*
More broadly, the pairing of `p`‑compression [DK15] with a sum‑of‑two‑squares
condition is **established prior art**: it appears for `ℓ≡0 (mod 3)` and `(mod 5)`
in [KK21], [KKB+23], is studied under the name “Legendre pairs under compression”
in [KGG25], and the quaternary analogue in [KKW25] explicitly notes that the
compression construction is available exactly when the relevant integer is a sum
of two squares. Theorem A is a **clean general formulation** of this machinery for
an arbitrary prime `p|L`; it is not claimed as new (see §9).

**Remark 3.3 (existence of a surjecting `H`).** For any prime `p|L`, reduction
`(ℤ/L)^× → (ℤ/p)^×` is surjective (CRT together with the surjectivity of
`(ℤ/p^a)^× → (ℤ/p)^×`), so a *cyclic* `H=⟨u⟩` with `u` mapping to a primitive
root mod `p` always exists.  Hence the hypothesis of Theorem A is realizable for
every `p|L`; the obstruction is never vacuous on the symmetry side.  (Exhibited
for many `(L,p)` in `verify_core.py`, check **V3**.)

**Remark 3.4 (scope: fixed invariance only).** Throughout, `H` acts by *fixed*
multiplication (`a_i = a_{ui}`), the object enumerated by every group‑invariant LP
search. Multipliers‑with‑translate (`a_{ti}=a_{i+c}`) are **out of scope**: the
collapse of `Ã(k)` to a rational integer (Lemma 2.2, Theorem A) uses fixed
invariance, and we make no claim in the translate setting.

---

## 4. Theorem B — the totally‑real obstruction, and the CM dichotomy

Fix `p|L` and let `K=K_p ≤ (ℤ/p)^×` have index `f`, so `K` has `(p−1)/f`
elements and the nonzero residues split into `f` cosets `C_0=K,C_1,…,C_{f−1}`.
The `p`‑compression `ã` is constant on each coset; write its values
`ã_0` (at `0`) and `u_0,…,u_{f−1}` (on `C_0,…,C_{f−1}`). With the *Gaussian
periods* `η_r=Σ_{j∈C_r}ζ_p^{j}` (`r∈ℤ_f`), Lemma 2.1 gives, for `k∈C_σ`,

> `Ã(k) = ã_0 + Σ_{r} u_r η_{r+σ}`,

so `Ã(k)` lies in the degree‑`f` subfield `𝕂_f ⊂ ℚ(ζ_p)` fixed by `K` (the
`η_r` and their `K`‑orbit sums generate `𝕂_f`), and the `f` values
`{Ã(k):k∈C_σ}` are the Galois conjugates of `α:=Ã(1)∈𝒪_{𝕂_f}` under
`Gal(𝕂_f/ℚ)≅(ℤ/p)^×/K`. Complex conjugation `ζ_p↦ζ_p^{-1}` corresponds to the
coset of `−1`.

> **Dichotomy.** Let `𝕂_f^+ ⊆ 𝕂_f` be the maximal real subfield (the fixed field
> of `⟨K,−1⟩`).
> * `−1∈K`: `𝕂_f` is totally real, `𝕂_f^+=𝕂_f`, and `Ã(−k)=Ã(k)`, so
>   `|Ã(k)|²=Ã(k)²` directly. The relative norm from `𝕂_f` to itself is the
>   identity and is not the square map (Theorem B; restrictive).
> * `−1∉K`, `f=2`: `𝕂_f^+ = ℚ`, so `|Ã(k)|² = N(Ã(k))` is a **rational** integer
>   (Proposition D; the sum‑of‑two‑norms picture, census‑permissive).
> * `−1∉K`, `f≥4`: `𝕂_f^+` is a **nontrivial** real field of degree `f/2`, so
>   `|Ã(k)|²` is generally **irrational** (it lies in `𝕂_f^+`, not `ℚ`); the
>   rational sum‑of‑two‑norms picture does *not* apply. (Counterexample below.)
> In the last two cases `𝕂_f/𝕂_f^+` is quadratic and
> `|Ã(k)|²=Ã(k)Ã(−k)=N_{𝕂_f/𝕂_f^+}(Ã(k))`.

**Theorem B (totally‑real case, `−1∈K`).** *Let `L` be odd, `p|L` a fixed odd
prime, and `H≤(ℤ/L)^×` with image `K=K_p` satisfying `−1∈K`, of index `f`; let
`𝕂_f⊂ℚ(ζ_p)` be the (totally real) fixed field of `K` and `𝒪=𝒪_{𝕂_f}`.  If `(a,b)`
is an `H`‑invariant Legendre pair, then `2L+2 = α²+β²` for some `α,β∈𝒪` (namely
`α=Ã(1),β=B̃(1)`).  Hence if `2L+2` is not a sum of two squares in `𝒪`, no such
Legendre pair exists.*

*Proof.* Since `−1∈K`, `𝕂_f⊂ℝ` and `α=Ã(1),β=B̃(1)∈𝒪` are real; so `|Ã(1)|²=α²`,
`|B̃(1)|²=β²`. Lemma 2.1 (`k=1`) and **(PSD)** give `α²+β²=|A(L/p)|²+|B(L/p)|²
=2L+2`. ∎

For `f=1` (`K=(ℤ/p)^×`, which always contains `−1`) we have `𝕂_1=ℚ`, `𝒪=ℤ`, and
Theorem B is exactly Theorem A. The mechanism — `Ã(k)` lands in the degree‑`f`
*real* subfield and is real — is verified exactly (mod `Φ_p`) for
`(p,f)∈{(5,2),(13,2),(17,2),(37,2),(17,4),(41,4)}` in
`scripts/norm_form_obstruction.py`, check **[2]**.

**Remark 4.1 (why the index‑2 totally‑real case can bite).** In the totally‑real
case `α²` is *not* Galois‑invariant, so requiring `α²+β²∈ℚ` imposes genuine extra
rational equations (see (R) in §5). In the `f=2` CM/imaginary case `|Ã(k)|²=N(α)`
is *already* rational, so no extra equation appears and the resulting condition
(sum of two rational norms) is far more permissive (Prop. D). This is why the
index‑2 exclusions come from `p ≡ 1 (mod 4)` (real, Theorem C), not from `f=2`
imaginary. **This contrast is specific to `f=2`.** For `f≥4` with `−1∉K` the
relative norm `|Ã(k)|²` is generally *irrational* (it lives in the nontrivial real
subfield `𝕂_f^+`), so neither the “rational‑norm/permissive’’ conclusion of Prop. D
nor the clean two‑equation form of Theorem C applies; such cases are left open.

**Remark 4.2 (CM counterexample, `p=13, f=4`).** The order‑3 subgroup
`K=⟨3⟩={1,3,9}` of `(ℤ/13)^×` has `−1=12∉K`, index `f=4`, and `⟨K,−1⟩=QR(13)` so
`𝕂_4^+=ℚ(√13)`. For the explicit `K`‑invariant length‑13 sequence
`ã=(1,1,1,1,1,1,1,−1,−1,1,1,−1,1)`, the exact computation (mod `Φ₁₃`) gives
`|Ã(1)|²` and `|Ã(2)|²` equal to the two roots `10±2√13` of `t²−20t+48`, i.e.
`|Ã(k)|² ∈ ℚ(√13)\ℚ`. This concretely refutes any claim that `−1∉K` makes
`|Ã(k)|²` automatically rational or the case permissive. (Verified in
`norm_form_obstruction.py`, check **[3]**.)

---

## 5. Theorem C — the index‑2 refinement, and Proposition D

`(ℤ/p)^×` is cyclic, so it has a unique index‑2 subgroup: the quadratic residues
`QR(p)`. Here `−1∈QR(p) ⇔ p≡1 (mod 4)`.

**Theorem C (`p≡1 mod 4`, `K=QR(p)`).** *Let `p≡1(mod4)` be a fixed odd prime,
`p|L`, and `H≤(ℤ/L)^×` with image `K_p=QR(p)`.  Put `α=a₁+a₂η₀, β=b₁+b₂η₀∈𝒪_{ℚ(√p)}`
where `η₀=(−1+√p)/2`.  If `(a,b)` is an `H`‑invariant Legendre pair then the
integers `a₁,a₂,b₁,b₂` satisfy*

> **(R)** `2a₁a₂ − a₂² + 2b₁b₂ − b₂² = 0`,   **(S)** `a₁²+b₁² + (p−1)/4·(a₂²+b₂²) = 2L+2`.

*Equivalently `2L+2 = α²+β²` in `𝒪_{ℚ(√p)}`.  If **(R)+(S)** has no integer
solution, no such Legendre pair exists.*

*Proof.* By Theorem B with `f=2`, `𝕂_2=ℚ(√p)` (real, since `p≡1 mod4`), `α=Ã(1),
β=B̃(1)∈𝒪_{ℚ(√p)}=ℤ[η₀]`, and `α²+β²=2L+2∈ℚ`. Writing `α²+β² = X + Y√p` with
`X,Y∈ℚ` (`η₀²=−η₀+(p−1)/4`), a direct expansion gives `2Y = 2a₁a₂−a₂²+2b₁b₂−b₂²`
and, when `Y=0`, `X = a₁²+b₁²+ (p−1)/4·(a₂²+b₂²)`.  Requiring `α²+β²=2L+2`
(rational) is `Y=0` and `X=2L+2`, i.e. **(R)+(S)**. The relaxation to *arbitrary*
integers `a₁,a₂,b₁,b₂` is a valid necessary condition (the actual compression
values are particular integers of this form). ∎

(The identity `α²+β²=X+Y√p` with the stated `X,Y` is verified symbolically in
`norm_form_obstruction.py`, check **[1]**.)

**What Theorem C does (and does not) add.** Taking `a₂=b₂=0` in **(S)** shows the
system is solvable whenever `2L+2` is a sum of two *rational* squares; hence
Theorem C forbids classes only when `2L+2` is not a sum of two squares — *the same
numerical regime as Theorem A*. Theorem C therefore **extends the symmetry reach**
(it forbids the proper index‑2 image `QR(p) ≠ (ℤ/p)^×`, which Theorem A cannot
touch), **not the numerical regime**. An **exhaustive** census
(`norm_form_obstruction.py`, check **[4]**) over **every** prime `p≡1(mod4)`
dividing an odd `L≤1200` finds:

> **428** classes `(L,p)` total; **139** are **forbidden** (i.e. **(R)+(S)**
> infeasible), across **116** distinct lengths, primes up to **373**. Examples:
> `(L,p)=(65,5),(65,13),(75,5),(85,17),(87,29),(91,13),(111,37),(119,17),(123,41),
> (183,61),(185,5),(185,37),(187,17),(203,29),…`.

For each forbidden class, `2L+2` is not a sum of two squares in `ℤ` (so Theorem A
already forbids the *full*‑image class), and additionally not a sum of two squares
in `𝒪_{ℚ(√p)}` (so Theorem C forbids the *index‑2* class): a strictly deeper,
symmetry‑level statement. Unlike Theorem A (Corollary 6.1), the forbidden lengths
here are *not* a full congruence class (e.g. for `p=5` they are a proper subset of
`L≡5 (mod 10)`), so a clean unconditional infinitude proof does not follow from
Dirichlet; it is left as an open problem (§10).

**Proposition D (`p≡3 mod 4`, `K=QR(p)`: exact identity, census‑permissive).**
*For `p≡3(mod4)` (including `p=3`), `p|L`, `H` with `K_p=QR(p)`, an `H`‑invariant
Legendre pair forces the **exact** identity*

> `2L+2 = g(a₁,a₂)+g(b₁,b₂)`, `g(x,y)=x²−xy+(p+1)/4·y²` (principal form of
> discriminant `−p`; `p=3` is the Eisenstein norm `x²−xy+y²`),

*a sum of two norms from `𝒪_{ℚ(√−p)}`. This is a proven necessary condition. Its
**solvability** is a finite‑census fact: no infeasible case was found for
`p≡3(mod4)`, `L≤1500` (797 cases; `norm_form_obstruction.py`, check **[5]**, with
sample saved witnesses computed via the complete bound `4g=(2x−y)²+p y²`). We therefore
report the imaginary index‑2 case as **census‑permissive** — no closed nonexistence
obstruction was found — while making **no universal‑solvability claim**.*

*Proof of the identity.* Here `−1∉QR(p)`, so `𝕂_2^+=ℚ` and `|Ã(k)|²=Ã(1)Ã(−1)
=N(α)`, the field norm of `α=a₁+a₂η₀ ∈ 𝒪_{ℚ(√−p)}`, `η₀=(−1+√−p)/2`; `N(α)=g(a₁,a₂)`.
**(PSD‑p)** gives `N(α)+N(β)=2L+2`. ∎

**Interpretation.** Proposition D indicates *why* proper‑subgroup families in
`f=2` imaginary‑period situations resisted closed obstructions in the `L=333` study
and had to be settled by exact search; it is an honest negative (census‑level)
finding, in contrast to Theorem C. It is limited to `f=2`: for `f≥4` imaginary the
relative norm is generally irrational (Remark 4.2), so no permissive conclusion
holds.

**Remark 5.1 (higher totally real index).** Theorem B applies to any `−1∈K` of
index `f`, giving *`2L+2` a sum of two squares in the totally real order
`𝒪_{𝕂_f}`* — a degree‑`f` real field. For `f=4` this requires `p≡1(mod8)`; the
collapse mechanism (`Ã(k)` real, in the degree‑`f` field) is verified for
`(p,f)=(17,4),(41,4)`. A systematic census of `f≥4` classes is a natural
continuation (§10).

---

## 6. Corollary 1 — infinite families of forbidden surjecting‑symmetry classes

**Corollary 6.1 (infinite forbidden families; Theorem A).** *Fix an odd prime `p`.
There are infinitely many odd multiples `L` of `p` with `2L+2` not a sum of two
squares; for each, the fixed‑symmetry class “`H ≤ (ℤ/L)^×` surjects onto
`(ℤ/p)^×`” is forbidden — no `H`‑invariant Legendre pair of length `L` exists (in
particular none invariant under a multiplier that is a primitive root mod `p`).
This forbids symmetry classes, not lengths.*

*Proof.* Choose a prime `r ≡ 3 (mod 4)` with `r ∤ 2p` (Dirichlet: infinitely many
exist). By CRT the system `L ≡ 0 (mod p)`, `L ≡ r−1 (mod r²)`, `L ≡ 1 (mod 2)` has
a solution, and its solutions form an arithmetic progression with common
difference `2pr²`, hence are infinite. Each solution is odd, divisible by `p`, and
has `v_r(L+1)=1` (since `L+1 ≡ r (mod r²)`), so `L+1`—hence `2L+2`—is not a sum of
two squares (Remark 3.1). A surjecting `H` exists by Remark 3.3. ∎

The construction and a verified batch (12 lengths per prime, with an explicit
surjecting generator) are in `scripts/families.py`; e.g. (lengths at which the
surjecting‑mod‑`p` class is forbidden):

| `p` | first such lengths `L` (AP, common difference) |
|----|-----------------------------------------------------|
| 3  | 153, 447, 741, 1035, 1329, 1623, … (diff 294) |
| 5  | 65, 155, 245, 335, 425, 515, … (diff 90) |
| 7  | 119, 245, 371, 497, 623, 749, … (diff 126) |
| 11 | 11, 209, 407, 605, 803, 1001, … (diff 198) |
| 37 | 407, 1073, 1739, 2405, 3071, 3737, … (diff 666) |

**Corollary 6.2 (density).** *For each fixed odd prime `p`, the odd multiples `L` of
`p` with `2L+2` not a sum of two squares have asymptotic density `1` among odd
multiples of `p`; for each such `L` the surjecting‑mod‑`p` symmetry class is
forbidden.* Indeed sums of two squares have density `0` (Landau–Ramanujan: their
counting function is `∼ K·X/√(log X)`, `K≈0.7642`), so their complement in any
fixed arithmetic progression has density `1`. (Empirically, up to `4000`, the
fraction is already `0.60–0.71`; it tends to `1` slowly like `1 − O(1/√log X)`.
See `families.py`. This is a statement about symmetry classes, not about the
existence of Legendre pairs of those lengths.)

**Theorem C (index‑2, `p≡1 mod4`).** The exhaustive census (§5) records `139`
forbidden classes with `L≤1200` (across 116 distinct lengths); for `p=5` the
forbidden lengths include `65,75,175,185,235,265,285,315,…`. These are **not** a
full congruence class (they are a proper, apparently positive‑density subset of
`L≡5 (mod 10)`), so — in contrast to Corollary 6.1 — we do *not* have an
unconditional infinitude proof; establishing (or refuting) it is Problem (i) in
§10. The empirical data strongly suggest infinitely many.

---

## 7. Corollary 2 — simultaneous per‑prime forbidden images

For composite `L`, the theorems constrain the multiplier group at *every* prime
`p|L` at once.

**Corollary 7.1.** *Let `L` be odd with `2L+2` not a sum of two squares, and let
`(a,b)` be an `H`‑invariant Legendre pair.  Then for every prime `p|L`
simultaneously, `K_p ≠ (ℤ/p)^×` (Theorem A); and for every `p≡1(mod4)` with `p|L`
such that the index‑2 system **(R)+(S)** is infeasible, `K_p ≠ QR(p)` (Theorem C).
Equivalently, `H` maps into `∏_{p|L}(\text{admissible subgroups of }(ℤ/p)^×)`.*

`scripts/families.py` tabulates this; representative rows (“forbidden” = that
image is a forbidden fixed‑symmetry class):

| `L` | `2L+2` | per‑prime verdict |
|----|--------|-------------------|
| **185** = 5·37 | 372 | `p=5`: full **forbidden(A)**, `QR(5)` **forbidden(C)**; `p=37`: full **forbidden(A)**, `QR(37)` **forbidden(C)** |
| 555 = 3·5·37 | 1112 | `p=3`: full forbidden(A); `p=5`: full forbidden(A), `QR(5)` forbidden(C); `p=37`: full forbidden(A), `QR(37)` forbidden(C) |
| 65 = 5·13 | 132 | `p=5`: full forbidden(A), `QR(5)` forbidden(C); `p=13`: full forbidden(A), `QR(13)` forbidden(C) |
| 333 = 3²·37 | 668 | `p=3`: full forbidden(A); `p=37`: full forbidden(A) (`QR(37)` **not** forbidden — see §8) |
| 1443 = 3·13·37 | 2888 = 2³·19² | `2L+2` **is** a sum of two squares — no class forbidden by A/C at any prime |

**Spotlight `L=185`.** `185` is a currently **open** Legendre‑pair length — it is
on the list of lengths `≤200` left unsettled in [KKB+23] (April 2024):
`{115,145,159,161,169,175,177,185,187,195}`. The theorems give a new restriction
on the *symmetry* of any invariant LP of length `185`: its multiplier group must
have image **trivial** mod `5` (both `(ℤ/5)^×` and `QR(5)` are forbidden classes)
and image *neither full nor `QR(37)`* mod `37`. This constrains the symmetry of a
potential LP(185); it does **not** decide LP(185) existence, and it does not follow
from the two‑square condition alone (which only forbids the *full*‑image classes).

---

## 8. Corollary 3 — the `L = 333` consequence, and the theorem boundary

`L=333=3²·37`, Hadamard order `2L+2=668=2²·167` with `167 ≡ 3 (mod 4)` prime,
so `668` is **not** a sum of two squares.  Applying the theorems (script
`scripts/l333_consequences.py`, cross‑checked against the **vendored, hashed**
metadata `data/lp333_classification_metadata.json`, extracted from
`lp333/results/subgroup_classification.json` with its source sha256 recorded for
self‑containment):

* **Theorem A, `p=3`.** `(ℤ/3)^×` has order 2; Theorem A forbids every class with
  `K_3=(ℤ/3)^×`. Surviving `H` lie in `ker((ℤ/333)^× → (ℤ/3)^×)`, the order‑108
  subgroup — this is exactly why the classification enumerates the `30` subgroups
  of that kernel.  *(Theorem A is the source of the mod‑3 reduction, not merely a
  restatement of it.)*

* **Theorem A, `p=37`.** Forbids the classes that surject onto `(ℤ/37)^×`;
  these are ids `25,26,27,29` (orders `36,36,36,108`).  This **matches exactly**
  the vendored metadata’s `killed_ids = {25,26,27,29}` (assertion in the script).

* **Theorem C, `p=37`.** `37≡1(mod4)`, so the index‑2 image `QR(37)` (order 18) is
  the *real‑quadratic* case. Here **(R)+(S)** for `2L+2=668` in `𝒪_{ℚ(√37)}` **is
  solvable** (a witness is produced), so Theorem C does **not** fire. The families
  with image `QR(37)` (ids `20,21,22`, and `28` which has image `QR(37)` of order
  18 inside a larger group) are therefore **not settled by Theorems A/C** — the
  prior study settled them by meet‑in‑the‑middle. Proposition D (for the `mod 9`
  imaginary/Eisenstein images, the `f=2` imaginary case) likewise yields no closed
  obstruction, consistent with the study settling those by CP‑SAT/exhaustion.

**The boundary.** The general theorems, applied at `L=333`, close *exactly* the 4
surjecting‑mod‑37 classes and produce the entire mod‑3 reduction to the order‑108
kernel. The remaining classes are **not settled by Theorems A/C** (image `QR(37)`
and smaller / imaginary images); we make **no claim** that they are irreducibly
computational — other closed obstructions may well exist (e.g. higher‑index
totally‑real analogues, or hybrids using the size/parity constraints; §10). Thus
this note is not a re‑derivation of the `L=333` computation: it isolates the part
forced by a general obstruction, and it produces new forbidden classes at *other*
lengths (§5–§7) that the `L=333` study never touched.

---

## 9. What is established prior art, and what is potentially new

Following a prior‑art review (including the zbMATH review of [GK02]), the
attribution is now settled as follows. We separate the established ingredients and
the base obstruction from the potentially‑new refinements.

**Established prior art.**

* **Compression / DFT identity (Lemma 2.1).** Đoković–Kotsireas, *Compression of
  periodic complementary sequences and applications* [DK15]: exactly `X̃(k)=X(mk)`
  for `m`‑compressions. Used verbatim.
* **LP / PSD formalism (§1).** Fletcher–Gysin–Seberry [FGS01] introduced Legendre
  pairs, the order‑`2L+2` construction, and the PSD condition `|A|²+|B|²=2L+2`.
* **Compression + sum‑of‑two‑squares (the base obstruction, Theorem A).** This
  pairing is **established**: it is used for `ℓ≡0(mod 3)` and `(mod 5)` in [KK21],
  [KKB+23]; it is studied directly under the name “Legendre pairs under
  compression” by Kotsireas–Gómez–Gómez‑Pérez [KGG25]; and in the quaternary
  setting Kotsireas–Koutschan–Winterhof [KKW25] explicitly state that the
  compression construction is available exactly when the relevant integer is a sum
  of two squares, and they use **Galois theory for cyclotomic fields to sharpen
  the PSD test** — precisely the style of machinery underlying Theorem B. An
  **informal** README of the `hadamard668` project [Cho25] states the `L=333`
  `p=3`/`p=37` instances. **Consequently Theorem A is presented here as a clean
  synthesis / general formulation of this established machinery, and is NOT claimed
  as new.**
* **[GK02] is not the relevant prior art.** Georgiou–Koukouvinos, *On generalized
  Legendre pairs and multipliers of the corresponding supplementary difference
  sets*, Util. Math. **61** (2002) 47–63 (Zbl 1001.05031): per its zbMATH review, a
  **multiplier‑based small‑length construction / search strategy**, not a
  compression / norm‑form *nonexistence* theorem. It therefore does not anticipate
  Theorem A’s obstruction, nor Theorems B–C.
* **Cyclotomic norm‑form machinery (§4).** Turyn [Tur65], Baumert [Bau71], Storer
  [Sto67], Lander [Lan83]: character‑sum / Gaussian‑period / norm‑form nonexistence
  for cyclic difference sets. The algebraic framework is theirs.
* **Sum‑of‑two‑squares in optimal‑design theory.** Ehlich [Ehl64], Wojtas [Woj64]:
  an `n−1=x²+y²` condition for `D`‑optimal matrices of order `n≡2(mod4)` — a
  different modular class and object.

**Potentially new (pending a broader specialist review).**

Since Galois–cyclotomic PSD conditions are already in use ([KKW25]), we label the
refinements only as *potentially new*, not as established priority:

1. **Theorem B — fixed‑field formulation.** Organising the compression obstruction
   by the image `K_p` and its fixed field: `2L+2` as a sum of two squares in the
   totally‑real order `𝒪_{𝕂_f}`, with the `−1∈K_p` (real) vs. `−1∉K_p` (CM)
   dichotomy and the `f`‑dependence (Remarks 4.1–4.2). *Potentially new as a
   formulation; the underlying Galois/Gaussian‑period tools are classical and in
   current use.*
2. **Theorem C — real‑quadratic index‑2 obstruction.** The explicit `(R)+(S)`
   system for `p≡1(mod4)`, `K_p=QR(p)`, forbidding the proper `QR(p)` class that
   Theorem A cannot touch (within the same numerical regime), with an exhaustive
   census (**139 of 428** classes, `L≤1200`). *Potentially new; this is the main
   candidate contribution for non‑surjective images.*
3. **Proposition D** — the exact norm identity plus the finite‑census permissiveness
   for `f=2` imaginary and the `f≥4` irrationality obstruction (Remark 4.2).
   *A bounded negative/structural result, not a universal theorem.*
4. **Corollaries and the `L=333` boundary** (§6–§8). *Straightforward consequences;
   potentially new as stated, but not claimed beyond the potentially‑new status of
   Theorems B–C.*

**Recommendation.** A broader specialist review (and a scan of
Georgiou–Koukouvinos, Util. Math. 56 (1999); Koukouvinos–Seberry–Whiteman–Xia,
JSPI 62 (1997)) is advisable before asserting priority for Theorems B–C. Nothing in
the *correctness* of Theorems A–D depends on the attribution; only the priority
claim does, and it is deliberately kept modest.

---

## 10. Limitations and directions

* **Problem (i): infinitude for Theorem C.** Prove or refute that, for a fixed
  prime `p≡1(mod4)`, infinitely many odd multiples `L` of `p` have `2L+2` **not**
  a sum of two squares in `𝒪_{ℚ(√p)}`. Equivalently, does the quaternary
  form‑with‑constraint **(R)+(S)** fail to represent `2L+2` for infinitely many
  `L`? The exhaustive census (139 of 428 classes, `L≤1200`) shows a
  positive‑density‑looking exceptional set, but the forbidden `L` are not a full
  congruence class, so Dirichlet does not settle it.
* **Problem (ii): higher totally real index `f≥4`** (Remark 5.1). The collapse
  mechanism is verified for `(p,f)=(17,4),(41,4)`, but a census of forbidden
  classes (requiring arithmetic in real cyclic fields of degree `≥4`) is open.
* **Problem (iii): the `f≥4` imaginary case** (Remark 4.2). Since `|Ã(k)|²` is
  then generally irrational (lands in `𝕂_f^+`), the PSD identity is an equation in
  a nontrivial real order; whether it yields nonexistence obstructions is open.
* Composite compressions `d=p₁p₂` and prime‑power compressions `d=p^e` fit the
  same Lemma 2.1 framework and may yield mixed obstructions.
* Whether Theorem C (or higher‑`f` analogues) can be combined with the exact
  size/parity constraints (`|ã_j|≤L/p`, row sum `±1`) into a stronger *hybrid*
  closed obstruction — possibly reaching some `QR(37)` classes at `L=333` — is an
  attractive open question.

*(Scope note: multipliers‑with‑translate are deliberately out of scope, per
Remark 3.4; all results here are for fixed `H`‑invariance.)*

---

## 11. Bibliography

```
[FGS01]  R.J. Fletcher, M. Gysin, J. Seberry. "Application of the Discrete Fourier
         Transform to the Search for Generalised Legendre Pairs and Hadamard
         Matrices." Australasian J. Combinatorics 23 (2001) 75–86.
[DK15]   Đ.Ž. Đoković, I.S. Kotsireas. "Compression of Periodic Complementary
         Sequences and Applications." Designs, Codes and Cryptography 74(2) (2015)
         365–377. arXiv:1302.0571; DOI 10.1007/s10623-013-9862-z.
[KK21]   I. Kotsireas, C. Koutschan. "Legendre Pairs of Lengths ℓ ≡ 0 (mod 3)."
         J. Combinatorial Designs 29(12) (2021) 870–887. arXiv:2101.03116;
         DOI 10.1002/jcd.21806.
[KKB+23] I. Kotsireas, C. Koutschan, D. Bulutoglu, J. Arquette, J. Turner,
         K.P. Ryan. "Legendre Pairs of Lengths ℓ ≡ 0 (mod 5)." Special Matrices
         11 (2023) 20230105. arXiv:2111.02105; DOI 10.1515/spma-2023-0105.
         [uses compression + a sum-of-two-squares condition]
[KGG25]  I.S. Kotsireas, A.-I. Gómez, D. Gómez-Pérez. "On Properties of Legendre
         Pairs under Compression." Proc. ISSAC 2025, pp. 79–86.
         DOI 10.1145/3747199.3747549.
[KKW25]  I.S. Kotsireas, C. Koutschan, A. Winterhof. "Quaternary Legendre Pairs
         II." Discrete Mathematics 348(9) (2025), art. 114501. arXiv:2408.16318;
         DOI 10.1016/j.disc.2025.114501. [compression requires the relevant
         integer to be a sum of two squares; uses Galois theory for cyclotomic
         fields to sharpen the PSD test]
[TBKG21] J. Turner, D. Bulutoglu, I. Kotsireas, A. Geyer. "A Legendre Pair of
         Length 77." Designs, Codes and Cryptography 89 (2021) 2787–2797.
         arXiv:2101.10918.
[GK02]   S. Georgiou, C. Koukouvinos. "On Generalized Legendre Pairs and
         Multipliers of the Corresponding Supplementary Difference Sets."
         Utilitas Mathematica 61 (2002) 47–63. Zbl 1001.05031. [per its zbMATH
         review: a multiplier-based small-length construction/search strategy,
         NOT a compression/norm-form nonexistence theorem]
[Tur65]  R.J. Turyn. "Character Sums and Difference Sets." Pacific J. Math. 15(1)
         (1965) 319–346. DOI 10.2140/pjm.1965.15.319.
[Bau71]  L.D. Baumert. Cyclic Difference Sets. LNM 182, Springer, 1971.
[Sto67]  T. Storer. Cyclotomy and Difference Sets. Markham, Chicago, 1967.
[Lan83]  E.S. Lander. Symmetric Designs: An Algebraic Approach. LMS LNS 74,
         Cambridge Univ. Press, 1983.
[Ehl64]  H. Ehlich. "Determinantenabschätzungen für binäre Matrizen." Math. Z. 83
         (1964) 123–132.
[Woj64]  M. Wojtas. "On Hadamard's Inequality for the Determinants of Order Non-
         Divisible by 4." Colloq. Math. 12 (1964) 73–83.
[Eli25]  S. Eliahou. "A 64-modular Hadamard Matrix of Order 668." Australasian J.
         Combinatorics 93 (2025) 422–428.
[Cho25]  P. Chojecki. hadamard668 project (informal), github.com/przchojecki/hadamard668.
```

---

## 12. Reproducibility

```
scripts/cyclo.py                  exact arithmetic in ℚ(ζ_L) modulo Φ_L
scripts/verify_core.py            V1–V5: PSD identity, Lemma 2.1, surjective and
                                  Gaussian-period collapses (all exact)
scripts/norm_form_obstruction.py  [1] symbolic (R)/(S), norm g, 4g bound, p=3;
                                  [2] totally-real collapse f=2,4; [3] CM relative
                                  norm (f=2 rational; f=4 p=13 IRRATIONAL, Q(√13));
                                  [4] EXHAUSTIVE Theorem C census (428 cases, 139
                                  forbidden); [5] Proposition D finite census
                                  (797 cases, 0 infeasible; witnesses)
scripts/l333_consequences.py      L=333 derivation from vendored metadata + cross-check
scripts/families.py               infinite forbidden families, density, simultaneous
data/lp333_classification_metadata.json  vendored L=333 subgroup metadata (with
                                  provenance + source sha256), for self-containment
scripts/check_note_claims.py      asserts every numeric claim in this note
scripts/run_all.sh                one-shot driver; writes certificates/*.json + manifest
```

Requirements: Python 3, `sympy`, `numpy`. Each script prints its checks and writes
a JSON certificate under `certificates/`. `run_all.sh` runs the whole pipeline;
`manifest.sha256` fixes the artifact hashes (note, scripts, vendored data,
certificates). The artifact is **self‑contained**: the only external input, the
`L=333` subgroup metadata, is vendored in `data/` with its source path and sha256
recorded, and is independently regenerable by `lp333/code/classify.py`.
