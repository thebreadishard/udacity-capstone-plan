"""E7 / rung B — the correction as pairwise local force-constant terms, learned and projected (pre-registered 23 September 2026,
PreRegistration_2026-09-23_E7_Couplings_in_Local_Coordinates.md, section "Rung B").

Target per molecule: the minimum-norm internal correction ΔF = B⁺ᵀ ΔH B⁺ (redundant geomeTRIC primitives, deterministic construction) on the
pattern that post-hoc (ix) showed carries three quarters of ΔH: the diagonal, pairs of primitives sharing an atom, and bond–bond pairs inside
one ring (ortho / meta / para interaction constants). Every element is rotation-invariant and sign-consistent; a molecule contributes thousands
of labelled pairs.

Features: per primitive — class (bond/angle/dihedral/oop/linear), element counts, ring flag, value, F_low,kk, the 12 environment classes of
its atoms, ring counts; per pair — symmetric combination (sum and |difference| of the two primitive vectors), shared atoms, same-ring flag,
ring-path distance for bond pairs (one-hot 1/2/3), F_low,ij, F_low,ii·F_low,jj, diagonal flag.

Models: B1 = MLP (2 × 128, GELU; targets standardised per pair class; AdamW; 3 seeds); B2 = HistGradientBoosting (non-neural check).
Prediction: ΔF_pred on the pattern → ΔH_pred = Bᵀ ΔF_pred B → K_pred in the B3LYP mode basis; E6 read-outs (diagonal per family, ring
coupling RMS and ratio to the zero rule, ring block vs median rule) on hold-outs (a) and (b), plus corrected-frequency RMS, Duschinsky
overlap and the Cartesian ΔH residual ratio. Sizes 45, 100, full pool.

Usage: python e7_rungB_pairs.py <corpus/molecules dir> <out prefix> [--threads 16] [--sizes 45,100,all] [--epochs 60] [--smoke]
"""
import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

sys.path.insert(0, str(Path(__file__).resolve().parent))
import e6_learning_curve as E6  # noqa: E402
import e7_t2_posthoc as PH  # noqa: E402
import e7_t2_sqm as T2  # noqa: E402
from learning_curve_layerA import FAMILIES  # noqa: E402
from learning_curve_layerA_v2_descriptors import C_CLASSES, H_CLASSES, X_CLASSES, atom_classes, bond_graph, rings  # noqa: E402

RING = "ring-ip"
ELEMS = ["H", "C", "N", "O", "S", "F", "Cl"]
CLASSES = H_CLASSES + C_CLASSES + X_CLASSES
PRIM_CLASSES = ["Distance", "Angle", "Dihedral", "OutOfPlane", "LinearAngle", "other"]
PAIR_CLASS = ["diag_bond", "diag_angle", "diag_dihedral", "diag_other", "off_bondbond", "off_other"]


# ------------------------------------------------------------------------------------------------------------- geometry side
def ring_cycles(adj, R):
    """Ordered atom cycles for the ring sets of rings()."""
    cycles = []
    for r in R:
        r = set(r); start = min(r); order = [start]; prev = None; cur = start
        while True:
            nxt = [w for w in adj[cur] if w in r and w != prev and w not in order]
            if not nxt:
                break
            prev, cur = cur, nxt[0]; order.append(cur)
        cycles.append(order if len(order) == len(r) else sorted(r))
    return cycles


def molecule_pairs(symbols_raw, coords_bohr, F_low):
    """Primitive feature vectors, the pattern pairs with pair features, and metadata."""
    from geometric.internal import Angle, Dihedral, Distance, LinearAngle, OutOfPlane, PrimitiveInternalCoordinates
    from geometric.molecule import Molecule
    symbols = [s.capitalize() for s in symbols_raw]; coords = np.asarray(coords_bohr, float)
    M = Molecule(); M.elem = list(symbols); M.xyzs = [coords * T2.BOHR2ANG]
    ic = PrimitiveInternalCoordinates(M, build=True, connect=True, addcart=False)
    prims = ic.Internals; xyz = coords.flatten(); n = len(prims)
    adj = bond_graph(symbols, coords); R = rings(adj); cycles = ring_cycles(adj, R)
    cls, _ = atom_classes(symbols, coords)
    nring_atom = np.zeros(len(symbols), int)
    for r in R:
        for a_ in r:
            nring_atom[a_] += 1
    ring_bonds = {}
    for ri, cyc in enumerate(cycles):
        L = len(cyc)
        for k in range(L):
            e = frozenset((cyc[k], cyc[(k + 1) % L])); ring_bonds.setdefault(e, {})[ri] = k
    atoms, feats, pclass, is_bond, bond_edge = [], [], [], [], []
    for p in prims:
        at = [getattr(p, k) for k in ("a", "b", "c", "d") if hasattr(p, k)]
        if isinstance(p, Distance):
            pc = 0; ringflag = frozenset((p.a, p.b)) in ring_bonds
        elif isinstance(p, Angle):
            pc = 1; ringflag = frozenset((p.a, p.b)) in ring_bonds and frozenset((p.b, p.c)) in ring_bonds
        elif isinstance(p, Dihedral):
            pc = 2; ringflag = frozenset((p.b, p.c)) in ring_bonds
        elif isinstance(p, OutOfPlane):
            pc = 3; ringflag = nring_atom[p.a] > 0
        elif isinstance(p, LinearAngle):
            pc = 4; ringflag = False
        else:
            pc = 5; ringflag = False
        try:
            val = float(p.value(xyz))
        except Exception:  # noqa: BLE001
            val = 0.0
        f = np.zeros(len(PRIM_CLASSES) + len(ELEMS) + 1 + 1 + 1 + len(CLASSES) + 1, np.float32)
        f[pc] = 1.0
        for a_ in at:
            e = symbols[a_]
            if e in ELEMS:
                f[len(PRIM_CLASSES) + ELEMS.index(e)] += 1.0
            if cls[a_] in CLASSES:
                f[len(PRIM_CLASSES) + len(ELEMS) + 3 + CLASSES.index(cls[a_])] += 1.0
            f[-1] += nring_atom[a_]
        f[len(PRIM_CLASSES) + len(ELEMS)] = float(ringflag)
        f[len(PRIM_CLASSES) + len(ELEMS) + 1] = val
        f[len(PRIM_CLASSES) + len(ELEMS) + 2] = float(F_low[len(atoms), len(atoms)])
        atoms.append(set(at)); feats.append(f); pclass.append(pc); is_bond.append(pc == 0); bond_edge.append(frozenset(at) if pc == 0 else None)
    feats = np.stack(feats)
    pairs, pfeat, pcls = [], [], []
    for i in range(n):
        for j in range(i, n):
            shared = len(atoms[i] & atoms[j]); same_ring = 0; rdist = 0
            if is_bond[i] and is_bond[j] and i != j:
                ri_ = ring_bonds.get(bond_edge[i], {}); rj_ = ring_bonds.get(bond_edge[j], {})
                common = set(ri_) & set(rj_)
                if common:
                    same_ring = 1
                    rdist = min(min(abs(ri_[r] - rj_[r]), len(cycles[r]) - abs(ri_[r] - rj_[r])) for r in common)
            if not (i == j or shared > 0 or same_ring):
                continue
            if i == j:
                pc_pair = {0: 0, 1: 1, 2: 2}.get(pclass[i], 3)
            else:
                pc_pair = 4 if (is_bond[i] and is_bond[j]) else 5
            extra = np.array([shared, same_ring, float(rdist == 1), float(rdist == 2), float(rdist >= 3), F_low[i, j], F_low[i, i] * F_low[j, j], float(i == j)], np.float32)
            pairs.append((i, j)); pfeat.append(np.concatenate([feats[i] + feats[j], np.abs(feats[i] - feats[j]), extra])); pcls.append(pc_pair)
    return np.array(pairs), np.stack(pfeat).astype(np.float32), np.array(pcls), ic.wilsonB(xyz)


# ------------------------------------------------------------------------------------------------------------------ models
class MLP(nn.Module):
    def __init__(self, d_in, d=128):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(d_in, d), nn.GELU(), nn.Linear(d, d), nn.GELU(), nn.Linear(d, 1))

    def forward(self, x):
        return self.net(x).squeeze(-1)


def train_mlp(X, y, c, seed, epochs, mu, sd, tscale, bs=4096):
    torch.manual_seed(seed); rng = np.random.default_rng(seed)
    Xt = torch.tensor((X - mu) / sd); yt = torch.tensor(y / tscale[c])
    m = MLP(X.shape[1]); opt = torch.optim.AdamW(m.parameters(), lr=1e-3, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, epochs)
    for _ in range(epochs):
        m.train(); order = rng.permutation(len(y))
        for s in range(0, len(y), bs):
            b = torch.tensor(order[s:s + bs]); loss = ((m(Xt[b]) - yt[b]) ** 2).mean()
            opt.zero_grad(); loss.backward(); opt.step()
        sched.step()
    m.eval(); return m


def predict_mlp(m, X, c, mu, sd, tscale):
    with torch.no_grad():
        return m(torch.tensor((X - mu) / sd)).numpy() * tscale[c]


def assemble(m, pairs, vals):
    n = m["B"].shape[0]; dF = np.zeros((n, n))
    for (i, j), v in zip(pairs, vals):
        dF[i, j] = v; dF[j, i] = v
    return dF


def readouts(mols, ids, tr, dF_of):
    P = {i: PH.k_of(mols[i], dF_of(i)) for i in ids}
    res = dict(E6.readout(P, mols, ids, tr), **T2.basis_free(P, mols, ids))
    res["dH_residual_ratio"] = float(np.sqrt(np.mean([np.mean((mols[i]["B"].T @ dF_of(i) @ mols[i]["B"] - mols[i]["dH_true"]) ** 2) for i in ids])
                                             / np.mean([np.mean(mols[i]["dH_true"] ** 2) for i in ids])))
    return res


# ---------------------------------------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("molecules"); ap.add_argument("out_prefix")
    ap.add_argument("--threads", type=int, default=16); ap.add_argument("--sizes", default="45,100,all"); ap.add_argument("--epochs", type=int, default=60)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--orbit-average-targets", action="store_true", help="E11.8 (25 Sep 2026): average every per-pair target over its symmetry orbit (graph automorphisms, same-parity pairs) before training, for every molecule with a manifest SMILES; the frequency/coupling read-outs still compare against the original dH_true")
    ap.add_argument("--seeds", default="0,1,2", help="25 Sep 2026: seeds to train (the E11.2 orbit rerun uses 0); default unchanged")
    ap.add_argument("--shuffle-labels", action="store_true", help="E11.1 (25 Sep 2026): targets permuted within pair class across the pool — a control that must NOT learn")
    ap.add_argument("--dump", action="store_true", help="E11.2/3/6/7 (25 Sep 2026): per-molecule errors, pair-class breakdown, symmetry consistency, ring bond-bond terms of the seed-0 model at the full pool")
    ap.add_argument("--split", default="e6", help="e6 (default): E6 hold-outs (a) layer-A, (b) scaffolds. size:N (25 Sep 2026, size-extrapolation desk test): (a) := admitted molecules with more than N atoms, (b) := E6 scaffold hold-out with <= N atoms, pool := the rest with <= N atoms")
    ap.add_argument("--use-analytic", action="store_true",
                    help="23 Sep: for molecules with hessian_<tag>_analytic.npz (pyscf second route, corpus/analytic_hessians.py) use those Hessians instead of the psi4 "
                         "finite-difference ones (benzene's FD wB97X Hessian was a 133 cm-1 artefact)")
    a = ap.parse_args(); torch.set_num_threads(a.threads); t0 = time.time()
    mols = T2.load(a.molecules)
    test_a, test_b, cores, pool = E6.splits(mols)
    substituted = []
    if a.use_analytic:
        import e7_rungB_reread_analytic as RR
        for i, m in mols.items():
            d = Path(a.molecules) / i
            if (d / "hessian_b3lyp_analytic.npz").exists() and (d / "hessian_wb97x_analytic.npz").exists():
                RR.substitute(m, d); substituted.append(i)
        print(f"analytic second-route Hessians substituted for {len(substituted)} molecules: {substituted}", flush=True)
    mols = {i: m for i, m in mols.items() if not m["imaginary"]}
    test_a = [i for i in test_a if i in mols]; test_b = [i for i in test_b if i in mols]; pool = [i for i in pool if i in mols]
    if a.split.startswith("size:"):
        N = int(a.split.split(":")[1]); nat = {i: len(m["masses"]) for i, m in mols.items()}
        test_a = sorted(i for i in mols if nat[i] > N); test_b = [i for i in test_b if nat[i] <= N]
        pool = sorted((i for i in mols if nat[i] <= N and i not in set(test_b)), key=E6.sha)
        print(f"size split at {N} atoms: hold-out (a) = {len(test_a)} molecules > {N} atoms, (b) = {len(test_b)} scaffold molecules <= {N}, pool {len(pool)}", flush=True)
    sizes = sorted({min(int(s) if s != "all" else len(pool), len(pool)) for s in a.sizes.split(",")})
    seeds = [int(s) for s in a.seeds.split(",")]
    if a.smoke:
        sizes, seeds, a.epochs = sizes[:1], [0], 2
    # pairs, features, targets (minimum-norm internal ΔF) per molecule
    for i, m in mols.items():
        g = json.load(open(Path(a.molecules) / i / "geometry.json"))
        pairs, X, c, B = molecule_pairs(g["symbols"], np.asarray(g["coords_bohr"]), m["F_low"])
        Bp = np.linalg.pinv(m["B"]); dFmn = Bp.T @ m["dH_true"] @ Bp
        m.update(pairs=pairs, X=X, pc=c, y=np.array([dFmn[i_, j_] for i_, j_ in pairs]), symbols=g["symbols"], coords=np.asarray(g["coords_bohr"]))
    if a.orbit_average_targets:
        import csv as _csv, e11_extras as E11
        man = {r["id"]: r for r in _csv.DictReader(open(Path(a.molecules).parent / "manifest.csv", newline="", encoding="utf-8"))}
        n_avg = 0; n_pairs_avg = 0; moved = []
        for i, m in mols.items():
            if i not in man: continue
            og = E11.orbit_groups(m, man[i]["smiles"])
            if not og: continue
            y0 = m["y"].copy()
            for g in og: m["y"][g] = m["y"][g].mean()
            n_avg += 1; n_pairs_avg += int(sum(len(g) for g in og)); moved.append(float(np.sqrt(np.mean((m["y"] - y0) ** 2)) / max(float(np.sqrt(np.mean(y0 ** 2))), 1e-12)))
        print(f"E11.8: targets averaged over symmetry orbits in {n_avg} molecules ({n_pairs_avg} pairs in orbits); RMS change of the targets, median {np.median(moved):.3f} of their RMS, max {max(moved):.3f}", flush=True)
    if a.shuffle_labels:
        import e11_extras as E11
        print(f"E11.1: targets shuffled within pair class across {E11.shuffle_targets(mols, pool, seed=0)} pool molecules — this run is a CONTROL", flush=True)
    npairs = np.array([len(m["pairs"]) for m in mols.values()])
    print(f"{len(mols)} molecules; pattern pairs per molecule {npairs.min()}–{npairs.max()} (features {mols[pool[0]]['X'].shape[1]}); hold-out (a) {len(test_a)}, (b) {len(test_b)} ({cores}); "
          f"pool {len(pool)}; sizes {sizes}; seeds {seeds}; epochs {a.epochs}", flush=True)
    tests = {"a": test_a, "b": test_b}
    res = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "smoke": a.smoke, "n_molecules": len(mols), "holdout_a": test_a, "holdout_b": test_b, "scaffold_cores": cores,
           "pool": len(pool), "sizes": sizes, "seeds": seeds, "epochs": a.epochs, "n_features": int(mols[pool[0]]["X"].shape[1]), "substituted_analytic": substituted, "curve": {}}
    zero = {h: readouts(mols, ids, pool, lambda i: np.zeros_like(mols[i]["F_low"])) for h, ids in tests.items()}
    res["zero_rule"] = zero
    for n in sizes:
        tr = pool[:n]
        X = np.concatenate([mols[i]["X"] for i in tr]); y = np.concatenate([mols[i]["y"] for i in tr]); c = np.concatenate([mols[i]["pc"] for i in tr])
        mu = X.mean(0); sd = X.std(0) + 1e-6
        tscale = np.array([max(float(np.std(y[c == k])), 1e-6) if (c == k).any() else 1.0 for k in range(len(PAIR_CLASS))], np.float32)
        row = {"n": n, "n_pairs_train": int(len(y)), "target_scale_per_class": {PAIR_CLASS[k]: float(tscale[k]) for k in range(len(PAIR_CLASS))}, "B1_mlp": {"per_seed": []}, "B2_gbt": {}}
        t1 = time.time()
        for seed in seeds:
            m_ = train_mlp(X, y, c, seed, a.epochs, mu, sd, tscale)
            pred = {i: assemble(mols[i], mols[i]["pairs"], predict_mlp(m_, mols[i]["X"], mols[i]["pc"], mu, sd, tscale)) for i in test_a + test_b}
            if a.dump and seed == seeds[0] and n == sizes[-1]:
                import e11_extras as E11
                vals0 = {i: predict_mlp(m_, mols[i]["X"], mols[i]["pc"], mu, sd, tscale) for i in test_a + test_b}
                E11.dump(mols, tests, pred, vals0, a.out_prefix, a.molecules, PAIR_CLASS); print("E11 dump written", flush=True)
            row["B1_mlp"]["per_seed"].append({h: readouts(mols, ids, tr, lambda i, pred=pred: pred[i]) for h, ids in tests.items()})
        row["B1_mlp"]["mean"] = {h: E6.mean_records([p[h] for p in row["B1_mlp"]["per_seed"]]) for h in tests}; row["B1_mlp"]["seconds"] = round(time.time() - t1)
        t2 = time.time()
        from sklearn.ensemble import HistGradientBoostingRegressor
        gbt = HistGradientBoostingRegressor(max_iter=(20 if a.smoke else 400), learning_rate=0.08, max_leaf_nodes=63, random_state=0).fit(X, y)
        pred = {i: assemble(mols[i], mols[i]["pairs"], gbt.predict(mols[i]["X"])) for i in test_a + test_b}
        row["B2_gbt"] = {h: readouts(mols, ids, tr, lambda i, pred=pred: pred[i]) for h, ids in tests.items()}; row["B2_gbt"]["seconds"] = round(time.time() - t2)
        for label, r_ in (("B1 MLP", row["B1_mlp"]["mean"]), ("B2 GBT", row["B2_gbt"])):
            for h in ("a", "b"):
                x = r_[h]
                print(f"n={n:3d} ({h}) {label}: diag " + " ".join(f"{F} {x['diag_rms'][F]:6.2f} |" for F in FAMILIES)
                      + f" ring couplings {x['coupling_rms']:.2f} vs zero {x['coupling_zero_rms']:.2f} (ratio {x['coupling_ratio']:.2f}) | block {x['block_rms']:.2f} vs median {x['block_median_rule_rms']:.2f}"
                      + f" | corrected ω {x['corrected_freq_rms']:.2f} (zero {x['corrected_freq_rms_zero_rule']:.2f}) | overlap {x['duschinsky_overlap_median']:.3f} | ΔH residual {x['dH_residual_ratio']:.2f}", flush=True)
        res["curve"][str(n)] = row
        json.dump(res, open(a.out_prefix + ".json", "w"), indent=1)
    ln = np.log(sizes)
    ratios = {h: [res["curve"][str(n)]["B1_mlp"]["mean"][h]["coupling_ratio"] for n in sizes] for h in tests}
    slope = {h: (float(np.polyfit(ln, np.log(np.maximum(ratios[h], 1e-6)), 1)[0]) if len(sizes) > 1 else float("nan")) for h in tests}
    nf = str(sizes[-1]); ra = res["curve"][nf]["B1_mlp"]["mean"]["a"]["coupling_ratio"]; rb = res["curve"][nf]["B1_mlp"]["mean"]["b"]["coupling_ratio"]
    verdict = "WIN" if (ra <= 0.6 and rb <= 0.6 and slope["a"] < 0) else ("LOSE" if ra >= 0.9 else "between")
    res["readings"] = {"coupling_ratio_curve_mlp": ratios, "slope_mlp": slope, "verdict": verdict, "ratio_a_full": ra, "ratio_b_full": rb}; res["seconds"] = round(time.time() - t0)
    json.dump(res, open(a.out_prefix + ".json", "w"), indent=1)
    md = [f"# E7 / rung B — pairwise local force-constant terms, learned and projected ({res['date']}){' — SMOKE, NOT A RESULT' if a.smoke else ''}", "",
          f"{len(mols)} molecules; hold-out (a) {len(test_a)} layer-A molecules, (b) scaffold cores {cores} ({len(test_b)}); pool {len(pool)}; sizes {sizes}; seeds {seeds}; "
          f"{a.epochs} epochs; {res['n_features']} pair features; pattern pairs per molecule {npairs.min()}–{npairs.max()}. RMS in cm⁻¹; MLP mean over seeds.", "",
          "| n | hold-out | model | " + " | ".join(f"diag {F}" for F in FAMILIES) + " | ring coupling RMS / zero | ratio | ring block / median | corrected ω RMS (zero) | overlap | ΔH residual |",
          "|---|---|---|" + "---|" * (len(FAMILIES) + 6)]
    for n in sizes:
        for h in ("a", "b"):
            for label, x in (("zero rule", zero[h]), ("B1 MLP", res["curve"][str(n)]["B1_mlp"]["mean"][h]), ("B2 GBT", res["curve"][str(n)]["B2_gbt"][h])):
                md.append(f"| {n} | ({h}) | {label} | " + " | ".join(f"{x['diag_rms'][F]:.2f}" for F in FAMILIES)
                          + f" | {x['coupling_rms']:.2f} / {x['coupling_zero_rms']:.2f} | **{x['coupling_ratio']:.2f}** | {x['block_rms']:.2f} / {x['block_median_rule_rms']:.2f} | {x['corrected_freq_rms']:.2f} ({x['corrected_freq_rms_zero_rule']:.2f}) | {x['duschinsky_overlap_median']:.3f} | {x['dH_residual_ratio']:.2f} |")
    md += ["", "## Readings (pre-registered)", "",
           f"- B1 MLP ring coupling ratio vs n: (a) " + ", ".join(f"{n}: {v:.2f}" for n, v in zip(sizes, ratios['a'])) + f" (slope {slope['a']:+.2f}); (b) " + ", ".join(f"{n}: {v:.2f}" for n, v in zip(sizes, ratios['b'])) + f" (slope {slope['b']:+.2f})",
           f"- Verdict at n = {nf}: ratio (a) {ra:.2f}, (b) {rb:.2f}, slope (a) {slope['a']:+.2f} → **{verdict}** (win: ≤ 0.6 on both and a negative slope; lose: ≥ 0.9 on (a))",
           "", f"Total {res['seconds']} s."]
    open(a.out_prefix + ".md", "w", encoding="utf-8").write("\n".join(md) + "\n")
    print("wrote", a.out_prefix + ".json/.md", f"in {res['seconds']} s", flush=True)


if __name__ == "__main__":
    main()
