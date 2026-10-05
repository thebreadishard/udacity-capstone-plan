"""Composite anchor level, test 2 (`GoalGathering/notes/Design_2026-10-04_Composite_Anchor_Level_DZ_TZ.md`; test 1 of 4 Oct 16:4x chose X = MP2).

Two steps, two environments:

  compute  (pyscf, WSL qc05)  — the MP2 (frozen core) Hessian rows of a molecule's symmetry-unique displacements at one basis, by central differences of
           analytic gradients with the anchors' step; the rows are kept per displacement so the full Hessian is assembled by the same symmetry
           expansion the anchors use (`probes/e8_symmetry.reconstruct`).
      python probes/cc_composite_full_check.py compute <geometry.json> <out.npz> --basis cc-pvtz [--threads 4] [--step 0.005] [--frozen auto] [--max-memory 12000] [--ks 0,1]

  read     (Windows, the project's python) — H_composite = H_CC/DZ + [H_MP2/TZ − H_MP2/DZ], symmetrised and projected, read per family against the full
           CC/TZ anchor with CC/DZ against CC/TZ as the baseline: rms of corrected frequencies per family (ring-ip, CH-stretch, CH-oop, other), all
           modes, and the ring-coupling ratio — the read-out the rehearsal and the T3 line use.
      python probes/cc_composite_full_check.py read <dz anchor dir> <tz anchor dir> <mol_id> <mp2_dz.npz> <mp2_tz.npz> <out_prefix>
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import e8_symmetry as SYM  # noqa: E402

FAMILIES = ("ring-ip", "CH-stretch", "CH-oop", "other")
CORE = {"H": 0, "C": 1, "N": 1, "O": 1, "F": 1, "S": 5, "Cl": 5}


def load_geometry(path: Path):
    g = json.loads(Path(path).read_text(encoding="utf-8"))
    return [s.capitalize() for s in g["symbols"]], np.asarray(g["coords_bohr"], float), np.asarray(g["masses_amu"], float)


def compute(a) -> int:
    from cc_composite_basis_check import gradient  # pyscf; imported only here
    from pyscf import lib
    lib.num_threads(a.threads)
    sym, x0, _ = load_geometry(a.geometry)
    n = len(sym)
    ops = SYM.point_group_ops(sym, x0)
    ks, reps = SYM.unique_displacements(ops, n)
    if a.ks:
        ks = [int(v) for v in a.ks.split(",")]
    frozen = sum(CORE[s] for s in sym) if a.frozen == "auto" else int(a.frozen)
    rows = {}
    for k in ks:
        t0 = datetime.now()
        g = []
        for s in (+1, -1):
            x = x0.ravel().copy(); x[k] += s * a.step
            g.append(gradient("mp2", sym, x.reshape(-1, 3), a.basis, (99, 590), frozen, a.max_memory, a.cart))
        rows[k] = (g[0] - g[1]) / (2 * a.step)
        print(f"[{datetime.now():%H:%M:%S}] mp2 {a.basis} k={k}: H_kk {rows[k][k]:+.6f} ({(datetime.now() - t0).seconds} s)", flush=True)
    np.savez(a.out, ks=np.array(ks), reps=np.array(reps), step=a.step, basis=a.basis, frozen=frozen, cart=a.cart, coords_bohr=x0,
             **{f"row_{k:02d}": rows[k] for k in ks})
    print(f"→ {a.out} ({len(ks)} displacements)")
    return 0


def assemble(npz: Path, ops, reps, n: int) -> tuple[np.ndarray, float]:
    z = np.load(npz)
    block = {}
    for i in reps:
        b = np.zeros((3, 3 * n))
        for d in range(3):
            k = 3 * i + d
            if f"row_{k:02d}" not in z.files:
                raise SystemExit(f"{npz}: row for displacement {k} (atom {i}, xyz {d}) missing — compute all symmetry-unique displacements first")
            b[d] = z[f"row_{k:02d}"]
        block[i] = b
    H, spread = SYM.reconstruct(block, ops, n)
    return 0.5 * (H + H.T), float(spread)


def read(a) -> int:
    sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "m05"))
    import e7_t2_sqm as T2
    from anchor_deck_rehearsal import project_tr, readout
    from rungC_train import load_corpus
    molecules = PLAN / "modules" / "05_support_predictor" / "corpus" / "molecules"
    mol_dir = molecules / a.mol_id
    sym, x0, masses = load_geometry(mol_dir / "geometry.json")
    n = len(sym)
    ops = SYM.point_group_ops(sym, x0)
    _, reps = SYM.unique_displacements(ops, n)
    H_dz = np.asarray(np.load(Path(a.dz_anchor) / "hessian_ccsd_t.npz")["H_raw"], float)
    H_tz = np.asarray(np.load(Path(a.tz_anchor) / "hessian_ccsd_t.npz")["H_raw"], float)
    H_low = np.asarray(np.load(mol_dir / "hessian_b3lyp_analytic.npz")["H_raw"], float)
    M_dz, s_dz = assemble(Path(a.mp2_dz), ops, reps, n)
    M_tz, s_tz = assemble(Path(a.mp2_tz), ops, reps, n)
    H_comp = H_dz + (M_tz - M_dz)
    mols, *_ = load_corpus(str(molecules), True, log=lambda *_: None)
    m = mols[a.mol_id]
    Hp = {name: project_tr(H, masses, x0)[0] for name, H in (("low", H_low), ("dz", H_dz), ("tz", H_tz), ("comp", H_comp), ("mp2_dz", M_dz), ("mp2_tz", M_tz))}
    K_tz = T2.K_from_dH(m, Hp["tz"] - Hp["low"])
    wt, Ut = T2.corrected_frequencies(m, K_tz)
    fam = np.array(m["family"])[np.argmax(np.abs(Ut), axis=0)]
    ring = np.where(np.array(m["family"]) == "ring-ip")[0]
    res = {name: readout(m, Hp[name], Hp["low"], K_tz, wt, fam, ring) for name in ("dz", "comp", "low")}
    step_dz = float(np.sqrt(np.mean((M_tz - M_dz) ** 2)))
    lines = {f: res["comp"].get(f, 0.0) <= 3.0 for f in FAMILIES if f in res["comp"]}
    verdict = "composite within 3 cm⁻¹ of CC/TZ in every family" if all(lines.values()) else \
        ("3–10 cm⁻¹ in some family" if all(res["comp"].get(f, 0.0) <= 10.0 for f in FAMILIES) else "> 10 cm⁻¹ in a family")
    md = [f"# Composite anchor level, test 2 — {a.mol_id}: CC/DZ + [MP2/TZ − MP2/DZ] against the full CC/TZ anchor — {datetime.now():%Y-%m-%d %H:%M}", "",
          f"Anchors: DZ `{Path(a.dz_anchor).name}`, TZ `{Path(a.tz_anchor).name}`; MP2 rows `{Path(a.mp2_dz).name}`, `{Path(a.mp2_tz).name}` (symmetry spread "
          f"{s_dz:.1e} / {s_tz:.1e} a.u.); rms of the MP2 basis step over the Hessian {step_dz:.2e} a.u. Read-out: rms of corrected frequencies per family against "
          "CC/TZ (the B3LYP 6-31G* low level and the corpus modes, as in the T3 read-out); 'B3LYP alone' is the zero rule.", "",
          "| read-out | B3LYP alone | CC/DZ (the anchors so far) | **composite** |", "|---|---|---|---|"]
    for f in (*FAMILIES, "all", "ratio"):
        fmt = (lambda v: f"{v:.3f}") if f == "ratio" else (lambda v: f"{v:.2f}")
        md.append(f"| {f} | {fmt(res['low'].get(f, float('nan')))} | {fmt(res['dz'].get(f, float('nan')))} | **{fmt(res['comp'].get(f, float('nan')))}** |")
    md += ["", f"**Lines:** {verdict} — " + ", ".join(f"{f} {'≤' if ok else '>'} 3" for f, ok in lines.items()) + "."]
    Path(a.out_prefix + ".md").write_text("\n".join(md), encoding="utf-8")
    Path(a.out_prefix + ".json").write_text(json.dumps(dict(date=datetime.now().strftime("%Y-%m-%d %H:%M"), mol_id=a.mol_id, dz_anchor=a.dz_anchor, tz_anchor=a.tz_anchor,
                                                            mp2_dz=a.mp2_dz, mp2_tz=a.mp2_tz, spread=dict(dz=s_dz, tz=s_tz), mp2_step_rms=step_dz,
                                                            results=res, lines=lines, verdict=verdict), indent=1), encoding="utf-8")
    print("\n".join(md))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("compute")
    c.add_argument("geometry"); c.add_argument("out")
    c.add_argument("--basis", required=True); c.add_argument("--threads", type=int, default=4); c.add_argument("--step", type=float, default=0.005)
    c.add_argument("--frozen", default="auto"); c.add_argument("--max-memory", type=int, default=12000); c.add_argument("--ks", default=None)
    c.add_argument("--cart", action="store_true", help="Cartesian d functions (the corpus's 6-31G* convention); the cc-pVnZ anchors are spherical")
    r = sub.add_parser("read")
    r.add_argument("dz_anchor"); r.add_argument("tz_anchor"); r.add_argument("mol_id"); r.add_argument("mp2_dz"); r.add_argument("mp2_tz"); r.add_argument("out_prefix")
    a = ap.parse_args()
    return compute(a) if a.cmd == "compute" else read(a)


if __name__ == "__main__":
    sys.exit(main())
