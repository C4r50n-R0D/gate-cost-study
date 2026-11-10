cd "$(dirname "$0")/.."
while pgrep -f "gen_drafts.py data/tasks.jsonl runs/cal/drafts.jsonl" >/dev/null; do sleep 20; done
python3 code/pipeline.py all
