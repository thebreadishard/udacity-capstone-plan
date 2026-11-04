"""Our G-level GVPT2 fundamentals beside PAHdb's anharmonic library v1.00 (S3's comparison outside the verdict; the matching rule of
GoalGathering/notes/PreRegistration_2026-11-02_S3_Route_A_Transfer.md, amendment 5).

The library gives every VPT2 transition (fundamentals, overtones, combinations) as a frequency and an intensity, without assignment or
symmetry. So our side is the IR-active fundamentals in the window (D2h labels b1u, b2u, b3u from the signs of the mode characters, as
probes/hot_band_desk_naphthalene.py labels them) and their side is the transitions at or above an intensity threshold; the two are paired
one to one with the least total |Δν| (scipy's linear_sum_assignment), a pair farther apart than CAP_CM left unpaired. Reported per threshold,
no line and no verdict: the pairs, mean and rms of Δν = ours − theirs, the rms about the mean, and the unpaired on both sides.

    python pahdb_anharmonic_match.py --setting <molecule/G> --uid <PAHdb uid> --xml <library xml> --out <dir>
"""
from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import linear_sum_assignment

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from s2_read import WINDOW, write_atomic  # noqa: E402

IR_ACTIVE = frozenset({"b1u", "b2u", "b3u"})
CAP_CM = 25.0                       # a pair farther apart than this is not a match
THRESHOLDS_KM_MOL = (0.5, 0.1, 2.0)  # the first is the main read; the other two show how much the threshold decides
LIBRARY_SHA256 = "2fb7a77608d57169d8b561f0b8ade073618b8e26f381e6c7c83d19c481506071"


def pahdb_transitions(xml_path: Path, uid: str) -> np.ndarray:
    """(n, 2): frequency (cm⁻¹) and intensity (km/mol) of every transition of one species."""
    root = ET.parse(xml_path).getroot()
    ns = root.tag.split("}")[0] + "}" if root.tag.startswith("{") else ""
    for sp in root.iter(f"{ns}specie"):
        if sp.get("uid") == uid:
            rows = [(float(m.findtext(f"{ns}frequency")), float(m.findtext(f"{ns}intensity"))) for m in sp.find(f"{ns}transitions")]
            return np.array(rows, float).reshape(-1, 2)
    raise SystemExit(f"{xml_path}: no species with uid {uid}")


def candidates(transitions: np.ndarray, i_min: float) -> np.ndarray:
    """Their frequencies at or above i_min km/mol, in the window widened by CAP_CM on each side (a band just outside can still pair)."""
    f, inten = transitions[:, 0], transitions[:, 1]
    keep = (inten >= i_min) & (f >= WINDOW[0] - CAP_CM) & (f <= WINDOW[1] + CAP_CM)
    return np.sort(f[keep])


def ours_in_window(nu: np.ndarray, labels: list[str]) -> np.ndarray:
    """Our IR-active fundamentals in the window, sorted."""
    sel = np.array([lab in IR_ACTIVE for lab in labels]) & (nu >= WINDOW[0]) & (nu <= WINDOW[1])
    return np.sort(nu[sel])


def match(ours: np.ndarray, theirs: np.ndarray, cap: float = CAP_CM) -> dict[str, Any]:
    """One-to-one pairs with the least total |Δν|; pairs beyond cap dropped. Δν = ours − theirs."""
    if len(ours) == 0 or len(theirs) == 0:
        return {"pairs": [], "unpaired_ours": ours.tolist(), "unpaired_theirs": theirs.tolist()}
    cost = np.abs(ours[:, None] - theirs[None, :])
    big = cost.max() + 10 * cap + 1.0
    rows, cols = linear_sum_assignment(np.where(cost <= cap, cost, big))
    pairs = [(float(ours[r]), float(theirs[c])) for r, c in zip(rows, cols, strict=True) if cost[r, c] <= cap]
    used_o, used_t = {p[0] for p in pairs}, {p[1] for p in pairs}
    return {"pairs": pairs, "unpaired_ours": [float(x) for x in ours if x not in used_o],
            "unpaired_theirs": [float(x) for x in theirs if x not in used_t]}


def summary(m: dict[str, Any]) -> dict[str, Any]:
    """Counts, mean, rms and rms about the mean of the pairs' Δν."""
    d = np.array([o - t for o, t in m["pairs"]], float)
    stats = {"n_pairs": len(d), "n_unpaired_ours": len(m["unpaired_ours"]), "n_unpaired_theirs": len(m["unpaired_theirs"])}
    if len(d):
        stats |= {"mean_cm": float(d.mean()), "rms_cm": float(np.sqrt(np.mean(d**2))), "rms_about_mean_cm": float(d.std()),
                  "max_abs_cm": float(np.abs(d).max())}
    return stats


def our_fundamentals(setting: Path) -> tuple[np.ndarray, list[str]]:
    """GVPT2 fundamentals as probes/gvpt2_labels.py computes them, and every mode's D2h label."""
    from gvpt2_labels import gvpt2
    from hot_band_desk_naphthalene import characters, classify
    from s1_anharmonic_level import harmonic_modes
    from s2_label_check import molecule_inputs
    arrays, B, zeta = molecule_inputs(str(setting))
    omega, q = harmonic_modes(str(setting / "ref.json"))
    if not np.allclose(omega, arrays["omega_cm"], atol=1e-6):
        raise SystemExit(f"{setting}: the reference's modes are not the report's")
    with open(setting / "ref.json", encoding="utf-8") as fh:
        mol = json.load(fh)["molecule"]
    labels = classify(characters(mol["symbols"], np.array(mol["geometry"], float).reshape(-1, 3), q))
    nu = gvpt2(arrays["omega_cm"], arrays["phi_ijk"], arrays["phi_iijj_sym"], B, zeta)["nu_gvpt2"]
    return np.asarray(nu, float), labels


def compare(nu: np.ndarray, labels: list[str], transitions: np.ndarray) -> dict[str, Any]:
    """Every threshold's pairs and summary."""
    ours = ours_in_window(nu, labels)
    out = {}
    for i_min in THRESHOLDS_KM_MOL:
        m = match(ours, candidates(transitions, i_min))
        out[f"{i_min:g}"] = {**summary(m), **m}
    return {"n_ours": len(ours), "by_threshold_km_mol": out}


def main(argv: list[str] | None = None) -> int:
    """Command line."""
    import hashlib
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--setting", required=True)
    ap.add_argument("--uid", required=True)
    ap.add_argument("--xml", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    xml = Path(a.xml)
    sha = hashlib.sha256(xml.read_bytes()).hexdigest()
    if sha != LIBRARY_SHA256:
        raise SystemExit(f"{xml}: sha256 {sha} is not the library v1.00 the rule was written for")
    nu, labels = our_fundamentals(Path(a.setting))
    res = {"setting": a.setting, "uid": a.uid, "library_sha256": sha, "cap_cm": CAP_CM, "window": WINDOW,
           **compare(nu, labels, pahdb_transitions(xml, a.uid))}
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    write_atomic(str(out / f"pahdb_match_{a.uid}.json"), json.dumps(res, indent=1))
    main_read = res["by_threshold_km_mol"][f"{THRESHOLDS_KM_MOL[0]:g}"]
    print(f"uid {a.uid}: {res['n_ours']} of ours, {main_read['n_pairs']} paired at ≥ {THRESHOLDS_KM_MOL[0]} km/mol; "
          + ", ".join(f"{k} {main_read[k]:.2f}" for k in ("mean_cm", "rms_cm", "rms_about_mean_cm") if k in main_read))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
