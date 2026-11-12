"""Copies of QFF setting folders whose symmetric quartic constants are averaged over the point group's pairs (TASKS 204, 12 Nov 2026).

Reports written before TASKS 204 averaged phi_iijj_sym over neighbours within 0.5 cm⁻¹. For each setting folder this first recomputes
the stored nu_sym from the stored constants with those gap pairs (it must agree within REPRODUCE_CM, or the folder is refused: the
report's VPT2 settings would not be the ones assumed here; the pairs must also reproduce its phi_iijj_sym), then writes
<out>/<label>/ with ref.json copied and qff_report.npz holding
phi_iijj_sym, chi_sym and nu_sym recomputed over the point group's pairs (dpir.symmetry.degenerate_pairs) and those pairs stored. The
existing reads (probes/s1_anharmonic_level.py compare, probes/s1tz_read.py) then run on the copies unchanged. The pairs are read in the
reference record's unaligned mode basis; an old report aligned its basis inside clusters within 0.5 cm⁻¹, so the pair indices are
checked against that report's ω order only, not its rotation.

    python rewrite_sym_reports.py <out dir> LABEL=SETTING_DIR [LABEL=SETTING_DIR ...] [--fermi-window 200] [--fermi-min-k 0]
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from s2_label_check import molecule_inputs, reference_modes, report_pairs

from dpir.provenance import provenance
from dpir.qff import symmetry_average, vpt2
from dpir.symmetry import degenerate_pairs

REPRODUCE_CM = 1e-6


def rewrite(setting: str, out_dir: str, fermi_window: float, fermi_min_k: float) -> dict:
    """Write the corrected copy of one setting folder; returns the old and new pairs and the largest ν change."""
    arrays, B, zeta = molecule_inputs(setting)
    w, p3, p4 = arrays["omega_cm"], arrays["phi_ijk"], arrays["phi_iijj"]
    gap = report_pairs(arrays)
    old_nu = vpt2(w, p3, symmetry_average(p4, gap), B, zeta, fermi_window, fermi_min_k)[0]
    worst = float(np.abs(old_nu - arrays["nu_sym"]).max())
    if worst > REPRODUCE_CM:
        raise ValueError(f"{setting}: the stored nu_sym is not reproduced with the gap pairs ({worst:.2e} cm⁻¹); other VPT2 settings?")
    symbols, geom, omega, q = reference_modes(setting)
    if not np.allclose(omega, w, atol=1e-6):
        raise ValueError(f"{setting}: the reference record's modes are not the report's")
    pairs = degenerate_pairs(symbols, geom, q, omega)
    p4s = symmetry_average(p4, pairs)
    nu, chi, _ = vpt2(w, p3, p4s, B, zeta, fermi_window, fermi_min_k)
    os.makedirs(out_dir, exist_ok=True)
    shutil.copy2(os.path.join(setting, "ref.json"), os.path.join(out_dir, "ref.json"))
    new = {**arrays, "phi_iijj_sym": p4s, "chi_sym": chi, "nu_sym": nu, "degenerate_pairs": np.array(pairs, dtype=int).reshape(-1, 2)}
    fd, tmp = tempfile.mkstemp(dir=out_dir, suffix=".npz")
    with os.fdopen(fd, "wb") as fh:
        np.savez(fh, **new)
    os.replace(tmp, os.path.join(out_dir, "qff_report.npz"))
    return {"setting": setting, "gap_pairs": gap, "group_pairs": pairs, "max_abs_dnu_sym_cm": float(np.abs(nu - arrays["nu_sym"]).max())}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("out")
    ap.add_argument("settings", nargs="+", help="LABEL=SETTING_DIR")
    ap.add_argument("--fermi-window", type=float, default=200.0)
    ap.add_argument("--fermi-min-k", type=float, default=0.0)
    a = ap.parse_args()
    pairs = [s.split("=", 1) for s in a.settings]
    bad = [s for s, p in zip(a.settings, pairs, strict=True) if len(p) != 2]
    if bad:
        raise SystemExit(f"not LABEL=SETTING_DIR: {bad}")
    log = {label: rewrite(d, os.path.join(a.out, label), a.fermi_window, a.fermi_min_k) for label, d in pairs}
    log["provenance"] = provenance()
    for label, r in ((k, v) for k, v in log.items() if k != "provenance"):
        print(f"{label}: pairs {len(r['gap_pairs'])} (gap) -> {len(r['group_pairs'])} (group), max |Δν_sym| {r['max_abs_dnu_sym_cm']:.3f} cm⁻¹")
    fd, tmp = tempfile.mkstemp(dir=a.out, suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(log, fh, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
    os.replace(tmp, os.path.join(a.out, "rewrite_log.json"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
