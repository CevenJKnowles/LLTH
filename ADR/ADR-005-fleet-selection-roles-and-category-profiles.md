---
id: ADR-005
title: Fleet Selection, Roles and Category Profiles
type: adr
status: amended
version: v1.5
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
  - adr
  - model-selection
  - architecture
  - profiles
  - k2-horizon
subordinate_to: ADR-004
relationships:
  related:
    - ADR-001
    - ADR-002
    - ADR-004
    - DOC-IMPL-001
    - DOC-IMPL-006
    - DOC-IMPL-010
    - DOC-OVW-019
provenance:
  - human
---

# ADR-005 — Fleet Selection, Roles and Category Profiles

## Status

Amended (v1.5)

---

## 1. Context

ADR-004 tested six models on the reference machine: speed (`DOC-IMPL-012` to `DOC-IMPL-014`), a blind quality round of 20 prompts (`DOC-IMPL-010`), reasoning-effort probes (`DOC-IMPL-015`), a steward pass of reduced scope (`DOC-IMPL-010` §7) and the time to swap one model for another (`DOC-IMPL-016`). ADR-004 §6 leaves the final choice and the launch configuration to this ADR. This ADR records which models form the fleet, what each one is for, how the user chooses between them, and the exact server configurations. How the interface that applies these choices is built is decided separately, in ADR-006.

### Decision drivers

- **The designer's priorities** (ADR-004, decision drivers): independence and freedom to fine-tune first, then the best quality the machine can reach, then speed. Coding wins a tie.
- **Round 1 result (computed, final score set, `DOC-IMPL-010` §3):**

| Model | Mean | Writing | Python | Reasoning | Deceptive | Median time |
|---|---|---|---|---|---|---|
| K2 Horizon MoVA 36B-A4B | **3.75** | 3.00 | **4.60** | 3.60 | **3.80** | 264 s |
| Qwen3.6-35B-A3B, thinking | 3.45 | 3.00 | 4.00 | **3.80** | 3.00 | 329 s |
| Gemma 4 26B-A4B | 3.30 | 2.60 | 4.20 | 3.00 | 3.40 | 138 s |
| K2 Horizon 7B | 3.15 | 3.00 | 3.20 | 3.00 | 3.40 | 59 s |
| K2 Horizon 3.7B | 3.10 | **3.60** | 3.00 | 3.20 | 2.60 | 33 s |
| Qwen3.6-35B-A3B, no thinking | 2.70 | **3.60** | 3.80 | 2.20 | 1.20 | 30 s |
| K2 Horizon 0.9B | 1.80 | 2.60 | 1.40 | 1.40 | 1.80 | 12 s |

  One scorer and 20 prompts: differences under about 0.2 in the mean are noise.
- **Self-routing does not work (verified, `DOC-IMPL-010` §7.1).** With the frozen steward prompt of `DOC-IMPL-017` section 5, the 3.7B routed 45% of prompts as labelled at low effort and 50% at medium. Half the prompts are labelled easy, so always answering would also score 50%.
- **Reasoning effort changes the waiting time, not the speed (verified, `DOC-IMPL-015`).** The 3.7B at low effort answered the plain-language prompts correctly in 1 to 2 seconds and was confidently wrong on numbers and code (D1, D4, P1). K2 MoVA stayed accurate at low effort but took 8 to 98 seconds per answer.
- **Only one of the two chosen models fits in VRAM at a time (verified, `benchmarks/quality/load-tests.log`).** At the round 1 settings the 3.7B uses 4,815 MiB and K2 MoVA 4,709 MiB, against 5,746 MiB usable.
- **Swap time (verified, `DOC-IMPL-016`).** 3.7B to MoVA about 14 seconds (12.8 to 15.3, n = 3); MoVA to 3.7B about 6 seconds (5.4 to 6.0, n = 2). Effort is set per request, so moving between effort levels of one model needs no swap.
- **Interface requirements (`DOC-OVW-019`):** the user chooses an *expert* from a `/mode` menu in a terminal-style interface; the experts are Administration, Writing, Coding and Think; the list is extensible; the menu order and wording are decided later. This replaces the category buttons of the earlier direction below.

### Rationale

The quality round names the specialist clearly: K2 MoVA has the highest mean and the best Python and deceptive scores, and is correct on all five Python prompts when the code is run. It is also from the fully open K2 Horizon family (Apache-2.0, open data, code and checkpoints), which serves the first priority. The steward is the 3.7B: the designer's choice, supported by the best writing score of all models (3.60, shared), the shortest median time of the usable models, and the same open family. ADR-004 §6 names the everyday model as the best of models 1 and 2 on quality per time: the 3.7B gives 3.10 in 33 s against the 7B's 3.15 in 59 s.

A router was the original plan (PD-012). The steward pass shows that the 3.7B cannot judge when to hand over, and a front-end classifier would need a third model in a VRAM budget that already holds only one. A choice of expert moves that judgement to the user, who knows what they are asking, and costs nothing at run time.

---

## 2. Decision

### §1 The fleet

| Role | Model | File (ADR-004 §1, SHA-256 verified) | Licence |
|---|---|---|---|
| **Steward** (plain-language tasks: writing, admin, short replies) | K2 Horizon 3.7B Q5_K_M | `$LLTH_HOME/models/IFM/K2-Horizon-3.7B-GGUF/K2-Horizon-4B-Q5_K_M.gguf` (3,643,776,384 bytes, `944ec951…f14066`) | Apache-2.0 |
| **Specialist** (code, numbers and data, multi-step reasoning) | K2 Horizon MoVA 36B-A4B Q4_K_M | `$LLTH_HOME/models/IFM/K2-Horizon-MoVA-36B-A4B-GGUF/K2-Horizon-MoVA-36B-A4B-Q4_K_M.gguf` (22,368,011,616 bytes, `513dd785…f4cbd`) | Apache-2.0 |

Both models are from one fully open family. The licences were checked on 2026-10-27 and are re-checked at release.

### §2 Models outside the fleet

Qwen3.6-35B-A3B, Gemma 4 26B-A4B, K2 Horizon 7B and K2 Horizon 0.9B are not used by any expert. They stay on disk as reference models for research (PD-015) and for possible later roles.
- **Gemma 4** is the first candidate for an LLM judge in a future evaluator, as it was correct on all five Python prompts and is from another family. It is not part of this ADR.
- **Qwen3.6** scored second (3.45) but is slower than MoVA (329 s median) and is not fully open in data and recipe. With thinking off it fails the deceptive prompts (1.20).
- **The 7B** has no role between the 3.7B and MoVA, and runs at the VRAM ceiling (5,675 MiB) and up to 90 °C.
- **The 0.9B** scored 1.80, with 1.40 on both Python and reasoning, the lowest of the seven runs. It is not used by any expert; the fleet is the 3.7B and MoVA (§1).

### §3 Experts (the menu entries)

The user chooses an expert for each request, from a menu that the `/mode` command opens. An expert is a model plus a per-request `reasoning_effort`, with an optional instructions field (below). There is no automatic routing, and no model decides where a request goes. This ADR fixes the four experts below; the list is extensible, so experts are data and not code.

| Expert | Server (§4) | `reasoning_effort` | Intended for | Evidence |
|---|---|---|---|---|
| Writing | S1 (3.7B) | `low` | Writing, rewording, summaries, short replies | W1, W2, W4 correct in 1 to 2 s; wrong on D1, D4, P1 (`DOC-IMPL-015`) |
| Administration | S1 (3.7B) | `medium` | Dates, amounts, forms, structured admin text | At medium: D1 and P1 right, **D4 wrong** (a wrong fix), R2 right; W2 and W4 not read (§18). Thin evidence; 89 °C over 20 consecutive medium prompts (`DOC-IMPL-010` §7.2) |
| Coding | S2 (MoVA) | `medium` | Python, data, anything with numbers | Correct on all seven probe prompts and the most complete W4 (`DOC-IMPL-015`). Only P1 and D4 are code, one sample each; the round 1 Python score (4.60) was at high effort, and medium has no scored round. Thin evidence |
| Think | S2 (MoVA) | `high` | Hard reasoning, planning, prompts that look easier than they are | Round 1 configuration: Python 4.60, deceptive 3.80 (`DOC-IMPL-010`) |

- **Extensible.** Adding an expert means adding one small text file (name, server, effort, a one-line description, optional instructions); no code changes. Whether a user-added expert may use any model on disk, or only the fleet, is open. The menu order and wording are decided later.
- **Instructions are a provision only.** The optional field exists in case one is needed; it is empty by default, and no expert has instructions for now. If one is added, its effect on quality is unmeasured, because every score so far was produced without a system prompt.

- **Sampling for all four:** temperature 1.0, top_p 0.95, top_k and min_p at the server defaults (the round 1 values, `DOC-IMPL-017` section 3). No fixed seed in use; a seed may be set for reproducing an answer.
- **Output budget:** up to 32,768 tokens (the K2 card's recommendation, as in round 1).
- **No system prompt** in any expert for now. The round 1 answers and the probes were produced without one; the steward routing prompt of `DOC-IMPL-017` section 5 is not used.
- **Guidance, not enforcement.** Each menu entry carries a one-line description of what it is for (wording decided later). Nothing stops a user from asking the Writing expert for code.
- **Answer extraction.** The reply text is the content after the end-of-thinking marker `</ifm|think>` wherever it appears, in `content` or in `reasoning_content` (KI-026, handled as KI-R14 in `quality_blind.py`). At low effort on MoVA and medium on the 3.7B the answer arrives in the reasoning field.

### §4 Server configurations

Two configurations, exactly as scored in round 1 and as timed in `DOC-IMPL-016`. Common flags, required by KI-025 and ADR-002: `--host 127.0.0.1 --port 8080 -np 1 -fa on -cram 0`, with the context always set explicitly.

| Server | Command (one line) |
|---|---|
| S1, steward | `$LLTH_HOME/llama.cpp/build/bin/llama-server -m $LLTH_HOME/models/IFM/K2-Horizon-3.7B-GGUF/K2-Horizon-4B-Q5_K_M.gguf --host 127.0.0.1 --port 8080 -np 1 -fa on -cram 0 -c 34816 -ngl 99 -ctk q4_0 -ctv q4_0` |
| S2, specialist | `$LLTH_HOME/llama.cpp/build/bin/llama-server -m $LLTH_HOME/models/IFM/K2-Horizon-MoVA-36B-A4B-GGUF/K2-Horizon-MoVA-36B-A4B-Q4_K_M.gguf --host 127.0.0.1 --port 8080 -np 1 -fa on -cram 0 -c 34816 -ngl 99 -ncmoe 46 -ot attn_v_exps=CPU -ctk q4_0 -ctv q4_0` |

- **`-c 34816`:** the 32,768-token output budget plus 2,048 for the prompt, the template and a margin (`DOC-IMPL-017` section 3).
- **`q4_0` cache on both:** the only cache with which either model reaches 32K depth (`DOC-IMPL-012` §2 and `DOC-IMPL-013` §4). The early favourite "Option A" (3.7B, 16K, `q8_0`) was never scored and is not adopted (§5, Option F).
- **`-ot attn_v_exps=CPU`:** MoVA does not load without it (KI-R13).
- **One server at a time, on port 8080.** Choosing an expert on the other server means stopping the running one and starting the other (about 14 s to MoVA, 6 s back). How that is done, and the 92 °C safety stop, are part of ADR-006.
- **Thermals.** Long runs reached 86 °C (MoVA at high effort) and 89 to 91 °C (3.7B at medium and high, long prompts; KI-023). The 92 °C stop of ADR-004 §4a stays a requirement for anything that starts these servers.

### §5 Routing and the steward test (closes PD-012)

- **No automatic routing.** PD-012 (routing architecture) is closed by §3. A routing ADR is not needed unless automatic routing returns.
- **Reduced scope of ADR-004 §5a, recorded:** the steward pass ran for the 3.7B only, at low and medium effort (`DOC-IMPL-010` §7). The planned Qwen3.6 and Gemma 4 steward runs were not made, because they only matter for automatic routing. K2 MoVA, the 7B and the 0.9B were excluded by the designer. The easy-prompt blind sheet of §5a was not built.

---

## 3. Consequences

### Positive

- The fleet is two models from one fully open family.
- Each expert rests on measurements made in exactly its configuration: the round 1 scores, the effort probes and the swap time.
- No router means no extra model, no extra VRAM and no routing errors made by a model. The user's choice is visible and inspectable.
- Coding and Think share one server, so the most frequent switch for technical work costs no swap.

### Negative

- **A wrong choice gives a worse answer.** The Writing expert (low effort) is confidently wrong on numbers and code, and Administration (medium) is better but not reliable (D4 was wrong). The menu descriptions (§3) are the only mitigation.
- **The specialist is slow:** about 10 tokens per second, and a median 264 s per answer at high effort. Medium effort helps (the probe total fell from 971 s to 459 s), but MoVA answers are never instant.
- **Crossing between the 3.7B experts (Writing, Administration) and the MoVA experts (Coding, Think) costs 6 to 14 seconds** while the other server loads.
- **Thermal margin is small.** Long answers run at 86 to 91 °C, near the 92 °C stop.
- **MoVA cannot be fine-tuned on this machine** (PD-006); the 3.7B is the local fine-tuning candidate.
- **The evidence is thin in places:** one scorer, one sample per prompt, and the Coding (MoVA at medium) and Administration (3.7B at medium) experts rest on seven probe prompts, not on a full scored round.

### Implementation notes

- A scored round of the Coding and Administration experts (medium effort) on the frozen set would firm up their evidence. Optional, and possible under ADR-004 §4a.
- More experts can be added by amendment or as data (§3).

### Related

- ADR-001 — llama.cpp as the Local Inference Engine
- ADR-002 — Native User-Space Install, No Docker, Localhost Only
- ADR-004 — First-Round Model Selection and Benchmark Protocol (§5a, §5b, §6)
- ADR-006 — Interface, a Local Web Page with an Expert Menu
- `DOC-IMPL-015`, `DOC-IMPL-016`, `DOC-IMPL-010`, `DOC-IMPL-001` (KI-023, KI-025, KI-R13, KI-R14, PD-012, PD-014)

---

## 4. Non-goals

- How the interface is built: framework, endpoints, server manager and dependencies (ADR-006).
- Automatic routing or classification of requests.
- An evaluator or LLM judge.
- Fine-tuning (PD-006).
- Hardware tiers and profiles for other machines (PD-011, the installer ADR).
- Deleting models, or downloading new ones.
- Publication.

---

## 5. Options considered

### Option A — A steward that answers or escalates (the original plan)
Rejected on evidence: the 3.7B's self-routing was no better than always answering (45% and 50%, `DOC-IMPL-010` §7).

### Option B — The 0.9B as a front-end classifier (the designer's idea)
Set aside: it cannot share 5.7 GiB with either chosen model, its card advises high effort only, and its judgement scored lowest (1.80). The expert menu removes the need for it.

### Option C — One model, many dials (K2 MoVA alone, roles as effort levels)
Accurate, and no swap ever. Rejected for everyday use: MoVA's low-effort answers took 8 to 98 seconds where the 3.7B took 1 to 2 for the same plain-language prompts (`DOC-IMPL-015`).

### Option D — K2 3.7B and K2 MoVA with an expert menu (chosen)
Fast plain-language answers, the strongest specialist for technical work, one open family, and no routing model; costs are stated in §3.

### Option E — Qwen3.6 (thinking) or Gemma 4 as the specialist
Rejected: lower means than MoVA (3.45 and 3.30), and Qwen is slower. Neither is fully open in data and recipe. Gemma stays the evaluator candidate (§2).

### Option F — "Option A" settings for the steward (3.7B at `-c 16384`, `q8_0` cache)
Not adopted: faster at depth, but its quality was never scored, and §4 keeps the configuration that the evidence describes. It can be scored and adopted by amendment.

### Option G — A profile for the 3.7B at medium effort (adopted in v1.1 as Administration)
Deferred in v1.0 (right on D1 and P1 in the probe, still wrong on D4, only seven prompts of evidence). The designer adopted it on 2026-11-05 as the Administration expert, with Writing at low effort; the thin evidence is stated in §3.

### Option H — Two entries only: 3.7B low and MoVA high
Rejected: code would always wait for MoVA at high effort, the slowest setting, although medium was as accurate on the probe prompts.

---

## 6. Amendment record

| Version | Date | Summary |
|---------|------|---------|
| v1.4 | 2026-11-07 | Drafted and reviewed, accepted by the designer. Four acceptance checks were made first. |
| v1.5 | 2026-11-07 | Editorial revision for publication. |
