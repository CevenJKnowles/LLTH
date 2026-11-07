---
id: DOC-IMPL-012
title: Benchmark Results: Small Models
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
  - small-models
  - speed
relationships:
  related:
    - ADR-004
    - DOC-IMPL-006
    - DOC-IMPL-013
provenance:
  - human
---

# Benchmark Results: Small Models

Speed measurements for the dense models K2 Horizon 7B, 3.7B and 0.9B, and the two exploration rounds on the 7B and 3.7B. Method, conditions and gate verdicts are in `DOC-IMPL-006`.

## 1. K2 Horizon 7B (Q4_K_M, 37 offloadable layers)

Generation speed (tokens/s), best settings in **bold**.

| Depth | Cache | GPU layers | Reading | Generation | Peak VRAM (MiB) | Peak GPU temp |
|---|---|---|---|---|---|---|
| 0 | q8_0 | **99 (all)** | 1,067.8 | **40.0** | 5,535 | 61 °C |
| 0 | q8_0 | 35 | 1,018.8 | 33.0 | 5,291 | 65 °C |
| 0 | q8_0 | 33 | 964.0 | 27.2 | 5,051 | 69 °C |
| 0 | q8_0 | 31 | 921.2 | 22.1 | 4,847 | 72 °C |
| 0 | q4_0 | **99 (all)** | 1,056.1 | **38.7** | 5,517 | 68 °C |
| 8K | q8_0 | 99 | did not load | | | |
| 8K | q8_0 | **34** | 733.4 | **14.8** | 5,739 | 67 °C |
| 8K | q8_0 | 32 | 692.0 | 9.6 | 5,483 | 72 °C |
| 8K | q8_0 | 30 | 654.0 | 7.3 | 5,229 | 77 °C |
| 8K | q4_0 | 99 | did not load | | | |
| 8K | q4_0 | **36** | 744.7 | **23.6** | 5,707 | 73 °C |
| 8K | q4_0 | 34 | 709.3 | 16.4 | 5,457 | 78 °C |
| 8K | q4_0 | 32 | 679.5 | 11.5 | 5,221 | 77 °C |
| 16K | q8_0 | 99 | did not load | | | |
| 16K | q8_0 | **30** | 514.6 | **3.8** | 5,723 | 77 °C |
| 16K | q8_0 | 28 | 495.0 | 3.1 | 5,451 | 79 °C |
| 16K | q8_0 | 26 | 482.2 | 2.5 | 5,167 | 80 °C |
| 16K | q4_0 | 34 | did not load | | | |
| 16K | q4_0 | **32** | 522.5 | **5.9** | 5,499 | 82 °C |
| 16K | q4_0 | 30 | 506.8 | 4.2 | 5,245 | 82 °C |
| 16K | q4_0 | 28 | 498.4 | 3.5 | 5,005 | 82 °C |
| 32K | q8_0 | 26 | did not load | | | |
| 32K | q8_0 | **24** | 317.8 | **1.3** | 5,659 | 84 °C |
| 32K | q8_0 | 22 | 306.9 | 1.1 | 5,319 | 89 °C |
| 32K | q8_0 | 20 | 297.1 | 1.0 | 4,965 | 87 °C |
| 32K | q8_0 | 18 | 300.5 | 0.9 | 4,609 | 86 °C |
| 32K | q4_0 | 30 | did not load | | | |
| 32K | q4_0 | **28** | 334.1 | **2.0** | 5,491 | 84 °C |
| 32K | q4_0 | 26 | 321.7 | 1.7 | 5,205 | 86 °C |
| 32K | q4_0 | 24 | 322.1 | 1.4 | 4,911 | 86 °C |

## 2. K2 Horizon 3.7B (Q5_K_M, all layers on the GPU unless stated)

| Depth | Cache | GPU layers | Reading | Generation | Peak VRAM (MiB) | Peak GPU temp |
|---|---|---|---|---|---|---|
| 0 | q8_0 | 99 | 1,686.8 | **56.1** | 3,789 | 75 °C |
| 0 | q4_0 | 99 | 1,666.4 | **55.1** | 3,771 | 77 °C |
| 8K | q8_0 | 99 | 1,031.3 | **33.9** | 4,409 | 76 °C |
| 8K | q4_0 | 99 | 1,025.1 | **34.6** | 4,103 | 78 °C |
| 16K | q8_0 | 99 | 726.2 | **23.4** | 5,029 | 78 °C |
| 16K | q4_0 | 99 | 715.2 | **23.9** | 4,435 | 80 °C |
| 32K | q8_0 | 99 | did not load | | | |
| 32K | q8_0 | 32 | 410.5 | 3.2 | 5,535 | 81 °C |
| 32K | q8_0 | 30 | 387.6 | 2.3 | 5,259 | 85 °C |
| 32K | q8_0 | 28 | 382.5 | 1.9 | 4,989 | 86 °C |
| 32K | q4_0 | 99 | 423.7 | **14.2** | 5,099 | 85 °C |

## 3. Why the 3.7B at 32K did not load with the q8_0 cache

The model has 36 layers, 8 key/value heads of dimension 128. At 32,768 tokens the `q8_0` cache is about 2.4 GiB and the weights are 3.4 GiB, together 5.8 GiB, more than the 5.6 GiB of VRAM before the 547 MiB working buffer is even allocated. The `q4_0` cache is about 1.2 GiB and fits (peak 5,099 MiB). The earlier recorded "peak 3,207 MiB" for that failed run is an artefact: the process died in under a second, between two one-second samples.

## 4. K2 Horizon 0.9B (Q8_0)

K2 Horizon 0.9B Q8_0, all 99 layers on the GPU, `-p 512 -n 128 -r 3 -fa on`, performance power profile, Chrome closed, mains power, helper with safety stop (never triggered; highest GPU temperature 69 °C, lowest available RAM 22,689 MiB). Script `depth_sweep_0p9b.sh`, log `2026-10-24_k2-horizon-0.9b_depth-sweep.log`. Reading and generation in tokens/s; all eight runs exited with 0.

| Depth | Cache | Reading | Generation | Peak VRAM (MiB) | Peak temp |
|---|---|---|---|---|---|
| 0 | `q8_0` | 5,862 ± 529 | **164.8 ± 1.3** | 1,337 | 51 °C |
| 8K | `q8_0` | 3,458 ± 86 | **100.2 ± 1.0** | 1,583 | 54 °C |
| 16K | `q8_0` | 2,356 ± 38 | **69.2 ± 0.1** | 1,829 | 57 °C |
| 32K | `q8_0` | 1,387 ± 21 | **41.4 ± 0.2** | 2,321 | 63 °C |
| 0 | `q4_0` | 6,063 ± 213 | 161.2 ± 1.2 | 1,329 | 61 °C |
| 8K | `q4_0` | 3,556 ± 378 | 100.7 ± 1.0 | 1,455 | 62 °C |
| 16K | `q4_0` | 2,275 ± 28 | 70.8 ± 0.3 | 1,597 | 64 °C |
| 32K | `q4_0` | 1,350 ± 15 | 42.8 ± 0.2 | 1,865 | 69 °C |

**Against the 3.7B (same cache, same depth, generation):** 164.8 against 56.1 at depth 0 (2.9 times), 100.2 against 33.9 at 8K (3.0), 69.2 against 23.4 at 16K (3.0), and 42.8 against 14.2 at 32K with the `q4_0` cache (3.0; the 3.7B could not load at 32K with `q8_0`). Prompt reading is about 3.4 to 3.5 times faster.

**Reading.**
1. **Gate 2 (speed) is passed by a wide margin:** about 100 tokens/s at 8K against the 20 required, with either cache. Stability and thermals also pass (ADR-004 section 6).
2. **The cache type makes no practical speed difference for this model:** `q4_0` is at most 3% faster at 32K and 2% slower at depth 0, well inside the spread. It saves about 460 MiB of VRAM at 32K, which is not needed here, so the more precise `q8_0` cache is the sensible choice for model 6 (the quality side is not measured by this test).
3. **Every layer fits on the GPU at every depth**, so there is no layer-split cliff as with the 7B. The VRAM growth is about 0.03 MiB per cached token with `q8_0` (738 MiB over the 24,576 tokens from 8K to 32K, the same in every depth step); extrapolating [E, not measured], a depth of 128K would peak near 5,270 MiB, inside the 5,746 MiB available but with under 500 MiB to spare (`DOC-IMPL-006` §5, idea 13).
4. **Generation slows with depth** (164.8 down to 41.4 tokens/s from 0 to 32K) because attention reads the whole cache for every token, as for the other models.
5. **Speed is only half the picture.** K2 Horizon always reasons; at 100 tokens/s a 3,000-token chain of thought takes about 30 seconds at 8K. Answer quality and the effect of `reasoning_effort` are not measured here (quality test, PD-014).
6. **Noise:** the one wide interval is prompt reading at depth 0 with the `q8_0` cache (± 529, about 9%); generation intervals are at most ± 1.3.
7. **The model loaded and ran in the pinned build 11839,** which the card says needs at least b11454 for the `k2-horizon` architecture; no flags beyond the standard ones were needed.

## 5. Exploration round 1 (ADR-004 section 4a)

Screening runs, 2 repetitions each, `q4_0` cache unless stated, governor name `powersave` (the performance power profile was active, see `DOC-IMPL-006` §2), Chrome open, helper with safety stop (peak GPU temperature 68 to 89 °C, nothing stopped). Logs: `2026-10-23_k2-horizon-7b_explore-round1.log` and `..._3.7b_explore-round1.log`. Script: `$LLTH_HOME/benchmarks/scripts/speed/explore-round1.sh`.

### 5.1 K2 Horizon 7B at 16K depth (generation tokens/s; reading in brackets)

| Experiment | GPU layers | Result | Peak VRAM (MiB) |
|---|---|---|---|
| E0 baseline (same session) | 32 | **6.9** (561) | 5,499 |
| E1 `-ub 256` | 32 | 6.6 (484) | 5,235 |
| E1 `-ub 256` | 34 | 9.2 (495) | 5,489 |
| E1 `-ub 256` | 36 | out of memory | |
| E2 `-ub 128` | 34 | 9.3 (381) | 5,359 |
| E2 `-ub 128` | **36** | **15.7** (407) | 5,635 |
| E3 `-nkvo 1` (cache in RAM) | 99 (all weights on the GPU) | 9.0 (505) | 5,477 |
| E4 threads 8 | 32 | 6.6 (506) | 5,499 |
| E4 threads 12 | 32 | 7.7 (508) | 5,499 |
| E5 output matrix on the CPU (`-ot`) | 99 | out of memory | |
| E6 output on the CPU + `-ub 256` | 99 | 12.4 (486) | 5,567 |
| E6 output on the CPU + `-ub 128` | 99 | 12.2 (380) | 5,441 |

### 5.2 K2 Horizon 3.7B at 32K depth

| Experiment | Cache | Result | Peak VRAM (MiB) |
|---|---|---|---|
| E0 baseline (all layers) | q4_0 | **14.2** (417); matches the earlier 14.2 | 5,099 |
| E1 `-ub 256` | q4_0 | 14.0 (395) | 4,833 |
| E3 `-nkvo 1` | q4_0 | 5.0 (336) | 3,741 |
| E3 `-nkvo 1` | q8_0 | 2.8 (310) | 3,739 |
| E5 output on the CPU | q8_0 | out of memory | |
| E5 output on the CPU | q4_0 | 11.7 (406) | 4,843 |

### 5.3 What the round shows

1. **A smaller working buffer is the winner for the 7B.** `-ub 128` at 36 GPU layers gives **15.7 tokens/s at 16K, 2.3 times the same-session baseline (6.9) and 2.7 times the earlier sweep's best (5.9)**. The mechanism: the working buffer shrinks, which frees about 400 MiB for two more layers. Quality was not measured. Prompt reading drops about 27% (407 against 561 tokens/s). `-ub 128` at 36 layers uses 5,635 of 5,746 MiB, leaving 111 MiB.
2. **Keeping every layer on the GPU matters most**, as in section 7: each layer moved to the CPU is expensive. The `-ub` setting is the cheapest way to make room.
3. **Cache in RAM (`-nkvo 1`) helps the 7B a little** (9.0 against 6.9 at 16K) **but hurts the 3.7B badly** (5.0 against 14.2 at 32K). It is not a general win; the cache must live on the GPU if it fits.
4. **Putting the output matrix on the CPU works** (12.2 to 12.4 tokens/s at 16K, nearly double the baseline) but is slower than `-ub 128` at 36 layers, and on the 3.7B it is slower than leaving it alone (11.7 against 14.2). It only helps when it frees room that is otherwise missing. Why the 36-layer setting (15.7) beats "all layers plus output on the CPU" (12.2) is unexplained; the two should be nearly the same. See `DOC-IMPL-006` §5, idea 4.
5. **More threads help slightly** (12 threads: 7.7 against 6.9, about +11%); 8 threads did nothing.
6. **Repeatability caveat.** The same baseline (7B, 16K, `q4_0`, 32 layers) gave 5.87 tokens/s in the earlier sweep (3 repetitions, GPU 82 °C) and 6.89 now (2 repetitions, GPU 68 °C): about 15% apart. Differences below roughly 15% in the CPU-bound regime are not conclusions. The 3.7B baseline (all on the GPU) reproduced almost exactly (14.23 and 14.20), so GPU-resident runs are far more repeatable.

## 6. Exploration round 2 (confirm and combine)

K2 Horizon 7B Q4_K_M, `q4_0` cache, 3 repetitions, **performance power profile** (CPU preference `performance`, turbo on), Chrome closed, helper with safety stop (nothing stopped; the highest GPU temperature was 89 °C, below the 92 °C limit). Run on 2026-10-23 23:49 to 2026-10-24 00:30. Log: `2026-10-23_k2-horizon-7b_explore-round2.log`; script: `explore-round2.sh`. Reading and generation in tokens/s.

| Depth | Setting | GPU layers | Reading | Generation | Peak VRAM (MiB) | Peak temp |
|---|---|---|---|---|---|---|
| 0 | baseline `-ub 512` | all | 1,065.5 | **39.7** | 5,517 | 62 °C |
| 0 | `-ub 128` | all | 977.2 | 39.1 | 5,123 | 65 °C |
| 8K | baseline `-ub 512` | 36 | 747.4 | 23.8 | 5,707 | 72 °C |
| 8K | **`-ub 128`** | **all** | 597.7 | **26.7** | 5,449 | 75 °C |
| 8K | `-ub 128` | 36 | 557.3 | 22.4 | 5,321 | 77 °C |
| 8K | `-ub 64` | all | 516.1 | 26.0 | 5,379 | 78 °C |
| 16K | baseline `-ub 512` | 32 | 527.0 | 6.2 | 5,499 | 79 °C |
| 16K | `-ub 128` | 36 | 409.4 | 15.2 | 5,635 | 83 °C |
| 16K | `-ub 128` | all | did not load (5,743 MiB at the limit) | | | |
| 16K | **`-ub 64`** | **all** | 365.0 | **18.6** | 5,711 | 86 °C |
| 16K | `-ub 64` | 36 | 345.3 | 15.0 | 5,593 | 85 °C |
| 16K | `-ub 128`, 12 threads | 36 | 401.0 | 15.8 | 5,635 | 87 °C |
| 32K | baseline `-ub 512` | 28 | 313.3 | 1.9 | 5,491 | 88 °C |
| 32K | `-ub 128` | 32 | 229.2 | **3.0** | 5,725 | 89 °C |
| 32K | `-ub 128` | 30 | 203.5 | 2.3 | 5,433 | 87 °C |
| 32K | `-ub 128` | 28 | 199.9 | 1.9 | 5,159 | 88 °C |
| 32K | `-ub 64` | 30 | 159.7 | 2.3 | 5,421 | 89 °C |
| 32K | `-ub 128`, 12 threads | 30 | 210.1 | **3.1** | 5,433 | 87 °C |

### 6.1 What round 2 shows

1. **A smaller working buffer is confirmed as the lever, and it works best when it lets *every* layer stay on the GPU.** At 16K, `-ub 64` with all layers gives **18.6 tokens/s, three times the 6.2 baseline** (round 1's best was 15.7 with 36 layers and `-ub 128`). At 8K, `-ub 128` with all layers gives 26.7, 12% above the best baseline (23.8).
2. **The cost is prompt reading:** about 20% slower at 8K with `-ub 128` and about 31% slower at 16K with `-ub 64`. `-ub` is fixed per server launch, so one configuration cannot have both the faster generation and the faster reading.
3. **The best 16K setting is fragile.** `-ub 64` with all layers uses 5,711 of 5,746 MiB: 35 MiB to spare. `-ub 128` with all layers does not load. A slightly different context or driver state could push it over. A deployed setting would need margin (for example 36 layers and `-ub 128`: 15.2 tokens/s, 111 MiB spare).
4. **Threads matter only when much work runs on the CPU:** 12 threads gave +4% at 16K (36 layers, noise level) but +35% at 32K (30 layers: 3.1 against 2.3). Use 12 for the CPU-heavy regime.
5. **32K stays out of reach for the 7B** (about 3 tokens/s at best). The 3.7B is the 32K model (14.2 tokens/s with the `q4_0` cache).
6. **GPU-resident runs reproduce well; CPU-bound runs vary.** Depth 0 baseline: 39.7 (earlier 38.7 and 40.0); 8K baseline at 36 layers: 23.8 (earlier 23.6). The 16K baseline at 32 layers: 6.2 (earlier 5.9 and 6.9). The unexplained difference between "36 layers" and "all layers plus output matrix on the CPU" from round 1 is not resolved.
7. **Thermals:** 86 to 89 °C at 16K and 32K; the helper's 92 °C limit never triggered. Sustained long-context runs run close to it.

### 6.2 What this means for the choices

- **The 7B is usable to 16K at about 15 to 19 tokens/s with a small buffer;** the 3.7B does 24 tokens/s at 16K with default settings and reads prompts twice as fast (715 against 365). **Option A (3.7B at 16K) stays ahead on speed and robustness;** the 7B is the candidate to test for quality (its independent index is 21 against 16) and for harder reasoning tasks where its slower speed is acceptable.
- **No ADR-004 gate changes are needed:** the 7B already passes the 8K gate (23.6 tokens/s with the `q4_0` cache).
- **Candidate launch settings** (from the evidence): 3.7B: all layers, `q8_0` cache up to 16K, `q4_0` at 32K; 7B: `q4_0` cache, `-ub 128`, 36 layers (safe) or `-ub 64` with all layers (fastest, fragile), 12 threads.

## 7. Reading

- **The 3.7B runs at 32K with the `q4_0` cache (14.2 tokens/s) and holds 23 tokens/s at 16K.**
- **The 7B generates 40 tokens/s at short context and is limited at depth.** With the `q4_0` cache it clears 8K (23.6 tokens/s); at 16K it drops to 5.9, at 32K to 2.0.
- **Every layer moved to the CPU costs the 7B roughly 3 to 4 tokens/s at 8K** (23.6, 16.4 and 11.5 tokens/s at 36, 34 and 32 layers).
- **Prompt reading holds up better than generation:** the 7B still reads 318 to 334 tokens/s at 32K depth.

## Amendment record

| Version | Date | Summary |
|---------|------|---------|
| v1.0 | 2026-11-07 | Split out of `DOC-IMPL-006` (sections 2, 5, 8, 9 and 11.2). Measurements unchanged. Correction carried over: the VRAM growth of model 6 is about 0.03 MiB per cached token (0.04 was a miscalculation). |

