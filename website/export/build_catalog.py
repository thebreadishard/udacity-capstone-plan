"""Spectrum Atlas — mechanical export of the pipeline repository to the site's JSON (BACKLOG step 1, 24 September 2026).

Sources (read-only): the corpus manifest and ledger, every corpus molecule directory with a result, the release manifests, the second-route
checks, the anchor registry (`modules/05_support_predictor/out/ANCHORS_STATUS.json`: a molecule with a carried coupled-cluster entry is anchored,
its file is the evidence — 7 Oct 2026) and the fixed list of validated molecules below. Outputs:
  out/catalog.json           one row per manifest molecule: identity, size, source, rung, flags, release membership, formula and InChIKey (RDKit)
  out/molecules/<id>.json    per computed molecule: geometry, frequency lists per functional, imaginary counts, timings, deck, second route, releases
  out/summary.json           rung, layer and source counts, data freshness, source hashes, the carried network's accuracy, licence and
                             network pair (decision 66: release networks print, measurement networks measure)
The script fails (non-zero exit) when an invariant breaks: a catalog id without a manifest row, a frequency list whose length is not 3N, rung
counts that do not add up, a computed molecule without both Hessians. Nothing here is typed by hand; the anchored/validated list names its files.

Usage: python build_catalog.py [--repo <CapstonePlan root>] [--out <dir>] [--limit N]
"""
import argparse
import csv
import glob
import hashlib
import importlib
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

RUNGS = ["listed", "cheap_level_done", "correction_predicted", "spectrum_predicted", "anchored", "validated"]

# Where a manifest row came from (step (d) of the candidate generator's batch route, 6 Oct 2026), keyed by the manifest layer. A layer without a line
# here stops the export (KeyError) rather than shipping an unlabelled molecule. Generator rows carry 'pubchem yes|no' in their manifest note.
SOURCES = {
    "A": "parent molecules chosen by hand (benzene, naphthalene, the PAH cores and their relatives)",
    "A2": "substituted three- and four-ring cores, enumerated from the parents (layer A′)",
    "B": "cores with one or two substituents, enumerated from the parents",
    "C": "Hessian-QM9 (small molecules of up to nine heavy atoms)",
    "P3": "pool 3, chosen by rule (decision 54): aza four-rings and five-ring systems",
    "P3c": "pool 3, chosen by rule (decision 54): cations of finished parents",
    "G": "proposed by the candidate generator (module 06): a new fused ring system",
    "R4": "rung 4 of the size ladder, chosen by rule: four-ring families as broad sets (TASKS 61)",
    "T": "large PAHs from NASA Ames PAHdb (coronene to hexa-peri-hexabenzocoronene), computed to test how the method scales with size",
    "D": "PAHs of 22 to 34 carbons from NASA Ames PAHdb, computed to test how the method scales with size",
}


def source_of(r):
    """The source line of a manifest row; generator rows say whether PubChem knows the ring system."""
    s = SOURCES[r["layer"]]
    if r["layer"] == "G":
        s += ", known to PubChem" if "pubchem yes" in r.get("note", "") else ", not in PubChem"
    return s


def second_route_of(mdir: str, analytic_only: bool) -> dict | None:
    """Per functional the largest frequency difference (cm⁻¹) and dH_max between the analytic second route and the corpus's
    finite-difference Hessian; None without a check. An analytic-only folder has no finite-difference Hessian — its labels are the
    analytic ones — so there is nothing to compare and None is returned. A check without corpus frequencies in a folder with
    finite-difference labels is refused with the reason."""
    path = os.path.join(mdir, "analytic_check.json")
    if analytic_only or not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        chk = json.load(f)
    bare = sorted(tag for tag, v in chk.items() if "freq_corpus" not in v)
    if bare:
        raise ValueError(f"{path}: no corpus frequencies for {bare} in a folder with finite-difference labels, so the second route has "
                         "nothing to be compared with")
    return {tag: dict(max_abs_dfreq_cm=float(np.abs(np.array(v["freq_analytic"]) - np.array(v["freq_corpus"])).max()), dH_max=v["dH_max"])
            for tag, v in chk.items()}


def deck_of(result: dict, mdir: str, analytic_only: bool) -> dict | None:
    """The deck the molecule's labels were made with. result.json's deck describes psi4's finite-difference Hessians; in an
    analytic-only folder psi4 optimised the geometry only and both Hessians are pyscf's analytic ones, said from the files' own
    provenance (the pyscf version in analytic_check.json, the grid in the Hessian files)."""
    deck = result.get("deck")
    if not analytic_only:
        return deck
    with open(os.path.join(mdir, "analytic_check.json"), encoding="utf-8") as f:
        pyscf = {v["software"]["pyscf"] for v in json.load(f).values()}
    grids = set()
    for tag in ("b3lyp", "wb97x"):
        with np.load(os.path.join(mdir, f"hessian_{tag}_analytic.npz")) as z:
            grids.add(tuple(int(x) for x in np.ravel(z["grid"])))
    if len(pyscf) != 1 or len(grids) != 1:
        raise ValueError(f"{mdir}: the two analytic Hessians come from {sorted(pyscf)} on grids {sorted(grids)}; one deck has one of each")
    hessian = (f"pyscf {pyscf.pop()} analytic Hessians of both functionals at the psi4-optimised geometry, 6-31G* with Cartesian d, grid "
               f"{grids.pop()} (module 05's corpus/analytic_hessians.py); psi4 optimised the geometry only")
    return {**{k: v for k, v in deck.items() if k != "text_corrections"}, "hessian": hessian, "labels": "analytic_only"}


def licence_line(accuracy: dict) -> float:
    """The one error line every family's licence is read against; families or test sets with different lines are refused, since the
    Atlas card states a single line."""
    lines = {row["target"] for holdout in accuracy["holdouts"].values() for row in holdout["product"].values()}
    if len(lines) != 1:
        raise ValueError(f"the licence lines differ between families or test sets ({sorted(lines)}); the Atlas card states one line")
    return lines.pop()


CHARGE = re.compile(r"\bcharge (-?\d+)")


def charge_of(row: dict) -> int:
    """A manifest row's charge: charged rows (pool 3's cations) state it in their note; the others are neutral, the deck's charge 0."""
    m = CHARGE.search(row.get("note", ""))
    return int(m.group(1)) if m else 0


def canonical_smiles(smiles: str) -> str:
    """RDKit's canonical SMILES; an unparsable one is refused. It keeps tautomers apart, which the InChIKey merges (4- and
    5-formylimidazole are two computed rows with one InChIKey)."""
    from rdkit import Chem
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"unparsable SMILES {smiles!r}")
    return Chem.MolToSmiles(mol)


def pool_of(ids: set[str], manifest: list[dict]) -> dict:
    """What a training pool holds, from the manifest: its entries (corpus rows), the distinct molecule-and-charge pairs among them (a
    molecule may have a row in two layers) and the range of their atom counts. An id without a manifest row is refused."""
    rows = {r["id"]: r for r in manifest if r["id"] in ids}
    if len(rows) != len(ids):
        raise ValueError(f"training ids without a manifest row: {sorted(ids - set(rows))[:5]}")
    pairs = {(canonical_smiles(r["smiles"]), charge_of(r)) for r in rows.values()}
    atoms = [int(r["n_atoms"]) for r in rows.values()]
    return dict(entries=len(rows), distinct=len(pairs), atoms=[min(atoms), max(atoms)])


def network_pair(pipeline, manifest: list[dict]) -> dict:
    """Decision 66's pair of the carried version, as module 08's pipeline runs it (`m08.pipeline.product_networks`): which kind makes
    the printed spectra, how many networks, the atom-count range of their training pool, and for release networks the number of
    training-pool entries, the distinct molecule-and-charge pairs among them and how each network used them; the errors and the licence
    are always the measurement networks'."""
    made = pipeline.product_networks()
    pool = pool_of(pipeline.train_ids(made.models), manifest)
    out = dict(kind=made.kind, n_networks=len(made.models), held_back=made.held_back, pool_atoms=pool["atoms"],
               measurement_networks=len(pipeline.carried_models(pipeline.NK.MEASUREMENT)), trained_on_entries=None,
               distinct_entries=None, fitting=None)
    if made.kind == pipeline.NK.RELEASE:
        share = pipeline.inner_validation_share(made.models)
        out |= dict(trained_on_entries=pool["entries"], distinct_entries=pool["distinct"],
                    fitting=pipeline.NK.fitting_sentence(len(made.models), share))
    return out


def anchored_from_registry(plan: str) -> tuple[dict, dict]:
    """7 Oct 2026: {mol_id: [evidence path]} and {mol_id: level} for every carried entry of the anchor registry — the best coupled-cluster Hessian of
    each molecule, chosen in one place (`m05/anchor_registry.py`); superseded, imaginary and invalid entries never reach the Atlas."""
    p = os.path.join(plan, "modules", "05_support_predictor", "out", "ANCHORS_STATUS.json")
    with open(p, encoding="utf-8") as f:
        entries = json.load(f)["anchors"]
    carried = [e for e in entries if e["status"] == "carried"]
    return ({e["mol_id"]: [e["path"], *READINGS.get(e["mol_id"], [])] for e in carried},
            {e["mol_id"]: e["level"] for e in carried})


# The readings of a molecule's coupled-cluster data (documents, not Hessians), listed after the registry's file: module 08's certificate reads the
# per-family deviation of the composite from CCSD(T) out of benzene's R0 table (8 Oct 2026: dropped by the 7 Oct switch, restored here).
READINGS = {
    "A_8448043181": ["probes/results_m1/e8_benzene_ccpvdz_tlambda/E8_locality_benzene.md", "probes/results_m1/R0_DIAGONAL_READING_2026-09-22.md"],
    "A_01f3186607": ["probes/results_m1/e8_naphthalene_ccpvdz_tlambda_2026-10-02/E8_locality_naphthalene.md",
                     "probes/results_m1/M3_TZ_MODE22_READING_2026-09-23.md"],
}


# The hand list this registry replaced (2 Oct 2026), kept for the record of what the Atlas showed until 7 Oct: the four CCSD(T)/cc-pVDZ Hessians.
# 2 Oct 2026: the four CCSD(T)/cc-pVDZ Hessians of the corrected route (lambda incident of 29 Sep: the earlier benzene reading is kept as
# history).
ANCHORED_UNTIL_2026_10_07 = {
    "A_8448043181": ["probes/results_m1/e8_benzene_ccpvdz_tlambda/E8_locality_benzene.md", "probes/results_m1/e8_benzene_ccpvdz_tlambda/hessian_ccsd_t.npz",
                     "probes/results_m1/R0_DIAGONAL_READING_2026-09-22.md"],
    "A_01f3186607": ["probes/results_m1/e8_naphthalene_ccpvdz_tlambda_2026-10-02/E8_locality_naphthalene.md",
                     "probes/results_m1/e8_naphthalene_ccpvdz_tlambda_2026-10-02/hessian_ccsd_t.npz", "probes/results_m1/M3_TZ_MODE22_READING_2026-09-23.md"],
    "B_8b12a55d3a": ["probes/results_m1/e8_fluorobenzene_ccpvdz_2026-09-30/hessian_ccsd_t.npz"],
    "A_6e858b26e5": ["probes/results_m1/e8_pyridine_ccpvdz_2026-09-30/hessian_ccsd_t.npz"],
}
VALIDATED = {
    "A_8448043181": ["probes/results_vpt2/benzene_benchmark_2026-09-22.md"],
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def formula_and_key(smiles):
    """(formula, InChIKey, n_atoms with hydrogens, n_heavy) from RDKit; Nones when RDKit is absent or the SMILES does not parse."""
    try:
        from rdkit import Chem, RDLogger
        from rdkit.Chem import rdMolDescriptors
        RDLogger.DisableLog("rdApp.*")
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None, None, None, None
        try:
            key = Chem.MolToInchiKey(mol) or None
        except Exception:  # noqa: BLE001  RDKit's InChI layer raises its own error kinds; a molecule without a key gets None
            key = None
        return rdMolDescriptors.CalcMolFormula(mol), key, Chem.AddHs(mol).GetNumAtoms(), mol.GetNumHeavyAtoms()
    except ImportError:
        return None, None, None, None


def _plain(s):
    """The ledger's markdown as the page shows it, plain text: bold and code markers removed (they showed literally, 14 Oct 2026)."""
    return s.replace("**", "").replace("`", "").strip()


def read_changelog(ledger_md):
    """The obstacle ledger's dated entries ('- **23 Sep, 14:4x — title.** body…'): date, time, title (the bold head up to its first full stop) and the
    first 300 characters of the body, newest first as the ledger keeps them. Mechanical; nothing is rewritten."""
    if not os.path.exists(ledger_md):
        return []
    months = {"Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12", "Aug": "08"}
    head = re.compile(r"- \*\*(\d{1,2}) (Sep|Oct|Nov|Dec|Aug),? ([0-9:x]+) — ")
    # An entry is its head line and the continuation lines up to the next list item, heading or blank line: a bold head may run over two
    # lines (14 Oct 2026: a line-by-line match had missed 11 of 489 entries).
    with open(ledger_md, encoding="utf-8") as f:
        lines = list(f)
    entries, cur = [], None
    for line in lines:
        s = line.strip()
        if head.match(s):
            cur = [s]
            entries.append(cur)
        elif cur is not None and s and not s.startswith(("- ", "#", "|")):
            cur.append(s)
        else:
            cur = None
    out = []
    for e in entries:
        text = " ".join(e)
        m = re.match(r"- \*\*(\d{1,2}) (Sep|Oct|Nov|Dec|Aug),? ([0-9:x]+) — (.+?)\*\*\s*(.*)", text, re.DOTALL)
        if not m:   # a head whose bold is never closed (6 entries): its first sentence is the title
            m = re.match(r"- \*\*(\d{1,2}) (Sep|Oct|Nov|Dec|Aug),? ([0-9:x]+) — (.+?[.:])(?:\s+|$)(.*)", text, re.DOTALL)
        if not m:
            continue
        day, mon, hhmm, title, body = m.groups()
        out.append(dict(date=f"2026-{months[mon]}-{int(day):02d}", time=hhmm, title=_plain(title), body=_plain(body)[:300]))
    out.sort(key=lambda e: (e["date"], e["time"].replace("x", "0")), reverse=True)   # the ledger's day blocks are not strictly ordered; the site is
    return out


def vib_only(freq):
    f = np.asarray(freq, float)
    keep = np.argsort(np.abs(f))[6:]
    return np.sort(f[keep])


HEIGHT_TOLERANCE_CM = 0.5      # 10 Oct 2026: heights only when the shape module's positions match the listed ones (same Hessian)


def heights_for(shape: dict, listed: list[float]) -> list[float] | None:
    """Heights (km/mol) in the order of the listed B3LYP positions, or None (no APT, or positions that do not match the listed ones). A listed
    mode below the spectrum's vibrational threshold (stilbene's −4.66 cm⁻¹ torsion in the psi4 list) has no stick and gets no height."""
    if shape.get("kind") != "positions and heights":
        return None
    dev = shape.get("max_dev_from_listed_cm")
    w = np.asarray(listed, float)
    vib = np.flatnonzero(np.abs(w) > shape["vib_min_cm"])
    if dev is None or dev > HEIGHT_TOLERANCE_CM or len(shape["sticks"]) != len(vib):
        return None
    out: list[float | None] = [None] * len(listed)
    for i, s in zip(vib[np.argsort(w[vib], kind="stable")], shape["sticks"], strict=True):    # the sticks come sorted by position
        out[i] = round(float(s["km_mol"]), 3)
    return out


@dataclass(frozen=True)
class ExportSources:
    """What the export reads once besides the molecule folders."""
    manifest: list[dict]                 # every manifest row: the training pool is read against all of them, whatever a build keeps
    manifest_path: str
    ledger_path: str
    ledger: dict[str, dict]              # the done rows of the corpus ledger
    releases: dict[str, list[str]]       # the release names each molecule belongs to
    replaced: set[str]                   # molecules a release took from the analytic second route
    verdicts: dict[str, str]             # the imaginary-mode read-out of 24 Sep: healed / genuine per molecule
    screen: dict[str, dict]
    anchored: dict[str, list[str]]       # the anchor registry's evidence files per molecule
    anchor_level: dict[str, str]


@dataclass
class Tally:
    """The counts the summary states, and the invariant breaks found while the rows are exported."""
    rung_counts: dict[str, int] = field(default_factory=lambda: dict.fromkeys(RUNGS, 0))
    layer_counts: dict[str, int] = field(default_factory=dict)
    source_counts: dict[str, int] = field(default_factory=dict)
    problems: list[str] = field(default_factory=list)
    n_heights: int = 0
    n_anchor_spectra: int = 0

    def count(self, row: dict) -> None:
        """Count a finished catalogue row under its rung, layer and source."""
        self.rung_counts[row["rung_label"]] += 1
        self.layer_counts[row["layer"]] = self.layer_counts.get(row["layer"], 0) + 1
        self.source_counts[row["source"]] = self.source_counts.get(row["source"], 0) + 1


MODULE05 = os.path.join("modules", "05_support_predictor")
TAGS = ("b3lyp", "wb97x")
SECOND_ROUTE_AGREES_CM = 15     # the largest frequency difference at which the second route is said to agree
SCREEN_FLAG_CM = 80             # the corpus screen's shift above which a molecule is flagged
SHAPE_KEYS = ("n_ir_active", "apt_source", "hessian_source", "broadening", "method", "max_dev_from_listed_cm")


def _load_json(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _load_csv(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _dump_json(path: str, obj, **json_options) -> None:
    """Write `obj` to a temp file beside `path` and move it over the target."""
    part = path + ".part"
    with open(part, "w", encoding="utf-8") as f:
        json.dump(obj, f, **json_options)
    os.replace(part, path)


def select_rows(manifest: list[dict], limit: int | None, ids: set[str] | None) -> list[dict]:
    """The manifest rows a build exports: the named `ids` (an id without a row is refused), or the first `limit` rows with done rows
    and layer A (benzene, naphthalene) first, or every row."""
    if ids:
        unknown = sorted(set(ids) - {r["id"] for r in manifest})
        if unknown:
            raise ValueError(f"build: no manifest row for {unknown}")
        manifest = [r for r in manifest if r["id"] in ids]
    if limit:
        manifest = sorted(manifest, key=lambda r: (r["status"] != "done", r["layer"] != "A", r["id"]))[:limit]
    return manifest


def read_releases(plan: str) -> tuple[dict[str, list[str]], set[str]]:
    """{mol_id: [release name]} over every release manifest, and the molecules a release took from the analytic second route."""
    releases: dict[str, list[str]] = {}
    replaced: set[str] = set()
    for rp in sorted(glob.glob(os.path.join(plan, MODULE05, "data", "corpus_release", "*_manifest.json"))):
        release = _load_json(rp)
        name = os.path.basename(rp).replace("_manifest.json", "")
        for row in release["molecules"]:
            releases.setdefault(row["id"], []).append(name)
        replaced.update(release.get("analytic_second_route", []))
    return releases, replaced


def read_verdicts(second_route_dir: str) -> dict[str, str]:
    """The flag of the imaginary-mode read-out of 24 Sep per molecule: healed by the second route, or a genuine imaginary mode."""
    verdicts = {}
    for vp in sorted(glob.glob(os.path.join(second_route_dir, "imaginary_second_route_*.json"))):
        for row in _load_json(vp)["rows"]:
            v = row.get("molecule_verdict", "")
            if v.startswith("healed"):
                verdicts[row["id"]] = "second_route_healed"
            elif v.startswith("genuine"):
                verdicts[row["id"]] = "imaginary_mode_genuine"
    return verdicts


def read_screen(second_route_dir: str) -> dict[str, dict]:
    """The corpus screen of 23 Sep per molecule; empty without its file."""
    sp = os.path.join(second_route_dir, "corpus_screen_2026-09-23.json")
    return {r["id"]: r for r in _load_json(sp)["rows"]} if os.path.exists(sp) else {}


def read_sources(plan: str, corpus: str, manifest: list[dict]) -> ExportSources:
    """Everything the export reads besides the molecule folders, with every manifest row."""
    ledger_path = os.path.join(corpus, "ledger.csv")
    releases, replaced = read_releases(plan)
    second_route_dir = os.path.join(plan, MODULE05, "data", "second_route")
    anchored, anchor_level = anchored_from_registry(plan)
    return ExportSources(manifest=manifest, manifest_path=os.path.join(corpus, "manifest.csv"), ledger_path=ledger_path,
                         ledger={r["id"]: r for r in _load_csv(ledger_path) if r["status"] == "done"}, releases=releases,
                         replaced=replaced, verdicts=read_verdicts(second_route_dir), screen=read_screen(second_route_dir),
                         anchored=anchored, anchor_level=anchor_level)


def check_evidence(plan: str, anchored: dict[str, list[str]]) -> None:
    """Stop the export when an anchored or validated molecule's evidence file is missing."""
    for mid, files in [*anchored.items(), *VALIDATED.items()]:
        for f in files:
            if not os.path.exists(os.path.join(plan, f)):
                raise SystemExit(f"evidence file missing for {mid}: {f}")


def identity_row(r: dict, releases: dict[str, list[str]], computed: bool, problems: list[str]) -> dict:
    """A manifest row's catalogue entry before its rung is known: identity, size, source and release membership. A computed
    molecule whose manifest atom count differs from its SMILES is an invariant break."""
    formula, ikey, n_atoms_rd, n_heavy_rd = formula_and_key(r["smiles"])
    n_atoms = int(r["n_atoms"]) if r.get("n_atoms") else n_atoms_rd          # pending rows of layers B/C carry no atom counts yet
    n_heavy = int(r["n_heavy"]) if r.get("n_heavy") else n_heavy_rd
    if computed and n_atoms_rd is not None and n_atoms != n_atoms_rd:
        problems.append(f"{r['id']}: manifest n_atoms {n_atoms} differs from the SMILES count {n_atoms_rd}")
    return dict(id=r["id"], name=r["name"], smiles=r["smiles"], formula=formula, inchikey=ikey, layer=r["layer"], source=source_of(r),
                n_heavy=n_heavy, n_atoms=n_atoms, rung=0, rung_label="listed", flags=[], releases=releases.get(r["id"], []),
                manifest_status=r["status"])


def flags_of(mid: str, n_imaginary: dict[str, int], second: dict | None, sources: ExportSources) -> list[str]:
    """A computed molecule's flags: its imaginary modes' verdict, its second route's agreement, a release's replacement, the screen."""
    flags = []
    if any(n_imaginary.values()):
        flags.append(sources.verdicts.get(mid, "imaginary_mode_under_review"))
    if second is not None:
        worst = max(v["max_abs_dfreq_cm"] for v in second.values())
        flags.append("second_route_agrees" if worst <= SECOND_ROUTE_AGREES_CM else "second_route_disagrees")
    if mid in sources.replaced:
        flags.append("replaced_by_second_route")
    if mid in sources.screen and sources.screen[mid]["max_abs_shift"] > SCREEN_FLAG_CM:
        flags.append("screen_flagged")
    return flags


def frequency_lists(mdir: str, n_atoms: int, mid: str, problems: list[str]) -> dict[str, dict]:
    """Per functional every listed frequency and the vibrational ones; a list whose length is not 3N is an invariant break."""
    from m08 import spectrum
    lists = {}
    for tag in TAGS:
        with np.load(spectrum.listed_hessian(Path(mdir), tag)) as z:
            fr = np.asarray(z["freq_cm"], float)
        if len(fr) != 3 * n_atoms:
            problems.append(f"{mid}: {tag} frequency list has {len(fr)} entries, 3N = {3 * n_atoms}")
        lists[tag] = dict(all=fr.round(2).tolist(), vibrational=vib_only(fr).round(2).tolist())
    return lists


def attach_heights(mol: dict, row: dict, tally: Tally) -> None:
    """The band heights of the B3LYP positions from module 08's shape module, or the reason there are none; an APT whose positions
    do not match the listed ones is an invariant break."""
    from m08 import spectrum
    listed = mol["frequencies_cm"]["b3lyp"]["vibrational"]
    sh = spectrum.shape(mol["id"], listed)
    heights = heights_for(sh, listed)
    if heights is not None:
        mol["intensities_km_mol"] = {"b3lyp": heights}
        mol["shape"] = {k: sh[k] for k in SHAPE_KEYS}
        row["has_intensities"] = True
        tally.n_heights += 1
    elif sh.get("kind") == "positions and heights":
        tally.problems.append(f"{mol['id']}: APT present but its positions do not match the listed ones ({sh.get('max_dev_from_listed_cm')} cm⁻¹)")
    else:
        mol["heights_missing"] = sh["reason"]


def attach_anchor_spectrum(mol: dict, tally: Tally) -> None:
    """TASKS 45: an anchored molecule's page leads with the best spectrum it has, the anchor's, with its comparison and test prediction."""
    from m08 import spectrum
    mid = mol["id"]
    an = spectrum.anchor_series(mid)
    if an is not None:
        mol["anchor_spectrum"] = an
        mol["comparison"] = spectrum.comparison(mid, an)
        mol["test_prediction"] = spectrum.test_prediction(mid, an)
        tally.n_anchor_spectra += 1


def export_molecule(row: dict, mdir: str, sources: ExportSources, tally: Tally, out: str) -> None:
    """A computed molecule: its row reaches rung 1 with its flags, and molecules/<id>.json is written. A missing Hessian is an
    invariant break and nothing is written for the molecule."""
    from m08 import spectrum
    mid = row["id"]
    res = _load_json(os.path.join(mdir, "result.json"))
    analytic_only = spectrum.analytic_only(Path(mdir))
    missing = [tag for tag in TAGS if not spectrum.listed_hessian(Path(mdir), tag).exists()]
    if missing:
        tally.problems.extend(f"{mid}: computed but no {tag} Hessian" for tag in missing)
        return
    row["rung"] = 1
    n_imaginary = {tag: int(res.get(f"n_imaginary_{tag}", 0)) for tag in TAGS}
    second = second_route_of(mdir, analytic_only)
    row["flags"] = flags_of(mid, n_imaginary, second, sources)
    mol = dict(id=mid, name=row["name"], smiles=row["smiles"], formula=row["formula"], layer=row["layer"], source=row["source"],
               n_atoms=row["n_atoms"], geometry=_load_json(os.path.join(mdir, "geometry.json")), deck=deck_of(res, mdir, analytic_only),
               timings_s=res.get("timings_s"), energies=dict(b3lyp=res.get("e_b3lyp"), wb97x=res.get("e_wb97x")), n_imaginary=n_imaginary,
               frequencies_cm=frequency_lists(mdir, row["n_atoms"], mid, tally.problems), releases=sources.releases.get(mid, []),
               ledger=sources.ledger.get(mid), second_route=None, intensities_km_mol=None, shape=None, heights_missing=None,
               predicted_spectrum=None, anchor_spectrum=None, comparison=None, test_prediction=None)
    attach_heights(mol, row, tally)
    if mid in sources.anchored:
        attach_anchor_spectrum(mol, tally)
    mol["second_route"] = second
    _dump_json(os.path.join(out, "molecules", mid + ".json"), mol, ensure_ascii=False)


def place_on_rung(row: dict, sources: ExportSources) -> None:
    """An anchored molecule is on rung 4 with the registry's evidence, a validated one on rung 5; the label follows the rung."""
    mid = row["id"]
    if mid in sources.anchored:
        row["rung"] = 4
        row["evidence"] = sources.anchored[mid]
        row["anchor_level"] = sources.anchor_level[mid]
    if mid in VALIDATED:
        row["rung"] = 5
        row["evidence"] = sources.anchored.get(mid, []) + VALIDATED[mid]
    row["rung_label"] = RUNGS[row["rung"]]


def catalog_entry(r: dict, corpus: str, sources: ExportSources, tally: Tally, out: str) -> dict:
    """One manifest row's catalogue entry, counted; a computed molecule's file is written on the way."""
    mdir = os.path.join(corpus, "molecules", r["id"])
    computed = r["status"] == "done" and os.path.exists(os.path.join(mdir, "result.json"))
    row = identity_row(r, sources.releases, computed, tally.problems)
    if computed:
        export_molecule(row, mdir, sources, tally, out)
    place_on_rung(row, sources)
    tally.count(row)
    return row


def check_invariants(manifest: list[dict], catalog: list[dict], tally: Tally) -> None:
    """Stop the export (exit 1, each break on stderr) when an invariant broke on the way or the catalogue does not add up."""
    kept = {r["id"] for r in manifest}
    if any(row["id"] not in kept for row in catalog):
        tally.problems.append("catalog id without a manifest row")
    if sum(tally.rung_counts.values()) != len(catalog):
        tally.problems.append("rung counts do not add up")
    if tally.problems:
        for p in tally.problems:
            print("INVARIANT:", p, file=sys.stderr)
        raise SystemExit(1)


def summary_of(catalog: list[dict], tally: Tally, sources: ExportSources, n_changelog: int) -> dict:
    """The summary: counts, data freshness, source hashes, the carried network's accuracy (decision 65), licence and network pair."""
    from m08 import pipeline
    from m08.accuracy import HIGHER_LEVEL_NAME, carried_accuracy
    from m08.licence import state as licence_state
    accuracy = carried_accuracy()
    licence = licence_state(accuracy)
    return dict(built_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), n_molecules=len(catalog), rung_counts=tally.rung_counts,
                layer_counts=tally.layer_counts, source_counts=tally.source_counts, rungs=RUNGS,
                sources=dict(manifest=sha256(sources.manifest_path), ledger=sha256(sources.ledger_path)),
                releases=sorted({n for v in sources.releases.values() for n in v}), n_changelog=n_changelog, n_with_intensities=tally.n_heights,
                n_anchor_spectra=tally.n_anchor_spectra, shape_accuracy=accuracy,
                licence={k: licence[k] for k in ("licensed_families", "statement", "rule_source")} | {"line_cm": licence_line(accuracy)},
                higher_level_name=HIGHER_LEVEL_NAME, networks=network_pair(pipeline, sources.manifest))


# Imported in this order before the first row: importing m08.pipeline puts module 05's code on sys.path, which m08.spectrum's anchor
# series loads from (a deferred import made the split of build() fail there).
MODULE08_IMPORTS = ("m08.spectrum", "m08.accuracy", "m08.licence", "m08.pipeline")


def import_module08(plan: str) -> None:
    """Put module 08 on the path and import the parts the export uses. TASKS 44: module 08 holds the one implementation of the heights."""
    sys.path.insert(0, os.path.join(plan, "modules", "08_industry_synthesis"))
    for name in MODULE08_IMPORTS:
        importlib.import_module(name)


def build(repo: str, out: str, limit: int | None = None, ids: set[str] | None = None) -> dict:
    """Export the catalogue to `out`. `limit` keeps the first N rows (layer A first); `ids` keeps the named manifest rows (an id without
    a row is refused); the two do not combine."""
    if limit and ids:
        raise ValueError("build: give limit or ids, not both")
    plan = os.path.join(repo, "plans", "05_delta-probed-ir-pipeline")
    corpus = os.path.join(plan, MODULE05, "corpus")
    import_module08(plan)
    manifest_all = _load_csv(os.path.join(corpus, "manifest.csv"))
    manifest = select_rows(manifest_all, limit, ids)
    sources = read_sources(plan, corpus, manifest_all)
    check_evidence(plan, sources.anchored)
    os.makedirs(os.path.join(out, "molecules"), exist_ok=True)
    tally = Tally()
    catalog = [catalog_entry(r, corpus, sources, tally, out) for r in manifest]
    check_invariants(manifest, catalog, tally)
    _dump_json(os.path.join(out, "catalog.json"), catalog, ensure_ascii=False)
    changelog = read_changelog(os.path.join(plan, "GoalGathering", "notes", "Mandate_2026-09-13_Affordable_Plan_Obstacle_Ledger.md"))
    _dump_json(os.path.join(out, "changelog.json"), changelog, ensure_ascii=False, indent=0)
    summary = summary_of(catalog, tally, sources, len(changelog))
    _dump_json(os.path.join(out, "summary.json"), summary, indent=1)
    return summary


def main() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=os.path.abspath(os.path.join(here, "..", "..")))
    ap.add_argument("--out", default=os.path.join(here, "out"))
    ap.add_argument("--limit", type=int)
    a = ap.parse_args()
    summary = build(a.repo, a.out, a.limit)
    print(json.dumps({k: v for k, v in summary.items() if k != "sources"}, indent=1))


if __name__ == "__main__":
    main()
