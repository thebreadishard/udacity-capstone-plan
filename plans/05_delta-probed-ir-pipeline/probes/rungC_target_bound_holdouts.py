"""Target bound on the hold-outs (1 Oct 2026 13:2x, Sherlock day): the read-out a model would get if it reproduced its pattern target exactly — the
ceiling of lever 4 (ridge target, pattern d) and lever 1b (pattern f) on the hold-outs the runs are judged on. Targets come from the trainer's cache
(`out/ls_targets/<pattern>_lam<λ>/<id>.npz`, computed when missing); the truth K is the trainer's (analytic second route substituted where it exists,
`e7_rungB_reread_analytic.substitute`), so the numbers compare with the records. The projected target (the registered one) is the reference column.

    python probes/rungC_target_bound_holdouts.py <corpus/molecules> <record.json with holdout_a/holdout_b> <out_prefix> [--patterns d,f] [--lam 1e-3]
"""
import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
M05 = HERE.parent / "modules" / "05_support_predictor" / "m05"
sys.path.insert(0, str(M05))
import e7_rungB_pairs as RB  # noqa: E402
import e7_rungB_reread_analytic as RR  # noqa: E402
import e7_t2_sqm as T2  # noqa: E402
import rungC_targets as RT  # noqa: E402
from rungC_equivariant import load_molecule  # noqa: E402
from rungC_train import pattern_classes  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("molecules")
    ap.add_argument("record")
    ap.add_argument("out_prefix")
    ap.add_argument("--patterns", default="d,f")
    ap.add_argument("--lam", type=float, default=RT.LAM_REL)
    a = ap.parse_args()
    t0 = time.time()
    mdir = Path(a.molecules)
    rec = json.load(open(a.record, encoding="utf-8"))
    holds = {"a": list(rec["holdout_a"]), "b": list(rec["holdout_b"])}
    mols = T2.load(mdir)
    for i in set(holds["a"]) | set(holds["b"]):
        d = mdir / i
        if (d / "hessian_b3lyp_analytic.npz").exists() and (d / "hessian_wb97x_analytic.npz").exists():
            RR.substitute(mols[i], d)
    cache = Path(a.out_prefix).parent / "ls_targets"
    res = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "record": a.record, "lam_rel": a.lam, "patterns": a.patterns.split(","), "bounds": {}}
    lines = [f"# Target bound on the hold-outs ({res['date']}) — the read-out of a model that reproduces its target exactly", "",
             f"Hold-outs of `{Path(a.record).name}`; λ_rel {a.lam:g}.", "",
             "| pattern | target | (a) ratio | (a) ω | (a) ΔH res. | (b) ratio | (b) ω | (b) ΔH res. |", "|---|---|---|---|---|---|---|---|"]
    for p in res["patterns"]:
        targets = {"projected": {}, "ridge": {}}
        for i in set(holds["a"]) | set(holds["b"]):
            m = load_molecule(mdir / i, use_analytic=True)
            mask = (pattern_classes(mdir / i, mols[i], p) >= 0).numpy()
            B = mols[i]["B"]
            targets["projected"][i] = np.where(mask, RT.projected_target(m["dH_true"], B), 0.0)
            targets["ridge"][i], _cached = RT.cached_pattern_ls_target(cache, i, p, m["dH_true"], B, m["masses"], mask, lam_rel=a.lam)
        for name, tg in targets.items():
            row = {}
            for h, ids in holds.items():
                r = RB.readouts(mols, ids, ids, lambda j, tg=tg: tg[j])
                row[h] = {"coupling_ratio": r["coupling_ratio"], "corrected_freq_rms": r["corrected_freq_rms"], "dH_residual_ratio": r["dH_residual_ratio"]}
            res["bounds"][f"{p}:{name}"] = row
            lines.append(f"| {p} | {name} | {row['a']['coupling_ratio']:.3f} | {row['a']['corrected_freq_rms']:.2f} | {row['a']['dH_residual_ratio']:.3f} | "
                         f"{row['b']['coupling_ratio']:.3f} | {row['b']['corrected_freq_rms']:.2f} | {row['b']['dH_residual_ratio']:.3f} |")
    res["seconds"] = round(time.time() - t0)
    out = Path(a.out_prefix)
    json.dump(res, open(out.with_suffix(".json"), "w"), indent=1)
    lines += ["", f"{res['seconds']} s."]
    out.with_suffix(".md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
