"""Every mode a label marked as outside VPT2's domain, solved on a block of its own modes (TASKS 209).

    python probes/solve_marked_modes.py <label.json> <setting dir: qff_report.npz> <out dir> --block one|pair

A marked mode is a fundamental VPT2 cannot state. This solves it instead, on a block of modes taken from the same force field:

    one   the mode alone: its φ_iii and φ_iiii
    pair  the mode and the partner carrying the largest |x_ij| the label recorded, with every cubic and semi-diagonal quartic
          constant of the two (`dpir.qff.block_cubic` and `block_quartic`). The quartic ones need φ_ijkk, which reports written
          before 13 November 2026 do not carry; `probes/qff_quartic_tensor.py` derives it from the displaced Hessians on disk and
          writes `qff_quartic_tensor.npz` beside the report, which this reads.

**A block may only replace what it dominates.** Beside the block's own second-order value — taken from the same diagonalisation by
`dpir.mode_solver.block_second_order`, not from a second set of formulas — VPT2 adds everything the block does not hold. Call that the
outside part. Where it is small, the corrected fundamental is VPT2's with the block's part solved instead of perturbed. Where it is
itself large, the two are a near cancellation of large numbers and replacing one half breaks it, so no corrected fundamental is given
and the row says how large the outside part is. The bound is `vpt2_domain.STRAIN_MAX` × ω, the same tenth that marked the mode.

A block whose potential falls away in some direction is reported as refused with its reason, not dropped and not guessed. Everything
goes to solved_modes.json and solved_modes.md.
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

from dpir.mode_solver import block_second_order, by_order, corrected_fundamentals, solve_block  # noqa: E402
from dpir.qff import block_cubic, block_quartic  # noqa: E402
from dpir.vpt2_domain import STRAIN_MAX  # noqa: E402

TENSOR_NAME = "qff_quartic_tensor.npz"


def one_mode_constants(report: Any, mode: int) -> dict[tuple[int, ...], float]:
    """The one-mode block's own force constants, keyed as a block's are: φ_iii and φ_iiii."""
    return by_order({3: float(report["phi_ijk"][mode, mode, mode]), 4: float(np.diag(report["phi_iijj_sym"])[mode])})


def pair_constants(report: Any, tensor: np.ndarray, modes: tuple[int, int]) -> tuple[dict[tuple[int, ...], float], float]:
    """A two-mode block's constants with indices local to the block, and the worst disagreement between the quartic routes."""
    local = {mode: position for position, mode in enumerate(modes)}
    quartic = block_quartic(tensor, modes)
    out = {tuple(local[i] for i in key): value for key, value in block_cubic(report["phi_ijk"], modes).items()}
    out |= {tuple(local[i] for i in key): value for key, value in quartic.constants.items()}
    return out, quartic.worst_spread


def load_tensor(setting: Path, n_modes: int) -> np.ndarray:
    """φ_ijkk of this force field, from the report when it carries it and otherwise from the file derived beside it."""
    with np.load(setting / "qff_report.npz") as report:
        if "phi_ijkk" in report.files:
            return np.asarray(report["phi_ijkk"])
    path = setting / TENSOR_NAME
    if not path.is_file():
        raise FileNotFoundError(f"{path} is missing: derive it with probes/qff_quartic_tensor.py, which verifies the rebuild against "
                                f"the stored report before writing")
    with np.load(path) as stored:
        tensor = np.asarray(stored["phi_ijkk"])
    if tensor.shape != (n_modes, n_modes, n_modes):
        raise ValueError(f"{path}: {tensor.shape} for {n_modes} modes")
    return tensor


def solve_one(omega: np.ndarray, nu: np.ndarray, constants: dict[tuple[int, ...], float], modes: tuple[int, ...]) -> dict[str, Any]:
    """One block solved: the outside part, whether it is covered, and the corrected fundamental of the marked mode when it is."""
    block_omega = [float(omega[m]) for m in modes]
    block_nu = [float(nu[m]) for m in modes]
    second = block_second_order(block_omega, constants, modes)
    outside = block_nu[0] - second[0]
    row = {"block": list(modes), "outside_cm": outside, "covered": abs(outside) <= STRAIN_MAX * block_omega[0],
           "second_order_cm": second[0]}
    try:
        solution = solve_block(block_omega, constants, modes)
    except ValueError as refusal:
        return {**row, "solved": False, "reason": str(refusal)}
    corrected, _ = corrected_fundamentals(block_omega, constants, block_nu, modes)
    row |= {"solved": True, "block_exact_cm": solution.fundamental(modes[0]), "quanta": solution.quanta,
            "overlap": min(solution.overlaps), "correction_cm": solution.fundamental(modes[0]) - second[0]}
    if not row["covered"]:
        return {**row, "reason": f"the block does not cover the breakdown: VPT2 puts {outside:+.1f} cm-1 outside it, over "
                                 f"{STRAIN_MAX:.2f} x omega = {STRAIN_MAX * block_omega[0]:.1f}"}
    return {**row, "nu_corrected_cm": corrected[0]}


def solve_label(label: dict[str, Any], report: Any, setting: Path | None, block: str) -> dict[str, Any]:
    """Every marked mode of one label, on a block of the chosen size."""
    omega, nu = np.asarray(label["omega"], float), np.asarray(label["nu_gvpt2"], float)
    domain = label.get("vpt2_domain")
    if domain is None:
        raise ValueError(f"{label['id']}: no vpt2_domain record; relabel with probes/gvpt2_labels.py (TASKS 207)")
    partner = {d["mode"]: d["partner"] for d in domain["diagnostics"]}
    share = {d["mode"]: d["partner_share"] for d in domain["diagnostics"]}
    tensor = load_tensor(setting, len(omega)) if block == "pair" and domain["marked"] else None
    rows = []
    for i in (int(m) for m in domain["marked"]):
        head = {"mode": i, "omega_cm": float(omega[i]), "nu_vpt2_cm": float(nu[i]), "partner": partner.get(i),
                "partner_share": share.get(i)}
        if block == "one":
            rows.append({**head, "route_spread_cm": 0.0, **solve_one(omega, nu, one_mode_constants(report, i), (i,))})
            continue
        modes = (i, int(partner[i]))
        constants, spread = pair_constants(report, tensor, modes)
        rows.append({**head, "route_spread_cm": spread, **solve_one(omega, nu, constants, modes)})
    return {"id": label["id"], "block": block, "marked": list(domain["marked"]), "modes": rows}


def report_lines(res: dict[str, Any]) -> list[str]:
    """One table of what the blocks changed, and what they could not reach."""
    lines = [f"# {res['block']}-mode blocks of {res['id']} (TASKS 209)", "",
             "| mode | block | ω | ν(VPT2) | second order | outside | block exact | correction | ν corrected |",
             "|---|---|---|---|---|---|---|---|---|"]
    for r in res["modes"]:
        head = (f"| {r['mode']} | {'+'.join(str(m) for m in r['block'])} | {r['omega_cm']:.2f} | {r['nu_vpt2_cm']:.2f} | "
                f"{r['second_order_cm']:.2f} | {r['outside_cm']:+.1f} | ")
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
    worst = max((r["route_spread_cm"] for r in res["modes"]), default=0.0)
    if worst:
        lines.append(f"- the quartic constants' two routes disagree by at most {worst:.1f} cm-1 over these blocks")
    return lines


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("label", type=Path, help="a probes/gvpt2_labels.py json carrying a vpt2_domain record")
    ap.add_argument("setting", type=Path, help="the molecule's setting directory, holding qff_report.npz")
    ap.add_argument("out", type=Path)
    ap.add_argument("--block", required=True, choices=("one", "pair"), help="the mode alone, or with the partner carrying its "
                                                                            "largest x_ij")
    a = ap.parse_args(argv)
    label = json.loads(a.label.read_text(encoding="utf-8"))
    with np.load(a.setting / "qff_report.npz") as report:
        res = solve_label(label, report, a.setting, a.block)
    os.makedirs(a.out, exist_ok=True)
    write_atomic(str(a.out / f"solved_modes_{a.block}.json"), json.dumps(res, indent=1))
    lines = report_lines(res)
    write_atomic(str(a.out / f"solved_modes_{a.block}.md"), "\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
