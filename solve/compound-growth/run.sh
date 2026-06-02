#!/usr/bin/env bash
# Export compound-growth Live Photo (.pvt) for Xiaohongshu
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
export PYTHONPATH="${ROOT}/solve/_common:${ROOT}/solve/compound-growth"
cd "${ROOT}"
conda run -n math python -m compound_growth
