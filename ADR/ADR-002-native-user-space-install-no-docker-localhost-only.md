---
id: ADR-002
title: Native User-Space Install, No Docker, Localhost Only
type: adr
status: amended
version: v1.2
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
  - adr
  - security
  - deployment
  - isolation
subordinate_to: ADR-001
provenance:
  - human
---

# ADR-002 — Native User-Space Install, No Docker, Localhost Only

## Status

Amended (v1.2)

---

## 1. Context

### Decision drivers

- Hard rules: no sudo and no system pip.
- The designer wants to know exactly where everything lives and be able to remove it by deleting one folder.
- The earlier Ollama setup was exposed to the network on 0.0.0.0.
- Timeshift snapshots `@` but not `@home`, so large model files should live under `@home`.

### Rationale

llama.cpp runs as the normal user. GGUF model files are data, not executable code. With the server bound to localhost, the remaining exposure is a parser bug triggered by a malicious model file, which careful model sourcing mitigates. Container isolation would reduce that residual risk but adds GPU-passthrough complexity and, with Docker, a root-run daemon.

---

## 2. Decision

### §1 Location

Everything lives under `$LLTH_HOME/`. The build is in `$LLTH_HOME/llama.cpp/build/`. Models are in `$LLTH_HOME/models/`, selected by setting `LLAMA_CACHE` in the launcher scripts (not in dotfiles).

### §2 Network

The server binds to `127.0.0.1` only (port 8080, always set explicitly with `--port 8080`), never `0.0.0.0`.

### §3 Isolation

No Docker and no system-wide installs. Models come only from official publishers or well-known quantisers.

---

## 3. Consequences

### Positive

- No system changes; removal is deleting one folder.
- No GPU passthrough complexity.
- Timeshift snapshots are not bloated by model files.

### Negative

- No container isolation. Mitigated by: normal-user execution, GGUF being data, localhost binding, reputable model sources.
- Updates are manual.

### Implementation notes

- Revisit this ADR (by amendment or superseding ADR) if unvetted community models become part of the workflow. The first option to consider then is a bubblewrap (`bwrap`) sandbox around `llama-server`.

### Related

- ADR-001 — llama.cpp as the Local Inference Engine

---

## 4. Non-goals

- Multi-user or network serving.
- Sandboxing of untrusted models (see Implementation notes).

---

## 5. Options considered

### Option A — Docker with nvidia-container-toolkit

More isolation, but more complexity, and the Docker daemon runs as root (membership of the `docker` group is effectively root access). Rejected for now.

### Option B — bubblewrap or firejail sandbox

Lightweight isolation without Docker's root daemon. Needs a package installed by the designer. Deferred; the recommended first step if the threat model changes.

### Option C — System-wide pacman/AUR package

Needs sudo and lags upstream. Rejected.

---

## 6. Amendment record

| Version | Date | Summary |
|---------|------|---------|
| v1.0 | 2026-10-23 | Initial |
| v1.1 | 2026-10-23 | Correction: §2 said 8080 was the default port. In build 11839 the default is 9931 (`llama-server --help`). The decision is unchanged: the server listens on 127.0.0.1 only, on port 8080, set explicitly with `--port 8080`. Verified read-only. |
| v1.2 | 2026-11-07 | Editorial revision for publication. |
