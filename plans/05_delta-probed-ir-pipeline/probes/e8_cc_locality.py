"""E8 — is the coupled-cluster correction as local as the DFT proxy? (pre-registration PreRegistration_2026-09-23_E8_CC_Correction_Locality.md)

Inputs: the FD CCSD(T) Hessian of e8_cc_hessian_fd.py and the molecule's geometry. This script computes the reference DFT Hessians at the same basis
and geometry (pyscf analytic B3LYP and ωB97X, grid 99/590), forms ΔH_CC = H_CC − H_B3LYP and ΔH_proxy = H_ωB97X − H_B3LYP, and reads both through the
E7 post-hoc projections (vii)–(ix): minimum-norm internal ΔF = B⁺ᵀ ΔH B⁺ in geomeTRIC primitives, zeroed outside a pattern, back to Cartesian; per pattern
the ΔH residual ratio, the ring coupling ratio in the B3LYP mode basis, the corrected-frequency RMS. Self-contained (no torch): the descriptor helpers
of learning_curve_layerA_v2_descriptors are re-implemented here in their minimal form (s2_read, qff_noise_diagnosis and geometry_symmetry_survey
import them from here).

Usage: python e8_cc_locality.py <geometry.json> <hessian_ccsd_t.npz> <out prefix> [--threads 16] [--basis cc-pvdz]
"""
import argparse
import json
import os
import time
from datetime import datetime
from pathlib import Path

import numpy as np
from qc_common import AMU2AU, HARTREE2CM, project_tr

BOHR = 0.529177210903
COV = {"H": 0.31, "C": 0.76, "N": 0.71, "O": 0.66, "S": 1.05, "F": 0.57, "Cl": 1.02}
BOND_FACTOR = 1.2               # bonded when closer than 1.2 × the sum of covalent radii
PLANAR_BOHR = 0.5               # planar when every atom lies within 0.5 bohr of the plane
WIN_RESIDUAL, WIN_RING, LOSE_RESIDUAL = 0.35, 0.5, 0.55     # the pre-registered verdict lines on pattern (c)
PATTERN_C = "(c) + ring bond-bond pairs"
CC_KEY, PROXY_KEY = "CC − B3LYP", "proxy ωB97X − B3LYP"
FAMILY_NAMES = ("CH-stretch", "CH-oop", "ring-ip", "other")


# ------------------------------------------------------------------------------------------------------------ helpers
def normal_modes(H, masses_amu):
    m = np.repeat(masses_amu * AMU2AU, 3)
    w, V = np.linalg.eigh(H / np.sqrt(np.outer(m, m)))
    keep = np.argsort(np.abs(w))[6:]
    keep = keep[np.argsort(w[keep])]
    w = w[keep]
    V = V[:, keep]
    return w, np.sign(w) * np.sqrt(np.abs(w)) * HARTREE2CM, V


def bond_graph(symbols, coords_bohr):
    x = np.asarray(coords_bohr) * BOHR
    n = len(symbols)
    adj = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if np.linalg.norm(x[i] - x[j]) < BOND_FACTOR * (COV.get(symbols[i], 0.75) + COV.get(symbols[j], 0.75)):
                adj[i].add(j)
                adj[j].add(i)
    return adj


def rings(adj, max_len=7):
    found = set()
    for start in range(len(adj)):
        stack = [(start, [start])]
        while stack:
            v, path = stack.pop()
            for w in adj[v]:
                if w == start and len(path) >= 3:
                    found.add(frozenset(path))
                elif w not in path and len(path) < max_len and w > start:
                    stack.append((w, [*path, w]))
    return [r for r in found if 5 <= len(r) <= max_len]


def mode_shares(V, symbols, masses, coords_bohr):
    """Per mode of the mass-weighted modes V (3N × M): the hydrogen share, the share along the normal of the largest principal moment
    (the molecular plane's normal for a planar molecule), and whether the molecule is planar (every atom within 0.5 bohr of that plane)."""
    n = len(symbols)
    A = (V.reshape(n, 3, -1) ** 2).sum(1)
    sym = np.array(symbols)
    hshare = A[sym == "H"].sum(0) if (sym == "H").any() else np.zeros(V.shape[1])
    x = coords_bohr - (coords_bohr * masses[:, None]).sum(0) / masses.sum()
    inertia = sum(mm * (np.dot(r, r) * np.eye(3) - np.outer(r, r)) for r, mm in zip(x, masses, strict=True))
    ev, R = np.linalg.eigh(inertia)
    nrm = R[:, np.argmax(ev)]
    planar = float(np.abs(x @ nrm).max()) < PLANAR_BOHR
    Vn = (V.reshape(n, 3, -1) * nrm[None, :, None]).sum(1)
    return hshare, (Vn ** 2).sum(0), planar


def families(freq, V, symbols, masses, coords_bohr):
    """The corpus family rule (learning_curve_layerA.molecule_features), minimal copy."""
    hshare, oop, planar = mode_shares(V, symbols, masses, coords_bohr)
    if not planar:
        oop = np.zeros(V.shape[1])
    fam = []
    for i, f in enumerate(freq):
        if f > 2800 and hshare[i] > 0.5:
            fam.append("CH-stretch")
        elif 600 < f < 1050 and oop[i] > 0.6 and hshare[i] > 0.3:
            fam.append("CH-oop")
        elif 950 < f < 1750 and oop[i] < 0.3:
            fam.append("ring-ip")
        else:
            fam.append("other")
    return np.array(fam)


def _ring_bonds(prims, symbols, coords_bohr) -> dict[int, set]:
    """Per bond primitive, the rings (5–7 members) both its atoms belong to."""
    from geometric.internal import Distance
    R = rings(bond_graph(symbols, coords_bohr))
    ring_of_bond = {}
    for k, p in enumerate(prims):
        if isinstance(p, Distance):
            for ri, r in enumerate(R):
                if p.a in r and p.b in r:
                    ring_of_bond.setdefault(k, set()).add(ri)
    return ring_of_bond


def primitives(symbols, coords_bohr) -> tuple[list, np.ndarray]:
    """geomeTRIC's primitive internal coordinates of the molecule and Wilson's B over them."""
    from geometric.internal import PrimitiveInternalCoordinates
    from geometric.molecule import Molecule
    M = Molecule()
    M.elem = [s.capitalize() for s in symbols]
    M.xyzs = [np.asarray(coords_bohr) * BOHR]
    ic = PrimitiveInternalCoordinates(M, build=True, connect=True, addcart=False)
    return ic.Internals, np.asarray(ic.wilsonB(np.asarray(coords_bohr, float).flatten()))


def primitive_atoms(prims) -> list[set]:
    return [{getattr(p, k) for k in ("a", "b", "c", "d") if hasattr(p, k)} for p in prims]


def pattern_masks(prims, symbols, coords_bohr) -> dict[str, np.ndarray]:
    """The three registered patterns over the primitives: (a) the diagonal, (b) + pairs sharing an atom, (c) + bond-bond pairs in a common ring."""
    symbols = [s.capitalize() for s in symbols]
    n = len(prims)
    atoms = primitive_atoms(prims)
    ring_of_bond = _ring_bonds(prims, symbols, coords_bohr)
    share = np.zeros((n, n), bool)
    ringpair = np.zeros((n, n), bool)
    for i in range(n):
        for j in range(i, n):
            if atoms[i] & atoms[j]:
                share[i, j] = share[j, i] = True
            if i in ring_of_bond and j in ring_of_bond and (ring_of_bond[i] & ring_of_bond[j]):
                ringpair[i, j] = ringpair[j, i] = True
    diag = np.eye(n, dtype=bool)
    return {"(a) diagonal": diag, "(b) + atom-sharing pairs": share | diag, PATTERN_C: share | ringpair | diag}


def internals(symbols, coords_bohr):
    """(Wilson's B in geomeTRIC primitives, the three registered patterns over them, the number of primitives)."""
    prims, B = primitives(symbols, coords_bohr)
    return B, pattern_masks(prims, symbols, coords_bohr), len(prims)


def readout(dH_pred, dH_true, H_low, masses, freq, V, fam, w):  # noqa: PLR0913  (H_low unused; e8_between_extension calls it with it)
    """ΔH residual ratio, ring coupling ratio (K in the low-level mode basis), corrected-frequency RMS vs truth and vs zero rule."""
    m = np.repeat(masses * AMU2AU, 3)
    om = np.sqrt(np.abs(w))

    def K_of(dH):
        Km = V.T @ (dH / np.sqrt(np.outer(m, m))) @ V
        return Km / (2 * np.sqrt(np.outer(om, om))) * HARTREE2CM
    Kt, Kp = K_of(dH_true), K_of(dH_pred)
    r = np.where(fam == "ring-ip")[0]
    iu = np.triu_indices(len(r), 1)
    ct = Kt[np.ix_(r, r)][iu]
    cp = Kp[np.ix_(r, r)][iu]
    same = fam[:, None] == fam[None, :]
    S = np.sqrt(np.outer(np.abs(freq), np.abs(freq)))

    def corrected(K):
        Kb = np.where(same, K, 0.0)
        Kb = 0.5 * (Kb + Kb.T)
        return np.sqrt(np.abs(np.linalg.eigvalsh(np.diag(freq ** 2) + 2 * S * Kb)))
    wt, wp, w0 = corrected(Kt), corrected(Kp), corrected(np.zeros_like(Kt))
    return dict(dH_residual_ratio=float(np.sqrt(np.mean((dH_pred - dH_true) ** 2) / np.mean(dH_true ** 2))),
                ring_coupling_ratio=float(np.sqrt(np.mean((cp - ct) ** 2) / np.mean(ct ** 2))),
                ring_diag_rms=float(np.sqrt(np.mean((np.diag(Kp) - np.diag(Kt))[fam == "ring-ip"] ** 2))),
                corrected_freq_rms=float(np.sqrt(np.mean((wp - wt) ** 2))), corrected_freq_rms_zero_rule=float(np.sqrt(np.mean((w0 - wt) ** 2))))


# ------------------------------------------------------------------------------------------------------------- main
def dft_hessians(symbols, x, masses, basis: str) -> dict[str, np.ndarray]:
    """The analytic B3LYP and ωB97X Hessians (grid 99/590, unpruned), symmetrised, translations and rotations projected out."""
    from pyscf import dft, gto
    mol = gto.M(atom=[(s, tuple(c)) for s, c in zip(symbols, x, strict=True)], unit="Bohr", basis=basis, symmetry=False, verbose=0, max_memory=26000)
    n = len(symbols)
    H = {}
    for tag, xc in (("b3lyp", "b3lyp"), ("wb97x", "wb97x")):
        t1 = time.time()
        mf = dft.RKS(mol)
        mf.xc = xc
        mf.grids.atom_grid = (99, 590)
        mf.grids.prune = None
        mf.conv_tol = 1e-11
        mf.kernel()
        Hc = mf.Hessian().kernel().transpose(0, 2, 1, 3).reshape(3 * n, 3 * n)
        H[tag] = project_tr(0.5 * (Hc + Hc.T), masses, x)[0]
        print(f"{tag}/{basis} analytic Hessian: {time.time() - t1:.0f} s", flush=True)
    return H


def pattern_reads(dHs: dict, patterns: dict, B: np.ndarray, modes: tuple, H_low, masses) -> tuple[dict, dict]:
    """(read per pattern and correction, the minimum-norm internal ΔF per correction)."""
    w, freq, V, fam = modes
    Bp = np.linalg.pinv(B)
    dF = {k: Bp.T @ v @ Bp for k, v in dHs.items()}
    reads = {}
    for pname, pat in patterns.items():
        reads[pname] = {}
        for k in dHs:
            r = readout(B.T @ (dF[k] * pat) @ B, dHs[k], H_low, masses, freq, V, fam, w)
            reads[pname][k] = r
            print(f"{pname:28s} {k:22s} ΔH residual {r['dH_residual_ratio']:.2f} | ring coupling ratio {r['ring_coupling_ratio']:.2f} | ring diag "
                  f"{r['ring_diag_rms']:6.2f} | corrected ω {r['corrected_freq_rms']:.2f} (zero {r['corrected_freq_rms_zero_rule']:.2f})", flush=True)
    return reads, dF


def exploratory(dF: dict, pattern: np.ndarray, n_ic: int) -> dict:
    iu = np.triu_indices(n_ic)
    vc, vp = (dF[CC_KEY] * pattern)[iu], (dF[PROXY_KEY] * pattern)[iu]
    sel = pattern[iu]
    return {"corr_CC_vs_proxy_on_pattern_c": float(np.corrcoef(vc[sel], vp[sel])[0, 1]),
            "norm_ratio_CC_over_proxy": float(np.linalg.norm(vc[sel]) / np.linalg.norm(vp[sel]))}


def verdict_of(rc: dict) -> str:
    if rc["dH_residual_ratio"] <= WIN_RESIDUAL and rc["ring_coupling_ratio"] <= WIN_RING:
        return "WIN"
    return "LOSE" if rc["dH_residual_ratio"] >= LOSE_RESIDUAL else "between"


def report_lines(res: dict, basis: str, n_ic: int) -> list[str]:
    rc = res["patterns"][PATTERN_C][CC_KEY]
    md = [f"# E8 — locality of the CCSD(T) − B3LYP correction, {basis} ({res['date']})", "",
          f"ΔH RMS (a.u.): CC − B3LYP {res['norms'][CC_KEY]:.2e}, proxy {res['norms'][PROXY_KEY]:.2e}. Internals: {n_ic}. Parameter-free "
          "projections of the minimum-norm internal correction.", "",
          "| pattern | correction | ΔH residual ratio | ring coupling ratio | ring diag RMS | corrected ω RMS (zero rule) |", "|---|---|---|---|---|---|"]
    for pname, reads in res["patterns"].items():
        for k, r in reads.items():
            md.append(f"| {pname} | {k} | {r['dH_residual_ratio']:.2f} | **{r['ring_coupling_ratio']:.2f}** | {r['ring_diag_rms']:.2f} | "
                      f"{r['corrected_freq_rms']:.2f} ({r['corrected_freq_rms_zero_rule']:.2f}) |")
    ex = res["exploratory"]
    md += ["", f"Exploratory: correlation of ΔF_CC and ΔF_proxy on pattern (c) {ex['corr_CC_vs_proxy_on_pattern_c']:.3f}; norm ratio CC/proxy "
           f"{ex['norm_ratio_CC_over_proxy']:.2f}.",
           f"**Verdict (pre-registered):** pattern (c) residual {rc['dH_residual_ratio']:.2f}, ring coupling ratio {rc['ring_coupling_ratio']:.2f} → "
           f"**{res['verdict']}**.", f"Total {res['seconds']} s."]
    return md


def write_text(path: str, text: str) -> None:
    tmp = path + ".tmp"
    Path(tmp).write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def main():
    ap = argparse.ArgumentParser()
    for name in ("geometry", "cc_hessian", "out_prefix"):
        ap.add_argument(name)
    ap.add_argument("--threads", type=int, default=16)
    ap.add_argument("--basis", default="cc-pvdz")
    a = ap.parse_args()
    t0 = time.time()
    from pyscf import lib
    lib.num_threads(a.threads)
    g = json.loads(Path(a.geometry).read_text())
    sym, x, masses = [s.capitalize() for s in g["symbols"]], np.array(g["coords_bohr"], float), np.array(g["masses_amu"])
    with np.load(a.cc_hessian) as z:
        H_cc = z["H_projected"]
    H = dft_hessians(sym, x, masses, a.basis)
    w, freq, V = normal_modes(H["b3lyp"], masses)
    fam = families(freq, V, sym, masses, x)
    print("B3LYP/" + a.basis + " frequencies:", np.round(freq, 0).astype(int).tolist())
    print("families:", {F: int((fam == F).sum()) for F in FAMILY_NAMES})
    _, fcc, _ = normal_modes(H_cc, masses)
    print("CCSD(T) FD frequencies:", np.round(fcc, 0).astype(int).tolist())
    B, patterns, n_ic = internals(sym, x)
    res = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "basis": a.basis, "n_internals": int(n_ic), "freq_b3lyp": freq.tolist(),
           "freq_ccsd_t": fcc.tolist(), "freq_wb97x": normal_modes(H["wb97x"], masses)[1].tolist(), "patterns": {}}
    dHs = {CC_KEY: H_cc - H["b3lyp"], PROXY_KEY: H["wb97x"] - H["b3lyp"]}
    res["norms"] = {k: float(np.sqrt(np.mean(v ** 2))) for k, v in dHs.items()}
    print("RMS of ΔH (a.u.): " + ", ".join(f"{k} {v:.2e}" for k, v in res["norms"].items()), flush=True)
    res["patterns"], dF = pattern_reads(dHs, patterns, B, (w, freq, V, fam), H["b3lyp"], masses)
    res["exploratory"] = exploratory(dF, patterns[PATTERN_C], n_ic)
    print("exploratory: element-wise correlation of ΔF_CC and ΔF_proxy on pattern (c):", round(res["exploratory"]["corr_CC_vs_proxy_on_pattern_c"], 3),
          "| norm ratio CC/proxy:", round(res["exploratory"]["norm_ratio_CC_over_proxy"], 2))
    res["verdict"] = verdict_of(res["patterns"][PATTERN_C][CC_KEY])
    res["seconds"] = round(time.time() - t0)
    write_text(a.out_prefix + ".json", json.dumps(res, indent=1))
    write_text(a.out_prefix + ".md", "\n".join(report_lines(res, a.basis, n_ic)) + "\n")
    print("wrote", a.out_prefix, "verdict", res["verdict"])


if __name__ == "__main__":
    main()
