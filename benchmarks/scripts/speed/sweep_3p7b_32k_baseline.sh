#!/usr/bin/env bash
# Baseline (q8_0 cache) 3.7B at 32K depth with fewer GPU layers, appended to the existing baseline log. Run with bash.
# Waits for the PID given as $1 (the q4_0 variant sweep) to finish first.
S="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LLTH_HOME="${LLTH_HOME:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
B=$LLTH_HOME/llama.cpp/build/bin/llama-bench
M3=$LLTH_HOME/models/IFM/K2-Horizon-3.7B-GGUF/K2-Horizon-4B-Q5_K_M.gguf
LOG3=$LLTH_HOME/benchmarks/speed/2026-10-23_k2-horizon-3.7b_depth-sweep.log

if [ -n "${1:-}" ]; then tail --pid="$1" -f /dev/null; sleep 60; fi

for ngl in 32 30 28; do
  bash "$S/bench_wrap.sh" "K2-Horizon-3.7B Q5_K_M  ngl=${ngl}  depth=32768  (added: fewer layers, baseline q8_0 cache)" "$LOG3" -- \
    "$B" -m "$M3" -p 512 -n 128 -r 3 -ngl "$ngl" -fa on -ctk q8_0 -ctv q8_0 -d 32768 -o md
  sleep 20
done
echo "ALL DONE (3.7B 32K baseline retry)" >> "$LOG3"
