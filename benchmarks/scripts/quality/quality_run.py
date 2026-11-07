#!/usr/bin/env python3
"""quality_run.py v1.0 - runner for the quality and steward tests (ADR-004 section 5b).

A CLIENT of a llama-server that the designer has already started. It sends the
approved prompts one at a time and records everything; it does no scoring.

  * Standard library only. Run as:  python3 -I quality_run.py ...
  * Talks to 127.0.0.1 only (the host cannot be changed). The port defaults to
    8080; --port exists so the script can be tested against a mock server.
  * Does not start or stop servers, does not execute model output, and contacts
    nothing else.
  * Safety limits (ADR-004 section 4a): a request is aborted if the GPU reaches
    92 C, available RAM falls below 1,500 MiB, or --timeout-min passes. A thermal
    or RAM abort also stops the whole run (exit code 3).
  * Resumable: an existing result file is never overwritten (--redo writes a new
    file with a numbered suffix). Failed attempts (server lost, stream ended early,
    thermal or RAM abort) are kept as <ID>.failed-<time>-<status>.json, are not
    results, and the prompt is retried on resume (v1.1; exit code 4 for a lost server).

Results: <out-root>/<model-id>_<config-id>/<PROMPT-ID>.json, plus run-header.json
and run.log in the same folder.

Example (the K2 Horizon 0.9B pilot; the server was started by the designer):
  python3 -I quality_run.py --model-id k2-0p9b --config-id high \\
    --expect-sha256 <sha of prompts.md> --max-tokens 32768 \\
    --temperature 0.6 --top-p 0.95 \\
    --extra-json '{"reasoning_effort":"high"}' --only W1,P2 \\
    --server-command '<the exact llama-server command>'
"""
import argparse
import datetime
import hashlib
import http.client
import json
import os
import re
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

VERSION = "1.1"
HOST = "127.0.0.1"
ROOT = Path(__file__).resolve().parents[3]  # $LLTH_HOME: quality/ -> scripts/ -> benchmarks/ -> root
GPU_LIMIT_C = 92
RAM_LIMIT_MIB = 1500
EXPECTED_PROMPTS = 20
FAILED_STATUSES = ("error", "incomplete", "aborted_temp", "aborted_ram")


# ---------------------------------------------------------------- prompts
def parse_prompts(text):
    """Return [{'id','title','text'}] from prompts.md (the blockquote under each ### heading)."""
    lines = text.splitlines()
    heading = re.compile(r"^### ([WPRD]\d) · (.*)$")
    out, i = [], 0
    while i < len(lines):
        m = heading.match(lines[i])
        if not m:
            i += 1
            continue
        pid, title = m.group(1), m.group(2).strip()
        i += 1
        while i < len(lines) and not lines[i].startswith("**Prompt"):
            if heading.match(lines[i]):
                raise ValueError("no prompt block under " + pid)
            i += 1
        if i >= len(lines):
            raise ValueError("no prompt block under " + pid)
        i += 1
        while i < len(lines) and lines[i].strip() == "":
            i += 1
        quote = []
        while i < len(lines) and lines[i].startswith(">"):
            piece = lines[i][1:]
            if piece.startswith(" "):
                piece = piece[1:]
            quote.append(piece)
            i += 1
        text_ = "\n".join(quote).strip()
        if not text_:
            raise ValueError("empty prompt for " + pid)
        out.append({"id": pid, "title": title, "text": text_})
    ids = [p["id"] for p in out]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate prompt ids")
    return out


# ---------------------------------------------------------------- machine state
def gpu_state():
    """(temperature C, memory used MiB) or (None, None)."""
    try:
        r = subprocess.run(
            ["nvidia-smi", "--query-gpu=temperature.gpu,memory.used", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=10)
        t, m = [x.strip() for x in r.stdout.strip().splitlines()[0].split(",")]
        return int(t), int(m)
    except Exception:
        return None, None


def mem_available_mib():
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemAvailable:"):
                    return int(line.split()[1]) // 1024
    except Exception:
        pass
    return None


def read_text(path):
    try:
        return Path(path).read_text().strip()
    except Exception:
        return None


def run_cmd(cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return r.stdout.strip()
    except Exception:
        return None


def browser_count():
    out = run_cmd(["ps", "-eo", "comm"]) or ""
    return len([c for c in out.splitlines() if re.search(r"chrome|firefox|brave", c, re.I)])


def machine_state():
    t, m = gpu_state()
    return {
        "gpu_temp_c": t,
        "gpu_mem_used_mib": m,
        "mem_available_mib": mem_available_mib(),
        "power_profile": run_cmd(["busctl", "get-property", "net.hadess.PowerProfiles",
                                  "/net/hadess/PowerProfiles", "net.hadess.PowerProfiles", "ActiveProfile"]),
        "energy_performance_preference": read_text("/sys/devices/system/cpu/cpu0/cpufreq/energy_performance_preference"),
        "browser_processes": browser_count(),
        "free_m": run_cmd(["free", "-m"]),
    }


# ---------------------------------------------------------------- HTTP helpers
def http_json(port, method, path, body=None, timeout=30):
    conn = http.client.HTTPConnection(HOST, port, timeout=timeout)
    try:
        data = json.dumps(body) if body is not None else None
        conn.request(method, path, data, {"Content-Type": "application/json"} if data else {})
        resp = conn.getresponse()
        raw = resp.read()
        if resp.status != 200:
            raise RuntimeError("HTTP %d from %s: %r" % (resp.status, path, raw[:300]))
        return json.loads(raw) if raw else {}
    finally:
        conn.close()


def count_tokens(port, text):
    if not text:
        return 0
    try:
        r = http_json(port, "POST", "/tokenize", {"content": text, "add_special": False})
        return len(r.get("tokens", []))
    except Exception:
        return None


class Job:
    def __init__(self):
        self.reasoning, self.content = [], []
        self.t = {}
        self.usage = None
        self.timings = None
        self.finish = None
        self.error = None
        self.done = False
        self.sock = None
        self.aborted = False


def worker(job, port, body, read_timeout):
    try:
        conn = http.client.HTTPConnection(HOST, port, timeout=read_timeout)
        conn.connect()
        job.sock = conn.sock  # own reference: http.client drops conn.sock after a close-delimited response
        conn.request("POST", "/v1/chat/completions", json.dumps(body), {"Content-Type": "application/json"})
        resp = conn.getresponse()
        if resp.status != 200:
            job.error = "HTTP %d: %r" % (resp.status, resp.read()[:500])
            return
        job.t["headers"] = time.monotonic()
        while True:
            line = resp.readline()
            if not line:
                break
            line = line.decode("utf-8", "replace").strip()
            if not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if data == "[DONE]":
                break
            try:
                ev = json.loads(data)
            except ValueError:
                continue
            if ev.get("usage"):
                job.usage = ev["usage"]
            if ev.get("timings"):
                job.timings = ev["timings"]
            for ch in ev.get("choices") or []:
                d = ch.get("delta") or {}
                now = time.monotonic()
                rc, c = d.get("reasoning_content"), d.get("content")
                if rc:
                    job.t.setdefault("first_token", now)
                    job.t.setdefault("first_reasoning", now)
                    job.reasoning.append(rc)
                if c:
                    job.t.setdefault("first_token", now)
                    job.t.setdefault("first_content", now)
                    job.content.append(c)
                if ch.get("finish_reason"):
                    job.finish = ch["finish_reason"]
    except Exception as e:  # noqa: BLE001 - recorded, not hidden
        if not job.aborted:
            job.error = repr(e)
    finally:
        job.t["end"] = time.monotonic()
        job.done = True


def abort_job(job):
    job.aborted = True
    try:
        if job.sock is not None:
            job.sock.shutdown(socket.SHUT_RDWR)  # wakes the reader thread; the server stops generating on disconnect
    except OSError:
        pass


# ---------------------------------------------------------------- one prompt
def build_body(args, prompt, seed, system_text):
    messages = []
    if system_text:
        messages.append({"role": "system", "content": system_text})
    messages.append({"role": "user", "content": prompt["text"]})
    body = {
        "model": "local",
        "messages": messages,
        "stream": True,
        "stream_options": {"include_usage": True},
        "max_tokens": args.max_tokens,
        "temperature": args.temperature,
        "top_p": args.top_p,
        "seed": seed,
        "cache_prompt": False,
    }
    if args.top_k is not None:
        body["top_k"] = args.top_k
    if args.min_p is not None:
        body["min_p"] = args.min_p
    if args.chat_template_kwargs:
        body["chat_template_kwargs"] = json.loads(args.chat_template_kwargs)
    if args.extra_json:
        body.update(json.loads(args.extra_json))
    return body


def log(out_dir, msg):
    line = "[%s] %s" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg)
    print(line, flush=True)
    with open(out_dir / "run.log", "a") as f:
        f.write(line + "\n")


def run_prompt(args, prompt, seed, system_text, out_dir, out_path):
    body = build_body(args, prompt, seed, system_text)
    job = Job()
    th = threading.Thread(target=worker, args=(job, args.port, body, args.read_timeout), daemon=True)
    started_at = datetime.datetime.now().isoformat(timespec="seconds")
    t0 = time.monotonic()
    job.t["start"] = t0
    samples, peak_temp, peak_vram, min_ram = [], None, None, None
    status, last = None, -1e9
    th.start()
    while th.is_alive():
        th.join(timeout=1.0)
        now = time.monotonic()
        if now - last >= args.sample_interval:
            last = now
            temp, vram = gpu_state()
            ram = mem_available_mib()
            samples.append({"t_s": round(now - t0, 1), "gpu_temp_c": temp, "gpu_mem_mib": vram, "mem_available_mib": ram})
            if temp is not None:
                peak_temp = temp if peak_temp is None else max(peak_temp, temp)
            if vram is not None:
                peak_vram = vram if peak_vram is None else max(peak_vram, vram)
            if ram is not None:
                min_ram = ram if min_ram is None else min(min_ram, ram)
            if temp is not None and temp >= GPU_LIMIT_C:
                status = "aborted_temp"
            elif ram is not None and ram < RAM_LIMIT_MIB:
                status = "aborted_ram"
            save_partial(out_path, prompt, job, samples, t0)
        if status is None and now - t0 > args.timeout_min * 60:
            status = "aborted_timeout"
        if status:
            abort_job(job)
            break
    th.join(timeout=15)
    t_end = job.t.get("end", time.monotonic())
    if status is None:
        # a stream that ends without a finish reason means the server went away mid-answer: not a complete result
        status = "error" if job.error else ("incomplete" if job.finish is None else "complete")
    reasoning = "".join(job.reasoning)
    content = "".join(job.content)
    rt = count_tokens(args.port, reasoning)
    ct = count_tokens(args.port, content)
    usage = job.usage or {}

    def rel(key):
        return round(job.t[key] - t0, 3) if key in job.t else None

    result = {
        "id": prompt["id"], "title": prompt["title"], "prompt_text": prompt["text"],
        "system_prompt": system_text, "request": body, "seed": seed,
        "started_at": started_at, "status": status, "error": job.error,
        "finish_reason": job.finish,
        "did_not_finish_within_budget": job.finish == "length",
        "reasoning_split_in_response": bool(reasoning),
        "reasoning_text": reasoning, "content": content,
        "usage": job.usage, "timings": job.timings,
        "tokens": {"reasoning_tokenized": rt, "content_tokenized": ct,
                   "completion_tokens_usage": usage.get("completion_tokens"),
                   "prompt_tokens_usage": usage.get("prompt_tokens"),
                   "method": "server /tokenize on the streamed text; usage as reported by the server"},
        "times_s": {"to_first_token": rel("first_token"), "to_first_reasoning": rel("first_reasoning"),
                    "to_first_answer_token": rel("first_content"),
                    "to_final_answer": round(t_end - t0, 3)},
        "peaks": {"gpu_temp_c": peak_temp, "gpu_mem_mib": peak_vram, "min_mem_available_mib": min_ram},
        "samples": samples,
    }
    part = out_path.with_suffix(".partial.json")
    final_path = out_path
    if status in FAILED_STATUSES:
        # kept for the record, but under a name the resume logic and the tally do not treat as a result
        final_path = out_path.with_name("%s.failed-%s-%s.json" % (out_path.stem.split(".")[0], datetime.datetime.now().strftime("%Y%m%d-%H%M%S"), status))
    tmp = final_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(result, indent=1, ensure_ascii=False))
    os.replace(tmp, final_path)
    if part.exists():
        part.unlink()
    return result


def save_partial(out_path, prompt, job, samples, t0):
    try:
        part = out_path.with_suffix(".partial.json")
        tmp = part.with_suffix(".tmp")
        tmp.write_text(json.dumps({
            "id": prompt["id"], "elapsed_s": round(time.monotonic() - t0, 1),
            "reasoning_chars": sum(len(x) for x in job.reasoning),
            "content_chars": sum(len(x) for x in job.content),
            "reasoning_text": "".join(job.reasoning), "content": "".join(job.content),
            "samples": samples}, ensure_ascii=False))
        os.replace(tmp, part)
    except Exception:
        pass


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description="Quality and steward test runner (ADR-004 section 5b)")
    ap.add_argument("--model-id", required=True, help="short id, for example k2-0p9b")
    ap.add_argument("--config-id", required=True, help="for example high, steward-low, nothink")
    ap.add_argument("--prompts", default=str(ROOT / "benchmarks" / "prompts.md"))
    ap.add_argument("--expect-sha256", required=True, help="SHA-256 of the approved prompts file")
    ap.add_argument("--out-root", default=str(ROOT / "benchmarks" / "quality"))
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--max-tokens", type=int, required=True)
    ap.add_argument("--temperature", type=float, required=True)
    ap.add_argument("--top-p", type=float, required=True)
    ap.add_argument("--top-k", type=int, default=None, help="if omitted the server default applies (recorded in the header)")
    ap.add_argument("--min-p", type=float, default=None, help="if omitted the server default applies (recorded in the header)")
    ap.add_argument("--seed-base", type=int, default=1000, help="seed = base + the prompt's position (W1 = base+1)")
    ap.add_argument("--chat-template-kwargs", default=None, help="JSON object sent as chat_template_kwargs")
    ap.add_argument("--extra-json", default=None, help="JSON object merged into the request body (for example reasoning_effort)")
    ap.add_argument("--system-prompt", default=None)
    ap.add_argument("--system-prompt-file", default=None)
    ap.add_argument("--server-command", default="", help="the exact llama-server command, recorded in the header")
    ap.add_argument("--only", default=None, help="comma-separated prompt ids, for example W1,P2")
    ap.add_argument("--timeout-min", type=float, default=90.0, help="per-request limit in minutes")
    ap.add_argument("--read-timeout", type=float, default=3600.0, help="socket read timeout in seconds")
    ap.add_argument("--sample-interval", type=float, default=10.0, help="seconds between temperature/RAM samples")
    ap.add_argument("--max-start-temp", type=int, default=50, help="GPU temperature allowed at the start of a run (ADR-004 section 3)")
    ap.add_argument("--allow-browser", action="store_true", help="run although a browser process is open (ADR-004 section 3 says none)")
    ap.add_argument("--redo", action="store_true", help="write a new numbered result for prompts that already have one")
    ap.add_argument("--list", action="store_true", help="parse the prompts and print them, then exit")
    ap.add_argument("--dry-run", action="store_true", help="print the first request body and exit")
    args = ap.parse_args()

    raw = Path(args.prompts).read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != args.expect_sha256.lower():
        sys.exit("prompts file checksum %s does not match --expect-sha256 %s: refusing to run" % (sha, args.expect_sha256))
    prompts = parse_prompts(raw.decode("utf-8"))
    if len(prompts) != EXPECTED_PROMPTS:
        sys.exit("expected %d prompts, parsed %d" % (EXPECTED_PROMPTS, len(prompts)))
    position = {p["id"]: i + 1 for i, p in enumerate(prompts)}
    if args.list:
        for p in prompts:
            print("%s  seed %d  %5d chars  %s" % (p["id"], args.seed_base + position[p["id"]], len(p["text"]), p["title"]))
        return
    if args.only:
        want = [x.strip() for x in args.only.split(",") if x.strip()]
        unknown = [x for x in want if x not in position]
        if unknown:
            sys.exit("unknown prompt ids: %s" % unknown)
        prompts = [p for p in prompts if p["id"] in want]

    system_text = args.system_prompt
    if args.system_prompt_file:
        system_text = Path(args.system_prompt_file).read_text().strip()

    if args.dry_run:
        print(json.dumps(build_body(args, prompts[0], args.seed_base + position[prompts[0]["id"]], system_text), indent=1))
        return

    out_dir = Path(args.out_root) / ("%s_%s" % (args.model_id, args.config_id))
    out_dir.mkdir(parents=True, exist_ok=True)

    state = machine_state()
    if state["browser_processes"] and not args.allow_browser:
        sys.exit("a browser process is running (ADR-004 section 3): close it, or pass --allow-browser")
    if state["gpu_temp_c"] is not None and state["gpu_temp_c"] > args.max_start_temp:
        sys.exit("GPU is at %d C, above the start limit of %d C: let it cool" % (state["gpu_temp_c"], args.max_start_temp))

    try:
        http_json(args.port, "GET", "/health")
        props = http_json(args.port, "GET", "/props")
    except Exception as e:  # noqa: BLE001
        sys.exit("cannot reach llama-server on %s:%d (%s). The designer starts the server; this script does not." % (HOST, args.port, e))
    gen = (props.get("default_generation_settings") or {})
    n_ctx = gen.get("n_ctx")
    if isinstance(n_ctx, int) and n_ctx < args.max_tokens + 1024:
        sys.exit("server context %d is too small for max_tokens %d plus the prompt" % (n_ctx, args.max_tokens))
    if props.get("total_slots") not in (None, 1):
        print("WARNING: server has %s slots, ADR-004 section 5b expects -np 1" % props.get("total_slots"))

    header = {
        "script": "quality_run.py v" + VERSION, "model_id": args.model_id, "config_id": args.config_id,
        "created": datetime.datetime.now().isoformat(timespec="seconds"),
        "prompts_file": str(Path(args.prompts).resolve()), "prompts_sha256": sha,
        "server_command": args.server_command, "server_port": args.port,
        "sampling": {"temperature": args.temperature, "top_p": args.top_p, "top_k": args.top_k, "min_p": args.min_p,
                     "seed_base": args.seed_base, "cache_prompt": False,
                     "server_defaults_if_omitted": gen.get("params") or gen},
        "max_tokens": args.max_tokens, "chat_template_kwargs": args.chat_template_kwargs, "extra_json": args.extra_json,
        "system_prompt": system_text,
        "system_prompt_sha256": hashlib.sha256(system_text.encode()).hexdigest() if system_text else None,
        "limits": {"gpu_temp_c": GPU_LIMIT_C, "min_mem_available_mib": RAM_LIMIT_MIB, "timeout_min": args.timeout_min,
                   "max_start_temp_c": args.max_start_temp},
        "server_props": {k: props.get(k) for k in ("build_info", "total_slots", "model_path", "model_alias", "modalities")},
        "n_ctx": n_ctx, "machine_state_at_start": state,
        "runner_command_line": sys.argv, "python": sys.version.split()[0],
    }
    header_path = out_dir / "run-header.json"
    if header_path.exists():
        old = json.loads(header_path.read_text())
        same = (old.get("prompts_sha256") == sha and old.get("max_tokens") == args.max_tokens
                and old.get("sampling", {}).get("temperature") == args.temperature
                and old.get("sampling", {}).get("top_p") == args.top_p
                and old.get("system_prompt_sha256") == header["system_prompt_sha256"]
                and old.get("extra_json") == args.extra_json
                and old.get("chat_template_kwargs") == args.chat_template_kwargs)
        if not same:
            sys.exit("%s already exists with different settings: use a new --config-id" % header_path)
        with open(out_dir / "run-headers-resumed.jsonl", "a") as f:
            f.write(json.dumps(header) + "\n")
    else:
        header_path.write_text(json.dumps(header, indent=1))

    log(out_dir, "run start: %s, %d prompts, max_tokens %d, n_ctx %s, prompts sha256 %s" % (
        out_dir.name, len(prompts), args.max_tokens, n_ctx, sha[:12]))
    for prompt in prompts:
        out_path = out_dir / (prompt["id"] + ".json")
        if out_path.exists():
            if not args.redo:
                log(out_dir, "%s: result exists, skipped" % prompt["id"])
                continue
            n = 2
            while (out_dir / ("%s.redo%d.json" % (prompt["id"], n))).exists():
                n += 1
            out_path = out_dir / ("%s.redo%d.json" % (prompt["id"], n))
        seed = args.seed_base + position[prompt["id"]]
        res = run_prompt(args, prompt, seed, system_text, out_dir, out_path)
        tk = res["tokens"]
        log(out_dir, "%s: %s finish=%s reasoning_tok=%s answer_tok=%s total_tok=%s time=%.1fs peak_temp=%s min_ram=%s%s" % (
            prompt["id"], res["status"], res["finish_reason"], tk["reasoning_tokenized"], tk["content_tokenized"],
            tk["completion_tokens_usage"], res["times_s"]["to_final_answer"], res["peaks"]["gpu_temp_c"],
            res["peaks"]["min_mem_available_mib"], " ERROR " + res["error"] if res["error"] else ""))
        if res["status"] in ("aborted_temp", "aborted_ram"):
            log(out_dir, "STOPPING THE RUN: %s. The attempt is kept as %s.failed-*.json and is retried on resume. Let the machine recover, then run the same command again." % (res["status"], prompt["id"]))
            sys.exit(3)
        if res["status"] in ("error", "incomplete"):
            log(out_dir, "STOPPING THE RUN: %s (the server connection was lost or the stream ended early). The attempt is kept as %s.failed-*.json and is retried on resume. Restart the server, then run the same command again." % (res["status"], prompt["id"]))
            sys.exit(4)
    log(out_dir, "run finished")


if __name__ == "__main__":
    main()
