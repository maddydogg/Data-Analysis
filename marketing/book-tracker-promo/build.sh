#!/usr/bin/env bash
# Build the 14.9 s Etsy listing video from the raw screen recording.
#   usage: build.sh <raw-recording> <work-dir> <output.mp4>
set -euo pipefail

RAW="${1:?raw recording}"
W="${2:?work dir}"
OUT="${3:?output file}"
FF="$(python3 -c 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())')"
HERE="$(cd "$(dirname "$0")" && pwd)"

mkdir -p "$W/src" "$W/scenes" "$W/layers"

# 0. normalise the Chrome .webm (variable frame rate, odd width, no duration header)
if [ ! -f "$W/src/rec.mp4" ]; then
  "$FF" -y -hide_banner -loglevel error -fflags +genpts -i "$RAW" \
    -vf "crop=1918:916:0:0" -r 30 -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p "$W/src/rec.mp4"
fi

# 1. design layers (background, laptop mockup, badge, captions)
python3 "$HERE/make_layers.py" "$W/layers" "$W/fonts"

SCREEN_W=888; SCREEN_H=500

cut () { # name  start  duration  filter
  "$FF" -y -hide_banner -loglevel error -ss "$2" -t "$3" -i "$W/src/rec.mp4" \
    -vf "$4,setsar=1,format=yuv420p" -an -r 30 -c:v libx264 -preset medium -crf 16 "$W/scenes/$1.mp4"
}

# 2. the five shots — each cropped to the part of the sheet that sells the tab
cut s1 5.2  3.4 "crop=1560:878:48:28,scale=${SCREEN_W}:${SCREEN_H}:flags=lanczos"
cut s2 41.8 3.4 "crop=1180:664:55:58,scale=${SCREEN_W}:${SCREEN_H}:flags=lanczos"
cut s3 23.5 3.4 "crop=700:394:110:'45+(285*t/3.4)',scale=${SCREEN_W}:${SCREEN_H}:flags=lanczos"
cut s4 15.7 3.4 "crop=860:870:55:30,scale=-2:${SCREEN_H}:flags=lanczos,pad=${SCREEN_W}:${SCREEN_H}:44:0:white"
cut s5 0.5  3.3 "crop=1520:855:55:60,scale=${SCREEN_W}:${SCREEN_H}:flags=lanczos"

# 3. cross-fade the shots into one continuous screen recording
"$FF" -y -hide_banner -loglevel error \
  -i "$W/scenes/s1.mp4" -i "$W/scenes/s2.mp4" -i "$W/scenes/s3.mp4" \
  -i "$W/scenes/s4.mp4" -i "$W/scenes/s5.mp4" \
  -filter_complex "\
    [0][1]xfade=transition=fade:duration=0.5:offset=2.9[a]; \
    [a][2]xfade=transition=fade:duration=0.5:offset=5.8[b]; \
    [b][3]xfade=transition=fade:duration=0.5:offset=8.7[c]; \
    [c][4]xfade=transition=fade:duration=0.5:offset=11.6,format=yuv420p[v]" \
  -map "[v]" -r 30 -c:v libx264 -preset medium -crf 16 "$W/screen.mp4"

# 4. compose: background + screen + bezel/badge overlay + timed captions
"$FF" -y -hide_banner -loglevel error \
  -loop 1 -framerate 30 -t 14.9 -i "$W/layers/bg.png" \
  -i "$W/screen.mp4" \
  -loop 1 -framerate 30 -t 14.9 -i "$W/layers/fg.png" \
  -loop 1 -framerate 30 -t 14.9 -i "$W/layers/cap1.png" \
  -loop 1 -framerate 30 -t 14.9 -i "$W/layers/cap2.png" \
  -loop 1 -framerate 30 -t 14.9 -i "$W/layers/cap3.png" \
  -loop 1 -framerate 30 -t 14.9 -i "$W/layers/cap4.png" \
  -loop 1 -framerate 30 -t 14.9 -i "$W/layers/cap5.png" \
  -filter_complex "\
    [0:v]format=rgba[bg]; \
    [1:v]format=rgba[scr]; \
    [bg][scr]overlay=96:318:format=auto[s1]; \
    [2:v]format=rgba[fg]; [s1][fg]overlay=0:0:format=auto[s2]; \
    [3:v]format=rgba,fade=in:st=0.35:d=0.3:alpha=1,fade=out:st=2.55:d=0.3:alpha=1[k1]; \
    [4:v]format=rgba,fade=in:st=3.35:d=0.3:alpha=1,fade=out:st=5.55:d=0.3:alpha=1[k2]; \
    [5:v]format=rgba,fade=in:st=6.25:d=0.3:alpha=1,fade=out:st=8.45:d=0.3:alpha=1[k3]; \
    [6:v]format=rgba,fade=in:st=9.15:d=0.3:alpha=1,fade=out:st=11.35:d=0.3:alpha=1[k4]; \
    [7:v]format=rgba,fade=in:st=12.05:d=0.3:alpha=1,fade=out:st=14.5:d=0.3:alpha=1[k5]; \
    [s2][k1]overlay=0:0:format=auto[c1]; \
    [c1][k2]overlay=0:0:format=auto[c2]; \
    [c2][k3]overlay=0:0:format=auto[c3]; \
    [c3][k4]overlay=0:0:format=auto[c4]; \
    [c4][k5]overlay=0:0:format=auto[c5]; \
    [c5]fade=t=in:st=0:d=0.4:color=white,fade=t=out:st=14.55:d=0.35:color=white,format=yuv420p[out]" \
  -map "[out]" -t 14.9 -r 30 -an \
  -c:v libx264 -preset medium -crf 19 -profile:v high -level 4.0 -movflags +faststart "$OUT"

echo "built $OUT"
"$FF" -hide_banner -i "$OUT" 2>&1 | grep -E "Duration|Stream"
