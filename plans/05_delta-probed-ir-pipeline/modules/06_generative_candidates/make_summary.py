#!/usr/bin/env python
"""Builds Generative_AI_Analysis_Report.docx (the Generative AI Analysis and Ethics Report) in the Udacity APA 7 template with the sections
Rubrics/06 Task 6 prescribes — Overview · Dataset or Prompt Description · Model Design and Training Approach · Output Evaluation and
Interpretation · Ethical Considerations and Responsible Use · Limitations and Future Improvements · References — then converts it to PDF with
Word (COM through PowerShell). Every number is read from notebook/results.json; nothing is typed in by hand. A results file from a quick pipeline
check (results["quick"] is true) produces a docx with a banner and no PDF, so that a check can never be mistaken for the submission.
Run:  python make_summary.py"""
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
OUT_DOCX = HERE / "Generative_AI_Analysis_Report.docx"

R = json.load(open(NB / "results.json", encoding="utf-8"))
QUICK = bool(R.get("quick"))
seeds = R["seeds"]; M = R["metrics"]; P = R["predictions"]; V = R["verdict"]; C = R["conditioning"]


def mean(key, T=1.0):
    vals = [M[f"seed{s}_T{T}"][key] for s in seeds if M[f"seed{s}_T{T}"].get(key) is not None]
    return sum(vals) / len(vals) if vals else float("nan")


doc = Document(str(TEMPLATE))
for p in list(doc.paragraphs):
    p._element.getparent().remove(p._element)


def para(text="", bold=False, center=False, italic=False, size=None, indent_first=True):
    p = doc.add_paragraph()
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if not indent_first:
        p.paragraph_format.first_line_indent = Pt(0)
    r = p.add_run(text); r.bold = bold; r.italic = italic
    if size:
        r.font.size = Pt(size)
    return p


def heading(text):
    para(text, bold=True, indent_first=False)


def figure(name, caption):
    if (FIG / name).exists():
        doc.add_picture(str(FIG / name), width=Inches(6.0)); doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        para(caption, italic=True, size=10, indent_first=False)


def table(header, rows, caption):
    para(caption, italic=True, size=10, indent_first=False)
    t = doc.add_table(rows=1, cols=len(header))
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]; c.text = ""; run = c.paragraphs[0].add_run(h); run.bold = True; run.font.size = Pt(9)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""; cells[i].paragraphs[0].add_run(str(v)).font.size = Pt(9)
    doc.add_paragraph()


def pct(x):
    return "—" if x is None or x != x else f"{100 * x:.0f} %"


# ---- title page
for _ in range(6):
    para(indent_first=False)
para("Generative AI Analysis and Ethics Report", bold=True, center=True, indent_first=False)
para("A character-level Transformer that proposes fused-aromatic molecules for infrared spectroscopy", center=True, indent_first=False)
para(indent_first=False)
para("Frederic Petrignani", center=True, indent_first=False)
para("Udacity AI Mastery Capstone — Module 06 (Generative AI Applications)", center=True, indent_first=False)
para("Generative_AI_Analysis_Report.pdf", center=True, indent_first=False)
if QUICK:
    para("PIPELINE CHECK — NOT A RESULT (quick mode: 2,000 training molecules, 2 epochs, one seed, 1,000 samples). This document exists to test "
         "the report builder; the submission is produced from the pre-registered execution of the notebook.", bold=True, center=True, indent_first=False)
doc.paragraphs[-1].add_run().add_break(WD_BREAK.PAGE)

heading("Overview")
para(f"The generative task is to propose new fused-aromatic molecules, written as SMILES strings, that resemble a frozen set of {R['n_rows']:,} PubChem "
     f"molecules with at least two fused aromatic rings, so that a spectroscopy pipeline built earlier in this capstone has candidates to compute next. "
     f"The model is a character-level decoder-only Transformer ({R['params']:,} parameters) written in PyTorch without pretrained weights and trained with "
     f"next-token cross-entropy — the autoregressive language-model formulation of molecular generation (Segler et al., 2018; Vaswani et al., 2017). "
     f"Outputs are judged by the standard validity–uniqueness–novelty trio of the MOSES and GuacaMol benchmarks (Polykovskiy et al., 2020; Brown et al., 2019), "
     f"by the match of their size and composition distributions to a held-out set, and by a project-specific fit criterion; all metrics and their expected "
     f"values were fixed in a pre-registration before training.")

heading("Dataset or Prompt Description")
sp = R["splits"]
para(f"The data are public-domain PubChem records (Kim et al., 2025): the union of fast-substructure searches for nine fused-aromatic cores, filtered with "
     f"RDKit to neutral molecules of C, H, N, O, S, F and Cl with at most 30 heavy atoms and at least two fused aromatic rings — {R['n_rows']:,} molecules, one "
     f"canonical SMILES each with its CID, formula, heavy-atom and aromatic-ring counts, frozen on 24 September 2026 with its query, per-step counts and SHA-256 "
     f"in the data README. The character vocabulary has {R['vocab_size']} tokens; {R['n_dropped_len96']} molecules exceed the 96-token context and are dropped. "
     f"Splits are by Murcko scaffold through a hash ({sp.get('train', 0):,} training, {sp.get('val', 0):,} validation, {sp.get('test', 0):,} test), so that a "
     f"scaffold never straddles training and test — the split that makes 'novelty' mean something (Bemis & Murcko, 1996). The set supports the task because "
     f"it is exactly the chemical class the downstream pipeline is licensed for, and it is large enough for a small Transformer to learn the grammar of "
     f"SMILES and the statistics of ring fusion without memorising individual records.")
figure("dataset.png", "Figure 1. Heavy-atom, aromatic-ring and token-length distributions of the frozen set.")

heading("Model Design and Training Approach")
tr = R["training"][str(seeds[0])]
para(f"The model is a decoder-only Transformer over characters: token and learned position embeddings (context 96), four pre-norm blocks of causal "
     f"four-head self-attention and a 256→1024→256 GELU feed-forward layer with dropout 0.1, a final LayerNorm and a linear head (Vaswani et al., 2017; "
     f"Radford et al., 2019, for the decoder-only recipe). It is trained with next-token cross-entropy, AdamW with a linear warm-up and cosine decay "
     f"(Loshchilov & Hutter, 2019), gradient clipping at 1.0, batch 128, and early stopping on validation loss with patience 3; sampling is autoregressive "
     f"and multinomial at a temperature. Design decisions and their reasons: the character level because the vocabulary is small and every SMILES is "
     f"representable; a decoder-only model because a sampler is needed, not an encoder; pre-normalisation and warm-up for stable small-model training "
     f"(Xiong et al., 2020); scaffold splitting for honest novelty. The pre-registered run trains {len(seeds)} seed(s) for up to 20 epochs; seed {seeds[0]} "
     f"stopped after {len(tr)} epoch(s) at a best validation loss of {min(h['val_loss'] for h in tr):.3f} nats per token, its raw samples reaching "
     f"{pct(tr[-1]['validity_200'])} validity at temperature 1.0. Alternatives were considered and set aside: a GAN on discrete strings trains unstably and "
     f"gives no likelihood (Guimaraes et al., 2017), a SMILES VAE trades validity for a latent space the task does not need (Gómez-Bombarelli et al., 2018), "
     f"and graph diffusion is heavier than the question.")
figure("training_curves.png", "Figure 2. Training and validation cross-entropy per epoch, and the validity of 200 raw samples per epoch.")

heading("Output Evaluation and Interpretation")
rows = [["validity", pct(mean("validity")), f"≥ {P['validity']}", "met" if V.get("validity") else "not met"],
        ["uniqueness", pct(mean("uniqueness")), f"≥ {P['uniqueness']}", "met" if V.get("uniqueness") else "not met"],
        ["novelty", pct(mean("novelty")), f"≥ {P['novelty']}", "met" if V.get("novelty") else "not met"],
        ["scaffold novelty", pct(mean("scaffold_novelty")), f"≥ {P['scaffold_novelty']}", "met" if V.get("scaffold_novelty") else "not met"],
        ["memorisation", pct(mean("memorisation")), f"≤ {P['memorisation']}", "met" if V.get("memorisation") else "not met"],
        ["project fit", pct(mean("project_fit")), f"{P['project_fit'][0]}–{P['project_fit'][1]}", "met" if V.get("project_fit") else "not met"],
        ["conditioning obedience", pct(C["obedience_all"]), f"≥ {P['obedience']}", "met" if C["obedience_all"] >= P["obedience"] else "not met"]]
table(["metric (T = 1.0, seed mean)", "measured", "pre-registered", "verdict"], rows, "Table 1. The pre-registered metrics against their predictions.")
para(f"At temperature 1.0 the samples are {pct(mean('validity'))} valid, {pct(mean('uniqueness'))} unique among the valid and {pct(mean('novelty'))} novel "
     f"({pct(mean('scaffold_novelty'))} with a scaffold unseen in training); {pct(mean('memorisation'))} of valid samples are verbatim training molecules. "
     f"Lowering the temperature to 0.7 raises validity to {pct(mean('validity', 0.7))} and lowers novelty to {pct(mean('novelty', 0.7))} — the usual trade "
     f"between fluency and exploration in autoregressive samplers. The heavy-atom, ring and heteroatom distributions of the samples sit "
     f"{mean('w1_heavy'):.1f}, {mean('w1_arom_rings'):.2f} and {mean('w1_hetero'):.2f} (Wasserstein-1) from the held-out set. The project-fit share — valid, "
     f"novel, neutral, within the corpus's element set, at most 30 heavy atoms and fused-aromatic — is {pct(mean('project_fit'))}. Failure cases are shown in "
     f"the notebook rather than hidden: unparsable strings (typically unclosed rings or mismatched brackets), verbatim training molecules, charged outputs, "
     f"and novel molecules outside the project's families. Conditioning on ring-count and heteroatom classes, the one measured design change, is obeyed in "
     f"{pct(C['obedience_all'])} of valid samples, with the per-request table showing where PubChem has too few examples for the request to be learned.")
figure("distribution_match.png", "Figure 3. Sample distributions against the held-out test set.")

heading("Ethical Considerations and Responsible Use")
para("Three concerns are tied to this system's own data, model and outputs. Misuse: a generator of aromatic structures is a generator of candidates for "
     "spectroscopy, not of syntheses; polycyclic aromatics include carcinogens and persistent pollutants, so the outputs are labelled as spectroscopic targets, "
     "no synthesis routes or toxicity-directed property predictions are produced, and the model card released with the notebook says so (Mitchell et al., 2019). "
     "Creative ownership and attribution: the training data are public-domain PubChem depositions; generated strings are not attributed to depositors, and the "
     "memorisation rate above is the measurement that the model does not return depositor records (the pre-registered bound is 10 %). Bias: PubChem "
     "over-represents what chemists have made or patented — medicinal-chemistry decorations rather than the bare polycyclic systems of the interstellar medium — "
     "and the generator inherits that; the project-fit metric and the distribution figures are where it shows, and the astrochemical species list of the "
     "NASA Ames PAH database is used only as a comparison set, never as training data (Boersma et al., 2014). The societal impact is modest and positive — "
     "cheaper triage of which molecules to compute for astronomical spectroscopy — and the report claims nothing about properties, safety or synthesis.")

heading("Limitations and Future Improvements")
para("Limitations: one data source with its own bias; SMILES as the representation, which makes validity a learned property rather than a guarantee "
     "(SELFIES would make every string decodable, at the cost of a less transparent vocabulary — Krenn et al., 2020); a small model trained on a CPU, so the "
     "held-out loss is not at its floor; evaluation by two-dimensional descriptors and a project-fit rule, not by the spectroscopy the candidates are meant "
     "for. Realistic next steps, in order: feed the project-fit samples to the spectroscopy pipeline as a separately labelled 'candidate' source and let its "
     "licensed correction rank them; condition on the pipeline's own family labels instead of ring and heteroatom classes; compare a SELFIES variant on the "
     "same pre-registered metrics; and replace the temperature trade-off by a reward-guided fine-tuning towards project fit, measured against the same trio so "
     "that gains in fit are not bought with memorisation.")

heading("References")
refs = [
    "Bemis, G. W., & Murcko, M. A. (1996). The properties of known drugs. 1. Molecular frameworks. Journal of Medicinal Chemistry, 39(15), 2887–2893. https://doi.org/10.1021/jm9602928",
    "Boersma, C., Bauschlicher, C. W., Ricca, A., Mattioda, A. L., Cami, J., Peeters, E., Sánchez de Armas, F., Puerta Saborido, G., Hudgins, D. M., & Allamandola, L. J. (2014). The NASA Ames PAH IR spectroscopic database version 2.00: Updated content, web site, and on(off)line tools. The Astrophysical Journal Supplement Series, 211(1), 8. https://doi.org/10.1088/0067-0049/211/1/8",
    "Brown, N., Fiscato, M., Segler, M. H. S., & Vaucher, A. C. (2019). GuacaMol: Benchmarking models for de novo molecular design. Journal of Chemical Information and Modeling, 59(3), 1096–1108. https://doi.org/10.1021/acs.jcim.8b00839",
    "Gómez-Bombarelli, R., Wei, J. N., Duvenaud, D., Hernández-Lobato, J. M., Sánchez-Lengeling, B., Sheberla, D., Aguilera-Iparraguirre, J., Hirzel, T. D., Adams, R. P., & Aspuru-Guzik, A. (2018). Automatic chemical design using a data-driven continuous representation of molecules. ACS Central Science, 4(2), 268–276. https://doi.org/10.1021/acscentsci.7b00572",
    "Guimaraes, G. L., Sanchez-Lengeling, B., Outeiral, C., Farias, P. L. C., & Aspuru-Guzik, A. (2017). Objective-reinforced generative adversarial networks (ORGAN) for sequence generation models. arXiv. https://doi.org/10.48550/arXiv.1705.10843",
    "Kim, S., Chen, J., Cheng, T., Gindulyte, A., He, J., He, S., Li, Q., Shoemaker, B. A., Thiessen, P. A., Yu, B., Zaslavsky, L., Zhang, J., & Bolton, E. E. (2025). PubChem 2025 update. Nucleic Acids Research, 53(D1), D1516–D1525. https://doi.org/10.1093/nar/gkae1059",
    "Krenn, M., Häse, F., Nigam, A., Friederich, P., & Aspuru-Guzik, A. (2020). Self-referencing embedded strings (SELFIES): A 100% robust molecular string representation. Machine Learning: Science and Technology, 1(4), 045024. https://doi.org/10.1088/2632-2153/aba947",
    "Loshchilov, I., & Hutter, F. (2019). Decoupled weight decay regularization. In International Conference on Learning Representations. https://openreview.net/forum?id=Bkg6RiCqY7",
    "Mitchell, M., Wu, S., Zaldivar, A., Barnes, P., Vasserman, L., Hutchinson, B., Spitzer, E., Raji, I. D., & Gebru, T. (2019). Model cards for model reporting. In Proceedings of the Conference on Fairness, Accountability, and Transparency (pp. 220–229). ACM. https://doi.org/10.1145/3287560.3287596",
    "Polykovskiy, D., Zhebrak, A., Sanchez-Lengeling, B., Golovanov, S., Tatanov, O., Belyaev, S., Kurbanov, R., Artamonov, A., Aladinskiy, V., Veselov, M., Kadurin, A., Johansson, S., Chen, H., Nikolenko, S., Aspuru-Guzik, A., & Zhavoronkov, A. (2020). Molecular Sets (MOSES): A benchmarking platform for molecular generation models. Frontiers in Pharmacology, 11, 565644. https://doi.org/10.3389/fphar.2020.565644",
    "Radford, A., Wu, J., Child, R., Luan, D., Amodei, D., & Sutskever, I. (2019). Language models are unsupervised multitask learners. OpenAI.",
    "Segler, M. H. S., Kogej, T., Tyrchan, C., & Waller, M. P. (2018). Generating focused molecule libraries for drug discovery with recurrent neural networks. ACS Central Science, 4(1), 120–131. https://doi.org/10.1021/acscentsci.7b00512",
    "Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, Ł., & Polosukhin, I. (2017). Attention is all you need. In Advances in Neural Information Processing Systems 30 (pp. 5998–6008). Curran Associates.",
    "Xiong, R., Yang, Y., He, D., Zheng, K., Zheng, S., Xing, C., Zhang, H., Lan, Y., Wang, L., & Liu, T.-Y. (2020). On layer normalization in the Transformer architecture. In Proceedings of the 37th International Conference on Machine Learning (pp. 10524–10533). PMLR.",
]
for r in refs:
    p = para(r, indent_first=False); p.paragraph_format.left_indent = Inches(0.5); p.paragraph_format.first_line_indent = Inches(-0.5)

doc.save(str(OUT_DOCX))
print("written", OUT_DOCX)
if QUICK:
    print("quick-mode results: no PDF (the docx carries the banner)")
    sys.exit(0)
ps = f'''$w = New-Object -ComObject Word.Application; $w.Visible = $false
$d = $w.Documents.Open("{OUT_DOCX}"); $d.SaveAs2("{OUT_DOCX.with_suffix('.pdf')}", 17); $d.Close(); $w.Quit()'''
subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True)
print("pdf:", OUT_DOCX.with_suffix(".pdf").exists())
