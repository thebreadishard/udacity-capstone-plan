"""What must hold before release networks are shipped (decision 66; GoalGathering/notes/Design_2026-11-17_Measurement_and_Release_
Networks.md, §4): five checks, each with its numbers, in one record. A failed check is a refusal with its number, the record says
`passed: false`, and the pipeline then keeps the measurement networks as the product (`m08.pipeline.product_networks`).

    python probes/release_checks.py <release checkpoints> --measurement <measurement checkpoints>
                                    [--m05 <a module-05 folder holding corpus/molecules>] [--out <record prefix>]
                                    [--holdout NAME=FILE ...] [--sample 40] [--threads 2]
                                    [--previous-release <the previous version's release checkpoints>]

  1 same recipe      the release training's saved arguments differ from the measurement training's, seed by seed, in the kind only
                     (and in RUN_ONLY: where the run wrote, its threads, how the seeds were grouped into runs). `sizes` may differ
                     only where the measurement network trained on its whole pool, which is what the release's `all` says. A
                     setting a checkpoint does not hold because it was saved before the setting existed is read as the value of
                     `m05/rungC_settings_added.py` and named in the record; any other absent setting is a difference.
  2 no surprise      on a seeded sample of pool molecules that every network of both kinds trained on: per family, the rms
                     difference between the two kinds' corrected band positions (each kind's seed-mean ΔH, what the pipeline
                     prints) is at most the rms difference among the measurement networks' own seeds (single seeds, every pair).
  3 learnt           on each hold-out set (default: the clean hold-out (a) `a8` and the frozen hold-out (b)): per family, the
                     release networks' error — in-sample now — is below the measurement networks' held-out error; both are the
                     product's error (`product_error_read.molecule_read`: the corrected band positions of the seed-mean ΔH against
                     ωB97X). A set's molecule in a measurement network's training data, under any id, refuses the check.
  4 early stopping   no release seed's best epoch is at the cap: decision 51's rule as `v14_search.at_cap` has it.
  5 benzene by name  A_8448043181: every band's position under both kinds beside B3LYP and ωB97X, and its error per family; it
                     must be in the release networks' training data, and the record says how many of them fitted it (the others
                     stopped on it: inner validation). With --previous-release the previous version's release networks stand
                     beside them; a first release records 'none'. Nothing is compared: the numbers are for the reader.

What is loaded: the named checkpoints and the training record beside each (`<prefix>.json`); the corpus manifest (for check 3's
twins); and, molecule by molecule, the folders of the sampled pool molecules, the hold-out sets and benzene — geometry, the analytic
B3LYP Hessian and, for checks 3 and 5, the analytic ωB97X Hessian. The corpus loader is never called and no quantum chemistry is
run. The record is `<prefix>.json` and `.md` (default: `<release stem>_release_checks` beside the release checkpoints), each written
to a temporary file and moved over the target.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import torch

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
from m08 import pipeline as P  # noqa: E402  module 08 puts module 05's code and probes/ on the path

# isort: split
import holdout_twins as HT  # noqa: E402
import network_kind as NK  # noqa: E402
import product_error_read as PE  # noqa: E402
import rungC_intensities as RINT  # noqa: E402
import v14_search as V14  # noqa: E402
from learning_curve_layerA import molecule_features, normal_modes  # noqa: E402
from promotion_read import FAMILIES  # noqa: E402
from rungC_settings_added import RUN_ONLY, setting_differences  # noqa: E402

BENZENE = "A_8448043181"
SAMPLE_SEED = 20261117
SAMPLE_SIZE = 40
SUFFIX = "_release_checks"
PREVIOUS = "previous_release"
HOLDOUT_FILES = {"a8": "out/holdout_a_clean_2026-10-30.txt", "b": "corpus/holdout_b_frozen_2026-10-08.txt"}   # relative to --m05
CHECKS = ("same_recipe", "pool_agreement", "holdouts_learnt", "early_stopping", "benzene")
DEFINITIONS = {
    "same_recipe": "the checkpoints' saved arguments (the trainer's whole validated config), release against measurement of the same "
                   f"seed; ignored: {', '.join(RUN_ONLY)} and {NK.FIELD}",
    "pool_agreement": "per family, over the sampled molecules' bands: 'difference' = rms of (corrected band position under the release "
                      "networks' seed-mean ΔH − under the measurement networks' seed-mean ΔH); 'seed_spread' = rms of the same "
                      "difference between two single measurement seeds, over every pair; bands in the order of their B3LYP partners "
                      "(mode overlap), families by the certificate's rule. Under one distribution the seed means of three seeds "
                      "differ by about 0.58 of the single-seed spread, so the bound leaves that margin and no more",
    "holdouts_learnt": "per set and family: rms over the family's bands of the corrected band position's error against ωB97X, the "
                       "seed-mean ΔH of each kind (the licence's quantity); the release networks' is in-sample",
    "early_stopping": "per release seed: its best epoch, the epoch cap and v14_search.at_cap (constant rate: a best epoch within 10 % "
                      "of the cap); a seed without a best epoch trained without early stopping and is refused",
    "benzene": "per B3LYP mode of benzene, cm⁻¹: its position, its family, its ωB97X partner and its corrected position under each "
               "kind's seed-mean ΔH; per family the error of each kind against ωB97X",
}


@dataclass(frozen=True)
class Net:
    """One checkpoint as the checks read it: its kind and settings from its own saved arguments, and the training record beside it."""

    path: Path
    kind: str
    seed: int
    n: int
    args: dict
    train_ids: frozenset[str]
    record: dict


@dataclass(frozen=True)
class Check:
    """One check's outcome: every number it read, and the refusal — the reason with its number — when it did not pass."""

    name: str
    passed: bool
    numbers: dict
    refusal: str | None = None


@dataclass(frozen=True)
class Config:
    """What the checks are made on; refused combinations stop before any molecule is read."""

    release: tuple[Net, ...]
    measurement: tuple[Net, ...]
    molecules: Path
    holdouts: dict[str, Path]
    out: Path
    sample: int
    threads: int
    previous: tuple[Net, ...] = ()       # the previous version's release networks, for check 5; none for a first release

    def __post_init__(self) -> None:
        problems = [f"{n.path.name} is a {n.kind} network, named as a {want} one" for want, nets in
                    ((NK.RELEASE, self.release), (NK.MEASUREMENT, self.measurement), (NK.RELEASE, self.previous)) for n in nets if n.kind != want]
        seeds = [sorted(n.seed for n in nets) for nets in (self.release, self.measurement)]
        if seeds[0] != seeds[1] or len(set(seeds[0])) != len(seeds[0]):
            problems.append(f"the two kinds must hold the same seeds, one checkpoint each: release {seeds[0]}, measurement {seeds[1]}")
        if len(self.measurement) < 2:
            problems.append("check 2 needs at least two measurement seeds: their differences are its bound")
        if not self.molecules.is_dir():
            problems.append(f"no corpus/molecules at {self.molecules}")
        problems += [f"--holdout {name}: no file {path}" for name, path in self.holdouts.items() if not path.is_file()]
        if not 1 <= self.threads <= 8:
            problems.append(f"--threads {self.threads}: 1 to 8 (the checks run beside other jobs)")
        if self.sample < 1:
            problems.append(f"--sample {self.sample}: at least one molecule")
        if problems:
            raise SystemExit("release checks not started:\n  - " + "\n  - ".join(problems))

    def models(self, kind: str) -> tuple[Path, ...]:
        return tuple(n.path for n in (self.release if kind == NK.RELEASE else self.measurement))

    def compared(self) -> dict[str, tuple[Path, ...]]:
        """Check 5's columns: both kinds and, when given, the previous version's release networks."""
        both = {kind: self.models(kind) for kind in NK.KINDS}
        return both | ({PREVIOUS: tuple(n.path for n in self.previous)} if self.previous else {})


def load_net(path: Path) -> Net:
    """A checkpoint with the training record beside it; one without its record or its training ids cannot be checked."""
    if not path.is_file():
        raise SystemExit(f"{path}: no such checkpoint")
    ck = torch.load(path, map_location="cpu", weights_only=False)
    record = P.MR.result_record(path)
    if record is None or not ck.get("train_ids"):
        raise SystemExit(f"{path.name}: {'no training record beside it' if record is None else 'no training ids in it'}; the checks read both")
    return Net(path=path, kind=NK.kind_of_checkpoint(ck, path.name), seed=int(ck["seed"]), n=int(ck["n"]), args=dict(ck["args"]),
               train_ids=frozenset(ck["train_ids"]), record=record)


def same_recipe(release: tuple[Net, ...], measurement: tuple[Net, ...]) -> Check:
    """Check 1: seed by seed, the two trainings' saved arguments differ in the kind only."""
    by_seed = {m.seed: m for m in measurement}
    differences, whole_pool, read_as = {}, {}, {}
    for r in release:
        m = by_seed[r.seed]
        pairs, read_as[m.path.name], read_as[r.path.name] = setting_differences(m.args, r.args, {*RUN_ONLY, NK.FIELD})
        diff = {k: {NK.MEASUREMENT: mv, NK.RELEASE: rv} for k, (mv, rv) in pairs.items()}
        whole_pool[m.path.name] = NK.trained_on_whole_pool(m.record, m.n)
        if whole_pool[m.path.name] and r.args.get("sizes") == "all":
            diff.pop("sizes", None)                      # the measurement network trained on its whole pool, which is what 'all' says
        differences[r.path.name] = diff
    records = {n.path.name: NK.stated_kind(n.record, f"{n.path.name}'s training record") for n in (*release, *measurement)}
    contradicted = sorted(n.path.name for n in (*release, *measurement) if records[n.path.name] != n.kind)
    n_diff = sum(len(d) for d in differences.values())
    refusal = None
    if n_diff:
        named = sorted({k for d in differences.values() for k in d})
        refusal = f"{n_diff} setting(s) differ beside the kind: {', '.join(named)}"
    elif contradicted:
        refusal = f"{len(contradicted)} training record(s) state another kind than their checkpoint: {', '.join(contradicted)}"
    return Check("same_recipe", refusal is None, {"differences": differences, "measurement_trained_on_its_whole_pool": whole_pool,
                                                  "record_kinds": records, "ignored": [*RUN_ONLY, NK.FIELD],
                                                  "absent_settings_read_as": read_as}, refusal)


def seed_entry(net: Net) -> dict:
    """The checkpoint's own seed in the training record beside it."""
    return next(s for s in net.record["curve"][str(net.n)]["per_seed"] if s["seed"] == net.seed)


def early_stopping(release: tuple[Net, ...]) -> Check:
    """Check 4: decision 51 on every release seed, by `v14_search.at_cap`."""
    rows = {}
    for r in release:
        entry = seed_entry(r)
        read = V14.SeedRead({}, {}, entry.get("best_epoch"), int(r.record["epochs"]), {})
        schedule = r.record.get("lr_schedule", "constant")           # records before the schedule existed trained at a constant rate
        rows[r.path.name] = {"best_epoch": read.best_epoch, "cap": read.cap, "lr_schedule": schedule, "at_cap": V14.at_cap(read, schedule),
                             "read_as": V14.epoch_note(read, schedule)}
    bad = [f"{name} (best epoch {v['best_epoch']} of {v['cap']})" for name, v in rows.items() if v["at_cap"] or v["best_epoch"] is None]
    refusal = f"{len(bad)} release seed(s) stopped by the cap or trained without early stopping: {', '.join(bad)}" if bad else None
    return Check("early_stopping", not bad, {"seeds": rows, "cap_margin": V14.CAP_MARGIN}, refusal)


def low_hessian(folder: Path) -> tuple[np.ndarray, np.ndarray]:
    """(the analytic B3LYP Hessian, the masses) of a corpus folder."""
    with np.load(folder / P.RI.LOW_HESSIAN) as z:
        lo = np.array(z["H_projected"], float)
    return lo, np.asarray(json.loads((folder / "geometry.json").read_text(encoding="utf-8"))["masses_amu"], float)


def band_positions(lo: np.ndarray, masses: np.ndarray, dH: np.ndarray) -> np.ndarray:
    """The band positions of H_B3LYP + ΔH (cm⁻¹), in the order of the B3LYP modes: each band at the place of its partner by mode overlap."""
    _, _, V_low, _ = normal_modes(lo, masses)
    _, w, V, _ = normal_modes(lo + dH, masses)
    return w[RINT.match_modes(V_low, V)]


def pool_sample(nets: tuple[Net, ...], molecules: Path, size: int) -> tuple[list[str], int]:
    """(the sample, the number it was drawn from): pool molecules every network trained on that hold an analytic B3LYP Hessian, in id
    order, `size` of them drawn without replacement by SAMPLE_SEED."""
    common = frozenset.intersection(*(n.train_ids for n in nets))
    candidates = sorted(i for i in common if (molecules / i / P.RI.LOW_HESSIAN).is_file())
    drawn = np.random.default_rng(SAMPLE_SEED).choice(len(candidates), size=min(size, len(candidates)), replace=False)
    return [candidates[k] for k in sorted(drawn.tolist())], len(candidates)


def pool_agreement(cfg: Config) -> Check:
    """Check 2: on the sample, the two kinds differ by no more than the measurement seeds differ among themselves, per family."""
    ids, n_candidates = pool_sample((*cfg.release, *cfg.measurement), cfg.molecules, cfg.sample)
    difference: dict[str, list] = {f: [] for f in FAMILIES}
    spread: dict[str, list] = {f: [] for f in FAMILIES}
    for done, i in enumerate(ids, 1):
        folder = cfg.molecules / i
        lo, masses = low_hessian(folder)
        family = np.array(molecule_features(folder, lo=lo, hi=lo)["family"])         # the families follow the B3LYP modes alone
        release_mean = band_positions(lo, masses, P.correction(cfg.models(NK.RELEASE), folder)[0])
        mean, seeds = P.correction(cfg.models(NK.MEASUREMENT), folder)
        per_seed = [band_positions(lo, masses, d) for d in seeds]
        for f in FAMILIES:
            difference[f].append((release_mean - band_positions(lo, masses, mean))[family == f])
            spread[f] += [(per_seed[a] - per_seed[b])[family == f] for a in range(len(per_seed)) for b in range(a)]
        print(f"release checks: pool sample {done}/{len(ids)} {i}", flush=True)
    rows = {f: {"difference": PE.rms(difference[f]), "seed_spread": PE.rms(spread[f]), "n_bands": int(sum(len(x) for x in difference[f]))}
            for f in FAMILIES}
    over = [f"{f} ({v['difference']:.3f} against {v['seed_spread']:.3f} cm⁻¹)" for f, v in rows.items()
            if v["difference"] is not None and v["difference"] > v["seed_spread"]]
    refusal = None
    if not ids:
        refusal = "no pool molecule that every network trained on holds an analytic B3LYP Hessian: nothing to compare on"
    elif over:
        refusal = f"the kinds differ by more than the measurement seeds do in {len(over)} family(ies): {', '.join(over)}"
    return Check("pool_agreement", refusal is None, {"families": rows, "sample": ids, "drawn_from": n_candidates, "sample_seed": SAMPLE_SEED}, refusal)


def family_errors(ids: list[str], molecules: Path, models: tuple[Path, ...]) -> dict[str, dict]:
    """Per family the product's error over a set of molecules (`product_error_read.molecule_read`), with its number of bands."""
    reads = [PE.molecule_read(molecules / i, models) for i in ids]
    return {f: {"rms": PE.rms([r.band[r.band_family == f] for r in reads]), "n_bands": int(sum((r.band_family == f).sum() for r in reads))}
            for f in FAMILIES}


def holdout_set(name: str, path: Path, cfg: Config, keys: dict) -> tuple[dict, list[str]]:
    """(one hold-out set's numbers, the reasons to refuse it). Read on the listed molecules every release network trained on; the
    others are named as dropped. A molecule a measurement network trained on, by id or as a twin of any charge (TASKS 157, 253), makes
    its error no held-out one."""
    listed = read_ids(path)
    ids = [i for i in listed if all(i in r.train_ids for r in cfg.release)]
    trained = sorted(frozenset.union(*(m.train_ids for m in cfg.measurement)))
    leaked = sorted(set(ids) & set(trained)) + [f"{t} (a twin)" for t in HT.twins(trained, ids, keys, any_charge=True)]
    numbers = {"file": path.name, "n_listed": len(listed), "n_read": len(ids), "dropped_not_in_the_release_training_data": sorted(set(listed) - set(ids)),
               "in_a_measurement_networks_training_data": leaked}
    if not ids:
        return numbers, [f"({name}) no listed molecule is in the release networks' training data"]
    if leaked:
        return numbers, [f"({name}) {len(leaked)} molecule(s) are in a measurement network's training data ({', '.join(leaked[:5])}): its "
                         "error there is not a held-out one (TASKS 157, 253)"]
    errors = {kind: family_errors(ids, cfg.molecules, cfg.models(kind)) for kind in NK.KINDS}
    numbers["families"] = {f: {NK.RELEASE: errors[NK.RELEASE][f]["rms"], NK.MEASUREMENT: errors[NK.MEASUREMENT][f]["rms"],
                               "n_bands": errors[NK.RELEASE][f]["n_bands"]} for f in FAMILIES}
    not_below = [f"({name}) {f}: {v[NK.RELEASE]:.3f} in-sample against {v[NK.MEASUREMENT]:.3f} cm⁻¹ held out"
                 for f, v in numbers["families"].items() if v[NK.RELEASE] is not None and v[NK.RELEASE] >= v[NK.MEASUREMENT]]
    return numbers, not_below


def holdouts_learnt(cfg: Config) -> Check:
    """Check 3: on every hold-out set and in every family the release networks' in-sample error is below the measurement networks'."""
    keys = HT.manifest_keys(cfg.molecules)
    sets, reasons = {}, []
    for name, path in cfg.holdouts.items():
        sets[name], found = holdout_set(name, path, cfg, keys)
        reasons += found
        print(f"release checks: hold-out ({name}) read on {sets[name]['n_read']} molecules", flush=True)
    refusal = f"{len(reasons)} hold-out reading(s) not below the measurement networks' or not readable: {'; '.join(reasons)}" if reasons else None
    return Check("holdouts_learnt", refusal is None, {"sets": sets}, refusal)


def benzene(cfg: Config) -> Check:
    """Check 5: benzene's bands under both kinds, by name; refused only when it cannot be reported as a molecule the release trained on."""
    folder = cfg.molecules / BENZENE
    if not (folder / P.RI.LOW_HESSIAN).is_file() or not (folder / P.TRUTH_HESSIAN).is_file():
        return Check("benzene", False, {"molecule": BENZENE}, f"{BENZENE} has no analytic B3LYP and ωB97X Hessians under {cfg.molecules}: 0 bands reported")
    in_training = {kind: sorted(n.path.name for n in nets if BENZENE in n.train_ids)
                   for kind, nets in ((NK.RELEASE, cfg.release), (NK.MEASUREMENT, cfg.measurement))}
    lo, masses = low_hessian(folder)
    hi = PE.label_hessians(folder)[1]
    _, w_low, V_low, _ = normal_modes(lo, masses)
    _, w_ref, V_ref, _ = normal_modes(hi, masses)
    family = molecule_features(folder, lo=lo, hi=hi)["family"]
    compared = cfg.compared()
    position = {name: band_positions(lo, masses, P.correction(models, folder)[0]) for name, models in compared.items()}
    truth = w_ref[RINT.match_modes(V_low, V_ref)]
    bands = [{"b3lyp": round(float(w_low[k]), 2), "family": family[k], "wb97x": round(float(truth[k]), 2),
              **{name: round(float(position[name][k]), 2) for name in compared}} for k in range(len(w_low))]
    errors = {name: {f: v["rms"] for f, v in family_errors([BENZENE], cfg.molecules, models).items()} for name, models in compared.items()}
    fitted = sorted(r.path.name for r in cfg.release if BENZENE in r.train_ids and BENZENE not in seed_entry(r)["inner_val_ids"])
    missing = len(cfg.release) - len(in_training[NK.RELEASE])
    refusal = f"{missing} release network(s) did not train on {BENZENE}" if missing else None
    return Check("benzene", refusal is None, {"molecule": BENZENE, "in_training_data_of": in_training, "fitted_by_release_networks": fitted,
                                             PREVIOUS: [n.path.name for n in cfg.previous] or "none", "bands": bands, "family_error": errors},
                 refusal)


def read_ids(path: Path) -> list[str]:
    """The ids of a list file: one per line, '#' comments."""
    return [s.strip() for s in path.read_text(encoding="utf-8").splitlines() if s.strip() and not s.startswith("#")]


def markdown(record: dict) -> str:
    """The record for a reader: one line per check, every refusal, check 2's and 3's tables and benzene's bands."""
    c = record["checks"]
    lines = [f"# Release checks ({record['date']}) — {'PASSED' if record['passed'] else 'REFUSED: the release networks are not shipped'}", "",
             f"Release networks: {', '.join(record['release'])}. Measurement networks: {', '.join(record['measurement'])}. Decision 66, "
             "design note of 17 Nov 2026, §4.", "", "| check | passed | refusal |", "|---|---|---|"]
    lines += [f"| {k + 1} {name} | {'yes' if c[name]['passed'] else 'NO'} | {c[name]['refusal'] or ''} |" for k, name in enumerate(CHECKS)]
    lines += ["", f"## 2 Pool sample ({len(c['pool_agreement']['numbers']['sample'])} of {c['pool_agreement']['numbers']['drawn_from']} "
              "molecules; cm⁻¹)", "", "| family | release − measurement, seed means | among the measurement seeds | bands |", "|---|---|---|---|"]
    lines += [f"| {f} | {_cell(v['difference'])} | {_cell(v['seed_spread'])} | {v['n_bands']} |" for f, v in c["pool_agreement"]["numbers"]["families"].items()]
    for name, s in c["holdouts_learnt"]["numbers"]["sets"].items():
        lines += ["", f"## 3 Hold-out ({name}): {s['n_read']} of {s['n_listed']} listed molecules (cm⁻¹)", "",
                  "| family | release, in-sample | measurement, held out | bands |", "|---|---|---|---|"]
        lines += [f"| {f} | {_cell(v[NK.RELEASE])} | {_cell(v[NK.MEASUREMENT])} | {v['n_bands']} |" for f, v in s.get("families", {}).items()]
    benzene_numbers = c["benzene"]["numbers"]
    columns = [NK.MEASUREMENT, NK.RELEASE, *([PREVIOUS] if benzene_numbers.get(PREVIOUS, "none") != "none" else [])]
    lines += ["", f"## 5 Benzene ({BENZENE}), cm⁻¹", "",
              f"Fitted by {len(benzene_numbers.get('fitted_by_release_networks', []))} of {len(record[NK.RELEASE])} release networks (the others "
              f"stopped on it); previous version's release networks: {benzene_numbers.get(PREVIOUS, 'none') if PREVIOUS not in columns else 'beside'}.",
              "", "| B3LYP | family | ωB97X | " + " | ".join(c.replace("_", " ") for c in columns) + " |", "|---|---|---|" + "---|" * len(columns)]
    lines += [f"| {b['b3lyp']:.2f} | {b['family']} | {b['wb97x']:.2f} | " + " | ".join(f"{b[c]:.2f}" for c in columns) + " |"
              for b in benzene_numbers.get("bands", [])]
    return "\n".join(lines) + "\n"


def _cell(value: float | None) -> str:
    return "—" if value is None else f"{value:.3f}"


def write_record(prefix: Path, record: dict) -> None:
    """The JSON record and its markdown, each written to a temporary file and moved over the target."""
    prefix.parent.mkdir(parents=True, exist_ok=True)
    for path, content in ((Path(f"{prefix}.json"), json.dumps(record, indent=1, ensure_ascii=False)), (Path(f"{prefix}.md"), markdown(record))):
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(content, encoding="utf-8")
        os.replace(tmp, path)


def parse(argv: list[str] | None) -> Config:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("release", type=Path, nargs="+", help="the release networks' checkpoints, one per seed")
    ap.add_argument("--measurement", type=Path, nargs="+", required=True, help="the measurement networks' checkpoints of the same version and seeds")
    ap.add_argument("--m05", type=Path, default=P.M05, help="the module-05 folder whose corpus/molecules is read")
    ap.add_argument("--out", type=Path, default=None, help=f"the record's prefix (default: <release stem>{SUFFIX} beside the release checkpoints)")
    ap.add_argument("--holdout", action="append", default=[], metavar="NAME=FILE",
                    help="a hold-out set for check 3, repeatable (default: " + ", ".join(f"{k}=<m05>/{v}" for k, v in HOLDOUT_FILES.items()) + ")")
    ap.add_argument("--sample", type=int, default=SAMPLE_SIZE, help="check 2's number of pool molecules")
    ap.add_argument("--previous-release", type=Path, nargs="+", default=[],
                    help="check 5: the previous version's release checkpoints, set beside this one's on benzene (none for a first release)")
    ap.add_argument("--threads", type=int, default=2)
    a = ap.parse_args(argv)
    m05 = a.m05.resolve()
    holdouts = {name: m05 / rel for name, rel in HOLDOUT_FILES.items()}
    if a.holdout:
        if any("=" not in spec or not all(spec.partition("=")[::2]) for spec in a.holdout):
            raise SystemExit(f"--holdout {a.holdout}: NAME=FILE")
        holdouts = {spec.partition("=")[0]: Path(spec.partition("=")[2]).resolve() for spec in a.holdout}
    release = tuple(load_net(p.resolve()) for p in a.release)
    out = a.out.resolve() if a.out else release[0].path.parent / f"{PE.common_stem(tuple(n.path for n in release))}{SUFFIX}"
    return Config(release=release, measurement=tuple(load_net(p.resolve()) for p in a.measurement), molecules=m05 / "corpus" / "molecules",
                  holdouts=holdouts, out=out, sample=a.sample, threads=a.threads, previous=tuple(load_net(p.resolve()) for p in a.previous_release))


def main(argv: list[str] | None = None) -> int:
    cfg = parse(argv)
    started = time.time()
    torch.set_num_threads(cfg.threads)
    checks = [same_recipe(cfg.release, cfg.measurement), pool_agreement(cfg), holdouts_learnt(cfg), early_stopping(cfg.release), benzene(cfg)]
    refusals = [f"check {k + 1} ({c.name}): {c.refusal}" for k, c in enumerate(checks) if not c.passed]
    record = {"kind": "release checks", "date": time.strftime("%Y-%m-%d %H:%M"), "decision": "66 (design note of 17 Nov 2026, §4)",
              "passed": not refusals, "refusals": refusals,
              **{kind: [n.path.name for n in nets] for kind, nets in ((NK.RELEASE, cfg.release), (NK.MEASUREMENT, cfg.measurement))},
              "model_sha16": {n.path.name: P.sha16(n.path) for n in (*cfg.release, *cfg.measurement)},
              "checks": {c.name: {k: v for k, v in asdict(c).items() if k != "name"} for c in checks}, "definitions": DEFINITIONS,
              "data_root": str(cfg.molecules), "provenance": P.provenance(),
              "run": {"seconds": round(time.time() - started, 1), "peak_memory_gb": round(PE.peak_memory_gb(), 2), "threads": cfg.threads}}
    write_record(cfg.out, record)
    for line in refusals:
        print(f"REFUSED {line}", flush=True)
    print(f"release checks {'passed' if not refusals else 'REFUSED'}: record {cfg.out}.json", flush=True)
    return 0 if not refusals else 1


if __name__ == "__main__":
    sys.exit(main())
