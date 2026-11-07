#!/usr/bin/env bash
# Power-profile A/B test (ADR-004 section 4a): how much is the performance profile worth in tokens/s?
# Usage:  bash profile-ab-test.sh <expected-profile> <phase-label>
#   expected-profile: performance | balanced | power-saver   (as shown by the system's power profile service)
#   phase-label:      free text for the log, e.g. 1, 2, 3, 4  (suggested order: performance, balanced, balanced, performance)
# The script REFUSES to run if the active profile is not the one you named, so a missed switch cannot spoil the data.
# Switch the profile yourself in the system settings between phases. No sudo needed. Each phase takes about 10 minutes.
S="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LLTH_HOME="${LLTH_HOME:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
B=$LLTH_HOME/llama.cpp/build/bin/llama-bench
M7=$LLTH_HOME/models/IFM/K2-Horizon-7B-GGUF/K2-Horizon-7B-Q4_K_M.gguf
M3=$LLTH_HOME/models/IFM/K2-Horizon-3.7B-GGUF/K2-Horizon-4B-Q5_K_M.gguf
LOG=$LLTH_HOME/benchmarks/speed/2026-10-23_profile-ab-test.log

want="${1:-}"; phase="${2:-?}"
[ -z "$want" ] && { echo "usage: bash $0 <performance|balanced|power-saver> <phase-label>"; exit 1; }
active="$(busctl get-property net.hadess.PowerProfiles /net/hadess/PowerProfiles net.hadess.PowerProfiles ActiveProfile 2>/dev/null | sed 's/^s "\(.*\)"$/\1/')"
if [ "$active" != "$want" ]; then
  echo "STOP: you asked for '$want' but the active power profile is '${active:-unknown}'."
  echo "Switch it in the system settings, then run this command again."
  exit 2
fi
if pgrep -f 'llama-bench -m' >/dev/null; then echo "STOP: another llama-bench is running."; exit 3; fi
echo "Active profile: $active. Starting phase $phase. Log: $LOG"

wait_cool() {  # wait until the GPU is at or below 55 C (at most 3 minutes)
  for _ in $(seq 1 36); do
    t=$(nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader)
    [ "$t" -le 55 ] && return 0
    sleep 5
  done
}

run() {  # label model extra-args...
  local label="$1" model="$2"; shift 2
  wait_cool
  bash "$S/bench_wrap.sh" "AB profile=${active} phase=${phase}  ${label}" "$LOG" -- \
    "$B" -m "$model" -p 512 -n 128 -r 3 -fa on -ctk q4_0 -ctv q4_0 "$@" -o md
}

run "A (GPU only)  3.7B d=8K  ngl=99"            "$M3" -d 8192  -ngl 99
run "B (mixed)     7B   d=16K ngl=36 ub=128"     "$M7" -d 16384 -ngl 36 -ub 128
run "C (CPU heavy) 7B   d=32K ngl=30 ub=128"     "$M7" -d 32768 -ngl 30 -ub 128
echo "Phase $phase done (profile $active)."
