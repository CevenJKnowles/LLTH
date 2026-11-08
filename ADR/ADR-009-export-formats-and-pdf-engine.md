---
id: ADR-009
title: Export, Formats and the PDF Engine
type: adr
status: amended
version: v1.3
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
  - export
  - documents
  - pdf
  - architecture
relationships:
  related:
    - ADR-006
    - ADR-007
    - ADR-008
    - DOC-OVW-019
    - DOC-IMPL-011
provenance:
  - human
---

# ADR-009 — Export, Formats and the PDF Engine

## Status

Amended (v1.3)

---

## 1. Context

The designer wants basic administration tools in LLTH, including export to PDF, DOC, ODT and HTML (`DOC-OVW-019` EX-1), with lean dependencies (EX-2). ADR-007 (accepted) fixes where the results go (`outputs/`, in a project or under `user/documents/`) and how LLTH changes files. ADR-008 (accepted) fixes how documents come in and become cleaned Markdown. This ADR decides how text becomes a file in another format. The designer's requirements are in `DOC-OVW-019` §4; the tools were researched on 2026-11-07 (`DOC-IMPL-011`, and the checks below).

### Decision drivers

- **The formats:** PDF, DOC (as `.docx`), ODT and HTML (`DOC-OVW-019` EX-1).
- **Lean dependencies** (EX-2) and **free and open source**, for anyone's machine.
- **Nothing sent out** (ADR-002), and **nothing assumed to be on the machine**, so the installer provides the tools inside LLTH's own folder (ADR-008 §4).
- **What the tools say on their own pages** (read on 2026-11-07, `DOC-IMPL-011` §4 and the checks below):
  - **Pandoc** writes DOCX, ODT, HTML, LaTeX and plain text, and PDF through an engine; its valid PDF engines include `typst`, `tectonic` and `weasyprint`, and by default it uses LaTeX, "which requires that a LaTeX engine be installed". A DOCX or ODT is styled by a reference document (`--reference-doc`); a single self-contained HTML file uses `--embed-resources` with `--standalone`.
  - **Typst** (0.15.1, Apache-2.0) compiles to PDF with `typst compile file.typ`. Its command-line program embeds the fonts Libertinus Serif, New Computer Modern, New Computer Modern Math and DejaVu Sans Mono and otherwise uses the system's fonts. Its pages do not state the release file sizes, the platforms, how it fetches packages, or whether it makes PDF/A or PDF/UA files.
  - **Tectonic** "can download the many necessary support files on the fly"; its binary size and licence were not on the pages read.
  - **WeasyPrint** (70.0, BSD-3-Clause) turns HTML and CSS into PDF but needs Python 3.10 or newer and the Pango library on the machine.

### Rationale

Pandoc already converts to every format the designer named except PDF, in one small program that the installer provides (ADR-008). For PDF, Typst is one self-contained program that Pandoc can drive, so LaTeX is not needed. Where the PDF engine is missing, the browser's own print function gives a PDF with no extra dependency.

---

## 2. Decision

### §1 The formats

LLTH exports to **PDF, DOCX, ODT and HTML** (`DOC-OVW-019` EX-1). The word-processor format is **`.docx`, not the old `.doc`**, and **LibreOffice is left out**.

### §2 The tools

- **Pandoc** converts to DOCX, ODT and HTML.
- **Typst** is the PDF engine, as one small program that Pandoc can use.
- **The browser's own print-to-PDF is the fallback** when no engine is available, with no extra dependency.
- **LaTeX is an optional extra, not installed by default**.

### §3 Where an export goes

An export is a **new file in the `outputs/` folder** of the project, or in `user/documents/outputs/`, as ADR-007 §2 sets out. Creating it is a change of the first kind in ADR-007 §6, so it follows the user's Confirm setting.

### §4 The details

1. **The source of an export is the converted Markdown,** not the original file. The `title`, `author` and `date` in the document's frontmatter become the metadata of the export.
2. **What `/export` exports:** a command (`/export`) opens a menu of the four formats, and then exports **LLTH's last reply** (a letter, a draft), **the full chat**, or **a document the user picks** from the project or from `user/documents/`.
3. **Formats at no extra cost:** Pandoc also writes Markdown, plain text and LaTeX source, so the menu offers `.md`, `.txt` and `.tex` as well, with no new dependency.
4. **The look, and templates:** LLTH ships a plain default reference document for DOCX and ODT. **Templates live in `user/preferences/templates/`, wherever a template helps:** the user's own reference `.docx` or `.odt` for every export, a Typst template for PDF, a stylesheet for HTML, and later starting points for letters and other documents. The usual export format goes in `defaults.md`. The subfolders are decided when this is built.
5. **HTML** is exported as one self-contained file (`--standalone` with `--embed-resources`).
6. **Typst is provided by the installer** as a program inside LLTH's folder. Its release files, platforms and package behaviour were not confirmed (see Consequences), so this clause waits on a trial download.
7. **When Typst is missing, LLTH says so** and offers the browser's print-to-PDF. The browser saves the file where the user chooses, which may be outside the root, so LLTH cannot place that file in `outputs/` itself.
8. **LLTH makes no claim that its PDF files are accessible.** Typst's pages read do not say whether it produces tagged PDF, PDF/A or PDF/UA, so this is checked before any claim is made; DOCX and HTML keep their headings and structure.
9. **Fonts:** exports use Typst's embedded fonts, plus the machine's own fonts for other scripts. A document in a script those fonts lack may show missing glyphs; LLTH warns the user before exporting.

---

## 3. Consequences

### Positive

- Every format the designer named comes out of one converter that is already in the toolkit, with LaTeX avoided.
- The export is a normal new file in `outputs/`, under the Confirm setting of ADR-007.
- Nothing is sent out, and the fallback needs no extra program.
- The user can restyle DOCX and ODT with a reference document of their own.

### Negative

- **Typst's own pages leave gaps:** no release file names or sizes, no statement of platforms, no word on offline package use or on PDF accessibility. Whether the installer can provide it on every machine is **unconfirmed**.
- **Pandoc's manual does not describe the Typst route:** it lists `typst` as a valid PDF engine but states no requirement for it, so the working combination has to be tried.
- **PDF accessibility is unverified.**
- **Exports do not reproduce the original's look,** because they come from cleaned Markdown.
- **A document in a script the embedded fonts lack** needs system fonts.
- **The fallback saves outside LLTH's root,** so the result is not filed for the user.
- **Pandoc's own gaps:** the pages read do not say how math and tables come out in DOCX and ODT, or whether an external program is needed for them; a trial on real documents is needed.
- **LaTeX users** who want LaTeX-quality PDFs must install a TeX engine themselves.

### Implementation notes

- A trial export of a few real documents (a letter with a table, a longer text with headings, one with German umlauts and one with math) to DOCX, ODT, HTML and PDF should be done before the design is built.
- Typst should be checked for its release files by platform, its package behaviour offline, and its PDF standards (the accessibility guide on its site was not read).
- The evidence is in `DOC-IMPL-011`; the checks for this ADR are summarised in §1.

### Related

- ADR-002 — Native User-Space Install, No Docker, Localhost Only
- ADR-006 — Interface, a Local Web Page with an Expert Menu
- ADR-007 — Storage and Memory, Directory Tree, Locations and Confirmation (`outputs/` folders; the Confirm setting)
- ADR-008 — Document Intake, Conversion and Filing (the converted Markdown; the toolkit)
- `DOC-OVW-019` — Interface and document handling requirements, section 4
- `DOC-IMPL-011` — Document tools research

---

## 4. Non-goals

- The old `.doc` format, and LibreOffice.
- Editing a document and converting it back (round trips).
- A template designer or page-layout tool.
- Guaranteeing that an export looks like the original.
- PDF/A, PDF/UA or tagged-PDF claims (until checked).
- Reading or converting documents into LLTH (ADR-008).
- The installer.

---

## 5. Options considered

### Option A — Pandoc for every format, with Typst as the PDF engine (chosen)
One converter for all four formats, one small program for PDF, no LaTeX.

### Option B — LaTeX as the default PDF engine
Not chosen: Pandoc's default, but it needs a LaTeX installation, against the designer's lean dependencies. Kept as an optional extra.

### Option C — Tectonic as the PDF engine
Not chosen: it is a single executable, but it "can download the many necessary support files on the fly", and its binary size and licence were not on the pages read. That conflicts with "nothing sent out" unless offline use is confirmed.

### Option D — WeasyPrint for PDF
Not chosen: BSD-3-Clause and a Pandoc engine, but it needs Python 3.10 or newer and the Pango library, a system package that cannot live in LLTH's own folder without root.

### Option E — LibreOffice for DOCX, ODT and PDF
Not chosen: left out by the designer (2026-11-05) as heavy.

---

## 6. Amendment record

| Version | Date | Summary |
|---------|------|---------|
| v1.2 | 2026-11-07 | Drafted and reviewed, accepted by the designer. |
| v1.3 | 2026-11-07 | Editorial revision for publication. |
