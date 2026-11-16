"""One molecule, one checkpoint: the input tensors' and ΔH's fingerprints, to compare two platforms (read-only).

Usage: platform_diff.py <plan folder> <molecule id> <checkpoint relative to module 05's out/> <out.npz>
"""
from __future__ import annotations

import platform
import sys
from pathlib import Path

import numpy as np
import torch

PLAN = Path(sys.argv[1]).resolve()
M05 = PLAN / "modules" / "05_support_predictor"
for _p in (M05 / "m05", M05 / "corpus", PLAN / "probes"):
    sys.path.insert(0, str(_p))
import rungC_infer as RI  # noqa: E402
import rungC_train as RT  # noqa: E402

folder = M05 / "corpus" / "molecules" / sys.argv[2]
model, record = RT.load_hybrid_model(M05 / "out" / sys.argv[3])
tensors = RI.input_tensors_of(folder, RT.tensor_config(record))
print(f"{platform.system()} python {platform.python_version()} torch {torch.__version__} numpy {np.__version__} threads {torch.get_num_threads()}")
saved = {}
for key, value in tensors.items():
    if isinstance(value, torch.Tensor):
        array = value.detach().numpy()
        saved[f"in_{key}"] = array
        finite = np.isfinite(array.astype(float)).all()
        print(f"  in {key:<14}{tuple(array.shape)!s:<16}{array.dtype!s:<9} max|x| {np.abs(array.astype(float)).max():.6g} "
              f"sum {array.astype(float).sum():.10g} finite {finite}")
dh = RI.delta_H(model.eval(), tensors).numpy().astype(float)
saved["delta_H"] = dh
print(f"  ΔH max|x| {np.abs(dh).max():.6g}, finite {np.isfinite(dh).all()}")
np.savez(sys.argv[4], **saved)
