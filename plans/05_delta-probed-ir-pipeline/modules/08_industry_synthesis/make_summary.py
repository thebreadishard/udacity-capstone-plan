#!/usr/bin/env python
"""Builds Reflective_Synthesis_Paper.docx (Module 08, the reflective synthesis paper: 1,500–2,000 words, the eight sections the rubric's
submission list prescribes, in-text citations, a References list) in the Udacity APA 7 template and converts it to PDF with Word (COM
through PowerShell), as modules 06 and 07 do.

Every measured number is read from notebook/results.json (written by the executed notebook); none is typed. A key the record lacks
stops the build with its name. A sentence that states an outcome ("every cost line traced") is written only when the record shows
it; otherwise the build stops and says which. The text is built by `blocks`, so a test can read it without Word.

A record made from an interim scenario run — on the fixed S3 candidate, without S5, or read from another folder than the module's
out/ — is refused unless `--interim` is given; the builder then prints why the paper is interim. The text itself never says so:
an interim paper is for reading the draft, not for submission.

Run:  python make_summary.py [--interim] [--no-pdf] [--out PATH]"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parents[3] / "Rubrics" / "APA7_template.docx"
RESULTS = HERE / "notebook" / "results.json"
FIGURES = HERE / "notebook" / "figures"
OUT_DOCX = HERE / "Reflective_Synthesis_Paper.docx"
AUTHOR = "Frederic Petrignani"         # the title page's author line, and the file's own author fields
WORD_RANGE = (1500, 2000)              # the rubric's range for the body
ANCHOR_STEP, CHEAP_STEP = "anchor_e8_cc_hessian_naphthalene", "cheap_deck_v1"
FIXED_CANDIDATE_FLAG = "--no-candidate"
GLOSSARY = "https://github.com/thebreadishard/udacity-capstone-plan/blob/master/plans/05_delta-probed-ir-pipeline/modules/GLOSSARY.md"

Block = tuple[str, str] | tuple[str, str, str]

REFERENCES = (
    "Mackie, C. J., Candian, A., Huang, X., Maltseva, E., Petrignani, A., Oomens, J., Buma, W. J., Lee, T. J., & Tielens, A. G. G. M. (2015). "
    "The anharmonic quartic force field infrared spectra of three polycyclic aromatic hydrocarbons: Naphthalene, anthracene, and tetracene. "
    "The Journal of Chemical Physics, 143(22), 224314. https://doi.org/10.1063/1.4936779",
    "Mitchell, M., Wu, S., Zaldivar, A., Barnes, P., Vasserman, L., Hutchinson, B., Spitzer, E., Raji, I. D., & Gebru, T. (2019). Model cards "
    "for model reporting. In Proceedings of the Conference on Fairness, Accountability, and Transparency (pp. 220–229). ACM. "
    "https://doi.org/10.1145/3287560.3287596",
    "Ricca, A., Boersma, C., Maragkoudakis, A., Roser, J. E., Shannon, M. J., Allamandola, L. J., & Bauschlicher, C. W. (2026). The NASA Ames "
    "PAH IR Spectroscopic Database: Version 4.00. The Astrophysical Journal Supplement Series, 282, 7. https://doi.org/10.3847/1538-4365/ae1c38",
    "Shavit, Y., Agarwal, S., Brundage, M., Adler, S., O'Keefe, C., Campbell, R., Lee, T., Mishkin, P., Eloundou, T., Hickey, A., Slama, K., "
    "Ahmad, L., McMillan, P., Beutel, A., Passos, A., & Robinson, D. G. (2023). Practices for governing agentic AI systems. OpenAI. "
    "https://openai.com/research/practices-for-governing-agentic-ai-systems",
)


def interim_reasons(results: dict[str, Any]) -> list[str]:
    """Why this record is not the one a submitted paper is built from; empty for the final run's record."""
    scenarios = results["scenarios"]
    reasons = []
    if FIXED_CANDIDATE_FLAG in scenarios["written_by"].split():
        reasons.append(f"the scenario run used {FIXED_CANDIDATE_FLAG}: S3 ran on the fixed candidate, not on a drawn one")
    if "S5" not in scenarios["mechanical"]:
        reasons.append("the scenario run has no S5 (run_scenarios.py without --with-catalog)")
    if scenarios["results_env_set"]:
        reasons.append(f"the notebook read its scenario results from M08_SCENARIO_RESULTS ({scenarios['results_dir']}), not from the module's out/")
    return reasons


def checked_outcome(results: dict[str, Any]) -> dict[str, Any]:
    """The notebook's outcome block, refused when a claim the paper's text makes does not hold in the record."""
    outcome = results["outcome"]
    unmet = [claim for claim, holds in outcome["claims"].items() if not holds]
    if unmet:
        raise ValueError("the paper states outcomes the record does not show: " + "; ".join(unmet) + " — rewrite those sentences "
                         "before building")
    return outcome


def licence_sentence(licence: dict[str, Any], version: str) -> str:
    """What the licence record says for the network version in use: which families are licensed and between which errors."""
    licensed, errors = licence["licensed_families"], licence["errors"]
    if not licensed:
        return f"For version {version} no family is licensed, and the certificate says so on every band."
    values = [v for f in licensed for v in errors[f].values()]
    held_back = [f for f in errors if f not in licensed]
    rest = f"; {', '.join(held_back)} {'is' if len(held_back) == 1 else 'are'} not" if held_back else ""
    return (f"For version {version} of the network, {len(licensed)} of {len(errors)} families are licensed ({', '.join(licensed)}{rest}), "
            f"with errors between {min(values):.2f} and {max(values):.2f} cm⁻¹.")


def anharmonic_sentence(step: dict[str, Any], line_cm: float) -> str:
    """The anharmonic step's measured error bars, what they rest on, and what follows for a claim on ν — from the stored run's record."""
    bars = step["bars_cm"]
    listed = ", ".join(f"{bars[f]:.2f} ({f})" for f in sorted(bars, key=lambda f: bars[f]))
    rows = sum(step["target_rows"].values())
    within = [f for f in bars if bars[f] <= line_cm]
    verdict = (f"None is within {line_cm:g} cm⁻¹, so no anharmonic position is claimed to that line" if not within else
               f"Only {', '.join(within)} {'is' if len(within) == 1 else 'are'} within {line_cm:g} cm⁻¹, and the bars are too thin to claim a line")
    return (f"The anharmonic step has a measured error bar in {len(bars)} families: {listed} cm⁻¹. The bars rest on {rows} modes of "
            f"{len(step['target_molecules'])} molecules, {' and '.join(step['target_molecules'])}. {verdict}; the licence is about the "
            "harmonic position only.")


def stored_run_sentence(run: dict[str, Any]) -> str:
    """Which stored run the notebook shows and what it is evidence of, from that run's record."""
    spread = "carries" if run["has_own_spread"] else "was written before"
    seen = run["seen"]
    known = (f"{run['molecule'].capitalize()} is in the release networks' training data, so the run shows the certificate's form and not an "
             "out-of-sample error" if seen["role"] == "release_trained" else f"The record says of this molecule: {seen['text']}")
    return (f"The notebook cannot run it, so it reads one stored run ({run['molecule']}, written by version {run['pipeline_version']}), "
            f"which {spread} the own-spread check. {known}.")


def scenario_sentences(scenarios: dict[str, Any], outcome: dict[str, Any]) -> str:
    """What the scenario record shows: the requests by kind, then the three mechanical checks, each from the record."""
    registered, added = scenarios["registered_ids"], scenarios["added_ids"]
    mechanical = scenarios["mechanical"]
    s5 = ("S5, the catalogue's consistency check, exited with code " f"{mechanical['S5']['exit_code']} and problems {mechanical['S5']['problems']}"
          if "S5" in mechanical else "S5, the catalogue's consistency check, was not part of this run")
    return (f"The officer answered {scenarios['n']} requests — {len(registered)} pre-registered ({', '.join(registered)}) and "
            f"{len(added)} added cases ({', '.join(added)}) — and all produced the registered kind of output ({scenarios['n_pass']} of "
            f"{scenarios['n']}). The three mechanical checks are separate. S7: every cost line traced to its source "
            f"({mechanical['S7']['lines_traced']} of {mechanical['S7']['lines_checked']}); {outcome['n_unpriced']} anchor lines are shown as "
            f"not priced. S6, accessibility, is not run by the scenario script; its record says: {mechanical['S6']['status']}. {s5}.")


def failure_sentence(coverage: list[dict[str, Any]]) -> str:
    """The failure case S8 displays: the families whose composite deviates from CCSD(T) by more than the laboratory tolerance."""
    wider = [a for a in coverage if a["wider_than_tolerance"]]
    if not wider:
        raise ValueError("results.json shows no family wider than its tolerance on benzene: the paper's failure case (S8) is gone; "
                         "rewrite that paragraph before building")
    deviations = ", ".join(f"{a['rms_dev_vs_ccsdt']:.0f} cm⁻¹ in the {a['family'].split(' (')[0]} family" for a in wider)
    return (f"The failure case is real: on benzene, the coupled-cluster composite deviates from CCSD(T) by {deviations} against "
            f"tolerances of {' and '.join(f'{a['u_band']:.0f}' for a in wider)}, and the certificate marks those families as not decidable "
            "at this rung.")


def context(results: dict[str, Any]) -> list[Block]:
    """Sections 1–2: the industry problem and the integrated solution."""
    steps, counts = results["prices"]["steps"], results["catalogue"]["rung_counts"]
    anchor, cheap = steps[ANCHOR_STEP], steps[CHEAP_STEP]
    return [
        ("heading", "Industry Context and Problem Definition"),
        ("para", "Laboratory astrophysics reads the infrared spectra that the James Webb Space Telescope returns from interstellar matter against "
                 "databases of molecular spectra; for the aromatic families the reference is NASA's PAHdb, whose fourth release holds more than ten "
                 "thousand computed entries (Ricca et al., 2026). Every entry in such a database is either a laboratory measurement or a computed "
                 "spectrum whose accuracy the reader has to guess, because the paper that describes the library does not state the systematic "
                 "uncertainty of its scaled-harmonic method. The industry problem this module addresses is therefore a data-service problem: to "
                 "deliver, for a molecule that no laboratory has measured, a computed spectrum with a stated and measured accuracy and a stated "
                 "price — or, when neither can be given, a refusal that says which step is missing and what it would cost."),
        ("para", "The constraint that shapes the whole design is cost. The accurate method, coupled-cluster theory, is unaffordable per molecule at "
                 f"the sizes that matter: one anchor run of that kind for a naphthalene-sized molecule was priced at {anchor['hours']:.1f} "
                 f"machine-hours on a rented server ({anchor['eur_ex_vat']:.0f} € before tax) on 28 September. The cheap method, "
                 f"density-functional theory, costs about {cheap['hours'] * 60:.0f} minutes per molecule and is systematically wrong by an amount "
                 "that differs per vibrational family. The project's thesis is a learned correction: a neural network that turns the cheap "
                 "calculation into a better one. What this capstone proves is a proxy version of that thesis. The network is trained on the "
                 "difference between two density functionals, B3LYP and ωB97X, and tested on whether it reproduces the second from the first on "
                 "molecules it never saw. Nothing is claimed at the coupled-cluster level, and I decided in October that no new coupled-cluster "
                 "anchors are computed before July 2027."),
        ("heading", "Overview of the Integrated Solution"),
        ("para", "The integrated artifact is a request service on top of the project's public Spectrum Atlas. A request names a molecule, a target "
                 "rung on a six-rung ladder (listed, cheap level done, correction predicted, spectrum predicted, anchored, validated), a budget and "
                 "free text. A request officer reads the repository's export — the only catalogue it is allowed to read — and answers with one of "
                 "three outputs. A certificate carries the spectrum, a per-band error budget expressed in the laboratory's own tolerance per family, "
                 "a cost record, a coverage table of the coupled-cluster evidence, and a provenance block. A refusal names the gate or the cap that "
                 "stopped the request and the price of the missing step. A run order is a proposal in the run steward's schema, and it can start "
                 "nothing until the steward's deterministic gate has approved it. The worker behind a run order replays recorded run logs, so the "
                 "officer spends no money and touches no machine."),
        ("para", "Since 29 October the module also holds the pipeline the service points to: one molecule in, its corrected infrared spectrum out "
                 f"with a certificate, computed on a laptop. It stands at version {results['pipeline_version']}. "
                 f"{stored_run_sentence(results['pipeline_run'])}"),
        ("para", "For a reader without chemistry: the system turns a request — a molecule, how accurate the answer must be, a budget — into "
                 "either a computed infrared spectrum with a stated accuracy and price, or a refusal that names the missing step. Terms are "
                 f"defined in the glossary ({GLOSSARY})."),
        ("para", f"The catalogue holds {results['catalogue']['n']:,} molecules: "
                 f"{counts['cheap_level_done']:,} at the cheap rung, {counts['anchored']} anchored and {counts['validated']} validated. The two "
                 "predicted rungs are empty in the catalogue because a catalogue record is the cheap level; the corrected spectrum is computed "
                 f"per molecule by the pipeline. {scenario_sentences(results['scenarios'], checked_outcome(results))}"),
        ("figure", "ladder_counts.png", f"Figure 1. The ladder as the export of {results['catalogue']['built_utc'][:10]} builds it: the predicted "
                                        "rungs are empty in the catalogue because the pipeline computes the corrected spectrum per molecule."),
    ]


def integration(results: dict[str, Any]) -> list[Block]:
    """Sections 3–4: what the earlier modules contribute, and the design decisions."""
    licence, candidate = results["licence"], results["s3"]["candidate"]
    version = results["shape"]["accuracy"]["version"]
    checked_outcome(results)           # the gate sentence below is one of the checked claims
    return [
        ("heading", "Integration of Prior Projects and Methods"),
        ("para", "Four earlier modules are used in the code. From the data-analysis module (03) comes the laboratory tolerance per vibrational "
                 "family, u_band; the certificate's error budget is that table, and the family rule is copied from module 03's script so that "
                 "the two agree by construction. From the deep-learning module (05) come the network and the licence. A family of vibrations is "
                 "licensed when the error of the corrected harmonic band positions, measured against ωB97X, is within "
                 f"{licence['line_cm']:g} cm⁻¹ on both test sets: test set (a), unseen molecules, and test set (b), molecules of held-out "
                 f"scaffolds. The officer reads that error from the network's evaluation records. {licence_sentence(licence, version)} The error "
                 "is measured on networks that never saw the test sets, and the printed spectrum is made by networks of the same recipe trained "
                 "on all data. The library module (02) and the machine-learning module (04) belong to the story — module 04 showed that a "
                 "per-band correction trained on laboratory residuals did not beat the library as served — but no code here reads their output."),
        ("para", "From the generative module (06) comes the candidate of scenario S3: a molecule from that module's generator, listed in the "
                 f"catalogue but not computed ({candidate['smiles']}; {candidate['source']}). The officer refused it under its budget and named the "
                 "cheapest rung it could buy. From the agentic module (07) comes the boundary: a run order is a proposal in the steward's schema, "
                 f"the steward's rule table of {results['n_rules']} rules is loaded, and its gate decides here. Asked to launch an anchor for "
                 f"{results['s2']['request']['molecule']} under a sufficient budget, the gate did not approve the order and forced the "
                 f"{results['s2b']['gate']['forced_action']['action'].replace('_', ' ')} first, and the replay worker queued it without touching a "
                 "machine. The standout proposer's measurement plan appears only as a labelled proxy line: its coupled-cluster test was run on "
                 "benzene on 28 September and failed, so the label stays."),
        ("heading", "Technical Design Decisions and Tradeoffs"),
        ("para", "The site is static and has one dynamic component. It is an export of repository files with a mechanical builder that fails "
                 "when an invariant breaks, and the request officer is the one dynamic piece. This trades live queries for a site whose every "
                 "number can be traced to a file at a commit. The worker replays; it is not live. It re-executes recorded logs and returns the "
                 "same run record marked as a replay. An earlier design had a live worker that rents a server per job. I no longer promise it: "
                 "under the proxy proof there is no coupled-cluster job to launch, and a new molecule is served by running the pipeline on a "
                 "laptop. The refusal is a first-class output. The officer names the gate (cap, closed rung, invalid input, an instruction "
                 "hidden in the request) and prices the missing step from a table in which every entry names the record it comes from. The "
                 "measured error stands beside every number. The pipeline certificate prints each corrected band with its family's measured "
                 "error, and since version 0.15 it licenses a band only if the band's own position stayed within the line when the networks were "
                 "given the same molecule turned, mirrored or with its atoms in another order. That check is a sample, not a bound, and the "
                 "certificate says so. Printing an error beside every band makes the certificate harder to read."),
        ("figure", "naphthalene_budget.png", "Figure 2. Naphthalene's catalogue record at the cheap rung: modes of both functionals with the "
                                             "laboratory tolerance of their family shaded. The corrected positions are the pipeline's."),
    ]


def reflection(results: dict[str, Any]) -> list[Block]:
    """Sections 5–8: ethics, limitations, relevance and what comes next."""
    counts, licence = results["catalogue"]["rung_counts"], results["licence"]
    return [
        ("heading", "Ethical, Governance, and Responsible AI Considerations"),
        ("para", "The concrete harm this system could do is a certified-looking spectrum being cited in an astronomical analysis for a molecule "
                 "whose accuracy was never measured. Three safeguards answer it: the ladder on every certificate; the licence, which is a measured "
                 "error against a line fixed beforehand and not an opinion; and the refusal, which carries the same provenance as a certificate. "
                 "Governance follows the practices that agentic-systems work now recommends — bounded action, identifiers, human oversight and a "
                 "record of every step (Shavit et al., 2023): the officer's allow-list is the steward's, every decision lands in a request ledger "
                 "with its rule identifiers, and a request whose text tries to instruct the system is refused under the rule that observed content "
                 "is data. Transparency is mechanical: the cost check S7 recomputes every euro as hours times a list price, and a certificate "
                 "names release, deck hash and commit in the manner of a model card for a data product (Mitchell et al., 2019). Coverage bias is "
                 "stated: the service is for neutral, closed-shell aromatic molecules, a molecule outside the sizes or the chemistry the networks "
                 "trained on is printed with no band licensed, and the cation request is refused with the measured price of the closed step. "
                 "The certificate states what the service does not cover."),
        ("heading", "Limitations and Risks"),
        ("para", "The largest limitation is the level of the proof. The licence is on the harmonic position against a second density functional, "
                 "not against coupled cluster and not against the laboratory, and the certificate says so in its licence statement. "
                 f"{anharmonic_sentence(results['pipeline_run']['anharmonic'], licence['line_cm'])} Where a licensed family rests on few molecules "
                 f"its interval crosses the line ({len(licence['caveats'])} such cases today). The catalogue is thin above the cheap rung: "
                 f"{counts['anchored']} anchored molecules and {counts['validated']} validated. The price of an anchor is that of one run in "
                 "September; the anchors in force today are later runs, which the registry carries without a price. "
                 f"{failure_sentence(results['s8']['coverage'])}"),
        ("heading", "Professional and Industry Relevance"),
        ("para", "The product form is a spectrum with a per-band budget, a cost record and a provenance block, or a refusal with a price. A "
                 "database curator or an observer needs that, and the existing libraries do not give it: the anharmonic protocol behind the PAHdb "
                 "anharmonic entries states its method (Mackie et al., 2015), but a user still cannot read, per band, how far a given entry may be "
                 "trusted. The module shows what the earlier ones taught separately: that the controls (module 03's tolerances, module 05's "
                 "measured test-set error, module 07's gate) are the product."),
        ("heading", "Future Extensions or Improvements"),
        ("para", "The next step lies outside this capstone: the coupled-cluster anchors that would turn the proxy proof into a proof at the "
                 "reference level. None are computed before July 2027, and after June 2027 my supervisor decides how they are made. Three things "
                 "are within reach before that. The anharmonic step's error bars need more target molecules than the present ones before any "
                 "of them can carry a claim. Cations need a pipeline that takes open-shell input. And the notebook's stored run should be "
                 "replaced by one of a molecule the networks have not seen, with the own-spread measurement. Two improvements follow from this "
                 "build: the anchor coverage should be produced by the anchor scripts as a small JSON beside their reports rather than parsed "
                 "from Markdown, and the request scanner should be shared with module 07 so that both read the same patterns."),
    ]


def blocks(results: dict[str, Any]) -> list[Block]:
    """The paper in order: ('title' | 'heading' | 'para', text) and ('figure', file name, caption)."""
    return [("title", "Reflective Synthesis Paper — A Computed Infrared Spectrum With a Stated Accuracy and a Stated Price"),
            ("title", "Module 08, Industry-Integrated AI Systems Synthesis · AI Mastery Capstone"),
            ("title", f"{AUTHOR} · {results['date'][:10]}"),
            *context(results), *integration(results), *reflection(results)]


def body_words(paper: list[Block]) -> int:
    """The words the rubric counts: the paragraphs, without titles, headings, captions and references."""
    return sum(len(re.findall(r"\S+", block[1])) for block in paper if block[0] == "para")


def checked_words(paper: list[Block]) -> int:
    """The body's word count, refused outside the rubric's range."""
    words = body_words(paper)
    if not WORD_RANGE[0] <= words <= WORD_RANGE[1]:
        raise ValueError(f"the body has {words} words; the rubric asks for {WORD_RANGE[0]:,}–{WORD_RANGE[1]:,}: not written")
    return words


def _paragraph(doc: Any, text: str, *, bold: bool = False, center: bool = False, caption: bool = False, indent_first: bool = True) -> Any:
    p = doc.add_paragraph()
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if not indent_first:
        p.paragraph_format.first_line_indent = Pt(0)
    run = p.add_run(text)
    run.bold, run.italic = bold, caption
    if caption:
        run.font.size = Pt(10)
    return p


def _add_block(doc: Any, block: Block, first_title: bool) -> None:
    kind = block[0]
    if kind == "title":
        _paragraph(doc, block[1], bold=first_title, center=True)
    elif kind == "heading":
        _paragraph(doc, block[1], bold=True, indent_first=False)
    elif kind == "para":
        _paragraph(doc, block[1])
    elif kind == "figure":
        if not (FIGURES / block[1]).is_file():
            raise FileNotFoundError(f"{FIGURES / block[1]}: the notebook writes the paper's figures; execute it first")
        doc.add_picture(str(FIGURES / block[1]), width=Inches(6.0))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        _paragraph(doc, block[2], caption=True, indent_first=False)
    else:
        raise ValueError(f"unknown block kind {kind!r}")


def write_docx(paper: list[Block], path: Path) -> None:
    """The paper in the APA 7 template, written to a temp file that is moved over `path`.

    The template's own author fields name whoever saved the template last; they are set to the paper's author.
    """
    if not TEMPLATE.is_file():
        raise FileNotFoundError(f"{TEMPLATE}: the APA 7 template is in the plan repository's Rubrics folder; the paper is built there")
    doc = Document(str(TEMPLATE))
    for p in list(doc.paragraphs):
        p._element.getparent().remove(p._element)
    for i, block in enumerate(paper):
        _add_block(doc, block, first_title=i == 0)
    _paragraph(doc, "References", bold=True, indent_first=False)
    for reference in REFERENCES:
        p = _paragraph(doc, reference, indent_first=False)
        p.paragraph_format.left_indent, p.paragraph_format.first_line_indent = Inches(0.5), Inches(-0.5)
    doc.core_properties.author = doc.core_properties.last_modified_by = AUTHOR
    tmp = path.with_name(path.stem + ".tmp.docx")
    doc.save(str(tmp))
    os.replace(tmp, path)


def to_pdf(docx: Path) -> Path:
    """Convert with Word through PowerShell, as modules 06 and 07 do, into a temp file moved over the PDF; raises when Word wrote none."""
    pdf, tmp = docx.with_suffix(".pdf"), docx.with_name(docx.stem + ".tmp.pdf")
    script = (f'$w = New-Object -ComObject Word.Application; $w.Visible = $false\n'
              f'$d = $w.Documents.Open("{docx}"); $d.SaveAs2("{tmp}", 17); $d.Close(); $w.Quit()')
    subprocess.run(["powershell", "-NoProfile", "-Command", script], check=True)
    if not tmp.is_file():
        raise FileNotFoundError(f"Word did not write {tmp}")
    os.replace(tmp, pdf)
    return pdf


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Build module 08's reflective synthesis paper from notebook/results.json.")
    ap.add_argument("--interim", action="store_true", help="build from a record of an interim scenario run (a draft, not the submitted paper)")
    ap.add_argument("--no-pdf", action="store_true", help="write the .docx only (no Word needed)")
    ap.add_argument("--out", type=Path, default=OUT_DOCX, help="the .docx to write (default: the module's paper)")
    a = ap.parse_args(argv)
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    reasons = interim_reasons(results)
    if reasons and not a.interim:
        raise SystemExit("notebook/results.json is not the final run's record: " + "; ".join(reasons) + ". Run the scenarios with "
                         "--with-catalog --submitted and rebuild the notebook, or pass --interim for a draft.")
    if a.interim and not reasons:
        raise SystemExit("--interim, but notebook/results.json is the final run's record: build without the flag")
    for reason in reasons:
        print("INTERIM PAPER —", reason)
    paper = blocks(results)
    print(f"body words: {checked_words(paper)}")
    write_docx(paper, a.out.resolve())
    print("written", a.out)
    if not a.no_pdf:
        print("pdf:", to_pdf(a.out.resolve()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
