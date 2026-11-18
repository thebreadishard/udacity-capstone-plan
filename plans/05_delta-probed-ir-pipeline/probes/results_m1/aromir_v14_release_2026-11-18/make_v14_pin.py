"""aromir's platform pin for v1.4: the release networks' ΔH for 4-cyanobiphenyl, computed in WSL (decision 66).

    python make_v14_pin.py <aromir's src folder> <v1.3 pin .npz> <v1.4 release folder> <out .npz>

The input is v1.3's pin (`tests/data/release/delta_h_biphenyl_cn_v1.3.npz`: the molecule at its B3LYP/6-31G* geometry and its
projected B3LYP Hessian); the output adds v1.4's three seeds' ΔH as `delta_h_linux` (Ubuntu in WSL; the Windows Python here has no safetensors). aromir's CI
then checks the same ΔH on its other platforms (`tests/test_bundled_release.py`). No quantum chemistry is run.
"""
from __future__ import annotations

import os
import platform
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(sys.argv[1]).resolve()))
from aromir import release  # aromir from the source folder named above
from aromir.molecule import Geometry


def main() -> None:
    pin, folder, out = Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
    with np.load(pin) as arrays:
        symbols, coords, hessian = arrays["symbols"], arrays["coords_bohr"], arrays["hessian"]
    loaded = release.load(folder)
    corrections = loaded.corrections(Geometry(tuple(str(s) for s in symbols), coords), hessian)
    delta = np.array(corrections.per_seed)
    tmp = out.with_name(out.name + ".tmp.npz")
    np.savez_compressed(tmp, symbols=symbols, coords_bohr=coords, hessian=hessian, delta_h_linux=delta)
    os.replace(tmp, out)
    print(f"{platform.platform()}, numpy {np.__version__}: v{loaded.network_version}, {len(delta)} seeds, largest |ΔH| "
          f"{float(np.abs(delta).max()):.4f}; largest difference to v1.3's pin "
          f"{float(np.abs(delta - np.load(pin)['delta_h_windows']).max()):.4f}", flush=True)


if __name__ == "__main__":
    main()
