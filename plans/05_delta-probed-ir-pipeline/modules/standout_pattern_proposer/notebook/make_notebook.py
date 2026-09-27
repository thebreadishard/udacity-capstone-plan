#!/usr/bin/env python
"""Writes and executes the standout module's notebook `pattern_proposer.ipynb` from source cells kept here (27 September 2026; the module-05/06 layout).

What the notebook shows, top to bottom: the question and the pre-registration · the data (exports of the corpus Δ₂ response records, splits) · the
recovery replayed live on one small molecule for the fixed order, the hand-feature scorer and the oracle · the orderings (P1 features, P2 architecture)
and the validation read of the fair-chance search · the registered read-outs of E1 (band pool), E2 (all pairs) and the adaptive variants, rebuilt from the
committed read-out JSONs · the deck-cost comparison · ethics · a summary written to `notebook/results.json` for `make_summary.py`.

Everything heavy (the pools on hel1-23, the fits) is *read* here, not re-run; the one live computation is three curves on the smallest layer-B molecule
(≈ 1–2 minutes on one thread). Environment knobs: PP_THREADS (torch threads, default 1). Run: python notebook/make_notebook.py [--no-execute]
"""
import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

HERE = Path(__file__).resolve().parent
cells = []


def md(s):
    cells.append(new_markdown_cell(s.strip()))


def code(s):
    cells.append(new_code_cell(s.strip()))


md("""# Standout module — the pattern proposer: which measurement next?

*Executed notebook of the standout module (27 September 2026). The plan of record is the pre-registration of 26 September
(`GoalGathering/notes/PreRegistration_2026-09-26_Standout_Pattern_Proposer.md`) with its dated amendments and outcome sections; the design note is
`../DESIGN_2026-09-27.md`, the file map `../README.md`.*

**The task.** Every molecule of plan 05 has a coupling table Δ₂ that we can only afford to know in part: each entry costs an expensive energy. The recovery
reconstructs the table from *pattern responses* R_s = ½ aᵀ Δ a and stops when its held-out residual ρ_off is low enough. The deck fixes which patterns
exist and in which order they are measured. This module asks whether a network that has only seen other molecules can choose a better order — and,
since 27 September, whether the deck should reach every pair at all. The generative object is the order; the generator is a scorer of pairs of modes.

**Why it is a simulation with no new quantum chemistry.** The corpus's DFT-against-DFT Hessians give the full Δ₂ for 289 molecules, hence the exact
response of any pattern; ordering the deck and replaying the recovery costs CPU minutes per molecule. Every number is proxy-level (DFT against DFT) and is
labelled so.""")

code("""import json, os, sys, time
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from IPython.display import display, Markdown
sys.path.insert(0, str(Path("..").resolve()))
sys.path.insert(0, str((Path("..") / ".." / "05_support_predictor" / "m05").resolve()))
import torch
torch.set_num_threads(int(os.environ.get("PP_THREADS", "1")))
from pp import core as C, scorer as S, embed_scorer as E
OUT = Path("..") / "out"
FIG = Path("figures"); FIG.mkdir(exist_ok=True)
print("torch", torch.__version__, "| threads", torch.get_num_threads(), "| exports:", (OUT / "exports").exists())""")

md("""## 1. Data — the corpus Δ₂ response records and the splits

One export per molecule (`run_export.py`): modes and frequencies, atomic participations, the low-level Hessian (what a scorer may see), Δ₂ (the answer,
used only for the oracle and the truth-based read-outs), the probe deck's patterns and their exact responses. Splits are hashed and were fixed before the
first run: the parents (unsubstituted aromatics, larger than any training molecule) are evaluation only; A2/B molecules 70/10/20.""")

code("""index = json.load(open(OUT / "exports" / "index.json"))["molecules"]
df = pd.DataFrame(index)
tab = df.groupby(["layer", "split"]).size().unstack(fill_value=0)
display(tab)
print(f"{len(df)} molecules; evaluation {int((df.split != 'train').sum() - (df.split == 'val').sum())} (parents {(df.split == 'eval_parents').sum()}), validation {(df.split == 'val').sum()}, training {(df.split == 'train').sum()}")
share = pd.DataFrame(json.load(open(OUT / "inband_share_2026-09-26.json")))
print("in-band share of off-diagonal coupling power (26 Sep), mean per layer:", share.groupby("layer")["inband"].mean().round(3).to_dict(), "| all:", round(float(share.inband.mean()), 3))
fig, ax = plt.subplots(figsize=(5, 3)); ax.hist(share.inband, bins=20); ax.set_xlabel("share of off-diagonal coupling power inside the 200 cm⁻¹ band"); ax.set_ylabel("molecules")
fig.tight_layout(); fig.savefig(FIG / "inband_share.png", dpi=120); plt.show()""")

md("""## 2. The recovery, replayed live on one small molecule

Consume the single-mode block, then the off-diagonal patterns in the given order; after every stride solve the banded-ℓ₁ recovery (FISTA, warm-started,
λ chosen on the held-out patterns) and record the held-out ρ_off — the plan's own stopping quantity, which needs no truth. Three orders: P0 (the deck's
hashed order), P1 (the hand-feature scorer, seed 0) and P3 (the oracle, which knows Δ₂).""")

code("""ids = sorted([r["id"] for r in index if r["id"].startswith("B_") and r["split"] != "train"], key=lambda i: next(x for x in index if x["id"] == i).get("M", 0))
mid = ids[0] if ids else sorted(r["id"] for r in index if r["id"].startswith("B_"))[0]
e = C.load_export(OUT / "exports" / f"{mid}.npz")
X, _, pairs = S.pair_features(e)
sc = S.Scorer.load(OUT / "p1", 0)
pool = C.order_p0(e); stride = max(2, int(np.ceil(len(pool) / 30)))
t0 = time.time()
curves = {"P0 (hashed)": C.rho_curve(e, pool, stride=stride),
          "P1 (hand-feature scorer)": C.rho_curve(e, C.order_by_scores(e, S.scores_matrix(e, sc.predict(X), pairs)), stride=stride),
          "P3 (oracle)": C.rho_curve(e, C.order_oracle(e), stride=stride)}
print(f"{mid}: M = {e['M']} modes, {len(pool)} off-diagonal patterns in the band pool, stride {stride}; {time.time() - t0:.0f} s for three curves")
fig, ax = plt.subplots(figsize=(6, 3.6))
for name, c in curves.items():
    ax.plot([r[0] for r in c], [r[2] for r in c], label=name)
ax.set_xlabel("energies consumed"); ax.set_ylabel("held-out ρ_off"); ax.set_ylim(0, 1.05); ax.legend(); ax.set_title(f"{mid}: the recovery under three orders")
fig.tight_layout(); fig.savefig(FIG / "one_molecule_curves.png", dpi=120); plt.show()
for name, c in curves.items():
    print(f"  {name:26s} ρ_off after the single block {c[0][2]:.3f}, at the end {c[-1][2]:.3f}; energies to ρ_off ≤ 0.3: {C.k_off_at(c, 0.3, e['M'])}")""")

md("""## 3. The orderings, and the fair chance for the learned representation

**P1** — an MLP on 21 hand-made pair features (frequencies, |Δω|, the band flag, atom-sharing overlaps of the participations, projections of the low-level
Hessian) → log₁₀|Δ_ij|. **P2** — the rung-C equivariant body of module 05 (unchanged) turns atoms, coordinates and the low-level Hessian into per-atom features;
a mode's embedding is its participation-weighted sum; a pair head reads two embeddings and |Δω|. **P12** — the z-score average of the two. A pattern's score is
the *mean* over the pairs it touches (dated amendment: the sum favoured broad random patterns on the planted test).

The user's rule of 26 September 12:1x: no sentence about the learned representation before a five-stage search (recipe, loss, capacity, data growth,
pretraining), each stage read on the validation split by the ordering metric with a margin fixed before the numbers.""")

code("""rows = []
for f, stage in ((OUT / "stage2_readout_2026-09-26.json", "stage 2"), (OUT / "stage3_readout_2026-09-26.json", "stage 3")):
    if f.exists():
        r = json.load(open(f))
        for name, res in r["results"].items():
            s = res["summary"]
            rows.append(dict(read=stage, recipe=name, spearman=round(s["spearman"]["mean"], 4), spearman_min=round(s["spearman"]["min"], 4), spearman_max=round(s["spearman"]["max"], 4),
                             mse=round(s["mse"]["mean"], 4), p10_out_of_band=round(s["p10_out"]["mean"], 3), p10_in_band=round(s["p10_in"]["mean"], 3)))
val = pd.DataFrame(rows).drop_duplicates(subset=["recipe"], keep="last")
display(val)
p2 = E.EmbedScorer.load(OUT / "p2s1_lr1e-3_w128", 0)
print("P2 (stage-1 recipe): parameters", sum(p.numel() for p in p2.params), "| P1 features:", X.shape[1])
print("Reading rule: stage 2 by the incumbent's seed spread (18:1x), stage 3 the same; from stage 4 a paired per-molecule Wilcoxon test. Stages 1–3: recipe +0.03, loss and capacity within the margins; nothing licensed either way.")""")

md("""## 4. The registered read-outs — E1 (band pool), E2 (all pairs), the adaptive variants

Rebuilt from the committed read-out JSONs (`out/sim/*_readout.json`, produced by `readout.py` from the pools that ran on hel1-23). Primary read-out:
K_off(0.3) as a ratio to P0; fallback where P0 does not reach 0.3 (the band pool): n_half (energies to the midpoint between the single block and P0's end
point) and the AUC of ρ_off over P0's checkpoint grid, both as per-molecule ratios (median; fraction improved).""")

code("""def table(readout, split, tag="rho_off"):
    r = json.load(open(OUT / "sim" / readout))[split]
    t = r[tag]
    rows = [dict(ordering=n, n=v["n_half"], median_n_half_ratio=v["median_half_ratio"], half_improved=v["frac_half_improved"], median_auc_ratio=v["median_auc_ratio"], auc_improved=v["frac_auc_improved"])
            for n, v in t.items() if isinstance(v, dict)]
    d = pd.DataFrame(rows).set_index("ordering").round(3)
    d.attrs["P0"] = (t["P0_start_median"], t["P0_final_median"], r["n_molecules"], r["P0_reaches_K_off_0p3"])
    return d
summary_rows = []
for readout, label in (("band_p2_readout.json", "E1 band pool"), ("all_p2_readout.json", "E2 all pairs"), ("band_p2s1A_readout.json", "band pool + adaptive")):
    for split in ("eval_parents", "eval"):
        d = table(readout, split)
        s, f, n, k = d.attrs["P0"]
        display(Markdown(f"**{label}, {split} ({n} molecules): P0 median ρ_off {s:.3f} → {f:.3f} over the whole deck; P0 reaches 0.3 on {k}**"))
        display(d)
        for name in d.index:
            summary_rows.append(dict(experiment=label, split=split, ordering=name, median_n_half_ratio=d.loc[name, "median_n_half_ratio"]))
sm = pd.DataFrame(summary_rows)
fig, axes = plt.subplots(1, 3, figsize=(12, 3.8), sharey=True)
for ax, (label, g) in zip(axes, sm.groupby("experiment", sort=False)):
    piv = g.pivot(index="ordering", columns="split", values="median_n_half_ratio")
    piv.plot.barh(ax=ax, legend=(ax is axes[0])); ax.set_title(label); ax.set_xlabel("median n_half ratio vs P0"); ax.axvline(1.0, color="k", lw=0.8)
fig.tight_layout(); fig.savefig(FIG / "n_half_ratios.png", dpi=120); plt.show()""")

md("""### 4a. Adaptive ordering, paired per molecule (S5)

P0+A, P1+A, P2+A re-rank the remaining patterns after every checkpoint by z(prior) + z(feedback), feedback being the mean over touched pairs of
log₁₀|Δ̂_ij| from the current reconstruction, with optimism for untouched pairs (the correction the planted dry run forced before any real molecule ran).
The paired statistics below are computed from the merged simulation JSON when it is present locally and otherwise loaded from the committed
`out/sim/band_p2s1A_paired.json` written by this cell.""")

code("""sys.path.insert(0, str(Path("..").resolve()))
from readout import per_molecule
paired_path = OUT / "sim" / "band_p2s1A_paired.json"
merged = OUT / "sim" / "band_p2s1A_merged.json"
if merged.exists():
    res = json.load(open(merged))
    pairs_ab = [("P0A", "P0")] + [(f"P{k}A_seed{s}", f"P{k}_seed{s}") for k in (1, 2) for s in range(3)]
    paired = {}
    for split in ("eval_parents", "eval"):
        mols = {i: m for i, m in res["per_molecule"].items() if m["split"] == split}
        paired[split] = {}
        for a, b in pairs_ab:
            nh, au = [], []
            for m in mols.values():
                pm = per_molecule(m, [a] if a == "P0A" else [a, b])
                x = pm[(a, "rho_off")]
                yh = pm[(a, "rho_off")]["base_half"] if a == "P0A" else pm[(b, "rho_off")]["n_half"]
                ya = 1.0 if a == "P0A" else pm[(b, "rho_off")]["auc_ratio"]
                if x["n_half"] is not None and yh is not None: nh.append((x["n_half"], yh))
                au.append((x["auc_ratio"], ya))
            paired[split][f"{a} vs {b}"] = dict(n=len(mols), n_half_better=float(np.mean([u < v for u, v in nh])), n_half_equal=float(np.mean([u == v for u, v in nh])),
                                              median_n_half_ratio=float(np.median([u / max(v, 1) for u, v in nh])), auc_better=float(np.mean([u < v for u, v in au])),
                                              median_auc_ratio=float(np.median([u / v for u, v in au])))
    json.dump(paired, open(paired_path, "w"), indent=1)
else:
    paired = json.load(open(paired_path))
for split, t in paired.items():
    display(Markdown(f"**{split}** — fraction of molecules where the adaptive variant is strictly better / equal, and median ratios adaptive/fixed"))
    display(pd.DataFrame(t).T.round(3))
print("S5 (P1+A better than P1 on ≥ 70 % of molecules): fails on n_half (mostly ties at the checkpoint grid), passes on the AUC (95–100 %). The oracle gap is knowledge, not feedback.")""")

md("""## 5. The deck itself — the band candidate set against every pair

`deck_cost_readout.py` compares, per evaluation split, what the band deck and the all-pairs candidate set cost and buy. This is the result that changes
plan 05's deck design (pre-registered for after the 28th: `PreRegistration_2026-09-27_Wide_Candidate_Deck_Stop_Rule.md`).""")

code("""dc = json.load(open(OUT / "sim" / "deck_cost_2026-09-27.json"))
rows = []
for split, r in dc.items():
    rows.append(dict(split=split, molecules=r["n_molecules"], band_deck_energies=r["band_deck_energies"], all_pairs_energies=r["wide_pool_energies"],
                     band_final_rho_off=round(r["band_deck_final_rho_off"], 3), all_pairs_final_rho_off=round(r["wide_pool_final_rho_off"], 3),
                     to_0p3_P0=r["wide_K_off_0p3_P0"], to_0p3_P1=r["wide_K_off_0p3_P1"], to_0p3_P12=r["wide_K_off_0p3_P12"], to_0p3_oracle=r["wide_K_off_0p3_oracle"],
                     P12_over_band_deck=round(r["wide_K_off_0p3_P12_over_band_deck"], 2)))
deck = pd.DataFrame(rows).set_index("split")
display(deck)""")

md("""## 6. Ethics and responsible use

The module proposes *which* calculation to run next, never a molecule or a claim about it. Its failure mode is wasted compute, not a wrong spectrum: the
stopping quantity (held-out ρ_off) is measured, not predicted. Every number is proxy-level (DFT against DFT) and labelled so; the oracle column is a ceiling,
not an achievable order. The data are the project's own corpus. The fair-chance rule protects the learned representation from a premature negative verdict
and, symmetrically, the reader from a premature positive one: nothing about it is licensed before stage 5.""")

md("## 7. Summary")

code("""e1p = table("band_p2_readout.json", "eval_parents"); e1s = table("band_p2_readout.json", "eval")
e2p = table("all_p2_readout.json", "eval_parents"); e2s = table("all_p2_readout.json", "eval")
best = lambda d, pref: float(min(d.loc[[i for i in d.index if i.startswith(pref)], "median_n_half_ratio"]))  # noqa: E731
summary = (f"On the band pool the learned order reaches the halfway point with {best(e1p, 'P1_'):.2f} (parents) / {best(e1s, 'P1_'):.2f} (substituted) of the fixed order's energies "
           f"(oracle {best(e1p, 'P3'):.2f} / {best(e1s, 'P3'):.2f}); on the all-pairs pool the fixed order itself ends at ρ_off {dc['eval_parents']['wide_pool_final_rho_off']:.2f} where the band deck ends at "
           f"{dc['eval_parents']['band_deck_final_rho_off']:.2f}, and the learned order reaches 0.3 at {dc['eval_parents']['wide_K_off_0p3_P12_over_band_deck']:.2f}× the whole band deck "
           f"(oracle {dc['eval_parents']['wide_K_off_0p3_oracle_over_band_deck']:.2f}×). Feedback during measurement helps the blind order and not the scorer's halfway point; "
           f"the gap to the oracle is knowledge. Stages 1–3 of the fair-chance search moved the validation Spearman from "
           f"{val.set_index('recipe').loc['p2', 'spearman'] if 'p2' in val.recipe.values else float('nan'):.3f} to {val.spearman.max():.3f} (P1 {val.set_index('recipe').loc['P1', 'spearman']:.3f}); nothing about the learned representation is licensed before stage 5.")
print(summary)
out = dict(date=time.strftime("%Y-%m-%d %H:%M"), molecules=len(df), splits=tab.to_dict(), live_molecule=dict(id=mid, M=int(e["M"]), curves={k: dict(final_rho_off=c[-1][2], k_off_0p3=C.k_off_at(c, 0.3, e["M"])) for k, c in curves.items()}),
           validation=val.to_dict(orient="records"), n_half_ratios=sm.to_dict(orient="records"), paired_adaptive=paired, deck_cost=dc, summary=summary)
json.dump(out, open("results.json", "w"), indent=1); print("results.json written")""")

nb = new_notebook(cells=cells, metadata={"kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"}})
path = HERE / "pattern_proposer.ipynb"
nbformat.write(nb, path)
if "--no-execute" not in sys.argv:
    NotebookClient(nb, timeout=3600, kernel_name="python3", resources={"metadata": {"path": str(HERE)}}).execute()
    nbformat.write(nb, path)
    print("executed and written:", path)
else:
    print("written (not executed):", path, f"{len(cells)} cells")
