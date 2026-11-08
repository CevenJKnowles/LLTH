---
id: ADR-007
title: Storage and Memory, Directory Tree, Locations and Confirmation
type: adr
status: amended
version: v1.14
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
  - adr
  - storage
  - memory
  - architecture
relationships:
  related:
    - ADR-002
    - ADR-005
    - ADR-006
    - DOC-OVW-019
    - DOC-OVW-020
provenance:
  - human
---

# ADR-007 — Storage and Memory, Directory Tree, Locations and Confirmation

## Status

Amended (v1.14)

---

## 1. Context

ADR-006 (accepted) builds the interface and says that its saved settings (the last-used expert and the accessibility setting) depend on a storage decision. The designer also wants a memory setup in which projects and session notes are saved, and in which every expert works in the same place. This ADR decides where LLTH's files live, how they are arranged, who may change them and how, and how the user stays in control. The designer's requirements, in the designer's words, are in `DOC-OVW-020`; it is the brief for this ADR.

### Decision drivers

- **The user chooses where the files live** and how memory and documents are handled.
- **Independence and openness** (ADR-004): plain readable files in folders, not a hidden store, so that the user can see, open, edit, copy and delete what LLTH keeps.
- **One place for every expert:** all experts have the same access to one directory.
- **Control:** a model never changes a file on its own. The user decides, during a session, how much LLTH may do without asking.
- **ADR-002:** everything for the project lives in one folder, and removal is deleting that folder. A root the user has moved elsewhere has to fit that idea.
- **What the machine does for backups** (checked read-only on 2026-11-07): `/` and `/home` are separate btrfs subvolumes (`@` and `@home`) on one partition; the project is in `@home`. Timeshift is installed, but its configuration shows btrfs mode off, no backup device and every schedule off. Whether any snapshot exists is **unverified**, because listing needs root.

### Rationale

Plain folders and files fit the project's openness and the designer's wish to see and handle everything by hand. Putting the model's work behind LLTH's own code, with the user in charge of how much runs unasked, makes it possible to give every expert write and delete access without letting a model, or a document it reads, change a file silently. Because the user's files sit where the machine takes no snapshots, the design carries its own undo: a trash folder and a log.

---

## 2. Decision

### §1 The root, and where it lives

- LLTH's memory and storage files live under **one root folder**.
- **The root has a default location inside `$LLTH_HOME`, and the user may choose to move it** at installation. The name of the default folder is open.
- **A tiny pointer file kept beside the code holds the root's location and nothing else.** It is how the code finds the root when it has been moved. Everything else is read from `LLTH/settings/`.
- The root has exactly two parts, `LLTH/` and `user/`.

### §2 The directory tree

The two parts and the four user folders are the designer's; the folders below them are confirmed by the designer.

```
<root>/
├── LLTH/
│   ├── instructions/    what the experts are told; empty by default (ADR-005's optional field)
│   ├── experts/         one small file per expert (name, server, effort, description)
│   ├── memory/
│   │   ├── index.md     one line per memory, like a table of contents
│   │   └── ...          one file per memory, each with frontmatter
│   ├── sessions/        one note per session that belongs to no project, dated
│   ├── handoffs/        the note a new session reads first, for work outside any project
│   ├── settings/        saved settings, as readable JSON
│   ├── trash/           what LLTH replaced or deleted, so that it can be put back
│   └── logs/            what LLTH wrote or deleted, and when
└── user/
    ├── preferences/     about-me.md, style.md, defaults.md, templates/
    ├── projects/
    │   └── <project>/   PROJECT.md, HANDOFF.md, notes/, documents/, code/, outputs/
    ├── documents/       originals/, converted/, outputs/
    └── code/
        └── <name>/      README.md and the code
```

- **A project** is a folder that holds everything for one piece of work. Inside it, `documents/` has the same three parts as the root `user/documents/` (`originals/`, `converted/`, `outputs/`). Any expert can open any project.
- **The user may add their own folders** under `user/`, and LLTH can see them.
- **Where replaced or deleted files go:** `LLTH/trash/`, so that a replacement or a delete can be undone. The user can open and empty it like any folder.

### §3 Memory and session notes

- A **session note** records what happened in one session. A **memory** is a lasting fact that LLTH keeps across sessions.
- `user/preferences/` is what the user wrote about themselves (three plain files that every expert reads at the start of a session and the user can edit). `LLTH/memory/` is what LLTH noted on its own.
- Session notes and handoffs exist at two levels: inside a project (`notes/` and `HANDOFF.md`) and, for work outside any project, in `LLTH/sessions/` and `LLTH/handoffs/`.
- **Whether and when they are saved** follows the user's choice (§5 and §6).

### §4 Documents

- Documents are stored as **originals, converted files and outputs**, in the three folders of §2, in the project or at the root of `user/documents/`.
- **Originals are not destroyed.** LLTH stores the originals and the outputs in the user's directory, so that the user may add or delete as they like. This replaces the destruction of the original in `DOC-OVW-019` DI-5.
- An original and its converted files **share one name stem** (for example `2026-11-07-tenancy-agreement.pdf`, `.md` and `.json`), so that they pair easily. The converted `.md` has frontmatter for the text details and the `.json` holds the formatting data (`DOC-OVW-019` DI-2 and DI-3). How documents are read and converted is the intake ADR's decision.

### §5 Settings

- Settings are **plain readable files, JSON or similar, in `LLTH/settings/`**.
- The code reads each setting from there and from nowhere else, so that **a change to a setting file changes behaviour where it applies**.
- The settings include the last-used expert and the accessibility setting that ADR-006 needs, the options the user chose at installation for memory and documents, and how far automatic reaches (§6).
- **At installation the user chooses** where the files live (§1) and how memory and documents are handled: how far "automatic" reaches (§6), for example whether sessions may update memory automatically or must ask before saving.

### §6 Who changes what, and how

**All experts have the same access to one directory.** No expert has special rights. A model never touches the disk. LLTH's own code does all the writing, saving, moving and deleting. **LLTH's code never acts outside the root, with no exceptions**.

**Two ways, A and B**:
- **A. The user gives the commands** (for example `/save`, `/delete`, `/move`) and LLTH carries them out. It needs nothing special from a model and works with every expert.
- **B. The model proposes and the user approves.** The model writes a small, fixed-format block; LLTH reads it, shows exactly what would change, and acts after the user approves. Its reliability on the K2 models is **untested** and must be probed before it is relied on.
- **C. The model's built-in tool calling is left for a future version** (see Non-goals).

**Three kinds of change, and what "automatic" covers**:
- **Kind 1:** creating a new file or appending a note (memory and session notes, and filing a document, are of this kind).
- **Kind 2:** changing or overwriting an existing file. The old version goes to the trash first.
- **Kind 3:** deleting a file. It goes to the trash folder and leaves a line in the log.
- **Anything LLTH replaces or deletes goes to the trash first**, so that one undo covers both.
- **In manual,** LLTH asks before every change of every kind. **In planning,** LLTH shows a plan and acts after the user approves it. **In automatic,** LLTH acts without asking for the kinds of change the user allowed; the other kinds still ask.
- **The installation question sets how far "automatic" reaches.** The default is kind 1 only, so overwrites and deletes still ask. The user may widen it, up to all three kinds, at installation and later in `LLTH/settings/`, for memory and for documents separately.
- This also answers the risk of hidden instructions in documents: every session starts in manual, and automatic reaches only the kinds the user allowed (by default, new files and notes), so a document that tries to push an expert into overwriting or deleting a file meets a confirmation by default.

**The user decides, during a session, whether confirmations are automatic or manual, or planning.** The root rule, the log and the trash stay on in every setting: even when confirmations are automatic, a delete goes to the trash and leaves a line in the log. **The setting is shown clearly in the interface:** on the bottom line, with the label **"Confirm"** and the words `ask`, `auto` and `plan`: `Confirm: ask`, `Confirm: auto`, `Confirm: plan`, beside `Mode:`. **A change of setting shows at once on the bottom line and adds a short line to the chat, `Confirm: plan`.** Screen readers are told the change in full words, "Confirmation: planning", by that same chat line (a live region), so it is announced once and not twice. **While a change or a plan waits for approval, the prompt shows the instruction in Garnet, in the way "(Esc to stop)" is shown:** for a single change, `(Enter to approve, Esc to cancel)`; for a plan, `(Enter to run all, S to go step by step, Esc to cancel)`; and for each step while the user goes through a plan, `(Enter to do this step, S to skip it, Esc to stop)`.

**Planning:** LLTH works out what it would do and shows a plan, listing the files it would create, change or delete. It changes nothing until the user approves. **The user chooses whether to carry out the whole plan or to go through it step by step.** If a step fails during a plan, LLTH stops at that step, leaves the rest undone and tells the user; anything already changed is in the trash and the log. After a plan has run, the setting stays "plan", ready for the next plan.

**Every session starts in manual, whatever was chosen at installation.** The user switches to automatic or to planning from the prompt during the session (for example with a `/confirm` command), and a switch lasts only for that session. The installation choice does not set the starting setting; it sets how far automatic reaches.

### §7 Backups and snapshots

- This ADR does **not** rely on snapshots. The user's files sit in `@home`, which Timeshift is recorded as not covering, and its configuration shows nothing scheduled (see Context). The trash folder is the undo that LLTH provides, and the log is the record of what it did.
- A backup of the root is the user's responsibility, or something LLTH may offer in a later ADR. A root moved to another drive has different protection again.
- Whether any btrfs snapshot exists on the reference machine is unverified.

---

## 3. Consequences

### Positive

- The user sees, opens and edits everything LLTH keeps; nothing is hidden in a store.
- Every expert works on the same files, so the next mode finds the same notes and handoff.
- A model, or a document it reads, cannot change a file silently: LLTH's code does the work, the user sets how much runs unasked, and deletes are recoverable and logged.
- The user chooses where the files live, and moving them needs only the pointer file to change.
- The ADR-006 settings (last-used expert, accessibility) have a place, so that part of the interface can be built once this ADR is accepted.

### Negative

- **The user's files are not snapshotted** on the reference machine. LLTH therefore keeps the undo itself: anything it replaces or deletes goes to the trash first. The trash undoes only what LLTH itself changed; the log records changes but holds no copies.
- **Way B is untested on the K2 models.** Until it is probed, only way A (the user's commands) can be relied on.
- **The pointer file is a single point of failure:** if it is lost or wrong, the code cannot find a moved root.
- **Asking first slows work.** Automatic mode removes the check.
- **The trash grows,** faster because replaced files go there too, until the user empties it; this ADR does not decide how or when.
- **Storing originals** keeps sensitive documents on disk for as long as the user keeps them. This is the user's choice, but it removes the privacy of destruction that `DOC-OVW-019` DI-5 had.

### Implementation notes

- A short probe of way B on the K2 models, in the manner of the effort probes (`DOC-IMPL-015`), should come before any use of it.
- The place of the pointer file, the default folder name, and the file formats are chosen at build time.
- Each item in the trash keeps its original location, in its name or in the log, so that it can be put back.

### Related

- ADR-002 — Native User-Space Install, No Docker, Localhost Only (one folder; Timeshift note)
- ADR-005 — Fleet Selection, Roles and Category Profiles (experts as data; the optional instructions field)
- ADR-006 — Interface, a Local Web Page with an Expert Menu (the saved settings; the bottom line)
- `DOC-OVW-019` — Interface and document handling requirements (document intake; DI-5 replaced by §4)
- `DOC-OVW-020` — Storage and memory requirements (the brief for this ADR)

---

## 4. Non-goals

- How documents are read, converted, filed and exported (the intake and export ADRs).
- **Native tool calling by a model (way C).** Noted for a future version: it would need the K2 chat template's support to be verified, tests on the K2 models and its own ADR, and it would build on the same code as ways A and B. ADR-004 left tool use as a non-goal.
- Backups, snapshots and their schedules.
- The sharing and licensing of the user's files, which are the user's own.
- A database, an index service or any hidden store.
- Network storage and syncing between machines.
- Permissions per expert (all experts have the same access).
- The installer and its questions.

---

## 5. Options considered

### Option A — Plain folders and readable files under one root (chosen)
Matches the designer's request for a directory tree of readable files, and keeps the user in control.

### Option B — Everything inside `$LLTH_HOME`, in a fixed place
Not chosen: the designer wants the user to choose where the files live. A default inside `$LLTH_HOME` that the user may move covers both.

### Option C — A database for memory and notes
Not pursued: the designer asked for a directory tree and readable files, and a database would hide the files from the user's own editor and file manager.

---

## 6. Amendment record

| Version | Date | Summary |
|---------|------|---------|
| v1.11 | 2026-11-07 | Drafted and reviewed, accepted by the designer. |
| v1.12 | 2026-11-07 | Amended after ADR-009 (export): the tree gains `user/preferences/templates/`, for the user's export styles and other templates, wherever a template helps (designer). Its subfolders are decided when it is built. No other decision changed. |
| v1.13 | 2026-11-07 | Editorial revision for publication. |
| v1.14 | 2026-11-08 | §8 (left for the build) removed: it listed details not yet decided, which is not a decision. |
