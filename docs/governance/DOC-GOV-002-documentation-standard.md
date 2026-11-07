---
id: DOC-GOV-002
title: Documentation Standard
type: governance
status: active
version: v1.8
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
  - frontmatter
  - naming
  - templates
provenance:
  - human
---

# Documentation Standard

## Purpose

This is the documentation standard for this project. Every document gets YAML frontmatter, follows the naming rules below, and starts from a template in this file. The only exceptions are code and files that would break or be incompatible with frontmatter (source code, JSON, YAML config, CSV, lock files, and similar) and the project's root `README.md`.

---

## Frontmatter fields

Fields appear in exactly this order. Optional fields are omitted entirely when they do not apply; never leave them empty.

| Field | Required | Format and rules |
|-------|----------|------------------|
| `id` | yes | `ADR-NNN`, or `DOC-<AREA>-NNN` |
| `title` | yes | Short descriptive title |
| `type` | yes | One of: `adr`, `architecture`, `governance`, `implementation`, `overview`, `runtime` |
| `status` | yes | Lifecycle. ADRs: `reserved`, `draft`, `accepted`, `amended`, `superseded`. Other documents: `reserved`, `draft`, `active`, `complete`. `reserved` = id allocated for a planned document, no content yet |
| `version` | yes | `vMAJOR.MINOR`, for example `v1.0` |
| `canonical` | yes | `true`, or `pending` while `status` is `reserved` or `draft`. Becomes `true` when the document leaves draft |
| `scope` | yes | Project slug, for example `llth`; add a suffix for phases (`llth-phase-2`) |
| `audience` | yes | List. Values: `developer`, `maintainer`, `operator` |
| `created` | yes | Quoted `"YYYY-MM-DD"` |
| `updated` | yes | Quoted `"YYYY-MM-DD"` |
| `tags` | yes | List, lowercase kebab-case |
| `maturity` | optional | Confidence in the content, independent of `status`: `alpha`, `beta` or `stable` |
| `milestone` | optional | For example `M1.0`; omit for cross-phase documents |
| `subordinate_to` | optional | Parent ADR id |
| `amends` | optional | ADR id that this one amends |
| `supersedes` | optional | Id (and version) that this one replaces |
| `relationships` | optional | Map of lists of ids. Allowed keys: `related`, `parents`, `contrasts`. Use only the keys that apply |
| `provenance` | yes | List of who produced the document, one item per line. Default: `human` (the designer sets the conditions). Other values only when the designer says so |

Formatting rules:
- Scalar values are unquoted.
- Dates are always quoted.
- `audience`, `tags` and `provenance` are always lists, one item per line.
- `relationships` is a nested block: the key on one line, then each key with its ids as list items beneath it.
- Frontmatter holds short, machine-readable metadata only: no prose, examples, instructions or rubrics. Those belong in the body.
- No ad-hoc fields. A new field requires an amendment to this document.
- The `type` of a document is fixed by its area code (table below).

---

## Naming and location

| Document kind | Id | Filename | Location |
|---------------|----|----------|----------|
| ADR | `ADR-NNN` | `ADR-NNN-kebab-case-title.md` | `$LLTH_HOME/ADR/` |
| Project root README | none | `README.md` | the project root, for example `$LLTH_HOME/` |
| ADR index | `ADR-000` | `ADR-000-README.md` | `$LLTH_HOME/ADR/` |
| Architecture | `DOC-ARCH-NNN` | `DOC-ARCH-NNN-kebab-title.md` | `$LLTH_HOME/docs/architecture/` |
| Governance | `DOC-GOV-NNN` | `DOC-GOV-NNN-kebab-title.md` | `$LLTH_HOME/docs/governance/` |
| Implementation | `DOC-IMPL-NNN` | `DOC-IMPL-NNN-kebab-title.md` | `$LLTH_HOME/docs/implementation/` |
| Overview | `DOC-OVW-NNN` | `DOC-OVW-NNN-kebab-title.md` (project root `README.md` keeps its name) | `$LLTH_HOME/docs/overview/` |
| Runtime | `DOC-RUN-NNN` | `DOC-RUN-NNN-kebab-title.md` | `$LLTH_HOME/docs/runtime/` |

Rules:
- NNN is three digits, zero-padded, incrementing, never reused.
- Ids are stable. If a published file must be renamed, leave a redirect note at the old path.
- Titles in filenames are lowercase kebab-case.
- **Version strings never appear in filenames.**
- Folders are created when the first document of that area exists.
- A new `type` or area code requires an amendment to this document.
- The root `README.md` of a project is exempt from the naming, location and frontmatter rules: it keeps the name `README.md`, stays at the project root and carries no frontmatter, so that the repository page opens with its title.
- `reserved` documents are allocated an id and appear in the relevant index, so numbers are never reused.

---

## Exemptions

The standard governs the documents of this project. It does not govern the author's own working files outside the repository: session handoff files and working notes, generated or raw working files, and scratch files. These are exempt from the naming, id and location rules (and from frontmatter wherever it would be unhelpful or incompatible).

Everything in the project folder (`$LLTH_HOME/`) is fully governed. When unsure whether a file is a project document or a working file, treat it as a project document.

---

## Amendment records

- Every document ends with an amendment record table.
- A row records new content, a decision, or the correction of a value.
- Wording-only corrections, including typo fixes, share one "Editorial revision" row per release.
- The root `README.md` keeps its history in the developer guide (`DOC-OVW-004`).

---

## Templates

### ADR

```
---
id: ADR-NNN
title: Short Descriptive Title
type: adr
status: draft
version: v1.0
canonical: pending
scope: llth
audience:
  - developer
  - maintainer
  - operator
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
tags:
  - llth
  - adr
  - relevant-tag
milestone: MN.N              (optional)
subordinate_to: ADR-NNN      (optional)
amends: ADR-NNN              (optional)
provenance:
  - human
---

# ADR-NNN — Short Descriptive Title

## Status

Draft

---

## 1. Context

### Decision drivers

### Rationale

---

## 2. Decision

### §1 First decision clause

### §2 Second decision clause

---

## 3. Consequences

### Positive

### Negative

### Implementation notes

### Related

---

## 4. Non-goals

---

## 5. Options considered    (optional)

### Option A — Name

### Option B — Name

---

## 6. Amendment record

| Version | Date | Summary |
|---------|------|---------|
| v1.0 | YYYY-MM-DD | Initial |
```

### Any other document

```
---
id: DOC-<AREA>-NNN
title: Short Descriptive Title
type: architecture | governance | implementation | overview | runtime
status: draft
version: v1.0
canonical: pending
scope: llth
audience:
  - developer
  - maintainer
  - operator
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
tags:
  - relevant-tag
provenance:
  - human
---

# Short Descriptive Title

## Purpose

(body)

---

## Amendment record

| Version | Date | Summary |
|---------|------|---------|
| v1.0 | YYYY-MM-DD | Initial |
```

---

## Amendment record

| Version | Date | Summary |
|---------|------|---------|
| v1.0 | 2026-10-23 | Initial. Frontmatter required on every document. |
| v1.1 | 2026-10-23 | `canonical` is `true` once a document is out of draft and `pending` while it is a draft; templates updated. |
| v1.2 | 2026-10-23 | Optional `maturity` and `relationships` fields and a `reserved` status. Added stable-id/redirect, no-prose-in-frontmatter and no-ad-hoc-field rules. |
| v1.3 | 2026-10-23 | The ADR index file is named `ADR-000-README.md` (was `README.md`), so every file in `ADR/` follows the `ADR-NNN-` pattern. |
| v1.4 | 2026-10-23 | Added the Exemptions section (the author's tool configuration is outside the standard) and the root `README.md` exemption from naming and location. |
| v1.5 | 2026-10-23 | The id of a project's root `README.md` is `README`. `DOC-OVW-001` is no longer used by the README and is free for the first overview document. |
| v1.7 | 2026-10-23 | `provenance` is now a list. Templates updated. |
| v1.8 | 2026-11-07 | Added the rules for amendment records. The root `README.md` carries no frontmatter. Editorial revision for publication. |
