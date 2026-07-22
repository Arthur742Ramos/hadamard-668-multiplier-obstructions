#!/usr/bin/env bash
# Reproduce the id12 impossibility proof end-to-end.
# Uses the project venvs:  ../.venv (ortools, numpy),  ../../solver-venv (z3).
set -euo pipefail
cd "$(dirname "$0")"
ROOT="$(pwd)"

VENV="$ROOT/../.venv/bin/python"
ZVENV="$ROOT/../../../solver-venv/bin/python"
[ -x "$VENV" ] || VENV="$(command -v python3)"
[ -x "$ZVENV" ] || ZVENV="$(command -v python3)"

echo "== 1. exact core data + self-checks =="
( cd code && "$VENV" phase2_core.py >/dev/null && echo "phase2_core OK" )

echo "== 2. quartic Gaussian-period ring self-check =="
( cd code && "$VENV" periods.py | tail -2 )

echo "== 3. structural lemmas + compression solution set =="
( cd code && "$VENV" analysis1_structure.py | tail -3 )

echo "== 4. compression obstruction: identity + DFS + CP-SAT =="
( cd code && "$VENV" verify_compression.py | tail -3 )

echo "== 5. master certificate: exhaustive + CP-SAT (ortools) =="
( cd code && rm -f ../results/master_certificate.json && "$VENV" master_certificate.py E1 E2 | tail -2 )

echo "== 6. master certificate: z3 engine (merge) =="
( cd code && "$ZVENV" master_certificate.py E3 | tail -2 ) || echo "(z3 engine skipped: solver-venv unavailable)"

echo "== 7. Gaussian-period / PSD Galois-collapse check =="
( cd code && "$VENV" psd_analysis.py | tail -2 )

echo "== 8. assemble certificate + run embedded standalone verifier =="
( cd code && "$VENV" make_certificate.py | tail -2 )

echo "== 9. STANDALONE VERIFIER (pure stdlib, no venv) =="
( cd code && python3 standalone_verifier.py )

echo "== 10. GENERALIZATION: value-set 9-compression on all trivial-mod-9 families =="
( cd code && "$VENV" general_compression.py | tail -13 )

echo "== 11. GENERAL VERIFIER (pure stdlib): id6, id8, id12 closed; id0,id1 not =="
( cd code && python3 general_verifier.py | tail -9 )

echo "== 12. assemble generalized certificate =="
( cd code && "$VENV" make_general_certificate.py | tail -2 )

echo
echo "DONE.  Certificates:"
echo "  results/id12_impossible_certificate.json          (id12 primary)"
echo "  results/general_compression_certificate.json      (id6, id8, id12)"
