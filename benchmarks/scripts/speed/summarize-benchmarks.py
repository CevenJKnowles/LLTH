#!/usr/bin/env python3
"""Summarise the llama-bench logs in $LLTH_HOME/benchmarks/speed/ as markdown tables.

Usage (standard library only; run with -I so no local files are imported):
    python3 -I $LLTH_HOME/benchmarks/scripts/speed/summarize-benchmarks.py            # all logs
    python3 -I .../summarize-benchmarks.py round2                                           # logs whose name contains 'round2'

Each log is a sequence of blocks written by bench_wrap.sh:
    ### label / start: ... / cmd: ... / <llama-bench markdown table> / peaks: ... / end: ...
For every block this prints the settings recovered from the command line (depth, GPU layers, cache types,
ubatch, threads, ...), the prompt-reading and generation speeds (tokens/s), and peak VRAM and GPU temperature.
A block without result rows is shown as 'no result' (the model did not load, or the run was stopped).
"""
import os
import re
import sys
from pathlib import Path

# The project root is two levels above this script unless LLTH_HOME says otherwise
LOG_DIR = Path(os.environ.get("LLTH_HOME", Path(__file__).resolve().parents[3])) / "benchmarks" / "speed"


def flag(cmd: str, name: str, default: str = "-") -> str:
    m = re.search(rf"(?:^|\s){re.escape(name)}\s+(\S+)", cmd)
    return m.group(1) if m else default


def parse_block(block: str) -> dict:
    lines = block.split("\n")
    title = lines[0].strip()
    cmd = next((l[5:].strip() for l in lines if l.startswith("cmd:")), "")
    start = next((l for l in lines if l.startswith("start:")), "")
    results = {}
    for l in lines:
        if l.startswith("|") and "---" not in l and "t/s" not in l:
            cells = [c.strip() for c in l.strip("|").split("|")]
            if len(cells) >= 2 and re.match(r"^(pp|tg)\d+", cells[-2]):
                kind = cells[-2].split()[0][:2]
                results[kind] = cells[-1].split(" ±")[0]
    peaks = re.search(r"peaks: vram_MiB=(\d+) gpu_temp_C=(\d+)", block)
    safety = "SAFETY STOP" in block
    env = re.search(r"governor=(\S+)(?: epp=(\S+))?", start)
    return {
        "title": title, "cmd": cmd, "results": results,
        "vram": peaks.group(1) if peaks else "-", "temp": peaks.group(2) if peaks else "-",
        "safety": safety, "gov": (env.group(1) + ("/" + env.group(2) if env and env.group(2) else "")) if env else "-",
        "start": start.split()[1][:19] if len(start.split()) > 1 else "-",
    }


def main() -> None:
    needle = sys.argv[1] if len(sys.argv) > 1 else ""
    for log in sorted(LOG_DIR.glob("*.log")):
        if needle not in log.name:
            continue
        text = log.read_text(encoding="utf-8", errors="replace")
        blocks = [b for b in text.split("### ")[1:]]
        if not blocks:
            continue
        print(f"\n## {log.name}\n")
        print("| Run | Depth | GPU layers | Cache K/V | ub | threads | Other | Reading t/s | Generation t/s | Peak VRAM MiB | Peak GPU C | CPU policy |")
        print("|---|---|---|---|---|---|---|---|---|---|---|---|")
        for b in blocks:
            r = parse_block(b)
            c = r["cmd"]
            other = []
            if flag(c, "-nkvo", "0") not in ("0", "-"):
                other.append("cache in RAM")
            ot = re.search(r'-ot\s+("[^"]*"|\S+)', c)
            if ot:
                other.append("override " + ot.group(1).strip('"'))
            name = re.sub(r"\s+\[governor=.*$", "", r["title"])[:48]
            res = r["results"]
            if not res:
                rd, gen = "no result", ("STOPPED" if r["safety"] else "-")
            else:
                rd, gen = res.get("pp", "-"), res.get("tg", "-")
            print(f"| {name} | {flag(c, '-d', '0')} | {flag(c, '-ngl')} | {flag(c, '-ctk')}/{flag(c, '-ctv')} | "
                  f"{flag(c, '-ub', '512')} | {flag(c, '-t', '6')} | {', '.join(other) or '-'} | {rd} | {gen} | "
                  f"{r['vram']} | {r['temp']} | {r['gov']} |")


if __name__ == "__main__":
    main()
