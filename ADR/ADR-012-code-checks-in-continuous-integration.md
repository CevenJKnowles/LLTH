---
id: ADR-012
title: Code Checks in Continuous Integration
type: adr
status: draft
version: v1.0
canonical: pending
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

Draft (v1.0)

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
2. Check formatting and lint (P-2).
3. Run the tests (P-1).

### §3 Tests

- Tests live in `tests/` at the repository root, in files named after the module they test.
- Tests start no model and open no connection except to `127.0.0.1`. They write only to a temporary folder.
- A stand-in process (a short-lived command) replaces `llama-server` for process handling. A stand-in HTTP server replaces it for streaming and readiness.
- The first tests cover the behaviour of the modules of ADR-011 §1 that needs no hardware.

### §4 Development dependencies

Test and lint tools are listed in a development dependency group in `pyproject.toml`, never under `dependencies`. They are not installed for users.

### §5 Test framework (Proposed, P-1)

The tests use pytest.

### §6 Lint and format tool (Proposed, P-2)

Formatting and lint use ruff, with its default line length of 88.

### §7 Python versions (Proposed, P-3)

The checks run on Python 3.12, the minimum of ADR-011 §2, and on Python 3.14, the version used in development.

### §8 Installation in the workflow (Proposed, P-4)

The workflow installs uv with `pip` into a virtual environment on the runner, then runs `uv sync --locked`. It adds no third-party action beyond `actions/checkout` (ADR-010 §4).

### §9 Workflow file (Proposed, P-5)

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
- The workflow runs on two Python versions, so a run takes longer.

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

### P-1 — Test framework

- **Option A — pytest (proposed).** The common standard; simple fixtures for temporary folders and stand-ins. A development dependency.
- **Option B — `unittest`.** Standard library, no dependency. More code for the same tests.

### P-2 — Lint and format tool

- **Option A — ruff (proposed).** One development dependency for lint and format.
- **Option B — no tool; a compile check only.** No dependency, and no style enforcement.

### P-3 — Python versions

- **Option A — 3.12 and 3.14 (proposed).** The minimum and the version in use.
- **Option B — 3.12 only.** Faster; a break on newer versions goes unnoticed.
- **Option C — every supported minor version.** The most coverage and the longest run.

### P-4 — Installation in the workflow

- **Option A — `pip install uv` in a virtual environment, then `uv sync --locked` (proposed).** Uses the lock file with no extra action.
- **Option B — the `astral-sh/setup-uv` action, pinned by commit SHA.** One more third-party action (ADR-010 §4).
- **Option C — `pip install` the development group without uv.** Ignores `uv.lock`.

### P-5 — Workflow file

- **Option A — a new `code-check.yml` (proposed).** Separate status for documentation and code; each can fail alone.
- **Option B — a second job in `docs-check.yml`.** One file; one status for both.

---

## 6. Amendment record

| Version | Date | Summary |
|---------|------|---------|
| v1.0 | 2026-11-08 | Initial draft. Five points are marked Proposed (P-1 to P-5). |
