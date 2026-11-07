---
id: DOC-OVW-004
title: Developer Guide
type: overview
status: active
version: v1.20
canonical: true
scope: llth
audience:
  - developer
  - maintainer
  - operator
created: "2026-10-27"
updated: "2026-11-07"
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
| `ADR-008` | Document intake: dropping a file onto the window or `/open`; pypdfium2, Pandoc and charset-normalizer, provided inside LLTH's folder; a review before filing; originals kept; OCR for scans is an anticipated update | amended (v1.27) |
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

---

## Amendment record

### This guide

| Version | Date | Summary |
|---------|------|---------|
| v1.0 | 2026-10-27 | Created from the content of the project README (v2.12), moved here unchanged except for the folder map entries for the README and the overview folder. "How it is judged" added, moved from the design intention. |
| v1.1 | 2026-10-27 | Prepared for a public repository: the project path is `$LLTH_HOME` everywhere, details of the author's workspace and tools moved to a local-only reference (not committed), "the designer" used throughout the older documents, benchmark scripts made independent of the author's home directory, and the paths in the benchmark logs replaced by `$LLTH_HOME`. Licence files, `NOTICE` and `benchmarks/README.md` added. |
| v1.2 | 2026-11-05 | Where things stand: blind quality round 1 done (`DOC-IMPL-010`), thinking-control tests partly done (`DOC-IMPL-015`, KI-026). |
| v1.3 | 2026-11-05 | Where things stand: the answer split is handled (KI-R14). |
| v1.4 | 2026-11-05 | Where things stand: steward test done (reduced scope); ADR-005 direction. |
| v1.5 | 2026-11-05 | Where things stand: ADR-005 drafted (experts instead of category buttons); swap time measured. |
| v1.6 | 2026-11-07 | ADR-005 accepted and reflected: the compound-system goal (the user chooses the expert), where things stand (selection accepted, interface mockup approved, ADR-006 drafted), and the decisions table (ADR-005 and ADR-006 added). |
| v1.7 | 2026-11-07 | ADR-006 accepted and reflected (where things stand, decisions table). |
| v1.8 | 2026-11-07 | ADR-007 accepted and reflected (where things stand, decisions table). |
| v1.9 | 2026-11-07 | ADR-006 shown as amended (v1.13, the Confirm setting). |
| v1.10 | 2026-11-07 | ADR-008 accepted and reflected (where things stand, decisions table). |
| v1.11 | 2026-11-07 | ADR-006 shown as amended (v1.14, document intake). |
| v1.12 | 2026-11-07 | ADR-006 shown as amended (v1.15) and ADR-008 as amended (v1.19): a file chooser as a second way in. |
| v1.13 | 2026-11-07 | ADR-007 shown as amended (v1.12). |
| v1.14 | 2026-11-07 | ADR-009 accepted and reflected; ADR-006 shown as amended (v1.16). |
| v1.15 | 2026-11-07 | New section "Anticipated future updates"; the decisions table brought up to date (ADR-006 v1.18, ADR-007 v1.13, ADR-008 v1.27, ADR-009 v1.3). |
| v1.16 | 2026-11-07 | Editorial revision for publication. |
| v1.17 | 2026-11-07 | Folder map lists the requirements documents `DOC-OVW-019` and `DOC-OVW-020`. |
| v1.18 | 2026-11-07 | `DOC-OVW-001` retired; the folder map says so. |
| v1.19 | 2026-11-07 | Motivation section moved here from the README. |
| v1.20 | 2026-11-07 | ADR-010 and the `.github` folder added to the decisions table and the folder map. |

### History of the README (before this guide existed)

| Version | Date | Summary |
|---------|------|---------|
| v2.1 | 2026-10-24 | Round 2 results reflected in the status table. |
| v2.2 | 2026-10-24 | Power-profile A/B result reflected in the status table; amendment record given a proper table. |
| v2.3 | 2026-10-24 | Model 6 (K2 Horizon 0.9B, ADR-004 v1.4) added to the models table and the decisions table. |
| v2.4 | 2026-10-24 | Mini-checkpoint: models 3 to 6 downloaded and verified, model 6 benchmarked, large-model benchmark script added to the common tasks. |
| v2.5 | 2026-10-24 | Gemma 4 benchmark results reflected in the status and models tables. |
| v2.6 | 2026-10-24 | Qwen benchmark results and the K2 MoVA loading finding reflected in the status and models tables. |
| v2.7 | 2026-10-24 | Mini-checkpoint 3: all three large models benchmarked, K2 MoVA override and cache finding reflected in the status, models and common-tasks sections. |
| v2.8 | 2026-10-24 | Added `docs/overview/` and the design intention document `DOC-OVW-001` (draft) to the folder map. |
| v2.9 | 2026-10-24 | Combined power-profile A/B result reflected in the status table. |
| v2.10 | 2026-10-24 | Wrap-up: informal `llama-server` use recorded in the status table; a by-hand example added to the common tasks. |
| v2.11 | 2026-10-27 | Project name LLTH applied throughout; `DOC-OVW-001` is now active. |
| v2.12 | 2026-10-27 | `DOC-OVW-001` is the release-day text and is a draft until release. |
| v3.0 | 2026-10-27 | The README became the release-day text of the former design intention (`DOC-OVW-001`, v3.8). Its working content (status, folder map, models, common tasks, decisions, rules) moved to this guide. |

### History of the design intention (`DOC-OVW-001`, now the README)

| Version | Date | Summary |
|---------|------|---------|
| v1.0 | 2026-10-24 | Initial draft. Written from the designer's statement of purpose (a system optimised for constrained hardware, released free and open source) and the project's measurements to date. |
| v1.1 | 2026-10-27 | Project name is LLTH (Liberated Local Thinking Harness), applied throughout. Recorded the licence intention (free, patent-retaliation condition, Apache-2.0 fits; not yet decided). Updated the open questions. |
| v1.2 | 2026-10-27 | Review pass. Licences of the six models checked against the model cards and recorded under Principle 1 (all Apache-2.0; Gemma 4 not under Google's Terms of Use). Added thinking control to the intended shape. Softened the transfer claim, labelled the device-ownership claim as an observation and brought the status up to 2026-10-27. |
| v1.3 | 2026-10-27 | Licence intention split: Apache-2.0 for code, CC BY-NC 4.0 for documentation and benchmark data (free, not for commercial use or sale); models keep their own licences. Open question updated. |
| v1.4 | 2026-10-27 | Benchmark data moved from CC BY-NC 4.0 to CC BY 4.0 (open reuse with credit); documentation stays CC BY-NC 4.0. Open question on the prose and data boundary added. |
| v2.0 | 2026-10-27 | Reviewed and approved by the designer; status set to active and canonical. No change to content. |
| v2.1 | 2026-10-27 | Opening rewritten in the designer's words: free, open-source, personal and local, independent of cloud APIs and subscriptions, built from the constraint of an ordinary consumer laptop on open weights. The Problem section now opens with the cloud-dependence problem. "Owner" replaced by "designer" throughout. |
| v2.2 | 2026-10-27 | Opening paragraph rewritten in plain language. Accuracy pass: usable GPU memory corrected from 5.7 to 5.6 GiB (5,746 MiB); the 18.6 tokens/s example now names its settings (`-ub 64`, `q4_0` cache); the cloud-use and tested-on-larger-machines statements are labelled as the designer's observation; the claim about every owner of a 6 to 8 GB GPU narrowed to what was measured; "filter" dropped from the independence claim because models carry their publishers' built-in refusals. |
| v3.0 | 2026-10-27 | Rewritten as the release-day text, in the present tense and for the public, to be published only when it is true. Full scope: the installer for non-expert users with customisation, the steward and specialists, the router, thinking control and the hardware-aware layer. Removed the status section, the open questions and the internal references. Returned to draft until release. |
| v3.1 | 2026-10-27 | The problem section rewritten from the designer's question (how can a wholly independent, smart and accurate AI run on a small GPU without subscriptions or third-party limits), with a definition of independence, the four measured findings kept, and the observation about cloud use stated in the first person. |
| v3.2 | 2026-10-27 | Why this is worth solving rewritten from the designer's own reasons: independence and data control as hardware ages, public availability, less technological waste, low cost. The device-flexibility, hard-constraint and orchestration points were removed from this section. |
| v3.3 | 2026-10-27 | What LLTH is rewritten as a single solution in eight parts, in plain language: fully local, no layer between the user and the engine, models chosen for openness, a fleet of different sizes, the right model for each request, tuning to the machine, an easy and customisable installer, and documented, reproducible testing. |
| v3.4 | 2026-10-27 | Design principles rewritten in plain language and kept as seven; each is an intentional design principle that the rest of the document shows in practice. |
| v3.5 | 2026-10-27 | What LLTH is rewritten from the user's perspective as six short paragraphs: models and fleet combined, routing and tuning combined, and documentation, decisions and honesty combined. The Design principles section removed; what it said that was not already covered is now in the last paragraph. |
| v3.6 | 2026-10-27 | The reference machine changed from a line of specifications to a table, with a closing sentence naming it as the designer's aging laptop and the source of every result. |
| v3.7 | 2026-10-27 | Release and licences reordered: the free open-source statement is limited to the code, the licence table comes first with the emphasis that each kind of content has its own licence, and the release contents follow. Models and llama.cpp are separate rows. |
| v3.8 | 2026-10-27 | Limits section removed. |
| v3.9 | 2026-10-27 | The text became the project README (v3.0), without "How it is judged" (moved to the developer guide, `DOC-OVW-004`) and without this record (moved to the same guide). `DOC-OVW-001` is now a pointer to the README. |
