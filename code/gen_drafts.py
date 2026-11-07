#!/usr/bin/env python3
"""Generate drafts on local Ollama. Writes one JSON row per draft, resumable. Runs no model-written code.
  gen_drafts.py TASKS OUT --split pilot --model qwen2.5-coder:3b --reps 1 [--context FILE]"""
import argparse,json,os,re,time,urllib.request
WRAP="Write a Python solution to the task below. Reply with one fenced python code block and nothing else.\n\n{p}"
ap=argparse.ArgumentParser();ap.add_argument('tasks');ap.add_argument('out');ap.add_argument('--split');ap.add_argument('--model',default='qwen2.5-coder:3b');ap.add_argument('--reps',type=int,default=1);ap.add_argument('--num_predict',type=int,default=1024);a=ap.parse_args()
T=[json.loads(l) for l in open(a.tasks)]; T=[t for t in T if t['split']==a.split]
done=set()
if os.path.exists(a.out):
    done={(r['task_id'],r['rep']) for r in map(json.loads,open(a.out))}
def extract(s):
    m=re.search(r"```(?:python|py)?\s*\n(.*?)```",s,re.S)
    return (m.group(1) if m else s).strip()+"\n"
with open(a.out,'a') as f:
    for t in T:
        for rep in range(a.reps):
            if (t['task_id'],rep) in done: continue
            b=dict(model=a.model,prompt=WRAP.format(p=t['instruct_prompt']),stream=False,options=dict(temperature=0.8,seed=1000+rep,num_predict=a.num_predict,num_ctx=8192))
            t0=time.time()
            r=json.load(urllib.request.urlopen(urllib.request.Request("http://localhost:11434/api/generate",json.dumps(b).encode(),{"Content-Type":"application/json"}),timeout=900))
            row=dict(task_id=t['task_id'],split=t['split'],rep=rep,model=a.model,code=extract(r['response']),tokens_in=r.get('prompt_eval_count'),tokens_out=r.get('eval_count'),done=r.get('done_reason'),wall=round(time.time()-t0,2))
            f.write(json.dumps(row)+"\n");f.flush()
