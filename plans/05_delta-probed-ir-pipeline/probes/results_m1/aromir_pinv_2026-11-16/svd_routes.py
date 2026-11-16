"""The null singular values of a saved Wilson B by the two SVD routes numpy has (TASKS 236; read-only).

`np.linalg.svd(B, compute_uv=False)` and the SVD with vectors that `np.linalg.pinv` uses are different LAPACK paths and need not
agree on values that are rounding residue. This prints both around the rank, and what the default cutoff keeps of each.

    python svd_routes.py <npz written by repro_explosion.py>
"""
from __future__ import annotations

import platform
import sys

import numpy as np

WINDOW = 4


def main() -> None:
    with np.load(sys.argv[1]) as z:
        b = np.array(z["B"], float)
    rank = b.shape[1] - 6
    print(f"{platform.system()} numpy {np.__version__}: B {b.shape}, 3N-6 = {rank}")
    values_only = np.linalg.svd(b, compute_uv=False)
    u, with_vectors, vt = np.linalg.svd(b, full_matrices=False)
    for name, s in (("values only", values_only), ("with vectors (pinv's route)", with_vectors)):
        cutoff = 1e-15 * s[0]
        print(f"  {name}: s[{rank - WINDOW + 1}..{rank + WINDOW}] = " + " ".join(f"{v:.3e}" for v in s[rank - WINDOW:rank + WINDOW]))
        print(f"    default cutoff {cutoff:.3e} keeps {int((s > cutoff).sum())}; largest null value {s[rank:].max():.3e}, "
              f"1/smallest kept {1 / s[s > cutoff].min():.3e}")
    kept = (vt[:rank].T / with_vectors[:rank]) @ u[:, :rank].T
    print(f"  rank-{rank} pseudo-inverse from the SVD with vectors: max|B+| {np.abs(kept).max():.6g}")
    for rcond in (1e-15, 1e-13, 1e-10, 1e-6):
        print(f"  np.linalg.pinv(B, rcond={rcond:g}): max|B+| {np.abs(np.linalg.pinv(b, rcond=rcond)).max():.6g}, "
              f"max|difference to rank-{rank}| {np.abs(np.linalg.pinv(b, rcond=rcond) - kept).max():.3e}")
    try:
        import scipy.linalg
    except ImportError:
        return
    for driver in ("gesdd", "gesvd"):
        s = scipy.linalg.svd(b, compute_uv=True, full_matrices=False, lapack_driver=driver)[1]
        print(f"  scipy {driver} with vectors: first null {s[rank]:.3e}, largest null {s[rank:].max():.3e}")


if __name__ == "__main__":
    main()
