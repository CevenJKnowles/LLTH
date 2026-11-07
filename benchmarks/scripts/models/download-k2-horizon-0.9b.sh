#!/usr/bin/env bash
# Downloads model 6 (K2 Horizon 0.9B, Q8_0) into $LLTH_HOME/models/ and verifies its SHA-256.
# Authority: ADR-004 v1.4 section 1a (accepted 2026-10-24). Source: the authors' own repo, pinned to one revision.
# Run with bash:   bash $LLTH_HOME/benchmarks/scripts/models/download-k2-horizon-0.9b.sh
# Safe to stop with Ctrl+C at any time; running it again resumes where it stopped.
# Needs: curl, sha256sum. Contacts only huggingface.co. No login, no sudo, no pip.
set -u
LLTH_HOME="${LLTH_HOME:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
M=$LLTH_HOME/models

# repo | revision | file | sha256 | size in bytes   (values from ADR-004 section 1a)
REPO="IFM/K2-Horizon-0.9B-GGUF"
REV="118965081cf1d876990219a1856a93a97b2668fa"
FILE="K2-Horizon-1B-Q8_0.gguf"
SHA="741fb9ad263956c003883cb7caddeb14b4dfb9b4b67b5414ad12967e965dd547"
SIZE="1148614016"

if pgrep -x llama-bench >/dev/null; then
  echo "WARNING: llama-bench is still running. The download would disturb the benchmark. Wait for it to finish, then run this again."
  exit 1
fi
if pgrep -f 'download-remaining-models' >/dev/null; then
  echo "WARNING: the main model download is still running. ADR-004 section 1a: model 6 comes after models 3 to 5 are verified."
  exit 1
fi
echo "Free disk in /home: $(df -h /home | awk 'NR==2 {print $4}')"
echo

dest="$M/${REPO%%/*}/${REPO#*/}"
out="$dest/$FILE"
mkdir -p "$dest"
echo "=== $FILE  ($(awk -v s="$SIZE" 'BEGIN{printf "%.2f", s/1e9}') GB), revision ${REV:0:12}"
if [ -f "$out" ] && [ "$(stat -c %s "$out")" = "$SIZE" ]; then
  echo "    file already has the right size; checking checksum"
else
  echo "    downloading (resumes if partial)"
  for attempt in 1 2 3; do
    curl -L -C - --fail --retry 3 --retry-delay 5 -o "$out" "https://huggingface.co/$REPO/resolve/$REV/$FILE" && break
    echo "    attempt $attempt failed; retrying in 10 s"; sleep 10
  done
fi
if [ ! -f "$out" ] || [ "$(stat -c %s "$out")" != "$SIZE" ]; then
  echo "    WRONG SIZE: expected $SIZE bytes, found $(stat -c %s "$out" 2>/dev/null || echo none). Run this script again to resume."
  exit 3
fi
echo "    verifying checksum (a few seconds)..."
got="$(sha256sum "$out" | cut -d' ' -f1)"
if [ "$got" = "$SHA" ]; then
  echo "    OK: checksum matches ADR-004 section 1a"
else
  echo "    CHECKSUM MISMATCH: expected $SHA"
  echo "                       got      $got"
  echo "    Delete the file and run this script again:  rm \"$out\""
  exit 2
fi
echo
echo "Model 6 downloaded and verified: $out"
