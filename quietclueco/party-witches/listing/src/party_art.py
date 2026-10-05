"""Poster art for Murder at the Lantern Supper, in the old horror-film one-sheet look of case No. 3
(poster.py) and the same palette: plum, aubergine, amethyst, candle gold, moon parchment, sage.

New pieces for the party: Larkwell Hall on its hill with lit windows and a bell tower, a winding
path of guests' lanterns, a figure seen from behind carrying a lantern (no face), the green glass.
Everything is drawn with code.

    hall_scene(fr, k, ...)      the night scene (sky, moon, crows, hill, hall, lantern path)
    cover_poster(W, H)          portrait one-sheet for the PDF covers
    hero_poster()               the square listing image 01
"""
import math, random
from PIL import Image, ImageDraw, ImageFilter
import kit
from poster import (PLUM, AUB, AMETHYST, GOLD, MOON, SAGE, NIGHT, GOLD_DARK, hf, fit, layer, gradient, glow, grain,
                    tracked, halftone, aged, deco_frame, star, moon, figure_from_behind, crescent_pin, crow, title_word,
                    stub, bez)

S = 2000
WINDOW = (0xFF, 0xD3, 0x7A)

def hall(img, cx, base, s, col=NIGHT, lit=True, seed=6):
    """Larkwell Hall: a long house with three gables, tall chimneys and a bell tower over the porch."""
    d = ImageDraw.Draw(img)
    w = s * 6.2
    x0, x1 = cx - w / 2, cx + w / 2
    d.rectangle([x0, base - s * 1.6, x1, base], fill=col)                              # body
    for gx in (x0 + s * 0.2, cx - s * 0.9, x1 - s * 2.0):                               # gables
        d.polygon([(gx, base - s * 1.6), (gx + s * 0.9, base - s * 2.7), (gx + s * 1.8, base - s * 1.6)], fill=col)
    for chx in (x0 + s * 0.5, x1 - s * 0.8, cx + s * 1.2):                             # chimneys
        d.rectangle([chx, base - s * 2.6, chx + s * 0.28, base - s * 1.5], fill=col)
    tx = cx + s * 0.0                                                                   # bell tower
    d.rectangle([tx - s * 0.45, base - s * 3.4, tx + s * 0.45, base - s * 1.4], fill=col)
    d.polygon([(tx - s * 0.6, base - s * 3.4), (tx, base - s * 4.4), (tx + s * 0.6, base - s * 3.4)], fill=col)
    d.ellipse([tx - s * 0.08, base - s * 4.6, tx + s * 0.08, base - s * 4.44], fill=col)
    if not lit:
        return
    rng = random.Random(seed)
    lay, ld = layer(img.size)
    wins = [(tx - s * 0.16, base - s * 3.1, tx + s * 0.16, base - s * 2.7)]            # the bell opening
    for row, yy in enumerate((base - s * 1.3, base - s * 0.8)):
        for k in range(9):
            xx = x0 + s * 0.35 + k * (w - s * 0.7) / 9
            if abs(xx - tx) < s * 0.6 or rng.random() < 0.25:
                continue
            wins.append((xx, yy, xx + s * 0.32, yy + s * 0.38))
    for gx in (x0 + s * 0.2, cx - s * 0.9, x1 - s * 2.0):
        wins.append((gx + s * 0.75, base - s * 2.25, gx + s * 1.05, base - s * 1.85))
    for (a, b, c_, e) in wins:
        ld.rectangle([a - s * 0.18, b - s * 0.18, c_ + s * 0.18, e + s * 0.18], fill=GOLD + (90,))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(s * 0.18)))
    d = ImageDraw.Draw(img)
    for (a, b, c_, e) in wins:
        d.rectangle([a, b, c_, e], fill=WINDOW)
        d.line([((a + c_) / 2, b), ((a + c_) / 2, e)], fill=col, width=max(1, int(s * 0.03)))
    d.rectangle([tx - s * 0.22, base - s * 0.7, tx + s * 0.22, base], fill=WINDOW)    # the open front door
    return (tx, base - s * 2.9)

def lantern(img, x, y, s, col=NIGHT, light=GOLD):
    """A small hand lantern hanging from a short pole or handle, lit."""
    glow(img, [x - s * 1.6, y - s * 1.6, x + s * 1.6, y + s * 1.6], light, 120, s * 0.7)
    d = ImageDraw.Draw(img)
    d.rectangle([x - s * 0.36, y - s * 0.5, x + s * 0.36, y + s * 0.5], fill=col)
    d.rectangle([x - s * 0.24, y - s * 0.36, x + s * 0.24, y + s * 0.36], fill=WINDOW)
    d.polygon([(x - s * 0.46, y - s * 0.5), (x, y - s * 0.86), (x + s * 0.46, y - s * 0.5)], fill=col)
    d.arc([x - s * 0.2, y - s * 1.12, x + s * 0.2, y - s * 0.7], 180, 360, fill=col, width=max(1, int(s * 0.08)))

def lantern_path(img, pts, s, seed=3):
    """Guests' lanterns bobbing up the hill path: small warm dots with halos, smaller further away."""
    rng = random.Random(seed)
    lay, ld = layer(img.size)
    for i, (x, y) in enumerate(pts):
        r = s * (0.35 + 0.65 * i / max(1, len(pts) - 1))
        ld.ellipse([x - r * 2.6, y - r * 2.6, x + r * 2.6, y + r * 2.6], fill=GOLD + (70,))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(s * 0.5)))
    d = ImageDraw.Draw(img)
    for i, (x, y) in enumerate(pts):
        r = s * (0.35 + 0.65 * i / max(1, len(pts) - 1))
        d.ellipse([x - r, y - r, x + r, y + r], fill=WINDOW)

def hill(d, W, base, top, col):
    pts = [(0, base)] + bez((0, base), (W * 0.25, top + (base - top) * 0.15), (W * 0.65, top - (base - top) * 0.05),
                            (W, base - (base - top) * 0.35), 40) + [(W, base + 400), (0, base + 400)]
    d.polygon(pts, fill=col)

def green_glass(img, x, y, s):
    """Rowena's green glass, a little stemmed goblet, glinting."""
    glow(img, [x - s * 1.4, y - s * 1.6, x + s * 1.4, y + s * 1.2], SAGE, 110, s * 0.5)
    d = ImageDraw.Draw(img)
    gl = (0x4E, 0x7A, 0x52)
    d.polygon([(x - s * 0.55, y - s * 1.2), (x + s * 0.55, y - s * 1.2), (x + s * 0.4, y - s * 0.35),
               (x + s * 0.1, y - s * 0.15), (x - s * 0.1, y - s * 0.15), (x - s * 0.4, y - s * 0.35)], fill=gl)
    d.rectangle([x - s * 0.06, y - s * 0.2, x + s * 0.06, y + s * 0.35], fill=gl)
    d.ellipse([x - s * 0.42, y + s * 0.28, x + s * 0.42, y + s * 0.46], fill=gl)
    d.polygon([(x - s * 0.42, y - s * 1.1), (x - s * 0.3, y - s * 1.1), (x - s * 0.22, y - s * 0.5), (x - s * 0.3, y - s * 0.45)],
              fill=(0xB8, 0xD8, 0xB0))
    d.ellipse([x - s * 0.55, y - s * 1.3, x + s * 0.55, y - s * 1.1], outline=(0x9C, 0xC4, 0x96), width=max(1, int(s * 0.05)))

def figure_with_lantern(img, cx, base, s):
    """The figure in the pointed hat, from behind, a lantern held out at arm's length."""
    pin = figure_from_behind(img, cx, base, s, NIGHT)
    d = ImageDraw.Draw(img)
    d.polygon([(cx + s * 0.62, base - s * 0.7), (cx + s * 1.3, base - s * 0.95), (cx + s * 1.34, base - s * 0.82),
               (cx + s * 0.7, base - s * 0.5)], fill=NIGHT)                                 # arm
    lantern(img, cx + s * 1.36, base - s * 0.6, s * 0.22)
    return pin

def hall_scene(fr, k, moon_c, moon_r, horizon, hall_c, hall_s, crows=True, path=True):
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
    d = ImageDraw.Draw(img)
    if crows:
        for x, y, s_, fl, fc in ((0.18, -0.55, 40, 0.2, 1), (0.28, -0.75, 28, 0.6, 1), (0.82, -0.35, 36, 0.3, -1),
                                 (0.72, -0.8, 26, 0.0, -1)):
            crow(d, W * x, moon_c[1] + moon_r * y * 1.6, s_ * k * 1.3, NIGHT, fl, fc)
    hill(d, W, horizon + 120 * k, hall_c[1] - 10 * k, (0x24, 0x16, 0x33))
    hall(img, hall_c[0], hall_c[1], hall_s)
    if path:
        pts = []
        for i in range(11):
            t = i / 10
            x = hall_c[0] + math.sin(t * 3.4 + 0.4) * W * 0.16 * t - W * 0.02
            y = hall_c[1] + 20 * k + (horizon + 180 * k - hall_c[1]) * t ** 1.3
            pts.append((x, y))
        lantern_path(img, pts, 9 * k)

def big_stub(f, cx, cy, label, bg, fg, w, h):
    """A bigger ticket stub than case No. 3's, so the badge reads on a 250 px thumbnail."""
    d = f.draw()
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], radius=16, fill=bg)
    for sx in (-1, 1):
        d.ellipse([cx + sx * w / 2 - 26, cy - 26, cx + sx * w / 2 + 26, cy + 26], fill=(0x1A, 0x10, 0x26))
    for yy in range(int(cy - h / 2 + 12), int(cy + h / 2 - 8), 18):
        d.line([(cx - w / 2 + 50, yy), (cx - w / 2 + 50, yy + 9)], fill=fg, width=4)
    fnt = fit(label, "bebas", 120, w - 120)
    d.text((cx + 22, cy + 4), label, font=fnt, fill=fg, anchor="mm")
    f.note("drawn", "badge", label)

# ---------------------------------------------------------------- the PDF cover (portrait)
def cover_poster(W=1200, H=1800, record=None):
    k = W / 1200
    f = kit.Frame(int(W), int(H), PLUM); img = f.img
    horizon = H * 0.5
    mc = (W * 0.62, H * 0.2); mr = 190 * k
    hall_scene(f, k, mc, mr, horizon, (W * 0.5, horizon - 20 * k), 70 * k)
    gradient(img, (0x22, 0x14, 0x30), PLUM, (0, horizon + 140 * k, W, H))
    pin = figure_with_lantern(img, W * 0.3, horizon + 330 * k, 120 * k)
    crescent_pin(img, pin[0], pin[1], 9 * k)
    green_glass(img, W * 0.8, horizon + 300 * k, 60 * k)
    tracked(f, W / 2, 62 * k, "QUIETCLUECO PRESENTS", hf("cinzel", 34 * k, 700), MOON, 9 * k)
    y = horizon + 380 * k
    tracked(f, W / 2, y, "MURDER AT THE", hf("cinzel", 76 * k, 800), MOON, 10 * k)
    big = fit("LANTERN SUPPER", "abril", 170 * k, W - 120 * k)
    title_word(f, "LANTERN SUPPER", W / 2, y + 92 * k, big, depth=14 * k, k=k)
    y2 = y + 92 * k + big.size * 1.2
    tracked(f, W / 2, y2, "A MORROWMERE MURDER MYSTERY PARTY", fit("A MORROWMERE MURDER MYSTERY PARTY", "bebas", 60 * k,
                                                                    W - 260 * k, track=5 * k), GOLD, 5 * k)
    tracked(f, W / 2, y2 + 82 * k, "6–12 PLAYERS  ·  2–3 HOURS  ·  HOST CAN PLAY", hf("oswald", 32 * k, 500), MOON, 4 * k)
    deco_frame(f, 34 * k, k)
    aged(img, 3, border=int(20 * k))
    if record:
        for _, _, t in f.sources:
            record(t)
    return f

# ---------------------------------------------------------------- listing image 01 (square)
def hero_poster():
    k = 1.6
    f = kit.Frame(S, S, PLUM); img = f.img
    horizon = 900
    mc = (S * 0.66, 380); mr = 260
    hall_scene(f, k, mc, mr, horizon, (S * 0.5, 820), 112)
    pin = figure_with_lantern(img, 420, 1220, 200)
    crescent_pin(img, pin[0], pin[1], 14)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 1180, S, S], fill=PLUM)
    gradient(img, (0x22, 0x14, 0x30), PLUM, (0, 1180, S, 1260))
    green_glass(img, S - 300, 1170, 70)
    tracked(f, S / 2, 66, "QUIETCLUECO PRESENTS", hf("cinzel", 50, 700), MOON, 12)
    y = 1200
    tracked(f, S / 2, y, "MURDER AT THE", hf("cinzel", 112, 800), MOON, 14)
    big = fit("LANTERN SUPPER", "abril", 260, S - 160)
    title_word(f, "LANTERN SUPPER", S / 2, y + 130, big, depth=20, k=k)
    by = y + 130 + big.size * 1.12 + 10
    bw, bh = 1500, 150
    d = f.draw()
    for sx in (-1, 1):
        e = S / 2 + sx * bw / 2
        d.polygon([(e + sx * 80, by + 12), (e, by + 12), (e, by + bh + 12), (e + sx * 80, by + bh + 12),
                   (e + sx * 42, by + bh / 2 + 12)], fill=GOLD_DARK)
    d.rectangle([S / 2 - bw / 2, by, S / 2 + bw / 2, by + bh], fill=GOLD)
    tracked(f, S / 2, by + 6, "MURDER MYSTERY PARTY", hf("bebas", 148), PLUM, 10)
    tracked(f, S / 2, S - 122, "A MORROWMERE MYSTERY  ·  HOST CAN PLAY  ·  2–3 HOURS", hf("cinzel", 40, 700), GOLD, 6)
    big_stub(f, 400, 225, "6–12 PLAYERS", GOLD, PLUM, w=600, h=170)
    big_stub(f, S - 440, 225, "PRINTABLE PARTY KIT", AMETHYST, MOON, w=700, h=170)
    deco_frame(f, 36, 1.5)
    aged(img, 5, border=24)
    return f

if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "previews")
    os.makedirs(out, exist_ok=True)
    hero_poster().img.convert("RGB").save(os.path.join(out, "hero.jpg"), quality=88)
    cover_poster(1275, 1650).img.convert("RGB").save(os.path.join(out, "cover_letter.jpg"), quality=88)
    print("ok")
