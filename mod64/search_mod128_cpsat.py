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
    parser.add_argument("--fixed-flips", type=int)
    parser.add_argument("--lag58-target", type=int, choices=(-64, 0))
    args = parser.parse_args()

    with open(args.sequences_json, encoding="ascii") as handle:
        full = json.load(handle)["sequences"]
    s, _, sq, _ = full
    base = [s[:84], s[84:], sq[:84], sq[84:]]

    model = cp_model.CpModel()
    flips = [
        [
            model.new_bool_var(f"flip_{sequence_index}_{index}")
            for index in range(len(sequence))
        ]
        for sequence_index, sequence in enumerate(base)
    ]
    xor_count = 0
    quotients = []
    new_correlation_expressions = {}
    for lag in range(1, 84):
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
        maximum = sum(
            len(sequence) - lag for sequence in base if lag < len(sequence)
        )
        quotient = model.new_int_var(
            -(maximum // 64 + 1),
            maximum // 64 + 1,
            f"quotient_{lag}",
        )
        quotients.append(quotient)
        new_correlation = original_total - 2 * sum(weighted_changes)
        new_correlation_expressions[lag] = new_correlation
        model.add(new_correlation == 64 * quotient)

    all_flips = [variable for sequence in flips for variable in sequence]
    if args.fixed_flips is None:
        model.minimize(sum(all_flips))
    else:
        model.add(sum(all_flips) == args.fixed_flips)
    if args.lag58_target is not None:
        if args.fixed_flips != 16:
            raise ValueError("the tight lag-58 branch requires --fixed-flips 16")
        desired_weight = -1 if args.lag58_target == 0 else 1
        for sequence_index, sequence in enumerate(base):
            paired = set()
            for index in range(len(sequence) - 58):
                left, right = index, index + 58
                paired.update((left, right))
                if sequence[left] * sequence[right] != desired_weight:
                    model.add(flips[sequence_index][left] == 0)
                    model.add(flips[sequence_index][right] == 0)
                else:
                    model.add(
                        flips[sequence_index][left]
                        + flips[sequence_index][right]
                        <= 1
                    )
            for index in set(range(len(sequence))) - paired:
                model.add(flips[sequence_index][index] == 0)
        model.add(new_correlation_expressions[58] == args.lag58_target)
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
        "target": "128-modular GS from special-form base sequences",
        "base_aperiodic_target": "0 modulo 64 at every lag 1..83",
        "primary_flip_variables": len(all_flips),
        "xor_auxiliaries": xor_count,
        "objective_value": (
            solver.objective_value
            if args.fixed_flips is None
            and status in (cp_model.FEASIBLE, cp_model.OPTIMAL)
            else None
        ),
        "best_objective_bound": solver.best_objective_bound,
        "fixed_flips": args.fixed_flips,
        "lag58_target": args.lag58_target,
        "model_sha256": model_sha256,
        "solver_stats": solver.response_stats(),
    }
    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        changed = [
            [bool(solver.value(variable)) for variable in sequence]
            for sequence in flips
        ]
        candidate_base = [
            [
                -value if change else value
                for value, change in zip(sequence, changes)
            ]
            for sequence, changes in zip(base, changed)
        ]
        correlations = [
            sum(
                aperiodic(sequence, lag)
                for sequence in candidate_base
                if lag < len(sequence)
            )
            for lag in range(1, 84)
        ]
        assert all(value % 64 == 0 for value in correlations)
        candidate_s = candidate_base[0] + candidate_base[1]
        candidate_sq = candidate_base[2] + candidate_base[3]
        candidate_q = [
            left * right for left, right in zip(candidate_s, candidate_sq)
        ]
        candidate_s_prime = candidate_s[:84] + [
            -value for value in candidate_s[84:]
        ]
        candidate_sq_prime = candidate_sq[:84] + [
            -value for value in candidate_sq[84:]
        ]
        result["flip_count"] = sum(map(sum, changed))
        result["row_sums"] = list(map(sum, candidate_base))
        result["base_aperiodic_correlations"] = correlations
        result["candidate_base_sequences"] = candidate_base
        result["candidate_full_sequences"] = [
            candidate_s,
            candidate_s_prime,
            candidate_sq,
            candidate_sq_prime,
        ]
        result["candidate_q"] = candidate_q

    with open(args.output_json, "w", encoding="ascii") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
