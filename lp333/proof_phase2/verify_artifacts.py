#!/usr/bin/env python3
"""Recheck the saved LP(333) proof-phase artifacts without rerunning a solver."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Dict, List, Tuple


PHASE = Path(__file__).resolve().parent
ROOT = PHASE.parent
AUDIT_DIR = PHASE / "audits"
LOG_DIR = PHASE / "logs"


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            hasher.update(block)
    return hasher.hexdigest()


def read_json(path: Path) -> Dict:
    return json.loads(path.read_text(encoding="utf-8"))


def exact_marker_count(output: str, marker: str) -> int:
    return sum(
        line.strip() == marker
        for line in output.replace("\r", "\n").splitlines()
    )


def dependency_pin_check(manifest: Dict) -> Tuple[Dict, List[str]]:
    pins_path = PHASE / "dependency_pins.json"
    errors = []
    if not pins_path.is_file():
        return {"result": "FAIL", "reason": "missing dependency_pins.json"}, [
            "dependency pins missing"
        ]
    pins = read_json(pins_path)
    checks = []
    for item in pins.get("files", []):
        path = (PHASE / item["path"]).resolve()
        actual = digest(path) if path.is_file() else None
        ok = actual == item.get("sha256")
        checks.append({"path": item["path"], "sha256": actual, "result": "PASS" if ok else "FAIL"})
        if not ok:
            errors.append(f"dependency pin mismatch: {item['path']}")
    classification_path = ROOT / "results" / "subgroup_classification.json"
    if classification_path.is_file():
        classification = read_json(classification_path)
        records = {int(item["id"]): item for item in classification["subgroups"]}
        for item in pins.get("subgroup_records", []):
            record = records.get(int(item["id"]))
            encoded = (
                json.dumps(record, sort_keys=True, separators=(",", ":")).encode("utf-8")
                if record is not None
                else b""
            )
            actual = hashlib.sha256(encoded).hexdigest() if record is not None else None
            if actual != item.get("canonical_sha256"):
                errors.append(f"subgroup pin mismatch: {item['id']}")
    else:
        errors.append("missing subgroup classification")

    checker_source_pin = next(
        (item for item in pins.get("files", []) if item["path"] == "tools/drat-trim/drat-trim.c"),
        None,
    )
    checker_manifest_hash = manifest.get("tools", {}).get("drat_trim_source_sha256")
    if (
        checker_source_pin is None
        or checker_manifest_hash != checker_source_pin.get("sha256")
    ):
        errors.append("checker source pin does not match manifest")
    return {
        "path": "dependency_pins.json",
        "sha256": digest(pins_path),
        "checks": checks,
        "result": "PASS" if not errors else "FAIL",
    }, errors


def run_checker(
    checker: Path, cnf: Path, proof: Path, log_path: Path, timeout: int
) -> Tuple[int | None, str]:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    command = [str(checker), str(cnf), str(proof), "-I"]
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
                timeout=timeout,
                check=False,
            )
            returncode = completed.returncode
    except subprocess.TimeoutExpired:
        with log_path.open("a", encoding="utf-8", newline="\n") as log:
            log.write(f"\nTIMEOUT after {timeout} seconds\n")
        returncode = None
    return returncode, log_path.read_text(encoding="utf-8", errors="replace")


def full_checker_check(manifest: Dict, timeout: int) -> Tuple[Dict, List[str]]:
    errors = []
    tools = manifest.get("tools", {})
    checker = Path(tools.get("drat_trim", ""))
    if not checker.is_absolute():
        checker = PHASE / checker
    checker_source = checker.parent / "drat-trim.c"
    expected_source_hash = tools.get("drat_trim_source_sha256")
    actual_source_hash = digest(checker_source) if checker_source.is_file() else None
    if actual_source_hash != expected_source_hash:
        errors.append("checker source hash mismatch")

    records = []
    trace_records = []
    for record in manifest["records"]:
        identifier = record["subgroup_id"]
        checker_log = LOG_DIR / f"full_id{identifier:02d}_drat_trim.log"
        returncode, output = run_checker(
            checker,
            PHASE / record["proof_cnf"],
            PHASE / record["proof"],
            checker_log,
            timeout,
        )
        verified_count = exact_marker_count(output, "s VERIFIED")
        rejected_count = exact_marker_count(output, "s NOT VERIFIED")
        kind = record["external_check"]["verification_kind"]
        if kind == "drat_trace_verified":
            ok = (
                returncode == 0
                and verified_count == 1
                and rejected_count == 0
                and "c trivial UNSAT" not in output
            )
            trace_records.append(record)
        elif kind == "input_cnf_trivial_unsat":
            ok = (
                returncode == 1
                and verified_count == 1
                and rejected_count == 0
                and "c trivial UNSAT" in output
            )
        else:
            ok = False
        if not ok:
            errors.append(f"id {identifier}: full checker behavior mismatch")
        records.append(
            {
                "id": identifier,
                "kind": kind,
                "returncode": returncode,
                "verified_marker_count": verified_count,
                "not_verified_marker_count": rejected_count,
                "log": str(checker_log.relative_to(PHASE)),
                "result": "PASS" if ok else "FAIL",
            }
        )

    if not trace_records:
        errors.append("no nontrivial trace available for bogus-proof control")
        bogus = {"result": "FAIL"}
    else:
        target = trace_records[0]
        bogus_proof = AUDIT_DIR / f"bogus_id{target['subgroup_id']:02d}_empty.drat"
        bogus_log = LOG_DIR / f"full_bogus_id{target['subgroup_id']:02d}_drat_trim.log"
        bogus_proof.write_text("0\n", encoding="ascii")
        returncode, output = run_checker(
            checker,
            PHASE / target["proof_cnf"],
            bogus_proof,
            bogus_log,
            timeout,
        )
        verified_count = exact_marker_count(output, "s VERIFIED")
        rejected_count = exact_marker_count(output, "s NOT VERIFIED")
        ok = returncode != 0 and verified_count == 0 and rejected_count == 1
        if not ok:
            errors.append("bogus proof was not rejected")
        bogus = {
            "target_id": target["subgroup_id"],
            "proof": str(bogus_proof.relative_to(PHASE)),
            "proof_sha256": digest(bogus_proof),
            "log": str(bogus_log.relative_to(PHASE)),
            "returncode": returncode,
            "verified_marker_count": verified_count,
            "not_verified_marker_count": rejected_count,
            "result": "PASS" if ok else "FAIL",
        }

    payload = {
        "kind": "full-independent-drat-trim-reverification",
        "checker": {
            "path": str(checker.relative_to(PHASE)),
            "source": str(checker_source.relative_to(PHASE)),
            "source_sha256": actual_source_hash,
            "expected_source_sha256": expected_source_hash,
            "result": "PASS" if actual_source_hash == expected_source_hash else "FAIL",
        },
        "records": records,
        "bogus_proof_control": bogus,
        "result": "PASS" if not errors else "FAIL",
        "errors": errors,
    }
    output_path = AUDIT_DIR / "full_validation.json"
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload, errors


def is_volatile_hash_entry(relative: str) -> bool:
    return (
        relative in {"audits/final_validation.json", "audits/full_validation.json", "logs/hash_verification.log"}
        or relative.startswith("logs/full_")
        or relative.startswith("audits/bogus_")
    )


def refresh_immutable_artifacts(manifest: Dict) -> None:
    """Regenerate report and immutable hashes after a full checker rerun."""
    from run_proofs import write_report
    from refresh_hashes import main as refresh_hashes

    write_report(manifest)
    if refresh_hashes() != 0:
        raise RuntimeError("could not refresh immutable artifact hashes")


def validate_full_validation(reference: Dict) -> Tuple[Dict | None, List[str]]:
    errors = []
    path = PHASE / reference["path"]
    if not path.is_file() or digest(path) != reference.get("sha256"):
        return None, ["pinned full verification failed"]
    payload = read_json(path)
    if payload.get("result") != "PASS":
        errors.append("full verification recorded failure")
    checker = payload.get("checker", {})
    checker_path = PHASE / checker.get("path", "")
    checker_source = PHASE / checker.get("source", "")
    if not checker_path.is_file():
        errors.append("full verification checker binary missing")
    if (
        not checker_source.is_file()
        or digest(checker_source) != checker.get("source_sha256")
        or checker.get("source_sha256") != checker.get("expected_source_sha256")
    ):
        errors.append("full verification checker pin mismatch")
    for item in payload.get("records", []):
        log = PHASE / item["log"]
        output = log.read_text(encoding="utf-8", errors="replace") if log.is_file() else ""
        if (
            not log.is_file()
            or exact_marker_count(output, "s VERIFIED")
            != item.get("verified_marker_count")
            or exact_marker_count(output, "s NOT VERIFIED")
            != item.get("not_verified_marker_count")
        ):
            errors.append(f"full verification log mismatch: id {item.get('id')}")
    bogus = payload.get("bogus_proof_control", {})
    proof = PHASE / bogus.get("proof", "")
    if not proof.is_file() or digest(proof) != bogus.get("proof_sha256"):
        errors.append("full verification bogus proof mismatch")
    log = PHASE / bogus.get("log", "")
    output = log.read_text(encoding="utf-8", errors="replace") if log.is_file() else ""
    if (
        not log.is_file()
        or exact_marker_count(output, "s VERIFIED")
        != bogus.get("verified_marker_count")
        or exact_marker_count(output, "s NOT VERIFIED")
        != bogus.get("not_verified_marker_count")
    ):
        errors.append("full verification bogus log mismatch")
    return {
        "path": reference["path"],
        "result": "PASS" if not errors else "FAIL",
        "mode": "pinned-prior-full-run",
    }, errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--full",
        action="store_true",
        help="rerun drat-trim on every saved trace and test a bogus proof",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=1800,
        help="per-checker-run timeout in seconds for --full",
    )
    args = parser.parse_args()

    manifest_path = PHASE / "manifest.json"
    manifest = read_json(manifest_path)
    full_summary = None
    full_errors: List[str] = []
    if args.full:
        preflight_pins, preflight_pin_errors = dependency_pin_check(manifest)
        full_summary, full_errors = full_checker_check(manifest, args.timeout)
        standalone_path = AUDIT_DIR / "independent_standalone_audit.json"
        standalone = read_json(standalone_path) if standalone_path.is_file() else {}
        manifest["publication_hardening"] = {
            "dependency_pins": {
                "path": "dependency_pins.json",
                "sha256": digest(PHASE / "dependency_pins.json"),
                "result": preflight_pins["result"],
            },
            "standalone_independent_audit": {
                "path": "audits/independent_standalone_audit.json",
                "sha256": digest(standalone_path) if standalone_path.is_file() else None,
                "result": standalone.get("result", "FAIL"),
            },
            "full_verification": {
                "path": "audits/full_validation.json",
                "sha256": digest(AUDIT_DIR / "full_validation.json"),
                "result": full_summary["result"],
            },
        }
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        refresh_immutable_artifacts(manifest)
        manifest = read_json(manifest_path)
        full_errors.extend(preflight_pin_errors)

    hash_entries = {}
    for line in (PHASE / "hashes" / "sha256sums.txt").read_text(
        encoding="ascii"
    ).splitlines():
        expected, relative = line.split("  ", 1)
        hash_entries[relative] = expected

    errors = list(full_errors)
    for relative, expected in hash_entries.items():
        if is_volatile_hash_entry(relative):
            continue
        path = PHASE / relative
        if not path.is_file():
            errors.append(f"missing hashed artifact: {relative}")
        elif digest(path) != expected:
            errors.append(f"hash mismatch: {relative}")

    pins, pin_errors = dependency_pin_check(manifest)
    errors.extend(pin_errors)
    record_summaries = []
    for record in manifest["records"]:
        identifier = record["subgroup_id"]
        for path_key, hash_key in (
            ("cnf", "cnf_sha256"),
            ("proof_cnf", "proof_cnf_sha256"),
            ("proof", "proof_sha256"),
            ("audit", "audit_sha256"),
            ("unit_split_map", "unit_split_map_sha256"),
        ):
            path = PHASE / record[path_key]
            if not path.is_file() or digest(path) != record[hash_key]:
                errors.append(f"id {identifier}: invalid {path_key} hash")
        checker = record["external_check"]
        checker_log = PHASE / checker["checker_log"]
        if not checker["verified"] or "s VERIFIED" not in checker_log.read_text(
            encoding="utf-8", errors="replace"
        ):
            errors.append(f"id {identifier}: checker verdict missing")
        kind = checker.get("verification_kind")
        if kind == "drat_trace_verified" and checker["checker_run"]["returncode"] != 0:
            errors.append(f"id {identifier}: trace checker did not return success")
        if kind == "input_cnf_trivial_unsat":
            obstruction = record.get("direct_pb_upper_bound_certificate", {})
            if not obstruction.get("obstructions"):
                errors.append(f"id {identifier}: missing direct PB obstruction")
            for item in obstruction.get("obstructions", []):
                if item["required_weighted_xor_sum"] <= item["maximum_weighted_xor_sum"]:
                    errors.append(f"id {identifier}: invalid PB upper bound")
        record_summaries.append(
            {
                "id": identifier,
                "evidence": kind,
                "result": "PASS",
            }
        )

    controls = manifest["controls"]
    for length_key in ("length_5", "length_7"):
        control = controls[length_key]
        if (
            control["solver_status"] != "SAT"
            or not control["solver_witness_directly_verified"]
            or not control["known_pair_satisfies_cnf"]
        ):
            errors.append(f"{length_key}: positive control failed")

    header_audit = manifest.get("dimacs_header_audit", {})
    if not header_audit or not all(
        audit["result"] == "PASS" for audit in header_audit.values()
    ):
        errors.append("DIMACS header audit failed or absent")

    rebuild_path = PHASE / "audits" / "independent_rebuild_audit.json"
    if not rebuild_path.is_file():
        errors.append("independent rebuild audit missing")
    else:
        rebuild = json.loads(rebuild_path.read_text(encoding="utf-8"))
        if (
            rebuild.get("result") != "PASS"
            or len(rebuild.get("records", [])) != len(manifest["records"])
            or not all(item.get("result") == "PASS" for item in rebuild.get("records", []))
        ):
            errors.append("independent rebuild audit failed")

    standalone_path = PHASE / "audits" / "independent_standalone_audit.json"
    standalone = {}
    if not standalone_path.is_file():
        errors.append("standalone independent audit missing")
    else:
        standalone = read_json(standalone_path)
        if (
            standalone.get("result") != "PASS"
            or len(standalone.get("records", [])) != len(manifest["records"])
            or not all(item.get("result") == "PASS" for item in standalone.get("records", []))
        ):
            errors.append("standalone independent audit failed")

    if args.full:
        hardening = manifest.get("publication_hardening", {})
        full_reference = hardening.get("full_verification")
        if full_reference:
            _, full_reference_errors = validate_full_validation(full_reference)
            errors.extend(full_reference_errors)
    else:
        hardening = manifest.get("publication_hardening", {})
        for key in ("dependency_pins", "standalone_independent_audit"):
            reference = hardening.get(key)
            if reference:
                path = PHASE / reference["path"]
                if (
                    not path.is_file()
                    or digest(path) != reference.get("sha256")
                    or (
                        key == "standalone_independent_audit"
                        and read_json(path).get("result") != "PASS"
                    )
                ):
                    errors.append(f"pinned {key} failed")
        full_reference = hardening.get("full_verification")
        if full_reference:
            full_summary, full_reference_errors = validate_full_validation(full_reference)
            errors.extend(full_reference_errors)

    result = {
        "hash_entries_checked": len(hash_entries),
        "record_checks": record_summaries,
        "positive_controls": ["length_5", "length_7"],
        "dimacs_files_checked": len(header_audit),
        "independent_rebuild_checked": rebuild_path.is_file(),
        "dependency_pins": pins,
        "standalone_independent_audit_checked": standalone_path.is_file(),
        "full_verification": full_summary,
        "result": "PASS" if not errors else "FAIL",
        "errors": errors,
    }
    output = AUDIT_DIR / "final_validation.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
