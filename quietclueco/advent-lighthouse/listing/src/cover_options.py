"""Three alternative main images (2000 x 2000) for a quick poll, next to the current cover.

A  "Tea time"     — a cosy table seen from above: Window 1's journal page, a mug of cocoa, fairy lights,
                    pine, day envelopes tied with twine, a hand in a knitted sleeve ringing a clue, Bosun.
B  "Window seat"  — inside the cottage at dusk: the lighthouse through the window, a candle, cocoa,
                    envelopes on the sill and Bosun looking out to sea.
C  "Lamp out"     — the travel poster in warm sunset colours with the lamp dark and the hook line.

Same rules as the mockups: no faces, only Window 1 is shown, every string is recorded and scanned.
Run:  python3 cover_options.py      -> listing/cover-options/
"""
import math, os, random
from PIL import Image, ImageDraw
import kit
import cal_listing as CL
from cal_listing import art as A, scenes as SC, COVER

S = 2000
OUT = os.path.join(CL.CASE, "listing", "cover-options")
WOOD_H = (176, 128, 84)      # honey pine
COCOA = (104, 64, 42)
SKIN = (233, 190, 156)

# ---------------------------------------------------------------- small drawn things (canvas units)
def fairy_lights(cv, pts, n, seed=1, cord=A.INK):
    path = A.smooth(pts, 12)
    cv.line(path, cord, w=1.6, alpha=200)
    rng = random.Random(seed)
    step = max(1, len(path) // n)
    for k in range(step // 2, len(path), step):
        x, y = path[k]
        col = rng.choice([A.LAMP, A.OCHRE_L, A.LAMP])
        cv.glow(x, y + 6, 22, col, alpha=120, blur=14)
        cv.ellipse((x - 4, y + 1, x + 4, y + 14), col)
        cv.rect((x - 3, y - 2, x + 3, y + 3), A.INK)

def pine(cv, x0, y0, x1, y1, s=1.0, col=A.MOSS_D, seed=1):
    rng = random.Random(seed)
    cv.line([(x0, y0), (x1, y1)], A.WOOD, w=3 * s)
    L = math.hypot(x1 - x0, y1 - y0); ux, uy = (x1 - x0) / L, (y1 - y0) / L
    for k in range(int(L / 5)):
        t = k * 5 / L; x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        ln = (16 + 10 * math.sin(t * math.pi)) * s
        for sd in (-1, 1):
            a = math.atan2(uy, ux) + sd * (0.9 + rng.uniform(-0.15, 0.15))
            cv.line([(x, y), (x + math.cos(a) * ln, y + math.sin(a) * ln)], rng.choice([col, A.MOSS, col]), w=2.2 * s)

def mug_top(cv, x, y, r):
    cv.ellipse((x - r * 1.05, y - r * 1.0, x + r * 1.15, y + r * 1.2), (0, 0, 0), alpha=40)
    cv.ellipse((x + r * 0.75, y - r * 0.28, x + r * 1.5, y + r * 0.28), A.RUST)
    cv.ellipse((x + r * 0.95, y - r * 0.12, x + r * 1.3, y + r * 0.12), WOOD_H)
    cv.ellipse((x - r, y - r, x + r, y + r), A.RUST)
    cv.ellipse((x - r * 0.84, y - r * 0.84, x + r * 0.84, y + r * 0.84), COCOA)
    cv.ellipse((x - r * 0.84, y - r * 0.84, x + r * 0.3, y + r * 0.3), A.shade(COCOA, 1.18), alpha=90)
    rng = random.Random(4)
    for _ in range(5):
        a = rng.uniform(0, 6.28); d = rng.uniform(0, r * 0.5); mx, my = x + math.cos(a) * d, y + math.sin(a) * d
        m = r * 0.12
        cv.ellipse((mx - m, my - m, mx + m, my + m), A.shade(A.PAPER, 0.9))
        cv.ellipse((mx - m * 0.8, my - m * 0.85, mx + m * 0.7, my + m * 0.6), A.PAPER)

def candle(cv, x, base, h, lit=True):
    cv.ellipse((x - h * 0.42, base - h * 0.08, x + h * 0.42, base + h * 0.08), A.BRASS)
    cv.rect((x - h * 0.16, base - h, x + h * 0.16, base - h * 0.02), A.PAPER)
    cv.rect((x - h * 0.16, base - h, x - h * 0.08, base - h * 0.02), A.WHITE)
    if lit:
        cv.glow(x, base - h * 1.15, h * 0.9, A.LAMP, alpha=140)
        cv.poly(A.smooth([(x, base - h * 1.4), (x + h * 0.07, base - h * 1.15), (x, base - h * 1.03), (x - h * 0.07, base - h * 1.15),
                          (x, base - h * 1.4)], 4), A.OCHRE_L)
    cv.line([(x, base - h), (x, base - h * 1.06)], A.INK, w=2)

def cat_sitting(cv, x, base, s, col=A.OCHRE):
    """Bosun sitting up, seen from behind, looking out of the window."""
    st = A.shade(col, 0.8)
    cv.poly(A.smooth([(x - s * 0.36, base), (x - s * 0.4, base - s * 0.35), (x - s * 0.25, base - s * 0.72), (x, base - s * 0.8),
                      (x + s * 0.25, base - s * 0.72), (x + s * 0.4, base - s * 0.35), (x + s * 0.36, base)], 6), col)
    cv.ellipse((x - s * 0.24, base - s * 1.12, x + s * 0.24, base - s * 0.7), col)
    for sx in (-1, 1):
        cv.poly([(x + sx * s * 0.08, base - s * 1.06), (x + sx * s * 0.2, base - s * 1.28), (x + sx * s * 0.23, base - s * 0.98)], col)
        cv.poly([(x + sx * s * 0.12, base - s * 1.07), (x + sx * s * 0.19, base - s * 1.2), (x + sx * s * 0.2, base - s * 1.03)], A.ROSE)
    for k in range(4):
        yy = base - s * (0.62 - 0.13 * k)
        cv.line(A.smooth([(x - s * 0.2, yy - s * 0.03), (x, yy + s * 0.02), (x + s * 0.2, yy - s * 0.03)], 4), st, w=max(2, s * 0.045))
    for k in range(2):
        yy = base - s * (0.98 - 0.08 * k)
        cv.line([(x - s * 0.1, yy), (x + s * 0.1, yy)], st, w=max(2, s * 0.04))
    cv.line(A.smooth([(x + s * 0.3, base - s * 0.04), (x + s * 0.6, base - s * 0.02), (x + s * 0.72, base - s * 0.2),
                      (x + s * 0.66, base - s * 0.38)], 6), col, w=max(3, s * 0.11))

def cat_curled_top(cv, x, y, s, col=A.OCHRE):
    """Bosun asleep, seen from above."""
    st = A.shade(col, 0.8)
    cv.ellipse((x - s, y - s * 0.78, x + s, y + s * 0.78), col)
    cv.ellipse((x + s * 0.25, y - s * 0.55, x + s * 0.95, y + s * 0.15), A.shade(col, 1.05))
    for sx in (0.42, 0.78):
        cv.poly([(x + s * sx - s * 0.12, y - s * 0.42), (x + s * sx, y - s * 0.72), (x + s * sx + s * 0.12, y - s * 0.42)], col)
    for k in range(5):
        a = 2.4 + k * 0.42
        cv.line([(x + math.cos(a) * s * 0.35, y + math.sin(a) * s * 0.3), (x + math.cos(a) * s * 0.85, y + math.sin(a) * s * 0.66)], st, w=max(2, s * 0.06))
    cv.line(A.smooth([(x - s * 0.9, y + s * 0.2), (x - s * 0.6, y + s * 0.72), (x + s * 0.1, y + s * 0.8), (x + s * 0.6, y + s * 0.45)], 8),
            A.shade(col, 0.9), w=max(3, s * 0.2))

def knit(cv, box, a=A.RUST, b=A.CREAM, cell=18):
    x0, y0, x1, y1 = box
    cv.rect(box, a)
    for r in range(int((y1 - y0) / cell) + 1):
        for c in range(int((x1 - x0) / cell) + 1):
            cx = x0 + c * cell + cell / 2; cy = y0 + r * cell
            for sx in (-1, 1):
                cv.line([(cx + sx * cell * 0.38, cy), (cx, cy + cell * 0.7)], A.shade(a, 0.82), w=2)
            if (r // 2 + c // 2) % 4 == 0 and r % 6 in (2, 3):
                cv.ellipse((cx - cell * 0.18, cy + cell * 0.2, cx + cell * 0.18, cy + cell * 0.55), b)

def sleeve_hand(cv, x, y, s, angle=-0.55):
    """A hand in a chunky moss-green jumper coming in from the bottom edge, holding a red pencil."""
    ca, sa = math.cos(angle), math.sin(angle)
    def R(px, py):
        return (x + px * s * ca - py * s * sa, y + px * s * sa + py * s * ca)
    def poly(pts, col, n=0):
        pts = [R(*p) for p in pts]
        cv.poly(A.smooth(pts, n) if n else pts, col)
    def blob(px, py, rx, ry, col, k=14):
        poly([(px + rx * math.cos(t * 6.283 / k), py + ry * math.sin(t * 6.283 / k)) for t in range(k)], col, 3)
    knitc, cuff = A.MOSS, A.MOSS_D
    poly([(-0.4, 3.0), (-0.36, 0.5), (0.36, 0.5), (0.4, 3.0)], knitc)
    for k in range(9):
        xx = -0.3 + k * 0.075
        cv.line([R(xx, 0.75), R(xx * 1.05, 3.0)], A.shade(knitc, 0.82), w=2)
    poly([(-0.4, 0.78), (-0.38, 0.42), (0.38, 0.42), (0.4, 0.78)], cuff)
    for k in range(11):
        xx = -0.35 + k * 0.07
        cv.line([R(xx, 0.45), R(xx, 0.75)], A.shade(cuff, 0.8), w=2)
    blob(0, 0.12, 0.31, 0.36, SKIN)                                            # palm, back of the hand
    cv.line([R(0.0, -0.12), R(0.18, -1.25)], A.RUST, w=s * 0.085)             # pencil under the fingers
    cv.line([R(0.18, -1.25), R(0.215, -1.43)], PEACH_WOOD, w=s * 0.07)
    cv.line([R(0.215, -1.43), R(0.225, -1.5)], A.INK, w=s * 0.04)
    for k, fx in enumerate((-0.2, -0.07, 0.06, 0.19)):                          # curled fingers
        blob(fx, -0.2 - 0.03 * (k in (1, 2)), 0.085, 0.12, A.shade(SKIN, 0.96 - 0.02 * k))
        cv.line([R(fx - 0.05, -0.27), R(fx + 0.05, -0.27)], A.shade(SKIN, 0.82), w=2)
    blob(-0.25, -0.06, 0.09, 0.2, A.shade(SKIN, 0.93))                         # thumb over the pencil

PEACH_WOOD = (226, 190, 140)

def twine_bundle(f, cx, cy, numbers, w=430, angle=-8):
    """Day envelopes stacked and tied with twine (Frame units)."""
    stack = Image.new("RGBA", (w + 80, int(w * 0.62) + 120), (0, 0, 0, 0))
    for k, n in enumerate(numbers):
        e = kit.envelope(w, n)
        stack.alpha_composite(e, (40 - k * 10 + (k % 2) * 16, 60 - k * 14 + k * 4))
    d = ImageDraw.Draw(stack)
    tw = (190, 150, 100); sx = stack.width * 0.34
    d.line([(sx, 0), (sx + 10, stack.height)], fill=tw, width=7)
    d.line([(0, stack.height * 0.62), (stack.width, stack.height * 0.58)], fill=tw, width=7)
    for a in (-1, 1):
        d.ellipse([sx - 36 + a * 26, stack.height * 0.6 - 24, sx + 10 + a * 26, stack.height * 0.6 + 14], outline=tw, width=7)
    d.line([(sx, stack.height * 0.6), (sx - 50, stack.height * 0.6 + 90)], fill=tw, width=6)
    d.line([(sx, stack.height * 0.6), (sx + 40, stack.height * 0.6 + 96)], fill=tw, width=6)
    f.paste(stack, cx, cy, angle=angle)
    for n in numbers:
        f.note("drawn", "envelope", str(n))

# ---------------------------------------------------------------- type
def title_block(f, cx, top, width, ink=A.NIGHT, offset=A.RUST, kicker="A COSY LIGHTHOUSE MYSTERY", kick_col=A.RUST,
                sub="ADVENT CALENDAR", sub_col=A.RUST_D):
    d = f.draw()
    fk = kit.fit_font(f, kicker, "semi", 66, width - 13 * len(kicker))
    kit.spaced(f.img, (cx, top + fk.size), kicker, fk, kick_col, fk.size * 0.18); f.note("drawn", "title", kicker)
    t1, t2 = "THE KEEPER OF", "CANDLEHOLM"
    f1 = kit.fit_font(f, t1, "display", 150, width * 0.78)
    f2 = kit.fit_font(f, t2, "display", 330, width)
    y1 = top + fk.size + f1.size * 1.3
    y2 = y1 + f2.size * 0.98
    for t, fn, y, sp in ((t1, f1, y1, f1.size * 0.08), (t2, f2, y2, f2.size * 0.01)):
        sh = max(4, fn.size // 22)
        kit.spaced(f.img, (cx + sh, y + sh), t, fn, offset, sp)
        kit.spaced(f.img, (cx, y), t, fn, ink, sp)
        f.note("drawn", "title", t)
    y3 = y2
    if sub:
        fs = kit.fit_font(f, sub, "display", 104, width * 0.8)
        y3 = y2 + fs.size * 1.45
        kit.spaced(f.img, (cx, y3), sub, fs, sub_col, fs.size * 0.16); f.note("drawn", "title", sub)
    return y3

def band(f, text="PRINTABLE  ·  iPAD  ·  1–4 PLAYERS", h=150, bg=A.CREAM, fg=A.NIGHT, rule=A.RUST):
    d = f.draw()
    d.rectangle([0, S - h, S, S], fill=bg); d.rectangle([0, S - h, S, S - h + 12], fill=rule)
    fb = kit.fit_font(f, text, "display", 92, S - 220 - 8 * len(text))
    kit.spaced(f.img, (S / 2, S - h * 0.3), text, fb, fg, 8); f.note("drawn", "band", text)

def stamp(f, cx, cy, r, top="24", bottom="DAYS"):
    COVER.stamp(f.img, cx, cy, r, top, bottom); f.note("drawn", "stamp", f"{top} {bottom}")

def hand_note(f, xy, text, size, col, angle=-4, bold=True):
    fnt = kit.font("handb" if bold else "hand", size)
    d = f.draw(); w = d.textlength(text, font=fnt) + 30
    im = Image.new("RGBA", (int(w), int(size * 1.7)), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((15, size * 0.1), text, font=fnt, fill=col)
    f.paste(im, xy[0], xy[1], angle=angle, shadow=False)
    f.note("drawn", "note", text)

def tag(f, cx, cy, text, size, angle=0):
    """A handwritten line on a strip of cream paper."""
    fnt = kit.font("handb", size)
    w = int(f.draw().textlength(text, font=fnt) + size * 1.4); h = int(size * 1.7)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w - 1, h - 1], fill=A.PAPER, outline=(214, 200, 170), width=3)
    d.text((w / 2, h / 2 + size * 0.05), text, font=fnt, fill=A.RUST_D, anchor="mm")
    f.paste(im, cx, cy, angle=angle, shadow_strength=110)
    f.note("drawn", "tag", text)

# ---------------------------------------------------------------- option A: tea time, from above
def bg_tea():
    cv = A.Canvas(S // 2, S // 2, ss=2, bg=WOOD_H)
    W = H = S // 2
    for k in range(7):
        x = k * W / 7
        cv.rect((x, 0, x + 3, H), A.shade(WOOD_H, 0.84))
        rng = random.Random(k)
        for _ in range(9):
            y = rng.uniform(0, H); cv.line([(x + 18, y), (x + 20 + rng.uniform(-2, 2), y + rng.uniform(60, 160))], A.shade(WOOD_H, 0.92), w=1.3)
    cv.glow(W * 0.5, H * 0.55, W * 0.6, (255, 214, 150), alpha=60)
    pine(cv, -20, H * 0.52, W * 0.2, H * 0.36, s=1.3, seed=1)
    pine(cv, -10, H * 0.62, W * 0.16, H * 0.62, s=1.1, seed=2)
    pine(cv, W * 1.02, H * 0.36, W * 0.84, H * 0.46, s=1.2, seed=3)
    A.holly(cv, W * 0.13, H * 0.5, 40)
    for (x, y) in ((0.86, 0.45), (0.9, 0.5)):
        cv.ellipse((W * x - 10, H * y - 10, W * x + 10, H * y + 10), A.RUST)
    mug_top(cv, W * 0.13, H * 0.8, 96)
    return cv

def option_a(A_):
    cv = bg_tea()
    im = cv.finish(seed=3).resize((S, S), Image.LANCZOS)
    f = kit.Frame(S, S); f.img = im.convert("RGBA")
    # the open pages of Window 1, as in play
    j = A_.L.image(A_.p["w1journal"], 1020)
    f.paste_page(j, 860, 1330, angle=-4)
    c = A_.L.image(A_.p["w1chart"], 900)
    f.paste_page(c, 1350, 1320, angle=5)
    kit.pen_circle(f, 1310, 1440, 80, 60, col=A.RUST, width=8, seed=4)
    twine_bundle(f, 1690, 1300, [24, 3, 2, 1], w=440, angle=9)
    # hand in a knitted sleeve ringing a clue on the journal page (drawn on a transparent canvas)
    hv = A.Canvas(S // 2, S // 2, ss=2, bg=(0, 0, 0)); hv.img.putalpha(0)
    sleeve_hand(hv, 660, 790, 150, angle=-0.4)
    hand = hv.img.resize((S, S), Image.LANCZOS)
    f.img.alpha_composite(hand)
    # fairy lights across the top of the table, over the card
    card = Image.new("RGBA", (1760, 830), (0, 0, 0, 0)); cd = ImageDraw.Draw(card)
    cd.rounded_rectangle([0, 0, 1759, 829], radius=26, fill=A.PAPER + (255,), outline=(214, 200, 170), width=4)
    cd.rounded_rectangle([22, 22, 1737, 807], radius=18, outline=A.RUST + (255,), width=5)
    f.paste(card, S / 2, 500, angle=-1.5, shadow_strength=110)
    title_block(f, S / 2, 110, 1560)
    lv = A.Canvas(S // 2, S // 2, ss=2, bg=(0, 0, 0)); lv.img.putalpha(0)
    fairy_lights(lv, [(-10, 10), (180, 30), (420, 14), (640, 32), (860, 12), (1010, 26)], 14, seed=2)
    f.img.alpha_composite(lv.img.resize((S, S), Image.LANCZOS))
    stamp(f, 1760, 900, 150)
    band(f)
    return f

# ---------------------------------------------------------------- option B: window seat at dusk
def view_dusk(sub):
    hz = sub.H * 0.66
    A.sky(sub, [A.NIGHT2, A.DUSK, (176, 160, 150), A.PEACH, (244, 200, 140)], y1=hz + 2, seed=21)
    A.stars(sub, 30, hz * 0.35, seed=21)
    A.moon(sub, sub.W * 0.16, sub.H * 0.16, sub.W * 0.035, sky_col=A.NIGHT2)
    SC.mainland(sub, hz, seed=21)
    A.sea(sub, hz, sub.H, top=A.SEA3, bottom=A.SEA2, stroke=A.PEACH, seed=21)
    A.island(sub, sub.W * 0.66, hz + sub.H * 0.09, sub.W * 0.42, sub.H * 0.13, seed=21)
    A.cottage(sub, sub.W * 0.72, hz - sub.H * 0.005, sub.W * 0.09, sub.H * 0.06)
    A.lighthouse(sub, sub.W * 0.6, hz + sub.H * 0.01, sub.H * 0.5, beam_angle=190)
    A.boat(sub, sub.W * 0.25, hz + sub.H * 0.08, sub.W * 0.14, kind="mail")
    A.snow(sub, 70, seed=21)

def window_seat(cat_x=0.5, cushion=True, journal=True, wall=(232, 214, 180), y0f=0.4, y1f=0.79):
    """The keeper's window seat at dusk: the lighthouse through the window, curtains, fairy lights, a cup, a
    candle and Bosun on the sill looking out to sea. Returns the Canvas (1000 units) for the caller to finish."""
    W = H = S // 2
    cv = A.Canvas(W, H, ss=2, bg=wall)
    SC._interior(cv, wall=wall, floor=WOOD_H, y=1.0)
    x0, y0, x1, y1 = W * 0.1, H * y0f, W * 0.9, H * y1f
    cv.rect((x0 - 16, y0 - 16, x1 + 16, y1 + 4), A.WOOD)
    sub = A.Canvas(int(x1 - x0), int(y1 - y0), ss=cv.ss); view_dusk(sub)
    cv.img.alpha_composite(sub.img, (int(x0 * cv.ss), int(y0 * cv.ss)))
    cv.line([((x0 + x1) / 2, y0), ((x0 + x1) / 2, y1)], A.WOOD, w=7)
    cv.line([(x0, (y0 + y1) / 2 - 20), (x1, (y0 + y1) / 2 - 20)], A.WOOD, w=7)
    for sx, xa in ((-1, x0 - 16), (1, x1 + 16)):                                   # curtains
        pts = [(xa, y0 - 40), (xa - sx * 70, y0 - 40), (xa - sx * 46, y0 + 120), (xa - sx * 64, y1), (xa, y1)]
        cv.poly(A.smooth(pts, 6), A.RUST)
        for k in range(3):
            cv.line([(xa - sx * (14 + 16 * k), y0 - 30), (xa - sx * (10 + 14 * k), y1 - 10)], A.RUST_D, w=2, alpha=150)
    cv.rect((x0 - 120, y0 - 50, x1 + 120, y0 - 40), A.WOOD)
    fairy_lights(cv, [(x0 - 40, y0 - 34), (x0 + 150, y0 - 6), (W / 2, y0 - 26), (x1 - 150, y0 - 4), (x1 + 40, y0 - 34)], 15, seed=5)
    cv.rect((x0 - 60, y1, x1 + 60, y1 + 26), A.WOOD_L)                               # the sill
    cv.rect((x0 - 60, y1 + 26, x1 + 60, y1 + 34), A.shade(A.WOOD_L, 0.75))
    if cushion:
        knit(cv, (0, y1 + 34, W, H), a=A.CREAM, b=A.RUST, cell=18)
    A.cup(cv, x0 + 70, y1, 70)
    candle(cv, x0 + 175, y1, 62)
    if cat_x is not None:
        cat_sitting(cv, W * cat_x, y1 + 4, 150)
    if journal:
        A.journal(cv, x1 - 210, y1 + 2, 160, 34, open_=False, col=A.SEA2)
    pine(cv, x1 - 110, y1 - 4, x1 - 10, y1 - 30, s=0.9, seed=7)
    A.holly(cv, x1 - 60, y1 - 18, 26)
    return cv

def option_b(A_=None):
    im = window_seat().finish(seed=7).resize((S, S), Image.LANCZOS)
    f = kit.Frame(S, S); f.img = im.convert("RGBA")
    twine_bundle(f, 1420, 1450, [3, 2, 1], w=330, angle=-6)
    title_block(f, S / 2, 40, 1700)
    stamp(f, 300, 900, 150)
    tag(f, S / 2, 1735, "Christmas Eve. The lamp didn’t light…", 76, angle=-1.5)
    band(f, bg=A.NIGHT, fg=A.CREAM, rule=A.RUST)
    return f

# ---------------------------------------------------------------- option C: warm poster, lamp out
SUNSET = [(70, 80, 104), (126, 112, 128), (198, 146, 128), (232, 176, 128), (246, 210, 150)]

def option_c(A_):
    old = SC.DUSK_SKY
    SC.DUSK_SKY = SUNSET
    try:
        art = SC.keyart(S // 2, S // 2, seed=11, lit=False, hz_frac=0.67, tower=0.3, fig_x=0.24, moon_xy=(0.86, 0.47),
                        beams=False, snow_n=260)
    finally:
        SC.DUSK_SKY = old
    f = kit.Frame(S, S); f.img = art.resize((S, S), Image.LANCZOS).convert("RGBA")
    title_block(f, S / 2, 90, 1720, ink=A.CREAM, offset=A.RUST, kick_col=A.PAPER, sub_col=A.PAPER)
    stamp(f, 300, 1080, 150)
    hand_note(f, (1420, 1560), "Christmas Eve.", 88, A.PAPER, angle=-4)
    hand_note(f, (1440, 1670), "The lamp didn’t light…", 88, A.PAPER, angle=-4)
    band(f, text="24 COSY EVENINGS  ·  PRINTABLE  ·  iPAD")
    return f

# ---------------------------------------------------------------- sheet
def current(A_):
    """The cover in use now (listing image 01, already checked by the mockup build)."""
    f = kit.Frame(S, S)
    f.img = Image.open(os.path.join(CL.CASE, "listing", "mockups", f"{CL.SLUG}_01-main.jpg")).convert("RGBA")
    return f

def build():
    os.makedirs(OUT, exist_ok=True)
    A_ = type("X", (), {})(); A_.L, A_.I, A_.p, A_.ip = CL.pages()
    bad = CL.forbidden()
    opts = [("0-current", current), ("A-tea-time", option_a), ("B-window-seat", option_b), ("C-lamp-out", option_c)]
    import sys
    only = sys.argv[1:]
    ims = []
    for name, fn in opts:
        p = os.path.join(OUT, f"{CL.SLUG}_cover-{name}.jpg")
        if only and name[0] not in only and os.path.exists(p):
            ims.append((name, Image.open(p).convert("RGB"))); continue
        f = fn(A_)
        hits = kit.spoiler_scan(f.sources, bad)
        f.img.convert("RGB").save(p, quality=88, optimize=True)
        print(name, "spoiler hits:", len(hits), hits[:3], flush=True)
        ims.append((name, f.img.convert("RGB")))
    # comparison sheet: big previews, and below the same four at Etsy search size (250 px)
    lab = kit.font("display", 34)
    sheet = Image.new("RGB", (4 * 520 + 40, 520 + 60 + 300 + 70), A.CREAM); d = ImageDraw.Draw(sheet)
    for k, (name, im) in enumerate(ims):
        x = 20 + k * 520
        sheet.paste(im.resize((500, 500), Image.LANCZOS), (x + 10, 50))
        d.text((x + 260, 30), {"0": "NOW", "A": "A · TEA TIME", "B": "B · WINDOW SEAT", "C": "C · LAMP OUT"}[name[0]],
               font=lab, fill=A.NIGHT, anchor="ms")
        sheet.paste(im.resize((250, 250), Image.LANCZOS), (x + 135, 600))
    d.text((sheet.width / 2, 590 - 8), "the same at Etsy search size (250 px)", font=kit.font("semi", 28), fill=A.RUST_D, anchor="ms")
    sp = os.path.join(OUT, f"{CL.SLUG}_cover-options_sheet.jpg"); sheet.save(sp, quality=88)
    print(sp)

if __name__ == "__main__":
    build()
