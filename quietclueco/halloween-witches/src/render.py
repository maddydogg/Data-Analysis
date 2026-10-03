"""Render Full Moon over Morrowmere to PDF: the case book (print Letter, print A4, iPad)
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
# Witch-village palette. The names are kept from the house template so the layout code is shared:
# GREEN = plum (headings), CRAN = amethyst (accents), AUB = aubergine, PARCH = moon parchment,
# MUST = candle gold, MOSS = sage.
GREEN = HexColor("#2B1B3D"); AUB = HexColor("#4A2C5E"); CRAN = HexColor("#8E5BB5")
PARCH = HexColor("#EDE6D6"); MUST = HexColor("#E3A64B"); MOSS = HexColor("#8FA382")
INK = HexColor("#1E1A22"); WHITE = HexColor("#FFFFFF")
PALE = HexColor("#F7F3EC")      # zebra rows: a whisper of parchment, cheap to print
RULE = HexColor("#DCD3C4"); SOFT = HexColor("#68606E")
STONE = HexColor("#9A93A0"); STONE_DARK = HexColor("#4E4757"); GRASS = HexColor("#E6ECDF")
MEADOW = HexColor("#F1F0E4")

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
def crescent(c, x, y, r, col=MUST, bg=WHITE):
    """A crescent moon centred at (x, y): a disc with a second disc cut out of it."""
    c.saveState(); c.setFillColor(col); c.circle(x, y, r, fill=1, stroke=0)
    c.setFillColor(bg); c.circle(x + r * 0.45, y + r * 0.22, r * 0.86, fill=1, stroke=0)
    c.restoreState()

def full_moon(c, x, y, r, col=MUST, rim=None):
    c.saveState(); c.setFillColor(col); c.circle(x, y, r, fill=1, stroke=0)
    c.setFillColor(Color(1, 1, 1, alpha=0.28))
    for dx, dy, rr in ((-0.3, 0.2, 0.22), (0.25, -0.25, 0.16), (0.1, 0.35, 0.1)):
        c.circle(x + dx * r, y + dy * r, rr * r, fill=1, stroke=0)
    if rim:
        c.setStrokeColor(rim); c.setLineWidth(max(0.5, r * 0.08)); c.circle(x, y, r, fill=0, stroke=1)
    c.restoreState()

def cloud(c, x, y, w, col=STONE):
    c.saveState(); c.setFillColor(col)
    for dx, dy, r in ((0, 0, 0.28), (0.25, 0.1, 0.24), (-0.25, 0.04, 0.22), (0.45, -0.02, 0.18), (-0.42, -0.04, 0.16)):
        c.circle(x + dx * w, y + dy * w, r * w, fill=1, stroke=0)
    c.rect(x - 0.55 * w, y - 0.2 * w, 1.1 * w, 0.2 * w, fill=1, stroke=0)
    c.restoreState()

def star(c, x, y, r, col=MUST, points=4):
    c.saveState(); c.setFillColor(col)
    p = c.beginPath()
    for k in range(points * 2):
        a = math.pi / 2 + math.pi * k / points
        rr = r if k % 2 == 0 else r * 0.32
        (p.moveTo if k == 0 else p.lineTo)(x + math.cos(a) * rr, y + math.sin(a) * rr)
    p.close(); c.drawPath(p, fill=1, stroke=0); c.restoreState()

def hat(c, x, y, h, col=GREEN, band=MUST, pin=True):
    """A tall pointed hat (no wearer) with its brim centred at (x, y)."""
    c.saveState(); c.setFillColor(col)
    c.ellipse(x - h * 0.55, y - h * 0.08, x + h * 0.55, y + h * 0.08, fill=1, stroke=0)
    p = c.beginPath(); p.moveTo(x - h * 0.28, y)
    p.curveTo(x - h * 0.18, y + h * 0.45, x - h * 0.05, y + h * 0.8, x + h * 0.22, y + h)
    p.curveTo(x + h * 0.08, y + h * 0.7, x + h * 0.2, y + h * 0.35, x + h * 0.28, y)
    p.close(); c.drawPath(p, fill=1, stroke=0)
    c.setFillColor(band); c.rect(x - h * 0.27, y + h * 0.02, h * 0.54, h * 0.08, fill=1, stroke=0)
    if pin:
        crescent(c, x + h * 0.02, y + h * 0.2, h * 0.07, HexColor("#D9D9E0"), col)
    c.restoreState()

def cauldron(c, x, y, r, col=GREEN, brew=MOSS):
    """A round cauldron on three short legs, centred at (x, y)."""
    c.saveState(); c.setFillColor(col)
    for dx in (-0.55, 0, 0.55):
        c.rect(x + dx * r - r * 0.08, y - r * 0.95, r * 0.16, r * 0.3, fill=1, stroke=0)
    c.circle(x, y - r * 0.1, r * 0.82, fill=1, stroke=0)
    c.roundRect(x - r * 0.95, y + r * 0.5, r * 1.9, r * 0.22, r * 0.1, fill=1, stroke=0)
    c.setFillColor(brew); c.ellipse(x - r * 0.8, y + r * 0.6, x + r * 0.8, y + r * 0.7, fill=1, stroke=0)
    c.setFillColor(Color(1, 1, 1, alpha=0.55))
    for dx, dy, rr in ((-0.3, 0.95, 0.12), (0.1, 1.15, 0.09), (0.32, 0.92, 0.07)):
        c.circle(x + dx * r, y + dy * r, rr * r, fill=1, stroke=0)
    c.restoreState()

def candle(c, x, y, h, col=PARCH, flame=MUST):
    c.saveState(); c.setFillColor(col); c.setStrokeColor(GREEN); c.setLineWidth(max(0.4, h * 0.03))
    c.rect(x - h * 0.12, y, h * 0.24, h * 0.7, fill=1, stroke=1)
    c.setFillColor(flame)
    p = c.beginPath(); p.moveTo(x, y + h); p.curveTo(x + h * 0.12, y + h * 0.86, x + h * 0.08, y + h * 0.74, x, y + h * 0.74)
    p.curveTo(x - h * 0.08, y + h * 0.74, x - h * 0.12, y + h * 0.86, x, y + h); c.drawPath(p, fill=1, stroke=0)
    c.restoreState()

def standing_stone(c, x, y, h, col=STONE, edge=STONE_DARK):
    """One standing stone, base centre at (x, y)."""
    c.saveState(); c.setFillColor(col); c.setStrokeColor(edge); c.setLineWidth(max(0.4, h * 0.06))
    p = c.beginPath(); p.moveTo(x - h * 0.3, y)
    p.curveTo(x - h * 0.34, y + h * 0.5, x - h * 0.22, y + h * 0.95, x, y + h)
    p.curveTo(x + h * 0.24, y + h * 0.92, x + h * 0.32, y + h * 0.5, x + h * 0.28, y)
    p.close(); c.drawPath(p, fill=1, stroke=1); c.restoreState()

def tree(c, x, y, r, col=MOSS):
    c.saveState(); c.setFillColor(HexColor("#6B5A44")); c.rect(x - r * 0.12, y - r * 1.1, r * 0.24, r * 0.7, fill=1, stroke=0)
    c.setFillColor(col); c.circle(x, y - r * 0.1, r * 0.7, fill=1, stroke=0)
    c.setFillColor(HexColor("#C8553D"))
    for dx, dy in ((-0.3, 0.1), (0.25, -0.2), (0.05, 0.3)):
        c.circle(x + dx * r, y + dy * r - r * 0.1, r * 0.1, fill=1, stroke=0)
    c.restoreState()

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

def checkbox(c, x, y, s, col=GREEN):
    c.saveState(); c.setStrokeColor(col); c.setLineWidth(0.9); c.roundRect(x, y, s, s, 2, fill=0, stroke=1)
    c.restoreState()

def scribble(c, x, y, w, h, col, seed=7):
    """An unreadable curly signature: two loops joined by a flourish."""
    rng = random.Random(seed)
    c.saveState(); c.setStrokeColor(col); c.setLineWidth(max(0.8, h * 0.07)); c.setLineCap(1)
    p = c.beginPath(); p.moveTo(x, y + h * 0.3)
    for k in range(2):
        bx = x + w * (0.08 + 0.42 * k)
        p.curveTo(bx + w * 0.22, y + h * 1.1, bx - w * 0.08, y + h * 1.2, bx + w * 0.02, y + h * 0.45)
        p.curveTo(bx + w * 0.1, y - h * 0.15, bx + w * 0.36, y + h * 0.1, bx + w * 0.3, y + h * 0.55)
        p.curveTo(bx + w * 0.26, y + h * 0.85, bx + w * 0.12, y + h * 0.5, bx + w * 0.4, y + h * 0.2 + rng.uniform(-1, 1))
    p.curveTo(x + w * 0.95, y - h * 0.1, x + w * 1.05, y + h * 0.3, x + w * 0.7, y - h * 0.25)
    c.drawPath(p, fill=0, stroke=1)
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
        crescent(c, Lx.m + 6, Lx.m - 11, 6, MUST)

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

LOG_COLS = [("Entry", 44), ("Ticket", 44), ("First name", 74), ("Surname", 96),
            ("Home village", 96), ("Entrance", 54), ("Last stall", 54), ("", 22)]

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
            ("map", "Evidence 1 — Fair map", 0, draw_map),
            ("directory", "Evidence 2 — Stall directory", 0, draw_directory),
            ("brews", "Evidence 3 — The Book of Brews", 0, draw_brews),
            ("moon", "Evidence 4 — Moon-watcher’s log", 0, draw_moon),
            ("reading", "Evidence 5 — Reading book & Bryony’s note", 0, draw_reading),
            ("ledger", "Evidence 6 — Shop ledger & carrier’s rounds", 0, draw_ledger),
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
            "brews": "Evidence 3", "moon": "Evidence 4", "reading": "Evidence 5",
            "ledger": "Evidence 6", "notebook": "Clues", "notes": "Notes",
            "check": "Check your answer", "thanks": ""}.get(key, "")

# ---- cover
ART = os.path.join(HERE, "art")

def draw_cover(b):
    """Full-bleed cover art (an old horror-mystery one-sheet), rendered for this page shape by
    listing/src/make_cover_art.py. The title is also written as invisible text so the PDF stays
    searchable and accessible."""
    c, Lx = b.c, b.L; W, H = Lx.W, Lx.H
    art = os.path.join(ART, f"cover_{Lx.fmt}.jpg")
    if not os.path.exists(art):
        raise FileNotFoundError(f"{art} is missing: run listing/src/make_cover_art.py first")
    c.drawImage(art, 0, 0, W, H)
    t = c.beginText(); t.setTextRenderMode(3); t.setFont("Nunito", 12)
    for i, line in enumerate([C.TITLE, C.SUBTITLE, C.TAGLINE, f"{C.BRAND} · Printable case file · {C.CASE_NO}"]):
        t.setTextOrigin(40, H - 60 - i * 16); t.textLine(line)
    c.drawText(t)

# ---- how to play
def draw_howto(b):
    c, Lx = b.c, b.L
    y = b.title_block("Before you begin", "How to play")
    for head, text in C.HOW_TO_PLAY:
        y = para(c, f"<font name='Nunito-ExtraBold' color='#4A2C5E'>{esc(head)}.</font> {esc(text)}",
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
    y = b.title_block(f"Morrowmere Police · {C.DATE}", "The case")
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

# ---- evidence 1: the fair map
def draw_map(b):
    c, Lx = b.c, b.L
    y = b.title_block("Evidence 1", "Fair map")
    y = para(c, f"Morrowmere green on Moon Fair night, {C.DATE}. North is at the top. Stalls are numbered; "
                "the stall directory (Evidence 2) says what each one sells.", Lx.m, y, Lx.cw, Lx.small)
    legend_h = 70 * Lx.s
    avail_h = y - Lx.bottom - legend_h
    size = min(Lx.cw, avail_h)
    ox = Lx.m + (Lx.cw - size) / 2; oy = y - size
    u = size / 100.0
    c.setFillColor(MEADOW); c.setStrokeColor(RULE); c.setLineWidth(0.6)
    c.rect(ox, oy, size, size, fill=1, stroke=1)
    wl, wb, wr, wt = ox + 22 * u, oy + 24 * u, ox + size - 7 * u, oy + size - 12 * u
    cx, cyy = (wl + wr) / 2, (wb + wt) / 2
    # the Hob Stones in the south-west meadow, and the footpaths
    hx, hy = ox + 11 * u, oy + 12 * u
    def path(pts, dash=True):
        c.setStrokeColor(HexColor("#B39C7A")); c.setLineWidth(2.6 * u); c.setLineCap(1); c.setDash()
        p = c.beginPath(); p.moveTo(*pts[0])
        for q in pts[1:]:
            p.lineTo(*q)
        c.drawPath(p, fill=0, stroke=1)
        c.setStrokeColor(HexColor("#7A6448")); c.setLineWidth(0.7); c.setDash(2, 2)
        c.drawPath(p, fill=0, stroke=1); c.setDash()
    path([(ox, oy + 3 * u), (hx, hy)])                                  # from the drove road
    path([(hx, hy), (hx, cyy), (wl, cyy)])                              # to Mill Stile (west)
    path([(hx, hy), (cx, hy), (cx, wb)])                                # to Orchard Gap (south)
    path([(cx, wt), (cx, oy + size)])                                   # Bramble Gate to the village street
    path([(wr, cyy), (ox + size, cyy)])                                 # Church Lychgate to the churchyard
    c.setStrokeColor(STONE); c.setLineWidth(0.6); c.setDash(1, 2)
    c.ellipse(hx - 7.6 * u, hy - 6.2 * u, hx + 7.6 * u, hy + 6.2 * u, fill=0, stroke=1); c.setDash()
    for k in range(9):                                                  # the ring, far stones first
        a = 2 * math.pi * k / 9 + 0.35
        pts = (hx + math.cos(a) * 7.6 * u, hy + math.sin(a) * 6.2 * u - 1.4 * u)
        if pts[1] > hy - 1.4 * u:
            standing_stone(c, pts[0], pts[1], 3.4 * u)
    for k in range(9):
        a = 2 * math.pi * k / 9 + 0.35
        pts = (hx + math.cos(a) * 7.6 * u, hy + math.sin(a) * 6.2 * u - 1.4 * u)
        if pts[1] <= hy - 1.4 * u:
            standing_stone(c, pts[0], pts[1], 3.4 * u)
    c.setFillColor(GREEN); c.setFont("Nunito-ExtraBold", 7.5 * Lx.s)
    c.drawString(hx + 9.5 * u, hy + 3.4 * u, "THE HOB STONES")
    c.setFillColor(SOFT); c.setFont("Nunito-Italic", 7 * Lx.s)
    c.drawString(ox + 4 * u, oy + 1.4 * u, "from the drove road")
    c.drawRightString(cx - 2.6 * u, oy + size - 3 * u, "to the village street")
    c.saveState(); c.translate(ox + size - 2.2 * u, cyy + 4.5 * u); c.rotate(90)
    c.drawString(0, 0, "to the churchyard"); c.restoreState()
    # orchard trees south of the green, the mill to the west
    for k in range(6):
        tree(c, cx + 9 * u + (k % 3) * 6.5 * u, oy + 15 * u - (k // 3) * 6.5 * u, 2.6 * u)
    c.setFillColor(SOFT); c.setFont("Nunito-Italic", 7 * Lx.s); c.drawString(cx + 7 * u, oy + 3 * u, "the orchard")
    mx, my = ox + 7 * u, cyy + 16 * u
    c.setFillColor(PARCH); c.setStrokeColor(GREEN); c.setLineWidth(0.8)
    c.rect(mx - 4 * u, my - 3 * u, 8 * u, 6 * u, fill=1, stroke=1)
    p = c.beginPath(); p.moveTo(mx - 5 * u, my + 3 * u); p.lineTo(mx, my + 7 * u); p.lineTo(mx + 5 * u, my + 3 * u); p.close()
    c.setFillColor(AUB); c.drawPath(p, fill=1, stroke=0)
    c.setStrokeColor(GREEN); c.circle(mx + 5.5 * u, my - 0.5 * u, 3 * u, fill=0, stroke=1)
    for k in range(4):
        a = math.pi / 4 * k
        c.line(mx + 5.5 * u - math.cos(a) * 3 * u, my - 0.5 * u - math.sin(a) * 3 * u,
               mx + 5.5 * u + math.cos(a) * 3 * u, my - 0.5 * u + math.sin(a) * 3 * u)
    c.setFillColor(SOFT); c.setFont("Nunito-Italic", 7 * Lx.s); c.drawCentredString(mx + 1 * u, my - 6 * u, "the mill")
    # the green, edged by a hedge
    c.setFillColor(GRASS); c.setStrokeColor(MOSS); c.setLineWidth(2.4 * u)
    c.roundRect(wl, wb, wr - wl, wt - wb, 3 * u, fill=1, stroke=1)
    gate_w = 7 * u
    def gate(x, y_, vertical):
        c.setStrokeColor(HexColor("#D9C9AA")); c.setLineWidth(2.6 * u)
        if vertical:
            c.line(x, y_ - gate_w / 2, x, y_ + gate_w / 2)
        else:
            c.line(x - gate_w / 2, y_, x + gate_w / 2, y_)
        c.setFillColor(CRAN)
        for dx, dy in ([(0, -gate_w / 2), (0, gate_w / 2)] if vertical else [(-gate_w / 2, 0), (gate_w / 2, 0)]):
            c.circle(x + dx, y_ + dy, 1.3 * u, fill=1, stroke=0)
    gate(cx, wt, False); gate(cx, wb, False); gate(wl, cyy, True); gate(wr, cyy, True)
    c.setFillColor(GREEN); c.setFont("Nunito-ExtraBold", 7.5 * Lx.s)
    c.drawRightString(cx - 5 * u, wt + 2.4 * u, "BRAMBLE GATE")
    c.drawString(cx + 5 * u, wb - 4.6 * u, "ORCHARD GAP")
    c.saveState(); c.translate(wl - 2.6 * u, cyy - 15 * u); c.rotate(90)
    c.drawCentredString(0, 0, "MILL STILE"); c.restoreState()
    c.saveState(); c.translate(wr + 3 * u, cyy - 15 * u); c.rotate(90)
    c.drawCentredString(0, 0, "CHURCH LYCHGATE"); c.restoreState()
    # Quell's Apothecary on the edge of the green, outside the hedge by Bramble Gate
    aw = pdfmetrics.stringWidth("Quell’s Apothecary", "Nunito-Bold", 6.6 * Lx.s) + 7.5 * u
    ax, ay = wr - aw - 2 * u, wt + 2.2 * u
    c.setFillColor(PARCH); c.setStrokeColor(GREEN); c.setLineWidth(1)
    c.rect(ax, ay, aw, 6.5 * u, fill=1, stroke=1)
    p = c.beginPath(); p.moveTo(ax - 1 * u, ay + 6.5 * u); p.lineTo(ax + aw / 2, ay + 9.4 * u); p.lineTo(ax + aw + 1 * u, ay + 6.5 * u); p.close()
    c.setFillColor(AUB); c.drawPath(p, fill=1, stroke=0)
    c.setStrokeColor(CRAN); c.setLineWidth(1.6)
    c.line(ax + aw - 4.6 * u, ay + 1.6 * u, ax + aw - 2 * u, ay + 4.4 * u); c.line(ax + aw - 4.6 * u, ay + 4.4 * u, ax + aw - 2 * u, ay + 1.6 * u)
    c.setFillColor(INK); c.setFont("Nunito-Bold", 6.6 * Lx.s)
    c.drawString(ax + 1.2 * u, ay + 2.2 * u, "Quell’s Apothecary")
    # stall rows
    inner_w = wr - wl - 6 * u
    sw = inner_w / 9 * 0.84; gap = inner_w / 9 * 0.16
    sh = 6.2 * u
    rows_y = [wt - 4.5 * u - sh, wt - 17 * u - sh, wb + 19.5 * u, wb + 7 * u]
    for li, lane in enumerate(C.LANES):
        ry = rows_y[li]
        for k in range(9):
            num = li * 9 + k + 1
            sx = wl + 3 * u + k * (sw + gap) + gap / 2
            stall_icon(c, sx, ry, sw, sh, num, CRAN if li % 2 == 0 else AUB, font=7.5 * Lx.s)
        c.setFillColor(AUB); c.setFont("Fraunces-SemiBold", 8.5 * Lx.s)
        c.drawCentredString(cx, ry - 3.4 * u, lane.upper())
    # middle of the green: the great cauldron and Mother Meridew's tent
    mid = (rows_y[1] - 3.4 * u + rows_y[2] + sh) / 2
    cauldron(c, cx - 24 * u, mid - 0.4 * u, 2.6 * u)
    c.setFillColor(INK); c.setFont("Nunito-Bold", 7 * Lx.s)
    c.drawString(cx - 20 * u, mid - 1.6 * u, "Great Cauldron")
    tx = cx + 4 * u
    p = c.beginPath(); p.moveTo(tx - 4.2 * u, mid - 3.4 * u); p.lineTo(tx, mid + 3.6 * u); p.lineTo(tx + 4.2 * u, mid - 3.4 * u); p.close()
    c.setFillColor(AUB); c.drawPath(p, fill=1, stroke=0)
    c.setFillColor(MUST); c.circle(tx, mid - 0.6 * u, 0.7 * u, fill=1, stroke=0)
    star(c, tx, mid + 4.8 * u, 1.0 * u, MUST)
    c.setFillColor(INK); c.drawString(tx + 5.6 * u, mid - 1.6 * u, "Mother Meridew’s tent")
    # compass
    qx, qy = ox + 4.5 * u, oy + size - 6 * u
    c.setFillColor(GREEN); p = c.beginPath(); p.moveTo(qx, qy + 4 * u); p.lineTo(qx - 1.4 * u, qy)
    p.lineTo(qx + 1.4 * u, qy); p.close(); c.drawPath(p, fill=1, stroke=0)
    c.setFont("Nunito-ExtraBold", 7 * Lx.s); c.drawCentredString(qx, qy - 3 * u, "N")
    # legend
    ly2 = oy - 14 * Lx.s
    items = [("stall", "Stall (number)"), ("stone", "Standing stone"), ("path", "Footpath"),
             ("gate", "Entrance"), ("shop", "Quell’s Apothecary, where the body was found")]
    lx2 = Lx.m; fs = 7.6 * Lx.s
    for kind, text in items:
        if kind == "stall":
            stall_icon(c, lx2, ly2 - 8, 14, 11, "", CRAN, 5)
        elif kind == "stone":
            standing_stone(c, lx2 + 7, ly2 - 8, 11)
        elif kind == "path":
            c.setStrokeColor(HexColor("#B39C7A")); c.setLineWidth(4); c.line(lx2, ly2 - 3, lx2 + 14, ly2 - 3)
        elif kind == "gate":
            c.setFillColor(CRAN); c.circle(lx2 + 3, ly2 - 3, 2.2, fill=1, stroke=0); c.circle(lx2 + 11, ly2 - 3, 2.2, fill=1, stroke=0)
        else:
            c.setStrokeColor(CRAN); c.setLineWidth(1.4); c.line(lx2 + 3, ly2 - 7, lx2 + 11, ly2 + 1); c.line(lx2 + 3, ly2 + 1, lx2 + 11, ly2 - 7)
        c.setFillColor(INK); c.setFont("Nunito", fs); c.drawString(lx2 + 18, ly2 - 6, text)
        lx2 += 18 + pdfmetrics.stringWidth(text, "Nunito", fs) + 13
        if lx2 > Lx.W - Lx.m - 150 and kind != items[-1][0]:
            lx2 = Lx.m; ly2 -= 18 * Lx.s

# ---- evidence 2: stall directory
def draw_directory(b):
    c, Lx = b.c, b.L
    y = b.title_block("Evidence 2", "Stall directory")
    y = para(c, "From the Moon Fair programme. Each stall’s lane is also shown on the fair map; the brews "
                "are described in the Book of Brews.", Lx.m, y, Lx.cw, Lx.small)
    cols = [("No.", 34), ("Stall", 150), ("Lane", 112), ("Sells", Lx.cw - 296)]
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

# ---- evidence 3: the Book of Brews
def draw_brews(b):
    c, Lx = b.c, b.L
    y = b.title_block("Evidence 3", "The Book of Brews")
    y = para(c, "The Hearth Circle’s recipe book: every brew served at the Moon Fair and everything that "
                "goes into it. Nothing else is added at the stalls.", Lx.m, y, Lx.cw, Lx.small)
    keys = list(C.BREWS)
    ncol = 3; gap = 12 * Lx.s
    cw = (Lx.cw - gap) / ncol
    nrow = math.ceil(len(keys) / ncol)
    ch = min(170 * Lx.s, (y - Lx.bottom - 10 - gap * (nrow - 1)) / nrow)
    for i, k in enumerate(keys):
        name, ing = C.BREWS[k]
        col, row = i % ncol, i // ncol
        if i == len(keys) - 1 and len(keys) % ncol:
            x0 = Lx.m + (Lx.cw - cw) / 2
        else:
            x0 = Lx.m + col * (cw + gap)
        y0 = y - 6 - row * (ch + gap)
        c.setFillColor(PARCH); c.setStrokeColor(RULE); c.setLineWidth(0.6)
        c.roundRect(x0, y0 - ch, cw, ch, 8, fill=1, stroke=1)
        c.setFillColor(AUB); c.rect(x0, y0 - 6 * Lx.s, cw, 6 * Lx.s, fill=1, stroke=0)
        cup_x = x0 + cw - 26 * Lx.s; cup_y = y0 - ch + 26 * Lx.s
        c.setFillColor(CRAN); c.roundRect(cup_x - 11 * Lx.s, cup_y - 12 * Lx.s, 20 * Lx.s, 22 * Lx.s, 4, fill=1, stroke=0)
        c.setStrokeColor(CRAN); c.setLineWidth(2.2 * Lx.s); c.circle(cup_x + 11 * Lx.s, cup_y, 5.5 * Lx.s, fill=0, stroke=1)
        c.setStrokeColor(SOFT); c.setLineWidth(1)
        for dx in (-5, 1):
            c.bezier(cup_x + dx * Lx.s, cup_y + 13 * Lx.s, cup_x + (dx + 4) * Lx.s, cup_y + 18 * Lx.s,
                     cup_x + (dx - 3) * Lx.s, cup_y + 22 * Lx.s, cup_x + (dx + 1) * Lx.s, cup_y + 27 * Lx.s)
        c.setFillColor(GREEN)
        fsn = 13 * Lx.s
        while pdfmetrics.stringWidth(name, "Fraunces-SemiBold", fsn) > cw - 22 * Lx.s:
            fsn -= 0.5
        c.setFont("Fraunces-SemiBold", fsn)
        c.drawString(x0 + 12 * Lx.s, y0 - 26 * Lx.s, name)
        c.setFont("Nunito-ExtraBold", 7.5 * Lx.s); c.setFillColor(CRAN)
        c.drawString(x0 + 12 * Lx.s, y0 - 40 * Lx.s, "WHAT GOES IN")
        c.setFont("Nunito", 10 * Lx.s); c.setFillColor(INK)
        yy = y0 - 54 * Lx.s
        lh = min(15 * Lx.s, (ch - 62 * Lx.s) / max(len(ing), 1))
        for it in ing:
            c.setFillColor(MOSS); c.circle(x0 + 15 * Lx.s, yy + 3 * Lx.s, 2 * Lx.s, fill=1, stroke=0)
            c.setFillColor(INK); c.drawString(x0 + 22 * Lx.s, yy, it)
            yy -= lh

# ---- evidence 4: the moon-watcher's log
def draw_moon(b):
    c, Lx = b.c, b.L
    y = b.title_block("Evidence 4", "Moon-watcher’s log")
    c.setFillColor(PARCH); bh = 38 * Lx.s
    c.rect(Lx.m, y - bh, Lx.cw, bh, fill=1, stroke=0)
    c.setFillColor(GREEN); c.setFont("Nunito-ExtraBold", 10 * Lx.s)
    c.drawString(Lx.m + 12, y - 16 * Lx.s, "THE MORROWMERE MOON-WATCH")
    c.setFont("Nunito", 9 * Lx.s); c.setFillColor(INK)
    c.drawString(Lx.m + 12, y - 29 * Lx.s, f"Kept by {C.WATCHER} from the church tower, {C.DATE}. "
                 "Times are inclusive, to the minute.")
    full_moon(c, Lx.W - Lx.m - 24 * Lx.s, y - bh / 2, 13 * Lx.s, MUST)
    y -= bh + 18
    cols = [("From", 70), ("To", 70), ("The sky over the green", 240), ("", Lx.cw - 380)]
    rh = 30 * Lx.s; fs = 11 * Lx.s
    c.setFont("Nunito-ExtraBold", 9 * Lx.s); c.setFillColor(CRAN)
    x = Lx.m
    for n, w in cols:
        c.drawString(x + 6, y - 12, n.upper()); x += w
    y -= 18; c.setStrokeColor(GREEN); c.line(Lx.m, y, Lx.W - Lx.m, y)
    for a, bb, sky, vis in C.MOON_LOG:
        c.setFillColor(PALE if vis else WHITE); c.rect(Lx.m, y - rh, Lx.cw, rh, fill=1, stroke=0)
        c.setFillColor(INK); c.setFont("Nunito-Bold", fs)
        c.drawString(Lx.m + 6, y - rh / 2 - fs / 3, a); c.drawString(Lx.m + 76, y - rh / 2 - fs / 3, bb)
        c.setFont("Nunito", fs); c.drawString(Lx.m + 146, y - rh / 2 - fs / 3, sky)
        ix = Lx.m + 400 * Lx.s
        if vis:
            full_moon(c, ix, y - rh / 2, 9 * Lx.s, MUST)
        elif "below" in sky:
            c.setStrokeColor(SOFT); c.setLineWidth(1); c.line(ix - 12 * Lx.s, y - rh / 2 - 3, ix + 12 * Lx.s, y - rh / 2 - 3)
        else:
            full_moon(c, ix - 3 * Lx.s, y - rh / 2 + 3 * Lx.s, 7 * Lx.s, HexColor("#E8D9B0"))
            cloud(c, ix + 2 * Lx.s, y - rh / 2 - 3 * Lx.s, 22 * Lx.s, STONE)
        y -= rh
        c.setStrokeColor(RULE); c.setLineWidth(0.5); c.line(Lx.m, y, Lx.W - Lx.m, y)
    # timeline bar
    y -= 34
    t0, t1 = C.tmin("16:00"), C.tmin("21:00")
    x0, x1 = Lx.m + 10, Lx.W - Lx.m - 10
    def X(t):
        return x0 + (x1 - x0) * (t - t0) / (t1 - t0)
    c.setFillColor(HexColor("#E9E3D6")); c.rect(x0, y - 18, x1 - x0, 18, fill=1, stroke=0)
    for a, bb in C.MOON_WINDOWS:
        c.setFillColor(GREEN); c.rect(X(a), y - 18, X(bb + 1) - X(a), 18, fill=1, stroke=0)
        full_moon(c, (X(a) + X(bb + 1)) / 2, y - 9, 6, MUST)
    c.setFont("Nunito", 8 * Lx.s); c.setFillColor(INK)
    for h in range(16, 22):
        c.drawCentredString(X(h * 60), y - 32, f"{h}:00")
        c.setStrokeColor(SOFT); c.line(X(h * 60), y - 22, X(h * 60), y - 18)
    c.setFont("Nunito-Italic", 8 * Lx.s); c.setFillColor(SOFT)
    c.drawString(x0, y + 6, "The evening at a glance (dark bands = full moon in clear sky)")
    y -= 64
    para(c, "<i>Watcher’s note: from the tower I can see the whole green, the meadow and the Hob Stones "
            "at once. When the moon was out, it was out for all of them; when cloud covered it, it was "
            "hidden for all of them.</i>", Lx.m, y, Lx.cw, Lx.small)

# ---- evidence 5: Mother Meridew's reading book & Bryony's note
def draw_reading(b):
    c, Lx = b.c, b.L
    s = Lx.s
    y = b.title_block("Evidence 5", "The reading book & Bryony’s note")
    y = para(c, f"Above: a page from {C.READER}’s reading book. Below: the note {C.WITNESS} left for the "
                "Inspector.", Lx.m, y, Lx.cw, Lx.small)
    # the reading book: a ruled page with handwritten rows
    cols = [("Time", 48 * s), ("Who sat", 128 * s), ("The cup", Lx.cw - 300 * s), ("The leaves showed", 124 * s)]
    hand = ParagraphStyle("hand", fontName="Caveat", fontSize=12.6 * s, leading=13.4 * s, textColor=HexColor("#3B2A55"), spaceAfter=0)
    rows = []
    for t, who, cup, leaves in C.READINGS:
        hh = max(para_h(esc(v), w - 10, hand) for v, (_, w) in zip((t, who, cup, leaves), cols)) + 10 * s
        rows.append((t, who, cup, leaves, hh))
    head_h = 46 * s
    bh = head_h + sum(r[-1] for r in rows) + 16 * s
    top = y - 4
    c.setFillColor(HexColor("#FBF7EE")); c.setStrokeColor(RULE); c.setLineWidth(0.8)
    c.rect(Lx.m, top - bh, Lx.cw, bh, fill=1, stroke=1)
    c.setFillColor(AUB); c.rect(Lx.m, top - 22 * s, Lx.cw, 22 * s, fill=1, stroke=0)
    c.setFillColor(PARCH); c.setFont("Nunito-ExtraBold", 8.5 * s)
    c.drawString(Lx.m + 10, top - 15 * s, "MOTHER MERIDEW · READINGS AT THE MOON FAIR · ONE EVERY QUARTER HOUR")
    star(c, Lx.W - Lx.m - 14 * s, top - 11 * s, 6 * s, MUST)
    x = Lx.m; c.setFillColor(CRAN); c.setFont("Nunito-ExtraBold", 7.6 * s)
    for n, w in cols:
        c.drawString(x + 6, top - 36 * s, n.upper()); x += w
    yy = top - head_h
    c.setStrokeColor(GREEN); c.setLineWidth(0.8); c.line(Lx.m, yy + 4, Lx.W - Lx.m, yy + 4)
    for t, who, cup, leaves, hh in rows:
        x = Lx.m
        for v, (_, w) in zip((t, who, cup, leaves), cols):
            para(c, esc(v), x + 6, yy - 2, w - 10, hand); x += w
        yy -= hh
        c.setStrokeColor(HexColor("#C9D3E4")); c.setLineWidth(0.6); c.line(Lx.m + 4, yy + 3, Lx.W - Lx.m - 4, yy + 3)
    c.setFont("Caveat", 12 * s); c.setFillColor(HexColor("#3B2A55"))
    c.drawRightString(Lx.W - Lx.m - 10, top - bh + 6 * s, "Honey makes the leaves clump, so I always write it down. — M.M.")
    # Bryony's note
    y2 = top - bh - 22 * s
    nh = min(250 * s, y2 - Lx.bottom - 10)
    nw = min(Lx.cw * 0.74, 400 * s)
    nx, ny = Lx.m + (Lx.cw - nw) / 2, y2 - nh
    c.saveState(); c.translate(nx + nw / 2, ny + nh / 2); c.rotate(-1.8)
    c.setFillColor(HexColor("#E8E2D8")); c.rect(-nw / 2 + 4, -nh / 2 - 4, nw, nh, fill=1, stroke=0)
    c.setFillColor(HexColor("#FFFDF7")); c.setStrokeColor(RULE); c.rect(-nw / 2, -nh / 2, nw, nh, fill=1, stroke=1)
    lh = (nh - 30 * s) / (len(C.NOTE) + 0.4)
    c.setStrokeColor(HexColor("#D6CDE4")); c.setLineWidth(0.6)
    yy = nh / 2 - 22 * s
    for _ in range(len(C.NOTE)):
        c.line(-nw / 2 + 6, yy - 5, nw / 2 - 6, yy - 5); yy -= lh
    c.setFillColor(HexColor("#2A3A63"))
    fsz = min(15 * s, lh * 0.95)
    maxw = max(pdfmetrics.stringWidth(t, "Caveat", fsz) for t in C.NOTE)
    if maxw > nw - 40 * s:
        fsz *= (nw - 40 * s) / maxw
    c.setFont("Caveat", fsz)
    yy = nh / 2 - 22 * s
    for t in C.NOTE:
        c.drawString(-nw / 2 + 24 * s, yy, t); yy -= lh
    c.setFillColor(Color(0.89, 0.65, 0.29, alpha=0.55))
    c.rect(-24 * s, nh / 2 - 8 * s, 48 * s, 16 * s, fill=1, stroke=0)
    c.restoreState()

# ---- evidence 6: the shop ledger & the carrier's rounds
def draw_ledger(b):
    c, Lx = b.c, b.L
    s = Lx.s
    y = b.title_block("Evidence 6", "Shop ledger & carrier’s rounds")
    y = para(c, f"Above: the day ledger at {C.SHOP}, kept by {C.SHOPBOY}. Below: the village carrier’s "
                "weekly rounds, pinned up behind the shop counter.", Lx.m, y, Lx.cw, Lx.small)
    hand = ParagraphStyle("lh", fontName="Caveat", fontSize=12.6 * s, leading=14 * s, textColor=HexColor("#2E2440"), spaceAfter=0)
    cols = [("Time", 52 * s), ("Item", Lx.cw - 140 * s), ("Paid", 88 * s)]
    rows = [(t, it, pd, max(para_h(esc(it), cols[1][1] - 12, hand) + 8 * s, 20 * s)) for t, it, pd in C.LEDGER]
    sig_h = 66 * s
    bh = 44 * s + sum(r[-1] for r in rows) + sig_h + 12 * s
    top = y - 4
    c.setFillColor(HexColor("#FBF7EE")); c.setStrokeColor(RULE); c.setLineWidth(0.8)
    c.rect(Lx.m, top - bh, Lx.cw, bh, fill=1, stroke=1)
    c.setStrokeColor(HexColor("#E2A9A9")); c.setLineWidth(0.8)
    c.line(Lx.m + cols[0][1], top - 26 * s, Lx.m + cols[0][1], top - bh + 4)
    c.setFillColor(GREEN); c.setFont("Fraunces-SemiBold", 12 * s)
    c.drawString(Lx.m + 10, top - 18 * s, f"{C.SHOP} · Day ledger · {C.DATE}")
    x = Lx.m; c.setFillColor(CRAN); c.setFont("Nunito-ExtraBold", 7.6 * s)
    for n, w in cols:
        c.drawString(x + 6, top - 36 * s, n.upper()); x += w
    yy = top - 44 * s
    for t, it, pd, hh in rows:
        c.setFont("Caveat", 12.6 * s); c.setFillColor(HexColor("#2E2440"))
        c.drawString(Lx.m + 6, yy - 12 * s, t)
        para(c, esc(it), Lx.m + cols[0][1] + 6, yy - 1, cols[1][1] - 12, hand)
        c.drawRightString(Lx.W - Lx.m - 10, yy - 12 * s, pd)
        yy -= hh
        c.setStrokeColor(HexColor("#C9D3E4")); c.setLineWidth(0.6); c.line(Lx.m + 4, yy + 3, Lx.W - Lx.m - 4, yy + 3)
    c.setFont("Caveat", 12.6 * s); c.setFillColor(HexColor("#2E2440"))
    c.drawString(Lx.m + cols[0][1] + 6, yy - 18 * s, "Signed:")
    scribble(c, Lx.m + cols[0][1] + 52 * s, yy - 22 * s, 58 * s, 16 * s, HexColor("#1F2E5C"))
    # Tobias's margin note, in pencil
    note_w = 196 * s
    nx = Lx.W - Lx.m - note_w - 4; ny = yy - 36 * s
    c.saveState(); c.translate(nx, ny); c.rotate(3)
    c.setFont("Caveat", 12 * s); c.setFillColor(HexColor("#6A6470"))
    for i, t in enumerate(C.LEDGER_NOTE):
        c.drawString(0, 22 * s - i * 12.5 * s, t)
    c.restoreState()
    # carrier's rounds
    y2 = top - bh - 22 * s
    c.setFillColor(GREEN); bh2 = 40 * s
    c.roundRect(Lx.m, y2 - bh2, Lx.cw, bh2, 6, fill=1, stroke=0)
    c.setFillColor(PARCH); c.setFont("Fraunces-SemiBold", 14 * s)
    c.drawString(Lx.m + 14, y2 - 18 * s, "Morrowmere Village Carrier")
    c.setFont("Nunito", 8.6 * s)
    c.drawString(Lx.m + 14, y2 - 31 * s, f"{C.CARRIER}, carrier · parcels left at the Apothecary go out on the "
                 "round named · one round a day, Morrowmere first")
    y2 -= bh2 + 10
    st = ParagraphStyle("cell", parent=Lx.body, fontSize=10 * s, leading=13 * s, spaceAfter=0)
    for i, (day, towns) in enumerate(C.ROUNDS):
        txt = ", ".join(towns)
        h = max(22 * s, para_h(esc(txt), Lx.cw - 120 * s, st) + 9 * s)
        c.setFillColor(PALE if i % 2 else WHITE); c.rect(Lx.m, y2 - h, Lx.cw, h, fill=1, stroke=0)
        c.setFillColor(INK); c.setFont("Nunito-ExtraBold", 10.5 * s); c.drawString(Lx.m + 8, y2 - 15 * s, day)
        para(c, esc(txt), Lx.m + 110 * s, y2 - 5 * s, Lx.cw - 120 * s, st)
        y2 -= h; c.setStrokeColor(RULE); c.setLineWidth(0.5); c.line(Lx.m, y2, Lx.W - Lx.m, y2)
    c.setFont("Nunito-Italic", 8.5 * s); c.setFillColor(SOFT)
    c.drawString(Lx.m, y2 - 14 * s, "The carrier calls only at the villages listed for each day. No rounds on Sunday.")

# ---- notebook
def draw_notebook(b):
    c, Lx = b.c, b.L
    y = b.title_block(C.INSPECTOR, "The Inspector’s Notebook")
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
    y = para(c, f"Every moon token scanned at the fair entrances on {C.DATE}, in the order it was scanned. "
                "Each line is one visitor.", Lx.m, y, Lx.cw, Lx.body)
    rows = [("Entry", "time the token was scanned at the entrance (24-hour clock)"),
            ("Ticket", "ticket and token number, 0001–6000"),
            ("First name, Surname", "as given when the ticket was bought"),
            ("Home village", "as given when the ticket was bought"),
            ("Entrance", "Bramble (Bramble Gate), Mill (Mill Stile), Church (Church Lychgate) or Orchard (Orchard Gap)"),
            ("Last stall", "number of the stall where the token made its final purchase"),
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
        star(c, Lx.m + 30 + (i * 53) % (Lx.cw - 40), Lx.top - 60 - (i * 97) % (Lx.top - Lx.bottom - 160),
             7, MUST)
    full_moon(c, Lx.W / 2, Lx.H / 2 + 130 * Lx.s, 30 * Lx.s, MUST)
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
    for p in ["Thank you for spending a moonlit night at the Morrowmere Moon Fair. We hope the "
              "lanterns, the brews and the silver crescent pin kept you guessing.",
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
                        f"by {C.GATE_NAMES[K['gate']]} · last stall {K['stall']}")
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
    fcols = [("Ticket", 46), ("Visitor", 118), ("Village", 84), ("Entrance", 50), ("Entry", 40), ("Stall", 34),
             ("Ruled out by", Lx.cw - 372)]
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
