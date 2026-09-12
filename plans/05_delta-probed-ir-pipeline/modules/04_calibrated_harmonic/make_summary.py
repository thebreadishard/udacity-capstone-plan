#!/usr/bin/env python
"""Builds module_summary.docx (the Machine Learning Analysis Report) in the Udacity APA 7 template
(Rubrics/APA7_template.docx) with the sections the Module 04 instructions prescribe, then converts it to
module_summary.pdf with Word (COM automation through PowerShell). Run:  python make_summary.py
Every number in the text is read from notebook/training_table.csv and notebook/model_results.json (written by
the executed notebook); citations are APA author-year and the References list contains exactly the sources cited."""
import json, subprocess
from pathlib import Path
import pandas as pd
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parents[3] / "Rubrics" / "APA7_template.docx"
NB = HERE / "notebook"
FIG = NB / "figures"
OUT_DOCX = HERE / "module_summary.docx"

df = pd.read_csv(NB / "training_table.csv", dtype={"uid": str})
R = json.load(open(NB / "model_results.json", encoding="utf-8"))
O = R["overall"]; D = R["diagnostics"]; best = R["best_by_recipe_rule"]
unc = pd.read_csv(NB / "uncertainty_layer.csv", index_col=0)
n_rows, n_cols = df.shape
n_mol = df.uid.nunique()
NAMES = {"zero": "zero model (library as served)", "family_mean": "per-family constant", "ridge": "ridge regression", "hgb": "gradient-boosted trees"}

doc = Document(str(TEMPLATE))
for p in list(doc.paragraphs):
    p._element.getparent().remove(p._element)

def para(text="", bold=False, center=False, italic=False, size=None, indent_first=True):
    p = doc.add_paragraph()
    if center: p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if not indent_first: p.paragraph_format.first_line_indent = Pt(0)
    r = p.add_run(text); r.bold = bold; r.italic = italic
    if size: r.font.size = Pt(size)
    return p

def heading(text):
    p = doc.add_paragraph(); p.paragraph_format.first_line_indent = Pt(0); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text); r.bold = True
    return p

def page_break():
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

def figure(name, caption, width=6.0):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.first_line_indent = Pt(0)
    p.add_run().add_picture(str(FIG / name), width=Inches(width))
    c = doc.add_paragraph(); c.paragraph_format.first_line_indent = Pt(0)
    r = c.add_run(caption); r.italic = True; r.font.size = Pt(10)

def table(header, rows, caption):
    c = doc.add_paragraph(); c.paragraph_format.first_line_indent = Pt(0)
    r = c.add_run(caption); r.italic = True; r.font.size = Pt(10)
    t = doc.add_table(rows=1, cols=len(header))
    try: t.style = doc.styles["Table Grid"]
    except KeyError: pass
    for i, h in enumerate(header):
        cell = t.rows[0].cells[i]; cell.text = ""; run = cell.paragraphs[0].add_run(h); run.bold = True; run.font.size = Pt(9)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""; run = cells[i].paragraphs[0].add_run(str(v)); run.font.size = Pt(9)
    doc.add_paragraph()

TITLE = "Can a Model Learn the Error of Scaled-Harmonic DFT? A Leave-One-Molecule-Out Regression on Paired Computed and Laboratory PAH Bands"

for _ in range(6): para(indent_first=False)
para(TITLE, bold=True, center=True, indent_first=False)
para(indent_first=False)
para("Frederic Petrignani", center=True, indent_first=False)
para("Udacity AI Mastery Capstone", center=True, indent_first=False)
para("Module 04 — Applied Machine Learning: Model Design, Training, and Performance Evaluation", center=True, indent_first=False)
para("Machine Learning Analysis Report (module_summary.pdf)", center=True, indent_first=False)
para("12 September 2026", center=True, indent_first=False)
page_break()
para(TITLE, bold=True, center=True, indent_first=False)

heading("Overview")
para(f"I addressed a supervised regression problem: predicting, per infrared band of a polycyclic aromatic hydrocarbon "
     f"(PAH), the error that NASA's library of scaled-harmonic computed spectra makes against the laboratory band "
     f"position, from descriptors of the band and the molecule alone. The dataset is a paired table I derived from two "
     f"public libraries of the NASA Ames PAH IR Spectroscopic Database: the computed library version 4.00 "
     f"(https://www.astrochemistry.org/pahdb/theoretical/4.00; Ricca et al., 2026) and the experimental, argon-matrix "
     f"library version 3.10 (https://www.astrochemistry.org/pahdb/experimental/3.10; Mattioda et al., 2020). I trained "
     f"and compared a per-family constant, a ridge regression and a gradient-boosted tree ensemble against the "
     f"uncorrected library, under a recipe fixed before the first run.")

heading("Dataset Description")
para(f"Each row pairs one laboratory band with the computed band of the same molecule that the fixed join rule assigns "
     f"to it (nearest free computed band with intensity of at least 1 km/mol within ±30 cm⁻¹, laboratory bands taken in "
     f"descending intensity, one-to-one). The table has {n_rows:,} rows and {n_cols} columns for {n_mol} molecules of "
     f"10 to 50 carbon atoms, neutral, cationic and anionic. The target is y = ν(lab) − ν(scaled), in cm⁻¹; its mean is "
     f"{df.y_cm.mean():+.2f}, its standard deviation {df.y_cm.std():.2f}, and the mean absolute error of the uncorrected "
     f"library is {O['zero']['MAE']:.2f} cm⁻¹. Features per band are the unscaled harmonic frequency, the logarithm of "
     f"the computed intensity, the relative intensity within the molecule, the stored scale-factor region and a "
     f"frequency-range family label; per molecule the carbon and hydrogen counts, the charge, a nitrogen flag and four "
     f"hydrogen-adjacency counts. No laboratory quantity is a feature. The table is derived from public measured and "
     f"computed science data, is not AI-generated, and differs from my Module 02 dataset (the computed library) and my "
     f"Module 03 dataset (the laboratory bands): the pairing exists in neither.")

heading("Modeling Approach")
para("Preparation. The table has no missing values. The two categorical columns (family, scale-factor region) are one-hot "
     "encoded; the numeric features are standardised for the ridge model, whose penalty depends on feature scale, and "
     "passed through unchanged to the tree ensemble, which is invariant to monotone rescaling. The molecule identifier is "
     "kept as the grouping variable for the split and never used as a feature.")
para("Model selection. Four models were fixed in advance. The zero model predicts no correction and is the reference: "
     "it is the library as served. The per-family constant predicts each family's mean error in the training fold, the "
     "simplest recalibration of the scale factors. Ridge regression is the transparent linear baseline. Gradient-boosted "
     "trees (Friedman, 2001), in scikit-learn's histogram implementation with library defaults, can represent "
     "interactions between size, family and intensity that a linear model cannot. No hyper-parameter search was run: the "
     "recipe set the tuning budget to zero so that the baseline is reproducible from the defaults, with the random seed 0. "
     "The approach follows the machine-learning correction of DFT scale factors published by Bos et al. (2025), implemented "
     "independently on the public library's own frequencies.")
para("Evaluation. Bands of one molecule share that molecule's systematic error, so a random split of bands would place "
     "a molecule on both sides and reward memorising it; grouped cross-validation, holding out whole clusters, is the "
     "appropriate design when observations are structured in this way (Roberts et al., 2017). I therefore used "
     f"leave-one-molecule-out: {n_mol} folds, each molecule predicted by models that never saw any of its bands. The "
     "primary metric is the mean absolute error (MAE) of the corrected position against the laboratory band, because the "
     "larger project scores per-band absolute errors; the root-mean-square error, the coefficient of determination R² and "
     "the share of bands within 5 cm⁻¹ are reported beside it. The models assume that the descriptors carry information "
     "about the error, that pairs within a fold are exchangeable, and, for ridge, that the relation is additive in the "
     "features.")

heading("Results")
rows = [[NAMES[k], f"{O[k]['MAE']:.2f}", f"{O[k]['RMSE']:.2f}", f"{O[k]['R2']:.3f}", f"{O[k]['within_5']:.1%}"] for k in ["zero", "family_mean", "ridge", "hgb"]]
table(["model", "MAE (cm⁻¹)", "RMSE (cm⁻¹)", "R²", "within 5 cm⁻¹"], rows, f"Table 1. Held-out performance, leave-one-molecule-out over {n_mol} molecules and {n_rows:,} pairs.")
figure("fig1_residuals.png", "Figure 1. Residual of the corrected band position against the laboratory band: uncorrected library versus gradient-boosted trees (held out).")
figure("fig2_mae_by_family.png", "Figure 2. Held-out MAE per band family for the four models.")
figure("fig3_pred_vs_actual.png", "Figure 3. Gradient-boosted trees: predicted against actual error, held out.", width=4.6)
para(f"No model learns the error (Table 1). The best held-out MAE, {O[best]['MAE']:.2f} cm⁻¹ for the {NAMES[best]}, "
     f"improves on the uncorrected library's {O['zero']['MAE']:.2f} by less than a tenth of a wavenumber; R² is at most "
     f"{max(O[k]['R2'] for k in O):.3f}, and the share of bands within 5 cm⁻¹ moves from {O['zero']['within_5']:.1%} to "
     f"{O[best]['within_5']:.1%}. Figure 1 shows the two residual distributions lying on top of each other, with the same "
     f"heavy tails; Figure 2 shows that no family improves by more than a fraction of a wavenumber and that the tree model "
     f"is slightly worse than doing nothing in some families; Figure 3 shows the predicted error hardly varying with the "
     f"actual one. Two diagnostics locate the cause. An instance-level five-fold split, which lets a molecule sit on both "
     f"sides, gives the trees an MAE of {D['hgb_mae_instance_5fold']:.2f} cm⁻¹ — no better — so the failure is not a "
     f"consequence of the strict split. And the error decomposes into a per-molecule offset with a standard deviation of "
     f"{D['sd_molecule_mean_offset']:.2f} cm⁻¹ and band-to-band scatter within a molecule with a standard deviation of "
     f"{D['mean_within_molecule_sd']:.2f} cm⁻¹: what a molecule-level descriptor could predict is small, and the "
     f"band-level descriptors do not predict the rest. Restricting to the {D['n_strong']} strong laboratory bands changes "
     f"the picture only in level (MAE {D['mae_zero_strong']:.2f} uncorrected, {D['mae_hgb_strong']:.2f} with trees). "
     f"By the recipe's rule the baseline column for the larger project is the {NAMES[best]}; the uncertainty layer it "
     f"provides is wide: 68 % of held-out absolute residuals lie within {unc.loc['all families', 'q68']:.1f} cm⁻¹ and 95 % "
     f"within {unc.loc['all families', 'q95']:.1f} cm⁻¹.")

heading("Interpretation for a Non-Technical Audience")
para("Computers can predict where a molecule's infrared \"fingerprint\" lines fall, but the predictions are a little "
     "off, and chemists routinely multiply them by a correction factor to bring them closer to what is measured. I asked "
     "whether a computer program could learn a smarter correction: given simple facts about a line and its molecule, can "
     "it guess how far off the prediction is for that particular line? The answer, tested fairly by always hiding the "
     "molecule being judged, is no. The learned corrections were no better than the plain correction factors already "
     "built into the library, and the reason is visible in the data: the remaining errors do not follow the size of the "
     "molecule or the type of line in any pattern the program could find. For my larger project this is useful rather "
     "than disappointing. It means the bar that a physics-based improvement has to clear is the library itself, about six "
     "and a half wavenumbers of typical error, and it means that the only way to do better is to compute the missing "
     "physics rather than to fit around it.")

heading("Limitations and Potential Bias")
para(f"Limitations. The pairing of laboratory and computed bands is itself a model: a fixed nearest-neighbour rule within "
     f"a window. About {D['share_abs_y_gt_15']:.0%} of pairs have an error above 15 cm⁻¹, larger than the published scale "
     f"of scaled-DFT-versus-matrix mismatch for these molecules (typically within 5, at worst about 15 cm⁻¹; Hudgins & "
     f"Sandford, 1998), so a fraction of the pairs are probably mis-assigned; such pairs inflate every model's error "
     f"equally and cap the attainable R². The laboratory side is argon-matrix data, not gas phase, so the learned "
     f"correction, had there been one, would have been a matrix-calibrated one. Only {n_mol} molecules of at most 50 "
     f"carbon atoms are available, and the four test molecules of the larger project are among them. The metrics are "
     f"averages over bands of unequal reliability, weak and strong alike.")
para("Bias and responsible use. The dataset over-represents the molecules that laboratory groups chose to measure — "
     "mostly compact, neutral or singly charged PAHs of 10 to 50 carbons — and any model trained on it would carry that "
     "selection into predictions for larger or differently shaped molecules. A second risk is specific to my project: "
     "this baseline is the opponent my own method will be compared with, so I had an interest in a weak baseline. The step "
     "taken against that interest was to fix the recipe — target, join, features, models, split, metrics, zero tuning "
     "and the rule for choosing the baseline column — in a note committed to version control before the first training "
     "run, and to report the diagnostics that would have exposed a split artefact. A stricter pairing rule is a plausible "
     "improvement, and it will be decided on its own merits before its effect on the model ranking is looked at.")
para("Use of AI assistance. This module was planned, coded and written with Claude (Anthropic) as an assistant under my "
     "direction; every run and decision is mine, every number traces to a named script and commit in the repository, and "
     "the text was revised against the actual outputs.")

page_break()
heading("References")
REFS = [
 "Bos, R., King, M., Calangian, A. J., Davin, K. A., McCraley, S., Putnam, R. A., Manjarrés, J., & Stoneburner, S. J. (2025). Ethereal AI: Infrared spectra of polycyclic aromatic hydrocarbons with machine learning DFT scaling factors. ACS Omega, 10(50), 62282–62290. https://doi.org/10.1021/acsomega.5c10225",
 "Friedman, J. H. (2001). Greedy function approximation: A gradient boosting machine. The Annals of Statistics, 29(5). https://doi.org/10.1214/aos/1013203451",
 "Hudgins, D. M., & Sandford, S. A. (1998). Infrared spectroscopy of matrix isolated polycyclic aromatic hydrocarbons. 1. PAHs containing two to four rings. The Journal of Physical Chemistry A, 102(2), 329–343. https://doi.org/10.1021/jp9834816",
 "Mattioda, A. L., Hudgins, D. M., Boersma, C., Bauschlicher, C. W., Jr., Ricca, A., Cami, J., Peeters, E., Sánchez de Armas, F., Puerta Saborido, G., & Allamandola, L. J. (2020). The NASA Ames PAH IR Spectroscopic Database: The laboratory spectra. The Astrophysical Journal Supplement Series, 251(2), 22. https://doi.org/10.3847/1538-4365/abc2c8",
 "Ricca, A., Boersma, C., Maragkoudakis, A., Roser, J. E., Shannon, M. J., Allamandola, L. J., & Bauschlicher, C. W., Jr. (2026). The NASA Ames PAH IR Spectroscopic Database: Computational version 4.00, software tools, website, and documentation. The Astrophysical Journal Supplement Series, 282(1), 7. https://doi.org/10.3847/1538-4365/ae1c38",
 "Roberts, D. R., Bahn, V., Ciuti, S., Boyce, M. S., Elith, J., Guillera-Arroita, G., Hauenstein, S., Lahoz-Monfort, J. J., Schröder, B., Thuiller, W., Warton, D. I., Wintle, B. A., Hartig, F., & Dormann, C. F. (2017). Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. Ecography, 40(8), 913–929. https://doi.org/10.1111/ecog.02881",
]
for ref in REFS:
    p = doc.add_paragraph(); p.paragraph_format.first_line_indent = Inches(-0.5); p.paragraph_format.left_indent = Inches(0.5)
    p.add_run(ref)

doc.save(str(OUT_DOCX)); print("written", OUT_DOCX)
ps = f'''$w = New-Object -ComObject Word.Application; $w.Visible = $false
$d = $w.Documents.Open("{OUT_DOCX}"); $d.SaveAs2("{OUT_DOCX.with_suffix('.pdf')}", 17); $d.Close(); $w.Quit()'''
r = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True)
print("pdf:", OUT_DOCX.with_suffix(".pdf").exists(), r.stderr[:300])
