"""Chain 41's id files, written from the frozen set file (rung C pre-registration, chain 41, registered 11 Oct 2026;
`modules/05_support_predictor/out/chain41_size5_folds_2026-10-11.json`). One id per line, a '#' header naming the source. Built 13 Oct 2026 with the
run spec (`probes/runs/chain41.json`).

- s5: the thirty five-ring neutrals.
- s4N: the thirty aza four-rings, which the size arm reads beside s5.
- fold{1,2}_test: each control fold's fifteen test molecules.
- fold{1,2}_exclude: what each control fold leaves out of a pool that includes layer P3.
- all_labelled: every id the run needs labelled (s5 ∪ s4N), the wait condition's list.

The size arm keeps pool 3 out through `--pool-layers A,A2,B` (P3 is not listed). Passing its exclude list as well would be refused by the
trainer, because no id of it is in that pool.

    python probes/chain41_prepare.py   → modules/05_support_predictor/out/chain41_<name>.txt
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "modules" / "05_support_predictor" / "out"
SRC = OUT / "chain41_size5_folds_2026-10-11.json"


def lists(d: dict) -> dict:
    return {"s5": d["s5"], "s4N": d["s4N"],
            "fold1_test": d["control_fold1"]["test"], "fold1_exclude": d["control_fold1"]["exclude"],
            "fold2_test": d["control_fold2"]["test"], "fold2_exclude": d["control_fold2"]["exclude"],
            "all_labelled": sorted(set(d["s5"]) | set(d["s4N"]))}


def main():
    d = json.load(open(SRC, encoding="utf-8"))
    for name, ids in lists(d).items():
        (OUT / f"chain41_{name}.txt").write_text(f"# chain 41 ({name}), from {SRC.name} (sha256 of its candidates csv {d['candidates_csv_sha256'][:12]})\n"
                                                  + "".join(i + "\n" for i in ids), encoding="utf-8")
        print(name, len(ids))


if __name__ == "__main__":
    main()
