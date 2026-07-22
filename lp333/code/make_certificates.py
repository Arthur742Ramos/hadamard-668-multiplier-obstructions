#!/usr/bin/env python3
"""Emit a single consolidated certificate for every family DECLARED IMPOSSIBLE,
bundling the exact certifying evidence for each, plus the OPEN list.  This is the
machine-readable 'certificate for every family declared impossible' deliverable.
"""
import json
import os

HERE = os.path.dirname(__file__)
RES = os.path.join(HERE, "..", "results")
CERT = os.path.join(HERE, "..", "certificates")


def load(p, d=None):
    try:
        return json.load(open(p))
    except FileNotFoundError:
        return d


def main():
    master = load(os.path.join(RES, "master_status.json"))
    nc = {r["id"]: r for r in load(os.path.join(RES, "necessary_conditions.json"), [])}
    obstr = load(os.path.join(CERT, "obstruction_certificates.json"))

    families = []
    for e in master["families"]:
        sid = e["id"]
        rec = {"id": sid, "order": e["order"], "r": e["r"],
               "reduction_mod9_order": e["reduction_mod9_order"],
               "reduction_mod37_order": e["reduction_mod37_order"],
               "generators": e["generators"], "status": e["status"],
               "label": e["label"], "method": e["method"]}
        if e["status"] != "IMPOSSIBLE":
            rec["note"] = "not exhausted within budget; no impossibility claimed"
            families.append(rec)
            continue
        m = e["method"]
        if m == "mod37_full_reduction_obstruction":
            rec["certificate"] = {
                "argument": "H reduces onto (Z/37)^*; 37-compression is constant on "
                            "the 36 nonzero residues, so A~(k)=a~_0-c is an integer and "
                            "(a~_0-c)^2+(b~_0-d)^2=668 is a sum of two squares = 668 (impossible).",
                "core_fact": "668 is not a sum of two integer squares",
                "source": "certificates/obstruction_certificates.json",
            }
        elif m == "rowsum_modular_obstruction":
            rec["certificate"] = {
                "argument": "Row sum R = sum_O |O| x_O (x_O = +/-1) can never equal +/-1: "
                            f"R mod {nc[sid]['rowsum_witness_modulus']} avoids +/-1 for all sign patterns.",
                "witness_modulus": nc[sid]["rowsum_witness_modulus"],
                "verification": "exhaustive modular DP over orbit-size residues",
                "source": "results/necessary_conditions.json",
            }
        elif m == "exact_meet_in_the_middle":
            det = load(os.path.join(RES, "mitm", f"id{sid}.json"), {})
            rec["certificate"] = {
                "argument": "Exhaustive meet-in-the-middle over all 2^(r-1) orbit-value "
                            "assignments (a_0=b_0=+1): no pair of PAF profiles sums to the "
                            "all -2 vector with both row sums +/-1.",
                "enumerated": det.get("enumerated"),
                "rowsum_valid_sequences": det.get("rowsum_ok"),
                "distinct_profiles": det.get("distinct_profiles"),
                "source": f"results/mitm/id{sid}.json",
            }
        elif m.startswith("exact_CP_SAT"):
            rec["certificate"] = {
                "argument": "Exact CP-SAT decision of the booleanized PAF system "
                            "returned INFEASIBLE; the deterministic model and verdict "
                            "are reproducible, but this JSON is not a proof trace.",
                "engine": m,
                "source": f"results/cpsat/ (id{sid} INFEASIBLE record)",
            }
        elif m == "phase2_value_set_9_compression_obstruction":
            rec["certificate"] = {
                "argument": "Value-set-restricted 9-compression: column sums lie in "
                            "the exact K37-invariant value set V; the compression "
                            "identity + LP force PAF_atilde(s)+PAF_btilde(s)=-74 "
                            "(s=1..8), row sums +-1, and squared norm 594; a complete "
                            "square-sum-pruned exhaustive search over V^9 finds no "
                            "compressed pair. Verified by a dependency-free standalone "
                            "verifier and (id8,id12) by CP-SAT/z3.",
                "source": e.get("certificate")
                          or "id12_phase2/results/general_compression_certificate.json",
            }
        families.append(rec)

    out = {
        "title": "Impossibility certificates for common-multiplier-invariant "
                 "Legendre pairs of length 333",
        "core_fact": obstr["core_fact"] if obstr else None,
        "summary": master["summary"],
        "families": families,
    }
    with open(os.path.join(CERT, "impossible_certificates.json"), "w") as f:
        json.dump(out, f, indent=2)
    imp = [r for r in families if r["status"] == "IMPOSSIBLE"]
    print("impossible families certified:", len(imp))
    print("open families:", [r["id"] for r in families if r["status"] == "OPEN"])
    print("wrote certificates/impossible_certificates.json")


if __name__ == "__main__":
    main()
