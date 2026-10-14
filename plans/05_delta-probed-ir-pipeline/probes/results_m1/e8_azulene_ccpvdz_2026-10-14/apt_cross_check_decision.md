# Azulene, anchor set three — the APT cross-check failed for a diagnosed cause; the field-route APT is accepted (14 Oct 2026)

**The user, 14 Oct 2026, ≈ 22:0x: 'Optie 1, accepteer de veldroute en haal azuleen op'.**

- Registered line of the field route (`PreRegistration_2026-10-12_Anchor_Set_Three.md`, item 2): translation sum rule ≤ 1e-6 → **1.7e-10, met**.
- Cross-check of `probes/anchor_wave.sh` against the FD-dipole APT (`apt_ccsd_t.npz`), max |ΔP| ≤ 1e-3 e → **2.39e-3, failed** (marker
  '=== (AS3) azulene apt FAIL' 2026-10-14 18:52:05 server time).
- Diagnosis (`probes/apt_symmetry_diagnosis.py`, both files at the same geometry; quinoxaline, which passed, beside it):
  - the corpus geometry is C2v only to 2.6e-3 bohr (quinoxaline 9.7e-5);
  - the field APT deviates from C2v by 3.4e-3 (quinoxaline 5.1e-5) — the same ratio to the geometry's asymmetry: the true APT at this
    geometry is not symmetric;
  - the FD-dipole route symmetrises its APT (spread before averaging 3.0e-3) and breaks the translation sum rule by 1.7e-3 (quinoxaline
    3.7e-5): the reference carries more than the line's 1e-3 itself;
  - both symmetrised, the difference is 1.09e-3; it sits on C0 and C5–C9.
- Decision: the field-route APT (`apt_ccsd_t_field.npz`) is the anchor's APT; the cross-check is recorded as failed for this cause. Open,
  separately: why azulene's corpus geometry is less symmetric than the others, and what that means for its CC Hessian (TASKS 51).
