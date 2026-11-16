"""The singular values of a saved Wilson B and what numpy's default pinv cutoff does with them (read-only).

Usage: pinv_cutoff.py <npz written by platform_diff.py>
"""
import platform
import sys

import numpy as np

with np.load(sys.argv[1]) as z:
    b = z["in_B"].astype(float)
s = np.linalg.svd(b, compute_uv=False)
default_cut = 1e-15 * s[0]
print(f"{platform.system()} numpy {np.__version__}: B {b.shape}, 3N-6 = {b.shape[1] - 6}")
print("  singular values 60..68:", " ".join(f"{v:.3e}" for v in s[60:69]))
print(f"  default cutoff rcond*s_max = {default_cut:.3e}; values kept: {int((s > default_cut).sum())}")
for rcond in (None, 1e-10, 1e-6):
    p = np.linalg.pinv(b) if rcond is None else np.linalg.pinv(b, rcond=rcond)
    print(f"  pinv rcond {rcond}: max|x| {np.abs(p).max():.6g}")
