"""Listing video, direction A "Noir snowfall": 1080x1080, exactly 14.9 s, 30 fps, no sound.

One continuous night scene. A street lamp flickers on over Ember Square; the camera drifts past
the closing market to the Judges' Tent; a figure in a red bobble hat slips out and walks through
the lamplight (the hat is the only colour), leaving footprints; the camera sinks to the snow
where thousands of other trails appear; end card. Every frame is spoiler-scanned.

    python3 video_noir.py
"""
import math, os, random, subprocess
from PIL import Image, ImageDraw, ImageFilter
import imageio_ffmpeg
import kit
from kit import GREEN, CRAN, PARCH, MUST, font
import case_listing as CL

WW, WH = 3600, 2160          # world (drawn at 2x the video size)
V = 1080
FPS = 30
DURATION = 14.9
N = int(round(DURATION * FPS))      # 447

NIGHT = (0x07, 0x0A, 0x09); COLD = (0x19, 0x28, 0x22)
GROUND_Y = 1400
LAMP_X, LAMP_TOP = 900, 430
TENT_X = 2900
FIG_Y = 1640
WALK_T0, WALK_T1 = 5.2, 9.9          # the figure walks from the tent to beyond the lamp
FIG_X0, FIG_X1 = TENT_X - 20, 260
END = 12.3
WINDOWS = [(180, 1235), (560, 1275), (1320, 1245), (1700, 1270), (2140, 1240), (2480, 1265), (3340, 1250)]

def ease(t):
    t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)

def seg(t, a, b):
    return ease((t - a) / (b - a)) if b > a else float(t >= a)

def lerp(a, b, t):
    return a + (b - a) * t

# ---------------------------------------------------------------- static world
def blur_poly(size, pts, col, alpha, blur):
    g = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(g).polygon(pts, fill=col + (alpha,))
    return g.filter(ImageFilter.GaussianBlur(blur))

class World:
    def __init__(self):
        self.base = self._base()
        self.cones = [self._cone(k / 4) for k in range(5)]          # lamp intensity 0, .25 ... 1
        self.window_glow = self._glow(70, (0xF6, 0xD0, 0x7A), 120)
        self.flap_glow = self._glow(260, (0xF6, 0xD0, 0x7A), 150)
        self.trails = self._trails()
        self.flakes = self._flakes()
        m = Image.radial_gradient("L").resize((V, V)).point(lambda v: int(max(0, v - 60) * 1.25))
        self.vignette = Image.new("RGBA", (V, V), (0, 0, 0, 255)); self.vignette.putalpha(m)
        self.grains = []
        for i in range(6):
            n = Image.effect_noise((V, V), 42 + i).convert("L")
            self.grains.append(Image.merge("RGBA", (n, n, n, Image.new("L", (V, V), 16))))
        self.cover = kit.Pdf(CL.PDF["letter"]).image(0, 560)

    def _base(self):
        im = Image.new("RGBA", (WW, WH)); d = ImageDraw.Draw(im)
        for y in range(WH):
            t = y / WH
            d.line([(0, y), (WW, y)], fill=tuple(int(lerp(a, b, t)) for a, b in zip(NIGHT, COLD)) + (255,))
        mist = Image.new("RGBA", (WW, WH), (0, 0, 0, 0)); md = ImageDraw.Draw(mist)
        for y in (820, 1060, 1250):
            md.rectangle([0, y, WW, y + 70], fill=(0x3A, 0x4A, 0x44, 38))
        im.alpha_composite(mist.filter(ImageFilter.GaussianBlur(40)))
        d = ImageDraw.Draw(im)
        rng = random.Random(4)
        x = -80
        while x < WW:                                     # market stall silhouettes
            w = rng.randint(250, 330); h = rng.randint(220, 300)
            if not (TENT_X - 420 < x < TENT_X + 300) and not (1820 < x < 2080):
                d.rectangle([x, GROUND_Y - h * 0.62, x + w, GROUND_Y], fill=(0x10, 0x18, 0x14))
                d.polygon([(x - 20, GROUND_Y - h * 0.62), (x + w / 2, GROUND_Y - h), (x + w + 20, GROUND_Y - h * 0.62)], fill=(0x10, 0x18, 0x14))
            x += w + rng.randint(40, 90)
        # the Great Fir, unlit
        for i in range(4):
            tw = 330 - i * 70; ty = GROUND_Y - i * 150
            d.polygon([(1950 - tw / 2, ty), (1950 + tw / 2, ty), (1950, ty - 260)], fill=(0x0D, 0x15, 0x11))
        # Judges' Tent: dark stripes, the flap drawn per frame
        tb, th, tw = GROUND_Y + 40, 560, 600
        d.polygon([(TENT_X - tw / 2, tb), (TENT_X, tb - th), (TENT_X + tw / 2, tb)], fill=(0x2B, 0x2A, 0x27))
        for k in range(0, 8, 2):
            x0 = TENT_X - tw / 2 + k * tw / 8
            d.polygon([(x0, tb), (TENT_X, tb - th), (x0 + tw / 8, tb)], fill=(0x3E, 0x1A, 0x20))
        d.polygon([(TENT_X - 70, tb), (TENT_X, tb - 230), (TENT_X + 70, tb)], fill=(0x14, 0x12, 0x10))
        # snowy ground
        pts = [(0, WH)] + [(x, GROUND_Y + math.sin(x / 300) * 18) for x in range(0, WW + 1, 30)] + [(WW, WH)]
        d.polygon(pts, fill=(0x26, 0x2D, 0x2A))
        # lamp post
        d.rectangle([LAMP_X - 14, LAMP_TOP, LAMP_X + 14, 1660], fill=(0x04, 0x05, 0x05))
        d.polygon([(LAMP_X - 70, LAMP_TOP), (LAMP_X + 70, LAMP_TOP), (LAMP_X + 40, LAMP_TOP - 60), (LAMP_X - 40, LAMP_TOP - 60)], fill=(0x04, 0x05, 0x05))
        d.rectangle([LAMP_X - 44, 1640, LAMP_X + 44, 1670], fill=(0x04, 0x05, 0x05))
        return im

    def _cone(self, k):
        im = Image.new("RGBA", (WW, WH), (0, 0, 0, 0))
        if k == 0:
            return im
        a = lambda v: int(v * k)
        im.alpha_composite(blur_poly((WW, WH), [(LAMP_X - 40, LAMP_TOP + 10), (LAMP_X + 40, LAMP_TOP + 10), (LAMP_X + 640, 1700), (LAMP_X - 560, 1700)], (0xFF, 0xE6, 0xB5), a(58), 34))
        pool = Image.new("RGBA", (WW, WH), (0, 0, 0, 0))
        ImageDraw.Draw(pool).ellipse([LAMP_X - 700, 1520, LAMP_X + 760, 1860], fill=(0xE9, 0xE4, 0xD8, a(150)))
        im.alpha_composite(pool.filter(ImageFilter.GaussianBlur(60)))
        bulb = Image.new("RGBA", (WW, WH), (0, 0, 0, 0))
        ImageDraw.Draw(bulb).ellipse([LAMP_X - 110, LAMP_TOP - 100, LAMP_X + 110, LAMP_TOP + 120], fill=(0xFF, 0xE2, 0xA6, a(230)))
        im.alpha_composite(bulb.filter(ImageFilter.GaussianBlur(40)))
        return im

    def _glow(self, r, col, a):
        g = Image.new("RGBA", (r * 4, r * 4), (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse([r, r, r * 3, r * 3], fill=col + (a,))
        return g.filter(ImageFilter.GaussianBlur(r * 0.5))

    def _trails(self):
        """Faint footprint trails of the other visitors, revealed at the end."""
        rng = random.Random(11); out = []
        for _ in range(34):
            x, y = rng.uniform(-200, WW + 200), rng.uniform(1480, 2150)
            ang = rng.uniform(-0.5, 0.5) + (math.pi if rng.random() < 0.5 else 0)
            steps = []
            for k in range(40):
                x += math.cos(ang) * 58; y += math.sin(ang) * 20 + rng.uniform(-6, 6)
                side = 1 if k % 2 else -1
                steps.append((x + math.sin(ang) * 14 * side, y + math.cos(ang) * 8 * side))
            out.append((rng.uniform(0, 0.8), steps))
        return out

    def _flakes(self):
        rng = random.Random(7)
        return [(rng.random(), rng.random(), rng.choice([0.35, 0.6, 1.0]), rng.uniform(3, 9), rng.uniform(0, 6.28)) for _ in range(300)]

# ---------------------------------------------------------------- dynamic pieces
def lamp_level(t):
    seq = [0, 0, 0.5, 0.1, 0.75, 0.3, 1.0]
    if t < 0.9:
        return seq[min(len(seq) - 1, int(t / 0.13))]
    if 8.15 < t < 8.45:                   # it flickers as the figure passes beneath
        return 0.5 if int(t * 20) % 2 else 1.0
    return 1.0

def fig_x(t):
    return lerp(FIG_X0, FIG_X1, (t - WALK_T0) / (WALK_T1 - WALK_T0))

def camera(t):
    """World centre (x, y) and zoom."""
    if t < 2.0:
        cx = 1080
    elif t < 5.0:
        cx = lerp(1080, 2560, seg(t, 2.0, 5.0))
    elif t < WALK_T0 + 0.6:
        cx = 2560
    else:
        follow = max(1080, min(2560, fig_x(t) + 260))
        cx = follow
    z, cy = 1.0, 1080
    if t >= 9.9:
        e = seg(t, 9.9, 11.4)
        z, cy, cx = lerp(1.0, 1.32, e), lerp(1080, 1520, e), lerp(cx, 1250, e)
    return cx, cy, z

def draw_figure(d, fx, fy, s, phase, hat):
    body = (0x03, 0x04, 0x04)
    bob = abs(math.sin(phase)) * 8 * s
    fy = fy - bob
    step = math.sin(phase) * 40 * s
    d.polygon([(fx - 70 * s, fy - 330 * s), (fx + 70 * s, fy - 330 * s), (fx + 118 * s, fy), (fx - 118 * s, fy)], fill=body)
    d.ellipse([fx - 62 * s, fy - 450 * s, fx + 62 * s, fy - 320 * s], fill=body)
    d.chord([fx - 72 * s, fy - 500 * s, fx + 72 * s, fy - 350 * s], 180, 360, fill=hat)
    d.rectangle([fx - 72 * s, fy - 432 * s, fx + 72 * s, fy - 408 * s], fill=tuple(int(c * 0.7) for c in hat))
    d.ellipse([fx - 32 * s, fy - 548 * s, fx + 32 * s, fy - 484 * s], fill=hat)
    d.rectangle([fx - 90 * s + step, fy, fx - 20 * s + step, fy + 34 * s + bob], fill=body)
    d.rectangle([fx + 20 * s - step, fy, fx + 90 * s - step, fy + 34 * s + bob], fill=body)

def caption_layer(text, y, size, col, alpha, name="display", chars=None, anchor="ma", x=None):
    lay = kit.Frame(V, V, (0, 0, 0)); lay.img = Image.new("RGBA", (V, V), (0, 0, 0, 0))
    shown = text if chars is None else text[:chars]
    if shown:
        f = kit.fit_font(lay, text, name, size, 980)
        lay.text((V / 2 if x is None else x, y), shown, f, col, anchor=anchor)
    lay.img.putalpha(lay.img.split()[3].point(lambda v: int(v * alpha)))
    return lay

def render(Wd, t, sources):
    cx, cy, z = camera(t)
    size = int(WH / z)
    x0 = int(min(max(cx - size / 2, 0), WW - size)); y0 = int(min(max(cy - size / 2, 0), WH - size))
    box = (x0, y0, x0 + size, y0 + size)
    c = Wd.base.crop(box)
    d = ImageDraw.Draw(c)
    # market windows switch off one by one as the market closes
    for i, (wx, wy) in enumerate(WINDOWS):
        if t < 1.2 + i * 0.55 and x0 - 200 < wx < x0 + size + 200:
            g = Wd.window_glow
            c.alpha_composite(g, (int(wx - x0 - g.width / 2), int(wy - y0 - g.height / 2)))
            d.rectangle([wx - x0 - 30, wy - y0 - 22, wx - x0 + 30, wy - y0 + 22], fill=(0xC8, 0xA2, 0x55))
    # the tent flap glows while someone is inside, dims after they leave
    fl = 1.0 if t < WALK_T0 else max(0.25, 1 - (t - WALK_T0) / 1.5)
    if x0 - 400 < TENT_X < x0 + size + 400:
        g = Wd.flap_glow.copy(); g.putalpha(g.split()[3].point(lambda v: int(v * fl)))
        c.alpha_composite(g, (int(TENT_X - x0 - g.width / 2), int(GROUND_Y - 110 - y0 - g.height / 2)))
        tb = GROUND_Y + 40
        open_w = 70 + 40 * seg(t, WALK_T0 - 0.4, WALK_T0) * (1 - seg(t, WALK_T0 + 0.6, WALK_T0 + 1.2))
        col = tuple(int(lerp(0x14, v, fl)) for v in (0xF6, 0xD0, 0x7A))
        d.polygon([(TENT_X - open_w - x0, tb - y0), (TENT_X - x0, tb - 230 - y0), (TENT_X + open_w - x0, tb - y0)], fill=col)
    # lamp light
    lv = lamp_level(t)
    cone = Wd.cones[int(round(lv * 4))].crop(box)
    c.alpha_composite(cone)
    # other visitors' trails (the 6,000), revealed at the end
    if t >= 10.3:
        k = seg(t, 10.3, 11.8)
        tr = Image.new("RGBA", c.size, (0, 0, 0, 0)); td = ImageDraw.Draw(tr)
        for start, steps in Wd.trails:
            n = int(len(steps) * max(0.0, min(1.0, (k - start) / 0.5 + k)))
            for (px, py) in steps[:n]:
                td.ellipse([px - x0 - 12, py - y0 - 5, px - x0 + 12, py - y0 + 5], fill=(0x0C, 0x10, 0x0F, 95))
        c.alpha_composite(tr)
    # the figure's own footprints
    if t >= WALK_T0:
        k = 0
        tt = WALK_T0
        while tt <= min(t, WALK_T1):
            px = fig_x(tt); py = FIG_Y + 40 + (18 if k % 2 else -4)
            d.ellipse([px - x0 - 20, py - y0 - 9, px - x0 + 20, py - y0 + 9], fill=(0x12, 0x16, 0x15))
            k += 1; tt += 0.22
    # the figure and its long shadow
    if WALK_T0 <= t <= WALK_T1:
        fx = fig_x(t); dx = fx - LAMP_X
        light = max(0.28, 1 - abs(dx) / 900) * (lv if abs(dx) < 900 else 1)
        if abs(dx) < 1300:
            L = 220 + abs(dx) * 0.7; sgn = 1 if dx >= 0 else -1
            a = int(170 * lv * max(0, 1 - abs(dx) / 1300))
            sh = Image.new("RGBA", (1800, 500), (0, 0, 0, 0))
            ImageDraw.Draw(sh).polygon([(900 - 100, 60), (900 + 100, 60), (900 + sgn * L + 60, 300), (900 + sgn * L - 60, 330)], fill=(0, 0, 0, a))
            sh = sh.filter(ImageFilter.GaussianBlur(10))
            c.alpha_composite(sh, (int(fx - x0 - 900), int(FIG_Y - y0 - 40)))
        hat = tuple(int(lerp(0x2A, v, light)) for v in CRAN)
        ph = (t - WALK_T0) * 2 * math.pi * 1.4
        draw_figure(d, fx - x0, FIG_Y - y0, 1.0, ph, hat)
    # snow, three depths; bright inside the lamp cone
    snow = Image.new("RGBA", c.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(snow)
    for (u, v, depth, r, ph) in Wd.flakes:
        wx = (u * size * 1.2 - (cx - 1080) * depth * 0.6 + math.sin(t * 0.9 + ph) * 30) % (size * 1.2) - size * 0.1
        wy = (v * size + t * 170 * depth) % size
        worldx, worldy = wx + x0, wy + y0
        inside = lv > 0 and LAMP_TOP < worldy < 1700 and abs(worldx - LAMP_X) < 40 + (worldy - LAMP_TOP) * 0.49
        a = (230 if inside else 70) * (0.5 + depth / 2)
        col = (0xFF, 0xF6, 0xE3) if inside else (0xB8, 0xC4, 0xBE)
        rr = r * depth * 1.6
        sd.ellipse([wx - rr, wy - rr, wx + rr, wy + rr], fill=col + (int(a),))
    c.alpha_composite(snow)
    frame = c.resize((V, V), Image.LANCZOS)
    frame.alpha_composite(Wd.vignette)
    frame.alpha_composite(Wd.grains[int(t * 12) % len(Wd.grains)])
    # captions
    def put(lay):
        frame.alpha_composite(lay.img); sources.extend(lay.sources)
    if 0.7 <= t <= 4.8:
        a = 1 - seg(t, 4.4, 4.8)
        put(caption_layer("Ember Square. 23 December.", 70, 44, (0xC9, 0xC2, 0xB2), a, "display-italic",
                          chars=int((t - 0.7) * 22), anchor="la", x=70))
    if 5.5 <= t <= 7.9:
        a = min(seg(t, 5.5, 5.8), 1 - seg(t, 7.6, 7.9))
        put(caption_layer("20:05. Someone slips out of the Judges’ Tent.", 930, 50, PARCH, a))
    if 8.1 <= t <= 9.9:
        a = min(seg(t, 8.1, 8.4), 1 - seg(t, 9.6, 9.9))
        put(caption_layer("No one saw a face. Only a red bobble hat.", 930, 50, PARCH, a))
    if 10.2 <= t <= END + 0.2:
        a = seg(t, 10.2, 10.5) * (1 - seg(t, END - 0.1, END + 0.2))
        put(caption_layer("6,000 visitors.", 360, 96, PARCH, a))
        if t >= 10.9:
            put(caption_layer("One of them is a killer.", 490, 70, (0xE0, 0x6B, 0x78), a * seg(t, 10.9, 11.2)))
    # end card
    if t >= END:
        e = seg(t, END, END + 0.5)
        frame.alpha_composite(Image.new("RGBA", (V, V), (0x07, 0x0A, 0x09, int(236 * e))))
        if e > 0.25:
            cov = Wd.cover
            yy = int(560 + (1 - seg(t, END + 0.2, END + 0.8)) * 380)
            frame.alpha_composite(cov.img, (70, yy - cov.img.height // 2))
            sources.append(("pdf", cov.source, cov.text))
            q = seg(t, END + 0.5, END + 1.0)
            lay = kit.Frame(V, V, (0, 0, 0)); lay.img = Image.new("RGBA", (V, V), (0, 0, 0, 0))
            lay.text((770, 230), "Snowfall at\nEmber Square", font("display", 74), PARCH, anchor="ma", align="center")
            lay.text((770, 450), "Can you find the killer?", font("display-italic", 50), (0xE0, 0x6B, 0x78), anchor="ma")
            kit.pill(lay, (770, 600), "Printable + iPad", font("black", 46), MUST, GREEN)
            lay.text((770, 690), "6,000 suspects · 18 clues", font("bold", 40), PARCH, anchor="ma")
            lay.text((770, 930), CL.C.BRAND, font("display", 50), PARCH, anchor="ma")
            lay.img.putalpha(lay.img.split()[3].point(lambda v: int(v * q)))
            put(lay)
    return frame

def build(outpath, poster=None):
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    Wd = World()
    bad = CL.forbidden()
    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{V}x{V}", "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
           "-crf", "23", "-preset", "slow", "-movflags", "+faststart", "-frames:v", str(N), outpath]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    hits_total = 0; hit_frames = 0
    for i in range(N):
        t = i / FPS
        sources = []
        img = render(Wd, t, sources)
        hits = kit.spoiler_scan(sources, bad)
        hits_total += len(hits); hit_frames += bool(hits)
        if poster and i == int(8.0 * FPS):
            img.convert("RGB").save(poster)
        proc.stdin.write(img.convert("RGB").tobytes())
    proc.stdin.close(); proc.wait()
    return N, hits_total, hit_frames

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    vid = os.path.join(here, "..", "video")
    n, hits, hf = build(os.path.join(vid, f"{CL.SLUG}_noir-video_1080.mp4"),
                        os.path.join(vid, f"{CL.SLUG}_noir-video_poster.png"))
    print(n, "frames; spoiler hits:", hits, "in", hf, "frames")
