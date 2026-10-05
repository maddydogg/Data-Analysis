"""Two listing videos, variant 2 ("action"): 1080 x 1080, 30 fps, no sound, drawn with code.

trailer       13.5 s  a fast-cut teaser: the store clock smashes in at 21:20, a whip pan along the
                      burning windows of Quillon's, the striped cup knocked over mid-splash, a figure
                      sprinting through the snow, the brass magpie glinting, the register racing past,
                      24 windows flipping open, and the cover slamming in as the end card.
presentation  14.0 s  the product with the same energy: 24 windows flipping open, Day 1 pages thrown in,
                      the register struck out at speed, Day 3 and its hints, envelopes and the iPad,
                      the cover.

Action grammar: smash zooms, whip pans with motion blur, camera shake on every hit, white-amber flash
frames at cuts, manga focus lines, snow streaking past, title-card captions that slam in. Every frame
is a kit.Frame, so the spoiler check reads every caption and every PDF region shown; only Windows 1-3
and the set-up pages ever appear.

    python3 video_v2.py
"""
import math, os, random, subprocess
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageChops
import imageio_ffmpeg
import kit
import cal_listing as CL
from cal_listing import art
import action as X
import cover_v2 as CV
import mockups as M1
import mockups_v2 as M2

V, FPS, BAR = 1080, 30, 54
VARIANT = "v2-action"
VID = os.path.join(CL.CASE, "listing", "v2", "video")

def ease(x):
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)

def out_back(x):
    x = max(0.0, min(1.0, x)); c = 1.9
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

def seg(t, a, b):
    return max(0.0, min(1.0, (t - a) / (b - a)))

# ---------------------------------------------------------------- the film look
class Look:
    def __init__(self, seed=9):
        rng = random.Random(seed)
        self.streaks = [(rng.uniform(-200, V + 200), rng.uniform(-200, V + 200), rng.uniform(30, 120), rng.uniform(1, 3),
                         rng.uniform(600, 1400), rng.randint(50, 170)) for _ in range(150)]
        self.grain = [Image.effect_noise((V, V), 70).convert("L").point(lambda v: 128 + (v - 128) // 3) for _ in range(6)]
        m = Image.new("L", (V, V), 0)
        ImageDraw.Draw(m).ellipse([-V * 0.25, -V * 0.25, V * 1.25, V * 1.25], fill=255)
        self.vmask = m.filter(ImageFilter.GaussianBlur(V * 0.15))

    def snow(self, img, t, alpha=1.0, speed=1.0):
        """Snow streaking down and left past the camera."""
        L = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        a = math.radians(-58); ca, sa = math.cos(a), -math.sin(a)
        for x0, y0, ln, w, sp, al in self.streaks:
            k = (sp * t * speed)
            x = (x0 - ca * k * -1) % (V + 400) - 200; y = (y0 + sa * k) % (V + 400) - 200
            x = (x0 + ca * k) % (V + 400) - 200
            d.line([(x, y), (x - ca * ln, y - sa * ln)], fill=kit.SNOW + (int(al * alpha),), width=int(w))
        img.alpha_composite(L)

    def film(self, img, i, flash=0.0, shake=0.0, blur=(0, 0)):
        im = img.convert("RGB")
        if blur != (0, 0):
            im = X.motion_blur(im, blur[0], blur[1], n=9)
        if shake:
            im = X.shake(im, i, shake)
        dark = Image.new("RGB", im.size, kit.NIGHT0)
        im = Image.composite(im, Image.blend(im, dark, 0.45), self.vmask)
        g = self.grain[i % len(self.grain)]
        im = ImageChops.overlay(im, Image.merge("RGB", (g, g, g)))
        if flash > 0:
            im = Image.blend(im, Image.new("RGB", im.size, (255, 236, 200)), min(0.85, flash))
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, V, BAR], fill=(0, 0, 0)); d.rectangle([0, V - BAR, V, V], fill=(0, 0, 0))
        return im

def hit(t, at, length=0.18):
    """1 at the moment of a hit, decaying to 0 over `length` seconds."""
    if t < at or t > at + length:
        return 0.0
    return 1 - (t - at) / length

def slam(f, text, t, at, y, size=96, fill=kit.SNOW, shadow=kit.AMBER_D, angle=-3, glow=None, maxw=V - 120, name="display"):
    """A caption that slams in: starts big and transparent, lands at full size with an overshoot."""
    if t < at:
        return
    k = seg(t, at, at + 0.16)
    sc = 1.0 + 0.6 * (1 - out_back(k))
    fnt = kit.fit_font(f, text, name, int(size * sc), int(maxw * sc))
    L = Image.new("RGBA", f.img.size, (0, 0, 0, 0))
    X.slam_text(L, (V / 2, y), text, fnt, fill=fill, shadow=shadow, angle=angle, glow=glow)
    if k < 1:
        L.putalpha(L.split()[3].point(lambda v: int(v * min(1, k * 2.5))))
    f.img.alpha_composite(L)
    f.note("drawn", "caption", text)

def bg_frame(im):
    f = kit.Frame(V, V, kit.NIGHT0)
    f.img = im.convert("RGBA") if im.mode != "RGBA" else im.copy()
    return f

def zoom(im, z, cx=0.5, cy=0.5):
    w, h = im.size; s = max(V / w, V / h) * z
    rim = im.resize((int(w * s), int(h * s)), Image.BILINEAR)
    x = int((rim.width - V) * cx); y = int((rim.height - V) * cy)
    return rim.crop((x, y, x + V, y + V)).convert("RGBA")

# ---------------------------------------------------------------- assets
class Assets:
    def __init__(self):
        self.look = Look()
        self.M = M1.Assets(); L, I, p, ip = self.M.L, self.M.I, self.M.p, self.M.ip
        print("assets: art")
        self.clock = M2.art_clock(1300, 1300, 21, 20)
        self.street = CV.keyart(1600, 1080, seed=11, runner=False, ss=1, grain=0)
        self.street_bg = CV.keyart(1200, 1080, seed=13, runner=False, lines=True, ss=1, grain=0)
        self.cups = [M2.art_cup(1080, 1080, t=k / 8) for k in range(9)]
        self.brooch = [M2.art_brooch(1080, 1080, glint=g) for g in (0.0, 0.5, 1.0, 1.4)]
        self.runner = []
        for k in range(8):                      # a stride cycle, drawn once
            cv = art.Canvas(700, 820, ss=2); cv.img = Image.new("RGBA", cv.img.size, (0, 0, 0, 0)); cv.d = ImageDraw.Draw(cv.img)
            X.runner(cv, 300, 800, 760, phase=k / 8, tail=k / 8)
            self.runner.append(cv.img.resize((700, 820), Image.LANCZOS))
        rec = []
        self.cover = CV.cover(V, V, badges=True, record=rec.append, seed=11)
        self.cover_text = rec
        self.cover_art = CV.keyart(V, V, seed=11, ss=1, grain=0)
        print("assets: pages")
        self.cal = L.image(p["calendar"], 900)
        self.w1 = L.image(p["w1"], 860); self.letter = L.image(p["w1letter"], 820)
        self.log = L.image(self.M.log_page, 1500); self.log_rows = CL.log_rows(L, self.M.log_page)
        self.log_small = L.image(self.M.log_page, 860)
        self.w3 = L.image(p["w3"], 800)
        w4 = L.doc[p["hint1"]].search_for("Window 4")[0]
        clip = (40, 60, 572, w4.y0 - 4)
        self.hint = L.image(p["hint1"], int(560 * (clip[3] - clip[1]) / (clip[2] - clip[0])), clip=clip)
        self.ipadcal = I.image(ip["calendar"], 700)
        self.env = L.image(p["envelope"], 640)
        self.envs = {n: M2.env_img(n, 300) for n in (1, 2, 3, 12, 24)}
        self.bg = M2.bg(21, focus=(0.5, 0.5)).img.resize((V, V), Image.BILINEAR)

# ---------------------------------------------------------------- shared shots
def grid_shot(A, f, t, t0, t1, title_at=None):
    """24 windows flipping open in quick succession, each with a little flash."""
    d = f.draw()
    cols, rows = 6, 4; gap = 16; w = (V - 140 - gap * (cols - 1)) / cols; h = (V - 2 * BAR - 330 - gap * (rows - 1)) / rows
    k = seg(t, t0, t1) * 24
    for n in range(24):
        x = 70 + (n % cols) * (w + gap); y = BAR + 250 + (n // cols) * (h + gap)
        on = n < k
        d.rounded_rectangle([x, y, x + w, y + h], radius=12, fill=kit.NIGHT1, outline=kit.STEEL, width=3)
        if on:
            age = k - n
            pad = 10 + max(0, 1 - age) * 30
            d.rounded_rectangle([x + pad * 0.5, y + 8, x + w - pad * 0.5, y + h - 8], radius=8, fill=kit.AMBER)
            if age < 1:
                g = Image.new("RGBA", f.img.size, (0, 0, 0, 0))
                ImageDraw.Draw(g).rounded_rectangle([x - 10, y - 10, x + w + 10, y + h + 10], radius=16, fill=kit.AMBER_L + (int(200 * (1 - age)),))
                f.img.alpha_composite(g.filter(ImageFilter.GaussianBlur(10))); d = f.draw()
        d.text((x + w / 2, y + h / 2), str(n + 1), font=kit.font("display", 74), fill=kit.NIGHT0 if on else kit.FROST, anchor="mm")
    f.note("drawn", "grid", " ".join(str(n) for n in range(1, 25)))

def cover_slam(A, f, t, at):
    """The cover lands: zooms down from 1.25 with an overshoot."""
    k = seg(t, at, at + 0.22)
    z = 1.0 + 0.25 * (1 - out_back(k))
    im = zoom(A.cover, z)
    f.img = im if k >= 1 else Image.blend(f.img.convert("RGB"), im.convert("RGB"), min(1, k * 3)).convert("RGBA")
    for s in A.cover_text:
        f.note("drawn", "cover", s)

def runner_on(A, f, t, x, base, scale=1.0, rate=10):
    im = A.runner[int(t * rate) % 8]
    if scale != 1.0:
        im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
    f.img.alpha_composite(im, (int(x - im.width * 0.43), int(base - im.height)))

# ---------------------------------------------------------------- trailer
TR = dict(N=405, cuts=[0.0, 1.5, 3.0, 4.7, 6.4, 7.8, 9.2, 10.6])
def trailer_frame(A, t, i):
    flash = max(hit(t, c, 0.12) for c in TR["cuts"]); shake = 0; blur = (0, 0)
    if t < 1.5:                                    # the clock smashes in
        k = seg(t, 0.0, 0.25); z = 1.0 + 0.9 * (1 - out_back(k)) + 0.04 * seg(t, 0.25, 1.5)
        f = bg_frame(zoom(A.clock, z))
        if k < 1:
            blur = (0, int(40 * (1 - k)))
        shake = 16 * hit(t, 0.25, 0.3)
        slam(f, "CHRISTMAS EVE. 21:20.", t, 0.45, V - BAR - 110, size=110)
    elif t < 3.0:                                  # whip pan along the burning windows
        k = seg(t, 1.5, 3.0); e = 1 - (1 - k) ** 3
        x = int((A.street.width - V) * (1 - e))
        f = bg_frame(A.street.crop((x, 0, x + V, V)))
        A.look.snow(f.img, t, speed=1.6)
        blur = (int(90 * (1 - e) ** 2), 0)
        slam(f, "THE GRAND WINDOW OPENS IN 10 MINUTES.", t, 1.9, BAR + 110, size=80)
    elif t < 4.7:                                  # the cup knocked over
        k = seg(t, 3.0, 3.6)
        f = bg_frame(zoom(A.cups[min(8, int(k * 8.99))], 1.0 + 0.06 * seg(t, 3.6, 4.7)))
        shake = 14 * hit(t, 3.2, 0.35)
        slam(f, "THE WINDOW DRESSER NEVER SAW IT.", t, 3.55, V - BAR - 100, size=86)
    elif t < 6.4:                                  # a figure sprinting through the snow
        k = seg(t, 4.7, 6.4)
        x = int((A.street_bg.width - V) * (0.15 + 0.6 * k))
        f = bg_frame(A.street_bg.crop((x, 0, x + V, V)))
        A.look.snow(f.img, t, speed=2.2)
        runner_on(A, f, t, V * 0.42, V + 30, scale=1.05, rate=12)
        shake = 4 + 3 * math.sin(t * 40)
        slam(f, "THE KILLER IS STILL IN THE CROWD.", t, 5.0, BAR + 100, size=84)
    elif t < 7.8:                                  # the brass magpie glints
        k = seg(t, 6.4, 7.8)
        g = 1 if k < 0.2 else (2 if k < 0.35 else (3 if k < 0.55 else 2))
        f = bg_frame(zoom(A.brooch[g], 1.0 + 0.12 * k, cx=0.5, cy=0.45))
        flash = max(flash, 0.45 * hit(t, 6.85, 0.2))
        slam(f, "2,400 SHOPPERS. ONE WORE A BRASS MAGPIE.", t, 6.7, V - BAR - 100, size=80)
    elif t < 9.2:                                  # the register races past
        k = seg(t, 7.8, 9.2)
        f = bg_frame(A.bg)
        pg = A.log_small
        y = V * 0.56 + (1 - out_back(seg(t, 7.8, 8.15))) * 900 - 60 * k
        f.paste_page(pg, V / 2, y, angle=-5)
        blur = (0, int(70 * (1 - ease(seg(t, 7.8, 8.4)))))
        slam(f, "2,400 SUSPECTS.", t, 8.0, BAR + 120, size=130, fill=kit.AMBER, shadow=kit.NIGHT0, glow=kit.AMBER)
        slam(f, "24 NIGHTS TO FIND ONE.", t, 8.5, V - BAR - 120, size=110)
    elif t < 10.6:                                 # 24 windows flip open
        f = bg_frame(A.bg)
        grid_shot(A, f, t, 9.25, 10.3)
        slam(f, "ONE WINDOW. ONE LEAD. EVERY NIGHT.", t, 9.3, BAR + 110, size=84)
        shake = 3 * (seg(t, 9.25, 10.3) < 1)
    else:                                          # the cover slams in
        f = bg_frame(A.cover_art)
        cover_slam(A, f, t, 10.6)
        A.look.snow(f.img, t, alpha=0.5, speed=0.8)
        shake = 18 * hit(t, 10.75, 0.3)
    return A.look.film(f.img, i, flash=flash, shake=shake, blur=blur), f.sources

# ---------------------------------------------------------------- presentation
PR = dict(N=420, cuts=[0.0, 2.4, 4.8, 7.4, 9.8, 12.0])
def throw(f, pg, x, y, ang, k, frm=(-700, 0), spin=-14):
    """Throw a page onto the table: flies in from `frm`, spins down to `ang`, lands with an overshoot."""
    if k <= 0:
        return
    e = out_back(k)
    f.paste_page(pg, x + frm[0] * (1 - e), y + frm[1] * (1 - e), angle=ang + spin * (1 - e))

def presentation_frame(A, t, i):
    flash = max(hit(t, c, 0.1) for c in PR["cuts"]); shake = 0; blur = (0, 0)
    f = bg_frame(A.bg); A.look.snow(f.img, t, alpha=0.6, speed=0.9)
    if t < 2.4:
        grid_shot(A, f, t, 0.2, 1.9)
        slam(f, "24 WINDOWS. 24 NIGHTS.", t, 0.1, BAR + 110, size=120)
        slam(f, "A CHRISTMAS EVE MURDER MYSTERY ADVENT CALENDAR", t, 0.5, V - BAR - 60, size=50, fill=kit.AMBER, shadow=kit.NIGHT0)
    elif t < 4.8:
        throw(f, A.w1, V * 0.36, V * 0.56, -6, seg(t, 2.45, 2.75), frm=(-900, 100))
        throw(f, A.letter, V * 0.66, V * 0.58, 6, seg(t, 3.0, 3.3), frm=(900, 150), spin=18)
        blur = (int(80 * hit(t, 2.45, 0.3)) + int(80 * hit(t, 3.0, 0.3)), 0)
        shake = 10 * hit(t, 2.75, 0.2) + 10 * hit(t, 3.3, 0.2)
        slam(f, "DAY 1: THE CASE", t, 2.5, BAR + 100, size=130)
        slam(f, "A LETTER · A STORE PLAN · A MURDER AT 21:20", t, 3.5, V - BAR - 70, size=56, fill=kit.AMBER, shadow=kit.NIGHT0)
    elif t < 7.4:
        pg = A.log_small; k = seg(t, 4.85, 5.15)
        x0, y0 = V / 2 - pg.img.width / 2, V * 0.58 - pg.img.height / 2 + 700 * (1 - out_back(k))
        f.paste_page(pg, V / 2, y0 + pg.img.height / 2)
        blur = (0, int(70 * hit(t, 4.85, 0.3)))
        rows = A.log_rows; ks = seg(t, 5.3, 7.2)
        pick = [j for j in range(1, len(rows), 2)]
        n_done = ks * len(pick)
        for n, j in enumerate(pick[:int(n_done) + 1]):
            yt, yb, xa, xb, _ = rows[j]
            px0, py = pg.px(xa, (yt + yb) / 2); px1, _ = pg.px(xb, 0)
            prog = 1.0 if n < int(n_done) else n_done % 1
            kit.marker_strike(f, x0 + px0 - 4, y0 + py, x0 + px1 + 4, (yb - yt) * pg.zoom * 1.4, col=kit.AMBER_D,
                              alpha=170, seed=j, progress=prog)
        slam(f, "DAY 2: 2,400 SUSPECTS", t, 4.9, BAR + 100, size=120)
        slam(f, "CROSS THEM OUT, NIGHT BY NIGHT", t, 5.6, V - BAR - 70, size=64, fill=kit.AMBER, shadow=kit.NIGHT0)
    elif t < 9.8:
        k = seg(t, 7.45, 7.75)
        z = 1.0 + 0.35 * ease(seg(t, 8.4, 8.9))          # punch in on the question
        sub = kit.Frame(V, V, kit.NIGHT0); sub.img = f.img.copy()
        throw(sub, A.w3, V * 0.5, V * 0.6, -3, k, frm=(0, -900), spin=10)
        if z > 1.0:
            sub.img = zoom(sub.img, z, cx=0.32, cy=0.78)
        f.img = sub.img; f.sources += sub.sources
        shake = 12 * hit(t, 7.75, 0.25)
        slam(f, "DAYS 3–23: NEW EVIDENCE EVERY NIGHT", t, 7.5, BAR + 90, size=100)
        if t > 9.0:
            f.paste_page(A.hint, V * 0.62, V * 0.8, angle=5)
            X.badge(f.img, (V * 0.72, V * 0.68), "3 LEVELS OF HINTS", kit.font("display", 56), bg=kit.SNOW, fg=kit.NIGHT0, angle=6)
            f.note("drawn", "badge", "3 LEVELS OF HINTS")
            shake = max(shake, 10 * hit(t, 9.0, 0.2))
    elif t < 12.0:
        throw(f, A.env, V * 0.3, V * 0.57, -6, seg(t, 9.85, 10.15), frm=(-900, 0))
        k = seg(t, 10.3, 10.6); ih = 640; iw = ih * 0.75
        if k > 0:
            e = out_back(k); yy = V * 0.55 + 700 * (1 - e)
            tab = kit.Frame(int(iw) + 40, ih + 40, (0, 0, 0)); tab.img = Image.new("RGBA", tab.img.size, (0, 0, 0, 0))
            kit.ipad(tab, (20, 20, 20 + iw, 20 + ih), A.ipadcal)
            f.paste(tab.img, V * 0.7, yy, angle=5)
            f.sources += tab.sources
        if t > 11.0:
            r = 30 + 160 * seg(t, 11.0, 11.5)
            d = f.draw(); cx, cy = V * 0.66, V * 0.5
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=kit.AMBER, width=8)
            d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=kit.AMBER)
        for n, (x, y, a, at) in zip((1, 12, 24), ((V * 0.16, V * 0.3, -14, 10.05), (V * 0.5, V * 0.24, 10, 10.2), (V * 0.86, V * 0.84, -10, 10.4))):
            kk = seg(t, at, at + 0.25)
            if kk > 0:
                f.paste(A.envs[n], x - 500 * (1 - out_back(kk)), y, angle=a); f.note("drawn", "envelope", str(n))
        blur = (int(90 * hit(t, 9.85, 0.3)), int(60 * hit(t, 10.3, 0.3)))
        slam(f, "PRINT AND FOLD — OR TAP ON iPAD", t, 9.9, BAR + 100, size=96)
    else:
        f = bg_frame(A.cover_art)
        cover_slam(A, f, t, 12.0)
        A.look.snow(f.img, t, alpha=0.5, speed=0.8)
        shake = 18 * hit(t, 12.15, 0.3)
    return A.look.film(f.img, i, flash=flash, shake=shake, blur=blur), f.sources

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

def build(only=None):
    A = Assets(); out = {}
    if only in (None, "trailer"):
        tp = os.path.join(VID, f"{CL.SLUG}_{VARIANT}_trailer_1080.mp4")
        out["trailer"] = (tp,) + encode(A, trailer_frame, TR, tp, 11.8,
                                        {int(s * FPS) for s in (0.9, 2.0, 2.8, 3.5, 4.3, 5.4, 6.9, 8.3, 8.9, 9.8, 11.2, 13.3)})
    if only in (None, "presentation"):
        pp = os.path.join(VID, f"{CL.SLUG}_{VARIANT}_calendar-presentation_1080.mp4")
        out["presentation"] = (pp,) + encode(A, presentation_frame, PR, pp, 1.9,
                                             {int(s * FPS) for s in (1.0, 2.0, 3.2, 4.4, 5.8, 7.0, 8.0, 9.3, 10.6, 11.6, 12.6, 13.8)})
    return out

if __name__ == "__main__":
    import sys
    for k, v in build(sys.argv[1] if len(sys.argv) > 1 else None).items():
        print(k, v)
