#!/usr/bin/env bash
# Build the 14.9 s Etsy listing video for the Job Invoice workbook.
#   usage: build_invoice_video.sh <raw-recording> <work-dir> <output.mp4>
#
# The listing's argument is "set it up once, then every job is one page", so the
# film opens on the whole Setup sheet — which fits one screen, and is therefore
# held whole rather than scrolled — and closes on the whole Invoice travelling
# past in one uncut move to the balance due. Between them sit the two beats that
# show the sheet doing the pricing, each in a SINGLE shot: a line switched to a
# flat price, and a rate type picked. Cutting between a before and an after is
# what makes a viewer doubt the sheet did the work.
set -euo pipefail

RAW="${1:?raw recording}"; W="${2:?work dir}"; OUT="${3:?output}"
FF="$(python3 -c 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())')"
HERE="$(cd "$(dirname "$0")" && pwd)"
export WORK="$W"
mkdir -p "$W/src" "$W/scenes" "$W/layers"

# 0. normalise the Chrome .webm. This take is 1860x849 — an odd height, which
#    libx264 refuses — so it is cropped to 848 on the way in.
if [ ! -f "$W/src/rec.mp4" ]; then
  "$FF" -y -hide_banner -loglevel error -fflags +genpts -i "$RAW" \
    -vf "crop=1860:848:0:0" -r 30 -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p "$W/src/rec.mp4"
fi

[ -f "$W/fonts/PlayfairDisplay-700.ttf" ] || "$HERE/fetch_fonts.sh" "$W/fonts"
python3 "$HERE/make_layers_invoice.py" "$W/layers" "$W/fonts"

# 1. shot 1 — the whole Setup sheet. The take nudges it down 120 px and back
#    between 1.5 s and 3.0 s, which is enough to reach the end of YOUR SERVICES;
#    stitched, the sheet is 842 px, shorter than the window's own 877, so
#    make_page holds it whole instead of scrolling it. That IS the claim.
python3 "$HERE/make_page.py" "$W/src/rec.mp4" "$W/scenes/s01.mp4" "0.8,2.2" 1560 "1.00,1.70,0.60"

# 2. shot 2 — the flat price. One shot, no cut: the rate type list is open on
#    "After hours", "Flat rate" is picked, the Rate column empties, the Fixed
#    price cell turns amber because that is what the sheet now needs, and the
#    Labour subtotal drops 702.50 -> 477.50.
"$FF" -y -hide_banner -loglevel error -ss 10.40 -t 3.00 -i "$W/src/rec.mp4" \
  -vf "crop=1056:594:0:170,scale=960:540:flags=lanczos,setsar=1,format=yuv420p" -an -r 30 \
  -c:v libx264 -preset medium -crf 16 "$W/scenes/s02.mp4"

# 3. shot 3 — the rate type. Same treatment: the list opens, "Weekend" is
#    picked, and the rate 65.00 -> 95.00, the amount 260.00 -> 380.00 and the
#    Labour subtotal 640.00 -> 760.00 all move inside the one frame. It has to
#    end before 23.4 s, which is where the take starts scrolling, and that
#    leaves only eight tenths of a second on the new number — so this shot runs
#    at 0.8x, which buys a full second of it.
"$FF" -y -hide_banner -loglevel error -ss 20.95 -t 2.40 -i "$W/src/rec.mp4" \
  -vf "crop=1056:594:0:170,scale=960:540:flags=lanczos,setsar=1,setpts=1.25*PTS,format=yuv420p" -an -r 30 \
  -c:v libx264 -preset medium -crf 16 "$W/scenes/s03.mp4"

# 4. shot 4 — the whole Invoice, one move, landing on BALANCE DUE. The pass is
#    the take's own resting moments between wheel steps, 23.0 s to 31.8 s.
#    The take only ever shows the sheet's header BEFORE the rate types are
#    edited, so PAGE_HEAD takes the first 150 px from 4.6 s and everything below
#    from the final pass — otherwise this one uncut shot would carry an old
#    Labour subtotal above a new one in the totals.
INV="23.0,23.5,23.8,24.1,25.0,25.3,25.6,26.2,26.8,27.3,27.6,27.9,28.2,28.7,29.6,30.2,30.6,30.9,31.2,31.5,31.8"
PAGE_HEAD="4.6,150" python3 "$HERE/make_page.py" "$W/src/rec.mp4" "$W/scenes/s04.mp4" "$INV" 1260 "1.00,5.00,0.64"

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

# 6. compose. Captions are timed against the film, not against shots.
CAPS=("0.15 2.95" "3.30 4.55" "4.80 5.80" "6.10 8.40" "8.70 11.10" "11.45 14.60")
PILLS=("0.00 3.10" "3.10 14.90")

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
FC2+="[$PREV]fade=t=in:st=0:d=0.35:color=0xD3E5DB,fade=t=out:st=14.6:d=0.3:color=0xD3E5DB,format=yuv420p[out]"

"$FF" -y -hide_banner -loglevel error "${INPUTS[@]}" -filter_complex "$FC2" \
  -map "[out]" -t $TOTAL -r 30 -an \
  -c:v libx264 -preset medium -crf 19 -profile:v high -level 4.0 -movflags +faststart "$OUT"

"$FF" -y -hide_banner -loglevel error -ss 1.2 -i "$OUT" -frames:v 1 -q:v 2 \
  "$(dirname "$OUT")/$(basename "${OUT%.mp4}" | sed 's/promo/cover/').jpg" 2>/dev/null || true
echo "built $OUT"
"$FF" -hide_banner -i "$OUT" 2>&1 | grep -E "Duration|Stream"
