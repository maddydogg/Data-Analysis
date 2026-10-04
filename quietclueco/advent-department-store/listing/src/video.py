"""Two listing videos for The Windows at Quillon's, 1080 x 1080, 30 fps, no sound, drawn with code.

trailer       13.5 s  a film-style teaser: the snowy city, the store's windows lighting one by one, the
                      striped cup, the Grand Window, the brass magpie, the cover as the end card.
presentation  14.0 s  the product: the calendar of 24 windows, Day 1, Day 2 (the register being crossed
                      out), Day 3, envelopes and the iPad calendar, the cover.

Both share an anime-noir film look (letterbox, grain, light flicker, slow push-ins). Every frame is a
kit.Frame, so the spoiler check reads every caption and every PDF region shown; only Windows 1-3 and
the set-up pages ever appear.

    python3 video.py
"""
import math, os, random, subprocess
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import imageio_ffmpeg
import kit
import cal_listing as CL
from cal_listing import art, COVER
import mockups as M

V, FPS, BAR = 1080, 30, 84
HERE = os.path.dirname(os.path.abspath(__file__))
VID = os.path.join(CL.CASE, "listing", "video")

def ease(x):
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)

def seg(t, a, b):
    return max(0.0, min(1.0, (t - a) / (b - a)))

# ---------------------------------------------------------------- shared look
class Look:
    def __init__(self, seed=5):
        rng = random.Random(seed)
        self.flakes = [(rng.uniform(0, V * 1.3), rng.uniform(0, V), rng.uniform(1.2, 4.2), rng.uniform(40, 120))
                       for _ in range(260)]
        self.grain = []
        for k in range(6):
            n = Image.effect_noise((V, V), 70).convert("L").point(lambda v: 128 + (v - 128) // 3)
            self.grain.append(n)
        m = Image.new("L", (V, V), 0)
        ImageDraw.Draw(m).ellipse([-V * 0.2, -V * 0.2, V * 1.2, V * 1.2], fill=255)
        self.vmask = m.filter(ImageFilter.GaussianBlur(V * 0.16))

    def snow(self, img, t, alpha=170, scale=1.0):
        L = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        for x0, y0, r, sp in self.flakes:
            y = (y0 + sp * t * scale) % V; x = (x0 - sp * t * 0.55 * scale) % (V * 1.3) - V * 0.15
            d.ellipse([x - r, y - r, x + r, y + r], fill=kit.SNOW + (int(alpha * (r / 4.2)),))
        img.alpha_composite(L)

    def film(self, img, i, cuts=(), t=0.0):
        im = img.convert("RGB")
        fl = 1.0 + 0.025 * math.sin(i * 1.7) + 0.015 * math.sin(i * 0.31)
        for c in cuts:                      # a short bright flash at every cut
            if 0 <= t - c < 0.07:
                fl += 0.18
        im = ImageEnhance.Brightness(im).enhance(fl)
        dark = Image.new("RGB", im.size, kit.NIGHT0)
        im = Image.composite(im, Image.blend(im, dark, 0.5), self.vmask)
        g = self.grain[i % len(self.grain)]
        from PIL import ImageChops
        im = ImageChops.overlay(im, Image.merge("RGB", (g, g, g)))
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, V, BAR], fill=(0, 0, 0)); d.rectangle([0, V - BAR, V, V], fill=(0, 0, 0))
        return im

def caption(f, text, alpha=1.0, y=None, size=58, col=None):
    if alpha <= 0:
        return
    y = y or V - BAR - 64
    L = Image.new("RGBA", f.img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    fnt = kit.fit_font(f, text, "display", size, V - 100)
    c = col or kit.SNOW
    tw = d.textlength(text, font=fnt)
    d.rounded_rectangle([V / 2 - tw / 2 - 28, y - size * 0.62, V / 2 + tw / 2 + 28, y + size * 0.62], radius=12,
                        fill=kit.NIGHT0 + (int(200 * alpha),))
    d.text((V / 2, y), text, font=fnt, fill=c + (int(255 * alpha),), anchor="mm")
    f.img.alpha_composite(L); f.note("drawn", "caption", text)

def cover_frame(f, A, a):
    im = A.cover.copy()
    f.img = Image.blend(f.img.convert("RGB"), im, a).convert("RGBA")
    for s in A.cover_text:
        f.note("drawn", "cover", s)

def push(im, t, z0=1.0, z1=1.12, cx=0.5, cy=0.5):
    """Slow push-in on an image to fill V x V."""
    z = z0 + (z1 - z0) * t
    w, h = im.size; s = max(V / w, V / h) * z
    rim = im.resize((int(w * s), int(h * s)), Image.BILINEAR)
    x = int((rim.width - V) * cx); y = int((rim.height - V) * cy)
    return rim.crop((x, y, x + V, y + V)).convert("RGBA")

# ---------------------------------------------------------------- assets
class Assets:
    def __init__(self):
        self.look = Look()
        self.M = M.Assets(); L, I, p, ip = self.M.L, self.M.I, self.M.p, self.M.ip
        rec = []
        self.cover = COVER.cover(V, V, badges=True, record=rec.append)
        self.cover_text = rec
        cv = art.Canvas(V, V, ss=1); art.sky(cv); art.skyline(cv, V * 0.78, seed=3, lit=0.12, height=(0.2, 0.6))
        art.ground(cv, V * 0.78); art.lamp(cv, V * 0.2, V * 0.9, V * 0.55); art.lamp(cv, V * 0.82, V * 0.9, V * 0.55)
        self.city = cv.finish(grain=0, vignette=0)
        self.store = [art.storefront(V, V, seed=7, windows=5, lit=list(range(k)), figure_at=0.5, snow_n=1, grain=0)
                      for k in range(6)]
        self.cup = art.scene(12, 1600, 1000, grain=0)
        self.grand = art.scene(24, 1600, 1000, grain=0)
        # the brass magpie on a dark coat collar
        cv = art.Canvas(V, V, ss=1); art.sky(cv, art.NIGHT0, art.NIGHT1)
        cv.d.polygon(cv.P([(0, V), (V * 0.15, V * 0.25), (V * 0.5, V * 0.62), (V * 0.86, V * 0.2), (V, V)]), fill=art.INK)
        cv.d.polygon(cv.P([(V * 0.15, V * 0.25), (V * 0.38, V * 0.2), (V * 0.5, V * 0.62)]), fill=art.INK2)   # lapel
        cv.d.polygon(cv.P([(V * 0.86, V * 0.2), (V * 0.62, V * 0.18), (V * 0.5, V * 0.62)]), fill=art.INK2)
        art.o_brooch(cv, V * 0.31, V * 0.42, V * 0.22)
        self.brooch = cv.finish(grain=0, vignette=0)
        # pages (Windows 1-3 and set-up pages only)
        self.cal = L.image(p["calendar"], 900)
        self.w1 = L.image(p["w1"], 880); self.letter = L.image(p["w1letter"], 860)
        self.log = L.image(self.M.log_page, 1000); self.log_rows = CL.log_rows(L, self.M.log_page)
        self.w3 = L.image(p["w3"], 900)
        self.ipadcal = I.image(ip["calendar"], 700)
        self.env = L.image(p["envelope"], 620)

def frame(bg=None):
    f = kit.Frame(V, V, kit.NIGHT0)
    if bg is not None:
        f.img = bg.copy() if bg.mode == "RGBA" else bg.convert("RGBA")
    return f

def table_bg(A, t):
    f = M.night_bg(9, glow=(0.5, 0.5))
    im = f.img.resize((V, V), Image.BILINEAR)
    g = frame(im); A.look.snow(g.img, t, alpha=110, scale=0.6)
    return g

# ---------------------------------------------------------------- trailer
TR = dict(N=405, cuts=[2.2, 4.8, 7.0, 9.0, 10.8])
def trailer_frame(A, t, i):
    if t < 2.2:
        k = seg(t, 0, 2.2)
        f = frame(push(A.city, k, 1.0, 1.08, cy=0.6)); A.look.snow(f.img, t)
        caption(f, "CHRISTMAS EVE. LANTERN NIGHT.", ease(seg(t, 0.3, 0.8)) * (1 - ease(seg(t, 1.95, 2.2))))
    elif t < 4.8:
        k = seg(t, 2.2, 4.8); lit = min(5, int(k * 6.5))
        f = frame(push(A.store[lit], k, 1.0, 1.06, cy=0.7)); A.look.snow(f.img, t)
        caption(f, "QUILLON’S OPENS ONE NEW WINDOW EVERY DAY.", ease(seg(t, 2.4, 2.9)))
    elif t < 7.0:
        k = seg(t, 4.8, 7.0)
        f = frame(push(A.cup, k, 1.15, 1.45, cx=0.5, cy=0.48)); A.look.snow(f.img, t, alpha=120)
        caption(f, "A STRIPED CUP OF COCOA. A WINDOW DRESSER WHO SAW TOO MUCH.", ease(seg(t, 5.0, 5.5)), size=50)
    elif t < 9.0:
        k = seg(t, 7.0, 9.0)
        f = frame(push(A.grand, k, 1.1, 1.3, cx=0.45, cy=0.45)); A.look.snow(f.img, t, alpha=120)
        caption(f, "ON THE 24TH, THE GRAND WINDOW NEVER OPENED.", ease(seg(t, 7.2, 7.7)))
    elif t < 10.8:
        k = seg(t, 9.0, 10.8)
        f = frame(push(A.brooch, k, 1.7, 1.95, cx=0.18, cy=0.3))
        g = Image.new("RGBA", f.img.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
        s = 60 + 160 * max(0, math.sin(math.pi * seg(t, 9.6, 10.4)))
        cx, cy = V * 0.42, V * 0.47
        gd.polygon([(cx - s, cy), (cx, cy - 8), (cx + s, cy), (cx, cy + 8)], fill=kit.AMBER_L + (220,))
        gd.polygon([(cx, cy - s), (cx - 8, cy), (cx, cy + s), (cx + 8, cy)], fill=kit.AMBER_L + (220,))
        f.img.alpha_composite(g.filter(ImageFilter.GaussianBlur(2)))
        A.look.snow(f.img, t, alpha=90)
        caption(f, "2,400 SHOPPERS. ONE WORE A BRASS MAGPIE.", ease(seg(t, 9.2, 9.7)))
    else:
        f = frame(A.city.convert("RGBA")); cover_frame(f, A, ease(seg(t, 10.8, 11.4)))
    return A.look.film(f.img, i, TR["cuts"], t), f.sources

# ---------------------------------------------------------------- presentation
PR = dict(N=420, cuts=[2.4, 5.0, 7.6, 10.0, 12.0])
def calendar_grid(f, t):
    d = f.draw()
    cols, rows = 6, 4; gap = 18; w = (V - 160 - gap * (cols - 1)) / cols; h = (V - 2 * BAR - 260 - gap * (rows - 1)) / rows
    opened = int(seg(t, 0.3, 2.1) * 24.99)
    for k in range(24):
        x = 80 + (k % cols) * (w + gap); y = BAR + 190 + (k // cols) * (h + gap)
        on = k < opened
        d.rounded_rectangle([x, y, x + w, y + h], radius=14, fill=kit.NIGHT1, outline=kit.STEEL, width=3)
        if on:
            d.rounded_rectangle([x + 10, y + 10, x + w - 10, y + h - 10], radius=8, fill=kit.AMBER)
        d.text((x + w / 2, y + h / 2), str(k + 1), font=kit.font("display", 78), fill=kit.NIGHT0 if on else kit.FROST, anchor="mm")
    f.note("drawn", "grid", " ".join(str(k) for k in range(1, 25)))
    d.text((V / 2, BAR + 100), "24 WINDOWS · ONE A DAY", font=kit.font("display", 96), fill=kit.SNOW, anchor="mm")
    f.note("drawn", "title", "24 WINDOWS · ONE A DAY")

def drop(f, pg, x, y, ang, a, dy=-500):
    if a <= 0:
        return
    e = ease(a)
    f.paste_page(pg, x, y + dy * (1 - e), angle=ang)

def presentation_frame(A, t, i):
    f = table_bg(A, t)
    if t < 2.4:
        calendar_grid(f, t)
        caption(f, "A CHRISTMAS EVE MURDER MYSTERY ADVENT CALENDAR", ease(seg(t, 0.2, 0.6)), size=48, col=kit.AMBER)
    elif t < 5.0:
        drop(f, A.w1, V * 0.4, V * 0.52, -4, seg(t, 2.4, 2.9))
        drop(f, A.letter, V * 0.62, V * 0.55, 5, seg(t, 3.5, 4.0), dy=700)
        caption(f, "DAY 1: THE CASE · A LETTER · A STORE PLAN", ease(seg(t, 2.6, 3.0)))
    elif t < 7.6:
        pg = A.log; x0, y0 = V / 2 - pg.img.width / 2, V * 0.52 - pg.img.height / 2
        f.paste_page(pg, V / 2, V * 0.52)
        k = seg(t, 5.4, 7.4); rows = A.log_rows
        pick = [j for j in range(2, len(rows), 3)][:int(k * 14) + 1]
        for n, j in enumerate(pick):
            yt, yb, xa, xb, _ = rows[j]
            px0, py = pg.px(xa, (yt + yb) / 2); px1, _ = pg.px(xb, 0)
            prog = 1.0 if n < len(pick) - 1 else min(1.0, (k * 14) % 1 * 1.4)
            kit.marker_strike(f, x0 + px0 - 4, y0 + py, x0 + px1 + 4, (yb - yt) * pg.zoom * 1.4, col=kit.AMBER_D,
                              alpha=160, seed=j, progress=prog)
        caption(f, "DAY 2: 2,400 SHOPPERS · CROSS THEM OUT", ease(seg(t, 5.2, 5.6)))
    elif t < 10.0:
        drop(f, A.w3, V / 2, V * 0.53, -2, seg(t, 7.6, 8.1))
        if t > 8.6:
            kit.pill(f, (V * 0.74, V * 0.24), "TODAY’S QUESTION", kit.font("display", 52), kit.AMBER, kit.NIGHT0)
        caption(f, "DAYS 3–23: A NEW CLUE EACH DAY", ease(seg(t, 7.8, 8.2)))
    elif t < 12.0:
        drop(f, A.env, V * 0.3, V * 0.55, -5, seg(t, 10.0, 10.4))
        ih = 620; iw = ih * 0.75; a = ease(seg(t, 10.5, 11.0))
        if a > 0:
            kit.ipad(f, (V * 0.7 - iw / 2, V * 0.52 - ih / 2 + 400 * (1 - a), V * 0.7 + iw / 2, V * 0.52 + ih / 2 + 400 * (1 - a)), A.ipadcal)
        caption(f, "PRINT AND FOLD · OR TAP TODAY’S WINDOW ON iPAD", ease(seg(t, 10.2, 10.6)), size=50)
    else:
        cover_frame(f, A, ease(seg(t, 12.0, 12.5)))
    return A.look.film(f.img, i, PR["cuts"], t), f.sources

# ---------------------------------------------------------------- encode
def encode(A, fn, spec, outpath, poster_at, picks):
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    bad = CL.forbidden(); N = spec["N"]
    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{V}x{V}", "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
           "-crf", "23", "-preset", "slow", "-movflags", "+faststart", "-frames:v", str(N), outpath]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    hits = hit_frames = 0; stills = {}
    for i in range(N):
        t = i / FPS
        img, src = fn(A, t, i)
        h = kit.spoiler_scan(src, bad); hits += len(h); hit_frames += bool(h)
        if i == int(poster_at * FPS):
            img.save(outpath.replace("_1080.mp4", "_poster.jpg"), quality=90)
        if i in picks:
            stills[i] = img
        proc.stdin.write(img.tobytes())
    proc.stdin.close(); proc.wait()
    sheet = Image.new("RGB", (4 * 360, 3 * 360))
    for k, (i, im) in enumerate(sorted(stills.items())):
        sheet.paste(im.resize((360, 360)), ((k % 4) * 360, (k // 4) * 360))
    sheet.save(outpath.replace("_1080.mp4", "_storyboard.jpg"), quality=85)
    return N, hits, hit_frames

def build():
    A = Assets(); out = {}
    tp = os.path.join(VID, f"{CL.SLUG}_trailer_1080.mp4")
    out["trailer"] = (tp,) + encode(A, trailer_frame, TR, tp, 11.6,
                                    {int(s * FPS) for s in (0.9, 1.9, 2.8, 3.9, 4.6, 5.8, 6.7, 7.9, 9.5, 10.1, 11.5, 13.2)})
    pp = os.path.join(VID, f"{CL.SLUG}_calendar-presentation_1080.mp4")
    out["presentation"] = (pp,) + encode(A, presentation_frame, PR, pp, 1.9,
                                         {int(s * FPS) for s in (0.8, 1.9, 3.0, 4.4, 5.6, 7.0, 8.4, 9.6, 10.7, 11.6, 12.8, 13.8)})
    return out

if __name__ == "__main__":
    for k, v in build().items():
        print(k, v)
