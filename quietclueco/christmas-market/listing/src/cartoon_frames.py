"""Cartoon 'Christmas detective' concept frames for a 14.9 s listing video.
Flat colours, thick ink outlines, all drawn by code (no photos, no AI images).
Hero: Inspector Wren, the case's detective, drawn as a little wren bird.

    python3 cartoon_frames.py OUTDIR
"""
import math, os, random, sys
from PIL import Image, ImageDraw, ImageFilter
import kit
from kit import GREEN, CRAN, PARCH, MUST, INK, DEEP, PARCH_DARK, font
import case_listing as CL

OUT = 1080
SS = 1                      # design units are px on the 2160 canvas
W = OUT * 2                 # draw at 2x, downscale to 1080 for smooth edges
OL = 8                      # outline width
BROWN = (0x8A, 0x5A, 0x3C); BROWN_D = (0x5E, 0x3C, 0x28); BELLY = (0xE8, 0xC9, 0x9B)
SKY_TOP = (0x10, 0x1C, 0x17); SNOW = (0xF7, 0xF3, 0xEA); SNOW_SH = (0xDD, 0xE3, 0xE0)
CORK = (0xB9, 0x8B, 0x5E); WOOD = (0x6B, 0x45, 0x2C); WOOD_L = (0x86, 0x5A, 0x3A)
GLOW = (0xF6, 0xD0, 0x7A)

def new(bg=GREEN):
    return kit.Frame(W, W, bg)

def d_(f):
    return ImageDraw.Draw(f.img)

def sky(f, top=SKY_TOP, bottom=GREEN):
    d = d_(f)
    for y in range(W):
        t = y / W
        d.line([(0, y), (W, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip(top, bottom)))

def glow(f, x, y, r, col, a=110):
    g = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse([x - r, y - r, x + r, y + r], fill=col + (a,))
    f.img.alpha_composite(g.filter(ImageFilter.GaussianBlur(r * 0.45)))

def snow(f, n, seed, y0=0, y1=None):
    kit.snow_field(f, n, seed, (0, y0, W, y1 or W), alpha=(120, 230), size=(5 * SS, 14 * SS))

def ground(f, y, col=SNOW):
    d = d_(f)
    pts = [(0, W)] + [(x, y + math.sin(x / 260) * 22 * SS + math.sin(x / 90) * 6 * SS) for x in range(0, W + 1, 20)] + [(W, W)]
    d.polygon(pts, fill=col, outline=INK)
    d.line(pts[1:-1], fill=INK, width=OL)

def stall(f, x, y, w, h, awning=CRAN, lit=True):
    d = d_(f)
    d.rectangle([x, y, x + w, y + h], fill=(0x2E, 0x46, 0x3B), outline=INK, width=OL)
    if lit:
        d.rectangle([x + w * 0.18, y + h * 0.42, x + w * 0.82, y + h * 0.82], fill=GLOW, outline=INK, width=OL // 2)
        glow(f, x + w / 2, y + h * 0.6, w * 0.5, GLOW, 60)
    d.polygon([(x - w * 0.12, y), (x + w / 2, y - h * 0.55), (x + w * 1.12, y)], fill=(0x1F, 0x30, 0x28), outline=INK)
    d.line([(x - w * 0.12, y), (x + w / 2, y - h * 0.55), (x + w * 1.12, y)], fill=INK, width=OL)
    n = 5; aw = w * 1.24 / n
    for i in range(n):
        xx = x - w * 0.12 + i * aw
        d.pieslice([xx, y - aw * 0.45, xx + aw, y + aw * 0.55], 0, 180, fill=awning if i % 2 == 0 else PARCH, outline=INK, width=OL // 2)
    # snow cap
    d.polygon([(x - w * 0.1, y - 2), (x + w / 2, y - h * 0.53), (x + w * 1.1, y - 2), (x + w / 2, y - h * 0.4)], fill=SNOW)

def fir(f, x, y, w, h):
    d = d_(f)
    for i in range(4):
        tw = w * (1 - i * 0.2); ty = y - i * h * 0.21
        pts = [(x - tw / 2, ty), (x + tw / 2, ty), (x, ty - h * 0.36)]
        d.polygon(pts, fill=(0x1B, 0x4D, 0x36), outline=INK)
        d.line(pts + [pts[0]], fill=INK, width=OL)
        d.polygon([(x - tw * 0.36, ty - h * 0.02), (x, ty - h * 0.3), (x + tw * 0.36, ty - h * 0.02), (x, ty - h * 0.12)], fill=SNOW)
    d.rectangle([x - w * 0.07, y, x + w * 0.07, y + h * 0.1], fill=BROWN_D, outline=INK, width=OL)
    kit.star5_pil = None
    star(f, x, y - h * 0.86, h * 0.07, MUST)
    rng = random.Random(4)
    for _ in range(14):
        bx = x + rng.uniform(-w * 0.35, w * 0.35); by = y - rng.uniform(h * 0.05, h * 0.62)
        if abs(bx - x) < (w / 2) * (1 - (y - by) / (h * 0.9)):
            c = [CRAN, MUST, PARCH][rng.randint(0, 2)]
            d.ellipse([bx - 10 * SS, by - 10 * SS, bx + 10 * SS, by + 10 * SS], fill=c, outline=INK, width=OL // 2)

def star(f, x, y, r, col):
    d = d_(f)
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    glow(f, x, y, r * 2.2, GLOW, 90)
    d.polygon(pts, fill=col, outline=INK)
    d.line(pts + [pts[0]], fill=INK, width=OL // 2)

def lights(f, x0, x1, y, sag, n):
    d = d_(f)
    pts = [(x0 + (x1 - x0) * t / 60, y + sag * math.sin(math.pi * t / 60)) for t in range(61)]
    d.line(pts, fill=INK, width=OL // 2)
    for i in range(1, n):
        t = i / n; xx = x0 + (x1 - x0) * t; yy = y + sag * math.sin(math.pi * t) + 14 * SS
        c = [MUST, CRAN, PARCH][i % 3]
        glow(f, xx, yy, 26 * SS, c, 70)
        d.ellipse([xx - 9 * SS, yy - 12 * SS, xx + 9 * SS, yy + 12 * SS], fill=c, outline=INK, width=OL // 2)

def wren(f, x, y, s, look=1, magnifier=True, hat=True):
    """Inspector Wren: round brown bird, cocked tail, green scarf, little hat, magnifying glass."""
    d = d_(f)
    # tail (cocked up, wren-style)
    tail = [(x - look * s * 0.55, y - s * 0.05), (x - look * s * 1.05, y - s * 0.75), (x - look * s * 0.8, y - s * 0.85), (x - look * s * 0.35, y - s * 0.25)]
    d.polygon(tail, fill=BROWN_D, outline=INK); d.line(tail + [tail[0]], fill=INK, width=OL)
    # legs
    for k in (-0.15, 0.15):
        d.line([(x + k * s, y + s * 0.5), (x + k * s, y + s * 0.78)], fill=INK, width=OL)
        d.line([(x + k * s, y + s * 0.78), (x + k * s + look * s * 0.12, y + s * 0.8)], fill=INK, width=OL)
    # body
    d.ellipse([x - s * 0.62, y - s * 0.5, x + s * 0.62, y + s * 0.6], fill=BROWN, outline=INK, width=OL)
    d.ellipse([x - s * 0.2 + look * s * 0.12, y - s * 0.1, x + s * 0.45 + look * s * 0.12, y + s * 0.55], fill=BELLY)
    # wing
    wing = [x - look * s * 0.1, y - s * 0.05, x - look * s * 0.1 - look * s * 0.55, y + s * 0.4]
    d.ellipse([min(wing[0], wing[2]), wing[1], max(wing[0], wing[2]), wing[3]], fill=BROWN_D, outline=INK, width=OL)
    # head
    hx, hy = x + look * s * 0.28, y - s * 0.55
    d.ellipse([hx - s * 0.38, hy - s * 0.36, hx + s * 0.38, hy + s * 0.36], fill=BROWN, outline=INK, width=OL)
    # eye stripe + eye
    d.arc([hx - s * 0.2, hy - s * 0.22, hx + s * 0.34, hy + s * 0.08], 200, 340, fill=PARCH, width=OL)
    ex = hx + look * s * 0.12
    d.ellipse([ex - s * 0.09, hy - s * 0.1, ex + s * 0.09, hy + s * 0.08], fill=INK)
    d.ellipse([ex - s * 0.03 + look * s * 0.02, hy - s * 0.07, ex + s * 0.02 + look * s * 0.02, hy - s * 0.02], fill=(255, 255, 255))
    # beak
    bx = hx + look * s * 0.36
    beak = [(bx, hy - s * 0.04), (bx + look * s * 0.28, hy + s * 0.02), (bx, hy + s * 0.08)]
    d.polygon(beak, fill=MUST, outline=INK); d.line(beak + [beak[0]], fill=INK, width=OL // 2)
    # blush
    d.ellipse([hx - s * 0.02, hy + s * 0.08, hx + s * 0.12, hy + s * 0.16], fill=(0xD9, 0x8A, 0x86))
    # scarf (brand green) with tail
    d.rounded_rectangle([hx - s * 0.36, hy + s * 0.22, hx + s * 0.36, hy + s * 0.38], radius=s * 0.06, fill=GREEN, outline=INK, width=OL)
    sc = [(hx - look * s * 0.2, hy + s * 0.3), (hx - look * s * 0.45, hy + s * 0.75), (hx - look * s * 0.28, hy + s * 0.78), (hx - look * s * 0.05, hy + s * 0.34)]
    d.polygon(sc, fill=GREEN, outline=INK); d.line(sc + [sc[0]], fill=INK, width=OL)
    for k in range(3):
        yy = hy + s * (0.5 + k * 0.08)
        d.line([(hx - look * s * (0.3 + k * 0.04), yy), (hx - look * s * (0.18 + k * 0.04), yy)], fill=MUST, width=OL // 2)
    if hat:   # soft round detective hat with a mustard band
        d.ellipse([hx - s * 0.46, hy - s * 0.36, hx + s * 0.46, hy - s * 0.2], fill=DEEP, outline=INK, width=OL)
        d.chord([hx - s * 0.3, hy - s * 0.66, hx + s * 0.3, hy - s * 0.05], 180, 360, fill=DEEP, outline=INK, width=OL)
        d.rectangle([hx - s * 0.29, hy - s * 0.38, hx + s * 0.29, hy - s * 0.3], fill=MUST)
    if magnifier:
        mx, my, r = x + look * s * 0.95, y - s * 0.1, s * 0.34
        d.line([(x + look * s * 0.4, y + s * 0.25), (mx - look * r * 0.7, my + r * 0.7)], fill=WOOD, width=int(s * 0.1))
        d.ellipse([mx - r, my - r, mx + r, my + r], fill=(0xDC, 0xEB, 0xEA), outline=INK, width=int(s * 0.07))
        d.arc([mx - r * 0.65, my - r * 0.65, mx + r * 0.2, my + r * 0.2], 190, 260, fill=(255, 255, 255), width=int(s * 0.05))

def caption(f, text, sub=None, y=None, bg=PARCH, fg=GREEN):
    """Chunky cartoon caption card at the bottom."""
    d = d_(f)
    y = y or W - 330 * SS
    d.rounded_rectangle([90, y, W - 90, y + (280 if sub else 190)], radius=40, fill=bg, outline=INK, width=OL)
    fnt = kit.fit_font(f, text, "display", 104, W - 260)
    f.text((W / 2, y + 36), text, fnt, fg, anchor="ma", align="center")
    if sub:
        f.text((W / 2, y + 180), sub, font("black", 60), CRAN, anchor="ma")

def burst(f, x, y, r, col=MUST, n=14):
    d = d_(f)
    pts = []
    for i in range(n * 2):
        a = i * math.pi / n
        rr = r if i % 2 == 0 else r * 0.72
        pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
    d.polygon(pts, fill=col, outline=INK); d.line(pts + [pts[0]], fill=INK, width=OL)

# ---------------------------------------------------------------- the five frames
def frame1_market():
    """0.0-2.8s: camera glides down from the sky into the snowy market."""
    f = new(); sky(f)
    d = d_(f)
    d.ellipse([1560 * SS, 150 * SS, 1740 * SS, 330 * SS], fill=PARCH, outline=INK, width=OL)
    glow(f, 1650 * SS, 240 * SS, 160 * SS, PARCH, 50)
    snow(f, 70, 1, 0, W)
    lights(f, -40, W + 40, 120 * SS, 110 * SS, 16)
    for i, x in enumerate([40, 470, 1310, 1740]):
        stall(f, x, 1080, 380, 440, [CRAN, GREEN, CRAN, MUST][i])
    fir(f, W / 2, 1620 * SS, 620 * SS, 1250 * SS)
    ground(f, 1560 * SS)
    snow(f, 40, 2, 0, W)
    caption(f, "Ember Square · 23 December", "20:05, the last night of the market", y=W - 360 * SS)
    return f

def frame2_tent():
    """2.8-5.6s: the tent flap twitches; a red bobble hat slips out into the snow."""
    f = new(); sky(f, (0x14, 0x22, 0x1B), (0x2A, 0x42, 0x37))
    snow(f, 60, 3, 0, W)
    d = d_(f)
    # tent
    tx, ty = 820 * SS, 1500 * SS
    tent = [(tx - 620 * SS, ty), (tx, ty - 820 * SS), (tx + 620 * SS, ty)]
    for i in range(8):
        a0 = tx - 620 * SS + i * 155 * SS
        pass
    d.polygon(tent, fill=PARCH, outline=INK)
    for i in range(6):                               # cranberry stripes
        x0 = tx - 620 * SS + i * 2 * 1240 * SS / 12
        x1 = x0 + 1240 * SS / 12
        stripe = [(x0, ty), (tx, ty - 820 * SS), (x1, ty)]
        d.polygon(stripe, fill=CRAN)
    d.line(tent + [tent[0]], fill=INK, width=OL)
    # open flap with warm light
    flap = [(tx - 150 * SS, ty), (tx, ty - 470 * SS), (tx + 150 * SS, ty)]
    glow(f, tx, ty - 180 * SS, 330 * SS, GLOW, 120)
    d.polygon(flap, fill=GLOW, outline=INK); d.line(flap + [flap[0]], fill=INK, width=OL)
    d.polygon([(tx + 150 * SS, ty), (tx, ty - 470 * SS), (tx + 300 * SS, ty - 60 * SS)], fill=PARCH_DARK, outline=INK)
    d.line([(tx + 150 * SS, ty), (tx, ty - 470 * SS), (tx + 300 * SS, ty - 60 * SS), (tx + 150 * SS, ty)], fill=INK, width=OL)
    # sign
    d.rounded_rectangle([tx - 260 * SS, ty - 700 * SS, tx + 260 * SS, ty - 590 * SS], radius=20 * SS, fill=GREEN, outline=INK, width=OL)
    f.text((tx, ty - 670 * SS), "JUDGES", font("black", 60 * SS), PARCH, anchor="ma")
    ground(f, ty - 20 * SS)
    # the figure from behind: a round dark coat and the red bobble hat, no face
    fx, fy = 1640 * SS, 1560 * SS
    coat = [(fx - 95, fy - 300), (fx + 95, fy - 300), (fx + 150, fy + 60), (fx - 150, fy + 60)]
    d.polygon(coat, fill=(0x3B, 0x3F, 0x55), outline=INK); d.line(coat + [coat[0]], fill=INK, width=OL)
    d.line([(fx, fy - 290), (fx, fy + 55)], fill=INK, width=OL // 2)
    for bx in (fx - 150, fx + 150):                  # boots
        d.rounded_rectangle([bx - 10 if bx < fx else bx - 70, fy + 50, bx + 70 if bx < fx else bx + 10, fy + 95], radius=18, fill=INK)
    d.ellipse([fx - 85, fy - 420, fx + 85, fy - 270], fill=(0x6B, 0x4A, 0x36), outline=INK, width=OL)   # back of head / hair
    d.rounded_rectangle([fx - 115, fy - 330, fx + 115, fy - 270], radius=26, fill=GREEN, outline=INK, width=OL)  # scarf
    d.chord([fx - 100 * SS, fy - 470 * SS, fx + 100 * SS, fy - 290 * SS], 180, 360, fill=CRAN, outline=INK, width=OL)
    d.rectangle([fx - 100 * SS, fy - 390 * SS, fx + 100 * SS, fy - 360 * SS], fill=(0x7C, 0x1F, 0x2C), outline=INK, width=OL // 2)
    d.ellipse([fx - 45 * SS, fy - 540 * SS, fx + 45 * SS, fy - 450 * SS], fill=CRAN, outline=INK, width=OL)
    for k in range(5):                              # footprints back to the tent
        px = fx - 230 * SS - k * 150 * SS; py = fy + 90 * SS + (k % 2) * 36 * SS
        d.ellipse([px - 26 * SS, py - 14 * SS, px + 26 * SS, py + 14 * SS], fill=SNOW_SH, outline=INK, width=OL // 3)
    d.text((fx + 150 * SS, fy - 520 * SS), "?", font=font("display", 150 * SS), fill=MUST, stroke_width=OL, stroke_fill=INK)
    snow(f, 30, 4, 0, W)
    caption(f, "Someone slipped out of the Judges’ Tent…", y=W - 300 * SS)
    return f

def frame3_wren():
    """5.6-8.4s: Inspector Wren hops in and peers through the magnifier at the torn receipt."""
    f = new(); sky(f, (0x1C, 0x2E, 0x26), (0x33, 0x4E, 0x42))
    snow(f, 50, 5, 0, W)
    ground(f, 1300 * SS)
    d = d_(f)
    # torn receipt lying in the snow
    rx, ry = 1180 * SS, 1180 * SS
    rec = Image.new("RGBA", (560 * SS, 720 * SS), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rec)
    pts = [(0, 60 * SS)] + [(i * 40 * SS, (60 if i % 2 == 0 else 20) * SS) for i in range(15)] + [(560 * SS, 60 * SS), (560 * SS, 720 * SS), (0, 720 * SS)]
    rd.polygon(pts, fill=(255, 255, 255), outline=INK)
    rd.line(pts + [pts[0]], fill=INK, width=OL)
    mono = kit.ImageFont.truetype(os.path.join(kit.FONT_DIR, "CourierPrime-Bold.ttf"), 44 * SS)
    for i, line in enumerate(["EMBER SQUARE", "23/12  19:48", "1 x SPICED", "APPLE PUNCH", "MERRY CHRISTMAS"]):
        rd.text((280 * SS, 130 * SS + i * 105 * SS), line, font=mono, fill=INK, anchor="ma")
    rec = rec.rotate(-10, expand=True, resample=Image.BICUBIC)
    f.img.alpha_composite(rec, (int(rx - rec.width / 2 + 180 * SS), int(ry - rec.height / 2)))
    f.note("drawn", "receipt", "EMBER SQUARE 23/12 19:48 1 x SPICED APPLE PUNCH MERRY CHRISTMAS")
    # the wren with her magnifier over the time
    wren(f, 620 * SS, 1180 * SS, 330 * SS, look=1)
    # magnified "19:48" bubble
    burst(f, 1550 * SS, 520 * SS, 240 * SS)
    f.text((1550 * SS, 440 * SS), "19:48", font("display", 120 * SS), INK, anchor="ma")
    snow(f, 25, 6, 0, W)
    caption(f, "Inspector Wren needs your help", y=W - 290 * SS)
    return f

def frame4_board():
    """8.4-11.6s: the clue board; red string snaps between pins, a marker crosses out suspects."""
    f = new(CORK)
    d = d_(f)
    rng = random.Random(8)
    for _ in range(900):                                    # cork speckle
        x, y = rng.uniform(0, W), rng.uniform(0, W)
        d.ellipse([x, y, x + 5 * SS, y + 4 * SS], fill=(0xA3, 0x77, 0x4E))
    d.rectangle([0, 0, W, W], outline=WOOD, width=40 * SS)
    cards = [(330, 330, -6, "map"), (840, 280, 4, "receipt"), (1400, 340, -3, "snow"),
             (500, 820, 5, "coach"), (1060, 800, -5, "note"), (1620, 860, 6, "talk")]
    pins = []
    for (cx, cy, ang, kind) in cards:
        cx *= SS; cy *= SS
        card = kit.Frame(360 * SS, 300 * SS, PARCH)
        cd = ImageDraw.Draw(card.img)
        cd.rectangle([0, 0, 360 * SS - 1, 300 * SS - 1], outline=INK, width=OL)
        icon_on(card, kind)
        im = card.img.rotate(ang, expand=True, resample=Image.BICUBIC)
        f.paste(im, cx, cy, shadow=True, shadow_strength=90)
        f.sources += card.sources
        pins.append((cx, cy - 130 * SS))
    for a, b in [(0, 1), (1, 2), (0, 3), (3, 4), (4, 5), (1, 4), (2, 5)]:     # red string
        (x0, y0), (x1, y1) = pins[a], pins[b]
        d.line([(x0, y0), ((x0 + x1) / 2, (y0 + y1) / 2 + 30 * SS), (x1, y1)], fill=CRAN, width=6 * SS, joint="curve")
    for x, y in pins:
        d.ellipse([x - 22 * SS, y - 22 * SS, x + 22 * SS, y + 22 * SS], fill=CRAN, outline=INK, width=OL // 2)
    # the lineup of suspects (anonymous silhouettes), most crossed out
    y = 1380 * SS
    for i in range(9):
        x = 220 * SS + i * 215 * SS
        d.ellipse([x - 55 * SS, y - 150 * SS, x + 55 * SS, y - 40 * SS], fill=(0x3A, 0x3A, 0x42), outline=INK, width=OL)
        d.chord([x - 90 * SS, y - 40 * SS, x + 90 * SS, y + 150 * SS], 180, 360, fill=(0x3A, 0x3A, 0x42), outline=INK, width=OL)
        d.text((x, y - 125 * SS), "?", font=font("black", 70 * SS), fill=PARCH, anchor="ma")
        if i not in (3, 6):
            d.line([(x - 80, y - 150), (x + 80, y + 110)], fill=CRAN, width=22)
            d.line([(x + 80, y - 150), (x - 80, y + 110)], fill=CRAN, width=22)
    d.rounded_rectangle([90 * SS, 1640 * SS, W - 90 * SS, 1960 * SS], radius=40 * SS, fill=GREEN, outline=INK, width=OL)
    f.text((W / 2, 1680 * SS), "6,000 suspects · 18 clues", font("display", 92 * SS), PARCH, anchor="ma")
    f.text((W / 2, 1830 * SS), "only 1 killer", font("black", 70 * SS), MUST, anchor="ma")
    return f

def icon_on(card, kind):
    d = ImageDraw.Draw(card.img); s = SS
    cx, cy = 180 * s, 150 * s
    if kind == "map":
        d.rectangle([50 * s, 50 * s, 310 * s, 250 * s], fill=(255, 255, 255), outline=INK, width=OL // 2)
        for r in range(3):
            for k in range(5):
                d.rectangle([70 * s + k * 48 * s, 70 * s + r * 60 * s, 104 * s + k * 48 * s, 96 * s + r * 60 * s], fill=CRAN if r % 2 == 0 else GREEN)
        d.ellipse([230 * s, 170 * s, 300 * s, 240 * s], outline=CRAN, width=6 * s)
    elif kind == "receipt":
        d.rectangle([110 * s, 30 * s, 250 * s, 270 * s], fill=(255, 255, 255), outline=INK, width=OL // 2)
        for k in range(6):
            d.line([(130 * s, 70 * s + k * 30 * s), (230 * s, 70 * s + k * 30 * s)], fill=(0x88, 0x80, 0x78), width=5 * s)
    elif kind == "snow":
        kit.snowflake(d, cx, cy, 95 * s, GREEN, 9 * s)
    elif kind == "coach":
        d.rounded_rectangle([60 * s, 90 * s, 300 * s, 210 * s], radius=24 * s, fill=MUST, outline=INK, width=OL // 2)
        for k in range(4):
            d.rectangle([80 * s + k * 52 * s, 110 * s, 120 * s + k * 52 * s, 150 * s], fill=(0xDC, 0xEB, 0xEA), outline=INK, width=3 * s)
        for wx in (110, 250):
            d.ellipse([(wx - 24) * s, 190 * s, (wx + 24) * s, 238 * s], fill=INK)
    elif kind == "note":
        d.rectangle([70 * s, 40 * s, 290 * s, 260 * s], fill=(0xFF, 0xF3, 0xB8), outline=INK, width=OL // 2)
        for k in range(5):
            d.line([(95 * s, 90 * s + k * 34 * s), (265 * s, 90 * s + k * 34 * s)], fill=(0x2A, 0x3A, 0x63), width=4 * s)
    elif kind == "talk":
        d.rounded_rectangle([50 * s, 50 * s, 310 * s, 200 * s], radius=50 * s, fill=(255, 255, 255), outline=INK, width=OL // 2)
        d.polygon([(110 * s, 195 * s), (90 * s, 260 * s), (160 * s, 198 * s)], fill=(255, 255, 255), outline=INK)
        for k in range(3):
            d.ellipse([(125 + k * 50) * s, 110 * s, (145 + k * 50) * s, 130 * s], fill=INK)

def frame5_desk():
    """11.6-14.9s: cozy desk by the window; the case file lands, cocoa steams, title pops in."""
    f = new(GREEN)
    d = d_(f)
    # window with falling snow
    d.rounded_rectangle([1180 * SS, 110 * SS, 2010 * SS, 900 * SS], radius=30 * SS, fill=SKY_TOP, outline=INK, width=OL)
    kit.snow_field(f, 45, 9, (1200 * SS, 130 * SS, 1990 * SS, 880 * SS), alpha=(150, 240), size=(5 * SS, 12 * SS))
    d.line([(1595 * SS, 110 * SS), (1595 * SS, 900 * SS)], fill=WOOD, width=22 * SS)
    d.line([(1180 * SS, 505 * SS), (2010 * SS, 505 * SS)], fill=WOOD, width=22 * SS)
    d.rounded_rectangle([1180 * SS, 110 * SS, 2010 * SS, 900 * SS], radius=30 * SS, outline=INK, width=OL)
    # lamp glow
    glow(f, 520 * SS, 780 * SS, 700 * SS, GLOW, 70)
    # desk
    d.rectangle([0, 1180 * SS, W, W], fill=WOOD, outline=INK, width=OL)
    for k in range(5):
        d.line([(0, (1260 + k * 170) * SS), (W, (1240 + k * 170) * SS)], fill=WOOD_L, width=6 * SS)
    # the real cover of the case file lying on the desk
    L = kit.Pdf(CL.PDF["letter"])
    cover = L.image(0, 1020 * SS)
    f.paste_page(cover, 820 * SS, 1260 * SS, angle=7)
    # mug of cocoa
    mx, my = 1640 * SS, 1420 * SS
    d.rounded_rectangle([mx - 150 * SS, my - 170 * SS, mx + 130 * SS, my + 150 * SS], radius=40 * SS, fill=CRAN, outline=INK, width=OL)
    d.arc([mx + 70 * SS, my - 110 * SS, mx + 230 * SS, my + 60 * SS], -90, 90, fill=INK, width=OL * 3)
    d.arc([mx + 70 * SS, my - 110 * SS, mx + 230 * SS, my + 60 * SS], -90, 90, fill=CRAN, width=OL * 2)
    d.ellipse([mx - 140 * SS, my - 200 * SS, mx + 120 * SS, my - 140 * SS], fill=(0x5A, 0x33, 0x20), outline=INK, width=OL)
    for k in (-60, 0, 60):
        pts = [(mx + k * SS + math.sin(t / 2.2) * 18 * SS, my - 220 * SS - t * 22 * SS) for t in range(12)]
        d.line(pts, fill=PARCH, width=8 * SS, joint="curve")
    # the wren sits on the mug rim, peeking
    wren(f, 1950 * SS, 1180 * SS, 170 * SS, look=-1, magnifier=False)
    # title card
    d.rounded_rectangle([1160, 1600, 2110, 2110], radius=36, fill=PARCH, outline=INK, width=OL)
    f.text((1635, 1630), "Can you find\nthe killer?", font("display", 118), GREEN, anchor="ma", align="center")
    kit.pill(f, (1635, 2010), "Printable + iPad", font("black", 64), MUST, GREEN)
    snow(f, 10, 10, 0, 600 * SS)
    return f

FRAMES = [("1-market", frame1_market), ("2-tent", frame2_tent), ("3-inspector-wren", frame3_wren),
          ("4-clue-board", frame4_board), ("5-cozy-desk", frame5_desk)]

def build(outdir):
    os.makedirs(outdir, exist_ok=True)
    bad = CL.forbidden()
    report, thumbs = [], []
    for name, fn in FRAMES:
        fr = fn()
        img = fr.img.convert("RGB").resize((OUT, OUT), Image.LANCZOS)
        p = os.path.join(outdir, f"cartoon-frame-{name}.png")
        img.save(p, optimize=True)
        report.append((name, kit.spoiler_scan(fr.sources, bad)))
        thumbs.append(img.resize((400, 400), Image.LANCZOS))
    sheet = Image.new("RGB", (5 * 400 + 6 * 16, 432), GREEN)
    for i, t in enumerate(thumbs):
        sheet.paste(t, (16 + i * 416, 16))
    sheet.save(os.path.join(outdir, "cartoon-frames-overview.png"), optimize=True)
    return report

if __name__ == "__main__":
    for name, hits in build(sys.argv[1] if len(sys.argv) > 1 else "cartoon"):
        print(name, "spoiler hits:", len(hits))
