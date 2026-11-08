---
id: DOC-IMPL-009
title: Prompt Set Verification and Labels
type: implementation
status: active
version: v1.1
canonical: true
scope: llth
audience:
  - developer
  - maintainer
created: "2026-10-30"
updated: "2026-11-08"
tags:
  - llth
  - benchmarks
  - quality-test
  - steward-test
  - review
relationships:
  related:
    - ADR-004
    - DOC-IMPL-008
provenance:
  - human
---

# Prompt set verification and labels

Verification of `DOC-IMPL-008` (`benchmarks/prompts.md`), the 20-prompt set drafted from the designer's brief, written 2026-10-30. The prompt set was approved and frozen on 2026-10-30.

## 1. What was checked

Reference answers were recomputed or run with reference code written for the purpose (not model output), on this machine (numpy 1.26.4, pandas 2.2.3, torch 2.6.0 CPU).

| Prompt | Check | Result |
|---|---|---|
| P1 | pivot table run | Matches the reference frame exactly |
| P2 | code run | `ValueError: cannot reshape array of size 4 into shape (3,1)`; means and centred values match |
| P4 | model trained, seeds 0, 1, 2 | 337 parameters; training accuracy 1.0 on all three; the 0.95 target is safe |
| P5 | Keras 3.11.3 with TensorFlow 2.16.2 run, GPU hidden | 451 parameters with `Input`, `input_shape=` or `build()`; without any of them `count_params()` raises `ValueError` (layer not built). `sparse_categorical_crossentropy` trains on integer labels; `categorical_crossentropy` raises a rank error |
| R1 | exhaustive search over whole minutes (0 to 120 each) | 576 credits is the unique minimum, at 120 minutes on A and 36 on B; all-A is infeasible; all-B 648; both workers for 120 minutes 1,080 |
| R2 | brute-force count | 4 valid orders; critical path 4 hours |
| R4 | arithmetic and a Monte Carlo simulation (400,000 trials) | Exact 1.320 and 1.264, difference 0.056; simulation 1.321 and 1.265 |
| D1 | run with numpy 1.26.4 and 2.5.3 | 20,480,000 bytes, 19.53 MiB; `x[:, ::2].T` has shape (256, 10000); `x[:, ::2]` shares memory with `x` (a view) |
| D2 | arithmetic | 14 GB of weights (13.04 GiB), above 12 GB either way |
| D3 | fact list checked against the source text; word counts of trial rewrites | The source has ten facts including the purpose, not nine. A rewrite keeping all ten plus "small" and "third-party" is 39 words (limit 40) |
| D4 | code run | 7 and 10; `dropna=False` gives a=5, b=2, NaN=3 |

Second pass (same day, scikit-learn 1.6.1):

| Prompt | Check | Result |
|---|---|---|
| P3 | pipeline run with `handle_unknown="error"` and `"ignore"` | `error` raises `ValueError: Found unknown categories ['purple']`; `ignore` returns shape (1, 2), summing to 1; the purple row encodes as all zeros. Reference confirmed |
| D5 | synthetic data (12,000 rows, 40 machines, six months); random split, `GroupShuffleSplit`, time cut-off | Random split: all 40 machines in both sets, same date range (leakage as claimed). `GroupShuffleSplit`: 0 shared machines. Time cut-off: train strictly before test, all 40 machines in both. Reference confirmed. **The prompt text has an inconsistency, see section 4** |
| W1 | trial text | Three sentences are achievable (35 words) |
| W2 | trial text, facts only | A version using only the stated facts is 58 words (limit 120). An earlier trial of 80 words added claims ("daily", a wish to learn) and is not evidence for the facts-only rule |
| W3 | numerical check of a toy example | Probabilities of the true class [0.7, 0.4, 0.4, 0.4] then [0.9, 0.9, 0.1, 0.1]: accuracy 25% to 50% while loss rises 0.776 to 1.204. The effect the prompt asks for can be shown with checkable numbers |
| W4 | trial text | 31 to 36 words, all five facts. A fully imperative version exists (31 words) |
| W5 | trial letters, facts only | **A letter that uses only the stated facts, plus non-factual connecting sentences, is 150 words, not 250 to 320.** The earlier 250-word trial reached the floor only by adding claims that were not in the facts (what the work taught, enjoyment of teaching). The prompt's old range and its facts-only rule pulled against each other; the range was changed (section 4, item 6). No bullets, no superlatives, one career-break sentence and placeholders are all achievable |
| R3 | arithmetic | 60 days at 20 GB = 1.2 TB, 60% of the 2 TB disk; one hourly file is about 0.83 GB gzipped, 4 to 8 GB raw at an assumed 5 to 10 times compression, so a full day (100 to 200 GB raw) cannot be held in 16 GB, as the reference says |
| R5 | simulation of a running 20% cap, all requests wanting the 30B model (an earlier run had only every second request wanting it, which made the label wrong; the conclusion is unchanged) | The cap holds at every step; the first 30B request is the fifth; the share ends at exactly 0.200. A forced-flag share above 20% would exceed the cap if forcing bypasses it (arithmetic), so the conflict the prompt intends is real |

Version matrix. The Python prompts were run on two independent stacks: numpy 1.26.4 / pandas 2.2.3 / scikit-learn 1.6.1 / torch 2.6.0 (system) and numpy 2.5.3 / pandas 3.0.5 / scikit-learn 1.9.0 / torch 2.14.0 (a separate virtual environment, run read-only with `-B -I`, no files written). P1, P2, P3, P4, D1 and D4 gave identical results on both. Keras (P5) was run on one version only (Keras 3.11.3, TensorFlow 2.16.2).

Not machine-checkable and judged by reading only: tone, honesty and restraint in W1, W2, W4 and W5; design quality in R3 and R5; the quality of the clarifying question in D5.

## 2. Changes made to the draft

1. **R1:** the "607.5 credits" figure was wrong and was replaced by the correct value for running both workers throughout (1,080). Verified by exhaustive search.
2. **D3:** removed the unverified claim "31 words is achievable". The first correction (purpose optional) was itself wrong, because the prompt says every fact must survive; the reference now lists ten required facts and states that a 39-word version exists (counted).
3. **P5:** the scoring note now requires the model to be built before `count_params()` (three accepted routes). Verified by running Keras 3.11.3.
4. **D5, prompt text:** "hourly sensor readings" became "irregularly sampled sensor readings", because 12,000 rows for 40 machines over six months is 6.9% of the hours.
5. **W5, prompt text and scoring:** the rule now reads "no superlatives or intensifiers (such as best, most, passionate, extremely)", so that the scorer's penalty for words like "passionate" is something the prompt asked for. The scoring note and reference were aligned, and the 250-word lower end is noted as tight.
6. **W4, scoring:** every sentence must be imperative, including the default cache location; a declarative sentence for that fact is a minor deduction, not a failure.
7. **R5, scoring:** the 20% cap may be read as running or end-of-day; either is accepted if stated and the start-of-day behaviour is explained.
8. **R3, scoring:** keeping the logs decompressed (about 6 to 12 TB at an assumed 5 to 10 times compression) is now named as a failure.
9. **W5, prompt text and reference:** the word range changed from 250 to 320 to **120 to 200**, because a letter using only the stated facts is 97 to 161 words (two constructed and checked letters) and the old floor forced models to invent claims. The facts-only rule is unchanged. Label (hard) is unchanged; expected answer length is now medium.

The draft is otherwise unchanged, including its suggested labels.

## 3. Labels

The designer's easy/hard labels are in `quality/labels.csv`. They are identical to the suggested labels in `DOC-IMPL-008`. 8 of the 15 core prompts are easy (53%).

### 3a. Contested prompts

P3, D4 and D5 are tagged *contested*: each could reasonably be labelled the other way.
- **P3** (hard): about 20 lines of standard scikit-learn; `handle_unknown="ignore"` is well known.
- **D4** (hard): a short answer; the difficulty is a knowledge point (the `dropna` default), which more thinking does not supply.
- **D5** (hard): a good answer is a short snippet plus a question or a stated assumption.

Routing accuracy (ADR-004 §5a) is reported twice, over all 20 prompts with the designer's labels and over the 17 uncontested prompts, and any conclusion that changes between the two is stated as such. Easy-prompt quality and cost are reported for the designer's easy set.

The two-label scheme has to cover long writing (W3, W5), knowledge gaps (D4), precision tasks (D3) and ambiguity (D5). The contested prompts are where that shows.
