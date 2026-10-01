"""e7_rungB_pairs (1 Oct 2026, H9 confirmation): the per-pair target switch exists with the registered default (projected) and the ridge option."""
import re
from pathlib import Path

M05 = Path(__file__).resolve().parents[1] / "modules" / "05_support_predictor" / "m05"


def test_rungb_target_switch_present_with_projected_default():
    text = (M05 / "e7_rungB_pairs.py").read_text(encoding="utf-8")
    assert re.search(r'add_argument\("--target", default="projected", choices=\["projected", "ls"\]', text)
    assert re.search(r'add_argument\("--ls-lam", type=float, default=LAM_REL', text)
    assert 'if a.target == "ls":' in text and "cached_pattern_ls_target(" in text
