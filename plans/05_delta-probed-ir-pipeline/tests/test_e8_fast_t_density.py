"""E8 --fast-t-density (29 Sep 2026): the switch exists, is RHF-only, installs the kernel before the header line, and the reference gradient
alone runs the two-route check against pyscf under FAST_T_LIMIT — read from the source, since the laptop has no pyscf. The kernel's own
numerical tests are in test_t_density_kernel.py (WSL, built library)."""
import ast
import re
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1]
SRC = PLAN / "probes" / "e8_cc_hessian_fd.py"
KDIR = PLAN / "probes" / "t_density_kernel"


def test_switch_plumbing_and_two_route_check():
    text = SRC.read_text(encoding="utf-8")
    tree = ast.parse(text)
    grad = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "gradient")
    names = [a.arg for a in grad.args.args]
    assert names[-2:] == ["fast", "check_fast"]
    assert re.search(r'add_argument\("--fast-t-density", action="store_true"', text)
    assert 'raise SystemExit("--fast-t-density is RHF only' in text
    assert text.index("fast.install()") < text.index('log(f"E8 FD Hessian:')                 # installed before the first gradient
    assert "check_fast=True)" in text and text.count("check_fast=True") == 1                 # the reference gradient only
    assert "fast.check_against_pyscf(" in text and "FAST_T_LIMIT = 1e-10" in text
    assert "refusing to continue" in text
    assert "ccsd_t_grad.Gradients(mycc).kernel(mycc.t1, mycc.t2, l1, l2, eris)" in text       # the checked lambda is reused, not re-solved


def test_kernel_sources_and_build_script_present():
    assert (KDIR / "ccsd_t_rdm_kernel.c").exists() and (KDIR / "t_density_fast.py").exists() and (KDIR / "build.sh").exists()
    c = (KDIR / "ccsd_t_rdm_kernel.c").read_text(encoding="utf-8")
    assert "int t_density_intermediates(" in c and "#pragma omp parallel" in c and "schedule(dynamic, 1)" in c
    py = (KDIR / "t_density_fast.py").read_text(encoding="utf-8")
    assert "def install()" in py and "def uninstall()" in py and "def check_against_pyscf(" in py
    assert "RTLD_GLOBAL" in py                                                                # pyscf's BLAS/OpenMP runtime, not a second one
