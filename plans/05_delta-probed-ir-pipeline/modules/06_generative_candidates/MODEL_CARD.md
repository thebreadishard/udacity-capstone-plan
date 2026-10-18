# Model card — the candidate generator (module 06)

*In the format of Mitchell et al. (2019), "Model cards for model reporting". Every number comes from `notebook/results.json` (the
pre-registered run of 26 September 2026) or `PRE_REGISTRATION.md`; written 18 October 2026.*

## Model details

- **What it is.** A character-level, decoder-only Transformer that writes molecules as SMILES strings: 4 layers, 4 heads, model width 256,
  feed-forward 1024, dropout 0.1, learned positional embeddings, 3,201,024 parameters, a vocabulary of 33 tokens. Own PyTorch code
  (`m06/model.py`, `m06/train.py`).
- **Versions** (`MODELS.md`). 0.1: unconditioned, seeds 0 and 1 (seed 2's weights of 26 September were not saved; the file now on disk is
  from a re-execution and is marked invalid). 0.2: conditioned on two prefix tokens, ring-count class (2, 3, ≥ 4) and heteroatom set
  (none, N, O, S), 3,205,120 parameters. Both are *experimental*, not part of the project's production pipeline.
- **Training.** AdamW (learning rate 3e-4, weight decay 0.01), cosine schedule with 500 warm-up steps, batch 128, at most 20 epochs with early
  stopping on the validation loss (patience 3), seeds 0, 1, 2. The recipe was fixed before any training (`PRE_REGISTRATION.md`).
- **Author.** Frederic Petrignani, for the Udacity AI capstone (module 06). The training data are public domain (PubChem).

## Intended use

- **Primary use.** Proposing new fused-aromatic molecules — substituted and heteroatom polycyclic aromatic hydrocarbons (PAHs) — as
  candidates for the project's quantum-chemistry pipeline to compute next.
- **Primary users.** The project itself, and researchers who want a small, inspectable generator of PAH-like molecules.
- **Out of scope.** Proposing molecules for synthesis, for biological activity or for any property related to toxicity; claims that a
  generated molecule exists in space or in a laboratory. The model produces strings that parse as molecules. It does not produce synthesis
  routes, and it has never been asked to optimise any property.

## Training and evaluation data

160,972 fused-aromatic molecules from PubChem (public domain), retrieved through PUG-REST on 24 September 2026. The query, the filters
and their counts, and the SHA-256 of the frozen file are in `data/README.md`. The filters keep neutral molecules with only C, H, N, O, S,
F and Cl, at most 30 heavy atoms, no isotopes, and at least two aromatic rings that share an edge. The split is by Murcko scaffold, so that
no scaffold appears in two splits: 125,065 training, 15,434 validation and 20,473 test molecules.

## Metrics and results

10,000 samples per model, temperature 1.0 unless stated, scored with the pre-registered metrics (`m06/evaluate.py`).

| metric | what it measures | prediction | seed 0 | seed 1 | seed 2 |
|---|---|---|---|---|---|
| validity | share of samples that parse as molecules | ≥ 0.85 | 0.924 | 0.926 | 0.923 |
| uniqueness | share of valid samples that are distinct | ≥ 0.95 | 0.992 | 0.992 | 0.992 |
| novelty | share of distinct samples not in the training data | ≥ 0.50 | 0.907 | 0.907 | 0.910 |
| scaffold novelty | share with a scaffold not in the training data | ≥ 0.30 | 0.534 | 0.535 | 0.538 |
| memorisation | share of valid samples copied from the training data | ≤ 0.10 | 0.099 | 0.099 | 0.096 |
| project fit | share of novel samples the pipeline can compute | 0.30–0.60 | 0.945 | 0.944 | 0.947 |

Six of the seven registered predictions were met. The miss is project fit, where the model did better than predicted. The three seeds
agree within 0.004 on validity.

- **Lower temperature (0.7).** Validity rises to 0.98, but memorisation rises to 0.18–0.19, above the 0.10 line. Temperature 1.0 is the
  setting reported.
- **Conditioned model (0.2).** It follows its ring and heteroatom request in 0.869 of samples (prediction ≥ 0.80). Sulphur requests are the
  weakest, down to 0.625 for two rings with sulphur.
- **Baseline.** A 5-gram token model trained on the same split: validity 0.030, project fit 0.024. The Transformer beats it on the
  registered comparison: validity and project fit by margins of 0.89 and 0.92, and it is closer to the test set on all three
  distribution distances. The baseline's higher novelty (0.996) comes from samples that are 97 % invalid.

## Ethical considerations

- **Data.** The data come from PubChem depositors, so they carry their choices. Medicinal chemistry and patented compounds are
  over-represented, while the bare polycyclic systems of the interstellar medium are rare. How far the samples sit from an astrochemical
  list is measured against the computed PAHdb library (`notebook/pahdb_comparison.json`, added 18 October 2026).
- **Privacy and memorisation.** There are no personal data. The 0.099 memorisation is the measured share of samples that repeat a
  deposited molecule; the model is not used to retrieve deposited records.
- **Misuse.** A general molecule generator could be pointed at harmful chemistry. This one is trained only on neutral fused aromatics up
  to 30 heavy atoms, generates without property guidance, and none of its candidates is proposed for synthesis or exposure.
- **Environmental cost.** Four training runs (three seeds and the conditioned model) of 9 to 12 hours each on six threads of a rented
  server, about 43 hours in total (0.5 h per epoch), plus about 10 minutes of sampling per model and temperature.

## Caveats and recommendations

- **Training cap.** Every training run reached its best validation loss at epoch 19 or 20 of 20, so by the project's own rule (decision
  51) the cap was binding. The validation curves are flat to 1e-4 over their last three epochs, which suggests a longer run would change the
  read-outs by less than the seed spread. That longer run has not been done.
- **SMILES validity is not usefulness.** A valid string can still be a molecule the pipeline handles badly. The project fit metric checks
  only the pipeline's input rules (neutral, allowed elements, at most 30 heavy atoms, fused aromatic rings).
- **Size.** Use within the training distribution, molecules of up to 30 heavy atoms. The model has not been tested on the large PAHs of
  astrochemistry.
