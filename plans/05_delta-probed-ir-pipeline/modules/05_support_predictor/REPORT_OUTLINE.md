# Module 05 — Deep Learning Systems Analysis Report: outline (skeleton, 2026-09-12)

*The rubric (Rubrics/05) requires nine sections in `module_summary.pdf` (APA 7 template, in-text citations, a
References list with at least two credible sources of which one scholarly). This outline fixes what goes where
and which numbers each section will take from the notebook, so that the report can be written the day the
training outputs exist. Nothing here is a result.*

| # | required section | what goes in it | source of the numbers |
|---|---|---|---|
| 1 | Report Overview | the task in two sentences: a Transformer predicts the support of the correction matrix Δ₂ from DFT normal-mode tokens; why it matters for plan 05 (a learned prior that places expensive measurements); what was compared and the one-line outcome | notebook §7 |
| 2 | Dataset and Task Description | Hessian QM9 (Williams et al. 2025; 41,645 ωB97X/6-31G* numerical Hessians; ~15 cm⁻¹ displacement sensitivity as the label noise floor) plus the project's own four-layer aromatic corpus (A 45 / A′ 868 / B 4,353 / C 6,055 candidates; the computed number by dated note); Δ₂ = H(ωB97X) − H(B3LYP); TR projection; label θ = 0.1; the split (leave-molecule-out by scaffold family); the ring survey (only 66 all-carbon aromatics in QM9) and why the own corpus exists | `out/HESSIAN_QM9_SUMMARY.md`, `out/HESSIAN_QM9_RINGS.md`, `corpus/DESIGN_2026-09-12.md`, notebook §1 |
| 3 | Model Architecture and Design Decisions | encoder-only Transformer over mode tokens with a pair head; d_model 64, 4 heads, 2 layers, dropout 0.1; class-weighted BCE; why a Transformer (variable-length, permutation-aware sequences of modes; pairwise output) — cite a sequence-modelling source and the attention paper; parameter count | `RECIPE.md`, `m05/model.py`, notebook §2 |
| 4 | Experimental Comparison | the one controlled change (2 vs 4 layers), three seeds each, everything else fixed; the rule for a second comparison | `RECIPE.md`, notebook §3 |
| 5 | Results and Interpretation | loss curves; per-pair precision/recall at recall 0.9; the implied pattern count K_prior against the prior-free K per held-out molecule; the seed spread; interpretation for a technical and a non-technical reader (does the prior save measurements, and is it trusted?) | notebook §4–5, `out/training_log.json` |
| 6 | Limitations and Risks | DFT-vs-DFT stand-in for the real CC − DFT target; QM9's size range (≤ 9 heavy atoms) against PAHs; numerical-Hessian noise in the labels; one functional pair; the licence rule of the plan (the prior is used only after it agrees with the prior-free check) | plan 05 Ladder §3, Distilled §5 |
| 7 | Ethical and Responsible Use | open data (CC0) and open code; no personal data; the risk of a prior that silently steers a physical measurement — mitigated by the fail-closed licence and by printing K_prior beside K; energy cost of the corpus (desktop-days) stated | plan 05 README, `corpus/README.md` |
| 8 | Future Improvements | the real CC − DFT labels from the R0/R1 pilots; larger aromatic layers; a second controlled change (token features); the network of decision 32 as the named follow-up outside the module sequence | proposal §6, decision 32 |
| 9 | References | Williams et al. 2025 (Sci Data, DOI 10.1038/s41597-024-04361-2); Vaswani et al. 2017 (attention) — record to verify before citing; a sequence-modelling or class-imbalance source — to verify; Danchev 2022 (JOSE) as in modules 02–04; own results not cited | Crossref-verified before the report is written |

Also required by the rubric: the notebook runs top to bottom (the skeleton's stub cells raise by design until the corpus
exists — the submitted notebook must not contain them), dataset access instructions (`data/hessian_qm9/fetch_hessian_qm9.ps1`,
the figshare DOI, the corpus release DOI once minted), and `requirements.txt` from `pip freeze` in the environment that ran it.
