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
import e7_rungB_reread_analytic as RR  # noqa: E402
import e7_t2_sqm as T2  # noqa: E402
from e11_noise_floor import freqs_cm, vib_only  # noqa: E402
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


def partial_row(d: Path) -> dict:
    """A row directory without the full set of four Hessians (today: benzene⁺ lacks the FD ωB97X): what can still be read — the B3LYP frequencies,
    FD against analytic — so that the gate names the gap instead of skipping the row silently."""
    g = json.load(open(d / "geometry.json", encoding="utf-8"))
    masses = np.asarray(g["masses_amu"], float)
    have = {k: (d / f"hessian_{k}.npz").exists() for k in ("b3lyp", "wb97x", "b3lyp_analytic", "wb97x_analytic")}
    rec = {"id": d.name, "n_atoms": len(masses), "incomplete": True, "files": have}
    if have["b3lyp"] and have["b3lyp_analytic"]:
        fd = np.sort(vib_only(freqs_cm(np.load(d / "hessian_b3lyp.npz")["H_projected"], masses)))
        an = np.sort(vib_only(freqs_cm(np.load(d / "hessian_b3lyp_analytic.npz")["H_projected"], masses)))
        rec["b3lyp_freq_fd_vs_analytic_rms"] = float(np.sqrt(np.mean((fd - an) ** 2)))
        rec["n_imaginary_analytic_b3lyp"] = int((freqs_cm(np.load(d / "hessian_b3lyp_analytic.npz")["H_projected"], masses) < -5).sum())
    return rec


def rows_from_dirs(dirs: list[Path], log=print) -> tuple[list[dict], list[dict]]:
    """P3-2, the cation gate (decision 54): the per-family floor of arbitrary row directories (cation rows, hold-out rows computed outside the corpus).
    Rows with both FD Hessians and both analytic ones go through the corpus loader on a temporary directory (the family labels come from the same
    labeller as the corpus) and `floor_rows`; incomplete rows get `partial_row`. Returns (floor rows, partial rows)."""
    import shutil
    import tempfile
    full, partial = [], []
    for d in dirs:
        d = Path(d)
        if all((d / f"hessian_{k}.npz").exists() for k in ("b3lyp", "wb97x", "b3lyp_analytic", "wb97x_analytic")):
            full.append(d)
        else:
            partial.append(partial_row(d))
            log(f"{d.name}: incomplete row — {partial[-1].get('b3lyp_freq_fd_vs_analytic_rms', float('nan')):.2f} cm⁻¹ B3LYP FD vs analytic; files {partial[-1]['files']}")
    if not full:
        return [], partial
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "molecules"
        root.mkdir()
        for d in full:
            shutil.copytree(d, root / d.name)
        mols = T2.load(str(root))
        for i, m in mols.items():
            RR.substitute(m, root / i)
        rows = floor_rows(mols, root, list(mols))
    return rows, partial


def gate_verdict(rows: list[dict], limit: float) -> dict:
    """The registered line of P3-2: floor ≤ limit in every family present → FD-only rows may follow; else every cation row carries the analytic route."""
    med = {f: float(np.median([r["fd_vs_analytic"][f] for r in rows if f in r["fd_vs_analytic"]])) for f in FAMILIES
           if any(f in r["fd_vs_analytic"] for r in rows)}
    return {"n_rows": len(rows), "median_floor": med, "limit": limit, "pass": bool(rows) and all(v <= limit for v in med.values())}


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
    ap.add_argument("molecules", nargs="?", default="corpus/molecules")
    ap.add_argument("out_prefix")
    ap.add_argument("--pattern", default="f")
    ap.add_argument("--lam", type=float, default=1e-3)
    ap.add_argument("--cache-dir", default="out/ls_targets")
    ap.add_argument("--parts", default="floor,ceiling")
    ap.add_argument("--dirs", nargs="+", default=None, help="P3-2 cation gate: row directories outside the corpus (floor only); the molecules argument is then unused")
    ap.add_argument("--gate-limit", type=float, default=1.5, help="the registered line: median floor per family ≤ this (cm⁻¹) → FD-only rows may follow")
    a = ap.parse_args()
    t0 = time.time()
    if a.dirs:
        rows, partial = rows_from_dirs([Path(d) for d in a.dirs], print)
        verdict = gate_verdict(rows, a.gate_limit)
        res = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "dirs": a.dirs, "floor_rows": rows, "partial_rows": partial, "gate": verdict,
               "seconds": round(time.time() - t0, 1)}
        md = [f"# Cation gate (P3-2) — per-family noise floor of {len(a.dirs)} row directories — {res['date']}", "",
              f"**Gate:** median floor per family ≤ {a.gate_limit:g} cm⁻¹ → **{'PASS: FD-only rows may follow' if verdict['pass'] else 'NOT PASSED: every cation row carries the analytic route'}** "
              f"({verdict['n_rows']} complete rows; medians {fmt(verdict['median_floor']) if verdict['median_floor'] else 'none'}).", ""]
        md += [f"- {r['id']}: {fmt(r['fd_vs_analytic'])}" for r in rows]
        md += [f"- {r['id']}: **incomplete** (files {', '.join(k for k, v in r['files'].items() if v)}); B3LYP FD vs analytic "
               f"{r.get('b3lyp_freq_fd_vs_analytic_rms', float('nan')):.2f} cm⁻¹, imaginary (analytic) {r.get('n_imaginary_analytic_b3lyp', '?')}" for r in partial]
        Path(a.out_prefix + ".json").write_text(json.dumps(res, indent=1), encoding="utf-8")
        Path(a.out_prefix + ".md").write_text("\n".join(md + ["", f"{res['seconds']} s."]), encoding="utf-8")
        print("gate:", "PASS" if verdict["pass"] else "NOT PASSED", verdict["median_floor"], "| incomplete rows:", len(partial))
        return 0 if verdict["pass"] else 1
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
