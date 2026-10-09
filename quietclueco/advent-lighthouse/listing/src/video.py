"""Two listing videos: 1080 x 1080, 30 fps, no sound, drawn with code. A calm pace, like turning the
pages of a picture book.

trailer       14.0 s  dusk over the Sound with the beam slowly sweeping and snow falling; Ezra's journal
                      page writing itself line by line; the boathouse at night with a hand lamp flickering;
                      Christmas Eve, when the light goes out; the Sound Book sliding in and a pencil
                      striking lines; the cover.
presentation  14.0 s  the product: a finger taps Window 1 on the calendar and it lights up; the Day 1 pages
                      turn over; a pencil works down the Sound Book; Day 3 with a slow push in on the
                      question; envelopes and a tap on the iPad; the cover.

Every frame is a kit.Frame, so the spoiler check reads every caption and every PDF region shown; only
Windows 1-3 and the set-up pages ever appear.

    python3 video.py [trailer|presentation]
"""
import math, os, random, subprocess
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import imageio_ffmpeg
import kit
import cal_listing as CL
from cal_listing import art as A, scenes as SC, COVER
import cover_options as CO
import mockups as M

V, FPS = 1080, 30
VID = os.path.join(CL.CASE, "listing", "video")

def ease(x):
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)

def seg(t, a, b):
    return max(0.0, min(1.0, (t - a) / (b - a)))

def fade(t, a, b, d=0.4):
    """1 inside [a, b], easing in and out over d seconds."""
    return ease(seg(t, a, a + d)) * (1 - ease(seg(t, b - d, b)))

# ---------------------------------------------------------------- look
class Look:
    def __init__(self, seed=5):
        rng = random.Random(seed)
        self.flakes = [(rng.uniform(0, V), rng.uniform(0, V), rng.uniform(1.4, 3.6), rng.uniform(25, 60), rng.uniform(0, 6.28))
                       for _ in range(170)]
        self.grain = [Image.effect_noise((V, V), 50).convert("L").point(lambda v: 128 + (v - 128) // 7) for _ in range(5)]

    def snow(self, img, t, alpha=1.0):
        L = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        for x0, y0, r, sp, ph in self.flakes:
            y = (y0 + sp * t) % (V + 20) - 10
            x = (x0 + 14 * math.sin(t * 0.7 + ph)) % V
            d.ellipse([x - r, y - r, x + r, y + r], fill=A.SNOW + (int(200 * alpha),))
        img.alpha_composite(L)

    def film(self, img, i):
        im = img.convert("RGB")
        g = self.grain[i % len(self.grain)]
        return ImageChops.overlay(im, Image.merge("RGB", (g, g, g)))

def caption(f, text, t, a, b, y=V - 110, size=46):
    """A cream caption band that fades in and out (no slams: a calm read)."""
    k = fade(t, a, b, 0.45)
    if k <= 0:
        return
    fnt = kit.fit_font(f, text, "display", size, V - 180)
    d0 = ImageDraw.Draw(f.img)
    w = kit.spaced_width(d0, text, fnt, size * 0.06) + 80
    L = Image.new("RGBA", f.img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle([V / 2 - w / 2, y - size * 0.95, V / 2 + w / 2, y + size * 0.65], radius=size * 0.8, fill=A.CREAM + (240,))
    kit.spaced(L, (V / 2, y + size * 0.3), text, fnt, A.NIGHT, size * 0.06)
    if k < 1:
        L.putalpha(L.split()[3].point(lambda v: int(v * k)))
    f.img.alpha_composite(L)
    f.note("drawn", "caption", text)

def bg_frame(im):
    f = kit.Frame(V, V)
    f.img = im.convert("RGBA") if im.mode != "RGBA" else im.copy()
    return f

def zoom(im, z, cx=0.5, cy=0.5):
    w, h = im.size; s = max(V / w, V / h) * z
    rim = im.resize((int(w * s), int(h * s)), Image.BILINEAR)
    x = int((rim.width - V) * cx); y = int((rim.height - V) * cy)
    return rim.crop((x, y, x + V, y + V)).convert("RGBA")

def beam(img, x, y, angle, length, spread=5, alpha=80):
    L = Image.new("RGBA", (img.width // 2, img.height // 2), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    for k, (sp, al) in enumerate(((spread, alpha), (spread * 0.45, alpha))):
        a1, a2 = math.radians(angle - sp), math.radians(angle + sp)
        pts = [(x / 2, y / 2), (x / 2 + math.cos(a1) * length / 2, y / 2 + math.sin(a1) * length / 2),
               (x / 2 + math.cos(a2) * length / 2, y / 2 + math.sin(a2) * length / 2)]
        d.polygon(pts, fill=A.LAMP + (al,))
    L = L.filter(ImageFilter.GaussianBlur(5)).resize(img.size, Image.BILINEAR)
    img.alpha_composite(L)

def lamp_pos(w, h, hz_frac, tower):
    ih = min(w, h); base = h * hz_frac + ih * 0.005; ht = h * tower
    return w * 0.63, base - ht * 0.895

def page_turn(f, a_img, b_img, k, cx, cy):
    """A page turning over about its left edge: a shrinks to the spine, then b grows from it."""
    if k < 0.5:
        s = 1 - ease(k * 2)
        im = a_img
    else:
        s = ease((k - 0.5) * 2)
        im = b_img
    w = max(2, int(im.width * s))
    sq = im.resize((w, im.height), Image.BILINEAR)
    shade = Image.new("RGBA", sq.size, (0, 0, 0, int(90 * (1 - s))))
    sq.alpha_composite(shade)
    f.paste(sq, cx - im.width / 2 + w / 2, cy, shadow=True)

def finger(f, x, y, press=0.0):
    """An index finger reaching up from the bottom of the frame, nail and knuckle creases drawn, with a tap ripple."""
    d = f.draw()
    if press > 0:
        for k, rr in enumerate((90 * press, 60 * press)):
            d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=A.RUST + (int(220 * (1 - press * 0.6)),), width=6 - k * 2)
    L = Image.new("RGBA", f.img.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
    skin, shade_, line = (226, 180, 146, 255), (204, 156, 122, 255), (160, 112, 84, 255)
    ld.rounded_rectangle([x - 33, y - 6, x + 33, V + 80], radius=33, fill=skin, outline=line, width=3)
    ld.rounded_rectangle([x + 10, y + 8, x + 31, V + 80], radius=20, fill=shade_)
    ld.rounded_rectangle([x - 20, y + 4, x + 20, y + 52], radius=16, fill=(240, 214, 198, 255), outline=line, width=2)
    for k in (130, 142, 236, 246):
        ld.arc([x - 22, y + k - 6, x + 22, y + k + 6], 200, 340, fill=line, width=2)
    f.img.alpha_composite(L)

# ---------------------------------------------------------------- assets
class Assets:
    def __init__(self):
        self.look = Look()
        self.M = M.Assets(); L, I, p, ip = self.M.L, self.M.I, self.M.p, self.M.ip
        print("assets: art", flush=True)
        self.hz, self.tw = 0.6, 0.33
        self.dusk = SC.keyart(1300, 1300, seed=11, figure=False, beams=False, snow_n=0, moon_xy=(0.14, 0.12))
        self.lamp = lamp_pos(1300, 1300, self.hz, self.tw)
        self.dark = SC.keyart(1080, 1080, seed=11, figure=False, lit=False, snow_n=0, moon_xy=None, boat_x=0.25)
        self.lit = SC.keyart(1080, 1080, seed=11, figure=False, lit=True, beams=False, snow_n=0, moon_xy=None, boat_x=0.25)
        self.night = M._night(1080, 1080, figure=True)
        cf = CO.option_b()                          # the main listing image: the window seat with Bosun
        self.cover = cf.img.convert("RGB").resize((V, V), Image.LANCZOS)
        self.cover_text = [t for k, _, t in cf.sources if k == "drawn"]
        print("assets: pages", flush=True)
        j = L.doc[p["w1journal"]]
        r0 = j.search_for("1 December")[0]; r1 = j.search_for("a day at a time")[0]
        clip = (40, r0.y0 - 12, 572, r1.y1 + 14)
        self.journal = L.image(p["w1journal"], int(980 * (clip[3] - clip[1]) / (clip[2] - clip[0])), clip=clip)
        self.cal = I.image(ip["calendar"], 1000)
        self.calpage = L.image(p["calendar"], 900)
        self.w1 = L.image(p["w1"], 900); self.chartpg = L.image(p["w1chart"], 900); self.tower = L.image(p["w1tower"], 900)
        self.log = L.image(self.M.log_page, 1000); self.log_rows = CL.log_rows(L, self.M.log_page)
        self.w3 = L.image(p["w3"], 1000)
        self.env = L.image(p["envelope"], 640)
        self.ipadcal = I.image(ip["calendar"], 640)
        self.envs = {n: kit.envelope(300, n) for n in (1, 2, 3, 12, 24)}
        self.table = M.bg_table(31).resize((V, V), Image.LANCZOS)
        self.office = M._office(1080, 1080)

# ---------------------------------------------------------------- trailer
TR = dict(N=420)
def trailer_frame(A_, t, i):
    if t < 3.2:                                     # dusk, the beam sweeping, a slow rise from the sea to the tower
        k = seg(t, 0, 3.2)
        f = bg_frame(zoom(A_.dusk, 1.0 + 0.06 * k, cx=0.55, cy=0.7 - 0.35 * ease(k)))
        sc = V * (1.06 + 0.06 * k) / 1300
        x0 = (1300 * sc - V) * 0.55; y0 = (1300 * sc - V) * (0.7 - 0.35 * ease(k))
        lx, ly = A_.lamp[0] * sc - x0, A_.lamp[1] * sc - y0
        beam(f.img, lx, ly, 150 + 70 * k, V * 1.6, alpha=70)
        A_.look.snow(f.img, t)
        caption(f, "CANDLEHOLM, DECEMBER", t, 0.4, 3.2)
    elif t < 5.8:                                   # the journal writes itself
        k = seg(t, 3.2, 5.8)
        f = bg_frame(A_.table)
        pg = A_.journal
        im = pg.img.copy()
        reveal = int(im.width * 0.12 + im.width * 0.95 * ease(k * 1.1))
        mask = Image.new("L", im.size, 0); md = ImageDraw.Draw(mask)
        rows = 7
        for r in range(rows):                       # reveal line by line, top to bottom
            y0 = im.height * (0.18 + 0.115 * r)
            done = (k * 1.25 * rows) - r
            if done > 0:
                md.rectangle([0, y0 - 6, im.width * min(1, done), y0 + im.height * 0.115 + 2], fill=255)
        md.rectangle([0, 0, im.width, im.height * 0.18], fill=255)
        paper = Image.new("RGBA", im.size, (253, 251, 244, 255))
        paper.paste(im, (0, 0), mask)
        f.paste(paper, V / 2, V / 2 - 30, angle=-2)
        f.note("pdf", pg.source, pg.text)
        caption(f, "THE KEEPER WROTE EVERYTHING DOWN", t, 3.3, 5.8)
    elif t < 8.3:                                   # the boathouse at night, a hand lamp flickering
        k = seg(t, 5.8, 8.3)
        f = bg_frame(zoom(A_.night, 1.05 + 0.08 * k, cx=0.25, cy=0.6))
        fl = 0.6 + 0.4 * abs(math.sin(t * 9)) * (0.5 + 0.5 * math.sin(t * 3.1))
        g = Image.new("RGBA", f.img.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
        gd.ellipse([180, 560, 420, 760], fill=A.LAMP + (int(120 * fl),))
        f.img.alpha_composite(g.filter(ImageFilter.GaussianBlur(30)))
        A_.look.snow(f.img, t, 0.8)
        caption(f, "SOMEONE IN A RED CAP KEPT COMING BACK", t, 5.9, 8.3)
    elif t < 10.8:                                  # Christmas Eve: the light goes out
        k = seg(t, 8.3, 10.8)
        f = bg_frame(Image.blend(A_.lit, A_.dark, ease(seg(t, 8.9, 9.9))))
        if t < 9.9:
            lx, ly = lamp_pos(1080, 1080, 0.6, 0.33)
            beam(f.img, lx, ly, 200, V * 1.4, alpha=int(70 * (1 - ease(seg(t, 8.9, 9.9)))))
        A_.look.snow(f.img, t)
        caption(f, "ON CHRISTMAS EVE THE LAMP DID NOT COME ON", t, 8.4, 10.8)
    elif t < 12.6:                                  # the Sound Book and a pencil
        f = bg_frame(A_.office)
        pg = A_.log; k = seg(t, 10.8, 11.3)
        cy = V * 0.52 + 600 * (1 - ease(k))
        x0, y0 = V / 2 - pg.img.width / 2, cy - pg.img.height / 2
        f.paste_page(pg, V / 2, cy)
        rows = A_.log_rows; ks = seg(t, 11.3, 12.5)
        pick = [j for j in range(0, len(rows), 2)][:22]
        n_done = ks * len(pick)
        for n, j in enumerate(pick[:int(n_done) + 1]):
            yt, yb, xa, xb, _ = rows[j]
            px0, py = pg.px(xa, (yt + yb) / 2); px1, _ = pg.px(xb, 0)
            prog = 1.0 if n < int(n_done) else n_done % 1
            kit.pencil_strike(f, x0 + px0 - 4, y0 + py, x0 + px1 - pg.zoom * 20, (yb - yt) * pg.zoom * 1.3, seed=j, progress=prog)
        caption(f, "2,400 TRAVELLERS. 24 COSY EVENINGS. ONE RED CAP.", t, 10.9, 12.6)
    else:                                           # the cover
        f = bg_frame(A_.cover)
        k = fade(t, 12.6, 15, 0.5)
        if k < 1:
            f.img = Image.blend(A_.office.convert("RGB"), A_.cover.convert("RGB"), k).convert("RGBA")
        for s_ in A_.cover_text:
            f.note("drawn", "cover", s_)
    return A_.look.film(f.img, i), f.sources

# ---------------------------------------------------------------- presentation
PR = dict(N=420)
def presentation_frame(A_, t, i):
    if t < 2.6:                                     # tap Window 1 on the calendar
        f = bg_frame(A_.table)
        pg = A_.cal
        f.paste_page(pg, V / 2, V / 2 - 20)
        x0, y0 = V / 2 - pg.img.width / 2, V / 2 - 20 - pg.img.height / 2
        cal = A_.M.I.doc[A_.M.ip["calendar"]]
        r = cal.search_for("1 December")[0]
        px, py = pg.px((r.x0 + r.x1) / 2, r.y0 - 40)
        tx, ty = x0 + px, y0 + py
        press = seg(t, 1.0, 1.6)
        if t > 1.15:
            g = Image.new("RGBA", f.img.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
            gd.rounded_rectangle([tx - 80, ty - 70, tx + 80, ty + 70], radius=14, fill=A.LAMP + (int(170 * ease(seg(t, 1.15, 1.6))),))
            f.img.alpha_composite(g.filter(ImageFilter.GaussianBlur(10)))
        fy = ty + 200 * (1 - ease(seg(t, 0.2, 1.0))) + (8 if 1.0 < t < 1.3 else 0)
        finger(f, tx + 10, fy, press if 1.0 < t < 1.8 else 0)
        caption(f, "OPEN ONE WINDOW A NIGHT", t, 0.2, 2.6)
    elif t < 5.4:                                   # the Day 1 pages turn over
        f = bg_frame(A_.table)
        k = seg(t, 2.6, 5.4)
        a, b, c = A_.w1, A_.tower, A_.chartpg
        if k < 0.42:
            page_turn(f, a.img, b.img, seg(k, 0.05, 0.42), V / 2, V / 2 - 10); f.note("pdf", a.source, a.text); f.note("pdf", b.source, b.text)
        elif k < 0.8:
            page_turn(f, b.img, c.img, seg(k, 0.45, 0.8), V / 2, V / 2 - 10); f.note("pdf", b.source, b.text); f.note("pdf", c.source, c.text)
        else:
            f.paste_page(c, V / 2, V / 2 - 10)
        caption(f, "DAY 1: THE CASE, THE TOWER, THE CHART", t, 2.7, 5.4)
    elif t < 8.4:                                   # the pencil works down the Sound Book
        f = bg_frame(A_.office)
        pg = A_.log
        x0, y0 = V / 2 - pg.img.width / 2, V * 0.5 - pg.img.height / 2
        f.paste_page(pg, V / 2, V * 0.5)
        rows = A_.log_rows; ks = seg(t, 5.7, 8.2)
        rng = random.Random(3)
        pick = [j for j in range(len(rows)) if rng.random() < 0.5]
        n_done = ks * len(pick)
        for n, j in enumerate(pick[:int(n_done) + 1]):
            yt, yb, xa, xb, _ = rows[j]
            px0, py = pg.px(xa, (yt + yb) / 2); px1, _ = pg.px(xb, 0)
            prog = 1.0 if n < int(n_done) else n_done % 1
            kit.pencil_strike(f, x0 + px0 - 4, y0 + py, x0 + px1 - pg.zoom * 20, (yb - yt) * pg.zoom * 1.3, seed=j, progress=prog)
        caption(f, "DAY 2: THE SOUND BOOK. CROSS THEM OUT", t, 5.5, 8.4)
    elif t < 11.0:                                  # Day 3, a slow push in on the question
        k = seg(t, 8.4, 11.0)
        sub = kit.Frame(V, V); sub.img = A_.table.convert("RGBA").copy()
        sub.paste_page(A_.w3, V / 2, V / 2 + 20)
        z = 1.0 + 0.32 * ease(seg(t, 9.2, 10.9))
        f = bg_frame(zoom(sub.img, z, cx=0.4, cy=0.72))
        f.sources += sub.sources
        caption(f, "DAYS 3–23: A JOURNAL PAGE AND A NEW LEAD EACH NIGHT", t, 8.5, 11.0, size=40)
    elif t < 12.8:                                  # envelopes and the iPad
        f = bg_frame(A_.table)
        f.paste_page(A_.env, V * 0.3, V * 0.52, angle=-5)
        for n, (x, y, a, at) in zip((1, 12, 24), ((V * 0.17, V * 0.2, -10, 11.1), (V * 0.42, V * 0.84, 8, 11.25), (V * 0.12, V * 0.8, -6, 11.4))):
            kk = ease(seg(t, at, at + 0.4))
            if kk > 0:
                f.paste(A_.envs[n], x, y + 300 * (1 - kk), angle=a); f.note("drawn", "envelope", str(n))
        ih = 620; iw = ih * 0.75
        tab = kit.Frame(int(iw) + 40, ih + 40); tab.img = Image.new("RGBA", tab.img.size, (0, 0, 0, 0))
        kit.ipad(tab, (20, 20, 20 + iw, 20 + ih), A_.ipadcal)
        f.paste(tab.img, V * 0.72, V * 0.5, angle=4); f.sources += tab.sources
        press = seg(t, 12.0, 12.5)
        finger(f, V * 0.7, V * 0.42 + 120 * (1 - ease(seg(t, 11.4, 12.0))), press if t > 12.0 else 0)
        caption(f, "PRINT AND FOLD, OR TAP ON iPAD", t, 11.0, 12.8)
    else:
        f = bg_frame(A_.cover)
        k = fade(t, 12.8, 15, 0.5)
        if k < 1:
            f.img = Image.blend(A_.table.convert("RGB"), A_.cover.convert("RGB"), k).convert("RGBA")
        for s_ in A_.cover_text:
            f.note("drawn", "cover", s_)
    return A_.look.film(f.img, i), f.sources

# ---------------------------------------------------------------- encode
def encode(A_, fn, spec, outpath, poster_at, picks):
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    bad = CL.forbidden(); N = spec["N"]
    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{V}x{V}", "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
           "-crf", "24", "-preset", "slow", "-movflags", "+faststart", "-frames:v", str(N), outpath]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    hits = hit_frames = 0; stills = {}; captions = set()
    for i in range(N):
        t = i / FPS
        img, src = fn(A_, t, i)
        h = kit.spoiler_scan(src, bad); hits += len(h); hit_frames += bool(h)
        captions |= {s for k, kind, s in src if kind == "caption"}
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
    return N, hits, hit_frames, sorted(captions)

def build(only=None):
    A_ = Assets(); out = {}
    if only in (None, "trailer"):
        tp = os.path.join(VID, f"{CL.SLUG}_trailer_1080.mp4")
        out["trailer"] = (tp,) + encode(A_, trailer_frame, TR, tp, 13.5,
                                        {int(s * FPS) for s in (0.8, 2.4, 3.6, 5.2, 6.4, 7.8, 8.6, 10.2, 11.2, 12.2, 13.0, 13.9)})
    if only in (None, "presentation"):
        pp = os.path.join(VID, f"{CL.SLUG}_calendar-presentation_1080.mp4")
        out["presentation"] = (pp,) + encode(A_, presentation_frame, PR, pp, 1.4,
                                             {int(s * FPS) for s in (0.6, 1.4, 3.0, 3.9, 4.8, 6.3, 7.6, 9.0, 10.6, 11.6, 12.4, 13.9)})
    return out

if __name__ == "__main__":
    import sys
    for k, v in build(sys.argv[1] if len(sys.argv) > 1 else None).items():
        print(k, v[:4])
