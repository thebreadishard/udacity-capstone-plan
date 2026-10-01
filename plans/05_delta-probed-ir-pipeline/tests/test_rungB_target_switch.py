"""e7_rungB_pairs (1 Oct 2026, H9 confirmation): the per-pair target switch exists with the registered default (projected) and the ridge option."""
import re
from pathlib import Path

M05 = Path(__file__).resolve().parents[1] / "modules" / "05_support_predictor" / "m05"


def test_rungb_target_switch_present_with_projected_default():
    text = (M05 / "e7_rungB_pairs.py").read_text(encoding="utf-8")
    assert re.search(r'add_argument\("--target", default="projected", choices=\["projected", "ls"\]', text)
    assert re.search(r'add_argument\("--ls-lam", type=float, default=LAM_REL', text)
    assert 'if a.target == "ls":' in text and "cached_pattern_ls_target(" in text


def test_rungb_pattern_switch_present_with_c_default():
    text = (M05 / "e7_rungB_pairs.py").read_text(encoding="utf-8")
    assert re.search(r'add_argument\("--pattern", default="c", choices=sorted\(PATTERN_REACH\)', text)
    assert 'molecule_pairs(g["symbols"], np.asarray(g["coords_bohr"]), m["F_low"], pattern=a.pattern)' in text


def test_rungb_pair_classes_match_the_trainer():
    """1 Oct 2026: rung B's per-class target scales index by pair class; with patterns d-f the classes reach 8 (the 15:2x IndexError)."""
    import sys
    sys.path.insert(0, str(M05))
    import e7_rungB_pairs as RB
    import rungC_train as RT
    assert RB.PAIR_CLASS == list(RT.PAIR_CLASS_NAMES) and len(RB.PAIR_CLASS) == 9
