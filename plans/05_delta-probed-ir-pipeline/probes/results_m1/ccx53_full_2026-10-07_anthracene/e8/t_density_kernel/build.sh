#!/usr/bin/env bash
# Build the (T) density kernel as a standalone shared library next to this script, linked against the
# BLAS and OpenMP runtime that the running pyscf already uses (its bundled libopenblas/libgomp when the
# wheel ships them, the system libraries otherwise), so that one process never carries two OpenMP runtimes.
# Usage: bash build.sh [python]   (default: the python on PATH)
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
PY=${1:-python}
LIB=$("$PY" -c "import os, pyscf; print(os.path.join(os.path.dirname(pyscf.__file__), 'lib'))")
OUT="$HERE/ccsd_t_rdm_kernel.so"
GOMP=$(ls "$LIB"/libgomp*.so* 2>/dev/null | head -1 || true)
BLAS=$(ls "$LIB"/libopenblas*.so* 2>/dev/null | head -1 || true)
CFLAGS="-O3 -fPIC -fopenmp -Wall"
gcc $CFLAGS -c "$HERE/ccsd_t_rdm_kernel.c" -o "$HERE/ccsd_t_rdm_kernel.o"
if [ -n "$GOMP" ] && [ -n "$BLAS" ]; then
    echo "linking against pyscf's bundled $(basename "$BLAS") and $(basename "$GOMP")"
    gcc -shared "$HERE/ccsd_t_rdm_kernel.o" -L"$LIB" -l:"$(basename "$BLAS")" -l:"$(basename "$GOMP")" -Wl,-rpath,"$LIB" -o "$OUT"
else
    echo "no bundled BLAS/OpenMP in $LIB: linking -lopenblas -fopenmp from the system"
    gcc -shared -fopenmp "$HERE/ccsd_t_rdm_kernel.o" -lopenblas -o "$OUT"
fi
rm -f "$HERE/ccsd_t_rdm_kernel.o"
echo "built $OUT"
