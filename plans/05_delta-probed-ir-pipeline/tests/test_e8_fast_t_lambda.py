"""E8 --fast-t-lambda (30 Sep 2026): the switch exists, is RHF-only, installs the (T)-lambda C kernel before the header line, the reference
gradient alone runs its two-route check against pyscf's make_intermediates under FAST_T_LIMIT before the lambda is solved, the gate-1 stamp must
cover it, and the density check runs only when the density kernel is installed. Read from the source (the laptop's Windows python has no pyscf);
the kernel's numbers are tested in test_t_density_kernel.py and in gate 1."""
import re
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1]
SRC = PLAN / "probes" / "e8_cc_hessian_fd.py"
FAST = PLAN / "probes" / "t_density_kernel" / "t_density_fast.py"


def test_switch_and_install_order():
    text = SRC.read_text(encoding="utf-8")
    assert re.search(r'add_argument\("--fast-t-lambda", action="store_true"', text)
    assert "if a.fast_t_density or a.fast_t_lambda:" in text
    assert "--fast-t-density and --fast-t-lambda are RHF only" in text
    assert text.index("fast.install_lambda()") < text.index('log(f"E8 FD Hessian:')
    assert "gate1_problem(a.fast_t_density, a.spin > 0, a.fast_t_lambda)" in text
    assert "the stamp does not cover the (T) lambda C kernel" in text


def test_two_route_check_before_the_lambda_solve():
    text = SRC.read_text(encoding="utf-8")
    check = text.index("fast.check_lambda_against_pyscf(mycc, mycc.t1, mycc.t2, eris)")
    solve = text.index("conv, l1, l2 = ccsd_t_lambda.kernel(mycc, eris, mycc.t1, mycc.t2, tol=LAMBDA_TOL)")
    assert check < solve
    assert "if fast is not None and check_fast and fast.lambda_installed():" in text
    assert "if fast is not None and check_fast and fast.density_installed():" in text
    assert "the fast (T) lambda kernel disagrees with pyscf on the reference gradient — refusing to continue" in text


def test_wrapper_api():
    py = FAST.read_text(encoding="utf-8")
    for name in ("def lambda_kernel(", "def make_intermediates(", "def install_lambda()", "def uninstall_lambda()",
                 "def check_lambda_against_pyscf(", "def lambda_installed()", "def density_installed()"):
        assert name in py, name
    c = (PLAN / "probes" / "t_density_kernel" / "ccsd_t_rdm_kernel.c").read_text(encoding="utf-8")
    assert "int t_lambda_intermediates(" in c and c.count("#pragma omp for schedule(dynamic, 1)") == 2
