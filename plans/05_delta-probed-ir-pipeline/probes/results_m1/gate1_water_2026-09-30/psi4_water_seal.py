# Sealed psi4 CCSD(T)/cc-pVDZ frozen-core energies of water for gate 1 (tests/test_acceptance_water.py), 30 Sep 2026.
import psi4
psi4.set_memory("8 GB"); psi4.set_num_threads(4); psi4.core.set_output_file("psi4_water_seal.out", False)
GEOM = """
{charge} {mult}
O 0.000000 0.000000 0.229980
H 0.000000 1.418995 -0.919730
H 0.000000 -1.418995 -0.919730
units bohr
no_com
no_reorient
symmetry c1
"""
for charge, mult, ref in ((0, 1, "rhf"), (1, 2, "uhf")):
    psi4.core.clean(); psi4.geometry(GEOM.format(charge=charge, mult=mult))
    psi4.set_options({"basis": "cc-pvdz", "puream": True, "reference": ref, "freeze_core": True, "scf_type": "pk", "cc_type": "conv",
                      "e_convergence": 1e-11, "d_convergence": 1e-10, "r_convergence": 1e-10})
    e = psi4.energy("ccsd(t)")
    print(f"SEAL {ref} charge {charge} mult {mult}: E_CCSD(T) = {e:.10f}  E_SCF = {psi4.variable('SCF TOTAL ENERGY'):.10f}  psi4 {psi4.__version__}", flush=True)
