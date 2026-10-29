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
import inspect
import json
from pathlib import Path

import numpy as np

from .catalog import PLAN

M05 = PLAN / "modules" / "05_support_predictor"
CORPUS = M05 / "corpus" / "molecules"
APT_FILES = ("dipole_b3lyp_cphf.npz", "dipole_b3lyp_fd.npz")
HESSIAN = "hessian_b3lyp.npz"
FWHM, GRID = 10.0, (500.0, 3500.0)                     # module 05's read-out: Lorentzian FWHM 10 cm⁻¹ on 500–3500 cm⁻¹
ACTIVE_FRACTION = 0.005                                # 'infrared-active': ≥ 0.5 % of the strongest band (FD noise leaks ~0.1 km/mol into dark modes)
ANCHORS_STATUS = M05 / "out" / "ANCHORS_STATUS.json"
TEST_SEEDS = 3                        # the carried model's three seeds: the test band needs all of them
CC_APT = "apt_ccsd_t.npz"            # the CC APT an anchor run stores beside its Hessian (cc_dipole_capture, 3 Oct 2026)
                                    # 10 Oct 2026: the first version read 'network_head' (λ = 0) and quoted 0.59 instead of 0.37.


def _ri():
    spec = importlib.util.spec_from_file_location("rungC_intensities", M05 / "m05" / "rungC_intensities.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _rel(p: Path) -> str:
    """A source path relative to the plan; a pipeline result outside the plan keeps its absolute path."""
    p = Path(p).resolve()
    return str(p.relative_to(PLAN) if p.is_relative_to(PLAN) else p).replace("\\", "/")


def _geometry(mid: str) -> dict:
    return json.load(open(CORPUS / mid / "geometry.json", encoding="utf-8"))


def series(hessian: Path, masses: np.ndarray, apt: Path | None, H: np.ndarray | None = None) -> dict:
    """One spectrum from a projected Cartesian Hessian (the file, or `H` in memory with the file as its named source) and, when given, an APT
    file: sticks sorted by position with heights in km/mol, or positions only (km_mol None) without an APT. The sources travel with it."""
    ri = _ri()
    H = np.load(hessian)["H_projected"] if H is None else H
    P = np.asarray(np.load(apt)["apt"], float) if apt is not None else np.zeros((3, H.shape[0]))
    freq, inten = ri.mode_intensities(H, masses, P)
    order = np.argsort(freq)
    freq, inten = freq[order], inten[order]
    out = dict(hessian_source=_rel(hessian), broadening=dict(lineshape="Lorentzian", fwhm_cm=FWHM, grid_cm=list(GRID)),
               method="double harmonic: A_k = 974.88 km/mol · |P L_k/√m|² (module 05 m05/rungC_intensities.py)")
    if apt is None:
        return dict(out, kind="positions only", sticks=[dict(omega_cm=round(float(w), 1), km_mol=None) for w in freq], apt_source=None, n_ir_active=None)
    return dict(out, kind="positions and heights", apt_source=_rel(apt), n_ir_active=int((inten >= ACTIVE_FRACTION * inten.max()).sum()),
                sticks=[dict(omega_cm=round(float(w), 1), km_mol=round(float(a), 2)) for w, a in zip(freq, inten, strict=True)])


def cheap_apt(d: Path) -> Path | None:
    """The molecule's B3LYP APT file, or None: the first of APT_FILES that exists and has not failed its own checks (a file written with
    passed=False — the labels route keeps a failed APT on disk since 11 Oct 2026 — is not drawn; a file without the field counts as passed)."""
    for f in APT_FILES:
        p = d / f
        if p.exists():
            with np.load(p) as z:
                if "passed" not in z.files or bool(z["passed"]):
                    return p
    return None


def _vib_min_cm() -> float:
    """The vibrational threshold of `rungC_intensities.mode_intensities` (its default), so the listed modes are cut where the spectrum is."""
    return float(inspect.signature(_ri().mode_intensities).parameters["vib_min_cm"].default)


def shape(mid: str, listed_cm: list[float] | None = None) -> dict:
    """The cheap rung's sticks (position, height) for one corpus molecule, or the reason there are none. `listed_cm` = the listed B3LYP positions:
    the largest difference to the positions computed here is recorded as a consistency check (same Hessian → ≈ 0)."""
    d = CORPUS / mid
    apt = cheap_apt(d)
    if apt is None or not (d / HESSIAN).exists():
        return dict(kind="positions only", reason="no dipole derivatives (APT) computed for this molecule — heights are not shown rather than guessed")
    s = series(d / HESSIAN, np.asarray(_geometry(mid)["masses_amu"], float), apt)
    freq = np.array([x["omega_cm"] for x in s["sticks"]])
    check = None
    listed = None if listed_cm is None else np.sort(np.asarray(listed_cm, float))
    if listed is not None:
        listed = listed[np.abs(listed) > _vib_min_cm()]
    if listed is not None and len(listed) == len(freq):
        check = round(float(np.abs(listed - freq).max()), 2)
    return dict(s, max_dev_from_listed_cm=check, vib_min_cm=_vib_min_cm())


def carried_anchor(mid: str) -> dict | None:
    """The carried entry of module 05's anchor registry for this molecule (one at most), or None."""
    rows = json.load(open(ANCHORS_STATUS, encoding="utf-8"))["anchors"]
    hits = [e for e in rows if e["mol_id"] == mid and e["status"] == "carried"]
    return hits[0] if hits else None


def _cc_apt_at(anchor_hessian: Path, mid: str, tol: float = 1e-6) -> Path | None:
    """The anchor run's own CC APT (`apt_ccsd_t.npz` beside its Hessian), only when it was computed at the corpus geometry."""
    p = anchor_hessian.parent / CC_APT
    if not p.exists():
        return None
    d = float(np.abs(np.asarray(np.load(p)["coords_bohr"], float) - np.asarray(_geometry(mid)["coords_bohr"], float)).max())
    return p if d <= tol else None


def anchor_series(mid: str) -> dict | None:
    """The anchor's spectrum (TASKS 45): positions and mode shapes from the carried anchor Hessian; heights from the anchor's own CC APT where
    one exists, else from the B3LYP APT (labelled), else positions only. None for a molecule without a carried anchor."""
    e = carried_anchor(mid)
    if e is None:
        return None
    h = PLAN / e["path"]
    cc = _cc_apt_at(h, mid)
    b3 = cheap_apt(CORPUS / mid)
    apt, apt_level = (cc, "CCSD(T) (the anchor's own)") if cc is not None else ((b3, "B3LYP (cheap level)") if b3 is not None else (None, None))
    s = series(h, np.asarray(_geometry(mid)["masses_amu"], float), apt)
    return dict(s, level=e["level"], tier=e.get("tier"), apt_level=apt_level, registry_sha16=e.get("sha16"))


def _overlap(a: list[dict], b: list[dict]) -> float:
    ri = _ri()
    grid = np.arange(GRID[0], GRID[1], 1.0)
    cur = lambda s: ri.broadened(np.array([x["omega_cm"] for x in s]), np.array([x["km_mol"] for x in s]), grid, FWHM)   # noqa: E731
    return round(float(ri.cosine(cur(a), cur(b))), 3)


def test_prediction(mid: str, anchor: dict) -> dict | None:
    """The network's leave-one-anchor-out prediction for an anchor (TASKS 45): per seed, the fold's low level + its predicted ΔH, with the
    anchor's APT. Labelled a test, never a served prediction. None unless all TEST_SEEDS fold files exist (a run in progress never shows a
    partial band) and the anchor has heights."""
    files = sorted((M05 / "out").glob(f"T3_tz_folds_c34_seed*_fold_{mid}.npz"))
    if len(files) != TEST_SEEDS or anchor.get("apt_source") is None:
        return None
    masses = np.asarray(_geometry(mid)["masses_amu"], float)
    seeds = []
    for f in files:
        z = np.load(f)
        s = series(f, masses, PLAN / anchor["apt_source"], H=z["H_low"] + z["dH_pred"])
        seeds.append(dict(file=_rel(f), mode=str(z["mode"]), low_level=str(z["low_level"]), sticks=s["sticks"],
                          spectrum_overlap=_overlap(s["sticks"], anchor["sticks"])))
    ov = [s["spectrum_overlap"] for s in seeds]
    return dict(label="test of the network, not a served prediction: the anchor was left out of the fine-tune (T3, chain 34's models — "
                      "v1.1, superseded, a fixed-step fine-tune — "
                "head-tuned with λ = 1), so this is how the network does on a molecule it did not see at this level",
                seeds=seeds, spectrum_overlap_mean=round(float(np.mean(ov)), 3), spectrum_overlap_range=[min(ov), max(ov)])


def cheap_hessian(mid: str) -> Path:
    """The cheap Hessian of every coupled-cluster comparison: the analytic B3LYP where it exists, else the deck's finite differences."""
    a = CORPUS / mid / "hessian_b3lyp_analytic.npz"
    return a if a.exists() else CORPUS / mid / HESSIAN


def comparison(mid: str, anchor: dict) -> dict:
    """The cheap Hessian with the anchor's own APT, so the two spectra differ only by the Hessian: its sticks, the spectrum overlap with the
    anchor (only with heights) and the rms of the sorted frequencies."""
    apt = PLAN / anchor["apt_source"] if anchor["apt_source"] else None
    c = series(cheap_hessian(mid), np.asarray(_geometry(mid)["masses_amu"], float), apt)
    fa = np.array([x["omega_cm"] for x in anchor["sticks"]]); fc = np.array([x["omega_cm"] for x in c["sticks"]])
    rms = round(float(np.sqrt(np.mean((fa - fc) ** 2))), 1) if len(fa) == len(fc) else None
    overlap = _overlap(c["sticks"], anchor["sticks"]) if apt is not None else None
    return dict(cheap=c, spectrum_overlap=overlap, freq_rms_cm=rms, note="the cheap Hessian with the anchor's dipole derivatives: the curves differ only by the Hessian")


def broadened(sticks: list[dict], step: float = 1.0) -> tuple[np.ndarray, np.ndarray]:
    """The drawn spectrum: the sticks with the read-out's Lorentzian (the same function the accuracy numbers were measured with)."""
    grid = np.arange(GRID[0], GRID[1], step)
    w = np.array([s["omega_cm"] for s in sticks]); a = np.array([s["km_mol"] for s in sticks])
    return grid, _ri().broadened(w, a, grid, FWHM)


def _mean(xs: list[float]) -> float:
    return round(float(np.mean(xs)), 3)


SHAPE_KEYS = ("spectrum_overlap", "spectrum_overlap_zero_rule", "intensity_rel_rms_matched", "intensity_rel_rms_zero_rule_matched")


def shape_accuracy(records: list[dict], hold: str = "a") -> dict:
    """Seed means over one hold-out's molecules with an APT, from `rungC_eval_saved.py` records: 'cheap' = no correction (the zero rule:
    the cheap rung's own spectrum against the higher level), 'corrected' = the network's correction."""
    per_seed = []
    for r in records:
        pm = {i: v for i, v in r[hold]["per_molecule"].items() if v.get("spectrum_overlap") is not None}
        per_seed.append({k: float(np.mean([v[k] for v in pm.values()])) for k in SHAPE_KEYS} | dict(n=len(pm)))
    return dict(n_molecules=per_seed[0]["n"],
                cheap=dict(spectrum_overlap=_mean([s["spectrum_overlap_zero_rule"] for s in per_seed]),
                           intensity_error=_mean([s["intensity_rel_rms_zero_rule_matched"] for s in per_seed])),
                corrected=dict(spectrum_overlap=_mean([s["spectrum_overlap"] for s in per_seed]),
                               intensity_error=_mean([s["intensity_rel_rms_matched"] for s in per_seed])))

