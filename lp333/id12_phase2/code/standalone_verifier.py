#!/usr/bin/env python3
"""
STANDALONE, DEPENDENCY-FREE verifier of the impossibility of an id12-invariant
Legendre pair of length L=333 (Hadamard order 668).  Pure Python standard
library; imports nothing from the rest of the project.

Every step is a DETERMINISTIC finite check (no random sampling):

  * the group H = id12 is generated on the fly from <10, 46> mod 333 and its
    defining properties are checked;
  * the K37-orbit sizes of Z_37 are computed;
  * the compression identity  PAF_atilde(s) = sum_{s'==s (mod 9)} PAF_a(s')  is
    proved by comparing the exact integer coefficient matrices of the two
    quadratic forms over the 333 sequence variables (not by random testing);
  * the identity  sum_{s=0..8} PAF_x(s) = (sum x)^2  is proved the same way;
  * the column-sum value set V is the exact reachable set from the orbit sizes;
  * the forced squared norm 594 gives the UNIQUE square-multiset {16x1, 2x289},
    and with the row sums this forces the (2,0) structure: one compressed
    sequence has +17 (at position p) and -17 (at position q != p) and seven +-1
    entries, the other is nine +-1 entries;
  * PRIMARY PROOF -- an analytic single-shift contradiction (NO pair
    enumeration): at the shift s = (q - p) mod 9, PAF_atilde(s) decomposes into
    one big-big term (= -289), two big-small terms (<= +17 each) and six
    small-small terms (<= +1 each), so PAF_atilde(s) <= -249; and PAF_btilde(s)
    <= 9; hence the compression requirement PAF_atilde(s)+PAF_btilde(s) = -74 is
    violated (the actual value is <= -240).  The term-count structure is verified
    for all 72 distinct (p,q);
  * the same fact is INDEPENDENTLY confirmed by a complete square-sum-pruned
    exhaustive decision over V^9;  a POSITIVE CONTROL exercises that routine on
    satisfiable instances.

Prints PASS/FAIL per step and a final verdict.
"""
from math import gcd
import itertools

L = 333


# ---------------------------------------------------------------------------
# elementary primitives
# ---------------------------------------------------------------------------
def paf(x, s):
    n = len(x)
    return sum(x[i] * x[(i + s) % n] for i in range(n))


def compress9(a):
    """atilde_j = sum_{t=0}^{36} a_{j+9t}  (sum over the residue class j mod 9)."""
    return [sum(a[j + 9 * t] for t in range(37)) for j in range(9)]


def is_legendre_pair(a, b):
    n = len(a)
    if sum(a) not in (-1, 1) or sum(b) not in (-1, 1):
        return False
    return all(paf(a, s) + paf(b, s) == -2 for s in range(1, n))


# ---------------------------------------------------------------------------
# H = id12 generated from <10, 46> mod 333
# ---------------------------------------------------------------------------
def generate_subgroup(gens, mod=L):
    S = {1}
    frontier = [1]
    while frontier:
        x = frontier.pop()
        for g in gens:
            y = (x * g) % mod
            if y not in S:
                S.add(y); frontier.append(y)
    return S


def check_group():
    H = generate_subgroup([10, 46])
    ok = (len(H) == 9)
    for u in H:
        ok &= (gcd(u, L) == 1)
        for v in H:
            ok &= ((u * v) % L in H)          # closed under multiplication
    ok &= ({u % 9 for u in H} == {1})          # trivial mod 9
    K = {u % 37 for u in H}
    ok &= (len(K) == 9)                         # order-9 image mod 37
    for x in K:                                 # K is a subgroup of (Z/37)^*
        for y in K:
            ok &= ((x * y) % 37 in K)
    return ok, sorted(H), sorted(K)


def k37_orbit_sizes(K):
    seen = [False] * 37
    sizes = []
    for x in range(37):
        if seen[x]:
            continue
        o = set(); st = [x]
        while st:
            y = st.pop()
            if y in o:
                continue
            o.add(y)
            for h in K:
                st.append((h * y) % 37)
        for y in o:
            seen[y] = True
        sizes.append(len(o))
    return sorted(sizes)


# ---------------------------------------------------------------------------
# DETERMINISTIC identity checks via exact coefficient matrices
# ---------------------------------------------------------------------------
def compression_identity_exact():
    """Prove PAF_atilde(s) = sum_{s'==s (mod 9)} PAF_a(s') for every s by
    comparing the integer coefficient matrices C^{(s)} and D^{(s)} of the two
    quadratic forms in the 333 variables a_0..a_332 (ordered pairs (p,q))."""
    ok = True
    for s in range(9):
        # C^{(s)}[p][q] from PAF_atilde(s)=sum_j (sum_t a_{9t+j})(sum_u a_{9u+j+s})
        C = {}
        for j in range(9):
            for t in range(37):
                p = (9 * t + j) % L
                for u in range(37):
                    q = (9 * u + j + s) % L
                    C[(p, q)] = C.get((p, q), 0) + 1
        # D^{(s)}[p][q] from sum_{s'==s (mod9)} sum_i a_i a_{i+s'}
        D = {}
        for sp in range(L):
            if sp % 9 != s:
                continue
            for i in range(L):
                p = i; q = (i + sp) % L
                D[(p, q)] = D.get((p, q), 0) + 1
        ok &= (C == D)
        # closed-form cross-check: coefficient is 1 iff (q-p) == s (mod 9)
        ok &= all(v == 1 for v in C.values())
        ok &= all(((q - p) % 9 == s) for (p, q) in C)
    return ok


def squared_norm_identity_exact():
    """Prove sum_{s=0..8} PAF_x(s) = (sum x)^2 for length-9 x by showing the
    coefficient matrix of the LHS quadratic form is the all-ones 9x9 matrix
    (which is exactly the form (sum x)^2)."""
    E = {}
    for s in range(9):
        for j in range(9):
            p = j; q = (j + s) % 9
            E[(p, q)] = E.get((p, q), 0) + 1
    return all(E.get((p, q), 0) == 1 for p in range(9) for q in range(9))


# ---------------------------------------------------------------------------
# column-sum value set V from orbit sizes (exact reachable set)
# ---------------------------------------------------------------------------
def value_set(orbit_sizes):
    reach = {0}
    for sz in orbit_sizes:
        reach = {v + sz for v in reach} | {v - sz for v in reach}
    return sorted(reach)


def square_multisets(V, total=594, slots=18):
    sq = sorted({v * v for v in V})
    sols = []

    def rec(idx, sl, ss, cur):
        if idx == len(sq):
            if sl == 0 and ss == 0:
                sols.append({sq[i]: cur[i] for i in range(len(sq)) if cur[i]})
            return
        for n in range(sl + 1):
            if n * sq[idx] > ss:
                break
            rec(idx + 1, sl - n, ss - n * sq[idx], cur + [n])
    rec(0, slots, total, [])
    return sols


# ---------------------------------------------------------------------------
# COMPLETE parameterized exhaustive decision of the compressed problem
# ---------------------------------------------------------------------------
def decide_compressed(V, target_paf, rowsums, sqnorm_total, node_cap=10 ** 9):
    """Decide whether there exist atilde,btilde in V^9 with
        sum(atilde), sum(btilde) in `rowsums`,
        PAF_atilde(s)+PAF_btilde(s) = target_paf for s=1..8.
    The identity sum_s PAF = (sum)^2 forces sum atilde^2 + sum btilde^2 =
    `sqnorm_total`, so every sequence has square-sum <= sqnorm_total; we
    enumerate those (pruned DFS) and match A/B by square-sum complement and PAF
    profile.  COMPLETE.  Returns (feasible, witness_or_None, num_sequences)."""
    Vs = sorted(V, key=lambda x: x * x)
    minsq = min(x * x for x in V)
    seqs = []
    cur = [0] * 9
    nodes = [0]

    def rec(pos, sq, rs):
        nodes[0] += 1
        if nodes[0] > node_cap or sq > sqnorm_total:
            return
        if pos == 9:
            if rs in rowsums:
                seqs.append((tuple(cur), sq))
            return
        if sq + (9 - pos) * minsq > sqnorm_total:
            return
        for v in Vs:
            cur[pos] = v
            rec(pos + 1, sq + v * v, rs + v)
    rec(0, 0, 0)
    if nodes[0] > node_cap:
        raise RuntimeError("node cap exceeded (value set too dense)")
    from collections import defaultdict
    idx = defaultdict(list)
    for v, sq in seqs:
        idx[(sq, tuple(paf(v, s) for s in range(1, 9)))].append(v)
    for vb, sqb in seqs:
        need = (sqnorm_total - sqb,
                tuple(target_paf - paf(vb, s) for s in range(1, 9)))
        if need[0] >= 0 and idx.get(need):
            return True, (list(idx[need][0]), list(vb)), len(seqs)
    return False, None, len(seqs)


# ---------------------------------------------------------------------------
# PRIMARY PROOF: an analytic single-shift contradiction (no pair enumeration).
# ---------------------------------------------------------------------------
def forced_structure_lemma():
    """From the unique square-multiset {16x1, 2x289} (two |.|=17 columns, sixteen
    |.|=1) and row sums +-1, the ONLY compatible arrangement of the two big
    columns over the pair (atilde, btilde) is:  both big columns lie in a SINGLE
    sequence, one = +17 (at some position p), one = -17 (at some position q != p),
    with that sequence's other seven entries in {+-1}; and the OTHER sequence is
    nine entries in {+-1}.

    Proof (finite): a sequence with k in {0,1,2} big columns (each +-17) and the
    rest small (each +-1) has row sum in {+-1} only for the cases enumerated
    below; combined with 'exactly two big total', only the (2,0)/(0,2) split with
    the two big values being exactly {+17,-17} survives."""
    def big_multisets_giving_rowsum_pm1(k):
        out = set()
        for bigs in itertools.product((17, -17), repeat=k):
            for sm in itertools.product((1, -1), repeat=9 - k):
                if sum(bigs) + sum(sm) in (-1, 1):
                    out.add(tuple(sorted(bigs)))
        return out
    per_k = {k: big_multisets_giving_rowsum_pm1(k) for k in range(3)}
    # k=1 must be infeasible (a lone +-17 can never yield row sum +-1)
    ok = (per_k[1] == set())
    # k=0 feasible (all small); k=2 feasible ONLY with the multiset {+17,-17}
    ok &= (per_k[0] == {()})
    ok &= (per_k[2] == {(-17, 17)})
    # feasible (kA,kB) splits with kA+kB=2:
    splits = [(kA, 2 - kA) for kA in range(3)
              if per_k[kA] and per_k[2 - kA]]
    ok &= (splits == [(0, 2), (2, 0)])
    return ok, {"per_k_feasible_big_multisets": {k: sorted(map(list, v))
                                                 for k, v in per_k.items()},
                "feasible_splits": splits}


def analytic_single_shift_bound():
    """PRIMARY analytic contradiction.  Assume the forced (2,0) structure:
    atilde has +17 at position p and -17 at position q (p != q), other 7 entries
    in {+-1}; btilde is nine entries in {+-1}.  Evaluate the SINGLE shift
    s = (q - p) mod 9 (nonzero since p != q).

    Term decomposition of PAF_atilde(s) = sum_j atilde_j * atilde_{(j+s) mod 9}:
      * exactly ONE 'big-big' term, the product atilde_p*atilde_q = 17*(-17) = -289
        (there is no second big-big term because 2s != 0 mod 9, as gcd(2,9)=1 and
         s != 0);
      * exactly TWO 'big-small' terms, each a product (+-17)*(+-1) <= +17;
      * exactly SIX 'small-small' terms, each a product (+-1)*(+-1) <= +1.
    Hence  PAF_atilde(s) <= -289 + 2*17 + 6*1 = -249.
    Also PAF_btilde(s) <= 9 (nine unit products).  Therefore
      PAF_atilde(s) + PAF_btilde(s) <= -240  <  -74,
    contradicting the compression requirement PAF_atilde(s)+PAF_btilde(s) = -74.

    We verify the term-count structure for EVERY distinct (p,q) (72 position
    pairs -- NOT a sign enumeration) and the arithmetic of the bound."""
    struct_ok = True
    for p in range(9):
        for q in range(9):
            if p == q:
                continue
            s = (q - p) % 9
            if s == 0:
                struct_ok = False
            bb = bs = ss = 0
            bigbig_is_pq = True
            for j in range(9):
                left_big = j in (p, q)
                right_big = (j + s) % 9 in (p, q)
                if left_big and right_big:
                    bb += 1
                    # the unique big-big term must be atilde_p * atilde_q
                    if not (j == p and (j + s) % 9 == q):
                        bigbig_is_pq = False
                elif left_big or right_big:
                    bs += 1
                else:
                    ss += 1
            if not (bb == 1 and bs == 2 and ss == 6 and bigbig_is_pq):
                struct_ok = False
    # per-term bounds -> aggregate bound
    bigbig_term = 17 * (-17)              # = -289 (fixed by the forced structure)
    bound_a = bigbig_term + 2 * 17 + 6 * 1   # <= -249
    bound_b = 9                              # nine (+-1)*(+-1) terms
    bound_sum = bound_a + bound_b            # <= -240
    arithmetic_ok = (bigbig_term == -289 and bound_a == -249
                     and bound_b == 9 and bound_sum == -240)
    contradiction = bound_sum < -74
    return (struct_ok and arithmetic_ok and contradiction), {
        "shift_used": "s = (q - p) mod 9 (nonzero)",
        "term_decomposition": "1 big-big (=-289) + 2 big-small (<=+17 each) "
                              "+ 6 small-small (<=+1 each), verified for all 72 "
                              "distinct (p,q)",
        "bound_PAF_atilde": bound_a,
        "bound_PAF_btilde": bound_b,
        "bound_sum": bound_sum,
        "required_value": -74,
        "contradiction": contradiction,
    }


def analytic_bound_numeric_confirmation():
    """Independent confirmation (small): over ALL (2,0) configurations
    (positions p!=q and the 2^7 small signs of atilde), the maximum of
    PAF_atilde((q-p) mod 9) equals -251 (<= the analytic bound -249); and the
    maximum PAF of any nine-term +-1 sequence at a nonzero shift is 9."""
    max_a = -10 ** 9
    for p in range(9):
        for q in range(9):
            if p == q:
                continue
            s = (q - p) % 9
            smallpos = [i for i in range(9) if i not in (p, q)]
            for bits in itertools.product((1, -1), repeat=7):
                a = [0] * 9
                a[p] = 17; a[q] = -17
                for i, pos in enumerate(smallpos):
                    a[pos] = bits[i]
                v = paf(a, s)
                if v > max_a:
                    max_a = v
    max_b = -10 ** 9
    for b in itertools.product((1, -1), repeat=9):
        for s in range(1, 9):
            max_b = max(max_b, paf(list(b), s))
    return {"max_PAF_atilde_at_q_minus_p": max_a, "analytic_bound": -249,
            "bound_valid": max_a <= -249, "max_PAF_btilde": max_b,
            "max_sum": max_a + max_b, "contradiction": (max_a + max_b) < -74}


# ---------------------------------------------------------------------------
def main():
    print("=" * 72)
    print("STANDALONE VERIFIER  --  id12 impossibility  (LP 333 / Hadamard 668)")
    print("=" * 72)
    results = {}

    g_ok, H, K = check_group()
    print(f"[{'PASS' if g_ok else 'FAIL'}] H=<10,46> mod 333 = {H}")
    print(f"        order 9, trivial mod 9, K37 = {K}")
    results["group"] = g_ok

    sizes = k37_orbit_sizes(set(K))
    o_ok = (sizes == [1, 9, 9, 9, 9])
    print(f"[{'PASS' if o_ok else 'FAIL'}] K37-orbit sizes of Z_37 = {sizes}")
    results["orbit_sizes"] = o_ok

    id_ok = compression_identity_exact()
    print(f"[{'PASS' if id_ok else 'FAIL'}] compression identity "
          f"PAF_atilde(s)=sum_(s'=s mod9) PAF_a(s') "
          f"(exact coefficient-matrix equality, all s)")
    results["compression_identity"] = id_ok

    sn_ok = squared_norm_identity_exact()
    print(f"[{'PASS' if sn_ok else 'FAIL'}] identity sum_s PAF_x(s)=(sum x)^2 "
          f"(coefficient matrix = all-ones)")
    results["squared_norm_identity"] = sn_ok

    V = value_set(sizes)
    v_ok = (V == [-37, -35, -19, -17, -1, 1, 17, 19, 35, 37])
    print(f"[{'PASS' if v_ok else 'FAIL'}] column-sum value set V = {V}")
    results["value_set"] = v_ok

    # forced squared norm 594 (arithmetic from the two exact identities)
    forced = 1 + 1 - 8 * (-74)          # rowsums +-1, target -74
    sq_ok = (forced == 594)
    print(f"[{'PASS' if sq_ok else 'FAIL'}] forced squared norm = {forced} "
          f"(= (+-1)^2+(+-1)^2 - 8*(-74))")
    results["forced_norm"] = sq_ok

    msol = square_multisets(V)
    mu_ok = (msol == [{1: 16, 289: 2}])
    print(f"[{'PASS' if mu_ok else 'FAIL'}] unique 18-square V-multiset -> 594 is "
          f"16x1 + 2x289")
    results["square_multiset_unique"] = mu_ok

    # ---- forced (2,0) structure ----
    fs_ok, fs = forced_structure_lemma()
    print(f"[{'PASS' if fs_ok else 'FAIL'}] forced structure: two big columns "
          f"(one +17, one -17) in a single sequence; the other all +-1 "
          f"(splits {fs['feasible_splits']}; (1,1) impossible)")
    results["forced_structure"] = fs_ok

    # ---- PRIMARY PROOF: analytic single-shift contradiction ----
    an_ok, an = analytic_single_shift_bound()
    print(f"[{'PASS' if an_ok else 'FAIL'}] PRIMARY analytic proof: at s=q-p, "
          f"PAF_a<=-249 and PAF_b<=9, so sum<={an['bound_sum']} < -74 "
          f"(term-count verified for all 72 (p,q))")
    results["analytic_contradiction"] = an_ok

    anc = analytic_bound_numeric_confirmation()
    anc_ok = anc["bound_valid"] and anc["contradiction"]
    print(f"[{'PASS' if anc_ok else 'FAIL'}] analytic bound confirmed numerically "
          f"(max PAF_a at q-p = {anc['max_PAF_atilde_at_q_minus_p']} <= -249; "
          f"max PAF_b = {anc['max_PAF_btilde']})")
    results["analytic_confirmation"] = anc_ok

    # ---- INDEPENDENT CONFIRMATION: full exhaustive decision ----
    feasible, wit, nseq = decide_compressed(V, target_paf=-74, rowsums=(-1, 1),
                                            sqnorm_total=594)
    ex_ok = (feasible is False)
    print(f"[{'PASS' if ex_ok else 'FAIL'}] independent confirmation: exhaustive "
          f"compressed decision INFEASIBLE ({nseq} pruned sequences, 0 feasible)")
    results["exhaustive"] = ex_ok

    # POSITIVE CONTROL: the SAME routine must FIND a solution when one exists.
    # (a) V'={-1,1}, target +18, row sums {9}: atilde=btilde=[1]*9 (PAF(s)=9 each,
    #     sum 9); forced squared norm = 81+81-8*18 = 18.
    pf, pw, _ = decide_compressed([-1, 1], target_paf=18, rowsums=(9,),
                                  sqnorm_total=18)
    pc1 = (pf is True and pw is not None
           and all(paf(pw[0], s) + paf(pw[1], s) == 18 for s in range(1, 9)))
    # (b) the routine recovers a NONTRIVIAL -74 solution when the value set is
    #     enlarged to contain a known free-odd witness value set.
    Vpc = sorted({-21, -3, -1, 1, 3, 5})
    pf2, pw2, _ = decide_compressed(Vpc, target_paf=-74, rowsums=(-1, 1),
                                    sqnorm_total=594)
    pc2 = (pf2 is True and pw2 is not None
           and all(paf(pw2[0], s) + paf(pw2[1], s) == -74 for s in range(1, 9)))
    # (c) the LP checker accepts a genuine small Legendre pair
    lp5 = None
    for a in itertools.product((1, -1), repeat=5):
        if sum(a) not in (-1, 1):
            continue
        for b in itertools.product((1, -1), repeat=5):
            if is_legendre_pair(list(a), list(b)):
                lp5 = (list(a), list(b)); break
        if lp5:
            break
    pc3 = lp5 is not None
    pc_ok = pc1 and pc2 and pc3
    print(f"[{'PASS' if pc_ok else 'FAIL'}] positive controls: routine finds "
          f"trivial solution={pc1}, finds nontrivial -74 solution={pc2}, "
          f"accepts length-5 LP={pc3}")
    results["positive_controls"] = pc_ok

    allok = all(results.values())
    print("-" * 72)
    if allok:
        print("VERDICT: PROOF VERIFIED.  No id12-invariant Legendre pair of "
              "length 333 exists.")
        print("         PRIMARY proof: analytic single-shift contradiction "
              "(PAF sum <= -240 at s=q-p, vs required -74).")
        print("         Independently confirmed by exhaustive enumeration.")
        print("         (Family id12 is IMPOSSIBLE; the last open order->=9 "
              "common-multiplier LP(333) family is now closed.)")
    else:
        print("VERDICT: VERIFICATION FAILED:", results)
    print("=" * 72)
    return allok


if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
