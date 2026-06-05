#!/usr/bin/env bash
# Export plank-block-friction MP4s; on macOS optionally build Live Photo (.pvt).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
export PYTHONPATH="${ROOT}/solve/_common:${ROOT}/solve/plank-block-friction"
cd "${ROOT}"

conda run -n math python -m plank_block_friction

if [[ "$(uname -s)" == "Darwin" ]]; then
  echo "macOS: optional Live Photo export not wired in v1 run.sh (use MP4 in ami/plank-block-friction/)."
fi
