"""GVPT2 fundamentals from a stored dpir.qff force field (18 Oct 2026; S2 amendment 2, §1) — runs in the WSL env with pyVPT2 (`vpt2`).

    python gvpt2_labels.py <s2_root> --selection <selection.json> [--extra ID=DIR ...] [--setting G|X] --out <dir>

Per molecule: dpir.qff.vpt2 with Martin's threshold (min K 1 cm⁻¹, window 200 cm⁻¹: pyVPT2's FERMI_K_THRESH / FERMI_OMEGA_THRESH defaults)
gives the deperturbed χ and fundamentals; overtone and combination energies follow from χ by the expressions pyVPT2's process_vpt2 uses;
then pyVPT2's own process_fermi_solver builds the Fermi interactions and diagonalises the polyads with fermi_solver (upstream tests:
pyvpt2/tests/test_polyad.py, test_fermi_solver.py, and test_h2co.py with GVPT2 on). Degenerate modes are the pairs of a
two-dimensional irreducible representation of the point group (e8_symmetry.degenerate_pairs; 12 Nov 2026: a 0.5 cm⁻¹ gap had paired
accidental neighbours of asymmetric tops); the quartic constants are averaged over these pairs, and a resonance that touches one is
left deperturbed and named (pyVPT2 handles degeneracy for linear molecules only). Because pyVPT2's polyad builder adds an interaction to
the first polyad that holds one of its states and never merges two polyads, each molecule is also checked for interactions that bridge two
of them; the count is reported (a bridge means a polyad was solved incomplete).

Output: <out>/<id>.json with ω, the DVPT2 (K 1) and GVPT2 fundamentals, the modes the polyads moved, the degenerate resonances skipped,
the bridge count, and the solver's provenance (module path, sha256 of fermi_solver.py). Upstream pyVPT2 2eae571 fails on S2's molecules
(eigenvalue assignment KeyError, unmerged polyads); run with the fork's fix on the path:
    PYTHONPATH=~/pyvpt2-wt-polyad python gvpt2_labels.py …     (branch polyad-assignment-and-merge, eb353ab)
"""
import argparse
import hashlib
import importlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "src"))
from e8_symmetry import degenerate_pairs  # noqa: E402
from s2_label_check import molecule_inputs, reference_modes  # noqa: E402
from s2_read import ReadOptions, load_selection, options_from_args, write_atomic  # noqa: E402

from dpir.qff import symmetry_average, vpt2  # noqa: E402
from dpir.vpt2_domain import as_record, mode_domains  # noqa: E402

FERMI_WINDOW = 200.0     # cm⁻¹, pyVPT2's FERMI_OMEGA_THRESH default
FERMI_MIN_K = 1.0        # cm⁻¹, pyVPT2's FERMI_K_THRESH default (Martin et al. 1995)


def overtones_and_bands(w: np.ndarray, chi: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """First overtones 2ω_i + 6χ_ii + Σ_{j≠i} χ_ij and combination bands ω_i + ω_j + 2χ_ii + 2χ_jj + 2χ_ij + ½Σ_{k≠i,j}(χ_ik + χ_jk), as in
    pyVPT2's process_vpt2 for non-degenerate modes (energies above the ground state, cm⁻¹)."""
    n = len(w)
    d = np.diag(chi)
    off = chi.sum(axis=1) - d
    overtone = 2 * w + 6 * d + off
    band = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            rest = 0.5 * (off[i] - chi[i, j] + off[j] - chi[j, i])
            band[i, j] = band[j, i] = w[i] + w[j] + 2 * d[i] + 2 * d[j] + 2 * chi[i, j] + rest
    return overtone, band


def polyad_bridges(fermi: list) -> int:
    """Interactions that join two polyads already built by pyVPT2's rule (add to the first polyad holding either state; never merge)."""
    polyads: list[set] = []
    bridges = 0
    for k, pair in fermi:
        left, right = (k,), pair
        hits = [p for p in polyads if left in p or right in p]
        if hits:
            hits[0].update((left, right))
            bridges += len(hits) > 1
        else:
            polyads.append({left, right})
    return bridges


def symmetry_pairs(setting_dir: str, omega_cm: np.ndarray) -> list[tuple[int, int]]:
    """The force field's degenerate mode pairs from the point group of its reference record; raises when the record's modes are not the
    force field's."""
    symbols, geom, omega, q = reference_modes(setting_dir)
    if not np.allclose(omega, omega_cm, atol=1e-6):
        raise ValueError(f"{setting_dir}: the reference record's modes are not the force field's")
    return degenerate_pairs(symbols, geom, q, omega)


def gvpt2(w: np.ndarray, p3: np.ndarray, p4_raw: np.ndarray, B: np.ndarray, zeta: np.ndarray, pairs: list[tuple[int, int]]) -> dict:
    """DVPT2 (K 1) and GVPT2 fundamentals of one force field. The semi-diagonal quartic constants are averaged over the symmetry pairs
    (`degenerate_pairs`); resonances touching a pair's mode are not diagonalised. `vpt2_domain` marks the fundamentals the theory cannot
    hold (TASKS 207), measured on the fundamentals this function returns."""
    nu_dep, chi, fermi = vpt2(w, p3, symmetry_average(p4_raw, pairs), B, zeta, FERMI_WINDOW, FERMI_MIN_K)
    degenerate = {i for pair in pairs for i in pair}
    kept = [(k, pair) for k, pair in fermi if not ({k, *pair} & degenerate)]
    overtone, band = overtones_and_bands(w, chi)
    nu = nu_dep.copy()
    moved: list[int] = []
    if kept:
        from pyvpt2.vpt2 import process_fermi_solver
        nu, moved = process_fermi_solver(kept, list(range(len(w))), nu, overtone, band, p3)
    return {"nu_dvpt2": nu_dep, "nu_gvpt2": nu, "moved": sorted(int(i) for i in moved), "n_resonances": len(fermi),
            "skipped_degenerate": [[int(k), [int(x) for x in pair]] for k, pair in fermi if (k, pair) not in kept],
            "polyad_bridges": polyad_bridges(kept), "vpt2_domain": as_record(mode_domains(w, nu, chi))}


def solver_provenance() -> dict:
    """Which fermi_solver.py the labels came from: its path and sha256."""
    path = importlib.import_module("pyvpt2.fermi_solver").__file__
    with open(path, "rb") as fh:
        return {"fermi_solver": path, "sha256": hashlib.sha256(fh.read()).hexdigest()}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("root")
    ap.add_argument("--selection", required=True)
    ap.add_argument("--extra", nargs="*", default=[])
    ap.add_argument("--setting", default="G", help="the setting folder under each molecule (X: amendment 4's GFN2-xTB force fields)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    write_labels(a.root, a.selection, options_from_args(a), a.out)
    return 0


def write_labels(root: str, selection: str, options: ReadOptions, out_dir: str) -> None:
    """One <id>.json per usable molecule of the selection under root (the setting and 'extra' folders as options say), into out_dir."""
    by_scaf, _used, _excluded = load_selection(root, selection, options)
    os.makedirs(out_dir, exist_ok=True)
    provenance = solver_provenance()
    print(f"pyVPT2 polyad solver: {provenance['fermi_solver']} sha256 {provenance['sha256'][:12]}")
    for rec in (m for ms in by_scaf.values() for m in ms):
        arrays, B, zeta = molecule_inputs(rec["dir"])
        pairs = symmetry_pairs(rec["dir"], arrays["omega_cm"])
        r = gvpt2(arrays["omega_cm"], arrays["phi_ijk"], arrays["phi_iijj"], B, zeta, pairs)
        out = {"id": rec["id"], "omega": arrays["omega_cm"].tolist(), "nu_dvpt2_k1": r["nu_dvpt2"].tolist(), "nu_gvpt2": r["nu_gvpt2"].tolist(),
               "moved": r["moved"], "n_resonances": r["n_resonances"], "skipped_degenerate": r["skipped_degenerate"],
               "degenerate_pairs": [list(p) for p in pairs],
               "polyad_bridges": r["polyad_bridges"], "fermi_window": FERMI_WINDOW, "fermi_min_k": FERMI_MIN_K,
               "vpt2_domain": r["vpt2_domain"], "solver": provenance}
        write_atomic(os.path.join(out_dir, f"{rec['id']}.json"), json.dumps(out, indent=1))
        shift = np.abs(np.array(out["nu_gvpt2"]) - np.array(out["nu_dvpt2_k1"]))
        marked = r["vpt2_domain"]["marked"]
        print(f"{rec['id']}: {r['n_resonances']} resonances, {len(r['moved'])} fundamentals moved (max {shift.max():.1f} cm⁻¹), "
              f"{len(pairs)} symmetry pairs, {len(r['skipped_degenerate'])} resonances skipped beside them, {r['polyad_bridges']} polyad bridges"
              + (f"; OUTSIDE VPT2's DOMAIN: modes {marked}" if marked else ""))


if __name__ == "__main__":
    sys.exit(main())
