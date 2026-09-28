"""Hot-band desk test on benzene (pre-registration 2026-09-28, Hot_Band_Lines §2): the sequence-band offsets of ν₁₁ from the anharmonic
constants of the two-route QFF record, against Hollenstein, Piccirillo, Quack & Snels 1990 (Mol. Phys. 71, 759; item 89).

Convention (Mills; `src/dpir/qff.py` vpt2): sequence band ν_a + ν_b − ν_b sits at ν_a + χ_ab, the overtone sequence 2ν_a − ν_a at ν_a + 2 χ_aa.
Mode mapping of the 22 Sep benchmark: 0/1 = ν₁₆ (e2u), 2/3 = ν₆ (e2g), 4 = ν₁₁ (a2u), 5 = ν₄ (b2g).

Usage: python probes/hot_band_desk_benzene.py [--record probes/results_vpt2/qff_benzene_pyscf_analytic_d010_2026-09-21.npz]
                                              [--out probes/results_vpt2/hot_bands_benzene_2026-09-28]
"""
import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
from dpir.provenance import provenance  # noqa: E402

HC_OVER_K = 1.438776877  # cm·K (second radiation constant)
MEASURED = {  # Hollenstein et al. 1990, abstract: fundamental 673.97465 cm⁻¹; offsets in cm⁻¹ (effective constants to 1e-4)
    "nu11+nu6-nu6": -0.466, "nu11+nu16-nu16": -1.099, "2nu11-nu11": +0.127}
MODES = {"nu16": (0, 1), "nu6": (2, 3), "nu11": (4,), "nu4": (5,)}
A = 4  # ν₁₁


def offsets(chi: np.ndarray) -> dict:
    """The three measured offsets from a χ matrix: component means for the degenerate lower levels, with the spread as a check."""
    out = {}
    for key, comps in (("nu11+nu6-nu6", MODES["nu6"]), ("nu11+nu16-nu16", MODES["nu16"])):
        vals = [float(chi[A, b]) for b in comps]
        out[key] = dict(offset=float(np.mean(vals)), component_spread=float(max(vals) - min(vals)))
    out["2nu11-nu11"] = dict(offset=float(2 * chi[A, A]), component_spread=0.0)
    return out


def judge(pred: dict, raw: dict) -> dict:
    """P1 sign (3/3), P2 size (factor 2 or 0.3 cm⁻¹, whichever is wider), P3 two-route noise (|χ_sym − χ_raw| ≤ 0.1)."""
    rows, p1, p2, p3 = [], 0, 0, 0
    for key, meas in MEASURED.items():
        p = pred[key]["offset"]; r = raw[key]["offset"]
        sign_ok = (p > 0) == (meas > 0)
        tol = max(0.3, abs(meas))                      # within a factor 2 ⇔ |p − meas| ≤ |meas|; floor 0.3 cm⁻¹
        size_ok = abs(p - meas) <= tol
        noise_ok = abs(p - r) <= 0.1
        p1 += sign_ok; p2 += size_ok; p3 += noise_ok
        rows.append(dict(band=key, measured=meas, predicted_sym=round(p, 4), predicted_raw=round(r, 4), component_spread=round(pred[key]["component_spread"], 4),
                         sign_ok=bool(sign_ok), size_ok=bool(size_ok), noise_ok=bool(noise_ok)))
    verdict = dict(P1_sign=("pass" if p1 == 3 else "fail"), P2_size=("pass" if p2 == 3 else "reported with the miss named" if p2 == 2 else "fail"),
                   P3_noise=("pass" if p3 == 3 else "suspended: two-route noise"))
    return dict(rows=rows, counts=dict(P1=p1, P2=p2, P3=p3), verdict=verdict)


def sequence_table(chi: np.ndarray, nu: np.ndarray, omega: np.ndarray, T: float = 300.0) -> list[dict]:
    """The reported output for ν₁₁: every low-lying lower level (ω_b ≤ 1,000 cm⁻¹), its offset and Boltzmann weight."""
    rows = []
    seen = set()
    for name, comps in MODES.items():
        if name == "nu11":
            continue
        b0 = comps[0]
        if omega[b0] > 1000 or name in seen:
            continue
        seen.add(name)
        vals = [float(chi[A, b]) for b in comps]
        rows.append(dict(lower_level=name, omega_b=round(float(omega[b0]), 1), degeneracy=len(comps), offset=round(float(np.mean(vals)), 4),
                         position=round(float(nu[A] + np.mean(vals)), 3), boltzmann_300K=round(len(comps) * math.exp(-HC_OVER_K * float(omega[b0]) / T), 4)))
    rows.append(dict(lower_level="nu11 (overtone sequence)", omega_b=round(float(omega[A]), 1), degeneracy=1, offset=round(float(2 * chi[A, A]), 4),
                     position=round(float(nu[A] + 2 * chi[A, A]), 3), boltzmann_300K=round(math.exp(-HC_OVER_K * float(omega[A]) / T), 4)))
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--record", default=str(HERE / "results_vpt2" / "qff_benzene_pyscf_analytic_d010_2026-09-21.npz"))
    ap.add_argument("--out", default=str(HERE / "results_vpt2" / "hot_bands_benzene_2026-09-28"))
    a = ap.parse_args(argv)
    z = np.load(a.record)
    chi_sym, chi_raw, nu, omega = z["chi_sym"], z["chi_raw"], z["nu_sym"], z["omega_cm"]
    assert 690 < omega[A] < 700 and 405 < nu[0] < 410, "the mode mapping of the 22 Sep benchmark does not hold for this record"
    pred, raw = offsets(chi_sym), offsets(chi_raw)
    J = judge(pred, raw)
    table = sequence_table(chi_sym, nu, omega)
    rec = dict(date=time.strftime("%Y-%m-%d %H:%M"), record=str(Path(a.record).name), fundamental_nu11=dict(dft=round(float(nu[A]), 3), measured=673.97465),
               measured_source="Hollenstein, Piccirillo, Quack & Snels, Mol. Phys. 71, 759 (1990), abstract; item 89", judged=J, sequence_table=table,
               label="DFT-anharmonic offsets (B3LYP/6-31G*, two-route QFF) on the DFT fundamental; the corrected harmonic part is not yet applied to benzene",
               provenance=provenance())
    json.dump(rec, open(a.out + ".json", "w", encoding="utf-8"), indent=1)
    lines = [f"# Hot-band desk test, benzene ν₁₁ — {rec['date']} (pre-registration 2026-09-28 §2)", "",
             f"Record `{rec['record']}`; DFT ν₁₁ {rec['fundamental_nu11']['dft']} against 673.97465 cm⁻¹ measured. {rec['label']}.", "",
             "| band | measured offset | predicted (χ_sym) | predicted (χ_raw) | component spread | sign | size | noise |", "|---|---|---|---|---|---|---|---|"]
    for r in J["rows"]:
        lines.append(f"| {r['band']} | {r['measured']:+.3f} | {r['predicted_sym']:+.3f} | {r['predicted_raw']:+.3f} | {r['component_spread']:.3f} | "
                     f"{'ok' if r['sign_ok'] else 'WRONG'} | {'ok' if r['size_ok'] else 'miss'} | {'ok' if r['noise_ok'] else 'noisy'} |")
    lines += ["", f"**Verdict:** P1 sign {J['verdict']['P1_sign']} ({J['counts']['P1']}/3); P2 size {J['verdict']['P2_size']} ({J['counts']['P2']}/3); "
              f"P3 noise {J['verdict']['P3_noise']} ({J['counts']['P3']}/3).", "",
              "## Reported output: sequence bands of ν₁₁ (lower levels ω_b ≤ 1,000 cm⁻¹), 300 K", "",
              "| lower level | ω_b | g | offset χ | position | Boltzmann weight |", "|---|---|---|---|---|---|"]
    for r in table:
        lines.append(f"| {r['lower_level']} | {r['omega_b']} | {r['degeneracy']} | {r['offset']:+.3f} | {r['position']:.3f} | {r['boltzmann_300K']:.4f} |")
    open(a.out + ".md", "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
