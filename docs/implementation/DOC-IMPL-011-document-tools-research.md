---
id: DOC-IMPL-011
title: Document Tools Research (Free and Open-Source Readers, Converters and OCR)
type: implementation
status: complete
version: v1.4
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
  - research
  - documents
  - ocr
  - adr-008
relationships:
  related:
    - ADR-006
    - ADR-007
    - ADR-008
    - DOC-OVW-019
provenance:
  - human
---

# Document tools research

## Purpose

LLTH is installed by other people on other machines, so the choice of the programs that read, convert and OCR documents cannot rest on what is installed on the reference machine. This note records what the free and open-source options are, as of 2026-11-07, for the formats the designer named (`.md`, `.docx`, `.pdf`, `.odt`, `.txt`, `.tex`) plus code and the basics of administrative work. It is the evidence base for ADR-008 and for the later export ADR. **No tool was run or benchmarked for this note;** every figure comes from a public page.

## Method and limits

- Two kinds of source. **Primary:** each project's own repository, release page, documentation or model card, read on 2026-11-07. **Secondary:** blog comparisons from a web search; used only to find candidates, never as evidence for a figure.
- Where a summary of a page and the verbatim top of a release page disagreed, the verbatim text was used (this happened for Pandoc, Docling, MarkItDown, Tesseract, OCRmyPDF and docTR). "Latest" below is the entry marked "Latest" at the top of the project's releases page.
- Many pages do not state a version, a date, an installed size or a CPU-only guarantee. Those cells say **not found**; nothing was filled in.
- Release years are mostly not shown on the pages; the dates are from 2026 where the page or its footer shows 2026.

## 1. Converting documents to Markdown

| Tool | Latest | Licence | Reads | Packaging and weight | Notes |
|---|---|---|---|---|---|
| **Pandoc** | 3.13 (26 Oct 2026) | GPL-2.0-or-later ("Released under the GPL, version 2 or greater") | Markdown, DOCX, ODT, LaTeX, HTML, Typst. **Does not read PDF.** Plain text is not in the input list by name. | **Statically linked executable, no dynamic dependencies.** Linux x86_64 archive 34.4 MB. | Writes Markdown, DOCX, ODT, LaTeX, HTML, plain text and PDF (PDF through an engine: the manual's engine list, from a summary, names pdflatex, lualatex, xelatex, latexmk, tectonic, wkhtmltopdf, weasyprint, pagedjs-cli, prince, context, groff and typst). Static builds cannot use Lua filters that need C modules. |
| **Docling** | 2.148.0 (5 Nov) | Code: MIT. Models: "refer to the model licenses found in the original packages" | PDF, DOCX, XLSX, PPTX, ODT, ODS, ODP, EPUB, Markdown, AsciiDoc, LaTeX, HTML, CSV, images (PNG, JPEG, TIFF, BMP, WEBP), plain text (per the homepage), and more | Python package (`pip install docling`, Python 3.10+). "Models depend on the PyTorch library." Install size: not found. | OCR engines: RapidOCR (installed by default), EasyOCR, Tesseract, and others. Lists "local execution capabilities for sensitive data and air-gapped environments". CPU-only operation: not stated as a fact. |
| **MarkItDown** (Microsoft) | 0.1.9 (21 Oct) | MIT (sidebar) | PDF, Word, Excel, PowerPoint, images, HTML, CSV, JSON, XML, EPUB, ZIP. **ODT and LaTeX: not found.** | Python 3.10 to 3.14, extras per format. | No built-in OCR; image captioning and some features "rely on web-hosted services". |
| **PyMuPDF / MuPDF** | not found | **AGPL-3.0** (commercial licence also sold) | PDF, XPS, EPUB, TXT, MD and more; Office formats only through a paid add-on | Python package over a C engine | The AGPL is a poor fit for a project that is released under Apache-2.0 (see ADR-008 §4). |

Candidates from secondary sources only, **not checked on primary pages and not recommended on this evidence:** Marker (one source: code under GPL, model weights with a revenue threshold) and MinerU (sources disagree on its licence).

## 2. Reading text out of PDF files that already have a text layer

| Tool | Licence | Packaging | Notes |
|---|---|---|---|
| **pypdf** | BSD-style (the licence file gives no name) | "a free and open-source pure-python PDF library"; `pip install pypdf` | Reads and writes PDF; `extract_text()`. Pure Python, so it runs anywhere Python runs. |
| **pypdfium2** | "Apache-2.0 / BSD-3-Clause" | Python bindings to PDFium; pre-built wheels; "does not require any mandatory runtime dependencies, apart from Python and PDFium itself (which is commonly bundled)" | Opens, renders and extracts text; **not** pure Python (a binary wheel per platform). |
| **poppler** (`pdftotext`) | not stated on its homepage | Source tarball; a system package on most Linux distributions | Latest "poppler-26.11.0, released on November 5, 2026". The homepage does not mention `pdftotext` or a licence. |

## 3. Optical character recognition (scans and photographs)

| Tool | Latest | Licence | Languages | Weight and runtime | Outputs |
|---|---|---|---|---|---|
| **Tesseract** | 5.5.4 (28 Oct) | Apache-2.0 | "more than 100 languages" out of the box; **German (`deu`) listed** | Needs Leptonica for images. A binary plus language data files. Model sizes: not found. CPU-only: not stated, no GPU mentioned. | text, hOCR, PDF (including invisible-text-only), TSV, ALTO, PAGE |
| **OCRmyPDF** | 17.13.0 (28 Sep) | MPL-2.0 (non-core code MIT) | Uses Tesseract's language packs (German available) | Python 3.11+, Tesseract 4.1.1+, Ghostscript 9.54+ **or** pypdfium2 (Ghostscript "is now optional"), fpdf2, uharfbuzz. Optional: unpaper, pngquant, jbig2enc. | **Searchable PDF/PDF/A**, plus a `--sidecar` text file |
| **PaddleOCR** (PP-OCR) | 3.7.0 (11 Jun 2026) | Apache-2.0 | PP-OCRv6: "50 languages" (Chinese, English, Japanese and 46 Latin-script languages); README: "Supports 100+ languages". **German is not named.** | PaddlePaddle **or ONNX Runtime**; models "tiny (1.5M) / small (7.7M) / medium (34.5M)" parameters; "5.2× CPU inference speedup" for v6 | text with coordinates |
| **RapidOCR** | 3.10.0 (8 Oct) | Apache-2.0 (source and models) | "Default support for Chinese and English"; **German: not found** | `pip install rapidocr onnxruntime`; package "from the previous 15 MB to 29 MB"; ONNX Runtime | text, boxes (not stated verbatim) |
| **docTR** | 1.1.0 (21 Aug) | Apache-2.0 | not found | Python 3.11+; **PyTorch is the only backend** | text, JSON, hOCR, Markdown, layout, tables |

### Small vision-language models for OCR that can run through llama.cpp

These are newer. LLTH already runs llama.cpp, so a document model served the same way would add no new runtime. The evidence is thinner than for the classical engines.

| Model | Parameters | Licence | llama.cpp | Languages | Notes |
|---|---|---|---|---|---|
| **PaddleOCR-VL** (now 1.6 "0.9B") | 0.9B (the card shows 1.0B parameters) | Apache-2.0 (model and code) | `docs/multimodal.md` lists it only as an OCR note, "PaddleOCR-VL: #18825"; **no official GGUF found** (9 community quantisations linked) | "efficiently supports 109 languages"; German not named | Markdown and JSON output; tables, formulas, charts. No CPU or memory figures. |
| **Granite-Docling-258M** (IBM) | 0.3B (card title "258M") | Apache-2.0 | The card says to browse quantisations "to use this model in llama.cpp"; **16 community quantisations**; no official GGUF found | **English**; Japanese, Arabic and Chinese "experimental" | "not intended for general image understanding"; released 17 Sep 2025; outputs DocTags convertible to Markdown, HTML, JSON |
| **DeepSeek-OCR** | 3B | MIT (card metadata) | "DeepSeek-OCR: #17400" noted in `multimodal.md`; no official GGUF found | "multilingual", no list | GPU-oriented per its card (CUDA); no CPU figures |
| **olmOCR** | 7B | Apache-2.0 (code); weights licence not read | not listed | not found | "requires a GPU", at least 12 GB of GPU memory; **too heavy** for LLTH's target |

Not found for any of the vision models: a CPU-only or RAM guarantee, and an official GGUF from the publisher.

## 4. Producing PDF (for the later export ADR)

| Tool | Latest | Licence | What it is |
|---|---|---|---|
| **Typst** | 0.15.1 (17 Jul 2026) | Apache-2.0 (sidebar) | A command-line typesetting tool: Typst source to PDF, PNG, SVG, HTML. Pre-built binaries. Binary size: not found. Pandoc can write Typst and call it as its PDF engine. |
| **Tectonic** | no single stable version found (per-crate tags and a "Continuous Deployment" pre-release) | MIT (licence file) | "a modernized, complete, self-contained TeX/LaTeX engine, powered by XeTeX and TeXLive". Whether it downloads TeX files on first use and needs a network: **not found**. |

## 5. Office files, plain text, code and the administrative basics

| Tool | Licence | Use |
|---|---|---|
| **python-docx** | MIT (sidebar) | Read and write `.docx` (Pandoc already covers conversion). |
| **odfpy** | "GNU General Public License v.2 or (at your option) any later version or APACHE License v.2" | OpenDocument 1.2 files; the page does not name ODT explicitly. |
| **charset-normalizer** | MIT | Detects the text encoding of unknown bytes (99 encodings listed); pure Python. Needed for `.txt` and code files in other encodings. |
| **openpyxl** | MIT/Expat | Read and write `.xlsx`; the docs seen were for version 3.1.3 and may not be current. |
| **python-calamine** | MIT | Read-only `.xlsx`, `.xls`, `.xlsb` and `.ods`, through the Rust calamine library. |
| **tree-sitter** | MIT | A dependency-free C parser library that builds a syntax tree for source files; the page does not say it extracts outlines and does not list languages. |
| **universal-ctags** | GPL-2.0 | A command-line tool that indexes language objects in source files (an outline of functions and classes); languages and kinds not listed on the page. |
| **repomix** | MIT | npm tool that packs a repository into one file; `--compress` uses tree-sitter to keep key code elements. Needs Node. |

Code files are plain text. The basics for them are reading with the right encoding and, when wanted, an outline.

## 6. Findings

1. **Pandoc is the one small, general converter:** a 34.4 MB statically linked binary under GPL-2.0-or-later that reads and writes Markdown, DOCX, ODT, LaTeX and HTML, and writes plain text and PDF. Its gap is that it **cannot read PDF**.
2. **PDFs with a text layer** can be read by a pure-Python library (pypdf) or by a binary-wheel library (pypdfium2) without any system package; poppler's `pdftotext` also works but is a system package and its licence is not stated on its own homepage.
3. **Tesseract:** Apache-2.0, more than 100 languages with German listed, plain outputs including hOCR and searchable PDF, and it is packaged almost everywhere. OCRmyPDF wraps it for searchable PDFs under MPL-2.0 and now accepts pypdfium2 instead of Ghostscript.
4. **ONNX-based alternatives exist** (RapidOCR at about 29 MB, PaddleOCR on ONNX Runtime), but their **German support could not be confirmed** from the pages.
5. **Docling is an all-in-one converter** (MIT, many formats, layout and tables, runs locally, uses RapidOCR by default), but it is built on **PyTorch**, and no install size or CPU guarantee was found. It fits as an optional, heavier upgrade and not as the default.
6. **Small OCR vision models on llama.cpp are unproven:** PaddleOCR-VL (0.9B, Apache-2.0, 109 languages) and Granite-Docling-258M (Apache-2.0, English) both have community GGUFs, but no official GGUF, no CPU figures and no confirmed German were found.
7. **Licences to avoid in a released Apache-2.0 project:** PyMuPDF/MuPDF is AGPL-3.0. Marker and MinerU were not verified on primary pages.
8. **For PDF output,** Typst (Apache-2.0) is a compact option that Pandoc can drive; Tectonic (MIT) is the self-contained TeX option, with its network behaviour unverified.

## 7. Gaps

- No tool was run on real documents; accuracy, speed and installed size were not measured.
- German OCR support is confirmed for Tesseract only.
- poppler's licence, Tectonic's first-use downloads, Docling's installed size and CPU behaviour, and llama.cpp's current support for the vision models are not confirmed.
- Release years are mostly not shown on the pages.

## 8. Size of the default stack (a rough figure)

| Part | Size | Source |
|---|---|---|
| Pandoc (static Linux release) | 34.4 MB download | Read from the releases page; the unpacked size is not stated |
| Tesseract: program, `libtesseract`, `libleptonica` | about 7 MB (51 KB, 3.5 MB, 3.1 MB) | Measured on the reference machine; the libraries' own dependencies are not counted |
| English OCR data (`eng.traineddata`) | 23 MB | Measured on the reference machine |
| One more OCR language, such as German | expected to be of the same order | Estimate; not checked (only `eng`, `afr` at 7.5 MB and `osd` at 11 MB are installed there) |
| charset-normalizer | 0.7 MB | Measured on the reference machine |
| poppler: `pdftotext` and `libpoppler` | about 4 MB | Measured on the reference machine |
| pypdf, pypdfium2 | not measured | Not installed there; their pages state no size |

English-only, the default stack comes to roughly **70 to 100 MB**. The figure mixes a download size with installed sizes, so it is loose. The reference machine's Pandoc is a distribution package of 64 KB that links to many separate libraries, so it is not comparable with the 34.4 MB static release. No install size was found for Docling, which is PyTorch-based.

## 9. Tesseract on Linux: ways to get it onto a machine

Researched on 2026-11-07 for ADR-008 item 6 (whether an installer can place Tesseract in LLTH's own folder). Primary pages were read; "S" marks facts that come only from a summary of an unread part of a page.

**Upstream:** Tesseract 5.5.4 (Apache-2.0). The official installation page is dated (its Linux section names Ubuntu and Debian commands, a Snap and an AppImage, and does not list Arch, Alpine or Conda); it says "Most users will want tessdata_fast and that is what will be shipped as part of Linux distributions".

| Route | Needs root? | Version | What was found |
|---|---|---|---|
| **Distribution package** (`tesseract-ocr`, `tesseract`) | yes | Debian trixie 5.5.0; Ubuntu 26.04 5.5.0, 24.04 5.3.4, 22.04 4.1.1; AlmaLinux 8 and 9 4.1.1; Alpine 3.24 5.5.2, Edge 5.5.3; Fedora 44 updates, Rawhide and Arch 5.5.4 (S); openSUSE Tumbleweed 5.5.3 (S) | Available almost everywhere, but older releases lag upstream. OCRmyPDF supports Tesseract 4.1.1 and newer. German data is a separate package: `tesseract-ocr-deu` (Debian, Ubuntu), `tesseract-langpack-deu` (Fedora), `tesseract-data-deu` (Arch). |
| **Build from source into a home folder** | no | any | Official: "Tesseract can be configured to install anywhere, which makes it possible to install it without root access" (`./configure --prefix=$HOME/local/`). Needs a C++17 compiler, GNU Autotools, pkg-config and Leptonica. Heavy for ordinary users. |
| **Python wheels: `tesserocr` 2.12.0 (MIT)** | no (a virtual environment) | bundled version not stated | PyPI: "Pre-built wheels for Linux, macOS, and 64-bit Windows bundle Tesseract, Leptonica, and their runtime dependencies. No separate Tesseract installation is required to use these wheels." Linux wheels: manylinux x86-64 and aarch64 (glibc 2.27+ and 2.28+) and musllinux x86-64, for CPython 3.9 to 3.15. A Python API, not the command-line program. Whether the wheel includes any language data is not stated. |
| **Community static binary** (DanielMYT/tesseract-static) | no | 5.5.4 | A static musl binary for x86_64 and aarch64: "does not have any host Glibc minimum version requirement" and needs no FUSE. No languages bundled; it looks for `tessdata` in the current folder or `TESSDATA_PREFIX`. Built by GitHub Actions. One individual, 12 stars, not described as official; checksums in older release notes, none seen in the newest. |
| **Community AppImage** (AlexanderP/tesseract-appimage) | no | 5.5.4 | x86_64 only; built in a Docker container on Debian 13; supports Debian 10+, Fedora 30+, Ubuntu 14.04+ and others. Bundles German, English, Finnish, French, Portuguese, Russian, Spanish and orientation data. One individual, 21 stars, not described as official; no checksums or signatures found; whether FUSE is needed is not stated. |
| **Snap** | yes (snap) | edge channel | The official page gives `sudo snap install --channel=edge tesseract` and says the traineddata "is currently not shipped with the snap package and must be placed manually". |
| **conda-forge** | no (micromamba) | 5.5.3 (updated 2026-07-27; 5.5.4 not listed) | Apache-2.0 for the package. Platforms, download size and whether language data is included were not found. The install route without root comes from a secondary source (a feedstock issue). |
| **Tesseract.js / tesseract-wasm** (WebAssembly) | no | tesseract.js 7.0.0 (Apache-2.0); tesseract-wasm 0.11.0 (BSD-2-Clause) | Run in a browser or Node. Offline use means self-hosting the worker, the core and the language files; the local-installation guide is written for version 5. tesseract-wasm: "The library and English training data require a ~2.1MB download (with Brotli compression)". German support, fast or best models for tesseract.js, and speed or accuracy against native Tesseract were not found; tesseract.js "does not support PDF files". |

**Language data.** `tessdata` is the legacy-plus-LSTM set, `tessdata_best` the slowest and most accurate, and `tessdata_fast` an integer LSTM set that is the fastest and least accurate. All three are Apache-2.0 and work with Tesseract 4 and 5 (the `best` and `fast` sets only with the LSTM engine). The official pages do not state file sizes. **The 23 MB for English in section 8 is the full `tessdata` set** installed on the reference machine; the fast models are smaller (a secondary source puts English fast near 2 MB compressed; unverified). The pages do not say whether `TESSDATA_PREFIX` may point to a folder the user owns; the community static build and the Python wheels both use it that way, which suggests it can.

**What this means for LLTH.**
1. The one route that needs neither root nor a build is the **`tesserocr` wheel**: `pip install` into LLTH's own virtual environment brings its own Tesseract, on Linux x86-64 and aarch64 with glibc 2.27 or newer. Its bundled Tesseract version and its language data must be checked in a trial install.
2. The community static binary and AppImage also need no root, but each is one individual's unofficial build.
3. A WebAssembly build would let the browser page do OCR with nothing installed, but its German support and accuracy are unknown.
4. Distribution packages work but need root and are often older than 5.5.4.

## 10. Platform coverage of the default toolkit

Read on 2026-11-07. The file lists of the PyPI pages were partly summarised ("S" below); the Pandoc asset list did not load and is not known.

| Tool | Linux | macOS | Windows | Python |
|---|---|---|---|---|
| **tesserocr 2.12.0** (bundles Tesseract) | manylinux x86-64 and aarch64 (glibc 2.27 or 2.28+), musllinux x86-64; musllinux aarch64 not found | x86_64 and arm64, wheels tagged `macosx_15_0` (built for macOS 15 or newer) | **win_amd64 only** (23.1 MB); no arm64 or 32-bit found | CPython 3.9 to 3.15 (S); "Python >=3.9" |
| **pypdfium2 5.15.0** (S) | manylinux and musllinux for x86_64 and aarch64, plus riscv64, s390x, ppc64le, i686 and armv7l | x86_64 and arm64, `macosx_13_0` | x64, x86 and arm64 | `py3-none` (any Python 3) |
| **charset-normalizer 3.5.2** (S) | compiled wheels for many platforms, with a pure-Python fallback | universal2 | amd64, 32-bit and arm64 | Python 3.7 or newer |
| **Pandoc 3.13** | static Linux binary (34.4 MB for amd64); arm64 not confirmed | the install page points to the releases page; file names not obtained | same | not applicable |

Wheel sizes for tesserocr: 5.6 MB (Linux x86-64), 5.3 MB (Linux aarch64), 4.1 MB and 3.6 MB (macOS), 23.1 MB (Windows). Wheel sizes are small, so the bundled Tesseract is lean; which Tesseract version they bundle and whether they include language data are **not stated**.

**Reading.** The document toolkit can run on Linux, macOS and 64-bit Windows, with these gaps: Windows on ARM (for Tesseract), macOS older than 15 (for the `tesserocr` wheel), and Pandoc's arm64 builds (unconfirmed). Whether LLTH as a whole runs on macOS or Windows is a different question; it is built and tested on Linux only.

## Amendment record

| Version | Date | Summary |
|---------|------|---------|
| v1.0 | 2026-11-07 | Initial. Primary pages read for 26 tools on 2026-11-07 (and pdf.js, left out as a viewer); nothing benchmarked. |
| v1.1 | 2026-11-07 | Section 8 added: a rough size for the default stack, with each figure labelled as read, measured or estimated. |
| v1.2 | 2026-11-07 | Section 9 added: Tesseract on Linux, the ways to get it onto a machine, from the official documentation, the distribution packaging pages, PyPI and the community builds. |
| v1.3 | 2026-11-07 | Section 10 added: platform coverage of the default toolkit (Linux, macOS, Windows), with the gaps and the facts that could not be confirmed. |
| v1.4 | 2026-11-07 | Editorial revision for publication. |
