#!/usr/bin/env bash
# Build the 14.9 s Etsy listing video for the dark-theme Annual Budget spreadsheet.
#   usage: build.sh <raw-recording> <work-dir> <output.mp4>
set -euo pipefail

RAW="${1:?raw recording}"; W="${2:?work dir}"; OUT="${3:?output}"
FF="$(python3 -c 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())')"
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$W/src" "$W/scenes" "$W/layers"

# 0. normalise the Chrome .webm (VFR, odd width, no duration header)
if [ ! -f "$W/src/rec.mp4" ]; then
  "$FF" -y -hide_banner -loglevel error -fflags +genpts -i "$RAW" \
    -vf "crop=1918:882:0:0" -r 30 -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p "$W/src/rec.mp4"
fi

python3 "$HERE/make_layers_dark.py" "$W/layers" "$W/fonts"

SW=960; SH=540; D=1.76; X=0.30

cut () {  # name start crop
  "$FF" -y -hide_banner -loglevel error -ss "$2" -t "$D" -i "$W/src/rec.mp4" \
    -vf "$3,scale=${SW}:${SH}:flags=lanczos,setsar=1,format=yuv420p" -an -r 30 \
    -c:v libx264 -preset medium -crf 16 "$W/scenes/$1.mp4"
}

# 1. ten shots. Every crop starts at x=56 to clear the light row-number gutter
#    and at y>=28 to clear the column-letter strip. Defects avoided:
#      1.5-3.0 s and 52.0-59.0 s  Russian "Преобразовать в таблицу" toast
#      39.0 s and 49.5 s          white flash while switching tabs
#    The Bill Calendar shot is taken during the toast window but cropped to
#    x<836; the toast sits at x 867-1131, outside the frame.
cut s01 3.2  "crop=880:495:56:32"     # Setup — lists
cut s02 9.4  "crop=860:484:56:32"     # Transactions — account dropdown open
cut s03 15.5 "crop=1300:731:56:32"    # Annual Dashboard — KPIs + month table
cut s04 20.6 "crop=925:520:56:305"    # 50/30/20 table + Spending by Category
cut s05 28.0 "crop=700:394:56:45"     # Income vs Expenses by month
cut s06 33.5 "crop=1100:619:56:28"    # 50 / 30 / 20 Rule
cut s07 36.8 "crop=1000:563:56:28"    # Spending Tracker
cut s08 44.6 "crop=900:506:56:32"     # Month View — month picker open
cut s09 53.2 "crop=780:439:56:100"    # Bill Calendar — frequency changed, totals recalculated
cut s10 60.2 "crop=1200:675:56:28"    # Savings & Net Worth

# 2. cross-fade the ten shots into one continuous screen
FC=""; PREV="0"
for i in $(seq 2 10); do
  OFF=$(python3 -c "print(round(($i-1)*($D-$X),3))")
  IN=$((i-1))
  FC+="[$PREV][$IN]xfade=transition=fade:duration=$X:offset=$OFF[x$i]; "
  PREV="x$i"
done
"$FF" -y -hide_banner -loglevel error \
  $(for i in $(seq -w 1 10); do printf ' -i %s' "$W/scenes/s$i.mp4"; done) \
  -filter_complex "${FC}[$PREV]format=yuv420p[v]" -map "[v]" -r 30 \
  -c:v libx264 -preset medium -crf 16 "$W/screen.mp4"

# 3. compose: background + screen + window gloss + captions + tab highlight + progress bar
TOTAL=14.9
INPUTS=(-loop 1 -framerate 30 -t $TOTAL -i "$W/layers/bg.png"
        -i "$W/screen.mp4"
        -loop 1 -framerate 30 -t $TOTAL -i "$W/layers/fg.png"
        -loop 1 -framerate 30 -t $TOTAL -i "$W/layers/bar.png")
for i in $(seq 1 10); do INPUTS+=(-loop 1 -framerate 30 -t $TOTAL -i "$W/layers/cap$i.png"); done
for i in $(seq 1 10); do INPUTS+=(-loop 1 -framerate 30 -t $TOTAL -i "$W/layers/pill$i.png"); done

FC2="[0:v]format=rgba[bg];[1:v]format=rgba[scr];[bg][scr]overlay=60:300:format=auto[a];"
FC2+="[2:v]format=rgba[fg];[a][fg]overlay=0:0:format=auto[b];"
# progress bar slides in from the left over the full duration
FC2+="[3:v]format=rgba[pb];[b][pb]overlay=x='-1080+1080*t/${TOTAL}':y=1075:format=auto[c0];"
PREV="c0"
for i in $(seq 1 10); do
  ST=$(python3 -c "print(round(($i-1)*($D-$X),3))")
  CIN=$(python3 -c "print(round($ST+0.12,3))"); COUT=$(python3 -c "print(round($ST+1.28,3))")
  IDX=$((3+i))
  FC2+="[$IDX:v]format=rgba,fade=in:st=$CIN:d=0.22:alpha=1,fade=out:st=$COUT:d=0.22:alpha=1[k$i];"
  FC2+="[$PREV][k$i]overlay=0:0:format=auto[c$i];"; PREV="c$i"
done
for i in $(seq 1 10); do
  ST=$(python3 -c "print(round(($i-1)*($D-$X),3))")
  PIN=$(python3 -c "print(round($ST,3))"); POUT=$(python3 -c "print(round($ST+1.46,3))")
  IDX=$((13+i))
  FC2+="[$IDX:v]format=rgba,fade=in:st=$PIN:d=0.16:alpha=1,fade=out:st=$POUT:d=0.16:alpha=1[p$i];"
  FC2+="[$PREV][p$i]overlay=0:0:format=auto[q$i];"; PREV="q$i"
done
FC2+="[$PREV]fade=t=in:st=0:d=0.35:color=0x0A101E,fade=t=out:st=14.6:d=0.3:color=0x0A101E,format=yuv420p[out]"

"$FF" -y -hide_banner -loglevel error "${INPUTS[@]}" -filter_complex "$FC2" \
  -map "[out]" -t $TOTAL -r 30 -an \
  -c:v libx264 -preset medium -crf 19 -profile:v high -level 4.0 -movflags +faststart "$OUT"

echo "built $OUT"
"$FF" -hide_banner -i "$OUT" 2>&1 | grep -E "Duration|Stream"
