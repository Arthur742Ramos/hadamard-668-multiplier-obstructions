#!/usr/bin/env python3
"""Standalone audit of LP(333) orbit coefficients and CNF semantics.

This intentionally imports only the Python standard library.  In particular it
does not import ``lp333_cnf``, ``build_lp333_model``, ``audit_rebuild``, or any
serializer from the primary proof implementation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from itertools import product
from math import gcd
from pathlib import Path
import random
from typing import Dict, Iterable, List, Sequence, Tuple


LENGTH = 333
PHASE = Path(__file__).resolve().parent
ROOT = PHASE.parent

Literal = int
Clause = Tuple[int, ...]


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            hasher.update(block)
    return hasher.hexdigest()


def canonical_sha256(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def check_pins() -> Dict:
    pins_path = PHASE / "dependency_pins.json"
    pins = json.loads(pins_path.read_text(encoding="utf-8"))
    checks = []
    for item in pins["files"]:
        path = (PHASE / item["path"]).resolve()
        actual = sha256_file(path)
        if actual != item["sha256"]:
            raise AssertionError(f"dependency pin mismatch: {item['path']}")
        checks.append({"path": item["path"], "sha256": actual, "result": "PASS"})
    classification = json.loads(
        (ROOT / "results" / "subgroup_classification.json").read_text(encoding="utf-8")
    )
    by_id = {int(record["id"]): record for record in classification["subgroups"]}
    subgroup_checks = []
    for item in pins["subgroup_records"]:
        record = by_id.get(int(item["id"]))
        actual = canonical_sha256(record) if record is not None else None
        if actual != item["canonical_sha256"]:
            raise AssertionError(f"subgroup record pin mismatch: {item['id']}")
        subgroup_checks.append(
            {"id": item["id"], "canonical_sha256": actual, "result": "PASS"}
        )
    return {
        "path": "dependency_pins.json",
        "checks": checks,
        "subgroup_record_checks": subgroup_checks,
        "result": "PASS",
    }


def validate_subgroup(elements: Sequence[int]) -> List[int]:
    group = sorted(set(int(value) for value in elements))
    if 1 not in group or not group:
        raise AssertionError("subgroup lacks identity")
    if any(gcd(value, LENGTH) != 1 for value in group):
        raise AssertionError("subgroup contains a nonunit")
    group_set = set(group)
    if any((left * right) % LENGTH not in group_set for left in group for right in group):
        raise AssertionError("subgroup is not closed")
    return group


def multiplication_orbits(group: Sequence[int]) -> List[List[int]]:
    unseen = set(range(LENGTH))
    orbits = []
    while unseen:
        seed = min(unseen)
        orbit = {seed}
        frontier = [seed]
        while frontier:
            value = frontier.pop()
            for multiplier in group:
                image = (multiplier * value) % LENGTH
                if image not in orbit:
                    orbit.add(image)
                    frontier.append(image)
        unseen.difference_update(orbit)
        orbits.append(sorted(orbit))
    return sorted(orbits, key=lambda orbit: (len(orbit), orbit[0]))


def build_orbit_spec(group: Sequence[int]) -> Dict:
    orbits = multiplication_orbits(group)
    if orbits[0] != [0]:
        raise AssertionError("orbit zero is not first")
    index = [0] * LENGTH
    for orbit_index, orbit in enumerate(orbits):
        for value in orbit:
            index[value] = orbit_index
    rank = len(orbits)
    sizes = [len(orbit) for orbit in orbits]
    representatives = [orbit[0] for orbit in orbits[1:]]
    matrices = []
    constants = []
    for shift in representatives:
        directed = [[0] * rank for _ in range(rank)]
        for position in range(LENGTH):
            directed[index[position]][index[(position + shift) % LENGTH]] += 1
        constants.append(sum(directed[q][q] for q in range(rank)))
        weights = [[0] * rank for _ in range(rank)]
        for q in range(rank):
            for q2 in range(q + 1, rank):
                weights[q][q2] = directed[q][q2] + directed[q2][q]
                weights[q2][q] = weights[q][q2]
        matrices.append(weights)
    return {
        "orbits": orbits,
        "index": index,
        "sizes": sizes,
        "representatives": representatives,
        "constants": constants,
        "weights": matrices,
    }


def paf_from_weights(spec: Dict, signs: Sequence[int], representative_index: int) -> int:
    total = spec["constants"][representative_index]
    weights = spec["weights"][representative_index]
    for q in range(len(signs)):
        for q2 in range(q + 1, len(signs)):
            total += weights[q][q2] * signs[q] * signs[q2]
    return total


def direct_paf(sequence: Sequence[int], shift: int) -> int:
    return sum(
        sequence[position] * sequence[(position + shift) % LENGTH]
        for position in range(LENGTH)
    )


class IndependentCNF:
    def __init__(self) -> None:
        self.next_variable = 1
        self.false = self.new_variable()
        self.clauses: List[Clause] = []
        self.gates: List[Tuple] = []
        self.add_clause(-self.false)

    @property
    def variables(self) -> int:
        return self.next_variable - 1

    def new_variable(self) -> int:
        value = self.next_variable
        self.next_variable += 1
        return value

    def add_clause(self, *literals: int) -> None:
        seen = set()
        normalized = []
        for literal in literals:
            if literal == 0:
                raise AssertionError("zero is reserved for DIMACS termination")
            if -literal in seen:
                return
            if literal not in seen:
                seen.add(literal)
                normalized.append(literal)
        self.clauses.append(tuple(normalized))

    def xor(self, left: Literal, right: Literal) -> int:
        output = self.new_variable()
        self.add_clause(-left, -right, -output)
        self.add_clause(left, right, -output)
        self.add_clause(-left, right, output)
        self.add_clause(left, -right, output)
        self.gates.append(("xor", output, left, right))
        return output

    def full_adder(
        self, left: Literal, right: Literal, carry_in: Literal
    ) -> Tuple[int, int]:
        sum_bit = self.new_variable()
        carry_out = self.new_variable()
        for values in product((0, 1), repeat=3):
            expected = sum(values) & 1
            forbidden = 1 - expected
            clause = [
                signal if value == 0 else -signal
                for signal, value in zip((left, right, carry_in), values)
            ]
            clause.append(sum_bit if forbidden == 0 else -sum_bit)
            self.add_clause(*clause)
        self.add_clause(-left, -right, carry_out)
        self.add_clause(-left, -carry_in, carry_out)
        self.add_clause(-right, -carry_in, carry_out)
        self.add_clause(left, right, -carry_out)
        self.add_clause(left, carry_in, -carry_out)
        self.add_clause(right, carry_in, -carry_out)
        self.gates.append(("full", sum_bit, carry_out, left, right, carry_in))
        return sum_bit, carry_out

    def weighted_sum(
        self, terms: Iterable[Tuple[int, Literal]]
    ) -> Tuple[List[int], int]:
        values = [(int(weight), literal) for weight, literal in terms if weight]
        if any(weight < 0 for weight, _ in values):
            raise AssertionError("negative PB coefficient")
        total = sum(weight for weight, _ in values)
        columns: List[List[Literal]] = []
        for weight, literal in values:
            bit = 0
            while weight:
                if weight & 1:
                    while len(columns) <= bit:
                        columns.append([])
                    columns[bit].append(literal)
                weight >>= 1
                bit += 1
        bit = 0
        while bit < len(columns):
            while len(columns[bit]) >= 3:
                left = columns[bit].pop()
                right = columns[bit].pop()
                carry_in = columns[bit].pop()
                sum_bit, carry_out = self.full_adder(left, right, carry_in)
                columns[bit].append(sum_bit)
                while len(columns) <= bit + 1:
                    columns.append([])
                columns[bit + 1].append(carry_out)
            bit += 1
        width = max(1, total.bit_length(), len(columns))
        columns.extend([] for _ in range(width - len(columns)))
        left_row = [
            columns[bit][0] if len(columns[bit]) else self.false
            for bit in range(width)
        ]
        right_row = [
            columns[bit][1] if len(columns[bit]) > 1 else self.false
            for bit in range(width)
        ]
        bits = []
        carry = self.false
        for bit in range(width):
            sum_bit, carry = self.full_adder(left_row[bit], right_row[bit], carry)
            bits.append(sum_bit)
        self.add_clause(-carry)
        return bits, total

    def force_value(self, bits: Sequence[Literal], value: int) -> None:
        if value < 0 or value.bit_length() > len(bits):
            self.add_clause()
            return
        for bit, signal in enumerate(bits):
            self.add_clause(signal if (value >> bit) & 1 else -signal)

    def equivalence(self, left: Literal, right: Literal) -> None:
        self.add_clause(-left, right)
        self.add_clause(left, -right)

    def force_two_values(self, bits: Sequence[Literal], low: int, high: int) -> None:
        if low == high:
            self.force_value(bits, low)
            return
        if low < 0 or high.bit_length() > len(bits):
            self.add_clause()
            return
        differing = [
            bit
            for bit in range(len(bits))
            if ((low >> bit) & 1) != ((high >> bit) & 1)
        ]
        if not differing:
            self.force_value(bits, low)
            return
        pivot = differing[0]
        choose_high = bits[pivot] if ((low >> pivot) & 1) == 0 else -bits[pivot]
        for bit, signal in enumerate(bits):
            if bit == pivot:
                continue
            low_bit = (low >> bit) & 1
            high_bit = (high >> bit) & 1
            if low_bit == high_bit:
                self.add_clause(signal if low_bit else -signal)
            elif low_bit == 0:
                self.equivalence(signal, choose_high)
            else:
                self.equivalence(signal, -choose_high)

    def dimacs_hash(self, split_units: bool) -> str:
        units = [clause for clause in self.clauses if len(clause) == 1]
        variables = self.variables + (len(units) if split_units else 0)
        clauses = len(self.clauses) + (len(units) if split_units else 0)
        hasher = hashlib.sha256()

        def line(text: str) -> None:
            hasher.update(text.encode("ascii"))

        line(f"p cnf {variables} {clauses}\n")
        mask = self.variables + 1
        for clause in self.clauses:
            if split_units and len(clause) == 1:
                literal = clause[0]
                line(f"{literal} {mask} 0\n")
                line(f"{literal} {-mask} 0\n")
                mask += 1
            else:
                line(" ".join(str(literal) for literal in clause) + " 0\n")
        return hasher.hexdigest()

    @staticmethod
    def literal_value(literal: Literal, values: Sequence[bool | None]) -> bool:
        value = values[abs(literal)]
        if value is None:
            raise AssertionError(f"undefined literal {literal}")
        return bool(value) if literal > 0 else not bool(value)

    def extend(self, values: List[bool | None]) -> None:
        for gate in self.gates:
            if gate[0] == "xor":
                _, output, left, right = gate
                values[output] = self.literal_value(left, values) ^ self.literal_value(
                    right, values
                )
            else:
                _, sum_bit, carry, left, right, carry_in = gate
                total = (
                    int(self.literal_value(left, values))
                    + int(self.literal_value(right, values))
                    + int(self.literal_value(carry_in, values))
                )
                values[sum_bit] = bool(total & 1)
                values[carry] = total >= 2

    def clauses_hold(self, values: Sequence[bool | None]) -> bool:
        return all(
            any(self.literal_value(literal, values) for literal in clause)
            for clause in self.clauses
        )


def bits_value(bits: Sequence[int], values: Sequence[bool | None]) -> int:
    return sum(
        (1 << bit) * int(IndependentCNF.literal_value(signal, values))
        for bit, signal in enumerate(bits)
    )


def build_independent_model(spec: Dict) -> Dict:
    rank = len(spec["orbits"])
    cnf = IndependentCNF()
    za = [cnf.new_variable() for _ in range(rank)]
    zb = [cnf.new_variable() for _ in range(rank)]
    cnf.add_clause(-za[0])
    cnf.add_clause(-zb[0])
    used_pairs = sorted(
        {
            (q, q2)
            for weights in spec["weights"]
            for q in range(rank)
            for q2 in range(q + 1, rank)
            if weights[q][q2]
        }
    )
    wa = {pair: cnf.xor(za[pair[0]], za[pair[1]]) for pair in used_pairs}
    wb = {pair: cnf.xor(zb[pair[0]], zb[pair[1]]) for pair in used_pairs}
    paf_bits = []
    targets = []
    obstructions = []
    for index, weights in enumerate(spec["weights"]):
        terms = []
        coefficient_sum = 0
        for pair in used_pairs:
            coefficient = weights[pair[0]][pair[1]]
            if coefficient:
                terms.extend(((coefficient, wa[pair]), (coefficient, wb[pair])))
                coefficient_sum += coefficient
        bits, total = cnf.weighted_sum(terms)
        target = spec["constants"][index] + coefficient_sum + 1
        if total != 2 * coefficient_sum:
            raise AssertionError("PAF PB total mismatch")
        if target > total:
            obstructions.append(
                {
                    "representative_index": index,
                    "shift": spec["representatives"][index],
                    "required_weighted_xor_sum": target,
                    "maximum_weighted_xor_sum": total,
                }
            )
        cnf.force_value(bits, target)
        paf_bits.append(bits)
        targets.append(target)
    row_a_bits, _ = cnf.weighted_sum(zip(spec["sizes"], za))
    row_b_bits, _ = cnf.weighted_sum(zip(spec["sizes"], zb))
    cnf.force_two_values(row_a_bits, 166, 167)
    cnf.force_two_values(row_b_bits, 166, 167)
    return {
        "cnf": cnf,
        "za": za,
        "zb": zb,
        "wa": wa,
        "wb": wb,
        "paf_bits": paf_bits,
        "row_a_bits": row_a_bits,
        "row_b_bits": row_b_bits,
        "targets": targets,
        "pairs": used_pairs,
        "obstructions": obstructions,
    }


def semantic_value(spec: Dict, za: Sequence[int], zb: Sequence[int]) -> bool:
    if za[0] != 0 or zb[0] != 0:
        return False
    xa = [1 - 2 * value for value in za]
    xb = [1 - 2 * value for value in zb]
    if sum(size * sign for size, sign in zip(spec["sizes"], xa)) not in (-1, 1):
        return False
    if sum(size * sign for size, sign in zip(spec["sizes"], xb)) not in (-1, 1):
        return False
    return all(
        paf_from_weights(spec, xa, index) + paf_from_weights(spec, xb, index) == -2
        for index in range(len(spec["representatives"]))
    )


def audit_model_semantics(spec: Dict, model: Dict, samples: int, seed: int) -> Dict:
    rng = random.Random(seed)
    rank = len(spec["orbits"])
    cnf: IndependentCNF = model["cnf"]
    semantic_true = 0
    cnf_true = 0
    for _ in range(samples):
        za = [0] + [rng.randrange(2) for _ in range(rank - 1)]
        zb = [0] + [rng.randrange(2) for _ in range(rank - 1)]
        values: List[bool | None] = [None] * (cnf.variables + 1)
        values[cnf.false] = False
        for variable, value in zip(model["za"], za):
            values[variable] = bool(value)
        for variable, value in zip(model["zb"], zb):
            values[variable] = bool(value)
        cnf.extend(values)
        if any(value is None for value in values[1:]):
            raise AssertionError("undefined generated CNF variable")

        for pair, variable in model["wa"].items():
            if bool(values[variable]) != bool(za[pair[0]] ^ za[pair[1]]):
                raise AssertionError("a XOR semantic mismatch")
        for pair, variable in model["wb"].items():
            if bool(values[variable]) != bool(zb[pair[0]] ^ zb[pair[1]]):
                raise AssertionError("b XOR semantic mismatch")
        for index, weights in enumerate(spec["weights"]):
            expected = sum(
                weights[q][q2]
                * ((za[q] ^ za[q2]) + (zb[q] ^ zb[q2]))
                for q in range(rank)
                for q2 in range(q + 1, rank)
            )
            if bits_value(model["paf_bits"][index], values) != expected:
                raise AssertionError("PAF PB output mismatch")
        if bits_value(model["row_a_bits"], values) != sum(
            size * value for size, value in zip(spec["sizes"], za)
        ):
            raise AssertionError("row-a PB output mismatch")
        if bits_value(model["row_b_bits"], values) != sum(
            size * value for size, value in zip(spec["sizes"], zb)
        ):
            raise AssertionError("row-b PB output mismatch")

        direct = semantic_value(spec, za, zb)
        encoded = cnf.clauses_hold(values)
        if direct != encoded:
            raise AssertionError("direct LP predicate and generated CNF differ")
        semantic_true += int(direct)
        cnf_true += int(encoded)
    return {
        "samples": samples,
        "seed": seed,
        "semantic_true_count": semantic_true,
        "cnf_true_count": cnf_true,
        "xor_checks": samples * 2 * len(model["pairs"]),
        "weighted_sum_checks": samples * (len(spec["representatives"]) + 2),
        "result": "PASS",
    }


def audit_coefficients(spec: Dict, samples: int, seed: int) -> Dict:
    rng = random.Random(seed)
    rank = len(spec["orbits"])
    checked = 0
    for _ in range(samples):
        signs = [rng.choice((-1, 1)) for _ in range(rank)]
        sequence = [signs[spec["index"][position]] for position in range(LENGTH)]
        for index, shift in enumerate(spec["representatives"]):
            if paf_from_weights(spec, signs, index) != direct_paf(sequence, shift):
                raise AssertionError(f"PAF coefficient mismatch at shift {shift}")
            checked += 1
    digest_payload = {
        "orbits": spec["orbits"],
        "sizes": spec["sizes"],
        "representatives": spec["representatives"],
        "constants": spec["constants"],
        "weights": spec["weights"],
    }
    return {
        "samples": samples,
        "representative_paf_checks": checked,
        "coefficient_sha256": canonical_sha256(digest_payload),
        "result": "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=11)
    parser.add_argument(
        "--output",
        type=Path,
        default=PHASE / "audits" / "independent_standalone_audit.json",
    )
    args = parser.parse_args()

    pins = check_pins()
    manifest = json.loads((PHASE / "manifest.json").read_text(encoding="utf-8"))
    classification = json.loads(
        (ROOT / "results" / "subgroup_classification.json").read_text(encoding="utf-8")
    )
    records_by_id = {
        int(record["id"]): record for record in classification["subgroups"]
    }
    results = []
    for record in manifest["records"]:
        subgroup_id = int(record["subgroup_id"])
        group_record = records_by_id[subgroup_id]
        group = validate_subgroup(group_record["elements"])
        spec = build_orbit_spec(group)
        model = build_independent_model(spec)
        base_generated = model["cnf"].dimacs_hash(False)
        proof_generated = model["cnf"].dimacs_hash(True)
        base_actual = sha256_file(PHASE / record["cnf"])
        proof_actual = sha256_file(PHASE / record["proof_cnf"])
        if base_generated != base_actual or base_generated != record["cnf_sha256"]:
            raise AssertionError(f"id {subgroup_id}: base CNF independent hash mismatch")
        if proof_generated != proof_actual or proof_generated != record["proof_cnf_sha256"]:
            raise AssertionError(f"id {subgroup_id}: proof CNF independent hash mismatch")
        coefficient_audit = audit_coefficients(
            spec, args.samples, 810000 + subgroup_id
        )
        semantic_audit = audit_model_semantics(
            spec, model, args.samples, 820000 + subgroup_id
        )
        results.append(
            {
                "id": subgroup_id,
                "subgroup_order": len(group),
                "orbit_count": len(spec["orbits"]),
                "coefficient_audit": coefficient_audit,
                "cnf_semantic_audit": semantic_audit,
                "base_cnf_sha256": base_generated,
                "proof_cnf_sha256": proof_generated,
                "direct_pb_obstructions": model["obstructions"],
                "result": "PASS",
            }
        )
    payload = {
        "kind": "standalone-standard-library-orbit-PAF-and-CNF-audit",
        "implementation": (
            "independent_audit.py uses no imports from the primary proof encoder, "
            "core.py, search_common.py, or existing audit serializers"
        ),
        "dependency_pins": pins,
        "records": results,
        "result": "PASS",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"records": len(results), "result": payload["result"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
