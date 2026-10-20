"""Composite anchor level (`GoalGathering/notes/Design_2026-10-04_Composite_Anchor_Level_DZ_TZ.md`): H = CC/DZ + [MP2/TZ − MP2/DZ].

  compute     (pyscf, WSL qc05) — the MP2 (frozen core) Hessian rows of a molecule's symmetry-unique displacements at one basis, by central
              differences of analytic gradients with the anchors' step; kept per displacement so the full Hessian is assembled by the same
              symmetry expansion the anchors use (`probes/e8_symmetry.reconstruct`). The rows of the 7 Oct anchors; set three's rows come from
              `probes/dfmp2_rows.py` in the same format.
      python probes/cc_composite_full_check.py compute <geometry.json> <out.npz> --basis cc-pvtz [--threads 4] [--step 0.005]
          [--frozen auto] [--max-memory 12000] [--ks 0,1] [--cart]
  build       — the full composite anchor of the anchor registry (TASKS 28, 7 Oct 2026), every symmetry-unique displacement:
      python probes/cc_composite_full_check.py build <hessian_ccsd_t.npz> <mol_id> <mp2_dz.npz> <mp2_tz.npz> <out_prefix> [--planeframe <json>]
  planeframe  — the geometry in its principal frame (plane normal on z; `frame` and `origin` kept for the way back) and its out-of-plane
              unique displacements:   python probes/cc_composite_full_check.py planeframe <geometry.json> <geometry_planeframe.json>
  merge       — rows computed in several lanes into one file:   python probes/cc_composite_full_check.py merge <out.npz> <part1.npz> ...

Two registered tests whose reads are kept for their outcomes (the design note):
  read        test 2 (6 Oct) — the composite read per family against the full CC/TZ anchor, CC/DZ beside it:
      python probes/cc_composite_full_check.py read <dz anchor dir> <tz anchor dir> <mol_id> <mp2_dz.npz> <mp2_tz.npz> <out_prefix>
  repair-oop  test 3 (6 Oct) — only the out-of-plane block of an IMAGINARY CC/DZ anchor gets the basis step (planar molecule: that block
              does not couple to the in-plane one by symmetry), H = R [Rᵀ H_CC/DZ R + (M_TZ − M_DZ)|oop] Rᵀ:
      python probes/cc_composite_full_check.py repair-oop <anchor dir> <mol_id> <geometry_planeframe.json> <mp2_dz.npz> <mp2_tz.npz> <out_prefix>
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import e8_symmetry as SYM  # noqa: E402
from qc_common import CORE_ORBITALS, project_tr  # noqa: E402

FAMILIES = ("ring-ip", "CH-stretch", "CH-oop", "other")
IMAGINARY_CM = -10.0      # a frequency below this is an imaginary mode (the corpus rule)
CONVENTIONAL_STEP = "MP2 (pyscf, conventional)"   # the 7 Oct row files, which carry no 'method' key
CM_PER_SQRT_AU = 5140.4871      # cm⁻¹ per sqrt(E_h / (bohr² amu)); reproduces the E8 probe's frequencies (anthracene −51.2 / 7.0)
SOFT_LINE_CM = 40.0             # registered line: the two softest out-of-plane modes within 40 cm⁻¹ of ωB97X
FAMILY_LINE_CM = 3.0            # test 2: the composite within 3 cm⁻¹ of CC/TZ in every family
FAMILY_LOOSE_CM = 10.0          # test 2: '3–10 cm⁻¹ in some family'
FRAME_TOL_BOHR = 1e-6
ALL_DIRECTIONS = (0, 1, 2)
OUT_OF_PLANE = (2,)             # z in the plane frame


# ---- files

def load_geometry(path: Path):
    g = json.loads(Path(path).read_text(encoding="utf-8"))
    return [s.capitalize() for s in g["symbols"]], np.asarray(g["coords_bohr"], float), np.asarray(g["masses_amu"], float)


def corpus_dir(mol_id: str) -> Path:
    return PLAN / "modules" / "05_support_predictor" / "corpus" / "molecules" / mol_id


def load_anchor(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """(H_raw, coordinates as n × 3) of a CC anchor file."""
    with np.load(path) as z:
        return np.asarray(z["H_raw"], float), np.asarray(z["coords_bohr"], float).reshape(-1, 3)


@dataclass(frozen=True)
class PlaneFrame:
    """A geometry in its principal frame: x_r = (x − origin) @ V."""
    symbols: list[str]
    coords: np.ndarray
    masses: np.ndarray
    V: np.ndarray
    origin: np.ndarray

    def check(self, x0: np.ndarray) -> None:
        if np.abs((x0 - self.origin) @ self.V - self.coords).max() > FRAME_TOL_BOHR:
            raise SystemExit("the plane-frame geometry does not match the anchor's coordinates")


def load_planeframe(path: Path) -> PlaneFrame:
    pf = json.loads(Path(path).read_text(encoding="utf-8"))
    return PlaneFrame([s.capitalize() for s in pf["symbols"]], np.asarray(pf["coords_bohr"], float), np.asarray(pf["masses_amu"], float),
                      np.asarray(pf["frame"], float), np.asarray(pf["origin"], float))


def dft_reference(mol_dir: Path) -> dict[str, np.ndarray]:
    """The corpus's six lowest B3LYP and ωB97X frequencies, where the molecule has them."""
    dft = {}
    for tag in ("b3lyp", "wb97x"):
        p = mol_dir / f"hessian_{tag}.npz"
        if p.exists():
            with np.load(p) as z:
                fr = np.asarray(z["freq_cm"], float)
            dft[tag] = np.sort(fr[np.abs(fr) > 1.0])[:6]
    return dft


def write_text(path: Path, text: str) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def save_npz(path: str | Path, **arrays) -> Path:
    """np.savez's file (".npz" added when missing), written to a temporary file and moved over the target."""
    target = Path(path if str(path).endswith(".npz") else f"{path}.npz")
    tmp = target.with_name(target.name + ".tmp")
    with open(tmp, "wb") as fh:
        np.savez(fh, **arrays)
    os.replace(tmp, target)
    return target


def six(values) -> str:
    return ", ".join(f"{v:.0f}" for v in np.asarray(values)[:6])


def stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def status_of(n_imaginary: int) -> str:
    return "VALID" if n_imaginary == 0 else "IMAGINARY"


# ---- rows and Hessians

def assemble(npz: Path, ops, reps, n: int, directions: tuple[int, ...] = ALL_DIRECTIONS) -> tuple[np.ndarray, float]:
    """The symmetrised Hessian from the representatives' rows in `directions` (the other rows zero) and the symmetry spread."""
    block = {}
    with np.load(npz) as z:
        for i in reps:
            b = np.zeros((3, 3 * n))
            for d in directions:
                k = 3 * i + d
                if f"row_{k:02d}" not in z.files:
                    raise SystemExit(f"{npz}: row for displacement {k} (atom {i}, xyz {d}) missing — compute every symmetry-unique displacement "
                                     "it needs first")
                b[d] = z[f"row_{k:02d}"]
            block[i] = b
    H, spread = SYM.reconstruct(block, ops, n)
    return 0.5 * (H + H.T), float(spread)


def mp2_pair(mp2_dz: str, mp2_tz: str, ops, reps, n: int, directions: tuple[int, ...] = ALL_DIRECTIONS):
    """(M_DZ, M_TZ, spread DZ, spread TZ)."""
    M_dz, s_dz = assemble(Path(mp2_dz), ops, reps, n, directions)
    M_tz, s_tz = assemble(Path(mp2_tz), ops, reps, n, directions)
    return M_dz, M_tz, s_dz, s_tz


def _mass_weighted(H: np.ndarray, masses: np.ndarray, x0: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    Hp = project_tr(H, masses, x0)[0]
    Mi = np.repeat(1 / np.sqrt(masses), 3)
    return 0.5 * (Hp + Hp.T) * Mi[:, None] * Mi[None, :], Mi


def _to_cm(w: np.ndarray) -> np.ndarray:
    return np.sign(w) * CM_PER_SQRT_AU * np.sqrt(np.abs(w))


def frequencies_cm(H: np.ndarray, masses: np.ndarray, x0: np.ndarray) -> np.ndarray:
    """Vibrational frequencies (signed, cm⁻¹) after projecting translations and rotations; the six smallest |ω| dropped."""
    f = _to_cm(np.linalg.eigvalsh(_mass_weighted(H, masses, x0)[0]))
    return np.sort(f[np.argsort(np.abs(f))[6:]])


def oop_fraction(H: np.ndarray, masses: np.ndarray, x0: np.ndarray, normal: np.ndarray, n_modes: int = 2) -> list[tuple[float, float]]:
    """Out-of-plane fraction of the n softest vibrations — for reporting."""
    A, Mi = _mass_weighted(H, masses, x0)
    w, v = np.linalg.eigh(A)
    f = _to_cm(w)
    out = []
    for i in [i for i in np.argsort(f) if abs(f[i]) > 1.0][:n_modes]:
        q = (v[:, i] * Mi).reshape(len(masses), 3)
        out.append((float(f[i]), float(((q @ normal) ** 2).sum() / (q ** 2).sum())))
    return out


# ---- compute, planeframe, merge

def compute(a) -> int:
    from cc_composite_basis_check import GradientSettings, gradient  # pyscf; imported only here
    from pyscf import lib
    lib.num_threads(a.threads)
    sym, x0, _ = load_geometry(a.geometry)
    n = len(sym)
    ks, reps = SYM.unique_displacements(SYM.point_group_ops(sym, x0), n)
    if a.ks:
        ks = [int(v) for v in a.ks.split(",")]
    frozen = sum(CORE_ORBITALS[s] for s in sym) if a.frozen == "auto" else int(a.frozen)
    settings = GradientSettings(a.basis, (99, 590), frozen, a.max_memory, a.cart)
    rows = {}
    for k in ks:
        t0 = datetime.now()
        g = []
        for s in (+1, -1):
            x = x0.ravel().copy()
            x[k] += s * a.step
            g.append(gradient("mp2", sym, x.reshape(-1, 3), settings))
        rows[k] = (g[0] - g[1]) / (2 * a.step)
        print(f"[{datetime.now():%H:%M:%S}] mp2 {a.basis} k={k}: H_kk {rows[k][k]:+.6f} ({(datetime.now() - t0).seconds} s)", flush=True)
    save_npz(a.out, ks=np.array(ks), reps=np.array(reps), step=a.step, basis=a.basis, frozen=frozen, cart=a.cart, coords_bohr=x0,
             **{f"row_{k:02d}": rows[k] for k in ks})
    print(f"→ {a.out} ({len(ks)} displacements)")
    return 0


def plane_frame(x0: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Principal frame of a (near-)planar set of points: columns of V are the axes, the plane normal last (z); origin = centroid."""
    c = x0 - x0.mean(0)
    _, V = np.linalg.eigh(c.T @ c)
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
    write_text(Path(a.out), json.dumps(out, indent=1))
    print(f"{a.out}: {n} atoms, {len(ops)} operations, {len(ks)} unique displacements, out-of-plane {oop}; max |z| "
          f"{out['max_out_of_plane_bohr']:.1e} bohr")
    print(",".join(str(k) for k in oop))
    return 0


def merge(a) -> int:
    rows, meta = {}, None
    for p in a.parts:
        with np.load(p) as z:
            if meta is None:
                meta = {k: z[k] for k in z.files if not k.startswith("row_") and k != "ks"}
            rows.update({k: z[k] for k in z.files if k.startswith("row_")})
    ks = sorted(int(k[4:]) for k in rows)
    save_npz(a.out, ks=np.array(ks), **meta, **rows)
    print(f"→ {a.out}: {len(ks)} displacements {ks} from {len(a.parts)} files")
    return 0


# ---- build: the full composite anchor

def build_frame(a, x0: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(V, coordinates the rows were computed at): the plane frame when given, else the corpus frame."""
    if not a.planeframe:
        return np.eye(3), x0
    pf = load_planeframe(a.planeframe)
    pf.check(x0)
    return pf.V, pf.coords


def check_rows_coordinates(a, xr: np.ndarray) -> None:
    for rows in (a.mp2_dz, a.mp2_tz):
        with np.load(rows) as z:
            xc = np.asarray(z["coords_bohr"], float).reshape(-1, 3)
        if np.abs(xc - xr).max() > FRAME_TOL_BOHR:
            raise SystemExit(f"{rows}: rows computed at other coordinates than the anchor's (frame: {'plane' if a.planeframe else 'corpus'})")


def step_method_of(mp2_tz: str) -> str:
    with np.load(mp2_tz) as z:
        return str(z["method"]) if "method" in z.files else CONVENTIONAL_STEP


def build(a) -> int:
    """The full composite anchor H = CC/DZ + [MP2/TZ − MP2/DZ]. With --planeframe the rows were computed in that frame and the step is rotated
    back. Writes <out>.npz (H_raw, H_projected, freq_cm, status), .md and .json."""
    anchor = Path(a.anchor)
    H, x0 = load_anchor(anchor)
    n = len(x0)
    mol_dir = corpus_dir(a.mol_id)
    sym, xg, masses = load_geometry(mol_dir / "geometry.json")
    if np.abs(xg - x0).max() > FRAME_TOL_BOHR:
        raise SystemExit(f"{anchor}: coordinates differ from the corpus geometry of {a.mol_id}")
    V, xr = build_frame(a, x0)
    check_rows_coordinates(a, xr)
    ops = SYM.point_group_ops(sym, xr)
    _, reps = SYM.unique_displacements(ops, n)
    M_dz, M_tz, s_dz, s_tz = mp2_pair(a.mp2_dz, a.mp2_tz, ops, reps, n)
    T = np.kron(np.eye(n), V)
    step = T @ (M_tz - M_dz) @ T.T
    H_comp = H + step
    f_dz, f_comp = frequencies_cm(H, masses, x0), frequencies_cm(H_comp, masses, x0)
    n_im = int((f_comp < IMAGINARY_CM).sum())
    status = status_of(n_im)
    step_method = step_method_of(a.mp2_tz)
    dft = dft_reference(mol_dir)
    step_rms = float(np.sqrt(np.mean(step ** 2)))
    save_npz(f"{a.out_prefix}.npz", H_raw=H_comp, H_projected=project_tr(H_comp, masses, x0)[0], freq_cm=f_comp, coords_bohr=x0, status=status,
             source_anchor=str(anchor), mp2_dz=str(a.mp2_dz), mp2_tz=str(a.mp2_tz), spread_dz=s_dz, spread_tz=s_tz, step_rms=step_rms,
             planeframe=str(a.planeframe or ""), composite="CC/DZ + [MP2/TZ − MP2/DZ], every unique displacement (TASKS 28, 7 Oct 2026)",
             step_method=step_method)
    md = [f"# Composite anchor (full) — {a.mol_id}: CC/DZ + [MP2/TZ − MP2/DZ] — {stamp()}", "",
          f"Anchor `{anchor.parent.name}/{anchor.name}`; MP2 rows `{Path(a.mp2_dz).name}`, `{Path(a.mp2_tz).name}` (symmetry spread "
          f"{s_dz:.1e} / {s_tz:.1e} a.u.; rms of the basis step {step_rms:.2e} a.u.){' in the plane frame' if a.planeframe else ''}. "
          f"Status: **{status}** ({n_im} imaginary).", "",
          "| lowest six vibrations (cm⁻¹) | values |", "|---|---|", f"| CC/DZ anchor | {six(f_dz)} |", f"| **composite** | **{six(f_comp)}** |"]
    md += [f"| {tag} (corpus) | {six(v)} |" for tag, v in dft.items()]
    write_text(Path(f"{a.out_prefix}.md"), "\n".join(md) + "\n")
    record = dict(date=stamp(), mol_id=a.mol_id, anchor=str(anchor), status=status, n_imaginary=n_im, freq_dz=f_dz.tolist(),
                  freq_composite=f_comp.tolist(), step_rms=step_rms, step_method=step_method, dft={k: v.tolist() for k, v in dft.items()},
                  spread=dict(dz=s_dz, tz=s_tz))
    write_text(Path(f"{a.out_prefix}.json"), json.dumps(record, indent=1))
    print("\n".join(md))
    return 0


# ---- test 2: the composite against the full CC/TZ anchor (6 Oct 2026)

def test2_verdict(comp: dict) -> tuple[dict[str, bool], str]:
    lines = {f: comp.get(f, 0.0) <= FAMILY_LINE_CM for f in FAMILIES if f in comp}
    if all(lines.values()):
        return lines, "composite within 3 cm⁻¹ of CC/TZ in every family"
    return lines, "3–10 cm⁻¹ in some family" if all(comp.get(f, 0.0) <= FAMILY_LOOSE_CM for f in FAMILIES) else "> 10 cm⁻¹ in a family"


def test2_report(a, res: dict, spreads: tuple[float, float], step_rms: float, lines: dict, verdict: str) -> list[str]:
    md = [f"# Composite anchor level, test 2 — {a.mol_id}: CC/DZ + [MP2/TZ − MP2/DZ] against the full CC/TZ anchor — {stamp()}", "",
          f"Anchors: DZ `{Path(a.dz_anchor).name}`, TZ `{Path(a.tz_anchor).name}`; MP2 rows `{Path(a.mp2_dz).name}`, `{Path(a.mp2_tz).name}` "
          f"(symmetry spread {spreads[0]:.1e} / {spreads[1]:.1e} a.u.); rms of the MP2 basis step over the Hessian {step_rms:.2e} a.u. Read-out: "
          "rms of corrected frequencies per family against CC/TZ (the B3LYP 6-31G* low level and the corpus modes, as in the T3 read-out); "
          "'B3LYP alone' is the zero rule.", "",
          "| read-out | B3LYP alone | CC/DZ (the anchors so far) | **composite** |", "|---|---|---|---|"]
    for f in (*FAMILIES, "all", "ratio"):
        digits = 3 if f == "ratio" else 2
        low, dz, comp = (res[k].get(f, float("nan")) for k in ("low", "dz", "comp"))
        md.append(f"| {f} | {low:.{digits}f} | {dz:.{digits}f} | **{comp:.{digits}f}** |")
    md += ["", f"**Lines:** {verdict} — " + ", ".join(f"{f} {'≤' if ok else '>'} 3" for f, ok in lines.items()) + "."]
    return md


def read(a) -> int:
    sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "m05"))
    from anchor_deck_rehearsal import readout, truth_of
    from rungC_train import load_corpus
    mol_dir = corpus_dir(a.mol_id)
    sym, x0, masses = load_geometry(mol_dir / "geometry.json")
    n = len(sym)
    ops = SYM.point_group_ops(sym, x0)
    _, reps = SYM.unique_displacements(ops, n)
    H_dz = load_anchor(Path(a.dz_anchor) / "hessian_ccsd_t.npz")[0]
    H_tz = load_anchor(Path(a.tz_anchor) / "hessian_ccsd_t.npz")[0]
    with np.load(mol_dir / "hessian_b3lyp_analytic.npz") as z:
        H_low = np.asarray(z["H_raw"], float)
    M_dz, M_tz, s_dz, s_tz = mp2_pair(a.mp2_dz, a.mp2_tz, ops, reps, n)
    mols, *_ = load_corpus(str(mol_dir.parent), True, log=lambda *_: None)
    m = mols[a.mol_id]
    Hp = {name: project_tr(H, masses, x0)[0] for name, H in (("low", H_low), ("dz", H_dz), ("tz", H_tz), ("comp", H_dz + (M_tz - M_dz)),
                                                              ("mp2_dz", M_dz), ("mp2_tz", M_tz))}
    truth = truth_of(m, Hp["tz"], Hp["low"])
    res = {name: readout(m, Hp[name], Hp["low"], truth) for name in ("dz", "comp", "low")}
    step_rms = float(np.sqrt(np.mean((M_tz - M_dz) ** 2)))
    lines, verdict = test2_verdict(res["comp"])
    md = test2_report(a, res, (s_dz, s_tz), step_rms, lines, verdict)
    write_text(Path(a.out_prefix + ".md"), "\n".join(md))
    record = dict(date=stamp(), mol_id=a.mol_id, dz_anchor=a.dz_anchor, tz_anchor=a.tz_anchor, mp2_dz=a.mp2_dz, mp2_tz=a.mp2_tz,
                  spread=dict(dz=s_dz, tz=s_tz), mp2_step_rms=step_rms, results=res, lines=lines, verdict=verdict)
    write_text(Path(a.out_prefix + ".json"), json.dumps(record, indent=1))
    print("\n".join(md))
    return 0


# ---- test 3: the out-of-plane repair (6 Oct 2026)

def anchor_file(anchor_dir: Path) -> Path:
    src = next((anchor_dir / f for f in ("hessian_ccsd_t_IMAGINARY.npz", "hessian_ccsd_t.npz") if (anchor_dir / f).exists()), None)
    if src is None:
        raise SystemExit(f"{anchor_dir}: no hessian_ccsd_t(_IMAGINARY).npz")
    return src


@dataclass(frozen=True)
class Repair:
    """The out-of-plane repair of one anchor: the composite in both frames, its frequencies and the checks beside them."""
    H_comp: np.ndarray
    H_comp_r: np.ndarray
    f_dz: np.ndarray
    f_comp: np.ndarray
    soft_dz: list
    soft_comp: list
    spreads: tuple[float, float]
    coupling_cc: float
    coupling_step: float


def repaired(a, pf: PlaneFrame, H: np.ndarray, x0: np.ndarray) -> Repair:
    n = len(pf.symbols)
    T = np.kron(np.eye(n), pf.V)                     # x − origin = T x_r  →  H_r = Tᵀ H T
    H_r = T.T @ H @ T
    ops = SYM.point_group_ops(pf.symbols, pf.coords)
    _, reps = SYM.unique_displacements(ops, n)
    M_dz, M_tz, s_dz, s_tz = mp2_pair(a.mp2_dz, a.mp2_tz, ops, reps, n, OUT_OF_PLANE)
    zi = np.arange(2, 3 * n, 3)
    ip = np.array([k for k in range(3 * n) if k % 3 != 2])
    step = np.zeros_like(H_r)
    step[np.ix_(zi, zi)] = (M_tz - M_dz)[np.ix_(zi, zi)]
    H_comp_r = H_r + step
    H_comp = T @ H_comp_r @ T.T
    normal = pf.V[:, 2]
    return Repair(H_comp, H_comp_r, frequencies_cm(H, pf.masses, x0), frequencies_cm(H_comp, pf.masses, x0),
                  oop_fraction(H, pf.masses, x0, normal), oop_fraction(H_comp, pf.masses, x0, normal), (s_dz, s_tz),
                  float(np.abs(H_r[np.ix_(zi, ip)]).max()),            # zero by symmetry for a planar molecule
                  float(np.abs((M_tz - M_dz)[np.ix_(zi, ip)]).max()))


def repair_verdict(f_comp: np.ndarray, ref: np.ndarray | None) -> tuple[int, str]:
    n_im = int((f_comp < IMAGINARY_CM).sum())
    if n_im:
        return n_im, "still imaginary: the artefact survives the MP2 basis step — the anchor stays excluded"
    if ref is not None and len(f_comp) >= 2 and np.abs(f_comp[:2] - ref[:2]).max() <= SOFT_LINE_CM:
        return n_im, "repaired: no imaginary mode and both soft modes within 40 cm⁻¹ of ωB97X — the composite anchor enters T3 (lines provisional)"
    return n_im, "repaired but flagged: real, yet a soft mode more than 40 cm⁻¹ from ωB97X — the full composite is computed before use"


def repair_report(a, src: Path, r: Repair, dft: dict, n_im: int, verdict: str) -> list[str]:
    md = [f"# Composite anchor level, test 3 — {a.mol_id}: out-of-plane repair of the CC/DZ anchor — {stamp()}", "",
          f"Anchor `{src.name}` ({Path(a.anchor_dir).name}); MP2 rows `{Path(a.mp2_dz).name}`, `{Path(a.mp2_tz).name}` (symmetry spread "
          f"{r.spreads[0]:.1e} / {r.spreads[1]:.1e} a.u.); in-plane/out-of-plane coupling: anchor {r.coupling_cc:.1e}, MP2 step "
          f"{r.coupling_step:.1e} a.u. (zero by symmetry for a planar molecule). Status of the composite: **{status_of(n_im)}** "
          f"({n_im} imaginary).", "",
          "| lowest six vibrations (cm⁻¹) | values |", "|---|---|",
          f"| CC/DZ anchor | {six(r.f_dz)} |", f"| **composite (out-of-plane block repaired)** | **{six(r.f_comp)}** |"]
    md += [f"| {tag} (corpus) | {six(v)} |" for tag, v in dft.items()]
    md += ["", "Two softest modes and their out-of-plane fraction: CC/DZ " + ", ".join(f"{f:.0f} ({p:.2f})" for f, p in r.soft_dz)
           + "; composite " + ", ".join(f"{f:.0f} ({p:.2f})" for f, p in r.soft_comp) + ".", "", f"**Lines:** {verdict}."]
    return md


def repair_oop(a) -> int:
    src = anchor_file(Path(a.anchor_dir))
    pf = load_planeframe(a.planeframe)
    H, x0 = load_anchor(src)
    pf.check(x0)
    r = repaired(a, pf, H, x0)
    dft = dft_reference(corpus_dir(a.mol_id))
    n_im, verdict = repair_verdict(r.f_comp, dft.get("wb97x"))
    status = status_of(n_im)
    save_npz(f"{a.out_prefix}.npz", H_raw=r.H_comp, H_projected=project_tr(r.H_comp, pf.masses, x0)[0], H_plane_frame=r.H_comp_r,
             freq_cm=r.f_comp, coords_bohr=x0, frame=pf.V, origin=pf.origin, status=status, source_anchor=str(src), mp2_dz=str(a.mp2_dz),
             mp2_tz=str(a.mp2_tz), spread_dz=r.spreads[0], spread_tz=r.spreads[1], coupling_cc=r.coupling_cc, coupling_step=r.coupling_step,
             repair="out-of-plane block, MP2/TZ − MP2/DZ (test 3, 6 Oct 2026)")
    md = repair_report(a, src, r, dft, n_im, verdict)
    write_text(Path(f"{a.out_prefix}.md"), "\n".join(md))
    record = dict(date=stamp(), mol_id=a.mol_id, anchor=str(src), status=status, n_imaginary=n_im, freq_dz=r.f_dz.tolist(),
                  freq_composite=r.f_comp.tolist(), dft={k: v.tolist() for k, v in dft.items()}, soft_dz=r.soft_dz, soft_composite=r.soft_comp,
                  spread=dict(dz=r.spreads[0], tz=r.spreads[1]), coupling=dict(anchor=r.coupling_cc, step=r.coupling_step), verdict=verdict)
    write_text(Path(f"{a.out_prefix}.json"), json.dumps(record, indent=1))
    print("\n".join(md))
    return 0


# ---- command line

def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("compute")
    for name in ("geometry", "out"):
        c.add_argument(name)
    c.add_argument("--basis", required=True)
    c.add_argument("--threads", type=int, default=4)
    c.add_argument("--step", type=float, default=0.005)
    c.add_argument("--frozen", default="auto")
    c.add_argument("--max-memory", type=int, default=12000)
    c.add_argument("--ks", default=None)
    c.add_argument("--cart", action="store_true", help="Cartesian d functions (the corpus's 6-31G* convention); the cc-pVnZ anchors are spherical")
    r = sub.add_parser("read")
    for name in ("dz_anchor", "tz_anchor", "mol_id", "mp2_dz", "mp2_tz", "out_prefix"):
        r.add_argument(name)
    p = sub.add_parser("planeframe")
    for name in ("geometry", "out"):
        p.add_argument(name)
    m = sub.add_parser("merge")
    m.add_argument("out")
    m.add_argument("parts", nargs="+")
    b = sub.add_parser("build", help="TASKS 28: the full composite anchor")
    for name in ("anchor", "mol_id", "mp2_dz", "mp2_tz", "out_prefix"):
        b.add_argument(name)
    b.add_argument("--planeframe", default=None, help="rows computed in this plane frame (cc_composite_full_check.py planeframe)")
    o = sub.add_parser("repair-oop")
    for name in ("anchor_dir", "mol_id", "planeframe", "mp2_dz", "mp2_tz", "out_prefix"):
        o.add_argument(name)
    return ap


def main() -> int:
    a = build_parser().parse_args()
    return {"compute": compute, "read": read, "planeframe": planeframe, "merge": merge, "repair-oop": repair_oop, "build": build}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
