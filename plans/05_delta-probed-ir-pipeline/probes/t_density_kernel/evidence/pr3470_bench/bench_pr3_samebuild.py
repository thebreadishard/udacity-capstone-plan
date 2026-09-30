"""'Before' in the same build as 'after': master's unchanged ccsd_t_lambda.py / ccsd_t_rdm.py (git show master:...) loaded from files and
patched over the branch's modules, then the same benchmark as bench_pr3.py (label before_samebuild)."""
import importlib.util
import runpy
import subprocess
import sys

import pyscf.cc.ccsd_t_lambda as LAM
import pyscf.cc.ccsd_t_rdm as RDM

REPO = "/home/thebreadishard/pyscf-master"


def load_master(path, name):
    src = subprocess.run(["git", "-C", REPO, "show", f"master:{path}"], capture_output=True, text=True, check=True).stdout
    fn = f"/tmp/{name}.py"
    open(fn, "w").write(src)
    spec = importlib.util.spec_from_file_location(name, fn)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


old_rdm = load_master("pyscf/cc/ccsd_t_rdm.py", "old_ccsd_t_rdm")
old_lam = load_master("pyscf/cc/ccsd_t_lambda.py", "old_ccsd_t_lambda")
assert "CCsd_t_lambda_intermediates" not in open("/tmp/old_ccsd_t_lambda.py").read()
LAM.make_intermediates = old_lam.make_intermediates
RDM._gamma1_intermediates = old_rdm._gamma1_intermediates
RDM._gamma2_intermediates = old_rdm._gamma2_intermediates
RDM._gamma2_outcore = old_rdm._gamma2_outcore
BENCH = __file__.replace("bench_pr3_samebuild.py", "bench_pr3.py")
sys.argv = [BENCH] + sys.argv[1:]
runpy.run_path(BENCH, run_name="__main__")
