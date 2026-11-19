"""TASKS 287 probe: which network inputs change under a rigid rotation (read-only on m05; stored Hessians only).

Usage: python rotation_probe.py [fix]   ('fix' monkeypatches geomeTRIC's LinearAngle.reset with a geometry-derived reference axis.)
"""
import json
import sys
from pathlib import Path

import numpy as np

PLAN = Path(r"C:\Users\thebr\Documents\CapstonePlan\plans\05_delta-probed-ir-pipeline")
M05 = PLAN / "modules" / "05_support_predictor" / "m05"
CORPUS = PLAN / "modules" / "05_support_predictor" / "corpus" / "molecules"
sys.path.insert(0, str(M05))
import e7_rungB_pairs as RB  # noqa: E402
import e7_t2_sqm as T2  # noqa: E402
from geometric.internal import LinearAngle, PrimitiveInternalCoordinates  # noqa: E402
from geometric.molecule import Molecule  # noqa: E402

MOLS = {"diphenylacetylene": "A_014f8519af", "benzonitrile": "A_3100da3761", "phenylacetylene": "A_a848c04a21",
        "benzene": "A_8448043181", "biphenyl": "A_fdc27f1bd1"}


def invariant_reset(self, xyz):
    """Reference axis from the molecule itself: principal axis of the off-axis atoms' perpendicular second moment."""
    xyz = xyz.reshape(-1, 3)
    ev = xyz[self.c] - xyz[self.a]
    ev = ev / np.linalg.norm(ev)
    T = np.zeros((3, 3))
    m3 = []
    for j in range(len(xyz)):
        r = xyz[j] - xyz[self.b]
        p = r - np.dot(r, ev) * ev
        n = np.linalg.norm(p)
        if n < 1e-3:
            continue
        w = 1.0 / np.dot(r, r)
        T += w * np.outer(p, p)
        m3.append((w, p))
    _vals, vecs = np.linalg.eigh(T)
    e0 = vecs[:, -1]
    skew = sum(w * np.dot(p, e0) ** 3 for w, p in m3)
    if skew < 0:
        e0 = -e0
    self.e0 = e0
    self.stored_dot2 = 0.0


def random_rotation(rng):
    q = rng.normal(size=4)
    q /= np.linalg.norm(q)
    w, x, y, z = q
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def build(symbols, coords):
    M = Molecule()
    M.elem = [s.capitalize() for s in symbols]
    M.xyzs = [coords * T2.BOHR2ANG]
    ic = PrimitiveInternalCoordinates(M, build=True, connect=True, addcart=False)
    xyz = coords.flatten()
    return ic, np.array([float(p.value(xyz)) for p in ic.Internals]), np.asarray(ic.wilsonB(xyz))


def inputs(symbols, coords, H):
    ic, vals, B = build(symbols, coords)
    if PINV == "count":   # aromir's rule: exactly the 3N-6 largest singular values
        U, s, Vt = np.linalg.svd(B, full_matrices=False)
        n = B.shape[1] - 6
        Bp = (Vt[:n].T / s[:n]) @ U[:, :n].T
        F = Bp.T @ H @ Bp
    else:                 # the trainer's T2.to_internal: np.linalg.pinv's default cutoff
        F, _ = T2.to_internal(H, B)
    pairs, pfeat, _pcls, B2 = RB.molecule_pairs(symbols, coords, F)
    if not np.allclose(B, B2, atol=1e-10):
        raise RuntimeError("B of the probe and of molecule_pairs differ")
    return dict(reprs=[repr(p) for p in ic.Internals], vals=vals, B=B, F=F, pairs=pairs, pfeat=pfeat,
                linear=np.array([isinstance(p, LinearAngle) for p in ic.Internals]))


def compare(name, mid, rng, n_rot=5):
    g = json.loads((CORPUS / mid / "geometry.json").read_text(encoding="utf-8"))
    sym = g["symbols"]
    x = np.asarray(g["coords_bohr"], float)
    x = x - x.mean(0)
    with np.load(CORPUS / mid / "hessian_b3lyp_analytic.npz") as a:
        H = np.array(a["H_projected"], float)
    ref = inputs(sym, x, H)
    N = len(sym)
    lin = ref["linear"]
    worst = dict(val_lin=0.0, val_other=0.0, Brow_lin=0.0, Brow_other=0.0, F_lin=0.0, F_other=0.0, Fdiag_lin=0.0,
                 pfeat_prim=0.0, pairfeat=0.0)
    for _ in range(n_rot):
        R = random_rotation(rng)
        Rb = np.kron(np.eye(N), R)
        cur = inputs(sym, x @ R.T, Rb @ H @ Rb.T)
        if cur["reprs"] != ref["reprs"] or not np.array_equal(cur["pairs"], ref["pairs"]):
            raise RuntimeError(f"{name}: primitive set or pair pattern changed under rotation")
        dv = np.abs(cur["vals"] - ref["vals"])
        Bexp = (ref["B"].reshape(len(lin), N, 3) @ R.T).reshape(len(lin), -1)
        dB = np.abs(cur["B"] - Bexp).max(1) / (np.abs(ref["B"]).max(1) + 1e-30)
        dF = np.abs(cur["F"] - ref["F"])
        lin_mask = lin[:, None] | lin[None, :]
        nd = len(RB.PRIM_CLASSES)
        # per-primitive vector: the pair feature's sum and |diff| halves come from it; compare the pair features directly
        dP = np.abs(cur["pfeat"] - ref["pfeat"])
        worst["val_lin"] = max(worst["val_lin"], dv[lin].max(initial=0))
        worst["val_other"] = max(worst["val_other"], dv[~lin].max(initial=0))
        worst["Brow_lin"] = max(worst["Brow_lin"], dB[lin].max(initial=0))
        worst["Brow_other"] = max(worst["Brow_other"], dB[~lin].max(initial=0))
        worst["F_lin"] = max(worst["F_lin"], dF[lin_mask].max(initial=0))
        worst["F_other"] = max(worst["F_other"], dF[~lin_mask].max(initial=0))
        worst["Fdiag_lin"] = max(worst["Fdiag_lin"], np.diag(dF)[lin].max(initial=0))
        pair_lin = lin[ref["pairs"][:, 0]] | lin[ref["pairs"][:, 1]]
        worst["pairfeat"] = max(worst["pairfeat"], dP[~pair_lin].max(initial=0))
        worst["pfeat_prim"] = max(worst["pfeat_prim"], dP[pair_lin].max(initial=0))
        del nd
    Fd = np.diag(ref["F"])[lin]
    print(f"{name:18s} n_lin={int(lin.sum()):2d}  " + "  ".join(f"{k}={v:.2e}" for k, v in worst.items())
          + (f"  F_kk(lin, orig)={np.array2string(Fd, precision=4)}" if lin.any() else ""))


PINV = "count" if "count" in sys.argv else "default"


def main():
    print(f"pinv: {PINV}")
    if "fix" in sys.argv:
        LinearAngle.reset = invariant_reset
        print("== with the geometry-derived reference axis ==")
    else:
        print("== carried (geomeTRIC 1.1.1 lab-axis reference) ==")
    print("pairfeat = max |change| of pair features of pairs WITHOUT a linear angle; pfeat_prim = of pairs WITH one")
    rng = np.random.default_rng(7)
    for name, mid in MOLS.items():
        compare(name, mid, rng)


if __name__ == "__main__":
    main()
