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


PREFER_ANALYTIC = "--prefer-analytic" in sys.argv     # 23 Sep 2026: use the pyscf second-route Hessians where both exist (corpus/analytic_hessians.py)
USED_ANALYTIC: list = []
_TMP: list = []


def vib_only(freq):
    """3N−6 vibrational entries by the corpus convention: drop the six nearest zero; imaginary stay negative."""
    f = np.asarray(freq, float); keep = np.argsort(np.abs(f))[6:]
    return np.sort(f[keep])


def effective_dir(mol_dir: Path) -> Path:
    """The directory every feature builder reads. With --prefer-analytic and both second-route files present, a temporary copy of the
    molecule directory in which hessian_<tag>.npz ARE the analytic Hessians, so that tokens (mode vectors, shares) and the target K come
    from the same Hessian — benzene's finite-difference ωB97X Hessian was a 133 cm⁻¹ artefact (23 Sep 2026)."""
    if not (PREFER_ANALYTIC and (mol_dir / "hessian_b3lyp_analytic.npz").exists() and (mol_dir / "hessian_wb97x_analytic.npz").exists()):
        return mol_dir
    import shutil
    import tempfile
    tmp = tempfile.TemporaryDirectory(prefix="release_" + mol_dir.name + "_"); _TMP.append(tmp)
    t = Path(tmp.name) / mol_dir.name; t.mkdir()
    for f in ("geometry.json", "result.json"):
        shutil.copy(mol_dir / f, t / f)
    shutil.copy(mol_dir / "hessian_b3lyp_analytic.npz", t / "hessian_b3lyp.npz")
    shutil.copy(mol_dir / "hessian_wb97x_analytic.npz", t / "hessian_wb97x.npz")
    USED_ANALYTIC.append(mol_dir.name)
    return t


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
    ap.add_argument("--prefer-analytic", action="store_true", help="use hessian_<tag>_analytic.npz (pyscf second route) where both exist (23 Sep 2026)")
    a = ap.parse_args()
    global PREFER_ANALYTIC
    PREFER_ANALYTIC = a.prefer_analytic
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
        dd = effective_dir(d)
        if dd is not d:
            # 24 Sep 2026: with the analytic second route the imaginary-mode rule reads the analytic frequencies, not deck v1's finite-difference
            # counts — sixteen of the corpus's twenty imaginary modes were soft torsions flipped by grid noise (corpus README, 23 Sep)
            n_im = {tag: int((vib_only(np.load(dd / f"hessian_{tag}.npz")["freq_cm"]) < 0).sum()) for tag in ("b3lyp", "wb97x")}
        else:
            n_im = {tag: int(r.get(f"n_imaginary_{tag}", 0)) for tag in ("b3lyp", "wb97x")}
        if n_im["b3lyp"] or n_im["wb97x"]:
            skipped.append((d.name, "imaginary" + (" (analytic route agrees)" if dd is not d else ""), r.get("layer")))
            continue
        base = molecule_features(dd)
        tokens, cls, n_rings = environment_tokens(dd, base)
        K, freq = block_matrix(dd)
        g = json.load(open(d / "geometry.json"))
        rows.append(dict(id=d.name, layer=r.get("layer"), tokens=tokens.astype(np.float32), family=np.array([FAMILIES.index(f) for f in base["family"]]),
                         omega=freq, K=K, charge=int(g.get("charge", 0)), mult=int(g.get("multiplicity", 1)), n_atoms=len(g["symbols"]),
                         deck=hashlib.sha256(json.dumps(r.get("deck"), sort_keys=True).encode()).hexdigest()[:16],
                         sha=dict(b3lyp=sha256(dd / "hessian_b3lyp.npz"), wb97x=sha256(dd / "hessian_wb97x.npz"), analytic_second_route=(dd is not d))))
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
                    skipped=skipped, analytic_second_route=sorted(USED_ANALYTIC), npz_sha256=sha256(Path(str(out) + ".npz")))
    json.dump(manifest, open(str(out) + "_manifest.json", "w", encoding="utf-8"), indent=1)
    print(f"{N} molecules, max {M} modes, d_in {d_in}; families {fam_counts}; skipped {len(skipped)} -> {out}.npz ({Path(str(out) + '.npz').stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
