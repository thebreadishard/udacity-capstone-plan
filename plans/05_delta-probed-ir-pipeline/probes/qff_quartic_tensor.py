"""The semi-diagonal quartic tensor of a force field assembled before the report stored it (TASKS 209 stage 2).

    python probes/qff_quartic_tensor.py <setting dir: qff_report.npz, hess/> --disp 0.10 [--check-only]

A two-mode block needs φ_iiij and φ_ijjj, which the pair matrix `phi_iijj` cannot hold. Both are slices of φ_ijkk = d²H_ij/dq_k², and
that tensor comes from the very displaced Hessians the rest of the force field was built from — no new quantum chemistry. Reports
written before 13 November 2026 do not carry it, so this rebuilds the force field from the cached Hessians and writes the tensor beside
the report as `qff_quartic_tensor.npz`.

**It verifies before it writes.** The rebuild must reproduce every array the stored report already holds, to REBUILD_TOLERANCE in the
same units; a single mismatch raises and nothing is written, because a tensor that does not belong to the stored force field would be
worse than none. `--check-only` runs that verification and writes nothing.

`--disp` has no default on purpose: the displacement is a property of the run that made the Hessians, not of this tool. S2's force
fields used 0.10 and the assembly's own default is 0.05, so a default here would have written a tensor off by a factor of four — the
verification caught exactly that on 13 November 2026, which is why it runs before every write. The report's own `.md` names the
displacement in its header and in the command line it records.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from dpir.qff import load_results, qff_from_records

REBUILD_TOLERANCE = 1e-6        # cm-1; the rebuild is the same arithmetic on the same files, so only float replay differs
CHECKED = {"omega_cm": "omega_cm", "phi_ijk": "phi3", "phi_iijj": "phi4", "phi_iijj_route_a": "route_a", "phi_iijj_route_b": "route_b"}


def rebuild(setting: Path, disp: float) -> tuple[object, dict[str, float]]:
    """The force field rebuilt from the molecule's Hessian cache, and the largest difference per array against its stored report."""
    report_path = setting / "qff_report.npz"
    if not report_path.is_file():
        raise FileNotFoundError(f"{report_path} is missing")
    cache = setting / "hess"
    if not cache.is_dir():
        raise FileNotFoundError(f"{cache} is missing: without the displaced Hessians the tensor cannot be derived")
    qff, _harm, _ref, _info = qff_from_records(load_results(str(cache)), disp, allow_noisy=True)
    differences = {}
    with np.load(report_path) as stored:
        for name, attribute in CHECKED.items():
            if name not in stored.files:
                raise ValueError(f"{report_path} has no {name}: this is not a report of the same assembly")
            got = np.asarray(getattr(qff, attribute), float)
            if got.shape != stored[name].shape:
                raise ValueError(f"{name}: rebuilt {got.shape}, stored {stored[name].shape}")
            differences[name] = float(np.abs(got - stored[name]).max())
    return qff, differences


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("setting", type=Path, help="the molecule's setting directory (holds qff_report.npz and hess/)")
    ap.add_argument("--disp", type=float, required=True, help="the displacement the force field was built with; the report's .md header "
                                                              "names it, and the rebuild check refuses a wrong one")
    ap.add_argument("--check-only", action="store_true", help="verify the rebuild and write nothing")
    a = ap.parse_args(argv)
    qff, differences = rebuild(a.setting, a.disp)
    for name, worst in differences.items():
        print(f"  {name:20s} max |rebuilt - stored| {worst:.3e} cm-1")
    worst_name = max(differences, key=lambda k: differences[k])
    if differences[worst_name] > REBUILD_TOLERANCE:
        raise SystemExit(f"the rebuild does not reproduce the stored report ({worst_name} off by "
                         f"{differences[worst_name]:.3e} cm-1, over {REBUILD_TOLERANCE:.0e}); the tensor is not written")
    print(f"the rebuild reproduces the stored report (worst {differences[worst_name]:.3e} cm-1)")
    if a.check_only:
        return 0
    out = a.setting / "qff_quartic_tensor.npz"
    temporary = out.with_name(out.name + ".tmp.npz")   # savez appends .npz unless the name already ends in it
    np.savez_compressed(temporary, phi_ijkk=qff.phi_ijkk, omega_cm=qff.omega_cm, disp=np.array(a.disp))
    temporary.replace(out)
    print(f"wrote {out} ({out.stat().st_size / 1e6:.1f} MB, {qff.phi_ijkk.shape})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
