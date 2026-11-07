#!/usr/bin/env bash
# Exploration round 2 (ADR-004 section 4a): confirm and combine the winners of round 1 on K2 Horizon 7B.
# Run with bash, ideally with the CPU governor on "performance" and Chrome closed. 3 repetitions per run.
S="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LLTH_HOME="${LLTH_HOME:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
B=$LLTH_HOME/llama.cpp/build/bin/llama-bench
M7=$LLTH_HOME/models/IFM/K2-Horizon-7B-GGUF/K2-Horizon-7B-Q4_K_M.gguf
LOG=$LLTH_HOME/benchmarks/speed/2026-10-23_k2-horizon-7b_explore-round2.log

run() {  # label depth ngl extra-llama-bench-args...
  local label="$1" depth="$2" ngl="$3"; shift 3
  bash "$S/bench_wrap.sh" "$label  [governor=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor)]" "$LOG" -- \
    "$B" -m "$M7" -p 512 -n 128 -r 3 -fa on -ctk q4_0 -ctv q4_0 -d "$depth" -ngl "$ngl" "$@" -o md
  sleep 25
}

# depth 0
run "R2 d=0     baseline ub512  ngl=99"            0     99
run "R2 d=0     ub=128          ngl=99"            0     99  -ub 128
# depth 8K
run "R2 d=8K    baseline ub512  ngl=36"            8192  36
run "R2 d=8K    ub=128          ngl=99"            8192  99  -ub 128
run "R2 d=8K    ub=128          ngl=36"            8192  36  -ub 128
run "R2 d=8K    ub=64           ngl=99"            8192  99  -ub 64
# depth 16K
run "R2 d=16K   baseline ub512  ngl=32"            16384 32
run "R2 d=16K   ub=128          ngl=36"            16384 36  -ub 128
run "R2 d=16K   ub=128          ngl=99"            16384 99  -ub 128
run "R2 d=16K   ub=64           ngl=36"            16384 36  -ub 64
run "R2 d=16K   ub=64           ngl=99"            16384 99  -ub 64
run "R2 d=16K   ub=128 t=12     ngl=36"            16384 36  -ub 128 -t 12
# depth 32K
run "R2 d=32K   baseline ub512  ngl=28"            32768 28
run "R2 d=32K   ub=128          ngl=32"            32768 32  -ub 128
run "R2 d=32K   ub=128          ngl=30"            32768 30  -ub 128
run "R2 d=32K   ub=128          ngl=28"            32768 28  -ub 128
run "R2 d=32K   ub=64           ngl=30"            32768 30  -ub 64
run "R2 d=32K   ub=128 t=12     ngl=30"            32768 30  -ub 128 -t 12
echo "ALL DONE (exploration round 2)" >> "$LOG"
