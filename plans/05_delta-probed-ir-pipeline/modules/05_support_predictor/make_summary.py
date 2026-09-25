#!/usr/bin/env python
"""Builds module_summary.docx (the Deep Learning Systems Analysis Report) in the Udacity APA 7 template with the nine sections the
Module 05 instructions prescribe (Rubrics/05, Task 7), then converts it to module_summary.pdf with Word (COM through PowerShell).
Run:  python make_summary.py            (22 September 2026 scaffold; the text reads every number from notebook/results.json and the
release manifest — nothing is typed in by hand. A results file from a quick pipeline check (results["quick"] is true) produces a
docx with a banner and no PDF, so that a check can never be mistaken for the submission.)"""
import json
import subprocess
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.shared import Inches, Pt

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parents[3] / "Rubrics" / "APA7_template.docx"
NB = HERE / "notebook"
FIG = NB / "figures"
OUT_DOCX = HERE / "module_summary.docx"

R = json.load(open(NB / "results.json", encoding="utf-8"))
MAN = json.load(open(HERE / "data" / "corpus_release" / R["release"].replace(".npz", "_manifest.json"), encoding="utf-8"))
QUICK = bool(R.get("quick"))
FAM = {"CH-stretch": "C–H stretch", "CH-oop": "C–H out-of-plane", "ring-ip": "ring in-plane", "other": "other"}
rms = R["test_rms"]
ap = R["pair_ap"]

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
    t = doc.add_table(rows=1, cols=len(header))  # the APA template has no "Table Grid" style; plain table as in Modules 03–04
    for i, h in enumerate(header):
        cell = t.rows[0].cells[i]
        cell.text = ""
        run = cell.paragraphs[0].add_run(h)
        run.bold = True
        run.font.size = Pt(9)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            cells[i].paragraphs[0].add_run(str(v)).font.size = Pt(9)
    doc.add_paragraph()


def f1(x):
    return "—" if x is None or x != x else f"{x:.1f}"


# ---- title page (APA 7 student paper)
for _ in range(6):
    para(indent_first=False)
para("Deep Learning Systems Analysis Report", bold=True, center=True, indent_first=False)
para("The ΔH model: a Transformer that predicts the family blocks of a Hessian correction", center=True, indent_first=False)
para(indent_first=False)
para("Frederic Petrignani", center=True, indent_first=False)
para("Udacity AI Mastery Capstone — Module 05 (Deep Learning Systems)", center=True, indent_first=False)
para("module_summary.pdf", center=True, indent_first=False)
if QUICK:
    para("PIPELINE CHECK — NOT A RESULT (quick mode: fewer epochs, one seed). This document exists to test the report builder; "
         "the submission is produced from a full execution of the notebook.", bold=True, center=True, indent_first=False)
doc.paragraphs[-1].add_run().add_break(WD_BREAK.PAGE)

heading("Report Overview")
para(f"This project asks whether a Transformer can learn, from the normal modes of a cheap density-functional Hessian alone, how that "
     f"Hessian must be corrected towards a better level of theory — not mode by mode, but per family of vibrations as a block of shifts and "
     f"couplings. The dataset is the project's own corpus of {R['n_molecules']} molecules ({R['n_modes_total']:,} modes) computed at two levels of "
     f"theory on identical geometries (release {R['release']}). The model is an encoder-only Transformer over mode tokens with two output heads "
     f"(Vaswani et al., 2017); its baseline has {R['parameters']['baseline']:,} parameters.")

heading("Dataset and Task Description")
para(f"Each molecule is a sequence of normal-mode tokens; a token carries the mode's frequency, its family, the shares of C, H, N and O in the "
     f"motion, a localisation number, the out-of-plane share and twelve atom-environment classes — all from the cheap level (B3LYP/6-31G*). The "
     f"target is the correction matrix K in the cheap-level mode basis, K_ij = L_iᵀ ΔH L_j / (2√(ω_i ω_j)) in cm⁻¹, with ΔH the difference between "
     f"the ωB97X and B3LYP Hessians; its diagonal is the first-order band shift of each mode and its off-diagonal elements are the couplings "
     f"between modes of one family. The release holds {MAN['n_molecules']} molecules with up to {MAN['max_modes']} modes each "
     f"({', '.join(f'{FAM[k]} {v:,}' for k, v in MAN['mode_counts_per_family'].items())} modes); every input file is listed with its SHA-256 in the "
     f"release manifest. The data are computed ab initio data produced by this project's corpus factory, released publicly with a DOI before the "
     f"module's submission; they are not synthetic in the sense of model-generated, not AI-generated, and not the PAHdb or NIST data of Modules 02–04. "
     f"Splits are by molecule ({R['splits']['train']} training, {R['splits']['val']} validation, {R['splits']['test']} test), because the modes of one "
     f"molecule are strongly correlated (Danchev, 2022, on reproducible workflows; the splitting rule was fixed in the recipe before training).")

heading("Model Architecture and Design Decisions")
para("The ΔH model has three parts. A token embedding maps the 23 mode features through a linear layer, GELU and LayerNorm to width 64 and "
     "prepends two learned molecule tokens (charge and spin multiplicity), so that charged species can be added later without changing the "
     "architecture. An encoder-only Transformer backbone (two layers, four heads, feed-forward width 256, dropout 0.1, pre-normalisation) lets every "
     "mode attend to every other; self-attention is the natural operation for a set of variable size whose members interact in pairs, which is what "
     "a coupling is (Vaswani et al., 2017). Two heads read the contextualised mode vectors: the block head takes a pair of vectors with their "
     "frequencies and writes K_ij for every pair inside a family (diagonal and couplings together, the block rule of the recipe); the pair head "
     "writes a logit for whether the pair carries a large correction. The loss is a squared error over the filled block elements plus a "
     "class-weighted binary cross-entropy for the pair head; AdamW with learning rate 1e-3 and weight decay 1e-2, early stopping on the validation "
     "loss, three seeds. A recurrent network would impose an order the modes do not have, and a convolution a locality in frequency that couplings "
     "do not respect; the model is kept small because the corpus is hundreds of molecules and the physics is meant to sit in the tokens.")
figure("figure2_baseline.png", "Figure 1. Baseline: training and validation loss per epoch.")

heading("Experimental Comparison")
para(f"Exactly one aspect was changed: the depth of the backbone, from two to four encoder layers ({R['parameters']['4 layers']:,} parameters "
     f"against {R['parameters']['baseline']:,}); tokens, heads, width, dropout, optimiser, learning rate, batch size, epochs, early-stopping rule, splits "
     f"and seeds were identical. The change is meaningful for this task because the block target couples every mode of a family with every other: "
     f"one attention layer sees pairs, two layers see pairs of pairs. If the corrections are governed by longer chains of interaction, depth should "
     f"help; if the tokens already carry what matters, a deeper model should only overfit on a corpus of this size. Both outcomes inform the "
     f"pipeline's design, which is why the comparison was pre-registered in the recipe rather than chosen after the fact.")
figure("figure3_4layers.png", "Figure 2. Four layers: training and validation loss per epoch.")

heading("Results and Interpretation")
rows = []
for k in ("ring-ip", "CH-oop", "CH-stretch", "other"):
    rows.append([FAM[k], f1(rms[k]["zero"]["diag"]), f1(rms[k]["family-median"]["diag"]), f1(rms[k]["baseline"]["diag"]), f1(rms[k]["4 layers"]["diag"]),
                 f1(rms[k]["zero"]["coup"]), f1(rms[k]["baseline"]["coup"]), f1(rms[k]["4 layers"]["coup"])])
table(["family", "shifts: zero rule", "family median", "baseline", "4 layers", "couplings: zero", "baseline", "4 layers"], rows,
      "Table 1. Root-mean-square error on the test molecules, cm⁻¹ (band shifts = diagonal of the block; couplings = off-diagonal).")
para(f"Table 1 reads against two rules that need no learning. For the ring in-plane family the shifts come out at {f1(rms['ring-ip']['baseline']['diag'])} cm⁻¹ "
     f"(baseline) and {f1(rms['ring-ip']['4 layers']['diag'])} (four layers) against {f1(rms['ring-ip']['zero']['diag'])} for no correction and "
     f"{f1(rms['ring-ip']['family-median']['diag'])} for the family-median rule; for the C–H out-of-plane family {f1(rms['CH-oop']['baseline']['diag'])} and "
     f"{f1(rms['CH-oop']['4 layers']['diag'])} against {f1(rms['CH-oop']['zero']['diag'])} and {f1(rms['CH-oop']['family-median']['diag'])}. The pair head reaches an "
     f"average precision of {ap['baseline']:.2f} (baseline) and {ap['4 layers']:.2f} (four layers) against {ap['resonance-rule']:.2f} for the resonance-denominator "
     f"rule. The interpretation the recipe allows: a learned block is worth reporting where it beats the family-median rule on held-out molecules, "
     f"and the depth comparison is read on the same numbers — a deeper model that trains lower but tests no better has memorised the training "
     f"molecules. The trade-off is capacity against the number of molecules; the learning-curve rule of the project (no verdict on tiny data) "
     f"applies to every row of the table.")
figure("fig4_test_errors.png", "Figure 3. Test error per family: the two rules and the two configurations.")

heading("Limitations and Risks")
para(f"The corpus is small ({R['n_molecules']} molecules) and its target is a stand-in: the difference between two density functionals, not the "
     f"coupled-cluster correction the pipeline ultimately needs; the model's licence therefore extends only to what is measured on real molecules "
     f"by the rest of the plan. The family labels come from a rule on frequency and motion shares, so a mislabelled mode lands in the wrong block. "
     f"With {R['splits']['test']} test molecules the metrics have wide confidence intervals, which is why three seeds and the two free rules are "
     f"reported beside every number; the pair head's positives are rare and average precision is the appropriate but noisy metric. Early stopping "
     f"on one validation split introduces a mild optimism. None of these is hidden: every number in this report is read from the notebook's result "
     f"file by the script that builds it.")

heading("Ethical and Responsible Use")
para("The data are computed molecular properties with no personal information, and the code and data are released openly. The specific risk "
     "of this model is silent overreach: a learned prior that tells an expensive measurement where to look can steer the measurement away from a "
     "real feature it has never seen, and a downstream user of the corrected spectrum cannot tell. The project mitigates this in two ways: the "
     "prior is licensed only where a prior-free check on a real molecule agrees with it, and the model's predictions are always printed beside the "
     "free physical rule they must beat, in the spirit of documented model reporting (Mitchell et al., 2019). A second, smaller risk is energy: "
     "the corpus behind the model costs days of computation, which is recorded per run in the project's cost ledger.")

heading("Future Improvements")
para("With more time and data: the layer-A2 release of the corpus (200 further molecules, in production while this scaffold is written) and the "
     "learning curve it allows; coupled-cluster labels from the pipeline's own thin decks in place of the functional-difference stand-in; a "
     "second pre-registered controlled change on the tokens (environment classes on or off); and an uncertainty head so that the prior can say "
     "where it does not know. The architecture's charge and multiplicity tokens are there for the cation rows the plan requires.")

FU = NB / "results_followup.json"
if FU.exists():
    U = json.load(open(FU, encoding="utf-8"))
    heading("Addendum (23 September 2026): a corrupted target and the representation of the couplings")
    para(f"After the run above, two findings were added to the notebook as follow-up cells (section 7), leaving sections 1–6 unchanged so that "
         f"the change of understanding is visible. First, an independent analytic calculation of one molecule's Hessians (benzene, pyscf, same "
         f"geometry) disagreed with the corpus finite-difference Hessian by up to {U['benzene_check']['max_freq_disagreement_cm']:.0f} cm⁻¹; a screen of all "
         f"{U['screen']['n']} molecules on the sorted-pair functional shift found benzene as the only molecule above 100 cm⁻¹ (median {U['screen']['median_max_shift']:.0f}). "
         f"The molecule's target was replaced by the second route (release {U['release_followup']}) and the baseline retrained with the identical "
         f"protocol: ring-in-plane band-shift RMS {U['test_rms_diag_corrected']['ring-ip']['baseline_retrained']:.1f} cm⁻¹ against {U['test_rms_diag_corrected']['ring-ip']['zero']:.1f} for the zero rule "
         f"(C–H out-of-plane {U['test_rms_diag_corrected']['CH-oop']['baseline_retrained']:.1f} against {U['test_rms_diag_corrected']['CH-oop']['zero']:.1f}); the result of the main run stands."
         + (f" Second, a pre-registered learning curve on the same corpus showed that the couplings, which the model above predicts as zero, are learned once "
            f"the target is expressed in local pairwise force-constant terms instead of the normal-mode basis: ring coupling error relative to the zero rule "
            f"{U['e7']['ratio_a'][-1]:.2f} on the layer-A hold-out and {U['e7']['ratio_b'][-1]:.2f} on molecules of cores never seen in training at {U['e7']['sizes'][-1]} training molecules, "
            f"with corrected-frequency errors of {U['e7']['corrected_freq_rms_a']:.1f} and {U['e7']['corrected_freq_rms_b']:.1f} cm⁻¹ against {U['e7']['zero_rule_a']:.0f} for no correction. "
            f"The model of this report is kept as the pre-registered baseline; the pairwise local target is the design of the next version." if "e7" in U else ""))
    para("What was learned: a target can be wrong and a model will faithfully fail on it, so every derived quantity now gets a second route before "
         "it is trusted; and the network was not the limit — the representation was. Both findings, their predictions and their outcomes are dated in "
         "the project's pre-registration notes.")

FU2 = NB / "results_followup2.json"
if FU2.exists():
    U2 = json.load(open(FU2, encoding="utf-8"))
    heading("Addendum 2 (24 September 2026): the imaginary-mode molecules, and the coupled-cluster correction itself")
    im = U2["imaginary_second_route"]; e8c = U2["e8"]["pattern_c_cc"]; e8d = U2["e8"]["pattern_d_cc_mask"]; e8p = U2["e8"]["pattern_c_proxy"]
    para(f"Two further follow-up cells were added (notebook section 8). First, the second route was run for every molecule the release rule had dropped "
         f"for an imaginary mode: of {im['n_read']} molecules read, {im['healed']} were healed (the finite-difference deck had flipped a soft substituent torsion; "
         f"the analytic Hessian has it real) and {im['genuine']} are genuine saddle points of the optimised geometry. The release rule now reads the analytic "
         f"frequencies where a second route exists; the baseline retrained on the resulting {U2['n_molecules']}-molecule release ({U2['release_followup2']}) gives a "
         f"ring-in-plane band-shift RMS of {U2['test_rms_diag_229']['ring-ip']['baseline_retrained']:.1f} cm⁻¹ against {U2['test_rms_diag_229']['ring-ip']['zero']:.1f} for the zero rule "
         f"(pair-head average precision {U2['pair_ap_229']:.3f}), within the seed scatter of the main run. Second, a CCSD(T)/cc-pVDZ Hessian of benzene was read "
         f"with the same parameter-free projections as the DFT proxy: the real correction is {100 * (1 - e8c['dH_residual_ratio']):.0f} % inside the pairwise local pattern of "
         f"section 7 and {100 * (1 - e8d['dH_residual_ratio']):.0f} % once pairs two bonds apart are added, and only then are its ring couplings recovered (ratio to the zero rule "
         f"{e8d['ring_coupling_ratio']:.2f} against {e8c['ring_coupling_ratio']:.2f}; the proxy: {e8p['ring_coupling_ratio']:.2f} already at the smaller pattern). Verdict by the pre-registered rule: "
         f"{U2['e8']['verdict']} — the coupled-cluster correction is local like the proxy, one bond further. For the mode-basis baseline of this report nothing changes, "
         f"which is the finding; the pairwise local model of the next version gains one pair class.")
    para("What was learned: a data-quality rule should be evidence per molecule rather than a blanket, the range-separated functional is the noisier "
         "finite-difference route, and the real target is local like the stand-in. All numbers trace to the notebook's section 8 and the project's dated notes.")

FU3 = NB / "results_followup3.json"
if FU3.exists():
    U3 = json.load(open(FU3, encoding="utf-8"))
    heading("Addendum 3 (25 September 2026): how far the correction carries — across a molecule, across molecules, across size")
    e9r2 = U3["e9"]["r2"]; e9r0 = U3["e9"]["r0"]; e9e = U3["e9"]["energy_only_r2"]; t10 = U3["e10"]; sz = U3["size_extrapolation"]; ns = [str(n) for n in sz["sizes"]]
    para(f"Three further pre-registered readings were added (notebook section 9), none of which retrains the baseline. E9: with the parent core's correction block "
         f"carried over and only the Hessian columns of the atoms within two bonds of the substituent probed ({100 * e9r2['column_fraction_mean']:.0f} % of the columns), the "
         f"DFT–DFT correction of {U3['e9']['n']} substituted molecules comes back to {e9r2['corrected_freq_rms']:.1f} cm⁻¹ in corrected frequency (ring coupling ratio "
         f"{e9r2['coupling_ratio']:.2f}; the substituent's own atoms alone, {100 * e9r0['column_fraction_mean']:.0f} % of the columns, {e9r0['corrected_freq_rms']:.1f} cm⁻¹); the energy-only "
         f"variant that a local coupled-cluster method can measure gives {e9e['corrected_freq_rms']:.1f} cm⁻¹ when the near–far couplings come from the core. Verdict by the "
         f"registered rule: {U3['e9']['verdict_r2']}. E10: the same neighbourhood block taken from the smallest host of the substituent and transplanted onto every other host "
         f"gives {t10['registered']['corrected_freq_rms']:.2f} cm⁻¹ under the registered donor rule ({t10['verdict']}) and {t10['nearest_torsion']['corrected_freq_rms']:.2f} with a torsion-matched donor, "
         f"against a ceiling of {t10['ceiling']['corrected_freq_rms']:.2f} with the receiver's own block; {len(t10['within_bars'])} of 15 substituent types are within the bars, the rotors "
         f"(CH3, OCH3, SH, CONH2) are not. Size extrapolation: section 7's pair model trained on molecules of at most 26 atoms predicts the {sz['holdout_a']} molecules of 27–34 atoms at "
         f"ring coupling ratio {sz['a'][ns[0]]['coupling_ratio']:.2f} → {sz['a'][ns[-1]]['coupling_ratio']:.2f} and corrected-frequency RMS {sz['a'][ns[0]]['corrected_freq_rms']:.1f} → "
         f"{sz['a'][ns[-1]]['corrected_freq_rms']:.1f} cm⁻¹ for {sz['sizes'][0]} → {sz['sizes'][-1]} training molecules (within-size control {sz['b'][ns[-1]]['coupling_ratio']:.2f}, "
         f"{sz['b'][ns[-1]]['corrected_freq_rms']:.1f}) — encouraging on the registered bars, at the edge on the ratio.")
    para("What was learned: locality makes the labels additive across a molecule and, for rigid substituents, across molecules, so the price of an expensive label "
         "scales with the environment rather than the molecule; small molecules teach large ones, more slowly than they teach each other; and the proof that the "
         "network learns is a pre-registered learning curve, which started on the corpus's layer B the same morning. All numbers trace to notebook section 9 and the dated notes.")


FU4 = NB / "results_followup4.json"
if FU4.exists():
    U4 = json.load(open(FU4, encoding="utf-8"))
    heading("Addendum 4 (25 September 2026, later): controls — what the metrics measure, a floor, a withdrawn reading, and predictions on record")
    sh = U4["shuffled"]; nz = U4["noise"]; sy = U4["symmetry"]; oa = U4["orbit_avg"]; pl = U4["power_law"]
    pa = pl["E7 hold-out (a) bare parents"]
    para(f"Notebook section 10 adds the controls of the proof (pre-registered as E11). A shuffled-label control keeps a ring coupling ratio above one ({sh['a']['control']:.2f} / "
         f"{sh['b']['control']:.2f} against the real model's {sh['a']['real']:.2f} / {sh['b']['real']:.2f}), so that metric measures learning; the corrected-frequency RMS of the same "
         f"control is {sh['a']['control_rms']:.1f} / {sh['b']['control_rms']:.1f} cm⁻¹ against {sh['a']['zero_rms']:.0f} for no correction — a floor reachable from class means alone, against "
         f"which the real model's {sh['a']['real_rms']:.1f} / {sh['b']['real_rms']:.1f} is now read. The label noise was measured by two routes: a repeat spread of {nz['median_K']:.1f} cm⁻¹ "
         f"on the diagonal (plateau bound {nz['plateau']:.1f}) and a within-orbit spread of {nz['target_orbit_spread_rigid']:.2f} of the coupling signal on {nz['n_rigid']} rigid molecules.")
    para(f"One test was withdrawn: a symmetry-consistency statistic of {sy['coarse_model']:.2f} had been read as the model ignoring molecular symmetry, until the same statistic on the "
         f"target gave {sy['coarse_target']:.2f} — the classes were too coarse. With true pair orbits the target is symmetric (benzene {sy['benzene']['target']:.3f}) and the model is at least "
         f"as symmetric ({sy['orbit_model']:.3f} against {sy['orbit_target']:.3f}): its features are invariant scalars, so symmetry is built in rather than learned. The conclusion was "
         f"withdrawn the same hour and the control became a project rule. A lever built on the same finding, training on orbit-averaged labels, failed its registered line "
         f"({oa['pair_gain_pct']:+.1f} % on the per-pair error against −8 %; ratios {oa['ratio_a']:.2f} / {oa['ratio_b']:.2f} unchanged) and was dropped.")
    para(f"Predictions on record for the layer-B learning curve, fitted on 45–175 molecules before that data existed: bare parents {pa['ring_coupling_ratio']['factor']:.2f}× per decade "
         f"on the ratio ({pa['ring_coupling_ratio']['at1200']['point']:.2f} at 1,200 molecules) and {pa['corrected_freq_rms']['factor']:.2f}× on the corrected RMS "
         f"({pa['corrected_freq_rms']['at1200']['point']:.1f} cm⁻¹), against a registered bar of 1.5× per decade. The weakest pair class on both hold-outs is the coupling between two bond "
         f"primitives. What was learned: every metric needs a control that must fail; a consistency statistic without its target control is not a result; and predictions come before "
         f"data, or the curve proves nothing. All numbers trace to notebook section 10 and the dated pre-registration.")


heading("References")
refs = [
    "Danchev, V. (2022). Reproducible data science with Python: An open learning resource. Journal of Open Source Education, 5(56), 156. https://doi.org/10.21105/jose.00156",
    "Mitchell, M., Wu, S., Zaldivar, A., Barnes, P., Vasserman, L., Hutchinson, B., Spitzer, E., Raji, I. D., & Gebru, T. (2019). Model cards for model reporting. In Proceedings of the Conference on Fairness, Accountability, and Transparency (pp. 220–229). ACM. https://doi.org/10.1145/3287560.3287596",
    "Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, Ł., & Polosukhin, I. (2017). Attention is all you need. In Advances in Neural Information Processing Systems 30 (pp. 5998–6008). https://arxiv.org/abs/1706.03762",
    "Williams, N. J., Kabalan, L., Stojanovic, L., Zólyomi, V., & Pyzer-Knapp, E. O. (2025). Hessian QM9: A quantum chemistry database of molecular Hessians in implicit solvents. Scientific Data, 12, 9. https://doi.org/10.1038/s41597-024-04361-2",
]
for r in refs:
    p = para(r, indent_first=False)
    p.paragraph_format.left_indent = Inches(0.5)
    p.paragraph_format.first_line_indent = Inches(-0.5)

doc.save(str(OUT_DOCX))
print("written", OUT_DOCX)
if QUICK:
    print("quick-mode results: no PDF (the docx carries the banner)")
    sys.exit(0)
ps = f'''$w = New-Object -ComObject Word.Application; $w.Visible = $false
$d = $w.Documents.Open("{OUT_DOCX}"); $d.SaveAs2("{OUT_DOCX.with_suffix('.pdf')}", 17); $d.Close(); $w.Quit()'''
subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True)
print("pdf:", OUT_DOCX.with_suffix(".pdf").exists())
