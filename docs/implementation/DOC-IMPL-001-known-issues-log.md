---
id: DOC-IMPL-001
title: Known Issues Log
type: implementation
status: active
version: v1.23
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
  - issues
  - log
  - maintenance
relationships:
  related:
    - ADR-003
    - DOC-IMPL-002
    - DOC-ARCH-001
provenance:
  - human
---

# Known Issues Log

## Purpose

A running list of known, non-urgent issues found while building and setting up LLTH, so they can be worked on later instead of being forgotten. Anything that blocks work or is a security problem does not belong here; it gets fixed or decided immediately through an ADR.

## How to use this log

- Add new issues at the end of the relevant section with the next `KI-NNN` number. Numbers are never reused.
- Severity is `low` for everything in this log by definition. If an issue becomes more serious, raise it with the designer and move it out.
- When an issue is fixed, move it to "Resolved" with the date and the document (ADR or log entry) that fixed it. Do not delete entries.
- Fixing an issue that changes the build, install or configuration needs an ADR (or an ADR amendment) first (DOC-GOV-001, Rule 1).

---

## Open issues

| ID | Found | Area | Issue | Impact | Suggested next step |
|----|-------|------|-------|--------|---------------------|
| KI-001 | 2026-10-23 | Build | `ccache` is not installed. Configure prints a warning about it. | Rebuilds are slower than necessary (a full rebuild was about 15 minutes). | Either the designer installs `ccache` with pacman, or set `GGML_CCACHE=OFF` to silence the warning. Either needs an ADR-003 amendment. |
| KI-002 | 2026-10-23 | Build | The source is pinned at commit `e1e3b2c40` (build 11839) and is one commit behind upstream (`36e36e63a`, Hexagon CEIL op, not relevant to this hardware). | None now. Over time the pin falls behind new model support. | Decide an update policy (for example "update before each new model family") and record it in an ADR. |
| KI-003 | 2026-10-23 | Build | CUDA 13.3 only accepts GCC 15 or older as host compiler. The build depends on `gcc-15`/`g++-15` and on `NVCC_CCBIN=/usr/bin/g++-15` set in `/etc/profile.d`. | If the `gcc-15` package is removed or upgraded away, the build breaks. | Keep the package. Revisit when a newer CUDA supports gcc 16. |
| KI-004 | 2026-10-23 | Build | Flash attention kernels were compiled only for the K/V types `f16-f16`, `q4_0-q4_0`, `q8_0-q8_0` and `bf16-bf16`. | Mixed cache types (for example `q8_0` K with `q4_0` V) are unavailable. | If wanted, rebuild with `-DGGML_CUDA_FA_QUANTS=...` and amend ADR-003. |
| KI-005 | 2026-10-23 | Build | `HF_UI_VERSION` is read from the environment on every configure. Forgetting it falls back to `latest`, which moves over time. | A rebuild could silently fetch a different web UI. | Write a build script in `$LLTH_HOME/scripts/` that sets it and checks the archive exists (needs an ADR). |
| KI-006 | 2026-10-23 | Build | The build commands exist only inside ADR-003. There is no script. | Easy to mistype or forget a flag. | Same script as KI-005. |
| KI-007 | 2026-10-23 | Build | Four tiny deprecation-stub programs are built (`llama-llava-cli`, `llama-minicpmv-cli`, `llama-qwen2vl-cli`, `llama-gemma3-cli`). | Cosmetic; they only print a deprecation message. | Ignore, or disable if llama.cpp offers an option. Use `llama-mtmd-cli` instead. |
| KI-008 | 2026-10-23 | Security | The web UI archive checksum is fetched from the same Hugging Face bucket as the archive. | It guards against corruption, not a compromised bucket. Accepted in ADR-003 §8. | Optionally extract and read the archive, or build the UI from source if the risk assessment changes. |
| KI-009 | 2026-10-23 | System | Timeshift snapshots of `@` still hold about 60 GB of removed Ollama files. | Wasted disk space only (663 GB free). | The designer decides whether to wait for snapshots to age out or delete specific old ones. |
| KI-010 | 2026-10-23 | System | The current login session shows a nameless group id 958 (the removed `ollama` group). | Harmless. | Disappears after the next login. |
| KI-016 | 2026-10-23 | Verification | Tested so far: loading and benchmarking K2 Horizon 7B and 3.7B on the GPU (DOC-IMPL-012). Model 6 (dense, 0.9B) also runs (DOC-IMPL-012 section 4). MoE models and expert offload are tested with `llama-bench` (DOC-IMPL-013); `llama-server` and the web UI were started by hand with four models on 2026-10-25 (informal, not measured). Not yet tested: `--reasoning-budget`, `-hf` downloads. | The runtime is proven for the six models under `llama-bench` and informally under the server. | Covered by the remaining ADR-004 steps. |
| KI-019 | 2026-10-23 | Benchmarks | Thermal evidence is thin: the baseline sweeps logged only the peak GPU clock per run (up to 89 °C GPU temperature). The continuous clock log was added later. | Gate 3 (no throttling) cannot be proven from the first sweeps. | Use the new helper for all later runs; consider a long steady-load run (idea 10 in DOC-IMPL-006 §5). |
| KI-020 | 2026-10-23 | Governance | ADR-004 section 3 asks for a GPU start temperature of at most 50 °C, but the idle GPU is 43 to 56 °C and a 20-second pause leaves it at 47 to 66 °C. | The condition cannot be met as written. | Decide whether to amend it (for example at most 60 °C, or a longer pause). |
| KI-021 | 2026-10-23 | Models | IFM's 3.7B GGUF files are named `K2-Horizon-4B-*`. | Cosmetic; easy to mix up with another 4B model. | Keep the exact file names in ADR-004; no action. |
| KI-023 | 2026-10-24 | Thermals | Long-context runs on the large models run hot: 83 to 88 °C at 32K (K2 MoVA with `q4_0`: 88 °C, 4 °C below the 92 °C safety stop). | A longer or hotter run could trigger the safety stop or throttle; the within-run speed drop was not computed separately for these runs. | Keep the helper limits; consider the long steady-load run (idea 10 in DOC-IMPL-006 §5) and a within-run throttling check before ADR-005. Update 2026-11-05: the K2 3.7B reached 89 °C during 20 consecutive medium-effort steward prompts; the runner checks the temperature only before a run (`DOC-IMPL-010` §7.2). A cool-down between prompts is advisable for long runs. |
| KI-024 | 2026-10-24 | Benchmarks | In phase 1 of the combined power-profile A/B, two reading-speed measurements (Qwen 32K, 195 ± 91; K2 MoVA 32K, 126 ± 21) were far below the same tests in later phases, with one slow repetition each; K2 MoVA 8K reading also stepped down between phases 2 and 3. The cause is unknown (user interaction and the KDE file indexer are untested candidates; DOC-IMPL-014 section 2.4). | Reading-speed figures of the CPU-bound tests can contain slow repetitions; the helper logs neither system load nor per-repetition values, and the machine does not expose input idle time. | If outliers recur: log system load in `bench_wrap.sh`, use `llama-bench -o jsonl` for per-repetition values, and run a quiet-against-active test (idea 16 in DOC-IMPL-006 §5). Not planned.
| KI-025 | 2026-10-24 | Runtime | Defaults of `llama-server` (build 11839) are unsafe on this machine: `-c 0` loads the model's full context (131K to 524K tokens for K2), `-np` is automatic and splits the context between slots, the default port is 9931 (ADR-002 requires 8080), and `-cram` reserves up to 8192 MiB of host RAM for a prompt cache. | A bare `llama-server -m <model>` may fail to load, run out of memory, or listen on the wrong port; the 36B models are exposed to RAM exhaustion (no swap). | Always set `--host 127.0.0.1 --port 8080 -c <n> -np 1`, and `-cram 0` for the 36B models; record these in ADR-005 and the launcher scripts (DOC-IMPL-002, first server session).|

## Pending decisions (not defects)

| ID | Decision | Notes |
|----|----------|-------|
| PD-001 | Browser for the chat UI (Konqueror or Brave app mode) | Chat history is stored per browser, so pick one and stay with it. |
| PD-002 | Whether to run Ollama alongside llama.cpp | Not needed now. |
| PD-003 | Whether to add Open WebUI | Only if the built-in UI is not enough. |
| PD-004 | Where `LLAMA_CACHE` is set | Recommended: inside the launcher scripts, not in `~/.zshrc`. |
| PD-005 | A KDE `.desktop` launcher entry | Lives outside the project folders (`~/.local/share/applications/`), so it needs approval. |
| PD-006 | Fine-tuning approach | Local QLoRA only for roughly 3–4B dense models; MoE would need rented GPU time. Needs research and an ADR. |
| PD-007 | Container or sandbox isolation for unvetted models | Bubblewrap is the first option (ADR-002, Implementation notes). |
| PD-010 | Which exploration threads to follow first | The experiment list is in DOC-IMPL-006 section 5 |
| PD-011 | Publish LLTH as a git repository with an installer that downloads the chosen models | A later ADR (the designer decides). Shapes documentation and benchmark discipline now; see the README |
| PD-012 | **Closed 2026-11-07.** Routing architecture for the steward + specialists system | No automatic routing (ADR-005, accepted): the 3.7B's self-routing scored 45 to 50%, no better than always answering (`DOC-IMPL-010` §7), and the user chooses the expert from a menu. A routing ADR is needed only if automatic routing returns. |
| PD-013 | **Done 2026-10-24.** Power-profile A/B test (balanced against performance) with `profile-ab-test.sh` | Result: no meaningful speed difference (balanced +1.0% to +2.4%); earlier results stay valid. See DOC-IMPL-014 section 1 |
| PD-014 | **Partly done 2026-11-05.** Test K2's thinking controls (`--reasoning-effort`, `--reasoning off`, `--reasoning-budget`) and the steward configuration in `llama-server` | `reasoning_effort` low, medium and high probed on the K2 3.7B and K2 MoVA with seven frozen prompts (`DOC-IMPL-015`): effort changes the waiting time, not the tokens per second; the 3.7B at low effort suits plain-language tasks and fails on numbers and code. ADR-005 fixes the effort per expert from these probes (Writing low and Administration medium on the 3.7B; Coding medium and Think high on MoVA) and uses no system prompt. Open: `--reasoning-budget`, the 0.9B, and Qwen and Gemma with thinking off. The answer split is handled (KI-R14). |
| PD-015 | Research tracks R1 (quality–speed study) and R2 (small-architecture ablations): whether, when, and where | R2 would have its own project folder and ADR. See DOC-IMPL-006 section 5, ideas 11 and 12 |
| PD-016 | **Done 2026-10-24.** One combined power-profile A/B (ABBA) over models 3 to 6 | Result: balanced about 2% slower on average; only the fast, GPU-only 0.9B shows a difference clearly beyond the noise (3.5% to 4.6% slower); large models inside the noise. `performance` stays the benchmark condition. See DOC-IMPL-014 section 2 |
| PD-017 | Probe way B of ADR-007 §6 (the model proposes a change in a fixed-format block, LLTH shows it, the user approves) on the K2 models | Untested; must be probed, in the manner of the effort probes (`DOC-IMPL-015`), before it is relied on. Way A (the user's commands) works without it. |
| PD-018 | Trial install of the `tesserocr` wheel in a scratch virtual environment | Settles which Tesseract version the wheel bundles and whether it includes language data (ADR-008 §4a, `DOC-IMPL-011` §9). Needed only for the OCR update. Installing anything, even into a virtual environment, is the designer's decision. |
| PD-019 | Trial download of Typst and a trial export of real documents to DOCX, ODT, HTML and PDF | Settles Typst's release files by platform, offline package behaviour, PDF standards and how Pandoc drives it (ADR-009 §1 and Consequences). |
| PD-021 | Start the build: create the folders of ADR-007 (the root's default location inside `$LLTH_HOME`, its name and the pointer file), then the interface of ADR-006 | Needs the designer's confirmation of the full absolute paths first; the installer needs its own ADR. |
| PD-022 | Add the ask-first menu (File it, Use it in this chat, Cancel) and `/save` to ADR-006's interface text, and decide whether the ADR-008 amendments are accepted | ADR-008 is `amended` (v1.29) and its review is complete; ADR-006 v1.17 names the commands but has no wording for the menu. |

---

## Resolved

| ID | Found | Resolved | Issue | Resolution |
|----|-------|----------|-------|------------|
| KI-R01 | 2026-10-23 | 2026-10-23 | The shallow clone would have given build number `b1`. | Converted to full history; the server reports build 11839 (ADR-003 §7). |
| KI-R02 | 2026-10-23 | 2026-10-23 | The web UI archive for `b11839` does not exist, so the build fell back to `latest`. | Pinned `HF_UI_VERSION=b11838`; the archive is byte-identical to the one fetched as `latest` (ADR-003 v1.2). The remaining risk is KI-005. |
| KI-R03 | 2026-10-23 | 2026-10-23 | The ADR index file name (`README.md`) did not match the `ADR-NNN-` pattern. | Renamed to `ADR-000-README.md`; DOC-GOV-002 v1.3. |
| KI-R04 | 2026-10-23 | 2026-10-23 | Build time was unmeasured. | Measured: about 15 minutes for 433 steps (17:48 to 18:03 local time). |
| KI-R06 | 2026-10-23 | 2026-10-23 | DOC-GOV-002 was ambiguous about where the project README lives (formerly KI-015). | Root `README.md` files are exempt from naming and location (DOC-GOV-002 v1.4). |
| KI-R07 | 2026-10-23 | 2026-10-23 | ADR-002 stated that 8080 is llama-server's default port; the build's default is 9931. | ADR-002 amended to v1.1: port 8080 is set explicitly. |
| KI-R08 | 2026-10-23 | 2026-10-23 | The first depth sweep was launched from zsh, which does not split `$pair` into two words, so every command was malformed; no measurement was made. | The invalid log was deleted and the sweeps were rerun from bash scripts, now kept in `$LLTH_HOME/benchmarks/scripts/`. |
| KI-R09 | 2026-10-23 | 2026-10-23 | K2 Horizon 7B failed the 8K speed gate with the `q8_0` cache (14.8 tokens/s). | ADR-004 v1.1 added the `q4_0` cache variant; the 7B passes with it (23.6 tokens/s). |
| KI-R10 | 2026-10-23 | 2026-10-23 | The benchmark helper had no protection against overheating or running out of RAM. | The project copy now stops a run at 92 °C GPU or 1,500 MiB free RAM (ADR-004 section 4a); self-tested. |
| KI-R11 | 2026-10-23 | 2026-10-23 | The CPU governor was thought to be `powersave` during the first sweeps, with Chrome open. | The governor name is just how `intel_pstate` reports it; the designer had set the performance power profile before the benchmarks (energy preference `performance`, turbo on). Chrome has since been closed. The helper now logs the preference, turbo state and CPU frequency. See DOC-IMPL-006 section 2. |
| KI-R12 | 2026-10-23 | 2026-10-24 | A partial, unverified Gemma 4 download (1.39 GB of 14.44 GB) sat in the models folder (was KI-018). | The downloads of models 5, 4 and 3 were completed with `download-remaining-models.sh`; all three files were checked by size and by a recomputed SHA-256 against ADR-004 (DOC-IMPL-006 section 1). |
| KI-R13 | 2026-10-24 | 2026-10-24 | K2 Horizon MoVA 36B-A4B did not load with `-ncmoe` alone: a 5,723 MiB CUDA buffer was needed for the tensors `-ncmoe` does not move (was KI-022). | Resolved with `-ot 'attn_v_exps=CPU'` (flag-level, ADR-004 section 4a); the sweep and depth matrix then ran (DOC-IMPL-013 section 4). The override must be part of every launch configuration of this model (ADR-005). `bench_large_models.sh` v1.1 passes it through the `OT` variable. |
| KI-R14 | 2026-11-05 | 2026-11-05 | K2 Horizon replies at reduced reasoning effort were not split reliably by `llama-server`: the answer could sit in `reasoning_content` after `</ifm\|think>` with `content` empty, or the model wrote its working in `content` before the marker (was KI-026; `DOC-IMPL-015`). | Fixed in `quality_blind.py` v1.2, the one place answers are read: `final_answer()` recovers the text after the last marker when `content` is empty, and the routing rule reads only the text after the marker (`routed_answer()`). The runner still stores the raw fields unchanged (designer's rule: preserve model output). Tested: the 140 round 1 answers are unchanged; the 10 empty answers among the 42 probe replies are recovered; no marker is left in any routed text. Limit: the runner's reasoning-token count still includes an answer that came back inside the reasoning. |

---

## Withdrawn ids

KI-011, KI-012 and KI-013 were withdrawn by the designer on 2026-10-23: they concerned the author's tool configuration (global rules file, workspace file names, files left without frontmatter), which is outside the standard (DOC-GOV-002 v1.4, Exemptions). KI-014 and KI-015 were resolved (KI-R05, KI-R06). The ids are retired and are not reused.

---

## Amendment record

| Version | Date | Summary |
|---------|------|---------|
| v1.0 | 2026-10-23 | Initial: 16 open issues, 7 pending decisions and 4 resolved items from the first build session. |
| v1.1 | 2026-10-23 | Withdrew KI-011 to KI-013 as exempt; resolved KI-014 and KI-015; 11 open issues remain. |
| v1.2 | 2026-10-23 | Added KI-R07 (default port wording). |
| v1.4 | 2026-10-23 | Checkpoint 1: updated KI-016; added KI-017 to KI-021, PD-008 to PD-010 and resolved items KI-R08 to KI-R10. |
| v1.5 | 2026-10-23 | Added PD-011 (publication plan). |
| v1.6 | 2026-10-23 | Replaced KI-017 (governor) with resolved KI-R11: the performance power profile was active. |
| v1.7 | 2026-10-24 | Added PD-012 to PD-014 (routing architecture, power-profile A/B test, thinking-control tests). |
| v1.8 | 2026-10-24 | Added PD-015 (research tracks). |
| v1.9 | 2026-10-24 | PD-013 (power-profile A/B test) marked done with the result. |
| v1.10 | 2026-10-24 | Mini-checkpoint: KI-018 resolved as KI-R12 (downloads verified); KI-016 updated (model 6 runs); added PD-016 (combined power-profile A/B); PD-014 extended to model 6. |
| v1.11 | 2026-10-24 | Added KI-022 (K2 MoVA does not load with `-ncmoe` alone). |
| v1.12 | 2026-10-24 | Mini-checkpoint 3: KI-022 resolved as KI-R13; added KI-023 (thermal margin of long-context runs). |
| v1.13 | 2026-10-24 | PD-016 marked done with the result; added KI-024 (unexplained slow repetitions in phase 1 of the combined A/B). |
| v1.14 | 2026-10-24 | Wrap-up: KI-016 updated (server tried informally); added KI-025 (unsafe `llama-server` defaults). |
| v1.15 | 2026-11-05 | Added KI-026 (answer split at reduced reasoning effort); PD-014 marked partly done with the first effort probes. |
| v1.16 | 2026-11-05 | KI-026 resolved as KI-R14 (`quality_blind.py` v1.2 recovers the answer after the end-of-thinking marker); PD-014 updated. |
| v1.17 | 2026-11-05 | KI-023 updated (89 °C in the steward pass); PD-012 updated (self-routing result; the designer's direction: buttons instead of a router). |
| v1.18 | 2026-11-05 | PD-012 updated: closed by the ADR-005 draft (expert menu, no routing). |
| v1.19 | 2026-11-07 | ADR-005 accepted: PD-012 closed; PD-014 records the per-expert effort that ADR-005 fixes and that the steward prompt is not used. |
| v1.20 | 2026-11-07 | Added PD-017 to PD-021 (probe of way B, trial installs of tesserocr and Typst, the mockup update, the start of the build). |
| v1.21 | 2026-11-07 | PD-020: the chooser command is named `/open` (ADR-008 v1.23). |
| v1.22 | 2026-11-07 | PD-020 notes that the mockup v7 is built and awaits the designer; PD-022 added (ADR-006 wording for the ask-first menu; acceptance of the ADR-008 amendment). |
| v1.23 | 2026-11-07 | Editorial revision for publication. |
