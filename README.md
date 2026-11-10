# Injection cost at a code gate

Pre-registered study of what benign injected text does to a judge-gated code cascade (3B drafter, LLM judge, 14B escalation) with nine local judges on held-out BigCodeBench tasks.

- `design/PREREG.md`: the registered plan (commit 0b21d19). `design/DEVIATIONS.md`: every change after registration.
- `code/`: generation (`gen_drafts.py`), payloads (`payloads.py`), judging (`label.py`), scoring (`score_bcb.sh`, `export_bcb.py`), stage runner (`pipeline.py`), registered analysis (`analysis.py`), post hoc analysis (`exploratory.py`), figures (`figures.py`).
- `data/split_manifest.json`: salted task split. `data/thresholds.json`: frozen thresholds (commit c5dbcb4).
- `results/results.json`: registered results. `results/exploratory.json`: post hoc results.
- `paper/`: manuscript source and figures.

All payloads are inert canaries (tag GCX7). Model-written code runs only in containers with `--network none`.

## Reproduce the analysis

The replication archive on Zenodo adds `runs/` (drafts, stimuli, labels, scoring results). With it in place:

    pip install numpy scipy statsmodels pandas matplotlib
    sh reproduce.sh

`reproduce.sh` reruns the registered analysis, the post hoc analysis and the figures, and compares the results with the stored files.

Rerunning generation needs Ollama with the model digests in `data/thresholds.json`, and the BigCodeBench v0.1.4 evaluation image; see `code/fetch_bcb.sh` (pinned revision and SHA-256), `code/export_bcb.py` and `code/score_bcb.sh`.

Code: MIT. Data and text: CC BY 4.0. BigCodeBench task text inside `runs/` is from BigCodeBench (Apache 2.0).
