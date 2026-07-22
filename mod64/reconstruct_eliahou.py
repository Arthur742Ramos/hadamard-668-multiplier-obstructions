#!/usr/bin/env python3
import argparse
import itertools
import json


def expand_runs(runs):
    sequence = []
    sign = 1
    for length in runs:
        sequence.extend([sign] * length)
        sign = -sign
    return sequence


def aperiodic(sequence, lag):
    return sum(
        sequence[index] * sequence[index + lag]
        for index in range(len(sequence) - lag)
    )


def periodic(sequence, shift):
    n = len(sequence)
    return sum(
        sequence[index] * sequence[(index + shift) % n]
        for index in range(n)
    )


def target_row_sum_profiles(current_sums):
    profiles = []
    bounds = [84, 83, 84, 83]
    ranges = [
        range(-84, 85, 2),
        range(-83, 84, 2),
        range(-84, 85, 2),
        range(-83, 84, 2),
    ]
    for profile in itertools.product(*ranges):
        if sum(value * value for value in profile) != 334:
            continue
        distance = sum(
            abs(target - current) // 2
            for target, current in zip(profile, current_sums)
        )
        assert all(abs(value) <= bound for value, bound in zip(profile, bounds))
        profiles.append((distance, profile))
    profiles.sort()
    return profiles


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--certificate")
    parser.add_argument("--sequences")
    args = parser.parse_args()

    s_runs = (
        [4] * 5
        + [2, 1, 1] * 5
        + [1, 5]
        + [4] * 4
        + [2, 1, 1] * 6
        + [4] * 4
        + [3]
        + [1, 2, 1] * 5
        + [3]
        + [4] * 4
        + [3]
        + [1, 2, 1] * 5
    )
    q_runs = [83, 2, 81, 1]
    s = expand_runs(s_runs)
    q = expand_runs(q_runs)
    assert len(s) == len(q) == 167

    s_prime = s[:84] + [-value for value in s[84:]]
    sq = [left * right for left, right in zip(s, q)]
    sq_prime = sq[:84] + [-value for value in sq[84:]]
    quadruple = [s, s_prime, sq, sq_prime]

    x, y, z, w = s[:84], s[84:], sq[:84], sq[84:]
    base_sequences = [x, y, z, w]
    full_aperiodic = [
        sum(aperiodic(sequence, lag) for sequence in quadruple)
        for lag in range(1, 167)
    ]
    base_aperiodic = [
        sum(
            aperiodic(sequence, lag)
            for sequence in base_sequences
            if lag < len(sequence)
        )
        for lag in range(1, 84)
    ]
    assert all(
        full_aperiodic[lag - 1] == 2 * base_aperiodic[lag - 1]
        for lag in range(1, 84)
    )
    assert all(value == 0 for value in full_aperiodic[83:])

    expected_defects = {
        4: -512,
        8: 384,
        12: -256,
        16: 128,
        26: -64,
        30: 128,
        34: -192,
        38: 256,
        42: -320,
        46: 256,
        50: -192,
        54: 128,
        58: -64,
    }
    observed_defects = {
        lag: value
        for lag, value in enumerate(full_aperiodic, start=1)
        if value != 0
    }
    assert observed_defects == expected_defects

    combined_paf = [
        sum(periodic(sequence, shift) for sequence in quadruple)
        for shift in range(1, 167)
    ]
    assert all(value % 64 == 0 for value in combined_paf)
    assert any(value != 0 for value in combined_paf)

    full_row_sums = [sum(sequence) for sequence in quadruple]
    base_row_sums = [sum(sequence) for sequence in base_sequences]
    assert full_row_sums == [1, -5, -1, 1]
    assert base_row_sums == [-2, 3, 0, -1]
    assert sum(value * value for value in full_row_sums) == 28
    assert sum(value * value for value in base_row_sums) == 14

    profiles = target_row_sum_profiles(base_row_sums)
    minimum_distance = profiles[0][0]
    nearest_profiles = [
        profile for distance, profile in profiles if distance == minimum_distance
    ]

    certificate = {
        "source": "Eliahou, A 64-modular Hadamard matrix of order 668 (2025)",
        "length": 167,
        "s_run_lengths": s_runs,
        "q_run_lengths": q_runs,
        "full_row_sums": full_row_sums,
        "base_sequence_row_sums": base_row_sums,
        "base_sequence_row_sum_square_total": 14,
        "exact_base_sequence_required_total": 334,
        "minimum_hamming_distance_from_current_row_sums_to_exact_dc_profile": minimum_distance,
        "nearest_exact_dc_profiles": nearest_profiles,
        "exact_dc_profile_count": len(profiles),
        "aperiodic_defects": observed_defects,
        "combined_periodic_autocorrelation_nonzero_shifts": sum(
            value != 0 for value in combined_paf
        ),
        "combined_periodic_autocorrelation_max_abs": max(
            map(abs, combined_paf)
        ),
        "mod_64_valid": all(value % 64 == 0 for value in combined_paf),
        "mod_128_obstructing_aperiodic_lags": [
            lag for lag, value in observed_defects.items() if value % 128 != 0
        ],
    }
    payload = json.dumps(certificate, indent=2)
    print(payload)
    if args.certificate:
        with open(args.certificate, "w", encoding="ascii") as handle:
            handle.write(payload + "\n")
    if args.sequences:
        with open(args.sequences, "w", encoding="ascii") as handle:
            json.dump({"sequences": quadruple}, handle, separators=(",", ":"))
            handle.write("\n")


if __name__ == "__main__":
    main()
