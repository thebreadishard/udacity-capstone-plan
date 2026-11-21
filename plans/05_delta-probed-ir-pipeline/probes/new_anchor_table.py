"""The read of the new CC anchors: the table per milestone, and the outcome by the registered rule (TASKS 291;
`GoalGathering/notes/PreRegistration_2026-11-21_New_Anchors_Read_Rule.md`).

For every milestone k of the frozen training order (`new_anchor_read.milestones`: 20, 40, … while the first k anchors are finished), each
carried measurement network is fine-tuned on the first k training anchors with R2 (`rungC_cc_transfer.finetune_es`, recipe `body1_es`,
the split seeded by the network's seed) and predicts every finished test anchor; the seeds' mean ΔH is added to the B3LYP Hessian and
read as the licence reads the product (`product_error_read.corrected_bands`: bands paired by mode overlap, families of the B3LYP
partner, certificate families), per family the rms over the test anchors' bands with its 95 % bootstrap interval over molecules
(`product_error_read.bootstrap`). Every milestone is computed in this one run, with one test set and one set of networks.
`new_anchor_read.decide` gives the outcome from that table.

Finished = a carried entry on the composite tier (TZ) in the anchor registry. Beside the curves, read and not judged: the zero rule
(B3LYP alone), the proxy networks without a fine-tune (which the rule's NO LEARNING compares with), the per-class α scaling fitted on the
same k, and the size read-out (the largest quarter of the test anchors by atoms, at the last milestone).

The whole corpus is loaded (`rungC_cc_transfer.prepare_anchors`): on the laptop this is a run, not a quick check — give it its memory.

    python probes/new_anchor_table.py --out modules/05_support_predictor/out/new_anchors/read_<date>
        [--lists GoalGathering/notes/new_anchors_2026-11-21] [--m05 modules/05_support_predictor] [--threads 4]
        → <out>.json and <out>.md (refused when they exist)
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import new_anchor_read as R  # noqa: E402
import product_error_read as PE  # noqa: E402  puts module 05's code and module 08 on the path

# isort: split
import anchor_registry as AR  # noqa: E402
import rungC_cc_transfer as CT  # noqa: E402
from learning_curve_layerA import molecule_features  # noqa: E402
from rungC_train import load_hybrid_model, loss_settings, tensor_config  # noqa: E402

RECIPE = "body1_es"            # R2, the registration's fine-tune
READ_TIER = "TZ"               # the composite tier (and benzene's full CC/TZ); tiers are never mixed
LR, AUX_WEIGHT = 1e-3, 1.0     # the CC transfer script's and the anchor count's values
LARGEST_SHARE = 0.25           # the size read-out: this share of the test anchors, the largest by atoms
REGISTRATION = "GoalGathering/notes/PreRegistration_2026-11-21_New_Anchors_Read_Rule.md"

BandRead = tuple[np.ndarray, np.ndarray]          # (each band's error in cm⁻¹, each band's family)


def read_ids(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")]


def finished_anchors(ids: list[str], entries: list[dict]) -> tuple[dict[str, dict], dict[str, str]]:
    """(id → its carried entry on the read tier, id → why it is not read) for the ids given."""
    done, left_out = {}, {}
    for i in ids:
        entry = AR.carried(i, entries)
        if entry is None:
            left_out[i] = "no carried anchor yet"
        elif entry["tier"] != READ_TIER:
            left_out[i] = f"carried on tier {entry['tier']}, not {READ_TIER}: its MP2 basis step is missing"
        else:
            done[i] = entry
    return done, left_out


def verify_files(used: dict[str, dict], entries: list[dict], root: Path = PLAN) -> None:
    """Every anchor file read is its molecule's carried entry and unchanged since it was registered (`AR.require_carried_anchor`
    refuses otherwise): a file re-fetched over a registered one must not be read under the registry's old hash."""
    for i, e in used.items():
        AR.require_carried_anchor(i, root / e["path"], entries=entries, root=root)


def training_head(train_order: list[str], done: dict[str, dict], left_out: dict[str, str]) -> tuple[list[str], dict]:
    """(the training anchors a milestone can use: the finished head of the order, cut to a multiple of STEP; what holds the order —
    the first unfinished anchor with its reason, and how many are finished behind it)."""
    k_done = next((j for j, i in enumerate(train_order) if i not in done), len(train_order))
    blocked = None
    if k_done < len(train_order):
        first = train_order[k_done]
        blocked = {"position": k_done + 1, "id": first, "why": left_out[first], "finished_behind_it": len(done) - k_done}
    return train_order[:k_done - k_done % R.STEP], {"n_train_finished_in_order": k_done, "order_held_by": blocked}


def family_points(reads: dict[str, BandRead]) -> dict[str, dict]:
    """Per family with bands: the rms over the molecules' bands (cm⁻¹), its 95 % bootstrap interval over molecules, the counts."""
    out = {}
    for fam in R.FAMILIES:
        bands = [reads[i][0][reads[i][1] == fam] for i in sorted(reads)]
        mean = PE.rms(bands)
        if mean is None:
            continue
        lo, hi = PE.bootstrap(bands, R.LINE_CM)["interval"]
        out[fam] = {"mean": mean, "lo": lo, "hi": hi, "n_bands": int(sum(len(b) for b in bands)),
                    "n_molecules_with_bands": int(sum(len(b) > 0 for b in bands))}
    return out


def largest_quarter(test_ids: list[str], n_atoms: dict[str, int]) -> list[str]:
    """The largest share of the test anchors by atoms (ties: the id), at least one."""
    ranked = sorted(test_ids, key=lambda i: (-n_atoms[i], i))
    return sorted(ranked[:max(1, round(LARGEST_SHARE * len(ranked)))])


def curves_for_rule(table: dict[int, dict[str, dict]]) -> dict[str, dict[int, R.Point]]:
    """The milestone table (k → family → point) as the rule's curves (family → k → Point); a family absent at a milestone stays absent
    there, which the rule refuses to read."""
    curves: dict[str, dict[int, R.Point]] = {}
    for k, fams in table.items():
        for fam, p in fams.items():
            curves.setdefault(fam, {})[k] = R.Point(p["mean"], p["lo"], p["hi"])
    return curves


@dataclass(frozen=True)
class Network:
    """One carried measurement network: its file, the proxy-trained model and what its checkpoint says of loss, tensors and seed."""

    path: Path
    model: object
    loss_cfg: object
    cfg: object
    seed: int


def load_networks(paths: tuple[Path, ...]) -> list[Network]:
    """The networks, which must share one tensor configuration (the anchors' tensors are built once)."""
    nets = []
    for p in paths:
        model, ck = load_hybrid_model(p)
        nets.append(Network(p, model, loss_settings(ck), tensor_config(ck), int(ck["seed"])))
    if any(n.cfg != nets[0].cfg for n in nets[1:]):
        raise SystemExit("the carried measurement networks differ in their tensor configuration; one read needs one")
    return nets


@dataclass(frozen=True)
class Problem:
    """What one read works on: the loaded anchors, the networks, the training order's finished head and the test anchors read."""

    an: CT.Anchors
    nets: list[Network]
    train: list[str]
    test: list[str]
    molecules: Path


def seed_mean(dH_of_seed: list[Callable[[str], np.ndarray]], test: list[str]) -> dict[str, np.ndarray]:
    """Per test anchor the mean over the seeds of the Cartesian ΔH."""
    return {i: np.mean([f(i) for f in dH_of_seed], axis=0) for i in test}


def band_read(pr: Problem, i: str, dH: np.ndarray) -> BandRead:
    """One test anchor's bands for a Cartesian ΔH, against its CC Hessian, in the certificate's families."""
    m = pr.an.mols[i]
    lo = np.asarray(m["H_low"], float)
    hi = lo + np.asarray(m["dH_true"], float)
    truth = molecule_features(pr.molecules / i, lo=lo, hi=hi)
    bands = PE.corrected_bands(PE.Hessians(lo, hi, np.asarray(m["masses"], float)), dH, np.array(truth["family"]))
    if np.abs(bands.low_freq - np.asarray(truth["freq"], float)).max() > 1e-6:      # the guard of product_error_read.molecule_read
        raise SystemExit(f"{i}: the family rule's modes are not the B3LYP normal modes")
    return bands.error, bands.family


def points_for(pr: Problem, dH: dict[str, np.ndarray], ids: list[str] | None = None) -> dict[str, dict]:
    return family_points({i: band_read(pr, i, dH[i]) for i in (pr.test if ids is None else ids)})


def fit_milestone(pr: Problem, k: int, log: Callable[[str], None]) -> tuple[dict[str, np.ndarray], dict[str, dict]]:
    """R2 on the first k training anchors, per network; (the seed-mean ΔH per test anchor, each seed's fit record)."""
    train = {i: pr.an.tensors[i] for i in pr.train[:k]}
    predictors, fits = [], {}
    for net in pr.nets:
        model = copy.deepcopy(net.model)
        run = CT.EsRun(CT.EarlyStop(seed=net.seed), LR, AUX_WEIGHT)
        fits[str(net.seed)] = CT.finetune_es(model, net.loss_cfg, train, RECIPE, run, log=lambda s, tag=f"[k {k} seed {net.seed}]": log(f"{tag} {s}"))
        predictors.append(lambda i, model=model: CT.predict_cartesian(model, pr.an.tensors[i]))
    return seed_mean(predictors, pr.test), fits


def alpha_points(pr: Problem, k: int) -> dict[str, dict]:
    """The per-class α scaling fitted on the first k training anchors, read as the networks are."""
    dH = {}
    for i in pr.test:
        B = np.asarray(pr.an.mols[i]["B"], float)
        dH[i] = B.T @ CT.alpha_scaling_baseline(pr.an.mols, pr.an.tensors, pr.train[:k], i) @ B
    return points_for(pr, dH)


def run_read(pr: Problem, n_train_order: int, log: Callable[[str], None]) -> dict:
    """Every milestone, the read-outs beside them and the rule's outcome."""
    zero = points_for(pr, {i: np.zeros_like(np.asarray(pr.an.mols[i]["H_low"], float)) for i in pr.test})
    as_is = points_for(pr, seed_mean([lambda i, n=n: CT.predict_cartesian(n.model, pr.an.tensors[i]) for n in pr.nets], pr.test))
    ks = R.milestones(pr.train, set(pr.train))
    table, alpha, fits, last_dH = {}, {}, {}, None
    for k in ks:
        last_dH, fits[k] = fit_milestone(pr, k, log)
        table[k] = points_for(pr, last_dH)
        alpha[k] = alpha_points(pr, k)
        log(f"k {k}: " + ", ".join(f"{f} {p['mean']:.2f}" for f, p in table[k].items()))
    n_atoms = {i: len(pr.an.mols[i]["masses"]) for i in pr.test}
    large = largest_quarter(pr.test, n_atoms) if pr.test else []
    size = {"ids": large, "atoms": [n_atoms[i] for i in large],
            "families": points_for(pr, last_dH, large) if last_dH is not None else None, "k": ks[-1] if ks else None}
    outcome = R.decide(curves_for_rule(table), {f: p["mean"] for f, p in as_is.items()}, len(pr.test), n_train_order)
    return {"milestones": ks, "zero_rule": zero, "proxy_as_is": as_is, "curves": table, "alpha_scaling": alpha, "fits": fits,
            "size_readout": size, "outcome": {"verdict": outcome.verdict, "k": outcome.k, "families": outcome.families, "reason": outcome.reason}}


def markdown(rec: dict) -> list[str]:
    def cell(p: dict | None) -> str:
        return "—" if p is None else f"{p['mean']:.2f} ({p['lo']:.2f}–{p['hi']:.2f})"

    out = rec["outcome"]
    lines = [f"# New CC anchors — read of {rec['date']}", "",
             f"**Outcome: {out['verdict']}{'' if out['k'] is None else f' at k = {out['k']}'}** — {out['reason']}.", "",
             f"Rule: `{REGISTRATION}`. Networks: {', '.join(rec['networks'])}. Training anchors finished in order: "
             f"{rec['n_train_finished_in_order']} of {rec['n_train_order']}; test anchors read: {len(rec['test_read'])} of {rec['n_test_listed']}.",
             "", "Seed-mean rms of the corrected band positions against composite CC, cm⁻¹ (95 % interval over molecules).", "",
             "| read | " + " | ".join(R.FAMILIES) + " |", "|---|" + "---|" * len(R.FAMILIES)]
    rows = [("zero rule (B3LYP)", rec["zero_rule"]), ("proxy networks as they are", rec["proxy_as_is"])]
    rows += [(f"R2 on k = {k}", rec["curves"][k]) for k in rec["milestones"]]
    rows += [(f"α scaling on k = {k}", rec["alpha_scaling"][k]) for k in rec["milestones"]]
    lines += [f"| {name} | " + " | ".join(cell(fams.get(f)) for f in R.FAMILIES) + " |" for name, fams in rows]
    size = rec["size_readout"]
    if size["families"] is not None:
        lines += ["", f"Size read-out at k = {size['k']}: the {len(size['ids'])} largest test anchors ({min(size['atoms'])}–{max(size['atoms'])} "
                      "atoms): " + ", ".join(f"{f} {cell(size['families'].get(f))}" for f in R.FAMILIES) + "."]
    held = rec.get("order_held_by")
    if held:
        lines += ["", f"The training order is held at position {held['position']} by {held['id']} ({held['why']}); "
                      f"{held['finished_behind_it']} training anchors behind it are finished and wait."]
    if rec["test_left_out"]:
        lines += ["", "Test anchors not read: " + "; ".join(f"{i} ({why})" for i, why in sorted(rec["test_left_out"].items())) + "."]
    return [*lines, "", f"{rec['seconds']} s."]


def write_record(prefix: Path, rec: dict) -> None:
    """The JSON record and its markdown table, each through a temporary file."""
    for path, text in ((prefix.with_suffix(".json"), json.dumps(rec, indent=1)), (prefix.with_suffix(".md"), "\n".join(markdown(rec)) + "\n")):
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(text, encoding="utf-8", newline="\n")
        os.replace(tmp, path)


def build_problem(a, entries: list[dict]) -> tuple[Problem, dict]:
    """The lists against the registry, the networks and the loaded anchors; and the record's header."""
    train_order, test_listed = read_ids(a.lists / "train_ids.txt"), read_ids(a.lists / "test_ids.txt")
    both = sorted(set(train_order) & set(test_listed))
    if both:
        raise SystemExit(f"in the training order and among the test anchors: {both} — a test anchor is never trained on")
    train_done, train_left = finished_anchors(train_order, entries)
    test_done, test_left = finished_anchors(test_listed, entries)
    train, order = training_head(train_order, train_done, train_left)
    test = sorted(test_done)
    paths, _ = PE.carried(a.m05)
    nets = load_networks(paths)
    used = {i: {**train_done, **test_done}[i] for i in [*train, *test]}
    verify_files(used, entries)
    an = CT.prepare_anchors(a.m05 / "corpus" / "molecules", {i: str(PLAN / e["path"]) for i, e in used.items()}, [], nets[0].cfg,
                            a.out.parent / "ls_targets")
    header = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "registration": REGISTRATION, "recipe": RECIPE,
              "early_stop": {"max_epochs": CT.EarlyStop().max_epochs, "val": CT.EarlyStop().val, "patience": CT.EarlyStop().patience,
                             "seed": "each network's own"},
              "lr": LR, "aux_weight": AUX_WEIGHT, "networks": [p.name for p in paths], "n_train_order": len(train_order),
              "n_train_finished": len(train_done), **order, "n_test_listed": len(test_listed),
              "test_read": test, "test_left_out": test_left,
              "anchors": {i: {"path": e["path"], "sha16": e["sha16"], "level": e["level"]} for i, e in used.items()}}
    return Problem(an, nets, train, test, a.m05 / "corpus" / "molecules"), header


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", required=True, type=Path, help="record prefix: <out>.json and <out>.md")
    ap.add_argument("--lists", type=Path, default=PLAN / "GoalGathering" / "notes" / "new_anchors_2026-11-21")
    ap.add_argument("--m05", type=Path, default=PLAN / "modules" / "05_support_predictor")
    ap.add_argument("--threads", type=int, default=4)
    a = ap.parse_args(argv)
    existing = [p for p in (a.out.with_suffix(".json"), a.out.with_suffix(".md")) if p.exists()]
    if existing:
        raise SystemExit(f"{existing[0]} exists — a read is written once; name another --out")
    if not 1 <= a.threads <= 8:
        raise SystemExit(f"--threads {a.threads}: 1 to 8 (the read runs beside other jobs)")
    import torch
    torch.set_num_threads(a.threads)
    t0 = time.time()
    pr, rec = build_problem(a, AR.load())
    rec.update(run_read(pr, rec["n_train_order"], log=lambda s: print(s, flush=True)))
    rec["seconds"] = round(time.time() - t0)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    write_record(a.out, rec)
    print("\n".join(markdown(rec)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
