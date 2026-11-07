# Deviations from PREREG.md

Registered at commit 0b21d19 (2026-11-07 16:52 UTC). Every change after that commit is listed here.

## Implementation additions (no change to design, rule, split or analysis)

1. `code/gen_drafts.py` gained `--ids FILE` (generate for a fixed, ordered task list) and `--stageA` (prepend one of the six registered Stage A contexts, cycled by position, and record `cell` and `carried`). These implement the registered Stage A and the registered first-300 test tasks.
2. `code/pipeline.py` was added after registration to run the registered stages in order and resume after interruption. It commits `data/thresholds.json` and pushes before any test-split draft is generated.

## Bug fixes

3. 2026-11-07, about 14:05 EST. The first calibration scoring call did not run. The remote command changed into `research/gate-cost` and then redirected its log to a path relative to the home folder, so the shell could not open the log file and the scorer never started. No results were produced or read. Fix: the log path is now absolute (`$HOME/...`). No data was discarded, and no test-split row existed at the time.

## Open items to settle before analysis

4. The registration does not say how a judge row with no YES or NO probability (`p` is None) is treated on the test split. Calibration thresholds exclude such rows. The count of such rows per judge will be reported, and the analysis will be run with these rows counted as rejections, which matches the first study, and also with them excluded.
