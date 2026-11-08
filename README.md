# LLTH: Liberated Local Thinking Harness

[![Documentation check](https://github.com/CevenJKnowles/LLTH/actions/workflows/docs-check.yml/badge.svg)](https://github.com/CevenJKnowles/LLTH/actions/workflows/docs-check.yml) ![Licences: Apache-2.0, CC BY-NC 4.0, CC BY 4.0](https://img.shields.io/badge/licences-Apache--2.0%20%7C%20CC%20BY--NC%204.0%20%7C%20CC%20BY%204.0-blue) ![Maturity: alpha](https://img.shields.io/badge/maturity-alpha-orange)

LLTH, the **Liberated Local Thinking Harness**, is a free, open-source system for running open-weight language models entirely on the user's own computer, on ordinary consumer hardware. It is private by design: data stays on the machine, there is no cloud service or subscription, and no provider can change, slow down or withdraw it.

## Status

Built and measured: llama.cpp, six open-weight models, a speed benchmark and a blind quality test. In progress: the interface (the server code is written; the page is not, and nothing has run with a real model). Designed, not built: storage and memory, document intake and export (ADR-005 to ADR-009). No installer exists.

## Purpose

The question the project answers: how can a wholly independent, accurate AI run on a computer with a small GPU, without subscriptions or limitations from third parties? Independent means that nothing depends on a service that someone else runs: the models, the software and the settings are on the user's machine.

The reference machine is the designer's laptop with 6 GB of GPU memory. Everything in the project is shaped by what that machine can and cannot do. A larger machine is a bonus, not an assumption.

## Results so far

All six models were measured on the reference machine, for speed with `llama-bench` and for answer quality in a blind test of 20 prompts.

| Model | Generation at 8K context (tokens/s) | Quality mean (1 to 5) | Median time to answer |
|---|---|---|---|
| K2 Horizon MoVA 36B-A4B | 9.9 | 3.75 | 264 s |
| Qwen3.6-35B-A3B (thinking) | 18.2 | 3.45 | 329 s |
| Gemma 4 26B-A4B | 23.6 | 3.30 | 138 s |
| K2 Horizon 7B | 23.6 | 3.15 | 59 s |
| K2 Horizon 3.7B | 33.9 | 3.10 | 33 s |
| K2 Horizon 0.9B | 100.2 | 1.80 | 12 s |

Speeds use the `q8_0` cache, except the 7B with `q4_0`. Quality comes from one scorer and 20 prompts, so differences under about 0.2 are not meaningful. Qwen3.6 without thinking scored 2.70 in 30 s. The full tables, conditions and failures are in [`DOC-IMPL-006`](docs/implementation/DOC-IMPL-006-benchmark-results-overview.md) and [`DOC-IMPL-010`](docs/implementation/DOC-IMPL-010-quality-round1-results.md).

The measurements show three things:
- **A model that fits on paper can be slow in practice.** The 7B (5.2 GiB) on a card with 5.6 GiB usable generated 40 tokens/s with an empty context but only 4 to 6 at 16K with default settings, because the context cache pushed layers to the CPU. A smaller compute buffer (`-ub 64`) with the `q4_0` cache brought it to 18.6.
- **Context is not free, and its price differs by model.** The memory a conversation takes per token ranged from about 0.011 MiB to about 0.10 MiB, a factor of nine.
- **Defaults can fail outright.** The K2 Horizon MoVA model could not be loaded with the standard expert-offload flag until a specific tensor override was found.

## Design

- **Local only.** The server listens on `127.0.0.1`. Nothing is installed system-wide, and removing LLTH means deleting one folder (ADR-002).
- **No layer between the user and the engine.** LLTH runs llama.cpp directly, built from source, pinned to one commit and built for the GPU it runs on (ADR-001, ADR-003).
- **Open models.** Each model has open weights and a licence that allows free use, checked against the publisher's model card. Each file is verified against a published SHA-256 checksum (ADR-004).
- **Experts, not routing.** The user chooses an expert from a menu: Writing, Administration, Coding or Think. Each expert is a model with a reasoning effort. Writing and Administration use the K2 Horizon 3.7B at low and medium effort. Coding and Think use the K2 Horizon MoVA 36B-A4B at medium and high effort. Nothing routes requests automatically (ADR-005).
- **Documented decisions and evidence.** Each major choice is written down in a decision record (ADR) before the work starts and amended openly. The benchmarks keep their raw logs, conditions and failures, and [`benchmarks/MANIFEST.sha256`](benchmarks/MANIFEST.sha256) lists a checksum for every raw-evidence file.

## Repository

| Path | Contents |
|---|---|
| [`ADR/`](ADR/) | Architecture decision records and their index (`ADR-000-README.md`) |
| [`docs/overview/`](docs/overview/) | The developer guide (status, folder map, common tasks) and the requirements records |
| [`docs/architecture/`](docs/architecture/) | The project anatomy |
| [`docs/implementation/`](docs/implementation/) | Benchmark results, the quality test protocol, the known issues log and the build log |
| [`docs/governance/`](docs/governance/) | The ADR policy and the documentation standard |
| [`.github/`](.github/) | The documentation check that runs on every push and pull request (ADR-010) |
| [`benchmarks/`](benchmarks/) | Raw logs, per-prompt results, scripts and the checksum manifest |

Start with the [developer guide](docs/overview/DOC-OVW-004-developer-guide.md).

## The reference machine

| Part | Specification |
|---|---|
| Laptop | Acer ConceptD 7 (CN715-71) |
| Processor | Intel i7-9750H, 6 cores, 12 threads |
| Graphics card | NVIDIA RTX 2060 Mobile |
| Graphics memory | 6 GB (5,746 MiB usable) |
| Graphics features | Compute capability 7.5; no BF16, FP8 or FP4 |
| Main memory | 32 GB DDR4-2667 (about 24 GB available, no swap) |
| Storage | 1 TB NVMe |
| Operating system | Manjaro Linux |

Every result in the project is measured on this machine.

## Licences

LLTH is released to the general public. The code is free, open-source software, and **each kind of content has its own licence**:

| Content | Licence | Terms |
|---|---|---|
| Code (the harness, scripts) | **Apache-2.0** | Completely free to use, modify and redistribute, with an explicit patent grant that ends for anyone who sues over the work. |
| Documentation (the README, ADRs, guides and write-ups) | **CC BY-NC 4.0** | Free and stays free. Anyone may use it as a template or for inspiration, with credit, but not sell it or use it commercially. Code samples that appear inside documents follow the code licence. |
| Benchmark data (the raw logs and the result tables) | **CC BY 4.0** | Free to reuse for any purpose, including commercial, with credit, so that researchers and companies can cite and build on the measurements. |
| Models | Their own | Not part of the repository. Each is downloaded from its publisher and keeps its own licence. |
| llama.cpp | MIT | Built and called, not relicensed. |
