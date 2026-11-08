---
id: ADR-010
title: Documentation Checks in Continuous Integration
type: adr
status: amended
version: v1.7
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
  - ci
  - documentation
  - integrity
relationships:
  related:
    - ADR-004
    - DOC-GOV-001
    - DOC-GOV-002
provenance:
  - human
---

# ADR-010 — Documentation Checks in Continuous Integration

## Status

Amended (v1.7)

---

## 1. Context

The repository holds documentation, decision records and benchmark evidence. It has no application to build or test. Its quality rests on three things that a reader cannot see by looking at a page: every document follows `DOC-GOV-002`, every cross-reference resolves, every evidence file matches the checksum in `benchmarks/MANIFEST.sha256`, and no file holds a secret or a local path. These properties have been checked by hand. A check that runs on every push and every pull request keeps them true as the repository changes and as others contribute.

### Decision drivers

- **Enforce the standard automatically.** `DOC-GOV-002` and the ADR policy define fields, naming and structure that are mechanical to verify.
- **Protect the evidence and the repository.** The benchmark manifest is only useful if a failure is noticed when it happens, and a pull request from someone else gets the same secret and path checks as the maintainer's.
- **Lean dependencies** (ADR-004): no third-party packages, and as few third-party actions as possible.
- **Read-only and secret-free.** The workflow needs no credentials and cannot write to the repository.
- **Free on GitHub-hosted runners** for a public repository.

### Rationale

Every property to check is a rule of the documentation standard, a reference between documents, a checksum, or a generic pattern for secrets and local paths. A short Python script using only the standard library can verify all of them in under a minute. Existing linters check Markdown style, not identifiers, version agreement or the manifest, so they would add dependencies without covering the rules that matter here.

---

## 2. Decision

### §1 One workflow

One GitHub Actions workflow, `.github/workflows/docs-check.yml`, runs the documentation check on a GitHub-hosted Ubuntu runner. Its permissions are `contents: read` only. It uses no secrets. It runs on every push to `main` and on every pull request.

### §2 The checks

A run fails if any check reports a problem. Each problem is printed as `file:line: message`.

1. **Manifest.** `sha256sum -c benchmarks/MANIFEST.sha256` reports no failures.
2. **Frontmatter.** Every Markdown file has frontmatter, except the root `README.md` and the generated result files in `benchmarks/quality/scoring/`. The required fields of `DOC-GOV-002` are present and appear in its order. `canonical` is `true` when `status` is `active`, `complete`, `accepted` or `amended`.
3. **Version agreement.** The `version` in the frontmatter of an ADR equals the last row of its amendment record. The ADR index and other documents carry no amendment record and are not checked.
4. **Identifiers.** Each filename matches the document id and the naming pattern of `DOC-GOV-002`. Ids are unique. Every `ADR-NNN` and `DOC-<AREA>-NNN` identifier in the text resolves to a file. Retired ids are listed in the script.
5. **ADR structure.** Each ADR has the sections of `DOC-GOV-001` in order: Status, Context, Decision, Consequences, Non-goals and Amendment record. Options considered is optional. The ADR index is exempt.
6. **Links.** Every relative Markdown link resolves to a file or folder. External links are not checked.
7. **Secrets and local paths.** No tracked file contains a token in a known provider format (Hugging Face, GitHub, OpenAI-style, AWS), a private-key header, a hard-coded credential, or an absolute home-directory path (`/home/<user>/`, `/Users/<user>/`, `C:\Users\<user>\`).

### §3 The script

The checks are one Python 3 script, `.github/scripts/check_docs.py`, using only the standard library and run as `python3 -I`. It reads the repository and writes nothing.

### §4 Actions and dependencies

The workflow uses one third-party action, `actions/checkout`. It is pinned by commit SHA, with the version as a comment. Python is the runner's preinstalled Python 3. No package is installed.

### §5 What the check does not do

- It does not check wording, tone or the writing standard beyond the rules above.
- It does not scan for specific names, and it does not check commit messages or author addresses. Those checks run on the maintainer's machine before a push, because a list of names would publish what it protects. The generic secret and path patterns of §2 item 7 are public.
- It does not build llama.cpp, run benchmarks or deploy anything. The build and the benchmarks need the reference GPU.

---

## 3. Consequences

### Positive

- The documentation standard and the cross-references are enforced on every push and every pull request.
- A change to an evidence file without a matching manifest update fails visibly.
- Contributors receive the same structure, secret and path checks as the maintainer.

### Negative

- The script is code to maintain. It must change whenever `DOC-GOV-002` or `DOC-GOV-001` changes a rule it checks.
- The check covers structure, not content. A well-formed document can still break the writing standard.
- The manifest, secret and path checks duplicate checks in the local pre-push script.

### Implementation notes

- The script and the workflow are written after this ADR is accepted.
- The first run on the current tree must pass without exceptions other than those named in §2.
- The checks mirror the manual sweep carried out before publication.

### Related

- ADR-004 — First-Round Model Selection and Benchmark Protocol (the evidence the manifest protects)
- DOC-GOV-001 — ADR policy
- DOC-GOV-002 — Documentation standard

---

## 4. Non-goals

- Building llama.cpp or running benchmarks in continuous integration.
- Deployment, releases or publishing.
- Checking wording or the writing standard.
- Scanning for specific names, commit messages or author addresses in the workflow.
- Third-party linters.

---

## 5. Options considered

### Option A — One workflow and a standard-library script (chosen)
Covers every rule that matters here, adds no packages and one pinned action, and can be read in one sitting.

### Option B — Existing linters and a link-check action
Not chosen: markdownlint, yamllint and a link checker add several third-party tools and actions, and none checks identifiers, version agreement or the manifest.

### Option C — Local checks only
Not chosen: a local script gives no signal to visitors and no check on pull requests from others.

### Option D — The pre-commit framework
Not chosen: it adds a tool for every contributor and still runs only on the contributor's machine.

---

## 6. Amendment record

| Version | Date | Summary |
|---------|------|---------|
| v1.6 | 2026-11-07 | Drafted and reviewed, accepted by the designer. |
| v1.7 | 2026-11-08 | §6 (README badges) removed: the README's presentation is not an architecture decision. §2 item 3: version agreement applies to ADRs only. |
