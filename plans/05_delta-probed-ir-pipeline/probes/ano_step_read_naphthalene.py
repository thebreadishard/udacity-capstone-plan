"""ANO test, second molecule: does the ano-pVQZ MP2 step lift naphthalene's out-of-plane modes as it lifted benzene's? (TASKS 300;
`GoalGathering/notes/PreRegistration_2026-11-26_ANO_Step_Naphthalene.md`)

The composite Hessian is CCSD(T)/cc-pVDZ + (MP2/X − MP2/cc-pVDZ) at the corpus geometry, with X = cc-pVTZ (the control, from the
DF-MP2 rows we hold) and X = ano-pVQZ (the run's rows). No published CCSD(T) force field of naphthalene is known to us, so the
counterpart is the measured fundamentals (Martin, El-Yazal & François 1996): a harmonic frequency belongs above its fundamental, and
today's composite puts three out-of-plane ones 16–33 cm⁻¹ below. Frequencies are read as computed — the first-order geometry term
is not applied (no force field of naphthalene at the corpus level, no CCSD(T)/cc-pVTZ gradient) — and every outcome says so.
Modes are named by their D2h species from the mode vectors and paired with the measured ones by frequency order inside a species,
as `fundamentals_vs_experiment.py` does.

    python probes/ano_step_read_naphthalene.py <run dir> <out prefix> [--partial]

<run dir> holds rows_mp2_anopvqz.npz and rows_mp2_anopvqz_fit5z.npz. `--partial` reads the control alone while they are missing.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import ano_step_read as A  # noqa: E402  (probes are scripts, not a package)
import cc_composite_full_check as CCF  # noqa: E402
import fundamentals_vs_experiment as F  # noqa: E402

R1 = PLAN / "probes" / "results_m1"
N_FROZEN = 10
ANO = "mp2_anopvqz"
OUT_OF_PLANE = ("Au", "B1g", "B2g", "B3u")       # Martin's labelling: x normal to the plane
CH_STRETCH_ABOVE_CM = 3000.0
JUDGED_ABOVE_CM = 300.0         # the two butterfly modes below (176, 195) are reported, not judged: a fundamental there may lie above
BELOW_LINE = 5.0                # TRANSFERS: no judged out-of-plane harmonic more than this below its fundamental
KEY_MODE = ("B2g", 770.0)       # the ring-puckering mode, benzene's ω4 in naphthalene: 33.0 below its fundamental today
RISE_LINE = 20.0                # TRANSFERS: the key mode rises by at least this from the control
NO_RISE_LINE = 10.0             # NO TRANSFER: it rises by less than this
CONTROL_PINS = {("B2g", 770.0): -33.0, ("B2g", 980.0): -17.1, ("Au", 970.0): -15.6}    # the read of 19 Nov, harmonic minus fundamental
CONTROL_LINE = 0.5              # the DF-MP2 control repeats each pin this well (the DF swap of 20 Oct: largest change 0.46)
OVERLAP_LINE = 0.5              # a judged pair whose control and ano-pVQZ mode vectors overlap² less is named: not the same mode
HELD_LEVELS = {"dz": A.RowLevel("cc-pvdz", "mp2", "cc-pvdz-jkfit", "cc-pvdz-ri", frozen=N_FROZEN),
               "tz": A.RowLevel("cc-pvtz", "mp2", "cc-pvtz-jkfit", "cc-pvtz-ri", frozen=N_FROZEN)}
ANO_LEVEL = A.RowLevel("ano-pvqz", "mp2", "cc-pvqz-jkfit", "cc-pvqz-ri", frozen=N_FROZEN)
GEOMETRY_NOTE = ("read as computed at the B3LYP geometry, without the geometry term (on benzene that term moves a C–H wag by up to "
                 "about 20 cm⁻¹ down), so a C–H wag's place above its fundamental is flattered here")

Key = tuple[str, float]


@dataclass(frozen=True)
class Inputs:
    """What the read takes from earlier work: naphthalene's corpus record, CCSD(T)/cc-pVDZ Hessian and DF-MP2 rows."""
    corpus: Path = F.MOLECULES / "A_01f3186607"
    cc_dz: Path = R1 / "e8_naphthalene_ccpvdz_tlambda_2026-10-02" / "hessian_ccsd_t.npz"
    mp2_dz: Path = R1 / "dfmp2_composite_2026-10-19" / "dfmp2_rows_naphthalene_ccpvdz.npz"
    mp2_tz: Path = R1 / "dfmp2_composite_2026-10-19" / "dfmp2_rows_naphthalene_ccpvtz.npz"


@dataclass(frozen=True)
class Held:
    """The molecule and the parts every composite shares."""
    sym: list[str]
    x0: np.ndarray
    masses: np.ndarray
    cc_dz: np.ndarray
    mp2_dz: np.ndarray
    mp2_tz: np.ndarray
    spread: dict[str, float]
    psi4: dict[str, str]


def load_held(inputs: Inputs) -> Held:
    """The corpus geometry, the CCSD(T)/cc-pVDZ Hessian at it and the two DF-MP2 Hessians we hold; a file that is not what its
    place says (level, frozen orbitals, geometry, an invalid CC Hessian) is refused."""
    sym, x0, masses = CCF.load_geometry(inputs.corpus / "geometry.json")
    with np.load(inputs.cc_dz) as z:
        cc, at = np.asarray(z["H_raw"], float), np.asarray(z["coords_bohr"], float).reshape(-1, 3)
        told = (str(z["status"]), str(z["basis"]).lower(), int(z["frozen"]))
    if told != ("VALID", "cc-pvdz", N_FROZEN) or np.abs(at - x0).max() > CCF.FRAME_TOL_BOHR:
        raise SystemExit(f"{inputs.cc_dz}: holds {told}, expected a VALID cc-pvdz Hessian with {N_FROZEN} frozen orbitals at the "
                         "corpus geometry")
    M, spread, psi4 = {}, {}, {}
    for basis, path in (("dz", inputs.mp2_dz), ("tz", inputs.mp2_tz)):
        psi4[path.name] = A.check_row_file(path, HELD_LEVELS[basis])
        M[basis], _, spread[path.name] = CCF.rows_in_frame(str(path), None, sym, x0)
    return Held(sym, x0, masses, cc, M["dz"], M["tz"], spread, psi4)


def experiment() -> dict[Key, F.Exp]:
    """The measured fundamentals by (species, wavenumber); two of one species at one wavenumber would make the key ambiguous."""
    listed = F.naphthalene_experiment()
    out = {(e.irrep, e.nu): e for e in listed}
    if len(out) != len(listed):
        raise SystemExit("two measured fundamentals of one species at the same wavenumber: the modes cannot be named by them")
    return out


@dataclass(frozen=True)
class Named:
    """One composite's modes by (species, measured wavenumber): harmonic frequency, columns of V, possible-crossing flag."""
    freq: dict[Key, float]
    idx: dict[Key, tuple[int, ...]]
    crossing: dict[Key, bool]
    V: np.ndarray


def harmonic(held: Held, mp2_large: np.ndarray) -> Named:
    """The composite's modes named by the measured fundamentals. Raises `A.Unreadable` for an imaginary mode and for modes that
    do not sort into naphthalene's species; a Hessian with a value that is not finite is refused outright."""
    H = held.cc_dz + mp2_large - held.mp2_dz
    if not np.isfinite(H).all():
        raise SystemExit("a composite Hessian holds a value that is not finite: a damaged row file")
    H = CCF.project_tr(H, held.masses, held.x0)[0]
    _, freq, V, _ = F.normal_modes(H, held.masses)
    if freq.min() <= 0.0:
        raise A.Unreadable(f"an imaginary mode ({freq.min():.1f} cm⁻¹)")
    try:
        labels, _ = F.d2h_irreps(V, freq, held.sym, held.x0)
        pairs = F.pair_by_irrep(F.groups(freq, labels), list(experiment().values()))
    except ValueError as why:
        raise A.Unreadable(str(why)) from why
    keys = [(e.irrep, e.nu) for _, e, _ in pairs]
    return Named(dict(zip(keys, (g.freq for g, _, _ in pairs), strict=True)), dict(zip(keys, (g.idx for g, _, _ in pairs), strict=True)),
                 dict(zip(keys, (bool(flag) for _, _, flag in pairs), strict=True)), V)


def mode_rows(control: Named, ano: Named | None) -> list[dict]:
    """One row per measured fundamental: harmonic minus fundamental for the control and for the ano-pVQZ step, the rise, and the
    overlap² of the two recipes' mode vectors — pairing by order names a mode in each recipe apart, the overlap says whether the
    two are one mode."""
    rows = []
    for irrep, nu in sorted(control.freq, key=lambda key: key[1]):
        key, oop = (irrep, nu), irrep in OUT_OF_PLANE
        row = {"irrep": irrep, "nu": nu, "out_of_plane": oop, "judged": oop and nu > JUDGED_ABOVE_CM,
               "control": control.freq[key] - nu, "ano": None, "rise": None, "overlap": None, "crossing": control.crossing[key]}
        if ano is not None:
            row |= {"ano": ano.freq[key] - nu, "rise": ano.freq[key] - control.freq[key],
                    "overlap": F.subspace_overlap(control.V, control.idx[key], ano.V, ano.idx[key]),
                    "crossing": control.crossing[key] or ano.crossing[key]}
        rows.append(row)
    return rows


def control_misses(rows: list[dict]) -> dict[str, float]:
    """The pinned modes the control does not repeat within the line: 'species wavenumber' → the control's value."""
    by_key = {(r["irrep"], r["nu"]): r["control"] for r in rows}
    return {f"{irrep} {nu:.0f}": by_key[(irrep, nu)] for (irrep, nu), pin in CONTROL_PINS.items()
            if abs(by_key[(irrep, nu)] - pin) > CONTROL_LINE}


def outcome(rows: list[dict]) -> tuple[str, str]:
    """The registered outcome from the ano-pVQZ rows, compared on unrounded values."""
    judged = [r for r in rows if r["judged"]]
    if not judged or any(r["ano"] is None for r in judged):
        raise ValueError("no ano-pVQZ reading of the judged modes: there is nothing to judge")
    key = next(r for r in rows if (r["irrep"], r["nu"]) == KEY_MODE)
    rise, lowest = key["rise"], min(judged, key=lambda r: r["ano"])
    what = (f"the {KEY_MODE[0]} mode at {KEY_MODE[1]:.0f} rises by {rise:+.1f} cm⁻¹ (overlap² of its two mode vectors "
            f"{key['overlap']:.2f}); the lowest judged out-of-plane harmonic is "
            f"{lowest['ano']:+.1f} from its fundamental ({lowest['irrep']} {lowest['nu']:.0f})")
    if rise < NO_RISE_LINE:
        return "NO TRANSFER", f"{what}; a rise under {NO_RISE_LINE} is not benzene's effect"
    if rise >= RISE_LINE and lowest["ano"] >= -BELOW_LINE:
        return "TRANSFERS", f"{what}; rise at or over {RISE_LINE} and no judged mode more than {BELOW_LINE} below its fundamental"
    return "BETWEEN", f"{what}; lines: rise at or over {RISE_LINE} and no judged mode more than {BELOW_LINE} below"


def caveats(rows: list[dict], fitting: dict | None) -> list[str]:
    """What stands under any outcome."""
    out = [GEOMETRY_NOTE]
    if fitting is not None and not fitting["under_line"]:
        out.append(f"the fitting check is over its line of {A.FITTING_LINE:.0e} E_h/bohr² ({fitting['largest_change']:.1e})")
    other = [f"{r['irrep']} {r['nu']:.0f} ({r['overlap']:.2f})" for r in rows if r["judged"] and r["overlap"] < OVERLAP_LINE]
    if other:
        out.append(f"the two recipes' mode vectors overlap² under {OVERLAP_LINE} — the rise there compares two different modes: "
                   + ", ".join(other))
    crossed = [f"{r['irrep']} {r['nu']:.0f}" for r in rows if r["judged"] and r["crossing"]]
    if crossed:
        out.append("possible crossings inside a species (neighbours within "
                   f"{F.CROSSING_CM:.0f} cm⁻¹), where pairing by order may swap two modes: " + ", ".join(crossed))
    return out


def verdict(rows: list[dict], absent: str | None, unread: str | None, fitting: dict | None) -> tuple[str, str]:
    """The control first, then missing files, then an unreadable Hessian, then the registered lines with what stands under them."""
    misses = control_misses(rows)
    if misses:
        return "CONTROL FAILED", ("the control does not repeat the read of 19 Nov within "
                                  f"{CONTROL_LINE} cm⁻¹: " + ", ".join(f"{k} {v:+.2f}" for k, v in misses.items()))
    if absent:
        return "PARTIAL", f"the control alone: {absent}"
    if unread:
        return "NO OUTCOME", f"the ano-pVQZ composite cannot be read: {unread}"
    word, why = outcome(rows)
    return word, "; ".join([why, *caveats(rows, fitting)])


def run_files(run: Path, partial: bool) -> str | None:
    """Why the run's rows cannot be read yet, or None; without `partial` a missing or unfinished file stops the read."""
    found = [p for p in (A.file_problem(run, ANO), A.file_problem(run, ANO + A.FIT_SUFFIX)) if p]
    if found and not partial:
        raise SystemExit(f"{run}: " + "; ".join(found) + " (--partial reads the control alone, without an outcome)")
    return "; ".join(found) or None


def read(run: Path, inputs: Inputs, partial: bool) -> dict:
    """The whole read as one record."""
    held = load_held(inputs)
    absent = run_files(run, partial)
    try:
        control = harmonic(held, held.mp2_tz)
    except A.Unreadable as why:
        raise SystemExit(f"the control composite cannot be read: {why}") from why
    ano, unread, fitting = None, None, None
    spread, psi4 = dict(held.spread), dict(held.psi4)
    if not absent:
        path = A.row_path(run, ANO)
        psi4[path.name] = A.check_row_file(path, ANO_LEVEL)
        M, _, spread[path.name] = CCF.rows_in_frame(str(path), None, held.sym, held.x0)
        fitting = A.fitting_change(run, ANO, held.x0, ANO_LEVEL)
        try:
            ano = harmonic(held, M)
        except A.Unreadable as why:
            unread = str(why)
    rows = mode_rows(control, ano)
    word, sentence = verdict(rows, absent, unread, fitting)
    return {"run": str(run), "modes": rows, "fitting": fitting,
            "symmetry_spread": spread, "psi4": psi4, "outcome": word, "sentence": sentence}


def _cell(value: float | None) -> str:
    return "—" if value is None else f"{value:+.2f}"


def _shift_summary(rows: list[dict]) -> list[str]:
    """The in-plane modes' rise per group, reported and not judged."""
    out = []
    groups = {"C–H stretch": [r for r in rows if not r["out_of_plane"] and r["nu"] > CH_STRETCH_ABOVE_CM],
              "other in plane": [r for r in rows if not r["out_of_plane"] and r["nu"] <= CH_STRETCH_ABOVE_CM]}
    for name, members in groups.items():
        rises = np.array([r["rise"] for r in members if r["rise"] is not None])
        if rises.size:
            out.append(f"- In plane, {name} ({rises.size} modes), ano-pVQZ minus control: mean {rises.mean():+.2f}, rms "
                       f"{np.sqrt(np.mean(rises ** 2)):.2f}, largest {rises[np.argmax(np.abs(rises))]:+.2f} cm⁻¹ (not judged: against "
                       "fundamentals a few cm⁻¹ in plane cannot be read).")
    return out


def report(record: dict) -> str:
    """The record as the note that is kept."""
    lines = ["# ANO test on naphthalene: the read", "",
             f"Rows from `{record['run']}`. Registration: `GoalGathering/notes/PreRegistration_2026-11-26_ANO_Step_Naphthalene.md`. "
             "Harmonic frequency of the composite minus the measured fundamental, cm⁻¹, as computed (no geometry term). The lines "
             "are compared on unrounded values.", "",
             "| species | measured | control (cc-pVTZ step) | ano-pVQZ step | rise | overlap² | judged | flag |",
             "|---|---|---|---|---|---|---|---|"]
    lines += [f"| {r['irrep']} | {r['nu']:.0f} | {_cell(r['control'])} | {_cell(r['ano'])} | {_cell(r['rise'])} | "
              f"{'—' if r['overlap'] is None else format(r['overlap'], '.2f')} | "
              f"{'yes' if r['judged'] else 'no'} | {'crossing?' if r['crossing'] else ''} |" for r in record["modes"] if r["out_of_plane"]]
    lines += ["", *_shift_summary(record["modes"])]
    pins = {f"{i} {nu:.0f}": pin for (i, nu), pin in CONTROL_PINS.items()}
    lines.append(f"- Control pins (19 Nov, line {CONTROL_LINE}): " + ", ".join(f"{k} {v:+.1f}" for k, v in pins.items()) + ".")
    if record["fitting"]:
        f = record["fitting"]
        lines.append(f"- Fitting check: with cc-pV5Z fitting sets the first row's largest change of any element is "
                     f"{f['largest_change']:.1e} E_h/bohr² ({'under' if f['under_line'] else 'NOT under'} the line {A.FITTING_LINE:.0e}).")
    lines.append("- psi4 that made the rows: " + ", ".join(f"{k} {v}" for k, v in sorted(record["psi4"].items())) + ".")
    lines.append("- Symmetry spread of the rows (a.u.): " + ", ".join(f"{k} {v:.1e}" for k, v in sorted(record["symmetry_spread"].items())) + ".")
    lines += ["", f"**Outcome: {record['outcome']}** — {record['sentence']}.", ""]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("run", type=Path, help="folder with rows_mp2_anopvqz.npz and its _fit5z file")
    parser.add_argument("out_prefix", help="writes <out_prefix>.md and .json")
    parser.add_argument("--partial", action="store_true", help="read the control alone while the run's rows are missing; no outcome")
    a = parser.parse_args(argv)
    record = read(a.run, Inputs(), a.partial)
    text = report(record)
    CCF.write_text(Path(f"{a.out_prefix}.md"), text)
    CCF.write_text(Path(f"{a.out_prefix}.json"), json.dumps(record, indent=1, ensure_ascii=False))
    sys.stdout.buffer.write(text.encode("utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
