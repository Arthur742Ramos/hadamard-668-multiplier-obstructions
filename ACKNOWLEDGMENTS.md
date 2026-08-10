# Acknowledgments and contribution provenance

This project benefits from independent mathematical checks and community
extensions. The following contributions are incorporated in the repository's
current 25/30 fixed-multiplier classification.

- **Josh Arnold** ([@josh-sophon](https://github.com/josh-sophon)) contributed
  the CRT mod-8 proof, verifier, certificate, and repository integration that
  exclude IDs 9 and 10 in
  [PR #4](https://github.com/Arthur742Ramos/hadamard-668-multiplier-obstructions/pull/4).
- **Eric Alcaide** ([@hypnopump](https://github.com/hypnopump)) independently
  reported the IDs 9 and 10 exclusions in
  [issue #3](https://github.com/Arthur742Ramos/hadamard-668-multiplier-obstructions/issues/3),
  with a mod-24 proof, independent verification scripts, and a Lean 4
  formalization. The repository's mod-8 report links this corroborating work.
- **Claude**, an AI research partner working with **Patrick White**, contributed
  the ID-2 congruence-kernel fibre obstruction in
  [issue #2](https://github.com/Arthur742Ramos/hadamard-668-multiplier-obstructions/issues/2).
  It is integrated as the independently checked `id2_congruence_kernel` proof
  module.
- **Benedek “Ben” Blackthorn**
  ([@benblackthorn](https://github.com/benblackthorn)) independently obtained
  the ID-2 obstruction and developed a broader prime-square and affine-symmetry
  theorem with Lean 4 verification, archived at
  [doi:10.5281/zenodo.21779001](https://doi.org/10.5281/zenodo.21779001).
- **Dennison Bertram** coordinated the AI-assisted research process that
  produced and shared the elementary 222-term single-shift observation closing
  ID 7. In accordance with the submitted note, this credit records his
  coordination and communication of the result, not a claim of personal
  derivation, priority, or novelty. The repository independently rederived the
  argument and added an exact `PAF(111)` minimum and deterministic certificate.

Credit here records the provenance of these specific contributions; it does
not imply authorship of unrelated repository results.
