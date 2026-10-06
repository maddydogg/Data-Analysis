"""Ten listing images: 2000 x 2000 JPG, in the calendar's own cosy vintage illustration.

01 is the cover; then the calendar; Days 1, 2 and 3; print and fold; iPad; who it's for; what's inside;
checked by code. Each image has its own illustrated background scene (a tea table, the keeper's kitchen,
the Sound at dusk, the tally office, the boathouse at night...), poster headlines in Josefin capitals
with a rust offset print, and the pages shown as they look in play: pencil strikes in the Sound Book,
a ring round the island on the chart, ticks on the calendar.

Only Windows 1-3 and the set-up pages are shown. Every string drawn and the text layer of every PDF
region pasted is recorded on the kit.Frame, so the spoiler check reads exactly what a buyer can read.
"""
import math, os, random
from PIL import Image, ImageDraw, ImageFilter
import kit
import cal_listing as CL
from cal_listing import art as A, scenes as SC, COVER

S = 2000
NAMES = ["01-main", "02-the-calendar", "03-day-1-the-case", "04-day-2-the-sound-book", "05-day-3-first-lead",
         "06-print-and-fold", "07-ipad-calendar", "08-who-its-for", "09-whats-inside", "10-checked-by-code"]

class Assets:
    def __init__(self):
        self.bad = CL.forbidden()
        self.L, self.I, self.p, self.ip = CL.pages()
        clean = CL.clean_log_pages(self.L, self.bad)
        self.log_page = clean[len(clean) // 3]

# ---------------------------------------------------------------- illustrated backgrounds
def bg_table(seed=1, wood=(150, 108, 72)):
    """A wooden table seen from above in lamplight: a cup of tea, holly, a pencil, a few tallies."""
    cv = A.Canvas(S // 2, S // 2, ss=2, bg=wood)
    W = H = S // 2
    for k in range(9):                                     # planks
        y = k * H / 9
        cv.rect((0, y, W, y + 3), A.shade(wood, 0.82))
        rng = random.Random(seed + k)
        for _ in range(6):
            x = rng.uniform(0, W); cv.line([(x, y + 12), (x + rng.uniform(40, 120), y + 14 + rng.uniform(-3, 3))], A.shade(wood, 0.9), w=1.2)
    cv.glow(W * 0.5, H * 0.45, W * 0.55, (255, 220, 160), alpha=70)
    rng = random.Random(seed)
    corners = [(0.07, 0.36), (0.93, 0.32), (0.07, 0.9), (0.93, 0.88)]
    for k, (cx, cy) in enumerate(corners):
        kind = (k + seed) % 4
        if kind == 0:
            cv.ellipse((W * cx - 52, H * cy - 52, W * cx + 52, H * cy + 52), A.WHITE)
            cv.ellipse((W * cx - 40, H * cy - 40, W * cx + 40, H * cy + 40), (150, 100, 60))
            cv.ellipse((W * cx + 40, H * cy - 12, W * cx + 70, H * cy + 12), A.WHITE)
        elif kind == 1:
            A.holly(cv, W * cx, H * cy, 50)
        elif kind == 2:
            cv.line([(W * cx - 70, H * cy + 20), (W * cx + 60, H * cy - 30)], A.OCHRE, w=10)
            cv.line([(W * cx + 60, H * cy - 30), (W * cx + 76, H * cy - 36)], A.INK, w=5)
        else:
            for q in range(3):
                A.tally(cv, W * cx + q * 34 - 34, H * cy + (q % 2) * 22, 20, metal=[A.BRASS, A.COPPER, A.TIN][q])
    im = cv.finish(seed=seed).resize((S, S), Image.LANCZOS)
    return im

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

FOOT = "THE KEEPER OF CANDLEHOLM  ·  LIGHTHOUSE MURDER MYSTERY ADVENT CALENDAR"
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

# ---------------------------------------------------------------- the ten images
def m01(A_):
    f = kit.Frame(S, S); rec = []
    f.img = COVER.cover(S, S, badges=True, record=rec.append).convert("RGBA")
    for t in rec:
        f.note("drawn", "cover", t)
    return f

def m02(A_):
    f = frame_from(bg_table(2))
    headline(f, "24 WINDOWS. 24 DAYS.", "OPEN ONE EACH DAY FROM 1 TO 24 DECEMBER", y=210, on_dark=True)
    pg = A_.L.image(A_.p["calendar"], 1280)
    # tick the first three windows in pencil, as in play (drawn onto the page before it is placed)
    cal = A_.L.doc[A_.p["calendar"]]
    tmp = kit.Frame(pg.img.width, pg.img.height); tmp.img = pg.img
    for d in (1, 2, 3):
        r = cal.search_for(f"{d} December")[0]
        px, py = pg.px(r.x0 - 26, r.y0 - 30)
        kit.tick(tmp, px, py, 46, col=A.RUST, width=8)
    pg.img = tmp.img
    f.paste_page(pg, 760, 1140, angle=-3)
    for n, (x, y, a) in zip((1, 2, 3, 24), ((1590, 720, -10), (1640, 1010, 8), (1560, 1290, -6), (1630, 1580, 10))):
        f.paste(kit.envelope(430, n), x, y, angle=a)
        f.note("drawn", "envelope", str(n))
    note_hand(f, (1560, 470), "one a day!", 70, col=A.CREAM, angle=-6)
    footer(f)
    return f

def m03(A_):
    f = frame_from(bg_scene(lambda w, h: SC.keyart(w, h, seed=31, figure=False, hz_frac=0.55, tower=0.3, moon_xy=(0.12, 0.12)), dim=0.15))
    headline(f, "DAY 1: THE CASE", "THE KEEPER’S JOURNAL · THE TOWER · THE CHART OF THE SOUND", y=200)
    a = A_.L.image(A_.p["w1"], 1120); b = A_.L.image(A_.p["w1journal"], 1060); c = A_.L.image(A_.p["w1chart"], 1150)
    f.paste_page(a, 470, 1180, angle=-6)
    f.paste_page(b, 1010, 1210, angle=2)
    x0, y0 = 1520, 1150
    f.paste_page(c, x0, y0, angle=5)
    # a red pencil ring round the island on the chart (drawn on top, roughly where the island sits)
    kit.pen_circle(f, x0 - 40, y0 + 120, 95, 70, col=A.RUST, width=8, seed=4)
    note_hand(f, (1420, 1640), "the island!", 66, col=A.RUST, angle=-8)
    footer(f)
    return f

def m04(A_):
    f = frame_from(bg_scene(_office))
    headline(f, "DAY 2: 2,400 TRAVELLERS", "THE SOUND BOOK · CROSS THEM OUT, DAY BY DAY", y=200, on_dark=False)
    a = A_.L.image(A_.p["w2"], 1060)
    f.paste_page(a, 480, 1170, angle=-6)
    b = A_.L.image(A_.log_page, 1420)
    x0, y0 = 1270 - b.img.width / 2, 1130 - b.img.height / 2
    f.paste_page(b, 1270, 1130)
    rows = CL.log_rows(A_.L, A_.log_page)
    rng = random.Random(7)
    pick = {k for k in range(len(rows)) if rng.random() < 0.55}
    strike_rows(f, b, x0, y0, rows, pick, seed=5)
    note_hand(f, (1420, 1770), "2,400 down to 1", 76, col=A.RUST, angle=-5)
    footer(f)
    return f

def _office(w, h):
    cv = A.Canvas(w, h, ss=2)
    SC._interior(cv, wall=(222, 206, 176), floor=(150, 112, 80), y=0.86)
    SC._board(cv, w * 0.04, h * 0.22, w * 0.3, h * 0.62, n_rows=5, n_cols=5, metal=None, seed=3)
    SC._board(cv, w * 0.7, h * 0.22, w * 0.96, h * 0.62, n_rows=5, n_cols=5, metal=None, seed=9)
    SC._window(cv, w * 0.36, h * 0.24, w * 0.64, h * 0.5, inside=SC._harbour_view)
    return cv.finish(seed=5)

def m05(A_):
    f = frame_from(bg_scene(lambda w, h: _night(w, h), dim=0.0))
    headline(f, "DAYS 3–23: A NEW LEAD EACH DAY", "A PAGE OF THE JOURNAL + THE PAPER PINNED TO IT", y=200)
    a = A_.L.image(A_.p["w3"], 1500)
    f.paste_page(a, 720, 1150, angle=-4)
    w4 = A_.L.doc[A_.p["hint1"]].search_for("Window 4")[0]
    clip = (40, 60, 572, w4.y0 - 4)                                   # Window 3's level-1 hint only
    h = A_.L.image(A_.p["hint1"], int(860 * (clip[3] - clip[1]) / (clip[2] - clip[0])), clip=clip)
    f.paste_page(h, 1500, 1500, angle=6)
    badge(f, (1500, 1270), "3 LEVELS OF HINTS", 62, angle=5)
    badge(f, (1530, 720), "CHECK-INS ON DAYS 6, 12, 18", 44, bg=A.CREAM, fg=A.NIGHT, angle=-4)
    footer(f)
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

def m06(A_):
    f = frame_from(bg_table(6, wood=(132, 94, 62)))
    headline(f, "PRINT. FOLD. OPEN.", "ENVELOPE TEMPLATE + DAY NUMBERS 1–24 INCLUDED", y=200)
    a = A_.L.image(A_.p["envelope"], 1100); b = A_.L.image(A_.p["labels"], 1100)
    f.paste_page(a, 520, 1140, angle=-7); f.paste_page(b, 1080, 1190, angle=3)
    for n, (x, y, ang) in zip((5, 12, 18, 24), ((1660, 650, 12), (1600, 950, -8), (1680, 1250, 6), (1600, 1560, -10))):
        f.paste(kit.envelope(400, n), x, y, angle=ang); f.note("drawn", "envelope", str(n))
    footer(f)
    return f

def m07(A_):
    f = frame_from(bg_scene(lambda w, h: _window_seat(w, h)))
    headline(f, "ON iPAD: TAP TODAY’S WINDOW", "GOODNOTES · NOTABILITY · ANY PDF APP", y=200)
    scr = A_.I.image(A_.ip["calendar"], 1300)
    ih = 1300; iw = ih * 0.75
    tab = kit.Frame(int(iw) + 40, ih + 40); tab.img = Image.new("RGBA", tab.img.size, (0, 0, 0, 0))
    kit.ipad(tab, (20, 20, 20 + iw, 20 + ih), scr)
    f.paste(tab.img, S / 2, 1140, angle=-4)
    for kind, src, text in tab.sources:
        f.note(kind, src, text)
    tap(f, 1140, 900, 110)
    badge(f, (1560, 1640), "EVERY WINDOW LINKS BACK", 50, angle=6)
    footer(f)
    return f

def _window_seat(w, h):
    cv = A.Canvas(w, h, ss=2)
    SC._interior(cv, wall=(214, 196, 166), y=0.8)
    SC._window(cv, w * 0.12, h * 0.16, w * 0.88, h * 0.7, inside=lambda sub: _view(sub))
    cv.rect((0, h * 0.7, w, h * 0.8), A.WOOD_L)
    A.cup(cv, w * 0.84, h * 0.79, h * 0.08)
    A.cat(cv, w * 0.18, h * 0.79, h * 0.07)
    return cv.finish(seed=12)

def _view(sub):
    hz = sub.H * 0.62
    A.sky(sub, SC.DUSK_SKY, y1=hz + 2, seed=12)
    SC.mainland(sub, hz, seed=12)
    A.sea(sub, hz, sub.H, top=A.SEA3, bottom=A.SEA, seed=12)
    A.island(sub, sub.W * 0.7, hz + sub.H * 0.1, sub.W * 0.3, sub.H * 0.16, seed=12)
    A.lighthouse(sub, sub.W * 0.68, hz + sub.H * 0.01, sub.H * 0.45, beam_angle=200)
    A.snow(sub, 120, seed=12)

def m08(A_):
    f = frame_from(bg_table(8, wood=(120, 86, 58)))
    headline(f, "WHO IT’S FOR", "ONE DETECTIVE OR UP TO FOUR · 10–25 MINUTES A DAY", y=200)
    panels = [("FOR TWO", "A December ritual: one window with the evening tea.", _two),
              ("FOR THE FAMILY", "Teens and grown-ups split the Sound Book and race to the answer.", _family),
              ("AS A GIFT", "Instant download: a last-minute present for any mystery lover.", _gift)]
    for k, (title, text, fn) in enumerate(panels):
        cx = 360 + k * 640
        im = fn(560, 760)
        card = Image.new("RGBA", (600, 1180), A.CREAM + (255,)); cd = ImageDraw.Draw(card)
        cd.rectangle([0, 0, 599, 1179], outline=A.NIGHT, width=6)
        card.paste(im, (20, 20))
        tfit = kit.font("display", 74)
        while cd.textlength(title, font=tfit) > 540:
            tfit = kit.font("display", tfit.size - 4)
        cd.text((300, 880), title, font=tfit, fill=A.RUST, anchor="mm")
        tf = kit.font("bold", 40); words = text.split(); lines = [""]
        for wd in words:
            if cd.textlength(lines[-1] + " " + wd, font=tf) > 520:
                lines.append(wd)
            else:
                lines[-1] = (lines[-1] + " " + wd).strip()
        yy = 960
        for ln in lines:
            cd.text((300, yy), ln, font=tf, fill=A.NIGHT, anchor="mm"); yy += 56
        f.paste(card, cx, 1180, angle=(-3, 2, -2)[k])
        f.note("drawn", "panel", title); f.note("drawn", "panel", text)
    footer(f)
    return f

def _two(w, h):
    cv = A.Canvas(w, h, ss=2)
    hz = h * 0.55
    A.sky(cv, SC.DUSK_SKY, y1=hz + 2, seed=21); A.sea(cv, hz, h, top=A.SEA3, bottom=A.SEA, seed=21)
    A.island(cv, w * 0.72, hz + h * 0.06, w * 0.4, h * 0.1, seed=21); A.lighthouse(cv, w * 0.72, hz, h * 0.3, beam_angle=200)
    A.jetty(cv, -10, w * 0.7, h * 0.86)
    A.figure(cv, w * 0.3, h * 0.84, h * 0.36, cap=A.RUST, coat=A.NIGHT2)
    A.figure(cv, w * 0.52, h * 0.84, h * 0.34, cap=A.MOSS, coat=A.SEA, bobble=False)
    A.snow(cv, 80, seed=21)
    return cv.finish(seed=21)

def _family(w, h):
    cv = A.Canvas(w, h, ss=2)
    SC._interior(cv, wall=(222, 206, 176), y=0.72)
    A.stove(cv, w * 0.18, h * 0.72, h * 0.22)
    A.table(cv, w * 0.05, w * 0.95, h * 0.82)
    for k, (x, hh, capc) in enumerate(((0.3, 0.42, A.RUST), (0.55, 0.34, None), (0.78, 0.4, A.OCHRE))):
        A.figure(cv, w * x, h * 0.82, h * hh, cap=capc, coat=[A.SEA, A.MOSS_D, A.NIGHT2][k], bobble=capc is not None)
    return cv.finish(seed=22)

def _gift(w, h):
    cv = A.Canvas(w, h, ss=2)
    A.sky(cv, [A.NIGHT, A.NIGHT2, A.DUSK], seed=23)
    cv.glow(w * 0.5, h * 0.55, w * 0.4, A.LAMP, alpha=80)
    A.parcel(cv, w * 0.22, h * 0.82, w * 0.56, h * 0.42, paper=A.CREAM, string=A.RUST, label=True)
    A.holly(cv, w * 0.5, h * 0.4, 46)
    A.snow(cv, 120, seed=23)
    return cv.finish(seed=23)

def m09(A_):
    f = frame_from(bg_scene(lambda w, h: SC.keyart(w, h, seed=41, figure=False, hz_frac=0.72, tower=0.22, moon_xy=None), dim=0.35))
    headline(f, "WHAT’S INSIDE", "4 FILES · INSTANT DOWNLOAD", y=200)
    cards = [("US LETTER", "90 PAGES"), ("A4", "87 PAGES"), ("iPAD", "81 PAGES · LINKED"), ("SOLUTION", "SEPARATE ZIP")]
    d = f.draw()
    for k, (lab, sub) in enumerate(cards):
        cx = 300 + k * 470; cy = 640; ang = (-5, 3, -3, 5)[k]
        c = Image.new("RGBA", (380, 470), (0, 0, 0, 0)); cd = ImageDraw.Draw(c)
        cd.rounded_rectangle([0, 0, 379, 469], radius=20, fill=A.CREAM, outline=A.NIGHT, width=7)
        if lab != "SOLUTION":
            for r in range(4):
                for q in range(4):
                    x0 = 46 + q * 75; y0 = 50 + r * 62
                    cd.rounded_rectangle([x0, y0, x0 + 62, y0 + 50], radius=6, fill=A.RUST if (r * 4 + q) % 5 == 0 else A.NIGHT)
        else:
            cd.rounded_rectangle([90, 70, 290, 290], radius=20, fill=A.NIGHT)
            cd.text((190, 180), "ZIP", font=kit.font("display", 100), fill=A.OCHRE, anchor="mm")
        cd.text((190, 350), lab, font=kit.font("display", 64), fill=A.NIGHT, anchor="mm")
        cd.text((190, 415), sub, font=kit.font("bold", 28), fill=A.RUST_D, anchor="mm")
        f.paste(c, cx, cy, angle=ang)
        f.note("drawn", "card", f"{lab} {sub}")
    items = ["24 windows, one for every day from 1 to 24 December",
             "The keeper’s journal: one handwritten page a day",
             "The Sound Book: 2,400 travellers to cross out",
             "A sea chart, the tower in section, tide tables, an almanac",
             "Check-ins on Days 6, 12 and 18 so you never get lost",
             "3 levels of hints for every window",
             "The Sealed Check: test your answer without spoilers",
             "Envelope template, day numbers and the solution file"]
    y = 1000
    for it in items:
        d.polygon([(190, y - 18), (226, y), (190, y + 18)], fill=A.OCHRE)
        d.text((260, y), it, font=kit.font("bold", 52), fill=A.CREAM, anchor="lm"); f.note("drawn", "item", it)
        y += 104
    footer(f)
    return f

def m10(A_):
    f = frame_from(bg_scene(_sunset, dim=0.25))
    headline(f, "EXACTLY ONE ANSWER.", None, y=200)
    kit.spaced(f.img, (S / 2, 380), "CHECKED BY CODE.", kit.font("display", 130), A.OCHRE_L, 6); f.note("drawn", "title", "CHECKED BY CODE.")
    combos = 1
    for c in CL.C.CLUES:
        combos *= 1 + len(c["alts"])
    rows = [("1", "killer among 2,400 travellers, and only one"),
            ("21", "days of evidence, every one of them needed"),
            (f"{combos:,}", "combinations of readings tested: same answer"),
            ("tick", "chart, tide and time words read every reasonable way"),
            ("3", "check-ins so you can catch a slip early"),
            ("0", "spoilers on the pages you open early")]
    y = 600
    for k, (big, txt) in enumerate(rows):
        bar = Image.new("RGBA", (S - 300, 160), (0, 0, 0, 0)); bd = ImageDraw.Draw(bar)
        bd.rounded_rectangle([0, 0, S - 301, 159], radius=18, fill=A.CREAM + (245,), outline=A.NIGHT, width=5)
        bd.rounded_rectangle([0, 0, 320, 159], radius=18, fill=A.RUST)
        f.paste(bar, S / 2, y, angle=0, shadow=True)
        d = f.draw()
        if big == "tick":
            kit.tick(f, 245, y + 5, 90, col=A.CREAM, width=18); d = f.draw()
        else:
            fb = kit.fit_font(f, big, "display", 120, 270)
            d.text((310, y + 6), big, font=fb, fill=A.CREAM, anchor="mm"); f.note("drawn", "big", big)
        tf = kit.fit_font(f, txt, "bold", 52, S - 820)
        d.text((520, y), txt, font=tf, fill=A.NIGHT, anchor="lm"); f.note("drawn", "row", txt)
        y += 200
    footer(f)
    return f

def _sunset(w, h):
    cv = A.Canvas(w, h, ss=2)
    hz = h * 0.7
    A.sky(cv, [A.NIGHT, A.DUSK, (186, 168, 150), A.PEACH, (242, 196, 136)], y1=hz + 2, seed=16)
    A.sea(cv, hz, h, top=A.SEA3, bottom=A.SEA2, stroke=A.PEACH, seed=16)
    A.island(cv, w * 0.8, hz + h * 0.06, w * 0.3, h * 0.1, seed=16)
    A.lighthouse(cv, w * 0.8, hz, h * 0.3, beam_angle=200)
    return cv.finish(seed=16)

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
