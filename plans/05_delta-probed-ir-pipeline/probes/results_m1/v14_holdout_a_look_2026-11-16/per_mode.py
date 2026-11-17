"""Per-mode look at one corpus molecule under several saved ΔH models (read-only; one molecule, inference only).

Usage: per_mode.py <plan folder> <molecule id> <label=checkpoint relative to module 05's out/>...
Prints the sorted harmonic wavenumbers of the B3LYP label, the ωB97X label and B3LYP + ΔH per model, the lowest modes and the largest
errors, and each model's RMS error with and without the modes below 100 cm⁻¹.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

PLAN = Path(sys.argv[1]).resolve()
M05 = PLAN / "modules" / "05_support_predictor"
for _p in (M05 / "m05", M05 / "corpus", PLAN / "probes"):
    sys.path.insert(0, str(_p))
import rungC_infer as RI  # noqa: E402
import rungC_train as RT  # noqa: E402
from learning_curve_layerA import normal_modes  # noqa: E402
from model_registry import require_measurement  # noqa: E402

require_measurement([M05 / "out" / arg.split("=", 1)[1] for arg in sys.argv[3:]], "its error on a corpus molecule")   # decision 66

molecule = sys.argv[2]
folder = M05 / "corpus" / "molecules" / molecule
import json  # noqa: E402

stored = json.loads((folder / "geometry.json").read_text(encoding="utf-8"))
masses = np.array(stored["masses_amu"], float)
print(f"{molecule}: {len(masses)} atoms, formula symbols {''.join(sorted(stored['symbols']))}")
with np.load(folder / "hessian_b3lyp_analytic.npz") as z:
    low = np.array(z["H_projected"], float)
with np.load(folder / "hessian_wb97x_analytic.npz") as z:
    high = np.array(z["H_projected"], float)


def freqs(hessian: np.ndarray) -> np.ndarray:
    return np.sort(normal_modes(hessian, masses)[1])


f_low, f_high = freqs(low), freqs(high)
columns = {}
for arg in sys.argv[3:]:
    label, name = arg.split("=", 1)
    model, record = RT.load_hybrid_model(M05 / "out" / name)
    dh = RI.delta_H(model.eval(), RI.input_tensors_of(folder, RT.tensor_config(record))).numpy().astype(float)
    columns[label] = freqs(low + dh)

print(f"{'mode':>4} {'B3LYP':>9} {'wB97X':>9}" + "".join(f"{label:>10}" for label in columns))
for i in range(min(10, len(f_high))):
    print(f"{i:>4} {f_low[i]:>9.2f} {f_high[i]:>9.2f}" + "".join(f"{col[i]:>10.2f}" for col in columns.values()))
print()
for label, col in columns.items():
    err = col - f_high
    worst = np.argsort(-np.abs(err))[:5]
    above = f_high >= 100.0
    print(f"{label}: rms all {np.sqrt(np.mean(err**2)):.2f}, rms of modes >= 100 cm-1 {np.sqrt(np.mean(err[above]**2)):.2f} "
          f"({int((~above).sum())} modes below); worst: "
          + ", ".join(f"#{i} {f_high[i]:.0f}: {err[i]:+.1f}" for i in worst))
