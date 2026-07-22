# Multiplier obstructions for Legendre pairs of length 333

[![License: MIT](https://img.shields.io/badge/code-MIT-blue.svg)](LICENSE)
[![Documentation: CC BY 4.0](https://img.shields.io/badge/docs-CC%20BY%204.0-lightgrey.svg)](LICENSES/CC-BY-4.0.txt)

This repository contains proof-carrying computations and analytic obstructions
for multiplier-invariant Legendre pairs of length 333, a structured route to a
real Hadamard matrix of order 668.

## Result

Among the 30 common-multiplier subgroups compatible with the initial mod-3
obstruction:

- 21 are proved impossible;
- all 19 subgroups of order at least 9 are impossible;
- the nine unresolved subgroups have order at most 6.

The last order-9 family (`id12`) is excluded by a short analytic
9-compression argument. Its compressed values are forced into
`{+/-1,+/-17,+/-19,+/-35,+/-37}`. The LP equations force `+17` and `-17`
into one compressed sequence; at the shift joining them, the combined
autocorrelation is at most `-240`, contradicting the required `-74`.

This **does not construct or disprove** a Hadamard matrix of order 668. The
unrestricted problem remains open.

## Repository layout

- [`paper/`](paper/) — research outcome, classification, analytic proof,
  fixed-field note, and complete search log.
- [`lp333/`](lp333/) — subgroup classification, exact searches,
  certificates, and proof verifiers.
- [`compression_theorem/`](compression_theorem/) — fixed-field and
  real-quadratic compression refinements.
- [`mod64/`](mod64/) — exact reconstruction and lifting analysis of the known
  64-modular order-668 construction.
- [`scripts/`](scripts/) — independent Hadamard/Goethals-Seidel verifiers.

## Quick verification

The analytic id12 proof and generalized compression checks need only Python:

```bash
python3 lp333/id12_phase2/code/standalone_verifier.py
python3 lp333/id12_phase2/code/general_verifier.py
```

For the complete proof-carrying pipeline, download the proof artifact attached
to release `v1.0.0`, extract it into the repository root, then run:

```bash
./scripts/bootstrap.sh
source lp333/.venv/bin/activate
bash lp333/code/run_all.sh
bash compression_theorem/scripts/run_all.sh
```

The release asset is:

```text
proof-artifacts-v1.0.0.tar.zst
```

See [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for exact commands and expected
results.

## Scope and attribution

The basic compression/sum-of-two-squares mechanism is established prior art.
The fixed-field formulation and real-quadratic index-2 refinement in the
supporting note are labeled potentially new pending specialist review.

All nonexistence statements concern specified **fixed multiplier symmetries**,
not global Legendre-pair or Hadamard nonexistence.

## Citation

Citation metadata are provided in [`CITATION.cff`](CITATION.cff). A Zenodo DOI
will be added after the immutable release is archived.

## Licenses

- Source code: [MIT](LICENSE)
- Original notes, certificates, and generated data: [CC BY 4.0](LICENSES/CC-BY-4.0.txt)
- Third-party components retain their own licenses; see
  [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
