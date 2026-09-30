"""1080x1080 silent listing video (about 14.5 s, 30 fps), built frame by frame from real PDF pages.
Structure: hook -> promise -> documents -> proof (marker, map circle, notebook ticks) -> finale."""
import math, os, random, subprocess
from PIL import Image, ImageDraw
import imageio_ffmpeg
import kit
from kit import GREEN, CRAN, PARCH, MUST, INK, PARCH_DARK, font
import case_listing as CL
import mockups as M

V = 1080
FPS = 30
FADE = 0.25

def ease(t):
    t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3

class Snow:
    """Falling snow that moves smoothly between frames."""
    def __init__(self, n, seed):
        rng = random.Random(seed)
        self.f = [(rng.uniform(0, V), rng.uniform(0, V), rng.uniform(3, 11), rng.uniform(25, 70), rng.uniform(60, 190))
                  for _ in range(n)]
    def draw(self, frame, t):
        layer = Image.new("RGBA", (V, V), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
        for x, y, r, speed, a in self.f:
            yy = (y + speed * t) % (V + 40) - 20
            xx = x + math.sin(t * 0.8 + y) * 12
            kit.snowflake(d, xx, yy, r, PARCH + (int(a),), max(1, int(r / 5)))
        frame.img.alpha_composite(layer)

def caption(f, text, y=48, col=GREEN, size=78, alpha=1.0):
    fnt = kit.fit_font(f, text, "display", size, 980)
    if alpha >= 1:
        f.text((V / 2, y), text, fnt, col, anchor="ma", align="center")
        return
    layer = kit.Frame(V, V, (0, 0, 0)); layer.img = Image.new("RGBA", (V, V), (0, 0, 0, 0))
    layer.text((V / 2, y), text, fnt, col, anchor="ma", align="center")
    r, g, b, a = layer.img.split(); a = a.point(lambda v: int(v * alpha))
    layer.img.putalpha(a); f.img.alpha_composite(layer.img); f.sources += layer.sources

# ---------------------------------------------------------------- scenes: fn(A, t_local) -> Frame
def s_hook(A, t):
    f = kit.Frame(V, V, GREEN); A.snow.draw(f, t); kit.string_lights(f, 10, 36, 14)
    p = ease((t - 0.15) / 0.6)
    fnt = font("display", 118)
    layer = kit.Frame(V, V, (0, 0, 0)); layer.img = Image.new("RGBA", (V, V), (0, 0, 0, 0))
    layer.text((V / 2, 330 + (1 - p) * 60), "Love a good\nwhodunit?", fnt, PARCH, anchor="ma", align="center")
    a = layer.img.split()[3].point(lambda v: int(v * p)); layer.img.putalpha(a)
    f.img.alpha_composite(layer.img); f.sources += layer.sources
    if t > 1.0:
        kit.pill(f, (V / 2, 760), "A cozy Christmas case", font("black", 50), MUST, GREEN)
    return f

def s_promise(A, t):
    f = kit.Frame(V, V, GREEN); A.snow.draw(f, t + 2.2)
    lines = [("6,000 visitors", PARCH), ("18 clues", PARCH), ("1 killer", MUST)]
    for i, (s, col) in enumerate(lines):
        p = ease((t - 0.1 - i * 0.45) / 0.35)
        if p <= 0:
            continue
        size = int(112 * (0.7 + 0.3 * p))
        f.text((V / 2, 250 + i * 190), s, font("black", size), col, anchor="ma")
    if t > 1.5:
        kit.pen_circle(f, V / 2, 250 + 2 * 190 + 60, 250, 90, CRAN, 9, 7, ease((t - 1.5) / 0.4))
    return f

def s_documents(A, t):
    f = kit.Frame(V, V, PARCH); M.paper_bg_small(f)
    caption(f, "6 case documents", 36)
    docs = ["map", "receipt", "weather", "statements"]
    angles = [-14, -5, 5, 14]
    for i, (k, a) in enumerate(zip(docs, angles)):
        p = ease((t - i * 0.35) / 0.5)
        if p <= 0:
            continue
        pg = A.pages[k]
        R = 700; cx = V / 2 + R * math.sin(math.radians(a)); cy = 1400 - R * math.cos(math.radians(a))
        f.paste_page(pg, cx, cy + (1 - p) * 700, angle=-a)
    return f

def s_log(A, t):
    f = kit.Frame(V, V, PARCH); M.paper_bg_small(f)
    caption(f, "Cross out the innocent", 36)
    pg = A.L.image(A.log_page, A.log_h, clip=A.log_clip)
    M.strike_rows(pg, A.log_rows, M.holly_lane, progress=ease((t - 0.2) / 1.7), seed=3)
    f.paste_page(pg, V / 2, 150 + pg.img.height / 2, shadow=True)
    return f

def s_map(A, t):
    f = kit.Frame(V, V, PARCH); M.paper_bg_small(f)
    caption(f, "Circle the scene", 36)
    pg = A.L.image(A.p["map"], A.map_h, clip=A.map_clip)
    M.circle_tent(A.L, pg, A.p["map"], progress=ease((t - 0.25) / 1.1))
    f.paste_page(pg, V / 2, 160 + pg.img.height / 2)
    return f

def s_notebook(A, t):
    f = kit.Frame(V, V, GREEN); A.snow.draw(f, t + 9)
    caption(f, "Tick off every clue", 36, PARCH)
    pg = A.L.image(A.p["notebook"], A.nb_h, clip=A.nb_clip)
    M.tick_notebook(A.L, pg, A.p["notebook"], [str(i) for i in range(1, 13)], progress=ease((t - 0.1) / 1.5))
    f.paste_page(pg, V / 2, 160 + pg.img.height / 2)
    return f

def s_final(A, t):
    f = kit.Frame(V, V, GREEN); A.snow.draw(f, t + 12); kit.string_lights(f, 8, 34, 14)
    p = ease(t / 0.5)
    f.paste_page(A.cover, 300, 580 + (1 - p) * 40, angle=3)
    f.text((800, 250), "Snowfall at\nEmber Square", font("display", 70), PARCH, anchor="ma", align="center")
    f.text((800, 470), "Find the killer", font("black", 56), MUST, anchor="ma")
    if t > 0.5:
        kit.pill(f, (800, 640), "Printable + iPad", font("black", 50), MUST, GREEN)
    if t > 0.9:
        f.text((800, 760), "1–4 players · 90–150 min", font("bold", 40), PARCH, anchor="ma")
    f.text((800, 960), CL.C.BRAND, font("display", 48), PARCH, anchor="ma")
    return f

SCENES = [("hook", s_hook, 2.2), ("promise", s_promise, 2.0), ("documents", s_documents, 2.4),
          ("log", s_log, 2.2), ("map", s_map, 1.8), ("notebook", s_notebook, 1.8), ("final", s_final, 2.2)]

class VAssets:
    def __init__(self):
        base = M.Assets()
        self.L, self.p, self.log_page, self.bad = base.L, base.p, base.log_page, base.bad
        self.snow = Snow(60, 2)
        self.pages = {k: self.L.image(self.p[k], 660) for k in ("map", "receipt", "weather", "statements")}
        rows = CL.log_rows(self.L, self.log_page)
        self.log_rows = rows[:34]
        top = rows[0][0] - 20; bottom = rows[33][1] + 2
        self.log_clip = (40, top, 572, bottom)
        self.log_h = int((bottom - top) * 1000 / 532)
        self.map_clip = (60, 170, 560, 640)
        self.map_h = int(470 * 980 / 500)
        self.nb_clip = (44, 120, 568, 402)
        self.nb_h = int(282 * 1000 / 524)
        self.cover = self.L.image(0, 700)

def build(outpath):
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    A = VAssets()
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [ff, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{V}x{V}",
           "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
           "-preset", "medium", "-movflags", "+faststart", outpath]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    frames_report = []
    total = sum(d for _, _, d in SCENES)
    n = int(round(total * FPS))
    starts = []; acc = 0
    for name, fn, d in SCENES:
        starts.append(acc); acc += d
    for i in range(n):
        t = i / FPS
        k = max(j for j, s in enumerate(starts) if s <= t + 1e-9)
        name, fn, d = SCENES[k]
        fr = fn(A, t - starts[k])
        sources = list(fr.sources)
        # cross-fade into the next scene during the last FADE seconds
        if k + 1 < len(SCENES) and t > starts[k] + d - FADE:
            a = (t - (starts[k] + d - FADE)) / FADE
            nxt = SCENES[k + 1][1](A, 0.0)
            fr.img = Image.blend(fr.img, nxt.img, a)
            sources += nxt.sources
        hits = kit.spoiler_scan(sources, A.bad)
        frames_report.append(dict(frame=i, scene=name, hits=hits, n_sources=len(sources)))
        proc.stdin.write(fr.img.convert("RGB").tobytes())
    proc.stdin.close(); proc.wait()
    return frames_report, n, total
