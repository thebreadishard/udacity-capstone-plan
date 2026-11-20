"""The acceptance read of the imaginary-label re-optimisation (TASKS 215;
GoalGathering/notes/PreRegistration_2026-11-20_Imaginary_Label_Reoptimisation.md, sections 5 and 6).

Per molecule of the list: the corpus folder (the label that never trains) beside the re-optimised folder
`probes/imaginary_reopt_lane.sh` wrote. A molecule is accepted when all of these hold, and stays out with the first reason otherwise:

1. the optimisation finished (the folder holds geometry.json, which the optimiser writes last and only when geomeTRIC converged);
2. both label files exist, can be read, hold finite numbers and are not marked `low_mode_pending`; the APT file exists and carries
   `passed` = True (the label route writes the file with passed = False when the sum rule or the CPHF residual fails); result.json exists;
3. no label has an imaginary mode: the lowest projected vibrational frequency of both is above zero (`vibrations.vibrational_modes`,
   the route `probes/low_mode_coverage.py` counts with), and the label route's own counts in result.json are both zero;
4. it is still the same molecule: the atoms are the corpus folder's in its order and the bond graph is unchanged
   (`e8_cc_locality.bond_graph`, bonded below 1.2 times the sum of the covalent radii).

A folder with a missing or cut-off file is not a failed molecule by itself (section 6): with `--lane-logs` the lane's own markers
say whether the molecule was not run, is unfinished (started and cut off) or failed, in the optimisation or in the labels. Without
the logs such a molecule is reported as incomplete and the reason says that the logs were not given. One damaged folder never stops
the read of the others; a damaged corpus folder is a named reason too.

Reported and not deciding: the rms distance from the corpus geometry after a rigid rotation (`frame_match.kabsch`), over all atoms
and over the heavy atoms, and a flag when the heavy-atom distance passes CONFORMER_RMS_BOHR.

    python probes/imaginary_reopt_read.py <corpus molecules dir> <re-optimised dir> --ids FILE --out FOLDER [--lane-logs GLOB|FOLDER]
"""
from __future__ import annotations

import argparse
import glob
import json
import re
import sys
import zipfile
from collections import Counter
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
GEOMETRY_KEYS = ("symbols", "masses_amu", "coords_bohr")
# what reading a cut-off or damaged npz or json file raises (a JSON error is a ValueError); anything else is a fault of the read and raises
READ_ERRORS = (OSError, EOFError, KeyError, ValueError, zipfile.BadZipFile)

# the states a molecule's line can have; the last three and INCOMPLETE are not verdicts of the acceptance rule
ACCEPTED, REFUSED, FAILED, UNFINISHED, NOT_RUN = "accepted", "refused", "failed", "unfinished", "not run"
INCOMPLETE = "incomplete, lane logs not given"
SOURCE_PROBLEM = "corpus folder problem"
STATES = (ACCEPTED, REFUSED, FAILED, UNFINISHED, NOT_RUN, INCOMPLETE, SOURCE_PROBLEM)
NO_GEOMETRY = "no geometry.json"
NO_LOGS_NOTE = "the lane logs were not given (--lane-logs), so not run, unfinished and failed are not told apart"

# imaginary_reopt_lane.sh's per-molecule markers: '=== (IRL) <id>: <text> <date> <time>'
LANE_PREFIX = "=== (IRL) "
LANE_MARKER = re.compile(r"^=== \(IRL\) (?P<id>\S+): (?P<text>.*) (?P<stamp>\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)\s*$")
OPTIMISATION_FAILED = "FAILED in the optimisation"
LABELS_FAILED = re.compile(r"FAILED in the labels \(exit (\d+)\)")
STARTED_MARKERS = ("start", "optimisation kept from an earlier pass", "optimisation done")   # the lane was still working on the molecule
LOG_LINE_CHARS = 200


@dataclass(frozen=True)
class Refusal:
    """Why a molecule stays out. `incomplete`: a file is missing or cut off, so the lane's log decides between not run, unfinished and failed."""

    reason: str
    incomplete: bool = False


@dataclass(frozen=True)
class LabelRead:
    """One label file: its lowest projected vibrational frequency (None without a usable file), its pending mark, what is wrong with the file."""

    lowest_cm: float | None = None
    pending: bool = False
    problem: Refusal | None = None


@dataclass(frozen=True)
class Reoptimised:
    """What one re-optimised folder holds, as the verdict needs it; a field is None when its file is missing."""

    symbols: list[str] | None
    coords_bohr: np.ndarray | None
    lowest_cm: dict[str, float | None]
    pending: dict[str, bool]
    counts: dict[str, int | None] | None      # None: no result.json
    apt: Refusal | None = None                # None: the APT file is there and carries passed = True
    problem: Refusal | None = None            # the first file that cannot be read or holds a non-finite value
    folder_has_files: bool = True


@dataclass(frozen=True)
class LaneEvent:
    """The last marker a lane wrote for one molecule, and the last output line before it (the error, for a failure)."""

    text: str
    line_before: str


@dataclass(frozen=True)
class Verdict:
    """One molecule's line of the read."""

    mol_id: str
    accepted: bool
    state: str
    reason: str
    lowest_before_cm: dict[str, float | None]
    lowest_after_cm: dict[str, float | None]
    rms_bohr: float | None
    rms_heavy_bohr: float | None
    conformer_flag: bool
    changed_bonds: list[str]


def _symbols(geometry: dict) -> list[str]:
    return [s.capitalize() for s in geometry["symbols"]]


def _unreadable(path: Path, error: Exception) -> Refusal:
    return Refusal(f"label file unreadable: {path.name}: {type(error).__name__}", incomplete=True)


def load_geometry(path: Path) -> tuple[dict | None, Refusal | None]:
    """(geometry.json's content, None), or (None, why it cannot be read: damaged, or without one of GEOMETRY_KEYS)."""
    try:
        geometry = json.loads(path.read_text(encoding="utf-8"))
        missing = [key for key in GEOMETRY_KEYS if key not in geometry]
    except READ_ERRORS as error:
        return None, _unreadable(path, error)
    if missing:
        return None, Refusal(f"label file unreadable: {path.name}: no {', '.join(missing)}", incomplete=True)
    return geometry, None


def read_label(folder: Path, tag: str, geometry: dict) -> LabelRead:
    """One label file of a folder: the lowest projected vibrational frequency and the pending mark, or what is wrong with the file."""
    path = folder / f"hessian_{tag}_analytic.npz"
    if not path.is_file():
        return LabelRead()
    try:
        with np.load(path) as z:
            H, pending = np.asarray(z["H_raw"], float), "low_mode_pending" in z.files
    except READ_ERRORS as error:
        return LabelRead(problem=_unreadable(path, error))
    if not np.isfinite(H).all():
        return LabelRead(problem=Refusal(f"label holds a non-finite value: {path.name}"))
    modes = vibrational_modes(H, np.asarray(geometry["masses_amu"], float), np.asarray(geometry["coords_bohr"], float))
    return LabelRead(float(modes.omega_cm[0]), pending)


def apt_refusal(folder: Path) -> Refusal | None:
    """None when the APT file carries passed = True; the reason otherwise. analytic_hessians.write_apt writes the file with
    passed = False when the sum rule or the CPHF residual fails, so the file's existence alone says nothing."""
    path = folder / APT_FILE
    if not path.is_file():
        return Refusal(f"no {APT_FILE}: the APT was not written", incomplete=True)
    try:
        with np.load(path) as z:
            if "passed" not in z.files:
                return Refusal(f"{APT_FILE} carries no 'passed' mark: its checks are not on record")
            passed = np.asarray(z["passed"])
    except READ_ERRORS as error:
        return _unreadable(path, error)
    if passed.dtype != np.bool_ or passed.shape != ():
        return Refusal(f"{APT_FILE}: its 'passed' mark is not one true/false value")
    if not passed:
        return Refusal(f"{APT_FILE} is marked passed=False: the APT failed its sum rule or its CPHF residual")
    return None


def load_counts(folder: Path) -> tuple[dict[str, int | None] | None, Refusal | None]:
    """(the label route's own imaginary counts from result.json, None); (None, None) without the file; (None, why) when it cannot be read."""
    path = folder / "result.json"
    if not path.is_file():
        return None, None
    try:
        result = json.loads(path.read_text(encoding="utf-8"))
    except READ_ERRORS as error:
        return None, _unreadable(path, error)
    return {tag: result.get(f"n_imaginary_{tag}") for tag in LABEL_TAGS}, None


def read_reoptimised(folder: Path) -> Reoptimised:
    """A re-optimised folder as it stands on disk; a folder the lane never finished has None where its files are missing."""
    has_files = folder.is_dir() and any(folder.iterdir())
    geometry_path = folder / "geometry.json"
    geometry, problem = load_geometry(geometry_path) if geometry_path.is_file() else (None, None)
    if geometry is None:
        return Reoptimised(None, None, dict.fromkeys(LABEL_TAGS), dict.fromkeys(LABEL_TAGS, False), None, problem=problem,
                           folder_has_files=has_files)
    labels = {tag: read_label(folder, tag, geometry) for tag in LABEL_TAGS}
    counts, counts_problem = load_counts(folder)
    problems = [label.problem for label in labels.values() if label.problem] + ([counts_problem] if counts_problem else [])
    return Reoptimised(_symbols(geometry), np.asarray(geometry["coords_bohr"], float), {t: label.lowest_cm for t, label in labels.items()},
                       {t: label.pending for t, label in labels.items()}, counts, apt_refusal(folder),
                       problems[0] if problems else None, has_files)


def bond_changes(symbols: list[str], before: np.ndarray, after: np.ndarray) -> list[str]:
    """The bonds made or broken between two geometries of the same atoms, as 'C3-H11 broken' (atoms counted from 0)."""
    old, new = bond_graph(symbols, before), bond_graph(symbols, after)
    out = []
    for i, (a, b) in enumerate(zip(old, new, strict=True)):
        out += [f"{symbols[i]}{i}-{symbols[j]}{j} broken" for j in sorted(a - b) if j > i]
        out += [f"{symbols[i]}{i}-{symbols[j]}{j} made" for j in sorted(b - a) if j > i]
    return out


def _label_refusals(new: Reoptimised) -> Iterator[Refusal]:
    """The reasons the label files of a finished optimisation give, in the order of the rule; each later one assumes the earlier passed."""
    if new.problem:
        yield new.problem
        return
    missing = [t for t in LABEL_TAGS if new.lowest_cm[t] is None]
    if missing:
        yield Refusal(f"no label file for {', '.join(missing)}", incomplete=True)
        return
    pending = [t for t in LABEL_TAGS if new.pending[t]]
    if pending:
        yield Refusal(f"the label of {', '.join(pending)} is marked low_mode_pending: its soft-mode repair did not run", incomplete=True)
    if new.apt:
        yield new.apt
    if new.counts is None:
        yield Refusal("result.json missing", incomplete=True)
        return
    not_finite = [t for t in LABEL_TAGS if not np.isfinite(new.lowest_cm[t])]
    if not_finite:
        yield Refusal(f"the lowest mode of {', '.join(not_finite)} is not a finite number")
        return
    imaginary = [f"{t} {new.lowest_cm[t]:.2f}" for t in LABEL_TAGS if not new.lowest_cm[t] > 0.0]
    if imaginary:
        yield Refusal(f"still imaginary: lowest mode {', '.join(imaginary)} cm-1")
    counted = [f"{t} {new.counts[t]}" for t in LABEL_TAGS if new.counts[t] != 0]
    if counted:
        yield Refusal(f"the label route's own imaginary counts are not both zero ({', '.join(counted)})")


def refusal(source_symbols: list[str], new: Reoptimised, changed: list[str]) -> Refusal | None:
    """The first reason a re-optimised molecule stays out, or None when it is accepted. `changed` is its list of changed bonds."""
    if new.symbols is None:
        return new.problem or Refusal(NO_GEOMETRY, incomplete=True)
    if new.symbols != source_symbols:
        return Refusal("the atoms or their order differ from the corpus folder's")
    bonds = Refusal(f"the bond graph changed: {'; '.join(changed)}") if changed else None
    return next(_label_refusals(new), bonds)


def lane_log_paths(spec: str) -> list[Path]:
    """The lane logs a --lane-logs value names: a folder's *.log files, or the files a glob matches."""
    folder = Path(spec)
    found = folder.glob("*.log") if folder.is_dir() else (Path(p) for p in glob.glob(spec))
    paths = sorted(p for p in found if p.is_file())
    if not paths:
        raise FileNotFoundError(f"--lane-logs {spec}: no log file there (a folder's *.log files, or a glob)")
    return paths


def lane_events(paths: list[Path]) -> dict[str, LaneEvent]:
    """The last marker each molecule has in the lane logs, by the markers' time stamps (a second pass of a lane comes later)."""
    found: list[tuple[str, str, LaneEvent]] = []
    lane_lines = 0
    for path in paths:
        line_before = ""
        # a lane log also carries the libraries' output: a byte that is not UTF-8 there must not stop the read of the markers
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            marker = LANE_MARKER.match(line)
            if marker:
                found.append((marker["stamp"], marker["id"], LaneEvent(marker["text"], line_before)))
            if line.startswith(LANE_PREFIX):
                lane_lines += 1
                line_before = ""
            elif line.strip():
                line_before = line.strip()
    if not lane_lines:      # without this, the wrong files would turn every unfinished molecule into 'not run'
        raise ValueError(f"no '{LANE_PREFIX}…' line in {', '.join(str(p) for p in paths)}: these are not the lane logs")
    return {mol_id: event for _, mol_id, event in sorted(found, key=lambda entry: entry[0])}


def lane_state(event: LaneEvent | None, new: Reoptimised) -> tuple[str, str]:
    """(state, what the lane's log says) for a molecule whose folder is incomplete; (REFUSED, '') when the lane finished the molecule,
    so that what is missing on disk is the whole reason."""
    if event is None:
        if new.symbols is None and not new.folder_has_files:
            return NOT_RUN, "not run: no file in its folder and no marker in the lane logs"
        return UNFINISHED, "unfinished: its folder holds files and the lane logs hold no marker for it"
    if event.text.startswith(OPTIMISATION_FAILED):
        return FAILED, f"failed in the optimisation: {event.line_before[:LOG_LINE_CHARS] or 'the log holds no line before the marker'}"
    labels_failed = LABELS_FAILED.match(event.text)
    if labels_failed:
        return FAILED, f"failed in the labels (exit {labels_failed[1]})"
    if event.text.startswith(STARTED_MARKERS):
        return UNFINISHED, f"unfinished: started and cut off in the {'optimisation' if new.symbols is None else 'labels'}"
    return REFUSED, ""


def judge(refused: Refusal | None, new: Reoptimised, logs_given: bool, event: LaneEvent | None) -> tuple[str, str]:
    """(state, reason) of one molecule from the rule's refusal and, for an incomplete folder, from the lane's log."""
    if refused is None:
        return ACCEPTED, ""
    if not refused.incomplete:
        return REFUSED, refused.reason
    if not logs_given:
        return INCOMPLETE, f"{refused.reason}; {NO_LOGS_NOTE}"
    state, said = lane_state(event, new)
    return state, f"{said}; on disk: {refused.reason}" if said else refused.reason


def verdict(mol_id: str, source_geometry: dict, lowest_before: dict[str, float], new: Reoptimised,
            events: dict[str, LaneEvent] | None = None) -> Verdict:
    """One molecule's verdict from its corpus geometry and its re-optimised folder's content; `events` are the lane logs' (None: not given)."""
    symbols = _symbols(source_geometry)
    before = np.asarray(source_geometry["coords_bohr"], float)
    same_atoms = new.symbols == symbols
    changed = bond_changes(symbols, before, new.coords_bohr) if same_atoms else []
    rms = rms_heavy = None
    if same_atoms:
        heavy = np.array([s != "H" for s in symbols])
        rms, rms_heavy = kabsch(new.coords_bohr, before)[1], kabsch(new.coords_bohr[heavy], before[heavy])[1]
    state, reason = judge(refusal(symbols, new, changed), new, events is not None, (events or {}).get(mol_id))
    return Verdict(mol_id, state == ACCEPTED, state, reason, lowest_before, new.lowest_cm, rms, rms_heavy,
                   bool(rms_heavy is not None and rms_heavy > CONFORMER_RMS_BOHR), changed)


def read_source(source: Path) -> tuple[dict | None, dict[str, float | None], str]:
    """(geometry, lowest mode per label, '') of a corpus folder, or what keeps it from being the 'before' of the read."""
    lowest: dict[str, float | None] = dict.fromkeys(LABEL_TAGS)
    path = source / "geometry.json"
    if not path.is_file():
        return None, lowest, "the corpus folder has no geometry.json"
    geometry, problem = load_geometry(path)
    if geometry is None:
        return None, lowest, f"the corpus folder's {problem.reason}"
    labels = {tag: read_label(source, tag, geometry) for tag in LABEL_TAGS}
    lowest = {tag: label.lowest_cm for tag, label in labels.items()}
    problems = [f"the corpus folder's {label.problem.reason}" for label in labels.values() if label.problem]
    problems += [f"the corpus folder has no analytic label for {tag}" for tag, label in labels.items()
                 if label.lowest_cm is None and not label.problem]
    return geometry, lowest, problems[0] if problems else ""


def read_molecule(mol_id: str, corpus: Path, reoptimised: Path, events: dict[str, LaneEvent] | None = None) -> Verdict:
    """One molecule's line: the corpus folder's label before, the re-optimised folder's after, and the lane logs' markers when given."""
    geometry, before, problem = read_source(corpus / mol_id)
    if problem:
        return Verdict(mol_id, False, SOURCE_PROBLEM, problem, before, dict.fromkeys(LABEL_TAGS), None, None, False, [])
    return verdict(mol_id, geometry, before, read_reoptimised(reoptimised / mol_id), events)


def _cm(value: float | None) -> str:
    return "—" if value is None else f"{value:.2f}"


def result_text(verdicts: list[Verdict]) -> str:
    """RESULT.md: the counts, then one row per molecule."""
    states = Counter(v.state for v in verdicts)
    out = ", ".join(f"{states[s]} {s}" for s in STATES if s != ACCEPTED and states[s])
    lines = ["# Imaginary-label re-optimisation: the acceptance read (TASKS 215)", "",
             f"{len(verdicts)} molecules read, {states[ACCEPTED]} accepted, {len(verdicts) - states[ACCEPTED]} stay out"
             f"{f' ({out})' if out else ''}; "
             f"{sum(v.conformer_flag for v in verdicts)} flagged for a heavy-atom distance above {CONFORMER_RMS_BOHR} bohr.", "",
             "| id | lowest before (b3lyp / wb97x, cm⁻¹) | lowest after | rms all / heavy (bohr) | verdict |", "|---|---|---|---|---|"]
    for v in verdicts:
        rms = "—" if v.rms_bohr is None else f"{v.rms_bohr:.3f} / {v.rms_heavy_bohr:.3f}{' CONFORMER' if v.conformer_flag else ''}"
        said = "accepted" if v.accepted else "stays out: " + v.reason.replace("|", "/")      # a log line may carry the table's separator
        lines.append(f"| {v.mol_id} | {' / '.join(_cm(v.lowest_before_cm[t]) for t in LABEL_TAGS)} | "
                     f"{' / '.join(_cm(v.lowest_after_cm[t]) for t in LABEL_TAGS)} | {rms} | {said} |")
    return "\n".join(lines) + "\n"


def read_ids(path: Path) -> list[str]:
    """The molecule ids of a list file: the first field of each line, '#' starting a comment line."""
    ids = [line.split()[0] for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")]
    if not ids:
        raise ValueError(f"{path}: the id list names no molecule")
    repeated = sorted(i for i, n in Counter(ids).items() if n > 1)
    if repeated:
        raise ValueError(f"{path}: the id list repeats an id ({', '.join(repeated)})")
    return ids


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("corpus", type=Path)
    ap.add_argument("reoptimised", type=Path)
    ap.add_argument("--ids", type=Path, required=True, help="one molecule id per line, first field ('#' starts a comment)")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--lane-logs", help="the lanes' logs, a folder (its *.log files) or a glob: they tell not run, unfinished and failed apart")
    a = ap.parse_args(argv)
    ids = read_ids(a.ids)
    events = lane_events(lane_log_paths(a.lane_logs)) if a.lane_logs else None
    verdicts = [read_molecule(i, a.corpus, a.reoptimised, events) for i in ids]
    a.out.mkdir(parents=True, exist_ok=True)
    write_atomic(a.out / "record.json", json.dumps([asdict(v) for v in verdicts], indent=1))
    write_atomic(a.out / "RESULT.md", result_text(verdicts))
    print(f"{len(verdicts)} read, {sum(v.accepted for v in verdicts)} accepted -> {a.out / 'RESULT.md'}")


if __name__ == "__main__":
    main()
