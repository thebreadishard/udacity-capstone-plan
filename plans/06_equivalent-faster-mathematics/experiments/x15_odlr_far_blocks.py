"""X15 (2026-09-13) — off-diagonal low rank (ODLR) of the DFT Hessian's far blocks in PAHs, at band level (after reading O1NumHess).

Serves the decision rule's branch M (T3's restatement: Δ₂ = local + low-rank?) and branch C (lever C beyond the symmetry prior).
O1NumHess (Wang, Luo, Wang & Liu 2025) rests on the claim that the Hessian blocks between two DISTANT groups of atoms have low numerical
rank even when they are not small. Plan 02's stored B3LYP/6-31G* Hessians (git 57a7910) allow the claim to be tested on PAHs today, and —
because plan 05's tolerance is 0.5 cm⁻¹ on band positions — tested where it matters: not "how many singular values are small" but
"what rank r must the far blocks keep so that no harmonic band moves by more than 0.5 cm⁻¹ when H_AB is replaced by its rank-r truncation".

Groups: atoms ordered along the long inertial axis; A = the first third, B = the last third ("distant thirds"); and A = first half, B = second
half ("halves", larger and closer blocks). For each: block H_AB of the mass-weighted Hessian (3|A| × 3|B|), its singular values (relative to
the largest), the numerical rank at 1e-2 / 1e-3 / 1e-4, and the band-level rank r*(0.5 cm⁻¹) — the smallest r such that the max band shift
of the truncated Hessian (H_AB and H_BA replaced by the rank-r SVD truncation, everything else kept) is ≤ 0.5 cm⁻¹ — plus the shift at r = 0
(far blocks zeroed) and the shift at r = 3 and r = 6. Losing condition for ODLR at plan 05's tolerance (pre-stated in the O1NumHess reading
note): r* above a third of the block dimension. Molecules: the eight PAHs beyond benzene in X12. Every number from the files."""
import json
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
HARTREE_TO_CM = 219474.63
AMU_TO_ME = 1822.888486209
CONSTANTS = {"git_commit": "57a7910", "n_zero_modes": 6, "tolerance_cm": 0.5, "rank_thresholds_rel": [1e-2, 1e-3, 1e-4], "report_ranks": [0, 1, 2, 3, 6, 9, 12],
             "files": {"naphthalene": "plans/02_coupled-cluster-anharmonic-ir/probes/results_dft_locality/naphthalene.npz",
                       "anthracene": "plans/02_coupled-cluster-anharmonic-ir/probes/results_dft_locality/anthracene.npz",
                       "phenanthrene": "plans/02_coupled-cluster-anharmonic-ir/probes/batch_results/02_freq_phenanthrene.npz",
                       "tetracene": "plans/02_coupled-cluster-anharmonic-ir/probes/batch_results/03_freq_tetracene.npz",
                       "chrysene": "plans/02_coupled-cluster-anharmonic-ir/probes/batch_results/04_freq_chrysene.npz",
                       "triphenylene": "plans/02_coupled-cluster-anharmonic-ir/probes/batch_results/05_freq_triphenylene.npz",
                       "pyrene": "plans/02_coupled-cluster-anharmonic-ir/probes/batch_results/06_freq_pyrene.npz",
                       "coronene": "plans/02_coupled-cluster-anharmonic-ir/probes/batch_results/07_freq_coronene.npz"}}


def load_from_git(relpath, tmpdir):
    out = Path(tmpdir) / Path(relpath).name
    with open(out, "wb") as f:
        subprocess.run(["git", "-C", str(REPO), "show", f"{CONSTANTS['git_commit']}:{relpath}"], check=True, stdout=f)
    with np.load(out) as z:
        return {k: z[k] for k in z.files}


def freqs_cm(Hmw):
    w2 = np.linalg.eigvalsh((Hmw + Hmw.T) / 2)
    w2 = w2[np.argsort(np.abs(w2))][CONSTANTS["n_zero_modes"]:]
    return np.sort(np.sign(w2) * np.sqrt(np.abs(w2)) * HARTREE_TO_CM)


def long_axis_order(X, m):
    c = (X * m[:, None]).sum(0) / m.sum(); Y = X - c
    I = np.zeros((3, 3))
    for y, mm in zip(Y, m):
        I += mm * (np.dot(y, y) * np.eye(3) - np.outer(y, y))
    w, V = np.linalg.eigh(I)
    ax = V[:, np.argmin(w)]                      # smallest moment = long axis
    return np.argsort(Y @ ax), Y @ ax


def truncate(Hmw, A, B, r):
    idx = lambda G: np.concatenate([[3 * a, 3 * a + 1, 3 * a + 2] for a in G])
    ia, ib = idx(A), idx(B)
    H = Hmw.copy(); blk = Hmw[np.ix_(ia, ib)]
    U, s, Vt = np.linalg.svd(blk, full_matrices=False)
    tr = (U[:, :r] * s[:r]) @ Vt[:r] if r > 0 else np.zeros_like(blk)
    H[np.ix_(ia, ib)] = tr; H[np.ix_(ib, ia)] = tr.T
    return H, s


def analyse(name, z):
    H, X, m = z["hessian_au"], z["coords_bohr"], z["masses_amu"]; nat = len(m)
    minv = 1.0 / np.sqrt(np.repeat(m, 3) * AMU_TO_ME); Hmw = minv[:, None] * H * minv[None, :]
    f0 = freqs_cm(Hmw)
    order, proj = long_axis_order(X, m)
    res = {"molecule": name, "natom": nat, "length_bohr": float(proj.max() - proj.min()), "splits": {}}
    for label, (A, B) in {"distant thirds": (order[: nat // 3], order[-(nat // 3):]), "halves": (order[: nat // 2], order[nat // 2:])}.items():
        # minimum inter-group distance
        D = np.linalg.norm(X[A][:, None] - X[B][None], axis=2); dmin = float(D.min())
        _, s = truncate(Hmw, A, B, 0); srel = s / s[0]
        ranks = {str(t): int((srel > t).sum()) for t in CONSTANTS["rank_thresholds_rel"]}
        shifts = {}
        for r in CONSTANTS["report_ranks"]:
            if r <= len(s):
                Ht, _ = truncate(Hmw, A, B, r); shifts[str(r)] = float(np.abs(freqs_cm(Ht) - f0).max())
        rstar = None
        for r in range(0, len(s) + 1):
            Ht, _ = truncate(Hmw, A, B, r)
            if np.abs(freqs_cm(Ht) - f0).max() <= CONSTANTS["tolerance_cm"]:
                rstar = r; break
        res["splits"][label] = {"nA": len(A), "nB": len(B), "block_dim": [3 * len(A), 3 * len(B)], "min_intergroup_distance_bohr": dmin,
                                "singular_values_rel_top12": srel[:12].tolist(), "numerical_rank": ranks, "max_band_shift_by_rank_cm": shifts,
                                "r_star_0p5cm": rstar, "r_star_over_block_dim": (rstar / min(3 * len(A), 3 * len(B))) if rstar is not None else None}
    return res


def main():
    out = {"date": f"{datetime.now():%Y-%m-%d %H:%M}", "constants": CONSTANTS, "molecules": []}
    with tempfile.TemporaryDirectory() as tmp:
        for name, rel in CONSTANTS["files"].items():
            r = analyse(name, load_from_git(rel, tmp)); out["molecules"].append(r)
            t = r["splits"]["distant thirds"]; print(name, "thirds: dim", t["block_dim"], "rank@1e-3", t["numerical_rank"]["0.001"], "shift r=0", round(t["max_band_shift_by_rank_cm"]["0"], 1), "r*", t["r_star_0p5cm"], flush=True)
    json.dump(out, open(HERE / "x15_odlr_far_blocks.json", "w"), indent=1)
    L = [f"# X15 — off-diagonal low rank of the DFT Hessian's far blocks, at band level (B3LYP/6-31G*, plan 02 git {CONSTANTS['git_commit']}; {out['date']})", "",
         "Groups A and B along the long inertial axis (first/last third; first/second half). Block H_AB of the mass-weighted Hessian: singular values relative to the largest, "
         "numerical rank at three relative thresholds, and the largest harmonic band shift when H_AB (and H_BA) is replaced by its rank-r truncation; r* = smallest r with shift ≤ 0.5 cm⁻¹. "
         "Losing condition for ODLR at plan 05's tolerance: r* above a third of the block dimension.", ""]
    for label in ("distant thirds", "halves"):
        L += [f"## {label}", "", "| molecule | atoms A/B | block dim | min A–B distance (bohr) | rank at 1e-2 / 1e-3 / 1e-4 | shift r=0 / 1 / 3 / 6 (cm⁻¹) | **r\\* (0.5 cm⁻¹)** | r\\*/dim |", "|---|---|---|---|---|---|---|---|"]
        for r in out["molecules"]:
            t = r["splits"][label]; sh = t["max_band_shift_by_rank_cm"]; nr = t["numerical_rank"]
            L.append(f"| {r['molecule']} | {t['nA']}/{t['nB']} | {t['block_dim'][0]}×{t['block_dim'][1]} | {t['min_intergroup_distance_bohr']:.1f} | {nr['0.01']} / {nr['0.001']} / {nr['0.0001']} | "
                     f"{sh.get('0', float('nan')):.1f} / {sh.get('1', float('nan')):.1f} / {sh.get('3', float('nan')):.1f} / {sh.get('6', float('nan')):.1f} | **{t['r_star_0p5cm']}** | {t['r_star_over_block_dim']:.2f} |")
        L.append("")
    L += ["Top relative singular values (distant thirds):", ""] + [f"- **{r['molecule']}**: " + ", ".join(f"{v:.1e}" for v in r["splits"]["distant thirds"]["singular_values_rel_top12"]) for r in out["molecules"]]
    L += ["", "Reading: O1NumHess's ODLR predicts few dominant singular values in far blocks. The band-level r* says how many of them plan 05's 0.5 cm⁻¹ actually needs — "
          "if r* is a small fraction of the block dimension, a low-rank far part is a licensed structure for the DFT Hessian at this tolerance (the correction Δ₂ is a separate question, X15 on naphthalene later). "
          "Triphenylene and coronene files carry one imaginary mode each (X12).", "", "Constants: " + json.dumps(CONSTANTS)]
    (HERE / "x15_odlr_far_blocks.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[:34]).encode("ascii", "replace").decode())


if __name__ == "__main__":
    main()
