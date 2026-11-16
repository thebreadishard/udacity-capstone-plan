"""The benzene certificate of aromir cb01c7c against the one of 15 Nov (aromir 58d2065): positions, heights, licence (read-only).

Usage: compare_with_15nov.py <new certificate.json> <old certificate.json>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np


def bands(certificate: dict) -> list[dict]:
    """The certificate's list of bands, wherever the format keeps it."""
    for value in certificate.values():
        if isinstance(value, list) and value and isinstance(value[0], dict) and any("position" in k or "wavenumber" in k for k in value[0]):
            return value
    raise SystemExit(f"no band list among {list(certificate)}")


def column(rows: list[dict], *names: str) -> np.ndarray:
    key = next((n for n in names if n in rows[0]), None)
    if key is None:
        raise SystemExit(f"none of {names} among {list(rows[0])}")
    return np.array([row[key] for row in rows], float)


new = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
old = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
new_bands, old_bands = bands(new), bands(old)
print("new band keys:", list(new_bands[0]))
print("old band keys:", list(old_bands[0]))
print(f"bands: new {len(new_bands)}, old {len(old_bands)}")
for label, names in (("corrected position", ("position_cm", "position", "corrected_cm", "wavenumber_cm")),
                     ("B3LYP position", ("b3lyp_cm", "b3lyp", "low_cm", "b3lyp_position_cm")),
                     ("height", ("height_km_mol", "height", "intensity_km_mol"))):
    a, b = np.sort(column(new_bands, *names)), np.sort(column(old_bands, *names))
    diff = a - b
    print(f"{label}: largest |difference| {np.abs(diff).max():.3f}, rms {np.sqrt(np.mean(diff**2)):.3f}")
licensed_key = next(k for k in new_bands[0] if "licen" in k)
print("new licensed:", sum(bool(row[licensed_key]) for row in new_bands), "of", len(new_bands),
      "| old licensed:", sum(bool(row[next(k for k in old_bands[0] if 'licen' in k)]) for row in old_bands), "of", len(old_bands))
