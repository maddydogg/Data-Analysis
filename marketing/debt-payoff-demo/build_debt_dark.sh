#!/usr/bin/env bash
# Build the 14.9 s Etsy listing video for the DARK Debt Payoff workbook.
#   usage: build.sh <raw-recording> <work-dir> <output.mp4>
set -euo pipefail

RAW="${1:?raw recording}"; W="${2:?work dir}"; OUT="${3:?output}"
FF="$(python3 -c 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())')"
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$W/src" "$W/scenes" "$W/layers"

# 0. normalise the Chrome .webm (VFR, odd width, no duration header)
if [ ! -f "$W/src/rec.mp4" ]; then
  "$FF" -y -hide_banner -loglevel error -fflags +genpts -i "$RAW" \
    -vf "crop=1862:852:0:0" -r 30 -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p "$W/src/rec.mp4"
fi

python3 "$HERE/make_layers_debt_dark.py" "$W/layers" "$W/fonts"

SW=960; SH=540; N=9; D=1.9044; X=0.28

cut () {  # name start crop
  "$FF" -y -hide_banner -loglevel error -ss "$2" -t "$D" -i "$W/src/rec.mp4" \
    -vf "$3,scale=${SW}:${SH}:flags=lanczos,setsar=1,format=yuv420p" -an -r 30 \
    -c:v libx264 -preset medium -crf 16 "$W/scenes/$1.mp4"
}

slowcut () {  # name start crop source-length
  #  stretches a short, perfectly still stretch of the take to a full shot.
  #  Used where the only window without a defect is shorter than one shot;
  #  the page is frozen there, so the slow-down is invisible — and it keeps
  #  the cut calm instead of speeding the footage up.
  K=$(python3 -c "print(round($D/$4,6))")
  "$FF" -y -hide_banner -loglevel error -ss "$2" -t "$4" -i "$W/src/rec.mp4" \
    -vf "$3,scale=${SW}:${SH}:flags=lanczos,setsar=1,setpts=PTS*${K},fps=30,format=yuv420p" \
    -an -c:v libx264 -preset medium -crf 16 "$W/scenes/$1.mp4"
}

# 1. nine shots, 1.90 s each — deliberately unhurried, nothing sped up.
#    Two things had to stay out of frame. The dark workbook has number-format
#    bugs on the Dashboard: MONTHS TO GO renders as "$35,00" and the whole
#    SNOWBALL VS AVALANCHE block renders as "3500,0%" / "8662,326617". And the
#    take scrolls that block up the page from 9.8 s on, so a crop that is clean
#    at the first frame of a shot is not clean at its last. Every window below
#    was measured across its full 1.90 s, not on a single still.
cut     s01 0.4   "crop=900:506:0:4"      # Setup — the six debts
cut     s02 2.2   "crop=900:506:0:4"      # Setup — Method dropdown open
cut     s03 29.8  "crop=900:506:0:4"      # Dashboard, Snowball — Jun 2029
cut     s04 32.8  "crop=900:506:0:4"      # Setup — switching the method
cut     s05 8.6   "crop=900:506:0:4"      # Dashboard, Custom — Jul 2029, $8,662
cut     s06 9.8   "crop=760:428:0:196"    # Dashboard — total paid, progress, payoff order
slowcut s07 13.32 "crop=796:448:312:0" 1.10   # Dashboard — balance over time
cut     s08 15.3  "crop=900:506:0:4"      # Debt Tracker — paid so far, remaining, % paid
cut     s09 24.3  "crop=760:428:0:60"     # Debt Tracker — the totals row

# 2. cross-fade the ten shots into one continuous screen
FC=""; PREV="0"
for i in $(seq 2 $N); do
  OFF=$(python3 -c "print(round(($i-1)*($D-$X),3))")
  IN=$((i-1))
  FC+="[$PREV][$IN]xfade=transition=fade:duration=$X:offset=$OFF[x$i]; "
  PREV="x$i"
done
"$FF" -y -hide_banner -loglevel error \
  $(for i in $(seq 1 $N); do printf ' -i %s' "$(printf "$W/scenes/s%02d.mp4" $i)"; done) \
  -filter_complex "${FC}[$PREV]format=yuv420p[v]" -map "[v]" -r 30 \
  -c:v libx264 -preset medium -crf 16 "$W/screen.mp4"

# 3. compose: background + screen + window gloss + captions + tab highlight + progress bar
TOTAL=14.9
INPUTS=(-loop 1 -framerate 30 -t $TOTAL -i "$W/layers/bg.png"
        -i "$W/screen.mp4"
        -loop 1 -framerate 30 -t $TOTAL -i "$W/layers/fg.png"
        -loop 1 -framerate 30 -t $TOTAL -i "$W/layers/bar.png")
for i in $(seq 1 $N); do INPUTS+=(-loop 1 -framerate 30 -t $TOTAL -i "$W/layers/cap$i.png"); done
for i in $(seq 1 $N); do INPUTS+=(-loop 1 -framerate 30 -t $TOTAL -i "$W/layers/pill$i.png"); done

FC2="[0:v]format=rgba[bg];[1:v]format=rgba[scr];[bg][scr]overlay=60:300:format=auto[a];"
FC2+="[2:v]format=rgba[fg];[a][fg]overlay=0:0:format=auto[b];"
# progress bar slides in from the left over the full duration
FC2+="[3:v]format=rgba[pb];[b][pb]overlay=x='-1080+1080*t/${TOTAL}':y=1075:format=auto[c0];"
PREV="c0"
for i in $(seq 1 $N); do
  ST=$(python3 -c "print(round(($i-1)*($D-$X),3))")
  CIN=$(python3 -c "print(round($ST+0.10,3))"); COUT=$(python3 -c "print(round($ST+1.42,3))")
  IDX=$((3+i))
  FC2+="[$IDX:v]format=rgba,fade=in:st=$CIN:d=0.22:alpha=1,fade=out:st=$COUT:d=0.22:alpha=1[k$i];"
  FC2+="[$PREV][k$i]overlay=0:0:format=auto[c$i];"; PREV="c$i"
done
for i in $(seq 1 $N); do
  ST=$(python3 -c "print(round(($i-1)*($D-$X),3))")
  PIN=$(python3 -c "print(round($ST,3))"); POUT=$(python3 -c "print(round($ST+1.62,3))")
  IDX=$((3+$N+i))
  FC2+="[$IDX:v]format=rgba,fade=in:st=$PIN:d=0.16:alpha=1,fade=out:st=$POUT:d=0.16:alpha=1[p$i];"
  FC2+="[$PREV][p$i]overlay=0:0:format=auto[q$i];"; PREV="q$i"
done
FC2+="[$PREV]fade=t=in:st=0:d=0.35:color=0x0A0F1A,fade=t=out:st=14.6:d=0.3:color=0x0A0F1A,format=yuv420p[out]"

"$FF" -y -hide_banner -loglevel error "${INPUTS[@]}" -filter_complex "$FC2" \
  -map "[out]" -t $TOTAL -r 30 -an \
  -c:v libx264 -preset medium -crf 19 -profile:v high -level 4.0 -movflags +faststart "$OUT"

echo "built $OUT"
"$FF" -hide_banner -i "$OUT" 2>&1 | grep -E "Duration|Stream"
