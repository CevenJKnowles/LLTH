#!/usr/bin/env python3
"""Documentation check for the LLTH repository (ADR-010).

Standard library only. Run from anywhere as:  python3 -I .github/scripts/check_docs.py
Reads the tracked files and any new files that are not ignored, writes nothing, prints each problem as  file:line: message,
and exits 1 if there is any.

Checks
  1  manifest         benchmarks/MANIFEST.sha256 verifies
  2  frontmatter      required fields, order, allowed values, canonical against status
  3  version          an ADR's frontmatter version equals the last row of its amendment record (the index is exempt)
  4  identifiers      filename matches id, ids are unique, referenced ids resolve
  5  ADR structure    the sections of DOC-GOV-001 in order
  6  links            relative Markdown links resolve
  7  secrets, paths   no provider token, private key, hard-coded credential or home-directory path
"""
import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RETIRED_IDS = {"DOC-OVW-001"}
FIELD_ORDER = ["id", "title", "type", "status", "version", "canonical", "scope", "audience", "created", "updated",
               "tags", "maturity", "milestone", "subordinate_to", "amends", "supersedes", "relationships", "provenance"]
REQUIRED = ["id", "title", "type", "status", "version", "canonical", "scope", "audience", "created", "updated", "tags", "provenance"]
AREA_TYPE = {"ARCH": "architecture", "GOV": "governance", "IMPL": "implementation", "OVW": "overview", "RUN": "runtime"}
ADR_STATUS = {"reserved", "draft", "accepted", "amended", "superseded"}
DOC_STATUS = {"reserved", "draft", "active", "complete"}
GOVERNING = {"active", "complete", "accepted", "amended"}
ADR_SECTIONS = ["Status", "1. Context", "2. Decision", "3. Consequences", "4. Non-goals", "5. Options considered", "6. Amendment record"]
ADR_OPTIONAL = {"5. Options considered"}
GENERATED = re.compile(r"^benchmarks/quality/scoring/results-.*\.md$")

SECRETS = re.compile(r"hf_[A-Za-z0-9]{30,}|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|sk-[A-Za-z0-9]{32,}|AKIA[0-9A-Z]{16}"
                     r"|-----BEGIN ([A-Z]+ )?PRIVATE KEY-----")
CREDENTIAL = re.compile(r"(api[_-]?key|secret|token|passwd|password)\s*[:=]\s*[\"']?[A-Za-z0-9/+_.-]{20,}", re.I)
HOME_PATH = re.compile(r"/home/[A-Za-z0-9._-]+/|/Users/[A-Za-z0-9._-]+/|[A-Za-z]:\\Users\\[A-Za-z0-9._-]+")

problems = []


def problem(path, line, message):
    problems.append("%s:%s: %s" % (path, line if line else 1, message))


def tracked_files():
    try:
        out = subprocess.run(["git", "-C", str(ROOT), "ls-files", "--cached", "--others", "--exclude-standard"],
                             capture_output=True, text=True, check=True).stdout
        return [f for f in out.split("\n") if f]
    except (OSError, subprocess.CalledProcessError):
        return sorted(str(p.relative_to(ROOT)) for p in ROOT.rglob("*")
                      if p.is_file() and ".git" not in p.parts and "llama.cpp" not in p.parts)


def read(rel):
    try:
        return (ROOT / rel).read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None


def strip_code(text):
    """Blank out fenced code blocks, keeping line numbers."""
    out, fence = [], False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            fence = not fence
            out.append("")
        else:
            out.append("" if fence else line)
    return out


def frontmatter(text):
    if not text.startswith("---\n"):
        return None, 0
    end = text.find("\n---\n", 4)
    if end < 0:
        return None, 0
    block = text[4:end]
    fields = []
    for i, line in enumerate(block.split("\n"), 2):
        m = re.match(r"^([a-z_]+):\s*(.*)$", line)
        if m:
            fields.append((m.group(1), m.group(2).strip(), i))
    return fields, block.count("\n") + 3


def check_manifest(files):
    rel = "benchmarks/MANIFEST.sha256"
    text = read(rel)
    if text is None:
        return
    for n, line in enumerate(text.split("\n"), 1):
        if not line.strip():
            continue
        m = re.match(r"^([0-9a-f]{64})  (.+)$", line)
        if not m:
            problem(rel, n, "malformed manifest line")
            continue
        target = ROOT / m.group(2)
        if not target.is_file():
            problem(rel, n, "listed file is missing: " + m.group(2))
        elif hashlib.sha256(target.read_bytes()).hexdigest() != m.group(1):
            problem(rel, n, "checksum does not match: " + m.group(2))


def amendment_rows(lines):
    """Version strings of the first table under the last amendment-record heading."""
    heads = [i for i, l in enumerate(lines) if re.match(r"^#{2,3} .*[Aa]mendment record", l)]
    if not heads:
        return None
    rows = []
    for l in lines[heads[-1] + 1:]:
        if re.match(r"^#{3} .*[Hh]istory", l) or re.match(r"^## ", l):
            break
        m = re.match(r"^\| (v\d+\.\d+) \|", l)
        if m:
            rows.append(m.group(1))
    return rows


def check_document(rel, text, ids):
    fields, _ = frontmatter(text)
    if fields is None:
        problem(rel, 1, "no frontmatter")
        return None
    keys = [k for k, _, _ in fields]
    values = {k: v for k, v, _ in fields}
    for k in REQUIRED:
        if k not in keys:
            problem(rel, 1, "missing frontmatter field: " + k)
    for k, _, ln in fields:
        if k not in FIELD_ORDER:
            problem(rel, ln, "unknown frontmatter field: " + k)
    known = [FIELD_ORDER.index(k) for k in keys if k in FIELD_ORDER]
    if known != sorted(known):
        problem(rel, 1, "frontmatter fields are out of order")
    doc_id = values.get("id", "")
    is_adr = doc_id.startswith("ADR-")
    status = values.get("status", "")
    if status not in (ADR_STATUS if is_adr else DOC_STATUS):
        problem(rel, 1, "status '%s' is not allowed for this kind of document" % status)
    canonical = values.get("canonical", "")
    if status in GOVERNING and canonical != "true":
        problem(rel, 1, "canonical must be true when status is " + status)
    if status in ("reserved", "draft") and canonical not in ("pending", "true"):
        problem(rel, 1, "canonical must be pending or true")
    if not re.fullmatch(r"v\d+\.\d+", values.get("version", "")):
        problem(rel, 1, "version must look like v1.0")
    for k in ("created", "updated"):
        if k in values and not re.fullmatch(r'"\d{4}-\d{2}-\d{2}"', values[k]):
            problem(rel, 1, k + " must be a quoted date YYYY-MM-DD")
    m = re.fullmatch(r"DOC-([A-Z]+)-\d{3}", doc_id)
    expected_type = "adr" if is_adr else AREA_TYPE.get(m.group(1)) if m else None
    if expected_type and values.get("type") != expected_type:
        problem(rel, 1, "type should be '%s' for id %s" % (expected_type, doc_id))
    if not (is_adr and re.fullmatch(r"ADR-\d{3}", doc_id)) and not m:
        problem(rel, 1, "id '%s' does not follow the naming pattern" % doc_id)
    if doc_id in ids:
        problem(rel, 1, "duplicate id %s (also in %s)" % (doc_id, ids[doc_id]))
    else:
        ids[doc_id] = rel
    # filename
    if rel.startswith(("ADR/", "docs/")):
        name = Path(rel).name
        pattern = r"ADR-000-README\.md" if doc_id == "ADR-000" else re.escape(doc_id) + r"-[a-z0-9]+(-[a-z0-9]+)*\.md"
        if not re.fullmatch(pattern, name):
            problem(rel, 1, "filename does not match id %s" % doc_id)
    # version agreement (ADRs only; the index and other documents carry no amendment record)
    lines = strip_code(text)
    if is_adr and doc_id != "ADR-000":
        rows = amendment_rows(lines)
        if rows is None:
            problem(rel, 1, "no amendment record")
        elif not rows:
            problem(rel, 1, "amendment record has no rows")
        elif rows[-1] != values.get("version"):
            problem(rel, 1, "version %s differs from the last amendment row %s" % (values.get("version"), rows[-1]))
    # ADR structure
    if is_adr and doc_id != "ADR-000":
        heads = [l[3:].strip() for l in lines if l.startswith("## ")]
        required = [h for h in ADR_SECTIONS if h not in ADR_OPTIONAL]
        present = [h for h in heads if h in ADR_SECTIONS]
        if [h for h in present if h in required] != required:
            problem(rel, 1, "ADR sections are missing or out of order")
        elif present != [h for h in ADR_SECTIONS if h in present]:
            problem(rel, 1, "ADR sections are out of order")
    return doc_id


def check_references(rel, text, ids):
    for n, line in enumerate(text.split("\n"), 1):
        for m in re.finditer(r"\b(ADR-\d{3}|DOC-[A-Z]+-\d{3})\b", line):
            ref = m.group(1)
            if ref not in ids and ref not in RETIRED_IDS:
                problem(rel, n, "identifier does not resolve: " + ref)


def check_links(rel, text):
    base = (ROOT / rel).parent
    for n, line in enumerate(strip_code(text), 1):
        for m in re.finditer(r"\]\(([^)\s]+)\)", line):
            target = m.group(1).split("#")[0]
            if not target or re.match(r"^(https?:|mailto:)", target):
                continue
            if not (base / target).exists():
                problem(rel, n, "link does not resolve: " + m.group(1))


def check_secrets(rel, text):
    for n, line in enumerate(text.split("\n"), 1):
        if SECRETS.search(line):
            problem(rel, n, "possible secret")
        elif CREDENTIAL.search(line):
            problem(rel, n, "possible hard-coded credential")
        if HOME_PATH.search(line):
            problem(rel, n, "absolute home-directory path")


def main():
    files = tracked_files()
    check_manifest(files)
    ids = {}
    texts = {}
    for rel in files:
        text = read(rel)
        if text is None:
            continue
        texts[rel] = text
        if rel.endswith(".md") and rel != "README.md" and not GENERATED.match(rel):
            check_document(rel, text, ids)
    for rel, text in texts.items():
        if rel.endswith(".md"):
            check_references(rel, text, ids)
            check_links(rel, text)
        if (ROOT / rel).stat().st_size < 5_000_000:
            check_secrets(rel, text)
    if problems:
        print("\n".join(problems))
        print("\n%d problem(s) found." % len(problems))
        return 1
    print("Documentation check passed: %d tracked files, %d documents." % (len(files), len(ids)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
