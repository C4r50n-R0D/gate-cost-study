#!/usr/bin/env python3
"""Convert BigCodeBench v0.1.4 parquet to jsonl and assign a salted split. Run in the scorer image, no network."""
import hashlib,json,sys
import pyarrow.parquet as pq
SALT="gate-cost-2026-11-07"; N_PILOT=60; N_CAL=300
t=pq.read_table('/work/v0.1.4.parquet').to_pylist()
rank=sorted(t,key=lambda r:hashlib.sha256((SALT+r['task_id']).encode()).hexdigest())
split={r['task_id']:('pilot' if i<N_PILOT else 'cal' if i<N_PILOT+N_CAL else 'test') for i,r in enumerate(rank)}
with open('/work/bcb.jsonl','w') as f:
    for r in t: f.write(json.dumps(r)+"\n")
pub=[dict(task_id=r['task_id'],split=split[r['task_id']],instruct_prompt=r['instruct_prompt'],entry_point=r['entry_point']) for r in t]
with open('/work/tasks.jsonl','w') as f:
    for r in pub: f.write(json.dumps(r)+"\n")
ids=sorted(split.items())
json.dump(dict(salt=SALT,n=len(ids),counts={s:sum(v==s for _,v in ids) for s in('pilot','cal','test')},sha256=hashlib.sha256(json.dumps(ids).encode()).hexdigest()),open('/work/split_manifest.json','w'),indent=1)
print(sorted(t[0].keys()),len(t))
