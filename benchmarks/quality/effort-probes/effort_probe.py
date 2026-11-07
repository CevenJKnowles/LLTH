"""Reasoning-effort probe (copy of the script as run on 2026-11-05; personal paths replaced by $LLTH_HOME and <scoring-page>, the designer's personal scoring aid that holds parse_sheet)

Reasoning-effort probe for one model on llama-server (exploration, ADR-004 4a).

Sends selected frozen prompts at several reasoning efforts with round-1 sampling
and seeds, saves each raw response, and prints a summary row per call.
Usage: python3 -I -B effort_probe.py OUT_DIR
"""
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, "<scoring-page>")
from build_page import parse_sheet

SHEET = "$LLTH_HOME/benchmarks/quality/scoring/sheet-quality-round1.md"
ORDER = [f"{c}{i}" for c in "WPRD" for i in range(1, 6)]
PROMPTS = ["W1", "W2", "W4", "D1", "D4", "P1", "R2"]
EFFORTS = ["low", "medium", "high"]
TEMP_LIMIT = 89  # stop before the 92 C safety cut-off

out = Path(sys.argv[1])
out.mkdir(exist_ok=True)
text = {p["id"]: p["prompt"] for p in parse_sheet(Path(SHEET).read_text())}


def ntok(s):
    if not s:
        return 0
    req = urllib.request.Request("http://127.0.0.1:8080/tokenize", data=json.dumps({"content": s}).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return len(json.load(r)["tokens"])


def gpu_temp():
    r = subprocess.run(["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader"],
                       capture_output=True, text=True)
    return int(r.stdout.strip())


print("prompt effort reasoning_tok answer_tok gen_tok_s total_s finish split_ok gpu_c", flush=True)
for pid in PROMPTS:
    for effort in EFFORTS:
        while gpu_temp() > 60:  # let the GPU cool between calls
            time.sleep(5)
        body = {
            "messages": [{"role": "user", "content": text[pid]}],
            "temperature": 1.0, "top_p": 0.95, "seed": 1001 + ORDER.index(pid),
            "max_tokens": 32768, "reasoning_effort": effort, "cache_prompt": False, "stream": False,
        }
        req = urllib.request.Request("http://127.0.0.1:8080/v1/chat/completions",
                                     data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=1800) as r:
            resp = json.load(r)
        wall = time.time() - t0
        (out / f"{pid}_{effort}.json").write_text(json.dumps(resp, ensure_ascii=False, indent=1))
        msg = resp["choices"][0]["message"]
        content, reasoning = msg.get("content") or "", msg.get("reasoning_content") or ""
        tm = resp.get("timings", {})
        split_ok = bool(content.strip()) and "</ifm|think>" not in content
        print(pid, effort, ntok(reasoning), ntok(content), round(tm.get("predicted_per_second", 0), 1),
              round(wall, 1), resp["choices"][0]["finish_reason"], split_ok, gpu_temp(),
              f"generated={tm.get('predicted_n')}", flush=True)
        if gpu_temp() >= TEMP_LIMIT:
            print("STOP: GPU at limit", flush=True)
            sys.exit(3)
