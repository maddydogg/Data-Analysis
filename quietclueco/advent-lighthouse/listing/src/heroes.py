"""Five hero (main) image options for the Etsy listing, 2000 x 2000, for the seller to choose from.

Built with three installed skills in mind: canvas-design (a written design philosophy, "Lamplight Cartography", in
listing/hero-options/design-philosophy.md, then a crafted canvas), ad-creative (one buyer segment and one motive
per image, so the five test five different audiences, and the headline never captions the picture) and
marketing-psychology (the lever each one pulls).

  1 envelopes   gift buyers        "a present she opens every night"     endowment / goal gradient
  2 journal     mystery readers    "what happens next?"                   curiosity gap (Zeigarnik)
  3 chart       puzzle lovers      "a fair puzzle with one answer"        authority / fair play
  4 lamp        Christmas-mood     "beautiful, cosy, a little eerie"      contrast, one broken pattern
  5 two         couples            "our December evenings together"       jobs to be done (a date night)

Rules kept from the mockups: no faces, only Window 1 and set-up pages, every drawn string recorded on a kit.Frame
and scanned for spoilers and stop-listed words. Title, "24 days", "printable" and "iPad" sit inside the 4:3 safe zone
(y 230-1770), so they survive the crop Etsy's search grid can apply to a square photo.
Run:  python3 heroes.py [1 2 3 4 5]   ->  listing/hero-options/
"""
import math, os, random, re, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import kit
import cal_listing as CL
from cal_listing import art as A, C
import cover_options as CO

S = 2000
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(CL.CASE, "listing", "hero-options")
SAFE = (230, 1770)                     # 4:3 centre crop of a square: keep the essentials inside

NAVY = (27, 43, 59); INK = (38, 36, 36); CREAM = (246, 239, 224); PAPER = (250, 245, 233)
RUST = A.RUST; RUST_D = A.RUST_D; OCHRE = A.OCHRE; OCHRE_L = A.OCHRE_L; MOSS = A.MOSS
KRAFT = (212, 178, 134); SAGE = (200, 208, 188)

_f = {}
def F(name, size):
    files = {"gloock": "Gloock-Regular.ttf", "sans": "InstrumentSans-Regular.ttf", "sansb": "InstrumentSans-Bold.ttf",
             "serif-i": "InstrumentSerif-Italic.ttf", "serif": "InstrumentSerif-Regular.ttf", "arsenal": "ArsenalSC-Regular.ttf",
             "mono": "DMMono-Regular.ttf", "tall": "BigShoulders-Bold.ttf", "young": "YoungSerif-Regular.ttf",
             "note": "NothingYouCouldDo-Regular.ttf"}
    key = (name, int(size))
    if key not in _f:
        if name in ("kalam", "kalamb"):
            path = os.path.join(CL.CASE, "src", "fonts", "Kalam-Bold.ttf" if name == "kalamb" else "Kalam-Regular.ttf")
        else:
            path = os.path.join(HERE, "fonts-hero", files[name])
        _f[key] = ImageFont.truetype(path, int(size))
    return _f[key]

def width(d, s, f, tr=0):
    return d.textlength(s, font=f) + tr * (len(s) - 1)

def fit(d, s, name, size, maxw, tr_frac=0.0):
    while size > 12:
        f = F(name, size)
        if width(d, s, f, size * tr_frac) <= maxw:
            return f
        size -= 2
    return F(name, size)

def put(fr, xy, s, f, fill, tr=0, anchor="m"):
    """Tracked text on the frame's image, baseline at xy[1]; anchor m (centre), l or r. Recorded for the scan."""
    d = fr.draw()
    w = width(d, s, f, tr)
    x = {"m": xy[0] - w / 2, "l": xy[0], "r": xy[0] - w}[anchor]
    if not tr:
        d.text((x, xy[1]), s, font=f, fill=fill, anchor="ls")
    else:
        for ch in s:
            d.text((x, xy[1]), ch, font=f, fill=fill, anchor="ls")
            x += d.textlength(ch, font=f) + tr
    fr.note("drawn", "hero", s)
    return w

def frame(img):
    fr = kit.Frame(S, S); fr.img = img.convert("RGBA"); return fr

def grain(img, seed=1, amount=1.0, vignette=0.0):
    return A.gouache(img.convert("RGB"), seed=seed, amount=amount, vignette=vignette)

def big_layer(scale=2):
    return Image.new("RGBA", (S * scale, S * scale), (0, 0, 0, 0))

def down(layer):
    return layer.resize((S, S), Image.LANCZOS)

def shadow_paste(fr, im, x, y, angle=0, strength=90):
    fr.paste(im, x, y, angle=angle, shadow=True, shadow_strength=strength)

def pill(fr, cx, cy, s, f, bg, fg, padx=46, tr=0):
    d = fr.draw()
    w = width(d, s, f, tr) + 2 * padx; h = f.size * 1.6
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], radius=h / 2, fill=bg)
    put(fr, (cx, cy + f.size * 0.36), s, f, fg, tr)

def wrap(d, text, f, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) > maxw and cur:
            lines.append(cur); cur = w
        else:
            cur = t
    return lines + [cur]

# ======================================================================== 1  envelopes (gift)
def envelope(w, n, col, seal=RUST, open_=False, holly=False, ss=2):
    """One day envelope seen flat, drawn at 2x: paper, flap, a wax seal with the day number."""
    h = int(w * 0.64)
    extra = int(h * 0.9) if open_ else 0
    W, H = (w + 30) * ss, (h + 30 + extra) * ss
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    x0, y0 = 15 * ss, (15 + extra) * ss; x1, y1 = x0 + w * ss, y0 + h * ss
    edge = A.shade(col, 0.82)
    if open_:                                                       # the flap thrown back, a card rising out
        d.polygon([(x0, y0), (x1, y0), ((x0 + x1) / 2, y0 - h * 0.62 * ss)], fill=A.shade(col, 0.9), outline=edge)
        cw, ch = w * 0.82 * ss, h * 1.25 * ss
        cx0, cy0 = (x0 + x1) / 2 - cw / 2, y0 - h * 0.78 * ss
        d.rectangle([cx0, cy0, cx0 + cw, cy0 + ch], fill=PAPER, outline=(214, 204, 182), width=2 * ss)
        d.rectangle([cx0 + 14 * ss, cy0 + 14 * ss, cx0 + cw - 14 * ss, cy0 + ch * 0.52], fill=(204, 222, 222))
        bx = cx0 + cw * 0.5; by = cy0 + ch * 0.52                    # a tiny lighthouse on the card
        d.polygon([(bx - 9 * ss, by), (bx + 9 * ss, by), (bx + 6 * ss, by - 52 * ss), (bx - 6 * ss, by - 52 * ss)], fill=CREAM)
        for k in (0.25, 0.6):
            yy = by - 52 * ss * k
            d.rectangle([bx - 8 * ss, yy - 5 * ss, bx + 8 * ss, yy + 2 * ss], fill=RUST)
        d.rectangle([bx - 8 * ss, by - 64 * ss, bx + 8 * ss, by - 52 * ss], fill=NAVY)
        d.polygon([(bx - 9 * ss, by - 64 * ss), (bx + 9 * ss, by - 64 * ss), (bx, by - 74 * ss)], fill=RUST)
        d.ellipse([bx - 40 * ss, by - 8 * ss, bx + 40 * ss, by + 8 * ss], fill=A.MOSS)
        f = F("sansb", 15 * ss)
        t = "WINDOW 1"; tw = d.textlength(t, font=f)
        d.text(((cx0 + cx0 + cw) / 2 - tw / 2, cy0 + ch * 0.66), t, font=f, fill=RUST_D)
        for k in range(3):
            yy = cy0 + ch * (0.8 + 0.07 * k)
            d.line([(cx0 + 22 * ss, yy), (cx0 + cw - (22 + 30 * (k == 2)) * ss, yy)], fill=(200, 192, 176), width=2 * ss)
    d.rounded_rectangle([x0, y0, x1, y1], radius=8 * ss, fill=col, outline=edge, width=2 * ss)
    mx, my = (x0 + x1) / 2, y0 + h * 0.54 * ss
    if not open_:
        d.line([(x0 + 4 * ss, y0 + 4 * ss), (mx, my), (x1 - 4 * ss, y0 + 4 * ss)], fill=edge, width=3 * ss)
    d.line([(x0 + 4 * ss, y1 - 4 * ss), (mx - w * 0.12 * ss, my + h * 0.08 * ss)], fill=A.shade(col, 0.9), width=2 * ss)
    d.line([(x1 - 4 * ss, y1 - 4 * ss), (mx + w * 0.12 * ss, my + h * 0.08 * ss)], fill=A.shade(col, 0.9), width=2 * ss)
    r = h * 0.2 * ss
    if not open_:
        d.ellipse([mx - r * 1.08, my - r * 0.98, mx + r * 1.02, my + r * 1.1], fill=A.shade(seal, 0.7))
        d.ellipse([mx - r, my - r, mx + r, my + r], fill=seal)
        d.ellipse([mx - r * 0.76, my - r * 0.76, mx + r * 0.76, my + r * 0.76], outline=A.shade(seal, 1.25), width=2 * ss)
        f = F("gloock", r * 1.05)
        d.text((mx, my + r * 0.06), str(n), font=f, fill=CREAM, anchor="mm")
    if holly:
        for a in (-0.5, 0.5):
            cx, cy = x1 - 40 * ss + a * 22 * ss, y0 + 32 * ss
            d.ellipse([cx - 20 * ss, cy - 9 * ss, cx + 20 * ss, cy + 9 * ss], fill=A.MOSS_D)
        for dx in (-6, 6):
            d.ellipse([x1 - 40 * ss + dx * ss - 7 * ss, y0 + 38 * ss - 7 * ss, x1 - 40 * ss + dx * ss + 7 * ss, y0 + 38 * ss + 7 * ss], fill=RUST)
    return im.resize((im.width // ss, im.height // ss), Image.LANCZOS)

def hero_envelopes():
    bg = Image.new("RGB", (S, S), (244, 238, 226)); d = ImageDraw.Draw(bg)
    for k in range(0, S, 6):                                        # a fine linen weave
        d.line([(k, 0), (k, S)], fill=(238, 231, 218), width=1)
        d.line([(0, k), (S, k)], fill=(240, 234, 221), width=1)
    fr = frame(grain(bg, seed=101, amount=0.7, vignette=0.25))
    # type
    put(fr, (S / 2, 312), "A COSY MYSTERY ADVENT CALENDAR", F("sansb", 50), RUST, tr=12)
    put(fr, (S / 2, 470), "The Keeper of", F("gloock", 150), NAVY)
    put(fr, (S / 2, 700), "Candleholm", fit(fr.draw(), "Candleholm", "gloock", 270, 1500), NAVY)
    pill(fr, S / 2, 800, "24 DAYS  ·  PRINTABLE  ·  iPAD", F("sansb", 58), RUST, CREAM, tr=5)
    # the wall of 24 envelopes, number 1 open
    cols = [CREAM, KRAFT, SAGE]
    ew, gx, gy = 250, 30, 30
    eh = int(ew * 0.64)
    x0 = (S - (6 * ew + 5 * gx)) / 2; y0 = 950
    rng = random.Random(4)
    for i in range(24):
        r, c = divmod(i, 6)
        n = i + 1
        cx = x0 + c * (ew + gx) + ew / 2; cy = y0 + r * (eh + gy) + eh / 2
        if n == 1:
            continue
        im = envelope(ew, n, cols[(r + c) % 3], seal=OCHRE if n == 24 else RUST, holly=(n == 24))
        shadow_paste(fr, im, cx, cy, angle=rng.uniform(-1.6, 1.6), strength=60)
        fr.note("drawn", "envelope", str(n))
    im = envelope(ew, 1, CREAM, open_=True)
    cx = x0 + ew / 2; cy = y0 + eh / 2 - (im.height - eh - 30) / 2
    shadow_paste(fr, im, cx, cy, angle=-2.5, strength=70)
    fr.note("drawn", "card", "WINDOW 1")
    # the handwritten note, off to the right of the open one
    note = "open one every night"
    f = F("note", 66)
    nim = Image.new("RGBA", (900, 140), (0, 0, 0, 0)); ImageDraw.Draw(nim).text((10, 20), note, font=f, fill=RUST_D)
    fr.paste(nim, 820, 905, angle=2, shadow=False); fr.note("drawn", "note", note)
    put(fr, (S / 2, 1752), "INSTANT DOWNLOAD  ·  1–4 PLAYERS  ·  10–25 MINUTES A NIGHT", F("sansb", 40), A.shade(NAVY, 1.3), tr=6)
    return fr

# ======================================================================== 2  journal (mystery readers)
def hero_journal():
    bg = Image.new("RGB", (S, S), (74, 50, 37)); d = ImageDraw.Draw(bg)
    rng = random.Random(7)
    for k in range(260):                                            # walnut grain
        y = rng.uniform(0, S); x = rng.uniform(-200, S)
        d.line([(x, y), (x + rng.uniform(300, 900), y + rng.uniform(-8, 8))], fill=A.shade((74, 50, 37), rng.uniform(0.85, 1.15)), width=rng.randint(1, 3))
    glow = Image.new("RGBA", (S, S), (0, 0, 0, 0)); ImageDraw.Draw(glow).ellipse([100, -300, 1500, 1100], fill=(255, 205, 140, 70))
    bg = bg.convert("RGBA"); bg.alpha_composite(glow.filter(ImageFilter.GaussianBlur(160)))
    fr = frame(grain(bg, seed=202, amount=1.0, vignette=0.0))
    # the page
    pw, ph = 1720, 1420
    page = Image.new("RGBA", (pw, ph), PAPER + (255,)); pd = ImageDraw.Draw(page)
    step = 88; top = 190
    for k in range(int((ph - top) / step) + 1):
        y = top + k * step
        pd.line([(0, y), (pw, y)], fill=(176, 196, 210), width=2)
    pd.line([(200, 0), (200, ph)], fill=(214, 120, 110), width=3)
    pd.line([(206, 0), (206, ph)], fill=(214, 120, 110), width=1)
    for hx in (90, 90):
        for hy in (300, 700, 1100):
            pd.ellipse([hx - 22, hy - 22, hx + 22, hy + 22], fill=(74, 50, 37, 255))
    pd.ellipse([1300, 1010, 1660, 1370], outline=(176, 140, 104, 90), width=10)          # an old tea ring
    pd.ellipse([1314, 1026, 1644, 1356], outline=(176, 140, 104, 50), width=4)
    page = grain(page, seed=203, amount=0.9).convert("RGBA")
    pd = ImageDraw.Draw(page)
    hand = F("kalam", 66); handb = F("kalamb", 74)
    pd.text((240, top - 18), "1 December", font=handb, fill=RUST_D, anchor="ls")
    pd.text((pw - 90, top - 18), "Candleholm Light", font=F("kalam", 46), fill=(120, 110, 104), anchor="rs")
    entry = C.JOURNAL[1]
    lines = wrap(pd, entry, hand, pw - 240 - 90)
    key = "Someone is using Candleholm as a cupboard."
    y = top + step - 18
    unders = []; on = False
    for ln in lines:
        pd.text((240, y), ln, font=hand, fill=(42, 52, 74), anchor="ls")
        a = ln.index("Someone") if "Someone" in ln else (0 if on else None)
        if a is not None:
            on = True
            b = len(ln)
            if "cupboard." in ln:
                b = ln.index("cupboard.") + len("cupboard."); on = False
            unders.append((240 + pd.textlength(ln[:a], font=hand), 240 + pd.textlength(ln[:b], font=hand), y))
        y += step
    sources = [("drawn", "journal 1 December (Window 1)", entry)]
    for xa, xb, yy in unders:                                       # red pencil under the sentence that matters
        for k in range(2):
            pts = [(xa + t * (xb - xa), yy + 14 + k * 7 + math.sin(t * 9 + k) * 3) for t in [i / 30 for i in range(31)]]
            pd.line(pts, fill=(190, 52, 40), width=6 - k * 2)
    pd.text((110, top + step * 4 - 18), "who?", font=F("kalamb", 64), fill=(190, 52, 40), anchor="ms")
    fr.paste(page, S / 2 + 10, 150 + ph / 2, angle=-1.8, shadow=True, shadow_strength=130)
    for kind, src, t in sources:
        fr.note(kind, src, t)
    fr.note("drawn", "hero", "who?"); fr.note("drawn", "hero", "1 December"); fr.note("drawn", "hero", "Candleholm Light")
    # the band
    d = fr.draw()
    d.rectangle([0, 1390, S, S], fill=NAVY)
    d.rectangle([0, 1390, S, 1400], fill=RUST)
    put(fr, (S / 2, 1488), "A COSY LIGHTHOUSE MYSTERY ADVENT CALENDAR", F("sansb", 46), OCHRE_L, tr=10)
    put(fr, (S / 2, 1646), "The Keeper of Candleholm", fit(d, "The Keeper of Candleholm", "gloock", 170, 1800), CREAM)
    put(fr, (S / 2, 1748), "24 DAYS  ·  PRINTABLE  ·  iPAD", F("sansb", 70), CREAM, tr=6)
    return fr

# ======================================================================== 3  chart (puzzle lovers)
def inside(pt, poly):
    x, y = pt; ins = False
    for i in range(len(poly)):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % len(poly)]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            ins = not ins
    return ins

def hero_chart():
    sc = 2
    X0, X1, Y0, Y1 = -15.0, 16.0, -17.5, 13.5
    M = 96
    k = (S - 2 * M) / (X1 - X0)
    def P(x, y):
        return ((M + (x - X0) * k) * sc, (M + (Y1 - y) * k) * sc)
    L = Image.new("RGBA", (S * sc, S * sc), (238, 232, 214, 255)); d = ImageDraw.Draw(L)
    d.rectangle([M * sc, M * sc, (S - M) * sc, (S - M) * sc], fill=(212, 228, 226))
    shallow = (196, 218, 216)
    for poly in (C.MAINLAND, C.INISHVARRA):
        pts = [P(*q) for q in poly]
        d.line(pts + [pts[0]], fill=shallow, width=int(1.4 * k * sc), joint="curve")
    for poly in (C.MAINLAND, C.INISHVARRA):                         # a dotted five-metre line
        cx_ = sum(q[0] for q in poly) / len(poly); cy_ = sum(q[1] for q in poly) / len(poly)
        ring = [P(cx_ + (q[0] - cx_) * 1.06, cy_ + (q[1] - cy_) * 1.03) for q in poly]
        for i in range(len(ring)):
            a, b = ring[i], ring[(i + 1) % len(ring)]
            n = int(math.dist(a, b) / (14 * sc))
            for j in range(0, n, 2):
                t0, t1 = j / max(n, 1), (j + 1) / max(n, 1)
                d.line([(a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0), (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)],
                       fill=(120, 150, 160), width=2 * sc)
    land = (240, 230, 203)
    for poly in (C.MAINLAND, C.INISHVARRA):
        d.polygon([P(*q) for q in poly], fill=land, outline=NAVY)
        pts = [P(*q) for q in poly]; d.line(pts + [pts[0]], fill=NAVY, width=3 * sc, joint="curve")
    for i in range(len(C.LOCH_PATH) - 1):                           # the loch, cut through the land
        a, b = C.LOCH_PATH[i], C.LOCH_PATH[i + 1]
        narrow = min(math.dist(a, C.NARROWS), math.dist(b, C.NARROWS)) < 0.1
        d.line([P(*a), P(*b)], fill=(212, 228, 226), width=int((0.45 if narrow else 1.2) * k * sc))
    rng = random.Random(9)
    for hx, hy in ((15, 6), (19, 8), (21, 18), (14, 19), (18, 1), (12, -9), (14, -14), (24, 4), (-11, 0), (-10, 7), (-10, -7), (20, -6)):
        px, py = P(hx, hy)
        for j in range(5):
            r = (34 - j * 6) * sc
            d.arc([px - r * 1.6, py - r, px + r * 1.6, py + r], 200, 340, fill=(196, 182, 150), width=2 * sc)
    # soundings: a patient lattice of depths across the open water
    fm = F("mono", 22 * sc)
    for gx in [X0 + 0.9 + i * 1.55 for i in range(20)]:
        for gy in [Y0 + 0.8 + j * 1.45 for j in range(22)]:
            x, y = gx + rng.uniform(-0.35, 0.35), gy + rng.uniform(-0.3, 0.3)
            if inside((x, y), C.MAINLAND) or inside((x, y), C.INISHVARRA) or math.hypot(x, y) < 1.4 \
                    or math.hypot(x + 10.4, y + 14.3) < 3.0:
                continue
            dist = min(min(math.dist((x, y), q) for q in C.MAINLAND), min(math.dist((x, y), q) for q in C.INISHVARRA))
            if dist < 0.9:
                continue
            depth = int(4 + dist * 5.5 + rng.uniform(-3, 3))
            px, py = P(x, y)
            d.text((px, py), str(depth), font=fm, fill=(98, 124, 138), anchor="mm")
    # range rings and the light
    cx, cy = P(0, 0)
    for rr in (3, 6, 9, 12):
        R = rr * k * sc
        for a in range(0, 360, 4):
            a0, a1 = math.radians(a), math.radians(a + 2.2)
            d.arc([cx - R, cy - R, cx + R, cy + R], a, a + 2.2, fill=(180, 120, 60) if rr == 12 else (150, 140, 120), width=(3 if rr == 12 else 2) * sc)
    d.text((cx + 12 * k * sc * 0.906 + 40 * sc, cy + 12 * k * sc * 0.423), "12 M", font=F("mono", 26 * sc), fill=(160, 100, 50), anchor="mm")
    d.ellipse([cx - 0.75 * k * sc, cy - 0.45 * k * sc, cx + 0.75 * k * sc, cy + 0.45 * k * sc], fill=land, outline=NAVY, width=2 * sc)
    fl = [(cx, cy), (cx + 30 * sc, cy - 70 * sc), (cx + 8 * sc, cy - 92 * sc), (cx - 10 * sc, cy - 60 * sc)]   # the magenta light flare
    d.polygon(fl, fill=(196, 70, 120))
    d.ellipse([cx - 7 * sc, cy - 7 * sc, cx + 7 * sc, cy + 7 * sc], fill=NAVY)
    # compass rose, lower left
    rx, ry = P(-10.4, -14.3); R = 150 * sc
    d.ellipse([rx - R, ry - R, rx + R, ry + R], outline=NAVY, width=2 * sc)
    d.ellipse([rx - R * 0.86, ry - R * 0.86, rx + R * 0.86, ry + R * 0.86], outline=NAVY, width=1 * sc)
    for a in range(0, 360, 5):
        ra = math.radians(a); l = 0.14 if a % 45 == 0 else (0.09 if a % 15 == 0 else 0.05)
        d.line([(rx + math.cos(ra) * R * 0.86, ry + math.sin(ra) * R * 0.86), (rx + math.cos(ra) * R * (0.86 - l), ry + math.sin(ra) * R * (0.86 - l))], fill=NAVY, width=sc)
    for a, ln in ((0, 0.8), (90, 0.8), (180, 0.8), (270, 0.8), (45, 0.5), (135, 0.5), (225, 0.5), (315, 0.5)):
        ra = math.radians(a - 90)
        tip = (rx + math.cos(ra) * R * ln, ry + math.sin(ra) * R * ln)
        l_ = (rx + math.cos(ra + 1.5708) * R * 0.08, ry + math.sin(ra + 1.5708) * R * 0.08)
        r_ = (rx + math.cos(ra - 1.5708) * R * 0.08, ry + math.sin(ra - 1.5708) * R * 0.08)
        d.polygon([tip, l_, (rx, ry)], fill=NAVY); d.polygon([tip, r_, (rx, ry)], fill=(238, 232, 214), outline=NAVY)
    d.text((rx, ry - R - 12 * sc), "N", font=F("arsenal", 40 * sc), fill=NAVY, anchor="ms")
    # labels from the Window 1 chart
    def label(xy, s, f, fill, angle=0):
        t = Image.new("RGBA", (int(d.textlength(s, font=f) + 40), int(f.size * 1.6)), (0, 0, 0, 0))
        ImageDraw.Draw(t).text((20, f.size * 0.2), s, font=f, fill=fill)
        t = t.rotate(angle, expand=True, resample=Image.BICUBIC)
        L.alpha_composite(t, (int(xy[0] - t.width / 2), int(xy[1] - t.height / 2)))
    label(P(-10.3, -2.0), "I N I S H V A R R A", F("arsenal", 34 * sc), NAVY, angle=88)
    label(P(-4.9, -2.6), "Sound of Candleholm", F("serif-i", 46 * sc), (70, 100, 120), angle=82)
    label(P(19.5, 12.4), "Loch Tarrisk", F("serif-i", 36 * sc), (70, 100, 120), angle=8)
    label(P(1.7, -1.4), "Candleholm", F("serif-i", 34 * sc), NAVY)
    # neatline with the alternating latitude scale
    d.rectangle([M * sc, M * sc, (S - M) * sc, (S - M) * sc], outline=NAVY, width=3 * sc)
    m2 = M - 26
    d.rectangle([m2 * sc, m2 * sc, (S - m2) * sc, (S - m2) * sc], outline=NAVY, width=2 * sc)
    seg = (S - 2 * M) / 31
    for i in range(31):
        if i % 2 == 0:
            a, b = (M + i * seg) * sc, (M + (i + 1) * seg) * sc
            for box in ([a, m2 * sc, b, M * sc], [a, (S - M) * sc, b, (S - m2) * sc], [m2 * sc, a, M * sc, b], [(S - M) * sc, a, (S - m2) * sc, b]):
                d.rectangle(box, fill=NAVY)
    paper = Image.new("RGBA", L.size, (238, 232, 214, 255))
    mask = Image.new("L", L.size, 0); ImageDraw.Draw(mask).rectangle([M * sc, M * sc, (S - M) * sc, (S - M) * sc], fill=255)
    paper.paste(L, (0, 0), mask); L = paper; d = ImageDraw.Draw(L)
    d.rectangle([M * sc, M * sc, (S - M) * sc, (S - M) * sc], outline=NAVY, width=3 * sc)
    d.rectangle([m2 * sc, m2 * sc, (S - m2) * sc, (S - m2) * sc], outline=NAVY, width=2 * sc)
    for i in range(31):
        if i % 2 == 0:
            a, b = (M + i * seg) * sc, (M + (i + 1) * seg) * sc
            for box in ([a, m2 * sc, b, M * sc], [a, (S - M) * sc, b, (S - m2) * sc], [m2 * sc, a, M * sc, b], [(S - M) * sc, a, (S - m2) * sc, b]):
                d.rectangle(box, fill=NAVY)
    img = L.resize((S, S), Image.LANCZOS)
    fr = frame(grain(img, seed=303, amount=0.6))
    fr.note("drawn", "chart", "INISHVARRA Sound of Candleholm Loch Tarrisk Candleholm 12 M N")
    # cartouche
    cw, chh = 1380, 500
    car = Image.new("RGBA", (cw, chh), (0, 0, 0, 0)); cd = ImageDraw.Draw(car)
    cd.rectangle([0, 0, cw - 1, chh - 1], fill=(246, 241, 226), outline=NAVY, width=5)
    cd.rectangle([16, 16, cw - 17, chh - 17], outline=NAVY, width=2)
    for (ox, oy) in ((16, 16), (cw - 17, 16), (16, chh - 17), (cw - 17, chh - 17)):
        cd.ellipse([ox - 10, oy - 10, ox + 10, oy + 10], fill=RUST)
    fr.paste(car, S / 2, 150 + chh / 2 + 40, shadow=True, shadow_strength=60)
    put(fr, (S / 2, 300), "A LIGHTHOUSE MYSTERY ADVENT CALENDAR", F("arsenal", 50), RUST_D, tr=6)
    put(fr, (S / 2, 410), "THE KEEPER OF", F("arsenal", 104), NAVY, tr=10)
    put(fr, (S / 2, 600), "Candleholm", fit(fr.draw(), "Candleholm", "gloock", 230, 1200), NAVY)
    put(fr, (S / 2, 660), "surveyed by the keeper, 1 to 24 December", F("serif-i", 44), (90, 104, 112))
    # legend box, lower centre
    lw, lh = 720, 400
    lg = Image.new("RGBA", (lw, lh), (0, 0, 0, 0)); ld = ImageDraw.Draw(lg)
    ld.rectangle([0, 0, lw - 1, lh - 1], fill=(246, 241, 226), outline=NAVY, width=5)
    ld.rectangle([14, 14, lw - 15, lh - 15], outline=NAVY, width=2)
    lx, ly = 1010, 1540
    fr.paste(lg, lx, ly, shadow=True, shadow_strength=60)
    put(fr, (lx, ly - 70), "24 DAYS", F("gloock", 150), RUST)
    put(fr, (lx, ly + 40), "PRINTABLE  ·  iPAD", F("sansb", 62), NAVY, tr=5)
    put(fr, (lx, ly + 130), "2,400 travellers  ·  one answer", F("serif-i", 54), (70, 90, 104))
    return fr

# ======================================================================== 4  the lamp that did not light (mood)
def hero_lamp():
    sc = 2
    L = Image.new("RGBA", (S * sc, S * sc), (0, 0, 0, 255)); d = ImageDraw.Draw(L)
    top, bot = (22, 40, 56), (36, 70, 86)
    for y in range(0, S * sc, 4):
        t = y / (S * sc); d.rectangle([0, y, S * sc, y + 4], fill=A.lerp(top, bot, t))
    # a lattice of snow: perfect spacing, size breathing in a slow wave
    for i in range(41):
        for j in range(41):
            x = (i * 50 + (25 if j % 2 else 0)) * sc; y = (j * 50) * sc
            r = (2.2 + 1.6 * (0.5 + 0.5 * math.sin(i * 0.45 + j * 0.31))) * sc
            d.ellipse([x - r, y - r, x + r, y + r], fill=(220, 228, 230, 255))
    tx, base, tw_b, tw_t, th = 1470 * sc, 1900 * sc, 400 * sc, 270 * sc, 1350 * sc
    ttop = base - th
    # the ghost of the beam: where the light should be
    lx, ly = tx, ttop - 120 * sc
    g = Image.new("RGBA", L.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    for a0, a1 in ((168, 196),):
        pts = [(lx, ly)] + [(lx + math.cos(math.radians(a)) * 2600 * sc, ly + math.sin(math.radians(a)) * 2600 * sc) for a in (a0, a1)]
        gd.polygon(pts, fill=(240, 226, 190, 16))
    L.alpha_composite(g)
    for a in (168, 196):
        ra = math.radians(a); n = 120
        for j in range(0, n, 2):
            t0, t1 = j / n, (j + 1) / n
            p0 = (lx + math.cos(ra) * 2600 * sc * t0, ly + math.sin(ra) * 2600 * sc * t0)
            p1 = (lx + math.cos(ra) * 2600 * sc * t1, ly + math.sin(ra) * 2600 * sc * t1)
            d.line([p0, p1], fill=(214, 200, 168), width=2 * sc)
    # rock, cottage with a lit window, Bosun
    d.ellipse([tx - 900 * sc, base - 90 * sc, tx + 760 * sc, base + 260 * sc], fill=(30, 50, 46))
    d.ellipse([tx - 760 * sc, base - 110 * sc, tx + 560 * sc, base + 160 * sc], fill=(48, 72, 56))
    cx0 = tx - 700 * sc; cy = base - 80 * sc
    d.rectangle([cx0, cy - 150 * sc, cx0 + 300 * sc, cy], fill=(226, 218, 200))
    d.polygon([(cx0 - 20 * sc, cy - 150 * sc), (cx0 + 150 * sc, cy - 250 * sc), (cx0 + 320 * sc, cy - 150 * sc)], fill=(70, 80, 92))
    w = Image.new("RGBA", L.size, (0, 0, 0, 0)); ImageDraw.Draw(w).ellipse([cx0 + 40 * sc, cy - 150 * sc, cx0 + 180 * sc, cy - 10 * sc], fill=(255, 200, 110, 150))
    L.alpha_composite(w.filter(ImageFilter.GaussianBlur(30 * sc)))
    d.rectangle([cx0 + 70 * sc, cy - 120 * sc, cx0 + 150 * sc, cy - 50 * sc], fill=(246, 196, 104))
    d.line([(cx0 + 110 * sc, cy - 120 * sc), (cx0 + 110 * sc, cy - 50 * sc)], fill=(70, 60, 50), width=4 * sc)
    d.rectangle([cx0 + 220 * sc, cy - 100 * sc, cx0 + 270 * sc, cy], fill=RUST)
    # the tower: tapered, four rust bands, gallery, a dark lantern
    def tw(y):
        t = (base - y) / th; return tw_b + (tw_t - tw_b) * t
    d.polygon([(tx - tw(base) / 2, base), (tx + tw(base) / 2, base), (tx + tw(ttop) / 2, ttop), (tx - tw(ttop) / 2, ttop)], fill=(240, 234, 220))
    for b in range(4):
        y1 = base - th * (0.12 + b * 0.22); y0 = y1 - th * 0.1
        d.polygon([(tx - tw(y1) / 2, y1), (tx + tw(y1) / 2, y1), (tx + tw(y0) / 2, y0), (tx - tw(y0) / 2, y0)], fill=RUST)
    sh_ = Image.new("RGBA", L.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh_).polygon([(tx + tw(base) / 2, base), (tx + tw(base) / 2 * 0.42, base), (tx + tw(ttop) / 2 * 0.42, ttop), (tx + tw(ttop) / 2, ttop)], fill=(10, 20, 30, 60))
    L.alpha_composite(sh_); d = ImageDraw.Draw(L)
    d.rectangle([tx - 30 * sc, base - 150 * sc, tx + 30 * sc, base - 40 * sc], fill=(60, 40, 34))
    gy = ttop
    d.rectangle([tx - tw_t / 2 - 40 * sc, gy - 18 * sc, tx + tw_t / 2 + 40 * sc, gy], fill=(30, 30, 34))
    for k in range(9):
        xx = tx - tw_t / 2 - 30 * sc + k * (tw_t + 60 * sc) / 8
        d.line([(xx, gy - 18 * sc), (xx, gy - 70 * sc)], fill=(30, 30, 34), width=4 * sc)
    d.line([(tx - tw_t / 2 - 40 * sc, gy - 70 * sc), (tx + tw_t / 2 + 40 * sc, gy - 70 * sc)], fill=(30, 30, 34), width=5 * sc)
    lw_ = tw_t * 0.62
    d.rectangle([tx - lw_ / 2, gy - 190 * sc, tx + lw_ / 2, gy - 18 * sc], fill=(20, 30, 40))
    for k in range(4):
        xx = tx - lw_ / 2 + k * lw_ / 3
        d.line([(xx, gy - 190 * sc), (xx, gy - 18 * sc)], fill=(70, 84, 96), width=4 * sc)
    d.polygon([(tx - lw_ / 2 - 26 * sc, gy - 190 * sc), (tx + lw_ / 2 + 26 * sc, gy - 190 * sc), (tx, gy - 300 * sc)], fill=RUST)
    d.line([(tx, gy - 300 * sc), (tx, gy - 350 * sc)], fill=(30, 30, 34), width=5 * sc)
    img = L.resize((S, S), Image.LANCZOS)
    cvs = A.Canvas(S // 2, S // 2, ss=2, bg=(0, 0, 0)); cvs.img.putalpha(0)
    CO.cat_sitting(cvs, (tx / sc - 330) / 2, (base / sc - 92) / 2, 62, col=OCHRE)
    img = img.convert("RGBA"); img.alpha_composite(cvs.img.resize((S, S), Image.LANCZOS))
    fr = frame(grain(img, seed=404, amount=0.8))
    put(fr, (140, 420), "Christmas Eve.", F("serif-i", 118), OCHRE_L, anchor="l")
    put(fr, (140, 545), "The lamp never lit.", F("serif-i", 118), CREAM, anchor="l")
    d2 = fr.draw()
    ft = fit(d2, "CANDLEHOLM", "tall", 330, 1150, 0.02)
    put(fr, (140, 900), "THE KEEPER OF", F("tall", int(ft.size * 0.62)), CREAM, tr=int(ft.size * 0.02), anchor="l")
    put(fr, (140, 900 + ft.size * 0.95), "CANDLEHOLM", ft, CREAM, tr=int(ft.size * 0.02), anchor="l")
    yb = 900 + ft.size * 0.95
    put(fr, (146, yb + 120), "A COSY MYSTERY ADVENT CALENDAR", F("sansb", 42), (196, 210, 214), tr=9, anchor="l")
    d2 = fr.draw()
    d2.rectangle([140, yb + 175, 1000, yb + 185], fill=RUST)
    put(fr, (140, yb + 290), "24 DAYS  ·  PRINTABLE  ·  iPAD", fit(fr.draw(), "24 DAYS  ·  PRINTABLE  ·  iPAD", "sansb", 72, 1020, 0.07), OCHRE_L, tr=4, anchor="l")
    return fr

# ======================================================================== 5  two at the table (couples)
def hero_two(A_):
    cv = A.Canvas(S // 2, S // 2, ss=2, bg=(50, 72, 56))
    W = H = S // 2
    for k in range(0, W, 24):                                       # a woven check tablecloth
        cv.rect((k, 0, k + 8, H), (58, 82, 64))
        cv.rect((0, k, W, k + 8), (58, 82, 64))
    for k in range(0, W, 96):
        cv.rect((k + 2, 0, k + 5, H), (120, 62, 48))
        cv.rect((0, k + 2, W, k + 5), (120, 62, 48))
    cv.glow(W * 0.5, H * 0.58, W * 0.55, (255, 210, 150), alpha=48)
    CO.mug_top(cv, W * 0.13, H * 0.86, 78)
    CO.mug_top(cv, W * 0.88, H * 0.36, 78)
    CO.pine(cv, W + 20, H * 0.86, W * 0.78, H * 0.94, s=1.2, seed=5)
    A.holly(cv, W * 0.86, H * 0.9, 34)
    CO.fairy_lights(cv, [(-10, H * 0.965), (W * 0.3, H * 0.94), (W * 0.62, H * 0.97), (W + 10, H * 0.945)], 12, seed=8)
    img = cv.finish(seed=505).resize((S, S), Image.LANCZOS)
    fr = frame(img)
    # the printed Sound Book page with strikes, and the iPad calendar
    b = A_.L.image(A_.log_page, 1100)
    x0, y0 = 1330 - b.img.width / 2, 1160 - b.img.height / 2
    fr.paste_page(b, 1330, 1160, angle=0)
    rows = CL.log_rows(A_.L, A_.log_page)
    rng = random.Random(11)
    for j, (yt, yb, xa, xb, _) in enumerate(rows):
        if rng.random() < 0.6:
            px0, py = b.px(xa, (yt + yb) / 2); px1, _ = b.px(xb, 0)
            kit.pencil_strike(fr, x0 + px0 - 4, y0 + py, x0 + px1 - b.zoom * 20, (yb - yt) * b.zoom * 1.3, seed=j)
    scr = A_.I.image(A_.ip["calendar"], 1040)
    ih = 1040; iw = ih * 0.75
    tab = kit.Frame(int(iw) + 40, ih + 40); tab.img = Image.new("RGBA", tab.img.size, (0, 0, 0, 0))
    kit.ipad(tab, (20, 20, 20 + iw, 20 + ih), scr)
    fr.paste(tab.img, 690, 1150, angle=-5)
    for kind, src, text in tab.sources:
        fr.note(kind, src, text)
    for (px, py, ang) in ((1060, 1640, -28), (1790, 640, 62)):        # two pencils
        p = Image.new("RGBA", (420, 40), (0, 0, 0, 0)); pd = ImageDraw.Draw(p)
        pd.rectangle([40, 8, 400, 32], fill=RUST); pd.polygon([(40, 8), (0, 20), (40, 32)], fill=(226, 190, 140))
        pd.polygon([(12, 16), (0, 20), (12, 24)], fill=INK); pd.rectangle([380, 8, 400, 32], fill=(200, 200, 196))
        fr.paste(p, px, py, angle=ang, shadow=True, shadow_strength=80)
    # type
    put(fr, (S / 2, 300), "YOUR NEW DECEMBER DATE NIGHT", F("sansb", 56), OCHRE_L, tr=12)
    put(fr, (S / 2, 470), "The Keeper of Candleholm", fit(fr.draw(), "The Keeper of Candleholm", "young", 150, 1760), CREAM)
    pill(fr, S / 2, 1735, "24 DAYS  ·  PRINT IT OR PLAY ON iPAD", F("sansb", 62), CREAM, NAVY, tr=5)
    return fr

# ======================================================================== build + checks
NAMES = {1: ("1-envelopes", "Gift: 24 envelopes"), 2: ("2-journal", "Mystery readers: the journal"),
         3: ("3-chart", "Puzzle lovers: the chart"), 4: ("4-lamp", "Mood: the lamp never lit"),
         5: ("5-date-night", "Couples: date night")}

def build(which=None):
    os.makedirs(OUT, exist_ok=True)
    sys.path.insert(0, os.path.join(CL.CASE, "src"))
    import verify as VER
    bad = CL.forbidden()
    A_ = None
    report = []
    for n in which or sorted(NAMES):
        if n == 5:
            if A_ is None:
                A_ = type("X", (), {})(); A_.L, A_.I, A_.p, A_.ip = CL.pages()
                A_.log_page = CL.clean_log_pages(A_.L, bad)[len(CL.clean_log_pages(A_.L, bad)) // 3]
            fr = hero_two(A_)
        else:
            fr = {1: hero_envelopes, 2: hero_journal, 3: hero_chart, 4: hero_lamp}[n]()
        slug, label = NAMES[n]
        path = os.path.join(OUT, f"{CL.SLUG}_hero-{slug}.jpg")
        fr.img.convert("RGB").save(path, quality=90, optimize=True)
        hits = kit.spoiler_scan(fr.sources, bad)
        drawn = [t for k, _, t in fr.sources if k == "drawn"]
        stop = sorted({b for b in VER.BANNED for t in drawn if re.search(r"\b" + re.escape(b.lower()) + r"\b", t.lower())})
        clue = [t for t in drawn if re.search(r"\bclues?\b", t.lower())]
        txt = " ".join(drawn)
        need = all(s in txt for s in ("Candleholm" if n != 4 else "CANDLEHOLM", "24 DAYS", "PRINT", "iPAD"))
        report.append((n, label, len(hits), stop, clue, need))
        print(slug, "spoilers", len(hits), "stop", stop, "clue", clue, "title/24/print/ipad", need, flush=True)
    return report

def sheet():
    ims = [Image.open(os.path.join(OUT, f"{CL.SLUG}_hero-{NAMES[n][0]}.jpg")).convert("RGB") for n in sorted(NAMES)]
    W = 600; pad = 30; lab = F("sansb", 30)
    sh = Image.new("RGB", (5 * W + 6 * pad, 60 + W + 70 + 250 + 70 + 188 + 40), CREAM); d = ImageDraw.Draw(sh)
    for i, (n, im) in enumerate(zip(sorted(NAMES), ims)):
        x = pad + i * (W + pad)
        d.text((x + W / 2, 42), f"{n}. {NAMES[n][1].upper()}", font=lab, fill=NAVY, anchor="ms")
        sh.paste(im.resize((W, W), Image.LANCZOS), (x, 60))
        y2 = 60 + W + 60
        sh.paste(im.resize((250, 250), Image.LANCZOS), (int(x + W / 2 - 125), y2))
        y3 = y2 + 250 + 60
        crop = im.crop((0, 250, S, S - 250)).resize((250, 188), Image.LANCZOS)  # 4:3 centre crop
        sh.paste(crop, (int(x + W / 2 - 125), y3))
    d.text((sh.width / 2, 60 + W + 45), "at Etsy search size (250 px)", font=F("serif-i", 34), fill=RUST_D, anchor="ms")
    d.text((sh.width / 2, 60 + W + 60 + 250 + 45), "and cropped to 4:3, as the search grid may show it", font=F("serif-i", 34), fill=RUST_D, anchor="ms")
    p = os.path.join(OUT, f"{CL.SLUG}_hero-options_sheet.jpg"); sh.save(p, quality=88)
    return p

if __name__ == "__main__":
    which = [int(a) for a in sys.argv[1:]] or None
    build(which)
    print(sheet())
