"""Rung C — train the equivariant Δ-Hessian model (`rungC_equivariant.py`) on the pair model's pool and read it out with the pair model's own read-outs
(pre-registration `PreRegistration_2026-09-25_RungC_Equivariant_vs_Pair_Model.md`, R1–R3 and R5 here; R4, the within-orbit spread, holds by construction
and is checked by `tests/test_rungC_equivariance.py`). Built 27 September 2026 as desk work; **nothing is run on the pool before the user's word**
(the Sunday-evening decision; `Decision_Memo_2026-09-27_RungC_Tonight.md`).

Same pool, sizes, seeds and hold-outs as `e7_rungB_pairs.py` (E6 splits, or `--split layerB`), same analytic-Hessian substitution, same read-out
functions (`readouts` of e7: E6 ratios per class, T2's basis-free corrected ω, the Cartesian residual ratio) — the equivariant model's Cartesian ΔH is
projected to the pair model's internal coordinates with the pseudo-inverse of the Wilson B, exactly the auxiliary term of the registered loss.
Fixed recipe (C1, from scratch): AdamW 1e-3, weight decay 1e-4, one molecule per step, `--epochs` passes over the training set (default 60 as the pair
model's fixed recipe), loss = mass-weighted MSE + 0.1 × internal ΔF term; no early stopping, no tuning (the fair-chance search applies to rung C as to
the pair model: a flat result under this one recipe licenses nothing). Output JSON mirrors e7's: zero rule, per size and seed the read-outs on (a) and (b)
(and (c) for the layer-B split), wall time; a markdown table beside it.

    python m05/rungC_train.py corpus/molecules out/E7_rungC_<date> --use-analytic [--sizes 45,100,all] [--seeds 0,1,2] [--epochs 60] [--threads 8]
    python m05/rungC_train.py corpus/molecules out/_smoke --smoke          # 5 molecules, 2 epochs, seed 0: mechanics only"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import e6_learning_curve as E6  # noqa: E402
import e7_t2_sqm as T2  # noqa: E402
from e7_rungB_pairs import readouts  # noqa: E402
from rungC_equivariant import BOHR2ANG, LOSS_SCALE, DeltaHessianModel, load_molecule, to_torch  # noqa: E402

AUX_WEIGHT = 0.1


class Scaled(torch.nn.Module):
    """The equivariant model with a fixed output scale: the training set's RMS ΔH (build note of 27 Sep — the pair model scales its targets per class the
    same way; without it the head starts four orders of magnitude above the targets and spends its epochs shrinking). Equivariance is untouched."""

    def __init__(self, model: DeltaHessianModel, scale: float, class_scale=None):
        super().__init__()
        self.model, self.scale = model, float(scale)
        # search stage 1 (27 Sep): one scale per entry class (own block, bonded pair, non-bonded pair)
        self.class_scale = None if class_scale is None else [float(x) for x in class_scale]

    def scale_tensor(self, t):
        if self.class_scale is None:
            return self.scale
        s = torch.as_tensor(self.class_scale, dtype=torch.float32)[t["cls"]]      # n × n
        return s.repeat_interleave(3, 0).repeat_interleave(3, 1)                     # 3n × 3n

    def forward(self, Z, pos, H_low, t=None):
        return self.model(Z, pos, H_low) * (self.scale if t is None else self.scale_tensor(t))


COV_RADIUS_ANG = {1: 0.31, 6: 0.76, 7: 0.71, 8: 0.66, 9: 0.57, 16: 1.05, 17: 1.02}


def entry_classes(m: dict) -> torch.Tensor:
    """n × n long tensor: 0 = the atom's own 3×3 block, 1 = a bonded pair (distance < 1.25 × the sum of covalent radii), 2 = any other pair."""
    pos = np.asarray(m["pos"], float)
    Z = np.asarray(m["Z"])
    r = np.array([COV_RADIUS_ANG.get(int(z), 0.8) for z in Z]) / BOHR2ANG
    d = np.linalg.norm(pos[:, None, :] - pos[None, :, :], axis=-1)
    cls = np.full(d.shape, 2, dtype=np.int64)
    cls[d < 1.25 * (r[:, None] + r[None, :])] = 1
    np.fill_diagonal(cls, 0)
    return torch.as_tensor(cls)


def _terms(model, t):
    """Registered main term (mass-weighted Cartesian MSE) and the relative internal-ΔF term, with the per-molecule scale tensor when the model has one."""
    pred = model(t["Z"], t["pos"], t["H_low"], t)
    main = ((pred - t["dH_true"]) * t["mw"] * LOSS_SCALE).pow(2).mean()
    dF_p = t["Bp"].T @ pred @ t["Bp"]
    aux = ((dF_p - t["dF_true"]) ** 2).mean() / t["dF_norm"]        # relative internal-ΔF term (build note of 27 Sep: the raw term is ~1e9 in a.u.)
    return main, aux, pred


def inner_split(train_ids: list, seed: int, fraction: float) -> tuple[list, list]:
    """(validation ids, fit ids): a deterministic per-seed split of the training ids for the search's stage read-out (seed offset 1000 keeps it
    independent of the training seed's permutation). fraction <= 0 returns ([], train_ids)."""
    if fraction <= 0:
        return [], list(train_ids)
    perm = np.random.default_rng(1000 + seed).permutation(len(train_ids))
    n_val = max(1, int(round(fraction * len(train_ids))))
    return [train_ids[k] for k in sorted(perm[:n_val])], [train_ids[k] for k in sorted(perm[n_val:])]


def load_pretrained_body(path: str | Path, reinit_head: bool = True, seed: int = 0) -> DeltaHessianModel:
    """A fresh DeltaHessianModel carrying the body of a `rungC_pretrain.py` checkpoint; the output head re-initialised (the registered C2 recipe:
    "the output head re-initialised and the whole network fine-tuned on ΔH") unless asked otherwise."""
    ck = torch.load(path, map_location="cpu", weights_only=False)
    model = DeltaHessianModel()
    model.load_state_dict(ck["body_state"])
    if reinit_head:
        torch.manual_seed(seed)
        for layer in model.head:
            if hasattr(layer, "reset_parameters"):
                layer.reset_parameters()
    return model


def check_pretrained_transfer(body: torch.nn.Module, tensors: dict, ids: list, limit: float = 1e3) -> float:
    """Pre-flight before fine-tuning a pretrained body (incident of 27 Sep 22:4x: a body pretrained on QM9 was finite on 12–18-atom molecules and
    1e15–1e18 on 23-atom fused rings). Runs the body on every training molecule; raises if any raw output is non-finite or above `limit` (a fresh
    body gives 15–35 on the corpus). Returns the worst |output|."""
    worst, worst_id = 0.0, None
    with torch.no_grad():
        for mid in ids:
            t = tensors[mid]
            out = body(t["Z"], t["pos"], t["H_low"])
            m = float(out.abs().max()) if torch.isfinite(out).all() else float("inf")
            if m > worst:
                worst, worst_id = m, mid
    if worst > limit:
        raise RuntimeError(f"pretrained body output {worst:.3g} on {worst_id} exceeds {limit:g} before fine-tuning — the body does not transfer to "
                           "this molecule size/density (pre-flight of 27 Sep; fine-tuning it would diverge)")
    return worst


def inner_val_aux(model, tensors: dict, ids: list) -> float:
    model.eval()
    with torch.no_grad():
        return float(np.mean([float(_terms(model, tensors[i])[1]) for i in ids])) if ids else float("nan")


def train_one(train_ids: list, tensors: dict, seed: int, epochs: int, lr: float = 1e-3, log=print, aux_weight: float = AUX_WEIGHT,
              loss_mode: str = "registered", scale_mode: str = "rms", val_ids: list | None = None, patience: int = 0,
              pretrained: str | None = None) -> tuple[torch.nn.Module, list]:
    """Defaults = the registered recipe C1 of 19:50 (27 Sep). The other values are the cells of the fair-chance search registered at 20:0x:
    aux_weight 1.0; loss_mode 'internal' (the relative internal-ΔF term alone); scale_mode 'class' (one output scale per entry class: diagonal
    3×3 block, bonded pair, non-bonded pair — the pair model's per-class standardisation); val_ids = inner validation molecules held out of the
    training ids (the stage read-out), patience > 0 = early stopping on their internal term with the best state restored."""
    torch.manual_seed(seed)
    scale = float(np.sqrt(np.mean([float((tensors[i]["dH_true"] ** 2).mean()) for i in train_ids])))
    class_scale = None
    if scale_mode == "class":
        sq, cnt = np.zeros(3), np.zeros(3)
        for i in train_ids:
            t = tensors[i]
            c = t["cls"].repeat_interleave(3, 0).repeat_interleave(3, 1).numpy()
            d2 = (t["dH_true"] ** 2).numpy()
            for k in range(3):
                sq[k] += d2[c == k].sum()
                cnt[k] += (c == k).sum()
        class_scale = np.sqrt(sq / np.maximum(cnt, 1))
    body = load_pretrained_body(pretrained, reinit_head=True, seed=seed) if pretrained else DeltaHessianModel()
    if pretrained:
        log(f"  pretrained body pre-flight: worst |output| {check_pretrained_transfer(body, tensors, train_ids):.3g} on the training molecules")
    model = Scaled(body, scale, class_scale)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    rng = np.random.default_rng(seed)
    hist, t0 = [], time.time()
    best, best_state, best_ep, since = float("inf"), None, 0, 0
    for ep in range(epochs):
        model.train()
        tot_main = tot_aux = 0.0
        for k in rng.permutation(len(train_ids)):
            t = tensors[train_ids[k]]
            opt.zero_grad()
            main, aux, _pred = _terms(model, t)
            loss = aux if loss_mode == "internal" else main + aux_weight * aux
            if not torch.isfinite(loss):
                raise RuntimeError(f"non-finite loss at epoch {ep + 1}, molecule {train_ids[k]} — aborting instead of training through NaN "
                                   "(guard of 27 Sep; a diverged run is an incident, not a result)")
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            opt.step()
            tot_main += float(main.detach())
            tot_aux += float(aux.detach())
        rec = dict(epoch=ep + 1, main=tot_main / len(train_ids), aux=tot_aux / len(train_ids))
        if val_ids:
            rec["val_aux"] = inner_val_aux(model, tensors, val_ids)
            if rec["val_aux"] < best - 1e-9:
                best, best_ep, since = rec["val_aux"], ep + 1, 0
                best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
            else:
                since += 1
        hist.append(rec)
        if (ep + 1) % 10 == 0 or ep == 0 or ep + 1 == epochs:
            val_txt = f" val {rec['val_aux']:.4g}" if val_ids else ""
            log(f"    seed {seed} epoch {ep + 1}/{epochs}: loss main {rec['main']:.4g} aux {rec['aux']:.4g}{val_txt} ({time.time() - t0:.0f} s)")
        if patience and val_ids and since >= patience:
            log(f"    seed {seed}: early stop at epoch {ep + 1}, best inner val {best:.4g} at epoch {best_ep}")
            break
    if best_state is not None and patience:
        model.load_state_dict(best_state)
    model.best_epoch = best_ep if val_ids else None
    model.class_scale_values = None if class_scale is None else [float(x) for x in class_scale]
    return model, hist


def predictor(model: torch.nn.Module, tensors: dict, mols: dict):
    """dF_of(i): the model's Cartesian ΔH projected to the pair model's internal coordinates (B⁺ᵀ ΔH B⁺), as `readouts` expects."""
    cache = {}

    def dF_of(i):
        if i not in cache:
            t = tensors[i]
            model.eval()
            with torch.no_grad():
                dH = model(t["Z"], t["pos"], t["H_low"], t).numpy().astype(float)
            Bp = np.linalg.pinv(mols[i]["B"])
            cache[i] = Bp.T @ dH @ Bp
        return cache[i]
    return dF_of


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("molecules")
    ap.add_argument("out_prefix")
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--sizes", default="45,100,175", help="the pair model's registered sizes; 'all' = the whole pool")
    ap.add_argument("--pool-layers", default="A,A2",
                    help="split e6: keep only these layers in the pool (the registered floor's pool was layer A + A2; layer B entered the corpus later)")
    ap.add_argument("--seeds", default="0,1,2")
    ap.add_argument("--epochs", type=int, default=None, help="default 60 (2 under --smoke unless given)")
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--split", default="e6", help="e6 (default) or layerB, as in e7_rungB_pairs.py")
    ap.add_argument("--use-analytic", action="store_true")
    ap.add_argument("--smoke", action="store_true", help="5 pool molecules, 2 epochs, seed 0, hold-outs cut to 3 each: mechanics only, never a result")
    ap.add_argument("--aux-weight", type=float, default=AUX_WEIGHT,
                    help="search stage 1 (27 Sep 20:0x): weight of the internal term beside the Cartesian one (registered 0.1)")
    ap.add_argument("--loss", default="registered", choices=["registered", "internal"],
                    help="search stage 1: 'internal' = the relative internal-ΔF term alone")
    ap.add_argument("--scale", default="rms", choices=["rms", "class"],
                    help="search stage 1: output scale = training RMS ΔH (registered) or one per entry class")
    ap.add_argument("--inner-val", type=float, default=0.0,
                    help="search: fraction of the training ids held out per seed as inner validation (the stage read-out)")
    ap.add_argument("--patience", type=int, default=0, help="search stage 2: early stopping on the inner validation term, best state restored (0 = off)")
    ap.add_argument("--pretrained", default=None, help="C2: a `rungC_pretrain.py` checkpoint; its body is loaded, the head re-initialised per seed")
    a = ap.parse_args()
    torch.set_num_threads(a.threads)
    t_start = time.time()
    log = lambda s: print(s, flush=True)  # noqa: E731

    mols = T2.load(a.molecules)
    test_a, test_b, cores, pool = E6.splits(mols)
    substituted = []
    if a.use_analytic:
        import e7_rungB_reread_analytic as RR
        for i, m in mols.items():
            d = Path(a.molecules) / i
            if (d / "hessian_b3lyp_analytic.npz").exists() and (d / "hessian_wb97x_analytic.npz").exists():
                RR.substitute(m, d)
                substituted.append(i)
        log(f"analytic second-route Hessians substituted for {len(substituted)} molecules")
    mols = {i: m for i, m in mols.items() if not m["imaginary"]}
    test_a = [i for i in test_a if i in mols]
    test_b = [i for i in test_b if i in mols]
    pool = [i for i in pool if i in mols]
    nat = {i: len(m["masses"]) for i, m in mols.items()}
    if a.split == "e6" and a.pool_layers:
        keep = set(a.pool_layers.split(","))
        pool = [i for i in pool if mols[i]["layer"] in keep]
    if a.split == "layerB":
        pool = sorted((i for i, m in mols.items() if m["layer"] == "B"), key=E6.sha)
        test_a = sorted(i for i, m in mols.items() if m["layer"] == "A")
        assert pool, "no admitted layer-B molecules under the molecules directory"
    sizes = sorted({min(int(s) if s != "all" else len(pool), len(pool)) for s in a.sizes.split(",")})
    seeds = [int(s) for s in a.seeds.split(",")]
    if a.smoke:
        sizes, seeds, a.epochs = [min(5, len(pool))], [0], (a.epochs or 2)
        test_a, test_b = test_a[:3], test_b[:3]
    a.epochs = a.epochs or 60

    # tensors for the equivariant model (Cartesian; the registered inputs), plus B⁺ for the auxiliary term and the read-out projection
    needed = set(pool[: sizes[-1]]) | set(test_a) | set(test_b)
    if a.split == "layerB":
        needed |= {i for i, m in mols.items() if m["layer"] == "A2"}
    tensors = {}
    for i in sorted(needed):
        m = load_molecule(Path(a.molecules) / i, use_analytic=a.use_analytic)
        t = to_torch(m)
        t["Bp"] = torch.as_tensor(np.linalg.pinv(mols[i]["B"]), dtype=torch.float32)
        t["dF_true"] = t["Bp"].T @ t["dH_true"] @ t["Bp"]
        t["dF_norm"] = (t["dF_true"] ** 2).mean().clamp_min(1e-30)
        t["cls"] = entry_classes(m)
        tensors[i] = t
    log(f"{len(mols)} molecules; pool {len(pool)}; hold-out (a) {len(test_a)}, (b) {len(test_b)} ({cores}); sizes {sizes}; seeds {seeds}; epochs {a.epochs}; "
        f"threads {a.threads}; model {sum(p.numel() for p in DeltaHessianModel().parameters()):,} parameters" + (" — SMOKE" if a.smoke else ""))

    tests = {"a": test_a, "b": test_b}
    res = dict(date=datetime.now().strftime("%Y-%m-%d %H:%M"), smoke=a.smoke,
               model="rungC_equivariant C1 (from scratch; output scaled by the training set's RMS ΔH, or per entry class)",
               n_molecules=len(mols), holdout_a=test_a, holdout_b=test_b, scaffold_cores=cores, pool=len(pool), pool_ids=pool, pool_layers=a.pool_layers,
               sizes=sizes, seeds=seeds, epochs=a.epochs, lr=a.lr, aux_weight=a.aux_weight, loss=a.loss, scale=a.scale, inner_val=a.inner_val,
               patience=a.patience, pretrained=a.pretrained,
               substituted_analytic=substituted, curve={})
    res["zero_rule"] = {h: readouts(mols, ids, pool, lambda i: np.zeros_like(mols[i]["F_low"])) for h, ids in tests.items() if ids}
    lines = [f"# Rung C (equivariant ΔH, C1 from scratch) — {a.out_prefix} ({res['date']}){' — SMOKE, not a result' if a.smoke else ''}", "",
             f"recipe: lr {a.lr}, epochs {a.epochs}, loss {a.loss}, aux weight {a.aux_weight}, output scale {a.scale}, "
             f"inner validation {a.inner_val}, patience {a.patience}; pool layers {a.pool_layers}", "",
             "| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for n in sizes:
        tr = pool[:n]
        if a.split == "layerB":
            nmax = max(nat[i] for i in tr)
            tests["c"] = sorted(i for i, m in mols.items() if m["layer"] == "A2" and nat[i] > nmax and i not in set(test_b))
            res.setdefault("holdout_c", {})[str(n)] = dict(n_atoms_above=nmax, ids=tests["c"])
            if tests["c"]:
                res.setdefault("zero_rule_c", {})[str(n)] = readouts(mols, tests["c"], tr, lambda i: np.zeros_like(mols[i]["F_low"]))
        row = {"n": n, "per_seed": []}
        for seed in seeds:
            t1 = time.time()
            val_ids, fit_ids = inner_split(tr, seed, a.inner_val)
            model, hist = train_one(fit_ids, tensors, seed, a.epochs, a.lr, log, a.aux_weight, a.loss, a.scale, val_ids, a.patience, a.pretrained)
            dF_of = predictor(model, tensors, mols)
            out = {"seed": seed, "train_history": hist, "output_scale": model.scale, "class_scale": model.class_scale_values,
                   "seconds": round(time.time() - t1, 1), "inner_val_ids": val_ids,
                   "inner_val_aux": (inner_val_aux(model, tensors, val_ids) if val_ids else None), "best_epoch": model.best_epoch}
            if val_ids:
                log(f"  n={n} seed {seed}: inner validation internal term {out['inner_val_aux']:.4g} on {len(val_ids)} molecules (fit on {len(fit_ids)})")
            for h, ids in tests.items():
                if not ids:
                    continue
                r = readouts(mols, ids, tr, dF_of)
                out[h] = r
                z = res["zero_rule"][h] if h in res["zero_rule"] else res["zero_rule_c"][str(n)]
                lines.append(f"| {n} | {seed} | ({h}) | {r['coupling_rms']:.2f} | {r['coupling_zero_rms']:.2f} | {r['coupling_ratio']:.2f} | "
                             f"{r['corrected_freq_rms']:.2f} | "
                             f"{r['corrected_freq_rms_zero_rule']:.2f} | {r['dH_residual_ratio']:.3f} | {out['seconds']:.0f} |")
                log(f"  n={n} seed {seed} ({h}): ring couplings {r['coupling_rms']:.2f} vs zero {r['coupling_zero_rms']:.2f} "
                    f"(ratio {r['coupling_ratio']:.2f}) | corrected ω "
                    f"{r['corrected_freq_rms']:.2f} (zero {r['corrected_freq_rms_zero_rule']:.2f}) | ΔH residual ratio {r['dH_residual_ratio']:.3f}")
                del z
            row["per_seed"].append(out)
        res["curve"][str(n)] = row
    res["seconds"] = round(time.time() - t_start, 1)
    lines += ["", f"wall {res['seconds']:.0f} s; read-out keys: {sorted(k for k in next(iter(res['zero_rule'].values())).keys())}", ""]
    json.dump(res, open(a.out_prefix + ".json", "w"), indent=1)
    Path(a.out_prefix + ".md").write_text("\n".join(lines), encoding="utf-8")
    log(f"wrote {a.out_prefix}.json/.md in {res['seconds']:.0f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
