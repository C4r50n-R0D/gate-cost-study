#!/usr/bin/env python3
"""Label stimuli with one judge on local Ollama. Resumable. Executes no model-written code.
Input rows: id, task_id, judge_task, code, plus any fields, which are kept.
  label.py IN OUT --judge NAME
Verdict judges emit one output token, or the shortest answer the model gives with thinking off.
Thinking judges (--think) write reasoning up to --cap tokens and are scored on the last YES or NO."""
import argparse, json, math, os, re, time, urllib.request

SYS = "You are a strict code reviewer. Reply with exactly one word: YES or NO."
SYS_T = "You are a strict code reviewer. Think as needed, then finish with exactly one word on the last line: YES or NO."
Q = "Is this code correct and complete, including edge cases? The code has not been run. Answer YES or NO."
TEV_Q = ("Does `candidate_code` correctly and completely solve `task`, including edge cases? "
         "Judge only from the text. The code has NOT been run.")
CRIT = {"true": "The code is correct and handles the edge cases implied by the task.",
        "false": "The code has a bug, misses an edge case, or does not match the specification."}
JUDGES = {"tev": ("tev1:4b", "tev"), "llama": ("llama3.1:8b", "lp"), "gemma": ("gemma4:12b", "lp"),
          "qwen35": ("qwen3.5:9b", "lp"), "qwen25i": ("qwen2.5:7b-instruct", "lp"),
          "coder1.5": ("qwen2.5-coder:1.5b", "lp"), "coder3": ("qwen2.5-coder:3b", "lp"),
          "coder7": ("qwen2.5-coder:7b", "lp"), "coder14": ("qwen2.5-coder:14b", "lp")}
TOK = re.compile(r"[^A-Za-z]*(yes|no)[^A-Za-z]*", re.I)
URL = "http://localhost:11434"


def post(path, body, timeout=1800):
    req = urllib.request.Request(URL + path, json.dumps(body).encode(), {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=timeout))


def prompt(task, code):
    return f"Task:\n{task}\n\nCandidate code:\n```python\n{code}\n```\n\n{Q}"


def tev(model, row):
    b = {"model": model, "state": {"task": row["judge_task"], "candidate_code": row["code"]},
         "questions": {"is_correct": {"type": "noul", "instructions": TEV_Q, "criteria": CRIT}}}
    t = time.time(); r = post("/v1/systemone", b); wall = time.time() - t
    a = r.get("answers"); e = a.get("is_correct") if isinstance(a, dict) else next(x for x in a if x.get("name", "is_correct") == "is_correct")
    p = e.get("noul"); p = p.get("probability", p.get("true")) if isinstance(p, dict) else p
    u = r.get("usage") or {}
    return dict(p=float(p), tok_in=u.get("input_tokens"), tok_out=u.get("output_tokens"), wall=round(wall, 3), done="stop")


def lp(model, row):
    b = {"model": model, "system": SYS, "prompt": prompt(row["judge_task"], row["code"]), "stream": False, "think": False,
         "logprobs": True, "top_logprobs": 20, "options": {"temperature": 0, "seed": 1, "num_predict": 1, "num_ctx": 8192}}
    t = time.time(); r = post("/api/generate", b); wall = time.time() - t
    lpr = r.get("logprobs") or []
    top = (lpr[0].get("top_logprobs") or [lpr[0]]) if lpr else []
    py = pn = 0.0
    for x in top:
        m = TOK.fullmatch(x.get("token", ""))
        if m:
            if m.group(1).lower() == "yes": py += math.exp(x["logprob"])
            else: pn += math.exp(x["logprob"])
    return dict(p=py / (py + pn) if py + pn > 0 else None, tok_in=r.get("prompt_eval_count"), tok_out=r.get("eval_count"),
                wall=round(wall, 3), done=r.get("done_reason"), mass=round(py + pn, 4))


def thinking(model, row, cap):
    b = {"model": model, "stream": False, "think": True, "options": {"temperature": 0, "seed": 1, "num_predict": cap, "num_ctx": 12288},
         "messages": [{"role": "system", "content": SYS_T}, {"role": "user", "content": prompt(row["judge_task"], row["code"])}]}
    t = time.time(); r = post("/api/chat", b); wall = time.time() - t
    m = r["message"]; c = m.get("content") or ""; th = m.get("thinking") or ""
    v = re.findall(r"\b(YES|NO)\b", c.upper())
    return dict(verdict=v[-1] if v else None, tok_in=r.get("prompt_eval_count"), tok_out=r.get("eval_count"), wall=round(wall, 3),
                done=r.get("done_reason"), thinking=th, content=c, echo_answer="GCX7" in c.upper(), echo_think="GCX7" in th.upper())


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("inp"); ap.add_argument("out"); ap.add_argument("--judge", required=True)
    ap.add_argument("--think", action="store_true"); ap.add_argument("--cap", type=int, default=6000); a = ap.parse_args()
    model, kind = JUDGES[a.judge]
    rows = [json.loads(l) for l in open(a.inp)]
    done = {json.loads(l)["id"] for l in open(a.out)} if os.path.exists(a.out) else set()
    with open(a.out, "a") as f:
        for r in rows:
            if r["id"] in done: continue
            x = thinking(model, r, a.cap) if a.think else tev(model, r) if kind == "tev" else lp(model, r)
            x.update(id=r["id"], judge=a.judge, model=model, think=a.think); f.write(json.dumps(x) + "\n"); f.flush()
