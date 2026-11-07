---
id: DOC-IMPL-007
title: Benchmark Logs and Scripts
type: implementation
status: active
version: v2.0
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
  - benchmarks
  - logs
  - reproducibility
relationships:
  related:
    - README
    - DOC-IMPL-006
    - ADR-004
provenance:
  - human
---

# Benchmarks

The raw evidence behind every number in the project: the logs of each benchmark run, the per-prompt results of the quality test, and the scripts that produced them. The results and what they mean are in `DOC-IMPL-006` and the documents it lists.

```
benchmarks/
  README.md
  MANIFEST.sha256
  prompts.md                 the frozen quality-test prompt set (DOC-IMPL-008)
  prompts-verification.md    its verification and labels (DOC-IMPL-009)
  speed/                     raw llama-bench logs
  quality/                   run folders, scoring, effort probes, labels
  swap-time/                 model swap time data
  scripts/
    speed/                   run wrapper, sweeps, exploration and profile tests, log summariser
    quality/                 test runner, blinding and tally
    models/                  model download scripts
```

## What is here

| Item | What it is |
|---|---|
| `speed/*.log` | One log per run, named by date, model and test (for example `2026-10-24_gemma-4-26b-a4b_depth-matrix.log`). Logs are appended to, never overwritten, and failures and stopped runs stay in them |
| `quality/<model>_<config>/` | The quality test (ADR-004 §5, `DOC-IMPL-017`): one folder per run with one JSON file per prompt, a run header and the resumed-run headers |
| `quality/scoring/` | Round 1 blind scoring: the sealed key, the designer's scores and the final score set, each with its revealed results (`DOC-IMPL-010`) |
| `quality/effort-probes/` | Reasoning-effort probes: one folder per model with one raw server response per prompt and effort (`<prompt>_<effort>.json`), the probe's own log (`probe.log`) and the probe script as run (`DOC-IMPL-015`) |
| `quality/labels.csv`, `quality/load-tests.log` | The designer's easy/hard labels and the load tests of the run configurations |
| `swap-time/` | Model swap time between the K2 3.7B and K2 MoVA: the watcher's event log (one JSON object per line) and the watcher script as run (`DOC-IMPL-016`) |
| `MANIFEST.sha256` | SHA-256 of every raw-evidence file in this folder |

## Reading a log

Each log is a sequence of blocks written by `scripts/speed/bench_wrap.sh`: a label, the start time, the exact command, the `llama-bench` result table, the peak GPU memory, temperature and free RAM during the run, and the end time. A block without result rows means the model did not load or the run was stopped by the safety limits (92 °C GPU temperature or 1,500 MiB free RAM).

To print every log as tables, from the project root:
```bash
python3 -I benchmarks/scripts/speed/summarize-benchmarks.py
```
Pass part of a log name (for example `round2`) to select logs.

## Integrity and edits after the runs

`MANIFEST.sha256` lists the SHA-256 of every raw-evidence file in this folder: the logs, the run folders, the scoring files, the probe data, the swap-time data, the scripts and `prompts.md`. To verify, from the project root:

```bash
sha256sum -c benchmarks/MANIFEST.sha256
```

Edits made after the runs:
- The logs were written with the machine's real folder paths, which were replaced by `$LLTH_HOME` on 2026-10-27. The same replacement was made in the run headers of the quality runs on 2026-11-05. No other field was changed.
- The runs used `prompts.md` with SHA-256 `8d5e4fa32e0285a8dd7423f2f9d3314da5983dfaf7f908be17fb6a017f732e1f`, recorded in each run header. The header of the file was edited on 2026-11-07. The 20 prompts are unchanged.
- On 2026-11-07 the logs moved to `speed/` and the scripts into `scripts/speed/`, `scripts/quality/` and `scripts/models/`. The paths inside the scripts were adjusted; the commands they run are unchanged. `quality_blind.py` is now v1.3: the sealed key `quality/scoring/key-quality-round1.json` stores the run folders as `$LLTH_HOME` paths, and the script resolves them.
- The titles of the two result files in `quality/scoring/` and two sentences in `quality/load-tests.log` were edited on 2026-11-07.
- The blind scoring sheet (the final answers under random labels) is not included. The answers are in the run folders and the label mapping is in the sealed key.

## Conditions and licences

Every result was measured on the reference machine described in the project README, with the conditions stated in each block. The scripts are licensed Apache-2.0 (`LICENSE`) and the logs CC BY 4.0 (`LICENSE-DATA`).

## Amendment record

| Version | Date | Summary |
|---|---|---|
| v1.0 | 2026-10-27 | Initial. |
| v1.1 | 2026-11-05 | Added the prompt set, the quality test, the scoring and the effort probes. |
| v1.2 | 2026-11-05 | Added `swap-time/`. |
| v1.3 | 2026-11-05 | Run headers of the quality runs sanitised to `$LLTH_HOME`. |
| v2.0 | 2026-11-07 | Restructured: logs in `speed/`, scripts grouped by purpose, one manifest, prompt verification record, integrity and edits section. |
