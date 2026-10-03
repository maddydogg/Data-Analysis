"""Ten 2000x2000 listing images for Full Moon over Morrowmere, styled as an old horror-mystery
release: 01 is the one-sheet poster, 02-09 are lobby cards (a framed card with a caption and a
large real page of the case inside), 10 is a "What you get" poster. Every page shown is a real
PDF region; every word drawn by code is recorded for the spoiler scan."""
import math, os
from PIL import Image, ImageDraw, ImageFilter
import kit
from kit import GREEN, CRAN, PARCH, MUST, INK, WHITE, PARCH_DARK, DEEP, AUB, font
import poster as P
import case_listing as CL

S = 2000
CONTENT = (120, 236, 1880, 1566)          # the picture area of a lobby card

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

# ---------------------------------------------------------------- the lobby-card frame
def lobby(no, caption, sub, seed=1):
    """A lobby card: plum surround, a parchment card with a double rule, a header line, a
    halftone picture area and a caption panel. Returns the frame."""
    f = kit.Frame(S, S, P.PLUM); img = f.img
    P.gradient(img, P.NIGHT, P.AUB)
    P.halftone(img, (0, 0, S, S), P.AMETHYST + (34,), 30, falloff=lambda x, y: 0.55)
    d = f.draw()
    d.rectangle([56, 56, S - 56, S - 56], fill=PARCH)
    d.rectangle([76, 76, S - 76, S - 76], outline=AUB, width=6)
    d.rectangle([90, 90, S - 90, S - 90], outline=MUST, width=3)
    for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        P.star(d, (90 if sx > 0 else S - 90) + sx * 34, (90 if sy > 0 else S - 90) + sy * 34, 14, MUST)
    P.tracked(f, S / 2, 128, "FULL MOON OVER MORROWMERE", P.hf("cinzel", 50, 800), AUB, 10)
    f.text((150, 142), "QUIETCLUECO", P.hf("oswald", 30, 500), CRAN)
    f.text((S - 150, 142), f"LOBBY CARD No. {no}", P.hf("oswald", 30, 500), CRAN, anchor="ra")
    x0, y0, x1, y1 = CONTENT
    P.gradient(img, P.AUB, P.PLUM, CONTENT)
    P.halftone(img, CONTENT, P.AMETHYST + (70,), 26,
               falloff=lambda x, y: max(0.1, 1 - math.hypot(x - (x0 + x1) / 2, y - (y0 + y1) / 2) / 1100))
    d = f.draw()
    d.rectangle(CONTENT, outline=P.NIGHT, width=4)
    d.rectangle([120, 1592, 1880, 1880], fill=P.PLUM)
    d.rectangle([132, 1604, 1868, 1868], outline=MUST, width=3)
    cap = P.fit(caption, "abril", 120, 1640)
    f.text((S / 2, 1632), caption, cap, MUST, anchor="ma")
    f.text((S / 2, 1790), sub, P.hf("oswald", 50, 500), PARCH, anchor="ma")
    return f

def page_in(f, page, cx, cy, angle=0, border=True):
    f.paste_page(page, cx, cy, angle=angle, border=border)

def note_card(f, text, cx, cy, angle, w=500, h=330, size=66):
    note = kit.Frame(w, h, (250, 232, 176))
    note.text((w / 2, h * 0.22), text, font("hand", size), INK, anchor="ma", align="center")
    f.paste(note.img, cx, cy, angle=angle)
    f.sources += note.sources

# ---------------------------------------------------------------- annotations on page images
def circle_shop(L, page, pidx, progress=1.0):
    """Circle Quell's Apothecary (the crime scene, stated in the case text) on the fair map."""
    r = sorted(L.doc[pidx].search_for("Quell’s Apothecary"), key=lambda q: q.y0)[0]
    cx, cy = page.px((r.x0 + r.x1) / 2 + 8, (r.y0 + r.y1) / 2 - 3)
    fr = kit.Frame(page.img.width, page.img.height, (255, 255, 255)); fr.img = page.img
    kit.pen_circle(fr, cx, cy, (r.x1 - r.x0) * 0.85 * page.zoom, 18 * page.zoom, CRAN, max(5, int(2.4 * page.zoom)), 5, progress)

def tick_notebook(L, page, pidx, keys, progress=None):
    marks = CL.notebook_marks(L, pidx)
    fr = kit.Frame(page.img.width, page.img.height, (255, 255, 255)); fr.img = page.img
    margin = 48 if L.doc[pidx].rect.width == 768 else 54
    for i, k in enumerate(keys):
        x, y, h = marks[k]
        px, py = page.px(margin + 0.5, y + 1)
        p = 1.0 if progress is None else max(0.0, min(1.0, progress * len(keys) - i))
        if p > 0:
            kit.tick(fr, px, py, 13 * page.zoom, CRAN, max(3, int(1.9 * page.zoom)), p)

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
        kit.marker_strike(fr, a[0], a[1], b[0], (y1 - y0) * page.zoom * 1.3, CRAN, 165, seed + i, p)
    return len(hits)

def rowan_close(r):
    """Clues 10 and 11 are stated outright in the notebook: the last stall has two digits and is
    not on Rowan Close (28-36). Crossing those rows out shows real play without revealing any
    hidden evidence."""
    return r[5] < 10 or 28 <= r[5] <= 36

def log_clip(A, nrows=30):
    idx = A.log_page
    rows = CL.log_rows(A.L, idx)
    top = rows[0][0] - 22; bottom = rows[nrows - 1][1] + 2
    return idx, rows[:nrows], (40, top, 572, bottom)

# ---------------------------------------------------------------- the ten images
def m01_main(A):
    return P.hero_poster()

def m02_documents(A):
    f = lobby(2, "Six documents to study", "Map · stall directory · Book of Brews · moon log · reading book · ledger")
    docs = [("map", "Fair map"), ("directory", "Stall directory"), ("brews", "Book of Brews"),
            ("moon", "Moon-watcher’s log"), ("reading", "Reading book"), ("ledger", "Shop ledger")]
    lab = P.hf("oswald", 40, 600)
    for i, (k, label) in enumerate(docs):
        col, row = i % 3, i // 3
        cx, cy = 420 + col * 580, 555 + row * 650
        pg = A.page(k, 560)
        page_in(f, pg, cx, cy, angle=[1.5, -1, 1, -1.5, 1, -1][i])
        f.text((cx, cy + 290), label, lab, PARCH, anchor="ma")
    return f

def m03_map(A):
    f = lobby(3, "A map of the Moon Fair", "36 stalls · 4 lanes · 4 entrances · one apothecary")
    leg = A.L.doc[A.p["map"]].search_for("where the body was found")[0]
    clip = (54, 176, 558, leg.y1 + 12)
    h = 1290
    pg = A.L.image(A.p["map"], h, clip=clip)
    circle_shop(A.L, pg, A.p["map"])
    page_in(f, pg, 820, 901)
    note_card(f, "Where the\nbody was\nfound", 1640, 640, -6, w=400, h=360, size=64)
    d = f.draw()
    d.line([(1470, 640), (1250, 380)], fill=MUST, width=8)
    d.polygon([(1250, 380), (1290, 392), (1262, 420)], fill=MUST)
    return f

def m04_notebook(A):
    f = lobby(4, "The Inspector’s Notebook", "12 clues stated outright · 6 hidden in the documents")
    pidx = A.p["notebook"]
    words = A.L.words(pidx)
    yF = max(w[3] for w in words if w[4] == "F.")
    clip = (40, 70, 572, yF + 14)
    pg = A.L.image(pidx, int(1700 * (clip[3] - clip[1]) / (clip[2] - clip[0])), clip=clip)
    if pg.img.height > 1290:
        pg = A.L.image(pidx, 1290, clip=clip)
    tick_notebook(A.L, pg, pidx, [str(i) for i in range(1, 8)])
    page_in(f, pg, S / 2, 901, angle=-1)
    return f

def m05_log(A):
    f = lobby(5, "Cross out the innocent", "6,000 visitors in the Visitor Log")
    idx, rows, clip = log_clip(A, 30)
    zoom = 1640 / (clip[2] - clip[0])
    pg = A.L.image(idx, int((clip[3] - clip[1]) * zoom), clip=clip)
    if pg.img.height > 1290:
        pg = A.L.image(idx, 1290, clip=clip)
    strike_rows(pg, rows, rowan_close)
    fade = Image.new("L", pg.img.size, 0); fd = ImageDraw.Draw(fade)
    for yy in range(pg.img.height):                       # fade the lower rows into the card
        t = max(0.0, (yy - pg.img.height * 0.66) / (pg.img.height * 0.34))
        fd.line([(0, yy), (pg.img.width, yy)], fill=int(255 * min(1, t) * 0.9))
    pg.img = Image.composite(pg.img.filter(ImageFilter.GaussianBlur(5)), pg.img, fade.point(lambda v: min(255, v * 2)))
    veil = Image.new("RGBA", pg.img.size, PARCH + (255,)); veil.putalpha(fade); pg.img.alpha_composite(veil)
    page_in(f, pg, S / 2, 901)
    note_card(f, "Clues 10 & 11:\ntwo digits, not\nRowan Close", 1600, 1350, -6, w=500, h=340, size=60)
    return f

def m06_hints(A):
    f = lobby(6, "Stuck? Three levels of help", "Each level sits on its own pages, so no accidental spoilers")
    pidx = A.p["hint1"]
    words = A.L.words(pidx)
    yE = sorted(w[1] for w in words if w[4] == "Evidence")[0]
    clip = (40, 70, 572, yE + 150)
    pg = A.L.image(pidx, 1290, clip=clip)
    if pg.img.width > 1100:
        pg = A.L.image(pidx, int(1100 * (clip[3] - clip[1]) / (clip[2] - clip[0])), clip=clip)
    page_in(f, pg, 160 + pg.img.width / 2, 901, angle=-1)
    lab = P.hf("abril", 130)
    kit.envelope(f, (1340, 330, 1820, 720), 2, lab)
    kit.envelope(f, (1340, 900, 1820, 1290), 3, lab)
    sub = P.hf("oswald", 40, 600)
    f.text((1580, 740), "Level 2: a stronger push", sub, PARCH, anchor="ma")
    f.text((1580, 1310), "Level 3: nearly the answer", sub, PARCH, anchor="ma")
    return f

def m07_check(A):
    f = lobby(7, "Check your answer, no spoilers", "No names and no answers are printed in the case file")
    pidx = A.p["check"]
    r = CL.text_rect(A.L, pidx, "If your last three digits are")
    clip = (40, 70, 572, r.y0 - 30)
    pg = A.L.image(pidx, 1290, clip=clip)
    if pg.img.width > 1100:
        pg = A.L.image(pidx, int(1100 * (clip[3] - clip[1]) / (clip[2] - clip[0])), clip=clip)
    page_in(f, pg, 160 + pg.img.width / 2, 901, angle=-1.5)
    kit.envelope(f, (1360, 520, 1820, 860), "?", P.hf("abril", 110))
    f.text((1590, 900), "Digits match?", P.hf("abril", 64), MUST, anchor="ma")
    f.text((1590, 990), "Open the", P.hf("oswald", 52, 500), PARCH, anchor="ma")
    f.text((1590, 1056), "solution file", P.hf("oswald", 52, 500), PARCH, anchor="ma")
    return f

def m08_print_ipad(A):
    f = lobby(8, "Print it or play on iPad", "US Letter · A4 · iPad (Goodnotes, Notability)")
    pg = A.page("brews", 1220)
    page_in(f, pg, 600, 901, angle=2)
    ih = 1180; iw = ih * 0.766
    scr = A.I.image(A.ip["notebook"], int(ih * 0.91))
    tick_notebook(A.I, scr, A.ip["notebook"], [str(i) for i in range(1, 7)])
    tab = kit.Frame(int(iw) + 60, int(ih) + 60, PARCH_DARK)
    tab.img = Image.new("RGBA", tab.img.size, (0, 0, 0, 0))
    kit.ipad(tab, (30, 30, 30 + iw, 30 + ih), scr)
    f.paste(tab.img, 1420, 901, angle=0)
    f.sources += tab.sources
    return f

def m09_who(A):
    f = lobby(9, "Solo or date night", "Spooky, not gory: a cozy witch-village mystery")
    pg = A.page("howto", 1250)
    page_in(f, pg, 1390, 901, angle=1.5)
    d = f.draw()
    rows = [("1–4 players", "solo, a pair or a team"), ("90–150 min", "one cozy evening"),
            ("Print or iPad", "pencil or Apple Pencil")]
    y = 330
    for i, (big, small) in enumerate(rows):
        cx = 260
        if i == 0:
            kit.people(f, cx, y + 120, 140, 3, PARCH)
        elif i == 1:
            kit.clock(f, cx, y + 90, 80, PARCH, GREEN, MUST)
        else:
            P.cauldron(f.img, cx, y + 170, 70, steam=1.2)
        f.text((370, y + 30), big, P.hf("abril", 76), MUST)
        f.text((372, y + 140), small, P.hf("oswald", 44, 400), PARCH)
        y += 400
    return f

def m10_get(A):
    f = kit.Frame(S, S, P.PLUM); img = f.img
    P.gradient(img, P.NIGHT, P.AUB)
    P.halftone(img, (0, 0, S, S), P.AMETHYST + (40,), 30, falloff=lambda x, y: 0.6)
    P.tracked(f, S / 2, 92, "QUIETCLUECO PRESENTS", P.hf("cinzel", 46, 700), PARCH, 12)
    big = P.hf("abril", 190)
    P.title_word(f, "What you get", S / 2, 160, big, depth=16, k=1.4)
    lab = font("black", 50); bf = font("black", 32)
    cards = [("US Letter", A.L.image(0, 520)), ("A4", A.A4.image(0, 520)), ("iPad", A.I.image(0, 520))]
    x = 110
    for label, thumb in cards:
        kit.pdf_file_card(f, (x, 470, x + 400, 1040), thumb, label, lab, "PDF", bf)
        x += 450
    kit.pdf_file_card(f, (x, 470, x + 400, 1040), None, "Solution", lab, "PDF", bf)
    kit.envelope(f, (x + 60, 570, x + 340, 780), "?", P.hf("abril", 70))
    rules = A.page("rules", 700)
    f.paste_page(rules, 520, 1490, angle=-2)
    f.text((520, 1868), "House rules: every term defined", P.hf("oswald", 46, 600), PARCH, anchor="ma")
    d = f.draw()
    cx, cy, r = 1420, 1480, 360
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=MUST)
    d.ellipse([cx - r + 22, cy - r + 22, cx + r - 22, cy + r - 22], outline=P.PLUM, width=8)
    f.text((cx, cy - 200), "Exactly\none answer", P.hf("abril", 104), P.PLUM, anchor="ma", align="center")
    f.text((cx, cy + 82), "checked by code", P.hf("oswald", 62, 600), P.PLUM, anchor="ma")
    kit.tick(f, cx - 50, cy + 250, 100, P.PLUM, 14)
    P.deco_frame(f, 36, 1.5)
    P.aged(img, 7, border=24)
    return f

MOCKUPS = [("01-main", m01_main), ("02-six-documents", m02_documents), ("03-fair-map", m03_map),
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
        path = os.path.join(outdir, f"{CL.SLUG}_{name}.jpg")
        fr.img.convert("RGB").save(path, quality=90, optimize=True, progressive=True)
        results.append(dict(name=name, path=path, sources=fr.sources,
                            hits=kit.spoiler_scan(fr.sources, A.bad)))
        thumbs.append(fr.img.convert("RGB").resize((380, 380), Image.LANCZOS))
    g = 24; W = 5 * 380 + 6 * g; H = 2 * 380 + 3 * g + 90
    sheet = Image.new("RGB", (W, H), GREEN)
    d = ImageDraw.Draw(sheet)
    d.text((W / 2, 20), "Full Moon over Morrowmere — listing images 1–10", font=P.hf("abril", 48), fill=PARCH, anchor="ma")
    for i, t in enumerate(thumbs):
        sheet.paste(t, (g + (i % 5) * (380 + g), 90 + g + (i // 5) * (380 + g)))
        d.text((g + (i % 5) * (380 + g) + 14, 90 + g + (i // 5) * (380 + g) + 10), str(i + 1),
               font=font("black", 40), fill=MUST)
    sheet_path = os.path.join(outdir, f"{CL.SLUG}_overview.jpg")
    sheet.save(sheet_path, quality=88, optimize=True)
    return results, sheet_path, A

if __name__ == "__main__":
    res, sheet, A = build(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mockups"))
    for r in res:
        print(r["name"], len(r["sources"]), "sources", len(r["hits"]), "hits", os.path.getsize(r["path"]) // 1024, "KB")
