---
id: DOC-IMPL-008
title: Quality and Steward Test Prompt Set
type: implementation
status: active
version: v1.0
canonical: true
scope: llth
audience:
  - developer
  - maintainer
created: "2026-10-30"
updated: "2026-10-30"
tags:
  - llth
  - benchmarks
  - quality-test
  - steward-test
  - prompts
relationships:
  related:
    - ADR-004
    - DOC-IMPL-007
    - DOC-IMPL-009
provenance:
  - human
---

# Quality and steward test prompt set (v1.0)

Prompts for the blind quality test (ADR-004 section 5) and the steward test (section 5a). Each prompt is sent verbatim, in the blockquote, to every model. The suggested labels are proposals only: the designer sets the final easy/hard labels, in `DOC-IMPL-009` section 3, before any run. Reference answers and scoring notes are for the scorer and are never sent to a model.

Status: approved by the designer on 2026-10-30. Drafted from a brief by the designer; reference answers checked independently (see `DOC-IMPL-009`). The designer's easy/hard labels are in `DOC-IMPL-009` section 3; the suggested labels below are proposals that were not adopted as such. The text of this file is frozen: any change needs a version bump and an amendment row, and the runner records the file's SHA-256 with every run (`ADR-004` section 5b).

## Amendment record

| Version | Date | Summary |
|---|---|---|
| v0.1 | 2026-10-30 | Draft (20 prompts). |
| v1.0 | 2026-10-30 | Approved by the designer. Changes from the draft, all listed in `DOC-IMPL-009` section 2: R1 and D3 and P5 reference notes corrected after verification; D5 prompt text ("irregularly sampled"); W5 prompt text ("120 to 200 words" and "superlatives or intensifiers"); W4, R3 and R5 scoring notes. |

---

### W1 · README opening, three sentences
**Prompt (verbatim, in a blockquote):**
> Write the first three sentences of a README for gridhop, a command-line tool that converts CSV timetables into ICS calendar files. Sentence one says what it does, sentence two says who it is for (people who receive timetables as spreadsheets and want them in a calendar app), sentence three says how to install it (`pip install gridhop`). Plain wording, no marketing language.

**Suggested label:** easy
**Why that label:** Three constrained sentences with all facts supplied; no reasoning required.
**How it will be scored:** A 5 is exactly three sentences, each carrying the assigned content, with the install command intact. The most likely failure is padding with a fourth sentence or adding features not mentioned (web interface, Google Calendar sync).
**Reference answer or check:** Must respect: CSV in, ICS out; audience is spreadsheet-timetable recipients; install via `pip install gridhop`. Nothing else may be asserted about the tool.

---

### W2 · Cover letter opening paragraph with fixed facts
**Prompt (verbatim, in a blockquote):**
> Write the opening paragraph of a cover letter, at most 120 words, using only these facts and nothing else. The applicant has four years of experience using pandas and scikit-learn. They built a customer churn model that reduced false-positive alerts by 18 per cent over six months. They led a team of three. The role is Data Analyst at a mid-sized logistics company. The job advert asks for SQL and dashboard experience; the applicant has used SQL occasionally and has never built a dashboard. Do not invent any employer name, project name, dates or additional skills, and do not overstate the SQL experience.

**Suggested label:** easy
**Why that label:** Short output with every fact supplied; the only difficulty is restraint.
**How it will be scored:** A 5 uses the given facts accurately, stays under 120 words, and handles the SQL point honestly (occasional use, no dashboards). The most likely failure is inventing a company name, a technology or a metric, or describing the applicant as "proficient in SQL".
**Reference answer or check:** Must respect: 4 years pandas/scikit-learn; churn model, 18 per cent fewer false positives, six months; team of three; SQL only occasional, no dashboard experience. Any added fact counts against the answer.

---

### W3 · Substack article, validation loss versus accuracy
**Prompt (verbatim, in a blockquote):**
> Write a Substack article of 550 to 650 words for readers who have trained a model or two but have no maths background. Title it yourself. The topic: why validation accuracy can keep improving while validation loss gets worse during training, what that pattern tells you about the model, and what to do about it. Include one small worked example with made-up numbers (a handful of examples with their predicted probabilities before and after a few more epochs) that shows the effect. Finish with one practical takeaway. No code, no bullet points, no headings inside the body.

**Suggested label:** hard
**Why that label:** Long output that must carry a correct technical explanation and a self-consistent numerical illustration.
**How it will be scored:** A 5 explains that cross-entropy loss penalises confident wrong predictions, so a model can keep getting the same or more examples right while becoming more wrongly confident on the ones it misses, with a toy example whose numbers actually show loss rising and accuracy flat or rising. The most likely failure is a plausible-sounding but wrong mechanism (for example attributing it to learning-rate decay), or an example whose numbers do not demonstrate the claim.
**Reference answer or check:** Must respect: word count 550 to 650; correct mechanism (confidence on misclassified examples drives loss up while argmax decisions are unchanged); the worked example must be checkable by hand, that is, the loss computed from its stated probabilities must indeed rise; one practical takeaway (early stopping on loss, calibration, or label smoothing are all acceptable).

---

### W4 · README installation section, terse rewrite
**Prompt (verbatim, in a blockquote):**
> Rewrite the following README section so that it is at most 60 words, in the imperative mood, with no change to the facts and nothing added.
>
> "So, getting quillcache up and running is really straightforward, honestly. All you need to do is run `pip install quillcache` and you're basically good to go, as long as you have Python 3.9 or something newer installed on your machine. If you also want the plotting helpers, which depend on matplotlib, you can install them with the extra `pip install quillcache[viz]`. One more thing worth knowing: by default the cache lives in `~/.quillcache`, but you can point it somewhere else by setting the `QUILLCACHE_HOME` environment variable before you import the library."

**Suggested label:** easy
**Why that label:** A short rewrite with all facts present in the input.
**How it will be scored:** A 5 keeps the five facts, stays under 60 words and every sentence is imperative, including the one about the default cache location (for example "Expect the cache in `~/.quillcache`; to move it, set `QUILLCACHE_HOME` before importing the library"). A declarative sentence for that fact is a minor deduction, not a failure. A fully imperative 31-word version exists. The most likely failure is dropping the environment-variable detail or the note that it must be set before import.
**Reference answer or check:** Must respect: `pip install quillcache`; Python 3.9 or newer; `quillcache[viz]` extra pulls in matplotlib; default cache directory `~/.quillcache`; `QUILLCACHE_HOME` overrides it and must be set before import. Word count at most 60.

---

### W5 · Full cover letter from a fact list
**Prompt (verbatim, in a blockquote):**
> Write a complete cover letter of 120 to 200 words from these facts, and these facts only. The applicant worked two years as a data scientist at a retailer, where their demand-forecasting model improved stock accuracy by 11 per cent. They took an eight-month career break in 2024 for caring responsibilities. They designed and taught a six-week internal Python course to twelve colleagues. They are applying for a Junior Machine Learning Engineer role at a renewable-energy company. The advert asks for PyTorch and German at B2 level. The applicant has used PyTorch only in personal projects and speaks German at C1. Rules: mention the career break honestly in a single sentence, do not claim professional PyTorch experience, no superlatives or intensifiers (such as best, most, passionate, extremely), no bullet points, no invented names for the employer, the applicant, the retailer or the projects. Use placeholders in square brackets for names.

**Suggested label:** hard
**Why that label:** Full-length piece under several interacting constraints that are easy to violate while sounding fluent.
**How it will be scored:** A 5 reads as a complete letter, respects every rule and frames the PyTorch gap and the career break without spin. The most likely failure is a superlative or intensifier ("passionate", "exceptional", "extremely"), an invented company or project name, or quietly upgrading personal PyTorch work to professional experience.
**Reference answer or check:** Must respect: 2 years at a retailer, 11 per cent stock-accuracy improvement; 8-month break in 2024, one sentence; 6-week Python course, 12 colleagues; PyTorch personal only; German C1 against a B2 requirement; word count 120 to 200 (facts-only letters of 97 and 161 words were constructed and checked, so the range is achievable without inventing anything); no superlatives or intensifiers, no bullets, placeholders for all names.

---

### P1 · pandas pivot with zero fill
**Prompt (verbatim, in a blockquote):**
> pandas 2.x. I have this frame:
>
> ```python
> import pandas as pd
> df = pd.DataFrame({
>     "city": ["A", "B", "A", "C", "B", "A"],
>     "month": [1, 1, 2, 2, 3, 3],
>     "sales": [10, 20, 30, 40, 50, 60],
> })
> ```
>
> Give me code that produces a frame with one row per month, one column per city, total sales in each cell and 0 where a city had no sales that month, then adds a column `total` holding the row sum. Show the resulting frame as it would print.

**Suggested label:** easy
**Why that label:** One standard call plus a row sum; the expected output is tiny and fully determined.
**How it will be scored:** A 5 gives working code (`pivot_table` or `groupby` plus `unstack` with `fill_value=0`) and the correct printed frame. The most likely failure is leaving NaN instead of 0, or computing `total` before filling so that it becomes NaN for months with a missing city.
**Reference answer or check:** Expected frame, index `month`, columns `A, B, C, total`: month 1 → 10, 20, 0, 30; month 2 → 30, 0, 40, 70; month 3 → 60, 50, 0, 110.

---

### P2 · numpy broadcasting bug
**Prompt (verbatim, in a blockquote):**
> numpy 2.x. This code raises an error on the last line:
>
> ```python
> import numpy as np
> x = np.arange(12).reshape(3, 4)
> means = x.mean(axis=0)
> centred = x - means.reshape(3, 1)
> ```
>
> Tell me the exact exception type and message, why it happens, the minimal fix, and the values in `centred` after the fix.

**Suggested label:** easy
**Why that label:** Short diagnosis with a fully determined numerical result.
**How it will be scored:** A 5 names `ValueError: cannot reshape array of size 4 into shape (3,1)`, explains that `means` has shape (4,) because the mean was taken over axis 0, gives the fix (`x - means`, relying on broadcasting, or `means.reshape(1, 4)`), and lists the correct centred values. The most likely failure is diagnosing it as a broadcasting error between (3,4) and (3,1), which is not where the exception occurs.
**Reference answer or check:** Exception raised by `reshape`, not by the subtraction. `means` = [4, 5, 6, 7]. After the fix, `centred` = [[-4, -4, -4, -4], [0, 0, 0, 0], [4, 4, 4, 4]].

---

### P3 · scikit-learn pipeline with mixed types and an unseen category
**Prompt (verbatim, in a blockquote):**
> scikit-learn 1.5 or later, pandas 2.x. Data:
>
> ```python
> import pandas as pd
> X = pd.DataFrame({
>     "colour":   ["red", "blue", "red", "green", "blue", "green", "red", "blue"],
>     "size_cm":  [10.0, 12.5, 9.0, 15.0, 11.0, 14.0, 10.5, 13.0],
>     "weight_g": [120, 150, 110, 200, 140, 190, 125, 160],
> })
> y = [0, 1, 0, 1, 1, 1, 0, 1]
> ```
>
> Build a single `Pipeline` that one-hot encodes `colour`, standardises the two numeric columns, and fits a `LogisticRegression`. Fit it on `X, y`. Then call `predict_proba` on this one-row frame, which contains a colour never seen in training, and it must not raise: `{"colour": "purple", "size_cm": 12.0, "weight_g": 150}`. Give the complete runnable code and explain in two sentences why the unseen colour does not cause an error. Do not use any library beyond pandas and scikit-learn.

**Suggested label:** hard
**Why that label:** Several components must be composed correctly and one non-default parameter is essential for the unseen-category requirement.
**How it will be scored:** A 5 runs end to end, uses `ColumnTransformer` with `OneHotEncoder(handle_unknown="ignore")` and `StandardScaler`, returns a (1, 2) probability array, and explains that the unknown category becomes an all-zero row in the one-hot block. The most likely failure is omitting `handle_unknown="ignore"` (raises on "purple"), or scaling the one-hot columns as well.
**Reference answer or check:** Property check rather than exact numbers: code runs without error on the purple row; `predict_proba` output has shape (1, 2) and sums to 1; the explanation mentions the all-zero encoding for unknown categories. Exact probabilities are not scored.

---

### P4 · PyTorch MLP on a sign-product task
**Prompt (verbatim, in a blockquote):**
> PyTorch 2.x, CPU only. Generate the data exactly like this:
>
> ```python
> import torch
> torch.manual_seed(0)
> X = torch.rand(400, 2) * 2 - 1
> y = ((X[:, 0] * X[:, 1]) > 0).float().unsqueeze(1)
> ```
>
> Write an `nn.Module` with layers 2 → 16 → 16 → 1, ReLU between layers, no activation on the output. Train it full-batch with `BCEWithLogitsLoss` and `Adam(lr=0.01)` for 500 epochs. Print the total number of trainable parameters and the final training accuracy (threshold at logit 0). Give complete runnable code. Target: accuracy of at least 0.95.

**Suggested label:** hard
**Why that label:** Model definition, loss choice, training loop and evaluation all have to be right together; shape and activation mistakes are common.
**How it will be scored:** A 5 runs, prints 337 parameters and an accuracy at or above 0.95, and thresholds the raw logits (or applies sigmoid and thresholds at 0.5, which is equivalent). The most likely failure is applying `sigmoid` inside the model while still using `BCEWithLogitsLoss`, or a (400,) versus (400, 1) shape mismatch that silently broadcasts.
**Reference answer or check:** Parameter count = (2·16 + 16) + (16·16 + 16) + (16·1 + 1) = 48 + 272 + 17 = 337. Accuracy must be at least 0.95 when the developer runs the code; the developer confirms the threshold once before using the prompt.

---

### P5 · Keras classifier, compile and parameter count
**Prompt (verbatim, in a blockquote):**
> Keras 3 with the TensorFlow 2.x backend. I want a `Sequential` model for 10 input features: `Dense(32, activation="relu")`, then `Dropout(0.2)`, then `Dense(3, activation="softmax")`. My labels are integers 0, 1, 2, not one-hot. Give the model definition and the `compile` call with the correct loss, and tell me what `model.count_params()` will return.

**Suggested label:** easy
**Why that label:** Direct construction with one loss-selection decision and a small arithmetic check.
**How it will be scored:** A 5 gives correct code with `sparse_categorical_crossentropy` and states 451 parameters. A 5 also builds the model before calling `count_params()`, with `keras.Input(shape=(10,))`, `input_shape=(10,)` on the first layer (Keras 3 prints a deprecation warning) or `model.build((None, 10))`; without one of these, Keras 3 raises `ValueError: ... the layer isn't built` (tested on Keras 3.11.3 with TensorFlow 2.16.2). The most likely failure is choosing `categorical_crossentropy` (requires one-hot labels) or miscounting by forgetting the bias terms.
**Reference answer or check:** count_params = (10·32 + 32) + (32·3 + 3) = 352 + 99 = 451. Loss must be `sparse_categorical_crossentropy` (or the class `SparseCategoricalCrossentropy`). Dropout adds no parameters.

---

### R1 · Minimum-cost worker schedule
**Prompt (verbatim, in a blockquote):**
> A nightly job must process 4,320 records within 120 minutes. Two workers are available. Worker A processes 24 records per minute and costs 3 credits per minute while running. Worker B processes 40 records per minute and costs 6 credits per minute while running. Both can run at the same time, each can be started and stopped at any whole minute, and records can be split between them in any way. Find the schedule that minimises total credits, and state the minimum cost. Show the reasoning.

**Suggested label:** hard
**Why that label:** Requires comparing cost per record, recognising the time cap as the binding constraint, and computing the split.
**How it will be scored:** A 5 observes that A is cheaper per record (0.125 versus 0.15 credits), runs A for the full 120 minutes, assigns the remainder to B, and reports 576 credits. The most likely failure is picking all-B because it is faster (648 credits); running both workers for the whole 120 minutes costs 1,080 credits and also misses the minimum.
**Reference answer or check:** A for 120 min → 2,880 records, 360 credits. B for 36 min → 1,440 records, 216 credits. Total 576 credits. Any answer other than 576 is wrong.

---

### R2 · Dependency ordering and makespan
**Prompt (verbatim, in a blockquote):**
> Six tasks, each takes exactly one hour. Dependencies: extract and validate must both finish before transform; transform must finish before load and before features; load and features must both finish before publish. Two questions. First, if one worker runs the tasks one at a time, how many different valid orders are there? Second, with unlimited workers, what is the shortest wall-clock time to finish all six? Give both numbers and a brief justification.

**Suggested label:** easy
**Why that label:** Small graph; both answers follow from inspection.
**How it will be scored:** A 5 gives 4 orders and 4 hours with the right reasoning (two free pairs, each orderable two ways; longest chain has four tasks). The most likely failure is counting 6! or 2·2·2 = 8 orders, or reporting 6 hours.
**Reference answer or check:** Valid sequential orders = 2 (extract/validate) × 2 (load/features) = 4. Critical path extract or validate → transform → load or features → publish = 4 hours.

---

### R3 · Batch pipeline on a fixed server
**Prompt (verbatim, in a blockquote):**
> Design a daily batch pipeline under these conditions. Input: about 20 GB per day of gzipped JSONL event logs, arriving as hourly files in a local directory. Hardware: one server with 4 CPU cores, 16 GB RAM, 2 TB disk, no GPU, no cloud services. Requirements: daily aggregates per user and per event type must be ready by 06:00; raw logs are kept for 60 days then deleted; a scikit-learn classifier is retrained weekly on the last 30 days of aggregates; the pipeline must be restartable after a crash without reprocessing hours that already finished. Describe the stages, the storage format and directory layout, how you keep memory under 16 GB, the scheduling (plain cron is fine), how you detect failures, and rough estimates for processing time and disk use. Prose or a numbered list, your choice. No code.

**Suggested label:** hard
**Why that label:** Open design with several constraints that interact (disk, memory, restartability, deadline).
**How it will be scored:** A 5 proposes streaming or chunked parsing of the hourly files, columnar output (Parquet or similar) partitioned by day and hour, per-hour completion markers for idempotent restarts, and gives a disk estimate that notes raw retention alone uses roughly 1.2 TB of the 2 TB. The most likely failures are a design that loads a full day into a single DataFrame, ignoring the disk arithmetic entirely, or keeping the logs decompressed (several times the 1.2 TB, about 6 to 12 TB at an assumed 5 to 10 times compression, which does not fit).
**Reference answer or check:** Constraints to check: no GPU or cloud; memory strategy that works for 20 GB/day on 16 GB RAM; raw retention 60 days ≈ 1.2 TB with headroom accounted for; hour-level idempotency marker or equivalent; retrain reads 30 days of aggregates, not raw logs; a concrete failure signal (exit code, missing marker, row-count check).

---

### R4 · Expected cost of a retry policy
**Prompt (verbatim, in a blockquote):**
> An API call fails independently with probability 0.2 on each attempt. Every attempt costs 1 unit. The policy allows up to 3 attempts; if all 3 fail, a penalty of 10 units is paid and the call is abandoned. What is the expected total cost per call? Then: would raising the limit to 4 attempts lower the expected cost, and by how much? Show the arithmetic.

**Suggested label:** easy
**Why that label:** Two short expectation calculations with no modelling choices.
**How it will be scored:** A 5 reports 1.32 units for 3 attempts, 1.264 units for 4 attempts, and concludes that 4 attempts is cheaper by 0.056 units. The most likely failure is computing expected attempts as 3 × 0.2 or forgetting that an attempt is only made if the previous one failed.
**Reference answer or check:** Three attempts: expected attempts 1 + 0.2 + 0.04 = 1.24; penalty 0.008 × 10 = 0.08; total 1.32. Four attempts: 1 + 0.2 + 0.04 + 0.008 = 1.248; penalty 0.0016 × 10 = 0.016; total 1.264. Difference 0.056 in favour of four attempts.

---

### R5 · Deterministic routing layer for two local models
**Prompt (verbatim, in a blockquote):**
> Plan a routing layer that sits in front of two local models, a 1B fast model and a 30B slow model, and decides per request which one answers. No learned classifier: every rule must be readable and give the same result for the same input. Constraints: the decision must take under 5 ms; every decision is logged with the rule that fired; the 30B model may serve at most 20 per cent of requests over any calendar day; a request can carry a flag that forces the 30B model; if the 30B model is unavailable the request must still be answered. Give the rules in priority order, the quota mechanism and what happens when it is exhausted, the fallback path, the fields of the log record, and three example requests with the route each would take.

**Suggested label:** hard
**Why that label:** Open design where the constraints conflict (forced escalation versus daily quota versus availability) and the conflicts must be resolved explicitly.
**How it will be scored:** A 5 orders the rules so that availability and the forced flag are handled before cheap heuristics, states what the forced flag does when the quota is exhausted, uses only computations that fit in 5 ms (length, keywords, flags, counters), and gives three test cases whose expected routes follow from the stated rules. "At most 20 per cent over any calendar day" may be read as a running cap or an end-of-day total; either is accepted if the answer says which it uses and explains the start-of-day behaviour (a running cap allows no 30B request before the fifth). The most likely failure is a rule that needs a model call to decide (violating the latency bound), or leaving the quota-versus-forced-flag conflict unresolved.
**Reference answer or check:** Constraints to check: no learned component; all rules computable in under 5 ms; a daily counter or token bucket for the 20 per cent cap with explicit exhaustion behaviour; a health check and fallback to the 1B model; log fields including at least request id, timestamp, rule fired, chosen model, quota state; three examples consistent with the rules.

---

### D1 · Array memory and strided view (looks hard, is easy)
**Prompt (verbatim, in a blockquote):**
> numpy 2.x. `x = np.zeros((10000, 512), dtype=np.float32)`. Three questions: how many bytes does `x.nbytes` report, and what is that in MiB; what is the shape of `x[:, ::2].T`; and is `x[:, ::2]` a view or a copy? One line each.

**Suggested label:** easy
**Why that label:** Three facts that follow from multiplication and basic indexing semantics, despite the large-looking numbers.
**How it will be scored:** A 5 gives 20,480,000 bytes (about 19.5 MiB), shape (256, 10000), and "view". The most likely failure is reporting 20 MiB as if MB and MiB were the same, or saying the strided slice copies.
**Reference answer or check:** 10,000 × 512 × 4 = 20,480,000 bytes = 19.53 MiB (20.48 MB). `x[:, ::2]` has shape (10000, 256); its transpose is (256, 10000). Basic slicing returns a view.

---

### D2 · Will the model fit (looks hard, is easy)
**Prompt (verbatim, in a blockquote):**
> I want to run a 7-billion-parameter model in bfloat16 on a GPU with 12 GB of memory. Quantisation is not an option. The KV cache costs 0.5 MB per token per sequence at this model size, I want a 4,096-token context, and I was thinking of batch sizes of 1, 2 or 4. Activations are small enough to ignore. Which batch size should I use, and how much memory will be left over?

**Suggested label:** easy
**Why that label:** The weights alone settle the question; the cache and batch figures are distractors.
**How it will be scored:** A 5 states that 7B parameters at 2 bytes each need 14 GB, which already exceeds 12 GB, so no batch size works and the question of leftover memory does not arise. The most likely failure is computing KV-cache totals for each batch size and recommending batch 1 anyway.
**Reference answer or check:** Weights 7 × 10⁹ × 2 bytes = 14 GB > 12 GB. Answer: none of the batch sizes; the model does not fit without quantisation, a smaller model or offloading.

---

### D3 · Compress a paragraph without losing facts (looks easy, is hard)
**Prompt (verbatim, in a blockquote):**
> Shorten the paragraph below to at most 40 words. Every fact in it must survive. Do not add anything.
>
> "tidelog is a small Python library, currently at version 0.4.2, whose purpose is to read newline-delimited JSON log files and write them out again as Parquet files so that they can be queried more efficiently. It has been tested on files of up to 8 GB in size. It requires Python 3.10 or newer, and its only third-party dependency is pyarrow. The project is released under the MIT licence, and the maintainers currently publish a new release roughly every six weeks."

**Suggested label:** hard
**Why that label:** The task reads as trivial editing but packing ten facts into 40 words without dropping or distorting one requires care that most models skip.
**How it will be scored:** A 5 is 40 words or fewer and carries all ten facts. The most likely failure is dropping the purpose (efficient querying), the release cadence or the "only" in "only dependency", or exceeding the word limit while claiming to be under it.
**Reference answer or check:** Ten facts: name tidelog; version 0.4.2; reads newline-delimited JSON; writes Parquet; purpose is more efficient querying; tested on files up to 8 GB; Python 3.10 or newer; pyarrow is the only third-party dependency; MIT licence; new release roughly every six weeks. The descriptors "small", "currently" and "has been" are not scored. The developer counts the words. A version carrying all ten facts, "small" and "third-party" in 39 words was constructed and counted, so the limit is achievable but tight.

---

### D4 · Group totals that do not add up (looks easy, is hard)
**Prompt (verbatim, in a blockquote):**
> pandas 2.x.
>
> ```python
> import pandas as pd
> df = pd.DataFrame({"k": ["a", "b", None, "a"], "v": [1, 2, 3, 4]})
> print(df.groupby("k")["v"].sum().sum())
> print(df["v"].sum())
> ```
>
> The two printed numbers differ. State both numbers, explain why they differ, and give the one-argument change that makes the group totals add up to the column total.

**Suggested label:** hard
**Why that label:** Looks like a two-line arithmetic check, but the cause is a non-obvious default that smaller models routinely do not know.
**How it will be scored:** A 5 prints 7 and 10, attributes the gap to `groupby` dropping rows whose key is missing by default, and gives `groupby("k", dropna=False)`. The most likely failure is blaming `None` being coerced, or suggesting `fillna` on the key column, which works but is not the one-argument change asked for.
**Reference answer or check:** First print 7 (groups a = 5, b = 2), second print 10. Fix: `df.groupby("k", dropna=False)["v"].sum()` yields a = 5, b = 2, NaN = 3, total 10.

---

### D5 · Train/test split with hidden structure (ambiguous)
**Prompt (verbatim, in a blockquote):**
> I have a DataFrame of 12,000 rows of irregularly sampled sensor readings from 40 machines collected over six months, columns `machine_id`, `timestamp`, twelve numeric features, and a binary `failure_next_24h` label. Give me the code to split it into train and test for a classifier. scikit-learn and pandas only.

**Suggested label:** hard
**Why that label:** Nothing is technically difficult, but the request does not say whether the test set should hold out unseen machines, a later time period, or random rows, and the three choices give very different answers about generalisation.
**How it will be scored:** A 5 either asks which kind of generalisation matters (new machines, future time, or neither) or picks one, says so explicitly, and names the alternatives in a sentence; code for the chosen option is correct (`GroupShuffleSplit` or `GroupKFold` on `machine_id`, a timestamp cut-off, or a plain shuffled split with the caveat that it leaks across time and machines). The most likely failure is a bare `train_test_split` with `shuffle=True` and no mention of leakage.
**Reference answer or check:** Must respect: the ambiguity is acknowledged, by question or by stated assumption; whichever split is chosen, the code uses only pandas and scikit-learn; a random row split is acceptable only if its leakage across time and machines is stated.

---

| ID | Suggested label | Expected answer length |
|----|-----------------|------------------------|
| W1 | easy | short |
| W2 | easy | short |
| W3 | hard | long |
| W4 | easy | short |
| W5 | hard | medium |
| P1 | easy | short |
| P2 | easy | short |
| P3 | hard | medium |
| P4 | hard | medium |
| P5 | easy | short |
| R1 | hard | medium |
| R2 | easy | short |
| R3 | hard | long |
| R4 | easy | short |
| R5 | hard | long |
| D1 | easy | short |
| D2 | easy | short |
| D3 | hard | short |
| D4 | hard | short |
| D5 | hard | medium |
