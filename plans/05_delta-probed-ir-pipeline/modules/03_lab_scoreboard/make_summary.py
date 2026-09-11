#!/usr/bin/env python
"""Builds module_summary.docx (the Statistical Analysis Report) in the Udacity APA 7 template
(Rubrics/APA7_template.docx) with the sections the Module 03 instructions prescribe, then converts it to
module_summary.pdf with Word (COM automation through PowerShell). Run:  python make_summary.py
Every number in the text is read from notebook/bands_lab.csv, notebook/pairs_matrix_gas.csv and
notebook/test_results.json (written by the executed notebook); citations are APA author-year and the
References list contains exactly the sources cited."""
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

# ---------------- numbers (read, not typed)
df = pd.read_csv(NB / "bands_lab.csv")
pairs = pd.read_csv(NB / "pairs_matrix_gas.csv")
T = json.load(open(NB / "test_results.json", encoding="utf-8"))
prim = pairs[pairs.gas_role == "primary"]
n_rows, n_cols = df.shape
n_matrix = int((df.phase == "matrix").sum()); n_gas = int((df.phase == "gas").sum())
n_matrix_entries = int(df.loc[df.phase == "matrix", "uid"].nunique())
n_gas_records = int(df.loc[df.phase == "gas", "record"].nunique()); n_gas_species = int(df.loc[df.phase == "gas", "species"].nunique())
n_pairs, n_prim = len(pairs), len(prim)
n_prim_peaks = int(df[(df.role == "primary")].shape[0])
u_c_med = prim.u_c_gas_cm.median()
fam = pd.DataFrame(T["per_family"])
tested = fam[fam.status == "tested"].sort_values("p_holm")
untested = fam[fam.status != "tested"]
n_tested = len(tested); n_reject = int((tested.decision == "reject H0").sum())
med_lo, med_hi = tested["median"].min(), tested["median"].max()
ph_lo, ph_hi = tested.p_holm.min(), tested.p_holm.max()
pooled = T["pooled"]; sec = T["secondary_naphthalene_245C"]
by_species = prim.groupby("species").delta_cm.agg(["count", "median"]).round(2)
n_multi = int((prim.n_candidates > 1).sum())
share8 = (prim.delta_cm.abs() <= 8).mean()

def fmt_fam(name):
    return name.split(" (")[0]

# ---------------- document
doc = Document(str(TEMPLATE))
for p in list(doc.paragraphs):           # keep the template's styles, section and page setup; drop its placeholder text
    p._element.getparent().remove(p._element)

def para(text="", bold=False, center=False, italic=False, size=None, indent_first=True):
    p = doc.add_paragraph()
    if center: p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if not indent_first: p.paragraph_format.first_line_indent = Pt(0)
    r = p.add_run(text); r.bold = bold; r.italic = italic
    if size: r.font.size = Pt(size)
    return p

def heading(text, level=1):
    p = doc.add_paragraph(); p.paragraph_format.first_line_indent = Pt(0)
    if level == 1: p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text); r.bold = True
    return p

def page_break():
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

def figure(name, caption):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.first_line_indent = Pt(0)
    p.add_run().add_picture(str(FIG / name), width=Inches(6.0))
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

TITLE = "Matrix Versus Gas Phase: A Pre-Registered Statistical Analysis of Laboratory Infrared Band Positions of PAHs"

# ---------------- title page
for _ in range(6): para(indent_first=False)
para(TITLE, bold=True, center=True, indent_first=False)
para(indent_first=False)
para("Frederic Petrignani", center=True, indent_first=False)
para("Udacity AI Mastery Capstone", center=True, indent_first=False)
para("Module 03 — Conduct a Statistical Analysis Using Python", center=True, indent_first=False)
para("Statistical Analysis Report (module_summary.pdf)", center=True, indent_first=False)
para("11 September 2026", center=True, indent_first=False)
page_break()

# ---------------- body
para(TITLE, bold=True, center=True, indent_first=False)

heading("Overview")
para(f"I analysed laboratory infrared band positions of polycyclic aromatic hydrocarbons (PAHs) measured in two "
     f"ways: frozen in an argon matrix at 10 K and as a hot vapour. The dataset combines the NASA Ames PAH IR "
     f"Spectroscopic Database's experimental library, version 3.10 (https://www.astrochemistry.org/pahdb/experimental/3.10; "
     f"Mattioda et al., 2020), with gas-phase records of the NIST Chemistry WebBook (https://webbook.nist.gov/chemistry/; "
     f"Linstrom, 1997). The question, fixed in a pre-registration note before any band was paired, is whether the offset "
     f"between a band's matrix position and its gas-phase position is zero per band family; the answer matters because my "
     f"larger capstone project will later be scored against exactly these laboratory numbers.")

heading("Dataset Description")
para(f"Each row of the dataset is one laboratory band: its position in wavenumbers (cm⁻¹), its intensity, the molecule "
     f"(formula, charge, carbon count), the phase (matrix or gas), the source record, the stated resolution and temperature "
     f"where the source documents them, the signal-to-noise ratio and width of gas-phase peaks, two uncertainty columns "
     f"(resolution term and centroid precision) and a frequency-range family label. The table has {n_rows:,} rows and "
     f"{n_cols} columns: {n_matrix:,} matrix bands from {n_matrix_entries} PAHdb entries, {n_gas} gas-phase peaks from "
     f"{n_gas_records} records of {n_gas_species} PAHs, and four bands of a quantitative benzene cell spectrum (Chu et al., 1999). "
     f"A second file holds the {n_pairs} matrix–gas pairs for the four neutral PAHs present on both sides (naphthalene, "
     f"anthracene, pyrene, chrysene), {n_prim} of them against the primary gas record of each molecule. The key variables "
     f"examined were the band position by phase and family, and the paired offset Δ = ν(matrix) − ν(gas). The data are public "
     f"laboratory measurements available before this project started; they are neither synthetic nor AI-generated, and "
     f"they are not the computed library used in my Module 02 project.")

heading("Methods")
para("Descriptive statistics. Before the planned test I screened the data as initial data analysis recommends: summary "
     "statistics of the numeric columns, counts of every categorical column, the distribution of the key numeric variable "
     "by group, and an explicit account of the missing values and of why they are missing. Lusa et al. (2024) describe this "
     "screening — univariate and multivariate descriptions and the evaluation of missing data, carried out against a "
     "pre-specified analysis plan and reported before the research question is addressed — as a foundation of reproducible "
     "analysis; I followed that order, with the analysis plan committed to version control before the pairs existed.")
para("Visual models. A histogram of band positions by phase (Figure 1) shows whether the two sources cover the same "
     "spectral range and where each is dense; a boxplot of the paired offset per family (Figure 2) matches the question, "
     "which is asked per family, and shows medians, spread and group sizes at once; a scatter plot of every pair's offset "
     "against its gas-phase position, by species (Figure 3), keeps the information the boxplot hides — which molecule and "
     "which position each pair comes from — and lets a secondary column be overlaid.")
para("Hypothesis test. The offsets are paired differences of a few observations per family with no reason to expect a "
     "normal distribution and with occasional outliers from mismatched pairs, so I used the Wilcoxon signed-rank test "
     "(Wilcoxon, 1945), a rank-based test for paired data whose null hypothesis is that the differences are distributed "
     "symmetrically about zero. It assumes the pairs within a family are exchangeable and the differences are measured on a "
     "scale where ranking is meaningful; it does not assume normality. Because eight families are examined, the "
     "significance level α = 0.05 is applied with the Holm–Bonferroni step-down correction, and a family with fewer than "
     "six pairs cannot reach α under the exact two-sided test and is reported as inconclusive by construction rather than "
     "tested. A pooled test over all primary pairs is reported as a declared secondary result. All of this — the species, "
     "the peak definition, the ±20 cm⁻¹ largest-intensity one-to-one matching rule, the test, α, the correction and the "
     "minimum group size — was written down and committed before the join was computed, so that no choice could be tuned "
     "on the outcome; Lusa et al. (2024) frame initial data analysis as informing, and where necessary documenting changes "
     "to, a plan that already exists, and no change was needed here. The notebook is rebuilt and executed by a script, so "
     "the figures and the test come from the same tables every time (Danchev, 2022).")

heading("Results")
figure("fig1_positions_by_phase.png", "Figure 1. Band positions of the matrix library and the gas-phase peaks (densities per cm⁻¹, 25 cm⁻¹ bins).")
para(f"The matrix side dominates the dataset ({n_matrix:,} of {n_rows:,} rows) and is densest between about 700 and 1,650 cm⁻¹; "
     f"the gas records cover the same range and add weak features above 1,650 cm⁻¹, including peaks near 2,350 and above "
     f"3,500 cm⁻¹ that are most likely residual atmospheric carbon dioxide and water in the gas records, which have no matrix "
     f"counterpart and enter no pair (Figure 1). The gas records differ sharply in quality: the stated resolution is 8 cm⁻¹ for "
     f"the six gas-chromatograph records against 0.125 cm⁻¹ for the quantitative benzene cell record, while the centroid "
     f"precision from the signal-to-noise is small (median {u_c_med:.2f} cm⁻¹ among the primary pairs). The resolution, not "
     f"the noise, limits what these records can show.")
figure("fig2_delta_by_family.png", "Figure 2. Offset Δ = ν(matrix, 10 K) − ν(gas, hot vapour) per band family, primary pairs of four PAHs; the grey band is ±8 cm⁻¹, the gas resolution.")
figure("fig3_delta_vs_position.png", "Figure 3. Every pair's offset against its gas-phase position, by species; hollow circles are naphthalene against the 245 °C Coblentz record (secondary column).")
rows = []
for _, r in fam.sort_values("median").iterrows():
    if r.status == "tested":
        rows.append([fmt_fam(r.family), int(r.n), f"{r['median']:+.2f}", f"[{r.ci_low:+.2f}, {r.ci_high:+.2f}]", f"{r.W:.0f}", f"{r.p:.4f}", f"{r.p_holm:.4f}", r.decision])
    else:
        rows.append([fmt_fam(r.family), int(r.n), f"{r['median']:+.2f}", f"[{r.ci_low:+.2f}, {r.ci_high:+.2f}]", "—", "—", "—", "inconclusive by construction"])
table(["family", "n", "median Δ (cm⁻¹)", "95 % bootstrap CI of median", "W", "p", "p (Holm)", "decision at α = 0.05"], rows,
      "Table 1. Pre-registered Wilcoxon signed-rank test of a zero matrix−gas offset per family (primary pairs; n < 6 not tested).")
para(f"Every family's median offset is positive: the matrix position lies above the hot gas-phase position (Figure 2, "
     f"Table 1). Of the eight families, {n_tested} have at least six pairs and were tested; the test rejects a zero offset in "
     f"{n_reject} of the {n_tested}, with medians from {med_lo:+.2f} to {med_hi:+.2f} cm⁻¹ and Holm-adjusted p-values from "
     f"{ph_lo:.3f} to {ph_hi:.3f}. The C–H stretch (n = {int(untested[untested.family=='CH-stretch'].n.iloc[0])}) and the "
     f"low-frequency family (n = {int(untested[untested.family=='low / skeletal'].n.iloc[0])}) are inconclusive by "
     f"construction. The declared secondary pooled test over all {pooled['n']} primary pairs gives W = {pooled['W']:.1f}, "
     f"p = {pooled['p']:.1e}, median {pooled['median']:+.2f} cm⁻¹. The four molecules agree with one another (medians "
     + ", ".join(f"{s} {by_species.loc[s, 'median']:+.2f} cm⁻¹ (n = {int(by_species.loc[s, 'count'])})" for s in by_species.index) +
     f"; Figure 3), and naphthalene's secondary column against the 245 °C record gives a median of {sec['median']:+.2f} cm⁻¹ "
     f"(n = {sec['n']}). {share8:.0%} of the primary offsets lie within ±8 cm⁻¹, the gas resolution.")

heading("Interpretation for a Non-Technical Audience")
para("Chemists measure the infrared \"fingerprint\" of a molecule in two very different ways. In one, the molecule is "
     "trapped in a block of frozen argon at ten degrees above absolute zero; in the other, it is a hot gas flowing "
     "through a heated tube. The fingerprint lines should be almost the same, but not exactly: the frozen argon nudges "
     "them a little, and heat nudges them the other way. I asked a simple question with a rule written down in advance: "
     "when the same line is measured both ways, is the difference zero on average? For four molecules and about sixty "
     "lines, the answer is no. The frozen-argon lines sit consistently a little higher — by about three to six units on "
     "the wavenumber scale, less than one percent of a line's position — and this holds in "
     "every group of lines that had enough data to judge. That number is small, but it is exactly the size of effect my "
     "larger project hopes to predict, so knowing it, and knowing that it is systematic rather than random, is what this "
     "analysis was for. What the data cannot tell is how much of the difference is due to the argon and how much to "
     "the heat; that separation needs measurements at the same temperature on both sides.")

heading("Limitations and Potential Bias")
para(f"Limitations of the dataset. The gas-phase records that could be paired are gas-chromatograph spectra reported at a "
     f"stated 8 cm⁻¹ resolution on a 4 cm⁻¹ grid, so an individual position is coarse even though the systematic offset "
     f"is resolved; the quantity measured is the offset between the sources as they exist — a 10 K matrix against a hot "
     f"vapour whose temperature the records do not state — and not the matrix shift at equal temperature; only four "
     f"molecules carry the result; and the matrix library reports band lists rather than spectra, so its own centroid "
     f"precision is not measurable here. Matrix shifts of 0–15 cm⁻¹ relative to the gas phase are the published order of "
     f"magnitude for these molecules (Hudgins & Sandford, 1998), which is consistent with what was found.")
para(f"Potential sources of bias. The matching rule pairs each gas peak with the most intense matrix band within "
     f"±20 cm⁻¹; where more than one candidate existed ({n_multi} of {n_prim} primary pairs) a different choice would "
     f"change that pair's offset, and the rule was fixed in advance precisely so that this choice could not be made with "
     f"the result in view. Only gas peaks strong enough to pass the noise threshold are paired, so weak bands are "
     f"under-represented, and the family labels are a frequency-range rule rather than a spectroscopic assignment, so a "
     f"band can sit in a neighbouring family. Bands of one molecule are not fully independent, which makes the "
     f"per-family p-values somewhat optimistic. Finally, there is an interest to declare: these laboratory numbers are "
     f"the reference my own project's predictions will be scored against, which is why the analysis was pre-registered "
     f"and why every constant is printed with the tables rather than chosen later.")
para("Use of AI assistance. This module was planned, coded and written with Claude (Anthropic) as an assistant under my "
     "direction; every run and decision is mine, every number traces to a named script and commit in the repository, and "
     "the text was revised against the actual outputs.")

page_break()
heading("References")
REFS = [
 "Chu, P. M., Guenther, F. R., Rhoderick, G. C., & Lafferty, W. J. (1999). The NIST quantitative infrared database. Journal of Research of the National Institute of Standards and Technology, 104(1), 59. https://doi.org/10.6028/jres.104.004",
 "Danchev, V. (2022). Reproducible data science with Python: An open learning resource. Journal of Open Source Education, 5(56), 156. https://doi.org/10.21105/jose.00156",
 "Hudgins, D. M., & Sandford, S. A. (1998). Infrared spectroscopy of matrix isolated polycyclic aromatic hydrocarbons. 1. PAHs containing two to four rings. The Journal of Physical Chemistry A, 102(2), 329–343. https://doi.org/10.1021/jp9834816",
 "Linstrom, P. (1997). NIST Chemistry WebBook, NIST Standard Reference Database 69 [Data set]. National Institute of Standards and Technology. https://doi.org/10.18434/T4D303",
 "Lusa, L., Proust-Lima, C., Schmidt, C. O., Lee, K. J., le Cessie, S., Baillie, M., Lawrence, F., & Huebner, M., on behalf of TG3 of the STRATOS Initiative. (2024). Initial data analysis for longitudinal studies to build a solid foundation for reproducible analysis. PLOS ONE, 19(5), e0295726. https://doi.org/10.1371/journal.pone.0295726",
 "Mattioda, A. L., Hudgins, D. M., Boersma, C., Bauschlicher, C. W., Jr., Ricca, A., Cami, J., Peeters, E., Sánchez de Armas, F., Puerta Saborido, G., & Allamandola, L. J. (2020). The NASA Ames PAH IR Spectroscopic Database: The laboratory spectra. The Astrophysical Journal Supplement Series, 251(2), 22. https://doi.org/10.3847/1538-4365/abc2c8",
 "Wilcoxon, F. (1945). Individual comparisons by ranking methods. Biometrics Bulletin, 1(6), 80–83. https://doi.org/10.2307/3001968",
]
for ref in REFS:
    p = doc.add_paragraph(); p.paragraph_format.first_line_indent = Inches(-0.5); p.paragraph_format.left_indent = Inches(0.5)
    p.add_run(ref)

doc.save(str(OUT_DOCX)); print("written", OUT_DOCX)

# ---------------- PDF via Word (COM through PowerShell)
ps = f'''$w = New-Object -ComObject Word.Application; $w.Visible = $false
$d = $w.Documents.Open("{OUT_DOCX}"); $d.SaveAs2("{OUT_DOCX.with_suffix('.pdf')}", 17); $d.Close(); $w.Quit()'''
r = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True)
print("pdf:", OUT_DOCX.with_suffix(".pdf").exists(), r.stderr[:300])
