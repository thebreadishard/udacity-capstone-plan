# Module 05 — the Δ₂-support predictor (Udacity "Deep Learning Systems") — scaffold

**Status: scaffold only (2026-09-12).** No corpus has been downloaded, no subset recomputed, no model
trained. What exists: the recipe, the corpus builder in fixture mode, the PyTorch model, and a smoke
test that proves the code path on the plan's benzene dry-run tensor. See `PROVENANCE.md` for what the
module still needs and who owes it.

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
python m05/build_corpus.py fixture
python m05/smoke_test.py
```

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
