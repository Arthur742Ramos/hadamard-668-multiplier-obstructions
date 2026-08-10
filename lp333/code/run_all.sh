#!/usr/bin/env bash
# One-shot reproduction driver for the LP(333) exact proof pipeline.
# Requires: python3 (stdlib only for the core proofs), a C++ compiler, and the
# local venv at ../.venv with ortools installed.  z3 (../../solver-venv) is
# optional and only adds a third corroborating engine for id12.
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(cd .. && pwd)"
PY=python3
VENV="$ROOT/.venv/bin/python"
[ -x "$VENV" ] || VENV=python3

echo "[1/14] classify subgroup lattice"
$PY classify.py > /dev/null
echo "[2/14] proved obstruction certificates (mod-3, mod-37)"
$PY obstructions.py
echo "[3/14] cheap necessary conditions (row-sum, 37-compression)"
$PY necessary_conditions.py | tail -3
echo "[4/14] exact meet-in-the-middle on strong families (r<=27)"
$PY run_mitm.py 28 24 23 20 21 22 | sed 's/^/    /'
echo "[5/14] exact CP-SAT on remaining decidable phase-1 families"
for id in 11 13 14 15 19 20 21 23; do
  CPS_T=300 $VENV cpsat_search2.py $id | sed 's/^/    /'
done
echo "[6/14] validate orbit/PAF machinery"
$PY validate_and_refsearch.py > ../results/independent_validation.log
echo "[7/14] PHASE 2: value-set 9-compression (id12 primary; id6,id8 bonus)"
( cd ../id12_phase2 && ./run_all.sh > results/run_all.log 2>&1 )
echo "    phase-2 done; standalone verifier:"
$PY ../id12_phase2/code/standalone_verifier.py | tail -2 | sed 's/^/    /'
echo "[8/14] congruence-kernel fibre obstruction for id 2"
$PY ../id2_congruence_kernel/code/standalone_verifier.py | tail -1 | sed 's/^/    /'
echo "[9/14] CRT mod-8 obstruction for ids 9 and 10"
$PY ../id9_id10_mod8/code/standalone_verifier.py | tail -1 | sed 's/^/    /'
echo "[10/14] consolidate verdicts (asserts num_impossible=24, all order>=9 impossible)"
$PY consolidate.py | tail -3
echo "[11/14] regenerate consolidated certificates"
$PY make_certificates.py | tail -3
echo "[12/14] rerun and validate all proof-carrying SAT artifacts"
$PY ../proof_phase2/verify_artifacts.py --full >/dev/null
echo "    proof artifacts OK"
echo "[13/14] regenerate reproducible SHA-256 manifest (excludes volatile *.log)"
( cd "$ROOT" && find . -type f \
     \( -name '*.py' -o -name '*.json' -o -name '*.md' -o -name '*.sh' \
        -o -name '*.txt' -o -name '*.cpp' \) \
     ! -path './.venv/*' ! -path '*/__pycache__/*' -print0 \
   | LC_ALL=C sort -z | xargs -0 shasum -a 256 > manifest.sha256 )
( cd "$ROOT" && shasum -a 256 -c manifest.sha256 >/dev/null && \
    echo "    manifest OK ($(wc -l < manifest.sha256) files)" )
echo "[14/14] done."
echo
echo "Status: 24/30 families IMPOSSIBLE; OPEN: 0,1,3,4,5,7."
echo "See ../report.md, ../results/master_status.json, and the id2/id9-id10/id12 reports."
