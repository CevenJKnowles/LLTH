---
id: DOC-OVW-004
title: Developer Guide
type: overview
status: active
version: v1.21
canonical: true
scope: llth
audience:
  - developer
  - maintainer
  - operator
created: "2026-10-27"
updated: "2026-11-08"
tags:
  - llth
  - developer-guide
  - status
  - folder-map
  - common-tasks
relationships:
  related:
    - DOC-ARCH-001
    - DOC-IMPL-002
    - DOC-IMPL-006
provenance:
  - human
---

# LLTH developer guide

This guide holds the working information that was in the project README until 2026-10-27: where things stand, the folder map, the models, common tasks, decisions and rules. The README is now the project's front page.

A local, open-source, open-weight language-model setup on one laptop, built from source on llama.cpp with CUDA. Everything for the project lives in this one folder; to remove it, delete `$LLTH_HOME/`. `$LLTH_HOME` stands for the project folder, the one that contains the README.

## Goals

- **Independence.** Only open-source, open-weight models with no licensing ties and no gated downloads, run locally and privately. Training data and recipes open where possible.
- **Credibility.** Every choice is a recorded decision (ADRs). Every number comes from a logged, reproducible measurement with its conditions and failures documented.
- **A compound AI system.** The direction (2026-10-24): a fast, less-thinking **steward** model for everyday requests, with reasoning **specialists** for hard ones, routed by a simple rule. Since ADR-005 (accepted 2026-11-07) nothing routes automatically: the user chooses the expert from a menu. This is a plan and is not built yet.
- **Possible later:** a public repository with an installer that downloads the chosen models (and the designer's own fine-tunes, if they exist). Not before the system works; see the known issues log (PD-011).

## Motivation

- **Independence costs more as hardware ages.** Keeping up with high-functioning AI is expensive, and staying in charge of your own data gets harder.
- **It should be available to everyone.** AI at this level belongs in public hands.
- **It reduces waste.** Running well on older, ordinary hardware extends the life of machines and reduces technological waste.
- **It is cheap.** There is no subscription, and all data stays in the hands of the user.

## Where things stand (2026-11-07)

| Area | Status |
|---|---|
| llama.cpp built (build 11839, CUDA architecture 75) | done (ADR-003) |
| Models 1 and 2: K2 Horizon 7B and 3.7B, downloaded, checksum-verified, speed-benchmarked | done (`DOC-IMPL-012`) |
| Exploration of tuning flags on the small models | rounds 1 and 2 done: a small `-ub` keeps all 7B layers on the GPU (18.6 tokens/s at 16K); the power-profile A/B tests found no meaningful speed difference for the dense and large models and about 4% for the fast 0.9B (balanced slower); see `DOC-IMPL-012` sections 5 and 6 and `DOC-IMPL-014` |
| Models 3, 4, 5: K2 MoVA 36B, Qwen3.6-35B-A3B, Gemma 4 26B-A4B | downloaded, checksum-verified and speed-benchmarked (2026-10-24, `DOC-IMPL-013`): at 8K, Gemma 23.6, Qwen 18.2 and K2 MoVA 9.9 tokens/s; K2 MoVA needs the override `-ot attn_v_exps=CPU` and `q4_0` for 32K |
| Model 6: K2 Horizon 0.9B (ADR-004 v1.4) | downloaded, verified, depth-swept: 165 tokens/s at depth 0 and 100 at 8K, all on the GPU (`DOC-IMPL-012` section 4) |
| `llama-server` and the web UI | tried by hand with four models (3.7B, Gemma, Qwen, K2 MoVA; informal, not measured; `DOC-IMPL-002`) |
| Blind quality test, round 1 (ADR-004 §5 and §5b) | **done 2026-11-05:** 140 answers scored blind by the designer, Python verified by running it; K2 MoVA first (3.75 of 5), Qwen3.6 with thinking 3.45, Gemma 4 3.30, 7B 3.15, 3.7B 3.10, Qwen3.6 without thinking 2.70, 0.9B 1.80 (`DOC-IMPL-010`) |
| Thinking-control tests (PD-014) | **partly done:** `reasoning_effort` probed on the 3.7B and K2 MoVA; effort changes the waiting time, not the tokens per second (`DOC-IMPL-015`); the answer split is handled in `quality_blind.py` v1.2 (KI-R14) |
| Steward test (ADR-004 §5a) | **done, reduced scope:** K2 3.7B only, routing 45 to 50% (`DOC-IMPL-010` §7). The designer chose an expert menu in a local web interface instead of automatic routing (ADR-005) |
| Final selection and launch configuration (ADR-005), interface design | **ADR-005 accepted 2026-11-07:** steward K2 3.7B, specialist K2 MoVA, four experts chosen from a menu (Writing, Administration, Coding, Think), no automatic routing. **Interface:** **ADR-006 accepted 2026-11-07** (local web page, FastAPI and one HTML file); **ADR-007 accepted 2026-11-07** (storage and memory: one root with `LLTH/` and `user/`, readable settings, confirmation modes); **ADR-008 accepted 2026-11-07** (document intake: a drop onto the window, a layered free toolkit, a review before filing); **ADR-009 accepted 2026-11-07** (export: PDF, DOCX, ODT and HTML); nothing is built |

## Folder map

| Path | What it holds |
|---|---|
| `$LLTH_HOME/README.md` | The project front page |
| `$LLTH_HOME/ADR/` | Architecture decision records and their index (`ADR-000-README.md`) |
| `$LLTH_HOME/docs/overview/` | `DOC-OVW-004`: this guide. `DOC-OVW-019` and `DOC-OVW-020`: the interface, document, storage and memory requirements. `DOC-OVW-001` is retired; its text became the README |
| `$LLTH_HOME/docs/governance/` | ADR policy and the documentation standard (frontmatter, naming, templates) |
| `$LLTH_HOME/docs/architecture/` | `DOC-ARCH-001`: the full project anatomy (read this first when returning) |
| `$LLTH_HOME/docs/implementation/` | Logs and results: `DOC-IMPL-001` known issues, `-002` build and feature log, `-006` benchmark overview, `-012` to `-016` benchmark results, `-017` quality test protocol |
| `$LLTH_HOME/llama.cpp/` | llama.cpp source (pinned commit `e1e3b2c40`) and its `build/bin/` programs |
| `$LLTH_HOME/models/` | Downloaded GGUF model files, one folder per publisher and repository |
| `$LLTH_HOME/.github/` | The documentation check: `workflows/docs-check.yml` and `scripts/check_docs.py` (ADR-010) |
| `$LLTH_HOME/benchmarks/` | Raw evidence: `speed/` logs, `quality/` runs and scoring, `swap-time/`, the prompt set, one `MANIFEST.sha256`, and `scripts/` in `speed/`, `quality/` and `models/` |
| `$LLTH_HOME/scripts/` | Launcher and stop scripts (not written yet) |

## Models

| # | Model | File | Size | Status |
|---|---|---|---|---|
| 1 | K2 Horizon 7B | `K2-Horizon-7B-Q4_K_M.gguf` | 5.59 GB | downloaded, verified, benchmarked |
| 2 | K2 Horizon 3.7B | `K2-Horizon-4B-Q5_K_M.gguf` | 3.64 GB | downloaded, verified, benchmarked |
| 3 | K2 Horizon MoVA 36B-A4B | `K2-Horizon-MoVA-36B-A4B-Q4_K_M.gguf` | 22.37 GB | downloaded, verified, benchmarked (needs `-ot attn_v_exps=CPU`, `DOC-IMPL-013` section 4.1) |
| 4 | Qwen3.6-35B-A3B | `Qwen3.6-35B-A3B-UD-IQ4_XS.gguf` | 17.73 GB | downloaded, verified, benchmarked |
| 5 | Gemma 4 26B-A4B | `gemma-4-26B_q4_0-it.gguf` | 14.44 GB | downloaded, verified, benchmarked |
| 6 | K2 Horizon 0.9B | `K2-Horizon-1B-Q8_0.gguf` | 1.15 GB | downloaded, verified, benchmarked |

Exact repositories, byte sizes and SHA-256 checksums are in `ADR-004` sections 1 and 1a. To delete a model, delete its file or folder.

## Common tasks

Download the remaining models (done 2026-10-24; resumes if interrupted; verifies every checksum):
```bash
bash $LLTH_HOME/benchmarks/scripts/models/download-remaining-models.sh
```
Benchmark the large models (stage 1, the expert-offload sweep; then stage 2 at the chosen values; usage in the script header; done for all three on 2026-10-24):
```bash
bash $LLTH_HOME/benchmarks/scripts/speed/bench_large_models.sh gemma sweep
bash $LLTH_HOME/benchmarks/scripts/speed/bench_large_models.sh gemma depths <ncmoe>
```
K2 MoVA needs a tensor override, passed through a variable: `OT='attn_v_exps=CPU' LOGTAG=ot-attnv bash .../bench_large_models.sh k2mova sweep` (`DOC-IMPL-013` section 4.1).
Try a model by hand in the web UI (exploration only; stop with `Ctrl+C`; the defaults of `llama-server` are unsafe here, so keep every flag; the commands for four models are in `DOC-IMPL-002`):
```bash
$LLTH_HOME/llama.cpp/build/bin/llama-server -m $LLTH_HOME/models/IFM/K2-Horizon-3.7B-GGUF/K2-Horizon-4B-Q5_K_M.gguf --host 127.0.0.1 --port 8080 -c 16384 -np 1 -ngl 99 -fa on -ctk q8_0 -ctv q8_0 --temp 1.0 --top-p 0.95
```
Then open `http://127.0.0.1:8080`.

Summarise all benchmark logs into tables:
```bash
python3 -I $LLTH_HOME/benchmarks/scripts/speed/summarize-benchmarks.py
```
Run one benchmark by hand (example: the 3.7B at 8K depth):
```bash
$LLTH_HOME/llama.cpp/build/bin/llama-bench -m $LLTH_HOME/models/IFM/K2-Horizon-3.7B-GGUF/K2-Horizon-4B-Q5_K_M.gguf -p 512 -n 128 -r 3 -fa on -ctk q8_0 -ctv q8_0 -d 8192 -ngl 99
```
Use the shell scripts with `bash` (not zsh). The full build recipe and rebuild rules are in `DOC-IMPL-002`; changing the pinned source commit needs an ADR amendment first. There are no launcher scripts yet.

## Hardware (short)

Acer ConceptD 7 (CN715-71): i7-9750H (6 cores / 12 threads), RTX 2060 Mobile 6 GB (5,746 MiB usable, compute capability 7.5, no BF16/FP8/FP4), 32 GB DDR4-2667 (about 24.5 GB available, no swap), 1 TB NVMe (btrfs). Manjaro Linux, CUDA 13.3 with g++-15 as host compiler, power profile set to performance.

## Decisions

| ADR | Decision | Status |
|---|---|---|
| `ADR-001` | llama.cpp built from source with CUDA; `llama-server` as the main interface | amended (v1.1) |
| `ADR-002` | Native user-space install, no Docker, localhost only, models inside the project | amended (v1.2) |
| `ADR-003` | Exact build configuration; web UI pinned | amended (v1.3) |
| `ADR-004` | First-round model selection and benchmark protocol, incl. the `q4_0` cache variant, the exploration phase, the steward test and model 6 (K2 Horizon 0.9B) | amended (v1.8) |
| `ADR-005` | Fleet selection: K2 3.7B and K2 MoVA, four experts chosen by the user from a menu, no automatic routing | amended (v1.5) |
| `ADR-006` | Interface: a local web page (FastAPI and one HTML file), localhost only; the Confirm setting from ADR-007; document intake from ADR-008; the export menu from ADR-009 | amended (v1.18) |
| `ADR-007` | Storage and memory: one root with `LLTH/` and `user/`, a movable default location, readable settings, expert access by the user's commands or approved proposals, manual, planning and automatic confirmation | amended (v1.13) |
| `ADR-008` | Document intake: dropping a file onto the window or `/open`; pypdfium2, Pandoc and charset-normalizer, provided inside LLTH's folder; a review before filing; originals kept; OCR for scans is an anticipated update | amended (v1.28) |
| `ADR-009` | Export: PDF, DOCX, ODT and HTML with Pandoc and Typst, the browser's print as a fallback, templates in `user/preferences/templates/` | amended (v1.3) |
| `ADR-010` | Documentation checks in continuous integration: one workflow and a standard-library script | accepted (v1.6) |

Files are in `$LLTH_HOME/ADR/`.

## Rules

- **ADR first:** no code, build, install or configuration change without an accepted ADR; accepted ADRs are amended, never silently edited.
- **Every document** carries YAML frontmatter per `$LLTH_HOME/docs/governance/DOC-GOV-002-documentation-standard.md`.
- **Safety:** the server binds to `127.0.0.1` only, never `0.0.0.0`; no Docker; no system-wide installs; no sudo; models only from the sources in ADR-004, verified by checksum.
- **Only build and use llama.cpp;** never commit, push or open issues upstream.
- **The benchmark helper stops a run** at 92 °C GPU temperature or 1,500 MiB free RAM.

## Anticipated future updates

Updates that may follow the first version. None is scheduled. Contributions are welcome as pull requests, and each update is covered by an ADR before it is built.

| Anticipated update | What it would add | Recorded in |
|---|---|---|
| OCR for scans and photographs | Reading scans, photographs and scanned PDFs with Tesseract, the doubtful-word review and the OCR languages. The first version declines them with a message. | `ADR-008` §4a |
| Correcting a doubtful word | Fixing a word on the review screen; not designed yet. | `ADR-008` §4a |
| A heavier document tier | Docling as an optional tier for layout- and table-aware conversion. | `ADR-008` §4 |
| OCR vision models | Small OCR vision models served through llama.cpp, if they prove themselves. | `ADR-008` §4, Option D |
| Native tool calling | Letting a model call tools (write, save, delete, move) through the engine's built-in support. | `ADR-007` Non-goals |
| LaTeX as a PDF engine | An optional extra for users who want it. | `ADR-009` |

---

## How it is judged

*(Moved here from the design intention on 2026-10-27, when that text became the project README.)*

Success is judged by evidence, not by features:

1. **Everyday requests are answered at conversational speed** on the reference machine, with the project's speed gates met (`ADR-004` section 6: at least 20 tokens/s at 8K for small models, at least 8 for heavy ones).
2. **Hard requests reach a reasoning model** and are answered at an acceptable cost in time, with the routing accuracy measured against labels set in advance (`ADR-004` section 5a).
3. **Quality is judged by the designer's own blind scoring** on their real tasks, not by published indices alone.
4. **Another person can reproduce the setup** on comparable hardware from the repository, with the same checksums and the same logged procedure.
5. **Every claim in the public documentation is traceable** to a logged measurement or a cited source.
