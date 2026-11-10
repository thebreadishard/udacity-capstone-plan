"""TASKS 184 — how true the anchors are out of plane (`GoalGathering/notes/PreRegistration_2026-11-05_Anchor_CH-oop_Checks.md`).

  pin       this module's family read of benzene's composite against its full CC/TZ reproduces test 2 (6 Oct: CH-oop 7.30 cm⁻¹).
  pyridine  (a) the carried composite with its out-of-plane block replaced by CCSD(T)/cc-pVTZ (the z rows of `e8_cc_hessian_fd.py` in the
            plane frame) is the truth of the check; read: the composite against it per family (test 2's corrected-ω rms), and ωB97X and
            MP2/6-31G* against it in CH-oop with the scale fitted on the other ten anchors (the 5 Nov read's leave-one-out).
  qz        (b) benzene's full CC/TZ with [MP2/cc-pVQZ − MP2/cc-pVTZ] on the out-of-plane block; read: CC/TZ against it per family, and the
            out-of-plane modes of both against Goodman's estimated harmonics.

    python probes/anchor_oop_check.py pin
    python probes/anchor_oop_check.py pyridine <e8 run dir> <planeframe.json> <out dir>
    python probes/anchor_oop_check.py qz <mp2 tz rows.npz> <mp2 qz rows.npz> <planeframe.json> <out dir>
    python probes/anchor_oop_check.py qz <mp2 tz rows.npz> <df-mp2 qz rows.npz> <planeframe.json> <out dir> --df-tz <df-mp2 tz rows.npz>
              (the 10 Nov amendment: the step DF-QZ − DF-TZ, read only when the DF check passes)
"""
from __future__ import annotations

import argparse
import json
import sys
from functools import cache
from pathlib import Path
from typing import Any

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
M05 = PLAN / "modules" / "05_support_predictor"
sys.path.insert(0, str(PLAN / "probes"))
sys.path.insert(0, str(M05 / "m05"))
import anchor_registry as AR  # noqa: E402  (module 05's code is not a package)
import cc_composite_full_check as C  # noqa: E402
import e8_hessian_checks as HC  # noqa: E402
import e8_symmetry as SYM  # noqa: E402
import fundamentals_vs_experiment as FE  # noqa: E402
import mp2_proxy_alignment as M  # noqa: E402
from anchor_deck_rehearsal import readout, truth_of  # noqa: E402
from qc_common import project_tr  # noqa: E402
from rungC_train import load_corpus  # noqa: E402

BENZENE, PYRIDINE = "A_8448043181", "A_6e858b26e5"
STEP_BOHR = 0.005                      # registered: the anchors' step
CH_OOP = "CH-oop"
CANDIDATES = ("wb97x", "mp2_dz", M.STONE)
D6H_OUT_OF_PLANE = ("a2u", "b2g", "e1g", "e2u")
TEST2 = M05 / "out" / "composite_test2_benzene_2026-10-06.json"
FE_RECORD = M05 / "out" / "fundamentals_vs_experiment_2026-10-25.json"
READ_5NOV = PLAN / "probes" / "results_m1" / "mp2_proxy_alignment_631gs_2026-11-05" / "mp2_proxy_alignment.json"
STONE_ROWS = PLAN / "probes" / "results_m1" / "mp2_631gs_anchors_2026-11-04"
PIN_TOL_CM = 1e-6
COUPLING_TOL = 1e-6                    # a.u.: out-of-plane–in-plane elements of a planar molecule's Hessian, zero by symmetry
TZ_ROUTE_TOL = 1e-5                    # a.u.: the plane-frame MP2/TZ rows against the 4 Oct corpus-frame rows, rotated
# Registered lines: (a) the composite's CH-oop rms against the truth; (b) how far CH-oop moves past TZ.
A_HOLDS, A_FAILS = 10.0, 20.0
B_CONVERGED, B_NOT_TRUTH = 3.0, 10.0
DF_LINE_CM = 0.5                       # amendment of 10 Nov: max |Δω| the DF route may add at TZ (the 20 Oct swap test's adopt line)
DF_QZ_BASIS = "cc-pvqz"
PLAN_KEYS = ("ks", "reps", "step", "frozen", "cart")


# ---- the family read (test 2's)

@cache
def corpus_entry(mol_id: str) -> dict[str, Any]:
    mols, *_ = load_corpus(str(C.corpus_dir(mol_id).parent), True, log=lambda *_: None)
    return mols[mol_id]


def family_read(mol_id: str, H_test: np.ndarray, H_true: np.ndarray) -> dict[str, float]:
    """Test 2's read: the corrected-ω rms per family of H_test against H_true, both on the molecule's analytic B3LYP modes."""
    _, x0, masses = C.load_geometry(C.corpus_dir(mol_id) / "geometry.json")
    with np.load(C.corpus_dir(mol_id) / "hessian_b3lyp_analytic.npz") as z:
        H_low = np.asarray(z["H_raw"], float)
    low, test, true = (project_tr(H, masses, x0)[0] for H in (H_low, H_test, H_true))
    m = corpus_entry(mol_id)
    return readout(m, test, low, truth_of(m, true, low))


def carried_hessian(mol_id: str) -> tuple[np.ndarray, Path]:
    entry = AR.carried(mol_id)
    if entry is None:
        raise SystemExit(f"{mol_id}: no carried anchor")
    path = PLAN / entry["path"]
    with np.load(path) as z:
        return np.asarray(z["H_raw"], float), path


# ---- pin

def pin() -> dict[str, Any]:
    """Benzene's composite against its full CC/TZ through this module's read, against test 2's record."""
    t2 = json.loads(TEST2.read_text(encoding="utf-8"))
    sym, x0, _ = C.load_geometry(C.corpus_dir(BENZENE) / "geometry.json")
    n = len(sym)
    ops = SYM.point_group_ops(sym, x0)
    _, reps = SYM.unique_displacements(ops, n)
    H_dz = C.load_anchor(Path(t2["dz_anchor"]) / "hessian_ccsd_t.npz")[0]
    H_tz = C.load_anchor(Path(t2["tz_anchor"]) / "hessian_ccsd_t.npz")[0]
    M_dz, M_tz, _, _ = C.mp2_pair(t2["mp2_dz"], t2["mp2_tz"], ops, reps, n)
    res = family_read(BENZENE, H_dz + (M_tz - M_dz), H_tz)
    worst = max(abs(res[f] - v) for f, v in t2["results"]["comp"].items() if f in C.FAMILIES)
    if worst > PIN_TOL_CM:
        raise SystemExit(f"pin: the family read differs from test 2 by {worst:.2e} cm⁻¹")
    return {"families": res, "test2": t2["results"]["comp"], "worst_cm": worst}


# ---- (a) pyridine

def write_cc_rows(run_dir: Path, ks: list[int], coords: np.ndarray, out: Path) -> Path:
    """The CC/TZ rows (g(+k) − g(−k)) / 2δ of the e8 run's displacements, in `compute`'s row format."""
    with np.load(run_dir / "reference.npz") as z:
        if np.abs(np.asarray(z["coords_bohr"], float) - coords).max() > C.FRAME_TOL_BOHR:
            raise SystemExit(f"{run_dir}: the run's geometry is not the plane-frame geometry")
    if not HC.kernels_cleared(run_dir):
        raise SystemExit(f"{run_dir}: the (T) C kernels of these gradients are unchecked and no passing {HC.TWO_ROUTE_FILE} exists — run "
                         "e8 with --two-route-check only first (rule: every derived quantity has a second route)")
    rows = {}
    for k in ks:
        g_p, g_m = (np.load(run_dir / f"grad_{k:02d}_{s}.npy").ravel() for s in ("p", "m"))
        rows[f"row_{k:02d}"] = (g_p - g_m) / (2 * STEP_BOHR)
    return C.save_npz(out, ks=np.array(ks), step=STEP_BOHR, basis="cc-pvtz", coords_bohr=coords, **rows)


def oop_truth(pf: C.PlaneFrame, H_comp: np.ndarray, rows: Path) -> tuple[np.ndarray, float, float]:
    """(H_true, the rows' symmetry spread, the composite's largest out-of-plane–in-plane element in the plane frame)."""
    n = len(pf.symbols)
    T = C.plane_rotation(pf.V, n)
    zi, ip = C.oop_indices(n)
    coupling = float(np.abs((T.T @ H_comp @ T)[np.ix_(zi, ip)]).max())
    if coupling > COUPLING_TOL:
        raise SystemExit(f"the composite couples out-of-plane and in-plane by {coupling:.1e} a.u. — not a planar Hessian")
    ops = SYM.point_group_ops(pf.symbols, pf.coords)
    _, reps = SYM.unique_displacements(ops, n)
    block_r, spread = C.assemble(rows, ops, reps, n, C.OUT_OF_PLANE)
    return C.oop_block_replaced(H_comp, pf.V, block_r), float(spread), coupling


def save_truth_anchor(path: Path, H: np.ndarray, x0: np.ndarray, masses: np.ndarray, composite: Path) -> Path:
    """H_true in the anchor format `mp2_proxy_alignment.anchor_record` reads, with the composite's MP2 sources."""
    with np.load(composite) as z:
        sources = {k: z[k] for k in ("mp2_dz", "mp2_tz", "planeframe") if k in z.files}
    return C.save_npz(path, H_raw=H, H_projected=project_tr(H, masses, x0)[0], coords_bohr=x0, source_composite=str(composite), **sources)


def loo_residual(others: list[dict], rec: dict, cand: str, fam: str = CH_OOP) -> float:
    """rms of the truth − s·candidate on one molecule's `fam` modes, s fitted on the other anchors (the 5 Nov read's leave-one-out)."""
    def pooled(recs: list[dict], key: str) -> np.ndarray:
        return np.concatenate([np.asarray(r[key], float)[np.array(r["families"]) == fam] for r in recs])
    s = M._slope(pooled(others, "truth"), pooled(others, cand))
    sel = np.array(rec["families"]) == fam
    return M._rms(np.asarray(rec["truth"], float)[sel] - s * np.asarray(rec[cand], float)[sel])


def verdict_a(rms: float) -> str:
    if rms <= A_HOLDS:
        return "holds"
    return "weaker" if rms <= A_FAILS else "fails"


def read_pyridine(run_dir: Path, planeframe: Path, out: Path) -> dict[str, Any]:
    pf = C.load_planeframe(planeframe)
    _, x0, masses = C.load_geometry(C.corpus_dir(PYRIDINE) / "geometry.json")
    pf.check(x0)
    ks = json.loads(planeframe.read_text(encoding="utf-8"))["oop_ks"]
    H_comp, comp_file = carried_hessian(PYRIDINE)
    rows = write_cc_rows(run_dir, ks, pf.coords, out / "cc_tz_oop_rows_pyridine.npz")
    H_true, spread, coupling = oop_truth(pf, H_comp, rows)
    truth_file = save_truth_anchor(out / "pyridine_cc_tz_oop_truth.npz", H_true, x0, masses, comp_file)
    fam = family_read(PYRIDINE, H_comp, H_true)
    rec_true = M.anchor_record(PYRIDINE, str(truth_file), STONE_ROWS)
    rec_comp = M.anchor_record(PYRIDINE, str(comp_file), STONE_ROWS)
    records = json.loads(READ_5NOV.read_text(encoding="utf-8"))["records"]
    if next(r for r in records if r["mol_id"] == PYRIDINE) != rec_comp:
        raise SystemExit("pyridine's composite record differs from the 5 Nov read")
    others = [r for r in records if r["mol_id"] != PYRIDINE]
    stone = {c: {"against_composite": loo_residual(others, rec_comp, c), "against_cc_tz": loo_residual(others, rec_true, c)}
             for c in CANDIDATES}
    return {"families": fam, "verdict": verdict_a(fam[CH_OOP]), "spread": spread, "coupling": coupling, "stone": stone,
            "truth_file": str(truth_file), "rows": str(rows)}


# ---- (b) benzene's QZ step

def oop_modes_vs_goodman(H: np.ndarray, sym: list[str], x0: np.ndarray, masses: np.ndarray) -> list[dict[str, Any]]:
    """Benzene's out-of-plane modes of H, paired with the experiment by irrep and order (TASKS 111's pairing), against Goodman's ω."""
    _, freq, V, _ = FE.normal_modes(project_tr(H, masses, x0)[0], masses)
    labels, _ = FE.d6h_irreps(V, freq, sym, x0)
    pairs = FE.pair_by_irrep(FE.groups(freq, labels), FE.benzene_experiment())
    return [{"irrep": e.irrep, "wilson": e.wilson, "omega": g.freq, "omega_exp": e.omega, "d": g.freq - e.omega}
            for g, e, _ in pairs if e.irrep in D6H_OUT_OF_PLANE]


def ch_oop_wilson() -> set[int]:
    """Benzene's CH-oop modes by Wilson number, as TASKS 111 assigned them."""
    modes = json.loads(FE_RECORD.read_text(encoding="utf-8"))["benzene"]["modes"]
    return {m["wilson"] for m in modes if m["family"] == CH_OOP}


def check_goodman_route(rms_tz: float) -> None:
    """The CC/TZ CH-oop rms against Goodman's ω must be TASKS 111's, or the pairing here is not that read's."""
    stored = json.loads(FE_RECORD.read_text(encoding="utf-8"))["benzene"]["stats"]["cc_harmonic_minus_exp_harmonic"][CH_OOP]["rms"]
    if abs(rms_tz - stored) > PIN_TOL_CM:
        raise SystemExit(f"CC/TZ against Goodman: {rms_tz:.4f} cm⁻¹ here, {stored:.4f} in TASKS 111's record")


def tz_second_route(pf: C.PlaneFrame, M_tz_r: np.ndarray, x0: np.ndarray) -> float:
    """Largest difference of the out-of-plane block between the plane-frame MP2/TZ rows and test 2's corpus-frame rows, rotated."""
    t2 = json.loads(TEST2.read_text(encoding="utf-8"))
    n = len(pf.symbols)
    ops = SYM.point_group_ops(pf.symbols, x0)
    _, reps = SYM.unique_displacements(ops, n)
    M_old, _ = C.assemble(Path(t2["mp2_tz"]), ops, reps, n)
    T = C.plane_rotation(pf.V, n)
    return float(np.abs(C.oop_part(T.T @ M_old @ T) - C.oop_part(M_tz_r)).max())


def check_df_files(conv_tz: Path, df_tz: Path, df_qz: Path) -> None:
    """Refuse DF files that are not DF-MP2 at TZ and QZ on the conventional TZ file's plan."""
    with np.load(conv_tz) as c, np.load(df_tz) as t, np.load(df_qz) as q:
        for name, z, basis in (("DF-TZ", t, str(c["basis"])), ("DF-QZ", q, DF_QZ_BASIS)):
            if "method" not in z.files or not str(z["method"]).startswith("DF-MP2"):
                raise SystemExit(f"{name}: not a DF-MP2 row file")
            if str(z["basis"]) != basis:
                raise SystemExit(f"{name}: basis {z['basis']}, expected {basis}")
            for key in PLAN_KEYS:
                if not np.array_equal(z[key], c[key]):
                    raise SystemExit(f"{name}: {key} differs from the conventional TZ file's")


def df_error_cm(H_tz: np.ndarray, V: np.ndarray, M_conv: np.ndarray, M_df: np.ndarray, masses: np.ndarray, x0: np.ndarray) -> float:
    """Return the largest |Δω| the DF route adds at TZ: CC/TZ with its out-of-plane block shifted by DF-TZ − conventional TZ."""
    shifted = C.oop_step_added(H_tz, V, M_df - M_conv)
    return float(np.abs(C.frequencies_cm(shifted, masses, x0) - C.frequencies_cm(H_tz, masses, x0)).max())


def require_df_line(err: float) -> None:
    if err > DF_LINE_CM:
        raise SystemExit(f"the DF route moves CC/TZ by {err:.2f} cm⁻¹ at TZ (line {DF_LINE_CM}): (b) is not read")


def verdict_b(rms: float) -> str:
    if rms <= B_CONVERGED:
        return "converged"
    return "basis error" if rms <= B_NOT_TRUTH else "not the truth"


def read_qz(tz_rows: Path, qz_rows: Path, planeframe: Path, df_tz: Path | None = None) -> dict[str, Any]:
    pf = C.load_planeframe(planeframe)
    sym, x0, masses = C.load_geometry(C.corpus_dir(BENZENE) / "geometry.json")
    pf.check(x0)
    C.check_rows_coordinates((str(tz_rows), str(qz_rows)), pf.coords, "plane")
    n = len(sym)
    ops = SYM.point_group_ops(pf.symbols, pf.coords)
    _, reps = SYM.unique_displacements(ops, n)
    M_tz, s_tz = C.assemble(tz_rows, ops, reps, n, C.OUT_OF_PLANE)
    M_qz, s_qz = C.assemble(qz_rows, ops, reps, n, C.OUT_OF_PLANE)
    route = tz_second_route(pf, M_tz, x0)
    if route > TZ_ROUTE_TOL:
        raise SystemExit(f"the plane-frame MP2/TZ rows differ from test 2's by {route:.1e} a.u.")
    H_tz, _ = carried_hessian(BENZENE)
    M_base, df_err = M_tz, None
    if df_tz is not None:
        check_df_files(tz_rows, df_tz, qz_rows)
        M_base, _ = C.assemble(df_tz, ops, reps, n, C.OUT_OF_PLANE)
        df_err = df_error_cm(H_tz, pf.V, M_tz, M_base, masses, x0)
        require_df_line(df_err)
    H_qz = C.oop_step_added(H_tz, pf.V, M_qz - M_base)
    fam = family_read(BENZENE, H_tz, H_qz)
    wilson = ch_oop_wilson()
    modes = {"cc_tz": oop_modes_vs_goodman(H_tz, sym, x0, masses), "cc_tz_qz_step": oop_modes_vs_goodman(H_qz, sym, x0, masses)}
    goodman = {k: M._rms(np.array([r["d"] for r in v if r["wilson"] in wilson])) for k, v in modes.items()}
    check_goodman_route(goodman["cc_tz"])
    return {"families": fam, "verdict": verdict_b(fam[CH_OOP]), "spread": {"tz": s_tz, "qz": s_qz}, "tz_second_route": route,
            "route": "conventional" if df_tz is None else "df-mp2", "df_error_cm": df_err,
            "modes": modes, "ch_oop_rms_vs_goodman": goodman}


# ---- reports

def family_table(res: dict[str, float]) -> list[str]:
    fams = [f for f in C.FAMILIES if f in res]
    return ["| " + " | ".join(fams) + " | all |", "|" + "---|" * (len(fams) + 1),
            "| " + " | ".join(f"{res[f]:.2f}" for f in fams) + f" | {res['all']:.2f} |"]


def report_pyridine(r: dict[str, Any]) -> list[str]:
    lines = ["# TASKS 184 (a): pyridine's composite against CCSD(T)/cc-pVTZ out of plane", "",
             "Corrected-ω rms (cm⁻¹) of the carried composite against the truth (composite with its out-of-plane block from CC/TZ):", "",
             *family_table(r["families"]), "", f"**Verdict (registered line, CH-oop): {r['verdict']}.** Rows' symmetry spread "
             f"{r['spread']:.1e} a.u.; composite's out-of-plane–in-plane coupling {r['coupling']:.1e} a.u.", "",
             "CH-oop rms of truth − s·candidate on pyridine, s from the other ten anchors (descriptive, one molecule):", "",
             "| candidate | against the composite | against CC/TZ |", "|---|---|---|"]
    lines += [f"| {c} | {v['against_composite']:.2f} | {v['against_cc_tz']:.2f} |" for c, v in r["stone"].items()]
    return lines


def report_qz(r: dict[str, Any]) -> list[str]:
    lines = ["# TASKS 184 (b): how far benzene's out-of-plane modes move past cc-pVTZ (MP2/QZ − MP2/TZ step)", "",
             "Corrected-ω rms (cm⁻¹) of CC/TZ against CC/TZ + [MP2/QZ − MP2/TZ] on the out-of-plane block:", "", *family_table(r["families"]), "",
             f"**Verdict (registered line, CH-oop): {r['verdict']}.** MP2/TZ rows against test 2's, rotated: {r['tz_second_route']:.1e} a.u.", "",
             *([] if r["df_error_cm"] is None else [f"Step by DF-MP2 (10 Nov amendment); the DF check at TZ: max |Δω| "
                                                 f"{r['df_error_cm']:.3f} cm⁻¹ (line {DF_LINE_CM}).", ""]),
             "| irrep | Wilson | CC/TZ ω | with the QZ step | Goodman ω |", "|---|---|---|---|---|"]
    for a, b in zip(r["modes"]["cc_tz"], r["modes"]["cc_tz_qz_step"], strict=True):
        lines.append(f"| {a['irrep']} | {a['wilson']} | {a['omega']:.1f} | {b['omega']:.1f} | {a['omega_exp']:.0f} |")
    g = r["ch_oop_rms_vs_goodman"]
    lines += ["", f"CH-oop rms against Goodman's ω: CC/TZ {g['cc_tz']:.1f}, with the QZ step {g['cc_tz_qz_step']:.1f} cm⁻¹."]
    return lines


def write_outputs(out: Path, name: str, record: dict[str, Any], md: list[str]) -> None:
    out.mkdir(parents=True, exist_ok=True)
    M.write_atomic(out / f"{name}.json", json.dumps({"date": C.stamp(), **record}, indent=1))
    M.write_atomic(out / f"{name}.md", "\n".join(md) + "\n")
    print("\n".join(md))


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("pin")
    p = sub.add_parser("pyridine")
    for name in ("run_dir", "planeframe", "out"):
        p.add_argument(name, type=Path)
    q = sub.add_parser("qz")
    for name in ("tz_rows", "qz_rows", "planeframe", "out"):
        q.add_argument(name, type=Path)
    q.add_argument("--df-tz", type=Path, help="DF-MP2/TZ rows: qz_rows are then DF-MP2/QZ (the 10 Nov amendment)")
    return ap


def main(argv: list[str] | None = None) -> int:
    a = build_parser().parse_args(argv)
    if a.cmd == "pin":
        r = pin()
        print(f"pin: test 2 reproduced to {r['worst_cm']:.1e} cm⁻¹ — " + ", ".join(f"{f} {v:.2f}" for f, v in r["families"].items()))
    elif a.cmd == "pyridine":
        a.out.mkdir(parents=True, exist_ok=True)
        r = read_pyridine(a.run_dir, a.planeframe, a.out)
        write_outputs(a.out, "anchor_oop_pyridine", r, report_pyridine(r))
    else:
        r = read_qz(a.tz_rows, a.qz_rows, a.planeframe, a.df_tz)
        write_outputs(a.out, "anchor_oop_benzene_qz", r, report_qz(r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
