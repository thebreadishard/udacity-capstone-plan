"""How far the low-mode repair moves a label mode, read against the mode's frequency and force constant (TASKS 218; registered in
GoalGathering/notes/PreRegistration_2026-11-20_Low_Mode_Repair_Threshold.md).

The repair (`probes/low_mode_patch_run.py`) re-measures a label Hessian along mass-weighted directions and writes the patched Hessian
with its `directions`. It writes no before and after per mode, so this script derives them. With k directions the patch re-measured
a k-dimensional space, and in each functional the k label modes that lie deepest in that space are the modes it re-measured: one point
each, with the mode's share inside the space (its coverage), its frequency in the label, the frequency of the patched mode it overlaps
most, the signed change, the Cartesian force constant along the mode in the label, and how much frequency noise the finite difference
makes of a given gradient noise on that mode. The merged directions of two functionals are rotations of their modes, not the modes
themselves, which is why a point is a mode and not a direction (B_0e479d2c02, two directions).

A point whose mode is not inside the space or has no single counterpart after the patch (coverage or overlap below OVERLAP_MIN) is
kept in the table, flagged, and left out of every statistic; so is a point whose two step sizes disagree when a step check is given.
The registered rule is read on the unflagged B3LYP points of the unbiased sample, and only when the step check allows it: two checked
points that fail it make the outcome undecided, and a point that moved by an amount near the line and has no step check holds the
outcome back until it has one.

A source is a pair `<patch folder>=<label folder>`: `<patch folder>/<id>/hessian_<tag>_analytic_grfpatch.npz` and the label it was
patched from, `<label folder>/<id>/hessian_<tag>_analytic.npz`. For the repair of 13 November the labels are the superseded originals;
for a measurement run they are the corpus's current files. A label file that carries a repair is refused: it is not an original.

    python probes/low_mode_threshold_read.py --source <patches>=<labels> [--source ...] [--step-check <patches>=<labels>]
        --molecules <corpus molecules dir> --out <new results folder> [--sample <sample.json>]
        [--exploratory "<why this read decides nothing>"]

Writes points.csv, record.json and RESULT.md into the results folder, each through a temp file. numpy and scipy only.
"""
from __future__ import annotations

import argparse
import csv
import io
import itertools
import json
import math
import sys
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import spearmanr

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "corpus"))
from constants import HARTREE2CM  # noqa: E402  the path lines above come first
from qc_common import write_atomic  # noqa: E402
from vibrations import LABEL_TAGS, LOW_MODE_CM, Modes, displacement, mass_weights, vibrational_modes  # noqa: E402

BAND_EDGES_CM = (20.0, 30.0, 40.0, 50.0, 60.0, 80.0, 100.0)   # the read's frequency bands, by label frequency
MOVE_LINE_CM = 0.5            # a label counts as wrong when the repair moves it further: the bound the repair's own check uses
OVERLAP_MIN = 0.9             # below this the mode lies partly outside the patched space, or has no single counterpart after the patch
STEP_AGREEMENT_CM = 0.15      # steps 0.01 and 0.02 bohr agreed within this at the label grid (vibrations.STEP_BOHR's measurement)
STEP_FAILURES_STOP = 2        # this many registered points failing the step check make the outcome undecided
NEAR_LINE_CM = (0.25, 1.0)    # a registered point that moved by an amount inside this needs a step check before the rule is read
GRADIENT_NOISE_UNIT = 1e-7    # hartree/bohr: the gradient noise the per-point frequency noise is quoted for
STEP_CHECK_NOISE_CM = 0.5     # a registered point noisier than this per GRADIENT_NOISE_UNIT is step-checked from the start
LABEL_MATCH_CM = 0.05         # how far the given label's frequencies may stand from the ones the patch recorded for its label
DECISION_TAG = "b3lyp"
DECISION_WINDOW_CM = (20.0, 60.0)
SOUND_P_MAX, SOUND_UPPER_MAX = 0.20, 0.30        # outcome 1: p and p + 1 SE
MAJORITY_P_MIN, MAJORITY_LOWER_MIN = 0.50, 0.40  # outcome 2: p and p − 1 SE
RULE_MIN_POINTS = 16          # a binomial SE is zero at p = 0 or 1 whatever n, so the rule reads nothing from fewer points
COMPARE_EPS = 1e-12           # 5/25 against 0.20 is a comparison of the registered numbers, not of rounding
BIASED, UNBIASED = "biased", "unbiased"
OUTCOME_SOUND, OUTCOME_MAJORITY, OUTCOME_UNDECIDED, OUTCOME_NOT_STATED = "sound", "majority wrong", "undecided", "not stated"


@dataclass(frozen=True)
class Source:
    """Patched Hessians and the labels they were patched from."""

    patches: Path
    labels: Path

    @classmethod
    def parse(cls, text: str) -> Source:
        patches, sep, labels = text.partition("=")
        if not (sep and patches and labels):
            raise ValueError(f"a source is '<patch folder>=<label folder>', not {text!r}")
        return cls(Path(patches), Path(labels))


@dataclass(frozen=True)
class ReadConfig:
    """The read's inputs and its results folder, checked before any file is opened."""

    sources: tuple[Source, ...]
    step_checks: tuple[Source, ...]
    molecules: Path
    out: Path
    exploratory: str | None
    sample: Path | None = None

    def __post_init__(self) -> None:
        if not self.sources:
            raise ValueError("no source given")
        inputs = [self.molecules, *(p for s in (*self.sources, *self.step_checks) for p in (s.patches, s.labels))]
        missing = [str(p) for p in inputs if not p.is_dir()]
        if self.sample is not None and not self.sample.is_file():
            missing.append(str(self.sample))
        if missing:
            raise FileNotFoundError(f"not there: {missing}")
        out = self.out.resolve()
        inside = [str(p) for p in inputs if out == p.resolve() or p.resolve() in out.parents]
        if inside:
            raise ValueError(f"the results folder {self.out} lies in an input folder {inside}: a read writes into a folder of its own")
        if self.exploratory is not None and not self.exploratory.strip():
            raise ValueError("an exploratory read says why it decides nothing")


@dataclass(frozen=True)
class Strata:
    """The sample's design, from the sample script's record: each molecule's band, the eligible molecules per band, the atom limit."""

    band_of: dict[str, str]
    eligible: dict[str, int]
    max_atoms: int

    @classmethod
    def read(cls, path: Path) -> Strata:
        record = json.loads(path.read_text(encoding="utf-8"))
        return cls({m["id"]: m["band"] for m in record["molecules"]}, {p["band"]: int(p["eligible"]) for p in record["population"]},
                   int(record["settings"]["max_atoms"]))

    @property
    def population(self) -> str:
        return (f"molecules whose lowest {DECISION_TAG} mode lies in {DECISION_WINDOW_CM[0]:g}–{DECISION_WINDOW_CM[1]:g} cm⁻¹, with at most "
                f"{self.max_atoms} atoms, each band weighted equally")


@dataclass(frozen=True)
class Point:
    """One re-measured label mode in one functional."""

    mol_id: str
    tag: str
    mode: int                 # the mode's index among the label's vibrational modes, 0 the lowest
    atoms: int
    label_cm: float
    patched_cm: float
    coverage: float           # the share of the label mode inside the patched space
    overlap_patched: float    # the squared overlap of the label mode with the patched mode it was matched to
    k_cart: float             # hartree/bohr², the label's Rayleigh quotient along the mode's Cartesian displacement
    sample: str               # BIASED when the molecule was selected for a label mode below LOW_MODE_CM
    below_cm: float
    step_bohr: float
    noise_cm: float = 0.0     # frequency noise (cm⁻¹) per GRADIENT_NOISE_UNIT of gradient noise, at this step
    step_check_cm: float | None = None   # patched frequency at the other step minus this one; None when not checked

    @property
    def change_cm(self) -> float:
        return self.patched_cm - self.label_cm

    @property
    def flags(self) -> tuple[str, ...]:
        found = []
        if min(self.coverage, self.overlap_patched) < OVERLAP_MIN:
            found.append("overlap")
        if self.step_check_cm is not None and abs(self.step_check_cm) > STEP_AGREEMENT_CM:
            found.append("step")
        return tuple(found)

    @property
    def turned_imaginary(self) -> bool:
        return self.label_cm > 0 > self.patched_cm

    @property
    def name(self) -> str:
        return f"{self.mol_id} mode {self.mode}"


@dataclass(frozen=True)
class Rule:
    """The registered rule's arithmetic on one set of points."""

    n: int
    moved: int
    p: float | None
    se: float | None
    outcome: str
    statement: str


def cartesian_force_constant(H_raw: np.ndarray, direction: np.ndarray, masses_amu: np.ndarray) -> float:
    """The Rayleigh quotient dᵀHd / dᵀd (hartree/bohr²) of a Cartesian Hessian along the Cartesian displacement d of a mass-weighted
    direction: how stiff the molecule is against that displacement, whatever masses move."""
    d = np.asarray(direction, float) / mass_weights(masses_amu)
    return float(d @ (0.5 * (H_raw + H_raw.T)) @ d / (d @ d))


def noise_sensitivity_cm(mode: np.ndarray, omega_cm: float, masses_amu: np.ndarray, step_bohr: float) -> float:
    """The frequency noise (cm⁻¹) the patch makes of a gradient noise of GRADIENT_NOISE_UNIT per Cartesian component on one mode.

    The patch measures the mode's curvature as λ = d·(g₊ − g₋) / (2q), with d = v/√m the Cartesian displacement of the unit
    mass-weighted mode v and q the mass-weighted length of the step (the largest atomic displacement is step_bohr). Independent noise
    σ on every gradient component gives σ_λ = σ·√2·|d| / (2q), and with ω = √λ the frequency moves by σ_ω = σ_λ / (2ω). A mode of
    light atoms has a short step q for the same largest displacement, so it is the more sensitive one; so is a softer mode."""
    _, q = displacement(mode, masses_amu, step_bohr)
    d = float(np.linalg.norm(np.asarray(mode, float) / mass_weights(masses_amu)))
    if omega_cm == 0:
        return math.inf
    return GRADIENT_NOISE_UNIT * math.sqrt(2) * d / (2 * q) * HARTREE2CM ** 2 / (2 * abs(omega_cm))


def matched_mode(modes: Modes, direction: np.ndarray) -> tuple[float, float]:
    """The frequency (cm⁻¹) of the mode with the largest squared overlap with a mass-weighted unit direction, and that overlap."""
    overlap = (modes.vectors.T @ direction) ** 2
    best = int(overlap.argmax())
    return float(modes.omega_cm[best]), float(overlap[best])


def read_original_label(path: Path) -> np.ndarray:
    """H_raw of a label file that carries no repair; a repaired file is refused, because the change is read against the original."""
    with np.load(path) as z:
        if "low_mode_patch" in z.files:
            raise ValueError(f"{path} carries a low-mode repair: it is not the label a patch was made from (give the superseded original)")
        return np.asarray(z["H_raw"], float)


def read_patch(path: Path) -> dict[str, Any]:
    """What the read needs of one patched Hessian file."""
    with np.load(path) as z:
        return {"H": np.asarray(z["H_raw"], float), "U": np.asarray(z["directions"], float),
                "label_vib": np.asarray(z["freq_label_vib_cm"], float), "below_cm": float(z["below_cm"]), "step_bohr": float(z["step_bohr"])}


def patched_ids(patches: Path) -> list[str]:
    """The molecules of a patch folder that have patched Hessians; an unfinished molecule refuses the read."""
    ids = []
    for folder in sorted(p for p in patches.iterdir() if p.is_dir()):
        report = folder / "report.json"
        if not report.is_file():
            raise FileNotFoundError(f"{folder} has no report.json: the run has not finished this molecule")
        if json.loads(report.read_text(encoding="utf-8"))["directions"]:
            ids.append(folder.name)
    return ids


def remeasured_modes(modes: Modes, U: np.ndarray) -> list[tuple[int, float]]:
    """The k label modes with the largest share inside the space of the k patched directions, as (mode index, share), lowest first."""
    coverage = ((modes.vectors.T @ U) ** 2).sum(axis=1)
    chosen = np.sort(np.argsort(coverage)[::-1][:U.shape[1]])
    return [(int(i), float(coverage[i])) for i in chosen]


def molecule_points(mol_id: str, source: Source, molecules: Path) -> list[Point]:
    """Every re-measured label mode of one molecule, in both functionals."""
    geometry = json.loads((molecules / mol_id / "geometry.json").read_text(encoding="utf-8"))
    masses, coords = np.asarray(geometry["masses_amu"], float), np.asarray(geometry["coords_bohr"], float)
    labels = {tag: read_original_label(source.labels / mol_id / f"hessian_{tag}_analytic.npz") for tag in LABEL_TAGS}
    label_modes = {tag: vibrational_modes(H, masses, coords) for tag, H in labels.items()}
    sample = BIASED if any((np.abs(m.omega_cm) < LOW_MODE_CM).any() for m in label_modes.values()) else UNBIASED
    points = []
    for tag in LABEL_TAGS:
        patch = read_patch(source.patches / mol_id / f"hessian_{tag}_analytic_grfpatch.npz")
        apart = float(np.abs(np.sort(patch["label_vib"]) - label_modes[tag].omega_cm).max())
        if apart > LABEL_MATCH_CM:
            raise ValueError(f"{mol_id} {tag}: the label in {source.labels} stands {apart:.3f} cm⁻¹ from the one the patch recorded; "
                             "it is not the label this patch was made from")
        patched_modes = vibrational_modes(patch["H"], masses, coords)
        for i, coverage in remeasured_modes(label_modes[tag], patch["U"]):
            v, label_cm = label_modes[tag].vectors[:, i], float(label_modes[tag].omega_cm[i])
            patched_cm, overlap_patched = matched_mode(patched_modes, v)
            points.append(Point(mol_id, tag, i, len(masses), label_cm, patched_cm, coverage, overlap_patched,
                                cartesian_force_constant(labels[tag], v, masses), sample, patch["below_cm"], patch["step_bohr"],
                                noise_sensitivity_cm(v, label_cm, masses, patch["step_bohr"])))
    return points


def source_points(sources: tuple[Source, ...], molecules: Path) -> list[Point]:
    """The points of every source; a molecule in two sources is refused, since its points would count twice."""
    points: list[Point] = []
    seen: set[str] = set()
    for source in sources:
        for mol_id in patched_ids(source.patches):
            if mol_id in seen:
                raise ValueError(f"{mol_id} is in more than one source")
            seen.add(mol_id)
            points.extend(molecule_points(mol_id, source, molecules))
    return points


def with_step_check(points: list[Point], checks: list[Point]) -> tuple[list[Point], list[str]]:
    """Each point with the difference of its patched frequency at the other step, where the step check holds that mode; and the names
    of the check points that were set aside because their own mode has no single counterpart (such a frequency checks nothing)."""
    other = {(c.mol_id, c.tag, c.mode): c for c in checks}
    known = {(p.mol_id, p.tag, p.mode) for p in points}
    strangers = sorted(set(other) - known)
    if strangers:
        raise ValueError(f"the step check holds modes the sources do not: {strangers[:3]}")
    out, set_aside = [], []
    for p in points:
        c = other.get((p.mol_id, p.tag, p.mode))
        if c is None:
            out.append(p)
            continue
        if c.step_bohr == p.step_bohr:
            raise ValueError(f"{p.mol_id}: the step check used the same step ({p.step_bohr} bohr); it is no second route")
        if c.below_cm != p.below_cm:
            raise ValueError(f"{p.mol_id} {p.tag} mode {p.mode}: the step check patched below {c.below_cm} cm⁻¹, the source below "
                             f"{p.below_cm}; the two did not re-measure the same space")
        if "overlap" in c.flags:
            set_aside.append(f"{c.name} {c.tag}")
            out.append(p)
            continue
        out.append(replace(p, step_check_cm=c.patched_cm - p.patched_cm))
    return out, set_aside


def fraction_moved(points: list[Point]) -> tuple[int, float | None, float | None]:
    """How many points moved beyond MOVE_LINE_CM, the fraction and its binomial standard error (None for no points)."""
    n = len(points)
    moved = sum(abs(p.change_cm) > MOVE_LINE_CM for p in points)
    if n == 0:
        return moved, None, None
    p = moved / n
    return moved, p, math.sqrt(p * (1 - p) / n)


def summary_row(name: str, points: list[Point]) -> dict[str, Any]:
    """One table row: the size of the moves in a set of points, and the median of their noise per GRADIENT_NOISE_UNIT."""
    moves = np.array([abs(p.change_cm) for p in points])
    moved, p, se = fraction_moved(points)
    return {"group": name, "n": len(points), "median_abs_cm": float(np.median(moves)) if len(points) else None,
            "max_abs_cm": float(moves.max()) if len(points) else None, "moved": moved, "fraction": p, "se": se,
            "median_noise_cm": float(np.median([p.noise_cm for p in points])) if len(points) else None}


def band_rows(points: list[Point]) -> list[dict[str, Any]]:
    """The moves by label-frequency band; an empty band is a row with n = 0."""
    return [summary_row(f"{lo:g}–{hi:g}", [p for p in points if lo <= p.label_cm < hi]) for lo, hi in itertools.pairwise(BAND_EDGES_CM)]


def quartile_rows(points: list[Point]) -> list[dict[str, Any]]:
    """The moves by quartile of the Cartesian force constant; no rows when there are fewer than four points to split."""
    ordered = sorted(points, key=lambda p: p.k_cart)
    if len(ordered) < 4:
        return []
    rows = []
    for q, part in enumerate(np.array_split(np.arange(len(ordered)), 4), 1):
        chunk = [ordered[i] for i in part]
        rows.append(summary_row(f"Q{q}: {chunk[0].k_cart:.2e} to {chunk[-1].k_cart:.2e}", chunk))
    return rows


def spearman(x: list[float], y: list[float]) -> float | None:
    """Spearman's rank correlation, or None where it is undefined: fewer than three points, or one of the two constant."""
    if len(x) < 3 or len(set(x)) < 2 or len(set(y)) < 2:
        return None
    return float(spearmanr(x, y).statistic)


def correlations(points: list[Point]) -> dict[str, Any]:
    """Spearman of the size of the move against the label frequency and against log k (points with a positive force constant), and of
    the frequency against log k: when the last is large, the first two say the same thing twice."""
    stiff = [p for p in points if p.k_cart > 0]
    log_k = [math.log(p.k_cart) for p in stiff]
    return {"n_frequency": len(points), "rho_frequency": spearman([p.label_cm for p in points], [abs(p.change_cm) for p in points]),
            "n_log_k": len(stiff), "rho_log_k": spearman(log_k, [abs(p.change_cm) for p in stiff]),
            "rho_frequency_log_k": spearman([p.label_cm for p in stiff], log_k)}


def number(value: float | None, fmt: str = ".2f") -> str:
    """A number for a table or a sentence; an undefined one reads 'undefined', never NaN."""
    return "undefined" if value is None else format(value, fmt)


def ordering_sentence(points: list[Point]) -> str:
    """What orders the moves, as a description: both correlations with their signs, and how far the two quantities are one ordering."""
    c = correlations(points)
    return (f"Spearman of abs Δ against the label frequency: {number(c['rho_frequency'], '+.2f')} (n = {c['n_frequency']}); against log k: "
            f"{number(c['rho_log_k'], '+.2f')} (n = {c['n_log_k']}). Frequency against log k on the same points: "
            f"{number(c['rho_frequency_log_k'], '+.2f')}; as far as these two are one ordering the points cannot tell a frequency trigger from "
            "a force-constant trigger, and the read names none.")


def rule_outcome(n: int, moved: int) -> str:
    """The registered rule's outcome for `moved` of n points beyond the line."""
    if n < RULE_MIN_POINTS:
        return OUTCOME_UNDECIDED
    p = moved / n
    se = math.sqrt(p * (1 - p) / n)
    if p <= SOUND_P_MAX + COMPARE_EPS and p + se <= SOUND_UPPER_MAX + COMPARE_EPS:
        return OUTCOME_SOUND
    if p >= MAJORITY_P_MIN - COMPARE_EPS and p - se >= MAJORITY_LOWER_MIN - COMPARE_EPS:
        return OUTCOME_MAJORITY
    return OUTCOME_UNDECIDED


def outcome_probabilities(n: int, true_p: float) -> dict[str, float]:
    """The chance of each outcome of the rule when every one of n points moves beyond the line with probability true_p."""
    chance = dict.fromkeys((OUTCOME_SOUND, OUTCOME_MAJORITY, OUTCOME_UNDECIDED), 0.0)
    for moved in range(n + 1):
        chance[rule_outcome(n, moved)] += math.comb(n, moved) * true_p ** moved * (1 - true_p) ** (n - moved)
    return chance


def apply_rule(points: list[Point], population: str = "these points") -> Rule:
    """The registered decision rule on points already restricted to the decision window and to unflagged points; `population` names
    whom the outcome is about, and the sentence claims nothing beyond it."""
    moved, p, se = fraction_moved(points)
    n = len(points)
    outcome = rule_outcome(n, moved)
    head = f"n = {n}, {moved} moved more than {MOVE_LINE_CM} cm⁻¹"
    if p is None or se is None or n < RULE_MIN_POINTS:
        return Rule(n, moved, p, se, outcome, f"{head}: fewer than the {RULE_MIN_POINTS} points the rule needs, so it reads nothing from "
                                              "them. Outcome 3: undecided.")
    head += f": p = {p:.2f}, 1 SE = {se:.2f}"
    if outcome == OUTCOME_SOUND:
        return Rule(n, moved, p, se, outcome, f"{head}. p ≤ {SOUND_P_MAX:.2f} and p + 1 SE = {p + se:.2f} ≤ {SOUND_UPPER_MAX:.2f}. Outcome 1, "
                    f"for {population}: the labels of their modes in this window are sound at the {MOVE_LINE_CM} cm⁻¹ line.")
    if outcome == OUTCOME_MAJORITY:
        return Rule(n, moved, p, se, outcome,
                    f"{head}. p ≥ {MAJORITY_P_MIN:.2f} and p − 1 SE = {p - se:.2f} ≥ {MAJORITY_LOWER_MIN:.2f}. Outcome 2, for {population}: "
                    f"a majority of the labels of their modes in this window stand more than {MOVE_LINE_CM} cm⁻¹ from the patched value. That "
                    "says label and patch disagree, not why: the missing grid-weight derivative is one cause, the labels' older CPHF another, "
                    "and the finite difference corrects both.")
    return Rule(n, moved, p, se, outcome, f"{head}; p − 1 SE = {p - se:.2f}, p + 1 SE = {p + se:.2f}. Neither outcome 1 "
                f"(p ≤ {SOUND_P_MAX:.2f}, p + 1 SE ≤ {SOUND_UPPER_MAX:.2f}) nor outcome 2 (p ≥ {MAJORITY_P_MIN:.2f}, p − 1 SE ≥ "
                f"{MAJORITY_LOWER_MIN:.2f}) holds. Outcome 3: undecided at this sample size; the next step is the registered extension.")


def in_window(points: list[Point], window: tuple[float, float]) -> list[Point]:
    return [p for p in points if window[0] <= p.label_cm < window[1]]


def stratum_rows(points: list[Point], strata: Strata) -> list[dict[str, Any]]:
    """The fraction moved per band of the molecule's lowest mode, with the band's eligible molecules; a molecule outside the sample
    refuses the read, because its band and weight are unknown."""
    outside = sorted({p.mol_id for p in points} - set(strata.band_of))
    if outside:
        raise ValueError(f"not in the sample record: {outside[:3]}; the weighted fraction needs every registered molecule's band")
    rows = []
    for band, eligible in strata.eligible.items():
        inside = [q for q in points if strata.band_of[q.mol_id] == band]
        moved, p, _ = fraction_moved(inside)
        rows.append({"band": band, "eligible": eligible, "n": len(inside), "moved": moved, "fraction": p})
    return rows


def weighted_fraction(rows: list[dict[str, Any]]) -> float | None:
    """The fraction moved with every band weighted by its eligible molecules; undefined while a band has no point."""
    if any(r["fraction"] is None for r in rows):
        return None
    return sum(r["eligible"] * r["fraction"] for r in rows) / sum(r["eligible"] for r in rows)


def flagged_bounds(clean: list[Point], flagged: list[Point]) -> dict[str, Any]:
    """The rule's outcome with the flagged points counted as moved and as unmoved: how far the exclusion could carry the outcome."""
    n = len(clean) + len(flagged)
    moved = fraction_moved(clean)[0]
    return {"flagged": len(flagged), "n": n, "as_moved": {"moved": moved + len(flagged), "outcome": rule_outcome(n, moved + len(flagged))},
            "as_unmoved": {"moved": moved, "outcome": rule_outcome(n, moved)}}


def held_back(candidates: list[Point], clean: list[Point]) -> tuple[str, str] | None:
    """Why the step check forbids reading the rule now, as (outcome, statement), or None when it allows it."""
    failed = [p for p in candidates if "step" in p.flags]
    if len(failed) >= STEP_FAILURES_STOP:
        return OUTCOME_UNDECIDED, (f"{len(failed)} checked points differ by more than {STEP_AGREEMENT_CM} cm⁻¹ between the two steps "
                                   f"({', '.join(p.name for p in failed)}): the finite difference is not under control here. Outcome 3: "
                                   "undecided; the step check is extended to every sampled molecule before any statement.")
    waiting = [p for p in clean if NEAR_LINE_CM[0] < abs(p.change_cm) < NEAR_LINE_CM[1] and p.step_check_cm is None]
    if waiting:
        return OUTCOME_NOT_STATED, (f"No outcome is stated: {len(waiting)} point(s) moved by between {NEAR_LINE_CM[0]} and {NEAR_LINE_CM[1]} "
                                    f"cm⁻¹ and have no step check ({', '.join(f'{p.name} {p.change_cm:+.2f}' for p in waiting)}). They "
                                    "are repeated at the other step first.")
    return None


def registered_decision(points: list[Point], strata: Strata | None) -> dict[str, Any]:
    """The registered rule on the registered population, with what stands beside it: the step check's say, the bounds from the flagged
    points, and the fractions per band and weighted by the bands' sizes (descriptive)."""
    candidates = in_window([p for p in points if (p.tag, p.sample) == (DECISION_TAG, UNBIASED)], DECISION_WINDOW_CM)
    clean = [p for p in candidates if not p.flags]
    rule = apply_rule(clean, strata.population if strata else "the molecules of these sources")
    decision = asdict(rule) | {"bounds": flagged_bounds(clean, [p for p in candidates if p.flags]), "ordering": ordering_sentence(clean),
                               "strata": stratum_rows(clean, strata) if strata else None}
    decision["weighted_fraction"] = weighted_fraction(decision["strata"]) if strata else None
    stop = held_back(candidates, clean)
    if stop is not None:
        decision["outcome"], decision["statement"] = stop
    decision["points"] = [{"id": p.mol_id, "mode": p.mode, "label_cm": p.label_cm, "patched_cm": p.patched_cm, "change_cm": p.change_cm,
                           "noise_cm": p.noise_cm, "step_check_cm": p.step_check_cm, "flags": list(p.flags)} for p in candidates]
    return decision


def group_summary(tag: str, sample: str, points: list[Point]) -> dict[str, Any]:
    """The tables, correlations and rule arithmetic of one functional's unflagged points from one sample."""
    banded = in_window(points, (BAND_EDGES_CM[0], BAND_EDGES_CM[-1]))
    return {"tag": tag, "sample": sample, "registered": tag == DECISION_TAG and sample == UNBIASED, "n": len(banded),
            "bands": band_rows(banded), "quartiles": quartile_rows([p for p in banded if p.k_cart > 0]), "correlations": correlations(banded),
            "ordering": ordering_sentence(banded),
            "rms_change_cm": float(np.sqrt(np.mean([p.change_cm ** 2 for p in banded]))) if banded else None,
            "rule": asdict(apply_rule(in_window(points, DECISION_WINDOW_CM), "this group's molecules"))}


def summarise(points: list[Point], strata: Strata | None = None) -> dict[str, Any]:
    """The whole record: one group per functional and sample with unflagged points in the bands, the registered group always."""
    clean = [p for p in points if not p.flags]
    keys = sorted({(p.tag, p.sample) for p in clean} | {(DECISION_TAG, UNBIASED)})
    groups = [group_summary(tag, sample, [p for p in clean if (p.tag, p.sample) == (tag, sample)]) for tag, sample in keys]
    groups = [g for g in groups if g["n"] or g["registered"]]
    return {"points": len(points), "molecules": len({p.mol_id for p in points}),
            "flagged_overlap": sum("overlap" in p.flags for p in points), "flagged_step": sum("step" in p.flags for p in points),
            "step_checked": sum(p.step_check_cm is not None for p in points),
            "turned_imaginary": [f"{p.mol_id} {p.tag}" for p in points if p.turned_imaginary],
            "groups": groups, "decision": registered_decision(points, strata)}


def points_csv(points: list[Point]) -> str:
    """The points table, flagged points included."""
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["id", "tag", "mode", "atoms", "label_cm", "patched_cm", "change_cm", "coverage", "overlap_patched",
                     "k_cart_hartree_bohr2", "noise_cm_per_1e-7_hartree_bohr", "sample", "below_cm", "step_bohr", "step_check_cm",
                     "turned_imaginary", "flags"])
    for p in sorted(points, key=lambda p: (p.tag, p.label_cm)):
        writer.writerow([p.mol_id, p.tag, p.mode, p.atoms, f"{p.label_cm:.4f}", f"{p.patched_cm:.4f}", f"{p.change_cm:+.4f}",
                         f"{p.coverage:.4f}", f"{p.overlap_patched:.4f}", f"{p.k_cart:.6e}", f"{p.noise_cm:.4f}", p.sample, f"{p.below_cm:g}",
                         f"{p.step_bohr:g}", "" if p.step_check_cm is None else f"{p.step_check_cm:+.4f}", int(p.turned_imaginary),
                         "+".join(p.flags)])
    return buffer.getvalue()


def table(rows: list[dict[str, Any]], first: str) -> list[str]:
    """A markdown table of summary rows."""
    lines = [f"| {first} | n | median abs Δ (cm⁻¹) | max abs Δ | > {MOVE_LINE_CM} | fraction | 1 SE | median noise per {GRADIENT_NOISE_UNIT:g} |",
             "|---|---|---|---|---|---|---|---|"]
    lines += [f"| {r['group']} | {r['n']} | {number(r['median_abs_cm'])} | {number(r['max_abs_cm'])} | {r['moved']} | "
              f"{number(r['fraction'])} | {number(r['se'])} | {number(r['median_noise_cm'])} |" for r in rows]
    return lines


def group_lines(group: dict[str, Any]) -> list[str]:
    """One group's section of RESULT.md."""
    role = "the registered population; its outcome is in the section below" if group["registered"] else "description only"
    lines = [f"## {group['tag']}, {group['sample']} sample: {group['n']} unflagged points in {BAND_EDGES_CM[0]:g}–{BAND_EDGES_CM[-1]:g} cm⁻¹", "",
             *table(group["bands"], "label frequency (cm⁻¹)"), ""]
    if group["quartiles"]:
        lines += [*table(group["quartiles"], "force constant quartile (hartree/bohr²)"), ""]
    else:
        lines += ["Force-constant quartiles: fewer than four points, no split.", ""]
    lines += [f"{group['ordering']} Rms of the signed change: {number(group['rms_change_cm'])} cm⁻¹.", "",
              f"The rule's arithmetic on this group's points in {DECISION_WINDOW_CM[0]:g}–{DECISION_WINDOW_CM[1]:g} cm⁻¹ ({role}): "
              f"{group['rule']['statement']}", ""]
    return lines


def decision_lines(decision: dict[str, Any]) -> list[str]:
    """The registered rule's section of RESULT.md: the statement, what bounds it, and the registered points one by one."""
    b = decision["bounds"]
    lines = ["## The registered decision rule", "",
             f"Population: {DECISION_TAG}, {UNBIASED} sample, label frequency {DECISION_WINDOW_CM[0]:g}–{DECISION_WINDOW_CM[1]:g} cm⁻¹, unflagged. "
             f"{decision['statement']}", "",
             f"Flagged points in the window: {b['flagged']}. Counted as moved: {b['as_moved']['moved']} of {b['n']}, outcome "
             f"{b['as_moved']['outcome']}; counted as unmoved: {b['as_unmoved']['moved']} of {b['n']}, outcome {b['as_unmoved']['outcome']}. "
             "The registered fraction stays the one on unflagged points.", ""]
    if decision["strata"] is not None:
        per_band = "; ".join(f"{r['band']}: {r['moved']} of {r['n']}" for r in decision["strata"])
        sizes = "/".join(str(r["eligible"]) for r in decision["strata"])
        lines += [f"Moved per band of the molecule's lowest mode: {per_band}. Weighted by the bands' eligible molecules ({sizes}): "
                  f"{number(decision['weighted_fraction'])} (descriptive; the rule reads the unweighted fraction).", ""]
    lines += [f"What orders the moves (descriptive): {decision['ordering']}", "",
              f"| registered point | label (cm⁻¹) | patched | Δ | noise per {GRADIENT_NOISE_UNIT:g} hartree/bohr | other step − this | flags |",
              "|---|---|---|---|---|---|---|"]
    lines += [f"| {p['id']} mode {p['mode']} | {p['label_cm']:.2f} | {p['patched_cm']:.2f} | {p['change_cm']:+.2f} | {p['noise_cm']:.2f} | "
              f"{'not checked' if p['step_check_cm'] is None else format(p['step_check_cm'], '+.2f')} | {'+'.join(p['flags'])} |"
              for p in decision["points"]]
    return [*lines, ""]


def result_md(cfg: ReadConfig, record: dict[str, Any], points: list[Point]) -> str:
    """RESULT.md: what was read, the tables per functional and sample, the registered rule's statement, the flagged points."""
    lines = ["# The low-mode repair's change of a label mode, against frequency and force constant (TASKS 218)", ""]
    if cfg.exploratory is not None:
        lines += [f"**Exploratory read; it decides nothing.** {cfg.exploratory.strip()}", ""]
    lines += [f"{record['points']} points (re-measured label mode × functional) on {record['molecules']} molecules; {record['flagged_overlap']} "
              f"flagged for a coverage or overlap below {OVERLAP_MIN} and {record['flagged_step']} for two steps more than {STEP_AGREEMENT_CM} cm⁻¹ apart "
              f"({record['step_checked']} points have a step check; {len(record['step_checks_set_aside'])} check point(s) set aside for their own "
              f"overlap); flagged points are in points.csv and in no statistic. A molecule is "
              f"'{BIASED}' when a label mode of it lies below {LOW_MODE_CM:g} cm⁻¹, which is why the repair selected it. "
              f"{len(record['turned_imaginary'])} point(s) turned imaginary under the patch. 'Noise' is the frequency noise the finite "
              f"difference makes of {GRADIENT_NOISE_UNIT:g} hartree/bohr of gradient noise on that mode (see `noise_sensitivity_cm`); the "
              "gradient noise itself is not measured here.", ""]
    for group in record["groups"]:
        lines += group_lines(group)
    lines += [*decision_lines(record["decision"]), "## Flagged points", ""]
    flagged = [p for p in points if p.flags]
    lines += [f"- {p.mol_id} {p.tag} mode {p.mode}: label {p.label_cm:.2f} → {p.patched_cm:.2f} cm⁻¹, coverage {p.coverage:.2f}, overlap "
              f"after the patch {p.overlap_patched:.2f}, flags {'+'.join(p.flags)}" for p in flagged] or ["None."]
    return "\n".join(lines) + "\n"


def shown(path: Path) -> str:
    """A path as the record names it: relative to the plan folder when it lies inside."""
    resolved = path.resolve()
    return resolved.relative_to(PLAN).as_posix() if PLAN in resolved.parents else resolved.as_posix()


def run(cfg: ReadConfig) -> dict[str, Any]:
    """Read every source, write the three files, return the record."""
    points = source_points(cfg.sources, cfg.molecules)
    set_aside: list[str] = []
    if cfg.step_checks:
        points, set_aside = with_step_check(points, source_points(cfg.step_checks, cfg.molecules))
    record = summarise(points, Strata.read(cfg.sample) if cfg.sample else None)
    record["step_checks_set_aside"] = set_aside
    record["inputs"] = {"sources": [[shown(s.patches), shown(s.labels)] for s in cfg.sources],
                        "step_checks": [[shown(s.patches), shown(s.labels)] for s in cfg.step_checks],
                        "sample": shown(cfg.sample) if cfg.sample else None, "exploratory": cfg.exploratory}
    record["constants"] = {"band_edges_cm": BAND_EDGES_CM, "move_line_cm": MOVE_LINE_CM, "overlap_min": OVERLAP_MIN,
                           "step_agreement_cm": STEP_AGREEMENT_CM, "decision_window_cm": DECISION_WINDOW_CM, "rule_min_points": RULE_MIN_POINTS,
                           "near_line_cm": NEAR_LINE_CM, "step_failures_stop": STEP_FAILURES_STOP, "gradient_noise_unit": GRADIENT_NOISE_UNIT}
    cfg.out.mkdir(parents=True, exist_ok=True)
    write_atomic(cfg.out / "points.csv", points_csv(points))
    write_atomic(cfg.out / "record.json", json.dumps(record, indent=1, ensure_ascii=False) + "\n")
    write_atomic(cfg.out / "RESULT.md", result_md(cfg, record, points))
    return record


def parse_args(argv: list[str] | None = None) -> ReadConfig:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--source", action="append", default=[], help="<patch folder>=<folder of the labels it was patched from>; repeatable")
    ap.add_argument("--step-check", action="append", default=[], help="the same molecules patched at another step, as a source; repeatable")
    ap.add_argument("--molecules", type=Path, required=True, help="the corpus molecules folder (geometry.json per id)")
    ap.add_argument("--out", type=Path, required=True, help="a results folder of this read's own")
    ap.add_argument("--sample", type=Path, default=None, help="the sample script's sample.json: bands and their sizes, for the weighted fraction")
    ap.add_argument("--exploratory", default=None, help="why this read decides nothing; printed at the top of RESULT.md")
    a = ap.parse_args(argv)
    return ReadConfig(tuple(Source.parse(s) for s in a.source), tuple(Source.parse(s) for s in a.step_check), a.molecules, a.out, a.exploratory,
                      a.sample)


def main(argv: list[str] | None = None) -> None:
    cfg = parse_args(argv)
    run(cfg)
    print((cfg.out / "RESULT.md").read_text(encoding="utf-8"), flush=True)


if __name__ == "__main__":
    main()
