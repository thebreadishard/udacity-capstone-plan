"""Does a composite anchor depend on how its MP2 rows are combined by symmetry? (20 Oct 2026, azulene.)

The composite build reconstructs each MP2 Hessian from the symmetry-unique rows and averages every row that several operations reach; the
'symmetry spread' it reports is the largest disagreement. Azulene's corpus geometry is C2v only to 2.6e-3 bohr (14 Oct), and its rows'
spread was 1.9e-3 / 1.7e-3 a.u. against 2-3e-5 for the other anchors. This reports the spread of DZ, TZ and of the basis step itself
(TZ - DZ, what enters the composite), and the composite's frequencies with the step averaged (the build) against the step taken from the
first operation that reaches each row: the size of the choice's effect, with the matrices' own difference beside it so a zero is not vacuous.

    python probes/composite_step_symmetry.py <name> <corpus id> <e8 run folder>
"""
import sys
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import cc_composite_full_check as CC  # noqa: E402
import e8_symmetry as SYM  # noqa: E402

ROWS = PLAN / "probes" / "results_m1" / "dfmp2_anchors_2026-10-20"


def blocks(npz: Path, reps) -> dict:
    with np.load(npz) as z:
        return {i: np.stack([z[f"row_{3 * i + d:02d}"] for d in range(3)]) for i in reps}


def first_image(block: dict, ops, n: int) -> np.ndarray:
    """Each row from the first operation that reaches it (no averaging), symmetrised as the build does."""
    H = np.full((3 * n, 3 * n), np.nan)
    for i, rows in block.items():
        Bi = rows.reshape(3, n, 3)
        for R, p in ops:
            j = p[i]
            if not np.isnan(H[3 * j:3 * j + 3]).any():
                continue
            new = np.zeros((3, n, 3))
            for k in range(n):
                new[:, p[k], :] = R @ Bi[:, k, :] @ R.T
            H[3 * j:3 * j + 3] = new.reshape(3, 3 * n)
    return 0.5 * (H + H.T)


def main(name: str, mol_id: str, run: str) -> int:
    with np.load(PLAN / "probes" / "results_m1" / run / "hessian_ccsd_t.npz") as z:
        H = np.asarray(z["H_raw"], float)
        x0 = np.asarray(z["coords_bohr"], float).reshape(-1, 3)
    n = len(x0)
    sym, _, masses = CC.load_geometry(PLAN / "modules" / "05_support_predictor" / "corpus" / "molecules" / mol_id / "geometry.json")
    ops = SYM.point_group_ops(sym, x0)
    _, reps = SYM.unique_displacements(ops, n)
    bdz, btz = blocks(ROWS / f"dfmp2_rows_{name}_ccpvdz.npz", reps), blocks(ROWS / f"dfmp2_rows_{name}_ccpvtz.npz", reps)
    bstep = {i: btz[i] - bdz[i] for i in reps}
    for tag, b in (("DZ", bdz), ("TZ", btz), ("step TZ-DZ", bstep)):
        M, spread = SYM.reconstruct(b, ops, n)
        print(f"{tag:11s} spread {spread:.2e}  rms {np.sqrt(np.mean(M ** 2)):.2e}")
    step_avg = SYM.reconstruct(bstep, ops, n)[0]
    step_avg = 0.5 * (step_avg + step_avg.T)
    step_first = first_image(bstep, ops, n)
    f_avg = CC.frequencies_cm(H + step_avg, masses, x0)
    f_first = CC.frequencies_cm(H + step_first, masses, x0)
    print(f"step averaged vs first image: matrices max |diff| {np.abs(step_avg - step_first).max():.2e} a.u., composite frequencies max "
          f"|diff| {np.abs(f_avg - f_first).max():.2e} cm-1; lowest six {np.round(f_avg[:6], 1)}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    sys.exit(main(*sys.argv[1:]))
