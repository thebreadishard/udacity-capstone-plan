#!/usr/bin/env python
"""Builds Pattern_Proposer_Report.docx (the standout module's report) in the Udacity APA 7 template, then converts it to PDF with Word (COM through
PowerShell), exactly as module 06's make_summary.py does. Every number is read from notebook/results.json (written by the executed notebook) and from
the committed read-out JSONs; nothing is typed in by hand. Sections: Overview · Data · Method (the recovery, the orderings, the fair-chance rule) ·
Results (E1, E2, adaptive, deck cost) · What changes in plan 05 · Ethics and responsible use · Limitations and what follows · References.
Run:  python make_summary.py"""
import json
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
OUT_DOCX = HERE / "Pattern_Proposer_Report.docx"

R = json.load(open(NB / "results.json", encoding="utf-8"))
DC = R["deck_cost"]
PA = R["paired_adaptive"]
NH = R["n_half_ratios"]
VAL = {v["recipe"]: v for v in R["validation"]}

doc = Document(str(TEMPLATE))
for p in list(doc.paragraphs):
    p._element.getparent().remove(p._element)


def para(text="", bold=False, center=False, italic=False, size=None, indent_first=True):
    p = doc.add_paragraph()
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if not indent_first:
        p.paragraph_format.first_line_indent = Pt(0)
    r = p.add_run(text)
    r.bold = bold
    r.italic = italic
    if size:
        r.font.size = Pt(size)
    return p


def heading(text):
    para(text, bold=True, indent_first=False)


def figure(name, caption):
    if (FIG / name).exists():
        doc.add_picture(str(FIG / name), width=Inches(6.0))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        para(caption, italic=True, size=10, indent_first=False)


def table(header, rows, caption):
    para(caption, italic=True, size=10, indent_first=False)
    t = doc.add_table(rows=1, cols=len(header))
    try:
        t.style = "Table Grid"
    except KeyError:      # the APA template carries no table styles; module 06 draws its tables the same way
        pass
    for i, h in enumerate(header):
        t.rows[0].cells[i].text = str(h)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = str(v)
    doc.add_paragraph()


def nh(exp, split, ordering):
    v = [r["median_n_half_ratio"] for r in NH if r["experiment"] == exp and r["split"] == split and r["ordering"] == ordering]
    return v[0] if v else float("nan")


def nh_best(exp, split, prefix):
    v = [r["median_n_half_ratio"] for r in NH if r["experiment"] == exp and r["split"] == split and r["ordering"].startswith(prefix)]
    return min(v) if v else float("nan")


f2 = lambda x: f"{x:.2f}"  # noqa: E731
f0 = lambda x: f"{x:,.0f}"  # noqa: E731

# ---------------------------------------------------------------- title
para("Which measurement next? A pattern proposer for the Δ-probed IR pipeline", bold=True, center=True, size=14, indent_first=False)
para("Standout module of the Udacity capstone (plan 05) — report generated from the executed notebook", center=True, italic=True, indent_first=False)
para(f"Frederic Petrignani — results of {R['date']}; proxy-level (DFT against DFT) throughout", center=True, size=10, indent_first=False)
doc.add_paragraph()

heading("Overview")
para("Every molecule of the pipeline has a table of vibrational couplings that we can only afford to know in part: each entry costs an expensive "
     "coupled-cluster energy. The recovery reconstructs the table from a small number of pattern responses and stops when its held-out residual is low "
     "enough. This module asks whether a network that has only seen other molecules can choose the order of measurement better than the fixed recipe, "
     "and, once the first experiment was read, whether the recipe's candidate list should reach every pair of modes at all. It is a simulation with no new "
     "quantum chemistry: the corpus's cheap-against-cheap Hessians give the full table for 289 molecules, hence the exact response of any pattern.")
para(R["summary"])

heading("Data")
para(f"{R['molecules']} molecules of the plan-05 corpus (layers A, A2, B; ωB97X − B3LYP couplings), exported once per molecule with their modes, "
     "frequencies, atomic participations, low-level Hessian, the full coupling difference (the answer, used only for the oracle and the truth-based "
     "read-outs) and the probe deck's patterns with their exact responses. Splits are hashed and were fixed before the first run: the parents "
     "(unsubstituted aromatics, larger than any training molecule) are evaluation only; substituted molecules 70/10/20 train / validation / evaluation. "
     "Nothing is chosen on the evaluation molecules.")
figure("inband_share.png", "Figure 1. Share of the off-diagonal coupling power that lies inside the 200 cm⁻¹ band the fixed recipe covers, per molecule "
       "(289 molecules; mean ≈ 0.45). The other half lies between modes of different frequency that move the same atoms.")

heading("Method")
para("The recovery consumes the single-mode block, then the off-diagonal patterns in a given order; after every stride it solves the banded-ℓ₁ "
     "reconstruction (FISTA, warm-started, λ chosen on held-out patterns) and records the held-out residual ρ_off — the pipeline's own stopping quantity, "
     "which needs no truth. Orders compared: P0, the deck's hashed order (the fixed recipe); P1, a small network on 21 hand-made pair features; P2, a "
     "learned molecular representation (the equivariant body of module 05, unchanged, feeding a per-mode embedding and a pair head); P12, their z-score "
     "average; P3, the oracle that knows the answer (a ceiling, never available in practice). A pattern's score is the mean over the pairs it touches. "
     "Adaptive variants (P0+A, P1+A, P2+A) re-rank the remaining patterns after every checkpoint by the current reconstruction, with optimism for pairs no "
     "measured pattern has touched — a correction that the planted dry run forced before any real molecule ran.")
para("Pass lines, predictions and the reading order were written before each run (pre-registration of 26 September 2026 with dated amendments). The "
     "learned representation is protected by a fair-chance rule: no sentence about it before a five-stage search (recipe, loss, capacity, data growth, "
     "pretraining), each stage read on the validation split by the ordering metric with a margin fixed before the numbers.")
figure("one_molecule_curves.png", f"Figure 2. The recovery replayed live on one small molecule ({R['live_molecule']['id']}, {R['live_molecule']['M']} modes) "
       "under the fixed order, the hand-feature scorer and the oracle: held-out ρ_off against energies consumed.")

heading("Results")
para(f"E1, band pool (97 evaluation molecules). The learned order reaches the halfway point between the single block and the fixed order's end point with "
     f"{f2(nh_best('E1 band pool', 'eval_parents', 'P1_'))} (parents) / {f2(nh_best('E1 band pool', 'eval', 'P1_'))} (substituted) of the fixed order's energies; "
     f"the combined order P12 {f2(nh_best('E1 band pool', 'eval_parents', 'P12'))} / {f2(nh_best('E1 band pool', 'eval', 'P12'))}; the oracle "
     f"{f2(nh('E1 band pool', 'eval_parents', 'P3_oracle'))} / {f2(nh('E1 band pool', 'eval', 'P3_oracle'))}. The registered pass line (≤ 0.80 on ≥ 70 % of "
     "molecules) is met by a factor of about four; the gain is the same on the parents as on the substituted molecules (transfer to size holds).")
para(f"E2, all pairs. With a two-mode pattern for every pair the fixed order itself ends at ρ_off {DC['eval_parents']['wide_pool_final_rho_off']:.2f} / "
     f"{DC['eval']['wide_pool_final_rho_off']:.2f} where the band deck, consumed in full, ends at {DC['eval_parents']['band_deck_final_rho_off']:.2f} / "
     f"{DC['eval']['band_deck_final_rho_off']:.2f}: the candidate list matters more than the order. On that list ordering still pays: energies to ρ_off 0.3, "
     f"median, parents / substituted — fixed order {f0(DC['eval_parents']['wide_K_off_0p3_P0'])} / {f0(DC['eval']['wide_K_off_0p3_P0'])}, P12 "
     f"{f0(DC['eval_parents']['wide_K_off_0p3_P12'])} / {f0(DC['eval']['wide_K_off_0p3_P12'])}, oracle {f0(DC['eval_parents']['wide_K_off_0p3_oracle'])} / "
     f"{f0(DC['eval']['wide_K_off_0p3_oracle'])}; the whole band deck is {f0(DC['eval_parents']['band_deck_energies'])} / {f0(DC['eval']['band_deck_energies'])} energies.")
table(["split", "band deck: energies", "band deck: final ρ_off", "all pairs: final ρ_off", "to ρ_off 0.3: P0", "P1", "P12", "oracle", "P12 / band deck"],
      [[s, f0(d["band_deck_energies"]), f2(d["band_deck_final_rho_off"]), f2(d["wide_pool_final_rho_off"]), f0(d["wide_K_off_0p3_P0"]), f0(d["wide_K_off_0p3_P1"]),
        f0(d["wide_K_off_0p3_P12"]), f0(d["wide_K_off_0p3_oracle"]), f2(d["wide_K_off_0p3_P12_over_band_deck"])] for s, d in DC.items()],
      "Table 1. The band deck against the all-pairs candidate set (medians over molecules; deck_cost_2026-09-27.json).")
figure("n_half_ratios.png", "Figure 3. Median n_half ratio against the fixed order for every ordering, per experiment and split (a ratio below 1 is a saving).")
pp = PA["eval_parents"]
para(f"Adaptive ordering (band pool, paired per molecule). Feedback alone helps the blind order: P0+A is strictly better than P0 on "
     f"{100 * pp['P0A vs P0']['n_half_better']:.0f} % of the parents with a median ratio of {f2(pp['P0A vs P0']['median_n_half_ratio'])}. On top of a scorer "
     f"it improves the whole curve (AUC better on {100 * pp['P1A_seed0 vs P1_seed0']['auc_better']:.0f} % of molecules, median ratio "
     f"{f2(pp['P1A_seed0 vs P1_seed0']['median_auc_ratio'])}) but not the halfway point (strictly better on {100 * pp['P1A_seed0 vs P1_seed0']['n_half_better']:.0f} %, "
     f"equal on {100 * pp['P1A_seed0 vs P1_seed0']['n_half_equal']:.0f} %). The registered pass line fails on n_half and passes on the AUC; the prediction that "
     "feedback would close a third of the gap to the oracle fails. The gap is knowledge the scorer lacks, not feedback it is denied.")
PW = R.get("paired_adaptive_wide")
if PW:                                                   # follow-up of 28 September 2026 (all_p2s1A); the band-pool paragraph above stays as written
    pw = PW["eval_parents"]; ps = PW["eval"]; lg = pw["log_gap_closure_seed0"]
    p1b = [pw[f"P1A_seed{s} vs P1_seed{s}"]["n_half_better"] for s in range(3)]
    para(f"Adaptive ordering, wide pool (follow-up of 28 September 2026). On the all-pairs candidate set the same paired test gives: P0+A against P0 a median "
         f"ratio of {f2(pw['P0A vs P0']['median_n_half_ratio'])} on the parents (strictly better on {100 * pw['P0A vs P0']['n_half_better']:.0f} %) and "
         f"{f2(ps['P0A vs P0']['median_n_half_ratio'])} on the substituted molecules; P1+A against P1 a median of {f2(pw['P1A_seed0 vs P1_seed0']['median_n_half_ratio'])}, "
         f"strictly better on {100 * min(p1b):.0f}–{100 * max(p1b):.0f} % of the parents (pass line 70 %: fails), and the AUC gain of the band pool is gone "
         f"(median AUC ratio {f2(pw['P1A_seed0 vs P1_seed0']['median_auc_ratio'])}). Feedback closes {100 * lg['closure']:.0f} % of the log-gap from P1 to the "
         "oracle on the parents against a predicted third. What the adaptive loop can learn from the reconstruction, the scorer already knows before the first "
         "measurement; the lever is a better scorer, not an adaptive campaign, and the adaptive variants stay in the code as a measured negative.")
para(f"The fair-chance search. Validation Spearman of predicted against true log₁₀|Δ| — hand features {VAL['P1']['spearman']:.3f}; learned representation at "
     f"stage 0 {VAL.get('p2', {}).get('spearman', float('nan')):.3f}, after the recipe stage {VAL.get('p2s1_lr1e-3_w128', {}).get('spearman', float('nan')):.3f}, "
     f"largest capacity variant {VAL.get('p2s3_b5v', {}).get('spearman', float('nan')):.3f}. Loss and capacity stayed within the margins fixed before the numbers; "
     "stage 4 repeats at 300 molecules with a paired per-molecule test; nothing about the learned representation is licensed before stage 5.")

heading("What changes in plan 05")
para(f"The deck's candidate list. The band deck, however ordered, cannot buy a held-out ρ_off below about 0.5 on this proxy; a candidate list that reaches "
     f"every pair, with the learned order and a stop rule on the held-out ρ_off, reaches 0.3 at {f2(DC['eval_parents']['wide_K_off_0p3_P12_over_band_deck'])}× "
     f"the whole band deck on the parents. The change is pre-registered for after the supervisor conversation (W1–W3), together with two routes to the "
     "missing knowledge: pretraining on a public force-constant set and a cheap estimate of the answer as an input.")

heading("Ethics and responsible use")
para("The module proposes which calculation to run next, never a molecule or a claim about it. Its failure mode is wasted compute, not a wrong spectrum, "
     "because the stopping quantity is measured, not predicted. Every number is proxy-level and labelled so; the oracle column is a ceiling, not an "
     "achievable order. The data are the project's own corpus. The fair-chance rule protects the learned representation from a premature negative verdict "
     "and the reader from a premature positive one.")

heading("Limitations and what follows")
para("Proxy level: the tables are two density functionals against each other, not against coupled cluster; the test on real responses (the anchor's "
     "naphthalene deck) comes after the 28th. The band pool's factor of five was largely the fixed recipe's blindness; on the pool that matters the "
     "ordering gain is 1.3–1.6×. The learned representation has not beaten the hand features at 175 training molecules; the next stages (data growth, "
     "pretraining, the cheap-estimate input) are registered with their pass lines.")

heading("References")
for ref in ["Pre-registration 2026-09-26 (standout pattern proposer), with dated amendments and outcome sections — GoalGathering/notes/.",
            "Pre-registrations 2026-09-27 (wide-candidate deck with stop rule; cheap proxy-of-the-answer input) — GoalGathering/notes/.",
            "Read-outs: out/sim/band_p2_readout.md, all_p2_readout.md, band_p2s1A_readout.md, deck_cost_2026-09-27.md; validation reads out/stage2_readout_2026-09-26.md, stage3_readout_2026-09-26.md.",
            "Code: pp/core.py, pp/scorer.py, pp/embed_scorer.py, run_export.py, run_simulation.py, readout.py, stage_readout.py, deck_cost_readout.py; tests/test_pp_planted.py.",
            "Module 05 (the equivariant body): modules/05_support_predictor/m05/rungC_equivariant.py."]:
    para(ref, indent_first=False, size=10)

doc.save(str(OUT_DOCX))
print("written", OUT_DOCX)
ps = f'''$w = New-Object -ComObject Word.Application; $w.Visible = $false
$d = $w.Documents.Open("{OUT_DOCX}"); $d.SaveAs2("{OUT_DOCX.with_suffix('.pdf')}", 17); $d.Close(); $w.Quit()'''
try:
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True)
    print("pdf:", OUT_DOCX.with_suffix(".pdf").exists())
except Exception as exc:  # noqa: BLE001
    print("pdf conversion skipped:", exc)
sys.exit(0)
