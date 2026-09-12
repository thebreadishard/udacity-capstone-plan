"""X13 (2026-09-12, evening) — the naphthalene DFT mode table from plan 02's stored B3LYP/6-31G* Hessian: frequencies, D2h irreps,
families, the eligible (same-irrep) pair count for plan 05's symmetry prior at R1, and the DFT-only ranking of X10 applied to it.

Why now: plan 02's `results_dft_locality/naphthalene.npz` (git 57a7910) is a B3LYP/6-31G* Hessian at the geometry plan 05's dry run will
use (identical within 5e-4 bohr, checked 2026-09-12). Everything on the DFT side of X10 — modes, irreps, resonance denominators, the
eligible pair set — can therefore be tabulated tonight; only the correction tensor (the BHHLYP half) is missing, and with it the
'pairs needed for 0.5 cm⁻¹'. What this script fixes in advance, so that the naphthalene repeat of X10 (draft P25's licence test) reads
a table it did not choose: (i) the 48 modes with frequency, irrep and family (the dry run's family rule, `assign_families`, reproduced
unchanged); (ii) the number of same-irrep pairs among the 1,128 off-diagonal pairs — the size of the symmetry prior's off-diagonal deck
at R1; (iii) the DFT-only ranking 1/|ω_i² − ω_j²| over those pairs and what fraction of them lies within a factor 10 / 100 of the top
denominator, per irrep; (iv) the same numbers for benzene from the same file family, as a check against the dry run's own table.

Irreps: D2h has eight one-dimensional irreps; a mode's character under each of the eight operations (E, C2z, C2y, C2x, i, σxy, σxz, σyz)
is ⟨v|R v⟩ = ±1, with R acting on the mass-weighted displacement (rotation of every atom's vector and permutation of the atoms). The
molecule is put in its inertial frame first; the operations are the three coordinate-axis C2's and the three coordinate-plane mirrors.
A character vector that is not ±1 within 1e-3 is flagged. Every number from the file; constants in CONSTANTS."""
import itertools
import json
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
HARTREE_TO_CM = 219474.63
AMU_TO_ME = 1822.888486209
DEGENERATE_CM = 2.0
CONSTANTS = {"degenerate_cm": DEGENERATE_CM, "git_commit": "57a7910", "files": {"naphthalene": "plans/02_coupled-cluster-anharmonic-ir/probes/results_dft_locality/naphthalene.npz",
                                                 "benzene": "plans/02_coupled-cluster-anharmonic-ir/probes/results_dft_locality/benzene.npz"},
             "n_zero_modes": 6, "character_tolerance": 1e-3, "denominator_bands": [10, 100]}
D2H = {"Ag": [1, 1, 1, 1, 1, 1, 1, 1], "B1g": [1, 1, -1, -1, 1, 1, -1, -1], "B2g": [1, -1, 1, -1, 1, -1, 1, -1], "B3g": [1, -1, -1, 1, 1, -1, -1, 1],
       "Au": [1, 1, 1, 1, -1, -1, -1, -1], "B1u": [1, 1, -1, -1, -1, -1, 1, 1], "B2u": [1, -1, 1, -1, -1, 1, -1, 1], "B3u": [1, -1, -1, 1, -1, 1, 1, -1]}
OPS = {"E": np.diag([1, 1, 1]), "C2z": np.diag([-1, -1, 1]), "C2y": np.diag([-1, 1, -1]), "C2x": np.diag([1, -1, -1]),
       "i": np.diag([-1, -1, -1]), "sxy": np.diag([1, 1, -1]), "sxz": np.diag([1, -1, 1]), "syz": np.diag([-1, 1, 1])}


def load_from_git(relpath, tmpdir):
    out = Path(tmpdir) / Path(relpath).name
    with open(out, "wb") as f:
        subprocess.run(["git", "-C", str(REPO), "show", f"{CONSTANTS['git_commit']}:{relpath}"], check=True, stdout=f)
    with np.load(out) as z:
        return {k: z[k] for k in z.files}


def inertial_frame(X, m):
    c = (X * m[:, None]).sum(0) / m.sum(); Y = X - c
    I = np.zeros((3, 3))
    for y, mm in zip(Y, m):
        I += mm * (np.dot(y, y) * np.eye(3) - np.outer(y, y))
    w, V = np.linalg.eigh(I)
    order = np.argsort(w); R = V[:, order]; wv = w[order]         # ascending moments: x = long axis, z = largest moment = the plane normal
    if np.linalg.det(R) < 0:
        R[:, 2] *= -1
    Yf = Y @ R
    if abs(wv[0] - wv[1]) / wv[1] < 1e-3:                            # symmetric top in the plane (benzene): put the first heavy atom on +x
        a0 = int(np.argmax(m)); th = np.arctan2(Yf[a0, 1], Yf[a0, 0])
        Rz = np.array([[np.cos(th), np.sin(th), 0], [-np.sin(th), np.cos(th), 0], [0, 0, 1]])
        Yf = Yf @ Rz.T; R = R @ Rz.T
    return Yf, R


def assign_families(freq_cm, L, symbols, Minv):
    """The dry run's rule (dryrun_dft_delta_recovery.py), unchanged: molecule in the xy plane, z = out of plane."""
    fams = []; nat = len(symbols); h = np.array([s == "H" for s in symbols])
    for k in range(L.shape[1]):
        disp = (L[:, k] * Minv).reshape(nat, 3)
        h_share = np.sum(disp[h] ** 2) / max(np.sum(disp ** 2), 1e-30); oop = np.sum(disp[:, 2] ** 2) / max(np.sum(disp ** 2), 1e-30); f = freq_cm[k]
        if f > 2800: fams.append("CH-stretch")
        elif oop > 0.5: fams.append("CH-oop" if h_share > 0.5 else "ring-oop")
        elif 1300 <= f <= 1700: fams.append("CC-stretch")
        elif 1000 <= f < 1300: fams.append("CH-ip-bend")
        else: fams.append("ring-ip")
    return fams


def analyse(name, z):
    H, X, m = z["hessian_au"], z["coords_bohr"], z["masses_amu"]
    sym = ["C" if x > 6 else "H" for x in m]; nat = len(sym)
    Y, Rf = inertial_frame(X, m)
    Hf = np.kron(np.eye(nat), Rf).T @ H @ np.kron(np.eye(nat), Rf)     # Hessian in the inertial frame
    Minv = 1.0 / np.sqrt(np.repeat(m, 3) * AMU_TO_ME)
    F = Minv[:, None] * Hf * Minv[None, :]
    lam, V = np.linalg.eigh(F)
    keep = np.argsort(np.abs(lam))[CONSTANTS["n_zero_modes"]:]; keep = keep[np.argsort(lam[keep])]
    L = V[:, keep]; omega = np.sqrt(np.abs(lam[keep])); freq = np.sign(lam[keep]) * omega * HARTREE_TO_CM
    # atom permutation under each operation
    perms = {}
    for op, Rm in OPS.items():
        Yt = Y @ Rm.T; perm = []
        for a in range(nat):
            d = np.linalg.norm(Y - Yt[a], axis=1); b = int(np.argmin(d))
            if d[b] > 1e-2 or sym[b] != sym[a]:
                raise RuntimeError(f"{name}: operation {op} is not a symmetry (atom {a}, residual {d[b]:.3e})")
            perm.append(b)
        perms[op] = perm
    # symmetry-adapt degenerate pairs (benzene's E modes come out of eigh as arbitrary mixtures): within each group of modes closer
    # than DEGENERATE_CM, diagonalise the representation matrix of C2x so that every column has a definite character
    def rep_matrix(cols, op):
        Rm = OPS[op]; Mx = np.zeros((len(cols), len(cols)))
        for a_, ka in enumerate(cols):
            va = L[:, ka].reshape(nat, 3)
            for b_, kb in enumerate(cols):
                vb = L[:, kb].reshape(nat, 3); Rv = np.zeros_like(vb)
                for at in range(nat):
                    Rv[perms[op][at]] = Rm @ vb[at]
                Mx[a_, b_] = float((va * Rv).sum())
        return Mx
    k = 0
    while k < L.shape[1]:
        grp = [k]
        while grp[-1] + 1 < L.shape[1] and abs(freq[grp[-1] + 1] - freq[k]) < DEGENERATE_CM:
            grp.append(grp[-1] + 1)
        if len(grp) > 1:
            for op in ("C2x", "C2y", "sxz"):
                Mx = rep_matrix(grp, op)
                if np.abs(Mx - np.diag(np.diag(Mx))).max() > 1e-6:
                    _, U = np.linalg.eigh((Mx + Mx.T) / 2); L[:, grp] = L[:, grp] @ U
        k = grp[-1] + 1
    chars = np.zeros((L.shape[1], len(OPS))); irreps = []; flagged = 0
    for k in range(L.shape[1]):
        v = L[:, k].reshape(nat, 3)
        for oi, (op, Rm) in enumerate(OPS.items()):
            Rv = np.zeros_like(v)
            for a in range(nat):
                Rv[perms[op][a]] = Rm @ v[a]
            chars[k, oi] = float((v * Rv).sum())
        cv = np.round(chars[k]).astype(int)
        if np.abs(chars[k] - cv).max() > CONSTANTS["character_tolerance"]:
            flagged += 1
        lab = next((nm for nm, c in D2H.items() if list(cv) == c), "?")
        irreps.append(lab)
    fams = assign_families(freq, L, sym, Minv)
    M = L.shape[1]
    pairs = [(i, j) for i in range(M) for j in range(i + 1, M)]
    eligible = [(i, j) for i, j in pairs if irreps[i] == irreps[j] and irreps[i] != "?"]
    den = np.array([1.0 / abs(omega[i] ** 2 - omega[j] ** 2) for i, j in eligible])
    top = den.max()
    bands = {str(b): int((den >= top / b).sum()) for b in CONSTANTS["denominator_bands"]}
    per_irrep = {}
    for lab in D2H:
        idx = [k for k in range(M) if irreps[k] == lab]
        per_irrep[lab] = {"modes": len(idx), "pairs": len(idx) * (len(idx) - 1) // 2}
    order = np.argsort(-den)
    top10 = [{"pair": eligible[t], "irrep": irreps[eligible[t][0]], "omega_i": round(float(freq[eligible[t][0]]), 1), "omega_j": round(float(freq[eligible[t][1]]), 1),
              "gap_cm": round(float(abs(freq[eligible[t][0]] - freq[eligible[t][1]])), 1), "fam_i": fams[eligible[t][0]], "fam_j": fams[eligible[t][1]]} for t in order[:10]]
    return {"molecule": name, "natom": nat, "M": M, "n_imag": int((freq < 0).sum()), "characters_flagged": flagged,
            "modes": [{"k": k, "freq_cm": round(float(freq[k]), 1), "irrep": irreps[k], "family": fams[k]} for k in range(M)],
            "per_irrep": per_irrep, "n_pairs": len(pairs), "n_eligible_pairs": len(eligible), "eligible_fraction": len(eligible) / len(pairs),
            "denominator_top_uEh": float(top), "pairs_within_factor_of_top": bands, "top10_by_denominator": top10,
            "family_counts": {f: fams.count(f) for f in sorted(set(fams))}}


def main():
    out = {"date": f"{datetime.now():%Y-%m-%d %H:%M}", "constants": CONSTANTS, "results": {}}
    with tempfile.TemporaryDirectory() as tmp:
        for name, rel in CONSTANTS["files"].items():
            out["results"][name] = analyse(name, load_from_git(rel, tmp))
    json.dump(out, open(HERE / "x13_naphthalene_mode_table.json", "w"), indent=1)
    L = [f"# X13 — naphthalene DFT mode table (B3LYP/6-31G*, plan 02 git {CONSTANTS['git_commit']}), D2h irreps, families, eligible pairs ({out['date']})", ""]
    for name, r in out["results"].items():
        L += [f"## {name}: {r['M']} modes, {r['n_imag']} imaginary, {r['characters_flagged']} modes with non-integer characters", "",
              f"Families: {r['family_counts']}. Per irrep (modes, same-irrep pairs): " + ", ".join(f"{k} {v['modes']}/{v['pairs']}" for k, v in r["per_irrep"].items()) + ".", "",
              f"**Eligible (same-irrep) pairs: {r['n_eligible_pairs']} of {r['n_pairs']} ({100*r['eligible_fraction']:.1f} %).** Denominator ranking: pairs within a factor 10 / 100 of the top denominator: "
              f"{r['pairs_within_factor_of_top']['10']} / {r['pairs_within_factor_of_top']['100']}.", "",
              "Top 10 eligible pairs by 1/|ω_i² − ω_j²|:", ""]
        L += [f"- {t['pair']} {t['irrep']}: {t['omega_i']} / {t['omega_j']} cm⁻¹ (gap {t['gap_cm']}), {t['fam_i']} / {t['fam_j']}" for t in r["top10_by_denominator"]]
        L += ["", "| k | ν (cm⁻¹) | irrep | family |", "|---|---|---|---|"] + [f"| {m['k']} | {m['freq_cm']} | {m['irrep']} | {m['family']} |" for m in r["modes"]] + [""]
    L += ["Reading: the eligible-pair count is the off-diagonal size of plan 05's symmetry prior at R1 (2 energies per pair in the deck's two-mode patterns); the naphthalene repeat of X10 "
          "(draft P25's licence test) ranks exactly these pairs. Benzene from the same file family is the cross-check against the dry run's own irreps (D6h collapsed to D2h here: "
          "E-type pairs split into two one-dimensional irreps, so benzene's eligible count in this table is not the dry run's 57).", "", "Constants: " + json.dumps(CONSTANTS)]
    (HERE / "x13_naphthalene_mode_table.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[:40]).encode("ascii", "replace").decode())


if __name__ == "__main__":
    main()
