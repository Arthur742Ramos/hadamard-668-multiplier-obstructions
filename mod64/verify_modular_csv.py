#!/usr/bin/env python3
import argparse
import csv
import json
import sys
from collections import Counter


def fail(message):
    print(json.dumps({"valid": False, "error": message}, indent=2))
    return 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path")
    parser.add_argument("--order", type=int, default=668)
    parser.add_argument("--modulus", type=int, default=64)
    args = parser.parse_args()

    rows = []
    try:
        with open(args.csv_path, newline="", encoding="ascii") as handle:
            for row_number, raw_row in enumerate(csv.reader(handle), start=1):
                if len(raw_row) != args.order:
                    return fail(
                        f"row {row_number} has {len(raw_row)} entries; "
                        f"expected {args.order}"
                    )
                bits = 0
                for column_number, raw_value in enumerate(raw_row, start=1):
                    value = raw_value.strip()
                    if value not in {"-1", "1"}:
                        return fail(
                            f"entry ({row_number},{column_number}) is invalid"
                        )
                    if value == "1":
                        bits |= 1 << (column_number - 1)
                rows.append(bits)
    except (OSError, UnicodeError, csv.Error) as error:
        return fail(str(error))

    if len(rows) != args.order:
        return fail(f"found {len(rows)} rows; expected {args.order}")

    exact_nonzero = Counter()
    modular_violations = []
    for i, left in enumerate(rows):
        for j in range(i):
            inner_product = args.order - 2 * (left ^ rows[j]).bit_count()
            if inner_product:
                exact_nonzero[inner_product] += 1
            if inner_product % args.modulus:
                modular_violations.append((j + 1, i + 1, inner_product))

    result = {
        "valid_modular_hadamard": not modular_violations,
        "valid_exact_hadamard": not exact_nonzero,
        "order": args.order,
        "modulus": args.modulus,
        "checked_off_diagonal_pairs": args.order * (args.order - 1) // 2,
        "exact_nonzero_off_diagonal_pairs": sum(exact_nonzero.values()),
        "exact_inner_product_histogram": {
            str(key): exact_nonzero[key] for key in sorted(exact_nonzero)
        },
        "first_modular_violations": modular_violations[:20],
        "arithmetic": "exact integer bit counts",
    }
    print(json.dumps(result, indent=2))
    return 0 if result["valid_modular_hadamard"] else 1


if __name__ == "__main__":
    sys.exit(main())
