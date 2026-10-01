"""Pattern ceiling of the hybrid head, measured without training (1 Oct 2026, Sherlock day, after H5: naphthalene overfits to 0.41 under pattern d).

The hybrid head predicts ΔF only on its pattern pairs and reconstructs ΔH = Bᵀ ΔF B. The best it can ever do on a molecule is the least-squares fit
of a pattern-supported symmetric ΔF to the true ΔH (mass-weighted, as the registered main loss). This probe computes that fit for a family of
patterns on each molecule and reads it out exactly as rung C is read (ring-coupling ratio against the zero rule, corrected ω rms, ΔH residual):

  c  = the registered pattern (diagonal, shared-atom pairs, same-ring bond–bond pairs)        — `e7_rungB_pairs.molecule_pairs(pattern="c")`
  d  = c + pairs whose atom sets are disjoint and joined by one bond                           — `pattern="d"`
  e  = d + pairs whose atom sets are two bonds apart (graph distance 2 between the sets)
  f  = e + three bonds apart
  all = every pair of primitives (the B-reconstruction limit)

    python probes/rungC_pattern_ceiling.py <corpus/molecules> <out_prefix> [--ids A_01f3186607,...] [--holdout-a RECORD.json] [--threads 4]

Without --ids / --holdout-a: the molecules of the hold-outs (a) and (b) of the record given, else benzene, naphthalene, 2-methylnaphthalene, styrene.
"""
import argparse
import json
import sys
import time
from collections import deque
from datetime import datetime
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
M05 = HERE.parent / "modules" / "05_support_predictor" / "m05"
sys.path.insert(0, str(M05))
import e7_rungB_pairs as RB  # noqa: E402
import e7_t2_sqm as T2  # noqa: E402
from learning_curve_layerA_v2_descriptors import bond_graph  # noqa: E402

PATTERNS = ("c", "d", "e", "f", "all")
DEFAULT_IDS = ("A_8448043181", "A_01f3186607", "A_69789470db", "A_8f6ed7c002")
AMU2AU = 1822.888486209


def graph_distances(adj: dict, n: int) -> np.ndarray:
    """All-pairs shortest path lengths on the bond graph (BFS), n×n, -1 when disconnected."""
    D = -np.ones((n, n), dtype=int)
    for s in range(n):
        D[s, s] = 0
        q = deque([s])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if D[s, v] < 0:
                    D[s, v] = D[s, u] + 1
                    q.append(v)
    return D


def pattern_pairs(symbols, coords, F_low, pattern: str) -> tuple[np.ndarray, np.ndarray, list]:
    """(pairs (P, 2) with i <= j, B, atom sets) for the pattern: c and d from the pair builder itself, e/f/all by set distance on the bond graph."""
    if pattern in ("c", "d"):
        pairs, _f, _cls, B, atoms = RB.molecule_pairs(symbols, coords, F_low, return_atoms=True, pattern=pattern)
        return np.asarray(pairs), B, atoms
    pairs_d, _f, _cls, B, atoms = RB.molecule_pairs(symbols, coords, F_low, return_atoms=True, pattern="d")
    K = B.shape[0]
    if pattern == "all":
        iu = np.triu_indices(K)
        return np.stack(iu, 1), B, atoms
    adj = bond_graph([s.capitalize() for s in symbols], coords)
    D = graph_distances(adj, len(symbols))
    limit = {"e": 2, "f": 3}[pattern]
    have = {(int(i), int(j)) for i, j in pairs_d}
    extra = []
    for i in range(K):
        for j in range(i, K):
            if (i, j) in have:
                continue
            dist = min(D[a, b] for a in atoms[i] for b in atoms[j])
            if 0 <= dist <= limit:
                extra.append((i, j))
    pairs = np.array(sorted(have | set(extra)))
    return pairs, B, atoms


def ls_pattern_fit(dH: np.ndarray, B: np.ndarray, pairs: np.ndarray, mw: np.ndarray) -> np.ndarray:
    """Least-squares symmetric ΔF supported on `pairs` such that Bᵀ ΔF B ≈ ΔH in the mass-weighted Frobenius norm. Returns ΔF (K × K)."""
    K = B.shape[0]
    cols = []
    for i, j in pairs:
        E = np.outer(B[i], B[j])
        E = E + E.T if i != j else E
        cols.append((E * mw).ravel())
    A = np.stack(cols, 1)
    x, *_ = np.linalg.lstsq(A, (dH * mw).ravel(), rcond=None)
    dF = np.zeros((K, K))
    for (i, j), v in zip(pairs, x, strict=True):
        dF[i, j] = v
        dF[j, i] = v
    return dF


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("molecules")
    ap.add_argument("out_prefix")
    ap.add_argument("--ids", default=None, help="comma list of corpus ids")
    ap.add_argument("--holdout-a", default=None, help="a rungC_train record: its hold-out (a) and (b) ids are used")
    ap.add_argument("--patterns", default=",".join(PATTERNS))
    a = ap.parse_args()
    t0 = time.time()
    mols = T2.load(Path(a.molecules))
    if a.ids:
        ids = a.ids.split(",")
    elif a.holdout_a:
        rec = json.load(open(a.holdout_a, encoding="utf-8"))
        ids = list(rec["holdout_a"]) + list(rec["holdout_b"])
    else:
        ids = list(DEFAULT_IDS)
    ids = [i for i in ids if i in mols]
    patterns = a.patterns.split(",")
    res = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "ids": ids, "patterns": patterns, "per_molecule": {}, "summary": {}}
    fits = {p: {} for p in patterns}
    for i in ids:
        m = mols[i]
        g = json.load(open(Path(a.molecules) / i / "geometry.json", encoding="utf-8"))
        mm = np.repeat(np.asarray(g["masses_amu"], float) * AMU2AU, 3)
        mw = 1.0 / np.sqrt(np.outer(mm, mm))
        res["per_molecule"][i] = {"name": m.get("name", ""), "n_atoms": len(g["symbols"]), "n_primitives": int(m["B"].shape[0])}
        for p in patterns:
            pairs, B, _atoms = pattern_pairs(g["symbols"], np.asarray(g["coords_bohr"], float), m["F_low"], p)
            if B.shape != m["B"].shape or not np.allclose(B, m["B"], atol=1e-8):
                raise ValueError(f"{i}: pattern builder's B differs from the loader's")
            fits[p][i] = ls_pattern_fit(m["dH_true"], B, pairs, mw)
            r = RB.readouts(mols, [i], ids, lambda j, p=p: fits[p][j])
            res["per_molecule"][i][p] = {"n_pairs": int(len(pairs)), "coupling_ratio": r.get("coupling_ratio"), "corrected_freq_rms": r.get("corrected_freq_rms"),
                                         "dH_residual_ratio": r["dH_residual_ratio"]}
    for p in patterns:
        r = RB.readouts(mols, ids, ids, lambda j, p=p: fits[p][j])
        res["summary"][p] = {"coupling_ratio": r.get("coupling_ratio"), "corrected_freq_rms": r.get("corrected_freq_rms"), "dH_residual_ratio": r["dH_residual_ratio"]}
    res["seconds"] = round(time.time() - t0)
    out = Path(a.out_prefix)
    json.dump(res, open(out.with_suffix(".json"), "w"), indent=1)
    lines = [f"# Pattern ceiling of the hybrid head — least-squares ΔF on each pattern, read as rung C ({res['date']})", "",
             f"{len(ids)} molecules; patterns {patterns}. Pooled read-out:", "",
             "| pattern | ring-coupling ratio | corrected ω rms | ΔH residual ratio |", "|---|---|---|---|"]
    for p in patterns:
        s = res["summary"][p]
        lines.append(f"| {p} | {s['coupling_ratio']:.3f} | {s['corrected_freq_rms']:.2f} | {s['dH_residual_ratio']:.3f} |")
    lines += ["", "Per molecule (ring-coupling ratio; pairs in brackets):", "", "| id | name | atoms | prim. | " + " | ".join(patterns) + " |", "|---|---|---|---|" + "---|" * len(patterns)]
    for i, r in res["per_molecule"].items():
        cells = " | ".join(f"{r[p]['coupling_ratio']:.2f} [{r[p]['n_pairs']}]" if r[p]["coupling_ratio"] == r[p]["coupling_ratio"] else f"— [{r[p]['n_pairs']}]" for p in patterns)
        lines.append(f"| {i} | {r['name']} | {r['n_atoms']} | {r['n_primitives']} | {cells} |")
    lines += ["", f"{res['seconds']} s."]
    out.with_suffix(".md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
