#!/usr/bin/env python3
"""Dependency-free verifier for the LP(333) ID-7 single-shift obstruction."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from itertools import product
import json
from pathlib import Path
from typing import Iterable


N = 333
SHIFT = 111
GENERATORS = (73, 112)
EXPECTED_SUBGROUP = (1, 73, 112, 184, 223, 295)
DEFAULT_OUTPUT = (
    Path(__file__).resolve().parent.parent
    / "results"
    / "obstruction_certificate.json"
)


def require(condition: bool, message: str) -> None:
    """Enforce proof checks even under ``python -O``."""

    if not condition:
        raise AssertionError(message)


def generated_subgroup(generators: Iterable[int]) -> tuple[int, ...]:
    subgroup = {1}
    generators = tuple(generators)
    while True:
        expanded = subgroup | {
            (value * generator) % N
            for value in subgroup
            for generator in generators
        }
        if expanded == subgroup:
            return tuple(sorted(subgroup))
        subgroup = expanded


def multiplication_orbits(subgroup: Iterable[int]) -> tuple[list[list[int]], list[int]]:
    subgroup = tuple(subgroup)
    unseen = set(range(N))
    orbits = []
    orbit_index = [-1] * N
    while unseen:
        seed = min(unseen)
        orbit = sorted({(element * seed) % N for element in subgroup})
        index = len(orbits)
        for value in orbit:
            orbit_index[value] = index
        unseen.difference_update(orbit)
        orbits.append(orbit)
    require(all(index >= 0 for index in orbit_index), "incomplete orbit map")
    return orbits, orbit_index


def exact_quotient_minimum(
    orbit_count: int,
    orbit_index: list[int],
) -> tuple[int, list[dict]]:
    """Minimize the shift PAF over orbit signs, component by component."""

    weights: Counter[tuple[int, int]] = Counter()
    for value in range(N):
        left = orbit_index[value]
        right = orbit_index[(value + SHIFT) % N]
        edge = (left, right) if left <= right else (right, left)
        weights[edge] += 1

    forced_loops = sum(
        weight for (left, right), weight in weights.items() if left == right
    )
    adjacency = {index: set() for index in range(orbit_count)}
    for (left, right), _weight in weights.items():
        if left != right:
            adjacency[left].add(right)
            adjacency[right].add(left)

    components = []
    seen = set()
    for start in range(orbit_count):
        if start in seen or not adjacency[start]:
            continue
        stack = [start]
        seen.add(start)
        component = []
        while stack:
            current = stack.pop()
            component.append(current)
            for neighbor in adjacency[current]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)

        component = sorted(component)
        minimum = None
        for signs in product((-1, 1), repeat=len(component)):
            assignment = dict(zip(component, signs))
            value = sum(
                weight * assignment[left] * assignment[right]
                for (left, right), weight in weights.items()
                if left != right and left in assignment and right in assignment
            )
            minimum = value if minimum is None else min(minimum, value)
        require(minimum is not None, "empty quotient component")
        components.append({"size": len(component), "minimumContribution": minimum})

    exact_minimum = forced_loops + sum(
        record["minimumContribution"] for record in components
    )
    return exact_minimum, components


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    subgroup = generated_subgroup(GENERATORS)
    require(subgroup == EXPECTED_SUBGROUP, "ID-7 subgroup closure mismatch")

    crt_image = sorted((value % 9, value % 37) for value in subgroup)
    expected_crt_image = sorted(
        (mod9, mod37) for mod9 in (1, 4, 7) for mod37 in (1, 36)
    )
    require(crt_image == expected_crt_image, "ID-7 CRT product mismatch")
    require((SHIFT % 9, SHIFT % 37) == (3, 0), "shift CRT image mismatch")

    witnesses = {
        value: [
            element
            for element in subgroup
            if (element * value - (value + SHIFT)) % N == 0
        ]
        for value in range(N)
    }
    forced_values = [value for value, found in witnesses.items() if found]
    forced_by_mod9 = Counter(value % 9 for value in forced_values)
    require(len(forced_values) == 222, "same-orbit count is not 222")
    require(
        forced_by_mod9
        == {1: 37, 2: 37, 4: 37, 5: 37, 7: 37, 8: 37},
        "same-orbit residue distribution mismatch",
    )

    orbits, orbit_index = multiplication_orbits(subgroup)
    orbit_signature = Counter(len(orbit) for orbit in orbits)
    require(
        orbit_signature == {1: 3, 2: 54, 3: 2, 6: 36},
        "ID-7 orbit signature mismatch",
    )
    forced_by_orbit_map = [
        value
        for value in range(N)
        if orbit_index[value] == orbit_index[(value + SHIFT) % N]
    ]
    require(
        forced_by_orbit_map == forced_values,
        "orbit-map and multiplier-witness counts disagree",
    )

    elementary_row_lower_bound = len(forced_values) - (N - len(forced_values))
    elementary_pair_lower_bound = 2 * elementary_row_lower_bound
    require(
        (elementary_row_lower_bound, elementary_pair_lower_bound) == (111, 222),
        "elementary lower bound mismatch",
    )
    require(elementary_pair_lower_bound > -2, "Legendre contradiction disappeared")

    exact_row_minimum, components = exact_quotient_minimum(
        len(orbits), orbit_index
    )
    component_summary = Counter(
        (record["size"], record["minimumContribution"])
        for record in components
    )
    require(
        component_summary == {(3, -1): 1, (3, -2): 18},
        "unexpected quotient component structure",
    )
    require(exact_row_minimum == 185, "exact row minimum is not 185")

    # Mutation control: without the order-three generator 112, no shift-111
    # term is forced equal by the remaining order-two symmetry.
    mutated_subgroup = generated_subgroup((73,))
    mutated_forced_count = sum(
        any(
            (element * value - (value + SHIFT)) % N == 0
            for element in mutated_subgroup
        )
        for value in range(N)
    )
    require(mutated_forced_count == 0, "mutation control did not disable proof")

    payload = {
        "schema": "lp333.id7-single-shift-obstruction.v1",
        "status": "PASS",
        "verdict": "NO_ID7_INVARIANT_LP333_EXISTS",
        "subgroup": {
            "classificationId": 7,
            "generators": list(GENERATORS),
            "elements": list(subgroup),
            "crtImageMod9Mod37": [list(pair) for pair in crt_image],
            "orbitSignature": [
                [size, count] for size, count in sorted(orbit_signature.items())
            ],
        },
        "shift": {
            "value": SHIFT,
            "crtImageMod9Mod37": [3, 0],
            "forcedEqualTermCount": len(forced_values),
            "unforcedTermCount": N - len(forced_values),
            "forcedResiduesMod9": dict(sorted(forced_by_mod9.items())),
        },
        "elementaryProof": {
            "singleRowPafLowerBound": elementary_row_lower_bound,
            "pairPafLowerBound": elementary_pair_lower_bound,
            "legendrePairTarget": -2,
            "contradiction": "222 > -2",
        },
        "independentExactStrengthening": {
            "singleRowPafMinimum": exact_row_minimum,
            "pairPafLowerBound": 2 * exact_row_minimum,
            "componentSummary": [
                {
                    "componentSize": size,
                    "minimumContribution": minimum,
                    "count": count,
                }
                for (size, minimum), count in sorted(component_summary.items())
            ],
        },
        "mutationControl": {
            "subgroupGenerators": [73],
            "forcedEqualTermCount": mutated_forced_count,
            "result": "PASS",
        },
        "claimBoundary": (
            "Applies exactly to pairs with both rows fixed by common-multiplier "
            "ID 7. Unrestricted LP(333) and Hadamard-668 remain open."
        ),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    digest = hashlib.sha256(args.output.read_bytes()).hexdigest()
    print(f"certificate: {args.output}")
    print(f"sha256: {digest}")
    print("PROOF VERIFIED: ID 7 is impossible (single shift 111)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
