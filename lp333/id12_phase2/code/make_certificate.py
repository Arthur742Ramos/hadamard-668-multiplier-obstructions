#!/usr/bin/env python3
"""
Assemble the final machine-readable impossibility certificate for id12 and run
the standalone verifier programmatically to embed its per-step PASS record.
Writes:
  id12_phase2/results/id12_impossible_certificate.json
  lp333/certificates/id12_impossible_certificate.json   (project-level copy)
"""
import json
import os
import io
import contextlib

HERE = os.path.dirname(__file__)
RES = os.path.join(HERE, "..", "results")
CERTDIR = os.path.join(HERE, "..", "..", "certificates")

import standalone_verifier as sv


def run_verifier():
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ok = sv.main()
    # recompute structured results by calling the (deterministic) checks directly
    g_ok, H, K = sv.check_group()
    sizes = sv.k37_orbit_sizes(set(K))
    V = sv.value_set(sizes)
    id_ok = sv.compression_identity_exact()
    sn_ok = sv.squared_norm_identity_exact()
    msol = sv.square_multisets(V)
    fs_ok, fs = sv.forced_structure_lemma()
    an_ok, an = sv.analytic_single_shift_bound()
    anc = sv.analytic_bound_numeric_confirmation()
    feasible, wit, nseq = sv.decide_compressed(V, target_paf=-74,
                                               rowsums=(-1, 1), sqnorm_total=594)
    return {
        "overall_pass": bool(ok),
        "group_id12_from_gens_10_46": H,
        "K37": K,
        "k37_orbit_sizes": sizes,
        "value_set_V": V,
        "compression_identity_exact": bool(id_ok),
        "squared_norm_identity_exact": bool(sn_ok),
        "forced_squared_norm": 1 + 1 - 8 * (-74),
        "square_multisets_594": msol,
        "square_multiset_unique_16x1_2x289": (msol == [{1: 16, 289: 2}]),
        "forced_structure_2_0": {"ok": bool(fs_ok), **fs},
        "primary_analytic_proof": {"ok": bool(an_ok), **an},
        "analytic_numeric_confirmation": anc,
        "independent_exhaustive_feasible": feasible,
        "independent_exhaustive_pruned_sequences": nseq,
        "transcript": buf.getvalue(),
    }


def main():
    cert = {
        "title": "Impossibility certificate: id12-invariant Legendre pair of length 333",
        "context": {
            "L": 333, "hadamard_order": 668,
            "family": "id12 = <10,46> in (Z/333)^*, order 9",
            "structure": ("trivial mod 9; image mod 37 is the order-9 subgroup "
                          "K37 of (Z/37)^* (index-4, quartic cyclotomy)"),
            "prior_status": "OPEN (only order->=9 common-multiplier LP(333) family "
                            "left open after phase 1)",
            "new_status": "IMPOSSIBLE (proved)",
        },
        "theorem": (
            "No length-333 Legendre pair invariant under H=id12 exists. Hence a "
            "Hadamard matrix of order 668 cannot be built from an id12-invariant "
            "Legendre pair. (This does NOT resolve H(668) in general; it closes "
            "the last order->=9 multiplier-invariant family.)"),
        "proof_outline": [
            "Z_333 = Z_9 x Z_37 (CRT). H trivial mod 9, K37 (order 9) mod 37, so "
            "an H-invariant sequence a is a function a(c,d) constant on the "
            "K37-orbits of the Z_37 coordinate; those orbits are {0},C0,C1,C2,C3 "
            "of sizes 1,9,9,9,9.",
            "9-compression atilde_j = sum_t a_{j+9t} equals the column sums; each "
            "atilde_j = eps0 + 9(eps1+eps2+eps3+eps4), eps in {+-1}, so "
            "atilde_j in V = {+-1,+-17,+-19,+-35,+-37}.",
            "Compression identity PAF_atilde(s) = sum_{s'==s (mod 9)} PAF_a(s') "
            "(37 shifts s' per s). For an LP (PAF_a(s')+PAF_b(s') = -2, s'!=0) and "
            "s=1..8 this gives PAF_atilde(s)+PAF_btilde(s) = 37*(-2) = -74.",
            "Row sums: sum atilde = sum a = +-1 (LP), sum btilde = +-1.",
            "The identity sum_{s=0}^{8} PAF_x(s) = (sum x)^2 forces "
            "PAF_atilde(0)+PAF_btilde(0) = sum atilde^2 + sum btilde^2 = "
            "2 - 8*(-74) = 594. Over V-squares {1,289,361,1225,1369}, the ONLY "
            "18-term multiset summing to 594 is 16x1 + 2x289: exactly two columns "
            "have |value|=17, sixteen have |value|=1.",
            "Row sums then force the (2,0) structure: both big columns lie in one "
            "sequence, one = +17 (position p) and one = -17 (position q != p), its "
            "other 7 entries +-1; the OTHER sequence is nine +-1 entries. (A lone "
            "+-17 can never give row sum +-1, so the (1,1) split is impossible.)",
            "PRIMARY (analytic, no enumeration): evaluate the single shift "
            "s = (q-p) mod 9 (nonzero). PAF_atilde(s) = one big-big term "
            "atilde_p*atilde_q = 17*(-17) = -289 (unique, since 2s != 0 mod 9) + "
            "two big-small terms (each (+-17)*(+-1) <= +17) + six small-small "
            "terms (each (+-1)*(+-1) <= +1), so PAF_atilde(s) <= -289+34+6 = -249. "
            "And PAF_btilde(s) <= 9 (nine +-1 products). Hence "
            "PAF_atilde(s)+PAF_btilde(s) <= -240 < -74, contradicting the required "
            "-74. (Term structure verified for all 72 distinct (p,q); the true "
            "maximum of PAF_atilde(q-p) is -251, so the bound holds with room.)",
            "INDEPENDENT CONFIRMATION: an exhaustive square-sum-pruned search over "
            "all such (atilde,btilde) finds NO pair with PAF-sum -74 for all "
            "s=1..8 (0 of 2,540,160). Same conclusion, no shared logic.",
        ],
        "primary_proof": "analytic single-shift contradiction (no pair enumeration)",
        "key_new_ingredient": (
            "The exact K37-invariance value-set restriction atilde_j in V. A naive "
            "9-compression that treats column sums as free odd integers admits 842 "
            "distinct 18-square multisets summing to 594 and is NOT closed; "
            "restricting to V leaves the unique 16x1+2x289 multiset, which is "
            "infeasible. This is why prior work (which did not run a "
            "value-set-restricted 9-compression) left id12 open."),
        "symmetry_audit": (
            "Neither proof uses symmetry breaking. The PRIMARY analytic argument "
            "picks a single canonical shift s=q-p and bounds one PAF value, using "
            "only the forced structure -- no orbit quotient. The independent "
            "exhaustive confirmation over 2,540,160 compressed pairs is likewise "
            "complete and unquotiented. (Symmetries -- Z_9 column rotation, "
            "(Z/9)^* column scaling, the Z_4 cyclotomic rotation, negation and "
            "A<->B swap -- all exist but are deliberately not relied upon.)"),
        "decision_engines": {},
        "standalone_verifier": None,
        "discrepancy_with_prior_free_odd_relaxation": {
            "free_odd_18square_multisets_summing_to_594": 842,
            "V_restricted_multisets": 1,
            "V_restricted_multiset": {"1": 16, "289": 2},
        },
    }
    # pull engine decisions from master_certificate.json
    mc_path = os.path.join(RES, "master_certificate.json")
    if os.path.exists(mc_path):
        mc = json.load(open(mc_path))
        cert["decision_engines"] = mc.get("decisions", {})
        cert["all_engines_agree_infeasible"] = mc.get("all_engines_agree_infeasible")
    # embed compression cross-verification
    cvp = os.path.join(RES, "compression_verification.json")
    if os.path.exists(cvp):
        cert["compression_cross_verification"] = json.load(open(cvp))
    # run standalone verifier
    cert["standalone_verifier"] = run_verifier()

    os.makedirs(CERTDIR, exist_ok=True)
    for outp in (os.path.join(RES, "id12_impossible_certificate.json"),
                 os.path.join(CERTDIR, "id12_impossible_certificate.json")):
        with open(outp, "w") as f:
            json.dump(cert, f, indent=2)
        print("wrote", outp)
    print("\nstandalone verifier overall_pass:",
          cert["standalone_verifier"]["overall_pass"])
    print("engines agree infeasible:", cert.get("all_engines_agree_infeasible"))


if __name__ == "__main__":
    main()
