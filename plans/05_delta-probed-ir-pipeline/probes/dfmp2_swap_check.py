"""The swap test of GoalGathering/notes/PreRegistration_2026-10-19_DFMP2_Composite_Step.md (step 3, S): with the conventional MP2/DZ
Hessian as base, the vibrational frequencies of M_DZ + Δ_DF against M_DZ + Δ_conv (the conventional MP2/TZ Hessian), Δ = M_TZ − M_DZ.
Lines, per molecule: max |Δω| ≤ 0.5 cm⁻¹ → adopt; ≤ 2.0 → noted; > 2.0 → refused.

    python probes/dfmp2_swap_check.py --geometry <corpus geometry.json> --conv-dz A.npz --conv-tz B.npz --df-dz C.npz --df-tz D.npz --out <prefix>

The four row files must share one geometry (the DF rows are computed at the conventional files' stored coordinates); the corpus geometry
gives the symbols and masses and must be the same molecule in the same atom order (equal interatomic distances; it may be rotated).
Writes <prefix>.json and <prefix>.md.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import e8_symmetry as SYM
from cc_composite_full_check import assemble, frequencies_cm, load_geometry

LINE_ADOPT = 0.5      # cm⁻¹, max |Δω|
LINE_REFUSE = 2.0
SAME_GEOMETRY = 1e-10     # bohr: the DF rows were computed at the stored coordinates themselves
SAME_MOLECULE = 1e-4      # bohr: interatomic distances of the corpus geometry against the stored one


def distances(x: np.ndarray) -> np.ndarray:
    return np.linalg.norm(x[:, None, :] - x[None, :, :], axis=-1)


def check_same_molecule(x_rows: np.ndarray, x_corpus: np.ndarray) -> None:
    if x_rows.shape != x_corpus.shape or np.abs(distances(x_rows) - distances(x_corpus)).max() > SAME_MOLECULE:
        raise SystemExit("the corpus geometry is not the row files' molecule in the same atom order (interatomic distances differ)")


def swap_shift(M_dz: np.ndarray, D_conv: np.ndarray, D_df: np.ndarray, masses: np.ndarray, x0: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """The vibrational frequencies (cm⁻¹, sorted) of the base plus each basis step."""
    return frequencies_cm(M_dz + D_conv, masses, x0), frequencies_cm(M_dz + D_df, masses, x0)


def verdict(max_shift: float) -> str:
    if max_shift <= LINE_ADOPT:
        return "adopt"
    return "noted" if max_shift <= LINE_REFUSE else "refused"


def load_rows(paths: dict[str, Path]) -> tuple[dict[str, np.lib.npyio.NpzFile], np.ndarray]:
    files = {k: np.load(p) for k, p in paths.items()}
    x0 = np.asarray(files["conv_dz"]["coords_bohr"], float)
    for k, z in files.items():
        if np.abs(np.asarray(z["coords_bohr"], float) - x0).max() > SAME_GEOMETRY:
            raise SystemExit(f"{paths[k]}: computed at another geometry than {paths['conv_dz']}")
    for k in ("df_dz", "df_tz"):
        ref = files["conv_" + k[3:]]
        for key in ("step", "frozen", "basis", "cart"):
            if np.asarray(files[k][key]).tolist() != np.asarray(ref[key]).tolist():
                raise SystemExit(f"{paths[k]}: {key} {files[k][key]} differs from the conventional file's {ref[key]}")
    return files, x0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--geometry", required=True)
    for k in ("conv-dz", "conv-tz", "df-dz", "df-tz"):
        ap.add_argument(f"--{k}", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    paths = {k: Path(getattr(a, k)) for k in ("conv_dz", "conv_tz", "df_dz", "df_tz")}
    _, x0 = load_rows(paths)
    symbols, x_corpus, masses = load_geometry(Path(a.geometry))
    check_same_molecule(x0, x_corpus)
    n = len(symbols)
    ops = SYM.point_group_ops(symbols, x0)
    _, reps = SYM.unique_displacements(ops, n)
    M = {k: assemble(p, ops, reps, n) for k, p in paths.items()}
    D_conv, D_df = M["conv_tz"][0] - M["conv_dz"][0], M["df_tz"][0] - M["df_dz"][0]
    w_conv, w_df = swap_shift(M["conv_dz"][0], D_conv, D_df, masses, x0)
    shift = w_df - w_conv
    res = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "geometry": a.geometry, "rows": {k: str(p) for k, p in paths.items()},
           "max_abs_shift_cm": float(np.abs(shift).max()), "rms_shift_cm": float(np.sqrt(np.mean(shift ** 2))),
           "step_difference_ratio": float(np.sqrt(np.mean((D_df - D_conv) ** 2)) / np.sqrt(np.mean(D_conv ** 2))),
           "symmetry_spread": {k: v[1] for k, v in M.items()}, "omega_conv": w_conv.tolist(), "omega_df": w_df.tolist()}
    res["verdict"] = verdict(res["max_abs_shift_cm"])
    md = [f"# DF-MP2 swap test — {Path(a.geometry).parent.name} ({res['date']})", "",
          f"max |Δω| {res['max_abs_shift_cm']:.3f} cm⁻¹, rms {res['rms_shift_cm']:.3f} cm⁻¹ over {len(shift)} modes; "
          f"rms(Δ_DF − Δ_conv)/rms(Δ_conv) {res['step_difference_ratio']:.2e}; symmetry spread "
          + ", ".join(f"{k} {v:.1e}" for k, v in res["symmetry_spread"].items()) + ".", "",
          f"**Line (≤ {LINE_ADOPT} adopt, ≤ {LINE_REFUSE} noted, above refused): {res['verdict']}**", "",
          "| ω conventional step (cm⁻¹) | ω DF step | Δ |", "|---|---|---|"]
    md += [f"| {c:.2f} | {d:.2f} | {d - c:+.3f} |" for c, d in zip(w_conv, w_df, strict=True)]
    Path(a.out + ".json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    Path(a.out + ".md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md[:5]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
