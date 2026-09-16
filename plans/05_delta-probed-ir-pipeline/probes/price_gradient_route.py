#!/usr/bin/env python3
"""Price the gradient route for the couplings against the energies route (desk work, 16 Sep 2026).

Inputs, all measured or pre-registered elsewhere - nothing here is new physics:
  deck sizes            deck_counts_planar.py (point group; naphthalene checked against 141 pairs)
  96 gradients          stage C mode G at the declared rho, naphthalene_sym, 16 Sep (DFT stand-in)
  291 energies = 46 d   ledger 16 Sep 09:03 (levers G+H, xtight cc-pVDZ; 14 d at tight)
  g = 2.84 / 3.20       M2a, 14 Sep: PySCFAD AD at RHF / MP2. NOT measured for LNO-CCSD(T):
                        both canonical and LNO exceeded the VM. The laptop's ceiling is 20 GB since 16 Sep.
"""
DECKS = {  # molecule: (modes, H deck, diagonal H deck)
    "benzene":      (30, 139, 72),
    "naphthalene":  (48, 291, 114),
    "anthracene":   (66, 499, 156),
    "phenanthrene": (66, 1015, 178),
    "pyrene":       (72, 580, 170),
    "tetracene":    (84, 759, 198),
    "perylene":     (90, 858, 212),
    "pentacene":    (102, 1075, 240),
}
GRAD_NAPH, M_NAPH = 96, 48          # the one measured gradient count
H_PER_E = {"xtight": 46 * 24 / 291, "tight": 14 * 24 / 291}

print("A. Naphthalene, the only molecule with a measured gradient count")
M, deck, diag = DECKS["naphthalene"]
coup = deck - diag
print(f"   deck {deck} energies = {diag} diagonal + {coup} couplings; gradient route = {diag} energies + {GRAD_NAPH} gradients")
print(f"   break-even g = {coup}/{GRAD_NAPH} = {coup/GRAD_NAPH:.2f}\n")
print("   g     energy-equivalents   vs 291   laptop-days tight   laptop-days xtight")
for g in (1.84, 2.84, 3.20, 6.0, 20.0):
    tot = diag + GRAD_NAPH * g
    print(f"   {g:5.2f} {tot:16.0f} {tot/deck:8.2f}x {tot*H_PER_E['tight']/24:15.0f} {tot*H_PER_E['xtight']/24:20.0f}")

print("\nB. Break-even g per molecule (ASSUMPTION: gradients needed scale with the mode count,")
print("   anchored on naphthalene's 96. Only naphthalene is measured; the rest is arithmetic.)")
print("   molecule        modes  coupling energies  gradients (assumed)  break-even g")
for name, (M, deck, diag) in DECKS.items():
    ngrad = GRAD_NAPH * M / M_NAPH
    coup = deck - diag
    print(f"   {name:14s} {M:5d} {coup:18d} {ngrad:20.0f} {coup/ngrad:13.2f}")

print("\nC. Finite differences as a way to get gradients without new software")
M, deck, diag = DECKS["naphthalene"]
print(f"   one gradient by central differences in mode space = 2 x {M} = {2*M} energies, i.e. g = {2*M}")
print(f"   {GRAD_NAPH} gradients = {GRAD_NAPH*2*M:,} energies against {deck-diag} for the energies route"
      f" -> {GRAD_NAPH*2*M/(deck-diag):.0f}x worse. Ruled out by arithmetic, not by taste.")
