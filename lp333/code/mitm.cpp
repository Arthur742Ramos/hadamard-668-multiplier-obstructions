// Exact meet-in-the-middle search for common-multiplier-invariant Legendre
// pairs of length 333, restricted to one subgroup H (given by its PAF spec).
//
// Variables x[0..r-1] in {+1,-1} are the H-orbit values of a sequence.  We fix
// x[0]=+1 (orbit {0}) to remove the global-sign symmetry, and enumerate the
// remaining r-1 variables by Gray code.  For each shift representative m,
//     PAF(m) = const[m] + sum_{q<q'} W[m][q][q'] x_q x_{q'}.
// A Legendre pair needs profile(a)[m] + profile(b)[m] = -2 for all m, with row
// sums sum_q size[q] x_q in {+1,-1} for both a and b.  We collect all row-sum
// valid profiles into a hash map and look for two whose sum is the all -2
// vector (the b-profile is the complement (-2)-profile(a)).  Exhaustive.
//
// Output (stdout, one JSON object): result plus exact enumeration statistics.
#include <cstdio>
#include <cstdint>
#include <vector>
#include <string>
#include <unordered_map>
#include <cstring>
using namespace std;

int main(int argc, char** argv){
    if(argc<2){fprintf(stderr,"usage: mitm spec.txt\n");return 2;}
    FILE* f=fopen(argv[1],"r");
    if(!f){fprintf(stderr,"cannot open %s\n",argv[1]);return 2;}
    int r,nreps;
    if(fscanf(f,"%d %d",&r,&nreps)!=2){fprintf(stderr,"bad header\n");return 2;}
    vector<long long> sizes(r), cst(nreps);
    for(int q=0;q<r;q++) if(fscanf(f,"%lld",&sizes[q])!=1){return 2;}
    for(int m=0;m<nreps;m++) if(fscanf(f,"%lld",&cst[m])!=1){return 2;}
    // W[m] full symmetric r*r, diag 0
    vector<vector<int>> W(nreps, vector<int>(r*r,0));
    for(int m=0;m<nreps;m++){
        for(int q=0;q<r;q++) for(int q2=q+1;q2<r;q2++){
            int v; if(fscanf(f,"%d",&v)!=1){return 2;}
            W[m][q*r+q2]=v; W[m][q2*r+q]=v;
        }
    }
    fclose(f);

    vector<int> xval(r,1);
    vector<long long> paf(nreps);
    long long rowsum=0;
    for(int q=0;q<r;q++) rowsum+=sizes[q];
    for(int m=0;m<nreps;m++){
        long long t=cst[m];
        for(int q=0;q<r;q++) for(int q2=q+1;q2<r;q2++) t+=W[m][q*r+q2]; // all x=+1
        paf[m]=t;
    }

    // hash map: profile bytes -> x bitmask (bit q set => xval[q]==-1)
    unordered_map<string,uint64_t> seen;
    seen.reserve(1<<20);

    auto profkey=[&](const vector<int16_t>&p)->string{
        return string((const char*)p.data(), p.size()*sizeof(int16_t));
    };

    long long enumerated=0, rowsum_ok=0;
    uint64_t solA=0, solB=0; bool sat=false;

    vector<int16_t> prof(nreps), comp(nreps);
    unsigned long long total = 1ULL<<(r-1);

    auto process=[&](uint64_t mask)->bool{
        enumerated++;
        if(rowsum!=1 && rowsum!=-1) return false;
        rowsum_ok++;
        for(int m=0;m<nreps;m++){ prof[m]=(int16_t)paf[m]; comp[m]=(int16_t)(-2-paf[m]); }
        string ck=profkey(comp);
        auto it=seen.find(ck);
        if(it!=seen.end()){ solA=it->second; solB=mask; sat=true; return true; }
        // self pair (a==b): profile == complement
        bool self=true; for(int m=0;m<nreps;m++) if(prof[m]!=comp[m]){self=false;break;}
        if(self){ solA=mask; solB=mask; sat=true; return true; }
        string pk=profkey(prof);
        if(seen.find(pk)==seen.end()) seen.emplace(move(pk), mask);
        return false;
    };

    // initial state g=0 (all +1, mask 0)
    if(process(0)){ /* fallthrough to output */ }
    else {
        uint64_t mask=0;
        for(unsigned long long g=1; g<total && !sat; g++){
            // lowest set bit of g -> variable index (1..r-1)
            unsigned long long lsb=g & (~g+1);
            int bitpos=__builtin_ctzll(lsb);      // 0..r-2
            int j=bitpos+1;                        // variable index
            int oldxj=xval[j];
            for(int m=0;m<nreps;m++){
                const int* Wm=&W[m][j*r];
                long long dot=0;
                for(int q=0;q<r;q++) dot+=(long long)Wm[q]*xval[q];
                paf[m]+= -2LL*oldxj*dot;
            }
            rowsum += -2LL*oldxj*sizes[j];
            xval[j]=-oldxj;
            mask ^= (1ULL<<j);
            process(mask);
        }
    }

    // output
    printf("{\n");
    printf("  \"r\": %d, \"num_reps\": %d,\n", r, nreps);
    printf("  \"enumerated\": %lld, \"rowsum_ok\": %lld, \"distinct_profiles\": %zu,\n",
           enumerated, rowsum_ok, seen.size());
    printf("  \"sat\": %s", sat?"true":"false");
    if(sat){
        printf(",\n  \"a\": [");
        for(int q=0;q<r;q++) printf("%s%d", q?",":"", (solA>>q&1)?-1:1);
        printf("],\n  \"b\": [");
        for(int q=0;q<r;q++) printf("%s%d", q?",":"", (solB>>q&1)?-1:1);
        printf("]\n");
    } else printf("\n");
    printf("}\n");
    return 0;
}
