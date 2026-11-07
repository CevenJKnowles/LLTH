#!/usr/bin/env bash
# usage: fetch_model.sh <repo> <file> <sha256> <dest_dir>
# Downloads one file from huggingface.co with resume, then verifies its SHA-256.
set -u
repo="$1"; file="$2"; sha="$3"; dest="$4"
url="https://huggingface.co/${repo}/resolve/main/${file}"
out="${dest}/${file}"
echo "[$(date +%T)] downloading ${url}"
for attempt in 1 2 3; do
  command curl -L -C - --fail --retry 3 --retry-delay 5 -o "${out}" "${url}" && break
  echo "[$(date +%T)] attempt ${attempt} failed"; sleep 10
done
echo "[$(date +%T)] verifying checksum"
got="$(sha256sum "${out}" | cut -d' ' -f1)"
if [ "${got}" = "${sha}" ]; then
  echo "[$(date +%T)] OK ${file} $(stat -c %s "${out}") bytes"
else
  echo "[$(date +%T)] CHECKSUM MISMATCH for ${file}: got ${got} expected ${sha}"; exit 2
fi
