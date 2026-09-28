#!/usr/bin/env python
"""The CC-level confirmation of the pattern proposer on an anchored molecule (pre-registration 2026-09-28, Standout_CC_Level_Test): the proxy's own
export code with the CCSD(T) Hessian as the high level (`hi_override`), the same deck, the same recovery; orderings P0, P1 (seeds 0–2, trained on the
proxy exports, not retrained) and P3 (oracle); read-outs K_off(0.3), n_half and AUC ratio against P0 on the CC responses and, side by side, on the
proxy export of the same molecule; the lines C1–C3 judged as registered.

    python cc_level_test.py <molecule id> <cc hessian npz> [--out out/cc] [--stride N] [--seeds 0,1,2]
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PLAN = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(PLAN / "src"))
from pp import core as C  # noqa: E402
from pp import scorer as S  # noqa: E402
from readout import per_molecule  # noqa: E402

from dpir.provenance import provenance  # noqa: E402

CORPUS = PLAN / "modules" / "05_support_predictor" / "corpus" / "molecules"
OUT = HERE / "out"


def curves_for(exp: dict, seeds: list[int], stride: int, w_cm: float = C.W_BAND_CM) -> dict:
    X, _, pairs = S.pair_features(exp)
    pool = C.order_p0(exp)
    out = {"P0": C.rho_curve(exp, pool, stride=stride, w_cm=w_cm)}
    for s in seeds:
        sc = S.Scorer.load(OUT / "p1", s)
        out[f"P1_seed{s}"] = C.rho_curve(exp, C.order_by_scores(exp, S.scores_matrix(exp, sc.predict(X), pairs)), stride=stride, w_cm=w_cm)
    out["P3_oracle"] = C.rho_curve(exp, C.order_oracle(exp), stride=stride, w_cm=w_cm)
    return out


def readouts(exp: dict, curves: dict, seeds: list[int]) -> dict:
    M = exp["M"]
    m = {"M": M, "split": "eval_parents"}
    m.update({k: {"curve": v} for k, v in curves.items()})
    names = [f"P1_seed{s}" for s in seeds] + ["P3_oracle"]
    pm = per_molecule(m, names)
    k0 = C.k_off_at(curves["P0"], 0.3, M)
    rows = {}
    for name in names:
        k = C.k_off_at(curves[name], 0.3, M)
        r = pm[(name, "rho_off")]
        rows[name] = dict(k_off_0p3=k, k_off_ratio=(k / k0 if (k is not None and k0) else None), n_half=r["n_half"], n_half_ratio=r["half_ratio"], auc_ratio=r["auc_ratio"])
    p1 = [rows[f"P1_seed{s}"] for s in seeds]
    med = lambda key: (statistics.median([x[key] for x in p1 if x[key] is not None]) if any(x[key] is not None for x in p1) else None)  # noqa: E731
    return dict(M=M, n_patterns=int(len(exp["kinds"])), n_holdout=int(exp["holdout"].sum()), P0=dict(k_off_0p3=k0, rho_off_start=curves["P0"][0][2], rho_off_final=curves["P0"][-1][2]),
                orderings=rows, P1_median=dict(k_off_ratio=med("k_off_ratio"), n_half_ratio=med("n_half_ratio"), auc_ratio=med("auc_ratio")),
                oracle=dict(k_off_0p3=rows["P3_oracle"]["k_off_0p3"], k_off_ratio=rows["P3_oracle"]["k_off_ratio"]),
                p1_over_oracle=(med("k_off_ratio") / rows["P3_oracle"]["k_off_ratio"]) if (med("k_off_ratio") and rows["P3_oracle"]["k_off_ratio"]) else None)


def judge(cc: dict, proxy: dict) -> dict:
    p1c, p1p = cc["P1_median"], proxy["P1_median"]
    c1 = (p1c["k_off_ratio"] is not None and p1c["k_off_ratio"] <= 0.80) and (p1c["n_half_ratio"] is not None and p1c["n_half_ratio"] <= 0.80)
    same_dir = (p1c["k_off_ratio"] is not None and p1p["k_off_ratio"] is not None and ((p1c["k_off_ratio"] < 1) == (p1p["k_off_ratio"] < 1)))
    within = (p1c["k_off_ratio"] is not None and p1p["k_off_ratio"] and max(p1c["k_off_ratio"] / p1p["k_off_ratio"], p1p["k_off_ratio"] / p1c["k_off_ratio"]) <= 1.5)
    c2 = bool(same_dir and within)
    c3 = dict(oracle_k_off=cc["oracle"]["k_off_0p3"], p1_over_oracle=cc["p1_over_oracle"], near_ceiling=(cc["p1_over_oracle"] is not None and cc["p1_over_oracle"] <= 1.5))
    return dict(C1_pass=bool(c1), C2_pass=c2, C3=c3,
                label=("confirmed on this molecule (CC)" if c1 and c2 else "plan works on CC, proxy misjudged its size" if c1 else "proxy (C1 failed on CC)"))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("molecule_id"); ap.add_argument("cc_hessian")
    ap.add_argument("--out", default=str(OUT / "cc")); ap.add_argument("--stride", type=int, default=None); ap.add_argument("--seeds", default="0,1,2")
    ap.add_argument("--pool", choices=["band", "all"], default="band", help="band = the registered run (E1 deck); all = two-mode patterns for every pair (E2's wide pool) — exploratory")
    ap.add_argument("--w-cm", type=float, default=C.W_BAND_CM, help="the solver's band prior width; anything but the default is exploratory and labelled so")
    ap.add_argument("--tag", default="", help="suffix for the output files of an exploratory run")
    a = ap.parse_args(argv)
    seeds = [int(s) for s in a.seeds.split(",")]
    exploratory = a.pool != "band" or a.w_cm != C.W_BAND_CM
    mol_dir = CORPUS / a.molecule_id
    t0 = time.time()
    cc_exp = C.export_molecule(mol_dir, hi_override=Path(a.cc_hessian))
    proxy_exp = C.load_export(OUT / "exports" / f"{a.molecule_id}.npz")
    assert cc_exp["deck_hash"] == proxy_exp["deck_hash"], "the CC export must use the proxy's deck (same B3LYP frequencies)"
    if a.pool == "all":
        from run_simulation import widen_pool
        cc_exp, proxy_exp = widen_pool(cc_exp), widen_pool(proxy_exp)
    stride = a.stride or max(2, int(np.ceil(len(C.order_p0(cc_exp)) / 30)))
    cc_curves = curves_for(cc_exp, seeds, stride, a.w_cm); px_curves = curves_for(proxy_exp, seeds, stride, a.w_cm)
    cc, px = readouts(cc_exp, cc_curves, seeds), readouts(proxy_exp, px_curves, seeds)
    J = judge(cc, px)
    z = np.load(a.cc_hessian)
    off_cc = np.triu(cc_exp["D2"], 1); off_px = np.triu(proxy_exp["D2"], 1)
    rec = dict(date=time.strftime("%Y-%m-%d %H:%M"), molecule=a.molecule_id, cc_hessian=str(Path(a.cc_hessian).resolve().relative_to(PLAN)).replace("\\", "/"),
               cc_meta=dict(basis=str(z["basis"]) if "basis" in z.files else None, frozen=int(z["frozen"]) if "frozen" in z.files else None, step=float(z["step"]) if "step" in z.files else None),
               deck_hash=cc_exp["deck_hash"], stride=stride, seeds=seeds, seconds=round(time.time() - t0), pool=a.pool, w_cm=a.w_cm, exploratory=exploratory,
               registered_run=(not exploratory),
               delta2=dict(off_frob_cc=float(np.linalg.norm(off_cc)), off_frob_proxy=float(np.linalg.norm(off_px)), ratio=float(np.linalg.norm(off_cc) / np.linalg.norm(off_px)),
                           inband_share_cc=float((np.linalg.norm(off_cc * np.triu(np.abs(cc_exp["freq_cm"][:, None] - cc_exp["freq_cm"][None, :]) <= C.W_BAND_CM, 1)) / np.linalg.norm(off_cc)) ** 2),
                           inband_share_proxy=float((np.linalg.norm(off_px * np.triu(np.abs(proxy_exp["freq_cm"][:, None] - proxy_exp["freq_cm"][None, :]) <= C.W_BAND_CM, 1)) / np.linalg.norm(off_px)) ** 2)),
               cc=cc, proxy=px, curves=dict(cc={k: v for k, v in cc_curves.items()}, proxy={k: v for k, v in px_curves.items()}), judged=J, provenance=provenance())
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    stem = f"{a.molecule_id}_cc_test" + (f"_{a.tag}" if a.tag else ("_exploratory" if exploratory else ""))
    pj = out / f"{stem}.json"; json.dump(rec, open(pj, "w", encoding="utf-8"), indent=1)
    L = [f"# CC-level test — {a.molecule_id} ({rec['date']}; pre-registration 2026-09-28 Standout_CC_Level_Test)"
         + (f" — EXPLORATORY, not a registered line: pool {a.pool}, solver band {a.w_cm:g} cm⁻¹" if exploratory else ""), "",
         f"CC Hessian `{rec['cc_hessian']}` ({rec['cc_meta']}); deck {cc_exp['deck_hash'][:12]} (same as the proxy export); M = {cc['M']}, {cc['n_patterns']} patterns, {cc['n_holdout']} held out; "
         f"stride {stride}; Δ₂ off-diagonal Frobenius CC / proxy = {rec['delta2']['ratio']:.2f}; in-band share CC {rec['delta2']['inband_share_cc']:.2f} vs proxy {rec['delta2']['inband_share_proxy']:.2f}.", "",
         "| response | ordering | K_off(0.3) | ratio vs P0 | n_half ratio | AUC ratio |", "|---|---|---|---|---|---|"]
    for tag, d in (("CC", cc), ("proxy", px)):
        L.append(f"| {tag} | P0 | {d['P0']['k_off_0p3']} | 1.00 | 1.00 | 1.00 |")
        for name, r in d["orderings"].items():
            fmt = lambda x: "—" if x is None else f"{x:.2f}"  # noqa: E731
            L.append(f"| {tag} | {name} | {r['k_off_0p3']} | {fmt(r['k_off_ratio'])} | {fmt(r['n_half_ratio'])} | {fmt(r['auc_ratio'])} |")
        L.append(f"| {tag} | **P1 median** | — | {d['P1_median']['k_off_ratio'] if d['P1_median']['k_off_ratio'] is None else format(d['P1_median']['k_off_ratio'], '.2f')} | "
                 f"{d['P1_median']['n_half_ratio'] if d['P1_median']['n_half_ratio'] is None else format(d['P1_median']['n_half_ratio'], '.2f')} | "
                 f"{d['P1_median']['auc_ratio'] if d['P1_median']['auc_ratio'] is None else format(d['P1_median']['auc_ratio'], '.2f')} |")
    L += ["", f"**C1** (P1 vs P0 on CC: K_off ratio ≤ 0.80 and n_half ratio ≤ 0.80): {'pass' if J['C1_pass'] else 'FAIL'}. **C2** (same direction as the proxy, within a factor 1.5): {'pass' if J['C2_pass'] else 'FAIL'}. "
          f"**C3** oracle K_off(0.3) on CC {J['C3']['oracle_k_off']}, P1 / oracle {J['C3']['p1_over_oracle'] if J['C3']['p1_over_oracle'] is None else format(J['C3']['p1_over_oracle'], '.2f')} "
          f"({'near the ceiling' if J['C3']['near_ceiling'] else 'not near the ceiling'}). **Label for the plan line:** {J['label']}.", ""]
    pm = out / f"{stem}.md"; pm.write_text("\n".join(L), encoding="utf-8", newline="\n")
    print("\n".join(L)); print("written", pj.relative_to(HERE), pm.relative_to(HERE))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
