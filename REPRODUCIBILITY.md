# Reproducibility

## Lightweight analytic checks

These require only Python 3:

```bash
python3 lp333/id12_phase2/code/standalone_verifier.py
python3 lp333/id12_phase2/code/general_verifier.py
python3 lp333/id2_congruence_kernel/code/standalone_verifier.py
python3 lp333/id7_single_shift/code/standalone_verifier.py
python3 lp333/id9_id10_mod8/code/standalone_verifier.py
python3 scripts/verify_hadamard_csv.py --order 4 artifacts/hadamard4.csv
```

Each command checks a separate claim:

| Command | Required result |
|---|---|
| `id12_phase2/code/standalone_verifier.py` | prints `PROOF VERIFIED` |
| `id12_phase2/code/general_verifier.py` | reports ids 6, 8, and 12 impossible under the restricted 9-compression |
| `id2_congruence_kernel/code/standalone_verifier.py` | verifies the shift-111 fibre obstruction for id 2 |
| `id7_single_shift/code/standalone_verifier.py` | verifies the shift-111 orbit obstruction for id 7 |
| `id9_id10_mod8/code/standalone_verifier.py` | verifies the CRT mod-8 obstruction for ids 9 and 10 |
| `scripts/verify_hadamard_csv.py` | accepts the order-4 positive control |

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
25/30 families IMPOSSIBLE
all order >= 9 multiplier groups impossible
OPEN: 0,1,3,4,5
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
