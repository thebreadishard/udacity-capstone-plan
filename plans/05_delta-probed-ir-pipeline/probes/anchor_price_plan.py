"""The anchor price (TASKS 82 and TASKS 84 step 4; TASKS 140, claim 3): the proxy check's arm (a) again with the change of correction the
anchors measured, and a covering selection of fine-tune molecules against random draws of the same size.

Arm (a) of the proxy check (21 Oct 2026) distorted each family's block by one factor for every molecule. On the anchors the CC correction
differs from the proxy mainly by its mean shift, and for CH-oop that mean shift follows the ring context — ≈ 0 on single rings, about half
the proxy's with the opposite sign on fused rings, about the proxy's with a five-membered ring (27 Oct 2026, nine anchors) — while every
other family's ratio is nearly uniform. Arm (c) trains a base on that change (`rungC_train.py --distortion-file`: per family one factor on
the mean first-order shift and one on the rest, CH-oop's mean factor per context) and fine-tunes it on k molecules with the true label:
random draws (the count of anchors per accuracy) and covering selections (does choosing molecules by their cells need fewer?). Same
reservoir, read set, exclusions, recipe and seeds as the proxy check, so arm (a)'s curve is the comparison. Registration:
`GoalGathering/notes/PreRegistration_2026-10-27_Anchor_Price_Arm_C.md`.

    python probes/anchor_price_plan.py distortion <out_dir>   # <out_dir>/distortion.json + factors.md (decompose.json, the manifest)
    python probes/anchor_price_plan.py cover <out_dir>        # <out_dir>/cover_k<k>_d<d>.txt + cover.json (the proxy check's reservoir)
    python probes/anchor_price_plan.py plan <out_dir>         # probes/runs/anchor_price.json
    python probes/anchor_price_plan.py register <out_dir>     # chain step: the three base models into the registry as candidates
    python probes/anchor_price_plan.py read <out_dir>         # <out_dir>/anchor_price_read.{json,md}
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import statistics
import subprocess
import sys
from collections import Counter
from collections.abc import Callable
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import proxy_check_plan as PC  # noqa: E402  (after the sys.path insert)

M05, RUNS = PC.M05, PC.RUNS
PX_DIR = M05 / "out" / "proxy_check_2026-10-21"
FAMILIES = PC.FAMILIES
CONTEXT_FAMILIES = ("CH-oop",)          # the family whose mean ratio follows the ring context on the anchors; the others are uniform
UNIFORM_FAMILIES = ("CH-stretch",)      # its centred proxy shifts are noise (centred rms 0.2–1.7 cm⁻¹): one factor, the mean ratio, on both parts
RANDOM_SIZES = (5, 10, 20, 50, 100, 200)
COVER_SIZES = (5, 10, 20)               # the reservoir holds 89 fused, 67 single, 44 five-ring molecules: draws of 50 hold all three
COVER_DRAWS = 3
COVER_SEED = 20261027
DRAWS = 3
LINE_CM = 3.0                           # decision 53's line, every family
C1_NEEDED = 2                           # the cover is below random at two of the three cover sizes


# ------------------------------------------------------------------------------------------------------------------------- distortion
def anchor_contexts(decompose: dict, smiles_of: dict[str, str], context_of: Callable[[str], str]) -> dict[str, str]:
    """Anchor name → its context, from the anchor's corpus id in decompose.json."""
    return {name: context_of(smiles_of[v["id"]]) for name, v in decompose.items()}


def family_factors(decompose: dict, contexts: dict[str, str]) -> dict[str, dict]:
    """Per family the two factors from the anchors' 'total' (the TZ composite): the mean factor = the median over anchors of the CC mean
    shift over the proxy's (per context for CONTEXT_FAMILIES), the rest factor = the median centred slope (for UNIFORM_FAMILIES the mean
    factor again). Only anchors with more than one mode in the family count, as in the proxy check."""
    out: dict[str, dict] = {}
    for fam in FAMILIES:
        rows = [(contexts[name], v[fam]["total"]["mean"] / v[fam]["proxy mean"], v[fam]["total"]["centred_slope"])
                for name, v in decompose.items() if fam in v and v[fam]["n"] > 1]
        if not rows:
            raise SystemExit(f"no anchor with {fam} modes")
        if fam in CONTEXT_FAMILIES:
            mean: float | dict[str, float] = {c: round(statistics.median(r[1] for r in rows if r[0] == c), 2) for c in sorted({r[0] for r in rows})}
        else:
            mean = round(statistics.median(r[1] for r in rows), 2)
        rest = mean if fam in UNIFORM_FAMILIES else round(statistics.median(r[2] for r in rows), 2)
        out[fam] = {"mean": mean, "rest": rest}
    return out


def manifest_smiles() -> dict[str, str]:
    with (M05 / "corpus" / "manifest.csv").open(encoding="utf-8") as f:
        return {r["id"]: r["smiles"] for r in csv.DictReader(f) if r["smiles"]}


def smiles_context(smiles: str) -> str:
    import anchor_plan as AP
    from rdkit import Chem
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise SystemExit(f"unreadable SMILES {smiles!r}")
    return AP.fusion_context(mol)


def distortion(out_dir: Path) -> dict:
    decompose = json.loads(PC.DECOMPOSE.read_text(encoding="utf-8"))
    smiles = manifest_smiles()
    contexts = anchor_contexts(decompose, smiles, smiles_context)
    factors = family_factors(decompose, contexts)
    used = {c for f in factors.values() for part in f.values() if isinstance(part, dict) for c in part}
    mol_contexts = {i: smiles_context(s) for i, s in smiles.items()}
    if unknown := sorted(set(mol_contexts.values()) - used):
        raise SystemExit(f"corpus contexts {unknown} have no anchor, so no CH-oop factor")
    body = {"about": f"anchor price arm (c): factors from {PC.DECOMPOSE.name} (anchors: {contexts}); probes/anchor_price_plan.py",
            "families": factors, "contexts": mol_contexts}
    out_dir.mkdir(parents=True, exist_ok=True)
    PC.write_text(out_dir / "distortion.json", json.dumps(body, indent=1))
    PC.write_text(out_dir / "factors.md", "\n".join(factor_lines(factors, contexts, Counter(mol_contexts.values()))) + "\n")
    return {"families": factors, "anchors": contexts, "corpus_contexts": dict(Counter(mol_contexts.values()))}


def factor_lines(factors: dict, contexts: dict[str, str], counts: Counter) -> list[str]:
    lines = ["# Anchor price arm (c) — the distortion's factors", "", f"Anchors and contexts: {contexts}. Corpus molecules per context: "
             f"{dict(counts)}.", "", "| family | mean factor | rest factor |", "|---|---|---|"]
    return lines + [f"| {fam} | {f['mean']} | {f['rest']} |" for fam, f in factors.items()]


# ------------------------------------------------------------------------------------------------------------------------------ cover
def balanced_cover(cells_of: dict[str, set], k: int, rng: np.random.Generator) -> list[str]:
    """k molecules chosen one at a time by the most weight on their cells, a cell weighing 1 / (1 + molecules already holding it) — every
    cell first, then a second molecule per cell, and so on; ties go to the earlier place in a random order (the draw). Molecules without
    cells are taken only when nothing else is left."""
    order = {i: r for r, i in enumerate(rng.permutation(sorted(cells_of)))}
    held: Counter = Counter()
    left, chosen = set(cells_of), []
    for _ in range(k):
        best = max(left, key=lambda i: (sum(1.0 / (1 + held[c]) for c in cells_of[i]), -order[i]))
        chosen.append(best)
        held.update(cells_of[best])
        left.discard(best)
    return sorted(chosen)


def cover(out_dir: Path) -> dict:
    import anchor_plan as AP
    sys.path.insert(0, str(M05 / "m05"))
    from proxy_transfer_check import SUBSET_SEED, draw_subsets
    reservoir = (PX_DIR / "a_reservoir.txt").read_text(encoding="utf-8").split()
    rows = AP.corpus_cells()
    cells_of = {i: {tuple(c) for c in rows[i]["cells"]} if i in rows else set() for i in reservoir}
    out_dir.mkdir(parents=True, exist_ok=True)
    summary: dict = {}
    for k in COVER_SIZES:
        covers = [balanced_cover(cells_of, k, np.random.default_rng(COVER_SEED + d)) for d in range(COVER_DRAWS)]
        for d, ids in enumerate(covers):
            PC.write_text(out_dir / f"cover_k{k}_d{d}.txt", "\n".join(ids) + "\n")
        randoms = draw_subsets(reservoir, k, DRAWS, SUBSET_SEED)
        summary[k] = {"cells_cover": [len(set().union(*(cells_of[i] for i in ids))) for ids in covers],
                      "cells_random": [len(set().union(*(cells_of[i] for i in ids))) for ids in randoms]}
    summary["cells_reservoir"] = len(set().union(*cells_of.values()))
    PC.write_text(out_dir / "cover.json", json.dumps(summary, indent=1))
    return summary


# ------------------------------------------------------------------------------------------------------------------------------- plan
def base_model(out_rel: str, n: int, seed: int) -> str:
    return f"{out_rel}/base_c_model_n{n}_seed{seed}.pt"


def steps(out_rel: str, n_pool: int, flags: list[str]) -> list[dict]:
    """The chain: base (c), the registry entries, the random fine-tunes (head_all; scratch is base-free and the proxy check read it on the
    same draws), then the covering selections (head_all and scratch)."""
    def step(label: str, argv: list[str]) -> dict:
        return {"kind": "cmd", "label": label, "cwd": "modules/05_support_predictor", "log": f"modules/05_support_predictor/{out_rel}/{label}.log",
                "argv": argv}

    px_rel = Path(os.path.relpath(PX_DIR, M05)).as_posix()

    def fine_tune(label: str, seed: int, reservoir: str, k: int, subsets: int, modes: str) -> dict:
        return step(label, ["{python}", "m05/proxy_transfer_check.py", "corpus/molecules", base_model(out_rel, n_pool, seed), f"{out_rel}/{label}",
                            "--reservoir", reservoir, "--read", f"{px_rel}/a_read.txt", "--k", str(k), "--subsets", str(subsets),
                            "--modes", modes, "--threads", PC.THREADS, "--allow-any-model"])

    out = [step("base_c", ["{python}", "m05/rungC_train.py", "corpus/molecules", f"{out_rel}/base_c", *flags,
                           "--exclude-ids-file", f"{px_rel}/a_exclude.txt", "--distortion-file", f"{out_rel}/distortion.json"]),
           step("register", ["{python}", "../../probes/anchor_price_plan.py", "register", out_rel])]
    out += [fine_tune(f"ft_c_k{k}_seed{s}", s, f"{px_rel}/a_reservoir.txt", k, 1 if k == PC.ARMS["a"].reservoir else DRAWS, "head_all")
            for s in PC.SEEDS for k in RANDOM_SIZES]
    out += [fine_tune(f"cv_c_k{k}_d{d}_seed{s}", s, f"{out_rel}/cover_k{k}_d{d}.txt", k, 1, "head_all,scratch")
            for s in PC.SEEDS for k in COVER_SIZES for d in range(COVER_DRAWS)]
    return out


def plan(out_dir: Path) -> Path:
    for need in ("distortion.json", *(f"cover_k{k}_d{d}.txt" for k in COVER_SIZES for d in range(COVER_DRAWS))):
        if not (out_dir / need).exists():
            raise SystemExit(f"{out_dir / need}: run the distortion and cover actions first")
    out_rel = Path(os.path.relpath(out_dir, M05)).as_posix()
    n_pool = json.loads((PX_DIR / "manifest.json").read_text(encoding="utf-8"))["pool"]["a"]
    st = steps(out_rel, n_pool, PC.recipe_flags())
    spec = {"_about": "anchor price arm (c): probes/anchor_price_plan.py plan", "name": "AP", "steps": st,
            "outputs": [f"modules/05_support_predictor/{base_model(out_rel, n_pool, s)}" for s in PC.SEEDS]
            + [f"modules/05_support_predictor/{s['argv'][4]}.json" for s in st if s["label"].startswith(("ft_", "cv_"))]}
    path = RUNS / "anchor_price.json"
    PC.write_text(path, json.dumps(spec, indent=1))
    return path


def register(out_rel: str) -> int:
    n_pool = json.loads((PX_DIR / "manifest.json").read_text(encoding="utf-8"))["pool"]["a"]
    note = ("anchor price arm (c): base on the anchors' measured change of correction - for probes/anchor_price_plan.py only, never a "
            "production model (GoalGathering/notes/PreRegistration_2026-10-27_Anchor_Price_Arm_C.md)")
    return subprocess.run([sys.executable, "m05/model_registry.py", "--add-candidates", *(base_model(out_rel, n_pool, s) for s in PC.SEEDS),
                           "--chain", "AP", "--note", note], cwd=M05, check=False).returncode


# ------------------------------------------------------------------------------------------------------------------------------- read
def family_column(records: list[dict], mode: str) -> dict[str, tuple]:
    """Per family the mean ± se over every (seed, draw) read of one fine-tune mode."""
    return {fam: PC.mean_se(PC.values(records, mode, lambda r, f=fam: r["family_mean"][f])) for fam in FAMILIES}


def crossing(curve: dict[int, float], line: float = LINE_CM) -> float | None:
    """The smallest k at which the curve reaches the line, interpolated linearly in log k between the last k above and the first at or
    below it; the first k itself when it is already at or below; None when no k reaches it."""
    ks = sorted(curve)
    for j, k in enumerate(ks):
        if curve[k] <= line:
            if j == 0:
                return float(k)
            k0 = ks[j - 1]
            t = (curve[k0] - line) / (curve[k0] - curve[k])
            return float(np.exp(np.log(k0) + t * (np.log(k) - np.log(k0))))
    return None


def read_records(out_dir: Path, names: list[str]) -> list[dict]:
    paths = [out_dir / f"{n}.json" for n in names]
    if missing := [p.name for p in paths if not p.exists()]:
        raise SystemExit(f"missing records: {missing}")
    return [json.loads(p.read_text(encoding="utf-8")) for p in paths]


def assess(random_by_k: dict[int, list[dict]], cover_by_k: dict[int, list[dict]], arm_a_by_k: dict[int, list[dict]]) -> dict:
    """The registered lines: C1 (head_all on the covers below the random draws on CH-oop by SE_FACTOR combined se at C1_NEEDED of the
    cover sizes) and C2 (per family the k at the 3 cm⁻¹ line on arm (c)'s random curve, beside arm (a)'s from its own records)."""
    rand = {k: family_column(r, "head_all") for k, r in random_by_k.items()}
    arm_a = {k: family_column(r, "head_all") for k, r in arm_a_by_k.items()}
    cov = {k: {m: family_column(r, m) for m in ("head_all", "scratch")} for k, r in cover_by_k.items()}
    c1_at = [k for k in COVER_SIZES if PC.lower(cov[k]["head_all"]["CH-oop"], rand[k]["CH-oop"])]
    c2 = {arm: {fam: crossing({k: c[k][fam][0] for k in c}) for fam in FAMILIES} for arm, c in (("arm_c", rand), ("arm_a", arm_a))}
    return {"random": rand, "arm_a": arm_a, "cover": cov, "C1": {"holds": len(c1_at) >= C1_NEEDED, "at": c1_at}, "C2": c2}


def read(out_dir: Path) -> dict:
    random_by_k = {k: read_records(out_dir, [f"ft_c_k{k}_seed{s}" for s in PC.SEEDS]) for k in RANDOM_SIZES}
    cover_by_k = {k: read_records(out_dir, [f"cv_c_k{k}_d{d}_seed{s}" for s in PC.SEEDS for d in range(COVER_DRAWS)]) for k in COVER_SIZES}
    arm_a_by_k = {k: read_records(PX_DIR, [f"ft_a_k{k}_seed{s}" for s in PC.SEEDS]) for k in RANDOM_SIZES}
    res = assess(random_by_k, cover_by_k, arm_a_by_k)
    PC.write_text(out_dir / "anchor_price_read.json", json.dumps(res, indent=1, default=str))
    PC.write_text(out_dir / "anchor_price_read.md", "\n".join(report_lines(res)) + "\n")
    return res


def report_lines(res: dict) -> list[str]:
    def cell(x: tuple) -> str:
        return f"{x[0]:.2f} ± {x[1]:.2f}"

    c2 = res["C2"]
    lines = ["# Anchor price, arm (c) — read", "",
             f"**C1** (covering selections below random draws on CH-oop, whole head, at {C1_NEEDED} of k = {list(COVER_SIZES)}): "
             f"{'holds' if res['C1']['holds'] else 'does not hold'} (at {res['C1']['at']}).",
             f"**C2** (k at {LINE_CM} cm⁻¹ on the random curve), arm (c): " + ", ".join(f"{f} {v if v is None else round(v)}" for f, v in c2["arm_c"].items())
             + "; arm (a): " + ", ".join(f"{f} {v if v is None else round(v)}" for f, v in c2["arm_a"].items()) + ".", "",
             "| k | draws | " + " | ".join(FAMILIES) + " |", "|---|---|" + "---|" * len(FAMILIES)]
    lines += [f"| {k} | random, whole head | " + " | ".join(cell(c[f]) for f in FAMILIES) + " |" for k, c in res["random"].items()]
    lines += [f"| {k} | arm (a), whole head | " + " | ".join(cell(c[f]) for f in FAMILIES) + " |" for k, c in res["arm_a"].items()]
    for k, c in res["cover"].items():
        lines += [f"| {k} | cover, {m} | " + " | ".join(cell(c[m][f]) for f in FAMILIES) + " |" for m in ("head_all", "scratch")]
    return lines


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("action", choices=["distortion", "cover", "plan", "register", "read"])
    ap.add_argument("out_dir")
    a = ap.parse_args()
    if a.action == "register":
        return register(a.out_dir)
    out_dir = Path(a.out_dir).resolve()
    actions: dict[str, Callable[[Path], object]] = {"distortion": distortion, "cover": cover, "plan": plan}
    if a.action in actions:
        print(json.dumps(actions[a.action](out_dir), indent=1, default=str))
    else:
        print("\n".join(report_lines(read(out_dir))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
