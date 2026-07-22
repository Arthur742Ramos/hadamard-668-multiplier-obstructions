# Reproducibility

## Lightweight analytic checks

These require only Python 3:

```bash
python3 lp333/id12_phase2/code/standalone_verifier.py
python3 lp333/id12_phase2/code/general_verifier.py
python3 scripts/verify_hadamard_csv.py --order 4 artifacts/hadamard4.csv
```

The first command must print `PROOF VERIFIED`. The second must report ids
6, 8, and 12 impossible under the value-set-restricted 9-compression.

## Environment

```bash
./scripts/bootstrap.sh
source lp333/.venv/bin/activate
```

The research release used Python 3, NumPy 2.5.1, SymPy 1.14.0,
OR-Tools 9.15.6755, and z3-solver 5.0.0.

## Full proof bundle

Download `proof-artifacts-v1.0.0.tar.zst` from the GitHub release and verify
its SHA-256 checksum against `artifacts/proof-artifacts-v1.0.0.sha256`.

```bash
zstd -d -c proof-artifacts-v1.0.0.tar.zst | tar -xf -
make -C lp333/proof_phase2/tools/drat-trim
python3 lp333/proof_phase2/verify_artifacts.py --full
```

The full verifier reruns `drat-trim`, checks dependency pins and proof
markers, rejects a bogus proof control, and verifies all proof records.

## Complete LP(333) pipeline

After extracting the proof bundle:

```bash
bash lp333/code/run_all.sh
```

Expected final status:

```text
21/30 families IMPOSSIBLE
all order >= 9 multiplier groups impossible
OPEN: 0,1,2,3,4,5,7,9,10
```

## Fixed-field note

```bash
bash compression_theorem/scripts/run_all.sh
```

Expected checked census:

```text
real-quadratic: 139 forbidden / 428 cases
imaginary-quadratic finite census: 0 infeasible / 797 cases
```

These are fixed-symmetry restrictions, not global Legendre-pair
nonexistence statements.
