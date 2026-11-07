---
id: DOC-IMPL-017
title: Quality Test Protocol
type: implementation
status: active
version: v1.0
canonical: true
scope: llth
audience:
  - developer
  - maintainer
  - operator
created: "2026-10-30"
updated: "2026-11-07"
tags:
  - llth
  - benchmarks
  - quality-test
  - protocol
relationships:
  related:
    - ADR-004
    - ADR-005
    - DOC-IMPL-010
    - DOC-IMPL-012
    - DOC-IMPL-013
provenance:
  - human
---

# Quality Test Protocol

The protocol for the blind quality test and the steward test of ADR-004 §5 and §5a: the prompt set, the scripts, the run configurations, the order of work and the scoring procedure. ADR-004 §5b decides that these tests run under this protocol. A change to the protocol needs an amendment of ADR-004.

## 1. Prompt set (frozen)

`$LLTH_HOME/benchmarks/prompts.md` (`DOC-IMPL-008` v1.0, approved by the designer on 2026-10-30): 20 prompts, 15 core (W1 to W5 writing, P1 to P5 Python, R1 to R5 reasoning and planning) and 5 deceptive (D1 to D5). SHA-256 of the approved file as used for the runs (the header was edited on 2026-11-07; the prompts are unchanged, see `benchmarks/README.md`): `8d5e4fa32e0285a8dd7423f2f9d3314da5983dfaf7f908be17fb6a017f732e1f`. The designer's easy/hard labels are in `DOC-IMPL-009` section 3; P3, D4 and D5 are tagged *contested* (`DOC-IMPL-009` section 3a). A change to the prompt set needs a new version of `DOC-IMPL-008` and a re-run of the affected prompts; the runner records the file's SHA-256 with every run and refuses to run if it differs from the one given on its command line.

## 2. Scripts

Two scripts in `$LLTH_HOME/benchmarks/scripts/quality/`, Python 3 standard library only, run as `python3 -I <script>`; no package is installed:
- `quality_run.py` (the runner). It is a **client**: it sends requests to a `llama-server` that the designer has already started, on `127.0.0.1:8080` only. It does not start or stop servers (launchers are decided in ADR-005), executes no model output, and contacts nothing else. For each prompt it sends one chat request with streaming, and writes one JSON file recording: the request (messages, sampling values, seed, `max_tokens`, reasoning setting), the reasoning text and the final answer as separate fields, the server's `usage` and `timings`, the times of the request start, the first token, the first token of the final answer and the end, the finish reason, and GPU temperature and available RAM at the start, every 30 seconds and at the end. Reasoning tokens are taken from the server's report if it gives them separately, otherwise counted with the server's `/tokenize` endpoint; the method used is recorded. A request is aborted and marked so if the GPU reaches **92 °C**, available RAM falls below **1,500 MiB** (the ADR-004 §4a limits), or 90 minutes pass. The runner is resumable (an existing result file is never overwritten; a re-run gets a new suffix) and does no scoring.
- `quality_blind.py` (blinding and tally). `make` builds the scoring sheet; `reveal` merges the key, the scores and the measurements; `tally` prints the tables.
Paths are derived from the script's location (no hard-coded home directory). Results go to `$LLTH_HOME/benchmarks/quality/<model>_<config>/` with a `run-header.json` (exact server command, build 11839, prompt-file SHA-256, sampling values, machine state, power profile).

## 3. Run configurations

One model at a time, the server started by the designer with a command given in full from this table; mains power, `performance` profile, no browser open, GPU at or below 50 °C at the start (ADR-004 §3). Common flags: `--host 127.0.0.1 --port 8080 -np 1 -fa on -cram 0`. The context is **`-c 34816`** where the output budget is 32,768 tokens: the budget plus 2,048 tokens for the longest prompt, the chat template and a margin.

| # | Model | Flags after the common ones (besides `-m`) | Max output tokens | Evidence for the flags |
|---|---|---|---|---|
| 6 | K2 Horizon 0.9B Q8_0 | `-c 34816 -ngl 99 -ctk q8_0 -ctv q8_0` | 32,768 | `DOC-IMPL-012` section 4: all layers on the GPU, 41 tokens/s at 32K |
| 2 | K2 Horizon 3.7B Q5_K_M | `-c 34816 -ngl 99 -ctk q4_0 -ctv q4_0` | 32,768 | `DOC-IMPL-012` section 2: 14.2 tokens/s at 32K, `q4_0` only |
| 1 | K2 Horizon 7B Q4_K_M | `-c 16384 -ngl 99 -ub 64 -ctk q4_0 -ctv q4_0` | **15,000** | `DOC-IMPL-012` section 6: 18.6 tokens/s at 16K; 32K is out of reach (about 3 tokens/s) |
| 5 | Gemma 4 26B-A4B | `-c 34816 -ngl 99 -ncmoe 24 -ctk q8_0 -ctv q8_0` | 32,768 | `DOC-IMPL-013` section 2: 20.1 tokens/s at 32K |
| 4 | Qwen3.6-35B-A3B | `-c 34816 -ngl 99 -ncmoe 34 -ctk q8_0 -ctv q8_0` | 32,768 | `DOC-IMPL-013` section 3: 13.7 tokens/s at 32K |
| 3 | K2 Horizon MoVA 36B-A4B | `-c 34816 -ngl 99 -ncmoe 46 -ot attn_v_exps=CPU -ctk q4_0 -ctv q4_0` | 32,768 | `DOC-IMPL-013` sections 4 and 5: `q8_0` fails at 32K; 6.6 tokens/s with `q4_0` |

- **Untested depth.** The benchmarks stopped at 32,768 tokens of depth (plus 128 generated). A context of 34,816 is about 6% further. Before the pilot, each configuration is load-tested (start the server, send one short prompt, read VRAM, RAM and temperature) and the result recorded; a configuration that does not load is reduced by amendment, not silently.
- **Deviations from ADR-004 §5.** The 7B's output budget is 15,000 tokens, not the card's 32,768. The 3.7B and K2 MoVA are tested with the `q4_0` cache (as ADR-004 §6 requires when only `q4_0` reaches the depth), so the favourite "Option A" setting (3.7B, `q8_0`, 16K) is **not** what is scored. An optional extra configuration of the 3.7B at `-c 16384`, `q8_0`, 15,000 output tokens is permitted if the designer asks, so that the cache effect on answer quality can be seen. An answer that stops at the budget (finish reason `length`) is kept, marked "did not finish within budget" and scored as it stands (ADR-004 §5 already records "failed to finish").
- **Sampling** (recorded with each answer): K2 Horizon 7B, 3.7B and MoVA: temperature 1.0, top_p 0.95, `reasoning_effort` `high`. K2 Horizon 0.9B: temperature 0.6 and top_p 0.95 (its card's recommendation; `ADR-004` §1a), `high`. Gemma 4: temperature 1.0, top_p 0.95, top_k 64 (from the model card of the exact file). Qwen3.6: the values on its card, written into the run header, with the card's non-thinking values for the thinking-off run. The seed is fixed per prompt (1,000 plus the prompt's position, W1 = 1,001 to D5 = 1,020) so that a run can be repeated. One sample per prompt and configuration; the sampling variance this leaves is a stated limitation.
- **Reasoning controls.** The mechanism for `reasoning_effort` (a server flag or a per-request chat-template argument) and for switching Qwen's thinking off (`--reasoning off` or a template argument) is recorded in the run header.
- **Machine time (estimate [E], upper bound).** If every answer ran to its budget, using the measured generation speeds at depth (`DOC-IMPL-012` and `DOC-IMPL-013`, interpolated in 1/speed), one answer takes about 8 minutes (0.9B), 24 (3.7B), 10 (7B), 24 (Gemma), 34 (Qwen) and 63 (K2 MoVA); 20 prompts take about 2.7, 7.9, 3.2, 8.1, 11.2 and 20.9 hours, **54 hours in total** for the ADR-004 §5 pass alone. Real answers are expected to be well below the budget; the pilot measures the typical length. The Qwen thinking-off run and the ADR-004 §5a passes come on top.

## 4. Order of work

(a) A load test of each configuration when its server is first started (the server starts, one short prompt is sent, VRAM, RAM and temperature are read and recorded). (b) A pilot on the first model in the run order with two prompts (W1 and P2): checks logging, timing, the separation of reasoning and answer, the reasoning-control mechanism and the token count; the designer reviews it before the rest of that model's prompts run. (c) The ADR-004 §5 pass, one model at a time, **largest first**: K2 MoVA, Qwen (with the thinking-off run), Gemma, the 7B, the 3.7B, the 0.9B (the cost is that a pipeline fault in the first, slowest runs shows up late, which the pilot in (b) and the resumable runner limit), each model's 20 prompts complete before the next server start, with a cool-down to 50 °C between models. (d) The thinking-control tests (PD-014) **before** the ADR-004 §5a pass, because they decide each model's steward configuration. (e) The ADR-004 §5a pass. (f) Scoring and tally.

## 5. Steward pass details

The system prompt is fixed before the pilot: *"Answer directly if you can do so reliably in a few sentences or a short snippet. If the task needs long multi-step reasoning, reply with exactly the word ESCALATE and nothing else."* (accepted as written by the designer on 2026-10-30 and frozen; a change needs an amendment). **Routing rule, fixed in advance:** a prompt counts as *escalated* if the final answer, with surrounding whitespace, quotes and punctuation removed and compared without regard to case, is `ESCALATE`; as *answered* if it contains no `ESCALATE`; and as *mixed* if it contains `ESCALATE` together with other text. Mixed outcomes are reported separately and counted as escalations in the headline figure. Routing accuracy is reported over all 20 prompts with the designer's labels and again over the 17 uncontested prompts (`DOC-IMPL-009` section 3a); a conclusion that differs between the two is stated as such. The steward configurations per model (reasoning off where the model allows it, the default, and for the K2 family `reasoning_effort` `low` and `medium`) are recorded in the results document after the thinking-control tests.

## 6. Blind scoring

`quality_blind.py make` stores the answers under random labels (A to G per prompt, drawn with the standard library's `secrets` module and re-shuffled for each prompt; seven answers because Qwen has a thinking-off run), shows the designer the **final answer only** (not the reasoning), and writes the key to a separate file that nobody opens until the designer has scored every answer. The designer scores 1 to 5 for overall usefulness, runs the Python answers in their own environment (model output is not otherwise executed), and may mark an answer as looped. Blinding applies to the scorer: the raw logs are visible while the runs are monitored, and some models may be recognisable by style. The ADR-004 §5a easy-prompt answers are scored on a second sheet with its own labels. Scores are saved as a table in `$LLTH_HOME/benchmarks/quality/`.

## 7. Not authorised

A launcher or stop script; additional models or quantisations; rebuilding llama.cpp; `sudo` or system settings; executing model-generated code; any network connection other than `127.0.0.1:8080`; changes to the ADR-004 §6 gates. Flag-level exploration remains governed by ADR-004 §4a.

## 8. Exception (2026-11-05)

After the designer had scored all 140 answers and revealed the key, the designer had the round 1 Python answers run to check their correctness (first P4, then all of P1 to P4; P5 could not run, as Keras is not installed). The code ran unchanged with `python3 -I -B` in a temporary folder outside the project, read only the prompt data, and wrote no files in the project. The exception covered that check only; the rule above stands for all other work. The results, and the final score set the designer chose from them, are in `DOC-IMPL-010`.

## Amendment record

| Version | Date | Summary |
|---------|------|---------|
| v1.0 | 2026-11-07 | Moved from ADR-004 §5b. The run order change of 2026-10-30 and the exception of 2026-11-05 are recorded in the ADR-004 amendment record. |
