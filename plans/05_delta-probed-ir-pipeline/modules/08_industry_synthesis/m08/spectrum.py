"""The spectral shape on the certificate (TASKS 39, 10 Oct 2026; the user, 9 Oct: 'Kunnen we de spectrale vorm toevoegen aan de betreffende Udacity
module die over de pipeline gaat?'): band positions *and* heights, as astronomers read a spectrum, with its accuracy stated from measured records.

Heights are double-harmonic intensities from the molecule's atomic polar tensor (APT, module 05's `dipole_b3lyp_cphf.npz`, or the FD route's file)
and the cheap rung's own B3LYP Hessian (`hessian_b3lyp.npz`, deck v1, the Hessian the listed positions come from), computed with module 05's
`rungC_intensities.mode_intensities`. The intensities stored inside the APT files are not used: eight of the ten were computed on 2 Oct with the FD
Hessian, two with the analytic one (checked 10 Oct), so they are not one consistent set. IR-inactive modes carry height zero and therefore weigh
nothing in the drawn spectrum. A molecule without an APT gets positions only, and the certificate says so (the rung rule of TASKS 39).

The accuracy statement is read from the records, not typed: module 05's re-read of chain 34 on hold-out (a) with eigenvector-matched pairing (9 Oct)
and the T3 transfer to CCSD(T)/cc-pVTZ on benzene (9 Oct), seed means over three seeds."""
from __future__ import annotations

import importlib.util
import json

import numpy as np

from .catalog import PLAN

M05 = PLAN / "modules" / "05_support_predictor"
CORPUS = M05 / "corpus" / "molecules"
APT_FILES = ("dipole_b3lyp_cphf.npz", "dipole_b3lyp_fd.npz")
HESSIAN = "hessian_b3lyp.npz"
FWHM, GRID = 10.0, (500.0, 3500.0)                     # module 05's read-out: Lorentzian FWHM 10 cm⁻¹ on 500–3500 cm⁻¹
ACTIVE_FRACTION = 0.005                                # 'infrared-active': ≥ 0.5 % of the strongest band (FD noise leaks ~0.1 km/mol into dark modes)
PROXY_RECORDS = [f"modules/05_support_predictor/out/E7_rungC_chain34_eval_matched_2026-10-09_seed{s}.json" for s in range(3)]
CC_RECORDS = [f"modules/05_support_predictor/out/T3_tz_intensity_matched_c34_seed{s}_2026-10-09.json" for s in range(3)]
BENZENE = "A_8448043181"
CC_COLUMN = "network_head_l2"       # the TZ-tier standard: head-tuned with the L2 pull λ = 1 (amendment (A), 7 Oct 2026; m05 `fit_mode`).
                                    # 10 Oct 2026: the first version read 'network_head' (λ = 0) and quoted 0.59 instead of 0.37.


def _ri():
    spec = importlib.util.spec_from_file_location("rungC_intensities", M05 / "m05" / "rungC_intensities.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def shape(mid: str, listed_cm: list[float] | None = None) -> dict:
    """Sticks (position, height) for one corpus molecule, or the reason there are none. `listed_cm` = the certificate's listed B3LYP positions:
    the largest difference to the positions computed here is recorded as a consistency check (same Hessian → ≈ 0)."""
    d = CORPUS / mid
    apt = next((d / f for f in APT_FILES if (d / f).exists()), None)
    if apt is None or not (d / HESSIAN).exists():
        return dict(kind="positions only", reason="no dipole derivatives (APT) computed for this molecule — heights are not shown rather than guessed")
    ri = _ri()
    masses = np.asarray(json.load(open(d / "geometry.json", encoding="utf-8"))["masses_amu"], float)
    freq, inten = ri.mode_intensities(np.load(d / HESSIAN)["H_projected"], masses, np.asarray(np.load(apt)["apt"], float))
    order = np.argsort(freq)
    freq, inten = freq[order], inten[order]
    check = None
    if listed_cm is not None and len(listed_cm) == len(freq):
        check = round(float(np.abs(np.sort(np.asarray(listed_cm, float)) - freq).max()), 2)
    rel = lambda p: str(p.relative_to(PLAN)).replace("\\", "/")   # noqa: E731
    return dict(kind="positions and heights", sticks=[dict(omega_cm=round(float(w), 1), km_mol=round(float(a), 2)) for w, a in zip(freq, inten, strict=True)],
                n_ir_active=int((inten >= ACTIVE_FRACTION * inten.max()).sum()), apt_source=rel(apt), hessian_source=rel(d / HESSIAN),
                broadening=dict(lineshape="Lorentzian", fwhm_cm=FWHM, grid_cm=list(GRID)), max_dev_from_listed_cm=check,
                method="double harmonic: A_k = 974.88 km/mol · |P L_k/√m|² (module 05 m05/rungC_intensities.py)")


def broadened(sticks: list[dict], step: float = 1.0) -> tuple[np.ndarray, np.ndarray]:
    """The drawn spectrum: the sticks with the read-out's Lorentzian (the same function the accuracy numbers were measured with)."""
    grid = np.arange(GRID[0], GRID[1], step)
    w = np.array([s["omega_cm"] for s in sticks]); a = np.array([s["km_mol"] for s in sticks])
    return grid, _ri().broadened(w, a, grid, FWHM)


def _mean(xs: list[float]) -> float:
    return round(float(np.mean(xs)), 3)


def measured_accuracy() -> dict:
    """Seed means from the records. 'cheap' = no correction (the zero rule: the cheap rung's own spectrum against the higher level), 'corrected' =
    the network's correction, which is not served (no family licensed) and is reported as what the next rungs would bring."""
    proxy = [json.load(open(PLAN / p, encoding="utf-8")) for p in PROXY_RECORDS]
    cc = [json.load(open(PLAN / p, encoding="utf-8")) for p in CC_RECORDS]
    keys = ("spectrum_overlap", "spectrum_overlap_zero_rule", "intensity_rel_rms_matched", "intensity_rel_rms_zero_rule_matched")
    per_seed = []
    for r in proxy:
        pm = {i: v for i, v in r["a"]["per_molecule"].items() if v.get("spectrum_overlap") is not None}
        per_seed.append({k: float(np.mean([v[k] for v in pm.values()])) for k in keys} | dict(n=len(pm)))
    head = [r["folds"][BENZENE][CC_COLUMN]["intensity"] for r in cc]
    zero = [r["folds"][BENZENE]["zero_rule"]["intensity"] for r in cc]
    return dict(
        proxy=dict(level="DFT proxy (ωB97X as the higher level), 10 unseen molecules of hold-out (a), chain 34 (carried model), seed mean of 3",
                   n_molecules=per_seed[0]["n"], sources=PROXY_RECORDS,
                   cheap=dict(spectrum_overlap=_mean([s["spectrum_overlap_zero_rule"] for s in per_seed]),
                              intensity_error=_mean([s["intensity_rel_rms_zero_rule_matched"] for s in per_seed])),
                   corrected=dict(spectrum_overlap=_mean([s["spectrum_overlap"] for s in per_seed]),
                                  intensity_error=_mean([s["intensity_rel_rms_matched"] for s in per_seed]))),
        cc=dict(level="CCSD(T)/cc-pVTZ with its own CC APT, benzene (leave-one-anchor-out, head-tuned with λ = 1), seed mean of 3",
                sources=CC_RECORDS, column=CC_COLUMN,
                cheap=dict(spectrum_overlap=_mean([z["spectrum_overlap"] for z in zero]), intensity_error=_mean([z["intensity_rel_rms_matched"] for z in zero])),
                corrected=dict(spectrum_overlap=_mean([h["spectrum_overlap"] for h in head]), intensity_error=_mean([h["intensity_rel_rms_matched"] for h in head])),
                note="benzene's symmetry fixes its band heights, so the intensity error cannot separate corrected from uncorrected here; a "
                     "low-symmetry molecule with a CC APT is the open test"),
        definitions=dict(spectrum_overlap="cosine similarity of the two Lorentzian-broadened spectra (FWHM 10 cm⁻¹, 500–3500 cm⁻¹); 1 = identical shape",
                         intensity_error="intensity-weighted rms of the relative height error per band, bands paired by the shape of the motion "
                                         "(eigenvector overlap); 0 = identical heights"),
        open=["the APT itself is computed at the cheap level; its CC-minus-B3LYP difference (≈ 20 % on benzene) is not corrected by any rung yet"])
