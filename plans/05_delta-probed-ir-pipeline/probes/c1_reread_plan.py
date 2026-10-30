"""C1 read again with the early-stopped fine-tune (TASKS 145; registration `GoalGathering/notes/PreRegistration_2026-10-30_C1_Reread.md`).
Arm (c)'s C1 — a covering selection of anchors below random draws on CH-oop — was read on 28 Oct with the fixed-step fine-tune (head_all,
3000 steps), which the recipe follow-up found to under-fit. This re-read keeps everything of arm (c) but the fine-tune: base (c), the same
random draws (`proxy_transfer_check.py --k --subsets 3`) and the same covers (`out/anchor_price_2026-10-28/cover_k*_d*.txt`) at k = 5, 10,
20, seeds 0–2, fine-tuned with the anchor count's recipe R2 (body1_es, early-stopped, cap 120 epochs) — and the same line.

    python probes/c1_reread_plan.py plan <out_dir>     # writes probes/runs/c1_reread.json (chain C1R)
    python probes/c1_reread_plan.py read <out_dir>     # c1_reread.json / .md beside the records
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import anchor_count_plan as AC
import anchor_price_plan as AP
import anchor_recipe_plan as AR
import proxy_check_plan as PC

M05, RUNS, AP_DIR = PC.M05, PC.RUNS, AR.AP_DIR
MODE = AR.RECIPES["R2"]                # body1_es: the anchor count's recipe
SIZES, DRAWS = AP.COVER_SIZES, AP.COVER_DRAWS
NEEDED = AP.C1_NEEDED                  # the registered C1 rule of 27 Oct: below at two of the three sizes


def random_name(k: int, s: int) -> str:
    return f"rd_k{k}_seed{s}"


def cover_name(k: int, d: int, s: int) -> str:
    return f"cv_k{k}_d{d}_seed{s}"


def steps(out_rel: str, n_pool: int) -> list[dict]:
    """The chain: the random draws (three per run), then the covers (one per run), each seed along k; every fine-tune R2 on base (c)."""
    ap_rel = Path(os.path.relpath(AP_DIR, M05)).as_posix()
    px_rel = Path(os.path.relpath(AR.PX_DIR, M05)).as_posix()
    out = [AR.fine_tune_step(out_rel, random_name(k, s), AP.base_model(ap_rel, n_pool, s), k, [MODE], AC.ES_MAX_EPOCHS)
           for s in PC.SEEDS for k in SIZES]
    for s in PC.SEEDS:
        for k in SIZES:
            for d in range(DRAWS):
                label = cover_name(k, d, s)
                out.append(AR.step(out_rel, label, ["{python}", "m05/proxy_transfer_check.py", "corpus/molecules", AP.base_model(ap_rel, n_pool, s),
                                                    f"{out_rel}/{label}", "--reservoir", f"{ap_rel}/cover_k{k}_d{d}.txt",
                                                    "--read", f"{px_rel}/a_read.txt", "--k", str(k), "--subsets", "1", "--modes", MODE,
                                                    "--es-max-epochs", str(AC.ES_MAX_EPOCHS), "--threads", PC.THREADS, "--allow-any-model"]))
    return out


def plan(out_dir: Path) -> Path:
    n_pool = AR.proxy_manifest()["pool"]["a"]
    needed = [AP_DIR / f"base_c_model_n{n_pool}_seed{s}.pt" for s in PC.SEEDS]
    needed += [AP_DIR / f"cover_k{k}_d{d}.txt" for k in SIZES for d in range(DRAWS)]
    if missing := [p.name for p in needed if not p.exists()]:
        raise SystemExit(f"arm (c)'s inputs are missing: {missing}")
    out_dir.mkdir(parents=True, exist_ok=True)
    st = steps(Path(os.path.relpath(out_dir, M05)).as_posix(), n_pool)
    spec = {"_about": "C1 re-read with body1_es: probes/c1_reread_plan.py plan (TASKS 145)", "name": "C1R", "steps": st,
            "outputs": [f"modules/05_support_predictor/{s['argv'][4]}.json" for s in st]}
    path = RUNS / "c1_reread.json"
    PC.write_text(path, json.dumps(spec, indent=1))
    return path


def assess(random_by_k: dict[int, list[dict]], cover_by_k: dict[int, list[dict]]) -> dict:
    """C1 on R2: per size the CH-oop mean ± se over seeds × draws of the random draws and of the covers; below at NEEDED sizes holds."""
    rand = {k: AP.family_column(r, MODE)["CH-oop"] for k, r in random_by_k.items()}
    cov = {k: AP.family_column(r, MODE)["CH-oop"] for k, r in cover_by_k.items()}
    at = [k for k in SIZES if PC.lower(cov[k], rand[k])]
    return {"random": rand, "cover": cov, "C1": {"holds": len(at) >= NEEDED, "at": at}}


def read(out_dir: Path) -> dict:
    random_by_k = {k: AP.read_records(out_dir, [random_name(k, s) for s in PC.SEEDS]) for k in SIZES}
    cover_by_k = {k: AP.read_records(out_dir, [cover_name(k, d, s) for s in PC.SEEDS for d in range(DRAWS)]) for k in SIZES}
    res = assess(random_by_k, cover_by_k)
    fixed = json.loads((AP_DIR / "anchor_price_read.json").read_text(encoding="utf-8"))["C1"]
    res["fixed_step_C1"] = fixed
    PC.write_text(out_dir / "c1_reread.json", json.dumps(res, indent=1, default=str))
    PC.write_text(out_dir / "c1_reread.md", "\n".join(report_lines(res)) + "\n")
    return res


def report_lines(res: dict) -> list[str]:
    c1, fixed = res["C1"], res.get("fixed_step_C1", {})
    lines = ["# C1 read again with the early-stopped fine-tune (TASKS 145)", "",
             f"**C1 on R2 ({MODE}, cap {AC.ES_MAX_EPOCHS})**, covers below random draws on CH-oop by more than {PC.SE_FACTOR} combined se at "
             f"{NEEDED} of k = {list(SIZES)}: {'holds' if c1['holds'] else 'does not hold'} (at {c1['at']}). "
             f"With the fixed-step fine-tune (28 Oct): {'holds' if fixed.get('holds') else 'does not hold'} (at {fixed.get('at')}).", "",
             "| k | random draws, CH-oop | covers, CH-oop |", "|---|---|---|"]
    lines += [f"| {k} | {res['random'][k][0]:.2f} ± {res['random'][k][1]:.2f} | {res['cover'][k][0]:.2f} ± {res['cover'][k][1]:.2f} |" for k in SIZES]
    return lines


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("action", choices=["plan", "read"])
    ap.add_argument("out_dir", type=Path)
    a = ap.parse_args(argv)
    print(plan(a.out_dir) if a.action == "plan" else json.dumps(read(a.out_dir)["C1"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
