"""Write aromir's cross-platform pin of the bundled release's ΔH on one molecule (TASKS 236).

    python make_release_fixture.py <plan folder> <corpus id> <delta_h_windows_before.npz> <fixture.npz>

The fixture holds the corpus molecule (symbols, coordinates in bohr), its projected B3LYP Hessian — the network's input — and each
seed's ΔH as aromir at main (43d93a4, `np.linalg.pinv` at its default cutoff) computed it on Windows with numpy 2.5.1, where that
call was right for this molecule (`delta_h_windows_before.npz`, written by `aromir_delta_h.py`). The script refuses a ΔH that is
not the bounded one.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np

LOW_HESSIAN = "hessian_b3lyp_analytic.npz"   # the file module 05's inference path reads (rungC_infer.LOW_HESSIAN)
LARGEST_SANE = 1.0                           # hartree/bohr²; this molecule's ΔH has max 0.040


def main() -> None:
    plan, molecule_id, reference, target = Path(sys.argv[1]).resolve(), sys.argv[2], Path(sys.argv[3]), Path(sys.argv[4])
    folder = plan / "modules" / "05_support_predictor" / "corpus" / "molecules" / molecule_id
    stored = json.loads((folder / "geometry.json").read_text(encoding="utf-8"))
    symbols = np.array([s[0].upper() + s[1:].lower() for s in stored["symbols"]])
    with np.load(folder / LOW_HESSIAN) as low:
        hessian = np.array(low["H_projected"], float)
    with np.load(reference) as z:
        delta_h = np.array(z[f"{molecule_id}/delta_h"])
    largest = float(np.abs(delta_h).max())
    print(f"{molecule_id}: {len(symbols)} atoms, ΔH {delta_h.shape} {delta_h.dtype}, max|ΔH| {largest:.6f} hartree/bohr²")
    if not np.isfinite(delta_h).all() or largest > LARGEST_SANE:
        raise SystemExit("the reference ΔH is not the bounded one; nothing written")
    tmp = target.with_name(target.name + ".tmp.npz")
    np.savez_compressed(tmp, symbols=symbols, coords_bohr=np.array(stored["coords_bohr"], float), hessian=hessian,
                        delta_h_windows=delta_h)
    os.replace(tmp, target)
    print(f"wrote {target} ({target.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
