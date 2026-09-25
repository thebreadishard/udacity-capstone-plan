"""E11 extras for the rung-B script (pre-registered 25 September 2026, PreRegistration_2026-09-25_E11_Proof_Strengthening_Desk_Tests.md):
E11.1 shuffled labels (a control), E11.2 symmetry consistency of the predictions, E11.3 the ring bond–bond pair terms of benzene / naphthalene,
E11.6 per-molecule errors against size, E11.7 the error per pair class and ring-path distance. Imported by e7_rungB_pairs.py under flags;
the defaults of that script are unchanged, so E7's numbers stand."""
import csv
import json
from pathlib import Path

import numpy as np


def shuffle_targets(mols, pool, seed=0):
    """E11.1: give every pool molecule targets drawn from the pool's pairs of the same pair class (a permutation within each class across the pool).
    The molecule keeps its own features and pair list; only the numbers it is asked to fit are someone else's."""
    rng = np.random.default_rng(seed)
    by_cls = {}
    for i in pool:
        for c, y in zip(mols[i]["pc"], mols[i]["y"]):
            by_cls.setdefault(int(c), []).append(float(y))
    perm = {c: rng.permutation(np.array(v)) for c, v in by_cls.items()}; cursor = {c: 0 for c in perm}
    for i in pool:
        y = np.empty_like(mols[i]["y"])
        for k, c in enumerate(mols[i]["pc"]):
            y[k] = perm[int(c)][cursor[int(c)]]; cursor[int(c)] += 1
        mols[i]["y"] = y
    return len(pool)


def prim_atom_tuples(symbols_raw, coords_bohr):
    """Atom tuples of the geomeTRIC primitives in the same construction as molecule_pairs (order of primitives identical)."""
    from geometric.internal import PrimitiveInternalCoordinates
    from geometric.molecule import Molecule
    import e7_t2_sqm as T2
    symbols = [s.capitalize() for s in symbols_raw]
    M = Molecule(); M.elem = list(symbols); M.xyzs = [np.asarray(coords_bohr) * T2.BOHR2ANG]
    ic = PrimitiveInternalCoordinates(M, build=True, connect=True, addcart=False)
    out = []
    for p in ic.Internals:
        t = tuple(getattr(p, k) for k in ("a", "b", "c", "d") if hasattr(p, k)); out.append((type(p).__name__, t))
    return out


def atom_ranks(smiles):
    """RDKit canonical atom ranks without tie breaking (symmetry classes); AddHs order = the corpus geometry order (verified in E9)."""
    from rdkit import Chem
    m = Chem.AddHs(Chem.MolFromSmiles(smiles))
    return list(Chem.CanonicalRankAtoms(m, breakTies=False))


def pair_symmetry_key(prims, ranks, i, j):
    def key(k):
        name, t = prims[k]; r = tuple(ranks[x] for x in t)
        return (name, min(r, r[::-1]))
    a, b = key(i), key(j); return (a, b) if a <= b else (b, a)


def symmetry_spread(mol, pred_vals, smiles):
    """E11.2: RMS spread of the predictions within symmetry classes of pairs / RMS of predictions over all classed pairs (one molecule)."""
    prims = prim_atom_tuples(mol["symbols"], mol["coords"]); ranks = atom_ranks(smiles)
    if len(ranks) != len(mol["symbols"]): return None
    groups = {}
    for (i, j), v in zip(mol["pairs"], pred_vals):
        groups.setdefault(pair_symmetry_key(prims, ranks, int(i), int(j)), []).append(float(v))
    multi = [np.array(v) for v in groups.values() if len(v) > 1]
    if not multi: return None
    within = np.sqrt(np.mean(np.concatenate([(v - v.mean()) ** 2 for v in multi]))); total = np.sqrt(np.mean(np.concatenate(multi) ** 2))
    return dict(n_classes=len(multi), n_pairs_classed=int(sum(len(v) for v in multi)), within_rms=float(within), total_rms=float(total), spread_ratio=float(within / total) if total > 0 else None)


def ring_bond_pairs(mol, pred_vals, true_vals, F_low):
    """E11.3: predicted and true ΔF (and the B3LYP F_low for orientation) for ring bond–bond pairs at ring-path distance 1, 2, 3 (the features carry rdist one-hot)."""
    X = mol["X"]; nf = X.shape[1]; out = {}
    # the last eight pair features are: shared, same_ring, rdist==1, rdist==2, rdist>=3, F_low_ij, F_ii*F_jj, diag (molecule_pairs)
    for (i, j), p, t, feat in zip(mol["pairs"], pred_vals, true_vals, X):
        if i == j or feat[nf - 7] != 1.0: continue           # same_ring pairs only
        d = 1 if feat[nf - 6] == 1.0 else 2 if feat[nf - 5] == 1.0 else 3 if feat[nf - 4] == 1.0 else None
        if d is None: continue
        if mol["types"][int(i)][0] != "bond" or mol["types"][int(j)][0] != "bond": continue
        out.setdefault(d, {"pred": [], "true": [], "F_low": []})
        out[d]["pred"].append(float(p)); out[d]["true"].append(float(t)); out[d]["F_low"].append(float(F_low[int(i), int(j)]))
    return {{1: "ortho", 2: "meta", 3: "para"}[d]: {k: (float(np.mean(v)), len(v)) for k, v in dd.items()} for d, dd in out.items()}


def dump(mols, tests, pred_dF, pred_vals, out_prefix, mdir, pair_class_names):
    """E11.2, E11.3, E11.6, E11.7 read-outs for the seed-0 model at the full pool; writes <out_prefix>_dump.json/.md."""
    import e6_learning_curve as E6
    import e7_t2_sqm as T2
    man = {r["id"]: r for r in csv.DictReader(open(Path(mdir).parent / "manifest.csv", newline="", encoding="utf-8"))}
    res = {"per_molecule": {}, "pair_class_rms": {}, "symmetry": {}, "ring_bond_pairs": {}}
    for h, ids in tests.items():
        cls_err = {c: [] for c in range(len(pair_class_names))}; cls_val = {c: [] for c in range(len(pair_class_names))}
        for i in ids:
            m = mols[i]; P = {i: __import__("e7_t2_posthoc").k_of(m, pred_dF[i])}
            bf = T2.basis_free(P, mols, [i]); rd = E6.readout(P, mols, [i], ids)
            res["per_molecule"][i] = dict(holdout=h, n_atoms=int(len(m["masses"])), corrected_freq_rms=bf["corrected_freq_rms"], corrected_freq_rms_zero=bf["corrected_freq_rms_zero_rule"],
                                          coupling_ratio=rd["coupling_ratio"], name=man.get(i, {}).get("name", i))
            err = pred_vals[i] - m["y"]
            for c in range(len(pair_class_names)):
                sel = m["pc"] == c
                if sel.any(): cls_err[c].append(err[sel]); cls_val[c].append(m["y"][sel])
            s = symmetry_spread(m, pred_vals[i], man[i]["smiles"]) if i in man else None
            if s: res["symmetry"][i] = s
            if man.get(i, {}).get("name") in ("benzene", "naphthalene"):
                res["ring_bond_pairs"][man[i]["name"]] = ring_bond_pairs(m, pred_vals[i], m["y"], m["F_low"])
        res["pair_class_rms"][h] = {pair_class_names[c]: dict(rms_error=float(np.sqrt(np.mean(np.concatenate(cls_err[c]) ** 2))), rms_true=float(np.sqrt(np.mean(np.concatenate(cls_val[c]) ** 2))), n=int(sum(len(e) for e in cls_err[c])))
                                    for c in range(len(pair_class_names)) if cls_err[c]}
    # E11.6: slope of log(RMS per molecule) vs log(N_atoms), per hold-out
    res["size_slope"] = {}
    for h in tests:
        pm = [v for v in res["per_molecule"].values() if v["holdout"] == h and v["corrected_freq_rms"] > 0]
        if len(pm) >= 4:
            x = np.log([v["n_atoms"] for v in pm]); y = np.log([v["corrected_freq_rms"] for v in pm]); b, a_ = np.polyfit(x, y, 1)
            res["size_slope"][h] = dict(slope=float(b), n=len(pm), n_atoms_range=[int(np.exp(x.min())), int(np.exp(x.max()))])
    sp = [v["spread_ratio"] for v in res["symmetry"].values() if v and v["spread_ratio"] is not None]
    res["symmetry_pooled"] = dict(n_molecules=len(sp), median_spread_ratio=float(np.median(sp)) if sp else None, mean_spread_ratio=float(np.mean(sp)) if sp else None,
                                  pooled_ratio=float(np.sqrt(np.sum([v["within_rms"] ** 2 * v["n_pairs_classed"] for v in res["symmetry"].values()]) / np.sum([v["total_rms"] ** 2 * v["n_pairs_classed"] for v in res["symmetry"].values()]))) if sp else None)
    json.dump(res, open(out_prefix + "_dump.json", "w"), indent=1, default=float)
    md = ["# E11 dump — seed-0 model at the full pool", "", f"**E11.2 symmetry:** {res['symmetry_pooled']}", "", "**E11.6 size slope:** " + json.dumps(res["size_slope"]), "",
          "## E11.7 error per pair class (RMS of prediction error / RMS of the true ΔF entries)", "", "| hold-out | class | n | rms error | rms true | ratio |", "|---|---|---|---|---|---|"]
    for h, d in res["pair_class_rms"].items():
        for c, v in d.items():
            md.append(f"| {h} | {c} | {v['n']} | {v['rms_error']:.4f} | {v['rms_true']:.4f} | {v['rms_error'] / v['rms_true'] if v['rms_true'] else float('nan'):.2f} |")
    md += ["", "## E11.3 ring bond–bond pair terms (mean ΔF predicted / true, and B3LYP F_low for orientation; hartree/bohr² units of the internal ΔF)", ""]
    for name, d in res["ring_bond_pairs"].items():
        md.append(f"- **{name}:** " + "; ".join(f"{k}: pred {v['pred'][0]:+.5f} true {v['true'][0]:+.5f} F_low {v['F_low'][0]:+.4f} (n={v['pred'][1]})" for k, v in d.items()))
    open(out_prefix + "_dump.md", "w", encoding="utf-8").write("\n".join(md) + "\n")
    return res
