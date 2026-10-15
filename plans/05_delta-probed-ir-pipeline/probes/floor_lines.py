"""The registered lines shared by the two floor tests of TASKS 65 (15 Oct 2026; `architecture_floor.py`, `hybrid_form_floor.py`): exact pooling of
mode-basis errors per band family and of the ring couplings, line 1's size bound, and line 2's power law with its bootstrap interval.

Pooling works on sums of squares, so a pooled rms is exact over molecules of different sizes. The ring-coupling ratio is E6.readout's
`coupling_ratio` (rms of the ring family's off-diagonal error over the rms of its true couplings), pooled the same way.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

FAMILIES = ("CH-stretch", "CH-oop", "ring-ip", "other")       # learning_curve_layerA.FAMILIES; a test keeps the two equal
RING = "ring-ip"
LINE_1_MIN_ATOMS, LINE_1_MIN_MOLECULES = 25, 30
LINE_2_AT_ATOMS = 60
BOOTSTRAP, BOOTSTRAP_SEED = 1000, 0


@dataclass(frozen=True)
class FitRule:
    """Which molecules enter line 2's power law: at least `min_atoms` atoms and a value of at least `min_value` (exact zeros never enter)."""
    name: str
    min_atoms: int
    min_value: float


SIZE_BINS = ((0, 14), (15, 19), (20, 23), (24, 27), (28, 33), (34, 45), (46, 99))   # atoms; 34+ for lever 5's large PAHs

ORIGINAL = FitRule("original", 10, 0.0)          # as registered 15 Oct 19:0x / 19:4x; took numerically-zero floors — its forecasts are invalid
AMENDED = FitRule("amended", 15, 1e-6)           # the amendment of 15 Oct 21:2x, fixed before lever 5's large-PAH re-read
RULES = {r.name: r for r in (ORIGINAL, AMENDED)}


def error_sums(K_true: np.ndarray, K_fit: np.ndarray, families: list[str]) -> dict:
    """Per family [sum of squared diagonal errors, modes]; "ring_coupling": [sum of squared off-diagonal errors, sum of squared true couplings]
    over the ring family's upper triangle."""
    fam = np.asarray(families)
    err = K_fit - K_true
    out = {F: [float(np.sum(np.diag(err)[fam == F] ** 2)), int(np.sum(fam == F))] for F in FAMILIES}
    r = np.flatnonzero(fam == RING)
    iu = np.triu_indices(len(r), 1)
    out["ring_coupling"] = [float(np.sum(err[np.ix_(r, r)][iu] ** 2)), float(np.sum(K_true[np.ix_(r, r)][iu] ** 2))]
    return out


def pooled(sums: list[dict], key: str) -> float:
    """A family's pooled diagonal rms, or (key "ring_coupling") the pooled ring-coupling ratio; nan when nothing is pooled."""
    num = sum(s[key][0] for s in sums)
    den = sum(s[key][1] for s in sums)
    return float(np.sqrt(num / den)) if den else float("nan")


def per_molecule(s: dict, key: str) -> float | None:
    """One molecule's value of a read-out, None when it has nothing of it (no modes of the family, no ring couplings) or it is exactly zero,
    which a log–log fit cannot take."""
    num, den = s[key]
    return float(np.sqrt(num / den)) if den and num > 0 else None


def line_1_bound(n_atoms: list[int]) -> int:
    """≥ LINE_1_MIN_ATOMS atoms, lowered one atom at a time until at least LINE_1_MIN_MOLECULES molecules are in (registered)."""
    bound = LINE_1_MIN_ATOMS
    while bound > 0 and sum(n >= bound for n in n_atoms) < LINE_1_MIN_MOLECULES:
        bound -= 1
    return bound


def power_law_at(n_atoms: np.ndarray, values: np.ndarray, at: float) -> float:
    """Least squares in log–log, evaluated at `at` atoms."""
    slope, icpt = np.polyfit(np.log(n_atoms), np.log(values), 1)
    return float(np.exp(icpt + slope * np.log(at)))


def bootstrap_interval(n_atoms: np.ndarray, values: np.ndarray, at: float, rng: np.random.Generator) -> list[float]:
    """The 2.5 and 97.5 percentiles of the power law's value at `at` over BOOTSTRAP resamples of the molecules."""
    draws = []
    for _ in range(BOOTSTRAP):
        idx = rng.integers(0, len(n_atoms), len(n_atoms))
        draws.append(power_law_at(n_atoms[idx], values[idx], at))
    return [float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))]


def forecast(points: list[tuple[int, float]], rng: np.random.Generator, rule: FitRule = ORIGINAL) -> tuple[float, list[float] | None, int]:
    """(value at LINE_2_AT_ATOMS, bootstrap interval, molecules fitted) from the (atoms, value) points the rule admits; nan and None with fewer
    than three points."""
    kept = [(n, v) for n, v in points if n >= rule.min_atoms and v >= rule.min_value]
    if len(kept) < 3:
        return float("nan"), None, len(kept)
    n, v = (np.asarray(x, dtype=float) for x in zip(*kept, strict=True))
    return power_law_at(n, v, LINE_2_AT_ATOMS), bootstrap_interval(n, v, LINE_2_AT_ATOMS, rng), len(kept)


def binned_forecast(items: list[tuple[int, list[float]]], rule: FitRule = ORIGINAL, at: float = LINE_2_AT_ATOMS) -> float:
    """A forecast from pooled size bins (amendment 2, 15 Oct 2026): `items` are (atoms, [num, den]) per molecule; each bin of SIZE_BINS is
    pooled exactly and placed at its molecules' mean atom count; a log–log line through the bins with a non-zero value is evaluated at `at`.
    Per-molecule values spread over orders of magnitude within a narrow size range, which made the per-molecule fit unstable; a bin is not.
    Only the molecules the rule admits are binned (atoms and value), so an exact-fit regime does not set the slope.
    nan with fewer than three such bins."""
    pts = []
    admitted = [(n, s) for n, s in items if n >= rule.min_atoms and s[1] and np.sqrt(s[0] / s[1]) >= rule.min_value]
    for lo, hi in SIZE_BINS:
        inside = [(n, s) for n, s in admitted if lo <= n <= hi]
        value = pooled([{"x": s} for _, s in inside], "x") if inside else float("nan")
        if inside and np.isfinite(value) and value > 0:
            pts.append((float(np.mean([n for n, _ in inside])), value))
    if len(pts) < 3:
        return float("nan")
    n, v = (np.asarray(x, dtype=float) for x in zip(*pts, strict=True))
    return power_law_at(n, v, at)
