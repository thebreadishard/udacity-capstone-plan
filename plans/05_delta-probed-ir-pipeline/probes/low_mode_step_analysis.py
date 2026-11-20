"""Is the difference between the low-mode repair's two steps noise, or a bias of the step? (TASKS 218; the question behind amendment 3
of GoalGathering/notes/PreRegistration_2026-11-20_Low_Mode_Repair_Threshold.md.)

The registered read flagged every checked point: steps 0.01 and 0.02 bohr gave patched frequencies more than 0.15 cm⁻¹ apart. Two
causes leave different marks. A central difference of gradients measures a curvature with an error that grows as the square of the
step q (the quartic and higher terms along the direction), so doubling the step multiplies that error by four: the two steps then
differ by three times the small step's error, by an amount that belongs to the mode and does not change between repeats. Gradient
noise σ enters a curvature as σ/q instead: it halves on doubling and has no preferred sign.

For every molecule that was patched at both steps this script lists, per re-measured label mode and functional, the patched frequency
at each step, their signed difference, the same difference as a curvature (cm⁻²), and the noise the difference would carry at the
gradient noise the registration calibrated (section 2: σ between 1e-8 and 2e-8 hartree/bohr). Per direction it also lists the measured
curvature uᵀC at both steps in both functionals: the two functionals are separate SCFs, so their noise is independent, while a step
bias of the potential shows in both alike. A point whose mode has no single counterpart at either step is listed apart.

    python probes/low_mode_step_analysis.py --small <patches>=<labels> --large <patches>=<labels>
        --molecules <corpus molecules dir> --out <new results folder>

Writes STEP_ANALYSIS.md, step_points.csv and record.json into the results folder, each through a temp file. numpy only.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "corpus"))
import low_mode_threshold_read as R  # noqa: E402  the path lines above come first
from constants import HARTREE2CM  # noqa: E402
from qc_common import write_atomic  # noqa: E402
from vibrations import LABEL_TAGS, displacement, mass_weights  # noqa: E402

SIGMA_RANGE = (1e-8, 2e-8)    # hartree/bohr: the gradient noise the registration calibrated on B_0f06474656 (its section 2)
TWO_STEP_NOISE = math.hypot(1.0, 1.0 / R.STEP_RATIO)   # noise of (large − small) over the small step's: the large step's is 1/ratio of it


@dataclass(frozen=True)
class AnalysisConfig:
    """The two steps of one measurement and the results folder, checked before any file is opened."""

    small: R.Source
    large: R.Source
    molecules: Path
    out: Path

    def __post_init__(self) -> None:
        inputs = [self.molecules, self.small.patches, self.small.labels, self.large.patches, self.large.labels]
        missing = [str(p) for p in inputs if not p.is_dir()]
        if missing:
            raise FileNotFoundError(f"not there: {missing}")
        out = self.out.resolve()
        inside = [str(p) for p in inputs if out == p.resolve() or p.resolve() in out.parents]
        if inside:
            raise ValueError(f"the results folder {self.out} lies in an input folder {inside}: an analysis writes into a folder of its own")


@dataclass(frozen=True)
class StepPoint:
    """One re-measured label mode in one functional, at both steps."""

    mol_id: str
    tag: str
    mode: int
    label_cm: float
    small_cm: float
    large_cm: float
    noise_cm: float     # frequency noise at the small step per R.GRADIENT_NOISE_UNIT of gradient noise
    flagged: bool       # the mode has no single counterpart at one of the steps: its frequencies there are not this mode's

    @property
    def diff_cm(self) -> float:
        return self.large_cm - self.small_cm

    @property
    def curvature_diff_cm2(self) -> float:
        """The two steps' difference as a signed curvature, ω|ω| at the large step minus the same at the small one."""
        return self.large_cm * abs(self.large_cm) - self.small_cm * abs(self.small_cm)

    def noise_of_diff_cm(self, sigma: float) -> float:
        """One standard deviation of the two steps' frequency difference at gradient noise sigma, were it noise alone."""
        return self.noise_cm * sigma / R.GRADIENT_NOISE_UNIT * TWO_STEP_NOISE


def step_points(cfg: AnalysisConfig) -> list[StepPoint]:
    """Every re-measured mode of the molecules patched at both steps; a large-step molecule the small step lacks is refused."""
    small_ids = set(R.patched_ids(cfg.small.patches))
    points = []
    for mol_id in R.patched_ids(cfg.large.patches):
        if mol_id not in small_ids:
            raise ValueError(f"{mol_id} was patched at the large step only")
        large = {(p.tag, p.mode): p for p in R.molecule_points(mol_id, cfg.large, cfg.molecules)}
        for p in R.molecule_points(mol_id, cfg.small, cfg.molecules):
            other = large.get((p.tag, p.mode))
            if other is None:
                raise ValueError(f"{mol_id} {p.tag} mode {p.mode}: the large step did not re-measure this mode")
            if abs(other.step_bohr / p.step_bohr - R.STEP_RATIO) > R.STEP_RATIO_TOL:
                raise ValueError(f"{mol_id}: the steps are {p.step_bohr:g} and {other.step_bohr:g} bohr, not a ratio of {R.STEP_RATIO:g}")
            points.append(StepPoint(mol_id, p.tag, p.mode, p.label_cm, p.patched_cm, other.patched_cm, p.noise_cm,
                                    bool(p.flags or other.flags)))
    return sorted(points, key=lambda p: (p.tag, p.label_cm))


def direction_rows(cfg: AnalysisConfig) -> list[dict[str, Any]]:
    """Per molecule, functional and direction: the measured curvature uᵀC (cm⁻²) at both steps, and the noise (cm⁻²) their difference
    would carry per R.GRADIENT_NOISE_UNIT. Where the two steps' directions differ, the curvatures are along other directions and no
    difference is given."""
    rows = []
    for mol_id in R.patched_ids(cfg.large.patches):
        mol = R.Molecule.read(mol_id, cfg.small.labels, cfg.molecules)
        for tag in LABEL_TAGS:
            small, large = R.patch_of(mol, tag, cfg.small, R.read_step), R.patch_of(mol, tag, cfg.large, R.read_step)
            same = R.directions_apart(small["U"], large["U"]) <= R.DIRECTIONS_TOL
            for j in range(small["U"].shape[1]):
                u = small["U"][:, j]
                _, q = displacement(u, mol.masses, small["step_bohr"])
                noise = R.GRADIENT_NOISE_UNIT * math.sqrt(2) * float(np.linalg.norm(u / mass_weights(mol.masses))) / (2 * q)
                at_small = float(u @ small["C"][:, j]) * HARTREE2CM ** 2
                at_large = float(large["U"][:, j] @ large["C"][:, j]) * HARTREE2CM ** 2
                rows.append({"id": mol_id, "tag": tag, "direction": j, "same_directions": same, "small_cm2": at_small,
                             "large_cm2": at_large, "diff_cm2": at_large - at_small if same else None,
                             "noise_of_diff_cm2": noise * HARTREE2CM ** 2 * TWO_STEP_NOISE})
    return rows


def functional_gaps(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Per direction measured along the same vector at both steps: the two-step curvature difference in each functional, and how far
    the functionals stand apart in it."""
    gaps = []
    for mol_id, j in sorted({(r["id"], r["direction"]) for r in rows if r["same_directions"]}):
        by_tag = {r["tag"]: r for r in rows if (r["id"], r["direction"]) == (mol_id, j)}
        diffs = [by_tag[tag]["diff_cm2"] for tag in LABEL_TAGS]
        gaps.append({"id": mol_id, "direction": j, "diffs_cm2": diffs, "gap_cm2": max(diffs) - min(diffs),
                     "noise_of_diff_cm2": by_tag[LABEL_TAGS[0]]["noise_of_diff_cm2"]})
    return gaps


def summary(points: list[StepPoint], gaps: list[dict[str, Any]]) -> dict[str, Any]:
    """The numbers the verdict rests on, over the unflagged points."""
    clean = [p for p in points if not p.flagged]
    if not clean:
        raise ValueError("no unflagged point at both steps: nothing to analyse")
    diffs = np.array([p.diff_cm for p in clean])
    curv = np.array([p.curvature_diff_cm2 for p in clean])
    ratios = {f"{s:g}": [abs(p.diff_cm) / p.noise_of_diff_cm(s) for p in clean] for s in SIGMA_RANGE}
    return {"n": len(clean), "positive": int((diffs > 0).sum()), "negative": int((diffs < 0).sum()),
            "chance_one_sign": 2.0 ** (1 - len(clean)),
            "diff_cm": {"min": float(diffs.min()), "max": float(diffs.max()), "max_abs": float(np.abs(diffs).max())},
            "curvature_diff_cm2": {"min": float(curv.min()), "max": float(curv.max()), "mean": float(curv.mean()),
                                   "sd": float(curv.std(ddof=1)) if len(curv) > 1 else None},
            "diff_over_noise": {s: {"min": min(r), "median": float(np.median(r)), "max": max(r), "below_3": sum(x < 3 for x in r)}
                                for s, r in ratios.items()},
            "functional_gaps": gaps}


def points_csv(points: list[StepPoint]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["id", "tag", "mode", "label_cm", "small_step_cm", "large_step_cm", "large_minus_small_cm", "curvature_diff_cm2",
                     "noise_cm_per_1e-7_hartree_bohr", *(f"diff_over_noise_at_{s:g}" for s in SIGMA_RANGE), "flagged_overlap"])
    for p in points:
        writer.writerow([p.mol_id, p.tag, p.mode, f"{p.label_cm:.4f}", f"{p.small_cm:.4f}", f"{p.large_cm:.4f}", f"{p.diff_cm:+.4f}",
                         f"{p.curvature_diff_cm2:+.3f}", f"{p.noise_cm:.4f}",
                         *(f"{abs(p.diff_cm) / p.noise_of_diff_cm(s):.2f}" for s in SIGMA_RANGE), int(p.flagged)])
    return buffer.getvalue()


def verdict(s: dict[str, Any]) -> str:
    """What the numbers say, without a threshold of its own: the reader of the registration decides what follows."""
    low, high = (s["diff_over_noise"][f"{sigma:g}"] for sigma in SIGMA_RANGE)
    gaps = s["functional_gaps"]
    text = (f"Of {s['n']} unflagged points, {s['positive']} have the large step above the small one and {s['negative']} below; noise "
            f"without a preferred sign gives one sign on all of them with probability {s['chance_one_sign']:.1e}. The differences run "
            f"from {s['diff_cm']['min']:+.3f} to {s['diff_cm']['max']:+.3f} cm⁻¹; as curvatures from {s['curvature_diff_cm2']['min']:+.1f} "
            f"to {s['curvature_diff_cm2']['max']:+.1f} cm⁻² (mean {s['curvature_diff_cm2']['mean']:+.1f}, standard deviation "
            f"{R.number(s['curvature_diff_cm2']['sd'], '.1f')}). Against the noise the difference would carry, a point's difference is "
            f"{high['min']:.1f} to {high['max']:.1f} standard deviations at σ = {SIGMA_RANGE[1]:g} hartree/bohr (median {high['median']:.1f}; "
            f"{high['below_3']} point(s) below 3) and {low['min']:.1f} to {low['max']:.1f} at σ = {SIGMA_RANGE[0]:g} (median "
            f"{low['median']:.1f}; {low['below_3']} below 3).")
    if gaps:
        text += (f" Along the {len(gaps)} direction(s) measured along the same vector at both steps, the two functionals' curvature "
                 f"differences stand {min(g['gap_cm2'] for g in gaps):.1f} to {max(g['gap_cm2'] for g in gaps):.1f} cm⁻² apart, where "
                 f"the differences themselves are {min(min(g['diffs_cm2']) for g in gaps):+.1f} to "
                 f"{max(max(g['diffs_cm2']) for g in gaps):+.1f} cm⁻²: two separate SCFs give the same step difference.")
    return text + (" Two steps cannot show that the error grows as the square of the step; that is the central difference's own error "
                   "law, and a third step would test it.")


def analysis_md(cfg: AnalysisConfig, record: dict[str, Any], points: list[StepPoint], rows: list[dict[str, Any]]) -> str:
    lines = ["# The two steps of the low-mode repair: noise or step bias? (TASKS 218)", "",
             f"Small step: `{R.shown(cfg.small.patches)}`; large step: `{R.shown(cfg.large.patches)}`. {len(points)} points (re-measured "
             f"label mode × functional) on {len({p.mol_id for p in points})} molecules; {sum(p.flagged for p in points)} flagged for a "
             f"coverage or overlap below {R.OVERLAP_MIN} at one of the steps, listed and left out of the summary. 'Noise' is the frequency "
             f"noise the small step makes of {R.GRADIENT_NOISE_UNIT:g} hartree/bohr of gradient noise (`low_mode_threshold_read."
             f"noise_sensitivity_cm`); the two steps' difference carries {TWO_STEP_NOISE:.3f} times that, and the last two columns set the "
             "difference against it at the registration's two values of σ.", "",
             "## The points", "",
             "| point | label (cm⁻¹) | small step | large step | large − small | as curvature (cm⁻²) | noise per 1e-07 | "
             + " | ".join(f"diff / noise at σ = {s:g}" for s in SIGMA_RANGE) + " | flag |", "|---|---|---|---|---|---|---|---|---|---|"]
    lines += [f"| {p.mol_id} {p.tag} mode {p.mode} | {p.label_cm:.2f} | {p.small_cm:.3f} | {p.large_cm:.3f} | {p.diff_cm:+.3f} | "
              f"{p.curvature_diff_cm2:+.2f} | {p.noise_cm:.2f} | "
              + " | ".join(f"{abs(p.diff_cm) / p.noise_of_diff_cm(s):.1f}" for s in SIGMA_RANGE) + f" | {'overlap' if p.flagged else ''} |"
              for p in points]
    lines += ["", "## The measured curvature along each direction, uᵀC (cm⁻²)", "",
              f"| molecule | functional | direction | small step | large step | large − small | noise of the difference per "
              f"{R.GRADIENT_NOISE_UNIT:g} |", "|---|---|---|---|---|---|---|"]
    lines += [f"| {r['id']} | {r['tag']} | {r['direction']} | {r['small_cm2']:.2f} | {r['large_cm2']:.2f} | "
              f"{format(r['diff_cm2'], '+.2f') if r['same_directions'] else 'the steps used other directions'} | "
              f"{r['noise_of_diff_cm2']:.1f} |" for r in rows]
    return "\n".join([*lines, "", "## What the numbers say", "", record["verdict"], ""])


def run(cfg: AnalysisConfig) -> dict[str, Any]:
    """Read both steps, write the three files, return the record."""
    points, rows = step_points(cfg), direction_rows(cfg)
    record = summary(points, functional_gaps(rows))
    record["verdict"] = verdict(record)
    record |= {"directions": rows, "sigma_range": SIGMA_RANGE, "two_step_noise": TWO_STEP_NOISE,
               "flagged": [f"{p.mol_id} {p.tag} mode {p.mode}" for p in points if p.flagged],
               "inputs": {"small": [R.shown(cfg.small.patches), R.shown(cfg.small.labels)],
                          "large": [R.shown(cfg.large.patches), R.shown(cfg.large.labels)]}}
    cfg.out.mkdir(parents=True, exist_ok=True)
    write_atomic(cfg.out / "step_points.csv", points_csv(points))
    write_atomic(cfg.out / "record.json", json.dumps(record, indent=1, ensure_ascii=False) + "\n")
    write_atomic(cfg.out / "STEP_ANALYSIS.md", analysis_md(cfg, record, points, rows))
    return record


def parse_args(argv: list[str] | None = None) -> AnalysisConfig:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--small", required=True, help="<patch folder>=<label folder> of the small step")
    ap.add_argument("--large", required=True, help="the same molecules, or some of them, at twice the step")
    ap.add_argument("--molecules", type=Path, required=True, help="the corpus molecules folder (geometry.json per id)")
    ap.add_argument("--out", type=Path, required=True, help="a results folder of this analysis's own")
    a = ap.parse_args(argv)
    return AnalysisConfig(R.Source.parse(a.small), R.Source.parse(a.large), a.molecules, a.out)


def main(argv: list[str] | None = None) -> None:
    cfg = parse_args(argv)
    run(cfg)
    print((cfg.out / "STEP_ANALYSIS.md").read_text(encoding="utf-8"), flush=True)


if __name__ == "__main__":
    main()
