"""The read of the ANO test on benzene (TASKS 300): which target of the composite's MP2 step brings the reference Hessian to the published
CCSD(T)/ano-pV5Z harmonics (Semidalas & Martin 2023, Table 5). Everything it decides was fixed beforehand in
GoalGathering/notes/PreRegistration_2026-11-25_ANO_Step_Benzene.md (with amendments 1 and 2); this script chooses nothing.

Per recipe the composite is H = CCSD(T)/cc-pVDZ + (target − DF-MP2/cc-pVDZ), the target built from the row files of
probes/ano_step_benzene.sh. Each composite is corrected to the higher level's minimum by the first-order geometry term
Δω_i = ½ Σ_k φ_iik Δq_k: the Newton step from the stored CCSD(T)/cc-pVTZ gradient and the Hessian being corrected, the B3LYP cubic
constants of level G (the functions of probes/geometry_term_check.py). A mode is named from its own vector — in or out of the plane,
parity under inversion, character under C6 — and matched within a symmetry species by order; a degenerate pair counts once.

The conventional-MP2 composite of 7 October is rebuilt first and must repeat the 7.6 / 30.2 / 8.9 cm⁻¹ of 25 November
(results_m1/supervisor_chat_2026-11-25/benzene_geometry_term.txt): the check that this script reads as that one did.

    python probes/ano_step_read.py <run dir with rows_<label>.npz> <out prefix> [--partial]

Writes <out prefix>.md and .json. Without --partial every row file of every recipe must be there.
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
sys.path.insert(0, str(PLAN / "src"))
import cc_composite_full_check as CCF  # noqa: E402
import dfmp2_rows as D  # noqa: E402
import geometry_term_check as GT  # noqa: E402
from s1_anharmonic_level import newton_step  # noqa: E402

from dpir.qff import Harmonic, harmonic  # noqa: E402
from dpir.symmetry import Operation, point_group_ops  # noqa: E402

M05 = PLAN / "modules" / "05_support_predictor"
R1 = PLAN / "probes" / "results_m1"

# CCSD(T)/ano-pV5Z harmonics of benzene, cm⁻¹ (Semidalas & Martin, Mol. Phys. 2023, doi 10.1080/00268976.2023.2263593, Table 5)
REF = {"ω1": ("a1g", 1006.6), "ω2": ("a1g", 3204.3), "ω3": ("a2g", 1380.5), "ω4": ("b2g", 712.4), "ω5": ("b2g", 1012.4),
       "ω6": ("e2g", 611.5), "ω7": ("e2g", 3179.6), "ω8": ("e2g", 1639.3), "ω9": ("e2g", 1191.8), "ω10": ("e1g", 863.4),
       "ω11": ("a2u", 683.6), "ω12": ("b1u", 1024.6), "ω13": ("b1u", 3169.9), "ω14": ("b2u", 1328.6), "ω15": ("b2u", 1158.4),
       "ω16": ("e2u", 406.3), "ω17": ("e2u", 987.0), "ω18": ("e1u", 1057.2), "ω19": ("e1u", 1511.3), "ω20": ("e1u", 3195.1)}
# CCSD(T)/ANO4321′ (Martin, Taylor & Lee 1997), printed beside the reference by amendment 1; the lines stay on ano-pV5Z
MTL_1997 = {"ω4": 708.8, "ω5": 1008.8, "ω10": 865.1, "ω11": 687.2, "ω16": 405.8}
# a species as (out of plane, even under inversion, 2 × character under C6)
KEY = {"a1g": (False, True, 2), "a2g": (False, True, 2), "b1u": (False, False, -2), "b2u": (False, False, -2), "e2g": (False, True, -1),
       "e1u": (False, False, 1), "b2g": (True, True, -2), "a2u": (True, False, 2), "e1g": (True, True, 1), "e2u": (True, False, -1)}
OUT_OF_PLANE = {"b2g", "a2u", "e1g", "e2u"}
CH_STRETCH_ABOVE_CM = 3000.0
MODES = sorted(REF, key=lambda name: int(name[1:]))
GROUPS = {"C-H stretch": [m for m in MODES if REF[m][1] > CH_STRETCH_ABOVE_CM],
          "out of plane": [m for m in MODES if REF[m][0] in OUT_OF_PLANE],
          "other in plane": [m for m in MODES if REF[m][1] <= CH_STRETCH_ABOVE_CM and REF[m][0] not in OUT_OF_PLANE]}

# the registered lines, cm⁻¹
PASS_LINE = 2.0                 # every group at or under
USEFUL_OOP_LINE = 10.0          # the out-of-plane group at or under
USEFUL_OTHER_MARGIN = 1.0       # and neither other group more than this above the control's
GAIN_LINE = 5.0                 # NO GAIN: no recipe lowers the out-of-plane group by this much below the control
CONTROL_LINE = 0.5              # the DF-MP2 control against the conventional composite, per group
FITTING_LINE = 1e-6             # E_h/bohr²: an ANO set's row with cc-pV5Z fitting sets against the same row with cc-pVQZ's
DIAGNOSTIC_LINE = 5.0           # [CCSD(T) − MP2] may change by this between cc-pVDZ and cc-pVTZ
DIAGNOSTIC_MODES = ("ω4", "ω5", "ω17")
CONVENTIONAL_PINS = {"C-H stretch": 7.6, "out of plane": 30.2, "other in plane": 8.9}   # 25 Nov, to one decimal
PIN_TOLERANCE = 0.051
MAX_STEP_BOHR = 0.05            # the first-order term is not read beyond this Newton step (25 Nov: 0.0062 bohr)
MAP_LINE_BOHR = 0.005           # corpus geometry onto the force field's (25 Nov: 0.0003 bohr)
CONTROL, STEP_FROM = "1", "mp2_ccpvdz"
N_FROZEN = 6
KIND = {"mp2": "DF-MP2", "scf": "DF-SCF"}
FIT_SUFFIX = "_fit5z"


@dataclass(frozen=True)
class RowLevel:
    """What a label's row file must hold, as the lane (probes/ano_step_benzene.sh) and the registration fix it."""
    basis: str
    theory: str
    scf_fit: str
    mp2_fit: str | None = None
    frozen: int = N_FROZEN

    def level_text(self) -> str:
        """The level as dfmp2_rows.method_text writes it behind the psi4 version."""
        return f"({self.scf_fit})" if self.theory == "scf" else f"({self.scf_fit} / {self.mp2_fit}, frozen {self.frozen})"

    def five_zeta(self) -> RowLevel:
        """The same rows with cc-pV5Z fitting sets: the fitting check."""
        return replace(self, scf_fit="cc-pv5z-jkfit", mp2_fit="cc-pv5z-ri")


EXPECTED = {"mp2_ccpvdz": RowLevel("cc-pvdz", "mp2", "cc-pvdz-jkfit", "cc-pvdz-ri"),
            "mp2_ccpvtz": RowLevel("cc-pvtz", "mp2", "cc-pvtz-jkfit", "cc-pvtz-ri"),
            "mp2_ccpvqz": RowLevel("cc-pvqz", "mp2", "cc-pvqz-jkfit", "cc-pvqz-ri"),
            "mp2_roosanotz": RowLevel("roos-ano-tz", "mp2", "cc-pvqz-jkfit", "cc-pvqz-ri"),
            "mp2_anopvqz": RowLevel("ano-pvqz", "mp2", "cc-pvqz-jkfit", "cc-pvqz-ri"),
            "scf_ccpvtz": RowLevel("cc-pvtz", "scf", "cc-pvtz-jkfit"),
            "scf_ccpvqz": RowLevel("cc-pvqz", "scf", "cc-pvqz-jkfit"),
            "mp2_ccpwcvtz_fc": RowLevel("cc-pwcvtz", "mp2", "cc-pvtz-jkfit", "cc-pwcvtz-ri"),
            "mp2_ccpwcvtz_ae": RowLevel("cc-pwcvtz", "mp2", "cc-pvtz-jkfit", "cc-pwcvtz-ri", frozen=0)}
FITTING_CHECKED = ("mp2_anopvqz", "mp2_roosanotz")


class Unreadable(Exception):
    """A Hessian the geometry term or the naming of modes cannot be applied to; the reason is the message."""


def basis_limit(M: dict[str, np.ndarray]) -> np.ndarray:
    """Recipe 6's target (amendment 2): Hartree–Fock at cc-pVQZ plus the MP2 correlation part extrapolated by n⁻³ from n = 3 and 4."""
    corr_tz, corr_qz = M["mp2_ccpvtz"] - M["scf_ccpvtz"], M["mp2_ccpvqz"] - M["scf_ccpvqz"]
    return M["scf_ccpvqz"] + (64.0 * corr_qz - 27.0 * corr_tz) / 37.0


def with_core_valence(M: dict[str, np.ndarray]) -> np.ndarray:
    """Recipe 7's target: recipe 6 plus [MP2(all electrons) − MP2(frozen 1s)] in cc-pwCVTZ."""
    return basis_limit(M) + M["mp2_ccpwcvtz_ae"] - M["mp2_ccpwcvtz_fc"]


@dataclass(frozen=True)
class Recipe:
    name: str
    labels: tuple[str, ...]
    target: Callable[[dict[str, np.ndarray]], np.ndarray]


_LIMIT = ("mp2_ccpvtz", "scf_ccpvtz", "mp2_ccpvqz", "scf_ccpvqz")
RECIPES = {"1": Recipe("cc-pVTZ, DF-MP2 (control)", ("mp2_ccpvtz",), lambda M: M["mp2_ccpvtz"]),
           "2": Recipe("cc-pVQZ", ("mp2_ccpvqz",), lambda M: M["mp2_ccpvqz"]),
           "3": Recipe("roos-ano-tz as psi4 ships it (414 functions)", ("mp2_roosanotz",), lambda M: M["mp2_roosanotz"]),
           "5": Recipe("ano-pVQZ", ("mp2_anopvqz",), lambda M: M["mp2_anopvqz"]),
           "6": Recipe("MP2 basis-set limit from cc-pVTZ and cc-pVQZ", _LIMIT, basis_limit),
           "7": Recipe("recipe 6 + MP2 core-valence (cc-pwCVTZ)", (*_LIMIT, "mp2_ccpwcvtz_fc", "mp2_ccpwcvtz_ae"), with_core_valence)}


@dataclass(frozen=True)
class Inputs:
    """What the read takes from earlier work: benzene's force field (level G), corpus record, CC Hessians and conventional MP2 rows."""
    force_field: Path = R1 / "routea_2026-11-02" / "gate" / "benzene" / "G"
    corpus: Path = M05 / "corpus" / "molecules" / "A_8448043181"
    cc_dz: Path = R1 / "e8_benzene_ccpvdz_dip_2026-10-03" / "hessian_ccsd_t.npz"
    cc_tz: Path = R1 / "e8_benzene_ccpvtz_oop_2026-10-03" / "hessian_ccsd_t.npz"
    mp2_dz_conventional: Path = R1 / "composite_mp2_rows_benzene_ccpvdz_2026-10-04.npz"
    mp2_tz_conventional: Path = R1 / "composite_mp2_rows_benzene_ccpvtz_2026-10-04.npz"


# ---------------------------------------------------------------- the frame of the force field, and a mode's name

def _ring(x: np.ndarray, idx: list[int]) -> list[int]:
    """The carbons in order around the ring."""
    normal = np.linalg.svd(x)[2][-1]
    u = x[idx[0]] / np.linalg.norm(x[idx[0]])
    v = np.cross(normal, u)
    return sorted(idx, key=lambda i: np.arctan2(x[i] @ v, x[i] @ u))


def rigid_map(sym_a: list[str], xa: np.ndarray, sym_b: list[str], xb: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    """An orthogonal R and a permutation p with R (xa_i − centre) ≈ xb_p[i] − centre for same elements: Kabsch on the carbon ring for
    every start and direction of the ring, the hydrogens placed by nearest position; the best is returned with its largest atom
    distance (bohr)."""
    a, b = xa - xa.mean(0), xb - xb.mean(0)
    ra, rb = _ring(a, [i for i, s in enumerate(sym_a) if s == "C"]), _ring(b, [i for i, s in enumerate(sym_b) if s == "C"])
    best = None
    for shift, step in itertools.product(range(len(rb)), (1, -1)):
        target = [rb[(shift + step * k) % len(rb)] for k in range(len(rb))]
        U, _, Vt = np.linalg.svd(a[ra].T @ b[target])
        R = (U @ Vt).T                                   # orthogonal, proper or improper: either carries a Hessian correctly
        moved = a @ R.T
        perm = np.empty(len(sym_a), int)
        for i, s in enumerate(sym_a):
            same = [j for j, t in enumerate(sym_b) if t == s]
            perm[i] = same[int(np.argmin([np.linalg.norm(moved[i] - b[j]) for j in same]))]
        if len(set(perm.tolist())) != len(perm):
            continue
        worst = float(np.linalg.norm(moved - b[perm], axis=1).max())
        if best is None or worst < best[2]:
            best = (R, perm, worst)
    if best is None:
        raise SystemExit("no rigid map between the two geometries")
    return best


def carried(H: np.ndarray, R: np.ndarray, perm: np.ndarray) -> np.ndarray:
    """A Cartesian Hessian in the frame the rigid map leads to."""
    n = len(perm)
    blocks = np.einsum("ac,ikcd,bd->ikab", R, H.reshape(n, 3, n, 3).transpose(0, 2, 1, 3), R)
    out = np.zeros_like(blocks)
    out[np.ix_(perm, perm)] = blocks
    return out.transpose(0, 2, 1, 3).reshape(3 * n, 3 * n)


def species(q: np.ndarray, x: np.ndarray, ops: list[Operation]) -> list[tuple[bool, bool, int]]:
    """Per mode (mass-weighted columns of q): (out of plane, even under inversion, 2 × character under C6, rounded). Equivalent atoms
    have equal masses, so the characters of the mass-weighted vector are the mode's."""
    normal = np.linalg.svd(x - x.mean(0))[2][-1]
    inversion = next(o for o in ops if abs(np.trace(o[0]) + 3) < 1e-3)
    c6 = next(o for o in ops if np.linalg.det(o[0]) > 0 and abs(np.trace(o[0]) - 2) < 1e-3)

    def character(v: np.ndarray, op: Operation) -> float:
        moved = np.zeros_like(v)
        moved[np.array(op[1])] = v @ op[0].T
        return float(np.sum(v * moved))

    out = []
    for k in range(q.shape[1]):
        v = q[:, k].reshape(-1, 3)
        out.append((bool(np.sum((v @ normal) ** 2) > 0.5), character(v, inversion) > 0, round(2 * character(v, c6))))
    return out


def named(freq: np.ndarray, keys: list[tuple[bool, bool, int]]) -> dict[str, float]:
    """Wilson name → frequency: within a species key by order, a degenerate pair averaged. a1g and a2g share a key, as do b1u and
    b2u (the three characters do not tell them apart): those are matched by order across the two, which benzene's spacing carries
    (the nearest two are over 100 cm⁻¹ apart)."""
    groups: dict[tuple, list[float]] = defaultdict(list)
    for f, k in zip(freq, keys, strict=True):
        groups[k].append(float(f))
    out = {}
    for key in set(KEY.values()):
        values = sorted(groups[key])
        if abs(key[2]) == 1:
            values = [float(np.mean(values[i:i + 2])) for i in range(0, len(values), 2)]
        refs = sorted((r, name) for name, (s, r) in REF.items() if KEY[s] == key)
        if len(values) != len(refs):
            raise Unreadable(f"species {key}: {len(values)} modes of ours, {len(refs)} in the reference")
        out.update({name: f for f, (_, name) in zip(values, refs, strict=True)})
    return out


@dataclass(frozen=True)
class Frame:
    """The force field's frame: its geometry and modes, the cubic constants φ_iik, each mode's species, the map from the corpus
    geometry into it and the CCSD(T)/cc-pVTZ gradient carried along."""
    sym: list[str]
    x: np.ndarray
    h: Harmonic
    cubic: np.ndarray
    ops: list[Operation]
    keys: list[tuple[bool, bool, int]]
    R: np.ndarray
    perm: np.ndarray
    gradient: np.ndarray
    map_worst_bohr: float


def load_frame(inputs: Inputs) -> tuple[Frame, list[str], np.ndarray]:
    """The frame, with the corpus symbols and coordinates the row files must be at. Refuses a force field whose reference Hessian does
    not give its own frequencies, and a corpus geometry that does not lie on the force field's."""
    sym, x_g, H_g = GT.read_reference(inputs.force_field)
    sym, x_g = [s.capitalize() for s in sym], np.asarray(x_g, float)
    with np.load(inputs.force_field / "qff_report.npz") as z:
        omega_ff, phi = z["omega_cm"], z["phi_ijk"]
    h = harmonic(H_g, sym, x_g)
    if np.abs(h.omega_cm - omega_ff).max() > GT.OMEGA_CHECK_CM:
        raise SystemExit("the force field's reference Hessian does not give the force field's frequencies")
    sym_c, x_c, _ = CCF.load_geometry(inputs.corpus / "geometry.json")
    R, perm, worst = rigid_map(sym_c, x_c, sym, x_g)
    if worst > MAP_LINE_BOHR:
        raise SystemExit(f"corpus geometry against the force field's: largest atom distance {worst:.4f} bohr, line {MAP_LINE_BOHR}")
    with np.load(inputs.cc_tz, allow_pickle=True) as z:
        gradient = np.zeros((len(sym), 3))
        gradient[perm] = np.asarray(z["gradient"], float).reshape(-1, 3) @ R.T
    ops = point_group_ops(sym, x_g)
    return Frame(sym, x_g, h, np.einsum("iik->ik", phi), ops, species(h.q, x_g, ops), R, perm, gradient, worst), sym_c, x_c


def own_modes(frame: Frame, H_corpus: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    """(frequencies in the order of the force field's modes, the Hessian in the frame, the smallest overlap² of the pairing). Refuses
    a Hessian with an imaginary mode and one whose modes do not pair with the force field's inside their own species."""
    H = carried(H_corpus, frame.R, frame.perm)
    try:
        w, q = GT.modes_at_target(H, frame.sym, frame.x, "benzene")
    except SystemExit as stop:                 # geometry_term_check stops its own run this way; an imaginary mode is one recipe's reason
        if "imaginary" not in str(stop):
            raise
        raise Unreadable(str(stop)) from stop
    order, overlap = GT.paired(frame.h.q, q)
    if species(q[:, order], frame.x, frame.ops) != frame.keys:
        raise Unreadable("its modes do not pair with the force field's inside their own symmetry species")
    return w[order], H, overlap


@dataclass(frozen=True)
class Reading:
    """A Hessian's named frequencies as computed and corrected, its Newton step (largest atom displacement) and pairing overlap²."""
    raw: dict[str, float]
    corrected: dict[str, float]
    step_bohr: float
    overlap: float


def reading(frame: Frame, H_corpus: np.ndarray) -> Reading:
    """A Hessian's named frequencies as computed and with the first-order geometry term."""
    raw, H, overlap = own_modes(frame, H_corpus)
    dx = newton_step(frame.x, frame.gradient, H)
    largest = float(np.linalg.norm(dx.reshape(-1, 3), axis=1).max())
    if not largest <= MAX_STEP_BOHR:
        raise Unreadable(f"Newton step of {largest:.4f} bohr, beyond the {MAX_STEP_BOHR} the first-order term is read for")
    shift = 0.5 * frame.cubic @ GT.reduced(frame.h, dx)
    return Reading(named(raw, frame.keys), named(raw + shift, frame.keys), largest, overlap)


def group_rms(values: dict[str, float]) -> dict[str, float]:
    """rms of (ours − ano-pV5Z) per registered group, each distinct mode once."""
    return {g: float(np.sqrt(np.mean([(values[m] - REF[m][1]) ** 2 for m in modes]))) for g, modes in GROUPS.items()}


# ---------------------------------------------------------------- the row files

def row_path(run: Path, label: str) -> Path:
    """The row file the lane writes for a label."""
    return run / f"rows_{label}.npz"


def file_problem(run: Path, label: str) -> str | None:
    """Why a label's rows cannot be read yet, or None. dfmp2_rows.py saves after every row, so a file in the making exists with some
    of its rows; a '_fit5z' file holds the plan's first row and no other."""
    path = row_path(run, label)
    if not path.is_file():
        return f"no row file for {label}"
    with np.load(path) as z:
        ks = [int(k) for k in z["ks"]]
        held = [k for k in ks if f"row_{k:02d}" in z.files]
    wanted = ks[:1] if label.endswith(FIT_SUFFIX) else ks
    return None if held == wanted else f"{path.name} holds rows {held}, the read needs {wanted}"


def check_row_file(path: Path, level: RowLevel) -> None:
    """Refuse a row file that is not what its label says: basis, kind of calculation, fitting sets, frozen orbitals, step, functions."""
    with np.load(path) as z:
        if "method" not in z.files:
            raise SystemExit(f"{path}: no 'method' key — not a row file of dfmp2_rows.py")
        basis, method, step, cart = str(z["basis"]).lower(), str(z["method"]), float(z["step"]), bool(z["cart"])
    kind, _, level_text = D.method_parts(method)
    if (basis, kind, level_text.lower(), step, cart) != (level.basis, KIND[level.theory], level.level_text(), D.ANCHOR_STEP, False):
        raise SystemExit(f"{path}: holds {method} at {basis}, step {step}, cartesian {cart}; expected {KIND[level.theory]} "
                         f"{level.level_text()} at {level.basis}, step {D.ANCHOR_STEP}, spherical")


def hessians(run: Path, labels: list[str], sym: list[str], x0: np.ndarray) -> tuple[dict[str, np.ndarray], dict[str, float]]:
    """label → symmetrised Hessian from its rows, and label → symmetry spread."""
    M, spread = {}, {}
    for label in labels:
        check_row_file(row_path(run, label), EXPECTED[label])
        M[label], _, spread[label] = CCF.rows_in_frame(str(row_path(run, label)), None, sym, x0)
    return M, spread


def fitting_change(run: Path, label: str) -> dict[str, float | bool]:
    """The plan's first row recomputed with cc-pV5Z fitting sets against the same row of the label's own file, E_h/bohr²: the largest
    change of any element, which is judged against the line, and the change of the row's largest element (the registration's wording
    read literally; never the larger of the two)."""
    again = row_path(run, label + FIT_SUFFIX)
    check_row_file(again, EXPECTED[label].five_zeta())
    with np.load(row_path(run, label)) as a, np.load(again) as b:
        name = f"row_{int(b['ks'][0]):02d}"
        ours, theirs = np.asarray(a[name], float), np.asarray(b[name], float)
    change = np.abs(ours - theirs)
    return {"largest_change": float(change.max()), "change_of_largest_element": float(change[np.argmax(np.abs(ours))]),
            "under_line": bool(change.max() < FITTING_LINE)}


def available(run: Path, partial: bool) -> tuple[list[str], dict[str, str]]:
    """(recipes whose row files are all finished, recipe → reason for the others). Without `partial` a missing or unfinished file
    stops the read; the cc-pVDZ rows every recipe steps from stop it always."""
    needs = {key: (STEP_FROM, *r.labels, *(lab + FIT_SUFFIX for lab in r.labels if lab in FITTING_CHECKED)) for key, r in RECIPES.items()}
    problems = {lab: file_problem(run, lab) for lab in sorted({lab for labs in needs.values() for lab in labs})}
    found = [p for p in problems.values() if p]
    if problems[STEP_FROM] or (found and not partial):
        raise SystemExit(f"{run}: " + "; ".join(found) + ("" if partial else " (--partial reads the recipes that are complete, "
                                                         "without an outcome)"))
    absent = {key: "; ".join(problems[lab] for lab in labs if problems[lab]) for key, labs in needs.items()}
    return [key for key, why in absent.items() if not why], {key: why for key, why in absent.items() if why}


# ---------------------------------------------------------------- the registered lines

def control_holds(control: dict[str, float], conventional: dict[str, float]) -> bool:
    """Recipe 1 repeats the conventional-MP2 composite, as read here, within the registered 0.5 cm⁻¹ in every group."""
    return all(abs(control[g] - conventional[g]) <= CONTROL_LINE for g in GROUPS)


def outcome(rms: dict[str, dict[str, float]], unread: dict[str, str]) -> tuple[str, str]:
    """(PASS | USEFUL | NO GAIN | BETWEEN | NO OUTCOME, the sentence) from the corrected rms per recipe and group, compared unrounded.
    The control is not a candidate. A recipe that could not be read forbids NO GAIN and BETWEEN, which speak about every recipe."""
    control = rms[CONTROL]
    others = {k: v for k, v in rms.items() if k != CONTROL}
    passed = [k for k, v in others.items() if all(v[g] <= PASS_LINE for g in GROUPS)]
    useful = [k for k, v in others.items() if v["out of plane"] <= USEFUL_OOP_LINE
              and all(v[g] <= control[g] + USEFUL_OTHER_MARGIN for g in GROUPS if g != "out of plane")]
    left = f"; recipe(s) {', '.join(sorted(unread))} not read" if unread else ""
    if passed:
        return "PASS", f"recipe(s) {', '.join(passed)}: every group at or under {PASS_LINE} cm⁻¹{left}"
    if useful:
        return "USEFUL", (f"recipe(s) {', '.join(useful)}: out of plane at or under {USEFUL_OOP_LINE} cm⁻¹ and no other group more than "
                          f"{USEFUL_OTHER_MARGIN} above the control's; the same test follows on a second molecule before anything is "
                          f"adopted{left}")
    if unread:
        return "NO OUTCOME", f"recipe(s) {', '.join(sorted(unread))} not read, and no recipe that was read reaches USEFUL"
    best = min(v["out of plane"] for v in others.values())
    if control["out of plane"] - best < GAIN_LINE:
        return "NO GAIN", (f"no recipe lowers the out-of-plane group by {GAIN_LINE} cm⁻¹ or more below the control "
                           f"({control['out of plane']:.2f} → best {best:.2f}): MP2 does not carry the basis-set effect on these modes")
    return "BETWEEN", (f"the best recipe lowers the out-of-plane group from {control['out of plane']:.2f} to {best:.2f} cm⁻¹: "
                       "between USEFUL and NO GAIN, reported as measured, no verdict")


def verdict(rms: dict[str, dict[str, float]], conventional: dict[str, float], absent: dict[str, str],
            failed: dict[str, str]) -> tuple[str, str]:
    """The outcome by the registered lines, or why there is none. `absent`: recipes whose row files are missing or unfinished
    (--partial); `failed`: recipes whose Hessian could not be read."""
    if CONTROL not in rms:
        return "NO OUTCOME", f"the control (recipe {CONTROL}) was not read: {(absent | failed)[CONTROL]}"
    if not control_holds(rms[CONTROL], conventional):
        return "CONTROL FAILED", (f"the DF-MP2 control differs from the conventional composite by more than {CONTROL_LINE} cm⁻¹ in a "
                                  "group: no outcome until that is understood")
    if absent:
        return "PARTIAL", f"the rows of recipe(s) {', '.join(sorted(absent))} are missing or unfinished: no outcome"
    if len(rms) == 1:
        return "NO OUTCOME", "no recipe beside the control was read: " + "; ".join(f"{k}: {why}" for k, why in sorted(failed.items()))
    return outcome(rms, failed)


def diagnostic(frame: Frame, cc: dict[str, np.ndarray], mp2: dict[str, np.ndarray]) -> dict[str, dict[str, float]]:
    """Amendment 1: [CCSD(T) − MP2] per registered mode in cc-pVDZ and in cc-pVTZ, as computed (no geometry term), and its change."""
    w = {(level, basis): named(own_modes(frame, H)[0], frame.keys)
         for level, by_basis in (("cc", cc), ("mp2", mp2)) for basis, H in by_basis.items()}
    out = {}
    for mode in DIAGNOSTIC_MODES:
        dz, tz = w["cc", "dz"][mode] - w["mp2", "dz"][mode], w["cc", "tz"][mode] - w["mp2", "tz"][mode]
        out[mode] = {"dz": dz, "tz": tz, "change": tz - dz}
    return out


def caveats(fitting: dict[str, dict], changes: dict[str, dict[str, float]]) -> list[str]:
    """What is said with the outcome whatever it is: a fitting check over its line (reported, not blocking — the registration gives
    the line without a consequence) and the diagnostic when it fires (amendment 1)."""
    out = []
    for label, check in fitting.items():
        if not check["under_line"]:
            recipes = ", ".join(k for k, r in RECIPES.items() if label in r.labels)
            out.append(f"the fitting check of {label} (recipe {recipes}) is over its line of {FITTING_LINE:.0e} E_h/bohr² "
                       f"({check['largest_change']:.1e}): that recipe's numbers stand under this")
    fired = [m for m, d in changes.items() if abs(d["change"]) > DIAGNOSTIC_LINE]
    if fired:
        out.append(f"[CCSD(T) − MP2] changes by more than {DIAGNOSTIC_LINE} cm⁻¹ between cc-pVDZ and cc-pVTZ on {', '.join(fired)}: the "
                   "artefact sits in the coupled-cluster part as well, and no MP2 step can remove it there")
    return out


# ---------------------------------------------------------------- the read

def conventional_parts(inputs: Inputs, sym: list[str], x0: np.ndarray) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray]]:
    """({dz, tz} CCSD(T) Hessians, {dz, tz} conventional MP2 Hessians), all at the corpus geometry."""
    cc = {}
    for basis, path in (("dz", inputs.cc_dz), ("tz", inputs.cc_tz)):
        with np.load(path, allow_pickle=True) as z:
            cc[basis], at = np.asarray(z["H_raw"], float), np.asarray(z["coords_bohr"], float).reshape(-1, 3)
        if np.abs(at - x0).max() > CCF.FRAME_TOL_BOHR:
            raise SystemExit(f"{path}: not at the corpus geometry")
    mp2 = {basis: CCF.rows_in_frame(str(path), None, sym, x0)[0]
           for basis, path in (("dz", inputs.mp2_dz_conventional), ("tz", inputs.mp2_tz_conventional))}
    return cc, mp2


def conventional_reading(frame: Frame, cc: dict[str, np.ndarray], mp2: dict[str, np.ndarray]) -> Reading:
    """The 7 October composite, read here; it must repeat the 25 November numbers or this script does not read as that one did."""
    result = reading(frame, cc["dz"] + mp2["tz"] - mp2["dz"])
    rms = group_rms(result.corrected)
    if any(abs(rms[g] - pin) > PIN_TOLERANCE for g, pin in CONVENTIONAL_PINS.items()):
        raise SystemExit("the conventional composite reads " + " / ".join(f"{rms[g]:.2f}" for g in GROUPS) + " here, "
                         + " / ".join(f"{p}" for p in CONVENTIONAL_PINS.values()) + " on 25 November: the read itself is off")
    return result


def read_recipes(frame: Frame, cc_dz: np.ndarray, M: dict[str, np.ndarray], keys: list[str]) -> tuple[dict[str, Reading], dict[str, str]]:
    """(recipe → reading, recipe → why its Hessian could not be read)."""
    done, failed = {}, {}
    for key in keys:
        try:
            done[key] = reading(frame, cc_dz + RECIPES[key].target(M) - M[STEP_FROM])
        except Unreadable as why:
            failed[key] = str(why)
    return done, failed


def _entry(result: Reading) -> dict:
    """A reading as the record keeps it."""
    return {"rms": group_rms(result.corrected), "raw_rms": group_rms(result.raw), "corrected": result.corrected, "raw": result.raw,
            "step_bohr": result.step_bohr, "overlap": result.overlap}


def read(run: Path, inputs: Inputs, partial: bool) -> dict:
    """The whole record of the read."""
    frame, sym, x0 = load_frame(inputs)
    cc, mp2 = conventional_parts(inputs, sym, x0)
    conventional = _entry(conventional_reading(frame, cc, mp2))
    keys, absent = available(run, partial)
    labels = sorted({STEP_FROM, *(lab for k in keys for lab in RECIPES[k].labels)})
    M, spread = hessians(run, labels, sym, x0)
    done, failed = read_recipes(frame, cc["dz"], M, keys)
    recipes = {k: {"name": RECIPES[k].name, **_entry(r)} for k, r in done.items()}
    fitting = {lab: fitting_change(run, lab) for lab in FITTING_CHECKED if lab in labels}
    changes = diagnostic(frame, cc, mp2)
    word, sentence = verdict({k: r["rms"] for k, r in recipes.items()}, conventional["rms"], absent, failed)
    return {"date": CCF.stamp(), "run": str(run), "map_worst_bohr": frame.map_worst_bohr, "outcome": word,
            "sentence": "; ".join([sentence, *caveats(fitting, changes)]), "conventional": conventional, "recipes": recipes,
            "unread": absent | failed, "spread": spread, "fitting": fitting, "diagnostic": changes,
            "diagnostic_fired": any(abs(d["change"]) > DIAGNOSTIC_LINE for d in changes.values())}


def _table(record: dict) -> list[str]:
    """Per mode the corrected composite minus ano-pV5Z, then the rms per group."""
    cols = [("conventional", record["conventional"]["corrected"]), *((f"recipe {k}", r["corrected"]) for k, r in record["recipes"].items())]
    lines = ["| mode | species | ano-pV5Z | ANO4321′ (1997) | " + " | ".join(name for name, _ in cols) + " |", "|---|---|---|---|" + "---|" * len(cols)]
    for m in MODES:
        s, ref = REF[m]
        old = f"{MTL_1997[m]:.1f}" if m in MTL_1997 else ""
        lines.append(f"| {m} | {s} | {ref:.1f} | {old} | " + " | ".join(f"{v[m] - ref:+.1f}" for _, v in cols) + " |")
    lines += ["", "| rms against ano-pV5Z, corrected (as computed) | " + " | ".join(GROUPS) + " |", "|---|" + "---|" * len(GROUPS)]
    rows = [("conventional composite (7 Oct)", record["conventional"]), *((f"{k}. {r['name']}", r) for k, r in record["recipes"].items())]
    lines += [f"| {name} | " + " | ".join(f"{r['rms'][g]:.2f} ({r['raw_rms'][g]:.2f})" for g in GROUPS) + " |" for name, r in rows]
    return lines


def _checks(record: dict) -> list[str]:
    """The bullets under the tables: what was not read, the control, the steps, the fitting check, the spreads, the diagnostic."""
    lines = [f"- Recipe {k} not read: {why}." for k, why in sorted(record["unread"].items())]
    if CONTROL in record["recipes"]:
        control, conventional = record["recipes"][CONTROL]["rms"], record["conventional"]["rms"]
        lines.append("- Control: DF-MP2 minus conventional MP2 in the cc-pVTZ step, corrected rms per group: "
                     + " / ".join(f"{control[g] - conventional[g]:+.2f}" for g in GROUPS) + f" cm⁻¹ (line {CONTROL_LINE}).")
    lines.append(f"- Newton step, largest atom displacement in bohr (read up to {MAX_STEP_BOHR}), and smallest overlap² of the pairing "
                 f"with the B3LYP modes: conventional {record['conventional']['step_bohr']:.4f}, {record['conventional']['overlap']:.3f}"
                 + "".join(f"; recipe {k} {r['step_bohr']:.4f}, {r['overlap']:.3f}" for k, r in record["recipes"].items()) + ".")
    lines += [f"- Fitting check, {lab}: with cc-pV5Z fitting sets the first row's largest change of any element is {c['largest_change']:.1e} "
              f"E_h/bohr² ({'under' if c['under_line'] else 'NOT under'} the line {FITTING_LINE:.0e}; this is what is judged), the change of "
              f"its largest element {c['change_of_largest_element']:.1e}." for lab, c in record["fitting"].items()]
    lines.append("- Symmetry spread of the rows (a.u.): " + ", ".join(f"{lab} {v:.1e}" for lab, v in record["spread"].items()) + ".")
    lines.append("- Diagnostic [CCSD(T) − MP2], cc-pVDZ → cc-pVTZ (the conventional MP2 Hessians we hold, as computed): "
                 + "; ".join(f"{m} {d['dz']:+.1f} → {d['tz']:+.1f} (change {d['change']:+.1f})" for m, d in record["diagnostic"].items())
                 + f"; line {DIAGNOSTIC_LINE} cm⁻¹, {'crossed' if record['diagnostic_fired'] else 'not crossed'}.")
    return lines


def report(record: dict) -> str:
    """The read as markdown: the table per mode (corrected composite − ano-pV5Z), the rms per group, the checks, the outcome."""
    lines = [f"# ANO test on benzene: the read — {record['date']}", "",
             f"Rows from `{record['run']}`. Registration: `GoalGathering/notes/PreRegistration_2026-11-25_ANO_Step_Benzene.md`. "
             "Columns: corrected composite minus CCSD(T)/ano-pV5Z, cm⁻¹. The lines are compared on unrounded values.", "",
             *_table(record), "", *_checks(record), "", f"**Outcome: {record['outcome']}** — {record['sentence']}."]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("run", type=Path, help="folder with rows_<label>.npz")
    parser.add_argument("out_prefix", help="writes <out_prefix>.md and .json")
    parser.add_argument("--partial", action="store_true", help="read the recipes whose rows are finished; no outcome while one is missing")
    a = parser.parse_args()
    record = read(a.run, Inputs(), a.partial)
    text = report(record)
    CCF.write_text(Path(f"{a.out_prefix}.md"), text)
    CCF.write_text(Path(f"{a.out_prefix}.json"), json.dumps(record, indent=1, ensure_ascii=False))
    sys.stdout.buffer.write(text.encode("utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
