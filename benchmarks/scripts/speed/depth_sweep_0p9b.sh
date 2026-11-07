#!/usr/bin/env bash
# Depth sweep for model 6, K2 Horizon 0.9B Q8_0 (ADR-004 v1.4 section 1a, protocol of section 4). Run with bash (not zsh).
# Dense small model: all layers on the GPU. Both KV-cache variants (q8_0 baseline, then q4_0), depths 0, 8K, 16K, 32K.
# Usage:  bash depth_sweep_0p9b.sh
S="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LLTH_HOME="${LLTH_HOME:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
B=$LLTH_HOME/llama.cpp/build/bin/llama-bench
M=$LLTH_HOME/models/IFM/K2-Horizon-0.9B-GGUF/K2-Horizon-1B-Q8_0.gguf
LOG=$LLTH_HOME/benchmarks/speed/2026-10-24_k2-horizon-0.9b_depth-sweep.log

[ -f "$M" ] || { echo "STOP: model file not found: $M"; exit 1; }
if pgrep -x llama-bench >/dev/null; then echo "STOP: another llama-bench is running."; exit 3; fi
echo "Model 6 depth sweep. Log: $LOG"

run() {  # label cache-type depth
  bash "$S/bench_wrap.sh" "$1" "$LOG" -- "$B" -m "$M" -p 512 -n 128 -r 3 -ngl 99 -fa on -ctk "$2" -ctv "$2" -d "$3" -o md
  sleep 20
}

for cache in q8_0 q4_0; do
  for depth in 0 8192 16384 32768; do
    run "K2-Horizon-0.9B Q8_0  KV=${cache}  ngl=99  depth=${depth}" "$cache" "$depth"
  done
done
echo "ALL DONE (model 6 depth sweep)" | tee -a "$LOG"
