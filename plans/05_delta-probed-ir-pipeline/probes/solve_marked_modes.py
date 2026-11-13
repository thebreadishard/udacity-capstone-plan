"""Every mode a label marked as outside VPT2's domain, solved on its own one-mode block (TASKS 209 stage 1).

    python probes/solve_marked_modes.py <label.json> <setting dir: qff_report.npz> <out dir>

For each marked mode the block holds the mode's own constants — φ_iii from the force field's cubic tensor and φ_iiii from the diagonal
of its semi-diagonal quartic one — and `dpir.mode_solver` diagonalises it. The corrected fundamental is VPT2's with that block replaced
by its exact level spacing, so nothing the block did not solve is touched (`corrected_fundamental`).

A mode whose block is unbounded (a negative quartic constant) is reported as refused with its reason, not dropped and not guessed: it
needs a measured potential.

**A block may only replace what it dominates.** Beside the block's own second-order value ω + 2·x_ii(block), VPT2 adds everything the
block does not hold: the terms of x_ii that run through other modes, and every x_ij. Call that the outside part. Where it is small, the
corrected fundamental is VPT2's with the block's part solved instead of perturbed. Where it is itself large, the two parts are a near
cancellation of large numbers, and replacing one of them breaks the cancellation rather than mending it — so no corrected fundamental is
given, and the row says how large the outside part is. The bound is `vpt2_domain.STRAIN_MAX` × ω, the same tenth that marked the mode.

Measured on our six marked modes (13 November 2026): not one is covered. Coronene's rest on a direct quartic coupling to one partner
(x(24,36) = 69.8 cm⁻¹); the three corpus molecules each hold a low mode whose quartic (+148 to +203 cm⁻¹) is nearly cancelled by a cubic
coupling to an X–H stretch (φ_iik of 1,451 to 1,702 cm⁻¹, giving −127 to −248). Both need a block of more than one mode, and so the
semi-diagonal quartic constants a block of two would need — TASKS 209 stage 2.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "src"))
from s2_read import write_atomic  # noqa: E402

from dpir.mode_solver import block_x_cm, corrected_fundamental  # noqa: E402
from dpir.vpt2_domain import STRAIN_MAX  # noqa: E402


def block_constants(report: Any, mode: int) -> dict[int, float]:
    """The one-mode block's own force constants: φ_iii and φ_iiii, in cm⁻¹."""
    return {3: float(report["phi_ijk"][mode, mode, mode]), 4: float(np.diag(report["phi_iijj_sym"])[mode])}


def outside_block_cm(omega_cm: float, nu_vpt2_cm: float, constants: dict[int, float]) -> float:
    """Everything VPT2 put into this fundamental that the one-mode block does not hold: the x_ii terms running through other modes,
    and every x_ij."""
    return nu_vpt2_cm - (omega_cm + 2.0 * block_x_cm(omega_cm, constants))


def solve_label(label: dict[str, Any], report: Any) -> dict[str, Any]:
    """Every marked mode of one label, solved or refused with its reason."""
    omega, nu = np.asarray(label["omega"], float), np.asarray(label["nu_gvpt2"], float)
    domain = label.get("vpt2_domain")
    if domain is None:
        raise ValueError(f"{label['id']}: no vpt2_domain record; relabel with probes/gvpt2_labels.py (TASKS 207)")
    share = {d["mode"]: d["partner_share"] for d in domain["diagnostics"]}
    partner = {d["mode"]: d["partner"] for d in domain["diagnostics"]}
    rows = []
    for i in (int(m) for m in domain["marked"]):
        constants = block_constants(report, i)
        row = {"mode": i, "omega_cm": float(omega[i]), "nu_vpt2_cm": float(nu[i]), "phi_iii_cm": constants[3],
               "phi_iiii_cm": constants[4], "partner": partner.get(i), "partner_share": share.get(i)}
        outside = outside_block_cm(float(omega[i]), float(nu[i]), constants)
        covers = abs(outside) <= STRAIN_MAX * float(omega[i])
        row |= {"outside_cm": outside, "covered": covers}
        try:
            corrected, solution = corrected_fundamental(float(omega[i]), constants, float(nu[i]))
        except ValueError as refusal:
            rows.append({**row, "solved": False, "reason": str(refusal)})
            continue
        row |= {"solved": True, "block_exact_cm": solution.fundamental_cm, "basis": solution.basis,
                "correction_cm": solution.fundamental_cm - (float(omega[i]) + 2.0 * block_x_cm(float(omega[i]), constants))}
        rows.append({**row, "nu_corrected_cm": corrected} if covers else
                    {**row, "reason": f"the block does not cover the breakdown: VPT2 puts {outside:+.1f} cm-1 outside it, over "
                                      f"{STRAIN_MAX:.2f} x omega = {STRAIN_MAX * float(omega[i]):.1f}"})
    return {"id": label["id"], "marked": list(domain["marked"]), "modes": rows}


def report_lines(res: dict[str, Any]) -> list[str]:
    """One table of what the blocks changed, and what they could not reach."""
    lines = [f"# One-mode blocks of {res['id']} (TASKS 209 stage 1)", "",
             "| mode | ω | φ_iii | φ_iiii | ν(VPT2) | outside the block | block exact | block correction | ν corrected |",
             "|---|---|---|---|---|---|---|---|---|"]
    for r in res["modes"]:
        head = (f"| {r['mode']} | {r['omega_cm']:.2f} | {r['phi_iii_cm']:.1f} | {r['phi_iiii_cm']:.1f} | {r['nu_vpt2_cm']:.2f} | "
                f"{r.get('outside_cm', float('nan')):+.1f} | ")
        if not r["solved"]:
            lines.append(head + "refused | — | — |")
        elif r.get("nu_corrected_cm") is None:
            lines.append(head + f"{r['block_exact_cm']:.2f} | {r['correction_cm']:+.2f} | not covered |")
        else:
            lines.append(head + f"{r['block_exact_cm']:.2f} | {r['correction_cm']:+.2f} | {r['nu_corrected_cm']:.2f} |")
    given = [r for r in res["modes"] if r.get("nu_corrected_cm") is not None]
    lines += ["", f"{len(given)} of {len(res['modes'])} marked mode(s) have a corrected fundamental; a block that does not cover the "
                  f"breakdown gives none."]
    lines += [f"- mode {r['mode']}: {r['reason']}" for r in res["modes"] if r.get("reason")]
    return lines


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("label", type=Path, help="a probes/gvpt2_labels.py json carrying a vpt2_domain record")
    ap.add_argument("setting", type=Path, help="the molecule's setting directory, holding qff_report.npz")
    ap.add_argument("out", type=Path)
    a = ap.parse_args(argv)
    label = json.loads(a.label.read_text(encoding="utf-8"))
    with np.load(a.setting / "qff_report.npz") as report:
        res = solve_label(label, report)
    os.makedirs(a.out, exist_ok=True)
    write_atomic(str(a.out / "solved_modes.json"), json.dumps(res, indent=1))
    lines = report_lines(res)
    write_atomic(str(a.out / "solved_modes.md"), "\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
