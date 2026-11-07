#!/bin/sh
# Score drafts in the BigCodeBench image with no network. usage: score_bcb.sh DIR SAMPLES.jsonl
# The evaluator requires every problem to be present, so a problem file is cut to the tasks in SAMPLES.
D=$1; S=$2
python3 - "$D/$S" "$HOME/research/gate-cost/data/bcb.jsonl" "$D/problems.jsonl" <<'PY'
import json,sys
ids={json.loads(l)['task_id'] for l in open(sys.argv[1])}
with open(sys.argv[3],'w') as f:
    for l in open(sys.argv[2]):
        if json.loads(l)['task_id'] in ids: f.write(l)
PY
docker run --rm --network none --memory 6g --cpus 3 -v "$D":/app \
  -e BIGCODEBENCH_OVERRIDE_PATH=/app/problems.jsonl -e HF_DATASETS_OFFLINE=1 -e MPLBACKEND=Agg --workdir /app \
  --entrypoint python bigcodebench/bigcodebench-evaluate:latest -m bigcodebench.evaluate \
  --samples "/app/$S" --split instruct --subset full --execution local --no_gt --parallel 3 --save_pass_rate True --pass_k 1,5
