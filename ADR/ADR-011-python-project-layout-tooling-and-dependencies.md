---
id: ADR-011
title: Python Project Layout, Tooling and Dependencies
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
  - python
  - dependencies
  - build
relationships:
  related:
    - ADR-002
    - ADR-006
    - ADR-010
    - ADR-012
    - DOC-GOV-001
provenance:
  - human
---

# ADR-011 — Python Project Layout, Tooling and Dependencies

## Status

Draft (v1.0)

---

## 1. Context

ADR-006 decides that the interface is a FastAPI backend with one HTML file, and names FastAPI and an ASGI server as the dependencies it adds. The build began on 2026-11-07. It needs decisions that no accepted ADR makes: where the Python code lives, which tool creates and locks the environment, how dependencies are declared, and which dependencies exist beyond those of ADR-006. The designer took several of these decisions during the first build sessions (2026-11-07 and 2026-11-08). This ADR records them and marks the open ones as Proposed.

### Decision drivers

- **Lean dependencies** (ADR-006): every dependency is installed on the user's machine, so each one needs a reason.
- **Reproducible environments.** The same locked versions must install on the developer's machine, on a contributor's machine and in continuous integration (ADR-012).
- **No system Python** (ADR-006 §1): packages go into a virtual environment only.
- **A reply can be stopped.** The browser stops a reply by closing its connection (ADR-006 §6). The request from the app to `llama-server` must close with it, so that generation can stop.

### Rationale

A `src/` layout keeps the package out of the working directory's import path, so tests and the app use the installed package and an accidental import of unpackaged code fails. One tool (uv) creates the environment, resolves versions and writes a lock file, which replaces a separate virtual-environment tool, a requirements file and a resolver. For streaming a reply, the standard-library HTTP client blocks a worker thread; in a test with a stand-in server it kept the upstream request open after the browser disconnected. An asynchronous client closes the upstream request when the browser's request is cancelled.

---

## 2. Decision

### §1 Layout

- The Python package `llth` lives in `src/llth/`. `pyproject.toml` and `uv.lock` are at the repository root.
- The app starts with `python -m llth` (`src/llth/__main__.py`). The page is `src/llth/static/index.html` (ADR-006 §1).
- Each module has one job:

| Module | Job |
|--------|-----|
| `paths.py` | Builds every location. The only module that builds paths; other modules import names from it. |
| `experts.py` | Reads the expert files (ADR-005 §3). |
| `servers.py` | Reads the server settings; starts, stops and waits for `llama-server` (ADR-005 §4). |
| `chat.py` | Streams a reply from `llama-server`. |
| `app.py` | The web app: routes and the state it keeps. |
| `__main__.py` | Starts the app on the configured port. |

### §2 Tooling

- uv creates the environment and writes `uv.lock`. `uv.lock` is committed.
- The build backend is `uv_build`, with a version range in `pyproject.toml`.
- `requires-python` is `>=3.12`.
- The environment is never the system Python (ADR-006 §1).

### §3 Dependencies

- Direct dependencies are listed under `dependencies` in `pyproject.toml` without version limits. `uv.lock` records the resolved versions.
- The direct dependencies are:
  - `fastapi` and `uvicorn`, from ADR-006 §1.
  - `httpx`, from this ADR: the asynchronous HTTP client that `chat.py` uses to stream a reply from `llama-server`. When the browser closes its connection, leaving the request block closes the connection to `llama-server`. Whether `llama-server` then stops generating is checked in the first run with the real model (ADR-006 §6).
- The Python standard library covers everything else.

### §4 Adding a dependency (Proposed, P-1)

A new direct dependency is added only through an ADR that names it and gives the reason, as ADR-006 §1 and §3 of this ADR do. An ADR that adds one lists it in its own Decision section.

### §5 Entry point (Proposed, P-2)

The only entry point is `python -m llth`. The package declares no console script. A `llth` command belongs to the installer ADR.

---

## 3. Consequences

### Positive

- The environment is reproducible from `uv.lock`.
- Code under `src/` cannot be imported from the working directory by accident.
- Every dependency has a recorded reason.
- A cancelled reply closes the request to `llama-server`.

### Negative

- `httpx` and its own dependencies add to the runtime footprint, against "lean" (ADR-006).
- Dependencies without version limits can pick up a breaking release when the lock file is regenerated. Regenerating it is a deliberate step.
- Development needs uv. The build backend's version range needs maintenance.

### Implementation notes

- The repository already follows §1 to §3.
- ADR-006 §1 is not amended: it lists the dependencies that ADR adds, not every dependency the project may have.
- Tests and the lint tool are development dependencies, decided in ADR-012.

### Related

- ADR-002 — Native User-Space Install, No Docker, Localhost Only
- ADR-006 — Interface, a Local Web Page with an Expert Menu
- ADR-010 — Documentation Checks in Continuous Integration
- ADR-012 — Code Checks in Continuous Integration
- DOC-GOV-001 — ADR policy

---

## 4. Non-goals

- Installing LLTH for users, including a non-editable install and where a user's environment lives (installer ADR).
- Publishing the package to a package index.
- Vendoring dependencies or scanning them for vulnerabilities.
- Supporting Python versions below the stated minimum.

---

## 5. Options considered

### Layout

- **Option A — `src/llth/` (chosen).** Tests and the app use the installed package.
- **Option B — `llth/` at the root.** Not chosen: the package is importable from the working directory without being installed.

### Environment tool

- **Option A — uv (chosen).** One tool for the environment, the resolver and the lock file.
- **Option B — `venv`, `pip` and a requirements file.** Not chosen: no lock file, and the resolved versions are not recorded.

### Streaming client

- **Option A — `httpx` (chosen).** About ten lines; a cancelled request closes the connection.
- **Option B — the standard-library client.** Not chosen: it blocks a worker thread, and in a test with a stand-in server the request stayed open after the browser left.
- **Option C — asyncio streams with a hand-written HTTP/1.1 request and a chunked-reply parser.** Not chosen: more code to maintain than the dependency it replaces.

### P-1 — Adding a dependency

- **Option A — an ADR names each new dependency (proposed).** Every dependency is traceable to a decision.
- **Option B — a note in the feature's ADR amendment.** Same record, less ceremony.
- **Option C — no rule.** Not proposed: dependencies could grow unrecorded.

### P-2 — Entry point

- **Option A — `python -m llth` only (proposed).** The installer ADR decides on a command.
- **Option B — also a `llth` console script now.** The command would exist before the installer defines how it is found.

---

## 6. Amendment record

| Version | Date | Summary |
|---------|------|---------|
| v1.0 | 2026-11-08 | Initial draft. Records the layout, tooling and dependency decisions of the first build sessions. Two points are marked Proposed (P-1, P-2). |
