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

Test 3 (6 Oct 2026) — the out-of-plane repair of an anchor whose CC/DZ Hessian is IMAGINARY through the small-basis arene artefact (anthracene: −51 and
+7 cm⁻¹ for the two softest out-of-plane modes). Only the out-of-plane block gets the MP2 basis step; for a planar molecule that block does not couple to
the in-plane block by symmetry, so the rows of the representatives' out-of-plane displacements suffice (anthracene: 7 of 21 unique displacements):

  planeframe  — writes the geometry in its principal frame (plane normal on z; `frame` and `origin` kept for the way back) and lists the out-of-plane
                unique displacements:   python probes/cc_composite_full_check.py planeframe <geometry.json> <geometry_planeframe.json>
  merge       — rows computed in several lanes into one file:   python probes/cc_composite_full_check.py merge <out.npz> <part1.npz> <part2.npz> ...
  repair-oop  (Windows, the project's python) — H = R [ Rᵀ H_CC/DZ R + (M_TZ − M_DZ)|out-of-plane ] Rᵀ, frequencies, the two softest out-of-plane modes
                against the corpus DFT values, the registered lines:
      python probes/cc_composite_full_check.py repair-oop <anchor dir> <mol_id> <geometry_planeframe.json> <mp2_dz.npz> <mp2_tz.npz> <out_prefix>
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


# ---- test 3: the out-of-plane repair (6 Oct 2026) ------------------------------------------------------------------------------------------------
CM_PER_SQRT_AU = 5140.4871      # cm⁻¹ per sqrt(E_h / (bohr² amu)); reproduces the E8 probe's frequencies (anthracene −51.2 / 7.0)
SOFT_LINE_CM = 40.0             # registered line: the two softest out-of-plane modes within 40 cm⁻¹ of ωB97X


def plane_frame(x0: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Principal frame of a (near-)planar set of points: columns of V are the axes, the plane normal last (z); origin = centroid."""
    c = x0 - x0.mean(0)
    w, V = np.linalg.eigh(c.T @ c)
    V = V[:, ::-1]                                   # largest extent first, the normal (smallest) on z
    if np.linalg.det(V) < 0:
        V[:, 2] *= -1                                # keep a proper rotation
    return V, x0.mean(0)


def planeframe(a) -> int:
    sym, x0, masses = load_geometry(a.geometry)
    V, origin = plane_frame(x0)
    xr = (x0 - origin) @ V
    n = len(sym)
    ops = SYM.point_group_ops(sym, xr)
    ks, reps = SYM.unique_displacements(ops, n)
    oop = [3 * i + 2 for i in reps]
    out = dict(symbols=sym, coords_bohr=xr.tolist(), masses_amu=masses.tolist(), frame=V.tolist(), origin=origin.tolist(), source=str(a.geometry),
               max_out_of_plane_bohr=float(np.abs(xr[:, 2]).max()), n_ops=len(ops), unique_ks=ks, oop_ks=oop)
    Path(a.out).write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"{a.out}: {n} atoms, {len(ops)} operations, {len(ks)} unique displacements, out-of-plane {oop}; max |z| {out['max_out_of_plane_bohr']:.1e} bohr")
    print(",".join(str(k) for k in oop))
    return 0


def merge(a) -> int:
    parts = [np.load(p) for p in a.parts]
    rows = {}
    for z in parts:
        for key in z.files:
            if key.startswith("row_"):
                rows[key] = z[key]
    meta = {k: parts[0][k] for k in parts[0].files if not k.startswith("row_") and k != "ks"}
    ks = sorted(int(k[4:]) for k in rows)
    np.savez(a.out, ks=np.array(ks), **meta, **rows)
    print(f"→ {a.out}: {len(ks)} displacements {ks} from {len(parts)} files")
    return 0


def assemble_oop(npz: Path, ops, reps, n: int) -> tuple[np.ndarray, float]:
    """Rows of the representatives' z displacements only (the plane frame); the in-plane rows are zero, so the reconstruction carries the out-of-plane
    block and nothing else."""
    z = np.load(npz)
    block = {}
    for i in reps:
        b = np.zeros((3, 3 * n))
        k = 3 * i + 2
        if f"row_{k:02d}" not in z.files:
            raise SystemExit(f"{npz}: out-of-plane row for atom {i} (displacement {k}) missing")
        b[2] = z[f"row_{k:02d}"]
        block[i] = b
    H, spread = SYM.reconstruct(block, ops, n)
    return 0.5 * (H + H.T), float(spread)


def frequencies_cm(H: np.ndarray, masses: np.ndarray, x0: np.ndarray) -> np.ndarray:
    """Vibrational frequencies (signed, cm⁻¹) of a Cartesian Hessian after projecting translations and rotations; the six smallest |ω| dropped."""
    sys.path.insert(0, str(PLAN / "probes"))
    from anchor_deck_rehearsal import project_tr
    Hp = project_tr(H, masses, x0)[0]
    Mi = np.repeat(1 / np.sqrt(masses), 3)
    w = np.linalg.eigvalsh(0.5 * (Hp + Hp.T) * Mi[:, None] * Mi[None, :])
    f = np.sign(w) * CM_PER_SQRT_AU * np.sqrt(np.abs(w))
    keep = np.argsort(np.abs(f))[6:]
    return np.sort(f[keep])


def oop_fraction(H: np.ndarray, masses: np.ndarray, normal: np.ndarray, n_modes: int = 2):
    """Out-of-plane fraction of the n softest modes of a mass-weighted Hessian (no projection; the softest modes are far from the TR null space only
    when they are real — used for reporting)."""
    n = len(masses); Mi = np.repeat(1 / np.sqrt(masses), 3)
    w, v = np.linalg.eigh(0.5 * (H + H.T) * Mi[:, None] * Mi[None, :])
    f = np.sign(w) * CM_PER_SQRT_AU * np.sqrt(np.abs(w))
    order = [i for i in np.argsort(f) if abs(f[i]) > 1.0][:n_modes]
    out = []
    for i in order:
        q = (v[:, i] * Mi).reshape(n, 3)
        out.append((float(f[i]), float(((q @ normal) ** 2).sum() / (q ** 2).sum())))
    return out


def repair_oop(a) -> int:
    anchor = Path(a.anchor_dir)
    src = next((anchor / f for f in ("hessian_ccsd_t_IMAGINARY.npz", "hessian_ccsd_t.npz") if (anchor / f).exists()), None)
    if src is None:
        raise SystemExit(f"{anchor}: no hessian_ccsd_t(_IMAGINARY).npz")
    pf = json.loads(Path(a.planeframe).read_text(encoding="utf-8"))
    sym = [s.capitalize() for s in pf["symbols"]]; xr = np.asarray(pf["coords_bohr"], float); masses = np.asarray(pf["masses_amu"], float)
    V = np.asarray(pf["frame"], float); origin = np.asarray(pf["origin"], float); n = len(sym)
    z = np.load(src); H = np.asarray(z["H_raw"], float); x0 = np.asarray(z["coords_bohr"], float).reshape(n, 3)
    if np.abs((x0 - origin) @ V - xr).max() > 1e-6:
        raise SystemExit("the plane-frame geometry does not match the anchor's coordinates")
    T = np.kron(np.eye(n), V)                        # x − origin = T x_r  →  H_r = Tᵀ H T
    H_r = T.T @ H @ T
    ops = SYM.point_group_ops(sym, xr)
    _, reps = SYM.unique_displacements(ops, n)
    M_dz, s_dz = assemble_oop(Path(a.mp2_dz), ops, reps, n)
    M_tz, s_tz = assemble_oop(Path(a.mp2_tz), ops, reps, n)
    zi = np.arange(2, 3 * n, 3); ip = np.array([k for k in range(3 * n) if k % 3 != 2])
    coupling_cc = float(np.abs(H_r[np.ix_(zi, ip)]).max())          # in-plane/out-of-plane coupling of the anchor (zero by symmetry for a planar molecule)
    coupling_step = float(np.abs((M_tz - M_dz)[np.ix_(zi, ip)]).max())
    step = np.zeros_like(H_r); step[np.ix_(zi, zi)] = (M_tz - M_dz)[np.ix_(zi, zi)]
    H_comp_r = H_r + step
    H_comp = T @ H_comp_r @ T.T
    f_dz = frequencies_cm(H, masses, x0); f_comp = frequencies_cm(H_comp, masses, x0)
    normal = V[:, 2]
    soft_dz = oop_fraction(H, masses, normal); soft_comp = oop_fraction(H_comp, masses, normal)
    molecules = PLAN / "modules" / "05_support_predictor" / "corpus" / "molecules" / a.mol_id
    dft = {}
    for tag in ("b3lyp", "wb97x"):
        p = molecules / f"hessian_{tag}.npz"
        if p.exists():
            fr = np.asarray(np.load(p)["freq_cm"], float); fr = fr[np.abs(fr) > 1.0]; dft[tag] = np.sort(fr)[:6]
    n_im = int((f_comp < -10.0).sum())
    ref = dft.get("wb97x")
    within = bool(ref is not None and len(f_comp) >= 2 and np.abs(f_comp[:2] - ref[:2]).max() <= SOFT_LINE_CM)
    if n_im:
        verdict = "still imaginary: the artefact survives the MP2 basis step — the anchor stays excluded"
    elif within:
        verdict = "repaired: no imaginary mode and both soft modes within 40 cm⁻¹ of ωB97X — the composite anchor enters T3 (lines provisional)"
    else:
        verdict = "repaired but flagged: real, yet a soft mode more than 40 cm⁻¹ from ωB97X — the full composite is computed before use"
    status = "VALID" if n_im == 0 else "IMAGINARY"
    out = Path(a.out_prefix)
    np.savez(str(out) + ".npz", H_raw=H_comp, H_plane_frame=H_comp_r, freq_cm=f_comp, coords_bohr=x0, frame=V, origin=origin, status=status,
             source_anchor=str(src), mp2_dz=str(a.mp2_dz), mp2_tz=str(a.mp2_tz), spread_dz=s_dz, spread_tz=s_tz, coupling_cc=coupling_cc,
             coupling_step=coupling_step, repair="out-of-plane block, MP2/TZ − MP2/DZ (test 3, 6 Oct 2026)")
    fmt = lambda arr: ", ".join(f"{v:.0f}" for v in np.asarray(arr)[:6])  # noqa: E731
    md = [f"# Composite anchor level, test 3 — {a.mol_id}: out-of-plane repair of the CC/DZ anchor — {datetime.now():%Y-%m-%d %H:%M}", "",
          f"Anchor `{src.name}` ({anchor.name}); MP2 rows `{Path(a.mp2_dz).name}`, `{Path(a.mp2_tz).name}` (symmetry spread {s_dz:.1e} / {s_tz:.1e} a.u.); "
          f"in-plane/out-of-plane coupling: anchor {coupling_cc:.1e}, MP2 step {coupling_step:.1e} a.u. (zero by symmetry for a planar molecule). "
          f"Status of the composite: **{status}** ({n_im} imaginary).", "",
          "| lowest six vibrations (cm⁻¹) | values |", "|---|---|",
          f"| CC/DZ anchor | {fmt(f_dz)} |", f"| **composite (out-of-plane block repaired)** | **{fmt(f_comp)}** |"]
    md += [f"| {tag} (corpus) | {fmt(v)} |" for tag, v in dft.items()]
    md += ["", "Two softest modes and their out-of-plane fraction: CC/DZ " + ", ".join(f"{f:.0f} ({p:.2f})" for f, p in soft_dz)
           + "; composite " + ", ".join(f"{f:.0f} ({p:.2f})" for f, p in soft_comp) + ".", "", f"**Lines:** {verdict}."]
    out.with_suffix(".md").write_text("\n".join(md), encoding="utf-8")
    out.with_suffix(".json").write_text(json.dumps(dict(date=datetime.now().strftime("%Y-%m-%d %H:%M"), mol_id=a.mol_id, anchor=str(src), status=status,
                                                        n_imaginary=n_im, freq_dz=f_dz.tolist(), freq_composite=f_comp.tolist(),
                                                        dft={k: v.tolist() for k, v in dft.items()}, soft_dz=soft_dz, soft_composite=soft_comp,
                                                        spread=dict(dz=s_dz, tz=s_tz), coupling=dict(anchor=coupling_cc, step=coupling_step),
                                                        verdict=verdict), indent=1), encoding="utf-8")
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
    p = sub.add_parser("planeframe"); p.add_argument("geometry"); p.add_argument("out")
    m = sub.add_parser("merge"); m.add_argument("out"); m.add_argument("parts", nargs="+")
    o = sub.add_parser("repair-oop")
    o.add_argument("anchor_dir"); o.add_argument("mol_id"); o.add_argument("planeframe"); o.add_argument("mp2_dz"); o.add_argument("mp2_tz"); o.add_argument("out_prefix")
    a = ap.parse_args()
    return {"compute": compute, "read": read, "planeframe": planeframe, "merge": merge, "repair-oop": repair_oop}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
