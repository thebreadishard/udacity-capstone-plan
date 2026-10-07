"""Chain 33c's promotion rule (7 Oct 2026): VALID composites are promoted; where the cc-pVDZ anchor was IMAGINARY the two softest modes must lie
within 40 cm⁻¹ of ωB97X."""
import sys
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import composite_promote as CP  # noqa: E402


def _rec(status="VALID", n_im=0, soft=(86.0, 115.0), ref=(105.0, 126.0)):
    return dict(status=status, n_imaginary=n_im, freq_composite=list(soft) + [200.0], dft={"wb97x": list(ref) + [300.0]})


def test_valid_is_promoted_and_imaginary_is_not():
    assert CP.decide(_rec(), dz_was_imaginary=False)[0]
    ok, why = CP.decide(_rec(status="IMAGINARY", n_im=1), dz_was_imaginary=False)
    assert not ok and "imaginary" in why


def test_soft_mode_line_applies_only_to_repaired_anchors():
    assert CP.decide(_rec(), dz_was_imaginary=True)[0]                                   # anthracene's test 3 numbers: 19 and 11 cm⁻¹ off
    far = _rec(soft=(40.0, 115.0))
    assert not CP.decide(far, dz_was_imaginary=True)[0] and CP.decide(far, dz_was_imaginary=False)[0]
    assert not CP.decide(dict(_rec(), dft={}), dz_was_imaginary=True)[0]
