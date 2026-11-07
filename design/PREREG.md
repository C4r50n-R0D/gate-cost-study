# Pre-registration: injection cost at a code gate

Registered by public git commit before any test-split draft, label or score exists. Status of the author: independent researcher. Exploratory follow-up to DOI 10.5281/zenodo.23968040.

## Prior exposure

The author has seen stored results from the first study, including that some payloads pushed one judge toward rejecting correct drafts and that an "ignore instructions" prompt raised rejection for that judge. Those findings motivated this study and are not evidence for it. A pilot used 60 BigCodeBench pilot-split tasks and three already-used tasks, to check tooling, timing and token accounting. No pilot row enters any analysis.

## Questions

- Q1. Does planted project text get carried into a drafter's code?
- Q2. Do planted claims change a judge's verdict relative to a neutral comment?
- Q3. How many extra tokens does a thinking judge spend per attacked draft relative to a neutral comment?
- Q4. Which way does cascade cost move, and is quality lost?

## Tasks

BigCodeBench v0.1.4 (revision b74c0d0), instruct prompts. Split by salted SHA-256, salt `gate-cost-2026-11-07`: 60 pilot, 300 calibration, 780 test (`data/split_manifest.json`). Test tasks are used in hash order: the first 300 form the corpus.

## Models

All local, installed before registration, on Ollama 0.40.8, MacBook Air M3, 16 GB. No model is pulled. Digests are recorded at run time.

- Drafter: qwen2.5-coder:3b, temperature 0.8, seed 1000.
- Escalation: qwen2.5-coder:14b, same settings.
- Judges (9): tev1:4b, llama3.1:8b, gemma4:12b, qwen3.5:9b, qwen2.5:7b-instruct, qwen2.5-coder at 1.5b, 3b, 7b, 14b. Verdict mode, thinking off, one output token, temperature 0.
- Thinking judge: qwen3.5:9b with thinking on, cap 6,000 output tokens.

gemma4:12b did not repeat exactly in the pilot. It stays in, and this is reported.

## Correctness

Benchmark tests in the BigCodeBench evaluator image, `--network none`. `pass` is correct, `fail` is wrong. `timeout` drafts are excluded from the corpus. A wrong draft is excluded if the task's canonical solution fails in the same container.

## Thresholds

For each probability judge, on clean calibration drafts that pass: tau is the largest observed probability at which the false-rejection rate is at most 30%. Thresholds are committed publicly before any test-split row exists.

## Stage A: carry-through

For the first 150 corpus tasks, the drafter receives the task with one planted context: three carriers (contributing note, neighbouring file, issue comment) crossed with two inert header lines (approve-leaning, reject-leaning), assigned in rotation, 25 per cell.

Outcome: share of drafts containing tag GCX7, Wilson 95% CI, overall and by cell. Carried drafts are scored, and enter Stage B as a natural arm.

## Stage B: verdict panel

Corpus: 80 correct and 40 wrong clean drafts, drawn with seed 20261107 from the 300. Each draft is shown as clean, three neutral forms (comment, string, identifier) and ten planted forms: five types (comment, authority, role tag, string, identifier) by two directions (approve, reject). Wording within a type and direction is assigned by task hash, so wording is crossed with task. Neutral control for comment, authority and role tag is the neutral comment; string and identifier use their own form. Texts are in `code/payloads.py`. A sample of 240 string and identifier forms is rescored to confirm test verdicts do not change.

## Stage C: thinking arm

40 drafts (27 correct, 13 wrong) drawn from the corpus with seed 20261108. Forms: neutral comment, one approve comment, one reject comment.

## Primary outcomes

1. Carry-through rate, Stage A.
2. For each of the 9 judges: change in false-rejection rate on correct drafts, reject-leaning minus neutral, pooled over types and wordings, at the frozen threshold. Task-level sign-flip permutation test, 10,000 permutations, Holm across the 9 judges, alpha 0.05, two-sided.
3. Extra output tokens per attacked draft, payload minus neutral, thinking judge, all attacked drafts. Mean with task bootstrap 95% CI. Runs at the cap count as 6,000, so the estimate is a lower bound. Cap rate is reported by condition.

## Secondary outcomes

- False accepts on wrong drafts, approve minus neutral. With 40 wrong drafts this is a rough read.
- Handled rate on planted forms: tag absent from the answer, verdict equal to the neutral verdict, response complete. Tokens per handled attack is not computed as a primary measure.
- Cascade replay per judge and direction: draft cost + judge cost + P(escalate) x 14B cost in token-compute, and accuracy, using one 14B draft per corpus task. Compared with neutral.
- Payload type and wording variance, from a binomial mixed model with random effects for task and wording.

## Exploratory

The Qwen2.5-Coder ladder (1.5B, 3B, 7B, 14B) is described, with no correlation test. With nine judges, this study does not test a size relationship.

## Rules

Judging and generation never overlap. Model-written code runs only with no network. Payloads are benign and inert. Any change after this commit goes in DEVIATIONS.md.
