"""The XC quadrature error of the corpus's analytic Hessians, read from their translational invariance (TASKS 201, step 1).

pyscf's CPU DFT Hessian has no grid-weight derivative (pyscf#3437; software ledger row 56), so a rigid translation of the whole molecule,
whose curvature is exactly 0, gets a curvature from the quadrature. For every molecule with both analytic Hessians this probe reads, from
the unprojected `H_raw`: max|H t| (hartree/bohr^2, pyscf#3437's measure) and the rigid-translation curvature along x, y, z as a signed
frequency, for B3LYP, for wB97X and for their difference dH, the training target's Hessian. It also counts the vibrational modes whose
|frequency| lies below the B3LYP file's largest translation frequency (modes the file cannot resolve).

The per-mode label noise is an estimate, not a measurement: the target of mode i is the first-order shift (v_i' dH~ v_i) / (2 w_i), and a
curvature error of the translation's size, w_t(dH)^2 in cm^-2, moves it by w_t(dH)^2 / (2 w_i). The translation residual bounds the size
of the error, not its direction in the vibrational space; step 2 of TASKS 201 measures the vibrational error itself on two molecules.

Writes <out>/quadrature.csv (one row per molecule), <out>/quadrature.json (the summary) and <out>/quadrature.md.

    python probes/hessian_quadrature_check.py <corpus/molecules dir> <out dir>
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import tempfile
from pathlib import Path

import numpy as np

M05 = Path(__file__).resolve().parents[1] / "modules" / "05_support_predictor" / "m05"
sys.path.insert(0, str(M05))
from learning_curve_layerA import AMU2AU, FAMILIES, HARTREE2CM, molecule_features  # noqa: E402

TAGS = ("b3lyp", "wb97x")
NOISE_LEVELS_CM = (0.5, 1.0, 3.0)      # label-noise estimates counted per family; 3.0 is decision 53's line


def signed_cm(k_au: float) -> float:
    """A mass-weighted curvature (hartree / (bohr^2 me)) as a signed frequency in cm-1."""
    return float(np.sign(k_au) * np.sqrt(abs(k_au)) * HARTREE2CM)


def translation_residual(H: np.ndarray, masses_amu: np.ndarray) -> tuple[float, list[float]]:
    """max|H t| over the three unit translations and their curvatures as signed frequencies (cm-1)."""
    H = 0.5 * (H + H.T)
    worst, freqs = 0.0, []
    for ax in range(3):
        t = np.zeros(H.shape[0])
        t[ax::3] = 1.0
        worst = max(worst, float(np.abs(H @ t).max()))
        freqs.append(signed_cm(t @ H @ t / (masses_amu.sum() * AMU2AU)))
    return worst, freqs


def molecule_row(mol_dir: Path) -> tuple[dict, dict[str, list[float]]]:
    """One molecule's residuals and its per-mode noise estimates by family."""
    masses = np.asarray(json.loads((mol_dir / "geometry.json").read_text(encoding="utf-8"))["masses_amu"], dtype=float)
    raw, projected = {}, {}
    for tag in TAGS:
        with np.load(mol_dir / f"hessian_{tag}_analytic.npz") as z:
            raw[tag], projected[tag] = np.asarray(z["H_raw"], float), np.asarray(z["H_projected"], float)
    row: dict = {"id": mol_dir.name, "n_atoms": len(masses)}
    for tag, H in (*raw.items(), ("dH", raw["wb97x"] - raw["b3lyp"])):
        worst, freqs = translation_residual(H, masses)
        row[f"max_Ht_{tag}"] = worst
        row[f"w_t_{tag}"] = max(freqs, key=abs)
    feats = molecule_features(mol_dir, projected["b3lyp"], projected["wb97x"])
    freq = np.asarray(feats["freq"], float)
    row["lowest_cm"] = float(freq.min())
    row["n_unresolved"] = int((np.abs(freq) < abs(row["w_t_b3lyp"])).sum())
    noise = row["w_t_dH"] ** 2 / (2 * np.abs(freq))
    by_family = {f: [float(n) for n, fam in zip(noise, feats["family"], strict=True) if fam == f] for f in FAMILIES}
    return row, by_family


def summary(rows: list[dict], noise: dict[str, list[float]]) -> dict:
    """Percentiles of the translation frequencies, unresolved-mode counts and the per-family noise estimates."""
    out: dict = {"molecules": len(rows)}
    for tag in (*TAGS, "dH"):
        a = np.abs([r[f"w_t_{tag}"] for r in rows])
        out[f"w_t_{tag}_cm"] = {"median": float(np.median(a)), "p90": float(np.percentile(a, 90)), "max": float(a.max())}
    out["unresolved_modes"] = int(sum(r["n_unresolved"] for r in rows))
    out["molecules_with_unresolved"] = int(sum(r["n_unresolved"] > 0 for r in rows))
    out["noise_by_family_cm"] = {
        f: {"modes": len(v), "rms": float(np.sqrt(np.mean(np.square(v)))) if v else float("nan"),
            **{f"above_{lvl:g}": int(sum(x > lvl for x in v)) for lvl in NOISE_LEVELS_CM}}
        for f, v in noise.items()}
    return out


def write_atomic(path: Path, text: str) -> None:
    """Text through a temp file in the same folder, moved over the target."""
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    os.replace(tmp, path)


def markdown(s: dict) -> str:
    """quadrature.md: the summary as two tables."""
    lines = [f"# XC quadrature error of the analytic Hessians — {s['molecules']} molecules", "",
             "Rigid-translation curvature (exactly 0 in theory) as |frequency|, cm⁻¹:", "", "| Hessian | median | 90th pct | max |",
             "|---|---|---|---|"]
    lines += [f"| {t} | {s[f'w_t_{t}_cm']['median']:.2f} | {s[f'w_t_{t}_cm']['p90']:.2f} | {s[f'w_t_{t}_cm']['max']:.2f} |"
              for t in (*TAGS, "dH")]
    lines += ["", f"Modes below their B3LYP file's translation frequency: {s['unresolved_modes']} in {s['molecules_with_unresolved']} "
              "molecules.", "", "Estimated label noise per mode, w_t(dH)² / (2ω), cm⁻¹ (an estimate from the translation residual):", "",
              "| family | modes | rms | > 0.5 | > 1 | > 3 |", "|---|---|---|---|---|---|"]
    lines += [f"| {f} | {v['modes']} | {v['rms']:.3f} | {v['above_0.5']} | {v['above_1']} | {v['above_3']} |"
              for f, v in s["noise_by_family_cm"].items()]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("molecules", type=Path)
    ap.add_argument("out", type=Path)
    a = ap.parse_args(argv)
    dirs = sorted(d for d in a.molecules.iterdir() if all((d / f"hessian_{t}_analytic.npz").exists() for t in TAGS))
    if not dirs:
        raise SystemExit(f"{a.molecules}: no folder with both analytic Hessians")
    rows, noise = [], {f: [] for f in FAMILIES}
    for i, d in enumerate(dirs, 1):
        row, by_family = molecule_row(d)
        rows.append(row)
        for f, v in by_family.items():
            noise[f].extend(v)
        if i % 100 == 0:
            print(f"(HQC) {i}/{len(dirs)} molecules read", flush=True)
    a.out.mkdir(parents=True, exist_ok=True)
    s = summary(rows, noise)
    with tempfile.NamedTemporaryFile("w", dir=a.out, suffix=".tmp", delete=False, newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    os.replace(fh.name, a.out / "quadrature.csv")
    write_atomic(a.out / "quadrature.json", json.dumps(s, indent=1))
    write_atomic(a.out / "quadrature.md", markdown(s))
    print(markdown(s), flush=True)


if __name__ == "__main__":
    main()
