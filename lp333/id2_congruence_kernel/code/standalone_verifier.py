#!/usr/bin/env python3
"""Dependency-free verifier for the LP(333) ID-2 fibre obstruction."""

from __future__ import annotations

import argparse
from collections import Counter
from itertools import product
import hashlib
import json
from math import gcd
from pathlib import Path


N = 333
P = 3
M = 111
GENERATOR = 112
DEFAULT_OUTPUT = (
    Path(__file__).resolve().parent.parent
    / "results"
    / "obstruction_certificate.json"
)


def require(condition: bool, message: str) -> None:
    """Enforce proof checks even under ``python -O``."""

    if not condition:
        raise AssertionError(message)


def generated_subgroup(generator: int) -> tuple[int, ...]:
    subgroup = {1}
    while True:
        expanded = subgroup | {(generator * value) % N for value in subgroup}
        if expanded == subgroup:
            return tuple(sorted(subgroup))
        subgroup = expanded


def fibre(residue: int) -> tuple[int, ...]:
    return tuple(residue + M * layer for layer in range(P))


def cyclic_contribution(signs: tuple[int, ...]) -> int:
    return sum(signs[layer] * signs[(layer + 1) % P] for layer in range(P))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    subgroup = generated_subgroup(GENERATOR)
    require(subgroup == (1, 112, 223), "ID-2 subgroup closure mismatch")

    quotient_kernel = tuple(
        value
        for value in range(N)
        if gcd(value, N) == 1 and value % M == 1
    )
    require(subgroup == quotient_kernel, "subgroup is not the mod-111 kernel")

    action_records = []
    forced_monochromatic = []
    for residue in range(M):
        positions = fibre(residue)
        image_layers = tuple(
            ((GENERATOR * position) % N - residue) // M
            for position in positions
        )
        expected_layers = tuple(
            (layer + residue) % P for layer in range(P)
        )
        require(
            image_layers == expected_layers,
            f"unexpected multiplier action on fibre {residue}",
        )
        cycle_length = 1 if residue % P == 0 else P
        if cycle_length == P:
            forced_monochromatic.append(residue)
        action_records.append(
            {
                "residue": residue,
                "positions": list(positions),
                "imageLayers": list(image_layers),
                "cycleLength": cycle_length,
            }
        )

    require(
        len(forced_monochromatic) == 74,
        "wrong number of nontrivial three-cycle fibres",
    )

    pattern_audit = []
    contribution_counts: Counter[int] = Counter()
    for signs in product((-1, 1), repeat=P):
        contribution = cyclic_contribution(signs)
        monochromatic = len(set(signs)) == 1
        require(
            contribution == (3 if monochromatic else -1),
            "fibre autocorrelation dichotomy failed",
        )
        contribution_counts[contribution] += 1
        pattern_audit.append(
            {
                "signs": list(signs),
                "monochromatic": monochromatic,
                "shift111Contribution": contribution,
            }
        )
    require(contribution_counts == {-1: 6, 3: 2}, "pattern count mismatch")

    # PAF_X(111) = 4*mu(X)-111, where mu counts monochromatic fibres.
    # The Legendre equation PAF_A(111)+PAF_B(111)=-2 therefore forces
    # mu(A)+mu(B)=55.
    compatible_mu_pairs = [
        [mu_a, mu_b]
        for mu_a in range(M + 1)
        for mu_b in range(M + 1)
        if (4 * mu_a - M) + (4 * mu_b - M) == -2
    ]
    require(len(compatible_mu_pairs) == 56, "unexpected fibre-count solutions")
    require(
        {mu_a + mu_b for mu_a, mu_b in compatible_mu_pairs} == {55},
        "Legendre shift equation did not force total 55",
    )
    require(
        all(mu_a < 74 and mu_b < 74 for mu_a, mu_b in compatible_mu_pairs),
        "a shift-compatible pair permits an invariant row",
    )

    payload = {
        "schema": "lp333.id2-congruence-kernel-obstruction.v1",
        "status": "PASS",
        "verdict": "NO_LP333_HAS_EITHER_ROW_INVARIANT_UNDER_ID2",
        "subgroup": {
            "classificationId": 2,
            "generator": GENERATOR,
            "elements": list(subgroup),
            "description": "kernel of reduction from units mod 333 to units mod 111",
        },
        "fibreAction": {
            "representation": "n = r + 111*t with 0 <= r < 111 and t in Z/3Z",
            "generatorAction": "t maps to t+r modulo 3",
            "records": action_records,
            "forcedMonochromaticResidues": forced_monochromatic,
            "forcedMonochromaticCount": len(forced_monochromatic),
        },
        "localPatternAudit": pattern_audit,
        "localContributionCounts": {
            str(key): value for key, value in sorted(contribution_counts.items())
        },
        "legendreShift111": {
            "singleRowFormula": "PAF_X(111) = 4*mu(X)-111",
            "pairTarget": -2,
            "requiredMonochromaticTotal": 55,
            "compatiblePairCount": len(compatible_mu_pairs),
            "compatibleMuPairs": compatible_mu_pairs,
        },
        "contradiction": {
            "invariantRowLowerBound": 74,
            "bothRowsTotalRequired": 55,
            "statement": (
                "one invariant row already has more monochromatic fibres "
                "than the pair total"
            ),
        },
        "claimBoundary": (
            "Excludes a Legendre pair when either row is invariant under ID 2; "
            "unrestricted LP(333) and Hadamard-668 remain open."
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
    print("PROOF VERIFIED: ID 2 is impossible (even one invariant row suffices)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
