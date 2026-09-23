"""E7 / T1 — the sign test (pre-registered 23 September 2026, PreRegistration_2026-09-23_E7_Couplings_in_Local_Coordinates.md).

Hypothesis: the mode tokens are invariant under L_i -> -L_i while the coupling K_ij is odd under it, so any model on those tokens has its
MSE optimum at K_ij = 0 (E6: ratio 1.00 at every n). If that is the obstacle, the same model trained on |K_ij| (diagonal unchanged) must
beat the best constant on the magnitudes.

Model and data exactly as E6's M2 (module-05 DeltaHModel, block loss, 30 epochs, batches of 8, seeds 0 1 2), hold-outs (a) and (b) of E6,
imaginary-mode molecules excluded after the split. Read-out on the ring-in-plane pairs of each hold-out: RMS of the model on |K| against the
zero rule (RMS |K|) and against the constant rule (mean |K| of the training ring pairs); the signed-K model at the same n is trained too,
as the paired control.

Usage: python e7_t1_sign_test.py <corpus/molecules dir> <out prefix> [--threads 16] [--sizes 45,all] [--epochs 30] [--smoke]
"""
import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import e6_learning_curve as E6  # noqa: E402
from learning_curve_layerA import FAMILIES, rms  # noqa: E402

RING = "ring-ip"


def abs_offdiag(mols):
    out = {}
    for i, m in mols.items():
        K = m["K"].copy(); d = np.diag(K).copy()
        K = np.abs(K); np.fill_diagonal(K, d)
        out[i] = dict(m, K=K, K_signed=m["K"])
    return out


def ring_pairs(m):
    r = np.where(np.array(m["family"]) == RING)[0]
    if len(r) < 2:
        return None
    iu = np.triu_indices(len(r), 1)
    return r, iu


def readout_abs(P, mols_abs, ids, const):
    """P: predicted (M, M) per molecule on the |K| target. Returns ring coupling RMS of the model, of zero and of the constant rule, plus the diagonal per family."""
    err, zero, cst, diag = [], [], [], {F: [] for F in FAMILIES}
    for i in ids:
        m = mols_abs[i]; T = m["K"]; Pi = P[i]; fam = np.array(m["family"])
        for F in FAMILIES:
            diag[F].append((np.diag(Pi) - np.diag(T))[fam == F])
        rp = ring_pairs(m)
        if rp is None:
            continue
        r, iu = rp; t = T[np.ix_(r, r)][iu]; p = Pi[np.ix_(r, r)][iu]
        err.append(p - t); zero.append(t); cst.append(t - const)
    e, z, c = (np.concatenate(x) if x else np.array([np.nan]) for x in (err, zero, cst))
    return {"diag_rms": {F: rms(np.concatenate(diag[F])) for F in FAMILIES}, "coupling_rms": rms(e), "zero_rms": rms(z), "const_rms": rms(c),
            "ratio_to_zero": rms(e) / rms(z), "ratio_to_const": rms(e) / rms(c), "const": const}


def train_m2(mols, tr, seed, epochs, bs=8):
    from deltah_model import DeltaHConfig, DeltaHModel, block_loss
    import torch.nn as nn
    torch.manual_seed(seed); rng = np.random.default_rng(seed)
    cfg = DeltaHConfig(n_families=4, n_irreps=0, n_env=13, n_layers=2)
    m = DeltaHModel(cfg); opt = torch.optim.AdamW(m.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay)
    T = E6.pad_block(mols, tr)
    for _ in range(epochs):
        m.train(); order = rng.permutation(len(tr))
        for s in range(0, len(tr), bs):
            b = torch.tensor(order[s:s + bs])
            out = m(T["tokens"][b], T["family"][b], T["charge"][b], T["mult"][b], T["mask"][b])
            loss = block_loss(out["block"], T["K"][b], T["family"][b], T["mask"][b])
            opt.zero_grad(); loss.backward(); nn.utils.clip_grad_norm_(m.parameters(), 1.0); opt.step()
    m.eval(); return m


def predict(m, mols, ids):
    with torch.no_grad():
        Tt = E6.pad_block(mols, ids)
        B = m(Tt["tokens"], Tt["family"], Tt["charge"], Tt["mult"], Tt["mask"])["block"].numpy()
    return {i: B[b, :len(mols[i]["target"]), :len(mols[i]["target"])] for b, i in enumerate(ids)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("molecules"); ap.add_argument("out_prefix")
    ap.add_argument("--threads", type=int, default=16); ap.add_argument("--sizes", default="45,all"); ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args(); torch.set_num_threads(a.threads); t0 = time.time()
    mols = E6.load_corpus(Path(a.molecules))
    test_a, test_b, cores, pool = E6.splits(mols)
    mols = {i: m for i, m in mols.items() if not m["imaginary"]}
    test_a = [i for i in test_a if i in mols]; test_b = [i for i in test_b if i in mols]; pool = [i for i in pool if i in mols]
    sizes = sorted({min(int(s) if s != "all" else len(pool), len(pool)) for s in a.sizes.split(",")})
    seeds = [0, 1, 2]
    if a.smoke:
        sizes, seeds, a.epochs = sizes[:1], [0], 1
    mols_abs = abs_offdiag(mols)
    tests = {"a": test_a, "b": test_b}
    print(f"{len(mols)} molecules; hold-out (a) {len(test_a)}, (b) {len(test_b)} ({cores}); pool {len(pool)}; sizes {sizes}; seeds {seeds}; epochs {a.epochs}", flush=True)
    res = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "smoke": a.smoke, "n_molecules": len(mols), "holdout_a": test_a, "holdout_b": test_b,
           "scaffold_cores": cores, "pool": len(pool), "sizes": sizes, "seeds": seeds, "epochs": a.epochs, "curve": {}}
    for n in sizes:
        tr = pool[:n]
        const = float(np.mean(np.concatenate([mols_abs[i]["K"][np.ix_(*[ring_pairs(mols_abs[i])[0]] * 2)][ring_pairs(mols_abs[i])[1]]
                                               for i in tr if ring_pairs(mols_abs[i]) is not None])))
        row = {"n": n, "const_abs_ring": const, "abs": {"per_seed": []}, "signed": {"per_seed": []}}
        for seed in seeds:
            m_abs = train_m2(mols_abs, tr, seed, a.epochs)
            row["abs"]["per_seed"].append({h: readout_abs(predict(m_abs, mols_abs, ids), mols_abs, ids, const) for h, ids in tests.items()})
            m_sg = train_m2(mols, tr, seed, a.epochs)
            row["signed"]["per_seed"].append({h: E6.readout(predict(m_sg, mols, ids), mols, ids, tr) for h, ids in tests.items()})
        for kind in ("abs", "signed"):
            row[kind]["mean"] = {h: E6.mean_records([p[h] for p in row[kind]["per_seed"]]) for h in tests}
        ma, ms = row["abs"]["mean"]["a"], row["signed"]["mean"]["a"]
        print(f"n={n:3d} |K| model: ring coupling RMS {ma['coupling_rms']:.2f} vs zero {ma['zero_rms']:.2f} (ratio {ma['ratio_to_zero']:.2f}) vs constant {ma['const_rms']:.2f} "
              f"(ratio {ma['ratio_to_const']:.2f}; c = {const:.2f}) | diag ring {ma['diag_rms'][RING]:.2f} || signed control: ratio {ms['coupling_ratio']:.2f}, diag ring {ms['diag_rms'][RING]:.2f} "
              f"|| (b) |K| ratio to constant {row['abs']['mean']['b']['ratio_to_const']:.2f}  [{time.time() - t0:.0f} s]", flush=True)
        res["curve"][str(n)] = row
        json.dump(res, open(a.out_prefix + ".json", "w"), indent=1)
    nfull = str(sizes[-1]); r = res["curve"][nfull]["abs"]["mean"]["a"]["ratio_to_const"]
    verdict = "WIN (ratio to the constant rule ≤ 0.85)" if r <= 0.85 else ("LOSE (≥ 0.95)" if r >= 0.95 else "between")
    res["verdict"] = {"ratio_to_const_a_full": r, "verdict": verdict}; res["seconds"] = round(time.time() - t0)
    json.dump(res, open(a.out_prefix + ".json", "w"), indent=1)
    md = [f"# E7 / T1 — the sign test ({res['date']}){' — SMOKE, NOT A RESULT' if a.smoke else ''}", "",
          f"{len(mols)} molecules (imaginary-mode molecules excluded after the E6 split); hold-out (a) {len(test_a)} layer-A molecules, (b) scaffold cores {cores} ({len(test_b)}); "
          f"pool {len(pool)}; seeds {seeds}; {a.epochs} epochs. Ring-in-plane pairs; RMS in cm⁻¹, mean over seeds.", "",
          "| n | hold-out | |K| model RMS | zero rule | constant rule (c) | ratio to zero | ratio to constant | signed control ratio | diag ring: |K| model / signed |",
          "|---|---|---|---|---|---|---|---|---|"]
    for n in sizes:
        row = res["curve"][str(n)]
        for h in ("a", "b"):
            ma, ms = row["abs"]["mean"][h], row["signed"]["mean"][h]
            md.append(f"| {n} | ({h}) | {ma['coupling_rms']:.2f} | {ma['zero_rms']:.2f} | {ma['const_rms']:.2f} ({row['const_abs_ring']:.2f}) | {ma['ratio_to_zero']:.2f} | **{ma['ratio_to_const']:.2f}** | {ms['coupling_ratio']:.2f} | {ma['diag_rms'][RING]:.2f} / {ms['diag_rms'][RING]:.2f} |")
    md += ["", f"**Verdict (pre-registered, hold-out (a) at n = {nfull}):** ratio to the constant rule {r:.2f} → {verdict}.", "", f"Total {res['seconds']} s."]
    open(a.out_prefix + ".md", "w", encoding="utf-8").write("\n".join(md) + "\n")
    print("wrote", a.out_prefix + ".json/.md", flush=True)


if __name__ == "__main__":
    main()
