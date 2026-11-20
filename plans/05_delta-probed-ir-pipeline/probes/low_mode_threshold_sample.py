"""Draw the unbiased sample for the low-mode threshold measurement (TASKS 218; registered in
GoalGathering/notes/PreRegistration_2026-11-20_Low_Mode_Repair_Threshold.md).

The population is the corpus molecules the repair never touched (no `low_mode_patch` entry in either analytic label), small enough to
patch on the laptop, whose lowest B3LYP mode lies in one of the bands of the decision window and whose lowest ωB97X mode is not below
the present threshold (such a molecule would be a repair candidate already, or carries an imaginary mode and never trains). Per band
the sorted ids are shuffled once with a seeded generator and the first few taken, so a larger draw with the same seed contains the
smaller one: that is the registered extension.

For each sampled molecule the script counts the merged directions the runner would patch at each candidate `--below` (the runner's
own `label_directions`), hence the gradients, and estimates the time from the seconds per gradient that earlier repairs recorded in
their `dir_*.json` files, by atom count and functional.

    python probes/low_mode_threshold_sample.py --molecules <corpus molecules dir> --out <new folder> --timing <patch folder> [...]
        [--per-band 5] [--max-atoms 25] [--seed 218]

The step check's list is a rule, not a choice: the smallest sampled molecule of each band, and every sampled molecule with a
registered point (a B3LYP mode in the decision window) whose frequency noise per unit of gradient noise passes the read script's line.

Writes ids_sample.txt, ids_step02.txt (the step check's list), sample.json and SAMPLE.md, each through a temp file. Reads H_raw of every
unrepaired molecule and takes its modes with the runner's own arithmetic, so the bands are
the frequencies the runner selects by; computes no chemistry. numpy only.
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "corpus"))
from low_mode_patch import label_directions, read_label  # noqa: E402  the path lines above come first
from low_mode_threshold_read import (  # noqa: E402
    BAND_EDGES_CM,
    DECISION_TAG,
    DECISION_WINDOW_CM,
    GRADIENT_NOISE_UNIT,
    STEP_CHECK_NOISE_CM,
    noise_sensitivity_cm,
)
from qc_common import write_atomic  # noqa: E402
from vibrations import LABEL_TAGS, LOW_MODE_CM, STEP_BOHR, vibrational_modes  # noqa: E402

SAMPLE_BANDS_CM = tuple(b for b in itertools.pairwise(BAND_EDGES_CM) if DECISION_WINDOW_CM[0] <= b[0] and b[1] <= DECISION_WINDOW_CM[1])
BELOW_OPTIONS_CM = (60.0, 100.0)       # the two `--below` values the run is priced at; the author chooses
LISTED_BELOW_CM = BAND_EDGES_CM[-1]    # modes up to here are listed per sampled molecule
TIMING_ATOM_EDGES = (12, 16, 20, 25)   # upper atom counts of the timing bins
REFERENCE_SHARE = 0.40                 # reference SCFs and start-up, as a share of one direction's four gradients: B_0f06474656's check
                                       # ran 809.68 s (low_mode_patch_check.log) against 577.1 s in its four dir_*.json files
THREAD_FACTOR_RANGE = (1.0, 2.0)       # 4 threads against the 8 the timings were taken at: not measured, assumed between these
GRADIENTS_PER_DIRECTION = 4            # ± one step in each of the two functionals
REFERENCE_SCFS = 2                     # one per functional and molecule


@dataclass(frozen=True)
class SampleConfig:
    """The draw's settings, checked before any label is read."""

    molecules: Path
    out: Path
    timing: tuple[Path, ...]
    per_band: int
    max_atoms: int
    seed: int

    def __post_init__(self) -> None:
        missing = [str(p) for p in (self.molecules, *self.timing) if not p.is_dir()]
        if missing:
            raise FileNotFoundError(f"not a folder: {missing}")
        if not self.timing:
            raise ValueError("no timing folder given: the time estimate needs recorded gradient times")
        if self.per_band < 1:
            raise ValueError(f"per band {self.per_band}: at least 1")
        if not 3 <= self.max_atoms <= TIMING_ATOM_EDGES[-1]:
            raise ValueError(f"atom limit {self.max_atoms}: between 3 and {TIMING_ATOM_EDGES[-1]}, the largest size with a timing bin")
        if self.out.resolve() == self.molecules.resolve() or self.molecules.resolve() in self.out.resolve().parents:
            raise ValueError(f"the output folder {self.out} lies in the corpus: the draw writes into a folder of its own")


@dataclass(frozen=True)
class Candidate:
    """An unrepaired corpus molecule: its size and both labels' vibrational frequencies (cm⁻¹, ascending)."""

    mol_id: str
    atoms: int
    omega: dict[str, np.ndarray]

    @property
    def lowest(self) -> float:
        return float(self.omega[DECISION_TAG][0])

    @property
    def eligible(self) -> bool:
        """No mode of the other label below the present threshold, imaginary ones included."""
        return all(float(w[0]) >= LOW_MODE_CM for w in self.omega.values())


def is_repaired(folder: Path) -> bool:
    """Whether either analytic label of a corpus folder carries a low-mode repair."""
    for tag in LABEL_TAGS:
        with np.load(folder / f"hessian_{tag}_analytic.npz") as z:
            if "low_mode_patch" in z.files:
                return True
    return False


def candidates(molecules: Path) -> list[Candidate]:
    """Every folder with both analytic labels and no repair, of any size, sorted by id."""
    found = []
    for folder in sorted(p for p in molecules.iterdir() if p.is_dir()):
        if not all((folder / f"hessian_{t}_analytic.npz").is_file() for t in LABEL_TAGS) or is_repaired(folder):
            continue
        geometry, hessians = read_label(folder)
        masses, coords = np.asarray(geometry["masses_amu"], float), np.asarray(geometry["coords_bohr"], float)
        found.append(Candidate(folder.name, len(masses), {t: vibrational_modes(H, masses, coords).omega_cm for t, H in hessians.items()}))
    return found


def draw(population: list[Candidate], cfg: SampleConfig) -> dict[tuple[float, float], list[Candidate]]:
    """Per band the first `per_band` of the eligible ids within the atom limit, shuffled once; a band with too few molecules refuses
    the draw."""
    rng = np.random.default_rng(cfg.seed)
    chosen = {}
    for lo, hi in SAMPLE_BANDS_CM:
        pool = sorted((c for c in population if c.eligible and c.atoms <= cfg.max_atoms and lo <= c.lowest < hi), key=lambda c: c.mol_id)
        if len(pool) < cfg.per_band:
            raise ValueError(f"band {lo:g}–{hi:g} cm⁻¹ holds {len(pool)} eligible molecules, fewer than the {cfg.per_band} asked for")
        order = rng.permutation(len(pool))
        chosen[(lo, hi)] = sorted((pool[i] for i in order[:cfg.per_band]), key=lambda c: c.mol_id)
    return chosen


def timing_bin(atoms: int) -> int:
    """The index of the timing bin an atom count falls in."""
    for k, edge in enumerate(TIMING_ATOM_EDGES):
        if atoms <= edge:
            return k
    raise ValueError(f"{atoms} atoms: past the largest timing bin ({TIMING_ATOM_EDGES[-1]})")


def gradient_seconds(timing: tuple[Path, ...], molecules: Path) -> dict[tuple[int, str], dict[str, float]]:
    """The median seconds per gradient point and the number of points, by timing bin and functional, from earlier repairs' point files."""
    seconds: dict[tuple[int, str], list[float]] = {}
    for folder in (f for root in timing for f in sorted(root.iterdir()) if f.is_dir()):
        atoms = len(json.loads((molecules / folder.name / "geometry.json").read_text(encoding="utf-8"))["masses_amu"])
        if atoms > TIMING_ATOM_EDGES[-1]:
            continue
        for tag in LABEL_TAGS:
            for point in sorted((folder / tag).glob("dir_*.json")):
                seconds.setdefault((timing_bin(atoms), tag), []).append(float(json.loads(point.read_text(encoding="utf-8"))["seconds"]))
    return {key: {"median_s": float(np.median(v)), "points": len(v)} for key, v in seconds.items()}


def registered_points(molecule_dir: Path) -> list[dict[str, float]]:
    """The molecule's modes of the decision functional inside the decision window, each with the frequency noise the patch makes of
    GRADIENT_NOISE_UNIT of gradient noise at the repair's step (the read script's formula, on the label mode)."""
    geometry, hessians = read_label(molecule_dir)
    masses = np.asarray(geometry["masses_amu"], float)
    modes = vibrational_modes(hessians[DECISION_TAG], masses, np.asarray(geometry["coords_bohr"], float))
    return [{"mode": i, "label_cm": float(w), "noise_cm": noise_sensitivity_cm(modes.vectors[:, i], float(w), masses, STEP_BOHR)}
            for i, w in enumerate(modes.omega_cm) if DECISION_WINDOW_CM[0] <= w < DECISION_WINDOW_CM[1]]


def molecule_row(c: Candidate, band: tuple[float, float], cfg: SampleConfig, per_gradient: dict[tuple[int, str], dict[str, float]]) -> dict[str, Any]:
    """One sampled molecule: its soft modes, its registered points, and per `--below` option the directions, gradients and seconds at the
    timings' threads."""
    row: dict[str, Any] = {"id": c.mol_id, "band": f"{band[0]:g}–{band[1]:g}", "atoms": c.atoms,
                           "modes_cm": {t: [round(float(w), 2) for w in c.omega[t] if w < LISTED_BELOW_CM] for t in LABEL_TAGS},
                           "registered_points": registered_points(cfg.molecules / c.mol_id), "below": {}}
    missing = [t for t in LABEL_TAGS if (timing_bin(c.atoms), t) not in per_gradient]
    if missing:
        raise ValueError(f"no recorded gradient time for {c.atoms} atoms in {missing}: give a timing folder that covers this size")
    pair_s = sum(2 * per_gradient[(timing_bin(c.atoms), t)]["median_s"] for t in LABEL_TAGS)   # ± one step in both functionals
    for below in BELOW_OPTIONS_CM:
        k = int(label_directions(cfg.molecules / c.mol_id, below).shape[1])
        row["below"][f"{below:g}"] = {"directions": k, "gradients": GRADIENTS_PER_DIRECTION * k, "seconds": (k + REFERENCE_SHARE) * pair_s}
    return row


def totals(rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    """Per `--below` option the sample's directions, gradients, reference SCFs and hours (at the timings' threads, and the assumed range)."""
    out = {}
    for below in (f"{b:g}" for b in BELOW_OPTIONS_CM):
        hours = sum(r["below"][below]["seconds"] for r in rows) / 3600
        out[below] = {"directions": sum(r["below"][below]["directions"] for r in rows),
                      "gradients": sum(r["below"][below]["gradients"] for r in rows), "reference_scfs": REFERENCE_SCFS * len(rows),
                      "hours_8_threads": hours, "hours_low": hours * THREAD_FACTOR_RANGE[0], "hours_high": hours * THREAD_FACTOR_RANGE[1]}
    return out


def step_check_ids(rows: list[dict[str, Any]]) -> dict[str, str]:
    """The step check's molecules with the reason each is on the list, in the sample's order: the smallest of each band (ties by id),
    and every molecule with a registered point noisier than STEP_CHECK_NOISE_CM per GRADIENT_NOISE_UNIT."""
    smallest = {min((r for r in rows if r["band"] == band), key=lambda r: (r["atoms"], r["id"]))["id"] for band in {r["band"] for r in rows}}
    reasons = {}
    for r in rows:
        noisy = max((p["noise_cm"] for p in r["registered_points"]), default=0.0) > STEP_CHECK_NOISE_CM
        if r["id"] in smallest or noisy:
            reasons[r["id"]] = " and ".join(text for text, holds in (("smallest of its band", r["id"] in smallest),
                                                                     ("a registered point above the noise line", noisy)) if holds)
    return reasons


def population_rows(population: list[Candidate], max_atoms: int) -> list[dict[str, Any]]:
    """Per band: the unrepaired molecules of any size, those within the atom limit, and the eligible ones the draw is made from."""
    rows = []
    for lo, hi in SAMPLE_BANDS_CM:
        inside = [c for c in population if lo <= c.lowest < hi]
        small = [c for c in inside if c.atoms <= max_atoms]
        rows.append({"band": f"{lo:g}–{hi:g}", "unrepaired": len(inside), "within_atom_limit": len(small), "eligible": sum(c.eligible for c in small)})
    return rows


def sample_md(record: dict[str, Any]) -> str:
    """SAMPLE.md: the population, the draw and its price at each `--below`."""
    s = record["settings"]
    belows = [f"{b:g}" for b in BELOW_OPTIONS_CM]
    lines = ["# The sample for the low-mode threshold measurement (TASKS 218)", "",
             f"Seed {s['seed']}, {s['per_band']} per band, at most {s['max_atoms']} atoms; bands by the lowest {DECISION_TAG} label mode.", "",
             f"| lowest {DECISION_TAG} mode (cm⁻¹) | unrepaired molecules | with ≤ {s['max_atoms']} atoms | eligible | drawn |", "|---|---|---|---|---|"]
    lines += [f"| {p['band']} | {p['unrepaired']} | {p['within_atom_limit']} | {p['eligible']} | {s['per_band']} |" for p in record["population"]]
    lines += ["", f"Eligible: no mode of either label below {LOW_MODE_CM:g} cm⁻¹ (imaginary ones included).", "",
              "| id | band | atoms | " + " | ".join(f"{t} modes below {LISTED_BELOW_CM:g}" for t in LABEL_TAGS)
              + f" | noise per {GRADIENT_NOISE_UNIT:g} (cm⁻¹) | "
              + " | ".join(f"directions / gradients / min at --below {b}" for b in belows) + " |", "|---|---|---|---|---|---|---|---|"]
    for r in record["molecules"]:
        modes = " | ".join(", ".join(f"{w:.1f}" for w in r["modes_cm"][t]) for t in LABEL_TAGS)
        noise = ", ".join(f"{p['noise_cm']:.2f}" for p in r["registered_points"])
        cost = " | ".join(f"{r['below'][b]['directions']} / {r['below'][b]['gradients']} / {r['below'][b]['seconds'] / 60:.0f}" for b in belows)
        lines.append(f"| {r['id']} | {r['band']} | {r['atoms']} | {modes} | {noise} | {cost} |")
    lines += ["", f"Noise: the frequency noise the patch makes of {GRADIENT_NOISE_UNIT:g} hartree/bohr of gradient noise on each registered point "
              f"(a {DECISION_TAG} mode in {DECISION_WINDOW_CM[0]:g}–{DECISION_WINDOW_CM[1]:g} cm⁻¹), in the order of the modes; "
              "`low_mode_threshold_read.noise_sensitivity_cm`.", ""]
    for name, key in (("The sample", "totals"), ("The step check", "step_check_totals")):
        for b in belows:
            t = record[key][b]
            lines.append(f"{name} at `--below {b}`: {t['directions']} directions, {t['gradients']} gradients and {t['reference_scfs']} reference "
                         f"SCFs; {t['hours_8_threads']:.1f} h at the timings' 8 threads, so {t['hours_low']:.1f}–{t['hours_high']:.1f} h at 4 "
                         f"threads (factor {THREAD_FACTOR_RANGE[0]:g}–{THREAD_FACTOR_RANGE[1]:g}, assumed, not measured; no other job beside it).")
    lines += ["", "Seconds per gradient (median, 8 threads) from the timing folders, by atom count: "
              + "; ".join(f"≤ {TIMING_ATOM_EDGES[int(k.split()[0])]} atoms {k.split()[1]} {v['median_s']:.0f} s ({v['points']} points)"
                          for k, v in sorted(record["gradient_seconds"].items())) + ".",
              f"A molecule costs (directions + {REFERENCE_SHARE}) × 2 × (the two functionals' seconds); the {REFERENCE_SHARE} is the reference "
              "SCFs and start-up measured on B_0f06474656.", "",
              f"Step check (the smallest molecule of each band, and every molecule with a registered point above {STEP_CHECK_NOISE_CM} cm⁻¹ "
              f"per {GRADIENT_NOISE_UNIT:g}): " + "; ".join(f"{i} ({why})" for i, why in record["step_check"].items()) + "."]
    return "\n".join(lines) + "\n"


def run(cfg: SampleConfig) -> dict[str, Any]:
    """Draw, price and write the sample; returns the record."""
    population = candidates(cfg.molecules)
    chosen = draw(population, cfg)
    per_gradient = gradient_seconds(cfg.timing, cfg.molecules)
    rows = [molecule_row(c, band, cfg, per_gradient) for band, picked in chosen.items() for c in picked]
    step_check = step_check_ids(rows)
    record = {"settings": {"seed": cfg.seed, "per_band": cfg.per_band, "max_atoms": cfg.max_atoms},
              "population": population_rows(population, cfg.max_atoms), "molecules": rows, "totals": totals(rows),
              "step_check_totals": totals([r for r in rows if r["id"] in step_check]), "step_check": step_check,
              "gradient_seconds": {f"{k} {t}": v for (k, t), v in sorted(per_gradient.items())}, "step_check_ids": list(step_check)}
    cfg.out.mkdir(parents=True, exist_ok=True)
    head = f"# low_mode_threshold_sample.py: seed {cfg.seed}, {cfg.per_band} per band, at most {cfg.max_atoms} atoms (id, band, atoms)"
    write_atomic(cfg.out / "ids_sample.txt", "\n".join([head, *(f"{r['id']} {r['band']} {r['atoms']}" for r in rows)]) + "\n")
    write_atomic(cfg.out / "ids_step02.txt", "\n".join(["# the step check: id, why", *(f"{i} # {why}" for i, why in step_check.items())]) + "\n")
    write_atomic(cfg.out / "sample.json", json.dumps(record, indent=1, ensure_ascii=False) + "\n")
    write_atomic(cfg.out / "SAMPLE.md", sample_md(record))
    return record


def parse_args(argv: list[str] | None = None) -> SampleConfig:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--molecules", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--timing", type=Path, action="append", default=[], help="a patch folder with <id>/<tag>/dir_*.json; repeatable")
    ap.add_argument("--per-band", type=int, default=5)
    ap.add_argument("--max-atoms", type=int, default=25)
    ap.add_argument("--seed", type=int, default=218)
    a = ap.parse_args(argv)
    return SampleConfig(a.molecules, a.out, tuple(a.timing), a.per_band, a.max_atoms, a.seed)


def main(argv: list[str] | None = None) -> None:
    cfg = parse_args(argv)
    run(cfg)
    print((cfg.out / "SAMPLE.md").read_text(encoding="utf-8"), flush=True)


if __name__ == "__main__":
    main()
