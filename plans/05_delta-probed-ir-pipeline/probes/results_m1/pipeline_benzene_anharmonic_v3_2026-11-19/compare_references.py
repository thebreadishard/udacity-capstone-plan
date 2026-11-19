"""Why the registered checks refused the run of 19 Nov 2026 against their default reference, in numbers: the networks and artefact
each result ran, the largest harmonic-position gap of the run to each reference, and the 1655 cm-1 degenerate pair's steps.

    python compare_references.py
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = {
    "run": HERE / "benzene",
    "old reference": HERE.parent / "anharmonic_step_2026-11-16" / "stored_field_demo" / "benzene",
    "new reference": HERE.parent / "anharmonic_reference_v14release_v3_2026-11-19" / "benzene",
}


def networks(rec: dict) -> list[str]:
    """The ΔH network version and kind of every seed a result ran, as its record keeps them."""
    found: list[str] = []

    def walk(node: object) -> None:
        if isinstance(node, dict):
            if "version" in node and ("network_kind" in node or "seed" in node or "checkpoint" in node):
                found.append(f"{node.get('version')}/{node.get('network_kind', 'measurement')}")
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(rec)
    return sorted(set(found))


def main() -> None:
    recs = {k: json.loads((p / "pipeline.json").read_text(encoding="utf-8")) for k, p in RESULTS.items()}
    sticks = {k: sorted(r["spectra"]["network"]["sticks"], key=lambda s: s["omega_cm"]) for k, r in recs.items()}
    for k, r in recs.items():
        art = r["spectra"]["anharmonic"].get("artefact", {}).get("file")
        print(f"{k:14s} networks {networks(r)}  artefact {art}  stepped {r['spectra']['anharmonic']['bands']['stepped']}")
    for k in ("old reference", "new reference"):
        gap = max(abs(a["omega_cm"] - b["omega_cm"]) for a, b in zip(sticks["run"], sticks[k], strict=True))
        print(f"largest harmonic-position gap, run against {k}: {gap:.2f} cm-1")
    for k, ss in sticks.items():
        pair = [s for s in ss if 1640 < s["omega_cm"] < 1720]
        print(f"{k:14s} pair near 1691: " + ", ".join(
            f"ω {s['omega_cm']} Δ {None if s['anharmonic'] is None else s['anharmonic']['delta_anh_cm']}" for s in pair))


if __name__ == "__main__":
    main()
