---
id: DOC-ARCH-001
title: LLTH Project Anatomy
type: architecture
status: active
version: v1.24
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
  - architecture
  - anatomy
  - local-llm
relationships:
  related:
    - ADR-001
    - ADR-002
    - ADR-003
    - DOC-GOV-001
    - DOC-GOV-002
    - DOC-IMPL-001
    - DOC-IMPL-002
provenance:
  - human
---

# LLTH Project Anatomy

## Purpose

A complete map of LLTH: what it is, how a request travels through it, where every file and folder lives, what each part of the llama.cpp source does, which rules govern it, and what is built, planned or still open. Status labels used throughout: **built** (exists and was checked), **planned** (decided or expected, not started), **open** (not decided).

LLTH is a local large-language-model workspace on one laptop.

---

## 1. The system at a glance

```
 You (browser, terminal, or Python)
        │  HTTP, localhost only: http://127.0.0.1:8080  (OpenAI-compatible API under /v1, web UI at /)
        ▼
 llama-server ── embedded web UI (b11838)
        │
        ▼
 libllama  (model loading, tokenizer, KV cache, sampling)       ← src/, include/, common/
        │
        ▼
 ggml  (tensor maths and scheduling)                            ← ggml/
        ├──► CUDA backend  → RTX 2060, 6 GB VRAM               (attention layers, hot weights)
        └──► CPU backend   → i7-9750H + 32 GB RAM              (MoE expert weights, overflow)
        ▲
        │ reads
 GGUF model files in $LLTH_HOME/models/             (all 6 models downloaded and verified)
```

**Fleet (ADR-005):** a steward (K2 Horizon 3.7B) and a specialist (K2 Horizon MoVA). The user chooses the expert from a menu; nothing routes automatically. The diagram above is one model server; one server runs at a time (ADR-006).

How a token is made: the model weights are read once per generated token, so speed is roughly memory bandwidth divided by the bytes read. For a mixture-of-experts (MoE) model only a few experts are used per token, so keeping the shared layers in fast VRAM and the experts in RAM (`--n-cpu-moe`) gives the best quality for this hardware.

---

## 2. Hardware and system (verified 2026-10-23)

| Part | Value | Consequence |
|---|---|---|
| Laptop | Acer ConceptD 7 (CN715-71), Manjaro Linux, kernel 6.18 | Plug in and use a performance profile for long runs |
| CPU | Intel i7-9750H, 6 cores / 12 threads, AVX2 + FMA, no AVX-512 | Good for token generation with CPU experts, slow at reading long prompts |
| GPU | NVIDIA RTX 2060 Mobile, 6 GB, compute capability 7.5, driver 610.57.04 | The fast tier. FP16 only: no native BF16, FP8 or FP4 |
| RAM | 32 GB DDR4-2667 dual channel, no swap | Overfilling kills the process instead of slowing down |
| Disk | 1 TB NVMe, btrfs, about 663 GB free | Room for many models. Timeshift snapshots `@` but not `@home` |
| CUDA | 13.3.73 at `/opt/cuda` | Needs GCC 15 or older as the host compiler |
| Compilers | gcc/g++ 16.2.1 (default), gcc-15/g++-15 15.3.0 (used) | See KI-003 |

Capability tiers (generation speed at depth 0 from `DOC-IMPL-012` and `DOC-IMPL-013`; tier C not measured):

| Tier | What fits | Measured speed |
|---|---|---|
| A: fully in VRAM | Dense models up to about 7–9B at 4-bit | 40.0 to 164.8 tokens/s (7B, 3.7B, 0.9B) |
| B: MoE with experts in RAM | MoE models of about 20–35B total, 2–4B active, up to about 22 GB at 4-bit | 10–20 tokens/s |
| C: dense models spilling into RAM | Dense 12–32B | not measured |

Hard ceiling: about a 35B-total MoE at 4-bit. Fine-tuning locally is limited to about 3–4B dense models with QLoRA (PD-006).

---

## 3. Folder anatomy

```
$LLTH_HOME/
├── README.md                                   the project front page
├── LICENSE, LICENSE-DOCS, LICENSE-DATA         Apache-2.0 (code), CC BY-NC 4.0 (documentation), CC BY 4.0 (benchmark data)
├── NOTICE                                      copyright, licence summary, third-party credits
├── .gitignore                                  keeps models/, llama.cpp/ and docs/local/ out of the repository
├── .github/                                    the documentation check: workflows/docs-check.yml and scripts/check_docs.py (ADR-010)
├── ADR/                                        decisions (the "why")
│   ├── ADR-000-README.md                       index of all ADRs and their status
│   ├── ADR-001-llama-cpp-as-local-inference-engine.md
│   ├── ADR-002-native-user-space-install-no-docker-localhost-only.md
│   ├── ADR-003-llama-cpp-build-configuration.md
│   ├── ADR-004-first-round-model-selection-and-benchmark-protocol.md
│   ├── ADR-005-fleet-selection-roles-and-category-profiles.md
│   ├── ADR-006-interface-local-web-page-and-expert-menu.md
│   ├── ADR-007-storage-and-memory-directory-tree-and-confirmation.md
│   ├── ADR-008-document-intake-conversion-and-filing.md
│   └── ADR-009-export-formats-and-pdf-engine.md
├── docs/
│   ├── governance/                             the rules
│   │   ├── DOC-GOV-001-adr-policy.md
│   │   └── DOC-GOV-002-documentation-standard.md
│   ├── overview/
│   │   ├── DOC-OVW-004-developer-guide.md      status, folder map, models, common tasks, decisions, rules
│   │   ├── DOC-OVW-019-interface-and-document-handling-requirements.md
│   │   └── DOC-OVW-020-storage-and-memory-requirements.md
│   ├── architecture/
│   │   └── DOC-ARCH-001-project-anatomy.md     this file
│   └── implementation/
│       ├── DOC-IMPL-001-known-issues-log.md
│       ├── DOC-IMPL-002-build-and-feature-log.md
│       ├── DOC-IMPL-006-benchmark-results-overview.md
│       ├── DOC-IMPL-010-quality-round1-results.md
│       ├── DOC-IMPL-011-document-tools-research.md
│       ├── DOC-IMPL-012-benchmark-results-small-models.md
│       ├── DOC-IMPL-013-benchmark-results-large-models.md
│       ├── DOC-IMPL-014-power-profile-tests.md
│       ├── DOC-IMPL-015-reasoning-effort-probes.md
│       ├── DOC-IMPL-016-model-swap-time.md
│       └── DOC-IMPL-017-quality-test-protocol.md
├── llama.cpp/                                  upstream source, full git history, pinned at e1e3b2c40
│   └── build/                                  compiled output (266 MB); delete to force a clean build
│       └── bin/                                22 programs and 29 shared libraries
├── models/                                     GGUF model files, one folder per publisher/repo (ADR-004)
│   ├── IFM/K2-Horizon-7B-GGUF/                 downloaded, verified
│   ├── IFM/K2-Horizon-3.7B-GGUF/               downloaded, verified
│   ├── IFM/K2-Horizon-0.9B-GGUF/               downloaded, verified, benchmarked (model 6, ADR-004 v1.4)
│   ├── IFM/K2-Horizon-MoVA-36B-A4B-GGUF/       downloaded, verified, benchmarked (needs -ot attn_v_exps=CPU)
│   ├── unsloth/Qwen3.6-35B-A3B-GGUF/           downloaded, verified, benchmarked
│   └── google/gemma-4-26B-A4B-it-qat-q4_0-gguf/  downloaded, verified, benchmarked
├── benchmarks/                                 README.md (DOC-IMPL-007), speed/ logs, quality/, swap-time/, MANIFEST.sha256, and scripts/ (speed/, quality/, models/)
└── scripts/                                    launcher, stop and build scripts (empty; planned)
```

`docs/runtime/` is created when its first document exists (DOC-GOV-002).

Sizes: whole `llama.cpp` folder 840 MB, of which `.git` 395 MB and `build/` 266 MB.

---

## 4. The llama.cpp source (what each part is for)

Upstream project, MIT licence. Used as-is; nothing is committed, pushed or opened upstream (ADR-001). Its own contributor rule files do not apply here.

| Path in `$LLTH_HOME/llama.cpp/` | Role |
|---|---|
| `include/` | Public C header of the library |
| `src/` | The core library `libllama`: model loading, architectures, KV cache, sampling |
| `ggml/` | The tensor library underneath, with one folder per hardware backend under `ggml/src/` |
| `ggml/src/ggml-cuda/` | The NVIDIA backend (built, architecture 75) |
| `ggml/src/ggml-cpu/` | The CPU backend (built, native tuning) |
| `ggml/src/ggml-*` (Vulkan, HIP, Metal, SYCL, OpenCL and others) | Other backends, not built |
| `common/` | Shared code for the programs: argument parsing, downloads (`-hf`), chat templates |
| `tools/server/` | `llama-server` |
| `tools/cli/`, `tools/completion/` | `llama-cli`, `llama-completion` |
| `tools/llama-bench/` | `llama-bench` |
| `tools/quantize/` | `llama-quantize` |
| `tools/gguf-split/`, `tools/imatrix/`, `tools/perplexity/`, `tools/export-lora/`, `tools/cvector-generator/`, `tools/tokenize/`, `tools/tts/`, `tools/fit-params/`, `tools/batched-bench/`, `tools/results/` | Helper programs, built |
| `tools/mtmd/` | Multimodal (image) input: `llama-mtmd-cli` and deprecation stubs |
| `tools/ui/` | Source of the web UI (not used; the prebuilt archive is embedded instead) |
| `app/` | Source of the unified `llama` binary (not evaluated) |
| `convert_hf_to_gguf.py`, `convert_lora_to_gguf.py`, `gguf-py/` | Python tools to turn Hugging Face models or LoRA adapters into GGUF. Not used yet; running them needs Python packages, which means a venv and approval (no system pip) |
| `docs/build.md`, `docs/backend/` | Upstream build and backend documentation |
| `tests/`, `examples/`, `benches/`, `pocs/` | Not built (tests and examples OFF) |
| `vendor/` | Bundled third-party code (for example the HTTP library) |

### Compiled programs (in `build/bin/`)

| Program | What it does | Status |
|---|---|---|
| `llama-server` | Web UI plus OpenAI-compatible API server | built |
| `llama-cli` | Command-line chat | built |
| `llama-bench` | Measures prompt and generation speed | built |
| `llama-quantize` | Converts a model to a lower precision | built |
| `llama-gguf-split` | Splits or merges GGUF files | built |
| `llama-perplexity`, `llama-imatrix` | Quality measurement, quantization calibration | built |
| `llama-export-lora`, `llama-cvector-generator` | Adapter merging, control vectors | built |
| `llama-mtmd-cli`, `llama-mtmd-debug` | Image-capable chat | built |
| `llama-tokenize`, `llama-tts`, `llama-fit-params`, `llama-batched-bench`, `llama-completion`, `llama-results`, `llama` | Tokenizing, speech, offload-fit estimate, batch benchmark, completion, results, unified binary | built |
| `llama-llava-cli`, `llama-minicpmv-cli`, `llama-qwen2vl-cli`, `llama-gemma3-cli` | Deprecation stubs | built (KI-007) |

---

## 5. Build anatomy

Everything is decided in ADR-003 and logged in DOC-IMPL-002.

| Setting | Value | Why |
|---|---|---|
| Generator / type | Ninja, Release | Fast, optimised |
| Compiler | gcc-15 / g++-15 for C, C++ and the CUDA host | CUDA 13.3 rejects gcc 16 |
| GPU target | `CMAKE_CUDA_ARCHITECTURES=75` | The RTX 2060 only: shorter build, smaller files |
| CPU target | `GGML_NATIVE` on | Tuned to this CPU, not portable |
| NCCL, tests, examples | Off | Not needed |
| Kept at defaults | Flash attention on, CUDA graphs on, OpenSSL on, shared libraries on | Listed in ADR-003 §6 |
| Web UI | Prebuilt archive `b11838`, set with `HF_UI_VERSION` on every configure | Reproducible (ADR-003 §8) |

The network is used at build time for: the GitHub clone and fetch, and the web UI archive from Hugging Face. No sudo, no system packages and no pip are involved.

---

## 6. Runtime anatomy

| Item | Decision or status |
|---|---|
| Server address | `127.0.0.1`, port 8080 set explicitly with `--port 8080` (the build default is 9931), never `0.0.0.0` (ADR-002) |
| Model storage | `$LLTH_HOME/models/`, via the `LLAMA_CACHE` environment variable set in launcher scripts (planned; PD-004) |
| Model format | GGUF; default quantisation Q4_K_M; avoid FP4 formats (no native support on this GPU) |
| Model download | `llama-server -hf <org>/<repo>:<quant>` (needs HTTPS, which is built) |
| MoE launch flags | `-ngl 99 --n-cpu-moe N -c <context> -fa on -ctk q8_0 -ctv q8_0`, with N tuned down until VRAM is nearly full. Flag spelling must be checked against `--help` first |
| Python access | HTTP to `http://localhost:8080/v1` with the `openai` client from pacman (`python-openai`) or a venv; the `llama-cpp-python` wrapper is not used (ADR-001) |
| Chat interface | LLTH's own local web page (ADR-006); `llama-server` also serves a built-in web UI |
| Thinking length | Reasoning models can be steered with `--reasoning-effort` (low, medium, high), switched off with `--reasoning off`, or capped with `--reasoning-budget N` and `-n`; K2 Horizon's template defines three effort modes and an empty-thinking mode. `reasoning_effort` is probed in `DOC-IMPL-015` |
| Context and cache | Context depth costs speed because the cache competes with the weights for the 5.7 GB: measured in DOC-IMPL-012 and DOC-IMPL-013. `-ub 128` frees room for two more layers; the `q4_0` cache halves the cache memory (ADR-004 v1.1, v1.2) |
| Routing | None: the user chooses the expert from a menu (ADR-005) |
| Stop procedure | A stop script frees RAM and VRAM (planned) |

Model selection criteria: permissive licence (Apache-2.0 or MIT preferred), official or well-known publishers, 4-bit size up to about 22 GB for Tier B, fresh web research with named sources because the field changes monthly.

---

## 7. Governance anatomy

| Rule | Where it is defined |
|---|---|
| ADR before any code, build, install or configuration change; no silent edits; supersession needs a new ADR | DOC-GOV-001 |
| Every document has YAML frontmatter, fixed field order, `ADR-NNN-` / `DOC-<AREA>-NNN-` names, templates | DOC-GOV-002 |
| `canonical: pending` while a document is reserved or draft; `provenance` is a list | DOC-GOV-002 |

Decisions so far:

| ADR | Decision | Status |
|---|---|---|
| ADR-001 | llama.cpp built from source with CUDA, `llama-server` as the main interface | amended (v1.1) |
| ADR-002 | Native user-space install, no Docker, localhost only, models inside the project | amended (v1.2) |
| ADR-003 | Exact build configuration and web UI pin | amended (v1.3) |
| ADR-004 | First-round selection (six models, exact files and checksums), benchmark protocol, gates, `q4_0` cache variant, exploration phase, steward test, model 6 (K2 Horizon 0.9B) | amended (v1.8) |
| ADR-005 | Fleet: K2 3.7B and K2 MoVA, four experts chosen from a menu, no automatic routing | amended (v1.5) |
| ADR-006 | Interface: a local web page (FastAPI and one HTML file), localhost only | amended (v1.18) |
| ADR-007 | Storage and memory: one root with `LLTH/` and `user/`, readable settings, confirmation modes | amended (v1.13) |
| ADR-008 | Document intake: a drop onto the window or `/open`, a layered free toolkit, a review before filing, originals kept | amended (v1.27) |
| ADR-009 | Export: PDF, DOCX, ODT and HTML with Pandoc and Typst | amended (v1.3) |
| ADR-010 | Documentation checks in continuous integration: one workflow and a standard-library script | accepted (v1.6) |

---

## 8. Relationship to the rest of the machine

| Location | Role | Notes |
|---|---|---|
| `$LLTH_HOME/` | This project | The only place LLTH files live |

Removed on 2026-10-23: Ollama (package, manual install, service, models, about 60 GB) and LM Studio (package, its data folder, about 52 GB), so that the system uses llama.cpp directly.

---

## 9. Security boundaries

- Runs as the normal user; nothing needs root; nothing is installed system-wide (ADR-002).
- The server listens on localhost only.
- GGUF files are data, not programs, but file-parser bugs have existed. Take models only from official or well-known publishers. Sandboxing with bubblewrap is the first step if unvetted models are ever used (PD-007).
- No container isolation (accepted trade-off, ADR-002).
- Downloaded at build time: the web UI archive, checked by a checksum from the same bucket (KI-008).

---

## 10. Where the project stands

| Area | Status |
|---|---|
| Old tools removed | done |
| Folders, governance documents, ADR-001 to ADR-004 | done |
| llama.cpp built (CUDA, sm_75), version and device check | done |
| Model research, ADR-004 | done |
| Models 1, 2 and 6 (K2 Horizon 7B, 3.7B, 0.9B) downloaded and benchmarked | done (DOC-IMPL-012) |
| Models 3, 4, 5 (K2 MoVA 36B, Qwen3.6, Gemma 4) | downloaded, verified and speed-benchmarked with `bench_large_models.sh` (DOC-IMPL-013); K2 MoVA needs `-ot attn_v_exps=CPU` |
| Power-profile A/B tests | done: no meaningful difference for the dense and large models, about 4% for the fast 0.9B (DOC-IMPL-014); `performance` stays the benchmark condition |
| `llama-server`, web UI | tried by hand with four models (informal, not measured; DOC-IMPL-002); thinking controls not yet tested; MoE expert offload (`-ncmoe`, `-ot`) works with `llama-bench` and the server; defaults are unsafe (KI-025) |
| Exploration rounds on the small models (flags: `-ub`, `-nkvo`, threads, output on the CPU) | rounds 1 and 2 done (DOC-IMPL-012 sections 5 and 6) |
| Blind quality test and steward test (ADR-004 section 5a), then ADR-005 | done (DOC-IMPL-010; ADR-005 accepted) |
| Routing design | closed: no automatic routing (ADR-005) |
| Launcher scripts, build script | planned |
| Fine-tuning | open (PD-006) |

---

## Amendment record

| Version | Date | Summary |
|---------|------|---------|
| v1.0 | 2026-10-23 | Initial anatomy after the first successful build. |
| v1.1 | 2026-10-23 | Removed references to withdrawn or resolved issues (KI-011, KI-014). |
| v1.2 | 2026-10-23 | The project README now has the id `README` (DOC-GOV-002 v1.5). |
| v1.3 | 2026-10-23 | Removed references to another project. |
| v1.5 | 2026-10-23 | Port wording corrected (build default is 9931). |
| v1.7 | 2026-10-23 | Governance table now describes `provenance` as a list (DOC-GOV-002 v1.7). |
| v1.9 | 2026-10-23 | Checkpoint 1: models folder, benchmarks folder and status updated; DOC-IMPL-006 added to the tree. |
| v1.10 | 2026-10-24 | Documentation update: steward/compound-system direction, thinking and cache controls, ADR-004 v1.3 and ADR-002 v1.1 in the decisions table, VSCode relationship, current status and next steps. |
| v1.11 | 2026-10-24 | Round 2 reflected in the status table and next steps. |
| v1.12 | 2026-10-24 | Mini-checkpoint: all six models downloaded and verified, model 6 added (ADR-004 v1.4), A/B result and large-model benchmark script reflected in the tree, status and next steps. |
| v1.13 | 2026-10-24 | Mini-checkpoint 3: models 3 to 5 benchmarked (K2 MoVA with the value-expert override), expert offload status, next steps. |
| v1.14 | 2026-10-24 | Added `docs/overview/` and `DOC-OVW-001` (design intention) to the tree. |
| v1.15 | 2026-10-24 | Combined power-profile A/B done; status and next steps updated. |
| v1.16 | 2026-10-24 | Wrap-up: `llama-server` status updated. |
| v1.17 | 2026-10-27 | Project name LLTH applied throughout; `DOC-OVW-001` is now active. |
| v1.18 | 2026-10-27 | `DOC-OVW-001` is the release-day text and is a draft until release. |
| v1.19 | 2026-10-27 | The README is now the release-day text (draft); its working content moved to the developer guide `DOC-OVW-004`; `DOC-OVW-001` is a pointer to the README. Tree updated. |
| v1.20 | 2026-10-27 | Prepared for a public repository: paths shown as `$LLTH_HOME`, section 8 reduced to this project, tree gained the licence files, `NOTICE`, `.gitignore` and the benchmarks README. |
| v1.21 | 2026-11-07 | Editorial revision for publication. |
| v1.22 | 2026-11-07 | The requirements documents `DOC-OVW-019` and `DOC-OVW-020` added to the folder tree. |
| v1.23 | 2026-11-07 | Capability tiers show measured speeds; the folder tree lists every ADR and implementation document; the runtime table is brought up to date. |
| v1.24 | 2026-11-07 | ADR-010 and the `.github` folder added. |
