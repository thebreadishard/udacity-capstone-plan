# Benzonitrile on the anharmonic step's format 3 — result (19 Nov 2026, TASKS 211 step 2)

Run spec `benzonitrile_anharm_v3_2026-11-19`, launched 20:06:31, exit 0; pipeline 0.14, v1.4 release networks, artefact
`x2star_v3.json` (sha16 0bc87e653fb05d6d). Registered before launch in `REGISTRATION_2026-11-19.md`, which says check 1 would
not be read.

| check | result | numbers |
|---|---|---|
| 1. steps within tolerance of an independent field | not read | no stored GFN2-xTB quartic field exists for any substituted molecule outside x2*'s table |
| 2. no band lost | pass, against the registered replay count | 27 of 33 stepped; the 6 without a step are 'unmeasured' (the five lowest, 167.5–467.9 cm⁻¹, and the C≡N stretch at 2386.3); no 'no-xtb-partner' |
| 3. degenerate pairs equal | not applicable | no degenerate pair (C2v) |
| 4. time and memory recorded | pass | 1830.9 s, 1003 MB peak (the search ran beside it; 655.9 s on 17 Nov) |

Against the run of 17 Nov (information, not a check: the same code on the same geometry): all 27 steps agree to 0.1 cm⁻¹.

What this does not show: that the step is right for a substituted molecule — that needs an independent field (check 1). The
substituent's own band (C≡N) is printed harmonic. At 1831 s beside the search the force field alone exceeds the demo's half hour.
