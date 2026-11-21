# When the Judge Reads the Attack: Verdict and Compute Costs of Injected Text in LLM-Gated Code Cascades

Pre-registered study of what benign injected text does to a judge-gated code cascade (3B drafter, LLM judge, 14B escalation) with nine local judges on held-out BigCodeBench tasks.

Archived replication package: https://doi.org/10.5281/zenodo.24117786

- `design/PREREG.md`: the registered plan (commit 0b21d19). `design/DEVIATIONS.md`: every change after registration.
- `code/`: generation (`gen_drafts.py`), payloads (`payloads.py`), judging (`label.py`), scoring (`score_bcb.sh`, `export_bcb.py`), stage runner (`pipeline.py`), registered analysis (`analysis.py`), post hoc analysis (`exploratory.py`), figures (`figures.py`).
- `data/split_manifest.json`: salted task split. `data/thresholds.json`: frozen thresholds (commit c5dbcb4).
- `runs/`: drafts, stimuli, judge labels, thinking-judge outputs and scoring results.
- `results/results.json`: registered results. `results/exploratory.json`: post hoc results.
- `paper/`: manuscript source, figures and preview PDF.

All payloads are inert canaries (tag GCX7). Model-written code runs only in containers with `--network none`.

## Reproduce the analysis

From a clone of this repository (or the Zenodo archive):

    pip install numpy scipy statsmodels pandas matplotlib
    sh reproduce.sh

`reproduce.sh` reruns the registered analysis, the post hoc analysis and the figures, and compares the results with the stored files.

Rerunning generation needs Ollama with the model digests in `data/thresholds.json`, and the BigCodeBench v0.1.4 evaluation image; see `code/fetch_bcb.sh` (pinned revision and SHA-256), `code/export_bcb.py` and `code/score_bcb.sh`.

Code: MIT. Data and text: CC BY 4.0. BigCodeBench task text inside `runs/` is from BigCodeBench (Apache 2.0).
