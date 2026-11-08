---
id: ADR-003
title: llama.cpp Build Configuration
type: adr
status: amended
version: v1.4
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
  - adr
  - build
  - cuda
  - cmake
subordinate_to: ADR-001
provenance:
  - human
---

# ADR-003 — llama.cpp Build Configuration

## Status

Amended (v1.4)

---

## 1. Context

ADR-001 chose llama.cpp built from source with CUDA for sm_75. ADR-002 fixed the install to user space under `$LLTH_HOME/`. This ADR fixes the exact build configuration. It must be accepted before any `cmake` command is run (DOC-GOV-001, Rule 1).

### Decision drivers

- Correct and reproducible: the same command gives the same binary, and the llama.cpp commit is recorded.
- Fast on the target hardware: RTX 2060 Mobile (compute capability 7.5), i7-9750H (AVX2, no AVX-512).
- Minimal attack surface and no system changes: no sudo, no installs, nothing outside `$LLTH_HOME/`.
- Short build time on a laptop with limited cooling.
- Traceability: `llama-server --version` should report a meaningful build number.

### Facts verified on 2026-10-23

| Item | Value |
|---|---|
| Source commit | `e1e3b2c` (shallow clone, depth 1) |
| CUDA toolkit | 13.3.73 at `/opt/cuda`; `nvcc` on PATH; `NVCC_CCBIN=/usr/bin/g++-15` set by `/etc/profile.d` |
| nvcc host-compiler limit | `/opt/cuda/include/crt/host_config.h` rejects GCC newer than 15 |
| Compilers | default gcc/g++ 16.2.1; `gcc-15` and `g++-15` 15.3.0 installed |
| GPU | RTX 2060, compute capability 7.5, driver 610.57.04 |
| OpenSSL | 3.6.4 headers present (needed for `-hf` downloads) |
| NCCL | installed (`/usr/include/nccl.h`); multi-GPU only, irrelevant here |
| Build tools | cmake 4.4.3, ninja 1.13.2; ccache not installed |
| Resources | 12 threads, 24 GB RAM available |
| Shallow-clone effect | `git rev-list --count HEAD` returns 1, so the build number would be `b1` |
| Web UI | By default the build downloads prebuilt UI assets from a Hugging Face bucket (`ggml-org/llama-ui`), checking them against a checksum fetched from the same bucket. It tries version `b<build number>` first, then `latest`. |

### Rationale

Options left at their defaults are listed in §6.

---

## 2. Decision

### §1 Build command

```bash
cmake -S $LLTH_HOME/llama.cpp -B $LLTH_HOME/llama.cpp/build -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_COMPILER=/usr/bin/gcc-15 \
  -DCMAKE_CXX_COMPILER=/usr/bin/g++-15 \
  -DCMAKE_CUDA_HOST_COMPILER=/usr/bin/g++-15 \
  -DGGML_CUDA=ON \
  -DCMAKE_CUDA_ARCHITECTURES=75 \
  -DGGML_CUDA_NCCL=OFF \
  -DLLAMA_BUILD_TESTS=OFF \
  -DLLAMA_BUILD_EXAMPLES=OFF
cmake --build $LLTH_HOME/llama.cpp/build --config Release -j 8
```

### §2 Toolchain

One toolchain for everything: gcc-15 and g++-15 for C, C++ and the CUDA host compiler. CUDA 13.3 cannot use gcc 16, and mixing compilers in one binary adds an avoidable variable.

### §3 GPU target

`CMAKE_CUDA_ARCHITECTURES=75` builds only for the RTX 2060. This gives a deterministic result (no dependence on GPU auto-detection), a shorter build and smaller binaries. If the GPU ever changes, this ADR is amended.

### §4 CPU target

`GGML_NATIVE` stays at its default (ON), which tunes the CPU code to this i7-9750H (AVX2/FMA). The binaries are not portable to other CPUs, which is acceptable.

### §5 Targets built

Tools stay ON (`llama-server`, `llama-cli`, `llama-bench`, `llama-quantize`, `llama-gguf-split`, `llama-perplexity`). Tests and examples are OFF to cut build time. NCCL is OFF because it is for multi-GPU setups and would link an unneeded library.

### §6 Defaults deliberately kept

`GGML_CUDA_FA=ON` (flash attention). `GGML_CUDA_FA_QUANTS` default (`q4_0-q4_0;q8_0-q8_0;f16-f16;bf16-bf16`), so `-ctk q8_0 -ctv q8_0` works, while mixed K/V cache types (for example `q8_0` K with `q4_0` V) are not compiled. `LLAMA_OPENSSL=ON` for HTTPS downloads. `BUILD_SHARED_LIBS=ON`, so the binaries load libraries from the build directory and cannot be copied elsewhere alone. CUDA graphs and link compression mode are left at their defaults; the configure output is checked and recorded.

### §7 Build identity

Before configuring, convert the shallow clone to a full one (`git -C $LLTH_HOME/llama.cpp fetch --unshallow`). Then the build number is the real commit count, `llama-server --version` is meaningful, and the UI download requests the version matching the build. The cost is a larger download (history) and about the same again in disk space inside the project folder.

### §8 Web UI

Use the default prebuilt UI download (`LLAMA_USE_PREBUILT_UI=ON`, `LLAMA_BUILD_UI=OFF`). Building the UI from source needs `npm install` of a large dependency tree, which is a bigger supply-chain exposure than one checksum-verified archive from the official `ggml-org` bucket. The checksum comes from the same bucket, so it guards against corruption, not against a compromised bucket. If the download fails or the version does not exist, the build falls back to `latest`, and the fallback is recorded.

**Pin rule:** the UI archive bucket only holds archives for builds that changed UI inputs, so `b<build number>` often does not exist (it did not for b11839) and `latest` moves over time. Therefore configure with the environment variable `HF_UI_VERSION` set to the newest existing archive at or below the build number (check with `curl -s -o /dev/null -w '%{http_code}' -L 'https://huggingface.co/buckets/ggml-org/llama-ui/resolve/b<N>/dist.tar.gz.sha256?download=true'`, which returns 200 when it exists). The variable must be set on every configure, because CMake reads it from the environment. For commit `e1e3b2c40` (b11839) the pin is `b11838`. Finding: the archive downloaded as `latest` and the `b11838` archive were byte-identical (SHA-256 `8714ff36…`), and b11839 changed only `tools/ui/package.json` and `package-lock.json`.

---

## 3. Consequences

### Positive

- Reproducible: the commit and every option are recorded.
- Faster configure and compile than a generic build.
- No system changes; the build can be deleted with `$LLTH_HOME/llama.cpp/build/`.
- The server reports a real build number and commit (`build 11839, commit e1e3b2c40`). The web UI does not match the server version (see Implementation notes).

### Negative

- The binaries are tied to this CPU and this GPU architecture.
- The build downloads UI assets from Hugging Face at build time (network access during the build).
- Mixed K/V cache types need a rebuild with `-DGGML_CUDA_FA_QUANTS=...`.
- gcc-15 must stay installed. When CUDA supports gcc 16 and `/etc/profile.d` is changed, this ADR gets an amendment.
- Build time was about 15 minutes (`DOC-IMPL-002`).

### Implementation notes

- `/opt/cuda/bin/nvcc` is on PATH, so `CMAKE_CUDA_COMPILER` is not set explicitly. If configure fails to find CUDA, the first fix is `-DCMAKE_CUDA_COMPILER=/opt/cuda/bin/nvcc`; any change like that is recorded as an amendment.
- None of the commands in this build needs sudo (ADR-002).
- Updating later: `git -C $LLTH_HOME/llama.cpp pull`, then re-run the build command in §1 (an update to the pinned commit is recorded in this ADR).
- **Configure result (2026-10-23):** clone converted to full history (11,839 commits, pack 392 MiB) at commit `e1e3b2c40`, which is one commit behind upstream and deliberately pinned. Configure succeeded in 4.5 s with GNU 15.3.0 (C, C++, CUDA host), NVIDIA CUDA compiler 13.3.73, `CMAKE_CUDA_ARCHITECTURES=75`, OpenSSL 3.6.4, CPU backend `-march=native`, FlashAttention combinations `f16-f16;q4_0-q4_0;q8_0-q8_0;bf16-bf16`. Defaults confirmed in the cache: `GGML_CUDA_GRAPHS=ON`, `GGML_CUDA_COMPRESSION_MODE=size`, `BUILD_SHARED_LIBS=ON`, `LLAMA_USE_PREBUILT_UI=ON`, `LLAMA_BUILD_UI=OFF`. Build targets present: `llama-server`, `llama-cli`, `llama-bench`, `llama-quantize`. 
- **Build result (2026-10-23):** compile finished with exit code 0 (433 steps; wall-clock time not measured). `llama-server --version` reports `0.7.0-dev (build 11839, commit e1e3b2c40)`, built with GNU 15.3.0. `llama-cli --list-devices` reports `CUDA0: NVIDIA GeForce RTX 2060 (5746 MiB, 5583 MiB free)`. Binaries are in `$LLTH_HOME/llama.cpp/build/bin/`. Build log: kept only in a temporary location.
- **Web UI fallback:** the UI archive for `b11839` does not exist in the `ggml-org/llama-ui` bucket (HTTP error on its checksum file), so the build fell back to `latest`, verified its checksum, extracted and embedded 70 assets. The UI is therefore not guaranteed to match this server build.

### Related

- ADR-001 — llama.cpp as the Local Inference Engine
- ADR-002 — Native User-Space Install, No Docker, Localhost Only

---

## 4. Non-goals

- Model selection and runtime launch flags (separate ADR).
- Multi-GPU, ROCm, Vulkan or CPU-only builds.
- Portable or redistributable binaries.
- Installing ccache or any other package.

---

## 5. Options considered

### Option A — Auto-detected CUDA architecture (`-DGGML_CUDA=ON` only)

Works when the GPU is visible, but relies on detection and, with `GGML_NATIVE` off, builds for many architectures. Rejected in favour of an explicit `75`.

### Option B — Default compiler (gcc 16) for C and C++, g++-15 for CUDA only

Works. Rejected because it mixes two compiler versions in one binary for no benefit.

### Option C — Build the web UI from source with npm

Avoids the Hugging Face download but pulls a large npm dependency tree. Rejected on supply-chain grounds. Revisit if the prebuilt UI becomes unavailable.

### Option D — Keep the shallow clone

Smaller and quicker, but the build number would be `b1` and the UI download would fall back to `latest`, losing traceability. Rejected (§7).

### Option E — `-DGGML_NATIVE=OFF` and a multi-architecture build

Portable but a large, slow build with no benefit on a single machine. Rejected.

### Option F — Build all targets, including tests and examples

Adds build time with no use for this project. Rejected.

---

## 6. Amendment record

| Version | Date | Summary |
|---------|------|---------|
| v1.0 | 2026-10-23 | Initial. Accepted by the designer on 2026-10-23 after reviewing the pros and cons of §7 (unshallow clone) and §8 (prebuilt web UI). |
| v1.1 | 2026-10-23 | Recorded the build result. Correction to §7/§8 reasoning: the unshallow step gave a real build number (11839) but did not make the UI download match, because the bucket has no `b11839` archive and the build used `latest`. §7 remains justified by traceability of the server build; the UI match benefit does not apply. |
| v1.2 | 2026-10-23 | Added the web UI pin rule (§8): configure with `HF_UI_VERSION=b11838`. Reconfigure and incremental rebuild approved by the designer. |
| v1.3 | 2026-11-07 | Editorial revision for publication. |
| v1.4 | 2026-11-08 | §9 (verification after the build) removed: the build number, commit and GPU target are recorded in the build log (`DOC-IMPL-002`). |
