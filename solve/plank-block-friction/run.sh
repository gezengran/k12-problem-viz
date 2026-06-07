#!/usr/bin/env bash
# Export plank-block-friction MP4s; on macOS also build Live Photos (.pvt).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
export PYTHONPATH="${ROOT}/solve/_common:${ROOT}/solve/plank-block-friction"
cd "${ROOT}"

conda run -n math python -m plank_block_friction
