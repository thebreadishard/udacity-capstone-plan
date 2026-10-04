"""Where does the 'other' family's error sit? (4 Oct 2026, the measurement registered as the first part of chain 34's third branch.)

For every hold-out (a) molecule and each saved model given: the corrected-ω error per mode (as `rungC_cc_transfer.family_freq_rms`: Ω² + 2√(ω_i ω_j) K,
modes paired by overlap), grouped by family with 'other' split into **other-low** (uncorrected ω < --low cm⁻¹: torsions, ring puckers, skeletal bends)
and **other-mid** (the rest); beside it the zero rule (no correction) and, where the molecule has both the finite-difference and the analytic Hessian,
the FD-vs-analytic floor split the same way. Pooled rows over the hold-out and per molecule. Nothing is trained; the models are read with
`--allow-any-model` named in the record (decision 55: candidate models may be *measured*, never used as evidence for a reading).

    python probes/rungC_low_modes_noise.py out/<prefix> out/<record>_model_n750_seed0.pt [more models] [--molecules corpus/molecules] [--low 700]
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "m05"))
sys.path.insert(0, str(PLAN / "probes"))
import e7_t2_posthoc as PH  # noqa: E402
import e7_t2_sqm as T2  # noqa: E402
import model_registry as MR  # noqa: E402
from rungC_equivariant import load_molecule  # noqa: E402
from rungC_train import console_utf8_safe, load_corpus, load_hybrid_model, molecule_tensors, predictor  # noqa: E402

GROUPS = ("ring-ip", "CH-stretch", "CH-oop", "other-low", "other-mid")


def mode_errors(m: dict, K_pred: np.ndarray, low: float) -> tuple[np.ndarray, np.ndarray]:
    """Per corrected mode: the error wp − wt (cm⁻¹) and its group label (family of the uncorrected mode it overlaps most; 'other' split by its ω)."""
    wt, Ut = T2.corrected_frequencies(m, m["K"])
    wp, _ = T2.corrected_frequencies(m, K_pred)
    idx = np.argmax(np.abs(Ut), axis=0)
    fam = np.array(m["family"])[idx]
    om = np.abs(np.asarray(m["freq"], float))[idx]
    grp = np.array([("other-low" if om[k] < low else "other-mid") if fam[k] == "other" else fam[k] for k in range(len(fam))])
    return wp - wt, grp


def rms_by_group(err: np.ndarray, grp: np.ndarray) -> dict:
    return {g: float(np.sqrt(np.mean(err[grp == g] ** 2))) for g in GROUPS if (grp == g).any()}


def counts(grp: np.ndarray) -> dict:
    return {g: int((grp == g).sum()) for g in GROUPS}


def pooled(rows: list[dict], key: str) -> dict:
    out = {}
    for g in GROUPS:
        sq = [r[key][g] ** 2 * r["n"][g] for r in rows if g in r[key]]
        n = [r["n"][g] for r in rows if g in r[key]]
        out[g] = float(np.sqrt(sum(sq) / sum(n))) if n else float("nan")
    return out


def fmt(v) -> str:
    return "—" if v is None or (isinstance(v, float) and np.isnan(v)) else f"{v:.2f}"


def main() -> int:
    console_utf8_safe()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("out_prefix")
    ap.add_argument("models", nargs="+")
    ap.add_argument("--molecules", default=str(PLAN / "modules" / "05_support_predictor" / "corpus" / "molecules"))
    ap.add_argument("--low", type=float, default=700.0, help="'other' modes below this uncorrected ω (cm⁻¹) are 'other-low'")
    ap.add_argument("--threads", type=int, default=2)
    a = ap.parse_args()
    import torch
    torch.set_num_threads(a.threads)
    molecules = Path(a.molecules)
    mols, test_a, _, _, _, substituted = load_corpus(a.molecules, True, log=lambda *_: None)
    rows = []
    for i in test_a:
        m = mols[i]
        row = {"id": i, "n_atoms": len(m["masses"]), "pred": {}, "pred_models": []}
        zero_err, grp = mode_errors(m, np.zeros_like(m["K"]), a.low)
        row["n"] = counts(grp)
        row["zero"] = rms_by_group(zero_err, grp)
        d = molecules / i
        if (d / "hessian_b3lyp_analytic.npz").exists() and (d / "hessian_wb97x_analytic.npz").exists() and (d / "hessian_wb97x.npz").exists():
            dH_fd = np.load(d / "hessian_wb97x.npz")["H_projected"] - np.load(d / "hessian_b3lyp.npz")["H_projected"]
            fe, fg = mode_errors(m, T2.K_from_dH(m, dH_fd), a.low)
            row["floor"] = rms_by_group(fe, fg)
        rows.append(row)
    for mp in a.models:
        MR.require_carried(Path(mp), allow=True)
        model, ck = load_hybrid_model(Path(mp))
        cfg = SimpleNamespace(aux=ck["aux_mode"], head=ck["head"], pattern=ck["pattern"], aux_target=ck["aux_target"], ls_lam=ck["ls_lam"], zero_hlow=False)
        tensors = {i: molecule_tensors(i, load_molecule(molecules / i, use_analytic=True), mols[i], molecules / i, cfg, Path(a.out_prefix).parent / "ls_targets") for i in test_a}
        dF_of = predictor(model, tensors, mols)
        for row in rows:
            m = mols[row["id"]]
            err, grp = mode_errors(m, PH.k_of(m, dF_of(row["id"])), a.low)
            row["pred_models"].append(rms_by_group(err, grp))
    for row in rows:
        row["pred"] = {g: float(np.sqrt(np.mean([pm[g] ** 2 for pm in row["pred_models"] if g in pm]))) for g in GROUPS if any(g in pm for pm in row["pred_models"])}
    pooled_pred, pooled_zero = pooled(rows, "pred"), pooled(rows, "zero")
    floor_rows = [r for r in rows if "floor" in r]
    pooled_floor = pooled(floor_rows, "floor") if floor_rows else None
    # how much of 'other' is low: share of the pooled squared error
    sq_low = sum(r["pred"].get("other-low", 0.0) ** 2 * r["n"]["other-low"] for r in rows)
    sq_mid = sum(r["pred"].get("other-mid", 0.0) ** 2 * r["n"]["other-mid"] for r in rows)
    share_low = sq_low / (sq_low + sq_mid) if (sq_low + sq_mid) > 0 else float("nan")
    n_low, n_mid = sum(r["n"]["other-low"] for r in rows), sum(r["n"]["other-mid"] for r in rows)
    md = [f"# 'other' split into low (< {a.low:.0f} cm⁻¹) and mid — hold-out (a), {datetime.now():%Y-%m-%d %H:%M}", "",
          f"Models: {', '.join(Path(p).name for p in a.models)} (rms over models per molecule); corpus with analytic Hessians substituted for {len(substituted)} molecules.", "",
          "## Pooled over the hold-out (rms, cm⁻¹; n modes)", "", "| group | n | models | zero rule | FD floor (molecules with both routes) |", "|---|---|---|---|---|"]
    for g in GROUPS:
        md.append(f"| {g} | {sum(r['n'][g] for r in rows)} | {fmt(pooled_pred[g])} | {fmt(pooled_zero[g])} | {fmt(pooled_floor[g]) if pooled_floor else '—'} |")
    md += ["", f"Share of the pooled squared 'other' error in the low modes: **{100 * share_low:.0f} %** ({n_low} low modes, {n_mid} mid modes).", "",
           "## Per molecule (rms, cm⁻¹): models / zero rule / floor", "", "| molecule | atoms | " + " | ".join(GROUPS) + " |", "|---|---|" + "---|" * len(GROUPS)]
    for r in rows:
        cells = []
        for g in GROUPS:
            if r["n"][g] == 0:
                cells.append("—")
            else:
                cells.append(f"{fmt(r['pred'].get(g))} / {fmt(r['zero'].get(g))}" + (f" / {fmt(r['floor'].get(g))}" if "floor" in r else ""))
        md.append(f"| {r['id']} | {r['n_atoms']} | " + " | ".join(cells) + " |")
    res = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "low_cm": a.low, "models": a.models, "pooled_pred": pooled_pred, "pooled_zero": pooled_zero,
           "pooled_floor": pooled_floor, "share_low": share_low, "n_low": n_low, "n_mid": n_mid, "rows": rows}
    Path(a.out_prefix + ".md").write_text("\n".join(md), encoding="utf-8")
    Path(a.out_prefix + ".json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
