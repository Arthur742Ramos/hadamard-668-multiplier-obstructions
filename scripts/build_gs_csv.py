#!/usr/bin/env python3
import argparse
import csv
import json


def circulant(sequence):
    n = len(sequence)
    return [
        [sequence[(column - row) % n] for column in range(n)]
        for row in range(n)
    ]


def transpose(matrix):
    return [list(column) for column in zip(*matrix)]


def times_reversal(matrix):
    return [list(reversed(row)) for row in matrix]


def negate(matrix):
    return [[-value for value in row] for row in matrix]


def assemble_block_row(blocks):
    return [
        [value for block in blocks for value in block[row]]
        for row in range(len(blocks[0]))
    ]


def combined_paf(sequences, shift):
    n = len(sequences[0])
    return sum(
        sum(
            sequence[index] * sequence[(index + shift) % n]
            for index in range(n)
        )
        for sequence in sequences
    )


def main():
    parser = argparse.ArgumentParser(
        description="Build a Goethals-Seidel matrix from four exact sequences."
    )
    parser.add_argument("json_path")
    parser.add_argument("csv_path")
    parser.add_argument("--key", default="best_state")
    parser.add_argument("--allow-invalid", action="store_true")
    args = parser.parse_args()

    with open(args.json_path, encoding="utf-8") as handle:
        sequences = json.load(handle)[args.key]
    if len(sequences) != 4:
        raise ValueError("expected four sequences")
    n = len(sequences[0])
    if any(len(sequence) != n for sequence in sequences):
        raise ValueError("sequence lengths differ")
    if any(
        type(value) is not int or value not in {-1, 1}
        for sequence in sequences
        for value in sequence
    ):
        raise ValueError("sequence entries must be -1 or 1")

    violations = []
    for shift in range(1, n):
        value = combined_paf(sequences, shift)
        if value != 0:
            violations.append((shift, value))
    if violations and not args.allow_invalid:
        raise ValueError(f"reduced GS condition fails: {violations[:8]}")

    a, b, c, d = map(circulant, sequences)
    br, cr, dr = map(times_reversal, (b, c, d))
    btr, ctr, dtr = map(
        times_reversal, (transpose(b), transpose(c), transpose(d))
    )
    block_rows = [
        [a, br, cr, dr],
        [negate(br), a, negate(dtr), ctr],
        [negate(cr), dtr, a, negate(btr)],
        [negate(dr), negate(ctr), btr, a],
    ]
    matrix = [
        row
        for blocks in block_rows
        for row in assemble_block_row(blocks)
    ]
    with open(args.csv_path, "w", newline="", encoding="ascii") as handle:
        csv.writer(handle, lineterminator="\n").writerows(matrix)


if __name__ == "__main__":
    main()
