"""X1d (2026-09-12) — does plan 05's measurement noise survive the three recovery schemes?

X1b/X1c counted products: CPR 8–18, symmetric direct 7–14, triangular substitution 6–7 at benzene. Coleman &
Moré (1984, §6) warn that substitution "may magnify errors considerably". Here the schemes are run on NOISY
probes of the benzene Δ₂ tensor and the error of the recovered matrix — in elements and in harmonic band
positions — is printed against the direct measurement of every element (plan 05's deck).

Noise model (X2's rule, unchanged): every measured number carries Gaussian noise of standard deviation
σ_E/2 in E_h per q² (the four-point finite-difference pattern at q_s = 1), σ_E = 0.5 and 1.0 µE_h. A probe
entry (A d_k)_i is one such measured number; a directly measured element is one such number too. So the
comparison is fair per measured number; the schemes differ in HOW MANY numbers they measure and in how
noise propagates through the algebra.

Truth: the FULL tensor D2_direct (all 435 off-diagonal elements, including the ones below θ). The schemes
assume the pattern P = {|Δ₂,ij| > θ} ∪ diagonal, so their error contains the pattern truncation as well as
the noise; the row "θ truncation only" isolates the truncation (noise-free probes) for reference.

Schemes: (b) CPR direct read; (c) symmetric direct read, one side; (c') the same, averaging the two sides
where both are readable; (d) triangular substitution (X1c's colouring and ordering); (e) plan 05's deck —
every element of the full matrix measured once, no pattern (K = 448 energies is the measured cost; here it
is the noise reference). N_TRIALS noise draws per case; medians and 95th percentiles printed.
Every number printed comes from the files; constants are listed in CONSTANTS."""
import json
import sys
from datetime import datetime
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from x1b_symmetric_colouring import pattern, readable_col, greedy_proper, greedy_symmetric, symm_valid, cpr_valid  # noqa: E402
from x1c_triangular_substitution import smallest_last_order, lower_pattern, intersection_graph, sequential_colouring, is_proper, recover_by_substitution  # noqa: E402

PLAN05 = HERE.parents[1] / "05_delta-probed-ir-pipeline"
HARTREE_TO_CM = 219474.63
CONSTANTS = {"sigma_E_uEh": [0.5, 1.0], "theta_multiples_of_noise": [1, 2, 5, 10], "element_uncertainty_rule": "delta = sigma_E / 2 per measured number (X2)",
             "n_trials": 200, "seed": 0, "band_threshold_cm": 0.5, "K_measured_plan05": 448}


def freqs_cm(W2):
    w2 = np.linalg.eigvalsh(W2)
    return np.sign(w2) * np.sqrt(np.abs(w2)) * HARTREE_TO_CM


def recover_cpr(P, colour, probes):
    n = P.shape[0]; A = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if P[i, j]:
                A[i, j] = probes[colour[j]][i]
    return A


def recover_symm(P, colour, probes, average=False):
    n = P.shape[0]; A = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if P[i, j]:
                rc = readable_col(P, colour, i, j); rr = readable_col(P, colour, j, i)
                if rc and rr and average:
                    A[i, j] = 0.5 * (probes[colour[j]][i] + probes[colour[i]][j])
                elif rc:
                    A[i, j] = probes[colour[j]][i]
                else:
                    A[i, j] = probes[colour[i]][j]
    return A


def main():
    z = np.load(PLAN05 / "probes/results_dryrun/benzene/stageA_hessians.npz")
    DQ, DE, w = z["D2_direct_Q"], z["D2_direct"], z["omega_au"]; M = len(w)
    s = np.sqrt(np.abs(np.diag(DE) / np.diag(DQ)))
    W2_true = np.diag(w ** 2) + DQ
    f_true = freqs_cm(W2_true)
    rng = np.random.default_rng(CONSTANTS["seed"])
    NT = CONSTANTS["n_trials"]
    out = {"date": f"{datetime.now():%Y-%m-%d %H:%M}", "M": M, "constants": CONSTANTS, "source": "plan 05 probes/results_dryrun/benzene/stageA_hessians.npz"}
    rows = []

    def band_err(DE_rec):
        DQ_rec = DE_rec / np.outer(s, s)
        return float(np.abs(freqs_cm(np.diag(w ** 2) + DQ_rec) - f_true).max())

    def elem_err(DE_rec):
        return float(np.sqrt(np.mean((DE_rec - DE) ** 2)) * 1e6), float(np.abs(DE_rec - DE).max() * 1e6)

    for sig in CONSTANTS["sigma_E_uEh"]:
        delta = sig * 1e-6 / 2.0
        for m in CONSTANTS["theta_multiples_of_noise"]:
            theta = m * delta
            P = pattern(DE, theta); H = P.copy(); np.fill_diagonal(H, False)
            Hcpr = (P.T.astype(int) @ P.astype(int)) > 0; np.fill_diagonal(Hcpr, False)
            c_b = greedy_proper(Hcpr); assert cpr_valid(P, c_b)
            c_c = greedy_symmetric(P); assert symm_valid(P, c_c)
            pos = smallest_last_order(H); Lp = lower_pattern(P, pos); Gu = intersection_graph(Lp)
            cands = [c for c in (sequential_colouring(Gu, list(np.argsort(-Gu.sum(1)))), sequential_colouring(Gu, sorted(range(M), key=lambda v: smallest_last_order(Gu)[v]))) if is_proper(Gu, c)]
            c_d = min(cands, key=lambda c: c.max())
            schemes = {"b_cpr": (c_b, lambda pr: recover_cpr(P, c_b, pr)), "c_symm": (c_c, lambda pr: recover_symm(P, c_c, pr)),
                       "c2_symm_avg": (c_c, lambda pr: recover_symm(P, c_c, pr, average=True)), "d_subst": (c_d, lambda pr: recover_by_substitution(P, pos, c_d, pr))}
            # noise-free (truncation only)
            res = {"sigma_E_uEh": sig, "theta_uEh": theta * 1e6, "pattern_entries": int(P.sum()), "products": {k: int(c.max() + 1) for k, (c, _) in schemes.items()}}
            trunc = {}
            for k, (c, rec) in schemes.items():
                probes = [DE @ (c == q).astype(float) for q in range(c.max() + 1)]
                A = rec(probes); trunc[k] = {"band_max_cm": band_err(A), "elem_rms_uEh": elem_err(A)[0]}
            res["truncation_only_noise_free"] = trunc
            # noisy trials
            stats = {k: {"band": [], "rms": [], "max": []} for k in list(schemes) + ["e_deck_all_elements"]}
            for _ in range(NT):
                for k, (c, rec) in schemes.items():
                    probes = [DE @ (c == q).astype(float) + rng.normal(0.0, delta, M) for q in range(c.max() + 1)]
                    A = rec(probes)
                    stats[k]["band"].append(band_err(A)); r, mx = elem_err(A); stats[k]["rms"].append(r); stats[k]["max"].append(mx)
                N = rng.normal(0.0, delta, (M, M)); N = np.triu(N) + np.triu(N, 1).T      # every element measured once (symmetric)
                A = DE + N
                stats["e_deck_all_elements"]["band"].append(band_err(A)); r, mx = elem_err(A); stats["e_deck_all_elements"]["rms"].append(r); stats["e_deck_all_elements"]["max"].append(mx)
            res["noisy"] = {k: {"band_max_cm_median": float(np.median(v["band"])), "band_max_cm_p95": float(np.percentile(v["band"], 95)),
                                "elem_rms_uEh_median": float(np.median(v["rms"])), "elem_max_uEh_p95": float(np.percentile(v["max"], 95)),
                                "trials_band_gt_thr_pct": float(100 * np.mean(np.array(v["band"]) > CONSTANTS["band_threshold_cm"]))} for k, v in stats.items()}
            rows.append(res)
    out["rows"] = rows
    json.dump(out, open(HERE / "x1d_noise_propagation.json", "w"), indent=1)
    L = [f"# X1d — noise propagation through the recovery schemes on the benzene Δ₂ tensor ({out['date']})", "",
         f"Noise σ_E/2 per measured number (X2's rule), {NT} draws per case; truth = the full tensor; schemes assume the pattern above θ. "
         "Errors: largest harmonic band shift against the true tensor (cm⁻¹; X2's threshold 0.5) and RMS element error (µE_h). "
         "(e) = plan 05's deck, every element measured once (the noise reference; its cost is the measured K = 448).", "",
         "| σ_E | θ (µE_h) | scheme | products | band max shift, noise-free truncation (cm⁻¹) | band max shift, noisy: median / p95 (cm⁻¹) | trials > 0.5 cm⁻¹ | element RMS median (µE_h) | element max p95 (µE_h) |",
         "|---|---|---|---|---|---|---|---|---|"]
    names = {"b_cpr": "(b) CPR direct", "c_symm": "(c) symmetric direct", "c2_symm_avg": "(c′) symmetric, two sides averaged", "d_subst": "(d) triangular substitution", "e_deck_all_elements": "(e) deck: all elements"}
    for r in rows:
        for k in names:
            nz = r["noisy"][k]; tr = r["truncation_only_noise_free"].get(k, {"band_max_cm": 0.0})
            prod = r["products"].get(k, "every element")
            L.append(f"| {r['sigma_E_uEh']} | {r['theta_uEh']:.2f} | {names[k]} | {prod} | {tr['band_max_cm']:.3f} | {nz['band_max_cm_median']:.3f} / {nz['band_max_cm_p95']:.3f} | "
                     f"{nz['trials_band_gt_thr_pct']:.0f} % | {nz['elem_rms_uEh_median']:.3f} | {nz['elem_max_uEh_p95']:.2f} |")
    L += ["", "Reading aid: if (d)'s noisy band shift is close to (e)'s, substitution does not magnify plan 05's noise at benzene and the 6–7-product count is a route "
          "candidate; if (d) is far above (e), the count is not. The truncation column shows what dropping the elements below θ costs regardless of noise.", "",
          "Constants: " + json.dumps(CONSTANTS)]
    (HERE / "x1d_noise_propagation.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L).encode("ascii", "replace").decode())


if __name__ == "__main__":
    main()
