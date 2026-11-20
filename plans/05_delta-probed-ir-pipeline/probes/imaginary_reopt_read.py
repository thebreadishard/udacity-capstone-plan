"""The acceptance read of the imaginary-label re-optimisation (TASKS 215;
GoalGathering/notes/PreRegistration_2026-11-20_Imaginary_Label_Reoptimisation.md, section 5).

Per molecule of the list: the corpus folder (the label that never trains) beside the re-optimised folder
`probes/imaginary_reopt_lane.sh` wrote. A molecule is accepted when all of these hold, and stays out with the first reason otherwise:

1. the optimisation finished (the folder holds geometry.json, which the optimiser writes last and only when geomeTRIC converged);
2. both label files exist, neither is marked `low_mode_pending`, and the APT file exists;
3. no label has an imaginary mode: the lowest projected vibrational frequency of both is above zero (`vibrations.vibrational_modes`,
   the route `probes/low_mode_coverage.py` counts with), and the label route's own counts in result.json are both zero;
4. it is still the same molecule: the atoms are the corpus folder's in its order and the bond graph is unchanged
   (`e8_cc_locality.bond_graph`, bonded below 1.2 times the sum of the covalent radii).

Reported and not deciding: the rms distance from the corpus geometry after a rigid rotation (`frame_match.kabsch`), over all atoms
and over the heavy atoms, and a flag when the heavy-atom distance passes CONFORMER_RMS_BOHR.

    python probes/imaginary_reopt_read.py <corpus molecules dir> <re-optimised dir> --ids FILE --out FOLDER
"""
from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterator
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "modules" / "05_support_predictor" / "corpus"))
from e8_cc_locality import bond_graph
from frame_match import kabsch
from qc_common import write_atomic
from vibrations import LABEL_TAGS, vibrational_modes

CONFORMER_RMS_BOHR = 0.5      # heavy atoms, after rotation: past this the minimum found is another conformer, said beside the verdict
APT_FILE = "dipole_b3lyp_cphf.npz"


@dataclass(frozen=True)
class Reoptimised:
    """What one re-optimised folder holds, as the verdict needs it; a field is None when its file is missing."""

    symbols: list[str] | None
    coords_bohr: np.ndarray | None
    lowest_cm: dict[str, float | None]
    pending: dict[str, bool]
    counts: dict[str, int | None]
    has_apt: bool


@dataclass(frozen=True)
class Verdict:
    """One molecule's line of the read."""

    mol_id: str
    accepted: bool
    reason: str
    lowest_before_cm: dict[str, float]
    lowest_after_cm: dict[str, float | None]
    rms_bohr: float | None
    rms_heavy_bohr: float | None
    conformer_flag: bool
    changed_bonds: list[str]


def _symbols(geometry: dict) -> list[str]:
    return [s.capitalize() for s in geometry["symbols"]]


def lowest_mode_cm(folder: Path, tag: str, geometry: dict) -> tuple[float | None, bool]:
    """(the lowest projected vibrational frequency of one label file, whether the file is marked pending); (None, False) without a file."""
    path = folder / f"hessian_{tag}_analytic.npz"
    if not path.is_file():
        return None, False
    with np.load(path) as z:
        H, pending = np.asarray(z["H_raw"], float), "low_mode_pending" in z.files
    modes = vibrational_modes(H, np.asarray(geometry["masses_amu"], float), np.asarray(geometry["coords_bohr"], float))
    return float(modes.omega_cm[0]), pending


def read_reoptimised(folder: Path) -> Reoptimised:
    """A re-optimised folder as it stands on disk; a folder the lane never finished has None where its files are missing."""
    geometry_path = folder / "geometry.json"
    if not geometry_path.is_file():
        return Reoptimised(None, None, dict.fromkeys(LABEL_TAGS), dict.fromkeys(LABEL_TAGS, False), dict.fromkeys(LABEL_TAGS), False)
    geometry = json.loads(geometry_path.read_text(encoding="utf-8"))
    result = json.loads((folder / "result.json").read_text(encoding="utf-8"))
    read = {tag: lowest_mode_cm(folder, tag, geometry) for tag in LABEL_TAGS}
    return Reoptimised(_symbols(geometry), np.asarray(geometry["coords_bohr"], float), {t: r[0] for t, r in read.items()},
                       {t: r[1] for t, r in read.items()}, {t: result.get(f"n_imaginary_{t}") for t in LABEL_TAGS},
                       (folder / APT_FILE).is_file())


def bond_changes(symbols: list[str], before: np.ndarray, after: np.ndarray) -> list[str]:
    """The bonds made or broken between two geometries of the same atoms, as 'C3-H11 broken' (atoms counted from 0)."""
    old, new = bond_graph(symbols, before), bond_graph(symbols, after)
    out = []
    for i, (a, b) in enumerate(zip(old, new, strict=True)):
        out += [f"{symbols[i]}{i}-{symbols[j]}{j} broken" for j in sorted(a - b) if j > i]
        out += [f"{symbols[i]}{i}-{symbols[j]}{j} made" for j in sorted(b - a) if j > i]
    return out


def _label_refusals(new: Reoptimised) -> Iterator[str]:
    """The reasons the label files of a finished optimisation give, in the order of the rule; each later one assumes the earlier passed."""
    missing = [t for t in LABEL_TAGS if new.lowest_cm[t] is None]
    if missing:
        yield f"no label file for {', '.join(missing)}"
        return
    pending = [t for t in LABEL_TAGS if new.pending[t]]
    if pending:
        yield f"the label of {', '.join(pending)} is marked low_mode_pending: its soft-mode repair did not run"
    if not new.has_apt:
        yield f"no {APT_FILE}: the APT failed its checks or was not written"
    imaginary = [f"{t} {new.lowest_cm[t]:.2f}" for t in LABEL_TAGS if not new.lowest_cm[t] > 0.0]
    if imaginary:
        yield f"still imaginary: lowest mode {', '.join(imaginary)} cm-1"
    counted = [f"{t} {new.counts[t]}" for t in LABEL_TAGS if new.counts[t] != 0]
    if counted:
        yield f"the label route's own imaginary counts are not both zero ({', '.join(counted)})"


def refusal(source_symbols: list[str], new: Reoptimised, changed: list[str]) -> str:
    """The first reason a re-optimised molecule stays out, or '' when it is accepted. `changed` is its list of changed bonds."""
    if new.symbols is None:
        return "no geometry.json: the optimisation did not finish or did not converge"
    if new.symbols != source_symbols:
        return "the atoms or their order differ from the corpus folder's"
    bonds = f"the bond graph changed: {'; '.join(changed)}" if changed else ""
    return next(_label_refusals(new), bonds)


def verdict(mol_id: str, source_geometry: dict, lowest_before: dict[str, float], new: Reoptimised) -> Verdict:
    """One molecule's verdict from its corpus geometry and its re-optimised folder's content."""
    symbols = _symbols(source_geometry)
    before = np.asarray(source_geometry["coords_bohr"], float)
    same_atoms = new.symbols == symbols
    changed = bond_changes(symbols, before, new.coords_bohr) if same_atoms else []
    rms = rms_heavy = None
    if same_atoms:
        heavy = np.array([s != "H" for s in symbols])
        rms, rms_heavy = kabsch(new.coords_bohr, before)[1], kabsch(new.coords_bohr[heavy], before[heavy])[1]
    reason = refusal(symbols, new, changed)
    return Verdict(mol_id, not reason, reason, lowest_before, new.lowest_cm, rms, rms_heavy,
                   bool(rms_heavy is not None and rms_heavy > CONFORMER_RMS_BOHR), changed)


def read_molecule(mol_id: str, corpus: Path, reoptimised: Path) -> Verdict:
    source = corpus / mol_id
    geometry = json.loads((source / "geometry.json").read_text(encoding="utf-8"))
    before = {}
    for tag in LABEL_TAGS:
        lowest, _ = lowest_mode_cm(source, tag, geometry)
        if lowest is None:
            raise FileNotFoundError(f"{source} has no analytic label for {tag}")
        before[tag] = lowest
    return verdict(mol_id, geometry, before, read_reoptimised(reoptimised / mol_id))


def _cm(value: float | None) -> str:
    return "—" if value is None else f"{value:.2f}"


def result_text(verdicts: list[Verdict]) -> str:
    """RESULT.md: the counts, then one row per molecule."""
    accepted = [v for v in verdicts if v.accepted]
    lines = ["# Imaginary-label re-optimisation: the acceptance read (TASKS 215)", "",
             f"{len(verdicts)} molecules read, {len(accepted)} accepted, {len(verdicts) - len(accepted)} stay out; "
             f"{sum(v.conformer_flag for v in verdicts)} flagged for a heavy-atom distance above {CONFORMER_RMS_BOHR} bohr.", "",
             "| id | lowest before (b3lyp / wb97x, cm⁻¹) | lowest after | rms all / heavy (bohr) | verdict |", "|---|---|---|---|---|"]
    for v in verdicts:
        rms = "—" if v.rms_bohr is None else f"{v.rms_bohr:.3f} / {v.rms_heavy_bohr:.3f}{' CONFORMER' if v.conformer_flag else ''}"
        lines.append(f"| {v.mol_id} | {' / '.join(_cm(v.lowest_before_cm[t]) for t in LABEL_TAGS)} | "
                     f"{' / '.join(_cm(v.lowest_after_cm[t]) for t in LABEL_TAGS)} | {rms} | "
                     f"{'accepted' if v.accepted else 'stays out: ' + v.reason} |")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("corpus", type=Path)
    ap.add_argument("reoptimised", type=Path)
    ap.add_argument("--ids", type=Path, required=True, help="one molecule id per line, first field ('#' starts a comment)")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    ids = [line.split()[0] for line in a.ids.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")]
    if not ids or len(set(ids)) != len(ids):
        raise ValueError(f"{a.ids}: the id list is empty or repeats an id")
    verdicts = [read_molecule(i, a.corpus, a.reoptimised) for i in ids]
    a.out.mkdir(parents=True, exist_ok=True)
    write_atomic(a.out / "record.json", json.dumps([asdict(v) for v in verdicts], indent=1))
    write_atomic(a.out / "RESULT.md", result_text(verdicts))
    print(f"{len(verdicts)} read, {sum(v.accepted for v in verdicts)} accepted -> {a.out / 'RESULT.md'}")


if __name__ == "__main__":
    main()
