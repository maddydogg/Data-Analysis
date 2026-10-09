"""Ten listing images: 2000 x 2000 JPG in the chart style the seller chose (hero option 3).

01 is the chart of the Sound with the title cartouche; then one window a night; Days 1, 2 and 3; print and fold; iPad;
who it's for; what you get; exactly one answer. Every image takes its own region of the same chart (chartstyle.py),
with a headline cartouche, legend boxes and notes in the keeper's hand, and the pages shown as they look in play:
pencil strikes in the Sound Book, a ring round the island on the chart, ticks on the calendar.

Only Windows 1-3 and the set-up pages are shown. Every string drawn and the text layer of every PDF region pasted is
recorded on the kit.Frame, so the spoiler check reads exactly what a buyer can read.
"""
import math, os, random
from PIL import Image, ImageDraw, ImageFilter
import kit
import cal_listing as CL
from cal_listing import art as A, scenes as SC, COVER
import cover_options as CO
import heroes as H
import chartstyle as CS

S = 2000
NAMES = ["01-main", "02-one-window-a-night", "03-day-1-the-case", "04-day-2-the-sound-book", "05-a-new-lead-each-night",
         "06-print-and-fold", "07-ipad-calendar", "08-who-its-for", "09-whats-inside", "10-exactly-one-answer"]

class Assets:
    def __init__(self):
        self.bad = CL.forbidden()
        self.L, self.I, self.p, self.ip = CL.pages()
        clean = CL.clean_log_pages(self.L, self.bad)
        self.log_page = clean[len(clean) // 3]

# ---------------------------------------------------------------- illustrated backgrounds
def bg_table(seed=1, wood=(164, 116, 76)):
    """A honey-pine table seen from above in lamplight: fairy lights along the top, pine and holly, a mug of
    cocoa, a pencil and a few tallies in the corners."""
    cv = A.Canvas(S // 2, S // 2, ss=2, bg=wood)
    W = H = S // 2
    for k in range(9):                                     # planks
        y = k * H / 9
        cv.rect((0, y, W, y + 3), A.shade(wood, 0.84))
        rng = random.Random(seed + k)
        for _ in range(6):
            x = rng.uniform(0, W); cv.line([(x, y + 12), (x + rng.uniform(40, 120), y + 14 + rng.uniform(-3, 3))], A.shade(wood, 0.92), w=1.2)
    cv.glow(W * 0.5, H * 0.45, W * 0.6, (255, 214, 150), alpha=70)
    CO.pine(cv, -20, H * 0.5, W * 0.14, H * 0.36, s=1.2, seed=seed)
    CO.pine(cv, W + 20, H * 0.62, W * 0.86, H * 0.5, s=1.1, seed=seed + 1)
    A.holly(cv, W * 0.08, H * 0.42, 34)
    rng = random.Random(seed)
    corners = [(0.07, 0.9), (0.93, 0.88)]
    for k, (cx, cy) in enumerate(corners):
        kind = (k + seed) % 3
        if kind == 0:
            CO.mug_top(cv, W * cx, H * cy, 58)
        elif kind == 1:
            cv.line([(W * cx - 70, H * cy + 20), (W * cx + 60, H * cy - 30)], A.RUST, w=10)
            cv.line([(W * cx + 60, H * cy - 30), (W * cx + 76, H * cy - 36)], A.INK, w=5)
        else:
            for q in range(3):
                A.tally(cv, W * cx + q * 34 - 34, H * cy + (q % 2) * 22, 20, metal=[A.BRASS, A.COPPER, A.TIN][q])
    CO.fairy_lights(cv, [(-10, 8), (200, 26), (430, 10), (650, 28), (860, 9), (1010, 22)], 14, seed=seed)
    im = cv.finish(seed=seed).resize((S, S), Image.LANCZOS)
    return im

def bg_room(seed=1, cat=True, dim=0.0):
    """The window seat at dusk (the main image's scene) with an empty wall for the headline."""
    cv = CO.window_seat(cat_x=0.86 if cat else None, journal=False)
    im = cv.finish(seed=seed).resize((S, S), Image.LANCZOS)
    if dim:
        im = Image.blend(im, Image.new("RGB", im.size, A.CREAM), dim)
    return im

def sunset_keyart(w, h, **kw):
    old = SC.DUSK_SKY; SC.DUSK_SKY = CO.SUNSET
    try:
        return SC.keyart(w, h, **kw)
    finally:
        SC.DUSK_SKY = old

def bg_scene(fn, seed=1, dim=0.0):
    im = fn(S // 2, S // 2).resize((S, S), Image.LANCZOS)
    if dim:
        im = Image.blend(im, Image.new("RGB", im.size, A.NIGHT), dim)
    return im

def frame_from(im):
    f = kit.Frame(S, S); f.img = im.convert("RGBA"); return f

# ---------------------------------------------------------------- type
def headline(f, top, sub=None, y=200, on_dark=True):
    """Poster headline: Josefin capitals in cream with a rust offset (or navy on light), a ribbon subline."""
    fnt = kit.fit_font(f, top, "display", 150, S - 260)
    col = A.CREAM if on_dark else A.NIGHT
    sh = max(4, fnt.size // 20)
    kit.spaced(f.img, (S / 2 + sh, y + sh), top, fnt, A.RUST, fnt.size * 0.05)
    kit.spaced(f.img, (S / 2, y), top, fnt, col, fnt.size * 0.05)
    f.note("drawn", "title", top)
    if sub:
        sf = kit.fit_font(f, sub, "semi", 58, S - 420)
        d = f.draw()
        w = kit.spaced_width(d, sub, sf, sf.size * 0.12) + 90
        d.rounded_rectangle([S / 2 - w / 2, y + 40, S / 2 + w / 2, y + 40 + sf.size * 1.7], radius=sf.size * 0.85, fill=A.RUST)
        kit.spaced(f.img, (S / 2, y + 40 + sf.size * 1.22), sub, sf, A.CREAM, sf.size * 0.12)
        f.note("drawn", "sub", sub)

FOOT = "THE KEEPER OF CANDLEHOLM  ·  A COSY LIGHTHOUSE MYSTERY ADVENT CALENDAR"
def footer(f):
    d = f.draw()
    d.rectangle([0, S - 96, S, S], fill=A.CREAM); d.rectangle([0, S - 96, S, S - 88], fill=A.RUST)
    fnt = kit.fit_font(f, FOOT, "display", 40, S - 200 - 4 * len(FOOT))
    kit.spaced(f.img, (S / 2, S - 32), FOOT, fnt, A.NIGHT, 4)
    f.note("drawn", "footer", FOOT)

def badge(f, xy, text, size=56, bg=A.RUST, fg=A.CREAM, angle=0):
    fnt = kit.font("display", size)
    d = f.draw()
    w = d.textlength(text, font=fnt) + size * 1.3; h = size * 1.75
    im = Image.new("RGBA", (int(w), int(h)), (0, 0, 0, 0)); dd = ImageDraw.Draw(im)
    dd.rounded_rectangle([0, 0, w - 1, h - 1], radius=h / 2, fill=bg)
    dd.text((w / 2, h / 2 + size * 0.08), text, font=fnt, fill=fg, anchor="mm")
    f.paste(im, xy[0], xy[1], angle=angle, shadow=True, shadow_strength=70)
    f.note("drawn", "badge", text)

def note_hand(f, xy, text, size=64, col=kit.PENCIL, angle=-4):
    fnt = kit.font("hand", size)
    d = f.draw(); w = d.textlength(text, font=fnt) + 20
    im = Image.new("RGBA", (int(w), int(size * 1.6)), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, size * 0.1), text, font=fnt, fill=col)
    f.paste(im, xy[0], xy[1], angle=angle, shadow=False)
    f.note("drawn", "note", text)

def strike_rows(f, pg, x0, y0, rows, pick, seed=3):
    for k, (yt, yb, xa, xb, t) in enumerate(rows):
        if k in pick:
            px0, py = pg.px(xa, (yt + yb) / 2); px1, _ = pg.px(xb, 0)
            kit.pencil_strike(f, x0 + px0 - 4, y0 + py, x0 + px1 - pg.zoom * 20, (yb - yt) * pg.zoom * 1.3, seed=seed + k)

def tap(f, x, y, r):
    d = f.draw()
    for k, rr in enumerate((r, r * 0.66, r * 0.34)):
        d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=A.RUST + (255 - k * 60,), width=9 - k * 2)
    d.ellipse([x - 20, y - 20, x + 20, y + 20], fill=A.RUST)

# ---------------------------------------------------------------- the ten images (chart style, hero 3)
def m01(A_):
    return H.hero_chart()

def m02(A_):
    f = CS.frame_on(0.48, 0.42, 1.7, 0.3, seed=2)
    CS.cartouche(f, "Open one window a night", kicker="24 DAYS  ·  1 TO 24 DECEMBER", sub="a sealed envelope for every evening of Advent")
    pg = A_.L.image(A_.p["calendar"], 1200)
    cal = A_.L.doc[A_.p["calendar"]]
    tmp = kit.Frame(pg.img.width, pg.img.height); tmp.img = pg.img
    for d in (1, 2, 3):
        r = cal.search_for(f"{d} December")[0]
        px, py = pg.px(r.x0 - 26, r.y0 - 30)
        kit.tick(tmp, px, py, 46, col=A.RUST, width=8)
    pg.img = tmp.img
    f.paste_page(pg, 760, 1150, angle=-3)
    for n, (x, y, a) in zip((1, 2, 3, 24), ((1620, 660, -8), (1660, 920, 7), (1600, 1180, -5), (1650, 1440, 8))):
        f.paste(H.envelope(330, n, (H.CREAM, H.KRAFT, H.SAGE, H.SAGE)[n % 4 if n < 24 else 3], seal=H.OCHRE if n == 24 else H.RUST, holly=n == 24), x, y, angle=a)
        f.note("drawn", "envelope", str(n))
    CS.note(f, (1560, 1660), "one a night!", 72)
    CS.footer(f)
    return f

def m03(A_):
    f = CS.frame_on(0.5, 0.5, 1.0, 0.35, seed=3)
    CS.cartouche(f, "Day 1: the case opens", kicker="WINDOW 1", sub="the keeper’s journal, the tower and the chart of the Sound")
    a = A_.L.image(A_.p["w1"], 1100); b = A_.L.image(A_.p["w1journal"], 1040); c = A_.L.image(A_.p["w1chart"], 1120)
    f.paste_page(a, 470, 1210, angle=-6)
    f.paste_page(b, 1010, 1235, angle=2)
    x0, y0 = 1520, 1180
    f.paste_page(c, x0, y0, angle=5)
    kit.pen_circle(f, x0 - 40, y0 + 120, 95, 70, col=A.RUST, width=8, seed=4)
    CS.note(f, (1420, 1690), "the island!", 66, angle=-8)
    CS.footer(f)
    return f

def m04(A_):
    f = CS.frame_on(0.82, 0.24, 2.0, 0.3, seed=4)
    CS.cartouche(f, "2,400 travellers. One answer.", kicker="WINDOW 2  ·  THE SOUND BOOK", sub="cross them out, night by night")
    a = A_.L.image(A_.p["w2"], 1040)
    f.paste_page(a, 480, 1190, angle=-6)
    b = A_.L.image(A_.log_page, 1260)
    x0, y0 = 1270 - b.img.width / 2, 1150 - b.img.height / 2
    f.paste_page(b, 1270, 1150)
    rows = CL.log_rows(A_.L, A_.log_page)
    rng = random.Random(7)
    pick = {k for k in range(len(rows)) if rng.random() < 0.55}
    strike_rows(f, b, x0, y0, rows, pick, seed=5)
    CS.note(f, (1430, 1730), "2,400 down to 1", 76, angle=-5)
    CS.footer(f)
    return f

def m05(A_):
    f = CS.frame_on(0.17, 0.5, 1.8, 0.3, seed=5)
    CS.cartouche(f, "A new lead every night", kicker="WINDOWS 3 TO 23", sub="a page of the keeper’s journal and the paper pinned to it")
    a = A_.L.image(A_.p["w3"], 1280)
    f.paste_page(a, 700, 1140, angle=-4)
    w4 = A_.L.doc[A_.p["hint1"]].search_for("Window 4")[0]
    clip = (40, 60, 572, w4.y0 - 4)                                   # Window 3's level-1 hint only
    h = A_.L.image(A_.p["hint1"], int(780 * (clip[3] - clip[1]) / (clip[2] - clip[0])), clip=clip)
    f.paste_page(h, 1480, 1560, angle=6)
    CS.legend(f, 1500, 1330, [("3 LEVELS OF HINTS", H.F("sansb", 50), A.RUST, 4)], angle=5)
    CS.legend(f, 1540, 780, [("CHECK-INS", H.F("sansb", 44), CS.NAVY, 4), ("DAYS 6 · 12 · 18", H.F("gloock", 64), A.RUST, 0)], angle=-4)
    CS.footer(f)
    return f

def m06(A_):
    f = CS.frame_on(0.18, 0.88, 2.2, 0.3, seed=6)
    CS.cartouche(f, "Print. Fold. Open.", kicker="PRINT AT HOME", sub="envelope template and day numbers 1–24 included")
    a = A_.L.image(A_.p["envelope"], 1060); b = A_.L.image(A_.p["labels"], 1060)
    f.paste_page(a, 520, 1180, angle=-7); f.paste_page(b, 1080, 1220, angle=3)
    for n, (x, y, ang) in zip((5, 12, 18, 24), ((1650, 650, 10), (1600, 910, -7), (1660, 1170, 5), (1600, 1440, -9))):
        f.paste(H.envelope(320, n, (H.KRAFT, H.CREAM, H.SAGE, H.SAGE)[(5, 12, 18, 24).index(n)], seal=H.OCHRE if n == 24 else H.RUST, holly=n == 24), x, y, angle=ang)
        f.note("drawn", "envelope", str(n))
    CS.footer(f)
    return f

def m07(A_):
    f = CS.frame_on(0.5, 0.62, 1.35, 0.25, seed=7)
    CS.cartouche(f, "Or play it on iPad", kicker="TAP TONIGHT’S WINDOW", sub="GoodNotes, Notability or any PDF app")
    scr = A_.I.image(A_.ip["calendar"], 1240)
    ih = 1240; iw = ih * 0.75
    tab = kit.Frame(int(iw) + 40, ih + 40); tab.img = Image.new("RGBA", tab.img.size, (0, 0, 0, 0))
    kit.ipad(tab, (20, 20, 20 + iw, 20 + ih), scr)
    f.paste(tab.img, S / 2, 1150, angle=-4)
    for kind, src, text in tab.sources:
        f.note(kind, src, text)
    tap(f, 1140, 900, 110)
    CS.legend(f, 1580, 1650, [("EVERY WINDOW LINKS BACK", H.F("sansb", 44), CS.NAVY, 4)], angle=5)
    CS.footer(f)
    return f

def m08(A_):
    f = CS.frame_on(0.5, 0.5, 1.2, 0.45, seed=8)
    CS.cartouche(f, "For two, for four, or as a gift", kicker="1 TO 4 PLAYERS  ·  10–25 MINUTES A NIGHT")
    panels = [("FOR TWO", "A December ritual with your evening tea.", _two),
              ("WITH FAMILY", "Split the Sound Book and race to the answer.", _family),
              ("AS A GIFT", "Instant download: print it tonight, give it tomorrow.", _gift)]
    for k, (title, text, fn) in enumerate(panels):
        cx = 360 + k * 640
        im = fn(540, 720)
        card = CS.box(590, 1120); cd = ImageDraw.Draw(card)
        card.paste(im, (25, 25))
        cd.rectangle([25, 25, 565, 745], outline=CS.NAVY, width=3)
        tfit = H.fit(cd, title, "gloock", 80, 520)
        cd.text((295, 850), title, font=tfit, fill=A.RUST, anchor="ms")
        tf = H.F("sansb", 38); lines = H.wrap(cd, text, tf, 500)
        yy = 930
        for ln in lines:
            cd.text((295, yy), ln, font=tf, fill=CS.NAVY, anchor="ms"); yy += 54
        f.paste(card, cx, 1150, angle=(-3, 2, -2)[k])
        f.note("drawn", "panel", title); f.note("drawn", "panel", text)
    CS.footer(f)
    return f

def m09(A_):
    f = CS.frame_on(0.62, 0.78, 1.6, 0.35, seed=9)
    CS.cartouche(f, "Everything you get", kicker="INSTANT DOWNLOAD", sub="4 files: US Letter, A4, iPad and the solution, sealed apart")
    cards = [("US LETTER", "90 PAGES"), ("A4", "87 PAGES"), ("iPAD", "81 PAGES · LINKED"), ("SOLUTION", "SEPARATE ZIP")]
    for k, (lab, sub) in enumerate(cards):
        cx = 330 + k * 450; cy = 700; ang = (-4, 3, -3, 4)[k]
        c = CS.box(360, 400); cd = ImageDraw.Draw(c)
        if lab != "SOLUTION":
            for r in range(3):
                for q in range(4):
                    x0 = 44 + q * 70; y0 = 44 + r * 62
                    cd.rectangle([x0, y0, x0 + 58, y0 + 50], fill=A.RUST if (r * 4 + q) % 5 == 0 else CS.NAVY)
        else:
            cd.rectangle([110, 50, 250, 230], fill=CS.NAVY)
            cd.text((180, 140), "ZIP", font=H.F("gloock", 70), fill=H.OCHRE_L, anchor="mm")
        cd.text((180, 310), lab, font=H.fit(cd, lab, "gloock", 58, 320), fill=CS.NAVY, anchor="ms")
        cd.text((180, 360), sub, font=H.F("sansb", 26), fill=A.RUST_D, anchor="ms")
        f.paste(c, cx, cy, angle=ang)
        f.note("drawn", "card", f"{lab} {sub}")
    items = ["24 windows, one for every night from 1 to 24 December",
             "The keeper’s journal: one handwritten page a night",
             "The Sound Book: 2,400 travellers to cross out",
             "A sea chart, the tower in section, tide tables, an almanac",
             "Check-ins on Days 6, 12 and 18 so you never get lost",
             "3 levels of hints for every window",
             "The Sealed Check: test your answer without spoilers",
             "Envelope template, day numbers and the solution file"]
    f.paste(CS.box(1640, 840), S / 2, 1355, shadow=True, shadow_strength=55)
    d = f.draw(); y = 1010; fi = H.fit(d, max(items, key=len), "sans", 46, 1400)
    for it in items:
        d.polygon([(250, y - 15), (280, y), (250, y + 15)], fill=A.RUST)
        d.text((310, y), it, font=fi, fill=CS.NAVY, anchor="lm"); f.note("drawn", "item", it)
        y += 94
    CS.footer(f)
    return f

def m10(A_):
    f = CS.frame_on(0.3, 0.74, 1.5, 0.35, seed=10)
    CS.cartouche(f, "Exactly one answer", kicker="FAIR PLAY", sub="every case is checked by code before it reaches you")
    rows = [("1", "culprit among 2,400 travellers"),
            ("21", "nights of evidence, every one needed"),
            ("3", "check-ins so you never get lost"),
            ("3", "levels of hints for every window"),
            ("tick", "tested by computer: one answer"),
            ("0", "spoilers: the answer has its own file")]
    bw, rh = 1560, 186; top = 560
    f.paste(CS.box(bw, rh * len(rows) + 40), S / 2, top + (rh * len(rows) + 40) / 2, shadow=True, shadow_strength=55)
    d = f.draw(); x0 = S / 2 - bw / 2
    for k, (big, txt) in enumerate(rows):
        yc = top + 20 + rh * k + rh / 2
        if k:
            d.line([(x0 + 30, yc - rh / 2), (x0 + bw - 30, yc - rh / 2)], fill=(190, 182, 160), width=2)
        if big == "tick":
            kit.tick(f, x0 + 150, yc + 4, 80, col=A.RUST, width=16); d = f.draw()
        else:
            d.text((x0 + 150, yc + 8), big, font=H.F("gloock", 118), fill=A.RUST, anchor="mm"); f.note("drawn", "big", big)
        d.line([(x0 + 290, yc - rh / 2 + 30), (x0 + 290, yc + rh / 2 - 30)], fill=CS.NAVY, width=3)
        d.text((x0 + 340, yc), txt, font=H.fit(d, txt, "sansb", 58, bw - 400), fill=CS.NAVY, anchor="lm"); f.note("drawn", "row", txt)
    CS.footer(f)
    return f

def _night(w, h, figure=False):
    cv = A.Canvas(w, h, ss=2)
    hz = h * 0.66
    A.sky(cv, SC.NIGHT_SKY, y1=hz + 2, seed=8); A.stars(cv, 160, hz, seed=8)
    A.moon(cv, w * 0.85, h * 0.12, w * 0.03)
    A.sea(cv, hz, h, top=A.NIGHT2, bottom=A.NIGHT, stroke=A.DUSK, seed=8)
    A.island(cv, w * 0.55, hz + h * 0.1, w * 0.9, h * 0.2, col=A.MOSS_D, seed=8)
    A.lighthouse(cv, w * 0.8, hz, h * 0.42, beam_angle=205)
    A.boathouse(cv, w * 0.22, hz + h * 0.04, w * 0.12, h * 0.1, lamp=True)
    if figure:
        A.figure(cv, w * 0.4, hz + h * 0.06, h * 0.2, cap=A.RUST, coat=A.INK, lantern=True)
    A.snow(cv, 160, seed=8)
    return cv.finish(seed=8)


def _two(w, h):
    """Two people at the window seat, seen from behind, the lighthouse beyond."""
    cv = A.Canvas(w, h, ss=2, bg=(232, 214, 180))
    SC._interior(cv, wall=(232, 214, 180), floor=CO.WOOD_H, y=0.9)
    SC._window(cv, w * 0.08, h * 0.12, w * 0.92, h * 0.6, inside=CO.view_dusk)
    CO.fairy_lights(cv, [(0, h * 0.08), (w * 0.3, h * 0.11), (w * 0.6, h * 0.085), (w, h * 0.105)], 8, seed=3)
    cv.rect((0, h * 0.6, w, h * 0.64), A.WOOD_L)
    CO.knit(cv, (0, h * 0.64, w, h * 0.9), a=A.RUST, b=A.CREAM, cell=16)
    A.figure(cv, w * 0.34, h * 0.86, h * 0.44, cap=A.RUST, coat=A.SEA2, bobble=True)
    A.figure(cv, w * 0.64, h * 0.86, h * 0.4, cap=None, coat=A.MOSS, scarf=A.OCHRE, bobble=False)
    A.cup(cv, w * 0.12, h * 0.6, h * 0.06)
    CO.candle(cv, w * 0.88, h * 0.6, h * 0.06)
    return cv.finish(seed=21)


def _family(w, h):
    cv = A.Canvas(w, h, ss=2)
    SC._interior(cv, wall=(232, 214, 180), floor=CO.WOOD_H, y=0.72)
    CO.fairy_lights(cv, [(0, h * 0.08), (w * 0.3, h * 0.11), (w * 0.6, h * 0.085), (w, h * 0.105)], 8, seed=5)
    A.stove(cv, w * 0.15, h * 0.72, h * 0.22)
    A.table(cv, w * 0.05, w * 0.95, h * 0.82)
    for k, (x, hh, capc) in enumerate(((0.32, 0.42, A.RUST), (0.56, 0.34, None), (0.8, 0.4, A.OCHRE))):
        A.figure(cv, w * x, h * 0.82, h * hh, cap=capc, coat=[A.SEA, A.MOSS_D, A.RUST_D][k], bobble=capc is not None)
    CO.cat_sitting(cv, w * 0.12, h * 0.98, h * 0.1)
    return cv.finish(seed=22)


def _gift(w, h):
    cv = A.Canvas(w, h, ss=2, bg=(232, 214, 180))
    SC._interior(cv, wall=(232, 214, 180), floor=CO.WOOD_H, y=0.86)
    CO.fairy_lights(cv, [(0, h * 0.08), (w * 0.3, h * 0.11), (w * 0.6, h * 0.085), (w, h * 0.105)], 8, seed=7)
    cv.glow(w * 0.5, h * 0.55, w * 0.4, A.LAMP, alpha=60)
    A.parcel(cv, w * 0.2, h * 0.86, w * 0.6, h * 0.38, paper=(214, 182, 140), string=A.RUST, label=True)
    CO.pine(cv, w * 0.1, h * 0.46, w * 0.5, h * 0.42, s=1.0, seed=8)
    A.holly(cv, w * 0.5, h * 0.44, 40)
    A.cat(cv, w * 0.86, h * 0.86, h * 0.06)
    return cv.finish(seed=23)


BUILDERS = [m01, m02, m03, m04, m05, m06, m07, m08, m09, m10]

def build(outdir):
    os.makedirs(outdir, exist_ok=True)
    for fn in os.listdir(outdir):
        if fn.endswith(".jpg"):
            os.remove(os.path.join(outdir, fn))
    A_ = Assets(); res = []
    for name, fn in zip(NAMES, BUILDERS):
        f = fn(A_)
        path = os.path.join(outdir, f"{CL.SLUG}_{name}.jpg")
        f.img.convert("RGB").save(path, quality=88, optimize=True)
        res.append(dict(name=name, path=path, sources=f.sources, hits=kit.spoiler_scan(f.sources, A_.bad)))
        print(name, "ok", len(res[-1]["hits"]), "hits", flush=True)
    sheet = Image.new("RGB", (5 * 400, 2 * 400))
    for k, r in enumerate(res):
        sheet.paste(Image.open(r["path"]).resize((400, 400)), ((k % 5) * 400, (k // 5) * 400))
    sp = os.path.join(outdir, f"{CL.SLUG}_overview.jpg"); sheet.save(sp, quality=85)
    return res, sp, A_

if __name__ == "__main__":
    import sys
    out = os.path.join(CL.CASE, "listing", "mockups")
    if len(sys.argv) > 1:
        os.makedirs(out, exist_ok=True); A_ = Assets()
        for k in map(int, sys.argv[1:]):
            f = BUILDERS[k - 1](A_)
            p = os.path.join(out, f"{CL.SLUG}_{NAMES[k - 1]}.jpg"); f.img.convert("RGB").save(p, quality=88)
            print(NAMES[k - 1], kit.spoiler_scan(f.sources, A_.bad))
    else:
        res, sp, A_ = build(out)
