---
id: DOC-GOV-001
title: ADR Policy
type: governance
status: active
version: v1.3
canonical: true
scope: llth
audience:
  - developer
  - maintainer
  - operator
created: "2026-10-23"
updated: "2026-11-07"
tags:
  - governance
  - adr
provenance:
  - human
---

# ADR Policy

## Purpose

ADRs (Architecture Decision Records) capture why a decision was made, so that a sub-optimal decision can always be traced to its origin and its reasoning. No structural change may be implemented without a corresponding accepted ADR. This is the ADR-first rule. It applies to every coding and app project, not only LLTH.

---

## Rules

**Rule 1 — ADR before implementation.** Create and accept an ADR before writing code, building, installing, configuring or choosing anything that affects: the inference engine or runtime stack; build flags and toolchain; model selection and quantisation; network exposure, security posture or isolation; data storage locations; or any change that alters the meaning of an accepted ADR.

**Rule 2 — No silent edits.** Once an ADR reaches `accepted` status, its decisions may not be quietly reworded. If a decision changes, increment the version, add an Amendment record entry, and update the body to the new decision. Wording-only corrections do not change a decision and share one "Editorial revision" row.

**Rule 3 — Supersession requires a new ADR.** If an accepted ADR is fully replaced, create a new ADR, mark the old one `superseded`, and add a reference to the new ADR in the old file's body.

**Rule 4 — The index is authoritative.** `$LLTH_HOME/ADR/ADR-000-README.md` (ADR-000) lists every ADR and its current status. Update it whenever an ADR is added or changes status.

**Rule 5 — Frontmatter on every document.** All documents follow DOC-GOV-002.

---

## Status lifecycle

| Status | Meaning |
|--------|---------|
| `reserved` | Number allocated for a planned ADR; no content yet |
| `draft` | Being written; not yet in force |
| `accepted` | Adopted and currently governing behaviour |
| `amended` | Governing current behaviour; one or more decisions revised — see Amendment record |
| `superseded` | Replaced entirely by a later ADR; no longer governing |

---

## File naming and location

ADRs live in `$LLTH_HOME/ADR/`. Filename pattern: `ADR-NNN-kebab-case-title.md`, where NNN is a three-digit zero-padded incrementing number. Version strings must not appear in filenames.

---

## Canonical ADR structure

The full template, including the frontmatter, is in DOC-GOV-002. Section order is fixed:

1. `## Status` (the status word and the current version, for example `Amended (v1.3)`)
2. `## 1. Context` (with `### Decision drivers` and `### Rationale`)
3. `## 2. Decision` (clauses as `### §1`, `### §2`)
4. `## 3. Consequences` (with `### Positive`, `### Negative`, `### Implementation notes`, `### Related`)
5. `## 4. Non-goals`
6. `## 5. Options considered` (optional; only when the choice was non-obvious or contested)
7. `## 6. Amendment record`

---

## Amendment record

| Version | Date | Summary |
|---------|------|---------|
| v1.0 | 2026-10-23 | Initial. |
| v1.1 | 2026-10-23 | Added `reserved` status (see DOC-GOV-002 v1.2). |
| v1.3 | 2026-11-07 | The Status section format; Rule 2 allows wording-only corrections in one row. |
