---
id: ADR-000
title: README | ADR
type: adr
status: accepted
version: v1.57
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

# Architecture Decision Records (ADR)

This directory (`$LLTH_HOME/ADR/`) contains the canonical architecture and governance decisions for LLTH.

ADRs capture why a decision was made, so a sub-optimal decision can always be traced to its origin. No structural change may be implemented without a corresponding accepted ADR. Rules: `$LLTH_HOME/docs/governance/DOC-GOV-001-adr-policy.md`. Format and frontmatter: `$LLTH_HOME/docs/governance/DOC-GOV-002-documentation-standard.md`.

## Status vocabulary

| Status | Meaning |
|--------|---------|
| `reserved` | Number allocated for a planned ADR; no content yet |
| `draft` | Being written; not yet in force |
| `accepted` | Adopted and currently governing behaviour |
| `amended` | Governing current behaviour; one or more decisions revised — see Amendment record |
| `superseded` | Replaced entirely by a later ADR; no longer governing |

## Index

- **ADR-001 — llama.cpp as the Local Inference Engine**
  Path: `$LLTH_HOME/ADR/ADR-001-llama-cpp-as-local-inference-engine.md`
  Status: amended (v1.1)

- **ADR-002 — Native User-Space Install, No Docker, Localhost Only**
  Path: `$LLTH_HOME/ADR/ADR-002-native-user-space-install-no-docker-localhost-only.md`
  Status: amended (v1.2 — port wording corrected)

- **ADR-003 — llama.cpp Build Configuration**
  Path: `$LLTH_HOME/ADR/ADR-003-llama-cpp-build-configuration.md`
  Status: amended (v1.3 — build completed; UI fell back to `latest`)

- **ADR-004 — First-Round Model Selection and Benchmark Protocol**
  Path: `$LLTH_HOME/ADR/ADR-004-first-round-model-selection-and-benchmark-protocol.md`
  Status: amended (v1.8 — q4_0 cache variant, exploration phase, steward test, model 6 K2 Horizon 0.9B, the quality-test runner and run configurations, a largest-first run order, and a one-time no-execution exception for the round 1 Python check)

- **ADR-005 — Fleet Selection, Roles and Category Profiles**
  Path: `$LLTH_HOME/ADR/ADR-005-fleet-selection-roles-and-category-profiles.md`
  Status: amended (v1.5 — K2 3.7B steward and K2 MoVA specialist, four experts, no automatic routing; command `/mode`)

- **ADR-006 — Interface, a Local Web Page with an Expert Menu**
  Path: `$LLTH_HOME/ADR/ADR-006-interface-local-web-page-and-expert-menu.md`
  Status: amended (v1.18 — local web page, FastAPI and one HTML file, localhost only; the Confirm setting from ADR-007; document intake from ADR-008, with a drop or a file chooser; the export menu from ADR-009; depends on ADR-005)

- **ADR-007 — Storage and Memory, Directory Tree, Locations and Confirmation**
  Path: `$LLTH_HOME/ADR/ADR-007-storage-and-memory-directory-tree-and-confirmation.md`
  Status: amended (v1.13 — one root with `LLTH/` and `user/`, a movable default location, readable settings, expert access by the user's commands or approved proposals, manual, planning and automatic confirmation; depends on ADR-006)

- **ADR-008 — Document Intake, Conversion and Filing**
  Path: `$LLTH_HOME/ADR/ADR-008-document-intake-conversion-and-filing.md`
  Status: amended (v1.27 — dropping a file onto the window or a file chooser, a layered toolkit of free tools for .md, .docx, .pdf (text layer), .odt, .txt and .tex, OCR for scans an anticipated update, conversion to Markdown with a JSON formatting file, review before filing, originals kept; depends on ADR-007)

- **ADR-009 — Export, Formats and the PDF Engine**
  Path: `$LLTH_HOME/ADR/ADR-009-export-formats-and-pdf-engine.md`
  Status: amended (v1.3 — export to PDF, DOCX, ODT and HTML with Pandoc and Typst, the browser's print as a fallback; depends on ADR-007 and ADR-008)

- **ADR-010 — Documentation Checks in Continuous Integration**
  Path: `$LLTH_HOME/ADR/ADR-010-documentation-checks-in-continuous-integration.md`
  Status: accepted (v1.6 — one workflow and a standard-library script check the manifest, frontmatter, version agreement, identifiers, ADR structure, links, secrets and local paths)

## Amendment record

| Version | Date | Summary |
|---------|------|---------|
| v1.6 | 2026-11-05 | Added ADR-005 (draft) to the index. |
| v1.19 | 2026-11-07 | ADR-006 accepted (v1.12). |
| v1.20 | 2026-11-07 | Added ADR-007 (draft) to the index. |
| v1.31 | 2026-11-07 | ADR-007 accepted (v1.11). |
| v1.33 | 2026-11-07 | Added ADR-008 (draft) to the index. |
| v1.51 | 2026-11-07 | ADR-008 accepted (v1.18). |
| v1.54 | 2026-11-07 | Added ADR-009 (draft) to the index. |
| v1.55 | 2026-11-07 | Editorial revision for publication. |
| v1.56 | 2026-11-07 | Added ADR-010 (draft) to the index. |
| v1.57 | 2026-11-07 | ADR-010 accepted (v1.6). |
