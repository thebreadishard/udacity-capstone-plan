"""GFN2-xTB Hessians by dxtb for a quartic force field (18 Oct 2026; S2 amendment 4) — the counterpart of pyscf_hessians_for_qff.py,
writing the same qcschema-like records, so that dpir.qff assembles the force field unchanged. Runs in the WSL env `dxtb` (dxtb 0.4.0,
tad-libcint 0.3.0, torch CPU). The xtb binary's own Hessian file is rotation-projected and unusable away from a minimum.

    python dxtb_hessians_for_qff.py hess <stub_dir> <out_dir> --method autograd|forces-fd [--shard k/K]   every stub (existing
                                                                                    results skipped; with --shard, stub i when i mod K = k)
    python dxtb_hessians_for_qff.py one <record.json> --method autograd|forces-fd            one Hessian: time and the record's ω

Methods: 'autograd' — dxtb's Hessian by automatic differentiation (exact; memory grows steeply with size, dxtb issue #231);
'forces-fd' — central differences of dxtb's autograd forces, step FD_STEP, symmetrised (one numerical layer; 6N force calls, little
memory). Every quantity uses a fresh AutogradCalculator: a second call on the same calculator returned a wrong gradient in dxtb 0.4.0
(memory 'reference-dxtb-pitfalls'). GFN2 needs the libcint integral driver and the autograd calculator (no analytic GFN2 gradient in 0.4.0).
"""
import argparse
import glob
import json
import os
import sys
import time

import numpy as np
import torch
from dxtb import GFN2_XTB
from dxtb.calculators import AutogradCalculator

Z = {"H": 1, "C": 6, "N": 7, "O": 8, "F": 9, "S": 16, "Cl": 17}
OPTS = {"maxiter": 200, "mixer": "anderson", "scf_mode": "full", "verbosity": 0, "f_atol": 1e-10, "x_atol": 1e-10, "int_driver": "libcint"}
DD = {"dtype": torch.double, "device": torch.device("cpu")}
FD_STEP = 1e-3            # bohr, central differences of exact forces: truncation O(h²) ≈ 1e-6 relative
METHODS = ("autograd", "forces-fd")


def calculator(symbols):
    return AutogradCalculator(torch.tensor([Z[s] for s in symbols]), GFN2_XTB, opts=OPTS, **DD)


def energy(symbols, geom_bohr) -> float:
    return float(calculator(symbols).energy(torch.tensor(np.asarray(geom_bohr).reshape(-1, 3), **DD), 0))


def gradient(symbols, geom_bohr) -> np.ndarray:
    pos = torch.tensor(np.asarray(geom_bohr).reshape(-1, 3), **DD).requires_grad_(True)
    return -calculator(symbols).forces(pos, 0).detach().numpy().reshape(-1)


def hessian(symbols, geom_bohr, method) -> np.ndarray:
    """The Cartesian Hessian (E_h/bohr², 3N × 3N) by `method`."""
    if method not in METHODS:
        raise ValueError(f"unknown method {method!r}; one of {METHODS}")
    x = np.asarray(geom_bohr, float).reshape(-1)
    if method == "autograd":
        pos = torch.tensor(x.reshape(-1, 3), **DD).requires_grad_(True)
        return calculator(symbols).hessian(pos, 0, matrix=True).detach().numpy()
    n = x.size
    H = np.zeros((n, n))
    for k in range(n):
        xp, xm = x.copy(), x.copy()
        xp[k] += FD_STEP
        xm[k] -= FD_STEP
        H[:, k] = (gradient(symbols, xp) - gradient(symbols, xm)) / (2 * FD_STEP)
    return 0.5 * (H + H.T)


def record(symbols, geom, H, method):
    return {"driver": "hessian", "model": {"method": "GFN2-xTB", "basis": f"dxtb 0.4.0 ({method})"},
            "molecule": {"symbols": symbols, "geometry": list(np.asarray(geom, float).reshape(-1))},
            "return_result": H.reshape(-1).tolist(), "properties": {"return_energy": energy(symbols, geom)}}


def parse_shard(text):
    """'k/K' → (k, K) with 0 ≤ k < K."""
    k, n = (int(v) for v in text.split("/"))
    if not 0 <= k < n:
        raise ValueError(f"shard {text}: need 0 <= k < K")
    return k, n


def hessians(stub_dir, out_dir, method, shard=(0, 1)):
    """dxtb's Hessian at every stub of stub_dir (this shard's share), as records in out_dir; one progress line per Hessian."""
    os.makedirs(out_dir, exist_ok=True)
    stubs = sorted(glob.glob(os.path.join(stub_dir, "*.json")))
    mine = [s for i, s in enumerate(stubs) if i % shard[1] == shard[0]]
    todo = [s for s in mine if not os.path.exists(os.path.join(out_dir, os.path.basename(s)))]
    t_all = time.time()
    for k, path in enumerate(todo, 1):
        t0 = time.time()
        with open(path, encoding="utf-8") as fh:
            d = json.load(fh)
        sym, geom = d["molecule"]["symbols"], d["molecule"]["geometry"]
        tmp = os.path.join(out_dir, os.path.basename(path) + ".tmp")
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(record(sym, geom, hessian(sym, geom, method), method), fh)
        os.replace(tmp, os.path.join(out_dir, os.path.basename(path)))
        print(f"[{time.strftime('%H:%M:%S')}] {k}/{len(todo)} {os.path.basename(path)} in {time.time() - t0:.1f} s", flush=True)
    print(f"done: {len(todo)} Hessians in {(time.time() - t_all) / 60:.1f} min", flush=True)


def one(path, method):
    """One Hessian at a record's geometry: its time and the lowest and highest harmonic ω (cm⁻¹), as a measurement before a batch."""
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
    from dpir.qff import harmonic
    with open(path, encoding="utf-8") as fh:
        d = json.load(fh)
    sym, geom = d["molecule"]["symbols"], np.asarray(d["molecule"]["geometry"], float)
    t0 = time.time()
    H = hessian(sym, geom, method)
    w = np.asarray(harmonic(H, sym, geom.reshape(-1, 3)).omega_cm)
    print(f"{method}: {time.time() - t0:.1f} s; ω {w.min():.1f} … {w.max():.1f} cm⁻¹ ({w.size} modes)", flush=True)
    return H


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    h = sub.add_parser("hess")
    h.add_argument("stub_dir")
    h.add_argument("out_dir")
    h.add_argument("--method", choices=METHODS, required=True)
    h.add_argument("--shard", type=parse_shard, default=(0, 1), help="k/K: this process takes stub i when i mod K = k")
    o = sub.add_parser("one")
    o.add_argument("record")
    o.add_argument("--method", choices=METHODS, required=True)
    a = ap.parse_args()
    if a.cmd == "hess":
        hessians(a.stub_dir, a.out_dir, a.method, a.shard)
    else:
        one(a.record, a.method)
    return 0


if __name__ == "__main__":
    sys.exit(main())
