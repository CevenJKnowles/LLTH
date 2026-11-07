---
id: ADR-008
title: Document Intake, Conversion and Filing
type: adr
status: amended
version: v1.27
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
  - documents
  - intake
  - ocr
  - architecture
relationships:
  related:
    - ADR-002
    - ADR-005
    - ADR-006
    - ADR-007
    - DOC-OVW-019
    - DOC-OVW-020
    - DOC-IMPL-011
provenance:
  - human
---

# ADR-008 — Document Intake, Conversion and Filing

## Status

Amended (v1.27)

---

## 1. Context

The designer wants to hand documents to LLTH, such as PDFs and scans, and have LLTH read them once, convert them to a form the models can use, and file them. ADR-007 (accepted) fixes where documents live (`user/documents/` and each project's `documents/`, each with `originals/`, `converted/` and `outputs/`), how they are named, and how LLTH changes files. This ADR decides how a document gets from the user's hand to those folders, and which kinds of tool do the reading. Export (PDF, DOCX, ODT, HTML) is a separate ADR. The designer's requirements are in `DOC-OVW-019` §3, `DOC-OVW-020` and the designer's statement of 2026-11-07 below.

### Decision drivers

- **LLTH is installed by other people on other machines.** The tools are chosen for anyone's machine, not for what is on the reference machine.
- **Free and open source, contemporary and lightweight.**
- **The formats to cover:** `.md`, `.docx`, `.pdf`, `.odt`, `.txt` and `.tex`, with the basics for writing and administrative tasks well covered, and code files.
- **Read once, use many times.** The document is converted at intake, so a model does not convert it again for every use (`DOC-OVW-019` DI-2).
- **The user stays in charge.** LLTH shows what it extracted and the user confirms before anything is filed.
- **Originals are kept.** LLTH stores the originals and the outputs in the user's directory, and the user may add or delete as they like (ADR-007 §4).
- **Lean dependencies** (`DOC-OVW-019` EX-2) and **nothing sent out** (ADR-002).
- **Evidence.** The options were researched on 2026-11-07 from the projects' own pages (`DOC-IMPL-011`): versions, licences, formats, languages and, where stated, sizes. Nothing was benchmarked on real documents.

### Rationale

Converting at intake gives each document one clean Markdown file with a small JSON file for its formatting, which any expert can open cheaply. The research shows that no single small tool covers every format: Pandoc converts the office and markup formats but cannot read PDF; PDFs with a text layer are read by a small library; scans need OCR, for which Tesseract is the default choice (left to a later version, §4a). A layered toolkit, each layer small and with a permissive or arm's-length licence, covers the designer's list on any machine. Keeping the original beside the converted files means a doubtful conversion can always be checked or redone.

---

## 2. Decision

### §1 What intake is

Intake takes a document the user has handed to LLTH, reads it, converts it to Markdown, and files it with its original in the folders of ADR-007. Nothing is converted again each time a model uses the document (`DOC-OVW-019` DI-2).

### §2 The formats

Intake covers `.md`, `.docx`, `.pdf` (with a text layer), `.odt`, `.txt` and `.tex`, and code files, which are read as plain text. **Scanned pages and photographs are not covered in the first version;** they wait for the OCR update of §4a.

### §3 How a document comes in

- **There is no inbox folder.** The user hands a document to LLTH by **dropping it onto the window**, and LLTH files it in its working directory for projects and memories. This replaces the single inbox folder of `DOC-OVW-019` DI-1.
- **A file chooser is a second way in.** A command, `/open`, opens the browser's own file chooser, which works from the keyboard and with a screen reader. The chosen file follows the same steps as a dropped one.
- **LLTH asks what to do first.** Once LLTH has read a dropped or chosen file, it does not go straight to filing. It asks "What would you like to do with *name*?" in a menu of the same kind as `/mode`, with three choices: **File it** (the review and filing steps of §6 and §7), **Use it in this chat** (the document is added to the conversation and not filed) and **Cancel** (nothing is kept). Esc also cancels. The prompt is not locked while this menu is open.
- **Where to file:** the review screen asks whether the document belongs to a project or to `user/documents/`, and files it there.

### §4 Reading

The default toolkit is a small layer for each kind of file, each called by LLTH's own code:

- **Scans and photographs** are **not in the default toolkit of the first version.** OCR with Tesseract is an anticipated update, recorded in §4a.
- **PDFs:** **pypdfium2** (Apache-2.0 or BSD-3, binary wheels). It reads the text of a PDF that already has a text layer, which needs no OCR. (It can also render the pages of a scanned PDF to images, which the OCR update of §4a will use.)
- **Office and markup documents** (`.docx`, `.odt`, `.tex`, `.md`, `.html`): **Pandoc** (a statically linked binary, 34.4 MB for the Linux release, GPL-2.0-or-later, called as a separate program). It cannot read PDF. A `.md` file is already Markdown, so intake only adds the frontmatter and the JSON file.
- **`.txt` and code files:** read as text, with the encoding detected by **charset-normalizer** (MIT, pure Python), so that German files saved as Windows-1252 or Latin-1 read correctly.

- **Upgrades, not defaults:** **Docling** (MIT; many formats, layout and tables; built on PyTorch, install size not found) may be offered as an optional heavier tier for layout- and table-aware conversion. Small OCR vision models served through llama.cpp, such as PaddleOCR-VL and Granite-Docling, are noted as a possible later upgrade; they are not chosen, because no official GGUF, no CPU figures and no confirmed German were found.
- **Licences:** only free and open-source programs. Anything linked into LLTH's own Apache-2.0 code must have a licence compatible with it, which excludes AGPL libraries such as PyMuPDF. A program called as a separate process (Pandoc, GPL) is kept at arm's length, and **the installer ships each GPL program's licence notice and a link to its source.** Licences are checked at release.
- **The installer provides the toolkit inside LLTH's own folder.** **Pandoc** is the static release binary; **pypdfium2** and **charset-normalizer** are Python wheels installed into LLTH's own virtual environment. The installer is its own ADR; this clause fixes only what it provides. (Tesseract and its language data are added by the OCR update, §4a.)

### §4a Anticipated update: OCR for scans and photographs

OCR is **not part of the first version.** It is an anticipated update. The decisions made for it so far are:

- **Reading:** **OCR with Tesseract** (Apache-2.0, more than 100 languages with German listed) (`DOC-OVW-019` DI-4) for PNG, JPEG and TIFF files and for the pages of a scanned PDF, which pypdfium2 renders to images. OCR is a **single pass**, and the doubtful words are marked from Tesseract's own confidence for each word. Further passes with other settings may be added if a trial on real scans shows that the confidence misses too much.
- **Languages:** the user chooses the OCR languages at installation, from those Tesseract offers, and can add more later in `LLTH/settings/`; the installer adds the data for each. English is the default.
- **Installer:** Tesseract comes from the `tesserocr` Python wheel (MIT), which bundles Tesseract and Leptonica, installed into LLTH's own virtual environment; its language data is downloaded from `tessdata_fast` (Apache-2.0) into LLTH's folder. A trial install must first show which Tesseract version and which language data the wheel bundles (see Implementation notes).
- **Review:** the review screen marks the doubtful words, with N and P to jump between them. Every OCR document that the user chooses to file is reviewed, in every Confirm setting.
- **In the chat:** a scan or photograph used in the chat is read by the same single OCR pass, without the review, and the interface says that the text has not been reviewed and that the doubtful words are not marked. If a trial on real scans shows too many misreads reaching answers, a review before attaching may be added as an option.
- **Correcting a doubtful word** on the review screen is not designed yet.

**Until the OCR update exists,** a scan, photograph or scanned PDF that the user drops or opens is **declined with a plain message** in the chat, "Scanned document reading is unavailable in this current version.", and nothing is filed or attached. Recognising a scanned PDF means finding that it has no text layer, which pypdfium2 can report.

### §5 The converted files

- Each document becomes a **Markdown (`.md`) file with YAML frontmatter** for the text details and a **JSON file beside it** with the formatting data, with pointers between them (`DOC-OVW-019` DI-3).
- The converted files **share one name stem** with the original (for example `2026-11-07-tenancy-agreement.pdf`, `.md` and `.json`) and live in `converted/` (ADR-007 §4).
- **The frontmatter holds:** the **title** (the file name or the first heading), the **date taken in**, the **kind of source** (the file extension), the **method** (text layer or conversion; OCR once the update of §4a exists), the **language** (the OCR language used; empty until then), the **checksum of the original** (a standard hash) and a **one-line quality summary** that LLTH's own code writes from counts, for example "text layer, 12 pages, 4,310 words" (with OCR later, "OCR, 14 doubtful words out of 1,820").
- **The JSON holds** page breaks (and, once OCR exists, the flagged words with their confidence). **It has no table positions,** because none of the default tools finds tables; only the optional Docling tier could supply them.
- **Reading a document into a model:** a document is read whole if it fits in the free context with room left for the reply, worked out from the live token count that the interface already shows; otherwise it is read in sections. For any document that does not fit, an **outline with page and line positions is built at intake**, not later. The interface says when a file is too long to load whole.

### §6 The review

- **LLTH shows the information it has extracted, and the user confirms it. Once the user confirms, the document is filed.** Until then the original is kept, so a result that looks wrong can be converted again with other settings.
- **The review screen** shows the extracted text. In the first version every document has a text layer or is converted, so the review follows the Confirm setting. The marking of doubtful words, and the rule that every OCR document is reviewed in every Confirm setting, belong to the OCR update (§4a).
- **Text in a document is data, not instructions.** LLTH passes a document's text to a model inside clear markers and labels it as a document. How well the K2 models respect this is **untested.** What a model reads from a document never acts by itself: any change still goes through the confirmation of ADR-007 §6.

### §6a Using a document in the chat without filing it

- **"Use it in this chat" holds the document in memory only.** The converted text is held in memory for the current conversation, passed to the model under the markers and label of §6, and counted in the context line at once. Nothing is written to disk. The user types the instruction after the document is attached. The reading rule is the one of §5: a document that fits in the free context, with room for the reply, is attached whole; otherwise LLTH says in the chat that it is too long to load whole, builds the outline in memory, and reads it in sections. The reading rule is the same for a filed and an unfiled document.
- **An attached document stays until `/clear` or until LLTH closes, and can be filed from the chat.** Then it is discarded. While it is attached, the user can file it without dropping it again: the command **`/save`** files it, and the document follows the steps of §6 and §7 from there. `/save` with nothing attached says so. LLTH does not file an attached document by itself.
- **Scans and photographs used in the chat** wait for the OCR update (§4a). The review of §6 belongs to filing only.

### §7 Originals

- **Originals are not destroyed.** LLTH stores the originals and the outputs in the user's directory, and the user may add or delete as they like. This replaces the destruction of the original in `DOC-OVW-019` DI-5; ADR-007 §4 says the same.
- **While the user reviews, LLTH holds the dropped file in memory only.** When the user confirms, LLTH writes a copy to `originals/`; if the user cancels, or LLTH closes mid-review, the held file is discarded. The user's own file stays where they keep it, untouched.

### §8 Out of scope

- **Screenshots and audio** are out of scope for now (`DOC-OVW-019` DI-6).
- **Scans, photographs and OCR** are out of scope for the first version and anticipated as an update (§4a).

---

## 3. Consequences

### Positive

- Each document is read once and then cheap to use, with one clean Markdown file and a JSON file for its formatting.
- The original is always kept, so a doubtful conversion can be checked or redone.
- The user confirms what LLTH takes as true.
- The toolkit is small, free and open source, runs on Linux, macOS and 64-bit Windows apart from the gaps listed below, and covers every format the designer named except scans and photographs, which wait for the OCR update (§4a).
- A document that tries to give a model instructions meets the confirmation of ADR-007.

### Negative

- **The first version cannot read scans or photographs.**
- **The conversion does not reproduce the look of the original page;** exports come from the cleaned Markdown, not the original.
- **No single tool covers everything:** Pandoc cannot read PDF, and PDF text extraction is a separate step, so LLTH has to choose the right tool for each file.
- **`.tex` with custom macros may convert imperfectly** to Markdown.
- **For the OCR update:** each OCR language adds a data file. Only Tesseract's German support was confirmed from its own pages; the lighter ONNX engines (RapidOCR, PaddleOCR) could not be confirmed for German and are not chosen. The doubtful words are only as good as the confidence of a single OCR pass.
- **Originals stay on disk** for as long as the user keeps them, so sensitive documents are not destroyed by LLTH.
- **The review adds a step** before a document is filed.
- **Long documents** do not fit a model's context whole; they need the outline and section reading.
- **Platform coverage has gaps.** pypdfium2 and charset-normalizer have wheels for Linux, macOS and Windows on common processors; Pandoc's arm64 build is a possible gap. For the OCR update, the `tesserocr` wheels cover Linux x86-64 and aarch64, macOS (Intel and Apple Silicon, built for macOS 15 or newer) and 64-bit Windows, but not Windows on ARM. LLTH as a whole is intended for any machine and tested on Linux only (`DOC-IMPL-011` §10).
- **The research was not a benchmark:** accuracy, speed and installed size on real documents are unmeasured.

### Implementation notes

- **Before the OCR update (§4a),** a trial `pip install` of `tesserocr` in a scratch virtual environment must show which Tesseract version the wheel bundles and whether it includes any language data; none of that is stated on its page. Installing anything, even into a virtual environment, is the user's decision. The trial is not needed for the first version.
- A few real documents (a text PDF, a Word file, a `.tex` file) should be run through the chosen tools before the design is built, to see the quality and to check how well pypdfium2 reads them. A scanned page is added to that set for the OCR update.
- The evidence, with each figure marked as read, measured or estimated, is in `DOC-IMPL-011`. Several facts there are unconfirmed (poppler's licence, Docling's installed size, the vision models' CPU use) and are re-checked when the installer is decided.
- ADR-007's tree needs no change: there is no inbox.

### Related

- ADR-002 — Native User-Space Install, No Docker, Localhost Only
- ADR-005 — Fleet Selection, Roles and Category Profiles
- ADR-006 — Interface, a Local Web Page with an Expert Menu
- ADR-007 — Storage and Memory, Directory Tree, Locations and Confirmation (where documents live; the confirmation rules)
- `DOC-OVW-019` — Interface and document handling requirements, section 3
- `DOC-OVW-020` — Storage and memory requirements
- `DOC-IMPL-011` — Document tools research

---

## 4. Non-goals

- Export to PDF, DOCX, ODT or HTML (its own ADR).
- Screenshots and audio.
- Handwriting recognition.
- OCR in the first version (anticipated, §4a).
- Reproducing the look of the original page.
- Guaranteeing that OCR is correct.
- The installer and how the programs reach a user's machine.
- Saving or filing anything without the user's confirmation under the settings of ADR-007.

---

## 5. Options considered

### Option A — A layered toolkit: Pandoc, a PDF text library, Tesseract, with the original kept (chosen; Tesseract deferred to the update of §4a)
Small, free, open source and portable; covers every format the designer named; the user confirms the result. The first version ships the layers without Tesseract.

### Option B — Docling as the default for everything
Not chosen as the default: it is MIT and covers many formats, but it is built on PyTorch and no install size or CPU behaviour was found. Kept as an optional upgrade (§4).

### Option C — OCRmyPDF as the OCR layer
Not chosen: its job is to produce searchable PDFs, which intake does not need, because it converts to Markdown; it adds Python 3.11+ and more programs.

### Option D — Small OCR vision models served by llama.cpp as the default
Not chosen yet: no official GGUF, no CPU figures and no confirmed German were found. Noted as a future option.

### Option E — Keep only the original and convert every time a model needs it
Not chosen: the designer wants conversion at intake so that the model does not convert again each time.

---

## 6. Amendment record

| Version | Date | Summary |
|---------|------|---------|
| v1.0 | 2026-11-07 | Initial draft, from `DOC-OVW-019` §3 and `DOC-OVW-020`, with the tools checked on the reference machine. Ten items marked Proposed. |
| v1.1 | 2026-11-07 | Rewritten around the research of `DOC-IMPL-011`, at the designer's request that the tools suit anyone's machine: the reference-machine facts are removed from the Context; the formats the designer named are stated; the Proposed items now include a layered default toolkit, upgrades that are not defaults, a licence rule, the installer's role and the languages; options B to E are added. Thirteen items are marked Proposed. |
| v1.2 | 2026-11-07 | Review step 1: the inbox is `user/documents/inbox/`, read when the user asks with `/intake`, and a file dropped onto the window is a second way in (designer, A and C); moved out of Proposed. Twelve Proposed items remain. A note that ADR-007's tree needs the `inbox/` folder. |
| v1.3 | 2026-11-07 | The designer dropped the inbox: there is no inbox folder and no `/intake` command; a document comes in by dropping it onto the window. §3 rewritten; the Proposed item about moving the original now says LLTH stores a copy in `originals/`; the note about ADR-007's tree is replaced. |
| v1.4 | 2026-11-07 | Review step 2: pypdfium2 reads PDFs, both text layers and rendering scanned pages for Tesseract; pypdf is dropped (designer). The PDF layer moved out of the Proposed toolkit item into §4. Eleven Proposed items remain. |
| v1.5 | 2026-11-07 | Review step 3: the default toolkit (Tesseract, pypdfium2, Pandoc, charset-normalizer) accepted by the designer and moved into §4 Reading as plain clauses. Ten Proposed items remain. |
| v1.6 | 2026-11-07 | Review step 4: the upgrades that are not defaults (Docling as an optional heavier tier; small OCR vision models noted for later) accepted by the designer as written and moved into §4. Nine Proposed items remain. |
| v1.7 | 2026-11-07 | Review step 5: the licence rule accepted with the addition that the installer ships each GPL program's licence notice and a link to its source (designer); moved into §4. Eight Proposed items remain. |
| v1.8 | 2026-11-07 | Review step 6: the installer provides the toolkit inside LLTH's own folder (designer, option A), with Tesseract from the `tesserocr` wheel and language data from `tessdata_fast`; moved out of Proposed into §4. Platform gaps and the trial install added to the Consequences and notes. Eight Proposed items remain. |
| v1.9 | 2026-11-07 | Review step 7: where to file (ask on the review screen: a project or `user/documents/`) accepted as written by the designer and moved into §3. Seven Proposed items remain. |
| v1.10 | 2026-11-07 | Review step 8: the review screen (doubtful words marked for OCR; every OCR document is reviewed in every Confirm setting; text-layer documents follow the setting) accepted as written by the designer and moved into §6. Six Proposed items remain. |
| v1.11 | 2026-11-07 | Review step 9: OCR is one pass with the doubtful words marked from Tesseract's own confidence (designer, option B); several passes may come later. Moved into §4. Five Proposed items remain. |
| v1.12 | 2026-11-07 | Review step 10: the frontmatter and JSON fields accepted by the designer in the corrected form (no table positions; language is the OCR language used, empty otherwise; the quality summary is written by LLTH's code); moved into §5. Four Proposed items remain. |
| v1.13 | 2026-11-07 | Review step 11: the dropped file is held in memory only during the review and written to `originals/` on confirmation (designer, option A); moved into §7. Three Proposed items remain. |
| v1.14 | 2026-11-07 | Review step 12: the languages accepted in the corrected form (chosen at installation, English by default, more can be added later in `LLTH/settings/`; the size estimate is dropped); moved into §4. Two Proposed items remain. |
| v1.15 | 2026-11-07 | Review step 13: reading a document into a model accepted with two changes (a document is read whole if it fits in the free context with room for the reply; the outline is built at intake for any document that does not fit); moved into §5. One Proposed item remains. |
| v1.16 | 2026-11-07 | Review step 14: the document text is passed to a model inside markers and labelled as a document (designer, option B); moved into §6. §10 removed; no Proposed items remain. Two stale references corrected. |
| v1.18 | 2026-11-07 | Accepted by the designer after the step-by-step review (v1.1 to v1.17). Status `accepted`, canonical `true`. No text of the decisions changed. Nothing is built, created or installed yet. |
| v1.19 | 2026-11-07 | Amended (status becomes `amended`): a file chooser opened by a command is added as a second way in, so that intake can be started from the keyboard (designer). The decisions of v1.18 are otherwise unchanged. |
| v1.20 | 2026-11-07 | Amended: after a drop or `/file`, LLTH asks what to do with the document (File it, Use it in this chat, Cancel), added to §3 (designer, option A in the mockup review). §6 now says the review applies to documents the user files. New §6a holds three Proposed items (what "use in chat" does, how long it stays, OCR without review) for the designer to decide one at a time. Status stays `amended`. Nothing is built. |
| v1.21 | 2026-11-07 | Review of §6a, P-1: "Use it in this chat" holds the document in memory only and reads it by the rule of §5, with the outline built in memory for a long one (designer, option A); moved out of Proposed. Two Proposed items remain (P-2, P-3). |
| v1.22 | 2026-11-07 | Review of §6a, P-2: an attached document stays until `/clear` or until LLTH closes, and can be filed from the chat without dropping it again (designer, option B); how the offer is shown is left for the mockup. Moved out of Proposed. One Proposed item remains (P-3). |
| v1.23 | 2026-11-07 | Naming: the command that opens the file chooser is `/open` (it was `/file`, an example), and `/save` is the way to file a document attached to the chat; this settles the open detail of v1.22 (designer). The history rows above keep the old name as it was written. One Proposed item remains (P-3). |
| v1.24 | 2026-11-07 | Review of §6a, P-3: a scan used in the chat is read by one OCR pass with no review and a notice that it is unreviewed (designer, option A); moved out of Proposed. No Proposed items remain. §6a is complete; the amendment awaits the designer's acceptance. |
| v1.25 | 2026-11-07 | Amended at the designer's request: OCR with Tesseract (the `tesserocr` wheel, its language data, the doubtful-word review and the scan-in-chat clause) is removed from the default toolkit of the first version and recorded as an anticipated update in the new §4a. §2, §4, §5, §6, §6a, §8, the Consequences, the notes, the Non-goals and Option A are made consistent. One Proposed item in §4a (decline a scan with a plain message). The acceptance of v1.24 is still pending. |
| v1.26 | 2026-11-07 | The one Proposed item of v1.25 is decided: a scan, photograph or scanned PDF is declined in the first version with the message "Scanned document reading is unavailable in this current version." (designer's wording). No Proposed items remain. The acceptance of v1.24 and v1.25/v1.26 is pending. |
| v1.27 | 2026-11-07 | Editorial revision for publication. |
