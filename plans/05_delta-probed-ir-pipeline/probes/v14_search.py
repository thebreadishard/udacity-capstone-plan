"""Version 1.4's hyperparameter search (registration GoalGathering/notes/Design_2026-10-26_DeltaH_v1.4_Recipe_and_Search.md, §4–§5).

    python probes/v14_search.py plan --carried-models <3 .pt>
                                       the frozen list (control, its parity, target and schedule variants, 12 drawn), the carried
                                       version named, stage 1's chain (two seeds each)
    python probes/v14_search.py read1  stage 1 scored on the selection set; stage 2's chain (best four + control, the third seed)
    python probes/v14_search.py read2  the winner (no-worsening rule, two SE); the final chain
    python probes/v14_search.py read3  the target check and the promotion against the carried version

Selection uses only the selection set (`rungC_train.py --selection-split`, whole scaffold cores, never trained); the hold-outs are read once,
for the winner and the carried version, in the final chain. A configuration's score per seed is the mean of the five read-outs on the
selection set, each divided by its line (the families' diagonal rms by 3 cm⁻¹, the coupling ratio by 0.25). The parity-odd factor and rung B's
pair features do not combine (`rungC_config`), so the search deals one or the other; the target (projected or ridge) is dealt the same way
(the user, 8 Nov 2026: a categorical of the search instead of chain 44). Since the amendment of 15 Nov 2026 (§11; the user: the learning
rate is always part of our search) the learning-rate schedule is drawn the same way, the two loss weights stay at the carried values
(34b/34c measured no response), and stage 1 trains two seeds of every configuration, because one seed's score moves by as much as a
hyperparameter does. Paths are relative to module 05 unless named otherwise.
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
from rungC_config import LR_SCHEDULES, WEIGHT_DECAY  # noqa: E402, RUF100
from rungC_equivariant import N_BLOCKS, N_S  # noqa: E402, RUF100

SEARCH_SEED = 20261026
N_DRAWN = 12
STAGE1_SEEDS = (0, 1)                      # two seeds screen: v1.3's seeds differ by up to 0.8 cm⁻¹ within a family
STAGE1_TAGS = {0: "s1a", 1: "s1b"}         # a step and a record per seed: a restart loses one training, and seed 0's pass ranks alone
STAGE2_SEED = 2                            # the third seed, for the best of stage 1 and the control
STAGE2_BEST = 4
SELECTION = "26:0.15"
POOL_LAYERS = "A,A2,B,P3,P3c"
EPOCH_CAP = 300
CAP_MARGIN = 0.10                          # decision 51: a best epoch within 10 % of the cap means the cap, not the data, stopped it
THREADS = "8"
MAX_GAP_MINUTES = 120                      # the run-spec schema's ceiling; the chain runner prints progress every 30 min
LINES = {**dict.fromkeys(P.FAMILIES, 3.0), P.RATIO: 0.25}
OUT = "out/v14"
SPACE = {"lr": (1e-4, 1e-3), "weight_decay": (1e-5, 1e-3),
         "body_width": (64, 96, 128), "body_blocks": (3, 4), "hybrid_hidden": (128, 256, 512)}
LOG_RANGES = ("lr", "weight_decay")
TARGETS = ("projected", "ls")
CARRIED_TARGET = "projected"                 # the carried recipe's (RECIPE_V11 has no --aux-target)
CHOICES_SEED = SEARCH_SEED + 1               # the generator that shuffles the dealt choices: the drawn ranges keep theirs
SCHEDULES = LR_SCHEDULES                     # the trainer's: constant (carried) or cosine with its warm-up
CARRIED_SCHEDULE = "constant"
HOURS = {"constant": 2.0, "cosine": 3.5}     # per training at ≈ 1,200 molecules: chain 41 ran 1.0-1.9 h per seed at 972 and stopped
                                             # early; a cosine runs all of the cap's epochs


@dataclass(frozen=True)
class Config:
    """One point of the search. `parity` True = the parity-odd factor without rung B's pair features; False = the pair features (carried).
    `target` is one of TARGETS (projected = the carried one), `schedule` one of SCHEDULES (constant = the carried one). The two loss
    weights are the carried values in every configuration since 15 Nov 2026."""
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
    schedule: str


def _recipe_value(flag: str) -> str:
    r = chain_runner.RECIPE_V11
    return r[r.index(flag) + 1]


def control() -> Config:
    """The carried recipe: RECIPE_V11's values, the trainer's weight decay and body size, the carried target."""
    return Config("c00_control", float(_recipe_value("--lr")), WEIGHT_DECAY, N_S, N_BLOCKS, int(_recipe_value("--hybrid-hidden")),
                  float(_recipe_value("--kring-weight")), float(_recipe_value("--kdiag-weight")), parity=False, target=CARRIED_TARGET,
                  schedule=CARRIED_SCHEDULE)


def _three_digits(x: float) -> float:
    return float(f"{x:.3g}")


def dealt_choices(n: int, seed: int) -> list[tuple[bool, str, str]]:
    """n triples (parity, target, schedule) as one design, in an order shuffled by `seed`: the eight combinations, then the half
    fraction in which an even number of the three differ from the carried value, and so on round. Twelve fair coins left ten of one
    target; three separate shuffles would balance each choice and leave the pairs to chance. At n = 12 every value of every choice
    comes six times and every pair of values of two choices three times."""
    full = [(p, t, s) for p in (False, True) for t in TARGETS for s in SCHEDULES]
    half = [c for c in full if (c[0] + (c[1] != CARRIED_TARGET) + (c[2] != CARRIED_SCHEDULE)) % 2 == 0]
    design = [*full, *half]
    cycle = [design[k % len(design)] for k in range(n)]
    return [cycle[k] for k in np.random.default_rng(seed).permutation(n)]


def draw(n: int = N_DRAWN, seed: int = SEARCH_SEED, choices_seed: int = CHOICES_SEED) -> list[Config]:
    """n configurations drawn once from SPACE (log-uniform on the log ranges, uniform choices); the parity variant, the target and the
    schedule are dealt together as one balanced design (`dealt_choices`); the loss weights are the control's."""
    rng = np.random.default_rng(seed)
    choices = dealt_choices(n, choices_seed)
    carried = control()
    out = []
    for k in range(n):
        v = {name: _three_digits(10 ** rng.uniform(math.log10(SPACE[name][0]), math.log10(SPACE[name][1]))) for name in LOG_RANGES}
        v |= {name: int(rng.choice(SPACE[name])) for name in ("body_width", "body_blocks", "hybrid_hidden")}
        parity, target, schedule = choices[k]
        out.append(Config(f"c{k + 4:02d}", parity=parity, target=target, schedule=schedule,
                          kring_weight=carried.kring_weight, kdiag_weight=carried.kdiag_weight, **v))
    return out


def frozen_list() -> list[Config]:
    """The control, its three one-factor ablations (the parity factor; the other target; the other schedule) and the drawn
    configurations."""
    c = control()
    other = next(t for t in TARGETS if t != CARRIED_TARGET)
    other_schedule = next(s for s in SCHEDULES if s != CARRIED_SCHEDULE)
    return [c, replace(c, name="c01_control_parity", parity=True), replace(c, name="c02_control_target", target=other),
            replace(c, name="c03_control_schedule", schedule=other_schedule), *draw()]


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
    if cfg.schedule != CARRIED_SCHEDULE:
        # the cosine is defined on the cap: stopped at the carried patience of 20 it would end near epoch 120-180 with the rate still at
        # 0.35-0.67 of its value, and the search would have tested a warm-up, not an anneal. A patience of the cap never stops the run
        # and still restores the best state on the inner validation term.
        flags |= {"--lr-schedule": cfg.schedule, "--patience": str(EPOCH_CAP)}
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
            "progress": {"regex": f"^=== \\({tag}\\) progress: |^\\({tag}\\) .* done ", "max_gap_minutes": MAX_GAP_MINUTES,
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


def at_cap(r: SeedRead, schedule: str) -> bool:
    """Decision 51's rule, for a constant rate: a best epoch within CAP_MARGIN of the cap means the cap stopped the run. A cosine
    configuration trains every epoch of the cap and its rate reaches the floor there by construction, so a late best epoch is the
    schedule working, and a higher cap would be another schedule, not a rerun; the reads mark it LATE and refuse nothing."""
    return schedule == "constant" and r.best_epoch is not None and r.best_epoch >= (1 - CAP_MARGIN) * r.cap


def epoch_note(r: SeedRead, schedule: str) -> str:
    """A seed's best epoch as the reads print it: AT CAP under the constant rate's rule, LATE for a cosine whose best is that late."""
    late = r.best_epoch is not None and r.best_epoch >= (1 - CAP_MARGIN) * r.cap
    return f"{r.best_epoch}{(' AT CAP' if schedule == 'constant' else ' LATE') if late else ''}"


def no_worse(new: dict, old: dict) -> tuple[str, ...]:
    """The read-outs on which one seed's selection read is worse than another's at the reported precision."""
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
def cmd_plan(carried_models: list[str]) -> int:
    missing = [m for m in carried_models if not (M05 / m).is_file()]
    if missing:
        raise SystemExit(f"--carried-models: not found under module 05: {missing}")
    configs = frozen_list()
    sha = canonical_sha(configs)
    write_new(M05 / OUT / "configs.json", {"search_seed": SEARCH_SEED, "selection_split": SELECTION, "pool_layers": POOL_LAYERS,
                                           "epoch_cap": EPOCH_CAP, "space": SPACE, "schedules": list(SCHEDULES),
                                           "stage1_seeds": list(STAGE1_SEEDS), "stage2_seed": STAGE2_SEED,
                                           "configs": [asdict(c) for c in configs], "sha256": sha,
                                           "carried_models": carried_models})
    steps = [{"kind": "cmd", "label": "design check of the v1.4 pool", "cwd": M05_REL, "log": f"{M05_REL}/{OUT}/design_check.log",
              "argv": ["{python}", "m05/design_check.py", "corpus/molecules", "--aggregation", "sum", "--out", f"{OUT}/design_check"]}]
    seeds = ",".join(str(s) for s in STAGE1_SEEDS)
    steps += [train_step(c, STAGE1_TAGS[s], str(s)) for s in STAGE1_SEEDS for c in configs] + [read_step("read1")]
    about = (f"v1.4 stage 1 (registration of 26 Oct 2026, amended 15 Nov): {len(configs)} configurations, seeds {seeds} (every "
             f"configuration's seed {STAGE1_SEEDS[0]} first), scored on the selection set; frozen list sha256 {sha}")
    write_new(PLAN / "probes" / "runs" / "v14_stage1.json", chain("V14S1", about, steps, [f"{M05_REL}/{OUT}/read1.json"]))
    write_new(PLAN / "probes" / "runspecs" / "v14_stage1.json",
              runspec("v14_stage1", "V14S1", "v1.4 stage 1: the frozen list, two seeds each, then read1 writes stage 2",
                      len(STAGE1_SEEDS) * sum(HOURS[c.schedule] for c in configs),
                      "≈ 2 h per constant-rate training at ≈ 1,200 molecules (chain 41: 1.0-1.9 h per seed at 972, stopped early), "
                      "≈ 3.5 h for a cosine, which runs all 300 epochs"))
    print(f"frozen list of {len(configs)} configurations, sha256 {sha}; stage 1 chain and runspec written")
    return 0


def cmd_read1() -> int:
    configs, _ = load_list()
    ctrl = configs[0]
    reads = {c.name: stage1_seeds(c) for c in configs}
    means = {c.name: sum(score(r.sel) for r in reads[c.name]) / len(reads[c.name]) for c in configs}
    ctrl_arm = P.arm_from_seeds([{"sel": r.sel} for r in reads[ctrl.name]], ("sel",))
    ranked = sorted(configs, key=lambda c: means[c.name])
    lines = [f"# v1.4 stage 1 — selection-set scores (seeds {', '.join(str(s) for s in STAGE1_SEEDS)})", "",
             "| rank | configuration | schedule | score (seed mean) | per seed | worse than control on | best epoch / cap |",
             "|---|---|---|---|---|---|---|"]
    for k, c in enumerate(ranked, 1):
        rs = reads[c.name]
        arm = P.arm_from_seeds([{"sel": r.sel} for r in rs], ("sel",))
        worse = "—" if c.name == ctrl.name else ", ".join(P.promotion(P.compare(arm, ctrl_arm)).worse) or "—"
        epochs = ", ".join(epoch_note(r, c.schedule) for r in rs)
        per_seed = ", ".join(f"{score(r.sel):.3f}" for r in rs)
        lines.append(f"| {k} | {c.name} | {c.schedule} | {means[c.name]:.3f} | {per_seed} | {worse} | {epochs} / {rs[0].cap} |")
    best = [c for c in ranked if c.name != ctrl.name][:STAGE2_BEST]
    lines += ["", f"Stage 2: {', '.join(c.name for c in best)} and the control, seed {STAGE2_SEED}. Two seeds: the no-worsening column "
              "informs, stage 2 decides on three."]
    _write_report("read1", lines, {"scores": means, "seed_scores": {n: [score(r.sel) for r in rs] for n, rs in reads.items()},
                                   "stage2": [c.name for c in best]})
    steps = [train_step(c, "s2", str(STAGE2_SEED)) for c in [ctrl, *best]] + [read_step("read2")]
    about = f"v1.4 stage 2: the best four of stage 1 and the control, seed {STAGE2_SEED}, then read2"
    write_new(PLAN / "probes" / "runs" / "v14_stage2.json", chain("V14S2", about, steps, [f"{M05_REL}/{OUT}/read2.json"]))
    write_new(PLAN / "probes" / "runspecs" / "v14_stage2.json",
              runspec("v14_stage2", "V14S2", "v1.4 stage 2: the third seed for the best four and the control, then read2",
                      sum(HOURS[c.schedule] for c in [ctrl, *best]), "≈ 2 h per constant-rate training, ≈ 3.5 h per cosine, one seed each"))
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


def stage1_seeds(c: Config) -> list[SeedRead]:
    return [seed_reads(prefix(c, STAGE1_TAGS[s]))[s] for s in STAGE1_SEEDS]


def three_seeds(c: Config) -> list[SeedRead]:
    return [*stage1_seeds(c), seed_reads(prefix(c, "s2"))[STAGE2_SEED]]


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
                         any(at_cap(r, by_name[n].schedule) for r in rs))
    name, reason = winner([rows[n] for n in chosen], rows[ctrl.name])
    if rows[name].at_cap:
        raise SystemExit(f"{name}: a best epoch within {CAP_MARGIN:.0%} of the cap — rerun it at a higher cap before it can win (decision 51)")
    lines = ["# v1.4 stage 2 — three seeds on the selection set", "",
             f"| configuration | score (mean ± SE) | seed {STAGE2_SEED} alone | worse than control on | best epochs |", "|---|---|---|---|---|"]
    lines += [f"| {r.name} | {r.mean:.3f} ± {r.se:.3f} | {r.scores[-1]:.3f} | {', '.join(r.worse) or '—'} | "
              f"{', '.join(epoch_note(x, by_name[r.name].schedule) for x in arms[r.name])} |" for r in rows.values()]
    lines += ["", f"**Winner: {name}** — {reason}.", "",
              f"Two of a candidate's three seeds are the ones stage 1 chose it on, and the control was not chosen: the mean flatters a "
              f"candidate. Seed {STAGE2_SEED} alone is the unselected comparison, and the hold-out promotion of read3 is the guard.", "",
              cation_line(arms[name])]
    _write_report("read2", lines, {"winner": name, "reason": reason, "rows": {n: asdict(r) for n, r in rows.items()}})
    _write_final_chain(by_name[name], carried_models)
    print("\n".join(lines))
    return 0


def _eval_step(model: str, out: str) -> dict:
    return {"kind": "cmd", "label": f"eval {Path(out).name}", "cwd": M05_REL, "log": f"{M05_REL}/{out}.log",
            "glob_args": True, "argv": ["{python}", "../../probes/rungC_eval_saved.py", model, out, "--use-analytic", "--threads", THREADS,
                                        "--allow-any-model", "--holdout-b-file", chain_runner.HOLDOUT_B]}


def winner_models(w: Config) -> list[str]:
    return [*(f"{prefix(w, STAGE1_TAGS[s])}_model_n*_seed{s}.pt" for s in STAGE1_SEEDS), f"{prefix(w, 's2')}_model_n*_seed{STAGE2_SEED}.pt"]


def _write_final_chain(w: Config, carried_models: list[str]) -> None:
    other = replace(w, target=next(t for t in TARGETS if t != w.target))
    steps = [train_step(other, "s3other", "0,1,2")]
    steps += [_eval_step(m, f"{OUT}/eval_winner_seed{s}") for s, m in enumerate(winner_models(w))]
    steps += [_eval_step(m, f"{OUT}/eval_carried_seed{s}") for s, m in enumerate(carried_models)]
    steps.append(read_step("read3"))
    about = f"v1.4 final: {w.name} with the other target (three seeds), the winner and the carried version read on the hold-outs, read3"
    write_new(PLAN / "probes" / "runs" / "v14_final.json", chain("V14F", about, steps, [f"{M05_REL}/{OUT}/read3.json"]))
    write_new(PLAN / "probes" / "runspecs" / "v14_final.json",
              runspec("v14_final", "V14F", "v1.4 final: target check, hold-out reads, promotion", 3 * HOURS[w.schedule] + 1.0,
                      "three trainings at the winner's schedule, six evals ≈ 20 min"))


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
    plan.add_argument("--carried-models", nargs=3, required=True, help="the carried version's three checkpoints, relative to module 05")
    sub.add_parser("read1")
    sub.add_parser("read2")
    sub.add_parser("read3")
    a = ap.parse_args(argv)
    if a.cmd == "plan":
        return cmd_plan(a.carried_models)
    if a.cmd == "read1":
        return cmd_read1()
    if a.cmd == "read2":
        return cmd_read2()
    return cmd_read3()


if __name__ == "__main__":
    raise SystemExit(main())
