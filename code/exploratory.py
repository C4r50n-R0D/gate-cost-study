#!/usr/bin/env python3
"""Post-hoc exploratory analyses (not pre-registered; see design/DEVIATIONS.md item 10).
1. Log-parameter count vs reject-direction susceptibility across the nine judges.
2. Benign-probe score (neutral minus clean false rejection) vs susceptibility.
Both with leave-one-out prediction error. Writes results/exploratory.json."""
import json, os, numpy as np
from scipy import stats
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = json.load(open(os.path.join(ROOT, "results/results.json")))["panel"]
B = {"tev": 4.2, "llama": 8.0, "gemma": 12.0, "qwen35": 9.0, "qwen25i": 7.6, "coder1.5": 1.5, "coder3": 3.1, "coder7": 7.6, "coder14": 14.8}
J = list(B); y = np.array([P[j]["primary_FR_reject_minus_neutral"]["mean"] for j in J])
def loo(x):
    e = []
    for k in range(len(x)):
        m = np.ones(len(x), bool); m[k] = False; b = np.polyfit(x[m], y[m], 1); e.append(y[k] - np.polyval(b, x[k]))
    return float(np.sqrt(np.mean(np.square(e))))
def summarize(x, seed):
    rng = np.random.default_rng(seed); bs = []
    for _ in range(10000):
        i = rng.integers(0, len(x), len(x))
        if len(set(x[i])) > 2 and len(set(y[i])) > 2: bs.append(stats.spearmanr(x[i], y[i]).statistic)
    s = stats.spearmanr(x, y); p = stats.pearsonr(x, y)
    return dict(values=dict(zip(J, x.tolist())), spearman=float(s.statistic), spearman_p=float(s.pvalue), spearman_boot_ci=np.nanpercentile(bs, [2.5, 97.5]).tolist(),
                pearson=float(p.statistic), pearson_p=float(p.pvalue), loo_rmse=loo(x), slope_intercept=np.polyfit(x, y, 1).tolist())
out = dict(note="post-hoc exploratory; n = 9 judges", outcome=dict(zip(J, y.tolist())), sd_outcome=float(y.std(ddof=1)),
           log_params=summarize(np.log(np.array([B[j] for j in J])), 1),
           benign_probe=summarize(np.array([P[j]["false_reject_correct"]["neutral"] - P[j]["false_reject_correct"]["clean"] for j in J]), 2))
json.dump(out, open(os.path.join(ROOT, "results/exploratory.json"), "w"), indent=1)
for k in ("log_params", "benign_probe"):
    v = out[k]; print(k, f"rho={v['spearman']:.2f} p={v['spearman_p']:.3f} CI={np.round(v['spearman_boot_ci'],2)} r={v['pearson']:.2f} p={v['pearson_p']:.3f} LOO={v['loo_rmse']:.3f} sd={out['sd_outcome']:.3f}")
