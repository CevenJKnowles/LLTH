---
id: DOC-IMPL-015
title: Reasoning-Effort Probes
type: implementation
status: active
version: v1.0
canonical: true
scope: llth
audience:
  - developer
  - maintainer
  - operator
created: "2026-11-05"
updated: "2026-11-07"
tags:
  - llth
  - benchmarks
  - reasoning-effort
  - probes
relationships:
  related:
    - ADR-004
    - ADR-005
    - DOC-IMPL-006
    - DOC-IMPL-010
provenance:
  - human
---

# Reasoning-Effort Probes

Probes of `reasoning_effort` (low, medium, high) on the K2 3.7B and K2 MoVA, 2026-11-05 (PD-014).

**Question.** What does `reasoning_effort` change for a steward or specialist? In particular, does lower effort raise the generation speed, and what does it cost in answer quality? This is flag-level exploration under ADR-004 §4a; no new model, build or setting was introduced.

## 1. Method

- **Prompts:** seven from the frozen set (`DOC-IMPL-008`): three plain-language tasks of the kind a steward would answer (W1, W2, W4), two "looks hard, is easy" prompts (D1, D4), one pandas task (P1) and one reasoning task (R2).
- **Efforts and sampling:** `reasoning_effort` low, medium and high, sent per request to `llama-server` on `127.0.0.1:8080`. Round 1 sampling (temperature 1.0, top_p 0.95; server defaults for top_k and min_p) and round 1 seeds (1001 + position in the set); `max_tokens` 32,768; `cache_prompt` false; no system prompt.
- **Servers:** started by the designer with the round 1 commands. 3.7B: `-c 34816 -ngl 99 -ctk q4_0 -ctv q4_0`. K2 MoVA: `-c 34816 -ngl 99 -ncmoe 46 -ot attn_v_exps=CPU -ctk q4_0 -ctv q4_0`. Both with `-np 1 -fa on -cram 0`.
- **Conditions:**
  - Each request waited until the GPU was under 60 °C, and the probe would have stopped at 89 °C. Peaks were 80 °C (3.7B) and 72 °C (MoVA).
  - **A browser was open during the 3.7B probe,** a deviation from the benchmark conditions in ADR-004 §3. Speeds are comparable within the probe and close to the depth-sweep figures (`DOC-IMPL-012` section 2, `DOC-IMPL-013` section 4).
- **Measures:** reasoning and answer tokens are counted with the server's `/tokenize` endpoint. Speed is the server's `predicted_per_second`; time is the wall-clock time of the request. One sample per cell.
- **Reproducibility (verified):** at high effort both models reproduced their round 1 answers exactly. The token counts are identical, and for MoVA the answer text is identical too. The high column therefore carries the round 1 scores (`DOC-IMPL-010`).
- **Raw data:** `$LLTH_HOME/benchmarks/quality/effort-probes/` (`k2-3p7b/`, `k2-mova/`, each with 21 raw responses and `probe.log`, plus `effort_probe.py` as run).

## 2. Speed and waiting time (verified)

| Model | Effort | Generation speed (tokens/s) | Total time, 7 prompts | Without R2 |
|---|---|---|---|---|
| K2 3.7B | low | 50.9–59.6 | 68 s | 20 s |
| | medium | 53.3–60.3 | 87 s | 64 s |
| | high | 48.1–59.8 | 180 s | 146 s |
| K2 MoVA | low | 8.5–12.4 | 226 s | 128 s |
| | medium | 10.0–11.3 | 459 s | 314 s |
| | high | 9.4–11.0 | 971 s | 606 s |

**Reasoning effort does not change the generation speed; it changes the number of tokens generated.** The small differences follow the length of the output: speed falls as the context fills, so the longest outputs are the slowest (3.7B D4 at high, 3,729 tokens, 48.1 tokens/s). Low effort cut the 3.7B's waiting time by 63% (by 87% without R2), and MoVA's by 77%.

**Per prompt (reasoning tokens / answer tokens / seconds):**

| Prompt | 3.7B low | 3.7B medium | 3.7B high | MoVA low | MoVA medium | MoVA high |
|---|---|---|---|---|---|---|
| W1 | 0 / 37 / 1.0 | 121* / 2.1 | 156 / 51 / 3.5 | 42* / 12.0 | 109 / 42 / 15.7 | 228 / 38 / 26.2 |
| W2 | 0 / 103 / 1.8 | 741* / 12.8 | 453 / 77 / 9.3 | 207* / 20.5 | 620 / 100 / 70.5 | 2,857 / 66 / 297.4 |
| W4 | 0 / 69 / 1.5 | 878* / 15.8 | 1,541 / 66 / 30.5 | 0 / 62 / 7.6 | 312 / 65 / 38.1 | 375 / 68 / 44.7 |
| D1 | 0 / 69 / 1.6 | 346* / 6.4 | 499 / 68 / 10.4 | 0 / 74 / 8.3 | 285 / 65 / 35.0 | 964 / 25 / 99.8 |
| D4 | 0 / 457 / 8.6 | 904* / 17.0 | 3,559 / 168 / 77.8 | 96 / 296 / 39.8 | 321 / 506 / 83.2 | 176 / 334 / 51.4 |
| P1 | 0 / 267 / 5.2 | 525* / 9.8 | 433 / 324 / 14.2 | 13 / 376 / 39.7 | 229 / 425 / 71.6 | 345 / 443 / 86.7 |
| R2 | 0† / 2,419 / 47.9 | 1,230* / 23.4 | 1,573 / 220 / 34.7 | 884* / 98.2 | 1,021 / 413 / 144.5 | 3,468 / 110 / 364.6 |

\* The answer came back inside `reasoning_content`, after the marker `</ifm|think>`, with `content` empty; the count includes the answer (KI-026).
† The model wrote its working inside `content`, then the marker, then the answer.

## 3. Answer quality (judged, one sample per cell)

✓ correct · ~ correct with a loss · ✗ wrong. The high-effort answers are the round 1 answers; the round 1 final score is in brackets.

| Prompt | 3.7B low | 3.7B medium | 3.7B high | MoVA low | MoVA medium | MoVA high |
|---|---|---|---|---|---|---|
| W1 | ✓ | ✓ | (4) | ✓ | ✓ | (3) |
| W2 | ✓ all facts kept | not read | (4) | ~ softens the dashboard fact | ✓ | (2) |
| W4 | ~ drops matplotlib | not read | (3) | ~ drops "before importing" | ✓ complete | (3) |
| D1 | ✗ invented numbers | ✓ | (3) | ✓ | ✓ | (3) |
| D4 | ✗ says 6 | ✗ wrong fix (`observed=True`) | (4) | ✓ `dropna=False` | ✓ `dropna=False` | (4) |
| P1 | ✗ month 3 wrong | ✓ | (2) | ✓ | ✓ | (4) |
| R2 | ✓ | ✓ | (4) | ✓ | ✓ | (3) |

## 4. Reading

1. **The 3.7B at low effort fits plain-language tasks.** W1, W2 and W4 came back usable in 1 to 2 seconds. **It is unsafe on numbers and code:** D1, D4 and P1 were confidently wrong. At medium effort, D1 and P1 were right and D4 still wrong. A steward rule follows: plain language at low effort; anything with numbers, code or data at medium or higher, or routed to the specialist.
2. **K2 MoVA keeps its accuracy at low effort.** D1, D4, P1 and R2 were all correct; the losses were small omissions in the writing tasks. But at about 10 tokens per second, its low-effort answers took 8 to 98 seconds, against 1 to 48 seconds for the 3.7B at low and 3.5 to 78 seconds for the 3.7B at high. The "one model, many dials" design (MoVA alone, roles as effort levels) is therefore accurate but slow for everyday requests.
3. **More effort is not uniformly better.** The 3.7B's P1 was right at medium and wrong at high, and MoVA's medium W4 was its most complete. With one sample per cell these are anecdotes, but they show that effort should not be treated as a quality dial.
4. **The answer split fails in both directions (KI-026):** at medium on the 3.7B (7 of 7 prompts) and at low on MoVA (3 of 7). Any client must check both fields for `</ifm|think>` on every reply. Handled since `quality_blind.py` v1.2 (KI-R14).
5. **Not covered:** `--reasoning-budget`, the 0.9B, Qwen and Gemma with thinking off, the steward system prompt, the swap time between two models (measured since: `DOC-IMPL-016`), and repeated samples.

## Amendment record

| Version | Date | Summary |
|---------|------|---------|
| v1.0 | 2026-11-07 | Split out of `DOC-IMPL-006` (section 18). Measurements unchanged. |

