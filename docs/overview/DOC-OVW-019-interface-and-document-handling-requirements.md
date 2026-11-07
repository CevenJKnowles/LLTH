---
id: DOC-OVW-019
title: Interface and Document Handling, Requirements
type: overview
status: active
version: v1.0
canonical: true
scope: llth
audience:
  - developer
  - maintainer
  - operator
created: "2026-11-05"
updated: "2026-11-07"
tags:
  - llth
  - interface
  - requirements
  - documents
relationships:
  related:
    - ADR-005
    - ADR-006
    - ADR-007
    - ADR-008
    - ADR-009
    - DOC-OVW-020
provenance:
  - human
---

# Interface and Document Handling: Requirements

The designer's requirements for the LLTH interface, the experts, document intake and export. The decisions taken from them are in ADR-005 to ADR-009. Where a requirement and an ADR differ, the ADR governs.

---

## 1. Interface

| # | Requirement | Outcome |
|---|---|---|
| UI-1 | A terminal-style page, styled as a window inside a wrapper. Minimal visual stimulation; everything clear and simple. | ADR-006 §1, §2 |
| UI-2 | A hint line at the bottom of the screen shows the basic commands. | Changed: there is no hint line. The prompt placeholder reads "Type a message, or / for commands" and typing `/` lists the commands (ADR-006 §2, §3). |
| UI-3 | An overview with metrics: the context window and tokens. | ADR-006 §5 |
| UI-4 | Slash commands. `/mode` opens a menu for changing the expert. | ADR-006 §3 |
| UI-5 | The interface is intuitive. | Not tested with anyone other than the designer. |
| UI-6 | When the expert changes, a prompt tells the user what is happening and shows progress, for example `Loading Coding [██████░░░░] 9 s`. | ADR-006 §6 |

**Technical notes (verified).**
- `llama-server` reports prompt tokens, generated tokens and tokens per second for every reply. The context size is set at start (34,816 in the round 1 configuration). The context used across a conversation is the sum of the turns and is tracked by the interface.
- `llama-server` reports no loading percentage: `/health` returns "not ready" and then "ready". The progress in UI-6 is therefore time-based from the measured swap times (about 14 s to MoVA, about 6 s back to the 3.7B; `DOC-IMPL-016`) and held at about 95% until the server reports ready.
- A terminal look needs no framework: monospace text, two or three colours, a message area, an input line. The build is a FastAPI backend with one hand-written `index.html` (ADR-006 §1).

---

## 2. Experts

An expert is a model with a reasoning effort and an optional instructions field. The aim of an expert is focus: the user chooses a purpose and not a model.

- The list is extensible. Think stays, and more experts may be added.
- Instructions are a provision only. The field is optional and empty, and no expert has instructions.
- The order and wording of the `/mode` menu are decided later.

| Expert | Model | Effort |
|---|---|---|
| Writing | K2 Horizon 3.7B | low |
| Administration | K2 Horizon 3.7B | medium |
| Coding | K2 Horizon MoVA | medium |
| Think | K2 Horizon MoVA | high |

The split between Writing and Administration follows the effort probes (`DOC-IMPL-015`). The evidence for Administration is thin. The decision is ADR-005 §3.

**Open:** whether any expert needs instructions and what they would say; whether a user-added expert may use any model on disk or only the fleet.

---

## 3. Document intake

| # | Requirement | Outcome |
|---|---|---|
| DI-1 | The user hands documents (PDF and similar) to a single inbox folder, and LLTH files them in its working directory for projects and memories. | Superseded: there is no inbox. A document comes in by dropping it onto the window or with `/open` (ADR-008 §3). |
| DI-2 | Each document is read, parsed and converted to Markdown at intake, so that the model does not convert it again for every use. | ADR-008 §1, §5 |
| DI-3 | The `.md` file carries YAML frontmatter for the text metadata, and a JSON file beside it holds the formatting data, with pointers between them. | ADR-008 §5 |
| DI-4 | OCR for scanned PDFs with Tesseract. | Deferred to a later version (ADR-008 §4a). |
| DI-5 | After conversion the original is destroyed and only the conversion remains. The model displays the information it extracted and the user confirms it. | Superseded: originals are kept in the user's directory (ADR-007 §4, ADR-008 §7). The user still confirms the extracted text before a document is filed (ADR-008 §6). |
| DI-6 | Screenshots and audio are out of scope for now. | ADR-008 §8 |

---

## 4. Export and dependencies

| # | Requirement | Outcome |
|---|---|---|
| EX-1 | Basic administration tools, including export to PDF, DOC, ODT and HTML. | ADR-009 |
| EX-2 | Lean dependencies. LLTH is installed by users together with the two models and all dependencies. Compromises are accepted. | ADR-006 §1, ADR-008 §4, ADR-009 §2 |

The export stack decided on 2026-11-05 (ADR-009 §2):
1. Pandoc for DOCX, ODT and HTML.
2. Typst for PDF, as one small program that Pandoc can use as its PDF engine.
3. The browser's print-to-PDF as a fallback with no extra dependency.
4. LaTeX as an optional extra, not installed by default.
5. `.docx` instead of the old `.doc`. LibreOffice is left out.

Exports come from the converted Markdown, not from the original, so they will not reproduce the look of the original page. Licences are checked at release (ADR-008 §4).

---

## 5. Parked

- Permissions and system actions, such as an administrative assistant that plans and schedules on the system calendar. Out of scope for now.

---

## Amendment record

| Version | Date | Summary |
|---------|------|---------|
| v1.0 | 2026-11-07 | Initial. The designer's requirements of 2026-11-05 to 2026-11-07 with the outcome of each. |
