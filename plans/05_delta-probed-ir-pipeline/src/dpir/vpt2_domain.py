"""Is second-order perturbation theory inside its domain for a mode? (TASKS 207, registered 13 November 2026.)

VPT2 writes a fundamental as the harmonic frequency plus a second-order correction. The correction is only meaningful while it stays
small against the frequency it corrects. Coronene's mode 36 (807.1 cm⁻¹, out of plane) shows what happens when it does not: D6h forbids
the cubic constants that cancel the quartic term, so 2x_ii = 2·φ_iiii/16 = +88.75 cm⁻¹ lands whole on the fundamental beside +90.45 from
its partners, of which +34.9 from mode 24 alone (x(24,36) = +69.8). The label reads +179.2, 22 % of ω, and S3's 'other' family then reads
rms 41.18 cm⁻¹ where the other 23 modes give 3.84.

Two diagnostics mark a mode, each of them a ratio to the mode's own harmonic frequency:

    strain         |ν − ω| / ω          the whole correction
    partner share  max_{j≠i} |x_ij| / ω_i   the largest single two-mode coupling

Both thresholds are 0.10, set from the labels we had on 13 November 2026 (2,028 modes in 36 force fields): the strain's median is 0.018,
its 99th percentile 0.052, and the CH stretches — where a −170 cm⁻¹ correction is sound VPT2 — sit at 0.054 to 0.056. Above that the
distribution is empty until the four broken modes at 0.166, 0.193, 0.222 and 0.388. A threshold of 0.10 therefore separates sound
anharmonicity from breakdown with a wide margin on both sides, and marks 8 modes in 5 of those force fields, beside coronene's 24 and 36.
The partner share catches a mode whose correction is carried by one coupling even when the total stays small; it marks conservatively,
because a marked mode is not discarded but solved without perturbation theory (TASKS 209).

A marked mode is a measurement this method cannot make. Nothing here drops one: the marks travel with the label, and every reader
states what it does with them (`marked_to_drop`, one of MARKED_POLICIES), so no marked mode can enter a fit unnoticed.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

STRAIN_MAX = 0.10          # |nu - omega| / omega
PARTNER_MAX = 0.10         # max_{j != i} |x_ij| / omega_i
OMEGA_FLOOR_CM = 1.0       # a frequency below this is not a denominator; such a mode is marked outright
MARKED_POLICIES = ("raise", "exclude", "keep")   # what a reader may do with a marked mode; it states one, there is no default


@dataclass(frozen=True)
class ModeDomain:
    """One mode's VPT2 diagnostics and the reasons, if any, that put it outside the theory's domain."""

    mode: int
    omega_cm: float
    nu_cm: float
    strain: float
    partner: int
    partner_share: float
    reasons: tuple[str, ...]

    @property
    def marked(self) -> bool:
        """True when any diagnostic put this mode outside the domain."""
        return bool(self.reasons)

    def as_record(self) -> dict[str, float | int | list[str]]:
        """The json form that travels with the label."""
        return {"mode": self.mode, "omega_cm": self.omega_cm, "nu_cm": self.nu_cm, "strain": self.strain,
                "partner": self.partner, "partner_share": self.partner_share, "reasons": list(self.reasons)}


def _reasons(strain: float, partner_share: float, omega_cm: float) -> tuple[str, ...]:
    """The named diagnostics this mode fails, in the order they are documented."""
    out = []
    if omega_cm < OMEGA_FLOOR_CM:
        out.append(f"omega {omega_cm:.3f} cm-1 below the floor {OMEGA_FLOOR_CM}")
    if strain > STRAIN_MAX:
        out.append(f"strain {strain:.3f} over {STRAIN_MAX}")
    if partner_share > PARTNER_MAX:
        out.append(f"partner share {partner_share:.3f} over {PARTNER_MAX}")
    return tuple(out)


def mode_domains(omega_cm: np.ndarray, nu_cm: np.ndarray, chi_cm: np.ndarray) -> list[ModeDomain]:
    """Every mode's diagnostics. `nu_cm` is the label that will be written (after any variational resonance step); `chi_cm` is the
    deperturbed anharmonicity matrix the same VPT2 call produced."""
    omega, nu, chi = np.asarray(omega_cm, float), np.asarray(nu_cm, float), np.asarray(chi_cm, float)
    if omega.ndim != 1 or nu.shape != omega.shape:
        raise ValueError(f"omega {omega.shape} and nu {nu.shape}: one value per mode")
    if chi.shape != (omega.size, omega.size):
        raise ValueError(f"chi {chi.shape}: square on {omega.size} modes")
    denominator = np.maximum(np.abs(omega), OMEGA_FLOOR_CM)
    off_diagonal = chi - np.diag(np.diag(chi))
    strain = np.abs(nu - omega) / denominator
    share = np.abs(off_diagonal) / denominator[:, None]
    partner = share.argmax(axis=1) if omega.size > 1 else np.zeros(omega.size, int)
    return [ModeDomain(i, float(omega[i]), float(nu[i]), float(strain[i]), int(partner[i]),
                       float(share[i, partner[i]]), _reasons(float(strain[i]), float(share[i, partner[i]]), float(omega[i])))
            for i in range(omega.size)]


def marked_modes(domains: list[ModeDomain]) -> tuple[int, ...]:
    """The modes outside the domain, in order."""
    return tuple(d.mode for d in domains if d.marked)


def as_record(domains: list[ModeDomain]) -> dict[str, object]:
    """What a label stores: the thresholds it was marked against, the marked modes, and every marked mode's diagnostics."""
    return {"strain_max": STRAIN_MAX, "partner_max": PARTNER_MAX, "omega_floor_cm": OMEGA_FLOOR_CM,
            "marked": list(marked_modes(domains)), "diagnostics": [d.as_record() for d in domains if d.marked]}


def marked_to_drop(marked: Sequence[int] | None, policy: str, context: str) -> tuple[int, ...]:
    """The modes a reader must leave out, under its stated policy. Every reader of a label states one, so no marked mode enters a fit
    unnoticed and no reader carries a default:

        raise    refuse the label outright (the reader has no treatment for a marked mode)
        exclude  leave the marked modes out, and say in the report how many went
        keep     use them anyway, for a comparison that means to show what they do

    `marked` is a label's `vpt2_domain["marked"]`, or the marked modes of a molecule already loaded. None means the label was written
    before this check; that is refused under every policy, because unchecked is not clean — relabel it.
    """
    if policy not in MARKED_POLICIES:
        raise ValueError(f"{context}: policy {policy!r}, one of {MARKED_POLICIES}")
    if marked is None:
        raise ValueError(f"{context}: no vpt2_domain record, so these modes were never checked against VPT2's domain (TASKS 207)")
    found = tuple(int(i) for i in marked)
    if policy == "raise" and found:
        raise ValueError(f"{context}: modes {list(found)} are outside VPT2's domain (TASKS 207); say what to do with them")
    return found if policy == "exclude" else ()
