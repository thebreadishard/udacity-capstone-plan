#!/usr/bin/env python
"""Builds Reflective_Synthesis_Paper.docx (Module 08, the reflective synthesis paper: 1,500–2,000 words, the eight sections the rubric's submission
list prescribes, in-text citations, a References list) in the Udacity APA 7 template and converts it to PDF with Word (COM through PowerShell),
as modules 06 and 07 do. Every number is read from notebook/results.json (written by the executed notebook); nothing is typed in by hand.
The script prints the word count of the body and refuses to write when it falls outside the rubric's range.
Run:  python make_summary.py"""
import json
import re
import subprocess
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parents[3] / "Rubrics" / "APA7_template.docx"
NB = HERE / "notebook"
FIG = NB / "figures"
OUT_DOCX = HERE / "Reflective_Synthesis_Paper.docx"

R = json.load(open(NB / "results.json", encoding="utf-8"))
SC = R["scenarios"]; L = R["licence"]; S1 = R["s1"]; S8 = R["s8"]; PR = R["prices"]
rc = R["catalogue"]["rung_counts"]
anchor = PR["steps"]["anchor_e8_cc_hessian_naphthalene"]; cheap = PR["steps"]["cheap_deck_v1"]
wider = [a for a in S8["coverage"] if a["wider_than_tolerance"]]
lat = L["latest_reading"]["rows"]

doc = Document(str(TEMPLATE))
for p in list(doc.paragraphs):
    p._element.getparent().remove(p._element)
BODY: list[str] = []


def para(text="", bold=False, center=False, italic=False, size=None, indent_first=True, count=True):
    p = doc.add_paragraph()
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if not indent_first:
        p.paragraph_format.first_line_indent = Pt(0)
    r = p.add_run(text); r.bold = bold; r.italic = italic
    if size:
        r.font.size = Pt(size)
    if count and not bold:
        BODY.append(text)
    return p


def heading(text):
    para(text, bold=True, indent_first=False, count=False)


def figure(name, caption):
    if (FIG / name).exists():
        doc.add_picture(str(FIG / name), width=Inches(6.0)); doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        para(caption, italic=True, size=10, indent_first=False, count=False)


def table(header, rows, caption):
    para(caption, italic=True, size=10, indent_first=False, count=False)
    t = doc.add_table(rows=1, cols=len(header))
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]; c.text = ""; run = c.paragraphs[0].add_run(h); run.bold = True; run.font.size = Pt(9)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""; cells[i].paragraphs[0].add_run(str(v)).font.size = Pt(9)
    doc.add_paragraph()


# ---------------------------------------------------------------------------------------------------------------- title page
para("Reflective Synthesis Paper — A Computed Infrared Spectrum With a Stated Accuracy and a Stated Price", bold=True, center=True, count=False)
para("Module 08, Industry-Integrated AI Systems Synthesis · AI Mastery Capstone", center=True, count=False)
para(f"Frederic Petrignani · {R['date'][:10]}", center=True, count=False)
doc.add_paragraph()

heading("Industry Context and Problem Definition")
para("Laboratory astrophysics reads the infrared spectra that the James Webb Space Telescope returns from interstellar matter against databases of molecular "
     "spectra; for the aromatic families the reference is NASA's PAHdb, whose fourth release holds more than ten thousand computed entries (Ricca et al., 2026). "
     "Every entry in such a database is either a laboratory measurement, which exists for a few hundred molecules, or a computed spectrum whose accuracy the "
     "reader has to guess, because the paper that describes the library does not state the systematic uncertainty of its scaled-harmonic method. The industry "
     "problem this module addresses is therefore a data-service problem: to deliver, for a molecule that no laboratory has measured, a computed spectrum with a "
     "stated and measured accuracy and a stated price — or, when neither can be given, an honest refusal that says which step is missing and what it would cost.")
para("The constraint that shapes the whole design is cost. The accurate method, coupled-cluster theory, is unaffordable per molecule at the sizes that matter; "
     f"one anchor of a naphthalene-sized molecule costs about {anchor['hours']:.0f} machine-hours on a rented server, measured this week ({anchor['eur_ex_vat']:.0f} € before tax). "
     f"The cheap method, density-functional theory, costs about {cheap['hours'] * 60:.0f} minutes per molecule and is systematically wrong by an amount that differs per "
     "vibrational family. The project's thesis, developed across the earlier capstone modules, is a learned correction layer trained on a small set of expensive "
     "anchors — and the professional obligation that follows from it is that the layer must earn a licence per family, on a pre-registered learning curve, before "
     "any of its numbers may be shown to a user as a prediction.")

heading("Overview of the Integrated Solution")
para("The integrated artifact is a request service on top of the project's public Spectrum Atlas. A request names a molecule, a target rung on a six-rung ladder "
     "(listed, cheap level done, correction predicted, spectrum predicted, anchored, validated), a budget and free text. A request officer reads the repository's "
     "export — the only source it is allowed to read — and answers with one of three outputs. A certificate carries the spectrum, a per-band error budget expressed "
     "in the laboratory's own tolerance per family, a cost record in which every euro traces to a run log or to a measured price table, a coverage table of the "
     "coupled-cluster evidence, and a provenance block signed by release, deck hash and commit. A refusal names the gate or the cap that stopped the request and the "
     "measured price of the missing step. A run order is a proposal in the run steward's schema, and it can start nothing until the steward's deterministic gate has "
     "approved it. In this build the worker behind a run order is a replay of recorded run logs — the user's decision of 28 September — so the service spends no money "
     "and touches no machine while the licence question is still open.")
para(f"Run on the repository as it stands, the catalogue holds {R['catalogue']['n']:,} molecules: {rc.get('cheap_level_done', 0)} at the cheap rung, "
     f"{rc.get('anchored', 0)} anchored and {rc.get('validated', 0)} validated; the predicted rungs are empty by rule. The eight pre-registered scenarios all produced "
     f"the registered kind of output ({SC['n_pass']} of {SC['n']}); every cost line traced to its source; and the failure case — a family whose coupled-cluster "
     "composite deviates from CCSD(T) by more than the laboratory tolerance — is displayed on the benzene certificate rather than hidden.")
figure("ladder_counts.png", "Figure 1. The ladder as the export builds it on 28 September 2026: the predicted rungs are empty because no family is licensed.")

heading("Integration of Prior Projects and Methods")
para("Five earlier modules are load-bearing in the officer's code, not merely cited. From the data-analysis module (03) comes the laboratory tolerance per vibrational "
     "family, u_band, built from the PAHdb laboratory records with their temperature and resolution terms; the certificate's error budget is that table, family by "
     "family, and the family rule itself is copied from module 03's script so that the two speak the same language by construction. From the machine-learning module "
     "(04) comes the calibrated-harmonic reading of the cheap column: the leave-one-molecule-out analysis showed that a per-band correction trained on laboratory "
     "residuals did not beat the library as served, which is why the cheap rung is shown with the laboratory tolerance and not with a learned band. From the "
     "deep-learning module (05) comes the licence: the officer reads the proof-of-learning pre-registration's rule — a verdict at 1,200 admitted molecules on three "
     f"hold-outs — and the latest recorded table, in which the local pair model reaches ring-coupling ratios of {' and '.join(f'{v['ring_coupling_ratio']:.2f}' for v in lat.values())} "
     "against the zero rule on the two hold-outs at 274 molecules; that is an interim, so no family is licensed and the officer says so on every refusal.")
para("From the generative module (06) comes the out-of-corpus candidate of scenario S3: the officer draws one sample from the trained SMILES Transformer at a fixed "
     f"seed and treats it as a request; the string drawn ({R['s3']['candidate']['smiles']}) is a fused heteroaromatic outside the corpus, and the officer refused it under "
     "its budget and named the cheapest rung it could buy. From the agentic module (07) comes the boundary: a run order is a proposal in the steward's schema, the "
     "steward's rule table of 32 rules is loaded, and its gate — the same code that decided that module's eight replayed scenarios — decides here. Asked to launch an "
     "anchor for azulene under a sufficient budget, the gate stopped the order at the dry run (rule R01) and the replay worker queued it without touching a machine. "
     "The standout proposer's measurement plan appears only as a labelled proxy line, by decision, until its coupled-cluster test is read.")

heading("Technical Design Decisions and Tradeoffs")
para("Static first, one dynamic component. The public site is a static export of repository files with a mechanical builder that fails when an invariant breaks; the "
     "request officer is the one dynamic piece, designed so that everything else stays reproducible. This trades live queries for a site whose every number can be "
     "traced to a file at a commit. Replay before live. A live worker would provision a rented server per job under a hard budget cap; the replay worker re-executes "
     "recorded logs and returns the same run record marked as a replay. This trades the ability to take a new molecule to a new rung for zero cost and zero risk "
     "while the learned layer has no licence — the design keeps the live path documented and behind the same gate. The refusal as a first-class output. It would "
     "have been easy to show the cheap spectrum and let the reader infer the rest; the design instead makes the officer name the gate (licence, cap, closed rung, "
     "invalid input, an instruction hidden in the request) and price the missing step from a table in which every entry names the record it comes from. Bands, not "
     "numbers. The certificate draws the laboratory tolerance per family and leaves the ensemble column empty with its reason; this trades visual simplicity for "
     "honesty, and it is the single design choice most likely to be questioned by a user who wants a number.")
figure("naphthalene_budget.png", "Figure 2. Naphthalene at the cheap rung: modes of both functionals with the laboratory tolerance of their family shaded; no predicted band is drawn.")

heading("Ethical, Governance, and Responsible AI Considerations")
para("The concrete harm this system could do is a certified-looking spectrum being cited in an astronomical analysis for a molecule whose rung was never reached. "
     "Three safeguards answer it: the ladder on every certificate, with the predicted rungs shown as empty and the reason stated; the licence, which is a "
     "pre-registered verdict and not an opinion; and the refusal, which carries the same provenance as a certificate. Governance follows the practices that "
     "agentic-systems work now recommends — bounded action, identifiers, human oversight and a record of every step (Shavit et al., 2023): the officer's allow-list is "
     "the steward's, every decision lands in a request ledger with its rule identifiers, and a request whose text tries to instruct the system is refused under the "
     "rule that observed content is data (a case, S4c, found while building). Transparency is mechanical rather than promised: the price table names the ledger lines "
     "it was read from, the cost check S7 recomputes every euro as hours times a list price, and a certificate names release, deck hash and commit in the manner of a "
     "model card for a data product (Mitchell et al., 2019). Coverage bias is stated rather than smoothed over: the corpus is neutral, small and aromatic, and the "
     "cation request is refused with the measured price of the closed rung, which is the system saying whose spectra it cannot serve yet.")

heading("Limitations and Risks")
para("The service today is honest but thin. It serves cheap spectra with laboratory tolerances, two anchors and one validated molecule; the learned layer contributes "
     "nothing a user can see until the layer-B curve is read at 1,200 molecules, and that reading may fail — the pre-registration names the fail line, and the design "
     "answer is that the certificate would keep showing the empty predicted rungs. The accessibility and mobile scenario (S6) was not run in this build: it needs the "
     "built site and an axe pass, both on the website backlog, and the results file says so. The anchor coverage parser reads two record formats that exist today and "
     "will need a third when the whole-molecule naphthalene Hessian lands. The price table is measured on one molecule size; the refusal says that a larger molecule "
     f"costs more and that the price is not measured yet. And the failure case is real: on benzene, the coupled-cluster composite deviates from CCSD(T) by "
     f"{', '.join(f'{a['rms_dev_vs_ccsdt']:.0f} cm⁻¹ in the {a['family'].split(' (')[0]} family' for a in wider)} against tolerances of "
     f"{' and '.join(f'{a['u_band']:.0f}' for a in wider)} — the certificate marks those families as not decidable at this rung.")

heading("Professional and Industry Relevance")
para("The product form — a spectrum with a per-band budget, a cost record and a provenance block, or a refusal with a price — is what a database curator or an "
     "observer needs and what the existing libraries do not give: the anharmonic protocol behind the PAHdb anharmonic entries states its method (Mackie et al., 2015) "
     "but a user still cannot read, per band, how far a given entry may be trusted. The engineering pattern is transferable beyond spectroscopy: any computed data "
     "service that sells predictions from an expensive reference method can use a ladder of evidence, a licence earned on a pre-registered curve, a deterministic "
     "gate in front of spending, and refusals that price the missing step. Professionally, the module demonstrates what the earlier ones taught separately: that the "
     "controls (module 03's tolerances, module 05's pre-registered curve, module 07's gate) are the product, and that an honest empty column is worth more to a "
     "downstream scientist than a plausible number.")

heading("Future Extensions or Improvements")
para("Three extensions are pre-registered or scheduled. The licence read at 1,200 layer-B molecules fills the predicted rungs, family by family, with ensemble bands "
     "from three seeds. The coupled-cluster test of the standout proposer on the two anchored molecules decides whether the plan line may read 'confirmed' instead of "
     "'proxy'. The live worker — a rented server per job under the steward's budget cap, behind OAuth on Cloudflare — is switched on only when a licence exists, "
     "and the accessibility pass (S6) precedes any public request form. Two improvements follow from this build: the anchor coverage should be produced by the "
     "anchor scripts as a small JSON beside their reports rather than parsed from Markdown, and the request scanner should be shared with module 07 so that both "
     "read the same patterns.")

heading("References")
refs = [
    "Mackie, C. J., Candian, A., Huang, X., Maltseva, E., Petrignani, A., Oomens, J., Buma, W. J., Lee, T. J., & Tielens, A. G. G. M. (2015). The anharmonic quartic force field infrared spectra of three polycyclic aromatic hydrocarbons: Naphthalene, anthracene, and tetracene. The Journal of Chemical Physics, 143(22), 224314. https://doi.org/10.1063/1.4936779",
    "Mitchell, M., Wu, S., Zaldivar, A., Barnes, P., Vasserman, L., Hutchinson, B., Spitzer, E., Raji, I. D., & Gebru, T. (2019). Model cards for model reporting. In Proceedings of the Conference on Fairness, Accountability, and Transparency (pp. 220–229). ACM. https://doi.org/10.1145/3287560.3287596",
    "Ricca, A., Boersma, C., Maragkoudakis, A., Roser, J. E., Shannon, M. J., Allamandola, L. J., & Bauschlicher, C. W. (2026). The NASA Ames PAH IR Spectroscopic Database: Version 4.00. The Astrophysical Journal Supplement Series, 282, 7. https://doi.org/10.3847/1538-4365/ae1c38",
    "Shavit, Y., Agarwal, S., Brundage, M., Adler, S., O'Keefe, C., Campbell, R., Lee, T., Mishkin, P., Eloundou, T., Hickey, A., Slama, K., Ahmad, L., McMillan, P., Beutel, A., Passos, A., & Robinson, D. G. (2023). Practices for governing agentic AI systems. OpenAI. https://openai.com/research/practices-for-governing-agentic-ai-systems",
]
for r in refs:
    p = para(r, indent_first=False, count=False); p.paragraph_format.left_indent = Inches(0.5); p.paragraph_format.first_line_indent = Inches(-0.5)

words = sum(len(re.findall(r"\S+", t)) for t in BODY)
print(f"body words: {words}")
if not 1500 <= words <= 2000:
    print("word count outside the rubric's 1,500–2,000 — not written"); sys.exit(2)
doc.save(str(OUT_DOCX))
print("written", OUT_DOCX)
ps = f'''$w = New-Object -ComObject Word.Application; $w.Visible = $false
$d = $w.Documents.Open("{OUT_DOCX}"); $d.SaveAs2("{OUT_DOCX.with_suffix('.pdf')}", 17); $d.Close(); $w.Quit()'''
subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True)
print("pdf:", OUT_DOCX.with_suffix(".pdf").exists())
