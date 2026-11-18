"""The error of what aromir ships, on the hold-outs, beside the error its release record prints (TASKS 243).

The release record (`evaluation.json`) holds, per family, each seed's first-order diagonal error averaged over the seeds (the trainer's
`diag_rms`). The product applies the seed-mean ΔH to the B3LYP Hessian and diagonalises. This script measures both with aromir's own
code on stored corpus Hessians (B3LYP and ωB97X analytic labels), for the hold-out sets of the release's source record:

    python product_error.py <plan folder> <out.json> <release folder>

Per set and family, in cm⁻¹: (1) the first-order diagonal error per seed and their mean — the printed quantity; (2) the first-order
diagonal error of the seed-mean ΔH; (3) the error of the corrected band positions of the seed-mean ΔH, each corrected band paired to
the reference band by mode overlap and counted in the family of its B3LYP partner — the product's quantity; (4) the same per seed.
Both in the corpus atom order (the trainer's) and in the order aromir gives the molecule. No quantum chemistry is run.

v1.4's copy of ../aromir_product_error_2026-11-16/product_error.py (18 Nov 2026, decision 66): the release folder is an argument —
for v1.4 the measurement networks converted by make_folders.py — and the sets are those v1.4's licence is read on.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import numpy as np
import torch
from aromir import admission, families, release, spectrum, vibrations
from aromir import geometry as aromir_geometry
from aromir.constants import ANGSTROM_PER_BOHR, WAVENUMBERS_PER_HARTREE
from aromir.molecule import Geometry

PLAN = Path(sys.argv[1]).resolve()
RELEASE = Path(sys.argv[3]).resolve()   # the folder whose networks are read (v1.4: the measurement networks)
M05 = PLAN / "modules" / "05_support_predictor"
CORPUS = M05 / "corpus" / "molecules"
SOURCE = M05 / "out" / "v14" / "E7_rungC_v14s3clean_c00_control_eval_clean_seed0.json"   # names the sets the licence is read on
SETS = ("a8", "b")
FAMILIES = families.FAMILIES
sys.path.insert(0, str(PLAN / "probes"))
from aromir_common import aromir_symbol  # noqa: E402  the probes folder is not a package

torch.set_num_threads(2)


def load(molecule_id: str) -> tuple[Geometry, np.ndarray, np.ndarray]:
    """The stored geometry and the two analytic label Hessians of one corpus molecule."""
    folder = CORPUS / molecule_id
    stored = json.loads((folder / "geometry.json").read_text(encoding="utf-8"))
    geometry = Geometry(tuple(aromir_symbol(s) for s in stored["symbols"]), np.array(stored["coords_bohr"], float))
    hessians = []
    for level in ("b3lyp", "wb97x"):
        with np.load(folder / f"hessian_{level}_analytic.npz") as z:
            hessians.append(np.array(z["H_projected"], float))
    return geometry, hessians[0], hessians[1]


def permuted(geometry: Geometry, hessian: np.ndarray, order: list[int]) -> tuple[Geometry, np.ndarray]:
    index = (3 * np.array(order)[:, None] + np.arange(3)).ravel()
    return geometry.reordered(order), hessian[np.ix_(index, index)]


def aromir_order(geometry: Geometry, scratch: Path) -> list[int]:
    """The atom order aromir gives a molecule read from an xyz file in the corpus order."""
    lines = [str(geometry.n_atoms), "product_error"]
    for symbol, row in zip(geometry.symbols, geometry.coords_bohr * ANGSTROM_PER_BOHR, strict=True):
        lines.append(f"{symbol} {row[0]:.10f} {row[1]:.10f} {row[2]:.10f}")
    path = scratch / "molecule.xyz"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return list(aromir_geometry.canonical_order(admission.parse_xyz(path)))


def first_order(delta: np.ndarray, low: vibrations.Modes, weights: np.ndarray) -> np.ndarray:
    """The first-order shift of every B3LYP mode under a Hessian change, cm⁻¹."""
    weighted = 0.5 * (delta + delta.T) / np.outer(weights, weights)
    eigen_shift = np.einsum("ik,ij,jk->k", low.vectors, weighted, low.vectors)
    return eigen_shift * WAVENUMBERS_PER_HARTREE**2 / (2 * low.wavenumbers)


def molecule_errors(geometry: Geometry, h_low: np.ndarray, h_ref: np.ndarray, rel: release.Release) -> dict:
    """Per estimate (each seed and the seed mean): the family and error of every mode, first order and after diagonalisation."""
    low = vibrations.vibrational_modes(h_low, geometry)
    ref = vibrations.vibrational_modes(h_ref, geometry)
    family = np.array(families.classify(geometry, low))
    weights = vibrations.mass_weights(geometry.masses_amu)
    truth = first_order(h_ref - h_low, low, weights)
    corrections = rel.corrections(geometry, h_low)
    estimates = {"mean": corrections.mean, **{f"seed{k}": d for k, d in enumerate(corrections.per_seed)}}
    out = {}
    for name, delta in estimates.items():
        corrected = vibrations.vibrational_modes(h_low + delta, geometry)
        to_ref = spectrum.partners(corrected, ref)
        to_low = spectrum.partners(corrected, low)
        out[name] = {"family_first": family, "first": first_order(delta, low, weights) - truth,
                     "family_band": family[to_low], "band": corrected.wavenumbers - ref.wavenumbers[to_ref]}
    return out


def rms(parts: list[np.ndarray]) -> float | None:
    values = np.concatenate(parts) if parts else np.array([])
    return float(np.sqrt(np.mean(values**2))) if values.size else None


def bootstrap(per_molecule_errors: list[np.ndarray], line: float = 3.0, draws: int = 4000) -> dict:
    """The set's rms under resampling of whole molecules (modes of one molecule are not independent): the 2.5th and 97.5th percentile
    and the share of draws below the licence line. Seeded; a statement about this hold-out's molecules as a sample, nothing more."""
    rng = np.random.default_rng(20261116)
    sums = np.array([float(np.sum(e**2)) for e in per_molecule_errors])
    counts = np.array([len(e) for e in per_molecule_errors], float)
    picks = rng.integers(0, len(sums), size=(draws, len(sums)))
    drawn = np.sqrt(sums[picks].sum(axis=1) / np.maximum(counts[picks].sum(axis=1), 1.0))
    return {"p2.5": float(np.percentile(drawn, 2.5)), "p97.5": float(np.percentile(drawn, 97.5)),
            "share_below_line": float(np.mean(drawn < line)), "line": line, "draws": draws,
            "largest_single_molecule_rms": float(np.sqrt(np.max(sums / np.maximum(counts, 1.0))))}


def summarise(per_molecule: list[dict]) -> dict:
    """Per estimate and family: the rms over all modes of the set, and the number of modes."""
    table: dict = {}
    for name in per_molecule[0]:
        table[name] = {}
        for fam in FAMILIES:
            first = [m[name]["first"][m[name]["family_first"] == fam] for m in per_molecule]
            band = [m[name]["band"][m[name]["family_band"] == fam] for m in per_molecule]
            table[name][fam] = {"first_order": rms(first), "band": rms(band), "n_modes": int(sum(len(x) for x in first))}
    table["mean_band_bootstrap"] = {fam: bootstrap([m["mean"]["band"][m["mean"]["family_band"] == fam] for m in per_molecule])
                                    for fam in FAMILIES}
    seeds = [n for n in table if n.startswith("seed")]
    table["printed_quantity"] = {fam: float(np.mean([table[s][fam]["first_order"] for s in seeds])) for fam in FAMILIES}
    table["band_seed_average"] = {fam: float(np.mean([table[s][fam]["band"] for s in seeds])) for fam in FAMILIES}
    return table


def main() -> None:
    rel = release.load(RELEASE)
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    record: dict = {"release": RELEASE.name, "source_of_sets": SOURCE.name, "sets": {}}
    with tempfile.TemporaryDirectory() as scratch:
        for key in SETS:
            ids = list(source[key]["per_molecule"])
            by_order: dict[str, list[dict]] = {"corpus": [], "aromir": []}
            same_order, largest_shift = 0, []
            for molecule_id in ids:
                geometry, h_low, h_ref = load(molecule_id)
                order = aromir_order(geometry, Path(scratch))
                same_order += order == list(range(geometry.n_atoms))
                by_order["corpus"].append(molecule_errors(geometry, h_low, h_ref, rel))
                moved, h_low_moved = permuted(geometry, h_low, order)
                _, h_ref_moved = permuted(geometry, h_ref, order)
                by_order["aromir"].append(molecule_errors(moved, h_low_moved, h_ref_moved, rel))
                largest_shift.append(float(np.abs(np.sort(by_order["corpus"][-1]["mean"]["band"])
                                                  - np.sort(by_order["aromir"][-1]["mean"]["band"])).max()))
                print(f"{key} {molecule_id} done", flush=True)
            record["sets"][key] = {"n_molecules": len(ids), "ids": ids, "aromir_order_equals_corpus_order": same_order,
                                   "largest_band_error_change_between_orders_cm": largest_shift,
                                   **{order_name: summarise(rows) for order_name, rows in by_order.items()}}
    out = Path(sys.argv[2])
    temp = out.with_suffix(".tmp")
    temp.write_text(json.dumps(record, indent=1), encoding="utf-8")
    temp.replace(out)
    for key, entry in record["sets"].items():
        print(f"\n=== {key}: {entry['n_molecules']} molecules; aromir's order equals the corpus order for {entry['aromir_order_equals_corpus_order']}")
        for order_name in ("corpus", "aromir"):
            table = entry[order_name]
            print(f"  {order_name} order" + "".join(f"{fam:>12}" for fam in FAMILIES))
            print("    printed quantity      " + "".join(f"{table['printed_quantity'][fam]:>12.2f}" for fam in FAMILIES))
            print("    seed mean, 1st order  " + "".join(f"{table['mean'][fam]['first_order']:>12.2f}" for fam in FAMILIES))
            print("    per seed, bands (avg) " + "".join(f"{table['band_seed_average'][fam]:>12.2f}" for fam in FAMILIES))
            print("    seed mean, bands      " + "".join(f"{table['mean'][fam]['band']:>12.2f}" for fam in FAMILIES))
        print("    modes                 " + "".join(f"{entry['corpus']['mean'][fam]['n_modes']:>12}" for fam in FAMILIES))
        boot = entry["aromir"]["mean_band_bootstrap"]
        print("    seed mean, bands: 95 % interval over molecules "
              + "".join(f"  {fam} {boot[fam]['p2.5']:.2f}-{boot[fam]['p97.5']:.2f}" for fam in FAMILIES))
        print("    share of resamples below 3.0 "
              + "".join(f"  {fam} {boot[fam]['share_below_line']:.2f}" for fam in FAMILIES)
              + "; worst single molecule " + "".join(f"  {fam} {boot[fam]['largest_single_molecule_rms']:.2f}" for fam in FAMILIES))


main()
