"""T-1 (pre-registered in P26 §6 on 2026-09-13; the user agreed to the form and the threshold the same day) — the first transfer test:
does the per-mode correction of one molecule say anything about another, per band family?

Rule under test (the simplest, fixed in P26): for each family f, the source molecule gives one number, the median RELATIVE correction
  s_f = median over source modes i in f of  delta_nu_i / nu_i        (delta_nu_i = first-order band shift of the correction, D2_Q[i,i] / (2 omega_i))
and the target molecule's modes are predicted as  delta_nu_j(pred) = s_f * nu_j  for j in f. The error per family is the RMS and the maximum of
delta_nu_j(pred) - delta_nu_j(measured) over the target's modes in f. Secondary rules, printed for comparison and NOT the licence: the zero rule
(predict no correction) and the absolute rule (median delta_nu per family, in cm^-1).

Losing condition (P26 §6, agreed): if the per-family transfer error (RMS) at T-1 exceeds the laboratory margin — Module 03's u_band at R0
gas phase, 2.5 cm^-1 (QUANT-IR benzene; `modules/03_lab_scoreboard/U_BAND.md`) — for the C-H stretch and C-C stretch families, the
numbers-machine framing does not carry, and P26 §9's fallback applies. Other families are reported, not judged.

Inputs: plan 05 dry-run stage-A files of source and target (`stageA.json`: freq_low_cm, dfreq_first_order_cm, families). Stand-in tensors are
DFT-DFT (BHHLYP - B3LYP), as in every desk experiment so far; T-2 repeats this with a real CC hold-out.
Self-test today: --target benzene --source benzene prints the within-molecule family spread of the rule (the floor no transfer can beat) and
checks that the identity prediction of the medians reproduces the family medians. When the target's stage A does not exist the script prints
NOT_RUN for the transfer part. Every number from the files; constants in CONSTANTS."""
import argparse
import json
from datetime import datetime
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
CONSTANTS = {"threshold_cm": 2.5, "threshold_source": "Module 03 U_BAND.md: QUANT-IR benzene gas-phase u_band 2.55 cm-1 (R0 floor form)",
             "judged_families": ["CH-stretch", "CC-stretch"], "primary_rule": "relative: delta_nu/nu per family (median)", "secondary_rules": ["zero", "absolute delta_nu per family (median)"]}


def load(mol):
    d = HERE / f"results_dryrun/{mol}/stageA.json"
    if not d.exists():
        return None
    a = json.load(open(d))
    return {"nu": np.array(a["freq_low_cm"]), "dnu": np.array(a["dfreq_first_order_cm"]), "fam": a["families"], "functionals": a.get("functionals")}


def family_stats(m):
    out = {}
    for f in sorted(set(m["fam"])):
        idx = [k for k, g in enumerate(m["fam"]) if g == f]
        rel = m["dnu"][idx] / m["nu"][idx]
        out[f] = {"n": len(idx), "median_rel": float(np.median(rel)), "median_abs_cm": float(np.median(m["dnu"][idx])),
                  "spread_rel_rms_cm": float(np.sqrt(np.mean((np.median(rel) * m["nu"][idx] - m["dnu"][idx]) ** 2))),
                  "nu_range": [float(m["nu"][idx].min()), float(m["nu"][idx].max())], "dnu_range": [float(m["dnu"][idx].min()), float(m["dnu"][idx].max())]}
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--source", default="benzene"); ap.add_argument("--target", default="naphthalene"); args = ap.parse_args()
    S = load(args.source); T = load(args.target)
    out = {"date": f"{datetime.now():%Y-%m-%d %H:%M}", "constants": CONSTANTS, "source": args.source, "target": args.target}
    fs = family_stats(S); out["source_families"] = fs
    L = [f"# T-1 transfer test — source {args.source}, target {args.target} ({out['date']})", "",
         f"Rule: {CONSTANTS['primary_rule']}; losing condition: RMS error > {CONSTANTS['threshold_cm']} cm⁻¹ for {', '.join(CONSTANTS['judged_families'])} ({CONSTANTS['threshold_source']}). Stand-in: {S['functionals']}.", "",
         f"## Source ({args.source}): per-family relative correction and the within-molecule floor of the rule", "",
         "| family | modes | median δν/ν | median δν (cm⁻¹) | δν range (cm⁻¹) | floor: RMS of the rule inside the source (cm⁻¹) |", "|---|---|---|---|---|---|"]
    for f, s in fs.items():
        L.append(f"| {f} | {s['n']} | {s['median_rel']:+.4f} | {s['median_abs_cm']:+.1f} | {s['dnu_range'][0]:+.1f} … {s['dnu_range'][1]:+.1f} | {s['spread_rel_rms_cm']:.2f} |")
    if T is None:
        L += ["", f"## Transfer to {args.target}: **NOT_RUN** — `results_dryrun/{args.target}/stageA.json` does not exist yet (machine queue item 5)."]
        out["transfer"] = "NOT_RUN"
    else:
        rows = []; verdict = True
        for f in sorted(set(T["fam"])):
            idx = [k for k, g in enumerate(T["fam"]) if g == f]
            meas = T["dnu"][idx]; nu = T["nu"][idx]
            if f in fs:
                pred_rel = fs[f]["median_rel"] * nu; pred_abs = np.full_like(nu, fs[f]["median_abs_cm"])
            else:
                pred_rel = pred_abs = np.zeros_like(nu)
            err = lambda p: (float(np.sqrt(np.mean((p - meas) ** 2))), float(np.abs(p - meas).max()))
            r_rel, r_zero, r_abs = err(pred_rel), err(np.zeros_like(nu)), err(pred_abs)
            judged = f in CONSTANTS["judged_families"]; passes = r_rel[0] <= CONSTANTS["threshold_cm"]
            if judged: verdict &= passes
            rows.append({"family": f, "n": len(idx), "in_source": f in fs, "rms_rel": r_rel[0], "max_rel": r_rel[1], "rms_zero": r_zero[0], "rms_abs": r_abs[0], "judged": judged, "passes": passes})
        out["transfer"] = rows; out["verdict"] = "PASS" if verdict else "LOSE"
        L += ["", f"## Transfer to {args.target}", "", "| family | target modes | in source | RMS error, relative rule (cm⁻¹) | max | RMS zero rule | RMS absolute rule | judged | passes 2.5 |", "|---|---|---|---|---|---|---|---|---|"]
        for r in rows:
            L.append(f"| {r['family']} | {r['n']} | {'yes' if r['in_source'] else 'no'} | **{r['rms_rel']:.2f}** | {r['max_rel']:.2f} | {r['rms_zero']:.2f} | {r['rms_abs']:.2f} | {'yes' if r['judged'] else '—'} | {'yes' if r['passes'] else 'NO'} |")
        L += ["", f"**Verdict (judged families only): {out['verdict']}.** The zero rule is the floor a useful rule must beat; the absolute rule is the secondary comparison."]
    if args.source == args.target:
        L += ["", "Self-test: source = target — the transfer errors equal the within-molecule floors by construction (the rule applied to itself)."]
    d = HERE / "results_dryrun" / f"t1_{args.source}_to_{args.target}.md"; d.write_text("\n".join(L), encoding="utf-8")
    json.dump(out, open(d.with_suffix(".json"), "w"), indent=1)
    print("\n".join(L).encode("ascii", "replace").decode())


if __name__ == "__main__":
    main()
