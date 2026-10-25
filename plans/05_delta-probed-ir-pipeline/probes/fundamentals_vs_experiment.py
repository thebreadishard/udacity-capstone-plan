"""TASKS 111, reading 3 of the pre-registration `GoalGathering/notes/PreRegistration_2026-10-25_Scale_Factor_Residuals.md`: benzene and
naphthalene mode by mode against experiment — Mai et al. 2026's scaled frequencies, our carried coupled-cluster anchors (harmonic) and our
B3LYP/6-31G* with the PAHdb factors.

Mode identity as registered: irreducible representations from the mode vectors (benzene D6h through `dryrun_symmetry_prior.assign_irreps`,
naphthalene D2h from the characters under `e8_symmetry.point_group_ops`, Martin's axes fixed from the structure), computed and experimental
modes paired by frequency order within an irrep (a degenerate pair counts as one mode), pairs with a neighbour within CROSSING_CM in either
list flagged. Mai's modes, which carry no vectors, take the irrep and family of our B3LYP mode paired by sorted order; families come from
`learning_curve_layerA.molecule_features` on our analytic B3LYP Hessian. Mai's data are CC BY-NC-SA 4.0, so only statistics of them are
written, never their frequencies.

    python probes/fundamentals_vs_experiment.py [--mai …/IR_COMPAS.zip] [--out …/out/fundamentals_vs_experiment_2026-10-25]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
M05 = PLAN / "modules" / "05_support_predictor"
sys.path.insert(0, str(M05 / "m05"))
import anchor_registry as AR  # noqa: E402  (module 05's code is not a package)
from dryrun_symmetry_prior import assign_irreps  # noqa: E402
from e8_symmetry import point_group_ops  # noqa: E402
from learning_curve_layerA import FAMILIES, molecule_features, normal_modes  # noqa: E402
from scale_factor_baseline import PAHDB_FACTORS, pahdb_region  # noqa: E402

MOLECULES = M05 / "corpus" / "molecules"
MAI_ZIP = M05 / "data" / "external_mai2026" / "IR_COMPAS.zip"
BENZENE_REFS = PLAN / "probes" / "results_vpt2" / "benzene_benchmark_2026-09-22_harmonic_refs.json"
NAPHTHALENE_EXP = PLAN / "probes" / "data" / "naphthalene_fundamentals_martin1996.json"
OUT = M05 / "out" / "fundamentals_vs_experiment_2026-10-25"
CROSSING_CM = 15.0          # registered: a pair whose irrep neighbour lies this close in either list may be a crossing
DEGENERATE_CM = 0.5         # two modes of one degenerate irrep closer than this are one mode
MAI_PAIR_WARN_CM = 50.0     # registered: a Mai–B3LYP pair farther apart is counted and reported
GEOMETRY_TOL_BOHR = 1e-6
CHARACTER_TOL = 0.1          # a non-degenerate mode's character is ±1; farther off, the mode mixes species
D2H_SPECIES = {"Ag": 9, "Au": 4, "B1g": 3, "B1u": 8, "B2g": 4, "B2u": 8, "B3g": 8, "B3u": 4}   # naphthalene, Martin's labelling


@dataclass(frozen=True)
class Exp:
    """One experimental mode: fundamental, and for benzene the harmonic frequency derived from experiment and the Wilson number."""
    irrep: str
    nu: float
    omega: float | None = None
    wilson: int | None = None


@dataclass(frozen=True)
class Group:
    """One computed mode: the indices of its (possibly degenerate) normal modes, its frequency and irrep."""
    idx: tuple[int, ...]
    freq: float
    irrep: str


@dataclass(frozen=True)
class Molecule:
    name: str
    mol_id: str
    formula: str
    irreps: Callable[[np.ndarray, np.ndarray, list[str], np.ndarray], list[str]]
    experiment: Callable[[], list[Exp]]


# ------------------------------------------------------------------------------------------------- symmetry

def characters(V: np.ndarray, R: np.ndarray, perm: list[int]) -> np.ndarray:
    """χ of every mode under one operation: Σ_atoms v[perm[a]] · (R v[a]) for mass-weighted mode vectors (equivalent atoms share a mass)."""
    n = V.shape[0] // 3
    W = V.reshape(n, 3, -1)
    moved = np.einsum("xy,ayk->axk", R, W)
    return np.einsum("axk,axk->k", W[perm], moved)


def d2h_irreps(V: np.ndarray, freq: np.ndarray, symbols: list[str], coords: np.ndarray) -> list[str]:
    """Martin's D2h labels per mode: x normal to the plane; z the in-plane axis whose C2 keeps three out-of-plane gerade modes symmetric."""
    x = coords - coords.mean(0)
    normal = np.linalg.eigh(x.T @ x)[1][:, 0]
    ops = point_group_ops(symbols, coords)
    inversion = next((op for op in ops if np.allclose(op[0], -np.eye(3), atol=1e-3)), None)
    c2 = [op for op in ops if np.linalg.det(op[0]) > 0 and abs(np.trace(op[0]) + 1) < 1e-3]
    if inversion is None or len(c2) != 3:
        raise ValueError(f"not D2h: inversion {'found' if inversion else 'missing'}, {len(c2)} C2 axes")
    axis = {k: np.linalg.eigh((op[0] + op[0].T) / 2)[1][:, -1] for k, op in enumerate(c2)}
    k_normal = max(axis, key=lambda k: abs(axis[k] @ normal))
    chi = {k: characters(V, *c2[k]) for k in axis} | {"i": characters(V, *inversion)}
    worst = max(float(np.max(np.abs(np.abs(c) - 1))) for c in chi.values())
    if worst > CHARACTER_TOL:
        raise ValueError(f"a mode's D2h character is {worst:.2f} away from ±1: mixed species")
    sign = {k: np.sign(chi[k]) for k in axis}
    g = chi["i"] > 0
    in_plane = [k for k in axis if k != k_normal]
    oop_g = g & (sign[k_normal] < 0)
    k_z = next((k for k in in_plane if int(np.sum(oop_g & (sign[k] > 0))) == D2H_SPECIES["B1g"]), None)
    if k_z is None:
        raise ValueError("no in-plane C2 keeps exactly three out-of-plane gerade modes symmetric (Martin's B1g)")
    k_y = next(k for k in in_plane if k != k_z)
    names = {(1, 1, 1): "A", (1, -1, -1): "B1", (-1, 1, -1): "B2", (-1, -1, 1): "B3"}     # (C2z, C2y, C2x)
    labels = [names[(int(sign[k_z][i]), int(sign[k_y][i]), int(sign[k_normal][i]))] + ("g" if g[i] else "u") for i in range(len(freq))]
    counts = {s: labels.count(s) for s in D2H_SPECIES}
    if counts != D2H_SPECIES:
        raise ValueError(f"D2h species counts {counts} differ from Martin's {D2H_SPECIES}")
    return labels


def d6h_irreps(V: np.ndarray, freq: np.ndarray, symbols: list[str], coords: np.ndarray) -> list[str]:
    """Benzene's D6h labels per mode (lower case, as the benchmark file writes them); a mixed accidental pair is refused, not guessed."""
    labels, _, _, worst = assign_irreps(V, freq, coords, symbols)
    if worst > 0.05:
        raise ValueError(f"D6h operations map atoms only within {worst:.3f}")
    out = []
    for lab in labels:
        if len(lab) != 1 or next(iter(lab)).startswith("?"):
            raise ValueError(f"benzene mode without one clean D6h irrep: {sorted(lab)}")
        out.append(next(iter(lab)).lower())
    return out


# ------------------------------------------------------------------------------------------------- experiment and pairing

def benzene_experiment() -> list[Exp]:
    refs = json.loads(BENZENE_REFS.read_text(encoding="utf-8"))
    by_wilson = {r["wilson"]: r for r in refs.values()}
    return [Exp(r["sym"], float(r["exp_nu"]), float(r["miani_omega_exp"]), w) for w, r in sorted(by_wilson.items())]


def naphthalene_experiment() -> list[Exp]:
    data = json.loads(NAPHTHALENE_EXP.read_text(encoding="utf-8"))
    return [Exp(s, float(nu)) for s, values in data["fundamentals"].items() for nu in values]


def groups(freq: np.ndarray, labels: list[str]) -> list[Group]:
    """Normal modes merged into computed modes: consecutive modes of one degenerate species (D6h's e) closer than DEGENERATE_CM are one."""
    out: list[Group] = []
    for i, (f, lab) in enumerate(zip(freq, labels, strict=True)):
        last = out[-1] if out else None
        if last and last.irrep == lab and lab.startswith("e") and abs(f - last.freq) < DEGENERATE_CM:
            idx = (*last.idx, i)
            out[-1] = Group(idx, float(np.mean(freq[list(idx)])), lab)
        else:
            out.append(Group((i,), float(f), lab))
    return out


def crossing(values: list[float], k: int) -> bool:
    return any(abs(values[k] - values[j]) < CROSSING_CM for j in (k - 1, k + 1) if 0 <= j < len(values))


def pair_by_irrep(computed: list[Group], experiment: list[Exp]) -> list[tuple[Group, Exp, bool]]:
    """Within each irrep, computed and experimental modes in frequency order; the flag marks a possible crossing."""
    if sorted({g.irrep for g in computed}) != sorted({e.irrep for e in experiment}):
        raise ValueError(f"species differ: computed {sorted({g.irrep for g in computed})}, experimental {sorted({e.irrep for e in experiment})}")
    pairs = []
    for irrep in sorted({e.irrep for e in experiment}):
        exp = sorted((e for e in experiment if e.irrep == irrep), key=lambda e: e.nu)
        com = sorted((g for g in computed if g.irrep == irrep), key=lambda g: g.freq)
        if len(exp) != len(com):
            raise ValueError(f"irrep {irrep}: {len(com)} computed modes, {len(exp)} experimental")
        fc, fe = [g.freq for g in com], [e.nu for e in exp]
        pairs += [(g, e, crossing(fc, k) or crossing(fe, k)) for k, (g, e) in enumerate(zip(com, exp, strict=True))]
    return pairs


def subspace_overlap(Va: np.ndarray, ia: tuple[int, ...], Vb: np.ndarray, ib: tuple[int, ...]) -> float:
    """How much of mode group a lies in mode group b: ‖Va[:, ia]ᵀ Vb[:, ib]‖²_F / |ia| (1 = the same mode)."""
    return float(np.sum((Va[:, list(ia)].T @ Vb[:, list(ib)]) ** 2) / len(ia))


# ------------------------------------------------------------------------------------------------- Mai et al. 2026

MaiSpectrum = tuple[str, np.ndarray, np.ndarray]          # (entry name, scaled frequencies, their factors)


def mai_spectra(zip_path: Path, formulas: list[str]) -> dict[str, MaiSpectrum]:
    """The one neutral entry of each formula, in one pass over the archive. Refuses a formula with none or several entries."""
    hits: dict[str, list[tuple[str, str]]] = {f: [] for f in formulas}
    with zipfile.ZipFile(zip_path) as z:
        for info in z.infolist():
            if not info.filename.startswith("IR_COMPAS/charge_0/") or not info.filename.endswith(".xyz"):
                continue
            text = z.read(info).decode("utf-8")
            m = re.search(r"Formula=(\S+)", text.splitlines()[1])
            if m and m[1] in hits:
                hits[m[1]].append((info.filename, text))
    out = {}
    for formula, found in hits.items():
        if len(found) != 1:
            raise ValueError(f"{formula}: {len(found)} neutral entries in {zip_path.name}, expected one")
        name, text = found[0]
        values = np.array(text.split("scale_factor", 1)[1].split(), float).reshape(-1, 3)
        out[formula] = (Path(name).stem, values[:, 0], values[:, 2])
    return out


# ------------------------------------------------------------------------------------------------- one molecule

def stats(diffs: dict[str, list[float]]) -> dict[str, dict]:
    out = {}
    for fam in (*FAMILIES, "all"):
        d = np.array(diffs.get(fam, []), float) if fam != "all" else np.concatenate([np.array(v, float) for v in diffs.values()])
        out[fam] = {"n": len(d), "mean": float(d.mean()) if len(d) else None, "rms": float(np.sqrt(np.mean(d ** 2))) if len(d) else None}
    return out


def collect(rows: list[dict], key: str) -> dict[str, list[float]]:
    out: dict[str, list[float]] = {}
    for r in rows:
        if r.get(key) is not None:
            out.setdefault(r["family"], []).append(r[key])
    return out


def read_molecule(mol: Molecule, mai: MaiSpectrum) -> dict:
    d = MOLECULES / mol.mol_id
    g = json.loads((d / "geometry.json").read_text(encoding="utf-8"))
    symbols, coords, masses = g["symbols"], np.asarray(g["coords_bohr"]), np.asarray(g["masses_amu"])
    entry = AR.carried(mol.mol_id)
    if entry is None:
        raise ValueError(f"{mol.name}: no carried anchor")
    cc = np.load(PLAN / entry["path"])
    if np.abs(cc["coords_bohr"] - coords).max() > GEOMETRY_TOL_BOHR:
        raise ValueError(f"{mol.name}: the anchor's geometry is not the corpus geometry")
    h_b3 = np.load(d / "hessian_b3lyp_analytic.npz")["H_projected"]
    h_wb = np.load(d / "hessian_wb97x_analytic.npz")["H_projected"]
    family = molecule_features(d, lo=h_b3, hi=h_wb)["family"]
    _, f_b3, V_b3, _ = normal_modes(h_b3, masses)
    _, f_cc, V_cc, _ = normal_modes(cc["H_projected"], masses)
    exp = mol.experiment()
    p_b3 = pair_by_irrep(groups(f_b3, mol.irreps(V_b3, f_b3, symbols, coords)), exp)
    p_cc = pair_by_irrep(groups(f_cc, mol.irreps(V_cc, f_cc, symbols, coords)), exp)
    cc_of = {id(e): (gc, flag) for gc, e, flag in p_cc}
    scaled_b3 = np.array([PAHDB_FACTORS[r] for r in pahdb_region({"freq": f_b3})]) * f_b3
    entry_mai, s_mai, factor_mai = mai
    order = np.argsort(s_mai / factor_mai)
    s_mai, u_mai = s_mai[order], (s_mai / factor_mai)[order]
    if len(s_mai) != len(f_b3):
        raise ValueError(f"{mol.name}: Mai has {len(s_mai)} modes, our B3LYP {len(f_b3)}")
    rows = []
    for gb, e, flag_b3 in p_b3:
        gc, flag_cc = cc_of[id(e)]
        idx = list(gb.idx)
        rows.append({"irrep": e.irrep, "wilson": e.wilson, "family": family[idx[0]], "nu_exp": e.nu, "omega_exp": e.omega,
                     "omega_cc": gc.freq, "d_cc": gc.freq - e.nu, "d_cc_harmonic": None if e.omega is None else gc.freq - e.omega,
                     "omega_b3_pahdb": float(scaled_b3[idx].mean()), "d_b3_pahdb": float(scaled_b3[idx].mean()) - e.nu,
                     "_d_mai": float(s_mai[idx].mean()) - e.nu, "crossing": flag_b3 or flag_cc,
                     "overlap_cc_b3": subspace_overlap(V_cc, gc.idx, V_b3, gb.idx), "family_mixed": len({family[i] for i in idx}) > 1})
    comparisons = {"mai_scaled_minus_exp": "_d_mai", "b3lyp_pahdb_minus_exp": "d_b3_pahdb", "cc_harmonic_minus_exp": "d_cc",
                   "cc_harmonic_minus_exp_harmonic": "d_cc_harmonic"}
    out = {"anchor": {k: entry[k] for k in ("path", "level", "tier")}, "mai_entry": entry_mai,
           "mai_pairs_over_warn": int(np.sum(np.abs(u_mai - f_b3) > MAI_PAIR_WARN_CM)), "mai_max_pair_cm": float(np.abs(u_mai - f_b3).max()),
           "stats": {name: stats(collect(rows, key)) for name, key in comparisons.items() if collect(rows, key)},
           "min_overlap_cc_b3": min(r["overlap_cc_b3"] for r in rows), "crossings": sum(r["crossing"] for r in rows)}
    out["modes"] = [{k: v for k, v in r.items() if not k.startswith("_")} for r in rows]       # Mai's per-mode values stay out (licence)
    return out


MOLECULES_READ = (Molecule("benzene", "A_8448043181", "C6H6", d6h_irreps, benzene_experiment),
                  Molecule("naphthalene", "A_01f3186607", "C10H8", d2h_irreps, naphthalene_experiment))


# ------------------------------------------------------------------------------------------------- report

def stats_table(name: str, res: dict) -> list[str]:
    labels = {"mai_scaled_minus_exp": "Mai 2026 scaled − exp. fundamental", "b3lyp_pahdb_minus_exp": "our B3LYP/6-31G* × PAHdb factors − exp.",
              "cc_harmonic_minus_exp": "our CC harmonic − exp. fundamental", "cc_harmonic_minus_exp_harmonic": "our CC harmonic − exp. harmonic (Miani)"}
    lines = [f"### {name}: mean / rms (cm⁻¹) per family", "", "| comparison | " + " | ".join(f"{f} (n)" for f in (*FAMILIES, "all")) + " |",
             "|---|" + "---|" * (len(FAMILIES) + 1)]
    for key, label in labels.items():
        if key in res["stats"]:
            cells = [f"{v['mean']:+.1f} / {v['rms']:.1f} ({v['n']})" if v["n"] else "—" for v in res["stats"][key].values()]
            lines.append(f"| {label} | " + " | ".join(cells) + " |")
    return lines


def mode_table(res: dict) -> list[str]:
    lines = ["| irrep | family | exp. ν | CC ω | CC − ν | B3LYP×PAHdb − ν | exp. ω | CC − ω_exp | flag |", "|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(res["modes"], key=lambda r: r["nu_exp"]):
        harm = f"{r['omega_exp']:.0f} | {r['d_cc_harmonic']:+.1f}" if r["omega_exp"] is not None else "— | —"
        flag = ", ".join(x for x, on in (("crossing?", r["crossing"]), ("families mixed", r["family_mixed"])) if on)
        cc = f"{r['omega_cc']:.1f} | {r['d_cc']:+.1f}"
        lines.append(f"| {r['irrep']} | {r['family']} | {r['nu_exp']:.0f} | {cc} | {r['d_b3_pahdb']:+.1f} | {harm} | {flag} |")
    return lines


def molecule_section(name: str, r: dict) -> list[str]:
    note = (f"Anchor `{r['anchor']['path']}` ({r['anchor']['level']}); Mai entry {r['mai_entry']}, its modes paired with our B3LYP by sorted "
            f"order: {r['mai_pairs_over_warn']} pairs more than {MAI_PAIR_WARN_CM:.0f} cm⁻¹ apart (largest {r['mai_max_pair_cm']:.1f}); smallest "
            f"overlap of a CC mode with its B3LYP partner {r['min_overlap_cc_b3']:.2f}; {r['crossings']} pairs flagged as possible crossings.")
    return [*stats_table(name, r), "", note, "", f"#### {name}, per mode (Mai's values are not shown: licence)", "", *mode_table(r), ""]


def report(res: dict) -> list[str]:
    lines = ["# Benzene and naphthalene mode by mode against experiment (TASKS 111, reading 3)", "",
             "Pre-registration: `GoalGathering/notes/PreRegistration_2026-10-25_Scale_Factor_Residuals.md`. Experiment: benzene Goodman et al. 1991 "
             "and Miani et al. 2000 (`probes/data/benzene_benchmark_goodman1991_miani2000.json`); naphthalene Martin, El-Yazal & François 1996 via "
             "NIST CCCBDB (`probes/data/naphthalene_fundamentals_martin1996.json`). Mai et al. 2026 enter as statistics only (CC BY-NC-SA 4.0). "
             "Our CC anchors are Hessians at the B3LYP/6-31G* geometry of the corpus, the project's convention.", ""]
    for name, r in res.items():
        lines += molecule_section(name, r)
    return lines


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--mai", type=Path, default=MAI_ZIP)
    ap.add_argument("--out", type=Path, default=OUT, help="output prefix: <out>.json and <out>.md")
    a = ap.parse_args(argv)
    if not a.mai.exists():
        raise SystemExit(f"{a.mai}: Mai et al. 2026's archive is not here (it is kept outside git; TASKS 108)")
    mai = mai_spectra(a.mai, [m.formula for m in MOLECULES_READ])
    res = {m.name: read_molecule(m, mai[m.formula]) for m in MOLECULES_READ}
    lines = report(res)
    for path, text in ((a.out.with_suffix(".json"), json.dumps(res, indent=1)), (a.out.with_suffix(".md"), "\n".join(lines) + "\n")):
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(text, encoding="utf-8")
        tmp.replace(path)
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
