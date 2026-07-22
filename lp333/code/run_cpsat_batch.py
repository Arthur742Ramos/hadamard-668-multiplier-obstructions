#!/usr/bin/env python3
"""Run CP-SAT on a list of family ids, writing one JSON result file per family
under results/cpsat/ and appending a line to results/cpsat_progress.log.
Unbuffered so progress is visible."""
import json
import os
import sys
import time
sys.path.insert(0, os.path.dirname(__file__))
from cpsat_search import solve_family

HERE = os.path.dirname(__file__)
OUTDIR = os.path.join(HERE, "..", "results", "cpsat")
os.makedirs(OUTDIR, exist_ok=True)
LOG = os.path.join(HERE, "..", "results", "cpsat_progress.log")


def main():
    ids = [int(x) for x in sys.argv[1:]]
    tsec = float(os.environ.get("CPS_T", "300"))
    workers = int(os.environ.get("CPS_W", "8"))
    for sid in ids:
        t0 = time.time()
        with open(LOG, "a") as f:
            f.write(f"START id={sid} t={time.strftime('%H:%M:%S')}\n")
        res = solve_family(sid, max_seconds=tsec, workers=workers)
        with open(os.path.join(OUTDIR, f"id{sid}.json"), "w") as f:
            json.dump(res, f, indent=2)
        line = (f"DONE id={sid:>3} order={res['order']:>3} r={res['r']:>3} "
                f"status={res['status']:>10} t={res['seconds']:>7}s "
                f"sat={res.get('sat')}")
        with open(LOG, "a") as f:
            f.write(line + "\n")
        print(line, flush=True)


if __name__ == "__main__":
    main()
