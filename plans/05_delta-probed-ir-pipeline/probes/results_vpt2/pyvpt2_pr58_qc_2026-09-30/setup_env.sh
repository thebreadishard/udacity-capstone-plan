#!/bin/bash
set -euo pipefail
cd /tmp
curl -fsSL -o Miniforge3.sh https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
bash Miniforge3.sh -b -p $HOME/miniforge3
$HOME/miniforge3/bin/mamba create -y -q -n vpt2 -c conda-forge python=3.13 psi4=1.10.2 qcelemental=0.30.1 qcengine=0.34.2 optking=0.5.0 pytest
cd $HOME && rm -rf pyvpt2-fork && git clone -q -b quartic-route-consistency https://github.com/thebreadishard/pyvpt2.git pyvpt2-fork
$HOME/miniforge3/envs/vpt2/bin/python -m pip install -q --no-deps -e $HOME/pyvpt2-fork
$HOME/miniforge3/envs/vpt2/bin/python -c "import psi4, qcelemental, qcengine, pyvpt2; print(\"ENV OK psi4\", psi4.__version__, \"qcel\", qcelemental.__version__, \"qcng\", qcengine.__version__, \"pyvpt2\", pyvpt2.__file__)"
