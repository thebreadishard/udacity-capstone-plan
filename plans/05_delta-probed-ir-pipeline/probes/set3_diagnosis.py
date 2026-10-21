"""Why did anchor set three read negative? A night of experiments on the data we have (the user, 21 Oct 2026 00:1x: 'Ligt het aan te weinig
data? Aan de hyperparameters? Aan de kop, het aantal hidden layers, het type netwerk? Aan het gebrek aan embedding? … tenminste twintig
ideeën'). Exploratory: no line is tested here; every number is reported beside the reference run (λ = 1, chain 34's carried model).

Every experiment is one `m05/rungC_cc_transfer.py` run over all eleven carried TZ anchors, each held out in turn, one fine-tune mode
(`--modes`), on a copy of the eleven anchors' corpus folders (`corpus`: loading the whole corpus costs ~2 GB beside the cation run; the copy
reproduces the full-corpus record of anchor set three's arm M within 3.2e-6 cm⁻¹ (6 threads here, 8 there;
run V00_arm_m_seed0). Seed 0 first; the read names what deserves seeds 1, 2.

    python probes/set3_diagnosis.py corpus <out_dir>        # the eleven anchors' folders and the manifest
    python probes/set3_diagnosis.py plan <out_dir> <name>   # probes/runs/set3_diag_<name>.json from the experiment list
    python probes/set3_diagnosis.py read <out_dir>          # <out_dir>/diagnosis.{json,md}
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
M05 = PLAN / "modules" / "05_support_predictor"
sys.path.insert(0, str(PLAN / "probes"))
import anchor_set3_read as S3  # noqa: E402

SET3 = M05 / "out" / "anchor_set3_2026-10-20"
FAMILIES = ("CH-oop", "other", "ring-ip", "CH-stretch")
MODEL = "out/E7_rungC_{chain}_seed{seed}.pt"
CHAIN34 = "chain34_kdfamily_750_2026-10-05_model_n750"
BASE = ["--threads", "6", "--epochs", "300", "--lr", "1e-3"]

# name -> (fine-tune mode, extra arguments, base model): the reference and one change each
EXPERIMENTS = {
    "E01_ref_lambda1": ("head_l2", ["--head-l2", "1", "--save-fold-predictions"], CHAIN34),
    "E02_lambda0": ("head", [], CHAIN34),
    "E03_lambda0.1": ("head_l2", ["--head-l2", "0.1"], CHAIN34),
    "E04_lambda0.3": ("head_l2", ["--head-l2", "0.3"], CHAIN34),
    "E05_lambda3": ("head_l2", ["--head-l2", "3"], CHAIN34),
    "E06_lambda10": ("head_l2", ["--head-l2", "10"], CHAIN34),
    "E07_no_finetune": ("none", [], CHAIN34),
    "E08_alpha_only": ("alpha", [], CHAIN34),
    "E09_lr3e-4": ("head_l2", ["--head-l2", "1", "--lr", "3e-4"], CHAIN34),
    "E10_lr3e-3": ("head_l2", ["--head-l2", "1", "--lr", "3e-3"], CHAIN34),
    "E11_epochs100": ("head_l2", ["--head-l2", "1", "--epochs", "100"], CHAIN34),
    "E12_epochs1000": ("head_l2", ["--head-l2", "1", "--epochs", "1000"], CHAIN34),
    "E13_aux0": ("head_l2", ["--head-l2", "1", "--aux-weight", "0"], CHAIN34),
    "E14_aux3": ("head_l2", ["--head-l2", "1", "--aux-weight", "3"], CHAIN34),
    "E15_lora4": ("lora", ["--lora-rank", "4"], CHAIN34),
    "E16_head_all": ("head_all", ["--head-all"], CHAIN34),
    "E17_insample_lambda1": ("head_l2", ["--head-l2", "1", "--in-sample"], CHAIN34),
    "E18_insample_head_all": ("head_all", ["--head-all", "--in-sample"], CHAIN34),
    "E19_base_analytic_labels": ("head_l2", ["--head-l2", "1", "--allow-any-model"], "chain35h2_analytic_model_n750"),
    "E20_base_more_data_n972": ("head_l2", ["--head-l2", "1", "--allow-any-model"], "chain41_size_model_n972"),
    "E21_base_hinge": ("head_l2", ["--head-l2", "1", "--allow-any-model"], "chain36_hinge_750_2026-10-07_model_n750"),
    "E22_base_coverage_n912": ("head_l2", ["--head-l2", "1", "--allow-any-model"], "chain37_coverage_2026-10-08_model_n912"),
    "E23_base_fivering_n972": ("head_l2", ["--head-l2", "1", "--allow-any-model"], "chain40_fivering30_model_n972"),
    # wave 2 (after E01-E07: the pull toward the proxy's last layer costs, the untuned network reads like the proxy itself)
    "W01_lastlayer0_lambda0": ("head", ["--init-scale", "0"], CHAIN34),
    "W02_lastlayer-0.6_lambda0": ("head", ["--init-scale", "-0.6"], CHAIN34),
    "W03_lastlayer-0.6_lambda1": ("head_l2", ["--init-scale", "-0.6", "--head-l2", "1"], CHAIN34),
    "W04_lastlayer0_lambda1": ("head_l2", ["--init-scale", "0", "--head-l2", "1"], CHAIN34),
    "W05_lastlayer-0.6_no_finetune": ("none", ["--init-scale", "-0.6"], CHAIN34),
    # wave 3 (after wave 2: the last layer's start does not matter at lambda 0, the L2 strength does)
    "W06_insample_lambda0": ("head", ["--in-sample"], CHAIN34),
    "W09_base_analytic_labels_lambda0": ("head", ["--allow-any-model"], "chain35h2_analytic_model_n750"),
    "W10_base_more_data_n972_lambda0": ("head", ["--allow-any-model"], "chain41_size_model_n972"),
    # wave 4 (after E16/E18/W06: the last layer cannot fit the out-of-plane correction even in-sample; the whole head halves the error)
    "W11_head_all_epochs100": ("head_all", ["--head-all", "--epochs", "100"], CHAIN34),
    "W12_head_all_lr3e-4": ("head_all", ["--head-all", "--lr", "3e-4"], CHAIN34),
    "W13_head_all_base_n972": ("head_all", ["--head-all", "--allow-any-model"], "chain41_size_model_n972"),
    "W14_head_all_base_analytic": ("head_all", ["--head-all", "--allow-any-model"], "chain35h2_analytic_model_n750"),
    "W15_head_all_originals_only": ("head_all", ["--head-all"], CHAIN34),
}
ORIGINALS_ONLY = {"W15_head_all_originals_only"}      # anchors: the original six alone (pool 5), against E16's eleven (pool 10)
VALIDATE = "V00_arm_m_seed0"
BENZENE_DZ = PLAN / "probes" / "results_m1" / "e8_benzene_ccpvdz_dip_2026-10-03" / "hessian_ccsd_t.npz"


def anchors() -> dict[str, str]:
    """The eleven carried TZ anchor files, as anchor set three's plan recorded them."""
    manifest = json.loads((SET3 / "manifest.json").read_text(encoding="utf-8"))
    return {i: manifest["files"][i] for i in (*S3.ORIGINALS, *S3.NEW)}


def dz_files() -> dict[str, Path]:
    """Each anchor's CC/DZ Hessian: the composite record's source anchor (benzene's full TZ anchor: its DZ run), skipping invalid ones."""
    out = {}
    for i, tz in anchors().items():
        if i == "A_8448043181":
            out[i] = BENZENE_DZ
            continue
        rec = json.loads(Path(tz).with_suffix(".json").read_text(encoding="utf-8"))
        src = Path(rec["anchor"])
        if "INVALID" not in src.name and "IMAGINARY" not in src.name:
            out[i] = src if src.is_absolute() else PLAN / src
    return out


def build_corpus(out_dir: Path) -> Path:
    """The eleven anchors' corpus folders and the manifest, copied (the run reads them; the whole corpus would cost ~2 GB of memory)."""
    src = M05 / "corpus"
    dst = out_dir / "corpus"
    if dst.exists():
        raise SystemExit(f"{dst} exists - refusing to overwrite")
    for i in anchors():
        shutil.copytree(src / "molecules" / i, dst / "molecules" / i)
    shutil.copyfile(src / "manifest.csv", dst / "manifest.csv")
    return dst / "molecules"


def run_argv(name: str, out_rel: str, mols: Path, seed: int = 0) -> list[str]:
    files = {i: f for i, f in anchors().items() if name not in ORIGINALS_ONLY or i in S3.ORIGINALS}
    if name == VALIDATE:      # anchor set three's arm M, seed 0, on the copied corpus: must equal its full-corpus record
        mode, extra, chain = "head_l2", ["--head-l2", "1", *[x for i in S3.NEW for x in ("--held", i)]], CHAIN34
    else:
        mode, extra, chain = EXPERIMENTS[name]
    argv = ["{python}", "m05/rungC_cc_transfer.py", str(mols), MODEL.format(chain=chain, seed=seed), f"{out_rel}/{name}_seed{seed}", *BASE,
            "--modes", mode, *extra]
    argv += [x for i in files for x in ("--anchor", f"{i}={files[i]}")]
    argv += [x for i in files if i in S3.APTS for x in ("--apt", f"{i}={S3.APTS[i].as_posix()}")]
    return argv


def plan(out_dir: Path, label: str, names: list[str], seeds: list[int]) -> Path:
    mols = out_dir / "corpus" / "molecules"
    if not mols.exists():
        raise SystemExit(f"{mols} missing - run `corpus` first")
    unknown = [n for n in names if n not in EXPERIMENTS and n != VALIDATE]
    if unknown:
        raise SystemExit(f"unknown experiments {unknown}")
    out_rel = Path(os.path.relpath(out_dir, M05)).as_posix()
    steps = [{"kind": "cmd", "label": f"{n}_seed{s}", "cwd": "modules/05_support_predictor", "log": f"modules/05_support_predictor/{out_rel}/{n}_seed{s}.log",
              "argv": run_argv(n, out_rel, mols, s)} for s in seeds for n in names]
    spec = {"_about": f"set-three diagnosis ({label}): probes/set3_diagnosis.py plan", "name": f"S3D{label}", "steps": steps,
            "outputs": [f"modules/05_support_predictor/{out_rel}/{n}_seed{s}.json" for s in seeds for n in names]}
    path = PLAN / "probes" / "runs" / f"set3_diag_{label}.json"
    path.write_text(json.dumps(spec, indent=1), encoding="utf-8", newline="\n")
    return path


def column(name: str) -> str:
    return f"network_{EXPERIMENTS[name][0]}"


def summary(rec: dict, col: str) -> dict:
    """Per family the mean ω rms over the folds (all, the original six, the new five) and the mean matched intensity error."""
    folds = rec["folds"]
    out = {}
    for fam in FAMILIES:
        for part, ids in (("all", list(folds)), ("orig", [i for i in folds if i in S3.ORIGINALS]), ("new", [i for i in folds if i in S3.NEW])):
            vals = [folds[i][col]["freq_rms_by_family"][fam] for i in ids if fam in folds[i][col]["freq_rms_by_family"]]
            out[f"{fam} {part}"] = float(np.mean(vals)) if vals else float("nan")
    inten = [folds[i][col]["intensity"][S3.MATCHED] for i in folds if "intensity" in folds[i][col]]
    zero = [folds[i]["zero_rule"]["intensity"][S3.MATCHED] for i in folds if "intensity" in folds[i]["zero_rule"]]
    out["intensity"] = float(np.mean(inten)) if inten else float("nan")
    orig = [folds[i][col]["intensity"][S3.MATCHED] for i in folds if i in S3.ORIGINALS and "intensity" in folds[i][col]]
    out["intensity orig"] = float(np.mean(orig)) if orig else float("nan")
    out["intensity zero rule"] = float(np.mean(zero)) if zero else float("nan")
    out["ring ratio"] = float(np.mean([folds[i][col]["coupling_ratio"] for i in folds]))
    return out


def seed_mean(per_seed: list[dict]) -> dict:
    """Mean and spread (sd, ddof 1) of each read-out over an experiment's seeds."""
    return {k: (float(np.mean([s[k] for s in per_seed])), float(np.std([s[k] for s in per_seed], ddof=1))) for k in per_seed[0]}


def read(out_dir: Path) -> dict:
    rows, spread = {}, {}
    for name in EXPERIMENTS:
        seeds = sorted(out_dir.glob(f"{name}_seed*.json"))
        for p in seeds:
            rec = json.loads(p.read_text(encoding="utf-8"))
            rows[p.stem] = summary(rec, column(name))
            if name == "E01_ref_lambda1" and "zero rule" not in rows:
                rows["zero rule"] = summary(rec, "zero_rule")
                rows["alpha scaling (no network)"] = summary(rec, "alpha_scaling")
        if len(seeds) > 1:
            spread[f"{name} ({len(seeds)} seeds)"] = seed_mean([rows[p.stem] for p in seeds])
    keys = ["CH-oop all", "CH-oop orig", "CH-oop new", "other all", "other orig", "ring-ip all", "CH-stretch all", "intensity", "intensity orig",
            "ring ratio"]
    md = ["# Set-three diagnosis — every experiment over the eleven anchors' folds", "",
          "Mean corrected-ω rms per family (cm⁻¹) over the held-out folds (orig = the original six, new = set three's five), matched intensity "
          "rel. rms over the anchors with a CC APT, ring-coupling ratio. Exploratory; one change against E01 each.", "",
          "| run | " + " | ".join(keys) + " |", "|---|" + "---|" * len(keys)]
    md += [f"| {r} | " + " | ".join(f"{v[k]:.3f}" if k.startswith("intensity") else f"{v[k]:.2f}" for k in keys) + " |" for r, v in rows.items()]
    if spread:
        md += ["", "Over seeds — mean ± sd:", "", "| experiment | " + " | ".join(keys) + " |", "|---|" + "---|" * len(keys)]
        md += [f"| {r} | " + " | ".join(f"{v[k][0]:.3f} ± {v[k][1]:.3f}" if k.startswith("intensity") else f"{v[k][0]:.2f} ± {v[k][1]:.2f}"
                                        for k in keys)
               + " |" for r, v in spread.items()]
    (out_dir / "diagnosis.json").write_text(json.dumps({"runs": rows, "over_seeds": spread}, indent=1), encoding="utf-8")
    (out_dir / "diagnosis.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("action", choices=("corpus", "plan", "read"))
    ap.add_argument("out_dir", type=Path)
    ap.add_argument("label", nargs="?", default="")
    ap.add_argument("--names", default="", help="comma-separated experiments (default all, without the validation)")
    ap.add_argument("--seeds", default="0")
    a = ap.parse_args()
    out = a.out_dir.resolve()
    if a.action == "corpus":
        print(build_corpus(out))
    elif a.action == "plan":
        names = [n for n in a.names.split(",") if n] or list(EXPERIMENTS)
        print(plan(out, a.label, names, [int(s) for s in a.seeds.split(",")]))
    else:
        read(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
