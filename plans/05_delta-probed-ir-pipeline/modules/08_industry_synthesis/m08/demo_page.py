"""The demo page of the pipeline (TASKS 146, decision 64: shown at the supervisor meeting as it stands): one self-contained HTML page built
from the pipeline's result folders alone. Per molecule the network's spectrum beside the B3LYP spectrum it corrects and, where the corpus
holds it, the ωB97X truth; the certificate's families, licence and laptop time; the network's measured error on its hold-outs. Every
number is read from a record or computed from a result folder's arrays; the page types none in.

    python -m m08.demo_page [--out modules/08_industry_synthesis/out/pipeline_demo.html]
"""
from __future__ import annotations

import argparse
import html
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from . import live_certificate as LC
from . import pipeline as P
from .spectrum import broadened

# isort: split
# module 05's code, on the path through m08.pipeline
from rungC_intensities import mode_intensities

RESULTS = P.PLAN / "probes" / "results_m1"
OUT = P.PLAN / "modules" / "08_industry_synthesis" / "out" / "pipeline_demo.html"
FAMILY_ORDER = ("CH-stretch", "ring-ip", "CH-oop", "other")
CURVES = (("truth", "ωB97X truth"), ("network", "network (corrected)"), ("b3lyp", "B3LYP (uncorrected)"))
SVG_W, SVG_H, PAD_L, PAD_R, PAD_T, PAD_B = 720, 230, 14, 14, 12, 34
X_HI, X_LO, X_TICK = 3500.0, 500.0, 500.0      # wavenumber decreasing to the right, the infrared convention
PLOT_STEP_CM = 2.0                              # the drawn curve's step; the read-outs use module 05's 1 cm⁻¹ grid


@dataclass(frozen=True)
class DemoMolecule:
    """One demo run: its result folder and what the page says about where the molecule comes from."""
    folder: Path
    origin: str


DEMO = (
    DemoMolecule(RESULTS / "pipeline_demo_v04_2026-10-30" / "benzene", "from its SMILES; the corpus holds its ωB97X truth"),
    DemoMolecule(RESULTS / "pipeline_demo_v04_2026-10-30" / "phenanthrene", "from its SMILES; the corpus holds its ωB97X truth"),
    DemoMolecule(RESULTS / "pipeline_demo_v04_2026-10-30" / "candidate06",
                 "drawn from module 06's generator (seed 0): the first valid fused-aromatic molecule that is not in the corpus"),
)


@dataclass(frozen=True)
class Panel:
    """What the page shows of one molecule: its records, its drawn curves on one grid and its truth comparison, if any."""
    demo: DemoMolecule
    record: dict
    certificate: dict
    vs_corpus: dict | None
    grid: np.ndarray
    curves: dict[str, np.ndarray]


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sticks(H: np.ndarray, masses: np.ndarray, apt: np.ndarray) -> list[dict]:
    w, a = mode_intensities(H, masses, apt)
    return [{"omega_cm": float(x), "km_mol": float(y)} for x, y in zip(w, a, strict=True)]


def load_panel(demo: DemoMolecule) -> Panel:
    """A result folder's records and curves: the network's from its recorded sticks, the B3LYP and truth spectra from the Hessians with the
    folder's B3LYP APT (the pairing `probes/pipeline_vs_corpus.py` measures with)."""
    r = LC.load_result(demo.folder)
    vs_file = demo.folder / "vs_corpus.json"
    vs = _json(vs_file) if vs_file.exists() else None
    sticks = {"network": r.record["spectra"]["network"]["sticks"], "b3lyp": _sticks(r.H_low, r.masses, r.apt)}
    if vs is not None:
        with np.load(Path(vs["corpus"]) / P.TRUTH_HESSIAN) as z:
            sticks["truth"] = _sticks(z["H_projected"], r.masses, r.apt)
    curves = {k: broadened(s, step=PLOT_STEP_CM) for k, s in sticks.items()}
    grid = next(iter(curves.values()))[0]
    return Panel(demo, r.record, _json(demo.folder / "certificate.json"), vs, grid, {k: c[1] for k, c in curves.items()})


def _x(cm: float) -> float:
    return PAD_L + (X_HI - cm) / (X_HI - X_LO) * (SVG_W - PAD_L - PAD_R)


def _y(rel: float) -> float:
    return SVG_H - PAD_B - rel * (SVG_H - PAD_T - PAD_B)


def svg_spectrum(grid: np.ndarray, curves: dict[str, np.ndarray], label: str) -> str:
    """The curves on one scale: every curve divided by the panel's largest value, wavenumber decreasing to the right."""
    top = max(float(c.max()) for c in curves.values())
    if top <= 0.0:
        raise ValueError(f"{label}: every curve is zero")
    paths = []
    for key, _ in CURVES:
        if key in curves:
            pts = " ".join(f"{_x(g):.1f},{_y(v / top):.1f}" for g, v in zip(grid, curves[key], strict=True))
            paths.append(f'<polyline class="c-{key}" points="{pts}"/>')
    ticks = []
    for cm in np.arange(X_LO, X_HI + 1.0, X_TICK):
        x = _x(float(cm))
        ticks.append(f'<line class="tick" x1="{x:.1f}" x2="{x:.1f}" y1="{PAD_T}" y2="{SVG_H - PAD_B}"/>'
                     f'<text class="tl" x="{x:.1f}" y="{SVG_H - PAD_B + 16}">{int(cm)}</text>')
    axis = f'<text class="tl" x="{SVG_W / 2:.0f}" y="{SVG_H - 2}">wavenumber (cm⁻¹)</text>'
    return (f'<svg viewBox="0 0 {SVG_W} {SVG_H}" role="img" aria-label="{html.escape(label)}">'
            f'<line class="base" x1="{PAD_L}" x2="{SVG_W - PAD_R}" y1="{_y(0)}" y2="{_y(0)}"/>{"".join(ticks)}{"".join(paths)}{axis}</svg>')


def family_rows(bands: list[dict], readouts: dict[str, dict], readouts_b: dict[str, dict]) -> list[dict]:
    """Per family the certificate's band count and licence, with the network's measured error on hold-outs (a) and (b)."""
    rows = []
    for fam in FAMILY_ORDER:
        mine = [b for b in bands if b["family"] == fam]
        if not mine:
            continue
        licensed = {b["licensed"] for b in mine}
        if len(licensed) != 1:
            raise ValueError(f"family {fam}: bands disagree on the licence")
        rows.append({"family": fam, "bands": len(mine), "licensed": licensed.pop(),
                     "error_a": readouts[fam]["mean"], "error_b": readouts_b[fam]["mean"]})
    if sum(r["bands"] for r in rows) != len(bands):
        raise ValueError("a band's family is outside " + ", ".join(FAMILY_ORDER))
    return rows


def _e(x: object) -> str:
    return html.escape(str(x))


def _chip(licensed: bool) -> str:
    return '<span class="chip ok">licensed</span>' if licensed else '<span class="chip no">not licensed</span>'


def _minutes(seconds: float) -> str:
    if seconds < 90:
        return f"{seconds:.0f} s"
    return f"{seconds / 60:.0f} min" if seconds < 5400 else f"{seconds / 3600:.1f} h"


def _tiles(p: Panel) -> str:
    c = p.certificate
    tiles = []
    if p.vs_corpus is not None:
        t = p.vs_corpus["against_truth"]
        tiles += [("network against ωB97X", f'{t["all_modes"]["network"]:.2f} cm⁻¹', "rms over all modes"),
                  ("B3LYP against ωB97X", f'{t["all_modes"]["B3LYP"]:.2f} cm⁻¹', "rms over all modes"),
                  ("spectrum overlap", f'{t["spectrum_overlap"]["network"]:.3f}', f'B3LYP {t["spectrum_overlap"]["B3LYP"]:.3f}; 1 = the same shape')]
    else:
        n_lic = sum(b["licensed"] for b in c["bands"])
        tiles.append(("bands licensed", f'{n_lic} of {len(c["bands"])}', "no truth in the corpus: the certificate's error applies"))
    tiles.append(("laptop time", _minutes(c["cost"]["seconds"]), f'€ {c["cost"]["eur_ex_vat"]:.2f} ex VAT'))
    return "".join(f'<div class="tile"><span class="tk">{_e(k)}</span><span class="tv">{_e(v)}</span><span class="ts">{_e(s)}</span></div>'
                   for k, v, s in tiles)


def _family_table(p: Panel) -> str:
    h = p.certificate["accuracy"]["holdouts"]
    rows = family_rows(p.certificate["bands"], h["a"]["readouts"], h["b"]["readouts"])
    truth = p.vs_corpus["against_truth"]["per_family"] if p.vs_corpus is not None else {}
    head = "<th>family</th><th class=num>bands</th><th>licence</th><th class=num>error (a) / (b)</th>"
    head += "<th class=num>this molecule: network / B3LYP</th>" if truth else ""
    body = []
    for r in rows:
        cells = (f'<td>{_e(r["family"])}</td><td class=num>{r["bands"]}</td><td>{_chip(r["licensed"])}</td>'
                 f'<td class=num>{r["error_a"]:.2f} / {r["error_b"]:.2f}</td>')
        if truth:
            f = truth[r["family"]]
            cells += f'<td class=num>{f["network"]:.2f} / {f["B3LYP"]:.2f}</td>'
        body.append(f"<tr>{cells}</tr>")
    return f'<div class="scroll"><table><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table></div>'


def _legend(p: Panel) -> str:
    return "".join(f'<span class="lg"><i class="sw c-{k}"></i>{_e(name)}</span>' for k, name in CURVES if k in p.curves)


def molecule_section(p: Panel) -> str:
    m = p.certificate["molecule"]
    svg = svg_spectrum(p.grid, p.curves, f'{m["name"]}: infrared spectra, relative absorbance against wavenumber')
    return (f'<section class="mol" id="{_e(m["name"])}"><header><h2>{_e(m["name"])}</h2>'
            f'<p class="meta"><code>{_e(m["smiles"])}</code> · {_e(m["formula"])} · {m["n_atoms"]} atoms · '
            f'pipeline {_e(p.certificate["pipeline_version"])}</p><p class="meta">{_e(p.demo.origin)}</p>'
            f'<p class="meta">The network: {_e(m["seen"]["text"])}.</p></header>'
            f'<div class="tiles">{_tiles(p)}</div><figure class="plot">{svg}<figcaption>{_legend(p)}'
            f'<span class="lg note">Lorentzian, FWHM 10 cm⁻¹; heights from the B3LYP APT; each panel scaled to its largest peak</span>'
            f"</figcaption></figure>{_family_table(p)}</section>")


STEPS = (("Admission", "canonical SMILES; elements and size inside the network's training set; the carried models", None),
         ("Geometry", "psi4, B3LYP/6-31G* optimisation", "optimise"),
         ("B3LYP Hessian and APT", "pyscf, analytic, in WSL", "low_level"),
         ("ΔH correction", "ΔH-network, three seeds; their spread is each band's range", "correction_and_spectra"),
         ("Spectra", "double harmonic; corrected and uncorrected", None),
         ("Certificate", "per band: family, licence, measured error, laboratory tolerance", None))


def steps_section(panels: list[Panel]) -> str:
    names = "".join(f"<th class=num>{_e(p.certificate['molecule']['name'])}</th>" for p in panels)
    rows = []
    for title, what, key in STEPS:
        cells = "".join(f"<td class=num>{_minutes(p.certificate['cost']['steps_s'][key]) if key else ''}</td>" for p in panels)
        rows.append(f"<tr><td><b>{_e(title)}</b><br><span class=muted>{_e(what)}</span></td>{cells}</tr>")
    note = "the correction's time covers the spectra and the certificate too"
    return (f'<section><h2>Six steps, molecule in, spectrum out</h2><div class="scroll"><table class="steps"><thead><tr><th>step</th>{names}'
            f'</tr></thead><tbody>{"".join(rows)}</tbody></table></div><p class="muted small">Times on the laptop; {note}.</p></section>')


def licence_section(cert: dict) -> str:
    h = cert["accuracy"]["holdouts"]
    rows = "".join(
        f'<tr><td>{_e(f)}</td><td class=num>{h["a"]["readouts"][f]["mean"]:.2f}</td><td class=num>{h["b"]["readouts"][f]["mean"]:.2f}</td>'
        f'<td>{_chip(f in cert["licence"]["licensed_families"])}</td></tr>'
        for f in FAMILY_ORDER)
    shape = h["a"]["shape"]
    return (f'<section><h2>How well the network is known</h2><p>{_e(cert["network"]["name"])} v{_e(cert["network"]["version"])} predicts '
            f'{_e(cert["network"]["predicts"])}. A family is licensed where its error stays within 3 cm⁻¹ on both hold-outs '
            f'({_e(cert["licence"]["rule_source"])}).</p><div class="scroll"><table><thead><tr><th>family</th>'
            f'<th class=num>hold-out (a), {h["a"]["n_molecules"]} molecules</th><th class=num>hold-out (b), {h["b"]["n_molecules"]} molecules</th>'
            f'<th>licence</th></tr></thead><tbody>{rows}</tbody></table></div><p class="muted small">Seed-mean rms error of the corrected '
            f'positions, cm⁻¹. Spectrum overlap on hold-out (a): {shape["cheap"]["spectrum_overlap"]} uncorrected, '
            f'{shape["corrected"]["spectrum_overlap"]} corrected.</p><p class="muted small">{_e(h["a"]["description"])}.</p>'
            f'<p class="muted small">{_e(h["b"]["description"])}.</p></section>')


LIMITS = ("Positions are harmonic: the anharmonic shift is not in this version (TASKS 53).",
          "The coupled-cluster level is not measured for this network version; the anchor decision is in November.",
          "A molecule that is not planar gets no CH-oop band under the family rule, so those bands count as 'other' and are not licensed.",
          "Closed-shell neutral molecules only; cations wait for their training rows (TASKS 121).",
          "The answer depends slightly on the atom order; the pipeline starts from the canonical SMILES so that every writing gives one "
          "answer, and network v1.5 removes the cause (TASKS 149).")


def _provenance(panels: list[Panel]) -> str:
    rows = []
    for p in panels:
        pv = p.certificate["provenance"]
        models = ", ".join(m["sha16"][:8] for m in p.certificate["network"]["models"])
        folder = p.demo.folder.relative_to(P.PLAN).as_posix()
        rows.append(f"<tr><td>{_e(p.certificate['molecule']['name'])}</td><td><code>{_e(folder)}</code></td>"
                    f"<td><code>{_e(pv['run_commit'][:8])}</code></td><td><code>{_e(models)}</code></td></tr>")
    return ('<section><h2>Sources</h2><div class="scroll"><table class="small"><thead><tr><th>molecule</th><th>result folder</th>'
            f'<th>run commit</th><th>models</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div></section>')


def page(panels: list[Panel]) -> str:
    """The whole page; every panel must come from the same network version, since the page states one measured error."""
    versions = {(p.certificate["network"]["name"], p.certificate["network"]["version"]) for p in panels}
    if len(versions) != 1:
        raise ValueError(f"the demo mixes network versions: {sorted(versions)}")
    cert = panels[0].certificate
    lead = (f'A molecule goes in as a SMILES string; out comes its infrared spectrum: B3LYP/6-31G* corrected toward ωB97X/6-31G* by the '
            f'{_e(cert["network"]["name"])} v{_e(cert["network"]["version"])}, with a certificate that says per band how well the network '
            f'is known there. Pipeline {_e(", ".join(sorted({p.certificate["pipeline_version"] for p in panels})))}; built from the result '
            f'folders listed at the end.')
    limits = "".join(f"<li>{_e(x)}</li>" for x in LIMITS)
    return (f'<title>Spectrum Pipeline Demo</title><meta name="claude:viewport-fit-sides" content="cover">{STYLE}'
            f'<main class="wrap"><header class="top"><p class="eyebrow">Module 08 · the pipeline</p><h1>From a SMILES string to an infrared '
            f'spectrum</h1><p class="lead">{lead}</p><nav>{" ".join(_nav(p) for p in panels)}</nav></header>'
            f'{steps_section(panels)}{"".join(molecule_section(p) for p in panels)}{licence_section(cert)}'
            f'<section><h2>Not in this version</h2><ul>{limits}</ul></section>{_provenance(panels)}</main>')


def _nav(p: Panel) -> str:
    name = p.certificate["molecule"]["name"]
    return f'<a href="#{_e(name)}">{_e(name)}</a>'


STYLE = """<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet"
href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700&family=JetBrains+Mono:wght@400;500&display=swap">
<style>
/* One reading column; a molecule per section, its spectrum full width; the Spectrum Atlas's tokens (website/site/src/styles/tokens.css). */
:root {
  --bg: oklch(0.99 0.004 260); --bg-elev: oklch(1 0 0); --fg: oklch(0.22 0.02 260); --fg-muted: oklch(0.48 0.02 260);
  --line: oklch(0.90 0.01 260); --accent: oklch(0.50 0.16 275); --accent-soft: oklch(0.94 0.04 275);
  --ok: oklch(0.55 0.14 150); --no: oklch(0.55 0.02 260); --b3lyp: oklch(0.62 0.13 45); --focus: oklch(0.55 0.20 275);
  --font-sans: "Source Sans 3", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --bg: oklch(0.17 0.015 260); --bg-elev: oklch(0.21 0.015 260); --fg: oklch(0.93 0.01 260); --fg-muted: oklch(0.70 0.015 260);
  --line: oklch(0.30 0.015 260); --accent: oklch(0.78 0.12 275); --accent-soft: oklch(0.30 0.06 275);
  --ok: oklch(0.75 0.13 150); --no: oklch(0.65 0.02 260); --b3lyp: oklch(0.76 0.12 50); --focus: oklch(0.80 0.16 275); color-scheme: dark } }
:root[data-theme="dark"] {
  --bg: oklch(0.17 0.015 260); --bg-elev: oklch(0.21 0.015 260); --fg: oklch(0.93 0.01 260); --fg-muted: oklch(0.70 0.015 260);
  --line: oklch(0.30 0.015 260); --accent: oklch(0.78 0.12 275); --accent-soft: oklch(0.30 0.06 275);
  --ok: oklch(0.75 0.13 150); --no: oklch(0.65 0.02 260); --b3lyp: oklch(0.76 0.12 50); --focus: oklch(0.80 0.16 275); color-scheme: dark }
*, *::before, *::after { box-sizing: border-box; }
body { background: var(--bg); color: var(--fg); font-family: var(--font-sans); font-size: 16px; line-height: 1.5; }
.wrap { max-width: 860px; margin-inline: auto; padding-block: 32px 64px;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px));
  display: grid; grid-template-columns: minmax(0, 1fr); gap: 40px; }
.wrap > * { min-width: 0; }
h1, h2 { line-height: 1.2; letter-spacing: -0.01em; text-wrap: balance; margin: 0 0 12px; font-weight: 700; }
h1 { font-size: 2rem; } h2 { font-size: 1.35rem; }
p, li { max-width: 68ch; } p { margin: 0 0 12px; }
a { color: var(--accent); text-underline-offset: 2px; }
:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; border-radius: 4px; }
code { font-family: var(--font-mono); font-size: 0.88em; overflow-wrap: anywhere; }
.eyebrow { text-transform: uppercase; letter-spacing: 0.08em; font-size: 0.8rem; color: var(--fg-muted); margin: 0 0 6px; }
.lead { font-size: 1.1rem; }
nav { display: flex; flex-wrap: wrap; gap: 8px 16px; }
.muted { color: var(--fg-muted); } .small { font-size: 0.88rem; }
.meta { color: var(--fg-muted); margin: 0 0 4px; }
.mol { display: grid; gap: 16px; border-top: 1px solid var(--line); padding-top: 24px; }
.mol header, .mol .tiles, .mol .plot, .mol .scroll { min-width: 0; }
.tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 12px; }
.tile { display: grid; gap: 2px; padding: 12px 14px; background: var(--bg-elev); border: 1px solid var(--line); border-radius: 10px; }
.tk { font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--fg-muted); }
.tv { font-family: var(--font-mono); font-variant-numeric: tabular-nums; font-size: 1.35rem; font-weight: 500; }
.ts { font-size: 0.82rem; color: var(--fg-muted); }
.plot { margin: 0; }
.plot svg { width: 100%; height: auto; display: block; }
.plot polyline { fill: none; stroke-width: 1.4; stroke-linejoin: round; }
.c-truth { stroke: var(--fg); background: var(--fg); }
.c-network { stroke: var(--accent); background: var(--accent); }
.c-b3lyp { stroke: var(--b3lyp); background: var(--b3lyp); stroke-dasharray: 4 3; }
.plot .tick { stroke: var(--line); stroke-width: 1; }
.plot .base { stroke: var(--fg-muted); stroke-width: 1; }
.plot .tl { fill: var(--fg-muted); font-size: 11px; text-anchor: middle; font-family: var(--font-sans); }
figcaption { display: flex; flex-wrap: wrap; gap: 6px 18px; font-size: 0.88rem; margin-top: 6px; }
.lg { display: inline-flex; align-items: center; gap: 6px; } .lg.note { color: var(--fg-muted); flex-basis: 100%; }
.sw { display: inline-block; width: 18px; height: 3px; border-radius: 2px; }
.scroll { overflow-x: auto; }
table { border-collapse: collapse; width: 100%; font-size: 0.95rem; }
th, td { text-align: left; padding: 7px 10px; border-bottom: 1px solid var(--line); vertical-align: top; }
th { font-weight: 600; color: var(--fg-muted); font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.04em; }
.num { text-align: right; font-family: var(--font-mono); font-variant-numeric: tabular-nums; white-space: nowrap; }
.chip { display: inline-block; padding: 1px 9px; border-radius: 999px; border: 1px solid currentColor; font-size: 0.82rem; white-space: nowrap; }
.chip.ok { color: var(--ok); } .chip.no { color: var(--no); }
ul { margin: 0; padding-left: 20px; display: grid; gap: 6px; }
</style>"""


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", type=Path, default=OUT)
    a = ap.parse_args(argv)
    text = page([load_panel(d) for d in DEMO])
    a.out.parent.mkdir(parents=True, exist_ok=True)
    tmp = a.out.with_suffix(".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(a.out)
    print(f"demo page: {a.out} ({len(text) / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
