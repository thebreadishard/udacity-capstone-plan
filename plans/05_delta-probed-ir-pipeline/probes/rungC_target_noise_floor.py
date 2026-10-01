"""Target noise floor of the corpus Δ-Hessians (1 Oct 2026, Sherlock day): on every molecule that has both routes — the psi4 finite-difference
Hessians of the corpus deck and the pyscf analytic Hessians of 23 September — read the finite-difference ΔH *as if it were a prediction* of the
analytic ΔH, in exactly the read-outs rung C is judged on (ring-coupling ratio, corrected ω, ΔH residual). The ratio that comes out is the share of
the target that is finite-difference noise; no network trained on those targets can be expected below it on the same read-out.

The second-route molecules were chosen as suspects (20 with an imaginary mode in one functional, ledger 23 Sep 16:2x), so the numbers are split:
'clean' = no imaginary mode (the ones the training pool admits), 'suspect' = the rest (excluded from the pool). The clean group is the estimate that
applies to training; the suspect group is the upper bound.

    python probes/rungC_target_noise_floor.py modules/05_support_predictor/corpus/molecules modules/05_support_predictor/out/rungC_target_noise_floor_<date>
"""
import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "modules" / "05_support_predictor" / "m05"))
import e7_rungB_pairs as RB  # noqa: E402
import e7_t2_posthoc as PH  # noqa: E402
import e7_t2_sqm as T2  # noqa: E402


def analytic_delta(d: Path) -> np.ndarray | None:
    lo, hi = d / "hessian_b3lyp_analytic.npz", d / "hessian_wb97x_analytic.npz"
    if not (lo.exists() and hi.exists()):
        return None
    return np.load(hi)["H_projected"] - np.load(lo)["H_projected"]


def scalar_items(res: dict) -> dict:
    return {k: v for k, v in res.items() if isinstance(v, (int, float))}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("molecules")
    ap.add_argument("out_prefix")
    a = ap.parse_args()
    t0 = time.time()
    mdir = Path(a.molecules)
    mols = T2.load(mdir)
    ids = sorted(i for i in mols if analytic_delta(mdir / i) is not None)
    if not ids:
        raise SystemExit("no molecule has both routes")
    dF_fd, mols_an, kcheck = {}, {}, []
    for i in ids:
        m = mols[i]
        Bp = np.linalg.pinv(m["B"])
        dH_an = analytic_delta(mdir / i)
        dF_fd[i] = Bp.T @ m["dH_true"] @ Bp
        dF_an = Bp.T @ dH_an @ Bp
        K_fd = PH.k_of(m, dF_fd[i])
        kcheck.append(float(np.abs(K_fd - m["K"]).max() / np.abs(m["K"]).max()))   # the formula reproduces the stored K up to the B reconstruction
        mols_an[i] = dict(m, K=PH.k_of(m, dF_an), dH_true=dH_an)
    groups = {"clean": [i for i in ids if not mols[i]["imaginary"]], "suspect": [i for i in ids if mols[i]["imaginary"]], "all": ids}
    res = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "n_two_route": len(ids), "ids": ids, "k_formula_max_rel_dev": max(kcheck),
           "groups": {}, "per_molecule": {}}
    for name, g in groups.items():
        if not g:
            continue
        fd = RB.readouts(mols_an, g, g, lambda i: dF_fd[i])                     # finite differences read as a prediction of the analytic truth
        zero = RB.readouts(mols_an, g, g, lambda i: np.zeros_like(dF_fd[i]))
        res["groups"][name] = {"n": len(g), "ids": g, "fd_as_prediction": scalar_items(fd), "zero": scalar_items(zero)}
    for i in ids:
        try:
            r = RB.readouts(mols_an, [i], ids, lambda j: dF_fd[j])
            res["per_molecule"][i] = {"name": mols[i].get("name", ""), "imaginary": bool(mols[i]["imaginary"]), "n_atoms": int(len(mols[i]["masses"])),
                                      **{k: v for k, v in scalar_items(r).items() if "ratio" in k or "rms" in k}}
        except Exception as e:                                                    # a molecule without two ring modes has no coupling read-out
            res["per_molecule"][i] = {"error": repr(e)[:120]}
    res["seconds"] = round(time.time() - t0)
    out = Path(a.out_prefix)
    out.parent.mkdir(parents=True, exist_ok=True)
    json.dump(res, open(out.with_suffix(".json"), "w"), indent=1)
    lines = [f"# Target noise floor — finite-difference ΔH read as a prediction of the analytic ΔH ({res['date']})", "",
             f"{len(ids)} two-route molecules; K formula vs stored K: max relative deviation {max(kcheck):.2e}.", "",
             "| group | n | ring-coupling rms | zero rms | **ratio = noise share** | corrected ω rms | zero ω | ΔH residual ratio |", "|---|---|---|---|---|---|---|---|"]
    for name, g in res["groups"].items():
        f, z = g["fd_as_prediction"], g["zero"]
        om = next((k for k in f if "freq" in k and "rms" in k and "zero" not in k), None)
        lines.append(f"| {name} | {g['n']} | {f['coupling_rms']:.2f} | {f['coupling_zero_rms']:.2f} | **{f['coupling_ratio']:.2f}** | "
                     f"{f.get(om, float('nan')):.2f} | {z.get(om, float('nan')):.2f} | {f['dH_residual_ratio']:.3f} |")
    lines += ["", "Per molecule (ring-coupling ratio; 'imag' = an imaginary mode in the corpus deck, excluded from the training pool):", "",
              "| id | name | atoms | imag | ratio | ΔH residual ratio |", "|---|---|---|---|---|---|"]
    for i, r in res["per_molecule"].items():
        if "error" in r:
            lines.append(f"| {i} | | | | — | {r['error']} |")
        else:
            lines.append(f"| {i} | {r['name']} | {r['n_atoms']} | {'yes' if r['imaginary'] else 'no'} | {r.get('coupling_ratio', float('nan')):.2f} | "
                         f"{r.get('dH_residual_ratio', float('nan')):.3f} |")
    lines += ["", f"Read-out keys of the group tables: {sorted(scalar_items(next(iter(res['groups'].values()))['fd_as_prediction']))}", "",
              f"{res['seconds']} s."]
    out.with_suffix(".md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:4 + len(res["groups"])]))
    print(f"wrote {out.with_suffix('.json')} / .md in {res['seconds']} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
