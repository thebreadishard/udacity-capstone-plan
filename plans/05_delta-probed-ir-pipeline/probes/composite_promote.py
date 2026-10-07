"""The promotion rule of chain 33c (rung C pre-registration, amendment of 7 Oct 2026 07:1x), applied to built composite anchors, and the anchor list
of a read from the registry.

  promote   — a composite built by `cc_composite_full_check.py build` is registered `carried` (tier TZ; the molecule's previous carried entry becomes
              superseded) when it is VALID and, for a molecule whose cc-pVDZ anchor is IMAGINARY, its two softest modes lie within 40 cm⁻¹ of ωB97X;
              otherwise it is registered `experimental`. Prints the decision.
      python probes/composite_promote.py promote <composite.npz> <mol_id> <name> <date>
  t3-args   — the --anchor arguments of every carried entry of one tier (the registry refuses anything else in the read anyway).
      python probes/composite_promote.py t3-args TZ
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "m05"))
import anchor_registry as AR  # noqa: E402

SOFT_LINE_CM = 40.0


def decide(build_json: dict, dz_was_imaginary: bool) -> tuple[bool, str]:
    if build_json["status"] != "VALID":
        return False, f"{build_json['n_imaginary']} imaginary mode(s) remain"
    if dz_was_imaginary:
        ref = build_json.get("dft", {}).get("wb97x")
        if ref is None:
            return False, "no ωB97X reference to test the soft modes against"
        d = float(np.abs(np.asarray(build_json["freq_composite"][:2]) - np.asarray(ref[:2])).max())
        if d > SOFT_LINE_CM:
            return False, f"a soft mode {d:.0f} cm⁻¹ from ωB97X (line {SOFT_LINE_CM:.0f})"
        return True, f"VALID; soft modes within {d:.0f} cm⁻¹ of ωB97X"
    return True, "VALID"


def promote(npz: str, mol_id: str, name: str, date: str) -> int:
    rec = json.loads(Path(npz).with_suffix(".json").read_text(encoding="utf-8"))
    entries = AR.load()
    dz_imag = any(e["mol_id"] == mol_id and e["status"] == "imaginary" and e["tier"] == "DZ" for e in entries)
    ok, why = decide(rec, dz_imag)
    soft = ", ".join(f"{v:.0f}" for v in rec["freq_composite"][:2])
    AR.register(dict(mol_id=mol_id, name=name, path=npz, level="CCSD(T)/cc-pVDZ + [MP2/cc-pVTZ − MP2/cc-pVDZ]", tier="TZ", kind="composite",
                     status="experimental", date=date, checks=f"MP2 row symmetry spread {rec['spread']['dz']:.1e} / {rec['spread']['tz']:.1e}; basis step rms "
                     f"{rec['step_rms']:.1e}; softest {soft} cm⁻¹", note=f"chain 33c promotion rule: {why}"), promote=ok)
    print(f"{name}: {'PROMOTED (carried, TZ)' if ok else 'experimental'} — {why}")
    return 0


def t3_args(tier: str) -> int:
    print(" ".join(f"--anchor {e['mol_id']}={(AR.PLAN / e['path']).as_posix()}" for e in AR.load() if e["status"] == "carried" and e["tier"] == tier))
    return 0


if __name__ == "__main__":
    if sys.argv[1] == "promote":
        sys.exit(promote(*sys.argv[2:6]))
    sys.exit(t3_args(sys.argv[2]))
