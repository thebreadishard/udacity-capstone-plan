"""What does pyscf 2.15.0 change for the pipeline's step 3? (TASKS 225)

`m08/pipeline.py` step 3 runs the label route on `~/qc05/bin/python`, which is pyscf 2.14.0, and the low-mode repair needs 2.15.0:
`corpus/grid_response_blocked.py` refuses anything older, so a molecule with a mode below 20 cm-1 stops the pipeline there. Before the
default moves, this says what else moves with it. 2.15.0 carries the Krylov CPHF fix (pyscf #3384, ours), which the Hessian's own
response uses; the APT's response is refined either way, so that side should barely move.

The comparison is exact in everything but the pyscf version: the fresh run is the same label route on a copy of the same folder, so
the geometry, the grid, the basis and the thresholds are the ones that wrote the stored file.

    python probes/step3_pyscf_check.py <stored label folder> <fresh label folder> --out <folder>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "corpus"))
from vibrations import vibrational_modes  # noqa: E402

LABEL = "hessian_b3lyp_analytic.npz"
APT = "dipole_b3lyp_cphf.npz"   # analytic_hessians.APT_FILE: the name the export and module 08 read


def software(path: Path) -> dict[str, Any]:
    """The software stamp a label file carries, or {} for a file written before the stamp existed."""
    with np.load(path, allow_pickle=False) as z:
        return json.loads(str(z["software"])) if "software" in z.files else {}


def frequencies(folder: Path, geometry: dict) -> tuple[np.ndarray, np.ndarray]:
    """The projected Hessian of a folder's B3LYP label and its frequencies."""
    with np.load(folder / LABEL, allow_pickle=False) as z:
        hessian = np.asarray(z["H_projected"], float)
    modes = vibrational_modes(hessian, np.array(geometry["masses_amu"]), np.array(geometry["coords_bohr"]))
    return hessian, np.asarray(modes.omega_cm, float)


def apt_record(folder: Path) -> dict[str, Any]:
    """The APT and its sum rule, when the folder has one."""
    path = folder / APT
    if not path.is_file():
        return {}
    with np.load(path, allow_pickle=False) as z:
        return {"apt": np.asarray(z["apt"], float), "sum_rule_max": float(z["sum_rule_max"]),
                "intensity_km_mol": np.asarray(z["intensity_km_mol"], float)}


def compare(stored: Path, fresh: Path) -> dict[str, Any]:
    """Everything the two folders differ in, as numbers: the Hessian, the frequencies, the APT and the intensities."""
    geometry = json.loads((stored / "geometry.json").read_text(encoding="utf-8"))
    h_old, w_old = frequencies(stored, geometry)
    h_new, w_new = frequencies(fresh, geometry)
    if h_old.shape != h_new.shape:
        raise ValueError(f"the two Hessians have different shapes, {h_old.shape} and {h_new.shape}: not the same molecule")
    record: dict[str, Any] = {
        "stored": {"folder": str(stored), "software": software(stored / LABEL)},
        "fresh": {"folder": str(fresh), "software": software(fresh / LABEL)},
        "hessian_max_abs_diff": float(np.abs(h_new - h_old).max()),
        "frequency_max_abs_diff_cm": float(np.abs(np.sort(w_new) - np.sort(w_old)).max()),
        "frequency_rms_diff_cm": float(np.sqrt(np.mean((np.sort(w_new) - np.sort(w_old)) ** 2))),
        "lowest_cm": {"stored": float(np.sort(w_old)[0]), "fresh": float(np.sort(w_new)[0])},
    }
    old_apt, new_apt = apt_record(stored), apt_record(fresh)
    if old_apt and new_apt:
        record["apt_max_abs_diff_e"] = float(np.abs(new_apt["apt"] - old_apt["apt"]).max())
        record["sum_rule_max"] = {"stored": old_apt["sum_rule_max"], "fresh": new_apt["sum_rule_max"]}
        record["intensity_max_abs_diff_km_mol"] = float(np.abs(new_apt["intensity_km_mol"] - old_apt["intensity_km_mol"]).max())
    else:
        record["apt"] = "one of the two folders has no APT file"
    return record


def report(record: dict[str, Any]) -> list[str]:
    old, new = record["stored"]["software"].get("pyscf", "?"), record["fresh"]["software"].get("pyscf", "?")
    lines = [f"# Step 3 on pyscf {old} against {new} (TASKS 225)", "",
             "The same label route on the same folder, so the pyscf version is the only difference.", "",
             f"- Hessian, largest element: **{record['hessian_max_abs_diff']:.3e}** hartree/bohr²",
             f"- frequencies, largest shift: **{record['frequency_max_abs_diff_cm']:.4f}** cm⁻¹ "
             f"(rms {record['frequency_rms_diff_cm']:.4f})",
             f"- lowest mode: {record['lowest_cm']['stored']:.2f} → {record['lowest_cm']['fresh']:.2f} cm⁻¹"]
    if "apt_max_abs_diff_e" in record:
        lines += [f"- APT, largest element: **{record['apt_max_abs_diff_e']:.3e}** e",
                  f"- band heights, largest: **{record['intensity_max_abs_diff_km_mol']:.3e}** km/mol",
                  f"- sum rule: {record['sum_rule_max']['stored']:.3e} → {record['sum_rule_max']['fresh']:.3e}"]
    else:
        lines.append(f"- APT: {record['apt']}")
    return lines


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("stored", type=Path, help="the folder whose label file was written by the older pyscf")
    ap.add_argument("fresh", type=Path, help="the folder the label route has just rewritten on the newer one")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    record = compare(a.stored, a.fresh)
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "step3_pyscf_check.json").write_text(json.dumps(record, indent=1), encoding="utf-8")
    lines = report(record)
    (a.out / "step3_pyscf_check.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
