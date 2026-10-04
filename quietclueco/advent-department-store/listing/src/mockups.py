"""Ten listing images (2000 x 2000 JPG) in the anime-noir look of the calendar.

01 is the cover. 02-10 put real pages of the calendar (Windows 1-3 and the set-up pages only) on a
snowy night background. Every image is built on a kit.Frame, which records every string drawn and
the text layer of every PDF region pasted, so the spoiler check reads exactly what a buyer can read.
"""
import math, os, random
from PIL import Image, ImageDraw, ImageFilter
import kit
import cal_listing as CL
from cal_listing import art, COVER

S = 2000
NAMES = ["01-main", "02-the-calendar", "03-day-1-the-case", "04-day-2-the-register", "05-day-3-first-clue",
         "06-print-and-fold", "07-ipad-calendar", "08-who-its-for", "09-whats-inside", "10-checked-by-code"]

class Assets:
    def __init__(self):
        self.bad = CL.forbidden()
        self.L, self.I, self.p, self.ip = CL.pages()
        clean = CL.clean_log_pages(self.L, self.bad)
        self.log_page = clean[len(clean) // 3]

def night_bg(seed=1, glow=(0.5, 0.42)):
    f = kit.Frame(S, S, kit.NIGHT0)
    d = ImageDraw.Draw(f.img)
    for y in range(S):
        t = y / S
        d.line([(0, y), (S, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip(kit.NIGHT0, kit.NIGHT1)) + (255,))
    g = Image.new("RGBA", f.img.size, (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse([S * (glow[0] - 0.36), S * (glow[1] - 0.3), S * (glow[0] + 0.36), S * (glow[1] + 0.3)],
                              fill=kit.AMBER + (46,))
    f.img.alpha_composite(g.filter(ImageFilter.GaussianBlur(S * 0.09)))
    snow_layer(f, 260, seed)
    return f

def snow_layer(f, n, seed, alpha=(40, 150)):
    rng = random.Random(seed); L = Image.new("RGBA", f.img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    for i in range(n):
        x, y, r = rng.uniform(0, f.w), rng.uniform(0, f.h), rng.uniform(1.5, 4.5)
        d.ellipse([x - r, y - r, x + r, y + r], fill=kit.SNOW + (rng.randint(*alpha),))
    f.img.alpha_composite(L)

def headline(f, top, sub=None, y=150):
    d = f.draw()
    fnt = kit.fit_font(f, top, "display", 150, S - 220)
    d.text((S / 2, y), top, font=fnt, fill=kit.SNOW, anchor="mm"); f.note("drawn", "headline", top)
    if sub:
        sf = kit.fit_font(f, sub, "body", 56, S - 260)
        d.text((S / 2, y + 112), sub, font=sf, fill=kit.AMBER, anchor="mm"); f.note("drawn", "sub", sub)

def footer(f):
    d = f.draw()
    d.rectangle([0, S - 110, S, S], fill=kit.NIGHT0 + (235,))
    d.line([(0, S - 110), (S, S - 110)], fill=kit.AMBER, width=4)
    t = "THE WINDOWS AT QUILLON’S  ·  A CHRISTMAS EVE MURDER MYSTERY ADVENT CALENDAR"
    d.text((S / 2, S - 55), t, font=kit.font("body", 40), fill=kit.FROST, anchor="mm"); f.note("drawn", "footer", t)

def page(A, pdf, idx, height, clip=None):
    return pdf.image(idx, height, clip=clip)

def strike_rows(f, A, pg, x0, y0, rows, pick, seed=3):
    """Felt-tip strikes through some register rows of a pasted page (pg pasted with top-left at x0, y0)."""
    for k, (yt, yb, xa, xb, t) in enumerate(rows):
        if k in pick:
            px0, py = pg.px(xa, (yt + yb) / 2); px1, _ = pg.px(xb, 0)
            kit.marker_strike(f, x0 + px0 - 6, y0 + py, x0 + px1 + 6, (yb - yt) * pg.zoom * 1.4, col=kit.AMBER_D,
                              alpha=150, seed=seed + k)

def m01(A):
    f = kit.Frame(S, S, kit.NIGHT0)
    rec = []
    im = COVER.cover(S, S, badges=True, record=rec.append)
    f.img = im.convert("RGBA")
    for t in rec:
        f.note("drawn", "cover", t)
    return f

def m02(A):
    f = night_bg(2)
    headline(f, "24 WINDOWS. ONE A DAY.", "OPEN ONE WINDOW EACH DAY FROM 1 TO 24 DECEMBER")
    pg = page(A, A.L, A.p["calendar"], 1300)
    f.paste_page(pg, 760, 1080, angle=3)
    # a stack of numbered envelopes on the right
    for k, n in enumerate((5, 4, 3, 2, 1)):
        x = 1560 + (k % 2) * 30; y = 700 + k * 230
        kit.envelope(f, (x - 230, y - 120, x + 230, y + 120), n, kit.font("display", 96), col=kit.SNOW, seal=kit.NIGHT1)
    footer(f)
    return f

def m03(A):
    f = night_bg(3)
    headline(f, "DAY 1: THE CASE", "A LETTER, A STORE PLAN AND A MURDER ON CHRISTMAS EVE")
    a = page(A, A.L, A.p["w1"], 1250); b = page(A, A.L, A.p["w1letter"], 1180)
    f.paste_page(a, 640, 1080, angle=-3); f.paste_page(b, 1380, 1110, angle=4)
    footer(f)
    return f

def m04(A):
    f = night_bg(4)
    headline(f, "DAY 2: THE LANTERN REGISTER", "2,400 SHOPPERS · CROSS THEM OUT, WINDOW BY WINDOW")
    a = page(A, A.L, A.p["w2"], 1150)
    f.paste_page(a, 560, 1110, angle=-4)
    b = page(A, A.L, A.log_page, 1300)
    x0, y0 = 1360 - b.img.width / 2, 1080 - b.img.height / 2
    f.paste_page(b, 1360, 1080)
    rows = CL.log_rows(A.L, A.log_page)
    strike_rows(f, A, b, x0, y0, rows, set(range(2, len(rows), 3)) | {5, 9, 17})
    footer(f)
    return f

def m05(A):
    f = night_bg(5)
    headline(f, "DAYS 3–23: A NEW CLUE EACH DAY", "STATEMENTS, PLANS, MAPS AND RECEIPTS — WORK OUT WHAT EACH ONE MEANS")
    a = page(A, A.L, A.p["w3"], 1500)
    f.paste_page(a, 760, 1090, angle=-2)
    w4 = A.L.doc[A.p["hint1"]].search_for("Window 4")[0]
    clip = (40, 60, 572, w4.y0 - 4)                                        # Window 3's level-1 hint only
    h = page(A, A.L, A.p["hint1"], int(860 * (clip[3] - clip[1]) / (clip[2] - clip[0])), clip=clip)
    f.paste_page(h, 1450, 1560, angle=4)
    d = f.draw()
    kit.pill(f, (1540, 1330), "3 LEVELS OF HINTS", kit.font("display", 70), kit.AMBER, kit.NIGHT0)
    footer(f)
    return f

def m06(A):
    f = night_bg(6)
    headline(f, "PRINT · FOLD · NUMBER", "AN ENVELOPE TEMPLATE AND DAY NUMBERS 1–24 ARE INCLUDED")
    a = page(A, A.L, A.p["envelope"], 1150); b = page(A, A.L, A.p["labels"], 1150)
    f.paste_page(a, 560, 1050, angle=-4); f.paste_page(b, 1180, 1100, angle=3)
    for k, n in enumerate((24, 12, 7)):
        x = 1720; y = 760 + k * 300
        kit.envelope(f, (x - 200, y - 110, x + 200, y + 110), n, kit.font("display", 90), col=kit.SNOW, seal=kit.NIGHT1)
    footer(f)
    return f

def m07(A):
    f = night_bg(7, glow=(0.5, 0.55))
    headline(f, "ON iPAD: TAP TODAY’S WINDOW", "GOODNOTES · NOTABILITY · ANY PDF APP")
    scr = page(A, A.I, A.ip["calendar"], 1300)
    ih = 1400; iw = ih * 0.75
    kit.ipad(f, (S / 2 - iw / 2, 330, S / 2 + iw / 2, 330 + ih), scr)
    footer(f)
    return f

def person(f, x, base, h, hat=True):
    cv = art.Canvas(int(h * 0.7), int(h * 1.15), ss=2)
    cv.img = Image.new("RGBA", cv.img.size, (0, 0, 0, 0)); cv.d = ImageDraw.Draw(cv.img)
    art.figure(cv, h * 0.35, h * 1.1, h, hat=hat, shadow=None, col=kit.NIGHT0)
    im = cv.img.resize((cv.W, cv.H), Image.LANCZOS)
    f.img.alpha_composite(im, (int(x - im.width / 2), int(base - im.height)))

def m08(A):
    f = night_bg(8)
    headline(f, "WHO IT’S FOR", "ONE DETECTIVE OR UP TO FOUR · 10–25 MINUTES A DAY")
    d = f.draw()
    panels = [("FOR TWO", "A cosy December ritual for couples: one window with the evening tea.", [(-60, True), (60, False)]),
              ("FOR THE FAMILY", "Teens and grown-ups split the register and compare notes.", [(-110, False), (0, True), (110, False)]),
              ("AS A GIFT", "Instant download: a last-minute present for any mystery lover.", [])]
    for k, (title, text, figs) in enumerate(panels):
        cx = 360 + k * 640; top = 420
        d.rounded_rectangle([cx - 290, top, cx + 290, top + 1300], radius=40, fill=kit.NIGHT1 + (230,), outline=kit.STEEL, width=3)
        box = (cx - 220, top + 70, cx + 220, top + 700)
        sub = art.Canvas(440, 630, ss=1)
        art.sky(sub); art.shop_window(sub, (60, 120, 380, 470), panes=(1, 1)); art.ground(sub, 520)
        if figs:
            for dx, hat in figs:
                art.figure(sub, 220 + dx, 640, 330, hat=hat, shadow=None)
        else:
            sub.d.rectangle(sub.S(160, 260, 280, 380), fill=art.INK)
            sub.d.rectangle(sub.S(212, 260, 228, 380), fill=art.AMBER_L); sub.d.rectangle(sub.S(160, 312, 280, 328), fill=art.AMBER_L)
        art.snow(sub, 160, seed=k)
        f.img.alpha_composite(sub.finish(grain=8, vignette=0.3).convert("RGBA"), (box[0], box[1]))
        d = f.draw()
        d.text((cx, top + 800), title, font=kit.font("display", 110), fill=kit.AMBER, anchor="mm"); f.note("drawn", "t", title)
        tf = kit.font("body", 46)
        words = text.split(); lines = [""]
        for w in words:
            if d.textlength(lines[-1] + " " + w, font=tf) > 500:
                lines.append(w)
            else:
                lines[-1] = (lines[-1] + " " + w).strip()
        for i, ln in enumerate(lines):
            d.text((cx, top + 920 + i * 66), ln, font=tf, fill=kit.SNOW, anchor="mm")
        f.note("drawn", "t", text)
    footer(f)
    return f

def m09(A):
    f = night_bg(9)
    headline(f, "WHAT’S INSIDE", "4 FILES · INSTANT DOWNLOAD")
    cards = [("US LETTER", A.L, A.p["cover"]), ("A4", A.L, A.p["cover"]), ("iPAD", A.I, 0), ("SOLUTION ZIP", None, None)]
    for k, (lab, pdf, idx) in enumerate(cards):
        x0 = 140 + k * 450; box = (x0, 330, x0 + 380, 830)
        th = pdf.image(idx, 420) if pdf else None
        kit.pdf_file_card(f, box, th, lab, kit.font("display", 56))
        if not pdf:
            d = f.draw(); cx = x0 + 190
            d.rounded_rectangle([cx - 110, 450, cx + 110, 680], radius=20, fill=kit.NIGHT1)
            d.text((cx, 565), "ZIP", font=kit.font("display", 110), fill=kit.AMBER, anchor="mm"); f.note("drawn", "zip", "ZIP")
    items = ["24 windows, one for every day from 1 to 24 December",
             "The Lantern Register: 2,400 shoppers to cross out",
             "A store plan, a street plan and a city map with the tram line",
             "Check-ins on Days 6, 12 and 18 so you never get lost",
             "3 levels of hints for every window",
             "The Sealed Check: test your answer without spoilers",
             "Envelope template and day numbers 1–24 for printing",
             "The solution in its own file, with the full story"]
    d = f.draw(); y = 960
    for it in items:
        d.ellipse([200, y - 14, 228, y + 14], fill=kit.AMBER)
        d.text((260, y), it, font=kit.font("body", 54), fill=kit.SNOW, anchor="lm"); f.note("drawn", "item", it)
        y += 108
    footer(f)
    return f

def m10(A):
    f = night_bg(10, glow=(0.5, 0.5))
    headline(f, "EXACTLY ONE ANSWER,", None, y=170)
    d = f.draw()
    d.text((S / 2, 320), "CHECKED BY CODE", font=kit.font("display", 150), fill=kit.AMBER, anchor="mm"); f.note("drawn", "h", "CHECKED BY CODE")
    rows = [("1", "killer among 2,400 shoppers, and only one"),
            ("21", "clue windows, every one of them needed"),
            ("110,592", "combinations of readings tested: same answer"),
            ("tick", "plans and maps read every reasonable way: straight, through, higher, between, next to"),
            ("3", "check-ins so you can catch a slip early"),
            ("0", "spoilers on the pages you open early")]
    y = 560
    for big, txt in rows:
        d.rounded_rectangle([170, y - 80, S - 170, y + 80], radius=30, fill=kit.NIGHT1 + (230,), outline=kit.STEEL, width=3)
        if big == "tick":
            kit.tick(f, 285, y + 5, 90, col=kit.AMBER, width=16); d = f.draw()
        else:
            d.text((330, y + 4), big, font=kit.font("display", 120), fill=kit.AMBER, anchor="mm"); f.note("drawn", "big", big)
        tf = kit.fit_font(f, txt, "body", 54, S - 700)
        d.text((520, y), txt, font=tf, fill=kit.SNOW, anchor="lm"); f.note("drawn", "row", txt)
        y += 205
    footer(f)
    return f

BUILDERS = [m01, m02, m03, m04, m05, m06, m07, m08, m09, m10]

def build(outdir):
    os.makedirs(outdir, exist_ok=True)
    for fn in os.listdir(outdir):
        if fn.endswith(".jpg"):
            os.remove(os.path.join(outdir, fn))
    A = Assets(); res = []
    for name, fn in zip(NAMES, BUILDERS):
        f = fn(A)
        path = os.path.join(outdir, f"{CL.SLUG}_{name}.jpg")
        f.img.convert("RGB").save(path, quality=88, optimize=True)
        res.append(dict(name=name, path=path, sources=f.sources, hits=kit.spoiler_scan(f.sources, A.bad)))
    sheet = Image.new("RGB", (5 * 400, 2 * 400))
    for k, r in enumerate(res):
        sheet.paste(Image.open(r["path"]).resize((400, 400)), ((k % 5) * 400, (k // 5) * 400))
    sp = os.path.join(outdir, f"{CL.SLUG}_overview.jpg"); sheet.save(sp, quality=85)
    return res, sp, A

if __name__ == "__main__":
    res, sp, A = build(os.path.join(CL.CASE, "listing", "mockups"))
    for r in res:
        print(r["name"], len(r["sources"]), "hits:", r["hits"])
