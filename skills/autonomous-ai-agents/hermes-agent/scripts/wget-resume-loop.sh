#!/bin/bash
# wget-resume-loop.sh — Download Hermes Agent tarball with wget + retry loop
#
# Usage:
#   1. Edit TAG below to match target version
#   2. Run in background: terminal(command="bash /path/to/wget-resume-loop.sh",
#                                   background=true, notify_on_complete=true, timeout=1800)
#   3. When notified: check /tmp/hermes-source.tar.gz
#
# WSL2+China network: wget achieves ~38KB/s vs curl's ~26KB/s.
# --continue resumes partial downloads so each retry picks up where it left off.

# ═══════════════════════════════════════════
# CONFIG — Edit these before running
# ═══════════════════════════════════════════
TAG="v2026.6.19"                       # Target release tag
OUTDIR="/tmp"                          # Output directory (use /tmp for Linux fs)
MAX_ATTEMPTS=30                        # Max retry attempts
MIN_BYTES=27000000                     # Minimum expected size (28MB ≈ 27000000)
# ═══════════════════════════════════════════

# Use API endpoint (more reliable on restricted networks)
# Alternative: https://github.com/NousResearch/hermes-agent/archive/refs/tags/${TAG}.tar.gz
TARBALL_URL="https://api.github.com/repos/NousResearch/hermes-agent/tarball/${TAG}"
OUTFILE="${OUTDIR}/hermes-source.tar.gz"

log() { echo "[$(date '+%H:%M:%S')] $*"; }

# Clean up any partial file from previous runs
rm -f "${OUTFILE}"

log "Starting download: ${TAG}"
log "Target: ${OUTFILE}"

for i in $(seq 1 "${MAX_ATTEMPTS}"); do
  log "=== Attempt ${i}/${MAX_ATTEMPTS} ==="
  wget \
    --continue \
    --timeout=120 \
    --read-timeout=120 \
    --retry-connrefused \
    --tries=1 \
    "${TARBALL_URL}" \
    -O "${OUTFILE}" 2>&1

  if [ -f "${OUTFILE}" ]; then
    size=$(stat -c%s "${OUTFILE}" 2>/dev/null)
    log "Size: ${size} bytes"

    if [ "${size}" -gt "${MIN_BYTES}" ]; then
      log "✅ DOWNLOAD COMPLETE! Size: $(ls -lh "${OUTFILE}" | awk '{print $5}')"
      log "File: ${OUTFILE}"
      exit 0
    fi
    log "Partial: need >${MIN_BYTES}, got ${size}"
  else
    log "No file yet"
  fi

  log "Retrying in 5s..."
  sleep 5
done

log "❌ FAILED after ${MAX_ATTEMPTS} attempts"
ls -lh "${OUTFILE}" 2>/dev/null || log "No file found"
exit 1