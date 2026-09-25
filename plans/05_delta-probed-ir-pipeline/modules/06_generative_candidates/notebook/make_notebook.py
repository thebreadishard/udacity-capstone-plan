#!/usr/bin/env python
"""Writes and executes the Module 06 notebook `generative_model.ipynb` from source cells kept here (25 September 2026; the module-05 layout).

Rubric (Generative AI module): the generative task and the model choice declared and justified · the dataset loaded and inspected · the model's
architecture, training loop and sampling shown and run top to bottom · training curves · the outputs evaluated with metrics fit for the task,
failure cases shown · one design change (conditioning) measured · ethics and responsible use · a short summary. Everything pre-registered in
`PRE_REGISTRATION.md` (24 September 2026) before any training.

Data: `data/pubchem_aromatics_2026-09-24.csv` (frozen; query, counts and SHA-256 in `data/README.md`). Code: `m06/` (own PyTorch model, no
pretrained weights). Results go to `notebook/results.json` for `make_summary.py`. Environment knobs: M06_QUICK=1 → 2,000 training molecules,
2 epochs, one seed, 1,000 samples (a pipeline check, never a result); M06_THREADS → torch threads. Run: python notebook/make_notebook.py [--no-execute]
"""
import os
import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

HERE = Path(__file__).resolve().parent
DATASET = os.environ.get("M06_DATASET", "pubchem_aromatics_2026-09-24.csv")
cells = []


def md(s):
    cells.append(new_markdown_cell(s))


def code(s):
    cells.append(new_code_cell(s))


md(f"""# Module 06 — a generative model of aromatic candidates: a character-level Transformer on SMILES

**The generative task (declared for the rubric).** Generate *new* fused-aromatic molecules — as SMILES strings — that resemble a frozen set of
160,972 PubChem molecules with at least two fused aromatic rings, so that the Δ-probed IR pipeline of plan 05 has candidates to compute next:
molecules inside the families its learned correction is licensed for, not yet in any spectral library. The output is a sequence of characters
that must parse into a valid molecule, be new, be diverse, and fit the project's families; that is what the evaluation measures.

**Why this model.** A decoder-only Transformer trained with next-token cross-entropy on SMILES is the simplest generative model whose samples can be
*checked exactly* (RDKit parses them or not), whose training is stable on a CPU in hours, and whose failure modes (invalid strings, memorisation, mode
collapse) are all measurable. A GAN on discrete strings needs tricks to train and gives no likelihood; a VAE on SMILES trades validity for a
continuous latent we do not need; a diffusion model on graphs is heavier than the question. The architecture is written here in PyTorch from
scratch (`m06/model.py`), ≈ 3 M parameters; no pretrained weights.

**Dataset.** `data/{DATASET}` — the union of PubChem fast-substructure searches for nine fused-aromatic cores, filtered with RDKit to neutral
molecules of C, H, N, O, S, F, Cl with at most 30 heavy atoms and at least two fused aromatic rings; one canonical SMILES per molecule with its
CID (`data/README.md`: query, filters, counts per step, retrieval date, SHA-256). Public-domain records (PubChem); not synthetic, not AI-generated,
not used in modules 02–05. Splits are by Murcko scaffold (sha-hashed 80/10/10), so a scaffold never straddles train and test.

Sections: **Setup · 1 Load and inspect · 2 The model · 3 Training · 4 Sampling and evaluation · 5 The design change: conditioning · 6 Ethics and responsible use · 7 Summary**.""")

md("## Setup")
code(f"""import json, math, os, sys, time, random
from pathlib import Path
import numpy as np, pandas as pd, torch
%matplotlib inline
import matplotlib.pyplot as plt
from IPython.display import display
sys.path.insert(0, str(Path("..") / "m06"))
from data import read_dataset, assign_splits, tokenize, Vocab, hetero_class, prefix_for, murcko
from model import SmilesTransformer
from train import train_model, generate
from evaluate import canonical, descriptors, project_fit, wasserstein1, evaluate_samples, obedience
QUICK = os.environ.get("M06_QUICK") == "1"
torch.set_num_threads(int(os.environ.get("M06_THREADS", "4")))
SEEDS = [0] if QUICK else [0, 1, 2]
N_SAMPLES = 1000 if QUICK else 10000
os.makedirs("figures", exist_ok=True)
DATASET = Path("..") / "data" / "{DATASET}"
PRED = dict(validity=0.85, uniqueness=0.95, novelty=0.50, scaffold_novelty=0.30, project_fit=(0.30, 0.60), obedience=0.80, memorisation=0.10)  # PRE_REGISTRATION.md, fixed 24 Sep 2026
print("quick mode" if QUICK else "pre-registered run", "| torch", torch.__version__, "| threads", torch.get_num_threads(), "| seeds", SEEDS, "| samples per model", N_SAMPLES)""")

md("## 1. Load and inspect")
code("""t0 = time.time(); rows = assign_splits(read_dataset(DATASET)); print(f"{len(rows):,} molecules loaded and split by scaffold in {time.time() - t0:.0f} s")
df = pd.DataFrame(rows)
split_counts = df.split.value_counts().to_dict(); print("splits:", split_counts, "| distinct scaffolds:", df.scaffold.nunique())
lengths = np.array([len(tokenize(s)) + 2 for s in df.smiles]); n_drop = int((lengths > 96).sum())
print(f"token length (with <bos>/<eos>): median {np.median(lengths):.0f}, 95th percentile {np.percentile(lengths, 95):.0f}, max {lengths.max()}; dropped at max_len 96: {n_drop} ({100 * n_drop / len(rows):.2f} %)")
vocab0 = Vocab.build(df.smiles.tolist()); print(f"character vocabulary: {len(vocab0.itos)} tokens:", " ".join(t for t in vocab0.itos if not t.startswith("<")))
display(df[["cid", "smiles", "formula", "n_heavy", "n_arom_rings", "split"]].sample(8, random_state=0).reset_index(drop=True))
fig, axes = plt.subplots(1, 3, figsize=(11, 2.8))
axes[0].hist(df.n_heavy, bins=np.arange(5.5, 31.5, 1), color="tab:blue"); axes[0].set_title("heavy atoms"); axes[1].hist(df.n_arom_rings, bins=np.arange(1.5, 8.5, 1), color="tab:orange"); axes[1].set_title("aromatic rings")
axes[2].hist(lengths, bins=40, color="tab:green"); axes[2].set_title("SMILES tokens"); fig.tight_layout(); fig.savefig("figures/dataset.png", dpi=150); plt.show()""")
code("""from rdkit import Chem
from rdkit.Chem import Draw
show = df[df.split == "train"].sample(8, random_state=1)
display(Draw.MolsToGridImage([Chem.MolFromSmiles(s) for s in show.smiles], molsPerRow=4, subImgSize=(220, 170), legends=[f"CID {c}" for c in show.cid]))""")
md("""*What the inspection says.* The set is what the query made it: fused aromatics of 10–30 heavy atoms, two to five aromatic rings, mostly
neutral C/H/N/O with some S, F and Cl; SMILES of 15–60 characters, so a context of 96 tokens loses almost nothing. Scaffold splitting matters
here more than in most tasks: with random splitting, novelty would be inflated by near-duplicates of training scaffolds in the test set.""")

md("""## 2. The model

A decoder-only Transformer over the character vocabulary: token + learned position embeddings (context 96), four pre-norm blocks of causal
multi-head self-attention (4 heads) and a feed-forward layer (256 → 1024 → 256, GELU, dropout 0.1), a final LayerNorm and a linear head to the
vocabulary. Training objective: next-token cross-entropy on `<bos> … <eos>` sequences with padding masked. Sampling: autoregressive from `<bos>`,
multinomial at a temperature, stopped at `<eos>` or the context length. Design choices, each with its reason: *character level* (the vocabulary
is 30 tokens, so no tokeniser to learn, and every SMILES is representable); *decoder-only* (we need a sampler, not an encoder); *pre-norm* and
*AdamW with warm-up and cosine decay* (stable small-model training without tuning); *dropout 0.1* (160 k sequences, 3 M parameters — mild
regularisation is enough); *early stopping on validation loss* with patience 3.""")
code("""model0 = SmilesTransformer(len(vocab0.itos)); print(model0); print(f"parameters: {model0.n_params():,}")
ids = torch.tensor([vocab0.encode(s) for s in df.smiles.head(4)]); print("input batch", tuple(ids.shape), "→ logits", tuple(model0(ids).shape), "| loss on untrained model", float(model0.loss(ids)), "(ln vocab ≈", round(math.log(len(vocab0.itos)), 2), ")")""")

md("## 3. Training")
code("""logs = {}
def train_or_load(out_dir, seed, conditioning=False, label=None):
    # 25 Sep 2026: M06_REUSE=1 loads weights trained earlier by m06/train.py with the same seed, recipe and dataset (a cache of the identical computation) instead of retraining; never in quick mode
    import json as _json
    p = Path(out_dir) / f"model_seed{seed}.pt"; lg = Path(out_dir) / f"train_log_seed{seed}.json"
    if os.environ.get("M06_REUSE") == "1" and not QUICK and p.exists() and lg.exists():
        L = _json.load(open(lg)); v = Vocab(L["vocab"]); m = SmilesTransformer(len(v.itos), max_len=L["max_len"]); m.load_state_dict(torch.load(p)); m.eval()
        print(f"reused: {p} — {len(L['history'])} epochs trained by m06/train.py (seed {seed}, conditioning={L['conditioning']}, n_train {L['n_train']}), best val loss {min(h['val_loss'] for h in L['history']):.3f}")
        return m, v, L["history"]
    return train_model(rows, out_dir, seed=seed, epochs=20, conditioning=conditioning, quick=QUICK, log=log_to(label if label is not None else seed))

def log_to(seed):
    def _log(msg):
        print(f"[seed {seed}] {msg}", flush=True); logs.setdefault(seed, []).append(msg)
    return _log
t0 = time.time(); models = {}
for seed in SEEDS:
    models[seed] = train_or_load(("out/quick/" if QUICK else "out/") + f"seed{seed}", seed)   # quick mode writes beside, never over, a real run's weights
print(f"trained {len(SEEDS)} model(s) in {(time.time() - t0) / 60:.1f} min")
fig, axes = plt.subplots(1, 2, figsize=(9, 3.2))
for seed, (m, v, hist) in models.items():
    ep = [h["epoch"] for h in hist]
    axes[0].plot(ep, [h["train_loss"] for h in hist], label=f"train, seed {seed}"); axes[0].plot(ep, [h["val_loss"] for h in hist], "--", label=f"val, seed {seed}")
    axes[1].plot(ep, [h["validity_200"] for h in hist], marker="o", label=f"seed {seed}")
axes[0].set_xlabel("epoch"); axes[0].set_ylabel("cross-entropy per token"); axes[0].legend(fontsize=8); axes[1].set_xlabel("epoch"); axes[1].set_ylabel("validity of 200 samples (T = 1)"); axes[1].set_ylim(0, 1.02); axes[1].legend(fontsize=8)
fig.tight_layout(); fig.savefig("figures/training_curves.png", dpi=150); plt.show()
hist_tab = pd.DataFrame([dict(seed=s, epochs=len(h), best_val_loss=min(x["val_loss"] for x in h), final_validity_200=h[-1]["validity_200"], minutes=sum(x["seconds"] for x in h) / 60) for s, (m, v, h) in models.items()]).round(3); display(hist_tab)""")
md("""*Reading the curves.* Train and validation loss fall together and stay close (the scaffold split keeps them honest); the validity of raw
samples rises within the first epochs from near zero to the plateau the evaluation measures below. Early stopping on validation loss picks the
checkpoint; the epoch counts per seed are in the table.""")

md("""## 4. Sampling and evaluation

Pre-registered metrics (24 September, before training): **validity** (RDKit parses), **uniqueness** (distinct canonical SMILES among valid),
**novelty** (valid unique samples not in the training set) and **scaffold novelty** (Murcko scaffold not in training) — the MOSES / GuacaMol
trio with the scaffold refinement; **memorisation** (valid samples that *are* training molecules); **distribution match** as Wasserstein-1 distances of
heavy-atom, aromatic-ring and heteroatom counts against the held-out test set; and **project fit** (valid novel samples that are neutral, within the
corpus's element set, ≤ 30 heavy atoms and fused-aromatic). Predictions were fixed at validity ≥ 0.85, uniqueness ≥ 0.95, novelty ≥ 0.50,
scaffold novelty ≥ 0.30, memorisation ≤ 0.10, project fit 0.30–0.60, three seeds within ±0.03 on validity.""")
code("""train_smiles = df[df.split == "train"].smiles.tolist(); train_scaf = df[df.split == "train"].scaffold.tolist(); test_rows = [r for r in rows if r["split"] == "test"]
results = {}; samples = {}
for seed, (m, v, hist) in models.items():
    for T in (1.0, 0.7):
        t0 = time.time(); s = generate(m, v, n=N_SAMPLES, temperature=T, seed=seed); res, extra = evaluate_samples(s, train_smiles, train_scaf, test_rows, murcko)
        res["seconds"] = round(time.time() - t0, 1); results[(seed, T)] = res; samples[(seed, T)] = (s, extra)
        print(f"seed {seed} T={T}: validity {res['validity']:.3f} uniqueness {res['uniqueness']:.3f} novelty {res['novelty']:.3f} scaffold novelty {res['scaffold_novelty']:.3f} memorisation {res['memorisation']:.3f} project fit {res['project_fit']:.3f} | W1 heavy {res['w1_heavy']:.2f} rings {res['w1_arom_rings']:.2f} hetero {res['w1_hetero']:.2f} ({res['seconds']} s)")
tab = pd.DataFrame([dict(seed=s, T=T, **{k: r[k] for k in ("validity", "uniqueness", "novelty", "scaffold_novelty", "memorisation", "project_fit", "w1_heavy", "w1_arom_rings", "w1_hetero")}) for (s, T), r in results.items()]).round(3)
display(tab)
# 25 Sep 2026 (dated amendment of the pre-registration): the control the model must beat — a 5-gram token Markov baseline on the same train split, same evaluation
from baseline_ngram import fit as ngram_fit, sample_one as ngram_sample
import random as _random
t0 = time.time(); ng = ngram_fit(train_smiles, 5); _rng = _random.Random(0); ng_samples = [ngram_sample(ng, 5, _rng) for _ in range(N_SAMPLES)]
baseline_res, _ = evaluate_samples(ng_samples, train_smiles, train_scaf, test_rows, murcko); baseline_res["seconds"] = round(time.time() - t0, 1)
r0 = results[(SEEDS[0], 1.0)]
baseline_check = dict(validity_margin=r0["validity"] - baseline_res["validity"], project_fit_margin=r0["project_fit"] - baseline_res["project_fit"],
                      w1_smaller_all=all((r0[k] or 0) < (baseline_res[k] or 0) for k in ("w1_heavy", "w1_arom_rings", "w1_hetero")))
baseline_check["beats_baseline"] = bool(baseline_check["validity_margin"] >= 0.25 and baseline_check["project_fit_margin"] >= 0.15 and baseline_check["w1_smaller_all"])
print(f"5-gram baseline (10,000 samples, T = 1.0): validity {baseline_res['validity']:.3f} uniqueness {baseline_res['uniqueness']:.3f} novelty {baseline_res['novelty']:.3f} project fit {baseline_res['project_fit']:.3f} | "
      f"W1 heavy {baseline_res['w1_heavy']:.2f} rings {baseline_res['w1_arom_rings']:.2f} hetero {baseline_res['w1_hetero']:.2f} ({baseline_res['seconds']:.0f} s)")
print(f"seed {SEEDS[0]} vs baseline: validity {baseline_check['validity_margin']:+.3f} (rule ≥ 0.25), project fit {baseline_check['project_fit_margin']:+.3f} (rule ≥ 0.15), all W1 smaller: {baseline_check['w1_smaller_all']} → "
      + ("beats the baseline" if baseline_check["beats_baseline"] else "does NOT beat the baseline — FAIL by the amendment's rule" + (" (expected in quick mode)" if QUICK else "")))
m10 = tab[tab["T"] == 1.0].mean(numeric_only=True)
verdict = {"validity": m10.validity >= PRED["validity"], "uniqueness": m10.uniqueness >= PRED["uniqueness"], "novelty": m10.novelty >= PRED["novelty"], "scaffold_novelty": m10.scaffold_novelty >= PRED["scaffold_novelty"],
           "memorisation": m10.memorisation <= PRED["memorisation"], "project_fit": PRED["project_fit"][0] <= m10.project_fit <= PRED["project_fit"][1],
           "seed_spread_validity": (tab[tab["T"] == 1.0].validity.max() - tab[tab["T"] == 1.0].validity.min()) <= 0.03 if len(SEEDS) > 1 else None}
print("against the pre-registered predictions at T = 1.0 (seed mean):", {k: ("met" if v else "NOT met") if v is not None else "n/a (one seed)" for k, v in verdict.items()})""")
code("""fig, axes = plt.subplots(1, 3, figsize=(11, 2.8)); s10 = samples[(SEEDS[0], 1.0)][1]["valid_unique"]
d_s = np.array([descriptors(s) for s in s10]); d_t = np.array([descriptors(r["smiles"]) for r in test_rows])
for k, (ax, name, bins) in enumerate(zip(axes, ("heavy atoms", "aromatic rings", "heteroatoms"), (np.arange(3.5, 40.5, 1), np.arange(-0.5, 9.5, 1), np.arange(-0.5, 12.5, 1)))):
    ax.hist(d_t[:, k], bins=bins, density=True, alpha=0.5, label="held-out test"); ax.hist(d_s[:, k], bins=bins, density=True, alpha=0.5, label=f"samples (seed {SEEDS[0]}, T = 1)"); ax.set_title(name); ax.legend(fontsize=7)
fig.tight_layout(); fig.savefig("figures/distribution_match.png", dpi=150); plt.show()""")
md("""### Failure cases (shown, not hidden)""")
code("""s, extra = samples[(SEEDS[0], 1.0)]
print(f"invalid strings ({len(s) - int(round(results[(SEEDS[0], 1.0)]['validity'] * len(s)))} of {len(s)}), first ten:"); print("\\n".join("  " + x for x in extra["invalid_examples"][:10]))
dups = [x for x in extra["valid_unique"] if x in set(train_smiles)][:6]; print(f"training molecules reproduced verbatim (memorisation): {len([x for x in extra['valid_unique'] if x in set(train_smiles)])}; e.g. {dups}")
charged = [x for x in extra["novel"] if any(a.GetFormalCharge() for a in Chem.MolFromSmiles(x).GetAtoms())][:6]; print(f"charged outputs among novel: {len([x for x in extra['novel'] if any(a.GetFormalCharge() for a in Chem.MolFromSmiles(x).GetAtoms())])}; e.g. {charged}")
nonfit = [x for x in extra["novel"] if not project_fit(x)][:8]
print(f"novel samples outside the project families: {len([x for x in extra['novel'] if not project_fit(x)])} of {len(extra['novel'])}")
if nonfit: display(Draw.MolsToGridImage([Chem.MolFromSmiles(x) for x in nonfit], molsPerRow=4, subImgSize=(200, 150), legends=["novel but outside the project's families"] * len(nonfit)))""")
md("""### Five samples and their nearest training neighbours""")
code("""from rdkit.Chem import rdFingerprintGenerator, DataStructs
fpg = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
train_fit = [x for x in extra["novel"] if project_fit(x)]; rng = random.Random(0); picks = rng.sample(train_fit, min(5, len(train_fit)))
sub = train_smiles if len(train_smiles) <= 40000 else rng.sample(train_smiles, 40000); fps = [fpg.GetFingerprint(Chem.MolFromSmiles(x)) for x in sub]
mols, legends = [], []
for p in picks:
    sims = DataStructs.BulkTanimotoSimilarity(fpg.GetFingerprint(Chem.MolFromSmiles(p)), fps); top = np.argsort(sims)[::-1][:3]
    mols += [Chem.MolFromSmiles(p)] + [Chem.MolFromSmiles(sub[i]) for i in top]; legends += ["sample"] + [f"train, Tanimoto {sims[i]:.2f}" for i in top]
print(f"novel project-fit samples available for the neighbour grid: {len(train_fit)}; shown: {len(picks)}")
if mols: display(Draw.MolsToGridImage(mols, molsPerRow=4, subImgSize=(200, 150), legends=legends))
else: print("no novel project-fit sample to show (expected in quick mode after two epochs)")""")
md("""*Reading.* The trio says whether the model writes chemistry (validity), does not copy (memorisation, novelty) and does not collapse
(uniqueness); the histograms say whether it writes the *same* chemistry as the held-out set; the neighbour grid shows what "novel" means in
practice — usually a known scaffold with a new decoration, sometimes a new fusion. Project fit is the number the atlas would use: the share of
candidates the pipeline's correction is licensed for.""")

md("""## 5. The design change: conditioning tokens

One controlled change, fixed before training: two prefix tokens — the ring-count class (`<r2>`, `<r3>`, `<r4+>`) and the heteroatom class
(`<hnone>`, `<hN>`, `<hO>`, `<hS>`, `<hmixed>`) — placed after `<bos>` during training, so that the atlas can ask for "three rings, one nitrogen".
The pre-registered read-out is **obedience**: the fraction of valid samples whose ring and heteroatom class equal the request, predicted ≥ 0.80,
plus the same trio as above to see what conditioning costs.""")
code("""t0 = time.time(); mc, vc, hc = train_or_load(("out/quick/" if QUICK else "out/") + "cond_seed0", 0, conditioning=True, label="cond")
print(f"conditioned model trained in {(time.time() - t0) / 60:.1f} min; vocabulary {len(vc.itos)}")
def ring_class_of(smi):
    n = descriptors(smi)[1]; return "<r2>" if n <= 2 else "<r3>" if n == 3 else "<r4+>"
requests = [(r, h) for r in ("<r2>", "<r3>", "<r4+>") for h in ("<hnone>", "<hN>", "<hO>", "<hS>")]
per = 100 if QUICK else 500; swp = []; rows_ob = []
for r, h in requests:
    s = generate(mc, vc, n=per, temperature=1.0, prefix=(r, h), seed=11); swp += [(x, (r, h)) for x in s]
    ob = obedience([(x, (r, h)) for x in s], hetero_class, ring_class_of); val = sum(1 for x in s if canonical(x)) / per; rows_ob.append(dict(request=f"{r} {h}", validity=round(val, 3), obedience=round(ob, 3)))
ob_all = obedience(swp, hetero_class, ring_class_of); ob_tab = pd.DataFrame(rows_ob); display(ob_tab)
s_c = generate(mc, vc, n=N_SAMPLES, temperature=1.0, prefix=(), seed=0); res_c, _ = evaluate_samples(s_c, train_smiles, train_scaf, test_rows, murcko)
print(f"obedience over all requests: {ob_all:.3f} (predicted ≥ {PRED['obedience']}) | unconditioned sampling from the conditioned model: validity {res_c['validity']:.3f}, novelty {res_c['novelty']:.3f}, project fit {res_c['project_fit']:.3f}")""")
md("""*Reading.* Conditioning is the atlas's steering wheel; the table shows for which requests it works and where the model runs out of examples
(requests that are rare in PubChem, such as sulfur in four-ring systems, are where obedience drops). The unconditioned metrics of the
conditioned model say whether the change cost anything on the trio.""")

md("""## 6. Ethics and responsible use

- **Misuse and dual use.** A generator of aromatic structures is a generator of *candidates for spectroscopy*, not of syntheses. Polycyclic
  aromatics include carcinogens and persistent pollutants; the outputs are labelled as spectroscopic targets, no synthesis routes or toxicity-directed
  property predictions are produced, and the model card released with the notebook says so.
- **Creative ownership and attribution.** The training data are public-domain PubChem records; generated strings are not attributed to
  depositors, and the model is checked *not* to return depositor records (the memorisation rate above is the measurement, with the prediction ≤ 0.10).
- **Bias.** PubChem over-represents what chemists have made or patented — medicinal-chemistry decorations, not the bare polycyclic systems of
  the interstellar medium. The generator inherits that; the project-fit metric and the distribution histograms are where it shows, and PAHdb's species
  list is the comparison set the report uses to say how far the sample distribution sits from the astrochemical one (never as training data).
- **Environmental cost.** One CPU-day of training; recorded in the results file and the report.
- **Societal impact.** Modest and positive — cheaper triage of which molecules to compute for astronomical spectroscopy — and the report says what
  it does not claim: no property, no safety, no synthesis.""")

md("## 7. Summary")
code("""r0 = results[(SEEDS[0], 1.0)]
summary = (f"A character-level decoder-only Transformer ({model0.n_params():,} parameters, written in PyTorch without pretrained weights) was trained on "
           f"{split_counts.get('train', 0):,} fused-aromatic PubChem molecules split by scaffold. At temperature 1.0 its samples are {100 * m10.validity:.0f} % valid, "
           f"{100 * m10.uniqueness:.0f} % unique and {100 * m10.novelty:.0f} % novel ({100 * m10.scaffold_novelty:.0f} % with a scaffold unseen in training), with a memorisation rate of "
           f"{100 * m10.memorisation:.1f} % and a project-fit share of {100 * m10.project_fit:.0f} %; the heavy-atom, ring and heteroatom distributions of the samples sit "
           f"{r0['w1_heavy']:.1f}, {r0['w1_arom_rings']:.2f} and {r0['w1_hetero']:.2f} (Wasserstein-1) from the held-out set. Conditioning on ring and heteroatom classes is obeyed in "
           f"{100 * ob_all:.0f} % of valid samples. Against the predictions fixed before training, {sum(1 for v in verdict.values() if v)} of {sum(1 for v in verdict.values() if v is not None)} "
           f"read-outs were met" + (" (quick mode: a pipeline check, not a result)" if QUICK else "") + ".")
print(summary)
out = dict(quick=QUICK, dataset=str(DATASET.name), n_rows=len(rows), splits=split_counts, n_dropped_len96=n_drop, vocab_size=len(vocab0.itos), params=model0.n_params(), seeds=SEEDS, n_samples=N_SAMPLES,
           training={str(s): h for s, (m, v, h) in models.items()}, metrics={f"seed{s}_T{T}": r for (s, T), r in results.items()}, predictions=PRED, verdict={k: (None if v is None else bool(v)) for k, v in verdict.items()},
           conditioning=dict(obedience_all=ob_all, per_request=rows_ob, unconditioned_metrics=res_c, history=hc), summary=summary, date=time.strftime("%Y-%m-%d %H:%M"))
out["baseline"] = dict(model="5-gram token Markov, stupid back-off, train split only", metrics=baseline_res, check=baseline_check)
json.dump(out, open("results.json", "w"), indent=1); print("results.json written")""")
md("""*What the rubric asks for in words.* The task, the model and the reason for it are in the header; the data and their inspection in section 1;
the architecture, training loop, curves and sampling in sections 2–3; the metrics, the histograms, the failure gallery and the neighbour grid in
section 4; the one measured design change in section 5; the ethics in section 6. Every number in the report traces to a cell here and to the
pre-registration written before training.""")

nb = new_notebook(cells=cells, metadata={"kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"}})
path = HERE / "generative_model.ipynb"
nbformat.write(nb, path)
if "--no-execute" not in sys.argv:
    NotebookClient(nb, timeout=6 * 3600, kernel_name="python3", resources={"metadata": {"path": str(HERE)}}).execute()
    nbformat.write(nb, path)
    print("executed and written:", path)
else:
    print("written (not executed):", path, f"{len(cells)} cells")
