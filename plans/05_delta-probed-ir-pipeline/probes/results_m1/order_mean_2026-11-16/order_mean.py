"""Does the mean of ΔH over K presentations of one molecule make aromir's answer better, or only stable? (TASKS 238)

A presentation is the same molecule listed in another atom order, turned by a proper rotation and optionally mirrored, geometry and
B3LYP Hessian transformed together. The release's seed-mean ΔH is computed in the presentation and mapped back to the stored frame and
order; the mean over K mapped-back ΔH is applied to the stored B3LYP Hessian and its band positions are read against the stored ωB97X
labels, per family, on hold-outs (a) and (b):

    python order_mean.py <plan folder> <out folder> [--smoke]

The layer called is `Release.corrections(geometry, hessian)` on the presentation as given, as `product_error.py` does: below
`aromir.geometry.canonical_order`, which the front door applies to an input before the network sees it. A uniform random permutation
is therefore an order no user of the front door produces; the kind `front_door` is the order `canonical_order` gives a shuffled xyz
listing of the molecule (the orders a user's input can reach), with a rotation and the mirror image half the time.

`load`, `rms` and `bootstrap` are copied verbatim from `probes/results_m1/aromir_product_error_2026-11-16/product_error.py` (that
script runs on import and cannot be imported); `band_errors` is the band part of its `molecule_errors` for a given ΔH.
No quantum chemistry is run.
"""
from __future__ import annotations

import argparse
import csv
import json
import multiprocessing
import pickle
import sys
import tempfile
import time
import zlib
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
from aromir import admission, families, release, spectrum, vibrations
from aromir import geometry as aromir_geometry
from aromir.constants import ANGSTROM_PER_BOHR
from aromir.errors import RefusedError
from aromir.molecule import Geometry

KS = (1, 4, 16, 64)
KINDS = ("permutation", "rotation_mirror", "all", "front_door")
MAIN_KIND = "all"
WORKERS = 2
MAX_REFUSED_LISTINGS = 200
N_SETS = 2
SETS = ("a8", "b")
FAMILIES = families.FAMILIES
BASE_SEED = 20261116
ROUND_TRIP_TOLERANCE = 1e-12
REFERENCE_TOLERANCE_CM = 0.01
# the product's error in the stored order and frame (product_error.txt, 16 Nov 2026), which this script must reproduce
REFERENCE = {"a8": (1.43, 0.95, 1.64, 2.78), "b": (1.91, 2.19, 1.88, 2.77)}
BENZENE = "A_8448043181"
BIPHENYL = "A_fdc27f1bd1"
EXTRA = ("A_3100da3761",)   # benzonitrile: not in the clean eight, read as a labelled case outside the pooled numbers
N_WORST = 3


@dataclass(frozen=True)
class Config:
    """Where the corpus is, where the record goes, and how much is read."""

    plan: Path
    out: Path
    smoke: bool

    @property
    def m05(self) -> Path:
        return self.plan / "modules" / "05_support_predictor"

    @property
    def ks(self) -> tuple[int, ...]:
        return KS[:2] if self.smoke else KS

    @property
    def stem(self) -> str:
        return "order_mean_smoke" if self.smoke else "order_mean"


@dataclass(frozen=True, eq=False)
class Presentation:
    """Atom `order[k]` of the stored molecule in position k, coordinates x → x Qᵀ with Q orthogonal (det −1: a mirror image)."""

    order: np.ndarray
    q: np.ndarray
    refused_listings: int = 0   # front door only: shuffled listings aromir refused before it accepted this one

    @property
    def index(self) -> np.ndarray:
        return (3 * self.order[:, None] + np.arange(3)).ravel()

    def big(self) -> np.ndarray:
        return np.kron(np.eye(len(self.order)), self.q)


@dataclass(frozen=True, eq=False)
class Molecule:
    """One stored molecule with what every read of it shares."""

    molecule_id: str
    geometry: Geometry
    h_low: np.ndarray
    low: vibrations.Modes
    ref: vibrations.Modes
    family: np.ndarray


def stop(reason: str) -> None:
    print(f"STOP: {reason}", flush=True)
    raise SystemExit(1)


def aromir_symbol(symbol: str) -> str:
    """An element symbol as aromir's table keys it ('Cl'); the corpus writes 'CL' (as `probes/aromir_common.py`)."""
    return symbol[0].upper() + symbol[1:].lower()


def load(corpus: Path, molecule_id: str) -> tuple[Geometry, np.ndarray, np.ndarray]:
    """The stored geometry and the two analytic label Hessians of one corpus molecule."""
    folder = corpus / molecule_id
    stored = json.loads((folder / "geometry.json").read_text(encoding="utf-8"))
    geometry = Geometry(tuple(aromir_symbol(s) for s in stored["symbols"]), np.array(stored["coords_bohr"], float))
    hessians = []
    for level in ("b3lyp", "wb97x"):
        with np.load(folder / f"hessian_{level}_analytic.npz") as z:
            hessians.append(np.array(z["H_projected"], float))
    return geometry, hessians[0], hessians[1]


def rms(parts: list[np.ndarray]) -> float | None:
    values = np.concatenate(parts) if parts else np.array([])
    return float(np.sqrt(np.mean(values**2))) if values.size else None


def bootstrap(per_molecule_errors: list[np.ndarray], line: float = 3.0, draws: int = 4000) -> dict:
    """The set's rms under resampling of whole molecules (modes of one molecule are not independent): the 2.5th and 97.5th percentile
    and the share of draws below the licence line. Seeded; a statement about this hold-out's molecules as a sample, nothing more."""
    rng = np.random.default_rng(20261116)
    sums = np.array([float(np.sum(e**2)) for e in per_molecule_errors])
    counts = np.array([len(e) for e in per_molecule_errors], float)
    picks = rng.integers(0, len(sums), size=(draws, len(sums)))
    drawn = np.sqrt(sums[picks].sum(axis=1) / np.maximum(counts[picks].sum(axis=1), 1.0))
    return {"p2.5": float(np.percentile(drawn, 2.5)), "p97.5": float(np.percentile(drawn, 97.5)),
            "share_below_line": float(np.mean(drawn < line)), "line": line, "draws": draws,
            "largest_single_molecule_rms": float(np.sqrt(np.max(sums / np.maximum(counts, 1.0))))}


def paired_bootstrap(errors: list[np.ndarray], baseline: list[np.ndarray], draws: int = 4000) -> dict:
    """The set's rms minus the baseline's under the same resampling of whole molecules: the interval of the difference."""
    rng = np.random.default_rng(20261116)
    picks = rng.integers(0, len(errors), size=(draws, len(errors)))
    drawn = []
    for part in (errors, baseline):
        sums = np.array([float(np.sum(e**2)) for e in part])
        counts = np.array([len(e) for e in part], float)
        drawn.append(np.sqrt(sums[picks].sum(axis=1) / np.maximum(counts[picks].sum(axis=1), 1.0)))
    difference = drawn[0] - drawn[1]
    return {"p2.5": float(np.percentile(difference, 2.5)), "p97.5": float(np.percentile(difference, 97.5)),
            "share_of_draws_worse": float(np.mean(difference > 0))}


def random_rotation(rng: np.random.Generator) -> np.ndarray:
    """A proper rotation, uniform over the rotation group (QR of a normal matrix, signs fixed)."""
    q, r = np.linalg.qr(rng.normal(size=(3, 3)))
    q = q * np.sign(np.diag(r))
    if np.linalg.det(q) < 0:
        q[:, 0] = -q[:, 0]
    return q


def front_door_order(geometry: Geometry, rng: np.random.Generator, scratch: Path) -> tuple[np.ndarray, int]:
    """The atom order aromir gives the molecule when its xyz file lists the atoms in a shuffled order, as indices of the stored
    order; and how many shuffled listings aromir refused first (its bond perception depends on the listing)."""
    path = scratch / "molecule.xyz"
    for refused in range(MAX_REFUSED_LISTINGS):
        shuffle = rng.permutation(geometry.n_atoms)
        lines = [str(geometry.n_atoms), "order_mean"]
        for k in shuffle:
            x, y, z = geometry.coords_bohr[k] * ANGSTROM_PER_BOHR
            lines.append(f"{geometry.symbols[k]} {x:.10f} {y:.10f} {z:.10f}")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        try:
            return shuffle[np.array(aromir_geometry.canonical_order(admission.parse_xyz(path)))], refused
        except RefusedError:
            continue
    raise RuntimeError(f"aromir refused {MAX_REFUSED_LISTINGS} shuffled xyz listings in a row")


def draw(kind: str, geometry: Geometry, rng: np.random.Generator, scratch: Path) -> Presentation:
    """One presentation of its kind: a uniform permutation; a uniform rotation with a mirror image half the time; both; or the
    front door's order of a shuffled listing with the rotation and the mirror image."""
    if kind not in KINDS:
        raise ValueError(f"{kind} is not one of {KINDS}")
    refused = 0
    if kind == "front_door":
        order, refused = front_door_order(geometry, rng, scratch)
    else:
        order = np.arange(geometry.n_atoms) if kind == "rotation_mirror" else rng.permutation(geometry.n_atoms)
    if kind == "permutation":
        return Presentation(order, np.eye(3))
    q = random_rotation(rng)
    if rng.random() < 0.5:   # a fair coin: the mirror image half the time
        q = q @ np.diag([1.0, 1.0, -1.0])
    return Presentation(order, q, refused)


def presentations(molecule_id: str, geometry: Geometry, kind: str, set_index: int, count: int) -> list[Presentation]:
    """The seeded sequence of a molecule's presentations: the first K are the K-set, so each K-set holds the smaller ones."""
    rng = np.random.default_rng([BASE_SEED, zlib.crc32(molecule_id.encode()), KINDS.index(kind), set_index])
    with tempfile.TemporaryDirectory() as scratch:
        return [draw(kind, geometry, rng, Path(scratch)) for _ in range(count)]


def present(geometry: Geometry, hessian: np.ndarray, p: Presentation) -> tuple[Geometry, np.ndarray]:
    """The molecule and a Hessian of it as the presentation lists and places them."""
    big = p.big()
    moved = Geometry(tuple(geometry.symbols[k] for k in p.order), geometry.coords_bohr[p.order] @ p.q.T)
    return moved, big @ hessian[np.ix_(p.index, p.index)] @ big.T


def map_back(matrix: np.ndarray, p: Presentation) -> np.ndarray:
    """A (3N, 3N) matrix given in the presentation, in the stored frame and atom order."""
    big = p.big()
    out = np.empty_like(matrix)
    out[np.ix_(p.index, p.index)] = big.T @ matrix @ big
    return out


def band_errors(molecule: Molecule, delta: np.ndarray) -> dict[str, np.ndarray]:
    """The corrected bands of the stored Hessian plus ΔH: each band's error against its reference partner and its family."""
    corrected = vibrations.vibrational_modes(molecule.h_low + delta, molecule.geometry)
    to_ref = spectrum.partners(corrected, molecule.ref)
    to_low = spectrum.partners(corrected, molecule.low)
    return {"band": corrected.wavenumbers - molecule.ref.wavenumbers[to_ref], "family": molecule.family[to_low],
            "wavenumbers": corrected.wavenumbers}


def prepared(corpus: Path, molecule_id: str) -> Molecule:
    geometry, h_low, h_ref = load(corpus, molecule_id)
    low = vibrations.vibrational_modes(h_low, geometry)
    ref = vibrations.vibrational_modes(h_ref, geometry)
    return Molecule(molecule_id, geometry, h_low, low, ref, np.array(families.classify(geometry, low)))


def round_trip_check(corpus: Path, rel: release.Release) -> dict:
    """On benzene, eight presentations of every kind: the B3LYP Hessian presented and mapped back must be the stored one to 1e-12;
    its wavenumbers must not depend on the presentation; and the bands corrected inside the presentation must equal the bands of
    the stored Hessian plus the mapped-back ΔH (the mapping of ΔH itself)."""
    molecule = prepared(corpus, BENZENE)
    worst = {"hessian_round_trip_max_abs": 0.0, "b3lyp_wavenumbers_max_cm": 0.0, "corrected_in_frame_vs_mapped_back_max_cm": 0.0}
    for kind in KINDS:
        for p in presentations(BENZENE, molecule.geometry, kind, 0, 8):
            moved, h_moved = present(molecule.geometry, molecule.h_low, p)
            delta_moved = rel.corrections(moved, h_moved).mean
            in_frame = vibrations.vibrational_modes(h_moved + delta_moved, moved).wavenumbers
            back = vibrations.vibrational_modes(molecule.h_low + map_back(delta_moved, p), molecule.geometry).wavenumbers
            found = (np.abs(map_back(h_moved, p) - molecule.h_low).max(),
                     np.abs(vibrations.vibrational_modes(h_moved, moved).wavenumbers - molecule.low.wavenumbers).max(),
                     np.abs(in_frame - back).max())
            worst = {name: max(old, float(new)) for (name, old), new in zip(worst.items(), found, strict=True)}
    if worst["hessian_round_trip_max_abs"] > ROUND_TRIP_TOLERANCE:
        stop(f"the round trip of benzene's B3LYP Hessian is off by {worst['hessian_round_trip_max_abs']:.2e}")
    return {"molecule": BENZENE, "presentations": 8 * len(KINDS), "tolerance": ROUND_TRIP_TOLERANCE, **worst}


def mapped_deltas(molecule: Molecule, plist: list[Presentation], rel: release.Release) -> tuple[list[np.ndarray], float]:
    """The release's seed-mean ΔH in every presentation, mapped back; and the seconds the network calls took."""
    deltas = []
    started = time.perf_counter()
    for p in plist:
        moved, h_moved = present(molecule.geometry, molecule.h_low, p)
        if np.abs(map_back(h_moved, p) - molecule.h_low).max() > ROUND_TRIP_TOLERANCE:
            stop(f"{molecule.molecule_id}: the round trip of the B3LYP Hessian is not exact")
        deltas.append(map_back(rel.corrections(moved, h_moved).mean, p))
    return deltas, time.perf_counter() - started


def drawn(molecule: Molecule, count: int) -> dict[str, list[list[Presentation]]]:
    """Every presentation of one molecule, per kind and set."""
    return {kind: [presentations(molecule.molecule_id, molecule.geometry, kind, set_index, count) for set_index in range(N_SETS)]
            for kind in KINDS}


def read_presented(job: tuple[Molecule, tuple[int, ...], dict[str, list[list[Presentation]]]]) -> tuple[dict, float]:
    """Every read of one molecule: per kind and set the K-means' bands, and every single presentation's errors pooled.
    Runs in a worker process, which holds the release its parent loaded."""
    molecule, ks, plan = job
    rel = _WORKER_RELEASE[0]
    reads: dict = {}
    seconds = 0.0
    for kind in KINDS:
        singles = []
        orders = set()
        for set_index, plist in enumerate(plan[kind]):
            orders |= {tuple(p.order.tolist()) for p in plist}
            deltas, spent = mapped_deltas(molecule, plist, rel)
            seconds += spent
            for k in ks:
                reads[f"{kind}/set{set_index}/K{k}"] = band_errors(molecule, np.mean(deltas[:k], axis=0))
            singles += [band_errors(molecule, delta) for delta in deltas]
        reads[f"{kind}/singles"] = {"band": np.concatenate([s["band"] for s in singles]),
                                    "family": np.concatenate([s["family"] for s in singles]), "n_orders": len(orders),
                                    "refused_listings": sum(p.refused_listings for plist in plan[kind] for p in plist)}
    return reads, seconds


# the release of the worker processes: loaded once by the parent before the pool forks, so its weights are shared pages
_WORKER_RELEASE: list[release.Release] = []


def per_family(read: dict) -> dict:
    out = {fam: {"rms": rms([read["band"][read["family"] == fam]]), "n": int((read["family"] == fam).sum())} for fam in FAMILIES}
    out["all"] = {"rms": rms([read["band"]]), "n": len(read["band"])}
    return out


def pooled(rows: list[dict], label: str) -> dict:
    """One estimate on one hold-out, per family: the rms over all bands, the molecule-level interval, the difference to stored."""
    table = {}
    for fam in FAMILIES:
        parts = [r[label]["band"][r[label]["family"] == fam] for r in rows]
        stored = [r["stored"]["band"][r["stored"]["family"] == fam] for r in rows]
        table[fam] = {"rms": rms(parts), "n_bands": int(sum(len(p) for p in parts)), "bootstrap": bootstrap(parts),
                      "minus_stored": paired_bootstrap(parts, stored)}
    return table


def stability(rows: list[dict], kind: str, k: int) -> dict:
    """Two independent K-sets per molecule: the difference between their corrected band positions, in ascending order."""
    gaps = [r[f"{kind}/set0/K{k}"]["wavenumbers"] - r[f"{kind}/set1/K{k}"]["wavenumbers"] for r in rows]
    return {"max_cm": float(max(np.abs(g).max() for g in gaps)), "rms_cm": rms(gaps),
            "per_molecule_max_cm": [float(np.abs(g).max()) for g in gaps]}


def summarise(rows: list[dict], ks: tuple[int, ...]) -> dict:
    labels = ["stored"] + [f"{kind}/set{s}/K{k}" for kind in KINDS for s in range(N_SETS) for k in ks]
    labels += [f"{kind}/singles" for kind in KINDS]
    return {"error": {label: pooled(rows, label) for label in labels},
            "stability": {kind: {f"K{k}": stability(rows, kind, k) for k in ks} for kind in KINDS}}


def molecule_record(molecule: Molecule, reads: dict, seconds: float, smiles: str, ks: tuple[int, ...]) -> dict:
    calls = len(KINDS) * N_SETS * max(ks)
    return {"id": molecule.molecule_id, "smiles": smiles, "n_atoms": molecule.geometry.n_atoms,
            "triple_bond": "#" in smiles, "seconds_per_correction": seconds / calls,
            "distinct_orders_of_128": {kind: reads[f"{kind}/singles"]["n_orders"] for kind in KINDS},
            "front_door_refused_listings": reads["front_door/singles"]["refused_listings"],
            "error": {label: per_family(read) for label, read in reads.items()},
            "stability_max_cm": {kind: {f"K{k}": float(np.abs(reads[f"{kind}/set0/K{k}"]["wavenumbers"]
                                                              - reads[f"{kind}/set1/K{k}"]["wavenumbers"]).max()) for k in ks}
                                 for kind in KINDS}}


def reference_check(stored_rows: dict[str, list[dict]]) -> dict:
    """The stored order and frame must give the product's error as measured on 16 Nov, to 0.01 cm⁻¹ per family and hold-out."""
    found = {}
    for key, rows in stored_rows.items():
        found[key] = [rms([r["stored"]["band"][r["stored"]["family"] == fam] for r in rows]) for fam in FAMILIES]
        for fam, value, expected in zip(FAMILIES, found[key], REFERENCE[key], strict=True):
            if abs(round(value, 2) - expected) > REFERENCE_TOLERANCE_CM + 1e-9:
                stop(f"hold-out {key}, {fam}: {value:.3f} cm-1 in the stored presentation, the reference is {expected:.2f}")
    return {"found": found, "expected": {key: list(REFERENCE[key]) for key in found}, "tolerance_cm": REFERENCE_TOLERANCE_CM}


def worst_cases(records: dict[str, dict], top_label: str) -> list[dict]:
    """The molecules whose error over all bands changes most between the stored presentation and the largest K-mean."""
    changes = [{"id": mid, "stored": rec["error"]["stored"]["all"]["rms"], "k_mean": rec["error"][top_label]["all"]["rms"]}
               for mid, rec in records.items() if mid not in EXTRA]
    for row in changes:
        row["change"] = row["k_mean"] - row["stored"]
    return sorted(changes, key=lambda row: -abs(row["change"]))[:N_WORST]


def fmt(value: float | None) -> str:
    return "    -" if value is None else f"{value:5.2f}"


def error_lines(summary: dict, ks: tuple[int, ...]) -> list[str]:
    lines = []
    rows = [("K=1 stored", "stored")]
    for kind in KINDS:
        rows.append((f"{kind}: K=1, all 128 singles", f"{kind}/singles"))
        rows += [(f"{kind}: K={k}, set {s}", f"{kind}/set{s}/K{k}") for k in ks for s in range(N_SETS)]
    lines.append(f"  {'estimate':38s}" + "".join(f"{fam:>22s}" for fam in FAMILIES))
    for name, label in rows:
        cells = [f"{fmt(e['rms'])} ({e['bootstrap']['p2.5']:.2f}-{e['bootstrap']['p97.5']:.2f})"
                 for e in (summary["error"][label][fam] for fam in FAMILIES)]
        lines.append(f"  {name:38s}" + "".join(f"{c:>22s}" for c in cells))
    for kind in KINDS:
        cells = [f"{e['p2.5']:+.2f}..{e['p97.5']:+.2f} ({e['share_of_draws_worse']:.2f})"
                 for e in (summary["error"][f"{kind}/set0/K{max(ks)}"][fam]["minus_stored"] for fam in FAMILIES)]
        lines.append(f"  {kind + ' K=' + str(max(ks)) + ' minus stored (share worse)':38s}" + "".join(f"{c:>22s}" for c in cells))
    lines.append("  stability, two independent K-sets, corrected bands: max / rms cm-1")
    for kind in KINDS:
        cells = [f"K={k}: {summary['stability'][kind][f'K{k}']['max_cm']:.2f} / {summary['stability'][kind][f'K{k}']['rms_cm']:.3f}"
                 for k in ks]
        lines.append(f"    {kind:18s}" + "   ".join(cells))
    return lines


def molecule_lines(rec: dict, ks: tuple[int, ...]) -> list[str]:
    lines = [f"  {rec['id']} {rec['smiles']} (n={rec['n_atoms']}; distinct front-door orders "
             f"{rec['distinct_orders_of_128']['front_door']}, refused listings {rec['front_door_refused_listings']})"]
    for kind in (MAIN_KIND, "front_door"):
        top = f"{kind}/set0/K{max(ks)}"
        cells = [f"{fam} {fmt(rec['error']['stored'][fam]['rms'])}>{fmt(rec['error'][top][fam]['rms'])}"
                 for fam in (*FAMILIES, "all")]
        spread = " ".join(f"K{k} {rec['stability_max_cm'][kind][f'K{k}']:.2f}" for k in ks)
        lines.append(f"    {kind:10s} stored>K{max(ks)} " + "  ".join(cells) + f" | spread {spread}")
    return lines


def tables(record: dict, ks: tuple[int, ...]) -> str:
    check = record["round_trip_check"]
    lines = [f"order_mean: aromir {record['aromir']}, release {record['release']}",
             f"round trip on benzene, {check['presentations']} presentations: B3LYP Hessian max abs "
             f"{check['hessian_round_trip_max_abs']:.2e} (tolerance {check['tolerance']:.0e}); B3LYP wavenumbers "
             f"{check['b3lyp_wavenumbers_max_cm']:.2e} cm-1; corrected in frame vs mapped back "
             f"{check['corrected_in_frame_vs_mapped_back_max_cm']:.2e} cm-1",
             f"largest round-trip error of any presentation in the run: below {ROUND_TRIP_TOLERANCE:.0e} (checked on every one)"]
    for key, summary in record["sets"].items():
        lines.append(f"\n=== hold-out {key}: {summary['n_molecules']} molecules; rms cm-1 (95 % interval over molecules)")
        lines += error_lines(summary, ks)
    lines.append(f"\n=== the {N_WORST} molecules whose error changes most, stored against the K={max(ks)} mean (all three)")
    for row in record["worst_cases"]:
        lines += molecule_lines(record["molecules"][row["id"]], ks)
    lines.append("=== named cases: biphenyl, benzonitrile (outside the pooled numbers), every hold-out molecule with a triple bond")
    for mid in record["named_cases"]:
        lines += molecule_lines(record["molecules"][mid], ks)
    refused = {mid: rec["front_door_refused_listings"] for mid, rec in record["molecules"].items()
               if rec["front_door_refused_listings"]}
    lines.append(f"\nshuffled xyz listings aromir's front door refused before 128 were accepted, per molecule: {refused}")
    lines.append(f"seconds per correction (three seeds, one presentation, one thread, {WORKERS} processes side by side): "
                 f"median {record['seconds_per_correction_median']:.3f}, "
                 f"largest {record['seconds_per_correction_max']:.3f}; wall {record['wall_seconds']:.0f} s")
    return "\n".join(lines) + "\n"


def write(path: Path, text: str) -> None:
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(text, encoding="utf-8")
    temp.replace(path)


def all_reads(config: Config, molecules: list[Molecule], rel: release.Release) -> dict[str, tuple[dict, float]]:
    """Every molecule's reads. All presentations are drawn before the first network call, so a molecule the front door cannot
    present stops the run at once; each molecule's reads are kept in a file, so a stopped run resumes where it was."""
    partial = config.out / f"{config.stem}_partial"
    partial.mkdir(exist_ok=True)
    tag = {"ks": config.ks, "kinds": KINDS, "base_seed": BASE_SEED, "n_sets": N_SETS}
    done: dict[str, tuple[dict, float]] = {}
    for molecule in molecules:
        path = partial / f"{molecule.molecule_id}.pkl"
        if path.is_file():
            kept = pickle.loads(path.read_bytes())   # this script's own file, written below
            if kept["tag"] != tag:
                stop(f"{path} was made with other settings: {kept['tag']}")
            done[molecule.molecule_id] = kept["result"]
    pending = [m for m in molecules if m.molecule_id not in done]
    print(f"kept from an earlier run: {len(done)} molecules; to read: {len(pending)}", flush=True)
    jobs = [(m, config.ks, drawn(m, max(config.ks))) for m in pending]
    print(f"every presentation drawn: {len(jobs)} molecules", flush=True)
    _WORKER_RELEASE.append(rel)
    with multiprocessing.get_context("fork").Pool(WORKERS) as pool:
        for molecule, result in zip(pending, pool.imap(read_presented, jobs), strict=True):
            path = partial / f"{molecule.molecule_id}.pkl"
            temp = path.with_suffix(".tmp")
            temp.write_bytes(pickle.dumps({"tag": tag, "result": result}))
            temp.replace(path)
            done[molecule.molecule_id] = result
            print(f"order-mean {len(done)}/{len(molecules)} {molecule.molecule_id} {result[1]:.0f} s in the network", flush=True)
    return done


def holdout_ids(config: Config) -> dict[str, list[str]]:
    source = json.loads((config.m05 / "out" / "E7_rungC_chain35_analytic_a8read_seed0.json").read_text(encoding="utf-8"))
    ids = {key: list(source[key]["per_molecule"]) for key in SETS}
    return {key: value[:1] for key, value in ids.items()} if config.smoke else ids


def smiles_by_id(config: Config) -> dict[str, str]:
    with (config.m05 / "corpus" / "manifest.csv").open(encoding="utf-8", newline="") as handle:
        return {row["id"]: row["smiles"] for row in csv.DictReader(handle)}


def run(config: Config) -> dict:
    started = time.perf_counter()
    corpus = config.m05 / "corpus" / "molecules"
    rel = release.load(release.bundled())
    record: dict = {"aromir": str(Path(release.__file__).parent), "release": rel.network_version, "ks": list(config.ks),
                    "kinds": list(KINDS), "base_seed": BASE_SEED, "round_trip_check": round_trip_check(corpus, rel)}
    print(f"round trip on benzene: {record['round_trip_check']}", flush=True)
    ids = holdout_ids(config)
    todo = {key: [prepared(corpus, mid) for mid in members] for key, members in ids.items()}
    todo["extra"] = [prepared(corpus, mid) for mid in EXTRA]
    rows = {key: [{"stored": band_errors(m, rel.corrections(m.geometry, m.h_low).mean)} for m in members]
            for key, members in todo.items()}
    if not config.smoke:
        record["reference_check"] = reference_check({key: rows[key] for key in SETS})
        print(f"reference row reproduced: {record['reference_check']['found']}", flush=True)
    smiles = smiles_by_id(config)
    flat = [(key, molecule, row) for key, members in todo.items() for molecule, row in zip(members, rows[key], strict=True)]
    record["molecules"] = {}
    results = all_reads(config, [molecule for _, molecule, _ in flat], rel)
    for _, molecule, row in flat:
        reads, seconds = results[molecule.molecule_id]
        row.update(reads)
        record["molecules"][molecule.molecule_id] = molecule_record(molecule, row, seconds, smiles[molecule.molecule_id], config.ks)
    record["sets"] = {key: {"n_molecules": len(ids[key]), "ids": ids[key], **summarise(rows[key], config.ks)} for key in SETS}
    record["worst_cases"] = worst_cases(record["molecules"], f"{MAIN_KIND}/set0/K{max(config.ks)}")
    held = [mid for key in SETS for mid in ids[key]]
    record["named_cases"] = ([mid for mid in (BIPHENYL,) if mid in held] + list(EXTRA)
                             + [mid for mid in held if record["molecules"][mid]["triple_bond"]])
    record["biphenyl_in_holdouts"] = BIPHENYL in held
    per_call = [rec["seconds_per_correction"] for rec in record["molecules"].values()]
    record["seconds_per_correction_median"] = float(np.median(per_call))
    record["seconds_per_correction_max"] = float(max(per_call))
    record["wall_seconds"] = time.perf_counter() - started
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("plan", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--smoke", action="store_true", help="one molecule per hold-out, K = 1 and 4, no reference check")
    args = parser.parse_args()
    config = Config(args.plan.resolve(), args.out.resolve(), args.smoke)
    if not config.out.is_dir():
        stop(f"{config.out} is not a folder")
    torch.set_num_threads(1)   # one thread per process: the pool forks, and a forked torch thread pool can hang
    record = run(config)
    write(config.out / f"{config.stem}.json", json.dumps(record, indent=1))
    text = tables(record, config.ks)
    write(config.out / f"{config.stem}.txt", text)
    sys.stdout.write(text)
    print(f"order mean read: {len(record['molecules'])} molecules, record {config.out / (config.stem + '.json')}", flush=True)


if __name__ == "__main__":
    main()
