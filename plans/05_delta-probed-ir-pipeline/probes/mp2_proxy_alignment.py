"""Does MP2 − B3LYP follow the anchors' CC − B3LYP correction per family better than the network's stepping stone ωB97X − B3LYP? (TASKS 11 (c),
registered in GoalGathering/notes/PreRegistration_2026-11-04_MP2_Proxy_Alignment.md.) No training and no new calculation: the eleven carried TZ
anchors, the MP2 rows the composites were built from (benzene's own rows), the corpus's analytic B3LYP and ωB97X Hessians.

Per anchor, in the low level's mode basis (analytic B3LYP/6-31G*, mass-weighted, translations and rotations projected), the first-order shifts
K_kk of the CC correction (the carried anchor − B3LYP) and of each candidate (ωB97X − B3LYP, MP2/cc-pVDZ − B3LYP, MP2/cc-pVTZ − B3LYP): the
shifts of probes/set3_decompose.py, the families of probes/e8_cc_locality.py. Pooled per family over the anchors: the correlation, the least-
squares slope of CC on the candidate, the rms of CC − candidate (the candidate used as it is) and of CC − s·candidate with s fitted on the other
anchors (one factor per family, as the anchors tune the head). The verdict per family compares MP2/cc-pVDZ with ωB97X on that last rms.
Amendment 1 (TASKS 183): with --mp2-631gs DIR the candidate MP2/6-31G* (the stone's affordable basis; rows mp2_rows_<id>_631gs.npz in the
corpus frame) is added, with its own verdict against ωB97X; without it the read is the registered one.

    python probes/mp2_proxy_alignment.py <out_dir> [--mp2-631gs <rows dir>]   → <out_dir>/mp2_proxy_alignment.json and .md
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import e8_cc_locality as L  # noqa: E402
import set3_diagnosis as D  # noqa: E402
from cc_composite_full_check import corpus_dir, load_geometry, mp2_rows_frame, rows_in_frame  # noqa: E402
from qc_common import project_tr  # noqa: E402
from set3_decompose import FAMS, projected, shifts  # noqa: E402

CANDIDATES = ("wb97x", "mp2_dz", "mp2_tz")
MAIN, BASELINE = "mp2_dz", "wb97x"
STONE = "mp2_631gs"                # amendment 1: MP2 at the pool's basis, read against the same baseline
BETTER, WORSE = 0.8, 1.25          # ratio of the scaled rms, MP2/cc-pVDZ over ωB97X
MIN_ANCHORS, MIN_MODES = 3, 10     # below either, a family is not read
BENZENE = "A_8448043181"           # its carried anchor is a full CC/TZ Hessian; its MP2 rows are test 1's (4 Oct)
BENZENE_ROWS = (PLAN / "probes/results_m1/composite_mp2_rows_benzene_ccpvdz_2026-10-04.npz",
                PLAN / "probes/results_m1/composite_mp2_rows_benzene_ccpvtz_2026-10-04.npz")


def mp2_sources(mol_id: str, anchor_file: str) -> tuple[str, str, str | None]:
    """(MP2/DZ rows, MP2/TZ rows, plane frame or None) of one anchor: the composite's own record, benzene's test-1 rows."""
    if mol_id == BENZENE:
        return str(BENZENE_ROWS[0]), str(BENZENE_ROWS[1]), None
    with np.load(anchor_file) as z:
        if "mp2_dz" not in z.files:
            raise SystemExit(f"{anchor_file}: no MP2 rows named - not a composite anchor")
        return str(z["mp2_dz"]), str(z["mp2_tz"]), str(z["planeframe"]) or None


def mp2_hessians(mol_id: str, anchor_file: str, sym: list[str], x0: np.ndarray, masses: np.ndarray) -> dict[str, np.ndarray]:
    """MP2/cc-pVDZ and MP2/cc-pVTZ Hessians in the corpus frame, projected as the corpus's are."""
    dz, tz, plane = mp2_sources(mol_id, anchor_file)
    M_dz, M_tz, T, _, _ = mp2_rows_frame(dz, tz, plane, sym, x0)
    return {name: project_tr(T @ M @ T.T, masses, x0)[0] for name, M in (("mp2_dz", M_dz), ("mp2_tz", M_tz))}


def hessian_631gs(rows_dir: Path, mol_id: str, sym: list[str], x0: np.ndarray, masses: np.ndarray) -> np.ndarray:
    """MP2/6-31G* Hessian of one anchor from its row file (corpus frame), projected as the corpus's are."""
    path = rows_dir / f"mp2_rows_{mol_id}_631gs.npz"
    if not path.is_file():
        raise SystemExit(f"{path}: no MP2/6-31G* rows for {mol_id}")
    M, _, _ = rows_in_frame(str(path), None, sym, x0)
    return project_tr(M, masses, x0)[0]


def anchor_record(mol_id: str, anchor_file: str, stone_dir: Path | None = None) -> dict[str, Any]:
    """The shifts K_kk of the CC correction and of every candidate, and each mode's family, for one anchor."""
    mol_dir = corpus_dir(mol_id)
    sym, x0, masses = load_geometry(mol_dir / "geometry.json")
    low = projected(mol_dir / "hessian_b3lyp_analytic.npz")
    w, freq, V = L.normal_modes(low, masses)
    hess = {"truth": projected(Path(anchor_file)), "wb97x": projected(mol_dir / "hessian_wb97x_analytic.npz"),
            **mp2_hessians(mol_id, anchor_file, sym, x0, masses)}
    if stone_dir is not None:
        hess[STONE] = hessian_631gs(stone_dir, mol_id, sym, x0, masses)
    rec = {name: shifts(H - low, V, w, masses).tolist() for name, H in hess.items()}
    return {"mol_id": mol_id, "families": list(L.families(freq, V, sym, masses, x0)), **rec}


def _slope(t: np.ndarray, c: np.ndarray) -> float:
    """Least-squares slope of t on c through the origin; 0 when c carries nothing."""
    cc = float(c @ c)
    return float(t @ c / cc) if cc > 0 else 0.0


def _rms(x: np.ndarray) -> float:
    return float(np.sqrt(np.mean(x ** 2))) if len(x) else float("nan")


def family_stats(records: list[dict[str, Any]], fam: str, cand: str) -> dict[str, Any]:
    """Pooled over the anchors that have modes of `fam`: correlation, slope, the rms of the CC shifts, of CC − candidate and of CC − s·candidate
    with s fitted on the other anchors."""
    parts = []
    for r in records:
        sel = np.array([f == fam for f in r["families"]])
        if sel.any():
            parts.append((np.asarray(r["truth"], float)[sel], np.asarray(r[cand], float)[sel]))
    n_modes = sum(len(t) for t, _ in parts)
    out: dict[str, Any] = {"n_anchors": len(parts), "n_modes": n_modes}
    if len(parts) < MIN_ANCHORS or n_modes < MIN_MODES:
        return {**out, "too_few": True}
    t = np.concatenate([p[0] for p in parts])
    c = np.concatenate([p[1] for p in parts])
    loo = []
    for k, (tk, ck) in enumerate(parts):
        others_t = np.concatenate([p[0] for j, p in enumerate(parts) if j != k])
        others_c = np.concatenate([p[1] for j, p in enumerate(parts) if j != k])
        loo.append(tk - _slope(others_t, others_c) * ck)
    corr = float(np.corrcoef(t, c)[0, 1]) if np.std(t) > 0 and np.std(c) > 0 else float("nan")
    return {**out, "too_few": False, "corr": corr, "slope": _slope(t, c), "rms_cc": _rms(t), "rms_direct": _rms(t - c),
            "rms_scaled_loo": _rms(np.concatenate(loo))}


def family_verdict(main: dict[str, Any], base: dict[str, Any]) -> tuple[str, float | None]:
    """'better', 'worse' or 'no clear difference' for MP2/cc-pVDZ against ωB97X on the scaled rms, with the ratio; 'too few modes' when unread."""
    if main["too_few"] or base["too_few"]:
        return "too few modes", None
    m, b = main["rms_scaled_loo"], base["rms_scaled_loo"]
    if b == 0:
        return ("no clear difference" if m == 0 else "worse"), None
    ratio = m / b
    if ratio <= BETTER:
        return "better", ratio
    if ratio >= WORSE:
        return "worse", ratio
    return "no clear difference", ratio


def read(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Every family's statistics per candidate and its verdict; MP2/6-31G*'s own verdict when the records carry it (amendment 1)."""
    stone = all(STONE in r for r in records)
    cands = (*CANDIDATES, STONE) if stone else CANDIDATES
    res = {}
    for fam in FAMS:
        stats = {cand: family_stats(records, fam, cand) for cand in cands}
        verdict, ratio = family_verdict(stats[MAIN], stats[BASELINE])
        res[fam] = {"stats": stats, "verdict": verdict, "ratio": ratio}
        if stone:
            res[fam]["verdict_631gs"], res[fam]["ratio_631gs"] = family_verdict(stats[STONE], stats[BASELINE])
    return res


def report(res: dict[str, Any], records: list[dict[str, Any]]) -> str:
    lines = [f"# MP2 against ωB97X as the stepping stone, on the {len(records)} carried TZ anchors (TASKS 11 (c))", "",
             "Shifts K_kk in the analytic B3LYP mode basis, pooled per family; 'scaled' = CC − s·candidate with s fitted on the other anchors.", "",
             "| family | candidate | anchors | modes | corr | slope | rms CC | rms CC − cand | rms scaled |", "|---|---|---|---|---|---|---|---|---|"]
    for fam, r in res.items():
        for cand, s in r["stats"].items():
            if s["too_few"]:
                lines.append(f"| {fam} | {cand} | {s['n_anchors']} | {s['n_modes']} | too few | | | | |")
                continue
            lines.append(f"| {fam} | {cand} | {s['n_anchors']} | {s['n_modes']} | {s['corr']:+.2f} | {s['slope']:+.2f} | {s['rms_cc']:.2f} | "
                         f"{s['rms_direct']:.2f} | {s['rms_scaled_loo']:.2f} |")
    lines += ["", "| family | verdict (MP2/cc-pVDZ against ωB97X, scaled rms) | ratio |", "|---|---|---|"]
    for fam, r in res.items():
        ratio = "" if r["ratio"] is None else f"{r['ratio']:.2f}"
        lines.append(f"| {fam} | {r['verdict']} | {ratio} |")
    if all("verdict_631gs" in r for r in res.values()):
        lines += ["", "| family | verdict (MP2/6-31G* against ωB97X, scaled rms; amendment 1) | ratio |", "|---|---|---|"]
        for fam, r in res.items():
            ratio = "" if r["ratio_631gs"] is None else f"{r['ratio_631gs']:.2f}"
            lines.append(f"| {fam} | {r['verdict_631gs']} | {ratio} |")
    return "\n".join(lines) + "\n"


def write_atomic(path: Path, text: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def main(out_dir: Path, stone_dir: Path | None = None) -> int:
    records = [anchor_record(mol_id, f, stone_dir) for mol_id, f in D.anchors().items()]
    res = read(records)
    out_dir.mkdir(parents=True, exist_ok=True)
    write_atomic(out_dir / "mp2_proxy_alignment.json", json.dumps({"families": res, "records": records}, indent=1))
    text = report(res, records)
    write_atomic(out_dir / "mp2_proxy_alignment.md", text)
    print(text)
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("out_dir", type=Path)
    ap.add_argument("--mp2-631gs", type=Path, default=None, help="folder of the MP2/6-31G* row files (amendment 1)")
    a = ap.parse_args()
    sys.exit(main(a.out_dir.resolve(), a.mp2_631gs.resolve() if a.mp2_631gs else None))
