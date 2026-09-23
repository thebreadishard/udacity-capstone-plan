"""E7 / rung B diagnosis of hold-out (a) (23 September 2026, post-hoc): which of the ten layer-A molecules carry the residual, and is it coverage?
Trains the GBT of rung B (deterministic) on (1) the full pool and (2) the layer-A molecules of the pool only, and prints per molecule of (a):
ring coupling ratio, ring diagonal RMS, corrected-frequency RMS, ΔH residual ratio, and the molecule's name/core.
Usage: python e7_rungB_diag_a.py <corpus/molecules dir> [--threads 8]"""
import argparse, csv, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import e6_learning_curve as E6  # noqa: E402
import e7_rungB_pairs as RB  # noqa: E402
import e7_t2_sqm as T2  # noqa: E402
from sklearn.ensemble import HistGradientBoostingRegressor  # noqa: E402

ap = argparse.ArgumentParser(); ap.add_argument("molecules"); ap.add_argument("--threads", type=int, default=8); a = ap.parse_args()
mols = T2.load(a.molecules); test_a, test_b, cores, pool = E6.splits(mols)
mols = {i: m for i, m in mols.items() if not m["imaginary"]}
test_a = [i for i in test_a if i in mols]; pool = [i for i in pool if i in mols]
names = {r["id"]: r["name"] for r in csv.DictReader(open(Path(a.molecules).parent / "manifest.csv", newline="", encoding="utf-8"))}
for i, m in mols.items():
    g = json.load(open(Path(a.molecules) / i / "geometry.json"))
    pairs, X, c, B = RB.molecule_pairs(g["symbols"], np.asarray(g["coords_bohr"]), m["F_low"])
    Bp = np.linalg.pinv(m["B"]); dFmn = Bp.T @ m["dH_true"] @ Bp
    m.update(pairs=pairs, X=X, pc=c, y=np.array([dFmn[i_, j_] for i_, j_ in pairs]))
poolA = [i for i in pool if mols[i]["layer"] == "A"]
print(f"pool {len(pool)} (layer A in pool: {len(poolA)}); hold-out (a): " + ", ".join(f"{i}={names.get(i, '?')}" for i in test_a), flush=True)
for label, tr in (("trained on the full pool", pool), ("trained on layer-A pool only", poolA)):
    X = np.concatenate([mols[i]["X"] for i in tr]); y = np.concatenate([mols[i]["y"] for i in tr])
    gbt = HistGradientBoostingRegressor(max_iter=400, learning_rate=0.08, max_leaf_nodes=63, random_state=0).fit(X, y)
    print(f"\n=== {label} ({len(tr)} molecules)")
    for i in test_a:
        dF = RB.assemble(mols[i], mols[i]["pairs"], gbt.predict(mols[i]["X"]))
        x = RB.readouts(mols, [i], tr, lambda j, dF=dF: dF)
        print(f"  {i} {names.get(i, '?'):22s} layer {mols[i]['layer']} | ring coupling ratio {x['coupling_ratio']:.2f} | ring diag {x['diag_rms']['ring-ip']:6.2f} | corrected ω {x['corrected_freq_rms']:.2f} (zero {x['corrected_freq_rms_zero_rule']:.2f}) | ΔH residual {x['dH_residual_ratio']:.2f}", flush=True)
    x = RB.readouts(mols, test_a, tr, lambda j, gbt=gbt: RB.assemble(mols[j], mols[j]["pairs"], gbt.predict(mols[j]["X"])))
    print(f"  ALL (a): ratio {x['coupling_ratio']:.2f} | ring diag {x['diag_rms']['ring-ip']:.2f} | corrected ω {x['corrected_freq_rms']:.2f} | residual {x['dH_residual_ratio']:.2f}", flush=True)
