#!/usr/bin/env python3
import argparse
import hashlib
import json
import time

from ortools import __version__ as ortools_version
from ortools.sat.python import cp_model


def aperiodic(sequence, lag):
    return sum(
        sequence[index] * sequence[index + lag]
        for index in range(len(sequence) - lag)
    )


def xor_variable(model, left, right, name):
    result = model.new_bool_var(name)
    model.add_bool_xor([left, right, result.Not()])
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("sequences_json")
    parser.add_argument("output_json")
    parser.add_argument("--seconds", type=float, default=1800)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()

    with open(args.sequences_json, encoding="ascii") as handle:
        full = json.load(handle)["sequences"]
    s, _, sq, _ = full
    base = [s[:84], s[84:], sq[:84], sq[84:]]
    assert list(map(sum, base)) == [-2, 3, 0, -1]

    model = cp_model.CpModel()
    flips = [model.new_bool_var(f"flip_{index}") for index in range(84)]
    for index, value in enumerate(base[0]):
        if value == -1:
            model.add(flips[index] == 0)
    model.add(sum(flips) == 8)

    xor_count = 0
    for lag in range(1, 84):
        original_total = sum(
            aperiodic(sequence, lag)
            for sequence in base
            if lag < len(sequence)
        )
        weighted_changes = []
        for index in range(84 - lag):
            left = flips[index]
            right = flips[index + lag]
            if base[0][index] == -1:
                left = None
            if base[0][index + lag] == -1:
                right = None
            if left is None and right is None:
                continue
            if left is None:
                disagreement = right
            elif right is None:
                disagreement = left
            else:
                disagreement = xor_variable(
                    model, left, right, f"xor_{lag}_{index}"
                )
                xor_count += 1
            weight = base[0][index] * base[0][index + lag]
            weighted_changes.append(weight * disagreement)
        assert original_total % 2 == 0
        model.add(sum(weighted_changes) == original_total // 2)

    model_path = args.output_json.rsplit(".", 1)[0] + ".model.txt"
    model.export_to_file(model_path)
    with open(model_path, "rb") as handle:
        model_sha256 = hashlib.sha256(handle.read()).hexdigest()

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = args.seconds
    solver.parameters.num_search_workers = args.workers
    solver.parameters.log_search_progress = True
    start = time.monotonic()
    status = solver.solve(model)
    elapsed = time.monotonic() - start

    result = {
        "solver": f"OR-Tools CP-SAT {ortools_version}",
        "status": solver.status_name(status),
        "elapsed_seconds": elapsed,
        "workers": args.workers,
        "time_limit_seconds": args.seconds,
        "primary_flip_variables": 84,
        "eligible_plus_positions": sum(value == 1 for value in base[0]),
        "required_flips": 8,
        "xor_auxiliaries": xor_count,
        "constraints": "all 83 exact aperiodic complementary equations",
        "source_row_sums": list(map(sum, base)),
        "required_row_sums": [-18, 3, 0, -1],
        "model_sha256": model_sha256,
        "solver_stats": solver.response_stats(),
    }
    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        changed = [bool(solver.value(variable)) for variable in flips]
        candidate = [
            -value if changed[index] else value
            for index, value in enumerate(base[0])
        ]
        candidate_base = [candidate] + base[1:]
        correlations = [
            sum(
                aperiodic(sequence, lag)
                for sequence in candidate_base
                if lag < len(sequence)
            )
            for lag in range(1, 84)
        ]
        assert not any(correlations)
        result["flipped_positions_zero_based"] = [
            index for index, value in enumerate(changed) if value
        ]
        result["candidate_base_sequences"] = candidate_base

    with open(args.output_json, "w", encoding="ascii") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
