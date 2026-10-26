"""Anchor set three's final read (GoalGathering/notes/PreRegistration_2026-10-12_Anchor_Set_Three.md): the lines of 12 Oct, the amendment
of 14 Oct (R-A, R-B and arm M along the anchor count) and the declaration of 19 Oct (the read is on waves 1-2: quinoxaline, azulene,
acenaphthylene, quinoline, isoquinoline; an anchor that fails promotion leaves the read by name).

plan — the runs of `m05/rungC_cc_transfer.py`, from the anchor registry, as chain_runner specs:
  R-A / R-B: the original six anchors held out (--held), the fine-tune pool of every fold the other five plus k_s new carried anchors,
    k_s in {0, 2, 4, all} (k_s = 0 is the 10 Oct read again, on today's code), the subsets of `anchor_subsets`, three seeds; the CC APTs of
    benzene and the three low-symmetry anchors for R-B.
  Arm M (and arm C, and the new anchors' own intensities): every carried anchor in, the new ones held out, --oop-diagonal-model with
    --oop-fit-sizes 4,8 and --oop-couplings-low, three seeds.
  Same models and arguments as the 10 Oct read (probes/runs/t3_folds_1010.json): chain 34's three carried models, 300 epochs, lr 1e-3,
  head L2 1 (lambda = 1), 8 threads. The first run is its own spec: its time is stated before the rest run (amendment of 14 Oct).
read — the registered verdicts from the runs' records (a manifest the plan writes names every run): R-A, R-B, arm M, arm C.

    python probes/anchor_set3_read.py plan <out_dir>     → <out_dir>/manifest.json, probes/runs/anchor_set3_{first,rest}.json
    python probes/anchor_set3_read.py read <out_dir>     → <out_dir>/read_set3.{json,md}
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
M05 = PLAN / "modules" / "05_support_predictor"
RESULTS = PLAN / "probes" / "results_m1"
RUNS = PLAN / "probes" / "runs"
sys.path.insert(0, str(M05 / "m05"))

ORIGINALS = {"A_8448043181": "benzene", "A_01f3186607": "naphthalene", "A_6e858b26e5": "pyridine", "B_8b12a55d3a": "fluorobenzene",
             "A_3100da3761": "benzonitrile", "A_a1e6ec1862": "anthracene"}
NEW = {"A_7aa232d4e9": "quinoxaline", "A_d9139359ab": "azulene", "A_45187bb7c8": "acenaphthylene", "A_ff98e1160d": "quinoline",
       "A_d09f8d1ef8": "isoquinoline"}
LOW_SYMMETRY = ("A_6e858b26e5", "B_8b12a55d3a", "A_3100da3761")          # R-B's three: pyridine, fluorobenzene, benzonitrile
FIELD = RESULTS / "cc_apt_field_2026-10-12"
APTS = {"A_8448043181": RESULTS / "e8_benzene_ccpvtz_oop_2026-10-03" / "apt_ccsd_t.npz",           # as in the 10 Oct read
        "A_6e858b26e5": FIELD / "pyridine_ccpvdz_field.npz", "B_8b12a55d3a": FIELD / "fluorobenzene_ccpvdz_field.npz",
        "A_3100da3761": FIELD / "benzonitrile_ccpvdz_field.npz",
        "A_7aa232d4e9": RESULTS / "e8_quinoxaline_ccpvdz_2026-10-13" / "apt_ccsd_t_field.npz",       # set three: the field route (item 2)
        "A_d9139359ab": RESULTS / "e8_azulene_ccpvdz_2026-10-14" / "apt_ccsd_t_field.npz",
        "A_45187bb7c8": RESULTS / "e8_acenaphthylene_ccpvdz_2026-10-16" / "apt_ccsd_t_field.npz",
        "A_ff98e1160d": RESULTS / "e8_quinoline_ccpvdz_2026-10-18" / "apt_ccsd_t_field.npz",
        "A_d09f8d1ef8": RESULTS / "e8_isoquinoline_ccpvdz_2026-10-19" / "apt_ccsd_t_field.npz"}
MODEL = "out/E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed{seed}.pt"
SEEDS = (0, 1, 2)
TRANSFER_ARGS = ["--threads", "8", "--epochs", "300", "--lr", "1e-3", "--head-l2", "1", "--fit-mode", "head_l2",   # the registered λ = 1
                 "--modes", "none,alpha,head,head_l2"]
KS_BELOW_ALL = (2, 4)                     # R-A's k_s besides 0 and 'all'
KT_BELOW_ALL = (4, 8)                     # arm M's k_t besides 'all'
TIER = "TZ"

STANDARD = "network_head_l2"              # lambda = 1, the TZ tier's standard column
LAMBDA0 = "network_head"
ARM_M = "network_head_l2_oopmodel"
ARM_C = "network_head_l2_ooplow"
ZERO = "zero_rule"
MATCHED = "intensity_rel_rms_matched"
LEVER = 0.20                              # R-A and arm M: >= 20 % lower
FLAT = 0.05                               # < 5 % lower: the flat / data-limited branch
OTHER_ALLOWANCE = 0.10                    # arm M: 'other' at most 10 % above lambda = 1's
ARM_C_OOP_CM = 1.0                        # arm C: CH-oop within 1.0 cm-1 of lambda = 1's
SE_FACTOR = 2.0                           # 'still learning': below the previous size by more than twice the combined standard error


@dataclass(frozen=True)
class Protocol:
    """How the transfer runs and which column R-A and R-B read: the registered read (12 Oct, λ = 1, with arms M and C) or the whole-head
    repeat (amendment of 21 Oct, after the night's diagnosis)."""
    name: str
    label: str
    suffix: str
    chain: str
    transfer_args: tuple[str, ...]
    standard: str
    beside: str | None
    arms: bool
    rb_wait: str
    rb_stands: str


REGISTERED = Protocol("registered", "lambda = 1", "", "S3", tuple(TRANSFER_ARGS), STANDARD, LAMBDA0, True,
                      "the lambda question waits for anchor set four (the error is still falling with k_s)",
                      "the lambda question stands: a chain to re-choose lambda on frequencies and intensities together is registered")
HEAD_ALL = Protocol("head_all", "whole head", "_headall", "S3H",
                    ("--threads", "8", "--epochs", "300", "--lr", "1e-3", "--modes", "head_all"), "network_head_all", None, False,
                    "the shape question waits for anchor set four (the error is still falling with k_s)",
                    "the shape question stands: the whole head does not repair the shapes at this count")
PROTOCOLS = {p.name: p for p in (REGISTERED, HEAD_ALL)}


# ---- plan

@dataclass(frozen=True)
class Run:
    """One run of the transfer script: its arm ('RA' or 'M'), k (new anchors in the pool; -1 for arm M), subset index and seed."""
    arm: str
    k: int
    subset: int
    seed: int
    anchors: tuple[str, ...]
    held: tuple[str, ...]
    prefix: str


def plan_runs(new_carried: list[str], out_rel: str, arms: bool = True) -> list[Run]:
    """R-A for every k_s and subset and seed, then (with `arms`) arm M per seed; `out_rel` is the output folder relative to module 05."""
    import rungC_cc_transfer as CT

    n_new = len(new_carried)
    sizes = [0, *[k for k in KS_BELOW_ALL if k < n_new], n_new] if n_new else [0]
    runs = []
    for seed in SEEDS:
        for k in sizes:
            for j, sub in enumerate(CT.anchor_subsets(new_carried, k) if k else [()]):
                runs.append(Run("RA", k, j, seed, (*ORIGINALS, *sub), tuple(ORIGINALS), f"{out_rel}/RA_k{k}_s{j}_seed{seed}"))
    if n_new and arms:
        runs += [Run("M", -1, 0, seed, (*ORIGINALS, *new_carried), tuple(new_carried), f"{out_rel}/M_seed{seed}") for seed in SEEDS]
    return runs


def run_argv(run: Run, files: dict[str, str], protocol: Protocol = REGISTERED, molecules: str = "corpus/molecules") -> list[str]:
    """The transfer script's command line for a run; `files` maps every anchor id to its carried TZ file."""
    argv = ["{python}", "m05/rungC_cc_transfer.py", molecules, MODEL.format(seed=run.seed), run.prefix, *protocol.transfer_args]
    for i in run.anchors:
        argv += ["--anchor", f"{i}={files[i]}"]
    for i in run.anchors:
        if i in APTS:
            argv += ["--apt", f"{i}={APTS[i].as_posix()}"]
    argv += [x for h in run.held for x in ("--held", h)]
    if run.arm == "M":
        sizes = [k for k in KT_BELOW_ALL if k < len(run.anchors) - 1]
        argv += ["--oop-diagonal-model", "--oop-couplings-low"] + (["--oop-fit-sizes", ",".join(map(str, sizes))] if sizes else [])
    return argv


def chain_spec(name: str, about: str, runs: list[Run], files: dict[str, str], protocol: Protocol = REGISTERED,
               molecules: str = "corpus/molecules") -> dict:
    steps = [{"kind": "cmd", "label": Path(r.prefix).name, "cwd": "modules/05_support_predictor",
              "log": f"modules/05_support_predictor/{r.prefix}.log", "argv": run_argv(r, files, protocol, molecules)} for r in runs]
    return {"_about": about, "name": name, "steps": steps,
            "outputs": [f"modules/05_support_predictor/{r.prefix}.json" for r in runs]}


def carried_files(entries: list[dict] | None = None) -> tuple[dict[str, str], list[str]]:
    """The carried TZ file of every original and every new anchor. A new anchor whose promotion failed (a TZ entry that is not carried,
    as composite_promote.py registers it) is named and leaves the read; one with no TZ entry has not been promoted yet, and the plan waits."""
    import anchor_registry as AR

    entries = AR.load() if entries is None else entries
    files, left, undecided = {}, [], []
    for i in (*ORIGINALS, *NEW):
        e = AR.carried(i, entries)
        if e is not None and e["tier"] == TIER:
            files[i] = (PLAN / e["path"]).as_posix()
        elif i in ORIGINALS:
            raise SystemExit(f"original anchor {ORIGINALS[i]} ({i}) has no carried {TIER} entry: the read compares against all six")
        elif any(x["mol_id"] == i and x["tier"] == TIER for x in entries):
            left.append(i)
        else:
            undecided.append(NEW[i])
    if undecided:
        raise SystemExit(f"not promoted yet: {undecided} - the read is on all five, an anchor leaves it only by failing its promotion")
    return files, left


def check_inputs(files: dict[str, str]) -> None:
    """Before any run: every CC APT matches its corpus geometry and every model is carried (the runs would refuse later, one by one)."""
    import model_registry as MR
    import rungC_cc_transfer as CT

    for i in files:
        if i in APTS:
            CT.load_cc_apt(APTS[i], M05 / "corpus" / "molecules" / i)
    for seed in SEEDS:
        MR.require_carried(M05 / MODEL.format(seed=seed))


def write_json(path: Path, obj) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(obj, indent=1), encoding="utf-8", newline="\n")
    os.replace(tmp, path)


def plan(out_dir: Path, entries: list[dict] | None = None, check: bool = True, runs_dir: Path = RUNS,
         protocol: Protocol = REGISTERED, molecules: str = "corpus/molecules") -> dict:
    files, left = carried_files(entries)
    new_carried = [i for i in NEW if i in files]
    if check:
        check_inputs(files)
    out_rel = Path(os.path.relpath(out_dir, M05)).as_posix()
    runs = plan_runs(new_carried, out_rel, protocol.arms)
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest = {"new_carried": new_carried, "left_the_read": {i: NEW[i] for i in left}, "files": files, "protocol": protocol.name,
                "molecules": molecules, "runs": [r.__dict__ for r in runs]}
    write_json(out_dir / "manifest.json", manifest)
    about = f"Anchor set three's read, protocol {protocol.name} (probes/anchor_set3_read.py plan): "
    stem = f"anchor_set3{protocol.suffix}"
    write_json(runs_dir / f"{stem}_first.json", chain_spec(f"{protocol.chain}F", about + "the first run alone, timed before the rest run.",
                                                          runs[:1], files, protocol, molecules))
    write_json(runs_dir / f"{stem}_rest.json", chain_spec(f"{protocol.chain}R", about + "every run after the first.", runs[1:], files, protocol,
                                                         molecules))
    print(f"{len(runs)} runs ({sum(r.arm == 'RA' for r in runs)} R-A, {sum(r.arm == 'M' for r in runs)} arm M); new carried "
          f"{[NEW[i] for i in new_carried]}; left the read {[NEW[i] for i in left] or 'none'}")
    return manifest


# ---- read

@dataclass(frozen=True)
class Point:
    """One size on a curve: the mean over subsets and seeds of a per-run mean, and its standard error."""
    k: int
    mean: float
    se: float
    n: int


def finite(x, what: str) -> float:
    v = float(x)
    if not math.isfinite(v):
        raise ValueError(f"{what}: {v}")
    return v


def family(fold: dict, col: str, fam: str) -> float:
    return of_family(fold[col], fam, col)


def of_family(column: dict, fam: str, what: str) -> float:
    return finite(column["freq_rms_by_family"][fam], f"{what} {fam}")


def matched(fold: dict, col: str) -> float:
    return finite(fold[col]["intensity"][MATCHED], f"{col} {MATCHED}")


def point(k: int, values: list[float]) -> Point:
    v = np.asarray(values, float)
    se = float(v.std(ddof=1) / np.sqrt(len(v))) if len(v) > 1 else 0.0
    return Point(k, float(v.mean()), se, len(v))


def curve(records: list[tuple[Run, dict]], per_run) -> list[Point]:
    """Per k, the point of `per_run(record)` over that k's runs (subsets and seeds), ascending in k."""
    ks = sorted({r.k for r, _ in records})
    return [point(k, [per_run(rec) for r, rec in records if r.k == k]) for k in ks]


def lower_by(value: float, reference: float, share: float) -> bool:
    """value is at least `share` below reference (as a product: a value on the line counts as on it)."""
    return value <= (1 - share) * reference


def still_learning(c: list[Point]) -> bool:
    """The amendment's test: the error at 'all' (the last point) is below the previous size's by more than twice the combined standard
    error, and that last step is downward."""
    if len(c) < 2:
        return False
    last, prev = c[-1], c[-2]
    return last.mean < prev.mean and prev.mean - last.mean > SE_FACTOR * math.hypot(last.se, prev.se)


def mean_over(fold_ids, record: dict, value) -> float:
    return float(np.mean([value(record["folds"][i]) for i in fold_ids]))


def ra_read(records: list[tuple[Run, dict]], protocol: Protocol = REGISTERED) -> dict:
    """R-A: the original six's leave-one-out error along k_s; the line on CH-oop of the protocol's standard column, 'other' and the
    column beside it (the registered read's lambda = 0) reported."""
    ra = [(r, rec) for r, rec in records if r.arm == "RA"]
    cols = [c for c in (protocol.standard, protocol.beside) if c]
    curves = {f"{col} {fam}": curve(ra, lambda rec, col=col, fam=fam: mean_over(ORIGINALS, rec, lambda f: family(f, col, fam)))
              for col in cols for fam in ("CH-oop", "other")}
    c = curves[f"{protocol.standard} CH-oop"]
    if c[0].k != 0 or len(c) < 2:
        raise ValueError("R-A needs the k_s = 0 baseline and at least one size with new anchors")
    reduction = 1 - c[-1].mean / c[0].mean
    learning = still_learning(c)
    if lower_by(c[-1].mean, c[0].mean, LEVER):
        verdict = "more anchors move T3 where it is weakest (>= 20 % lower)"
    elif not lower_by(c[-1].mean, c[0].mean, FLAT):
        verdict = ("data-limited: anchors are still the lever at this count; anchor set four is priced and put to the user, the structural "
                   "change registered beside it" if learning else
                   "flat: anchors at this count are not the lever for the out-of-plane block; the structural change is registered next")
    else:
        verdict = "between: noted"
    return {"reduction": reduction, "still_learning": learning, "verdict": verdict, "curves": curves}


def rb_read(records: list[tuple[Run, dict]], protocol: Protocol = REGISTERED) -> dict:
    """R-B: lambda = 1's matched intensity error against the zero rule on the three low-symmetry anchors, with the enlarged pool ('all');
    along k_s, the mean over the three."""
    ra = [(r, rec) for r, rec in records if r.arm == "RA"]
    k_all = max(r.k for r, _ in ra)
    at_all = [rec for r, rec in ra if r.k == k_all]
    col = protocol.standard
    per_anchor = {i: {"standard": float(np.mean([matched(rec["folds"][i], col) for rec in at_all])),
                      "zero_rule": float(np.mean([matched(rec["folds"][i], ZERO) for rec in at_all]))} for i in LOW_SYMMETRY}
    below = sum(v["standard"] < v["zero_rule"] for v in per_anchor.values())
    c = curve(ra, lambda rec: mean_over(LOW_SYMMETRY, rec, lambda f: matched(f, col)))
    learning = still_learning(c)
    passed = below >= 2
    verdict = "anchors repair the shapes" if passed else protocol.rb_wait if learning else protocol.rb_stands
    return {"below_zero_rule": below, "passed": passed, "still_falling": learning, "verdict": verdict, "per_anchor": per_anchor, "curve": c}


def two_thirds(count: int, n: int) -> bool:
    return 3 * count >= 2 * n


def arm_m_read(records: list[tuple[Run, dict]], rb_passed: bool) -> dict:
    """Arm M on the new anchors' folds: the model's out-of-plane block against lambda = 1, at 'all' and along k_t."""
    m = [rec for r, rec in records if r.arm == "M"]
    new = sorted(m[0]["folds"])
    n_train = len(m[0]["folds"][new[0]]["train"])

    def at(fold: dict, k: str, j: int) -> dict:
        return fold[ARM_M] if k == "all" else fold["oop_fit_subsets"][k][j]["read"]

    kts = sorted(m[0]["folds"][new[0]].get("oop_fit_subsets", {}), key=int)
    c = []
    for k in [*kts, "all"]:
        n_sub = 1 if k == "all" else len(m[0]["folds"][new[0]]["oop_fit_subsets"][k])
        values = [float(np.mean([of_family(at(rec["folds"][i], k, j), "CH-oop", f"arm M k_t {k}") for i in new]))
                  for rec in m for j in range(n_sub)]
        c.append(point(n_train if k == "all" else int(k), values))
    lam_oop = float(np.mean([family(rec["folds"][i], STANDARD, "CH-oop") for rec in m for i in new]))
    lam_other = float(np.mean([family(rec["folds"][i], STANDARD, "other") for rec in m for i in new]))
    arm_other = float(np.mean([family(rec["folds"][i], ARM_M, "other") for rec in m for i in new]))
    reduction = 1 - c[-1].mean / lam_oop
    other_rise = arm_other / lam_other - 1
    intens = {i: (float(np.mean([matched(rec["folds"][i], ARM_M) for rec in m])), float(np.mean([matched(rec["folds"][i], STANDARD) for rec in m])))
              for i in new}
    intens_ok = two_thirds(sum(a <= s for a, s in intens.values()), len(new))
    learning = still_learning(c)
    adopt = lower_by(c[-1].mean, lam_oop, LEVER) and arm_other <= (1 + OTHER_ALLOWANCE) * lam_other and intens_ok
    if adopt:
        verdict = ("its lines hold, but R-B passed: not adopted as it stands; the variant with the model's diagonal and the network's couplings "
                   "is registered" if rb_passed else "adopt: the standard's out-of-plane block becomes the model's")
    elif not lower_by(c[-1].mean, lam_oop, FLAT):
        verdict = "data-limited: read again with anchor set four" if learning else "fails out of sample"
    else:
        verdict = "between: noted"
    return {"reduction": reduction, "other_rise": other_rise, "intensity_at_or_below": intens_ok, "still_learning": learning,
            "adopted": adopt and not rb_passed, "verdict": verdict, "curve": c, "lambda1_ch_oop": lam_oop,
            "intensity": {i: {"arm_m": a, "standard": s} for i, (a, s) in intens.items()}}


def arm_c_read(records: list[tuple[Run, dict]], rb_passed: bool, m_adopted: bool) -> dict:
    """Arm C, read only when R-B fails and arm M is not adopted: the out-of-plane couplings from the low level."""
    if rb_passed or m_adopted:
        return {"read": False, "verdict": "not read: " + ("R-B passed" if rb_passed else "arm M is adopted")}
    m = [rec for r, rec in records if r.arm == "M"]
    new = sorted(m[0]["folds"])
    intens = {i: (float(np.mean([matched(rec["folds"][i], ARM_C) for rec in m])), float(np.mean([matched(rec["folds"][i], STANDARD) for rec in m])))
              for i in new}
    below = sum(c < s for c, s in intens.values())
    oop_c = float(np.mean([family(rec["folds"][i], ARM_C, "CH-oop") for rec in m for i in new]))
    oop_s = float(np.mean([family(rec["folds"][i], STANDARD, "CH-oop") for rec in m for i in new]))
    adopt = two_thirds(below, len(new)) and abs(oop_c - oop_s) <= ARM_C_OOP_CM
    return {"read": True, "adopted": adopt, "verdict": "adopt" if adopt else "not adopted", "intensity_below": below,
            "ch_oop_arm_c": oop_c, "ch_oop_standard": oop_s, "intensity": {i: {"arm_c": c, "standard": s} for i, (c, s) in intens.items()}}


def new_anchor_intensities(records: list[tuple[Run, dict]]) -> dict:
    """Reported, no line: each new anchor's matched intensity error (lambda = 1 and the zero rule), a held-out fold each."""
    m = [rec for r, rec in records if r.arm == "M"]
    return {i: {"standard": float(np.mean([matched(rec["folds"][i], STANDARD) for rec in m])),
                "zero_rule": float(np.mean([matched(rec["folds"][i], ZERO) for rec in m]))} for i in sorted(m[0]["folds"])}


def load_records(out_dir: Path) -> tuple[dict, list[tuple[Run, dict]]]:
    manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    records = []
    for d in manifest["runs"]:
        run = Run(**{**d, "anchors": tuple(d["anchors"]), "held": tuple(d["held"])})
        path = M05 / f"{run.prefix}.json"
        if not path.exists():
            raise SystemExit(f"{path}: missing - the read waits for every run of the manifest")
        rec = json.loads(path.read_text(encoding="utf-8"))
        if sorted(rec["folds"]) != sorted(run.held):
            raise SystemExit(f"{path}: folds {sorted(rec['folds'])}, the manifest holds out {sorted(run.held)}")
        records.append((run, rec))
    return manifest, records


def read_all(records: list[tuple[Run, dict]], protocol: Protocol = REGISTERED) -> dict:
    ra, rb = ra_read(records, protocol), rb_read(records, protocol)
    has_m = any(r.arm == "M" for r, _ in records)
    m = arm_m_read(records, rb["passed"]) if has_m else None
    c = arm_c_read(records, rb["passed"], bool(m and m["adopted"])) if has_m else None
    return {"R-A": ra, "R-B": rb, "arm M": m, "arm C": c, "new_anchor_intensities": new_anchor_intensities(records) if has_m else None}


def _jsonable(x):
    if isinstance(x, Point):
        return x.__dict__
    if isinstance(x, dict):
        return {k: _jsonable(v) for k, v in x.items()}
    if isinstance(x, list | tuple):
        return [_jsonable(v) for v in x]
    return x


def _curve_text(c: list[Point]) -> str:
    return "; ".join(f"k {p.k}: {p.mean:.2f} ± {p.se:.2f} (n {p.n})" for p in c)


def report_lines(res: dict, manifest: dict, protocol: Protocol = REGISTERED) -> list[str]:
    ra, rb, m, c = res["R-A"], res["R-B"], res["arm M"], res["arm C"]
    lab = protocol.label
    title = "the final read" if protocol is REGISTERED else f"the read with protocol {protocol.name} ({lab})"
    lines = [f"# Anchor set three — {title}", "",
             f"New carried anchors: {', '.join(NEW[i] for i in manifest['new_carried'])}; left the read: "
             f"{', '.join(manifest['left_the_read'].values()) or 'none'}.", "",
             f"**R-A** (CH-oop, {lab}, the original six): {ra['reduction']:+.1%} lower at 'all' than at k_s = 0; still learning: "
             f"{ra['still_learning']}. **{ra['verdict']}.**", ""]
    lines += [f"- {name}: {_curve_text(cv)}" for name, cv in ra["curves"].items()]
    lines += ["", f"**R-B** (matched intensity, {lab} below the zero rule on {rb['below_zero_rule']} of 3; along k_s still falling: "
              f"{rb['still_falling']}). **{rb['verdict']}.**", ""]
    lines += [f"- {ORIGINALS[i]}: {lab} {v['standard']:.3f}, zero rule {v['zero_rule']:.3f}" for i, v in rb["per_anchor"].items()]
    lines.append(f"- mean of the three along k_s: {_curve_text(rb['curve'])}")
    if m:
        lines += ["", f"**Arm M** (new anchors' folds): CH-oop {m['reduction']:+.1%} below lambda = 1's {m['lambda1_ch_oop']:.2f} cm-1; 'other' "
                  f"{m['other_rise']:+.1%}; intensity at or below lambda = 1 on two thirds: {m['intensity_at_or_below']}; still learning: "
                  f"{m['still_learning']}. **{m['verdict']}.**", "", f"- along k_t: {_curve_text(m['curve'])}"]
        lines += ["", f"**Arm C**: {c['verdict']}" + (f" (intensity below on {c['intensity_below']}; CH-oop {c['ch_oop_arm_c']:.2f} against "
                                                      f"{c['ch_oop_standard']:.2f})" if c["read"] else "") + "."]
        lines += ["", "New anchors' own intensities (matched rel. rms, reported, no line):", ""]
        lines += [f"- {NEW[i]}: lambda = 1 {v['standard']:.3f}, zero rule {v['zero_rule']:.3f}" for i, v in res["new_anchor_intensities"].items()]
    return lines


def read(out_dir: Path) -> dict:
    manifest, records = load_records(out_dir)
    protocol = PROTOCOLS[manifest.get("protocol", REGISTERED.name)]
    res = read_all(records, protocol)
    write_json(out_dir / "read_set3.json", _jsonable(res))
    lines = report_lines(res, manifest, protocol)
    tmp = out_dir / "read_set3.md.tmp"
    tmp.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    os.replace(tmp, out_dir / "read_set3.md")
    print("\n".join(lines))
    return res


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("action", choices=("plan", "read"))
    ap.add_argument("out_dir", type=Path)
    ap.add_argument("--protocol", choices=sorted(PROTOCOLS), default=REGISTERED.name, help="plan: the registered read or the whole-head repeat")
    ap.add_argument("--molecules", default="corpus/molecules", help="plan: the corpus folder the runs read (the validated eleven-anchor copy)")
    a = ap.parse_args(argv)
    if a.action == "plan":
        plan(a.out_dir.resolve(), protocol=PROTOCOLS[a.protocol], molecules=a.molecules)
    else:
        read(a.out_dir.resolve())
    return 0


if __name__ == "__main__":
    sys.exit(main())
