---
id: DOC-IMPL-014
title: Power-Profile Tests
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
  - power-profile
  - ab-test
relationships:
  related:
    - ADR-004
    - DOC-IMPL-006
    - DOC-IMPL-012
    - DOC-IMPL-013
provenance:
  - human
---

# Power-Profile Tests

Two balanced-against-performance tests (ABBA order): the dense models, and the large models with model 6. Method, conditions and gate verdicts for all benchmarks are in `DOC-IMPL-006`.

## 1. Dense models: 3.7B and 7B

**Question.** What is the performance power profile worth in tokens/s? (ADR-004 section 4a, `DOC-IMPL-006` §5 idea 5, PD-013.)

**Method.** Script `$LLTH_HOME/benchmarks/scripts/speed/profile-ab-test.sh`, run by the designer in four phases in ABBA order (performance 1, balanced 2, balanced 3, performance 4), switching the profile in the system settings between phases. The script refuses to run if the active profile differs from the one named, so a missed switch cannot enter the data. Each phase runs three tests with `llama-bench -p 512 -n 128 -r 3 -fa on -ctk q4_0 -ctv q4_0` through the safety helper, waiting for the GPU to cool to 55 °C or below before each test: **A** K2 Horizon 3.7B, depth 8K, all layers on the GPU; **B** K2 Horizon 7B, depth 16K, 36 layers, `-ub 128`; **C** K2 Horizon 7B, depth 32K, 30 layers, `-ub 128`. Date 2026-10-24, about 17:26 to 18:20, mains power, Chrome closed. The energy performance preference read `performance` in phases 1 and 4 and `balance_performance` in phases 2 and 3; turbo stayed on. Log: `2026-10-23_profile-ab-test.log` (the file name carries the date the script was written). All 12 runs ended with exit 0; the safety limits never triggered.

**Result** (generation in tokens/s; each value is the mean of 3 repetitions, the pair shows the two phases):

| Test | Performance (phases 1, 4) | Balanced (phases 2, 3) | Balanced against performance |
|---|---|---|---|
| A: 3.7B, 8K | 37.68 (37.81, 37.55) | 38.59 (38.40, 38.77) | +2.4% |
| B: 7B, 16K | 16.44 (16.49, 16.39) | 16.61 (16.54, 16.68) | +1.0% |
| C: 7B, 32K | 2.44 (2.41, 2.47) | 2.46 (2.46, 2.47) | +1.0% |

Prompt reading (tokens/s): A 1,097 against 1,116 (+1.7%), B 424 against 429 (+1.2%), C 228 against 228 (+0.3%).

**Reading.**
- **The performance profile does not make these benchmarks faster.** Balanced was equal or slightly ahead in all three tests. The direction is the same in every test, but the gaps are 1 to 2.4%, close to the run-to-run spread of the pairs, so the summary is "no meaningful difference", not "balanced is better".
- The ABBA order shows no sign of drift: phases 1 and 4 (both performance) agree within 0.7%.
- **Consequence:** all earlier benchmarks ran under the performance profile and remain valid; balanced would have given about the same speeds. The profile is not a precondition worth guarding for the large-model benchmarks.
- **Likely reasons** [E, not tested]: the GPU does most of the work and is not governed by the CPU profile; the balanced profile still keeps turbo on with the preference `balance_performance`; on mains power neither profile is short of power.
- **Power draw is not concluded.** The helper records one peak-watts sample per run, which is too coarse: test C drew 149 W in phase 1 but 94 W in phase 4 on the same profile.

**Limits.** Three configurations only; about 10 minutes per phase, so long-run heat effects are not covered; mains power only (no battery); balanced always sat in the middle of the order. **Unexplained:** test A under performance (37.7 tokens/s) is about 9% above the 34.6 of the earlier `q4_0` depth sweep with the same model, depth and cache type; the cause is not known (noise, starting temperature and a changed system state are candidates, none tested). Section 17 repeats the test over models 3 to 6 and qualifies the conclusion for the fast, GPU-only model.

## 2. Models 3 to 6

**Question.** Does the balanced power profile change speed for the CPU-heavy large models and for model 6, when the dense models of section 1 showed no meaningful difference? (PD-016.)

**Method.** Script `profile-ab-test-models3to6.sh` (written 2026-10-24, checked beforehand on a dry run with a stand-in program: same arguments as the matrices), run by the designer in four phases in ABBA order: performance 1, balanced 2, balanced 3, performance 4, switching the profile in the system settings between phases. The script refuses to run if the active profile differs from the one named, and also if a browser is open or less than 18,000 MiB of RAM is available. Each phase ran eight tests with `-p 512 -n 128 -r 3 -fa on -ngl 99`, default threads and memory mapping, at depths 8K and 32K, using the settings chosen in `DOC-IMPL-012` section 4 and `DOC-IMPL-013`:

| Model | Setting | Cache |
|---|---|---|
| 6 K2 Horizon 0.9B Q8_0 | all layers on the GPU | `q8_0` |
| 5 Gemma 4 26B-A4B | `-ncmoe 24` | `q8_0` |
| 4 Qwen3.6-35B-A3B | `-ncmoe 34` | `q8_0` |
| 3 K2 Horizon MoVA 36B-A4B | `-ncmoe 46 -ot attn_v_exps=CPU` | `q4_0` (so that 32K fits) |

**Conditions.** Mains power, Chrome closed. Phase times (2026-10-24 and 25): phase 1 23:35 to 23:55, phase 2 23:57 to 00:18, phase 3 00:21 to 00:42, phase 4 00:57 to 01:17; each phase took about 20 minutes. The CPU energy preference read `performance` in phases 1 and 4 and `balance_performance` in phases 2 and 3 (the profile service reported `performance` and `balanced` respectively). Log: `2026-10-24_profile-ab-test_models3to6.log`. All 32 runs exited with 0; the safety limit (92 °C, 1,500 MiB) never triggered. The highest GPU temperature per phase was 89, 88, 90 and 87 °C, always in the K2 MoVA test at 32K.

**Verification of the numbers.** The 32 generation and 32 reading values were extracted twice, with a block-wise parser and with an independent `awk` pass over the raw table rows; both agree exactly.

### 2.1 Generation speed (tokens/s)

| Test | Phase 1 (perf) | Phase 2 (bal) | Phase 3 (bal) | Phase 4 (perf) | Performance mean | Balanced mean | Balanced against performance | Spread between the two phases of a profile (1 vs 4 / 2 vs 3) |
|---|---|---|---|---|---|---|---|---|
| 6, 0.9B, 8K | 100.27 | 96.84 | 97.79 | 101.52 | 100.89 | 97.31 | **−3.5%** | 1.2% / 1.0% |
| 6, 0.9B, 32K | 41.45 | 39.66 | 40.11 | 42.14 | 41.80 | 39.88 | **−4.6%** | 1.7% / 1.1% |
| 5, Gemma, 8K | 23.18 | 22.15 | 23.14 | 23.74 | 23.46 | 22.64 | −3.5% | 2.4% / 4.5% |
| 5, Gemma, 32K | 19.73 | 19.13 | 19.50 | 19.28 | 19.51 | 19.31 | −1.0% | 2.3% / 1.9% |
| 4, Qwen, 8K | 16.88 | 16.52 | 16.69 | 17.35 | 17.12 | 16.61 | −3.0% | 2.8% / 1.0% |
| 4, Qwen, 32K | 12.90 | 12.81 | 13.69 | 13.76 | 13.33 | 13.25 | −0.6% | 6.7% / 6.9% |
| 3, K2 MoVA, 8K | 9.59 | 9.76 | 9.66 | 9.36 | 9.47 | 9.71 | +2.5% | 2.4% / 1.0% |
| 3, K2 MoVA, 32K | 6.45 | 6.17 | 6.45 | 6.72 | 6.58 | 6.31 | −4.2% | 4.2% / 4.5% |

Seven of the eight differences are negative; the mean of the eight is −2.2%.

### 2.2 Reading speed (tokens/s, with the interval of each run)

| Test | Phase 1 | Phase 2 | Phase 3 | Phase 4 |
|---|---|---|---|---|
| 6, 0.9B, 8K | 3,473 ± 76 | 3,360 ± 81 | 3,365 ± 71 | 3,480 ± 111 |
| 6, 0.9B, 32K | 1,393 ± 16 | 1,345 ± 17 | 1,354 ± 10 | 1,405 ± 9 |
| 5, Gemma, 8K | 443 ± 1 | 441 ± 1 | 441 ± 1 | 428 ± 6 |
| 5, Gemma, 32K | 359 ± 1 | 362 ± 1 | 360 ± 2 | 363 ± 1 |
| 4, Qwen, 8K | 352 ± 5 | 354 ± 4 | 350 ± 8 | 352 ± 3 |
| 4, Qwen, 32K | **195 ± 91** | 286 ± 28 | 305 ± 1 | 305 ± 1 |
| 3, K2 MoVA, 8K | 237 ± 3 | 240 ± 1 | 202 ± 53 | 201 ± 46 |
| 3, K2 MoVA, 32K | **126 ± 21** | 160 ± 2 | 159 ± 6 | 153 ± 9 |

### 2.3 Reading

1. **The profile does not make these benchmarks meaningfully faster or slower, with one exception.** Balanced is slower in seven of eight generation tests, by 0.6% to 4.6%, and faster in one (+2.5%).
2. **Model 6 is the one result clearly beyond the spread within a profile.** It is entirely on the GPU, it is the most repeatable test, and balanced is 3.5% (8K) and 4.6% (32K) slower, against 1.0% to 1.7% between the two phases of a profile; its reading speed shows the same (about 3.3% to 3.5% slower in both depths). A possible reason [E, untested] is that at 100 tokens/s the CPU that feeds the GPU becomes part of the bottleneck, so the CPU power setting matters. The 3.7B in section 1, GPU-only at about 38 tokens/s, showed the opposite sign (+2.4% for balanced), so the size of any effect depends on how fast the model runs.
3. **For the three large models the differences (−4.2% to +2.5%) lie inside the spread between phases of the same profile** (up to 6.9% for Qwen at 32K), so the data cannot tell a profile effect from phase-to-phase variation.
4. **Consequence:** `performance` stays the benchmark condition and no ADR changes. It is never meaningfully worse, and it is worth about 4% for the fast 0.9B. All earlier results remain valid.

### 2.4 Unexplained slow repetitions in phase 1

The two bold reading values in 2.2 (Qwen 32K, 195 ± 91; K2 MoVA 32K, 126 ± 21) are far below the same tests in phases 2 to 4, and their wide intervals mean one of the three repetitions inside the run was much slower than the others. The K2 MoVA 8K reading speed also stepped down between phases 2 and 3 (240 to 202, ± 53 and ± 46) and stayed there in phase 4. **The cause is not established.**
- What the log excludes: memory (available RAM at the start was 24,050 to 24,220 MiB in these runs), heat (GPU start temperature 55 °C and similar peak temperatures), the CPU clock at the start, errors (all exits 0), and the profile (phases 1 and 4 are both `performance`).
- Candidates, none tested: an interruption from the designer working at the machine (the journal shows System Settings opened at 23:54:43, during the last 14 seconds of the K2 MoVA 32K run, after its reading measurement; the Qwen window has no logged desktop event, which does not exclude interaction); the KDE file indexer `baloo_file_extractor`, which started roughly once a minute through all phases and so cannot explain phase 1 alone.
- The machine does not expose input idle time (`GetSessionIdleTime` is not supported), and `llama-bench` was run with the table output, which reports only the mean and spread of the three repetitions.
- The generation speeds of the same runs look normal (6.45 ± 0.25 for K2 MoVA 32K).
- The test was not repeated: the designer judged a rerun not worth the time, since the decision (keep `performance`) does not depend on it. Ideas 16 and 17 record how it could be settled.

### 2.5 Limits

One ABBA sequence of four phases; balanced always sat in the middle of the order; per-test intervals are wide for the CPU-bound models; the effect for the large models is of the same size as the noise. The test says nothing about battery use, runs much longer than about 20 minutes per phase, or models and settings other than those in the table.

## Amendment record

| Version | Date | Summary |
|---------|------|---------|
| v1.0 | 2026-11-07 | Split out of `DOC-IMPL-006` (sections 10 and 17). Measurements unchanged. |

