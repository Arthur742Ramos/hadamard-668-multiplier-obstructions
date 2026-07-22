#!/usr/bin/env python3
"""Refresh the publication artifact SHA-256 manifest without rerunning solvers."""

from __future__ import annotations

import hashlib
from pathlib import Path


PHASE = Path(__file__).resolve().parent
EXCLUDED = {
    "audits/final_validation.json",
    "audits/full_validation.json",
    "logs/hash_verification.log",
}


def is_volatile(relative: str) -> bool:
    return (
        relative in EXCLUDED
        or relative.endswith(".log")
        or relative.startswith("logs/full_")
        or relative.startswith("audits/bogus_")
    )


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            hasher.update(block)
    return hasher.hexdigest()


def candidates() -> list[Path]:
    paths = []
    for directory in ("cnf", "proofs", "logs", "audits", "controls"):
        paths.extend(path for path in (PHASE / directory).glob("*") if path.is_file())
    paths.extend(
        PHASE / name
        for name in (
            "manifest.json",
            "report.md",
            "dependency_pins.json",
            "lp333_cnf.py",
            "run_proofs.py",
            "audit_rebuild.py",
            "independent_audit.py",
            "pin_dependencies.py",
            "verify_artifacts.py",
            "refresh_hashes.py",
        )
    )
    return sorted(
        {
            path
            for path in paths
            if path.is_file() and not is_volatile(str(path.relative_to(PHASE)))
        }
    )


def main() -> int:
    entries = [
        (digest(path), str(path.relative_to(PHASE))) for path in candidates()
    ]
    output = PHASE / "hashes" / "sha256sums.txt"
    output.write_text(
        "".join(f"{checksum}  {relative}\n" for checksum, relative in entries),
        encoding="ascii",
    )
    print(f"hashed={len(entries)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
