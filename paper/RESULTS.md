# Results

Draft results section for "Injection cost at a code gate". All analyses follow `design/PREREG.md` (commit 0b21d19, 2026-11-07 16:52 UTC). Thresholds were frozen in commit c5dbcb4 before any test-split row existed. Post-registration changes are listed in `design/DEVIATIONS.md`. Numbers come from `results/results.json`, produced by `code/analysis.py`.

## 1. Sample

Calibration used 300 tasks. The 3B drafter passed 109 (36.3%), failed 190, and timed out on 1. Thresholds were set on the 109 passing drafts. Each judge's threshold gave a false-rejection rate of 29.4%.

The test split used 300 tasks. The drafter passed 96, failed 203, and timed out on 1. The canonical solution passed in the scoring container for 197 of the 203 failures. Those 197 were eligible as wrong drafts.

The corpus drew 80 correct and 40 wrong drafts (seed 20261107). Each was shown in 14 forms, giving 1,680 stimuli. Nine judges labelled every stimulus, for 15,120 labels. No judge returned a label without a YES or NO probability, so the registered sensitivity analysis matches the main analysis.

Planted string and identifier forms were checked against the benchmark tests: 240 forms were rescored, and none changed its verdict.

## 2. Primary outcome 1: carry-through (Stage A)

No draft carried the canary. 0 of 150 drafts contained the tag (Wilson 95% CI 0.0–2.5%). Each of the six carrier-by-header cells was 0 of 25 (CI 0.0–13.3%).

The planted contexts did reach the drafter. Poisoned prompts were 28–36 tokens longer than the clean prompts for the same tasks. The contexts also left correctness unchanged: 50 of 150 drafts passed with a context, against 49 of 150 clean drafts on the same tasks.

The registered natural arm therefore has no members. Within this design, a planted payload reaches the judge only if the code is modified after it is generated.

## 3. Primary outcome 2: false rejection under reject-leaning payloads

Table 1 gives the per-task change in the false-rejection rate on correct drafts. The change is the reject-leaning payload minus the matched neutral control, averaged over the five payload types.

- Tests: two-sided task-level sign-flip permutation test (10,000 permutations), Holm-adjusted across the nine judges.
- Confidence intervals: task bootstrap (10,000 resamples).
- n = 80 tasks per judge.

**Table 1. Change in false rejection of correct drafts, reject-leaning minus neutral**

| Judge | Params (B) | Neutral FR | Change | 95% CI | Holm p |
|---|---|---|---|---|---|
| qwen2.5-coder:1.5b | 1.5 | 0.550 | +0.432 | [+0.355, +0.510] | <0.001 |
| qwen2.5-coder:3b | 3.1 | 0.542 | +0.360 | [+0.283, +0.438] | <0.001 |
| qwen2.5:7b-instruct | 7.6 | 0.487 | +0.320 | [+0.253, +0.392] | <0.001 |
| qwen2.5-coder:14b | 14.8 | 0.329 | +0.283 | [+0.223, +0.348] | <0.001 |
| qwen3.5:9b | 9.0 | 0.196 | +0.273 | [+0.210, +0.335] | <0.001 |
| llama3.1:8b | 8.0 | 0.533 | +0.268 | [+0.205, +0.333] | <0.001 |
| qwen2.5-coder:7b | 7.6 | 0.346 | +0.197 | [+0.140, +0.260] | <0.001 |
| tev1:4b | 4.2 | 0.196 | +0.102 | [+0.057, +0.152] | <0.001 |
| gemma4:12b | 12.0 | 0.246 | +0.037 | [+0.003, +0.075] | 0.057 |

The null hypothesis is rejected for eight of nine judges. Gemma4:12b is the exception: its point estimate is positive, but it does not reach significance after Holm adjustment.

### 3.1 The neutral control alone shifts the operating point

Adding neutral text, with no instruction and no claim about correctness, raised false rejection above the calibrated level for several judges:

| Judge | Clean | Neutral |
|---|---|---|
| coder1.5 | 0.175 | 0.550 |
| coder3 | 0.250 | 0.542 |
| qwen25i | 0.212 | 0.487 |
| llama | 0.325 | 0.533 |

For tev, gemma, qwen35, coder7 and coder14, the change was within about 5 points.

This was not a registered outcome. It does show that a threshold calibrated on clean drafts does not carry over to drafts that contain any added text. It also confirms that the neutral control is needed: effects measured against clean drafts would mix the payload effect with this general shift.

### 3.2 By payload type (descriptive)

The plain reviewer comment was the most effective reject-leaning type for most judges:

| Judge | Reviewer comment effect |
|---|---|
| coder3 | +0.60 |
| coder1.5 | +0.56 |
| llama | +0.50 |
| qwen35 | +0.49 |
| qwen25i | +0.41 |
| coder14 | +0.40 |

Identifier payloads were the least effective: 0.11 or less for every judge except coder1.5 (+0.36). String payloads were strong for coder14 (+0.60) and coder3 (+0.46).

## 4. Primary outcome 3: extra thinking tokens (Stage C)

The thinking judge was qwen3.5:9b with thinking enabled and a cap of 6,000 output tokens. It labelled 40 drafts (27 correct, 13 wrong) in three forms each, for 120 responses.

**Table 2. Thinking judge output tokens**

| Form | Mean output tokens | Runs at cap |
|---|---|---|
| Neutral comment | 2,066 | 5/40 (12.5%) |
| Approve comment | 2,222 | 2/40 (5.0%) |
| Reject comment | 2,119 | 3/40 (7.5%) |

Extra output tokens per attacked draft (attacked minus neutral, averaged over both directions per task) were +104, with a task-bootstrap 95% CI of [−429, +615] (n = 40). Runs at the cap were counted as 6,000, so the estimate is a lower bound. Cap rates were low and were lower under attack than under the neutral form.

By direction, approve was +156 [−447, +737] and reject was +53 [−496, +612].

No measurable token cost of injection was detected. The interval rules out an average increase larger than about 30% of the neutral baseline.

The canary appeared in the reasoning trace in 53 of 120 responses and in no final answer. The handled rate on attacked forms was 55 of 80 (68.8%, Wilson CI 57.9–77.8%). A response counted as handled if the canary was absent from the answer, the verdict equalled the neutral verdict, and the response was complete.

## 5. Secondary outcomes

### 5.1 False acceptance under approve-leaning payloads

The registration does not specify a multiplicity correction for this outcome, so the p-values below are unadjusted. There are 40 wrong drafts per judge.

| Judge | Change | 95% CI | p |
|---|---|---|---|
| coder3 | +0.515 | [+0.405, +0.620] | <0.001 |
| llama | +0.205 | [+0.135, +0.280] | <0.001 |
| qwen35 | +0.120 | [+0.050, +0.205] | 0.004 |
| qwen25i | +0.105 | [+0.030, +0.185] | 0.014 |
| coder1.5 | +0.065 | [−0.020, +0.150] | 0.20 |
| coder7 | +0.040 | [−0.010, +0.095] | 0.21 |
| coder14 | +0.030 | [−0.020, +0.085] | 0.36 |
| tev | +0.020 | [0.000, +0.055] | 0.49 |
| gemma | +0.010 | [−0.015, +0.045] | 1.0 |

The largest effect is for coder3, the same model as the drafter.

### 5.2 Cascade replay

The replay cascade is: 3B draft, then the judge, then the 14B model on rejection. Cost is tokens times billions of parameters, averaged per stimulus. One 14B draft was produced per corpus task. The 14B model passed 69 of the 80 correct-draft tasks and 11 of the 40 wrong-draft tasks.

**Table 3. Cascade cost and accuracy, neutral versus reject-leaning**

| Judge | Cost, neutral | Cost, reject | Change | Accuracy, neutral → reject |
|---|---|---|---|---|
| coder1.5 | 5,224 | 7,155 | +37% | 0.664 → 0.665 |
| coder3 | 5,821 | 7,289 | +25% | 0.681 → 0.670 |
| qwen35 | 7,106 | 8,497 | +20% | 0.717 → 0.695 |
| llama | 7,551 | 8,801 | +17% | 0.669 → 0.663 |
| qwen25i | 7,348 | 8,553 | +16% | 0.664 → 0.663 |
| coder14 | 9,618 | 11,110 | +16% | 0.700 → 0.692 |
| coder7 | 6,885 | 7,949 | +15% | 0.689 → 0.682 |
| tev | 5,566 | 6,031 | +8% | 0.708 → 0.702 |
| gemma | 9,296 | 9,569 | +3% | 0.731 → 0.717 |

Reject-leaning payloads raised cascade cost for every judge, by 3% to 37%, while accuracy changed by 2 points or less. Approve-leaning payloads lowered cost; for coder3 the cost fell from 5,821 to 3,093, a 47% drop.

Accuracy here is for the 80/40 corpus mix, not a natural base rate.

### 5.3 Wording variance

The binomial mixed models gave large random-effect standard deviations for task, between 2.6 and 7.7 on the logit scale. The wording standard deviation was between 1.1 (tev) and 10.1 (coder3).

The variational fit is unstable at these values. The fixed-effect estimates are not interpreted. The ordering of the wording SDs is consistent with the descriptive type table: coder3 is the most sensitive to wording, while tev and gemma are the least.

## 6. Exploratory: size within one family

The Qwen2.5-Coder ladder, as registered, is described here without a test:

| Size | Change in false rejection | Change in false acceptance |
|---|---|---|
| 1.5B | +0.43 | +0.07 |
| 3B | +0.36 | +0.52 |
| 7B | +0.20 | +0.04 |
| 14B | +0.28 | +0.03 |

Susceptibility is not monotone in size. Across all nine judges, the two most resistant were a 4B judge trained for evaluation (tev) and a 12B model from another family (gemma). With nine judges of mixed family, training and quantization, these data cannot support a claim about parameter count.

## 7. Summary against the questions

| Question | Answer |
|---|---|
| Q1. Carry-through | Not observed: 0 of 150, upper bound 2.5%. |
| Q2. Verdict change | Reject-leaning text raised false rejection for 8 of 9 judges, by 10 to 43 points over a neutral control. Approve-leaning text raised false acceptance for 4 of 9. |
| Q3. Token cost | No detectable increase in thinking tokens: +104, CI [−429, +615]. The cost of the attack appears in cascade compute instead, through forced escalation: +3% to +37%. |
| Q4. Size | No monotone pattern in the one within-family ladder, which is descriptive only. |

## 8. Limitations

- The thinking arm uses one model and 40 drafts.
- The mixed-model estimates are unreliable.
- gemma4:12b does not repeat exactly between runs, as noted in the pilot.
- The payloads were placed by hand. Stage A found no generation-time delivery path for this drafter.
- The wrong-draft sample has 40 drafts, so false-acceptance results are rough.
- All models are local, quantized Ollama builds on one machine.
