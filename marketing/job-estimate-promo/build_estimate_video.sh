#!/usr/bin/env bash
# Build the 14.9 s Etsy listing video for the Estimate & Invoice workbook.
#   usage: build_estimate_video.sh <raw-recording> <work-dir> <output.mp4>
#
# The listing's claim is that a job is quoted, invoiced and filed on one page
# each, so the film proves it with two uncut moves: the whole Estimate travels
# past in one shot, then the whole Invoice does, landing on the balance due.
# Between them sits the one beat that shows the sheet doing the arithmetic —
# a rate type is picked and the line, the amount and the labour subtotal all
# move inside a SINGLE shot, because cutting between before and after is what
# makes a viewer doubt it. It closes on the Job Log filing the job.
set -euo pipefail

RAW="${1:?raw recording}"; W="${2:?work dir}"; OUT="${3:?output}"
FF="$(python3 -c 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())')"
HERE="$(cd "$(dirname "$0")" && pwd)"
export WORK="$W"
mkdir -p "$W/src" "$W/scenes" "$W/layers"

# 0. normalise the Chrome .webm (VP8, variable frame rate, no duration header).
if [ ! -f "$W/src/rec.mp4" ]; then
  "$FF" -y -hide_banner -loglevel error -fflags +genpts -i "$RAW" \
    -r 30 -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p "$W/src/rec.mp4"
fi

[ -f "$W/fonts/PlayfairDisplay-700.ttf" ] || "$HERE/fetch_fonts.sh" "$W/fonts"
python3 "$HERE/make_layers_estimate.py" "$W/layers" "$W/fonts"

# 1. shot 1 — the Estimate, whole page, one move. The take wheels UP through it
#    between 6.2 s and 3.4 s, so the pass is read in that order: these are the
#    moments it is at REST between wheel steps, which is what keeps the stitch
#    free of the ghost VP8 leaves at a viewport's top edge.
EST="6.2,5.8,5.4,5.1,4.8,4.1,3.4"
python3 "$HERE/make_page.py" "$W/src/rec.mp4" "$W/scenes/s01.mp4" "$EST" 1400 "1.00,3.80,0.60"

# 2. shot 2 — the rate type. One shot, no cut: the list is open on "After
#    hours", "Weekend" is picked, and the rate, the amount and the Labour
#    subtotal (797.50 -> 805.00) all move on screen. Cropped to 1072 px so the
#    subtotal is legible, stops short of the scrollbar, and is slowed to 0.81x:
#    the take only holds the open list for four tenths of a second, less than it
#    takes to read four rate types and then watch the number move.
"$FF" -y -hide_banner -loglevel error -ss 12.60 -t 2.10 -i "$W/src/rec.mp4" \
  -vf "crop=1072:603:0:187,scale=960:540:flags=lanczos,setsar=1,setpts=1.2381*PTS,format=yuv420p" -an -r 30 \
  -c:v libx264 -preset medium -crf 16 "$W/scenes/s02.mp4"

# 3. shot 3 — the Invoice, whole page, one move, ending on BALANCE DUE. Same
#    treatment as the Estimate; this pass wheels DOWN, 22.9 s to 30.2 s.
INV="22.9,23.4,23.7,24.2,24.5,25.0,25.4,25.9,26.5,27.3,27.6,27.9,29.6,29.9,30.2"
python3 "$HERE/make_page.py" "$W/src/rec.mp4" "$W/scenes/s03.mp4" "$INV" 1400 "0.65,3.30,0.55"

# 4. shot 4 — the Job Log. Three jobs are filed while the KPI row above them
#    recounts; uncut, for the same reason.
"$FF" -y -hide_banner -loglevel error -ss 35.10 -t 3.24 -i "$W/src/rec.mp4" \
  -vf "crop=1250:703:0:30,scale=960:540:flags=lanczos,setsar=1,format=yuv420p" -an -r 30 \
  -c:v libx264 -preset medium -crf 16 "$W/scenes/s04.mp4"

N=4
X=0.28
TOTAL=14.9

# 5. cross-fade the four into one screen
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

# 6. compose. Captions are timed against the film, not against shots, so a line
#    can change while the page keeps moving under it.
CAPS=("0.15 2.20" "2.50 4.95" "5.25 7.55" "7.85 9.55" "9.85 11.60" "11.95 14.60")
PILLS=("0.00 7.40" "7.40 11.70" "11.70 14.90")

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
FC2+="[$PREV]fade=t=in:st=0:d=0.35:color=0xD8C8A8,fade=t=out:st=14.6:d=0.3:color=0xD8C8A8,format=yuv420p[out]"

"$FF" -y -hide_banner -loglevel error "${INPUTS[@]}" -filter_complex "$FC2" \
  -map "[out]" -t $TOTAL -r 30 -an \
  -c:v libx264 -preset medium -crf 19 -profile:v high -level 4.0 -movflags +faststart "$OUT"

"$FF" -y -hide_banner -loglevel error -ss 1.2 -i "$OUT" -frames:v 1 -q:v 2 \
  "$(dirname "$OUT")/$(basename "${OUT%.mp4}" | sed 's/promo/cover/').jpg" 2>/dev/null || true
echo "built $OUT"
"$FF" -hide_banner -i "$OUT" 2>&1 | grep -E "Duration|Stream"
