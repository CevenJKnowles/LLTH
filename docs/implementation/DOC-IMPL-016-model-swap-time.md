---
id: DOC-IMPL-016
title: Model Swap Time
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
  - swap-time
relationships:
  related:
    - ADR-005
    - ADR-006
    - DOC-IMPL-006
    - DOC-IMPL-015
provenance:
  - human
---

# Model Swap Time

Time to stop one `llama-server` and start the other between the K2 3.7B and K2 MoVA, 2026-11-05.

**Question.** The steward (K2 3.7B) and the specialist (K2 MoVA) cannot both stay loaded in 5.7 GiB of VRAM, so crossing between them means stopping one `llama-server` and starting the other. How long does that swap take? Only timing was added; no model, build or setting changed (ADR-004 §4a).

## 1. Method

- **Servers:** started and stopped by the designer by hand, with the round 1 commands. 3.7B: `$LLTH_HOME/llama.cpp/build/bin/llama-server -m $LLTH_HOME/models/IFM/K2-Horizon-3.7B-GGUF/K2-Horizon-4B-Q5_K_M.gguf --host 127.0.0.1 --port 8080 -np 1 -fa on -cram 0 -c 34816 -ngl 99 -ctk q4_0 -ctv q4_0`. K2 MoVA: the same with `-m $LLTH_HOME/models/IFM/K2-Horizon-MoVA-36B-A4B-GGUF/K2-Horizon-MoVA-36B-A4B-Q4_K_M.gguf` and `-ncmoe 46 -ot attn_v_exps=CPU`. A server was stopped with `Ctrl+C`.
- **Watcher:** `swap_watch.py` (Python standard library only; it starts and stops nothing) polled every 50 ms for `llama-server` processes in `/proc` and `GET /health` on `127.0.0.1:8080`, and logged each transition.
  - **Load time:** from the process start time in `/proc/<pid>/stat` (10 ms resolution) to the first `/health` 200.
  - **Stop time:** from the last `/health` 200 to the process disappearing. This is an upper bound that includes up to one polling interval before the `Ctrl+C`.
  - **Swap time:** the old server's stop time plus the new server's load time. The pause between the old server ending and the designer starting the next one (6 to 44 s) is logged as `human_gap_s` and excluded; an interface would start the next server at once.
  - **First reply:** once a server was ready, the watcher sent one `/completion` request (prompt `Hello`, `n_predict` 1, `cache_prompt` false) and timed it.
- **Order:** 3.7B, MoVA, MoVA, 3.7B, MoVA, 3.7B, MoVA (the second MoVA start followed the first directly, not planned; it is kept as a restart measurement).
- **Conditions:** power profile `performance`; GPU at 42 °C before the first start; VSCode open; whether a browser was open was not checked. Before the run about 21 GB of file data sat in the RAM page cache; the two model files together are 26.0 GB, so part of the files may have been read from the disk on each start. The cache was not cleared (that needs root) and its contents were not inspected.
- **Raw data:** `$LLTH_HOME/benchmarks/swap-time/` (`2026-11-05_k2-3p7b-mova_swap-time.jsonl`, `swap_watch.py` as run).

## 2. Results (verified)

| Swap | Stop of the old server | Load of the new server | Swap time |
|---|---|---|---|
| 3.7B → MoVA (1) | 0.11 s | 15.15 s | **15.3 s** |
| 3.7B → MoVA (2) | 0.16 s | 12.61 s | **12.8 s** |
| 3.7B → MoVA (3) | 0.17 s | 13.85 s | **14.0 s** |
| MoVA → 3.7B (1) | 1.31 s | 4.12 s | **5.4 s** |
| MoVA → 3.7B (2) | 1.30 s | 4.68 s | **6.0 s** |

Means (computed): 3.7B → MoVA **14.0 s** (n = 3), MoVA → 3.7B **5.7 s** (n = 2).

| Other loads | Load time |
|---|---|
| 3.7B, first start of the session (no server before it) | 1.87 s |
| MoVA restarted straight after itself (stop 1.25 s) | 11.01 s |

First reply after ready: 3.7B 0.018 s on all four starts; MoVA 0.51, 0.35, 1.07 and 0.32 s.

## 3. Reading

1. **Crossing from the steward to the specialist costs about 13 to 15 seconds; the way back about 5 to 6.** Both are short next to MoVA's own answer times (8 to 98 s at low effort, `DOC-IMPL-015` section 2), but a user who alternates often will notice the first. An interface should show that a model is loading rather than appear frozen.
2. **Switching between MoVA buttons needs no swap.** `reasoning_effort` is sent per request (`DOC-IMPL-015`), so the Coding (medium) and Think (high) experts can share one MoVA server. Only crossings between the 3.7B and MoVA cost a swap.
3. **The 3.7B loads about two and a half times slower after MoVA has run (4.1 to 4.7 s against 1.9 s).** A possible cause [E, not tested] is that MoVA's 22.4 GB file pushes the 3.7B's file out of the page cache, so it is read from the disk again. If so, the 3.7B's load time depends on what ran before it, not on the 3.7B.
4. **MoVA stops in about 1.3 s, the 3.7B in about 0.15 s.** The stop is a small part of every swap.
5. **Limits:** one session, three and two samples per direction, a page cache in an unknown state, and the round 1 server settings only; final profiles with another context size or cache type may load slightly differently. Not measured: VRAM release timing, swaps that involve Gemma or Qwen, and the load time with the page cache cleared.

## Amendment record

| Version | Date | Summary |
|---------|------|---------|
| v1.0 | 2026-11-07 | Split out of `DOC-IMPL-006` (section 19). Measurements unchanged. |

