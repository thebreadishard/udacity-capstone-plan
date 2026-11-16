"""Step 6 of the pipeline (TASKS 211): each band's anharmonic position ν = ω + Δ_anh, printed as the best estimate where the step
applies, with no licence claimed for it (`m08/positions.py`).

The step is `probes/anharmonic_step.py`'s and nothing is modelled here. This module gives it what it needs of one molecule and
writes down what came back:

1. the molecule's B3LYP modes, from the Hessian of step 3 at the geometry of step 2 (`Modes.from_hessian`, the training path's own
   `dpir.qff.harmonic`);
2. its GFN2-xTB quartic force field with that field's GVPT2 label: `probes/xtb_field_for_step.sh` in WSL under
   `probes/wsl_capped.sh`, started from a reference record written into `<result>/anharmonic/G/` — the two existing runners
   (`xtb_anharmonic.sh`, `gvpt2_labels.py`), called as the repository calls them;
3. `mode_steps` on the two with the committed artefact, then `carry_to_bands` onto the modes of H_low + ΔH, by overlap.

Every network stick of the record gets its ν, its Δ_anh, the step's bar for the family and the reason where it has no step; the
whole output is saved beside the other steps' files as `anharmonic.json`. A molecule the step cannot serve — an element the
model's training table does not hold, a B3LYP Hessian `dpir.qff.harmonic` refuses, a force field that fails, is noisy, is stopped
at the memory cap or does not finish within the time budget — keeps its harmonic positions and the record says why: the run does
not fail. Anything else that goes wrong is an error and raises; the pipeline has delivered the harmonic result before step 6
starts, so no error here can lose it (`pipeline.run`).

The time budget (`FieldSettings.budget_s`; the pipeline's --anharmonic-minutes) is kept inside WSL by
`probes/run_in_scope.sh`: the force field runs in a systemd user scope of this run's own name (the memory properties of
`probes/wsl_capped.sh`, which is not used here because its scope has no name to ask for), under `timeout`. Whatever the exit,
the script reads the unit's cgroup, kills what is left in it and fails if anything survives — ownership, not a pattern on
command lines (tests/test_run_in_scope.py: a grandchild that ignores SIGTERM under a name of its own is gone at the budget).
Its exit is 124 at the budget. Where WSL cannot make such a scope the pipeline refuses before step 1 (`preflight`). The stopped
run's finished Hessians stay in <result>/anharmonic/xtb; this pipeline run does not take them up again, but the command below
does, because `probes/xtb_anharmonic.sh` skips the Hessians it finds — and the reason a certificate prints says so.

    python -m m08.anharmonic <pipeline result folder> [--shards 2] [--cap-mb 1536] [--threads 4] [--minutes 120] [--dry-run]

adds the step to a finished result, or takes up one that ran out of time. That is a delivery like the pipeline's own
(`pipeline._deliver`): pipeline.json gets the sticks' ν and a numbered delivery, the certificate's pair is written again, and the
result's progress record, where it has one, gets the delivery's number, so that a live show reads the result again.
"""
from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from . import pipeline as P
from . import positions as POS

# isort: split
# probes/ and module 05's code, on the path through m08.pipeline
import anharmonic_step as AS
import rungC_intensities as RINT
from anchor_registry import sha16
from learning_curve_layerA import molecule_features

FIELD_SCRIPT = P.PLAN / "probes" / "xtb_field_for_step.sh"
SCOPE_SCRIPT = P.PLAN / "probes" / "run_in_scope.sh"
SURVIVORS = 70                               # run_in_scope.sh: processes of the unit outlived SIGKILL
FOLDER, RECORD, LOG = "anharmonic", "anharmonic.json", "anharmonic_field.log"
UNIT_FILE = "scope_unit"                     # in <result>/anharmonic: the systemd unit of the force field that was started last
STICK_TOL_CM = 0.051                         # the record rounds positions to 0.1 cm⁻¹
MIN_CAP_MB = 1024                            # below this one dxtb process of a 12-atom molecule does not fit beside the label step
MIN_BUDGET_S = 60                            # a budget under a minute stops every force field: the switch for that is 'off'
KILL_AFTER_S = 30                            # after the budget's SIGTERM, how long the processes get before SIGKILL
FINALISE_S = 120                             # the label, the model and the second certificate after the force field: well under this
TIMED_OUT = 124                              # run_in_scope.sh's exit code when the budget was reached
RULE_FREQ_TOL_CM = 1.0                       # the two rules' B3LYP modes are the same modes: their ω differ by the mass tables only
FAILED_LINE = re.compile(r"^=== \(ANH\) FAILED: (.*?) \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", re.MULTILINE)
PEAK_LINE = re.compile(r"^=== \(ANH\) peak memory (\d+) MB", re.MULTILINE)
SOFTWARE = ("GFN2-xTB: the minimum by xtb, the Hessians by dxtb (central differences of its forces) at ±0.10 along every mode, "
            "dpir.qff; GVPT2 by probes/gvpt2_labels.py with pyVPT2's polyad solver (probes/xtb_field_for_step.sh)")


class NotApplied(Exception):
    """The step cannot serve this molecule; `reason` is what the record and the certificate say, `field` the force-field run's
    record where one was started."""

    def __init__(self, reason: str, field: dict | None = None) -> None:
        super().__init__(reason)
        self.reason = reason
        self.field = field


@dataclass(frozen=True)
class FieldSettings:
    """How the force field is computed: `shards` dxtb processes of `omp_threads` threads each, under a WSL cap of `cap_mb`, and
    stopped after `budget_s` seconds."""
    shards: int
    omp_threads: int
    cap_mb: int
    budget_s: int

    def __post_init__(self) -> None:
        if min(self.shards, self.omp_threads) < 1 or self.cap_mb < MIN_CAP_MB:
            raise ValueError(f"force-field settings {self}: at least one shard and one thread, and a cap of {MIN_CAP_MB} MB or more")
        if self.budget_s < MIN_BUDGET_S:
            raise ValueError(f"a time budget of {self.budget_s} s: at least {MIN_BUDGET_S} s, or the step switched off")

    @property
    def budget_minutes(self) -> float:
        return self.budget_s / 60

    @classmethod
    def of(cls, threads: int, shards: int, cap_mb: int, minutes: float) -> FieldSettings:
        """`threads` cores shared out over `shards` processes, for at most `minutes`."""
        if shards < 1:
            raise ValueError(f"{shards} force-field processes: at least one")
        return cls(shards, max(1, threads // shards), cap_mb, round(60 * minutes))


def load_artefact() -> AS.Artefact:
    """The committed artefact, checked (`anharmonic_step.load_artefact`): the pipeline reads it before any computation."""
    return AS.load_artefact()


def artefact_record(artefact: AS.Artefact) -> dict:
    """What a result keeps of the artefact it used: the file, its hash, the commit and date it was written at, its bars."""
    path = Path(AS.ARTEFACT)
    return {"file": path.relative_to(P.PLAN).as_posix(), "sha16": sha16(path), "commit": artefact.header["commit"],
            "written": artefact.header["written"], "bars_cm": AS.bars(artefact),
            "training_molecules": len(artefact.header["training_molecules"]), "elements": sorted(AS.elements(artefact)),
            "target_composition": artefact.header["target_composition"],
            "targets": {fa: {"rows": m.n_target_rows, "per_target_rms_cm": m.per_target_rms_cm}
                        for w in artefact.windows for fa, m in w.families.items()}}


def geometry(d: Path) -> tuple[list[str], np.ndarray, np.ndarray]:
    """The result folder's atoms: symbols as dpir.qff writes them, coordinates in bohr, masses in amu."""
    g = json.loads((d / "geometry.json").read_text(encoding="utf-8"))
    return [s.capitalize() for s in g["symbols"]], np.asarray(g["coords_bohr"], float).reshape(-1, 3), np.asarray(g["masses_amu"], float)


def b3lyp_modes(symbols: list[str], coords: np.ndarray, H_low: np.ndarray, artefact: AS.Artefact) -> AS.Modes:
    """The molecule's B3LYP modes as the model's inputs need them, or the reason the model cannot take this molecule: an element
    its training table (the artefact's own list) does not hold, or modes `dpir.qff.harmonic` refuses."""
    known = AS.elements(artefact)
    unseen = sorted(set(symbols) - known)
    if unseen:
        raise NotApplied(f"element(s) {', '.join(unseen)} outside the anharmonic model's training table ({', '.join(sorted(known))})")
    try:
        return AS.Modes.from_hessian(H_low, symbols, coords)
    except ValueError as e:
        raise NotApplied(f"the B3LYP modes are not the 3N−6 the force field needs: {e}") from e


def write_reference(d: Path, symbols: list[str], coords: np.ndarray, H_low: np.ndarray) -> Path:
    """The B3LYP minimum as the reference record `xtb_anharmonic.sh` starts from (<result>/anharmonic/G/ref.json); its folder."""
    g = d / FOLDER / "G"
    g.mkdir(parents=True, exist_ok=True)
    P.write_json(g / "ref.json", {"driver": "hessian", "model": {"method": "b3lyp", "basis": "6-31g*"},
                                  "molecule": {"symbols": symbols, "geometry": coords.ravel().tolist()},
                                  "return_result": np.asarray(H_low, float).ravel().tolist()})
    return g


def scope_unit(name: str) -> str:
    """A unit name no other run has: the scope the force field's processes belong to, and are stopped by."""
    return f"m08-anharmonic-{name}-{uuid.uuid4().hex[:10]}"


def stop_command(unit: str) -> str:
    """What stops a force field's scope by hand, from Windows."""
    return f"wsl -e systemctl --user stop {unit}.scope"


def scope_note(d: Path) -> str:
    """For the reason of an interrupted step: the scope its force field was started in, which may outlive the interrupt, and the
    command that stops it; '' where no force field was started."""
    path = d / FOLDER / UNIT_FILE
    if not path.is_file():
        return ""
    unit = path.read_text(encoding="utf-8").strip()
    return (f"; the force field's scope {unit}.scope may still run in WSL until its own time limit — `{stop_command(unit)}` stops it")


def field_command(name: str, d: Path, s: FieldSettings, unit: str, dry: bool = False) -> list[str]:
    """The WSL command of the force field and its label, in the scope `unit` under the memory cap and the time budget
    (`probes/run_in_scope.sh`, which leaves no process of the scope behind); with `dry`, the script's own check of its tools."""
    q, w = shlex.quote, P.wsl_path
    inner = (f"export SHARDS={s.shards} OMP_NUM_THREADS={s.omp_threads} PYTHONUNBUFFERED=1; "
             f"bash {q(w(SCOPE_SCRIPT))} {unit} {s.cap_mb} {s.budget_s} {KILL_AFTER_S} -- "
             f"bash {q(w(FIELD_SCRIPT))} {q(name)} {q(w(d / FOLDER / 'G'))} {q(w(d / FOLDER))}" + (" --dry-run" if dry else ""))
    return ["wsl.exe", "-e", "bash", "-lc", inner]


def preflight() -> None:
    """Refuse, before anything is computed, a machine on which the force field could not be owned and stopped: WSL without a
    systemd user manager. There is no fallback to killing by pattern."""
    r = subprocess.run(["wsl.exe", "-e", "bash", "-lc", f"bash {shlex.quote(P.wsl_path(SCOPE_SCRIPT))} --check"],
                       capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=120, check=False)
    if r.returncode != 0:
        raise P.Refused([f"the anharmonic step cannot run here: {(r.stdout + r.stderr).strip()[-300:] or f'exit {r.returncode}'} "
                         "(--no-anharmonic gives the harmonic result)"])


def force_field(name: str, d: Path, s: FieldSettings) -> tuple[AS.XtbField, dict]:
    """The molecule's GFN2-xTB force field with its GVPT2 label, computed in WSL from <result>/anharmonic/G/ref.json; and the
    run's record (seconds, peak memory where the cap's scope reports it). Raises NotApplied where there is no usable field."""
    t = time.time()
    unit = scope_unit(name)
    (d / FOLDER).mkdir(parents=True, exist_ok=True)
    (d / FOLDER / UNIT_FILE).write_text(unit, encoding="utf-8")       # before the run: an interrupt must be able to name the scope
    rc = P._run(field_command(name, d, s, unit), d / LOG, "GFN2-xTB quartic force field and its GVPT2 label (WSL)")
    log = (d / LOG).read_text(encoding="utf-8", errors="replace")
    peak = PEAK_LINE.search(log)
    record = {"seconds": round(time.time() - t, 1), "peak_memory_mb": int(peak.group(1)) if peak else None, "shards": s.shards,
              "omp_threads": s.omp_threads, "cap_mb": s.cap_mb, "budget_minutes": s.budget_minutes, "unit": f"{unit}.scope",
              "software": SOFTWARE, "log": LOG}
    if rc == SURVIVORS:
        raise RuntimeError(f"processes of the force field's scope {unit}.scope survived its stop ({LOG}): `{stop_command(unit)}`, "
                           "and look, before anything else runs")
    if rc == TIMED_OUT:
        raise NotApplied(f"{POS.timed_out(s.budget_minutes)}; its scope {unit}.scope was stopped at the budget and left no process "
                         f"(`{stop_command(unit)}` would stop one seen again) ({LOG})", record)
    if rc in P.KILLED_AT_CAP:
        raise NotApplied(f"the GFN2-xTB force field was stopped at the WSL cap of {s.cap_mb} MB ({LOG})", record)
    if rc != 0:
        failed = FAILED_LINE.findall(log)
        raise NotApplied(f"the GFN2-xTB force field could not be made: {failed[-1] if failed else f'exit {rc}'} ({LOG})", record)
    x = d / FOLDER / "xtb" / name / "X"
    try:
        return AS.XtbField.from_folder(str(x), str(d / FOLDER / "gvpt2_x" / f"{name}.json")), record
    except (ValueError, OSError) as e:
        raise NotApplied(f"the GFN2-xTB force field cannot be read: {e}", record) from e


def low_hessian(d: Path) -> np.ndarray:
    """Step 3's B3LYP Hessian of a result folder (Cartesian, hartree/bohr², projected)."""
    with np.load(d / P.RI.LOW_HESSIAN) as z:
        return np.asarray(z["H_projected"], float)


def dry_run(req: Request) -> int:
    """Everything the step checks before the force field's first Hessian: the artefact (loaded by the caller), the molecule's B3LYP
    modes, the reference record, and the WSL script's own dry run under the cap. The exit code."""
    symbols, coords, _ = geometry(req.folder)
    H_low = low_hessian(req.folder)
    try:
        b3lyp_modes(symbols, coords, H_low, req.artefact)
    except NotApplied as e:
        print(f"[anharmonic] dry run: the step would not be applied — {e.reason}", flush=True)
        return 0
    write_reference(req.folder, symbols, coords, H_low)
    return P._run(field_command(req.name, req.folder, req.settings, scope_unit(req.name), dry=True), req.folder / "anharmonic_dry_run.log",
                  "dry run of the GFN2-xTB force field's tools (WSL)")


def corrected_modes(H: np.ndarray, masses: np.ndarray, sticks: list[dict]) -> np.ndarray:
    """The mass-weighted modes of the corrected Hessian in the sticks' order (ascending position), checked against the sticks."""
    w, _, L = RINT.mode_intensities(H, masses, np.zeros((3, H.shape[0])), return_modes=True)
    order = np.argsort(w)
    if len(sticks) != len(w) or max(abs(s["omega_cm"] - x) for s, x in zip(sticks, w[order], strict=True)) > STICK_TOL_CM:
        raise RuntimeError("the recorded network spectrum is not the one H_low + ΔH gives")
    return L[:, order]


def stick_entry(omega_cm: float, band: AS.BandStep, steps: list[AS.ModeStep]) -> tuple[float | None, dict]:
    """A stick's ν and its anharmonic block, rounded as the record rounds positions; ν is the recorded ω plus the recorded Δ_anh."""
    delta = None if band.delta_anh_cm is None else round(band.delta_anh_cm, 1)
    entry = {"delta_anh_cm": delta, "bar_cm": band.bar_cm, "reason": band.reason, "error_not_measured": band.error_not_measured,
             "family": None if band.mode is None else steps[band.mode].family, "b3lyp_mode": band.mode, "overlap": round(band.overlap, 3)}
    return (None if delta is None else round(omega_cm + delta, 1)), entry


def counts(bands: list[AS.BandStep]) -> dict:
    no_step: dict[str, int] = {}
    for b in bands:
        if b.reason is not None:
            no_step[b.reason] = no_step.get(b.reason, 0) + 1
    return {"stepped": sum(b.reason is None for b in bands), "error_not_measured": sum(b.error_not_measured for b in bands),
            "no_step": no_step}


def with_summary(out: dict, summary: dict) -> dict:
    """The spectra with the step's summary and the sentence about the positions the record prints."""
    return {**out, "anharmonic": summary, "note": POS.note(summary)}


def not_applied(out: dict, reason: str, field: dict | None = None) -> dict:
    """The spectra of a molecule without the step: every stick harmonic, and the reason once, for the whole spectrum."""
    for stick in out["network"]["sticks"]:
        stick["nu_cm"], stick["anharmonic"] = None, None
    return with_summary(out, {"status": POS.NOT_APPLIED, "reason": reason, "model": AS.MODEL, "field": field})


@dataclass(frozen=True)
class Request:
    """One molecule's step: its name, result folder and canonical SMILES (None where the record names none), the artefact and the
    field's settings; artefact and settings None is the step switched off."""
    name: str
    folder: Path
    smiles: str | None
    artefact: AS.Artefact | None
    settings: FieldSettings | None

    def __post_init__(self) -> None:
        if (self.artefact is None) != (self.settings is None):
            raise ValueError("the step is on with an artefact and settings, or off with neither")


def first_delivery(req: Request, out: dict) -> dict:
    """The spectra of the pipeline's first delivery, before step 6 starts: every stick harmonic, and the note that says the step
    is running and what it will add — or, with the step switched off, that it is off (that delivery is then the only one)."""
    if req.artefact is None:
        return not_applied(out, POS.SWITCHED_OFF)
    for stick in out["network"]["sticks"]:
        stick["nu_cm"], stick["anharmonic"] = None, None
    deadline = time.localtime(time.time() + req.settings.budget_s + KILL_AFTER_S + FINALISE_S)
    return with_summary(out, {"status": POS.RUNNING, "reason": None, "model": AS.MODEL, "budget_minutes": req.settings.budget_minutes,
                              "final_by": time.strftime("%Y-%m-%d %H:%M", deadline), "field": None})


def certificate_families(d: Path, H_low: np.ndarray, omega: np.ndarray) -> list[str]:
    """Each B3LYP mode's family by the certificate's rule (`learning_curve_layerA.molecule_features`, as `live_certificate` reads
    it), in the step's mode order; the two mode lists must be the same modes."""
    feats = molecule_features(d, lo=H_low, hi=H_low)
    freq = np.asarray(feats["freq"], float)
    if freq.shape != omega.shape or np.abs(freq - omega).max() > RULE_FREQ_TOL_CM:
        raise RuntimeError(f"{d.name}: the certificate's family rule and the anharmonic step do not see the same B3LYP modes")
    return [str(f) for f in feats["family"]]


def step(req: Request, dH: np.ndarray, out: dict) -> dict:
    """Step 6: `out` (step 5's spectra) with each network stick's ν and anharmonic block, the summary and the positions note;
    `anharmonic.json` holds every mode's and every band's step."""
    d, artefact = req.folder, req.artefact
    if artefact is None:
        return not_applied(out, POS.SWITCHED_OFF)
    symbols, coords, masses = geometry(d)
    H_low = low_hessian(d)
    try:
        modes = b3lyp_modes(symbols, coords, H_low, artefact)
        write_reference(d, symbols, coords, H_low)
        xtb, field_record = force_field(req.name, d, req.settings)
    except NotApplied as e:
        print(f"[pipeline] anharmonic step not applied: {e.reason}", flush=True)
        return not_applied(out, e.reason, e.field)
    steps = AS.agree_on_family(AS.mode_steps(modes, xtb, artefact), certificate_families(d, H_low, modes.omega))
    sticks = out["network"]["sticks"]
    bands = AS.carry_to_bands(corrected_modes(H_low + dH, masses, sticks), modes.q, steps)
    for stick, band in zip(sticks, bands, strict=True):
        stick["nu_cm"], stick["anharmonic"] = stick_entry(stick["omega_cm"], band, steps)
    summary = {"status": POS.APPLIED, "reason": None, "model": AS.MODEL, "artefact": artefact_record(artefact), "bands": counts(bands),
               "seen": AS.seen(artefact, req.smiles), "composition": AS.composition(artefact, symbols), "field": field_record}
    P.write_json(d / RECORD, {"summary": summary, "modes": [s.as_record() for s in steps],
                              "bands": [{"omega_cm": s["omega_cm"], "nu_cm": s["nu_cm"], **b.as_record()}
                                        for s, b in zip(sticks, bands, strict=True)]})
    print(f"[pipeline] anharmonic step: {summary['bands']['stepped']} of {len(bands)} bands stepped ({RECORD})", flush=True)
    return with_summary(out, summary)


def deliver_resumed(rec: dict, d: Path, t0: float) -> None:
    """The delivery of a step added to a finished result: numbered after the result's earlier deliveries, with the certificate's
    pair and — where the folder has a progress record — the number the live show reads."""
    from . import live_certificate as LC  # that module imports the pipeline, as this one does
    from .catalog import Catalog
    from .progress import FILE, Progress

    def certify(folder: Path, what: str) -> None:
        _, md = LC.write(LC.certificate(folder, Catalog()), folder)
        print(f"[anharmonic] delivery ({what}): {md}", flush=True)

    rec.setdefault("deliveries", [])
    applied = rec["spectra"]["anharmonic"]["status"] == POS.APPLIED
    progress = Progress.load(d) if (d / FILE).is_file() else None
    P._deliver(rec, P.RESUMED_DELIVERY if applied else P.RESUMED_HARMONIC, P.Delivering(d, t0, certify, progress))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("result", type=Path, help="a finished pipeline result folder")
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--shards", type=int, default=2)
    ap.add_argument("--cap-mb", type=int, default=1536)
    ap.add_argument("--minutes", type=float, default=120, help="the force field's time budget; it is stopped there")
    ap.add_argument("--dry-run", action="store_true", help="check the artefact, the modes and the WSL tools; compute nothing")
    a = ap.parse_args(argv)
    d = a.result.resolve()
    rec = json.loads((d / "pipeline.json").read_text(encoding="utf-8"))
    if POS.summary_of(rec["spectra"])["status"] == POS.APPLIED:
        raise SystemExit(f"{d}: the anharmonic step is already in this result; a result is never overwritten")
    req = Request(rec["name"], d, rec["admission"].get("smiles"), load_artefact(),
                  FieldSettings.of(a.threads, a.shards, a.cap_mb, a.minutes))
    if a.dry_run:
        return dry_run(req)
    with np.load(d / P.CORRECTION) as z:
        dH = z["dH"]
    print(f"[anharmonic] start: {rec['name']}, {req.settings}", flush=True)
    t = time.time()
    rec["spectra"] = step(req, dH, rec["spectra"])
    rec["seconds"]["anharmonic"] = round(time.time() - t, 1)
    deliver_resumed(rec, d, t)
    s = rec["spectra"]["anharmonic"]
    print(f"[anharmonic] done: {s['status']}{'' if s['reason'] is None else ' — ' + s['reason']}; {rec['seconds']['anharmonic']} s; "
          f"field {s['field']}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
