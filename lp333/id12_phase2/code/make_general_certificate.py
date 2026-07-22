#!/usr/bin/env python3
"""Assemble the generalized 9-compression certificate from cached results."""
import json, os
HERE=os.path.dirname(__file__); RES=os.path.join(HERE,"..","results")
CERTDIR=os.path.join(HERE,"..","..","certificates")
def main():
    gcres=json.load(open(os.path.join(RES,"general_compression.json")))
    fams={f["id"]:f for f in gcres["families"]}
    closed=sorted(sid for sid,f in fams.items() if f.get("verdict","").startswith("IMPOSSIBLE"))
    cert={
     "title":"Generalized value-set-restricted 9-compression obstruction for common-multiplier LP(333)",
     "family_independent_facts":{"compression_modulus":9,"PAF_sum_target_s_ne_0":-74,"forced_squared_norm":594,
       "derivation":"For L=333,m=9: PAF_atilde(s)=sum_{s'==s mod9}PAF_a(s') (37 shifts each); LP=>-74 (s!=0); sum_{s=0..8}PAF=(sum)^2 => squared norm 594."},
     "family_dependent_ingredient":"column-sum value set V (from K37-orbit sizes of Z_37); atilde_j in V.",
     "scope":"families trivial mod 9 (H={1}xK37; 9-compression columns are clean K37-invariant Z_37 blocks): ids 0,1,3,6,8,12.",
     "per_family":fams,"closed_impossible":closed,"newly_closed_vs_phase1_were_OPEN":[s for s in closed if s in (6,8)],
     "primary_target":12,
     "not_closed":{"0":"value set = all odd integers (free-odd); NOT closed -- feasible by stored witness",
                   "1":"value set = all odd integers (free-odd); NOT closed -- feasible by stored witness",
                   "3":"|V|=26, 95 square-multisets; enumeration exceeds budget -> undecided (open candidate)"},
     "verification":{"complete_exhaustive":"square-sum-pruned MITM over V^9; algorithm cross-validated on id12 by three engines.",
       "standalone_pure_stdlib":"general_verifier.py (dependency-free, positive control) => IMPOSSIBLE for id6,id8,id12; 'not closed' for id0,id1.",
       "cpsat_independent":"id8,id12 INFEASIBLE under CP-SAT with proven 594 cut."},
    }
    for name,key in (("id6_cpsat_long.json","id6_cpsat_long"),("general_crosscheck_cpsat.json","cpsat_results"),
                     ("freeodd_relaxation_witness.json","free_odd_witness_id0_id1")):
        p=os.path.join(RES,name)
        if os.path.exists(p): cert["verification"][key]=json.load(open(p))
    for outp in (os.path.join(RES,"general_compression_certificate.json"),
                 os.path.join(CERTDIR,"general_compression_certificate.json")):
        json.dump(cert,open(outp,"w"),indent=2); print("wrote",outp)
    print("closed IMPOSSIBLE:",closed,"| newly closed vs phase1:",cert["newly_closed_vs_phase1_were_OPEN"])
if __name__=="__main__": main()
