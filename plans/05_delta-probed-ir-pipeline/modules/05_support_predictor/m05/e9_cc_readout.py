"""E9 at coupled-cluster level — reads R2 and R3 of anchor set two (pre-registration 2026-09-29, Anchor_Set_Two).

The E9 construction (`e9_core_transfer.py`, pre-registered 24 September 2026) unchanged, with the correction ΔH = H_high − H_B3LYP taken from
a CCSD(T) Hessian (E8 npz with `H_projected` at the corpus geometry) for both the core and the substituted molecule. Without `--core-hi` /
`--sub-hi` the ωB97X proxy is used, and the numbers are then E9's for that one pair (the tests hold the two code paths together).

- R2 (`--mode substituent`, default): benzene's block carried onto the parent core of the substituted molecule, the columns of the atoms within
  r bonds of the substituent from the molecule's own ΔH; lines as E9: corrected ω RMS ≤ 3.3 cm⁻¹ and ring coupling ratio ≤ 0.5 at r = 2.
- R3 (`--mode element`): the core mapped atom by atom onto a molecule with a heteroatom in place of a carbon (benzene → pyridine), no columns
  probed (`transfer_only` at r = 0 is the read); the corrected-frequency RMS is split by the modes' heteroatom participation. No pass line.

Usage: python e9_cc_readout.py <molecules dir> <core id> <sub id> <out prefix> [--core-hi npz] [--sub-hi npz] [--radii 0,1,2,3,4]
                               [--mode substituent|element] [--hetero N] [--label text]
"""
import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import e6_learning_curve as E6  # noqa: E402
import e7_t2_sqm as T2  # noqa: E402
from e9_core_transfer import RING, atom_map, kabsch, pooled, rebuild, with_probe  # noqa: E402
from learning_curve_layerA import molecule_features, normal_modes  # noqa: E402

VARIANTS = ("transfer_probe", "probe_only", "transfer_only")


def load_high(mol_dir: Path, hi_path: Path | None, coords: np.ndarray, tag: str = "") -> tuple[np.ndarray, str]:
    """The high-level projected Hessian: the E8 npz when given (its geometry must be the corpus one), else the ωB97X proxy (analytic when `tag`)."""
    if hi_path is None:
        return np.load(mol_dir / f"hessian_wb97x{tag}.npz")["H_projected"], "wB97X (proxy" + (", pyscf analytic)" if tag else ", psi4 FD)")
    z = np.load(hi_path)
    if "coords_bohr" in z.files and not np.allclose(z["coords_bohr"], coords, atol=1e-6):
        raise ValueError(f"{hi_path}: geometry differs from {mol_dir / 'geometry.json'}")
    return z["H_projected"], f"{hi_path.name} ({Path(hi_path).parent.name})"


def load_molecule(mdir: Path, mol_id: str, hi_path: Path | None = None, use_analytic: bool = False) -> dict:
    """One corpus molecule as E9 sees it (family labels, low-level modes) with ΔH_true and the truth K from the chosen high level. `use_analytic`
    takes the pyscf analytic pair (hessian_*_analytic.npz, grid 99/590) as the low level and, without an E8 npz, as the proxy high level —
    the corpus psi4 FD Hessians carry grid noise (benzene: ωB97X up to 132 cm⁻¹ off, 23 Sep 2026), so the CC read must not use them."""
    d = mdir / mol_id
    tag = "_analytic" if use_analytic else ""
    if use_analytic and not (d / "hessian_b3lyp_analytic.npz").exists():
        raise FileNotFoundError(f"{d.name}: no hessian_b3lyp_analytic.npz (run corpus/analytic_hessians.py on the folder first)")
    g = json.load(open(d / "geometry.json", encoding="utf-8"))
    masses = np.asarray(g["masses_amu"], float); coords = np.asarray(g["coords_bohr"], float)
    lo = np.load(d / f"hessian_b3lyp{tag}.npz")["H_projected"]
    hi, source = load_high(d, hi_path, coords, tag)
    m = molecule_features(d, lo=lo, hi=hi)
    w, _freq, V, _ = normal_modes(lo, masses)
    m.update(masses=masses, coords=coords, symbols=[s.upper() for s in g["symbols"]], V=V, w=w, H_low=lo, dH_true=hi - lo, high_source=source,
             low_source="B3LYP " + ("pyscf analytic (grid 99/590)" if use_analytic else "psi4 FD (grid 75/302)"))
    m["K"] = T2.K_from_dH(m, m["dH_true"])
    m["participation"] = (V.reshape(len(masses), 3, -1) ** 2).sum(1)          # (N atoms, M modes), mass-weighted squared amplitude
    return m


def element_map(core_smiles: str, sub_smiles: str, xC: np.ndarray, xS: np.ndarray, symC: list, symS: list):
    """Core atom -> S atom when a heavy atom changed element (benzene -> pyridine): the core's heavy-atom graph matched with every heavy atom a
    wildcard, the match with the smallest aligned RMSD kept; hydrogens as in E9's atom_map (nearest free H on the mapped heavy atom, the H that
    the heteroatom lost stays unmapped). Returns (mapping, rotation, [], distance matrix of S) or None."""
    from rdkit import Chem
    mC, mS = Chem.AddHs(Chem.MolFromSmiles(core_smiles)), Chem.AddHs(Chem.MolFromSmiles(sub_smiles))
    if [a.GetSymbol().upper() for a in mC.GetAtoms()] != [s.upper() for s in symC]: return None
    if [a.GetSymbol().upper() for a in mS.GetAtoms()] != [s.upper() for s in symS]: return None
    heavyC, heavyS = Chem.RemoveHs(mC), Chem.RemoveHs(mS)
    q = Chem.RWMol(heavyC)
    for a in q.GetAtoms(): a.SetAtomicNum(0)
    params = Chem.AdjustQueryParameters.NoAdjustments(); params.makeDummiesQueries = True; params.aromatizeIfPossible = False
    q = Chem.AdjustQueryProperties(q.GetMol(), params)
    matches = heavyS.GetSubstructMatches(q, uniquify=False, useChirality=False)
    matches = [mt for mt in matches if len(mt) == heavyC.GetNumAtoms()]
    if not matches: return None
    best = None
    for mt in matches:
        R, t = kabsch(xC[list(range(len(mt)))], xS[list(mt)])
        err = float(np.sqrt(np.mean(np.sum((xC[:len(mt)] @ R.T + t - xS[list(mt)]) ** 2, 1))))
        if best is None or err < best[0]: best = (err, mt, R, t)
    _err, mt, R, t = best
    mp = {k: mt[k] for k in range(len(mt))}
    xC_al = xC @ R.T + t; used = set(mp.values())
    for a in mC.GetAtoms():
        if a.GetSymbol() != "H": continue
        target = mp[a.GetNeighbors()[0].GetIdx()]
        cands = [n.GetIdx() for n in mS.GetAtomWithIdx(target).GetNeighbors() if n.GetSymbol() == "H" and n.GetIdx() not in used]
        if not cands: continue
        j = min(cands, key=lambda c: np.linalg.norm(xS[c] - xC_al[a.GetIdx()])); mp[a.GetIdx()] = j; used.add(j)
    return mp, R, [], Chem.GetDistanceMatrix(mS)


def near_atoms(subst: list, D: np.ndarray, r: int, n_atoms: int) -> list:
    return sorted(set(subst) | {a for a in range(n_atoms) if min(D[a, s] for s in subst) <= r}) if subst else []


def read_pair(core: dict, sub: dict, am, radii) -> dict:
    """E9's variants for one (core, substituted) pair at every radius; exact and zero rule beside them. Pooled read-outs are E6/E7's."""
    mp, R, subst, D = am
    mols = {core["id"]: core, sub["id"]: sub}; ids = [sub["id"]]; tr = [core["id"]]
    dHS, dHC = sub["dH_true"], core["dH_true"]; N = len(sub["symbols"])
    out = {"exact": pooled({sub["id"]: T2.K_from_dH(sub, dHS)}, mols, ids, tr), "zero": pooled({sub["id"]: np.zeros_like(sub["K"])}, mols, ids, tr)}
    out["mapped_atoms"] = len(mp); out["unmapped_core_atoms"] = [int(a) for a in range(len(core["symbols"])) if a not in mp]
    for r in radii:
        near = near_atoms(subst, D, r, N)
        far_block = rebuild(dHS, dHC, mp, R, set(near), True)
        recs = {"transfer_probe": with_probe(far_block, dHS, near), "probe_only": with_probe(np.zeros_like(dHS), dHS, near), "transfer_only": far_block}
        for k, H in recs.items():
            o = pooled({sub["id"]: T2.K_from_dH(sub, H)}, mols, ids, tr)
            o["dH_residual_ratio"] = float(np.sqrt(np.mean((H - dHS) ** 2) / np.mean(dHS ** 2)))
            o["column_fraction"] = len(near) / N; o["n_near"] = len(near)
            o["per_mode_error_cm"] = (T2.corrected_frequencies(sub, T2.K_from_dH(sub, H))[0] - T2.corrected_frequencies(sub, sub["K"])[0]).tolist()
            out[f"{k}_r{r}"] = o
    return out


def hetero_split(sub: dict, per_mode_error: list, hetero: str, share: float = 0.3) -> dict:
    """RMS of the per-mode corrected-frequency error for modes with and without dominant heteroatom participation (R3's split)."""
    sym = np.array(sub["symbols"]); part = sub["participation"][sym == hetero.upper()].sum(0) if (sym == hetero.upper()).any() else np.zeros(sub["V"].shape[1])
    e = np.asarray(per_mode_error); hi = part > share
    return {"hetero": hetero, "share_threshold": share, "n_modes_hetero": int(hi.sum()), "n_modes_other": int((~hi).sum()),
            "rms_hetero_modes": E6.rms(e[hi]) if hi.any() else float("nan"), "rms_other_modes": E6.rms(e[~hi]) if (~hi).any() else float("nan"),
            "rms_all": E6.rms(e)}


def markdown(res: dict, radii) -> str:
    md = [f"# E9 at CC level — {res['label']} ({res['date']}): core {res['core']['name']} → {res['sub']['name']}", "",
          f"Low level: {res['low_level']}. High level: core {res['core']['high_source']}; molecule {res['sub']['high_source']}. Mode {res['mode']}; {res['mapped_atoms']} of "
          f"{res['core']['n_atoms']} core atoms mapped onto the {res['sub']['n_atoms']}-atom molecule.", ""]
    if res["mode"] == "substituent":
        v = res["variants"]["transfer_probe_r2"]
        md += [f"**R2 at r = 2, transfer + probe: {res['verdict_r2']}** — corrected ω RMS {v['corrected_freq_rms']:.2f} cm⁻¹ (line ≤ 3.3), ring coupling "
               f"ratio {v['coupling_ratio']:.2f} (line ≤ 0.5); zero rule {v['corrected_freq_rms_zero_rule']:.2f} cm⁻¹.", ""]
    md += ["| r | variant | columns probed | ΔH residual ratio | ring coupling ratio | ring diag RMS | corrected ω RMS (zero rule) | overlap median |",
           "|---|---|---|---|---|---|---|---|"]
    for r in radii:
        for k in VARIANTS:
            x = res["variants"][f"{k}_r{r}"]
            md.append(f"| {r} | {k} | {x['column_fraction']:.2f} | {x['dH_residual_ratio']:.3f} | **{x['coupling_ratio']:.2f}** | {x['diag_rms'][RING]:.2f} | "
                      f"**{x['corrected_freq_rms']:.2f}** ({x['corrected_freq_rms_zero_rule']:.2f}) | {x['duschinsky_overlap_median']:.3f} |")
    x = res["variants"]["exact"]
    md.append(f"| — | exact | 1.00 | 0 | {x['coupling_ratio']:.2f} | {x['diag_rms'][RING]:.2f} | {x['corrected_freq_rms']:.2f} | {x['duschinsky_overlap_median']:.3f} |")
    if res.get("hetero_split"):
        h = res["hetero_split"]
        md += ["", f"## R3 split, transfer only at r = 0: modes with {h['hetero']} participation > {h['share_threshold']:.1f}", "",
               "| modes | n | corrected ω RMS |", "|---|---|---|",
               f"| {h['hetero']}-participating | {h['n_modes_hetero']} | {h['rms_hetero_modes']:.2f} |", f"| other | {h['n_modes_other']} | {h['rms_other_modes']:.2f} |",
               f"| all | {h['n_modes_hetero'] + h['n_modes_other']} | {h['rms_all']:.2f} |"]
    return "\n".join(md) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("Usage:")[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("molecules"); ap.add_argument("core_id"); ap.add_argument("sub_id"); ap.add_argument("out_prefix")
    ap.add_argument("--core-hi", type=Path, default=None, help="E8 npz of the core's CCSD(T) Hessian (default: the ωB97X proxy)")
    ap.add_argument("--sub-hi", type=Path, default=None, help="E8 npz of the molecule's CCSD(T) Hessian (default: the ωB97X proxy)")
    ap.add_argument("--radii", default="0,1,2,3,4"); ap.add_argument("--mode", choices=["substituent", "element"], default="substituent")
    ap.add_argument("--hetero", default="N", help="element whose modes R3 splits off (mode element)")
    ap.add_argument("--label", default="", help="free text for the report header, e.g. 'R2 benzonitrile'")
    ap.add_argument("--use-analytic", action="store_true", help="low level (and proxy high level) from the pyscf analytic pair instead of the psi4 FD files")
    a = ap.parse_args(argv); t0 = time.time()
    mdir = Path(a.molecules); radii = [int(x) for x in a.radii.split(",")]
    import csv
    man = {r["id"]: r for r in csv.DictReader(open(mdir.parent / "manifest.csv", newline="", encoding="utf-8"))}
    core, sub = load_molecule(mdir, a.core_id, a.core_hi, a.use_analytic), load_molecule(mdir, a.sub_id, a.sub_hi, a.use_analytic)
    mapper = atom_map if a.mode == "substituent" else element_map
    am = mapper(man[a.core_id]["smiles"], man[a.sub_id]["smiles"], core["coords"], sub["coords"], core["symbols"], sub["symbols"])
    if am is None:
        print("atom mapping failed (atom order or substructure match)"); return 2
    if a.mode == "element": radii = [0]
    v = read_pair(core, sub, am, radii)
    res = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "label": a.label or f"R{2 if a.mode == 'substituent' else 3}", "mode": a.mode, "radii": radii,
           "low_level": core["low_source"], "use_analytic": a.use_analytic,
           "core": {"id": a.core_id, "name": man[a.core_id]["name"], "high_source": core["high_source"], "n_atoms": len(core["symbols"])},
           "sub": {"id": a.sub_id, "name": man[a.sub_id]["name"], "high_source": sub["high_source"], "n_atoms": len(sub["symbols"])},
           "mapped_atoms": v.pop("mapped_atoms"), "unmapped_core_atoms": v.pop("unmapped_core_atoms"), "variants": v}
    if a.mode == "substituent":
        x = v["transfer_probe_r2"]
        res["verdict_r2"] = "PASS" if x["corrected_freq_rms"] <= 3.3 and x["coupling_ratio"] <= 0.5 else (
            "FAIL" if x["corrected_freq_rms"] > 6 or x["coupling_ratio"] > 0.8 else "BETWEEN")
    else:
        res["hetero_split"] = hetero_split(sub, v["transfer_only_r0"]["per_mode_error_cm"], a.hetero)
    res["seconds"] = round(time.time() - t0, 1)
    Path(a.out_prefix).parent.mkdir(parents=True, exist_ok=True)
    json.dump(res, open(a.out_prefix + ".json", "w", encoding="utf-8"), indent=1, default=float)
    open(a.out_prefix + ".md", "w", encoding="utf-8").write(markdown(res, radii))
    for r in radii:
        for k in VARIANTS:
            x = v[f"{k}_r{r}"]
            print(f"r={r} {k:15s} columns {x['column_fraction']:.2f} | ΔH residual {x['dH_residual_ratio']:.3f} | ring coupling ratio {x['coupling_ratio']:.2f} | "
                  f"corrected ω RMS {x['corrected_freq_rms']:.2f} (zero rule {x['corrected_freq_rms_zero_rule']:.2f})", flush=True)
    print("verdict R2:" if a.mode == "substituent" else "R3 split:", res.get("verdict_r2") or res.get("hetero_split"), "| wrote", a.out_prefix, f"in {res['seconds']} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
