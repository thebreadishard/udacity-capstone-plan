"""Fill the pattern-target cache ahead of training (1 Oct 2026, lever 4): for every admitted molecule of the given layers compute the mass-weighted
least-squares ΔF on the pattern (`rungC_targets.cached_pattern_ls_target`, cache `<out>/ls_targets/<pattern>/<id>.npz`) with a pool of workers, and
write one summary line per molecule (pattern pairs, seconds, residual of the projected target vs the fit) so the bound is on record for the whole pool.

    python probes/rungC_ls_targets_build.py <corpus/molecules> <out dir> --pattern d [--layers A,A2,B] [--workers 2] [--use-analytic]
"""
import argparse
import json
import sys
import time
from datetime import datetime
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
M05 = HERE.parent / "modules" / "05_support_predictor" / "m05"
sys.path.insert(0, str(M05))

_MOLS = None


def _init(mdir: str):
    global _MOLS
    import e7_t2_sqm as T2
    _MOLS = T2.load(Path(mdir))


def _one(args):
    mdir, out, pattern, i, use_analytic, lam = args
    import torch
    from rungC_equivariant import load_molecule
    from rungC_targets import cached_pattern_ls_target, projected_target, weighted_residual
    from rungC_train import pattern_classes
    torch.set_num_threads(1)
    t0 = time.time()
    m = load_molecule(Path(mdir) / i, use_analytic=use_analytic)
    cls = pattern_classes(Path(mdir) / i, _MOLS[i], pattern)
    mask = (cls >= 0).numpy()
    B = _MOLS[i]["B"]
    X, cached = cached_pattern_ls_target(Path(out) / "ls_targets", i, pattern, m["dH_true"], B, m["masses"], mask, lam_rel=lam)
    projected = np.where(mask, projected_target(m["dH_true"], B), 0.0)
    return dict(id=i, n_atoms=len(m["masses"]), n_pairs=int(np.triu(mask).sum()), seconds=round(time.time() - t0, 1), from_cache=cached,
                residual_projected=weighted_residual(m["dH_true"], B, m["masses"], projected), residual_ls=weighted_residual(m["dH_true"], B, m["masses"], X),
                scale_ratio=float(np.abs(X).max() / max(np.abs(projected).max(), 1e-30)))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("molecules")
    ap.add_argument("out")
    ap.add_argument("--pattern", default="d", choices=["c", "d"])
    ap.add_argument("--layers", default="A,A2,B")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--use-analytic", action="store_true")
    ap.add_argument("--lam", type=float, default=None, help="relative ridge toward the projected truth (default rungC_targets.LAM_REL)")
    a = ap.parse_args()
    t0 = time.time()
    import e7_t2_sqm as T2
    mols = T2.load(Path(a.molecules))
    layers = set(a.layers.split(","))
    ids = sorted(i for i, m in mols.items() if m["layer"] in layers and not m["imaginary"])
    ids.sort(key=lambda i: len(mols[i]["masses"]))                # small first: the cache fills for the 175 pool early
    from rungC_targets import LAM_REL
    lam = LAM_REL if a.lam is None else a.lam
    print(f"{len(ids)} molecules of layers {sorted(layers)}, pattern {a.pattern}, lam_rel {lam:g}, {a.workers} workers", flush=True)
    rows = []
    with Pool(a.workers, initializer=_init, initargs=(a.molecules,)) as pool:
        for k, r in enumerate(pool.imap(_one, [(a.molecules, a.out, a.pattern, i, a.use_analytic, lam) for i in ids]), 1):
            rows.append(r)
            print(f"  {k}/{len(ids)} {r['id']} atoms {r['n_atoms']} pairs {r['n_pairs']} {r['seconds']} s{' (cache)' if r['from_cache'] else ''} "
                  f"residual projected {r['residual_projected']:.3f} → ls {r['residual_ls']:.3f}; scale ×{r['scale_ratio']:.1f}", flush=True)
    res = dict(date=datetime.now().strftime("%Y-%m-%d %H:%M"), pattern=a.pattern, lam_rel=lam, layers=sorted(layers), n=len(rows), rows=rows,
               seconds=round(time.time() - t0))
    out = Path(a.out) / f"ls_targets_build_{a.pattern}_lam{lam:g}_{datetime.now():%Y-%m-%d}.json"
    json.dump(res, open(out, "w"), indent=1)
    rp = np.array([r["residual_projected"] for r in rows])
    rl = np.array([r["residual_ls"] for r in rows])
    sr = np.array([r["scale_ratio"] for r in rows])
    print(f"median residual projected {np.median(rp):.3f} → ls {np.median(rl):.3f}; scale ratio median {np.median(sr):.1f}, max {sr.max():.1f}; "
          f"wrote {out} in {res['seconds']} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
