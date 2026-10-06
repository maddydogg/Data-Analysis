"""Render The Keeper of Candleholm to PDF: the calendar (print Letter, print A4, iPad) and the
solution file (the Envelope) in the same three formats.

All graphics are drawn with code: the vignettes and the cover come from scenes.py / cover.py
(Pillow); the chart of the Sound, the lighthouse in section and the papers are drawn here with
ReportLab. Inside pages stay light to save ink; each window has its own small vignette.
"""
import math, os
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import LETTER, A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
import case as C
import hints as H
import generate as G

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")
ARTDIR = os.path.join(HERE, "art")

# ------------------------------------------------------------------ palette (light pages)
def hx(t):
    return HexColor("#%02X%02X%02X" % t)
INK = HexColor("#2B2A2A"); NAVY = HexColor("#23465A"); SEA = HexColor("#2F6074"); STEEL = HexColor("#5B6670")
SOFT = HexColor("#7A7F84"); CREAM = HexColor("#F3EAD7"); PALE = HexColor("#FAF6EC"); RULE = HexColor("#DCD3BF")
RUST = HexColor("#B5452F"); RUST_D = HexColor("#842E20"); RUST_L = HexColor("#F2DCD3"); OCHRE = HexColor("#D7A548")
OCHRE_L = HexColor("#F6E7C4"); MOSS = HexColor("#6B7B4B"); MOSS_L = HexColor("#DDE3CF"); WATER = HexColor("#DCE8EA")
WATER_D = HexColor("#9FBEC4"); LAND = HexColor("#F1EBDB"); WHITE = HexColor("#FFFFFF"); PAPER = HexColor("#FBF7EE")
BRASS = HexColor("#C49C48"); COPPER = HexColor("#B86C42"); TIN = HexColor("#B0B4B6")

def register_fonts():
    for name, f in [("Fraunces", "Fraunces-Regular"), ("Fraunces-SemiBold", "Fraunces-SemiBold"),
                    ("Fraunces-Bold", "Fraunces-Bold"), ("Fraunces-Italic", "Fraunces-Italic"),
                    ("Nunito", "Nunito-Regular"), ("Nunito-Bold", "Nunito-Bold"), ("Nunito-ExtraBold", "Nunito-ExtraBold"),
                    ("Nunito-Italic", "Nunito-Italic"), ("Kalam", "Kalam-Regular"), ("Kalam-Bold", "Kalam-Bold"),
                    ("Courier Prime", "CourierPrime-Regular"), ("Courier Prime-Bold", "CourierPrime-Bold"),
                    ("Josefin", "JosefinSans-Bold"), ("Josefin-Semi", "JosefinSans-SemiBold")]:
        pdfmetrics.registerFont(TTFont(name, os.path.join(FONTS, f + ".ttf")))
    addMapping("Nunito", 0, 0, "Nunito"); addMapping("Nunito", 1, 0, "Nunito-Bold")
    addMapping("Nunito", 0, 1, "Nunito-Italic"); addMapping("Nunito", 1, 1, "Nunito-Bold")
    addMapping("Fraunces", 0, 0, "Fraunces"); addMapping("Fraunces", 1, 0, "Fraunces-SemiBold")
    addMapping("Fraunces", 0, 1, "Fraunces-Italic"); addMapping("Fraunces", 1, 1, "Fraunces-SemiBold")
    addMapping("Courier Prime", 0, 0, "Courier Prime"); addMapping("Courier Prime", 1, 0, "Courier Prime-Bold")
    addMapping("Courier Prime", 0, 1, "Courier Prime"); addMapping("Courier Prime", 1, 1, "Courier Prime-Bold")
    addMapping("Kalam", 0, 0, "Kalam"); addMapping("Kalam", 1, 0, "Kalam-Bold")
    addMapping("Kalam", 0, 1, "Kalam"); addMapping("Kalam", 1, 1, "Kalam-Bold")

IPAD = (768, 1024)
FORMATS = {"letter": LETTER, "a4": A4, "ipad": IPAD}

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

class L:
    def __init__(self, fmt):
        self.fmt = fmt
        self.W, self.H = FORMATS[fmt]
        self.ipad = fmt == "ipad"
        self.m = 46 if self.ipad else 50
        self.s = 1.18 if self.ipad else 1.0
        self.cw = self.W - 2 * self.m
        self.top = self.H - self.m - 24
        self.bottom = self.m + 16
        s = self.s
        self.body = ParagraphStyle("body", fontName="Nunito", fontSize=10.2 * s, leading=14.6 * s, textColor=INK, spaceAfter=5 * s)
        self.small = ParagraphStyle("small", parent=self.body, fontSize=8.9 * s, leading=12.2 * s)
        self.h1 = ParagraphStyle("h1", fontName="Fraunces-SemiBold", fontSize=25 * s, leading=29 * s, textColor=NAVY, spaceAfter=3 * s)
        self.h2 = ParagraphStyle("h2", fontName="Fraunces-SemiBold", fontSize=14.5 * s, leading=18 * s, textColor=NAVY, spaceAfter=3 * s)
        self.hand = ParagraphStyle("hand", fontName="Kalam", fontSize=11.6 * s, leading=15.4 * s, textColor=HexColor("#2A3550"), spaceAfter=0)
        self.typed = ParagraphStyle("typed", fontName="Courier Prime", fontSize=9.2 * s, leading=12.4 * s, textColor=INK, spaceAfter=2 * s)

def para(c, text, x, y, w, style):
    p = Paragraph(text, style)
    _, h = p.wrap(w, 10000)
    p.drawOn(c, x, y - h)
    return y - h - style.spaceAfter

def para_h(text, w, style):
    return Paragraph(text, style).wrap(w, 10000)[1] + style.spaceAfter

def spaced(c, x, y, text, font, size, gap=1.2, col=None, anchor="l"):
    """Letter-spaced capitals (Josefin kickers)."""
    if col is not None:
        c.setFillColor(col)
    w = sum(pdfmetrics.stringWidth(ch, font, size) for ch in text) + gap * (len(text) - 1)
    xx = x - w / 2 if anchor == "c" else (x - w if anchor == "r" else x)
    c.saveState()
    t = c.beginText(xx, y); t.setFont(font, size); t.setCharSpace(gap); t.textOut(text); t.setCharSpace(0); c.drawText(t)
    c.restoreState()
    return w

# ------------------------------------------------------------------ art files
def art_path(key):
    return os.path.join(ARTDIR, f"scene_{key}.jpg")

def ensure_art(force=False):
    import scenes
    os.makedirs(ARTDIR, exist_ok=True)
    for d in range(1, 25):
        p = art_path(d)
        if force or not os.path.exists(p):
            scenes.scene(d, 1600, 500).save(p, quality=86)

# ------------------------------------------------------------------ book
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
            self.c.addOutlineEntry(outline, key, level=level)
        if chrome:
            self.chrome(header)

    def chrome(self, header):
        c, Lx = self.c, self.L
        c.setFillColor(NAVY); c.setFont("Fraunces-Italic", 9.3 * Lx.s)
        c.drawString(Lx.m, Lx.H - Lx.m + 2, C.TITLE)
        if header:
            spaced(c, Lx.W - Lx.m, Lx.H - Lx.m + 2, header.upper(), "Josefin-Semi", 8.4 * Lx.s, 1.0, STEEL, "r")
        c.setStrokeColor(RUST); c.setLineWidth(1.1)
        c.line(Lx.m, Lx.H - Lx.m - 6, Lx.W - Lx.m, Lx.H - Lx.m - 6)
        c.setStrokeColor(NAVY); c.setLineWidth(0.5)
        c.line(Lx.m, Lx.H - Lx.m - 8.5, Lx.W - Lx.m, Lx.H - Lx.m - 8.5)
        c.setFont("Nunito", 8 * Lx.s); c.setFillColor(SOFT)
        c.drawCentredString(Lx.W / 2, Lx.m - 16, str(self.page))
        c.drawRightString(Lx.W - Lx.m, Lx.m - 16, C.BRAND)
        tower_icon(c, Lx.m + 4, Lx.m - 19, 11, NAVY)

    def title_block(self, kicker, title, y=None):
        Lx = self.L; y = y or Lx.top
        spaced(self.c, Lx.m, y - 10 * Lx.s, kicker.upper(), "Josefin", 9.6 * Lx.s, 1.4, RUST_D)
        return para(self.c, esc(title), Lx.m, y - 15 * Lx.s, Lx.cw, Lx.h1)

    def link(self, key, x0, y0, x1, y1):
        self.c.linkAbsolute("", key, (x0, y0, x1, y1), thickness=0)

    def save(self):
        self.c.showPage(); self.c.save()

# ------------------------------------------------------------------ small vector pieces
def tower_icon(c, x, y, h, col):
    c.saveState(); c.setFillColor(col)
    p = c.beginPath(); p.moveTo(x - h * 0.17, y); p.lineTo(x - h * 0.1, y + h * 0.72); p.lineTo(x + h * 0.1, y + h * 0.72)
    p.lineTo(x + h * 0.17, y); p.close(); c.drawPath(p, fill=1, stroke=0)
    c.setFillColor(OCHRE); c.rect(x - h * 0.08, y + h * 0.74, h * 0.16, h * 0.12, fill=1, stroke=0)
    c.setFillColor(RUST); p = c.beginPath(); p.moveTo(x - h * 0.12, y + h * 0.86); p.lineTo(x, y + h); p.lineTo(x + h * 0.12, y + h * 0.86)
    p.close(); c.drawPath(p, fill=1, stroke=0); c.restoreState()

def checkbox(c, x, y, s, col=STEEL):
    c.saveState(); c.setStrokeColor(col); c.setLineWidth(0.8); c.roundRect(x, y, s, s, 1.6, fill=0, stroke=1); c.restoreState()

def card(c, x, y_top, w, h, fill=PALE, stroke=RULE, r=6):
    c.saveState(); c.setFillColor(fill); c.setStrokeColor(stroke); c.setLineWidth(0.8)
    c.roundRect(x, y_top - h, w, h, r, fill=1, stroke=1); c.restoreState()

def pin(c, x, y, s=5):
    c.saveState(); c.setFillColor(RUST); c.circle(x, y, s, fill=1, stroke=0)
    c.setFillColor(HexColor("#E48A72")); c.circle(x - s * 0.3, y + s * 0.3, s * 0.35, fill=1, stroke=0); c.restoreState()

# ------------------------------------------------------------------ the Sound Book data
def load_rows():
    return G.load(os.path.join(HERE, "data"))

def log_items(rows):
    items, day = [], None
    for r in rows:
        if r["day"] != day:
            day = r["day"]; items.append(("band", day))
        items.append(("rec", r))
    return items

LOG_COLS = [("Date", 34), ("Time", 34), ("Tally", 32), ("First name", 64), ("Surname", 80), ("Home", 72), ("Boat", 44),
            ("Landing", 38), ("", 18)]

def log_geometry(Lx):
    rh = 13.4 if Lx.ipad else 11.2
    avail = Lx.top - 46 - Lx.bottom
    return rh, int(avail // rh) - 1

def paginate_log(rows, Lx):
    rh, per = log_geometry(Lx)
    items = log_items(rows); pages = []; i = 0
    while i < len(items):
        chunk = items[i:i + per]
        if chunk and chunk[-1][0] == "band":
            chunk = chunk[:-1]
        pages.append(chunk); i += len(chunk)
    return pages

# ------------------------------------------------------------------ plan of the book
def window_date(d):
    return f"{d} December"

def book_plan(rows, Lx):
    P = []
    add = lambda key, title, level, fn, header="": P.append((key, title, level, fn, header))
    if Lx.ipad:
        add("calendar", "The calendar", 0, draw_calendar, "Advent calendar")
        add("cover", "Cover", 0, draw_cover)
    else:
        add("cover", None, None, draw_cover)
    add("howto", "How to play", 0, draw_howto, "Before you begin")
    add("contents", "Contents", 0, draw_contents, "Contents")
    add("rules", "House rules", 0, draw_rules, "House rules")
    if not Lx.ipad:
        add("calendar", "Your advent calendar", 0, draw_calendar, "Advent calendar")
        add("envelope", "Envelope template", 0, draw_envelope, "Set-up")
        add("labels", "Day numbers for the envelopes", 0, draw_labels, "Set-up")
    add("w1", "Window 1 — The Case", 0, draw_w1_case, "Window 1")
    add("w1journal", "Ezra’s journal, 1 December", 1, draw_w1_journal, "Window 1")
    add("w1tower", "The tower and the island", 1, draw_w1_tower, "Window 1")
    add("w1chart", "The chart of the Sound", 1, draw_w1_chart, "Window 1")
    add("w1words", "The chart in words", 1, draw_w1_words, "Window 1")
    add("w2", "Window 2 — The Sound Book", 0, draw_w2_intro, "Window 2")
    seen = set()
    for i, chunk in enumerate(paginate_log(rows, Lx)):
        title = None
        for it in chunk:
            if it[0] == "band" and it[1] not in seen:
                seen.add(it[1]); title = f"{it[1]} December"; break
        add(f"log{i}", title, 1 if title else None, (lambda b, chunk=chunk: draw_log_page(b, chunk)), "Window 2 · The Sound Book")
    for cl in C.CLUES:
        d = cl["day"]
        add(f"w{d}", f"Window {d} — {cl['window']}", 0, (lambda b, d=d: draw_window(b, d)), f"Window {d}")
    add("w24", "Window 24 — Christmas Eve", 0, draw_w24, "Window 24")
    add("check", "The Sealed Check", 1, draw_check, "Window 24")
    add("notes", "Detective’s notes", 0, draw_notes, "Notes")
    add("hintstop", "Hints", 0, draw_hint_stop, "Hints")
    for lv in range(3):
        for j, chunk in enumerate(hint_pages(Lx)[lv]):
            add(f"hint{lv}_{j}", H.LEVEL_NAMES[lv] if j == 0 else None, 1 if j == 0 else None,
                (lambda b, lv=lv, chunk=chunk, j=j: draw_hint_page(b, lv, chunk, j)), "Hints")
    add("thanks", "Thank you", 0, draw_thanks, "")
    return P

class _Counts:
    counts = None; empty = None

def build_book(fmt, path):
    rows = load_rows()
    b = Book(fmt, path, f"{C.TITLE_PLAIN} — {C.SUBTITLE}")
    b.rows = rows; b.seal = b_seal(C.KILLER); b.fmt = fmt
    b.counts, b.empty = Book.counts, Book.empty
    plan = book_plan(rows, b.L)
    b.plan = plan
    b.pageno = {key: i + 1 for i, (key, *_r) in enumerate(plan)}
    for key, title, level, fn, header in plan:
        b.new_page(key, header, title if (title and level is not None) else None, level or 0,
                   chrome=key not in ("cover",))
        fn(b)
    b.save()
    return b.page

# ------------------------------------------------------------------ cover
def draw_cover(b):
    c, Lx = b.c, b.L
    p = os.path.join(ARTDIR, f"cover_{Lx.fmt}.jpg")
    c.drawImage(p, 0, 0, Lx.W, Lx.H)
    t = c.beginText(); t.setTextRenderMode(3); t.setFont("Nunito", 12)
    for i, line in enumerate([C.TITLE, C.SUBTITLE, C.TAGLINE, f"{C.BRAND} · Printable advent calendar · 24 days"]):
        t.setTextOrigin(40, Lx.H - 60 - i * 16); t.textLine(line)
    c.drawText(t)
    if Lx.ipad and "calendar" in b.pageno:
        c.setFillColor(CREAM); c.roundRect(Lx.W - 186, Lx.H - 40, 170, 26, 8, fill=1, stroke=0)
        c.setFillColor(NAVY); c.setFont("Nunito-Bold", 11); c.drawCentredString(Lx.W - 101, Lx.H - 31, "← back to the calendar")
        b.link("calendar", Lx.W - 186, Lx.H - 40, Lx.W - 16, Lx.H - 14)

# ------------------------------------------------------------------ set-up pages
def draw_howto(b):
    c, Lx = b.c, b.L
    y = b.title_block("Before you begin", "How to play")
    for head, text in C.HOW_TO_PLAY:
        y = para(c, f"<font name='Nunito-ExtraBold' color='#842E20'>{esc(head)}.</font> {esc(text)}", Lx.m, y, Lx.cw, Lx.body)
    y -= 6
    tips = ("<b>Printing tip.</b> The inside pages are mostly white to save ink; each window has one small "
            "illustration. Window 2, the Sound Book, is the thick one: print it single- or double-sided, black "
            "and white is fine. A highlighter and a pencil are all you need. "
            "<b>Tip from our testers:</b> read each day’s papers first, then work through the Sound Book with the "
            "strongest filter of the day.")
    if Lx.ipad:
        tips = ("<b>On a tablet.</b> The first page is the calendar: tap today’s window. Every window page has a "
                "link back to the calendar. Highlight lines in the Sound Book as you rule them out.")
    h = para_h(tips, Lx.cw - 24, Lx.small) + 18
    card(c, Lx.m, y, Lx.cw, h, fill=OCHRE_L, stroke=OCHRE_L)
    para(c, tips, Lx.m + 12, y - 9, Lx.cw - 24, Lx.small)

def draw_contents(b):
    c, Lx = b.c, b.L
    y = b.title_block("Case file", "Contents")
    lines = [(k, t, lv) for k, t, lv, _, _ in b.plan if t and lv is not None and k != "contents"]
    two = len(lines) > 34
    colw = Lx.cw / 2 - 10 if two else Lx.cw
    x0 = Lx.m; ystart = y; per = math.ceil(len(lines) / 2) if two else len(lines)
    for i, (k, t, lv) in enumerate(lines):
        if two and i == per:
            x0 = Lx.m + Lx.cw / 2 + 10; y = ystart
        ind = 12 * Lx.s if lv == 1 else 0
        fs = (8.2 if lv == 1 else 9.4) * Lx.s
        font = "Nunito" if lv == 1 else "Nunito-Bold"
        label = ("Sound Book · " + t) if k.startswith("log") else t
        while pdfmetrics.stringWidth(label, font, fs) > colw - ind - 30:
            label = label[:-2]
        c.setFont(font, fs); c.setFillColor(INK if lv == 0 else SOFT)
        c.drawString(x0 + ind, y - fs, label)
        c.drawRightString(x0 + colw, y - fs, str(b.pageno[k]))
        b.link(k, x0, y - fs - 3, x0 + colw, y + 2)
        y -= fs * 1.55
    c.setFont("Nunito-Italic", 8.3 * Lx.s); c.setFillColor(SOFT)
    c.drawString(Lx.m, Lx.bottom - 6, "Tap any line to jump to that page. The hint pages are at the back.")

def draw_rules(b):
    c, Lx = b.c, b.L
    y = b.title_block("Read these once", "House rules")
    y = para(c, "Every window uses the words below in exactly this sense. If a window seems to have two "
                "meanings, this page decides.", Lx.m, y, Lx.cw, Lx.body)
    y -= 4
    for term, text in C.GLOSSARY:
        c.setFillColor(NAVY); c.setFont("Fraunces-SemiBold", 11.5 * Lx.s)
        c.drawString(Lx.m, y - 12 * Lx.s, term)
        y2 = para(c, esc(text), Lx.m + 112 * Lx.s, y, Lx.cw - 112 * Lx.s, Lx.body)
        y = min(y2, y - 19 * Lx.s) - 3
        c.setStrokeColor(RULE); c.setLineWidth(0.5); c.line(Lx.m, y + 2, Lx.W - Lx.m, y + 2)
        y -= 5

def draw_calendar(b):
    """Print: a tracker to tick off. iPad (first page): 24 tappable windows under a small title band."""
    c, Lx = b.c, b.L
    if Lx.ipad:
        bh = 150
        c.drawImage(os.path.join(ARTDIR, "banner_ipad.jpg"), 0, Lx.H - bh - 30, Lx.W, bh + 30)
        y = Lx.H - bh - 52
        spaced(c, Lx.m, y, "TAP TODAY’S WINDOW", "Josefin", 12 * Lx.s, 1.6, RUST_D)
        c.setFont("Nunito", 10 * Lx.s); c.setFillColor(INK)
        c.drawRightString(Lx.W - Lx.m, y, "Every window links back here.")
        t = "Cover and how to play →"
        c.setFont("Nunito-Bold", 10 * Lx.s); c.setFillColor(SEA)
        c.drawRightString(Lx.W - Lx.m, Lx.bottom - 8, t)
        tw = pdfmetrics.stringWidth(t, "Nunito-Bold", 10 * Lx.s)
        b.link("cover", Lx.W - Lx.m - tw, Lx.bottom - 12, Lx.W - Lx.m, Lx.bottom + 4)
        y -= 14
    else:
        y = b.title_block("Advent calendar", "Your advent calendar")
        y = para(c, "Tick off each window as you open it and write down how many lines are still in. The "
                    "check-ins on Windows 6, 12 and 18 tell you the number to expect.", Lx.m, y, Lx.cw, Lx.body)
    cols, rows_ = 4, 6
    gap = 10 * Lx.s
    cwid = (Lx.cw - gap * (cols - 1)) / cols
    ch = (y - Lx.bottom - 24 - gap * (rows_ - 1)) / rows_
    for d in range(1, 25):
        i = d - 1; cx = Lx.m + (i % cols) * (cwid + gap); cy = y - 6 - (i // cols) * (ch + gap)
        c.setFillColor(NAVY if d != 24 else RUST_D); c.roundRect(cx, cy - ch, cwid, ch, 7, fill=1, stroke=0)
        # a little window with four panes
        px0, py0, pw, ph = cx + 8, cy - ch * 0.74, cwid - 16, ch * 0.66
        c.setFillColor(OCHRE_L if d != 24 else CREAM); c.roundRect(px0, py0, pw, ph, 4, fill=1, stroke=0)
        c.setStrokeColor(NAVY if d != 24 else RUST_D); c.setLineWidth(2)
        c.line(px0 + pw / 2, py0 + ph * 0.62, px0 + pw / 2, py0 + ph); c.line(px0, py0 + ph * 0.62, px0 + pw, py0 + ph * 0.62)
        c.setFillColor(NAVY if d != 24 else RUST_D); c.setFont("Josefin", ch * 0.3)
        c.drawCentredString(cx + cwid / 2, py0 + ph * 0.13, str(d))
        c.setFillColor(CREAM); c.setFont("Nunito-Bold", 7.2 * Lx.s)
        c.drawCentredString(cx + cwid / 2, cy - ch * 0.88, window_date(d))
        if not Lx.ipad:
            checkbox(c, cx + 8, cy - ch + 5, 7, CREAM)
            c.setFont("Nunito", 6.6 * Lx.s); c.setFillColor(CREAM)
            c.drawRightString(cx + cwid - 8, cy - ch + 6, "left: ____")
        key = f"w{d}"
        if key in b.pageno:
            b.link(key, cx, cy - ch, cx + cwid, cy)

def draw_envelope(b):
    c, Lx = b.c, b.L
    y = b.title_block("Set-up", "Envelope template")
    y = para(c, "Print this page 24 times (or use any small envelopes). Cut along the solid line, fold the "
                "four flaps in along the dotted lines, glue the side flaps and tuck in the window page folded in "
                "quarters. Window 2 is thick: give it a bigger envelope or a paper clip.", Lx.m, y, Lx.cw, Lx.body)
    spaced(c, Lx.W / 2, y - 14, "ENVELOPE TEMPLATE · CUT ON THE SOLID LINE", "Josefin", 9.5 * Lx.s, 1.2, STEEL, "c")
    y -= 20
    cx, cy = Lx.W / 2, (y + Lx.bottom) / 2 - 6
    bw = min(Lx.cw * 0.62, 330); bh = bw * 0.68
    fl = bh * 0.55
    c.setStrokeColor(INK); c.setLineWidth(1)
    p = c.beginPath()
    pts = [(cx - bw / 2, cy + bh / 2), (cx, cy + bh / 2 + fl), (cx + bw / 2, cy + bh / 2), (cx + bw / 2 + fl * 0.8, cy),
           (cx + bw / 2, cy - bh / 2), (cx, cy - bh / 2 - fl), (cx - bw / 2, cy - bh / 2), (cx - bw / 2 - fl * 0.8, cy)]
    p.moveTo(*pts[0])
    for pt in pts[1:]:
        p.lineTo(*pt)
    p.close(); c.drawPath(p, fill=0, stroke=1)
    c.setDash(3, 3); c.setStrokeColor(STEEL)
    c.rect(cx - bw / 2, cy - bh / 2, bw, bh, fill=0, stroke=1); c.setDash()
    c.setFillColor(SOFT); c.setFont("Nunito-Italic", 8 * Lx.s)
    c.drawCentredString(cx, cy + bh / 2 + fl * 0.35, "top flap — fold last")
    c.drawCentredString(cx, cy - bh / 2 - fl * 0.45, "bottom flap — glue")
    c.drawString(cx + bw / 2 + 6, cy - 3, "side — glue")
    c.drawRightString(cx - bw / 2 - 6, cy - 3, "side — glue")
    tower_icon(c, cx, cy + 14, 34, NAVY)
    c.setFillColor(NAVY); c.setFont("Josefin", 17 * Lx.s)
    c.drawCentredString(cx, cy - 6, "CANDLEHOLM LIGHT")
    c.setFont("Nunito", 9 * Lx.s); c.drawCentredString(cx, cy - 22, "The keeper’s journal · do not open before the day")

def draw_labels(b):
    c, Lx = b.c, b.L
    y = b.title_block("Set-up", "Day numbers for the envelopes")
    y = para(c, "Cut out the 24 circles and stick one on each envelope. Print on sticker paper if you have it.",
             Lx.m, y, Lx.cw, Lx.body)
    spaced(c, Lx.W / 2, y - 10, "DAY NUMBERS 1 – 24", "Josefin", 9.5 * Lx.s, 1.2, STEEL, "c")
    y -= 18
    cols = 4; rows_ = 6
    cw = Lx.cw / cols; chh = (y - Lx.bottom - 10) / rows_
    r = min(cw, chh) * 0.4
    for d in range(1, 25):
        i = d - 1; cx = Lx.m + cw * (i % cols + 0.5); cy = y - chh * (i // cols + 0.5)
        c.setStrokeColor(RULE); c.setDash(2, 3); c.circle(cx, cy, r + 5, fill=0, stroke=1); c.setDash()
        c.setFillColor(NAVY if d != 24 else RUST); c.circle(cx, cy, r, fill=1, stroke=0)
        c.setStrokeColor(CREAM); c.setLineWidth(1.4); c.circle(cx, cy, r * 0.86, fill=0, stroke=1)
        c.setFillColor(CREAM); c.setFont("Josefin", r * 0.95)
        c.drawCentredString(cx, cy - r * 0.2, str(d))
        c.setFont("Nunito-Bold", r * 0.17)
        c.drawCentredString(cx, cy - r * 0.58, "DECEMBER")

# ------------------------------------------------------------------ window helpers
def window_head(b, d, title):
    c, Lx = b.c, b.L
    y = Lx.top
    spaced(c, Lx.m, y - 10 * Lx.s, f"WINDOW {d} OF 24", "Josefin", 10.5 * Lx.s, 1.5, RUST_D)
    spaced(c, Lx.W - Lx.m, y - 10 * Lx.s, window_date(d).upper(), "Josefin", 10.5 * Lx.s, 1.5, STEEL, "r")
    y = para(c, esc(title), Lx.m, y - 15 * Lx.s, Lx.cw, Lx.h1)
    if Lx.ipad and "calendar" in b.pageno:
        c.setFont("Nunito-Bold", 8.5 * Lx.s); c.setFillColor(RUST_D)
        t = "← calendar"
        c.drawRightString(Lx.W - Lx.m, y + 6, t)
        tw = pdfmetrics.stringWidth(t, "Nunito-Bold", 8.5 * Lx.s)
        b.link("calendar", Lx.W - Lx.m - tw - 4, y + 2, Lx.W - Lx.m + 2, y + 16)
    return y

def vignette(b, d, y, h):
    """The window's own illustration, in a thin double frame."""
    c, Lx = b.c, b.L
    c.saveState()
    p = c.beginPath(); p.roundRect(Lx.m, y - h, Lx.cw, h, 6); c.clipPath(p, stroke=0, fill=0)
    iw, ih = 1600, 500
    scale = max(Lx.cw / iw, h / ih)
    dw, dh = iw * scale, ih * scale
    c.drawImage(art_path(d), Lx.m + (Lx.cw - dw) / 2, y - h - (dh - h) / 2, dw, dh)
    c.restoreState()
    c.setStrokeColor(NAVY); c.setLineWidth(1.2); c.roundRect(Lx.m, y - h, Lx.cw, h, 6, fill=0, stroke=1)
    c.setStrokeColor(CREAM); c.setLineWidth(0.8); c.roundRect(Lx.m + 3, y - h + 3, Lx.cw - 6, h - 6, 4, fill=0, stroke=1)
    return y - h - 9 * Lx.s

def journal_card(b, y, d, w=None, x=None):
    """Ezra's page for the day, in his neat hand on lined paper."""
    c, Lx = b.c, b.L
    x = Lx.m if x is None else x; w = w or Lx.cw
    inner = w - 40
    text = esc(C.JOURNAL[d])
    hh = para_h(text, inner, Lx.hand) + 34 * Lx.s
    c.saveState()
    c.setFillColor(HexColor("#FDFBF4")); c.setStrokeColor(RULE); c.setLineWidth(0.8)
    c.rect(x, y - hh, w, hh, fill=1, stroke=1)
    c.setStrokeColor(HexColor("#E7E1D2")); c.setLineWidth(0.5)
    yy = y - 26 * Lx.s - Lx.hand.leading + 3
    while yy > y - hh + 4:
        c.line(x + 6, yy, x + w - 6, yy); yy -= Lx.hand.leading
    c.setStrokeColor(HexColor("#E9B7A9")); c.line(x + 28, y - 2, x + 28, y - hh + 2)
    c.restoreState()
    c.setFont("Kalam-Bold", 12.5 * Lx.s); c.setFillColor(RUST_D)
    c.drawString(x + 34, y - 17 * Lx.s, f"{d} December")
    c.setFont("Josefin-Semi", 7.4 * Lx.s); c.setFillColor(SOFT)
    c.drawRightString(x + w - 10, y - 15 * Lx.s, "FROM EZRA’S JOURNAL")
    para(c, text, x + 34, y - 23 * Lx.s, inner, Lx.hand)
    return y - hh - 9 * Lx.s

def doc_card(b, y, d, w=None, x=None):
    """The paper Ezra pinned to the page: typed, on a slightly darker card, with a pin."""
    c, Lx = b.c, b.L
    D = C.DOCS[d]
    x = Lx.m if x is None else x; w = w or Lx.cw
    inner = w - 26
    lines = D.get("lines", [])
    rows = D.get("rows", [])
    rh = 12.2 * Lx.s
    hh = 22 * Lx.s + sum(para_h(esc(t), inner, Lx.typed) for t in lines) + len(rows) * rh + (8 if rows else 0) + 10
    card(c, x, y, w, hh, fill=HexColor("#F6EFDD"), stroke=HexColor("#D9CCAE"), r=2)
    pin(c, x + w / 2, y - 2)
    spaced(c, x + 12, y - 15 * Lx.s, D["title"], "Josefin", 8.6 * Lx.s, 1.0, NAVY)
    yy = y - 22 * Lx.s
    if rows:
        ncol = len(rows[0])
        widths = {2: [0.16, 0.84], 5: [0.13, 0.35, 0.12, 0.2, 0.2]}[ncol]
        heads = {2: ["Date", "High and low water"], 5: ["Date", "Weather", "Wind", "Sunrise", "Lighting-up"]}[ncol]
        xx = x + 12
        c.setFont("Courier Prime-Bold", 8.6 * Lx.s); c.setFillColor(RUST_D)
        for hd, wf in zip(heads, widths):
            c.drawString(xx, yy - 9 * Lx.s, hd); xx += inner * wf
        yy -= rh
        for k, row in enumerate(rows):
            xx = x + 12
            c.setFont("Courier Prime", 8.8 * Lx.s); c.setFillColor(INK)
            for v, wf in zip(row, widths):
                c.drawString(xx, yy - 9 * Lx.s, v); xx += inner * wf
            yy -= rh
        yy -= 6
    for t in lines:
        yy = para(c, esc(t), x + 12, yy, inner, Lx.typed)
    return y - hh - 9 * Lx.s

def question_box(b, y, d, text):
    c, Lx = b.c, b.L
    st = ParagraphStyle("q", parent=Lx.body, fontName="Nunito-Bold", fontSize=10.6 * Lx.s, leading=14.4 * Lx.s)
    inner = Lx.cw - 30
    t2 = ("Work out what today’s papers mean, then cross out every line in the Sound Book that doesn’t "
          "fit. Only check the lines that are still in.")
    h = para_h(esc(text), inner, st) + para_h(t2, inner, Lx.small) + 34 * Lx.s
    c.setFillColor(CREAM); c.rect(Lx.m, y - h, Lx.cw, h, fill=1, stroke=0)
    c.setFillColor(RUST); c.rect(Lx.m, y - h, 4, h, fill=1, stroke=0)
    spaced(c, Lx.m + 14, y - 13 * Lx.s, "TODAY’S QUESTION", "Josefin", 9.4 * Lx.s, 1.2, RUST_D)
    yy = para(c, esc(text), Lx.m + 14, y - 17 * Lx.s, inner, st)
    yy = para(c, t2, Lx.m + 14, yy, inner, Lx.small)
    c.setFont("Nunito", 8.6 * Lx.s); c.setFillColor(STEEL)
    c.drawString(Lx.m + 14, y - h + 8, "Lines still in tonight:  ________")
    hk = f"hint0_{hint_page_of(b, d)}"
    t = f"Stuck? Hints for Window {d} start on page {b.pageno[hk]}."
    c.drawRightString(Lx.W - Lx.m - 10, y - h + 8, t)
    tw = pdfmetrics.stringWidth(t, "Nunito", 8.6 * Lx.s)
    b.link(hk, Lx.W - Lx.m - 10 - tw, y - h + 5, Lx.W - Lx.m - 10, y - h + 18)
    return y - h - 8 * Lx.s

def checkin_box(b, y, d):
    c, Lx = b.c, b.L
    n = b.counts[d]; empty = b.empty[d]
    first, last = min(empty), max(empty)
    chap = (f"the chapters from {first} to {last} December" if last - first + 1 == len(empty) else
            "the chapters for " + ", ".join(f"{x}" for x in empty) + " December")
    t = (f"If you have used Windows 3 to {d}, there should be {n:,} lines still in the Sound Book, and {chap} are now "
         "completely crossed out. A few more is fine if you read a window generously: a later window will catch "
         "them. Fewer? Check the hints for the windows so far.")
    h = para_h(esc(t), Lx.cw - 30, Lx.small) + 22 * Lx.s
    c.setStrokeColor(RUST); c.setLineWidth(1.2); c.setDash(4, 2)
    c.roundRect(Lx.m, y - h, Lx.cw, h, 6, fill=0, stroke=1); c.setDash()
    spaced(c, Lx.m + 12, y - 12 * Lx.s, "CHECK-IN · WHERE YOU ARE NOW", "Josefin", 9.4 * Lx.s, 1.2, RUST_D)
    para(c, esc(t), Lx.m + 12, y - 16 * Lx.s, Lx.cw - 30, Lx.small)
    return y - h - 8 * Lx.s

# ------------------------------------------------------------------ the chart of the Sound (vector)
class Chart:
    def __init__(self, x, y_top, w, h, view=C.VIEW):
        self.x, self.y_top, self.w, self.h = x, y_top, w, h
        vx0, vy0, vx1, vy1 = view
        self.k = min(w / (vx1 - vx0), h / (vy1 - vy0))
        self.ox = x + (w - (vx1 - vx0) * self.k) / 2 - vx0 * self.k
        self.oy = y_top - h + (h - (vy1 - vy0) * self.k) / 2 - vy0 * self.k
        self.view = view

    def P(self, mx, my):
        return self.ox + mx * self.k, self.oy + my * self.k

def path_of(c, ch, pts, close=True):
    p = c.beginPath(); p.moveTo(*ch.P(*pts[0]))
    for q in pts[1:]:
        p.lineTo(*ch.P(*q))
    if close:
        p.close()
    return p

def chart(c, x, y_top, w, h, Lx, view=C.VIEW, ring=True, passages=True, landings="all", villages=True, labels=True,
          fs=1.0, highlight_loch=False, compass=True):
    ch = Chart(x, y_top, w, h, view)
    s = Lx.s * fs
    c.saveState()
    c.setFillColor(WATER); c.rect(x, y_top - h, w, h, fill=1, stroke=0)
    p = c.beginPath(); p.rect(x, y_top - h, w, h); c.clipPath(p, stroke=0, fill=0)
    # depth contour (a soft line hugging each coast)
    c.setStrokeColor(WATER_D); c.setLineWidth(0.6); c.setDash(1, 2)
    for poly in (C.MAINLAND, C.INISHVARRA):
        cx_ = sum(q[0] for q in poly) / len(poly); cy_ = sum(q[1] for q in poly) / len(poly)
        c.drawPath(path_of(c, ch, [(cx_ + (q[0] - cx_) * 1.05, cy_ + (q[1] - cy_) * 1.03) for q in poly]), fill=0, stroke=1)
    c.setDash()
    c.setFillColor(LAND); c.setStrokeColor(NAVY); c.setLineWidth(0.9)
    c.drawPath(path_of(c, ch, C.MAINLAND), fill=1, stroke=1)
    c.drawPath(path_of(c, ch, C.INISHVARRA), fill=1, stroke=1)
    # hills (hatch) on the mainland
    c.setStrokeColor(HexColor("#CFC5AD")); c.setLineWidth(0.5)
    for hx_, hy_ in ((15, 6), (19, 8), (21, 18), (14, 19), (18, 1), (12, -9), (16, -13), (24, 4), (-11, 0), (-10, 7)):
        px, py = ch.P(hx_, hy_)
        for k in range(4):
            c.arc(px - 8 * s + k * 1.5, py - 4 * s, px + 8 * s - k * 1.5, py + 4 * s + k * 2, 20, 140)
    # the loch: water drawn over the land along its path
    c.setStrokeColor(WATER); c.setLineCap(1); c.setLineJoin(1)
    for k in range(len(C.LOCH_PATH) - 1):
        a, bq = C.LOCH_PATH[k], C.LOCH_PATH[k + 1]
        narrow = min(abs(a[0] - C.NARROWS[0]) + abs(a[1] - C.NARROWS[1]), abs(bq[0] - C.NARROWS[0]) + abs(bq[1] - C.NARROWS[1])) < 0.1
        c.setLineWidth((0.45 if narrow else 1.25) * ch.k)
        c.line(*ch.P(*a), *ch.P(*bq))
    c.setLineCap(0)
    # the island, the reef
    c.setFillColor(MOSS_L); c.setStrokeColor(NAVY); c.setLineWidth(0.9)
    ix, iy = ch.P(0, 0); c.ellipse(ix - 0.6 * ch.k, iy - 0.42 * ch.k, ix + 0.6 * ch.k, iy + 0.42 * ch.k, fill=1, stroke=1)
    c.setFillColor(STEEL)
    for rx, ry in C.SKERRY_ROCKS:
        px, py = ch.P(rx, ry)
        for dx, dy in ((-2, 0), (2, 1), (0, -2)):
            c.circle(px + dx * s * 0.8, py + dy * s * 0.8, 1.4 * s, fill=1, stroke=0)
    # passages
    if passages:
        c.setLineWidth(1.1); c.setDash(4, 3)
        c.setStrokeColor(RUST)
        c.drawPath(path_of(c, ch, [(-1.6, -9), (-1.9, -2), (-1.9, 2), (-1.4, 9)], close=False), fill=0, stroke=1)
        c.setStrokeColor(SEA)
        c.drawPath(path_of(c, ch, [(-5.0, -9), (-5.6, -2), (-5.6, 2), (-5.2, 9)], close=False), fill=0, stroke=1)
        c.setDash()
        if labels:
            for (mx, my), t, col in (((-1.9, 4.6), "INNER PASSAGE", RUST), ((-5.6, -4.6), "OUTER PASSAGE", SEA)):
                px, py = ch.P(mx, my)
                c.saveState(); c.translate(px, py); c.rotate(90)
                c.setFillColor(col); c.setFont("Josefin", 6.4 * s); c.drawCentredString(0, 2.5 * s, t); c.restoreState()
    # range circle
    if ring:
        c.setStrokeColor(OCHRE); c.setLineWidth(1.3); c.setDash(5, 3)
        ix, iy = ch.P(0, 0); c.circle(ix, iy, C.RANGE * ch.k, fill=0, stroke=1); c.setDash()
        if labels:
            px, py = ch.P(-6.2, -10.7)
            c.setFillColor(HexColor("#9A6F1E")); c.setFont("Nunito-Bold", 6.6 * s)
            c.drawCentredString(px, py, "range of the light: 12 miles")
    # the light
    ix, iy = ch.P(0, 0)
    tower_icon(c, ix, iy - 3 * s, 12 * s, NAVY)
    if labels:
        c.setFillColor(NAVY); c.setFont("Fraunces-SemiBold", 8 * s); c.drawString(ix + 6 * s, iy - 9 * s, "CANDLEHOLM")
    # villages
    if villages:
        for v, (vx, vy, kind) in C.VILLAGES.items():
            px, py = ch.P(vx, vy)
            big = v == C.PORT
            c.setFillColor(NAVY); c.circle(px, py, (2.6 if big else 1.8) * s, fill=1, stroke=0)
            if labels:
                c.setFont("Nunito-ExtraBold" if big else "Nunito-Bold", (7.2 if big else 6.6) * s); c.setFillColor(INK)
                off = {"Skellan": (-4, 4, "r"), "Ballyvarra": (-4, 3, "r"), "Kilvarra": (-4, 3, "r"), "Rathvarra": (-4, 3, "r"),
                       "Bayle": (4, 2, "l"), "Achnabrae": (-2, 4, "c"), "Inverlash": (2, -8, "c"), "Torrandhu": (2, 4, "c"),
                       "Balnacrae": (2, 4, "c")}.get(v, (4, -2, "l"))
                fn = {"l": c.drawString, "r": c.drawRightString, "c": c.drawCentredString}[off[2]]
                fn(px + off[0] * s, py + off[1] * s, v)
    # landings
    if landings:
        show = C.LANDINGS if landings == "all" else {n: C.LANDINGS[n] for n in landings}
        for n, (nm, lx, ly, shore) in show.items():
            px, py = ch.P(lx, ly)
            r = 4.2 * s
            c.setFillColor(WHITE); c.setStrokeColor(RUST_D); c.setLineWidth(0.9)
            c.circle(px, py, r, fill=1, stroke=1)
            c.setFillColor(RUST_D); c.setFont("Nunito-ExtraBold", 5.4 * s)
            c.drawCentredString(px, py - 1.9 * s, str(n))
    if labels:
        c.setFillColor(NAVY)
        for (mx, my), t, sz, ang in (((C.GANNET_HEAD[0] - 0.6, C.GANNET_HEAD[1] + 0.2), "Gannet Head", 6.8, 0),
                                     ((C.SELKIE_NESS[0] - 0.6, C.SELKIE_NESS[1] - 0.2), "Selkie Ness", 6.8, 0),
                                     ((-10.2, -2.0), "INISHVARRA", 9.0, 90), ((2.4, -13.5), "SOUND OF CANDLEHOLM", 7.6, 90),
                                     ((20.6, 16.9), "LOCH TARRISK", 7.6, 0), ((16.2, 11.4), "the Narrows", 6.4, 0),
                                     ((-3.3, -2.0), "Dulse Reef", 6.4, 0), ((22.0, -3.0), "MAINLAND", 9.0, 0)):
            px, py = ch.P(mx, my)
            c.saveState(); c.translate(px, py); c.rotate(ang)
            font = "Josefin" if t.isupper() else "Fraunces-Italic"
            c.setFont(font, sz * s)
            anchor = c.drawRightString if t in ("Gannet Head", "Selkie Ness") else c.drawCentredString
            anchor(0, 0, t); c.restoreState()
        px, py = ch.P(*C.GANNET_HEAD)
        c.setFillColor(RUST); c.rect(px - 1.6 * s, py - 1.6 * s, 3.2 * s, 3.2 * s, fill=1, stroke=0)   # coastguard lookout
    if compass:
        px, py = x + w - 22 * s, y_top - 26 * s
        c.setFillColor(NAVY)
        p = c.beginPath(); p.moveTo(px, py + 12 * s); p.lineTo(px - 4 * s, py); p.lineTo(px + 4 * s, py); p.close()
        c.drawPath(p, fill=1, stroke=0)
        c.setFont("Josefin", 8 * s); c.drawCentredString(px, py - 9 * s, "N")
        # scale bar: 5 nautical miles
        sx, sy = x + 10 * s, y_top - h + 10 * s
        c.setStrokeColor(NAVY); c.setLineWidth(1.4); c.line(sx, sy, sx + 5 * ch.k, sy)
        c.line(sx, sy - 2, sx, sy + 2); c.line(sx + 5 * ch.k, sy - 2, sx + 5 * ch.k, sy + 2)
        c.setFont("Nunito-Bold", 6 * s); c.drawString(sx, sy + 4, "5 nautical miles")
    c.restoreState()
    c.setStrokeColor(NAVY); c.setLineWidth(1.2); c.rect(x, y_top - h, w, h, fill=0, stroke=1)
    return ch

def tower_section(c, x, y_top, w, h, Lx):
    """Candleholm Light in section, bottom to top: thick white walls, a stair of steps climbing round the
    inside wall, a window on every level, what is kept on each floor, the gallery and the lamp."""
    levels = [("Entrance and oil store", "oil cans, the door to the island", 0.2),
              ("Store room", "coal, rope, spare wicks; the parcels on 23 December", 0.2),
              ("Spare bedroom", "a bunk for the relief keeper", 0.18),
              ("Watch room", "the log desk and the clock", 0.17),
              ("Lamp room", "the lamp and its lens, under the glass", 0.17)]
    cx = x + w * 0.33
    base = y_top - h + 26
    th = (h - 40) * 0.86
    wb, wt = w * 0.4, w * 0.26
    wall = 9
    def half(yy):
        t = max(0, min(1, (yy - base) / (th * 0.83)))
        return (wb + (wt - wb) * t) / 2
    # rock and sea at the foot
    c.setFillColor(WATER); c.rect(x, base - 26, w, 18, fill=1, stroke=0)
    c.setFillColor(HexColor("#B9B3A3")); p = c.beginPath(); p.moveTo(cx - wb * 0.9, base - 16); p.lineTo(cx - wb * 0.62, base)
    p.lineTo(cx + wb * 0.62, base); p.lineTo(cx + wb * 0.9, base - 16); p.close(); c.drawPath(p, fill=1, stroke=0)
    top_body = base + th * 0.83
    # outer wall
    c.setFillColor(CREAM); c.setStrokeColor(NAVY); c.setLineWidth(1.3)
    p = c.beginPath(); p.moveTo(cx - wb / 2, base); p.lineTo(cx - wt / 2, top_body); p.lineTo(cx + wt / 2, top_body)
    p.lineTo(cx + wb / 2, base); p.close(); c.drawPath(p, fill=1, stroke=1)
    # inside (white), inset by the wall thickness
    c.setFillColor(WHITE); c.setLineWidth(0.7)
    p = c.beginPath(); p.moveTo(cx - wb / 2 + wall, base); p.lineTo(cx - wt / 2 + wall, top_body); p.lineTo(cx + wt / 2 - wall, top_body)
    p.lineTo(cx + wb / 2 - wall, base); p.close(); c.drawPath(p, fill=1, stroke=1)
    yy = base
    for k, (name, what, frac) in enumerate(levels):
        hh = th * frac
        if k < 4:
            hw0, hw1 = half(yy) - wall, half(yy + hh) - wall
            # floor slab above this level
            c.setFillColor(HexColor("#C9BFA8")); c.rect(cx - hw1 - wall, yy + hh - 3, 2 * (hw1 + wall), 5, fill=1, stroke=0)
            # stair: steps along the wall, alternating sides
            left = k % 2 == 0
            n = 9
            for sidx in range(n):
                t = sidx / n
                sx = (cx - hw0 + 4 + (2 * hw0 - 30) * t) if left else (cx + hw0 - 26 - (2 * hw0 - 30) * t)
                sy = yy + 2 + (hh - 8) * t
                c.setFillColor(RUST); c.rect(sx, sy, 22, 3.2, fill=1, stroke=0)
            # a window in the wall
            wy = yy + hh * 0.55
            side = 1 if left else -1
            wxx = cx + side * (half(wy) - wall / 2)
            c.setFillColor(OCHRE_L); c.setStrokeColor(NAVY); c.setLineWidth(0.6)
            c.rect(wxx - 3, wy - 7, 6, 14, fill=1, stroke=1)
            # what is kept here (small drawings)
            ix = cx + (8 if left else -8)
            if k == 0:
                for q in range(3):
                    c.setFillColor(RUST_D); c.rect(ix - 14 + q * 11, yy + 3, 8, 13, fill=1, stroke=0)
                c.setFillColor(RUST_D); c.rect(cx - 7, base, 14, 22, fill=1, stroke=0)
            elif k == 1:
                c.setFillColor(HexColor("#A07450"))
                for q in range(3):
                    c.rect(ix - 16 + q * 12, yy + 3, 10, 9 - q, fill=1, stroke=0)
                c.setFillColor(HexColor("#785236")); c.rect(ix - 18, yy + 15, 36, 2.5, fill=1, stroke=0)
            elif k == 2:
                c.setFillColor(SEA); c.rect(ix - 16, yy + 3, 32, 7, fill=1, stroke=0)
                c.setFillColor(CREAM); c.rect(ix - 16, yy + 10, 10, 4, fill=1, stroke=0)
            elif k == 3:
                c.setFillColor(HexColor("#785236")); c.rect(ix - 14, yy + 3, 28, 12, fill=1, stroke=0)
                c.setFillColor(WHITE); c.setStrokeColor(NAVY); c.circle(ix, yy + hh * 0.62, 6, fill=1, stroke=1)
                c.line(ix, yy + hh * 0.62, ix, yy + hh * 0.62 + 4); c.line(ix, yy + hh * 0.62, ix + 3, yy + hh * 0.62)
        else:
            # gallery, lamp room glass, lamp, cap
            c.setStrokeColor(INK); c.setLineWidth(1.8); c.line(cx - wt * 0.7, yy, cx + wt * 0.7, yy)
            c.setLineWidth(0.8)
            for q in range(9):
                xx = cx - wt * 0.66 + wt * 1.32 * q / 8; c.line(xx, yy, xx, yy + 9)
            c.line(cx - wt * 0.7, yy + 9, cx + wt * 0.7, yy + 9)
            c.setFillColor(OCHRE_L); c.setStrokeColor(NAVY); c.rect(cx - wt * 0.36, yy + 1, wt * 0.72, hh - 4, fill=1, stroke=1)
            c.setFillColor(OCHRE); c.circle(cx, yy + hh * 0.48, hh * 0.2, fill=1, stroke=0)
            c.setStrokeColor(NAVY)
            for q in range(5):
                xx = cx - wt * 0.36 + wt * 0.72 * q / 4; c.line(xx, yy + 1, xx, yy + hh - 3)
            c.setFillColor(RUST); p = c.beginPath(); p.moveTo(cx - wt * 0.46, yy + hh - 3); p.lineTo(cx, yy + hh + th * 0.11)
            p.lineTo(cx + wt * 0.46, yy + hh - 3); p.close(); c.drawPath(p, fill=1, stroke=0)
            c.setStrokeColor(INK); c.setLineWidth(1.2); c.line(cx, yy + hh + th * 0.11, cx, yy + hh + th * 0.11 + 10)
        # label
        ly = yy + hh / 2
        lx = cx + wb / 2 + 24
        c.setStrokeColor(RULE); c.setLineWidth(0.6); c.line(cx + half(ly) + 2, ly, lx - 4, ly)
        c.setFillColor(NAVY); c.setFont("Fraunces-SemiBold", 10.5 * Lx.s); c.drawString(lx, ly + 2, name)
        c.setFillColor(SOFT); c.setFont("Nunito-Italic", 8.2 * Lx.s); c.drawString(lx, ly - 9 * Lx.s, what)
        yy += hh
    c.setFillColor(SOFT); c.setFont("Nunito-Italic", 7.6 * Lx.s)
    c.drawString(x, base - 38, "The stair climbs round the inside wall from the door to the lamp room. One door, at the foot.")

# ------------------------------------------------------------------ Window 1
def draw_w1_case(b):
    c, Lx = b.c, b.L
    y = window_head(b, 1, "The Case")
    y = vignette(b, 1, y, Lx.cw / 3.3)
    for ptxt in C.INTRO:
        y = para(c, esc(ptxt), Lx.m, y, Lx.cw, Lx.body)
    y = para(c, "What we know for certain", Lx.m, y - 2, Lx.cw, Lx.h2)
    for f in C.KNOWN_FACTS:
        c.setFillColor(RUST); c.circle(Lx.m + 4, y - 6 * Lx.s, 2.2, fill=1, stroke=0)
        y = para(c, esc(f), Lx.m + 14, y, Lx.cw - 14, Lx.small)
    if y < Lx.bottom - 4:
        raise RuntimeError(f"[{Lx.fmt}] Window 1 overflows by {Lx.bottom - y:.0f} pt")

def draw_w1_journal(b):
    c, Lx = b.c, b.L
    spaced(c, Lx.m, Lx.top - 10 * Lx.s, "WINDOW 1 · CONTINUED", "Josefin", 10.5 * Lx.s, 1.5, RUST_D)
    y = para(c, "Ezra’s journal", Lx.m, Lx.top - 15 * Lx.s, Lx.cw, Lx.h1)
    y = para(c, "The first page, as Superintendent Treleaven found it. From tomorrow, each window holds one more "
                "page, and the papers Ezra pinned to it.", Lx.m, y, Lx.cw, Lx.body)
    y = journal_card(b, y - 4, 1)
    y -= 6
    # the island, a little plan
    y = para(c, "Candleholm from above", Lx.m, y, Lx.cw, Lx.h2)
    ph = min(220 * Lx.s, y - Lx.bottom - 10)
    c.setFillColor(WATER); c.rect(Lx.m, y - ph, Lx.cw, ph, fill=1, stroke=0)
    cx, cy = Lx.m + Lx.cw / 2, y - ph / 2
    c.setFillColor(MOSS_L); c.setStrokeColor(NAVY); c.setLineWidth(1)
    c.ellipse(cx - Lx.cw * 0.32, cy - ph * 0.36, cx + Lx.cw * 0.32, cy + ph * 0.36, fill=1, stroke=1)
    items = [((-0.02, 0.12), "the tower", "t"), ((0.15, 0.1), "the cottage", "c"), ((-0.19, -0.14), "the boathouse", "b"),
             ((0.31, 0.0), "1 East Landing", "l"), ((-0.06, -0.33), "2 Boat Cove", "l")]
    for (dx, dy), t, kind in items:
        px, py = cx + dx * Lx.cw, cy + dy * ph
        if kind == "t":
            tower_icon(c, px, py - 8, 24, NAVY)
        elif kind == "c":
            c.setFillColor(WHITE); c.setStrokeColor(NAVY); c.rect(px - 14, py - 8, 28, 16, fill=1, stroke=1)
            c.setFillColor(STEEL); c.rect(px - 14, py + 4, 28, 4, fill=1, stroke=0)
        elif kind == "b":
            c.setFillColor(HexColor("#785236")); c.rect(px - 10, py - 7, 20, 14, fill=1, stroke=0)
        else:
            c.setFillColor(WHITE); c.setStrokeColor(RUST_D); c.circle(px, py, 5, fill=1, stroke=1)
        c.setFillColor(INK); c.setFont("Nunito-Bold", 8 * Lx.s)
        c.drawCentredString(px, py - 20, t)
    c.setStrokeColor(NAVY); c.rect(Lx.m, y - ph, Lx.cw, ph, fill=0, stroke=1)

def draw_w1_tower(b):
    c, Lx = b.c, b.L
    spaced(c, Lx.m, Lx.top - 10 * Lx.s, "WINDOW 1 · CONTINUED", "Josefin", 10.5 * Lx.s, 1.5, RUST_D)
    y = para(c, "Candleholm Light in section", Lx.m, Lx.top - 15 * Lx.s, Lx.cw, Lx.h1)
    y = para(c, "One white tower, five levels, one stair. Ezra lived in the cottage beside it and climbed the tower "
                "every evening at lighting-up time to light the lamp. On 23 December he moved the parcels up into "
                "the store room.", Lx.m, y, Lx.cw, Lx.body)
    tower_section(c, Lx.m, y - 6, Lx.cw, y - Lx.bottom - 24, Lx)

def draw_w1_chart(b):
    c, Lx = b.c, b.L
    spaced(c, Lx.m, Lx.top - 10 * Lx.s, "WINDOW 1 · CONTINUED", "Josefin", 10.5 * Lx.s, 1.5, RUST_D)
    y = para(c, "The chart of the Sound", Lx.m, Lx.top - 15 * Lx.s, Lx.cw, Lx.h1)
    y = para(c, "Numbered circles are the 24 landings; dots are the home villages in the Sound Book. The dashed "
                "circle is how far Candleholm Light can be seen. North is up. Every mark on this chart is also "
                "written out on the next page.", Lx.m, y, Lx.cw, Lx.small)
    chart(c, Lx.m, y - 4, Lx.cw, y - Lx.bottom - 8, Lx)

def chart_words():
    shores = {"isle": "on Candleholm", "outer": "on Inishvarra", "north": "on the mainland coast north of Loch Tarrisk",
              "loch": "on Loch Tarrisk", "south": "on the mainland coast south of Loch Tarrisk"}
    land = [f"{n} {nm} ({shores[sh]})" for n, (nm, _, _, sh) in C.LANDINGS.items()]
    kinds = {"coast": "on the open coast of the mainland", "loch": "on the shore of Loch Tarrisk",
             "inland": "inland on the mainland", "outer": "on Inishvarra"}
    def ring(v):
        d = C.dist_light(v)
        return "right on the range circle" if abs(d - C.RANGE) < 0.05 else ("inside the range circle" if d < C.RANGE else "outside it")
    vil = [f"{v}: {kinds[k]}, {ring(v)}" for v, (_, _, k) in C.VILLAGES.items()]
    return land, vil

def draw_w1_words(b):
    c, Lx = b.c, b.L
    spaced(c, Lx.m, Lx.top - 10 * Lx.s, "WINDOW 1 · CONTINUED", "Josefin", 10.5 * Lx.s, 1.5, RUST_D)
    y = para(c, "The chart in words", Lx.m, Lx.top - 15 * Lx.s, Lx.cw, Lx.h1)
    land, vil = chart_words()
    st = ParagraphStyle("w", parent=Lx.small, spaceAfter=1.4 * Lx.s)
    y = para(c, "The landings, numbered 1 to 24", Lx.m, y, Lx.cw, Lx.h2)
    half = (len(land) + 1) // 2
    yl = yr = y
    for i, t in enumerate(land):
        if i < half:
            yl = para(c, esc(t), Lx.m, yl, Lx.cw / 2 - 8, st)
        else:
            yr = para(c, esc(t), Lx.m + Lx.cw / 2 + 4, yr, Lx.cw / 2 - 4, st)
    y = min(yl, yr) - 6
    y = para(c, "The home villages", Lx.m, y, Lx.cw, Lx.h2)
    half = (len(vil) + 1) // 2
    yl = yr = y
    for i, t in enumerate(vil):
        if i < half:
            yl = para(c, esc(t), Lx.m, yl, Lx.cw / 2 - 8, st)
        else:
            yr = para(c, esc(t), Lx.m + Lx.cw / 2 + 4, yr, Lx.cw / 2 - 4, st)
    y = min(yl, yr) - 6
    y = para(c, "Other marks", Lx.m, y, Lx.cw, Lx.h2)
    for t in ["Candleholm Light stands on Candleholm, in the Sound between the mainland (east) and Inishvarra (west).",
              "The Dulse Reef lies just west of Candleholm. The Inner Passage runs between Candleholm and the reef; the "
              "Outer Passage runs west of the reef.",
              "Gannet Head is the headland north of the mouth of Loch Tarrisk, with the coastguard lookout on it. Selkie "
              "Ness is the headland between Lannagh and Polbrae.",
              "Loch Tarrisk runs east from its mouth to the Narrows, then on to the east and finally turns south to its "
              "head. Landings 13, 14, 15 and 16 are drawn further north than the Narrows; 17 and 18 further south."]:
        y = para(c, esc(t), Lx.m, y, Lx.cw, st)
    if y < Lx.bottom - 4:
        raise RuntimeError(f"[{Lx.fmt}] chart in words overflows by {Lx.bottom - y:.0f} pt")

# ------------------------------------------------------------------ Window 2: the Sound Book
def draw_w2_intro(b):
    c, Lx = b.c, b.L
    y = window_head(b, 2, "The Sound Book")
    y = vignette(b, 2, y, Lx.cw / 4.2)
    y = journal_card(b, y, 2)
    y = para(c, "Every soul who crossed the Sound from 1 to 23 December, on the day of their first crossing: 2,400 "
                "lines, in date and time order. Keep this window out of its envelope from now on: every window from "
                "tomorrow is checked against it.", Lx.m, y, Lx.cw, Lx.small)
    rows = [("Date, Time", "the day of the first crossing, and when they stepped aboard (24-hour clock)"),
            ("Tally", "their tally number, 0001–2400 (drawn from a bag, not in date order)"),
            ("First name, Surname", "as written in the Sound Book"),
            ("Home", "their home village; every village is on the chart (Window 1)"),
            ("Boat", "Mail, Fishing, Tender or Pilot (the Mail Boat, a fishing boat, the Lights Tender, the Pilot Cutter)"),
            ("Landing", "the number of the landing where the boat put them ashore (chart, Window 1)"),
            ("Box", "an empty box for your own ticks")]
    for k, v in rows:
        c.setFont("Nunito-ExtraBold", 9 * Lx.s); c.setFillColor(NAVY)
        c.drawString(Lx.m, y - 10 * Lx.s, k)
        y = min(para(c, esc(v), Lx.m + 120 * Lx.s, y, Lx.cw - 120 * Lx.s, Lx.small), y - 14 * Lx.s)
    y = para(c, "Chapters", Lx.m, y - 4, Lx.cw, Lx.h2)
    col = 0; yy = y; n = 0
    for key, title, level, _, _ in b.plan:
        if key.startswith("log") and title:
            xx = Lx.m + col * Lx.cw / 3
            c.setFont("Nunito-Bold", 8.6 * Lx.s); c.setFillColor(INK)
            c.drawString(xx + 4, yy - 10 * Lx.s, title)
            c.drawRightString(xx + Lx.cw / 3 - 12, yy - 10 * Lx.s, f"p. {b.pageno[key]}")
            b.link(key, xx, yy - 13 * Lx.s, xx + Lx.cw / 3 - 10, yy)
            col = (col + 1) % 3
            if col == 0:
                yy -= 13 * Lx.s
    if yy - 13 * Lx.s < Lx.bottom - 6:
        raise RuntimeError(f"[{Lx.fmt}] Window 2 overflows")

def draw_log_page(b, chunk):
    c, Lx = b.c, b.L
    rh, _ = log_geometry(Lx)
    recs = [it[1] for it in chunk if it[0] == "rec"]
    scale = min(Lx.cw / sum(w for _, w in LOG_COLS), 1.4)
    cols = [(n, w * scale) for n, w in LOG_COLS]
    tw = sum(w for _, w in cols); x0 = Lx.m + (Lx.cw - tw) / 2
    y = Lx.top + 6
    spaced(c, x0, y - 13 * Lx.s, "WINDOW 2 OF 24 · THE SOUND BOOK", "Josefin", 9.6 * Lx.s, 1.2, RUST_D)
    c.setFont("Nunito-Bold", 9 * Lx.s); c.setFillColor(INK)
    a, z = recs[0], recs[-1]
    c.drawRightString(x0 + tw, y - 13 * Lx.s, f"{a['day']} Dec {C.tstr(a['time'])} – {z['day']} Dec {C.tstr(z['time'])}")
    y -= 26 * Lx.s
    fs = 8.3 if not Lx.ipad else 9.9
    c.setFont("Nunito-ExtraBold", fs * 0.86); c.setFillColor(RUST_D)
    x = x0
    for n, w in cols:
        c.drawString(x + 3, y - rh + 3, n.upper()); x += w
    y -= rh
    c.setStrokeColor(NAVY); c.setLineWidth(0.9); c.line(x0, y, x0 + tw, y)
    zebra = 0
    for kind, v in chunk:
        if kind == "band":
            c.setFillColor(OCHRE_L); c.rect(x0, y - rh, tw, rh, fill=1, stroke=0)
            c.setFillColor(NAVY); c.setFont("Fraunces-SemiBold", fs)
            c.drawString(x0 + 6, y - rh + 3, f"Chapter · {v} December")
            y -= rh; zebra = 0; continue
        if zebra % 2:
            c.setFillColor(PALE); c.rect(x0, y - rh, tw, rh, fill=1, stroke=0)
        zebra += 1
        vals = [f"{v['day']} Dec", C.tstr(v["time"]), f"{v['tally']:04d}", v["first"], v["last"], v["home"], v["boat"],
                str(v["landing"]), ""]
        x = x0; c.setFillColor(INK)
        for (n, w), val in zip(cols, vals):
            if n == "":
                c.setStrokeColor(RULE); c.setLineWidth(0.6)
                c.rect(x + 5, y - rh + 2.5, rh - 5, rh - 5, fill=0, stroke=1)
            else:
                c.setFont("Nunito-Bold" if n in ("Time", "Tally") else "Nunito", fs)
                c.drawString(x + 3, y - rh + 3, val)
            x += w
        y -= rh
    c.setStrokeColor(NAVY); c.setLineWidth(0.9); c.line(x0, y, x0 + tw, y)

# ------------------------------------------------------------------ Windows 3-23
def morse_table(b, y):
    c, Lx = b.c, b.L
    cols = 7; rows = 4
    w = Lx.cw; cell = w / cols; rh = 17 * Lx.s
    h = rows * rh + 12
    card(c, Lx.m, y, w, h, fill=WHITE)
    for i, (k, v) in enumerate(C.MORSE.items()):
        cx = Lx.m + (i % cols) * cell + 10; cy = y - 6 - (i // cols + 1) * rh + 5
        c.setFont("Josefin", 10 * Lx.s); c.setFillColor(NAVY); c.drawString(cx, cy, k)
        xx = cx + 14 * Lx.s
        c.setFillColor(RUST)
        for ch in v:
            if ch == "·":
                c.circle(xx + 2, cy + 3.4, 2.1, fill=1, stroke=0); xx += 7
            else:
                c.rect(xx, cy + 1.8, 11, 3.2, fill=1, stroke=0); xx += 14
    return y - h - 8 * Lx.s

def boards(b, y):
    c, Lx = b.c, b.L
    h = 62 * Lx.s
    for k, (lab, nums) in enumerate((("LEFT-HAND BOARD · EVEN", ["0472", "1394", "2016"]), ("RIGHT-HAND BOARD · ODD", ["0815", "1203", "2361"]))):
        x = Lx.m + k * (Lx.cw / 2 + 6); w = Lx.cw / 2 - 6
        c.setFillColor(HexColor("#785236")); c.roundRect(x, y - h, w, h, 4, fill=1, stroke=0)
        c.setFillColor(HexColor("#A07450")); c.roundRect(x + 4, y - h + 4, w - 8, h - 8, 3, fill=1, stroke=0)
        c.setFillColor(CREAM); c.setFont("Josefin", 8 * Lx.s); c.drawString(x + 10, y - 13 * Lx.s, lab)
        for j, n in enumerate(nums):
            tx = x + 30 + j * (w - 60) / 2; ty = y - h * 0.62
            c.setFillColor(BRASS if j == 0 else (COPPER if j == 1 else TIN)); c.circle(tx, ty, 14 * Lx.s, fill=1, stroke=0)
            c.setFillColor(INK); c.setFont("Courier Prime-Bold", 7.2 * Lx.s); c.drawCentredString(tx, ty - 2.5, n)
    c.setFont("Nunito-Italic", 7.6 * Lx.s); c.setFillColor(SOFT)
    c.drawString(Lx.m, y - h - 10, "Example tallies only: these numbers are not anyone in this case.")
    return y - h - 18 * Lx.s

def metals(b, y):
    c, Lx = b.c, b.L
    h = 46 * Lx.s
    for k, (col, lab, rng) in enumerate(((BRASS, "BRASS", "0001 – 0800"), (COPPER, "COPPER", "0801 – 1600"), (TIN, "TIN", "1601 – 2400"))):
        x = Lx.m + k * Lx.cw / 3
        c.setFillColor(col); c.circle(x + 26 * Lx.s, y - h / 2, 18 * Lx.s, fill=1, stroke=0)
        c.setFillColor(NAVY); c.setFont("Josefin", 10 * Lx.s); c.drawString(x + 52 * Lx.s, y - h / 2 + 2, lab)
        c.setFont("Courier Prime-Bold", 9 * Lx.s); c.drawString(x + 52 * Lx.s, y - h / 2 - 11, rng)
    return y - h - 6 * Lx.s

def scarf_strip(b, y):
    c, Lx = b.c, b.L
    n = 9; w = 26 * Lx.s; h = 22 * Lx.s
    for k in range(n):
        c.setFillColor(RUST if k % 2 == 0 else CREAM); c.setStrokeColor(RULE)
        c.rect(Lx.m + k * w, y - h, w, h, fill=1, stroke=1)
    c.setFont("Nunito-Italic", 7.8 * Lx.s); c.setFillColor(SOFT)
    c.drawString(Lx.m + n * w + 10, y - h / 2 - 3, "Example: a name of 9 letters ends on a red stripe.")
    return y - h - 10 * Lx.s

WINDOW_CHART = {4: dict(view=(-9, -6, 5, 6), ring=False, villages=False, landings=[1, 2], passages=True),
                5: dict(view=(8, 6.5, 27.5, 17.5), ring=False, villages=False, landings=list(range(8, 19)), passages=False),
                6: dict(view=(-14.5, -15, 16, 15), ring=True, villages=True, landings=False, passages=False),
                11: dict(view=(-1, -16.5, 19, 21), ring=False, villages=True, landings=False, passages=False),
}
WINDOW_CHART_MAX = {4: 190, 5: 220, 6: 260, 11: 260}

def journal_h(b, d):
    Lx = b.L
    return para_h(esc(C.JOURNAL[d]), Lx.cw - 40, Lx.hand) + 34 * Lx.s + 9 * Lx.s

def doc_h(b, d):
    Lx = b.L; D = C.DOCS[d]
    return (22 * Lx.s + sum(para_h(esc(t), Lx.cw - 26, Lx.typed) for t in D.get("lines", []))
            + len(D.get("rows", [])) * 12.2 * Lx.s + (8 + 12.2 * Lx.s if D.get("rows") else 0) + 10 + 9 * Lx.s)

def question_h(b, d, text):
    Lx = b.L
    st = ParagraphStyle("q", parent=Lx.body, fontName="Nunito-Bold", fontSize=10.6 * Lx.s, leading=14.4 * Lx.s)
    t2 = ("Work out what today’s papers mean, then cross out every line in the Sound Book that doesn’t "
          "fit. Only check the lines that are still in.")
    return para_h(esc(text), Lx.cw - 30, st) + para_h(t2, Lx.cw - 30, Lx.small) + 34 * Lx.s + 8 * Lx.s

def checkin_h(b):
    Lx = b.L
    return para_h("x " * 190, Lx.cw - 30, Lx.small) + 22 * Lx.s + 8 * Lx.s + 10

EXTRA_H = {7: lambda s: 4 * 17 * s + 12 + 8 * s, 9: lambda s: 62 * s + 18 * s, 20: lambda s: 46 * s + 6 * s,
           23: lambda s: 22 * s + 10 * s}

def draw_window(b, d):
    c, Lx = b.c, b.L
    cl = next(x for x in C.CLUES if x["day"] == d)
    y = window_head(b, d, cl["window"])
    need = (journal_h(b, d) + doc_h(b, d) + question_h(b, d, cl["note"]) + (checkin_h(b) if d in C.CHECKPOINTS else 0)
            + (EXTRA_H[d](Lx.s) if d in EXTRA_H else 0))
    free = y - Lx.bottom - need - 9 * Lx.s
    if d in WINDOW_CHART:
        vh = max(46 * Lx.s, min(Lx.cw / 6.5, free * 0.25))
        ph = min(WINDOW_CHART_MAX[d] * Lx.s, free - vh - 8 * Lx.s)
        if ph < 120 * Lx.s:
            vh = 40 * Lx.s; ph = free - vh - 8 * Lx.s
    else:
        vh = min(Lx.cw / 2.5, free); ph = 0
    if vh < 36 * Lx.s or (d in WINDOW_CHART and ph < 110 * Lx.s):
        raise RuntimeError(f"[{Lx.fmt}] Window {d} has no room: vignette {vh:.0f}, chart {ph:.0f}")
    y = vignette(b, d, y, vh)
    y = journal_card(b, y, d)
    y = doc_card(b, y, d)
    if d == 7:
        y = morse_table(b, y)
    if d == 9:
        y = boards(b, y)
    if d == 20:
        y = metals(b, y)
    if d == 23:
        y = scarf_strip(b, y)
    if d in WINDOW_CHART:
        opts = WINDOW_CHART[d]
        chart(c, Lx.m, y, Lx.cw, ph, Lx, view=opts["view"], ring=opts["ring"], passages=opts["passages"],
              landings=opts["landings"], villages=opts["villages"], fs=0.95 if d != 12 else 0.8)
        y -= ph + 8 * Lx.s
    y = question_box(b, y, d, cl["note"])
    if d in C.CHECKPOINTS:
        y = checkin_box(b, y, d)
    if y < Lx.bottom - 4:
        raise RuntimeError(f"[{Lx.fmt}] Window {d} overflows the page by {Lx.bottom - y:.0f} pt")

# ------------------------------------------------------------------ Window 24, check, notes, hints
def draw_w24(b):
    c, Lx = b.c, b.L
    y = window_head(b, 24, "Christmas Eve")
    y = vignette(b, 24, y, Lx.cw / 2.3)
    for ptxt in C.FINALE:
        y = para(c, esc(ptxt), Lx.m, y, Lx.cw, Lx.body)
    tower_icon(c, Lx.W / 2, y - 50, 44, NAVY)

def draw_check(b):
    c, Lx = b.c, b.L
    spaced(c, Lx.m, Lx.top - 10 * Lx.s, "WINDOW 24 · CONTINUED", "Josefin", 10.5 * Lx.s, 1.5, RUST_D)
    y = para(c, "The Sealed Check", Lx.m, Lx.top - 15 * Lx.s, Lx.cw, Lx.h1)
    y = para(c, "Found your one remaining line? Do this sum with its details (a phone calculator is fine). It "
                "confirms the answer without printing the killer’s name anywhere in this calendar.", Lx.m, y, Lx.cw, Lx.body)
    steps = ["Take the tally number and multiply it by 4.",
             "Count the letters in the first name and in the surname, and add both counts to the result.",
             "Look at the last three digits of the total."]
    for i, s in enumerate(steps, 1):
        c.setFillColor(RUST); c.circle(Lx.m + 10, y - 9 * Lx.s, 9 * Lx.s, fill=1, stroke=0)
        c.setFillColor(CREAM); c.setFont("Josefin", 10 * Lx.s)
        c.drawCentredString(Lx.m + 10, y - 12.5 * Lx.s, str(i))
        y = min(para(c, esc(s), Lx.m + 30 * Lx.s, y, Lx.cw - 30 * Lx.s, Lx.body), y - 24 * Lx.s)
    y -= 6
    for lab in ["Tally number × 4 =", "+ letters in first name =", "+ letters in surname =", "Last three digits ="]:
        c.setFont("Nunito-Bold", 11 * Lx.s); c.setFillColor(INK); c.drawString(Lx.m + 10, y - 16 * Lx.s, lab)
        c.setStrokeColor(NAVY); c.setLineWidth(0.9)
        c.roundRect(Lx.m + 190 * Lx.s, y - 24 * Lx.s, 140 * Lx.s, 24 * Lx.s, 4, fill=0, stroke=1)
        y -= 34 * Lx.s
    y -= 8
    bh = 96 * Lx.s
    c.setFillColor(NAVY); c.roundRect(Lx.m, y - bh, Lx.cw, bh, 10, fill=1, stroke=0)
    c.setFillColor(CREAM); c.setFont("Nunito", 11 * Lx.s)
    c.drawCentredString(Lx.W / 2, y - 26 * Lx.s, "If your last three digits are")
    c.setFont("Josefin", 34 * Lx.s); c.setFillColor(OCHRE)
    c.drawCentredString(Lx.W / 2, y - 62 * Lx.s, b.seal)
    c.setFont("Nunito", 11 * Lx.s); c.setFillColor(CREAM)
    c.drawCentredString(Lx.W / 2, y - 84 * Lx.s, "you have found the red cap. Open the Envelope to read what happened.")
    y -= bh + 14
    para(c, "Not a match? Somewhere a line was kept or crossed out by mistake. The hints at the back show you which "
            "window to look at again, and the check-ins on Windows 6, 12 and 18 help you find where.",
         Lx.m, y, Lx.cw, Lx.body)

def draw_notes(b):
    c, Lx = b.c, b.L
    y = b.title_block("Your working", "Detective’s notes")
    c.setStrokeColor(RULE); c.setLineWidth(0.5)
    yy = y - 10
    while yy > Lx.bottom + 10:
        c.line(Lx.m, yy, Lx.W - Lx.m, yy); yy -= 24 * Lx.s

def draw_hint_stop(b):
    c, Lx = b.c, b.L
    c.setFillColor(CREAM); c.rect(Lx.m, Lx.bottom + 40, Lx.cw, Lx.top - Lx.bottom - 60, fill=1, stroke=0)
    tower_icon(c, Lx.W / 2, Lx.H / 2 + 90 * Lx.s, 70 * Lx.s, NAVY)
    spaced(c, Lx.W / 2, Lx.H / 2 + 60 * Lx.s, "STOP, DETECTIVE", "Josefin", 12 * Lx.s, 2, RUST_D, "c")
    c.setFillColor(NAVY); c.setFont("Fraunces-SemiBold", 34 * Lx.s)
    c.drawCentredString(Lx.W / 2, Lx.H / 2 + 14 * Lx.s, "Hints ahead")
    st = ParagraphStyle("c", parent=Lx.body, alignment=TA_CENTER)
    para(c, "Three levels of help for every window, each level on its own pages. Start with Level 1 and only "
            "go further if you need to. Nothing here names the killer.", Lx.m + 50, Lx.H / 2 - 10 * Lx.s, Lx.cw - 100, st)
    y = Lx.H / 2 - 90 * Lx.s
    for lv in range(3):
        key = f"hint{lv}_0"
        c.setFont("Nunito-Bold", 12 * Lx.s); c.setFillColor(INK)
        t = f"{H.LEVEL_NAMES[lv]}  ·  page {b.pageno[key]}"
        c.drawCentredString(Lx.W / 2, y, t)
        tw = pdfmetrics.stringWidth(t, "Nunito-Bold", 12 * Lx.s)
        b.link(key, Lx.W / 2 - tw / 2, y - 4, Lx.W / 2 + tw / 2, y + 12 * Lx.s)
        y -= 24 * Lx.s

def hint_pages(Lx):
    st = ParagraphStyle("h", parent=Lx.body)
    avail = Lx.top - Lx.bottom - 80 * Lx.s
    out = []
    for lv in range(3):
        pages, cur, used = [], [], 0
        for cl in C.CLUES:
            h = max(para_h(esc(H.HINTS[cl["id"]][lv]), Lx.cw - 96 * Lx.s, st) + 6, 24 * Lx.s)
            if used + h > avail and cur:
                pages.append(cur); cur, used = [], 0
            cur.append(cl["id"]); used += h
        pages.append(cur); out.append(pages)
    return out

def hint_page_of(b, d):
    for j, chunk in enumerate(hint_pages(b.L)[0]):
        if str(d) in chunk:
            return j
    return 0

def draw_hint_page(b, lv, chunk, j):
    c, Lx = b.c, b.L
    y = b.title_block("Hints" + (" (continued)" if j else ""), H.LEVEL_NAMES[lv])
    st = ParagraphStyle("h", parent=Lx.body)
    for cid in chunk:
        c.setFont("Nunito-ExtraBold", 10 * Lx.s); c.setFillColor(RUST_D)
        c.drawString(Lx.m, y - 11 * Lx.s, f"Window {cid}")
        y = min(para(c, esc(H.HINTS[cid][lv]), Lx.m + 96 * Lx.s, y, Lx.cw - 96 * Lx.s, st), y - 22 * Lx.s) - 6

def draw_thanks(b):
    c, Lx = b.c, b.L
    y = b.title_block(C.BRAND, "Thank you, detective")
    for ptxt in ["Thank you for spending Advent on Candleholm. We hope Ezra’s journal, the tides and the red knitted cap "
                 "kept you guessing until Christmas Eve.",
                 "Every QuietClueCo case is written and drawn by hand and checked by a computer program before it "
                 "reaches you. The program confirms that there is exactly one answer, that every window is needed, "
                 "and that the answer does not change if a window is read in a slightly different way, including "
                 "the words on the chart and in the almanac such as through, higher up, near, between, rising and "
                 "before, and the a.m. and p.m. of the lighting-up times.",
                 "If you enjoyed the calendar, a short review helps other detectives find us.",
                 "For personal use only. Please don’t share or resell the files. You may print as many copies as "
                 "you need for your own household or game night.",
                 "Fonts: Fraunces, Nunito, Kalam, Josefin Sans and Courier Prime (SIL Open Font License). All "
                 "illustrations are drawn with code. No AI-generated images are used."]:
        y = para(c, esc(ptxt), Lx.m, y, Lx.cw, Lx.body)

# ------------------------------------------------------------------ solution file
def build_solution(fmt, path, walk, finalists, index):
    b = Book(fmt, path, f"{C.TITLE_PLAIN} — The Envelope (solution)")
    c, Lx = b.c, b.L
    K = C.KILLER
    b.new_page("answer", "Solution", "The answer")
    c.setFillColor(NAVY); c.roundRect(Lx.m, Lx.top - 250 * Lx.s, Lx.cw, 250 * Lx.s, 12, fill=1, stroke=0)
    spaced(c, Lx.W / 2, Lx.top - 34 * Lx.s, "THE ENVELOPE · OPEN AFTER THE SEALED CHECK", "Josefin", 10 * Lx.s, 1.5, OCHRE, "c")
    c.setFillColor(CREAM); c.setFont("Fraunces-SemiBold", 40 * Lx.s)
    c.drawCentredString(Lx.W / 2, Lx.top - 100 * Lx.s, f"{K['first']} {K['last']}")
    c.setFont("Nunito", 10.8 * Lx.s)
    c.drawCentredString(Lx.W / 2, Lx.top - 132 * Lx.s,
                        f"Tally {K['tally']:04d} · {K['home']} · first crossing {K['day']} December at {C.tstr(K['time'])} "
                        f"on {C.BOAT_NAMES[K['boat']]} · landing {K['landing']} ({C.landing_name(K['landing'])})")
    c.setFont("Nunito-Italic", 10.5 * Lx.s)
    c.drawCentredString(Lx.W / 2, Lx.top - 160 * Lx.s, f"Sealed Check: {K['tally']:04d} × 4 + {len(K['first'])} + "
                        f"{len(K['last'])} = {K['tally'] * 4 + len(K['first']) + len(K['last'])}, last three digits {b_seal(K)}")
    c.setFont("Nunito", 10.5 * Lx.s)
    c.drawCentredString(Lx.W / 2, Lx.top - 200 * Lx.s, "In this file: what really happened · the solution day by day · "
                        "the finalists ·")
    c.drawCentredString(Lx.W / 2, Lx.top - 216 * Lx.s, "and an index showing which window rules out each of the 2,400 lines.")
    y = Lx.top - 280 * Lx.s
    y = para(c, "What really happened", Lx.m, y, Lx.cw, Lx.h2)
    for ptxt in C.EPILOGUE:
        if y - para_h(esc(ptxt), Lx.cw, Lx.body) < Lx.bottom:
            b.new_page(None, "Solution"); y = Lx.top
        y = para(c, esc(ptxt), Lx.m, y, Lx.cw, Lx.body)
    b.new_page("walk", "Solution", "Day by day")
    y = b.title_block("The solution", "Day by day")
    y = para(c, "What each window means and how many lines it rules out, in calendar order.", Lx.m, y, Lx.cw, Lx.body)
    cols = [("Day", 34), ("Window", 92), ("What it tells you", Lx.cw - 230), ("Out", 46), ("Left", 58)]
    st = ParagraphStyle("w", parent=Lx.small, spaceAfter=0)
    def head(y):
        x = Lx.m; c.setFont("Nunito-ExtraBold", 8.3 * Lx.s); c.setFillColor(RUST_D)
        for n, w in cols:
            c.drawString(x + 4, y - 11, n.upper()); x += w
        y -= 16; c.setStrokeColor(NAVY); c.line(Lx.m, y, Lx.W - Lx.m, y); return y
    y = head(y)
    c.setFont("Nunito", 9 * Lx.s); c.setFillColor(INK)
    c.drawString(Lx.m + 130, y - 12, "Window 2: the Sound Book"); c.drawRightString(Lx.W - Lx.m - 6, y - 12, "2,400")
    y -= 18
    for i, step in enumerate(walk):
        cl = next(x for x in C.CLUES if x["id"] == step["id"])
        h = max(para_h(esc(step["why"]), cols[2][1] - 8, st) + 8, para_h(esc(cl["window"]), cols[1][1] - 6, st) + 8, 18)
        if y - h < Lx.bottom:
            b.new_page(None, "Solution"); y = head(Lx.top)
        if i % 2:
            c.setFillColor(PALE); c.rect(Lx.m, y - h, Lx.cw, h, fill=1, stroke=0)
        c.setFillColor(INK); c.setFont("Nunito-Bold", 9 * Lx.s)
        c.drawString(Lx.m + 4, y - 12, str(step["day"]))
        para(c, esc(cl["window"]), Lx.m + 38, y - 3, cols[1][1] - 6, st)
        para(c, esc(step["why"]), Lx.m + 130, y - 3, cols[2][1] - 8, st)
        c.setFont("Nunito", 9 * Lx.s); c.drawRightString(Lx.W - Lx.m - 62, y - 12, f"{step['out']:,}")
        c.setFont("Nunito-Bold", 9 * Lx.s); c.drawRightString(Lx.W - Lx.m - 6, y - 12, f"{step['left']:,}")
        y -= h
    b.new_page("finalists", "Solution", "The finalists")
    y = b.title_block("The solution", "The finalists")
    y = para(c, "These travellers fit every window but one. Each is ruled out by exactly the window shown, which is "
                "how we know every window in the calendar is needed.", Lx.m, y, Lx.cw, Lx.body)
    fcols = [("Tally", 34), ("Traveller", 104), ("Home", 66), ("Boat", 40), ("Crossed", 64), ("Land.", 30), ("Ruled out by", Lx.cw - 338)]
    x = Lx.m; c.setFont("Nunito-ExtraBold", 8.3 * Lx.s); c.setFillColor(RUST_D)
    for n, w in fcols:
        c.drawString(x + 3, y - 11, n.upper()); x += w
    y -= 16; c.setStrokeColor(NAVY); c.line(Lx.m, y, Lx.W - Lx.m, y)
    fs = 8.2 * Lx.s; rh = 14.5 * Lx.s
    for i, f in enumerate(finalists):
        if y - rh < Lx.bottom:
            b.new_page(None, "Solution"); y = Lx.top
        if i % 2:
            c.setFillColor(PALE); c.rect(Lx.m, y - rh, Lx.cw, rh, fill=1, stroke=0)
        r = f["rec"]
        vals = [f"{r['tally']:04d}", f"{r['first']} {r['last']}", r["home"], r["boat"], f"{r['day']} Dec {C.tstr(r['time'])}",
                str(r["landing"]), f["why"]]
        x = Lx.m
        for (n, w), v in zip(fcols, vals):
            c.setFillColor(RUST_D if (n == "Ruled out by" and f["clue"] == "KILLER") else INK)
            c.setFont("Nunito-Bold" if n in ("Tally", "Ruled out by") else "Nunito", fs)
            vv = v
            while pdfmetrics.stringWidth(vv, "Nunito", fs) > w - 5 and len(vv) > 4:
                vv = vv[:-2] + "…" if not vv.endswith("…") else vv[:-3] + "…"
            c.drawString(x + 3, y - rh + 4, vv); x += w
        y -= rh
    b.new_page("index", "Solution", "Elimination index")
    y = b.title_block("The solution", "Elimination index")
    y = para(c, "Every tally from 0001 to 2400 with the first window (in calendar order) that rules it out. If you kept "
                "or crossed out someone by mistake, look them up here.", Lx.m, y, Lx.cw, Lx.small)
    tickets = sorted(index)
    ncol = 10 if not Lx.ipad else 12
    colw = Lx.cw / ncol; rh = 10.2 * Lx.s
    first = True; i = 0
    while i < len(tickets):
        if not first:
            b.new_page(None, "Elimination index"); y = Lx.top
        first = False
        per_col = int((y - Lx.bottom) // rh)
        for col in range(ncol):
            for row in range(per_col):
                if i >= len(tickets):
                    break
                t = tickets[i]; v = index[t]
                xx = Lx.m + col * colw; yy = y - (row + 1) * rh
                c.setFont("Nunito-Bold", 7.3 * Lx.s); c.setFillColor(INK); c.drawString(xx + 2, yy + 2, f"{t:04d}")
                c.setFont("Nunito-ExtraBold" if v == "KILLER" else "Nunito", 7.3 * Lx.s)
                c.setFillColor(RUST_D if v == "KILLER" else SOFT)
                c.drawString(xx + 25 * Lx.s, yy + 2, v if v == "KILLER" else f"W{v}")
                i += 1
    c.setFont("Nunito-Italic", 8 * Lx.s); c.setFillColor(SOFT)
    c.drawString(Lx.m, Lx.bottom - 4, "KILLER = the only line that fits every window. W3 to W23 = the window that rules the line out.")
    b.save()
    return b.page

def b_seal(K):
    return f"{G.seal(K):03d}"
