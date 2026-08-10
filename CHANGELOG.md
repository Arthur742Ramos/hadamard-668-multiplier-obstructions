# Changelog

## Unreleased

- Exclude multiplier ID 7 with a shift-111 orbit count: 222 terms are forced
  positive, giving a one-row PAF lower bound of 111 (exact minimum 185).
- Exclude multiplier ID 2 with a shift-111 congruence-kernel fibre count; the
  stronger statement needs only one invariant row.
- Exclude common-multiplier IDs 9 and 10 with a CRT mod-8 calculation on the
  compressed autocorrelation.
- Set the classification at 25 impossible families, with open IDs
  0, 1, 3, 4, and 5; every order-6 family is now closed.
- Record contribution provenance for Josh Arnold, Eric Alcaide, Claude with
  Patrick White, Benedek “Ben” Blackthorn, and Dennison Bertram.

## 1.0.0 — 2026-07-22

- Prove analytically that the final order-9 multiplier family (`id12`) cannot
  contain a Legendre pair of length 333.
- Close every common multiplier subgroup of order at least 9.
- Record exact status for all 30 mod-3-compatible multiplier families:
  21 impossible and nine open.
- Provide checked DRAT traces or direct pseudo-Boolean certificates for the
  solver-assisted exclusions.
- Add fixed-field compression refinements and exhaustive symmetry-class
  censuses.
- Reconstruct and verify the known 64-modular order-668 construction while
  explicitly rejecting it as an exact Hadamard matrix.
