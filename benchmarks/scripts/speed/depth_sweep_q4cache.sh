#!/usr/bin/env bash
# q4_0 KV-cache variant (ADR-004 v1.1) for the two small K2 Horizon models. Run with bash.
# Waits for the baseline sweep (PID given as $1) to finish first.
S="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LLTH_HOME="${LLTH_HOME:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
B=$LLTH_HOME/llama.cpp/build/bin/llama-bench
M7=$LLTH_HOME/models/IFM/K2-Horizon-7B-GGUF/K2-Horizon-7B-Q4_K_M.gguf
M3=$LLTH_HOME/models/IFM/K2-Horizon-3.7B-GGUF/K2-Horizon-4B-Q5_K_M.gguf
LOG7=$LLTH_HOME/benchmarks/speed/2026-10-23_k2-horizon-7b_depth-sweep_kv-q4_0.log
LOG3=$LLTH_HOME/benchmarks/speed/2026-10-23_k2-horizon-3.7b_depth-sweep_kv-q4_0.log

if [ -n "${1:-}" ]; then tail --pid="$1" -f /dev/null; sleep 60; fi   # let the GPU cool after the baseline

run() {  # label log model ngl depth
  bash "$S/bench_wrap.sh" "$1" "$2" -- "$B" -m "$3" -p 512 -n 128 -r 3 -ngl "$4" -fa on -ctk q4_0 -ctv q4_0 -d "$5" -o md
  sleep 20
}

for pair in "0:99" "8192:99" "8192:36" "8192:34" "8192:32" "16384:34" "16384:32" "16384:30" "16384:28" "32768:30" "32768:28" "32768:26" "32768:24"; do
  depth="${pair%%:*}"; ngl="${pair##*:}"
  run "K2-Horizon-7B Q4_K_M  KV=q4_0  ngl=${ngl}  depth=${depth}" "$LOG7" "$M7" "$ngl" "$depth"
done
for depth in 0 8192 16384 32768; do
  run "K2-Horizon-3.7B Q5_K_M  KV=q4_0  ngl=99  depth=${depth}" "$LOG3" "$M3" 99 "$depth"
done
echo "ALL DONE" | tee -a "$LOG7" >> "$LOG3"
