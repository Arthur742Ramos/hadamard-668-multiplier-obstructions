#!/usr/bin/env bash
# One-shot driver for the compression-theorem note.
# Runs all verifications and censuses, writing JSON certificates under certificates/.
set -euo pipefail
cd "$(dirname "$0")/.."
PY=python3
echo "===================================================================="
echo " Compression obstruction for multiplier-invariant Legendre pairs"
echo "===================================================================="
echo
echo ">>> [1/5] Core identities (exact, mod Phi_L): verify_core.py"
$PY scripts/verify_core.py
echo
echo ">>> [2/5] Gaussian-period norm forms: norm_form_obstruction.py"
$PY scripts/norm_form_obstruction.py
echo
echo ">>> [3/5] L=333 consequences + cross-check: l333_consequences.py"
$PY scripts/l333_consequences.py
echo
echo ">>> [4/5] Infinite families / density / simultaneous: families.py"
$PY scripts/families.py
echo
echo ">>> [5/5] Note claim-checks: check_note_claims.py"
$PY scripts/check_note_claims.py
echo
echo "All done.  Certificates in certificates/.  Building manifest..."
{ shasum -a 256 theorem_note.md README.md data/*.json scripts/*.py scripts/*.sh certificates/*.json 2>/dev/null || \
  sha256sum theorem_note.md README.md data/*.json scripts/*.py scripts/*.sh certificates/*.json; } > manifest.sha256
echo "wrote manifest.sha256"
