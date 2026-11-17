"""The chain that makes a version's release networks, written as explicit command steps (decision 66; review of 17 Nov 2026).

    python probes/release_chain.py <measurement prefix …> [--name release_<stem>] [--m05 <module-05 folder>] [--out-dir <plan folder>]

A standard rung-C step of `chain_runner.py` would enter the checkpoints in the registry as measurement networks and evaluate them
on the hold-outs — both wrong for networks that trained on the hold-outs. So the chain is four kinds of 'cmd' step, in module 05:

  train release <stem>          the measurement training's own command — rebuilt from the measurement checkpoints' saved arguments
                                (`rungC_config.argv_of`), so that release check 1 can pass — with `--network-kind release`,
                                `--sizes all`, every seed in one run and its own output prefix `<prefix>_release`
  register release candidates   `model_registry.py --add-candidates … --network-kind release`
  in-sample read seed <s>       `rungC_eval_saved.py … --insample-read` on the frozen hold-out (b) and the clean hold-out (a) as a8:
                                records `<prefix>_release_insample_seed<s>` (never `…_eval_…`, which the accuracy reads)
  release checks                `release_checks.py <release checkpoints> --measurement <measurement checkpoints>`; a refusal fails
                                the run, and the pipeline then keeps the measurement networks

A measurement prefix is a training's output prefix relative to module 05 (`<prefix>_model_n<N>_seed<S>.pt`, `<prefix>.json`);
several are given when the seeds were trained in several runs. Refused before anything is written: a checkpoint that is not a
measurement network, seeds trained with different settings, a measurement network trained on a part of its pool (check 1 would
refuse its release: `all` is not its recipe), settings the trainer refuses with `release`, and files that exist: the chain, its
run spec, and anything `<prefix>_release*` under module 05 (an earlier release of the recipe, whose checkpoints and records the
training would overwrite).

Written: `probes/runs/<name>.json` (the chain) and `probes/runspecs/<name>.json` (its run spec). Nothing is launched: dry-run the
chain and smoke the training first (`tools/runspec.py launch probes/runspecs/<name>.json`, on the user's word)."""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1]
M05_REL = "modules/05_support_predictor"
sys.path.insert(0, str(PLAN / M05_REL / "m05"))
import chain_runner  # noqa: E402  (beside this file)
import model_registry as MR  # noqa: E402
import network_kind as NK  # noqa: E402
import promotion_read  # noqa: E402
from rungC_config import TrainConfig, argv_of  # noqa: E402
from rungC_settings_added import with_absent_settings  # noqa: E402

TAG = "REL"
CLEAN_A = "out/holdout_a_clean_2026-10-30.txt"       # hold-out (a) without its two twins: the set the licence reads as a8
RUN_ONLY = ("out_prefix", "threads", "seeds")        # as release_checks.RUN_ONLY: the run's own, not the recipe's
MAX_GAP_MINUTES = 120                                # the run-spec schema's ceiling; the chain runner prints progress while a log grows
HOURS = 7.0
PEAK_GB = 7.7


@dataclass(frozen=True)
class Measured:
    """The measurement networks a release is made for: their checkpoints (relative to module 05), seeds and one shared config."""

    checkpoints: tuple[str, ...]
    seeds: tuple[int, ...]
    config: TrainConfig
    prefix: str


def measurement_networks(prefixes: list[str], m05: Path) -> Measured:
    """The checkpoints of the given prefixes, after every refusal: each must be a measurement network trained on its whole pool, and
    all must share their settings but for the run's own."""
    found = [(pre, p) for pre in prefixes for p in sorted(m05.glob(f"{pre}_model_n*_seed*.pt"))]
    if not found or {pre for pre, _ in found} != set(prefixes):
        raise SystemExit(f"no checkpoint <prefix>_model_n*_seed*.pt under {m05} for: {sorted(set(prefixes) - {pre for pre, _ in found}) or prefixes}")
    settings, seeds = [], []
    for pre, path in found:
        ck = MR.load_checkpoint(path)
        if NK.kind_of_checkpoint(ck, path.name) != NK.MEASUREMENT:
            raise SystemExit(f"{path.name} is a release network; the chain is built from a version's measurement networks")
        record = json.loads((m05 / f"{pre}.json").read_text(encoding="utf-8"))
        if not NK.trained_on_whole_pool(record, int(ck["n"])):
            raise SystemExit(f"{path.name} trained on {ck['n']} of its pool's {record['pool']} molecules: a release trains on all of its pool, "
                             "which is another recipe (release check 1 would refuse it)")
        settings.append({k: v for k, v in with_absent_settings(ck["args"])[0].items() if k not in RUN_ONLY})
        seeds.append(int(ck["seed"]))
    differing = sorted(k for k in set().union(*settings) if any(s.get(k) != settings[0].get(k) for s in settings))
    if differing or len(set(seeds)) != len(seeds):
        raise SystemExit(f"the measurement checkpoints are not one recipe with one checkpoint per seed: settings that differ {differing}, seeds {seeds}")
    config = TrainConfig(**settings[0], out_prefix=prefixes[0])
    return Measured(tuple(p.relative_to(m05).as_posix() for _, p in found), tuple(sorted(seeds)), config, prefixes[0])


def release_config(measured: Measured, threads: int) -> TrainConfig:
    """The measurement recipe as a release training: the kind, every molecule of the pool, all seeds in one run, its own prefix."""
    changed = {NK.FIELD: NK.RELEASE, "sizes": "all", "out_prefix": f"{measured.prefix}_release", "threads": threads, "save_model": True,
               "seeds": ",".join(str(s) for s in measured.seeds)}
    try:
        return TrainConfig(**(measured.config.model_dump() | changed))
    except ValueError as e:
        raise SystemExit(f"the measurement recipe cannot be trained as release networks: {e}") from None


def step(label: str, log: str, argv: list[str], glob_args: bool = False) -> dict:
    """One 'cmd' step in module 05; `glob_args` for a step that names checkpoints by pattern (N is known after the training)."""
    return {"kind": "cmd", "label": label, "cwd": M05_REL, "log": f"{M05_REL}/{log}", "argv": argv} | ({"glob_args": True} if glob_args else {})


def steps(measured: Measured, cfg: TrainConfig, name: str) -> list[dict]:
    rel, stem = cfg.out_prefix, Path(cfg.out_prefix).name
    release = [f"{rel}_model_n*_seed{s}.pt" for s in measured.seeds]
    labels = ["--use-analytic"] if cfg.use_analytic else []
    out = [step(f"train release {stem}", f"{rel}.log", ["{python}", "m05/rungC_train.py", *argv_of(cfg)]),
           step("register release candidates", f"{rel}_registry.log", glob_args=True,
                argv=["{python}", "m05/model_registry.py", "--add-candidates", *release, "--chain", name, "--network-kind", NK.RELEASE,
                      "--note", f"release networks of the recipe of {measured.prefix} (decision 66); not shipped until release checks pass"])]
    out += [step(f"in-sample read seed {s}", f"{rel}_insample_seed{s}.log", glob_args=True,
                 argv=["{python}", "../../probes/rungC_eval_saved.py", model, f"{rel}_insample_seed{s}", *labels, "--threads", str(cfg.threads),
                       "--allow-any-model", "--holdout-b-file", chain_runner.HOLDOUT_B, "--eval-ids-file", f"a8={CLEAN_A}", "--insample-read"])
            for s, model in zip(measured.seeds, release, strict=True)]
    # a checkpoint's own name is no pattern; the release ones are known by pattern only
    return [*out, step("release checks", f"{rel}_release_checks.log", glob_args=True,
                       argv=["{python}", "../../probes/release_checks.py", *release, "--measurement", *measured.checkpoints, "--threads", "2"])]


def chain(name: str, measured: Measured, cfg: TrainConfig) -> dict:
    rel = f"{M05_REL}/{cfg.out_prefix}"
    return {"_about": f"decision 66: the release networks of the recipe of {measured.prefix} — training, registration as release candidates, "
                      "in-sample reads, release checks (probes/release_chain.py wrote this file)",
            "name": TAG, "poll_s": 1800, "wait": [], "steps": steps(measured, cfg, name),
            "outputs": [f"{rel}.json", *(f"{rel}_insample_seed{s}.json" for s in measured.seeds), f"{rel}_release_checks.json"]}


def runspec(name: str, measured: Measured) -> dict:
    return {"name": name, "purpose": f"decision 66 (design note of 17 Nov 2026): the release networks of the recipe of {measured.prefix}, "
                                     "their in-sample reads and the release checks",
            "host": "laptop", "workdir": "probes/results_m1", "command": f"python ../chain_runner.py probes/runs/{name}.json",
            "sources": [{"local": "probes/chain_runner.py"}, {"local": "probes/release_chain.py"}, {"local": "probes/release_checks.py"},
                        {"local": "probes/rungC_eval_saved.py"}, {"local": f"{M05_REL}/m05/rungC_train.py"}],
            "progress": {"regex": f"^=== \\({TAG}\\) progress: |^\\({TAG}\\) .* done ", "max_gap_minutes": MAX_GAP_MINUTES,
                         "start_regex": f"^=== \\({TAG}\\) starting: "},
            "marker_regex": f"^=== \\({TAG}\\) (armed|starting|resuming|RUN FAILED|run done)", "end_regex": f"^=== \\({TAG}\\) run done",
            "fail_regex": f"^=== \\({TAG}\\) RUN FAILED", "dry_run_args": "--dry-run", "resumable": True,
            "memory": {"peak_gb": PEAK_GB, "basis": "chain 41's trainer peak (7.7 GB at n = 972-978, 19 Oct 2026); a release pool is about 1,130 "
                                                     "molecules, so this is a floor to be measured on the smoke run, not a bound"},
            "estimate": {"hours": HOURS, "basis": "design note of 17 Nov 2026, §5: one more training of three seeds, six to seven laptop hours"}}


def write_new(path: Path, obj: dict) -> None:
    """A JSON file that must not exist yet: a chain that may have run is never overwritten."""
    if path.exists():
        raise SystemExit(f"{path} exists — a chain is not overwritten; choose another --name")
    path.parent.mkdir(parents=True, exist_ok=True)
    promotion_read.write_atomic(path, json.dumps(obj, indent=1, ensure_ascii=False) + "\n")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("prefixes", nargs="+", help="the measurement trainings' output prefixes, relative to module 05")
    ap.add_argument("--name", default=None, help="the chain's file name (default: release_<stem of the first prefix>)")
    ap.add_argument("--m05", type=Path, default=PLAN / M05_REL, help="the module-05 folder that holds the measurement checkpoints")
    ap.add_argument("--out-dir", type=Path, default=PLAN, help="the plan folder whose probes/runs and probes/runspecs are written")
    ap.add_argument("--threads", type=int, default=8)
    a = ap.parse_args(argv)
    m05 = a.m05.resolve()
    measured = measurement_networks(a.prefixes, m05)
    cfg = release_config(measured, a.threads)
    if earlier := sorted(p.relative_to(m05).as_posix() for p in m05.glob(f"{cfg.out_prefix}*")):
        raise SystemExit(f"a release of this recipe exists under {m05}: {', '.join(earlier)}; its training would overwrite them — "
                         "move them away first")
    name = a.name or f"release_{Path(measured.prefix).name}"[:40]
    targets = {a.out_dir / "probes" / "runs" / f"{name}.json": chain(name, measured, cfg),
               a.out_dir / "probes" / "runspecs" / f"{name}.json": runspec(name, measured)}
    if existing := [str(p) for p in targets if p.exists()]:
        raise SystemExit(f"exists, not overwritten: {', '.join(existing)}; choose another --name")
    for path, obj in targets.items():
        write_new(path, obj)
        print(f"wrote {path}", flush=True)
    print("nothing launched: dry-run the chain and smoke the training before a first release run", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
