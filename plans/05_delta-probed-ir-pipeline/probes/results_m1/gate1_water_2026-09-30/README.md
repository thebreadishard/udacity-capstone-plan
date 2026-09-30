# Gate 1 — acceptance tests on water (30 Sep 2026)

The user, 29 Sep 21:3x, after the lambda incident: the launcher refuses an E8/CC run unless water acceptance tests pass on that machine.
Built: `tests/test_acceptance_water.py` (script mode writes `~/.dpir_gate1.json`), `probes/e8_cc_hessian_fd.py` refuses to start without a stamp
from this host, this pyscf and these exact files (`gate1_problem`), and `probes/launch_detached.sh` runs the gate before every E8 launch.

## Counterparts and results (laptop WSL, 8 threads, 30 s; hel1-23, 16 threads, 51 s — same numbers)

| check | counterpart | limit | result |
|---|---|---|---|
| RHF CCSD(T)/cc-pVDZ fc energy | psi4 1.11 on hel1-23, same bohr geometry (`psi4_water_seal.py`, `psi4_water_seal_extract.log`): −76.2413048758 | 1e-7 | 5.5e-10 |
| UHF H2O⁺ energy | psi4 1.11: −75.8024945203 | 1e-7 | 2.2e-9 |
| RHF gradient (probe's `gradient()`, explicit (T) lambda) | central FD (1e-3 bohr) of the CCSD(T) energy, all 9 components | 1e-6 | 1.3e-7 |
| energy at CCCBDB's geometry | CCCBDB R22 CCSD(T)/cc-pVDZ: −76.241305 | 1e-6 | 1.2e-7 |
| force at CCCBDB's geometry | Gaussian's default max force 4.5e-4 (CCCBDB's geometries converge to it) | 4.5e-4 | 2.2e-4 |
| our minimum | CCCBDB 0.9664 Å, 101.964° | 5e-4 Å, 0.1° | 0.96628 Å, 101.913° |
| FD Hessian ω (probe step 0.005, projector, pair check 2.3e-5) | CCCBDB 1690 / 3820 / 3926 (all-electron 1691 / 3824 / 3930) | 2 cm⁻¹ | 1690.2 / 3821.6 / 3927.6 |
| (T) density C kernel | pyscf's Python route (two-route check in the probe) and the gradient through it | 1e-10 / 1e-8 | pass / 6e-15 |
| **UHF gradient (UCCSD(T), explicit `uccsd_t_lambda`)** | central FD of the UCCSD(T) energy | 1e-6 | **4.9e-3 — FAIL** |

## Finding: pyscf 2.14's UCCSD(T) analytic gradient is not dE/dx

`uhf_diag.log`: H2O⁺ 4.9e-3 a.u. off, frozen core or all-electron; triplet water 4.5e-3; UCCSD without (T) agrees to 1.5e-7. pyscf's own
example (`__main__` of `pyscf/grad/uccsd_t.py`, the upstream example this call cites; the wheel ships no test file) prints the analytic
O-z component −0.148416 against its own FD −0.148094, and the reference value in its comment is −0.1480942, the FD number; its second
example (H4) is 9e-4 off (`pyscf_uccsd_t_example.log`). The error sits in the (T) part of the UHF lambda/density route, not in our call.
Consequence: the probe refuses `--spin > 0` (benzene⁺ of anchor set two) until the UHF path passes; the stamp records paths
`{"rhf": true, "uhf": false}` and the gate exits 2. No UHF E8 gradient had been computed before the gate.

## Cause and fix (30 Sep 07:0x–07:2x, laptop)

Localised in four steps on closed-shell water through UHF (`uhf_locate.py`, `uhf_dens.py`, `uhf_d1fg.py`, `uhf_d2map.py`): the UCCSD(T) lambda equals
the RHF (T) lambda to 2e-11; the UHF gradient code with the RHF lambda is still 4.5e-3 off; the unrelaxed (T) densities are right (Tr(H·D) = E_CCSD(T)
to 4e-11, every block equal to RHF to ≤ 1e-10); the `for_grad` d1 equals RHF's and every (T) 2-pdm increment follows the CCSD-level UHF↔RHF map to
≤ 1e-12. That left the gradient-only `compress_vvvv` branch — and pyscf upstream had found it: issue pyscf#3305, fixed by PR #3387 (commit
`aa2ad208`, 9 Aug 2026, after v2.14.0 of 18 Jul; no release carries it yet): the mixed-spin `dvvVV` block is compressed without its factor ½.
Upstream test: `pyscf/grad/test/test_uccsd_t.py` (added by that commit). No PR of ours needed.

Fix here: `install_uccsd_t_dvvvv_fix()` in `e8_cc_hessian_fd.py`, called on the UHF path only; it takes the uncompressed blocks and compresses them
itself with the ½, so it is right on fixed and unfixed pyscf alike (`uccsd_t_fix.py` is the same code as tested). Result (`uhf_diag_after_fix.log`):
H2O⁺ 1.5e-7 (frozen) / 1.6e-7 (all-electron), triplet water 2.3e-7 a.u. against FD of the energy. Gate 1 on the laptop: both paths pass, exit 0
(`gate1_laptop_wsl_after_fix.log`, UHF 1.5e-7). hel1-23 still has the stamp from before the fix (UHF refused) until the gate reruns there.
