# LP(333) proof-carrying CNF phase

This directory supplies an independent SAT encoding of the orbit-level row-sum and PAF equations used by the earlier CP-SAT closures.

For an orbit value `x_Q=1-2z_Q`, the encoder defines `w_QR = z_Q XOR z_R` with four exact CNF clauses.  For every shift representative it encodes

`sum_{Q<R} W_s(Q,R) (w^a_QR + w^b_QR) = const_s + sum W_s + 1`.

Its weighted sums are exact carry-save/full-adder circuits; their output bits are fixed to the target.  Each row condition is encoded exactly as `sum |Q| z_Q in {166,167}`.  Fixing orbit zero to `+1` is satisfiability preserving because either sequence can be globally negated independently.

Each `*_unit_split.cnf` proof input is an exact existential reformulation of the corresponding base CNF: every unit `(l)` is replaced by `(l v e)` and `(l v -e)` for a fresh private `e`.  This prevents a checker from short-circuiting during input-unit preprocessing when a nontrivial DRAT trace is needed.  The complete fresh-variable mapping is saved beside each proof CNF in `cnf/*_unit_split_map.json`.  A few families have a stronger direct PB upper-bound contradiction; those are explicitly labeled `input_cnf_trivial_unsat` and carry the numeric bound in the manifest rather than being described as trace-checked.

## Results

| id | orbit variables/sequence | solver | independently checked evidence |
|---:|---:|---|---|
| 11 | 65 | UNSAT | VERIFIED / input_cnf_trivial_unsat |
| 13 | 41 | UNSAT | VERIFIED / drat_trace_verified |
| 14 | 41 | UNSAT | VERIFIED / drat_trace_verified |
| 15 | 50 | UNSAT | VERIFIED / input_cnf_trivial_unsat |
| 19 | 35 | UNSAT | VERIFIED / input_cnf_trivial_unsat |
| 20 | 27 | UNSAT | VERIFIED / drat_trace_verified |
| 21 | 23 | UNSAT | VERIFIED / drat_trace_verified |
| 22 | 23 | UNSAT | VERIFIED / drat_trace_verified |
| 23 | 25 | UNSAT | VERIFIED / input_cnf_trivial_unsat |
| 24 | 20 | UNSAT | VERIFIED / input_cnf_trivial_unsat |
| 28 | 15 | UNSAT | VERIFIED / input_cnf_trivial_unsat |

### Direct PB upper-bound certificates

For each row below, all weighted XOR variables are Boolean, so the required sum cannot exceed the recorded maximum:
* id 11, shift 111: required `334`, maximum `222` (shortfall `112`).
* id 15, shift 111: required `334`, maximum `222` (shortfall `112`).
* id 19, shift 111: required `334`, maximum `222` (shortfall `112`).
* id 23, shift 111: required `334`, maximum `222` (shortfall `112`).
* id 24, shift 111: required `334`, maximum `222` (shortfall `112`).
* id 28, shift 111: required `334`, maximum `222` (shortfall `112`).

Externally checked UNSAT evidence: **[11, 13, 14, 15, 19, 20, 21, 22, 23, 24, 28]**.

The checker is the locally built upstream `drat-trim`; its per-instance log must contain `s VERIFIED`.  Rows marked `drat_trace_verified` were checked against the saved DRAT trace.  Rows marked `input_cnf_trivial_unsat` have a stronger direct PB upper-bound certificate in the base CNF and manifest.  CNFs, ASCII DRAT traces, logs, and SHA-256 hashes are listed in `manifest.json` and `hashes/sha256sums.txt`.

## Audits and controls

* `audits/positive_controls.json` records exhaustive end-to-end equivalence checks for normalized length-5 (256 assignments) and length-7 (4096 assignments) Legendre-pair controls, including SAT solver witnesses.
* The same file records exhaustive truth tables for the standalone XOR/PB equality and two-value PB-range transformations.
* Each `audits/lp333_id*.json` records random direct full-length PAF checks and canonical-CNF versus direct-model checks.
* `audit_rebuild.py` independently reconstructs orbit matrices and the full base/proof DIMACS serializations; its hash comparison is saved in `audits/independent_rebuild_audit.json`.
* `manifest.json` also contains a DIMACS-header/terminator audit for every saved base, proof, and positive-control CNF.
* `verify_artifacts.py` rechecks the saved hashes, checker markers, PB-bound records, controls, and DIMACS-audit status without rerunning CaDiCaL; `--full` reruns `drat-trim` on every saved trace, checks its exact marker/return behavior and checker-binary pin, and verifies rejection of a deliberately bogus proof.
* `independent_audit.py` is a standard-library-only implementation that independently reconstructs subgroup orbits, PAF coefficients, the deterministic CNF serialization, and sampled CNF semantics.
* `refresh_hashes.py` refreshes `hashes/sha256sums.txt` after verification-only artifacts change, without rerunning a solver.

No status is asserted as proof-carrying unless its own `external_check` field is `VERIFIED`; a missing trace or checker result is reported explicitly rather than promoted to an exclusion.

## Reproduction

From `lp333/`, run `proof_phase2/run_proofs.py`.  It requires `cadical` and the bundled `proof_phase2/tools/drat-trim/drat-trim`; run `make -C proof_phase2/tools/drat-trim` if the checker binary is not already built.  A direct checker invocation is `proof_phase2/tools/drat-trim/drat-trim proof_phase2/cnf/lp333_id13_unit_split.cnf proof_phase2/proofs/lp333_id13_unit_split.drat -I`.

## Publication hardening

* Dependency pins: `dependency_pins.json` (PASS); this pins `core.py`, `search_common.py`, subgroup data, and the checker binary.
* Standalone audit: `audits/independent_standalone_audit.json` (PASS).
* Full checker rerun: `audits/full_validation.json` (PASS); it reruns every trace and confirms rejection of a bogus empty proof.
* Full-checker logs are volatile and excluded from the immutable SHA-256 list; each log and the bogus-proof control is instead content-hashed inside the pinned full-validation record.
