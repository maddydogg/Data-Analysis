#!/usr/bin/env bash
# Rebuilds the Paycheck Budget listing video from the clean template.
#   ./build_paycheck.sh "Paycheck Budget  Light.xlsx"
# Needs: libreoffice-calc, python3 (openpyxl pymupdf pillow numpy imageio-ffmpeg).
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
SRC=${1:?pass the clean template .xlsx}
export WORK=${WORK:-$here/work}
mkdir -p "$WORK"

python3 "$here/fetch_fonts.py"
python3 "$here/make_demo_paycheck.py" "$SRC" "$here/PaycheckBudget_Light_DEMO.xlsx"
python3 "$here/render_sheets.py" "$here/PaycheckBudget_Light_DEMO.xlsx"
python3 "$here/make_video.py"

FFMPEG=$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())" 2>/dev/null || echo ffmpeg)
"$FFMPEG" -y -loglevel error -framerate 30 -i "$WORK/frames/f_%04d.png" \
  -vf "crop=1500:1124:0:0" -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p \
  -movflags +faststart "$here/paycheck_budget_promo_1500.mp4"
"$FFMPEG" -y -loglevel error -i "$here/paycheck_budget_promo_1500.mp4" \
  -ss 13.6 -frames:v 1 -q:v 2 "$here/paycheck_budget_cover.jpg"
echo "built $here/paycheck_budget_promo_1500.mp4"
