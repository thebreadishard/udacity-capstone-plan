"""The carried head's floor (TASKS 65; GoalGathering/notes/PreRegistration_2026-10-15_Hybrid_Form_Floor.md).

The carried recipe's head (`m05/rungC_hybrid.py`, `--head hybrid --pattern f`) writes a correction ΔF between internal primitives only on
pattern f, and ΔH = Bᵀ ΔF B. The read-out's matrix K (mode basis, cm⁻¹) is linear in ΔF, K = scale ∘ (C ΔF Cᵀ) (`e7_t2_posthoc.kmap`), so two
quantities are exact per molecule:
  form    the least-squares best ΔF on the pattern for the whole of K (upper triangle, equal weight): no network of this form reads better
  target  the read-out of the target the recipe trains (the projected truth masked to the pattern)
Each molecule is loaded as the trainer holds an analytic one (T2.load's fields with e7_rungB_reread_analytic.substitute's Hessians).

    python probes/hybrid_form_floor.py --inputs probes/results_m1/arch_floor_2026-10-15/inputs.tsv --out <prefix>

The inputs are architecture_floor's frozen list (sha256 checked); the read writes <prefix>.json and <prefix>.md.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "m05"))
sys.path.insert(0, str(PLAN / "probes"))
import architecture_floor as AF  # noqa: E402  (the frozen inputs and the mode-basis formula)
import e7_rungB_pairs as RB  # noqa: E402
import e7_t2_posthoc as PH  # noqa: E402
import e7_t2_sqm as T2  # noqa: E402
import floor_lines as FL  # noqa: E402
import learning_curve_layerA as LA  # noqa: E402
import rungC_targets as RT  # noqa: E402

PATTERN = "f"                                             # chain_runner.RECIPE_V11's --pattern; tests/test_hybrid_form_floor.py keeps them equal
QUANTITIES = ("form", "target")
KEYS = (*FL.FAMILIES, "ring_coupling")
LINE_1 = {"family": 1.0, "ring_coupling": 0.10}           # cm⁻¹ per family; the ring-coupling ratio
LINE_2 = {"family": 1.25, "ring_coupling": 0.15}
PROGRESS_EVERY = 25                                       # molecules between progress lines


# ---------------------------------------------------------------- one molecule

def analytic_molecule(folder: Path) -> dict:
    """The fields the read needs, built as T2.load builds them and with the analytic Hessians as e7_rungB_reread_analytic.substitute sets them."""
    g = json.loads((folder / "geometry.json").read_text(encoding="utf-8"))
    symbols, coords, masses = g["symbols"], np.asarray(g["coords_bohr"], dtype=float), np.asarray(g["masses_amu"], dtype=float)
    lo, hi = (np.load(folder / f"hessian_{lvl}_analytic.npz")["H_projected"] for lvl in ("b3lyp", "wb97x"))
    w, _, V, _ = LA.normal_modes(lo, masses)
    B, _types = T2.internals(symbols, coords)
    F_low, _ = T2.to_internal(lo, B)
    dH = hi - lo
    return {"id": folder.name, "symbols": symbols, "coords": coords, "masses": masses, "w": w, "V": V, "B": B, "F_low": F_low, "dH_true": dH,
            "K": AF.mode_correction(dH, masses, w, V), "family": list(LA.molecule_features(folder, lo, hi)["family"])}


def pattern_pairs(m: dict) -> np.ndarray:
    """(P, 2) the pattern's primitive pairs, p ≤ q, each once. The pattern builder's B must be the loader's (as rungC_train.pattern_classes)."""
    pairs, _feat, _cls, B = RB.molecule_pairs(m["symbols"], m["coords"], np.asarray(m["F_low"], dtype=float), pattern=PATTERN)
    if B.shape != m["B"].shape or not np.allclose(B, m["B"], atol=1e-8):
        raise ValueError(f"{m['id']}: the pattern builder's primitives differ from the loader's B matrix")
    return np.unique(np.sort(np.asarray(pairs), axis=1), axis=0)


def on_pattern(values: np.ndarray, pairs: np.ndarray, n: int) -> np.ndarray:
    """The symmetric n × n ΔF with `values` on the pattern pairs and zero elsewhere."""
    dF = np.zeros((n, n))
    dF[pairs[:, 0], pairs[:, 1]] = values
    dF[pairs[:, 1], pairs[:, 0]] = values
    return dF


def best_form_fit(m: dict, pairs: np.ndarray) -> np.ndarray:
    """The ΔF on the pattern whose K is closest to the true K over the whole upper triangle (least squares, minimum norm, rcond PINV_RCOND).
    Column of pair (p, q): scale ∘ (c_p c_qᵀ + c_q c_pᵀ) on the upper triangle, halved on the diagonal pairs (p = q) where both terms coincide."""
    C, scale = PH.kmap(m)
    i, j = np.triu_indices(C.shape[0])
    p, q = pairs[:, 0], pairs[:, 1]
    A = scale[i, j][:, None] * (C[i][:, p] * C[j][:, q] + C[j][:, p] * C[i][:, q]) * np.where(p == q, 0.5, 1.0)[None, :]
    x, *_ = np.linalg.lstsq(A, m["K"][i, j], rcond=RT.PINV_RCOND)
    return on_pattern(x, pairs, C.shape[1])


def target_on_pattern(m: dict, pairs: np.ndarray) -> np.ndarray:
    """The recipe's training target: the projected truth B⁺ᵀ ΔH B⁺ kept on the pattern."""
    T = RT.projected_target(m["dH_true"], m["B"])
    return on_pattern(T[pairs[:, 0], pairs[:, 1]], pairs, T.shape[0])


def molecule_record(folder: Path) -> dict:
    m = analytic_molecule(folder)
    pairs = pattern_pairs(m)
    fits = {"form": best_form_fit(m, pairs), "target": target_on_pattern(m, pairs)}
    return {"id": m["id"], "n_atoms": len(m["masses"]), "n_modes": int(m["K"].shape[0]), "n_pattern_pairs": int(len(pairs)),
            **{name: FL.error_sums(m["K"], PH.k_of(m, dF), m["family"]) for name, dF in fits.items()}}


# ---------------------------------------------------------------- the registered read

def _kind(key: str) -> str:
    return "ring_coupling" if key == "ring_coupling" else "family"


def read(records: list[dict]) -> dict:
    bound = FL.line_1_bound([r["n_atoms"] for r in records])
    upper = [r for r in records if r["n_atoms"] >= bound]
    rng = np.random.default_rng(FL.BOOTSTRAP_SEED)
    out = {}
    for qty in QUANTITIES:
        out[qty] = {}
        for key in KEYS:
            now = FL.pooled([r[qty] for r in upper], key)
            pts = [(r["n_atoms"], v) for r in records if (v := FL.per_molecule(r[qty], key)) is not None]
            at60, interval, n_fit = FL.forecast(pts, rng)
            out[qty][key] = {"line_1": now, "line_1_met": bool(now >= LINE_1[_kind(key)]), "line_2_at_60": at60, "line_2_interval": interval,
                             "line_2_met": bool(at60 >= LINE_2[_kind(key)]), "n_fit": n_fit}
    met = {qty: [k for k, x in out[qty].items() if x["line_1_met"] or x["line_2_met"]] for qty in QUANTITIES}
    if met["form"]:
        verdict = f"the form costs ({', '.join(met['form'])}): a wider pattern is registered as a training comparison"
    elif met["target"]:
        verdict = f"the form holds it but the trained target does not ({', '.join(met['target'])}): a target comparison is registered"
    else:
        verdict = "neither line met: pattern f and its target are not the limit at these sizes; the size penalty is a learning and data question"
    return {"verdict": verdict, "quantities": out, "line_1_bound_atoms": bound, "n_upper": len(upper), "n_molecules": len(records)}


def _cell(x: dict, line: str) -> str:
    value = x[line] if line == "line_1" else x["line_2_at_60"]
    return f"{value:.3f}{' MET' if x[f'{line}_met'] else ''}"


def report(res: dict) -> list[str]:
    lines = ["# The carried head's floor (TASKS 65, registered read)", "", f"**{res['verdict']}**", "",
             f"{res['n_molecules']} molecules; line 1 on the {res['n_upper']} of ≥ {res['line_1_bound_atoms']} atoms. Families in cm⁻¹ "
             "(lines 1.0 / 1.25); ring couplings as the ratio (lines 0.10 / 0.15).", "",
             "| quantity | read-out | line 1 | line 2 at 60 atoms | 95 % interval | molecules fitted |", "|---|---|---|---|---|---|"]
    for qty, block in res["quantities"].items():
        for key, x in block.items():
            span = f"{x['line_2_interval'][0]:.3f}–{x['line_2_interval'][1]:.3f}" if x["line_2_interval"] else "no fit"
            lines.append(f"| {qty} | {key} | {_cell(x, 'line_1')} | {_cell(x, 'line_2')} | {span} | {x['n_fit']} |")
    return lines


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--inputs", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    folders = AF.frozen_folders(a.inputs)
    records = []
    for n, d in enumerate(folders, 1):
        records.append(molecule_record(d))
        if n % PROGRESS_EVERY == 0 or n == len(folders):
            print(f"  progress {n}/{len(folders)} molecules", flush=True)       # the run spec's progress line
    res = read(records)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    Path(f"{a.out}.json").write_text(json.dumps({**res, "records": records}, indent=1, ensure_ascii=False), encoding="utf-8")
    lines = report(res)
    Path(f"{a.out}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
