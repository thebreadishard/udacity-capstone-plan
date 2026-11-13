"""src/dpir/vpt2_domain.py (TASKS 207): the two diagnostics on a sound mode and on coronene's broken one, the refusals, and the reader's
required question about a marked mode."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from dpir.vpt2_domain import (
    PARTNER_MAX,
    STRAIN_MAX,
    as_record,
    marked_modes,
    mode_domains,
    require_unmarked,
)


def _chi(n: int, diagonal: float = -1.0, couplings: dict[tuple[int, int], float] | None = None) -> np.ndarray:
    chi = np.diag(np.full(n, diagonal))
    for (i, j), v in (couplings or {}).items():
        chi[i, j] = chi[j, i] = v
    return chi


def test_a_sound_mode_is_not_marked():
    # a CH stretch: -172 cm-1 on 3186 is 5.4 %, sound VPT2 and the largest coupling small
    omega, nu = np.array([3186.5, 1600.0]), np.array([3014.1, 1595.0])
    domains = mode_domains(omega, nu, _chi(2, -10.0, {(0, 1): -20.0}))
    assert not any(d.marked for d in domains)
    assert marked_modes(domains) == ()
    assert domains[0].strain == pytest.approx(172.4 / 3186.5, rel=1e-9)
    assert domains[0].partner == 1 and domains[0].partner_share == pytest.approx(20.0 / 3186.5, rel=1e-9)


def test_coronenes_mode_36_is_marked_by_its_strain():
    omega, nu = np.array([642.9, 807.1]), np.array([709.2, 986.3])
    domains = mode_domains(omega, nu, _chi(2, 44.4, {(0, 1): 69.8}))
    assert marked_modes(domains) == (0, 1)
    strained = domains[1]
    assert strained.strain == pytest.approx(179.2 / 807.1, rel=1e-6) and strained.strain > STRAIN_MAX
    assert strained.partner == 0 and strained.partner_share == pytest.approx(69.8 / 807.1, rel=1e-6)
    # mode 36's one coupling is 8.7 % of its own frequency, under the threshold; the same coupling is 10.9 % of mode 24's
    assert [r.split()[0] for r in strained.reasons] == ["strain"]
    assert [r.split()[0] for r in domains[0].reasons] == ["strain", "partner"]


def test_one_coupling_marks_a_mode_whose_total_shift_is_small():
    # +7.3 cm-1 on 89.0 is under the strain threshold; a single x_ij of 12.5 is not
    omega, nu = np.array([89.0, 500.0]), np.array([96.3, 500.5])
    domains = mode_domains(omega, nu, _chi(2, 1.0, {(0, 1): 12.5}))
    assert domains[0].strain < STRAIN_MAX and domains[0].partner_share > PARTNER_MAX
    assert marked_modes(domains) == (0,)
    assert domains[0].reasons == (f"partner share {12.5 / 89.0:.3f} over {PARTNER_MAX}",)


def test_the_diagonal_is_never_a_partner():
    omega, nu = np.array([500.0, 1500.0]), np.array([505.0, 1505.0])
    domains = mode_domains(omega, nu, _chi(2, 400.0, {(0, 1): 1.0}))   # a huge x_ii, a tiny coupling
    assert domains[0].partner == 1 and domains[0].partner_share == pytest.approx(1.0 / 500.0, rel=1e-9)
    assert not domains[0].marked


def test_a_frequency_at_the_floor_is_marked_instead_of_dividing():
    domains = mode_domains(np.array([0.0, 500.0]), np.array([0.0, 505.0]), _chi(2, 1.0))
    assert domains[0].marked and "below the floor" in domains[0].reasons[0]
    assert np.isfinite(domains[0].strain)


def test_shapes_are_refused():
    with pytest.raises(ValueError, match="one value per mode"):
        mode_domains(np.zeros(3), np.zeros(2), _chi(3))
    with pytest.raises(ValueError, match="square on 3 modes"):
        mode_domains(np.zeros(3), np.zeros(3), _chi(2))


def test_a_reader_must_say_what_it_does_with_a_marked_mode():
    clean = as_record(mode_domains(np.array([3186.5]), np.array([3014.1]), _chi(1, -10.0)))
    assert clean["marked"] == [] and clean["diagnostics"] == [] and clean["strain_max"] == STRAIN_MAX
    require_unmarked(clean, "a clean label")

    broken = as_record(mode_domains(np.array([642.9, 807.1]), np.array([709.2, 986.3]), _chi(2, 44.4, {(0, 1): 69.8})))
    assert broken["marked"] == [0, 1] and len(broken["diagnostics"]) == 2
    with pytest.raises(ValueError, match=r"modes \[0, 1\] are outside"):
        require_unmarked(broken, "coronene")
    with pytest.raises(ValueError, match="never checked"):
        require_unmarked({}, "a label from before the check")
