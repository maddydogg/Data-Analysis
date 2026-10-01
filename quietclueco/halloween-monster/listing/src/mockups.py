"""Ten 2000x2000 listing mockups built from real pages of the case PDF plus code-drawn graphics."""
import math, os
from PIL import Image, ImageDraw, ImageFilter
import kit
from kit import GREEN, CRAN, PARCH, MUST, INK, WHITE, PARCH_DARK, DEEP, font
import case_listing as CL

S = 2000

def headline(f, text, y, col, size=150, name="display", maxw=1800):
    fnt = kit.fit_font(f, text, name, size, maxw)
    f.text((S / 2, y), text, fnt, col, anchor="ma", align="center")
    return fnt

def wrap(f, text, fnt, width):
    d = f.draw(); words = text.split(); lines = []; cur = ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textbbox((0, 0), t, font=fnt)[2] <= width:
            cur = t
        else:
            lines.append(cur); cur = w
    lines.append(cur)
    return "\n".join(lines)

def paper_bg(f, seed=1):
    """Bone-coloured paper with a faint bat pattern."""
    layer = Image.new("RGBA", f.img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    step = f.w // 8
    for i in range(0, f.w, step):
        for j in range(0, f.h, step):
            kit.bat(d, i + step / 2 + (j // step % 2) * step * 0.24, j + step / 2, step * 0.11, PARCH_DARK + (255,))
    f.img.alpha_composite(layer)

paper_bg_small = paper_bg

# ---------------------------------------------------------------- annotations on page images
def circle_tent(L, page, pidx, progress=1.0):
    """Circle the Laboratory Tower (the crime scene, stated in the case text) on the castle map."""
    r = sorted(L.doc[pidx].search_for("Laboratory Tower"), key=lambda q: q.y0)[0]
    lane = L.doc[pidx].search_for("BAT ALLEY")[0]
    u = ((lane.x0 + lane.x1) / 2 - r.x0) / 25.9     # map units: label x0 = ox + 24.1u, map centre = ox + 50u
    cx, cy = page.px(r.x0 - 5.6 * u, (r.y0 + r.y1) / 2 - 1.0 * u)
    im_frame = kit.Frame(page.img.width, page.img.height, (255, 255, 255))
    im_frame.img = page.img
    kit.pen_circle(im_frame, cx, cy, 6.6 * u * page.zoom, 6.2 * u * page.zoom, kit.CRAN, max(4, int(2.4 * page.zoom)), 5, progress)

def tick_notebook(L, page, pidx, keys, progress=None):
    marks = CL.notebook_marks(L, pidx)
    fr = kit.Frame(page.img.width, page.img.height, (255, 255, 255)); fr.img = page.img
    for i, k in enumerate(keys):
        x, y, h = marks[k]
        margin = 48 if L.doc[pidx].rect.width == 768 else 54     # page margin = checkbox left edge
        px, py = page.px(margin + 0.5, y + 1)
        p = 1.0 if progress is None else max(0.0, min(1.0, progress * len(keys) - i))
        if p > 0:
            kit.tick(fr, px, py, 13 * page.zoom, kit.CRAN, max(3, int(1.9 * page.zoom)), p)

def strike_rows(page, rows, predicate, progress=None, seed=0):
    fr = kit.Frame(page.img.width, page.img.height, (255, 255, 255)); fr.img = page.img
    hits = [r for r in rows if predicate(r)]
    for i, (y0, y1, x0, x1, *_rest) in enumerate(hits):
        p = 1.0 if progress is None else max(0.0, min(1.0, progress * len(hits) - i))
        if p <= 0:
            continue
        a = page.px(x0 - 4, (y0 + y1) / 2); b = page.px(x1 + 4, (y0 + y1) / 2)
        if a[1] < 0 or a[1] > page.img.height:
            continue
        kit.marker_strike(fr, a[0], a[1], b[0], (y1 - y0) * page.zoom * 1.3, kit.CRAN, 155, seed + i, p)
    return len(hits)

def holly_lane(r):
    """Clue 11 is stated outright in the notebook: the last purchase was not on Lantern Walk (booths 19-27).
    Crossing those rows out shows real play without revealing any hidden evidence."""
    return 19 <= r[5] <= 27

# ---------------------------------------------------------------- the ten mockups
def m01_main(A):
    f = kit.Frame(S, S, GREEN)
    kit.snow_field(f, 160, 11)
    kit.string_lights(f, 30, 70, 22)
    cover = A.L.image(0, 1640)
    f.paste_page(cover, 690, 1110, angle=3)
    fnt = kit.fit_font(f, CL.WORDS["hook"], "display", 210, 600)
    f.text((1665, 300), CL.WORDS["hook"], fnt, PARCH, anchor="ma", align="center", spacing=0.05)
    d = f.draw(); d.line([(1470, 800), (1860, 800)], fill=MUST, width=8)
    y = 860
    for i, line in enumerate(CL.WORDS["promise"]):
        pf = kit.fit_font(f, line, "black", 90, 590)
        f.text((1665, y), line, pf, MUST if i == 2 else PARCH, anchor="ma")
        y += 128
    pill_f = font("black", 70)
    kit.pill(f, (1665, 1400), CL.WORDS["badges"][0], pill_f, MUST, GREEN)
    kit.pill(f, (1665, 1560), CL.WORDS["badges"][1], pill_f, CRAN, PARCH)
    f.text((1665, 1860), CL.WORDS["brand"], font("display", 64), PARCH, anchor="ma")
    return f

def m02_inside(A):
    f = kit.Frame(S, S, PARCH); paper_bg(f)
    headline(f, "What's inside", 90, GREEN, 170)
    f.text((S / 2, 300), "18 clues · 6 documents · 3 levels of hints", font("bold", 62), CRAN, anchor="ma")
    keys = ["map", "receipt", "weather", "notebook", "log", "hint1"]
    angles = [-26, -15, -5, 5, 15, 26]
    for k, a in zip(keys, angles):
        pg = A.page(k, 1120)
        R = 1300; cx = S / 2 + R * math.sin(math.radians(a)); cy = 2560 - R * math.cos(math.radians(a))
        f.paste_page(pg, cx, cy, angle=-a)
    return f

def m03_documents(A):
    f = kit.Frame(S, S, PARCH); paper_bg(f)
    headline(f, "6 case documents", 80, GREEN, 160)
    docs = [("map", "Castle map"), ("directory", "Booth directory"), ("receipt", "Receipt & note"),
            ("weather", "Weather log"), ("coach", "Bus timetable"), ("statements", "Witness statements")]
    lab = font("black", 56)
    for i, (k, label) in enumerate(docs):
        col, row = i % 3, i // 3
        cx, cy = 360 + col * 640, 800 + row * 720
        pg = A.page(k, 600)
        if k == "map":
            circle_tent(A.L, pg, A.p["map"])
        f.paste_page(pg, cx, cy, angle=[2, -1.5, 1.5, -2, 1, -1][i])
        f.text((cx, cy + 322), label, lab, GREEN, anchor="ma")
    return f

def m04_notebook(A):
    f = kit.Frame(S, S, GREEN); kit.snow_field(f, 90, 4)
    headline(f, "Tick off every clue", 70, PARCH, 160)
    pg = A.L.image(A.p["notebook"], 1640)
    tick_notebook(A.L, pg, A.p["notebook"], [str(i) for i in range(1, 13)])
    f.paste_page(pg, S / 2, 1150, angle=-2)
    return f

def m05_log(A):
    f = kit.Frame(S, S, PARCH); paper_bg(f)
    headline(f, "Cross out the innocent", 70, GREEN, 150)
    f.text((S / 2, 262), "6,000 visitors in the Visitor Log", font("bold", 64), CRAN, anchor="ma")
    idx = A.log_page
    rows = CL.log_rows(A.L, idx)
    top = rows[0][0] - 20; bottom = rows[29][1] + 2
    clip = (40, top, 572, bottom)
    zoom = 1760 / (clip[2] - clip[0])
    pg = A.L.image(idx, int((bottom - top) * zoom), clip=clip)
    strike_rows(pg, rows[:30], holly_lane)
    # fade the lower rows so whole lines can't be read at the bottom edge
    fade = Image.new("L", pg.img.size, 0)
    fd = ImageDraw.Draw(fade)
    for yy in range(pg.img.height):
        t = max(0.0, (yy - pg.img.height * 0.62) / (pg.img.height * 0.38))
        fd.line([(0, yy), (pg.img.width, yy)], fill=int(255 * min(1, t) * 0.92))
    veil = Image.new("RGBA", pg.img.size, PARCH + (255,)); veil.putalpha(fade)
    blurred = pg.img.filter(ImageFilter.GaussianBlur(5))
    pg.img = Image.composite(blurred, pg.img, fade.point(lambda v: min(255, v * 2)))
    pg.img.alpha_composite(veil)
    f.paste_page(pg, S / 2, 400 + pg.img.height / 2, angle=0)
    # sticky note in the corner
    note = kit.Frame(520, 360, (250, 226, 160))
    note.text((260, 90), "Clue 11:\nnot Lantern Walk", font("hand", 72), INK, anchor="ma", align="center")
    f.paste(note.img, 1620, 1720, angle=-6)
    f.sources += note.sources
    return f

def m06_hints(A):
    f = kit.Frame(S, S, GREEN); kit.snow_field(f, 80, 6)
    headline(f, "Stuck? 3 levels of help", 70, PARCH, 150)
    d = f.draw()
    d.rounded_rectangle([150, 330, 1850, 950], radius=30, fill=PARCH)
    f.text((230, 390), "LEVEL 1 · A GENTLE NUDGE", font("black", 48), CRAN)
    f.text((230, 470), "Evidence B", font("display", 84), GREEN)
    body = font("bold", 62)
    f.text((230, 600), wrap(f, CL.H.HINTS["B"][0], body, 1540), body, INK, spacing=0.3)
    lab = font("display", 150)
    kit.envelope(f, (150, 1060, 960, 1640), 2, lab)
    kit.envelope(f, (1040, 1060, 1850, 1640), 3, lab)
    sub = font("bold", 58)
    f.text((555, 1690), "Level 2: a stronger push", sub, PARCH, anchor="ma")
    f.text((1445, 1690), "Level 3: nearly the answer", sub, PARCH, anchor="ma")
    f.text((S / 2, 1830), "Each level on its own pages, so no accidental spoilers", font("body", 52), MUST, anchor="ma")
    return f

def m07_check(A):
    f = kit.Frame(S, S, PARCH); paper_bg(f)
    headline(f, "Check your answer\nwithout spoilers", 60, GREEN, 140)
    pidx = A.p["check"]
    r = CL.text_rect(A.L, pidx, "If your last three digits are")
    clip = (0, 40, 612, r.y0 - 30)            # stop well above the green answer box
    width_px = 1200                          # size by width: the clip is wider than it is tall
    pg = A.L.image(pidx, int(width_px * (clip[3] - clip[1]) / (clip[2] - clip[0])), clip=clip)
    f.paste_page(pg, 700, 1020, angle=-2)
    kit.envelope(f, (1340, 700, 1930, 1110), "?", font("display", 110))
    f.text((1635, 1170), "Digits match?", font("black", 62), GREEN, anchor="ma")
    f.text((1635, 1255), "Open the", font("bold", 58), INK, anchor="ma")
    f.text((1635, 1330), "solution file", font("bold", 58), INK, anchor="ma")
    f.text((S / 2, 1600), "No names, no answers printed in the case file", font("black", 64), CRAN, anchor="ma")
    return f

def m08_print_ipad(A):
    f = kit.Frame(S, S, PARCH_DARK)
    headline(f, "Print it or play on iPad", 70, GREEN, 150)
    mm = 4.3
    lw, lh = 215.9 * mm, 279.4 * mm                 # US Letter
    iw, ih = 214.9 * mm, 280.6 * mm                 # 12.9-inch tablet body, 3:4 screen
    pg = A.L.image(A.p["map"], int(lh))
    circle_tent(A.L, pg, A.p["map"])
    f.paste_page(pg, 520, 1130, angle=2)
    scr = A.I.image(A.ip["notebook"], int(ih * 0.91))
    tick_notebook(A.I, scr, A.ip["notebook"], [str(i) for i in range(1, 7)])
    tab = kit.Frame(int(iw) + 60, int(ih) + 60, PARCH_DARK)
    tab.img = Image.new("RGBA", tab.img.size, (0, 0, 0, 0))
    kit.ipad(tab, (30, 30, 30 + iw, 30 + ih), scr)
    f.paste(tab.img, 1480, 1130, angle=0)
    f.sources += tab.sources
    lab = font("black", 58)
    f.text((520, 1800), "Print: US Letter & A4", lab, GREEN, anchor="ma")
    f.text((1480, 1800), "iPad: tap to jump", lab, GREEN, anchor="ma")
    return f

def m09_who(A):
    f = kit.Frame(S, S, GREEN); kit.snow_field(f, 120, 9)
    kit.string_lights(f, 20, 60, 18)
    headline(f, "Solo or date night", 200, PARCH, 170)
    kit.pumpkin(f, 400, 900, 170)
    kit.pumpkin(f, 890, 920, 140); kit.pumpkin(f, 1130, 920, 140, col=CRAN)
    kit.clock(f, 1620, 900, 190)
    lab = font("black", 72)
    f.text((400, 1150), "Just you", lab, PARCH, anchor="ma")
    f.text((1010, 1150), "For two", lab, PARCH, anchor="ma")
    f.text((1620, 1150), "90–150 min", lab, PARCH, anchor="ma")
    kit.people(f, 1000, 1480, 180, 4)
    kit.pill(f, (1000, 1690), "1–4 players", font("black", 90), MUST, GREEN)
    f.text((1000, 1830), "Spooky, not gory: a cozy mystery", font("bold", 60), PARCH, anchor="ma")
    return f

def m10_get(A):
    f = kit.Frame(S, S, PARCH); paper_bg(f)
    headline(f, "What you get", 70, GREEN, 170)
    lab = font("black", 54); bf = font("black", 34)
    cards = [("US Letter", A.L.image(0, 520)), ("A4", A.A4.image(0, 520)), ("iPad", A.I.image(0, 520))]
    x = 110
    for label, thumb in cards:
        kit.pdf_file_card(f, (x, 330, x + 400, 900), thumb, label, lab, "PDF", bf)
        x += 450
    kit.pdf_file_card(f, (x, 330, x + 400, 900), None, "Solution", lab, "PDF", bf)
    kit.envelope(f, (x + 60, 430, x + 340, 640), "?", font("display", 70))
    rules = A.page("rules", 760)
    f.paste_page(rules, 520, 1430, angle=-2)
    f.text((520, 1850), "House rules: every term defined", font("black", 50), GREEN, anchor="ma")
    d = f.draw()
    cx, cy, r = 1420, 1400, 380
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GREEN)
    d.ellipse([cx - r + 22, cy - r + 22, cx + r - 22, cy + r - 22], outline=MUST, width=8)
    f.text((cx, cy - 190), "Exactly\none answer", font("display", 112), PARCH, anchor="ma", align="center")
    f.text((cx, cy + 105), "checked by code", font("black", 64), MUST, anchor="ma")
    kit.tick(f, cx - 50, cy + 290, 100, MUST, 14)
    return f

MOCKUPS = [("01-main", m01_main), ("02-whats-inside", m02_inside), ("03-six-documents", m03_documents),
           ("04-inspectors-notebook", m04_notebook), ("05-visitor-log-in-progress", m05_log),
           ("06-three-levels-of-hints", m06_hints), ("07-sealed-check", m07_check),
           ("08-print-or-ipad", m08_print_ipad), ("09-who-its-for", m09_who), ("10-what-you-get", m10_get)]

class Assets:
    def __init__(self):
        self.L, self.I, self.p, self.ip = CL.pages()
        self.A4 = kit.Pdf(CL.PDF["a4"])
        self.bad = CL.forbidden()
        clean = CL.clean_log_pages(self.L, self.bad)
        # prefer a page from the busy evening chapters
        self.log_page = next((i for i in clean if "18:" in self.L.doc[i].get_text()[:400]), clean[0])
        self.p["log"] = self.log_page

    def page(self, key, height):
        return self.L.image(self.p[key], height)

def build(outdir):
    os.makedirs(outdir, exist_ok=True)
    A = Assets()
    results = []
    thumbs = []
    for name, fn in MOCKUPS:
        fr = fn(A)
        path = os.path.join(outdir, f"{CL.SLUG}_{name}.png")
        fr.save(path)
        results.append(dict(name=name, path=path, sources=fr.sources,
                            hits=kit.spoiler_scan(fr.sources, A.bad)))
        thumbs.append(fr.img.convert("RGB").resize((380, 380), Image.LANCZOS))
    # overview sheet
    g = 24; W = 5 * 380 + 6 * g; H = 2 * 380 + 3 * g + 90
    sheet = Image.new("RGB", (W, H), GREEN)
    d = ImageDraw.Draw(sheet)
    d.text((W / 2, 20), "Storm over Corvenmoor — listing images 1–10", font=font("display", 48), fill=PARCH, anchor="ma")
    for i, t in enumerate(thumbs):
        sheet.paste(t, (g + (i % 5) * (380 + g), 90 + g + (i // 5) * (380 + g)))
        d.text((g + (i % 5) * (380 + g) + 14, 90 + g + (i // 5) * (380 + g) + 10), str(i + 1),
               font=font("black", 40), fill=CRAN)
    sheet_path = os.path.join(outdir, f"{CL.SLUG}_overview.png")
    sheet.save(sheet_path, optimize=True)
    return results, sheet_path, A
