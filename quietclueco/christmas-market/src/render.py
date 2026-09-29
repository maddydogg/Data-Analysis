"""Render Snowfall at Ember Square to PDF: the case book (print Letter, print A4, iPad)
and the solution file (the Envelope) in the same three formats. All graphics are drawn
with code: no photos, no generated images."""
import csv, math, os, random
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.pagesizes import LETTER, A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import case as C
import hints as H

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")

# ------------------------------------------------------------------ brand
GREEN = HexColor("#24382F"); CRAN = HexColor("#9E2B3A"); PARCH = HexColor("#F4EDE0")
MUST = HexColor("#D6A441"); INK = HexColor("#1E1B18"); WHITE = HexColor("#FFFFFF")
PALE = HexColor("#FBF8F2")      # zebra rows: a whisper of parchment, cheap to print
RULE = HexColor("#D9CFBE"); SOFT = HexColor("#6B6259"); RIVER = HexColor("#DCE7EA")
RIVER_EDGE = HexColor("#9DB7BE")

def register_fonts():
    for name, f in [("Fraunces", "Fraunces-Regular"), ("Fraunces-SemiBold", "Fraunces-SemiBold"),
                    ("Fraunces-Bold", "Fraunces-Bold"), ("Fraunces-Italic", "Fraunces-Italic"),
                    ("Nunito", "Nunito-Regular"), ("Nunito-Bold", "Nunito-Bold"),
                    ("Nunito-ExtraBold", "Nunito-ExtraBold"), ("Nunito-Italic", "Nunito-Italic"),
                    ("Caveat", "Caveat-Medium"), ("Courier Prime", "CourierPrime-Regular"),
                    ("Courier Prime-Bold", "CourierPrime-Bold")]:
        pdfmetrics.registerFont(TTFont(name, os.path.join(FONTS, f + ".ttf")))
    addMapping("Nunito", 0, 0, "Nunito"); addMapping("Nunito", 1, 0, "Nunito-Bold")
    addMapping("Nunito", 0, 1, "Nunito-Italic"); addMapping("Nunito", 1, 1, "Nunito-Bold")
    addMapping("Fraunces", 0, 0, "Fraunces"); addMapping("Fraunces", 1, 0, "Fraunces-SemiBold")
    addMapping("Fraunces", 0, 1, "Fraunces-Italic"); addMapping("Fraunces", 1, 1, "Fraunces-SemiBold")
    addMapping("Courier Prime", 0, 0, "Courier Prime"); addMapping("Courier Prime", 1, 0, "Courier Prime-Bold")

IPAD = (768, 1024)  # 3:4 portrait, fits Goodnotes / Notability page templates
FORMATS = {"letter": LETTER, "a4": A4, "ipad": IPAD}

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

class L:
    """Layout context for one format."""
    def __init__(self, fmt):
        self.fmt = fmt
        self.W, self.H = FORMATS[fmt]
        self.ipad = fmt == "ipad"
        self.m = 48 if self.ipad else 54
        self.s = 1.22 if self.ipad else 1.0          # text scale
        self.cw = self.W - 2 * self.m
        self.top = self.H - self.m - 26              # below running header
        self.bottom = self.m + 18
        s = self.s
        self.body = ParagraphStyle("body", fontName="Nunito", fontSize=10.5 * s,
                                   leading=15.2 * s, textColor=INK, spaceAfter=6 * s)
        self.small = ParagraphStyle("small", parent=self.body, fontSize=9 * s, leading=12.5 * s)
        self.h1 = ParagraphStyle("h1", fontName="Fraunces-SemiBold", fontSize=26 * s,
                                 leading=31 * s, textColor=GREEN, spaceAfter=4 * s)
        self.h2 = ParagraphStyle("h2", fontName="Fraunces-SemiBold", fontSize=15 * s,
                                 leading=19 * s, textColor=GREEN, spaceAfter=3 * s)
        self.kicker = ParagraphStyle("kick", fontName="Nunito-ExtraBold", fontSize=8.5 * s,
                                     leading=11 * s, textColor=CRAN)

def para(c, text, x, y, w, style):
    """Draw a paragraph with its top at y; return the y below it."""
    p = Paragraph(text, style)
    _, h = p.wrap(w, 10000)
    p.drawOn(c, x, y - h)
    return y - h - style.spaceAfter

def para_h(text, w, style):
    return Paragraph(text, style).wrap(w, 10000)[1] + style.spaceAfter

# ------------------------------------------------------------------ small drawn icons
def snowflake(c, x, y, r, col=WHITE, lw=0.8):
    c.saveState(); c.setStrokeColor(col); c.setLineWidth(lw); c.setLineCap(1)
    for k in range(6):
        a = math.pi / 3 * k
        dx, dy = math.cos(a) * r, math.sin(a) * r
        c.line(x, y, x + dx, y + dy)
        for f in (0.55,):
            bx, by = x + dx * f, y + dy * f
            for s in (-1, 1):
                b = a + s * math.pi / 4
                c.line(bx, by, bx + math.cos(b) * r * 0.32, by + math.sin(b) * r * 0.32)
    c.restoreState()

def fir(c, x, y, w, h, col=GREEN, star=MUST):
    c.saveState(); c.setFillColor(col); c.setStrokeColor(col)
    tiers = 3
    for i in range(tiers):
        tw = w * (1 - i * 0.24); ty = y + h * 0.12 + i * h * 0.25
        p = c.beginPath(); p.moveTo(x - tw / 2, ty); p.lineTo(x + tw / 2, ty)
        p.lineTo(x, ty + h * 0.42); p.close(); c.drawPath(p, fill=1, stroke=0)
    c.setFillColor(HexColor("#5A3E2B")); c.rect(x - w * 0.06, y, w * 0.12, h * 0.13, fill=1, stroke=0)
    if star:
        star5(c, x, y + h * 0.98, h * 0.08, star)
    c.restoreState()

def star5(c, x, y, r, col):
    c.saveState(); c.setFillColor(col)
    p = c.beginPath()
    for i in range(10):
        a = math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        (p.moveTo if i == 0 else p.lineTo)(x + math.cos(a) * rr, y + math.sin(a) * rr)
    p.close(); c.drawPath(p, fill=1, stroke=0); c.restoreState()

def stall_icon(c, x, y, w, h, num, awning=CRAN, font=7):
    c.saveState()
    c.setFillColor(WHITE); c.setStrokeColor(INK); c.setLineWidth(0.6)
    c.rect(x, y, w, h, fill=1, stroke=1)
    ah = h * 0.32; stripes = 4
    for i in range(stripes):
        c.setFillColor(awning if i % 2 == 0 else WHITE)
        c.rect(x + i * w / stripes, y + h - ah, w / stripes, ah, fill=1, stroke=0)
    c.setStrokeColor(INK); c.rect(x, y + h - ah, w, ah, fill=0, stroke=1)
    c.setFillColor(INK); c.setFont("Nunito-ExtraBold", font)
    c.drawCentredString(x + w / 2, y + (h - ah) / 2 - font * 0.35, str(num))
    c.restoreState()

def lights(c, x0, x1, y, sag, n, cols=(MUST, CRAN, PARCH)):
    c.saveState(); c.setStrokeColor(HexColor("#101A15")); c.setLineWidth(0.8)
    pts = [(x0 + (x1 - x0) * t / 40, y - sag * math.sin(math.pi * t / 40)) for t in range(41)]
    p = c.beginPath(); p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    c.drawPath(p, fill=0, stroke=1)
    for i in range(1, n):
        t = i / n; xx = x0 + (x1 - x0) * t; yy = y - sag * math.sin(math.pi * t)
        c.setFillColor(cols[i % len(cols)]); c.circle(xx, yy - 4, 3.2, fill=1, stroke=0)
    c.restoreState()

def checkbox(c, x, y, s, col=GREEN):
    c.saveState(); c.setStrokeColor(col); c.setLineWidth(0.9); c.roundRect(x, y, s, s, 2, fill=0, stroke=1)
    c.restoreState()

# ------------------------------------------------------------------ page chrome
class Book:
    def __init__(self, fmt, path, title):
        self.L = L(fmt)
        self.c = canvas.Canvas(path, pagesize=(self.L.W, self.L.H))
        self.c.setTitle(title); self.c.setAuthor(C.BRAND); self.c.setSubject(C.SUBTITLE)
        self.c.setCreator(f"{C.BRAND} generator"); self.page = 0

    def new_page(self, key=None, header=None, outline=None, level=0, chrome=True):
        if self.page:
            self.c.showPage()
        self.page += 1
        if key:
            self.c.bookmarkPage(key)
        if outline:
            self.c.addOutlineEntry(outline, key, level=level, closed=level == 0 and False)
        if chrome:
            self.chrome(header)

    def chrome(self, header):
        c, Lx = self.c, self.L
        c.setFillColor(GREEN); c.setFont("Fraunces-Italic", 9.5 * Lx.s)
        c.drawString(Lx.m, Lx.H - Lx.m + 2, C.TITLE)
        if header:
            c.setFont("Nunito-Bold", 8.5 * Lx.s); c.setFillColor(CRAN)
            c.drawRightString(Lx.W - Lx.m, Lx.H - Lx.m + 2, header.upper())
        c.setStrokeColor(MUST); c.setLineWidth(1)
        c.line(Lx.m, Lx.H - Lx.m - 6, Lx.W - Lx.m, Lx.H - Lx.m - 6)
        c.setFont("Nunito", 8 * Lx.s); c.setFillColor(SOFT)
        c.drawCentredString(Lx.W / 2, Lx.m - 14, str(self.page))
        c.drawRightString(Lx.W - Lx.m, Lx.m - 14, C.BRAND)
        snowflake(c, Lx.m + 4, Lx.m - 11, 4, MUST, 0.6)

    def title_block(self, kicker, title, y=None):
        Lx = self.L; y = y or Lx.top
        y = para(self.c, esc(kicker.upper()), Lx.m, y, Lx.cw, Lx.kicker)
        return para(self.c, esc(title), Lx.m, y - 2, Lx.cw, Lx.h1)

    def link(self, key, x0, y0, x1, y1):
        self.c.linkAbsolute("", key, (x0, y0, x1, y1), thickness=0)

    def save(self):
        self.c.showPage(); self.c.save()

# ------------------------------------------------------------------ data
def load_rows():
    rows = []
    with open(os.path.join(HERE, "data", "visitor_log.csv")) as f:
        for r in csv.DictReader(f):
            rows.append(dict(entry=C.tmin(r["entry"]), ticket=int(r["ticket"]), first=r["first"],
                             last=r["last"], town=r["town"], gate=r["gate"], stall=int(r["stall"])))
    return rows

def log_items(rows):
    items, hour = [], None
    for r in rows:
        h = r["entry"] // 60
        if h != hour:
            hour = h; items.append(("band", h))
        items.append(("rec", r))
    return items

LOG_COLS = [("Entry", 44), ("Ticket", 44), ("First name", 80), ("Surname", 92),
            ("Home town", 96), ("Gate", 50), ("Last stall", 52), ("", 22)]

def log_geometry(Lx):
    rh = 13.2 if Lx.ipad else 11.3
    avail = Lx.top - 40 - Lx.bottom
    return rh, int(avail // rh) - 1

def paginate_log(rows, Lx):
    rh, per = log_geometry(Lx)
    items = log_items(rows)
    pages = []
    i = 0
    while i < len(items):
        chunk = items[i:i + per]
        if chunk and chunk[-1][0] == "band":   # never end a page on a chapter band
            chunk = chunk[:-1]
        pages.append(chunk); i += len(chunk)
    return pages

# ------------------------------------------------------------------ the case book
def book_plan(rows, Lx):
    """List of (key, toc_title, level, draw_fn). Built before drawing so the contents
    page knows every page number."""
    log_pages = paginate_log(rows, Lx)
    plan = [("cover", None, 0, draw_cover), ("howto", "How to play", 0, draw_howto),
            ("contents", "Contents", 0, draw_contents), ("case", "The case", 0, draw_case),
            ("rules", "House rules", 0, draw_rules),
            ("map", "Evidence 1 — Market map", 0, draw_map),
            ("directory", "Evidence 2 — Stall directory", 0, draw_directory),
            ("receipt", "Evidence 3 — The receipt & Pip’s note", 0, draw_receipt_note),
            ("weather", "Evidence 4 — Weather log", 0, draw_weather),
            ("coach", "Evidence 5 — Coach timetable", 0, draw_coach),
            ("statements", "Evidence 6 — Witness statements", 0, draw_statements),
            ("notebook", "The Inspector’s Notebook", 0, draw_notebook),
            ("logintro", "The Visitor Log", 0, draw_log_intro)]
    seen = set()
    for i, chunk in enumerate(log_pages):
        bands = [it[1] for it in chunk if it[0] == "band"]
        key, title = f"log{i}", None
        for h in bands:
            if h not in seen:
                seen.add(h); title = f"{h:02d}:00–{h:02d}:59"
        plan.append((key, title, 1 if title else None,
                     (lambda b, chunk=chunk: draw_log_page(b, chunk))))
    plan += [("notes", "Detective’s notes", 0, draw_notes),
             ("check", "The Sealed Check", 0, draw_check),
             ("hintstop", "Hints", 0, draw_hint_stop)]
    per_level = hint_pages(Lx)
    for lv in range(3):
        for j, chunk in enumerate(per_level[lv]):
            plan.append((f"hint{lv}_{j}", H.LEVEL_NAMES[lv] if j == 0 else None, 1 if j == 0 else None,
                         (lambda b, lv=lv, chunk=chunk, j=j: draw_hint_page(b, lv, chunk, j))))
    plan.append(("thanks", "Thank you", 0, draw_thanks))
    return plan

def build_book(fmt, path):
    rows = load_rows()
    b = Book(fmt, path, f"{C.TITLE} — {C.SUBTITLE}")
    b.rows = rows
    b.seal = b_seal(C.KILLER)
    plan = book_plan(rows, b.L)
    b.plan = plan
    b.pageno = {key: i + 1 for i, (key, *_rest) in enumerate(plan)}
    for key, title, level, fn in plan:
        chrome = key != "cover"
        header = section_header(key)
        b.new_page(key, header, title if (title and level is not None) else None,
                   level or 0, chrome=chrome)
        fn(b)
    b.save()
    return b.page

def section_header(key):
    if key.startswith("log"):
        return "Visitor Log"
    if key.startswith("hint"):
        return "Hints"
    return {"howto": "Before you begin", "contents": "Contents", "case": "The case",
            "rules": "House rules", "map": "Evidence 1", "directory": "Evidence 2",
            "receipt": "Evidence 3", "weather": "Evidence 4", "coach": "Evidence 5",
            "statements": "Evidence 6", "notebook": "Clues", "notes": "Notes",
            "check": "Check your answer", "thanks": ""}.get(key, "")

# ---- cover
def draw_cover(b):
    c, Lx = b.c, b.L; W, H = Lx.W, Lx.H
    c.setFillColor(GREEN); c.rect(0, 0, W, H, fill=1, stroke=0)
    rng = random.Random(7)
    for _ in range(70):
        x, y = rng.uniform(0, W), rng.uniform(H * 0.28, H)
        snowflake(c, x, y, rng.uniform(2, 7), Color(0.96, 0.93, 0.88, alpha=rng.uniform(0.25, 0.8)),
                  rng.uniform(0.5, 1.1))
    lights(c, -10, W + 10, H - 40, 34, 18)
    # skyline of stalls
    base = H * 0.14
    c.setFillColor(HexColor("#18261F")); c.rect(0, 0, W, base, fill=1, stroke=0)
    x = -10
    while x < W:
        sw = rng.uniform(58, 86); sh = rng.uniform(50, 70)
        c.setFillColor(HexColor("#1A2B23")); c.rect(x, base, sw, sh, fill=1, stroke=0)
        p = c.beginPath(); p.moveTo(x - 6, base + sh); p.lineTo(x + sw / 2, base + sh + 26)
        p.lineTo(x + sw + 6, base + sh); p.close(); c.drawPath(p, fill=1, stroke=0)
        for i in range(5):
            c.setFillColor(CRAN if i % 2 == 0 else PARCH)
            c.rect(x + i * sw / 5, base + sh - 12, sw / 5, 12, fill=1, stroke=0)
        c.setFillColor(HexColor("#F3C969")); c.rect(x + sw * 0.3, base + 10, sw * 0.4, sh * 0.35, fill=1, stroke=0)
        x += sw + rng.uniform(8, 20)
    fir(c, W * 0.5, base - 4, W * 0.36, H * 0.34, col=HexColor("#0F1B15"), star=MUST)
    # title panel
    pw, ph = W * 0.78, H * 0.36
    px, py = (W - pw) / 2, H * 0.48
    c.setFillColor(PARCH); c.roundRect(px, py, pw, ph, 14, fill=1, stroke=0)
    c.setStrokeColor(MUST); c.setLineWidth(2); c.roundRect(px + 7, py + 7, pw - 14, ph - 14, 10, fill=0, stroke=1)
    s = W / 612
    c.setFillColor(CRAN); c.setFont("Nunito-ExtraBold", 10 * s)
    c.drawCentredString(W / 2, py + ph - 34 * s, "A COZY MURDER MYSTERY LOGIC PUZZLE")
    c.setFillColor(GREEN); c.setFont("Fraunces-SemiBold", 44 * s)
    c.drawCentredString(W / 2, py + ph - 88 * s, "Snowfall at")
    c.drawCentredString(W / 2, py + ph - 136 * s, "Ember Square")
    c.setFont("Fraunces-Italic", 15 * s); c.setFillColor(INK)
    c.drawCentredString(W / 2, py + ph - 166 * s, C.SUBTITLE)
    c.setStrokeColor(MUST); c.setLineWidth(1.2)
    c.line(W / 2 - 90 * s, py + ph - 180 * s, W / 2 + 90 * s, py + ph - 180 * s)
    c.setFont("Nunito-Bold", 13 * s); c.setFillColor(GREEN)
    c.drawCentredString(W / 2, py + 44 * s, C.TAGLINE)
    c.setFont("Nunito", 10.5 * s); c.setFillColor(SOFT)
    c.drawCentredString(W / 2, py + 25 * s, f"Solo or together · {C.PLAYERS} · {C.PLAYTIME}")
    # brand
    c.setFillColor(PARCH); c.setFont("Fraunces-SemiBold", 16 * s)
    c.drawCentredString(W / 2, 30 * s, C.BRAND)
    c.setFont("Nunito", 8 * s); c.drawCentredString(W / 2, 17 * s, "Printable case file · Case No. 1")

# ---- how to play
def draw_howto(b):
    c, Lx = b.c, b.L
    y = b.title_block("Before you begin", "How to play")
    for head, text in C.HOW_TO_PLAY:
        y = para(c, f"<font name='Nunito-ExtraBold' color='#9E2B3A'>{esc(head)}.</font> {esc(text)}",
                 Lx.m, y, Lx.cw, Lx.body)
    y -= 6
    box_h = 70 * Lx.s
    c.setFillColor(PARCH); c.roundRect(Lx.m, y - box_h, Lx.cw, box_h, 8, fill=1, stroke=0)
    t = ("<b>Printing tip.</b> Inside pages are mostly white to save ink. Print the Visitor Log "
         "single- or double-sided, black and white is fine. The evidence pages look best in colour. "
         "On a tablet, use the contents page or the bookmarks to jump around, and highlight "
         "visitors as you rule them out.")
    para(c, t, Lx.m + 12, y - 10, Lx.cw - 24, Lx.small)

# ---- contents
def draw_contents(b):
    c, Lx = b.c, b.L
    y = b.title_block("Case file", "Contents")
    lines = [(k, t, lv) for k, t, lv, _ in b.plan if t and lv is not None and k not in ("contents",)]
    st = Lx.body
    for k, t, lv in lines:
        ind = 18 * Lx.s if lv == 1 else 0
        fs = (9.5 if lv == 1 else 11.5) * Lx.s
        font = "Nunito" if lv == 1 else "Nunito-Bold"
        c.setFont(font, fs); c.setFillColor(INK if lv == 0 else SOFT)
        label = t if lv == 0 else ("Visitor Log, " + t if k.startswith("log") else t)
        c.drawString(Lx.m + ind, y - fs, label)
        c.drawRightString(Lx.W - Lx.m, y - fs, str(b.pageno[k]))
        tw = pdfmetrics.stringWidth(label, font, fs)
        c.setStrokeColor(RULE); c.setDash(1, 2)
        c.line(Lx.m + ind + tw + 6, y - fs + 2, Lx.W - Lx.m - 28, y - fs + 2); c.setDash()
        b.link(k, Lx.m, y - fs - 3, Lx.W - Lx.m, y + 2)
        y -= fs * (1.55 if lv == 0 else 1.45)
    c.setFont("Nunito-Italic", 8.5 * Lx.s); c.setFillColor(SOFT)
    c.drawString(Lx.m, Lx.bottom, "Tap any line to jump to that page. The hint pages are at the back.")

# ---- case
def draw_case(b):
    c, Lx = b.c, b.L
    y = b.title_block("Emberfield Constabulary · 23 December", "The case")
    for p in C.INTRO:
        y = para(c, esc(p), Lx.m, y, Lx.cw, Lx.body)
    y = para(c, "What we know for certain", Lx.m, y - 6, Lx.cw, Lx.h2)
    for f in C.KNOWN_FACTS:
        c.setFillColor(CRAN); c.circle(Lx.m + 4, y - 7 * Lx.s, 2.2, fill=1, stroke=0)
        y = para(c, esc(f), Lx.m + 14, y, Lx.cw - 14, Lx.body)

# ---- rules
def draw_rules(b):
    c, Lx = b.c, b.L
    y = b.title_block("Read these once", "House rules")
    y = para(c, "Every clue in this case uses the words below in exactly this sense. If a clue "
                "seems to have two meanings, this page decides.", Lx.m, y, Lx.cw, Lx.body)
    y -= 6
    for term, text in C.GLOSSARY:
        c.setFillColor(GREEN); c.setFont("Fraunces-SemiBold", 12 * Lx.s)
        c.drawString(Lx.m, y - 12 * Lx.s, term)
        y2 = para(c, esc(text), Lx.m + 110 * Lx.s, y, Lx.cw - 110 * Lx.s, Lx.body)
        y = min(y2, y - 20 * Lx.s) - 4
        c.setStrokeColor(RULE); c.setLineWidth(0.5); c.line(Lx.m, y + 2, Lx.W - Lx.m, y + 2)
        y -= 6

# ---- evidence 1: the map
def draw_map(b):
    c, Lx = b.c, b.L
    y = b.title_block("Evidence 1", "Market map")
    y = para(c, "Ember Square on the night of 23 December. North is at the top. Stalls are numbered; "
                "the stall directory (Evidence 2) says what each one sells.", Lx.m, y, Lx.cw, Lx.small)
    # geometry: fit a square-ish map in the remaining space
    legend_h = 70 * Lx.s
    avail_h = y - Lx.bottom - legend_h
    size = min(Lx.cw, avail_h)
    ox = Lx.m + (Lx.cw - size) / 2; oy = y - size
    u = size / 100.0     # map units
    river = 7 * u; wall_l, wall_b = ox + 9 * u, oy + 12 * u
    wall_r, wall_t = ox + size - river - 3 * u, oy + size - 7 * u
    # river along east and south
    c.setFillColor(RIVER); c.setStrokeColor(RIVER_EDGE); c.setLineWidth(0.8)
    p = c.beginPath()
    p.moveTo(ox + size - river, oy + size); p.lineTo(ox + size, oy + size); p.lineTo(ox + size, oy)
    p.lineTo(ox, oy); p.lineTo(ox, oy + river); p.lineTo(ox + size - river, oy + river); p.close()
    c.drawPath(p, fill=1, stroke=1)
    c.setFillColor(RIVER_EDGE); c.setFont("Fraunces-Italic", 8 * Lx.s)
    c.drawString(ox + 3 * u, oy + 2.2 * u, "River Ember")
    c.saveState(); c.translate(ox + size - 2.3 * u, oy + size * 0.78); c.rotate(-90)
    c.drawString(0, 0, "River Ember"); c.restoreState()
    # square wall
    c.setFillColor(HexColor("#FFFFFF")); c.setStrokeColor(GREEN); c.setLineWidth(2.2)
    c.rect(wall_l, wall_b, wall_r - wall_l, wall_t - wall_b, fill=1, stroke=1)
    cx, cyy = (wall_l + wall_r) / 2, (wall_b + wall_t) / 2
    gate_w = 8 * u
    def gate(x, y, vertical, name):
        c.setFillColor(WHITE); c.setStrokeColor(WHITE); c.setLineWidth(3.2)
        if vertical:
            c.line(x, y - gate_w / 2, x, y + gate_w / 2)
        else:
            c.line(x - gate_w / 2, y, x + gate_w / 2, y)
        c.setFillColor(CRAN)
        for dx, dy in ([(0, -gate_w / 2), (0, gate_w / 2)] if vertical else [(-gate_w / 2, 0), (gate_w / 2, 0)]):
            c.circle(x + dx, y + dy, 1.4 * u, fill=1, stroke=0)
    gate(cx, wall_t, False, "North"); gate(cx, wall_b, False, "South")
    gate(wall_l, cyy, True, "West"); gate(wall_r, cyy, True, "East")
    # footbridges (East and South only)
    c.setFillColor(HexColor("#B08A5B")); c.setStrokeColor(HexColor("#6E5335")); c.setLineWidth(0.8)
    c.rect(wall_r, cyy - 2.6 * u, (ox + size) - wall_r, 5.2 * u, fill=1, stroke=1)
    c.rect(cx - 2.6 * u, oy, 5.2 * u, wall_b - oy, fill=1, stroke=1)
    for i in range(1, 6):
        xx = wall_r + ((ox + size) - wall_r) * i / 6
        c.line(xx, cyy - 2.6 * u, xx, cyy + 2.6 * u)
        yy = oy + (wall_b - oy) * i / 6
        c.line(cx - 2.6 * u, yy, cx + 2.6 * u, yy)
    # roads (North and West)
    c.setFillColor(HexColor("#E6E0D6")); c.setStrokeColor(RULE)
    c.rect(cx - 3 * u, wall_t, 6 * u, oy + size - wall_t, fill=1, stroke=0)
    c.rect(ox, cyy - 3 * u, wall_l - ox, 6 * u, fill=1, stroke=0)
    c.setFillColor(SOFT); c.setFont("Nunito-Italic", 7 * Lx.s)
    c.drawCentredString(cx, oy + size + 1.4 * u, "to Castle Road")
    c.saveState(); c.translate(ox + 3 * u, cyy + 5 * u); c.rotate(90)
    c.drawString(0, 0, "to Mill Lane"); c.restoreState()
    # gate labels
    c.setFillColor(GREEN); c.setFont("Nunito-ExtraBold", 7.5 * Lx.s)
    c.drawCentredString(cx - 13 * u, wall_t + 2 * u, "NORTH GATE")
    c.drawRightString(cx - 4.5 * u, wall_b - 3.8 * u, "SOUTH GATE")
    c.saveState(); c.translate(wall_l - 2 * u, cyy - 14 * u); c.rotate(90)
    c.drawCentredString(0, 0, "WEST GATE"); c.restoreState()
    c.saveState(); c.translate(wall_r + 2.2 * u, cyy + 14 * u); c.rotate(-90)
    c.drawCentredString(0, 0, "EAST GATE"); c.restoreState()
    c.setFont("Nunito-Italic", 6.5 * Lx.s); c.setFillColor(HexColor("#6E5335"))
    c.saveState(); c.translate(ox + size - river / 2 + 1.2 * u, cyy - 4 * u); c.rotate(-90)
    c.drawString(0, 0, "footbridge"); c.restoreState()
    c.drawString(cx + 3.6 * u, oy + 2.6 * u, "footbridge")
    # stall rows
    inner_w = wall_r - wall_l - 6 * u
    sw = inner_w / 9 * 0.84; gap = inner_w / 9 * 0.16
    sh = 6.2 * u
    rows_y = [wall_t - 4 * u - sh, wall_t - 17 * u - sh, cyy - 12 * u - sh, cyy - 25 * u - sh]
    for li, lane in enumerate(C.LANES):
        ry = rows_y[li]
        for k in range(9):
            num = li * 9 + k + 1
            sx = wall_l + 3 * u + k * (sw + gap) + gap / 2
            stall_icon(c, sx, ry, sw, sh, num, CRAN if li % 2 == 0 else GREEN, font=7.5 * Lx.s)
        c.setFillColor(CRAN); c.setFont("Fraunces-SemiBold", 8.5 * Lx.s)
        c.drawCentredString(cx, ry - 3.6 * u, lane.upper())
    # centre square: Great Fir, Bandstand, Judges' Tent, carousel near South Gate
    fir(c, cx, cyy - 6 * u, 10 * u, 13 * u, GREEN, MUST)
    c.setFillColor(INK); c.setFont("Nunito-Bold", 7 * Lx.s)
    c.drawCentredString(cx, cyy - 8.4 * u, "Great Fir")
    bx = wall_l + 16 * u
    c.setFillColor(PARCH); c.setStrokeColor(GREEN); c.setLineWidth(1)
    c.circle(bx, cyy, 4.2 * u, fill=1, stroke=1)
    c.setFillColor(INK); c.drawCentredString(bx, cyy - 7 * u, "Bandstand")
    tx = wall_r - 18 * u
    p = c.beginPath(); p.moveTo(tx - 6 * u, cyy - 3 * u); p.lineTo(tx + 6 * u, cyy - 3 * u)
    p.lineTo(tx, cyy + 4 * u); p.close()
    c.setFillColor(WHITE); c.setStrokeColor(CRAN); c.setLineWidth(1.3); c.drawPath(p, fill=1, stroke=1)
    c.setStrokeColor(CRAN); c.setLineWidth(1.6)
    c.line(tx - 1.6 * u, cyy - 1.8 * u, tx + 1.6 * u, cyy + 1.4 * u)
    c.line(tx - 1.6 * u, cyy + 1.4 * u, tx + 1.6 * u, cyy - 1.8 * u)
    c.setFillColor(CRAN); c.setFont("Nunito-Bold", 7 * Lx.s)
    c.drawCentredString(tx, cyy - 6.5 * u, "Judges’ Tent")
    # carousel just inside the South Gate, west of the path
    kx, ky = cx - 17 * u, wall_b + 4.6 * u
    c.setFillColor(PARCH); c.setStrokeColor(MUST); c.setLineWidth(1.2)
    c.circle(kx, ky, 3.6 * u, fill=1, stroke=1)
    for i in range(8):
        a = math.pi / 4 * i
        c.line(kx, ky, kx + math.cos(a) * 3.6 * u, ky + math.sin(a) * 3.6 * u)
    c.setFillColor(INK); c.setFont("Nunito-Bold", 7 * Lx.s)
    c.drawRightString(kx - 4.6 * u, ky - 1 * u, "Carousel")
    # market stop (coach) outside North Gate
    c.setFillColor(GREEN); c.roundRect(cx + 4 * u, wall_t + 1.2 * u, 12 * u, 3.4 * u, 1 * u, fill=1, stroke=0)
    c.setFillColor(WHITE); c.setFont("Nunito-ExtraBold", 6 * Lx.s)
    c.drawCentredString(cx + 10 * u, wall_t + 2.3 * u, "MARKET STOP")
    # compass
    qx, qy = ox + 4 * u, oy + size - 5 * u
    c.setFillColor(GREEN); p = c.beginPath(); p.moveTo(qx, qy + 4 * u); p.lineTo(qx - 1.4 * u, qy)
    p.lineTo(qx + 1.4 * u, qy); p.close(); c.drawPath(p, fill=1, stroke=0)
    c.setFont("Nunito-ExtraBold", 7 * Lx.s); c.drawCentredString(qx, qy - 3 * u, "N")
    # legend
    ly = oy - 14 * Lx.s
    items = [("stall", "Stall (number)"), ("bridge", "Footbridge over the river"),
             ("gate", "Gate"), ("tent", "Judges’ Tent, where the body was found")]
    lx = Lx.m; c.setFont("Nunito", 8 * Lx.s)
    for kind, text in items:
        if kind == "stall":
            stall_icon(c, lx, ly - 8, 14, 11, "", CRAN, 5)
        elif kind == "bridge":
            c.setFillColor(HexColor("#B08A5B")); c.rect(lx, ly - 6, 14, 6, fill=1, stroke=0)
        elif kind == "gate":
            c.setFillColor(CRAN); c.circle(lx + 3, ly - 3, 2.2, fill=1, stroke=0); c.circle(lx + 11, ly - 3, 2.2, fill=1, stroke=0)
        else:
            c.setStrokeColor(CRAN); c.setLineWidth(1.4); c.line(lx + 3, ly - 7, lx + 11, ly + 1); c.line(lx + 3, ly + 1, lx + 11, ly - 7)
        c.setFillColor(INK); c.drawString(lx + 19, ly - 6, text)
        lx += 19 + pdfmetrics.stringWidth(text, "Nunito", 8 * Lx.s) + 18

# ---- evidence 2: stall directory
def draw_directory(b):
    c, Lx = b.c, b.L
    y = b.title_block("Evidence 2", "Stall directory")
    y = para(c, "From the market programme. Each stall’s lane is also shown on the map.",
             Lx.m, y, Lx.cw, Lx.small)
    cols = [("No.", 34), ("Stall", 150), ("Lane", 118), ("Sells", Lx.cw - 302)]
    rh = min(15.5 * Lx.s, (y - Lx.bottom - 20) / 38)
    fs = min(9.5 * Lx.s, rh * 0.62)
    x = Lx.m; c.setFont("Nunito-ExtraBold", fs); c.setFillColor(CRAN)
    for name, w in cols:
        c.drawString(x + 4, y - rh + 4, name.upper()); x += w
    y -= rh
    c.setStrokeColor(GREEN); c.setLineWidth(1); c.line(Lx.m, y, Lx.W - Lx.m, y)
    for n in range(1, 37):
        name, goods = C.STALLS[n]
        if (n - 1) % 9 == 0 and n > 1:
            c.setStrokeColor(MUST); c.setLineWidth(0.8); c.line(Lx.m, y, Lx.W - Lx.m, y)
        if n % 2 == 0:
            c.setFillColor(PALE); c.rect(Lx.m, y - rh, Lx.cw, rh, fill=1, stroke=0)
        vals = [str(n), name, C.lane_of(n), ", ".join(C.GOODS[g] for g in goods)]
        x = Lx.m
        for (cn, w), v in zip(cols, vals):
            c.setFillColor(INK); c.setFont("Nunito-Bold" if cn == "No." else "Nunito", fs)
            c.drawString(x + 4, y - rh + (rh - fs) / 2 + 1.5, v); x += w
        y -= rh

# ---- evidence 3: receipt & note
def draw_receipt_note(b):
    c, Lx = b.c, b.L
    y = b.title_block("Evidence 3", "The receipt & Pip’s note")
    y = para(c, "Left: the receipt found under the judging table (the top was torn away). "
                "Right: the note Pip Calloway left for the Inspector.", Lx.m, y, Lx.cw, Lx.small)
    s = Lx.s
    rw, rhh = 190 * s, 330 * s
    rx, ry = Lx.m + 6, y - 20 - rhh
    # shadow + receipt with torn top
    c.setFillColor(HexColor("#E8E2D8"))
    c.rect(rx + 4, ry - 4, rw, rhh - 10, fill=1, stroke=0)
    c.setFillColor(WHITE); c.setStrokeColor(RULE); c.setLineWidth(0.6)
    p = c.beginPath(); p.moveTo(rx, ry); p.lineTo(rx + rw, ry); p.lineTo(rx + rw, ry + rhh - 12)
    rng = random.Random(3); n = 16
    for i in range(n, -1, -1):
        p.lineTo(rx + rw * i / n, ry + rhh - 12 + (rng.uniform(4, 12) if i % 2 else rng.uniform(-2, 3)))
    p.close(); c.drawPath(p, fill=1, stroke=1)
    lines = [("C", "EMBER SQUARE"), ("C", "CHRISTMAS MARKET"), ("-", ""),
             ("L", f"23/12   {C.RECEIPT_TIME}   TILL 2"), ("-", ""),
             ("R", ("1 x SPICED APPLE PUNCH", "4.50")), ("R", ("    MUG DEPOSIT", "2.00")),
             ("-", ""), ("B", ("TOTAL", "6.50")), ("L", "PAID BY WRISTBAND"), ("-", ""),
             ("C", "MUGS RETURNABLE"), ("C", "AT ANY STALL"), ("C", ""), ("C", "MERRY CHRISTMAS!")]
    ty = ry + rhh - 42 * s; fs = 8.6 * s
    for kind, v in lines:
        if kind == "-":
            c.setStrokeColor(SOFT); c.setDash(2, 2); c.line(rx + 12, ty + 3, rx + rw - 12, ty + 3); c.setDash()
        elif kind == "C":
            c.setFont("Courier Prime-Bold" if "MARKET" in v or "EMBER" in v else "Courier Prime", fs)
            c.setFillColor(INK); c.drawCentredString(rx + rw / 2, ty, v)
        elif kind == "L":
            c.setFont("Courier Prime", fs); c.setFillColor(INK); c.drawString(rx + 14, ty, v)
        else:
            c.setFont("Courier Prime-Bold" if kind == "B" else "Courier Prime", fs); c.setFillColor(INK)
            c.drawString(rx + 14, ty, v[0]); c.drawRightString(rx + rw - 14, ty, v[1])
        ty -= fs * 1.75
    # Pip's note
    nw, nh = Lx.cw - rw - 40, 300 * s
    nx, ny = rx + rw + 30, y - 40 - nh
    c.saveState(); c.translate(nx + nw / 2, ny + nh / 2); c.rotate(-2.2)
    c.setFillColor(HexColor("#E8E2D8")); c.rect(-nw / 2 + 4, -nh / 2 - 4, nw, nh, fill=1, stroke=0)
    c.setFillColor(HexColor("#FFFDF7")); c.setStrokeColor(RULE); c.rect(-nw / 2, -nh / 2, nw, nh, fill=1, stroke=1)
    lh = 27 * s
    c.setStrokeColor(HexColor("#C9D8E4")); c.setLineWidth(0.6)
    yy = nh / 2 - 34 * s
    while yy > -nh / 2 + 10:
        c.line(-nw / 2 + 6, yy - 5, nw / 2 - 6, yy - 5); yy -= lh
    c.setStrokeColor(HexColor("#E7A9A9")); c.line(-nw / 2 + 26 * s, nh / 2 - 4, -nw / 2 + 26 * s, -nh / 2 + 4)
    c.setFillColor(HexColor("#2A3A63"))
    fsz = 15.5 * s
    # shrink the handwriting if a line would overflow
    maxw = max(pdfmetrics.stringWidth(t, "Caveat", fsz) for t in C.PIP_NOTE)
    if maxw > nw - 40 * s:
        fsz *= (nw - 40 * s) / maxw
    c.setFont("Caveat", fsz)
    yy = nh / 2 - 34 * s
    for t in C.PIP_NOTE:
        c.drawString(-nw / 2 + 32 * s, yy, t); yy -= lh
    # tape
    c.setFillColor(Color(0.84, 0.64, 0.25, alpha=0.55))
    c.rect(-24 * s, nh / 2 - 8 * s, 48 * s, 16 * s, fill=1, stroke=0)
    c.restoreState()
    # caption
    c.setFont("Nunito-Italic", 8.5 * s); c.setFillColor(SOFT)
    c.drawString(Lx.m, min(ry, ny) - 26 * s, "Evidence bag 14 (receipt) and 15 (note). Both were logged at 21:30.")

# ---- evidence 4: weather
def draw_weather(b):
    c, Lx = b.c, b.L
    y = b.title_block("Evidence 4", "Weather log")
    c.setFillColor(PARCH); bh = 38 * Lx.s
    c.rect(Lx.m, y - bh, Lx.cw, bh, fill=1, stroke=0)
    c.setFillColor(GREEN); c.setFont("Nunito-ExtraBold", 10 * Lx.s)
    c.drawString(Lx.m + 12, y - 16 * Lx.s, "EMBERFIELD WEATHER STATION")
    c.setFont("Nunito", 9 * Lx.s); c.setFillColor(INK)
    c.drawString(Lx.m + 12, y - 29 * Lx.s, "Precipitation record for Ember Square, 23 December. "
                 "Times are inclusive, to the minute.")
    y -= bh + 18
    cols = [("From", 70), ("To", 70), ("Conditions", 200), ("", Lx.cw - 340)]
    rh = 30 * Lx.s; fs = 11 * Lx.s
    c.setFont("Nunito-ExtraBold", 9 * Lx.s); c.setFillColor(CRAN)
    x = Lx.m
    for n, w in cols:
        c.drawString(x + 6, y - 12, n.upper()); x += w
    y -= 18; c.setStrokeColor(GREEN); c.line(Lx.m, y, Lx.W - Lx.m, y)
    for a, bb, cond, snow in C.WEATHER:
        c.setFillColor(PALE if snow else WHITE); c.rect(Lx.m, y - rh, Lx.cw, rh, fill=1, stroke=0)
        c.setFillColor(INK); c.setFont("Nunito-Bold", fs)
        c.drawString(Lx.m + 6, y - rh / 2 - fs / 3, a); c.drawString(Lx.m + 76, y - rh / 2 - fs / 3, bb)
        c.setFont("Nunito", fs); c.drawString(Lx.m + 146, y - rh / 2 - fs / 3, cond)
        if snow:
            for k in range(3 if "Steady" in cond else 1):
                snowflake(c, Lx.m + 360 + k * 22 * Lx.s, y - rh / 2, 7 * Lx.s, GREEN, 1)
        y -= rh
        c.setStrokeColor(RULE); c.setLineWidth(0.5); c.line(Lx.m, y, Lx.W - Lx.m, y)
    # timeline bar
    y -= 34
    t0, t1 = C.tmin("16:00"), C.tmin("21:00")
    x0, x1 = Lx.m + 10, Lx.W - Lx.m - 10
    def X(t):
        return x0 + (x1 - x0) * (t - t0) / (t1 - t0)
    c.setFillColor(HexColor("#EFEAE0")); c.rect(x0, y - 18, x1 - x0, 18, fill=1, stroke=0)
    for a, bb in C.SNOW_WINDOWS:
        c.setFillColor(GREEN); c.rect(X(a), y - 18, X(bb + 1) - X(a), 18, fill=1, stroke=0)
        snowflake(c, (X(a) + X(bb + 1)) / 2, y - 9, 6, WHITE, 0.9)
    c.setFont("Nunito", 8 * Lx.s); c.setFillColor(INK)
    for h in range(16, 22):
        c.drawCentredString(X(h * 60), y - 32, f"{h}:00")
        c.setStrokeColor(SOFT); c.line(X(h * 60), y - 22, X(h * 60), y - 18)
    c.setFont("Nunito-Italic", 8 * Lx.s); c.setFillColor(SOFT)
    c.drawString(x0, y + 6, "Snowfall across the evening (dark bands = snowing)")
    # temperatures
    y -= 70
    c.setFont("Nunito-ExtraBold", 9 * Lx.s); c.setFillColor(CRAN); c.drawString(Lx.m, y, "AIR TEMPERATURE")
    y -= 18; c.setFont("Nunito", 10 * Lx.s); c.setFillColor(INK)
    step = Lx.cw / len(C.TEMPS)
    for i, (t, v) in enumerate(C.TEMPS):
        c.drawString(Lx.m + i * step, y, f"{t}   {v}")
    y -= 40
    para(c, "<i>Station note: gritters out on Mill Lane from 19:30. Footbridges salted at 20:00.</i>",
         Lx.m, y, Lx.cw, Lx.small)

# ---- evidence 5: coach timetable
def draw_coach(b):
    c, Lx = b.c, b.L
    y = b.title_block("Evidence 5", "Coach timetable")
    c.setFillColor(GREEN); bh = 44 * Lx.s
    c.roundRect(Lx.m, y - bh, Lx.cw, bh, 6, fill=1, stroke=0)
    c.setFillColor(PARCH); c.setFont("Fraunces-SemiBold", 15 * Lx.s)
    c.drawString(Lx.m + 14, y - 20 * Lx.s, "Ember Valley Coaches")
    c.setFont("Nunito", 9 * Lx.s)
    c.drawString(Lx.m + 14, y - 34 * Lx.s, "Evening departures from the Market Stop (outside the North Gate) · 23 December")
    y -= bh + 16
    cols = [("Departs", 80), ("Route", 80), ("Calls at, in order", Lx.cw - 160)]
    c.setFont("Nunito-ExtraBold", 9 * Lx.s); c.setFillColor(CRAN)
    x = Lx.m
    for n, w in cols:
        c.drawString(x + 6, y - 12, n.upper()); x += w
    y -= 18; c.setStrokeColor(GREEN); c.line(Lx.m, y, Lx.W - Lx.m, y)
    st = ParagraphStyle("cell", parent=Lx.body, spaceAfter=0)
    for i, (dep, route, towns) in enumerate(C.COACHES):
        txt = ", ".join(towns)
        h = max(30 * Lx.s, para_h(esc(txt), cols[2][1] - 12, st) + 14)
        c.setFillColor(PALE if i % 2 else WHITE); c.rect(Lx.m, y - h, Lx.cw, h, fill=1, stroke=0)
        c.setFillColor(INK); c.setFont("Nunito-ExtraBold", 13 * Lx.s); c.drawString(Lx.m + 6, y - 20 * Lx.s, dep)
        c.setFont("Nunito-Bold", 10.5 * Lx.s); c.drawString(Lx.m + 86, y - 19 * Lx.s, route)
        para(c, esc(txt), Lx.m + 166, y - 8, cols[2][1] - 12, st)
        y -= h; c.setStrokeColor(RULE); c.setLineWidth(0.5); c.line(Lx.m, y, Lx.W - Lx.m, y)
    y -= 16
    para(c, "<i>All coaches stop only at the towns listed. Emberfield residents: the town centre is "
            "a five-minute walk from the North Gate.</i>", Lx.m, y, Lx.cw, Lx.small)

# ---- evidence 6: statements
def statement(c, Lx, y, who, paras, taken):
    st = ParagraphStyle("typed", fontName="Courier Prime", fontSize=9.6 * Lx.s, leading=13.6 * Lx.s,
                        textColor=INK, spaceAfter=7 * Lx.s)
    h = sum(para_h(esc(p), Lx.cw - 28, st) for p in paras) + 74 * Lx.s
    c.setFillColor(WHITE); c.setStrokeColor(GREEN); c.setLineWidth(1)
    c.rect(Lx.m, y - h, Lx.cw, h, fill=1, stroke=1)
    c.setFillColor(GREEN); c.rect(Lx.m, y - 22 * Lx.s, Lx.cw, 22 * Lx.s, fill=1, stroke=0)
    c.setFillColor(PARCH); c.setFont("Nunito-ExtraBold", 8.5 * Lx.s)
    c.drawString(Lx.m + 12, y - 15 * Lx.s, "EMBERFIELD CONSTABULARY · WITNESS STATEMENT")
    c.drawRightString(Lx.W - Lx.m - 12, y - 15 * Lx.s, taken)
    c.setFillColor(INK); c.setFont("Nunito-Bold", 10.5 * Lx.s)
    c.drawString(Lx.m + 14, y - 38 * Lx.s, who)
    yy = y - 48 * Lx.s
    for p in paras:
        yy = para(c, esc(p), Lx.m + 14, yy, Lx.cw - 28, st)
    c.setFont("Caveat", 14 * Lx.s); c.setFillColor(HexColor("#2A3A63"))
    c.drawRightString(Lx.W - Lx.m - 16, y - h + 10 * Lx.s, who.split(",")[0])
    return y - h - 18

def draw_statements(b):
    c, Lx = b.c, b.L
    y = b.title_block("Evidence 6", "Witness statements")
    y = statement(c, Lx, y, C.STEWARD[0], C.STEWARD[1], "Taken 22:05")
    statement(c, Lx, y, C.DRIVER[0], C.DRIVER[1], "Taken 24 Dec, 07:40")

# ---- notebook
def draw_notebook(b):
    c, Lx = b.c, b.L
    y = b.title_block("Detective Inspector Wren Ashdown", "The Inspector’s Notebook")
    st = ParagraphStyle("clue", parent=Lx.body, fontSize=10.2 * Lx.s, leading=13.8 * Lx.s, spaceAfter=5 * Lx.s)
    y = para(c, "Clues 1–12: stated outright", Lx.m, y, Lx.cw, Lx.h2)
    for cl in C.CLUES:
        if cl["kind"] != "notebook":
            continue
        checkbox(c, Lx.m, y - 11 * Lx.s, 9 * Lx.s)
        c.setFont("Nunito-ExtraBold", 10.2 * Lx.s); c.setFillColor(CRAN)
        c.drawString(Lx.m + 15 * Lx.s, y - 10 * Lx.s, cl["id"] + ".")
        y = para(c, esc(cl["text"]), Lx.m + 36 * Lx.s, y, Lx.cw - 36 * Lx.s, st)
    y -= 4
    y = para(c, "Evidence A–F: work these out from the documents", Lx.m, y, Lx.cw, Lx.h2)
    for cl in C.CLUES:
        if cl["kind"] != "evidence":
            continue
        checkbox(c, Lx.m, y - 11 * Lx.s, 9 * Lx.s)
        c.setFont("Nunito-ExtraBold", 10.2 * Lx.s); c.setFillColor(CRAN)
        c.drawString(Lx.m + 15 * Lx.s, y - 10 * Lx.s, cl["id"] + ".")
        y = para(c, esc(cl["text"]) + " <font color='#6B6259'>— look at: " + esc(", ".join(cl["docs"])) + "</font>",
                 Lx.m + 36 * Lx.s, y, Lx.cw - 36 * Lx.s, st)
    b.notebook_bottom = y

# ---- log intro & pages
def draw_log_intro(b):
    c, Lx = b.c, b.L
    y = b.title_block("Ticket office export", "The Visitor Log")
    y = para(c, "Every wristband scanned at the gates on 23 December, in the order it was scanned. "
                "Each line is one visitor.", Lx.m, y, Lx.cw, Lx.body)
    rows = [("Entry", "time the wristband was scanned at the gate (24-hour clock)"),
            ("Ticket", "ticket and wristband number, 0001–6000"),
            ("First name, Surname", "as given when the ticket was bought"),
            ("Home town", "as given when the ticket was bought"),
            ("Gate", "North, East, South or West"),
            ("Last stall", "number of the stall where the wristband made its final purchase"),
            ("Box", "an empty box for your own ticks")]
    for k, v in rows:
        c.setFont("Nunito-ExtraBold", 10 * Lx.s); c.setFillColor(GREEN)
        c.drawString(Lx.m, y - 11 * Lx.s, k)
        y = min(para(c, esc(v), Lx.m + 140 * Lx.s, y, Lx.cw - 140 * Lx.s, Lx.body), y - 18 * Lx.s)
    y = para(c, "Chapters", Lx.m, y - 10, Lx.cw, Lx.h2)
    y = para(c, "The log is split into hourly chapters. Tap a chapter to jump to it.", Lx.m, y, Lx.cw, Lx.small)
    for key, title, level, _ in b.plan:
        if key.startswith("log") and title:
            c.setFont("Nunito-Bold", 11 * Lx.s); c.setFillColor(INK)
            c.drawString(Lx.m + 10, y - 13 * Lx.s, f"{title}")
            c.drawRightString(Lx.m + 260 * Lx.s, y - 13 * Lx.s, f"page {b.pageno[key]}")
            b.link(key, Lx.m, y - 17 * Lx.s, Lx.m + 270 * Lx.s, y)
            y -= 20 * Lx.s

def draw_log_page(b, chunk):
    c, Lx = b.c, b.L
    rh, _ = log_geometry(Lx)
    recs = [it[1] for it in chunk if it[0] == "rec"]
    scale = Lx.cw / sum(w for _, w in LOG_COLS)
    scale = min(scale, 1.35)
    cols = [(n, w * scale) for n, w in LOG_COLS]
    tw = sum(w for _, w in cols); x0 = Lx.m + (Lx.cw - tw) / 2
    y = Lx.top + 6
    c.setFont("Fraunces-SemiBold", 13 * Lx.s); c.setFillColor(GREEN)
    c.drawString(x0, y - 14 * Lx.s, "Visitor Log")
    c.setFont("Nunito-Bold", 9.5 * Lx.s); c.setFillColor(INK)
    c.drawRightString(x0 + tw, y - 13 * Lx.s,
                      f"entries {C.tstr(recs[0]['entry'])} – {C.tstr(recs[-1]['entry'])}")
    y -= 30 * Lx.s
    fs = 8.9 if not Lx.ipad else 10.4
    c.setFont("Nunito-ExtraBold", fs * 0.9); c.setFillColor(CRAN)
    x = x0
    for n, w in cols:
        c.drawString(x + 4, y - rh + 3, n.upper()); x += w
    y -= rh
    c.setStrokeColor(GREEN); c.setLineWidth(0.9); c.line(x0, y, x0 + tw, y)
    zebra = 0
    for kind, v in chunk:
        if kind == "band":
            c.setFillColor(PARCH); c.rect(x0, y - rh, tw, rh, fill=1, stroke=0)
            c.setFillColor(GREEN); c.setFont("Fraunces-SemiBold", fs)
            c.drawString(x0 + 6, y - rh + 3, f"Chapter · {v:02d}:00–{v:02d}:59")
            y -= rh; zebra = 0; continue
        if zebra % 2:
            c.setFillColor(PALE); c.rect(x0, y - rh, tw, rh, fill=1, stroke=0)
        zebra += 1
        vals = [C.tstr(v["entry"]), f"{v['ticket']:04d}", v["first"], v["last"], v["town"],
                v["gate"], str(v["stall"]), ""]
        x = x0; c.setFillColor(INK)
        for (n, w), val in zip(cols, vals):
            if n == "":
                c.setStrokeColor(RULE); c.setLineWidth(0.6)
                c.rect(x + 6, y - rh + 2.5, rh - 5, rh - 5, fill=0, stroke=1)
            else:
                c.setFont("Nunito-Bold" if n in ("Entry", "Ticket") else "Nunito", fs)
                c.drawString(x + 4, y - rh + 3, val)
            x += w
        y -= rh
    c.setStrokeColor(GREEN); c.setLineWidth(0.9); c.line(x0, y, x0 + tw, y)

# ---- notes, check, hints, thanks
def draw_notes(b):
    c, Lx = b.c, b.L
    y = b.title_block("Your working", "Detective’s notes")
    c.setStrokeColor(RULE); c.setLineWidth(0.5)
    yy = y - 10
    while yy > Lx.bottom + 10:
        c.line(Lx.m, yy, Lx.W - Lx.m, yy); yy -= 24 * Lx.s

def draw_check(b):
    c, Lx = b.c, b.L
    y = b.title_block("Check your answer without spoilers", "The Sealed Check")
    y = para(c, "Found your one remaining visitor? Do this sum with their details (a phone calculator "
                "is fine). It confirms the answer without printing the killer’s name anywhere in "
                "this case file.", Lx.m, y, Lx.cw, Lx.body)
    steps = ["Take their ticket number and multiply it by 7.",
             "Count the letters in their first name and in their surname, and add both counts to the result.",
             "Look at the last three digits of the total."]
    for i, s in enumerate(steps, 1):
        c.setFillColor(MUST); c.circle(Lx.m + 10, y - 9 * Lx.s, 9 * Lx.s, fill=1, stroke=0)
        c.setFillColor(GREEN); c.setFont("Nunito-ExtraBold", 10 * Lx.s)
        c.drawCentredString(Lx.m + 10, y - 12.5 * Lx.s, str(i))
        y = min(para(c, esc(s), Lx.m + 30 * Lx.s, y, Lx.cw - 30 * Lx.s, Lx.body), y - 24 * Lx.s)
    y -= 8
    labels = ["Ticket number × 7 =", "+ letters in first name =", "+ letters in surname =",
              "Last three digits ="]
    for lab in labels:
        c.setFont("Nunito-Bold", 11 * Lx.s); c.setFillColor(INK); c.drawString(Lx.m + 10, y - 16 * Lx.s, lab)
        c.setStrokeColor(GREEN); c.setLineWidth(0.9)
        c.roundRect(Lx.m + 190 * Lx.s, y - 24 * Lx.s, 140 * Lx.s, 24 * Lx.s, 4, fill=0, stroke=1)
        y -= 34 * Lx.s
    y -= 10
    bh = 96 * Lx.s
    c.setFillColor(GREEN); c.roundRect(Lx.m, y - bh, Lx.cw, bh, 10, fill=1, stroke=0)
    c.setFillColor(PARCH); c.setFont("Nunito", 11 * Lx.s)
    c.drawCentredString(Lx.W / 2, y - 26 * Lx.s, "If your last three digits are")
    c.setFont("Fraunces-SemiBold", 34 * Lx.s); c.setFillColor(MUST)
    c.drawCentredString(Lx.W / 2, y - 62 * Lx.s, b.seal)
    c.setFont("Nunito", 11 * Lx.s); c.setFillColor(PARCH)
    c.drawCentredString(Lx.W / 2, y - 84 * Lx.s, "you have caught the killer. Open the Envelope to read how it happened.")
    y -= bh + 16
    para(c, "Not a match? Somewhere a visitor was kept or crossed out by mistake. The hints at the "
            "back can show you which clue to look at again.", Lx.m, y, Lx.cw, Lx.body)

def draw_hint_stop(b):
    c, Lx = b.c, b.L
    c.setFillColor(PARCH); c.rect(Lx.m, Lx.bottom + 40, Lx.cw, Lx.top - Lx.bottom - 60, fill=1, stroke=0)
    for i in range(14):
        snowflake(c, Lx.m + 30 + (i * 53) % (Lx.cw - 40), Lx.top - 60 - (i * 97) % (Lx.top - Lx.bottom - 160),
                  6, MUST, 0.8)
    c.setFillColor(CRAN); c.setFont("Nunito-ExtraBold", 11 * Lx.s)
    c.drawCentredString(Lx.W / 2, Lx.H / 2 + 60 * Lx.s, "STOP, DETECTIVE")
    c.setFillColor(GREEN); c.setFont("Fraunces-SemiBold", 34 * Lx.s)
    c.drawCentredString(Lx.W / 2, Lx.H / 2 + 14 * Lx.s, "Hints ahead")
    st = ParagraphStyle("c", parent=Lx.body, alignment=TA_CENTER)
    para(c, "Three levels of help for every clue, each level on its own pages. Start with Level 1 "
            "and only go further if you need to. Nothing here names the killer.",
         Lx.m + 50, Lx.H / 2 - 10 * Lx.s, Lx.cw - 100, st)
    y = Lx.H / 2 - 90 * Lx.s
    for lv in range(3):
        key = f"hint{lv}_0"
        c.setFont("Nunito-Bold", 12 * Lx.s); c.setFillColor(INK)
        t = f"{H.LEVEL_NAMES[lv]}  ·  page {b.pageno[key]}"
        c.drawCentredString(Lx.W / 2, y, t)
        tw = pdfmetrics.stringWidth(t, "Nunito-Bold", 12 * Lx.s)
        b.link(key, Lx.W / 2 - tw / 2, y - 4, Lx.W / 2 + tw / 2, y + 12 * Lx.s)
        y -= 24 * Lx.s

def hint_items():
    order = [c for c in C.CLUES]
    return [(cl["label"], cl["id"]) for cl in order]

def hint_pages(Lx):
    """Split each level's 18 hints across pages by measured height."""
    st = ParagraphStyle("h", parent=Lx.body)
    avail = Lx.top - Lx.bottom - 90 * Lx.s
    out = []
    for lv in range(3):
        pages, cur, used = [], [], 0
        for label, cid in hint_items():
            h = para_h(esc(H.HINTS[cid][lv]), Lx.cw - 110 * Lx.s, st) + 6
            if used + h > avail and cur:
                pages.append(cur); cur, used = [], 0
            cur.append((label, cid)); used += h
        pages.append(cur); out.append(pages)
    return out

def draw_hint_page(b, lv, chunk, j):
    c, Lx = b.c, b.L
    y = b.title_block("Hints" + (" (continued)" if j else ""), H.LEVEL_NAMES[lv])
    st = ParagraphStyle("h", parent=Lx.body)
    for label, cid in chunk:
        c.setFont("Nunito-ExtraBold", 10 * Lx.s); c.setFillColor(CRAN)
        c.drawString(Lx.m, y - 11 * Lx.s, label)
        y = min(para(c, esc(H.HINTS[cid][lv]), Lx.m + 110 * Lx.s, y, Lx.cw - 110 * Lx.s, st), y - 18 * Lx.s) - 6

def draw_thanks(b):
    c, Lx = b.c, b.L
    y = b.title_block(C.BRAND, "Thank you, detective")
    for p in ["Thank you for spending an evening at Ember Square. We hope the snow, the punch and "
              "the red bobble hat kept you guessing.",
              "Every case from QuietClueCo is written and drawn by hand, and checked by a computer "
              "program before it reaches you: the program confirms there is exactly one answer, that "
              "every clue is needed, and that the answer does not change if a clue is read in a "
              "slightly different way.",
              "If you enjoyed the case, a short review helps other detectives find us.",
              "For personal use only. Please don’t share or resell the files. You may print as "
              "many copies as you need for your own household or game night.",
              "Fonts: Fraunces, Nunito, Caveat and Courier Prime (SIL Open Font License). "
              "All illustrations are drawn with code. No AI-generated images are used."]:
        y = para(c, esc(p), Lx.m, y, Lx.cw, Lx.body)

# ------------------------------------------------------------------ solution file
def build_solution(fmt, path, walk, finalists, index):
    b = Book(fmt, path, f"{C.TITLE} — The Envelope (solution)")
    c, Lx = b.c, b.L
    K = C.KILLER
    # page 1: the answer
    b.new_page("answer", "Solution", "The answer")
    c.setFillColor(GREEN); c.roundRect(Lx.m, Lx.top - 250 * Lx.s, Lx.cw, 250 * Lx.s, 12, fill=1, stroke=0)
    c.setFillColor(MUST); c.setFont("Nunito-ExtraBold", 10 * Lx.s)
    c.drawCentredString(Lx.W / 2, Lx.top - 34 * Lx.s, "THE ENVELOPE · OPEN AFTER THE SEALED CHECK")
    c.setFillColor(PARCH); c.setFont("Fraunces-SemiBold", 40 * Lx.s)
    c.drawCentredString(Lx.W / 2, Lx.top - 100 * Lx.s, f"{K['first']} {K['last']}")
    c.setFont("Nunito", 12 * Lx.s)
    c.drawCentredString(Lx.W / 2, Lx.top - 132 * Lx.s,
                        f"Ticket {K['ticket']:04d} · {K['town']} · entered {C.tstr(K['entry'])} "
                        f"by the {K['gate']} Gate · last stall {K['stall']}")
    c.setFont("Nunito-Italic", 10.5 * Lx.s)
    c.drawCentredString(Lx.W / 2, Lx.top - 160 * Lx.s, f"Sealed Check: {K['ticket']:04d} × 7 + "
                        f"{len(K['first'])} + {len(K['last'])} = {K['ticket'] * 7 + len(K['first']) + len(K['last'])} "
                        f", last three digits {b_seal(K)}")
    c.setFont("Nunito", 10.5 * Lx.s)
    c.drawCentredString(Lx.W / 2, Lx.top - 200 * Lx.s, "In this file: what really happened · the step-by-step "
                        "solution · the finalists ·")
    c.drawCentredString(Lx.W / 2, Lx.top - 216 * Lx.s, "and an index showing which clue rules out every one of the 6,000 visitors.")
    y = Lx.top - 280 * Lx.s
    y = para(c, "What really happened", Lx.m, y, Lx.cw, Lx.h2)
    epi = list(C.EPILOGUE)
    while epi:
        p = epi[0]
        h = para_h(esc(p), Lx.cw, Lx.body)
        if y - h < Lx.bottom:
            b.new_page("epilogue2", "Solution"); y = Lx.top
        y = para(c, esc(p), Lx.m, y, Lx.cw, Lx.body); epi.pop(0)
    # walkthrough
    b.new_page("walk", "Solution", "Step by step")
    y = b.title_block("The solution", "Step by step")
    y = para(c, "One good order for the clues. The big sweeps come first, so later clues only "
                "need checking against the visitors who are still in. Any order reaches the same answer.",
             Lx.m, y, Lx.cw, Lx.body)
    cols = [("Step", 34), ("Clue", 70), ("What it tells you", Lx.cw - 214), ("Out", 50), ("Left", 60)]
    st = ParagraphStyle("w", parent=Lx.small, spaceAfter=0)
    def head(y):
        x = Lx.m; c.setFont("Nunito-ExtraBold", 8.5 * Lx.s); c.setFillColor(CRAN)
        for n, w in cols:
            c.drawString(x + 4, y - 11, n.upper()); x += w
        y -= 16; c.setStrokeColor(GREEN); c.line(Lx.m, y, Lx.W - Lx.m, y); return y
    y = head(y)
    c.setFont("Nunito", 9 * Lx.s); c.setFillColor(INK)
    c.drawString(Lx.m + 108, y - 12, "Start: the Visitor Log"); c.drawRightString(Lx.W - Lx.m - 6, y - 12, "6,000")
    y -= 18
    for i, step in enumerate(walk, 1):
        txt = step["why"]
        h = max(para_h(esc(txt), cols[2][1] - 8, st) + 8, 18)
        if y - h < Lx.bottom:
            b.new_page(None, "Solution"); y = head(Lx.top)
        if i % 2 == 0:
            c.setFillColor(PALE); c.rect(Lx.m, y - h, Lx.cw, h, fill=1, stroke=0)
        c.setFillColor(INK); c.setFont("Nunito-Bold", 9 * Lx.s)
        c.drawString(Lx.m + 4, y - 12, str(i)); c.drawString(Lx.m + 38, y - 12, step["label"])
        para(c, esc(txt), Lx.m + 108, y - 3, cols[2][1] - 8, st)
        c.setFont("Nunito", 9 * Lx.s)
        c.drawRightString(Lx.W - Lx.m - 66, y - 12, f"{step['out']:,}")
        c.setFont("Nunito-Bold", 9 * Lx.s)
        c.drawRightString(Lx.W - Lx.m - 6, y - 12, f"{step['left']:,}")
        y -= h
    # finalists
    b.new_page("finalists", "Solution", "The finalists")
    y = b.title_block("The solution", "The finalists")
    y = para(c, "These visitors fit every clue but one. Each is ruled out by exactly the clue shown, "
                "which is how we know every clue in the case is needed.", Lx.m, y, Lx.cw, Lx.body)
    fcols = [("Ticket", 46), ("Visitor", 118), ("Town", 84), ("Gate", 40), ("Entry", 40), ("Stall", 36),
             ("Ruled out by", Lx.cw - 364)]
    x = Lx.m; c.setFont("Nunito-ExtraBold", 8.5 * Lx.s); c.setFillColor(CRAN)
    for n, w in fcols:
        c.drawString(x + 3, y - 11, n.upper()); x += w
    y -= 16; c.setStrokeColor(GREEN); c.line(Lx.m, y, Lx.W - Lx.m, y)
    fs = 8.6 * Lx.s; rh = 15 * Lx.s
    for i, f in enumerate(finalists):
        if y - rh < Lx.bottom:
            b.new_page(None, "Solution"); y = Lx.top
        if i % 2:
            c.setFillColor(PALE); c.rect(Lx.m, y - rh, Lx.cw, rh, fill=1, stroke=0)
        r = f["rec"]
        vals = [f"{r['ticket']:04d}", f"{r['first']} {r['last']}", r["town"], r["gate"], C.tstr(r["entry"]),
                str(r["stall"]), f["why"]]
        x = Lx.m
        for (n, w), v in zip(fcols, vals):
            c.setFillColor(CRAN if (n == "Ruled out by" and f["clue"] == "KILLER") else INK)
            c.setFont("Nunito-Bold" if n in ("Ticket", "Ruled out by") else "Nunito", fs)
            vv = v
            while pdfmetrics.stringWidth(vv, "Nunito", fs) > w - 6 and len(vv) > 4:
                vv = vv[:-2] + "…" if not vv.endswith("…") else vv[:-3] + "…"
            c.drawString(x + 3, y - rh + 4, vv); x += w
        y -= rh
    # index
    b.new_page("index", "Solution", "Elimination index")
    y = b.title_block("The solution", "Elimination index")
    y = para(c, "Every ticket from 0001 to 6000, with the first clue (in the step-by-step order) that "
                "rules that visitor out. If you kept or crossed out someone by mistake, look them up here.",
             Lx.m, y, Lx.cw, Lx.small)
    tickets = sorted(index)
    ncol = 10 if not Lx.ipad else 12
    colw = Lx.cw / ncol; rh = 10.2 * Lx.s
    per_col = int((y - Lx.bottom) // rh)
    first = True; i = 0
    while i < len(tickets):
        if not first:
            b.new_page(None, "Elimination index"); y = Lx.top
            per_col = int((y - Lx.bottom) // rh)
        first = False
        for col in range(ncol):
            for row in range(per_col):
                if i >= len(tickets):
                    break
                t = tickets[i]; v = index[t]
                xx = Lx.m + col * colw; yy = y - (row + 1) * rh
                c.setFont("Nunito-Bold", 7.4 * Lx.s); c.setFillColor(INK)
                c.drawString(xx + 2, yy + 2, f"{t:04d}")
                c.setFont("Nunito-ExtraBold" if v == "KILLER" else "Nunito", 7.4 * Lx.s)
                c.setFillColor(CRAN if v == "KILLER" else SOFT)
                c.drawString(xx + 26 * Lx.s, yy + 2, v)
                i += 1
    c.setFont("Nunito-Italic", 8 * Lx.s); c.setFillColor(SOFT)
    c.drawString(Lx.m, Lx.bottom - 2, "KILLER = the only visitor who fits every clue. Letters A to F are Evidence, numbers 1 to 12 are Clues.")
    b.save()
    return b.page

def b_seal(K):
    return f"{(K['ticket'] * 7 + len(K['first']) + len(K['last'])) % 1000:03d}"
