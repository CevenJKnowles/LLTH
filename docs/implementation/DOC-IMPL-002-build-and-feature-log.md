---
id: DOC-IMPL-002
title: Build and Feature Log
type: implementation
status: active
version: v1.7
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
  - build
  - features
  - log
relationships:
  related:
    - ADR-001
    - ADR-003
    - DOC-IMPL-001
    - DOC-ARCH-001
provenance:
  - human
---

# Build and Feature Log

## Purpose

A chronological record of every build of llama.cpp for LLTH (what was built, how, how long it took, what happened) and a list of the features the current build provides, with their verification status. Entries are appended; old entries are never rewritten. Decisions live in the ADRs; this log records what happened.

---

## Current build

| Item | Value |
|---|---|
| Build number / commit | 11839 / `e1e3b2c40` ("ui : bump packages to clear npm audit (#31038)") |
| Version string | `0.7.0-dev` (ggml 0.27.0) |
| Source | `$LLTH_HOME/llama.cpp/` (full history, 11,839 commits) |
| Build directory | `$LLTH_HOME/llama.cpp/build/` (266 MB) |
| Binaries | `$LLTH_HOME/llama.cpp/build/bin/` |
| Compiler | GNU 15.3.0 (C, C++, CUDA host); NVIDIA CUDA compiler 13.3.73 |
| GPU target | compute capability 7.5 (RTX 2060 Mobile) |
| Web UI | prebuilt archive `b11838` from `ggml-org/llama-ui`, SHA-256 `8714ff36c3252df0…` |
| Governing ADR | ADR-003 |
| Last rebuilt | 2026-10-27 (build 3, same source and flags) |

---

## Build history

### Build 1 — 2026-10-23, full build

| Item | Detail |
|---|---|
| Trigger | First build, after ADR-003 was accepted |
| Preparation | `git fetch --unshallow` (pack 392 MiB, 11,839 commits); source left at `e1e3b2c40`, one commit behind upstream |
| Configure | Ninja, Release, gcc-15/g++-15, `GGML_CUDA=ON`, `CMAKE_CUDA_ARCHITECTURES=75`, `GGML_CUDA_NCCL=OFF`, tests and examples OFF. Configured at 17:46 in 4.5 s |
| Compile | `cmake --build ... -j 8`, run in the background. 433 steps, started 17:48:11, finished 18:03:13 (about 15 minutes) |
| Result | Success, exit code 0 |
| Warnings | No compiler warnings. The only `warning` matches in the log are the file names of four deprecation stubs (KI-007). Configure warned that ccache is missing (KI-001) |
| Web UI | Download of `b11839` failed (no such archive), so the build fell back to `latest`, verified its checksum, and embedded 70 assets (KI-R02) |
| Verification | `llama-server --version` → `0.7.0-dev (build 11839, commit e1e3b2c40)`; `llama-cli --list-devices` → `CUDA0: NVIDIA GeForce RTX 2060 (5746 MiB, 5583 MiB free)` |
| Outputs | 22 executables and 29 shared libraries in `build/bin/` |
| Disk | Build directory 266 MB; `.git` 395 MB; whole `llama.cpp` folder 840 MB |

### Build 2 — 2026-10-23, incremental with UI pin

| Item | Detail |
|---|---|
| Trigger | Fix for the web UI fallback (ADR-003 v1.2) |
| Change | Reconfigured and rebuilt with `HF_UI_VERSION=b11838` |
| Compile | Incremental, 38 steps (relinks only); not timed |
| Result | Success. The UI stamp names the bucket `ggml-org/llama-ui` and version `b11838`; the archive checksum is unchanged (`8714ff36…`), proving the pinned archive equals the one fetched earlier as `latest` |
| Verification | Version string and device listing unchanged |

### Build 3 — 2026-10-27, clean rebuild at the project's final path

| Item | Detail |
|---|---|
| Trigger | The project folder moved to its final location, `$LLTH_HOME/`. The binaries carry an absolute `RUNPATH` and the CMake cache holds absolute paths, so the previous build could no longer find its shared libraries or be rebuilt incrementally |
| Preparation | The previous build directory was replaced. Its `RUNPATH` pointed at a location that no longer existed, so it could not be used |
| Configure and compile | The recipe below, unchanged from build 2, in a fresh `build/`. Run by the designer. 433 steps; wall-clock time not measured |
| Result | Success. Source commit `e1e3b2c40` unchanged |
| Web UI | `HF_UI_VERSION=b11838` downloaded, verified and extracted; 70 assets embedded |
| Verification | `llama-server --version` → `0.7.0-dev (build 11839, commit e1e3b2c40)`; `llama-cli --list-devices` → `CUDA0: NVIDIA GeForce RTX 2060 (5746 MiB, 5584 MiB free)`. Checked read-only afterwards: `RUNPATH` is `$LLTH_HOME/llama.cpp/build/bin`, `ldd` reports no missing libraries, `CMakeCache.txt` points at the new paths, and the six tools (`llama-server`, `llama-cli`, `llama-bench`, `llama-quantize`, `llama-gguf-split`, `llama-perplexity`) are present |

---

## Rebuild recipe (current)

```bash
HF_UI_VERSION=b11838 cmake -S $LLTH_HOME/llama.cpp -B $LLTH_HOME/llama.cpp/build -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=/usr/bin/gcc-15 -DCMAKE_CXX_COMPILER=/usr/bin/g++-15 \
  -DCMAKE_CUDA_HOST_COMPILER=/usr/bin/g++-15 -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=75 \
  -DGGML_CUDA_NCCL=OFF -DLLAMA_BUILD_TESTS=OFF -DLLAMA_BUILD_EXAMPLES=OFF
HF_UI_VERSION=b11838 cmake --build $LLTH_HOME/llama.cpp/build --config Release -j 8
```

If the source commit changes, choose a new `HF_UI_VERSION` first (ADR-003 §8) and record the change in this log and in an ADR amendment.

---

## Feature log

### Provided by the current build

| Feature | Status | Verified |
|---|---|---|
| CUDA backend for compute capability 7.5 | Built | Device listing shows the RTX 2060 |
| CPU backend tuned for this CPU (`-march=native`, AVX2/FMA) | Built | Not benchmarked |
| FlashAttention CUDA kernels (`f16-f16`, `q4_0-q4_0`, `q8_0-q8_0`, `bf16-bf16`) | Built | Used in every benchmark run, with the `q8_0` and `q4_0` caches (DOC-IMPL-006) |
| CUDA graphs | On (default) | Not tested |
| HTTPS support through OpenSSL 3.6.4 (for `-hf` downloads) | Built | Not tested |
| `llama-server`: OpenAI-compatible API and embedded web UI (b11838) | Built | Started by hand with four models (2026-10-25, informal and not measured; see the runtime verification section) |
| `llama-cli`: command-line chat and completion | Built | Device listing only |
| `llama-bench`: speed measurement | Built | **Run**: K2 Horizon 7B and 3.7B, depths 0 to 32K (DOC-IMPL-006) |
| `llama-quantize`: convert model precision | Built | Not run |
| `llama-gguf-split`, `llama-imatrix`, `llama-perplexity`, `llama-export-lora`, `llama-cvector-generator`, `llama-tokenize`, `llama-tts`, `llama-fit-params`, `llama-batched-bench`, `llama-completion`, `llama-results` | Built | Not run |
| `llama-mtmd-cli`, `llama-mtmd-debug`: multimodal (image) input | Built | Not run |
| `llama`: unified binary (from `app/`) | Built | Not evaluated |

### Deliberately not provided

| Feature | Why |
|---|---|
| NCCL (multi-GPU) | Single GPU (ADR-003 §5) |
| Other GPU backends (Vulkan, HIP, Metal, SYCL, etc.) | Not this hardware (ADR-003 non-goals) |
| Mixed K/V cache types in flash attention | Smaller, faster build (KI-004) |
| Test suites and examples | Build time (ADR-003 §5) |
| Locally built web UI | Supply-chain exposure (ADR-003 option C) |
| Portable binaries | Tuned for this machine (ADR-003 option E) |

---

## Runtime verification (2026-10-23, after the build)

- The K2 Horizon dense architecture loads and runs on the GPU in this build (`k2-horizon`; commit `462524043`). 7B Q4_K_M and 3.7B Q5_K_M were benchmarked with all layers on the GPU at short context.
- CUDA offload works in whole-layer steps (`-ngl`); the model, cache and working buffers must fit in 5,746 MiB, otherwise the load fails cleanly with a `cudaMalloc` out-of-memory message.
- Both compiled cache combinations work with flash attention: `q8_0`/`q8_0` and `q4_0`/`q4_0`.
- Model 6 (K2 Horizon 0.9B Q8_0) also loads and runs in this build with all layers on the GPU at depths up to 32K (DOC-IMPL-012 section 4, 2026-10-24).
- Expert offload works in this build: `-ncmoe` (`--n-cpu-moe`) with Gemma 4, Qwen3.6 and K2 Horizon MoVA under `llama-bench`; K2 MoVA additionally needs `-ot 'attn_v_exps=CPU'` because its attention value experts are not covered by `-ncmoe` (DOC-IMPL-013 section 4.1). CUDA out-of-memory ends a run cleanly with exit 1 or 134; no system harm was seen.
- Not yet exercised: `--reasoning-budget` and the other thinking flags (`reasoning_effort` was probed per request, DOC-IMPL-015), the unified `llama` binary, model downloads through `-hf`.
- Speed results and the conditions they were measured under: `$LLTH_HOME/docs/implementation/DOC-IMPL-006-benchmark-results-overview.md`.

### First interactive `llama-server` session (2026-10-25, informal)

The designer started `llama-server` by hand, one model at a time, and used the web UI at `http://127.0.0.1:8080` with four models: K2 Horizon 3.7B, Gemma 4 26B-A4B, Qwen3.6-35B-A3B and K2 Horizon MoVA 36B-A4B. Informal use; nothing was measured or logged, and a browser was open. Verified with read-only checks: the server listened on `127.0.0.1:8080` only (ADR-002); the 3.7B server held 4,573 MiB of VRAM and the K2 MoVA server about 4,506 MiB. The commands, all starting with `$LLTH_HOME/llama.cpp/build/bin/llama-server`:

| Model | Arguments |
|---|---|
| K2 Horizon 3.7B Q5_K_M | `-m .../models/IFM/K2-Horizon-3.7B-GGUF/K2-Horizon-4B-Q5_K_M.gguf --host 127.0.0.1 --port 8080 -c 16384 -np 1 -ngl 99 -fa on -ctk q8_0 -ctv q8_0 --temp 1.0 --top-p 0.95` |
| Gemma 4 26B-A4B | `-m .../models/google/gemma-4-26B-A4B-it-qat-q4_0-gguf/gemma-4-26B_q4_0-it.gguf --host 127.0.0.1 --port 8080 -c 16384 -np 1 -ngl 99 -ncmoe 24 -fa on -ctk q8_0 -ctv q8_0` |
| Qwen3.6-35B-A3B | `-m .../models/unsloth/Qwen3.6-35B-A3B-GGUF/Qwen3.6-35B-A3B-UD-IQ4_XS.gguf --host 127.0.0.1 --port 8080 -c 16384 -np 1 -ngl 99 -ncmoe 34 -fa on -ctk q8_0 -ctv q8_0` |
| K2 Horizon MoVA 36B-A4B | `-m .../models/IFM/K2-Horizon-MoVA-36B-A4B-GGUF/K2-Horizon-MoVA-36B-A4B-Q4_K_M.gguf --host 127.0.0.1 --port 8080 -c 16384 -np 1 -ngl 99 -ncmoe 46 -ot attn_v_exps=CPU -fa on -ctk q8_0 -ctv q8_0 -cram 0 --temp 1.0 --top-p 0.95` |

Defaults of this build that are unsafe on the 6 GB machine (KI-025): `-c 0` loads the model's full context; `-np` is automatic and splits the context between slots; the default port is 9931; `-cram` defaults to 8192 MiB of host RAM. Thinking controls present in `llama-server --help`: `--reasoning-effort`, `--reasoning-budget`, `--reasoning-format`, `--chat-template-kwargs`, `--jinja`. No launcher script exists.
