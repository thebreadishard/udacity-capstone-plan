"""The proxy check of the few-anchor transfer (the user, 21 Oct 2026: (a) and (b) before the cation run), planned and read.

Arm (a): a base trained on chain 34's pool with its label distorted per mode family by the CC correction's measured relation to the
proxy (the median slope over set three's anchors, `out/set3_diagnosis_2026-10-21/decompose.json`), fine-tuned on k molecules with the true
label. Arm (b): a base trained on chain 34's pool without layer A2, fine-tuned on k A2 molecules. Chain 34 is the base the CC transfer used;
its 750 molecules also train in about half the time of today's pool. Both read on fixed sets of held-out molecules with analytic labels
(`m05/proxy_transfer_check.py`). The base recipe is chain 34's, read from its record. Design and registration:
`GoalGathering/notes/Design_2026-10-21_Few_Anchor_Proxy_Check.md`.

    python probes/proxy_check_plan.py split <out_dir>    # loads the corpus once: id files, pool sizes, manifest.json
    python probes/proxy_check_plan.py plan <out_dir>     # probes/runs/proxy_check.json from the manifest
    python probes/proxy_check_plan.py register <out_dir> # chain step: the six base models into the model registry as candidates
    python probes/proxy_check_plan.py read <out_dir>     # <out_dir>/proxy_check_read.{json,md}
"""
from __future__ import annotations

import argparse
import json
import os
import shlex
import statistics
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
M05 = PLAN / "modules" / "05_support_predictor"
RUNS = PLAN / "probes" / "runs"
CHAIN34_RECORD = M05 / "out" / "E7_rungC_chain34_kdfamily_750_2026-10-05.json"
DECOMPOSE = M05 / "out" / "set3_diagnosis_2026-10-21" / "decompose.json"
FAMILIES = ("ring-ip", "CH-stretch", "CH-oop", "other")
SEEDS = (0, 1, 2)
LAYERS = ("A", "A2", "B")                 # chain 34's pool layers; cations and the size-test layer stay out
SE_FACTOR = 2.0                           # a difference is read when it exceeds twice the combined standard error
L1_SIZES = (5, 10, 20)                    # the few-anchor regime of line L1
L1_NEEDED = 2                             # L1 holds at two of the three
VS_LAMBDA1 = "whole head below the last layer (λ 1)"
VS_SCRATCH = "whole head below scratch (the base helps)"
THREADS = "8"


@dataclass(frozen=True)
class Arm:
    """One arm: its base's extra trainer flags (beyond chain 34's recipe), the k of the fine-tune curve, the reservoir size, the draws per
    k below the reservoir size."""

    name: str
    sizes: tuple[int, ...]
    reservoir: int
    draws: int = 3


ARMS = {"a": Arm("a", (5, 10, 20, 50, 100, 200), 200), "b": Arm("b", (5, 10, 20, 40), 40)}


def write_text(path: Path, text: str) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    os.replace(tmp, path)


def recipe_flags(record_path: Path = CHAIN34_RECORD) -> list[str]:
    """Chain 34's trainer flags, as its record states the command (the positional corpus and prefix dropped)."""
    command = json.loads(record_path.read_text(encoding="utf-8"))["provenance"]["command"]
    return shlex.split(command)[3:]


def cc_slopes(path: Path = DECOMPOSE) -> dict[str, float]:
    """Per family, the median over the anchors of the slope of the CC correction's first-order shifts on the proxy's (families with more
    than one mode on the anchor), rounded to two decimals."""
    d = json.loads(path.read_text(encoding="utf-8"))
    out = {}
    for fam in FAMILIES:
        slopes = [v[fam]["total"]["slope"] for v in d.values() if fam in v and v[fam]["n"] > 1]
        if not slopes:
            raise SystemExit(f"{path}: no anchor with {fam} modes")
        out[fam] = round(statistics.median(slopes), 2)
    return out


def family_scale_text(slopes: dict[str, float]) -> str:
    return ",".join(f"{f}={s:g}" for f, s in slopes.items())


def base_extra(arm: str, out_rel: str, slopes: dict[str, float]) -> list[str]:
    """The base's flags beyond chain 34's recipe: its exclusion file (chain 34's pool; for (b) without A2) and, for (a), the family scales."""
    extra = ["--exclude-ids-file", f"{out_rel}/{arm}_exclude.txt"]
    return [*extra, "--family-scale", family_scale_text(slopes)] if arm == "a" else extra


def sha_order(ids) -> list[str]:
    sys.path.insert(0, str(M05 / "m05"))
    import e6_learning_curve as E6
    return sorted(ids, key=E6.sha)


def eligible(mols: dict, substituted: list[str]) -> dict[str, str]:
    """Admitted molecules of the pool layers with analytic labels: id → layer."""
    return {i: mols[i]["layer"] for i in substituted if i in mols and mols[i]["layer"] in LAYERS}


def split_ids(elig: dict[str, str]) -> dict[str, list[str]]:
    """The reservoirs and read sets in hash order: (a) over every eligible molecule, (b) over the eligible A2 molecules."""
    every = sha_order(elig)
    a2 = [i for i in every if elig[i] == "A2"]
    na, nb = ARMS["a"].reservoir, ARMS["b"].reservoir
    if len(every) <= na or len(a2) <= nb:
        raise SystemExit(f"too few eligible molecules: {len(every)} (reservoir a {na}), A2 {len(a2)} (reservoir b {nb})")
    return {"a_reservoir": every[:na], "a_read": every[na:], "b_reservoir": a2[:nb], "b_read": a2[nb:]}


def pool_ids(argv: list[str]) -> list[str]:
    """The pool the trainer will train on with these arguments ('--sizes all'), as its own selection computes it."""
    sys.path.insert(0, str(M05 / "m05"))
    from rungC_config import config_from_argv
    from rungC_train import select_corpus
    return list(select_corpus(config_from_argv(argv), lambda s: None).pool)


def exclusions(pool_now: list[str], chain34_pool: list[str], a2: list[str]) -> dict[str, list[str]]:
    """The ids each base's exclusion file lists: (a) today's pool beyond chain 34's, (b) the same and every A2 molecule."""
    extra = sorted(set(pool_now) - set(chain34_pool))
    return {"a_exclude": extra, "b_exclude": sorted(set(extra) | set(a2))}


def split(out_dir: Path) -> dict:
    sys.path.insert(0, str(M05 / "m05"))
    from rungC_train import load_corpus
    mols, *_rest, substituted = load_corpus(str(M05 / "corpus" / "molecules"), use_analytic=True, log=lambda s: None)
    ids = split_ids(eligible(mols, substituted))
    out_dir.mkdir(parents=True, exist_ok=True)
    slopes, flags, mdir = cc_slopes(), recipe_flags(), str(M05 / "corpus" / "molecules")
    chain34 = json.loads(CHAIN34_RECORD.read_text(encoding="utf-8"))["pool_ids"]
    excl = exclusions(pool_ids([mdir, str(out_dir / "pool_now"), *flags]), chain34, [i for i, m in mols.items() if m["layer"] == "A2"])
    for name, lst in {**ids, **excl}.items():
        write_text(out_dir / f"{name}.txt", "\n".join(lst) + "\n")
    pools = {arm: pool_ids([mdir, str(out_dir / f"base_{arm}"), *flags, *base_extra(arm, str(out_dir), slopes)]) for arm in ARMS}
    manifest = {"slopes": slopes, "recipe": flags, "pool": {arm: len(p) for arm, p in pools.items()},
                "pool_a_vs_chain34": {"missing": sorted(set(chain34) - set(pools["a"])), "extra": sorted(set(pools["a"]) - set(chain34))},
                **{k: len(v) for k, v in {**ids, **excl}.items()}}
    write_text(out_dir / "manifest.json", json.dumps(manifest, indent=1))
    return manifest


def model_path(out_rel: str, arm: str, n: int, seed: int) -> str:
    return f"{out_rel}/base_{arm}_model_n{n}_seed{seed}.pt"


def draws_for(arm: Arm, k: int) -> int:
    return 1 if k == arm.reservoir else arm.draws


def steps(out_dir: Path, manifest: dict) -> list[dict]:
    """The chain: base (b), base (a), the registry entries, then the fine-tune runs — arm (b) first, each seed along k."""
    out_rel = Path(os.path.relpath(out_dir, M05)).as_posix()
    flags = manifest["recipe"]

    def step(label: str, argv: list[str]) -> dict:
        return {"kind": "cmd", "label": label, "cwd": "modules/05_support_predictor", "log": f"modules/05_support_predictor/{out_rel}/{label}.log",
                "argv": argv}

    out = [step(f"base_{arm}", ["{python}", "m05/rungC_train.py", "corpus/molecules", f"{out_rel}/base_{arm}", *flags,
                                *base_extra(arm, out_rel, manifest["slopes"])]) for arm in ("b", "a")]
    out.append(step("register", ["{python}", "../../probes/proxy_check_plan.py", "register", out_rel]))
    for arm in ("b", "a"):
        spec = ARMS[arm]
        for seed in SEEDS:
            for k in spec.sizes:
                out.append(step(f"ft_{arm}_k{k}_seed{seed}", [
                    "{python}", "m05/proxy_transfer_check.py", "corpus/molecules", model_path(out_rel, arm, manifest["pool"][arm], seed),
                    f"{out_rel}/ft_{arm}_k{k}_seed{seed}", "--reservoir", f"{out_rel}/{arm}_reservoir.txt", "--read", f"{out_rel}/{arm}_read.txt",
                    "--k", str(k), "--subsets", str(draws_for(spec, k)), "--threads", THREADS, "--allow-any-model"]))
    return out


def plan(out_dir: Path) -> Path:
    manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    out_rel = Path(os.path.relpath(out_dir, M05)).as_posix()
    st = steps(out_dir, manifest)
    outputs = [f"modules/05_support_predictor/{s['argv'][4]}.json" for s in st if s["label"].startswith("ft_")]
    spec = {"_about": "proxy check (a) and (b): probes/proxy_check_plan.py plan", "name": "PX", "steps": st,
            "outputs": [f"modules/05_support_predictor/{model_path(out_rel, arm, manifest['pool'][arm], s)}" for arm in ARMS for s in SEEDS] + outputs}
    path = RUNS / "proxy_check.json"
    write_text(path, json.dumps(spec, indent=1))
    return path


def register(out_rel: str) -> int:
    manifest = json.loads((M05 / out_rel / "manifest.json").read_text(encoding="utf-8"))
    paths = [model_path(out_rel, arm, manifest["pool"][arm], s) for arm in ARMS for s in SEEDS]
    note = ("proxy check (a) distorted label / (b) without layer A2 - bases for probes/proxy_check_plan.py only, never a production model "
            "(GoalGathering/notes/Design_2026-10-21_Few_Anchor_Proxy_Check.md)")
    return subprocess.run([sys.executable, "m05/model_registry.py", "--add-candidates", *paths, "--chain", "PX", "--note", note],
                          cwd=M05, check=False).returncode


# ----------------------------------------------------------------------------------------------------------------------------------- read
def mean_se(xs: list[float]) -> tuple[float, float, int]:
    if not xs or any(x is None or not np.isfinite(x) for x in xs):
        raise SystemExit(f"a missing or non-finite value among {xs}")
    n = len(xs)
    return float(np.mean(xs)), (float(np.std(xs, ddof=1) / np.sqrt(n)) if n > 1 else float("nan")), n


def intensity_column(xs: list[float | None]) -> tuple[float, float, int]:
    """The intensity's mean ± se over the reads that have one (a read has none when every molecule's prediction moved a mode across the
    threshold); n says how many. Reported, no line: never a reason to stop the read."""
    have = [x for x in xs if x is not None]
    return mean_se(have) if have else (float("nan"), float("nan"), 0)


def values(records: list[dict], mode: str, key) -> list[float]:
    """One value per (seed, draw) of a fine-tune mode, or per seed for 'none' and 'zero_rule'."""
    if mode in ("none", "zero_rule"):
        return [key(r[mode]) for r in records]
    return [key(d["modes"][mode]["read"]) for r in records for d in r["draws"]]


def lower(a: tuple, b: tuple) -> bool:
    """a's mean below b's by more than SE_FACTOR combined standard errors."""
    return a[0] < b[0] - SE_FACTOR * float(np.hypot(a[1], b[1]))


def read_arm(records_by_k: dict[int, list[dict]]) -> dict:
    """Per k and column the mean ± se of CH-oop, 'other' and the matched intensity; the registered comparisons."""
    keys = {"CH-oop": lambda r: r["family_mean"]["CH-oop"], "other": lambda r: r["family_mean"]["other"],
            "intensity": lambda r: r["intensity_matched_mean"]}
    out = {}
    for k, recs in sorted(records_by_k.items()):
        modes = ["zero_rule", "none", *recs[0]["modes"]]
        cols = {m: {q: (intensity_column if q == "intensity" else mean_se)(values(recs, m, f)) for q, f in keys.items()} for m in modes}
        for m in modes:
            cols[m]["intensity_failed"] = sum(values(recs, m, lambda r: r.get("n_intensity_failed", 0)))
        cmp = {}
        if {"head_all", "head_l2"} <= set(cols):
            cmp[VS_LAMBDA1] = {q: lower(cols["head_all"][q], cols["head_l2"][q]) for q in keys}
        if {"head_all", "scratch"} <= set(cols):
            cmp[VS_SCRATCH] = {q: lower(cols["head_all"][q], cols["scratch"][q]) for q in keys}
        out[k] = {"columns": cols, "comparisons": cmp}
    return out


def registered_lines(by_k: dict) -> dict:
    """The registered lines of one arm: L1 = head_all below head_l2 on CH-oop at L1_NEEDED of L1_SIZES; L2 = the largest k at which
    head_all is below scratch on CH-oop (None when at none)."""
    l1_at = [k for k in L1_SIZES if by_k[k]["comparisons"][VS_LAMBDA1]["CH-oop"]]
    l2_at = [k for k, r in by_k.items() if r["comparisons"][VS_SCRATCH]["CH-oop"]]
    return {"L1": {"holds": len(l1_at) >= L1_NEEDED, "at": l1_at}, "L2": {"largest_k": max(l2_at) if l2_at else None, "at": sorted(l2_at)}}


def read(out_dir: Path) -> dict:
    manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    res = {"manifest": manifest, "arms": {}}
    for arm, spec in ARMS.items():
        by_k = {}
        for k in spec.sizes:
            paths = [out_dir / f"ft_{arm}_k{k}_seed{s}.json" for s in SEEDS]
            missing = [p.name for p in paths if not p.exists()]
            if missing:
                raise SystemExit(f"missing records: {missing}")
            by_k[k] = [json.loads(p.read_text(encoding="utf-8")) for p in paths]
        res["arms"][arm] = read_arm(by_k)
        res["lines"] = {**res.get("lines", {}), arm: registered_lines(res["arms"][arm])}
    write_text(out_dir / "proxy_check_read.json", json.dumps(res, indent=1, default=str))
    write_text(out_dir / "proxy_check_read.md", "\n".join(report_lines(res)) + "\n")
    return res


def report_lines(res: dict) -> list[str]:
    lines = ["# Proxy check of the few-anchor transfer — read", "", f"Slopes of arm (a): {res['manifest']['slopes']}; pools {res['manifest']['pool']}.", ""]
    for arm, by_k in res["arms"].items():
        ln = res["lines"][arm]
        lines += [f"## Arm ({arm})", "", f"**L1** (whole head below λ 1 on CH-oop at {L1_NEEDED} of k = {list(L1_SIZES)}): "
                  f"{'holds' if ln['L1']['holds'] else 'does not hold'} (at {ln['L1']['at']}). **L2** (the base helps, CH-oop): largest k "
                  f"{ln['L2']['largest_k']} (at {ln['L2']['at']}).", "",
                  "| k | column | CH-oop | other | intensity | no intensity |", "|---|---|---|---|---|---|"]
        for k, r in by_k.items():
            lines += [f"| {k} | {m} | " + " | ".join(f"{c[q][0]:.2f} ± {c[q][1]:.2f}" for q in ("CH-oop", "other", "intensity"))
                      + f" | {c['intensity_failed']} |" for m, c in r["columns"].items()]
        lines += [""] + [f"- k {k}: {name}: " + ", ".join(f"{q} {'yes' if v else 'no'}" for q, v in c.items())
                         for k, r in by_k.items() for name, c in r["comparisons"].items()] + [""]
    return lines


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("action", choices=["split", "plan", "register", "read"])
    ap.add_argument("out_dir")
    a = ap.parse_args()
    if a.action == "register":
        return register(a.out_dir)
    out_dir = Path(a.out_dir).resolve()
    if a.action == "split":
        print(json.dumps(split(out_dir), indent=1))
    elif a.action == "plan":
        print(plan(out_dir))
    else:
        print("\n".join(report_lines(read(out_dir))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
