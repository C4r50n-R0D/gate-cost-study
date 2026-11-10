cd "$(dirname "$0")/.."
for s in panel strong think; do python3 code/pipeline.py $s || exit 1; done
