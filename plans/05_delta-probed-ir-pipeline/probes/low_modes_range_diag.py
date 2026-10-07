"""TASKS 23, step 0 (7 Oct 2026): is the 'other-low' error a matter of range? A diagnostic without training.

The equivariant head predicts ΔH only for atom pairs within its cosine cutoff (5 Å); every block between atoms farther apart is zero. This script takes
the TRUE correction of each hold-out (a) molecule — analytic ωB97X minus analytic B3LYP, the targets of the 5 Oct read — and zeroes every off-diagonal
3×3 block whose atoms are farther apart than r, for r = 3, 4, 5, 6, 8 Å and ∞, in two variants: (keep) the diagonal blocks untouched; (sum) the
diagonal blocks re-made from the acoustic sum rule over the kept blocks (H_ii = −Σ_j≠i H_ij), as a translation-invariant model must. The corrected
frequencies are read per group exactly as `probes/rungC_low_modes_noise.py` reads the models (the same `mode_errors`), so the truncation error at 5 Å
sits beside the models' error (record `out/rungC_low_modes_noise_c34_analytic_2026-10-05.json`) molecule by molecule.

Reading rule (written before the numbers): if the truncation alone at 5 Å costs other-low ≥ 2.0 cm⁻¹ pooled and its per-molecule pattern tracks the
models' (Spearman ρ ≥ 0.6 over the ten molecules), range is a cause and the input design starts with range (a longer cutoff or a long-range term);
if it costs ≤ 1.0 cm⁻¹, range is not the cause and the design starts with the torsion environment; between, both are carried into the design note.

    python probes/low_modes_range_diag.py modules/05_support_predictor/out/low_modes_range_diag_2026-10-07
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "m05"))
sys.path.insert(0, str(PLAN / "probes"))
import e7_t2_sqm as T2  # noqa: E402
from rungC_low_modes_noise import GROUPS, counts, mode_errors, pooled, rms_by_group  # noqa: E402
from rungC_train import load_corpus  # noqa: E402

BOHR2ANG = 0.529177210903
CUTOFFS = (3.0, 4.0, 5.0, 6.0, 8.0, None)
MODELS_RECORD = PLAN / "modules" / "05_support_predictor" / "out" / "rungC_low_modes_noise_c34_analytic_2026-10-05.json"


def truncate(dH: np.ndarray, x_bohr: np.ndarray, r_ang: float | None, sum_rule: bool) -> np.ndarray:
    if r_ang is None:
        return dH.copy()
    n = len(x_bohr)
    d = np.linalg.norm(x_bohr[:, None, :] - x_bohr[None, :, :], axis=-1) * BOHR2ANG
    keep = (d <= r_ang) | np.eye(n, dtype=bool)
    out = dH * np.kron(keep, np.ones((3, 3)))
    if sum_rule:
        for i in range(n):
            off = sum(out[3 * i:3 * i + 3, 3 * j:3 * j + 3] for j in range(n) if j != i)
            out[3 * i:3 * i + 3, 3 * i:3 * i + 3] = -off
        out = 0.5 * (out + out.T)
    return out


def spearman(a, b) -> float:
    ra, rb = np.argsort(np.argsort(a)), np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


def main() -> int:
    out = Path(sys.argv[1])
    molecules = PLAN / "modules" / "05_support_predictor" / "corpus" / "molecules"
    mols, test_a, *_ = load_corpus(str(molecules), True, log=lambda *_: None)
    models = {r["id"]: r for r in json.loads(MODELS_RECORD.read_text(encoding="utf-8"))["rows"]}
    rows = []
    for i in test_a:
        m, d = mols[i], molecules / i
        dH = np.load(d / "hessian_wb97x_analytic.npz")["H_projected"] - np.load(d / "hessian_b3lyp_analytic.npz")["H_projected"]
        x = np.asarray(json.loads((d / "geometry.json").read_text(encoding="utf-8"))["coords_bohr"], float)
        e0, grp = mode_errors(m, T2.K_from_dH(m, dH), 700.0)
        row = {"id": i, "n_atoms": len(x), "n": counts(grp), "identity": float(np.abs(e0).max()), "trunc": {}}
        for variant in ("keep", "sum"):
            for r in CUTOFFS:
                err, g = mode_errors(m, T2.K_from_dH(m, truncate(dH, x, r, variant == "sum")), 700.0)
                row["trunc"][f"{variant}_{r or 'inf'}"] = rms_by_group(err, g)
        row["models"] = models.get(i, {}).get("pred", {})
        rows.append(row)
    keys = [f"{v}_{r or 'inf'}" for v in ("keep", "sum") for r in CUTOFFS]
    pooled_t = {k: pooled([{"n": r["n"], k: r["trunc"][k]} for r in rows], k) for k in keys}
    pooled_m = pooled([{"n": r["n"], "models": r["models"]} for r in rows if r["models"]], "models")
    rho = {v: spearman([r["trunc"][f"{v}_5.0"].get("other-low", 0.0) for r in rows], [r["models"].get("other-low", 0.0) for r in rows]) for v in ("keep", "sum")}
    md = [f"# TASKS 23 step 0 — is 'other-low' a matter of range? Truncating the TRUE correction — {datetime.now():%Y-%m-%d %H:%M}", "",
          "Hold-out (a), analytic ωB97X − analytic B3LYP; off-diagonal blocks between atoms farther apart than r zeroed; 'keep' leaves the diagonal "
          "blocks, 'sum' re-makes them from the acoustic sum rule. Errors are corrected-ω rms against the untruncated correction (identity check: max "
          f"|error| at r = ∞ is {max(r['identity'] for r in rows):.1e} cm⁻¹). The models' column is chain 34's three seeds on the same targets (5 Oct record).", "",
          "## Pooled (rms, cm⁻¹)", "", "| truncation | " + " | ".join(GROUPS) + " |", "|---|" + "---|" * len(GROUPS)]
    for k in keys:
        md.append(f"| {k.replace('_', ' r = ')} Å | " + " | ".join(f"{pooled_t[k][g]:.2f}" for g in GROUPS) + " |")
    md.append("| **models (chain 34)** | " + " | ".join(f"{pooled_m[g]:.2f}" for g in GROUPS) + " |")
    md += ["", "## other-low per molecule (cm⁻¹): truncation at 5 Å (keep / sum) and the models", "", "| molecule | atoms | n low modes | keep 5 Å | sum 5 Å | models |", "|---|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['id']} | {r['n_atoms']} | {r['n']['other-low']} | {r['trunc']['keep_5.0'].get('other-low', float('nan')):.2f} | "
                  f"{r['trunc']['sum_5.0'].get('other-low', float('nan')):.2f} | {r['models'].get('other-low', float('nan')):.2f} |")
    lo5 = {v: pooled_t[f"{v}_5.0"]["other-low"] for v in ("keep", "sum")}
    best = min(lo5.values())
    verdict = ("range is a cause — the design starts with range" if best >= 2.0 and max(rho.values()) >= 0.6 else
               "range is not the cause — the design starts with the torsion environment" if best <= 1.0 else
               "between the lines — range and the torsion environment both go into the design note")
    md += ["", f"Spearman ρ (truncation at 5 Å vs the models, other-low, ten molecules): keep {rho['keep']:.2f}, sum {rho['sum']:.2f}.", "",
           f"**Reading rule:** other-low cost of the 5 Å truncation {lo5['keep']:.2f} (keep) / {lo5['sum']:.2f} (sum) cm⁻¹ → {verdict}."]
    out.with_suffix(".md").write_text("\n".join(md) + "\n", encoding="utf-8")
    out.with_suffix(".json").write_text(json.dumps(dict(date=datetime.now().strftime("%Y-%m-%d %H:%M"), rows=rows, pooled=pooled_t, pooled_models=pooled_m,
                                                        spearman=rho, verdict=verdict), indent=1), encoding="utf-8")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
