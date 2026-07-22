#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV="$ROOT/lp333/.venv"

python3 -m venv "$VENV"
"$VENV/bin/python" -m pip install --upgrade pip
"$VENV/bin/python" -m pip install -r "$ROOT/requirements.txt"

if [ -f "$ROOT/lp333/proof_phase2/tools/drat-trim/Makefile" ]; then
  make -C "$ROOT/lp333/proof_phase2/tools/drat-trim"
fi

echo "Environment ready: $VENV"
