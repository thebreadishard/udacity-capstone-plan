# Module 05 — the correction predictor (Udacity "Deep Learning Systems")

*Until decision 49 (23 September 2026) this module was named the Δ₂-support predictor; the notebook's pre-registered task is unchanged, the target is the correction itself.*

**Status (2026-10-03 18:0x).** The module has run and has kept learning. The main run of 23 September (a rented CCX53, fresh environment from `requirements.txt`) stands untouched in `notebook/deep_learning.ipynb`; the notebook has since gained dated follow-up sections 7–12.3 (23 September – 3 October), each executed append-only, and `module_summary.docx/.pdf` is rebuilt from the result files. Nothing in notebook or report is typed by hand (`make_notebook.py` fills the summary from `notebook/results*.json`, `make_summary.py` reads every number from the result files and the release manifest). Rung C — the equivariant network with the hybrid head (`m05/rungC_*.py`) — trained on 750 molecules on 1–2 October and met the first target (hold-out (a): ring-coupling ratio 0.22, corrected ω 2.8 cm⁻¹; chains 23/24, registry status `carried`); it carries part of the correction to coupled-cluster level on an unseen anchor (5–6 cm⁻¹ in-plane with three anchors, chain 25/27b) and taught the coverage rule (decision 52: ≈ 30 mixed children cover a scaffold family, ≈ 60 finish it). Since decision 53 (3 October) the targets are per mode family and stay open until the out-of-plane and the skeletal families are under 3 cm⁻¹ too; chain 34 (a family-balanced diagonal term) and analytic hold-out targets are queued. Saved networks are versioned in `MODELS.md` (decision 55). Still open: the user's pass over notebook and report, the Zenodo release of the corpus (the user), the submission copy at the very end, and the promotion of the model to `src/dpir` under decision 47. Running beside the module: the next pool of 200 molecules on a CPX62 and pool 3 (decision 54: cations, aza-four-rings, five-rings) prepared in the manifest; the anthracene and benzene⁺ coupled-cluster anchors on a CCX53 (`TASKS.md`). The history of every step is in `PROVENANCE.md` (dated notes) and `RUBRIC_CHECKLIST_2026-09-22.md` (status per rubric item, appended per date).

## Project description (as it reads)

*For readers without chemistry:* The colours at which a molecule absorbs infrared light follow from a table of spring stiffnesses between its atoms (the Hessian). A cheap calculation (DFT) gives that table with systematic errors; the expensive one (coupled cluster) gets it right but is affordable only for small molecules. This network learns the *difference* between the two tables from the molecule's structure and the cheap table, trained on a corpus of cheap-against-cheap differences and checked against the few expensive ones (the anchors). It is judged on molecules it never saw (hold-outs), per kind of vibration (family), in cm⁻¹ — a small unit of colour; the goal is a few cm⁻¹ where the cheap calculation is off by tens. Terms are defined in [`../GLOSSARY.md`](../GLOSSARY.md).

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
- **Rung C: the floor was ours, then the target was met (section 12, 1–2 October).** Every head of the equivariant network sat at the same error for a week because the auxiliary term's target was the *projected* truth, which no pattern-supported output can reach; with a ridge least-squares target on the pattern (`m05/rungC_targets.py`) the floor fell away, and the hybrid head (pattern term + ring block + a diagonal term, SQM α, pair features) reached ratio 0.22 / ω 2.8 cm⁻¹ on hold-out (a) at 750 molecules against 0.42 / 4.8 for the hand-made pair model (sections 12.1–12.2, `out/E7_rungC_carried_kd_750_*`).
- **What transfers to coupled-cluster level, and what coverage buys (sections 12.2–12.3, 2–3 October).** Fine-tuning α and the last layer on three CC anchors brings an unseen anchor's in-plane frequencies to 5–6 cm⁻¹ against 25 for no correction (T3, `m05/rungC_cc_transfer.py`); out-of-plane stays at 17–35 and waits for the basis-set question. Taking the 130 three-ring molecules out of the pool raised the error on unseen three-ring parents from 0.15 to 0.50; putting them back in steps (0 / 31 / 62 / 123 children) gave 0.45 / 0.22 / 0.17 / 0.15 — the first thirty children of a family buy three quarters of its gain, sixty almost all of it, and neighbours carry two thirds. Decision 52 made that the rule for every pool and the price list of the Atlas.
- **Targets per family, measured before training (decision 53, 3 October).** The all-mode ω hid two families: ring in-plane 2.2–2.5 and C–H stretch 1.3–1.9 cm⁻¹ are under the line, C–H out-of-plane 2.4–3.2 and the skeletal/substituent family 3.6–4.7 are not. Before any new lever, the representation ceiling of the head (≤ 0.6 cm⁻¹ in every family) and the noise floor of the finite-difference targets per family (3.3 cm⁻¹ for out-of-plane, 1.5 for the rest) were measured (`probes/rungC_family_floor_ceiling.py`): the out-of-plane gap needs cleaner targets, the skeletal gap is a learning gap. Section 12.4 follows with chain 34's outcome.

## How to run

```bash
pip install -r requirements.txt                                   # frozen by tools/freeze_environments.py from the Windows environment (3 Oct 2026; torch 2.14.0+cpu, rdkit, geometric)
python m05/build_release.py corpus/molecules data/corpus_release/layerA2_2026-09-23   # dataset file + manifest (needs the corpus folders; RELEASES.md lists the releases)
M05_RELEASE=layerA2_2026-09-23 python notebook/make_notebook.py    # writes and executes notebook/deep_learning.ipynb (M05_QUICK=1: one-minute pipeline check, labelled)
python make_summary.py                                             # the nine-section report + addenda from the result files (docx + PDF)
python m05/e7_rungB_pairs.py corpus/molecules out/E7_rungB_<date> --use-analytic --sizes 45,100,175 --seeds 0,1,2   # rung B, the pre-registered E7 curve
python m05/rungC_train.py corpus/molecules out/<prefix> --use-analytic --pool-layers A,A2,B --sizes all --seeds 0,1,2 --inner-val 0.15 --threads 8 --aggregation sum \
    --head hybrid --aux both --kring-weight 0.3 --kdiag-weight 0.1 --sqm-scale --pair-features --aux-weight 1.0 --epochs 200 --patience 20 --lr 3e-4 --hybrid-hidden 256 --pattern f --save-model
                                                                   # rung C, the carried recipe of chains 23/24 (MODELS.md); design_check.py before every run
python m05/rungC_cc_transfer.py corpus/molecules out/<model>.pt out/<prefix> --head-l2 1 --anchor <id>=<hessian_ccsd_t.npz> ...   # T3: leave-one-anchor-out to CC level (carried models only)
python m05/model_registry.py --check                               # the saved networks and their reviewed status
```

The corpus factory (`corpus/`: `run_corpus.py`, shards, `STATUS.md`, `ledger.csv`) is documented in `corpus/README.md`; the pre-registrations of the
E-series live in `GoalGathering/notes/PreRegistration_2026-09-*`. Superseded and kept for the record: `m05/model.py`, `m05/smoke_test.py`,
`m05/build_corpus.py fixture` (the 12 September scaffold).

## Model versions (decision 55, 3 October 2026)

`MODELS.md` lists every saved network in `out/` with its network name and version (decision 59: the ΔH-network, v1.1 = chain 34, v1.0 = chain 24), its reviewed status (`carried`, `superseded`, `invalid`, `smoke`, `pretrained`, `candidate`, `experimental`), the chain that made
it, the recipe read from the checkpoint, the hold-out numbers and the commit. It is generated — `python m05/model_registry.py`, checked by
`python m05/model_registry.py --check` and by `tests/test_model_registry.py` — from the checkpoints and `out/MODELS_STATUS.json`, the one file that is
written by hand (a judgement per model). Reads and transfers (`m05/rungC_cc_transfer.py`, `probes/rungC_eval_saved.py`) run on `carried` models only;
`--allow-any-model` is the named exception.

## Files

- `RECIPE.md` — task type, label rule, corpus, baseline, the one controlled change, metrics, seeds; frozen before any data, amended by dated note only.
- `notebook/make_notebook.py` → `notebook/deep_learning.ipynb`; `notebook/results.json` (main run) and `results_followup{,2,3,4,5}.json` (sections 7–11; section 12 reads `out/E7_rungC_*`); `notebook/figures/`.
- `make_summary.py` → `module_summary.docx`, `module_summary.pdf` (Report Overview, Dataset and Task Description, Model Architecture and Design
  Decisions, Experimental Comparison, Results and Interpretation, Limitations and Risks, Ethical and Responsible Use, Future Improvements, References; four addenda).
- `m05/deltah_model.py` (+ `sync_model.py`), `m05/build_release.py`, `m05/release_index.py`; the E-series scripts `m05/e6_*`, `e7_*`, `e9_*`, `e10_*`, `e11_*`.
- Rung C: `m05/rungC_equivariant.py` (body, charge-state input), `rungC_hybrid.py` (head), `rungC_targets.py` (ridge target), `rungC_train.py` (trainer, `--kdiag-mode family`, `--save-model`), `rungC_cc_transfer.py` (T3), `rungC_intensities.py`, `rungC_pretrain.py`, `rungC_stage_pick.py`; `m05/model_registry.py` → `MODELS.md` + `out/MODELS_STATUS.json`; `m05/design_check.py` (before every run).
- Probes that read the module's outputs: `probes/rungC_error_map.py`, `probes/rungC_eval_saved.py`, `probes/rungC_family_floor_ceiling.py` (floor, ceiling, the pool-3 cation gate), `probes/pool3_candidates.py`; tests in `tests/test_rungC_*.py`, `test_model_registry.py`, `test_pool3_candidates.py`.
- `data/corpus_release/` — manifests in git, archives local (size); `RELEASES.md` generated.
- `PROVENANCE.md`, `RUBRIC_CHECKLIST_2026-09-22.md`, `REPORT_OUTLINE.md`, `requirements.txt`.
