#!/usr/bin/env python3
import argparse
import csv
import json
import sys


def fail(message):
    print(json.dumps({"valid": False, "error": message}, indent=2))
    return 1


def main():
    parser = argparse.ArgumentParser(
        description="Verify a {-1,+1} Hadamard CSV using exact integer arithmetic."
    )
    parser.add_argument("csv_path")
    parser.add_argument("--order", type=int, default=668)
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
                            f"entry ({row_number},{column_number}) is "
                            f"{raw_value!r}; expected -1 or 1"
                        )
                    if value == "1":
                        bits |= 1 << (column_number - 1)
                rows.append(bits)
    except (OSError, UnicodeError, csv.Error) as error:
        return fail(str(error))

    if len(rows) != args.order:
        return fail(f"found {len(rows)} rows; expected {args.order}")

    violations = []
    max_abs_inner_product = 0
    checked_pairs = 0
    for i, left in enumerate(rows):
        diagonal = args.order - 2 * (left ^ left).bit_count()
        if diagonal != args.order:
            return fail(f"diagonal Gram entry ({i + 1},{i + 1}) is {diagonal}")
        for j in range(i):
            inner_product = args.order - 2 * (left ^ rows[j]).bit_count()
            checked_pairs += 1
            max_abs_inner_product = max(
                max_abs_inner_product, abs(inner_product)
            )
            if inner_product != 0 and len(violations) < 20:
                violations.append(
                    {
                        "row_i": j + 1,
                        "row_j": i + 1,
                        "inner_product": inner_product,
                    }
                )

    result = {
        "valid": not violations,
        "order": args.order,
        "rows": len(rows),
        "entries_per_row": args.order,
        "checked_off_diagonal_pairs": checked_pairs,
        "max_abs_off_diagonal_inner_product": max_abs_inner_product,
        "arithmetic": "exact integer bit counts",
    }
    if violations:
        result["first_violations"] = violations
    print(json.dumps(result, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
