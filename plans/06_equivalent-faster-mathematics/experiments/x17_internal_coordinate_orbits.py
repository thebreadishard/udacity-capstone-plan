"""X17 (2026-09-13) — lead D of the reflection, first desk test: is the CC−DFT Hessian correction COMPACT in internal coordinates?

Question. X8 showed the correction is not sparse in Cartesian atom blocks and X15 that it has no low-rank far field. Lead D asks the
older question of the scaled-quantum-mechanical (SQM) force-field lineage (Pulay et al. 1983; Rauhut & Pulay 1995; Baker, Jarzecki &
Pulay 1998 — Crossref-verified 13 September): expressed as corrections to force constants in redundant INTERNAL coordinates (bond
stretches, angle bends, out-of-plane wags, ring torsions), grouped into symmetry orbits, how many orbit parameters reproduce the
per-mode correction to band accuracy — and does the σ skeleton (C–H stretch, C–C–H bend, C–H wag) carry a separate, small part
from the π-related ring part (C–C stretch, C–C–C bend, ring torsion)?

Model. ΔH_cart ≈ Bᵀ ΔF B with B the Wilson B-matrix of a declared redundant internal set (numerical derivatives of the coordinate
functions) and ΔF a symmetric internal force-constant correction whose entries are constant on ORBITS: pairs of internal coordinates
(i, j) ~ (π(i), π(j)) under the molecule's permutation symmetry (the point-group operations found numerically from the geometry).
One free parameter per orbit; the fit is linear least squares of the effect in the B3LYP MODE basis (Lᵀ M^{-1/2} Bᵀ ΔF B M^{-1/2} L
against Δ₂_Q), so redundancy of the internal set cannot make the RESIDUAL non-unique — only the parameters, which are therefore not
reported as physics (the reflection's caveat). Nested parameter sets, each read per mode against the first-order shift
δν_i = Δ_ii/(2ω_i) and after full re-diagonalisation:
  S0  diagonal orbits only (one constant per coordinate type)                       — the SQM "scale factor" limit
  S1  S0 + couplings between internals sharing an atom (nearest neighbours)         — a valence force field's usual reach
  S2  S1 + couplings between internals one bond apart                                — second neighbours
  S3  all orbits                                                                     — the symmetric limit (exact if B spans the space)
and the σ/π question as two fits with S3 parameters restricted to σ-type or π-type coordinates (couplings between the two classes
counted separately).
Reading (fixed before running): "compact" = S1 reaches RMS first-order error ≤ 0.5 cm⁻¹ (plan 06's band threshold, X8/X15) or at least
≤ 2.5 cm⁻¹ (Module 03's u_band); the Kekulé B2u mode's residual is printed on its own because it is the largest correction (−36 cm⁻¹
in the stand-in). Stand-in: BHHLYP − B3LYP at benzene (plan 05 stageA_hessians.npz), as in every desk experiment; a real CC tensor
replaces it at R0. Every number from the files; constants in CONSTANTS. Output: x17_<molecule>.md/.json beside this script."""
import argparse
import itertools
import json
from datetime import datetime
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
P05 = HERE.parents[1] / "05_delta-probed-ir-pipeline" / "probes" / "results_dryrun"
HARTREE_TO_CM = 219474.6313632
CONSTANTS = {"thresholds_cm": [0.5, 2.5], "bond_cutoff_bohr": {"CC": 3.2, "CH": 2.3}, "fd_step_bohr": 1e-4, "sym_tol_bohr": 1e-3,
             "sigma_types": ["CH", "CCH", "wag"], "pi_types": ["CC", "CCC", "tors"], "kekule_hint": "the B2u C–C stretch mode ≈ 1357 cm⁻¹ (largest stand-in correction)"}


def load(mol):
    z = np.load(P05 / mol / "stageA_hessians.npz"); a = json.load(open(P05 / mol / "stageA.json"))
    return {"coords": np.array(z["coords"], float), "H_low": z["H_low"], "H_high": z["H_high"], "L": z["L"], "omega": z["omega_au"], "D2Q": z["D2_direct_Q"],
            "Minv": z["Minv"], "symbols": a["symbols"], "freq": np.array(a["freq_low_cm"]), "fam": a["families"]}


# ---- internal coordinates -------------------------------------------------------------------------------------------------
def bonds_of(coords, symbols):
    n = len(symbols); B = []
    for i, j in itertools.combinations(range(n), 2):
        t = "".join(sorted(symbols[i] + symbols[j])); d = np.linalg.norm(coords[i] - coords[j])
        cut = CONSTANTS["bond_cutoff_bohr"].get(t)
        if cut and d < cut: B.append((i, j))
    return B


def internal_set(coords, symbols):
    """Declared redundant set: all bonds; all angles i-j-k over bonded pairs; out-of-plane wags of every H (angle of the C–H bond with
    the plane of the carbon's other two bonds); torsions i-j-k-l along every ring C–C bond (one per bond: the two ring neighbours)."""
    bonds = bonds_of(coords, symbols); nb = {i: set() for i in range(len(symbols))}
    for i, j in bonds: nb[i].add(j); nb[j].add(i)
    ic = []
    for i, j in bonds: ic.append(("CC" if symbols[i] == symbols[j] == "C" else "CH", (i, j)))
    for j in range(len(symbols)):
        for i, k in itertools.combinations(sorted(nb[j]), 2):
            typ = "CCC" if symbols[i] == symbols[k] == "C" else "CCH"; ic.append((typ, (i, j, k)))
    for h in range(len(symbols)):
        if symbols[h] == "H":
            c = next(iter(nb[h])); others = sorted(nb[c] - {h}); ic.append(("wag", (h, c, others[0], others[1])))
    for i, j in bonds:
        if symbols[i] == symbols[j] == "C":
            a = sorted(x for x in nb[i] if x != j and symbols[x] == "C"); b = sorted(x for x in nb[j] if x != i and symbols[x] == "C")
            if a and b: ic.append(("tors", (a[0], i, j, b[0])))
    return ic, bonds


def q_value(typ, idx, X):
    if typ in ("CC", "CH"):
        return np.linalg.norm(X[idx[0]] - X[idx[1]])
    if typ in ("CCC", "CCH"):
        u = X[idx[0]] - X[idx[1]]; v = X[idx[2]] - X[idx[1]]
        return np.arccos(np.clip(u @ v / np.linalg.norm(u) / np.linalg.norm(v), -1, 1))
    if typ == "wag":
        h, c, a, b = idx; n = np.cross(X[a] - X[c], X[b] - X[c]); n /= np.linalg.norm(n); u = X[h] - X[c]; u /= np.linalg.norm(u)
        return np.arcsin(np.clip(n @ u, -1, 1))
    if typ == "tors":
        a, b, c, d = idx; b1 = X[b] - X[a]; b2 = X[c] - X[b]; b3 = X[d] - X[c]
        n1 = np.cross(b1, b2); n2 = np.cross(b2, b3); m = np.cross(n1, b2 / np.linalg.norm(b2))
        return np.arctan2(m @ n2, n1 @ n2)
    raise ValueError(typ)


def b_matrix(ic, coords):
    h = CONSTANTS["fd_step_bohr"]; n3 = coords.size; B = np.zeros((len(ic), n3))
    for r, (typ, idx) in enumerate(ic):
        for k in range(n3):
            Xp = coords.copy().reshape(-1); Xm = Xp.copy(); Xp[k] += h; Xm[k] -= h
            B[r, k] = (q_value(typ, idx, Xp.reshape(-1, 3)) - q_value(typ, idx, Xm.reshape(-1, 3))) / (2 * h)
    return B


# ---- symmetry: operations from the geometry, with the SIGN of every internal coordinate under each operation -----------------
def operations_of(coords, symbols):
    """All point-group operations that map the geometry onto itself (rotations by k·2π/n about z, vertical reflections, σh and
    products), each as (R, permutation π with atom k -> π(k)). Distinct operations are kept even when they share a permutation
    (σh has the identity permutation but flips every out-of-plane coordinate — this sign is what makes an orbit fit exact)."""
    X = coords - coords.mean(0); tol = CONSTANTS["sym_tol_bohr"]; ops = {}
    def perm_of(R):
        Y = X @ R.T; p = []
        for y in Y:
            d = np.linalg.norm(X - y, axis=1); k = int(np.argmin(d))
            if d[k] > tol or symbols[k] != symbols[len(p)]: return None
            p.append(k)
        return tuple(p) if len(set(p)) == len(p) else None
    cands = []
    for n in (12, 6, 4, 3, 2):
        for k in range(n):
            th = 2 * np.pi * k / n; Rz = np.array([[np.cos(th), -np.sin(th), 0], [np.sin(th), np.cos(th), 0], [0, 0, 1]])
            cands += [Rz, Rz @ np.diag([1, -1, 1]), Rz @ np.diag([1, 1, -1]), Rz @ np.diag([1, -1, -1])]
    for R in cands:
        p = perm_of(R)
        if p: ops[tuple(np.round(R, 6).ravel())] = (R, p)
    return list(ops.values())


def coordinate_images(ic, B, ops):
    """For each operation g = (R, π) and coordinate r: the image coordinate r' (atoms mapped by π) and the sign s with
    q_r(gX) = s · q_{r'}(X), read from the B-matrix rows: B_r·(gδ) = W·δ with W_k = Rᵀ B_r[π(k)], and W must equal ± B_{r'}
    (asserted: |cos(W, B_{r'})| = 1 within 1e-6). No random distortions, no division by small numbers."""
    key = {canon(t, i): r for r, (t, i) in enumerate(ic)}; nat = B.shape[1] // 3; images = []
    for R, p in ops:
        pinv = np.argsort(np.array(p)); rimg = np.array([key[canon(t, tuple(int(pinv[x]) for x in i))] for t, i in ic]); signs = np.zeros(len(ic), int)
        for r in range(len(ic)):
            Br = B[r].reshape(nat, 3); W = np.array([R.T @ Br[p[k]] for k in range(nat)]).reshape(-1); Bi = B[rimg[r]]
            c = W @ Bi / (np.linalg.norm(W) * np.linalg.norm(Bi)); assert abs(abs(c) - 1) < 1e-6, (r, c)
            signs[r] = 1 if c > 0 else -1
        images.append((rimg, signs))
    return images


def canon(typ, idx):
    if typ in ("CC", "CH"): return (typ, tuple(sorted(idx)))
    if typ in ("CCC", "CCH"): return (typ, (min(idx[0], idx[2]), idx[1], max(idx[0], idx[2])))
    if typ == "wag": return (typ, (idx[0], idx[1], min(idx[2], idx[3]), max(idx[2], idx[3])))
    if typ == "tors": return (typ, min(tuple(idx), tuple(reversed(idx))))


def orbits(ic, images):
    """Orbits of coordinate PAIRS under the operations, each member carrying the sign of its force constant relative to the
    representative; an orbit whose member is reached with both signs is symmetry-forbidden (its constant must vanish) and is dropped."""
    n = len(ic); seen = {}; orbit_list = []; forbidden = 0
    for a in range(n):
        for b in range(a, n):
            if (a, b) in seen: continue
            members = {(a, b): 1}; frontier = [(a, b, 1)]; bad = False
            while frontier:
                x, y, sgn = frontier.pop()
                for rimg, sg in images:
                    u, v, s2 = int(rimg[x]), int(rimg[y]), int(sg[x] * sg[y]) * sgn; m = (min(u, v), max(u, v))
                    if m in members:
                        if members[m] != s2: bad = True
                    else:
                        members[m] = s2; frontier.append((u, v, s2))
            for m in members: seen[m] = True
            if bad: forbidden += 1
            else: orbit_list.append(sorted(members.items()))
    return orbit_list, forbidden


def graph_distance(ic, bonds, natom):
    adj = {i: set() for i in range(natom)}
    for i, j in bonds: adj[i].add(j); adj[j].add(i)
    dist = np.full((natom, natom), 99)
    for s in range(natom):
        dist[s, s] = 0; frontier = [s]
        while frontier:
            nxt = []
            for u in frontier:
                for v in adj[u]:
                    if dist[s, v] > dist[s, u] + 1: dist[s, v] = dist[s, u] + 1; nxt.append(v)
            frontier = nxt
    def sep(a, b):  # smallest atom-graph distance between the atom sets of two internals (0 = share an atom)
        return int(min(dist[x, y] for x in ic[a][1] for y in ic[b][1]))
    return sep


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--molecule", default="benzene"); args = ap.parse_args()
    d = load(args.molecule); X = d["coords"]; sym = d["symbols"]; L = d["L"]; Minv = d["Minv"]; omega = d["omega"]; freq = d["freq"]; M = len(omega)
    ic, bonds = internal_set(X, sym); B = b_matrix(ic, X); ops = operations_of(X, sym); images = coordinate_images(ic, B, ops)
    orb, n_forbidden = orbits(ic, images); sep = graph_distance(ic, bonds, len(sym))
    types = [t for t, _ in ic]
    # effect of a unit ΔF on orbit o, in the mode basis
    T = B * Minv[None, :] @ L  # (n_ic × M): rows = ∂q/∂Q (mass-weighted mode coordinates)
    def design(orbit_ids):
        cols = []
        for o in orbit_ids:
            F = np.zeros((len(ic), len(ic)))
            for (a, b), sg in orb[o]: F[a, b] = sg; F[b, a] = sg
            cols.append((T.T @ F @ T).reshape(-1))
        return np.array(cols).T
    D2_check = L.T @ ((d["H_high"] - d["H_low"]) * np.outer(Minv, Minv)) @ L
    rel = np.linalg.norm(D2_check - d["D2Q"]) / np.linalg.norm(d["D2Q"]); assert rel < 1e-6, f"stageA D2_direct_Q is not L^T M^-1/2 (H_high-H_low) M^-1/2 L (rel {rel:.2e})"
    target = d["D2Q"].reshape(-1)  # Δ₂ in the mode basis (BHHLYP − B3LYP), E_h/(bohr² m_e); consistency with the Cartesian Hessians asserted above
    def orbit_kind(o):
        (a, b), _ = orb[o][0]; return "diag" if a == b else f"sep{sep(a, b)}"
    def cls(t): return "σ" if t in CONSTANTS["sigma_types"] else "π"
    def orbit_class(o):
        (a, b), _ = orb[o][0]; ca, cb = cls(types[a]), cls(types[b]); return ca if ca == cb else "σπ"
    sets = {"S0 diagonal": [o for o in range(len(orb)) if orbit_kind(o) == "diag"],
            "S1 +shared-atom couplings": [o for o in range(len(orb)) if orbit_kind(o) in ("diag", "sep0")],
            "S2 +one-bond-apart": [o for o in range(len(orb)) if orbit_kind(o) in ("diag", "sep0", "sep1")],
            "S3 all orbits": list(range(len(orb))),
            "σ-only (all σ orbits)": [o for o in range(len(orb)) if orbit_class(o) == "σ"],
            "π-only (all π orbits)": [o for o in range(len(orb)) if orbit_class(o) == "π"],
            "σ + π without σπ couplings": [o for o in range(len(orb)) if orbit_class(o) != "σπ"]}
    meas_first = np.diag(d["D2Q"]) / (2 * omega) * HARTREE_TO_CM
    w_high = np.sqrt(np.linalg.eigvalsh(np.diag(omega ** 2) + d["D2Q"])) * HARTREE_TO_CM
    kek = int(np.argmin(meas_first))  # the most negative first-order correction (benzene: the B2u Kekulé mode)
    rows = []
    for name, ids in sets.items():
        A = design(ids); x, *_ = np.linalg.lstsq(A, target, rcond=None); fit = (A @ x).reshape(M, M)
        res_first = np.diag(fit) / (2 * omega) * HARTREE_TO_CM - meas_first
        w_fit = np.sqrt(np.abs(np.linalg.eigvalsh(np.diag(omega ** 2) + fit))) * HARTREE_TO_CM
        fro = np.linalg.norm(fit - d["D2Q"]) / np.linalg.norm(d["D2Q"])
        rows.append({"set": name, "n_params": len(ids), "rms_first_order_cm": float(np.sqrt(np.mean(res_first ** 2))), "max_first_order_cm": float(np.abs(res_first).max()),
                     "rms_rediag_cm": float(np.sqrt(np.mean((w_fit - w_high) ** 2))), "kekule_residual_cm": float(res_first[kek]), "rel_frobenius_residual": float(fro),
                     "per_family_rms_cm": {f: float(np.sqrt(np.mean(res_first[[k for k in range(M) if d["fam"][k] == f]] ** 2))) for f in sorted(set(d["fam"]))}})
    out = {"date": f"{datetime.now():%Y-%m-%d %H:%M}", "molecule": args.molecule, "constants": CONSTANTS, "n_internal": len(ic), "internal_types": {t: types.count(t) for t in sorted(set(types))},
           "n_symmetry_ops": len(ops), "n_orbits_allowed": len(orb), "n_orbits_forbidden_by_symmetry": n_forbidden, "orbits_by_kind": {k: sum(1 for o in range(len(orb)) if orbit_kind(o) == k) for k in sorted(set(orbit_kind(o) for o in range(len(orb))))},
           "orbits_by_class": {k: sum(1 for o in range(len(orb)) if orbit_class(o) == k) for k in ("σ", "π", "σπ")},
           "kekule_mode": {"index": kek, "nu_cm": float(freq[kek]), "first_order_correction_cm": float(meas_first[kek]), "family": d["fam"][kek]},
           "measured_first_order_rms_cm": float(np.sqrt(np.mean(meas_first ** 2))), "fits": rows}
    json.dump(out, open(HERE / f"x17_{args.molecule}.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    Lm = [f"# X17 — internal-coordinate orbit fits of the stand-in correction, {args.molecule} ({out['date']})", "",
          f"Internal set: {out['internal_types']} ({len(ic)} coordinates, redundant); {len(ops)} symmetry operations found from the geometry; {len(orb)} symmetry-allowed pair orbits ({n_forbidden} orbits forbidden by symmetry dropped; {out['orbits_by_kind']}; by class {out['orbits_by_class']}). "
          f"Measured stand-in: first-order RMS over the {M} modes {out['measured_first_order_rms_cm']:.2f} cm⁻¹; the largest correction is mode {kek} ({freq[kek]:.0f} cm⁻¹, {d['fam'][kek]}): {meas_first[kek]:+.1f} cm⁻¹.", "",
          "| parameter set | params | RMS first-order error (cm⁻¹) | max | RMS after re-diagonalisation | Kekulé-mode residual | rel. Frobenius residual | per family |", "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        Lm.append(f"| {r['set']} | {r['n_params']} | **{r['rms_first_order_cm']:.2f}** | {r['max_first_order_cm']:.2f} | {r['rms_rediag_cm']:.2f} | {r['kekule_residual_cm']:+.2f} | {r['rel_frobenius_residual']:.3f} | " + ", ".join(f"{k} {v:.2f}" for k, v in r["per_family_rms_cm"].items()) + " |")
    th = CONSTANTS["thresholds_cm"]; s1 = rows[1]
    Lm += ["", f"Reading (fixed in the header): compact if S1 ≤ {th[0]} cm⁻¹ (band threshold) or at least ≤ {th[1]} (u_band). S1 = {s1['rms_first_order_cm']:.2f} cm⁻¹ → **{'compact at 0.5' if s1['rms_first_order_cm'] <= th[0] else ('compact only at 2.5' if s1['rms_first_order_cm'] <= th[1] else 'NOT compact')}**. "
           "Parameters are not reported (redundant set; only residuals are unique). Stand-in tensor; R0's CC tensor replaces it."]
    (HERE / f"x17_{args.molecule}.md").write_text("\n".join(Lm), encoding="utf-8"); print("\n".join(Lm).encode("ascii", "replace").decode())


if __name__ == "__main__":
    main()
