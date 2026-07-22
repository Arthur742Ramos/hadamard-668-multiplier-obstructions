#!/usr/bin/env python3
import argparse
import json
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Verify four reduced Goethals-Seidel sequences exactly."
    )
    parser.add_argument("json_path")
    parser.add_argument("--key", default="best_state")
    args = parser.parse_args()

    with open(args.json_path, encoding="utf-8") as handle:
        document = json.load(handle)
    sequences = document[args.key]
    if len(sequences) != 4:
        raise ValueError(f"expected 4 sequences, found {len(sequences)}")
    n = len(sequences[0])
    if n != 167 or any(len(sequence) != n for sequence in sequences):
        raise ValueError("expected four sequences of length 167")
    if any(
        type(value) is not int or value not in {-1, 1}
        for sequence in sequences
        for value in sequence
    ):
        raise ValueError("all sequence entries must be -1 or 1")

    combined_paf = []
    for shift in range(1, n):
        combined_paf.append(
            sum(
                sum(
                    sequence[index] * sequence[(index + shift) % n]
                    for index in range(n)
                )
                for sequence in sequences
            )
        )
    violations = [
        {"shift": shift, "combined_paf": value}
        for shift, value in enumerate(combined_paf, start=1)
        if value != 0
    ]
    result = {
        "valid_goethals_seidel_quadruple": not violations,
        "length": n,
        "row_sums": [sum(sequence) for sequence in sequences],
        "periodic_score": sum(value * value for value in combined_paf),
        "max_abs_combined_paf": max(map(abs, combined_paf)),
        "violating_shifts": len(violations),
        "first_violations": violations[:20],
        "arithmetic": "exact integer periodic autocorrelation",
    }
    print(json.dumps(result, indent=2))
    return 0 if result["valid_goethals_seidel_quadruple"] else 1


if __name__ == "__main__":
    sys.exit(main())
