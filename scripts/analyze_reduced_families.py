#!/usr/bin/env python3
import argparse
import itertools
import json
import math


def sum_of_squares(target, count):
    values = range(math.isqrt(target) + 1)
    return [
        terms
        for terms in itertools.combinations_with_replacement(values, count)
        if sum(value * value for value in terms) == target
    ]


def multiplicative_order(value, modulus):
    current = value % modulus
    order = 1
    while current != 1:
        current = current * value % modulus
        order += 1
    return order


def multiplier_orbits(modulus, multiplier):
    unseen = set(range(modulus))
    orbits = []
    while unseen:
        start = min(unseen)
        orbit = []
        value = start
        while value not in orbit:
            orbit.append(value)
            value = value * multiplier % modulus
        unseen.difference_update(orbit)
        orbits.append(sorted(orbit))
    return sorted(orbits, key=lambda orbit: (len(orbit), min(orbit)))


def difference_counts(block, modulus):
    counts = [0] * modulus
    for left in block:
        for right in block:
            if left != right:
                counts[(left - right) % modulus] += 1
    return counts


def four_odd_square_signatures():
    signatures = set()
    odds = range(1, math.isqrt(668) + 1, 2)
    for terms in itertools.combinations_with_replacement(odds, 4):
        if sum(value * value for value in terms) == 668:
            signatures.add(tuple(sorted(terms, reverse=True)))
    return sorted(signatures, reverse=True)


def legendre_macro_cases():
    psd_values = set()
    triples = 0
    for u in range(-111, 112, 2):
        for v in range(-111, 112, 2):
            w = 1 - u - v
            if w < -111 or w > 111 or w % 2 == 0:
                continue
            triples += 1
            psd = u * u + v * v + w * w - u * v - v * w - w * u
            if psd <= 668:
                psd_values.add(psd)
    cases = sorted(
        {
            tuple(sorted((left, 668 - left)))
            for left in psd_values
            if 668 - left in psd_values
        }
    )
    return triples, cases


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    args = parser.parse_args()

    signatures = four_odd_square_signatures()
    assert len(signatures) == 10
    sds_parameters = []
    for signature in signatures:
        sizes = tuple((167 - row_sum) // 2 for row_sum in signature)
        lam = sum(sizes) - 167
        assert sum(size * (size - 1) for size in sizes) == 166 * lam
        sds_parameters.append(
            {
                "row_sums": signature,
                "block_sizes": sizes,
                "lambda": lam,
            }
        )

    v, k, lam, multiplier = 667, 333, 166, 167
    assert math.gcd(multiplier, v) == 1
    assert math.gcd(multiplier - 1, v) == 1
    orbits = multiplier_orbits(v, multiplier)
    assert [len(orbit) for orbit in orbits] == [1, 11, 11, 14, 14, 154, 154, 154, 154]
    fixed_candidates = []
    for mask in range(1 << len(orbits)):
        chosen = [
            index for index in range(len(orbits)) if mask & (1 << index)
        ]
        if sum(len(orbits[index]) for index in chosen) != k:
            continue
        block = set().union(*(set(orbits[index]) for index in chosen))
        counts = difference_counts(block, v)
        nonzero_counts = counts[1:]
        failing_shift = next(
            shift for shift in range(1, v) if counts[shift] != lam
        )
        fixed_candidates.append(
            {
                "orbit_indices": chosen,
                "orbit_representatives": [min(orbits[index]) for index in chosen],
                "minimum_difference_count": min(nonzero_counts),
                "maximum_difference_count": max(nonzero_counts),
                "first_failing_shift": failing_shift,
                "count_at_first_failing_shift": counts[failing_shift],
                "squared_error": sum((count - lam) ** 2 for count in nonzero_counts),
            }
        )
    assert len(fixed_candidates) == 24
    assert all(
        candidate["squared_error"] > 0 for candidate in fixed_candidates
    )

    residues = {pow(value, 2, 167) for value in range(1, 167)}
    nonresidues = set(range(1, 167)) - residues
    qr_orbits = [{0}, residues, nonresidues]
    qr_invariant_sizes = sorted(
        {
            sum(len(qr_orbits[index]) for index in range(3) if mask & (1 << index))
            for mask in range(8)
        }
    )
    admissible_sizes = {
        size
        for parameters in sds_parameters
        for size in parameters["block_sizes"]
    }
    assert set(qr_invariant_sizes) & admissible_sizes == {83}
    assert (83, 83, 83, 83) not in {
        tuple(parameters["block_sizes"]) for parameters in sds_parameters
    }

    triples, macro_cases = legendre_macro_cases()
    assert macro_cases == [
        (16, 652),
        (64, 604),
        (76, 592),
        (112, 556),
        (172, 496),
        (256, 412),
        (268, 400),
        (304, 364),
    ]
    units_333 = [value for value in range(333) if math.gcd(value, 333) == 1]
    kernel_mod_3 = [value for value in units_333 if value % 3 == 1]
    assert len(units_333) == 216
    assert len(kernel_mod_3) == 108
    assert not sum_of_squares(167, 2)

    report = {
        "order": 668,
        "two_square_representations": sum_of_squares(668, 2),
        "three_square_representations": sum_of_squares(668, 3),
        "four_odd_square_signatures": signatures,
        "sds_parameter_sets": sds_parameters,
        "cyclic_difference_set_667": {
            "parameters": [v, k, lam],
            "first_multiplier": multiplier,
            "multiplier_order": multiplicative_order(multiplier, v),
            "translation_normalization_gcd": math.gcd(multiplier - 1, v),
            "orbit_sizes": [len(orbit) for orbit in orbits],
            "orbit_representatives": [min(orbit) for orbit in orbits],
            "fixed_orbit_unions_of_size_333": len(fixed_candidates),
            "valid_difference_sets": 0,
            "candidate_certificates": fixed_candidates,
        },
        "qr_invariant_gs_sds_167": {
            "qr_orbit_sizes": [len(orbit) for orbit in qr_orbits],
            "possible_block_sizes": qr_invariant_sizes,
            "intersection_with_admissible_block_sizes": [83],
            "all_four_blocks_qr_invariant_possible": False,
        },
        "legendre_pair_333": {
            "mod_3_compression_triples_checked": triples,
            "frequency_111_macro_cases": macro_cases,
            "units_mod_333": len(units_333),
            "kernel_of_reduction_mod_3": len(kernel_mod_3),
            "167_as_sum_of_two_squares": [],
            "nine_compression_parseval_total": (2 + 8 * 668) // 9,
            "thirty_seven_compression_parseval_total": (2 + 36 * 668) // 37,
        },
    }
    payload = json.dumps(report, indent=2)
    print(payload)
    if args.output:
        with open(args.output, "w", encoding="ascii") as handle:
            handle.write(payload + "\n")


if __name__ == "__main__":
    main()
