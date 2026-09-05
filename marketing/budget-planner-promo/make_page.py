"""Stitch the whole Budget Planner page out of the recording, then render one
continuous scroll down it.

The listing's whole point is that everything lives on one page, so the video
must not cut the page into pieces. The recording only ever shows one viewport at
a time, so the page is reassembled from a single monotonic scroll pass: each
frame is aligned to the previous one by minimising the difference over the
overlap, and every row is taken from the last viewport that had it near the top
— never from a viewport's bottom edge, which carries the scrollbar and half-
drawn rows.

Usage: WORK=./work python3 make_page.py <recording.mp4> <out.mp4>
"""
import os, subprocess, sys
import numpy as np
from PIL import Image

SRC  = sys.argv[1]
OUT  = sys.argv[2]
WORK = os.environ.get("WORK", os.path.dirname(os.path.abspath(__file__)) + "/work")
FF   = subprocess.run(["python3", "-c", "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())"],
                      capture_output=True, text=True).stdout.strip()

H, W, CUT = 818, 1470, 44          # viewport grid area, page width, dropped bottom edge
# one monotonic scroll pass through the page, in recording time
TIMES = [0.0, 1.6, 2.0, 2.6, 2.8, 3.0, 3.2, 3.6, 3.8, 4.4, 5.2,
         10.8, 11.0, 11.2, 11.6, 12.0, 12.2, 12.4, 12.8, 13.4, 13.8]

FPS   = 30
HOLD_TOP, SCROLL, HOLD_BOT = 2.40, 6.40, 0.92
SW, SH = 960, 540

frames_dir = WORK + "/pagesrc"
os.makedirs(frames_dir, exist_ok=True)
if not os.listdir(frames_dir):
    subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error", "-i", SRC,
                    "-vf", "fps=5", "-q:v", "2", "-frames:v", "100",
                    frames_dir + "/f_%03d.png"], check=True)

def load(t):
    p = f"{frames_dir}/f_{int(round(t*5))+1:03d}.png"
    return np.asarray(Image.open(p).convert("RGB"))[:H, :W]

def refine(a, b):
    """rows of b start this far down inside a"""
    A = a.astype(np.float32).mean(axis=2); B = b.astype(np.float32).mean(axis=2)
    best, bestv = 0, 1e18
    for off in range(0, 131):
        ov = H - off - CUT
        if ov < 250: continue
        v = float(np.abs(A[off:off+ov] - B[:ov]).mean())
        if v < bestv: bestv, best = v, off
    return best

rows, cur, acc = [], load(TIMES[0]), 0
rows.append((0, cur))
for t in TIMES[1:]:
    nxt = load(t)
    rel = refine(cur, nxt)
    if rel == 0:
        continue
    acc += rel
    rows.append((acc, nxt))
    cur = nxt

PAGE = rows[-1][0] + H - 14
page = np.full((PAGE, W, 3), 255, np.uint8)
for start, arr in rows:                       # last writer wins: rows come from near a viewport top
    end = min(PAGE, start + H - CUT)
    page[start:end] = arr[:end-start]
start, arr = rows[-1]
page[start:PAGE] = arr[:PAGE-start]
Image.fromarray(page).save(WORK + "/page.png")
print(f"page {W}x{PAGE} from {len(rows)} viewports")

# ---------------------------------------------------------------- the scroll
view_h = int(round(W * SH / SW))               # the window's own aspect, in page pixels
span   = max(PAGE - view_h, 0)
n_hold, n_scroll, n_bot = (int(round(x*FPS)) for x in (HOLD_TOP, SCROLL, HOLD_BOT))
img = Image.fromarray(page)
clip = WORK + "/scroll"
os.makedirs(clip, exist_ok=True)
for f in os.listdir(clip):
    os.remove(os.path.join(clip, f))

def smooth(u): return u*u*(3-2*u)

i = 0
for k in range(n_hold + n_scroll + n_bot):
    if k < n_hold:            y = 0
    elif k < n_hold+n_scroll: y = span * smooth((k-n_hold) / (n_scroll-1))
    else:                     y = span
    y = int(round(y))
    img.crop((0, y, W, y+view_h)).resize((SW, SH), Image.LANCZOS).save(f"{clip}/s_{i:04d}.png")
    i += 1
subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error", "-framerate", str(FPS),
                "-i", f"{clip}/s_%04d.png", "-c:v", "libx264", "-preset", "medium",
                "-crf", "16", "-pix_fmt", "yuv420p", OUT], check=True)
print(f"scroll clip {i/FPS:.2f}s -> {OUT}  (page span {span}px)")
