"""E8 — is the coupled-cluster correction as local as the DFT proxy? (pre-registration PreRegistration_2026-09-23_E8_CC_Correction_Locality.md)

Inputs: the FD CCSD(T) Hessian of e8_cc_hessian_fd.py and the molecule's geometry. This script computes the reference DFT Hessians at the same basis
and geometry (pyscf analytic B3LYP and ωB97X, grid 99/590), forms ΔH_CC = H_CC − H_B3LYP and ΔH_proxy = H_ωB97X − H_B3LYP, and reads both through the
E7 post-hoc projections (vii)–(ix): minimum-norm internal ΔF = B⁺ᵀ ΔH B⁺ in geomeTRIC primitives, zeroed outside a pattern, back to Cartesian; per pattern
the ΔH residual ratio, the ring coupling ratio in the B3LYP mode basis, the corrected-frequency RMS. Self-contained (no torch): the descriptor helpers
of learning_curve_layerA_v2_descriptors are re-implemented here in their minimal form.

Usage: python e8_cc_locality.py <geometry.json> <hessian_ccsd_t.npz> <out prefix> [--threads 16] [--basis cc-pvdz]
"""
import argparse
import itertools
import json
import time
from datetime import datetime

import numpy as np

AMU2AU = 1822.888486209
HARTREE2CM = 219474.6313705
BOHR = 0.529177210903
COV = {"H": 0.31, "C": 0.76, "N": 0.71, "O": 0.66, "S": 1.05, "F": 0.57, "Cl": 1.02}


# ------------------------------------------------------------------------------------------------------------ helpers
def normal_modes(H, masses_amu):
    m = np.repeat(masses_amu * AMU2AU, 3); Hmw = H / np.sqrt(np.outer(m, m))
    w, V = np.linalg.eigh(Hmw); keep = np.argsort(np.abs(w))[6:]; keep = keep[np.argsort(w[keep])]
    w = w[keep]; V = V[:, keep]; freq = np.sign(w) * np.sqrt(np.abs(w)) * HARTREE2CM
    return w, freq, V


def project_tr(H, masses, x):
    n = len(masses); m = np.repeat(masses * AMU2AU, 3); sm = np.sqrt(m)
    com = (x * masses[:, None]).sum(0) / masses.sum(); r = x - com; D = []
    for k in range(3):
        v = np.zeros((n, 3)); v[:, k] = 1.0; D.append((v * np.sqrt(masses)[:, None]).ravel())
    for k in range(3):
        e = np.zeros(3); e[k] = 1.0; v = np.cross(np.tile(e, (n, 1)), r); D.append((v * np.sqrt(masses)[:, None]).ravel())
    D = np.array(D).T; q, _ = np.linalg.qr(D); P = np.eye(3 * n) - q @ q.T
    return (P @ (H / np.outer(sm, sm)) @ P) * np.outer(sm, sm)


def bond_graph(symbols, coords_bohr):
    x = np.asarray(coords_bohr) * BOHR; n = len(symbols); adj = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if np.linalg.norm(x[i] - x[j]) < 1.2 * (COV.get(symbols[i], 0.75) + COV.get(symbols[j], 0.75)):
                adj[i].add(j); adj[j].add(i)
    return adj


def rings(adj, max_len=7):
    found = set(); n = len(adj)
    for start in range(n):
        stack = [(start, [start])]
        while stack:
            v, path = stack.pop()
            for w in adj[v]:
                if w == start and len(path) >= 3:
                    found.add(frozenset(path))
                elif w not in path and len(path) < max_len and w > start:
                    stack.append((w, path + [w]))
    return [r for r in found if 5 <= len(r) <= max_len]


def families(freq, V, symbols, masses, coords_bohr):
    """The corpus family rule (learning_curve_layerA.molecule_features), minimal copy."""
    n = len(symbols); A = (V.reshape(n, 3, -1) ** 2).sum(1); sym = np.array(symbols)
    hshare = A[sym == "H"].sum(0) if (sym == "H").any() else np.zeros(V.shape[1])
    com = (coords_bohr * masses[:, None]).sum(0) / masses.sum(); x = coords_bohr - com
    I = sum(mm * (np.dot(r, r) * np.eye(3) - np.outer(r, r)) for r, mm in zip(x, masses)); ev, R = np.linalg.eigh(I); nrm = R[:, np.argmax(ev)]
    planar = float(np.abs(x @ nrm).max()) < 0.5
    Vn = (V.reshape(n, 3, -1) * nrm[None, :, None]).sum(1); oop = (Vn ** 2).sum(0) if planar else np.zeros(V.shape[1])
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


def internals(symbols, coords_bohr):
    from geometric.internal import Distance, PrimitiveInternalCoordinates
    from geometric.molecule import Molecule
    symbols = [s.capitalize() for s in symbols]
    M = Molecule(); M.elem = list(symbols); M.xyzs = [np.asarray(coords_bohr) * BOHR]
    ic = PrimitiveInternalCoordinates(M, build=True, connect=True, addcart=False)
    B = np.asarray(ic.wilsonB(np.asarray(coords_bohr, float).flatten()))
    prims = ic.Internals; n = len(prims)
    atoms = [set(getattr(p, k) for k in ("a", "b", "c", "d") if hasattr(p, k)) for p in prims]
    adj = bond_graph(symbols, coords_bohr); R = rings(adj)
    ring_of_bond = {}
    for k, p in enumerate(prims):
        if isinstance(p, Distance):
            for ri, r in enumerate(R):
                if p.a in r and p.b in r:
                    ring_of_bond.setdefault(k, set()).add(ri)
    share = np.zeros((n, n), bool); ringpair = np.zeros((n, n), bool)
    for i in range(n):
        for j in range(i, n):
            if atoms[i] & atoms[j]:
                share[i, j] = share[j, i] = True
            if i in ring_of_bond and j in ring_of_bond and (ring_of_bond[i] & ring_of_bond[j]):
                ringpair[i, j] = ringpair[j, i] = True
    diag = np.eye(n, dtype=bool)
    return B, {"(a) diagonal": diag, "(b) + atom-sharing pairs": share | diag, "(c) + ring bond-bond pairs": share | ringpair | diag}, n


def readout(dH_pred, dH_true, H_low, masses, freq, V, fam, w):
    """ΔH residual ratio, ring coupling ratio (K in the low-level mode basis), corrected-frequency RMS vs truth and vs zero rule."""
    m = np.repeat(masses * AMU2AU, 3); om = np.sqrt(np.abs(w))
    def K_of(dH):
        Km = V.T @ (dH / np.sqrt(np.outer(m, m))) @ V
        return Km / (2 * np.sqrt(np.outer(om, om))) * HARTREE2CM
    Kt, Kp = K_of(dH_true), K_of(dH_pred)
    r = np.where(fam == "ring-ip")[0]; iu = np.triu_indices(len(r), 1)
    ct = Kt[np.ix_(r, r)][iu]; cp = Kp[np.ix_(r, r)][iu]
    same = fam[:, None] == fam[None, :]; S = np.sqrt(np.outer(np.abs(freq), np.abs(freq)))
    def corrected(K):
        Kb = np.where(same, K, 0.0); Kb = 0.5 * (Kb + Kb.T); return np.sqrt(np.abs(np.linalg.eigvalsh(np.diag(freq ** 2) + 2 * S * Kb)))
    wt, wp, w0 = corrected(Kt), corrected(Kp), corrected(np.zeros_like(Kt))
    return dict(dH_residual_ratio=float(np.sqrt(np.mean((dH_pred - dH_true) ** 2) / np.mean(dH_true ** 2))),
                ring_coupling_ratio=float(np.sqrt(np.mean((cp - ct) ** 2) / np.mean(ct ** 2))),
                ring_diag_rms=float(np.sqrt(np.mean((np.diag(Kp) - np.diag(Kt))[fam == "ring-ip"] ** 2))),
                corrected_freq_rms=float(np.sqrt(np.mean((wp - wt) ** 2))), corrected_freq_rms_zero_rule=float(np.sqrt(np.mean((w0 - wt) ** 2))))


# ------------------------------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("geometry"); ap.add_argument("cc_hessian"); ap.add_argument("out_prefix")
    ap.add_argument("--threads", type=int, default=16); ap.add_argument("--basis", default="cc-pvdz")
    a = ap.parse_args(); t0 = time.time()
    from pyscf import dft, gto, lib
    lib.num_threads(a.threads)
    g = json.load(open(a.geometry)); sym = [s.capitalize() for s in g["symbols"]]; x = np.array(g["coords_bohr"], float); masses = np.array(g["masses_amu"])
    cc = np.load(a.cc_hessian); H_cc = cc["H_projected"]
    mol = gto.M(atom=[(s, tuple(c)) for s, c in zip(sym, x)], unit="Bohr", basis=a.basis, symmetry=False, verbose=0, max_memory=26000)
    H = {}
    for tag, xc in (("b3lyp", "b3lyp"), ("wb97x", "wb97x")):
        t1 = time.time(); mf = dft.RKS(mol); mf.xc = xc; mf.grids.atom_grid = (99, 590); mf.grids.prune = None; mf.conv_tol = 1e-11; mf.kernel()
        Hh = mf.Hessian().kernel(); n = len(sym); Hc = Hh.transpose(0, 2, 1, 3).reshape(3 * n, 3 * n); Hc = 0.5 * (Hc + Hc.T)
        H[tag] = project_tr(Hc, masses, x); print(f"{tag}/{a.basis} analytic Hessian: {time.time() - t1:.0f} s", flush=True)
    w, freq, V = normal_modes(H["b3lyp"], masses); fam = families(freq, V, sym, masses, x)
    print("B3LYP/" + a.basis + " frequencies:", np.round(freq, 0).astype(int).tolist()); print("families:", {F: int((fam == F).sum()) for F in ("CH-stretch", "CH-oop", "ring-ip", "other")})
    _, fcc, _ = normal_modes(H_cc, masses); print("CCSD(T) FD frequencies:", np.round(fcc, 0).astype(int).tolist())
    B, patterns, n_ic = internals(sym, x); Bp = np.linalg.pinv(B)
    res = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "basis": a.basis, "n_internals": int(n_ic), "freq_b3lyp": freq.tolist(), "freq_ccsd_t": fcc.tolist(),
           "freq_wb97x": normal_modes(H["wb97x"], masses)[1].tolist(), "patterns": {}}
    dHs = {"CC − B3LYP": H_cc - H["b3lyp"], "proxy ωB97X − B3LYP": H["wb97x"] - H["b3lyp"]}
    res["norms"] = {k: float(np.sqrt(np.mean(v ** 2))) for k, v in dHs.items()}
    print(f"RMS of ΔH (a.u.): " + ", ".join(f"{k} {v:.2e}" for k, v in res["norms"].items()), flush=True)
    dF = {k: Bp.T @ v @ Bp for k, v in dHs.items()}
    for pname, pat in patterns.items():
        res["patterns"][pname] = {}
        for k in dHs:
            pred = B.T @ (dF[k] * pat) @ B
            r = readout(pred, dHs[k], H["b3lyp"], masses, freq, V, fam, w); res["patterns"][pname][k] = r
            print(f"{pname:28s} {k:22s} ΔH residual {r['dH_residual_ratio']:.2f} | ring coupling ratio {r['ring_coupling_ratio']:.2f} | ring diag {r['ring_diag_rms']:6.2f} | corrected ω {r['corrected_freq_rms']:.2f} (zero {r['corrected_freq_rms_zero_rule']:.2f})", flush=True)
    pc = patterns["(c) + ring bond-bond pairs"]; iu = np.triu_indices(n_ic)
    vc, vp = (dF["CC − B3LYP"] * pc)[iu], (dF["proxy ωB97X − B3LYP"] * pc)[iu]; sel = pc[iu]
    res["exploratory"] = {"corr_CC_vs_proxy_on_pattern_c": float(np.corrcoef(vc[sel], vp[sel])[0, 1]), "norm_ratio_CC_over_proxy": float(np.linalg.norm(vc[sel]) / np.linalg.norm(vp[sel]))}
    print("exploratory: element-wise correlation of ΔF_CC and ΔF_proxy on pattern (c):", round(res["exploratory"]["corr_CC_vs_proxy_on_pattern_c"], 3), "| norm ratio CC/proxy:", round(res["exploratory"]["norm_ratio_CC_over_proxy"], 2))
    rc = res["patterns"]["(c) + ring bond-bond pairs"]["CC − B3LYP"]
    verdict = "WIN" if (rc["dH_residual_ratio"] <= 0.35 and rc["ring_coupling_ratio"] <= 0.5) else ("LOSE" if rc["dH_residual_ratio"] >= 0.55 else "between")
    res["verdict"] = verdict; res["seconds"] = round(time.time() - t0)
    json.dump(res, open(a.out_prefix + ".json", "w"), indent=1)
    md = [f"# E8 — locality of the CCSD(T) − B3LYP correction, {a.basis} ({res['date']})", "",
          f"ΔH RMS (a.u.): CC − B3LYP {res['norms']['CC − B3LYP']:.2e}, proxy {res['norms']['proxy ωB97X − B3LYP']:.2e}. Internals: {n_ic}. Parameter-free projections of the minimum-norm internal correction.", "",
          "| pattern | correction | ΔH residual ratio | ring coupling ratio | ring diag RMS | corrected ω RMS (zero rule) |", "|---|---|---|---|---|---|"]
    for pname in patterns:
        for k in dHs:
            r = res["patterns"][pname][k]
            md.append(f"| {pname} | {k} | {r['dH_residual_ratio']:.2f} | **{r['ring_coupling_ratio']:.2f}** | {r['ring_diag_rms']:.2f} | {r['corrected_freq_rms']:.2f} ({r['corrected_freq_rms_zero_rule']:.2f}) |")
    md += ["", f"Exploratory: correlation of ΔF_CC and ΔF_proxy on pattern (c) {res['exploratory']['corr_CC_vs_proxy_on_pattern_c']:.3f}; norm ratio CC/proxy {res['exploratory']['norm_ratio_CC_over_proxy']:.2f}.",
           f"**Verdict (pre-registered):** pattern (c) residual {rc['dH_residual_ratio']:.2f}, ring coupling ratio {rc['ring_coupling_ratio']:.2f} → **{verdict}**.", f"Total {res['seconds']} s."]
    open(a.out_prefix + ".md", "w", encoding="utf-8").write("\n".join(md) + "\n"); print("wrote", a.out_prefix, "verdict", verdict)


if __name__ == "__main__":
    main()
