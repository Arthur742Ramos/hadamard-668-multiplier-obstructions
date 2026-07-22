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
    parser.add_argument("--lags", required=True)
    parser.add_argument("--seconds", type=float, default=300)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()

    if args.lags == "all":
        lags = list(range(1, 84))
    else:
        lags = sorted({int(value) for value in args.lags.split(",")})
    if not lags or min(lags) < 1 or max(lags) > 83:
        raise ValueError("lags must lie in 1..83")

    with open(args.sequences_json, encoding="ascii") as handle:
        full = json.load(handle)["sequences"]
    s, _, sq, _ = full
    base = [s[:84], s[84:], sq[:84], sq[84:]]
    assert list(map(len, base)) == [84, 83, 84, 83]

    model = cp_model.CpModel()
    flips = [
        [
            model.new_bool_var(f"flip_{sequence_index}_{index}")
            for index in range(len(sequence))
        ]
        for sequence_index, sequence in enumerate(base)
    ]
    xor_count = 0
    original_correlations = {}
    for lag in lags:
        original_total = sum(
            aperiodic(sequence, lag)
            for sequence in base
            if lag < len(sequence)
        )
        original_correlations[lag] = original_total
        weighted_changes = []
        for sequence_index, sequence in enumerate(base):
            for index in range(len(sequence) - lag):
                disagreement = xor_variable(
                    model,
                    flips[sequence_index][index],
                    flips[sequence_index][index + lag],
                    f"xor_{lag}_{sequence_index}_{index}",
                )
                xor_count += 1
                weight = sequence[index] * sequence[index + lag]
                weighted_changes.append(weight * disagreement)
        assert original_total % 2 == 0
        model.add(sum(weighted_changes) == original_total // 2)

    all_flips = [variable for sequence in flips for variable in sequence]
    model.minimize(sum(all_flips))
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
        "lags": lags,
        "original_combined_aperiodic_correlations": original_correlations,
        "primary_flip_variables": len(all_flips),
        "xor_auxiliaries": xor_count,
        "objective_value": (
            solver.objective_value
            if status in (cp_model.FEASIBLE, cp_model.OPTIMAL)
            else None
        ),
        "best_objective_bound": solver.best_objective_bound,
        "model_sha256": model_sha256,
        "solver_stats": solver.response_stats(),
    }
    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        result["flipped_positions_zero_based"] = [
            [index for index, variable in enumerate(sequence) if solver.value(variable)]
            for sequence in flips
        ]
    with open(args.output_json, "w", encoding="ascii") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
