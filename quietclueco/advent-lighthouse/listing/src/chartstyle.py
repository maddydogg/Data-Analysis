"""The listing's visual system after the seller chose hero 3: a vintage nautical chart of the Sound.

One high-resolution chart (the Window 1 geography: the mainland, Inishvarra, Loch Tarrisk, Candleholm and its
range rings, a lattice of soundings, a compass rose) is drawn once. Every listing image takes its own region of it,
zoomed and lightened, inside a chart neatline with the alternating latitude scale; headlines sit in a cartouche,
facts in legend boxes, notes in the keeper's hand. Design philosophy: listing/hero-options/design-philosophy.md.
"""
import math, random
from PIL import Image, ImageDraw
import kit
from cal_listing import art as A, C
import heroes as H

S = H.S
M = 96                                  # neatline inset
RAW = (S - 2 * M) * 2                   # chart drawn at 2x the inner frame
X0, X1, Y0, Y1 = -15.0, 16.0, -17.5, 13.5
K = RAW / (X1 - X0)                     # raw px per nautical mile
PAPER = (238, 232, 214); CARD = (246, 241, 226); SEA = (212, 228, 226); SHALLOW = (196, 218, 216); LAND = (240, 230, 203)
NAVY, RUST, RUST_D = H.NAVY, H.RUST, H.RUST_D
GREY = (70, 90, 104)

def P(x, y):
    return ((x - X0) * K, (Y1 - y) * K)

_raw = None
def chart_raw():
    """The whole chart, full bleed, RAW x RAW px."""
    global _raw
    if _raw is not None:
        return _raw
    L = Image.new("RGBA", (RAW, RAW), SEA + (255,)); d = ImageDraw.Draw(L)
    for poly in (C.MAINLAND, C.INISHVARRA):
        pts = [P(*q) for q in poly]
        d.line(pts + [pts[0]], fill=SHALLOW, width=int(1.4 * K), joint="curve")
    for poly in (C.MAINLAND, C.INISHVARRA):                         # a dotted five-metre line
        cx_ = sum(q[0] for q in poly) / len(poly); cy_ = sum(q[1] for q in poly) / len(poly)
        ring = [P(cx_ + (q[0] - cx_) * 1.06, cy_ + (q[1] - cy_) * 1.03) for q in poly]
        for i in range(len(ring)):
            a, b = ring[i], ring[(i + 1) % len(ring)]
            n = int(math.dist(a, b) / 28)
            for j in range(0, n, 2):
                t0, t1 = j / max(n, 1), (j + 1) / max(n, 1)
                d.line([(a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0), (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)],
                       fill=(120, 150, 160), width=4)
    for poly in (C.MAINLAND, C.INISHVARRA):
        d.polygon([P(*q) for q in poly], fill=LAND)
        pts = [P(*q) for q in poly]; d.line(pts + [pts[0]], fill=NAVY, width=6, joint="curve")
    for i in range(len(C.LOCH_PATH) - 1):                           # the loch, cut through the land
        a, b = C.LOCH_PATH[i], C.LOCH_PATH[i + 1]
        narrow = min(math.dist(a, C.NARROWS), math.dist(b, C.NARROWS)) < 0.1
        d.line([P(*a), P(*b)], fill=SEA, width=int((0.45 if narrow else 1.2) * K))
    rng = random.Random(9)
    for hx, hy in ((15, 6), (19, 8), (21, 18), (14, 19), (18, 1), (12, -9), (14, -14), (24, 4), (-11, 0), (-10, 7), (-10, -7), (20, -6), (12, 3), (13, -4)):
        px, py = P(hx, hy)
        for j in range(5):
            r = (34 - j * 6) * 2
            d.arc([px - r * 1.6, py - r, px + r * 1.6, py + r], 200, 340, fill=(196, 182, 150), width=4)
    fm = H.F("mono", 44)                                            # soundings: a patient lattice of depths
    for gx in [X0 + 0.9 + i * 1.55 for i in range(20)]:
        for gy in [Y0 + 0.8 + j * 1.45 for j in range(22)]:
            x, y = gx + rng.uniform(-0.35, 0.35), gy + rng.uniform(-0.3, 0.3)
            if H.inside((x, y), C.MAINLAND) or H.inside((x, y), C.INISHVARRA) or math.hypot(x, y) < 1.4 \
                    or math.hypot(x + 10.4, y + 14.3) < 3.0:
                continue
            dist = min(min(math.dist((x, y), q) for q in C.MAINLAND), min(math.dist((x, y), q) for q in C.INISHVARRA))
            if dist < 0.9:
                continue
            px, py = P(x, y)
            d.text((px, py), str(int(4 + dist * 5.5 + rng.uniform(-3, 3))), font=fm, fill=(98, 124, 138), anchor="mm")
    cx, cy = P(0, 0)                                                # range rings and the light
    for rr in (3, 6, 9, 12):
        R = rr * K
        for a in range(0, 360, 4):
            d.arc([cx - R, cy - R, cx + R, cy + R], a, a + 2.2, fill=(180, 120, 60) if rr == 12 else (150, 140, 120), width=6 if rr == 12 else 4)
    d.text((cx + 12 * K * 0.906 + 80, cy + 12 * K * 0.423), "12 M", font=H.F("mono", 52), fill=(160, 100, 50), anchor="mm")
    d.ellipse([cx - 0.75 * K, cy - 0.45 * K, cx + 0.75 * K, cy + 0.45 * K], fill=LAND, outline=NAVY, width=4)
    d.polygon([(cx, cy), (cx + 60, cy - 140), (cx + 16, cy - 184), (cx - 20, cy - 120)], fill=(196, 70, 120))
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=NAVY)
    rx, ry = P(-10.4, -14.3); R = 300                               # compass rose
    d.ellipse([rx - R, ry - R, rx + R, ry + R], outline=NAVY, width=4)
    d.ellipse([rx - R * 0.86, ry - R * 0.86, rx + R * 0.86, ry + R * 0.86], outline=NAVY, width=2)
    for a in range(0, 360, 5):
        ra = math.radians(a); l = 0.14 if a % 45 == 0 else (0.09 if a % 15 == 0 else 0.05)
        d.line([(rx + math.cos(ra) * R * 0.86, ry + math.sin(ra) * R * 0.86), (rx + math.cos(ra) * R * (0.86 - l), ry + math.sin(ra) * R * (0.86 - l))], fill=NAVY, width=2)
    for a, ln in ((0, 0.8), (90, 0.8), (180, 0.8), (270, 0.8), (45, 0.5), (135, 0.5), (225, 0.5), (315, 0.5)):
        ra = math.radians(a - 90)
        tip = (rx + math.cos(ra) * R * ln, ry + math.sin(ra) * R * ln)
        l_ = (rx + math.cos(ra + 1.5708) * R * 0.08, ry + math.sin(ra + 1.5708) * R * 0.08)
        r_ = (rx + math.cos(ra - 1.5708) * R * 0.08, ry + math.sin(ra - 1.5708) * R * 0.08)
        d.polygon([tip, l_, (rx, ry)], fill=NAVY); d.polygon([tip, r_, (rx, ry)], fill=PAPER, outline=NAVY)
    d.text((rx, ry - R - 24), "N", font=H.F("arsenal", 80), fill=NAVY, anchor="ms")
    def label(xy, s, f, fill, angle=0):
        t = Image.new("RGBA", (int(d.textlength(s, font=f) + 40), int(f.size * 1.6)), (0, 0, 0, 0))
        ImageDraw.Draw(t).text((20, f.size * 0.2), s, font=f, fill=fill)
        t = t.rotate(angle, expand=True, resample=Image.BICUBIC)
        L.alpha_composite(t, (int(xy[0] - t.width / 2), int(xy[1] - t.height / 2)))
    label(P(-10.3, -2.0), "I N I S H V A R R A", H.F("arsenal", 68), NAVY, angle=88)
    label(P(-4.9, -2.6), "Sound of Candleholm", H.F("serif-i", 92), (70, 100, 120), angle=82)
    label(P(19.5, 12.4), "Loch Tarrisk", H.F("serif-i", 72), (70, 100, 120), angle=8)
    label(P(1.7, -1.4), "Candleholm", H.F("serif-i", 68), NAVY)
    _raw = L.convert("RGB")
    return _raw

LABELS = "INISHVARRA Sound of Candleholm Loch Tarrisk Candleholm 12 M N"

def neatline(d, m=M):
    m2 = m - 26
    d.rectangle([m, m, S - m, S - m], outline=NAVY, width=3)
    d.rectangle([m2, m2, S - m2, S - m2], outline=NAVY, width=2)
    seg = (S - 2 * m) / 31
    for i in range(0, 31, 2):
        a, b = m + i * seg, m + (i + 1) * seg
        for box in ([a, m2, b, m], [a, S - m, b, S - m2], [m2, a, m, b], [S - m, a, S - m2, b]):
            d.rectangle(box, fill=NAVY)

def chart_bg(cx=0.5, cy=0.5, zoom=1.0, lighten=0.0, seed=1, size=S):
    """A region of the chart inside the neatline: centre (cx, cy) as fractions, zoom >= 1, lighten 0..1 toward card."""
    raw = chart_raw()
    w = RAW / zoom
    x0 = min(max(cx * RAW - w / 2, 0), RAW - w); y0 = min(max(cy * RAW - w / 2, 0), RAW - w)
    inner = raw.crop((int(x0), int(y0), int(x0 + w), int(y0 + w))).resize((S - 2 * M, S - 2 * M), Image.LANCZOS)
    if lighten:
        inner = Image.blend(inner, Image.new("RGB", inner.size, CARD), lighten)
    img = Image.new("RGB", (S, S), PAPER); img.paste(inner, (M, M))
    neatline(ImageDraw.Draw(img))
    img = H.grain(img, seed=seed, amount=0.6)
    return img if size == S else img.resize((size, size), Image.LANCZOS)

def frame_on(cx=0.5, cy=0.5, zoom=1.0, lighten=0.0, seed=1):
    fr = H.frame(chart_bg(cx, cy, zoom, lighten, seed))
    fr.note("drawn", "chart", LABELS)
    return fr

def box(w, h, fill=CARD, dots=True):
    """A chart cartouche or legend box: double navy rule, rust corner dots."""
    im = Image.new("RGBA", (int(w), int(h)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w - 1, h - 1], fill=fill, outline=NAVY, width=5)
    d.rectangle([14, 14, w - 15, h - 15], outline=NAVY, width=2)
    if dots:
        for (ox, oy) in ((14, 14), (w - 15, 14), (14, h - 15), (w - 15, h - 15)):
            d.ellipse([ox - 9, oy - 9, ox + 9, oy + 9], fill=RUST)
    return im

def cartouche(fr, title, kicker=None, sub=None, y=150, w=1500):
    """Headline cartouche at the top of a listing image. Returns its bottom edge."""
    h = 40 + (60 if kicker else 0) + 132 + (66 if sub else 0) + 38
    fr.paste(box(w, h), S / 2, y + h / 2, shadow=True, shadow_strength=55)
    yy = y + 40
    if kicker:
        H.put(fr, (S / 2, yy + 44), kicker, H.F("arsenal", 44), RUST_D, tr=6); yy += 60
    ft = H.fit(fr.draw(), title, "gloock", 124, w - 120)
    H.put(fr, (S / 2, yy + 112), title, ft, NAVY); yy += 132
    if sub:
        H.put(fr, (S / 2, yy + 46), sub, H.fit(fr.draw(), sub, "serif-i", 52, w - 120), GREY)
    return y + h

def legend(fr, cx, cy, lines, w=None, angle=0, pad=40):
    """A legend box holding short lines: (text, font, colour, tracking)."""
    d = fr.draw()
    w = w or max(H.width(d, t, f, tr) for t, f, c, tr in lines) + 2 * pad + 20
    h = sum(f.size * 1.32 for _, f, _, _ in lines) + 2 * pad
    im = box(w, h); idr = ImageDraw.Draw(im)
    y = pad
    for t, f, c, tr in lines:
        y += f.size * 1.08
        tw = H.width(idr, t, f, tr); x = w / 2 - tw / 2
        for ch in t:
            idr.text((x, y), ch, font=f, fill=c, anchor="ls"); x += idr.textlength(ch, font=f) + tr
        y += f.size * 0.24
        fr.note("drawn", "legend", t)
    fr.paste(im, cx, cy, angle=angle, shadow=True, shadow_strength=60)

FOOT = "THE KEEPER OF CANDLEHOLM  ·  A LIGHTHOUSE MYSTERY ADVENT CALENDAR"
def footer(fr):
    f = H.F("arsenal", 34)
    w = H.width(fr.draw(), FOOT, f, 4) + 80
    fr.paste(box(w, 70, dots=False), S / 2, 1846, shadow=False)
    H.put(fr, (S / 2, 1858), FOOT, f, NAVY, tr=4)

def note(fr, xy, text, size=70, col=RUST_D, angle=-4):
    """A line in the keeper's hand (Kalam), as if pencilled onto the chart."""
    f = H.F("kalamb", size)
    im = Image.new("RGBA", (int(fr.draw().textlength(text, font=f) + 40), int(size * 1.7)), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((20, size * 0.1), text, font=f, fill=col)
    fr.paste(im, xy[0], xy[1], angle=angle, shadow=False)
    fr.note("drawn", "note", text)
