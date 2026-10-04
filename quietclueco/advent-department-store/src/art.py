"""Anime-noir art for The Windows at Quillon's, drawn entirely with code (Pillow).

Look: a 90s night-time detective cartoon in winter. Snow falling at a slant through lamplight,
dark blue city, flat cel-shaded shapes with hard-edged shadows, long shadows, film grain and
one warm accent: the amber of the shop windows. Only silhouettes seen from behind, hands in
gloves, objects, interiors and streets. No faces, no recognisable characters.

Used by the PDF renderer (one scene per window, the cover) and by the listing kit (mockups, video).
"""
import math, random
from PIL import Image, ImageDraw, ImageFilter, ImageChops

# ---------------------------------------------------------------- palette
NIGHT0 = (8, 12, 24); NIGHT1 = (22, 32, 56); NIGHT2 = (34, 48, 80)
INK = (12, 16, 30); INK2 = (20, 27, 46); STEEL = (70, 88, 118); STEEL2 = (104, 124, 158)
FROST = (196, 210, 230); SNOW = (236, 241, 248)
AMBER = (242, 163, 58); AMBER_D = (168, 92, 22); AMBER_L = (255, 210, 140); BROWN = (52, 32, 14)
LAMP = (214, 228, 246)      # street lamps stay cold; the only warm colour is the shop-window amber

def lerp(a, b, t):
    return tuple(int(x + (y - x) * t) for x, y in zip(a, b))

# ---------------------------------------------------------------- canvas helpers
class Canvas:
    """Draw at 2x and downscale, so every edge is smooth."""
    def __init__(self, w, h, ss=2):
        self.W, self.H, self.ss = w, h, ss
        self.img = Image.new("RGBA", (w * ss, h * ss), NIGHT0 + (255,))
        self.d = ImageDraw.Draw(self.img)

    def S(self, *v):
        return [x * self.ss for x in v]

    def P(self, pts):
        return [(x * self.ss, y * self.ss) for x, y in pts]

    def layer(self):
        return Image.new("RGBA", self.img.size, (0, 0, 0, 0))

    def glow(self, cx, cy, r, col, alpha=150, blur=None):
        g = self.layer(); gd = ImageDraw.Draw(g)
        gd.ellipse(self.S(cx - r, cy - r, cx + r, cy + r), fill=col + (alpha,))
        g = g.filter(ImageFilter.GaussianBlur((blur or r * 0.6) * self.ss))
        self.img.alpha_composite(g)

    def rect_glow(self, box, col, alpha=140, blur=30):
        g = self.layer(); ImageDraw.Draw(g).rectangle(self.S(*box), fill=col + (alpha,))
        self.img.alpha_composite(g.filter(ImageFilter.GaussianBlur(blur * self.ss)))

    def finish(self, grain=22, vignette=0.55, seed=1):
        im = self.img.resize((self.W, self.H), Image.LANCZOS).convert("RGB")
        if vignette:
            m = Image.new("L", (self.W, self.H), 0)
            ImageDraw.Draw(m).ellipse([-self.W * 0.25, -self.H * 0.3, self.W * 1.25, self.H * 1.3], fill=255)
            m = m.filter(ImageFilter.GaussianBlur(min(self.W, self.H) * 0.18))
            dark = Image.new("RGB", im.size, NIGHT0)
            im = Image.composite(im, Image.blend(im, dark, vignette), m)
        if grain:
            random.seed(seed)
            n = Image.effect_noise((self.W, self.H), 64).convert("L")
            n = n.point(lambda v: 128 + (v - 128) * grain // 40)
            im = ImageChops.overlay(im, Image.merge("RGB", (n, n, n)))
        return im

def sky(cv, top=NIGHT0, bottom=NIGHT2, y1=None):
    y1 = y1 or cv.H
    for y in range(int(y1)):
        cv.d.line(cv.S(0, y, cv.W, y), fill=lerp(top, bottom, y / y1) + (255,), width=cv.ss + 1)

def snow(cv, n, seed=3, angle=-28, length=(3, 8), alpha=(70, 200), area=None, big=True):
    """Snow falling at a slant through the light: mostly flakes, a few short streaks, and some large soft
    flakes close to the camera."""
    rng = random.Random(seed); L = cv.layer(); ld = ImageDraw.Draw(L)
    x0, y0, x1, y1 = area or (0, 0, cv.W, cv.H)
    a = math.radians(90 + angle)
    for i in range(n):
        x, y = rng.uniform(x0 - 40, x1), rng.uniform(y0, y1)
        al = rng.randint(*alpha)
        if i % 5 == 0:
            ln = rng.uniform(*length)
            ld.line(cv.S(x, y, x + math.cos(a) * ln, y + math.sin(a) * ln), fill=SNOW + (al,), width=max(1, cv.ss))
        else:
            r = rng.uniform(0.7, 2.0)
            ld.ellipse(cv.S(x - r, y - r, x + r, y + r), fill=SNOW + (al,))
    cv.img.alpha_composite(L)
    if big:
        B = cv.layer(); bd = ImageDraw.Draw(B)
        for i in range(max(4, n // 40)):
            x, y, r = rng.uniform(x0, x1), rng.uniform(y0, y1), rng.uniform(3, 7)
            bd.ellipse(cv.S(x - r, y - r, x + r, y + r), fill=SNOW + (rng.randint(60, 140),))
        cv.img.alpha_composite(B.filter(ImageFilter.GaussianBlur(2.2 * cv.ss)))

def skyline(cv, base, seed=5, col=INK, lit=0.12, height=(0.18, 0.42)):
    rng = random.Random(seed); x = -10
    while x < cv.W + 10:
        w = rng.uniform(cv.W * 0.06, cv.W * 0.14); h = cv.H * rng.uniform(*height)
        cv.d.rectangle(cv.S(x, base - h, x + w, base), fill=col)
        if rng.random() < 0.4:      # a chimney or gable
            cv.d.polygon(cv.P([(x, base - h), (x + w / 2, base - h - w * 0.35), (x + w, base - h)]), fill=col)
        for wy in range(int(base - h + 12), int(base - 8), 16):
            for wx in range(int(x + 6), int(x + w - 8), 14):
                if rng.random() < lit:
                    c = AMBER_D if rng.random() < 0.35 else STEEL
                    cv.d.rectangle(cv.S(wx, wy, wx + 5, wy + 8), fill=c)
        x += w + rng.uniform(2, 10)

def ground(cv, y, col=INK2, edge=STEEL):
    cv.d.rectangle(cv.S(0, y, cv.W, cv.H), fill=col)
    cv.d.line(cv.S(0, y, cv.W, y), fill=edge, width=cv.ss * 2)

def lamp(cv, x, base, h, glow=True):
    cv.d.rectangle(cv.S(x - 3, base - h, x + 3, base), fill=INK)
    cv.d.polygon(cv.P([(x - 12, base - h), (x + 12, base - h), (x + 8, base - h - 16), (x - 8, base - h - 16)]), fill=INK)
    cv.d.rectangle(cv.S(x - 7, base - h - 14, x + 7, base - h - 2), fill=LAMP)
    if glow:
        cv.glow(x, base - h - 8, h * 0.35, LAMP, alpha=70)
        L = cv.layer(); ImageDraw.Draw(L).polygon(cv.P([(x - 8, base - h), (x + 8, base - h), (x + h * 0.45, base),
                                                         (x - h * 0.45, base)]), fill=LAMP + (26,))
        cv.img.alpha_composite(L.filter(ImageFilter.GaussianBlur(6 * cv.ss)))

def figure(cv, x, base, h, hat=True, shadow=(1, 0.35), col=INK, coat=None):
    """A person seen from behind: long flared coat, broad shoulders, collar up, a fedora. Long hard-edged
    shadow on the snow."""
    s = h
    if shadow:
        dx, dy = shadow
        L = cv.layer(); ImageDraw.Draw(L).polygon(cv.P([(x - s * 0.16, base), (x + s * 0.16, base),
                                                         (x + s * 0.2 + dx * s * 1.8, base + dy * s * 0.6),
                                                         (x - s * 0.02 + dx * s * 1.8, base + dy * s * 0.66)]),
                                                  fill=NIGHT0 + (170,))
        cv.img.alpha_composite(L.filter(ImageFilter.GaussianBlur(0.8 * cv.ss)))
    c = coat or col
    body = [(-0.25, 0), (-0.2, -0.3), (-0.215, -0.5), (-0.2, -0.66), (-0.15, -0.72), (-0.07, -0.76),
            (0.07, -0.76), (0.15, -0.72), (0.2, -0.66), (0.215, -0.5), (0.2, -0.3), (0.25, 0)]
    cv.d.polygon(cv.P([(x + dx * s, base + dy * s) for dx, dy in body]), fill=c)
    cv.d.line(cv.P([(x, base - s * 0.7), (x + s * 0.02, base - s * 0.05)]), fill=lerp(c, NIGHT2, 0.35), width=cv.ss)  # coat vent
    cv.d.ellipse(cv.S(x - s * 0.058, base - s * 0.875, x + s * 0.058, base - s * 0.75), fill=c)
    cv.d.polygon(cv.P([(x - s * 0.1, base - s * 0.77), (x + s * 0.1, base - s * 0.77), (x + s * 0.075, base - s * 0.7),
                       (x - s * 0.075, base - s * 0.7)]), fill=c)   # turned-up collar
    if hat:
        cv.d.polygon(cv.P([(x - s * 0.145, base - s * 0.835), (x + s * 0.15, base - s * 0.85), (x + s * 0.145, base - s * 0.866),
                           (x - s * 0.15, base - s * 0.852)]), fill=c)                     # brim, tilted, resting on the head
        cv.d.polygon(cv.P([(x - s * 0.075, base - s * 0.845), (x + s * 0.08, base - s * 0.855), (x + s * 0.068, base - s * 0.93),
                           (x + s * 0.01, base - s * 0.915), (x - s * 0.062, base - s * 0.925)]), fill=c)   # pinched crown
    # rim light from the windows: a thin amber edge along the shoulder and upper arm
    cv.d.line(cv.P([(x + s * 0.13, base - s * 0.73), (x + s * 0.2, base - s * 0.66), (x + s * 0.215, base - s * 0.5)]),
              fill=AMBER_D, width=max(1, int(s * 0.012)) * cv.ss)

def shop_window(cv, box, frame=INK, panes=(2, 1), awning=True, label=None):
    """A glowing amber shop window. Returns the inner box for the display."""
    x0, y0, x1, y1 = box
    cv.rect_glow((x0 - 20, y0 - 10, x1 + 20, y1 + 30), AMBER, alpha=110, blur=26)
    for i in range(int(y1 - y0)):
        t = i / (y1 - y0)
        cv.d.line(cv.S(x0, y0 + i, x1, y0 + i), fill=lerp(AMBER_L, AMBER, min(1, t * 1.3)) + (255,), width=cv.ss + 1)
    cv.glow((x0 + x1) / 2, y0 + (y1 - y0) * 0.35, (x1 - x0) * 0.28, (255, 236, 196), alpha=120)
    w = max(4, (x1 - x0) * 0.025)
    cv.d.rectangle(cv.S(x0 - w, y0 - w, x1 + w, y1 + w), outline=frame, width=int(w * cv.ss))
    cx, cy = panes
    for k in range(1, cx):
        xx = x0 + (x1 - x0) * k / cx
        cv.d.rectangle(cv.S(xx - w / 3, y0, xx + w / 3, y1), fill=frame)
    cv.d.rectangle(cv.S(x0 - w * 2, y1, x1 + w * 2, y1 + w * 3), fill=frame)   # sill
    if awning:
        n = 8; aw = (x1 - x0 + w * 6) / n
        for k in range(n):
            ax = x0 - w * 3 + k * aw
            cv.d.polygon(cv.P([(ax, y0 - w * 7), (ax + aw, y0 - w * 7), (ax + aw * 0.92, y0 - w * 2), (ax + aw * 0.08, y0 - w * 2)]),
                         fill=INK2 if k % 2 else INK)
    # light spilling onto the snow
    L = cv.layer(); ld = ImageDraw.Draw(L)
    ld.polygon(cv.P([(x0, y1 + w * 3), (x1, y1 + w * 3), (x1 + (x1 - x0) * 0.35, cv.H), (x0 - (x1 - x0) * 0.35, cv.H)]),
               fill=AMBER + (46,))
    ld.polygon(cv.P([(x0 + (x1 - x0) * 0.1, y1 + w * 3), (x1 - (x1 - x0) * 0.1, y1 + w * 3),
                     (x1 + (x1 - x0) * 0.05, cv.H), (x0 - (x1 - x0) * 0.05, cv.H)]), fill=AMBER + (34,))
    cv.img.alpha_composite(L.filter(ImageFilter.GaussianBlur(0.6 * cv.ss)))
    return (x0 + w, y0 + w, x1 - w, y1 - w)

def facade(cv, top, base, col=INK, trim=INK2):
    cv.d.rectangle(cv.S(0, top, cv.W, base), fill=col)
    for k in range(0, cv.W, 160):
        cv.d.rectangle(cv.S(k, top, k + 14, base), fill=trim)
    cv.d.rectangle(cv.S(0, top, cv.W, top + 10), fill=trim)

def interior(cv, floor_y, wall=INK2, floor=NIGHT1):
    cv.d.rectangle(cv.S(0, 0, cv.W, floor_y), fill=wall)
    for k in range(0, cv.W, 70):           # wall panels
        cv.d.rectangle(cv.S(k + 8, floor_y * 0.35, k + 62, floor_y - 12), outline=INK, width=2 * cv.ss)
    for i in range(int(cv.H - floor_y)):
        t = i / max(1, cv.H - floor_y)
        cv.d.line(cv.S(0, floor_y + i, cv.W, floor_y + i), fill=lerp(INK, floor, t) + (255,), width=cv.ss + 1)
    for k in range(-8, 9):                 # floor tiles in perspective
        cv.d.line(cv.P([(cv.W / 2 + k * 30, floor_y), (cv.W / 2 + k * 130, cv.H)]), fill=INK, width=cv.ss)

def hanging_lamp(cv, x, y, r=16):
    cv.d.line(cv.S(x, 0, x, y - r * 0.6), fill=INK, width=2 * cv.ss)
    cv.d.pieslice(cv.S(x - r, y - r * 0.6, x + r, y + r * 0.9), 180, 360, fill=INK)
    cv.glow(x, y + r * 0.5, r * 3, AMBER, alpha=120)
    L = cv.layer(); ImageDraw.Draw(L).polygon(cv.P([(x - r, y + 2), (x + r, y + 2), (x + r * 5, cv.H), (x - r * 5, cv.H)]),
                                              fill=AMBER + (34,))
    cv.img.alpha_composite(L.filter(ImageFilter.GaussianBlur(8 * cv.ss)))

# ---------------------------------------------------------------- objects (silhouettes, unit size s)
def o_envelope(cv, x, y, s, col=BROWN):
    cv.d.rectangle(cv.S(x - s * 0.5, y - s * 0.32, x + s * 0.5, y + s * 0.32), fill=col)
    cv.d.line(cv.P([(x - s * 0.5, y - s * 0.32), (x, y + s * 0.05), (x + s * 0.5, y - s * 0.32)]), fill=AMBER_L, width=2 * cv.ss)
    cv.d.ellipse(cv.S(x - s * 0.07, y - s * 0.02, x + s * 0.07, y + s * 0.12), fill=AMBER_D)

def o_ledger(cv, x, y, s, col=BROWN):
    cv.d.polygon(cv.P([(x - s * 0.6, y + s * 0.2), (x, y + s * 0.32), (x + s * 0.6, y + s * 0.2), (x + s * 0.55, y - s * 0.22),
                       (x, y - s * 0.1), (x - s * 0.55, y - s * 0.22)]), fill=col)
    for k in range(5):
        yy = y - s * 0.1 + k * s * 0.07
        cv.d.line(cv.S(x - s * 0.48, yy - s * 0.06, x - s * 0.06, yy), fill=AMBER_L, width=cv.ss)
        cv.d.line(cv.S(x + s * 0.06, yy, x + s * 0.48, yy - s * 0.06), fill=AMBER_L, width=cv.ss)

def o_drum(cv, x, y, s, col=BROWN):
    cv.d.rectangle(cv.S(x - s * 0.45, y - s * 0.3, x + s * 0.45, y + s * 0.3), fill=col)
    cv.d.ellipse(cv.S(x - s * 0.45, y - s * 0.42, x + s * 0.45, y - s * 0.18), fill=lerp(col, AMBER_D, 0.4))
    for k in range(5):
        xx = x - s * 0.45 + k * s * 0.225
        cv.d.line(cv.S(xx, y - s * 0.28, xx + s * 0.11, y + s * 0.28), fill=AMBER_L, width=cv.ss)
    cv.d.line(cv.S(x + s * 0.2, y - s * 0.75, x + s * 0.05, y - s * 0.38), fill=col, width=4 * cv.ss)

def o_horn(cv, x, y, s, col=BROWN):
    cv.d.arc(cv.S(x - s * 0.4, y - s * 0.4, x + s * 0.4, y + s * 0.4), 200, 520, fill=col, width=int(s * 0.12 * cv.ss))
    cv.d.polygon(cv.P([(x + s * 0.3, y - s * 0.2), (x + s * 0.75, y - s * 0.55), (x + s * 0.75, y + s * 0.15)]), fill=col)

def o_glove(cv, x, y, s, col=BROWN):
    cv.d.rounded_rectangle(cv.S(x - s * 0.22, y - s * 0.1, x + s * 0.22, y + s * 0.45), radius=s * 0.08 * cv.ss, fill=col)
    for k, (dx, ln) in enumerate([(-0.17, 0.42), (-0.06, 0.52), (0.06, 0.5), (0.17, 0.4)]):
        cv.d.rounded_rectangle(cv.S(x + dx * s - s * 0.05, y - ln * s, x + dx * s + s * 0.05, y), radius=s * 0.05 * cv.ss, fill=col)
    cv.d.rounded_rectangle(cv.S(x - s * 0.4, y - s * 0.02, x - s * 0.16, y + s * 0.1), radius=s * 0.05 * cv.ss, fill=col)
    cv.d.rectangle(cv.S(x - s * 0.24, y + s * 0.4, x + s * 0.24, y + s * 0.5), fill=AMBER_D)

def o_parcel(cv, x, y, s, col=BROWN):
    for i, (dx, dy, w, h) in enumerate([(0, 0.2, 0.9, 0.5), (-0.1, -0.25, 0.6, 0.4), (0.12, -0.55, 0.35, 0.25)]):
        cx, cy = x + dx * s, y + dy * s
        cv.d.rectangle(cv.S(cx - w * s / 2, cy - h * s / 2, cx + w * s / 2, cy + h * s / 2), fill=col)
        cv.d.rectangle(cv.S(cx - s * 0.03, cy - h * s / 2, cx + s * 0.03, cy + h * s / 2), fill=AMBER_L)
        cv.d.rectangle(cv.S(cx - w * s / 2, cy - s * 0.03, cx + w * s / 2, cy + s * 0.03), fill=AMBER_L)
    cv.d.ellipse(cv.S(x + s * 0.02, y - s * 0.78, x + s * 0.14, y - s * 0.66), outline=AMBER_L, width=2 * cv.ss)
    cv.d.ellipse(cv.S(x + s * 0.12, y - s * 0.78, x + s * 0.24, y - s * 0.66), outline=AMBER_L, width=2 * cv.ss)

def o_watch(cv, x, y, s, col=BROWN, minute=0, hour=10):
    cv.d.ellipse(cv.S(x - s * 0.45, y - s * 0.45, x + s * 0.45, y + s * 0.45), fill=col)
    cv.d.ellipse(cv.S(x - s * 0.37, y - s * 0.37, x + s * 0.37, y + s * 0.37), fill=AMBER_L)
    cv.d.ellipse(cv.S(x - s * 0.08, y - s * 0.62, x + s * 0.08, y - s * 0.46), outline=col, width=3 * cv.ss)
    for k in range(12):
        a = math.pi / 6 * k
        cv.d.line(cv.S(x + math.cos(a) * s * 0.3, y + math.sin(a) * s * 0.3, x + math.cos(a) * s * 0.35,
                       y + math.sin(a) * s * 0.35), fill=col, width=cv.ss)
    am = math.radians(minute * 6 - 90); ah = math.radians((hour % 12) * 30 + minute * 0.5 - 90)
    cv.d.line(cv.S(x, y, x + math.cos(am) * s * 0.3, y + math.sin(am) * s * 0.3), fill=col, width=2 * cv.ss)
    cv.d.line(cv.S(x, y, x + math.cos(ah) * s * 0.2, y + math.sin(ah) * s * 0.2), fill=col, width=3 * cv.ss)

def o_tree(cv, x, base, s, col=INK, lights=True):
    for k in range(4):
        w = s * (0.55 - k * 0.11); yb = base - s * 0.08 - k * s * 0.24
        cv.d.polygon(cv.P([(x - w, yb), (x + w, yb), (x, yb - s * 0.36)]), fill=col)
    cv.d.rectangle(cv.S(x - s * 0.05, base - s * 0.08, x + s * 0.05, base), fill=col)
    if lights:
        rng = random.Random(4)
        for _ in range(26):
            t = rng.random(); yy = base - s * 0.1 - t * s * 0.9; ww = s * 0.5 * (1 - t * 0.85)
            xx = x + rng.uniform(-ww, ww)
            cv.glow(xx, yy, s * 0.03, AMBER, alpha=200, blur=s * 0.02)
        cv.glow(x, base - s * 1.05, s * 0.06, AMBER_L, alpha=255, blur=s * 0.03)

def o_cup(cv, x, y, s, col=SNOW):
    top, bot = y - s * 0.45, y + s * 0.45
    cv.d.polygon(cv.P([(x - s * 0.3, top), (x + s * 0.3, top), (x + s * 0.22, bot), (x - s * 0.22, bot)]), fill=col)
    for k in range(5):                      # the stripes
        a = -0.3 + k * 0.13
        cv.d.polygon(cv.P([(x + a * s, top), (x + (a + 0.06) * s, top), (x + (a + 0.06) * s * 0.75, bot),
                           (x + a * s * 0.75, bot)]), fill=AMBER_D)
    cv.d.rectangle(cv.S(x - s * 0.29, y - s * 0.12, x + s * 0.27, y + s * 0.12), fill=BROWN)
    cv.d.ellipse(cv.S(x - s * 0.32, top - s * 0.06, x + s * 0.32, top + s * 0.06), fill=INK)
    for k in (-0.12, 0.05, 0.2):
        pts = [(x + k * s + math.sin(t / 2.5) * s * 0.05, top - s * 0.08 - t * s * 0.06) for t in range(9)]
        cv.d.line(cv.P(pts), fill=SNOW + (180,), width=2 * cv.ss)

def o_train(cv, x, y, s, col=BROWN):
    cv.d.arc(cv.S(x - s * 0.9, y - s * 0.1, x + s * 0.9, y + s * 0.5), 180, 360, fill=AMBER_D, width=2 * cv.ss)
    cv.d.rectangle(cv.S(x - s * 0.55, y - s * 0.35, x - s * 0.1, y), fill=col)
    cv.d.rectangle(cv.S(x - s * 0.15, y - s * 0.5, x + s * 0.05, y), fill=col)
    cv.d.rectangle(cv.S(x - s * 0.5, y - s * 0.48, x - s * 0.4, y - s * 0.35), fill=col)
    for k in range(2):
        cv.d.rectangle(cv.S(x + s * (0.1 + k * 0.32), y - s * 0.28, x + s * (0.38 + k * 0.32), y), fill=col)
    for k in range(6):
        wx = x - s * 0.5 + k * s * 0.17
        cv.d.ellipse(cv.S(wx - s * 0.05, y - s * 0.03, wx + s * 0.05, y + s * 0.07), fill=INK)
    cv.glow(x - s * 0.45, y - s * 0.6, s * 0.12, SNOW, alpha=120)

def o_hatbox(cv, x, y, s, col=BROWN):
    for i, (dx, dy, w, h) in enumerate([(0, 0.15, 0.8, 0.5), (0.05, -0.3, 0.6, 0.4)]):
        cx, cy = x + dx * s, y + dy * s
        cv.d.rectangle(cv.S(cx - w * s / 2, cy - h * s / 2, cx + w * s / 2, cy + h * s / 2), fill=col)
        cv.d.ellipse(cv.S(cx - w * s / 2, cy - h * s / 2 - s * 0.06, cx + w * s / 2, cy - h * s / 2 + s * 0.06),
                     fill=lerp(col, AMBER_D, 0.5))
        cv.d.rectangle(cv.S(cx - w * s / 2, cy - h * s / 2 + s * 0.04, cx + w * s / 2, cy - h * s / 2 + s * 0.09), fill=AMBER_L)
    cv.d.rectangle(cv.S(x - s * 0.18, y + s * 0.1, x + s * 0.18, y + s * 0.24), fill=SNOW)

def o_card(cv, x, y, s, col=SNOW):
    for k, (dx, ang) in enumerate([(-0.3, -8), (0.0, 0), (0.3, 8)]):
        cx = x + dx * s
        pts = [(-0.22, -0.32), (0.22, -0.32), (0.22, 0.32), (-0.22, 0.32)]
        a = math.radians(ang)
        cv.d.polygon(cv.P([(cx + (px * math.cos(a) - py * math.sin(a)) * s, y + (px * math.sin(a) + py * math.cos(a)) * s)
                           for px, py in pts]), fill=col if k == 1 else FROST, outline=BROWN)
    o_tree(cv, x, y + s * 0.2, s * 0.4, col=BROWN, lights=False)

def o_passes(cv, x, y, s):
    for k, (dx, ang, c) in enumerate([(-0.18, -10, STEEL2), (0.18, 8, AMBER_D)]):
        a = math.radians(ang)
        pts = [(-0.4, -0.25), (0.4, -0.25), (0.4, 0.25), (-0.4, 0.25)]
        cx = x + dx * s
        cv.d.polygon(cv.P([(cx + (px * math.cos(a) - py * math.sin(a)) * s, y + (px * math.sin(a) + py * math.cos(a)) * s)
                           for px, py in pts]), fill=c, outline=INK)
        cv.d.ellipse(cv.S(cx + s * 0.18, y - s * 0.12, cx + s * 0.34, y + s * 0.04), outline=SNOW, width=2 * cv.ss)

def o_frame(cv, x, y, s, col=FROST):
    cv.d.rounded_rectangle(cv.S(x - s * 0.35, y - s * 0.45, x + s * 0.35, y + s * 0.45), radius=s * 0.08 * cv.ss, fill=col)
    cv.d.rounded_rectangle(cv.S(x - s * 0.25, y - s * 0.35, x + s * 0.25, y + s * 0.35), radius=s * 0.05 * cv.ss, fill=INK)
    cv.glow(x - s * 0.15, y - s * 0.3, s * 0.08, SNOW, alpha=160)

def o_jar(cv, x, y, s, col=FROST):
    cv.d.rounded_rectangle(cv.S(x - s * 0.32, y - s * 0.4, x + s * 0.32, y + s * 0.45), radius=s * 0.1 * cv.ss,
                           fill=lerp(col, AMBER_L, 0.4), outline=BROWN, width=2 * cv.ss)
    cv.d.rectangle(cv.S(x - s * 0.24, y - s * 0.55, x + s * 0.24, y - s * 0.4), fill=BROWN)
    rng = random.Random(9)
    for _ in range(22):
        ax, ay = x + rng.uniform(-0.24, 0.24) * s, y + rng.uniform(-0.25, 0.38) * s
        cv.d.ellipse(cv.S(ax - s * 0.05, ay - s * 0.03, ax + s * 0.05, ay + s * 0.03), fill=SNOW)

def o_spools(cv, x, y, s, col=BROWN):
    for k, dx in enumerate((-0.35, 0, 0.35)):
        cx = x + dx * s
        cv.d.rectangle(cv.S(cx - s * 0.12, y - s * 0.3, cx + s * 0.12, y + s * 0.3), fill=AMBER_D if k == 1 else col)
        cv.d.rectangle(cv.S(cx - s * 0.16, y - s * 0.36, cx + s * 0.16, y - s * 0.3), fill=INK)
        cv.d.rectangle(cv.S(cx - s * 0.16, y + s * 0.3, cx + s * 0.16, y + s * 0.36), fill=INK)
    cv.d.line(cv.P([(x, y - s * 0.1), (x + s * 0.2, y + s * 0.5), (x + s * 0.7, y + s * 0.42)]), fill=AMBER_L, width=2 * cv.ss)

def o_blankets(cv, x, y, s):
    for k in range(4):
        c = [BROWN, INK2, AMBER_D, STEEL][k]
        cv.d.rounded_rectangle(cv.S(x - s * 0.5, y + s * 0.3 - k * s * 0.2, x + s * 0.5, y + s * 0.48 - k * s * 0.2),
                               radius=s * 0.06 * cv.ss, fill=c)

def o_clock_wall(cv, x, y, s):
    rng = random.Random(18)
    for k in range(9):
        cx = x + (k % 3 - 1) * s * 0.55; cy = y + (k // 3 - 1) * s * 0.42
        r = s * rng.uniform(0.14, 0.2)
        cv.d.ellipse(cv.S(cx - r, cy - r, cx + r, cy + r), fill=AMBER_L, outline=BROWN, width=3 * cv.ss)
        a = math.radians(rng.choice([-90, -60, -30, 0, 200, 240, 300])); b = math.radians(rng.choice([-120, -90, 30, 150, 210]))
        cv.d.line(cv.S(cx, cy, cx + math.cos(a) * r * 0.8, cy + math.sin(a) * r * 0.8), fill=BROWN, width=2 * cv.ss)
        cv.d.line(cv.S(cx, cy, cx + math.cos(b) * r * 0.5, cy + math.sin(b) * r * 0.5), fill=BROWN, width=3 * cv.ss)

def o_magpie(cv, x, y, s, col=INK, necklace=True):
    """A magpie in profile: black with white belly and wing patch, long tail."""
    cv.d.polygon(cv.P([(x - s * 0.1, y), (x - s * 0.95, y + s * 0.18), (x - s * 0.95, y + s * 0.3), (x - s * 0.05, y + s * 0.14)]), fill=col)
    cv.d.ellipse(cv.S(x - s * 0.3, y - s * 0.22, x + s * 0.3, y + s * 0.2), fill=col)
    cv.d.ellipse(cv.S(x - s * 0.08, y - s * 0.08, x + s * 0.24, y + s * 0.18), fill=SNOW)
    cv.d.ellipse(cv.S(x - s * 0.24, y - s * 0.12, x - s * 0.02, y + s * 0.0), fill=SNOW)
    cv.d.ellipse(cv.S(x + s * 0.12, y - s * 0.38, x + s * 0.38, y - s * 0.12), fill=col)
    cv.d.polygon(cv.P([(x + s * 0.36, y - s * 0.28), (x + s * 0.55, y - s * 0.24), (x + s * 0.36, y - s * 0.2)]), fill=col)
    cv.d.line(cv.S(x, y + s * 0.18, x - s * 0.03, y + s * 0.38), fill=col, width=2 * cv.ss)
    cv.d.line(cv.S(x + s * 0.1, y + s * 0.18, x + s * 0.12, y + s * 0.38), fill=col, width=2 * cv.ss)
    if necklace:
        pts = [(x + s * 0.5 + math.sin(t / 3) * s * 0.06, y - s * 0.22 + t * s * 0.06) for t in range(10)]
        for px, py in pts:
            cv.d.ellipse(cv.S(px - s * 0.03, py - s * 0.03, px + s * 0.03, py + s * 0.03), fill=AMBER_L)
        cv.glow(pts[-1][0], pts[-1][1], s * 0.06, AMBER_L, alpha=255, blur=s * 0.03)

def o_brooch(cv, x, y, s):
    cv.glow(x, y, s * 0.6, AMBER, alpha=150)
    o_magpie(cv, x, y, s * 0.55, col=AMBER_D, necklace=False)

def o_lanterns(cv, x, y, s):
    for k, dx in enumerate((-0.45, 0, 0.45)):
        cx = x + dx * s; cy = y + (0.1 if k != 1 else -0.08) * s
        cv.d.line(cv.S(cx, cy - s * 0.5, cx, cy - s * 0.25), fill=INK, width=2 * cv.ss)
        cv.d.rectangle(cv.S(cx - s * 0.13, cy - s * 0.25, cx + s * 0.13, cy + s * 0.15), fill=INK)
        cv.d.rectangle(cv.S(cx - s * 0.09, cy - s * 0.2, cx + s * 0.09, cy + s * 0.1), fill=AMBER_L)
        cv.glow(cx, cy - s * 0.05, s * 0.3, AMBER, alpha=120)

def o_stamp(cv, x, y, s):
    cv.d.rectangle(cv.S(x - s * 0.55, y - s * 0.35, x + s * 0.55, y + s * 0.35), fill=AMBER_D, outline=INK, width=2 * cv.ss)
    cv.d.ellipse(cv.S(x - s * 0.25, y - s * 0.25, x + s * 0.25, y + s * 0.25), outline=SNOW, width=3 * cv.ss)
    cv.d.line(cv.S(x, y, x, y - s * 0.2), fill=SNOW, width=3 * cv.ss)       # the hand points at 12: no clue here

OBJECTS = {"envelope": o_envelope, "ledger": o_ledger, "drum": o_drum, "glove": o_glove, "parcel": o_parcel,
           "watch": o_watch, "cup": o_cup, "train": o_train, "hatbox": o_hatbox, "card": o_card, "passes": o_passes,
           "frame": o_frame, "jar": o_jar, "spools": o_spools, "blankets": o_blankets, "lanterns": o_lanterns,
           "stamp": o_stamp, "clocks": o_clock_wall}

# ---------------------------------------------------------------- composed scenes
def street_with_window(cv, obj, seed=1, figure_at=None, objscale=0.42, panes=(1, 1)):
    w, h = cv.W, cv.H
    sky(cv, y1=h)
    skyline(cv, h * 0.48, seed=seed, col=INK, lit=0.1, height=(0.1, 0.32))
    facade(cv, h * 0.12, h * 0.8)
    box = (w * 0.26, h * 0.24, w * 0.74, h * 0.74)
    inner = shop_window(cv, box, panes=panes)
    ground(cv, h * 0.8)
    if obj:
        OBJECTS[obj](cv, (inner[0] + inner[2]) / 2, (inner[1] + inner[3]) / 2 + h * 0.03, (inner[3] - inner[1]) * objscale * 2)
    lamp(cv, w * 0.12, h * 0.86, h * 0.62)
    if figure_at:
        figure(cv, w * figure_at, h * 0.97, h * 0.42)
    snow(cv, int(w * h / 900), seed=seed + 10)

def scene_tram(cv, seed=4, number="7", figure_at=0.72):
    w, h = cv.W, cv.H
    sky(cv); skyline(cv, h * 0.55, seed=seed, lit=0.14)
    ground(cv, h * 0.72)
    for k in range(2):                      # rails
        cv.d.line(cv.P([(0, h * (0.8 + k * 0.05)), (w, h * (0.78 + k * 0.05))]), fill=STEEL, width=2 * cv.ss)
    x0, x1, y0, y1 = w * 0.12, w * 0.62, h * 0.36, h * 0.76
    cv.d.rounded_rectangle(cv.S(x0, y0, x1, y1), radius=18 * cv.ss, fill=INK2)
    cv.d.rectangle(cv.S(x0, y1 - h * 0.08, x1, y1 - h * 0.06), fill=STEEL)
    for k in range(5):
        wx = x0 + 14 + k * (x1 - x0 - 20) / 5
        cv.d.rectangle(cv.S(wx, y0 + h * 0.06, wx + (x1 - x0) / 5 - 14, y0 + h * 0.18), fill=AMBER)
    cv.rect_glow((x0, y0, x1, y0 + h * 0.2), AMBER, alpha=70, blur=18)
    cv.d.line(cv.S((x0 + x1) / 2, y0, (x0 + x1) / 2 + w * 0.1, 0), fill=INK, width=3 * cv.ss)   # pole to the wire
    cv.d.line(cv.S(0, h * 0.06, w, h * 0.02), fill=INK, width=2 * cv.ss)
    cv.d.rectangle(cv.S(x1 - w * 0.09, y0 + h * 0.02, x1 - w * 0.02, y0 + h * 0.055), fill=AMBER_L)
    for k in range(3):
        cv.d.ellipse(cv.S(x0 + 30 + k * (x1 - x0 - 60) / 2 - 10, y1 - 10, x0 + 30 + k * (x1 - x0 - 60) / 2 + 10, y1 + 10), fill=INK)
    # shelter
    sx = w * 0.78
    cv.d.rectangle(cv.S(sx - w * 0.08, h * 0.42, sx + w * 0.1, h * 0.45), fill=INK)
    cv.d.rectangle(cv.S(sx - w * 0.075, h * 0.45, sx - w * 0.07, h * 0.78), fill=INK)
    cv.d.rectangle(cv.S(sx + w * 0.09, h * 0.45, sx + w * 0.095, h * 0.78), fill=INK)
    cv.d.ellipse(cv.S(sx - 14, h * 0.32, sx + 14, h * 0.32 + 28), fill=STEEL2)
    lamp(cv, w * 0.95, h * 0.8, h * 0.6)
    if figure_at:
        figure(cv, w * figure_at, h * 0.94, h * 0.38)
    snow(cv, int(w * h / 800), seed=seed + 3)

def scene_stairs(cv, seed=5):
    w, h = cv.W, cv.H
    interior(cv, h * 0.7)
    hanging_lamp(cv, w * 0.2, h * 0.18)
    n = 9
    for k in range(n):                      # a grand staircase rising to the right, cel-shaded
        x = w * 0.35 + k * w * 0.06; y = h * 0.9 - k * h * 0.08
        cv.d.rectangle(cv.S(x, y, w, y + h * 0.08), fill=INK if k % 2 else INK2)
        cv.d.line(cv.S(x, y, w, y), fill=STEEL, width=cv.ss)
    cv.d.line(cv.P([(w * 0.35, h * 0.62), (w * 0.95, h * 0.0)]), fill=AMBER_D, width=3 * cv.ss)   # brass handrail
    for k in range(10):
        x = w * 0.37 + k * w * 0.058
        cv.d.line(cv.S(x, h * 0.6 - k * h * 0.064, x, h * 0.86 - k * h * 0.08), fill=INK, width=2 * cv.ss)
    figure(cv, w * 0.62, h * 0.62, h * 0.36, shadow=(-1.2, 0.2))
    # a rocking horse in the toy hall below, lit amber
    rx, ry, s = w * 0.17, h * 0.86, h * 0.3
    cv.glow(rx, ry - s * 0.3, s * 0.7, AMBER, alpha=90)
    cv.d.arc(cv.S(rx - s * 0.6, ry - s * 0.3, rx + s * 0.6, ry + s * 0.25), 20, 160, fill=BROWN, width=4 * cv.ss)
    cv.d.polygon(cv.P([(rx - s * 0.35, ry - s * 0.2), (rx + s * 0.25, ry - s * 0.2), (rx + s * 0.3, ry - s * 0.45),
                       (rx + s * 0.45, ry - s * 0.65), (rx + s * 0.32, ry - s * 0.72), (rx + s * 0.12, ry - s * 0.45),
                       (rx - s * 0.35, ry - s * 0.45)]), fill=BROWN)

def scene_register(cv, seed=2):
    w, h = cv.W, cv.H
    interior(cv, h * 0.55)
    hanging_lamp(cv, w * 0.5, h * 0.14, r=20)
    cv.d.rectangle(cv.S(w * 0.15, h * 0.62, w * 0.85, h * 0.66), fill=BROWN)    # desk edge
    cv.d.rectangle(cv.S(w * 0.18, h * 0.66, w * 0.82, h), fill=INK)
    o_ledger(cv, w * 0.5, h * 0.55, h * 0.55, col=AMBER_L)
    o_passes(cv, w * 0.75, h * 0.56, h * 0.25)
    # gloved hand holding a pen, from the side
    cv.d.rounded_rectangle(cv.S(w * 0.24, h * 0.5, w * 0.36, h * 0.6), radius=12 * cv.ss, fill=INK)
    cv.d.line(cv.S(w * 0.33, h * 0.52, w * 0.42, h * 0.44), fill=INK, width=4 * cv.ss)

def scene_tree(cv, seed=10):
    w, h = cv.W, cv.H
    interior(cv, h * 0.78)
    for k in range(4):                      # gallery balconies
        cv.d.rectangle(cv.S(0, h * (0.12 + k * 0.16), w, h * (0.13 + k * 0.16)), fill=INK)
    o_tree(cv, w * 0.5, h * 0.95, h * 0.85)
    for k, fx in enumerate((0.18, 0.3, 0.7, 0.84)):
        figure(cv, w * fx, h * (1.02 + 0.02 * (k % 2)), h * 0.34, hat=k % 2 == 0, shadow=None)
    snow(cv, 40, seed=seed, alpha=(30, 80))

def scene_park(cv, seed=11):
    w, h = cv.W, cv.H
    sky(cv); skyline(cv, h * 0.5, seed=seed, lit=0.08, height=(0.06, 0.2))
    ground(cv, h * 0.62, col=(40, 52, 78))
    rng = random.Random(seed)
    for k in range(5):                      # bare trees
        x = w * (0.1 + k * 0.2) + rng.uniform(-20, 20); base = h * 0.66
        cv.d.line(cv.S(x, base, x, base - h * 0.4), fill=INK, width=6 * cv.ss)
        for j in range(5):
            yy = base - h * (0.18 + j * 0.05); s = 1 if j % 2 else -1
            cv.d.line(cv.S(x, yy, x + s * h * 0.12, yy - h * 0.1), fill=INK, width=3 * cv.ss)
    for k in range(0, w, 18):               # railings
        cv.d.line(cv.S(k, h * 0.72, k, h * 0.86), fill=INK, width=3 * cv.ss)
    cv.d.line(cv.S(0, h * 0.74, w, h * 0.74), fill=INK, width=3 * cv.ss)
    bx = w * 0.62
    cv.d.rectangle(cv.S(bx - 60, h * 0.8, bx + 60, h * 0.83), fill=INK)
    cv.d.rectangle(cv.S(bx - 60, h * 0.83, bx - 54, h * 0.9), fill=INK)
    cv.d.rectangle(cv.S(bx + 54, h * 0.83, bx + 60, h * 0.9), fill=INK)
    cv.d.rectangle(cv.S(bx - 58, h * 0.795, bx + 58, h * 0.805), fill=SNOW)
    lamp(cv, w * 0.86, h * 0.9, h * 0.6)
    # one warm window across the park
    cv.d.rectangle(cv.S(w * 0.3, h * 0.36, w * 0.34, h * 0.42), fill=AMBER)
    cv.glow(w * 0.32, h * 0.39, 30, AMBER, alpha=90)
    snow(cv, int(w * h / 700), seed=seed + 5)

def scene_grand(cv, seed=24):
    """The Grand Window: curtains drawn back, a magpie stealing a necklace from a gloved hand."""
    w, h = cv.W, cv.H
    sky(cv); facade(cv, 0, h * 0.86)
    box = (w * 0.18, h * 0.12, w * 0.82, h * 0.8)
    inner = shop_window(cv, box, panes=(1, 1), awning=False)
    for side in (0, 1):                     # curtains
        x = inner[0] if side == 0 else inner[2]
        sgn = 1 if side == 0 else -1
        cv.d.polygon(cv.P([(x, inner[1]), (x + sgn * w * 0.12, inner[1]), (x + sgn * w * 0.05, inner[3]), (x, inner[3])]), fill=INK)
        for k in range(3):
            cv.d.line(cv.S(x + sgn * w * (0.03 + k * 0.03), inner[1], x + sgn * w * (0.015 + k * 0.012), inner[3]),
                      fill=INK2, width=2 * cv.ss)
    cx, cy = (inner[0] + inner[2]) / 2, (inner[1] + inner[3]) / 2
    o_magpie(cv, cx - w * 0.04, cy - h * 0.02, h * 0.3)
    # a gloved hand reaching up from the right, holding out the necklace
    hx, hy = cx + w * 0.16, cy + h * 0.2
    cv.d.polygon(cv.P([(hx + w * 0.2, cy + h * 0.45), (hx + w * 0.12, cy + h * 0.45), (hx - w * 0.02, hy + h * 0.02),
                       (hx + w * 0.05, hy - h * 0.04)]), fill=INK)
    cv.d.ellipse(cv.S(hx - w * 0.045, hy - h * 0.07, hx + w * 0.035, hy + h * 0.03), fill=INK)
    ground(cv, h * 0.86)
    for k, fx in enumerate((0.1, 0.24, 0.76, 0.9)):
        figure(cv, w * fx, h * 1.05, h * 0.36, hat=k % 2 == 1, shadow=None)
    snow(cv, int(w * h / 800), seed=seed)

SCENES = {
    1: ("window", "envelope", 0.78), 2: ("register", None, None), 3: ("window", "drum", 0.2),
    4: ("tram", "", 0.72), 5: ("stairs", None, None), 6: ("tram", "7", None), 7: ("window", "glove", 0.8),
    8: ("window", "parcel", None), 9: ("window", "watch", 0.22), 10: ("tree", None, None), 11: ("park", None, None),
    12: ("window", "cup", None), 13: ("window", "lanterns", 0.8), 14: ("window", "train", 0.2),
    15: ("window", "spools", None), 16: ("window", "stamp", 0.78), 17: ("window", "hatbox", 0.2),
    18: ("window", "clocks", None), 19: ("window", "card", 0.8), 20: ("window", "passes", None),
    21: ("window", "blankets", 0.22), 22: ("window", "frame", None), 23: ("window", "jar", 0.8), 24: ("grand", None, None),
}

def scene(day, w, h, grain=12):
    cv = Canvas(w, h)
    kind, obj, fig = SCENES[day]
    if kind == "window":
        street_with_window(cv, obj, seed=day, figure_at=fig)
    elif kind == "tram":
        scene_tram(cv, seed=day, figure_at=fig)
    elif kind == "stairs":
        scene_stairs(cv, seed=day)
    elif kind == "register":
        scene_register(cv, seed=day)
    elif kind == "tree":
        scene_tree(cv, seed=day)
    elif kind == "park":
        scene_park(cv, seed=day)
    elif kind == "grand":
        scene_grand(cv, seed=day)
    return cv.finish(grain=grain, seed=day)

def storefront(w, h, seed=7, windows=5, lit=None, figure_at=0.5, snow_n=None, grain=12):
    """Quillon's at night from across Lantern Street: a row of amber windows under a long facade.
    Used for the cover and the trailer."""
    cv = Canvas(w, h)
    sky(cv); skyline(cv, h * 0.34, seed=seed, lit=0.08, height=(0.08, 0.2))
    facade(cv, h * 0.18, h * 0.78)
    for k in range(3):                      # upper floors: rows of small dim windows
        for j in range(12):
            x = w * (0.04 + j * 0.08); y = h * (0.22 + k * 0.08)
            cv.d.rectangle(cv.S(x, y, x + w * 0.035, y + h * 0.045), fill=NIGHT2 if (j + k) % 5 else AMBER_D)
    n = windows; gap = w * 0.03; ww = (w - gap * (n + 1)) / n
    lit = lit if lit is not None else list(range(n))
    for k in range(n):
        x0 = gap + k * (ww + gap)
        if k in lit:
            shop_window(cv, (x0, h * 0.5, x0 + ww, h * 0.74), panes=(1, 1), awning=True)
        else:
            cv.d.rectangle(cv.S(x0, h * 0.5, x0 + ww, h * 0.74), fill=NIGHT1, outline=INK, width=6 * cv.ss)
    ground(cv, h * 0.78)
    lamp(cv, w * 0.06, h * 0.9, h * 0.6)
    lamp(cv, w * 0.94, h * 0.9, h * 0.6)
    if figure_at is not None:
        figure(cv, w * figure_at, h * 1.0, h * 0.42)
    snow(cv, snow_n or int(w * h / 600), seed=seed)
    return cv.finish(grain=grain, seed=seed)

if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "previews", "art")
    os.makedirs(out, exist_ok=True)
    sheet = Image.new("RGB", (4 * 420, 6 * 150), (0, 0, 0))
    for d in range(1, 25):
        im = scene(d, 840, 300)
        sheet.paste(im.resize((420, 150)), (((d - 1) % 4) * 420, ((d - 1) // 4) * 150))
    sheet.save(os.path.join(out, "scenes.jpg"), quality=88)
    storefront(1200, 1500).save(os.path.join(out, "storefront.jpg"), quality=88)
    print("ok")
