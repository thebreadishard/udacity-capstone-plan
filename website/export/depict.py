"""Spectrum Atlas — 2D depictions of the catalogue molecules as themed SVG (BACKLOG step 2, 24 September 2026).

RDKit draws each molecule once at build time; the SVG is post-processed so that carbon bonds and labels use `currentColor` (the page's text colour,
light or dark) and heteroatoms use the accent token `var(--accent)`; no client JavaScript is needed to show a molecule. Alt text is built from the
name and the formula. Output: out/depictions/<id>.svg and out/depictions/index.json {id: {alt, width, height}}.

Usage: python depict.py [--catalog out/catalog.json] [--out out/depictions] [--only-computed] [--size 240]
"""
import argparse
import json
import os
import re

from rdkit import Chem, RDLogger
from rdkit.Chem import rdDepictor
from rdkit.Chem.Draw import rdMolDraw2D

RDLogger.DisableLog("rdApp.*")
HETERO = {"N": "#5b5bd6", "O": "#5b5bd6", "S": "#5b5bd6", "F": "#5b5bd6", "Cl": "#5b5bd6", "Br": "#5b5bd6"}   # one accent; the CSS variable replaces it


def depict(smiles, size=240):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    rdDepictor.SetPreferCoordGen(True); rdDepictor.Compute2DCoords(mol)
    d = rdMolDraw2D.MolDraw2DSVG(size, size); o = d.drawOptions()
    o.clearBackground = False; o.bondLineWidth = 2; o.padding = 0.08; o.addAtomIndices = False
    o.useBWAtomPalette()                       # black carbons and labels → currentColor after post-processing
    for sym, col in HETERO.items():
        z = Chem.GetPeriodicTable().GetAtomicNumber(sym); r, g, b = (int(col[i:i + 2], 16) / 255 for i in (1, 3, 5)); o.updateAtomPalette({z: (r, g, b)})
    d.DrawMolecule(mol); d.FinishDrawing(); svg = d.GetDrawingText()
    svg = re.sub(r"#000000", "currentColor", svg, flags=re.I); svg = re.sub(r"#5B5BD6", "var(--accent, #5b5bd6)", svg, flags=re.I)
    svg = svg.replace("<svg ", "<svg role='img' focusable='false' ", 1)
    return svg


def main():
    ap = argparse.ArgumentParser(); here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--catalog", default=os.path.join(here, "out", "catalog.json")); ap.add_argument("--out", default=os.path.join(here, "out", "depictions"))
    ap.add_argument("--only-computed", action="store_true"); ap.add_argument("--size", type=int, default=240); a = ap.parse_args()
    cat = json.load(open(a.catalog, encoding="utf-8")); os.makedirs(a.out, exist_ok=True); index = {}; skipped = 0
    for r in cat:
        if a.only_computed and r["rung"] < 1:
            continue
        if not r["smiles"]:
            skipped += 1; continue
        svg = depict(r["smiles"], a.size)
        if svg is None:
            skipped += 1; continue
        open(os.path.join(a.out, r["id"] + ".svg"), "w", encoding="utf-8").write(svg)
        index[r["id"]] = dict(alt=f"Structure of {r['name']}" + (f" ({r['formula']})" if r.get("formula") else ""), width=a.size, height=a.size)
    json.dump(index, open(os.path.join(a.out, "index.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print(f"depictions: {len(index)} written, {skipped} skipped (no or unparsable SMILES) → {a.out}")


if __name__ == "__main__":
    main()
