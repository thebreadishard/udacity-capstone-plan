"""The pipeline's anharmonic step (`m08/anharmonic.py`, TASKS 211), the sentences about positions (`m08/positions.py`) and the
pipeline's two deliveries: every switch and every wording branch, on the frozen corpus's benzene with the committed artefact. No
GFN2-xTB runs here: the force field is a stand-in built from the molecule's own B3LYP modes — exact, or rotated among themselves
where a test is about the match — and the WSL runner is replaced where a test is about its failures. What the certificate and
the pages print is in tests/test_m08_positions_pages.py."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path, PurePosixPath, PureWindowsPath
from types import SimpleNamespace

import numpy as np
import pytest

from pin_tools import PLAN
from test_m08_live_certificate import PIN_MODEL, ZERO, record, result, with_mode_at  # noqa: F401  result is a fixture

sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
from m08 import anharmonic as AN
from m08 import pipeline as P
from m08 import positions as POS

# isort: split
import anharmonic_step as AS  # probes/, on the path through m08.pipeline

SETTINGS = AN.FieldSettings.of(4, 2, 1536, 120)
BARS = {"ring-ip": 3.37, "other": 3.84, "CH-oop": 8.38, "CH-stretch": 6.21}
BENZENE = "c1ccccc1"
SWAPPED, SCRAMBLED = (13, 18), (4, 5, 10)      # the scrambled three are modes without a degenerate partner (TASKS 255):
#                                                 a member of a pair is read against its pair's partners, and two of three
#                                                 scrambled vectors can hold 8/9 of it


@pytest.fixture(scope="module")
def artefact() -> AS.Artefact:
    return AN.load_artefact()


def modes_of(d: Path) -> AS.Modes:
    symbols, coords, _ = AN.geometry(d)
    return AS.Modes.from_hessian(AN.low_hessian(d), symbols, coords)


def stand_in_field(d: Path, marked: tuple[int, ...] = (), perturbed: bool = False) -> AS.XtbField:
    """A force field whose modes are the molecule's B3LYP modes (every overlap 1) and whose shifts are 1 % of ω, downwards. With
    `perturbed`, its modes are not the B3LYP modes any more: two of them are rotated into each other by 60° (each B3LYP mode
    then overlaps the *other* xtb mode by 0.75), and three are mixed so that no B3LYP mode overlaps any of them by 0.5."""
    modes = modes_of(d)
    mask = np.zeros(len(modes.omega), bool)
    mask[list(marked)] = True
    q = modes.q.copy()
    if perturbed:
        a, b = SWAPPED
        c, s = np.cos(np.pi / 3), np.sin(np.pi / 3)
        q[:, a], q[:, b] = c * modes.q[:, a] + s * modes.q[:, b], -s * modes.q[:, a] + c * modes.q[:, b]
        q[:, list(SCRAMBLED)] = modes.q[:, list(SCRAMBLED)] @ (np.array([[-1.0, 2.0, 2.0], [2.0, -1.0, 2.0], [2.0, 2.0, -1.0]]) / 3.0)
    return AS.XtbField(-0.01 * modes.omega, mask, q)


def spectra_of(d: Path) -> dict:
    return json.loads((d / "pipeline.json").read_text(encoding="utf-8"))["spectra"]


def request(d: Path, artefact: AS.Artefact | None, smiles: str | None = BENZENE) -> AN.Request:
    return AN.Request("benzene", d, smiles, artefact, None if artefact is None else SETTINGS)


def stepped(d: Path, artefact: AS.Artefact, monkeypatch: pytest.MonkeyPatch, dH: np.ndarray = ZERO, **field: object) -> dict:
    """The folder with the pipeline's record of `dH` and step 6 applied on the stand-in field; the record's spectra."""
    record(d, dH, [dH])
    monkeypatch.setattr(AN, "force_field", lambda name, folder, s: (stand_in_field(folder, **field), {"seconds": 1.0, "peak_memory_mb": 7}))
    out = AN.step(request(d, artefact), dH, spectra_of(d))
    rec = json.loads((d / "pipeline.json").read_text(encoding="utf-8"))
    P.write_json(d / "pipeline.json", rec | {"spectra": out})
    return out


def by_mode(sticks: list[dict]) -> dict[int, dict]:
    """The sticks by the B3LYP mode each one's step came from (within a degenerate pair the band order is not the mode order)."""
    return {x["anharmonic"]["b3lyp_mode"]: x for x in sticks}


def no_runner(*args: object) -> int:
    raise AssertionError("the WSL runner was started")


REAL_FIELD_COMMAND = AN.field_command
WINDOWS_PLAN = PureWindowsPath(r"C:\plan folder\05")
WINDOWS_SCRIPTS = (WINDOWS_PLAN / "probes" / "run_in_scope.sh", WINDOWS_PLAN / "probes" / "xtb_field_for_step.sh")


@pytest.fixture(autouse=True)
def any_host(monkeypatch: pytest.MonkeyPatch) -> None:
    """These tests run on every host (CI is Linux). What they test of the runner — its exits, its markers, its record — does not
    depend on the command line, so the host counts as one with WSL and the command line is a stand-in; the command line itself
    is tested as the pure function it is, with literal Windows paths (REAL_FIELD_COMMAND), and the host check has its own tests."""
    monkeypatch.setattr(AN, "host_has_wsl", lambda: True)
    monkeypatch.setattr(AN, "field_command", lambda *a, **k: ["wsl.exe", "-e", "bash", "-lc", "a stand-in: the command line has its own test"])
    monkeypatch.setattr(AN, "SCOPE_SCRIPT", PureWindowsPath(r"C:\plan\probes\run_in_scope.sh"))


# ---------------------------------------------------------------- the step

def test_the_step_gives_every_band_its_position_and_its_reason(result, artefact, monkeypatch):  # noqa: F811
    out = stepped(result, artefact, monkeypatch)
    sticks, s = out["network"]["sticks"], out["anharmonic"]
    assert s["status"] == POS.APPLIED and s["model"] == "x2*" and s["artefact"]["bars_cm"] == BARS
    assert s["artefact"]["file"] == "probes/anharmonic_step/x2star_v3.json" and s["field"]["peak_memory_mb"] == 7
    assert len(sticks) == 30 and s["bands"]["stepped"] + sum(s["bands"]["no_step"].values()) == 30
    for stick in sticks:
        a = stick["anharmonic"]
        if a["delta_anh_cm"] is None:
            assert stick["nu_cm"] is None and a["reason"] == AS.UNMEASURED and a["bar_cm"] is None and stick["omega_cm"] < 550
        else:
            assert stick["nu_cm"] == round(stick["omega_cm"] + a["delta_anh_cm"], 1) and a["reason"] is None
            assert a["bar_cm"] == (None if a["error_not_measured"] else BARS[a["family"]]) and a["overlap"] == pytest.approx(1.0)
    assert s["bands"]["no_step"] == {AS.UNMEASURED: sum(x["omega_cm"] < 550 for x in sticks)} and s["bands"]["no_step"][AS.UNMEASURED] > 0
    assert sum(x["anharmonic"]["family"] == "CH-stretch" and x["nu_cm"] is not None for x in sticks) == 6
    flagged = [x for x in sticks if x["anharmonic"]["error_not_measured"]]
    assert len(flagged) == s["bands"]["error_not_measured"] > 0 and all(x["anharmonic"]["family"] == "other" for x in flagged)
    assert all(x["anharmonic"]["bar_cm"] is None for x in flagged)       # a bar that was not measured is not in the record at all
    saved = json.loads((result / AN.RECORD).read_text(encoding="utf-8"))
    assert len(saved["modes"]) == 30 and [b["nu_cm"] for b in saved["bands"]] == [x["nu_cm"] for x in sticks]
    assert out["note"] == POS.note(s) and f"for {s['bands']['stepped']} of 30 bands" in out["note"]


def test_the_summary_says_what_the_model_knows_of_the_molecule(result, artefact, monkeypatch):  # noqa: F811
    """Benzene is in x2*'s training table; a hydrocarbon is a composition the table holds 14 of. Another SMILES is unseen, none unknown."""
    s = stepped(result, artefact, monkeypatch)["anharmonic"]
    assert s["seen"] == {"role": "training", "id": "A_8448043181"}
    assert s["composition"] == {"elements": "C,H", "training_molecules": 14, "of": 37, "few": False,
                                "targets": {"coronene": "C,H", "tetracene": "C,H"}}
    assert s["artefact"]["elements"] == ["C", "H", "N", "O"] and s["artefact"]["targets"]["ring-ip"]["rows"] == 56
    for smiles, role in (("c1ccncc1", "unseen"), (None, "unknown"), ("c1ccc2cc3cc4ccccc4cc3cc2c1", "target")):
        assert AN.step(request(result, artefact, smiles), ZERO, spectra_of(result))["anharmonic"]["seen"]["role"] == role


def test_a_marked_xtb_partner_leaves_its_band_harmonic(result, artefact, monkeypatch):  # noqa: F811
    out = stepped(result, artefact, monkeypatch, marked=(12,))
    refused = [x for x in out["network"]["sticks"] if x["anharmonic"]["reason"] == AS.XTB_PARTNER_MARKED]
    assert len(refused) == 1 and refused[0]["anharmonic"]["b3lyp_mode"] == 12 and refused[0]["nu_cm"] is None
    assert out["anharmonic"]["bands"]["no_step"][AS.XTB_PARTNER_MARKED] == 1


def test_a_force_field_of_other_modes_is_matched_by_overlap_or_not_at_all(result, artefact, monkeypatch):  # noqa: F811
    """Review finding 9: a field that is not the stand-in at overlap 1. The two rotated xtb modes go to the B3LYP mode each
    overlaps by 0.75 — the other one — so each band's input is the other xtb mode's shift; the three mixed modes match nothing
    and their bands stay harmonic with the reason."""
    plain = by_mode(json.loads(json.dumps(stepped(result, artefact, monkeypatch)["network"]["sticks"])))
    out = stepped(result, artefact, monkeypatch, perturbed=True)
    sticks = by_mode(out["network"]["sticks"])
    saved = {m["mode"]: m for m in json.loads((result / AN.RECORD).read_text(encoding="utf-8"))["modes"]}
    for k in SWAPPED:
        assert saved[k]["xtb_overlap"] == pytest.approx(0.75) and saved[k]["reason"] is None
        assert sticks[k]["anharmonic"]["delta_anh_cm"] != plain[k]["anharmonic"]["delta_anh_cm"]
    expected = AS.mode_steps(modes_of(result), stand_in_field(result, perturbed=True), artefact)
    assert [sticks[k]["anharmonic"]["delta_anh_cm"] for k in SWAPPED] == [round(expected[k].delta_anh_cm, 1) for k in SWAPPED]
    for k in SCRAMBLED:
        assert saved[k]["xtb_overlap"] < 0.5 and sticks[k]["anharmonic"]["reason"] == AS.NO_XTB_PARTNER and sticks[k]["nu_cm"] is None
    assert out["anharmonic"]["bands"]["no_step"][AS.NO_XTB_PARTNER] == 3
    untouched = [k for k in range(30) if k not in (*SWAPPED, *SCRAMBLED)]
    assert all(sticks[k]["anharmonic"] == plain[k]["anharmonic"] for k in untouched)


def test_the_step_follows_the_mode_not_the_rank(result, artefact, monkeypatch):  # noqa: F811
    """A correction that lifts B3LYP mode 9 above the modes over it: the band keeps mode 9's step at its new rank, and the bands
    it passed keep theirs."""
    _, _, masses = AN.geometry(result)
    H = AN.low_hessian(result)
    modes = modes_of(result)
    target = float(modes.omega[11]) + 5.0
    passed = int((modes.omega[10:] < target).sum())
    out = stepped(result, artefact, monkeypatch, dH=with_mode_at(H, masses, 9, target) - H)
    sticks = out["network"]["sticks"]
    moved = next(i for i, x in enumerate(sticks) if x["anharmonic"]["b3lyp_mode"] == 9)
    assert passed >= 2 and moved == 9 + passed and sticks[moved]["omega_cm"] == round(target, 1)
    assert [x["anharmonic"]["b3lyp_mode"] for x in sticks[9:moved + 1]] == [*range(10, 10 + passed), 9]
    plain = AS.mode_steps(modes, stand_in_field(result), artefact)[9]
    assert sticks[moved]["anharmonic"]["delta_anh_cm"] == round(plain.delta_anh_cm, 1) and sticks[moved]["anharmonic"]["family"] == plain.family


def test_a_mode_the_two_family_rules_name_differently_gets_no_step(result, artefact, monkeypatch):  # noqa: F811
    """Review finding 8: the step's family rule and the certificate's are two implementations. On benzene they agree on every
    mode; where they did not, the band would print one family's bar under another family's name, so it gets no step."""
    agreed = AN.certificate_families(result, AN.low_hessian(result), modes_of(result).omega)
    assert agreed == [s.family for s in AS.mode_steps(modes_of(result), stand_in_field(result), artefact)]
    other = [("ring-ip" if i == 15 and f != "ring-ip" else "other" if i == 15 else f) for i, f in enumerate(agreed)]
    monkeypatch.setattr(AN, "certificate_families", lambda d, H, omega: other)
    out = stepped(result, artefact, monkeypatch)
    stick = by_mode(out["network"]["sticks"])[15]
    assert stick["anharmonic"]["reason"] == AS.FAMILY_MISMATCH and stick["nu_cm"] is None and stick["anharmonic"]["bar_cm"] is None
    assert out["anharmonic"]["bands"]["no_step"][AS.FAMILY_MISMATCH] == 1


def test_family_rules_that_see_other_modes_are_an_error(result):  # noqa: F811
    with pytest.raises(RuntimeError, match="do not see the same B3LYP modes"):
        AN.certificate_families(result, AN.low_hessian(result), modes_of(result).omega + 5.0)


def test_switched_off_the_step_computes_nothing_and_says_so(result, monkeypatch):  # noqa: F811
    record(result, ZERO, [ZERO])
    monkeypatch.setattr(P, "_run", no_runner)
    out = AN.step(request(result, None), ZERO, spectra_of(result))
    assert out["anharmonic"] == {"status": POS.NOT_APPLIED, "reason": POS.SWITCHED_OFF, "model": "x2*", "field": None}
    assert all(x["nu_cm"] is None and x["anharmonic"] is None for x in out["network"]["sticks"])
    assert out["note"] == f"positions are harmonic (ω): the anharmonic step was not applied — {POS.SWITCHED_OFF}"
    assert not (result / AN.RECORD).exists() and not (result / AN.FOLDER).exists()
    with pytest.raises(ValueError, match="on with an artefact and settings, or off with neither"):
        AN.Request("benzene", result, BENZENE, None, SETTINGS)


def test_an_element_outside_the_artefacts_table_gets_no_force_field(result, artefact, monkeypatch):  # noqa: F811
    """Review finding 6: the elements are the artefact's list of its training molecules' elements, not a mass table's keys."""
    record(result, ZERO, [ZERO])
    g = json.loads((result / "geometry.json").read_text(encoding="utf-8"))
    g["symbols"][6] = "F"
    P.write_json(result / "geometry.json", g)
    monkeypatch.setattr(P, "_run", no_runner)
    out = AN.step(request(result, artefact), ZERO, spectra_of(result))
    assert out["anharmonic"]["status"] == POS.NOT_APPLIED
    assert "element(s) F outside the anharmonic model's training table (C, H, N, O)" in out["note"]
    narrow = AS.Artefact(artefact.windows, artefact.header | {"elements": ["C", "N"]})
    with pytest.raises(AN.NotApplied, match=r"element\(s\) H outside the anharmonic model's training table \(C, N\)"):
        AN.b3lyp_modes(["C", "H"], np.zeros((2, 3)), np.zeros((6, 6)), narrow)


def test_modes_the_force_field_cannot_take_keep_the_run_alive(result, artefact, monkeypatch):  # noqa: F811
    """A B3LYP Hessian with a mode under dpir.qff's line (a near-free rotor): harmonic positions with the reason, no xtb run."""
    _, _, masses = AN.geometry(result)
    with np.load(result / P.RI.LOW_HESSIAN) as z:
        arrays = {k: z[k] for k in z.files}
    np.savez(result / P.RI.LOW_HESSIAN, **(arrays | {"H_projected": with_mode_at(arrays["H_projected"], masses, 0, 5.0)}))
    record(result, ZERO, [ZERO])
    monkeypatch.setattr(P, "_run", no_runner)
    out = AN.step(request(result, artefact), ZERO, spectra_of(result))
    assert out["anharmonic"]["status"] == POS.NOT_APPLIED and "the B3LYP modes are not the 3N−6 the force field needs" in out["note"]


@pytest.mark.parametrize(("rc", "log", "expect"), [
    (1, "=== (XTB) benzene: start\n=== (ANH) FAILED: the force field is NOISY (dpir.qff's noise guard), so it is not used 2026-11-16 20:00:00\n",
     "could not be made: the force field is NOISY (dpir.qff's noise guard), so it is not used (anharmonic_field.log)"),
    (2, "wsl_capped.sh: systemd-run missing - no cap, not run\n", "could not be made: exit 2 (anharmonic_field.log)"),
    (137, "KILLED: over the cap of 1536 MB\n", "was stopped at the WSL cap of 1536 MB (anharmonic_field.log)"),
    # round two, finding 4: the reason a certificate prints names what is kept and the command that takes the step up
    (124, "=== (XTB) benzene: 61 Hessians to compute\n=== (SCOPE) stopped at the budget of 7200 s\n",
     "the anharmonic step did not finish within 120 minutes; the force field's finished Hessians are kept in the result's anharmonic/xtb, "
     "and `python -m m08.anharmonic <result folder>` takes the step up from them; its scope m08-anharmonic-benzene-"),
    (0, "=== (ANH) done: benzene in 5 s 2026-11-16 20:00:05\n", "cannot be read: ")])
def test_a_force_field_that_fails_leaves_harmonic_positions_with_the_reason(result, artefact, monkeypatch, rc, log, expect):  # noqa: F811
    record(result, ZERO, [ZERO])

    def runner(argv: list[str], log_path: Path, what: str) -> int:
        log_path.write_text(log, encoding="utf-8")
        return rc

    monkeypatch.setattr(P, "_run", runner)
    out = AN.step(request(result, artefact), ZERO, spectra_of(result))
    s = out["anharmonic"]
    assert s["status"] == POS.NOT_APPLIED and expect in s["reason"] and out["note"].startswith("positions are harmonic (ω)")
    assert all(x["nu_cm"] is None for x in out["network"]["sticks"]) and not (result / AN.RECORD).exists()
    assert s["field"]["cap_mb"] == 1536 and s["field"]["budget_minutes"] == 120 and s["field"]["log"] == AN.LOG
    # round three, B: the scope's unit is in the field's record, and a stop's reason names it with the command that stops it
    unit = s["field"]["unit"]
    assert re.fullmatch(r"m08-anharmonic-benzene-[0-9a-f]{10}\.scope", unit)
    assert (result / AN.FOLDER / AN.UNIT_FILE).read_text(encoding="utf-8") + ".scope" == unit
    if rc == AN.TIMED_OUT:
        assert f"its scope {unit} was stopped at the budget and left no process (`wsl -e systemctl --user stop {unit}` would stop" in s["reason"]
    assert (result / AN.FOLDER / "G" / "ref.json").is_file()            # the reference record the runner starts from was written


def test_processes_that_survive_the_scopes_stop_are_an_error_not_a_reason(result, monkeypatch):  # noqa: F811
    """Round two, finding 2: the run is stopped by its scope (probes/run_in_scope.sh, tests/test_run_in_scope.py). If the scope
    reports survivors, that is nothing a certificate can state as a reason for harmonic positions: it raises."""
    def runner(argv: list[str], log_path: Path, what: str) -> int:
        log_path.write_text("=== (SCOPE) FAILED: 1 process(es) of m08-anharmonic-benzene-0123456789 survive SIGKILL on the unit\n", encoding="utf-8")
        return AN.SURVIVORS

    monkeypatch.setattr(P, "_run", runner)
    with pytest.raises(RuntimeError, match="survived its stop"):
        AN.force_field("benzene", result, SETTINGS)


def test_a_machine_that_cannot_own_the_force_field_is_refused_before_step_1(tmp_path, monkeypatch):
    """No systemd user scope, no step — said before anything is computed, and never a fallback to killing by pattern."""
    calls: list[str] = []
    stubbed_run(monkeypatch, calls, preflight=False)
    monkeypatch.setattr(AN, "load_artefact", lambda: pytest.fail("the artefact was read on a machine the step cannot run on"))
    asked = []

    def no_scope(argv: list[str], **kw: object) -> SimpleNamespace:
        asked.append(argv[-1])
        return SimpleNamespace(returncode=2, stdout="run_in_scope.sh: no systemd user scope can be made here\n", stderr="")

    monkeypatch.setattr(AN.subprocess, "run", no_scope)
    with pytest.raises(P.Refused, match="the anharmonic step cannot run here") as refused:
        P.run(base_config(tmp_path, reuse_corpus=False))
    assert "no systemd user scope can be made here" in refused.value.reasons[0] and "--no-anharmonic" in refused.value.reasons[0]
    assert calls == [] and not (tmp_path / "mol").exists() and asked[0].endswith("/probes/run_in_scope.sh --check")
    monkeypatch.setattr(AN.subprocess, "run", lambda argv, **kw: SimpleNamespace(returncode=0, stdout="", stderr=""))
    AN.preflight()


def test_the_runner_reports_its_peak_memory_and_time(result, monkeypatch):  # noqa: F811
    """`force_field` reads the script's markers; the read of the field itself is replaced."""
    def runner(argv: list[str], log_path: Path, what: str) -> int:
        log_path.write_text("=== (ANH) peak memory 612 MB (the scope's memory.peak, page cache included) 2026-11-16 20:00:05\n", encoding="utf-8")
        return 0

    monkeypatch.setattr(P, "_run", runner)
    seen = {}
    monkeypatch.setattr(AS.XtbField, "from_folder", classmethod(lambda cls, x, label: seen.update(x=x, label=label) or "field"))
    field, rec = AN.force_field("benzene", result, SETTINGS)
    assert field == "field" and rec["peak_memory_mb"] == 612 and rec["shards"] == 2 and rec["omp_threads"] == 2 and rec["cap_mb"] == 1536
    assert rec["unit"].startswith("m08-anharmonic-benzene-") and rec["unit"].endswith(".scope")
    assert seen["x"].endswith(str(Path("anharmonic") / "xtb" / "benzene" / "X")) and seen["label"].endswith("benzene.json")


def test_the_field_command_is_the_capped_script_under_its_time_budget():
    """A pure function of the Windows paths it is given: the same command line on every host (literal C:\\ paths, one with a
    space in it)."""
    d = PureWindowsPath(r"C:\results\mol")
    command = REAL_FIELD_COMMAND("mol", d, AN.FieldSettings.of(6, 3, 2048, 90), "m08-anharmonic-mol-0123456789", scripts=WINDOWS_SCRIPTS)
    assert command[:4] == ["wsl.exe", "-e", "bash", "-lc"]
    # the scope's own script, with the unit of this run, the cap, the budget and the kill-after; no process is found by a pattern
    assert command[-1] == ("export SHARDS=3 OMP_NUM_THREADS=2 PYTHONUNBUFFERED=1; "
                           "bash '/mnt/c/plan folder/05/probes/run_in_scope.sh' m08-anharmonic-mol-0123456789 2048 5400 30 -- "
                           "bash '/mnt/c/plan folder/05/probes/xtb_field_for_step.sh' mol /mnt/c/results/mol/anharmonic/G "
                           "/mnt/c/results/mol/anharmonic")
    assert "pgrep" not in command[-1] and "pkill" not in command[-1] and "wsl_capped" not in command[-1]
    assert re.fullmatch(r"m08-anharmonic-mol-[0-9a-f]{10}", AN.scope_unit("mol")) and AN.scope_unit("mol") != AN.scope_unit("mol")
    dry = REAL_FIELD_COMMAND("mol", d, SETTINGS, "u", dry=True, scripts=WINDOWS_SCRIPTS)[-1]
    assert dry.endswith("/mnt/c/results/mol/anharmonic --dry-run") and " u 1536 7200 30 -- " in dry
    with pytest.raises(ValueError, match="not an absolute Windows drive path"):          # a path of another system is refused, not guessed
        REAL_FIELD_COMMAND("mol", PurePosixPath("/home/runner/results/mol"), SETTINGS, "u", scripts=WINDOWS_SCRIPTS)


def test_a_host_without_wsl_is_refused_before_step_1_and_asks_nothing(tmp_path, monkeypatch):
    """CI on Linux, 16 Nov 2026: the step turned the plan folder's path into a WSL path before it knew its host. A host that is
    not Windows is refused with the reason before step 1 — no path converted, no process started — and a direct call of the
    runner gives the same reason as a step that is not applied."""
    calls: list[str] = []
    stubbed_run(monkeypatch, calls, preflight=False)
    monkeypatch.setattr(AN, "host_has_wsl", lambda: False)
    monkeypatch.setattr(AN, "SCOPE_SCRIPT", PurePosixPath("/home/runner/plan/probes/run_in_scope.sh"))
    monkeypatch.setattr(AN, "load_artefact", lambda: pytest.fail("the artefact was read on a host the step cannot run on"))
    start_process = AN.subprocess.run
    monkeypatch.setattr(AN.subprocess, "run", lambda *a, **k: pytest.fail("a process was started on a host without WSL"))
    monkeypatch.setattr(P, "_run", no_runner)
    with pytest.raises(P.Refused, match="the anharmonic step cannot run here") as refused:
        P.run(base_config(tmp_path, reuse_corpus=False))
    assert "runs in WSL, and this host is not Windows" in refused.value.reasons[0] and calls == [] and not (tmp_path / "mol").exists()
    with pytest.raises(AN.NotApplied, match="this host is not Windows"):
        AN.force_field("benzene", tmp_path, SETTINGS)
    assert not (tmp_path / AN.FOLDER).exists()
    monkeypatch.setattr(AN.subprocess, "run", start_process)                            # the record reads git's state through it
    rec = P.run(base_config(tmp_path, reuse_corpus=False, anharmonic_minutes=0))        # the step off: the pipeline runs as before
    assert [x["delivery"] for x in rec["deliveries"]] == [P.ONLY_DELIVERY]


def test_the_host_check_is_the_platform(monkeypatch):
    monkeypatch.undo()                                                              # the real check, not this file's stand-in
    assert AN.host_has_wsl() is (sys.platform == "win32")
    assert [AN.host_has_wsl(p) for p in ("linux", "darwin", "win32")] == [False, False, True]


@pytest.mark.parametrize(("args", "match"), [((4, 0, 1536, 120), "at least one"), ((4, 2, 512, 120), "at least one"),
                                             ((4, 2, 1536, 0.5), "at least 60 s, or the step switched off")])
def test_field_settings_that_cannot_run_are_refused(args, match):
    with pytest.raises(ValueError, match=match):
        AN.FieldSettings.of(*args)


def test_more_threads_than_shards_share_out_and_fewer_still_give_one():
    assert AN.FieldSettings.of(8, 2, 1536, 120).omp_threads == 4 and AN.FieldSettings.of(1, 2, 1536, 120).omp_threads == 1
    assert AN.FieldSettings.of(4, 2, 1536, 90) == AN.FieldSettings(2, 2, 1536, 5400) and SETTINGS.budget_minutes == 120


def test_a_record_whose_sticks_are_not_its_hessians_is_refused(result, artefact, monkeypatch):  # noqa: F811
    record(result, ZERO, [ZERO])
    out = spectra_of(result)
    out["network"]["sticks"][5]["omega_cm"] += 1.0
    monkeypatch.setattr(AN, "force_field", lambda name, folder, s: (stand_in_field(folder), {}))
    with pytest.raises(RuntimeError, match="not the one H_low"):
        AN.step(request(result, artefact), ZERO, out)


# ---------------------------------------------------------------- the sentences

ARTEFACT_RECORD = {"training_molecules": 37, "target_composition": {"coronene": "C,H", "tetracene": "C,H"},
                   "targets": {"ring-ip": {"rows": 56, "per_target_rms_cm": {"tetracene": 2.35, "coronene": 4.25}},
                               "CH-oop": {"rows": 22, "per_target_rms_cm": {"tetracene": 4.55, "coronene": 11.91}}}}
APPLIED = {"status": POS.APPLIED, "reason": None, "model": "x2*", "artefact": ARTEFACT_RECORD,
           "seen": {"role": "unseen", "id": None},
           "composition": {"elements": "C,H,O", "training_molecules": 3, "of": 37, "few": True, "targets": ARTEFACT_RECORD["target_composition"]},
           "bands": {"stepped": 24, "error_not_measured": 2, "no_step": {"unmeasured": 5, "mixed-band": 1}}}


def test_the_note_is_true_in_each_state_of_a_result():
    on = POS.note(APPLIED)
    assert "anharmonic position ν = ω + Δ_anh for 24 of 30 bands" in on and "the harmonic position ω for the other 6" in on
    assert "force field; for 2 of them the step's error is not measured for that kind of mode, and no bar is printed)" in on
    assert POS.LICENCE_SCOPE in on and on.endswith(POS.NO_LICENCE_FOR_NU)
    assert "not measured" not in POS.note(APPLIED | {"bands": APPLIED["bands"] | {"error_not_measured": 0}})
    off = POS.note({"status": POS.NOT_APPLIED, "reason": "no force field"})
    assert off == "positions are harmonic (ω): the anharmonic step was not applied — no force field" and "licen" not in off
    running = POS.note({"status": POS.RUNNING, "budget_minutes": 120.0, "final_by": "2026-11-16 22:32"})
    assert running.startswith("positions are harmonic (ω) in this first delivery: the anharmonic step is running, with a time budget of 120 "
                              "minutes — final by 2026-11-16 22:32;")
    assert POS.SECOND_DELIVERY in running and "finalised with these harmonic positions and the reason" in running
    # round two, finding 3: a first certificate nobody replaced is true by its own words
    assert running.endswith("if this text still stands after 2026-11-16 22:32, the run was stopped from outside and this harmonic "
                            "certificate is the final one")
    assert POS.summary_of({}) == {"status": POS.NOT_APPLIED, "reason": POS.BEFORE_THE_STEP}
    assert POS.summary_of({"anharmonic": APPLIED}) is APPLIED
    assert POS.timed_out(90) == ("the anharmonic step did not finish within 90 minutes; the force field's finished Hessians are kept in "
                                 "the result's anharmonic/xtb, and `python -m m08.anharmonic <result folder>` takes the step up from them")


def test_the_bar_is_named_as_the_steps_error_and_nu_carries_omegas_too():
    """Review finding 1: the bars are the rms of Δ_anh against a VPT2 label. Nowhere is one called ν's uncertainty, and the
    certificate says once that ν carries ω's error too and that neither is an error against experiment."""
    assert POS.BAR_HEADER == "± of Δ_anh, against its VPT2 label (measured, not licensed)"
    assert "the bar beside a step is the step's error alone — the rms of Δ_anh against its B3LYP VPT2 label — and not the error of ν" in POS.NU_ERROR
    assert "ν carries ω's error too, the harmonic position's error against the DFT proxy (ωB97X), which is what the licence is about" in POS.NU_ERROR
    assert POS.NU_ERROR.endswith("neither of the two is an error against experiment")
    said = POS.cautions(APPLIED)
    assert said["nu_error"] == POS.NU_ERROR and POS.cautions({"status": POS.NOT_APPLIED, "reason": "x"}) == {}
    for text in (POS.NO_LICENCE_FOR_NU, POS.note(APPLIED), POS.band(_stick(-1.0), APPLIED, AS.REASON_TEXT, AS.NOT_MEASURED_TEXT)["position_note"]):
        assert "its uncertainty" not in text and "± of ν" not in text


def test_the_certificate_says_what_the_bars_rest_on():
    """The registration's cautions (section 3), with the artefact's own counts and per-molecule numbers."""
    t = POS.cautions(APPLIED)["targets"]
    assert t.startswith("the bars rest on 2 target molecules, coronene and tetracene, both hydrocarbons — target modes: ring-ip 56, CH-oop 22;")
    assert "the step's rms per molecule, coronene / tetracene, in cm⁻¹: ring-ip 4.25 / 2.35; CH-oop 11.91 / 4.55" in t
    assert "coronene carries the larger error in every family" in t and "they are thin" in t
    assert "nothing here says the step helps a molecule unlike the targets" in t and "not a prediction interval for one band" in t
    # review of 17 Nov 2026: the scatter between two force fields of one molecule is not in the bars, and the certificate says so
    assert t.endswith("between two GFN2-xTB force fields of the same molecule the step itself also varies, by 1.7 cm⁻¹ on a C–H "
                      "stretch pair in the one case measured (benzene, 17 Nov 2026), and the bars do not contain that")
    assert "up to" not in POS.FIELD_SCATTER                 # one measurement is not a bound
    mixed = ARTEFACT_RECORD | {"targets": {"ring-ip": {"rows": 5, "per_target_rms_cm": {"a": 1.0, "b": 2.0}},
                                           "other": {"rows": 6, "per_target_rms_cm": {"a": 3.0, "b": 2.0}}},
                               "target_composition": {"a": "C,H", "b": "C,H,N"}}
    assert "carries the larger error" not in POS.targets_sentence(mixed) and "both molecules of C,H and C,H,N" in POS.targets_sentence(mixed)


@pytest.mark.parametrize(("seen", "expect"), [
    ({"role": "training", "id": "A_1"}, "has this molecule in its training table (A_1, one of 37): for this molecule the step's bar is not an "
                                        "out-of-sample error"),
    ({"role": "target", "id": "coronene"}, "this molecule (coronene) is one of the targets x2*'s bars were measured on; it is not in its training table"),
    ({"role": "unseen", "id": None}, "the anharmonic model x2* has not seen this molecule: it is neither in its training table (37 molecules) nor a target"),
    ({"role": "unknown", "id": None}, "whether the anharmonic model x2* has seen this molecule is not known: the record names no SMILES")])
def test_the_anharmonic_model_states_its_own_seen_status(seen, expect):
    """Review finding 5: 'held out, never trained on' is the ΔH network's statement; x2* makes its own."""
    assert expect in POS.cautions(APPLIED | {"seen": seen})["seen"]


def test_few_training_molecules_of_the_molecules_elements_are_named():
    assert POS.cautions(APPLIED)["composition"] == ("the training table of x2* holds 3 of 37 molecules made of this molecule's elements "
                                                    "(C,H,O): few, and the targets the bars were measured on are made of C,H")
    enough = APPLIED | {"composition": APPLIED["composition"] | {"training_molecules": 14, "few": False}}
    assert POS.cautions(enough)["composition"] is None


def _stick(delta: float | None, reason: str | None = None, flag: bool = False) -> dict:
    return {"omega_cm": 1000.0, "nu_cm": None if delta is None else round(1000.0 + delta, 1),
            "anharmonic": {"delta_anh_cm": delta, "bar_cm": None if delta is None or flag else 3.84, "reason": reason,
                           "error_not_measured": flag, "family": "other", "b3lyp_mode": 3, "overlap": 0.9}}


def test_a_band_says_which_position_it_prints_in_each_of_its_cases():
    band = lambda stick, summary=APPLIED: POS.band(stick, summary, AS.REASON_TEXT, AS.NOT_MEASURED_TEXT)   # noqa: E731
    with_bar = band(_stick(-12.3))
    assert (with_bar["printed_cm"], with_bar["printed"], with_bar["nu_cm"], with_bar["delta_anh_cm"]) == (987.7, POS.ANHARMONIC, 987.7, -12.3)
    assert with_bar["step_bar_cm"] == 3.84 and with_bar["step_error_measured"] is True
    assert with_bar["position_note"] == ("anharmonic estimate ν = ω + Δ_anh; the step's error is ± 3.84 cm⁻¹ (rms of Δ_anh against its "
                                         "VPT2 label, family other); no licence is claimed for ν")
    without = band(_stick(-12.3, flag=True))
    assert without["printed_cm"] == 987.7 and without["step_bar_cm"] is None and without["step_error_measured"] is False
    assert without["position_note"] == (f"anharmonic estimate ν = ω + Δ_anh, printed without an error bar: {AS.NOT_MEASURED_TEXT}; "
                                        "no licence is claimed for ν")
    for code in (AS.LARGE_AMPLITUDE, AS.NO_XTB_PARTNER, AS.XTB_PARTNER_MARKED, AS.UNMEASURED, AS.MIXED_BAND, AS.MIXED_SET,
                 AS.FAMILY_MISMATCH):
        refused = band(_stick(None, code))
        assert (refused["printed_cm"], refused["printed"], refused["nu_cm"], refused["no_step_reason"]) == (1000.0, POS.HARMONIC, None, code)
        assert refused["position_note"] == f"harmonic position, no anharmonic step: {AS.REASON_TEXT[code]}"
    off = band({"omega_cm": 1000.0}, {"status": POS.NOT_APPLIED, "reason": "no force field"})
    assert off["printed"] == POS.HARMONIC and off["no_step_reason"] == POS.NOT_APPLIED and off["position_note"].endswith("— no force field")
    waiting = band({"omega_cm": 1000.0, "nu_cm": None, "anharmonic": None}, {"status": POS.RUNNING, "budget_minutes": 120.0})
    assert waiting["no_step_reason"] == POS.RUNNING and waiting["position_note"].endswith("the step is still running (first delivery)")
    assert band(_stick(-12.3), {"status": POS.NOT_APPLIED, "reason": "x"})["nu_cm"] is None     # the summary decides, not a stray block
    with pytest.raises(ValueError, match="no anharmonic block"):
        band({"omega_cm": 1000.0})


def test_a_bar_that_was_not_measured_cannot_reach_a_band_line():
    """Review finding 7: the stick of a flagged band holds no bar; one that did would be refused, not hidden."""
    stray = _stick(-12.3, flag=True)
    stray["anharmonic"]["bar_cm"] = 3.84
    with pytest.raises(ValueError, match="carries a bar that was not measured for it"):
        POS.band(stray, APPLIED, AS.REASON_TEXT, AS.NOT_MEASURED_TEXT)


def test_no_sentence_about_nu_can_be_read_as_a_licence():
    """The words 'licensed'/'licence' reach a ν only in a denial, and the licence's scope names ω."""
    assert "on the harmonic position ω" in POS.LICENCE_SCOPE and "says nothing about the anharmonic position ν" in POS.LICENCE_SCOPE
    for text in (POS.band(_stick(-1.0), APPLIED, AS.REASON_TEXT, AS.NOT_MEASURED_TEXT)["position_note"],
                 POS.band(_stick(-1.0, flag=True), APPLIED, AS.REASON_TEXT, AS.NOT_MEASURED_TEXT)["position_note"]):
        assert "no licence is claimed for ν" in text and "licensed" not in text.replace("not licensed", "")


# ---------------------------------------------------------------- the pipeline's switch and its two deliveries

REQUIRED = dict(name="mol", smiles=BENZENE, models=(PIN_MODEL,), psi4_python=Path(sys.executable))


def base_config(tmp_path: Path, **kw: object) -> P.PipelineConfig:
    """A request that asks for the step, with the budget that is to become the default."""
    return P.PipelineConfig(**(REQUIRED | dict(out_root=tmp_path, anharmonic_minutes=120) | kw))


def test_by_default_no_run_starts_a_force_field_and_the_certificate_says_the_step_exists(tmp_path, monkeypatch):
    """Round three, A: until the first real run has passed its checks the budget's default is 0. A run that names no budget asks
    WSL nothing, reads no artefact, starts no runner, delivers once — and its note says the step exists and how to switch it on."""
    default = P.PipelineConfig(**REQUIRED, out_root=tmp_path, reuse_corpus=False)
    assert default.anharmonic_minutes == 0 and default.anharmonic is False
    assert P.PipelineConfig.model_fields["anharmonic_minutes"].default == 0
    calls: list[str] = []
    stubbed_run(monkeypatch, calls, preflight=False)
    for name in ("preflight", "load_artefact"):
        monkeypatch.setattr(AN, name, lambda name=name: pytest.fail(f"{name} was called although no budget was named"))
    monkeypatch.setattr(AN, "step", lambda req, dH, out: pytest.fail("step 6 ran although no budget was named"))
    monkeypatch.setattr(P, "_run", no_runner)
    delivered: list[str] = []
    rec = P.run(default, lambda folder, what: delivered.append(what))
    assert delivered == [P.ONLY_DELIVERY] and rec["spectra"]["anharmonic"]["status"] == POS.NOT_APPLIED
    assert rec["spectra"]["note"] == ("positions are harmonic (ω): the anharmonic step was not applied — the step exists and was not run: it "
                                      "is off unless the run names a time budget, and `--anharmonic-minutes 120` switches it on")
    common = ["--name", "m", "--out", str(tmp_path), "--smiles", BENZENE]
    assert P.parse_args(common).anharmonic_minutes is None and not P.parse_args(common).no_anharmonic      # the command line adds none


def test_the_step_is_asked_for_with_a_time_budget_checked_up_front(tmp_path, capsys):
    cfg = base_config(tmp_path)
    assert cfg.anharmonic is True and (cfg.anharmonic_minutes, cfg.anharmonic_shards, cfg.anharmonic_cap_mb) == (120, 2, 1536)
    assert base_config(tmp_path, anharmonic_minutes=0).anharmonic is False
    with pytest.raises(ValueError, match="more processes than cores"):
        base_config(tmp_path, threads=2, anharmonic_shards=4)
    with pytest.raises(ValueError, match="greater than or equal to 1024"):
        base_config(tmp_path, anharmonic_cap_mb=512)
    with pytest.raises(ValueError, match="at least 1, or 0 to switch the step off"):
        base_config(tmp_path, anharmonic_minutes=0.5)
    with pytest.raises(ValueError, match="greater than or equal to 0"):
        base_config(tmp_path, anharmonic_minutes=-1)
    common = ["--name", "m", "--out", str(tmp_path), "--smiles", BENZENE]
    a = P.parse_args([*common, "--anharmonic-minutes", "45", "--anharmonic-shards", "3"])
    assert (a.no_anharmonic, a.anharmonic_minutes, a.anharmonic_shards, a.anharmonic_cap_mb) == (False, 45.0, 3, 1536)
    assert P.parse_args([*common, "--no-anharmonic"]).no_anharmonic and P.parse_args(common).anharmonic_minutes is None
    with pytest.raises(SystemExit):
        P.parse_args([*common, "--no-anharmonic", "--anharmonic-minutes", "45"])
    assert "not allowed with argument" in capsys.readouterr().err


def stubbed_run(monkeypatch: pytest.MonkeyPatch, calls: list[str], preflight: bool = True) -> None:
    if preflight:
        monkeypatch.setattr(AN, "preflight", lambda: None)            # no WSL is asked in these tests
    monkeypatch.setattr(P.MR, "require_carried", lambda p, kind=None: {"status": "carried", "network": P.NETWORK, "version": "pin"})
    monkeypatch.setattr(P, "training_set", lambda models: (("C", "H"), (8, 30)))
    monkeypatch.setattr(P, "start_geometry", lambda cfg: calls.append("start_geometry") or ([], None))
    monkeypatch.setattr(P, "optimise", lambda cfg, xyz, opt: {})
    monkeypatch.setattr(P, "low_level", lambda cfg: {})
    monkeypatch.setattr(P, "correction", lambda models, d: (np.zeros(1), []))
    monkeypatch.setattr(P, "save_correction", lambda *a: None)
    monkeypatch.setattr(P, "spectra", lambda d, dH, dH_seeds: {"network": {"sticks": [{"omega_cm": 700.0}]}})


def stored(tmp_path: Path) -> dict:
    return json.loads((tmp_path / "mol" / "pipeline.json").read_text(encoding="utf-8"))


def progress_of(tmp_path: Path) -> dict:
    return json.loads((tmp_path / "mol" / "progress.json").read_text(encoding="utf-8"))


def test_the_artefact_is_read_before_the_first_step_computes(tmp_path, monkeypatch):
    calls: list[str] = []
    stubbed_run(monkeypatch, calls)

    def broken() -> None:
        raise ValueError("this code or its libraries are not the fit's")

    monkeypatch.setattr(AN, "load_artefact", broken)
    with pytest.raises(ValueError, match="not the fit's"):
        P.run(base_config(tmp_path, reuse_corpus=False))
    assert calls == [] and not (tmp_path / "mol").exists()


def test_the_harmonic_result_is_delivered_complete_before_step_6_starts(tmp_path, monkeypatch):
    """Review finding 2: at the moment the force field would start, the record of steps 1–5 is on disk, says that the step is
    running and what it will add, and has been handed to the certificate's writer once."""
    calls: list[str] = []
    stubbed_run(monkeypatch, calls)
    monkeypatch.setattr(AN, "load_artefact", lambda: "artefact")
    delivered: list[tuple[str, str]] = []
    seen = {}

    def step(req: AN.Request, dH: np.ndarray, out: dict) -> dict:
        first = stored(tmp_path)
        seen.update(req=req, first=first, delivered=list(delivered), progress=progress_of(tmp_path))
        out["network"]["sticks"][0]["nu_cm"] = 690.0
        return out | {"anharmonic": {"status": POS.APPLIED}, "note": "said"}

    monkeypatch.setattr(AN, "step", step)
    rec = P.run(base_config(tmp_path, reuse_corpus=False, threads=6, anharmonic_shards=3, anharmonic_cap_mb=2048, anharmonic_minutes=90),
                lambda folder, what: delivered.append((what, stored(tmp_path)["spectra"]["anharmonic"]["status"])))
    first = seen["first"]
    assert seen["delivered"] == [(P.FIRST_DELIVERY, POS.RUNNING)]
    final_by = first["spectra"]["anharmonic"].pop("final_by")
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}", final_by)
    assert first["spectra"]["anharmonic"] == {"status": POS.RUNNING, "reason": None, "model": "x2*", "budget_minutes": 90.0, "field": None}
    assert f"final by {final_by}" in first["spectra"]["note"] and first["spectra"]["network"]["sticks"][0]["nu_cm"] is None
    assert [(x["number"], x["delivery"], x["final_by"]) for x in first["deliveries"]] == [(1, P.FIRST_DELIVERY, final_by)]
    assert "anharmonic" not in first["seconds"]
    # round two, finding 1: the show has the result now — the run counts as finished at its first delivery, and says what is still to come
    assert seen["progress"]["finished"] is True
    assert seen["progress"]["delivery"] == {"number": 1, "state": f"harmonic delivered, anharmonic step running, final by {final_by}",
                                            "final": False}
    assert progress_of(tmp_path)["delivery"] == {"number": 2, "state": "final: with the anharmonic positions", "final": True}
    assert {"admission", "low_level", "provenance", "commit_at_end", "settings"} <= set(first)
    assert json.loads((tmp_path / "mol" / "progress.json").read_text(encoding="utf-8"))["steps"]["spectrum"]["state"] == "done"
    assert seen["req"] == AN.Request("mol", (tmp_path / "mol").resolve(), BENZENE, "artefact", AN.FieldSettings(3, 2, 2048, 5400))
    assert delivered == [(P.FIRST_DELIVERY, POS.RUNNING), (P.SECOND_DELIVERY, POS.APPLIED)]
    final = stored(tmp_path)
    assert [(x["number"], x["delivery"]) for x in final["deliveries"]] == [(1, P.FIRST_DELIVERY), (2, P.SECOND_DELIVERY)]
    assert final["deliveries"][1]["final_by"] is None and final["spectra"]["note"] == "said"
    assert final["spectra"]["network"]["sticks"][0]["nu_cm"] == 690.0 and "anharmonic" in final["seconds"] == rec["seconds"]
    assert all(x["seconds_since_start"] >= 0 and x["at"] for x in final["deliveries"]) and rec["pipeline_version"] == P.PIPELINE_VERSION == "0.13"


def test_a_step_over_its_budget_ends_in_the_harmonic_result_with_the_reason(tmp_path, monkeypatch):
    calls: list[str] = []
    stubbed_run(monkeypatch, calls)
    monkeypatch.setattr(AN, "load_artefact", lambda: "artefact")
    monkeypatch.setattr(AN, "step", lambda req, dH, out: AN.not_applied(out, POS.timed_out(req.settings.budget_minutes)))
    delivered: list[str] = []
    rec = P.run(base_config(tmp_path, reuse_corpus=False, anharmonic_minutes=30), lambda folder, what: delivered.append(what))
    assert delivered == [P.FIRST_DELIVERY, P.FINAL_HARMONIC] and rec["deliveries"] == stored(tmp_path)["deliveries"]
    assert rec["spectra"]["anharmonic"]["reason"] == POS.timed_out(30) and "python -m m08.anharmonic <result folder>" in rec["spectra"]["note"]
    assert rec["spectra"]["note"].startswith("positions are harmonic (ω): the anharmonic step was not applied — the anharmonic step did not "
                                             "finish within 30 minutes;")
    assert progress_of(tmp_path)["delivery"] == {"number": 2, "state": "final: harmonic, the anharmonic step was not applied", "final": True}
    assert rec["spectra"]["network"]["sticks"][0]["nu_cm"] is None


def test_an_error_in_step_6_cannot_lose_the_record_of_steps_1_to_5(tmp_path, monkeypatch):
    """Review finding 4: the error is raised — after the record is finalised at its harmonic positions with the error as the reason."""
    calls: list[str] = []
    stubbed_run(monkeypatch, calls)
    monkeypatch.setattr(AN, "load_artefact", lambda: "artefact")

    def broken(req: AN.Request, dH: np.ndarray, out: dict) -> dict:
        raise ImportError("No module named 'sklearn'")

    monkeypatch.setattr(AN, "step", broken)
    delivered: list[str] = []
    with pytest.raises(ImportError, match="sklearn"):
        P.run(base_config(tmp_path, reuse_corpus=False), lambda folder, what: delivered.append(what))
    rec = stored(tmp_path)
    assert delivered == [P.FIRST_DELIVERY, P.FINAL_HARMONIC] and [x["delivery"] for x in rec["deliveries"]] == delivered
    assert rec["spectra"]["anharmonic"]["status"] == POS.NOT_APPLIED
    assert rec["spectra"]["anharmonic"]["reason"] == "the anharmonic step failed: ImportError: No module named 'sklearn'"
    assert rec["admission"]["smiles"] == BENZENE and "anharmonic" in rec["seconds"]
    # round two, finding 1: the show is not left waiting — the progress record is finished and names the final, harmonic delivery
    assert progress_of(tmp_path)["finished"] is True and progress_of(tmp_path)["delivery"]["number"] == 2
    assert progress_of(tmp_path)["delivery"]["final"] is True


@pytest.mark.parametrize(("stop", "reason"), [(KeyboardInterrupt(), "the anharmonic step was interrupted: KeyboardInterrupt"),
                                              (SystemExit(3), "the anharmonic step was interrupted: SystemExit: 3")])
def test_an_interrupt_in_step_6_finalises_the_harmonic_result_before_it_is_raised(tmp_path, monkeypatch, stop, reason):
    """Round two, finding 3: Ctrl-C or an exit during step 6 does not leave a certificate that says 'running' for good."""
    calls: list[str] = []
    stubbed_run(monkeypatch, calls)
    monkeypatch.setattr(AN, "load_artefact", lambda: "artefact")

    def interrupted(req: AN.Request, dH: np.ndarray, out: dict) -> dict:
        raise stop

    monkeypatch.setattr(AN, "step", interrupted)
    delivered: list[str] = []
    with pytest.raises(type(stop)):
        P.run(base_config(tmp_path, reuse_corpus=False), lambda folder, what: delivered.append(what))
    rec = stored(tmp_path)
    assert delivered == [P.FIRST_DELIVERY, P.FINAL_HARMONIC] and rec["spectra"]["anharmonic"] == {
        "status": POS.NOT_APPLIED, "reason": reason, "model": "x2*", "field": None}
    assert progress_of(tmp_path)["delivery"]["final"] is True


def test_an_interrupts_reason_names_the_scope_that_may_still_run(tmp_path, monkeypatch):
    """Round three, B: after Ctrl-C the force field's scope in WSL is nobody's child; the certificate's reason names the unit,
    says it may run on until its own time limit, and gives the command that stops it."""
    calls: list[str] = []
    stubbed_run(monkeypatch, calls)
    monkeypatch.setattr(AN, "load_artefact", lambda: "artefact")

    def interrupted(req: AN.Request, dH: np.ndarray, out: dict) -> dict:
        (req.folder / AN.FOLDER).mkdir()
        (req.folder / AN.FOLDER / AN.UNIT_FILE).write_text("m08-anharmonic-mol-0123456789", encoding="utf-8")   # as force_field leaves it
        raise KeyboardInterrupt

    monkeypatch.setattr(AN, "step", interrupted)
    with pytest.raises(KeyboardInterrupt):
        P.run(base_config(tmp_path, reuse_corpus=False))
    assert stored(tmp_path)["spectra"]["anharmonic"]["reason"] == (
        "the anharmonic step was interrupted: KeyboardInterrupt; the force field's scope m08-anharmonic-mol-0123456789.scope may still "
        "run in WSL until its own time limit — `wsl -e systemctl --user stop m08-anharmonic-mol-0123456789.scope` stops it")
    assert AN.scope_note(tmp_path / "no such result") == ""


def test_a_resume_is_a_delivery_like_the_others(tmp_path, monkeypatch):
    """Round three, D: `python -m m08.anharmonic <folder>` on a result that ran out of time — the record gets delivery 3, the
    certificate's pair is written, and the progress record's delivery number moves, which is what makes a live show read again."""
    calls: list[str] = []
    stubbed_run(monkeypatch, calls)
    monkeypatch.setattr(AN, "load_artefact", lambda: "artefact")
    monkeypatch.setattr(AN, "step", lambda req, dH, out: AN.not_applied(out, POS.timed_out(req.settings.budget_minutes)))
    P.run(base_config(tmp_path, reuse_corpus=False))
    d = tmp_path / "mol"
    assert progress_of(tmp_path)["delivery"]["number"] == 2 and [x["number"] for x in stored(tmp_path)["deliveries"]] == [1, 2]
    np.savez(d / P.CORRECTION, dH=np.zeros(1))
    monkeypatch.setattr(AN, "step", lambda req, dH, out: out | {"anharmonic": {"status": POS.APPLIED, "reason": None, "field": {}}, "note": "ν"})
    written = []
    monkeypatch.setattr("m08.catalog.Catalog", lambda: "catalogue")
    monkeypatch.setattr("m08.live_certificate.certificate", lambda folder, catalog: {"delivery": len(stored(tmp_path)["deliveries"])})
    monkeypatch.setattr("m08.live_certificate.write", lambda c, folder: written.append(c) or (folder / "certificate.json", folder / "certificate.md"))
    assert AN.main([str(d), "--minutes", "30"]) == 0
    rec = stored(tmp_path)
    assert [(x["number"], x["delivery"]) for x in rec["deliveries"]] == [(1, P.FIRST_DELIVERY), (2, P.FINAL_HARMONIC), (3, P.RESUMED_DELIVERY)]
    assert rec["spectra"]["note"] == "ν" and written == [{"delivery": 3}]
    assert progress_of(tmp_path)["delivery"] == {"number": 3, "final": True,
                                                 "state": "final: with the anharmonic positions (the step was taken up again)"}
    (d / "progress.json").unlink()                               # a copied result without a progress record is delivered all the same
    rec["spectra"]["anharmonic"] = {"status": POS.NOT_APPLIED, "reason": "x"}
    P.write_json(d / "pipeline.json", rec)
    assert AN.main([str(d)]) == 0 and stored(tmp_path)["deliveries"][-1]["number"] == 4


def test_switched_off_there_is_one_delivery_and_no_force_field(tmp_path, monkeypatch):
    calls: list[str] = []
    stubbed_run(monkeypatch, calls)
    monkeypatch.setattr(AN, "load_artefact", lambda: pytest.fail("the artefact was read although the step is off"))
    monkeypatch.setattr(AN, "step", lambda req, dH, out: pytest.fail("step 6 ran although it is off"))
    monkeypatch.setattr(P, "_run", no_runner)
    delivered: list[str] = []
    rec = P.run(base_config(tmp_path, reuse_corpus=False, anharmonic_minutes=0), lambda folder, what: delivered.append(what))
    assert delivered == [P.ONLY_DELIVERY] and [x["delivery"] for x in rec["deliveries"]] == [P.ONLY_DELIVERY]
    assert rec["spectra"]["anharmonic"]["reason"] == POS.SWITCHED_OFF and rec["spectra"]["network"]["sticks"][0]["nu_cm"] is None
    assert rec["spectra"]["note"].startswith("positions are harmonic (ω)") and rec["settings"]["anharmonic_minutes"] == 0
    assert "anharmonic" not in rec["seconds"]
    assert progress_of(tmp_path)["finished"] is True
    assert progress_of(tmp_path)["delivery"] == {"number": 1, "state": "final: harmonic, the anharmonic step is switched off", "final": True}


def test_the_artefacts_load_predicts_before_any_force_field(monkeypatch):
    """Review finding 4: loading the artefact runs the model on its probe rows, so a missing library fails here, at the start."""
    called = []
    real = AS.predictors
    monkeypatch.setattr(AS, "predictors", lambda name: called.append(name) or real(name))
    AN.load_artefact()
    assert len(called) >= AS.MIN_PROBES
