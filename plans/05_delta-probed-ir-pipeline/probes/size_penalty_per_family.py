"""Where does the size penalty sit? (15 Oct 2026, desk; TASKS 37/61.) Chain 39 read one number — the ring-coupling ratio on the ≥ 27-atom hold-out
(s) is 1.96× larger when the network is trained on ≤ 20 atoms than on the control pool of every size below 27 (q). This splits that penalty into
the read-outs per band family, from the two records' own per-seed numbers: for each read-out the seed mean ± standard error in both runs and
the ratio size-run / control, with the ratio's spread from the seed ranges.

    python probes/size_penalty_per_family.py <size_record.json> <control_record.json> [--hold s] [--out prefix]
"""
import argparse
import json
import sys

import numpy as np

FAMILIES = ("CH-stretch", "CH-oop", "ring-ip", "other")


def readouts(rec_path: str, hold: str) -> dict:
    """{read-out: per-seed values} for the record's single pool size."""
    rec = json.load(open(rec_path, encoding="utf-8"))
    if len(rec["curve"]) != 1:
        raise ValueError(f"{rec_path}: {len(rec['curve'])} pool sizes — give a record of one size")
    seeds = next(iter(rec["curve"].values()))["per_seed"]
    out = {"ring_coupling_ratio": [s[hold]["coupling_ratio"] for s in seeds], "corrected_freq_rms": [s[hold]["corrected_freq_rms"] for s in seeds]}
    out.update({f"diag_rms_{f}": [s[hold]["diag_rms"][f] for s in seeds] for f in FAMILIES})
    return out


def penalty(size_rec: str, control_rec: str, hold: str = "s") -> dict:
    a, b = readouts(size_rec, hold), readouts(control_rec, hold)
    out = {}
    for k in a:
        x, y = np.array(a[k], float), np.array(b[k], float)
        out[k] = {"size_mean": float(x.mean()), "size_se": float(x.std(ddof=1) / np.sqrt(len(x))), "control_mean": float(y.mean()),
                  "control_se": float(y.std(ddof=1) / np.sqrt(len(y))), "ratio": float(x.mean() / y.mean()),
                  "ratio_range": [float(x.min() / y.max()), float(x.max() / y.min())]}
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("size_record")
    ap.add_argument("control_record")
    ap.add_argument("--hold", default="s")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    res = penalty(a.size_record, a.control_record, a.hold)
    lines = [f"# Size penalty per read-out, hold-out ({a.hold})", "", f"size run `{a.size_record}`, control `{a.control_record}`", "",
             "| read-out | size run (mean ± SE) | control (mean ± SE) | ratio | ratio from the seed ranges |", "|---|---|---|---|---|"]
    lines += [f"| {k} | {v['size_mean']:.3f} ± {v['size_se']:.3f} | {v['control_mean']:.3f} ± {v['control_se']:.3f} | {v['ratio']:.2f} | "
              f"{v['ratio_range'][0]:.2f}–{v['ratio_range'][1]:.2f} |" for k, v in res.items()]
    print("\n".join(lines))
    if a.out:
        json.dump(res, open(a.out + ".json", "w", encoding="utf-8"), indent=1)
        open(a.out + ".md", "w", encoding="utf-8").write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
