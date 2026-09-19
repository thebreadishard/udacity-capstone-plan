"""E5 — the word-embedding analogy taken literally (19 September 2026; pre-registered as E5 in
PreRegistration_2026-09-19_E_Series_Learned_Mode_Embeddings.md).

word2vec: a word's vector is learned by predicting its context; skip-gram ≈ implicit factorisation of the word–context
co-occurrence matrix (u_wᵀ v_c ≈ PMI). Here: a molecule is the sentence, its modes the words, and a mode's context is its
coupling row under the correction, K_ij = L_iᵀ ΔH L_j / (2 √(ω_i ω_j)) in cm⁻¹ (mode-basis correction matrix; diagonal =
the per-mode first-order shift). An encoder e(mode) → ℝ³² and a learned symmetric bilinear form W are trained so that
e_iᵀ W e_j ≈ K_ij over ALL pairs of every training molecule (diagonal included; zero pairs are the negatives).

Two encoders: E5-tok (first-pass tokens + environment tokens → MLP), E5-atoms (raw atom set → the E1 encoder).
Read-outs on the 12 held-out molecules: (a) diagonal per family; (b) within-family ring couplings vs the zero rule;
(c) ring family block trace vs the median rule; (d) ridge probe of the frozen embedding to the first-order shift.
Usage: python embedding_skipgram_E5.py <corpus/molecules dir> <out prefix> [--steps 1500] [--threads 1]
"""
import argparse
import hashlib
import json
import math
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

sys.path.insert(0, str(Path(__file__).resolve().parent))
from learning_curve_layerA import AMU2AU, FAMILIES, HARTREE2CM, molecule_features, normal_modes  # noqa: E402
from learning_curve_layerA_v2_descriptors import environment_tokens  # noqa: E402
from embedding_experiments_E import AtomSetEncoder, atom_sets, probe, rms  # noqa: E402

RING = "ring-ip"


def coupling_matrix(mol_dir):
    g = json.load(open(mol_dir / "geometry.json")); masses = np.asarray(g["masses_amu"])
    lo = np.load(mol_dir / "hessian_b3lyp.npz"); hi = np.load(mol_dir / "hessian_wb97x.npz")
    w, f, V, _ = normal_modes(lo["H_projected"], masses)
    m = np.repeat(masses * AMU2AU, 3)
    dH = hi["H_projected"] / np.sqrt(np.outer(m, m)) - lo["H_projected"] / np.sqrt(np.outer(m, m))
    Km = V.T @ dH @ V
    om = np.sqrt(np.abs(w))
    return (Km / (2 * np.sqrt(np.outer(om, om))) * HARTREE2CM).astype(np.float32)   # (M, M), diag = first-order shift


class TokenEncoder(nn.Module):
    def __init__(self, d_in, d=64, d_emb=32):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(d_in, d), nn.GELU(), nn.Linear(d, d), nn.GELU(), nn.Linear(d, d_emb))

    def forward(self, x, mask=None):
        return self.net(x)


class Bilinear(nn.Module):
    def __init__(self, d_emb=32):
        super().__init__()
        self.A = nn.Parameter(torch.randn(d_emb, d_emb) / d_emb)
        self.bias = nn.Parameter(torch.zeros(1))

    def W(self):
        return 0.5 * (self.A + self.A.T)

    def forward(self, E):                       # E (M, d) -> (M, M)
        return E @ self.W() @ E.T + self.bias


def train_e5(encode_batch, mol_ids, K, steps, seed, scale=50.0, d_in=None, atoms=False, lr=1e-3):
    torch.manual_seed(seed); rng = np.random.default_rng(seed)
    enc = AtomSetEncoder(d_emb=32) if atoms else TokenEncoder(d_in)
    head_proj = (lambda e: enc.proj(e)) if atoms else (lambda e: e)
    bil = Bilinear(32)
    opt = torch.optim.AdamW(list(enc.parameters()) + list(bil.parameters()), lr=lr, weight_decay=1e-4)
    for step in range(steps):
        ids = rng.choice(mol_ids, size=min(8, len(mol_ids)), replace=False)
        loss = 0.0
        for i in ids:
            E = head_proj(encode_batch(enc, i))
            pred = bil(E)
            tgt = torch.tensor(K[i] / scale)
            loss = loss + ((pred - tgt) ** 2).mean()
        loss = loss / len(ids)
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 500 == 0 or step == steps - 1:
            print(f"    E5 {'atoms' if atoms else 'tok'} seed {seed} step {step} loss {loss.item():.4f}", flush=True)
    enc.eval(); return enc, bil, head_proj, scale


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("molecules"); ap.add_argument("out_prefix")
    ap.add_argument("--steps", type=int, default=1500); ap.add_argument("--threads", type=int, default=1)
    a = ap.parse_args(); torch.set_num_threads(a.threads)
    mdir = Path(a.molecules)
    mols, K, tok, sets = {}, {}, {}, {}
    for d in sorted(p for p in mdir.iterdir() if (p / "hessian_wb97x.npz").exists()):
        try:
            base = molecule_features(d); mols[d.name] = base
            K[d.name] = coupling_matrix(d)
            tokB, _, _ = environment_tokens(d, base); tok[d.name] = tokB.astype(np.float32)
            sets[d.name] = atom_sets(d, base)
        except Exception as e:
            print("skip", d.name, repr(e))
    ids = sorted(mols, key=lambda i: hashlib.sha1(i.encode()).hexdigest())
    n_test = max(1, math.ceil(0.25 * len(ids))); test_ids, pool = ids[:n_test], ids[n_test:]
    train_ids = pool[:30]
    # sanity: K diagonal equals the first-order target
    dev = max(float(np.abs(np.diag(K[i]) - mols[i]["target"]).max()) for i in ids)
    n_pairs = sum(len(mols[i]["target"]) * (len(mols[i]["target"]) - 1) // 2 for i in train_ids)
    print(f"{len(ids)} molecules, {n_test} held out, {len(train_ids)} training; diag(K) vs target max dev {dev:.2e}; training pairs {n_pairs}", flush=True)
    res = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "n_train": len(train_ids), "n_test": n_test, "steps": a.steps, "training_pairs": n_pairs}

    def enc_tok(enc, i):
        return enc(torch.tensor(tok[i]))

    def enc_atoms(enc, i):
        X, Mk = sets[i]; return enc(torch.tensor(X), torch.tensor(Mk))

    for label, atoms, encode in (("tok", False, enc_tok), ("atoms", True, enc_atoms)):
        print(f"E5-{label}", flush=True)
        per_seed = []
        for s in (0, 1, 2):
            enc, bil, hp, scale = train_e5(encode, train_ids, K, a.steps, s, d_in=tok[ids[0]].shape[1], atoms=atoms)
            out = {"diag": {F: [] for F in FAMILIES}, "coup_err": [], "coup_zero": [], "block_pred": [], "block_true": [], "block_med": []}
            emb = {}
            with torch.no_grad():
                for i in ids:
                    E = hp(encode(enc, i)); emb[i] = E.numpy()
                    if i not in test_ids: continue
                    P = (bil(E) * scale).numpy(); T = K[i]; fam = np.array(mols[i]["family"])
                    for F in FAMILIES:
                        out["diag"][F].append((np.diag(P) - np.diag(T))[fam == F])
                    r = np.where(fam == RING)[0]
                    if len(r) > 1:
                        iu = np.triu_indices(len(r), 1)
                        out["coup_err"].append((P[np.ix_(r, r)] - T[np.ix_(r, r)])[iu]); out["coup_zero"].append(T[np.ix_(r, r)][iu])
                        out["block_pred"].append(np.trace(P[np.ix_(r, r)]) / len(r)); out["block_true"].append(np.trace(T[np.ix_(r, r)]) / len(r))
            med = float(np.median([np.trace(K[i][np.ix_(np.where(np.array(mols[i]["family"]) == RING)[0], np.where(np.array(mols[i]["family"]) == RING)[0])]) /
                                   max(1, (np.array(mols[i]["family"]) == RING).sum()) for i in train_ids]))
            rec = {"diag_rms": {F: rms(np.concatenate(out["diag"][F])) for F in FAMILIES},
                   "coupling_rms": rms(np.concatenate(out["coup_err"])), "coupling_zero_rms": rms(np.concatenate(out["coup_zero"])),
                   "block_rms": rms(np.array(out["block_pred"]) - np.array(out["block_true"])),
                   "block_median_rule_rms": rms(np.array(out["block_true"]) - med)}
            rec["coupling_ratio"] = rec["coupling_rms"] / rec["coupling_zero_rms"]
            rec["probe"] = probe(emb, mols, train_ids, test_ids, f"E5-{label} seed {s} embedding probe n=30")
            print(f"  E5-{label} seed {s}: diag " + " ".join(f"{F} {rec['diag_rms'][F]:6.2f} |" for F in FAMILIES)
                  + f" ring couplings {rec['coupling_rms']:.2f} vs zero {rec['coupling_zero_rms']:.2f} (ratio {rec['coupling_ratio']:.2f}) | ring block {rec['block_rms']:.2f} vs median {rec['block_median_rule_rms']:.2f}", flush=True)
            per_seed.append(rec)
        res[f"E5_{label}"] = {"per_seed": per_seed,
                              "mean": {"diag_rms": {F: float(np.mean([p["diag_rms"][F] for p in per_seed])) for F in FAMILIES},
                                       "coupling_ratio": float(np.mean([p["coupling_ratio"] for p in per_seed])),
                                       "coupling_rms": float(np.mean([p["coupling_rms"] for p in per_seed])),
                                       "coupling_zero_rms": float(np.mean([p["coupling_zero_rms"] for p in per_seed])),
                                       "block_rms": float(np.mean([p["block_rms"] for p in per_seed])),
                                       "block_median_rule_rms": float(np.mean([p["block_median_rule_rms"] for p in per_seed])),
                                       "probe_ring": float(np.mean([p["probe"][RING] for p in per_seed]))}}
        m = res[f"E5_{label}"]["mean"]
        print(f"  E5-{label} MEAN: diag " + " ".join(f"{F} {m['diag_rms'][F]:6.2f} |" for F in FAMILIES)
              + f" coupling ratio {m['coupling_ratio']:.2f} | block {m['block_rms']:.2f} vs median {m['block_median_rule_rms']:.2f} | probe ring {m['probe_ring']:.2f}", flush=True)
    json.dump(res, open(a.out_prefix + ".json", "w"), indent=1)
    md = [f"# E5 — skip-gram analogue: mode embeddings from the coupling context ({res['date']}); held-out RMS in cm⁻¹, 12 molecules", "",
          f"Training: 30 molecules, {n_pairs} mode pairs, {a.steps} steps, seeds 0–2. Readings: ring diagonal win < 10 (Transformer 12.4); ring coupling ratio to zero rule win ≤ 0.7.", "",
          "| encoder | " + " | ".join(f"diag {F}" for F in FAMILIES) + " | ring couplings RMS / zero | ratio | ring block RMS / median rule | probe ring |",
          "|---|" + "---|" * (len(FAMILIES) + 4)]
    for label in ("tok", "atoms"):
        m = res[f"E5_{label}"]["mean"]
        md.append(f"| E5-{label} | " + " | ".join(f"{m['diag_rms'][F]:.2f}" for F in FAMILIES) + f" | {m['coupling_rms']:.2f} / {m['coupling_zero_rms']:.2f} | {m['coupling_ratio']:.2f} | {m['block_rms']:.2f} / {m['block_median_rule_rms']:.2f} | {m['probe_ring']:.2f} |")
    open(a.out_prefix + ".md", "w", encoding="utf-8").write("\n".join(md) + "\n")
    print("wrote", a.out_prefix + ".json/.md", flush=True)


if __name__ == "__main__":
    main()
