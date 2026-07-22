#!/usr/bin/env python3
import argparse
import hashlib
import itertools
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


def exact_dc_profiles(current_sums, flip_count):
    ranges = [
        range(-84, 85, 2),
        range(-83, 84, 2),
        range(-84, 85, 2),
        range(-83, 84, 2),
    ]
    profiles = []
    for profile in itertools.product(*ranges):
        if sum(value * value for value in profile) != 334:
            continue
        minimum_flips = sum(
            abs(target - current) // 2
            for target, current in zip(profile, current_sums)
        )
        if minimum_flips <= flip_count and (flip_count - minimum_flips) % 2 == 0:
            profiles.append(profile)
    return profiles


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("sequences_json")
    parser.add_argument("output_json")
    parser.add_argument("--seconds", type=float, default=1800)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--lags", default="all")
    args = parser.parse_args()
    lags = (
        list(range(1, 84))
        if args.lags == "all"
        else sorted({int(value) for value in args.lags.split(",")})
    )

    with open(args.sequences_json, encoding="ascii") as handle:
        full = json.load(handle)["sequences"]
    s, _, sq, _ = full
    base = [s[:84], s[84:], sq[:84], sq[84:]]
    current_sums = list(map(sum, base))
    assert current_sums == [-2, 3, 0, -1]

    model = cp_model.CpModel()
    flips = [
        [
            model.new_bool_var(f"flip_{sequence_index}_{index}")
            for index in range(len(sequence))
        ]
        for sequence_index, sequence in enumerate(base)
    ]

    eligible_count = 0
    for sequence_index, sequence in enumerate(base):
        for index in range(len(sequence)):
            neighbors = [
                neighbor
                for neighbor in (index - 4, index + 4)
                if 0 <= neighbor < len(sequence)
            ]
            eligible = (
                len(neighbors) == 2
                and all(sequence[index] * sequence[neighbor] == -1 for neighbor in neighbors)
            )
            if eligible:
                eligible_count += 1
            else:
                model.add(flips[sequence_index][index] == 0)
        for index in range(len(sequence) - 4):
            model.add(
                flips[sequence_index][index]
                + flips[sequence_index][index + 4]
                <= 1
            )

    all_flips = [variable for sequence in flips for variable in sequence]
    model.add(sum(all_flips) == 64)

    xor_count = 0
    for lag in lags:
        original_total = sum(
            aperiodic(sequence, lag)
            for sequence in base
            if lag < len(sequence)
        )
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
                weighted_changes.append(
                    sequence[index] * sequence[index + lag] * disagreement
                )
        model.add(sum(weighted_changes) == original_total // 2)

    profiles = exact_dc_profiles(current_sums, 64)
    row_sum_expressions = [
        sum(
            value * (1 - 2 * flip)
            for value, flip in zip(sequence, sequence_flips)
        )
        for sequence, sequence_flips in zip(base, flips)
    ]
    selectors = []
    for profile_index, profile in enumerate(profiles):
        selected = model.new_bool_var(f"profile_{profile_index}")
        selectors.append(selected)
        for expression, target in zip(row_sum_expressions, profile):
            model.add(expression == target).only_enforce_if(selected)
    model.add_exactly_one(selectors)

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
        "distance": 64,
        "tight_lag4_conditions": {
            "eligible_vertices": eligible_count,
            "all_flips_have_two_negative_lag4_edges": True,
            "no_two_flips_are_lag4_adjacent": True,
        },
        "eligible_dc_profiles": len(profiles),
        "xor_auxiliaries": xor_count,
        "model_sha256": model_sha256,
        "solver_stats": solver.response_stats(),
    }
    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        changed = [
            [bool(solver.value(variable)) for variable in sequence]
            for sequence in flips
        ]
        candidate = [
            [
                -value if change else value
                for value, change in zip(sequence, changes)
            ]
            for sequence, changes in zip(base, changed)
        ]
        result["row_sums"] = list(map(sum, candidate))
        result["flipped_positions_zero_based"] = [
            [index for index, value in enumerate(changes) if value]
            for changes in changed
        ]
        result["candidate_base_sequences"] = candidate
    with open(args.output_json, "w", encoding="ascii") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
