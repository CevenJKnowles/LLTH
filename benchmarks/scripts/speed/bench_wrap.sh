#!/usr/bin/env bash
# usage: bench_wrap.sh <label> <logfile> -- <command...>
# Runs a command while sampling GPU memory/temperature/clock and available RAM once per second.
# Safety (ADR-004 section 4a): stops the command if the GPU reaches 92 C or available RAM drops below 1500 MiB.
# Prints the command output, then a one-line summary of peaks.
label="$1"; log="$2"; shift 3
TEMP_LIMIT=${TEMP_LIMIT:-92}; MEM_LIMIT_MIB=${MEM_LIMIT_MIB:-1500}
samples="$(mktemp)"; stopflag="$(mktemp)"; rm -f "$stopflag"
echo "### ${label}" | tee -a "$log"
echo "start: $(date -Is)  gpu_temp_before=$(nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader)  mem_available_MiB=$(awk '/MemAvailable/ {print int($2/1024)}' /proc/meminfo)  governor=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null) epp=$(cat /sys/devices/system/cpu/cpu0/cpufreq/energy_performance_preference 2>/dev/null) turbo_disabled=$(cat /sys/devices/system/cpu/intel_pstate/no_turbo 2>/dev/null) cpu_mhz_now=$(awk '{s+=$1} END {printf "%d", s/NR/1000}' /sys/devices/system/cpu/cpu[0-9]*/cpufreq/scaling_cur_freq 2>/dev/null)" | tee -a "$log"
echo "cmd: $*" | tee -a "$log"
"$@" > >(tee -a "$log") 2>&1 &
cmd_pid=$!
while kill -0 "$cmd_pid" 2>/dev/null; do
  g=$(nvidia-smi --query-gpu=memory.used,temperature.gpu,clocks.sm,power.draw --format=csv,noheader,nounits 2>/dev/null | tr -d ' ')
  a=$(awk '/MemAvailable/ {print int($2/1024)}' /proc/meminfo)
  echo "${g},${a}" >> "$samples"
  temp=$(echo "$g" | cut -d, -f2)
  if [ -n "$temp" ] && [ "$temp" -ge "$TEMP_LIMIT" ] 2>/dev/null; then echo "SAFETY STOP: GPU ${temp} C >= ${TEMP_LIMIT} C" | tee -a "$log"; kill "$cmd_pid"; touch "$stopflag"; break; fi
  if [ "$a" -lt "$MEM_LIMIT_MIB" ] 2>/dev/null; then echo "SAFETY STOP: available RAM ${a} MiB < ${MEM_LIMIT_MIB} MiB" | tee -a "$log"; kill "$cmd_pid"; touch "$stopflag"; break; fi
  sleep 1
done
wait "$cmd_pid" 2>/dev/null; rc=$?
python3 -I - "$samples" "$rc" <<'PY' | tee -a "$log"
import sys
rows=[l.strip().split(',') for l in open(sys.argv[1]) if l.count(',')==4]
if rows:
    vram=[float(r[0]) for r in rows]; temp=[float(r[1]) for r in rows]; clk=[float(r[2]) for r in rows]; pw=[float(r[3]) for r in rows]; av=[float(r[4]) for r in rows]
    print(f"peaks: vram_MiB={max(vram):.0f} gpu_temp_C={max(temp):.0f} sm_clock_min_MHz={min(clk):.0f} sm_clock_max_MHz={max(clk):.0f} power_max_W={max(pw):.0f} mem_available_min_MiB={min(av):.0f} samples={len(rows)} exit={sys.argv[2]}")
else:
    print(f"no samples exit={sys.argv[2]}")
PY
[ -e "$stopflag" ] && { echo "run was stopped by the safety limit" | tee -a "$log"; rm -f "$stopflag"; }
rm -f "$samples"
echo "end: $(date -Is)" | tee -a "$log"
echo | tee -a "$log"
exit $rc
