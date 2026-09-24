"""E9 post-hoc (NOT pre-registered; 24 September 2026, 22:2x) — the energy-only variant of the neighbourhood probe.

Registered E9 probed whole Hessian columns of the neighbourhood atoms (what gradients give). Coupled-cluster gradients are not available for
LNO methods, so an energy-only label can measure only the near × near block (directional second differences within the neighbourhood).
Variant (d): near × near from ΔH_S (probed), far × far from the core (transferred, rotated), near × far from the core where both atoms are
mapped (ipso/ortho atoms are; substituent atoms are not, their couplings stay zero). Variant (e): as (d) but the near × far block zero.
Same read-outs and radii as E9. Says whether an energy-only route can use the E9 saving.
Usage: python e9_posthoc_block.py <corpus/molecules dir> <out prefix>
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
import e9_core_transfer as E9  # noqa: E402

RING = "ring-ip"


def transfer_all(dHS, dHC, mp, R):
    """The whole ΔH_C carried over wherever both atoms are mapped (near and far alike); unmapped (substituent) atoms zero."""
    N = dHS.shape[0] // 3; rec = np.zeros_like(dHS); inv = {v: k for k, v in mp.items()}
    for a in range(N):
        if a not in inv: continue
        for b in range(N):
            if b not in inv: continue
            rec[3 * a:3 * a + 3, 3 * b:3 * b + 3] = R @ dHC[3 * inv[a]:3 * inv[a] + 3, 3 * inv[b]:3 * inv[b] + 3] @ R.T
    return rec


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("molecules"); ap.add_argument("out_prefix"); a = ap.parse_args(); t0 = time.time()
    mdir = Path(a.molecules)
    man = {r["id"]: r for r in csv.DictReader(open(mdir.parent / "manifest.csv", newline="", encoding="utf-8"))}
    mols = T2.load(mdir); ok = {i: m for i, m in mols.items() if not m["imaginary"]}
    core_id = {man[i]["name"]: i for i in ok if man.get(i, {}).get("layer") == "A" and man[i]["status"] == "done"}
    tr = [i for i in ok if man.get(i, {}).get("layer") == "A"]
    geo = {i: json.load(open(mdir / i / "geometry.json")) for i in ok}
    subs = []
    for i in ok:
        if man.get(i, {}).get("layer") != "A2" or "+" not in man[i]["name"]: continue
        core = man[i]["name"].split("+")[0]
        if core not in core_id: continue
        c = core_id[core]
        am = E9.atom_map(man[c]["smiles"], man[i]["smiles"], np.asarray(geo[c]["coords_bohr"]), np.asarray(geo[i]["coords_bohr"]), geo[c]["symbols"], geo[i]["symbols"])
        if am is not None: subs.append((i, c, am))
    ids = [i for i, _, _ in subs]; res = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "posthoc": True, "n": len(ids), "variants": {}}
    rows = []
    for r in (0, 1, 2, 3, 4):
        P = {"d_block_plus_core_couplings": {}, "e_block_only_far_core": {}, "a_registered_columns": {}}; res_num = {k: [0.0, 0.0] for k in P}; frac = []
        for i, c, (mp, R, subst, D) in subs:
            N = len(geo[i]["symbols"]); dHS = ok[i]["dH_true"]; dHC = ok[c]["dH_true"]
            near = sorted(set(subst) | {x for x in range(N) if min(D[x, s] for s in subst) <= r})
            idx = np.concatenate([np.arange(3 * x, 3 * x + 3) for x in near]); nearset = set(near)
            allC = transfer_all(dHS, dHC, mp, R)                          # core everywhere it is mapped
            d = allC.copy(); d[np.ix_(idx, idx)] = dHS[np.ix_(idx, idx)]  # (d): probed near×near block on top of the transferred core
            far = E9.rebuild(dHS, dHC, mp, R, nearset, True)
            e = far.copy(); e[np.ix_(idx, idx)] = dHS[np.ix_(idx, idx)]   # (e): near×far zero
            a_ = E9.with_probe(far, dHS, near)
            for k, H in (("d_block_plus_core_couplings", d), ("e_block_only_far_core", e), ("a_registered_columns", a_)):
                P[k][i] = T2.K_from_dH(ok[i], H); res_num[k][0] += np.mean((H - dHS) ** 2); res_num[k][1] += np.mean(dHS ** 2)
            frac.append(len(near) / N)
        for k in P:
            out = dict(E6.readout(P[k], ok, ids, tr), **T2.basis_free(P[k], ok, ids)); out["dH_residual_ratio"] = float(np.sqrt(res_num[k][0] / res_num[k][1]))
            out["column_fraction_mean"] = float(np.mean(frac)); res["variants"][f"{k}_r{r}"] = out
            rows.append((r, k, out)); print(f"r={r} {k:28s} residual {out['dH_residual_ratio']:.3f} | ring coupling ratio {out['coupling_ratio']:.2f} | corrected ω RMS {out['corrected_freq_rms']:.2f}", flush=True)
    res["seconds"] = round(time.time() - t0); json.dump(res, open(a.out_prefix + ".json", "w"), indent=1, default=float)
    md = [f"# E9 post-hoc — energy-only variants ({res['date']}; NOT pre-registered; {len(ids)} molecules)", "",
          "(d) near×near probed + the core's ΔH wherever both atoms are mapped; (e) near×near probed + far×far from the core, near×far zero; (a) the registered column probe.", "",
          "| r | variant | ΔH residual ratio | ring coupling ratio | corrected ω RMS (cm⁻¹) |", "|---|---|---|---|---|"]
    for r, k, out in rows:
        md.append(f"| {r} | {k} | {out['dH_residual_ratio']:.3f} | {out['coupling_ratio']:.2f} | **{out['corrected_freq_rms']:.2f}** |")
    open(a.out_prefix + ".md", "w", encoding="utf-8").write("\n".join(md) + "\n"); print("wrote", a.out_prefix, f"in {res['seconds']} s")


if __name__ == "__main__":
    main()
