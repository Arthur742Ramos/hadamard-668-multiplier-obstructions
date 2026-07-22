# Research outcome: Hadamard order 668

## Bottom line

No real Hadamard matrix of order 668 was constructed. The order remains open,
and no 668-by-668 CSV passed the exact integer verifier.

The research did produce a defensible standalone result about the strongest
multiplier-symmetric Legendre-pair route.

## Main theorem-level result

Let `H` be a common multiplier subgroup for a Legendre pair of length 333.
Among the 30 subgroups compatible with the initial mod-3 obstruction:

- 21 are proved impossible;
- all 19 subgroups of order at least 9 are impossible;
- the 9 remaining open subgroups have orders at most 6.

The last order-9 case, id12, has a short analytic proof. Its 9-compression values
must lie in

```text
{+/-1, +/-17, +/-19, +/-35, +/-37}.
```

The LP equations force exactly two magnitude-17 entries, one `+17` and one
`-17`, in a single compressed sequence; the other compressed sequence is all
`+/-1`. At the shift joining those two positions, the combined periodic
autocorrelation is at most `-240`, contradicting the required `-74`.

This closes id12 without relying on solver enumeration. Exhaustive enumeration,
CP-SAT, and z3 independently confirm it. The same value-set compression also
closes previously open subgroups id6 and id8.

## Proof package

- `lp333/report.md` — full classification and scope.
- `lp333/id12_phase2/report.md` — analytic id12 proof.
- `lp333/proof_phase2/` — DIMACS, DRAT traces, direct PB certificates,
  independent audits, positive controls, and full verification.
- `lp333/results/master_status.json` — machine-readable 21/30 status.

The top-level `lp333/code/run_all.sh` regenerates phase 1, phase 2, proof checks,
consolidated status, certificates, and the final manifest.

## Secondary potentially publishable result

`compression_theorem/theorem_note.md` formulates compression obstructions in
cyclotomic fixed fields. The basic compression/two-square obstruction is prior
art. The potentially new pieces are:

- a totally-real fixed-field sum-of-two-squares condition;
- an explicit real-quadratic index-2 norm-form obstruction;
- 139 forbidden fixed-symmetry classes among 428 cases with odd `L<=1200`.

Novelty for these refinements still requires specialist literature review.
Nothing in this note proves global nonexistence of a Legendre pair at a new
length.

## Publication assessment

The analytic id12 theorem plus the proof-carrying classification is suitable for
a short computational-designs note after external expert review. The fixed-field
refinement could strengthen that note if its novelty survives specialist review.

The work must be presented as a classification of multiplier-invariant
families, not as a solution of the Hadamard order-668 problem.
