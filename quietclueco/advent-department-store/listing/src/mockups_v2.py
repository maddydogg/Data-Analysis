"""Ten listing images, variant 2 ("action"): 2000 x 2000 JPG.

Same content as variant 1 (cover; the calendar; Days 1, 2 and 3; envelopes; iPad; who it's for;
what's inside; checked by code), restyled as anime action key frames: tilted title-card headlines
with a hard outline and an amber offset shadow, manga focus lines, snow streaking past, amber
barrier tape, slanted manga panels with action inserts (the runner, the cup knocked over, the
brass magpie glinting, the store clock at 21:20), pages thrown onto the frame at steep angles.

Only Windows 1-3 and the set-up pages are shown. Every string drawn and the text layer of every PDF
region pasted is recorded on the kit.Frame, so the spoiler check reads exactly what a buyer can read.
"""
import math, os, random
from PIL import Image, ImageDraw, ImageFilter
import kit
import cal_listing as CL
from cal_listing import art
import action as X
import cover_v2 as CV
import mockups as M1

S = 2000
VARIANT = "v2-action"
NAMES = M1.NAMES

# ---------------------------------------------------------------- shared pieces
def bg(seed=1, focus=(0.5, 0.55), beam=True, lines=True):
    cv = art.Canvas(S, S, ss=1)
    art.sky(cv, X.NIGHT0, X.NIGHT1)
    fx, fy = S * focus[0], S * focus[1]
    cv.glow(fx, fy, S * 0.42, X.AMBER, alpha=46)
    if lines:
        X.focus_lines(cv, fx, fy, n=150, r_in=(0.36, 0.52), col=X.SNOW, alpha=(10, 42), width=(2, 10), seed=seed)
        X.focus_lines(cv, fx, fy, n=30, r_in=(0.42, 0.56), col=X.AMBER, alpha=(18, 60), width=(3, 10), seed=seed + 1)
    if beam:
        X.light_beam(cv, (S * 1.05, -S * 0.05), 118, 142, S * 2.2, alpha=34, blur=30)
    X.streaks(cv, 260, angle=-58, length=(40, 150), alpha=(30, 120), width=(1.5, 3), seed=seed + 2)
    art.snow(cv, 380, seed=seed + 3, angle=-30, big=True)
    f = kit.Frame(S, S, kit.NIGHT0)
    f.img = cv.finish(grain=12, vignette=0.4, seed=seed).convert("RGBA")
    return f

def T(f, xy, text, size, fill=X.SNOW, shadow=X.AMBER_D, angle=-3, glow=None, maxw=S - 200, name="display"):
    """Title-card text, fitted to maxw, recorded for the spoiler check."""
    fnt = kit.fit_font(f, text, name, size, maxw)
    X.slam_text(f.img, xy, text, fnt, fill=fill, shadow=shadow, angle=angle, glow=glow)
    f.note("drawn", "title", text)

def B(f, xy, text, size, bg_=X.AMBER, fg=X.NIGHT0, angle=-3, name="display"):
    X.badge(f.img, xy, text, kit.font(name, size), bg=bg_, fg=fg, angle=angle)
    f.note("drawn", "badge", text)

def headline(f, top, sub=None, y=170, top_col=X.SNOW):
    T(f, (S / 2, y), top, 190, fill=top_col)
    if sub:
        fnt = kit.fit_font(f, sub, "display", 64, S - 360)
        X.badge(f.img, (S / 2, y + 150), sub, fnt, bg=X.NIGHT0, fg=X.AMBER, angle=-3, outline=X.AMBER)
        f.note("drawn", "sub", sub)

FOOT = "THE WINDOWS AT QUILLON’S  ·  MURDER MYSTERY ADVENT CALENDAR"
def footer(f):
    X.tape(f.img, S - 78, -2, FOOT, kit.font("display", 52), seed=7)
    f.note("drawn", "footer", FOOT)

def panel(f, poly, im, border=14):
    """Paste `im` into a slanted manga panel (polygon), with a dark border and a thin snow keyline."""
    xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
    x0, y0, x1, y1 = int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))
    im = im.convert("RGBA").resize((x1 - x0, y1 - y0), Image.LANCZOS)
    m = Image.new("L", (x1 - x0, y1 - y0), 0)
    ImageDraw.Draw(m).polygon([(x - x0, y - y0) for x, y in poly], fill=255)
    sh = Image.new("RGBA", f.img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).polygon([(x + 16, y + 22) for x, y in poly], fill=(0, 0, 0, 150))
    f.img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    f.img.paste(im, (x0, y0), m)
    d = f.draw()
    d.line(poly + [poly[0]], fill=X.NIGHT0, width=border, joint="curve")
    d.line(poly + [poly[0]], fill=X.SNOW, width=3)

def env_img(n, w=420):
    h = int(w * 0.52)
    fr = kit.Frame(w + 20, h + 20, (0, 0, 0)); fr.img = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0))
    kit.envelope(fr, (10, 10, w + 10, h + 10), n, kit.font("display", int(h * 0.42)), col=kit.SNOW, seal=kit.NIGHT1)
    return fr.img

def fly_env(f, n, x, y, ang, w=420, trail=True):
    im = env_img(n, w)
    if trail:          # motion trail: faint copies behind the envelope
        for k in (3, 2, 1):
            g = im.copy(); g.putalpha(g.split()[3].point(lambda v, k=k: int(v * 0.12 * (4 - k))))
            f.paste(g, x + k * 46, y + k * 30, angle=ang, shadow=False)
    f.paste(im, x, y, angle=ang)
    f.note("drawn", "envelope", str(n))

# ---------------------------------------------------------------- action inserts (code-drawn art)
def art_cup(w, h, t=1.0, seed=4):
    cv = art.Canvas(w, h, ss=1)
    art.sky(cv, X.NIGHT0, X.NIGHT1)
    cv.glow(w * 0.5, h * 0.5, w * 0.5, X.AMBER, alpha=80)
    X.focus_lines(cv, w * 0.42, h * 0.55, n=120, r_in=(0.18, 0.3), col=X.SNOW, alpha=(30, 110), width=(2, 8), seed=seed)
    cv.d.polygon(cv.P([(0, h * 0.78), (w, h * 0.7), (w, h), (0, h)]), fill=X.INK2)          # the workbench, tilted
    cv.d.line(cv.P([(0, h * 0.78), (w, h * 0.7)]), fill=X.AMBER_D, width=3)
    X.cup_splash(cv, w * 0.36, h * 0.6, h * 0.36, angle=58, t=t, seed=seed)
    return cv.finish(grain=10, vignette=0.35, seed=seed)

def art_brooch(w, h, glint=1.0, seed=6):
    cv = art.Canvas(w, h, ss=1)
    art.sky(cv, X.NIGHT1, X.NIGHT2)
    X.focus_lines(cv, w * 0.5, h * 0.48, n=120, r_in=(0.2, 0.34), col=X.AMBER, alpha=(20, 80), width=(2, 8), seed=seed)
    cv.d.polygon(cv.P([(-w * 0.1, h * 0.25), (w * 1.1, -h * 0.1), (w * 1.1, h * 1.1), (-w * 0.1, h * 1.1)]), fill=X.INK)   # the coat
    cv.d.polygon(cv.P([(-w * 0.1, h * 0.25), (w * 1.1, -h * 0.1), (w * 1.1, h * 0.12), (w * 0.1, h * 0.62)]), fill=X.INK2)  # the lapel
    cv.d.line(cv.P([(-w * 0.1, h * 0.25), (w * 1.1, -h * 0.1)]), fill=X.STEEL, width=3)
    cv.d.line(cv.P([(w * 0.1, h * 0.62), (w * 1.1, h * 0.12)]), fill=X.INK, width=6)
    cv.glow(w * 0.5, h * 0.42, h * 0.3, X.AMBER, alpha=120)
    gx, gy = X.brass_magpie(cv, w * 0.53, h * 0.44, h * 0.66, angle=-14)
    if glint > 0:
        X.flare(cv, gx, gy, h * 0.16 * glint)
    X.streaks(cv, 40, angle=-58, length=(20, 70), alpha=(40, 140), seed=seed)
    return cv.finish(grain=10, vignette=0.35, seed=seed)

def art_clock(w, h, hh=21, mm=20, seed=8):
    cv = art.Canvas(w, h, ss=1)
    art.sky(cv, X.NIGHT0, X.NIGHT2)
    X.focus_lines(cv, w * 0.5, h * 0.5, n=120, r_in=(0.3, 0.42), col=X.SNOW, alpha=(20, 80), width=(2, 8), seed=seed)
    X.wall_clock(cv, w * 0.5, h * 0.5, min(w, h) * 0.34, hh, mm)
    X.streaks(cv, 50, angle=-58, length=(20, 80), alpha=(40, 140), seed=seed)
    art.snow(cv, 80, seed=seed, angle=-30)
    return cv.finish(grain=10, vignette=0.35, seed=seed)

def art_run(w, h, seed=11):
    return CV.keyart(w, h, seed=seed, ss=1, grain=10)

# ---------------------------------------------------------------- the ten images
def m01(A):
    f = kit.Frame(S, S, kit.NIGHT0); rec = []
    f.img = CV.cover(S, S, badges=True, record=rec.append).convert("RGBA")
    for t in rec:
        f.note("drawn", "cover", t)
    return f

def m02(A):
    f = bg(2, focus=(0.42, 0.58))
    headline(f, "24 WINDOWS. 24 NIGHTS.", "OPEN ONE EACH DAY FROM 1 TO 24 DECEMBER")
    pg = A.L.image(A.p["calendar"], 1280)
    f.paste_page(pg, 700, 1110, angle=6)
    for n, x, y, a in ((1, 1560, 640, -14), (2, 1640, 960, 10), (3, 1530, 1270, -8), (24, 1620, 1580, 14)):
        fly_env(f, n, x, y, a, w=440)
    footer(f)
    return f

def m03(A):
    f = bg(3, focus=(0.55, 0.6))
    headline(f, "DAY 1: THE CASE", "A LETTER · A STORE PLAN · A MURDER AT 21:20")
    a = A.L.image(A.p["w1"], 1180); b = A.L.image(A.p["w1letter"], 1120)
    f.paste_page(a, 560, 1120, angle=-7); f.paste_page(b, 1180, 1160, angle=5)
    panel(f, [(1330, 480), (1930, 430), (1960, 960), (1380, 1010)], art_cup(640, 580))
    B(f, (1640, 1040), "10 MINUTES BEFORE THE CURTAIN", 50, angle=-5)
    footer(f)
    return f

def m04(A):
    f = bg(4, focus=(0.6, 0.55))
    headline(f, "DAY 2: 2,400 SUSPECTS", "THE LANTERN REGISTER · CROSS THEM OUT, NIGHT BY NIGHT")
    a = A.L.image(A.p["w2"], 1100)
    f.paste_page(a, 520, 1150, angle=-8)
    b = A.L.image(A.log_page, 1360)
    x0, y0 = 1300 - b.img.width / 2, 1110 - b.img.height / 2
    f.paste_page(b, 1300, 1110)
    rows = CL.log_rows(A.L, A.log_page)
    M1.strike_rows(f, A, b, x0, y0, rows, set(range(1, len(rows), 2)) | {4, 8}, seed=5)
    T(f, (1520, 1760), "FROM 2,400 TO 1", 170, fill=X.AMBER, shadow=X.NIGHT0, angle=-6, glow=X.AMBER, maxw=900)
    footer(f)
    return f

def m05(A):
    f = bg(5, focus=(0.4, 0.55))
    headline(f, "DAYS 3–23: NEW EVIDENCE EVERY NIGHT", "STATEMENTS · PLANS · MAPS · RECEIPTS")
    a = A.L.image(A.p["w3"], 1460)
    f.paste_page(a, 700, 1120, angle=-5)
    panel(f, [(1330, 440), (1960, 490), (1930, 1120), (1300, 1070)], art_brooch(660, 680))
    B(f, (1620, 1150), "ONE OF THEM WORE A BRASS MAGPIE", 48, angle=4)
    w4 = A.L.doc[A.p["hint1"]].search_for("Window 4")[0]
    clip = (40, 60, 572, w4.y0 - 4)                                   # Window 3's level-1 hint only
    h = A.L.image(A.p["hint1"], int(900 * (clip[3] - clip[1]) / (clip[2] - clip[0])), clip=clip)
    f.paste_page(h, 1480, 1600, angle=6)
    B(f, (1560, 1400), "3 LEVELS OF HINTS", 76, bg_=X.SNOW, angle=6)
    footer(f)
    return f

def m06(A):
    f = bg(6, focus=(0.7, 0.5))
    headline(f, "PRINT. FOLD. OPEN.", "ENVELOPE TEMPLATE + DAY NUMBERS 1–24 INCLUDED")
    a = A.L.image(A.p["envelope"], 1120); b = A.L.image(A.p["labels"], 1120)
    f.paste_page(a, 520, 1100, angle=-8); f.paste_page(b, 1080, 1160, angle=4)
    for n, x, y, ang in ((7, 1700, 620, 16), (12, 1610, 930, -12), (18, 1720, 1240, 8), (24, 1600, 1560, -16)):
        fly_env(f, n, x, y, ang, w=400)
    footer(f)
    return f

def tap_ripple(f, x, y, r):
    d = f.draw()
    for k, rr in enumerate((r, r * 0.68, r * 0.38)):
        d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=X.AMBER + (255 - k * 50,), width=10 - k * 2)
    d.ellipse([x - 22, y - 22, x + 22, y + 22], fill=X.AMBER)

def m07(A):
    f = bg(7, focus=(0.5, 0.58))
    headline(f, "ON iPAD: TAP TODAY’S WINDOW", "GOODNOTES · NOTABILITY · ANY PDF APP")
    scr = A.I.image(A.ip["calendar"], 1300)
    ih = 1340; iw = ih * 0.75
    tab = kit.Frame(int(iw) + 40, ih + 40, (0, 0, 0)); tab.img = Image.new("RGBA", tab.img.size, (0, 0, 0, 0))
    kit.ipad(tab, (20, 20, 20 + iw, 20 + ih), scr)
    f.paste(tab.img, S / 2, 1130, angle=-5)
    for kind, src, text in tab.sources:
        f.note(kind, src, text)
    tap_ripple(f, 1210, 1180, 120)
    B(f, (1560, 1530), "EVERY WINDOW LINKS BACK", 56, angle=8)
    footer(f)
    return f

def m08(A):
    f = bg(8, focus=(0.5, 0.5), beam=False)
    headline(f, "WHO IT’S FOR", "ONE DETECTIVE OR UP TO FOUR · 10–25 MINUTES A DAY")
    d = f.draw()
    panels = [("FOR TWO", "A December ritual for couples: one window with the evening tea.",
               [(60, 430), (700, 415), (650, 1330), (60, 1345)]),
              ("FOR THE FAMILY", "Teens and grown-ups split the register and race to the answer.",
               [(740, 412), (1290, 400), (1260, 1320), (690, 1330)]),
              ("AS A GIFT", "Instant download: a last-minute present for any mystery lover.",
               [(1330, 397), (1940, 385), (1940, 1310), (1300, 1318)])]
    arts = [scene_people(640, 930, [(-110, 0.0, 0.4), (110, 0.5, 0.36)], seed=1),
            scene_people(600, 930, [(-150, 0.5, 0.3), (0, 0.0, 0.38), (150, 0.55, 0.32)], seed=2),
            scene_gift(640, 930, seed=3)]
    for (title, text, poly), im in zip(panels, arts):
        panel(f, poly, im)
        cx = sum(p[0] for p in poly) / 4
        T(f, (cx, 1430), title, 110, fill=X.AMBER, shadow=X.NIGHT0, angle=-3, maxw=560)
        tf = kit.font("bold", 44); words = text.split(); lines = [""]
        for wd in words:
            if d.textlength(lines[-1] + " " + wd, font=tf) > 500:
                lines.append(wd)
            else:
                lines[-1] = (lines[-1] + " " + wd).strip()
        y = 1560
        for ln in lines:
            d.text((cx, y), ln, font=tf, fill=X.SNOW, anchor="mm"); y += 62
        f.note("drawn", "text", text)
    footer(f)
    return f

def scene_people(w, h, figs, seed=1):
    """Shop windows in the snow and people seen from behind hurrying towards them."""
    cv = art.Canvas(w, h, ss=1)
    art.sky(cv, X.NIGHT0, X.NIGHT1)
    q = X.Quad((-w * 0.2, h * 0.05), (w * 1.2, h * 0.12), (w * 1.25, h * 0.66), (-w * 0.25, h * 0.7))
    X.tower(cv, q, cols=3, rows=4, seed=seed, lit=0.4, band=(0.04, 0.68), shop=(0.72, 0.98))
    cv.d.polygon(cv.P([(-w * 0.25, h * 0.7), (w * 1.25, h * 0.66), (w * 1.3, h), (-w * 0.3, h)]), fill=X.NIGHT1)
    X.streaks(cv, 60, angle=-58, length=(20, 80), alpha=(40, 140), seed=seed)
    for dx, ph, hh in figs:
        X.runner(cv, w * 0.5 + dx, h * 0.97, h * hh, phase=ph, glow=True)
    art.snow(cv, 140, seed=seed, angle=-30)
    return cv.finish(grain=10, vignette=0.35, seed=seed)

def scene_gift(w, h, seed=3):
    cv = art.Canvas(w, h, ss=1)
    art.sky(cv, X.NIGHT0, X.NIGHT1)
    X.focus_lines(cv, w * 0.5, h * 0.45, n=120, r_in=(0.2, 0.32), col=X.AMBER, alpha=(20, 80), width=(2, 8), seed=seed)
    cv.glow(w * 0.5, h * 0.45, w * 0.4, X.AMBER, alpha=90)
    x, y, s = w * 0.5, h * 0.47, w * 0.5          # a parcel tied with ribbon, glowing
    cv.d.rectangle(cv.S(x - s * 0.5, y - s * 0.4, x + s * 0.5, y + s * 0.45), fill=X.INK, outline=X.AMBER_D, width=4)
    cv.d.rectangle(cv.S(x - s * 0.08, y - s * 0.4, x + s * 0.08, y + s * 0.45), fill=X.AMBER)
    cv.d.rectangle(cv.S(x - s * 0.5, y - s * 0.06, x + s * 0.5, y + s * 0.08), fill=X.AMBER)
    for sg in (-1, 1):
        cv.d.ellipse(cv.S(x + sg * s * 0.3 - s * 0.16, y - s * 0.62, x + sg * s * 0.3 + s * 0.16, y - s * 0.38), outline=X.AMBER, width=10)
    X.flare(cv, x + s * 0.42, y - s * 0.42, s * 0.3)
    art.snow(cv, 120, seed=seed, angle=-30)
    return cv.finish(grain=10, vignette=0.35, seed=seed)

def m09(A):
    f = bg(9, focus=(0.5, 0.4), beam=False)
    headline(f, "WHAT’S INSIDE", "4 FILES · INSTANT DOWNLOAD")
    cards = [("US LETTER", "89 PAGES"), ("A4", "85 PAGES"), ("iPAD", "77 PAGES · LINKED"), ("SOLUTION", "SEPARATE ZIP")]
    d = f.draw()
    for k, (lab, sub) in enumerate(cards):
        cx = 300 + k * 470; cy = 640; ang = (-6, 4, -4, 6)[k]
        c = Image.new("RGBA", (380, 470), (0, 0, 0, 0)); cd = ImageDraw.Draw(c)
        cd.rounded_rectangle([0, 0, 379, 469], radius=24, fill=X.SNOW, outline=X.NIGHT0, width=8)
        if lab != "SOLUTION":
            for r in range(4):
                for q in range(4):
                    x0 = 46 + q * 75; y0 = 50 + r * 62
                    cd.rounded_rectangle([x0, y0, x0 + 62, y0 + 50], radius=8, fill=X.AMBER if (r * 4 + q) % 5 == 0 else X.NIGHT1)
        else:
            cd.rounded_rectangle([90, 70, 290, 290], radius=20, fill=X.NIGHT1)
            cd.text((190, 180), "ZIP", font=kit.font("display", 120), fill=X.AMBER, anchor="mm")
        cd.text((190, 345), lab, font=kit.font("display", 74), fill=X.NIGHT0, anchor="mm")
        cd.text((190, 415), sub, font=kit.font("bold", 30), fill=X.AMBER_D, anchor="mm")
        f.paste(c, cx, cy, angle=ang)
        f.note("drawn", "card", f"{lab} {sub}")
    items = ["24 windows, one for every day from 1 to 24 December",
             "The Lantern Register: 2,400 shoppers to cross out",
             "A store plan, a street plan and a city map with the tram line",
             "Check-ins on Days 6, 12 and 18 so you never get lost",
             "3 levels of hints for every window",
             "The Sealed Check: test your answer without spoilers",
             "Envelope template and day numbers 1–24 for printing",
             "The solution in its own file, with the full story"]
    y = 1010
    for it in items:
        d.polygon([(190, y - 18), (226, y), (190, y + 18)], fill=X.AMBER)
        d.text((260, y), it, font=kit.font("bold", 54), fill=X.SNOW, anchor="lm"); f.note("drawn", "item", it)
        y += 104
    footer(f)
    return f

def m10(A):
    f = bg(10, focus=(0.5, 0.5))
    T(f, (S / 2, 170), "EXACTLY ONE ANSWER.", 180)
    T(f, (S / 2, 340), "CHECKED BY CODE.", 180, fill=X.AMBER, shadow=X.NIGHT0, glow=X.AMBER)
    rows = [("1", "killer among 2,400 shoppers, and only one"),
            ("21", "evidence windows, every one of them needed"),
            ("110,592", "combinations of readings tested: same answer"),
            ("tick", "plans and maps read every reasonable way: straight, through, higher, between, next to"),
            ("3", "check-ins so you can catch a slip early"),
            ("0", "spoilers on the pages you open early")]
    y = 600
    for k, (big, txt) in enumerate(rows):
        off = 30 if k % 2 else -30
        bar = Image.new("RGBA", (S - 300, 170), (0, 0, 0, 0)); bd = ImageDraw.Draw(bar)
        bd.polygon([(30, 0), (S - 300, 0), (S - 330, 169), (0, 169)], fill=X.NIGHT1 + (240,), outline=X.STEEL)
        bd.polygon([(30, 0), (330, 0), (300, 169), (0, 169)], fill=X.AMBER)
        f.paste(bar, S / 2 + off, y, angle=0, shadow=True)
        d = f.draw()
        if big == "tick":
            kit.tick(f, 255 + off, y + 5, 90, col=X.NIGHT0, width=18); d = f.draw()
        else:
            fb = kit.fit_font(f, big, "display", 130, 270)
            d.text((315 + off, y + 6), big, font=fb, fill=X.NIGHT0, anchor="mm"); f.note("drawn", "big", big)
        tf = kit.fit_font(f, txt, "bold", 52, S - 820)
        d.text((520 + off, y), txt, font=tf, fill=X.SNOW, anchor="lm"); f.note("drawn", "row", txt)
        y += 205
    footer(f)
    return f

BUILDERS = [m01, m02, m03, m04, m05, m06, m07, m08, m09, m10]

def build(outdir):
    os.makedirs(outdir, exist_ok=True)
    for fn in os.listdir(outdir):
        if fn.endswith(".jpg"):
            os.remove(os.path.join(outdir, fn))
    A = M1.Assets(); res = []
    for name, fn in zip(NAMES, BUILDERS):
        f = fn(A)
        path = os.path.join(outdir, f"{CL.SLUG}_{VARIANT}_{name}.jpg")
        f.img.convert("RGB").save(path, quality=88, optimize=True)
        res.append(dict(name=name, path=path, sources=f.sources, hits=kit.spoiler_scan(f.sources, A.bad)))
        print(name, "ok", len(res[-1]["hits"]), "hits")
    sheet = Image.new("RGB", (5 * 400, 2 * 400))
    for k, r in enumerate(res):
        sheet.paste(Image.open(r["path"]).resize((400, 400)), ((k % 5) * 400, (k // 5) * 400))
    sp = os.path.join(outdir, f"{CL.SLUG}_{VARIANT}_overview.jpg"); sheet.save(sp, quality=85)
    return res, sp, A

if __name__ == "__main__":
    import sys
    out = os.path.join(CL.CASE, "listing", "v2", "mockups")
    if len(sys.argv) > 1:          # build only some images, e.g. `python3 mockups_v2.py 3 5`
        os.makedirs(out, exist_ok=True); A = M1.Assets()
        for k in map(int, sys.argv[1:]):
            f = BUILDERS[k - 1](A)
            p = os.path.join(out, f"{CL.SLUG}_{VARIANT}_{NAMES[k - 1]}.jpg"); f.img.convert("RGB").save(p, quality=88)
            print(NAMES[k - 1], kit.spoiler_scan(f.sources, A.bad))
    else:
        res, sp, A = build(out)
