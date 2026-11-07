---
id: ADR-001
title: llama.cpp as the Local Inference Engine
type: adr
status: amended
version: v1.1
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
  - inference-engine
  - llama-cpp
  - cuda
provenance:
  - human
---

# ADR-001 — llama.cpp as the Local Inference Engine

## Status

Amended (v1.1)

---

## 1. Context

LLTH runs large language models locally on an Acer ConceptD 7 laptop: i7-9750H, RTX 2060 Mobile with 6 GB VRAM (Turing, sm_75), 32 GB DDR4, Manjaro Linux, CUDA 13.3.

### Decision drivers

- 6 GB VRAM makes MoE expert offload (`--n-cpu-moe`) the key technique for running 20–35B-total models.
- Full control over the settings that matter on small VRAM: `-ngl`, `-c`, KV-cache quantisation (`-ctk`/`-ctv`) and flash attention (`-fa`).
- Real measurements (`llama-bench`) instead of estimates.
- Newest model architectures supported first.
- The previous Ollama and LM Studio setup was split across versions (server 0.22.1 vs client 0.33.3) and Ollama was exposed on 0.0.0.0.
- The designer wants a clean setup they can understand end to end.

### Rationale

Generation speed is roughly memory bandwidth divided by the bytes read per token, so the engine must let the designer decide exactly what lives in VRAM and what in RAM. llama.cpp exposes that directly and is the upstream implementation of the GGUF format.

---

## 2. Decision

### §1 Engine

Use llama.cpp, built from source with CUDA for compute capability 7.5 (sm_75).

### §2 Interface

`llama-server` is the main interface: a web UI plus an OpenAI-compatible API at `http://localhost:8080/v1`. Python talks to it over HTTP. The `llama-cpp-python` wrapper is not used.

### §3 Location

Source in `$LLTH_HOME/llama.cpp/`, built into `$LLTH_HOME/llama.cpp/build/`.

---

## 3. Consequences

### Positive

- Full control of offload flags.
- New models are supported first.
- Real benchmarks with `llama-bench`.
- Open source (MIT).

### Negative

- No polished desktop app.
- Updates are manual (`git pull` plus a rebuild).
- Switching models needs a server restart (llama-swap could automate this later).
- More flags to learn.

### Implementation notes

- CUDA 13.3 needs `g++-15` as the host compiler, not the default gcc 16.
- The build configuration itself is a separate decision and gets its own ADR before it is run.

### Related

- ADR-002 — Native User-Space Install, No Docker, Localhost Only

---

## 4. Non-goals

- Model selection (decided later, separately).
- Fine-tuning.
- Serving other machines or users.

---

## 5. Options considered

### Option A — Ollama

Easiest to use, but limited control and a conservative GPU split on small VRAM. Rejected.

### Option B — LM Studio

Has a GUI, but is closed source and lags behind llama.cpp releases. Rejected.

### Option C — vLLM

Built for large datacenter GPUs; a poor fit for a 6 GB Turing card. Rejected.

### Option D — llama-cpp-python

Lags upstream and compiles during pip install, which the designer's rules forbid on the system Python. Rejected.

---

## 6. Amendment record

| Version | Date | Summary |
|---------|------|---------|
| v1.0 | 2026-10-23 | Initial |
| v1.1 | 2026-11-07 | Editorial revision for publication. |
