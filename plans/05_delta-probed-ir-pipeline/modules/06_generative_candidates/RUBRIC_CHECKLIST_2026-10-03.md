# Module 06 — rubric checklist (weekend review 2, 3 October 2026)

*What the rubric (Rubrics/06_Generative_AI_Applications.md and its grading tables) asks, what exists, what is still missing and who owes it.
The executed notebook (27 cells, 0 error outputs, the pre-registered run of 26 September 2026) and the report were re-read on 3 October; the
first checklist file written for 06.*

| Rubric item | Requirement | Status 3 Oct | Missing / owner |
|---|---|---|---|
| Generative model implementation | GAN, VAE or Transformer with course tools; notebook runs; model definition and generation shown | **done** — decoder-only Transformer in own PyTorch code (`m06/model.py`, 4 layers, 4 heads, d 256, ≈ 3 M parameters), sections 2–4 of `notebook/generative_model.ipynb` | — |
| Training and execution | trains and generates; loss trends or diagnostics shown | **done** — section 3: loss curves per seed, per-epoch validity of 200 samples, early stop; the decision-51 audit of 28 Sep found the 20-epoch cap binding for every seed and was closed by the user's ruling (PRE_REGISTRATION, 19:4x: the outcome stands as run) | — |
| Task definition and model choice | task defined, model fits data, design choices explained | **done** — README "Project description", notebook section 1, `DESIGN_2026-09-24.md` (why SMILES + Transformer, why PubChem fused aromatics) | — |
| Output evaluation | qualitative analysis of own outputs; strengths, limitations, failure cases with examples | **done** — section 4: the seven pre-registered metrics (6 of 7 met; the miss is a prediction the model exceeded), the failure gallery ("shown, not hidden"), five samples with nearest training neighbours, the 5-gram baseline beaten on every line | — |
| Justification and evidence | claims backed by own implementation and outputs; citations | **done** — report built from `notebook/results.json` by `make_summary.py`; APA citations with References | — |
| Ethical reflection | ≥ 1 concern tied to the data, model or outputs | **done** — section 6 and the report's "Ethical Considerations and Responsible Use": candidates are *what to compute next*, never claimed molecules; dual-use and distribution bias discussed on the actual outputs | — |
| Responsible-use reasoning | design, data or outputs related to responsible use, specifically | **done** — the candidates enter the atlas as a separately labelled source; PubChem public-domain data with the query and checksum published | — |
| Notebook organisation | clear markdown, design/training/generation easy to follow | **done** — Setup · 1 Load and inspect · 2 The model · 3 Training · 4 Sampling and evaluation · 5 The design change (conditioning) · 6 Ethics · 7 Summary | — |
| Written report quality | the Generative AI Analysis and Ethics Report, clear and structured | **done** — `Generative_AI_Analysis_Report.pdf` (Overview · Dataset · Model design and training · Output evaluation · Ethics · Limitations · References), built 26 Sep 20:0x from the results file | the student's own pass before submission |
| Reproducibility | `requirements.txt` from the working environment; data or prompt source documented | **done** — `requirements.txt` (25 Sep, the environment of the run); `data/README.md` with the PubChem query, date, filters, counts and SHA-256; the frozen CSV committed | regenerate the listing only if the environment changes before submission |
| Academic integrity | outputs from the student's own runs; analysis references specific outputs | **done** — three seeds and the conditioned model trained by `m06/train.py` on 26 Sep (PROVENANCE dated notes); every number in notebook and report from `results.json` | — |

## Open points (not rubric failures)

- The three design decisions of 24 September (PubChem as the source; freeze now; candidates as a separately labelled source for the atlas) were
  taken as recommended and stand open for the user to confirm or change (README status).
- The pre-registered run stopped at its cap of 20 epochs for every seed; closed by the user's ruling of 28 September, not by a re-run. A later
  run with the cap lifted is a dated follow-up section if the user wants one, never a replacement.
