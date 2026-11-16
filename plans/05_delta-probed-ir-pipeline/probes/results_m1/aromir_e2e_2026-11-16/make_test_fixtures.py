"""Write aromir's test data for the invariance tests and the per-molecule evaluation pin (TASKS 245: T1.1-T1.3).

    python make_test_fixtures.py <plan folder> <hold-out folder written by holdouts_for_aromir.py> <out folder>

- `stored_<name>.npz` for benzonitrile and biphenyl: the corpus geometry (`symbols`, `coords_bohr`) and its projected analytic
  B3LYP Hessian (`hessian`), in the corpus atom order — what the audit's invariance experiment rotated, mirrored and shuffled.
- `holdout_a_benzene.npz`: benzene as hold-out (a) holds it in aromir's evaluation format (with the ωB97X `reference_hessian`).
Prints, for the pin, what `aromir.evaluation.molecule_errors` gives for that benzene with the bundled release.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import numpy as np
from aromir import evaluation, families, release

STORED = {"benzonitrile": "A_3100da3761", "biphenyl": "A_fdc27f1bd1"}
BENZENE = "A_8448043181"


def main() -> None:
    plan, holdouts, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2]), Path(sys.argv[3])
    corpus = plan / "modules" / "05_support_predictor" / "corpus" / "molecules"
    out.mkdir(parents=True, exist_ok=True)
    for name, molecule_id in STORED.items():
        stored = json.loads((corpus / molecule_id / "geometry.json").read_text(encoding="utf-8"))
        with np.load(corpus / molecule_id / "hessian_b3lyp_analytic.npz") as low:
            hessian = np.array(low["H_projected"], float)
        symbols = np.array([s[0].upper() + s[1:].lower() for s in stored["symbols"]])
        np.savez_compressed(out / f"stored_{name}.npz", symbols=symbols, coords_bohr=np.array(stored["coords_bohr"], float),
                            hessian=hessian)
        print(f"stored_{name}.npz: {molecule_id}, {len(symbols)} atoms")
    (source,) = list((holdouts / "a").glob(f"*_{BENZENE}.npz"))
    shutil.copyfile(source, out / "holdout_a_benzene.npz")
    loaded = release.load(release.bundled())
    errors = evaluation.molecule_errors(evaluation.read(out / "holdout_a_benzene.npz"), loaded)
    for family in families.FAMILIES:
        band = errors.band[np.array(errors.band_family) == family]
        first = errors.first_order[:, np.array(errors.first_order_family) == family]
        print(f"benzene {family:<11}{band.size:>3} bands: band error rms {np.sqrt(np.mean(band**2)):.4f}, largest "
              f"{np.abs(band).max():.4f}; first order per seed " + " ".join(f"{np.sqrt(np.mean(row**2)):.4f}" for row in first))


if __name__ == "__main__":
    main()
