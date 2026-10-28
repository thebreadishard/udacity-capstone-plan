"""Version 1.4's hyperparameter search (registration GoalGathering/notes/Design_2026-10-26_DeltaH_v1.4_Recipe_and_Search.md, §4–§5).

    python probes/v14_search.py plan --target projected|ls --carried-models <3 .pt>
                                       the frozen list (control, its parity variant, 24 drawn), the carried version named, stage 1's chain
    python probes/v14_search.py read1  stage 1 scored on the selection set; stage 2's chain (best four + control)
    python probes/v14_search.py read2  the winner (no-worsening rule, two SE); the final chain
    python probes/v14_search.py read3  the target check and the promotion against the carried version

Selection uses only the selection set (`rungC_train.py --selection-split`, whole scaffold cores, never trained); the hold-outs are read once,
for the winner and the carried version, in the final chain. A configuration's score per seed is the mean of the five read-outs on the
selection set, each divided by its line (the families' diagonal rms by 3 cm⁻¹, the coupling ratio by 0.25). The parity-odd factor and rung B's
pair features do not combine (`rungC_config`), so the search draws one or the other. Paths are relative to module 05 unless named otherwise.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from dataclasses import asdict, dataclass, replace
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
M05_REL = "modules/05_support_predictor"
M05 = PLAN / M05_REL
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(M05 / "m05"))
import chain_runner  # noqa: E402, RUF100  (pre-commit's pinned ruff flags imports after the path inserts; the newer one calls it unused)
import promotion_read as P  # noqa: E402, RUF100
from rungC_config import WEIGHT_DECAY  # noqa: E402, RUF100
from rungC_equivariant import N_BLOCKS, N_S  # noqa: E402, RUF100

SEARCH_SEED = 20261026
N_DRAWN = 24
STAGE2_BEST = 4
SELECTION = "26:0.15"
POOL_LAYERS = "A,A2,B,P3,P3c"
EPOCH_CAP = 300
CAP_MARGIN = 0.10                          # decision 51: a best epoch within 10 % of the cap means the cap, not the data, stopped it
THREADS = "8"
LINES = {**dict.fromkeys(P.FAMILIES, 3.0), P.RATIO: 0.25}
OUT = "out/v14"
SPACE = {"lr": (1e-4, 1e-3), "weight_decay": (1e-5, 1e-3), "kring_weight": (0.1, 1.0), "kdiag_weight": (0.03, 0.3),
         "body_width": (64, 96, 128), "body_blocks": (3, 4), "hybrid_hidden": (128, 256, 512)}
LOG_RANGES = ("lr", "weight_decay", "kring_weight", "kdiag_weight")
TARGETS = ("projected", "ls")


@dataclass(frozen=True)
class Config:
    """One point of the search. `parity` True = the parity-odd factor without rung B's pair features; False = the pair features (carried)."""
    name: str
    lr: float
    weight_decay: float
    body_width: int
    body_blocks: int
    hybrid_hidden: int
    kring_weight: float
    kdiag_weight: float
    parity: bool
    target: str


def _recipe_value(flag: str) -> str:
    r = chain_runner.RECIPE_V11
    return r[r.index(flag) + 1]


def control(target: str) -> Config:
    """The carried recipe's values (RECIPE_V11, the trainer's weight decay and body size), with the target of chain 44's read."""
    return Config("c00_control", float(_recipe_value("--lr")), WEIGHT_DECAY, N_S, N_BLOCKS, int(_recipe_value("--hybrid-hidden")),
                  float(_recipe_value("--kring-weight")), float(_recipe_value("--kdiag-weight")), parity=False, target=target)


def _three_digits(x: float) -> float:
    return float(f"{x:.3g}")


def draw(target: str, n: int = N_DRAWN, seed: int = SEARCH_SEED) -> list[Config]:
    """n configurations drawn once from SPACE (log-uniform on the log ranges, uniform choices), the parity variant by a fair coin."""
    rng = np.random.default_rng(seed)
    out = []
    for k in range(n):
        v = {name: _three_digits(10 ** rng.uniform(math.log10(SPACE[name][0]), math.log10(SPACE[name][1]))) for name in LOG_RANGES}
        v |= {name: int(rng.choice(SPACE[name])) for name in ("body_width", "body_blocks", "hybrid_hidden")}
        out.append(Config(f"c{k + 2:02d}", parity=bool(rng.random() < 0.5), target=target, **v))
    return out


def frozen_list(target: str) -> list[Config]:
    c = control(target)
    return [c, replace(c, name="c01_control_parity", parity=True), *draw(target)]


def _flags(flags: list[str]) -> dict[str, str | None]:
    """A flag list as {flag: value or None for a switch}, in order."""
    out: dict[str, str | None] = {}
    for k, f in enumerate(flags):
        if f.startswith("--"):
            nxt = flags[k + 1] if k + 1 < len(flags) else None
            out[f] = None if nxt is None or nxt.startswith("--") else nxt
    return out


def trainer_argv(cfg: Config, prefix: str, seeds: str) -> list[str]:
    """The trainer command of one configuration: the carried BASE and RECIPE_V11 with the search's values put in their place."""
    flags = _flags([*chain_runner.BASE, *chain_runner.RECIPE_V11])
    flags |= {"--pool-layers": POOL_LAYERS, "--epochs": str(EPOCH_CAP), "--lr": f"{cfg.lr:g}", "--weight-decay": f"{cfg.weight_decay:g}",
              "--body-width": str(cfg.body_width), "--body-blocks": str(cfg.body_blocks), "--hybrid-hidden": str(cfg.hybrid_hidden),
              "--kring-weight": f"{cfg.kring_weight:g}", "--kdiag-weight": f"{cfg.kdiag_weight:g}"}
    if cfg.parity:
        flags.pop("--pair-features")
        flags["--parity-odd-mixed"] = None
    if cfg.target != "projected":
        flags["--aux-target"] = cfg.target
    argv = [x for f, v in flags.items() for x in ((f,) if v is None else (f, v))]
    return ["{python}", "m05/rungC_train.py", "corpus/molecules", prefix, *argv, "--selection-split", SELECTION, "--sizes", "all",
            "--seeds", seeds, "--threads", THREADS, "--save-model"]


def prefix(cfg: Config, stage: str) -> str:
    return f"{OUT}/E7_rungC_v14{stage}_{cfg.name}"


def train_step(cfg: Config, stage: str, seeds: str) -> dict:
    pre = prefix(cfg, stage)
    return {"kind": "cmd", "label": f"train {cfg.name} ({stage}, seeds {seeds})", "cwd": M05_REL,
            "log": f"{M05_REL}/{pre}.log", "argv": trainer_argv(cfg, pre, seeds)}


def read_step(command: str, extra: list[str] | None = None) -> dict:
    return {"kind": "cmd", "label": f"v1.4 search {command}", "cwd": ".", "log": f"{M05_REL}/{OUT}/{command}.log",
            "argv": ["{python}", "probes/v14_search.py", command, *(extra or [])]}


def chain(name: str, about: str, steps: list[dict], outputs: list[str]) -> dict:
    return {"_about": about, "name": name, "poll_s": 1800, "wait": [], "steps": steps, "outputs": outputs}


def runspec(name: str, tag: str, purpose: str, hours: float, basis: str) -> dict:
    return {"name": name, "purpose": purpose, "host": "laptop", "workdir": "probes/results_m1",
            "command": f"python ../chain_runner.py probes/runs/{name}.json",
            "sources": [{"local": "probes/chain_runner.py"}, {"local": "probes/v14_search.py"}, {"local": "probes/promotion_read.py"},
                        {"local": f"{M05_REL}/m05/rungC_train.py"}],
            "progress": {"regex": f"^=== \\({tag}\\) progress: |^\\({tag}\\) .* done ", "max_gap_minutes": 180,
                         "start_regex": f"^=== \\({tag}\\) starting: "},
            "marker_regex": f"^=== \\({tag}\\) (armed|starting|resuming|RUN FAILED|run done)", "end_regex": f"^=== \\({tag}\\) run done",
            "fail_regex": f"^=== \\({tag}\\) RUN FAILED", "dry_run_args": "--dry-run", "resumable": True,
            "memory": {"peak_gb": 7.7, "basis": "chain 41's trainer peak (7.7 GB at n = 972-978, 19 Oct 2026); v1.4's pool ≈ 1,200"},
            "estimate": {"hours": hours, "basis": basis}}


def write_new(path: Path, obj: object) -> None:
    """A JSON file that must not exist yet: a frozen list or a chain is never overwritten."""
    if path.exists():
        raise SystemExit(f"{path} exists — refusing to overwrite a frozen file")
    path.parent.mkdir(parents=True, exist_ok=True)
    P.write_atomic(path, json.dumps(obj, indent=1, ensure_ascii=False) + "\n")


def canonical_sha(configs: list[Config]) -> str:
    return hashlib.sha256(json.dumps([asdict(c) for c in configs], sort_keys=True).encode()).hexdigest()


def load_list() -> tuple[list[Config], list[str]]:
    """(the frozen configurations, the carried version's three checkpoints), checked against the list's sha256."""
    rec = json.loads((M05 / OUT / "configs.json").read_text(encoding="utf-8"))
    configs = [Config(**c) for c in rec["configs"]]
    if canonical_sha(configs) != rec["sha256"]:
        raise SystemExit("configs.json does not match its sha256 — the frozen list was edited")
    return configs, rec["carried_models"]


# ------------------------------------------------------------------------------------------------------------------------------- scores
@dataclass(frozen=True)
class SeedRead:
    sel: dict
    per_molecule: dict
    best_epoch: int | None
    cap: int


def seed_reads(pre: str) -> dict[int, SeedRead]:
    """The selection-set read-outs of every seed in a trainer record (`<prefix>.json`, one pool size)."""
    rec = json.loads((M05 / f"{pre}.json").read_text(encoding="utf-8"))
    if rec.get("selection_split") != SELECTION:
        raise SystemExit(f"{pre}.json was not trained with --selection-split {SELECTION}")
    (entry,) = rec["curve"].values()
    return {s["seed"]: SeedRead(s["sel"], s["sel"].get("per_molecule", {}), s.get("best_epoch"), rec["epochs"]) for s in entry["per_seed"]}


def score(sel: dict) -> float:
    """The mean of the five read-outs, each over its line: 1.0 = on the lines on average."""
    vals = [sel["diag_rms"][f] / LINES[f] for f in P.FAMILIES] + [sel[P.RATIO] / LINES[P.RATIO]]
    return sum(vals) / len(vals)


def at_cap(r: SeedRead) -> bool:
    return r.best_epoch is not None and r.best_epoch >= (1 - CAP_MARGIN) * r.cap


def no_worse(new: dict, old: dict) -> tuple[str, ...]:
    """The read-outs on which one seed's selection read is worse than another's at the reported precision (stage 1: one seed each)."""
    return tuple(q for q in P.QUANTITIES if P.reported(_q(new, q), q) > P.reported(_q(old, q), q))


def _q(sel: dict, q: str) -> float:
    return sel[P.RATIO] if q == P.RATIO else sel["diag_rms"][q]


def cation_line(reads: list[SeedRead]) -> str:
    """Per-molecule corrected ω rms of the cation rows (P3c_) against the neutral rows of the selection set, mean over seeds and molecules;
    the trainer's per-molecule record carries no per-family diagonal, so this is the cation number the records allow."""
    def mean_of(pred) -> tuple[float, int]:
        v = [m["corrected_freq_rms"] for r in reads for i, m in r.per_molecule.items() if pred(i) and m.get("corrected_freq_rms") is not None]
        return (sum(v) / len(v), len(v)) if v else (float("nan"), 0)
    (c, nc), (n, nn) = mean_of(lambda i: i.startswith("P3c_")), mean_of(lambda i: not i.startswith("P3c_"))
    return f"cations: corrected ω {c:.2f} cm⁻¹ over {nc} reads; neutrals {n:.2f} over {nn}"


# -------------------------------------------------------------------------------------------------------------------------------- commands
def cmd_plan(target: str, carried_models: list[str]) -> int:
    missing = [m for m in carried_models if not (M05 / m).is_file()]
    if missing:
        raise SystemExit(f"--carried-models: not found under module 05: {missing}")
    configs = frozen_list(target)
    sha = canonical_sha(configs)
    write_new(M05 / OUT / "configs.json", {"search_seed": SEARCH_SEED, "selection_split": SELECTION, "pool_layers": POOL_LAYERS,
                                           "epoch_cap": EPOCH_CAP, "space": SPACE, "configs": [asdict(c) for c in configs], "sha256": sha,
                                           "carried_models": carried_models})
    steps = [{"kind": "cmd", "label": "design check of the v1.4 pool", "cwd": M05_REL, "log": f"{M05_REL}/{OUT}/design_check.log",
              "argv": ["{python}", "m05/design_check.py", "corpus/molecules", "--aggregation", "sum", "--out", f"{OUT}/design_check"]}]
    steps += [train_step(c, "s1", "0") for c in configs] + [read_step("read1")]
    about = f"v1.4 stage 1 (registration of 26 Oct 2026): {len(configs)} configurations, seed 0, scored on the selection set; frozen list sha256 {sha}"
    write_new(PLAN / "probes" / "runs" / "v14_stage1.json", chain("V14S1", about, steps, [f"{M05_REL}/{OUT}/read1.json"]))
    write_new(PLAN / "probes" / "runspecs" / "v14_stage1.json",
              runspec("v14_stage1", "V14S1", "v1.4 stage 1: the frozen list, one seed each, then read1 writes stage 2", 2.0 * len(configs),
                      "≈ 2 h per training at ≈ 1,200 molecules (chain 41: 1.0-1.9 h per seed at 972)"))
    print(f"frozen list of {len(configs)} configurations, sha256 {sha}; stage 1 chain and runspec written")
    return 0


def cmd_read1() -> int:
    configs, _ = load_list()
    ctrl = configs[0]
    reads = {c.name: seed_reads(prefix(c, "s1"))[0] for c in configs}
    ranked = sorted(configs, key=lambda c: score(reads[c.name].sel))
    lines = ["# v1.4 stage 1 — selection-set scores (one seed)", "", "| rank | configuration | score | worse than control on | best epoch / cap |",
             "|---|---|---|---|---|"]
    for k, c in enumerate(ranked, 1):
        r = reads[c.name]
        worse = ", ".join(no_worse(r.sel, reads[ctrl.name].sel)) or "—"
        lines.append(f"| {k} | {c.name} | {score(r.sel):.3f} | {worse} | {r.best_epoch} / {r.cap}{' AT CAP' if at_cap(r) else ''} |")
    best = [c for c in ranked if c.name != ctrl.name][:STAGE2_BEST]
    lines += ["", f"Stage 2: {', '.join(c.name for c in best)} and the control, seeds 1 and 2. One seed: the no-worsening column informs, "
              "stage 2 decides."]
    _write_report("read1", lines, {"scores": {c.name: score(reads[c.name].sel) for c in configs}, "stage2": [c.name for c in best]})
    steps = [train_step(c, "s2", "1,2") for c in [ctrl, *best]] + [read_step("read2")]
    about = "v1.4 stage 2: the best four of stage 1 and the control, seeds 1 and 2, then read2"
    write_new(PLAN / "probes" / "runs" / "v14_stage2.json", chain("V14S2", about, steps, [f"{M05_REL}/{OUT}/read2.json"]))
    write_new(PLAN / "probes" / "runspecs" / "v14_stage2.json",
              runspec("v14_stage2", "V14S2", "v1.4 stage 2: three seeds for the best four and the control, then read2", 2.0 * 2 * (1 + len(best)),
                      "≈ 2 h per training, two seeds each"))
    print("\n".join(lines))
    return 0


@dataclass(frozen=True)
class Stage2:
    name: str
    scores: tuple[float, ...]
    worse: tuple[str, ...]
    at_cap: bool

    @property
    def mean(self) -> float:
        return sum(self.scores) / len(self.scores)

    @property
    def se(self) -> float:
        m = self.mean
        return math.sqrt(sum((x - m) ** 2 for x in self.scores) / (len(self.scores) - 1)) / math.sqrt(len(self.scores))


def three_seeds(c: Config) -> list[SeedRead]:
    return [seed_reads(prefix(c, "s1"))[0], *(seed_reads(prefix(c, "s2"))[s] for s in (1, 2))]


def winner(cands: list[Stage2], ctrl: Stage2) -> tuple[str, str]:
    """(name, reason): the eligible candidate with the lowest mean score when its advantage over the control exceeds two combined SE."""
    eligible = sorted((c for c in cands if not c.worse), key=lambda c: c.mean)
    if not eligible:
        return ctrl.name, "no candidate is free of a worse read-out against the control; the control stays"
    w = eligible[0]
    gap, needed = ctrl.mean - w.mean, 2 * math.sqrt(w.se ** 2 + ctrl.se ** 2)
    if gap > needed:
        return w.name, f"{w.name} beats the control by {gap:.3f} in score against two combined SE {needed:.3f}"
    return ctrl.name, f"the best eligible ({w.name}) beats the control by {gap:.3f}, not beyond two combined SE {needed:.3f}; the control stays"


def cmd_read2() -> int:
    configs, carried_models = load_list()
    chosen = json.loads((M05 / OUT / "read1.json").read_text(encoding="utf-8"))["stage2"]
    ctrl = configs[0]
    by_name = {c.name: c for c in configs}
    arms = {n: three_seeds(by_name[n]) for n in [ctrl.name, *chosen]}
    ctrl_arm = P.arm_from_seeds([{"sel": r.sel} for r in arms[ctrl.name]], ("sel",))
    rows = {}
    for n, rs in arms.items():
        arm = P.arm_from_seeds([{"sel": r.sel} for r in rs], ("sel",))
        rows[n] = Stage2(n, tuple(score(r.sel) for r in rs), P.promotion(P.compare(arm, ctrl_arm)).worse if n != ctrl.name else (),
                         any(at_cap(r) for r in rs))
    name, reason = winner([rows[n] for n in chosen], rows[ctrl.name])
    if rows[name].at_cap:
        raise SystemExit(f"{name}: a best epoch within {CAP_MARGIN:.0%} of the cap — rerun it at a higher cap before it can win (decision 51)")
    lines = ["# v1.4 stage 2 — three seeds on the selection set", "", "| configuration | score (mean ± SE) | worse than control on |", "|---|---|---|"]
    lines += [f"| {r.name} | {r.mean:.3f} ± {r.se:.3f} | {', '.join(r.worse) or '—'} |" for r in rows.values()]
    lines += ["", f"**Winner: {name}** — {reason}.", "", cation_line(arms[name])]
    _write_report("read2", lines, {"winner": name, "reason": reason, "rows": {n: asdict(r) for n, r in rows.items()}})
    _write_final_chain(by_name[name], carried_models)
    print("\n".join(lines))
    return 0


def _eval_step(model: str, out: str) -> dict:
    return {"kind": "cmd", "label": f"eval {Path(out).name}", "cwd": M05_REL, "log": f"{M05_REL}/{out}.log",
            "glob_args": True, "argv": ["{python}", "../../probes/rungC_eval_saved.py", model, out, "--use-analytic", "--threads", THREADS,
                                        "--allow-any-model", "--holdout-b-file", chain_runner.HOLDOUT_B]}


def winner_models(w: Config) -> list[str]:
    return [f"{prefix(w, 's1')}_model_n*_seed0.pt", *(f"{prefix(w, 's2')}_model_n*_seed{s}.pt" for s in (1, 2))]


def _write_final_chain(w: Config, carried_models: list[str]) -> None:
    other = replace(w, target=next(t for t in TARGETS if t != w.target))
    steps = [train_step(other, "s3other", "0,1,2")]
    steps += [_eval_step(m, f"{OUT}/eval_winner_seed{s}") for s, m in enumerate(winner_models(w))]
    steps += [_eval_step(m, f"{OUT}/eval_carried_seed{s}") for s, m in enumerate(carried_models)]
    steps.append(read_step("read3"))
    about = f"v1.4 final: {w.name} with the other target (three seeds), the winner and the carried version read on the hold-outs, read3"
    write_new(PLAN / "probes" / "runs" / "v14_final.json", chain("V14F", about, steps, [f"{M05_REL}/{OUT}/read3.json"]))
    write_new(PLAN / "probes" / "runspecs" / "v14_final.json",
              runspec("v14_final", "V14F", "v1.4 final: target check, hold-out reads, promotion", 7.0, "three trainings ≈ 6 h, six evals ≈ 20 min"))


def cmd_read3() -> int:
    configs = {c.name: c for c in load_list()[0]}
    w = configs[json.loads((M05 / OUT / "read2.json").read_text(encoding="utf-8"))["winner"]]
    other = replace(w, target=next(t for t in TARGETS if t != w.target))
    w_arm = P.arm_from_seeds([{"sel": r.sel} for r in three_seeds(w)], ("sel",))
    o_reads = seed_reads(prefix(other, "s3other"))
    o_arm = P.arm_from_seeds([{"sel": o_reads[s].sel} for s in (0, 1, 2)], ("sel",))
    target_check = P.promotion(P.compare(o_arm, w_arm))
    evals = [M05 / f"{OUT}/eval_{who}_seed{s}.json" for who in ("winner", "carried") for s in (0, 1, 2)]
    new, carried = P.load_eval_arm(evals[:3]), P.load_eval_arm(evals[3:])
    comps = P.compare(new, carried)
    promo = P.promotion(comps)
    lines = ["# v1.4 final read", "", f"Winner {w.name} ({w.target}); the other target ({other.target}) on the selection set: "
             + ("**better on no read-out and worse on none — the target choice stands**" if not target_check.better and not target_check.worse
                else f"better on {', '.join(target_check.better) or 'none'}, worse on {', '.join(target_check.worse) or 'none'}"
                + (" — **the other target passes the no-worsening rule: the choice goes to the user**" if target_check.promoted else " — the choice stands")),
             "", *P.comparison_table(new, carried, comps, "v1.4 winner", "carried"), "",
             f"**Promotion: {'carried as version 1.4' if promo.promoted else 'not promoted'}** — worse on {', '.join(promo.worse) or 'none'}, "
             f"better on {len(promo.better)} of {len(comps)} (decision 57, the user's rule of 26 Oct)."]
    _write_report("read3", lines, {"winner": w.name, "target_check": asdict(target_check), "promotion": asdict(promo),
                                   "comparisons": [asdict(c) for c in comps]})
    print("\n".join(lines))
    return 0


def _write_report(name: str, lines: list[str], record: dict) -> None:
    base = M05 / OUT / name
    P.write_atomic(base.with_suffix(".md"), "\n".join(lines) + "\n")
    P.write_atomic(base.with_suffix(".json"), json.dumps(record, indent=1))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    plan = sub.add_parser("plan")
    plan.add_argument("--target", choices=TARGETS, required=True, help="the target chain 44's read chose")
    plan.add_argument("--carried-models", nargs=3, required=True, help="the carried version's three checkpoints, relative to module 05")
    sub.add_parser("read1")
    sub.add_parser("read2")
    sub.add_parser("read3")
    a = ap.parse_args(argv)
    if a.cmd == "plan":
        return cmd_plan(a.target, a.carried_models)
    if a.cmd == "read1":
        return cmd_read1()
    if a.cmd == "read2":
        return cmd_read2()
    return cmd_read3()


if __name__ == "__main__":
    raise SystemExit(main())
