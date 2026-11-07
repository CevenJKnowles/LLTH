#!/usr/bin/env python3
"""quality_blind.py v1.3 - blinding, routing and tally for the quality and steward tests (ADR-004 section 5b).

Standard library only. Run as:  python3 -I quality_blind.py <command> ...

Commands
  make     build a blind scoring sheet, a sealed key and a score template from run folders
  reveal   merge the key, the designer's scores and the measurements into result tables
  routing  steward test: routing accuracy against the designer's labels (all prompts and uncontested only)
  stats    cost measures per run (reasoning and answer tokens, time to the final answer, failures)

The designer sees the FINAL ANSWER ONLY (never the reasoning) under random labels A, B, C...,
re-shuffled for every prompt. The key is written to its own file (mode 0600) and is not opened
until every answer has been scored. Run folders are the ones written by quality_run.py; only the
base result file <ID>.json is used (a --redo file <ID>.redoN.json is ignored unless it is renamed).

Routing rule (fixed in advance, ADR-004 section 5b item 5):
  escalated  the final answer, with whitespace, quotes and punctuation stripped and compared
             without regard to case, is exactly ESCALATE
  mixed      the upper-case word ESCALATE appears together with other text
  answered   otherwise
  no_answer  the run produced no final answer (for example the budget ended inside the reasoning)
Mixed counts as an escalation in the headline figure and is also reported separately.
K2 end-of-thinking marker (v1.2, KI-026): at reduced reasoning effort llama-server may leave `content`
empty and put the answer in the reasoning after </ifm|think>; the answer is then recovered from there.
If the model wrote its working inside the answer before the marker, the sheet still shows the answer
as stored, but the routing rule reads only the text after the marker.
Interpretation note: "contains ESCALATE" is read as the upper-case word ESCALATE, so that an
ordinary answer that discusses escalation in lower case (R5, for example) is not misread.
"""
import argparse
import csv
import json
import os
import re
import secrets
import statistics
import sys
from pathlib import Path

VERSION = "1.3"
THINK_END = "</ifm|think>"  # K2 Horizon end-of-thinking marker (KI-026)
ROOT = Path(__file__).resolve().parents[3]


def portable(path):
    """Path under the project folder as $LLTH_HOME/..., otherwise the resolved path."""
    p = Path(path).resolve()
    try:
        return "$LLTH_HOME/" + p.relative_to(ROOT).as_posix()
    except ValueError:
        return str(p)


def resolve(path):
    """Inverse of portable(): replaces a leading $LLTH_HOME with the project folder."""
    return Path(str(path).replace("$LLTH_HOME", str(ROOT), 1))
QDIR = ROOT / "benchmarks" / "quality"
GROUPS = {"W": "writing", "P": "Python", "R": "reasoning", "D": "deceptive"}


# ---------------------------------------------------------------- shared
def load_run(run_dir):
    run_dir = Path(run_dir)
    results = {}
    for p in sorted(run_dir.glob("*.json")):
        name = p.name
        if name == "run-header.json" or name.endswith(".partial.json") or ".redo" in name or ".failed" in name:
            continue
        data = json.loads(p.read_text())
        results[data["id"]] = data
    if not results:
        sys.exit("no results in " + str(run_dir))
    return results


def final_answer(res):
    """The answer as stored; if `content` is empty, the text after the last end-of-thinking marker in the reasoning."""
    content = (res.get("content") or "").strip()
    if content:
        return content
    reasoning = res.get("reasoning_text") or ""
    return reasoning.rsplit(THINK_END, 1)[1].strip() if THINK_END in reasoning else ""


def routed_answer(res):
    """What the routing rule reads: the final answer without any working written before the marker."""
    answer = final_answer(res)
    return answer.rsplit(THINK_END, 1)[1].strip() if THINK_END in answer else answer


def classify_routing(content):
    t = (content or "").strip()
    if not t:
        return "no_answer"
    core = re.sub(r"^[\W_]+|[\W_]+$", "", t).upper()
    if core == "ESCALATE":
        return "escalated"
    if re.search(r"\bESCALATE\b", t):
        return "mixed"
    return "answered"


def load_labels(path):
    labels = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            labels[row["id"]] = {"label": row["label"].strip().lower(), "contested": row["contested"].strip().lower() in ("yes", "true", "1")}
    return labels


def fence_for(text):
    longest = max([len(m) for m in re.findall(r"`+", text)] + [2])
    return "`" * (longest + 1)


def median(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


def fmt(x, nd=1):
    return "-" if x is None else (("%." + str(nd) + "f") % x if isinstance(x, float) else str(x))


def md_table(rows, header):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(out)


def run_name(run_dir):
    return Path(run_dir).name


# ---------------------------------------------------------------- make
def cmd_make(a):
    runs = {run_name(d): load_run(d) for d in a.run_dir}
    if len(runs) != len(a.run_dir):
        sys.exit("run folders must have distinct names")
    labels = load_labels(a.labels_file) if a.labels_file else None
    if a.mode == "steward" and not labels:
        sys.exit("steward mode needs --labels-file (only answered easy prompts are scored)")
    out_dir = Path(a.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    sheet_path, key_path, csv_path = (out_dir / ("sheet-%s.md" % a.name), out_dir / ("key-%s.json" % a.name), out_dir / ("scores-%s.csv" % a.name))
    for p in (sheet_path, key_path, csv_path):
        if p.exists():
            sys.exit("%s exists: choose another --name (nothing is overwritten)" % p)
    rng = secrets.SystemRandom()
    prompt_ids = []
    first = next(iter(runs.values()))
    order = sorted(first, key=lambda k: (list(GROUPS).index(k[0]), int(k[1:])))
    sheet, key, rows = [], {}, []
    sheet.append("# Blind scoring sheet: %s\n\nScore each answer 1 to 5 for overall usefulness in `scores-%s.csv`. Only the final answers are shown. Run the Python yourself. Mark `looped` as yes if an answer repeats itself. Do not open `key-%s.json` until every row is scored.\n" % (a.name, a.name, a.name))
    for pid in order:
        entries = []
        for name, res in runs.items():
            if pid not in res:
                continue
            r = res[pid]
            ans = final_answer(r)
            if a.mode == "steward":
                if classify_routing(routed_answer(r)) != "answered" or labels[pid]["label"] != "easy":
                    continue
            entries.append((name, ans))
        if not entries:
            continue
        rng.shuffle(entries)
        prompt_text = next(iter(runs.values()))[pid]["prompt_text"] if pid in next(iter(runs.values())) else ""
        sheet.append("\n---\n\n## %s\n\n**Prompt**\n\n%s\n" % (pid, "\n".join("> " + l for l in prompt_text.splitlines())))
        key[pid] = {}
        for i, (name, ans) in enumerate(entries):
            lab = chr(ord("A") + i)
            key[pid][lab] = name
            if ans:
                f = fence_for(ans)
                sheet.append("\n### Answer %s (%s)\n\n%stext\n%s\n%s\n" % (lab, pid, f, ans, f))
            else:
                sheet.append("\n### Answer %s (%s)\n\n_[no final answer was produced]_\n" % (lab, pid))
            rows.append([pid, lab, "", "", ""])
    sheet_path.write_text("\n".join(sheet))
    key_path.write_text(json.dumps({"name": a.name, "mode": a.mode, "script": "quality_blind.py v" + VERSION,
                                    "runs": {n: portable(d) for n, d in zip(runs, a.run_dir)}, "key": key}, indent=1))
    os.chmod(key_path, 0o600)
    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["prompt_id", "label", "score", "looped", "notes"])
        w.writerows(rows)
    print("wrote %s, %s (sealed, mode 0600), %s: %d answers over %d prompts" % (sheet_path, key_path, csv_path, len(rows), len(key)))


# ---------------------------------------------------------------- stats
def run_stats(res_by_id):
    rs = list(res_by_id.values())
    return {
        "n": len(rs),
        "reasoning_tok_median": median([r["tokens"]["reasoning_tokenized"] for r in rs]),
        "answer_tok_median": median([r["tokens"]["content_tokenized"] for r in rs]),
        "time_median": median([r["times_s"]["to_final_answer"] for r in rs]),
        "time_total_h": sum(r["times_s"]["to_final_answer"] for r in rs) / 3600,
        "not_finished": sum(1 for r in rs if r.get("did_not_finish_within_budget")),
        "no_answer": sum(1 for r in rs if not final_answer(r)),
        "aborted": sum(1 for r in rs if r["status"].startswith("aborted")),
        "errors": sum(1 for r in rs if r["status"] == "error"),
        "peak_temp": max([r["peaks"]["gpu_temp_c"] for r in rs if r["peaks"]["gpu_temp_c"] is not None] or [None]) if any(r["peaks"]["gpu_temp_c"] is not None for r in rs) else None,
        "min_ram": min([r["peaks"]["min_mem_available_mib"] for r in rs if r["peaks"]["min_mem_available_mib"] is not None] or [None]) if any(r["peaks"]["min_mem_available_mib"] is not None for r in rs) else None,
    }


def stats_table(named):
    rows = []
    for name, res in named.items():
        s = run_stats(res)
        rows.append([name, s["n"], fmt(s["reasoning_tok_median"], 0), fmt(s["answer_tok_median"], 0), fmt(s["time_median"], 0),
                     fmt(s["time_total_h"], 2), s["not_finished"], s["no_answer"], s["aborted"] + s["errors"], fmt(s["peak_temp"], 0), fmt(s["min_ram"], 0)])
    return md_table(rows, ["run", "prompts", "median reasoning tok", "median answer tok", "median time to final answer (s)",
                           "total time (h)", "hit budget", "no final answer", "aborted or error", "peak GPU C", "min RAM free MiB"])


def cmd_stats(a):
    named = {run_name(d): load_run(d) for d in a.run_dir}
    print(stats_table(named))


# ---------------------------------------------------------------- routing
def cmd_routing(a):
    labels = load_labels(a.labels_file)
    named = {run_name(d): load_run(d) for d in a.run_dir}
    rows, detail = [], []
    for name, res in named.items():
        for scope, ids in (("all %d" % len(labels), list(labels)), ("uncontested %d" % sum(1 for v in labels.values() if not v["contested"]), [k for k, v in labels.items() if not v["contested"]])):
            ok = fe = me = noans = mixed = n = 0
            for pid in ids:
                if pid not in res:
                    continue
                n += 1
                c = classify_routing(routed_answer(res[pid]))
                lab = labels[pid]["label"]
                if c == "no_answer":
                    noans += 1
                    continue
                esc = c in ("escalated", "mixed")
                mixed += c == "mixed"
                if (lab == "easy" and not esc) or (lab == "hard" and esc):
                    ok += 1
                elif lab == "easy" and esc:
                    fe += 1
                else:
                    me += 1
            rows.append([name, scope, n, "%d (%.0f%%)" % (ok, 100 * ok / n) if n else "-", fe, me, noans, mixed])
        for pid in labels:
            if pid in res:
                detail.append([name, pid, labels[pid]["label"] + (" (contested)" if labels[pid]["contested"] else ""), classify_routing(routed_answer(res[pid]))])
    print(md_table(rows, ["run", "scope", "prompts run", "routed as labelled", "false escalations (easy escalated)", "missed escalations (hard answered)", "no final answer", "mixed (counted as escalated)"]))
    if a.detail:
        print()
        print(md_table(detail, ["run", "prompt", "designer label", "routing"]))


# ---------------------------------------------------------------- reveal
def cmd_reveal(a):
    keyfile = json.loads(Path(a.key).read_text())
    key = keyfile["key"]
    scores = {}
    missing = []
    with open(a.scores, newline="") as f:
        for row in csv.DictReader(f):
            s = row["score"].strip()
            if not s:
                missing.append((row["prompt_id"], row["label"]))
                continue
            if not re.fullmatch(r"[1-5]", s):
                sys.exit("score %r for %s/%s is not an integer from 1 to 5" % (s, row["prompt_id"], row["label"]))
            scores[(row["prompt_id"], row["label"])] = (int(s), row["looped"].strip().lower() in ("yes", "y", "true", "1"))
    if missing and not a.allow_incomplete:
        sys.exit("%d answers are not scored yet (first: %s/%s). Finish scoring, or pass --allow-incomplete" % (len(missing), missing[0][0], missing[0][1]))
    labels = load_labels(a.labels_file) if a.labels_file else None
    per_run = {}
    for pid, mp in key.items():
        for lab, name in mp.items():
            if (pid, lab) in scores:
                s, looped = scores[(pid, lab)]
                per_run.setdefault(name, []).append((pid, s, looped))
    rows = []
    for name, items in per_run.items():
        def mean(sel):
            v = [s for pid, s, _ in items if sel(pid)]
            return (sum(v) / len(v)) if v else None
        row = [name, len(items), fmt(mean(lambda p: True), 2)]
        for g in "WPRD":
            row.append(fmt(mean(lambda p, g=g: p[0] == g), 2))
        if labels:
            row.append(fmt(mean(lambda p: labels[p]["label"] == "easy"), 2))
            row.append(fmt(mean(lambda p: labels[p]["label"] == "hard"), 2))
            row.append(fmt(mean(lambda p: not labels[p]["contested"]), 2))
        row.append(sum(1 for _, _, lp in items if lp))
        rows.append(row)
    header = ["run", "scored", "mean (all)"] + ["mean " + GROUPS[g] for g in "WPRD"]
    if labels:
        header += ["mean easy", "mean hard", "mean uncontested"]
    header += ["marked looped"]
    out = ["# Result: %s (%s)\n" % (keyfile["name"], keyfile["mode"]), md_table(rows, header)]
    named = {n: load_run(resolve(d)) for n, d in keyfile["runs"].items() if n in per_run}
    out += ["", "## Cost measures", "", stats_table(named)]
    text = "\n".join(out)
    print(text)
    if a.save:
        Path(a.save).write_text(text + "\n")
        print("\nsaved to " + a.save)


def main():
    ap = argparse.ArgumentParser(description="Blinding, routing and tally (ADR-004 section 5b)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("make")
    m.add_argument("--name", required=True)
    m.add_argument("--mode", choices=["quality", "steward"], default="quality")
    m.add_argument("--run-dir", action="append", required=True)
    m.add_argument("--labels-file", default=str(QDIR / "labels.csv"))
    m.add_argument("--out-dir", default=str(QDIR / "scoring"))
    m.set_defaults(fn=cmd_make)
    r = sub.add_parser("reveal")
    r.add_argument("--key", required=True)
    r.add_argument("--scores", required=True)
    r.add_argument("--labels-file", default=str(QDIR / "labels.csv"))
    r.add_argument("--allow-incomplete", action="store_true")
    r.add_argument("--save", default=None)
    r.set_defaults(fn=cmd_reveal)
    t = sub.add_parser("routing")
    t.add_argument("--run-dir", action="append", required=True)
    t.add_argument("--labels-file", default=str(QDIR / "labels.csv"))
    t.add_argument("--detail", action="store_true")
    t.set_defaults(fn=cmd_routing)
    s = sub.add_parser("stats")
    s.add_argument("--run-dir", action="append", required=True)
    s.set_defaults(fn=cmd_stats)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
