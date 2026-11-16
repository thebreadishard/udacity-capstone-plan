"""Which position a page prints, said once (TASKS 211; PreRegistration_2026-11-14_Printed_Band_Position.md).

The pipeline prints a band at its best estimate: the anharmonic position ν = ω + Δ_anh where the anharmonic step applies, the
harmonic position ω where it does not. Two statements about such a band must never be read as one:

- the **licence** (decision 65) is a claim about the harmonic position ω of the ΔH-corrected Hessian against the DFT proxy (ωB97X);
- the **anharmonic position ν** carries no licence at all: its stated uncertainty is the measured rms of the band's mode family on
  two molecules, and for one kind of mode not even that was measured.

Every sentence a certificate or a page prints about positions is built here, from the pipeline record's own fields, so that the
live certificate, the export certificate, the demo and show pages and the request officer cannot say different things.
"""
from __future__ import annotations

APPLIED, NOT_APPLIED = "applied", "not applied"
ANHARMONIC, HARMONIC = "anharmonic ν", "harmonic ω"
MODEL_TARGETS = "coronene and tetracene"         # the two molecules every bar was measured on (the registration, section 3)
LICENCE_SCOPE = ("the licence (decision 65) is on the harmonic position ω against the DFT proxy (ωB97X); it says nothing about the "
                 "anharmonic position ν")
NO_LICENCE_FOR_NU = (f"no licence is claimed for ν: its uncertainty is the rms of the band's family measured on {MODEL_TARGETS}, "
                     "stated, not licensed, and not a prediction interval for one band")
BEFORE_THE_STEP = "the result was computed by a pipeline version before the anharmonic step (0.11)"
SWITCHED_OFF = "switched off (--no-anharmonic)"
CATALOGUE = ("positions are harmonic (ω): a catalogue record carries no anharmonic step; the pipeline (m08/pipeline.py) prints the "
             "anharmonic estimate ν = ω + Δ_anh for a molecule it computes, and claims no licence for it")
DRAWN = ("curves are drawn at the harmonic positions ω, so that the network, B3LYP and ωB97X are compared like with like; the "
         "certificate lists each band's anharmonic estimate ν beside its ω")


PIPELINE = ("the pipeline prints each band at its best estimate — the anharmonic position ν = ω + Δ_anh where its anharmonic step "
            f"applies, the harmonic ω where it does not — and says which; {LICENCE_SCOPE}")


def of_certificate(cert: dict) -> str:
    """A live certificate's sentence about the positions it prints; a certificate stored before the step existed printed
    harmonic positions, and that is what is said of it."""
    return cert["positions"]["note"] if "positions" in cert else note(summary_of({}))


def summary_of(spectra: dict) -> dict:
    """The anharmonic step's summary in a pipeline record's spectra, or — for a record written before the step existed — the
    statement that it was not applied and why."""
    return spectra.get("anharmonic") or {"status": NOT_APPLIED, "reason": BEFORE_THE_STEP}


def note(summary: dict) -> str:
    """The sentence about the whole spectrum's positions, true whether the step was applied or not (it replaces HARMONIC_NOTE)."""
    if summary["status"] != APPLIED:
        return f"positions are harmonic (ω): the anharmonic step was not applied — {summary['reason']}"
    counts = summary["bands"]
    total = counts["stepped"] + sum(counts["no_step"].values())
    flagged = (f"; for {counts['error_not_measured']} of them the step's error is not measured for that kind of mode, and no bar is printed"
               if counts["error_not_measured"] else "")
    return (f"each band is printed at its best estimate — the anharmonic position ν = ω + Δ_anh for {counts['stepped']} of {total} bands "
            f"(Δ_anh from the model {summary['model']} on the molecule's GFN2-xTB force field{flagged}), the harmonic position ω for the "
            f"other {total - counts['stepped']}, each with its reason; ω stands beside every ν; {LICENCE_SCOPE}; {NO_LICENCE_FOR_NU}")


def band(stick: dict, summary: dict, reason_text: dict[str, str], not_measured_text: str) -> dict:
    """What one band's line says of its position, from the stick the pipeline recorded and the step's summary (`summary_of`): the
    printed position and which it is, the step and its bar, and the sentence. `reason_text` and `not_measured_text` are the
    step's own wordings (probes/anharmonic_step.py), passed in so that this module needs none of the step's code.

    A bar is given only where it was measured for the band's kind of mode: a band whose step's error was not measured prints its
    step and no bar."""
    a = stick.get("anharmonic") if summary["status"] == APPLIED else None
    if a is None or a["delta_anh_cm"] is None:
        if summary["status"] != APPLIED:
            code, why = NOT_APPLIED, f"the step was not applied to this molecule — {summary['reason']}"
        elif a is None:
            raise ValueError(f"the band at {stick['omega_cm']} cm⁻¹ has no anharmonic block although the step was applied")
        else:
            code, why = a["reason"], reason_text[a["reason"]]
        return dict(printed_cm=stick["omega_cm"], printed=HARMONIC, nu_cm=None, delta_anh_cm=None, anharmonic_bar_cm=None,
                    anharmonic_error_measured=None, step_family=a["family"] if a else None, no_step_reason=code,
                    position_note=f"harmonic position, no anharmonic step: {why}")
    measured = not a["error_not_measured"]
    sentence = (f"anharmonic estimate ν = ω + Δ_anh, ± {a['bar_cm']} cm⁻¹ (the measured rms of family {a['family']} on {MODEL_TARGETS}); "
                "no licence is claimed for ν" if measured else
                f"anharmonic estimate ν = ω + Δ_anh, printed without an error bar: {not_measured_text}; no licence is claimed for ν")
    return dict(printed_cm=stick["nu_cm"], printed=ANHARMONIC, nu_cm=stick["nu_cm"], delta_anh_cm=a["delta_anh_cm"],
                anharmonic_bar_cm=a["bar_cm"] if measured else None, anharmonic_error_measured=measured, step_family=a["family"],
                no_step_reason=None, position_note=sentence)
