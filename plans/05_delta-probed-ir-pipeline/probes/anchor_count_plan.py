"""The anchor count under the change the anchors measured (TASKS 82; the user, 29 Oct 2026: 'Doe de nieuwe proef met de betere check'):
where does arm (c)'s CH-oop curve cross 3 cm⁻¹ between k = 100 and 200 under the early-stopped recipe, with a control that reads each
fine-tune against its own base? Registration: `GoalGathering/notes/PreRegistration_2026-10-29_Anchor_Count.md`.

The recipe follow-up's CH-stretch control compared the two arms' fine-tuned models directly and so also counted the gap their bases
already had; G′ compares each run's change from its own base. Arms (c) and (a2) are the follow-up's bases; `plan` refuses to write the
chain unless their inputs differ only by the distortion.

    python probes/anchor_count_plan.py plan <out_dir>   # the input gate, then the chain file probes/runs/anchor_count.json
    python probes/anchor_count_plan.py read <out_dir>   # the registered lines → anchor_count_read.json/.md
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import anchor_price_plan as AP
import anchor_recipe_plan as AR
import proxy_check_plan as PC

M05, RUNS = PC.M05, PC.RUNS
AP_DIR, AR_DIR = AR.AP_DIR, M05 / "out" / "anchor_recipe_2026-10-28"
FAMILIES = PC.FAMILIES
SIZES = (100, 120, 150, 170, 200)
R0, R1, R2 = (AR.RECIPES[r] for r in ("R0", "R1", "R2"))
C_MODES = (R2, R1, R0)             # R2 is read (the follow-up's validation rule); R1 and R0 are reported beside it
ES_MAX_EPOCHS = 120                # decision 51: one of arm (c)'s R2 runs at k = 200 kept an epoch within 10 % of the follow-up's 60
G_FAILS_ALLOWED = 1                # G′ holds when it fails at no more than one of the five k
LINE_CM = AP.LINE_CM
LABELS = re.compile(r"analytic second-route Hessians substituted for (\d+) molecules")


# ------------------------------------------------------------------------------------------------------------------- the input gate
def chain_argv(chain: str, label: str) -> list[str]:
    """A step's command as its chain file states it."""
    return next(s["argv"] for s in json.loads((RUNS / chain).read_text(encoding="utf-8"))["steps"] if s["label"] == label)


def without(argv: list[str], flag: str) -> tuple[list[str], str]:
    """The command without `flag` and its value, and that value; refused when the flag is not there once."""
    if argv.count(flag) != 1:
        raise SystemExit(f"{flag} appears {argv.count(flag)} times in the base's command, once expected")
    i = argv.index(flag)
    return argv[:i] + argv[i + 2:], argv[i + 1]


def substituted_labels(log: str) -> int:
    counts = set(LABELS.findall(log))
    if len(counts) != 1:
        raise SystemExit(f"a base log states the substituted analytic labels {sorted(counts) or 'nowhere'}, once expected")
    return int(counts.pop())


def input_gate(argv_c: list[str], argv_a2: list[str], log_c: str, log_a2: str, distortion: dict) -> dict:
    """Refused unless the two bases' commands differ only by the distortion flags (and the output prefix, argv[3]), both logs state the
    same number of substituted analytic labels, and CH-stretch's factor is arm (a2)'s family scale in arm (c)'s mean and rest."""
    rest_c, _ = without(argv_c, "--distortion-file")
    rest_a2, scales = without(argv_a2, "--family-scale")
    if rest_c[:3] + rest_c[4:] != rest_a2[:3] + rest_a2[4:]:
        raise SystemExit("the bases' commands differ beyond the distortion flags and the output prefix")
    n_c, n_a2 = substituted_labels(log_c), substituted_labels(log_a2)
    if n_c != n_a2:
        raise SystemExit(f"the bases substituted {n_c} and {n_a2} analytic labels")
    stretch = float(dict(s.split("=") for s in scales.split(","))["CH-stretch"])
    c_stretch = distortion["families"]["CH-stretch"]
    if not stretch == c_stretch["mean"] == c_stretch["rest"]:
        raise SystemExit(f"CH-stretch's factor: arm (a2) {stretch}, arm (c) mean {c_stretch['mean']} rest {c_stretch['rest']}")
    return {"labels": n_c, "ch_stretch_factor": stretch}


# ------------------------------------------------------------------------------------------------------------------------------- plan
def c_name(k: int, s: int) -> str:
    return f"c_k{k}_seed{s}"


def a2_name(k: int, s: int) -> str:
    return f"a2_k{k}_seed{s}"


def steps(out_rel: str, n_pool: int) -> list[dict]:
    """The chain: arm (c)'s R2/R1/R0 and arm (a2)'s R2 at every k, each seed along k."""
    ap_rel = Path(os.path.relpath(AP_DIR, M05)).as_posix()
    ar_rel = Path(os.path.relpath(AR_DIR, M05)).as_posix()
    out = [AR.fine_tune_step(out_rel, c_name(k, s), AP.base_model(ap_rel, n_pool, s), k, list(C_MODES), ES_MAX_EPOCHS)
           for s in PC.SEEDS for k in SIZES]
    out += [AR.fine_tune_step(out_rel, a2_name(k, s), AR.base_a2_model(ar_rel, n_pool, s), k, [R2], ES_MAX_EPOCHS)
            for s in PC.SEEDS for k in SIZES]
    return out


def plan(out_dir: Path) -> Path:
    n_pool = AR.proxy_manifest()["pool"]["a"]
    gate = input_gate(chain_argv("anchor_price.json", "base_c"), chain_argv("anchor_recipe.json", "base_a2"),
                      (AP_DIR / "base_c.log").read_text(encoding="utf-8"), (AR_DIR / "base_a2.log").read_text(encoding="utf-8"),
                      json.loads((AP_DIR / "distortion.json").read_text(encoding="utf-8")))
    needed = [AP_DIR / f"base_c_model_n{n_pool}_seed{s}.pt" for s in PC.SEEDS] + [AR_DIR / f"base_a2_model_n{n_pool}_seed{s}.pt"
                                                                                   for s in PC.SEEDS]
    if missing := [p.name for p in needed if not p.exists()]:
        raise SystemExit(f"the bases are missing: {missing}")
    out_dir.mkdir(parents=True, exist_ok=True)
    st = steps(Path(os.path.relpath(out_dir, M05)).as_posix(), n_pool)
    spec = {"_about": f"anchor count: probes/anchor_count_plan.py plan; input gate {gate}", "name": "AC", "steps": st,
            "outputs": [f"modules/05_support_predictor/{s['argv'][4]}.json" for s in st]}
    path = RUNS / "anchor_count.json"
    PC.write_text(path, json.dumps(spec, indent=1))
    return path


# ------------------------------------------------------------------------------------------------------------------------------- read
def stretch_change(records: list[dict], mode: str) -> list[float]:
    """Per (seed, draw): the fine-tuned CH-stretch minus that seed's base as it is (the record's 'none' read)."""
    return [d["modes"][mode]["read"]["family_mean"]["CH-stretch"] - r["none"]["family_mean"]["CH-stretch"] for r in records
            for d in r["draws"]]


def control(c_by_k: dict[int, list[dict]], a2_by_k: dict[int, list[dict]]) -> dict:
    """G′ per k: arm (c)'s change from its base above arm (a2)'s by twice the combined se is a failure; it holds with at most
    G_FAILS_ALLOWED failures."""
    per_k = {}
    for k in SIZES:
        dc, da2 = PC.mean_se(stretch_change(c_by_k[k], R2)), PC.mean_se(stretch_change(a2_by_k[k], R2))
        per_k[k] = {"c": dc, "a2": da2, "fails": PC.lower(da2, dc)}
    fails = sum(v["fails"] for v in per_k.values())
    return {"per_k": per_k, "fails": fails, "holds": fails <= G_FAILS_ALLOWED}


def crossings(by_k: dict[int, dict]) -> dict[str, dict]:
    """Per family the k at the line on the mean curve, and on the mean − se and mean + se curves (its range)."""
    out = {}
    for fam in FAMILIES:
        col = {k: by_k[k]["family"][fam] for k in SIZES}
        out[fam] = {"k": AP.crossing({k: v[0] for k, v in col.items()}),
                    "low": AP.crossing({k: v[0] - v[1] for k, v in col.items()}),
                    "high": AP.crossing({k: v[0] + v[1] for k, v in col.items()})}
    return out


def outcome(ctrl: dict, cap_binds: bool, n: float | None) -> str:
    if not ctrl["holds"]:
        return "no reading"
    if cap_binds:
        return "undecided: the cap binds"
    if n is None:
        return "above 200"
    return f"count ≤ {SIZES[0]}" if n <= SIZES[0] else f"count {n:.0f}"


def assess(c_by_k: dict[int, list[dict]], a2_by_k: dict[int, list[dict]]) -> dict:
    """The table ({arm: {mode: {k: cell}}}, the bases as they are), G′, the cap, the crossings per mode and the outcome."""
    t = {"c": {m: {k: AR.cell(c_by_k[k], m, ES_MAX_EPOCHS) for k in SIZES} for m in C_MODES},
         "a2": {R2: {k: AR.cell(a2_by_k[k], R2, ES_MAX_EPOCHS) for k in SIZES}}}
    base = {arm: {f: PC.mean_se([r["none"]["family_mean"][f] for r in recs[SIZES[0]]]) for f in FAMILIES}
            for arm, recs in (("c", c_by_k), ("a2", a2_by_k))}
    ctrl = control(c_by_k, a2_by_k)
    cap = {k: t["c"][R2][k]["at_cap"] > AR.CAP_SHARE for k in SIZES}
    cross = {m: crossings(t["c"][m]) for m in C_MODES}
    return {"table": t, "base": base, "control": ctrl, "cap_binds": cap, "crossings": cross,
            "outcome": outcome(ctrl, any(cap.values()), cross[R2]["CH-oop"]["k"])}


def read(out_dir: Path) -> dict:
    c_by_k = {k: AP.read_records(out_dir, [c_name(k, s) for s in PC.SEEDS]) for k in SIZES}
    a2_by_k = {k: AP.read_records(out_dir, [a2_name(k, s) for s in PC.SEEDS]) for k in SIZES}
    res = assess(c_by_k, a2_by_k)
    PC.write_text(out_dir / "anchor_count_read.json", json.dumps(res, indent=1, default=str))
    PC.write_text(out_dir / "anchor_count_read.md", "\n".join(report_lines(res)) + "\n")
    return res


def report_lines(res: dict) -> list[str]:
    def ms(x: tuple) -> str:
        return f"{x[0]:.2f} ± {x[1]:.2f}"

    def kk(x: float | None) -> str:
        return "> 200" if x is None else f"{x:.0f}"

    out = ["# Anchor count — read", "", f"**Outcome: {res['outcome']}.**", "",
           f"G′ (CH-stretch change from each base, arm (c) against arm (a2), {R2}): fails at {res['control']['fails']} of {len(SIZES)} k "
           f"(holds: {res['control']['holds']}); the cap binds at {[k for k, v in res['cap_binds'].items() if v] or 'no k'}.", "",
           "| k | change (c) | change (a2) | fails |", "|---|---|---|---|"]
    out += [f"| {k} | {ms(v['c'])} | {ms(v['a2'])} | {v['fails']} |" for k, v in res["control"]["per_k"].items()]
    out += ["", "Crossings of 3 cm⁻¹ (k on the mean curve; range from the mean ∓ se curves):", "",
            "| mode | " + " | ".join(FAMILIES) + " |", "|---|" + "---|" * len(FAMILIES)]
    out += [f"| {m} | " + " | ".join(f"{kk(c[f]['k'])} ({kk(c[f]['low'])}–{kk(c[f]['high'])})" for f in FAMILIES) + " |"
            for m, c in res["crossings"].items()]
    out += ["", "| arm | mode | k | " + " | ".join(FAMILIES) + " | training loss | best epoch (at cap) |",
            "|---|---|---|" + "---|" * (len(FAMILIES) + 2)]
    out += [f"| {arm} | base as is | – | " + " | ".join(ms(res["base"][arm][f]) for f in FAMILIES) + " | – | – |" for arm in res["base"]]
    for arm, by_m in res["table"].items():
        for m, by_k in by_m.items():
            for k, c in by_k.items():
                be = f"{ms(c['best_epoch'])} ({c['at_cap']:.0%})" if "best_epoch" in c else "–"
                out.append(f"| {arm} | {m} | {k} | " + " | ".join(ms(c["family"][f]) for f in FAMILIES)
                           + f" | {c['fit_loss'][0]:.4f} ± {c['fit_loss'][1]:.4f} | {be} |")
    return out


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")  # the report holds superscripts; a Windows console defaults to cp1252
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("action", choices=["plan", "read"])
    ap.add_argument("out_dir")
    a = ap.parse_args()
    out_dir = Path(a.out_dir).resolve()
    if a.action == "plan":
        print(plan(out_dir))
    else:
        print("\n".join(report_lines(read(out_dir))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
