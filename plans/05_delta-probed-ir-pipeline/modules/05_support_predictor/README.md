# Module 05 — the Δ₂-support predictor (Udacity "Deep Learning Systems") — scaffold

**Status update 2026-09-22 (dated note; the rubric text below is the 12 September scaffold and is not rewritten until the module starts).** Since the scaffold: (1) the corpus factory is running — layer A2, four shards of 50 molecules on Hetzner (E6, started 19 September; phase 1 expected 23 September), on top of layer A (39 molecules); (2) the E-series of 19 September showed that a per-mode ring-family label is ill-posed (E4) and that the transferable object is the *family block* — diagonal plus couplings — so the model's target is the block, not a per-mode support bit (plan README, learned-features lessons; pre-registered learning curve E6); (3) the architecture now names the network **the ΔH model** (backbone, block head, pair head; `architecture/50_deltaH_model_components.mmd`, `51_deltaH_model_pytorch.py`), which supersedes `m05/model.py` as the module's model when the module is written; (4) Hessian QM9 holds 66 all-carbon aromatic rings in 41,645 molecules (PROVENANCE, 12 September) — the subset definition is still the user's decision; the project's own corpus is the primary data; (5) the anharmonic tail of the pipeline is settled on analytic pyscf Hessians (decisions 46, 21 September). RECIPE.md stays frozen; amendments by dated note only. Code under the quality policy of decision 47 (`QUALITY_POLICY.md`).

**Status: scaffold (2026-09-12, evening).** Hessian QM9 downloaded and inventoried; no subset recomputed, no model
trained. What exists: the recipe, the corpus builder in fixture mode, the PyTorch model, a smoke test that proves the
code path on the plan's benzene dry-run tensor, the resumable corpus factory (`corpus/`, 11,321 candidates in four
layers, nothing computed yet), **the notebook skeleton in the rubric's structure** (`notebook/make_notebook.py` →
`deep_learning.ipynb`; fixture cells and marked stubs, not executed) and **the report outline** (`REPORT_OUTLINE.md`,
the nine required sections with their number sources). See `PROVENANCE.md` for what the module still needs and who owes it.

## Project description (as it will read)

**Task type: sequence modelling with a Transformer.** A molecule is a sequence of DFT normal-mode
tokens; the network predicts, per pair of modes, whether the correction matrix Δ₂ between two levels
of theory has a large element there — the *support* of Δ₂. The prediction is a learned prior that
tells the larger project's recovery where to place its expensive measurements. The success criterion is
whether that prior saves patterns and agrees with the prior-free check on a real molecule, not accuracy.

**Dataset (planned):** the public Hessian QM9 set (Williams et al., 2025; figshare DOI
10.6084/m9.figshare.26363959, 41,645 molecules, ωB97x/6-31G* Hessians) plus B3LYP/6-31G* Hessians
recomputed by this project on an aromatic-heavy subset, giving Δ₂ = H(ωB97x) − H(B3LYP) per molecule;
published as its own release before the module starts. Computed ab initio data, not AI-generated,
not used in any earlier capstone module.

## How to run what exists

```bash
pip install -r requirements.txt
python m05/build_release.py corpus/molecules data/corpus_release/layerA_2026-09-22   # dataset file + manifest (needs the corpus folders)
python notebook/make_notebook.py        # writes and executes notebook/deep_learning.ipynb (M05_QUICK=1 for a one-minute pipeline check)
python make_summary.py                  # the nine-section report from notebook/results.json (quick-mode results: banner, no PDF)
```

*11:5x, 22 September 2026:* the rubric-form deliverables exist and run end to end on the layer-A release (42 molecules): the notebook in the rubric's
structure around the ΔH model (`m05/deltah_model.py`, a verbatim copy of the architecture sheet kept identical by `m05/sync_model.py`), the report builder,
the dataset builder with a checksummed manifest, and `RUBRIC_CHECKLIST_2026-09-22.md` (item by item: done / missing / owner). The numbers come with the
layer-A2 release and a full execution; today's execution was a quick pipeline check and is labelled so in the notebook and the docx.

Older scaffold pieces (still present, superseded for the submission): `python m05/build_corpus.py fixture`, `python m05/smoke_test.py`.

`build_corpus.py fixture` reads the dry-run archives under `../../probes/results_dryrun/` and writes
`data/corpus_fixture.npz` with tokens and support labels; `smoke_test.py` trains the baseline
Transformer for twenty steps on one molecule and prints the loss trajectory and the implied pattern
count. Neither output is a result. `python m05/build_corpus.py hessianqm9` prints what the real build
expects and exits (NOT_RUN).

## Files

- `RECIPE.md` — task type, label rule, corpus, baseline, the one controlled change, metrics, seeds; written before any data or model.
- `m05/build_corpus.py`, `m05/model.py` (SupportTransformer, implied pattern count), `m05/smoke_test.py`.
- `requirements.txt` (`pip freeze`; PyTorch 2.14 CPU installed 2026-09-12).
- To come, in the rubric form of Modules 02–04: `notebook/deep_learning.ipynb`, `module_summary.pdf`
  (sections: Report Overview, Dataset and Task Description, Model Architecture and Design Decisions,
  Experimental Comparison, Results and Interpretation, Limitations and Risks, Ethical and Responsible
  Use, Future Improvements, References).
