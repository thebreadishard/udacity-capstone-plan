#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Probe 1 — Zero-CC dry run, both modes (plan 05, probes/README item 1).

Δ between B3LYP and a high-exact-exchange functional (BHHLYP), 6-31G*, at one molecule:
  stage A  geometry, two Hessians (timed), modes, families, the DIRECT Δ₂ (the reference);
  stage B  the hashed, ordered deck (single-mode ± block, second-amplitude block, two-mode
           patterns within a DFT frequency band, multi-mode completion patterns), the seeded
           pair-wise hold-out, and the responses in mode E (symmetric combinations R_s over the
           ± pairs, one shared reference energy) and mode G (gradient differences), cached;
  stage C  the recoveries — diagonal-only (CMA-0 block) and full (banded ℓ₁ structural prior)
           — the ρ(n) curves per complete pair, K and K_off at a declared ρ, the w rule, the
           recovered-vs-direct frequency error per family, the reference constant c₀, the
           DFT-arm noise floor from a nine-point scan, and the noise-injection column
           (independent noise per energy, one shared ε₀ per molecule, per component in mode G).

Everything printed is a measurement of THIS run on THIS machine. Nothing here is a local-CC
number: both arms are DFT. Runs in the conda environment `qc` (psi4 1.11) on Windows.

Usage (from the repository root):
  C:\\Users\\thebr\\.conda\\envs\\qc\\python.exe plans/05_delta-probed-ir-pipeline/probes/dryrun_dft_delta_recovery.py \
      --molecule benzene --threads 8 [--quick] [--stage A|B|C|all]

Deviations from the frozen form, printed as such at the end of the report:
  - the low-rank term of the structural prior is not implemented in this first version
    (banded ℓ₁ only);
  - the multi-atom "completion" patterns are random sparse mode combinations, not the
    O1NumHess construction (which needs the O1NumHess code, a pinned debt).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
from datetime import datetime

import numpy as np

try:  # Windows consoles default to cp1252; the report uses subscripts and Greek letters
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:  # noqa: BLE001
    pass

# ----------------------------------------------------------------------------- constants
AMU_TO_ME = 1822.888486209
HARTREE_TO_CM = 219474.6313705
FUNCTIONALS = {"low": "b3lyp", "high": "bhhlyp"}     # the dry-run pair (Distilled §3)
BASIS = "6-31g*"
Q_S = 1.0          # pattern amplitude (dimensionless normal coordinate; Ladder §3 expects 1.0)
Q_2 = 0.5          # second amplitude on every mode (the q₂ block; identifies c₀, gives φ_iii)
F_H = 0.2          # hold-out fraction of pairs
DECK_SEED = 20260905
HOLDOUT_SEED = 20260905 + 1
BAND_W_CANDIDATES = [25.0, 50.0, 100.0, 200.0, 400.0]   # cm⁻¹, for the w rule
TAU7_CM = 5.0      # Q7-class tolerance used only to read off w in the dry run (pilot-note item 11 later)
RHO_DECLARED = 0.10  # the "declared ρ" at which the dry-run K is read (README item 1); c comes later
RHO_MAX = 0.5
SIGMA_GRID_UEH = [0.5, 1.0, 2.0, 5.0, 10.0, 20.0]        # µE_h per energy, the noise-injection grid
C_GRID = [1.0, 1.5, 2.0, 3.0]
SMOOTH_MODES_FAMILIES = ["CC-stretch", "CH-stretch", "CH-oop", "totally-symmetric"]

GEOMETRIES = {
    # Cartesian starting guesses (Å); psi4 optimises at B3LYP/6-31G* first.
    "benzene": """0 1
C  1.3970  0.0000  0.0000
C  0.6985  1.2098  0.0000
C -0.6985  1.2098  0.0000
C -1.3970  0.0000  0.0000
C -0.6985 -1.2098  0.0000
C  0.6985 -1.2098  0.0000
H  2.4810  0.0000  0.0000
H  1.2405  2.1486  0.0000
H -1.2405  2.1486  0.0000
H -2.4810  0.0000  0.0000
H -1.2405 -2.1486  0.0000
H  1.2405 -2.1486  0.0000
no_com
no_reorient
symmetry c1
""",
}


def log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


# ----------------------------------------------------------------------------- psi4 helpers
def psi4_setup(threads: int, outfile: str):
    import psi4  # noqa: WPS433
    psi4.core.set_output_file(outfile, False)
    psi4.set_memory("8 GB")
    psi4.set_num_threads(threads)
    psi4.set_options({"scf_type": "df", "d_convergence": 1e-8, "e_convergence": 1e-10,
                      "dft_spherical_points": 590, "dft_radial_points": 99})
    return psi4


def make_molecule(psi4, symbols, coords_bohr):
    lines = ["0 1"]
    for s, (x, y, z) in zip(symbols, coords_bohr):
        lines.append(f"{s} {x:.12f} {y:.12f} {z:.12f}")
    lines += ["units bohr", "no_com", "no_reorient", "symmetry c1"]
    return psi4.geometry("\n".join(lines))


def dft_energy_gradient(psi4, mol, functional: str):
    """Energy (E_h) and Cartesian gradient (E_h/bohr, shape 3N) at the molecule's geometry."""
    g, wfn = psi4.gradient(f"{functional}/{BASIS}", molecule=mol, return_wfn=True)
    return float(wfn.energy()), np.asarray(g).reshape(-1)


# ----------------------------------------------------------------------------- stage A
def stage_a(psi4, name: str, out: str, threads: int) -> dict:
    """Geometry, two Hessians (timed), modes, families, direct Δ₂."""
    log("stage A: geometry optimisation at B3LYP/6-31G*")
    mol = psi4.geometry(GEOMETRIES[name])
    t0 = time.time()
    psi4.optimize(f"{FUNCTIONALS['low']}/{BASIS}", molecule=mol)
    t_opt = time.time() - t0
    symbols = [mol.symbol(i) for i in range(mol.natom())]
    coords = np.array([[mol.x(i), mol.y(i), mol.z(i)] for i in range(mol.natom())])  # bohr
    masses_amu = np.array([mol.mass(i) for i in range(mol.natom())])
    natom = len(symbols)

    hess = {}
    timing = {"optimize_s": t_opt}
    for arm, fn in FUNCTIONALS.items():
        log(f"stage A: Hessian {fn}/{BASIS}")
        m = make_molecule(psi4, symbols, coords)
        t0 = time.time()
        H = psi4.hessian(f"{fn}/{BASIS}", molecule=m)
        timing[f"hessian_{fn}_s"] = time.time() - t0
        hess[arm] = np.asarray(H)
        log(f"stage A: Hessian {fn} took {timing[f'hessian_{fn}_s']:.1f} s")

    # mass-weighted Hessian of the low arm → modes
    m_me = np.repeat(masses_amu * AMU_TO_ME, 3)
    Minv = 1.0 / np.sqrt(m_me)
    F_low = hess["low"] * np.outer(Minv, Minv)
    F_high = hess["high"] * np.outer(Minv, Minv)
    lam, L = np.linalg.eigh(F_low)
    # drop the six translations/rotations: smallest |λ|
    order = np.argsort(np.abs(lam))
    keep = np.sort(order[6:])
    lam_v, L_v = lam[keep], L[:, keep]
    omega_au = np.sqrt(np.abs(lam_v))            # E_h (ħ = 1)
    freq_cm = omega_au * HARTREE_TO_CM
    srt = np.argsort(freq_cm)
    omega_au, freq_cm, L_v = omega_au[srt], freq_cm[srt], L_v[:, srt]
    M = len(freq_cm)

    # direct Δ₂ in the low arm's mode basis, in mass-weighted normal coordinates (E_h/(bohr²·m_e))
    D2_direct_Q = L_v.T @ (F_high - F_low) @ L_v
    # convert to dimensionless normal coordinates: Q_i = q_i/√ω_i  →  Δ₂^q_ij = Δ₂^Q_ij/√(ω_i ω_j)
    s = 1.0 / np.sqrt(omega_au)
    D2_direct = D2_direct_Q * np.outer(s, s)    # E_h per (dimensionless q)²
    # first-order frequency shift per mode: δω_i ≈ Δ₂^Q_ii/(2ω_i)
    dfreq_first_order_cm = (np.diag(D2_direct_Q) / (2.0 * omega_au)) * HARTREE_TO_CM
    # exact high-arm frequencies for the same geometry (the "direct" spectrum)
    lam_h = np.linalg.eigvalsh(F_high)
    lam_h = np.sort(lam_h[np.argsort(np.abs(lam_h))[6:]])
    freq_high_cm = np.sqrt(np.abs(lam_h)) * HARTREE_TO_CM

    families = assign_families(freq_cm, L_v, symbols, Minv, coords)
    # a totally symmetric mode: the one with the largest in-plane radial ("breathing") character
    ts_index = pick_totally_symmetric(L_v, Minv, coords, symbols, freq_cm)

    res = {
        "molecule": name, "symbols": symbols, "coords_bohr": coords.tolist(),
        "masses_amu": masses_amu.tolist(), "natom": natom, "M": M,
        "functionals": FUNCTIONALS, "basis": BASIS,
        "timing": timing, "freq_low_cm": freq_cm.tolist(), "freq_high_direct_cm": freq_high_cm.tolist(),
        "dfreq_first_order_cm": dfreq_first_order_cm.tolist(),
        "families": families, "totally_symmetric_index": int(ts_index),
        "machine": platform.node(), "threads": threads, "psi4": psi4.__version__,
    }
    np.savez(os.path.join(out, "stageA_hessians.npz"),
             H_low=hess["low"], H_high=hess["high"], L=L_v, omega_au=omega_au,
             D2_direct=D2_direct, D2_direct_Q=D2_direct_Q, Minv=Minv, coords=coords)
    json.dump(res, open(os.path.join(out, "stageA.json"), "w"), indent=1)
    log(f"stage A done: M={M}, Hessian times {timing}")
    return res


def assign_families(freq_cm, L, symbols, Minv, coords):
    """Family label per mode: CH-stretch / CC-stretch / CH-ip-bend / CH-oop / ring, by frequency
    window and by the out-of-plane share of the hydrogen motion (benzene lies in the xy plane)."""
    fams = []
    nat = len(symbols)
    for k in range(nat and L.shape[1]):
        disp = (L[:, k] * Minv).reshape(nat, 3)
        h = np.array([s == "H" for s in symbols])
        h_share = np.sum(disp[h] ** 2) / max(np.sum(disp ** 2), 1e-30)
        oop_share = np.sum(disp[:, 2] ** 2) / max(np.sum(disp ** 2), 1e-30)
        f = freq_cm[k]
        if f > 2800:
            fams.append("CH-stretch")
        elif oop_share > 0.5:
            fams.append("CH-oop" if h_share > 0.5 else "ring-oop")
        elif 1300 <= f <= 1700:
            fams.append("CC-stretch")
        elif 1000 <= f < 1300:
            fams.append("CH-ip-bend")
        else:
            fams.append("ring-ip")
    return fams


def pick_totally_symmetric(L, Minv, coords, symbols, freq_cm):
    """Mode with the largest radial (breathing) projection: Σ (r̂·d) over atoms, normalised."""
    nat = len(symbols)
    best, best_k = -1.0, 0
    for k in range(L.shape[1]):
        disp = (L[:, k] * Minv).reshape(nat, 3)
        r = coords - coords.mean(axis=0)
        rn = r / np.maximum(np.linalg.norm(r, axis=1, keepdims=True), 1e-12)
        radial = np.sum(np.sum(disp * rn, axis=1)) / max(np.sqrt(np.sum(disp ** 2)) * np.sqrt(nat), 1e-30)
        if abs(radial) > best and 700 < freq_cm[k] < 1100:
            best, best_k = abs(radial), k
    return best_k


# ----------------------------------------------------------------------------- stage B
def build_deck(a: dict, quick: bool) -> dict:
    """The hashed, ordered pattern set in dimensionless normal coordinates."""
    M = a["M"]
    freq = np.array(a["freq_low_cm"])
    rng = np.random.default_rng(DECK_SEED)
    patterns = []   # each: {"kind", "a": list(M), "amp"}
    # block 1: single-mode ±q_s (2M energies; the CMA-0 block; consumed first)
    for i in range(M):
        v = np.zeros(M); v[i] = Q_S
        patterns.append({"kind": "single", "a": v.tolist(), "amp": Q_S, "modes": [i]})
    # block q₂: second amplitude on every mode (outside K; identifies c₀ and φ_iii)
    for i in range(M):
        v = np.zeros(M); v[i] = Q_2
        patterns.append({"kind": "q2", "a": v.tolist(), "amp": Q_2, "modes": [i]})
    # two-mode patterns for pairs within the widest candidate band (DFT frequencies only —
    # no knowledge of the answer enters the deck)
    w_deck = 200.0 if not quick else 60.0
    pairs = [(i, j) for i in range(M) for j in range(i + 1, M) if abs(freq[i] - freq[j]) <= w_deck]
    for (i, j) in pairs:
        for sgn in (+1.0, -1.0):
            v = np.zeros(M); v[i] = Q_S / np.sqrt(2); v[j] = sgn * Q_S / np.sqrt(2)
            patterns.append({"kind": "two-mode", "a": v.tolist(), "amp": Q_S, "modes": [i, j]})
    # multi-mode completion patterns: random sparse combinations (k modes, random signs)
    n_multi = (4 * M) if not quick else 12
    for _ in range(n_multi):
        k = int(rng.integers(3, 7))
        idx = rng.choice(M, size=k, replace=False)
        v = np.zeros(M); v[idx] = rng.choice([-1.0, 1.0], size=k)
        v *= Q_S / np.linalg.norm(v)
        patterns.append({"kind": "multi", "a": v.tolist(), "amp": Q_S, "modes": sorted(int(t) for t in idx)})
    # hashed order: the single block first (in a seeded shuffle among themselves), then the
    # off-diagonal patterns in a seeded shuffle; the q₂ block is evaluated but sits outside K
    singles = [p for p in patterns if p["kind"] == "single"]
    q2s = [p for p in patterns if p["kind"] == "q2"]
    offs = [p for p in patterns if p["kind"] in ("two-mode", "multi")]
    rng2 = np.random.default_rng(DECK_SEED + 7)
    rng2.shuffle(singles); rng2.shuffle(offs)
    ordered = singles + offs
    for n, p in enumerate(ordered):
        p["index"] = n
    for n, p in enumerate(q2s):
        p["index"] = 10_000 + n
    # hold-out per pair (one deck index per ± pair): only off-diagonal pairs are held out
    rng3 = np.random.default_rng(HOLDOUT_SEED)
    n_off = len(offs)
    n_hold = max(1, int(round(F_H * n_off)))
    hold_idx = set(int(t) for t in rng3.choice([p["index"] for p in offs], size=n_hold, replace=False))
    for p in ordered:
        p["holdout"] = p["index"] in hold_idx
    for p in q2s:
        p["holdout"] = False
    deck = {"molecule": a["molecule"], "M": M, "q_s": Q_S, "q_2": Q_2, "f_h": F_H,
            "deck_seed": DECK_SEED, "holdout_seed": HOLDOUT_SEED, "w_deck_cm": w_deck,
            "patterns": ordered + q2s}
    blob = json.dumps(deck, sort_keys=True).encode()
    deck["deck_hash"] = hashlib.sha256(blob).hexdigest()
    return deck


def pattern_to_cartesian(a_vec, L, omega_au, Minv):
    """Dimensionless mode amplitudes a → Cartesian displacement (bohr)."""
    Q = np.asarray(a_vec) / np.sqrt(omega_au)      # mass-weighted normal coordinates
    return (L @ Q) * Minv


def stage_b(psi4, a: dict, deck: dict, out: str) -> None:
    """Responses: energies and gradients at every ±pattern geometry, both arms, cached."""
    z = np.load(os.path.join(out, "stageA_hessians.npz"))
    L, omega, Minv, coords0 = z["L"], z["omega_au"], z["Minv"], z["coords"]
    symbols = a["symbols"]
    cache_path = os.path.join(out, "stageB_responses.json")
    cache = json.load(open(cache_path)) if os.path.exists(cache_path) else {}
    # reference energies/gradients (shared per molecule)
    if "ref" not in cache:
        rec = {}
        for arm, fn in FUNCTIONALS.items():
            m = make_molecule(psi4, symbols, coords0)
            e, g = dft_energy_gradient(psi4, m, fn)
            rec[arm] = {"E": e, "g": g.tolist()}
        cache["ref"] = rec
        json.dump(cache, open(cache_path, "w"))
    total = len(deck["patterns"])
    t_start = time.time()
    n_done = 0
    for p in deck["patterns"]:
        key = str(p["index"])
        if key in cache:
            continue
        rec = {}
        for sign in ("+", "-"):
            x = coords0 + (1.0 if sign == "+" else -1.0) * pattern_to_cartesian(p["a"], L, omega, Minv).reshape(-1, 3)
            rec[sign] = {}
            for arm, fn in FUNCTIONALS.items():
                m = make_molecule(psi4, symbols, x)
                t0 = time.time()
                e, g = dft_energy_gradient(psi4, m, fn)
                rec[sign][arm] = {"E": e, "g": g.tolist(), "wall_s": time.time() - t0}
        cache[key] = rec
        n_done += 1
        if n_done % 5 == 0:
            json.dump(cache, open(cache_path, "w"))
            el = time.time() - t_start
            done_total = sum(1 for q in deck["patterns"] if str(q["index"]) in cache)
            log(f"stage B: {done_total}/{total} pairs, {el/60:.1f} min elapsed, "
                f"{el/max(n_done,1):.1f} s per pair (4 gradient calls)")
    json.dump(cache, open(cache_path, "w"))
    log("stage B done")


# ----------------------------------------------------------------------------- stage C: recovery
def sym_index(M):
    """Map (i,j) i<=j → flat index; returns list of pairs and a (M,M) index matrix."""
    pairs = [(i, j) for i in range(M) for j in range(i, M)]
    idx = -np.ones((M, M), dtype=int)
    for n, (i, j) in enumerate(pairs):
        idx[i, j] = idx[j, i] = n
    return pairs, idx


def design_row_E(a_vec, pairs):
    """R_s(a) = ½ aᵀ Δ a = Σ_i ½ a_i² Δ_ii + Σ_{i<j} a_i a_j Δ_ij."""
    a = np.asarray(a_vec)
    return np.array([0.5 * a[i] * a[i] if i == j else a[i] * a[j] for (i, j) in pairs])


def design_rows_G(a_vec, pairs, M):
    """Mode-G response vector: ½[Δg(+a) − Δg(−a)] = Δ a  (M rows)."""
    a = np.asarray(a_vec)
    rows = np.zeros((M, len(pairs)))
    for n, (i, j) in enumerate(pairs):
        if i == j:
            rows[i, n] += a[i]
        else:
            rows[i, n] += a[j]
            rows[j, n] += a[i]
    return rows


def fista_lasso(A, b, weights, n_iter=3000, tol=1e-10):
    """min ½‖A d − b‖² + Σ_n weights_n |d_n|  (weights = 0 on unpenalised entries)."""
    d = np.zeros(A.shape[1]); y = d.copy(); t = 1.0
    Lc = np.linalg.norm(A, 2) ** 2 + 1e-12
    step = 1.0 / Lc
    for _ in range(n_iter):
        grad = A.T @ (A @ y - b)
        z = y - step * grad
        d_new = np.sign(z) * np.maximum(np.abs(z) - step * weights, 0.0)
        t_new = 0.5 * (1 + np.sqrt(1 + 4 * t * t))
        y = d_new + ((t - 1) / t_new) * (d_new - d)
        if np.linalg.norm(d_new - d) < tol * (1 + np.linalg.norm(d)):
            d = d_new; break
        d, t = d_new, t_new
    return d


def band_weights(pairs, freq, w_cm, lam):
    """ℓ₁ weight per unknown: 0 on the diagonal and inside the band, lam outside."""
    return np.array([0.0 if (i == j or abs(freq[i] - freq[j]) <= w_cm) else lam for (i, j) in pairs])


def unpack(d, pairs, M):
    D = np.zeros((M, M))
    for n, (i, j) in enumerate(pairs):
        D[i, j] = D[j, i] = d[n]
    return D


def family_rms_freq_error(D2_rec_q, D2_direct_q, omega, families, L=None):
    """Per-family RMS of the first-order frequency difference (recovered − direct), cm⁻¹,
    plus the full-matrix version: re-diagonalise ω²+Δ in the mode basis for both."""
    M = len(omega)
    # convert dimensionless-q matrices back to mass-weighted-Q units: Δ^Q = Δ^q * √(ω_i ω_j)
    s = np.sqrt(omega)
    DQ_rec = D2_rec_q * np.outer(s, s)
    DQ_dir = D2_direct_q * np.outer(s, s)
    W2 = np.diag(omega ** 2)
    f_rec = np.sqrt(np.abs(np.linalg.eigvalsh(W2 + DQ_rec))) * HARTREE_TO_CM
    f_dir = np.sqrt(np.abs(np.linalg.eigvalsh(W2 + DQ_dir))) * HARTREE_TO_CM
    f_rec.sort(); f_dir.sort()
    diff_full = f_rec - f_dir
    diff_diag = (np.diag(DQ_rec) - np.diag(DQ_dir)) / (2 * omega) * HARTREE_TO_CM
    outp = {}
    for fam in sorted(set(families)):
        idx = [k for k, f in enumerate(families) if f == fam]
        outp[fam] = {"rms_first_order_cm": float(np.sqrt(np.mean(diff_diag[idx] ** 2))),
                     "rms_full_rediag_cm": float(np.sqrt(np.mean(diff_full[idx] ** 2))),
                     "n_modes": len(idx)}
    return outp


def rho_of(D2, holdout_A, holdout_b):
    pred = holdout_A @ D2
    denom = np.sqrt(np.mean(holdout_b ** 2)) + 1e-30
    return float(np.sqrt(np.mean((pred - holdout_b) ** 2)) / denom)


def stage_c(a: dict, deck: dict, out: str, quick: bool) -> dict:
    z = np.load(os.path.join(out, "stageA_hessians.npz"))
    L, omega, Minv = z["L"], z["omega_au"], z["Minv"]
    D2_direct = z["D2_direct"]
    M = a["M"]; freq = np.array(a["freq_low_cm"]); families = a["families"]
    cache = json.load(open(os.path.join(out, "stageB_responses.json")))
    pairs, _ = sym_index(M)
    ref = cache["ref"]
    dE0 = ref["high"]["E"] - ref["low"]["E"]
    # gradient difference at the reference in mode space (Δ₁): ∂ΔE/∂q_i = (Lᵀ M^{-1/2} Δg)_i / √ω_i
    dg0 = (np.array(ref["high"]["g"]) - np.array(ref["low"]["g"])) * Minv
    delta1_q = (L.T @ dg0) / np.sqrt(omega)

    def resp_E(p, noise=None):
        rec = cache[str(p["index"])]
        e_plus = rec["+"]["high"]["E"] - rec["+"]["low"]["E"]
        e_minus = rec["-"]["high"]["E"] - rec["-"]["low"]["E"]
        e0 = dE0
        if noise is not None:
            e_plus += noise["eps"][str(p["index"])][0]; e_minus += noise["eps"][str(p["index"])][1]; e0 += noise["eps0"]
        Rs = 0.5 * (e_plus + e_minus) - e0
        Ra = 0.5 * (e_plus - e_minus)
        return Rs, Ra

    def resp_G(p, noise_sigma=None, rng=None):
        rec = cache[str(p["index"])]
        gp = (np.array(rec["+"]["high"]["g"]) - np.array(rec["+"]["low"]["g"])) * Minv
        gm = (np.array(rec["-"]["high"]["g"]) - np.array(rec["-"]["low"]["g"])) * Minv
        if noise_sigma is not None:
            gp = gp + rng.normal(0, noise_sigma, size=gp.shape); gm = gm + rng.normal(0, noise_sigma, size=gm.shape)
        qp = (L.T @ gp) / np.sqrt(omega); qm = (L.T @ gm) / np.sqrt(omega)
        return 0.5 * (qp - qm)          # = Δ₂ a in dimensionless units

    singles = [p for p in deck["patterns"] if p["kind"] == "single"]
    q2s = {p["modes"][0]: p for p in deck["patterns"] if p["kind"] == "q2"}
    offs = [p for p in deck["patterns"] if p["kind"] in ("two-mode", "multi")]
    ordered = sorted(singles + offs, key=lambda p: p["index"])

    # ---- c₀ from the two-amplitude read on every mode (Ladder §3)
    c0_list, d_ii_two_amp, phi_iii = [], np.zeros(M), np.zeros(M)
    for p in singles:
        i = p["modes"][0]
        Rs1, Ra1 = resp_E(p); Rs2, Ra2 = resp_E(q2s[i])
        dii = 2 * (Rs2 - Rs1) / (Q_2 ** 2 - Q_S ** 2)
        c0_list.append(Rs1 - 0.5 * dii * Q_S ** 2)
        d_ii_two_amp[i] = dii
        # R_a(q) = Δ₁q + φ q³/6 → φ = 6 (R_a(q_s) − Δ₁ q_s)/q_s³ with Δ₁ from the two amplitudes
        # (two equations: R_a1 = Δ₁ q_s + φ q_s³/6 ; R_a2 = Δ₁ q_2 + φ q_2³/6)
        A = np.array([[Q_S, Q_S ** 3 / 6], [Q_2, Q_2 ** 3 / 6]])
        sol = np.linalg.solve(A, np.array([Ra1, Ra2]))
        phi_iii[i] = sol[1]
    c0 = float(np.mean(c0_list)); c0_sd = float(np.std(c0_list))

    # ---- design matrices (mode E), responses with c₀ subtracted
    A_all = np.array([design_row_E(p["a"], pairs) for p in ordered])
    b_all = np.array([resp_E(p)[0] - c0 for p in ordered])
    hold = np.array([p["holdout"] for p in ordered])
    is_single = np.array([p["kind"] == "single" for p in ordered])
    A_tr, b_tr = A_all[~hold], b_all[~hold]
    A_ho, b_ho = A_all[hold], b_all[hold]
    D2_direct_flat = np.array([D2_direct[i, j] for (i, j) in pairs])

    # ---- diagonal-only recovery (CMA-0): from the single block
    D2_diag = np.zeros((M, M))
    for p in singles:
        i = p["modes"][0]
        Rs, _ = resp_E(p)
        D2_diag[i, i] = 2 * (Rs - c0) / Q_S ** 2
    fam_err_diag = family_rms_freq_error(D2_diag, D2_direct, omega, families)

    # ---- the w rule: smallest band width whose full recovery (all training pairs) reproduces the
    # direct Δ₂ within τ₇ on every family; λ from the hold-out ρ minimum on a small grid
    lam_grid = [1e-7, 1e-6, 1e-5, 1e-4]
    scaleA = np.max(np.abs(A_tr))
    w_rule = None; best = None
    w_table = []
    for w in BAND_W_CANDIDATES:
        best_lam, best_rho, best_D = None, np.inf, None
        for lam in lam_grid:
            wts = band_weights(pairs, freq, w, lam * scaleA)
            d = fista_lasso(A_tr, b_tr, wts)
            r = rho_of(d, A_ho, b_ho)
            if r < best_rho:
                best_lam, best_rho, best_D = lam, r, d
        fam_err = family_rms_freq_error(unpack(best_D, pairs, M), D2_direct, omega, families)
        worst = max(v["rms_full_rediag_cm"] for v in fam_err.values())
        w_table.append({"w_cm": w, "lambda": best_lam, "rho_holdout": best_rho, "worst_family_rms_cm": worst,
                        "family_rms_cm": fam_err})
        if w_rule is None and worst <= TAU7_CM:
            w_rule, best = w, (best_lam, best_D)
    if w_rule is None:   # none passes: take the best worst-family
        k = int(np.argmin([t["worst_family_rms_cm"] for t in w_table]))
        w_rule = w_table[k]["w_cm"]; best = (w_table[k]["lambda"], None)
    lam_rule = best[0]

    # ---- ρ(n) curve, mode E: consume in hashed order, refit after each complete pair (n > 2M)
    def rho_curve(A_all_, b_all_, wts, order_mask_single, n_min_pairs=None):
        curve = []
        idx_train = []
        M2 = int(np.sum(order_mask_single))
        for n, (row, val, h) in enumerate(zip(A_all_, b_all_, hold)):
            if h:
                continue
            idx_train.append(n)
            n_energy = 2 * len(idx_train)
            if n_energy <= 2 * M2:
                continue  # the single block is consumed first; the rule is evaluated for n > 2M
            d = fista_lasso(A_all_[idx_train], b_all_[idx_train], wts, n_iter=1500)
            curve.append((n_energy, rho_of(d, A_ho, b_ho)))
        return curve

    wts_rule = band_weights(pairs, freq, w_rule, lam_rule * scaleA)
    curve_E = rho_curve(A_all, b_all, wts_rule, is_single)
    K_E = next((n for n, r in curve_E if r <= RHO_DECLARED), None)
    d_full = fista_lasso(A_tr, b_tr, wts_rule)
    D2_full = unpack(d_full, pairs, M)
    fam_err_full = family_rms_freq_error(D2_full, D2_direct, omega, families)
    rho_final_E = rho_of(d_full, A_ho, b_ho)
    rms_resp_E = float(np.sqrt(np.mean(b_ho ** 2)))
    # ---- off-diagonal view: subtract the single-block diagonal prediction from every response;
    # ρ_off measures how much of the OFF-diagonal signal the recovery explains (ρ on the raw R_s is
    # dominated by ½ a_i² Δ_ii and is blind to the off-diagonal elements — quick-run finding)
    d_diag_flat = np.array([D2_diag[i, j] if i == j else 0.0 for (i, j) in pairs])
    b_off_all = b_all - A_all @ d_diag_flat
    b_off_ho = b_off_all[hold]
    rms_off_E = float(np.sqrt(np.mean(b_off_ho ** 2)))
    ratio_off = rms_resp_E / (rms_off_E + 1e-30)
    curve_E_off = [(n, r * ratio_off) for n, r in curve_E]
    K_E_off = next((n for n, r in curve_E_off if r <= RHO_DECLARED), None)
    # diagonal-anchored recovery: diagonal fixed from the single block, fit only the off-diagonal
    # unknowns to the off-diagonal residual (the two-mode ± differences isolate Δ_ij exactly)
    off_cols = np.array([i != j for (i, j) in pairs])
    d_anch = np.zeros(len(pairs))
    d_anch[off_cols] = fista_lasso(A_tr[:, off_cols], b_off_all[~hold], wts_rule[off_cols])
    d_anch += d_diag_flat
    fam_err_anch = family_rms_freq_error(unpack(d_anch, pairs, M), D2_direct, omega, families)
    rho_anch_off = rho_of(d_anch, A_ho, b_ho) * ratio_off
    rho_dry_floor = rho_final_E   # the model floor of ρ with noiseless responses (quartic contamination)
    # quartic-corrected variant: per mode, the two amplitudes give Δ_ii and the diagonal quartic
    # Δ₄,iiii (R_s = ½Δ_ii q² + Δ₄ q⁴/24 + c₀, c₀ taken as its estimate); subtract Σ_i Δ₄,iiii a_i⁴/24
    # from every response, then anchor the diagonal and fit the off-diagonals
    d4 = np.zeros(M); d2q = np.zeros(M)
    for p in singles:
        i = p["modes"][0]
        Rs1, _ = resp_E(p); Rs2, _ = resp_E(q2s[i])
        Aq = np.array([[0.5 * Q_S ** 2, Q_S ** 4 / 24], [0.5 * Q_2 ** 2, Q_2 ** 4 / 24]])
        sol = np.linalg.solve(Aq, np.array([Rs1 - c0, Rs2 - c0]))
        d2q[i], d4[i] = sol
    quart = np.array([np.sum(d4 * np.asarray(p["a"]) ** 4) / 24.0 for p in ordered])
    d_diag_q = np.array([d2q[i] if i == j else 0.0 for (i, j) in pairs])
    b_offq_all = b_all - quart - A_all @ d_diag_q
    rms_offq_E = float(np.sqrt(np.mean(b_offq_all[hold] ** 2)))
    d_qc = np.zeros(len(pairs))
    d_qc[off_cols] = fista_lasso(A_tr[:, off_cols], b_offq_all[~hold], wts_rule[off_cols])
    d_qc += d_diag_q
    fam_err_qc = family_rms_freq_error(unpack(d_qc, pairs, M), D2_direct, omega, families)
    rho_qc_off = float(np.sqrt(np.mean((A_ho @ d_qc - (b_ho - quart[hold])) ** 2)) / (rms_offq_E + 1e-30))
    fam_err_diag_q = family_rms_freq_error(np.diag(d2q), D2_direct, omega, families)

    # ---- mode G: gradient responses (M per pattern), same deck, same hold-out
    AG_all = np.vstack([design_rows_G(p["a"], pairs, M) for p in ordered])
    bG_all = np.concatenate([resp_G(p) for p in ordered])
    holdG = np.repeat(hold, M)
    AG_tr, bG_tr, AG_ho, bG_ho = AG_all[~holdG], bG_all[~holdG], AG_all[holdG], bG_all[holdG]
    scaleG = np.max(np.abs(AG_tr))
    wtsG = band_weights(pairs, freq, w_rule, lam_rule * scaleG)
    # ρ(n) in gradients: consume pairs in hashed order from the first pair (no diagonal block in mode G)
    curve_G = []
    idx_tr_pairs = []
    for n, (p, h) in enumerate(zip(ordered, hold)):
        if h:
            continue
        idx_tr_pairs.append(n)
        rows = np.concatenate([np.arange(k * M, (k + 1) * M) for k in idx_tr_pairs])
        if len(idx_tr_pairs) % 2 == 1 and len(idx_tr_pairs) > 6:
            continue   # every second pair to keep the curve affordable
        d = fista_lasso(AG_all[rows], bG_all[rows], wtsG, n_iter=1500)
        curve_G.append((2 * len(idx_tr_pairs), rho_of(d, AG_ho, bG_ho)))
    K_G = next((n for n, r in curve_G if r <= RHO_DECLARED), None)
    dG_full = fista_lasso(AG_tr, bG_tr, wtsG)
    fam_err_G = family_rms_freq_error(unpack(dG_full, pairs, M), D2_direct, omega, families)
    rms_resp_G = float(np.sqrt(np.mean(bG_ho ** 2)))

    # ---- off-diagonal blocks flagged large in the direct Δ₂ (for the real deck's two-mode patterns)
    diag_scale = np.sqrt(np.mean(np.diag(D2_direct) ** 2)) + 1e-30
    flagged = [(int(i), int(j), float(D2_direct[i, j] / diag_scale), float(freq[i]), float(freq[j]))
               for i in range(M) for j in range(i + 1, M) if abs(D2_direct[i, j]) > 0.2 * diag_scale]
    flagged.sort(key=lambda t: -abs(t[2]))

    # ---- noise-injection column (mode E: per energy with shared ε₀; mode G: per component)
    noise_table = []
    rng = np.random.default_rng(424242)
    for s_ueh in ([1.0, 5.0] if quick else SIGMA_GRID_UEH):
        sig = s_ueh * 1e-6
        # the response noise for ρ_noise: σ(R_s) = σ_E/√2 (shared reference; c₀ re-identified)
        rho_noise_E = (sig / np.sqrt(2)) / rms_resp_E
        eps = {str(p["index"]): rng.normal(0, sig, size=2).tolist() for p in deck["patterns"]}
        noise = {"eps": eps, "eps0": float(rng.normal(0, sig))}
        # re-identify c₀ from the noisy two-amplitude reads
        c0n = []
        for p in singles:
            i = p["modes"][0]
            Rs1, _ = resp_E(p, noise); Rs2, _ = resp_E(q2s[i], noise)
            dii = 2 * (Rs2 - Rs1) / (Q_2 ** 2 - Q_S ** 2)
            c0n.append(Rs1 - 0.5 * dii * Q_S ** 2)
        c0n = float(np.mean(c0n))
        bn = np.array([resp_E(p, noise)[0] - c0n for p in ordered])
        curve = rho_curve(A_all, bn, wts_rule, is_single)
        entry = {"sigma_E_uEh": s_ueh, "mode": "E", "rho_noise": rho_noise_E, "c0_reidentified": c0n,
                 "rho_final": curve[-1][1] if curve else None, "K_at": {}}
        entry["K_at_with_floor"] = {}
        for c in C_GRID:
            rho_star = c * rho_noise_E
            if rho_star >= RHO_MAX:
                entry["K_at"][str(c)] = "at-noise"
            else:
                entry["K_at"][str(c)] = next((n for n, r in curve if r <= rho_star), "not-reached")
            rho_star_f = max(rho_dry_floor * 1.1, rho_star)
            entry["K_at_with_floor"][str(c)] = ("at-noise" if rho_star_f >= RHO_MAX
                                                else next((n for n, r in curve if r <= rho_star_f), "not-reached"))
        noise_table.append(entry)
        # mode G at the same σ per gradient component (E_h/bohr — a different unit; the mode-G
        # line is σ_g ≤ 2.8 τ q_s; here we inject in the same numeric grid for the shape of K(σ))
        rngG = np.random.default_rng(int(s_ueh * 1000) + 5)
        bGn = np.concatenate([resp_G(p, noise_sigma=sig, rng=rngG) for p in ordered])
        rho_noise_G = sig / np.sqrt(2) / rms_resp_G
        curveG = []
        idx_tr_pairs = []
        for n, (p, h) in enumerate(zip(ordered, hold)):
            if h:
                continue
            idx_tr_pairs.append(n)
            if len(idx_tr_pairs) % 4 != 0:
                continue
            rows = np.concatenate([np.arange(k * M, (k + 1) * M) for k in idx_tr_pairs])
            d = fista_lasso(AG_all[rows], bGn[rows], wtsG, n_iter=1000)
            curveG.append((2 * len(idx_tr_pairs), rho_of(d, AG_ho, bG_ho)))
        entryG = {"sigma_g_uEh_per_bohr": s_ueh, "mode": "G", "rho_noise": rho_noise_G, "K_at": {}}
        for c in C_GRID:
            rho_star = c * rho_noise_G
            entryG["K_at"][str(c)] = ("at-noise" if rho_star >= RHO_MAX
                                      else next((n for n, r in curveG if r <= rho_star), "not-reached"))
        noise_table.append(entryG)

    # ---- DFT-arm floor from the nine-point scans (stage B2, if present)
    floor = json.load(open(os.path.join(out, "stageB2_floor.json"))) if os.path.exists(os.path.join(out, "stageB2_floor.json")) else None

    result = {
        "molecule": a["molecule"], "M": M, "deck_hash": deck["deck_hash"],
        "n_pairs_total": len(ordered), "n_pairs_holdout": int(hold.sum()), "n_single": len(singles),
        "energies_evaluated": 2 * len(deck["patterns"]) + 1,
        "Delta1_q": delta1_q.tolist(), "c0_Eh": c0, "c0_sd_Eh": c0_sd,
        "phi_iii_Eh_per_q3": phi_iii.tolist(),
        "w_rule_cm": w_rule, "lambda_rule": lam_rule, "w_table": w_table,
        "modeE": {"rho_curve": curve_E, "K_at_declared_rho": K_E, "K_off": (K_E - 2 * M) if K_E else None,
                  "rho_final_all_training": rho_final_E, "rms_resp_holdout_Eh": rms_resp_E,
                  "rho_off_curve": curve_E_off, "K_at_declared_rho_off": K_E_off,
                  "rms_offdiag_holdout_Eh": rms_off_E, "rho_dry_floor": rho_dry_floor,
                  "family_error_full": fam_err_full, "family_error_diagonal_only": fam_err_diag,
                  "family_error_diagonal_anchored": fam_err_anch, "rho_off_diagonal_anchored": rho_anch_off,
                  "quartic_corrected": {"rms_offdiag_after_quartic_uEh": rms_offq_E * 1e6, "rho_off": rho_qc_off,
                                        "family_error": fam_err_qc, "family_error_diag_two_amplitude": fam_err_diag_q,
                                        "Delta4_iiii": d4.tolist()}},
        "modeG": {"rho_curve": curve_G, "K_at_declared_rho": K_G, "rms_resp_holdout": rms_resp_G,
                  "family_error_full": fam_err_G},
        "flagged_offdiagonal_blocks": flagged[:40],
        "noise_column": noise_table, "dft_arm_floor": floor,
        "declared_rho": RHO_DECLARED, "rho_max": RHO_MAX,
        "deviations": ["low-rank term of the structural prior not implemented (banded l1 only)",
                       "completion patterns are random sparse mode combinations, not O1NumHess"],
    }
    json.dump(result, open(os.path.join(out, "stageC_recovery.json"), "w"), indent=1)
    return result


# ----------------------------------------------------------------------------- stage B2: DFT-arm floor
def stage_b2(psi4, a: dict, out: str) -> dict:
    """Nine-point ΔE(q) scans along four modes (the Q6 estimator applied to the DFT−DFT arm):
    σ_E = √(SSR/(n−p)) about a degree-4 fit, per mode and pooled."""
    z = np.load(os.path.join(out, "stageA_hessians.npz"))
    L, omega, Minv, coords0 = z["L"], z["omega_au"], z["Minv"], z["coords"]
    symbols = a["symbols"]; fam = a["families"]; freq = np.array(a["freq_low_cm"])
    picks = {}
    for f in ["CC-stretch", "CH-stretch", "CH-oop"]:
        cands = [k for k, g in enumerate(fam) if g == f]
        if cands:
            picks[f] = int(cands[len(cands) // 2])
    picks["totally-symmetric"] = int(a["totally_symmetric_index"])
    qs = np.linspace(-1, 1, 9)
    out_rows = {}
    ssr_tot, nu_tot = 0.0, 0
    for f, k in picks.items():
        dE = []
        for q in qs:
            v = np.zeros(len(omega)); v[k] = q
            x = coords0 + pattern_to_cartesian(v, L, omega, Minv).reshape(-1, 3)
            e = {}
            for arm, fn in FUNCTIONALS.items():
                m = make_molecule(psi4, symbols, x)
                e[arm] = psi4.energy(f"{fn}/{BASIS}", molecule=m)
            dE.append(e["high"] - e["low"])
        dE = np.array(dE)
        coef = np.polyfit(qs, dE, 4)
        res = dE - np.polyval(coef, qs)
        ssr = float(np.sum(res ** 2)); nu = len(qs) - 5
        sigma = np.sqrt(ssr / nu)
        ssr_tot += ssr; nu_tot += nu
        out_rows[f] = {"mode_index": k, "freq_cm": float(freq[k]), "sigma_E_uEh": sigma * 1e6,
                       "studentised_max": float(np.max(np.abs(res)) / (sigma + 1e-30)),
                       "dE_uEh": (dE * 1e6).tolist()}
        log(f"stage B2: {f} mode {k} ({freq[k]:.0f} cm⁻¹): σ_E = {sigma*1e6:.3f} µE_h")
    pooled = np.sqrt(ssr_tot / nu_tot) * 1e6
    res = {"per_mode": out_rows, "pooled_sigma_E_uEh": pooled, "n_points": 9, "degree": 4, "nu_pooled": nu_tot,
           "note": "DFT-arm floor: the scatter of the BHHLYP−B3LYP energy difference about a degree-4 fit; "
                   "the numerical (grid/SCF) noise of two DFT arms, not local-CC noise"}
    json.dump(res, open(os.path.join(out, "stageB2_floor.json"), "w"), indent=1)
    log(f"stage B2 done: pooled σ_E = {pooled:.3f} µE_h (ν = {nu_tot})")
    return res


# ----------------------------------------------------------------------------- report
def write_report(a, deck, c, out, quick):
    lines = []
    P = lines.append
    P(f"# Dry run — {a['molecule']} — {datetime.now():%Y-%m-%d %H:%M} — machine {a['machine']}, "
      f"{a['threads']} threads, psi4 {a['psi4']}{' — QUICK (reduced deck)' if quick else ''}")
    P("")
    P("## Timing (B2 laptop, this run)")
    for k, v in a["timing"].items():
        P(f"- {k}: {v/60:.2f} min")
    P("")
    P(f"## Modes: M = {a['M']}; families: " + ", ".join(f"{f}×{a['families'].count(f)}" for f in sorted(set(a['families']))))
    P(f"- totally symmetric mode used by the Q6 scan: index {a['totally_symmetric_index']} "
      f"({a['freq_low_cm'][a['totally_symmetric_index']]:.0f} cm⁻¹)")
    P("")
    P(f"## Deck: hash {deck['deck_hash'][:16]}…, {c['n_pairs_total']} ± pairs in K "
      f"({c['n_single']} single-mode + {c['n_pairs_total']-c['n_single']} off-diagonal), "
      f"{c['n_pairs_holdout']} held out (f_h = {deck['f_h']}), q_s = {deck['q_s']}, q₂ = {deck['q_2']}; "
      f"{c['energies_evaluated']} energies evaluated per arm (gradients too)")
    P("")
    P(f"## Reference constant c₀ = {c['c0_Eh']*1e6:.3f} ± {c['c0_sd_Eh']*1e6:.3f} µE_h (two-amplitude read over all modes)")
    P(f"## Δ₁ (∂ΔE/∂q at the B3LYP geometry, dimensionless q), |Δ₁| max = {np.max(np.abs(c['Delta1_q']))*1e6:.1f} µE_h per unit q")
    P("")
    P(f"## The w rule: w = {c['w_rule_cm']} cm⁻¹ (λ = {c['lambda_rule']}); table:")
    for t in c["w_table"]:
        P(f"- w = {t['w_cm']:.0f}: hold-out ρ = {t['rho_holdout']:.3f}, worst family RMS = {t['worst_family_rms_cm']:.2f} cm⁻¹")
    P("")
    P(f"## Mode E: K at declared ρ = {c['declared_rho']}: {c['modeE']['K_at_declared_rho']} energies "
      f"(K_off = {c['modeE']['K_off']}); ρ with all training pairs = {c['modeE']['rho_final_all_training']:.3f}; "
      f"RMS held-out response = {c['modeE']['rms_resp_holdout_Eh']*1e6:.2f} µE_h")
    P("- recovered-vs-direct RMS frequency error per family (cm⁻¹), full recovery (re-diagonalised) / diagonal-only (CMA-0):")
    for fam, v in c["modeE"]["family_error_full"].items():
        vd = c["modeE"]["family_error_diagonal_only"][fam]
        P(f"  - {fam} (n={v['n_modes']}): full {v['rms_full_rediag_cm']:.2f} / diag-only {vd['rms_full_rediag_cm']:.2f}")
    P(f"- ρ(n) curve (energies, ρ): " + ", ".join(f"({n},{r:.3f})" for n, r in c['modeE']['rho_curve'][::max(1,len(c['modeE']['rho_curve'])//12)]))
    e = c["modeE"]
    P(f"- **model floor** ρ_dry = {e['rho_dry_floor']:.4f} (noiseless responses, all training pairs): the quartic "
      f"contamination of the quadratic model at q_s = {deck['q_s']}")
    P(f"- **off-diagonal view**: RMS of the off-diagonal part of the held-out responses = {e['rms_offdiag_holdout_Eh']*1e6:.2f} µE_h "
      f"(vs {e['rms_resp_holdout_Eh']*1e6:.2f} raw); ρ_off(n) curve: " +
      ", ".join(f"({n},{r:.3f})" for n, r in e['rho_off_curve'][::max(1,len(e['rho_off_curve'])//12)]) +
      f"; K at declared ρ_off = {e['K_at_declared_rho_off']}")
    P(f"- **diagonal-anchored recovery** (diagonal from the single block, off-diagonals fitted to the residual): "
      f"ρ_off = {e['rho_off_diagonal_anchored']:.3f}; family RMS (cm⁻¹): " +
      ", ".join(f"{fam} {v['rms_full_rediag_cm']:.2f}" for fam, v in e['family_error_diagonal_anchored'].items()))
    qc = e["quartic_corrected"]
    P(f"- **quartic-corrected, diagonal-anchored recovery** (Δ_ii and Δ₄,iiii from the two amplitudes; Σ Δ₄ a⁴/24 subtracted): "
      f"off-diagonal RMS after subtraction = {qc['rms_offdiag_after_quartic_uEh']:.2f} µE_h; ρ_off = {qc['rho_off']:.3f}; family RMS (cm⁻¹): " +
      ", ".join(f"{fam} {v['rms_full_rediag_cm']:.2f}" for fam, v in qc['family_error'].items()) +
      "; two-amplitude diagonal alone: " +
      ", ".join(f"{fam} {v['rms_full_rediag_cm']:.2f}" for fam, v in qc['family_error_diag_two_amplitude'].items()))
    P("")
    P(f"## Mode G: K at declared ρ: {c['modeG']['K_at_declared_rho']} gradients; family error (full):")
    for fam, v in c["modeG"]["family_error_full"].items():
        P(f"  - {fam}: {v['rms_full_rediag_cm']:.2f} cm⁻¹")
    P("")
    P("## Off-diagonal blocks flagged large in the direct Δ₂ (|Δ_ij| > 0.2 × RMS diagonal); (i, j, ratio, ω_i, ω_j):")
    for t in c["flagged_offdiagonal_blocks"][:15]:
        P(f"- ({t[0]}, {t[1]}, {t[2]:+.2f}, {t[3]:.0f}, {t[4]:.0f})")
    P("")
    if c["dft_arm_floor"]:
        fl = c["dft_arm_floor"]
        P(f"## DFT-arm noise floor (nine-point degree-4 estimator): pooled σ_E = {fl['pooled_sigma_E_uEh']:.3f} µE_h (ν = {fl['nu_pooled']})")
        for f, v in fl["per_mode"].items():
            P(f"- {f} ({v['freq_cm']:.0f} cm⁻¹): σ_E = {v['sigma_E_uEh']:.3f} µE_h, max |studentised residual| = {v['studentised_max']:.2f}")
        P("")
    P("## Noise-injection column (K in energies or gradients at ρ* = c·ρ_noise; 'at-noise' if c·ρ_noise ≥ 0.5)")
    for e in c["noise_column"]:
        if e["mode"] == "E":
            P(f"- mode E, σ_E = {e['sigma_E_uEh']} µE_h: ρ_noise = {e['rho_noise']:.3f}; " +
              "; ".join(f"c={k}: K={v}" for k, v in e["K_at"].items()) +
              "  | with the model floor, ρ* = max(1.1·ρ_dry, c·ρ_noise): " +
              "; ".join(f"c={k}: K={v}" for k, v in e["K_at_with_floor"].items()))
        else:
            P(f"- mode G, σ_g = {e['sigma_g_uEh_per_bohr']} µE_h/bohr: ρ_noise = {e['rho_noise']:.3f}; " +
              "; ".join(f"c={k}: K={v}" for k, v in e["K_at"].items()))
    P("")
    P("## Deviations from the frozen form (this version)")
    for d in c["deviations"]:
        P(f"- {d}")
    P("")
    P("Printed by probes/dryrun_dft_delta_recovery.py. Both arms are DFT; no local-CC number exists here.")
    txt = "\n".join(lines)
    open(os.path.join(out, "REPORT.md"), "w", encoding="utf-8").write(txt)
    print("\n" + txt)


# ----------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--molecule", default="benzene")
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--quick", action="store_true", help="tiny deck, short noise grid (pipeline test)")
    ap.add_argument("--stage", default="all", choices=["A", "B", "B2", "C", "all"])
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))
    out = args.out or os.path.join(here, "results_dryrun", args.molecule + ("_quick" if args.quick else ""))
    os.makedirs(out, exist_ok=True)
    psi4 = psi4_setup(args.threads, os.path.join(out, "psi4.out"))
    log(f"dry run: {args.molecule}, out = {out}, quick = {args.quick}")

    a_path = os.path.join(out, "stageA.json")
    if args.stage == "A" or not os.path.exists(a_path):
        a = stage_a(psi4, args.molecule, out, args.threads)
    else:
        a = json.load(open(a_path))
    if args.stage in ("A",):
        return
    deck_path = os.path.join(out, "deck.json")
    if os.path.exists(deck_path):
        deck = json.load(open(deck_path))
    else:
        deck = build_deck(a, args.quick)
        json.dump(deck, open(deck_path, "w"))
        log(f"deck: {len(deck['patterns'])} patterns (incl. q₂ block), hash {deck['deck_hash'][:16]}…")
    if args.stage in ("B", "all"):
        stage_b(psi4, a, deck, out)
    if args.stage in ("B2", "all"):
        if not os.path.exists(os.path.join(out, "stageB2_floor.json")):
            stage_b2(psi4, a, out)
    if args.stage in ("C", "all"):
        c = stage_c(a, deck, out, args.quick)
        write_report(a, deck, c, out, args.quick)


if __name__ == "__main__":
    main()
