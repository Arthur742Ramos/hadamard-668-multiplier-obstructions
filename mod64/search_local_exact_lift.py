#!/usr/bin/env python3
import argparse
import hashlib
import itertools
import json
import os
import time

import z3


def exact_dc_profiles(current_sums):
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
        distance = sum(
            abs(target - current) // 2
            for target, current in zip(profile, current_sums)
        )
        profiles.append((distance, profile))
    return sorted(profiles)


def bool_count(variables):
    return z3.Sum([z3.If(variable, 1, 0) for variable in variables])


def new_sign(original, flip):
    return original * z3.If(flip, -1, 1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("sequences_json")
    parser.add_argument("output_dir")
    parser.add_argument("--max-radius", type=int, default=8)
    parser.add_argument("--timeout-ms", type=int, default=300000)
    parser.add_argument("--proof", action="store_true")
    args = parser.parse_args()

    if args.proof:
        z3.set_param(proof=True)

    with open(args.sequences_json, encoding="ascii") as handle:
        full = json.load(handle)["sequences"]
    s, _, sq, _ = full
    sequences = [s[:84], s[84:], sq[:84], sq[84:]]
    lengths = list(map(len, sequences))
    assert lengths == [84, 83, 84, 83]
    current_sums = list(map(sum, sequences))
    assert current_sums == [-2, 3, 0, -1]

    flips = [
        [z3.Bool(f"f_{sequence_index}_{index}") for index in range(length)]
        for sequence_index, length in enumerate(lengths)
    ]
    all_flips = [variable for sequence in flips for variable in sequence]
    row_sum_expressions = [
        z3.Sum(
            [
                new_sign(original, flip)
                for original, flip in zip(sequence, sequence_flips)
            ]
        )
        for sequence, sequence_flips in zip(sequences, flips)
    ]

    solver = z3.Solver()
    solver.set(timeout=args.timeout_ms)
    for lag in range(1, 84):
        terms = []
        for sequence, sequence_flips in zip(sequences, flips):
            for index in range(len(sequence) - lag):
                weight = sequence[index] * sequence[index + lag]
                changed = z3.Xor(
                    sequence_flips[index], sequence_flips[index + lag]
                )
                terms.append(weight * z3.If(changed, -1, 1))
        solver.add(z3.Sum(terms) == 0)

    profiles = exact_dc_profiles(current_sums)
    os.makedirs(args.output_dir, exist_ok=True)
    results = []
    for radius in range(0, args.max_radius + 1):
        eligible_profiles = [
            profile for distance, profile in profiles if distance <= radius
        ]
        if not eligible_profiles:
            results.append(
                {
                    "radius": radius,
                    "status": "UNSAT_BY_DC",
                    "eligible_dc_profiles": 0,
                }
            )
            continue

        solver.push()
        solver.add(bool_count(all_flips) <= radius)
        solver.add(
            z3.Or(
                [
                    z3.And(
                        [
                            expression == target
                            for expression, target in zip(
                                row_sum_expressions, profile
                            )
                        ]
                    )
                    for profile in eligible_profiles
                ]
            )
        )
        smt2 = solver.to_smt2()
        smt2_path = os.path.join(args.output_dir, f"radius_{radius}.smt2")
        with open(smt2_path, "w", encoding="ascii") as handle:
            handle.write(smt2)
        start = time.monotonic()
        status = solver.check()
        elapsed = time.monotonic() - start
        result = {
            "radius": radius,
            "status": str(status).upper(),
            "eligible_dc_profiles": len(eligible_profiles),
            "elapsed_seconds": elapsed,
            "smt2_sha256": hashlib.sha256(smt2.encode("ascii")).hexdigest(),
        }
        if status == z3.sat:
            model = solver.model()
            changed = [
                [z3.is_true(model.evaluate(variable)) for variable in row]
                for row in flips
            ]
            candidate = [
                [
                    -value if flip else value
                    for value, flip in zip(sequence, sequence_changes)
                ]
                for sequence, sequence_changes in zip(sequences, changed)
            ]
            result["flip_count"] = sum(map(sum, changed))
            result["row_sums"] = list(map(sum, candidate))
            result["candidate_base_sequences"] = candidate
        elif status == z3.unknown:
            result["reason_unknown"] = solver.reason_unknown()
        elif args.proof:
            proof = solver.proof().sexpr()
            proof_path = os.path.join(
                args.output_dir, f"radius_{radius}.proof.sexpr"
            )
            with open(proof_path, "w", encoding="ascii") as handle:
                handle.write(proof)
            result["proof_sha256"] = hashlib.sha256(
                proof.encode("ascii")
            ).hexdigest()
        results.append(result)
        solver.pop()
        if status == z3.unknown or status == z3.sat:
            break

    output = {
        "solver": f"Z3 {z3.get_version_string()}",
        "source_lengths": lengths,
        "source_row_sums": current_sums,
        "constraints": "all 83 exact aperiodic complementary equations",
        "results": results,
    }
    output_path = os.path.join(args.output_dir, "results.json")
    with open(output_path, "w", encoding="ascii") as handle:
        json.dump(output, handle, indent=2)
        handle.write("\n")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
