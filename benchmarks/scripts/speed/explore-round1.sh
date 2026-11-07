#!/usr/bin/env bash
# Exploration round 1 (ADR-004 section 4a): screening of tuning flags on the two small K2 Horizon models.
# Run with bash. Uses bench_wrap.sh (stops at 92 C GPU or 1500 MiB free RAM). Screening uses 2 repetitions.
S="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LLTH_HOME="${LLTH_HOME:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
B=$LLTH_HOME/llama.cpp/build/bin/llama-bench
M7=$LLTH_HOME/models/IFM/K2-Horizon-7B-GGUF/K2-Horizon-7B-Q4_K_M.gguf
M3=$LLTH_HOME/models/IFM/K2-Horizon-3.7B-GGUF/K2-Horizon-4B-Q5_K_M.gguf
LOG7=$LLTH_HOME/benchmarks/speed/2026-10-23_k2-horizon-7b_explore-round1.log
LOG3=$LLTH_HOME/benchmarks/speed/2026-10-23_k2-horizon-3.7b_explore-round1.log

run() {  # label log model extra-llama-bench-args...
  local label="$1" log="$2" model="$3"; shift 3
  bash "$S/bench_wrap.sh" "$label  [governor=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor)]" "$log" -- \
    "$B" -m "$model" -p 512 -n 128 -r 2 -fa on "$@" -o md
  sleep 25
}

# ---- 7B, depth 16384, q4_0 cache
KV=(-ctk q4_0 -ctv q4_0 -d 16384)
run "7B E0 baseline            ngl=32"                       "$LOG7" "$M7" -ngl 32 "${KV[@]}"
run "7B E1 ub=256              ngl=32"                       "$LOG7" "$M7" -ngl 32 "${KV[@]}" -ub 256
run "7B E1 ub=256              ngl=34"                       "$LOG7" "$M7" -ngl 34 "${KV[@]}" -ub 256
run "7B E1 ub=256              ngl=36"                       "$LOG7" "$M7" -ngl 36 "${KV[@]}" -ub 256
run "7B E2 ub=128              ngl=34"                       "$LOG7" "$M7" -ngl 34 "${KV[@]}" -ub 128
run "7B E2 ub=128              ngl=36"                       "$LOG7" "$M7" -ngl 36 "${KV[@]}" -ub 128
run "7B E3 no-kv-offload       ngl=99"                       "$LOG7" "$M7" -ngl 99 "${KV[@]}" -nkvo 1
run "7B E4 threads=8           ngl=32"                       "$LOG7" "$M7" -ngl 32 "${KV[@]}" -t 8
run "7B E4 threads=12          ngl=32"                       "$LOG7" "$M7" -ngl 32 "${KV[@]}" -t 12
run "7B E5 output.weight->CPU  ngl=99"                       "$LOG7" "$M7" -ngl 99 "${KV[@]}" -ot "output\.weight=CPU"
run "7B E6 output->CPU + ub=256 ngl=99"                      "$LOG7" "$M7" -ngl 99 "${KV[@]}" -ot "output\.weight=CPU" -ub 256
run "7B E6 output->CPU + ub=128 ngl=99"                      "$LOG7" "$M7" -ngl 99 "${KV[@]}" -ot "output\.weight=CPU" -ub 128

# ---- 3.7B, depth 32768
D32=(-d 32768)
run "3.7B E0 baseline q4_0     ngl=99"                       "$LOG3" "$M3" -ngl 99 -ctk q4_0 -ctv q4_0 "${D32[@]}"
run "3.7B E1 q4_0 ub=256       ngl=99"                       "$LOG3" "$M3" -ngl 99 -ctk q4_0 -ctv q4_0 "${D32[@]}" -ub 256
run "3.7B E3 q4_0 no-kv-offload ngl=99"                      "$LOG3" "$M3" -ngl 99 -ctk q4_0 -ctv q4_0 "${D32[@]}" -nkvo 1
run "3.7B E3 q8_0 no-kv-offload ngl=99"                      "$LOG3" "$M3" -ngl 99 -ctk q8_0 -ctv q8_0 "${D32[@]}" -nkvo 1
run "3.7B E5 q8_0 output->CPU  ngl=99"                       "$LOG3" "$M3" -ngl 99 -ctk q8_0 -ctv q8_0 "${D32[@]}" -ot "output\.weight=CPU"
run "3.7B E5 q4_0 output->CPU  ngl=99"                       "$LOG3" "$M3" -ngl 99 -ctk q4_0 -ctv q4_0 "${D32[@]}" -ot "output\.weight=CPU"
echo "ALL DONE (exploration round 1)" | tee -a "$LOG7" >> "$LOG3"
