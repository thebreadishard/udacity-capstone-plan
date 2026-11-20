"""The dry run of probes/g_label_for_step.sh: do the two environments import what the run will call, and is the start geometry
one the runner can read? Nothing is computed.

    python g_label_tools_check.py <geometry.json>     in the pyscf env: pyscf, scipy (the runner's BFGS), numpy
    python g_label_tools_check.py --label             in the vpt2 env with the polyad fork on the path
"""
from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path

FIELD_MODULES = ("pyscf", "scipy.optimize", "numpy")
LABEL_MODULES = ("pyvpt2.fermi_solver", "numpy")
GEOMETRY_KEYS = ("symbols", "coords_bohr")      # what `s1_anharmonic_level.py optimise` reads


def versions(modules: tuple[str, ...]) -> str:
    """Each module imported, with its version where it states one; an ImportError is the caller's failure."""
    found = []
    for name in modules:
        top = importlib.import_module(name.split(".")[0])
        importlib.import_module(name)
        found.append(f"{name} {vars(top).get('__version__', 'imported')}")
    return ", ".join(found)


def atoms_of(geometry: Path) -> int:
    """The number of atoms of a start geometry, refused when it is not the record the runner reads."""
    record = json.loads(geometry.read_text(encoding="utf-8"))
    missing = [k for k in GEOMETRY_KEYS if k not in record]
    if missing:
        raise SystemExit(f"{geometry}: no {', '.join(missing)}; the runner reads {', '.join(GEOMETRY_KEYS)}")
    n = len(record["symbols"])
    if len(record["coords_bohr"]) not in (n, 3 * n):
        raise SystemExit(f"{geometry}: {n} symbols and {len(record['coords_bohr'])} coordinate entries")
    return n


def main(argv: list[str] | None = None) -> int:
    """Print what was found; exit non-zero through the import's or the geometry's own error."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("geometry", nargs="?", type=Path)
    ap.add_argument("--label", action="store_true", help="check the label's environment instead of the force field's")
    a = ap.parse_args(argv)
    if a.label == (a.geometry is not None):
        ap.error("give a geometry (the force field's environment) or --label, not both and not neither")
    if a.label:
        print(f"label tools: {versions(LABEL_MODULES)}", flush=True)
    else:
        n = atoms_of(a.geometry)
        print(f"field tools: {versions(FIELD_MODULES)}; {n} atoms, {3 * n - 6} modes, {2 * (3 * n - 6) + 1} Hessians", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
