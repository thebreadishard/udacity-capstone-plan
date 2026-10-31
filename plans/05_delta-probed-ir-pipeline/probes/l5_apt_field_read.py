"""The read of `l5_apt_field` (TASKS 49; chain 42's registered risk 4): the field route as the APT's second route for the large PAHs whose
labels-route APT failed its translation sum rule. Lines fixed on 31 Oct 2026 before any output of the run:

    A  the field route's APT with grid response, Richardson over F and 2F (R = (4 A(F) − A(2F)) / 3, L4's D1), meets the labels route's
       sum-rule limit (5e-4 e, unchanged).
    B  the field route without grid response, Richardson, lies within L4's line (1e-4 e) of the labels-route APT: both take the same
       derivative on a fixed grid, so the labels route's miss is the missing grid response and not its response
       (`apt_l4_diag.diagnose`, one implementation).

Both hold → the Richardson APT with grid response is the molecule's APT for the intensity read: `<id>/dipole_b3lyp_field.npz`, passed=True.
Either fails → passed=False, the intensity read loses the molecule, examined further. Reported beside: max |R − labels APT| and the band
heights on the B3LYP Hessian with either APT (rel. rms over the bands above 1 % of the strongest, and the largest change among them).

    python probes/l5_apt_field_read.py [--dir probes/results_m1/l5_apt_field_2026-10-31]     # l5_apt_field_read.{json,md} in --dir
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "modules" / "05_support_predictor" / "corpus"))
import apt_l4_diag as D  # noqa: E402
from apt import SUM_RULE_LIMIT, intensities, sum_rule  # noqa: E402

FIELDS = ("1e-3", "2e-3")
STRONG = 0.01                       # bands above this fraction of the strongest enter the height comparison
OUT_APT = "dipole_b3lyp_field.npz"
DEFAULT_DIR = HERE / "results_m1" / "l5_apt_field_2026-10-31"


def richardson(a1: np.ndarray, a2: np.ndarray) -> np.ndarray:
    """The F² term removed from central differences at F (a1) and 2F (a2)."""
    return (4 * a1 - a2) / 3


def load_field(d: Path) -> dict[str, dict[str, np.ndarray]]:
    """Both grid modes at both fields; refuses a molecule whose run has not written both."""
    missing = [f for f in FIELDS if not (d / f"field_F{f}.npz").exists()]
    if missing:
        raise SystemExit(f"{d.name}: no field-route output at F = {', '.join(missing)}")
    out = {}
    for f in FIELDS:
        with np.load(d / f"field_F{f}.npz") as z:
            out[f] = {"no_gr": np.array(z["apt_no_grid_response"], float), "gr": np.array(z["apt_grid_response"], float)}
    return out


def heights(P_new: np.ndarray, P_old: np.ndarray, H: np.ndarray, masses: np.ndarray) -> dict:
    """Band heights with either APT on the same Hessian: rel. rms and largest relative change over the strong bands."""
    _, k_new = intensities(P_new, H, masses)
    freq, k_old = intensities(P_old, H, masses)
    strong = k_old > STRONG * k_old.max()
    rel = (k_new[strong] - k_old[strong]) / k_old[strong]
    return {"strong_bands": int(strong.sum()), "rel_rms": float(np.sqrt(np.mean(rel**2))), "rel_max": float(np.abs(rel).max()),
            "strong_band_cm": [round(float(x), 1) for x in freq[strong]]}


def assess(P_labels: np.ndarray, field: dict, H: np.ndarray, masses: np.ndarray) -> tuple[dict, np.ndarray]:
    """Lines A and B for one molecule, the comparison beside them, and the Richardson APT with grid response."""
    R = richardson(field[FIELDS[0]]["gr"], field[FIELDS[1]]["gr"])
    sr = sum_rule(R)
    two_route = D.diagnose(P_labels, field[FIELDS[0]]["no_gr"], field[FIELDS[1]]["no_gr"])
    line_a, line_b = sr <= SUM_RULE_LIMIT, two_route["max_diff_richardson_e"] <= D.LINE_E
    res = {"line_A": {"sum_rule_e": sr, "limit_e": SUM_RULE_LIMIT, "holds": bool(line_a)},
           "line_B": {"max_diff_richardson_e": two_route["max_diff_richardson_e"], "line_e": D.LINE_E, "holds": bool(line_b),
                      "diagnosis": two_route},
           "passed": bool(line_a and line_b), "labels_sum_rule_e": sum_rule(P_labels),
           "max_diff_to_labels_apt_e": float(np.abs(R - P_labels).max()), "heights": heights(R, P_labels, H, masses)}
    return res, R


def write_apt(d: Path, R: np.ndarray, res: dict) -> None:
    """The molecule's field-route APT, through a temp file."""
    tmp = d / f"{OUT_APT}.tmp.npz"
    np.savez_compressed(tmp, apt=R, sum_rule_max=res["line_A"]["sum_rule_e"], passed=res["passed"], route="field_grid_response_richardson",
                        fields=np.array([float(f) for f in FIELDS]), xc="b3lyp", basis="6-31g*")
    os.replace(tmp, d / OUT_APT)


def read_molecule(d: Path) -> dict:
    with np.load(d / D.APT_FILE) as z:
        P_labels = np.array(z["apt"], float)
    with np.load(d / "hessian_b3lyp_analytic.npz") as z:
        H = np.array(z["H_projected"], float)
    masses = np.array(json.loads((d / "geometry.json").read_text(encoding="utf-8"))["masses_amu"], float)
    res, R = assess(P_labels, load_field(d), H, masses)
    write_apt(d, R, res)
    return res


def ids(folder: Path) -> list[str]:
    lines = (folder / "ids.tsv").read_text(encoding="utf-8").splitlines()
    return [s.split("\t")[0] for s in lines if s.strip() and not s.startswith("#")]


def report(rows: dict) -> str:
    out = ["# The field route as the APT's second route for the large PAHs (TASKS 49)", "",
           "| molecule | A: sum rule (≤ 5e-4) | B: Richardson vs labels APT (≤ 1e-4 e) | passed | heights rel. rms / max (strong bands) |",
           "|---|---|---|---|---|"]
    for i, r in rows.items():
        h = r["heights"]
        out.append(f"| {i} | {r['line_A']['sum_rule_e']:.1e} | {r['line_B']['max_diff_richardson_e']:.1e} | {r['passed']} | "
                   f"{h['rel_rms']:.3f} / {h['rel_max']:.3f} ({h['strong_bands']}) |")
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dir", type=Path, default=DEFAULT_DIR)
    a = ap.parse_args(argv)
    rows = {i: read_molecule(a.dir / i) for i in ids(a.dir)}
    (a.dir / "l5_apt_field_read.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    text = report(rows)
    (a.dir / "l5_apt_field_read.md").write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
