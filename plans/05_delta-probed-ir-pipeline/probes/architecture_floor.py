"""The rung-C architecture's floor (TASKS 65; GoalGathering/notes/PreRegistration_2026-10-15_Architecture_Floor.md).

Rung C's head (m05/rungC_equivariant.py) writes an off-diagonal block ΔH_ij only for atom pairs within 5 Å, each block symmetric, and every
diagonal block from the translational sum rule. The *oracle of that form* keeps every block of the true correction the head could write and
nothing else; its error in the mode basis is the floor under every network of this form — what perfect local learning would still miss.

    python probes/architecture_floor.py freeze <folder root> [...] --out <inputs.tsv>     ids and sha256 of every input, before any number
    python probes/architecture_floor.py read --inputs <inputs.tsv> --out <prefix>          checks the sha256, computes, applies the lines

A folder qualifies when it holds geometry.json and both analytic Hessians (hessian_{b3lyp,wb97x}_analytic.npz); a molecule found under two
roots is taken from the first root given. The read writes <prefix>.json and <prefix>.md.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "m05"))
sys.path.insert(0, str(PLAN / "probes"))
import floor_lines as FL  # noqa: E402  (pooling, line 1's bound, line 2's power law: shared with hybrid_form_floor.py)
import learning_curve_layerA as LA  # noqa: E402  (normal modes, mode families and units exactly as rung C's read-outs use them)

BOHR_PER_ANGSTROM = 1 / 0.529177210903
MODEL_CUTOFF_ANGSTROM = 5.0                  # rungC_equivariant.CUTOFF_BOHR in Å; tests/test_architecture_floor.py keeps the two equal
SWEEP_ANGSTROM = (4.0, 5.0, 6.0, 8.0, 10.0)
FAMILIES = FL.FAMILIES
LABEL_FILES = ("geometry.json", "hessian_b3lyp_analytic.npz", "hessian_wb97x_analytic.npz")
LINE_1_CM, LINE_2_CM = 1.0, 1.25             # the registered lines (cm⁻¹); the size bound and the forecast's rules are floor_lines'


@dataclass(frozen=True)
class Variant:
    name: str
    cut: bool              # zero the blocks beyond the cutoff
    symmetric: bool        # keep only each off-diagonal block's symmetric part


FORM = Variant("form", cut=True, symmetric=True)
VARIANTS = (FORM, Variant("cutoff only", cut=True, symmetric=False), Variant("symmetry only", cut=False, symmetric=True))


# ---------------------------------------------------------------- the oracle and the mode basis (pure)

def to_blocks(H: np.ndarray) -> np.ndarray:
    """(3N, 3N) → (N, N, 3, 3) with [i, j] the block of atoms i and j."""
    n = H.shape[0] // 3
    return H.reshape(n, 3, n, 3).transpose(0, 2, 1, 3)


def from_blocks(B: np.ndarray) -> np.ndarray:
    n = B.shape[0]
    return B.transpose(0, 2, 1, 3).reshape(3 * n, 3 * n)


def form_oracle(dH: np.ndarray, coords_bohr: np.ndarray, cutoff_angstrom: float, variant: Variant) -> np.ndarray:
    """The Cartesian correction the head's form keeps of `dH`.

    Off-diagonal blocks: zero beyond the cutoff (variant.cut), the symmetric part (variant.symmetric). Diagonal blocks: changed by the sum
    rule over what the form changed, ΔH_ii + Σ_j (ΔH_ij − ΔH_ij^form). With labels that obey the sum rule this is the head's −Σ_j ΔH_ij^form;
    written this way the labels' own small sum-rule residual stays out of the floor, and a variant that changes nothing returns `dH` exactly.
    """
    B = to_blocks(dH)
    n = B.shape[0]
    off = ~np.eye(n, dtype=bool)
    F = B.copy()
    if variant.symmetric:
        F[off] = 0.5 * (F[off] + F[off].transpose(0, 2, 1))
    if variant.cut:
        dist = np.linalg.norm(coords_bohr[:, None, :] - coords_bohr[None, :, :], axis=-1)
        F[(dist > cutoff_angstrom * BOHR_PER_ANGSTROM) & off] = 0.0
    change = np.where(off[:, :, None, None], B - F, 0.0)
    idx = np.arange(n)
    F[idx, idx] = B[idx, idx] + change.sum(axis=1)
    out = from_blocks(F)
    return 0.5 * (out + out.T)


def mode_correction(dH: np.ndarray, masses_amu: np.ndarray, w: np.ndarray, V: np.ndarray) -> np.ndarray:
    """K in cm⁻¹ from a Cartesian correction, exactly as embedding_skipgram_E5.coupling_matrix builds it (diagonal = first-order shift)."""
    m = np.repeat(np.asarray(masses_amu) * LA.AMU2AU, 3)
    km = V.T @ (dH / np.sqrt(np.outer(m, m))) @ V
    om = np.sqrt(np.abs(w))
    return km / (2 * np.sqrt(np.outer(om, om))) * LA.HARTREE2CM


# ---------------------------------------------------------------- one molecule (I/O)

def molecule_floor(folder: Path) -> dict:
    g = json.loads((folder / "geometry.json").read_text(encoding="utf-8"))
    coords, masses = np.asarray(g["coords_bohr"], dtype=float), np.asarray(g["masses_amu"], dtype=float)
    lo, hi = (np.load(folder / f"hessian_{lvl}_analytic.npz") for lvl in ("b3lyp", "wb97x"))
    w, _, V, _ = LA.normal_modes(lo["H_projected"], masses)
    families = list(LA.molecule_features(folder, lo["H_projected"], hi["H_projected"])["family"])
    dH = hi["H_raw"] - lo["H_raw"]
    K_true = mode_correction(dH, masses, w, V)
    K_projected = mode_correction(hi["H_projected"] - lo["H_projected"], masses, w, V)
    rec = {"id": folder.name, "n_atoms": len(masses), "raw_vs_projected_max_cm": float(np.max(np.abs(K_true - K_projected))),
           "variants": {v.name: FL.error_sums(K_true, mode_correction(form_oracle(dH, coords, MODEL_CUTOFF_ANGSTROM, v), masses, w, V), families)
                        for v in VARIANTS},
           "sweep": {str(c): FL.error_sums(K_true, mode_correction(form_oracle(dH, coords, c, FORM), masses, w, V), families)
                     for c in SWEEP_ANGSTROM}}
    return rec


# ---------------------------------------------------------------- the registered read (pure, on the records)

def pooled_rms(records: list[dict], key: str, family: str, where: str = "variants") -> float:
    """A family's pooled rms (or, family "ring_coupling", the ring-coupling ratio) of one variant or sweep point over records."""
    return FL.pooled([r[where][key] for r in records], family)


def line_1_bound(records: list[dict]) -> int:
    return FL.line_1_bound([r["n_atoms"] for r in records])


def read(records: list[dict]) -> dict:
    bound = line_1_bound(records)
    upper = [r for r in records if r["n_atoms"] >= bound]
    rng = np.random.default_rng(FL.BOOTSTRAP_SEED)
    fam_out = {}
    for F in FAMILIES:
        line1 = pooled_rms(upper, FORM.name, F)
        points = [(r["n_atoms"], v) for r in records if (v := FL.per_molecule(r["variants"][FORM.name], F)) is not None]
        at60, interval, n_fit = FL.forecast(points, rng)
        fam_out[F] = {
            "line_1_floor_cm": line1, "line_1_met": bool(line1 >= LINE_1_CM),
            "line_2_floor_at_60_cm": at60, "line_2_interval_cm": interval,
            "line_2_met": bool(at60 >= LINE_2_CM), "n_fit": n_fit,
            "attribution_upper_cm": {v.name: pooled_rms(upper, v.name, F) for v in VARIANTS},
            "sweep_upper_cm": {c: pooled_rms(upper, c, F, "sweep") for c in map(str, SWEEP_ANGSTROM)},
        }
    met = [F for F, x in fam_out.items() if x["line_1_met"] or x["line_2_met"]]
    verdict = (f"the form costs in {', '.join(met)}: a model change is registered before more data is bought for size" if met
               else "neither line met: the form is not the limit at these sizes; the size levers stay with data")
    return {"verdict": verdict, "families": fam_out, "line_1_bound_atoms": bound, "n_upper": len(upper), "n_molecules": len(records),
            "ring_coupling_floor_upper": {v.name: pooled_rms(upper, v.name, "ring_coupling") for v in VARIANTS},
            "raw_vs_projected_max_cm": max(r["raw_vs_projected_max_cm"] for r in records)}


def _met(value: float, met: bool) -> str:
    return f"{value:.3f}{' MET' if met else ''}"


def _family_row(family: str, x: dict) -> str:
    interval = x["line_2_interval_cm"]
    span = f"{interval[0]:.3f}–{interval[1]:.3f}" if interval else "no fit (fewer than 3 molecules)"
    att = x["attribution_upper_cm"]
    return (f"| {family} | {_met(x['line_1_floor_cm'], x['line_1_met'])} | {_met(x['line_2_floor_at_60_cm'], x['line_2_met'])} | {span} | "
            f"{att['cutoff only']:.3f} | {att['symmetry only']:.3f} |")


def report(res: dict) -> list[str]:
    lines = ["# The rung-C architecture's floor (TASKS 65, registered read)", "", f"**{res['verdict']}**", "",
             f"{res['n_molecules']} molecules; line 1 on the {res['n_upper']} of ≥ {res['line_1_bound_atoms']} atoms.", "",
             "| family | line 1: form floor (≥ 1.0) | line 2: at 60 atoms (≥ 1.25) | 95 % interval | cutoff only | symmetry only |",
             "|---|---|---|---|---|---|"]
    lines += [_family_row(F, x) for F, x in res["families"].items()]
    lines += ["", "Form floor on the upper set by cutoff (beside, no line), cm⁻¹:", "",
              "| family | " + " | ".join(f"{c} Å" for c in SWEEP_ANGSTROM) + " |", "|---|" + "---|" * len(SWEEP_ANGSTROM)]
    lines += [f"| {F} | " + " | ".join(f"{x['sweep_upper_cm'][str(c)]:.3f}" for c in SWEEP_ANGSTROM) + " |" for F, x in res["families"].items()]
    rc = res["ring_coupling_floor_upper"]
    lines += ["", f"Ring-coupling floor (error rms / true rms, upper set): form {rc['form']:.3f}, cutoff only {rc['cutoff only']:.3f}, "
                  f"symmetry only {rc['symmetry only']:.3f}. Raw against projected Hessians, largest K difference: "
                  f"{res['raw_vs_projected_max_cm']:.2e} cm⁻¹."]
    return lines


# ---------------------------------------------------------------- freeze and read (CLI)

def qualifying_folders(roots: list[Path]) -> dict[str, Path]:
    found: dict[str, Path] = {}
    for root in roots:
        for d in sorted(p for p in root.iterdir() if p.is_dir()):
            if d.name not in found and all((d / f).is_file() for f in LABEL_FILES):
                found[d.name] = d
    return found


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def freeze(roots: list[Path], out: Path) -> int:
    folders = qualifying_folders(roots)
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("# architecture floor inputs (TASKS 65): id, folder, then the sha256 of " + ", ".join(LABEL_FILES) + "\n")
        for i, d in folders.items():
            rel = d.relative_to(PLAN).as_posix() if d.is_relative_to(PLAN) else d.as_posix()
            fh.write("\t".join([i, rel, *(sha256(d / f) for f in LABEL_FILES)]) + "\n")
    return len(folders)


def frozen_folders(inputs: Path) -> list[Path]:
    """The folders of a frozen input list, each file checked against its sha256; any difference stops the read."""
    out = []
    for row in csv.reader((ln for ln in inputs.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")), delimiter="\t"):
        d = PLAN / row[1]
        for f, want in zip(LABEL_FILES, row[2:], strict=True):
            if sha256(d / f) != want:
                raise SystemExit(f"{row[0]}: {f} differs from the frozen sha256 — not read")
        out.append(d)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("freeze")
    f.add_argument("roots", nargs="+", type=Path)
    f.add_argument("--out", type=Path, required=True)
    r = sub.add_parser("read")
    r.add_argument("--inputs", type=Path, required=True)
    r.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.cmd == "freeze":
        print(f"{freeze(a.roots, a.out)} molecules frozen in {a.out}")
        return 0
    records = [molecule_floor(d) for d in frozen_folders(a.inputs)]
    res = read(records)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    Path(f"{a.out}.json").write_text(json.dumps({**res, "records": records}, indent=1, ensure_ascii=False), encoding="utf-8")
    lines = report(res)
    Path(f"{a.out}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
