"""E10 — measure each environment once, assemble the correction (pre-registered 24 September 2026,
PreRegistration_2026-09-24_E10_Environment_Once_Assembled_Correction.md).

Per substituent X: donor = the admitted host of X with the fewest atoms; every other host of X is a receiver. For a receiver S with parent core
C: ΔH_assembled = the core's ΔH wherever both atoms map to the core (E9 variant (d)), with the near × near block (substituent + ipso + ortho)
replaced by the donor's block, rotated into S's frame. Nothing of S's own ΔH is used. Variants: (a) assembled, (b) own block (ceiling),
(c) core only, zero rule. Read-outs as E6/E7/E9, pooled over receivers.

Usage: python e10_environment_once.py <corpus/molecules dir> <out prefix>
"""
import argparse
import csv
import itertools
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import e6_learning_curve as E6  # noqa: E402
import e7_t2_sqm as T2  # noqa: E402
import e9_core_transfer as E9  # noqa: E402
from e9_posthoc_block import transfer_all  # noqa: E402

RING = "ring-ip"


def neighbourhood(mol_h, subst, coords):
    """(near list, ipso, ortho pair, attach atom, per-atom signature) of a substituted molecule; near = subst ∪ ipso ∪ ortho (E9's r = 2 set)."""
    from rdkit import Chem
    D = Chem.GetDistanceMatrix(mol_h); sset = set(subst)
    attach = [a for a in subst if any(n.GetIdx() not in sset for n in mol_h.GetAtomWithIdx(a).GetNeighbors())]
    assert len(attach) == 1, attach
    attach = attach[0]
    ipso = [n.GetIdx() for n in mol_h.GetAtomWithIdx(attach).GetNeighbors() if n.GetIdx() not in sset]; assert len(ipso) == 1; ipso = ipso[0]
    ortho = [n.GetIdx() for n in mol_h.GetAtomWithIdx(ipso).GetNeighbors() if n.GetIdx() != attach]
    near = sorted(sset | {ipso} | set(ortho))
    sig = {a: (mol_h.GetAtomWithIdx(a).GetSymbol(), a in sset, int(D[ipso, a])) for a in near}
    return near, ipso, ortho, attach, sig


def torsion(mol_h, x, subst, ipso, ortho, attach):
    """Substituent torsion against the ring, folded to [0, 90] degrees: dihedral(ortho[0], ipso, attach, ref) with ref the heaviest substituent atom bonded to attach
    (0 for single-atom substituents, whose block is torsion-free)."""
    nb = [n for n in mol_h.GetAtomWithIdx(attach).GetNeighbors() if n.GetIdx() in set(subst)]
    if not nb: return 0.0
    ref = sorted(nb, key=lambda n: (-n.GetAtomicNum(), n.GetIdx()))[0].GetIdx()
    p0, p1, p2, p3 = x[ortho[0]], x[ipso], x[attach], x[ref]
    b0, b1, b2 = p0 - p1, p2 - p1, p3 - p2; b1n = b1 / np.linalg.norm(b1)
    v = b0 - np.dot(b0, b1n) * b1n; w = b2 - np.dot(b2, b1n) * b1n
    ang = abs(np.degrees(np.arctan2(np.dot(np.cross(b1n, v), w), np.dot(v, w))))
    return float(min(ang, 180.0 - ang))


def match_neighbourhoods(gd, gs):
    """Map donor neighbourhood atoms -> receiver neighbourhood atoms: ipso and attach fixed, both ortho pairings tried, the rest assigned by
    nearest position within (element, in-substituent, distance-from-ipso) classes after a Kabsch alignment; the pairing with the lower RMSD wins.
    Returns (mapping, rotation) or None if the element/class multisets differ."""
    nd, ipd, ortd, attd, sigd = gd["near"], gd["ipso"], gd["ortho"], gd["attach"], gd["sig"]
    ns, ips, orts, atts, sigs = gs["near"], gs["ipso"], gs["ortho"], gs["attach"], gs["sig"]
    if sorted(sigd.values()) != sorted(sigs.values()): return None
    xd, xs = gd["coords"], gs["coords"]; best = None
    for perm in itertools.permutations(orts):
        if len(perm) != len(ortd): return None
        fixed = {ipd: ips, attd: atts, **dict(zip(ortd, perm))}
        R, t = E9.kabsch(xd[list(fixed)], xs[list(fixed.values())]); xd_al = xd @ R.T + t
        mp = dict(fixed); used = set(fixed.values())
        rest = [a for a in nd if a not in fixed]
        for a in sorted(rest, key=lambda a: (sigd[a][2], a)):
            cands = [b for b in ns if b not in used and sigs[b] == sigd[a]]
            if not cands: mp = None; break
            b = min(cands, key=lambda b: np.linalg.norm(xs[b] - xd_al[a])); mp[a] = b; used.add(b)
        if mp is None: continue
        R2, t2 = E9.kabsch(xd[list(mp)], xs[list(mp.values())]); rmsd = float(np.sqrt(np.mean(np.sum((xd[list(mp)] @ R2.T + t2 - xs[list(mp.values())]) ** 2, 1))))
        if best is None or rmsd < best[0]: best = (rmsd, mp, R2)
    return None if best is None else (best[1], best[2], best[0])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("molecules"); ap.add_argument("out_prefix")
    ap.add_argument("--donor", default="smallest", choices=["smallest", "class-smallest", "nearest-torsion"],
                    help="smallest: the registered rule (smallest host of X). POST-HOC (not registered): class-smallest = smallest host within the environment class "
                         "(X + the neighbourhood signature, i.e. ortho elements); nearest-torsion = within the class, the host whose substituent torsion is nearest")
    a = ap.parse_args(); t0 = time.time()
    mdir = Path(a.molecules)
    man = {r["id"]: r for r in csv.DictReader(open(mdir.parent / "manifest.csv", newline="", encoding="utf-8"))}
    mols = T2.load(mdir); ok = {i: m for i, m in mols.items() if not m["imaginary"]}
    core_id = {man[i]["name"]: i for i in ok if man.get(i, {}).get("layer") == "A" and man[i]["status"] == "done"}
    tr = [i for i in ok if man.get(i, {}).get("layer") == "A"]
    geo = {i: json.load(open(mdir / i / "geometry.json")) for i in ok}
    hosts = {}   # id -> dict(core id, atom map, neighbourhood data)
    for i in ok:
        if man.get(i, {}).get("layer") != "A2" or "+" not in man[i]["name"]: continue
        core, X = man[i]["name"].split("+", 1)
        if core not in core_id: continue
        c = core_id[core]; xs = np.asarray(geo[i]["coords_bohr"])
        am = E9.atom_map(man[c]["smiles"], man[i]["smiles"], np.asarray(geo[c]["coords_bohr"]), xs, geo[c]["symbols"], geo[i]["symbols"])
        if am is None: continue
        mp, R, subst, _ = am; mol_h = E9.rdkit_mol(man[i]["smiles"])
        near, ipso, ortho, attach, sig = neighbourhood(mol_h, subst, xs)
        hosts[i] = dict(core=c, mp=mp, R=R, subst=subst, X=X, near=near, ipso=ipso, ortho=ortho, attach=attach, sig=sig, coords=xs, n=len(geo[i]["symbols"]),
                        cls=(X, tuple(sorted(sig.values()))), tors=torsion(mol_h, xs, subst, ipso, ortho, attach))
    by_X = {}
    for i, h in hosts.items(): by_X.setdefault(h["X"], []).append(i)
    donors = {X: sorted(ids, key=lambda i: (hosts[i]["n"], i))[0] for X, ids in by_X.items()}
    by_cls = {}
    for i, h in hosts.items(): by_cls.setdefault(h["cls"], []).append(i)
    def donor_of(i):
        h = hosts[i]
        if a.donor == "smallest": return donors[h["X"]]
        pool = [j for j in by_cls[h["cls"]] if j != i]
        if not pool: return None
        if a.donor == "class-smallest": return sorted(pool, key=lambda j: (hosts[j]["n"], j))[0]
        return sorted(pool, key=lambda j: (abs(hosts[j]["tors"] - h["tors"]), hosts[j]["n"], j))[0]
    used_donors = set()
    P = {"a_assembled": {}, "b_own_block": {}, "c_core_only": {}, "zero": {}}; resid = {k: [0.0, 0.0] for k in P}; skipped = {}; rows = []
    for X, ids in sorted(by_X.items()):
        for i in ids:
            d = donor_of(i)
            if d is None or i == d: skipped[i] = f"{X}: no other host in its environment class" if d is None else f"{X}: donor"; continue
            gd = hosts[d]; used_donors.add(d); gs = hosts[i]; m = match_neighbourhoods(gd, gs)
            if m is None: skipped[i] = f"{X}: neighbourhood differs from donor {man[d]['name']}"; continue
            nmap, Rn, rmsd = m
            dHS, dHC, dHD = ok[i]["dH_true"], ok[gs["core"]]["dH_true"], ok[d]["dH_true"]
            allC = transfer_all(dHS, dHC, gs["mp"], gs["R"])
            asm = allC.copy()
            for ad, as_ in nmap.items():
                for bd, bs in nmap.items():
                    asm[3 * as_:3 * as_ + 3, 3 * bs:3 * bs + 3] = Rn @ dHD[3 * ad:3 * ad + 3, 3 * bd:3 * bd + 3] @ Rn.T
            idx = np.concatenate([np.arange(3 * x, 3 * x + 3) for x in gs["near"]])
            own = allC.copy(); own[np.ix_(idx, idx)] = dHS[np.ix_(idx, idx)]
            for k, H in (("a_assembled", asm), ("b_own_block", own), ("c_core_only", allC), ("zero", np.zeros_like(dHS))):
                P[k][i] = T2.K_from_dH(ok[i], H); resid[k][0] += np.mean((H - dHS) ** 2); resid[k][1] += np.mean(dHS ** 2)
            rows.append(dict(id=i, X=X, donor=man[d]["name"], receiver=man[i]["name"], rmsd_bohr=round(rmsd, 3), n_near=len(gs["near"]), tors_receiver=round(gs["tors"], 1), tors_donor=round(gd["tors"], 1)))
    ids = [r["id"] for r in rows]
    res = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "n_receivers": len(ids), "n_hosts": len(hosts), "donors": {X: man[d]["name"] for X, d in donors.items()},
           "skipped": skipped, "donor_rule": a.donor, "n_environment_classes": len(by_cls),
           "cost": {"molecules_in_layer": len(hosts), "measurements_under_claim": len(core_id) + (len(donors) if a.donor == "smallest" else len(used_donors)), "cores": len(core_id), "donors": len(donors) if a.donor == "smallest" else len(used_donors)}, "variants": {}}
    for k in P:
        out = dict(E6.readout(P[k], ok, ids, tr), **T2.basis_free(P[k], ok, ids)); out["dH_residual_ratio"] = float(np.sqrt(resid[k][0] / resid[k][1])); res["variants"][k] = out
        print(f"{k:14s} residual {out['dH_residual_ratio']:.3f} | ring coupling ratio {out['coupling_ratio']:.2f} | ring diag {out['diag_rms'][RING]:.2f} | corrected ω RMS {out['corrected_freq_rms']:.2f} | overlap {out['duschinsky_overlap_median']:.3f}", flush=True)
    v = res["variants"]["a_assembled"]
    res["verdict"] = "PASS" if v["corrected_freq_rms"] <= 3.3 and v["coupling_ratio"] <= 0.5 else ("FAIL" if v["corrected_freq_rms"] > 6 or v["coupling_ratio"] > 0.8 else "BETWEEN")
    groups = {"substituent": {}, "core": {}}
    for r in rows: groups["substituent"].setdefault(r["X"], []).append(r["id"]); groups["core"].setdefault(man[hosts[r["id"]]["core"]]["name"], []).append(r["id"])
    for g, dct in groups.items():
        res[f"by_{g}"] = {name: {k: dict(n=len(ii), corrected_freq_rms=T2.basis_free({j: P[k][j] for j in ii}, ok, ii)["corrected_freq_rms"], coupling_ratio=E6.readout({j: P[k][j] for j in ii}, ok, ii, tr)["coupling_ratio"])
                                 for k in ("a_assembled", "b_own_block")} for name, ii in sorted(dct.items())}
    res["rows"] = rows; res["seconds"] = round(time.time() - t0)
    json.dump(res, open(a.out_prefix + ".json", "w"), indent=1, default=float)
    md = [f"# E10 — measure each environment once, assemble the correction ({res['date']}); donor rule `{a.donor}`{'' if a.donor == 'smallest' else ' (POST-HOC, not registered)'}; {len(ids)} receivers, {res['cost']['donors']} donors, {len(skipped)} skipped, {len(by_cls)} environment classes", "",
          f"**Verdict, variant (a) assembled: {res['verdict']}** (pass ≤ 3.3 cm⁻¹ and ratio ≤ 0.5; fail > 6 or > 0.8). Measurements the layer needs under the claim: {res['cost']['measurements_under_claim']} ({res['cost']['cores']} cores + {res['cost']['donors']} donors) for {len(hosts)} molecules.", "",
          "| variant | ΔH residual ratio | ring coupling ratio | ring diag RMS | corrected ω RMS (cm⁻¹) | overlap median |", "|---|---|---|---|---|---|"]
    for k in ("a_assembled", "b_own_block", "c_core_only", "zero"):
        x = res["variants"][k]; md.append(f"| {k} | {x['dH_residual_ratio']:.3f} | **{x['coupling_ratio']:.2f}** | {x['diag_rms'][RING]:.2f} | **{x['corrected_freq_rms']:.2f}** | {x['duschinsky_overlap_median']:.3f} |")
    md += ["", "## Per substituent (donor → receivers), assembled vs own block (not registered)", "", "| substituent | donor | receivers | assembled: corrected ω RMS / ratio | own block: corrected ω RMS / ratio |", "|---|---|---|---|---|"]
    for X, x in res["by_substituent"].items():
        md.append(f"| {X} | {res['donors'][X]} | {x['a_assembled']['n']} | {x['a_assembled']['corrected_freq_rms']:.2f} / {x['a_assembled']['coupling_ratio']:.2f} | {x['b_own_block']['corrected_freq_rms']:.2f} / {x['b_own_block']['coupling_ratio']:.2f} |")
    md += ["", "## Per core (not registered)", "", "| core | receivers | assembled: corrected ω RMS / ratio |", "|---|---|---|"]
    for name, x in res["by_core"].items(): md.append(f"| {name} | {x['a_assembled']['n']} | {x['a_assembled']['corrected_freq_rms']:.2f} / {x['a_assembled']['coupling_ratio']:.2f} |")
    if skipped: md += ["", f"Skipped receivers ({len(skipped)}): " + "; ".join(f"{man[i]['name']} ({w})" for i, w in skipped.items())]
    open(a.out_prefix + ".md", "w", encoding="utf-8").write("\n".join(md) + "\n"); print("wrote", a.out_prefix, f"in {res['seconds']} s")


if __name__ == "__main__":
    main()
