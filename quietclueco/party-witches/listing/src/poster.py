"""The poster look for Full Moon over Morrowmere: an old horror-mystery one-sheet (1940s-50s
lithograph feel) in the case palette. Everything is drawn with code from silhouettes and objects
only: a full moon, a figure in a pointed hat seen from behind (no face), crows, the standing
stones, a cauldron, a hand holding a candle, moon phases. Fonts are open-licence (SIL OFL)
files in fonts_horror/.

    cover_poster(W, H)  -> portrait one-sheet used as the PDF cover (any page shape)
    hero_poster()       -> the square listing image 01
"""
import math, os, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import kit

HERE = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(HERE, "fonts_horror")
S = 2000

# palette (from the brief)
PLUM = (0x2B, 0x1B, 0x3D); AUB = (0x4A, 0x2C, 0x5E); AMETHYST = (0x8E, 0x5B, 0xB5)
GOLD = (0xE3, 0xA6, 0x4B); MOON = (0xED, 0xE6, 0xD6); SAGE = (0x8F, 0xA3, 0x82)
NIGHT = (0x14, 0x0C, 0x1E)        # plum pushed to near-black for silhouettes
GOLD_DARK = (0x8A, 0x5A, 0x1E)

FILES = {"bebas": "BebasNeue-Regular.ttf", "cinzel": "Cinzel[wght].ttf", "fell": "IMFeENrm28P.ttf",
         "fell-it": "IMFeENit28P.ttf", "oswald": "Oswald[wght].ttf", "abril": "AbrilFatface-Regular.ttf"}
def hf(name, size, wght=None):
    f = ImageFont.truetype(os.path.join(FD, FILES[name]), int(size))
    if wght:
        f.set_variation_by_axes([wght])
    return f

def fit(text, name, size, maxw, wght=None, track=0):
    while size > 12:
        f = hf(name, size, wght)
        if f.getlength(text) + track * (len(text) - 1) <= maxw:
            return f
        size -= 2
    return hf(name, size, wght)

def layer(size):
    im = Image.new("RGBA", size, (0, 0, 0, 0)); return im, ImageDraw.Draw(im)

def gradient(img, top, bottom, box=None):
    d = ImageDraw.Draw(img); x0, y0, x1, y1 = box or (0, 0, img.width, img.height)
    for y in range(int(y0), int(y1)):
        t = (y - y0) / max(1, y1 - y0 - 1)
        d.line([(x0, y), (x1, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip(top, bottom)))

def glow(img, box, col, a, blur, kind="ellipse"):
    lay, d = layer(img.size)
    (d.ellipse if kind == "ellipse" else d.polygon)(box, fill=col + (a,))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(blur)))

def grain(img, amount=22):
    n = Image.effect_noise(img.size, 60).convert("L")
    img.alpha_composite(Image.merge("RGBA", (n, n, n, Image.new("L", img.size, amount))))

def tracked(fr, cx, y, text, fnt, fill, track, stroke=0, stroke_fill=None):
    """Letter-spaced single line centred on cx; records the text for the spoiler scan."""
    d = fr.draw()
    widths = [fnt.getlength(ch) for ch in text]
    total = sum(widths) + track * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        d.text((x, y), ch, font=fnt, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
        x += w + track
    fr.note("drawn", "text", text)
    return total

# ---------------------------------------------------------------- textures
def halftone(img, box, col, step, seed=1, max_r=None, falloff=None):
    """Old-print halftone dots inside box; dot size follows falloff(x, y) in 0..1."""
    lay, d = layer(img.size); x0, y0, x1, y1 = box
    max_r = max_r or step * 0.42
    y = y0
    row = 0
    while y < y1:
        x = x0 + (step / 2 if row % 2 else 0)
        while x < x1:
            k = falloff(x, y) if falloff else 1.0
            r = max_r * k
            if r > 0.6:
                d.ellipse([x - r, y - r, x + r, y + r], fill=col)
            x += step
        y += step * 0.87; row += 1
    img.alpha_composite(lay)

def aged(img, seed=3, border=26):
    """Old one-sheet: pale edge, fold creases, foxing, a warm tint and grain."""
    w, h = img.size; d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w - 1, h - 1], outline=(0xE9, 0xE1, 0xCF), width=border)
    lay, ld = layer(img.size)
    ld.line([(w / 2, 0), (w / 2, h)], fill=(255, 255, 255, 30), width=3)
    for y in (h / 3, 2 * h / 3):
        ld.line([(0, y), (w, y)], fill=(255, 255, 255, 26), width=3)
    rng = random.Random(seed)
    for _ in range(70):
        x, y, r = rng.uniform(0, w), rng.uniform(0, h), rng.uniform(4, 18)
        ld.ellipse([x - r, y - r, x + r, y + r], fill=(0xB0, 0x90, 0x50, 22))
    img.alpha_composite(lay)
    img.alpha_composite(Image.new("RGBA", img.size, (0xD8, 0xB8, 0x78, 16)))
    grain(img, 24)

def deco_frame(fr, inset, k, col=GOLD):
    """Double rule border with stepped art-deco corners and small stars."""
    d = fr.draw(); w, h = fr.img.size; i = inset
    d.rectangle([i, i, w - i, h - i], outline=col, width=max(2, int(5 * k)))
    j = i + 16 * k
    d.rectangle([j, j, w - j, h - j], outline=col, width=max(1, int(2 * k)))
    for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        cx = i if sx > 0 else w - i; cy = i if sy > 0 else h - i
        for n in range(3):
            o = (26 + n * 14) * k
            d.line([(cx, cy + sy * o), (cx + sx * o, cy + sy * o), (cx + sx * o, cy)], fill=col, width=max(1, int(2 * k)))
        star(d, cx + sx * 70 * k, cy + sy * 70 * k, 13 * k, col)

def star(d, x, y, r, col, points=4):
    pts = []
    for n in range(points * 2):
        a = -math.pi / 2 + math.pi * n / points
        rr = r if n % 2 == 0 else r * 0.3
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    d.polygon(pts, fill=col)

# ---------------------------------------------------------------- objects and silhouettes
def moon(img, cx, cy, r, seed=2):
    glow(img, [cx - r * 1.9, cy - r * 1.9, cx + r * 1.9, cy + r * 1.9], GOLD, 70, r * 0.5)
    glow(img, [cx - r * 1.25, cy - r * 1.25, cx + r * 1.25, cy + r * 1.25], MOON, 120, r * 0.18)
    lay, d = layer(img.size)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=MOON + (255,))
    rng = random.Random(seed)
    for _ in range(7):                                                # a few small craters
        a = rng.uniform(0, 2 * math.pi); q = rng.uniform(0.2, 0.75) * r; rr = rng.uniform(0.02, 0.05) * r
        x, y = cx + math.cos(a) * q, cy + math.sin(a) * q
        d.ellipse([x - rr, y - rr * 0.85, x + rr, y + rr * 0.85], fill=(0xD9, 0xCF, 0xBA, 110))
    for x, y, rr in ((-0.3, -0.2, 0.26), (0.18, 0.12, 0.2), (-0.1, 0.35, 0.16)):
        lay2, d2 = layer(img.size)
        d2.ellipse([cx + x * r - rr * r, cy + y * r - rr * r * 0.8, cx + x * r + rr * r, cy + y * r + rr * r * 0.8], fill=(0xDC, 0xD2, 0xBE, 120))
        img.alpha_composite(lay2.filter(ImageFilter.GaussianBlur(r * 0.05)))
    img.alpha_composite(lay)
    # halftone shading on the lower-left limb, like a two-colour print
    mask = Image.new("L", img.size, 0); ImageDraw.Draw(mask).ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    dots, _ = layer(img.size)
    halftone(dots, (cx - r, cy - r, cx + r, cy + r), (0xB9, 0x9E, 0x7A, 200), max(6, r * 0.045),
             falloff=lambda x, y: max(0.0, min(1.0, ((cx - x) * 0.6 + (y - cy) * 0.8) / r - 0.15)))
    dots.putalpha(Image.composite(dots.split()[3], Image.new("L", img.size, 0), mask))
    img.alpha_composite(dots)

def bez(p0, p1, p2, p3, n=24):
    out = []
    for i in range(n + 1):
        t = i / n; u = 1 - t
        out.append((u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
                    u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1]))
    return out

def figure_shape(cx, base, s):
    """Polygons for a figure seen from behind: cloak and shoulders, the back of the head and a
    tall pointed hat with a bent tip. No face is ever drawn."""
    cloak = ([(cx - s * 0.9, base)] + bez((cx - s * 0.9, base), (cx - s * 0.84, base - s * 0.55),
                                          (cx - s * 0.62, base - s * 0.86), (cx - s * 0.16, base - s * 0.94))
             + bez((cx + s * 0.16, base - s * 0.94), (cx + s * 0.62, base - s * 0.86),
                   (cx + s * 0.84, base - s * 0.55), (cx + s * 0.9, base)))
    head = [cx - s * 0.24, base - s * 1.5, cx + s * 0.24, base - s * 0.9]
    brim = [cx - s * 0.8, base - s * 1.44, cx + s * 0.8, base - s * 1.26]
    left = bez((cx - s * 0.36, base - s * 1.38), (cx - s * 0.24, base - s * 1.9), (cx - s * 0.1, base - s * 2.35),
               (cx + s * 0.12, base - s * 2.62))
    tip = bez((cx + s * 0.12, base - s * 2.62), (cx + s * 0.3, base - s * 2.8), (cx + s * 0.5, base - s * 2.72),
              (cx + s * 0.62, base - s * 2.58), 10)
    back = bez((cx + s * 0.62, base - s * 2.58), (cx + s * 0.4, base - s * 2.62), (cx + s * 0.22, base - s * 2.5),
               (cx + s * 0.2, base - s * 2.25), 10) + bez((cx + s * 0.2, base - s * 2.25), (cx + s * 0.22, base - s * 1.9),
                                                         (cx + s * 0.3, base - s * 1.6), (cx + s * 0.38, base - s * 1.38), 12)
    hat = left + tip + back
    band = [(cx - s * 0.36, base - s * 1.38), (cx + s * 0.38, base - s * 1.38), (cx + s * 0.35, base - s * 1.5),
            (cx - s * 0.33, base - s * 1.5)]
    return cloak, head, brim, hat, band

def figure_from_behind(img, cx, base, s, col, rim=MOON, band=AUB):
    """Draw the figure with a soft moonlight rim so it separates from the rooftops."""
    cloak, head, brim, hat, bandp = figure_shape(cx, base, s)
    lay, d = layer(img.size)
    g = s * 0.035
    d.polygon(cloak, fill=rim + (255,)); d.ellipse([head[0] - g, head[1] - g, head[2] + g, head[3] + g], fill=rim + (255,))
    d.ellipse([brim[0] - g, brim[1] - g, brim[2] + g, brim[3] + g], fill=rim + (255,)); d.polygon(hat, fill=rim + (255,))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(s * 0.05)))
    d = ImageDraw.Draw(img)
    d.polygon(cloak, fill=col); d.ellipse(head, fill=col); d.ellipse(brim, fill=col); d.polygon(hat, fill=col)
    d.polygon(bandp, fill=band)
    return (cx + s * 0.2, base - s * 1.44)                # where the crescent pin sits on the band

def crescent_pin(img, x, y, r):
    glow(img, [x - r * 3, y - r * 3, x + r * 3, y + r * 3], (0xFF, 0xF4, 0xDC), 150, r * 1.2)
    lay, d = layer(img.size)
    d.ellipse([x - r, y - r, x + r, y + r], fill=(0xEE, 0xEE, 0xF4, 255))
    d.ellipse([x - r * 0.45, y - r * 1.1, x + r * 1.3, y + r * 0.6], fill=(0, 0, 0, 0))
    img.alpha_composite(lay)

def crow(d, x, y, s, col, flap=0.0, facing=1):
    """A crow in flight, seen from below: small head, wedge tail and two long wings in a shallow
    M with fingered primaries. flap (-1..1) raises or lowers the wing tips."""
    lift = 0.55 - 0.75 * flap                     # tip height relative to the shoulders
    for sd in (-1, 1):
        sh = (x + sd * s * 0.12, y - s * 0.04)
        el = (x + sd * s * 0.55, y - s * (0.18 + lift * 0.45))
        tip = (x + sd * s * 1.15, y - s * (0.05 + lift))
        w = [sh, el, tip]
        for kf in range(4):                       # fingered trailing edge, from tip back to the body
            w.append((tip[0] - sd * s * (0.08 + kf * 0.1), tip[1] + s * (0.16 + kf * 0.04)))
            w.append((tip[0] - sd * s * (0.12 + kf * 0.1), tip[1] + s * (0.08 + kf * 0.05)))
        w += [(x + sd * s * 0.5, y + s * 0.06 - s * lift * 0.2), (x + sd * s * 0.1, y + s * 0.16)]
        d.polygon(w, fill=col)
    d.ellipse([x - s * 0.14, y - s * 0.12, x + s * 0.14, y + s * 0.3], fill=col)          # body
    d.ellipse([x - s * 0.1 + facing * s * 0.02, y - s * 0.26, x + s * 0.1 + facing * s * 0.02, y - s * 0.06], fill=col)  # head
    d.polygon([(x - s * 0.08, y + s * 0.26), (x + s * 0.08, y + s * 0.26), (x + s * 0.16, y + s * 0.48),
               (x - s * 0.16, y + s * 0.48)], fill=col)                                    # tail

def village(d, base, x0, x1, s, col, seed=4):
    """Rooftops, a church tower and the Hob Stones along a horizon line."""
    rng = random.Random(seed); x = x0
    d.rectangle([x0, base, x1, base + s * 0.4], fill=col)
    while x < x1:
        w = rng.uniform(0.7, 1.4) * s; h = rng.uniform(0.5, 1.0) * s
        d.rectangle([x, base - h, x + w, base + 2], fill=col)
        d.polygon([(x - s * 0.08, base - h), (x + w / 2, base - h - rng.uniform(0.4, 0.8) * s), (x + w + s * 0.08, base - h)], fill=col)
        if rng.random() < 0.5:
            d.rectangle([x + w * 0.7, base - h - s * 0.55, x + w * 0.82, base - h - s * 0.1], fill=col)
        x += w + rng.uniform(0.05, 0.4) * s
    tx = x0 + (x1 - x0) * 0.78                                          # church tower
    d.rectangle([tx, base - s * 2.6, tx + s * 0.7, base], fill=col)
    d.polygon([(tx - s * 0.08, base - s * 2.6), (tx + s * 0.35, base - s * 3.6), (tx + s * 0.78, base - s * 2.6)], fill=col)

def stones(d, cx, base, s, col, n=7):
    for k in range(n):
        x = cx + (k - (n - 1) / 2) * s * 0.75; h = s * (0.9 + 0.35 * ((k * 37) % 5) / 4)
        w = s * 0.32
        d.polygon([(x - w, base), (x - w * 1.08, base - h * 0.6), (x - w * 0.5, base - h), (x + w * 0.6, base - h * 0.96),
                   (x + w, base - h * 0.5), (x + w * 0.95, base)], fill=col)

def cauldron(img, cx, base, s, steam=2.2):
    d = ImageDraw.Draw(img)
    glow(img, [cx - s * 1.0, base - s * 1.5, cx + s * 1.0, base - s * 0.7], GOLD, 140, s * 0.25)
    for dx in (-0.6, 0.0, 0.6):
        d.rectangle([cx + dx * s - s * 0.08, base - s * 0.25, cx + dx * s + s * 0.08, base], fill=NIGHT)
    d.ellipse([cx - s * 0.9, base - s * 1.3, cx + s * 0.9, base - s * 0.15], fill=NIGHT)
    d.rounded_rectangle([cx - s * 1.0, base - s * 1.36, cx + s * 1.0, base - s * 1.12], radius=s * 0.1, fill=NIGHT)
    d.ellipse([cx - s * 0.84, base - s * 1.42, cx + s * 0.84, base - s * 1.2], fill=GOLD)
    lay, ld = layer(img.size)                                           # steam
    for k in range(3):
        x = cx + (k - 1) * s * 0.4; pts = []
        for i in range(40):
            t = i / 39
            pts.append((x + math.sin(t * 7 + k) * s * 0.22, base - s * 1.4 - t * s * steam))
        ld.line(pts, fill=MOON + (90,), width=max(3, int(s * 0.12)), joint="curve")
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(s * 0.06)))

def candle_hand(img, cx, base, s):
    """A hand (a simple sleeve-and-fist silhouette) raising a lit candle from the bottom edge."""
    glow(img, [cx - s * 1.2, base - s * 4.2, cx + s * 1.2, base - s * 1.8], GOLD, 150, s * 0.6)
    d = ImageDraw.Draw(img)
    d.rectangle([cx - s * 0.16, base - s * 3.2, cx + s * 0.16, base - s * 1.7], fill=MOON)        # candle
    d.polygon([(cx, base - s * 3.95), (cx + s * 0.16, base - s * 3.5), (cx, base - s * 3.24),
               (cx - s * 0.16, base - s * 3.5)], fill=(0xFF, 0xD9, 0x8A))                         # flame
    d.polygon([(cx - s * 0.62, base), (cx - s * 0.5, base - s * 1.3), (cx + s * 0.5, base - s * 1.3),
               (cx + s * 0.66, base)], fill=NIGHT)                                                  # sleeve
    d.rounded_rectangle([cx - s * 0.42, base - s * 2.05, cx + s * 0.42, base - s * 1.25], radius=s * 0.22, fill=NIGHT)  # fist
    for k in range(3):
        d.line([(cx - s * 0.36, base - s * (1.9 - k * 0.2)), (cx + s * 0.1, base - s * (1.9 - k * 0.2))], fill=AUB, width=max(2, int(s * 0.04)))

def moon_phases(fr, cx, y, r, gap, col=MOON, dark=AUB):
    """Seven phases, new to full to new, in a row centred on cx."""
    d = fr.draw(); n = 7
    for k in range(n):
        x = cx + (k - 3) * (2 * r + gap)
        d.ellipse([x - r, y - r, x + r, y + r], fill=col)
        p = k / 3 - 1                       # -1 .. 1, 0 = full
        if abs(p) > 0.01:
            off = (1 - abs(p)) * 2 * r * (1 if p < 0 else -1)
            d.ellipse([x - r + off, y - r, x + r + off, y + r], fill=dark)
        d.ellipse([x - r, y - r, x + r, y + r], outline=col, width=max(1, int(r * 0.12)))

def title_word(fr, text, cx, y, fnt, fill=GOLD, shadow=AUB, depth=14, outline=NIGHT, inline=MOON, k=1.0):
    """Big poster lettering: a stepped block shadow, a dark keyline and a thin inline highlight."""
    d = fr.draw(); w = fnt.getlength(text); x = cx - w / 2
    for e in range(int(depth), 0, -1):
        d.text((x + e * 0.8, y + e), text, font=fnt, fill=shadow)
    d.text((x, y), text, font=fnt, fill=fill, stroke_width=max(2, int(5 * k)), stroke_fill=outline)
    lay, ld = layer(fr.img.size)
    ld.text((x - max(1, 2 * k), y - max(1, 2 * k)), text, font=fnt, fill=inline + (110,))
    m = Image.new("L", fr.img.size, 0); ImageDraw.Draw(m).text((x, y), text, font=fnt, fill=255)
    lay.putalpha(Image.composite(lay.split()[3], Image.new("L", fr.img.size, 0), m.filter(ImageFilter.MinFilter(5))))
    fr.img.alpha_composite(lay)
    fr.note("drawn", "text", text)
    return w

def sky(fr, k, moon_c, moon_r, horizon):
    img = fr.img; W, H = img.size
    gradient(img, (0x1A, 0x10, 0x26), AUB, (0, 0, W, horizon))
    gradient(img, AUB, PLUM, (0, horizon, W, H))
    halftone(img, (0, 0, W, horizon), AMETHYST + (40,), 22 * k,
             falloff=lambda x, y: max(0.0, 1 - math.hypot(x - moon_c[0], y - moon_c[1]) / (moon_r * 3.2)))
    rng = random.Random(9); d = fr.draw()
    for _ in range(int(70 * W / 1200)):
        x, y = rng.uniform(0, W), rng.uniform(0, horizon * 0.9)
        if math.hypot(x - moon_c[0], y - moon_c[1]) > moon_r * 1.4:
            star(d, x, y, rng.uniform(2, 6) * k, MOON + (rng.randint(90, 200),))
    moon(img, moon_c[0], moon_c[1], moon_r)

# ---------------------------------------------------------------- the cover (portrait, any size)
def cover_poster(W=1200, H=1800):
    k = W / 1200
    f = kit.Frame(int(W), int(H), PLUM)
    img = f.img
    horizon = H * 0.52
    mc = (W * 0.5, horizon - 330 * k); mr = 300 * k
    sky(f, k, mc, mr, horizon)
    d = ImageDraw.Draw(img)
    for x, y, s_, fl in ((W * 0.2, mc[1] - 230 * k, 46 * k, 0.1), (W * 0.31, mc[1] - 250 * k, 32 * k, 0.5),
                         (W * 0.8, mc[1] - 120 * k, 40 * k, 0.3), (W * 0.71, mc[1] - 260 * k, 28 * k, 0.0),
                         (W * 0.62, mc[1] - 330 * k, 22 * k, 0.6)):
        crow(d, x, y, s_ * 1.3, NIGHT, fl, 1 if x < W / 2 else -1)
    village(d, horizon, 0, W, 70 * k, NIGHT)
    stones(d, W * 0.22, horizon + 4 * k, 80 * k, NIGHT)
    gradient(img, NIGHT, PLUM, (0, horizon + 26 * k, W, H))
    d = ImageDraw.Draw(img)
    fig_base = horizon + 40 * k
    pin = figure_from_behind(img, mc[0] + 10 * k, fig_base, 180 * k, NIGHT)
    crescent_pin(img, pin[0], pin[1], 13 * k)
    d = ImageDraw.Draw(img); d.rectangle([0, fig_base, W, fig_base + 4 * k], fill=NIGHT)
    gradient(img, NIGHT, PLUM, (0, fig_base, W, fig_base + 120 * k))
    cauldron(img, W * 0.15, H - 120 * k, 74 * k, steam=1.1)
    candle_hand(img, W * 0.86, H - 96 * k, 46 * k)
    d = ImageDraw.Draw(img)
    # top lines
    tracked(f, W / 2, 62 * k, "QUIETCLUECO PRESENTS", hf("cinzel", 34 * k, 700), MOON, 9 * k)
    moon_phases(f, W / 2, 140 * k, 15 * k, 18 * k)
    # title
    y = horizon + 60 * k
    tracked(f, W / 2, y, "FULL MOON OVER", hf("cinzel", 74 * k, 800), MOON, 10 * k)
    big = fit("MORROWMERE", "abril", 230 * k, W - 150 * k)
    title_word(f, "MORROWMERE", W / 2, y + 96 * k, big, depth=16 * k, k=k)
    y2 = y + 96 * k + big.size * 1.22
    tracked(f, W / 2, y2, "A HALLOWEEN MYSTERY IN 18 CLUES", fit("A HALLOWEEN MYSTERY IN 18 CLUES", "bebas", 64 * k, W - 300 * k, track=6 * k), GOLD, 6 * k)
    d.line([(W * 0.2, y2 + 84 * k), (W * 0.8, y2 + 84 * k)], fill=GOLD, width=max(1, int(2 * k)))
    tracked(f, W / 2, y2 + 104 * k, "6,000 VISITORS  ·  ONE COVEN  ·  ONE KILLER", hf("oswald", 34 * k, 500), MOON, 4 * k)
    tracked(f, W / 2, H - 112 * k, "PRINTABLE CASE FILE  ·  PRINT OR PLAY ON iPAD", hf("oswald", 28 * k, 400), MOON, 3 * k)
    deco_frame(f, 34 * k, k)
    aged(img, 3, border=int(20 * k))
    return f

# ---------------------------------------------------------------- listing image 01 (square)
def hero_poster(badges=("PRINTABLE", "iPad")):
    k = 1.6
    f = kit.Frame(S, S, PLUM); img = f.img
    horizon = 980
    mc = (S * 0.5, 560); mr = 360
    sky(f, k, mc, mr, horizon)
    d = ImageDraw.Draw(img)
    for x, y, s_, fl, fc in ((440, 330, 84, 0.2, 1), (600, 230, 56, 0.7, 1), (1560, 440, 76, 0.4, -1),
                             (1420, 290, 52, 0.0, -1), (1290, 190, 40, 0.8, -1)):
        crow(d, x, y, s_, NIGHT, fl, fc)
    village(d, horizon, 0, S, 96, NIGHT)
    stones(d, 330, horizon + 6, 120, NIGHT)
    pin = figure_from_behind(img, mc[0] + 12, horizon + 30, 250, NIGHT)
    crescent_pin(img, pin[0], pin[1], 18)
    d = ImageDraw.Draw(img)
    d.rectangle([0, horizon + 40, S, S], fill=PLUM)
    gradient(img, (0x1A, 0x10, 0x26), PLUM, (0, horizon + 40, S, horizon + 140))
    # top lines
    tracked(f, S / 2, 70, "QUIETCLUECO PRESENTS", hf("cinzel", 50, 700), MOON, 12)
    # title
    y = horizon + 70
    tracked(f, S / 2, y, "FULL MOON OVER", hf("cinzel", 118, 800), MOON, 16)
    big = fit("MORROWMERE", "abril", 330, S - 190)
    title_word(f, "MORROWMERE", S / 2, y + 140, big, depth=22, k=k)
    # FIND THE KILLER banner
    by = y + 140 + big.size * 1.1 + 20
    bw, bh = 1180, 150
    d = f.draw()
    d.polygon([(S / 2 - bw / 2 - 70, by + 12), (S / 2 - bw / 2, by + 12), (S / 2 - bw / 2, by + bh + 12),
               (S / 2 - bw / 2 - 70, by + bh + 12), (S / 2 - bw / 2 - 36, by + bh / 2 + 12)], fill=GOLD_DARK)
    d.polygon([(S / 2 + bw / 2 + 70, by + 12), (S / 2 + bw / 2, by + 12), (S / 2 + bw / 2, by + bh + 12),
               (S / 2 + bw / 2 + 70, by + bh + 12), (S / 2 + bw / 2 + 36, by + bh / 2 + 12)], fill=GOLD_DARK)
    d.rectangle([S / 2 - bw / 2, by, S / 2 + bw / 2, by + bh], fill=GOLD)
    tracked(f, S / 2, by + 4, "FIND THE KILLER", hf("bebas", 150), PLUM, 12)
    tracked(f, S / 2, by + bh + 40, "6,000 SUSPECTS  ·  6 DOCUMENTS  ·  1 KILLER", hf("oswald", 66, 600), MOON, 5)
    tracked(f, S / 2, S - 118, "NOW SHOWING  ·  A HALLOWEEN MYSTERY IN 18 CLUES", hf("cinzel", 40, 700), GOLD, 7)
    # ticket-stub badges in the top corners
    for (cx, label, bg, fg) in ((300, badges[0], GOLD, PLUM), (S - 300, badges[1], AMETHYST, MOON)):
        stub(f, cx, 210, label, bg, fg)
    deco_frame(f, 36, 1.5)
    aged(img, 5, border=24)
    return f

def stub(f, cx, cy, label, bg, fg, w=330, h=118):
    """A cinema ticket stub: notched ends and a perforated line."""
    d = f.draw()
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], radius=14, fill=bg)
    for sx in (-1, 1):
        d.ellipse([cx + sx * w / 2 - 22, cy - 22, cx + sx * w / 2 + 22, cy + 22], fill=(0x1A, 0x10, 0x26))
    for yy in range(int(cy - h / 2 + 10), int(cy + h / 2 - 6), 16):
        d.line([(cx - w / 2 + 44, yy), (cx - w / 2 + 44, yy + 8)], fill=fg, width=3)
    fnt = fit(label, "oswald", 64, w - 110, 600)
    d.text((cx + 20, cy - 2), label, font=fnt, fill=fg, anchor="mm")
    f.note("drawn", "badge", label)
