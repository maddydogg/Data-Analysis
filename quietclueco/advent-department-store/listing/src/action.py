"""Action look for the second listing variant of The Windows at Quillon's ("v2 action").

Same world and palette as art.py (snowy night, amber shop windows, silhouettes seen from behind, no
faces), pushed towards a 90s anime action key frame: dutch angles, a store towering in steep
perspective, manga focus lines, motion streaks in the snow, a figure running away from the camera
with an amber rim light, a striped cup knocked over mid-splash, a glint on a brass brooch, and title
type with a hard outline and an offset shadow. Everything is drawn with code (Pillow).
"""
import math, random
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import art
from art import NIGHT0, NIGHT1, NIGHT2, INK, INK2, STEEL, STEEL2, FROST, SNOW, AMBER, AMBER_D, AMBER_L, BROWN

# ---------------------------------------------------------------- geometry
def _solve(A, b):
    n = len(b); M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c])); M[c], M[p] = M[p], M[c]
        for r in range(n):
            if r != c:
                f = M[r][c] / M[c][c]
                M[r] = [x - f * y for x, y in zip(M[r], M[c])]
    return [M[i][n] / M[i][i] for i in range(n)]

class Quad:
    """Projective map from the unit square (u right, v down) to a quad on screen:
    corners top-left, top-right, bottom-right, bottom-left. Gives true perspective foreshortening."""
    def __init__(self, tl, tr, br, bl):
        src = [(0, 0), (1, 0), (1, 1), (0, 1)]; dst = [tl, tr, br, bl]
        A, b = [], []
        for (u, v), (x, y) in zip(src, dst):
            A.append([u, v, 1, 0, 0, 0, -u * x, -v * x]); b.append(x)
            A.append([0, 0, 0, u, v, 1, -u * y, -v * y]); b.append(y)
        self.h = _solve(A, b)

    def __call__(self, u, v):
        a, b, c, d, e, f, g, h = self.h
        w = g * u + h * v + 1
        return ((a * u + b * v + c) / w, (d * u + e * v + f) / w)

    def poly(self, u0, v0, u1, v1):
        return [self(u0, v0), self(u1, v0), self(u1, v1), self(u0, v1)]

# ---------------------------------------------------------------- manga effects
def focus_lines(cv, cx, cy, n=160, r_in=(0.18, 0.34), col=SNOW, alpha=(30, 110), width=(2, 9), seed=1, reach=None):
    """Manga focus lines (shuchusen): thin wedges pointing at (cx, cy) from beyond the frame edge."""
    rng = random.Random(seed); L = cv.layer(); d = ImageDraw.Draw(L)
    R = reach or math.hypot(cv.W, cv.H)
    for _ in range(n):
        a = rng.uniform(0, 2 * math.pi)
        r0 = min(cv.W, cv.H) * rng.uniform(*r_in)
        w = rng.uniform(*width)
        ca, sa = math.cos(a), math.sin(a)
        p0 = (cx + ca * r0, cy + sa * r0)
        q1 = (cx + ca * R - sa * w, cy + sa * R + ca * w); q2 = (cx + ca * R + sa * w, cy + sa * R - ca * w)
        d.polygon(cv.P([p0, q1, q2]), fill=col + (rng.randint(*alpha),))
    cv.img.alpha_composite(L)

def streaks(cv, n, angle=-62, length=(30, 140), col=SNOW, alpha=(40, 170), width=(1, 3), seed=2, area=None):
    """Snow streaking past the camera: motion-blurred flakes as long thin lines."""
    rng = random.Random(seed); L = cv.layer(); d = ImageDraw.Draw(L)
    x0, y0, x1, y1 = area or (0, 0, cv.W, cv.H)
    a = math.radians(angle); ca, sa = math.cos(a), math.sin(a)
    for _ in range(n):
        x, y = rng.uniform(x0 - 100, x1 + 100), rng.uniform(y0 - 100, y1 + 100)
        ln = rng.uniform(*length); w = rng.uniform(*width)
        d.line(cv.S(x, y, x + ca * ln, y - sa * ln), fill=col + (rng.randint(*alpha),), width=max(1, int(w * cv.ss)))
    cv.img.alpha_composite(L.filter(ImageFilter.GaussianBlur(0.6 * cv.ss)))

def halftone(cv, box, col=INK, step=14, r_max=5.0, direction=(0, 1), alpha=200):
    """Screentone dots growing along `direction` inside box (x0, y0, x1, y1)."""
    x0, y0, x1, y1 = box; L = cv.layer(); d = ImageDraw.Draw(L)
    dx, dy = direction
    for j, y in enumerate(range(int(y0), int(y1), step)):
        off = step / 2 if j % 2 else 0
        for x in range(int(x0 + off), int(x1), step):
            t = ((x - x0) / max(1, x1 - x0)) * dx + ((y - y0) / max(1, y1 - y0)) * dy
            r = r_max * max(0.0, min(1.0, t))
            if r > 0.4:
                d.ellipse(cv.S(x - r, y - r, x + r, y + r), fill=col + (alpha,))
    cv.img.alpha_composite(L)

def light_beam(cv, apex, a0, a1, length, col=AMBER, alpha=60, blur=18):
    ax, ay = apex
    p1 = (ax + math.cos(math.radians(a0)) * length, ay + math.sin(math.radians(a0)) * length)
    p2 = (ax + math.cos(math.radians(a1)) * length, ay + math.sin(math.radians(a1)) * length)
    L = cv.layer(); ImageDraw.Draw(L).polygon(cv.P([apex, p1, p2]), fill=col + (alpha,))
    cv.img.alpha_composite(L.filter(ImageFilter.GaussianBlur(blur * cv.ss)))

def flare(cv, x, y, s, col=AMBER_L, alpha=235):
    """A four-point star glint with a soft halo."""
    cv.glow(x, y, s * 0.5, col, alpha=170)
    L = cv.layer(); d = ImageDraw.Draw(L); t = s * 0.06
    d.polygon(cv.P([(x - s, y), (x, y - t), (x + s, y), (x, y + t)]), fill=col + (alpha,))
    d.polygon(cv.P([(x, y - s * 1.2), (x - t, y), (x, y + s * 1.2), (x + t, y)]), fill=col + (alpha,))
    s2 = s * 0.45
    d.polygon(cv.P([(x - s2, y - s2), (x + t * 0.5, y - t * 0.5), (x + s2, y + s2), (x - t * 0.5, y + t * 0.5)]), fill=col + (150,))
    d.polygon(cv.P([(x + s2, y - s2), (x + t * 0.5, y + t * 0.5), (x - s2, y + s2), (x - t * 0.5, y - t * 0.5)]), fill=col + (150,))
    cv.img.alpha_composite(L.filter(ImageFilter.GaussianBlur(0.8 * cv.ss)))
    cv.glow(x, y, s * 0.12, (255, 250, 236), alpha=255, blur=s * 0.05)

# ---------------------------------------------------------------- the store, towering
def tower(cv, quad, cols=7, rows=8, seed=3, lit=0.3, band=(0.06, 0.8), shop=(0.83, 0.985), face=INK, trim=INK2,
          amber_bias=0.7, roof=True):
    """One facade of Quillon's on a perspective quad: stone face, pilasters, rows of windows (some
    amber), a cornice, and a band of tall display windows at street level."""
    rng = random.Random(seed); d = cv.d
    d.polygon(cv.P(quad.poly(0, 0, 1, 1)), fill=face)
    for k in range(cols + 1):                       # pilasters
        u = k / cols
        d.polygon(cv.P(quad.poly(u - 0.01, 0, u + 0.01, shop[0] - 0.01)), fill=trim)
    if roof:
        d.polygon(cv.P(quad.poly(-0.01, 0, 1.01, 0.025)), fill=trim)
    top, bot = band; span = (bot - top) / rows
    for r in range(rows):
        v = top + r * span
        d.polygon(cv.P(quad.poly(0, v - 0.004, 1, v + 0.002)), fill=trim)
        for c in range(cols):
            u0 = c / cols + 0.03; u1 = (c + 1) / cols - 0.03
            v0 = v + span * 0.2; v1 = v + span * 0.86
            on = rng.random() < lit
            col = (AMBER if rng.random() < amber_bias else AMBER_D) if on else NIGHT1
            pts = quad.poly(u0, v0, u1, v1)
            if on:
                cx = sum(p[0] for p in pts) / 4; cy = sum(p[1] for p in pts) / 4
                cv.glow(cx, cy, abs(pts[1][0] - pts[0][0]) * 0.8, AMBER, alpha=55)
            d.polygon(cv.P(pts), fill=col)
            mu = (u0 + u1) / 2
            d.line(cv.P([quad(mu, v0), quad(mu, v1)]), fill=face, width=max(1, cv.ss * 2))
            mv = v0 + (v1 - v0) * 0.4
            d.line(cv.P([quad(u0, mv), quad(u1, mv)]), fill=face, width=max(1, cv.ss * 2))
    v0, v1 = shop
    d.polygon(cv.P(quad.poly(0, v0 - 0.025, 1, v0 - 0.005)), fill=trim)   # fascia over the shop windows
    for c in range(cols):
        u0 = c / cols + 0.025; u1 = (c + 1) / cols - 0.025
        pts = quad.poly(u0, v0, u1, v1)
        cx = sum(p[0] for p in pts) / 4; cy = sum(p[1] for p in pts) / 4
        cv.glow(cx, cy, abs(pts[1][0] - pts[0][0]) * 0.9, AMBER, alpha=100)
        d.polygon(cv.P(pts), fill=AMBER_L)
        d.polygon(cv.P(quad.poly(u0 + 0.008, v0 + (v1 - v0) * 0.25, u1 - 0.008, v1)), fill=AMBER)

def wall_clock(cv, cx, cy, r, hh=21, mm=20):
    """A big round store clock with an amber face."""
    d = cv.d
    cv.glow(cx, cy, r * 1.7, AMBER, alpha=110)
    d.ellipse(cv.S(cx - r * 1.14, cy - r * 1.14, cx + r * 1.14, cy + r * 1.14), fill=INK)
    d.ellipse(cv.S(cx - r, cy - r, cx + r, cy + r), fill=AMBER_L, outline=AMBER_D, width=max(2, int(r * 0.07 * cv.ss)))
    for k in range(12):
        a = math.pi / 6 * k
        d.line(cv.S(cx + math.cos(a) * r * 0.76, cy + math.sin(a) * r * 0.76,
                    cx + math.cos(a) * r * 0.9, cy + math.sin(a) * r * 0.9), fill=BROWN, width=max(2, int(r * 0.06 * cv.ss)))
    clock_hands(cv, cx, cy, r, hh, mm)

def clock_hands(cv, cx, cy, r, hh, mm, col=INK):
    am = math.radians(mm * 6 - 90); ah = math.radians((hh % 12 + mm / 60) * 30 - 90)
    cv.d.line(cv.S(cx, cy, cx + math.cos(ah) * r * 0.5, cy + math.sin(ah) * r * 0.5), fill=col, width=int(r * 0.09 * cv.ss))
    cv.d.line(cv.S(cx, cy, cx + math.cos(am) * r * 0.78, cy + math.sin(am) * r * 0.78), fill=col, width=int(r * 0.06 * cv.ss))
    cv.d.ellipse(cv.S(cx - r * 0.07, cy - r * 0.07, cx + r * 0.07, cy + r * 0.07), fill=col)

# ---------------------------------------------------------------- the runner
# A person running away from the camera and to the right, seen from behind in three-quarter view:
# hat, turned-up collar, body leaning into the run, a long coat whose tails stream back, one leg
# reaching forward and one kicked up behind, arms pumping. No face is ever visible.
# Joints in units of height h, origin at the ground under the hips, y up is negative.
POSE_A = dict(hip=(0.0, -0.5), sh=(0.08, -0.79), head=(0.11, -0.885),
              fhip=(0.05, -0.48), fknee=(0.24, -0.31), ffoot=(0.3, -0.04),        # front leg reaching forward
              bhip=(-0.02, -0.48), bknee=(-0.05, -0.24), bfoot=(-0.29, -0.2),     # back leg kicked up
              fsh=(0.16, -0.77), fel=(0.26, -0.64), fhand=(0.33, -0.67),          # front arm forward
              bsh=(-0.02, -0.76), bel=(-0.12, -0.62), bhand=(-0.21, -0.53))       # back arm swung back
POSE_B = dict(hip=(0.0, -0.53), sh=(0.08, -0.82), head=(0.11, -0.915),
              fhip=(0.05, -0.51), fknee=(0.04, -0.27), ffoot=(-0.2, -0.22),
              bhip=(-0.02, -0.51), bknee=(0.16, -0.34), bfoot=(0.24, -0.07),
              fsh=(0.16, -0.8), fel=(0.17, -0.63), fhand=(0.24, -0.53),
              bsh=(-0.02, -0.79), bel=(0.05, -0.67), bhand=(0.14, -0.78))

def _pose(phase):
    t = 0.5 - 0.5 * math.cos(phase * 2 * math.pi)
    return {k: (a[0] + (POSE_B[k][0] - a[0]) * t, a[1] + (POSE_B[k][1] - a[1]) * t) for k, a in POSE_A.items()}, t

def runner(cv, x, base, h, col=INK, rim=AMBER, phase=0.0, flip=False, glow=True, tail=0.0):
    """Draw the runner; phase in [0, 1) animates the stride, tail in [0, 1] flutters the coat."""
    s = h; sg = -1 if flip else 1
    J, t = _pose(phase)
    def pt(p):
        return (x + sg * p[0] * s, base + p[1] * s)
    def P(pts):
        return cv.P([pt(p) for p in pts])
    L = cv.layer(); d = ImageDraw.Draw(L); C = col + (255,)
    def limb(a, b, w):
        d.line(P([a, b]), fill=C, width=int(w * s * cv.ss))
        r = w * 0.5
        d.ellipse(P([(b[0] - r, b[1] - r), (b[0] + r, b[1] + r)]), fill=C)
    for leg in ("b", "f"):
        limb(J[leg + "hip"], J[leg + "knee"], 0.085); limb(J[leg + "knee"], J[leg + "foot"], 0.07)
        fx, fy = J[leg + "foot"]
        back = fx < J[leg + "knee"][0]
        if back:      # sole towards us
            d.polygon(P([(fx - 0.06, fy - 0.035), (fx + 0.02, fy - 0.05), (fx + 0.035, fy + 0.03), (fx - 0.06, fy + 0.04)]), fill=C)
        else:
            d.polygon(P([(fx - 0.03, fy - 0.03), (fx + 0.09, fy - 0.005), (fx + 0.085, fy + 0.03), (fx - 0.035, fy + 0.03)]), fill=C)
    hx, hy = J["hip"]; sx, sy = J["sh"]
    fl = 0.04 * math.sin(tail * 2 * math.pi)
    coat = [(sx - 0.13, sy - 0.01), (sx - 0.04, sy - 0.04), (sx + 0.08, sy - 0.035), (sx + 0.14, sy + 0.0),
            (sx + 0.15, sy + 0.12), (hx + 0.13, hy + 0.04), (hx + 0.16, hy + 0.12), (hx + 0.09, hy + 0.14),
            (hx - 0.03, hy + 0.13 + fl * 0.5), (hx - 0.16, hy + 0.15 + fl), (hx - 0.33, hy + 0.12 + fl),
            (hx - 0.46, hy + 0.06 + fl * 1.5), (hx - 0.36, hy + 0.04), (hx - 0.42, hy - 0.02 + fl),
            (hx - 0.24, hy - 0.05), (hx - 0.13, hy - 0.14), (sx - 0.15, sy + 0.12)]
    d.polygon(P(coat), fill=C)
    for arm in ("b", "f"):
        limb(J[arm + "sh"], J[arm + "el"], 0.075); limb(J[arm + "el"], J[arm + "hand"], 0.062)
    # head seen from behind, collar up, hat tilted forward with the run
    hx2, hy2 = J["head"]
    d.polygon(P([(sx - 0.1, sy - 0.02), (sx + 0.11, sy - 0.03), (hx2 + 0.07, hy2 + 0.06), (hx2 - 0.07, hy2 + 0.07)]), fill=C)
    d.ellipse(P([(hx2 - 0.062, hy2 - 0.065), (hx2 + 0.062, hy2 + 0.065)]), fill=C)
    hb = hy2 + 0.022                    # the brim sits low, across the back of the head
    d.polygon(P([(hx2 - 0.15, hb + 0.005), (hx2 + 0.165, hb - 0.025), (hx2 + 0.16, hb - 0.045), (hx2 - 0.155, hb - 0.015)]), fill=C)
    d.polygon(P([(hx2 - 0.075, hb - 0.01), (hx2 + 0.085, hb - 0.03), (hx2 + 0.07, hb - 0.105), (hx2 + 0.01, hb - 0.09),
                 (hx2 - 0.06, hb - 0.1)]), fill=C)
    a = L.split()[3]
    if glow:
        g = Image.new("RGBA", L.size, rim + (0,))
        g.putalpha(a.filter(ImageFilter.GaussianBlur(h * 0.018 * cv.ss)).point(lambda v: int(v * 0.8)))
        cv.img.alpha_composite(g)
    cv.img.alpha_composite(L)
    # rim light on the edges facing the store (up and ahead): mask minus itself shifted back and down
    k = max(2, int(h * 0.007 * cv.ss))
    edge = ImageChops.subtract(a, ImageChops.offset(a, -sg * k, k)).filter(ImageFilter.GaussianBlur(0.6 * cv.ss))
    r = Image.new("RGBA", L.size, rim + (0,)); r.putalpha(edge)
    cv.img.alpha_composite(r)

def kicked_snow(cv, x, base, h, seed=5, n=60):
    rng = random.Random(seed); L = cv.layer(); d = ImageDraw.Draw(L)
    for _ in range(n):
        a = math.radians(rng.uniform(200, 340)); r = rng.uniform(0.05, 0.5) * h
        px, py = x + math.cos(a) * r * 1.4, base + math.sin(a) * r * 0.5
        s = rng.uniform(1.5, 6)
        d.ellipse(cv.S(px - s, py - s, px + s, py + s), fill=SNOW + (rng.randint(80, 220),))
    cv.img.alpha_composite(L.filter(ImageFilter.GaussianBlur(0.8 * cv.ss)))

# ---------------------------------------------------------------- the cup, knocked over
def cup_splash(cv, x, y, s, angle=-28, t=1.0, seed=4):
    """The striped paper cup tipping over, cocoa leaping out in an arc of drops. t in [0, 1] grows the splash."""
    L = cv.layer(); d = ImageDraw.Draw(L)
    a = math.radians(angle); ca, sa = math.cos(a), math.sin(a)
    def R(px, py):
        return (x + (px * ca - py * sa) * s, y + (px * sa + py * ca) * s)
    top, bot = -0.45, 0.45
    d.polygon(cv.P([R(-0.3, top), R(0.3, top), R(0.22, bot), R(-0.22, bot)]), fill=SNOW + (255,))
    for k in range(5):
        u = -0.3 + k * 0.13
        d.polygon(cv.P([R(u, top), R(u + 0.06, top), R((u + 0.06) * 0.75, bot), R(u * 0.75, bot)]), fill=AMBER_D + (255,))
    d.polygon(cv.P([R(-0.29, -0.12), R(0.29, -0.12), R(0.27, 0.12), R(-0.27, 0.12)]), fill=BROWN + (255,))
    d.polygon(cv.P([R(0.32 * math.cos(k / 20 * 2 * math.pi), top + 0.06 * math.sin(k / 20 * 2 * math.pi)) for k in range(20)]),
              fill=INK + (255,))
    cv.img.alpha_composite(L)
    # cocoa: a ribbon out of the mouth, then drops flying on
    rng = random.Random(seed); S = cv.layer(); sd = ImageDraw.Draw(S)
    mx, my = R(0, top - 0.02)
    dirx, diry = sa, -ca                     # out of the mouth
    pts = []
    for i in range(18):
        u = i / 17 * t
        px = mx + dirx * u * s * 1.4 + u * u * s * 0.5
        py = my + diry * u * s * 1.4 + u * u * s * 1.4
        pts.append((px, py))
    COCOA = (122, 66, 28)
    for i in range(len(pts) - 1):
        w = s * (0.18 - 0.12 * i / len(pts))
        sd.line(cv.P([pts[i], pts[i + 1]]), fill=COCOA + (255,), width=int(w * cv.ss))
    for i in range(int(26 * t)):
        u = rng.uniform(0.2, 1.2) * t
        px = mx + dirx * u * s * 1.5 + u * u * s * rng.uniform(0.2, 0.9) + rng.uniform(-0.15, 0.15) * s
        py = my + diry * u * s * 1.5 + u * u * s * rng.uniform(0.8, 1.6) + rng.uniform(-0.15, 0.15) * s
        r = s * rng.uniform(0.02, 0.06)
        sd.ellipse(cv.S(px - r, py - r * 1.25, px + r, py + r * 1.25), fill=COCOA + (255,))
        sd.ellipse(cv.S(px - r * 0.45, py - r * 0.9, px + r * 0.05, py - r * 0.3), fill=AMBER_L + (220,))
    cv.img.alpha_composite(S)
    hl = cv.layer(); ImageDraw.Draw(hl).line(cv.P(pts[1:12]), fill=AMBER_L + (210,), width=max(1, int(s * 0.03 * cv.ss)))
    cv.img.alpha_composite(hl)

MAGPIE = [(0.47, -0.16), (0.36, -0.2), (0.3, -0.27), (0.2, -0.26), (0.13, -0.17), (0.0, -0.1), (-0.2, -0.03),
          (-0.66, 0.12), (-0.71, 0.2), (-0.62, 0.22), (-0.16, 0.11), (0.02, 0.16), (0.2, 0.1), (0.3, -0.03),
          (0.36, -0.12), (0.47, -0.15)]
def brass_magpie(cv, x, y, s, angle=-8):
    """The brass magpie brooch: a magpie in profile (facing right) cut from brass, white enamel on the
    belly and wing, a dark keyline. Drawn about its centre (x, y); s = beak-to-tail length.
    Returns the point where the light catches (top of the head)."""
    a = math.radians(angle); ca, sa = math.cos(a), math.sin(a)
    def R(px, py):
        return (x + (px * ca - py * sa) * s, y + (px * sa + py * ca) * s)
    def poly(pts):
        return cv.P([R(px, py) for px, py in pts])
    L = cv.layer(); d = ImageDraw.Draw(L)
    legs = [[(0.0, 0.14), (-0.02, 0.27), (0.04, 0.28)], [(0.07, 0.13), (0.08, 0.27), (0.14, 0.28)]]
    d.polygon(poly(MAGPIE), fill=AMBER + (255,))
    for lg in legs:
        d.line(poly(lg), fill=AMBER_D + (255,), width=max(2, int(s * 0.025 * cv.ss)), joint="curve")
    d.polygon(poly([(-0.2, -0.03), (-0.66, 0.12), (-0.71, 0.2), (-0.62, 0.22), (-0.16, 0.11)]), fill=AMBER_D + (255,))
    d.line(poly([(-0.22, 0.03), (-0.66, 0.17)]), fill=AMBER + (255,), width=max(1, int(s * 0.012 * cv.ss)))
    d.polygon(poly([(-0.2, -0.02), (0.12, -0.13), (0.17, -0.05), (-0.04, 0.08)]), fill=AMBER_D + (255,))   # wing
    d.polygon(poly([(-0.11, 0.0), (0.08, -0.08), (0.11, -0.04), (-0.07, 0.04)]), fill=SNOW + (255,))       # wing enamel
    d.polygon(poly([(-0.08, 0.09), (0.06, 0.04), (0.21, 0.06), (0.18, 0.1), (0.02, 0.15)]), fill=SNOW + (255,))   # belly enamel
    d.polygon(poly([(0.28, -0.255), (0.2, -0.235), (0.12, -0.15), (0.0, -0.085), (0.0, -0.1), (0.12, -0.165), (0.2, -0.25)]),
              fill=AMBER_L + (255,))                                                                      # light along the back
    ex, ey = R(0.31, -0.19); r = s * 0.02
    d.ellipse(cv.S(ex - r, ey - r, ex + r, ey + r), fill=BROWN + (255,))
    al = L.split()[3]
    k = max(3, int(s * 0.022 * cv.ss)) | 1
    key = Image.new("RGBA", L.size, BROWN + (0,)); key.putalpha(al.filter(ImageFilter.MaxFilter(k)))
    sh = Image.new("RGBA", L.size, (0, 0, 0, 0)); sh.putalpha(al.point(lambda v: v * 140 // 255))
    cv.img.alpha_composite(ImageChops.offset(sh, int(s * 0.03 * cv.ss), int(s * 0.045 * cv.ss)).filter(ImageFilter.GaussianBlur(s * 0.02 * cv.ss)))
    cv.img.alpha_composite(key)
    cv.img.alpha_composite(L)
    return R(0.27, -0.25)

# ---------------------------------------------------------------- type
def slam_text(img, xy, text, fnt, fill=SNOW, stroke=NIGHT0, stroke_w=None, shadow=AMBER, shadow_off=None,
              angle=0, anchor="mm", glow=None):
    """Anime title-card type: hard dark outline, offset amber shadow, optional glow, optional tilt.
    Draws on an RGBA image; returns the bounding box of the drawn text."""
    sw = stroke_w if stroke_w is not None else max(2, int(fnt.size * 0.05))
    so = shadow_off if shadow_off is not None else (int(fnt.size * 0.05), int(fnt.size * 0.06))
    probe = ImageDraw.Draw(img)
    l, t, r, b = probe.textbbox((0, 0), text, font=fnt, anchor="lt", stroke_width=sw)
    pad = int(fnt.size * 0.6)
    W, H = r - l + 2 * pad + abs(so[0]), b - t + 2 * pad + abs(so[1])
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    ox, oy = pad - l, pad - t
    if glow:
        G = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(G).text((ox, oy), text, font=fnt, fill=glow + (200,), anchor="lt", stroke_width=sw * 2)
        L.alpha_composite(G.filter(ImageFilter.GaussianBlur(fnt.size * 0.18)))
    if shadow:
        d.text((ox + so[0], oy + so[1]), text, font=fnt, fill=shadow + (255,), anchor="lt", stroke_width=sw, stroke_fill=shadow)
    d.text((ox, oy), text, font=fnt, fill=fill + (255,), anchor="lt", stroke_width=sw, stroke_fill=stroke)
    if angle:
        L = L.rotate(angle, resample=Image.BICUBIC, expand=True)
    x, y = xy
    if anchor == "mm":
        px, py = int(x - L.width / 2), int(y - L.height / 2)
    elif anchor == "lm":
        px, py = int(x - pad), int(y - L.height / 2)
    else:
        px, py = int(x - pad), int(y - pad)
    img.alpha_composite(L, (px, py))
    return (px, py, px + L.width, py + L.height)

def tape(img, y, angle, text, fnt, h=None, col=AMBER, ink=NIGHT0, seed=1):
    """A diagonal band of amber barrier tape across the frame with a repeating line of text."""
    W, H = img.size; h = h or int(fnt.size * 1.7)
    long = int(math.hypot(W, H) * 1.3)
    band = Image.new("RGBA", (long, h), col + (255,)); d = ImageDraw.Draw(band)
    d.rectangle([0, 0, long, int(h * 0.08)], fill=ink); d.rectangle([0, h - int(h * 0.08), long, h], fill=ink)
    unit = text + "     /     "
    x = -random.Random(seed).randint(0, 400)
    while x < long:
        d.text((x, h / 2), unit, font=fnt, fill=ink, anchor="lm"); x += d.textlength(unit, font=fnt)
    band = band.rotate(angle, resample=Image.BICUBIC, expand=True)
    sh = Image.new("RGBA", band.size, (0, 0, 0, 0)); sh.putalpha(band.split()[3].point(lambda v: v * 120 // 255))
    sh = sh.filter(ImageFilter.GaussianBlur(10))
    cx, cy = W / 2, y
    img.alpha_composite(sh, (int(cx - band.width / 2 + 8), int(cy - band.height / 2 + 14)))
    img.alpha_composite(band, (int(cx - band.width / 2), int(cy - band.height / 2)))

def badge(img, xy, text, fnt, bg=AMBER, fg=NIGHT0, angle=0, outline=NIGHT0):
    d = ImageDraw.Draw(img)
    l, t, r, b = d.textbbox((0, 0), text, font=fnt)
    padx, pady = fnt.size * 0.55, fnt.size * 0.3
    W, H = int(r - l + 2 * padx), int(b - t + 2 * pady)
    ow = max(3, int(fnt.size * 0.07))
    L = Image.new("RGBA", (W + 2 * ow + 20, H + 2 * ow + 20), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
    ld.rounded_rectangle([10, 10, 10 + W + 2 * ow, 10 + H + 2 * ow], radius=(H + 2 * ow) / 2, fill=outline)
    ld.rounded_rectangle([10 + ow, 10 + ow, 10 + ow + W, 10 + ow + H], radius=H / 2, fill=bg)
    ld.text((10 + ow + W / 2, 10 + ow + H / 2), text, font=fnt, fill=fg, anchor="mm")
    if angle:
        L = L.rotate(angle, resample=Image.BICUBIC, expand=True)
    img.alpha_composite(L, (int(xy[0] - L.width / 2), int(xy[1] - L.height / 2)))

def seal(img, xy, r, top, big, bottom, f_small, f_big, angle=-12):
    """A round amber stamp: small text on top, a big number, small text below."""
    S = int(r * 2.4); L = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(L); c = S / 2
    d.ellipse([c - r - 8, c - r - 8, c + r + 8, c + r + 8], fill=NIGHT0)
    d.ellipse([c - r, c - r, c + r, c + r], fill=AMBER)
    d.ellipse([c - r * 0.9, c - r * 0.9, c + r * 0.9, c + r * 0.9], outline=NIGHT0, width=max(3, int(r * 0.03)))
    d.text((c, c - r * 0.52), top, font=f_small, fill=NIGHT0, anchor="mm")
    d.text((c, c + r * 0.04), big, font=f_big, fill=NIGHT0, anchor="mm")
    d.text((c, c + r * 0.55), bottom, font=f_small, fill=NIGHT0, anchor="mm")
    L = L.rotate(angle, resample=Image.BICUBIC)
    img.alpha_composite(L, (int(xy[0] - S / 2), int(xy[1] - S / 2)))

def shake(img, i, amp):
    """Camera shake: shift the frame by a pseudo-random offset (edges filled by stretching)."""
    if amp <= 0:
        return img
    rng = random.Random(i * 7919)
    dx, dy = int(rng.uniform(-amp, amp)), int(rng.uniform(-amp, amp))
    W, H = img.size; m = int(amp) + 2
    big = img.resize((W + 2 * m, H + 2 * m), Image.BILINEAR)
    return big.crop((m + dx, m + dy, m + dx + W, m + dy + H))

def motion_blur(img, dx, dy, n=8):
    """Directional blur by averaging shifted copies (for whip pans and smash zooms)."""
    if n <= 1 or (abs(dx) < 1 and abs(dy) < 1):
        return img
    base = img.convert("RGB"); acc = base
    for k in range(1, n):
        t = k / (n - 1) - 0.5
        sh = ImageChops.offset(base, int(dx * t), int(dy * t))
        acc = Image.blend(acc, sh, 1 / (k + 1))
    return acc.convert(img.mode)
