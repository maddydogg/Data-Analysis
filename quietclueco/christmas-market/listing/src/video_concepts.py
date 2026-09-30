"""Five different directions for the second listing video, one hero frame each (1080x1080).
A Noir snowfall · B Redacted case file · C The last 40 minutes · D Paper-cut shadow theatre ·
E Inspector Wren (cozy cartoon). All drawn by code; spoiler-scanned like every other asset.

    python3 video_concepts.py OUTDIR
"""
import math, os, random, sys
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import kit
from kit import GREEN, CRAN, PARCH, MUST, INK, DEEP, PARCH_DARK, font
import case_listing as CL
import cartoon_frames as CF

W = 2160
OUT = 1080
NIGHT = (0x0B, 0x10, 0x0E); COLD = (0x1D, 0x2E, 0x28)

def new(bg):
    return kit.Frame(W, W, bg)

def grad(f, top, bottom):
    d = f.draw()
    for y in range(W):
        t = y / W
        d.line([(0, y), (W, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip(top, bottom)))

def vignette(f, strength=200):
    m = Image.radial_gradient("L").resize((W, W))
    m = m.point(lambda v: int(max(0, v - 70) * strength / 185))
    dark = Image.new("RGBA", (W, W), (0, 0, 0, 255)); dark.putalpha(m)
    f.img.alpha_composite(dark)

def grain(f, amount=18):
    n = Image.effect_noise((W, W), 40).convert("L")
    layer = Image.merge("RGBA", (n, n, n, Image.new("L", (W, W), amount)))
    f.img.alpha_composite(layer)

def glow(f, x, y, r, col, a=110):
    g = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse([x - r, y - r, x + r, y + r], fill=col + (a,))
    f.img.alpha_composite(g.filter(ImageFilter.GaussianBlur(r * 0.45)))

def poly(f, pts, col, alpha=255, blur=0):
    g = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    ImageDraw.Draw(g).polygon(pts, fill=col + (alpha,))
    if blur:
        g = g.filter(ImageFilter.GaussianBlur(blur))
    f.img.alpha_composite(g)

def flakes(f, n, seed, box, col=PARCH, amin=90, amax=240, smin=4, smax=14):
    rng = random.Random(seed)
    g = Image.new("RGBA", (W, W), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    x0, y0, x1, y1 = box
    for _ in range(n):
        x, y, r = rng.uniform(x0, x1), rng.uniform(y0, y1), rng.uniform(smin, smax)
        d.ellipse([x - r, y - r, x + r, y + r], fill=col + (int(rng.uniform(amin, amax)),))
    f.img.alpha_composite(g)

def silhouette(d, fx, fy, s, body=(8, 10, 9), hat=CRAN):
    """A figure seen from behind: long coat, scarf, red bobble hat. No face."""
    coat = [(fx - 70 * s, fy - 330 * s), (fx + 70 * s, fy - 330 * s), (fx + 125 * s, fy), (fx - 125 * s, fy)]
    d.polygon(coat, fill=body)
    d.ellipse([fx - 62 * s, fy - 450 * s, fx + 62 * s, fy - 320 * s], fill=body)
    d.chord([fx - 72 * s, fy - 500 * s, fx + 72 * s, fy - 350 * s], 180, 360, fill=hat)
    d.rectangle([fx - 72 * s, fy - 432 * s, fx + 72 * s, fy - 408 * s], fill=tuple(int(c * 0.72) for c in hat))
    d.ellipse([fx - 32 * s, fy - 548 * s, fx + 32 * s, fy - 484 * s], fill=hat)
    d.rectangle([fx - 105 * s, fy, fx - 25 * s, fy + 30 * s], fill=body)
    d.rectangle([fx + 25 * s, fy, fx + 105 * s, fy + 30 * s], fill=body)

# ---------------------------------------------------------------- A. Noir snowfall
def concept_a():
    f = new(NIGHT); grad(f, NIGHT, COLD)
    d = f.draw()
    # far market rooftops, barely lit
    for i, x in enumerate(range(-60, W, 300)):
        h = 260 + (i % 3) * 40
        d.polygon([(x, 1380), (x + 140, 1380 - h), (x + 280, 1380)], fill=(0x14, 0x1E, 0x1A))
        d.rectangle([x + 30, 1380 - h * 0.35, x + 250, 1380], fill=(0x14, 0x1E, 0x1A))
        if i % 2 == 0:
            d.rectangle([x + 110, 1290, x + 170, 1340], fill=(0x6E, 0x5A, 0x2E))
    # snow ground
    d.rectangle([0, 1380, W, W], fill=(0x2B, 0x33, 0x30))
    # street lamp and its cone of light
    lx = 520
    d.rectangle([lx - 14, 420, lx + 14, 1400], fill=(0x05, 0x07, 0x06))
    d.polygon([(lx - 70, 420), (lx + 70, 420), (lx + 40, 360), (lx - 40, 360)], fill=(0x05, 0x07, 0x06))
    glow(f, lx, 440, 90, (0xFF, 0xE2, 0xA6), 220)
    poly(f, [(lx - 40, 440), (lx + 40, 440), (lx + 620, 1560), (lx - 520, 1560)], (0xFF, 0xE6, 0xB5), 60, 30)
    poly(f, [(lx - 500, 1420), (lx + 600, 1420), (lx + 700, 1640), (lx - 600, 1640)], (0xE9, 0xE4, 0xD8), 170, 40)
    # heavy snow inside the light, sparse outside
    flakes(f, 260, 1, (lx - 450, 450, lx + 560, 1560), (0xFF, 0xF6, 0xE3), 120, 250, 4, 11)
    flakes(f, 90, 2, (0, 0, W, W), (0xB8, 0xC4, 0xBE), 40, 120, 3, 8)
    # the figure walking out of the light, long shadow towards us
    fx, fy = 1340, 1560
    poly(f, [(fx - 110, fy + 20), (fx + 110, fy + 20), (fx + 420, W), (fx - 180, W)], (0, 0, 0), 150, 12)
    silhouette(f.draw(), fx, fy, 1.05)
    d = f.draw()
    for k in range(6):
        px = fx - 170 - k * 150; py = fy + 60 + (k % 2) * 30
        d.ellipse([px - 26, py - 12, px + 26, py + 12], fill=(0x1B, 0x22, 0x20))
    vignette(f, 230); grain(f, 22)
    f.text((150, 170), "Ember Square. 20:05.", font("display-italic", 70), (0xC9, 0xC2, 0xB2))
    f.text((W / 2, 1760), "6,000 visitors.", font("display", 150), PARCH, anchor="ma")
    f.text((W / 2, 1935), "One of them is a killer.", font("display", 104), (0xE0, 0x6B, 0x78), anchor="ma")
    return f

# ---------------------------------------------------------------- B. Redacted case file
def concept_b():
    f = new((0x2A, 0x1C, 0x13)); grad(f, (0x1E, 0x14, 0x0E), (0x3A, 0x27, 0x1A))
    glow(f, 700, 500, 900, (0xF6, 0xD0, 0x7A), 55)
    d = f.draw()
    # open green folder
    d.rounded_rectangle([140, 300, 2030, 1780], radius=26, fill=(0x1A, 0x2B, 0x23))
    d.rounded_rectangle([160, 250, 560, 330], radius=18, fill=CRAN)
    f.text((360, 262), "CASE No. 1", font("black", 48), PARCH, anchor="ma")
    # left sheet: typed report with redactions
    sheet = kit.Frame(900, 1300, (0xFB, 0xF8, 0xF1)); sd = sheet.draw()
    mono = kit.ImageFont.truetype(os.path.join(kit.FONT_DIR, "CourierPrime-Bold.ttf"), 42)
    monor = kit.ImageFont.truetype(os.path.join(kit.FONT_DIR, "CourierPrime-Regular.ttf"), 38)
    sd.text((60, 60), "EMBERFIELD CONSTABULARY", font=mono, fill=INK)
    sd.text((60, 120), "INCIDENT REPORT · 23 DECEMBER", font=monor, fill=INK)
    sd.line([(60, 185), (840, 185)], fill=INK, width=3)
    lines = [("VICTIM:", "Ambrose Thorne, judge"), ("FOUND:", "20:40, the Judges' Tent"),
             ("CAUSE:", "not cinnamon"), ("SUSPECTS:", "6,000 wristbands"),
             ("WITNESS:", "a red bobble hat, 20:05"), ("KILLER:", None), ("MOTIVE:", None), ("STATUS:", None)]
    y = 240
    rng = random.Random(5)
    for k, v in lines:
        sd.text((60, y), k, font=mono, fill=INK)
        if v:
            sd.text((330, y + 3), v, font=monor, fill=INK)
        else:
            sd.rectangle([330, y + 2, 330 + rng.randint(330, 500), y + 44], fill=INK)
        y += 105
    for _ in range(3):
        sd.rectangle([60, y, 60 + rng.randint(500, 780), y + 40], fill=INK); y += 70
    sheet.note("drawn", "report", " ".join(f"{k} {v or ''}" for k, v in lines))
    f.paste(sheet.img.rotate(-2, expand=True, resample=Image.BICUBIC), 660, 1030, shadow=True)
    f.sources += sheet.sources
    # right: a pinned sketch of the tent, a coffee ring and the UNSOLVED stamp
    ph = kit.Frame(720, 620, (0xF4, 0xED, 0xE0)); pd = ph.draw()
    pd.rectangle([30, 30, 690, 500], fill=(0x22, 0x2E, 0x29))
    pd.polygon([(120, 470), (360, 110), (600, 470)], fill=PARCH)
    for i in range(0, 6, 2):
        x0 = 120 + i * 80
        pd.polygon([(x0, 470), (360, 110), (x0 + 80, 470)], fill=CRAN)
    pd.polygon([(300, 470), (360, 290), (420, 470)], fill=(0xF6, 0xD0, 0x7A))
    ph.text((360, 530), "Judges' Tent, 20:40", font("hand", 64), INK, anchor="ma")
    f.paste(ph.img.rotate(5, expand=True, resample=Image.BICUBIC), 1520, 780, shadow=True)
    f.sources += ph.sources
    d = f.draw()
    d.rectangle([1490, 400, 1560, 470], fill=(0xB8, 0xB8, 0xB0))          # paperclip
    d.ellipse([1300, 1250, 1680, 1630], outline=(0x6A, 0x4A, 0x30), width=16)   # coffee ring
    stamp = kit.Frame(760, 240, (0, 0, 0)); stamp.img = Image.new("RGBA", (760, 240), (0, 0, 0, 0))
    sdd = stamp.draw()
    sdd.rounded_rectangle([10, 10, 750, 230], radius=20, outline=CRAN + (230,), width=14)
    sdd.text((380, 120), "UNSOLVED", font=font("black", 124), fill=CRAN + (230,), anchor="mm")
    stamp.note("drawn", "stamp", "UNSOLVED")
    f.paste(stamp.img.rotate(-12, expand=True, resample=Image.BICUBIC), 1560, 1400, shadow=False)
    f.sources += stamp.sources
    vignette(f, 170); grain(f, 14)
    d = f.draw()
    d.rectangle([0, 1840, W, W], fill=(0x0E, 0x0A, 0x07))
    f.text((W / 2, 1880), "The file is now yours.", font("display", 120), PARCH, anchor="ma")
    return f

# ---------------------------------------------------------------- C. The last 40 minutes
def concept_c():
    f = new(NIGHT); grad(f, (0x08, 0x0C, 0x0A), (0x16, 0x24, 0x1E))
    d = f.draw()
    for x in range(0, W, 120):
        d.line([(x, 0), (x, W)], fill=(0x13, 0x1C, 0x18), width=2)
    for y in range(0, W, 120):
        d.line([(0, y), (W, y)], fill=(0x13, 0x1C, 0x18), width=2)
    # big clock at 20:05
    cx, cy, r = W / 2, 720, 420
    glow(f, cx, cy, r * 1.1, (0xF6, 0xD0, 0x7A), 40)
    d = f.draw()
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(0x10, 0x18, 0x14), outline=MUST, width=14)
    for k in range(60):
        a = math.pi / 30 * k - math.pi / 2
        r0 = r * (0.84 if k % 5 == 0 else 0.9)
        d.line([(cx + math.cos(a) * r0, cy + math.sin(a) * r0), (cx + math.cos(a) * r * 0.95, cy + math.sin(a) * r * 0.95)],
               fill=PARCH if k % 5 == 0 else (0x6B, 0x75, 0x70), width=10 if k % 5 == 0 else 4)
    def hand(frac, length, width, col):
        a = 2 * math.pi * frac - math.pi / 2
        d.line([(cx, cy), (cx + math.cos(a) * length, cy + math.sin(a) * length)], fill=col, width=width)
    hand((8 + 5 / 60) / 12, r * 0.5, 26, PARCH)        # 8 o'clock (20:05)
    hand(5 / 60, r * 0.78, 16, PARCH)
    hand(38 / 60, r * 0.86, 6, CRAN)                    # sweeping second hand
    d.ellipse([cx - 26, cy - 26, cx + 26, cy + 26], fill=CRAN)
    # timeline of what the case file tells you
    y = 1400
    d.line([(160, y), (W - 160, y)], fill=(0x6B, 0x75, 0x70), width=6)
    marks = [(0.12, "19:48", "a receipt is printed", MUST), (0.5, "20:05", "someone leaves the tent", PARCH),
             (0.88, "20:40", "the judge is found", CRAN)]
    for t, tm, what, col in marks:
        x = 160 + (W - 320) * t
        d.ellipse([x - 26, y - 26, x + 26, y + 26], fill=col)
        f.text((x, y - 120), tm, font("black", 76), col, anchor="ma")
        f.text((x, y + 60), what, font("bold", 46), (0xC9, 0xC2, 0xB2), anchor="ma")
    grain(f, 16); vignette(f, 190)
    f.text((W / 2, 1720), "40 minutes. 6,000 suspects.", font("display", 116), PARCH, anchor="ma")
    f.text((W / 2, 1890), "Can you rebuild the night?", font("display-italic", 84), MUST, anchor="ma")
    return f

# ---------------------------------------------------------------- D. Paper-cut shadow theatre
def concept_d():
    f = new((0x12, 0x1E, 0x18)); grad(f, (0x0E, 0x18, 0x13), (0x24, 0x38, 0x2F))
    glow(f, W / 2, 1150, 900, (0xF6, 0xD0, 0x7A), 45)

    def layer(draw_fn, shadow=26, offset=(10, 16)):
        g = Image.new("RGBA", (W, W), (0, 0, 0, 0)); draw_fn(ImageDraw.Draw(g))
        sh = Image.new("RGBA", (W, W), (0, 0, 0, 0))
        sh.putalpha(g.split()[3].point(lambda a: 150 if a else 0))
        sh = sh.filter(ImageFilter.GaussianBlur(shadow))
        f.img.alpha_composite(sh, offset); f.img.alpha_composite(g)

    tone = [(0x3C, 0x55, 0x49), (0x8F, 0x9E, 0x92), (0xD9, 0xD0, 0xBE), PARCH]
    def moon(d):
        d.ellipse([1500, 220, 1760, 480], fill=tone[3]); d.ellipse([1560, 190, 1820, 450], fill=(0, 0, 0, 0))
    layer(moon, 30)
    def hills(d):
        pts = [(0, W)] + [(x, 1250 + math.sin(x / 300) * 70) for x in range(0, W + 1, 40)] + [(W, W)]
        d.polygon(pts, fill=tone[0])
    layer(hills)
    def stalls(d):
        for x in range(-40, W, 330):
            d.rectangle([x, 1150, x + 250, 1450], fill=tone[1])
            d.polygon([(x - 30, 1150), (x + 125, 1020), (x + 280, 1150)], fill=tone[1])
            for i in range(5):
                d.pieslice([x - 30 + i * 62, 1120, x + 32 + i * 62, 1182], 0, 180, fill=tone[1])
    layer(stalls)
    def tree_and_tent(d):
        for i in range(4):
            tw = 520 - i * 100; ty = 1500 - i * 190
            d.polygon([(560 - tw / 2, ty), (560 + tw / 2, ty), (560, ty - 330)], fill=tone[2])
        d.rectangle([530, 1500, 590, 1560], fill=tone[2])
        d.polygon([(1250, 1560), (1560, 1080), (1870, 1560)], fill=tone[2])
    layer(tree_and_tent)
    def star(d):
        pts = []
        for i in range(10):
            a = -math.pi / 2 + i * math.pi / 5; rr = 70 if i % 2 == 0 else 30
            pts.append((560 + math.cos(a) * rr, 690 + math.sin(a) * rr))
        d.polygon(pts, fill=MUST)
    layer(star, 16)
    def front(d):
        pts = [(0, W)] + [(x, 1580 + math.sin(x / 210 + 1) * 40) for x in range(0, W + 1, 40)] + [(W, W)]
        d.polygon(pts, fill=tone[3])
        rng = random.Random(3)
        for k in range(30):                            # cut-out snowflakes (dots)
            x, y, r = rng.uniform(0, W), rng.uniform(80, 1000), rng.uniform(6, 16)
            d.ellipse([x - r, y - r, x + r, y + r], fill=tone[3])
    layer(front)
    # the only colour: the figure's hat, walking away from the tent (lit flap)
    d = f.draw()
    d.polygon([(1500, 1560), (1560, 1350), (1620, 1560)], fill=(0xF6, 0xD0, 0x7A))
    def fig(d):
        silhouette(d, 1020, 1620, 0.62, body=(0x1C, 0x2A, 0x23))
    layer(fig, 18)
    d = f.draw()
    for k in range(6):
        px = 1150 + k * 60; py = 1650 - k * 12
        d.ellipse([px - 14, py - 7, px + 14, py + 7], fill=(0xC9, 0xBF, 0xAA))
    f.text((W / 2, 1760), "Six thousand footprints in the snow.", font("display-italic", 92), GREEN, anchor="ma")
    f.text((W / 2, 1900), "Only one leads out of the tent.", font("display", 104), CRAN, anchor="ma")
    return f

# ---------------------------------------------------------------- E. Inspector Wren (cozy cartoon)
def concept_e():
    fr = CF.frame3_wren()
    return fr

CONCEPTS = [("A-noir-snowfall", concept_a), ("B-redacted-case-file", concept_b),
            ("C-last-40-minutes", concept_c), ("D-paper-cut-shadows", concept_d),
            ("E-inspector-wren-cartoon", concept_e)]

def build(outdir):
    os.makedirs(outdir, exist_ok=True)
    bad = CL.forbidden(); rep = []; thumbs = []
    for name, fn in CONCEPTS:
        fr = fn()
        img = fr.img.convert("RGB").resize((OUT, OUT), Image.LANCZOS)
        img.save(os.path.join(outdir, f"concept-{name}.png"), optimize=True)
        rep.append((name, kit.spoiler_scan(fr.sources, bad)))
        thumbs.append((name, img.resize((400, 400), Image.LANCZOS)))
    sheet = Image.new("RGB", (5 * 416 + 16, 500), (0x10, 0x18, 0x14))
    sd = ImageDraw.Draw(sheet)
    for i, (name, t) in enumerate(thumbs):
        sheet.paste(t, (16 + i * 416, 16))
        sd.text((16 + i * 416 + 200, 440), name.split("-", 1)[0], font=font("display", 44), fill=PARCH, anchor="ma")
    sheet.save(os.path.join(outdir, "concepts-overview.png"), optimize=True)
    return rep

if __name__ == "__main__":
    for name, hits in build(sys.argv[1] if len(sys.argv) > 1 else "concepts"):
        print(name, "spoiler hits:", len(hits))
