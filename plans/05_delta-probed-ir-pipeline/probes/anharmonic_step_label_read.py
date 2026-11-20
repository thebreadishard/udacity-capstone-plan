"""The anharmonic step's printed shifts of one molecule against the label the step was trained on (TASKS 211;
GoalGathering/notes/PreRegistration_2026-11-20_Anharmonic_Step_Substituted_Molecule.md, part B and the prior table).

    python anharmonic_step_label_read.py read --run <pipeline result folder> --g-dir <label's G folder> --label <gvpt2 json> --out <folder>
    python anharmonic_step_label_read.py prior --modes-json <modes.json> --out <folder>

`read`: the run is a pipeline result with the step applied (pipeline.json's network sticks carry ν and the step's block); the
label is the molecule's B3LYP/6-31G* quartic force field with its GVPT2 file (probes/g_label_for_step.sh). Each band is matched
to the label's modes by `s2_xtb_read.match_sets`, the match the step and its training use, after the label's geometry is
rotated onto the run's. Per band: the printed step minus the label's shift. Per family: the rms over the bands that carry the
family's bar, by `s3_read.family_read` — the function that computed the bars on coronene and tetracene — beside the bar, the
95 % line for that number of bands (`line_factor`) and the registered statement: within the bar, consistent with it at this n,
or beyond it. Bands printed harmonic are listed with the label's shift: what leaving them harmonic costs.

Refused: a label of other atoms, another atom order or a geometry past `frame_match.FRAME_TOLERANCE_BOHR`; a label with
another number of modes than the run has bands; a label that predates the VPT2-domain check; a label with symmetry pairs
(the bars count a pair once, and this read does not collapse pairs). Not read, and recorded as such: a NOISY force field
(`s2_read.load_molecule`'s noise rule, the one S2 excluded its five molecules by).

`prior`: from the stored scaffold-left-out read of the training molecules (results_m1/anharmonic_design_questions_2026-11-16),
the substituted molecules' rms per family beside the bars, and the same count for the unsubstituted molecules of that read.
No run; prior information for the read above.

Writes <out>/label_read.json and RESULT.md, or <out>/prior.json and PRIOR.md, each through a temp file; an existing record is
never overwritten.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import chi2

HERE = Path(__file__).resolve().parent
PLAN = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
from m08 import anharmonic as AN  # noqa: E402
from m08 import pipeline as P  # noqa: E402

# isort: split
import anharmonic_step as AS  # noqa: E402
from frame_match import frame_onto  # noqa: E402
from s1_anharmonic_level import harmonic_modes  # noqa: E402
from s2_read import load_molecule, write_atomic  # noqa: E402
from s2_xtb_read import match_sets  # noqa: E402
from s3_read import family_read  # noqa: E402

REGISTRATION = "GoalGathering/notes/PreRegistration_2026-11-20_Anharmonic_Step_Substituted_Molecule.md"
MIN_BANDS = 4               # a family with fewer bands under its bar gets its rms reported and no statement
BAR_DECIMALS = 2            # the bars are stated to 0.01 cm⁻¹; an rms is compared at the precision it is printed with
LINE_QUANTILE = 0.95        # one-sided: the rms that n independent errors with the bar as their sd stay under 19 times in 20
WITHIN, CONSISTENT, BEYOND, NO_STATEMENT = "within the bar", "consistent with the bar at this n", "beyond the bar", "no statement"
NONE_BEYOND = "no family beyond its bar"        # the molecule's outcome when every family with a statement is WITHIN or CONSISTENT
NOISY_REASON = "NOISY"      # how `s2_read.load_molecule` opens the reason of a force field its noise rule excludes
ALL = "all"                 # the stored read's row over every family
# The training molecules with a substituent on the ring system, by corpus id (names from the corpus manifest); the other 30 of
# the artefact's 37 are bare ring systems. The stored read (modes.json) holds 38 molecules: those 37 and coronene, a target,
# which that read fitted on all training molecules (its modes.py, line 14); tetracene is in its `skipped` for want of a corpus
# row. The baseline of the prior table is therefore 31 unsubstituted molecules, 30 with their scaffold left out and coronene.
SUBSTITUTED = {"B_a41f4cff9d": "naphthalene+CN", "B_052693bd01": "oxazole+CN", "A_a848c04a21": "phenylacetylene",
               "B_410ac0fb2f": "benzene+NH2+ethynyl", "B_079e66d017": "isoquinoline+CH3", "B_78f8233b4c": "azulene+NH2",
               "B_0603418c5b": "azulene+ethynyl"}
CONSEQUENCE = {
    NONE_BEYOND: "No family is beyond its bar on this molecule. TASKS 211's step (3), the default of 120 minutes, may go to a "
                 "reviewed change, with the certificate's wording unchanged; the numbers are recorded as one substituted data point "
                 "beside the bars, not as a new bar.",
    BEYOND: "At least one family is beyond its bar on this molecule: evidence that the bar understates the step's error here. The "
            "default does not change by this run; the certificate's sentence about what the bars rest on gains the measured number "
            "for a substituted molecule; and the question whether the bars need a substituted target goes to the author with that "
            "number (a new target is label compute). No bar changes.",
    NO_STATEMENT: f"No family has {MIN_BANDS} bands under its bar, so this run makes no statement and the default does not change.",
}


class NotReadError(Exception):
    """The label exists and is not read, for a reason the registration names (a NOISY force field)."""


@dataclass(frozen=True)
class ReadConfig:
    """One read: the pipeline result, the label's G folder and GVPT2 file, and the folder the record goes to."""
    run: Path
    g_dir: Path
    label: Path
    out: Path

    def __post_init__(self) -> None:
        for needed in (self.run / "pipeline.json", self.run / "geometry.json", self.g_dir / "ref.json"):
            if not needed.is_file():
                raise ValueError(f"{needed} is missing")
        refuse_existing(self.out / "label_read.json")


@dataclass(frozen=True)
class Bands:
    """A pipeline result's bands in ascending position: the geometry, the unrounded positions, the mass-weighted modes
    (3N × M), the recorded sticks and the artefact's bars as the run recorded them."""
    symbols: list[str]
    coords: np.ndarray
    omega: np.ndarray
    q: np.ndarray
    sticks: list[dict[str, Any]]
    bars: dict[str, float]


@dataclass(frozen=True)
class Label:
    """A label's modes in the run's frame: positions, GVPT2 shifts, VPT2-domain marks, families, and the distance between the
    label's geometry and the run's after rotation."""
    omega: np.ndarray
    delta: np.ndarray
    marked: np.ndarray
    family: np.ndarray
    q: np.ndarray
    geometry_rms_bohr: float


def refuse_existing(path: Path) -> None:
    """A record is written once; a second read goes to a folder of its own."""
    if path.exists():
        raise ValueError(f"{path} exists: a result is never overwritten")


def load_bands(run: Path) -> Bands:
    """The run's bands, refused where the step was not applied or the recorded spectrum is not the stored Hessians'."""
    record = json.loads((run / "pipeline.json").read_text(encoding="utf-8"))
    spectra = record["spectra"]
    summary = spectra.get("anharmonic") or {}
    if summary.get("status") != AN.POS.APPLIED:
        raise ValueError(f"{run}: the anharmonic step was not applied (status {summary.get('status')!r}), so there is no step to read")
    sticks = sorted(spectra["network"]["sticks"], key=lambda s: s["omega_cm"])
    symbols, coords, masses = AN.geometry(run)
    with np.load(run / P.CORRECTION) as z:
        dH = np.asarray(z["dH"], float)
    omega, q = AN.corrected_modes(AN.low_hessian(run) + dH, masses, sticks)
    return Bands(symbols, coords, omega, q, sticks, dict(summary["artefact"]["bars_cm"]))


def load_label(g_dir: Path, label_file: Path, bands: Bands) -> Label:
    """The label in the run's frame; `NotReadError` for a NOISY field, ValueError for a label that is not this run's."""
    record, why = load_molecule(str(g_dir), str(label_file))
    if record is None:
        if why.startswith(NOISY_REASON):
            raise NotReadError(f"the B3LYP force field in {g_dir} is {why}: it gets no label and part B is not read")
        raise ValueError(f"{g_dir}: {why}")
    if not record["vpt2_checked"]:
        raise ValueError(f"{label_file}: the label predates the VPT2-domain check; relabel with probes/gvpt2_labels.py")
    if json.loads(label_file.read_text(encoding="utf-8")).get("degenerate_pairs"):
        raise ValueError(f"{label_file}: the label names symmetry pairs; the bars count a pair once and this read does not collapse pairs")
    ref = g_dir / "ref.json"
    molecule = json.loads(ref.read_text(encoding="utf-8"))["molecule"]
    frame = frame_onto((molecule["symbols"], np.asarray(molecule["geometry"], float)), (bands.symbols, bands.coords), str(g_dir))
    if len(record["omega"]) != len(bands.omega):
        raise ValueError(f"the label has {len(record['omega'])} modes and the run {len(bands.omega)} bands: not the same molecule")
    return Label(np.asarray(record["omega"], float), np.asarray(record["delta"], float), np.asarray(record["vpt2_marked"], bool),
                 np.asarray(record["family"]), frame.modes(harmonic_modes(str(ref))[1]), frame.rms_bohr)


def not_counted(step: float | None, bar: float | None, label: float | None, marked: bool, reason: str | None) -> str | None:
    """Why a band is outside its family's rms, None when it is in it. A band is in when it is printed with a step and the
    family's bar and the label states a shift for it."""
    if step is None:
        return f"no step: {reason}"
    if label is None:
        return "no label mode matches the band"
    if marked:
        return "the label's mode is outside VPT2's domain"
    if bar is None:
        return "stepped without the family's bar (its error is not measured)"
    return None


def compare(bands: Bands, label: Label) -> list[dict[str, Any]]:
    """Per band, in ascending position: what the run printed, what the label says, and the difference."""
    match = match_sets(bands.omega, bands.q, label.q)
    carried, marked = match.carry(label.delta), match.flagged(label.marked)
    rows = []
    for k, stick in enumerate(bands.sticks):
        block = stick.get("anharmonic") or {}
        step, partner = block.get("delta_anh_cm"), int(match.partner[k])
        shift = float(carried[k]) if np.isfinite(carried[k]) else None
        rows.append({"omega_cm": stick["omega_cm"], "family": block.get("family"), "step_delta_cm": step, "bar_cm": block.get("bar_cm"),
                     "step_reason": block.get("reason"), "label_omega_cm": float(label.omega[partner]) if partner >= 0 else None,
                     "label_family": str(label.family[partner]) if partner >= 0 else None, "label_delta_cm": shift,
                     "label_marked": bool(marked[k]), "label_overlap": round(float(match.overlap[k]), 3),
                     "error_cm": None if step is None or shift is None else step - shift,
                     "not_counted": not_counted(step, block.get("bar_cm"), shift, bool(marked[k]), block.get("reason"))})
    return rows


def family_errors(family: np.ndarray, step: np.ndarray, label: np.ndarray) -> dict[str, dict[str, float]]:
    """Per family present: the number of rows and the rms of step − label, by `s3_read.family_read` — the arithmetic of the
    printed bars, here on one molecule's rows."""
    rows = {"molecule": {"family": np.asarray(family), "truth": np.asarray(label, float), "pred": {AS.MODEL: np.asarray(step, float)}}}
    return {fa: {"n": entry["n"], "rms_cm": entry["per_molecule"]["molecule"][AS.MODEL]} for fa, entry in family_read(rows, {}).items()}


def line_factor(n: int) -> float:
    """The rms of n errors, in units of the bar, that is exceeded LINE_QUANTILE's remainder of the time when the bar is right:
    n independent Gaussian errors with the bar as their standard deviation have n·rms²/bar² chi-square distributed with n degrees
    of freedom, so the line is √(χ²_q(n)/n). 1.32 at n = 12, 1.45 at 6, 1.49 at 5. Errors within one molecule are not
    independent, which makes the true line wider than this one: the statement 'beyond' is, if anything, too eager.
    (`scipy.stats.chi2.ppf`, as scipy/stats/tests/test_distributions.py calls it; pinned here on the tabulated quantiles.)"""
    if n < 1:
        raise ValueError(f"a line for {n} bands: at least one is needed")
    return math.sqrt(float(chi2.ppf(LINE_QUANTILE, n)) / n)


def line_cm(n: int, bar_cm: float) -> float:
    """The family's line for n bands, in cm⁻¹ and at the precision the rms is compared with."""
    return round(bar_cm * line_factor(n), BAR_DECIMALS)


def statement(n: int, rms_cm: float, bar_cm: float) -> str:
    """The registered statement of one family with at least MIN_BANDS bands, on the rms as printed: within the bar; above it and
    at most the line for this n; or beyond the line."""
    if n < MIN_BANDS:
        return NO_STATEMENT
    printed = round(rms_cm, BAR_DECIMALS)
    if printed <= bar_cm:
        return WITHIN
    return CONSISTENT if printed <= line_cm(n, bar_cm) else BEYOND


def judge(rows: list[dict[str, Any]], bars: dict[str, float]) -> dict[str, dict[str, Any]]:
    """Per family with a bar: n and rms over the bands under the bar, the statement, and for information the same over every
    stepped band the label covers (the bands stepped without the bar's claim included)."""
    def errors(chosen: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
        return family_errors(np.array([r["family"] for r in chosen]), np.array([r["step_delta_cm"] for r in chosen], float),
                             np.array([r["label_delta_cm"] for r in chosen], float))

    stepped = [r for r in rows if r["error_cm"] is not None and not r["label_marked"]]
    under_bar, every = errors([r for r in stepped if r["not_counted"] is None]), errors(stepped)
    out = {}
    for fa, bar in bars.items():
        # a family without a band has no rms: None in the record, never NaN, which no JSON reader outside Python accepts
        n, rms_cm = int(under_bar.get(fa, {}).get("n", 0)), under_bar.get(fa, {}).get("rms_cm")
        out[fa] = {"n": n, "rms_cm": rms_cm, "bar_cm": bar, "line_cm": line_cm(n, bar) if n >= MIN_BANDS else None,
                   "statement": NO_STATEMENT if rms_cm is None else statement(n, rms_cm, bar),
                   "n_every_stepped_band": int(every.get(fa, {}).get("n", 0)), "rms_every_stepped_band_cm": every.get(fa, {}).get("rms_cm")}
    return out


def outcome(families: dict[str, dict[str, Any]]) -> str:
    """The molecule's outcome: BEYOND when any family is, NONE_BEYOND when every family with a statement is within its bar or
    consistent with it, and NO_STATEMENT when no family has one."""
    said = [f["statement"] for f in families.values() if f["statement"] != NO_STATEMENT]
    if not said:
        return NO_STATEMENT
    return BEYOND if BEYOND in said else NONE_BEYOND


def cell(value: float | None, digits: int = 1) -> str:
    """A number for a table, a dash where there is none."""
    return "—" if value is None or not math.isfinite(value) else f"{value:.{digits}f}"


def family_lines(families: dict[str, dict[str, Any]]) -> list[str]:
    """The per-family table: rms with n beside the bar, and the statement."""
    lines = ["| family | bands under the bar | rms of step − label (cm⁻¹) | printed bar (cm⁻¹) | 95 % line at this n (cm⁻¹) | statement | "
             "every stepped band: n, rms |", "|---|---|---|---|---|---|---|"]
    for fa, f in families.items():
        lines.append(f"| {fa} | {f['n']} | {cell(f['rms_cm'], 2)} | {f['bar_cm']:.2f} | {cell(f['line_cm'], 2)} | {f['statement']} | "
                     f"{f['n_every_stepped_band']}, {cell(f['rms_every_stepped_band_cm'], 2)} |")
    return lines


def band_lines(rows: list[dict[str, Any]]) -> list[str]:
    """The per-band table."""
    lines = ["| ω (cm⁻¹) | family | step Δ | label Δ | step − label | label ω | overlap | outside the rms because |", "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['omega_cm']:.1f} | {r['family'] or '—'} | {cell(r['step_delta_cm'])} | {cell(r['label_delta_cm'])} | "
                     f"{cell(r['error_cm'])} | {cell(r['label_omega_cm'])} | {r['label_overlap']:.3f} | {r['not_counted'] or ''} |")
    return lines


def mismatch_lines(rows: list[dict[str, Any]]) -> list[str]:
    """The bands whose printed family is not their label mode's: each is judged against the printed family's bar, because that
    is the bar the certificate prints on it, and named here so a reader can see which."""
    other = [r for r in rows if r["family"] is not None and r["label_family"] is not None and r["family"] != r["label_family"]]
    lines = ["## Bands whose printed family differs from the label mode's", ""]
    if not other:
        return [*lines, "None."]
    lines += ["Each is read against the printed family's bar: that is the bar the certificate prints on it.", "",
              "| ω (cm⁻¹) | printed family | label mode's family | step − label |", "|---|---|---|---|"]
    return [*lines, *(f"| {r['omega_cm']:.1f} | {r['family']} | {r['label_family']} | {cell(r['error_cm'])} |" for r in other)]


def report(record: dict[str, Any]) -> list[str]:
    """RESULT.md of a read that was made."""
    harmonic = [r for r in record["bands"] if r["step_delta_cm"] is None]
    lines = ["# The anharmonic step against its label — one substituted molecule", "",
             f"Registration: `{REGISTRATION}`, part B. Run `{record['run']}`; label `{record['label']}` "
             f"(geometry {record['geometry_rms_bohr']:.4f} bohr rms from the run's after rotation).", "",
             f"**Outcome: {record['outcome']}.** {CONSEQUENCE[record['outcome']]}", "", *family_lines(record["families"]), "",
             f"The statement is read on the bands printed with a step and the family's bar, at least {MIN_BANDS} of them; the rms is "
             f"compared as printed, to {BAR_DECIMALS} decimals. The line is the rms that n independent errors with the bar as their "
             f"standard deviation stay under {LINE_QUANTILE:.0%} of the time; with three families judged, about one run in seven "
             "shows a 'beyond' when every bar is right, and errors within a molecule are not independent, so the line is "
             "approximate and, if anything, too narrow. One molecule cannot establish a bar. The printed steps are the record's, "
             "rounded to 0.1 cm⁻¹.", "",
             "## Bands printed harmonic, and what the label says for them", "",
             "| ω (cm⁻¹) | why no step | label Δ (cm⁻¹) | label outside VPT2's domain |", "|---|---|---|---|"]
    lines += [f"| {r['omega_cm']:.1f} | {r['step_reason']} | {cell(r['label_delta_cm'])} | {'yes' if r['label_marked'] else 'no'} |" for r in harmonic]
    return [*lines, "", *mismatch_lines(record["bands"]), "", "## Every band", "", *band_lines(record["bands"])]


def write_record(out: Path, name: str, record: dict[str, Any], markdown: tuple[str, list[str]]) -> None:
    """The JSON record and its reading, each through a temp file."""
    out.mkdir(parents=True, exist_ok=True)
    write_atomic(str(out / name), json.dumps(record, indent=1, ensure_ascii=False))
    write_atomic(str(out / markdown[0]), "\n".join(markdown[1]) + "\n")


def read(cfg: ReadConfig) -> dict[str, Any]:
    """The read's record: per band, per family and the outcome — or, for a NOISY label, that it was not read and why."""
    bands = load_bands(cfg.run)
    head = {"registration": REGISTRATION, "run": cfg.run.as_posix(), "g_dir": cfg.g_dir.as_posix(), "label": cfg.label.as_posix()}
    try:
        label = load_label(cfg.g_dir, cfg.label, bands)
    except NotReadError as e:
        return {**head, "read": False, "reason": str(e)}
    rows = compare(bands, label)
    families = judge(rows, bands.bars)
    return {**head, "read": True, "geometry_rms_bohr": label.geometry_rms_bohr, "min_bands": MIN_BANDS, "bars_cm": bands.bars,
            "families": families, "outcome": outcome(families), "bands": rows}


def group_summary(families_of: list[dict[str, Any]], bars: dict[str, float]) -> dict[str, dict[str, Any]]:
    """Per family, over a group of molecules of the stored read: how many have MIN_BANDS modes or more, how many of those lie
    above the bar and how many beyond their line, the median of their rms, and the rms pooled over every mode of the group."""
    out = {}
    for fa, bar in bars.items():
        have = [f[fa] for f in families_of if fa in f]
        judged = [(f["n"], f["rms_inputs_on_B"]) for f in have if f["n"] >= MIN_BANDS]
        modes = sum(f["n"] for f in have)
        out[fa] = {"molecules_judged": len(judged), "above_the_bar": sum(round(r, BAR_DECIMALS) > bar for _, r in judged),
                   "beyond_the_line": sum(statement(n, r, bar) == BEYOND for n, r in judged),
                   "median_rms_cm": float(np.median([r for _, r in judged])) if judged else None, "modes": modes,
                   "pooled_rms_cm": math.sqrt(math.fsum(f["n"] * f["rms_inputs_on_B"] ** 2 for f in have) / modes) if modes else None}
    return out


def prior(modes_json: Path) -> dict[str, Any]:
    """The substituted training molecules' scaffold-left-out rms per family beside the bars, from the stored read, and the same
    read's unsubstituted molecules as the baseline."""
    stored = json.loads(modes_json.read_text(encoding="utf-8"))["per_molecule"]
    artefact = AS.load_artefact()
    missing = sorted(set(SUBSTITUTED) - set(artefact.header["training_molecules"]) | set(SUBSTITUTED) - set(stored))
    if missing:
        raise ValueError(f"{missing}: not among the artefact's training molecules, or not in {modes_json}")
    bars = AS.bars(artefact)
    molecules = {}
    for mol, name in SUBSTITUTED.items():
        fams = stored[mol]["families"]
        molecules[mol] = {"name": name, "all": {"n": fams[ALL]["n"], "rms_cm": fams[ALL]["rms_inputs_on_B"]},
                          "families": {fa: {"n": fams[fa]["n"], "rms_cm": fams[fa]["rms_inputs_on_B"], "bar_cm": bar,
                                            "statement": statement(fams[fa]["n"], fams[fa]["rms_inputs_on_B"], bar)}
                                       for fa, bar in bars.items() if fa in fams}}
    plain = [m for m in stored if m not in SUBSTITUTED]
    return {"registration": REGISTRATION, "source": modes_json.as_posix(), "quantity": "rms_inputs_on_B", "min_bands": MIN_BANDS,
            "bars_cm": bars, "molecules": molecules,
            "groups": {"substituted": {"molecules": len(SUBSTITUTED), **group_summary([stored[m]["families"] for m in SUBSTITUTED], bars)},
                       "unsubstituted": {"molecules": len(plain), "not_training_molecules": sorted(set(plain) - set(artefact.header["training_molecules"])),
                                         **group_summary([stored[m]["families"] for m in plain], bars)}}}


def prior_report(record: dict[str, Any]) -> list[str]:
    """PRIOR.md: one row per molecule, each family's rms with n, in bold where it lies above the bar with enough modes; then
    the two groups of the read side by side."""
    bars = record["bars_cm"]
    lines = ["# Substituted training molecules: the step's scaffold-left-out error beside the printed bars", "",
             f"Registration: `{REGISTRATION}`, section 5 (descriptive; no run). Source: `{record['source']}`, `per_molecule`, "
             f"`{record['quantity']}`: x2* fitted without the molecule's scaffold, against the molecule's B3LYP GVPT2 label; rms in "
             f"cm⁻¹ with the number of modes. Bold: above the bar with at least {record['min_bands']} modes.", "",
             "| molecule | id | " + " | ".join(bars) + " | all |", "|---|---|" + "---|" * (len(bars) + 1)]
    for mol, m in record["molecules"].items():
        cells = []
        for fa in bars:
            f = m["families"].get(fa)
            text = "—" if f is None else f"{f['rms_cm']:.2f} ({f['n']})"
            cells.append(f"**{text}**" if f is not None and f["statement"] in (CONSISTENT, BEYOND) else text)
        lines.append(f"| {m['name']} | {mol} | " + " | ".join(cells) + f" | {m['all']['rms_cm']:.2f} ({m['all']['n']}) |")
    lines.append("| printed bar | | " + " | ".join(f"{b:.2f}" for b in bars.values()) + " | |")
    groups = record["groups"]
    lines += ["", "## Beside the unsubstituted molecules of the same read", "",
              f"Molecules with at least {record['min_bands']} modes in the family: how many lie above the printed bar, how many beyond the "
              f"{LINE_QUANTILE:.0%} line for their number of modes, the median of their rms, and the rms pooled over every mode of the "
              f"group. Unsubstituted: {groups['unsubstituted']['molecules']} molecules, the bare ring systems of the training table and "
              f"{', '.join(groups['unsubstituted']['not_training_molecules']) or 'no other'} (a target, fitted on all training molecules).", "",
              "| family | bar | substituted: above / beyond / of | median | pooled | unsubstituted: above / beyond / of | median | pooled |",
              "|---|---|---|---|---|---|---|---|"]
    for fa, bar in bars.items():
        s, u = groups["substituted"][fa], groups["unsubstituted"][fa]
        lines.append(f"| {fa} | {bar:.2f} | " + " | ".join(
            f"{g['above_the_bar']} / {g['beyond_the_line']} / {g['molecules_judged']} | {cell(g['median_rms_cm'], 2)} | {cell(g['pooled_rms_cm'], 2)}"
            for g in (s, u)) + " |")
    return [*lines, "", "The substituted molecules were in the fit of every scaffold but their own, and the bars were measured on two other "
            "molecules: the table says which outcome to expect of an unseen substituted molecule, it is not that measurement."]


def main(argv: list[str] | None = None) -> int:
    """Command line. Exit 0 after a read or the prior table, 3 when the label is not read (NOISY)."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="command", required=True)
    r = sub.add_parser("read", help="a pipeline result's printed steps against the molecule's label")
    r.add_argument("--run", type=Path, required=True)
    r.add_argument("--g-dir", type=Path, required=True)
    r.add_argument("--label", type=Path, required=True)
    p = sub.add_parser("prior", help="the substituted training molecules' stored errors beside the bars")
    p.add_argument("--modes-json", type=Path, required=True)
    for parser in (r, p):
        parser.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.command == "prior":
        refuse_existing(a.out / "prior.json")
        record = prior(a.modes_json)
        write_record(a.out, "prior.json", record, ("PRIOR.md", prior_report(record)))
        print("\n".join(prior_report(record)), flush=True)
        return 0
    record = read(ReadConfig(a.run, a.g_dir, a.label, a.out))
    if not record["read"]:
        write_record(a.out, "label_read.json", record, ("RESULT.md", ["# The anharmonic step against its label — not read", "",
                                                                      f"Registration: `{REGISTRATION}`, part B.", "", record["reason"]]))
        print(f"NOT READ: {record['reason']}", flush=True)
        return 3
    write_record(a.out, "label_read.json", record, ("RESULT.md", report(record)))
    print("\n".join(report(record)[:12]), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
