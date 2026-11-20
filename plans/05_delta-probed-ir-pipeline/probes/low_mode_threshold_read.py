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

**The extrapolated read (amendment 3 of the registration).** With `--second-step` the sources are read together with the same
molecules patched at twice the step, along the same directions. A central difference's error is even in the step, so per direction
the two steps' stored columns are combined as (4·C(q) − C(2q))/3, which cancels the error's q² term, and the patched Hessian is
rebuilt from those columns with the repair's own `vibrations.patched_hessian`. The extrapolated frequency is then the measurement;
each point also carries the small step's frequency and the large step's. A point whose two steps stand more than NOT_QUADRATIC_CM
apart is flagged and left out. So are the points of a molecule whose two steps were measured along rotated directions of the same
space: columns along other directions do not combine, so those points have no extrapolated value. A molecule without a second step
is a missing measurement: it is listed and holds the outcome back. The extrapolation rests on the step error growing as q², which
`probes/low_mode_step_analysis.py --third` tests on a third step; the read states an outcome only when that test's record is named
with `--q2-test` and says the law holds. `--step-check` and `--second-step` do not combine: the first is the registered read, kept
as it ran.

    python probes/low_mode_threshold_read.py --source <patches>=<labels> [--source ...]
        [--step-check <patches>=<labels> | --second-step <patches>=<labels> [--second-step ...] [--q2-test <q2_test.json>]]
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
from collections.abc import Callable
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
from vibrations import (  # noqa: E402
    LABEL_TAGS,
    LOW_MODE_CM,
    Modes,
    displacement,
    mass_weights,
    patched_hessian,
    vibrational_modes,
)

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
STEP_RATIO = 2.0              # the extrapolated read's second step is twice its first (0.02 against 0.01 bohr)
WEIGHT_SMALL = STEP_RATIO ** 2 / (STEP_RATIO ** 2 - 1)   # 4/3 and
WEIGHT_LARGE = -1.0 / (STEP_RATIO ** 2 - 1)              # −1/3: Richardson's weights in q², which cancel the step's quadratic error
# √65/6 ≈ 1.344: a column's gradient noise goes as 1/q, so the large step's is 1/STEP_RATIO of the small step's, and the two add in
# quadrature with the weights. The extrapolated value is this much noisier than the small step's.
EXTRAPOLATED_NOISE_FACTOR = math.hypot(WEIGHT_SMALL, WEIGHT_LARGE / STEP_RATIO)
NOT_QUADRATIC_CM = 1.0        # two steps further apart than this: a two-point extrapolation is not trusted (the seven checked reach 0.57)
NOT_QUADRATIC = "not quadratic"
DIRECTIONS_DIFFER = "directions differ"   # the two steps were measured along rotated directions of one space: no extrapolated value
SPAN_TOL = 1e-10              # how far the two steps' projectors may stand apart and their directions still span one space
Q2_HOLDS, Q2_FAILS = "holds", "fails"     # the verdicts of the q²-test record (probes/low_mode_step_analysis.py --third)
DIRECTIONS_TOL = 1e-12        # the two steps' directions must be the same numbers: columns along rotated directions do not combine
STEP_RATIO_TOL = 1e-9
REBUILD_TOL_CM = 1e-6         # a step's patch rebuilt from its stored columns must give the patched frequencies the runner stored
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
    second_steps: tuple[Source, ...] = ()   # the sources' molecules at STEP_RATIO times the step: the read is then the extrapolated one
    q2_test: Path | None = None             # the q²-test record; without one that holds the extrapolated read states no outcome

    def __post_init__(self) -> None:
        if not self.sources:
            raise ValueError("no source given")
        if self.q2_test is not None and not self.second_steps:
            raise ValueError("a q²-test record belongs to the extrapolated read: give it with a second step")
        if self.step_checks and self.second_steps:
            raise ValueError("a step check belongs to the registered read and a second step to the extrapolated one: give one of the two")
        inputs = [self.molecules,
                  *(p for s in (*self.sources, *self.step_checks, *self.second_steps) for p in (s.patches, s.labels))]
        missing = [str(p) for p in inputs if not p.is_dir()]
        if self.sample is not None and not self.sample.is_file():
            missing.append(str(self.sample))
        if self.q2_test is not None and not self.q2_test.is_file():
            missing.append(str(self.q2_test))
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
    small_step_cm: float | None = None   # an extrapolated point only: the patched frequency at the small step
    large_step_cm: float | None = None   # and at the large one; patched_cm is then the value extrapolated to step zero
    directions_differ: bool = False      # the two steps used rotated directions: patched_cm is the small step's, nothing is extrapolated

    @property
    def change_cm(self) -> float:
        return self.patched_cm - self.label_cm

    @property
    def two_step_cm(self) -> float | None:
        """The large step's patched frequency minus the small step's; None for a point that is not extrapolated."""
        if self.small_step_cm is None or self.large_step_cm is None:
            return None
        return self.large_step_cm - self.small_step_cm

    @property
    def small_step_change_cm(self) -> float | None:
        """The change the small step alone gives: what the registered read called the change."""
        return None if self.small_step_cm is None else self.small_step_cm - self.label_cm

    @property
    def bias_removed_cm(self) -> float | None:
        """How far the small step's frequency stands from the extrapolated one: the size of the step bias the extrapolation removed.
        None where nothing was extrapolated."""
        return None if self.small_step_cm is None or self.directions_differ else abs(self.small_step_cm - self.patched_cm)

    @property
    def flags(self) -> tuple[str, ...]:
        found = []
        if min(self.coverage, self.overlap_patched) < OVERLAP_MIN:
            found.append("overlap")
        if self.step_check_cm is not None and abs(self.step_check_cm) > STEP_AGREEMENT_CM:
            found.append("step")
        if self.two_step_cm is not None and abs(self.two_step_cm) > NOT_QUADRATIC_CM:
            found.append(NOT_QUADRATIC)
        if self.directions_differ:
            found.append(DIRECTIONS_DIFFER)
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


def read_step(path: Path) -> dict[str, Any]:
    """One patched Hessian file as a step of the extrapolation: what the read needs, the measured columns, and the patched frequencies
    the runner stored."""
    with np.load(path) as z:
        stored = {"C": np.asarray(z["columns"], float), "patched_vib": np.asarray(z["freq_patched_vib_cm"], float)}
    return read_patch(path) | stored


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


@dataclass(frozen=True)
class Molecule:
    """One molecule's geometry and original labels, with the labels' vibrational modes."""

    mol_id: str
    masses: np.ndarray
    coords: np.ndarray
    labels: dict[str, np.ndarray]
    modes: dict[str, Modes]

    @classmethod
    def read(cls, mol_id: str, labels: Path, molecules: Path) -> Molecule:
        geometry = json.loads((molecules / mol_id / "geometry.json").read_text(encoding="utf-8"))
        masses, coords = np.asarray(geometry["masses_amu"], float), np.asarray(geometry["coords_bohr"], float)
        hessians = {tag: read_original_label(labels / mol_id / f"hessian_{tag}_analytic.npz") for tag in LABEL_TAGS}
        return cls(mol_id, masses, coords, hessians, {tag: vibrational_modes(H, masses, coords) for tag, H in hessians.items()})

    @property
    def sample(self) -> str:
        return BIASED if any((np.abs(m.omega_cm) < LOW_MODE_CM).any() for m in self.modes.values()) else UNBIASED


def patch_of(mol: Molecule, tag: str, source: Source, reader: Callable[[Path], dict[str, Any]] = read_patch) -> dict[str, Any]:
    """One functional's patch record from a source, refused when it was not made from this molecule's label."""
    patch = reader(source.patches / mol.mol_id / f"hessian_{tag}_analytic_grfpatch.npz")
    apart = float(np.abs(np.sort(patch["label_vib"]) - mol.modes[tag].omega_cm).max())
    if apart > LABEL_MATCH_CM:
        raise ValueError(f"{mol.mol_id} {tag}: the label in {source.labels} stands {apart:.3f} cm⁻¹ from the one the patch recorded; "
                         "it is not the label this patch was made from")
    return patch


def tag_points(mol: Molecule, tag: str, patch: dict[str, Any], H_patched: np.ndarray) -> list[Point]:
    """Every re-measured label mode of one functional, read against a patched Hessian made along the patch's directions."""
    modes, patched_modes = mol.modes[tag], vibrational_modes(H_patched, mol.masses, mol.coords)
    points = []
    for i, coverage in remeasured_modes(modes, patch["U"]):
        v, label_cm = modes.vectors[:, i], float(modes.omega_cm[i])
        patched_cm, overlap_patched = matched_mode(patched_modes, v)
        points.append(Point(mol.mol_id, tag, i, len(mol.masses), label_cm, patched_cm, coverage, overlap_patched,
                            cartesian_force_constant(mol.labels[tag], v, mol.masses), mol.sample, patch["below_cm"], patch["step_bohr"],
                            noise_sensitivity_cm(v, label_cm, mol.masses, patch["step_bohr"])))
    return points


def molecule_points(mol_id: str, source: Source, molecules: Path) -> list[Point]:
    """Every re-measured label mode of one molecule, in both functionals."""
    mol = Molecule.read(mol_id, source.labels, molecules)
    points = []
    for tag in LABEL_TAGS:
        patch = patch_of(mol, tag, source)
        points.extend(tag_points(mol, tag, patch, patch["H"]))
    return points


def molecules_of(sources: tuple[Source, ...], kind: str = "source") -> dict[str, Source]:
    """Each patched molecule's source; a molecule in two of them is refused, since its points would count twice."""
    found: dict[str, Source] = {}
    for source in sources:
        for mol_id in patched_ids(source.patches):
            if mol_id in found:
                raise ValueError(f"{mol_id} is in more than one {kind}")
            found[mol_id] = source
    return found


def source_points(sources: tuple[Source, ...], molecules: Path) -> list[Point]:
    """The points of every source."""
    return [p for mol_id, source in molecules_of(sources).items() for p in molecule_points(mol_id, source, molecules)]


def extrapolated_columns(small: np.ndarray, large: np.ndarray) -> np.ndarray:
    """The columns at step zero from the columns at a step q and at STEP_RATIO·q along the same directions.

    A central difference's error is even in the step, C(q) = C₀ + a·q² + b·q⁴ + …, so WEIGHT_SMALL·C(q) + WEIGHT_LARGE·C(STEP_RATIO·q)
    cancels the q² term: exact for a potential that is quartic along the direction, and with −STEP_RATIO²·b·q⁴ left of a sextic one."""
    if small.shape != large.shape:
        raise ValueError(f"the two steps' columns differ in shape: {small.shape} and {large.shape}")
    return WEIGHT_SMALL * small + WEIGHT_LARGE * large


def directions_apart(small: np.ndarray, large: np.ndarray) -> float:
    """The largest difference between two steps' directions; infinite when even their shapes differ."""
    return math.inf if small.shape != large.shape else float(np.abs(small - large).max())


def step_pair_refusal(small: dict[str, Any], large: dict[str, Any], rotated: bool = False) -> str | None:
    """Why two patch records are not the two steps of one measurement, or None when they are. `rotated` asks only for the steps and
    the space: the two records are then not combined, and their directions may differ."""
    apart = directions_apart(small["U"], large["U"])
    if not rotated and apart > DIRECTIONS_TOL:
        return (f"the two steps were measured along different directions (largest difference {apart:.1e}); columns along other "
                "directions carry another step error and do not combine")
    if abs(large["step_bohr"] / small["step_bohr"] - STEP_RATIO) > STEP_RATIO_TOL:
        return f"the steps are {small['step_bohr']:g} and {large['step_bohr']:g} bohr; the weights are those of a ratio of {STEP_RATIO:g}"
    if large["below_cm"] != small["below_cm"]:
        return f"the steps patched below {small['below_cm']:g} and below {large['below_cm']:g} cm⁻¹: not the same space"
    return None


def rebuilt_modes(mol: Molecule, tag: str, step: dict[str, Any]) -> Modes:
    """The modes of one step's patch, rebuilt from the label and the step's stored columns. They must be the ones the runner stored:
    only then is the extrapolated Hessian the runner's own arithmetic on other columns."""
    modes = vibrational_modes(patched_hessian(mol.labels[tag], mol.masses, step["U"], step["C"]), mol.masses, mol.coords)
    stored = np.sort(step["patched_vib"])
    apart = float(np.abs(modes.omega_cm - stored).max()) if stored.shape == modes.omega_cm.shape else math.inf
    if apart > REBUILD_TOL_CM:
        raise ValueError(f"{mol.mol_id} {tag}, step {step['step_bohr']:g}: the patch rebuilt from the stored columns stands {apart:.2e} "
                         f"cm⁻¹ from the stored patched frequencies (limit {REBUILD_TOL_CM:g}); the columns are not this label's")
    return modes


def extrapolated_tag_points(mol: Molecule, tag: str, small: dict[str, Any], large: dict[str, Any]) -> list[Point]:
    """One functional's points with the step extrapolated away: the patched Hessian is rebuilt from the extrapolated columns, and each
    point keeps the frequencies of the two steps beside it. The overlap is the smallest of the three matches, so a point whose mode has
    no single counterpart at either step is flagged like one that has none at step zero."""
    refusal = step_pair_refusal(small, large)
    if refusal is not None:
        raise ValueError(f"{mol.mol_id} {tag}: {refusal}")
    at_small, at_large = rebuilt_modes(mol, tag, small), rebuilt_modes(mol, tag, large)
    H_zero = patched_hessian(mol.labels[tag], mol.masses, small["U"], extrapolated_columns(small["C"], large["C"]))
    points = []
    for p in tag_points(mol, tag, small, H_zero):
        v = mol.modes[tag].vectors[:, p.mode]
        (small_cm, small_overlap), (large_cm, large_overlap) = matched_mode(at_small, v), matched_mode(at_large, v)
        points.append(replace(p, small_step_cm=small_cm, large_step_cm=large_cm, noise_cm=p.noise_cm * EXTRAPOLATED_NOISE_FACTOR,
                              overlap_patched=min(p.overlap_patched, small_overlap, large_overlap)))
    return points


def same_space(small: np.ndarray, large: np.ndarray) -> bool:
    """Whether two steps' directions span one space, whatever their rotation in it."""
    return small.shape == large.shape and float(np.abs(small @ small.T - large @ large.T).max()) <= SPAN_TOL


def rotated_tag_points(mol: Molecule, tag: str, small: dict[str, Any], large: dict[str, Any]) -> list[Point]:
    """One functional's points where the two steps were measured along rotated directions of one space. Each step's patched Hessian
    is whole, so both frequencies are known, but the columns do not combine: the point keeps the small step's value as its patched
    frequency and is flagged, which leaves it out of every statistic."""
    refusal = step_pair_refusal(small, large, rotated=True)
    if refusal is not None or not same_space(small["U"], large["U"]):
        raise ValueError(f"{mol.mol_id} {tag}: {refusal or 'the two steps did not re-measure the same space'}")
    at_large = vibrational_modes(large["H"], mol.masses, mol.coords)
    points = []
    for p in tag_points(mol, tag, small, small["H"]):
        large_cm, large_overlap = matched_mode(at_large, mol.modes[tag].vectors[:, p.mode])
        points.append(replace(p, small_step_cm=p.patched_cm, large_step_cm=large_cm, directions_differ=True,
                              overlap_patched=min(p.overlap_patched, large_overlap)))
    return points


def extrapolated_points(cfg: ReadConfig) -> tuple[list[Point], list[dict[str, str]]]:
    """The points of every source molecule that has both steps — extrapolated, or flagged where the two steps used rotated
    directions — and the molecules that have no second step: those are missing measurements and hold the outcome back."""
    first, second = molecules_of(cfg.sources), molecules_of(cfg.second_steps, "second-step folder")
    strangers = sorted(set(second) - set(first))
    if strangers:
        raise ValueError(f"the second step holds molecules the sources do not: {strangers[:3]}")
    points: list[Point] = []
    unread: list[dict[str, str]] = []
    for mol_id, source in first.items():
        if mol_id not in second:
            unread.append({"id": mol_id, "reason": "no second step"})
            continue
        mol = Molecule.read(mol_id, source.labels, cfg.molecules)
        steps = {tag: (patch_of(mol, tag, source, read_step), patch_of(mol, tag, second[mol_id], read_step)) for tag in LABEL_TAGS}
        apart = max(directions_apart(small["U"], large["U"]) for small, large in steps.values())
        for tag, (small, large) in steps.items():
            points.extend((rotated_tag_points if apart > DIRECTIONS_TOL else extrapolated_tag_points)(mol, tag, small, large))
    return points, unread


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


@dataclass(frozen=True)
class Extrapolation:
    """What the extrapolated read knows besides its points: the molecules without a second step, and the q²-test record it was
    given (None when it was given none)."""

    unread: tuple[dict[str, str], ...] = ()
    q2_test: dict[str, Any] | None = None


def read_q2_test(path: Path) -> dict[str, Any]:
    """The q²-test record's verdict, ratios and interval; a file that is no such record is refused."""
    record = json.loads(path.read_text(encoding="utf-8"))
    ratios = record.get("ratios") if isinstance(record, dict) else None
    if not isinstance(ratios, list) or not ratios or record.get("verdict") not in (Q2_HOLDS, Q2_FAILS) or "interval" not in record:
        raise ValueError(f"{path} is no q²-test record: it needs a verdict ({Q2_HOLDS!r} or {Q2_FAILS!r}), its ratios and their interval")
    return {"record": shown(path), "verdict": record["verdict"], "interval": list(record["interval"]),
            "ratios": [{key: r[key] for key in ("id", "tag", "direction", "ratio")} for r in ratios]}


def q2_sentence(q2_test: dict[str, Any]) -> str:
    """The q² test's ratios and verdict in one sentence."""
    ratios = ", ".join(f"{r['id']} {r['tag']} {r['ratio']:.2f}" for r in q2_test["ratios"])
    return (f"the q² test {q2_test['verdict']} (`{q2_test['record']}`): R = {ratios}; the law is taken to hold when every R lies in "
            f"{q2_test['interval'][0]:g}–{q2_test['interval'][1]:g}")


def held_back_extrapolated(candidates: list[Point], extrapolation: Extrapolation) -> tuple[str, str] | None:
    """Why the extrapolated read states no outcome, or an undecided one, as (outcome, statement); None when the rule may be read."""
    if extrapolation.unread:
        return OUTCOME_NOT_STATED, (f"No outcome is stated: {len(extrapolation.unread)} molecule(s) have no second step "
                                    f"({', '.join(u['id'] for u in extrapolation.unread)}). That is a missing measurement; the rule is "
                                    "read when every molecule has both steps.")
    if extrapolation.q2_test is None:
        return OUTCOME_NOT_STATED, ("No outcome is stated: no record of the q² test was given (`--q2-test`). The extrapolated value is "
                                    "the measurement only once the step error is shown to grow as q² on a third step.")
    if extrapolation.q2_test["verdict"] != Q2_HOLDS:
        return OUTCOME_NOT_STATED, (f"No outcome is stated by the extrapolated read: {q2_sentence(extrapolation.q2_test)}. A two-point "
                                    "extrapolation is not trusted, and the registered read's outcome 3 stands.")
    failed = [p for p in candidates if NOT_QUADRATIC in p.flags]
    if len(failed) >= STEP_FAILURES_STOP:
        return OUTCOME_UNDECIDED, (f"{len(failed)} points differ by more than {NOT_QUADRATIC_CM} cm⁻¹ between the two steps "
                                   f"({', '.join(p.name for p in failed)}): the step error is not quadratic there and a two-point "
                                   "extrapolation is not trusted. Outcome 3: undecided.")
    return None


def decision_point(p: Point, extrapolated: bool) -> dict[str, Any]:
    """One registered point as the record lists it; an extrapolated one with its three numbers and the two steps' difference."""
    listed = {"id": p.mol_id, "mode": p.mode, "label_cm": p.label_cm, "patched_cm": p.patched_cm, "change_cm": p.change_cm,
              "noise_cm": p.noise_cm, "step_check_cm": p.step_check_cm, "flags": list(p.flags)}
    if extrapolated:
        listed |= {"small_step_change_cm": p.small_step_change_cm, "bias_removed_cm": p.bias_removed_cm, "two_step_cm": p.two_step_cm}
    return listed


def registered_decision(points: list[Point], strata: Strata | None, extrapolation: Extrapolation | None = None) -> dict[str, Any]:
    """The registered rule on the registered population, with what stands beside it: the step check's say, the bounds from the flagged
    points, and the fractions per band and weighted by the bands' sizes (descriptive). `extrapolation` is given by the extrapolated
    read; the rule is then held back by a molecule without a second step, by a q² test that is absent or failed, and by points that
    are not quadratic in the step."""
    candidates = in_window([p for p in points if (p.tag, p.sample) == (DECISION_TAG, UNBIASED)], DECISION_WINDOW_CM)
    clean = [p for p in candidates if not p.flags]
    rule = apply_rule(clean, strata.population if strata else "the molecules of these sources")
    decision = asdict(rule) | {"bounds": flagged_bounds(clean, [p for p in candidates if p.flags]), "ordering": ordering_sentence(clean),
                               "strata": stratum_rows(clean, strata) if strata else None}
    decision["weighted_fraction"] = weighted_fraction(decision["strata"]) if strata else None
    stop = held_back(candidates, clean) if extrapolation is None else held_back_extrapolated(candidates, extrapolation)
    if stop is not None:
        decision["outcome"], decision["statement"] = stop
    decision["points"] = [decision_point(p, extrapolation is not None) for p in candidates]
    return decision


def group_summary(tag: str, sample: str, points: list[Point]) -> dict[str, Any]:
    """The tables, correlations and rule arithmetic of one functional's unflagged points from one sample."""
    banded = in_window(points, (BAND_EDGES_CM[0], BAND_EDGES_CM[-1]))
    return {"tag": tag, "sample": sample, "registered": tag == DECISION_TAG and sample == UNBIASED, "n": len(banded),
            "bands": band_rows(banded), "quartiles": quartile_rows([p for p in banded if p.k_cart > 0]), "correlations": correlations(banded),
            "ordering": ordering_sentence(banded),
            "rms_change_cm": float(np.sqrt(np.mean([p.change_cm ** 2 for p in banded]))) if banded else None,
            "rule": asdict(apply_rule(in_window(points, DECISION_WINDOW_CM), "this group's molecules"))}


def summarise(points: list[Point], strata: Strata | None = None, extrapolation: Extrapolation | None = None) -> dict[str, Any]:
    """The whole record: one group per functional and sample with unflagged points in the bands, the registered group always. For the
    extrapolated read the record also names the molecules without a second step, counts the points that are not quadratic in the
    step and those whose steps used rotated directions, and carries the q² test it was given."""
    clean = [p for p in points if not p.flags]
    keys = sorted({(p.tag, p.sample) for p in clean} | {(DECISION_TAG, UNBIASED)})
    groups = [group_summary(tag, sample, [p for p in clean if (p.tag, p.sample) == (tag, sample)]) for tag, sample in keys]
    groups = [g for g in groups if g["n"] or g["registered"]]
    record = {"points": len(points), "molecules": len({p.mol_id for p in points}),
              "flagged_overlap": sum("overlap" in p.flags for p in points), "flagged_step": sum("step" in p.flags for p in points),
              "step_checked": sum(p.step_check_cm is not None for p in points),
              "turned_imaginary": [f"{p.mol_id} {p.tag}" for p in points if p.turned_imaginary],
              "groups": groups, "decision": registered_decision(points, strata, extrapolation)}
    if extrapolation is not None:
        record |= {"flagged_not_quadratic": sum(NOT_QUADRATIC in p.flags for p in points),
                   "flagged_directions": sum(DIRECTIONS_DIFFER in p.flags for p in points),
                   "unread": list(extrapolation.unread), "q2_test": extrapolation.q2_test}
    return record


def points_csv(points: list[Point], extrapolated: bool = False) -> str:
    """The points table, flagged points included; for the extrapolated read with the small step's change, the bias removed and the
    two steps' difference (patched_cm and change_cm are then the extrapolated values, step_bohr the small step)."""
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    header = ["id", "tag", "mode", "atoms", "label_cm", "patched_cm", "change_cm", "coverage", "overlap_patched",
              "k_cart_hartree_bohr2", "noise_cm_per_1e-7_hartree_bohr", "sample", "below_cm", "step_bohr", "step_check_cm",
              "turned_imaginary", "flags"]
    writer.writerow(header + (["small_step_change_cm", "bias_removed_cm", "large_minus_small_step_cm"] if extrapolated else []))
    for p in sorted(points, key=lambda p: (p.tag, p.label_cm)):
        row = [p.mol_id, p.tag, p.mode, p.atoms, f"{p.label_cm:.4f}", f"{p.patched_cm:.4f}", f"{p.change_cm:+.4f}",
               f"{p.coverage:.4f}", f"{p.overlap_patched:.4f}", f"{p.k_cart:.6e}", f"{p.noise_cm:.4f}", p.sample, f"{p.below_cm:g}",
               f"{p.step_bohr:g}", "" if p.step_check_cm is None else f"{p.step_check_cm:+.4f}", int(p.turned_imaginary),
               "+".join(p.flags)]
        if extrapolated:
            row += [f"{p.small_step_change_cm:+.4f}", "" if p.bias_removed_cm is None else f"{p.bias_removed_cm:.4f}",
                    f"{p.two_step_cm:+.4f}"]
        writer.writerow(row)
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


def extrapolated_row(name: str, label_cm: float, values: dict[str, Any]) -> str:
    """One row of an extrapolated read's point table: the extrapolated change first, then what the small step alone gave. A point
    whose steps used rotated directions has no extrapolated value, and its row says so."""
    if values["bias_removed_cm"] is None:
        zero, bias = "none | none", "none"
    else:
        zero, bias = f"{values['patched_cm']:.2f} | {values['change_cm']:+.2f}", f"{values['bias_removed_cm']:.2f}"
    return (f"| {name} | {label_cm:.2f} | {zero} | {values['small_step_change_cm']:+.2f} | {bias} | {values['two_step_cm']:+.2f} | "
            f"{values['noise_cm']:.2f} | {'+'.join(values['flags'])} |")


def extrapolated_table(first: str) -> list[str]:
    """The head of an extrapolated read's point table."""
    return [f"| {first} | label (cm⁻¹) | extrapolated | Δ extrapolated | Δ at the small step | step bias removed | large − small step | "
            f"noise per {GRADIENT_NOISE_UNIT:g} hartree/bohr | flags |", "|---|---|---|---|---|---|---|---|---|"]


def decision_lines(decision: dict[str, Any], extrapolated: bool = False) -> list[str]:
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
    lines += [f"What orders the moves (descriptive): {decision['ordering']}", ""]
    if extrapolated:
        lines += extrapolated_table("registered point")
        lines += [extrapolated_row(f"{p['id']} mode {p['mode']}", p["label_cm"], p) for p in decision["points"]]
        return [*lines, ""]
    lines += [f"| registered point | label (cm⁻¹) | patched | Δ | noise per {GRADIENT_NOISE_UNIT:g} hartree/bohr | other step − this | flags |",
              "|---|---|---|---|---|---|---|"]
    lines += [f"| {p['id']} mode {p['mode']} | {p['label_cm']:.2f} | {p['patched_cm']:.2f} | {p['change_cm']:+.2f} | {p['noise_cm']:.2f} | "
              f"{'not checked' if p['step_check_cm'] is None else format(p['step_check_cm'], '+.2f')} | {'+'.join(p['flags'])} |"
              for p in decision["points"]]
    return [*lines, ""]


def registered_intro(record: dict[str, Any]) -> list[str]:
    """What the registered read read, in one paragraph."""
    return [f"{record['points']} points (re-measured label mode × functional) on {record['molecules']} molecules; {record['flagged_overlap']} "
            f"flagged for a coverage or overlap below {OVERLAP_MIN} and {record['flagged_step']} for two steps more than {STEP_AGREEMENT_CM} cm⁻¹ apart "
            f"({record['step_checked']} points have a step check; {len(record['step_checks_set_aside'])} check point(s) set aside for their own "
            f"overlap); flagged points are in points.csv and in no statistic. A molecule is "
            f"'{BIASED}' when a label mode of it lies below {LOW_MODE_CM:g} cm⁻¹, which is why the repair selected it. "
            f"{len(record['turned_imaginary'])} point(s) turned imaginary under the patch. 'Noise' is the frequency noise the finite "
            f"difference makes of {GRADIENT_NOISE_UNIT:g} hartree/bohr of gradient noise on that mode (see `noise_sensitivity_cm`); the "
            "gradient noise itself is not measured here.", ""]


def extrapolated_intro(record: dict[str, Any], points: list[Point]) -> list[str]:
    """What the extrapolated read read, the molecules it could not read, and every point with its three numbers."""
    lines = [f"**Extrapolated to step zero (amendment 3 of the registration).** {record['points']} points (re-measured label mode × "
             f"functional) on {record['molecules']} molecules, each measured at a step and at {STEP_RATIO:g} times it. Per direction the two "
             f"steps' columns are combined as {WEIGHT_SMALL:.4f}·C(small) {WEIGHT_LARGE:+.4f}·C(large), which cancels the part of the "
             "finite-difference error that grows as the square of the step, and the patched Hessian is rebuilt from those columns. "
             "'Patched' and Δ below are the extrapolated values. "
             f"{record['flagged_overlap']} points are flagged for a coverage or overlap below {OVERLAP_MIN} (at step zero or at either step) "
             f"and {record['flagged_not_quadratic']} as '{NOT_QUADRATIC}', their two steps standing more than {NOT_QUADRATIC_CM} cm⁻¹ apart; "
             f"{record['flagged_directions']} are flagged '{DIRECTIONS_DIFFER}': their molecule's two steps were measured along rotated "
             "directions of the same space, so they have no extrapolated value (their noise is the small step's). "
             "Flagged points are in points.csv and in no statistic. "
             f"A molecule is '{BIASED}' when a label mode of it lies below {LOW_MODE_CM:g} cm⁻¹. {len(record['turned_imaginary'])} point(s) "
             f"turned imaginary under the patch. 'Noise' is the frequency noise the extrapolated value carries per {GRADIENT_NOISE_UNIT:g} "
             f"hartree/bohr of gradient noise: the small step's (`noise_sensitivity_cm`) times {EXTRAPOLATED_NOISE_FACTOR:.3f}; the gradient "
             "noise itself is not measured here.", ""]
    if record["q2_test"] is None:
        lines += ["**No record of the q² test was given**, so this read states no outcome.", ""]
    else:
        lines += [f"On a third step {q2_sentence(record['q2_test'])}.", ""]
    if record["unread"]:
        lines += [f"**{len(record['unread'])} molecule(s) have no second step** and no point here: "
                  + ", ".join(u["id"] for u in record["unread"]) + ".", ""]
    lines += ["## Every point: extrapolated, at the small step, and the step bias removed", "", *extrapolated_table("point")]
    lines += [extrapolated_row(f"{p.mol_id} {p.tag} mode {p.mode}", p.label_cm, decision_point(p, True))
              for p in sorted(points, key=lambda p: (p.tag, p.label_cm))]
    return [*lines, ""]


def result_md(cfg: ReadConfig, record: dict[str, Any], points: list[Point]) -> str:
    """RESULT.md: what was read, the tables per functional and sample, the registered rule's statement, the flagged points."""
    extrapolated = bool(cfg.second_steps)
    lines = ["# The low-mode repair's change of a label mode, against frequency and force constant (TASKS 218)", ""]
    if cfg.exploratory is not None:
        lines += [f"**Exploratory read; it decides nothing.** {cfg.exploratory.strip()}", ""]
    lines += extrapolated_intro(record, points) if extrapolated else registered_intro(record)
    for group in record["groups"]:
        lines += group_lines(group)
    lines += [*decision_lines(record["decision"], extrapolated), "## Flagged points", ""]
    flagged = [p for p in points if p.flags]
    lines += [f"- {p.mol_id} {p.tag} mode {p.mode}: label {p.label_cm:.2f} → {p.patched_cm:.2f} cm⁻¹, coverage {p.coverage:.2f}, overlap "
              f"after the patch {p.overlap_patched:.2f}, flags {'+'.join(p.flags)}" for p in flagged] or ["None."]
    return "\n".join(lines) + "\n"


def shown(path: Path) -> str:
    """A path as the record names it: relative to the plan folder when it lies inside."""
    resolved = path.resolve()
    return resolved.relative_to(PLAN).as_posix() if PLAN in resolved.parents else resolved.as_posix()


def registered_record(cfg: ReadConfig) -> tuple[dict[str, Any], list[Point]]:
    """The registered read: every source at its one step, with the step check where one is given."""
    points = source_points(cfg.sources, cfg.molecules)
    set_aside: list[str] = []
    if cfg.step_checks:
        points, set_aside = with_step_check(points, source_points(cfg.step_checks, cfg.molecules))
    record = summarise(points, Strata.read(cfg.sample) if cfg.sample else None)
    record["step_checks_set_aside"] = set_aside
    return record, points


def extrapolated_record(cfg: ReadConfig) -> tuple[dict[str, Any], list[Point]]:
    """The extrapolated read: every source molecule from its two steps."""
    points, unread = extrapolated_points(cfg)
    extrapolation = Extrapolation(tuple(unread), read_q2_test(cfg.q2_test) if cfg.q2_test else None)
    return summarise(points, Strata.read(cfg.sample) if cfg.sample else None, extrapolation), points


def run(cfg: ReadConfig) -> dict[str, Any]:
    """Read every source, write the three files, return the record."""
    extrapolated = bool(cfg.second_steps)
    record, points = extrapolated_record(cfg) if extrapolated else registered_record(cfg)
    record["inputs"] = {"sources": [[shown(s.patches), shown(s.labels)] for s in cfg.sources],
                        "step_checks": [[shown(s.patches), shown(s.labels)] for s in cfg.step_checks],
                        "sample": shown(cfg.sample) if cfg.sample else None, "exploratory": cfg.exploratory}
    record["constants"] = {"band_edges_cm": BAND_EDGES_CM, "move_line_cm": MOVE_LINE_CM, "overlap_min": OVERLAP_MIN,
                           "step_agreement_cm": STEP_AGREEMENT_CM, "decision_window_cm": DECISION_WINDOW_CM, "rule_min_points": RULE_MIN_POINTS,
                           "near_line_cm": NEAR_LINE_CM, "step_failures_stop": STEP_FAILURES_STOP, "gradient_noise_unit": GRADIENT_NOISE_UNIT}
    if extrapolated:
        record["inputs"]["second_steps"] = [[shown(s.patches), shown(s.labels)] for s in cfg.second_steps]
        record["constants"] |= {"step_ratio": STEP_RATIO, "weight_small": WEIGHT_SMALL, "weight_large": WEIGHT_LARGE,
                                "extrapolated_noise_factor": EXTRAPOLATED_NOISE_FACTOR, "not_quadratic_cm": NOT_QUADRATIC_CM,
                                "directions_tol": DIRECTIONS_TOL, "span_tol": SPAN_TOL, "rebuild_tol_cm": REBUILD_TOL_CM}
    cfg.out.mkdir(parents=True, exist_ok=True)
    write_atomic(cfg.out / "points.csv", points_csv(points, extrapolated))
    write_atomic(cfg.out / "record.json", json.dumps(record, indent=1, ensure_ascii=False) + "\n")
    write_atomic(cfg.out / "RESULT.md", result_md(cfg, record, points))
    return record


def parse_args(argv: list[str] | None = None) -> ReadConfig:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--source", action="append", default=[], help="<patch folder>=<folder of the labels it was patched from>; repeatable")
    ap.add_argument("--step-check", action="append", default=[], help="the same molecules patched at another step, as a source; repeatable")
    ap.add_argument("--second-step", action="append", default=[],
                    help="the sources' molecules patched at twice the step, as a source: the read extrapolates to step zero; repeatable")
    ap.add_argument("--q2-test", type=Path, default=None,
                    help="the q²-test record of low_mode_step_analysis.py --third; the extrapolated read states no outcome without one that holds")
    ap.add_argument("--molecules", type=Path, required=True, help="the corpus molecules folder (geometry.json per id)")
    ap.add_argument("--out", type=Path, required=True, help="a results folder of this read's own")
    ap.add_argument("--sample", type=Path, default=None, help="the sample script's sample.json: bands and their sizes, for the weighted fraction")
    ap.add_argument("--exploratory", default=None, help="why this read decides nothing; printed at the top of RESULT.md")
    a = ap.parse_args(argv)
    return ReadConfig(tuple(Source.parse(s) for s in a.source), tuple(Source.parse(s) for s in a.step_check), a.molecules, a.out, a.exploratory,
                      a.sample, tuple(Source.parse(s) for s in a.second_step), a.q2_test)


def main(argv: list[str] | None = None) -> None:
    cfg = parse_args(argv)
    run(cfg)
    print((cfg.out / "RESULT.md").read_text(encoding="utf-8"), flush=True)


if __name__ == "__main__":
    main()
