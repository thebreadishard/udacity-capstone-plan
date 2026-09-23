"""E6 — the embedding line as a learning curve in *data* (pre-registered 19 September 2026, 23:2x:
GoalGathering/notes/PreRegistration_2026-09-19_E6_Learning_Curve_in_Data.md; run 23 September on the CCX53 after E6 phase 1).

Data: corpus layers A (45) and A2 (199 done) — B3LYP and ωB97X Hessians at the B3LYP/6-31G* geometry; the mode-basis correction
matrix K_ij = L_iᵀ ΔH L_j / (2 √(ω_i ω_j)) in cm⁻¹ (diagonal = the per-mode first-order shift). Every molecule with both Hessians is
used, as in the E-series of 19 September (the module-05 release additionally drops molecules with an imaginary mode; not done here,
so that hold-out (a) stays the set of that night).

Held-out sets, fixed by the pre-registration:
  (a) the 12 layer-A molecules of 19 September (sha1 order of the layer-A ids, the first ceil(25 %));
  (b) scaffold hold-out inside A2: all substituted molecules of the first two cores in sha1 order of the core name
      (written into the results file before any training).
Training pool: everything else, in sha1 order of the id; sizes 45, 100 and the full pool (≈ 190; the pre-registered "200").

Models (three seeds each, settings of 19 September):
  M1  mode-token Transformer, per-mode target (learning_curve_layerA.RegTransformer on the descriptor tokens of the second pass);
  M2  the module's ΔH model with the block target (deltah_model.DeltaHModel, block loss, 30 epochs, batches of 8, no pair head);
  M3  E5b-tok  (token MLP encoder + symmetric bilinear form on K, balanced loss);
  M4  E5b-atoms (atom-set encoder + bilinear form, balanced loss);
  M5  baselines: zero rule, family-median rule (diagonal), ridge probe of the descriptor tokens.

Read-outs per model, size and hold-out: diagonal RMS per family; ring-in-plane coupling RMS and its ratio to the zero rule; ring block
trace RMS against the training-median rule; then the power-law slope of log RMS vs log n, the first n at which the ring coupling ratio
drops below 1.0 and 0.7, the first n at which the ring block beats the median rule, and the scaffold gap (b) − (a) on the ring block.

Usage: python e6_learning_curve.py <corpus/molecules dir> <out prefix> [--threads 16] [--sizes 45,100,all] [--m1-epochs 600]
       [--e5-steps 1500] [--m2-epochs 30] [--smoke]      (--smoke: two sizes, one seed, a few steps — a pipeline check, never a result)
"""
import argparse
import hashlib
import json
import math
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

sys.path.insert(0, str(Path(__file__).resolve().parent))
import embedding_experiments_E as EE  # noqa: E402
import embedding_skipgram_E5 as E5  # noqa: E402
from deltah_model import DeltaHConfig, DeltaHModel, block_loss  # noqa: E402
from embedding_experiments_E import atom_sets, probe  # noqa: E402

EE.NMAX = 32   # the E-series constant (28) was layer A's largest molecule; A2 reaches 30 atoms
from learning_curve_layerA import FAMILIES, molecule_features, predict, rms, train  # noqa: E402
from learning_curve_layerA_v2_descriptors import environment_tokens  # noqa: E402

RING = "ring-ip"
SEEDS = [0, 1, 2]


def sha(s):
    return hashlib.sha1(s.encode()).hexdigest()


# ----------------------------------------------------------------------------------------------------------------------- data
def load_corpus(mdir):
    import csv
    names = {}
    if (mdir.parent / "manifest.csv").exists():
        with open(mdir.parent / "manifest.csv", newline="", encoding="utf-8") as f:
            names = {r["id"]: r["name"] for r in csv.DictReader(f)}
    mols = {}
    for d in sorted(p for p in mdir.iterdir() if (p / "hessian_wb97x.npz").exists() and (p / "hessian_b3lyp.npz").exists()):
        try:
            base = molecule_features(d)
            tokB, _, _ = environment_tokens(d, base)
            r = json.load(open(d / "result.json")) if (d / "result.json").exists() else {}
            mols[d.name] = dict(base, tokens=tokB.astype(np.float32), K=E5.coupling_matrix(d), sets=atom_sets(d, base),
                                layer=r.get("layer", "A2" if d.name.startswith("A2_") else "A"),
                                core=names.get(d.name, d.name).split("+")[0],
                                imaginary=bool(r.get("n_imaginary_b3lyp", 0) or r.get("n_imaginary_wb97x", 0)))
        except Exception as e:  # noqa: BLE001 — a broken molecule is reported and skipped, as in the E-series
            print("skip", d.name, repr(e), flush=True)
    return mols


def splits(mols):
    ids_A = sorted((i for i, m in mols.items() if m["layer"] == "A"), key=sha)
    n_a = max(1, math.ceil(0.25 * len(ids_A)))
    test_a = ids_A[:n_a]
    cores = sorted({m["core"] for m in mols.values() if m["layer"] == "A2"}, key=sha)
    scaffold_cores = cores[:2]
    test_b = sorted(i for i, m in mols.items() if m["layer"] == "A2" and m["core"] in scaffold_cores)
    held = set(test_a) | set(test_b)
    pool = sorted((i for i in mols if i not in held), key=sha)
    return test_a, test_b, scaffold_cores, pool


# ----------------------------------------------------------------------------------------------------------------- read-outs
def readout(P, mols, ids, train_ids):
    """P: dict id -> predicted (M, M) matrix (only the diagonal and same-family pairs are read). Returns the E5 read-outs."""
    diag = {F: [] for F in FAMILIES}; cerr, czero, bp, bt = [], [], [], []
    for i in ids:
        T = mols[i]["K"]; fam = np.array(mols[i]["family"]); Pi = P[i]
        for F in FAMILIES:
            diag[F].append((np.diag(Pi) - np.diag(T))[fam == F])
        r = np.where(fam == RING)[0]
        if len(r) > 1:
            iu = np.triu_indices(len(r), 1)
            cerr.append((Pi[np.ix_(r, r)] - T[np.ix_(r, r)])[iu]); czero.append(T[np.ix_(r, r)][iu])
            bp.append(np.trace(Pi[np.ix_(r, r)]) / len(r)); bt.append(np.trace(T[np.ix_(r, r)]) / len(r))
    med = float(np.median([block_trace(mols[i]) for i in train_ids if block_trace(mols[i]) is not None]))
    out = {"diag_rms": {F: rms(np.concatenate(diag[F])) if diag[F] else float("nan") for F in FAMILIES},
           "coupling_rms": rms(np.concatenate(cerr)) if cerr else float("nan"),
           "coupling_zero_rms": rms(np.concatenate(czero)) if czero else float("nan"),
           "block_rms": rms(np.array(bp) - np.array(bt)) if bp else float("nan"),
           "block_median_rule_rms": rms(np.array(bt) - med) if bt else float("nan")}
    out["coupling_ratio"] = out["coupling_rms"] / out["coupling_zero_rms"] if out["coupling_zero_rms"] else float("nan")
    return out


def block_trace(m):
    r = np.where(np.array(m["family"]) == RING)[0]
    return float(np.trace(m["K"][np.ix_(r, r)]) / len(r)) if len(r) else None


def diag_only(preds, mols, ids):
    """M1 / M5: predictions of the diagonal only -> the same record with the coupling fields absent."""
    diag = {F: [] for F in FAMILIES}
    for i, p in zip(ids, preds):
        fam = np.array(mols[i]["family"])
        for F in FAMILIES:
            diag[F].append((p - mols[i]["target"])[fam == F])
    return {"diag_rms": {F: rms(np.concatenate(diag[F])) if diag[F] else float("nan") for F in FAMILIES}}


def mean_records(recs):
    out = {}
    for k in recs[0]:
        if isinstance(recs[0][k], dict):
            out[k] = {F: float(np.nanmean([r[k][F] for r in recs])) for F in recs[0][k]}
        else:
            out[k] = float(np.nanmean([r[k] for r in recs]))
    return out


# -------------------------------------------------------------------------------------------------------------------- models
def run_m1(mols, tr, tests, seed, epochs):
    model, scale = train([mols[i] for i in tr], seed, epochs)
    return {name: diag_only(predict(model, scale, [mols[i] for i in ids]), mols, ids) for name, ids in tests.items()}


def pad_block(mols, ids):
    M = max(len(mols[i]["target"]) for i in ids); d = mols[ids[0]]["tokens"].shape[1]
    X = np.zeros((len(ids), M, d), np.float32); K = np.zeros((len(ids), M, M), np.float32)
    fam = np.zeros((len(ids), M), np.int64); mask = np.zeros((len(ids), M), bool); om = np.zeros((len(ids), M), np.float32)
    for b, i in enumerate(ids):
        n = len(mols[i]["target"]); X[b, :n] = mols[i]["tokens"]; K[b, :n, :n] = mols[i]["K"]; mask[b, :n] = True
        fam[b, :n] = [FAMILIES.index(f) for f in mols[i]["family"]]; om[b, :n] = mols[i]["freq"]
    t = lambda a: torch.tensor(a)  # noqa: E731
    return dict(tokens=t(X), K=t(K), family=t(fam), mask=t(mask), omega=t(om),
                charge=torch.zeros(len(ids), dtype=torch.long), mult=torch.ones(len(ids), dtype=torch.long))


def run_m2(mols, tr, tests, seed, epochs, bs=8):
    torch.manual_seed(seed); rng = np.random.default_rng(seed)
    cfg = DeltaHConfig(n_families=4, n_irreps=0, n_env=13, n_layers=2)
    m = DeltaHModel(cfg); opt = torch.optim.AdamW(m.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay)
    T = pad_block(mols, tr)
    for _ in range(epochs):
        m.train(); order = rng.permutation(len(tr))
        for s in range(0, len(tr), bs):
            b = torch.tensor(order[s:s + bs])
            out = m(T["tokens"][b], T["family"][b], T["charge"][b], T["mult"][b], T["mask"][b])
            loss = block_loss(out["block"], T["K"][b], T["family"][b], T["mask"][b])
            opt.zero_grad(); loss.backward(); nn.utils.clip_grad_norm_(m.parameters(), 1.0); opt.step()
    m.eval(); res = {}
    with torch.no_grad():
        for name, ids in tests.items():
            Tt = pad_block(mols, ids)
            B = m(Tt["tokens"], Tt["family"], Tt["charge"], Tt["mult"], Tt["mask"])["block"].numpy()
            P = {i: B[b, :len(mols[i]["target"]), :len(mols[i]["target"])] for b, i in enumerate(ids)}
            res[name] = readout(P, mols, ids, tr)
    return res


def run_e5(mols, tr, tests, seed, steps, atoms):
    E5.BALANCED = True
    K = {i: mols[i]["K"] for i in mols}

    def enc_tok(enc, i):
        return enc(torch.tensor(mols[i]["tokens"]))

    def enc_atoms(enc, i):
        X, Mk = mols[i]["sets"]; return enc(torch.tensor(X), torch.tensor(Mk))

    encode = enc_atoms if atoms else enc_tok
    enc, bil, hp, scale = E5.train_e5(encode, tr, K, steps, seed, d_in=mols[tr[0]]["tokens"].shape[1], atoms=atoms)
    res = {}
    with torch.no_grad():
        for name, ids in tests.items():
            P = {i: (bil(hp(encode(enc, i))) * scale).numpy() for i in ids}
            res[name] = readout(P, mols, ids, tr)
    return res


def run_baselines(mols, tr, tests):
    med = {}
    for F in FAMILIES:
        vals = np.concatenate([mols[i]["target"][np.array(mols[i]["family"]) == F] for i in tr])
        med[F] = float(np.median(vals)) if vals.size else 0.0
    res = {}
    feat = {i: mols[i]["tokens"] for i in mols}
    for name, ids in tests.items():
        zero = diag_only([np.zeros_like(mols[i]["target"]) for i in ids], mols, ids)
        fm = diag_only([np.array([med[f] for f in mols[i]["family"]], np.float32) for i in ids], mols, ids)
        # zero-rule couplings and the median rule for the ring block come from readout with P = 0
        z = readout({i: np.zeros_like(mols[i]["K"]) for i in ids}, mols, ids, tr)
        pr = probe(feat, mols, tr, ids, f"ridge probe n={len(tr)} [{name}]")
        res[name] = {"zero": {"diag_rms": zero["diag_rms"], "coupling_zero_rms": z["coupling_zero_rms"], "block_median_rule_rms": z["block_median_rule_rms"]},
                     "family-median": fm, "ridge": {"diag_rms": {F: pr[F] for F in FAMILIES}, "lambda": pr["lambda"]}}
    return res


# ---------------------------------------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("molecules"); ap.add_argument("out_prefix")
    ap.add_argument("--threads", type=int, default=16)
    ap.add_argument("--sizes", default="45,100,all")
    ap.add_argument("--m1-epochs", type=int, default=600); ap.add_argument("--e5-steps", type=int, default=1500); ap.add_argument("--m2-epochs", type=int, default=30)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--exclude-imaginary", action="store_true",
                    help="drop molecules with an imaginary mode (the module-05 release rule); 23 Sep: the first-order target on an imaginary mode is ill-defined "
                         "and the per-mode model's 'other' family on hold-out (a) was dominated by one such molecule (A_b90527ca2d, mode -37 cm-1, prediction +394)")
    a = ap.parse_args(); torch.set_num_threads(a.threads)
    t_start = time.time()
    mols = load_corpus(Path(a.molecules))
    test_a, test_b, scaffold_cores, pool = splits(mols)     # the split is fixed on the full set, so hold-out (a) stays the 19 Sep set
    if a.exclude_imaginary:
        dropped = sorted(i for i, m in mols.items() if m["imaginary"])
        mols = {i: m for i, m in mols.items() if not m["imaginary"]}
        test_a = [i for i in test_a if i in mols]; test_b = [i for i in test_b if i in mols]; pool = [i for i in pool if i in mols]
        print(f"excluded {len(dropped)} molecules with an imaginary mode (after the split): {dropped}", flush=True)
    sizes = [int(s) if s != "all" else len(pool) for s in a.sizes.split(",")]
    sizes = sorted({min(s, len(pool)) for s in sizes})
    seeds = SEEDS
    if a.smoke:
        sizes, seeds, a.m1_epochs, a.e5_steps, a.m2_epochs = sizes[:2], [0], 5, 5, 1
    n_layers = {L: sum(m["layer"] == L for m in mols.values()) for L in ("A", "A2")}
    print(f"{len(mols)} molecules {n_layers}; hold-out (a) {len(test_a)} layer-A molecules; scaffold cores {scaffold_cores} -> hold-out (b) "
          f"{len(test_b)} molecules; pool {len(pool)}; sizes {sizes}; seeds {seeds}; smoke {a.smoke}", flush=True)
    res = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "smoke": a.smoke, "n_molecules": len(mols), "layers": n_layers,
           "imaginary_included": int(sum(m["imaginary"] for m in mols.values())),
           "holdout_a": test_a, "scaffold_cores": scaffold_cores, "holdout_b": test_b, "pool": len(pool), "sizes": sizes, "seeds": seeds,
           "settings": {"m1_epochs": a.m1_epochs, "e5_steps": a.e5_steps, "m2_epochs": a.m2_epochs}, "curve": {}}
    json.dump(res, open(a.out_prefix + ".json", "w"), indent=1)   # the hold-out choice is on disk before any training
    tests = {"a": test_a, "b": test_b}
    for n in sizes:
        tr = pool[:n]; row = {"n": n, "baselines": run_baselines(mols, tr, tests)}
        for label, fn in (("M1", lambda s: run_m1(mols, tr, tests, s, a.m1_epochs)),
                          ("M2", lambda s: run_m2(mols, tr, tests, s, a.m2_epochs)),
                          ("M3", lambda s: run_e5(mols, tr, tests, s, a.e5_steps, atoms=False)),
                          ("M4", lambda s: run_e5(mols, tr, tests, s, a.e5_steps, atoms=True))):
            t0 = time.time(); per_seed = [fn(s) for s in seeds]
            row[label] = {"per_seed": per_seed, "mean": {h: mean_records([p[h] for p in per_seed]) for h in tests}, "seconds": round(time.time() - t0)}
            ma = row[label]["mean"]["a"]
            line = f"n={n:3d} {label}: (a) diag " + " ".join(f"{F} {ma['diag_rms'][F]:6.2f} |" for F in FAMILIES)
            if "coupling_ratio" in ma:
                line += f" ring couplings ratio {ma['coupling_ratio']:.2f} | block {ma['block_rms']:.2f} vs median {ma['block_median_rule_rms']:.2f}"
                mb = row[label]["mean"]["b"]; line += f" || (b) ring diag {mb['diag_rms'][RING]:.2f} ratio {mb['coupling_ratio']:.2f} block {mb['block_rms']:.2f} vs median {mb['block_median_rule_rms']:.2f}"
            print(line + f"  [{row[label]['seconds']} s]", flush=True)
        res["curve"][str(n)] = row
        json.dump(res, open(a.out_prefix + ".json", "w"), indent=1)
    # ---- readings
    ln = np.log(sizes)
    slope = lambda ys: float(np.polyfit(ln, np.log(np.maximum(ys, 1e-6)), 1)[0]) if len(sizes) >= 2 else float("nan")  # noqa: E731
    readings = {"slopes": {}, "crossings": {}, "scaffold_gap_block_b_minus_a": {}}
    for label in ("M1", "M2", "M3", "M4"):
        readings["slopes"][label] = {"diag": {F: slope([res["curve"][str(n)][label]["mean"]["a"]["diag_rms"][F] for n in sizes]) for F in FAMILIES}}
        if label != "M1":
            ratios = [res["curve"][str(n)][label]["mean"]["a"]["coupling_ratio"] for n in sizes]
            blocks = [(res["curve"][str(n)][label]["mean"]["a"]["block_rms"], res["curve"][str(n)][label]["mean"]["a"]["block_median_rule_rms"]) for n in sizes]
            readings["slopes"][label]["coupling_ratio"] = slope(ratios)
            readings["crossings"][label] = {"ratio<1.0": next((n for n, r in zip(sizes, ratios) if r < 1.0), None),
                                            "ratio<0.7": next((n for n, r in zip(sizes, ratios) if r < 0.7), None),
                                            "block<median": next((n for n, (b, m) in zip(sizes, blocks) if b < m), None)}
            readings["scaffold_gap_block_b_minus_a"][label] = {str(n): res["curve"][str(n)][label]["mean"]["b"]["block_rms"] - res["curve"][str(n)][label]["mean"]["a"]["block_rms"] for n in sizes}
    res["readings"] = readings; res["seconds_total"] = round(time.time() - t_start)
    json.dump(res, open(a.out_prefix + ".json", "w"), indent=1)
    # ---- markdown
    md = [f"# E6 — learning curve in data ({res['date']}){' — SMOKE, NOT A RESULT' if a.smoke else ''}", "",
          f"{len(mols)} molecules (A {n_layers['A']}, A2 {n_layers['A2']}; {res['imaginary_included']} with an imaginary mode kept, as on 19 Sep). Hold-out (a): the "
          f"{len(test_a)} layer-A molecules of 19 Sep. Hold-out (b): scaffold cores {scaffold_cores} ({len(test_b)} molecules). Pool {len(pool)}; sizes {sizes}; seeds {seeds}; "
          f"M1 {a.m1_epochs} steps, M2 {a.m2_epochs} epochs, E5 {a.e5_steps} steps. Held-out RMS in cm⁻¹, mean over seeds.", "",
          "## Hold-out (a): the 12 layer-A molecules", "",
          "| n | model | " + " | ".join(f"diag {F}" for F in FAMILIES) + " | ring coupling RMS / zero | ratio | ring block RMS / median rule |", "|---|---|" + "---|" * (len(FAMILIES) + 3)]
    for h, title in (("a", None), ("b", "## Hold-out (b): the scaffold cores")):
        if title:
            md += ["", title, "", md[6], md[7]]
        for n in sizes:
            row = res["curve"][str(n)]; bl = row["baselines"][h]
            md.append(f"| {n} | zero rule | " + " | ".join(f"{bl['zero']['diag_rms'][F]:.2f}" for F in FAMILIES) + f" | — / {bl['zero']['coupling_zero_rms']:.2f} | 1.00 | — / {bl['zero']['block_median_rule_rms']:.2f} |")
            md.append(f"| {n} | family median | " + " | ".join(f"{bl['family-median']['diag_rms'][F]:.2f}" for F in FAMILIES) + " | | | |")
            md.append(f"| {n} | ridge probe | " + " | ".join(f"{bl['ridge']['diag_rms'][F]:.2f}" for F in FAMILIES) + " | | | |")
            for label in ("M1", "M2", "M3", "M4"):
                m = row[label]["mean"][h]
                cells = " | ".join(f"{m['diag_rms'][F]:.2f}" for F in FAMILIES)
                if "coupling_ratio" in m:
                    md.append(f"| {n} | {label} | {cells} | {m['coupling_rms']:.2f} / {m['coupling_zero_rms']:.2f} | {m['coupling_ratio']:.2f} | {m['block_rms']:.2f} / {m['block_median_rule_rms']:.2f} |")
                else:
                    md.append(f"| {n} | {label} | {cells} | | | |")
    md += ["", "## Readings (pre-registered)", ""]
    for label, s in readings["slopes"].items():
        md.append(f"- {label} slopes of log RMS vs log n: diag " + ", ".join(f"{F} {s['diag'][F]:+.2f}" for F in FAMILIES)
                  + (f"; ring coupling ratio {s['coupling_ratio']:+.2f}" if "coupling_ratio" in s else ""))
    for label, c in readings["crossings"].items():
        md.append(f"- {label} crossings: ratio < 1.0 at n = {c['ratio<1.0']}, < 0.7 at n = {c['ratio<0.7']}, ring block beats the median rule at n = {c['block<median']}")
    for label, g in readings["scaffold_gap_block_b_minus_a"].items():
        md.append(f"- {label} scaffold gap on the ring block, (b) − (a): " + ", ".join(f"n={n} {v:+.2f}" for n, v in g.items()))
    md += ["", f"Total {res['seconds_total']} s. M1 = per-mode Transformer; M2 = ΔH block model; M3 = E5b-tok; M4 = E5b-atoms."]
    open(a.out_prefix + ".md", "w", encoding="utf-8").write("\n".join(md) + "\n")
    print("wrote", a.out_prefix + ".json/.md", f"in {res['seconds_total']} s", flush=True)


if __name__ == "__main__":
    main()
