#!/usr/bin/env bash
# Build the 14.9 s Etsy listing video for the Simple Reseller Tracker workbook.
#   usage: build_simple_video.sh <raw-recording> <work-dir> <output.mp4>
#
# Two sheets, so five shots: the Items table, the one beat that proves the sheet
# does the arithmetic, and the three things the Summary works out from it. The
# beat is uncut on purpose — a platform is picked and the Fees and Profit cells
# fill in inside a single frame, because cutting between a before and an after
# is what makes a viewer doubt the sheet did the work.
#
# Both sheets freeze their head, and the take reads them the way anyone reads a
# spreadsheet: scroll, stop, look. So four of the five shots are the stops,
# slowed to the time it takes to read them — none of them is stitched, because
# nothing here is longer than the thing it has to say.
set -euo pipefail

RAW="${1:?raw recording}"; W="${2:?work dir}"; OUT="${3:?output}"
FF="$(python3 -c 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())')"
HERE="$(cd "$(dirname "$0")" && pwd)"
export WORK="$W"
mkdir -p "$W/src" "$W/scenes" "$W/layers"

# 0. normalise the Chrome .webm. 1862x718, both even; the grid area is 676 px.
if [ ! -f "$W/src/rec.mp4" ]; then
  "$FF" -y -hide_banner -loglevel error -fflags +genpts -i "$RAW" \
    -r 30 -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p "$W/src/rec.mp4"
fi

[ -f "$W/fonts/PlayfairDisplay-700.ttf" ] || "$HERE/fetch_fonts.sh" "$W/fonts"
python3 "$HERE/make_layers_simple.py" "$W/layers" "$W/fonts"

# 1. the five shots.  id  start  length  crop  speed
#   s01 Items — the rows come to rest under the frozen header: Item, Paid, Sold
#       for, Profit, Platform, Date sold, Shipping, Fees, Date bought.
#   s02 THE BEAT, uncut: the Platform list is open on Vinted, which charges
#       nothing, Poshmark is picked, and Fees goes 0.00 -> 3.47 while Profit
#       goes 13.11 -> 9.64. The row above it did the same a moment earlier,
#       16.00 -> 13.72, and both are in frame.
#   s03 Summary, head: profit this month and all time, items sold, average
#       profit per sale, stock still to sell — beside YOUR SETTINGS, the fee
#       table those numbers are worked out from.
#   s04 BY MONTH, every month and the year: 50 items, 1,815.92 sold,
#       193.24 in fees, 960.73 profit.
#   s05 BY PLATFORM: Mercari 279.92 against Whatnot 99.28 on the same 7-10 items.
SHOTS=(
  "s01  3.30 2.00 1120:630:0:0    1.80"
  "s02  7.60 2.40 1000:563:0:60   1.3333"
  "s03 11.10 1.05 1031:580:0:0    2.9524"
  "s04 17.00 0.40 836:470:0:110   7.75"
  "s05 20.00 0.30 750:422:0:100  10.0667"
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
CAPS=("0.15 1.85" "2.10 3.30" "3.60 4.90" "5.15 6.45" "6.75 9.20" "9.50 11.95" "12.25 14.60")
PILLS=("0.00 6.35" "6.35 14.90")

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
FC2+="[$PREV]fade=t=in:st=0:d=0.35:color=0xD8EDE1,fade=t=out:st=14.6:d=0.3:color=0xD8EDE1,format=yuv420p[out]"

"$FF" -y -hide_banner -loglevel error "${INPUTS[@]}" -filter_complex "$FC2" \
  -map "[out]" -t $TOTAL -r 30 -an \
  -c:v libx264 -preset medium -crf 19 -profile:v high -level 4.0 -movflags +faststart "$OUT"

"$FF" -y -hide_banner -loglevel error -ss 1.2 -i "$OUT" -frames:v 1 -q:v 2 \
  "$(dirname "$OUT")/$(basename "${OUT%.mp4}" | sed 's/promo/cover/').jpg" 2>/dev/null || true
echo "built $OUT"
"$FF" -hide_banner -i "$OUT" 2>&1 | grep -E "Duration|Stream"
