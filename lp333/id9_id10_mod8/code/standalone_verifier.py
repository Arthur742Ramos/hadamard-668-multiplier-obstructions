#!/usr/bin/env python3
"""Exact dependency-free verifier for the LP(333) ID-9/ID-10 mod-8 proof."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from itertools import product
import json
from pathlib import Path
from typing import Iterable


N = 333
CASES = {
    9: {
        "generators": (73, 85),
        "elements": (1, 73, 85, 211, 232, 286),
    },
    10: {
        "generators": (73, 121),
        "elements": (1, 73, 121, 175, 196, 322),
    },
}
DEFAULT_OUTPUT = (
    Path(__file__).resolve().parent.parent
    / "results"
    / "obstruction_certificate.json"
)


def require(condition: bool, message: str) -> None:
    """Enforce proof checks even when Python is invoked with optimization."""

    if not condition:
        raise AssertionError(message)


def canonical_sha256(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def generated_subgroup(generators: Iterable[int]) -> tuple[int, ...]:
    subgroup = {1}
    generators = tuple(generators)
    while True:
        expanded = subgroup | {
            (element * generator) % N
            for element in subgroup
            for generator in generators
        }
        if expanded == subgroup:
            return tuple(sorted(subgroup))
        subgroup = expanded


def multiplication_orbits(subgroup: Iterable[int]) -> list[list[int]]:
    subgroup = tuple(subgroup)
    unseen = set(range(N))
    orbits = []
    while unseen:
        seed = min(unseen)
        orbit = sorted({(element * seed) % N for element in subgroup})
        unseen.difference_update(orbit)
        orbits.append(orbit)
    return sorted(orbits, key=lambda orbit: (len(orbit), orbit[0]))


def local_residue_certificate(row_sums: tuple[int, ...]) -> dict:
    """Exhaust all c=0 sign patterns and compatible compressed residues."""

    local_patterns = []
    paf_residues = set()
    for rho in row_sums:
        for d3, d6, u, v in product((-1, 1), repeat=4):
            z0 = 1 + d3 + d6 + 3 * u + 3 * v

            # The other 36 mod-37 fibers form six size-six cosets. Their
            # compressed values are odd, so rho-z0 is divisible by 12.
            if (rho - z0) % 12:
                continue

            local_patterns.append(
                {"rho": rho, "d3": d3, "d6": d6, "u": u, "v": v, "z0": z0}
            )
            if row_sums == (-1, 1):
                require(z0 == rho, "bounded mod-12 step did not force z0=rho")
                require(v == -u, "c=0 fiber did not force v=-u")

            # Pairing c with -c gives mu=u (mod 4), nu=v (mod 4).
            # Both mu and nu are odd because each is a sum of 37 signs.
            for mu, nu in product((1, 3, 5, 7), repeat=2):
                if (mu - u) % 4 or (nu - v) % 4:
                    continue
                total = (mu + nu) % 8
                if row_sums == (-1, 1):
                    require(total % 4 == 0, "mu+nu is not divisible by 4")
                    require(
                        (mu * nu - (total - 1)) % 8 == 0,
                        "unified mu*nu congruence failed",
                    )
                    require(
                        (rho * total - total) % 8 == 0,
                        "row-sum term did not reduce to mu+nu",
                    )
                    require(
                        total * total % 8 == 0,
                        "squared total did not vanish",
                    )
                alpha_beta_gamma = (rho - 3 * total) % 8
                paf1 = (alpha_beta_gamma * total + 3 * mu * nu) % 8
                paf_residues.add(paf1)

    return {
        "allowedRowSums": list(row_sums),
        "localPatternCount": len(local_patterns),
        "localPatterns": local_patterns,
        "compressedPaf1ResiduesMod8": sorted(paf_residues),
    }


def direct_assignment_controls(
    subgroup: tuple[int, ...],
    orbits: list[list[int]],
    seed: int,
    required: int = 48,
) -> dict:
    """Check deterministic full invariant assignments as an implementation control."""

    state = seed & ((1 << 64) - 1)

    def next_sign() -> int:
        nonlocal state
        state ^= (state << 13) & ((1 << 64) - 1)
        state ^= state >> 7
        state ^= (state << 17) & ((1 << 64) - 1)
        state &= (1 << 64) - 1
        return 1 if state & 1 else -1

    accepted = 0
    attempts = 0
    transcript = []
    while accepted < required and attempts < 2_000_000:
        attempts += 1
        orbit_signs = [1] + [next_sign() for _ in range(len(orbits) - 1)]
        row_sum = sum(
            len(orbit) * sign for orbit, sign in zip(orbits, orbit_signs)
        )
        if row_sum not in (-1, 1):
            continue

        sequence = [0] * N
        for orbit, sign in zip(orbits, orbit_signs):
            for position in orbit:
                sequence[position] = sign
        require(
            all(
                sequence[(element * position) % N] == sequence[position]
                for element in subgroup
                for position in range(N)
            ),
            "constructed sequence is not subgroup-invariant",
        )

        compressed9 = [
            sum(sequence[position] for position in range(residue, N, 9))
            for residue in range(9)
        ]
        require(
            compressed9[1] == compressed9[4] == compressed9[7],
            "first mod-9 row orbit did not compress to one value",
        )
        require(
            compressed9[2] == compressed9[5] == compressed9[8],
            "second mod-9 row orbit did not compress to one value",
        )
        paf1 = sum(
            compressed9[index] * compressed9[(index + 1) % 9]
            for index in range(9)
        )
        require(paf1 % 8 == 5, "direct compressed PAF residue is not 5 mod 8")

        z0 = sum(sequence[position] for position in range(0, N, 37))
        require(z0 == row_sum, "direct c=0 fiber identity failed")
        transcript.append(
            {"rowSum": row_sum, "compressed9": compressed9, "paf1": paf1}
        )
        accepted += 1

    require(accepted == required, "insufficient direct row-sum controls")
    return {
        "kind": "deterministic-full-orbit-bug-control",
        "seed": seed,
        "attempts": attempts,
        "acceptedAssignments": accepted,
        "transcriptSha256": canonical_sha256(transcript),
        "result": "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    exact = local_residue_certificate((-1, 1))
    require(exact["localPatternCount"] == 6, "unexpected local-pattern count")
    require(
        exact["compressedPaf1ResiduesMod8"] == [5],
        "exact single-sequence PAF residue set is not {5}",
    )

    # Mutation control: changing the row-sum hypothesis to +/-3 admits an
    # additional residue and must disable the contradiction.
    mutated = local_residue_certificate((-3, 3))
    mutated_pair_sums = sorted(
        {
            (left + right) % 8
            for left in mutated["compressedPaf1ResiduesMod8"]
            for right in mutated["compressedPaf1ResiduesMod8"]
        }
    )
    require(
        mutated["compressedPaf1ResiduesMod8"] == [1, 5],
        "row-sum mutation did not produce residues {1,5}",
    )
    require(
        6 in mutated_pair_sums,
        "row-sum mutation did not disable obstruction",
    )

    records = []
    for subgroup_id, source in CASES.items():
        subgroup = generated_subgroup(source["generators"])
        require(subgroup == source["elements"], "subgroup closure mismatch")
        require(
            tuple(sorted({element % 9 for element in subgroup})) == (1, 4, 7),
            "mod-9 subgroup image mismatch",
        )
        require(
            tuple(sorted({element % 37 for element in subgroup}))
            == (1, 10, 11, 26, 27, 36),
            "mod-37 subgroup image mismatch",
        )
        require((73 % 9, 73 % 37) == (1, 36), "CRT image of 73 is incorrect")

        orbits = multiplication_orbits(subgroup)
        require(
            Counter(map(len, orbits)) == {1: 3, 3: 2, 6: 54},
            "multiplication-orbit signature mismatch",
        )
        controls = direct_assignment_controls(
            subgroup, orbits, seed=900_000 + subgroup_id
        )
        records.append(
            {
                "subgroupId": subgroup_id,
                "generators": list(source["generators"]),
                "elements": list(subgroup),
                "mod9Image": [1, 4, 7],
                "mod37Image": [1, 10, 11, 26, 27, 36],
                "orbitSignature": [[1, 3], [3, 2], [6, 54]],
                "symbolicResidueAudit": {
                    "localPatternCount": exact["localPatternCount"],
                    "compressedPaf1ResiduesMod8": [5],
                    "result": "PASS",
                },
                "directAssignmentControls": controls,
                "result": "PASS",
            }
        )

    target = 37 * -2
    derived_pair_residue = (5 + 5) % 8
    target_pair_residue = target % 8
    require(
        (derived_pair_residue, target_pair_residue) == (2, 6),
        "final mod-8 contradiction disappeared",
    )

    payload = {
        "schema": "lp333.id9-id10-crt-mod8-obstruction.v1",
        "status": "PASS",
        "verdict": "NO_ID9_OR_ID10_INVARIANT_LP333_EXISTS",
        "proof": {
            "allowedRowSums": [-1, 1],
            "singleSequenceCompressedPaf1ResiduesMod8": [5],
            "derivedPairResidueMod8": derived_pair_residue,
            "compressionIdentityTarget": target,
            "targetPairResidueMod8": target_pair_residue,
            "contradiction": "2 != 6 (mod 8)",
        },
        "exhaustiveLocalResidueAudit": exact,
        "mutationControl": {
            "allowedRowSums": [-3, 3],
            "singleSequenceResiduesMod8": mutated[
                "compressedPaf1ResiduesMod8"
            ],
            "possiblePairSumsMod8": mutated_pair_sums,
            "targetResidue6BecomesPossible": 6 in mutated_pair_sums,
            "result": "PASS",
        },
        "subgroups": records,
        "claimBoundary": (
            "Applies exactly to pairs fixed by common-multiplier ID 9 or 10. "
            "Unrestricted LP(333) and Hadamard-668 remain open."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    digest = hashlib.sha256(args.output.read_bytes()).hexdigest()
    print(f"certificate: {args.output}")
    print(f"sha256: {digest}")
    print("PROOF VERIFIED: IDs 9 and 10 are impossible (fixed common multipliers)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
