"""Standout — the pattern proposer as a zero-CC simulation on the corpus Δ-Hessians (pre-registration of 26 September 2026).

Core pieces, reused from the dry-run probe wherever it defines the object (`probes/dryrun_dft_delta_recovery.py`: `build_deck`, `design_row_E`,
`band_weights`, `sym_index`, `rho_of`; psi4 is imported there only inside functions, so the import is cheap):

- `delta2(mol_dir)`: the mode-basis Δ₂ in dimensionless normal coordinates of the B3LYP modes, Δ_ij = L_iᵀ ΔH_mw L_j / √(ω_i ω_j) (E_h), plus the
  frequencies, modes and atom participations the proposers may see.
- `export_molecule(mol_dir)`: Δ₂, the deterministic deck P0 (the probe's `build_deck`, hash recorded) and the exact response of every pattern,
  R_s(a) = ½ aᵀ Δ a.
- `rho_curve(exp, order, ...)`: the banded-ℓ₁ recovery (FISTA, warm-started) consuming the single-mode block and then the off-diagonal patterns in the
  given order; ρ and ρ_off on the held-out patterns after every `stride` pairs, the truth-based relative off-diagonal Frobenius error beside them;
  `k_off_at(curve, level)` reads K_off.
- Orderings: `order_p0` (the hashed order), `order_oracle` (true |Δ_ij|), `order_by_scores` (any per-pair score → P1/P2 plug in here).

Units: E_h throughout; nothing is judged here."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PLAN / "probes"))
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "m05"))
import dryrun_dft_delta_recovery as PROBE  # noqa: E402
from learning_curve_layerA import AMU2AU, normal_modes  # noqa: E402

LAM_GRID = (1e-7, 1e-6, 1e-5, 1e-4)
W_BAND_CM = 200.0          # the probe's widest candidate band; the banded prior is free inside it
HOLDOUT_SEED = 20260906    # per the pre-registration (the probe's own is 20260905 + 1 = 20260906 — identical)


# ------------------------------------------------------------------------------------------------------------------ object
def delta2(mol_dir: Path, use_analytic: bool = False, hi_override: Path | None = None) -> dict:
    """Δ₂ of a corpus molecule: the high level is ωB97X unless `hi_override` names another projected Hessian at the same geometry — the CC-level test of
    28 Sep 2026 passes the CCSD(T) Hessian of the anchor (E8) here, so that the proxy and the real response go through one code path."""
    d = Path(mol_dir)
    g = json.load(open(d / "geometry.json", encoding="utf-8"))
    tag = "_analytic" if use_analytic and (d / "hessian_b3lyp_analytic.npz").exists() and (d / "hessian_wb97x_analytic.npz").exists() else ""
    lo = np.load(d / f"hessian_b3lyp{tag}.npz")["H_projected"]
    if hi_override is not None:
        z = np.load(hi_override)
        if "coords_bohr" in z.files and not np.allclose(z["coords_bohr"], np.asarray(g["coords_bohr"], float), atol=1e-6):
            raise ValueError(f"{hi_override}: geometry differs from {d / 'geometry.json'}")
        hi = z["H_projected"]
    else:
        hi = np.load(d / f"hessian_wb97x{tag}.npz")["H_projected"]
    masses = np.asarray(g["masses_amu"], float)
    w, freq, V, _ = normal_modes(lo, masses)
    m = np.repeat(masses * AMU2AU, 3)
    dHmw = (hi - lo) / np.sqrt(np.outer(m, m))
    om = np.sqrt(np.abs(w))
    D2 = (V.T @ dHmw @ V) / np.sqrt(np.outer(om, om))                         # ∂²ΔE/∂q_i∂q_j, E_h
    D2 = 0.5 * (D2 + D2.T)
    A = (V.reshape(len(masses), 3, -1) ** 2).sum(1)                              # atom participation (N, M)
    return dict(id=d.name, symbols=[s.upper() for s in g["symbols"]], M=int(V.shape[1]), freq_cm=freq, omega_au=om, D2=D2, participation=A,
                imaginary=bool((freq < 0).any()), analytic=bool(tag), pos=np.asarray(g["coords_bohr"], float), masses=masses, H_low=lo, V=V)


def pack(D2: np.ndarray, pairs) -> np.ndarray:
    return np.array([D2[i, j] for (i, j) in pairs])


def unpack(d: np.ndarray, pairs, M: int) -> np.ndarray:
    D = np.zeros((M, M))
    for n, (i, j) in enumerate(pairs):
        D[i, j] = D[j, i] = d[n]
    return D


# ------------------------------------------------------------------------------------------------------------------ export
def export_molecule(mol_dir: Path, use_analytic: bool = False, quick: bool = False, hi_override: Path | None = None) -> dict:
    """Δ₂, the deterministic deck and every exact response. `quick` narrows the deck as the probe's --quick does (smoke only); `hi_override` as in
    `delta2` (the deck and its hash still come from the B3LYP frequencies, so the CC-level export uses the same deck as the proxy export)."""
    o = delta2(mol_dir, use_analytic, hi_override)
    a = {"M": o["M"], "freq_low_cm": o["freq_cm"].tolist(), "molecule": o["id"]}
    deck = PROBE.build_deck(a, quick)
    pairs, _ = PROBE.sym_index(o["M"])
    d_true = pack(o["D2"], pairs)
    pats = [p for p in deck["patterns"] if p["kind"] != "q2"]                    # the q₂ block sits outside K (probe) and outside this experiment
    pats.sort(key=lambda p: p["index"])
    Avec = np.array([p["a"] for p in pats])                                      # (P, M)
    rows = np.array([PROBE.design_row_E(p["a"], pairs) for p in pats])           # (P, n_unknowns)
    R = rows @ d_true                                                            # exact responses, E_h
    return dict(id=o["id"], M=o["M"], freq_cm=o["freq_cm"], D2=o["D2"], participation=o["participation"], symbols=o["symbols"],
                deck_hash=deck["deck_hash"], kinds=np.array([p["kind"] for p in pats]), modes=[p["modes"] for p in pats],
                holdout=np.array([bool(p["holdout"]) for p in pats]), A=Avec, rows=rows, R=R, pairs=pairs, d_true=d_true,
                pos=o["pos"], masses=o["masses"], H_low=o["H_low"], V=o["V"])


def save_export(exp: dict, path: Path) -> None:
    np.savez_compressed(path, id=exp["id"], M=exp["M"], freq_cm=exp["freq_cm"], D2=exp["D2"], participation=exp["participation"],
                        symbols=np.array(exp["symbols"]), deck_hash=exp["deck_hash"], kinds=exp["kinds"], holdout=exp["holdout"], A=exp["A"], R=exp["R"],
                        modes=np.array(json.dumps(exp["modes"])), pos=exp["pos"], masses=exp["masses"], H_low=exp["H_low"], V=exp["V"])


def load_export(path: Path) -> dict:
    z = np.load(path, allow_pickle=False)
    M = int(z["M"])
    pairs, _ = PROBE.sym_index(M)
    A = z["A"]
    rows = np.array([PROBE.design_row_E(a, pairs) for a in A])
    D2 = z["D2"]
    return dict(id=str(z["id"]), M=M, freq_cm=z["freq_cm"], D2=D2, participation=z["participation"], symbols=list(z["symbols"]),
                deck_hash=str(z["deck_hash"]), kinds=z["kinds"], modes=json.loads(str(z["modes"])), holdout=z["holdout"], A=A, rows=rows, R=z["R"],
                pairs=pairs, d_true=pack(D2, pairs), pos=z["pos"], masses=z["masses"], H_low=z["H_low"], V=z["V"])


# ------------------------------------------------------------------------------------------------------------------ recovery
def fista(A, b, weights, d0=None, n_iter=2000, tol=1e-9):
    """min ½‖A d − b‖² + Σ weights|d|, warm-started at d0 (the probe's FISTA with a starting point)."""
    d = np.zeros(A.shape[1]) if d0 is None else d0.copy()
    y = d.copy()
    t = 1.0
    step = 1.0 / (np.linalg.norm(A, 2) ** 2 + 1e-12)
    AtA_b = A.T @ b
    AtA = A.T @ A
    for _ in range(n_iter):
        z = y - step * (AtA @ y - AtA_b)
        d_new = np.sign(z) * np.maximum(np.abs(z) - step * weights, 0.0)
        t_new = 0.5 * (1 + np.sqrt(1 + 4 * t * t))
        y = d_new + ((t - 1) / t_new) * (d_new - d)
        if np.linalg.norm(d_new - d) < tol * (1 + np.linalg.norm(d)):
            d = d_new
            break
        d, t = d_new, t_new
    return d


def order_p0(exp: dict) -> np.ndarray:
    """Indices of the non-held-out off-diagonal patterns in the deck's hashed order."""
    return np.array([n for n, k in enumerate(exp["kinds"]) if k != "single" and not exp["holdout"][n]])


def pair_scores_to_pattern_scores(exp: dict, S: np.ndarray) -> np.ndarray:
    """A per-pair score matrix S (M × M, symmetric, ≥ 0) → a score per pattern: two-mode patterns the pair's score, multi-mode patterns the *mean* over
    the pairs they touch (dated amendment of 26 Sep: the sum favoured broad random patterns over the targeted two-mode pattern of the strongest pair,
    which the planted-block test exposed; the mean is the expected information per unknown the pattern spends)."""
    out = np.zeros(len(exp["kinds"]))
    for n, (k, modes) in enumerate(zip(exp["kinds"], exp["modes"], strict=True)):
        if k == "single":
            continue
        touched = [S[i, j] for a, i in enumerate(modes) for j in modes[a + 1:]]
        out[n] = float(np.mean(touched)) if touched else 0.0
    return out


def order_by_scores(exp: dict, S: np.ndarray) -> np.ndarray:
    """Off-diagonal, non-held-out patterns by descending score; ties by the hashed order."""
    base = order_p0(exp)
    sc = pair_scores_to_pattern_scores(exp, S)
    return base[np.lexsort((base, -sc[base]))]


def order_oracle(exp: dict) -> np.ndarray:
    return order_by_scores(exp, np.abs(exp["D2"]))


def adaptive_pick(exp: dict, prior: np.ndarray, d: np.ndarray, remaining: np.ndarray, n: int, touched=None) -> np.ndarray:
    """The adaptive rule registered on 26 Sep 2026 (18:4x): among the patterns not yet measured, rank by z(prior score) + z(feedback score), where the
    feedback score of a pattern is the mean over its touched pairs of log10|Δ̂_ij| from the current reconstruction d (zero information at the start:
    a constant feedback column has zero z-score and the prior decides). Returns the next n pattern indices; ties by the hashed order."""
    S = np.log10(np.abs(unpack(d, exp["pairs"], exp["M"])) + 1e-8)
    if touched is not None:
        # optimism for what no measured pattern has touched yet (the planted dry run of 26 Sep 22:xx exposed the exploration hole of the plain
        # magnitude rule: an untouched pair has Δ̂ = 0 and would never be chosen); untouched pairs take the 90th percentile of the touched ones
        T = unpack(np.asarray(touched, float), exp["pairs"], exp["M"]) > 0
        off = ~np.eye(exp["M"], dtype=bool)
        seen = S[T & off]
        S = np.where(T, S, float(np.quantile(seen, 0.9)) if seen.size else 0.0)
    fb = pair_scores_to_pattern_scores(exp, S)[remaining]
    pr = np.asarray(prior, float)[remaining]
    z = lambda x: (x - x.mean()) / (x.std() + 1e-12) if x.std() > 0 else np.zeros_like(x)  # noqa: E731
    score = z(pr) + z(fb)
    return remaining[np.lexsort((remaining, -score))][:n]


def rho_curve(exp: dict, order: np.ndarray, stride: int = 4, lam_grid=LAM_GRID, w_cm: float = W_BAND_CM, noise_sigma: float = 0.0, seed: int = 0,
              inband_mask=None, adapt_prior=None):
    """Consume the single block, then `order`; after every `stride` patterns solve the banded-ℓ₁ recovery (λ chosen on the held-out patterns) and record
    (n_energies, ρ, ρ_off, frob_off, λ, frob_inband). n_energies counts a ± pair as 2 (mode E). Optional Gaussian noise per energy: σ on each of the two
    energies of a pair adds σ/√2 to R_s. `inband_mask` (pairs-length bool) selects the off-diagonal unknowns whose Frobenius error fills the sixth column
    (the pre-registration's in-band n₁₀); without it that column repeats the all-pairs value. `adapt_prior` (a score per pattern, 26 Sep 2026 18:4x):
    the order is then built as it goes — `order` only defines the pool — with `adaptive_pick` after every solve; the checkpoints and n_energies are
    identical to the fixed-order curve, so the read-outs compare directly."""
    pairs, rows, R = exp["pairs"], exp["rows"], exp["R"].copy()
    if noise_sigma > 0:
        R = R + np.random.default_rng(seed).normal(scale=noise_sigma / np.sqrt(2), size=R.shape)
    singles = np.array([n for n, k in enumerate(exp["kinds"]) if k == "single"])
    ho = np.where(exp["holdout"])[0]
    A_ho, b_ho = rows[ho], R[ho]
    diag_mask = np.array([i == j for (i, j) in pairs])
    # off-diagonal contribution of the held-out responses (the probe's ratio_off scaling)
    b_off = b_ho - A_ho[:, diag_mask] @ exp["d_true"][diag_mask]
    rms_off = np.sqrt(np.mean(b_off ** 2)) + 1e-30
    off_true = exp["d_true"][~diag_mask]
    frob_true = np.linalg.norm(off_true) + 1e-30
    in_mask = ~diag_mask if inband_mask is None else (np.asarray(inband_mask, bool) & ~diag_mask)
    in_true = np.linalg.norm(exp["d_true"][in_mask]) + 1e-30
    weights = {lam: PROBE.band_weights(pairs, exp["freq_cm"], w_cm, lam) for lam in lam_grid}
    curve = []
    warm = {lam: None for lam in lam_grid}
    consumed = list(singles)
    checkpoints = list(range(stride, len(order) + 1, stride))
    if not checkpoints or checkpoints[-1] != len(order):
        checkpoints.append(len(order))
    adaptive = adapt_prior is not None
    chosen, remaining, d_last = [], np.array(order, dtype=int), None
    for n_off in [0] + checkpoints:
        if adaptive and len(chosen) < n_off:
            touched = np.any(rows[np.array(consumed + chosen)] != 0, axis=0)
            pick = adaptive_pick(exp, adapt_prior, d_last, remaining, n_off - len(chosen), touched=touched)
            chosen += [int(p) for p in pick]
            remaining = remaining[~np.isin(remaining, pick)]
        idx = np.array(consumed + (chosen[:n_off] if adaptive else list(order[:n_off])))
        A_tr, b_tr = rows[idx], R[idx]
        best = None
        for lam in lam_grid:
            d = fista(A_tr, b_tr, weights[lam], d0=warm[lam])
            warm[lam] = d
            rho = PROBE.rho_of(d, A_ho, b_ho)
            if best is None or rho < best[0]:
                best = (rho, lam, d)
        rho, lam, d = best
        d_last = d
        rho_off = np.sqrt(np.mean((A_ho @ d - b_ho) ** 2)) / rms_off
        frob = np.linalg.norm(d[~diag_mask] - off_true) / frob_true
        frob_in = np.linalg.norm((d - exp["d_true"])[in_mask]) / in_true
        curve.append((int(2 * len(idx)), float(rho), float(rho_off), float(frob), float(lam), float(frob_in)))
    return curve


def k_off_at(curve, level: float, M: int, key: int = 2) -> int | None:
    """Smallest n_energies − 2M at which the chosen column (2 = ρ_off, 1 = ρ, 3 = frob_off all pairs, 5 = frob_off in band) is ≤ level; None if never."""
    for row in curve:
        if row[key] <= level:
            return int(row[0] - 2 * M)
    return None


def split_of(mol_id: str, layer: str) -> str:
    """Hashed split (sha1 of the id, as E6): layer-A parents are always evaluation; A2/B 70/10/20 train/val/eval."""
    if layer == "A":
        return "eval_parents"
    h = int(hashlib.sha1(mol_id.encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
    return "train" if h < 0.7 else ("val" if h < 0.8 else "eval")
