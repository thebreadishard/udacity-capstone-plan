"""Learning curve, second pass — one controlled change: environment descriptors (19 September 2026, afternoon).

The first pass (learning_curve_layerA.py, 12:4x) left the ring-in-plane family at 12.4 cm⁻¹ with a slope of −0.10:
more molecules will not fix it; the 18 September desk note's rule 2 says descriptors before capacity. This script
keeps model, split, sizes, seeds and steps identical and changes ONLY the token: token set A is the first pass's
(ω, family one-hot, C/H/N/O shares, localisation, out-of-plane share); token set B adds, per mode, the
participation-weighted shares of

  hydrogens by PAH environment class — solo / duo / trio / quartet (the run length of adjacent aromatic C–H
  along the ring), and substituent H (methyl, OH, NH2 …);
  carbons by ring role — fused (in two rings), ring edge with H, ring edge with a substituent, non-ring sp2,
  sp3; and heteroatom (N/O/S) participation split ring / non-ring.

Bond graph from covalent radii (1.2 × sum), rings by a bounded cycle search (5–7 members). Everything else is
imported from learning_curve_layerA.py so that the comparison is like for like.

Usage: python learning_curve_layerA_v2_descriptors.py <corpus/molecules dir> <out prefix> [--epochs 600] [--threads 1]
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from learning_curve_layerA import (AMU2AU, FAMILIES, SEEDS, SIZES, molecule_features, normal_modes,  # noqa: E402
                                   predict, rms, train)

BOHR = 0.529177210903
COV = {"H": 0.31, "C": 0.76, "N": 0.71, "O": 0.66, "S": 1.05, "F": 0.57, "Cl": 1.02}
H_CLASSES = ["H_solo", "H_duo", "H_trio", "H_quartet", "H_subst"]
C_CLASSES = ["C_fused", "C_edgeH", "C_edgeX", "C_nonring_sp2", "C_sp3"]
X_CLASSES = ["X_ring", "X_nonring"]


def bond_graph(symbols, coords_bohr):
    x = np.asarray(coords_bohr) * BOHR
    n = len(symbols); adj = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if np.linalg.norm(x[i] - x[j]) < 1.2 * (COV.get(symbols[i], 0.75) + COV.get(symbols[j], 0.75)):
                adj[i].add(j); adj[j].add(i)
    return adj


def rings(adj, max_len=7):
    """All simple cycles of length 3..max_len as frozensets (each found once)."""
    found = set()
    n = len(adj)
    for start in range(n):
        stack = [(start, [start])]
        while stack:
            v, path = stack.pop()
            for w in adj[v]:
                if w == start and len(path) >= 3:
                    found.add(frozenset(path))
                elif w not in path and len(path) < max_len and w > start:
                    stack.append((w, path + [w]))
    return [r for r in found if 5 <= len(r) <= max_len]


def atom_classes(symbols, coords_bohr):
    adj = bond_graph(symbols, coords_bohr)
    R = rings(adj)
    n_rings = np.zeros(len(symbols), int)
    for r in R:
        for a in r: n_rings[a] += 1
    ring_atoms = {a for r in R for a in r}
    cls = [None] * len(symbols)
    # carbons and heteroatoms
    for a, s in enumerate(symbols):
        if s == "C":
            if len(adj[a]) >= 4: cls[a] = "C_sp3"
            elif n_rings[a] >= 2: cls[a] = "C_fused"
            elif n_rings[a] == 1:
                cls[a] = "C_edgeH" if any(symbols[b] == "H" for b in adj[a]) else "C_edgeX"
            else: cls[a] = "C_nonring_sp2"
        elif s != "H":
            cls[a] = "X_ring" if a in ring_atoms else "X_nonring"
    # hydrogens: run length of consecutive ring C–H along a ring
    ch_ring = {a for a, s in enumerate(symbols) if s == "C" and n_rings[a] == 1 and any(symbols[b] == "H" for b in adj[a])}
    for a, s in enumerate(symbols):
        if s != "H": continue
        c = next(iter(adj[a])) if adj[a] else None
        if c is None or c not in ch_ring:
            cls[a] = "H_subst"; continue
        # walk along ring neighbours that are also CH
        run = {c}; frontier = [c]
        while frontier:
            v = frontier.pop()
            for w in adj[v]:
                if w in ch_ring and w not in run and any(v in r and w in r for r in R):
                    run.add(w); frontier.append(w)
        cls[a] = H_CLASSES[min(len(run), 4) - 1]
    return cls, len(R)


def environment_tokens(mol_dir, base):
    g = json.load(open(mol_dir / "geometry.json"))
    symbols = g["symbols"]; masses = np.asarray(g["masses_amu"])
    lo = np.load(mol_dir / "hessian_b3lyp.npz")
    _, _, V, _ = normal_modes(lo["H_projected"], masses)
    A = (V.reshape(len(symbols), 3, -1) ** 2).sum(1)          # (N, M) participation per atom
    cls, n_rings = atom_classes(symbols, g["coords_bohr"])
    cols = []
    for name in H_CLASSES + C_CLASSES + X_CLASSES:
        idx = [a for a, c in enumerate(cls) if c == name]
        cols.append(A[idx].sum(0) if idx else np.zeros(A.shape[1]))
    extra = np.stack(cols, 1).astype(np.float32)
    return np.concatenate([base["tokens"], extra], 1), cls, n_rings


def curve(mols, sizes, test, pool, epochs, label):
    y_test = {F: np.concatenate([m["target"][np.array(m["family"]) == F] for m in test]) for F in FAMILIES}
    out = {"zero_rule_rms": {F: rms(y_test[F]) for F in FAMILIES}, "curve": {}}
    for n in sizes:
        tr = pool[:n]
        per_seed = []
        for s in SEEDS:
            model, scale = train(tr, s, epochs)
            preds = predict(model, scale, test)
            err = {F: np.concatenate([(p - m["target"])[np.array(m["family"]) == F] for p, m in zip(preds, test)]) for F in FAMILIES}
            tr_err = np.concatenate([p - m["target"] for p, m in zip(predict(model, scale, tr), tr)])
            per_seed.append({"seed": s, "rms": {F: rms(err[F]) for F in FAMILIES}, "train_rms_all": rms(tr_err)})
        out["curve"][str(n)] = {"model_rms_mean": {F: float(np.mean([p["rms"][F] for p in per_seed])) for F in FAMILIES},
                                "train_rms_all_mean": float(np.mean([p["train_rms_all"] for p in per_seed])), "per_seed": per_seed}
        print(f"[{label}] n={n:2d} " + " ".join(f"{F} {out['curve'][str(n)]['model_rms_mean'][F]:6.2f} |" for F in FAMILIES)
              + f" train {out['curve'][str(n)]['train_rms_all_mean']:.2f}", flush=True)
    ln = np.log(sizes)
    out["power_law_slope"] = {F: float(np.polyfit(ln, np.log([out["curve"][str(n)]["model_rms_mean"][F] for n in sizes]), 1)[0]) for F in FAMILIES} if len(sizes) >= 2 else {}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("molecules"); ap.add_argument("out_prefix")
    ap.add_argument("--test-frac", type=float, default=0.25); ap.add_argument("--epochs", type=int, default=600)
    ap.add_argument("--threads", type=int, default=1)
    a = ap.parse_args()
    torch.set_num_threads(a.threads)
    mdir = Path(a.molecules)
    molsA, molsB, cls_counts = [], [], {}
    for d in sorted(p for p in mdir.iterdir() if (p / "hessian_wb97x.npz").exists() and (p / "hessian_b3lyp.npz").exists()):
        try:
            base = molecule_features(d)
            tokB, cls, n_rings = environment_tokens(d, base)
            molsA.append(base); molsB.append(dict(base, tokens=tokB))
            for c in cls: cls_counts[c] = cls_counts.get(c, 0) + 1
        except Exception as e:
            print("skip", d.name, repr(e))
    order = sorted(range(len(molsA)), key=lambda i: hashlib.sha1(molsA[i]["id"].encode()).hexdigest())
    molsA = [molsA[i] for i in order]; molsB = [molsB[i] for i in order]
    n_test = max(1, math.ceil(a.test_frac * len(molsA)))
    sizes = [n for n in SIZES if n <= len(molsA) - n_test] or [len(molsA) - n_test]
    print(f"{len(molsA)} molecules, {n_test} held out; atom classes over the corpus: {cls_counts}; token widths A {molsA[0]['tokens'].shape[1]} B {molsB[0]['tokens'].shape[1]}", flush=True)
    resA = curve(molsA, sizes, molsA[:n_test], molsA[n_test:], a.epochs, "A: first-pass tokens")
    resB = curve(molsB, sizes, molsB[:n_test], molsB[n_test:], a.epochs, "B: + environment descriptors")
    res = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "n_molecules": len(molsA), "n_test": n_test, "sizes": sizes, "seeds": SEEDS,
           "epochs": a.epochs, "atom_class_counts": cls_counts, "A": resA, "B": resB}
    json.dump(res, open(a.out_prefix + ".json", "w"), indent=1)
    md = [f"# Learning curve, second pass — environment descriptors as the one change ({res['date']})", "",
          f"{len(molsA)} molecules, {n_test} held out (same hash split as the first pass), {a.epochs} steps, seeds {SEEDS}; held-out RMS in cm⁻¹, A / B.", "",
          "| n_train | " + " | ".join(FAMILIES) + " | train (all) A / B |", "|---|" + "---|" * (len(FAMILIES) + 1)]
    for n in sizes:
        cA, cB = resA["curve"][str(n)], resB["curve"][str(n)]
        md.append(f"| {n} | " + " | ".join(f"{cA['model_rms_mean'][F]:.2f} / **{cB['model_rms_mean'][F]:.2f}**" for F in FAMILIES)
                  + f" | {cA['train_rms_all_mean']:.2f} / {cB['train_rms_all_mean']:.2f} |")
    md += ["", "Zero rule: " + ", ".join(f"{F} {resA['zero_rule_rms'][F]:.2f}" for F in FAMILIES),
           "Slopes A: " + ", ".join(f"{F} {s:+.2f}" for F, s in resA["power_law_slope"].items()),
           "Slopes B: " + ", ".join(f"{F} {s:+.2f}" for F, s in resB["power_law_slope"].items())]
    open(a.out_prefix + ".md", "w", encoding="utf-8").write("\n".join(md) + "\n")
    print("wrote", a.out_prefix + ".json/.md")


if __name__ == "__main__":
    main()
