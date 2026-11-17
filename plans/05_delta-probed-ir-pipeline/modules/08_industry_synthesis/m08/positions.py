"""Which position a page prints, said once (TASKS 211; PreRegistration_2026-11-14_Printed_Band_Position.md).

The pipeline prints a band at its best estimate: the anharmonic position ν = ω + Δ_anh where the anharmonic step applies, the
harmonic position ω where it does not. Three statements about such a band must never be read as one:

- the **licence** (decision 65) is a claim about the harmonic position ω of the ΔH-corrected Hessian against the DFT proxy (ωB97X);
- the **bar beside a step** is the step's error and nothing more: the rms of Δ_anh against its B3LYP VPT2 label over a family's
  target modes. It is not the error of ν: ν carries ω's error too, and neither is an error against experiment;
- the **anharmonic position ν** carries no licence at all, and the bars rest on two target molecules.

Every sentence a certificate or a page prints about positions is built here, from the pipeline record's own fields, so that the
live certificate, the export certificate, the demo and show pages and the request officer cannot say different things.
"""
from __future__ import annotations

APPLIED, NOT_APPLIED, RUNNING = "applied", "not applied", "running"
ANHARMONIC, HARMONIC = "anharmonic ν", "harmonic ω"
LICENCE_SCOPE = ("the licence (decision 65) is on the harmonic position ω against the DFT proxy (ωB97X); it says nothing about the "
                 "anharmonic position ν")
NO_LICENCE_FOR_NU = "no licence is claimed for ν"
BAR_HEADER = "± of Δ_anh, against its VPT2 label (measured, not licensed)"
NU_ERROR = ("the bar beside a step is the step's error alone — the rms of Δ_anh against its B3LYP VPT2 label — and not the error of "
            "ν: ν carries ω's error too, the harmonic position's error against the DFT proxy (ωB97X), which is what the licence is "
            "about; neither of the two is an error against experiment")
BEFORE_THE_STEP = "the result was computed by a pipeline version before the anharmonic step (0.11)"
SWITCHED_OFF = ("the step exists and was not run: it is off unless the run names a time budget, and `--anharmonic-minutes 120` "
                "switches it on (TASKS 211)")
CATALOGUE = ("positions are harmonic (ω): a catalogue record carries no anharmonic step; the pipeline (m08/pipeline.py) prints the "
             "anharmonic estimate ν = ω + Δ_anh for a molecule it computes, and claims no licence for it")
DRAWN = ("curves are drawn at the harmonic positions ω, so that the network, B3LYP and ωB97X are compared like with like; the "
         "certificate lists each band's anharmonic estimate ν beside its ω")
PIPELINE = ("the pipeline prints each band at its best estimate — the anharmonic position ν = ω + Δ_anh where its anharmonic step "
            f"applies, the harmonic ω where it does not — and says which; {LICENCE_SCOPE}")
SECOND_DELIVERY = ("per band the anharmonic estimate ν = ω + Δ_anh beside ω, with the step's error bar (the rms of Δ_anh against its "
                   "VPT2 label), from the molecule's GFN2-xTB force field and the model x2*")


def of_certificate(cert: dict) -> str:
    """A live certificate's sentence about the positions it prints; a certificate stored before the step existed printed
    harmonic positions, and that is what is said of it."""
    return cert["positions"]["note"] if "positions" in cert else note(summary_of({}))


def summary_of(spectra: dict) -> dict:
    """The anharmonic step's summary in a pipeline record's spectra, or — for a record written before the step existed — the
    statement that it was not applied and why."""
    return spectra.get("anharmonic") or {"status": NOT_APPLIED, "reason": BEFORE_THE_STEP}


RESUME = "python -m m08.anharmonic <result folder>"


def timed_out(minutes: float) -> str:
    """The reason of a step that was stopped at its time budget, with what is kept of it and the command that takes it up."""
    return (f"the anharmonic step did not finish within {minutes:g} minutes; the force field's finished Hessians are kept in the "
            f"result's anharmonic/xtb, and `{RESUME}` takes the step up from them")


def note(summary: dict) -> str:
    """The sentence about the whole spectrum's positions, true in each of the three states of a result: the first delivery while
    the step runs, the step applied, the step not applied (it replaces HARMONIC_NOTE)."""
    if summary["status"] == RUNNING:
        return (f"positions are harmonic (ω) in this first delivery: the anharmonic step is running, with a time budget of "
                f"{summary['budget_minutes']:g} minutes — final by {summary['final_by']}; when the step finishes, this certificate is "
                f"written again and adds {SECOND_DELIVERY}; if the step fails, runs out of time or is interrupted, the certificate is "
                f"finalised with these harmonic positions and the reason; and if this text still stands after {summary['final_by']}, "
                "the run was stopped from outside and this harmonic certificate is the final one")
    if summary["status"] != APPLIED:
        return f"positions are harmonic (ω): the anharmonic step was not applied — {summary['reason']}"
    counts = summary["bands"]
    total = counts["stepped"] + sum(counts["no_step"].values())
    flagged = (f"; for {counts['error_not_measured']} of them the step's error is not measured for that kind of mode, and no bar is printed"
               if counts["error_not_measured"] else "")
    return (f"each band is printed at its best estimate — the anharmonic position ν = ω + Δ_anh for {counts['stepped']} of {total} bands "
            f"(Δ_anh from the model {summary['model']} on the molecule's GFN2-xTB force field{flagged}), the harmonic position ω for the "
            f"other {total - counts['stepped']}, each with its reason; ω stands beside every ν; {LICENCE_SCOPE}; {NO_LICENCE_FOR_NU}")


def _both(names: list[str]) -> str:
    return " and ".join(names) if len(names) <= 2 else ", ".join(names[:-1]) + " and " + names[-1]


FIELD_SCATTER = ("The bars were measured with one stored force field per molecule; between two GFN2-xTB force fields of the same "
                 "molecule the step itself also varies, by 1.7 cm⁻¹ on a C–H stretch pair in the one case measured (benzene, "
                 "17 Nov 2026), and the bars do not contain that")


def targets_sentence(artefact: dict) -> str:
    """What the bars rest on, from the artefact's own record in the step's summary: the target molecules and what they are made
    of, each family's number of target modes, each target's rms, and the registration's two cautions (section 3: the bars are
    thin; nothing says the step helps a molecule unlike the targets)."""
    families = artefact["targets"]
    names = sorted({t for f in families.values() for t in f["per_target_rms_cm"]})
    made_of = set(artefact["target_composition"].values())
    kind = "hydrocarbons" if made_of == {"C,H"} else f"molecules of {_both(sorted(made_of))}"
    rows = ", ".join(f"{fa} {f['rows']}" for fa, f in families.items())
    per = "; ".join(f"{fa} " + " / ".join(f"{f['per_target_rms_cm'][t]:.2f}" for t in names) for fa, f in families.items())
    worst = {max(f["per_target_rms_cm"], key=f["per_target_rms_cm"].get) for f in families.values()}
    carries = f"; {worst.pop()} carries the larger error in every family" if len(worst) == 1 else ""
    return (f"the bars rest on {len(names)} target molecules, {_both(names)}, {'both' if len(names) == 2 else 'all'} {kind} — "
            f"target modes: {rows}; the step's rms per "
            f"molecule, {' / '.join(names)}, in cm⁻¹: {per}{carries}. They are the best numbers there are and they are thin: nothing "
            "here says the step helps a molecule unlike the targets, and a bar is a family's rms, not a prediction interval for one band. "
            + FIELD_SCATTER)


def seen_sentence(summary: dict) -> str:
    """Whether the anharmonic model has seen the molecule — its own statement, apart from the ΔH network's. For a molecule in the
    model's training table the bar is not an out-of-sample error, and the sentence says so."""
    seen, model = summary["seen"], summary["model"]
    n = summary["artefact"]["training_molecules"]
    if seen["role"] == "training":
        return (f"the anharmonic model {model} has this molecule in its training table ({seen['id']}, one of {n}): for this molecule "
                "the step's bar is not an out-of-sample error")
    if seen["role"] == "target":
        return f"this molecule ({seen['id']}) is one of the targets {model}'s bars were measured on; it is not in its training table"
    if seen["role"] == "unseen":
        return f"the anharmonic model {model} has not seen this molecule: it is neither in its training table ({n} molecules) nor a target"
    return f"whether the anharmonic model {model} has seen this molecule is not known: the record names no SMILES"


def composition_sentence(summary: dict) -> str | None:
    """The sentence a certificate adds when the model's training table holds few molecules of this molecule's elements; None
    where it holds enough."""
    c = summary["composition"]
    if not c["few"]:
        return None
    targets = _both(sorted(set(c["targets"].values())))
    return (f"the training table of {summary['model']} holds {c['training_molecules']} of {c['of']} molecules made of this molecule's "
            f"elements ({c['elements']}): few, and the targets the bars were measured on are made of {targets}")


def cautions(summary: dict) -> dict[str, str | None]:
    """The certificate-level sentences of a result with the step, each said once: what the bar is and what ν's error is, what the
    bars rest on, whether the model has seen the molecule, and — where it applies — how thin its elements are in the table."""
    if summary["status"] != APPLIED:
        return {}
    return {"nu_error": NU_ERROR, "targets": targets_sentence(summary["artefact"]), "seen": seen_sentence(summary),
            "composition": composition_sentence(summary)}


def band(stick: dict, summary: dict, reason_text: dict[str, str], not_measured_text: str) -> dict:
    """What one band's line says of its position, from the stick the pipeline recorded and the step's summary (`summary_of`): the
    printed position and which it is, the step and the step's bar, and the sentence. `reason_text` and `not_measured_text` are the
    step's own wordings (probes/anharmonic_step.py), passed in so that this module needs none of the step's code.

    The bar is the step's (`step_bar_cm`), never ν's. A band whose step's error was not measured carries no bar in the record
    and prints none."""
    a = stick.get("anharmonic") if summary["status"] == APPLIED else None
    if a is None or a["delta_anh_cm"] is None:
        if summary["status"] == RUNNING:
            code, why = RUNNING, "the step is still running (first delivery)"
        elif summary["status"] != APPLIED:
            code, why = NOT_APPLIED, f"the step was not applied to this molecule — {summary['reason']}"
        elif a is None:
            raise ValueError(f"the band at {stick['omega_cm']} cm⁻¹ has no anharmonic block although the step was applied")
        else:
            code, why = a["reason"], reason_text[a["reason"]]
        return dict(printed_cm=stick["omega_cm"], printed=HARMONIC, nu_cm=None, delta_anh_cm=None, step_bar_cm=None,
                    step_error_measured=None, step_family=a["family"] if a else None, no_step_reason=code,
                    position_note=f"harmonic position, no anharmonic step: {why}")
    measured = not a["error_not_measured"]
    if measured != (a["bar_cm"] is not None):
        raise ValueError(f"the band at {stick['omega_cm']} cm⁻¹ carries a bar that was not measured for it, or lacks its measured one")
    sentence = (f"anharmonic estimate ν = ω + Δ_anh; the step's error is ± {a['bar_cm']} cm⁻¹ (rms of Δ_anh against its VPT2 label, "
                f"family {a['family']}); {NO_LICENCE_FOR_NU}" if measured else
                f"anharmonic estimate ν = ω + Δ_anh, printed without an error bar: {not_measured_text}; {NO_LICENCE_FOR_NU}")
    return dict(printed_cm=stick["nu_cm"], printed=ANHARMONIC, nu_cm=stick["nu_cm"], delta_anh_cm=a["delta_anh_cm"],
                step_bar_cm=a["bar_cm"], step_error_measured=measured, step_family=a["family"], no_step_reason=None, position_note=sentence)
