"""Is the carried ΔH network's spectrum independent of the atom order and the orientation of its input? A corpus folder's geometry and
B3LYP Hessian are permuted and rotated (a random permutation and rotation, fixed by --seed), the network runs on both folders through the
pipeline's own step (`m08.pipeline.correction`), and the corrected frequencies are compared mode for mode (sorted). Found on 30 Oct 2026:
the pipeline's phenanthrene, optimised from another SMILES writing, differed from the corpus folder by 0.36 cm⁻¹ at B3LYP but up to
2.9 cm⁻¹ after the network — this separates the input's order and orientation from its geometry.

    python probes/network_invariance_check.py <corpus id> ... [--seeds 5] [--what both|permutation|rotation|smiles] [--out <record.json>]

'permutation' is any order; 'smiles' is an order another SMILES writing gives (heavy atoms in any order, then each hydrogen after the
heavy atom it is bonded to, as RDKit's AddHs numbers them) — the case a user of the pipeline meets.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
from m08 import pipeline as P  # noqa: E402
from rungC_intensities import mode_intensities  # noqa: E402  (on the path through m08.pipeline)

WHAT = ("both", "permutation", "rotation", "smiles")


def random_rotation(rng: np.random.Generator) -> np.ndarray:
    q, r = np.linalg.qr(rng.normal(size=(3, 3)))
    q = q * np.sign(np.diag(r))
    return q if np.linalg.det(q) > 0 else -q


def smiles_like_order(symbols: list[str], coords: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Heavy atoms in a random order, then the hydrogens in the order of the heavy atom nearest to each (its bond partner)."""
    heavy = np.array([i for i, s in enumerate(symbols) if s.upper() != "H"])
    hydrogens = [i for i, s in enumerate(symbols) if s.upper() == "H"]
    order = rng.permutation(heavy)
    rank = {a: k for k, a in enumerate(order)}
    partner = {h: int(heavy[np.argmin(np.linalg.norm(coords[heavy] - coords[h], axis=1))]) for h in hydrogens}
    return np.concatenate([order, np.array(sorted(hydrogens, key=lambda h: (rank[partner[h]], h)), dtype=int)])


def transformed(H: np.ndarray, coords: np.ndarray, perm: np.ndarray, R: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(H', x') of the molecule with atom i' = perm[i] and every Cartesian block rotated: x' = R x, H'_ij = R H_perm(i)perm(j) Rᵀ."""
    n = len(perm)
    idx = (3 * perm[:, None] + np.arange(3)[None, :]).ravel()
    big = np.kron(np.eye(n), R)
    return big @ H[np.ix_(idx, idx)] @ big.T, coords[perm] @ R.T


def write_copy(src: Path, dst: Path, perm: np.ndarray, R: np.ndarray) -> None:
    g = json.loads((src / "geometry.json").read_text(encoding="utf-8"))
    with np.load(src / P.RI.LOW_HESSIAN) as z:
        H = z["H_projected"]
    H2, x2 = transformed(H, np.asarray(g["coords_bohr"], float), perm, R)
    g2 = dict(g, symbols=[g["symbols"][i] for i in perm], coords_bohr=x2.tolist(), masses_amu=[g["masses_amu"][i] for i in perm])
    dst.mkdir(parents=True)
    (dst / "geometry.json").write_text(json.dumps(g2), encoding="utf-8")
    np.savez(dst / P.RI.LOW_HESSIAN, H_projected=H2)


def corrected_frequencies(d: Path) -> np.ndarray:
    dH, _ = P.correction(P.carried_models(), d)
    with np.load(d / P.RI.LOW_HESSIAN) as z:
        H = z["H_projected"]
    masses = np.asarray(json.loads((d / "geometry.json").read_text(encoding="utf-8"))["masses_amu"], float)
    return np.sort(mode_intensities(H + dH, masses, np.zeros((3, H.shape[0])))[0]), np.sort(mode_intensities(H, masses, np.zeros((3, H.shape[0])))[0])


def check(mol_id: str, seed: int, what: str = "both") -> dict:
    src = P.CORPUS / mol_id
    g = json.loads((src / "geometry.json").read_text(encoding="utf-8"))
    n = len(g["symbols"])
    rng = np.random.default_rng(seed)
    perm, R = rng.permutation(n), random_rotation(rng)
    if what == "rotation":
        perm = np.arange(n)
    elif what == "permutation":
        R = np.eye(3)
    elif what == "smiles":
        perm, R = smiles_like_order(g["symbols"], np.asarray(g["coords_bohr"], float), rng), np.eye(3)
    with tempfile.TemporaryDirectory() as tmp:
        a, b = Path(tmp) / "as_is", Path(tmp) / "permuted"
        a.mkdir()
        shutil.copy(src / "geometry.json", a)
        shutil.copy(src / P.RI.LOW_HESSIAN, a)
        write_copy(src, b, perm, R)
        net_a, low_a = corrected_frequencies(a)
        net_b, low_b = corrected_frequencies(b)
    return {"molecule": mol_id, "seed": seed, "what": what, "n_atoms": n, "models": [m.name for m in P.carried_models()],
            "b3lyp_max_abs_diff_cm": float(np.abs(low_a - low_b).max()), "network_max_abs_diff_cm": float(np.abs(net_a - net_b).max()),
            "network_rms_diff_cm": float(np.sqrt(np.mean((net_a - net_b) ** 2)))}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("mol_ids", nargs="+")
    ap.add_argument("--seeds", type=int, default=1, help="permutations/rotations per molecule (seeds 0 … n−1)")
    ap.add_argument("--what", choices=WHAT, default="both")
    ap.add_argument("--out", type=Path, default=None, help="write the checks and their summary as a JSON record")
    a = ap.parse_args(argv)
    if a.seeds < 1:
        ap.error("--seeds must be at least 1")
    checks = [check(m, s, a.what) for m in a.mol_ids for s in range(a.seeds)]
    summary = {m: {"max_cm": round(max(c["network_max_abs_diff_cm"] for c in checks if c["molecule"] == m), 2),
                   "rms_max_cm": round(max(c["network_rms_diff_cm"] for c in checks if c["molecule"] == m), 2)} for m in a.mol_ids}
    record = {"what": a.what, "seeds": a.seeds, "summary": summary, "checks": checks}
    if a.out is not None:
        tmp = a.out.with_name(a.out.name + ".tmp")
        tmp.write_text(json.dumps(record, indent=1), encoding="utf-8")
        tmp.replace(a.out)
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
