#!/usr/bin/env python3
"""Generate, solve, and independently check LP(333) CNF proof artifacts."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Dict, Iterable, List, Sequence

from lp333_cnf import (
    OrbitModel,
    build_lp333_model,
    build_singleton_model,
    direct_is_legendre_pair,
    exhaustive_small_audit,
    find_small_legendre_pair,
    orbit_spec_audit,
    random_equivalence_audit,
    transformation_truth_table_audit,
    write_dimacs,
)
from pin_dependencies import PIN_FILE, build_pins


PHASE = Path(__file__).resolve().parent
ROOT = PHASE.parent
CNF_DIR = PHASE / "cnf"
PROOF_DIR = PHASE / "proofs"
LOG_DIR = PHASE / "logs"
HASH_DIR = PHASE / "hashes"
AUDIT_DIR = PHASE / "audits"
CONTROL_DIR = PHASE / "controls"
DRAT_TRIM = PHASE / "tools" / "drat-trim" / "drat-trim"

CP_SAT_ONLY_IDS = (11, 13, 14, 15, 19)
MITM_IDS = (20, 21, 22, 23, 24, 28)
DEFAULT_IDS = CP_SAT_ONLY_IDS + MITM_IDS


def write_json(path: Path, payload: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def run_logged(
    command: Sequence[str], log_path: Path, timeout_seconds: int | None
) -> Dict:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"command": list(command), "timeout_seconds": timeout_seconds}
    try:
        with log_path.open("w", encoding="utf-8", newline="\n") as log:
            log.write("$ " + " ".join(command) + "\n")
            log.flush()
            completed = subprocess.run(
                command,
                cwd=ROOT,
                stdout=log,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )
            payload["returncode"] = completed.returncode
    except subprocess.TimeoutExpired:
        with log_path.open("a", encoding="utf-8", newline="\n") as log:
            log.write(f"\nTIMEOUT after {timeout_seconds} seconds\n")
        payload["returncode"] = None
        payload["timeout"] = True
    return payload


def read_solver_status(log_path: Path, returncode: int | None = None) -> str:
    if returncode == 20:
        return "UNSAT"
    if returncode == 10:
        return "SAT"
    content = log_path.read_text(encoding="utf-8", errors="replace")
    if "s UNSATISFIABLE" in content:
        return "UNSAT"
    if "s SATISFIABLE" in content:
        return "SAT"
    if "s UNKNOWN" in content:
        return "UNKNOWN"
    return "NO_STATUS"


def read_witness(path: Path) -> Dict[int, bool]:
    assignments: Dict[int, bool] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        fields = line.split()
        if not fields or fields[0] != "v":
            continue
        for field in fields[1:]:
            literal = int(field)
            if literal:
                assignments[abs(literal)] = literal > 0
    return assignments


def required_tools() -> Dict[str, str | None]:
    return {
        "cadical": shutil.which("cadical"),
        "drat_trim": str(DRAT_TRIM) if DRAT_TRIM.is_file() else None,
    }


def git_revision(path: Path) -> str | None:
    completed = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        text=True,
        capture_output=True,
        check=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else None


def parse_ids(value: str) -> List[int]:
    ids = [int(part) for part in value.split(",") if part.strip()]
    if not ids:
        raise argparse.ArgumentTypeError("expected at least one subgroup id")
    return ids


def control_record(length: int, cadical: str | None, timeout_seconds: int | None) -> Dict:
    model = build_singleton_model(length)
    cnf_path = CONTROL_DIR / f"positive_L{length}.cnf"
    witness_path = CONTROL_DIR / f"positive_L{length}.witness"
    solver_log = LOG_DIR / f"positive_L{length}_solver.log"
    write_dimacs(model.builder, cnf_path)

    exhaustive = exhaustive_small_audit(model)
    a, b = find_small_legendre_pair(length)
    za = [(1 - value) // 2 for value in a]
    zb = [(1 - value) // 2 for value in b]
    expected_cnf, _ = model.canonical_cnf_value(za, zb)
    result: Dict = {
        "length": length,
        "model": model.metadata(),
        "exhaustive_equivalence_audit": exhaustive,
        "known_normalized_legendre_pair": {"a": a, "b": b},
        "known_pair_directly_verified": direct_is_legendre_pair(a, b),
        "known_pair_satisfies_cnf": expected_cnf,
        "cnf": str(cnf_path.relative_to(PHASE)),
        "cnf_sha256": sha256(cnf_path),
    }
    if cadical is None:
        result["solver_status"] = "NOT_RUN"
        result["reason"] = "cadical not found"
        return result

    if witness_path.exists():
        witness_path.unlink()
    run = run_logged(
        [cadical, "-q", "-w", str(witness_path), str(cnf_path)],
        solver_log,
        timeout_seconds,
    )
    status = read_solver_status(solver_log, run.get("returncode"))
    result.update(
        {
            "solver_status": status,
            "solver_run": run,
            "solver_log": str(solver_log.relative_to(PHASE)),
            "solver_log_sha256": sha256(solver_log),
        }
    )
    if status == "SAT" and witness_path.exists():
        witness = read_witness(witness_path)
        if all(variable in witness for variable in model.za + model.zb):
            solver_za = [int(witness[variable]) for variable in model.za]
            solver_zb = [int(witness[variable]) for variable in model.zb]
            result["solver_witness_directly_verified"] = model.semantic_value(
                solver_za, solver_zb
            )
        else:
            result["solver_witness_directly_verified"] = False
            result["solver_witness_error"] = "missing primary assignments"
        result["witness"] = str(witness_path.relative_to(PHASE))
        result["witness_sha256"] = sha256(witness_path)
    return result


def run_controls(cadical: str | None, timeout_seconds: int | None) -> Dict:
    transformation = transformation_truth_table_audit()
    result = {
        "transformations": transformation,
        "length_5": control_record(5, cadical, timeout_seconds),
        "length_7": control_record(7, cadical, timeout_seconds),
    }
    write_json(AUDIT_DIR / "positive_controls.json", result)
    return result


def proof_record(
    subgroup_id: int,
    cadical: str | None,
    drat_trim: str | None,
    timeout_seconds: int | None,
    run_solver: bool,
) -> Dict:
    model, subgroup = build_lp333_model(subgroup_id)
    cnf_path = CNF_DIR / f"lp333_id{subgroup_id:02d}.cnf"
    proof_cnf_path = CNF_DIR / f"lp333_id{subgroup_id:02d}_unit_split.cnf"
    unit_split_map_path = CNF_DIR / f"lp333_id{subgroup_id:02d}_unit_split_map.json"
    proof_path = PROOF_DIR / f"lp333_id{subgroup_id:02d}_unit_split.drat"
    solver_log = LOG_DIR / f"lp333_id{subgroup_id:02d}_cadical.log"
    checker_log = LOG_DIR / f"lp333_id{subgroup_id:02d}_drat_trim.log"
    base_cnf_info = write_dimacs(model.builder, cnf_path)
    proof_cnf_info = write_dimacs(
        model.builder, proof_cnf_path, split_unit_clauses=True
    )
    write_json(
        unit_split_map_path,
        {
            "transformation": (
                "Every source unit (l) is replaced by (l v e) and (l v -e) "
                "for a fresh private mask variable e.  Existentially this is "
                "exactly equivalent to (l)."
            ),
            "base_cnf": str(cnf_path.relative_to(PHASE)),
            "proof_cnf": str(proof_cnf_path.relative_to(PHASE)),
            "source_unit_count": proof_cnf_info["unit_split_count"],
            "unit_split_map": proof_cnf_info["unit_split_map"],
        },
    )

    audit = {
        "model": model.metadata(),
        "subgroup_id": subgroup_id,
        "subgroup_order": len(subgroup["elements"]),
        "subgroup_generators": subgroup["generators"],
        "cnf_semantic_equivalence": random_equivalence_audit(
            model, samples=12, seed=333000 + subgroup_id
        ),
        "direct_orbit_paf_equivalence": orbit_spec_audit(
            subgroup_id, samples=24, seed=444000 + subgroup_id
        ),
    }
    write_json(AUDIT_DIR / f"lp333_id{subgroup_id:02d}.json", audit)
    record: Dict = {
        "subgroup_id": subgroup_id,
        "subgroup_order": len(subgroup["elements"]),
        "orbit_count": model.spec["r"],
        "shift_representatives": model.spec["num_reps"],
        "cnf": str(cnf_path.relative_to(PHASE)),
        "cnf_sha256": sha256(cnf_path),
        "cnf_bytes": cnf_path.stat().st_size,
        "cnf_dimacs": base_cnf_info,
        "proof_cnf": str(proof_cnf_path.relative_to(PHASE)),
        "proof_cnf_sha256": sha256(proof_cnf_path),
        "proof_cnf_bytes": proof_cnf_path.stat().st_size,
        "proof_cnf_dimacs": {
            key: value
            for key, value in proof_cnf_info.items()
            if key != "unit_split_map"
        },
        "unit_split_map": str(unit_split_map_path.relative_to(PHASE)),
        "unit_split_map_sha256": sha256(unit_split_map_path),
        "audit": str((AUDIT_DIR / f"lp333_id{subgroup_id:02d}.json").relative_to(PHASE)),
        "audit_sha256": sha256(AUDIT_DIR / f"lp333_id{subgroup_id:02d}.json"),
        "encoding": model.metadata(),
        "solver_status": "NOT_RUN",
        "external_check": {
            "status": "NOT_RUN",
            "verified": False,
        },
    }
    if model.direct_pb_obstructions:
        record["direct_pb_upper_bound_certificate"] = {
            "kind": "nonnegative weighted XOR sum cannot reach required target",
            "obstructions": model.direct_pb_obstructions,
        }
    if not run_solver:
        return record
    if cadical is None:
        record["solver_status"] = "NOT_RUN"
        record["solver_reason"] = "cadical not found"
        return record

    if proof_path.exists():
        proof_path.unlink()
    solver_run = run_logged(
        [
            cadical,
            "--binary=false",
            "--checkproof=1",
            "-q",
            str(proof_cnf_path),
            str(proof_path),
        ],
        solver_log,
        timeout_seconds,
    )
    solver_status = read_solver_status(solver_log, solver_run.get("returncode"))
    record.update(
        {
            "solver_status": solver_status,
            "solver_run": solver_run,
            "solver_log": str(solver_log.relative_to(PHASE)),
            "solver_log_sha256": sha256(solver_log),
        }
    )
    if proof_path.exists():
        record.update(
            {
                "proof": str(proof_path.relative_to(PHASE)),
                "proof_sha256": sha256(proof_path),
                "proof_bytes": proof_path.stat().st_size,
                "proof_format": "ASCII DRAT",
            }
        )

    if solver_status != "UNSAT":
        record["external_check"] = {
            "status": "NOT_ATTEMPTED",
            "verified": False,
            "reason": "CaDiCaL did not report UNSAT",
        }
        return record
    if drat_trim is None:
        record["external_check"] = {
            "status": "UNAVAILABLE",
            "verified": False,
            "reason": "drat-trim was not available",
        }
        return record
    if not proof_path.exists() or proof_path.stat().st_size == 0:
        record["external_check"] = {
            "status": "MISSING_PROOF",
            "verified": False,
            "reason": "CaDiCaL reported UNSAT without a nonempty trace",
        }
        return record

    checker_run = run_logged(
        [drat_trim, str(proof_cnf_path), str(proof_path), "-I"],
        checker_log,
        timeout_seconds,
    )
    checker_output = checker_log.read_text(encoding="utf-8", errors="replace")
    # drat-trim's early "trivial UNSAT" parser path prints "s VERIFIED" but leaves
    # its local ``sts`` value unset, yielding exit status 1 in the upstream tool.
    # The stable checker verdict is the documented text marker, which is also what
    # the supplied checker log preserves for external inspection.
    verified = "s VERIFIED" in checker_output
    record["external_check"] = {
        "status": "VERIFIED" if verified else "FAILED",
        "verified": verified,
        "verification_kind": (
            "input_cnf_trivial_unsat"
            if "trivial UNSAT" in checker_output
            else "drat_trace_verified"
        ),
        "checker": str(Path(drat_trim).relative_to(PHASE)),
        "checker_run": checker_run,
        "checker_log": str(checker_log.relative_to(PHASE)),
        "checker_log_sha256": sha256(checker_log),
    }
    if verified and checker_run.get("returncode") != 0:
        record["external_check"]["checker_exit_note"] = (
            "drat-trim emitted 's VERIFIED' on its early trivial-UNSAT path; "
            "upstream exits 1 on that path despite the verified marker"
        )
    return record


def write_hashes(paths: Iterable[Path]) -> Dict[str, str]:
    unique = sorted({path for path in paths if path.is_file()})
    entries = {
        str(path.relative_to(PHASE)): sha256(path)
        for path in unique
    }
    with (HASH_DIR / "sha256sums.txt").open("w", encoding="ascii", newline="\n") as handle:
        for relative, digest in entries.items():
            handle.write(f"{digest}  {relative}\n")
    return entries


def audit_dimacs(path: Path) -> Dict:
    """Independently validate a DIMACS header and every clause terminator."""
    with path.open("r", encoding="ascii") as handle:
        header = handle.readline().split()
        if len(header) != 4 or header[:2] != ["p", "cnf"]:
            raise AssertionError(f"invalid DIMACS header: {path}")
        variables = int(header[2])
        declared_clauses = int(header[3])
        actual_clauses = 0
        maximum_variable = 0
        empty_clauses = 0
        for line_number, line in enumerate(handle, start=2):
            fields = line.split()
            if not fields:
                continue
            literals = [int(field) for field in fields]
            if literals[-1] != 0:
                raise AssertionError(f"missing clause terminator in {path}:{line_number}")
            if any(literal == 0 for literal in literals[:-1]):
                raise AssertionError(f"embedded zero in {path}:{line_number}")
            if len(literals) > 1:
                maximum_variable = max(
                    maximum_variable,
                    max(abs(literal) for literal in literals[:-1]),
                )
            actual_clauses += 1
            empty_clauses += int(len(literals) == 1)
    if actual_clauses != declared_clauses:
        raise AssertionError(f"clause count mismatch in {path}")
    if maximum_variable > variables:
        raise AssertionError(f"variable bound mismatch in {path}")
    return {
        "variables": variables,
        "clauses": actual_clauses,
        "maximum_variable_seen": maximum_variable,
        "empty_clauses": empty_clauses,
        "result": "PASS",
    }


def write_report(manifest: Dict) -> None:
    records = manifest["records"]
    certified = [
        record["subgroup_id"]
        for record in records
        if record["external_check"]["verified"]
    ]
    direct_bound_records = [
        record for record in records if "direct_pb_upper_bound_certificate" in record
    ]
    hardening = manifest.get("publication_hardening", {})
    lines = [
        "# LP(333) proof-carrying CNF phase",
        "",
        "This directory supplies an independent SAT encoding of the orbit-level "
        "row-sum and PAF equations used by the earlier CP-SAT closures.",
        "",
        "For an orbit value `x_Q=1-2z_Q`, the encoder defines "
        "`w_QR = z_Q XOR z_R` with four exact CNF clauses.  For every shift "
        "representative it encodes",
        "",
        "`sum_{Q<R} W_s(Q,R) (w^a_QR + w^b_QR) = const_s + sum W_s + 1`.",
        "",
        "Its weighted sums are exact carry-save/full-adder circuits; their output "
        "bits are fixed to the target.  Each row condition is encoded exactly as "
        "`sum |Q| z_Q in {166,167}`.  Fixing orbit zero to `+1` is satisfiability "
        "preserving because either sequence can be globally negated independently.",
        "",
        "Each `*_unit_split.cnf` proof input is an exact existential reformulation "
        "of the corresponding base CNF: every unit `(l)` is replaced by `(l v e)` "
        "and `(l v -e)` for a fresh private `e`.  This prevents a checker from "
        "short-circuiting during input-unit preprocessing when a nontrivial DRAT "
        "trace is needed.  The complete fresh-variable mapping is saved beside "
        "each proof CNF in `cnf/*_unit_split_map.json`.  A few families have a "
        "stronger direct PB upper-bound contradiction; those are explicitly "
        "labeled `input_cnf_trivial_unsat` and carry the numeric bound in the "
        "manifest rather than being described as trace-checked.",
        "",
        "## Results",
        "",
        "| id | orbit variables/sequence | solver | independently checked evidence |",
        "|---:|---:|---|---|",
    ]
    for record in records:
        check = record["external_check"]
        lines.append(
            f"| {record['subgroup_id']} | {record['orbit_count']} | "
            f"{record['solver_status']} | "
            f"{check['status']} / {check.get('verification_kind', 'n/a')} |"
        )
    if direct_bound_records:
        lines.extend(
            [
                "",
                "### Direct PB upper-bound certificates",
                "",
                "For each row below, all weighted XOR variables are Boolean, so "
                "the required sum cannot exceed the recorded maximum:",
            ]
        )
        for record in direct_bound_records:
            witness = record["direct_pb_upper_bound_certificate"]["obstructions"][0]
            lines.append(
                f"* id {record['subgroup_id']}, shift {witness['shift']}: "
                f"required `{witness['required_weighted_xor_sum']}`, maximum "
                f"`{witness['maximum_weighted_xor_sum']}` "
                f"(shortfall `{witness['shortfall']}`)."
            )
    lines.extend(
        [
            "",
            f"Externally checked UNSAT evidence: **{certified}**.",
            "",
            "The checker is the locally built upstream `drat-trim`; its per-instance "
            "log must contain `s VERIFIED`.  Rows marked `drat_trace_verified` "
            "were checked against the saved DRAT trace.  Rows marked "
            "`input_cnf_trivial_unsat` have a stronger direct PB upper-bound "
            "certificate in the base CNF and manifest.  CNFs, ASCII DRAT traces, "
            "logs, and SHA-256 hashes are listed in `manifest.json` and "
            "`hashes/sha256sums.txt`.",
            "",
            "## Audits and controls",
            "",
            "* `audits/positive_controls.json` records exhaustive end-to-end "
            "equivalence checks for normalized length-5 (256 assignments) and "
            "length-7 (4096 assignments) Legendre-pair controls, including SAT "
            "solver witnesses.",
            "* The same file records exhaustive truth tables for the standalone "
            "XOR/PB equality and two-value PB-range transformations.",
            "* Each `audits/lp333_id*.json` records random direct full-length PAF "
            "checks and canonical-CNF versus direct-model checks.",
            "* `audit_rebuild.py` independently reconstructs orbit matrices and "
            "the full base/proof DIMACS serializations; its hash comparison is "
            "saved in `audits/independent_rebuild_audit.json`.",
            "* `manifest.json` also contains a DIMACS-header/terminator audit for "
            "every saved base, proof, and positive-control CNF.",
            "* `verify_artifacts.py` rechecks the saved hashes, checker markers, "
            "PB-bound records, controls, and DIMACS-audit status without rerunning "
            "CaDiCaL; `--full` reruns `drat-trim` on every saved trace, checks "
            "its exact marker/return behavior and checker-binary pin, and verifies "
            "rejection of a deliberately bogus proof.",
            "* `independent_audit.py` is a standard-library-only implementation "
            "that independently reconstructs subgroup orbits, PAF coefficients, "
            "the deterministic CNF serialization, and sampled CNF semantics.",
            "* `refresh_hashes.py` refreshes `hashes/sha256sums.txt` after "
            "verification-only artifacts change, without rerunning a solver.",
            "",
            "No status is asserted as proof-carrying unless its own `external_check` "
            "field is `VERIFIED`; a missing trace or checker result is reported "
            "explicitly rather than promoted to an exclusion.",
            "",
            "## Reproduction",
            "",
            "From `lp333/`, run `proof_phase2/run_proofs.py`.  It requires "
            "`cadical` and the bundled `proof_phase2/tools/drat-trim/drat-trim`; "
            "run `make -C proof_phase2/tools/drat-trim` if the checker binary is "
            "not already built.  A direct checker invocation is "
            "`proof_phase2/tools/drat-trim/drat-trim "
            "proof_phase2/cnf/lp333_id13_unit_split.cnf "
            "proof_phase2/proofs/lp333_id13_unit_split.drat -I`.",
        ]
    )
    if hardening:
        lines.extend(
            [
                "",
                "## Publication hardening",
                "",
                f"* Dependency pins: `{hardening['dependency_pins']['path']}` "
                f"({hardening['dependency_pins']['result']}); this pins `core.py`, "
                "`search_common.py`, subgroup data, and the checker binary.",
                f"* Standalone audit: `{hardening['standalone_independent_audit']['path']}` "
                f"({hardening['standalone_independent_audit']['result']}).",
                f"* Full checker rerun: `{hardening['full_verification']['path']}` "
                f"({hardening['full_verification']['result']}); it reruns every "
                "trace and confirms rejection of a bogus empty proof.",
                "* Full-checker logs are volatile and excluded from the immutable "
                "SHA-256 list; each log and the bogus-proof control is instead "
                "content-hashed inside the pinned full-validation record.",
            ]
        )
    (PHASE / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ids", type=parse_ids, default=list(DEFAULT_IDS))
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--skip-controls", action="store_true")
    parser.add_argument("--generate-only", action="store_true")
    args = parser.parse_args()

    for directory in (CNF_DIR, PROOF_DIR, LOG_DIR, HASH_DIR, AUDIT_DIR, CONTROL_DIR):
        directory.mkdir(parents=True, exist_ok=True)
    tools = required_tools()
    controls = (
        {"status": "SKIPPED"}
        if args.skip_controls
        else run_controls(tools["cadical"], args.timeout)
    )
    records = [
        proof_record(
            subgroup_id,
            tools["cadical"],
            tools["drat_trim"],
            args.timeout,
            not args.generate_only,
        )
        for subgroup_id in args.ids
    ]
    dimacs_header_audit = {
        str(path.relative_to(PHASE)): audit_dimacs(path)
        for path in sorted(CNF_DIR.glob("*.cnf")) + sorted(CONTROL_DIR.glob("*.cnf"))
    }
    manifest = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "generator": "proof_phase2/run_proofs.py",
        "target_cp_sat_only_ids": list(CP_SAT_ONLY_IDS),
        "cross_certification_ids": list(MITM_IDS),
        "requested_ids": args.ids,
        "tools": {
            "cadical": tools["cadical"],
            "cadical_version": (
                subprocess.run(
                    [tools["cadical"], "--version"],
                    text=True,
                    capture_output=True,
                    check=False,
                ).stdout.strip()
                if tools["cadical"]
                else None
            ),
            "drat_trim": tools["drat_trim"],
            "drat_trim_sha256": sha256(Path(tools["drat_trim"]))
            if tools["drat_trim"]
            else None,
            "drat_trim_git_revision": git_revision(DRAT_TRIM.parent)
            if tools["drat_trim"]
            else None,
        },
        "controls": controls,
        "dimacs_header_audit": dimacs_header_audit,
        "records": records,
        "hashes_file": "hashes/sha256sums.txt",
    }
    write_json(PHASE / "manifest.json", manifest)
    pins = build_pins()
    PIN_FILE.write_text(json.dumps(pins, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest["dependency_pins"] = {
        "path": "dependency_pins.json",
        "sha256": sha256(PIN_FILE),
        "result": "PASS",
    }
    write_json(PHASE / "manifest.json", manifest)
    write_report(manifest)
    hash_paths = list(CNF_DIR.glob("*"))
    hash_paths += list(PROOF_DIR.glob("*"))
    hash_paths += [
        path
        for path in LOG_DIR.glob("*")
        if path.name != "hash_verification.log" and not path.name.startswith("full_")
    ]
    hash_paths += [
        path
        for path in AUDIT_DIR.glob("*")
        if path.name not in {"final_validation.json", "full_validation.json"}
        and not path.name.startswith("bogus_")
    ]
    hash_paths += list(CONTROL_DIR.glob("*"))
    hash_paths += [
        PHASE / "manifest.json",
        PHASE / "report.md",
        PHASE / "lp333_cnf.py",
        Path(__file__),
        PHASE / "verify_artifacts.py",
        PHASE / "audit_rebuild.py",
        PHASE / "independent_audit.py",
        PHASE / "pin_dependencies.py",
        PHASE / "refresh_hashes.py",
        PIN_FILE,
    ]
    hashes = write_hashes(hash_paths)
    print(
        json.dumps(
            {
                "requested_ids": args.ids,
                "verified_ids": [
                    record["subgroup_id"]
                    for record in records
                    if record["external_check"]["verified"]
                ],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
