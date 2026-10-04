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
import sys
import time
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
from learning_curve_layerA import AMU2AU  # noqa: E402
from pp import core as C  # noqa: E402
from pp import scorer as S  # noqa: E402
from rungC_equivariant import load_molecule  # noqa: E402
from rungC_train import console_utf8_safe, load_corpus, load_hybrid_model, molecule_tensors  # noqa: E402

FAMILIES = ("ring-ip", "CH-stretch", "CH-oop", "other")
LIMIT_CM, LIMIT_RATIO = 1.0, 0.05


def project_tr(H, masses, x):
    """Translations and rotations projected out (mass-weighted projector); a copy of e8_cc_hessian_fd.project_tr, whose module imports pyscf."""
    n = len(masses); mm = np.repeat(masses * AMU2AU, 3); sm = np.sqrt(mm)
    com = (x * masses[:, None]).sum(0) / masses.sum(); r = x - com
    D = []
    for k in range(3):
        v = np.zeros((n, 3)); v[:, k] = 1.0; D.append((v * np.sqrt(masses)[:, None]).ravel())
    for k in range(3):
        e = np.zeros(3); e[k] = 1.0; v = np.cross(np.tile(e, (n, 1)), r); D.append((v * np.sqrt(masses)[:, None]).ravel())
    D = np.array(D).T; q, _ = np.linalg.qr(D); Pm = np.eye(3 * n) - q @ q.T
    Hmw = H / np.outer(sm, sm); Hp = Pm @ Hmw @ Pm
    return Hp * np.outer(sm, sm), Hmw


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def measured_rows(anchor: Path, ks: list, step: float, n: int) -> dict:
    rows = {}
    for k in ks:
        gp, gm = np.load(anchor / f"grad_{k:02d}_p.npy").ravel(), np.load(anchor / f"grad_{k:02d}_m.npy").ravel()
        rows[k] = (gp - gm) / (2 * step)
    return rows


def hybrid(H_pred: np.ndarray, rows: dict, measured: set, ops, reps, n: int) -> tuple[np.ndarray, float]:
    block = {}
    for i in reps:
        b = np.array(H_pred[3 * i:3 * i + 3])
        for d in range(3):
            k = 3 * i + d
            if k in measured:
                b[d] = rows[k]
        block[i] = b
    return SYM.reconstruct(block, ops, n)


def readout(m: dict, Hp_hyb: np.ndarray, Hp_low: np.ndarray, K_cc: np.ndarray, wt: np.ndarray, fam: np.ndarray, ring: np.ndarray) -> dict:
    K_h = T2.K_from_dH(m, Hp_hyb - Hp_low)
    wp, _ = T2.corrected_frequencies(m, K_h)
    err = wp - wt
    out = {f: float(np.sqrt(np.mean(err[fam == f] ** 2))) for f in FAMILIES if (fam == f).any()}
    off = np.ix_(ring, ring)
    d = (K_h - K_cc)[off]; t = K_cc[off]
    mask = ~np.eye(len(ring), dtype=bool)
    out["ratio"] = float(np.sqrt(np.mean(d[mask] ** 2)) / max(np.sqrt(np.mean(t[mask] ** 2)), 1e-30)) if len(ring) > 1 else float("nan")
    out["all"] = float(np.sqrt(np.mean(err ** 2)))
    return out


def within(r: dict) -> bool:
    return all(r.get(f, 0.0) <= LIMIT_CM for f in FAMILIES) and r["ratio"] <= LIMIT_RATIO


def main() -> int:
    console_utf8_safe()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("anchor"); ap.add_argument("mol_id"); ap.add_argument("out_prefix")
    ap.add_argument("--molecules", default=str(PLAN / "modules" / "05_support_predictor" / "corpus" / "molecules"))
    ap.add_argument("--models", nargs="*", default=[], help="carried checkpoints whose mean ΔH fills the unmeasured rows")
    ap.add_argument("--no-network", action="store_true", help="the analytic B3LYP Hessian alone fills the unmeasured rows (a baseline, not the registered hybrid)")
    ap.add_argument("--seeds", default="0,1,2", help="scorer seeds (modules/standout_pattern_proposer/out/p1_seed<s>.pt)")
    ap.add_argument("--threads", type=int, default=2)
    a = ap.parse_args()
    import torch
    torch.set_num_threads(a.threads)
    t0 = time.time()
    anchor, mol_dir = Path(a.anchor), Path(a.molecules) / a.mol_id
    z = np.load(anchor / "hessian_ccsd_t.npz")
    g = json.load(open(mol_dir / "geometry.json", encoding="utf-8"))
    sym = [s.capitalize() for s in g["symbols"]]; x0 = np.asarray(g["coords_bohr"], float); masses = np.asarray(g["masses_amu"], float); n = len(sym)
    assert np.abs(z["coords_bohr"] - x0).max() < 1e-8, "anchor geometry differs from the corpus geometry"
    ops = SYM.point_group_ops(sym, x0); ks, reps = SYM.unique_displacements(ops, n)
    have = sorted(int(p.name[5:7]) for p in anchor.glob("grad_*_p.npy"))
    assert sorted(ks) == have, f"gradient files {have} do not match the symmetry-unique displacements {sorted(ks)}"
    step = float(z["step"]); H_cc = np.asarray(z["H_raw"], float)
    rows = measured_rows(anchor, ks, step, n)
    H_low = np.asarray(np.load(mol_dir / "hessian_b3lyp_analytic.npz")["H_raw"], float)
    # the corpus record (families, modes) and the network's correction
    mols, *_ = load_corpus(a.molecules, True, log=lambda *_: None)
    m = mols[a.mol_id]
    dH_net, model_notes = np.zeros_like(H_low), []
    if not a.no_network:
        assert a.models, "--models or --no-network"
        preds = []
        for mp in a.models:
            st = MR.require_carried(Path(mp))
            model, ck = load_hybrid_model(Path(mp))
            cfg = SimpleNamespace(aux=ck["aux_mode"], head=ck["head"], pattern=ck["pattern"], aux_target=ck["aux_target"], ls_lam=ck["ls_lam"], zero_hlow=False)
            t = molecule_tensors(a.mol_id, load_molecule(mol_dir, use_analytic=True), m, mol_dir, cfg, Path(a.out_prefix).parent / "ls_targets")
            model.eval()
            with torch.no_grad():
                preds.append(model(t["Z"], t["pos"], t["H_low"], t).numpy().astype(float))
            model_notes.append({"path": str(mp), "status": st["status"], "sha": sha(Path(mp))})
        dH_net = np.mean(preds, axis=0)
    H_pred = H_low + dH_net
    Hp_cc = project_tr(H_cc, masses, x0)[0]; Hp_low = project_tr(H_low, masses, x0)[0]
    K_cc = T2.K_from_dH(m, Hp_cc - Hp_low)
    wt, Ut = T2.corrected_frequencies(m, K_cc)
    fam = np.array(m["family"])[np.argmax(np.abs(Ut), axis=0)]
    ring = np.where(np.array(m["family"]) == "ring-ip")[0]
    # orders
    blind = list(ks)
    oracle = sorted(ks, key=lambda k: -float(np.linalg.norm(H_cc[k] - H_pred[k])))
    exp = C.export_molecule(mol_dir, use_analytic=True, hi_override=anchor / "hessian_ccsd_t.npz")
    X, _, pairs = S.pair_features(exp)
    seeds = [int(s) for s in a.seeds.split(",")]
    Smat = np.mean([S.scores_matrix(exp, S.Scorer.load(PLAN / "modules" / "standout_pattern_proposer" / "out" / "p1", s).predict(X), pairs) for s in seeds], axis=0)
    V = np.asarray(exp["V"], float)                                        # (3N, M), mass-weighted normal modes of the analytic B3LYP Hessian
    s_k = (V ** 2) @ Smat.sum(1)                                            # Σ_{i<j} S_ij (V_ki² + V_kj²) for every Cartesian coordinate k
    p1 = sorted(ks, key=lambda k: -float(s_k[k]))
    scorer_sha = [sha(PLAN / "modules" / "standout_pattern_proposer" / "out" / f"p1_seed{s}.pt") for s in seeds]
    orders = {"P1": p1, "blind": blind, "oracle": oracle}
    curves, first, first_fam = {}, {}, {}
    for name, order in orders.items():
        cur = []
        for t_ in range(len(order) + 1):
            H_h, spread = hybrid(H_pred, rows, set(order[:t_]), ops, reps, n)
            r = readout(m, project_tr(H_h, masses, x0)[0], Hp_low, K_cc, wt, fam, ring)
            r.update(k=t_, pct=100.0 * t_ / len(order), spread=float(spread), within=within(r))
            cur.append(r)
        curves[name] = cur
        first[name] = next((r["k"] for r in cur if r["within"]), None)
        first_fam[name] = {f: next((r["k"] for r in cur if r.get(f, 0.0) <= LIMIT_CM), None) for f in FAMILIES}
        first_fam[name]["ratio"] = next((r["k"] for r in cur if r["ratio"] <= LIMIT_RATIO), None)
    nk = len(ks)
    md = [f"# Deck rehearsal on {a.mol_id} ({anchor.name}) — {datetime.now():%Y-%m-%d %H:%M}", "",
          f"{nk} symmetry-unique displacements ({len(reps)} representative atoms, {len(ops)} operations); unmeasured rows from "
          + ("the analytic B3LYP Hessian alone (--no-network)" if a.no_network else f"B3LYP + the mean ΔH of {len(model_notes)} carried model(s)")
          + f"; scorer seeds {seeds} (sha {', '.join(scorer_sha)}). Limits: rms ≤ {LIMIT_CM} cm⁻¹ in every family and ring-coupling ratio ≤ {LIMIT_RATIO}. "
          "k = 0 is the prediction alone (the 'network as is' column of the T3 read), k = all is the anchor itself.", "",
          "| order | first k within the limits | share of the gradients |", "|---|---|---|"]
    for name in orders:
        md.append(f"| {name} | {first[name] if first[name] is not None else 'never'} / {nk} | {('%.0f %%' % (100 * first[name] / nk)) if first[name] is not None else '—'} |")
    md += ["", "Per read-out, the first k at which that family's rms is within the limit (ratio: within its limit) — the split of the verdict, not a registered line:", "",
           "| order | " + " | ".join(FAMILIES) + " | ratio |", "|---|" + "---|" * (len(FAMILIES) + 1)]
    for name in orders:
        md.append(f"| {name} | " + " | ".join(str(first_fam[name][c]) if first_fam[name][c] is not None else "never" for c in [*FAMILIES, "ratio"]) + " |")
    md += ["", "## Curves (k gradients → rms per family in cm⁻¹, ring-coupling ratio)", ""]
    for name, cur in curves.items():
        md += [f"### {name}", "", "| k | % | " + " | ".join(FAMILIES) + " | all | ratio | spread |", "|---|---|" + "---|" * (len(FAMILIES) + 3)]
        for r in cur:
            md.append(f"| {r['k']} | {r['pct']:.0f} | " + " | ".join(f"{r[f]:.2f}" if f in r else "—" for f in FAMILIES) + f" | {r['all']:.2f} | {r['ratio']:.3f} | {r['spread']:.1e} |")
        md.append("")
    res = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "anchor": str(anchor), "mol_id": a.mol_id, "n_unique": nk, "reps": reps, "ks": ks, "orders": orders,
           "first_within": first, "first_per_readout": first_fam, "limits": {"cm": LIMIT_CM, "ratio": LIMIT_RATIO}, "no_network": a.no_network, "models": model_notes,
           "scorer_seeds": seeds, "scorer_sha": scorer_sha, "curves": curves, "seconds": round(time.time() - t0)}
    Path(a.out_prefix + ".md").write_text("\n".join(md), encoding="utf-8")
    Path(a.out_prefix + ".json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    print("\n".join(md[:18]))
    print(f"→ {a.out_prefix}.md ({res['seconds']} s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
