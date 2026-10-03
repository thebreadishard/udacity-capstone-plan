"""Decision 53 (3 Oct 2026), chain 34 step 0 and 1 — two measurements before any training on the open T1 families (CH-oop, other):

floor    per mode family, the corrected-ω noise floor of the proxy targets: the FD correction (psi4 deck) against the analytic second-route correction
         (pyscf), both read in the analytic B3LYP mode basis, on the molecules that carry both (e11_noise_floor pooled this over all modes: 1.5 cm⁻¹).
         Nothing can be read below a family's floor on FD targets.
ceiling  per mode family, the representation ceiling of the hybrid head on hold-out (a): the head's output is Bᵀ ΔF B with ΔF supported on the pattern,
         so the best it can do is the mass-weighted least-squares ΔF on that support (the ridge LS target, λ 1e-3) — its corrected ω per family against
         the truth is the floor of any training recipe with this head; the 'projected' column is what the carried recipe's own target (B⁺ᵀ ΔH B⁺ on the
         pattern) reconstructs to.

Usage: python probes/rungC_family_floor_ceiling.py corpus/molecules out/<prefix> [--pattern f] [--lam 1e-3] [--cache-dir out/ls_targets]
Run from modules/05_support_predictor. Writes <prefix>.json and <prefix>.md.
"""
import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "modules" / "05_support_predictor" / "m05"))
import e7_t2_sqm as T2  # noqa: E402
from rungC_cc_transfer import family_freq_rms  # noqa: E402
from rungC_targets import cached_pattern_ls_target, projected_target  # noqa: E402
from rungC_train import load_corpus, pattern_classes  # noqa: E402

FAMILIES = ("ring-ip", "CH-stretch", "CH-oop", "other")


def pooled(rows: list[dict], key: str) -> dict:
    """Pooled rms over molecules of a per-molecule per-family rms (as e11_noise_floor pools), per family."""
    out = {}
    for f in FAMILIES:
        v = [r[key][f] for r in rows if f in r[key]]
        out[f] = float(np.sqrt(np.mean(np.square(v)))) if v else float("nan")
    return out


def floor_rows(mols: dict, molecules: Path, substituted: list) -> list[dict]:
    rows = []
    for i in substituted:
        if i not in mols:                                   # dropped by the loader (imaginary mode)
            continue
        m = mols[i]
        d = molecules / i
        dH_fd = np.load(d / "hessian_wb97x.npz")["H_projected"] - np.load(d / "hessian_b3lyp.npz")["H_projected"]
        rows.append({"id": i, "n_atoms": len(m["masses"]), "fd_vs_analytic": family_freq_rms(m, T2.K_from_dH(m, dH_fd))})
    return rows


def ceiling_rows(mols: dict, molecules: Path, ids: list, pattern: str, lam: float, cache_dir: Path, log) -> list[dict]:
    rows = []
    for i in ids:
        m = mols[i]
        B = np.asarray(m["B"], float)
        mask = (pattern_classes(molecules / i, m, pattern) >= 0).numpy()
        t0 = time.time()
        X, cached = cached_pattern_ls_target(cache_dir, i, pattern, m["dH_true"], B, m["masses"], mask, lam_rel=lam)
        X0 = np.where(mask, projected_target(m["dH_true"], B), 0.0)
        r = {"id": i, "n_atoms": len(m["masses"]), "pattern_entries": int(np.triu(mask).sum()),
             "ls": family_freq_rms(m, T2.K_from_dH(m, B.T @ X @ B)),
             "projected": family_freq_rms(m, T2.K_from_dH(m, B.T @ X0 @ B)),
             "zero": family_freq_rms(m, np.zeros_like(m["K"]))}
        rows.append(r)
        log(f"{i} ({r['n_atoms']} atoms, {'cached' if cached else f'{time.time() - t0:.0f} s'}): ls {fmt(r['ls'])} | projected {fmt(r['projected'])}")
    return rows


def fmt(d: dict) -> str:
    return " ".join(f"{f} {d[f]:.2f}" for f in FAMILIES if f in d)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("molecules")
    ap.add_argument("out_prefix")
    ap.add_argument("--pattern", default="f")
    ap.add_argument("--lam", type=float, default=1e-3)
    ap.add_argument("--cache-dir", default="out/ls_targets")
    ap.add_argument("--parts", default="floor,ceiling")
    a = ap.parse_args()
    t0 = time.time()
    molecules = Path(a.molecules)
    mols, test_a, _test_b, _cores, _pool, substituted = load_corpus(str(molecules), True)
    res = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "pattern": a.pattern, "lam": a.lam, "holdout_a": test_a, "analytic_pairs": substituted}
    md = [f"# Per-family floor and ceiling at the proxy level — {res['date']}", ""]
    if "floor" in a.parts:
        rows = floor_rows(mols, molecules, substituted)
        res["floor_rows"] = rows
        res["floor_pooled"] = pooled(rows, "fd_vs_analytic")
        res["floor_median"] = {f: float(np.median([r["fd_vs_analytic"][f] for r in rows if f in r["fd_vs_analytic"]])) for f in FAMILIES}
        worst = max(rows, key=lambda r: r["fd_vs_analytic"].get("ring-ip", 0.0))
        md += [f"**Noise floor** (FD − analytic correction, corrected ω per family, {len(rows)} molecules with both routes, cm⁻¹). The pooled rms is "
               f"carried by single molecules with a bad FD deck (worst {worst['id']}: {fmt(worst['fd_vs_analytic'])}); the median is the floor of a typical target.", "",
               "| family | median | pooled rms |", "|---|---|---|"]
        md += [f"| {f} | **{res['floor_median'][f]:.2f}** | {res['floor_pooled'][f]:.2f} |" for f in FAMILIES] + [""]
        print("floor median:", fmt(res["floor_median"]), "| pooled:", fmt(res["floor_pooled"]))
    if "ceiling" in a.parts:
        rows = ceiling_rows(mols, molecules, test_a, a.pattern, a.lam, Path(a.cache_dir), print)
        res["ceiling_rows"] = rows
        for k in ("ls", "projected", "zero"):
            res[f"ceiling_{k}_pooled"] = pooled(rows, k)
        md += [f"**Representation ceiling of the pattern-{a.pattern} head** on hold-out (a) ({len(rows)} molecules; corrected ω per family against the "
               f"truth, pooled rms, cm⁻¹): 'ls' = the best ΔF on the pattern (ridge λ {a.lam:g}), 'projected' = the carried recipe's own target, "
               "'zero' = no correction.", "", "| family | ls (ceiling) | projected target | zero rule |", "|---|---|---|---|"]
        md += [f"| {f} | **{res['ceiling_ls_pooled'][f]:.2f}** | {res['ceiling_projected_pooled'][f]:.2f} | {res['ceiling_zero_pooled'][f]:.2f} |" for f in FAMILIES]
        md += ["", "Per molecule (ls): " + "; ".join(f"{r['id']} {fmt(r['ls'])}" for r in rows), ""]
        print("ceiling ls:", fmt(res["ceiling_ls_pooled"]), "| projected:", fmt(res["ceiling_projected_pooled"]))
    res["seconds"] = round(time.time() - t0, 1)
    Path(a.out_prefix + ".json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    Path(a.out_prefix + ".md").write_text("\n".join(md + [f"{res['seconds']} s."]), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
