"""Proxy check of the few-anchor transfer (the user, 21 Oct 2026, item 2): does a base model that learned one correction move to another
from k labelled molecules, and which part of the network has to move? Read on a fixed set of held-out corpus molecules, not on eleven anchors.

One run = one base model (one seed), one k: for each of up to `--subsets` draws of k molecules from the reservoir, the base is fine-tuned in
every mode asked and read on every molecule of the read set against its true ωB97X − B3LYP correction (analytic labels):
'head_l2' (the head's last layer + α with the L2 pull toward the base's last layer, set three's registered protocol), 'head' (the same
without the pull), 'head_all' (every head layer + α), and 'scratch' (the base's own training recipe, from its record, on the k molecules
alone — what the base is worth against no base); and the anchor-price follow-up's early-stopped recipes 'head_all_es' and 'body1_es'
('head_all', or it with the body's last interaction block, fitted on 1 − --es-val of the k molecules and stopped by the loss on the
rest, decision 51). The zero rule and the base as it is ('none') are read once. A fine-tune takes a fixed
number of optimiser steps (`--steps`, epochs = ⌈steps / k⌉): 3000 steps are set three's 300 epochs at ten anchors.

    python m05/proxy_transfer_check.py corpus/molecules <model.pt> <out_prefix> --reservoir ids.txt --read ids.txt --k 10 [--subsets 5]
        [--modes head_l2,head,head_all,scratch] [--steps 3000] [--lr 1e-3] [--head-l2 1] [--threads 8] [--allow-any-model]
        [--es-max-epochs 60] [--es-val 0.15] [--es-patience 10]

Planned and read by `probes/proxy_check_plan.py`; the design is `GoalGathering/notes/Design_2026-10-21_Few_Anchor_Proxy_Check.md`.
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import os
import re
import shlex
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import e7_t2_posthoc as PH
import model_registry as MR
import rungC_intensities as RI
from rungC_cc_transfer import KEPT, FinetuneSettings, family_freq_rms, finetune, finetune_early_stopped
from rungC_config import TrainConfig, config_from_argv
from rungC_train import (
    inner_split,
    load_corpus,
    load_hybrid_model,
    load_molecule,
    loss_settings,
    molecule_tensors,
    predictor,
    readouts,
    record_paths,
    tensor_config,
    train_one,
)

MODES = ("head_l2", "head", "head_all", "scratch", "head_all_es", "body1_es")
EARLY_STOPPED = {"head_all_es": "head_all", "body1_es": "head_all_body1"}   # the anchor-price follow-up's recipes (decision 51)
SUBSET_SEED = 0
MODEL_NAME = re.compile(r"_model_n\d+_seed(\d+)\.pt$")


def read_ids(path: Path) -> list[str]:
    """Ids one per line ('#' lines are comments), in file order; refuses an empty file or a repeated id."""
    ids = [s.strip() for s in path.read_text(encoding="utf-8").splitlines() if s.strip() and not s.startswith("#")]
    if not ids:
        raise SystemExit(f"{path}: no ids")
    if len(set(ids)) != len(ids):
        raise SystemExit(f"{path}: an id is listed twice")
    return ids


def draw_subsets(reservoir: list[str], k: int, n: int, seed: int = SUBSET_SEED) -> list[tuple[str, ...]]:
    """n distinct draws of k ids from the reservoir (the sorted reservoir, numpy's generator at `seed`: the same draws whatever order the
    reservoir is given in); one draw — the whole reservoir — when k is its size."""
    pool = sorted(reservoir)
    if not 0 < k <= len(pool):
        raise ValueError(f"a subset of {k} from a reservoir of {len(pool)}")
    if k == len(pool):
        return [tuple(pool)]
    if math.comb(len(pool), k) < n:
        raise ValueError(f"only {math.comb(len(pool), k)} subsets of {k} from {len(pool)}, {n} asked")
    rng = np.random.default_rng(seed)
    out: list[tuple[str, ...]] = []
    while len(out) < n:
        draw = tuple(pool[i] for i in sorted(rng.choice(len(pool), size=k, replace=False)))
        if draw not in out:
            out.append(draw)
    return out


def epochs_for(steps: int, k: int) -> int:
    """Epochs of a fine-tune on k molecules that take `steps` optimiser steps (one step per molecule)."""
    return max(1, math.ceil(steps / k))


def base_record_path(model: Path) -> Path:
    """The trainer's record beside a saved model (`<prefix>_model_n<n>_seed<s>.pt` → `<prefix>.json`)."""
    if not MODEL_NAME.search(model.name):
        raise SystemExit(f"{model.name}: not a model the trainer saved (<prefix>_model_n<n>_seed<s>.pt)")
    return record_paths(model.parent / MODEL_NAME.sub("", model.name))[0]


def scratch_config(record: dict, molecules: str, out_prefix: str, seed: int) -> TrainConfig:
    """The base's own training recipe, read from its record's command, on the true label (no --family-scale or --distortion-file), saving
    nothing, one seed."""
    argv = shlex.split(record["provenance"]["command"])[3:]          # rungC_train.py <molecules> <out_prefix> <flags…>
    cfg = config_from_argv([molecules, out_prefix, *argv])
    return cfg.model_copy(update={"family_scale": None, "distortion_file": None, "save_model": False, "seeds": str(seed)}).resolved()


@dataclass
class Inputs:
    """What every fine-tune of a run reads: the corpus entries (analytic labels substituted), the tensors of the reservoir and read set,
    the base model and the loss it was trained with."""

    mols: dict
    tensors: dict
    model0: torch.nn.Module
    loss_cfg: object
    record: dict


def load_inputs(molecules: str, model: Path, ids: list[str]) -> Inputs:
    mols, *_rest, substituted = load_corpus(molecules, use_analytic=True)
    missing = sorted(set(ids) - set(substituted))
    if missing:
        raise SystemExit(f"{len(missing)} ids without analytic labels (or not admitted), first {missing[:5]}: the check reads analytic labels only")
    model0, ck = load_hybrid_model(model)
    cfg = tensor_config(ck)
    cache = Path(molecules).parent / "ls_targets"
    tensors = {i: molecule_tensors(i, load_molecule(Path(molecules) / i, use_analytic=True), mols[i], Path(molecules) / i, cfg, cache)
               for i in sorted(set(ids))}
    record = json.loads(base_record_path(model).read_text(encoding="utf-8"))
    return Inputs(mols=mols, tensors=tensors, model0=model0, loss_cfg=loss_settings(ck), record=record)


def read_set(mols: dict, ids: list[str], train_ids: list[str], dF_of) -> dict:
    """Per read molecule the corrected-ω rms per family and, where its APT exists, the matched intensity error; their means over the
    read set; the registered read-outs over it."""
    per = {}
    for i in ids:
        m, dF = mols[i], dF_of(i)
        row = {"freq": family_freq_rms(m, PH.k_of(m, dF))}
        if "apt" in m:
            try:
                row["intensity"] = RI.intensity_readout(m["H_low"], m["dH_true"], m["B"].T @ dF @ m["B"], m["masses"], m["apt"])[RI.MATCHED]
            except RI.ModeCountChanged as e:
                row[RI.FAILED] = str(e)
        per[i] = row
    fams = sorted({f for r in per.values() for f in r["freq"]})
    inten = [r["intensity"] for r in per.values() if "intensity" in r]
    return {"family_mean": {f: float(np.mean([r["freq"][f] for r in per.values() if f in r["freq"]])) for f in fams},
            "intensity_matched_mean": float(np.mean(inten)) if inten else None, "n_intensity": len(inten),
            "n_intensity_failed": sum(RI.FAILED in r for r in per.values()),
            "kept": {k: v for k, v in readouts(mols, ids, train_ids, dF_of).items() if k in KEPT}, "per_molecule": per}


def fit(inp: Inputs, mode: str, train: tuple[str, ...], a, seed: int):
    """The model of one mode on one draw: a fine-tuned copy of the base, or the recipe trained from scratch. Returns (model, its record
    entries: the final training loss; for an early-stopped mode also the kept epoch, the epochs run, the validation loss and the split)."""
    def log(s: str) -> None:
        print(f"  [{mode} k{len(train)}] {s}", flush=True)

    if mode == "scratch":
        cfg = scratch_config(inp.record, a.molecules, a.out_prefix + "_scratch", seed)
        val_ids, fit_ids = inner_split(list(train), seed, cfg.inner_val)
        trained = train_one(fit_ids, inp.tensors, seed, cfg, val_ids, log=log)
        return trained.model, {"final_loss": trained.history[-1] if trained.history else None}
    model = copy.deepcopy(inp.model0)
    if mode in EARLY_STOPPED:
        val_ids, fit_ids = inner_split(list(train), seed, a.es_val)
        anchors = ({i: inp.tensors[i] for i in fit_ids}, {i: inp.tensors[i] for i in val_ids})
        es = finetune_early_stopped(model, inp.loss_cfg, anchors, EARLY_STOPPED[mode],
                                    FinetuneSettings(a.es_max_epochs, a.lr, a.aux_weight, patience=a.es_patience), log=log)
        return model, {"final_loss": es.hist[es.best_epoch - 1], "best_epoch": es.best_epoch, "epochs_run": len(es.hist),
                       "val_loss": es.val_hist[es.best_epoch - 1], "n_fit": len(fit_ids), "n_val": len(val_ids)}
    settings = FinetuneSettings(epochs_for(a.steps, len(train)), a.lr, a.aux_weight, a.head_l2 if mode == "head_l2" else 0.0)
    hist = finetune(model, inp.loss_cfg, {i: inp.tensors[i] for i in train}, mode, settings, log=log)
    return model, {"final_loss": hist[-1] if hist else None}


def run(inp: Inputs, reservoir: list[str], read_ids_: list[str], a, seed: int) -> dict:
    zero = read_set(inp.mols, read_ids_, reservoir, lambda i: np.zeros_like(inp.mols[i]["F_low"]))
    none = read_set(inp.mols, read_ids_, reservoir, predictor(inp.model0, inp.tensors, inp.mols))
    draws = []
    for train in draw_subsets(reservoir, a.k, a.subsets):
        entry = {"train": list(train), "modes": {}}
        for mode in a.modes:
            t0 = time.time()
            model, fitted = fit(inp, mode, train, a, seed)
            entry["modes"][mode] = {"read": read_set(inp.mols, read_ids_, list(train), predictor(model, inp.tensors, inp.mols)),
                                    **fitted, "seconds": round(time.time() - t0, 1)}
            fm = entry["modes"][mode]["read"]["family_mean"]
            print(f"k {a.k} draw {len(draws)} {mode}: CH-oop {fm.get('CH-oop', float('nan')):.2f} other {fm.get('other', float('nan')):.2f} "
                  f"({entry['modes'][mode]['seconds']:.0f} s)", flush=True)
        draws.append(entry)
    return {"zero_rule": zero, "none": none, "draws": draws}


def report(res: dict) -> list[str]:
    def fam(r: dict) -> str:
        return " | ".join(f"{r['family_mean'].get(f, float('nan')):.2f}" for f in ("ring-ip", "CH-stretch", "CH-oop", "other"))

    def inten(r: dict) -> str:
        failed = f" ({r['n_intensity_failed']} failed)" if r.get("n_intensity_failed") else ""
        return ("–" if r["intensity_matched_mean"] is None else f"{r['intensity_matched_mean']:.3f}") + failed

    lines = [f"# Proxy transfer check — k = {res['k']}, seed {res['seed']}", "", f"Base `{Path(res['model']).name}`; read set {res['n_read']} "
             f"molecules (intensity on {res['zero_rule']['n_intensity']}); reservoir {res['n_reservoir']}; {res['steps']} steps per fine-tune.", "",
             "| column | draw | ring-ip | CH-stretch | CH-oop | other | intensity | s |", "|---|---|---|---|---|---|---|---|",
             f"| zero rule | – | {fam(res['zero_rule'])} | {inten(res['zero_rule'])} | – |",
             f"| base as is | – | {fam(res['none'])} | {inten(res['none'])} | – |"]
    for j, d in enumerate(res["draws"]):
        lines += [f"| {mode} | {j} | {fam(v['read'])} | {inten(v['read'])} | {v['seconds']:.0f} |" for mode, v in d["modes"].items()]
    return lines


def write_record(prefix: str, res: dict, lines: list[str]) -> None:
    json_path, md_path = record_paths(prefix)
    for path, text in ((json_path, json.dumps(res, indent=1)), (md_path, "\n".join(lines) + "\n")):
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(text, encoding="utf-8")
        os.replace(tmp, path)


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("molecules")
    ap.add_argument("model", type=Path)
    ap.add_argument("out_prefix")
    ap.add_argument("--reservoir", type=Path, required=True, help="ids the k fine-tune molecules are drawn from, one per line")
    ap.add_argument("--read", type=Path, required=True, help="ids every model is read on, one per line; none of them in the reservoir")
    ap.add_argument("--k", type=int, required=True)
    ap.add_argument("--subsets", type=int, default=5, help="draws of k molecules (one when k is the reservoir's size)")
    ap.add_argument("--modes", type=lambda s: [m for m in s.split(",") if m], default=list(MODES), help=f"of {MODES}")
    ap.add_argument("--steps", type=int, default=3000, help="optimiser steps per fine-tune (epochs = ⌈steps / k⌉)")
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--aux-weight", type=float, default=1.0)
    ap.add_argument("--head-l2", type=float, default=1.0, help="the pull of mode 'head_l2' (set three's registered λ = 1)")
    ap.add_argument("--es-max-epochs", type=int, default=60, help=f"the epoch cap of the early-stopped modes {sorted(EARLY_STOPPED)}")
    ap.add_argument("--es-val", type=float, default=0.15, help="the share of the k molecules the early-stopped modes validate on")
    ap.add_argument("--es-patience", type=int, default=10, help="epochs without a better validation loss before an early-stopped mode stops")
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--allow-any-model", action="store_true", help="decision 55: a base that is not 'carried' — the distorted and the "
                    "family-ablated bases of this check are not production models; the record names it")
    return ap


def check_args(a, reservoir: list[str], read: list[str]) -> None:
    """Refuses what would read nothing or leak: an unknown mode, a step count or pull that is not positive, the scratch control on one
    molecule (its recipe holds an inner validation molecule out, nothing would be left to fit), a read id in the reservoir."""
    problems = [f"unknown mode {m!r} (of {MODES})" for m in a.modes if m not in MODES]
    problems += ["--steps must be positive"] * (a.steps < 1) + ["--head-l2 must be positive for mode head_l2"] * ("head_l2" in a.modes and a.head_l2 <= 0)
    problems += ["mode scratch needs --k 2 or more: its recipe holds one molecule out for inner validation"] * ("scratch" in a.modes and a.k < 2)
    if es := sorted(set(a.modes) & set(EARLY_STOPPED)):
        problems += [f"{es} need --k 2 or more: one molecule is held out for validation"] * (a.k < 2)
        problems += ["--es-max-epochs and --es-patience must be positive"] * (a.es_max_epochs < 1 or a.es_patience < 1)
        problems += ["--es-val must lie in (0, 0.5)"] * (not 0 < a.es_val < 0.5)
    if overlap := sorted(set(reservoir) & set(read)):
        problems.append(f"{len(overlap)} read ids are in the reservoir (first {overlap[:3]}): a read molecule may never be trained on")
    if problems:
        raise SystemExit("; ".join(problems))


def main(argv: list[str] | None = None) -> int:
    a = build_parser().parse_args(argv)
    reservoir, read = read_ids(a.reservoir), read_ids(a.read)
    check_args(a, reservoir, read)
    draw_subsets(reservoir, a.k, a.subsets)                                   # refuses an impossible k before the corpus is loaded
    seed_match = MODEL_NAME.search(a.model.name)
    seed = int(seed_match.group(1)) if seed_match else 0
    status = MR.require_carried(a.model, allow=a.allow_any_model)
    torch.set_num_threads(a.threads)
    torch.manual_seed(seed)
    t0 = time.time()
    inp = load_inputs(a.molecules, a.model, reservoir + read)
    print(f"base {a.model.name} (status {status['status']}); reservoir {len(reservoir)}, read {len(read)}; k {a.k}; modes {a.modes}", flush=True)
    res = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "model": str(a.model), "model_status": status["status"], "seed": seed, "k": a.k,
           "reservoir_file": str(a.reservoir), "read_file": str(a.read), "n_reservoir": len(reservoir), "n_read": len(read), "steps": a.steps,
           "lr": a.lr, "head_l2": a.head_l2, "modes": a.modes, "base_command": inp.record["provenance"]["command"],
           **({"early_stop": {"max_epochs": a.es_max_epochs, "val": a.es_val, "patience": a.es_patience}}
              if set(a.modes) & set(EARLY_STOPPED) else {}),
           **run(inp, reservoir, read, a, seed)}
    res["seconds"] = round(time.time() - t0, 1)
    write_record(a.out_prefix, res, report(res))
    print(f"wrote {a.out_prefix}.json/.md in {res['seconds']:.0f} s", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
