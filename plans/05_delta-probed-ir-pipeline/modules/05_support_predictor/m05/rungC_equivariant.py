"""Rung C — the E(3)-equivariant Δ-Hessian model of the pre-registration of 25 September 2026 (PaiNN-type body, rank-2 tensor head), built as
weekend-plan lever 4 (25/26 September 2026): loader, model, loss and a smoke test, unit-tested for equivariance; **no training on the pool** before
the Sunday decision (the pre-registration allows building; the test run waits).

Inputs (registered): atomic numbers, Cartesian coordinates of the B3LYP minimum, and the B3LYP Hessian as pair scalars only — per atom pair the
three invariants of its 3×3 block (trace, r̂ᵀ B r̂, ‖B‖_F); per atom the trace and norm of its diagonal block. Nothing else.
Body: three PaiNN-type interaction blocks, 64 scalar + 64 vector channels, 20 Gaussians, cosine cutoff 5 Å. No cross products, so the network is
O(3)-equivariant (rotations and reflections) and permutation-equivariant by construction; no augmentation.
Output: per atom pair within the cutoff ΔH_ij = a_ij I + b_ij r̂_ij r̂_ijᵀ + Σ_k c_ij^k (u_i^k u_j^kᵀ + u_j^k u_i^kᵀ), a, b, c invariant read-outs of the
symmetric pair features (s_i + s_j, s_i ⊙ s_j, the radial basis of d_ij), u a linear projection of the vector channels to 16 tensor channels; the
diagonal block ΔH_ii = −Σ_j ΔH_ij (translational invariance). Registered restriction: each off-diagonal block is itself symmetric.
Loss: mass-weighted MSE on the Cartesian ΔH (scaled by LOSS_SCALE to keep it O(1)) + 0.1 × MSE on the minimum-norm internal ΔF (B⁺ᵀ ΔH B⁺) so the
read-out's quantity is trained directly too.

    python m05/rungC_equivariant.py --smoke                # water (synthetic bond force field) and benzene (corpus A_8448043181): forward,
                                                           # rotation/reflection/permutation/translation errors, parameter count — seconds, 1 thread
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

AMU2AU = 1822.888486209
HARTREE2CM = 219474.6313632
BOHR2ANG = 0.529177210903
CUTOFF_BOHR = 5.0 / BOHR2ANG
N_RBF, N_S, N_V, N_BLOCKS, N_TENSOR = 20, 64, 64, 3, 16
LOSS_SCALE = 1.0e4          # mass-weighted Hessian corrections are ~1e-5 au; the loss is reported in (1e-4 au)² units
AUX_WEIGHT = 0.1
MASSES_AMU = {"H": 1.00782503, "C": 12.0, "N": 14.003074, "O": 15.99491462, "F": 18.99840316, "S": 31.97207117, "CL": 34.96885268}
Z_OF = {"H": 1, "C": 6, "N": 7, "O": 8, "F": 9, "S": 16, "CL": 17}


# ------------------------------------------------------------------------------------------------------------------ data
def pair_invariants(H: torch.Tensor, pos: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    """Registered pair scalars of a Cartesian Hessian: (N, N, 3) with trace, r̂ᵀ B r̂ and ‖B‖_F per block (the middle one is 0 on the diagonal),
    and (N, 2) per atom: trace and norm of its diagonal block."""
    n = pos.shape[0]
    B = H.reshape(n, 3, n, 3).permute(0, 2, 1, 3)                              # (N, N, 3, 3)
    r = pos[None, :, :] - pos[:, None, :]                                       # r_ij = x_j − x_i
    d = torch.linalg.norm(r, dim=-1)
    rhat = r / torch.where(d > 0, d, torch.ones_like(d))[..., None]
    tr = B.diagonal(dim1=-2, dim2=-1).sum(-1)
    proj = torch.einsum("ija,ijab,ijb->ij", rhat, B, rhat)
    nrm = torch.linalg.norm(B.reshape(n, n, 9), dim=-1)
    node = torch.stack([tr.diagonal(), nrm.diagonal()], -1)
    return torch.stack([tr, proj, nrm], -1), node


def edges_within(pos: torch.Tensor, cutoff: float = CUTOFF_BOHR) -> tuple[torch.Tensor, torch.Tensor]:
    """Directed edges i → j (i ≠ j) with d_ij < cutoff."""
    n = pos.shape[0]
    d = torch.cdist(pos, pos)
    mask = (d < cutoff) & ~torch.eye(n, dtype=torch.bool, device=pos.device)
    i, j = torch.nonzero(mask, as_tuple=True)
    return i, j


def synthetic_bond_hessian(pos: np.ndarray, bonds: list[tuple[int, int, float]]) -> np.ndarray:
    """A valence bond-stretch force field as a Cartesian Hessian (E_h/bohr²): translationally invariant, symmetric, exact — the smoke test's H_low."""
    n = pos.shape[0]
    H = np.zeros((3 * n, 3 * n))
    for a, b, k in bonds:
        u = pos[b] - pos[a]
        u = u / np.linalg.norm(u)
        blk = k * np.outer(u, u)
        for p, q, sgn in ((a, a, 1), (b, b, 1), (a, b, -1), (b, a, -1)):
            H[3 * p:3 * p + 3, 3 * q:3 * q + 3] += sgn * blk
    return H


def water() -> dict:
    """Water at a B3LYP-like geometry (bohr) with a synthetic H_low and a synthetic ΔH_true (5 % stiffer bonds, a weak H–H term): tests only."""
    pos = np.array([[0.0, 0.0, 0.2217], [0.0, 1.4309, -0.8867], [0.0, -1.4309, -0.8867]])
    bonds = [(0, 1, 0.55), (0, 2, 0.55)]
    H_low = synthetic_bond_hessian(pos, bonds)
    H_high = synthetic_bond_hessian(pos, [(a, b, 1.05 * k) for a, b, k in bonds]) + synthetic_bond_hessian(pos, [(1, 2, 0.02)])
    masses = np.array([MASSES_AMU["O"], MASSES_AMU["H"], MASSES_AMU["H"]])
    return dict(id="water_synthetic", symbols=["O", "H", "H"], Z=np.array([8, 1, 1]), pos=pos, masses=masses, H_low=H_low, dH_true=H_high - H_low)


def load_molecule(d: Path, use_analytic: bool = False) -> dict:
    """One corpus folder → Z, pos (bohr), masses (amu), H_low, dH_true (Cartesian, projected Hessians; analytic second route when asked and present)."""
    g = json.load(open(d / "geometry.json", encoding="utf-8"))
    tag = "_analytic" if use_analytic and (d / "hessian_b3lyp_analytic.npz").exists() and (d / "hessian_wb97x_analytic.npz").exists() else ""
    lo = np.load(d / f"hessian_b3lyp{tag}.npz")["H_projected"]
    hi = np.load(d / f"hessian_wb97x{tag}.npz")["H_projected"]
    sym = [s.upper() for s in g["symbols"]]
    return dict(id=d.name, symbols=sym, Z=np.array([Z_OF[s] for s in sym]), pos=np.asarray(g["coords_bohr"], float),
                masses=np.asarray(g["masses_amu"], float), H_low=lo, dH_true=hi - lo, analytic=bool(tag))


def load_molecules(mdir: Path, ids=None, use_analytic: bool = False) -> dict:
    out = {}
    for d in sorted(p for p in Path(mdir).iterdir() if (p / "hessian_b3lyp.npz").exists() and (p / "hessian_wb97x.npz").exists()):
        if ids is None or d.name in ids:
            out[d.name] = load_molecule(d, use_analytic)
    return out


def to_torch(m: dict, dtype=torch.float32) -> dict:
    t = dict(m)
    for k in ("pos", "H_low", "dH_true"):
        t[k] = torch.as_tensor(np.asarray(m[k]), dtype=dtype)
    t["Z"] = torch.as_tensor(np.asarray(m["Z"]), dtype=torch.long)
    mm = np.repeat(np.asarray(m["masses"]) * AMU2AU, 3)
    t["mw"] = torch.as_tensor(1.0 / np.sqrt(np.outer(mm, mm)), dtype=dtype)      # mass-weighting of a Cartesian Hessian
    return t


# ------------------------------------------------------------------------------------------------------------------ model
class RadialBasis(nn.Module):
    def __init__(self, n=N_RBF, cutoff=CUTOFF_BOHR):
        super().__init__()
        self.register_buffer("centres", torch.linspace(0.0, cutoff, n))
        self.gamma = 0.5 / (cutoff / n) ** 2
        self.cutoff = cutoff

    def forward(self, d):
        env = 0.5 * (torch.cos(np.pi * d / self.cutoff) + 1.0) * (d < self.cutoff)   # cosine cutoff
        return torch.exp(-self.gamma * (d[:, None] - self.centres[None, :]) ** 2) * env[:, None]


class Interaction(nn.Module):
    """One PaiNN interaction: message (scalars and vectors from neighbours, filtered by the radial basis and the pair invariants) + update
    (vector–vector products into scalars, gated vector rescaling)."""

    def __init__(self, n_s=N_S, n_v=N_V, n_filter_in=N_RBF + 16):
        super().__init__()
        self.phi = nn.Sequential(nn.Linear(n_s, n_s), nn.SiLU(), nn.Linear(n_s, n_s + 2 * n_v))
        self.W = nn.Linear(n_filter_in, n_s + 2 * n_v)
        self.U = nn.Linear(n_v, n_v, bias=False)
        self.V = nn.Linear(n_v, n_v, bias=False)
        self.a = nn.Sequential(nn.Linear(n_s + n_v, n_s), nn.SiLU(), nn.Linear(n_s, n_s + 2 * n_v))
        self.n_s, self.n_v = n_s, n_v

    def forward(self, s, v, i, j, filt, rhat):
        x = self.phi(s)[j] * self.W(filt)                                          # (E, n_s + 2 n_v)
        ds, dvv, dvs = torch.split(x, [self.n_s, self.n_v, self.n_v], dim=-1)
        dv = v[j] * dvv[:, None, :] + rhat[:, :, None] * dvs[:, None, :]          # (E, 3, n_v)
        s = s + torch.zeros_like(s).index_add(0, i, ds)
        v = v + torch.zeros_like(v).index_add(0, i, dv)
        Uv, Vv = self.U(v), self.V(v)                                              # (N, 3, n_v)
        vnorm = torch.sqrt((Vv ** 2).sum(1) + 1e-8)
        a = self.a(torch.cat([s, vnorm], -1))
        avv, asv, ass = torch.split(a, [self.n_v, self.n_v, self.n_s], dim=-1)
        v = v + avv[:, None, :] * Uv
        s = s + ass + asv * (Uv * Vv).sum(1)
        return s, v


class DeltaHessianModel(nn.Module):
    def __init__(self, n_s=N_S, n_v=N_V, n_blocks=N_BLOCKS, n_tensor=N_TENSOR, cutoff=CUTOFF_BOHR):
        super().__init__()
        self.emb = nn.Embedding(20, n_s)
        self.node_in = nn.Linear(2, n_s)
        self.rbf = RadialBasis(N_RBF, cutoff)
        self.inv = nn.Sequential(nn.Linear(3, 16), nn.SiLU(), nn.Linear(16, 16))
        self.blocks = nn.ModuleList(Interaction(n_s, n_v, N_RBF + 16) for _ in range(n_blocks))
        self.head = nn.Sequential(nn.Linear(2 * n_s + N_RBF, n_s), nn.SiLU(), nn.Linear(n_s, 2 + n_tensor))
        self.proj = nn.Linear(n_v, n_tensor, bias=False)
        self.cutoff, self.n_v = cutoff, n_v

    def forward(self, Z, pos, H_low):
        n = pos.shape[0]
        inv_pair, inv_node = pair_invariants(H_low, pos)
        i, j = edges_within(pos, self.cutoff)
        r = pos[j] - pos[i]
        d = torch.linalg.norm(r, dim=-1)
        rhat = r / d[:, None]
        rbf = self.rbf(d)
        filt = torch.cat([rbf, self.inv(inv_pair[i, j])], -1)
        s = self.emb(Z) + self.node_in(inv_node)
        v = torch.zeros(n, 3, self.n_v, dtype=pos.dtype, device=pos.device)
        for blk in self.blocks:
            s, v = blk(s, v, i, j, filt, rhat)
        u = self.proj(v)                                                           # (N, 3, n_tensor)
        p = self.head(torch.cat([s[i] + s[j], s[i] * s[j], rbf], -1))              # symmetric in i ↔ j
        a, b, c = p[:, 0], p[:, 1], p[:, 2:]
        eye = torch.eye(3, dtype=pos.dtype, device=pos.device)
        outer = torch.einsum("eak,ebk->ekab", u[i], u[j])
        blocks = (a[:, None, None] * eye + b[:, None, None] * torch.einsum("ea,eb->eab", rhat, rhat)
                  + torch.einsum("ek,ekab->eab", c, outer + outer.transpose(-1, -2)))
        dH = torch.zeros(n, n, 3, 3, dtype=pos.dtype, device=pos.device)
        dH = dH.index_put((i, j), blocks)
        diag = -dH.sum(1)                                                          # translational invariance: ΔH_ii = −Σ_j ΔH_ij
        dH = dH + torch.diag_embed(diag.permute(1, 2, 0)).permute(2, 3, 0, 1)
        return dH.permute(0, 2, 1, 3).reshape(3 * n, 3 * n)


def loss_terms(model, t, Bp=None):
    """Registered loss: mass-weighted MSE on ΔH (× LOSS_SCALE²) and, when the pseudo-inverse B⁺ is given, the internal-coordinate auxiliary term."""
    pred = model(t["Z"], t["pos"], t["H_low"])
    main = ((pred - t["dH_true"]) * t["mw"] * LOSS_SCALE).pow(2).mean()
    aux = torch.zeros((), dtype=pred.dtype)
    if Bp is not None:
        dF_p = Bp.T @ pred @ Bp
        dF_t = Bp.T @ t["dH_true"] @ Bp
        aux = (dF_p - dF_t).pow(2).mean() * LOSS_SCALE ** 2
    return main, aux, pred


def rotation(seed: int, reflect: bool = False) -> np.ndarray:
    q, _ = np.linalg.qr(np.random.default_rng(seed).normal(size=(3, 3)))
    if np.linalg.det(q) < 0:
        q[:, 0] = -q[:, 0]
    if reflect:
        q[:, 0] = -q[:, 0]
    return q


def transform_hessian(H: np.ndarray, R: np.ndarray, perm=None) -> np.ndarray:
    """H under x → R x (blocks R B Rᵀ) and an atom permutation."""
    n = H.shape[0] // 3
    B = H.reshape(n, 3, n, 3)
    B = np.einsum("ab,ibjc,dc->iajd", R, B, R)
    if perm is not None:
        B = B[perm][:, :, perm]
    return B.reshape(3 * n, 3 * n)


def equivariance_errors(model, m: dict, seed: int = 0) -> dict:
    """Max |Δ| between the transformed prediction and the prediction on the transformed input (rotation, reflection, translation, permutation),
    relative to the prediction's max |entry|. Float64. The pass line of the weekend plan: 1e-6."""
    with torch.no_grad():
        t = to_torch(m, torch.float64)
        ref = model(t["Z"], t["pos"], t["H_low"]).numpy()
        scale = np.abs(ref).max() + 1e-30
        out = {}
        rng = np.random.default_rng(seed)
        for name, R in (("rotation", rotation(seed)), ("reflection", rotation(seed, reflect=True))):
            mt = dict(m, pos=m["pos"] @ R.T + rng.normal(size=3), H_low=transform_hessian(m["H_low"], R))
            tt = to_torch(mt, torch.float64)
            out[name] = float(np.abs(model(tt["Z"], tt["pos"], tt["H_low"]).numpy() - transform_hessian(ref, R)).max() / scale)
        perm = rng.permutation(len(m["Z"]))
        mp = dict(m, Z=m["Z"][perm], pos=m["pos"][perm], H_low=transform_hessian(m["H_low"], np.eye(3), perm))
        tp = to_torch(mp, torch.float64)
        out["permutation"] = float(np.abs(model(tp["Z"], tp["pos"], tp["H_low"]).numpy() - transform_hessian(ref, np.eye(3), perm)).max() / scale)
        n = len(m["Z"])
        out["translation_sum_rule"] = float(np.abs(ref.reshape(n, 3, n, 3).sum(2)).max() / scale)   # Σ_j ΔH_ij = 0 for every i
        out["symmetry"] = float(np.abs(ref - ref.T).max() / scale)
    return out


def smoke(mdir: Path | None) -> int:
    torch.set_num_threads(1)
    torch.manual_seed(0)
    model = DeltaHessianModel().double()
    n_par = sum(p.numel() for p in model.parameters())
    print(f"DeltaHessianModel: {n_par} parameters; {N_BLOCKS} blocks × ({N_S} s + {N_V} v), {N_TENSOR} tensor channels, cutoff {CUTOFF_BOHR * BOHR2ANG:.1f} Å")
    mols = [water()]
    if mdir is not None and (Path(mdir) / "A_8448043181").exists():
        mols.append(load_molecule(Path(mdir) / "A_8448043181"))
    worst = 0.0
    for m in mols:
        t0 = time.time()
        err = equivariance_errors(model, m)
        t = to_torch(m, torch.float64)
        main, aux, pred = loss_terms(model, t)
        worst = max(worst, err["rotation"], err["reflection"], err["permutation"], err["translation_sum_rule"], err["symmetry"])
        print(f"  {m['id']}: {len(m['Z'])} atoms, {edges_within(t['pos'])[0].numel()} directed edges; loss {main.item():.3e} (untrained); "
              + "; ".join(f"{k} {v:.1e}" for k, v in err.items()) + f"; {time.time() - t0:.1f} s")
    ok = worst < 1e-6
    print(f"equivariance {'PASS' if ok else 'FAIL'}: worst relative error {worst:.1e} (pass line 1e-6)")
    return 0 if ok else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--molecules", default=str(Path(__file__).resolve().parents[1] / "corpus" / "molecules"))
    a = ap.parse_args()
    if a.smoke:
        sys.exit(smoke(Path(a.molecules)))
    print("training is not wired to the command line: the rung-C test run waits for the decision of Sunday 27 September 2026 (pre-registration).")
