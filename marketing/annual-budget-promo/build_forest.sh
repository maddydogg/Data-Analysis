#!/usr/bin/env bash
# Build the 14.9 s Etsy listing video for the LIGHT couples edition (forest-green frame).
#   usage: build.sh <raw-recording> <work-dir> <output.mp4>
set -euo pipefail

RAW="${1:?raw recording}"; W="${2:?work dir}"; OUT="${3:?output}"
FF="$(python3 -c 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())')"
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$W/src" "$W/scenes" "$W/layers"

# 0. normalise the Chrome .webm (VFR, odd width, no duration header)
if [ ! -f "$W/src/rec.mp4" ]; then
  "$FF" -y -hide_banner -loglevel error -fflags +genpts -i "$RAW" \
    -vf "crop=1918:886:0:0" -r 30 -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p "$W/src/rec.mp4"
fi

python3 "$HERE/make_layers_forest.py" "$W/layers" "$W/fonts"

SW=960; SH=540; D=1.609; X=0.28

cut () {  # name start crop
  "$FF" -y -hide_banner -loglevel error -ss "$2" -t "$D" -i "$W/src/rec.mp4" \
    -vf "$3,scale=${SW}:${SH}:flags=lanczos,setsar=1,format=yuv420p" -an -r 30 \
    -c:v libx264 -preset medium -crf 16 "$W/scenes/$1.mp4"
}

# 1. eleven shots. Crops start at x=58 — the light theme shows a row-number
#    gutter to the left of that. No Sheets toast or tab-switch flash in this take.
cut s01 2.2  "crop=1400:787:58:30"    # Transactions — Paid by / Share columns
cut s02 6.8  "crop=1400:787:58:30"    # Transactions — Share dropdown open
cut s03 20.2 "crop=1290:726:58:30"    # Annual Dashboard — KPIs + month table
cut s04 14.5 "crop=900:506:58:30"     # Spending by Category doughnut
cut s05 11.0 "crop=1000:563:58:100"   # Income vs Expenses + Saved by Month
cut s06 22.5 "crop=1150:647:58:20"    # 50 / 30 / 20 Rule — all three on track
cut s07 24.5 "crop=950:534:58:20"     # Spending Tracker
cut s08 27.0 "crop=900:506:58:20"     # Split and Settle — Sam owes Alex $5,089.00
cut s09 33.0 "crop=950:534:58:20"     # Month View — month picker open
cut s10 45.0 "crop=1100:619:58:20"    # Bill Calendar — frequency dropdown
cut s11 50.3 "crop=1350:759:58:20"    # Savings & Net Worth

# 2. cross-fade the ten shots into one continuous screen
FC=""; PREV="0"
for i in $(seq 2 11); do
  OFF=$(python3 -c "print(round(($i-1)*($D-$X),3))")
  IN=$((i-1))
  FC+="[$PREV][$IN]xfade=transition=fade:duration=$X:offset=$OFF[x$i]; "
  PREV="x$i"
done
"$FF" -y -hide_banner -loglevel error \
  $(for i in $(seq -w 1 11); do printf ' -i %s' "$W/scenes/s$i.mp4"; done) \
  -filter_complex "${FC}[$PREV]format=yuv420p[v]" -map "[v]" -r 30 \
  -c:v libx264 -preset medium -crf 16 "$W/screen.mp4"

# 3. compose: background + screen + window gloss + captions + tab highlight + progress bar
TOTAL=14.9
INPUTS=(-loop 1 -framerate 30 -t $TOTAL -i "$W/layers/bg.png"
        -i "$W/screen.mp4"
        -loop 1 -framerate 30 -t $TOTAL -i "$W/layers/fg.png"
        -loop 1 -framerate 30 -t $TOTAL -i "$W/layers/bar.png")
for i in $(seq 1 11); do INPUTS+=(-loop 1 -framerate 30 -t $TOTAL -i "$W/layers/cap$i.png"); done
for i in $(seq 1 11); do INPUTS+=(-loop 1 -framerate 30 -t $TOTAL -i "$W/layers/pill$i.png"); done

FC2="[0:v]format=rgba[bg];[1:v]format=rgba[scr];[bg][scr]overlay=60:300:format=auto[a];"
FC2+="[2:v]format=rgba[fg];[a][fg]overlay=0:0:format=auto[b];"
# progress bar slides in from the left over the full duration
FC2+="[3:v]format=rgba[pb];[b][pb]overlay=x='-1080+1080*t/${TOTAL}':y=1075:format=auto[c0];"
PREV="c0"
for i in $(seq 1 11); do
  ST=$(python3 -c "print(round(($i-1)*($D-$X),3))")
  CIN=$(python3 -c "print(round($ST+0.10,3))"); COUT=$(python3 -c "print(round($ST+1.14,3))")
  IDX=$((3+i))
  FC2+="[$IDX:v]format=rgba,fade=in:st=$CIN:d=0.22:alpha=1,fade=out:st=$COUT:d=0.22:alpha=1[k$i];"
  FC2+="[$PREV][k$i]overlay=0:0:format=auto[c$i];"; PREV="c$i"
done
for i in $(seq 1 11); do
  ST=$(python3 -c "print(round(($i-1)*($D-$X),3))")
  PIN=$(python3 -c "print(round($ST,3))"); POUT=$(python3 -c "print(round($ST+1.33,3))")
  IDX=$((14+i))
  FC2+="[$IDX:v]format=rgba,fade=in:st=$PIN:d=0.16:alpha=1,fade=out:st=$POUT:d=0.16:alpha=1[p$i];"
  FC2+="[$PREV][p$i]overlay=0:0:format=auto[q$i];"; PREV="q$i"
done
FC2+="[$PREV]fade=t=in:st=0:d=0.35:color=0x0C1B14,fade=t=out:st=14.6:d=0.3:color=0x0C1B14,format=yuv420p[out]"

"$FF" -y -hide_banner -loglevel error "${INPUTS[@]}" -filter_complex "$FC2" \
  -map "[out]" -t $TOTAL -r 30 -an \
  -c:v libx264 -preset medium -crf 19 -profile:v high -level 4.0 -movflags +faststart "$OUT"

echo "built $OUT"
"$FF" -hide_banner -i "$OUT" 2>&1 | grep -E "Duration|Stream"
