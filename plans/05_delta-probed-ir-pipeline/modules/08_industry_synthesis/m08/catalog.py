"""The repository as the request officer sees it: the website export (catalogue, per-molecule records, summary), module 03's tolerance table and
laboratory band table. Read-only. Families follow module 03's wavenumber rule so that the certificate's per-band budget and the laboratory
tolerance speak the same language."""
from __future__ import annotations

import csv
import json
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLAN = HERE.parents[2]                       # plans/05_delta-probed-ir-pipeline
REPO = PLAN.parents[1]                       # CapstonePlan
EXPORT = REPO / "website" / "export" / "out"
M03 = PLAN / "modules" / "03_lab_scoreboard"

# module 03's family rule (build_lab_tables.py, FAMILY_RULE) — copied, not re-derived, so that the two modules agree by construction
FAMILY_RULE = [
    (0.0, 650.0, "low / skeletal"), (650.0, 950.0, "CH-oop (10.5-15 um; benzene nu11 at 673 included)"), (950.0, 1100.0, "ring / CH-ip (9-10.5 um)"),
    (1100.0, 1250.0, "CH-ip-bend (8.6 um)"), (1250.0, 1500.0, "CC-stretch/CH-ip (7.7 um)"), (1500.0, 1650.0, "CC-stretch (6.2 um)"),
    (1650.0, 2950.0, "overtone / combination region"), (2950.0, 3200.0, "CH-stretch"), (3200.0, 1e9, "above 3200"),
]
FAMILY_SOURCE = "modules/03_lab_scoreboard/build_lab_tables.py FAMILY_RULE (12 Sep 2026)"
RUNG_LABELS = {0: "listed", 1: "cheap_level_done", 2: "correction_predicted", 3: "spectrum_predicted", 4: "anchored", 5: "validated"}


def family(nu: float) -> str:
    for lo, hi, lab in FAMILY_RULE:
        if lo <= nu < hi:
            return lab
    return "?"


def canonical(smiles: str | None) -> str | None:
    if not smiles:
        return None
    from rdkit import Chem, RDLogger
    RDLogger.DisableLog("rdApp.*")
    m = Chem.MolFromSmiles(smiles)
    return Chem.MolToSmiles(m) if m is not None else None


class Catalog:
    def __init__(self, export: Path = EXPORT):
        self.export = Path(export)
        self.rows = json.load(open(self.export / "catalog.json", encoding="utf-8"))
        self.summary = json.load(open(self.export / "summary.json", encoding="utf-8"))
        self.by_id = {r["id"]: r for r in self.rows}
        self.by_name: dict[str, dict] = {}
        for r in self.rows:
            self.by_name.setdefault(r["name"].lower(), r)
        self._by_canon: dict[str, dict] | None = None
        self._u_rows: list[dict] | None = None
        self._lab: list[dict] | None = None

    # ---------------------------------------------------------------------------------------------- lookup
    def _canon_index(self) -> dict[str, dict]:
        if self._by_canon is None:
            idx: dict[str, dict] = {}
            for r in self.rows:
                c = canonical(r.get("smiles"))
                if c:
                    idx.setdefault(c, r)
            self._by_canon = idx
        return self._by_canon

    def find(self, query: str) -> dict | None:
        """By manifest id, by corpus name (case-insensitive), or by SMILES (canonical match)."""
        q = query.strip()
        if q in self.by_id:
            return self.by_id[q]
        if q.lower() in self.by_name:
            return self.by_name[q.lower()]
        c = canonical(q)
        return self._canon_index().get(c) if c else None

    def molecule(self, mid: str) -> dict | None:
        p = self.export / "molecules" / f"{mid}.json"
        return json.load(open(p, encoding="utf-8")) if p.exists() else None

    # ---------------------------------------------------------------------------------------------- module 03
    def _u_band_rows(self) -> list[dict]:
        if self._u_rows is None:
            self._u_rows = list(csv.DictReader(open(M03 / "out" / "u_band_by_record_family.csv", encoding="utf-8")))
        return self._u_rows

    def u_band(self, species: str) -> dict[str, dict]:
        """Per family: the laboratory tolerance u_band (cm⁻¹) for this species (primary record's median) or the all-record median as the default."""
        rows = self._u_band_rows()
        out: dict[str, dict] = {}
        fams = sorted({r["family"] for r in rows})
        for f in fams:
            own = [r for r in rows if r["family"] == f and r["species"].lower() == species.lower()]
            own_primary = [r for r in own if r["role"] == "primary"] or own
            if own_primary:
                vals = [float(r["u_band_median"]) for r in own_primary]
                out[f] = dict(u_band=round(statistics.median(vals), 2), source=f"module 03 u_band_by_record_family.csv, {species}, record(s) "
                              + ", ".join(sorted({r['record'] for r in own_primary})), kind="species")
            else:
                vals = [float(r["u_band_median"]) for r in rows if r["family"] == f]
                out[f] = dict(u_band=round(statistics.median(vals), 2), source=f"module 03 u_band_by_record_family.csv, median over {len(vals)} records (family default)",
                              kind="family default")
        return out

    def _lab_rows(self) -> list[dict]:
        if self._lab is None:
            self._lab = list(csv.DictReader(open(M03 / "notebook" / "bands_lab.csv", encoding="utf-8")))
        return self._lab

    def lab_bands(self, species: str) -> dict:
        rows = [r for r in self._lab_rows() if r["species"].lower() == species.lower()]
        fams: dict[str, int] = {}
        for r in rows:
            fams[r["family"]] = fams.get(r["family"], 0) + 1
        return dict(n_bands=len(rows), records=sorted({r["record"] for r in rows}), per_family=fams, source="module 03 notebook/bands_lab.csv")
