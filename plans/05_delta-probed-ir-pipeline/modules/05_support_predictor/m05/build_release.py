"""Build the module-05 dataset file from the corpus factory's per-molecule results (22 September 2026).

One molecule folder (corpus/molecules/<id>/) holds geometry.json, hessian_b3lyp.npz, hessian_wb97x.npz and result.json. This
script turns every complete folder into the rows the notebook needs and writes one padded npz plus a manifest with checksums:

  ids (N,) str · layer (N,) str · n_modes (N,) · mask (N, M) bool · tokens (N, M, 23) float32 · family (N, M) int (−1 = pad)
  omega_cm (N, M) float32 · K (N, M, M) float32 · charge (N,) int · mult (N,) int

Tokens (per mode, from the B3LYP Hessian only — no high-level information): ω/1000, family one-hot (4), element shares C/H/N/O,
localisation, out-of-plane share, twelve atom-environment classes (`learning_curve_layerA.molecule_features`,
`learning_curve_layerA_v2_descriptors.environment_tokens`). Target (RECIPE amendment of 19 September 2026): the mode-basis
correction matrix K_ij = L_iᵀ ΔH_mw L_j / (2 √(ω_i ω_j)) in cm⁻¹, ΔH = H(ωB97X) − H(B3LYP) mass-weighted, in the B3LYP mode basis;
its diagonal is the first-order shift, the family blocks are what the block head predicts, and the pair label of the original
recipe is s_ij = |K_ij| ≥ θ · max_k |K_kk| (θ = 0.1), derived in the notebook.

Usage: python m05/build_release.py corpus/molecules data/corpus_release/layerA_2026-09-22 [--layer A]
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from learning_curve_layerA import AMU2AU, FAMILIES, HARTREE2CM, molecule_features, normal_modes  # noqa: E402
from learning_curve_layerA_v2_descriptors import environment_tokens  # noqa: E402


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def block_matrix(mol_dir: Path):
    """K (M × M, cm⁻¹) in the B3LYP mode basis, and the low-level ω (cm⁻¹)."""
    g = json.load(open(mol_dir / "geometry.json"))
    masses = np.asarray(g["masses_amu"])
    lo = np.load(mol_dir / "hessian_b3lyp.npz")
    hi = np.load(mol_dir / "hessian_wb97x.npz")
    w, freq, V, _ = normal_modes(lo["H_projected"], masses)
    m = np.repeat(masses * AMU2AU, 3)
    dH = (hi["H_projected"] - lo["H_projected"]) / np.sqrt(np.outer(m, m))
    omega = np.sqrt(np.abs(w))
    K = (V.T @ dH @ V) / (2 * np.sqrt(np.outer(omega, omega))) * HARTREE2CM
    return K.astype(np.float32), freq.astype(np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("molecules")
    ap.add_argument("out_prefix")
    ap.add_argument("--layer", default=None, help="keep only molecules whose result.json layer equals this")
    a = ap.parse_args()
    mdir = Path(a.molecules)
    rows = []
    skipped = []
    for d in sorted(p for p in mdir.iterdir() if p.is_dir()):
        if not all((d / f).exists() for f in ("geometry.json", "hessian_b3lyp.npz", "hessian_wb97x.npz", "result.json")):
            continue
        r = json.load(open(d / "result.json"))
        if r.get("status") != "done" or (a.layer and r.get("layer") != a.layer):
            skipped.append((d.name, r.get("status"), r.get("layer")))
            continue
        if r.get("n_imaginary_b3lyp", 0) or r.get("n_imaginary_wb97x", 0):
            skipped.append((d.name, "imaginary", r.get("layer")))
            continue
        base = molecule_features(d)
        tokens, cls, n_rings = environment_tokens(d, base)
        K, freq = block_matrix(d)
        g = json.load(open(d / "geometry.json"))
        rows.append(dict(id=d.name, layer=r.get("layer"), tokens=tokens.astype(np.float32), family=np.array([FAMILIES.index(f) for f in base["family"]]),
                         omega=freq, K=K, charge=int(g.get("charge", 0)), mult=int(g.get("multiplicity", 1)), n_atoms=len(g["symbols"]),
                         deck=hashlib.sha256(json.dumps(r.get("deck"), sort_keys=True).encode()).hexdigest()[:16], sha=dict(b3lyp=sha256(d / "hessian_b3lyp.npz"), wb97x=sha256(d / "hessian_wb97x.npz"))))
    if not rows:
        raise SystemExit("no complete molecules found")
    N = len(rows)
    M = max(len(r["omega"]) for r in rows)
    d_in = rows[0]["tokens"].shape[1]
    tokens = np.zeros((N, M, d_in), np.float32)
    family = np.full((N, M), -1, np.int64)
    omega = np.zeros((N, M), np.float32)
    K = np.zeros((N, M, M), np.float32)
    mask = np.zeros((N, M), bool)
    for i, r in enumerate(rows):
        n = len(r["omega"])
        tokens[i, :n] = r["tokens"]
        family[i, :n] = r["family"]
        omega[i, :n] = r["omega"]
        K[i, :n, :n] = r["K"]
        mask[i, :n] = True
    out = Path(a.out_prefix)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(str(out) + ".npz", ids=np.array([r["id"] for r in rows]), layer=np.array([r["layer"] for r in rows]),
                        n_modes=np.array([len(r["omega"]) for r in rows]), mask=mask, tokens=tokens, family=family, omega_cm=omega, K=K,
                        charge=np.array([r["charge"] for r in rows]), mult=np.array([r["mult"] for r in rows]), n_atoms=np.array([r["n_atoms"] for r in rows]))
    fam_counts = {F: int((family == k).sum()) for k, F in enumerate(FAMILIES)}
    manifest = dict(built_utc=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"), source=str(mdir), n_molecules=N, max_modes=M, d_in=d_in,
                    token_layout="omega/1000 | family one-hot (4: " + ", ".join(FAMILIES) + ") | shares C,H,N,O | localisation | oop share | 12 environment classes",
                    target="K_ij = L_i^T dH_mw L_j / (2 sqrt(w_i w_j)) in cm-1, B3LYP mode basis, dH = H(wB97X) - H(B3LYP)",
                    families=FAMILIES, mode_counts_per_family=fam_counts, decks=sorted({r["deck"] for r in rows if r["deck"]}),
                    molecules=[dict(id=r["id"], layer=r["layer"], n_atoms=r["n_atoms"], n_modes=len(r["omega"]), sha256=r["sha"]) for r in rows],
                    skipped=skipped, npz_sha256=sha256(Path(str(out) + ".npz")))
    json.dump(manifest, open(str(out) + "_manifest.json", "w", encoding="utf-8"), indent=1)
    print(f"{N} molecules, max {M} modes, d_in {d_in}; families {fam_counts}; skipped {len(skipped)} -> {out}.npz ({Path(str(out) + '.npz').stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
