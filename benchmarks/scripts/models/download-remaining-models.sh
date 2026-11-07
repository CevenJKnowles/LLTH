#!/usr/bin/env bash
# Downloads the three remaining ADR-004 models into $LLTH_HOME/models/ and verifies each file's SHA-256.
# Run with bash:   bash $LLTH_HOME/benchmarks/scripts/models/download-remaining-models.sh
# Safe to stop with Ctrl+C at any time; running it again resumes where it stopped.
# Needs: curl, sha256sum. Contacts only huggingface.co. No login, no sudo, no pip.
set -u
LLTH_HOME="${LLTH_HOME:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
M=$LLTH_HOME/models

# repo | file | sha256 | size in bytes   (values from ADR-004 section 1)
FILES=(
"google/gemma-4-26B-A4B-it-qat-q4_0-gguf|gemma-4-26B_q4_0-it.gguf|3eca3b8f6d7baf218a7dd6bba5fb59a56ee25fe2d567b6f5f589b4f697eca51d|14439363584"
"unsloth/Qwen3.6-35B-A3B-GGUF|Qwen3.6-35B-A3B-UD-IQ4_XS.gguf|649d7508507b84638732c4f52c24c8b15843c6dca2f3ff793ae07c14a67ebbb3|17730509792"
"IFM/K2-Horizon-MoVA-36B-A4B-GGUF|K2-Horizon-MoVA-36B-A4B-Q4_K_M.gguf|513dd78590ac29135a7cea5a99865d57d65291b1f857a8904fb9b1878d4f4cbd|22368011616"
)

if pgrep -x llama-bench >/dev/null; then
  echo "WARNING: llama-bench is still running. Downloads would disturb the benchmark. Wait for it to finish, then run this again."
  exit 1
fi
echo "Free disk in /home: $(df -h /home | awk 'NR==2 {print $4}')"
echo

for entry in "${FILES[@]}"; do
  IFS='|' read -r repo file sha size <<< "$entry"
  dest="$M/${repo%%/*}/${repo#*/}"
  out="$dest/$file"
  mkdir -p "$dest"
  echo "=== $file  ($(awk -v s="$size" 'BEGIN{printf "%.2f", s/1e9}') GB)"
  if [ -f "$out" ] && [ "$(stat -c %s "$out")" = "$size" ]; then
    echo "    file already has the right size; checking checksum"
  else
    echo "    downloading (resumes if partial)"
    for attempt in 1 2 3; do
      curl -L -C - --fail --retry 3 --retry-delay 5 -o "$out" "https://huggingface.co/$repo/resolve/main/$file" && break
      echo "    attempt $attempt failed; retrying in 10 s"; sleep 10
    done
  fi
  echo "    verifying checksum (about a minute)..."
  got="$(sha256sum "$out" | cut -d' ' -f1)"
  if [ "$got" = "$sha" ]; then
    echo "    OK: checksum matches ADR-004"
  else
    echo "    CHECKSUM MISMATCH: expected $sha"
    echo "                       got      $got"
    echo "    Delete the file and run this script again:  rm \"$out\""
    exit 2
  fi
  echo
done
echo "All three models downloaded and verified."
