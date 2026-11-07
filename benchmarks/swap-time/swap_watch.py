#!/usr/bin/env python3
"""Read-only swap-time watcher for llama-server on 127.0.0.1:8080.

Polls /proc for llama-server processes and GET /health every 50 ms and logs
transitions. Per load: process start (from /proc/<pid>/stat, 10 ms ticks)
to the first /health 200. Per stop: last /health 200 to process gone.
After each ready event it sends one 1-token /completion and times it.
Exits after --loads ready events or --max-min minutes.
"""
import argparse, json, os, time, urllib.request, urllib.error

URL = "http://127.0.0.1:8080"
TICK = os.sysconf("SC_CLK_TCK")

def boot():  # seconds since boot, same clock as /proc/<pid>/stat starttime
    return time.clock_gettime(time.CLOCK_BOOTTIME)

def servers():
    out = {}
    for p in os.listdir("/proc"):
        if not p.isdigit():
            continue
        try:
            with open(f"/proc/{p}/cmdline", "rb") as f:
                args = f.read().split(b"\0")
            if not args or not args[0].endswith(b"llama-server"):
                continue
            with open(f"/proc/{p}/stat") as f:
                start = int(f.read().rsplit(")", 1)[1].split()[19]) / TICK
            a = [x.decode() for x in args if x]
            model = os.path.basename(a[a.index("-m") + 1]) if "-m" in a else "?"
            out[int(p)] = (start, model)
        except (FileNotFoundError, ProcessLookupError, PermissionError, ValueError, IndexError):
            pass
    return out

def health():
    try:
        with urllib.request.urlopen(URL + "/health", timeout=0.5) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return None

def first_token():
    body = json.dumps({"prompt": "Hello", "n_predict": 1, "cache_prompt": False}).encode()
    req = urllib.request.Request(URL + "/completion", data=body, headers={"Content-Type": "application/json"})
    t = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            r.read()
        return round(time.monotonic() - t, 3)
    except Exception as e:
        return f"error: {e}"

def log(fh, **kv):
    kv["wall"] = time.strftime("%H:%M:%S")
    line = json.dumps(kv)
    print(line, flush=True)
    fh.write(line + "\n"); fh.flush()

ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
ap.add_argument("--loads", type=int, default=7)
ap.add_argument("--max-min", type=float, default=60)
a = ap.parse_args()

known, ready, last_ok, gone_at = {}, set(), None, None
loads, t_end = 0, time.monotonic() + a.max_min * 60
with open(a.out, "a") as fh:
    log(fh, event="watch_start", boot=round(boot(), 3))
    while time.monotonic() < t_end and loads < a.loads:
        now, procs, h = boot(), servers(), health()
        for pid, (start, model) in procs.items():
            if pid not in known:
                known[pid] = (start, model)
                gap = round(start - gone_at, 3) if gone_at else None
                log(fh, event="proc_start", pid=pid, model=model, seen_after_s=round(now - start, 3), human_gap_s=gap)
        if h == 200:
            last_ok = now
            for pid in procs:
                if pid not in ready:
                    ready.add(pid); loads += 1
                    start, model = known[pid]
                    log(fh, event="ready", pid=pid, model=model, load_s=round(now - start, 3), load_no=loads)
                    log(fh, event="first_token", pid=pid, model=model, seconds=first_token())
        for pid in list(known):
            if pid not in procs:
                start, model = known.pop(pid)
                gone_at = now
                stop = round(now - last_ok, 3) if last_ok else None
                log(fh, event="proc_gone", pid=pid, model=model, stop_s_upper=stop)
                ready.discard(pid)
        time.sleep(0.05)
    log(fh, event="watch_end", loads=loads)
