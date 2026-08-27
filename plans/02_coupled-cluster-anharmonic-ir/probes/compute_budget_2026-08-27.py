import numpy as np

# Measured today: B3LYP/6-31G* optimize + Hessian + dipole derivatives, 8 threads.
ATOMS = np.array([12, 18, 24], dtype=float)
MINUTES = np.array([8.1, 28.0, 86.0])

slope, intercept = np.polyfit(np.log(ATOMS), np.log(MINUTES), 1)
coeff = np.exp(intercept)
print(f"fit: t(min) = {coeff:.3e} * N^{slope:.2f}   (three points, N = 12, 18, 24)")
for n, t in zip(ATOMS, MINUTES):
    print(f"   check N={n:.0f}: measured {t:5.1f}   fit {coeff * n**slope:5.1f}")


def hours(n_atoms):
    return coeff * n_atoms**slope / 60.0


print("\nExtrapolated full frequency job (opt + Hessian + intensities):")
TARGETS = [
    ("pyrene", 26, "C16H10"),
    ("chrysene / triphenylene / tetracene", 30, "C18H12"),
    ("coronene", 36, "C24H12"),
    ("ovalene", 46, "C32H14"),
    ("circumcoronene", 72, "C54H18"),
]
for name, n, formula in TARGETS:
    h = hours(n)
    print(f"   {name:<36} {formula:<8} {n:>3} atoms  {h:8.1f} h  ({h/24:5.2f} days)")

# A quartic force field by numerical differentiation of analytic Hessians needs
# roughly 2*(3N-6) displaced Hessians. Hessians WITHOUT dipole derivatives are
# cheaper; measured ratio was about 2.3x for the full job.
print("\nAnharmonic quartic force field at the same DFT level,")
print("~6N displaced Hessians, Hessian-only cost (full job / 2.3):")
for name, n in (("benzene", 12), ("naphthalene", 18), ("anthracene", 24),
                ("pyrene", 26), ("coronene", 36)):
    per = hours(n) / 2.3
    total = per * 6 * n
    print(f"   {name:<14} {n:>3} atoms  {6*n:>4} Hessians x {per*60:6.1f} min"
          f" = {total:8.1f} h  ({total/24:6.2f} days)")

print("\nAgainst a compute budget of 168 h/week (24/7 on one laptop):")
for name, n in (("benzene", 12), ("naphthalene", 18), ("anthracene", 24),
                ("pyrene", 26), ("coronene", 36)):
    total = hours(n) / 2.3 * 6 * n
    print(f"   {name:<14} {total/168:6.2f} weeks of wall clock")
