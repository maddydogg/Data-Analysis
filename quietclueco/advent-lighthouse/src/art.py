"""Cosy vintage illustration for The Keeper of Candleholm, drawn entirely with code (Pillow + numpy).

Look: a mid-century picture book or a railway travel poster. A warm, muted palette (cream, sea blue,
rust red, moss green, lamp ochre), flat gouache shapes with a mottled brush texture, linocut strokes
in the sea and on the hills, banded poster skies and a paper grain over everything. Only things,
places and people seen from behind: the tower, the island, boats, the cottage, the stove, parcels and
a figure in a red knitted cap. No faces, no recognisable characters.

Used by the PDF renderer (one vignette per window, the cover) and by the listing kit (mockups, video).
"""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

# ---------------------------------------------------------------- palette
CREAM = (243, 234, 215); PAPER = (250, 245, 234); PAPER2 = (234, 223, 198)
SEA = (35, 70, 90); SEA2 = (47, 96, 116); SEA3 = (78, 124, 138); SEA_L = (128, 163, 167); FOAM = (233, 227, 208)
NIGHT = (28, 44, 60); NIGHT2 = (44, 66, 84); DUSK = (90, 118, 134)
RUST = (181, 69, 47); RUST_D = (132, 46, 32); RUST_L = (214, 120, 88)
MOSS = (107, 123, 75); MOSS_D = (74, 88, 51); MOSS_L = (150, 160, 104)
OCHRE = (215, 165, 72); OCHRE_L = (240, 208, 138); LAMP = (252, 226, 160)
INK = (43, 42, 42); SLATE = (91, 102, 112); STONE = (148, 146, 136); STONE_L = (196, 190, 174)
WHITE = (247, 243, 232); SNOW = (244, 242, 236); PEACH = (232, 196, 158); ROSE = (214, 160, 140)
WOOD = (120, 82, 54); WOOD_L = (160, 116, 78); BRASS = (196, 156, 72); COPPER = (184, 108, 66); TIN = (176, 180, 182)

def lerp(a, b, t):
    return tuple(int(x + (y - x) * t) for x, y in zip(a, b))

def shade(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c)

# ---------------------------------------------------------------- canvas
class Canvas:
    """Draw at `ss` x and downscale, so every edge is smooth."""
    def __init__(self, w, h, ss=2, bg=CREAM):
        self.W, self.H, self.ss = w, h, ss
        self.img = Image.new("RGBA", (w * ss, h * ss), bg + (255,))
        self.d = ImageDraw.Draw(self.img)

    def S(self, *v):
        return [x * self.ss for x in v]

    def P(self, pts):
        return [(x * self.ss, y * self.ss) for x, y in pts]

    def layer(self):
        return Image.new("RGBA", self.img.size, (0, 0, 0, 0))

    def poly(self, pts, col, alpha=255):
        if alpha == 255:
            self.d.polygon(self.P(pts), fill=col)
        else:
            L = self.layer(); ImageDraw.Draw(L).polygon(self.P(pts), fill=col + (alpha,)); self.img.alpha_composite(L)

    def ellipse(self, box, col, alpha=255):
        box = (min(box[0], box[2]), min(box[1], box[3]), max(box[0], box[2]), max(box[1], box[3]))
        if alpha == 255:
            self.d.ellipse(self.S(*box), fill=col)
        else:
            L = self.layer(); ImageDraw.Draw(L).ellipse(self.S(*box), fill=col + (alpha,)); self.img.alpha_composite(L)

    def rect(self, box, col, alpha=255):
        box = (min(box[0], box[2]), min(box[1], box[3]), max(box[0], box[2]), max(box[1], box[3]))
        if alpha == 255:
            self.d.rectangle(self.S(*box), fill=col)
        else:
            L = self.layer(); ImageDraw.Draw(L).rectangle(self.S(*box), fill=col + (alpha,)); self.img.alpha_composite(L)

    def line(self, pts, col, w=1.0, alpha=255):
        if alpha == 255:
            self.d.line(self.P(pts), fill=col, width=max(1, int(w * self.ss)), joint="curve")
        else:
            L = self.layer(); ImageDraw.Draw(L).line(self.P(pts), fill=col + (alpha,), width=max(1, int(w * self.ss)), joint="curve")
            self.img.alpha_composite(L)

    def glow(self, cx, cy, r, col, alpha=120, blur=None):
        g = self.layer(); ImageDraw.Draw(g).ellipse(self.S(cx - r, cy - r, cx + r, cy + r), fill=col + (alpha,))
        self.img.alpha_composite(g.filter(ImageFilter.GaussianBlur((blur or r * 0.6) * self.ss)))

    def finish(self, grain=1.0, seed=1, vignette=0.0):
        im = self.img.resize((self.W, self.H), Image.LANCZOS).convert("RGB")
        return gouache(im, seed=seed, amount=grain, vignette=vignette)

def gouache(im, seed=1, amount=1.0, vignette=0.0):
    """Mottled brush texture, paper fibres and a soft printed edge."""
    w, h = im.size
    rng = np.random.default_rng(seed)
    a = np.asarray(im).astype(np.float32)
    def noise(scale):
        sw, sh = max(2, w // scale), max(2, h // scale)
        n = rng.standard_normal((sh, sw)).astype(np.float32)
        n = np.asarray(Image.fromarray(((n * 40) + 128).clip(0, 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)).astype(np.float32)
        return (n - 128) / 128
    mottled = 0.55 * noise(70) + 0.45 * noise(18)
    fibre = rng.standard_normal((h, w)).astype(np.float32)
    fibre = np.asarray(Image.fromarray(((fibre * 30) + 128).clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))).astype(np.float32)
    fibre = (fibre - 128) / 128
    k = 1 + amount * (0.07 * mottled + 0.045 * fibre)
    a = a * k[..., None]
    if vignette:
        yy, xx = np.mgrid[0:h, 0:w]
        d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
        v = np.clip((d - 0.7) / 0.6, 0, 1)[..., None] * vignette
        a = a * (1 - v) + np.array(PAPER2, np.float32) * v
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))

def smooth(pts, n=10):
    """Catmull-Rom through the points: soft hills and coastlines."""
    out = []
    p = [pts[0]] + list(pts) + [pts[-1]]
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for k in range(n):
            t = k / n; t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in range(2)))
    out.append(pts[-1])
    return out

# ---------------------------------------------------------------- sky, sea, land
def sky(cv, cols, y1=None, bands=True, seed=1):
    """A poster sky: gradient through `cols`, cut into soft bands, with a few long brush streaks."""
    y1 = y1 or cv.H
    n = len(cols) - 1
    steps = 9 if bands else int(y1)
    for i in range(steps):
        t0, t1 = i / steps, (i + 1) / steps
        t = (t0 + t1) / 2 if bands else t0
        k = min(n - 1, int(t * n)); tt = t * n - k
        col = lerp(cols[k], cols[k + 1], tt)
        cv.rect((0, y1 * t0 - 1, cv.W, y1 * t1 + 1), col)
    rng = random.Random(seed)
    for _ in range(int(cv.W / 60)):
        y = rng.uniform(0.05, 0.8) * y1; x = rng.uniform(-0.2, 0.9) * cv.W; ln = rng.uniform(0.15, 0.4) * cv.W
        cv.line([(x, y), (x + ln, y + rng.uniform(-3, 3))], WHITE, w=rng.uniform(1, 2.6), alpha=rng.randint(18, 40))

def stars(cv, n, y1, seed=2, col=LAMP):
    rng = random.Random(seed)
    for _ in range(n):
        x, y, r = rng.uniform(0, cv.W), rng.uniform(0, y1), rng.uniform(0.6, 1.6)
        cv.ellipse((x - r, y - r, x + r, y + r), col, alpha=rng.randint(120, 230))

def moon(cv, x, y, r, col=LAMP, sky_col=None):
    """A crescent moon (cut out with a mask, so it sits on any sky)."""
    cv.glow(x, y, r * 2.2, col, alpha=40)
    m = Image.new("L", cv.img.size, 0); md = ImageDraw.Draw(m)
    md.ellipse(cv.S(x - r, y - r, x + r, y + r), fill=255)
    md.ellipse(cv.S(x - r * 0.45, y - r * 1.1, x + r * 1.55, y + r * 0.9), fill=0)
    L = Image.new("RGBA", cv.img.size, col + (255,)); L.putalpha(m)
    cv.img.alpha_composite(L)

def sea(cv, y0, y1=None, top=SEA2, bottom=SEA, stroke=SEA_L, seed=3, density=1.0, alpha=110):
    """Flat sea with rows of carved wave strokes, closer rows bigger (linocut)."""
    y1 = y1 or cv.H
    for i in range(8):
        t0, t1 = i / 8, (i + 1) / 8
        cv.rect((0, y0 + (y1 - y0) * t0 - 1, cv.W, y0 + (y1 - y0) * t1 + 1), lerp(top, bottom, (t0 + t1) / 2))
    rng = random.Random(seed)
    y = y0 + 4
    while y < y1:
        t = (y - y0) / max(1, y1 - y0)
        wl = 8 + 46 * t; gap = 4 + 16 * t
        x = rng.uniform(-wl, 0)
        while x < cv.W:
            if rng.random() < 0.55 * density:
                a = wl * rng.uniform(0.6, 1.2)
                pts = [(x + a * k / 8, y - math.sin(math.pi * k / 8) * (1.2 + 3.2 * t)) for k in range(9)]
                cv.line(pts, stroke, w=0.8 + 1.6 * t, alpha=alpha)
            x += wl * rng.uniform(1.0, 1.9)
        y += gap

def hills(cv, pts, base, col, hatch=None, seed=4, hatch_alpha=60):
    p = smooth(pts, 8)
    cv.poly(p + [(p[-1][0], base), (p[0][0], base)], col)
    if hatch:
        rng = random.Random(seed)
        xs = [q[0] for q in p]
        for _ in range(int((max(xs) - min(xs)) / 9)):
            x = rng.uniform(min(xs), max(xs))
            top = min(q[1] for q in p if abs(q[0] - x) < 6) if any(abs(q[0] - x) < 6 for q in p) else base
            y = rng.uniform(top + 4, base - 2)
            ln = rng.uniform(4, 12)
            cv.line([(x, y), (x + ln, y - ln * 0.35)], hatch, w=1, alpha=hatch_alpha)

def snow(cv, n, seed=5, y1=None, big=True, alpha=(120, 230)):
    rng = random.Random(seed)
    L = cv.layer(); ld = ImageDraw.Draw(L)
    y1 = y1 or cv.H
    for _ in range(n):
        x, y, r = rng.uniform(0, cv.W), rng.uniform(0, y1), rng.uniform(0.8, 2.2)
        ld.ellipse(cv.S(x - r, y - r, x + r, y + r), fill=SNOW + (rng.randint(*alpha),))
    cv.img.alpha_composite(L)
    if big:
        B = cv.layer(); bd = ImageDraw.Draw(B)
        for _ in range(max(4, n // 30)):
            x, y, r = rng.uniform(0, cv.W), rng.uniform(0, y1), rng.uniform(2.5, 4.5)
            bd.ellipse(cv.S(x - r, y - r, x + r, y + r), fill=SNOW + (rng.randint(110, 200),))
        cv.img.alpha_composite(B.filter(ImageFilter.GaussianBlur(1.2 * cv.ss)))

# ---------------------------------------------------------------- the island and its buildings
def island(cv, cx, base, w, h, col=MOSS, rock=STONE, seed=6):
    """A low green island with a rocky foot."""
    rp = [(cx - w * 0.55, base), (cx - w * 0.5, base - h * 0.25), (cx - w * 0.35, base - h * 0.42),
          (cx - w * 0.1, base - h * 0.5), (cx + w * 0.2, base - h * 0.46), (cx + w * 0.42, base - h * 0.3),
          (cx + w * 0.55, base)]
    cv.poly(smooth(rp, 6), rock)
    gp = [(cx - w * 0.47, base - h * 0.3), (cx - w * 0.3, base - h * 0.72), (cx - w * 0.05, base - h * 0.95),
          (cx + w * 0.22, base - h * 0.88), (cx + w * 0.4, base - h * 0.5), (cx + w * 0.47, base - h * 0.32)]
    g = smooth(gp, 8)
    cv.poly(g + [(cx + w * 0.47, base - h * 0.25), (cx - w * 0.47, base - h * 0.25)], col)
    rng = random.Random(seed)
    for _ in range(int(w / 5)):
        x = rng.uniform(cx - w * 0.42, cx + w * 0.42); y = rng.uniform(base - h * 0.8, base - h * 0.35)
        cv.line([(x, y), (x + 4, y - 2)], MOSS_D, w=1, alpha=90)
    for _ in range(int(w / 8)):
        x = rng.uniform(cx - w * 0.5, cx + w * 0.5); y = rng.uniform(base - h * 0.22, base - 2)
        cv.line([(x, y), (x + 5, y + 1)], shade(rock, 0.75), w=1.2, alpha=120)
    # foam at the foot
    for k in range(5):
        x = cx - w * 0.55 + w * 1.1 * k / 4
        cv.line([(x - 10, base + 1), (x + 10, base + 1)], FOAM, w=1.6, alpha=160)

def beam(cv, x, y, angle, length, spread, col=LAMP, alpha=70):
    """A soft beam of light from (x, y)."""
    a1, a2 = math.radians(angle - spread), math.radians(angle + spread)
    pts = [(x, y), (x + math.cos(a1) * length, y + math.sin(a1) * length), (x + math.cos(a2) * length, y + math.sin(a2) * length)]
    L = cv.layer(); ImageDraw.Draw(L).polygon(cv.P(pts), fill=col + (alpha,))
    cv.img.alpha_composite(L.filter(ImageFilter.GaussianBlur(4 * cv.ss)))

def lighthouse(cv, x, base, h, lit=True, beams=True, beam_angle=200, band=True):
    """White tapering tower, rust band, black gallery, lamp room and a rust-red cap."""
    wb, wt = h * 0.2, h * 0.12
    top = base - h
    cv.poly([(x - wb / 2, base), (x - wt / 2, top + h * 0.16), (x + wt / 2, top + h * 0.16), (x + wb / 2, base)], WHITE)
    # shading on the right
    cv.poly([(x + wb * 0.12, base), (x + wt * 0.12, top + h * 0.16), (x + wt / 2, top + h * 0.16), (x + wb / 2, base)],
            STONE_L, alpha=150)
    if band:
        for yy in (0.45, 0.72):
            yb = base - h * yy; wbb = wb + (wt - wb) * (yy - 0) / 0.84
            hb = h * 0.07
            wbt = wb + (wt - wb) * (yy + 0.07) / 0.84
            cv.poly([(x - wbb / 2, yb), (x - wbt / 2, yb - hb), (x + wbt / 2, yb - hb), (x + wbb / 2, yb)], RUST)
    # door and windows
    cv.poly([(x - wb * 0.13, base), (x - wb * 0.13, base - h * 0.1), (x, base - h * 0.125), (x + wb * 0.13, base - h * 0.1),
             (x + wb * 0.13, base)], RUST_D)
    for yy in (0.3, 0.58):
        cv.rect((x - wb * 0.05, base - h * yy - h * 0.03, x + wb * 0.05, base - h * yy), LAMP if lit else SLATE)
    # gallery
    gy = top + h * 0.16
    cv.rect((x - wt * 0.85, gy - h * 0.025, x + wt * 0.85, gy), INK)
    for k in range(7):
        xx = x - wt * 0.8 + wt * 1.6 * k / 6
        cv.line([(xx, gy - h * 0.025), (xx, gy - h * 0.065)], INK, w=max(1, h * 0.006))
    cv.line([(x - wt * 0.85, gy - h * 0.065), (x + wt * 0.85, gy - h * 0.065)], INK, w=max(1, h * 0.008))
    # lamp room
    lr0, lr1 = gy - h * 0.025, top + h * 0.05
    if lit:
        cv.glow(x, (lr0 + lr1) / 2, h * 0.22, LAMP, alpha=150)
        if beams:
            beam(cv, x, (lr0 + lr1) / 2, beam_angle, h * 3.2, 6, alpha=60)
            beam(cv, x, (lr0 + lr1) / 2, beam_angle + 180 + 8, h * 1.6, 5, alpha=35)
    cv.rect((x - wt * 0.45, lr1, x + wt * 0.45, lr0), LAMP if lit else NIGHT2)
    for k in range(4):
        xx = x - wt * 0.45 + wt * 0.9 * k / 3
        cv.line([(xx, lr1), (xx, lr0)], INK, w=max(1, h * 0.006))
    # cap
    cv.poly([(x - wt * 0.6, lr1), (x, top - h * 0.02), (x + wt * 0.6, lr1)], RUST)
    cv.line([(x, top - h * 0.02), (x, top - h * 0.06)], INK, w=max(1, h * 0.008))
    cv.ellipse((x - h * 0.012, top - h * 0.075, x + h * 0.012, top - h * 0.05), INK)

def cottage(cv, x, base, w, h, wall=WHITE, roof=SLATE, lit=True, smoke=True, door=RUST, seed=7):
    """A low keeper's cottage: whitewashed walls, slate roof, chimney, warm windows."""
    cv.rect((x, base - h, x + w, base), wall)
    cv.rect((x + w * 0.62, base - h, x + w, base), STONE_L, alpha=110)
    cv.poly([(x - w * 0.06, base - h), (x + w * 0.5, base - h * 1.75), (x + w * 1.06, base - h)], roof)
    cx = x + w * 0.74
    cv.rect((cx, base - h * 1.75, cx + w * 0.1, base - h * 1.25), STONE)
    if smoke:
        rng = random.Random(seed)
        for k in range(6):
            r = w * (0.06 + 0.03 * k)
            cv.ellipse((cx + w * 0.05 + k * w * 0.08 - r, base - h * 1.85 - k * h * 0.28 - r,
                        cx + w * 0.05 + k * w * 0.08 + r, base - h * 1.85 - k * h * 0.28 + r), WHITE, alpha=110 - k * 15)
    for k, wx in enumerate((0.15, 0.62)):
        if lit:
            cv.glow(x + w * (wx + 0.11), base - h * 0.55, w * 0.22, LAMP, alpha=90)
        cv.rect((x + w * wx, base - h * 0.78, x + w * (wx + 0.22), base - h * 0.32), LAMP if lit else SLATE)
        cv.line([(x + w * (wx + 0.11), base - h * 0.78), (x + w * (wx + 0.11), base - h * 0.32)], INK, w=1)
    cv.rect((x + w * 0.42, base - h * 0.7, x + w * 0.55, base), door)

def boathouse(cv, x, base, w, h, lamp=False):
    cv.rect((x, base - h, x + w, base), WOOD)
    for k in range(1, 6):
        cv.line([(x + w * k / 6, base - h), (x + w * k / 6, base)], shade(WOOD, 0.8), w=1)
    cv.poly([(x - w * 0.08, base - h), (x + w * 0.5, base - h * 1.6), (x + w * 1.08, base - h)], RUST_D)
    cv.rect((x + w * 0.3, base - h * 0.75, x + w * 0.7, base), NIGHT2)
    if lamp:
        cv.glow(x + w * 0.5, base - h * 0.35, w * 0.5, LAMP, alpha=170)
        cv.ellipse((x + w * 0.46, base - h * 0.42, x + w * 0.54, base - h * 0.28), LAMP)

def jetty(cv, x0, x1, y, col=WOOD):
    cv.rect((x0, y - 3, x1, y + 2), col)
    for k in range(int((x1 - x0) / 14) + 1):
        xx = x0 + k * 14
        cv.rect((xx, y + 2, xx + 3, y + 16), shade(col, 0.7))

def boat(cv, x, y, s, kind="fishing", hull=None, lit=True, facing=1, sail=False):
    """A small boat seen side on. kind: fishing, mail, cutter, rowing."""
    hull = hull or {"fishing": RUST, "mail": NIGHT2, "cutter": SEA, "rowing": WOOD}[kind]
    f = facing
    if kind == "rowing":
        cv.poly([(x - s * 0.5, y), (x - s * 0.42 * f * f, y + s * 0.16), (x + s * 0.42, y + s * 0.16), (x + s * 0.5, y - s * 0.02)], hull)
        cv.line([(x - s * 0.1, y - s * 0.02), (x + s * 0.6 * f, y + s * 0.3)], WOOD_L, w=max(1, s * 0.03))
        return
    pts = [(x - s * 0.55 * f, y - s * 0.06), (x - s * 0.45 * f, y + s * 0.18), (x + s * 0.4 * f, y + s * 0.18), (x + s * 0.6 * f, y - s * 0.1)]
    cv.poly(pts, hull)
    cv.line([(x - s * 0.55 * f, y - s * 0.06), (x + s * 0.6 * f, y - s * 0.1)], WHITE, w=max(1, s * 0.025))
    if kind in ("fishing", "mail"):
        cx0 = x - s * (0.25 if f > 0 else -0.05)
        cv.rect((min(cx0, cx0 + s * 0.3 * f), y - s * 0.32, max(cx0, cx0 + s * 0.3 * f), y - s * 0.07), WHITE)
        cv.rect((min(cx0, cx0 + s * 0.3 * f) - s * 0.02, y - s * 0.36, max(cx0, cx0 + s * 0.3 * f) + s * 0.02, y - s * 0.31), INK)
        for k in range(2):
            wx = min(cx0, cx0 + s * 0.3 * f) + s * (0.05 + 0.12 * k)
            cv.rect((wx, y - s * 0.26, wx + s * 0.07, y - s * 0.17), LAMP if lit else SLATE)
        mx = x + s * 0.2 * f
        cv.line([(mx, y - s * 0.08), (mx, y - s * 0.62)], INK, w=max(1, s * 0.02))
        if kind == "mail":
            cv.rect((mx, y - s * 0.62, mx + s * 0.16 * f if f > 0 else mx - s * 0.16, y - s * 0.52), RUST)
            sx = x - s * 0.05 * f
            cv.rect((sx - s * 0.04, y - s * 0.5, sx + s * 0.04, y - s * 0.32), RUST)
            for k in range(4):
                r = s * (0.04 + 0.02 * k)
                cv.ellipse((sx - s * 0.06 * f * k - r, y - s * 0.56 - k * s * 0.08 - r, sx - s * 0.06 * f * k + r,
                            y - s * 0.56 - k * s * 0.08 + r), WHITE, alpha=150 - 25 * k)
        if lit:
            cv.glow(mx, y - s * 0.6, s * 0.05, LAMP, alpha=200, blur=s * 0.03)
    if kind == "cutter" or sail:
        mx = x
        cv.line([(mx, y - s * 0.06), (mx, y - s * 0.95)], INK, w=max(1, s * 0.02))
        cv.poly([(mx + s * 0.02 * f, y - s * 0.92), (mx + s * 0.02 * f, y - s * 0.12), (mx + s * 0.48 * f, y - s * 0.12)], RUST_L)
        cv.poly([(mx - s * 0.02 * f, y - s * 0.85), (mx - s * 0.02 * f, y - s * 0.14), (mx - s * 0.36 * f, y - s * 0.14)], WHITE)

def gull(cv, x, y, s, col=WHITE):
    cv.line([(x - s, y - s * 0.1), (x - s * 0.45, y - s * 0.45), (x, y)], col, w=max(1, s * 0.16))
    cv.line([(x, y), (x + s * 0.45, y - s * 0.45), (x + s, y - s * 0.1)], col, w=max(1, s * 0.16))

def figure(cv, x, base, h, cap=RUST, coat=NIGHT2, scarf=None, bobble=True, lantern=False, rim=None):
    """A person seen from behind: a long duffel coat with the collar up, arms at the sides, boots, and a
    knitted cap with a bobble."""
    s = h
    # boots and legs
    for sx in (-1, 1):
        cv.poly([(x + sx * s * 0.035, base - s * 0.14), (x + sx * s * 0.1, base - s * 0.14), (x + sx * s * 0.105, base),
                 (x + sx * s * 0.03, base)], INK)
    body = [(-0.2, -0.12), (-0.17, -0.4), (-0.18, -0.58), (-0.165, -0.68), (-0.12, -0.735), (-0.05, -0.755),
            (0.05, -0.755), (0.12, -0.735), (0.165, -0.68), (0.18, -0.58), (0.17, -0.4), (0.2, -0.12)]
    cv.poly(smooth([(x + dx * s, base + dy * s) for dx, dy in body], 4) + [(x + s * 0.2, base - s * 0.12)], coat)
    dark = shade(coat, 0.72)
    for sx in (-1, 1):   # arms
        cv.poly(smooth([(x + sx * s * 0.165, base - s * 0.68), (x + sx * s * 0.205, base - s * 0.55), (x + sx * s * 0.21, base - s * 0.36),
                        (x + sx * s * 0.185, base - s * 0.33), (x + sx * s * 0.155, base - s * 0.4), (x + sx * s * 0.14, base - s * 0.62)], 4), dark)
    if rim:
        cv.line(smooth([(x + s * 0.17, base - s * 0.68), (x + s * 0.205, base - s * 0.5), (x + s * 0.2, base - s * 0.14)], 5), rim, w=max(1, s * 0.012), alpha=200)
    cv.line([(x, base - s * 0.7), (x + s * 0.005, base - s * 0.14)], dark, w=max(1, s * 0.008))
    cv.rect((x - s * 0.16, base - s * 0.45, x + s * 0.16, base - s * 0.425), dark)             # back belt of the duffel
    # collar and the back of the head
    cv.poly([(x - s * 0.1, base - s * 0.76), (x + s * 0.1, base - s * 0.76), (x + s * 0.085, base - s * 0.715),
             (x - s * 0.085, base - s * 0.715)], dark)
    cv.ellipse((x - s * 0.068, base - s * 0.875, x + s * 0.068, base - s * 0.745), (58, 44, 38))
    if scarf:
        cv.poly([(x - s * 0.11, base - s * 0.775), (x + s * 0.11, base - s * 0.775), (x + s * 0.1, base - s * 0.735),
                 (x - s * 0.1, base - s * 0.735)], scarf)
    if cap:
        cv.poly(smooth([(x - s * 0.078, base - s * 0.82), (x - s * 0.075, base - s * 0.875), (x - s * 0.045, base - s * 0.915),
                        (x, base - s * 0.925), (x + s * 0.045, base - s * 0.915), (x + s * 0.075, base - s * 0.875),
                        (x + s * 0.078, base - s * 0.82)], 4), cap)
        cv.rect((x - s * 0.08, base - s * 0.835, x + s * 0.08, base - s * 0.805), shade(cap, 0.78))
        for k in range(6):
            xx = x - s * 0.06 + s * 0.024 * k
            cv.line([(xx, base - s * 0.835), (xx, base - s * 0.9)], shade(cap, 0.86), w=max(1, s * 0.005))
        if bobble:
            cv.ellipse((x - s * 0.032, base - s * 0.968, x + s * 0.032, base - s * 0.904), WHITE)
    if lantern:
        cv.glow(x + s * 0.24, base - s * 0.36, s * 0.15, LAMP, alpha=170)
        cv.line([(x + s * 0.21, base - s * 0.36), (x + s * 0.24, base - s * 0.44)], INK, w=max(1, s * 0.01))
        cv.rect((x + s * 0.215, base - s * 0.42, x + s * 0.265, base - s * 0.33), LAMP)

def keeper(cv, x, base, h, jumper=SEA2):
    """The keeper from behind: thick jumper, flat cap."""
    figure(cv, x, base, h, cap=None, coat=jumper, bobble=False)
    s = h
    cv.poly([(x - s * 0.09, base - s * 0.86), (x + s * 0.09, base - s * 0.86), (x + s * 0.11, base - s * 0.83),
             (x - s * 0.11, base - s * 0.83)], INK)
    cv.ellipse((x - s * 0.08, base - s * 0.92, x + s * 0.08, base - s * 0.84), INK)

# ---------------------------------------------------------------- objects (interiors and close-ups)
def stove(cv, x, base, s, lit=True):
    cv.rect((x - s * 0.5, base - s * 0.7, x + s * 0.5, base), INK)
    cv.rect((x - s * 0.55, base - s * 0.76, x + s * 0.55, base - s * 0.68), SLATE)
    cv.rect((x - s * 0.1, base - s * 1.6, x + s * 0.1, base - s * 0.76), INK)
    if lit:
        cv.glow(x, base - s * 0.32, s * 0.4, OCHRE, alpha=120)
        cv.rect((x - s * 0.28, base - s * 0.48, x + s * 0.28, base - s * 0.18), OCHRE)
        for k in range(5):
            cv.line([(x - s * 0.24 + s * 0.12 * k, base - s * 0.48), (x - s * 0.24 + s * 0.12 * k, base - s * 0.18)], INK, w=max(1, s * 0.02))
    # a pot and a cup on top
    cv.rect((x - s * 0.36, base - s * 0.98, x - s * 0.06, base - s * 0.76), RUST)
    cv.rect((x - s * 0.38, base - s * 1.0, x - s * 0.04, base - s * 0.96), RUST_D)

def table(cv, x0, x1, y, col=WOOD_L):
    cv.rect((x0, y - 6, x1, y + 2), col)
    cv.rect((x0 + 8, y + 2, x0 + 16, y + 60), shade(col, 0.75)); cv.rect((x1 - 16, y + 2, x1 - 8, y + 60), shade(col, 0.75))

def journal(cv, x, y, w, h, open_=True, col=RUST_D):
    if open_:
        cv.poly([(x - w / 2, y + h * 0.05), (x, y + h * 0.1), (x + w / 2, y + h * 0.05), (x + w / 2, y - h), (x, y - h * 0.95), (x - w / 2, y - h)], col)
        cv.poly([(x - w * 0.47, y), (x - w * 0.01, y + h * 0.04), (x - w * 0.01, y - h * 0.92), (x - w * 0.47, y - h * 0.96)], PAPER)
        cv.poly([(x + w * 0.01, y + h * 0.04), (x + w * 0.47, y), (x + w * 0.47, y - h * 0.96), (x + w * 0.01, y - h * 0.92)], PAPER)
        for k in range(7):
            yy = y - h * 0.82 + h * 0.11 * k
            cv.line([(x - w * 0.42, yy), (x - w * 0.06, yy + 1)], SLATE, w=1, alpha=150)
            cv.line([(x + w * 0.06, yy + 1), (x + w * (0.42 - 0.08 * (k == 6)), yy)], SLATE, w=1, alpha=150)
    else:
        cv.rect((x - w / 2, y - h, x + w / 2, y), col)
        cv.rect((x - w / 2 + w * 0.08, y - h, x - w / 2 + w * 0.14, y), shade(col, 0.8))

def cup(cv, x, y, s, col=WHITE, steam=True):
    cv.poly([(x - s * 0.4, y - s * 0.6), (x + s * 0.4, y - s * 0.6), (x + s * 0.3, y), (x - s * 0.3, y)], col)
    cv.ellipse((x + s * 0.3, y - s * 0.5, x + s * 0.6, y - s * 0.2), col)
    cv.ellipse((x + s * 0.37, y - s * 0.43, x + s * 0.53, y - s * 0.27), PAPER2)
    cv.rect((x - s * 0.4, y - s * 0.45, x + s * 0.36, y - s * 0.38), RUST)
    if steam:
        for k in (-0.15, 0.1):
            pts = [(x + s * k + math.sin(t / 2) * s * 0.06, y - s * 0.7 - t * s * 0.08) for t in range(8)]
            cv.line(pts, WHITE, w=max(1, s * 0.05), alpha=140)

def parcel(cv, x, y, w, h, paper=WOOD_L, string=RUST, label=True, tilt=0.0):
    cv.poly([(x, y), (x + w, y + tilt), (x + w, y - h + tilt), (x, y - h)], paper)
    cv.poly([(x + w * 0.45, y + tilt * 0.45), (x + w * 0.55, y + tilt * 0.55), (x + w * 0.55, y - h + tilt * 0.55),
             (x + w * 0.45, y - h + tilt * 0.45)], string)
    cv.poly([(x, y - h * 0.45), (x + w, y - h * 0.45 + tilt), (x + w, y - h * 0.55 + tilt), (x, y - h * 0.55)], string)
    if label:
        cv.rect((x + w * 0.1, y - h * 0.9 + tilt * 0.1, x + w * 0.38, y - h * 0.65 + tilt * 0.1), PAPER)

def tally(cv, x, y, r, metal=BRASS, hole=True):
    cv.ellipse((x - r, y - r, x + r, y + r), metal)
    cv.ellipse((x - r * 0.82, y - r * 0.82, x + r * 0.82, y + r * 0.82), shade(metal, 1.12))
    cv.ellipse((x - r * 0.82, y - r * 0.82, x + r * 0.3, y + r * 0.3), shade(metal, 1.22), alpha=90)
    if hole:
        cv.ellipse((x - r * 0.14, y - r * 0.8, x + r * 0.14, y - r * 0.52), INK)
    for k in range(4):
        cv.rect((x - r * 0.5 + r * 0.26 * k, y - r * 0.1, x - r * 0.36 + r * 0.26 * k, y + r * 0.25), shade(metal, 0.65))

def holly(cv, x, y, s):
    for a in (-30, 30, 160):
        ra = math.radians(a)
        cx, cy = x + math.cos(ra) * s * 0.5, y + math.sin(ra) * s * 0.3
        cv.ellipse((cx - s * 0.45, cy - s * 0.18, cx + s * 0.45, cy + s * 0.18), MOSS_D)
    for dx, dy in ((-0.08, 0), (0.08, 0.02), (0, -0.1)):
        cv.ellipse((x + dx * s - s * 0.08, y + dy * s - s * 0.08, x + dx * s + s * 0.08, y + dy * s + s * 0.08), RUST)

def robin(cv, x, y, s):
    cv.ellipse((x - s * 0.5, y - s * 0.4, x + s * 0.4, y + s * 0.4), WOOD)
    cv.ellipse((x - s * 0.15, y - s * 0.1, x + s * 0.35, y + s * 0.35), RUST)
    cv.ellipse((x + s * 0.15, y - s * 0.7, x + s * 0.55, y - s * 0.3), WOOD)
    cv.poly([(x + s * 0.55, y - s * 0.52), (x + s * 0.72, y - s * 0.48), (x + s * 0.55, y - s * 0.44)], INK)
    cv.poly([(x - s * 0.45, y - s * 0.1), (x - s * 0.85, y - s * 0.3), (x - s * 0.8, y + s * 0.0)], WOOD)
    cv.line([(x - s * 0.05, y + s * 0.38), (x - s * 0.08, y + s * 0.62)], INK, w=max(1, s * 0.05))
    cv.line([(x + s * 0.1, y + s * 0.38), (x + s * 0.12, y + s * 0.62)], INK, w=max(1, s * 0.05))

def mitten(cv, x, y, s, col=RUST):
    cv.poly(smooth([(x - s * 0.3, y), (x - s * 0.34, y - s * 0.6), (x - s * 0.2, y - s * 0.95), (x + s * 0.1, y - s * 0.98),
                    (x + s * 0.3, y - s * 0.7), (x + s * 0.3, y)], 6), col)
    cv.poly(smooth([(x - s * 0.3, y - s * 0.45), (x - s * 0.55, y - s * 0.6), (x - s * 0.58, y - s * 0.75), (x - s * 0.38, y - s * 0.72)], 5), col)
    cv.rect((x - s * 0.34, y - s * 0.02, x + s * 0.34, y + s * 0.2), WHITE)
    for k in range(5):
        cv.line([(x - s * 0.28 + s * 0.14 * k, y - s * 0.02), (x - s * 0.28 + s * 0.14 * k, y + s * 0.2)], STONE_L, w=1)
    for k in range(4):
        cv.line([(x - s * 0.25, y - s * 0.25 - s * 0.15 * k), (x + s * 0.25, y - s * 0.25 - s * 0.15 * k)], shade(col, 0.85), w=1)

def scarf(cv, x, y, w, h, n=12, a=RUST, b=WHITE):
    for k in range(n):
        cv.rect((x, y + h * k / n, x + w, y + h * (k + 1) / n + 0.5), a if k % 2 == 0 else b)
    for k in range(6):
        cv.line([(x + w * (0.1 + 0.16 * k), y + h), (x + w * (0.1 + 0.16 * k), y + h + w * 0.5)], b if n % 2 == 0 else a, w=1.4)

def cake(cv, x, y, s):
    cv.rect((x - s * 0.6, y - s * 0.55, x + s * 0.6, y), WHITE)
    cv.ellipse((x - s * 0.6, y - s * 0.7, x + s * 0.6, y - s * 0.4), SNOW)
    cv.rect((x - s * 0.62, y - s * 0.25, x + s * 0.62, y - s * 0.12), RUST)
    cv.ellipse((x - s * 0.75, y - s * 0.08, x + s * 0.75, y + s * 0.1), STONE_L)
    for k in range(5):
        cv.ellipse((x - s * 0.38 + s * 0.19 * k - s * 0.05, y - s * 0.6, x - s * 0.38 + s * 0.19 * k + s * 0.05, y - s * 0.5),
                   [RUST, MOSS, OCHRE, RUST, MOSS][k])
    holly(cv, x, y - s * 0.68, s * 0.25)

def sea_chest(cv, x, y, w, h, col=SEA2):
    cv.rect((x - w / 2, y - h, x + w / 2, y), col)
    cv.poly([(x - w / 2, y - h), (x - w * 0.46, y - h * 1.3), (x + w * 0.46, y - h * 1.3), (x + w / 2, y - h)], shade(col, 1.15))
    for xx in (-0.38, 0.38):
        cv.rect((x + w * xx - w * 0.03, y - h * 1.3, x + w * xx + w * 0.03, y), BRASS)
    cv.rect((x - w * 0.06, y - h * 0.95, x + w * 0.06, y - h * 0.75), BRASS)
    for k in range(6):
        cv.rect((x - w * 0.3 + w * 0.1 * k, y - h * 0.5, x - w * 0.24 + w * 0.1 * k, y - h * 0.32), WHITE)

def tide_post(cv, x, base, h, level=0.45):
    cv.rect((x - 6, base - h, x + 6, base), WHITE)
    for k in range(9):
        yy = base - h * k / 8
        cv.line([(x - 6, yy), (x + (6 if k % 2 else 14), yy)], INK, w=1.4)
    return base - h * level

def lamp_hand(cv, x, y, s, lit=True):
    if lit:
        cv.glow(x, y, s * 1.2, LAMP, alpha=170)
    cv.rect((x - s * 0.25, y - s * 0.3, x + s * 0.25, y + s * 0.3), LAMP if lit else STONE)
    cv.rect((x - s * 0.3, y - s * 0.38, x + s * 0.3, y - s * 0.3), INK)
    cv.rect((x - s * 0.3, y + s * 0.3, x + s * 0.3, y + s * 0.38), INK)
    cv.line([(x - s * 0.2, y - s * 0.38), (x, y - s * 0.6), (x + s * 0.2, y - s * 0.38)], INK, w=max(1, s * 0.06))

def morse_marks(cv, x, y, s, code, col=LAMP):
    for ch in code:
        if ch == "·":
            cv.ellipse((x - s * 0.2, y - s * 0.2, x + s * 0.2, y + s * 0.2), col); x += s * 0.7
        else:
            cv.rect((x - s * 0.2, y - s * 0.16, x + s * 1.0, y + s * 0.16), col); x += s * 1.5

def cat(cv, x, base, s, col=OCHRE):
    """Bosun, curled up, seen from behind."""
    cv.ellipse((x - s * 0.6, base - s * 0.55, x + s * 0.6, base), col)
    cv.ellipse((x + s * 0.2, base - s * 0.8, x + s * 0.65, base - s * 0.4), col)
    cv.poly([(x + s * 0.24, base - s * 0.7), (x + s * 0.28, base - s * 0.95), (x + s * 0.4, base - s * 0.76)], col)
    cv.poly([(x + s * 0.48, base - s * 0.76), (x + s * 0.6, base - s * 0.95), (x + s * 0.63, base - s * 0.68)], col)
    for k in range(4):
        cv.line([(x - s * 0.4 + s * 0.2 * k, base - s * 0.5), (x - s * 0.36 + s * 0.2 * k, base - s * 0.3)], shade(col, 0.75), w=max(1, s * 0.05))
    cv.line(smooth([(x - s * 0.55, base - s * 0.1), (x - s * 0.2, base + s * 0.05), (x + s * 0.3, base - s * 0.02)], 6), col, w=max(1, s * 0.12))
