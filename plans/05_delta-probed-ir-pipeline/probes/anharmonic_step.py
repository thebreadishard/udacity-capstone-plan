"""The anharmonic step of a band position, ν = ω + Δ_anh (TASKS 211; PreRegistration_2026-11-14_Printed_Band_Position.md and the two
design decisions of 16 Nov 2026 in probes/results_m1/anharmonic_design_questions_2026-11-16/REPORT.md).

Δ_anh is the registered model x2*: kernel ridge on FX — family, ω, the hydrogen share h, the out-of-plane share o and the shift of
the matched GFN2-xTB mode — at the configuration S2b's nested read chose per family. Nothing is fitted or described here a second
time: the modes are described by `s2_read.mode_description`, matched to the xtb modes by `s2_xtb_read.attach_xtb`, and the shift is
`s3_read.predictors(<config>)["x2*"](<training table>, <the molecule's modes>)`, the very call the registered read made.

The artefact (`probes/anharmonic_step_fit.py` writes it; the design note of 14 Nov, section 5) is the pooled training table of
each reading window beside each family's configuration and its measured error bar. A table that names no read, no commit or no
training molecule is refused.

Three functions, none of which reads a file it was not handed:
- `load_artefact`: the artefact as a checked object;
- `mode_steps`: per B3LYP mode the step, or no step with its reason (the label-free rule of 16 Nov: a large-amplitude mode, a mode
  without an xtb partner, a mode whose xtb partner is outside VPT2's domain; and a mode in a family and range nothing was measured in),
  the family's bar, and whether the bar was measured for this kind of mode (family 'other' with o ≥ 0.8: it was not);
- `carry_to_bands`: the steps carried to the corrected bands by mode overlap, one B3LYP mode per band, never by rank; a band whose
  partner overlaps below 0.5 gets no step.
"""
from __future__ import annotations

import json
import math
import os
import sys
from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "src"))
from s1_anharmonic_level import harmonic_modes  # noqa: E402
from s2_read import FAMILIES, XTB_KEY, in_window, load_molecule, mode_description  # noqa: E402
from s2_xtb_read import MIN_OVERLAP, X2_GRID, attach_xtb, match_modes  # noqa: E402
from s3_read import predictors  # noqa: E402

from dpir.qff import MASS, harmonic  # noqa: E402

FORMAT = 1
MODEL = "x2*"
ARTEFACT = os.path.join(HERE, "anharmonic_step", "x2star_v1.json")
TABLE_KEYS = ("omega", "delta", "family", "h", "o", XTB_KEY)      # s2_read.concat's columns, in its order
REQUIRED = ("commit", "registration", "decisions", "scope", "training_molecules", "windows")
NOT_MEASURED_FAMILY = "other"     # decision 2 of 16 Nov: every mode a B3LYP label marked lies in this family with o ≥ 0.83, and only
NOT_MEASURED_O = 0.8              # two of the six are caught without the label; such a band keeps its step and loses its bar's claim

LARGE_AMPLITUDE = "large-amplitude"
NO_XTB_PARTNER = "no-xtb-partner"
XTB_PARTNER_MARKED = "xtb-partner-marked"
UNMEASURED = "unmeasured"
MIXED_BAND = "mixed-band"
NO_FORCE_FIELD = "no-force-field"
MODE_REASONS = (LARGE_AMPLITUDE, NO_XTB_PARTNER, XTB_PARTNER_MARKED)     # the label-free rule, in the order it is asked
REASON_TEXT = {
    LARGE_AMPLITUDE: "a large-amplitude mode (half or more of its hydrogen motion on an sp-carbon, N–H or O–H hydrogen): the model "
                     "was not trained on such modes",
    NO_XTB_PARTNER: f"no GFN2-xTB mode matches this B3LYP mode (overlap below {MIN_OVERLAP}), so the model has no input for it",
    XTB_PARTNER_MARKED: "the matched GFN2-xTB mode is outside perturbation theory's domain, so its shift is not a number the "
                        "theory can state",
    UNMEASURED: "no model was measured for this family in this range",
    MIXED_BAND: f"the corrected band mixes B3LYP modes (its partner overlaps below {MIN_OVERLAP}), so no mode's step is its own",
    NO_FORCE_FIELD: "the molecule has no GFN2-xTB force field",
}
NOT_MEASURED_TEXT = (f"the step's error is not measured for this kind of mode (family '{NOT_MEASURED_FAMILY}' with an out-of-plane "
                     f"share of {NOT_MEASURED_O} or more)")


@dataclass(frozen=True)
class FamilyModel:
    """One family's model in one window: S2b's configuration, the registered bar and the artefact's own reproduction of it."""
    config: str
    bar_cm: float
    bar_refit_cm: float
    n_training_modes: int
    n_target_rows: int


@dataclass(frozen=True)
class WindowModel:
    """A reading window's training table (the window modes of every training molecule) and its families' models."""
    name: str
    bounds: tuple[float, float]
    families: dict[str, FamilyModel]
    table: dict[str, np.ndarray]


@dataclass(frozen=True)
class Artefact:
    """The checked artefact: its windows, and the record's header (the reads, the commit, the training molecules)."""
    windows: tuple[WindowModel, ...]
    header: dict[str, Any]


@dataclass(frozen=True)
class Modes:
    """A molecule's harmonic modes as the training path has them (`dpir.qff.harmonic`): ω in cm⁻¹ ascending, mass-weighted q (3N × M)."""
    symbols: tuple[str, ...]
    coords_bohr: np.ndarray
    omega: np.ndarray
    q: np.ndarray

    @classmethod
    def from_hessian(cls, hessian: np.ndarray, symbols: list[str], coords_bohr: np.ndarray) -> Modes:
        """The modes of a Cartesian Hessian (hartree/bohr²) at its geometry; raises where that is not a minimum with 3N−6 modes."""
        coords = np.asarray(coords_bohr, float).reshape(-1, 3)
        h = harmonic(np.asarray(hessian, float), list(symbols), coords)
        return cls(tuple(symbols), coords, np.asarray(h.omega_cm), np.asarray(h.q))

    @classmethod
    def from_ref(cls, ref_json: str) -> Modes:
        """The modes of a stored reference record (a force field's ref.json), by the reads' own `harmonic_modes`."""
        with open(ref_json, encoding="utf-8") as fh:
            mol = json.load(fh)["molecule"]
        omega, q = harmonic_modes(ref_json)
        return cls(tuple(mol["symbols"]), np.array(mol["geometry"], float).reshape(-1, 3), omega, q)


@dataclass(frozen=True)
class XtbField:
    """A molecule's GFN2-xTB force field as the step reads it: each xtb mode's GVPT2 shift, its VPT2-domain mark, and the modes."""
    delta: np.ndarray
    marked: np.ndarray
    q: np.ndarray

    @classmethod
    def from_folder(cls, x_dir: str, label_file: str) -> XtbField:
        """An X setting folder (ref.json, qff_report.npz) with its probes/gvpt2_labels.py file, through `s2_read.load_molecule`."""
        rec, why = load_molecule(x_dir, label_file)
        if rec is None:
            raise ValueError(f"{x_dir}: {why}")
        if not rec["vpt2_checked"]:
            raise ValueError(f"{label_file}: the label predates the VPT2-domain check; relabel with probes/gvpt2_labels.py")
        return cls(np.asarray(rec["delta"], float), np.asarray(rec["vpt2_marked"], bool), harmonic_modes(os.path.join(x_dir, "ref.json"))[1])


@dataclass(frozen=True)
class ModeStep:
    """One B3LYP mode's step: Δ_anh with the family's bar, or None with the reason; `error_not_measured` says the bar is not this mode's."""
    mode: int
    omega_cm: float
    family: str
    h: float
    o: float
    xtb_overlap: float
    delta_anh_cm: float | None
    reason: str | None
    bar_cm: float | None
    error_not_measured: bool
    window: str | None

    def as_record(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BandStep:
    """A corrected band's step: its B3LYP partner (None below the overlap line), that overlap, and what the partner carries."""
    mode: int | None
    overlap: float
    delta_anh_cm: float | None
    reason: str | None
    bar_cm: float | None
    error_not_measured: bool

    def as_record(self) -> dict[str, Any]:
        return asdict(self)


def _window(name: str, raw: dict[str, Any]) -> WindowModel:
    """One window of the artefact's record, checked: equal-length columns, known configurations, every modelled family in the table."""
    table = {k: np.asarray(raw["table"][k], str if k == "family" else float) for k in TABLE_KEYS}
    if len({len(v) for v in table.values()}) != 1 or not len(table["omega"]):
        raise ValueError(f"window {name}: the training table's columns are empty or differ in length")
    lo, hi = raw["window"]
    families = {fa: FamilyModel(**m) for fa, m in raw["families"].items()}
    known = {c.name for c in X2_GRID}
    for fa, m in families.items():
        if fa not in FAMILIES or m.config not in known:
            raise ValueError(f"window {name}: family {fa!r} with configuration {m.config!r} is not one of the read's")
        if int((table["family"] == fa).sum()) != m.n_training_modes or not m.n_training_modes:
            raise ValueError(f"window {name}: the table holds {int((table['family'] == fa).sum())} {fa} modes, the record says "
                             f"{m.n_training_modes}")
    return WindowModel(name, (float(lo), math.inf if hi is None else float(hi)), families, table)


def load_artefact(path: str = ARTEFACT) -> Artefact:
    """The artefact as a checked object. Refused: another format or model, a header that does not name the reads, the commit and the
    training molecules it came from, and two windows that hold the same family (a mode would have two steps)."""
    with open(path, encoding="utf-8") as fh:
        raw = json.load(fh)
    if raw.get("format") != FORMAT or raw.get("model") != MODEL:
        raise ValueError(f"{path}: format {raw.get('format')!r}, model {raw.get('model')!r}; this code reads format {FORMAT} of {MODEL}")
    missing = [k for k in REQUIRED if not raw.get(k)]
    untraced = [n for n, w in raw.get("windows", {}).items() if not all(w.get(k) for k in ("s2b_read", "s3_read", "route_rule"))]
    if missing or untraced:
        raise ValueError(f"{path}: cannot be traced to a read — missing {missing}, windows without their reads {untraced}")
    windows = tuple(_window(n, w) for n, w in raw["windows"].items())
    seen = [fa for w in windows for fa in w.families]
    if len(set(seen)) != len(seen):
        raise ValueError(f"{path}: a family has a model in two windows: {sorted(seen)}")
    return Artefact(windows, {k: v for k, v in raw.items() if k != "windows"}
                    | {"window_sources": {n: {k: v for k, v in w.items() if k != "table"} for n, w in raw["windows"].items()}})


def bars(artefact: Artefact) -> dict[str, float]:
    """Each modelled family's registered error bar in cm⁻¹, as the certificate prints it."""
    return {fa: m.bar_cm for w in artefact.windows for fa, m in w.families.items()}


def describe(modes: Modes, xtb: XtbField) -> dict[str, np.ndarray]:
    """The molecule's B3LYP modes as a read's record with their xtb partners (`attach_xtb`). The molecule has no B3LYP label, so no
    mode carries a mark of its own: the mark is its xtb partner's."""
    n = len(modes.omega)
    masses = np.array([MASS[s] for s in modes.symbols])
    rec = {"omega": modes.omega, "delta": np.zeros(n), **mode_description(modes.omega, modes.q, list(modes.symbols), modes.coords_bohr, masses),
           "vpt2_marked": np.zeros(n, bool), "vpt2_checked": True}
    return attach_xtb(rec, {"delta": xtb.delta, "vpt2_marked": xtb.marked, "vpt2_checked": True}, modes.q, xtb.q)


def predict_window(rec: dict[str, np.ndarray], usable: np.ndarray, window: WindowModel) -> tuple[np.ndarray, np.ndarray]:
    """x2*'s shift for the usable modes of one window (nan elsewhere), each family at its own configuration, and each mode's bar."""
    delta, bar = np.full(len(usable), np.nan), np.full(len(usable), np.nan)
    at = np.flatnonzero(usable & in_window(rec["omega"], window.bounds))
    if not len(at):
        return delta, bar
    test = {k: rec[k][at] for k in TABLE_KEYS}
    for fa, model in window.families.items():
        sel = test["family"] == fa
        if sel.any():
            delta[at[sel]] = np.asarray(predictors(model.config)[MODEL](window.table, test), float)[sel]
            bar[at[sel]] = model.bar_cm
    return delta, bar


def mode_steps(modes: Modes, xtb: XtbField, artefact: Artefact) -> list[ModeStep]:
    """Per B3LYP mode, in the modes' order: the step with its family's bar, or no step with the reason."""
    rec = describe(modes, xtb)
    n = len(modes.omega)
    reason = np.full(n, None, object)
    for code, flag in zip(MODE_REASONS, (rec["large_amplitude"], rec["no_xtb"], rec["vpt2_marked"]), strict=True):
        reason[(reason == None) & flag] = code  # noqa: E711  an object array is compared element by element
    usable = reason == None  # noqa: E711
    delta, bar, name = np.full(n, np.nan), np.full(n, np.nan), np.full(n, None, object)
    for w in artefact.windows:
        d, b = predict_window(rec, usable, w)
        got = np.isfinite(d)
        delta[got], bar[got], name[got] = d[got], b[got], w.name
    reason[usable & ~np.isfinite(delta)] = UNMEASURED
    out = []
    for i in range(n):
        stepped = reason[i] is None
        out.append(ModeStep(mode=i, omega_cm=float(rec["omega"][i]), family=str(rec["family"][i]), h=float(rec["h"][i]),
                            o=float(rec["o"][i]), xtb_overlap=float(rec["xtb_overlap"][i]),
                            delta_anh_cm=float(delta[i]) if stepped else None, reason=reason[i],
                            bar_cm=float(bar[i]) if stepped else None,
                            error_not_measured=bool(stepped and rec["family"][i] == NOT_MEASURED_FAMILY and rec["o"][i] >= NOT_MEASURED_O),
                            window=name[i]))
    return out


def carry_to_bands(q_bands: np.ndarray, q_modes: np.ndarray, steps: list[ModeStep], min_overlap: float = MIN_OVERLAP) -> list[BandStep]:
    """Each corrected band's step: that of the B3LYP mode the one-to-one assignment of largest total squared overlap gives it
    (`s2_xtb_read.match_modes`, the match the training used), whatever the two modes' ranks. Below `min_overlap` the band is no
    B3LYP mode's and gets no step."""
    if len(steps) != q_modes.shape[1]:
        raise ValueError(f"{len(steps)} steps for {q_modes.shape[1]} B3LYP modes")
    partner, overlap = match_modes(q_bands, q_modes, min_overlap)
    out = []
    for k, ov in zip(partner, overlap, strict=True):
        if k < 0:
            out.append(BandStep(None, float(ov), None, MIXED_BAND, None, False))
        else:
            s = steps[int(k)]
            out.append(BandStep(int(k), float(ov), s.delta_anh_cm, s.reason, s.bar_cm, s.error_not_measured))
    return out
