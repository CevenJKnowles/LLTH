---
id: ADR-012
title: Code Checks in Continuous Integration
type: adr
status: accepted
version: v1.6
canonical: true
scope: llth
audience:
  - developer
  - maintainer
  - operator
created: "2026-11-08"
updated: "2026-11-08"
tags:
  - llth
  - adr
  - ci
  - testing
  - python
relationships:
  related:
    - ADR-006
    - ADR-010
    - ADR-011
    - DOC-GOV-001
provenance:
  - human
---

# ADR-012 — Code Checks in Continuous Integration

## Status

Accepted (v1.6)

---

## 1. Context

ADR-010 checks the documentation of the repository on every push and pull request, and leaves code checks to a later ADR because the repository held no code. The Python package of ADR-011 now exists. A check on every push and pull request keeps the code importable, consistently formatted and tested as it changes and as others contribute.

GitHub-hosted runners have no GPU and no models. The checks therefore cannot start a model or measure speed.

### Decision drivers

- **No GPU, no model, no network** beyond installing packages. The checks must run on a hosted runner.
- **Read-only and secret-free** (ADR-010 §1).
- **Lean.** Development tools are never installed for users, and a third-party action is added only when it is needed (ADR-010 §4).
- **Reproducible.** The checks install the versions in `uv.lock` (ADR-011 §2).
- **Contributors receive the same checks as the maintainer.**

### Rationale

Most of the logic worth testing does not need a model: the settings and expert loaders, process handling, mode switching and its loading state, and the streaming of a reply. Each can run against a stand-in process or a stand-in server written in the test. What needs the real hardware stays a manual run: the real swap time, the real chunk format and whether `llama-server` stops generating when a connection closes. Those results belong in the build log (`DOC-IMPL-002`).

---

## 2. Decision

### §1 Triggers and permissions

The code checks run on a GitHub-hosted Ubuntu runner on every push to `main` and every pull request. The workflow has `contents: read` permissions only and uses no secrets.

### §2 What runs

A run fails if any step fails:

1. Install the environment from `uv.lock`, including the development dependency group.
2. Check formatting and lint with ruff (§6).
3. Run the tests with pytest (§5).

### §3 Tests

- Tests live in `tests/` at the repository root, in files named after the module they test.
- Tests start no model and open no connection except to `127.0.0.1`. They write only to a temporary folder.
- A stand-in process (a short-lived command) replaces `llama-server` for process handling. A stand-in HTTP server replaces it for streaming and readiness.
- The first tests cover the behaviour of the modules of ADR-011 §1 that needs no hardware.

### §4 Development dependencies

Test and lint tools are listed in a development dependency group in `pyproject.toml`, never under `dependencies`. They are not installed for users.

### §5 Test framework

The tests use pytest, a development dependency (§4).

### §6 Lint and format tool

Formatting and lint use ruff, a development dependency (§4), with its default line length of 88.

### §7 Python versions

The checks run on every Python minor version from the minimum of ADR-011 §2 up to the newest stable release. The versions are listed in the workflow.

### §8 Installation in the workflow

The workflow installs uv with `pip` into a virtual environment on the runner, then runs `uv sync --locked`. It adds no third-party action beyond `actions/checkout` (ADR-010 §4).

### §9 Workflow file

The code checks are a new workflow, `.github/workflows/code-check.yml`. The documentation check of ADR-010 stays unchanged.

---

## 3. Consequences

### Positive

- A change that breaks an import, a format rule or a tested behaviour fails visibly.
- Contributors receive the same checks as the maintainer.
- The checks need no GPU and no secrets.

### Negative

- Tests with stand-ins check the code's logic, not the real `llama-server`. A stand-in can differ from the real server.
- The development dependency group adds tools to maintain.
- The workflow runs once for every supported Python version, so a run takes longer.

### Implementation notes

- The workflow and the first tests are written after this ADR is accepted.
- The first run on the current tree must pass.

### Related

- ADR-006 — Interface, a Local Web Page with an Expert Menu
- ADR-010 — Documentation Checks in Continuous Integration
- ADR-011 — Python Project Layout, Tooling and Dependencies
- DOC-GOV-001 — ADR policy

---

## 4. Non-goals

- Running a model, a benchmark or a build of llama.cpp in continuous integration.
- GPU runners.
- A minimum test coverage figure.
- Static type checking.
- Deployment, releases or publishing.

---

## 5. Options considered

### Test framework

- **Option A — pytest (chosen).** The common standard; simple fixtures for temporary folders and stand-ins. A development dependency.
- **Option B — `unittest`.** Not chosen: standard library, no dependency. More code for the same tests.

### Lint and format tool

- **Option A — ruff (chosen).** One development dependency for lint and format.
- **Option B — no tool; a compile check only.** Not chosen: no dependency, and no style enforcement.

### Python versions

- **Option A — the minimum and the version in use.** Not chosen: a break on a version between them goes unnoticed.
- **Option B — 3.12 only.** Not chosen: faster; a break on newer versions goes unnoticed.
- **Option C — every supported minor version (chosen).** The most coverage and the longest run.

### Installation in the workflow

- **Option A — `pip install uv` in a virtual environment, then `uv sync --locked` (chosen).** Uses the lock file with no extra action.
- **Option B — the `astral-sh/setup-uv` action, pinned by commit SHA.** Not chosen: one more third-party action (ADR-010 §4).
- **Option C — `pip install` the development group without uv.** Not chosen: it ignores `uv.lock`.

### Workflow file

- **Option A — a new `code-check.yml` (chosen).** Separate status for documentation and code; each can fail alone.
- **Option B — a second job in `docs-check.yml`.** Not chosen: one file; one status for both.

---

## 6. Amendment record

| Version | Date | Summary |
|---------|------|---------|
| v1.6 | 2026-11-08 | Drafted and reviewed, accepted by the designer. |
