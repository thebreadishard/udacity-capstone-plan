"""TASKS 112, reading 2 of the pre-registration `GoalGathering/notes/PreRegistration_2026-10-25_Scale_Factor_Residuals.md`: Mai et al. 2026's
teacher on our molecules — their unscaled frequencies (B3LYP/4-31G through a learned potential) against our analytic B3LYP/6-31G*, and their
scaled ones against our B3LYP/6-31G* with the same PAHdb factors, per mode family.

Our side: the neutral corpus molecules whose skeleton is carbon only and whose folder holds both analytic Hessians. Their side: the neutral entry
with the same formula and the same skeleton (RDKit bonds from each geometry, `fundamentals_vs_experiment.skeleton`); duplicates of one molecule
count once when their scaled frequencies agree within MAI_DUPLICATE_CM, and a disagreeing duplicate is left out by name (decided before the
read). Modes are paired by sorted order and take our mode's family. Their data are CC BY-NC-SA 4.0: only statistics are written.

    python probes/mai_teacher_overlap.py [--mai …/IR_COMPAS.zip] [--out …/out/mai_teacher_overlap_2026-10-25]
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import zipfile
from pathlib import Path

import numpy as np
from rdkit import Chem

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "m05"))
from anchor_plan import CATION_LAYERS  # noqa: E402  (probes/ is this script's own folder)
from fundamentals_vs_experiment import M05, MAI_DUPLICATE_CM, MAI_PAIR_WARN_CM, MAI_ZIP, MOLECULES, skeleton, stats, xyz_block  # noqa: E402
from learning_curve_layerA import molecule_features, normal_modes  # noqa: E402
from scale_factor_baseline import PAHDB_FACTORS, pahdb_region  # noqa: E402

MANIFEST = M05 / "corpus" / "manifest.csv"
OUT = M05 / "out" / "mai_teacher_overlap_2026-10-25"


def carbon_skeleton(smiles: str) -> bool:
    mol = Chem.MolFromSmiles(smiles) if smiles else None
    return mol is not None and all(a.GetSymbol() == "C" for a in mol.GetAtoms())


def our_molecules(manifest: Path, molecules: Path) -> dict[str, dict]:
    """id → {formula, skeleton} of the neutral carbon-skeleton molecules with both analytic Hessians."""
    out = {}
    with manifest.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            d = molecules / row["id"]
            if (row["layer"] in CATION_LAYERS or not carbon_skeleton(row["smiles"])
                    or not all((d / f"hessian_{t}_analytic.npz").exists() for t in ("b3lyp", "wb97x"))):
                continue
            g = json.loads((d / "geometry.json").read_text(encoding="utf-8"))
            n_c, n_h = g["symbols"].count("C"), g["symbols"].count("H")
            out[row["id"]] = {"formula": f"C{n_c}H{n_h}", "skeleton": skeleton(xyz_block(g["symbols"], np.asarray(g["coords_bohr"])))}
    return out


def match(zip_path: Path, ours: dict[str, dict]) -> tuple[dict[str, np.ndarray], dict[str, str]]:
    """(our id → their scaled/factor table, our id → why left out) in one pass over the neutral entries."""
    wanted = {(v["formula"], v["skeleton"]): i for i, v in ours.items()}
    formulas = {f for f, _ in wanted}
    found: dict[str, list[np.ndarray]] = {}
    with zipfile.ZipFile(zip_path) as z:
        for info in z.infolist():
            if not info.filename.startswith("IR_COMPAS/charge_0/") or not info.filename.endswith(".xyz"):
                continue
            text = z.read(info).decode("utf-8")
            lines = text.splitlines()
            m = re.search(r"Formula=(\S+)", lines[1])
            if not m or m[1] not in formulas:
                continue
            key = (m[1], skeleton("\n".join(lines[: int(lines[0]) + 2])))
            if key in wanted:
                found.setdefault(wanted[key], []).append(np.array(text.split("scale_factor", 1)[1].split(), float).reshape(-1, 3))
    tables, left_out = {}, {}
    for i, entries in found.items():
        if any(e.shape != entries[0].shape or np.abs(e[:, 0] - entries[0][:, 0]).max() > MAI_DUPLICATE_CM for e in entries[1:]):
            left_out[i] = f"{len(entries)} entries disagree by more than {MAI_DUPLICATE_CM} cm⁻¹"
        else:
            tables[i] = entries[0]
    return tables, left_out


def differences(mol_dir: Path, table: np.ndarray) -> tuple[dict[str, list[float]], dict[str, list[float]], int]:
    """Per family, their unscaled − our B3LYP and their scaled − our B3LYP × PAHdb, paired by sorted order; and the pairs beyond the warning."""
    g = json.loads((mol_dir / "geometry.json").read_text(encoding="utf-8"))
    h_b3 = np.load(mol_dir / "hessian_b3lyp_analytic.npz")["H_projected"]
    h_wb = np.load(mol_dir / "hessian_wb97x_analytic.npz")["H_projected"]
    family = molecule_features(mol_dir, lo=h_b3, hi=h_wb)["family"]
    _, f_b3, _, _ = normal_modes(h_b3, np.asarray(g["masses_amu"]))
    if len(table) != len(f_b3):
        raise ValueError(f"{mol_dir.name}: {len(table)} modes in their entry, {len(f_b3)} in ours")
    unscaled = table[:, 0] / table[:, 2]
    order = np.argsort(unscaled)
    scaled, unscaled = table[order, 0], unscaled[order]
    ours_scaled = np.array([PAHDB_FACTORS[r] for r in pahdb_region({"freq": f_b3})]) * f_b3
    teacher: dict[str, list[float]] = {}
    product: dict[str, list[float]] = {}
    for fam, u, s, w, ws in zip(family, unscaled, scaled, f_b3, ours_scaled, strict=True):
        teacher.setdefault(fam, []).append(float(u - w))
        product.setdefault(fam, []).append(float(s - ws))
    return teacher, product, int(np.sum(np.abs(unscaled - f_b3) > MAI_PAIR_WARN_CM))


def read(zip_path: Path, manifest: Path, molecules: Path) -> dict:
    ours = our_molecules(manifest, molecules)
    tables, left_out = match(zip_path, ours)
    teacher: dict[str, list[float]] = {}
    product: dict[str, list[float]] = {}
    beyond = 0
    for i in sorted(tables):
        t, p, b = differences(molecules / i, tables[i])
        for fam, v in t.items():
            teacher.setdefault(fam, []).extend(v)
        for fam, v in p.items():
            product.setdefault(fam, []).extend(v)
        beyond += b
    return {"candidates": len(ours), "matched": sorted(tables), "left_out": left_out, "pairs_beyond_warn": beyond,
            "unscaled_minus_our_b3lyp": stats(teacher), "scaled_minus_our_b3lyp_pahdb": stats(product)}


def report(res: dict) -> list[str]:
    fams = list(res["unscaled_minus_our_b3lyp"])
    lines = ["# Mai et al. 2026's teacher on our molecules (TASKS 112, reading 2)", "",
             "Pre-registration: `GoalGathering/notes/PreRegistration_2026-10-25_Scale_Factor_Residuals.md`. Statistics only (their data are CC BY-NC-SA 4.0). "
             f"{res['candidates']} of our neutral carbon-skeleton molecules with both analytic labels; {len(res['matched'])} found in their neutral set "
             f"by formula and skeleton; left out: {res['left_out'] or 'none'}. Modes paired by sorted order: {res['pairs_beyond_warn']} pairs more than "
             f"{MAI_PAIR_WARN_CM:.0f} cm⁻¹ apart.", "", "| mean / rms (cm⁻¹), modes | " + " | ".join(fams) + " |", "|---|" + "---|" * len(fams)]
    for key, label in (("unscaled_minus_our_b3lyp", "their unscaled − our B3LYP/6-31G*"),
                       ("scaled_minus_our_b3lyp_pahdb", "their scaled − our B3LYP/6-31G* × the same factors")):
        cells = [f"{v['mean']:+.1f} / {v['rms']:.1f} ({v['n']})" if v["n"] else "—" for v in res[key].values()]
        lines.append(f"| {label} | " + " | ".join(cells) + " |")
    lines += ["", "Matched: " + ", ".join(res["matched"]) + "."]
    return lines


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--mai", type=Path, default=MAI_ZIP)
    ap.add_argument("--out", type=Path, default=OUT, help="output prefix: <out>.json and <out>.md")
    a = ap.parse_args(argv)
    if not a.mai.exists():
        raise SystemExit(f"{a.mai}: Mai et al. 2026's archive is not here (it is kept outside git; TASKS 108)")
    res = read(a.mai, MANIFEST, MOLECULES)
    lines = report(res)
    for path, text in ((a.out.with_suffix(".json"), json.dumps(res, indent=1)), (a.out.with_suffix(".md"), "\n".join(lines) + "\n")):
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(text, encoding="utf-8")
        tmp.replace(path)
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
