"""The pipeline's anharmonic step (`m08/anharmonic.py`, TASKS 211) and the sentences about positions (`m08/positions.py`): every
switch and every wording branch, on the frozen corpus's benzene with the committed artefact. No GFN2-xTB runs here: the force field
is a stand-in built from the molecule's own B3LYP modes, and the WSL runner is replaced where a test is about its failures. What the
certificate and the pages print is in tests/test_m08_positions_pages.py."""
from __future__ import annotations

import json
import sys
from pathlib import Path

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

SETTINGS = AN.FieldSettings.of(4, 2, 1536)
BARS = {"ring-ip": 3.37, "other": 3.84, "CH-oop": 8.38, "CH-stretch": 6.21}


@pytest.fixture(scope="module")
def artefact() -> AS.Artefact:
    return AN.load_artefact()


def stand_in_field(d: Path, marked: tuple[int, ...] = ()) -> AS.XtbField:
    """A force field whose modes are the molecule's B3LYP modes (every overlap 1) and whose shifts are 1 % of ω, downwards."""
    symbols, coords, _ = AN.geometry(d)
    modes = AN.b3lyp_modes(symbols, coords, AN.low_hessian(d))
    mask = np.zeros(len(modes.omega), bool)
    mask[list(marked)] = True
    return AS.XtbField(-0.01 * modes.omega, mask, modes.q)


def spectra_of(d: Path) -> dict:
    return json.loads((d / "pipeline.json").read_text(encoding="utf-8"))["spectra"]


def stepped(d: Path, artefact: AS.Artefact, monkeypatch: pytest.MonkeyPatch, dH: np.ndarray = ZERO, marked: tuple[int, ...] = ()) -> dict:
    """The folder with the pipeline's record of `dH` and step 6 applied on the stand-in field; the record's spectra."""
    record(d, dH, [dH])
    monkeypatch.setattr(AN, "force_field", lambda name, folder, s: (stand_in_field(folder, marked), {"seconds": 1.0, "peak_memory_mb": 7}))
    out = AN.step(AN.Request("benzene", d, artefact, SETTINGS), dH, spectra_of(d))
    rec = json.loads((d / "pipeline.json").read_text(encoding="utf-8"))
    P.write_json(d / "pipeline.json", rec | {"spectra": out})
    return out


def no_runner(*args: object) -> int:
    raise AssertionError("the WSL runner was started")


# ---------------------------------------------------------------- the step

def test_the_step_gives_every_band_its_position_and_its_reason(result, artefact, monkeypatch):  # noqa: F811
    out = stepped(result, artefact, monkeypatch)
    sticks, s = out["network"]["sticks"], out["anharmonic"]
    assert s["status"] == POS.APPLIED and s["model"] == "x2*" and s["artefact"]["bars_cm"] == BARS
    assert s["artefact"]["file"] == "probes/anharmonic_step/x2star_v1.json" and s["field"]["peak_memory_mb"] == 7
    assert len(sticks) == 30 and s["bands"]["stepped"] + sum(s["bands"]["no_step"].values()) == 30
    for stick in sticks:
        a = stick["anharmonic"]
        if a["delta_anh_cm"] is None:
            assert stick["nu_cm"] is None and a["reason"] == AS.UNMEASURED and a["bar_cm"] is None and stick["omega_cm"] < 550
        else:
            assert stick["nu_cm"] == round(stick["omega_cm"] + a["delta_anh_cm"], 1) and a["bar_cm"] == BARS[a["family"]]
            assert a["reason"] is None and a["overlap"] == pytest.approx(1.0)
    assert s["bands"]["no_step"] == {AS.UNMEASURED: sum(x["omega_cm"] < 550 for x in sticks)} and s["bands"]["no_step"][AS.UNMEASURED] > 0
    assert sum(x["anharmonic"]["family"] == "CH-stretch" and x["nu_cm"] is not None for x in sticks) == 6
    flagged = [x for x in sticks if x["anharmonic"]["error_not_measured"]]
    assert len(flagged) == s["bands"]["error_not_measured"] > 0 and all(x["anharmonic"]["family"] == "other" for x in flagged)
    saved = json.loads((result / AN.RECORD).read_text(encoding="utf-8"))
    assert len(saved["modes"]) == 30 and [b["nu_cm"] for b in saved["bands"]] == [x["nu_cm"] for x in sticks]
    assert out["note"] == POS.note(s) and f"for {s['bands']['stepped']} of 30 bands" in out["note"]


def test_a_marked_xtb_partner_leaves_its_band_harmonic(result, artefact, monkeypatch):  # noqa: F811
    out = stepped(result, artefact, monkeypatch, marked=(12,))
    refused = [x for x in out["network"]["sticks"] if x["anharmonic"]["reason"] == AS.XTB_PARTNER_MARKED]
    assert len(refused) == 1 and refused[0]["anharmonic"]["b3lyp_mode"] == 12 and refused[0]["nu_cm"] is None
    assert out["anharmonic"]["bands"]["no_step"][AS.XTB_PARTNER_MARKED] == 1


def test_the_step_follows_the_mode_not_the_rank(result, artefact, monkeypatch):  # noqa: F811
    """A correction that lifts B3LYP mode 9 above the modes over it: the band keeps mode 9's step at its new rank, and the bands
    it passed keep theirs."""
    _, _, masses = AN.geometry(result)
    H = AN.low_hessian(result)
    modes = AN.b3lyp_modes(*AN.geometry(result)[:2], H)
    target = float(modes.omega[11]) + 5.0
    passed = int((modes.omega[10:] < target).sum())
    out = stepped(result, artefact, monkeypatch, dH=with_mode_at(H, masses, 9, target) - H)
    sticks = out["network"]["sticks"]
    moved = next(i for i, x in enumerate(sticks) if x["anharmonic"]["b3lyp_mode"] == 9)
    assert passed >= 2 and moved == 9 + passed and sticks[moved]["omega_cm"] == round(target, 1)
    assert [x["anharmonic"]["b3lyp_mode"] for x in sticks[9:moved + 1]] == [*range(10, 10 + passed), 9]
    plain = AS.mode_steps(modes, stand_in_field(result), artefact)[9]
    assert sticks[moved]["anharmonic"]["delta_anh_cm"] == round(plain.delta_anh_cm, 1) and sticks[moved]["anharmonic"]["family"] == plain.family


def test_switched_off_the_step_computes_nothing_and_says_so(result, monkeypatch):  # noqa: F811
    record(result, ZERO, [ZERO])
    monkeypatch.setattr(P, "_run", no_runner)
    out = AN.step(AN.Request("benzene", result, None, SETTINGS), ZERO, spectra_of(result))
    assert out["anharmonic"] == {"status": POS.NOT_APPLIED, "reason": POS.SWITCHED_OFF, "model": "x2*", "field": None}
    assert all(x["nu_cm"] is None and x["anharmonic"] is None for x in out["network"]["sticks"])
    assert out["note"] == f"positions are harmonic (ω): the anharmonic step was not applied — {POS.SWITCHED_OFF}"
    assert not (result / AN.RECORD).exists() and not (result / AN.FOLDER).exists()


def test_an_element_the_model_never_saw_gets_no_force_field(result, artefact, monkeypatch):  # noqa: F811
    record(result, ZERO, [ZERO])
    g = json.loads((result / "geometry.json").read_text(encoding="utf-8"))
    g["symbols"][6] = "F"
    P.write_json(result / "geometry.json", g)
    monkeypatch.setattr(P, "_run", no_runner)
    out = AN.step(AN.Request("benzene", result, artefact, SETTINGS), ZERO, spectra_of(result))
    assert out["anharmonic"]["status"] == POS.NOT_APPLIED and "element(s) F outside the anharmonic model's training set" in out["note"]


def test_modes_the_force_field_cannot_take_keep_the_run_alive(result, artefact, monkeypatch):  # noqa: F811
    """A B3LYP Hessian with a mode under dpir.qff's line (a near-free rotor): harmonic positions with the reason, no xtb run."""
    _, _, masses = AN.geometry(result)
    with np.load(result / P.RI.LOW_HESSIAN) as z:
        arrays = {k: z[k] for k in z.files}
    np.savez(result / P.RI.LOW_HESSIAN, **(arrays | {"H_projected": with_mode_at(arrays["H_projected"], masses, 0, 5.0)}))
    record(result, ZERO, [ZERO])
    monkeypatch.setattr(P, "_run", no_runner)
    out = AN.step(AN.Request("benzene", result, artefact, SETTINGS), ZERO, spectra_of(result))
    assert out["anharmonic"]["status"] == POS.NOT_APPLIED and "the B3LYP modes are not the 3N−6 the force field needs" in out["note"]


@pytest.mark.parametrize(("rc", "log", "expect"), [
    (1, "=== (XTB) benzene: start\n=== (ANH) FAILED: the force field is NOISY (dpir.qff's noise guard), so it is not used 2026-11-16 20:00:00\n",
     "could not be made: the force field is NOISY (dpir.qff's noise guard), so it is not used (anharmonic_field.log)"),
    (2, "wsl_capped.sh: systemd-run missing - no cap, not run\n", "could not be made: exit 2 (anharmonic_field.log)"),
    (137, "KILLED: over the cap of 1536 MB\n", "was stopped at the WSL cap of 1536 MB (anharmonic_field.log)"),
    (0, "=== (ANH) done: benzene in 5 s 2026-11-16 20:00:05\n", "cannot be read: ")])
def test_a_force_field_that_fails_leaves_harmonic_positions_with_the_reason(result, artefact, monkeypatch, rc, log, expect):  # noqa: F811
    record(result, ZERO, [ZERO])

    def runner(argv: list[str], log_path: Path, what: str) -> int:
        log_path.write_text(log, encoding="utf-8")
        return rc

    monkeypatch.setattr(P, "_run", runner)
    out = AN.step(AN.Request("benzene", result, artefact, SETTINGS), ZERO, spectra_of(result))
    s = out["anharmonic"]
    assert s["status"] == POS.NOT_APPLIED and expect in s["reason"] and out["note"].startswith("positions are harmonic (ω)")
    assert all(x["nu_cm"] is None for x in out["network"]["sticks"]) and not (result / AN.RECORD).exists()
    assert s["field"]["cap_mb"] == 1536 and s["field"]["log"] == AN.LOG            # the failed run's record is kept
    assert (result / AN.FOLDER / "G" / "ref.json").is_file()            # the reference record the runner starts from was written


def test_the_runner_reports_its_peak_memory_and_time(result, artefact, monkeypatch):  # noqa: F811
    """`force_field` reads the script's markers; the stand-in's files are absent, so the read fails after the record is made."""
    def runner(argv: list[str], log_path: Path, what: str) -> int:
        log_path.write_text("=== (ANH) peak memory 612 MB (the scope's memory.peak, page cache included) 2026-11-16 20:00:05\n", encoding="utf-8")
        return 0

    monkeypatch.setattr(P, "_run", runner)
    seen = {}
    monkeypatch.setattr(AS.XtbField, "from_folder", classmethod(lambda cls, x, label: seen.update(x=x, label=label) or "field"))
    field, rec = AN.force_field("benzene", result, SETTINGS)
    assert field == "field" and rec["peak_memory_mb"] == 612 and rec["shards"] == 2 and rec["omp_threads"] == 2 and rec["cap_mb"] == 1536
    assert seen["x"].endswith(str(Path("anharmonic") / "xtb" / "benzene" / "X")) and seen["label"].endswith("benzene.json")


def test_the_field_command_is_the_capped_script_with_its_settings(tmp_path):
    d = (tmp_path / "mol").resolve()
    inner = AN.field_command("mol", d, AN.FieldSettings.of(6, 3, 2048))[-1]
    assert AN.field_command("mol", d, SETTINGS)[:4] == ["wsl.exe", "-e", "bash", "-lc"]
    assert inner.startswith("export SHARDS=3 OMP_NUM_THREADS=2 PYTHONUNBUFFERED=1; bash ") and "/probes/wsl_capped.sh 2048 -- bash " in inner
    assert inner.endswith(f"/probes/xtb_field_for_step.sh mol {P.wsl_path(d / 'anharmonic' / 'G')} {P.wsl_path(d / 'anharmonic')}")
    assert AN.field_command("mol", d, SETTINGS, dry=True)[-1].endswith(" --dry-run")


@pytest.mark.parametrize("args", [(4, 0, 1536), (4, 2, 512)])
def test_field_settings_that_cannot_run_are_refused(args):
    with pytest.raises(ValueError, match="at least one"):
        AN.FieldSettings.of(*args)


def test_more_threads_than_shards_share_out_and_fewer_still_give_one():
    assert AN.FieldSettings.of(8, 2, 1536).omp_threads == 4 and AN.FieldSettings.of(1, 2, 1536).omp_threads == 1


def test_a_record_whose_sticks_are_not_its_hessians_is_refused(result, artefact, monkeypatch):  # noqa: F811
    record(result, ZERO, [ZERO])
    out = spectra_of(result)
    out["network"]["sticks"][5]["omega_cm"] += 1.0
    monkeypatch.setattr(AN, "force_field", lambda name, folder, s: (stand_in_field(folder), {}))
    with pytest.raises(RuntimeError, match="not the one H_low"):
        AN.step(AN.Request("benzene", result, artefact, SETTINGS), ZERO, out)


# ---------------------------------------------------------------- the sentences

APPLIED = {"status": POS.APPLIED, "reason": None, "model": "x2*",
           "bands": {"stepped": 24, "error_not_measured": 2, "no_step": {"unmeasured": 5, "mixed-band": 1}}}


def test_the_note_is_true_with_and_without_the_step():
    on = POS.note(APPLIED)
    assert "anharmonic position ν = ω + Δ_anh for 24 of 30 bands" in on and "the harmonic position ω for the other 6" in on
    assert "force field; for 2 of them the step's error is not measured for that kind of mode, and no bar is printed)" in on
    assert POS.LICENCE_SCOPE in on and POS.NO_LICENCE_FOR_NU in on
    assert "not measured" not in POS.note(APPLIED | {"bands": APPLIED["bands"] | {"error_not_measured": 0}})
    off = POS.note({"status": POS.NOT_APPLIED, "reason": "no force field"})
    assert off == "positions are harmonic (ω): the anharmonic step was not applied — no force field" and "licen" not in off
    assert POS.summary_of({}) == {"status": POS.NOT_APPLIED, "reason": POS.BEFORE_THE_STEP}
    assert POS.summary_of({"anharmonic": APPLIED}) is APPLIED


def _stick(delta: float | None, reason: str | None = None, flag: bool = False) -> dict:
    return {"omega_cm": 1000.0, "nu_cm": None if delta is None else round(1000.0 + delta, 1),
            "anharmonic": {"delta_anh_cm": delta, "bar_cm": None if delta is None else 3.84, "reason": reason, "error_not_measured": flag,
                           "family": "other", "b3lyp_mode": 3, "overlap": 0.9}}


def test_a_band_says_which_position_it_prints_in_each_of_its_four_cases():
    band = lambda stick, summary=APPLIED: POS.band(stick, summary, AS.REASON_TEXT, AS.NOT_MEASURED_TEXT)   # noqa: E731
    with_bar = band(_stick(-12.3))
    assert (with_bar["printed_cm"], with_bar["printed"], with_bar["nu_cm"], with_bar["delta_anh_cm"]) == (987.7, POS.ANHARMONIC, 987.7, -12.3)
    assert with_bar["anharmonic_bar_cm"] == 3.84 and with_bar["anharmonic_error_measured"] is True
    assert with_bar["position_note"] == ("anharmonic estimate ν = ω + Δ_anh, ± 3.84 cm⁻¹ (the measured rms of family other on coronene "
                                         "and tetracene); no licence is claimed for ν")
    without = band(_stick(-12.3, flag=True))
    assert without["printed_cm"] == 987.7 and without["anharmonic_bar_cm"] is None and without["anharmonic_error_measured"] is False
    assert without["position_note"] == (f"anharmonic estimate ν = ω + Δ_anh, printed without an error bar: {AS.NOT_MEASURED_TEXT}; "
                                        "no licence is claimed for ν")
    for code in (AS.LARGE_AMPLITUDE, AS.NO_XTB_PARTNER, AS.XTB_PARTNER_MARKED, AS.UNMEASURED, AS.MIXED_BAND):
        refused = band(_stick(None, code))
        assert (refused["printed_cm"], refused["printed"], refused["nu_cm"], refused["no_step_reason"]) == (1000.0, POS.HARMONIC, None, code)
        assert refused["position_note"] == f"harmonic position, no anharmonic step: {AS.REASON_TEXT[code]}"
    off = band({"omega_cm": 1000.0}, {"status": POS.NOT_APPLIED, "reason": "no force field"})
    assert off["printed"] == POS.HARMONIC and off["no_step_reason"] == POS.NOT_APPLIED and off["position_note"].endswith("— no force field")
    assert band(_stick(-12.3), {"status": POS.NOT_APPLIED, "reason": "x"})["nu_cm"] is None     # the summary decides, not a stray block
    with pytest.raises(ValueError, match="no anharmonic block"):
        band({"omega_cm": 1000.0})


def test_no_sentence_about_nu_can_be_read_as_a_licence():
    """The words 'licensed'/'licence' reach a ν only in a denial, and the licence's scope names ω."""
    assert "on the harmonic position ω" in POS.LICENCE_SCOPE and "says nothing about the anharmonic position ν" in POS.LICENCE_SCOPE
    for text in (POS.NO_LICENCE_FOR_NU, POS.band(_stick(-1.0), APPLIED, AS.REASON_TEXT, AS.NOT_MEASURED_TEXT)["position_note"],
                 POS.band(_stick(-1.0, flag=True), APPLIED, AS.REASON_TEXT, AS.NOT_MEASURED_TEXT)["position_note"]):
        assert "no licence is claimed for ν" in text and "licensed" not in text.replace("not licensed", "")


# ---------------------------------------------------------------- the pipeline's switch

def base_config(tmp_path: Path, **kw: object) -> P.PipelineConfig:
    return P.PipelineConfig(**(dict(name="mol", out_root=tmp_path, smiles="c1ccccc1", models=(PIN_MODEL,), psi4_python=Path(sys.executable)) | kw))


def test_the_step_is_on_by_default_and_its_settings_are_checked_up_front(tmp_path):
    cfg = base_config(tmp_path)
    assert cfg.anharmonic is True and (cfg.anharmonic_shards, cfg.anharmonic_cap_mb) == (2, 1536)
    with pytest.raises(ValueError, match="more processes than cores"):
        base_config(tmp_path, threads=2, anharmonic_shards=4)
    with pytest.raises(ValueError, match="greater than or equal to 1024"):
        base_config(tmp_path, anharmonic_cap_mb=512)
    a = P.parse_args(["--name", "m", "--out", str(tmp_path), "--smiles", "c1ccccc1", "--no-anharmonic", "--anharmonic-shards", "3"])
    assert a.no_anharmonic and a.anharmonic_shards == 3 and a.anharmonic_cap_mb == 1536
    assert not P.parse_args(["--name", "m", "--out", str(tmp_path), "--smiles", "c1ccccc1"]).no_anharmonic


def stubbed_run(monkeypatch: pytest.MonkeyPatch, calls: list[str]) -> None:
    monkeypatch.setattr(P.MR, "require_carried", lambda p: {"status": "carried", "network": P.NETWORK, "version": "pin"})
    monkeypatch.setattr(P, "training_set", lambda models: (("C", "H"), (8, 30)))
    monkeypatch.setattr(P, "start_geometry", lambda cfg: calls.append("start_geometry") or ([], None))
    monkeypatch.setattr(P, "optimise", lambda cfg, xyz, opt: {})
    monkeypatch.setattr(P, "low_level", lambda cfg: {})
    monkeypatch.setattr(P, "correction", lambda models, d: (np.zeros(1), []))
    monkeypatch.setattr(P, "save_correction", lambda *a: None)
    monkeypatch.setattr(P, "spectra", lambda d, dH, dH_seeds: {"network": {"sticks": [{"omega_cm": 700.0}]}})


def test_the_artefact_is_read_before_the_first_step_computes(tmp_path, monkeypatch):
    calls: list[str] = []
    stubbed_run(monkeypatch, calls)

    def broken() -> None:
        raise ValueError("cannot be traced to a read")

    monkeypatch.setattr(AN, "load_artefact", broken)
    with pytest.raises(ValueError, match="cannot be traced"):
        P.run(base_config(tmp_path, reuse_corpus=False))
    assert calls == [] and not (tmp_path / "mol").exists()


def test_a_run_hands_step_6_its_request_and_records_its_time(tmp_path, monkeypatch):
    calls: list[str] = []
    stubbed_run(monkeypatch, calls)
    monkeypatch.setattr(AN, "load_artefact", lambda: "artefact")
    seen = {}

    def step(req: AN.Request, dH: np.ndarray, out: dict) -> dict:
        seen["req"] = req
        return out | {"note": "said"}

    monkeypatch.setattr(AN, "step", step)
    rec = P.run(base_config(tmp_path, reuse_corpus=False, threads=6, anharmonic_shards=3, anharmonic_cap_mb=2048))
    assert seen["req"] == AN.Request("mol", (tmp_path / "mol").resolve(), "artefact", AN.FieldSettings(3, 2, 2048))
    assert rec["spectra"]["note"] == "said" and "anharmonic" in rec["seconds"] and rec["pipeline_version"] == "0.11"
    assert json.loads((tmp_path / "mol" / "progress.json").read_text(encoding="utf-8"))["steps"]["spectrum"]["state"] == "done"


def test_no_anharmonic_runs_no_force_field_and_the_record_says_switched_off(tmp_path, monkeypatch):
    calls: list[str] = []
    stubbed_run(monkeypatch, calls)
    monkeypatch.setattr(AN, "load_artefact", lambda: pytest.fail("the artefact was read although the step is off"))
    monkeypatch.setattr(P, "_run", no_runner)
    rec = P.run(base_config(tmp_path, reuse_corpus=False, anharmonic=False))
    assert rec["spectra"]["anharmonic"]["reason"] == POS.SWITCHED_OFF and rec["spectra"]["network"]["sticks"][0]["nu_cm"] is None
    assert rec["spectra"]["note"].startswith("positions are harmonic (ω)") and rec["settings"]["anharmonic"] is False
