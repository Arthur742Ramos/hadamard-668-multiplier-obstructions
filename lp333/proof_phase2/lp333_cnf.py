#!/usr/bin/env python3
"""Independent CNF/PB encoding for multiplier-invariant Legendre pairs.

The encoding intentionally has no dependency on OR-Tools.  It uses:

* four-clause Tseitin definitions for XOR;
* carry-save reduction of weighted Boolean inputs;
* exact full-adder definitions, followed by a ripple adder; and
* bit-level assertions for PB equalities and two-value row-sum domains.

All generated auxiliary variables are functionally defined by the orbit-value
variables.  ``canonical_cnf_value`` evaluates that unique extension and is used
by the model-equivalence audits in ``run_proofs.py``.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple
import hashlib
import random
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CODE = ROOT / "code"
if str(CODE) not in sys.path:
    sys.path.insert(0, str(CODE))

from core import L, orbits_on_ZL  # noqa: E402
from search_common import subgroup_by_id  # noqa: E402


Literal = int
Clause = Tuple[int, ...]


class CNFBuilder:
    """A DIMACS builder whose gates have a deterministic semantic extension."""

    def __init__(self) -> None:
        self.next_var = 1
        self.clauses: List[Clause] = []
        self.gates: List[Tuple] = []
        self.named_vars: Dict[str, int] = {}
        self.false = self.new_var("constant_false")
        self.add_clause(-self.false)

    @property
    def num_vars(self) -> int:
        return self.next_var - 1

    def new_var(self, name: str | None = None) -> int:
        var = self.next_var
        self.next_var += 1
        if name is not None:
            if name in self.named_vars:
                raise ValueError(f"duplicate variable name: {name}")
            self.named_vars[name] = var
        return var

    def add_clause(self, *literals: int) -> None:
        seen = set()
        normalized: List[int] = []
        for literal in literals:
            if literal == 0:
                raise ValueError("zero is not a DIMACS literal")
            if -literal in seen:
                return
            if literal not in seen:
                seen.add(literal)
                normalized.append(literal)
        self.clauses.append(tuple(normalized))

    def add_unit(self, literal: Literal) -> None:
        self.add_clause(literal)

    def add_equivalence(self, left: Literal, right: Literal) -> None:
        """Encode the equivalence of two Boolean signals (possibly literals)."""
        self.add_clause(-left, right)
        self.add_clause(left, -right)

    def add_xor(self, left: Literal, right: Literal, name: str | None = None) -> int:
        """Return a variable constrained to ``left XOR right``."""
        output = self.new_var(name)
        self.add_clause(-left, -right, -output)
        self.add_clause(left, right, -output)
        self.add_clause(-left, right, output)
        self.add_clause(left, -right, output)
        self.gates.append(("xor", output, left, right))
        return output

    def add_full_adder(
        self, left: Literal, right: Literal, carry_in: Literal, name: str | None = None
    ) -> Tuple[int, int]:
        """Return exact sum and carry signals for three one-bit inputs."""
        sum_bit = self.new_var(None if name is None else f"{name}_sum")
        carry_out = self.new_var(None if name is None else f"{name}_carry")

        signals = (left, right, carry_in)
        for values in product((0, 1), repeat=3):
            expected_sum = sum(values) & 1
            forbidden_sum = 1 - expected_sum
            clause = [
                signal if value == 0 else -signal
                for signal, value in zip(signals, values)
            ]
            clause.append(sum_bit if forbidden_sum == 0 else -sum_bit)
            self.add_clause(*clause)

        self.add_clause(-left, -right, carry_out)
        self.add_clause(-left, -carry_in, carry_out)
        self.add_clause(-right, -carry_in, carry_out)
        self.add_clause(left, right, -carry_out)
        self.add_clause(left, carry_in, -carry_out)
        self.add_clause(right, carry_in, -carry_out)
        self.gates.append(("full_adder", sum_bit, carry_out, left, right, carry_in))
        return sum_bit, carry_out

    def weighted_sum(
        self, terms: Iterable[Tuple[int, Literal]], name: str
    ) -> Tuple[List[int], int]:
        """Encode an exact binary sum of non-negative weighted Boolean signals.

        The carry-save phase preserves the represented integer at each bit
        column.  Its two final rows are combined by exact full adders.  The last
        carry is constrained to false, so the returned little-endian bits are a
        complete representation of the weighted sum.
        """
        normalized = [(int(weight), literal) for weight, literal in terms if weight]
        if any(weight < 0 for weight, _ in normalized):
            raise ValueError("weighted_sum only accepts non-negative weights")
        total = sum(weight for weight, _ in normalized)
        columns: List[List[Literal]] = []
        for weight, literal in normalized:
            bit = 0
            remaining = weight
            while remaining:
                if remaining & 1:
                    while len(columns) <= bit:
                        columns.append([])
                    columns[bit].append(literal)
                remaining >>= 1
                bit += 1

        bit = 0
        while bit < len(columns):
            while len(columns[bit]) >= 3:
                left = columns[bit].pop()
                right = columns[bit].pop()
                carry_in = columns[bit].pop()
                sum_bit, carry_out = self.add_full_adder(
                    left, right, carry_in, f"{name}_csa_{bit}_{len(self.gates)}"
                )
                columns[bit].append(sum_bit)
                while len(columns) <= bit + 1:
                    columns.append([])
                columns[bit + 1].append(carry_out)
            bit += 1

        width = max(1, total.bit_length(), len(columns))
        while len(columns) < width:
            columns.append([])
        left_row = [
            columns[bit][0] if len(columns[bit]) >= 1 else self.false
            for bit in range(width)
        ]
        right_row = [
            columns[bit][1] if len(columns[bit]) >= 2 else self.false
            for bit in range(width)
        ]

        output_bits: List[int] = []
        carry = self.false
        for bit in range(width):
            sum_bit, carry = self.add_full_adder(
                left_row[bit], right_row[bit], carry, f"{name}_ripple_{bit}"
            )
            output_bits.append(sum_bit)
        self.add_unit(-carry)
        return output_bits, total

    def force_value(self, bits: Sequence[Literal], value: int) -> None:
        """Constrain a little-endian binary vector to an exact non-negative value."""
        if value < 0 or value.bit_length() > len(bits):
            self.add_clause()
            return
        for bit, signal in enumerate(bits):
            self.add_unit(signal if ((value >> bit) & 1) else -signal)

    def force_one_of_two(self, bits: Sequence[Literal], low: int, high: int) -> None:
        """Constrain a binary vector to exactly one of two non-negative values."""
        if low > high:
            raise ValueError("invalid PB range")
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
        low_pivot = (low >> pivot) & 1
        high_selector = bits[pivot] if low_pivot == 0 else -bits[pivot]
        for bit, signal in enumerate(bits):
            low_bit = (low >> bit) & 1
            high_bit = (high >> bit) & 1
            if bit == pivot:
                continue
            if low_bit == high_bit:
                self.add_unit(signal if low_bit else -signal)
            elif low_bit == 0 and high_bit == 1:
                self.add_equivalence(signal, high_selector)
            else:
                self.add_equivalence(signal, -high_selector)

    @staticmethod
    def literal_value(literal: Literal, values: Sequence[bool | None]) -> bool:
        value = values[abs(literal)]
        if value is None:
            raise ValueError(f"unassigned literal {literal}")
        return bool(value) if literal > 0 else not bool(value)

    def extend(self, values: List[bool | None]) -> None:
        """Fill all gate outputs from assigned primary inputs in creation order."""
        for gate in self.gates:
            if gate[0] == "xor":
                _, output, left, right = gate
                values[output] = self.literal_value(left, values) ^ self.literal_value(
                    right, values
                )
            elif gate[0] == "full_adder":
                _, sum_bit, carry, left, right, carry_in = gate
                total = (
                    int(self.literal_value(left, values))
                    + int(self.literal_value(right, values))
                    + int(self.literal_value(carry_in, values))
                )
                values[sum_bit] = bool(total & 1)
                values[carry] = total >= 2
            else:
                raise ValueError(f"unknown gate type {gate[0]}")

    def clauses_hold(self, values: Sequence[bool | None]) -> bool:
        return all(
            any(self.literal_value(literal, values) for literal in clause)
            for clause in self.clauses
        )


def spec_from_orbits(length: int, orbits: Sequence[Sequence[int]]) -> Dict:
    """Build the independent orbit PAF specification for an arbitrary odd length."""
    if not orbits or list(orbits[0]) != [0]:
        raise ValueError("the first orbit must be {0}")
    index = [0] * length
    for orbit_index, orbit in enumerate(orbits):
        for position in orbit:
            index[position] = orbit_index
    sizes = [len(orbit) for orbit in orbits]
    reps = [list(orbit)[0] for orbit in orbits[1:]]
    matrices = []
    constants = []
    r = len(orbits)
    for shift in reps:
        directed = [[0] * r for _ in range(r)]
        for position in range(length):
            directed[index[position]][index[(position + shift) % length]] += 1
        constants.append(sum(directed[q][q] for q in range(r)))
        matrix = [[0] * r for _ in range(r)]
        for q in range(r):
            for q2 in range(q + 1, r):
                matrix[q][q2] = directed[q][q2] + directed[q2][q]
                matrix[q2][q] = matrix[q][q2]
        matrices.append(matrix)
    return {
        "r": r,
        "sizes": sizes,
        "reps": reps,
        "num_reps": len(reps),
        "const": constants,
        "W": matrices,
        "orbits": [list(orbit) for orbit in orbits],
        "idx": index,
    }


def singleton_spec(length: int) -> Dict:
    return spec_from_orbits(length, [[position] for position in range(length)])


def paf_from_spec(spec: Dict, values: Sequence[int], index: int) -> int:
    total = spec["const"][index]
    matrix = spec["W"][index]
    for q in range(spec["r"]):
        for q2 in range(q + 1, spec["r"]):
            total += matrix[q][q2] * values[q] * values[q2]
    return total


@dataclass
class OrbitModel:
    length: int
    spec: Dict
    builder: CNFBuilder
    za: List[int]
    zb: List[int]
    wa: Dict[Tuple[int, int], int]
    wb: Dict[Tuple[int, int], int]
    paf_bits: List[List[int]]
    row_a_bits: List[int]
    row_b_bits: List[int]
    paf_targets: List[int]
    direct_pb_obstructions: List[Dict]
    pair_count: int

    def semantic_value(self, za_values: Sequence[int], zb_values: Sequence[int]) -> bool:
        if len(za_values) != self.spec["r"] or len(zb_values) != self.spec["r"]:
            raise ValueError("wrong orbit assignment length")
        if za_values[0] != 0 or zb_values[0] != 0:
            return False
        xa = [1 - 2 * value for value in za_values]
        xb = [1 - 2 * value for value in zb_values]
        row_a = sum(size * value for size, value in zip(self.spec["sizes"], xa))
        row_b = sum(size * value for size, value in zip(self.spec["sizes"], xb))
        if row_a not in (-1, 1) or row_b not in (-1, 1):
            return False
        return all(
            paf_from_spec(self.spec, xa, index) + paf_from_spec(self.spec, xb, index)
            == -2
            for index in range(self.spec["num_reps"])
        )

    def canonical_cnf_value(
        self, za_values: Sequence[int], zb_values: Sequence[int]
    ) -> Tuple[bool, List[bool | None]]:
        values: List[bool | None] = [None] * (self.builder.num_vars + 1)
        values[self.builder.false] = False
        for variable, value in zip(self.za, za_values):
            values[variable] = bool(value)
        for variable, value in zip(self.zb, zb_values):
            values[variable] = bool(value)
        self.builder.extend(values)
        if any(value is None for value in values[1:]):
            raise ValueError("CNF has an undefined auxiliary variable")
        return self.builder.clauses_hold(values), values

    @staticmethod
    def bits_value(bits: Sequence[Literal], values: Sequence[bool | None]) -> int:
        return sum(
            (1 << bit) * int(CNFBuilder.literal_value(signal, values))
            for bit, signal in enumerate(bits)
        )

    def audit_extension(
        self,
        za_values: Sequence[int],
        zb_values: Sequence[int],
        values: Sequence[bool | None],
    ) -> None:
        """Check every generated XOR and PB output against independent arithmetic."""
        for pair, variable in self.wa.items():
            expected = bool(za_values[pair[0]] ^ za_values[pair[1]])
            if bool(values[variable]) != expected:
                raise AssertionError(f"a-XOR mismatch at orbit pair {pair}")
        for pair, variable in self.wb.items():
            expected = bool(zb_values[pair[0]] ^ zb_values[pair[1]])
            if bool(values[variable]) != expected:
                raise AssertionError(f"b-XOR mismatch at orbit pair {pair}")
        for index, matrix in enumerate(self.spec["W"]):
            expected = sum(
                matrix[q][q2]
                * (
                    (za_values[q] ^ za_values[q2])
                    + (zb_values[q] ^ zb_values[q2])
                )
                for q in range(self.spec["r"])
                for q2 in range(q + 1, self.spec["r"])
            )
            actual = self.bits_value(self.paf_bits[index], values)
            if actual != expected:
                raise AssertionError(f"PAF PB sum mismatch at representative {index}")
        expected_row_a = sum(
            size * value for size, value in zip(self.spec["sizes"], za_values)
        )
        expected_row_b = sum(
            size * value for size, value in zip(self.spec["sizes"], zb_values)
        )
        if self.bits_value(self.row_a_bits, values) != expected_row_a:
            raise AssertionError("row-a PB sum mismatch")
        if self.bits_value(self.row_b_bits, values) != expected_row_b:
            raise AssertionError("row-b PB sum mismatch")

    def metadata(self) -> Dict:
        return {
            "length": self.length,
            "orbit_count": self.spec["r"],
            "shift_representatives": self.spec["num_reps"],
            "pair_xor_count_per_sequence": self.pair_count,
            "primary_orbit_variables": 2 * self.spec["r"],
            "num_variables": self.builder.num_vars,
            "num_clauses": len(self.builder.clauses),
            "row_zero_normalization": "za[0] = zb[0] = 0",
            "xor_encoding": "four-clause exact Tseitin XOR",
            "pb_encoding": (
                "carry-save weighted-bit reduction followed by exact full-adder "
                "ripple sum; all output bits constrained"
            ),
            "row_sum_encoding": "weighted z sum in {(L-1)/2, (L+1)/2}",
            "paf_encoding": "sum W_s(q,q')*(wa+wb) = const_s+sum(W_s)+1",
            "paf_targets": self.paf_targets,
            "direct_pb_obstructions": self.direct_pb_obstructions,
        }


def build_orbit_model(length: int, spec: Dict) -> OrbitModel:
    if length % 2 == 0:
        raise ValueError("Legendre row-sum encoding needs odd length")
    if sum(spec["sizes"]) != length:
        raise ValueError("orbit sizes do not cover the length")
    builder = CNFBuilder()
    r = spec["r"]
    za = [builder.new_var(f"za_{q}") for q in range(r)]
    zb = [builder.new_var(f"zb_{q}") for q in range(r)]
    builder.add_unit(-za[0])
    builder.add_unit(-zb[0])

    used_pairs = sorted(
        {
            (q, q2)
            for matrix in spec["W"]
            for q in range(r)
            for q2 in range(q + 1, r)
            if matrix[q][q2]
        }
    )
    wa = {
        pair: builder.add_xor(za[pair[0]], za[pair[1]], f"wa_{pair[0]}_{pair[1]}")
        for pair in used_pairs
    }
    wb = {
        pair: builder.add_xor(zb[pair[0]], zb[pair[1]], f"wb_{pair[0]}_{pair[1]}")
        for pair in used_pairs
    }

    targets: List[int] = []
    paf_bits: List[List[int]] = []
    direct_pb_obstructions: List[Dict] = []
    for index, matrix in enumerate(spec["W"]):
        terms = []
        coefficient_sum = 0
        for pair in used_pairs:
            coefficient = matrix[pair[0]][pair[1]]
            if coefficient:
                terms.append((coefficient, wa[pair]))
                terms.append((coefficient, wb[pair]))
                coefficient_sum += coefficient
        bits, total = builder.weighted_sum(terms, f"paf_{index}")
        target = spec["const"][index] + coefficient_sum + 1
        if total != 2 * coefficient_sum:
            raise AssertionError("unexpected PAF weighted sum")
        if target > total:
            direct_pb_obstructions.append(
                {
                    "representative_index": index,
                    "shift": spec["reps"][index],
                    "diagonal_constant": spec["const"][index],
                    "coefficient_sum_per_sequence": coefficient_sum,
                    "required_weighted_xor_sum": target,
                    "maximum_weighted_xor_sum": total,
                    "shortfall": target - total,
                }
            )
        builder.force_value(bits, target)
        targets.append(target)
        paf_bits.append(bits)

    row_low = (length - 1) // 2
    row_high = (length + 1) // 2
    bits_a, _ = builder.weighted_sum(
        list(zip(spec["sizes"], za)), "row_a"
    )
    bits_b, _ = builder.weighted_sum(
        list(zip(spec["sizes"], zb)), "row_b"
    )
    builder.force_one_of_two(bits_a, row_low, row_high)
    builder.force_one_of_two(bits_b, row_low, row_high)
    return OrbitModel(
        length=length,
        spec=spec,
        builder=builder,
        za=za,
        zb=zb,
        wa=wa,
        wb=wb,
        paf_bits=paf_bits,
        row_a_bits=bits_a,
        row_b_bits=bits_b,
        paf_targets=targets,
        direct_pb_obstructions=direct_pb_obstructions,
        pair_count=len(used_pairs),
    )


def build_lp333_model(subgroup_id: int) -> Tuple[OrbitModel, Dict]:
    subgroup, record = subgroup_by_id(subgroup_id)
    spec = spec_from_orbits(L, orbits_on_ZL(subgroup, L))
    return build_orbit_model(L, spec), record


def build_singleton_model(length: int) -> OrbitModel:
    return build_orbit_model(length, singleton_spec(length))


def write_dimacs(
    builder: CNFBuilder, path: Path, split_unit_clauses: bool = False
) -> Dict:
    """Write DIMACS, optionally replacing each unit by an exact two-clause gadget.

    ``(l)`` is replaced with ``(l v e) & (l v -e)`` for a fresh variable ``e``.
    This is existentially equivalent to the unit clause, but keeps a proof
    checker from terminating during input-unit preprocessing before it reads the
    solver's DRAT trace.
    """
    unit_positions = [
        index for index, clause in enumerate(builder.clauses) if len(clause) == 1
    ]
    extra_variables = len(unit_positions) if split_unit_clauses else 0
    clause_count = (
        len(builder.clauses) + len(unit_positions)
        if split_unit_clauses
        else len(builder.clauses)
    )
    split_map = []
    with path.open("w", encoding="ascii", newline="\n") as handle:
        handle.write(f"p cnf {builder.num_vars + extra_variables} {clause_count}\n")
        next_mask = builder.num_vars + 1
        for index, clause in enumerate(builder.clauses):
            if split_unit_clauses and len(clause) == 1:
                literal = clause[0]
                handle.write(f"{literal} {next_mask} 0\n")
                handle.write(f"{literal} {-next_mask} 0\n")
                split_map.append(
                    {
                        "source_clause_index": index + 1,
                        "source_literal": literal,
                        "mask_variable": next_mask,
                    }
                )
                next_mask += 1
            else:
                handle.write(" ".join(str(literal) for literal in clause))
                handle.write(" 0\n")
    return {
        "num_variables": builder.num_vars + extra_variables,
        "num_clauses": clause_count,
        "split_unit_clauses": split_unit_clauses,
        "unit_split_count": len(split_map),
        "unit_split_map": split_map,
    }


def dimacs_sha256(builder: CNFBuilder, split_unit_clauses: bool = False) -> str:
    """Hash the deterministic DIMACS serialization without materializing a file."""
    unit_positions = [
        index for index, clause in enumerate(builder.clauses) if len(clause) == 1
    ]
    extra_variables = len(unit_positions) if split_unit_clauses else 0
    clause_count = (
        len(builder.clauses) + len(unit_positions)
        if split_unit_clauses
        else len(builder.clauses)
    )
    hasher = hashlib.sha256()

    def add_line(line: str) -> None:
        hasher.update(line.encode("ascii"))

    add_line(f"p cnf {builder.num_vars + extra_variables} {clause_count}\n")
    next_mask = builder.num_vars + 1
    for clause in builder.clauses:
        if split_unit_clauses and len(clause) == 1:
            literal = clause[0]
            add_line(f"{literal} {next_mask} 0\n")
            add_line(f"{literal} {-next_mask} 0\n")
            next_mask += 1
        else:
            add_line(" ".join(str(literal) for literal in clause) + " 0\n")
    return hasher.hexdigest()


def direct_is_legendre_pair(a: Sequence[int], b: Sequence[int]) -> bool:
    if len(a) != len(b) or len(a) % 2 == 0:
        return False
    length = len(a)
    if sum(a) not in (-1, 1) or sum(b) not in (-1, 1):
        return False
    return all(
        sum(a[i] * a[(i + shift) % length] for i in range(length))
        + sum(b[i] * b[(i + shift) % length] for i in range(length))
        == -2
        for shift in range(1, length)
    )


def find_small_legendre_pair(length: int) -> Tuple[List[int], List[int]]:
    if length > 11:
        raise ValueError("this deterministic control search is intentionally tiny")
    for bits_a in product((0, 1), repeat=length - 1):
        za = (0,) + bits_a
        a = [1 - 2 * value for value in za]
        for bits_b in product((0, 1), repeat=length - 1):
            zb = (0,) + bits_b
            b = [1 - 2 * value for value in zb]
            if direct_is_legendre_pair(a, b):
                return a, b
    raise AssertionError(f"no normalized small Legendre pair at length {length}")


def random_equivalence_audit(
    model: OrbitModel, samples: int, seed: int
) -> Dict:
    rng = random.Random(seed)
    semantic_true = 0
    cnf_true = 0
    for _ in range(samples):
        za = [0] + [rng.randrange(2) for _ in range(model.spec["r"] - 1)]
        zb = [0] + [rng.randrange(2) for _ in range(model.spec["r"] - 1)]
        semantic = model.semantic_value(za, zb)
        cnf, values = model.canonical_cnf_value(za, zb)
        model.audit_extension(za, zb, values)
        if semantic != cnf:
            raise AssertionError(
                f"semantic/CNF mismatch for length {model.length}: {za!r}, {zb!r}"
            )
        semantic_true += int(semantic)
        cnf_true += int(cnf)
    return {
        "kind": "random-orbit-model-equivalence",
        "samples": samples,
        "seed": seed,
        "semantic_true_count": semantic_true,
        "canonical_cnf_true_count": cnf_true,
        "xor_values_checked": samples * 2 * model.pair_count,
        "pb_sum_outputs_checked": samples * (model.spec["num_reps"] + 2),
        "result": "PASS",
    }


def exhaustive_small_audit(model: OrbitModel) -> Dict:
    r = model.spec["r"]
    if 2 * (r - 1) > 16:
        raise ValueError("control model too large for exhaustive audit")
    checked = 0
    satisfying = 0
    for bits_a in product((0, 1), repeat=r - 1):
        za = (0,) + bits_a
        for bits_b in product((0, 1), repeat=r - 1):
            zb = (0,) + bits_b
            semantic = model.semantic_value(za, zb)
            cnf, _ = model.canonical_cnf_value(za, zb)
            if semantic != cnf:
                raise AssertionError(f"small-model mismatch: {za!r}, {zb!r}")
            checked += 1
            satisfying += int(semantic)
    return {
        "kind": "exhaustive-small-model-equivalence",
        "assignments_checked": checked,
        "satisfying_assignments": satisfying,
        "result": "PASS",
    }


def transformation_truth_table_audit() -> Dict:
    """Exhaustively exercise the standalone XOR/equality/range transformations."""
    equality = CNFBuilder()
    x = equality.new_var("x")
    y = equality.new_var("y")
    z = equality.new_var("z")
    xor = equality.add_xor(x, y, "x_xor_y")
    bits, _ = equality.weighted_sum([(3, xor), (2, z), (1, x)], "equality")
    equality.force_value(bits, 4)

    for xv, yv, zv in product((0, 1), repeat=3):
        values: List[bool | None] = [None] * (equality.num_vars + 1)
        values[equality.false] = False
        values[x], values[y], values[z] = bool(xv), bool(yv), bool(zv)
        equality.extend(values)
        expected = 3 * (xv ^ yv) + 2 * zv + xv == 4
        if equality.clauses_hold(values) != expected:
            raise AssertionError("XOR/PB equality truth-table mismatch")

    range_builder = CNFBuilder()
    p = range_builder.new_var("p")
    q = range_builder.new_var("q")
    r = range_builder.new_var("r")
    range_bits, _ = range_builder.weighted_sum([(1, p), (2, q), (4, r)], "range")
    range_builder.force_one_of_two(range_bits, 3, 4)
    for pv, qv, rv in product((0, 1), repeat=3):
        values = [None] * (range_builder.num_vars + 1)
        values[range_builder.false] = False
        values[p], values[q], values[r] = bool(pv), bool(qv), bool(rv)
        range_builder.extend(values)
        expected = pv + 2 * qv + 4 * rv in (3, 4)
        if range_builder.clauses_hold(values) != expected:
            raise AssertionError("PB two-value range truth-table mismatch")

    for literal_value in (False, True):
        extensions = [
            (literal_value or mask) and (literal_value or not mask)
            for mask in (False, True)
        ]
        if any(extensions) != literal_value:
            raise AssertionError("unit-splitting equivalence mismatch")
    return {
        "kind": "exhaustive-xor-and-pb-transformation-truth-tables",
        "xor_equality_assignments": 8,
        "two_value_range_assignments": 8,
        "unit_split_assignment_extensions": 4,
        "result": "PASS",
    }


def orbit_spec_audit(subgroup_id: int, samples: int, seed: int) -> Dict:
    """Cross-check orbit PAF coefficients against direct length-333 PAF values."""
    subgroup, record = subgroup_by_id(subgroup_id)
    spec = spec_from_orbits(L, orbits_on_ZL(subgroup, L))
    rng = random.Random(seed)
    index = spec["idx"]
    checked = 0
    for _ in range(samples):
        values = [rng.choice((-1, 1)) for _ in range(spec["r"])]
        sequence = [values[index[position]] for position in range(L)]
        for matrix_index, shift in enumerate(spec["reps"]):
            direct = sum(
                sequence[position] * sequence[(position + shift) % L]
                for position in range(L)
            )
            encoded = paf_from_spec(spec, values, matrix_index)
            if direct != encoded:
                raise AssertionError(
                    f"orbit PAF mismatch for id {subgroup_id}, shift {shift}"
                )
            checked += 1
    return {
        "kind": "direct-full-length-orbit-PAF-audit",
        "subgroup_id": subgroup_id,
        "subgroup_order": len(record["elements"]),
        "random_orbit_assignments": samples,
        "representative_PAFs_checked": checked,
        "result": "PASS",
    }
