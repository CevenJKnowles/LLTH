#!/usr/bin/env bash
# Combined power-profile A/B test over models 3 to 6 (PD-016; ADR-004 section 4a, flag-level exploration). Run with bash (not zsh).
# Question: does the balanced profile change speed for the CPU-heavy large models and the small model 6,
#   when the dense models showed no meaningful difference (DOC-IMPL-014 section 1)?
# Usage:  bash profile-ab-test-models3to6.sh <expected-profile> <phase-label>
#   expected-profile: performance | balanced | power-saver   (as shown by the system's power profile service)
#   phase-label:      1, 2, 3, 4   (order ABBA: performance 1, balanced 2, balanced 3, performance 4)
# The script REFUSES to run if the active profile is not the one you named. Switch the profile yourself in the
#   system settings between phases (no sudo). Close all browsers; keep the laptop on mains power and awake.
# Each phase runs 8 tests (about 25 to 35 minutes [E, not measured]); settings are those chosen in
#   DOC-IMPL-012 section 4 and DOC-IMPL-013, all with -p 512 -n 128 -r 3 -fa on -ngl 99, default threads and memory mapping:
#   model 6  K2 Horizon 0.9B Q8_0            q8_0 cache, all on the GPU            depths 8K and 32K
#   model 5  Gemma 4 26B-A4B                 q8_0 cache, -ncmoe 24                 depths 8K and 32K
#   model 4  Qwen3.6-35B-A3B                 q8_0 cache, -ncmoe 34                 depths 8K and 32K
#   model 3  K2 Horizon MoVA 36B-A4B         q4_0 cache, -ncmoe 46, -ot attn_v_exps=CPU   depths 8K and 32K
#   (model 3 uses q4_0 because q8_0 cannot reach 32K; it is the hottest test and runs last in each phase.)
# Safety (bench_wrap.sh): a run stops at 92 C GPU or 1,500 MiB available RAM, and the whole phase is then aborted.
# Log: $LLTH_HOME/benchmarks/speed/${DATE}_profile-ab-test_models3to6.log   (runs are appended)
set -u
S="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LLTH_HOME="${LLTH_HOME:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
DATE="${DATE:-2026-10-24}"
B="$LLTH_HOME/llama.cpp/build/bin/llama-bench"
MD="$LLTH_HOME/models"
M6="$MD/IFM/K2-Horizon-0.9B-GGUF/K2-Horizon-1B-Q8_0.gguf"
M5="$MD/google/gemma-4-26B-A4B-it-qat-q4_0-gguf/gemma-4-26B_q4_0-it.gguf"
M4="$MD/unsloth/Qwen3.6-35B-A3B-GGUF/Qwen3.6-35B-A3B-UD-IQ4_XS.gguf"
M3="$MD/IFM/K2-Horizon-MoVA-36B-A4B-GGUF/K2-Horizon-MoVA-36B-A4B-Q4_K_M.gguf"
LOG="$LLTH_HOME/benchmarks/speed/${DATE}_profile-ab-test_models3to6.log"

want="${1:-}"; phase="${2:-?}"
[ -z "$want" ] && { echo "usage: bash $0 <performance|balanced|power-saver> <phase-label>"; exit 1; }
active="$(busctl get-property net.hadess.PowerProfiles /net/hadess/PowerProfiles net.hadess.PowerProfiles ActiveProfile 2>/dev/null | sed 's/^s "\(.*\)"$/\1/')"
if [ "$active" != "$want" ]; then
  echo "STOP: you asked for '$want' but the active power profile is '${active:-unknown}'."
  echo "Switch it in the system settings, then run this command again."
  exit 2
fi
if pgrep -x llama-bench >/dev/null; then echo "STOP: another llama-bench is running."; exit 3; fi
if ps -eo comm | grep -q -i -E '^(chrome|chromium|firefox|brave)'; then echo "STOP: a browser is running. Close it first."; exit 4; fi
for f in "$M6" "$M5" "$M4" "$M3"; do [ -f "$f" ] || { echo "STOP: model file not found: $f"; exit 1; }; done
avail=$(awk '/MemAvailable/ {print int($2/1024)}' /proc/meminfo)
[ "$avail" -ge 18000 ] || { echo "STOP: only ${avail} MiB RAM available (need 18000)."; exit 4; }
echo "Active profile: $active. Starting phase $phase. Log: $LOG"

wait_cool() {  # wait until the GPU is at or below 55 C (at most 3 minutes)
  for _ in $(seq 1 36); do
    t=$(nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader)
    [ "$t" -le 55 ] && return 0
    sleep 5
  done
}

run() {  # label model cache depth [extra llama-bench args...]
  local label="$1" model="$2" cache="$3" depth="$4"; shift 4
  local before=0; [ -f "$LOG" ] && before=$(wc -l < "$LOG")
  wait_cool
  bash "$S/bench_wrap.sh" "AB profile=${active} phase=${phase}  ${label}" "$LOG" -- \
    "$B" -m "$model" -p 512 -n 128 -r 3 -fa on -ctk "$cache" -ctv "$cache" -ngl 99 -d "$depth" "$@" -o md
  if tail -n +$((before+1)) "$LOG" | grep -q 'SAFETY STOP'; then
    echo "ABORT: a safety limit stopped a run in phase $phase (see the log). Nothing further is started." | tee -a "$LOG"; exit 5
  fi
  sleep 20
}

run "6 (0.9B Q8_0, all on GPU)   KV=q8_0  d=8K"                    "$M6" q8_0 8192
run "6 (0.9B Q8_0, all on GPU)   KV=q8_0  d=32K"                   "$M6" q8_0 32768
run "5 (Gemma 4)  ncmoe=24       KV=q8_0  d=8K"                    "$M5" q8_0 8192  -ncmoe 24
run "5 (Gemma 4)  ncmoe=24       KV=q8_0  d=32K"                   "$M5" q8_0 32768 -ncmoe 24
run "4 (Qwen3.6)  ncmoe=34       KV=q8_0  d=8K"                    "$M4" q8_0 8192  -ncmoe 34
run "4 (Qwen3.6)  ncmoe=34       KV=q8_0  d=32K"                   "$M4" q8_0 32768 -ncmoe 34
run "3 (K2 MoVA)  ncmoe=46 ot=attn_v_exps=CPU  KV=q4_0  d=8K"      "$M3" q4_0 8192  -ncmoe 46 -ot attn_v_exps=CPU
run "3 (K2 MoVA)  ncmoe=46 ot=attn_v_exps=CPU  KV=q4_0  d=32K"     "$M3" q4_0 32768 -ncmoe 46 -ot attn_v_exps=CPU
echo "Phase $phase done (profile $active)." | tee -a "$LOG"
