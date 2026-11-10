#!/usr/bin/env python3
"""Figures for the manuscript. Reads results/*.json and runs/test/think_qwen35.jsonl. Writes paper/fig/Fig*.pdf."""
import json, os, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); F = os.path.join(ROOT, "paper/fig")
R = json.load(open(os.path.join(ROOT, "results/results.json"))); X = json.load(open(os.path.join(ROOT, "results/exploratory.json")))
P = R["panel"]; RP = R["replay"]
NAME = {"tev": "tev1 4B", "llama": "llama3.1 8B", "gemma": "gemma4 12B", "qwen35": "qwen3.5 9B", "qwen25i": "qwen2.5-inst 7B",
        "coder1.5": "coder 1.5B", "coder3": "coder 3B", "coder7": "coder 7B", "coder14": "coder 14B"}
BLUE, ORANGE, GREY, INK = "#0072B2", "#D55E00", "#7f7f7f", "#222222"
plt.rcParams.update({"font.size": 8, "font.family": "serif", "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": GREY,
                     "axes.linewidth": 0.6, "xtick.color": INK, "ytick.color": INK, "legend.frameon": False, "pdf.fonttype": 42})
J = sorted(P, key=lambda j: P[j]["primary_FR_reject_minus_neutral"]["mean"])

# Fig 1: effects with CIs, both directions
fig, ax = plt.subplots(figsize=(4.6, 3.3)); yy = np.arange(len(J))
for off, key, col, lab in ((0.15, "primary_FR_reject_minus_neutral", ORANGE, "Reject-leaning: false rejection of correct drafts (n = 80)"),
                           (-0.15, "secondary_FA_approve_minus_neutral", BLUE, "Approve-leaning: false acceptance of wrong drafts (n = 40)")):
    m = [P[j][key]["mean"] for j in J]; lo = [P[j][key]["ci"][0] for j in J]; hi = [P[j][key]["ci"][1] for j in J]
    ax.errorbar(m, yy + off, xerr=[np.subtract(m, lo), np.subtract(hi, m)], fmt="o", ms=4, color=col, elinewidth=1.2, capsize=0, label=lab)
ax.axvline(0, color=GREY, lw=0.6); ax.set_yticks(yy, [NAME[j] for j in J]); ax.set_xlabel("Change vs matched neutral control (proportion)")
ax.legend(loc="lower center", bbox_to_anchor=(0.45, 1.0), fontsize=6.5, ncol=1); fig.tight_layout(); fig.savefig(os.path.join(F, "Fig1.pdf")); plt.close(fig)

# Fig 2: false rejection of correct drafts: clean, neutral, reject-leaning
fig, ax = plt.subplots(figsize=(4.6, 3.0))
for i, j in enumerate(J):
    f = P[j]["false_reject_correct"]; v = [f["clean"], f["neutral"], f["reject"]]
    ax.plot(v, [i] * 3, color=GREY, lw=0.8, zorder=1)
    for x, mk, col in zip(v, ("o", "s", "D"), (INK, GREY, ORANGE)): ax.scatter(x, i, marker=mk, s=18, color=col, zorder=2)
ax.axvline(0.294, color=GREY, lw=0.6, ls="--"); ax.text(0.30, len(J) - 0.4, "calibrated 0.294", color=GREY, fontsize=6.5)
ax.set_yticks(range(len(J)), [NAME[j] for j in J]); ax.set_xlim(0, 1); ax.set_xlabel("False rejection of correct drafts")
for mk, col, lab in (("o", INK, "clean"), ("s", GREY, "neutral text"), ("D", ORANGE, "reject-leaning payload")): ax.scatter([], [], marker=mk, color=col, s=18, label=lab)
ax.legend(loc="lower right", fontsize=6.5); fig.tight_layout(); fig.savefig(os.path.join(F, "Fig2.pdf")); plt.close(fig)

# Fig 4: cascade cost by condition
fig, ax = plt.subplots(figsize=(4.6, 3.0)); JC = sorted(RP, key=lambda j: RP[j]["neutral"]["cost"])
for i, j in enumerate(JC):
    n, a, r = (RP[j][c]["cost"] / 1000 for c in ("neutral", "approve", "reject"))
    ax.plot([min(n, a, r), max(n, a, r)], [i, i], color=GREY, lw=0.8, zorder=1)
    ax.scatter(n, i, color=INK, s=18, zorder=2); ax.scatter(a, i, color=BLUE, marker="v", s=22, zorder=2); ax.scatter(r, i, color=ORANGE, marker="^", s=22, zorder=2)
for mk, col, lab in (("o", INK, "neutral"), ("v", BLUE, "approve-leaning"), ("^", ORANGE, "reject-leaning")): ax.scatter([], [], marker=mk, color=col, s=20, label=lab)
ax.set_yticks(range(len(JC)), [NAME[j] for j in JC]); ax.set_xlabel("Cascade cost per stimulus (thousand token x B-params)")
ax.legend(loc="lower right", fontsize=6.5); fig.tight_layout(); fig.savefig(os.path.join(F, "Fig4.pdf")); plt.close(fig)

# Fig 3: thinking judge paired token differences
S = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(ROOT, "runs/test/stim_think.jsonl"))}
by = {}
for l in open(os.path.join(ROOT, "runs/test/think_qwen35.jsonl")):
    r = json.loads(l); s = S[r["id"]]; by.setdefault(s["task_id"], {})[s["form"]] = 6000 if r["done"] == "length" else r["tok_out"]
fig, ax = plt.subplots(figsize=(4.6, 2.2)); rng = np.random.default_rng(0)
for k, (f, col) in enumerate((("approve", BLUE), ("reject", ORANGE))):
    d = [x[f] - x["neutral"] for x in by.values()]; ax.scatter(d, k + rng.uniform(-0.15, 0.15, len(d)), s=10, color=col, alpha=0.8)
    ax.plot([np.mean(d)] * 2, [k - 0.3, k + 0.3], color=INK, lw=1.5)
ax.axvline(0, color=GREY, lw=0.6); ax.set_yticks([0, 1], ["approve - neutral", "reject - neutral"])
ax.set_xlabel("Output tokens, payload minus neutral, per draft")
fig.tight_layout(); fig.savefig(os.path.join(F, "Fig3.pdf")); plt.close(fig)

# Fig 5: exploratory predictors
fig, axs = plt.subplots(1, 2, figsize=(4.8, 2.3), sharey=True); y = X["outcome"]
for ax, key, lab in ((axs[0], "log_params", "log parameters (B)"), (axs[1], "benign_probe", "benign-probe score (neutral - clean)")):
    v = X[key]["values"]; xs = np.array([v[j] for j in J]); ys = np.array([y[j] for j in J])
    ax.scatter(xs, ys, s=14, color=INK); b = X[key]["slope_intercept"]; g = np.linspace(xs.min(), xs.max(), 10); ax.plot(g, b[0] * g + b[1], color=GREY, lw=0.8)
    for j in ("qwen35", "gemma", "tev", "coder1.5"): ax.annotate(NAME[j], (v[j], y[j]), fontsize=5.5, xytext=((-38, 4) if j == "qwen35" else (3, 2)), textcoords="offset points")
    ax.set_xlabel(lab); ax.set_title(f"r = {X[key]['pearson']:.2f}, LOO RMSE {X[key]['loo_rmse']:.3f}", fontsize=7)
axs[0].set_ylabel("Reject-direction effect"); fig.tight_layout(); fig.savefig(os.path.join(F, "Fig5.pdf")); plt.close(fig)
print("ok")
