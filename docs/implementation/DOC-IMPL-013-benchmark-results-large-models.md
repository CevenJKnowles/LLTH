---
id: DOC-IMPL-013
title: Benchmark Results: Large Models
type: implementation
status: active
version: v1.0
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
  - benchmarks
  - large-models
  - moe
  - speed
relationships:
  related:
    - ADR-004
    - ADR-005
    - DOC-IMPL-006
    - DOC-IMPL-012
provenance:
  - human
---

# Benchmark Results: Large Models

Speed measurements for the three mixture-of-experts models: Gemma 4 26B-A4B, Qwen3.6-35B-A3B and K2 Horizon MoVA 36B-A4B, with the experts of some layers kept on the CPU (`-ncmoe`). Method, conditions and gate verdicts are in `DOC-IMPL-006`.

## 1. Model facts read from the GGUF headers (verified 2026-10-24)

| Model | Architecture | Blocks (layers) | Experts (used per token) | Context length |
|---|---|---|---|---|
| 5 Gemma 4 26B-A4B | `gemma4` | 30 | 128 (8) | 262,144 |
| 4 Qwen3.6-35B-A3B | `qwen35moe` | 40 | 256 (8) | 262,144 |
| 3 K2 Horizon MoVA 36B-A4B | `k2-horizon` | 48 (the first 3 are dense) | 100 (8), plus 64 value experts (4) | 524,288 |

`bench_large_models.sh` uses these layer counts: the sweep starts with the experts of all layers on the CPU and moves layers to the GPU in steps of 2 (at most 7 layers' worth), once per cache type, at depths 0 and 8K; the depth matrix then runs at the chosen values. Usage is in the script header.

## 2. Model 5: Gemma 4 26B-A4B (ncmoe sweep and depth matrix)

Script `bench_large_models.sh` (stage 1 `sweep`, stage 2 `depths 24`), run by the designer on 2026-10-24 (sweep log last written 20:44, depth matrix 21:02). Gemma 4 26B-A4B `q4_0` (Google's QAT file, 14.44 GB), 30 layers, 128 experts (8 used). All runs: `-p 512 -n 128 -r 3 -fa on -ngl 99 -ncmoe N`, default 6 threads, default memory mapping (no `--no-mmap`, no `--mlock`), performance power profile, Chrome closed, mains power, helper with safety stop (92 °C, 1,500 MiB: never triggered). Logs: `2026-10-24_gemma-4-26b-a4b_ncmoe-sweep.log` and `2026-10-24_gemma-4-26b-a4b_depth-matrix.log`. `-ncmoe N` keeps the experts of the first N layers on the CPU (30 = all of them).

### 2.1 The ncmoe sweep (generation tokens/s; peak VRAM in MiB in brackets)

| ncmoe | `q8_0`, depth 0 | `q8_0`, depth 8K | `q4_0`, depth 0 | `q4_0`, depth 8K |
|---|---|---|---|---|
| 30 (all experts on the CPU) | 20.3 (2,323) | 19.9 (2,517) | 20.2 (2,297) | 18.8 (2,399) |
| 28 | 21.1 (3,143) | 20.2 (3,347) | 20.7 (3,117) | 20.1 (3,229) |
| 26 | 23.1 (3,957) | 22.0 (4,161) | 22.9 (3,931) | 21.8 (4,043) |
| **24** | 24.7 (4,777) | **23.3 (4,981)** | 24.1 (4,751) | **23.3 (4,863)** |
| 22 | 26.9 (5,591) | **out of memory** | 26.5 (5,565) | 25.3 (5,677) |
| 20 | not tried (the `q8_0` sweep stopped at 22) | | out of memory at load | |

Failures (kept as evidence): `q8_0`, ncmoe 22, depth 8K: "out of memory" (exit 134, 5,743 MiB at the limit); `q4_0`, ncmoe 20, depth 0: "cudaMalloc failed: out of memory" (exit 1). The script stops a cache type's sweep at its first failure by design. Reading speed in the sweep rose from about 405 (ncmoe 30) to about 490 tokens/s (ncmoe 22).

**Stable minimum (ADR-004 section 4):** `q8_0`: ncmoe 24 (ncmoe 22 loads at depth 0 but fails at 8K). `q4_0`: ncmoe 22 at 8K, but with only 69 MiB of VRAM to spare, which is as fragile as the 7B's `-ub 64` setting (`DOC-IMPL-012` section 6), so it was not carried forward. Chosen for the depth matrix: **ncmoe 24 for both cache types** (765 MiB spare at 8K with `q8_0`, about 880 MiB with `q4_0`).

### 2.2 The depth matrix at ncmoe 24

| Depth | Cache | Reading | Generation | Peak VRAM (MiB) | Peak temp |
|---|---|---|---|---|---|
| 0 | `q8_0` | 468 ± 8 | **25.3 ± 1.5** | 4,777 | 56 °C |
| 8K | `q8_0` | 439 ± 2 | **23.6 ± 0.7** | 4,981 | 68 °C |
| 16K | `q8_0` | 414 ± 2 | **22.4 ± 0.4** | 5,065 | 77 °C |
| 32K | `q8_0` | 364 ± 2 | **20.1 ± 0.5** | 5,235 | 83 °C |
| 0 | `q4_0` | 468 ± 7 | 24.7 ± 1.3 | 4,751 | 66 °C |
| 8K | `q4_0` | 440 ± 7 | 23.3 ± 0.8 | 4,863 | 72 °C |
| 16K | `q4_0` | 412 ± 0.2 | 21.0 ± 1.9 | 4,909 | 77 °C |
| 32K | `q4_0` | 360 ± 3 | 19.0 ± 0.2 | 4,999 | 84 °C |

All eight runs exited with 0; the lowest available RAM was 22,862 MiB.

### 2.3 Reading

1. **Gate verdicts (ADR-004 section 6):** speed passes by a wide margin (at least 8 tokens/s at 8K required; 23.6 with `q8_0`, 23.3 with `q4_0`); stability passes (available RAM never below 22,862 MiB with memory mapping, so no swap is needed); thermals: the highest GPU temperature was 84 °C, below the 92 °C limit, and the generation figures are smooth across the matrix, so no throttling is indicated (the within-run speed drop was not computed separately).
2. **Moving experts to the GPU pays about 1 to 2 tokens/s per two layers** (20.3 at ncmoe 30 to 26.9 at 22, `q8_0`, depth 0) and costs about 800 MiB of VRAM per step of two layers. The limit is VRAM, not RAM.
3. **Gemma slows only by about 20% from depth 0 to 32K** (25.3 to 20.1 tokens/s) and its VRAM grows only about 460 MiB over 32K. The 3.7B loses about 75% over the same range. Most of Gemma's layers therefore appear to use a cheap attention [E, inferred from these numbers, not from the architecture documents].
4. **`q8_0` is the better cache for Gemma:** equal or slightly faster at every depth (for example 22.4 against 21.0 at 16K), and `q4_0` saves only 150 to 240 MiB. There is no speed or fit reason to use `q4_0` with this model.
5. **At 32K with `q8_0` there are 511 MiB spare,** so ncmoe 23 might fit [E, not tested]; see `DOC-IMPL-006` §5, idea 14.
6. **Noise:** depth 0 shows spreads of ± 1.3 to 1.5 tokens/s (about 5 to 6%), the usual CPU-bound variation; trends across the sweep are larger than that.
7. **The depth matrix took about 18 minutes** (script start to `DONE`), much less than the 1 to 2 hours estimated in the script header.

## 3. Model 4: Qwen3.6-35B-A3B (ncmoe sweep and depth matrix)

Same script, flags and conditions as section 2 (`bench_large_models.sh`, `-p 512 -n 128 -r 3 -fa on -ngl 99 -ncmoe N`, default threads and memory mapping, performance profile, Chrome closed, mains power, safety stop never triggered). Qwen3.6-35B-A3B `UD-IQ4_XS` (Unsloth, 17.73 GB), 40 layers, 256 experts (8 used). Run by the designer on 2026-10-24: sweep 21:06 to 21:32 (about 26 minutes), depth matrix 21:36 to 21:53 (about 17 minutes). Logs: `2026-10-24_qwen3.6-35b-a3b_ncmoe-sweep.log` and `2026-10-24_qwen3.6-35b-a3b_depth-matrix.log`.

### 3.1 The ncmoe sweep (generation tokens/s; peak VRAM in MiB in brackets)

| ncmoe | `q8_0`, depth 0 | `q8_0`, depth 8K | `q4_0`, depth 0 | `q4_0`, depth 8K |
|---|---|---|---|---|
| 40 (all experts on the CPU) | 16.5 (2,713) | 14.2 (2,847) | 16.4 (2,711) | 14.8 (2,803) |
| 38 | 17.1 (3,577) | 14.3 (3,685) | 16.9 (3,575) | 14.7 (3,641) |
| 36 | 17.6 (4,287) | 15.2 (4,397) | 17.1 (4,285) | 15.5 (4,353) |
| **34** | 18.7 (5,075) | **17.9 (5,181)** | 18.8 (5,073) | **17.3 (5,137)** |
| 32 | **failed** (5,743) | not run | **failed** (5,741) | not run |

Failure (kept as evidence): at ncmoe 32 both cache types aborted at depth 0 with exit 134 and "CUDA error: the resource allocation failed", with VRAM at 5,741 to 5,743 MiB, the whole card. **Stable minimum: ncmoe 34 for both cache types**; spare VRAM at 8K was 565 MiB (`q8_0`) and 609 MiB (`q4_0`). Chosen for the depth matrix: ncmoe 34 for both.

### 3.2 The depth matrix at ncmoe 34

| Depth | Cache | Reading | Generation | Peak VRAM (MiB) | Peak temp |
|---|---|---|---|---|---|
| 0 | `q8_0` | 395 ± 6 | **19.2 ± 1.5** | 5,075 | 57 °C |
| 8K | `q8_0` | 358 ± 4 | **18.2 ± 1.0** | 5,181 | 70 °C |
| 16K | `q8_0` | 339 ± 4 | **16.2 ± 1.0** | 5,265 | 77 °C |
| 32K | `q8_0` | 306 ± 1 | **13.7 ± 0.4** | 5,435 | 86 °C |
| 0 | `q4_0` | 393 ± 7 | 18.9 ± 1.5 | 5,073 | 67 °C |
| 8K | `q4_0` | 356 ± 3 | 17.5 ± 0.9 | 5,137 | 76 °C |
| 16K | `q4_0` | 339 ± 2 | 15.8 ± 0.4 | 5,183 | 79 °C |
| 32K | `q4_0` | 305 ± 1 | 13.6 ± 0.4 | 5,273 | 86 °C |

All eight runs exited with 0; the lowest available RAM was 22,994 MiB.

### 3.3 Reading

1. **Gate verdicts:** speed passes (at least 8 tokens/s at 8K required; 18.2 with `q8_0`, 17.5 with `q4_0`); stability passes (available RAM never below 22,994 MiB with memory mapping); thermals: the highest GPU temperature was 86 °C at 32K, below the 92 °C limit but the closest margin of the models so far, and the speeds are smooth across the matrix.
2. **Qwen is slower than Gemma at the same split** (six layers' experts on the GPU: 17.9 against 23.3 tokens/s at 8K), consistent with a larger model with more experts per layer. [E for the cause]
3. **The step from ncmoe 36 to 34 is the large one at 8K** (15.2 to 17.9 with `q8_0`); the earlier steps add less than 1 token/s each.
4. **The extrapolation held:** from the 8K point (5,181 MiB) about 5,500 MiB was expected at 32K; the measured peak was 5,435 MiB, leaving 311 MiB. No fallback to ncmoe 36 was needed.
5. **Slowdown from depth 0 to 32K is about 29%** (19.2 to 13.7), against about 20% for Gemma and about 75% for the 3.7B. VRAM grows about 0.011 MiB per cached token with `q8_0` [computed from these peaks].
6. **`q8_0` is equal or slightly faster than `q4_0` at every depth** (18.2 against 17.5 at 8K; 13.7 against 13.6 at 32K) and `q4_0` saves only about 160 MiB at 32K, so `q8_0` is the sensible cache for Qwen.

## 4. Model 3: K2 Horizon MoVA 36B-A4B

### 4.1 First attempt: the model does not load with `-ncmoe` alone

The sweep for model 3 (`bench_large_models.sh k2mova sweep`, 2026-10-24 22:01, log `2026-10-24_k2-horizon-mova-36b_ncmoe-sweep.log`) produced **no result**. The first point, ncmoe 48 (the feed-forward experts of all 48 layers on the CPU), failed to load with both cache types within 12 seconds:

```
ggml_backend_cuda_buffer_type_alloc_buffer: allocating 5723.26 MiB on device 0: cudaMalloc failed: out of memory
llama_model_load: error loading model: unable to allocate CUDA0 buffer
```

The failure was clean: available RAM stayed at 23,373 MiB or more and the script stopped each cache type's sweep as designed. 

**Cause (computed from the tensor list in the GGUF file, read-only, 2026-10-24).** `-ncmoe N` places the feed-forward expert tensors (`ffn_up_exps`, `ffn_down_exps`, `ffn_gate_exps`) of the first N layers on the CPU. K2 Horizon MoVA ("Mixture of Value Attention") also has **attention value experts**, `attn_v_exps`, which `-ncmoe` does not touch:

| Tensor group (all 48 layers) | Size |
|---|---|
| Feed-forward experts (the part `-ncmoe` moves) | 15,253 MiB |
| **`attn_v_exps` (value experts)** | **4,050 MiB** |
| All other tensors (attention, shared experts, output matrix, embeddings) | 2,017 MiB |

The value experts plus the other tensors, less the 344 MiB token embedding that stays on the CPU, come to 5,723 MiB, **exactly the buffer the load tried to allocate**. The card has 5,746 MiB in total, so nothing is left for the cache or working buffers.

**Fix (flag-level, ADR-004 section 4a):** add `-ot 'attn_v_exps=CPU'` so that the value experts stay on the CPU as well. The GPU would then hold about 1.7 GiB of weights plus cache, leaving room to move feed-forward experts to the GPU. The same sweep and depth matrix would follow, with the override recorded in every log name and label (`DOC-IMPL-006` §5, idea 15). Whether the CPU cost of the value experts is modest is not known [E]; the model uses 4 of 64 value experts per token.

**Script:** `bench_large_models.sh` v1.1 (2026-10-24) adds an optional `OT` variable that passes `-ot "$OT"` and shows it in every label; with `OT` unset the commands are identical to v1.0, which produced the Gemma and Qwen results (checked on a dry run with a stand-in program: same arguments, same order). One script serves all three models, so the protocol is the same for each; the override is the only configuration difference for K2 MoVA and is visible in each log's `cmd:` line and label. Run: `OT='attn_v_exps=CPU' LOGTAG=ot-attnv bash bench_large_models.sh k2mova sweep`.

**Status:** resolved: the override works (sections 4.2 to 4.5). Recorded as KI-022 in `DOC-IMPL-001`, resolved as KI-R13.

### 4.2 Run with the value-expert override

Script `bench_large_models.sh` v1.1 with `OT='attn_v_exps=CPU' LOGTAG=ot-attnv`; flags otherwise as in sections 2 and 3 (`-p 512 -n 128 -r 3 -fa on -ngl 99 -ncmoe N -ot attn_v_exps=CPU`, default threads and memory mapping, performance profile, Chrome closed, mains power, safety stop never triggered). K2 Horizon MoVA 36B-A4B Q4_K_M (22.37 GB), 48 layers, 100 experts (8 used) plus 64 value experts (4 used). Run by the designer on 2026-10-24: sweep 22:13 to 22:52 (about 39 minutes), depth matrix 23:03 to 23:24 (about 21 minutes). Logs: `2026-10-24_k2-horizon-mova-36b_ncmoe-sweep_ot-attnv.log` and `2026-10-24_k2-horizon-mova-36b_depth-matrix_ot-attnv.log`.

### 4.3 The ncmoe sweep (generation tokens/s; peak VRAM in MiB in brackets)

| ncmoe | `q8_0`, depth 0 | `q8_0`, depth 8K | `q4_0`, depth 0 | `q4_0`, depth 8K |
|---|---|---|---|---|
| 48 (all experts on the CPU) | 11.1 (2,481) | 9.7 (3,305) | 10.4 (2,457) | 9.2 (2,897) |
| 46 | 10.8 (3,211) | 9.5 (4,051) | 10.8 (3,187) | 9.0 (3,647) |
| 44 | 11.3 (3,939) | 10.8 (4,783) | 11.5 (3,915) | 10.7 (4,375) |
| 42 | 11.6 (4,667) | 11.0 (5,511) | 11.4 (4,643) | 10.6 (5,103) |
| 40 | 12.3 (5,349) | **failed** | 12.0 (5,325) | **failed** (5,743) |

Failures (kept as evidence), both at ncmoe 40 and depth 8K: with `q8_0` the context failed while reserving working buffers (`allocating 523.09 MiB on device 0: cudaMalloc failed: out of memory`, exit 1); with `q4_0` the run started and then died in the CUDA graph set-up (`CUDA error: out of memory ... cudaGraphInstantiate`, exit 134, 5,743 MiB). Both are the same VRAM limit reached at different points.

**Stable minimum at 8K:** ncmoe 42 for both caches, but with only 235 MiB (`q8_0`) and 643 MiB (`q4_0`) spare. Because this model's cache grows fast (section 4.5), ncmoe 46 was chosen for the depth matrix: it is the highest value at which both caches were expected to reach the deepest depth they can.

### 4.4 The depth matrix at ncmoe 46

| Depth | Cache | Reading | Generation | Peak VRAM (MiB) | Peak temp |
|---|---|---|---|---|---|
| 0 | `q8_0` | 258 ± 1 | **11.5 ± 0.6** | 3,211 | 55 °C |
| 8K | `q8_0` | 239 ± 12 | **9.9 ± 1.2** | 4,055 | 71 °C |
| 16K | `q8_0` | 181 ± 35 | **8.8 ± 0.2** | 4,879 | 82 °C |
| 32K | `q8_0` | no result | **failed** | n/a | n/a |
| 0 | `q4_0` | 259 ± 1 | 11.2 ± 0.9 | 3,187 | 66 °C |
| 8K | `q4_0` | 228 ± 22 | 9.9 ± 0.6 | 3,647 | 76 °C |
| 16K | `q4_0` | 213 ± 1 | 9.3 ± 0.2 | 4,087 | 83 °C |
| 32K | `q4_0` | 157 ± 11 | **6.6 ± 0.1** | 4,963 | **88 °C** |

The `q8_0` run at 32K failed with `allocating 3315.00 MiB on device 0: cudaMalloc failed: out of memory` (exit 1): the KV cache alone does not fit. The other seven runs exited with 0; the lowest available RAM was 21,648 MiB.

### 4.5 Reading

1. **Gate verdicts:** speed passes at 8K (at least 8 tokens/s required; 9.9 with either cache, a margin of about 24%); stability passes (available RAM never below 21,648 MiB); thermals: the 32K `q4_0` run reached 88 °C, the highest of all runs and 4 °C below the 92 °C limit. Its GPU clock maximum stayed at 1,890 MHz, so no throttling is indicated, but there is little margin.
2. **The KV cache of this model is the largest measured:** VRAM grows about 0.10 MiB per cached token with `q8_0` (844, 824 MiB per 8K step at ncmoe 46) and about 0.055 with `q4_0` (460, 440, 876 MiB per 8K, 8K, 16K), against 0.014 for Gemma, 0.011 for Qwen and 0.076 for the 3.7B [computed from the logged peaks]. The extrapolation made after the sweep held within about 2%: predicted 3,376 MiB for the `q8_0` cache at 32K, the failed allocation was 3,315 MiB; predicted 5,027 MiB peak for `q4_0` at 32K, measured 4,963.
3. **Consequence for the cache choice:** `q8_0` cannot reach 32K at any ncmoe with this model on this card (the cache alone is 3.3 GiB); `q4_0` is the only cache that does. At 16K `q4_0` is also faster (9.3 against 8.8 tokens/s). This is the first model where the cache type changes the speed. The quality cost of `q4_0` is not measured here and enters the blind test if K2 MoVA is carried forward with it (ADR-004 section 6).
4. **Slowdown from depth 0 to 32K is about 41%** (11.2 to 6.6 tokens/s with `q4_0`), against 29% for Qwen and 20% for Gemma. Prompt reading is the slowest of the large models (157 to 259 tokens/s).
5. **The cost of keeping the value experts on the CPU cannot be isolated:** without the override the model does not load, so there is no baseline. At ncmoe 48 it generates 11.1 tokens/s, against 16.5 (Qwen, ncmoe 40) and 20.3 (Gemma, ncmoe 30) in the same all-on-CPU state, but these are different models.
6. **Noise:** the wide intervals are in prompt reading at depth 8K and 16K (for example 181 ± 35, 204 ± 39, 190 ± 57); generation intervals are at most ± 1.3.
7. **The override is part of the configuration:** every launch of this model needs `-ot 'attn_v_exps=CPU'` (or the equivalent `--override-tensor` for `llama-server`), to be recorded in ADR-005.

## 5. The three large models compared

Best stable setting per model, `q8_0` cache unless stated; generation tokens/s (reading in brackets) from the depth matrices:

| Model | ncmoe (of layers) | Depth 0 | 8K | 16K | 32K | Slowdown 0 to 32K | Peak temp |
|---|---|---|---|---|---|---|---|
| 5 Gemma 4 26B-A4B | 24 of 30 | 25.3 (468) | 23.6 (439) | 22.4 (414) | 20.1 (364) | 20% | 83 °C |
| 4 Qwen3.6-35B-A3B | 34 of 40 | 19.2 (395) | 18.2 (358) | 16.2 (339) | 13.7 (306) | 29% | 86 °C |
| 3 K2 Horizon MoVA 36B-A4B, with `-ot attn_v_exps=CPU` | 46 of 48 | 11.5 (258) | 9.9 (239) | 8.8 (181) | `q4_0` only: 6.6 (157) | 41% (`q4_0`) | 88 °C |

All three pass the speed gate at 8K (at least 8 tokens/s), stability and, as far as these runs show, thermals. They differ in what they cost: Gemma is the fastest and holds its speed best; Qwen is in between; K2 MoVA is the slowest, has the largest cache and runs hottest, but is the model with the highest independent quality index (ADR-004 section 1) and is fully open. The blind quality test decides the heavy model (ADR-004 section 6); speed does not.

## Amendment record

| Version | Date | Summary |
|---------|------|---------|
| v1.0 | 2026-11-07 | Split out of `DOC-IMPL-006` (sections 11.3, 12 to 16). Measurements unchanged. |

