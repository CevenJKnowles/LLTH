#!/usr/bin/env bash
# Benchmarks for the three large MoE models of ADR-004 (models 5, 4 and 3). Run with bash (not zsh).
# Version v1.1 (2026-10-24). v1.0 produced the Gemma and Qwen results. v1.1 adds the optional OT variable (below);
#   with OT unset the commands are identical to v1.0. The time estimate was corrected from measured runs.
#
# Usage:
#   bash bench_large_models.sh <model> sweep
#   bash bench_large_models.sh <model> depths <ncmoe-for-q8_0> [<ncmoe-for-q4_0>]
#   <model> is: gemma | qwen | k2mova      (sweep also accepts: all = gemma, qwen, k2mova in that order)
#
# Stage 1, sweep: finds how many layers' experts must stay on the CPU (-ncmoe). ADR-004 section 4: start from the safe
#   side (experts of ALL layers on the CPU) and move layers to the GPU in steps of 2 until a run no longer loads or
#   completes. Each point is measured at depth 0 and at depth 8192 (the speed-gate depth), once per KV-cache type.
# Stage 2, depths: with the chosen -ncmoe, the full depth matrix 0, 8K, 16K, 32K for both cache types. The chosen
#   values come from reading the sweep log together (the best stable point with some VRAM to spare, not the last
#   point that happened to load).
#
# Fixed by ADR-004: -p 512 -n 128 -r 3 -fa on -ngl 99; cache types q8_0/q8_0 (baseline) and q4_0/q4_0 (variant) are
#   reported side by side; default memory mapping (no --no-mmap, no --mlock: the machine has no swap); safety stop at
#   92 C GPU or 1,500 MiB available RAM (bench_wrap.sh). Default threads (llama-bench uses 6); set THREADS=12 for the
#   CPU-bound regime as an exploration pass under section 4a, and say so in the log name (see LOGTAG).
# Environment (all optional): LLTH_HOME, DATE (log file prefix), CACHES (default "q8_0 q4_0"), THREADS, LOGTAG,
#   ALLOW_BROWSER=1 (run although a browser is open; not recommended),
#   OT = an --override-tensor pattern passed as -ot "$OT" and shown in every label, e.g. OT='attn_v_exps=CPU' for K2 MoVA,
#   whose value experts (4,050 MiB) are not moved by -ncmoe (DOC-IMPL-013 section 4.1). Use LOGTAG to name those logs.
#
# Time, measured on Gemma and Qwen (2026-10-24): a sweep took about 25 minutes per model, a depth matrix (8 runs) about
#   18 minutes. Models that need more steps or have slower CPU parts may take longer.
# Log files (never overwritten, runs are appended): $LLTH_HOME/benchmarks/speed/${DATE}_<model-id>_ncmoe-sweep[_LOGTAG].log
#                                                  and ..._depth-matrix[_LOGTAG].log
set -u
S="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LLTH_HOME="${LLTH_HOME:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
B="$LLTH_HOME/llama.cpp/build/bin/llama-bench"
MD="$LLTH_HOME/models"
LOGDIR="$LLTH_HOME/benchmarks/speed"
DATE="${DATE:-2026-10-24}"
CACHES="${CACHES:-q8_0 q4_0}"
THREADS="${THREADS:-}"
LOGTAG="${LOGTAG:-}"
OT="${OT:-}"
OTLABEL="${OT:+  override-tensor=$OT}"
MIN_AVAIL_MIB=18000

usage() { sed -n '2,14p' "${BASH_SOURCE[0]}"; exit 1; }

model_info() {  # sets FILE LAYERS ID LABEL
  case "$1" in
    gemma)  FILE="$MD/google/gemma-4-26B-A4B-it-qat-q4_0-gguf/gemma-4-26B_q4_0-it.gguf";              LAYERS=30; ID="gemma-4-26b-a4b";     LABEL="Gemma-4-26B-A4B Q4_0" ;;
    qwen)   FILE="$MD/unsloth/Qwen3.6-35B-A3B-GGUF/Qwen3.6-35B-A3B-UD-IQ4_XS.gguf";                   LAYERS=40; ID="qwen3.6-35b-a3b";     LABEL="Qwen3.6-35B-A3B IQ4_XS" ;;
    k2mova) FILE="$MD/IFM/K2-Horizon-MoVA-36B-A4B-GGUF/K2-Horizon-MoVA-36B-A4B-Q4_K_M.gguf";          LAYERS=48; ID="k2-horizon-mova-36b"; LABEL="K2-Horizon-MoVA-36B-A4B Q4_K_M" ;;
    *) return 1 ;;
  esac
}

preflight() {
  [ -f "$B" ] || { echo "STOP: llama-bench not found: $B"; exit 1; }
  [ -f "$FILE" ] || { echo "STOP: model file not found: $FILE"; exit 1; }
  if pgrep -x llama-bench >/dev/null; then echo "STOP: another llama-bench is running."; exit 3; fi
  if [ "${ALLOW_BROWSER:-0}" != "1" ] && ps -eo comm | grep -q -i -E '^(chrome|chromium|firefox|brave)'; then
    echo "STOP: a browser is running. Close it (it takes RAM the large models need), or set ALLOW_BROWSER=1."; exit 4
  fi
  local avail; avail=$(awk '/MemAvailable/ {print int($2/1024)}' /proc/meminfo)
  if [ "$avail" -lt "$MIN_AVAIL_MIB" ]; then echo "STOP: only ${avail} MiB RAM available (need ${MIN_AVAIL_MIB}). Close programs first."; exit 4; fi
  local prof; prof="$(busctl get-property net.hadess.PowerProfiles /net/hadess/PowerProfiles net.hadess.PowerProfiles ActiveProfile 2>/dev/null | sed 's/^s "\(.*\)"$/\1/')"
  echo "Pre-flight OK: ${avail} MiB RAM available, power profile '${prof:-unknown}', model ${LABEL}."
}

wait_cool() {  # wait until the GPU is at or below 55 C (at most 3 minutes)
  for _ in $(seq 1 36); do
    t=$(nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader)
    [ "$t" -le 55 ] && return 0
    sleep 5
  done
}

run_one() {  # log label cache ncmoe depth   -> 0 if the run produced a generation result
  local log="$1" label="$2" cache="$3" ncmoe="$4" depth="$5"
  local before=0; [ -f "$log" ] && before=$(wc -l < "$log")
  local extra=(); [ -n "$THREADS" ] && extra=(-t "$THREADS")
  local otargs=(); [ -n "$OT" ] && otargs=(-ot "$OT")
  wait_cool
  bash "$S/bench_wrap.sh" "$label" "$log" -- "$B" -m "$FILE" -p 512 -n 128 -r 3 -fa on \
    -ctk "$cache" -ctv "$cache" -ngl 99 -ncmoe "$ncmoe" -d "$depth" ${extra[@]+"${extra[@]}"} ${otargs[@]+"${otargs[@]}"} -o md
  local rc=$?
  local new; new="$(tail -n +$((before+1)) "$log")"
  if echo "$new" | grep -q 'SAFETY STOP'; then
    echo "ABORT: the safety limit stopped a run (see the log). Nothing further is started. Check the machine, then decide." | tee -a "$log"
    exit 5
  fi
  sleep 20
  [ "$rc" -eq 0 ] && echo "$new" | grep -q 'tg128'
}

logname() { echo "$LOGDIR/${DATE}_${ID}_$1${LOGTAG:+_$LOGTAG}.log"; }

do_sweep() {
  model_info "$1" || usage
  preflight
  local log; log="$(logname ncmoe-sweep)"
  echo "ncmoe sweep for ${LABEL} (${LAYERS} layers). Log: $log"
  local cache off n
  for cache in $CACHES; do
    for off in 0 2 4 6 8 10 12 14; do
      n=$((LAYERS-off))
      if ! run_one "$log" "${LABEL}  KV=${cache}  ncmoe=${n} (experts of ${n} of ${LAYERS} layers on the CPU)${OTLABEL}  depth=0" "$cache" "$n" 0; then
        echo "ncmoe=${n}, KV=${cache}: did not load or complete at depth 0; the ${cache} sweep stops here." | tee -a "$log"; break
      fi
      if ! run_one "$log" "${LABEL}  KV=${cache}  ncmoe=${n} (experts of ${n} of ${LAYERS} layers on the CPU)${OTLABEL}  depth=8192" "$cache" "$n" 8192; then
        echo "ncmoe=${n}, KV=${cache}: did not complete at depth 8192; the ${cache} sweep stops here." | tee -a "$log"; break
      fi
    done
  done
  echo "DONE (ncmoe sweep ${ID})" | tee -a "$log"
}

do_depths() {
  model_info "$1" || usage
  local nc8="${2:-}" nc4="${3:-${2:-}}"
  case "$nc8$nc4" in ''|*[!0-9]*) echo "STOP: give the -ncmoe value(s) as whole numbers."; usage ;; esac
  [ "$nc8" -le "$LAYERS" ] && [ "$nc4" -le "$LAYERS" ] || { echo "STOP: -ncmoe cannot exceed ${LAYERS} for this model."; exit 1; }
  preflight
  local log; log="$(logname depth-matrix)"
  echo "Depth matrix for ${LABEL}: ncmoe=${nc8} (q8_0), ncmoe=${nc4} (q4_0). Log: $log"
  local cache nc depth
  for cache in $CACHES; do
    nc="$nc8"; [ "$cache" = "q4_0" ] && nc="$nc4"
    for depth in 0 8192 16384 32768; do
      run_one "$log" "${LABEL}  KV=${cache}  ncmoe=${nc}${OTLABEL}  depth=${depth}" "$cache" "$nc" "$depth" \
        || echo "ncmoe=${nc}, KV=${cache}, depth=${depth}: did not load or complete (recorded, continuing)." | tee -a "$log"
    done
  done
  echo "DONE (depth matrix ${ID})" | tee -a "$log"
}

model="${1:-}"; stage="${2:-}"
case "$stage" in
  sweep)
    if [ "$model" = "all" ]; then
      for m in gemma qwen k2mova; do do_sweep "$m"; sleep 120; done
    else
      do_sweep "$model"
    fi ;;
  depths) shift 2; do_depths "$model" "$@" ;;
  *) usage ;;
esac
