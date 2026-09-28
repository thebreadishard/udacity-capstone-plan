# Module 05 — the correction predictor (Udacity "Deep Learning Systems")

*Until decision 49 (23 September 2026) this module was named the Δ₂-support predictor; the notebook's pre-registered task is unchanged, the target is the correction itself.*

**Status (2026-09-27 15:1x).** The module has run. The first full run was executed on 23 September on a rented CCX53 in a fresh environment built
from `requirements.txt`; the notebook `notebook/deep_learning.ipynb` then gained five dated follow-up sections (7–11, 23–28 September), each executed
append-only after the untouched main run, and the report `module_summary.docx/.pdf` was rebuilt from the result files on 25 September 10:5x. Nothing in
the notebook or the report is typed by hand: `make_notebook.py` fills the summary from `notebook/results.json`, `make_summary.py` reads every number
from the result files and the release manifest. Still open: the user's pass over notebook and report, the Zenodo release of the corpus (the user), the
submission copy at the very end, and the promotion of the model to `src/dpir` under the quality policy of decision 47. Running beside the module:
layer B of the corpus (six shards on Hetzner; `TASKS.md`) for the pre-registered learning curve, with an interim reading on the evening of
27 September; and the equivariant network of rung C, built and smoke-tested (`m05/rungC_equivariant.py`, `m05/rungC_train.py`), whose training waits for
the user's decision (`GoalGathering/notes/Decision_Memo_2026-09-27_RungC_Tonight.md`). The history of every step is in `PROVENANCE.md` (dated notes) and
`RUBRIC_CHECKLIST_2026-09-22.md` (status per rubric item, appended per date).

## Project description (as it reads)

**Task type: sequence modelling with a Transformer.** A molecule is a sequence of DFT normal-mode tokens (one per vibration: frequency, band
family, symmetry and environment descriptors). The network predicts, per band family, the *correction block* between two levels of theory — the
shift of each vibration and the couplings inside the family — and, with a pair head, which pairs of modes carry a large coupling. The target
moved from a per-mode support bit to the family block on 19 September (the per-mode label proved ill-posed, E4), and decision 49 (23 September)
moved the couplings from the mode basis to local coordinates for the next version (rung B, see "What the project learned"); the notebook's
pre-registered baseline and its one controlled change are the mode-basis Transformer of `RECIPE.md`.

**Dataset: the project's own corpus, released with a checksummed manifest.** B3LYP/6-31G* and ωB97X/6-31G* Hessians computed by this project on
identical geometries, Δ = H(ωB97X) − H(B3LYP) per molecule; layer A (42 ladder-adjacent aromatics) and layer A2 (182 mono-substituted three- and
four-ring cores) in the release the notebook trains on, `data/corpus_release/layerA2_2026-09-23.npz` — 224 molecules, 14,607 modes, split by molecule
186 / 18 / 20 (train / validation / test), 20 candidates with an imaginary mode skipped. Later releases (`RELEASES.md`: the corrected `…23b`, the
229-molecule `…24`, the 60-molecule layer-B interim) feed the follow-up sections. Computed ab initio data, not AI-generated, not used in any earlier
capstone module. Hessian QM9 (Williams et al., 2025) was downloaded and inventoried on 12 September and is *not* in the dataset (the user's decision of
22 September: too few aromatic rings, at most nine heavy atoms); `PROVENANCE.md` keeps what was learned from it.

**Models and the one controlled change.** Baseline: the ΔH model of the architecture sheet (`m05/deltah_model.py`, kept identical to
`GoalGathering/architecture/51_deltaH_model_pytorch.py` by `m05/sync_model.py`), two Transformer layers, 135,939 parameters; the controlled change:
four layers, 235,907 parameters, everything else fixed. 30 epochs, early stopping on the validation loss, seeds 0, 1, 2; two rules as opponents (zero
correction; the family median of the training set) and, for the pair head, the resonance-denominator rule.

**Result of the main run** (`notebook/results.json`, third execution of 23 September; test RMS in cm⁻¹, diagonal shift / couplings inside the block, mean over seeds):

| model | CH-stretch | CH-oop | ring-ip | other | pair head AP |
|---|---|---|---|---|---|
| zero | 43.78 / 0.47 | 24.08 / 3.21 | 20.34 / 4.02 | 19.23 / 2.42 | resonance rule 0.062 |
| family-median | 2.71 / 0.47 | 8.12 / 3.21 | 15.64 / 4.02 | 14.53 / 2.42 | — |
| baseline (2 layers) | 3.18 / 0.47 | 4.05 / 3.24 | 5.46 / 4.02 | 8.30 / 2.38 | 0.287 |
| 4 layers | 2.61 / 0.47 | 4.03 / 3.22 | 5.22 / 4.02 | 8.58 / 2.39 | 0.289 |

The shifts are learned (four to six times better than the zero rule on the C–H out-of-plane and ring families, better than the median rule everywhere
except the C–H stretch, where the median rule is already good); the couplings in the mode basis are not (every model sits on the zero rule); the
extra layers change nothing outside seed scatter. That reading is the module's honest result, and it is what the follow-up sections explain.

## What the project learned (sections 7–10 of the notebook; the same story in `Uitleg/10_Module_05_Steunvoorspeller.md`)

- **Why the couplings did not learn, and where they do (E6 → E7, section 7).** A normal mode is a direction without a fixed sign, so a coupling
  per mode pair is sign-blind and the label is ill-posed; the learning curve stayed flat at 45, 100 and 175 molecules. Written in local coordinates
  (pairwise terms in primitive internals, projected onto the modes: rung B, `m05/e7_rungB_pairs.py`) the same molecules do teach the couplings:
  ring-coupling RMS 0.43 of the zero rule on unseen scaffolds and 0.47 on bare cores at 175 molecules, corrected frequencies 4.7 / 5.1 cm⁻¹ against
  23 without correction (`results_followup.json`, `results_followup4.json`). Decision 49.
- **The correction is local, measured three times (sections 8–9).** Three quarters of ΔH sit in primitive pairs that share an atom or a ring (E7);
  benzene's coupled-cluster correction sits for 98 % in that pattern one bond further (E8); a substituted molecule's correction is its parent's
  block plus the substituent's neighbourhood, a quarter of the Hessian columns returning the corrected frequencies to 1.7 cm⁻¹ (E9, `results_followup3.json`).
- **Controls (section 10).** Shuffled labels lose what the real labels win; the label noise floor by two routes is 2.09 cm⁻¹ median spread
  (plateau bound 6.3; `results_followup4.json`); a symmetry reading of 25 September that was wrong for an hour is kept in the notebook with its
  correction — the pair model has symmetry built in, not learned, which is the reason the next version is an equivariant network (rung C).
- **The epoch cap audited (section 11, 28 September).** The main run's best epochs (25–29 of 30) sat against the cap; under decision 51 (early stopping
  as a rule) both configurations were trained again with the cap at 100 (`results_followup5.json`): best epochs 25–45, test errors within 0.9 cm⁻¹ and
  the pair head within 0.02 of 23 September — the cap bound the epoch count, not the numbers. Sections 1–10 stay as run; the audit is appended.

## How to run

```bash
pip install -r requirements.txt                                   # frozen from the environment of the 23 September run (torch 2.14.0+cpu)
python m05/build_release.py corpus/molecules data/corpus_release/layerA2_2026-09-23   # dataset file + manifest (needs the corpus folders; RELEASES.md lists the releases)
M05_RELEASE=layerA2_2026-09-23 python notebook/make_notebook.py    # writes and executes notebook/deep_learning.ipynb (M05_QUICK=1: one-minute pipeline check, labelled)
python make_summary.py                                             # the nine-section report + addenda from the result files (docx + PDF)
python m05/e7_rungB_pairs.py corpus/molecules out/E7_rungB_<date> --use-analytic --sizes 45,100,175 --seeds 0,1,2   # rung B, the pre-registered E7 curve
python m05/rungC_train.py corpus/molecules out/_smoke --smoke      # rung C mechanics only; the real run waits for the user's decision
```

The corpus factory (`corpus/`: `run_corpus.py`, shards, `STATUS.md`, `ledger.csv`) is documented in `corpus/README.md`; the pre-registrations of the
E-series live in `GoalGathering/notes/PreRegistration_2026-09-*`. Superseded and kept for the record: `m05/model.py`, `m05/smoke_test.py`,
`m05/build_corpus.py fixture` (the 12 September scaffold).

## Files

- `RECIPE.md` — task type, label rule, corpus, baseline, the one controlled change, metrics, seeds; frozen before any data, amended by dated note only.
- `notebook/make_notebook.py` → `notebook/deep_learning.ipynb`; `notebook/results.json` (main run) and `results_followup{,2,3,4}.json` (sections 7–10); `notebook/figures/`.
- `make_summary.py` → `module_summary.docx`, `module_summary.pdf` (Report Overview, Dataset and Task Description, Model Architecture and Design
  Decisions, Experimental Comparison, Results and Interpretation, Limitations and Risks, Ethical and Responsible Use, Future Improvements, References; four addenda).
- `m05/deltah_model.py` (+ `sync_model.py`), `m05/build_release.py`, `m05/release_index.py`; the E-series scripts `m05/e6_*`, `e7_*`, `e9_*`, `e10_*`, `e11_*`;
  `m05/rungC_equivariant.py`, `m05/rungC_train.py`.
- `data/corpus_release/` — manifests in git, archives local (size); `RELEASES.md` generated.
- `PROVENANCE.md`, `RUBRIC_CHECKLIST_2026-09-22.md`, `REPORT_OUTLINE.md`, `requirements.txt`.
