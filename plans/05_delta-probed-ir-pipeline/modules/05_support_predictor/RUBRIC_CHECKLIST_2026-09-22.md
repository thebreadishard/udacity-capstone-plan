# Module 05 — rubric checklist (desk pass 22 September 2026)

*What the rubric (Rubrics/05_Deep_Learning_Systems.md, Tasks 1–8 and the grading table) asks, what exists after today's preparatory
work, what is still missing, and who owes it. Nothing here is a result; the numbers arrive with the layer-A2 release (E6, ≈ 23 September)
and the full execution of the notebook.*

| Rubric item | Requirement | Status 22 Sep | Missing / owner |
|---|---|---|---|
| Task type declared | CNN, RNN or Transformer stated in the notebook | **done** — Transformer, first cell of `notebook/deep_learning.ipynb`; `RECIPE.md` §"Task type" | — |
| Dataset | appropriate, enough samples, public, not synthetic/AI-generated, not reused; document how obtained and prepared | **prepared** — own corpus release (`m05/build_release.py` → `data/corpus_release/<release>.npz` + manifest with SHA-256 per input); layer A = 42 molecules today; layer A2 adds ≈ 200 | **the user:** Zenodo release with DOI before submission; **Claude:** rebuild the release when E6 lands; the "not synthetic" wording (computed ab initio data) stands as decided in the mapping; **dataset = own corpus alone (the user, 17:2x 22 Sep); Hessian QM9 out of the first run** |
| Load and inspect | load, representative samples, shapes/dtypes/labels, quality notes | **done** in §1 (samples table, shapes, symmetry check of K, histograms, padding/split notes) | — |
| Baseline model | full PyTorch architecture, design-choice markdown, loss/optimiser, training evidence | **done** in §2–3 — `m05/deltah_model.py` (verbatim copy of the architecture sheet, `m05/sync_model.py` keeps it identical), loss curves per seed | promotion of the model to `src/dpir` with tests before submission (quality policy) |
| One controlled change | exactly one major aspect changed; what/why/how documented | **done** in §4 — depth 2 → 4 layers, everything else fixed (RECIPE) | — |
| Evaluation and comparison | metrics fit for the task, both models, visualisation, direct comparison | **done** in §5 — RMS per family (shifts and couplings) against the zero and family-median rules; pair-head average precision against the resonance-denominator rule; Figure 4 | numbers = full run on the A2 release, 30 epochs, three seeds |
| Notebook summary | 4–6 sentences: task/data, models, main differences, challenges | **built by the notebook builder from `results.json`**; today's text carries the quick-mode disclaimer | rewrite by hand after the full run if the generated text needs judgement |
| Notebook runs top to bottom | no errors, outputs present | **done** in quick mode (3 epochs, one seed, ≈ 1 min on two threads, 22 Sep); fresh-environment check to repeat (`tools/modules_fresh_check.sh`) | full run + fresh-environment check |
| Report (nine sections, APA, citations) | `Deep_Learning_Systems_Analysis_Report.pdf` = `module_summary.pdf` | **builder done** — `make_summary.py` reads every number from `results.json` and the manifest; quick-mode results give a banner and no PDF; four verified references (Vaswani 2017; Williams 2025 Sci Data 12, DOI checked; Mitchell 2019 model cards, DOI checked; Danchev 2022) | PDF from the full run; the student's own pass |
| requirements.txt | `pip freeze` from the environment that ran the notebook | file of 12 Sep (PyTorch 2.14 CPU) | regenerate from the environment of the full run |
| Not reused / distinct data | | stated in notebook and report | — |

## Order of work when E6 lands (≈ 23 September)

1. `merge_shards.py`, then `python m05/build_release.py corpus/molecules data/corpus_release/layerA2_<date>` (all layers; the notebook takes
   `M05_RELEASE=<name>`).
2. `python notebook/make_notebook.py` without `M05_QUICK` (30 epochs, seeds 0 1 2; minutes on CPU at this corpus size — two threads beside the anchor
   or on hel1-14).
3. `python make_summary.py` → docx + PDF; read the generated summary and the results paragraph; edit by hand only where judgement is needed and
   record it in PROVENANCE.
4. `pip freeze > requirements.txt` in the environment that ran step 2; fresh-environment check.
5. The user's pass; the Zenodo release; the submission copy at the very end (the user's decision of 22 September).

## Status after the full run, 2026-09-23 09:5x

- Dataset: **released** — `data/corpus_release/layerA2_2026-09-23.npz` + manifest with SHA-256 (224 molecules, own corpus alone per the decision of 22 September).
- Notebook runs top to bottom: **done in full mode** on a fresh environment (CCX53, requirements as frozen), twice; `results.json` carries the numbers above (PROVENANCE dated note).
- Notebook summary: **filled from `results.json`** by the second pass (no quick-mode disclaimer).
- Report: built by `make_summary.py` from the same `results.json` (docx + PDF, see PROVENANCE) — the user's pass follows.
- requirements.txt: **regenerated** from the environment of the full run.
- Open: the user's pass; Zenodo release; the submission copy at the very end.

## Status after the follow-up cells, 2026-09-23 14:4x

- Notebook: **section 7 added** (second route on benzene, corpus screen, retrained baseline on the corrected release, E6/E7 comparison, what we learned);
  executed top to bottom a third time in the same environment; sections 1–6 unchanged in source. The reviewer sees the original run and the correction.
- Dataset: original release kept; corrected release `layerA2_2026-09-23b.npz` beside it with its own manifest (which molecule uses the second route).
- Report: addendum section built from `results_followup.json` (same rule: no number typed by hand).
- Open: the user's pass; Zenodo; the submission copy at the end.

## Status 2026-09-24 13:2x

Section 8 follow-up cells added to the generator (imaginary-mode second route; retrain on the 229-molecule release; E8's coupled-cluster reading);
report builder gains Addendum 2. Not executed yet — the executed notebook, `results.json`, docx and PDF in this folder are the 23 September run.
To close: run `python notebook/make_notebook.py` and `python make_summary.py` on a free machine, re-check items on the executed outputs, refresh PROVENANCE.

## Status 2026-09-24 14:4x — section 8 executed

Executed append-only (see PROVENANCE): notebook 39 cells, no errors; `results_followup2.json`; report with Addendum 2 (docx + PDF). The committed
outputs are current again. Items unchanged otherwise; the reviewer sees sections 7 and 8 as dated follow-ups after an untouched main run.

**2026-09-25 07:2x:** section 9 appended (E9, E10, size extrapolation; three pre-registered readings, no retraining), notebook 51 cells, no errors; `results_followup3.json`; report with Addendum 3. Cells 12 and 17 restored from the 23 September run after the 24 September executor had overwritten them (PROVENANCE dated note); the executor is fixed. What the reviewer sees: the module's target is local, additive and carries from small to large molecules, and the proof of learning is a pre-registered curve now running (layer B).
