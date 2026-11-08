---
id: DOC-IMPL-010
title: Blind Quality Test, Round 1 Results
type: implementation
status: active
version: v1.4
canonical: true
scope: llth
audience:
  - developer
  - maintainer
  - operator
created: "2026-11-05"
updated: "2026-11-08"
tags:
  - llth
  - quality-test
  - results
  - blind-scoring
  - python-verification
  - steward-test
relationships:
  related:
    - ADR-004
    - DOC-IMPL-006
    - DOC-IMPL-007
    - DOC-IMPL-008
    - DOC-IMPL-009
provenance:
  - human
---

# Blind quality test, round 1: results

This document reports round 1 of the blind quality test of ADR-004 §5 and §5b: the 20 frozen prompts of `DOC-IMPL-008`, answered by the seven run configurations, and scored blind. Evidence labels: **verified** (run or checked on the reference machine), **computed** (from the saved data), **judged** (a score or a reading).

## 1. What was scored

| Item | Value |
|---|---|
| Prompts | 20: writing W1–W5, Python P1–P5, reasoning R1–R5, deceptive D1–D5 (`DOC-IMPL-008` v1.0) |
| Runs | K2 MoVA (`k2-mova_high`), Qwen3.6 with and without thinking (`qwen3p6_think`, `qwen3p6_nothink`), Gemma 4 (`gemma4_think`), K2 7B, 3.7B and 0.9B (`k2-7b_high`, `k2-3p7b_high`, `k2-0p9b_high`) |
| Answers | 140, one sample per cell. One answer has no final text (R3, K2 7B, truncated at its 15,000-token budget) |
| Blinding | Labels A–G shuffled per prompt, `quality_blind.py make`; the sealed key was opened only after every row was scored |
| Scale | 1–5 per answer, plus `looped` and notes |

## 2. The two score sets

Both are in `$LLTH_HOME/benchmarks/quality/scoring/`.

| File | Scored by | Role |
|---|---|---|
| `scores-quality-round1.csv` → `results-quality-round1.md` | The designer, blind, all 140 rows | The human judgement |
| `scores-quality-round1-final.csv` → `results-quality-round1-final.md` | The designer's scores for W, R and D; the 35 Python rows rescored after running the code (§4) | **The round 1 result.** Chosen by the designer on 2026-11-05. |

## 3. Round 1 result (computed from the final score set)

| Run | Mean | Writing | Python | Reasoning | Deceptive | Easy | Hard | Median time to answer |
|---|---|---|---|---|---|---|---|---|
| **k2-mova_high** | **3.75** | 3.00 | **4.60** | 3.60 | **3.80** | 3.60 | **3.90** | 264 s |
| qwen3p6_think | 3.45 | 3.00 | 4.00 | **3.80** | 3.00 | 3.60 | 3.30 | 329 s |
| gemma4_think | 3.30 | 2.60 | 4.20 | 3.00 | 3.40 | 3.30 | 3.30 | 138 s |
| k2-7b_high | 3.15 | 3.00 | 3.20 | 3.00 | 3.40 | 3.10 | 3.20 | 59 s |
| k2-3p7b_high | 3.10 | **3.60** | 3.00 | 3.20 | 2.60 | 3.10 | 3.10 | 33 s |
| qwen3p6_nothink | 2.70 | **3.60** | 3.80 | 2.20 | 1.20 | 3.00 | 2.40 | 30 s |
| k2-0p9b_high | 1.80 | 2.60 | 1.40 | 1.40 | 1.80 | 1.80 | 1.80 | 12 s |

**Precision:** one scorer and 20 prompts per run. One point on one prompt moves a run's mean by 0.05 and a category mean by 0.20, so differences under about 0.2 in the overall mean are not meaningful.

The designer's original scores, before the Python rescoring, gave the same first place (K2 MoVA 3.50) and the same last two (Qwen without thinking 2.55, 0.9B 2.20). Gemma 4 moved from fifth (3.05) to third, because its Python was correct on all five prompts.

## 4. Python verification (verified)

**The ADR-004 rule that no model output is executed was lifted by the designer for this check only** (2026-11-05: first the P4 answers, then all Python answers). The code ran unchanged with `python3 -I -B` in a temporary folder outside the project, on the system Python (pandas 2.3.3, scikit-learn 1.9.1, torch 2.14.0 on the CPU).
- **P1:** answer D carried no data frame, so the prompt's `df` was put in front of it.
- **P2:** the prompt's code was run once to obtain the exception, then each answer's fix line.
- **P5:** not run (no Keras on the machine); judged by reading.

✓ correct · ~ the code works but the answer states something false · ✗ wrong result or crash

| Run | P1 | P2 | P3 | P4 | P5 |
|---|---|---|---|---|---|
| k2-mova_high | ✓ | ✓ | ✓ | ✓ | ✓ |
| gemma4_think | ✓ | ✓ | ✓ | ✓ | ✓ |
| qwen3p6_think | ✓ | ✓ | ✓ | ~ accuracy from the logits one step before the end (still 1.0) | ~ invents `count_parameters()` |
| qwen3p6_nothink | ~ output shown as floats | ~ opens with a wrong exception, then corrects itself | ✓ | ✓ | ~ states 487 (it is 451) |
| k2-7b_high | ✗ totals 31 / 72 / 113 (month summed in) | ~ invented message ending | ~ invented "typical output" | ✓ | ✗ `from tensorflow import layers` fails |
| k2-3p7b_high | ✗ the same `reset_index` bug | ✗ wrong shape and values for the means | ~ muddled explanation | ✓ | ✗ `from tf.keras import ...` fails |
| k2-0p9b_high | ✗ `KeyError: 'city'` | ✗ wrong cause; its second fix fails | ~ shape (2,), explanation wrong | ✗ target shape mismatch in the loss | ✗ `categorical_crossentropy` on integer labels |

**Run results:**
- **P4:** six runs reached 337 parameters and a training accuracy of 1.0; the 0.9B stopped at the first loss with `ValueError: Target size (torch.Size([400])) must be the same as input size (torch.Size([400, 1]))`.
- **P3:** all seven gave the probabilities `[[0.285, 0.715]]`; the 7B's "typical output" `[[0.123, 0.877]]` was invented.

**Final Python score per answer (1–5):** correctness first, then elegance as defined by the designer (simple, clear and small). Elegance was judged by hand against these criteria: correct, then safe, then lean (nothing dead, the built-in option over extra steps, a deletion where a deletion suffices). Broken code is capped at 2.

| Run | P1 | P2 | P3 | P4 | P5 | Mean |
|---|---|---|---|---|---|---|
| k2-mova_high | 4 | 5 | 4 | 5 | 5 | 4.6 |
| gemma4_think | 4 | 5 | 4 | 4 | 4 | 4.2 |
| qwen3p6_think | 4 | 5 | 5 | 3 | 3 | 4.0 |
| qwen3p6_nothink | 5 | 3 | 4 | 5 | 2 | 3.8 |
| k2-7b_high | 2 | 4 | 4 | 5 | 1 | 3.2 |
| k2-3p7b_high | 2 | 4 | 4 | 4 | 1 | 3.0 |
| k2-0p9b_high | 1 | 1 | 3 | 1 | 1 | 1.4 |

## 5. Observations (judged)

1. **K2 MoVA leads on what LLTH weighs most:** Python (correct on all five), hard prompts and deceptive prompts. It is also fully open.
2. **Thinking adds about 0.75 to Qwen3.6,** almost all of it on reasoning (3.80 against 2.20) and deceptive prompts (3.00 against 1.20). Without thinking it writes better.
3. **Fluent, fast answers can be confidently wrong.** Qwen without thinking scored 1.20 on deceptive prompts, and the 3.7B 2.60.
4. **Two answers reported output they had not computed** (7B P3, 3.7B P1). Only running the code exposed them.

## 6. Limits

- One sample per cell, at fixed seeds; temperature 1.0 for most runs.
- One human scorer.
- Python P5 checked by reading only.
- Category means rest on five prompts each.
- The steward pass (§5a) and the routing measures have not been run, so this round says nothing about routing accuracy.

## 7. Steward pass (ADR-004 §5a), reduced scope (verified)

**Scope.** The designer decided on 2026-11-05 that the K2 3.7B is the steward. The steward pass was then run for the 3.7B only. Qwen3.6 and Gemma 4 were planned as comparisons but were not run, because the designer chose a design without automatic routing (§7.3). K2 MoVA, the 7B and the 0.9B were excluded by the designer.

**Settings.** The frozen system prompt of `DOC-IMPL-017` section 5; `reasoning_effort` low and medium, the K2 steward configurations; round 1 sampling (temperature 1.0, top_p 0.95) and seeds; a 32,768-token budget. The server ran with the round 1 command (`-c 34816 -ctk q4_0 -ctv q4_0`). Runs: `$LLTH_HOME/benchmarks/quality/k2-3p7b_steward-low/` and `k2-3p7b_steward-medium/`. Routing was tallied with `quality_blind.py` v1.2 (`routing`), which reads answers after the end-of-thinking marker (KI-R14).

### 7.1 Routing

| Run | Routed as labelled | Easy but escalated | Hard but answered |
|---|---|---|---|
| steward-low, all 20 | 9 (45%) | 3 (P2, R2, D2) | 8 |
| steward-low, the 17 uncontested | 8 (47%) | 3 | 6 |
| steward-medium, all 20 | 10 (50%) | 0 | 10 |
| steward-medium, the 17 uncontested | 10 (59%) | 0 | 7 |

**Reading.**
- **At medium effort, the 3.7B escalated nothing.** It tried to answer all 20 prompts, including the ten labelled hard.
- **At low effort, it escalated five prompts, and three of them were easy.** It escalated only two of the hard ones (R5, D5).
- **Half the prompts are labelled easy, so "always answer" scores 50%.** The 3.7B's own judgement of when to escalate therefore adds nothing to routing.

### 7.2 Cost and heat

- **Time at low effort:** most answers took 0.2 to 6 seconds; the longest were R1 (23.5 s) and R3 (22.3 s).
- **Time at medium effort:** 3.3 to 58.4 seconds per answer. Every answer came back inside the reasoning field, after the marker (KI-R14).
- **Heat:** the GPU climbed through the 20-prompt medium run to **89 °C**, the closest to the 92 °C limit so far. The runner checks the temperature only before a run, not between prompts (KI-023).

### 7.3 Consequence: the designer's direction (2026-11-05)

- **No model routes.** The user chooses a category with a button in the interface: for example, Write (the 3.7B at low effort), Code and Think (K2 MoVA at medium and high).
- **A web interface on FastAPI** starts the matching `llama-server` profile and streams the answer back. It is decided in ADR-006.
- **The easy-prompt blind sheet of §5a was not built.**
