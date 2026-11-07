---
id: ADR-006
title: Interface, a Local Web Page with an Expert Menu
type: adr
status: amended
version: v1.18
canonical: true
scope: llth
audience:
  - developer
  - maintainer
  - operator
created: "2026-11-07"
updated: "2026-11-07"
tags:
  - llth
  - adr
  - interface
  - accessibility
  - architecture
relationships:
  related:
    - ADR-002
    - ADR-004
    - ADR-005
    - ADR-007
    - ADR-008
    - ADR-009
    - DOC-OVW-019
    - DOC-IMPL-006
provenance:
  - human
---

# ADR-006 — Interface, a Local Web Page with an Expert Menu

## Status

Amended (v1.18)

---

## 1. Context

ADR-005 (accepted 2026-11-07) fixes two models, two server configurations and four experts, and says that the user chooses an expert from a menu. It builds nothing: "the interface, its server manager and its dependencies need ADR-006". This ADR is that decision.

The designer wrote the requirements on 2026-11-05 (`DOC-OVW-019` sections 1 to 5), then built and approved a mockup on 2026-11-07: `llth-mockup-v6-redesign.html`. It is plain HTML with no backend and fake replies. This ADR turns the approved mockup into decisions for the real interface.

### Decision drivers

- **The designer's priorities** (ADR-004): independence first, then the best quality the machine can reach, then speed.
- **Lean dependencies.** LLTH is installed by users together with the two models and every dependency; the tools should be "lean and fierce" (`DOC-OVW-019` EX-2).
- **Localhost only** (ADR-002): nothing is exposed to the network and nothing leaves the machine.
- **A window, not a web page:** the interface fills the whole browser tab and looks like a terminal window.
- **Intuitive above all** (`DOC-OVW-019` UI-5), and usable by people with other needs than the designer's.
- **The server's own limits** (verified, `DOC-OVW-019` §1 notes): `llama-server` reports tokens used, tokens generated and tokens per second for every reply, and reports readiness only as "not ready" then "ready", with no loading percentage.

### Rationale

A local web page served from `127.0.0.1` runs in any browser that is already installed, needs no desktop toolkit, and can be made to fill the tab so that it reads as an application. One hand-written HTML file with no framework and no build step keeps the interface small, readable and fully under the designer's control. The mockup shows that the design works with that technology: no feature in it needs more than HTML, CSS and a little JavaScript.

---

## 2. Decision

### §1 Form and technology

- The interface is a **local web page** served by a small **FastAPI** backend, with **one hand-written `index.html`** (HTML, CSS and JavaScript in the file). No JavaScript framework, no build step.
- **Nothing is loaded from outside the machine:** no CDN, no web fonts, no analytics, no external requests. The font stack is the system's monospace fonts (`ui-monospace`, DejaVu Sans Mono, Menlo, Consolas, `monospace`).
- The backend binds to **`127.0.0.1` only** (ADR-002), with its port set explicitly. The port is chosen at installation, with a default offered that the user can accept or replace, and it is not the `llama-server` port (8080). The default number is open. It is checked as free on the machine when it is offered.
- **New dependencies** (the only ones this ADR adds): the Python packages FastAPI and an ASGI server (uvicorn is the usual choice). They are installed in a virtual environment, never on the system Python.

### §2 Layout

The window fills the whole tab, with no page background around it. From top to bottom:

1. **Title bar**, with "LLTH" as a large heading.
2. **Chat**, the conversation. LLTH's replies are on the left and the user's messages on the right, right-aligned, as in a web chat. The chat opens with one line from LLTH: "What would you like to do today?". There are no speaker names above messages and no pipe beside them; screen readers still get the speaker.
3. **Command prompt**, the line where the user types: a `>` symbol, the field and a placeholder ("Type a message, or / for commands").
4. **One bottom line** with the overview (§5), under the command prompt.

There is no hint bar of commands and no success or "ready" messages. Warnings appear in the chat as a labelled box ("! Warning: …").

### §3 Commands and menus

- Typing `/` lists the commands and narrows the list as more is typed. Arrow keys choose, Enter selects, Esc closes. Every popup says "Press Esc to close". Esc also stops a reply (§6).
- **`/mode`** opens the expert menu (the command is `/mode`, not `/model`). **`/clear`** starts a new conversation. **`/help`** lists the commands. **`/accessibility`** opens the accessibility setting (§7). **`/confirm`** changes the Confirm setting for the session (§5 and ADR-007 §6). **`/open`** opens the browser's file chooser, a second way to bring a document in (§7a). **`/save`** saves a document that is attached to the chat (§7a and ADR-008 §6a). **`/export`** opens the export menu (§7b).
- Commands are data in one table, so that others (`/export`, `/files` and the like) can be added by the ADRs that need them. They are not part of this ADR.
- `/palette` exists in the mockup as a design aid (it lists every colour pairing with its live contrast ratio). It is not part of the product.
- The expert menu lists the experts of ADR-005 §3 in plain words with a one-line description, and says "(current)" or "(loads MoVA, about 14 s)" where the choice needs the other server. The order and wording of the entries are placeholders until the designer decides them.

### §4 Experts as data

The interface reads the experts from small text files, one per expert, as ADR-005 §3 says (name, server, reasoning effort, one-line description, optional empty instructions). Adding an expert changes no code. The interface sends the expert's `reasoning_effort` with every request.

### §5 Overview line

The bottom line reads `Context: 9.4k of 34.8k [bar] 27% 62 tokens per second Confirm: ask Mode: Writing`.

- The figures come from the server, not from an estimate. Context used is the sum of the prompt and generated tokens that `llama-server` reports for the conversation so far. The window size is the context set at server start (34,816 in the round 1 configuration, ADR-005 §4). Tokens per second is the server's own figure for the last reply. (The mockup estimates these from text length, with invented speeds.)
- Counts show in thousands (`k`) or millions (`M`) with one decimal. The percentage follows the bar.
- `Mode:` names the current expert.
- **`Confirm:` shows the confirmation setting for the session** (ADR-007 §6): `Confirm: ask` (manual), `Confirm: auto` (automatic) or `Confirm: plan` (planning). Every session starts at `ask`. A change of the setting shows at once on the bottom line and adds a short line to the chat, `Confirm: plan`; screen readers hear that line in full words, "Confirmation: planning", once (ADR-007).

### §6 Server manager

- The interface starts and stops the `llama-server` processes of ADR-005 §4, **one at a time**, as ADR-005 §3 and §4 assume and as the swap time was measured. At the round 1 settings the two servers do not fit together in the 5,746 MiB of usable VRAM: their measured peaks are 5,099 MiB (3.7B) and 4,963 MiB (MoVA) at 32K, and 3,771 and 3,187 MiB at depth 0 (`DOC-IMPL-012` §2 and `DOC-IMPL-013` §4.4); `DOC-IMPL-016` states the same. **Running both together was not tested** (see Implementation notes). Choosing an expert on the other server stops the first and starts the second.
- **While an expert loads**, the page shows `Loading Coding [bar] 9 s of about 14 s`. The bar is driven by time from the measured swap times (about 14 s to MoVA, about 6 s back, `DOC-IMPL-016`), held at about 95% until `/health` reports ready, because the server reports no percentage.
- **While the model is loading or replying**, the command prompt is read-only; typing is not queued. The prompt stays in focus, so its highlight stays on. **While a reply is being generated,** the prompt shows "(Esc to stop)" in Garnet, in place of the placeholder, the same words as the waiting line. A model load cannot be interrupted (it takes 2 to 15 s, and stopping it would leave no server running), so no instruction is shown while loading.
- **While the model is working, a waiting line shows in the chat**, for example `Thinking… 42 s (Esc to stop)`, counting up in whole seconds in the style of the loading line, and replaced by the reply when it arrives. The line, including "(Esc to stop)", is in Garnet and one size smaller than the chat text (15.75 px, the size of the placeholder). Replies can take minutes at high effort (the round 1 median for Think was 264 s, `DOC-IMPL-015`). Screen readers are told once when the wait starts and once when the reply is complete, not every second.
- **Esc stops a reply.** When no menu is open, Esc cancels the request to `llama-server`; a stopped reply stays in the chat with the warning "! Stopped". Whether `llama-server` stops generating when a request is cancelled has not been verified and is checked at build time.
- **While a change or a plan waits for approval** (ADR-007 §6), the prompt shows the instruction in Garnet, in the way "(Esc to stop)" is shown: for a single change `(Enter to approve, Esc to cancel)`; for a plan `(Enter to run all, S to go step by step, Esc to cancel)`; and for each step while the user goes through a plan `(Enter to do this step, S to skip it, Esc to stop)`.
- **Servers start with LLTH.** When LLTH starts, it starts the server for the last-used expert, so the first reply does not wait for a model load. The last-used expert is a saved setting kept in `LLTH/settings/`, as ADR-007 §5 decides. Closing the browser tab does nothing: the interface is the FastAPI program, and when that program quits it stops both servers. If no last-used expert is saved yet, it starts Writing, the first in the list. At start LLTH checks for a `llama-server` already running, for example one left by an earlier crash. If it is the right server for the expert, LLTH reuses it; if not, LLTH warns the user ("! Warning: another llama-server is running") and starts nothing and stops nothing. How LLTH tells whether a running server is the right one is not yet decided and is checked at build time.

### §7 Accessibility baseline

The mockup built these in; the real interface keeps them:

- Text sizes in `rem`, so they follow the browser's text-size setting. Base size 18 px; the overview line 14.4 px.
- The conversation is a live log that waits for a reply to finish before it is announced. The command prompt is a labelled combobox and the menus are listboxes that announce the selected item. Speaker names and status messages are kept as text for screen readers.
- Menu rows are at least 44 px high. Reduced-motion settings show a reply at once. Rules exist for forced colours.
- **A highlight box round the command prompt appears only after the Tab key is pressed, or when the system asks for more contrast or forced colours.** A mouse click switches it off again unless the system asks for it.
- A page cannot detect a screen reader or low vision directly, so there is **an `/accessibility` command that opens a setting the user chooses.** What it contains is not yet designed. The first option is to always show the highlight box round the command prompt. A saved accessibility setting is kept in `LLTH/settings/` (ADR-007 §5).
- **Colours** are the AAA neighbours of the designer's seven colours. They are CSS variables in one block, so that changing a colour needs no ADR. Several pairings are about 2.0:1 (Garnet text on Black Onyx, Black Onyx text on Garnet, Quartz on the Red Jasper warning badge) and the Garnet lines are under 3:1, so the interface does **not** claim WCAG conformance.

### §7a Documents (from ADR-008)

ADR-008 (accepted) decides how a document is read, converted and filed. The interface carries two parts of it:

- **There are two ways in** (ADR-008 §3). **The whole window accepts a dropped file,** and a **command** (`/open`) **opens the browser's own file chooser,** which works from the keyboard and with a screen reader. There is no inbox folder and no `/intake` command. Either way starts intake, which follows the steps of ADR-008.
- **The review screen** (ADR-008 §6) is part of the chat. It shows the text LLTH extracted. It asks whether the document belongs to a project or to `user/documents/`, and files it after the user confirms. The prompt shows the approval instruction in Garnet, as for any other change (§6).
- The dropped file is held in memory while the user reviews it and is discarded if the user cancels (ADR-008 §7).

### §7b Export (from ADR-009)

ADR-009 (accepted) decides how text becomes a file in another format. The interface carries the menu:

- **`/export` opens a menu** in the same style as the other menus ("Press Esc to close") with **PDF, DOCX, ODT and HTML**, and also Markdown, plain text and LaTeX source (ADR-009 §4, items 2 and 3).
- **What is exported** is chosen next: **LLTH's last reply, the full chat, or a document the user picks** from the project or from `user/documents/`.
- **The file is a new file in the `outputs/` folder** of the project or of `user/documents/` (ADR-007 §2), and it follows the Confirm setting like any new file (§5; ADR-007 §6): in manual LLTH asks first, and the approval instruction appears in the prompt (§6).
- **When the PDF engine is missing,** LLTH says so in the chat and offers the browser's print-to-PDF; the browser saves where the user chooses, which may be outside the root (ADR-009 §4, item 7).
- **Before exporting a script the embedded fonts lack,** LLTH warns the user (ADR-009 §4, item 9). LLTH makes **no claim that its PDF files are accessible** (item 8).

---

## 3. Consequences

### Positive

- The interface is small: one HTML file and a thin backend, readable end to end, with no build step to break.
- It runs in the browser that is already installed, with nothing downloaded and nothing sent out.
- Experts and commands are data, so the interface grows without code changes to its core.
- Real accessibility structure (live log, combobox, text sizes, keyboard use) is part of the base.

### Negative

- **The colour pairings do not meet WCAG** (§7). The dim text, labels and menu names will be hard to read for some users. The colours are CSS variables in one block.
- **Two new Python dependencies** (FastAPI and an ASGI server), small but not zero.
- **Starting the last-used expert needs a saved setting,** kept in `LLTH/settings/` (ADR-007), so the settings folder has to exist before that part of the build.
- **One server at a time.** Crossing between the 3.7B and MoVA experts means 6 to 14 seconds of loading (ADR-005); the interface can only show the wait.
- **The mockup has been tested only in headless screenshots.** Typing, the arrow-key menus, the loading bar, the focus detection and a screen reader have not been tried.
- **The highlight detection is a heuristic.** A keyboard user who never presses Tab and has no contrast setting will not see the box until they turn it on with `/accessibility`.
- **Storage is decided in ADR-007.** This ADR keeps nothing on disk itself: the saved settings (last-used expert, accessibility, how far automatic reaches) go to `LLTH/settings/`, and projects, session notes and memory follow the tree of ADR-007.

### Implementation notes

- **Open: could both servers run together?** At the round 1 settings the measured VRAM says no. It has not been tried with smaller settings (a smaller context, fewer layers on the GPU, more experts on the CPU), and every such change slows a model and needs new measurements. The system RAM is also tight: the two model files total 26.0 GB, about 24.5 GB of RAM is available and there is no swap (`DOC-OVW-004`).
- Tokens, timings and readiness come from `llama-server` (verified in `DOC-OVW-019` §1 notes); the exact fields are checked at build time.
- The mockup file is the visual reference. It lives outside the LLTH repository; where it should live is open.
- ADR-005 uses `/mode`.

### Related

- ADR-002 — Native User-Space Install, No Docker, Localhost Only
- ADR-004 — First-Round Model Selection and Benchmark Protocol
- ADR-005 — Fleet Selection, Roles and Category Profiles (accepted 2026-11-07; this ADR depends on it)
- ADR-007 — Storage and Memory, Directory Tree, Locations and Confirmation (accepted 2026-11-07; the saved settings and the Confirm setting)
- ADR-008 — Document Intake, Conversion and Filing (accepted 2026-11-07; the drop onto the window and the review screen)
- ADR-009 — Export, Formats and the PDF Engine (accepted 2026-11-07; the `/export` menu)
- `DOC-OVW-019` — Interface and document handling requirements, section 1
- `DOC-IMPL-016` (swap time)

---

## 4. Non-goals

- How documents are read, OCR'd, converted and filed (decided in ADR-008); this ADR holds only the drop onto the window and the review screen (§7a).
- How export works, its tools and formats (decided in ADR-009); this ADR holds only the menu (§7b).
- Permissions and system actions, calendar access (parked, `DOC-OVW-019` §5).
- Saving projects, session notes, conversations and memories to disk (decided in ADR-007).
- Network access, remote use, accounts or sign-in (localhost only, ADR-002).
- A light theme, other themes, or a settings page.
- Automatic routing between experts (ADR-005).
- Packaging and the installer.

---

## 5. Options considered

### Option A — FastAPI and one hand-written HTML file (chosen)
Small, readable, needs no build step, and runs in any installed browser.

### Option B — A terminal interface (a text UI in the console)
Rejected: the designer wants a window in the browser, and a console interface is harder to make accessible and to size for different eyes.

### Option C — A JavaScript framework with a build step
Rejected: it adds a toolchain and many dependencies for an interface that needs little, against "lean and fierce".

### Option D — A desktop wrapper (Electron or similar)
Rejected: a large download and a second runtime for a page the browser already shows.

### Option E — The built-in page of `llama-server`
Not pursued: it talks to a single server and has no expert menu, no swapping between the two servers and none of the designed behaviour. This was not tested in detail.

---

## 6. Amendment record

| Version | Date | Summary |
|---------|------|---------|
| v1.0 | 2026-11-07 | Initial draft, from the approved mockup (`DOC-OVW-019`). Not in the ADR-000 index. Decisions marked Proposed are for the designer to accept or change. |
| v1.1 | 2026-11-07 | Added to the ADR-000 index (v1.7). No change to the decisions. |
| v1.3 | 2026-11-07 | §6: the unsupported statement "the machine cannot hold both models" is replaced by the measured VRAM figures and the fact that running both was not tested; an open item for a possible test is added to the Implementation notes. No decision changed. |
| v1.4 | 2026-11-07 | §6: the starting and stopping of servers is no longer ambiguous or dependent on a saved setting. Servers start on demand (the first message loads the current expert), nothing is saved between sessions, and quitting the program stops both servers (designer's choice, option B). A Consequences line added for the first-reply wait. |
| v1.5 | 2026-11-07 | §6: the designer reversed the server start-up choice: servers start with LLTH, with the last-used expert (a saved setting), not on demand. Because the designer wants projects and session notes saved, Consequences and Non-goals now name a separate storage ADR as wanted and as a dependency of this one. Nothing else changed. |
| v1.6 | 2026-11-07 | §3 and §6: a waiting line ("Thinking… 42 s (Esc to stop)") while the model works, and Esc to stop a reply, both accepted by the designer (item 3 of the review). Cancellation by `llama-server` to be verified at build time. |
| v1.7 | 2026-11-07 | §6: the waiting line is Garnet and one size smaller than the chat text (designer). |
| v1.9 | 2026-11-07 | Five Proposed items settled by the designer: the port is chosen at installation; `/palette` is not part of the product; the overview figures come from the server; the prompt stays read-only and shows "Press Esc to interrupt" in Garnet while a reply is generated; an `/accessibility` command with a user-chosen setting is added (contents not yet designed). These are now the designer's decisions, not Proposed. |
| v1.10 | 2026-11-07 | §1: the port chosen at installation comes with a default option (designer). The default number is open. |
| v1.11 | 2026-11-07 | Item 6 of the review: Writing is the first expert when none is saved; a `llama-server` already running is reused if it is the right one and otherwise LLTH warns and touches nothing; the prompt and the waiting line both say "(Esc to stop)". All the designer's decisions; three Proposed items remain: the default port is checked as free, a model load cannot be interrupted, and the first `/accessibility` option is to always show the highlight box. |
| v1.12 | 2026-11-07 | Accepted by the designer after the step-by-step review (v1.3 to v1.11). Status `accepted`, canonical `true`. The three items still marked Proposed (default port checked as free; a model load cannot be interrupted; first `/accessibility` option) are accepted with the ADR. Parts that need the storage ADR (the saved last-used expert, the saved accessibility setting) cannot be built until that ADR is accepted. |
| v1.13 | 2026-11-07 | Amended after the acceptance of ADR-007: the `Confirm:` segment on the bottom line, the `/confirm` command, the short chat line when the setting changes, and the saved settings in `LLTH/settings/` are added; the dependency on a storage ADR is replaced by ADR-007. Status `amended`. The approval instructions in the prompt are added to §6 in this version. |
| v1.14 | 2026-11-07 | Amended after the acceptance of ADR-008: §7a (Documents) adds the drop onto the window and the review screen; the Non-goals line that named the inbox folder now points to ADR-008; a Consequences line records that a drop cannot be done from the keyboard. Status stays `amended`. |
| v1.15 | 2026-11-07 | Amended after ADR-008 v1.19: a file chooser opened by a command (for example `/file`) is a second way in beside the drop, so that intake can be started from the keyboard; §3 and §7a updated; the Consequences line that recorded the keyboard gap is removed because the gap is closed. |
| v1.16 | 2026-11-07 | Amended after the acceptance of ADR-009: `/export` is added to the commands, a new §7b (Export) describes the menu, what is exported, where the file goes and the fallback; the Non-goals line about export points to ADR-009. Status stays `amended`. |
| v1.17 | 2026-11-07 | Amended after ADR-008 v1.23: the command that opens the file chooser is named `/open` (it was `/file`, an example) and `/save` is added for saving a document attached to the chat (designer). |
| v1.18 | 2026-11-07 | Editorial revision for publication. |
