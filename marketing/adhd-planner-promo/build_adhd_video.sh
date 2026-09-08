#!/usr/bin/env bash
# Build the 14.9 s Etsy listing video for the ADHD Planner workbook.
#   usage: build_adhd_video.sh <raw-recording> <work-dir> <output.mp4>
#
# The competitor for this product shows six dense dashboards in 15 seconds and
# explains none of them, under one headline that never changes. So this film
# does the opposite: the Today sheet travels past in ONE uncut move with the
# caption changing over it, then three close cuts on the things a still page
# cannot show — the energy list, the status list, the habit grid — each captioned
# in the sheet's own words, each framed large enough to read.
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
python3 "$HERE/make_layers_adhd.py" "$W/layers" "$W/fonts"

# 1. shot 1 — the Today sheet, held and then scrolled, in one take. The take
#    scrolls it in wheel steps between 0.5 s and 9.9 s; these are the moments it
#    is at rest, so the stitch never picks up the encoder's post-scroll ghost.
PASS="0.5,0.9,1.4,1.7,2.0,2.4,2.7,3.0,3.3,3.6,3.9,4.3,4.6,4.9,5.2,5.6,5.9,6.2,6.6,7.0,7.3,7.6,8.0,8.3,8.6,8.8,9.2,9.9"
python3 "$HERE/make_page.py" "$W/src/rec.mp4" "$W/scenes/s01.mp4" "$PASS" 1200 "1.60,5.00,0.70"

# 2. the four cuts that follow. Tabs switch at 10.8 s (Tasks) and 21.2 s
#    (Habits), so no shot crosses those. The two dropdown shots are cropped to
#    760 px wide — 1.26x on the way to the window — because the whole point
#    against this competitor is that you can read what is happening.
SHOTS=(
  "11.90 1.80  680:383:1100:52  break-it-down"
  "15.45 1.95  760:428:0:55    energy-list"
  "18.30 1.95  760:428:0:55    status-parked"
  "37.00 3.02  1150:647:0:20   habits"
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
CAPS=("0.15 2.45" "2.75 4.75" "5.05 6.85" "7.20 8.30" "8.80 10.05" "10.45 11.70" "12.10 14.62")
PILLS=("0.00 7.10" "7.10 11.95" "11.95 14.90")

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
FC2+="[$PREV]fade=t=in:st=0:d=0.35:color=0xFDFDFB,fade=t=out:st=14.6:d=0.3:color=0xFDFDFB,format=yuv420p[out]"

"$FF" -y -hide_banner -loglevel error "${INPUTS[@]}" -filter_complex "$FC2" \
  -map "[out]" -t $TOTAL -r 30 -an \
  -c:v libx264 -preset medium -crf 19 -profile:v high -level 4.0 -movflags +faststart "$OUT"

"$FF" -y -hide_banner -loglevel error -ss 1.2 -i "$OUT" -frames:v 1 -q:v 2 \
  "$(dirname "$OUT")/$(basename "${OUT%.mp4}" | sed 's/promo/cover/').jpg" 2>/dev/null || true
echo "built $OUT"
"$FF" -hide_banner -i "$OUT" 2>&1 | grep -E "Duration|Stream"
