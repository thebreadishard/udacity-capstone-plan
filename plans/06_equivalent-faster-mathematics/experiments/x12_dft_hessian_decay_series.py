"""X12 (2026-09-12, evening) — how the DFT Hessian itself decays with bond-graph distance, benzene → coronene (the mean-field half of T3/T3′).

X9 compared the correction with the DFT Hessian at benzene (graph distance ≤ 3). The correction's tensor does not exist for larger
molecules yet, but the DFT Hessian does: plan 02 stored B3LYP/6-31G* Hessians for benzene, naphthalene, anthracene (its locality probe)
and phenanthrene, tetracene, chrysene, triphenylene, pyrene, coronene (its batch runner) in git commit 57a7910 (the arrays were removed
from the tree on 2026-09-06 and live in history only). This script extracts them with `git show`, mass-weights them, cuts them into 3×3
atom-pair blocks and prints, per molecule, the median block norm per bond-graph distance (0 … max), the decay rate per bond from a
log-linear fit over distances 1 … max (on-atom blocks excluded), and the band-level far-block dependence (X2's exact rule: zero every
block at graph distance ≥ d*, largest harmonic shift) for d* = 2, 3, 4.

Why it matters: T3's hypothesis audit says the mean-field part is short-ranged (bonded force constants) and the correction's range follows
the π system; X9 showed the correction's share of the Hessian rising with distance at benzene. The Hessian-side decay length across the
series is the reference against which the naphthalene correction will be read (X9 on naphthalene), and it is the DFT-side "range" that
decision 32's precondition (a transferable model) implicitly assumes. Every number printed comes from the files; constants in CONSTANTS."""
import json
import subprocess
import tempfile
from collections import deque
from datetime import datetime
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
HARTREE_TO_CM = 219474.63
AMU_TO_ME = 1822.888486209
CONSTANTS = {"git_commit": "57a7910", "bond_cutoff_bohr": {"CC": 3.0, "CH": 2.4}, "n_zero_modes": 6, "distance_cuts_for_band_test": [2, 3, 4],
             "files": {"benzene": "plans/02_coupled-cluster-anharmonic-ir/probes/results_dft_locality/benzene.npz",
                       "naphthalene": "plans/02_coupled-cluster-anharmonic-ir/probes/results_dft_locality/naphthalene.npz",
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


def symbols_from_masses(m):
    return ["C" if x > 6 else "H" for x in m]


def graph_distance(sym, X):
    n = len(sym); D = np.linalg.norm(X[:, None] - X[None], axis=2)
    adj = [[j for j in range(n) if j != i and D[i, j] < CONSTANTS["bond_cutoff_bohr"].get("".join(sorted(sym[i] + sym[j])), 0.0)] for i in range(n)]
    G = np.full((n, n), 99, int)
    for s in range(n):
        G[s, s] = 0; q = deque([s])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if G[s, v] == 99:
                    G[s, v] = G[s, u] + 1; q.append(v)
    return G, adj


def freqs_cm(Hmw):
    w2 = np.linalg.eigvalsh((Hmw + Hmw.T) / 2)
    w2 = w2[np.argsort(np.abs(w2))][CONSTANTS["n_zero_modes"]:]
    return np.sort(np.sign(w2) * np.sqrt(np.abs(w2)) * HARTREE_TO_CM)


def main():
    out = {"date": f"{datetime.now():%Y-%m-%d %H:%M}", "constants": CONSTANTS, "molecules": []}
    with tempfile.TemporaryDirectory() as tmp:
        for name, rel in CONSTANTS["files"].items():
            z = load_from_git(rel, tmp)
            H, X, m = z["hessian_au"], z["coords_bohr"], z["masses_amu"]
            sym = symbols_from_masses(m); n = len(sym)
            minv = 1.0 / np.sqrt(np.repeat(m, 3) * AMU_TO_ME)
            Hmw = minv[:, None] * H * minv[None, :]
            G, adj = graph_distance(sym, X)
            maxdeg = max(len(a) for a in adj)
            B = np.array([[np.linalg.norm(Hmw[3 * a:3 * a + 3, 3 * b:3 * b + 3]) for b in range(n)] for a in range(n)])
            prof = []
            for d in sorted(set(G[np.triu_indices(n)].tolist())):
                idx = [(i, j) for i in range(n) for j in range(i, n) if G[i, j] == d]
                prof.append((int(d), len(idx), float(np.median([B[i, j] for i, j in idx])), float(max(B[i, j] for i, j in idx))))
            ds = np.array([p[0] for p in prof if p[0] >= 1]); ys = np.log([p[2] for p in prof if p[0] >= 1])
            slope = float(np.polyfit(ds, ys, 1)[0]) if len(ds) >= 2 else None
            sel = (ds >= 1) & (ds <= 4)
            slope4 = float(np.polyfit(ds[sel], ys[sel], 1)[0]) if sel.sum() >= 2 else None
            f_full = freqs_cm(Hmw)
            band = {}
            for dstar in CONSTANTS["distance_cuts_for_band_test"]:
                if dstar <= G[G < 99].max():
                    P = np.kron(G < dstar, np.ones((3, 3), bool))
                    band[str(dstar)] = float(np.abs(freqs_cm(Hmw * P) - f_full).max())
            out["molecules"].append({"molecule": name, "nC": sym.count("C"), "nH": sym.count("H"), "max_graph_distance": int(G[G < 99].max()), "max_degree": maxdeg,
                                     "top_freq_cm": float(f_full[-1]), "n_imag": int((f_full < 0).sum()),
                                     "profile": [{"d": d, "pairs": k, "median": med, "max": mx} for d, k, med, mx in prof],
                                     "log_slope_per_bond": slope, "decay_factor_per_bond": float(np.exp(slope)) if slope is not None else None,
                                     "decay_factor_per_bond_d1to4": float(np.exp(slope4)) if slope4 is not None else None,
                                     "band_shift_zeroing_far_blocks_cm": band})
            print(name, "max d", int(G[G < 99].max()), "factor/bond", round(float(np.exp(slope)), 3) if slope else None, "top", round(float(f_full[-1]), 1), flush=True)
    json.dump(out, open(HERE / "x12_dft_hessian_decay_series.json", "w"), indent=1)
    L = [f"# X12 — decay of the B3LYP/6-31G* Hessian with bond-graph distance, benzene → coronene ({out['date']})", "",
         f"Hessians from plan 02 (git `{CONSTANTS['git_commit']}`), mass-weighted (amu → mₑ), 3×3 atom-pair blocks; median block norm per bond-graph distance; "
         "decay factor per bond from a log-linear fit over distances ≥ 1 (on-atom blocks excluded); band test = zero every block at graph distance ≥ d*, largest harmonic shift (X2's rule). "
         "Sanity per molecule: the highest C–H stretch frequency and the number of imaginary modes.", "",
         "| molecule | C | H | max graph distance | decay factor per bond, all d ≥ 1 | same, d = 1…4 only | median norm d = 1 / d = 3 / d = max | band shift zeroing blocks at d ≥ 2 / ≥ 3 / ≥ 4 (cm⁻¹) | top ν (cm⁻¹) | imag |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for r in out["molecules"]:
        med = {p["d"]: p["median"] for p in r["profile"]}
        b = r["band_shift_zeroing_far_blocks_cm"]
        L.append(f"| {r['molecule']} | {r['nC']} | {r['nH']} | {r['max_graph_distance']} | {r['decay_factor_per_bond']:.3f} | **{r['decay_factor_per_bond_d1to4']:.3f}** | {med.get(1, float('nan')):.2e} / {med.get(3, float('nan')):.2e} / {med[r['max_graph_distance']]:.2e} | "
                 f"{b.get('2', float('nan')):.1f} / {b.get('3', float('nan')):.1f} / {b.get('4', float('nan')):.1f} | {r['top_freq_cm']:.0f} | {r['n_imag']} |")
    L += ["", "Per-distance profiles (median block norm; pairs in brackets):", ""]
    for r in out["molecules"]:
        L.append(f"- **{r['molecule']}**: " + ", ".join(f"d={p['d']}: {p['median']:.2e} ({p['pairs']})" for p in r["profile"]))
    L += ["", "Reading: a decay factor per bond that is stable across the series is the mean-field 'range' the correction will be compared against (X9 at benzene: the correction's share "
          "of the Hessian rises with distance). The band test says how far the *DFT* Hessian's own blocks matter at 0.5 cm⁻¹ — the reference for what a Cartesian truncation of any "
          "correction would have to beat. B3LYP/6-31G* only; no correction tensor beyond benzene exists yet.", "", "Constants: " + json.dumps(CONSTANTS)]
    (HERE / "x12_dft_hessian_decay_series.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[:20]).encode("ascii", "replace").decode())


if __name__ == "__main__":
    main()
