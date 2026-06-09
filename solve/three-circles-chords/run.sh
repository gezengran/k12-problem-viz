#!/usr/bin/env bash
# Export Live Photo for three-circles-chords (macOS only).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
export PYTHONPATH="${ROOT}/solve/_common:${ROOT}/solve/three-circles-chords"
cd "${ROOT}"
conda run -n math python -m three_circles_chords
