#!/usr/bin/env bash
# Build the 14.9 s Etsy listing video for the UK edition of the Reseller Tracker.
#   usage: build_uk_video.sh <raw-recording> <work-dir> <output.mp4>
#
# The workbook is the one the US listing sells, set for the UK, so the film
# leads with what actually differs and lets the rest follow: pounds, a tax year
# that starts on 6 April, HMRC's 45p a mile and a platform table with eBay
# private at nothing against eBay business at 15.9% including VAT. Then one row
# per item, a car-boot box logged once, the dashboard whose months run April to
# March, and the tax page that ends on profit after mileage.
#
# The take reads the sheets the way anyone reads a spreadsheet — scroll, stop,
# look — and every sheet here fits a screen at the right stop, so the shots are
# the stops, slowed to the time it takes to read them. Only the Lots shot is
# played near speed, because something happens in it.
set -euo pipefail

RAW="${1:?raw recording}"; W="${2:?work dir}"; OUT="${3:?output}"
FF="$(python3 -c 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())')"
HERE="$(cd "$(dirname "$0")" && pwd)"
export WORK="$W"
mkdir -p "$W/src" "$W/scenes" "$W/layers"

# 0. normalise the Chrome .webm. 1862x848, both even; the grid area is 806 px.
if [ ! -f "$W/src/rec.mp4" ]; then
  "$FF" -y -hide_banner -loglevel error -fflags +genpts -i "$RAW" \
    -r 30 -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p "$W/src/rec.mp4"
fi

[ -f "$W/fonts/PlayfairDisplay-700.ttf" ] || "$HERE/fetch_fonts.sh" "$W/fonts"
python3 "$HERE/make_layers_uk.py" "$W/layers" "$W/fonts"

# 1. the five shots.  id  start  length  crop  speed
#   s01 Setup — the UK shot. Currency label £, tax year starts day 6 month 4,
#       mileage 0.450, and in the sheet's own footnotes: "UK: tax year starts
#       6 April", "0.45 is the HMRC rate for the first 10,000 business miles
#       by car". Beside them the platform table: Vinted 0%, eBay (private) 0%,
#       eBay (business) 15.9% + 0.48, Depop 2.9% + 0.30, Whatnot 10.9%,
#       Etsy 10.5% + 0.36, car boot / cash 0%.
#   s02 Inventory & Sales — one row per item, blue in, green out.
#   s03 Lots, at speed: the Source list opens on a box of ten tees and the
#       sources are the British ones — charity shop, car boot sale, jumble
#       sale, house clearance — and 45.00 for 10 is still 4.50 an item.
#   s04 Dashboard — Period 06 Apr 2026 to 05 Apr 2027, net profit 1,898.00,
#       and a chart whose months run Apr 2026 to Mar 2027.
#   s05 Tax Summary — total expenses 900.88, NET PROFIT 1,898.00, then
#       372.2 miles at HMRC's rate, 167.49 off, 1,730.51 after mileage.
SHOTS=(
  "s01  3.80 1.25 1000:563:0:110   2.48"
  "s02 10.42 0.66 1120:630:0:0     4.5455"
  "s03 19.10 2.00 1060:596:0:0     1.30"
  "s04 33.20 1.75 1060:596:0:110   2.0571"
  "s05 44.45 1.00 760:428:0:330    3.72"
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
CAPS=("0.15 1.60" "1.85 2.95" "3.15 5.65" "5.90 7.95" "8.20 10.00" "10.30 11.30" "11.60 14.60")
PILLS=("0.00 2.95" "2.95 5.65" "5.65 7.95" "7.95 11.30" "11.30 14.90")

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
FC2+="[$PREV]fade=t=in:st=0:d=0.35:color=0xD4E2E9,fade=t=out:st=14.6:d=0.3:color=0xD4E2E9,format=yuv420p[out]"

"$FF" -y -hide_banner -loglevel error "${INPUTS[@]}" -filter_complex "$FC2" \
  -map "[out]" -t $TOTAL -r 30 -an \
  -c:v libx264 -preset medium -crf 19 -profile:v high -level 4.0 -movflags +faststart "$OUT"

"$FF" -y -hide_banner -loglevel error -ss 1.0 -i "$OUT" -frames:v 1 -q:v 2 \
  "$(dirname "$OUT")/$(basename "${OUT%.mp4}" | sed 's/promo/cover/').jpg" 2>/dev/null || true
echo "built $OUT"
"$FF" -hide_banner -i "$OUT" 2>&1 | grep -E "Duration|Stream"
