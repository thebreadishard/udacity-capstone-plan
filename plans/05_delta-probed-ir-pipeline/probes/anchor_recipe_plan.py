"""The anchor price's recipe follow-up (TASKS 82; the user, 28 Oct 2026): is arm (c)'s 'CH-oop not at 3 cm⁻¹ by 200' the anchor count or
the fine-tune recipe? Registration: `GoalGathering/notes/PreRegistration_2026-10-28_Anchor_Price_Recipe.md`.

Arm (c) under-fitted: its whole-head fine-tunes ended at about twice arm (a)'s training loss at every k, and its CH-stretch control
failed. Two arms, three recipes, on the proxy check's reservoir and read set:

- arm (c): arm (c)'s base as it is (`out/anchor_price_2026-10-28/base_c_*`); arm (a2): arm (a)'s distortion (one factor per family) on
  a base trained now, so that both bases learned from the same 862 analytic labels and the distortion is the only difference;
- R0 = 'head_all' (3000 steps, arm (c)'s recipe; for arm (c) its own records are read again), R1 = 'head_all_es' (the whole head, up to
  ES_MAX_EPOCHS epochs on 85 % of the k molecules, stopped by the loss on the rest, decision 51), R2 = 'body1_es' (R1 with the body's
  last interaction block free);
- k = 100 (three draws) and 200 (the whole reservoir), arm (c)'s draws; three seeds.

    python probes/anchor_recipe_plan.py plan <out_dir>       # the chain file probes/runs/anchor_recipe.json
    python probes/anchor_recipe_plan.py register <out_dir>   # base (a2) as registry candidates (a chain step)
    python probes/anchor_recipe_plan.py read <out_dir>       # the registered lines → anchor_recipe_read.json/.md
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import anchor_price_plan as AP
import proxy_check_plan as PC

M05, RUNS, PX_DIR = PC.M05, PC.RUNS, AP.PX_DIR
AP_DIR = M05 / "out" / "anchor_price_2026-10-28"
FAMILIES = PC.FAMILIES
SIZES = (100, 200)
RECIPES = {"R0": "head_all", "R1": "head_all_es", "R2": "body1_es"}
ES_MAX_EPOCHS = 60                 # four times the 15 epochs R0 gives k = 200; the cap binds when the best epoch is within 10 % of it
CAP_SHARE = 1 / 3                  # decision 51: a recipe whose best epoch sits at the cap in more than a third of its runs is still learning
FIT_RATIO = 1.5                    # line F: arm (c)'s training loss within this factor of arm (a2)'s
LINE_CM = AP.LINE_CM


# ------------------------------------------------------------------------------------------------------------------------------- plan
def base_a2_model(out_rel: str, n: int, seed: int) -> str:
    return f"{out_rel}/base_a2_model_n{n}_seed{seed}.pt"


def draws_for(k: int) -> int:
    return 1 if k == PC.ARMS["a"].reservoir else AP.DRAWS


def step(out_rel: str, label: str, argv: list[str]) -> dict:
    """One chain step, run from module 05, its log beside its outputs."""
    return {"kind": "cmd", "label": label, "cwd": "modules/05_support_predictor", "log": f"modules/05_support_predictor/{out_rel}/{label}.log",
            "argv": argv}


def fine_tune_step(out_rel: str, label: str, model: str, k: int, modes: list[str], max_epochs: int = ES_MAX_EPOCHS) -> dict:
    """One `proxy_transfer_check.py` run of `model` on the proxy check's reservoir and read set; `max_epochs` caps the early-stopped modes."""
    px_rel = Path(os.path.relpath(PX_DIR, M05)).as_posix()
    return step(out_rel, label, ["{python}", "m05/proxy_transfer_check.py", "corpus/molecules", model, f"{out_rel}/{label}",
                                 "--reservoir", f"{px_rel}/a_reservoir.txt", "--read", f"{px_rel}/a_read.txt", "--k", str(k),
                                 "--subsets", str(draws_for(k)), "--modes", ",".join(modes), "--es-max-epochs", str(max_epochs),
                                 "--threads", PC.THREADS, "--allow-any-model"])


def steps(out_rel: str, n_pool: int, flags: list[str], slopes: dict[str, float]) -> list[dict]:
    """The chain: base (a2), its registry entries, arm (c)'s R1/R2 fine-tunes, then arm (a2)'s R0/R1/R2 — each seed along k."""
    px_rel = Path(os.path.relpath(PX_DIR, M05)).as_posix()
    ap_rel = Path(os.path.relpath(AP_DIR, M05)).as_posix()
    out = [step(out_rel, "base_a2", ["{python}", "m05/rungC_train.py", "corpus/molecules", f"{out_rel}/base_a2", *flags,
                                     *PC.base_extra("a", px_rel, slopes)]),
           step(out_rel, "register", ["{python}", "../../probes/anchor_recipe_plan.py", "register", out_rel])]
    out += [fine_tune_step(out_rel, f"rc_k{k}_seed{s}", AP.base_model(ap_rel, n_pool, s), k, [RECIPES["R1"], RECIPES["R2"]])
            for s in PC.SEEDS for k in SIZES]
    out += [fine_tune_step(out_rel, f"ra2_k{k}_seed{s}", base_a2_model(out_rel, n_pool, s), k, list(RECIPES.values()))
            for s in PC.SEEDS for k in SIZES]
    return out


def plan(out_dir: Path) -> Path:
    manifest = proxy_manifest()
    n_pool = manifest["pool"]["a"]
    needed = [AP_DIR / f"base_c_model_n{n_pool}_seed{s}.pt" for s in PC.SEEDS] + [AP_DIR / f"ft_c_k{k}_seed{s}.json" for k in SIZES
                                                                                    for s in PC.SEEDS]
    if missing := [p.name for p in needed if not p.exists()]:
        raise SystemExit(f"arm (c)'s base and R0 records are read by this follow-up; missing in {AP_DIR}: {missing}")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_rel = Path(os.path.relpath(out_dir, M05)).as_posix()
    st = steps(out_rel, n_pool, PC.recipe_flags(), manifest["slopes"])
    spec = {"_about": "anchor price recipe follow-up: probes/anchor_recipe_plan.py plan", "name": "AR", "steps": st,
            "outputs": [f"modules/05_support_predictor/{base_a2_model(out_rel, n_pool, s)}" for s in PC.SEEDS]
            + [f"modules/05_support_predictor/{s['argv'][4]}.json" for s in st if s["label"].startswith(("rc_", "ra2_"))]}
    path = RUNS / "anchor_recipe.json"
    PC.write_text(path, json.dumps(spec, indent=1))
    return path


def proxy_manifest() -> dict:
    """The proxy check's manifest: arm (a)'s pool size and the slopes its family scales were made from (arm (a2) takes the same)."""
    return json.loads((PX_DIR / "manifest.json").read_text(encoding="utf-8"))


def register(out_rel: str) -> int:
    note = ("anchor price recipe follow-up: base (a2), arm (a)'s distortion on the 862 analytic labels - for probes/anchor_recipe_plan.py "
            "only, never a production model (GoalGathering/notes/PreRegistration_2026-10-28_Anchor_Price_Recipe.md)")
    return subprocess.run([sys.executable, "m05/model_registry.py", "--add-candidates",
                           *(base_a2_model(out_rel, proxy_manifest()["pool"]["a"], s) for s in PC.SEEDS), "--chain", "AR", "--note", note],
                          cwd=M05, check=False).returncode


# ------------------------------------------------------------------------------------------------------------------------------- read
def entries(records: list[dict], mode: str) -> list[dict]:
    """One entry per (seed, draw) of a mode."""
    return [d["modes"][mode] for r in records for d in r["draws"]]


def cell(records: list[dict], mode: str, max_epochs: int = ES_MAX_EPOCHS) -> dict:
    """Per family the mean ± se of the read, the training loss's mean ± se and, for an early-stopped mode, the share of runs whose kept
    epoch is within 10 % of the cap `max_epochs`."""
    es = entries(records, mode)
    out = {"family": AP.family_column(records, mode), "fit_loss": PC.mean_se([e["final_loss"] for e in es]), "n": len(es)}
    if "best_epoch" in es[0]:
        out["at_cap"] = float(np.mean([e["best_epoch"] >= 0.9 * max_epochs for e in es]))
        out["best_epoch"] = PC.mean_se([float(e["best_epoch"]) for e in es])
    return out


def table(rc: dict[int, list[dict]], rc0: dict[int, list[dict]], ra2: dict[int, list[dict]]) -> dict:
    """{arm: {recipe: {k: cell}}}: arm (c)'s R0 from arm (c)'s own records, its R1/R2 and all of arm (a2)'s from this follow-up."""
    c = {"R0": {k: cell(rc0[k], RECIPES["R0"]) for k in SIZES}}
    c |= {r: {k: cell(rc[k], RECIPES[r]) for k in SIZES} for r in ("R1", "R2")}
    a2 = {r: {k: cell(ra2[k], m) for k in SIZES} for r, m in RECIPES.items()}
    return {"c": c, "a2": a2}


def lines(t: dict) -> dict:
    """The registered lines per recipe: G (the CH-stretch control: arm (c) not above arm (a2) by 2 se at either k), F (arm (c)'s training
    loss within FIT_RATIO of arm (a2)'s at k = 200), the cap (decision 51), P (arm (c)'s CH-oop at 200: at or below the line; below
    R0's by 2 se); then the outcome."""
    per = {}
    for r in RECIPES:
        c, a2 = t["c"][r], t["a2"][r]
        g = all(not PC.lower(a2[k]["family"]["CH-stretch"], c[k]["family"]["CH-stretch"]) for k in SIZES)
        f = c[200]["fit_loss"][0] <= FIT_RATIO * a2[200]["fit_loss"][0]
        cap = any(c[k].get("at_cap", 0.0) > CAP_SHARE for k in SIZES)
        oop = c[200]["family"]["CH-oop"]
        per[r] = {"G": g, "F": f, "cap_binds": cap, "ch_oop_200": oop[:2], "at_line": oop[0] <= LINE_CM,
                  "below_R0": r != "R0" and PC.lower(oop, t["c"]["R0"][200]["family"]["CH-oop"])}
    return {"per_recipe": per, "outcome": outcome(per)}


def outcome(per: dict) -> str:
    """'no reading' when neither new recipe passes its control; else, over the new recipes that pass it: 'recipe-limited' (one is at the
    line and below R0), 'partly recipe' (one is below R0, none at the line), 'undecided: the cap binds' (none below R0 and the cap binds
    in one), 'data-limited' (none below R0, no cap)."""
    ok = {r: v for r, v in per.items() if r != "R0" and v["G"]}
    if not ok:
        return "no reading"
    if any(v["below_R0"] and v["at_line"] for v in ok.values()):
        return "recipe-limited"
    if any(v["below_R0"] for v in ok.values()):
        return "partly recipe"
    return "undecided: the cap binds" if any(v["cap_binds"] for v in ok.values()) else "data-limited"


def read(out_dir: Path) -> dict:
    rc = {k: AP.read_records(out_dir, [f"rc_k{k}_seed{s}" for s in PC.SEEDS]) for k in SIZES}
    rc0 = {k: AP.read_records(AP_DIR, [f"ft_c_k{k}_seed{s}" for s in PC.SEEDS]) for k in SIZES}
    ra2 = {k: AP.read_records(out_dir, [f"ra2_k{k}_seed{s}" for s in PC.SEEDS]) for k in SIZES}
    t = table(rc, rc0, ra2)
    res = {"table": t, **lines(t)}
    PC.write_text(out_dir / "anchor_recipe_read.json", json.dumps(res, indent=1, default=str))
    PC.write_text(out_dir / "anchor_recipe_read.md", "\n".join(report_lines(res)) + "\n")
    return res


def report_lines(res: dict) -> list[str]:
    def ms(x: tuple) -> str:
        return f"{x[0]:.2f} ± {x[1]:.2f}"

    out = ["# Anchor price, recipe follow-up — read", "", f"**Outcome: {res['outcome']}.**", "",
           "| recipe | G (CH-stretch control) | F (fit within ×1.5) | cap binds | CH-oop (c) at 200 | at 3 cm⁻¹ | below R0 |",
           "|---|---|---|---|---|---|---|"]
    out += [f"| {r} | {v['G']} | {v['F']} | {v['cap_binds']} | {ms(v['ch_oop_200'])} | {v['at_line']} | {v['below_R0']} |"
            for r, v in res["per_recipe"].items()]
    out += ["", "| arm | recipe | k | " + " | ".join(FAMILIES) + " | training loss | best epoch (at cap) |", "|---|---|---|" + "---|" * (len(FAMILIES) + 2)]
    for arm, by_r in res["table"].items():
        for r, by_k in by_r.items():
            for k, c in by_k.items():
                be = f"{ms(c['best_epoch'])} ({c['at_cap']:.0%})" if "best_epoch" in c else "–"
                out.append(f"| {arm} | {r} | {k} | " + " | ".join(ms(c["family"][f]) for f in FAMILIES)
                           + f" | {c['fit_loss'][0]:.4f} ± {c['fit_loss'][1]:.4f} | {be} |")
    return out


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")  # the report holds superscripts; a Windows console defaults to cp1252
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("action", choices=["plan", "register", "read"])
    ap.add_argument("out_dir")
    a = ap.parse_args()
    if a.action == "register":
        return register(a.out_dir)
    out_dir = Path(a.out_dir).resolve()
    if a.action == "plan":
        print(plan(out_dir))
    else:
        print("\n".join(report_lines(read(out_dir))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
