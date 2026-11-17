"""Version 1.4's hyperparameter search (registration GoalGathering/notes/Design_2026-10-26_DeltaH_v1.4_Recipe_and_Search.md, §4–§5).

    python probes/v14_search.py plan --carried-models <3 .pt>
                                       the frozen list (control, its parity, target and schedule variants, 12 drawn), the carried
                                       version named, stage 1's chain (two seeds each)
    python probes/v14_search.py read1  stage 1 scored on the selection set; stage 2's chain (best four + control, the third seed)
    python probes/v14_search.py read2  the winner (no-worsening rule, two SE); the final chain
    python probes/v14_search.py read3  the target check and the promotion against the carried version (the registry's: 1.4 since
                                       17 Nov 2026, read in chain v14_clean's evals, in place of the frozen list's v1.3)
    python probes/v14_search.py read-data [--arm {data,clean}] [--replace]
                                       §14: the carried recipe on the whole pool (chain v14_data's six evals) against the carried
                                       version, by read3's promotion; out/v14/read_data.md and .json. --arm clean reads the same recipe
                                       trained with --holdout-twins drop-any-charge (tag s3clean, evals eval_clean_seed*.json; TASKS
                                       253) into out/v14/read_clean.md and .json
    python probes/v14_search.py seleval [--only CONFIG]
                                       the selection evals of every finished stage training, made where missing and checked: the reads
                                       then find them (and one of them is the smoke run of that path)
    python probes/v14_search.py register  the final chain's own step: its six checkpoints into the model registry before their evals

Selection uses only the selection set (`rungC_train.py --selection-split`, whole scaffold cores, never trained); the hold-outs are read once,
for the winner and the carried version, in the final chain. A configuration's score per seed is the mean of the five read-outs on the
selection set, each divided by its line (the families' diagonal rms by 3 cm⁻¹, the coupling ratio by 0.25). The parity-odd factor and rung B's
pair features do not combine (`rungC_config`), so the search deals one or the other; the target (projected or ridge) is dealt the same way
(the user, 8 Nov 2026: a categorical of the search instead of chain 44). Since the amendment of 15 Nov 2026 (§11; the user: the learning
rate is always part of our search) the learning-rate schedule is drawn the same way, the two loss weights stay at the carried values
(34b/34c measured no response), and stage 1 trains two seeds of every configuration, because one seed's score moves by as much as a
hyperparameter does. Since the amendment of 16 Nov 2026 (§12) the final chain trains the winner's recipe again on the whole pool,
selection set included, and the promotion is read on those three models: the split had taken every derivative of one hold-out molecule's
scaffold core out of the training pool, and the carried version trained on them. Since the second amendment of that day (§13) the
score is read on the selection set without EXCLUDED_SELECTION_CORES: each read evaluates the stage checkpoints it needs on that set
(`rungC_eval_saved.py --eval-ids-file`, one record per checkpoint, reused when it exists) and prints the registered score, on the whole
selection set, beside it. Since 17 Nov 2026 (the user) read3 and read-data decide by decision 57 as amended that day
(`promotion_read.amended_promotion`: the composite below the carried version's beyond the Student-t line, no read-out worse beyond two
SE) and print the rule of 26 Oct beside it, deciding nothing. Paths are relative to module 05 unless named otherwise.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import subprocess
import sys
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass, replace
from operator import attrgetter
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
M05_REL = "modules/05_support_predictor"
M05 = PLAN / M05_REL
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(M05 / "m05"))
import chain_runner  # noqa: E402, RUF100  (pre-commit's pinned ruff flags imports after the path inserts; the newer one calls it unused)
import model_registry as MR  # noqa: E402, RUF100
import promotion_read as P  # noqa: E402, RUF100
from rungC_config import LR_SCHEDULES, WEIGHT_DECAY  # noqa: E402, RUF100
from rungC_equivariant import N_BLOCKS, N_S  # noqa: E402, RUF100
from rungC_settings_added import RUN_ONLY, setting_differences  # noqa: E402, RUF100

SEARCH_SEED = 20261026
N_DRAWN = 12
STAGE1_SEEDS = (0, 1)                      # two seeds screen: v1.3's seeds differ by up to 0.8 cm⁻¹ within a family
STAGE1_TAGS = {0: "s1a", 1: "s1b"}         # a step and a record per seed: a restart loses one training, and seed 0's pass ranks alone
STAGE2_SEED = 2                            # the third seed, for the best of stage 1 and the control
STAGE2_BEST = 4
FINAL_SEEDS = (0, 1, 2)                    # the final chain's trainings: the other target, and the winner on the whole pool
FULL_TAG = "s3full"                        # the data arm (§14): the control's recipe without the selection split
FINAL_TAG = "s3win"                        # the final chain's winner without the selection split (§12), never written over s3full
CLEAN_TAG = "s3clean"                      # the carried recipe on the whole pool without any hold-out twin of any charge (TASKS 253)
CLEAN_TWINS = "drop-any-charge"            # the twin rule of every whole-pool training a promotion is read on (TASKS 253)
CHECKPOINT = re.compile(r"(?P<prefix>.+)_model_n\d+_seed(?P<seed>\d+)\.pt")   # the trainer's `<prefix>_model_n<N>_seed<S>.pt`
SELECTION = "26:0.15"
N_SELECTION = 169                          # what the split sets aside in this search's corpus, of 18 scaffold cores
EXCLUDED_SELECTION_CORES = ("biphenylene",)  # not scored (§13): the corpus's only four-membered ring, and the split took all of its
N_EXCLUDED = 8                             # derivatives, so no configuration can learn it and its error is not a recipe's
SEL_ALL, SEL_SCORED = "selall", "selscored"  # the evaluator's names for the whole selection set and the part the score is read on
SEL_REPRODUCTION_TOL = 1e-3                # score units: a selection eval must give the trainer's own score on the whole set
TRAINED_WITH_SPLIT, TRAINED_WHOLE = 911, 1080  # molecules a stage training and a whole-pool one train on (an estimate: 1080 with two
                                                # hold-out twins dropped; drop-any-charge leaves about 1075)
PREDICTION_MOLECULE, PREDICTION_LINE = "A_72b86c2331", 4.7  # §12: biphenylene's corrected ω rms on the whole-pool models, cm⁻¹
RERUN_CAP = 450                            # the cap §12 names for a whole-pool rerun when the cap, not the data, stopped a seed
CLEAN_A = "a8"                             # hold-out (a) without its two trained twins, as the evals name it (m08.accuracy.CLEAN_SET)
DATA_LICENCE_NOTE = ("Apart from this read, and deciding nothing in it: the licence's quantity — the band error of the seed-mean ΔH "
                     "(decision 65 as amended on 16 Nov 2026) — is made by `probes/product_error_read.py` and is not in this read.")
REGISTRY_STATUS_FILE: Path | None = None   # None: the model registry's own status file for the checkpoint's folder; tests name another
REGISTRY_CHAIN = "v14 search"
REGISTRY_NOTE = "v1.4 search (Design_2026-10-26_DeltaH_v1.4_Recipe_and_Search.md): a model of the search, not a version"
POOL_LAYERS = "A,A2,B,P3,P3c"
EPOCH_CAP = 300
CAP_MARGIN = 0.10                          # decision 51: a best epoch within 10 % of the cap means the cap, not the data, stopped it
THREADS = "8"
MAX_GAP_MINUTES = 120                      # the run-spec schema's ceiling; the chain runner prints progress every 30 min
LINES = P.LINES                            # the lines live with the rule that reads them; the rule test of 17 Nov imports them here
SCORE_NOTE = (f"The score is read on the selection set without {', '.join(EXCLUDED_SELECTION_CORES)} ({N_SELECTION - N_EXCLUDED} of "
              f"{N_SELECTION} molecules, §13); the registered score is the same formula on all {N_SELECTION}.")
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


def trainer_argv(cfg: Config, prefix: str, seeds: str, *, selection_split: bool = True, twins: str | None = None) -> list[str]:
    """The trainer command of one configuration: the carried BASE and RECIPE_V11 with the search's values put in their place. Every
    training the search selects on sets the selection set aside; `selection_split=False` trains on the whole pool (the final chain's
    retraining of the winner), and `twins` names a --holdout-twins rule other than the trainer's default (that retraining's)."""
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
    split = ("--selection-split", SELECTION) if selection_split else ()
    twin_rule = ("--holdout-twins", twins) if twins else ()
    return ["{python}", "m05/rungC_train.py", "corpus/molecules", prefix, *argv, *split, *twin_rule, "--sizes", "all",
            "--seeds", seeds, "--threads", THREADS, "--save-model"]


def prefix(cfg: Config, stage: str) -> str:
    return f"{OUT}/E7_rungC_v14{stage}_{cfg.name}"


def train_step(cfg: Config, stage: str, seeds: str, *, selection_split: bool = True, twins: str | None = None) -> dict:
    pre = prefix(cfg, stage)
    return {"kind": "cmd", "label": f"train {cfg.name} ({stage}, seeds {seeds})", "cwd": M05_REL,
            "log": f"{M05_REL}/{pre}.log", "argv": trainer_argv(cfg, pre, seeds, selection_split=selection_split, twins=twins)}


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
    """One seed of one training. `sel` is the trainer's read on the whole selection set (the registered score's set); `scored` holds
    the same read-outs on the selection set without EXCLUDED_SELECTION_CORES, the set the score ranks and decides on since §13. A
    whole-pool training has neither (it trained on the selection set)."""
    sel: dict
    per_molecule: dict
    best_epoch: int | None
    cap: int
    scored: dict


SCORED, REGISTERED = attrgetter("scored"), attrgetter("sel")   # the two sets a seed's read-outs exist on


def trainer_record(pre: str) -> dict:
    """The trainer's record `<prefix>.json`, the prefix relative to module 05."""
    path = M05 / f"{pre}.json"
    if not path.is_file():
        raise SystemExit(f"{pre}.json: no trainer record under module 05")
    return json.loads(path.read_text(encoding="utf-8"))


@dataclass(frozen=True)
class SelectionSets:
    """The selection set as a trainer record names it (`holdout_sel`) and the part of it the score is read on."""
    all_ids: tuple[str, ...]
    scored_ids: tuple[str, ...]


def manifest_names() -> dict[str, str]:
    """Every corpus id → its manifest name (a scaffold core, or `core+substituent`)."""
    with (M05 / "corpus" / "manifest.csv").open(newline="", encoding="utf-8") as f:
        return {r["id"]: r["name"] for r in csv.DictReader(f)}


def selection_sets(holdout_sel: list[str], names: dict[str, str]) -> SelectionSets:
    """The two sets of this search's split; refuses any other count than N_EXCLUDED of N_SELECTION, so that a changed corpus or split
    cannot change the rule unseen."""
    unnamed = [i for i in holdout_sel if i not in names]
    if unnamed:
        raise SystemExit(f"the selection set holds {len(unnamed)} ids without a manifest row ({', '.join(unnamed[:3])})")
    excluded = {i for i in holdout_sel if names[i].split("+")[0] in EXCLUDED_SELECTION_CORES}
    if (len(holdout_sel), len(set(holdout_sel)), len(excluded)) != (N_SELECTION, N_SELECTION, N_EXCLUDED):
        raise SystemExit(f"the selection set holds {len(excluded)} molecules of {', '.join(EXCLUDED_SELECTION_CORES)} among "
                         f"{len(holdout_sel)}; the registered rule (§13) is {N_EXCLUDED} of {N_SELECTION}")
    return SelectionSets(tuple(holdout_sel), tuple(i for i in holdout_sel if i not in excluded))


def ids_file(name: str) -> str:
    return f"{OUT}/selection_{name}.ids"


def write_ids_files(sets: SelectionSets) -> None:
    """The two id lists the evaluator reads, written once; a list that differs from the one on disk is refused (every training of the
    search shares one split)."""
    for name, ids in ((SEL_ALL, sets.all_ids), (SEL_SCORED, sets.scored_ids)):
        path, text = M05 / ids_file(name), "\n".join(ids) + "\n"
        if not path.is_file():
            P.write_atomic(path, text)
        elif path.read_text(encoding="utf-8") != text:
            raise SystemExit(f"{ids_file(name)} differs from this record's selection set — the trainings do not share one split")


def run_evaluator(argv: list[str], log: Path) -> None:
    """One `rungC_eval_saved.py` process in module 05, its output appended to `log`."""
    with open(log, "a", encoding="utf-8") as fh:
        done = subprocess.run(argv, cwd=M05, stdin=subprocess.DEVNULL, stdout=fh, stderr=subprocess.STDOUT, check=False)
    if done.returncode != 0:
        raise SystemExit(f"the selection eval ended with exit {done.returncode} (log {log})")


def selection_eval_prefix(pre: str, seed: int) -> str:
    return f"{pre}_seleval_seed{seed}"


def register_candidates(models: list[str]) -> list[str]:
    """Enter checkpoints (paths relative to module 05) that the model registry does not know as `candidate`, the status
    `chain_runner` gives a chain's models before their evals: the evaluator stops at its first line on an unknown model, also with
    --allow-any-model (decision 55). A model that has a status keeps it. Returns the models entered. The registry's tables
    (`MODELS.md`) are not rebuilt here: that needs every checkpoint of the folder registered (`python m05/model_registry.py`)."""
    new = [M05 / m for m in models if MR.status_of(M05 / m, REGISTRY_STATUS_FILE) is None]
    if new:
        MR.add_candidates(new, REGISTRY_CHAIN, REGISTRY_NOTE, MR.NETWORK_NAMES[0], REGISTRY_STATUS_FILE)
    return [p.relative_to(M05).as_posix() for p in new]


def make_selection_eval(pre: str, seed: int) -> None:
    """Read one stage checkpoint on both selection sets with the evaluator the final chain uses (`--eval-ids-file`, which refuses a
    set the model trained on). The evaluator writes under a temporary prefix; the record is moved into place last, so a record that
    exists is a finished evaluation and a rerun of the read makes only the missing ones."""
    out = selection_eval_prefix(pre, seed)
    step = _eval_step(f"{pre}_model_n*_seed{seed}.pt", f"{out}.tmp", {name: ids_file(name) for name in (SEL_ALL, SEL_SCORED)})
    command = [sys.executable if a == "{python}" else a for a in step["argv"]]
    # the runner's own expansion of a checkpoint pattern; it becomes public there once the live chain, which runs that file, has ended
    argv = chain_runner._resolve(command, M05)
    register_candidates([argv[2]])
    t0 = time.time()
    run_evaluator(argv, M05 / f"{out}.log")
    for suffix in (".md", ".json"):
        (M05 / f"{out}.tmp{suffix}").replace(M05 / f"{out}{suffix}")
    print(f"selection eval {Path(out).name} made in {time.time() - t0:.0f} s", flush=True)   # the read's log grows: the runner's progress


def scored_read(pre: str, seed: int, registered: dict, sets: SelectionSets) -> dict:
    """One seed's read-outs on the scored set, from its selection eval (made here when missing). Checked before use: the record is of
    this checkpoint, each of its two sets holds exactly the molecules it should, and its read on the whole selection set reproduces
    the trainer's own (`registered`) — a second route to the same number, printed for every record."""
    out = selection_eval_prefix(pre, seed)
    if not (M05 / f"{out}.json").is_file():
        make_selection_eval(pre, seed)
    rec = json.loads((M05 / f"{out}.json").read_text(encoding="utf-8"))
    m = CHECKPOINT.fullmatch(Path(str(rec.get("model"))).name)
    if m is None or (m["prefix"], int(m["seed"])) != (Path(pre).name, seed):
        raise SystemExit(f"{out}.json evaluated {rec.get('model')}, not seed {seed} of {pre}")
    for name, ids in ((SEL_ALL, sets.all_ids), (SEL_SCORED, sets.scored_ids)):
        if set(rec.get(name, {}).get("per_molecule", {})) != set(ids):
            raise SystemExit(f"{out}.json: its set {name} is not the {len(ids)} molecules of {ids_file(name)}")
    again, own = score(rec[SEL_ALL]), score(registered)
    print(f"selection eval {Path(out).name}: score on all {N_SELECTION} {again:.4f}, the trainer's {own:.4f}, difference "
          f"{abs(again - own):.1e}", flush=True)
    if abs(again - own) > SEL_REPRODUCTION_TOL:
        raise SystemExit(f"{out}.json does not reproduce the trainer's selection score on all {N_SELECTION}: {again:.4f} against "
                         f"{own:.4f} (tolerance {SEL_REPRODUCTION_TOL:g}). The labels or the model changed between the training and "
                         f"this read, and the stage is not readable on changed labels. The way out (§13): name the changed molecules "
                         f"(the per-molecule read-outs of {out}.json against the trainer record's) and record an amendment; the "
                         f"tolerance is not loosened")
    return rec[SEL_SCORED]


def seed_reads(pre: str) -> dict[int, SeedRead]:
    """Every seed of a trainer record (`<prefix>.json`, one pool size): the trainer's selection read and the read on the scored set."""
    rec = trainer_record(pre)
    if rec.get("selection_split") != SELECTION:
        raise SystemExit(f"{pre}.json was not trained with --selection-split {SELECTION}")
    (entry,) = rec["curve"].values()
    sets = selection_sets(rec["holdout_sel"], manifest_names())
    write_ids_files(sets)
    return {s["seed"]: SeedRead(s["sel"], s["sel"].get("per_molecule", {}), s.get("best_epoch"), rec["epochs"],
                                scored_read(pre, s["seed"], s["sel"], sets)) for s in entry["per_seed"]}


def evaluated_checkpoint(path: Path) -> Path:
    """The checkpoint an eval record names (`rungC_eval_saved.py`: "model", relative to module 05)."""
    if not path.is_file():
        raise SystemExit(f"{path.name}: no eval record — the final chain's eval step has not written it")
    model = json.loads(path.read_text(encoding="utf-8")).get("model")
    if not model:
        raise SystemExit(f"{path.name} names no model")
    return Path(model)


def whole_pool_reads(w: Config, eval_paths: list[Path], tag: str) -> list[SeedRead]:
    """The trainings behind the winner's hold-out evals, one per seed of FINAL_SEEDS, with no selection read (they trained on that set).
    The trainer's record beside the checkpoint an eval names carries a selection split only when one was used. Refused: a checkpoint
    trained with a selection split — the stage checkpoints never saw the selection set's scaffold cores and the carried version did,
    so the promotion would compare the split, not the recipe (§12) — and any checkpoint other than the winner's whole-pool one of that
    seed (at stage `tag`)."""
    expected = Path(prefix(w, tag))
    reads = []
    for seed, path in zip(FINAL_SEEDS, eval_paths, strict=True):
        model = evaluated_checkpoint(path)
        m = CHECKPOINT.fullmatch(model.name)
        if m is None:
            raise SystemExit(f"{path.name} names {model.as_posix()}, not a trainer checkpoint (<prefix>_model_n<N>_seed<S>.pt)")
        rec = trainer_record((model.parent / m["prefix"]).as_posix())
        if rec.get("selection_split") is not None:
            raise SystemExit(f"{path.name} evaluated {model.name}, trained with --selection-split {rec['selection_split']}: the promotion "
                             f"is read on the winner retrained on the whole pool ({expected.name}), not on a stage checkpoint (§12)")
        if (model.parent / m["prefix"], int(m["seed"])) != (expected, seed):
            raise SystemExit(f"{path.name} evaluated {model.as_posix()}, not seed {seed} of {expected.as_posix()}")
        (entry,) = rec["curve"].values()
        best = {s["seed"]: s.get("best_epoch") for s in entry["per_seed"]}
        if seed not in best:
            raise SystemExit(f"{expected.as_posix()}.json holds no seed {seed}")
        reads.append(SeedRead({}, {}, best[seed], rec["epochs"], {}))
    return reads


def score(sel: dict) -> float:
    """The mean of the five read-outs, each over its line: 1.0 = on the lines on average."""
    return P.on_lines({q: _q(sel, q) for q in P.QUANTITIES})


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


def arm(reads: list[SeedRead], read: Callable[[SeedRead], dict]) -> P.Arm:
    """The seeds' read-outs on one of the two sets (SCORED or REGISTERED) as an arm of the no-worsening comparison."""
    return P.arm_from_seeds([{"sel": read(r)} for r in reads], ("sel",))


def seed_mean(reads: list[SeedRead], read: Callable[[SeedRead], dict]) -> float:
    return sum(score(read(r)) for r in reads) / len(reads)


def leaders(configs: list[Config], scores: dict[str, float]) -> list[Config]:
    """The STAGE2_BEST configurations with the lowest score, the control (the list's first) aside."""
    return sorted(configs[1:], key=lambda c: scores[c.name])[:STAGE2_BEST]


def registered_note(names: list[str], names_registered: list[str]) -> str:
    """What the registered score would send to stage 2, against what the scored set sends."""
    if names == names_registered:
        return " It sends the same configurations to stage 2, in the same order."
    if set(names) == set(names_registered):
        return f" It sends the same configurations to stage 2, in another order: {', '.join(names_registered)}."
    return f" **It would send other configurations to stage 2: {', '.join(names_registered)}.**"


def cmd_read1() -> int:
    configs, _ = load_list()
    ctrl = configs[0]
    reads = {c.name: stage1_seeds(c) for c in configs}
    means = {n: seed_mean(rs, SCORED) for n, rs in reads.items()}
    registered = {n: seed_mean(rs, REGISTERED) for n, rs in reads.items()}
    ctrl_arm = arm(reads[ctrl.name], SCORED)
    lines = [f"# v1.4 stage 1 — selection-set scores (seeds {', '.join(str(s) for s in STAGE1_SEEDS)})", "",
             f"| rank | configuration | schedule | score (seed mean) | per seed | registered score (all {N_SELECTION}) | worse than control on "
             "| best epoch / cap |", "|---|---|---|---|---|---|---|---|"]
    for k, c in enumerate(sorted(configs, key=lambda c: means[c.name]), 1):
        rs = reads[c.name]
        worse = "—" if c.name == ctrl.name else ", ".join(P.promotion(P.compare(arm(rs, SCORED), ctrl_arm)).worse) or "—"
        epochs = ", ".join(epoch_note(r, c.schedule) for r in rs)
        per_seed = ", ".join(f"{score(r.scored):.3f}" for r in rs)
        lines.append(f"| {k} | {c.name} | {c.schedule} | {means[c.name]:.3f} | {per_seed} | {registered[c.name]:.3f} | {worse} | "
                     f"{epochs} / {rs[0].cap} |")
    best, best_registered = leaders(configs, means), leaders(configs, registered)
    names, names_registered = [c.name for c in best], [c.name for c in best_registered]
    lines += ["", f"Stage 2: {', '.join(names)} and the control, seed {STAGE2_SEED}. Two seeds: the no-worsening column "
              "informs, stage 2 decides on three.", "",
              SCORE_NOTE + registered_note(names, names_registered)]
    _write_report("read1", lines, {"scores": means, "registered_scores": registered,
                                   "seed_scores": {n: [score(r.scored) for r in rs] for n, rs in reads.items()},
                                   "stage2": names, "stage2_registered": names_registered})
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


def stage2_rows(arms: dict[str, list[SeedRead]], by_name: dict[str, Config], ctrl_name: str,
                read: Callable[[SeedRead], dict]) -> dict[str, Stage2]:
    """Every arm's three seeds against the control's, on one of the two sets (SCORED or REGISTERED)."""
    ctrl_arm = arm(arms[ctrl_name], read)
    return {n: Stage2(n, tuple(score(read(r)) for r in rs),
                      P.promotion(P.compare(arm(rs, read), ctrl_arm)).worse if n != ctrl_name else (),
                      any(at_cap(r, by_name[n].schedule) for r in rs)) for n, rs in arms.items()}


def cmd_read2() -> int:
    configs, _ = load_list()
    chosen = json.loads((M05 / OUT / "read1.json").read_text(encoding="utf-8"))["stage2"]
    ctrl = configs[0]
    by_name = {c.name: c for c in configs}
    arms = {n: three_seeds(by_name[n]) for n in [ctrl.name, *chosen]}
    rows, rows_registered = stage2_rows(arms, by_name, ctrl.name, SCORED), stage2_rows(arms, by_name, ctrl.name, REGISTERED)
    name, reason = winner([rows[n] for n in chosen], rows[ctrl.name])
    name_registered, _ = winner([rows_registered[n] for n in chosen], rows_registered[ctrl.name])
    if rows[name].at_cap:
        raise SystemExit(f"{name}: a best epoch within {CAP_MARGIN:.0%} of the cap — rerun it at a higher cap before it can win (decision 51)")
    lines = ["# v1.4 stage 2 — three seeds on the selection set", "",
             f"| configuration | score (mean ± SE) | seed {STAGE2_SEED} alone | registered score, all {N_SELECTION} (mean ± SE) "
             "| worse than control on | best epochs |", "|---|---|---|---|---|---|"]
    lines += [f"| {r.name} | {r.mean:.3f} ± {r.se:.3f} | {r.scores[-1]:.3f} | {rows_registered[r.name].mean:.3f} ± "
              f"{rows_registered[r.name].se:.3f} | {', '.join(r.worse) or '—'} | "
              f"{', '.join(epoch_note(x, by_name[r.name].schedule) for x in arms[r.name])} |" for r in rows.values()]
    lines += ["", f"**Winner: {name}** — {reason}.", "",
              SCORE_NOTE + " Among these candidates, which stage 1 chose on the scored set, the winner rule on the registered score "
              + ("gives the same winner." if name == name_registered else f"**would give another winner: {name_registered}.**"), "",
              f"Two of a candidate's three seeds are the ones stage 1 chose it on, and the control was not chosen: the mean flatters a "
              f"candidate. Seed {STAGE2_SEED} alone is the unselected comparison, and the hold-out promotion of read3 is the guard.", "",
              cation_line(arms[name])]
    control_won = name == ctrl.name
    if control_won:
        lines += ["", control_stands(ctrl)]
    _write_report("read2", lines, {"winner": name, "reason": reason, "winner_registered": name_registered,
                                   "control_won": control_won, "final_chain": None if control_won else FINAL_CHAIN,
                                   "rows": {n: asdict(r) for n, r in rows.items()},
                                   "rows_registered": {n: asdict(r) for n, r in rows_registered.items()}})
    if not control_won:
        _write_final_chain(by_name[name])
    print("\n".join(lines))
    return 0


FINAL_CHAIN = "probes/runs/v14_final.json"   # relative to the plan


def control_stands(ctrl: Config) -> str:
    """§14 item 3: when the control wins, its whole-pool models are already the final models, so no final chain is written (it would
    train the carried recipe again as s3win and read3 would compare the carried version with a copy of itself). The registry's carried
    version must be that whole-pool training; the line read2 prints says so."""
    carried = carried_version()
    trained = {checkpoint_prefix(m) for m in carried.models}
    if trained != {prefix(ctrl, CLEAN_TAG)}:
        raise SystemExit(f"the control won, but the carried version {carried.version} is {sorted(trained)}, not the control's whole-pool "
                         f"training {prefix(ctrl, CLEAN_TAG)}: §14 item 3 does not apply and nothing is decided here")
    return (f"**The control stands: version {carried.version} stays carried.** By §14 item 3 the control's whole-pool models are already "
            f"the final models: the carried version is the control ({ctrl.name}) trained on the whole pool (chain {carried.chain}; "
            f"{', '.join(carried.models)}). No final chain is written, and read3 has nothing to read.")


def _eval_step(model: str, out: str, sets: dict[str, str] | None = None) -> dict:
    """One evaluator command; `sets` ({name: id file}) adds explicit test sets beside the two hold-outs."""
    extra = [x for name, file in (sets or {}).items() for x in ("--eval-ids-file", f"{name}={file}")]
    return {"kind": "cmd", "label": f"eval {Path(out).name}", "cwd": M05_REL, "log": f"{M05_REL}/{out}.log",
            "glob_args": True, "argv": ["{python}", "../../probes/rungC_eval_saved.py", model, out, "--use-analytic", "--threads", THREADS,
                                        "--allow-any-model", "--holdout-b-file", chain_runner.HOLDOUT_B, *extra]}


def winner_models(w: Config) -> list[str]:
    """The winner's whole-pool checkpoints, one per seed of FINAL_SEEDS (a pattern: the file name carries the pool size)."""
    return [f"{prefix(w, FINAL_TAG)}_model_n*_seed{s}.pt" for s in FINAL_SEEDS]


def _write_final_chain(w: Config) -> None:
    """The other target with the selection split (the target check is a selection-set read), the winner on the whole pool without any
    hold-out twin of any charge (the models the promotion is read on) on the hold-outs and the clean eight, read3. The carried version
    is not evaluated here: read3 reads it in the evals its own chain made (`carried_version`)."""
    other = replace(w, target=next(t for t in TARGETS if t != w.target))
    for pre in (prefix(w, FINAL_TAG), prefix(other, "s3other")):
        if (M05 / f"{pre}.json").is_file():
            raise SystemExit(f"{pre}.json exists: the final chain would train over a record on disk")
    seeds = ",".join(str(s) for s in FINAL_SEEDS)
    steps = [train_step(other, "s3other", seeds), train_step(w, FINAL_TAG, seeds, selection_split=False, twins=CLEAN_TWINS),
             read_step("register")]
    clean = {CLEAN_A: chain_runner.HOLDOUT_A_CLEAN}
    steps += [_eval_step(m, f"{OUT}/eval_winner_seed{s}", clean) for s, m in zip(FINAL_SEEDS, winner_models(w), strict=True)]
    steps.append(read_step("read3"))
    about = (f"v1.4 final: {w.name} with the other target and {w.name} on the whole pool (three seeds each), the whole-pool models "
             "read on the hold-outs, read3 against the carried version")
    write_new(PLAN / FINAL_CHAIN, chain("V14F", about, steps, [f"{M05_REL}/{OUT}/read3.json"]))
    write_new(PLAN / "probes" / "runspecs" / "v14_final.json",
              runspec("v14_final", "V14F", "v1.4 final: target check, whole-pool retraining, hold-out reads, promotion",
                      len(FINAL_SEEDS) * HOURS[w.schedule] * (1 + TRAINED_WHOLE / TRAINED_WITH_SPLIT) + 1.0,
                      f"six trainings at the winner's schedule: three with the other target, three on the whole pool at "
                      f"{TRAINED_WHOLE}/{TRAINED_WITH_SPLIT} of that time; three hold-out evals ≈ 10 min and three selection evals"))


def holdout_values(paths: list[Path], hold: str, molecule: str | None = None) -> list[float]:
    """The corrected ω rms of each eval record on one hold-out: the hold-out's own, or one of its molecules'."""
    out = []
    for p in paths:
        read = json.loads(p.read_text(encoding="utf-8")).get(hold, {})
        if molecule is not None:
            read = read.get("per_molecule", {}).get(molecule, {})
        if read.get("corrected_freq_rms") is None:
            raise SystemExit(f"{p.name}: no corrected_freq_rms of {molecule or 'the hold-out'} on hold-out ({hold})")
        out.append(read["corrected_freq_rms"])
    return out


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def prediction_read(winner_evals: list[Path], carried_evals: list[Path], *, a_set: str = "a") -> tuple[str, dict]:
    """§12's prediction as one report line and a record: the prediction molecule's corrected ω rms on hold-out (a), per seed and the
    mean, for the whole-pool winner and the carried version; PASS when the winner's mean is at most PREDICTION_LINE. `a_set` names
    hold-out (a) in the eval records: the ten, or the clean eight."""
    new, old = (holdout_values(paths, a_set, PREDICTION_MOLECULE) for paths in (winner_evals, carried_evals))
    passed = mean(new) <= PREDICTION_LINE

    def shown(values: list[float]) -> str:
        return f"{', '.join(f'{v:.2f}' for v in values)} (mean {mean(values):.2f})"
    line = (f"§12's prediction — biphenylene ({PREDICTION_MOLECULE}) on hold-out (a), corrected ω rms in cm⁻¹ per seed: winner "
            f"{shown(new)}, carried {shown(old)}; the winner's mean at most {PREDICTION_LINE:g}: "
            + ("**PASS**." if passed else "**FAIL** — the promotion is read as it is; the cause named in §12 is not the whole story and "
               "is looked at before any further amendment."))
    return line, {"molecule": PREDICTION_MOLECULE, "winner": new, "carried": old, "line": PREDICTION_LINE, "passed": passed}


def expectation_read(winner_evals: list[Path], carried_evals: list[Path], *, a_set: str = "a") -> tuple[str, dict]:
    """§12's expectation as one report line and a record: the whole-pool winner's corrected ω rms (mean of the seeds) below the carried
    version's on hold-out (b) and not above it on hold-out (a). §12 stated it when the carried version was 1.3, trained on fewer
    molecules; read-data still reads it against 1.3, while read3's carried side trained on the same whole pool as the winner, so there
    it no longer tests more data. It decides nothing; the promotion rule does. `a_set` names hold-out (a) in the eval records: the ten,
    or the clean eight."""
    b_new, b_old, a_new, a_old = (mean(holdout_values(paths, hold)) for hold in ("b", a_set) for paths in (winner_evals, carried_evals))
    b_held, a_held = b_new < b_old, a_new <= a_old
    line = (f"§12's expectation — corrected ω rms in cm⁻¹, mean of the seeds: hold-out (b) winner {b_new:.2f} against carried {b_old:.2f} "
            f"(expected below: {'held' if b_held else '**did not hold**'}); hold-out (a) winner {a_new:.2f} against carried {a_old:.2f} "
            f"(expected not above: {'held' if a_held else '**did not hold** — (a) is looked at per molecule before the promotion is decided'})."
            " The expectation decides nothing; the promotion rule does.")
    return line, {"b": {"winner": b_new, "carried": b_old, "held": b_held}, "a": {"winner": a_new, "carried": a_old, "held": a_held}}


def target_lines(w: Config, other: Config, check: P.Promotion, registered: P.Promotion) -> list[str]:
    """The target check on the scored set, which decides, and beside it on the registered set (all of the selection set). It is a
    selection screen, not a promotion, so it keeps the rule of 26 Oct (decision 57 as amended on 17 Nov: the screens keep their
    registered score); a choice it does not hand to the user is still printed with both sides."""
    def sides(c: P.Promotion) -> str:
        return f"better on {', '.join(c.better) or 'none'}, worse on {', '.join(c.worse) or 'none'}"
    if not check.better and not check.worse:
        verdict = "**better on no read-out and worse on none — the target choice stands**"
    else:
        verdict = sides(check) + (" — **the other target passes the no-worsening rule: the choice goes to the user**" if check.promoted
                                  else " — the choice stands")
    return [f"Winner {w.name} ({w.target}); the other target ({other.target}) on the selection set without "
            f"{', '.join(EXCLUDED_SELECTION_CORES)} (§13): {verdict}", "",
            f"On the registered set (all {N_SELECTION}): {sides(registered)} — "
            + ("the same decision." if check.promoted == registered.promoted else "**the other decision.**")]


def final_pair() -> tuple[Config, Config]:
    """(read2's winner, the same configuration with the other target). A control that won has no final chain: refused."""
    listed = load_list()[0]
    configs = {c.name: c for c in listed}
    w = configs[json.loads((M05 / OUT / "read2.json").read_text(encoding="utf-8"))["winner"]]
    if w.name == listed[0].name:
        raise SystemExit(f"read2's winner is the control ({w.name}): by §14 item 3 its whole-pool models are the carried version, read2 "
                         "wrote no final chain, and there is nothing to register or read here")
    return w, replace(w, target=next(t for t in TARGETS if t != w.target))


def cmd_register() -> int:
    """The final chain's step between its trainings and its evals: the six new checkpoints into the model registry."""
    w, other = final_pair()
    patterns = [*winner_models(w), *(f"{prefix(other, 's3other')}_model_n*_seed{s}.pt" for s in FINAL_SEEDS)]
    added = register_candidates(chain_runner._resolve(patterns, M05))               # the runner's expansion, as in make_selection_eval
    print(f"registered as candidate: {', '.join(added) or 'none (all six have a status)'}")
    return 0


def cmd_seleval(only: str | None) -> int:
    """Make the selection evals that are missing for every stage training that has finished (its record exists), and check every one:
    a line per eval with its seconds and its difference to the trainer's score. A training without a record is skipped — the reads
    refuse an incomplete stage, this does not. Exit 1 when an eval or its check failed."""
    configs, _ = load_list()
    if only is not None and only not in {c.name for c in configs}:
        raise SystemExit(f"--only {only}: not a configuration of the frozen list")
    prefixes = [prefix(c, tag) for c in configs if only in (None, c.name) for tag in (*STAGE1_TAGS.values(), "s2", "s3other")]
    finished = [pre for pre in prefixes if (M05 / f"{pre}.json").is_file()]
    failed = []
    for pre in finished:
        try:
            seed_reads(pre)
        except SystemExit as e:
            failed.append(pre)
            print(f"FAILED {Path(pre).name}: {e}", flush=True)
    print(f"selection evals: {len(finished)} finished trainings read, {len(failed)} failed, {len(prefixes) - len(finished)} without a record")
    return 1 if failed else 0


def require_below_cap(w: Config, full: list[SeedRead]) -> None:
    """Decision 51 on whole-pool trainings: no promotion is read from a seed the cap stopped."""
    if any(at_cap(r, w.schedule) for r in full):
        raise SystemExit(f"{w.name} on the whole pool: a best epoch within {CAP_MARGIN:.0%} of the cap of {EPOCH_CAP} — no promotion is "
                         f"read from it (decision 51). The way out (§12): a recorded amendment and a whole-pool rerun of the same recipe "
                         f"at a higher cap ({RERUN_CAP} epochs), nothing else changed")


def stated_lines(expectation: dict, prediction: dict) -> list[str]:
    """§12's and §14's three statements with PASS or FAIL, from the records `expectation_read` and `prediction_read` give for
    hold-out (a)'s clean set."""
    def verdict(passed: bool) -> str:
        return "**PASS**" if passed else "**FAIL**"

    def shown(values: list[float]) -> str:
        return f"{', '.join(f'{v:.2f}' for v in values)} (mean {mean(values):.2f})"
    b, a = expectation["b"], expectation["a"]
    return ["Stated before any whole-pool model existed (§12, §14), as corrected ω rms in cm⁻¹, hold-out (a) on its eight clean "
            "molecules. They decide nothing; the promotion does.", "",
            f"- hold-out (b) below the carried version on the mean of three seeds: {b['winner']:.2f} against {b['carried']:.2f} — "
            f"{verdict(b['held'])}",
            f"- hold-out (a) not above the carried version on the mean of three seeds: {a['winner']:.2f} against {a['carried']:.2f} — "
            f"{verdict(a['held'])}",
            f"- biphenylene ({prediction['molecule']}) on hold-out (a) at most {prediction['line']:g} on the mean of three seeds: the new "
            f"models {shown(prediction['winner'])}, the carried version {shown(prediction['carried'])} — {verdict(prediction['passed'])}"]


@dataclass(frozen=True)
class DataArm:
    """One reading of read-data (§14): which whole-pool trainings are read against the carried version, and where the read goes."""
    tag: str                     # the trainings' stage tag
    evals: str                   # the new models' eval records: out/v14/eval_<evals>_seed<S>.json
    report: str                  # out/v14/<report>.md and .json
    holdout_twins: str | None    # the trainer setting the trainings must have recorded; None: not checked (the data arm, as before)
    title: str                   # what the report's title adds
    promoted: str                # the report's meaning line when the promotion holds
    not_promoted: str            # and when it does not


NOT_PROMOTED = "nothing is carried, and the cause is looked at per molecule before anything else is decided."
RULE_BY = "by decision 57 as amended on 17 November"
RULE_NOTE = ("decision 57 as amended on 17 November: the composite below the carried version's beyond the Student-t line, and no "
             "read-out worse beyond two SE")
CLEAN_BY = ("By §14's addition of 17 November (the clean arm replaces the data arm, whose hold-out (a) was not clean for benzene)")
DATA_ARMS = {"data": DataArm(FULL_TAG, "data", "read_data", None, "", f"By §14, {RULE_BY}, these three models are version 1.4.",
                             f"By §14, {RULE_BY}, {NOT_PROMOTED}"),
             "clean": DataArm(CLEAN_TAG, "clean", "read_clean", CLEAN_TWINS, ", clean arm (no hold-out twin of any charge)",
                              f"{CLEAN_BY}, {RULE_BY}, these three models are version 1.4.", f"{CLEAN_BY}, {RULE_BY}, {NOT_PROMOTED}")}
BENZENE_CATION = "P3c_8448043181"          # hold-out (a)'s benzene as a radical cation: the twin the clean training exists to drop (TASKS 253)
TEN_NOTE = ("The eight decide (§14's addition of 16 Nov): the carried version trained on twins of two of the ten (2-naphthoic acid and "
            "benzonitrile, TASKS 157), so on the ten the comparison favours it on two molecules it has seen.")


V14_TEN_NOTE = ("The eight decide (§14's addition of 16 Nov). Version 1.4 and the winner both trained without any hold-out "
                "molecule's twin of any charge, so neither side trained on a twin of any of the ten; they are printed as before.")


def shown_value(v: object) -> str:
    text = repr(v)
    return text if len(text) <= 60 else f"{text[:57]}..."


def checkpoint_args(pre: str, seed: int) -> dict:
    """The validated trainer config (`args`) that the one checkpoint of `seed` under the prefix `pre` saved."""
    import torch  # only the clean arm's recipe check opens a checkpoint; every other read of the search runs without torch

    found = sorted((M05 / pre).parent.glob(f"{Path(pre).name}_model_n*_seed{seed}.pt"))
    if len(found) != 1:
        raise SystemExit(f"{pre}: {len(found)} checkpoints of seed {seed}, not one")
    return dict(torch.load(found[0], map_location="cpu", weights_only=False)["args"])


def recipe_differences(w: Config, arm: DataArm) -> list[str]:
    """Seed by seed, every saved setting in which the arm's checkpoints differ from the data arm's, beside the twin rule and the
    run's own fields — `setting_differences`, as release_checks' check 1 compares two trainings (absent settings by the table)."""
    out = []
    for seed in FINAL_SEEDS:
        pairs, _, _ = setting_differences(checkpoint_args(prefix(w, FULL_TAG), seed), checkpoint_args(prefix(w, arm.tag), seed),
                                          {*RUN_ONLY, "holdout_twins"})
        out += [f"seed {seed}: {k}: {shown_value(old)} -> {shown_value(new)}" for k, (old, new) in pairs.items()]
    return out


def require_twin_rule(pre: str, setting: str) -> None:
    """The trainer record `<pre>.json` trained under the twin rule `setting`, and benzene's radical cation left its pool."""
    rec = trainer_record(pre)
    found = rec.get("holdout_twins")
    if found != setting:
        raise SystemExit(f"{pre}.json was trained with holdout_twins {found!r}, not {setting!r}: the promotion is read on the recipe "
                         f"trained without any hold-out molecule's twin of any charge (--holdout-twins {setting}, TASKS 253)")
    if BENZENE_CATION not in rec.get("holdout_twins_dropped", []):
        raise SystemExit(f"{pre}.json did not drop {BENZENE_CATION}, benzene's radical cation, from its pool: its hold-out (a) is not "
                         "clean for benzene (TASKS 253)")


def require_clean_training(w: Config, arm: DataArm) -> None:
    """The clean arm's training is the data arm's with the twin rule `arm.holdout_twins` and nothing else changed."""
    require_twin_rule(prefix(w, arm.tag), arm.holdout_twins)
    diffs = recipe_differences(w, arm)
    if diffs:
        raise SystemExit(f"{prefix(w, arm.tag)}'s checkpoints differ from {prefix(w, FULL_TAG)}'s, the data arm's training, in "
                         f"{len(diffs)} saved setting(s) beside the twin rule ({'; '.join(diffs)}): the clean arm reads the carried "
                         "recipe with the twin rule alone changed")


def clean_ids() -> list[str]:
    """Hold-out (a)'s clean ids as the evaluator reads the list (`rungC_eval_saved.read_ids`: one per line, '#' comments), sorted."""
    lines = (M05 / chain_runner.HOLDOUT_A_CLEAN).read_text(encoding="utf-8").splitlines()
    return sorted(s.strip() for s in lines if s.strip() and not s.startswith("#"))


def require_clean_set(paths: list[Path]) -> None:
    """Every eval record holds hold-out (a)'s clean set on exactly the ids of its list (none dropped, none added) and hold-out (b) on
    the frozen list: the promotion is read on both."""
    wanted = clean_ids()
    for path in paths:
        rec = json.loads(path.read_text(encoding="utf-8"))
        if CLEAN_A not in rec:
            raise SystemExit(f"{path.name} holds no set {CLEAN_A} (hold-out (a)'s eight clean molecules): the evals of chains v14_data and "
                             f"v14_final carry it (--eval-ids-file {CLEAN_A}=…), an older record does not, and the promotion is read on "
                             "it (§14)")
        read = sorted(rec[CLEAN_A].get("per_molecule", {}))
        missing, extra = sorted(set(wanted) - set(read)), sorted(set(read) - set(wanted))
        if missing or extra or rec[CLEAN_A].get("dropped"):
            raise SystemExit(f"{path.name}: its set {CLEAN_A} holds {len(read)} molecules, not the {len(wanted)} of "
                             f"{chain_runner.HOLDOUT_A_CLEAN} (missing {missing}, extra {extra}, dropped {rec[CLEAN_A].get('dropped', [])})")
        if rec.get("holdout_b_file") != chain_runner.HOLDOUT_B:
            raise SystemExit(f"{path.name} read hold-out (b) on {rec.get('holdout_b_file')!r}, not the frozen list {chain_runner.HOLDOUT_B}")


def ten_section(new_evals: list[Path], old_evals: list[Path], label: str, note: str = TEN_NOTE) -> tuple[list[str], dict]:
    """(the report's lines, the record) of hold-out (a) on all ten molecules, printed beside the promotion and deciding nothing;
    `note` says why the eight decide."""
    new_ten, carried_ten = P.load_eval_arm(new_evals), P.load_eval_arm(old_evals)
    comps_ten = P.compare(new_ten, carried_ten)
    promo_ten = P.amended_promotion(new_ten, carried_ten)
    lines = ["## Beside it, deciding nothing: hold-out (a) on all ten molecules", "", note,
             "", *P.comparison_table(new_ten, carried_ten, comps_ten, label, "carried"), "",
             f"On the ten the same rule would read: {'promoted' if promo_ten.promoted else 'not promoted'}.", "", *P.amended_lines(promo_ten)]
    return lines, {"promotion": asdict(promo_ten), "comparisons": [asdict(c) for c in comps_ten]}


def promotion_lines(promo: P.AmendedPromotion, verdict: str, tail: str) -> list[str]:
    """The decision line (`tail` follows it), then the amended rule's two conditions and the rule of 26 Oct beside them."""
    return [f"**Promotion: {verdict}** ({RULE_NOTE}).{tail}", "", *P.amended_lines(promo)]


def pool_note(w: Config, arm: DataArm) -> str:
    """What the report says of the pool beside 'the whole pool': nothing for the data arm, the molecules that left it for the clean."""
    if arm.holdout_twins is None:
        return ""
    dropped = trainer_record(prefix(w, arm.tag))["holdout_twins_dropped"]
    return (f" without any hold-out molecule's twin of any charge (--holdout-twins {arm.holdout_twins}, TASKS 253: {len(dropped)} pool "
            f"molecules left it, {', '.join(dropped)})")


def data_arms(arm: DataArm = DATA_ARMS["data"]) -> tuple[Config, list[SeedRead], list[Path], list[Path]]:
    """§14's two sides, checked: (the control, its three whole-pool trainings of `arm`, their hold-out evals, the carried version's
    evals). The new models pass `whole_pool_reads` and the cap rule as read3's winner does, and the arm's twin setting when it names
    one; each carried eval must name the frozen list's carried checkpoint of its seed; every eval must hold hold-out (a)'s clean set,
    which the promotion is read on."""
    configs, carried_models = load_list()
    new_evals, old_evals = ([M05 / f"{OUT}/eval_{who}_seed{s}.json" for s in FINAL_SEEDS] for who in (arm.evals, "carried_data"))
    full = whole_pool_reads(configs[0], new_evals, arm.tag)
    if arm.holdout_twins is not None:
        require_clean_training(configs[0], arm)
    require_below_cap(configs[0], full)
    for path, model in zip(old_evals, carried_models, strict=True):
        if evaluated_checkpoint(path).as_posix() != model:
            raise SystemExit(f"{path.name} evaluated {evaluated_checkpoint(path).as_posix()}, not the carried version's {model}")
    require_clean_set([*new_evals, *old_evals])
    return configs[0], full, new_evals, old_evals


def cmd_read_data(replace_record: bool, arm_name: str = "data") -> int:
    """§14: the carried recipe on the whole pool against the carried version, by the registered promotion — read3's calls on the six
    evals of chain v14_data, with hold-out (a) read on its eight clean molecules (§14's dated addition) and the ten printed beside
    them; the clean arm reads the same recipe trained without any hold-out twin of any charge (TASKS 253). It writes its report and
    carries nothing: no registry entry changes here."""
    arm = DATA_ARMS[arm_name]
    base = M05 / OUT / arm.report
    on_record = [p.name for p in (base.with_suffix(".md"), base.with_suffix(".json")) if p.is_file()]
    if on_record and not replace_record:
        raise SystemExit(f"{' and '.join(on_record)} exist under {OUT}: the read is on record. --replace reads again and writes over it")
    w, full, new_evals, old_evals = data_arms(arm)
    new, carried = (P.load_eval_arm(paths, holdouts=(CLEAN_A, "b")) for paths in (new_evals, old_evals))
    comps = P.compare(new, carried)
    promo = P.amended_promotion(new, carried)
    ten_lines, ten = ten_section(new_evals, old_evals, "v1.4 candidate")
    _, expectation = expectation_read(new_evals, old_evals, a_set=CLEAN_A)
    _, prediction = prediction_read(new_evals, old_evals, a_set=CLEAN_A)
    meaning = arm.promoted if promo.promoted else arm.not_promoted
    lines = [f"# v1.4 on the data{arm.title} — the promotion read (design note §14)", "",
             f"The new models are the carried recipe ({w.name}) trained on the whole pool{pool_note(w, arm)} (seeds "
             f"{', '.join(str(s) for s in FINAL_SEEDS)}; "
             f"best epochs {', '.join(epoch_note(r, w.schedule) for r in full)} / {full[0].cap}); the carried version is the frozen "
             "list's three checkpoints, read again on the same hold-outs.", "",
             f"## The promotion: hold-out (a) on its eight clean molecules ({CLEAN_A}), and hold-out (b)",
             "", *P.comparison_table(new, carried, comps, "v1.4 candidate", "carried"), "",
             *promotion_lines(promo, "promoted" if promo.promoted else "not promoted",
                              f" {meaning} This read carries nothing itself and changes no registry entry."), "", *ten_lines,
             "", "## What was stated beforehand", "", *stated_lines(expectation, prediction), "", DATA_LICENCE_NOTE]
    if on_record:
        print(f"replacing the read on record ({' and '.join(on_record)})", flush=True)
    _write_report(arm.report, lines, {"models": w.name, "trained_on": "whole pool", "best_epochs": [r.best_epoch for r in full],
                                      **({"arm": arm_name, "holdout_twins": arm.holdout_twins} if arm.holdout_twins else {}),
                                      "decided_on": [CLEAN_A, "b"], "rule": RULE_NOTE, "promotion": asdict(promo), "meaning": meaning,
                                      "expectation": expectation, "prediction": prediction, "comparisons": [asdict(c) for c in comps],
                                      "on_the_ten_deciding_nothing": ten})
    print("\n".join(lines))
    return 0


@dataclass(frozen=True)
class CarriedVersion:
    """The version read3 reads the winner against: the registry's carried measurement networks, one per seed, and their evals."""
    version: str
    chain: str
    models: tuple[str, ...]      # relative to module 05, seeds FINAL_SEEDS in order
    evals: tuple[Path, ...]


CARRIED_EVALS = DATA_ARMS["clean"].evals       # v1.4's evals, made by chain v14_clean: out/v14/eval_clean_seed<S>.json


def carried_version() -> CarriedVersion:
    """§14: the search's winner is read against the carried version — 1.4 since 17 Nov 2026 (chain v14_clean) — and not the frozen
    list's carried models (chain 35, v1.3), which the registration named when the search began; the list is not rewritten, the report
    states the substitution. The checkpoints are the model registry's carried measurement networks (`model_registry.carried_keys`),
    one per seed of FINAL_SEEDS, of one version and chain, trained under the twin rule CLEAN_TWINS; their evals are chain v14_clean's
    and must each name the carried checkpoint of their seed."""
    status = MR.read_status(REGISTRY_STATUS_FILE or MR.STATUS_FILE)
    keys = MR.carried_keys(status, MR.NETWORK_NAMES[0], MR.NK.MEASUREMENT)
    by_seed: dict[int, list[str]] = {}
    for key in keys:
        m = CHECKPOINT.fullmatch(Path(key).name)
        if m is None:
            raise SystemExit(f"the registry's carried checkpoint {key} is not a trainer checkpoint (<prefix>_model_n<N>_seed<S>.pt)")
        by_seed.setdefault(int(m["seed"]), []).append(key)
    if sorted(by_seed) != list(FINAL_SEEDS) or any(len(v) != 1 for v in by_seed.values()):
        raise SystemExit(f"the model registry's carried {MR.NETWORK_NAMES[0]} measurement networks are {keys or 'none'}: read3 reads the "
                         f"winner against one per seed {', '.join(map(str, FINAL_SEEDS))}")
    picked = [by_seed[s][0] for s in FINAL_SEEDS]
    unnamed = [k for k in picked if not status[k].get("chain")]
    if unnamed:
        raise SystemExit(f"the registry's carried checkpoints {unnamed} name no chain: read3 states which chain it reads against")
    versions = {(str(status[k]["version"]), str(status[k]["chain"])) for k in picked}
    if len(versions) != 1:
        raise SystemExit(f"the registry's carried checkpoints {picked} are of {len(versions)} versions or chains: {sorted(versions)}")
    models = tuple(f"{MR.OUT.name}/{k}" for k in picked)
    for model in models:
        require_twin_rule(checkpoint_prefix(model), CLEAN_TWINS)
    evals = tuple(M05 / f"{OUT}/eval_{CARRIED_EVALS}_seed{s}.json" for s in FINAL_SEEDS)
    for path, model in zip(evals, models, strict=True):
        if evaluated_checkpoint(path).as_posix() != model:
            raise SystemExit(f"{path.name} evaluated {evaluated_checkpoint(path).as_posix()}, not the carried version's {model}")
    ((version, chain_name),) = versions
    return CarriedVersion(version, chain_name, models, evals)


def checkpoint_prefix(model: str) -> str:
    """The trainer prefix of a checkpoint path (`<prefix>_model_n<N>_seed<S>.pt`), relative to module 05 as the path is."""
    m = CHECKPOINT.fullmatch(Path(model).name)
    if m is None:
        raise SystemExit(f"{model} is not a trainer checkpoint (<prefix>_model_n<N>_seed<S>.pt)")
    return (Path(model).parent / m["prefix"]).as_posix()


def substitution_line(carried: CarriedVersion, frozen: list[str]) -> str:
    """The report's statement that read3 reads the winner against the carried version, not the frozen list's carried models."""
    return (f"The carried side is version {carried.version} (chain {carried.chain}; {', '.join(carried.models)}), as the model registry "
            f"carries it, read in its own chain's evals ({', '.join(p.name for p in carried.evals)}) — in place of the frozen list's "
            f"carried models ({', '.join(frozen)}), named when the search was registered and not rewritten (§14: the winner is read "
            f"against the carried version, {carried.version}). Both sides trained on the whole pool without any hold-out molecule's "
            "twin of any charge, so §12's expectation, stated against the frozen list's carried models, no longer tests more data here; "
            "it is printed as before.")


def final_evals(w: Config) -> tuple[list[SeedRead], list[Path], CarriedVersion]:
    """read3's checked inputs: (the winner's whole-pool trainings, their hold-out evals, the carried version with its evals). The
    trainings passed `whole_pool_reads`, the twin rule CLEAN_TWINS and the cap rule; every eval holds the clean set exactly and (b) on
    the frozen list (§14's addition of 16 Nov: hold-out (a) decides on its clean eight, the ten are printed beside them)."""
    evals = [M05 / f"{OUT}/eval_winner_seed{s}.json" for s in FINAL_SEEDS]
    full = whole_pool_reads(w, evals, FINAL_TAG)
    require_twin_rule(prefix(w, FINAL_TAG), CLEAN_TWINS)
    require_below_cap(w, full)
    carried = carried_version()
    require_clean_set([*evals, *carried.evals])
    return full, evals, carried


def cmd_read3() -> int:
    w, other = final_pair()
    w_reads, o_by_seed = three_seeds(w), seed_reads(prefix(other, "s3other"))
    o_reads = [o_by_seed[s] for s in FINAL_SEEDS]
    target_check = P.promotion(P.compare(arm(o_reads, SCORED), arm(w_reads, SCORED)))
    target_registered = P.promotion(P.compare(arm(o_reads, REGISTERED), arm(w_reads, REGISTERED)))
    full, new_evals, version = final_evals(w)
    old_evals = version.evals
    new, carried = (P.load_eval_arm(paths, holdouts=(CLEAN_A, "b")) for paths in (new_evals, old_evals))
    comps = P.compare(new, carried)
    promo = P.amended_promotion(new, carried)
    ten_lines, ten = ten_section(new_evals, old_evals, "v1.4 winner", V14_TEN_NOTE)
    expectation_line, expectation = expectation_read(new_evals, old_evals, a_set=CLEAN_A)
    prediction_line, prediction = prediction_read(new_evals, old_evals, a_set=CLEAN_A)
    lines = ["# v1.4 final read", "", *target_lines(w, other, target_check, target_registered),
             "", f"The winner's models below are {w.name} retrained on the whole pool, selection set included, without any hold-out "
             f"molecule's twin of any charge (--holdout-twins {CLEAN_TWINS}, TASKS 253; seeds "
             f"{', '.join(str(s) for s in FINAL_SEEDS)}; best epochs {', '.join(epoch_note(r, w.schedule) for r in full)} / {full[0].cap}): "
             "the selection split had taken every derivative of biphenylene, a hold-out (a) molecule, out of the training pool, and the "
             "carried version, trained on the whole pool with the selection set (§14), trained on them. Their selection-set scores are "
             "not shown: they trained on that set.",
             "", substitution_line(version, load_list()[1]), "",
             f"## The promotion: hold-out (a) on its eight clean molecules ({CLEAN_A}), and hold-out (b)", "",
             *P.comparison_table(new, carried, comps, "v1.4 winner", "carried"), "",
             *promotion_lines(promo, f"promoted over version {version.version}" if promo.promoted else "not promoted", ""), "",
             *ten_lines, "",
             expectation_line, "", prediction_line]
    _write_report("read3", lines, {"winner": w.name, "winner_trained_on": "whole pool", "winner_best_epochs": [r.best_epoch for r in full],
                                   "winner_holdout_twins": CLEAN_TWINS, "decided_on": [CLEAN_A, "b"], "rule": RULE_NOTE,
                                   "carried": {"version": version.version, "chain": version.chain, "models": version.models,
                                               "evals": [p.name for p in version.evals], "in_place_of": load_list()[1]},
                                   "target_check": asdict(target_check), "target_check_registered": asdict(target_registered),
                                   "promotion": asdict(promo), "expectation": expectation, "prediction": prediction,
                                   "comparisons": [asdict(c) for c in comps], "on_the_ten_deciding_nothing": ten})
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
    for name in ("read1", "read2", "read3", "register"):
        sub.add_parser(name)
    read_data = sub.add_parser("read-data")
    read_data.add_argument("--replace", action="store_true", help="read again over a read that is on record, and say so")
    read_data.add_argument("--arm", default="data", choices=sorted(DATA_ARMS),
                           help="data (default): chain v14_data's whole-pool trainings; clean: the same recipe trained with "
                                "--holdout-twins drop-any-charge (TASKS 253), read into read_clean.md and .json")
    seleval = sub.add_parser("seleval")
    seleval.add_argument("--only", default=None, metavar="CONFIG", help="one configuration of the frozen list, by name")
    a = ap.parse_args(argv)
    if a.cmd == "plan":
        return cmd_plan(a.carried_models)
    if a.cmd == "seleval":
        return cmd_seleval(a.only)
    if a.cmd == "read-data":
        return cmd_read_data(a.replace, a.arm)
    return {"read1": cmd_read1, "read2": cmd_read2, "read3": cmd_read3, "register": cmd_register}[a.cmd]()


if __name__ == "__main__":
    raise SystemExit(main())
