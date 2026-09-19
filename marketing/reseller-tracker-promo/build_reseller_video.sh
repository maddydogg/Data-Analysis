#!/usr/bin/env bash
# Build the 14.9 s Etsy listing video for the Reseller Tracker workbook.
#   usage: build_reseller_video.sh <raw-recording> <work-dir> <output.mp4>
#
# The take walks eight sheets in 46 s, which is four times more than fits. The
# film keeps the five that carry the argument, in the order a seller meets them:
# set the platform fees once, log one row per item, log a whole box as one lot,
# read which source actually pays, and take the tax totals off the last sheet.
# The last of those is the only one that does not fit a screen, so it is
# stitched out of the take's own scroll and travels past in ONE uncut move.
set -euo pipefail

RAW="${1:?raw recording}"; W="${2:?work dir}"; OUT="${3:?output}"
FF="$(python3 -c 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())')"
HERE="$(cd "$(dirname "$0")" && pwd)"
export WORK="$W"
mkdir -p "$W/src" "$W/scenes" "$W/layers"

# 0. normalise the Chrome .webm. This take is 1862x718 — a short viewport, so
#    the grid area is only 676 px and make_page is set to read that.
if [ ! -f "$W/src/rec.mp4" ]; then
  "$FF" -y -hide_banner -loglevel error -fflags +genpts -i "$RAW" \
    -r 30 -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p "$W/src/rec.mp4"
fi

[ -f "$W/fonts/PlayfairDisplay-700.ttf" ] || "$HERE/fetch_fonts.sh" "$W/fonts"
python3 "$HERE/make_layers_reseller.py" "$W/layers" "$W/fonts"

# 1-4. the four sheets that each fit one screen.
#   Setup      — the platform fee table, which is what makes every later number
#                work: eBay 13.3% + 0.40, Poshmark 20%, Mercari 10% + 0.50 …
#   Inventory  — the take scrolls the rows under the frozen header and settles;
#                played at 0.86x so the settle is not over before it is read.
#   Lots       — LOT-02: one box, 45.00 for 10 tees, 4.50 an item, worked out.
#   Dashboard  — WHERE TO BUY. Garage sale 227.6% ROI against retail clearance
#                125%. The take holds it for 1.7 s, so it runs at 0.65x.
SHOTS=(
  "s01  0.40 2.60 1010:568:0:20   1.0"
  "s02  9.40 2.50 1010:568:0:0    1.16"
  "s03 18.60 2.50 1010:568:0:0    1.0"
  "s04 36.10 1.70 900:506:0:150   1.5294"
)
for s in "${SHOTS[@]}"; do
  set -- $s
  "$FF" -y -hide_banner -loglevel error -ss "$2" -t "$3" -i "$W/src/rec.mp4" \
    -vf "crop=$4,scale=960:540:flags=lanczos,setsar=1,setpts=$5*PTS,format=yuv420p" -an -r 30 \
    -c:v libx264 -preset medium -crf 16 "$W/scenes/$1.mp4"
done

# 5. the Tax Summary, whole, one move. It is the only sheet here that is longer
#    than a screen — 1,347 px of it — and it has no frozen header, so the whole
#    page is stitched out of the take's resting moments between wheel steps and
#    scrolled from the tax year down to the profit after mileage.
TAX="39.6,40.4,41.0,41.4,42.0,42.9,43.8,45.0"
python3 "$HERE/make_page.py" "$W/src/rec.mp4" "$W/scenes/s05.mp4" "$TAX" 700 "0.70,4.10,0.62"

N=5
X=0.28
TOTAL=14.9

# 6. cross-fade the five into one screen
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

# 7. compose. Captions are timed against the film, not against shots.
CAPS=("0.15 2.20" "2.60 3.75" "4.00 5.10" "5.35 7.30" "7.55 9.60" "9.90 12.10" "12.40 14.60")
PILLS=("0.00 2.45" "2.45 4.95" "4.95 7.30" "7.30 9.60" "9.60 14.90")

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
FC2+="[$PREV]fade=t=in:st=0:d=0.35:color=0xDBE9E4,fade=t=out:st=14.6:d=0.3:color=0xDBE9E4,format=yuv420p[out]"

"$FF" -y -hide_banner -loglevel error "${INPUTS[@]}" -filter_complex "$FC2" \
  -map "[out]" -t $TOTAL -r 30 -an \
  -c:v libx264 -preset medium -crf 19 -profile:v high -level 4.0 -movflags +faststart "$OUT"

"$FF" -y -hide_banner -loglevel error -ss 1.2 -i "$OUT" -frames:v 1 -q:v 2 \
  "$(dirname "$OUT")/$(basename "${OUT%.mp4}" | sed 's/promo/cover/').jpg" 2>/dev/null || true
echo "built $OUT"
"$FF" -hide_banner -i "$OUT" 2>&1 | grep -E "Duration|Stream"
