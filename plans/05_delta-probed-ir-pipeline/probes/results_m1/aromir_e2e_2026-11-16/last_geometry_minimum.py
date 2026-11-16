"""Is the geometry at which 3-vinylfuran's second optimisation stopped a minimum? (TASKS 248, step 1)

    python last_geometry_minimum.py <threads> <max memory, MB>

aromir cb01c7c left the saddle point of 3-vinylfuran by 0.1 bohr and optimised again; after 100 steps geomeTRIC had the
energy and the gradient inside GAU_TIGHT and the displacement outside, and aromir kept nothing of that attempt. The last
geometry is in the run's pyscf.log (the last 'New geometry' block, bohr, twelve decimals). This computes aromir's own low
level there (aromir.lowlevel.compute) and measures the soft modes (aromir.repair.repair), as the pipeline would have, and
prints the lowest modes of both Hessians beside the saddle point's. The arrays are saved for the record.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
from aromir import lowlevel, records, repair, vibrations
from aromir.dft import Resources
from aromir.molecule import Geometry

HERE = Path(__file__).parent
LOWEST = 4
ATOM = re.compile(r"^\s*\d+\s+([A-Z][a-z]?)\s+\S+\s+\S+\s+\S+\s+AA\s+(\S+)\s+(\S+)\s+(\S+)\s+Bohr")


def last_geometry(log: str) -> Geometry:
    block = log[log.rindex("New geometry"):].splitlines()[1:]
    atoms = []
    for line in block:
        match = ATOM.match(line)
        if not match:
            break
        atoms.append(match.groups())
    if not atoms:
        raise SystemExit("no geometry after the last 'New geometry'")
    return Geometry(tuple(a[0] for a in atoms), np.array([[float(x) for x in a[1:]] for a in atoms]))


def lowest(hessian: np.ndarray, geometry: Geometry) -> list[float]:
    return np.round(np.sort(vibrations.vibrational_modes(hessian, geometry).wavenumbers)[:LOWEST], 2).tolist()


def main() -> None:
    resources = Resources(threads=int(sys.argv[1]), max_memory_mb=int(sys.argv[2]))
    geometry = last_geometry((HERE / "vinylfuran" / "pyscf.log").read_text(encoding="utf-8"))
    stored = json.loads((HERE / "vinylfuran" / "saddle_point_geometry.json").read_text(encoding="utf-8"))
    saddle = np.array(stored["coords_bohr"], float)
    if tuple(stored["symbols"]) != geometry.symbols:
        raise SystemExit("the log's atoms are not the saddle point's")
    print(f"(LASTGEO) {geometry.n_atoms} atoms; largest distance of an atom from its place at the saddle point: "
          f"{np.linalg.norm(geometry.coords_bohr - saddle, axis=1).max():.4f} bohr", flush=True)
    out = HERE / "vinylfuran_last_geometry"
    out.mkdir(exist_ok=True)
    with (out / "pyscf.log").open("a", encoding="utf-8") as log:
        low = lowlevel.compute(geometry, resources, log)
        print(f"(LASTGEO) energy {low.energy:.10f}; analytic Hessian, lowest {LOWEST}: {lowest(low.hessian, geometry)}", flush=True)
        repaired, record = repair.repair(geometry, low.hessian, resources, log)
    print(f"(LASTGEO) soft modes measured, lowest {LOWEST}: {lowest(repaired, geometry)}; record {record}", flush=True)
    modes = vibrations.vibrational_modes(repaired, geometry)
    print(f"(LASTGEO) imaginary modes with the soft modes measured: {modes.n_imaginary} -> "
          f"{'a minimum' if modes.n_imaginary == 0 else 'not a minimum'}", flush=True)
    records.write_arrays(out / "lowlevel.npz", {"coords_bohr": geometry.coords_bohr, "analytic_hessian": low.hessian,
                                                "hessian": repaired, "polar_tensor": low.polar_tensor,
                                                "energy": np.array(low.energy)})
    print("(LASTGEO) saved", flush=True)


if __name__ == "__main__":
    main()
