---
id: DOC-IMPL-006
title: Benchmark Results: Overview
type: implementation
status: active
version: v2.0
canonical: true
scope: llth
audience:
  - developer
  - maintainer
  - operator
created: "2026-10-23"
updated: "2026-11-08"
tags:
  - llth
  - benchmarks
  - speed
  - overview
relationships:
  related:
    - ADR-003
    - ADR-004
    - DOC-IMPL-002
    - DOC-IMPL-010
    - DOC-IMPL-012
    - DOC-IMPL-013
    - DOC-IMPL-014
    - DOC-IMPL-015
    - DOC-IMPL-016
provenance:
  - human
---

# Benchmark Results: Overview

Speed measurements on the reference machine for the six models of ADR-004, with the exploration rounds, the reasoning-effort probes and the model swap time. This document holds the method, the conditions, the gate verdicts, the summary of findings, the experiment list and the index of raw data. The results are in:

| Document | Contents |
|---|---|
| `DOC-IMPL-012` | Small models: K2 Horizon 7B, 3.7B and 0.9B; exploration rounds 1 and 2 |
| `DOC-IMPL-013` | Large models: Gemma 4 26B-A4B, Qwen3.6-35B-A3B and K2 Horizon MoVA 36B-A4B |
| `DOC-IMPL-014` | Power-profile tests (balanced against performance) |
| `DOC-IMPL-015` | Reasoning-effort probes on the K2 3.7B and K2 MoVA |
| `DOC-IMPL-016` | Model swap time between the K2 3.7B and K2 MoVA |

The quality results are in `DOC-IMPL-010`. The raw logs are in `$LLTH_HOME/benchmarks/`.

## 1. Method

- **Tool:** `llama-bench` from `$LLTH_HOME/llama.cpp/build/bin/` (build 11839, commit `e1e3b2c40`), run through `bench_wrap.sh`, which samples GPU memory, temperature and clock and the free RAM once per second.
- **Common settings:** `-p 512 -n 128 -r 3 -fa on`. "Reading" below is `pp512`, the speed of processing 512 new prompt tokens when `d` tokens of context are already in place; "generation" is `tg128`, the speed of producing 128 tokens. `d` is the context depth: 0, 8192, 16384 or 32768 tokens. All figures are tokens per second, the mean of three repetitions (the standard deviations are in the logs and are small, typically under 3%).
- **Cache variants (ADR-004 v1.1):** baseline `-ctk q8_0 -ctv q8_0`; variant `-ctk q4_0 -ctv q4_0`. The `q4_0` cache halves the cache memory and may cost some answer quality that this benchmark cannot see; the quality test must run in the configuration that is carried forward.
- **GPU layers (`-ngl`):** for each depth, several values were tried from "all" (99) downward. "Did not load" means the model plus cache plus working buffers did not fit in VRAM at that setting (a `cudaMalloc` out-of-memory error).
- **Files:** the exact files and SHA-256 values are in ADR-004 sections 1 and 1a. `K2-Horizon-7B-Q4_K_M.gguf` (5,592,217,984 bytes) and `K2-Horizon-4B-Q5_K_M.gguf` (3,643,776,384 bytes) were verified against them, and the other four as described below.

### Model files

- Models 5, 4 and 3 were downloaded with `download-remaining-models.sh` (file times: Gemma 18:40, Qwen 19:07, K2 MoVA 19:40). Verified afterwards, independently of the script: **sizes match ADR-004 section 1 to the byte, and `sha256sum -c` against the ADR values reported OK for all three** (2 minutes 6 seconds). No download process or partial file remained; 599 GB of disk were free.
- Model 6 (K2 Horizon 0.9B, `K2-Horizon-1B-Q8_0.gguf`) was downloaded with `download-k2-horizon-0.9b.sh` under ADR-004 v1.4 section 1a from `IFM/K2-Horizon-0.9B-GGUF`, pinned to revision `118965081cf1d876990219a1856a93a97b2668fa`. Verified: 1,148,614,016 bytes (exact), SHA-256 `741fb9ad…dd547` OK, file begins with the `GGUF` magic.

## 2. Conditions and deviations

- **Software:** llama.cpp build 11839 (`e1e3b2c40`); CUDA 13.3; one CUDA device (RTX 2060, compute capability 7.5, 5,746 MiB). Mains power connected.
- **Deviations from ADR-004 section 3 (first sweeps, models 1 and 2):**
  - Chrome (several processes, about 19% of one CPU core) was open during all runs of the first sweeps. Later runs had it closed.
  - The CPU governor name reads `powersave`, but that is how the `intel_pstate` driver reports it. The designer set the **performance power profile in the system settings before the first benchmark** [reported by the designer]. At later checks the profile service reported `performance`, the energy performance preference was `performance`, turbo was enabled, and the cores ran at 3.5 to 4.3 GHz even when idle. The ADR's "performance profile" condition was therefore met. The helper did not record the preference or the live frequency during the first sweeps (it logged only the governor name), so this rests on the designer's statement; later logs record all of them.
  - GPU temperature at the start of a run was often above the 50 °C the ADR asks for (47 to 66 °C), because only a 20-second pause separated runs.
  - A download of the Gemma 4 file (nice 19, about 1.4 GB, stopped by the designer) overlapped the first runs of the 7B depth sweep, between about 21:40 and 21:43.
- **Thermal evidence is limited.** The helper recorded the peak SM clock per run (1,680 to 1,890 MHz of 2,100 at up to 89 °C) and the standard deviations were small, so there is no sign of throttling, but it did not log the clock continuously during busy periods. A continuous log is part of the next helper version (the project copy of `bench_wrap.sh` now also stops a run at 92 °C GPU or 1,500 MiB free RAM).
- **One scripting error and its cleanup.** The first depth sweep was launched from zsh, which does not split `$pair` into two words like bash does, so every command was malformed and no measurement was made. The invalid log was deleted and the sweep was rerun from a bash script.
- **Quality is not measured here.** Speed only; quality is reported in `DOC-IMPL-010`.

## 3. Gate verdicts (ADR-004 section 6)

Speed thresholds: at least 20 tokens/s at 8K depth for the small models, at least 8 for the large models. The gate verdicts of all six models:

| Model | Generation at 8K (tokens/s) | Speed gate | Lowest free RAM | Highest GPU temperature | Where |
|---|---|---|---|---|---|
| K2 Horizon 7B | 23.6 (`q4_0`); 14.8 (`q8_0`) | Pass with `q4_0` only | 23.9 GiB | 89 °C | `DOC-IMPL-012` §1 |
| K2 Horizon 3.7B | 33.9 (`q8_0`); 34.6 (`q4_0`) | Pass | 23.9 GiB | 86 °C | `DOC-IMPL-012` §2 |
| K2 Horizon 0.9B | 100.2 (`q8_0`); 100.7 (`q4_0`) | Pass | 22,689 MiB | 69 °C | `DOC-IMPL-012` §4 |
| Gemma 4 26B-A4B | 23.6 (`q8_0`); 23.3 (`q4_0`) | Pass | 22,862 MiB | 84 °C | `DOC-IMPL-013` §2 |
| Qwen3.6-35B-A3B | 18.2 (`q8_0`); 17.5 (`q4_0`) | Pass | 22,994 MiB | 86 °C | `DOC-IMPL-013` §3 |
| K2 Horizon MoVA 36B-A4B | 9.9 (`q8_0` and `q4_0`) | Pass | 21,648 MiB | 88 °C | `DOC-IMPL-013` §4 |

The 7B is carried forward with the `q4_0` cache. The quality test (ADR-004 section 5) is reported in `DOC-IMPL-010`.

## 4. Summary of findings

1. **Both small models run on this machine, and fast at short context.** K2 Horizon 7B (Q4_K_M) generates **40.0 tokens/s** with all layers on the GPU at depth 0; K2 Horizon 3.7B (Q5_K_M) generates **56.1 tokens/s**. Prompt reading is 1,068 and 1,687 tokens/s.
2. **Context depth is the limit, because of VRAM.** The 7B's weights (5.2 GiB) nearly fill the 5.6 GiB card, so the context cache pushes layers to the CPU as context grows, and speed falls steeply.
3. **The `q4_0` cache is the main lever.** With it the 7B passes the ADR-004 speed gate at 8K (23.6 tokens/s against the 20 required), and the 3.7B holds **14.2 tokens/s at 32K with every layer on the GPU**, where the `q8_0` cache could not load at all and the best partial-offload setting managed 3.2.
4. **Gate verdicts (ADR-004 section 6):** K2 Horizon 3.7B passes the speed gate with both caches. K2 Horizon 7B passes only with the `q4_0` cache. Both are stable (at least 23.9 GiB of RAM free throughout). Thermals reached 89 °C at the worst point; see section 2.
5. **Exploration round 1 (`DOC-IMPL-012` section 5)** found a cheap lever: a smaller working buffer (`-ub 128`) lets the 7B keep 36 of 37 layers on the GPU at 16K and generate **15.7 tokens/s instead of about 6**, at the price of 27% slower prompt reading.
6. **Exploration round 2 (`DOC-IMPL-012` section 6)** confirmed the small-buffer lever and found a better setting: with `-ub 64` the 7B keeps **all layers on the GPU at 16K and generates 18.6 tokens/s** (3 times the baseline), and at 8K `-ub 128` with all layers gives 26.7. At 32K nothing helps enough (about 3 tokens/s).
7. **Power-profile A/B test (`DOC-IMPL-014` section 1)** found no meaningful speed difference between the balanced and performance profiles (balanced +1.0% to +2.4%, within noise); earlier results stay valid.
8. **Model 6, K2 Horizon 0.9B (`DOC-IMPL-012` section 4)** generates **164.8 tokens/s at depth 0, 100 at 8K, 69 at 16K and 41 at 32K** with every layer on the GPU (about 3 times the 3.7B at every depth), and the `q4_0` cache gives no speed advantage for it.
9. **Large model 5, Gemma 4 26B-A4B (`DOC-IMPL-013` section 2)** passes all gates: with the experts of 24 of 30 layers on the CPU it generates **25.3 tokens/s at depth 0, 23.6 at 8K and 20.1 at 32K** (`q8_0` cache) and slows by only 20% over that range; `q8_0` is equal or better than `q4_0` for it.
10. **Large model 4, Qwen3.6-35B-A3B (`DOC-IMPL-013` section 3)** passes all gates with the experts of 34 of 40 layers on the CPU: **19.2 tokens/s at depth 0, 18.2 at 8K, 13.7 at 32K** (`q8_0` cache), a 29% slowdown over that range; it is slower than Gemma at the same split, and the 32K runs reached 86 °C.
11. **Large model 3, K2 Horizon MoVA 36B-A4B (`DOC-IMPL-013` section 4)** needs a tensor override to load: its 4,050 MiB of attention value experts are not moved by `-ncmoe`; with `-ot 'attn_v_exps=CPU'` it runs. Best stable setting ncmoe 46: **11.5 tokens/s at depth 0, 9.9 at 8K, 8.8 at 16K** (`q8_0`); at 32K only the `q4_0` cache fits (6.6 tokens/s, 88 °C). It is the slowest large model and its KV cache is the largest (about 0.10 MiB per token with `q8_0`), so for it the cache type decides what fits.
12. **All six models are now speed-benchmarked** (`DOC-IMPL-013` section 5 compares the three large ones).
13. **The combined power-profile A/B over models 3 to 6 (`DOC-IMPL-014` section 2)** found balanced about 2% slower on average (7 of 8 tests negative), but only the fast, GPU-only 0.9B shows a difference clearly beyond the spread within a profile (3.5% and 4.6% slower); for the large models the differences are inside the phase-to-phase spread. `performance` stays the benchmark condition.
14. **Open questions** are in section 5 (the experiment list).

## 5. Experiment list

Each could be run under ADR-004 section 4a (exploration phase) unless marked.

| # | Idea | Rationale | Cost / approval |
|---|---|---|---|
| 1 | **Done (`DOC-IMPL-012` section 5; a winner).** `-ub 256` and `-ub 128` on the 7B at 16K | A smaller working buffer frees 250 to 400 MiB for 2 or 3 more layers; quality not measured | Flag only |
| 2 | **Done at 16K (`DOC-IMPL-012` section 5; modest).** `-nkvo 1` (cache in RAM, all weights on the GPU) on the 7B at 16K and 32K | May beat the layer-split cliff | Flag only |
| 3 | **Partly done (`DOC-IMPL-012` section 5; small).** Thread count `-t 8`, `-t 12`, `--cpu-mask` for the CPU-resident layers | CPU attention may be thread-bound | Flag only |
| 4 | **Done (`DOC-IMPL-012` section 5; works, but less than `-ub 128` alone).** `--override-tensor` to keep only the large output matrix (250,624-token vocabulary) on the CPU while all transformer layers stay on the GPU | The 7B's step from 37 to 36 layers already gained 7 tokens/s at 8K; the output matrix may be why. | Flag only |
| 5 | **Done (`DOC-IMPL-014` section 1; no meaningful difference).** Balanced against performance power profile, then repeat a few runs; Chrome closed | Quantify what the profile is worth in tokens/s (the earlier sweeps already ran under performance, so only the Chrome effect and the profile effect itself remain) | The designer switches the profile in the settings; no sudo |
| 6 | Mixed cache types (K at `q8_0`, V at `q4_0`) | Not tested | Needs a rebuild (ADR-003 amendment) |
| 7 | **Done (`DOC-IMPL-013`).** Compare the same sweeps on the three large MoE models | The real long-context contest; expert placement adds a dimension | Flag only |
| 8 | Speculative decoding with a draft model for Gemma 4 and Qwen3.6 | Not measured on this machine | Extra download (ADR amendment) |
| 9 | The K2 "Uno" diffusion adapter for faster inference | Experimental; needs custom code | Needs its own ADR and a careful review |
| 10 | A GPU clock and temperature plot over a long run | Settle the throttling question | Helper change only |
| 11 | **Research track R1: quality–speed study of cache types and quantisation.** `llama-perplexity` and KL divergence against a high-precision reference on K2 Horizon 3.7B: `f16`/`q8_0`/`q4_0` caches and Q4_K_M/Q5_K_M/Q6_K/Q8_0 weights, several runs, paired with the speed results as a Pareto frontier | Settles the quality blind spot of the speed benchmarks (ADR-004 v1.1); a publishable, reproducible small study. Reuses built tools; may need the BF16 reference file (about 10 GB, an ADR-004 amendment) | Flags and measurement; one possible download |
| 12 | **Research track R2: small-architecture ablations.** Train 20 to 50 million parameter transformer variants (attention types, normalisation, MoVA-like ideas) on this GPU with clean controls; K2 Horizon's open data and code are the reference | Architecture design and experiment design at a scale this machine can reach; larger runs can be rented | Needs a Python environment (venv, pip with approval), PyTorch on Turing, its own project folder and ADR; keep out of LLTH's scope |
| 13 | Model 6 (0.9B) at 64K and 128K depth, and with 12 threads on the large MoE models | `DOC-IMPL-012` section 4 shows the 0.9B needs only 2.3 GiB of VRAM at 32K, so the 128K maximum may fit; the large models are CPU-bound, where threads mattered most (`DOC-IMPL-012` section 6.1 point 4) | Flag only (ADR-004 section 4a) |
| 14 | Apply the round 1 and 2 lever (`-ub 128` or `-ub 64`) and single-layer `-ncmoe` steps (for Gemma: 23, or 22 with a small buffer) to the large MoE models | A smaller compute buffer freed VRAM for more layers on the 7B; here it may allow experts of one or two more layers on the GPU, worth about 0.5 to 1 token/s per layer [E] | Flag only (ADR-004 section 4a) |
| 15 | **Done (`DOC-IMPL-013` section 4).** K2 MoVA with `-ot 'attn_v_exps=CPU'` plus `-ncmoe`, then the sweep and depth matrix as for the other large models | `DOC-IMPL-013` section 4.1: without it the model cannot load. Only 4 of the 64 value experts are used per token, so the CPU cost may be modest [E, untested]; it would also free about 4 GiB of VRAM for FFN experts | Flag only (ADR-004 section 4a) |
| 16 | Find the cause of the unexplained slow repetitions seen in phase 1 of the combined A/B (`DOC-IMPL-014` section 2.4): a short quiet-against-active test (the designer clicking around during a run), per-repetition output (`llama-bench -o jsonl`), and system-load logging in `bench_wrap.sh` | Would show whether desktop interaction or a background indexer disturbs CPU-bound runs, and make every later run easier to interpret | Helper change only (ADR-004 section 4a). **Not planned.** |
| 17 | Replicate the combined A/B with more phases (ABBAABBA) or hands-off switching (the profile can be set through the power-profile service, `ActiveProfile` is writable) | Would narrow the interval on a 2% effect for the large models | The designer would run the switching wrapper; **not planned.** |

## 6. Raw data

All in `$LLTH_HOME/benchmarks/`. Logs are in `speed/`, scripts in `scripts/speed/`, `scripts/quality/` and `scripts/models/`:
- `2026-10-23_k2-horizon-7b_ngl-sweep.log` (depth 0, `q8_0` cache, 4 GPU-layer settings)
- `2026-10-23_k2-horizon-7b_depth-sweep.log` and `..._kv-q4_0.log`
- `2026-10-23_k2-horizon-3.7b_depth-sweep.log` and `..._kv-q4_0.log`
- `2026-10-23_k2-horizon-7b_explore-round1.log` and `2026-10-23_k2-horizon-3.7b_explore-round1.log`
- `2026-10-23_k2-horizon-7b_explore-round2.log`
- `2026-10-23_profile-ab-test.log` (power-profile A/B test, `DOC-IMPL-014` section 1; script `profile-ab-test.sh`)
- `2026-10-24_k2-horizon-0.9b_depth-sweep.log` (model 6, `DOC-IMPL-012` section 4; script `depth_sweep_0p9b.sh`)
- `2026-10-24_gemma-4-26b-a4b_ncmoe-sweep.log` and `2026-10-24_gemma-4-26b-a4b_depth-matrix.log` (model 5, `DOC-IMPL-013` section 2)
- `2026-10-24_qwen3.6-35b-a3b_ncmoe-sweep.log` and `..._depth-matrix.log` (model 4, `DOC-IMPL-013` section 3)
- `2026-10-24_k2-horizon-mova-36b_ncmoe-sweep.log` (model 3, first attempt, `DOC-IMPL-013` section 4.1: no result, kept as evidence)
- `2026-10-24_k2-horizon-mova-36b_ncmoe-sweep_ot-attnv.log` and `..._depth-matrix_ot-attnv.log` (model 3 with the override, `DOC-IMPL-013` section 4)
- `2026-10-24_profile-ab-test_models3to6.log` (combined power-profile A/B, `DOC-IMPL-014` section 2; script `profile-ab-test-models3to6.sh`)
- `scripts/speed/bench_large_models.sh` v1.1 (models 5, 4 and 3) and `scripts/models/download-k2-horizon-0.9b.sh`
- `scripts/` (helper, sweep, quality-test and download scripts)
- `quality/effort-probes/` (reasoning-effort probes, `DOC-IMPL-015`: raw responses, `probe.log` per model, `effort_probe.py` as run)
- `swap-time/` (model swap time, `DOC-IMPL-016`: the watcher's event log, `swap_watch.py` as run)
