"""Compositions: the key art (cover, listing, video) and one vignette for each of the 24 windows.
Everything is built from the pieces in art.py. Returns PIL RGB images."""
import math, random
from PIL import Image, ImageDraw, ImageFilter
import art as A
from art import Canvas

DUSK_SKY = [A.NIGHT, A.NIGHT2, A.DUSK, (150, 160, 162), A.PEACH]
NIGHT_SKY = [(20, 32, 46), A.NIGHT, A.NIGHT2, A.DUSK]
DAY_SKY = [(150, 176, 182), (184, 200, 198), (222, 220, 204), A.CREAM]
WARM_SKY = [A.DUSK, (166, 164, 156), A.PEACH, (238, 206, 160)]

def mainland(cv, y, seed=1, col=(96, 112, 128), lights=True):
    W = cv.W
    A.hills(cv, [(-20, y), (W * 0.1, y - cv.H * 0.07), (W * 0.24, y - cv.H * 0.03), (W * 0.4, y - cv.H * 0.1),
                 (W * 0.55, y - cv.H * 0.05), (W * 0.7, y - cv.H * 0.12), (W * 0.86, y - cv.H * 0.06), (W + 20, y - cv.H * 0.09)],
            y + 2, col, hatch=A.shade(col, 0.85), seed=seed)
    if lights:
        rng = random.Random(seed)
        for _ in range(int(W / 60)):
            x = rng.uniform(0, W); yy = y - rng.uniform(2, cv.H * 0.03)
            cv.rect((x, yy - 2, x + 3, yy + 1), A.LAMP)

def keyart(w, h, seed=11, lit=True, figure=True, snow_n=None, ss=2, beam_angle=196, boat_x=0.43, finish=True,
           hz_frac=0.6, tower=0.33, fig_x=0.2, moon_xy=(0.86, 0.1), beams=True):
    """Candleholm at a winter dusk: the island and its white tower, the beam over the Sound, the mail boat
    coming in, and in the foreground, seen from behind on the jetty, a figure in a red knitted cap."""
    cv = Canvas(w, h, ss=ss)
    hz = h * hz_frac
    A.sky(cv, DUSK_SKY, y1=hz + 2, seed=seed)
    A.stars(cv, int(w * h / 9000), hz * 0.55, seed=seed)
    if moon_xy:
        A.moon(cv, w * moon_xy[0], h * moon_xy[1], min(w, h) * 0.03, sky_col=A.NIGHT)
    mainland(cv, hz, seed=seed)
    A.sea(cv, hz, h, top=A.SEA3, bottom=A.SEA, stroke=A.SEA_L, seed=seed)
    L = cv.layer(); ld = ImageDraw.Draw(L)
    ix = w * 0.66
    for k in range(16):
        yy = hz + 6 + k * (h - hz) * 0.035
        xx = ix - (k * w * 0.02) - w * 0.08
        ld.line(cv.P([(xx, yy), (xx + w * 0.05 + k * 2, yy)]), fill=A.LAMP + (90 - k * 4,), width=2 * cv.ss)
    cv.img.alpha_composite(L)
    ih = min(w, h)
    A.island(cv, ix, hz + ih * 0.07, w * 0.42, ih * 0.11, seed=seed)
    A.cottage(cv, ix + w * 0.05, hz - ih * 0.01, w * 0.1, ih * 0.045, lit=lit)
    A.boathouse(cv, ix - w * 0.16, hz + ih * 0.025, w * 0.05, ih * 0.03)
    A.lighthouse(cv, ix - w * 0.03, hz + ih * 0.005, h * tower, lit=lit, beam_angle=beam_angle, beams=beams)
    cv.lamp_xy = (ix - w * 0.03, hz + ih * 0.005 - h * tower * 0.88)
    A.boat(cv, w * boat_x, hz + ih * 0.06, w * 0.12, kind="mail", facing=1)
    for gx, gy, gs in ((0.32, hz_frac - 0.2, 0.012), (0.37, hz_frac - 0.23, 0.009), (0.9, hz_frac - 0.12, 0.01)):
        A.gull(cv, w * gx, h * gy, w * gs)
    if figure:
        jy = h * 0.88
        cv.poly([(-10, jy), (w * 0.4, jy - ih * 0.02), (w * 0.42, jy + ih * 0.01), (-10, jy + ih * 0.05)], A.WOOD)
        for k in range(8):
            x = w * 0.03 + k * w * 0.052
            cv.rect((x, jy + ih * 0.01 - k * ih * 0.0025, x + w * 0.012, h), A.shade(A.WOOD, 0.7))
        cv.poly([(-10, jy - ih * 0.005), (w * 0.4, jy - ih * 0.025), (w * 0.4, jy - ih * 0.018), (-10, jy + ih * 0.002)], A.WOOD_L)
        A.boat(cv, w * 0.55, jy + ih * 0.06, w * 0.14, kind="rowing")
        A.figure(cv, w * fig_x, jy - ih * 0.012, ih * 0.27, cap=A.RUST, coat=(32, 40, 54), rim=A.OCHRE)
        A.cat(cv, w * (fig_x + 0.1), jy - ih * 0.018, ih * 0.035)
    A.snow(cv, snow_n if snow_n is not None else int(w * h / 2600), seed=seed)
    return cv.finish(seed=seed) if finish else cv

# ---------------------------------------------------------------- the 24 window vignettes
def _interior(cv, wall=(214, 196, 166), floor=(150, 112, 80), y=0.78):
    cv.rect((0, 0, cv.W, cv.H * y), wall)
    for k in range(int(cv.W / 26)):          # tongue-and-groove boards
        cv.line([(k * 26, 0), (k * 26, cv.H * y)], A.shade(wall, 0.92), w=1)
    cv.rect((0, cv.H * y, cv.W, cv.H), floor)
    cv.rect((0, cv.H * y - 4, cv.W, cv.H * y), A.shade(wall, 0.7))

def _window(cv, x0, y0, x1, y1, sky=A.DUSK, inside=None):
    cv.rect((x0 - 6, y0 - 6, x1 + 6, y1 + 6), A.WOOD)
    sub = Canvas(int(x1 - x0), int(y1 - y0), ss=cv.ss)
    if inside:
        inside(sub)
    else:
        A.sky(sub, [sky, A.PEACH], seed=3)
    cv.img.alpha_composite(sub.img, (int(x0 * cv.ss), int(y0 * cv.ss)))
    cv.line([((x0 + x1) / 2, y0), ((x0 + x1) / 2, y1)], A.WOOD, w=4)
    cv.line([(x0, (y0 + y1) / 2), (x1, (y0 + y1) / 2)], A.WOOD, w=4)

def _harbour_view(sub):
    A.sky(sub, [A.DUSK, A.PEACH], y1=sub.H * 0.6, seed=4)
    A.sea(sub, sub.H * 0.6, sub.H, top=A.SEA3, bottom=A.SEA2, seed=4)
    A.lighthouse(sub, sub.W * 0.7, sub.H * 0.62, sub.H * 0.4, beams=False)
    A.boat(sub, sub.W * 0.3, sub.H * 0.72, sub.W * 0.3, kind="fishing")

def _board(cv, x0, y0, x1, y1, n_rows=4, n_cols=6, metal=A.BRASS, seed=1, gaps=()):
    cv.rect((x0, y0, x1, y1), A.WOOD)
    cv.rect((x0 + 6, y0 + 6, x1 - 6, y1 - 6), A.WOOD_L)
    rng = random.Random(seed)
    for r in range(n_rows):
        for c in range(n_cols):
            cx = x0 + (x1 - x0) * (c + 0.5) / n_cols; cy = y0 + (y1 - y0) * (r + 0.42) / n_rows
            cv.ellipse((cx - 3, cy - 3, cx + 3, cy + 3), A.INK)
            if (r * n_cols + c) not in gaps and rng.random() < 0.8:
                A.tally(cv, cx, cy + (y1 - y0) / n_rows * 0.22, (x1 - x0) / n_cols * 0.26,
                        metal=rng.choice([A.BRASS, A.COPPER, A.TIN]) if metal is None else metal)

def scene(day, w=1600, h=500, seed=None):
    seed = seed or day * 7 + 3
    cv = Canvas(w, h, ss=2)
    W, H = w, h
    if day == 1:
        hz = H * 0.6
        A.sky(cv, DUSK_SKY, y1=hz + 2, seed=seed); A.stars(cv, 40, hz * 0.5, seed=seed)
        mainland(cv, hz, seed=seed)
        A.sea(cv, hz, H, top=A.SEA3, bottom=A.SEA, seed=seed)
        A.island(cv, W * 0.55, hz + H * 0.12, W * 0.3, H * 0.2, seed=seed)
        A.lighthouse(cv, W * 0.53, hz + H * 0.02, H * 0.62, beam_angle=192)
        A.cottage(cv, W * 0.58, hz + H * 0.01, W * 0.07, H * 0.09)
        A.boathouse(cv, W * 0.44, hz + H * 0.06, W * 0.04, H * 0.06)
        A.boat(cv, W * 0.18, hz + H * 0.12, W * 0.09, kind="mail")
        A.gull(cv, W * 0.8, H * 0.2, 10); A.gull(cv, W * 0.84, H * 0.26, 7)
        A.snow(cv, 140, seed=seed)
    elif day == 2:
        _interior(cv)
        _window(cv, W * 0.06, H * 0.12, W * 0.34, H * 0.62, inside=_harbour_view)
        _board(cv, W * 0.42, H * 0.08, W * 0.66, H * 0.62, seed=seed, metal=None)
        _board(cv, W * 0.7, H * 0.08, W * 0.94, H * 0.62, seed=seed + 1, metal=None)
        A.table(cv, W * 0.25, W * 0.8, H * 0.8)
        A.journal(cv, W * 0.52, H * 0.79, W * 0.22, H * 0.2, col=A.SEA)
        A.cup(cv, W * 0.7, H * 0.78, H * 0.12)
    elif day == 3:
        hz = H * 0.62
        A.sky(cv, NIGHT_SKY, y1=hz + 2, seed=seed); A.stars(cv, 120, hz, seed=seed)
        A.sea(cv, hz, H, top=A.NIGHT2, bottom=A.NIGHT, stroke=A.DUSK, seed=seed)
        A.island(cv, W * 0.52, hz + H * 0.14, W * 0.62, H * 0.24, col=A.MOSS_D, seed=seed)
        A.lighthouse(cv, W * 0.7, hz + H * 0.0, H * 0.7, beam_angle=200)
        A.boathouse(cv, W * 0.32, hz + H * 0.06, W * 0.08, H * 0.12, lamp=True)
        A.boat(cv, W * 0.12, hz + H * 0.2, W * 0.08, kind="rowing")
        A.figure(cv, W * 0.12, hz + H * 0.19, H * 0.16, coat=A.INK)
    elif day == 4:
        hz = H * 0.45
        A.sky(cv, DAY_SKY, y1=hz + 2, seed=seed)
        mainland(cv, hz, seed=seed, col=(130, 146, 150), lights=False)
        A.sea(cv, hz, H, top=A.SEA3, bottom=A.SEA2, seed=seed)
        A.island(cv, W * 0.2, hz + H * 0.24, W * 0.32, H * 0.22, seed=seed)
        A.lighthouse(cv, W * 0.18, hz + H * 0.08, H * 0.5, lit=False)
        rng = random.Random(seed)
        for k in range(7):        # the reef
            x = W * 0.72 + k * W * 0.035; y = hz + H * (0.3 + 0.05 * (k % 3))
            cv.poly([(x - 22, y), (x - 6, y - 18 - rng.uniform(0, 10)), (x + 14, y - 8), (x + 24, y)], A.STONE)
            cv.line([(x - 30, y + 2), (x + 30, y + 2)], A.FOAM, w=2, alpha=180)
        A.boat(cv, W * 0.48, hz + H * 0.32, W * 0.13, kind="mail")
        for gx in (0.55, 0.6, 0.66):
            A.gull(cv, W * gx, H * 0.2 + gx * 30, 9)
    elif day == 5:
        hz = H * 0.58
        A.sky(cv, DAY_SKY, y1=hz + 2, seed=seed)
        A.hills(cv, [(-20, hz), (W * 0.15, H * 0.2), (W * 0.35, hz - H * 0.05), (W * 0.42, hz)], hz + 2, (110, 122, 120), hatch=A.MOSS_D, seed=seed)
        A.hills(cv, [(W * 0.55, hz), (W * 0.65, H * 0.24), (W * 0.85, H * 0.3), (W + 20, H * 0.12)], hz + 2, (98, 112, 108), hatch=A.MOSS_D, seed=seed + 1)
        A.sea(cv, hz, H, top=A.SEA3, bottom=A.SEA2, seed=seed, density=0.7)
        for k in range(9):         # pines on the far shore
            x = W * (0.6 + 0.04 * k); y = hz - H * 0.01
            cv.poly([(x - 10, y), (x, y - 34 - (k % 3) * 8), (x + 10, y)], A.MOSS_D)
        A.boat(cv, W * 0.32, hz + H * 0.24, W * 0.14, kind="fishing")
        for k in range(4):
            cv.ellipse((W * (0.5 + 0.06 * k) - 6, hz + H * 0.18 - 6, W * (0.5 + 0.06 * k) + 6, hz + H * 0.18 + 6), A.RUST)
    elif day == 6:
        hz = H * 0.6
        A.sky(cv, NIGHT_SKY, y1=hz + 2, seed=seed); A.stars(cv, 90, hz, seed=seed)
        A.sea(cv, hz, H, top=A.NIGHT2, bottom=A.NIGHT, stroke=A.DUSK, seed=seed)
        A.island(cv, W * 0.18, hz + H * 0.06, W * 0.12, H * 0.08, col=A.MOSS_D, seed=seed)
        A.lighthouse(cv, W * 0.18, hz + H * 0.0, H * 0.3, beam_angle=-8)
        # the dashed range circle drawn on the water, and a cottage on the far shore within it
        L = cv.layer(); ld = ImageDraw.Draw(L)
        for k in range(36):
            a0 = math.radians(-60 + k * 3.4)
            if k % 2 == 0:
                pts = [(W * 0.18 + math.cos(a0 + t * 0.03) * W * 0.62, hz + 10 + math.sin(a0 + t * 0.03) * H * 0.38) for t in range(3)]
                ld.line(cv.P(pts), fill=A.LAMP + (170,), width=3 * cv.ss)
        cv.img.alpha_composite(L)
        A.hills(cv, [(W * 0.62, H * 0.66), (W * 0.75, H * 0.5), (W * 0.9, H * 0.55), (W + 20, H * 0.48)], H, A.MOSS_D, seed=seed)
        A.cottage(cv, W * 0.8, H * 0.66, W * 0.1, H * 0.12)
    elif day == 7:
        hz = H * 0.6
        A.sky(cv, NIGHT_SKY, y1=hz + 2, seed=seed); A.stars(cv, 110, hz, seed=seed)
        A.sea(cv, hz, H, top=A.NIGHT2, bottom=A.NIGHT, stroke=A.DUSK, seed=seed)
        A.island(cv, W * 0.2, hz + H * 0.12, W * 0.42, H * 0.2, col=A.MOSS_D, seed=seed)
        A.boathouse(cv, W * 0.2, hz + H * 0.03, W * 0.1, H * 0.16, lamp=True)
        for k in range(9):
            x = W * (0.36 + 0.045 * k); y = H * (0.42 + 0.03 * math.sin(k))
            cv.glow(x, y, 14, A.LAMP, alpha=150); cv.ellipse((x - 5, y - 5, x + 5, y + 5), A.LAMP)
        A.boat(cv, W * 0.82, hz + H * 0.16, W * 0.12, kind="fishing", lit=True, facing=-1)
    elif day == 8:
        _interior(cv, wall=(222, 206, 176))
        cv.rect((0, H * 0.58, W, H * 0.66), A.WOOD)         # the counter
        cv.rect((0, H * 0.66, W, H), A.WOOD_L)
        for k, (x, ww, hh) in enumerate(((0.1, 0.14, 0.2), (0.26, 0.1, 0.14), (0.38, 0.12, 0.26), (0.7, 0.16, 0.18), (0.88, 0.08, 0.12))):
            A.parcel(cv, W * x, H * 0.58, W * ww, H * hh, paper=[A.WOOD_L, A.PAPER2, A.CREAM, A.WOOD_L, A.PAPER2][k])
        cv.rect((W * 0.52, H * 0.45, W * 0.66, H * 0.58), A.PAPER)            # the slip
        for k in range(4):
            cv.line([(W * 0.54, H * (0.48 + 0.025 * k)), (W * 0.64, H * (0.48 + 0.025 * k))], A.SLATE, w=1)
        cv.ellipse((W * 0.6, H * 0.38, W * 0.66, H * 0.44), A.RUST)            # a ball of string
    elif day == 9:
        _interior(cv, wall=(216, 200, 170))
        _board(cv, W * 0.12, H * 0.08, W * 0.46, H * 0.72, n_rows=4, n_cols=7, seed=seed, metal=None)
        _board(cv, W * 0.54, H * 0.08, W * 0.88, H * 0.72, n_rows=4, n_cols=7, seed=seed + 4, metal=None)
    elif day == 10:
        hz = H * 0.5
        A.sky(cv, [(196, 200, 196), (214, 214, 204), (226, 222, 208)], y1=hz + 2, seed=seed)
        A.sea(cv, hz, H, top=(150, 170, 172), bottom=A.SEA3, stroke=A.FOAM, seed=seed)
        A.lighthouse(cv, W * 0.7, hz + H * 0.02, H * 0.42, lit=False)
        cv.rect((0, 0, W, H), (226, 224, 214), alpha=120)                    # fog
        wl = A.tide_post(cv, W * 0.28, H * 0.95, H * 0.7, level=0.42)
        cv.rect((W * 0.2, wl, W * 0.36, H), A.SEA3, alpha=160)
        cv.poly([(W * 0.4, H * 0.6), (W * 0.43, H * 0.5), (W * 0.46, H * 0.6)], A.RUST)
        cv.rect((W * 0.425, H * 0.6, W * 0.435, H * 0.75), A.RUST)
    elif day == 11:
        hz = H * 0.55
        A.sky(cv, WARM_SKY, y1=hz + 2, seed=seed)
        A.sea(cv, hz, H, top=A.SEA3, bottom=A.SEA2, seed=seed)
        A.hills(cv, [(W * 0.0, hz + 2), (W * 0.08, H * 0.32), (W * 0.2, H * 0.36), (W * 0.25, hz + H * 0.02)], hz + H * 0.04, A.MOSS, hatch=A.MOSS_D, seed=seed)
        A.hills(cv, [(W * 0.75, hz + 2), (W * 0.82, H * 0.34), (W * 0.95, H * 0.3), (W + 20, hz)], hz + H * 0.04, A.MOSS, hatch=A.MOSS_D, seed=seed + 1)
        cv.poly([(W * 0.22, hz + 6), (W * 0.78, hz + 6), (W * 0.78, hz - H * 0.07), (W * 0.22, hz - H * 0.05)], A.MOSS_L)
        for k, x in enumerate((0.3, 0.42, 0.55, 0.68)):
            A.cottage(cv, W * x, hz - H * 0.04, W * 0.06, H * 0.07, roof=[A.SLATE, A.RUST_D, A.SLATE, A.RUST_D][k])
    elif day == 12:
        hz = H * 0.55
        A.sky(cv, WARM_SKY, y1=hz + 2, seed=seed)
        A.sea(cv, hz, H, top=A.SEA3, bottom=A.SEA2, seed=seed)
        A.jetty(cv, 0, W * 0.6, H * 0.8)
        cv.rect((W * 0.1, H * 0.36, W * 0.4, H * 0.77), A.WOOD)        # the parcel shed
        cv.poly([(W * 0.08, H * 0.36), (W * 0.25, H * 0.18), (W * 0.42, H * 0.36)], A.RUST_D)
        cv.rect((W * 0.16, H * 0.46, W * 0.34, H * 0.77), A.NIGHT2)
        for k, x in enumerate((0.17, 0.23, 0.28)):
            A.parcel(cv, W * x, H * 0.77, W * 0.05, H * (0.12 + 0.04 * k), paper=[A.WOOD_L, A.PAPER2, A.CREAM][k])
        A.holly(cv, W * 0.25, H * 0.3, 26)
        A.boat(cv, W * 0.75, H * 0.72, W * 0.16, kind="mail", facing=-1)
    elif day == 13:
        cv.rect((0, 0, W, H), (126, 132, 120))
        rng = random.Random(seed)
        for _ in range(60):          # wet stones on the path
            x, y, r = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(18, 46)
            cv.ellipse((x - r, y - r * 0.6, x + r, y + r * 0.6), A.shade(A.STONE, rng.uniform(0.75, 1.05)))
        cv.poly([(W * 0.36, H * 0.2), (W * 0.62, H * 0.16), (W * 0.66, H * 0.84), (W * 0.4, H * 0.88)], A.PAPER)
        A.robin(cv, W * 0.51, H * 0.5, H * 0.16)
        A.holly(cv, W * 0.45, H * 0.76, 18)
        cv.line(A.smooth([(W * 0.7, H * 0.7), (W * 0.76, H * 0.6), (W * 0.8, H * 0.74), (W * 0.9, H * 0.66)], 6), A.RUST, w=2.4)
    elif day == 14:
        cv.rect((0, 0, W, H), A.WOOD_L)
        for k in range(int(H / 22)):
            cv.line([(0, k * 22), (W, k * 22 + 4)], A.shade(A.WOOD_L, 0.9), w=1)
        rng = random.Random(seed)
        for k in range(14):
            A.tally(cv, rng.uniform(W * 0.08, W * 0.92), rng.uniform(H * 0.2, H * 0.85), rng.uniform(22, 34),
                    metal=rng.choice([A.BRASS, A.COPPER, A.TIN]))
        A.boat(cv, W * 0.82, H * 0.3, W * 0.12, kind="fishing")
    elif day == 15:
        hz = H * 0.55
        A.sky(cv, DAY_SKY, y1=hz + 2, seed=seed)
        A.sea(cv, hz, H, top=A.SEA3, bottom=A.SEA2, seed=seed)
        A.boat(cv, W * 0.32, hz + H * 0.2, W * 0.28, kind="cutter")
        A.journal(cv, W * 0.75, H * 0.85, W * 0.26, H * 0.36, col=A.SEA)
        A.gull(cv, W * 0.6, H * 0.18, 10)
    elif day == 16:
        hz = H * 0.62
        A.sky(cv, [A.DUSK, (186, 168, 150), A.PEACH, (242, 196, 136)], y1=hz + 2, seed=seed)
        cv.glow(W * 0.32, hz, H * 0.3, (246, 190, 120), alpha=120)
        cv.ellipse((W * 0.32 - 26, hz - 26, W * 0.32 + 26, hz + 26), (246, 196, 120))
        A.sea(cv, hz, H, top=A.SEA3, bottom=A.SEA2, stroke=A.PEACH, seed=seed)
        A.island(cv, W * 0.66, hz + H * 0.14, W * 0.36, H * 0.22, seed=seed)
        A.lighthouse(cv, W * 0.66, hz + H * 0.02, H * 0.7, lit=False)
        A.keeper(cv, W * 0.66 + H * 0.05, hz + H * 0.02 - H * 0.7 + H * 0.12, H * 0.07)
    elif day == 17:
        cv.rect((0, 0, W, H), (126, 104, 82))
        for k in range(int(H / 26) + 1):     # deck planks
            cv.rect((0, k * 26, W, k * 26 + 2), A.shade((126, 104, 82), 0.75))
        cv.ellipse((W * 0.62, H * 0.2, W * 0.9, H * 0.8), (196, 176, 130))      # coiled rope
        for r in range(1, 6):
            cv.ellipse((W * 0.76 - r * 18, H * 0.5 - r * 14, W * 0.76 + r * 18, H * 0.5 + r * 14), A.shade((196, 176, 130), 0.8))
            cv.ellipse((W * 0.76 - r * 18 + 3, H * 0.5 - r * 14 + 3, W * 0.76 + r * 18 - 3, H * 0.5 + r * 14 - 3), (196, 176, 130))
        A.mitten(cv, W * 0.36, H * 0.7, H * 0.5)
    elif day == 18:
        A.sky(cv, [(186, 196, 196), (220, 218, 206)], y1=H, seed=seed)
        cv.rect((W * 0.25, H * 0.12, W * 0.75, H), A.WHITE)
        cv.rect((W * 0.42, H * 0.3, W * 0.58, H), A.RUST)
        cv.rect((W * 0.44, H * 0.34, W * 0.56, H * 0.6), A.shade(A.RUST, 0.85))
        cv.ellipse((W * 0.535, H * 0.65, W * 0.55, H * 0.69), A.BRASS)
        A.holly(cv, W * 0.5, H * 0.2, 40)
        for x in (0.3, 0.62):
            cv.rect((W * x, H * 0.32, W * (x + 0.08), H * 0.6), A.LAMP)
        cv.rect((0, H * 0.88, W, H), A.SNOW)
        A.snow(cv, 120, seed=seed)
    elif day == 19:
        _interior(cv, wall=(226, 210, 182))
        _window(cv, W * 0.08, H * 0.12, W * 0.3, H * 0.6, sky=A.DUSK)
        A.table(cv, W * 0.35, W * 0.9, H * 0.78)
        A.cake(cv, W * 0.6, H * 0.74, H * 0.42)
        A.cup(cv, W * 0.82, H * 0.74, H * 0.12)
    elif day == 20:
        cv.rect((0, 0, W, H), (104, 120, 124))
        for k, m in enumerate((A.BRASS, A.COPPER, A.TIN)):
            A.tally(cv, W * (0.28 + 0.22 * k), H * 0.52, H * 0.28, metal=m)
    elif day == 21:
        hz = H * 0.6
        A.sky(cv, WARM_SKY, y1=hz + 2, seed=seed)
        for k in range(8):           # the harbour front
            x = W * (0.02 + k * 0.12); hh = H * (0.22 + 0.06 * (k % 3))
            cv.rect((x, hz - hh, x + W * 0.11, hz), [A.WHITE, A.CREAM, (210, 196, 170), A.WHITE][k % 4])
            cv.poly([(x - 4, hz - hh), (x + W * 0.055, hz - hh - H * 0.08), (x + W * 0.11 + 4, hz - hh)], [A.SLATE, A.RUST_D][k % 2])
            cv.rect((x + W * 0.03, hz - hh * 0.6, x + W * 0.05, hz - hh * 0.35), A.LAMP)
        cv.rect((0, hz, W, H), A.STONE)
        A.sea(cv, H * 0.86, H, top=A.SEA3, bottom=A.SEA2, seed=seed)
        A.figure(cv, W * 0.3, H * 0.84, H * 0.42, cap=None, coat=A.SEA)
        A.figure(cv, W * 0.62, H * 0.82, H * 0.36, cap=A.RUST, coat=A.NIGHT2)
        A.gull(cv, W * 0.8, H * 0.2, 12); A.gull(cv, W * 0.86, H * 0.28, 9)
    elif day == 22:
        _interior(cv, wall=(206, 196, 176))
        A.sea_chest(cv, W * 0.5, H * 0.86, W * 0.42, H * 0.36)
        for k, col in enumerate((A.WHITE, A.RUST, A.SEA)):
            x = W * (0.12 + 0.07 * k)
            cv.rect((x - 18, H * 0.66, x + 18, H * 0.86), col)
            cv.rect((x - 20, H * 0.64, x + 20, H * 0.68), A.INK)
        cv.rect((W * 0.78, H * 0.62, W * 0.9, H * 0.86), A.PAPER)
    elif day == 23:
        _interior(cv, wall=(214, 196, 166))
        A.stove(cv, W * 0.24, H * 0.82, H * 0.42)
        cv.ellipse((W * 0.6, H * 0.12, W * 0.62, H * 0.16), A.INK)                 # the hook and the scarf
        A.scarf(cv, W * 0.585, H * 0.15, W * 0.05, H * 0.5, n=12)
        A.table(cv, W * 0.66, W * 0.96, H * 0.74)
        A.journal(cv, W * 0.81, H * 0.73, W * 0.18, H * 0.16, col=A.RUST_D)
        A.cat(cv, W * 0.4, H * 0.86, H * 0.12)
    elif day == 24:
        hz = H * 0.6
        A.sky(cv, [(30, 40, 54), A.NIGHT, A.NIGHT2, A.DUSK, A.PEACH], y1=hz + 2, seed=seed)
        A.stars(cv, 60, hz * 0.6, seed=seed)
        mainland(cv, hz, seed=seed, col=(70, 84, 98))
        A.sea(cv, hz, H, top=A.NIGHT2, bottom=A.NIGHT, stroke=A.DUSK, seed=seed)
        A.island(cv, W * 0.6, hz + H * 0.12, W * 0.32, H * 0.2, col=A.MOSS_D, seed=seed)
        A.lighthouse(cv, W * 0.58, hz + H * 0.02, H * 0.62, lit=False)
        A.cottage(cv, W * 0.63, hz + H * 0.01, W * 0.07, H * 0.09, lit=False, smoke=False)
        A.boat(cv, W * 0.2, hz + H * 0.14, W * 0.1, kind="mail", lit=True)
        A.snow(cv, 220, seed=seed)
    return cv.finish(seed=seed)

if __name__ == "__main__":
    import os, sys
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "previews", "art"); os.makedirs(out, exist_ok=True)
    if "key" in sys.argv:
        keyart(1000, 1000).save(os.path.join(out, "keyart_square.jpg"), quality=88)
    days = [int(a) for a in sys.argv[1:] if a.isdigit()] or list(range(1, 25))
    ims = []
    for d in days:
        im = scene(d, 800, 250); ims.append(im)
    sheet = Image.new("RGB", (1600, 250 * ((len(ims) + 1) // 2)), (255, 255, 255))
    for k, im in enumerate(ims):
        sheet.paste(im, ((k % 2) * 800, (k // 2) * 250))
    sheet.save(os.path.join(out, "scenes_sheet.jpg"), quality=85)
