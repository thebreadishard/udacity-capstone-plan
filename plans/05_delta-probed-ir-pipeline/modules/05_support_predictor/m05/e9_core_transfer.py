"""E9 — transfer the core, probe the substituent (pre-registered 24 September 2026,
PreRegistration_2026-09-24_E9_Core_Transfer_Substituent_Probe.md).

For every finished mono-substituted layer-A2 molecule S with parent core C in layer A: the Cartesian correction ΔH_S (ωB97X − B3LYP, projected
Hessians) is rebuilt from (i) its own rows and columns for the atoms within r bonds of the substituent (the probed columns) and (ii) the parent
core's ΔH_C for the remaining far × far block, rotated into S's frame. Nothing is fitted. Read-outs are E6/E7's, pooled; the cost read-out is the
fraction of Hessian columns probed. Variants: transfer + probe (the claim), probe only, transfer only, zero rule, exact.

Usage: python e9_core_transfer.py <corpus/molecules dir> <out prefix> [--radii 0,1,2,3,4]
"""
import argparse
import csv
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import e6_learning_curve as E6  # noqa: E402
import e7_t2_sqm as T2  # noqa: E402

RING = "ring-ip"


def kabsch(P, Q):
    """Rotation R and translation t with R P + t ≈ Q (rows are points)."""
    pc, qc = P.mean(0), Q.mean(0)
    H = (P - pc).T @ (Q - qc); U, _, Vt = np.linalg.svd(H)
    d = np.sign(np.linalg.det(Vt.T @ U.T)); D = np.diag([1, 1, d])
    R = Vt.T @ D @ U.T
    return R, qc - R @ pc


def rdkit_mol(smiles):
    from rdkit import Chem
    return Chem.AddHs(Chem.MolFromSmiles(smiles))


def atom_map(core_smiles, sub_smiles, xC, xS, symC, symS):
    """core atom -> S atom for the heavy atoms (substructure match) and the hydrogens (nearest free H on the mapped heavy atom after alignment).
    Returns (mapping dict, rotation R, substituent atom list, graph distance matrix of S) or None if the atom order does not match RDKit's."""
    from rdkit import Chem
    mC, mS = rdkit_mol(core_smiles), rdkit_mol(sub_smiles)
    if [a.GetSymbol().upper() for a in mC.GetAtoms()] != [s.upper() for s in symC]: return None
    if [a.GetSymbol().upper() for a in mS.GetAtoms()] != [s.upper() for s in symS]: return None
    heavyC = Chem.RemoveHs(mC); heavyS = Chem.RemoveHs(mS)       # heavy-atom indices are unchanged by AddHs/RemoveHs (H appended last)
    match = heavyS.GetSubstructMatch(heavyC)
    if not match or len(match) != heavyC.GetNumAtoms(): return None
    mp = {k: match[k] for k in range(len(match))}
    R, t = kabsch(xC[list(mp.keys())], xS[list(mp.values())])
    xC_al = xC @ R.T + t
    used = set(mp.values())
    for a in mC.GetAtoms():
        if a.GetSymbol() != "H": continue
        heavy = a.GetNeighbors()[0].GetIdx(); target = mp[heavy]
        cands = [n.GetIdx() for n in mS.GetAtomWithIdx(target).GetNeighbors() if n.GetSymbol() == "H" and n.GetIdx() not in used]
        if not cands: continue                                     # the hydrogen the substituent replaced
        j = min(cands, key=lambda c: np.linalg.norm(xS[c] - xC_al[a.GetIdx()]))
        mp[a.GetIdx()] = j; used.add(j)
    subst = [i for i in range(mS.GetNumAtoms()) if i not in used]
    D = Chem.GetDistanceMatrix(mS)
    return mp, R, subst, D


def rebuild(dHS, dHC, mp, R, near, far_ok):
    """ΔH_rec: rows/columns of atoms in `near` from ΔH_S; far×far block from ΔH_C rotated. Atoms neither near nor mapped stay zero (should not occur)."""
    N = dHS.shape[0] // 3; rec = np.zeros_like(dHS)
    inv = {v: k for k, v in mp.items()}
    far = [a for a in range(N) if a not in near and a in inv and far_ok]
    for a in far:
        for b in far:
            rec[3 * a:3 * a + 3, 3 * b:3 * b + 3] = R @ dHC[3 * inv[a]:3 * inv[a] + 3, 3 * inv[b]:3 * inv[b] + 3] @ R.T
    return rec


def with_probe(rec, dHS, near):
    out = rec.copy(); idx = np.concatenate([np.arange(3 * a, 3 * a + 3) for a in near]) if near else np.array([], int)
    out[idx, :] = dHS[idx, :]; out[:, idx] = dHS[:, idx]
    return out


def pooled(P, mols, ids, tr):
    r = dict(E6.readout(P, mols, ids, tr), **T2.basis_free(P, mols, ids))
    return r


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("molecules"); ap.add_argument("out_prefix"); ap.add_argument("--radii", default="0,1,2,3,4")
    a = ap.parse_args(); t0 = time.time(); radii = [int(x) for x in a.radii.split(",")]
    mdir = Path(a.molecules)
    man = {r["id"]: r for r in csv.DictReader(open(mdir.parent / "manifest.csv", newline="", encoding="utf-8"))}
    mols = T2.load(mdir)
    ok = {i: m for i, m in mols.items() if not m["imaginary"]}
    core_id = {man[i]["name"]: i for i in ok if man.get(i, {}).get("layer") == "A" and man[i]["status"] == "done"}
    tr = [i for i in ok if man.get(i, {}).get("layer") == "A"]
    geo = {i: json.load(open(mdir / i / "geometry.json")) for i in ok}
    subs = []; skipped = {}
    for i, m in ok.items():
        if man.get(i, {}).get("layer") != "A2" or "+" not in man[i]["name"]: continue
        core = man[i]["name"].split("+")[0]
        if core not in core_id: skipped[i] = f"core {core} not admitted"; continue
        c = core_id[core]
        am = atom_map(man[c]["smiles"], man[i]["smiles"], np.asarray(geo[c]["coords_bohr"]), np.asarray(geo[i]["coords_bohr"]), geo[c]["symbols"], geo[i]["symbols"])
        if am is None: skipped[i] = "atom order or substructure match failed"; continue
        subs.append((i, c, am))
    print(f"{len(subs)} substituted molecules admitted, {len(skipped)} skipped, {len(core_id)} cores; load {time.time() - t0:.0f} s", flush=True)
    res = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "n_admitted": len(subs), "skipped": skipped, "radii": radii, "variants": {}}
    ids = [i for i, _, _ in subs]
    exact = {i: T2.K_from_dH(ok[i], ok[i]["dH_true"]) for i in ids}
    zero = {i: np.zeros_like(ok[i]["K"]) for i in ids}
    res["variants"]["exact"] = pooled(exact, ok, ids, tr); res["variants"]["zero"] = pooled(zero, ok, ids, tr)
    per_mol = {}
    for r in radii:
        Ps = {"transfer_probe": {}, "probe_only": {}, "transfer_only": {}}; frac = []; nnear = []; resid = {k: [[], []] for k in Ps}
        for i, c, (mp, R, subst, D) in subs:
            N = len(geo[i]["symbols"]); dHS = ok[i]["dH_true"]; dHC = ok[c]["dH_true"]
            near = sorted(set(subst) | {a for a in range(N) if min(D[a, s] for s in subst) <= r}) if subst else []
            far_block = rebuild(dHS, dHC, mp, R, set(near), True)
            recs = {"transfer_probe": with_probe(far_block, dHS, near), "probe_only": with_probe(np.zeros_like(dHS), dHS, near), "transfer_only": far_block}
            for k, H in recs.items():
                Ps[k][i] = T2.K_from_dH(ok[i], H); resid[k][0].append(np.mean((H - dHS) ** 2)); resid[k][1].append(np.mean(dHS ** 2))
            frac.append(len(near) / N); nnear.append(len(near))
            if r == 2:
                per_mol[i] = {"core": man[c]["name"], "substituent": man[i]["name"].split("+")[1], "n_atoms": N, "n_near": len(near)}
        for k in Ps:
            out = pooled(Ps[k], ok, ids, tr)
            out["dH_residual_ratio"] = float(np.sqrt(np.sum(resid[k][0]) / np.sum(resid[k][1])))
            out["column_fraction_mean"] = float(np.mean(frac)); out["n_near_mean"] = float(np.mean(nnear))
            res["variants"][f"{k}_r{r}"] = out
            print(f"r={r} {k:15s} columns {out['column_fraction_mean']:.2f} | ΔH residual {out['dH_residual_ratio']:.3f} | ring coupling ratio {out['coupling_ratio']:.2f} | "
                  f"ring diag {out['diag_rms'][RING]:.2f} | corrected ω RMS {out['corrected_freq_rms']:.2f} (zero rule {out['corrected_freq_rms_zero_rule']:.2f}) | overlap {out['duschinsky_overlap_median']:.3f}", flush=True)
    # per-core and per-substituent corrected-frequency RMS at r = 2, variant (a) — printed for reading, not registered
    r2 = {}
    for i, c, (mp, R, subst, D) in subs:
        N = len(geo[i]["symbols"]); near = sorted(set(subst) | {a for a in range(N) if min(D[a, s] for s in subst) <= 2})
        r2[i] = T2.K_from_dH(ok[i], with_probe(rebuild(ok[i]["dH_true"], ok[c]["dH_true"], mp, R, set(near), True), ok[i]["dH_true"], near))
    groups = {"core": {}, "substituent": {}}
    for i in ids:
        groups["core"].setdefault(per_mol[i]["core"], []).append(i); groups["substituent"].setdefault(per_mol[i]["substituent"], []).append(i)
    for g, d in groups.items():
        res[f"by_{g}_r2"] = {name: dict(n=len(ii), corrected_freq_rms=T2.basis_free({j: r2[j] for j in ii}, ok, ii)["corrected_freq_rms"],
                                    coupling_ratio=E6.readout({j: r2[j] for j in ii}, ok, ii, tr)["coupling_ratio"]) for name, ii in sorted(d.items())}
    res["per_molecule_r2"] = per_mol
    v = res["variants"]["transfer_probe_r2"]
    verdict = "PASS" if v["corrected_freq_rms"] <= 3.3 and v["coupling_ratio"] <= 0.5 else ("FAIL" if v["corrected_freq_rms"] > 6 or v["coupling_ratio"] > 0.8 else "BETWEEN")
    res["verdict_r2"] = verdict; res["seconds"] = round(time.time() - t0)
    Path(a.out_prefix).parent.mkdir(parents=True, exist_ok=True)
    json.dump(res, open(a.out_prefix + ".json", "w"), indent=1, default=float)
    md = [f"# E9 — transfer the core, probe the substituent ({res['date']}); {len(subs)} substituted molecules, {len(core_id)} cores; pre-registered", "",
          f"**Verdict at r = 2, transfer + probe: {verdict}** (pass: corrected ω RMS ≤ 3.3 cm⁻¹ and ring coupling ratio ≤ 0.5; fail: > 6 or > 0.8).", "",
          "| r | variant | columns probed | ΔH residual ratio | ring coupling ratio | ring diag RMS | corrected ω RMS (zero rule) | overlap median |", "|---|---|---|---|---|---|---|---|"]
    for r in radii:
        for k in ("transfer_probe", "probe_only", "transfer_only"):
            x = res["variants"][f"{k}_r{r}"]
            md.append(f"| {r} | {k} | {x['column_fraction_mean']:.2f} | {x['dH_residual_ratio']:.3f} | **{x['coupling_ratio']:.2f}** | {x['diag_rms'][RING]:.2f} | **{x['corrected_freq_rms']:.2f}** ({x['corrected_freq_rms_zero_rule']:.2f}) | {x['duschinsky_overlap_median']:.3f} |")
    x = res["variants"]["exact"]; md.append(f"| — | exact | 1.00 | 0 | {x['coupling_ratio']:.2f} | {x['diag_rms'][RING]:.2f} | {x['corrected_freq_rms']:.2f} | {x['duschinsky_overlap_median']:.3f} |")
    md += ["", "## By core and by substituent at r = 2, transfer + probe (not registered)", "", "| group | n | corrected ω RMS | ring coupling ratio |", "|---|---|---|---|"]
    for g in ("core", "substituent"):
        for name, x in res[f"by_{g}_r2"].items():
            md.append(f"| {name} | {x['n']} | {x['corrected_freq_rms']:.2f} | {x['coupling_ratio']:.2f} |")
    if skipped: md += ["", "Skipped: " + "; ".join(f"{i} ({w})" for i, w in skipped.items())]
    open(a.out_prefix + ".md", "w", encoding="utf-8").write("\n".join(md) + "\n"); print("wrote", a.out_prefix, f"in {res['seconds']} s")


if __name__ == "__main__":
    main()
