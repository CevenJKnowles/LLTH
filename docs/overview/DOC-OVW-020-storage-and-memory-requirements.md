---
id: DOC-OVW-020
title: Storage and Memory, Requirements
type: overview
status: active
version: v1.0
canonical: true
scope: llth
audience:
  - developer
  - maintainer
  - operator
created: "2026-11-07"
updated: "2026-11-08"
tags:
  - llth
  - storage
  - memory
  - requirements
relationships:
  related:
    - ADR-002
    - ADR-005
    - ADR-006
    - ADR-007
    - DOC-OVW-019
provenance:
  - human
---

# Storage and Memory: Requirements

The designer's requirements for LLTH's storage and memory. The decisions taken from them are in ADR-007. Where a requirement and the ADR differ, the ADR governs.

---

## 1. Requirements

| # | Requirement | Outcome |
|---|---|---|
| ST-1 | The user chooses, during installation, where LLTH's memory and storage files live. | ADR-007 §1 |
| ST-2 | During installation the user also chooses how memory and documents are handled, for example whether sessions update memory automatically or ask before saving. | ADR-007 §5, §6 |
| ST-3 | All experts have the same access to one directory and can write, save and delete in any project the user requires. | ADR-007 §6 |
| ST-4 | One root directory with two parts, `LLTH/` and `user/`. | ADR-007 §1 |
| ST-5 | `LLTH/` is structured for instructions, memories, handoffs and the like. | ADR-007 §2 |
| ST-6 | `user/` has `preferences/`, `projects/`, `documents/` and `code/`, each with sub-directories. | ADR-007 §2 |
| ST-7 | The directory tree is developed under the root. | The confirmed tree is in ADR-007 §2. |
| ST-8 | Originals are not destroyed after conversion. LLTH stores the originals and the outputs in the user's directory, which the user may add to or delete from. This replaces `DOC-OVW-019` DI-5. | ADR-007 §4 |

---

## 2. Further requirements

| # | Requirement | Outcome |
|---|---|---|
| SR-1 | The root has a default location inside `$LLTH_HOME`. The user may move it. | ADR-007 §1 |
| SR-2 | The user may add folders under `user/`, and LLTH sees them. | ADR-007 §2 |
| SR-3 | Sharing and licensing of the user's files are not LLTH's concern. | ADR-007, Non-goals |
| SR-4 | Settings are plain readable files (JSON) in `LLTH/settings/`. The code reads them from there only, so that a change to a file changes behaviour where it applies. A pointer file kept beside the code holds the root's location and nothing else. | ADR-007 §1, §5 |
| SR-5 | A memory is a lasting fact that LLTH keeps across sessions. A session note records what happened in one session. Preferences are written by the user, memories by LLTH. | ADR-007 §3 |
| SR-6 | A model never writes to the disk. LLTH's code does the writing, saving, moving and deleting, in two ways: **A.** the user gives the commands (`/save`, `/delete`, `/move`); **B.** the model proposes a change in a fixed-format block and the user approves it. Way B is untested on the K2 models. LLTH's code never acts outside the root. | ADR-007 §6 |
| SR-7 | The user decides, during a session, whether confirmations are manual, automatic or planning. Creating a new file or appending a note may be automatic if the user allows it. Overwriting asks first by default. Deleting asks first, goes to a trash folder and is logged. The root rule, the log and the trash apply in every setting. | ADR-007 §6 |
| SR-8 | The current confirmation setting, and any change of it, is clearly visible in the interface: `Confirm: ask`, `Confirm: auto` or `Confirm: plan` on the bottom line. | ADR-006 §5, ADR-007 §6 |

---

## 3. For future versions

- **Native tool calling by a model.** The model calls tools (write, save, delete, move) through the engine's built-in support instead of the fixed-format blocks of way B. Whether the K2 Horizon chat template supports it is unverified. It needs testing on the K2 models and its own ADR (ADR-007, Non-goals).
