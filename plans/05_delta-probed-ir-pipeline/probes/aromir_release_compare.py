"""aromir's network on a release against the trainer's own inference path on the checkpoints it was converted from (TASKS 73).

`probes/aromir_network_golden.py` holds the two codes to the same output on seeded random models. This is the same comparison on the
real weights: for each corpus molecule and each seed, ΔH from `aromir.release` against `rungC_infer.delta_H` on the checkpoint, and
the molecule's `geometry.json` masses against `aromir.constants.ELEMENTS` (a mass difference moves every frequency).

    python probes/aromir_release_compare.py <release folder> <out.json> --models <checkpoint names, in seed order> --ids <corpus ids>

The record is written first; the script then stops with an error when a ΔH differs by more than --tolerance or a mass by more than
1e-9 amu.

Runs in an environment that holds both aromir and this repository's inference path (torch, geomeTRIC, RDKit).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
M05 = PLAN / "modules" / "05_support_predictor"
for _p in (M05 / "m05", M05 / "corpus", PLAN / "probes", PLAN / "src"):
    sys.path.insert(0, str(_p))
import rungC_infer as RI  # noqa: E402  (module 05's code is not a package)
import rungC_train as RT  # noqa: E402
import vibrations as VIB  # noqa: E402
from aromir import release as aromir_release  # noqa: E402
from aromir.constants import ELEMENTS  # noqa: E402
from aromir.molecule import Geometry  # noqa: E402
from aromir_common import aromir_symbol  # noqa: E402

CORPUS = M05 / "corpus" / "molecules"
OUT = M05 / "out"
DELTA_H_TOLERANCE = 1e-6      # hartree/bohr²: single precision leaves about 1e-8 in a ΔH of 5e-2; a wrong seed gives 3e-3
MASS_TOLERANCE_AMU = 1e-9     # a mass difference moves every frequency


def frequencies_cm(hessian: np.ndarray, masses: np.ndarray) -> np.ndarray:
    """Sorted harmonic wavenumbers of a Cartesian Hessian, imaginary ones negative."""
    weights = VIB.mass_weights(masses)
    return np.asarray(VIB.signed_cm(np.linalg.eigvalsh(hessian / np.outer(weights, weights))))


def compare_molecule(molecule_id: str, models: tuple[str, ...], release: aromir_release.Release) -> dict:
    """One molecule: the masses, and per seed the largest element of the two ΔH's difference and what it does to a band."""
    folder = CORPUS / molecule_id
    stored = json.loads((folder / "geometry.json").read_text(encoding="utf-8"))
    symbols = tuple(aromir_symbol(s) for s in stored["symbols"])
    masses = np.array(stored["masses_amu"], float)
    geometry = Geometry(symbols, np.array(stored["coords_bohr"], float))
    with np.load(folder / RI.LOW_HESSIAN) as low:
        hessian = np.array(low["H_projected"], float)
    corrections = release.corrections(geometry, hessian)
    seeds = []
    for model_name, ours in zip(models, corrections.per_seed, strict=True):
        model, record = RT.load_hybrid_model(OUT / model_name)
        theirs = RI.delta_H(model.eval(), RI.input_tensors_of(folder, RT.tensor_config(record))).numpy().astype(float)
        seeds.append({"model": model_name,
                      "max_abs_delta_h": float(np.abs(theirs).max()),
                      "max_abs_difference": float(np.abs(ours - theirs).max()),
                      "max_band_difference_cm": float(np.abs(frequencies_cm(hessian + ours, masses)
                                                             - frequencies_cm(hessian + theirs, masses)).max())})
    return {"id": molecule_id, "n_atoms": len(symbols),
            "max_mass_difference_amu": float(np.abs(masses - geometry.masses_amu).max()),
            "masses_corpus": {s: float(m) for s, m in zip(symbols, masses, strict=True)},
            "masses_aromir": {s: ELEMENTS[s].mass_amu for s in sorted(set(symbols))},
            "seeds": seeds}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("release", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--models", nargs="+", required=True, help="the checkpoints' names in the release's seed order")
    ap.add_argument("--ids", nargs="+", required=True, help="corpus ids")
    ap.add_argument("--tolerance", type=float, default=DELTA_H_TOLERANCE, help="largest allowed |ΔH difference|, hartree/bohr²")
    a = ap.parse_args()
    release = aromir_release.load(a.release)
    if len(a.models) != len(release.networks):
        raise SystemExit(f"{len(a.models)} checkpoints named for a release of {len(release.networks)} seeds")
    record = {"release": a.release.name, "network_version": release.network_version, "tensor_sha256": list(release.tensor_sha256),
              "molecules": [compare_molecule(i, tuple(a.models), release) for i in a.ids]}
    tmp = a.out.with_name(a.out.name + ".tmp")
    tmp.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    os.replace(tmp, a.out)
    for m in record["molecules"]:
        for s in m["seeds"]:
            print(f"{m['id']} ({m['n_atoms']} atoms) {s['model'][-8:]}: max|dH| {s['max_abs_delta_h']:.3e}, "
                  f"max|aromir - trainer| {s['max_abs_difference']:.3e}, bands {s['max_band_difference_cm']:.2e} cm-1; "
                  f"masses differ by at most {m['max_mass_difference_amu']:.2e} amu", flush=True)
    worst = max(s["max_abs_difference"] for m in record["molecules"] for s in m["seeds"])
    worst_mass = max(m["max_mass_difference_amu"] for m in record["molecules"])
    if worst > a.tolerance or worst_mass > MASS_TOLERANCE_AMU:
        raise SystemExit(f"NOT EQUAL: ΔH differs by {worst:.3e} (allowed {a.tolerance:.1e}), masses by {worst_mass:.2e} amu "
                         f"(allowed {MASS_TOLERANCE_AMU:.0e}); the record is in {a.out}")


if __name__ == "__main__":
    main()
