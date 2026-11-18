"""Decision 66 (17 Nov 2026) in the model registry: a network's kind beside its version, and 'carried' naming the pair.

The kind is the checkpoint's own; a status entry repeats it as `network_kind`, an entry without the field is a measurement network
(release entries state theirs), and an entry that contradicts its checkpoint stops the generator. `carried_keys` gives one kind's
files; a carried release network without carried measurement networks of its version is refused."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

torch = pytest.importorskip("torch")
PLAN = Path(__file__).resolve().parents[1]
M05 = PLAN / "modules" / "05_support_predictor"
sys.path.insert(0, str(M05 / "m05"))
import model_registry as MR  # noqa: E402
import network_kind as NK  # noqa: E402

DH = "ΔH-network"


def checkpoint(out: Path, stem: str, seed: int, kind: str | None) -> Path:
    """A hybrid checkpoint as the trainer saves it, of the given kind (None: saved before the decision, no field)."""
    ctor = {"aggregation": "sum", "tensor_input": False, "sqm_scale": True, "n_pair_features": 12, "hidden": 256, "n_s": 64, "n_v": 16, "n_blocks": 3}
    args = {"pool_layers": "A,A2,B", "use_analytic": True, "epochs": 200, "patience": 20, "lr": 3e-4, "head": "hybrid"}
    path = out / f"{stem}_model_n30_seed{seed}.pt"
    torch.save({"state": {}, "ctor": ctor, "args": args if kind is None else args | {NK.FIELD: kind}, "n": 30, "seed": seed}, path)
    return path


def entry(status: str = "carried", version: str = "1.4", kind: str | None = None) -> dict:
    return {"status": status, "network": DH, "version": version, "chain": "45"} | ({} if kind is None else {NK.FIELD: kind})


def write(path: Path, entries: dict) -> Path:
    path.write_text(json.dumps(entries, ensure_ascii=False), encoding="utf-8")
    return path


@pytest.fixture
def pair(tmp_path):
    """A carried version as a pair: two measurement seeds (one saved before the decision) and two release seeds."""
    files = {"m0": checkpoint(tmp_path, "V_meas", 0, None), "m1": checkpoint(tmp_path, "V_meas", 1, NK.MEASUREMENT),
             "r0": checkpoint(tmp_path, "V_rel", 0, NK.RELEASE), "r1": checkpoint(tmp_path, "V_rel", 1, NK.RELEASE)}
    entries = {files["m0"].name: entry(), files["m1"].name: entry(kind=NK.MEASUREMENT),
               files["r0"].name: entry(kind=NK.RELEASE), files["r1"].name: entry(kind=NK.RELEASE)}
    return tmp_path, files, entries


def test_every_committed_entry_states_its_kind_and_its_name_agrees():
    """An entry without the field reads as a measurement network (the migration's default); a release network states its kind,
    and its file name says `_release` (release_chain.py's prefix): a cheap cross-check of the naming, without the checkpoints
    (the generator's `checked_kind` compares an entry with its checkpoint). The carried ΔH version
    is three measurement networks and, once its release networks have passed their checks, three release networks of the same
    version (decision 66)."""
    for module in MR.MODULES.values():
        status = MR.read_status(module["status"])
        assert status
        for key, entry in status.items():
            assert (NK.stated_kind(entry, key) == NK.RELEASE) == ("_release" in Path(key).name), key
    status = MR.read_status(MR.STATUS_FILE)
    measured = MR.carried_keys(status, DH, NK.MEASUREMENT)
    released = MR.carried_keys(status, DH, NK.RELEASE)
    assert len(measured) == 3 and len(released) in (0, 3)
    versions = {str(status[k]["version"]) for k in (*measured, *released)}
    assert len(versions) == 1, versions          # one version: check_pairs allows release networks of any measured version


def test_the_committed_registries_carry_the_generators_header():
    """The four generated files were given the new rule text by patch (their checkpoints are not in git): each must open with what
    the generator renders today, so `--check` finds them current where the checkpoints are."""
    for module in MR.MODULES.values():
        assert module["registry"].read_text(encoding="utf-8").startswith(MR.render([], module))
    assert MR.OVERVIEW.read_text(encoding="utf-8").startswith(MR.OVERVIEW_HEADER.format(rule=MR.RULE))
    assert "**Kinds (decision 66, 17 Nov 2026):**" in MR.RULE and "`carried` names the pair" in MR.RULE


def test_carried_names_the_pair(pair):
    out, files, entries = pair
    status = MR.read_status(write(out / "status.json", entries))
    assert MR.carried_keys(status, DH, NK.MEASUREMENT) == [files["m0"].name, files["m1"].name]
    assert MR.carried_keys(status, DH, NK.RELEASE) == [files["r0"].name, files["r1"].name]
    with pytest.raises(ValueError, match="network kind 'both'"):
        MR.carried_keys(status, DH, "both")


def test_a_carried_release_network_is_no_base_for_a_read(pair):
    """`require_carried` means a measurement network unless told otherwise; --allow-any-model lifts the status, not the kind."""
    out, files, entries = pair
    st = write(out / "status.json", entries)
    assert MR.require_carried(files["m0"], status_file=st)["status"] == "carried"
    for allow in (False, True):
        with pytest.raises(SystemExit, match=r"entered in the model registry as a release network and a measurement network is meant here"):
            MR.require_carried(files["r0"], allow=allow, status_file=st)
    assert MR.require_carried(files["r0"], status_file=st, kind=NK.RELEASE)[NK.FIELD] == NK.RELEASE
    assert MR.require_carried(files["r0"], status_file=st, kind=None)[NK.FIELD] == NK.RELEASE
    assert MR.require_carried(files["m1"], status_file=st, kind=None)["status"] == "carried"
    with pytest.raises(SystemExit, match="as a measurement network and a release network is meant here"):
        MR.require_carried(files["m0"], status_file=st, kind=NK.RELEASE)


def test_the_rows_and_the_table_show_the_kind_beside_the_version(pair):
    out, files, entries = pair
    table, missing = MR.rows(out, write(out / "status.json", entries))
    assert not missing and [r["network_kind"] for r in table] == [NK.MEASUREMENT, NK.MEASUREMENT, NK.RELEASE, NK.RELEASE]
    md = MR.render(table)
    assert f"| `{files['r0'].name}` | {DH} | 1.4 (release) | hybrid |" in md and f"| `{files['m0'].name}` | {DH} | 1.4 | hybrid |" in md
    overview = MR.render_overview({"05": table})
    assert "| v1.4 (45; 2 seeds; release networks: 2 seeds) |" in overview


def test_an_entry_that_contradicts_its_checkpoint_stops_the_generator(pair, capsys):
    out, files, entries = pair
    as_measurement = entries | {files["r0"].name: entry()}                  # a release checkpoint entered without its kind
    with pytest.raises(ValueError, match=rf"{files['r0'].name} is entered as a measurement network, and its checkpoint says release"):
        MR.rows(out, write(out / "status.json", as_measurement))
    as_release = entries | {files["m1"].name: entry(kind=NK.RELEASE)}
    with pytest.raises(ValueError, match=rf"{files['m1'].name} is entered as a release network, and its checkpoint says measurement"):
        MR.rows(out, write(out / "status.json", as_release))


def test_an_unknown_kind_and_a_release_without_its_measurement_pair_are_refused(pair):
    out, files, entries = pair
    with pytest.raises(ValueError, match="states network_kind 'shipping'"):
        MR.read_status(write(out / "status.json", entries | {files["m0"].name: entry(kind="shipping")}))
    alone = {k: e for k, e in entries.items() if NK.FIELD in e and e[NK.FIELD] == NK.RELEASE}
    with pytest.raises(ValueError, match=r"carried release network.*without carried measurement networks of the same version"):
        MR.read_status(write(out / "status.json", alone))
    other_version = entries | {files["m0"].name: entry(version="1.3"), files["m1"].name: entry(version="1.3", kind=NK.MEASUREMENT)}
    with pytest.raises(ValueError, match="without carried measurement networks of the same version"):
        MR.read_status(write(out / "status.json", other_version))
    candidates = {k: e | {"status": "candidate", "version": ""} for k, e in alone.items()}
    assert len(MR.read_status(write(out / "status.json", candidates))) == 2      # not carried yet: no pair needed


def test_candidates_are_entered_with_the_kind_the_chain_trained(pair):
    out, files, _ = pair
    st = write(out / "status.json", {})
    args = ["--out-dir", str(out), "--status-file", str(st), "--registry", str(out / "M.md"), "--chain", "45", "--add-candidates"]
    assert MR.add_candidates([files["m0"], files["m1"]], "45", "v1.4", DH, status_file=st) == [files["m0"].name, files["m1"].name]
    assert MR.main([*args, str(files["r0"]), str(files["r1"]), "--network-kind", "release"]) == 0
    status = json.loads(st.read_text(encoding="utf-8"))
    assert NK.FIELD not in status[files["m0"].name] and status[files["r0"].name][NK.FIELD] == NK.RELEASE
    assert "| — (release) |" in (out / "M.md").read_text(encoding="utf-8")       # a candidate has no version yet; its kind shows
    with pytest.raises(SystemExit, match="--network-kind 'both'"):
        MR.add_candidates([files["r0"]], "45", "v1.4", DH, status_file=write(out / "other.json", {}), network_kind="both")


def test_release_candidates_entered_without_their_kind_stop_the_rebuild(pair):
    out, files, _ = pair
    st = write(out / "status.json", {})
    MR.add_candidates([files["m0"], files["m1"], files["r1"]], "45", "v1.4", DH, status_file=st)
    MR.add_candidates([files["r0"]], "45", "v1.4", DH, status_file=st, network_kind=NK.RELEASE)
    with pytest.raises(ValueError, match=rf"{files['r1'].name} is entered as a measurement network"):
        MR.main(["--out-dir", str(out), "--status-file", str(st), "--registry", str(out / "M.md")])
