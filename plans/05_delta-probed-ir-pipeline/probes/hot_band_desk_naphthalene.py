"""Hot-band desk test on naphthalene (PreRegistration_2026-09-28_Hot_Band_Lines.md §3 and its amendment of 4 Nov 2026; TASKS 180): the
sequence-band offsets of ν₄₆ from the anharmonic constants of S2's naphthalene force field, against Pirali et al. 2009.

Modes are mapped by D2h symmetry in Pirali's convention (x the molecular normal, y the long in-plane axis, z the short one): ν₄₈ the lowest
b3u, ν₄₆ the third b3u, ν₁₃ the lowest au, ν₁₆ the lowest b1g. χ from `dpir.qff.vpt2` with the report's deperturbation, on the symmetry-
averaged quartics (the report's χ, checked) and on each finite-difference route of the quartics (P3).

    python probes/hot_band_desk_naphthalene.py [--setting probes/results_m1/s2_anharmonic_2026-10-18/s2/A_01f3186607/G] --out <stem>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
from s2_label_check import molecule_inputs  # noqa: E402

from dpir.qff import MASS, vpt2  # noqa: E402  after the src path

SETTING = HERE / "results_m1" / "s2_anharmonic_2026-10-18" / "s2" / "A_01f3186607" / "G"
FERMI_WINDOW, FERMI_MIN_K = 200.0, 0.0      # the report's (`python -m dpir.qff` defaults)
CHAR_MIN = 0.99     # the four mapped modes
SIGN_MIN = 0.9      # every mode: its label is read from the signs
PERM_TOL_BOHR = 0.05
# D2h characters under (i, σ(xy), σ(xz), σ(yz)); x = normal, y = long axis, z = short axis (Pirali's band types)
IRREPS = {(1, 1, 1, 1): "ag", (1, 1, -1, -1): "b1g", (1, -1, 1, -1): "b2g", (1, -1, -1, 1): "b3g",
          (-1, -1, -1, -1): "au", (-1, -1, 1, 1): "b1u", (-1, 1, -1, 1): "b2u", (-1, 1, 1, -1): "b3u"}
MEASURED = {"16": -2.6, "13": 0.6, "48": -0.3}    # Pirali 2009, offsets of ν₄₆'s sequence bands (amendment of 4 Nov)
P2_FACTOR, P2_FLOOR, P3_LIMIT = 2.0, 0.3, 0.1


def pirali_frame(symbols: list[str], geom: np.ndarray) -> np.ndarray:
    """Columns x (normal), y (long in-plane axis), z (short in-plane axis) of the principal frame through the centre of mass."""
    m = np.array([MASS[s] for s in symbols])
    x = geom - (m[:, None] * geom).sum(0) / m.sum()
    inertia = sum(mi * (np.dot(r, r) * np.eye(3) - np.outer(r, r)) for mi, r in zip(m, x, strict=True))
    _, axes = np.linalg.eigh(inertia)            # ascending moments: long axis, short axis, normal
    return np.column_stack([axes[:, 2], axes[:, 0], axes[:, 1]])


def characters(symbols: list[str], geom: np.ndarray, q: np.ndarray) -> np.ndarray:
    """(n_modes, 4): each mass-weighted mode's overlap with itself after i, σ(xy), σ(xz), σ(yz)."""
    m = np.array([MASS[s] for s in symbols])
    frame = pirali_frame(symbols, geom)
    r = (geom - (m[:, None] * geom).sum(0) / m.sum()) @ frame
    n = len(symbols)
    qf = np.einsum("kxi,xa->kai", q.reshape(n, 3, -1), frame)
    ops = [np.diag(d) for d in ((-1, -1, -1), (1, 1, -1), (1, -1, 1), (-1, 1, 1))]
    out = []
    for R in ops:
        image = r @ R.T
        perm = [int(np.argmin(np.linalg.norm(r - p, axis=1))) for p in image]
        if any(np.linalg.norm(r[perm[k]] - image[k]) > PERM_TOL_BOHR or symbols[perm[k]] != symbols[k] for k in range(n)):
            raise SystemExit("the geometry is not D2h within the tolerance")
        moved = np.zeros_like(qf)
        for k in range(n):
            moved[perm[k]] = np.einsum("ab,bi->ai", R, qf[k])
        out.append(np.einsum("kai,kai->i", qf, moved))
    return np.array(out).T


def classify(chars: np.ndarray) -> list[str]:
    """The D2h label of every mode from the signs of its characters; a character below SIGN_MIN in size stops the read (near-degenerate
    pairs of different symmetry mix by ~1 % on this geometry, which is D2h to 6.5e-4 bohr)."""
    labels = []
    for i, c in enumerate(chars):
        if np.abs(c).min() < SIGN_MIN:
            raise SystemExit(f"mode {i}: characters {np.round(c, 3)} are not ±1")
        labels.append(IRREPS[tuple(int(np.sign(v)) for v in c)])
    return labels


def mapping(labels: list[str]) -> dict[str, int]:
    """Our mode index of ν₄₆, ν₄₈, ν₁₃, ν₁₆ by the amendment's rule (modes in ascending ω)."""
    of = lambda lab: [i for i, s in enumerate(labels) if s == lab]  # noqa: E731
    return {"46": of("b3u")[2], "48": of("b3u")[0], "13": of("au")[0], "16": of("b1g")[0]}


def passes(pred: dict[str, float], noise: dict[str, float]) -> dict:
    """§2's P1 (sign), P2 (factor 2 or 0.3 cm⁻¹), the amendment's P3 (route a vs b ≤ 0.1 cm⁻¹), per offset."""
    rows = {}
    for b, meas in MEASURED.items():
        p = pred[b]
        size_ok = abs(p - meas) <= P2_FLOOR or (np.sign(p) == np.sign(meas) and abs(meas) / P2_FACTOR <= abs(p) <= abs(meas) * P2_FACTOR)
        rows[b] = {"measured": meas, "predicted": p, "P1_sign": bool(np.sign(p) == np.sign(meas)), "P2_size": bool(size_ok),
                   "P3_route_gap": noise[b], "P3_ok": bool(noise[b] <= P3_LIMIT)}
    return rows


def read(setting: Path) -> dict:
    """The offsets and pass lines; the report's χ reproduced first."""
    arrays, B, zeta = molecule_inputs(str(setting))
    with open(setting / "ref.json", encoding="utf-8") as fh:
        ref = json.load(fh)
    from s1_anharmonic_level import harmonic_modes
    omega, q = harmonic_modes(str(setting / "ref.json"))
    w = arrays["omega_cm"]
    if not np.allclose(omega, w, atol=1e-6):
        raise SystemExit("the reference's modes are not the report's")
    labels = classify(characters(ref["molecule"]["symbols"], np.array(ref["molecule"]["geometry"], float).reshape(-1, 3), q))
    idx = mapping(labels)
    chars = characters(ref["molecule"]["symbols"], np.array(ref["molecule"]["geometry"], float).reshape(-1, 3), q)
    for b, i in idx.items():
        if np.abs(chars[i]).min() < CHAR_MIN:
            raise SystemExit(f"ν{b} (mode {i}) has characters {np.round(chars[i], 3)}: not clean enough to map")
    p3 = arrays["phi_ijk"]
    chi = {}
    for name, key in (("sym", "phi_iijj_sym"), ("a", "phi_iijj_route_a"), ("b", "phi_iijj_route_b")):
        p4 = np.array(arrays[key], float)
        if name != "sym":
            np.fill_diagonal(p4, np.diag(arrays["phi_iijj"]))
        chi[name] = vpt2(w, p3, p4, B, zeta, FERMI_WINDOW, FERMI_MIN_K)[1]
    if np.abs(chi["sym"] - arrays["chi_sym"]).max() > 1e-9:
        raise SystemExit("this χ does not reproduce the report's chi_sym")
    a46 = idx["46"]
    pred = {b: float(chi["sym"][a46, idx[b]]) for b in MEASURED}
    noise = {b: float(abs(chi["a"][a46, idx[b]] - chi["b"][a46, idx[b]])) for b in MEASURED}
    rows = passes(pred, noise)
    n1 = sum(r["P1_sign"] for r in rows.values())
    n2 = sum(r["P2_size"] for r in rows.values())
    return {"setting": str(setting), "mapping": {k: {"mode": v, "omega": float(w[v]), "label": labels[v]} for k, v in idx.items()},
            "labels": labels, "rows": rows, "P1": f"{n1}/3", "P2": f"{n2}/3", "P3": all(r["P3_ok"] for r in rows.values()),
            "omega_46": float(w[a46]), "nu_46": float(arrays["nu_sym"][a46])}


def main(argv: list[str] | None = None) -> int:
    """Command line: the json and a short md beside it."""
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--setting", default=str(SETTING))
    ap.add_argument("--out", required=True, help="path stem; .json and .md are written")
    a = ap.parse_args(argv)
    res = read(Path(a.setting))
    lines = [f"# Naphthalene hot-band desk test (amendment of 4 Nov 2026), ν₄₆ = mode {res['mapping']['46']['mode']} "
             f"(ω {res['omega_46']:.1f}, ν {res['nu_46']:.1f})", "", "| band | b mode (ω, label) | measured | ours χ | P1 | P2 | route gap |",
             "|---|---|---|---|---|---|---|"]
    for b, r in res["rows"].items():
        m = res["mapping"][b]
        lines.append(f"| ν₄₆+ν{b}−ν{b} | {m['mode']} ({m['omega']:.1f}, {m['label']}) | {r['measured']:+.1f} | {r['predicted']:+.3f} | "
                     f"{'pass' if r['P1_sign'] else 'fail'} | {'pass' if r['P2_size'] else 'fail'} | {r['P3_route_gap']:.3f} |")
    lines += ["", f"P1 {res['P1']}, P2 {res['P2']}, P3 {'pass' if res['P3'] else 'fail'}"]
    for suffix, text in ((".json", json.dumps(res, indent=1)), (".md", "\n".join(lines) + "\n")):
        path = Path(a.out + suffix)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(text, encoding="utf-8")
        tmp.replace(path)
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
