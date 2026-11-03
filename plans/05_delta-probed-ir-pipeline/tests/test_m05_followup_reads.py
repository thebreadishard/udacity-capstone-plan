"""m05/followup_reads.py: the readers shared by module 05's notebook builder and report return the committed records' numbers that
section 12 quotes, and None for an absent record."""
import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "modules" / "05_support_predictor" / "m05" / "followup_reads.py"
spec = importlib.util.spec_from_file_location("followup_reads", SCRIPT)
reads = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reads)


def test_absent_records_read_as_none():
    assert reads.record("no_such_record.json") is None
    assert reads.seed_mean("no_such_record", 750) is None
    assert reads.family_read("no_such_record") is None
    assert reads.coverage_parent("no_such_tag", "benzene") is None


def test_chain24_as_section_12_2_quotes_it():
    assert reads.seed_mean("E7_rungC_carried_kd_750_saved_2026-10-02", 750) == pytest.approx(0.22, abs=0.005)
    per_family = reads.family_read("E7_rungC_carried_kd_750_saved_2026-10-02").per_family
    assert per_family["ring-ip"] == pytest.approx(2.30, abs=0.005)
    assert per_family["other"] == pytest.approx(4.14, abs=0.005)


def test_matched_pairing_as_section_12_6_quotes_it():
    m = reads.matched_pairing_means()
    assert m["intensity_rel_rms_matched"] == pytest.approx(0.127, abs=0.0005)
    assert m["intensity_rel_rms_zero_rule_matched"] == pytest.approx(0.296, abs=0.0005)
