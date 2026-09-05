#!/usr/bin/env bash
# Build the 14.9 s Etsy listing video for the Paycheck Budget workbook.
#   usage: build_paycheck_video.sh <raw-recording> <work-dir> <output.mp4>
# Ten shots cut from one take, cross-faded, dropped into the paper frame.
set -euo pipefail

RAW="${1:?raw recording}"; W="${2:?work dir}"; OUT="${3:?output}"
FF="$(python3 -c 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())')"
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$W/src" "$W/scenes" "$W/layers"

# 0. normalise the Chrome .webm (VP8, variable frame rate, no duration header)
if [ ! -f "$W/src/rec.mp4" ]; then
  "$FF" -y -hide_banner -loglevel error -fflags +genpts -i "$RAW" \
    -r 30 -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p "$W/src/rec.mp4"
fi

[ -f "$W/fonts/PlayfairDisplay-700.ttf" ] || "$HERE/fetch_fonts.sh" "$W/fonts"
python3 "$HERE/make_layers_paycheck.py" "$W/layers" "$W/fonts"

# 1. the shots — start, length, crop. The take is 1844x852 with no row-number
#    gutter, so crops start at x=0. Two things are steered around: a Russian
#    "Преобразовать в таблицу" toast that Sheets floats at y455-500 from 31.5 s
#    and at y777 from 17 s, and the tab switches at 2.6 / 10.5 / 14.8 / 29.9 /
#    34.0 / 35.8 s.
SHOTS=(
  "0.60  1.80  1150:647:0:0    setup"
  "5.20  1.75  1150:647:0:45   dashboard-headline"
  "8.30  1.75  1150:647:0:0    dashboard-spending"
  "11.60 1.80  1000:563:0:90   paycheck-budget"
  "15.00 1.75  900:506:0:105   transactions"
  "16.85 1.80  900:506:0:105   account-dropdown"
  "25.55 1.80  830:467:0:330   category-dropdown"
  "29.95 1.52  820:461:0:10    bill-calendar"
  "34.05 1.70  620:349:0:0     savings"
  "36.20 1.75  700:394:0:0     debt"
)
N=${#SHOTS[@]}
X=0.28            # cross-fade
TOTAL=14.9

i=0
for s in "${SHOTS[@]}"; do
  set -- $s; i=$((i+1))
  printf -v id "s%02d" $i
  "$FF" -y -hide_banner -loglevel error -ss "$1" -t "$2" -i "$W/src/rec.mp4" \
    -vf "crop=$3,scale=960:540:flags=lanczos,setsar=1,format=yuv420p" -an -r 30 \
    -c:v libx264 -preset medium -crf 16 "$W/scenes/$id.mp4"
done

# 2. cross-fade them into one continuous screen
read -r -a DURS <<< "$(for s in "${SHOTS[@]}"; do set -- $s; printf '%s ' "$2"; done)"
DLIST=$(IFS=,; echo "${DURS[*]}")
FC=""; PREV="0"
for i in $(seq 2 $N); do
  OFF=$(python3 -c "
d=[$DLIST]
print(round(sum(d[:$i-1]) - ($i-1)*$X, 3))" )
  FC+="[$PREV][$((i-1))]xfade=transition=fade:duration=$X:offset=$OFF[x$i]; "
  PREV="x$i"
done
"$FF" -y -hide_banner -loglevel error \
  $(for i in $(seq -w 1 $N); do printf ' -i %s' "$W/scenes/s$i.mp4"; done) \
  -filter_complex "${FC}[$PREV]format=yuv420p[v]" -map "[v]" -r 30 \
  -c:v libx264 -preset medium -crf 16 "$W/screen.mp4"

# 3. compose: background + screen + window gloss + captions + tab pill + progress bar
INPUTS=(-loop 1 -framerate 30 -t $TOTAL -i "$W/layers/bg.png"
        -i "$W/screen.mp4"
        -loop 1 -framerate 30 -t $TOTAL -i "$W/layers/fg.png"
        -loop 1 -framerate 30 -t $TOTAL -i "$W/layers/bar.png")
for i in $(seq 1 $N); do INPUTS+=(-loop 1 -framerate 30 -t $TOTAL -i "$W/layers/cap$i.png"); done
for i in $(seq 1 $N); do INPUTS+=(-loop 1 -framerate 30 -t $TOTAL -i "$W/layers/pill$i.png"); done

FC2="[0:v]format=rgba[bg];[1:v]format=rgba[scr];[bg][scr]overlay=60:300:format=auto[a];"
FC2+="[2:v]format=rgba[fg];[a][fg]overlay=0:0:format=auto[b];"
FC2+="[3:v]format=rgba[pb];[b][pb]overlay=x='-1080+1080*t/${TOTAL}':y=1075:format=auto[c0];"
PREV="c0"
for i in $(seq 1 $N); do
  read ST DU < <(python3 -c "
d=[$DLIST]
st=sum(d[:$i-1]) - ($i-1)*$X
print(round(st,3), round(d[$i-1],3))")
  CIN=$(python3 -c "print(round($ST+0.10,3))")
  COUT=$(python3 -c "print(round($ST+$DU-0.42,3))")
  IDX=$((3+i))
  FC2+="[$IDX:v]format=rgba,fade=in:st=$CIN:d=0.22:alpha=1,fade=out:st=$COUT:d=0.22:alpha=1[k$i];"
  FC2+="[$PREV][k$i]overlay=0:0:format=auto[c$i];"; PREV="c$i"
  PIN=$ST; POUT=$(python3 -c "print(round($ST+$DU-0.24,3))")
  IDX2=$((3+N+i))
  FC2+="[$IDX2:v]format=rgba,fade=in:st=$PIN:d=0.16:alpha=1,fade=out:st=$POUT:d=0.16:alpha=1[p$i];"
  FC2+="[$PREV][p$i]overlay=0:0:format=auto[q$i];"; PREV="q$i"
done
FC2+="[$PREV]fade=t=in:st=0:d=0.35:color=0xF6F9FC,fade=t=out:st=14.6:d=0.3:color=0xF6F9FC,format=yuv420p[out]"

"$FF" -y -hide_banner -loglevel error "${INPUTS[@]}" -filter_complex "$FC2" \
  -map "[out]" -t $TOTAL -r 30 -an \
  -c:v libx264 -preset medium -crf 19 -profile:v high -level 4.0 -movflags +faststart "$OUT"

"$FF" -y -hide_banner -loglevel error -ss 2.4 -i "$OUT" -frames:v 1 -q:v 2 \
  "$(dirname "$OUT")/$(basename "${OUT%.mp4}" | sed "s/promo/cover/").jpg" 2>/dev/null || true
echo "built $OUT"
"$FF" -hide_banner -i "$OUT" 2>&1 | grep -E "Duration|Stream"
