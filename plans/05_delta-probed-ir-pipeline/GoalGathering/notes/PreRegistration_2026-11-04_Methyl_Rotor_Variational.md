# The methyl rotor of 4-methylimidazole: a torsion scan and a variational torsion + bend check (registered 4 Nov 2026, 09:4x, before any computation)

The user, 4 Nov 2026: 'Ja, doe optie 4 met optie 2 ernaast.' TASKS 156 (c): taking the methyl torsion out of the VPT2 of
4-methyl-1H-imidazole (`Cc1c[nH]cn1`, corpus id B_151c8ce719, B3LYP/6-31G*, grid 75/302) moves its CH3 bends by 6.5 and 3.3 cm⁻¹, and by
the same amount in Z-matrix internals (TASKS 173), so the torsion–bend coupling is real at VPT2 level. Whether VPT2 treats it right for a
rotor with a microwave barrier V3 = 317.20 cm⁻¹ (Gougoula et al., J. Chem. Phys. 2019, read from repository records; to be checked in the
paper before a document cites it) is what a variational treatment can tell. Methods and prices: `reports/Methylrotor in anharmonische IR.md`.

## Level, geometry and coordinates (fixed now)

B3LYP/6-31G*, grid 75/302, conv_tol 1e-11, pyscf in WSL `~/qc05` with the Hessian runs' RKS settings (`rks_setup`, `converged_scf`) — the
level of the force field. Reference geometry: the G setting's reference record (`s2/B_151c8ce719/G/refhess/ref.json`), its reduced normal
modes by `dpir.qff.harmonic`. Atoms (0-based): 0 methyl C, 1 C4, 2 C5, 3 N1(H), 4 C2, 5 N3, 6–8 methyl H. Torsion τ: the dihedral
H6–C0–C1–C2. CH3 bends: modes 20 and 21 (harmonic 1507.5 and 1521.1 cm⁻¹), the two whose VPT2 values move most when the torsion leaves.

## A — the relaxed torsion scan (option 2)

τ = τ₀ + 10° k, k = 0 … 12 (τ₀ the reference value), every other coordinate optimised by geomeTRIC through pyscf with the dihedral set
(`$set dihedral 7 1 2 3 <τ>`; upstream: geomeTRIC `tests/test_prepare.py` for the constraint syntax, pyscf `geomopt/geometric_solver.py`
`optimize(..., constraints=)`). Each optimised point must hold its dihedral within 0.05°, or the run stops.

Read (`probes/methyl_rotor_read.py scan`): (i) the scan is periodic: |E(k = 12) − E(k = 0)| ≤ 0.5 cm⁻¹, else 'scan not converged', no
verdict; (ii) V(τ) = V3/2 (1 − cos 3τ′) + V6/2 (1 − cos 6τ′) (τ′ = τ − τ₀) by least squares on the 12 distinct points; (iii) the internal-
rotation constant F = ħ²/(2 I_r) at the reference geometry, I_r = I_α (1 − Σ_g λ_g² I_α / I_g) (the top's moment I_α about the C0–C1 axis,
λ_g its direction cosines to the principal axes g); (iv) the 1D torsional levels in a free-rotor basis |m| ≤ 30. Verdict: |V3 − 317.20| /
317.20 ≤ 0.15 → 'B3LYP's barrier within 15 % of the microwave value'; otherwise 'B3LYP's barrier off by x %'. Reported beside: the barrier
implied by the harmonic torsion 108.0 cm⁻¹ (3 √(V3 F)), the 1D torsional fundamental, F.

## B — the variational torsion + two bends (option 4)

Grid: τ on 24 equally spaced points over 360° (15°), q₂₀ and q₂₁ each on the 11 Gauss–Hermite points of the reduced coordinate (|q| ≤ 3.67);
2,904 energies. A point is the reference displaced along A[:,20] q₂₀ + A[:,21] q₂₁, then the three methyl H turned by τ − τ₀ about the
displaced C1→C0 axis (the bends ride with the top). Energies by `probes/methyl_rotor_grid.py`, checkpointed per lane.

Hamiltonian, one approximation for all variants: H = −F ∂²/∂τ² + Σ_{i=20,21} (ω_i/2)(−∂²/∂q_i²) + V, F from A (iii), ω_i the harmonic
frequencies; the kinetic coupling between τ and the bends is left out. Product DVR: periodic Fourier DVR in τ, harmonic-oscillator DVR in q.
Three potentials: V_full (the grid); V_nt(τ, q) = V(τ, 0, 0) + V(τ₀, q₂₀, q₂₁) − V₀ (no torsion–bend coupling, the bend–bend coupling kept);
V_sep (fully separable) for the assignment. The bend fundamentals are the lowest states whose largest overlap with the separable product
states is (n₂₀, n₂₁) = (1, 0) or (0, 1) on the torsional ground level, against the lowest state. Δ_var,i = ν_i(V_full) − ν_i(V_nt).

The VPT2 counterpart on the same three modes: Psience through `probes/psience_vpt2_bridge.py` on the stored force field (fixed code, TASKS
174), Δ_VPT2,i = ν_i(modes 0, 20, 21) − ν_i(modes 20, 21); the full-dimensional Δ (6.50 and 3.29 cm⁻¹ for modes 20 and 21) beside it.

Read (`probes/methyl_rotor_read.py grid`): (i) convergence: Δ_var on the 12-point τ subset within 0.3 cm⁻¹ of the 24-point value, else 'not
converged', no verdict; (ii) |Δ_var,i − Δ_VPT2,i| ≤ 1.5 cm⁻¹ for both bends → 'VPT2's torsion–bend coupling holds variationally: a hindered
methyl keeps its coupled VPT2 value'; (iii) |Δ_var,20| ≤ 1.5 while |Δ_VPT2,20| ≥ 3 → 'VPT2's torsion–bend coupling is spurious here:
decouple a hindered methyl'; (iv) anything else is reported as it is, no verdict.

## What would not be learned

Both parts are at B3LYP/6-31G*; neither says whether B3LYP's bends are right against experiment. The kinetic τ–bend coupling and the methyl
C–H stretches (whose VPT2 values move 4–7 cm⁻¹ too) are outside B; a verdict covers the bends only.

## Runs and their checks

Scripts tested first on synthetic records (`tests/test_methyl_rotor_read.py`: a pure cosine recovers V3/V6; a free rotor gives F m²; a
separable harmonic surface gives ω exactly and Δ_var = 0; a bend made stiffer at τ₀ by a cos 3τ coupling comes out softer on V_full than
on V_nt, which cuts it at τ₀ — the torsion's zero-point motion samples the coupling away from τ₀, as removing the torsion from VPT2 freezes it
there). A smoke on the real
molecule (two scan points, three grid points) before the run spec `methyl_rotor`. Laptop, WSL under `probes/wsl_capped.sh`.


## Amendment 1 (4 Nov 2026, 10:0x — after the smoke, before any grid energy or any scan point beyond the smoke's two)

The registered VPT2 counterpart 'on the same three modes' is not defined for this rotor. Psience on the stored force field (`probes/results_m1/methyl_rotor_2026-11-04/vpt2/`): modes {0, 20, 21} give the torsion 2,730 cm⁻¹ and the bends 1,603.8 / 1,603.8 against {20, 21} 1,508.2 / 1,521.8 (Δ +95.6 / +82.0) in Cartesian normal modes, and 2,677 / 1,570.1 / 1,575.0 against 1,500.7 / 1,516.0 (Δ +69.5 / +59.0) in Z-matrix internals: the torsion's large quartic (φ_0000 ≈ 19,600 cm⁻¹) is cancelled in the full VPT2 by its cubic couplings to all the other modes, and a reduced VPT2 loses that cancellation. Read (ii)/(iii) against it would be decided by the truncation, not by the coupling. **Replacement:** Δ_VPT2,i is the full-dimensional one, ν_i(all 30 modes) − ν_i(torsion out), in both coordinate sets (TASKS 173: Cartesian 6.50 / 3.29, internals 7.46 / 4.43 cm⁻¹ for modes 20 / 21). (ii) holds when |Δ_var,i − Δ_VPT2,i| ≤ 1.5 cm⁻¹ for both bends in both coordinate sets; (iii) when |Δ_var,20| ≤ 1.5 while both Δ_VPT2,20 ≥ 3; otherwise (iv). A limitation named now: the grid's torsion turns the top rigidly with the other coordinates at the reference (only the bends move), so Δ_var holds the direct torsion–bend coupling, while the full VPT2 also holds the part carried through other modes (cubic terms φ_{0,0,k} φ_{i,i,k} / ω_k); a disagreement can come from that part, and the read says so. The three-mode runs stay in the folder as the record of why.


## Part A — outcome (10:3x)

Relaxed scan, 13 points, periodic to 0.007 cm⁻¹: V3 = 227.6, V6 = −3.3 cm⁻¹ (cosine fit, rms 1.9 cm⁻¹ — the ring is not symmetric about the barrier: V(50°) 209.9, V(70°) 213.6), F = 5.65 cm⁻¹, 1D torsional fundamental 91.3 cm⁻¹ (VPT2 94–97, harmonic 108.0, whose 3√(V3 F) implies V3 = 229.4); against the microwave V3 = 317.20(14) cm⁻¹ (Gougoula, Medcraft, Heitkämper & Walker, J. Chem. Phys. 151, 144301 (2019), checked in the paper's abstract on 4 Nov) B3LYP/6-31G* is −28.2 % — by the registered line, 'B3LYP's barrier off by −28.2 %'. The microwave value is now checked in the paper. The fit rms of 1.9 cm⁻¹ is the asymmetric part a cosine series cannot hold (the registered fit); it does not touch the verdict.

## Part B — outcome (4 November 2026, 14:0x; `probes/results_m1/methyl_rotor_2026-11-04/grid_read.json`)

24 × 11 × 11 = 2,904 B3LYP/6-31G* points (run spec `methyl_rotor`, ended 14:02, exit 0), F = 5.65 cm⁻¹: on the 24-point τ grid Δ_var = +1.37 (mode 20) and +0.10 cm⁻¹ (mode 21); on the 12-point subset +0.75 and −0.87: the subset moves Δ_var by 0.97 cm⁻¹, above the registered 0.3, so **not converged — no verdict** by line (i). The surface without torsion–bend coupling is converged already at 12 points (the same to 1e-11 cm⁻¹); what moves is the coupled surface, whose mode-21 state is mixed (character 0.93 at 24 points, 0.62 at 12). Beside it, reported as it is and not read: the full-dimensional Δ_VPT2 is 6.50 / 3.29 (Cartesian) and 7.46 / 4.43 cm⁻¹ (internals). A 24-point Δ_var smaller than Δ_VPT2 would point to line (iii), but an unconverged number decides nothing, and the gap between 1.37 and 6.5 is not to be read until a finer τ grid shows the 24-point value holds. The next check would be a 48-point τ grid (it contains the 24 points, so 2,904 new energies, ≈ 3.7 h on the laptop at the 55 s per point measured here) under the same lines, with convergence read between 24 and 48 points; it is not started: a decision of the user's (TASKS 176).

## Amendment 2 (4 November 2026, 17:1x — after part B's 24-point read, before any energy of the finer grid)

The 24-point grid was not converged (part B's outcome). On the user's word ('Ja, rooster met 48 punten') the same grid at 48 τ points: the 24 points are a subset of it (Δτ = 15° k is Δτ = 7.5° · 2k, the q nodes and the level unchanged), so their energies are reused read only (`probes/methyl_rotor_grid.py --reuse`, which refuses a point that does not sit on the same Δτ and q) and 2,904 energies are new, in `probes/results_m1/methyl_rotor_2026-11-04/grid48/` (run spec `methyl_rotor_tau48`); the 24-point files stay as they are and are copied with a sha256 manifest to `methyl_rotor_2026-11-04_backup_tau24/`. The read is unchanged but for its subset: (i) Δ_var on the 24-point subset within 0.3 cm⁻¹ of the 48-point value, else 'not converged', no verdict; (ii)–(iv) as registered, on the 48-point value. Disclosed: the 24-point values (+1.37 / +0.10 cm⁻¹) are known before this run, and they are the subset of line (i). If the 48-point grid is not converged either, there is no verdict and no further refinement without the user's word.

## Part B at 48 points — outcome (4 November 2026, 20:4x; `probes/results_m1/methyl_rotor_2026-11-04/grid_tau48_read.json`)

48 × 11 × 11 = 5,808 B3LYP/6-31G* points (2,904 reused read only from the 24-point grid, 2,904 new; run spec `methyl_rotor_tau48`, 17:13–20:39, exit 0), F = 5.65 cm⁻¹. Δ_var = +1.400 (mode 20) and +0.104 cm⁻¹ (mode 21) at 48 points; +1.367 and +0.097 on the 24-point subset: convergence 0.033 cm⁻¹, under the 0.3 of line (i). The surface without torsion–bend coupling is the same at 24 and 48 points (1507.414 / 1521.302 cm⁻¹); the coupled mode-21 state's character rises 0.93 → 0.96. Against the full-dimensional Δ_VPT2 (Cartesian 6.50 / 3.29, internals 7.46 / 4.43): line (ii) fails (|1.40 − 6.50| = 5.10 > 1.5); line (iii) holds: |Δ_var,20| = 1.40 ≤ 1.5 while Δ_VPT2,20 is 6.50 and 7.46, both ≥ 3. **Verdict by line (iii): 'VPT2's torsion–bend coupling is spurious here: decouple a hindered methyl.'** Named with it, as amendment 1 requires: (a) Δ_var,20 lies 0.10 cm⁻¹ under the 1.5 line, about three times the convergence step, so the branch is decided but not by a wide margin; (b) the grid turns the top rigidly and moves only the two bends, so Δ_var holds the direct torsion–bend coupling, while the full VPT2 also carries the part through other modes (φ_{0,0,k} φ_{i,i,k} / ω_k); the verdict says the direct coupling VPT2 assigns is not there variationally, not that every route through the torsion is; (c) one molecule, at B3LYP, whose barrier is 28 % under the microwave value (part A), so a real 4-methylimidazole is more hindered than this surface. Mode 21 points the same way (Δ_var +0.10 against 3.29 / 4.43). The rotor policy that follows from this is the user's decision (TASKS 156).

**Folder names (4 November 2026, 20:4x, after the run ended; the user: '176 akkoord').** `grid/` is now `grid_tau24/`, `grid48/` is `grid_tau48/` and `grid_read.json` is `grid_tau24_read.json`; `probes/methyl_rotor.sh` and the run spec `methyl_rotor_tau48` name the new folders. Earlier sections of this file, the run log, `grid_tau48/grid.json`'s `reused_from` and the backup's manifest (`methyl_rotor_2026-11-04_backup_tau24/MANIFEST.sha256`) keep the old names as they were written.
