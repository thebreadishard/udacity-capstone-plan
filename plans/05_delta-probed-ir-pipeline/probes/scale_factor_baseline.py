"""TASKS 112, reading 1 (pre-registration `GoalGathering/notes/PreRegistration_2026-10-25_Scale_Factor_Residuals.md`): what a scale factor
leaves per mode family on the proxy task (B3LYP/6-31G* → ωB97X/6-31G*), against the carried network on the same molecules and in the same
read-out.

A scale factor predicts the first-order shift of mode i as K_ii = (f − 1) ω_i. The factors are fitted once by least squares over every mode of
every pool molecule — one for all modes (S1), one per PAHdb region (S3) and one per family (SF) — and the prediction goes into `E6.readout` as
a diagonal matrix, so its `diag_rms` is computed by the code that reads the network. The network's numbers are the seed mean of the carried
model's evaluation records; the baselines are read on the molecules of those records.

    python probes/scale_factor_baseline.py [--molecules …/corpus/molecules] [--out …/out/scale_factor_baseline_2026-10-25]
"""
from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
M05 = PLAN / "modules" / "05_support_predictor"
sys.path.insert(0, str(M05 / "m05"))
import e6_learning_curve as E6  # noqa: E402  (module 05's code is not a package)
from chain41_read import family_rms  # noqa: E402  (the seed mean of the records' diag_rms per family)
from learning_curve_layerA import FAMILIES  # noqa: E402
from rungC_train import load_corpus  # noqa: E402

PAHDB_REGION_EDGES = (1111.0, 2500.0)   # cm⁻¹; Bauschlicher et al. 2018's regions as Mai et al. 2026 apply them (reading note of 25 Oct 2026)
CARRIED_RECORDS = tuple(M05 / "out" / f"E7_rungC_chain34_eval_analytic_2026-10-05_seed{s}.json" for s in range(3))   # decision 57
HOLDOUTS = ("a", "b")
OUT = M05 / "out" / "scale_factor_baseline_2026-10-25"

GroupOf = Callable[[dict], np.ndarray]


def one_group(m: dict) -> np.ndarray:
    """S1: every mode in group 0."""
    return np.zeros(len(m["freq"]), dtype=int)


def pahdb_region(m: dict) -> np.ndarray:
    """S3: 0 below 1111, 1 for 1111–2500 (both edges included), 2 above 2500 cm⁻¹ of the B3LYP harmonic frequency."""
    w = np.asarray(m["freq"], float)
    low, high = PAHDB_REGION_EDGES
    return np.where(w < low, 0, np.where(w > high, 2, 1))


def family_group(m: dict) -> np.ndarray:
    """SF: the index of the mode's family in FAMILIES."""
    return np.array([FAMILIES.index(f) for f in m["family"]])


BASELINES: dict[str, GroupOf] = {"S1": one_group, "S3": pahdb_region, "SF": family_group}


def fit_factors(mols: dict, ids: list[str], group_of: GroupOf) -> dict[int, float]:
    """Per group, the factor f minimising Σ ((f − 1) ω_i − K_ii)² over the modes of `ids`: f − 1 = Σ ω K / Σ ω²."""
    num: dict[int, float] = {}
    den: dict[int, float] = {}
    for i in ids:
        w = np.asarray(mols[i]["freq"], float)
        k = np.diag(mols[i]["K"]).astype(float)
        for g, wi, ki in zip(group_of(mols[i]), w, k, strict=True):
            num[int(g)] = num.get(int(g), 0.0) + wi * ki
            den[int(g)] = den.get(int(g), 0.0) + wi * wi
    return {g: 1.0 + num[g] / den[g] for g in sorted(num)}


def scaled_prediction(m: dict, factors: dict[int, float], group_of: GroupOf) -> np.ndarray:
    """The scale factor's first-order shifts as the diagonal matrix E6.readout reads."""
    w = np.asarray(m["freq"], float)
    f = np.array([factors[int(g)] for g in group_of(m)])
    return np.diag((f - 1.0) * w)


def baseline_diag_rms(mols: dict, ids: list[str], train: list[str], factors: dict[int, float], group_of: GroupOf) -> dict[str, float]:
    P = {i: scaled_prediction(mols[i], factors, group_of) for i in ids}
    return E6.readout(P, mols, ids, train)["diag_rms"]


def record_ids(records: list[dict], hold: str) -> list[str]:
    """The molecules a hold-out was read on; every seed's record must name the same ones."""
    sets = [list(r[hold]["per_molecule"]) for r in records]
    if any(sorted(s) != sorted(sets[0]) for s in sets):
        raise ValueError(f"hold-out ({hold}): the seed records read different molecules")
    return sets[0]


def line(name: str, net: dict[str, float], base: dict[str, float]) -> dict:
    """A registered line: the network below the baseline in every family."""
    below = {f: net[f] < base[f] for f in FAMILIES}
    return {"line": name, "pass": all(below.values()), "per_family": below}


def read(mols: dict, pool: list[str], current: dict[str, list[str]], records: list[dict]) -> dict:
    """Factors, the baselines' and the network's diag_rms per hold-out, the lines L1–L3."""
    factors = {name: fit_factors(mols, pool, g) for name, g in BASELINES.items()}
    out: dict = {"factors": {n: {str(g): f for g, f in fs.items()} for n, fs in factors.items()}, "pool_molecules": len(pool), "holdouts": {}}
    for h in HOLDOUTS:
        ids = record_ids(records, h)
        missing = [i for i in ids if i not in mols]
        if missing:
            raise ValueError(f"hold-out ({h}): {len(missing)} record molecules the loader no longer admits, e.g. {missing[:3]}")
        net = family_rms(records, h)
        base = {n: baseline_diag_rms(mols, ids, pool, factors[n], g) for n, g in BASELINES.items()}
        out["holdouts"][h] = {"ids": ids, "same_as_loader": sorted(ids) == sorted(current[h]), "network": net, **base,
                              "share_removed_vs_S3": {f: 1.0 - net[f] / base["S3"][f] for f in FAMILIES}}
    hs = out["holdouts"]
    out["lines"] = [line("L1: (a) network < S3 in every family", hs["a"]["network"], hs["a"]["S3"]),
                    line("L2: (a) network < SF in every family", hs["a"]["network"], hs["a"]["SF"]),
                    line("L3: (b) network < S3 in every family", hs["b"]["network"], hs["b"]["S3"])]
    return out


def line_text(x: dict) -> str:
    verdicts = ", ".join(f"{f} {'yes' if ok else 'no'}" for f, ok in x["per_family"].items())
    return f"- {x['line']}: **{'PASS' if x['pass'] else 'FAIL'}** ({verdicts})"


def loader_text(res: dict) -> str:
    parts = [f"({h}) {'yes' if r['same_as_loader'] else 'no, read on the records ids'}" for h, r in res["holdouts"].items()]
    return "Record molecules equal to the current loader's hold-out: " + ", ".join(parts)


def report(res: dict) -> list[str]:
    head = "| hold-out | read | " + " | ".join(FAMILIES) + " |"
    lines = ["# What a scale factor leaves per family on the proxy task (TASKS 112, reading 1)", "",
             "Pre-registration: `GoalGathering/notes/PreRegistration_2026-10-25_Scale_Factor_Residuals.md`. Quantity: `diag_rms`, the rms error of "
             "the first-order frequency shift B3LYP/6-31G* → ωB97X/6-31G* per mode family (cm⁻¹), read by `E6.readout`. Factors fitted by least "
             f"squares on all {res['pool_molecules']} pool molecules; network = carried chain 34 (v1.1), seed mean of its three analytic records.", "",
             "Fitted factors: " + "; ".join(f"{n} {', '.join(f'{f:.4f}' for f in fs.values())}" for n, fs in res["factors"].items())
             + f" (S3 regions: below {PAHDB_REGION_EDGES[0]:.0f}, {PAHDB_REGION_EDGES[0]:.0f}–{PAHDB_REGION_EDGES[1]:.0f}, above "
             f"{PAHDB_REGION_EDGES[1]:.0f} cm⁻¹; SF in the order {', '.join(FAMILIES)}).", "", head, "|---|---|" + "---|" * len(FAMILIES)]
    for h, r in res["holdouts"].items():
        for name in ("S1", "S3", "SF", "network"):
            lines.append(f"| ({h}), {len(r['ids'])} molecules | {name} | " + " | ".join(f"{r[name][f]:.2f}" for f in FAMILIES) + " |")
        shares = " | ".join(f"{100 * r['share_removed_vs_S3'][f]:.0f} %" for f in FAMILIES)
        lines.append(f"| ({h}) | share of S3's residual the network removes | {shares} |")
    lines += ["", "Registered lines:", "", *(line_text(x) for x in res["lines"]), "", loader_text(res), "",
              "This is the proxy task at one basis. A scale factor's real use, B3LYP → experimental fundamentals with the anharmonicity folded "
              "in, is reading 3 (`probes/fundamentals_vs_experiment.py`)."]
    return lines


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--molecules", type=Path, default=M05 / "corpus" / "molecules")
    ap.add_argument("--out", type=Path, default=OUT, help="output prefix: <out>.json and <out>.md")
    a = ap.parse_args(argv)
    records = [json.loads(p.read_text(encoding="utf-8")) for p in CARRIED_RECORDS]
    mols, test_a, test_b, _, pool, _ = load_corpus(str(a.molecules), use_analytic=True)
    res = read(mols, pool, {"a": test_a, "b": test_b}, records)
    lines = report(res)
    for path, text in ((a.out.with_suffix(".json"), json.dumps(res, indent=1)), (a.out.with_suffix(".md"), "\n".join(lines) + "\n")):
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(text, encoding="utf-8")
        tmp.replace(path)
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
