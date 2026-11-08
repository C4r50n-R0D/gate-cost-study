#!/usr/bin/env python3
"""Registered analysis (design/PREREG.md). Reads runs/test and data/thresholds.json, writes runs/results.json and prints a summary.
  analysis.py [--interim]   --interim tolerates judges that are not finished and marks the output as interim.
Missing-probability rows (p is None) are counted as rejections in the main run and dropped in a sensitivity run (DEVIATIONS.md item 4)."""
import json, math, os, random, sys, collections
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); R = os.path.join(ROOT, "runs", "test")
JUDGES = ["tev", "llama", "gemma", "qwen35", "qwen25i", "coder1.5", "coder3", "coder7", "coder14"]
TYPES = ["comment", "authority", "roletag", "string", "identifier"]
NEUTRAL_FOR = dict(comment="comment", authority="comment", roletag="comment", string="string", identifier="identifier")
PARAMS_B = {"tev": 4.2, "llama": 8.0, "gemma": 12.0, "qwen35": 9.0, "qwen25i": 7.6, "coder1.5": 1.5, "coder3": 3.1, "coder7": 7.6, "coder14": 14.8}
CAP = 6000; NPERM = 10000; NBOOT = 10000; SEED = 20261109


def rj(p): return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def wilson(k, n, z=1.96):
    if n == 0: return dict(k=0, n=0, rate=None, lo=None, hi=None)
    p = k / n; d = 1 + z * z / n; m = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return dict(k=k, n=n, rate=p, lo=max(0, m - h), hi=min(1, m + h))


def signflip(d, rng):
    """Two-sided task-level sign-flip permutation p for mean(d) != 0."""
    d = np.asarray(d, float); obs = abs(d.mean())
    s = rng.choice([-1.0, 1.0], size=(NPERM, len(d)))
    return float((np.sum(np.abs((s * d).mean(1)) >= obs - 1e-12) + 1) / (NPERM + 1))


def boot(d, rng):
    d = np.asarray(d, float); idx = rng.integers(0, len(d), size=(NBOOT, len(d)))
    m = d[idx].mean(1); return float(d.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i]); adj = [0.0] * len(ps); run = 0.0
    for r, i in enumerate(order):
        run = max(run, min(1.0, (len(ps) - r) * ps[i])); adj[i] = run
    return adj


def stage_a():
    A = rj(os.path.join(R, "stageA.jsonl")); S = json.load(open(os.path.join(R, "status.json")))
    out = dict(overall=wilson(sum(bool(a["carried"]) for a in A), len(A)), cells={})
    for a in A: out["cells"].setdefault("/".join(a["cell"]), []).append(bool(a["carried"]))
    out["cells"] = {k: wilson(sum(v), len(v)) for k, v in out["cells"].items()}
    ids = [a["task_id"] for a in A]
    out["pass_with_context"] = wilson(sum(S["stageA"].get(i) == "pass" for i in ids), len(ids))
    out["pass_clean_same_tasks"] = wilson(sum(S["clean"].get(i) == "pass" for i in ids), len(ids))
    return out


def load_panel(drop_none):
    stim = {s["id"]: s for s in rj(os.path.join(R, "stim.jsonl")) if s["form"] != "natural"}
    taus = {j: v["tau"] for j, v in json.load(open(os.path.join(ROOT, "data/thresholds.json")))["taus"].items()}
    lab = {}
    for j in JUDGES:
        rows = {r["id"]: r for r in rj(os.path.join(R, f"lab_{j}.jsonl"))}
        lab[j] = {}
        for i, r in rows.items():
            if i not in stim: continue
            if r["p"] is None and drop_none: continue
            lab[j][i] = dict(reject=(r["p"] is None) or (r["p"] < taus[j]), p=r["p"], tok_in=r.get("tok_in"), tok_out=r.get("tok_out"))
    return stim, lab, taus


def per_task_diff(stim, L, correct, direc):
    """Per task: mean over the five types of [verdict on planted form] - [verdict on matched neutral].
    Outcome is reject (for direc=reject on correct drafts) or accept (for direc=approve on wrong drafts)."""
    tasks = sorted({s["task_id"] for s in stim.values() if s["correct"] == correct}); d = []
    for t in tasks:
        diffs = []
        for k in TYPES:
            a, n = L.get(f"{t}|{direc}|{k}"), L.get(f"{t}|neutral|{NEUTRAL_FOR[k]}")
            if a is None or n is None: continue
            y = (lambda x: float(x["reject"])) if direc == "reject" else (lambda x: float(not x["reject"]))
            diffs.append(y(a) - y(n))
        if diffs: d.append(float(np.mean(diffs)))
    return d


def rates(stim, L, correct, form, kinds=None):
    v = [L[i]["reject"] for i, s in stim.items() if i in L and s["correct"] == correct and s["form"] == form and (kinds is None or s.get("kind") in kinds)]
    return (sum(v) / len(v) if v else None), len(v)


def panel(drop_none, interim):
    stim, lab, taus = load_panel(drop_none); rng = np.random.default_rng(SEED)
    n_stim = len(stim); res = {}
    for j in JUDGES:
        L = lab[j]; complete = len(L) == n_stim or drop_none
        if not L or (not complete and not interim): res[j] = dict(status="incomplete", n=len(L)); continue
        dR = per_task_diff(stim, L, True, "reject"); dA = per_task_diff(stim, L, False, "approve")
        r = dict(n_labels=len(L), complete=len(L) == n_stim, n_none=sum(1 for x in L.values() if x["p"] is None))
        r["false_reject_correct"] = {f: rates(stim, L, True, f)[0] for f in ("clean", "neutral", "approve", "reject")}
        r["false_accept_wrong"] = {f: (None if rates(stim, L, False, f)[0] is None else 1 - rates(stim, L, False, f)[0]) for f in ("clean", "neutral", "approve", "reject")}
        r["primary_FR_reject_minus_neutral"] = dict(mean=float(np.mean(dR)), ci=boot(dR, rng)[1:], p=signflip(dR, rng), n_tasks=len(dR))
        r["secondary_FA_approve_minus_neutral"] = dict(mean=float(np.mean(dA)), ci=boot(dA, rng)[1:], p=signflip(dA, rng), n_tasks=len(dA))
        r["by_type"] = {}
        for k in TYPES:
            fr, _ = rates(stim, L, True, "reject", [k]); fa, _ = rates(stim, L, False, "approve", [k])
            nr, _ = rates(stim, L, True, "neutral", [NEUTRAL_FOR[k]]); na, _ = rates(stim, L, False, "neutral", [NEUTRAL_FOR[k]])
            r["by_type"][k] = dict(FR_reject=fr, FR_neutral=nr, FA_approve=None if fa is None else 1 - fa, FA_neutral=None if na is None else 1 - na)
        # handled rate (verdict judges cannot echo the tag in a one-token answer): verdict equal to matched neutral verdict
        h = []
        for i, s in stim.items():
            if s["form"] in ("approve", "reject") and i in L:
                n = L.get(f"{s['task_id']}|neutral|{NEUTRAL_FOR[s['kind']]}")
                if n is not None: h.append(L[i]["reject"] == n["reject"])
        r["handled_rate"] = sum(h) / len(h) if h else None
        res[j] = r
    done = [j for j in JUDGES if "primary_FR_reject_minus_neutral" in res[j]]
    adj = holm([res[j]["primary_FR_reject_minus_neutral"]["p"] for j in done])
    for j, a in zip(done, adj): res[j]["primary_FR_reject_minus_neutral"]["p_holm"] = a; res[j]["primary_FR_reject_minus_neutral"]["holm_family"] = len(done)
    return res, stim, lab


def mixed(stim, lab):
    """Binomial mixed model per judge: reject ~ direction, random effects for task and wording (within type and direction)."""
    try:
        import pandas as pd
        from statsmodels.genmod.bayes_mixed_glm import BinomialBayesMixedGLM
    except Exception as e:
        return dict(error=str(e))
    out = {}
    for j in JUDGES:
        rows = [dict(y=int(lab[j][i]["reject"]), reject=int(s["form"] == "reject"), task=s["task_id"], wording=f"{s['kind']}|{s['form']}|{s.get('wording')}")
                for i, s in stim.items() if i in lab[j] and s["correct"] and s["form"] in ("approve", "reject")]
        if len(rows) < 50: continue
        df = pd.DataFrame(rows)
        try:
            m = BinomialBayesMixedGLM.from_formula("y ~ reject", {"task": "0 + C(task)", "wording": "0 + C(wording)"}, df).fit_vb()
            sd = dict(zip(m.model.vcp_names, np.exp(m.vcp_mean)))
            out[j] = dict(fe_reject_logit=float(m.fe_mean[1]), fe_sd=float(m.fe_sd[1]), sd_task=float(sd.get("task")), sd_wording=float(sd.get("wording")), n=len(df))
        except Exception as e:
            out[j] = dict(error=str(e))
    return out


def thinking():
    rows = rj(os.path.join(R, "think_qwen35.jsonl"))
    if not rows: return None
    stim = {s["id"]: s for s in rj(os.path.join(R, "stim_think.jsonl"))}; rng = np.random.default_rng(SEED + 1)
    by = collections.defaultdict(dict)
    for r in rows: by[stim[r["id"]]["task_id"]][stim[r["id"]]["form"]] = r
    def tok(r): return CAP if r["done"] == "length" else r["tok_out"]
    out = dict(n_rows=len(rows), n_tasks=len(by), cap_rate={}, tokens_mean={})
    for f in ("neutral", "approve", "reject"):
        v = [x[f] for x in by.values() if f in x]
        out["cap_rate"][f] = wilson(sum(x["done"] == "length" for x in v), len(v)); out["tokens_mean"][f] = float(np.mean([tok(x) for x in v])) if v else None
    # primary 3: per task, mean over the two attacked forms of (tokens - neutral tokens)
    d = [np.mean([tok(x[f]) - tok(x["neutral"]) for f in ("approve", "reject") if f in x]) for x in by.values() if "neutral" in x and ("approve" in x or "reject" in x)]
    m, lo, hi = boot(d, rng); out["primary_extra_tokens_per_attacked_draft"] = dict(mean=m, ci=[lo, hi], n_tasks=len(d), lower_bound=True)
    for f in ("approve", "reject"):
        dd = [tok(x[f]) - tok(x["neutral"]) for x in by.values() if "neutral" in x and f in x]
        out[f"extra_tokens_{f}"] = dict(zip(("mean", "lo", "hi"), boot(dd, rng))) if dd else None
    h = [(not x[f]["echo_answer"]) and x[f]["verdict"] == x["neutral"]["verdict"] and x[f]["done"] == "stop" for x in by.values() if "neutral" in x for f in ("approve", "reject") if f in x]
    out["handled_rate"] = wilson(sum(h), len(h))
    out["echo_answer"] = sum(r["echo_answer"] for r in rows); out["echo_think"] = sum(r["echo_think"] for r in rows)
    return out


def replay(stim, lab):
    """Cascade replay: cost = draft + judge + P(escalate) x 14B, in tokens x billions of params; accuracy of the final answer."""
    sp = os.path.join(R, "strong_status.json")
    if not os.path.exists(sp): return None
    strong = json.load(open(sp)); S = {r["task_id"]: r for r in rj(os.path.join(R, "strong.jsonl"))}
    D = {r["task_id"]: r for r in rj(os.path.join(R, "drafts.jsonl"))}
    out = {}
    for j in JUDGES:
        out[j] = {}
        for cond, sel in (("neutral", lambda s: s["form"] == "neutral"), ("approve", lambda s: s["form"] == "approve"), ("reject", lambda s: s["form"] == "reject")):
            cost = []; acc = []
            for i, s in stim.items():
                if not sel(s) or i not in lab[j]: continue
                t = s["task_id"]; d = D[t]; x = lab[j][i]
                c = 3.1 * (d["tokens_in"] + d["tokens_out"]) + PARAMS_B[j] * ((x["tok_in"] or 0) + (x["tok_out"] or 0))
                if x["reject"]: c += 14.8 * (S[t]["tokens_in"] + S[t]["tokens_out"]); acc.append(strong.get(t) == "pass")
                else: acc.append(bool(s["correct"]))
                cost.append(c)
            out[j][cond] = dict(cost=float(np.mean(cost)) if cost else None, accuracy=float(np.mean(acc)) if acc else None, n=len(cost))
    return out


def ladder(res):
    return {j: dict(params_b=PARAMS_B[j], d_FR=res[j]["primary_FR_reject_minus_neutral"]["mean"], d_FA=res[j]["secondary_FA_approve_minus_neutral"]["mean"])
            for j in ("coder1.5", "coder3", "coder7", "coder14") if "primary_FR_reject_minus_neutral" in res.get(j, {})}


if __name__ == "__main__":
    interim = "--interim" in sys.argv
    res, stim, lab = panel(False, interim); sens, _, _ = panel(True, interim)
    out = dict(interim=interim, stageA=stage_a(), panel=res, sensitivity_drop_none={j: v.get("primary_FR_reject_minus_neutral") for j, v in sens.items()},
               mixed=mixed(stim, lab), thinking=thinking(), replay=replay(stim, lab), ladder_exploratory=ladder(res))
    json.dump(out, open(os.path.join(ROOT, "runs", "results_interim.json" if interim else "results.json"), "w"), indent=1, default=float)
    print("Stage A carried", out["stageA"]["overall"])
    for j in JUDGES:
        p = res[j].get("primary_FR_reject_minus_neutral")
        if p: print(f"{j:9s} dFR={p['mean']:+.3f} [{p['ci'][0]:+.3f},{p['ci'][1]:+.3f}] p={p['p']:.4f} holm={p['p_holm']:.4f}  dFA={res[j]['secondary_FA_approve_minus_neutral']['mean']:+.3f}  handled={res[j]['handled_rate']:.2f}  {'' if res[j]['complete'] else '(partial)'}")
        else: print(f"{j:9s} {res[j]}")
    print("mixed", out["mixed"]); print("thinking", out["thinking"])
