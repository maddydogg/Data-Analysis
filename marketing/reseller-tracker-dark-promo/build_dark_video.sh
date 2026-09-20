#!/usr/bin/env bash
# Build the 14.9 s Etsy listing video for the dark edition of the Reseller Tracker.
#   usage: build_dark_video.sh <raw-recording> <work-dir> <output.mp4>
#
# The dark twin of ../reseller-tracker-promo, so it shows the same five sheets
# in the same order: the platform fee table that makes every later number work,
# one row per item, a box logged once as a lot, the dashboard, and the tax page.
# Same film, dark key — which is what makes a pair read as one product in two
# skins rather than as two products.
#
# Sheets' Russian "Преобразовать в таблицу" toast sits on the Setup sheet from
# 5.0 s to 7.7 s of the take. No shot goes near it: the Setup shot starts at
# 10.00 s, two and a third seconds after it is gone. See the README.
set -euo pipefail

RAW="${1:?raw recording}"; W="${2:?work dir}"; OUT="${3:?output}"
FF="$(python3 -c 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())')"
HERE="$(cd "$(dirname "$0")" && pwd)"
export WORK="$W"
mkdir -p "$W/src" "$W/scenes" "$W/layers"

# 0. normalise the Chrome .webm. This take is 1855x847 — both odd, which
#    libx264 refuses — so it is cropped to 1854x846 on the way in. The grid
#    area is 772 px; the tab strip below it stays light even in dark mode.
if [ ! -f "$W/src/rec.mp4" ]; then
  "$FF" -y -hide_banner -loglevel error -fflags +genpts -i "$RAW" \
    -vf "crop=1854:846:0:0" -r 30 -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p "$W/src/rec.mp4"
fi

[ -f "$W/fonts/PlayfairDisplay-700.ttf" ] || "$HERE/fetch_fonts.sh" "$W/fonts"
python3 "$HERE/make_layers_dark.py" "$W/layers" "$W/fonts"

# 1. the five shots.  id  start  length  crop  speed
#   s01 Setup — the platform fee table: eBay 13.3% + 0.40, Poshmark 20%,
#       Mercari 10% + 0.50, Depop 3.3% + 0.45, Etsy 9.5% + 0.45, Whatnot
#       10.9% + 0.30, Vinted and local cash at nothing. Starts at 10.00 s,
#       clear of both the Russian toast and the Yes/No list open at 9.0 s.
#   s02 Inventory & Sales — one row per item, blue in, green out.
#   s03 Lots — the Source list open on a bin of ten tees, and 45.00 for 10
#       still 4.50 an item.
#   s04 Dashboard — the whole year live: revenue 5,098.18, net profit 728.19,
#       108 items at 20.54 each, and the two-series chart beside it.
#   s05 Tax Summary — total expenses 1,490.32, NET PROFIT 728.19, then
#       573.0 miles, 401.10 off, 327.09 after mileage.
SHOTS=(
  "s01 10.00 0.90 1000:563:0:110   3.4444"
  "s02 19.85 1.55 1120:630:0:0     1.9355"
  "s03 26.45 1.40 1060:596:0:20    1.8571"
  "s04 46.20 1.45 1060:596:0:110   2.4621"
  "s05 62.90 1.05 760:428:0:344    3.5714"
)
for s in "${SHOTS[@]}"; do
  set -- $s
  "$FF" -y -hide_banner -loglevel error -ss "$2" -t "$3" -i "$W/src/rec.mp4" \
    -vf "crop=$4,scale=960:540:flags=lanczos,setsar=1,setpts=$5*PTS,format=yuv420p" -an -r 30 \
    -c:v libx264 -preset medium -crf 16 "$W/scenes/$1.mp4"
done

N=5
X=0.28
TOTAL=14.9

# 2. cross-fade the five into one screen
read -r -a DURS <<< "$(python3 -c "
import subprocess
ff='$FF'
d=[]
for i in range(1,$N+1):
    p=subprocess.run([ff,'-hide_banner','-i','$W/scenes/s%02d.mp4'%i],capture_output=True,text=True).stderr
    t=[l for l in p.splitlines() if 'Duration' in l][0].split('Duration:')[1].split(',')[0].strip()
    h,m,sec=t.split(':'); d.append(round(int(h)*3600+int(m)*60+float(sec),3))
print(' '.join(str(x) for x in d))")"
echo "shot durations: ${DURS[*]}"
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

# 3. compose. Captions are timed against the film, not against shots.
CAPS=("0.15 2.70" "3.05 4.25" "4.50 5.70" "5.95 7.95" "8.20 11.20" "11.50 14.60")
PILLS=("0.00 2.95" "2.95 5.70" "5.70 7.95" "7.95 11.25" "11.25 14.90")

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
FC2+="[$PREV]fade=t=in:st=0:d=0.35:color=0x0C1020,fade=t=out:st=14.6:d=0.3:color=0x0C1020,format=yuv420p[out]"

"$FF" -y -hide_banner -loglevel error "${INPUTS[@]}" -filter_complex "$FC2" \
  -map "[out]" -t $TOTAL -r 30 -an \
  -c:v libx264 -preset medium -crf 19 -profile:v high -level 4.0 -movflags +faststart "$OUT"

"$FF" -y -hide_banner -loglevel error -ss 1.0 -i "$OUT" -frames:v 1 -q:v 2 \
  "$(dirname "$OUT")/$(basename "${OUT%.mp4}" | sed 's/promo/cover/').jpg" 2>/dev/null || true
echo "built $OUT"
"$FF" -hide_banner -i "$OUT" 2>&1 | grep -E "Duration|Stream"
