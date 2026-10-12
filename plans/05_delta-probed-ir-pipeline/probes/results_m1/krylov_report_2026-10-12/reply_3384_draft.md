*Draft reply on pyscf/pyscf#2702 to jeanwsr's question 'Does #3384 solve your problem?' (12 Oct 2026). Not posted; posting waits for the
user's word. Numbers: `pr_residual_check.jsonl` (script `pr_residual_check.py`, WSL, 4 threads; #3384 = e799bb1 merged locally with master
52f5737, compiled libraries from a master build).*

---

Yes, it does for our case. I merged #3384 (e799bb1) locally onto master 52f5737 and measured the max |residual| of the Hessian CPHF, scaled by e_ai, with the script from my comment above (4 threads):

| case | master | #3384 | tol |
|---|---|---|---|
| benzene PBE/6-31G* Cartesian, grid (99, 590), the setting we run in production | 5.5e-5 (solve_mo1 298 s) | 5.4e-8 (313 s) | 1.2e-7 |
| benzene PBE/6-31G*, default grid (the reproduction above) | 6.4e-7 (57 s) | 1.9e-8 (58 s) | 1.2e-7 |
| water B3LYP/6-31G | 5.7e-6 | 1.5e-6 | 3e-8 |
| water HF/6-31G | 1.2e-8 | 3.9e-9 | 3e-8 |

Water B3LYP stops at 1.5e-6. That is inside the relaxed `fallback_tol`, as your description explains, and it is well inside what dipole derivatives need. In our tests, #3508 (one more Krylov solve on the true residual in `solve_withs1`) reached 5.8e-8, 3.2e-8, 4.0e-9 and 2.5e-9 in the same cases. However, it cost 392 s against #3384's 313 s in the first case, and it only fixes `solve_withs1`. #3384 fixes the solver itself, for every caller and at lower cost, so I'll close #3508 in favour of it. Thank you!
