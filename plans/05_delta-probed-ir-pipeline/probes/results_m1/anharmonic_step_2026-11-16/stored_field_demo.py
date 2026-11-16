"""A live certificate with the anharmonic step, from stored files only (16 Nov 2026, TASKS 211, stage 2) — what the certificate reads
like while the pipeline's own GFN2-xTB run on a new molecule is owed (probes/runspecs/anharmonic_field_timing.json).

    python stored_field_demo.py --data-root <plan folder holding the stored results> --out <folder>

It is NOT the production path in one respect, and only one: the force field. The pipeline computes the molecule's GFN2-xTB force
field from its own B3LYP minimum, in its own frame. Here the stored force field of S2's benzene is used instead
(probes/results_m1/s2_xtb_2026-10-18/xtb/A_8448043181/X with its GVPT2 label of 13 Nov), computed from S1's pyscf minimum; its modes
are rotated onto the pipeline's geometry (Kabsch; refused above FRAME_TOLERANCE_BOHR). Everything else is the pipeline's code on a
copy of a stored pipeline result (pipeline_benzene_computed_2026-11-03/benzene: psi4 minimum, pyscf B3LYP Hessian and APT, the
carried network's ΔH): `m08.anharmonic.step`, then `m08.live_certificate`. Writes <out>/benzene/{pipeline.json, anharmonic.json,
certificate.json, certificate.md}.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
PLAN = HERE.parents[2]
sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
from m08 import anharmonic as AN  # noqa: E402
from m08 import live_certificate as LC  # noqa: E402
from m08 import pipeline as P  # noqa: E402
from m08.catalog import Catalog  # noqa: E402

# isort: split
import anharmonic_step as AS  # noqa: E402  (probes/, on the path through m08.pipeline)

RESULT = "probes/results_m1/pipeline_benzene_computed_2026-11-03/benzene"
X_DIR = "probes/results_m1/s2_xtb_2026-10-18/xtb/A_8448043181/X"
X_LABEL = "probes/results_m1/labels_domain_2026-11-13/S2/gvpt2_x/A_8448043181.json"
COPIED = ("pipeline.json", "geometry.json", "hessian_b3lyp_analytic.npz", "correction.npz", "dipole_b3lyp_cphf.npz", "analytic_check.json",
          "result.json")
FRAME_TOLERANCE_BOHR = 0.05


def kabsch(moving: np.ndarray, fixed: np.ndarray) -> tuple[np.ndarray, float]:
    """The rotation R with (moving − centroid) @ R closest to (fixed − centroid), and the rms distance left."""
    a, b = moving - moving.mean(axis=0), fixed - fixed.mean(axis=0)
    u, _, vt = np.linalg.svd(a.T @ b)
    r = u @ np.diag([1.0, 1.0, np.sign(np.linalg.det(u @ vt))]) @ vt
    return r, float(np.sqrt(((a @ r - b) ** 2).sum(axis=1).mean()))


def stored_field(data_root: Path, symbols: list[str], coords: np.ndarray) -> tuple[AS.XtbField, dict]:
    """S2's stored benzene force field with its modes in the pipeline's frame, and how well the two geometries coincide."""
    x_dir = data_root / X_DIR
    field = AS.XtbField.from_folder(str(x_dir), str(data_root / X_LABEL))
    ref = json.loads((x_dir / "ref.json").read_text(encoding="utf-8"))["molecule"]
    if list(ref["symbols"]) != symbols:
        raise SystemExit("the stored force field's atoms are not in the pipeline's order")
    r, left = kabsch(np.array(ref["geometry"], float).reshape(-1, 3), coords)
    if left > FRAME_TOLERANCE_BOHR:
        raise SystemExit(f"the stored force field's geometry is {left:.3f} bohr rms from the pipeline's after rotation")
    n = len(symbols)
    q = np.einsum("nim,ij->njm", field.q.reshape(n, 3, -1), r).reshape(3 * n, -1)
    return AS.XtbField(field.delta, field.marked, q), {"source": X_DIR, "label": X_LABEL, "geometry_rms_bohr": left,
                                                         "note": "a stored field rotated onto the pipeline's frame, not the pipeline's own run"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-root", type=Path, default=PLAN)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    d = (a.out / "benzene").resolve()
    if d.exists():
        raise SystemExit(f"{d} exists: a result is never overwritten")
    d.mkdir(parents=True)
    for name in COPIED:
        shutil.copy2(a.data_root / RESULT / name, d / name)
    rec = json.loads((d / "pipeline.json").read_text(encoding="utf-8"))
    symbols, coords, _ = AN.geometry(d)
    field, source = stored_field(a.data_root, symbols, coords)
    AN.force_field = lambda name, folder, settings: (field, source)      # the one stand-in: the stored field for the WSL run
    with np.load(d / P.CORRECTION) as z:
        dH = z["dH"]
    req = AN.Request(rec["name"], d, rec["admission"]["smiles"], AN.load_artefact(), AN.FieldSettings.of(4, 2, 1536, 120))
    rec["spectra"] = AN.step(req, dH, rec["spectra"])
    rec["seconds"]["anharmonic"] = 0.0
    rec["pipeline_version"] = f"{P.PIPELINE_VERSION} (step 6 added to a {rec['pipeline_version']} result from a stored force field)"
    P.write_json(d / "pipeline.json", rec)
    _, md = LC.write(LC.certificate(d, Catalog()), d)
    print(f"[demo] {md}; {rec['spectra']['anharmonic']['bands']}; geometry rms {source['geometry_rms_bohr']:.4f} bohr", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
