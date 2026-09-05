#!/usr/bin/env bash
# Build the 14.9 s Etsy listing video for the Budget Planner workbook.
#   usage: build_budget_video.sh <raw-recording> <work-dir> <output.mp4>
#
# The product's claim is that everything is on one page, so the film opens on
# the whole page and then travels down it in ONE uncut move — the page is
# reassembled by make_page.py and scrolled programmatically, because the take
# itself scrolls in jumps. Only after that does it cut, and only to the two
# things a still page cannot show: the month switch, and the second sheet.
set -euo pipefail

RAW="${1:?raw recording}"; W="${2:?work dir}"; OUT="${3:?output}"
FF="$(python3 -c 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())')"
HERE="$(cd "$(dirname "$0")" && pwd)"
export WORK="$W"
mkdir -p "$W/src" "$W/scenes" "$W/layers"

# 0. normalise the Chrome .webm (VP8, variable frame rate, no duration header)
if [ ! -f "$W/src/rec.mp4" ]; then
  "$FF" -y -hide_banner -loglevel error -fflags +genpts -i "$RAW" \
    -r 30 -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p "$W/src/rec.mp4"
fi

[ -f "$W/fonts/PlayfairDisplay-700.ttf" ] || "$HERE/fetch_fonts.sh" "$W/fonts"
python3 "$HERE/make_layers_budget.py" "$W/layers" "$W/fonts"

# 1. shot 1 — the whole page, held and then scrolled, in one take
python3 "$HERE/make_page.py" "$W/src/rec.mp4" "$W/scenes/s01.mp4"

# 2. the four cuts that follow. The Russian "convert to table" toast Sheets
#    floats over the Log from 36.5 s sits at x980-1260 / y760-800: the wide Log
#    shot ends at 36.45 s, just before it appears, and the close one stops at
#    x950. The month pair and the wide Log are framed at the page's full width,
#    the same scale as the scroll, so the cut never changes the zoom — the point
#    being that this is all still one page.
SHOTS=(
  "29.45 1.40  1440:810:0:0    month-list-open"
  "31.45 1.70  1440:810:0:0    month-applied"
  "34.90 1.55  1440:810:0:0    log"
  "39.60 1.64  900:506:0:300   log-category-list"
)
i=1
for s in "${SHOTS[@]}"; do
  set -- $s; i=$((i+1))
  printf -v id "s%02d" $i
  "$FF" -y -hide_banner -loglevel error -ss "$1" -t "$2" -i "$W/src/rec.mp4" \
    -vf "crop=$3,scale=960:540:flags=lanczos,setsar=1,format=yuv420p" -an -r 30 \
    -c:v libx264 -preset medium -crf 16 "$W/scenes/$id.mp4"
done
N=5
X=0.28
TOTAL=14.9

# 3. cross-fade the five into one screen
read -r -a DURS <<< "$(python3 -c "
import subprocess,json
ff='$FF'
d=[]
for i in range(1,$N+1):
    p=subprocess.run([ff,'-hide_banner','-i','$W/scenes/s%02d.mp4'%i],capture_output=True,text=True).stderr
    t=[l for l in p.splitlines() if 'Duration' in l][0].split('Duration:')[1].split(',')[0].strip()
    h,m,sec=t.split(':'); d.append(round(int(h)*3600+int(m)*60+float(sec),3))
print(' '.join(str(x) for x in d))")"
DLIST=$(IFS=,; echo "${DURS[*]}")
FC=""; PREV="0"
for i in $(seq 2 $N); do
  OFF=$(python3 -c "d=[$DLIST]; print(round(sum(d[:$i-1]) - ($i-1)*$X, 3))")
  FC+="[$PREV][$((i-1))]xfade=transition=fade:duration=$X:offset=$OFF[x$i]; "
  PREV="x$i"
done
"$FF" -y -hide_banner -loglevel error \
  $(for i in $(seq 1 $N); do printf ' -i %s' "$(printf "$W/scenes/s%02d.mp4" $i)"; done) \
  -filter_complex "${FC}[$PREV]format=yuv420p[v]" -map "[v]" -r 30 -t $TOTAL \
  -c:v libx264 -preset medium -crf 16 "$W/screen.mp4"

# 4. compose. Captions are timed against the film rather than against shots, so
#    the line can change while the page keeps moving under it.
CAPS=("0.15 3.10" "3.45 6.30" "6.65 9.20" "9.60 10.70" "10.95 12.25" "12.45 14.62")
PILLS=("0.00 12.10" "12.10 14.90")

INPUTS=(-loop 1 -framerate 30 -t $TOTAL -i "$W/layers/bg.png"
        -i "$W/screen.mp4"
        -loop 1 -framerate 30 -t $TOTAL -i "$W/layers/fg.png"
        -loop 1 -framerate 30 -t $TOTAL -i "$W/layers/bar.png")
for i in $(seq 1 ${#CAPS[@]});  do INPUTS+=(-loop 1 -framerate 30 -t $TOTAL -i "$W/layers/cap$i.png"); done
for i in $(seq 1 ${#PILLS[@]}); do INPUTS+=(-loop 1 -framerate 30 -t $TOTAL -i "$W/layers/pill$i.png"); done

FC2="[0:v]format=rgba[bg];[1:v]format=rgba[scr];[bg][scr]overlay=60:300:format=auto[a];"
FC2+="[2:v]format=rgba[fg];[a][fg]overlay=0:0:format=auto[b];"
FC2+="[3:v]format=rgba[pb];[b][pb]overlay=x='-1080+1080*t/${TOTAL}':y=1075:format=auto[c0];"
PREV="c0"
for i in $(seq 1 ${#CAPS[@]}); do
  set -- ${CAPS[$((i-1))]}
  IDX=$((3+i))
  FC2+="[$IDX:v]format=rgba,fade=in:st=$1:d=0.22:alpha=1,fade=out:st=$2:d=0.22:alpha=1[k$i];"
  FC2+="[$PREV][k$i]overlay=0:0:format=auto[c$i];"; PREV="c$i"
done
for i in $(seq 1 ${#PILLS[@]}); do
  set -- ${PILLS[$((i-1))]}
  IDX=$((3+${#CAPS[@]}+i))
  FC2+="[$IDX:v]format=rgba,fade=in:st=$1:d=0.16:alpha=1,fade=out:st=$2:d=0.16:alpha=1[p$i];"
  FC2+="[$PREV][p$i]overlay=0:0:format=auto[q$i];"; PREV="q$i"
done
FC2+="[$PREV]fade=t=in:st=0:d=0.35:color=0xFCFDFB,fade=t=out:st=14.6:d=0.3:color=0xFCFDFB,format=yuv420p[out]"

"$FF" -y -hide_banner -loglevel error "${INPUTS[@]}" -filter_complex "$FC2" \
  -map "[out]" -t $TOTAL -r 30 -an \
  -c:v libx264 -preset medium -crf 19 -profile:v high -level 4.0 -movflags +faststart "$OUT"

"$FF" -y -hide_banner -loglevel error -ss 1.2 -i "$OUT" -frames:v 1 -q:v 2 \
  "$(dirname "$OUT")/$(basename "${OUT%.mp4}" | sed 's/promo/cover/').jpg" 2>/dev/null || true
echo "built $OUT"
"$FF" -hide_banner -i "$OUT" 2>&1 | grep -E "Duration|Stream"
