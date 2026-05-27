#!/usr/bin/env bash
# Run solver and export media for case umbrella-rain
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
export PYTHONPATH="${ROOT}/solve/_common:${ROOT}/solve/umbrella-rain"
cd "${ROOT}"
conda run -n math python -m umbrella_rain
conda run -n math python -c "
from paths import ami_dir
from umbrella_rain.constants import CASE_ID
from umbrella_rain.viz import export_all_media
out = export_all_media(ami_dir(CASE_ID))
print('Exported:', ', '.join(sorted(out.keys())))
"
