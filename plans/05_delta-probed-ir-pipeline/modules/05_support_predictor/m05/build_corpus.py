#!/usr/bin/env python
"""Module 05 corpus builder (RECIPE.md, 2026-09-12).

Two modes:
  fixture   : read the plan's dry-run stage-A archives (probes/results_dryrun/<mol>/stageA_hessians.npz + stageA.json)
              and write tokens / support labels / manifest -> data/corpus_fixture.npz. Proves the code path only.
  hessianqm9: NOT_RUN until the figshare download (DOI 10.6084/m9.figshare.26363959, 6.29 GB) has the user's
              permission and the B3LYP subset has been recomputed; prints what it expects and exits.
Run:  python build_corpus.py fixture
"""
import hashlib, json, sys
from datetime import datetime
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
PLAN = HERE.parents[2]
DRYRUN = PLAN / "probes" / "results_dryrun"
THETA = 0.1                      # RECIPE label rule: |D2_ij| >= THETA * max_k |D2_kk|  (pilot-note candidate)
FAMILIES = ["CH-oop", "ring-ip", "CH-ip-bend", "CC-stretch", "CH-stretch", "low", "other"]
HARTREE_TO_CM = 219474.63


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def mode_tokens(stage_a: dict, z) -> np.ndarray:
    """Per-mode token features from the low-level DFT result alone (no Δ₂ enters the tokens).
    [omega_cm/1000, family one-hot(7), mass-weighted participation of C, H, N, O, localisation index]"""
    L = z["L"]                                   # (3N, M) mass-weighted normal-mode vectors
    symbols = stage_a["symbols"]
    omega_cm = np.asarray(z["omega_au"]) * HARTREE_TO_CM
    fam = stage_a.get("families", ["other"] * L.shape[1])
    M = L.shape[1]
    tok = np.zeros((M, 1 + len(FAMILIES) + 4 + 1), dtype=np.float32)
    for i in range(M):
        v = L[:, i].reshape(-1, 3)
        w = (v ** 2).sum(axis=1); w = w / w.sum()
        tok[i, 0] = omega_cm[i] / 1000.0
        f = fam[i] if fam[i] in FAMILIES else "other"
        tok[i, 1 + FAMILIES.index(f)] = 1.0
        for k, el in enumerate(["C", "H", "N", "O"]):
            tok[i, 1 + len(FAMILIES) + k] = sum(w[a] for a, s in enumerate(symbols) if s == el)
        tok[i, -1] = float((w ** 2).sum() * len(w))   # inverse participation ratio × N  (1 = fully delocalised)
    return tok


def support_labels(D2Q: np.ndarray, theta: float = THETA) -> np.ndarray:
    d = np.abs(np.diag(D2Q)).max()
    S = (np.abs(D2Q) >= theta * d).astype(np.int8)
    np.fill_diagonal(S, 0)
    return S


def build_fixture():
    out = HERE.parent / "data"; out.mkdir(exist_ok=True)
    mols, arrays, manifest = [], {}, {"built": f"{datetime.now():%Y-%m-%d %H:%M}", "theta": THETA, "mode": "fixture", "molecules": []}
    for d in sorted(DRYRUN.iterdir()):
        npz, js = d / "stageA_hessians.npz", d / "stageA.json"
        if not (npz.exists() and js.exists()):
            continue
        z = np.load(npz); a = json.load(open(js))
        tok = mode_tokens(a, z); S = support_labels(z["D2_direct_Q"])
        key = d.name
        arrays[f"{key}__tokens"] = tok; arrays[f"{key}__labels"] = S; arrays[f"{key}__D2Q"] = z["D2_direct_Q"].astype(np.float32)
        manifest["molecules"].append(dict(name=key, M=int(tok.shape[0]), functionals=a.get("functionals"), basis=a.get("basis"),
                                          positive_pairs=int(S.sum() // 2), possible_pairs=int(tok.shape[0] * (tok.shape[0] - 1) // 2),
                                          source_sha256=sha256(npz)[:16], role="held-out PAH test set (fixture)"))
        mols.append(key)
    np.savez_compressed(out / "corpus_fixture.npz", **arrays)
    json.dump(manifest, open(out / "corpus_fixture_manifest.json", "w"), indent=1)
    print(json.dumps(manifest, indent=1))
    print("written", out / "corpus_fixture.npz")


def hessianqm9():
    print("NOT_RUN: Hessian QM9 (figshare DOI 10.6084/m9.figshare.26363959, v4, 6.29 GB) is not downloaded — the download needs the user's permission;")
    print("the B3LYP/6-31G* subset is not recomputed — its size is fixed by a dated note from the measured Hessian time (RECIPE.md).")
    print("Expected inputs once present: data/hessian_qm9/<index>.{xyz,hessian} (omega-B97x vacuum) and data/b3lyp_subset/<index>/stageA_hessians.npz")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "fixture"
    build_fixture() if mode == "fixture" else hessianqm9()
