#!/bin/sh
# Reruns the registered analysis, the post hoc analysis and the figures, then compares results with the stored copies.
set -e
cd "$(dirname "$0")"
PY=${PYTHON:-python3}
cp results/results.json /tmp/gc_results_stored.json; cp results/exploratory.json /tmp/gc_exploratory_stored.json
$PY code/analysis.py > /tmp/gc_analysis.txt
cp runs/results.json results/results.json
$PY code/exploratory.py
$PY code/figures.py
$PY - <<'PYEOF'
import json, math
def walk(a, b, path=""):
    if isinstance(a, dict):
        for k in set(a) | set(b): walk(a.get(k), b.get(k), f"{path}/{k}")
    elif isinstance(a, list):
        for i, (x, y) in enumerate(zip(a, b)): walk(x, y, f"{path}[{i}]")
    elif isinstance(a, float) and isinstance(b, float):
        tol = 1e-4 if path.startswith("/mixed") else 1e-9  # the variational mixed-model fit is not bit-for-bit repeatable
        if not math.isclose(a, b, rel_tol=tol, abs_tol=1e-12): raise SystemExit(f"MISMATCH {path}: {a} vs {b}")
    elif a != b: raise SystemExit(f"MISMATCH {path}: {a!r} vs {b!r}")
for new, old in (("results/results.json", "/tmp/gc_results_stored.json"), ("results/exploratory.json", "/tmp/gc_exploratory_stored.json")):
    walk(json.load(open(new)), json.load(open(old))); print("match:", new)
PYEOF
