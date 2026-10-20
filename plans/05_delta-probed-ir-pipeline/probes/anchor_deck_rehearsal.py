"""Rehearsal of decision 58 on an existing anchor: how many of its symmetry-unique CC gradients does a hybrid anchor need when the carried network
fills in the rest? (Registered 4 Oct 2026 09:1x, `PreRegistration_2026-10-04_Proposer_Order_Rehearsal_Naphthalene.md`.)

For an anchor directory with the per-displacement gradients (`grad_<k>_<p|m>.npy`, k the Cartesian index of a symmetry-unique displacement) and its
assembled Hessian: the hybrid Hessian after the first t displacements of an order = the measured rows for those displacements, the predicted rows
(analytic B3LYP + the network's ΔH, or B3LYP alone with --no-network) for the others, expanded by the point group (`e8_symmetry.reconstruct`),
translations and rotations projected out. Read-out per t: corrected-ω rms per family against the full anchor (modes paired in the B3LYP mode basis as
`e7_t2_sqm.corrected_frequencies`) and the ring-coupling ratio of the hybrid's error. Three orders: **P1** — the standout's hand-feature scorer
(`modules/standout_pattern_proposer/out/p1_seed*.pt`, mean of the seeds given) adapted to displacements, s_k = Σ_{i<j} S_ij (V_ki² + V_kj²) with V the
mass-weighted normal modes (a displacement weighs each mode pair by its share in the two modes); **blind** — the probe's own symmetry-unique order;
**oracle** — descending true row error of the prediction. Limits: rms ≤ 1 cm⁻¹ in every family and ratio ≤ 0.05.

    python probes/anchor_deck_rehearsal.py <anchor dir> <corpus molecule id> <out_prefix> [--models m1.pt m2.pt ...] [--no-network] [--seeds 0,1,2]
"""
import argparse
import hashlib
import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "m05"))
sys.path.insert(0, str(PLAN / "modules" / "standout_pattern_proposer"))
sys.path.insert(0, str(PLAN / "probes"))
import e7_t2_sqm as T2  # noqa: E402
import e8_symmetry as SYM  # noqa: E402
import model_registry as MR  # noqa: E402
from pp import core as C  # noqa: E402
from pp import scorer as S  # noqa: E402
from qc_common import project_tr  # noqa: E402
from rungC_equivariant import load_molecule  # noqa: E402
from rungC_train import console_utf8_safe, load_corpus, load_hybrid_model, molecule_tensors  # noqa: E402

FAMILIES = ("ring-ip", "CH-stretch", "CH-oop", "other")
LIMIT_CM, LIMIT_RATIO = 1.0, 0.05
GEOMETRY_TOL_BOHR = 1e-8
SCORER = PLAN / "modules" / "standout_pattern_proposer" / "out"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


@dataclass(frozen=True)
class Truth:
    """A reference Hessian's correction in the low level's mode basis: its K, its corrected frequencies, each mode's family (by its largest
    component), the ring-ip modes of the corpus record."""
    K: np.ndarray
    w: np.ndarray
    fam: np.ndarray
    ring: np.ndarray


def truth_of(m: dict, Hp_true: np.ndarray, Hp_low: np.ndarray) -> Truth:
    K = T2.K_from_dH(m, Hp_true - Hp_low)
    w, U = T2.corrected_frequencies(m, K)
    return Truth(K, w, np.array(m["family"])[np.argmax(np.abs(U), axis=0)], np.where(np.array(m["family"]) == "ring-ip")[0])


def readout(m: dict, Hp_test: np.ndarray, Hp_low: np.ndarray, truth: Truth) -> dict:
    """Corrected-ω rms per family and over all modes against the truth, and the ring-coupling ratio of the test Hessian's error."""
    K_h = T2.K_from_dH(m, Hp_test - Hp_low)
    wp, _ = T2.corrected_frequencies(m, K_h)
    err = wp - truth.w
    out = {f: float(np.sqrt(np.mean(err[truth.fam == f] ** 2))) for f in FAMILIES if (truth.fam == f).any()}
    off = np.ix_(truth.ring, truth.ring)
    d = (K_h - truth.K)[off]
    t = truth.K[off]
    mask = ~np.eye(len(truth.ring), dtype=bool)
    out["ratio"] = float(np.sqrt(np.mean(d[mask] ** 2)) / max(np.sqrt(np.mean(t[mask] ** 2)), 1e-30)) if len(truth.ring) > 1 else float("nan")
    out["all"] = float(np.sqrt(np.mean(err ** 2)))
    return out


def within(r: dict) -> bool:
    return all(r.get(f, 0.0) <= LIMIT_CM for f in FAMILIES) and r["ratio"] <= LIMIT_RATIO


def measured_rows(anchor: Path, ks: list, step: float) -> dict:
    rows = {}
    for k in ks:
        gp, gm = np.load(anchor / f"grad_{k:02d}_p.npy").ravel(), np.load(anchor / f"grad_{k:02d}_m.npy").ravel()
        rows[k] = (gp - gm) / (2 * step)
    return rows


def hybrid(H_pred: np.ndarray, rows: dict, measured: set, sym: tuple) -> tuple[np.ndarray, float]:
    """The predicted rows with the measured ones put in, expanded by the point group (`sym` = operations, representatives, atom count)."""
    ops, reps, n = sym
    block = {}
    for i in reps:
        b = np.array(H_pred[3 * i:3 * i + 3])
        for d in range(3):
            if 3 * i + d in measured:
                b[d] = rows[3 * i + d]
        block[i] = b
    return SYM.reconstruct(block, ops, n)


@dataclass(frozen=True)
class Anchor:
    """The anchor run, its corpus molecule and what the rehearsal reads from both."""
    path: Path
    mol_dir: Path
    masses: np.ndarray
    x0: np.ndarray
    ops: list
    ks: list
    reps: list
    rows: dict
    H_cc: np.ndarray
    H_low: np.ndarray


def load_anchor(anchor: Path, mol_dir: Path) -> Anchor:
    """The anchor's Hessian and per-displacement rows, refused when they do not belong to the corpus molecule's geometry and symmetry."""
    g = json.loads((mol_dir / "geometry.json").read_text(encoding="utf-8"))
    sym = [s.capitalize() for s in g["symbols"]]
    x0, masses = np.asarray(g["coords_bohr"], float), np.asarray(g["masses_amu"], float)
    with np.load(anchor / "hessian_ccsd_t.npz") as z:
        if np.abs(z["coords_bohr"] - x0).max() >= GEOMETRY_TOL_BOHR:
            raise SystemExit("anchor geometry differs from the corpus geometry")
        step, H_cc = float(z["step"]), np.asarray(z["H_raw"], float)
    ops = SYM.point_group_ops(sym, x0)
    ks, reps = SYM.unique_displacements(ops, len(sym))
    have = sorted(int(p.name[5:7]) for p in anchor.glob("grad_*_p.npy"))
    if sorted(ks) != have:
        raise SystemExit(f"gradient files {have} do not match the symmetry-unique displacements {sorted(ks)}")
    with np.load(mol_dir / "hessian_b3lyp_analytic.npz") as z:
        H_low = np.asarray(z["H_raw"], float)
    return Anchor(anchor, mol_dir, masses, x0, ops, ks, reps, measured_rows(anchor, ks, step), H_cc, H_low)


def network_correction(a, m: dict, mol_dir: Path, shape) -> tuple[np.ndarray, list[dict]]:
    """The mean ΔH of the carried models (zero with --no-network) and a note per model."""
    if a.no_network:
        return np.zeros(shape), []
    if not a.models:
        raise SystemExit("--models or --no-network")
    import torch
    preds, notes = [], []
    for mp in a.models:
        st = MR.require_carried(Path(mp))
        model, ck = load_hybrid_model(Path(mp))
        cfg = SimpleNamespace(aux=ck["aux_mode"], head=ck["head"], pattern=ck["pattern"], aux_target=ck["aux_target"], ls_lam=ck["ls_lam"], zero_hlow=False)
        t = molecule_tensors(a.mol_id, load_molecule(mol_dir, use_analytic=True), m, mol_dir, cfg, Path(a.out_prefix).parent / "ls_targets")
        model.eval()
        with torch.no_grad():
            preds.append(model(t["Z"], t["pos"], t["H_low"], t).numpy().astype(float))
        notes.append({"path": str(mp), "status": st["status"], "sha": sha(Path(mp))})
    return np.mean(preds, axis=0), notes


def p1_order(an: Anchor, seeds: list[int]) -> list[int]:
    """The P1 order: displacements by s_k = Σ_{i<j} S_ij (V_ki² + V_kj²), S the scorer's pair scores averaged over the seeds."""
    exp = C.export_molecule(an.mol_dir, use_analytic=True, hi_override=an.path / "hessian_ccsd_t.npz")
    X, _, pairs = S.pair_features(exp)
    for s in seeds:                                                        # decision 59: the order scorer is a registered network (status carried, v1.0)
        MR.require_carried(SCORER / f"p1_seed{s}.pt")
    Smat = np.mean([S.scores_matrix(exp, S.Scorer.load(SCORER / "p1", s).predict(X), pairs) for s in seeds], axis=0)
    V = np.asarray(exp["V"], float)                                        # (3N, M), mass-weighted normal modes of the analytic B3LYP Hessian
    s_k = (V ** 2) @ Smat.sum(1)                                            # Σ_{i<j} S_ij (V_ki² + V_kj²) for every Cartesian coordinate k
    return sorted(an.ks, key=lambda k: -float(s_k[k]))


def curve(an: Anchor, m: dict, H_pred: np.ndarray, order: list[int], truth: Truth, Hp_low: np.ndarray) -> list[dict]:
    """The read-out after the first t displacements of the order, t = 0 … all."""
    cur = []
    for t_ in range(len(order) + 1):
        H_h, spread = hybrid(H_pred, an.rows, set(order[:t_]), (an.ops, an.reps, len(an.masses)))
        r = readout(m, project_tr(H_h, an.masses, an.x0)[0], Hp_low, truth)
        r.update(k=t_, pct=100.0 * t_ / len(order), spread=float(spread), within=within(r))
        cur.append(r)
    return cur


def firsts(cur: list[dict]) -> tuple[int | None, dict]:
    """The first k within every limit, and per read-out the first k within its own limit."""
    per = {f: next((r["k"] for r in cur if r.get(f, 0.0) <= LIMIT_CM), None) for f in FAMILIES}
    per["ratio"] = next((r["k"] for r in cur if r["ratio"] <= LIMIT_RATIO), None)
    return next((r["k"] for r in cur if r["within"]), None), per


def report_lines(a, an: Anchor, res: dict) -> list[str]:
    nk, first, first_fam = res["n_unique"], res["first_within"], res["first_per_readout"]
    md = [f"# Deck rehearsal on {a.mol_id} ({an.path.name}) — {res['date']}", "",
          f"{nk} symmetry-unique displacements ({len(an.reps)} representative atoms, {len(an.ops)} operations); unmeasured rows from "
          + ("the analytic B3LYP Hessian alone (--no-network)" if a.no_network else f"B3LYP + the mean ΔH of {len(res['models'])} carried model(s)")
          + f"; scorer seeds {res['scorer_seeds']} (sha {', '.join(res['scorer_sha'])}). Limits: rms ≤ {LIMIT_CM} cm⁻¹ in every family and "
          f"ring-coupling ratio ≤ {LIMIT_RATIO}. k = 0 is the prediction alone (the 'network as is' column of the T3 read), k = all is the anchor itself.",
          "", "| order | first k within the limits | share of the gradients |", "|---|---|---|"]
    for name in res["orders"]:
        md.append(f"| {name} | {first[name] if first[name] is not None else 'never'} / {nk} | "
                  f"{f'{100 * first[name] / nk:.0f} %' if first[name] is not None else '—'} |")
    md += ["", "Per read-out, the first k at which that family's rms is within the limit (ratio: within its limit) — the split of the verdict, "
           "not a registered line:", "", "| order | " + " | ".join(FAMILIES) + " | ratio |", "|---|" + "---|" * (len(FAMILIES) + 1)]
    for name in res["orders"]:
        md.append(f"| {name} | " + " | ".join(str(first_fam[name][c]) if first_fam[name][c] is not None else "never" for c in [*FAMILIES, "ratio"]) + " |")
    md += ["", "## Curves (k gradients → rms per family in cm⁻¹, ring-coupling ratio)", ""]
    for name, cur in res["curves"].items():
        md += [f"### {name}", "", "| k | % | " + " | ".join(FAMILIES) + " | all | ratio | spread |", "|---|---|" + "---|" * (len(FAMILIES) + 3)]
        for r in cur:
            md.append(f"| {r['k']} | {r['pct']:.0f} | " + " | ".join(f"{r[f]:.2f}" if f in r else "—" for f in FAMILIES)
                      + f" | {r['all']:.2f} | {r['ratio']:.3f} | {r['spread']:.1e} |")
        md.append("")
    return md


def write_text(path: str, text: str) -> None:
    tmp = path + ".tmp"
    Path(tmp).write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for name in ("anchor", "mol_id", "out_prefix"):
        ap.add_argument(name)
    ap.add_argument("--molecules", default=str(PLAN / "modules" / "05_support_predictor" / "corpus" / "molecules"))
    ap.add_argument("--models", nargs="*", default=[], help="carried checkpoints whose mean ΔH fills the unmeasured rows")
    ap.add_argument("--no-network", action="store_true", help="the analytic B3LYP Hessian alone fills the unmeasured rows (a baseline, not the "
                    "registered hybrid)")
    ap.add_argument("--seeds", default="0,1,2", help="scorer seeds (modules/standout_pattern_proposer/out/p1_seed<s>.pt)")
    ap.add_argument("--threads", type=int, default=2)
    return ap


def main() -> int:
    console_utf8_safe()
    a = build_parser().parse_args()
    import torch
    torch.set_num_threads(a.threads)
    t0 = time.time()
    an = load_anchor(Path(a.anchor), Path(a.molecules) / a.mol_id)
    mols, *_ = load_corpus(a.molecules, True, log=lambda *_: None)          # the corpus record (families, modes)
    m = mols[a.mol_id]
    dH_net, model_notes = network_correction(a, m, an.mol_dir, an.H_low.shape)
    H_pred = an.H_low + dH_net
    Hp_low = project_tr(an.H_low, an.masses, an.x0)[0]
    truth = truth_of(m, project_tr(an.H_cc, an.masses, an.x0)[0], Hp_low)
    seeds = [int(s) for s in a.seeds.split(",")]
    orders = {"P1": p1_order(an, seeds), "blind": list(an.ks), "oracle": sorted(an.ks, key=lambda k: -float(np.linalg.norm(an.H_cc[k] - H_pred[k])))}
    curves = {name: curve(an, m, H_pred, order, truth, Hp_low) for name, order in orders.items()}
    first, first_fam = {}, {}
    for name, cur in curves.items():
        first[name], first_fam[name] = firsts(cur)
    res = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "anchor": str(an.path), "mol_id": a.mol_id, "n_unique": len(an.ks), "reps": an.reps,
           "ks": an.ks, "orders": orders, "first_within": first, "first_per_readout": first_fam, "limits": {"cm": LIMIT_CM, "ratio": LIMIT_RATIO},
           "no_network": a.no_network, "models": model_notes, "scorer_seeds": seeds,
           "scorer_sha": [sha(SCORER / f"p1_seed{s}.pt") for s in seeds], "curves": curves}
    md = report_lines(a, an, res)
    res["seconds"] = round(time.time() - t0)
    write_text(a.out_prefix + ".md", "\n".join(md))
    write_text(a.out_prefix + ".json", json.dumps(res, indent=1))
    print("\n".join(md[:18]))
    print(f"→ {a.out_prefix}.md ({res['seconds']} s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
