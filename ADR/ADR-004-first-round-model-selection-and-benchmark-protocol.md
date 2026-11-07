---
id: ADR-004
title: First-Round Model Selection and Benchmark Protocol
type: adr
status: amended
version: v1.8
canonical: true
scope: llth
audience:
  - developer
  - maintainer
  - operator
created: "2026-10-23"
updated: "2026-11-07"
tags:
  - llth
  - adr
  - model-selection
  - benchmark
  - quality-test
  - llama-cpp
subordinate_to: ADR-001
relationships:
  related:
    - ADR-002
    - ADR-003
    - DOC-IMPL-006
    - DOC-IMPL-017
    - DOC-IMPL-007
    - DOC-IMPL-008
    - DOC-IMPL-009
provenance:
  - human
---

# ADR-004 — First-Round Model Selection and Benchmark Protocol

## Status

Amended (v1.8)

---

## 1. Context

ADR-001 chose llama.cpp as the engine and ADR-003 built it (build 11839, CUDA architecture 75). This ADR chooses the **first round of five models to download and test**, fixes **how they are downloaded, stored and verified**, and fixes **how they are benchmarked and compared**, so that the final choice (a later ADR) is made on measurements, not estimates.

### Decision drivers

The designer's priorities, in order (confirmed 2026-10-23, with German removed as a criterion):
1. Independence and freedom to fine-tune: any-use licence, no gate, original weights available, open training data and recipe preferred.
2. The best quality and knowledge depth this machine can reach.
3. Tokens per second.

Constraints (verified 2026-10-23): RTX 2060 Mobile, 6 GB VRAM (5.7 GB usable); 32 GB RAM of which 24.7 GB available with the desktop running; no swap; 662 GB free disk; Turing GPU without BF16, FP8 or FP4; no sudo and no system pip; nothing outside `$LLTH_HOME/`.

Evidence base: model cards, licences, an independent quality index, speed measurements on small GPUs, German evidence, K2 Horizon support and fine-tuning. Key facts used here:
- One consistent independent quality index (Artificial Analysis v4.3.2): K2 Horizon MoVA 36B-A4B 25, K2 Horizon 7B 21, Qwen3.6-35B-A3B 18, Gemma 4 26B-A4B 17 (estimated), K2 Horizon 3.7B 16. The index measures reasoning and agent tasks, not this user's own writing and Python.
- K2 Horizon is Apache-2.0 and fully open (training data, code, logs, intermediate checkpoints). Its architecture, including MoVA, is in this build's source (commit `462524043`, 2026-10-06).
- Measured speeds on similar small GPUs: 17 to 33 tokens/s for the 35B-class MoE models; nothing measured on an RTX 2060 or on K2 Horizon.

### Rationale

Published scores do not show how these models behave on a 6 GB laptop with 24.7 GB of free RAM, how long they take to reach a final answer when they reason at length, or how good they are on the designer's own tasks. A small, controlled first round on exactly the files that would run answers those questions at a cost of about 64 GB of downloads and some hours of machine time.

---

## 2. Decision

### §1 The five models

One file per model, chosen to fit the hardware. All are GGUF files, so no custom Python code runs (the K2 Transformers code is not used).

| # | Model | Role | Publisher repo (source) | File | Size | SHA-256 (from the Hub's LFS metadata) |
|---|---|---|---|---|---|---|
| 1 | K2 Horizon 7B | Everyday, fast | `IFM/K2-Horizon-7B-GGUF` (the model's own authors) | `K2-Horizon-7B-Q4_K_M.gguf` | 5.59 GB (5,592,217,984 bytes) | `eb89c15a0ae9712be2ee462bf43802de14200f20f93b73da6eb68c2ebdd28e4e` |
| 2 | K2 Horizon 3.7B | Smallest, fine-tune candidate | `IFM/K2-Horizon-3.7B-GGUF` | `K2-Horizon-4B-Q5_K_M.gguf` (the repo names its files "4B") | 3.64 GB (3,643,776,384) | `944ec9515178a0e138a8951cd53e23967b9d24ff0604e07ca590ac2003f14066` |
| 3 | K2 Horizon MoVA 36B-A4B | Heavy model, fully open | `IFM/K2-Horizon-MoVA-36B-A4B-GGUF` | `K2-Horizon-MoVA-36B-A4B-Q4_K_M.gguf` | 22.37 GB (22,368,011,616) | `513dd78590ac29135a7cea5a99865d57d65291b1f857a8904fb9b1878d4f4cbd` |
| 4 | Qwen3.6-35B-A3B | Reference MoE (capability, coding) | `unsloth/Qwen3.6-35B-A3B-GGUF` (a well-known quantiser; Qwen publishes no GGUF) | `Qwen3.6-35B-A3B-UD-IQ4_XS.gguf` | 17.73 GB (17,730,509,792) | `649d7508507b84638732c4f52c24c8b15843c6dca2f3ff793ae07c14a67ebbb3` |
| 5 | Gemma 4 26B-A4B | Reference MoE (instruction following, speed) | `google/gemma-4-26B-A4B-it-qat-q4_0-gguf` (Google's quantisation-aware release) | `gemma-4-26B_q4_0-it.gguf` | 14.44 GB (14,439,363,584) | `3eca3b8f6d7baf218a7dd6bba5fb59a56ee25fe2d567b6f5f589b4f697eca51d` |

Total download: **63.77 GB**. Quant choices:
- Model 1: Q4_K_M, the largest quant that sits almost entirely in VRAM; the publisher's own quality check shows a small loss at Q4 (average 77.3 against 79.4 at BF16).
- Model 2: Q5_K_M, because the publisher's check shows a clear loss at Q4_K_M for this size (66.3 against 73.2).
- Model 3: the publisher's Q4_K_M, the smallest official file; if memory proves too tight, §6 allows a smaller quant.
- Model 4: Unsloth's dynamic IQ4_XS, the same file used in the published laptop benchmark.
- Model 5: Google's official quantisation-aware Q4_0, which is both the smallest and the one trained for 4-bit use.

### §1a Model 6: K2 Horizon 0.9B

**Rationale.** The K2 Horizon family has a model below the 3.7B (model 2), the 0.9B. The designer wants to keep the whole system inside one fully open fleet if the models work well for the purpose and a smaller sibling is the natural candidate for the steward role of §5a. A review of the publisher's pages on 2026-10-24 found **no non-thinking variant** anywhere in the family (121 repos under `IFM` checked): the 0.9B always reasons, and its only documented control is `reasoning_effort` (`high`, `medium`, `low`). Its card says "always `high`" and calls `medium` and `low` "not recommended except for research on reasoning efforts". Whether `low` works as a steward is therefore an open question that this amendment lets us measure; it is not a documented use.

**The model.**

| # | Model | Role | Publisher repo (source) | File | Size | SHA-256 (from the Hub's LFS metadata, read 2026-10-24) |
|---|---|---|---|---|---|---|
| 6 | K2 Horizon 0.9B | Smallest fleet member, candidate steward | `IFM/K2-Horizon-0.9B-GGUF` (the model's own authors), **pinned to revision `118965081cf1d876990219a1856a93a97b2668fa`** (last changed 2026-10-15) | `K2-Horizon-1B-Q8_0.gguf` (the repo names its files "1B"; the card says 0.9B, 1.08B stored parameters including embeddings) | 1.15 GB (1,148,614,016 bytes) | `741fb9ad263956c003883cb7caddeb14b4dfb9b4b67b5414ad12967e965dd547` |

- **Source:** the developers' own Hugging Face organisation, the same source as models 1 to 3. Licence Apache-2.0; not gated; no account or token. Only `huggingface.co` is contacted (§2 is unchanged).
- **Quantisation:** Q8_0. At this size the file is small enough that nothing is gained by a heavier quant, and small models lose more quality from aggressive quantisation than large ones. The repo also offers Q4_K_M (666,184,064 bytes), Q5_0, Q5_K_M (773,482,880), Q6_K and BF16 (2,159,424,896); these are **not** authorised here (Option G).
- **Download URL form:** `https://huggingface.co/IFM/K2-Horizon-0.9B-GGUF/resolve/118965081cf1d876990219a1856a93a97b2668fa/K2-Horizon-1B-Q8_0.gguf`, to `$LLTH_HOME/models/IFM/K2-Horizon-0.9B-GGUF/K2-Horizon-1B-Q8_0.gguf`, with `curl -L -C -` and `sha256sum` verification exactly as in §2 (a mismatch means delete and retry; a second mismatch means stop and report). A small download script in the style of `$LLTH_HOME/benchmarks/scripts/models/download-remaining-models.sh` may be written for this one file. The total download of the six models becomes **64.92 GB**.
- **Timing:** the download starts only after models 3, 4 and 5 are downloaded and verified (2026-10-24).

**How the other sections apply to model 6.**
- **§3 test conditions and memory safety:** unchanged. The 0.9B is a small dense model and should fit entirely in VRAM; no expert or layer-split sweeps are expected.
- **§4 speed benchmark:** the protocol for dense models, with both cache variants (`q8_0` and `q4_0`) and depths 0, 8K, 16K and 32K. The model's maximum context is 128K; longer depths are exploration under §4a.
- **§4a exploration:** unchanged. The `K2-Horizon-0.9B-Uno` diffusion adapter is a separate artefact and is **not** authorised.
- **§5 quality test:** model 6 joins the blind test with the sampling values on its card at test time, recorded with each answer. The card recommends temperature 0.6 and top_p 0.95 and asks for at least 32,768 output tokens; its own examples use temperature 1.0, so the value actually used is recorded. The reasoning effort is `high`, the card's recommendation.
- **§5a steward test:** model 6 is a candidate steward in two configurations, `reasoning_effort` `low` and `medium` (research use per its card), and with `high` for comparison. The per-request control is a chat-template argument; the exact `llama-server` flag is verified with `--help` on this build at test time and recorded. It also runs as a specialist under the normal §5 test.
- **§6 gates and selection:** the small-model gates apply (at least 20 tokens/s at 8K, stability, thermals). Model 6 competes with models 1 and 2 for the "everyday model" role by the same rule, and is eligible for the steward role under §5a. The heavy-model rule is unchanged.

**Known risks and open points.**
- The card states that llama.cpp support for the `k2-horizon` architecture merged in release b11454; this build is 11839, so it should load, but this is verified at the first run and not assumed.
- All benchmark numbers on the card (for example AIME 2026 48.5, HumanEval+ 79.9, LiveCodeBench v6 37.4, BFCL v4 28.0) are the publisher's own, measured at `high` effort; none is reproduced here. The card lists English and Chinese; German is not a criterion.
- The technical report was announced as "in progress" with an expected date of end of September 2026 and was not yet available on 2026-10-24.
- The model may spend most of its time reasoning even at `low`; time to the final answer, not tokens per second alone, is the measure that matters (§5).

### §2 Download, location and verification

- **Location:** `$LLTH_HOME/models/<publisher>/<repo>/<file>`, for example `$LLTH_HOME/models/IFM/K2-Horizon-7B-GGUF/K2-Horizon-7B-Q4_K_M.gguf`. The `models/` folder already exists.
- **Method:** one file at a time with `curl -L -C -` from `https://huggingface.co/<repo>/resolve/main/<file>` (resumable, no login, no account, no Python packages). The `-hf` downloader of llama.cpp is not used here, so that each file's location and checksum are explicit.
- **Verification:** `sha256sum` of every file against the table above. A mismatch means the file is deleted and downloaded again; it is never used.
- **Free disk before and after** is recorded; 662 GB are free, so space is not a constraint.
- Only `huggingface.co` is contacted. No authentication token is used or created.

### §3 Test conditions

Every benchmark run records: mains power connected; performance profile; no browser or other large process running; `free -m`, GPU temperature and `nvidia-smi` memory before the run; the llama.cpp build (11839, commit `e1e3b2c40`); the exact command. GPU temperature at the start of each model's runs must be at or below 50 °C (the idle value today is 43 °C); a pause between models allows cooling.

**Memory safety.** The machine has no swap, so exhausting RAM kills a process. Therefore the first runs use the llama.cpp defaults (memory-mapped model files, which the kernel can reclaim) and **do not use `--no-mmap` or `--mlock`**, which several published guides use for speed but which make memory unreclaimable. Expert placement is swept from the safe side: for each MoE model, start with the experts of all layers on the CPU, check headroom, then move layers to the GPU in steps.

### §4 Speed benchmark (objective)

`llama-bench` from `$LLTH_HOME/llama.cpp/build/bin/`, flags verified with `--help` on this build:
- All models: `-p 512 -n 128 -r 3 -fa on -ctk q8_0 -ctv q8_0 -d 0,8192,16384,32768 -o md` (prompt speed and generation speed, three repetitions, at four context depths; only the K and V cache types compiled into this build, ADR-003).
- MoE models (3, 4, 5): additionally sweep `-ncmoe` (number of layers whose experts stay on the CPU) downward in steps until the model no longer loads; record the stable minimum. `-ngl 99` throughout.
- Dense models (1, 2): sweep `-ngl` from 99 down in steps until all layers fit in VRAM with the cache at 32K depth; record the setting and VRAM used.
- **Cache-type variant.** Every speed sweep above is run twice: the baseline with `-ctk q8_0 -ctv q8_0` and a variant with `-ctk q4_0 -ctv q4_0`. The `q4_0` cache halves the memory used by the context, which may keep more layers on the GPU at long context, at some cost in answer quality that the speed benchmark cannot see. Both variants are compiled into this build (ADR-003, flash-attention combinations `q8_0-q8_0` and `q4_0-q4_0`). Results from the two variants are always reported side by side and never merged.
- Each run's output goes to `$LLTH_HOME/benchmarks/` (a new folder, §6) as markdown, plus the commands and the before/after memory and temperature readings.

### §4a Exploration phase

Alongside the fixed protocol above, **exploration experiments** are authorised under these rules.

**Authorised without a further ADR** (all use the existing binaries and the five downloaded models; nothing is installed or changed on the system):
- Any runtime flag that `llama-bench` or `llama-server` accepts in this build, for example `-ub`, `-b`, `-t`, `--cpu-mask`, `--cpu-strict`, `--poll`, `-nkvo`, `-nopo`, `--mmap`, `-ngl`, `-ncmoe`, flash attention on or off, and the cache-type combinations that were compiled (`q8_0`/`q8_0`, `q4_0`/`q4_0`, `f16`).
- Context depths up to what the model and memory allow; repeated runs; side-by-side comparisons.

**Not authorised without a separate approval or ADR:**
- Rebuilding llama.cpp (ADR-003 amendment), for example to compile more cache-type combinations.
- Downloading further models or other quantisations (a new ADR or an ADR-004 amendment).
- Anything needing `sudo` or changing system settings (the CPU governor, power profiles, BIOS, drivers, clocks): the designer runs such commands themselves.
- Running code that a model generated, and Python packages (venv and approval rules).

**Safety limits for every experiment run:**
- The helper script stops a run if the GPU reaches **92 °C** or available RAM falls below **1,500 MiB**, and records that it did so.
- The machine stays on mains power. Experiments run one at a time.
- The baseline settings of §4 are always re-measured alongside any tuned setting in the same session, so improvements are comparisons, not memories.

**Recording:** every experiment goes into `$LLTH_HOME/benchmarks/` with the command, the conditions and the peak readings. Tuned settings that beat the baseline are noted as candidates, then adopted only through the decision in §6 or in ADR-005.

### §5 Quality test (subjective, blind)

- **Prompts:** 15, in three groups of five: English writing (varied tone and length), Python (the designer's actual libraries and tasks), and multi-step reasoning or planning. The prompts are the designer's: a draft is proposed, the designer edits and approves the final set before any run. Prompts are saved in `$LLTH_HOME/benchmarks/prompts.md` so every model sees the identical text.
- **Settings:** each model with the sampling values and reasoning mode on its own card at test time (K2 Horizon: `reasoning_effort="high"`, temperature 1.0, top_p 0.95, at least 32,768 output tokens; the others per their cards), recorded with each answer. For Qwen3.6, an additional run with thinking switched off.
- **Blind scoring:** answers are stored under random labels (A to E per prompt, re-shuffled per prompt). The designer scores each answer 1 to 5 for overall usefulness before the labels are revealed. Python answers are run by the designer in their own environment and are not otherwise executed.
- **Also recorded per answer:** hidden-reasoning tokens, answer tokens, time to the final answer, and whether the model looped or failed to finish.

### §5a Steward test

The design under test routes everyday requests to a fast, less-thinking "steward" model that answers routine questions and escalates hard ones to a reasoning specialist. The quality test therefore also measures steward behaviour. ADR-005 later decided against automatic routing.

- **Labels before any run.** The designer labels each of the 15 prompts **easy** (a short answer or a short snippet suffices) or **hard** (needs long multi-step reasoning) before any model sees them. Optionally, five further "deceptive" prompts are added: ones that look hard but are easy, or look easy but are hard.
- **Steward configuration.** Each model is also run with a fixed system prompt along the lines of: *answer directly if you can do so reliably in a few sentences or a short snippet; if the task needs long multi-step reasoning, reply with exactly the word ESCALATE*. Where a model can switch its reasoning off, it is run with reasoning off (and, for comparison, with its default setting).
- **Measured per model:**
  1. **Routing accuracy:** the share of prompts routed as labelled (answered when easy, ESCALATE when hard), reported separately for false escalations (waste) and missed escalations (wrong answers where depth was needed).
  2. **Easy-prompt answer quality**, blind-scored as in §5.
  3. **Cost on easy prompts:** hidden-reasoning tokens, answer tokens and time to the final answer.
- **Use of the result.** The steward is the model with the best combination of fast, good easy answers and reliable routing; the specialist is chosen by §6. The routing logic itself is a separate decision (a later ADR). Candidate stewards beyond the five in §1 can be added by amendment.

### §5b Runner, run configurations and scoring procedure

**Rationale.** §5 and §5a define what the tests measure but not how they are run. Three facts need a decision: (1) none of the `llama-server` commands used by hand so far has a context large enough for the card's 32,768 output tokens (the first-session commands use `-c 16384`); (2) the 7B generates about 3 tokens/s at 32K depth (`DOC-IMPL-012` section 6), so 32K output is impractical for it; (3) the 3.7B and K2 MoVA reach 32K only with the `q4_0` cache. This section fixes the prompt set, the scripts, the run configurations, the scoring procedure and the order of work, so that the results are reproducible and the choices are on record before any model runs.

**Decision.** The quality and steward tests run under the protocol in `DOC-IMPL-017`. It fixes the frozen prompt set (`DOC-IMPL-008` v1.0, SHA-256 `8d5e4fa32e0285a8dd7423f2f9d3314da5983dfaf7f908be17fb6a017f732e1f`), two Python standard-library scripts that act as a client of `llama-server`, one run configuration per model (context 34,816 and 32,768 output tokens, except the 7B at context 16,384 and 15,000 output tokens), the `q4_0` cache for the 3.7B and K2 MoVA, fixed sampling and seeds, the order of work (largest model first; thinking-control tests before the steward pass), the steward system prompt and routing rule, and the blind-scoring procedure. A change to the protocol needs an amendment of this ADR. One exception to the rule that model output is not executed was made on 2026-11-05 for the round 1 Python check (`DOC-IMPL-017` section 8).

### §6 How the results will decide

Hard gates (confirmed by the designer on 2026-10-23):
1. **Stability:** completes the full prompt set without being killed or crashing, with at least 3 GB of RAM still available at the peak.
2. **Speed:** generation of at least 8 tokens/s at 8K depth for the heavy models (3 to 5), and at least 20 tokens/s at 8K depth for the small models (1 and 2). A model passes this gate if **either** cache variant (§4) meets it. If only the `q4_0` variant passes, the model is carried forward with the `q4_0` cache, and the quality test (§5) runs in exactly that configuration, so any quality cost of the cache is included in the blind scores.
3. **Thermals:** no sustained throttling (a drop of more than 30% in generation speed within one run).

Among the models that pass: the **heavy model** is the one with the highest blind quality score; the **everyday model** is the best of models 1 and 2 on quality per time to the final answer. Ties are broken by speed, then by openness. A later ADR (ADR-005) records the choice and the launch configuration. If no heavy model passes the gates, the fallback is to run the best small model only.

### §7 Consequential changes this ADR authorises

This ADR covers creating `$LLTH_HOME/models/IFM/`, `/models/unsloth/` and `/models/google/` subfolders (with the repo folders under them) and `$LLTH_HOME/benchmarks/`, downloading and verifying the five files as in §2, and running the benchmarks in §4. No file outside `$LLTH_HOME/` is altered. The quality test in §5 starts only after the designer has approved the prompt set.

---

## 3. Consequences

### Positive

- The final selection rests on measured speed and the designer's own blind judgements on this exact machine.
- Every file is verified and its origin is documented; all five are available without an account, and three are from the authors themselves.
- One fully open family (K2 Horizon) is tested at all three of its sizes, against the two reference models.
- Small downloads first (K2 3.7B and 7B) show quickly whether the K2 architecture runs here.

### Negative

- About 64 GB of downloads and several hours of machine time, with the laptop under sustained load.
- Models 4 and 5 are third-party or vendor quantisations of unknown quality against their originals; the benchmark measures the file, not the underlying model.
- The K2 Horizon models reason at length, so time to the final answer is long and the 32K output budget may be needed.
- Fine-tuning is not tested in this round.
- The §5 pass alone has an upper bound of about 54 hours of machine time (§5b), the 3.7B and K2 MoVA are scored with the `q4_0` cache, the 7B with a shorter output budget, and one sample per cell leaves sampling variance in the scores.

### Implementation notes

- Step order: (1) create the folders; (2) download and verify models 1 and 2, then run their benchmarks; (3) download and verify models 5, 4 and 3, benchmarking each; (4) quality test after prompt approval; (5) write the results as a governed document, then draft ADR-005.
- A file that fails verification twice is not used.
- If a model needs more than the flags listed here to load, record that in the results and in `DOC-IMPL-001` (known issues), but do not change the build without an ADR-003 amendment.
- Speculative decoding (draft models), larger quants, other candidates and launcher scripts are separate decisions.

### Related

- ADR-001 — llama.cpp as the Local Inference Engine
- ADR-002 — Native User-Space Install, No Docker, Localhost Only
- ADR-003 — llama.cpp Build Configuration
- `DOC-IMPL-017` — Quality Test Protocol

---

## 4. Non-goals

- Choosing the final model, or writing launch scripts (a later ADR).
- Fine-tuning or training of any kind.
- German-language quality (dropped by the designer on 2026-10-23).
- Vision, audio or tool-use features.
- Retrieval (RAG) and document search.
- Speculative decoding, other quantisations, other runtimes, container isolation.

---

## 5. Options considered

### Option A — Five models, one file each (chosen)
Covers the whole range (3.7B to 36B), three sizes of the open family against two reference models, at a bounded cost.

### Option B — Three models (K2 7B, Qwen3.6, Gemma 4)
Cheaper (about 38 GB) but leaves the 36B K2 model and the 3.7B untested, which are the most important for the independence priority.

### Option C — Choose without testing
Rejected: nothing about speed or answer length on this machine is known, and the published scores do not measure the designer's tasks.

### Option D — Include gpt-oss-20b and Trinity Mini as probes
Deferred. gpt-oss-20b scores 9 on the index; Trinity Mini has no independent score. They can be added as a second round if the first round leaves a gap.

### Option E — Other quantisations (for example Unsloth's Q4_K_XL for Gemma, Bartowski for Qwen)
Rejected for round one: Google's own QAT release is the better-documented Gemma file, and Unsloth's IQ4_XS is the file behind the published laptop measurement. Different quants can be compared later.

### Option F — Download BF16 and quantise locally
Rejected: 75 GB for the large model alone, a conversion step to verify, and no benefit over the authors' own GGUFs.

### Option G — Add the 0.9B in several quantisations, or from the safetensors
Rejected for now: the Q8_0 file from the authors' own GGUF repo answers the question (does the smallest fleet member work as a steward or everyday model?) with one 1.15 GB download. Additional quants (for example Q5_K_M for comparison with model 2) or a local conversion from safetensors can follow by amendment.

### Option H — One uniform output budget of 16K tokens for all models
Rejected for the main pass: it makes the runs shorter and the 7B comparable, but it truncates the K2 Horizon models below the 32,768 tokens their cards ask for, which penalises the models the designer most wants to succeed (§3, Negative). It remains the fallback if the load tests or the pilot show the 32K configurations to be unstable or too slow.

### Option I — Card-compliant budgets (32,768 tokens) with the `q4_0` cache where needed; the 7B at 15,000 (chosen)
Matches each model's documented use and keeps the context identical (`-c 34816`) for five of the six models; the costs are the longer runs and the `q4_0` cache for two models.

### Option J — Two tiers: a 16K pass for everything, then a 32K re-run only of the answers that were truncated
Cheaper in machine time, but it mixes two configurations inside one model's scores and needs a second pass to be scheduled; rejected for complexity. It can be reconsidered if the pilot shows that few answers need more than 16K tokens.

---

## 6. Amendment record

| Version | Date | Summary |
|---------|------|---------|
| v1.0 | 2026-10-23 | Initial. Accepted by the designer on 2026-10-23, who confirmed the decision thresholds (§6) and the quantisation choices (§1) as written. |
| v1.1 | 2026-10-23 | Added the `q4_0` KV-cache variant to the speed benchmark (§4) and the rule for gate 2 and the quality test (§6). Reason: the first measurement of K2 Horizon 7B Q4_K_M with the `q8_0` cache gave 40.0 tokens/s at depth 0 but 14.8, 3.8 and 1.3 tokens/s at 8K, 16K and 32K, failing the 20 tokens/s gate at 8K; the cache memory is the cause. Requested and approved by the designer. |
| v1.2 | 2026-10-23 | Added §4a, the exploration phase: what may be varied without further approval, what needs a separate approval, and safety limits (92 °C GPU, 1,500 MiB RAM). Requested by the designer, who wants to explore what the system can do at its limits. |
| v1.3 | 2026-10-24 | Added §5a, the steward test: easy/hard labels set by the designer before any run, a routing prompt, and measures for routing accuracy, easy-prompt quality and cost. Requested by the designer, who plans to route everyday requests to a less-thinking steward model. |
| v1.4 | 2026-10-24 | Adds §1a, model 6 K2 Horizon 0.9B (`K2-Horizon-1B-Q8_0.gguf`, 1,148,614,016 bytes, from the authors' own repo pinned to revision `118965081cf1d876990219a1856a93a97b2668fa`), to be downloaded after models 3 to 5, with Option G. Reason: the K2 Horizon family has no non-thinking model, and the designer wants to test whether the smallest sibling can serve as steward or everyday model inside one fully open fleet. Requested by the designer on 2026-10-24; accepted by the designer on 2026-10-24 as written. |
| v1.5 | 2026-10-30 | Adds §5b: the approved prompt set (`DOC-IMPL-008` v1.0, SHA-256 recorded), two Python scripts as a client of `llama-server` (runner; blinding and tally), run configurations per model with the 32,768-token output budget for five models and 15,000 for the 7B, sampling and seed rules, the order of work (thinking-control tests before the steward pass), the steward system prompt and the routing rule fixed in advance, and the blind-scoring procedure; Options H to J. Reason: the first-session server commands use `-c 16384`, too small for the cards' 32K output, and the 7B cannot generate at 32K depth. Drafted and **accepted by the designer on 2026-10-30 as written**, including Option I (output budgets), the 0.9B temperature of 0.6 and the steward system prompt. Open before the pilot, by design: the load tests of the six configurations, the reasoning-control mechanism, and the Qwen and Gemma card values. |
| v1.6 | 2026-10-30 | §5b item 4: run order changed from cheapest-first (0.9B, 3.7B, Gemma, Qwen, K2 MoVA, 7B) to largest-first (K2 MoVA, Qwen, Gemma, 7B, 3.7B, 0.9B); the pilot moves to the first model in the run order and the load test to each model's first server start. Requested by the designer on 2026-10-30. No other decision changed. |
| v1.7 | 2026-11-05 | §5b item 7: records a one-time exception to the no-execution rule. After scoring and reveal, the designer had the round 1 Python answers (P1 to P4) run to verify correctness; the rule otherwise stands. Records the round 1 result set chosen by the designer: the designer's scores for writing, reasoning and deceptive prompts, with the Python rows rescored after running the code (`scores-quality-round1-final.csv`; results in `DOC-IMPL-010`). The reasoning-effort probes of the same session (PD-014, `DOC-IMPL-015`) are flag-level exploration under §4a and need no amendment. Requested by the designer on 2026-11-05. |
| v1.8 | 2026-11-07 | §5b moved to `DOC-IMPL-017`; the ADR keeps the decision and the rationale. Editorial revision for publication. |
