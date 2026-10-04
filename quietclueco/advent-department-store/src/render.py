"""Render The Windows at Quillon's to PDF: the calendar (print Letter, print A4, iPad) and the
solution file (the Envelope) in the same three formats.

All graphics are drawn with code: the night scenes come from art.py (Pillow), the plans, maps
and documents are drawn here with ReportLab. Inside pages stay light to save ink; the scenes are
the dark accent.
"""
import csv, math, os
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.pagesizes import LETTER, A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
import case as C
import hints as H
import art

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")
HORROR = os.path.join(os.path.dirname(HERE), "listing", "src", "fonts_horror")
ARTDIR = os.path.join(HERE, "art")

# ------------------------------------------------------------------ palette (light pages)
INK = HexColor("#141B2D"); NAVY = HexColor("#1C2740"); STEEL = HexColor("#4A5A75"); SOFT = HexColor("#6A7488")
FROST = HexColor("#EEF1F6"); PALE = HexColor("#F5F7FA"); RULE = HexColor("#D3DAE4")
AMBER = HexColor("#E39A2E"); AMBER_D = HexColor("#A8601A"); AMBER_L = HexColor("#FBE7C6")
WHITE = HexColor("#FFFFFF"); PARK = HexColor("#E3EBDD"); RIVER = HexColor("#D6E2F0")
RED = HexColor("#B83A3A"); GREEN = HexColor("#3E7A55")

def register_fonts():
    for name, d, f in [("Fraunces", FONTS, "Fraunces-Regular"), ("Fraunces-SemiBold", FONTS, "Fraunces-SemiBold"),
                       ("Fraunces-Bold", FONTS, "Fraunces-Bold"), ("Fraunces-Italic", FONTS, "Fraunces-Italic"),
                       ("Nunito", FONTS, "Nunito-Regular"), ("Nunito-Bold", FONTS, "Nunito-Bold"),
                       ("Nunito-ExtraBold", FONTS, "Nunito-ExtraBold"), ("Nunito-Italic", FONTS, "Nunito-Italic"),
                       ("Caveat", FONTS, "Caveat-Medium"), ("Courier Prime", FONTS, "CourierPrime-Regular"),
                       ("Courier Prime-Bold", FONTS, "CourierPrime-Bold"), ("Bebas", HORROR, "BebasNeue-Regular")]:
        pdfmetrics.registerFont(TTFont(name, os.path.join(d, f + ".ttf")))
    addMapping("Nunito", 0, 0, "Nunito"); addMapping("Nunito", 1, 0, "Nunito-Bold")
    addMapping("Nunito", 0, 1, "Nunito-Italic"); addMapping("Nunito", 1, 1, "Nunito-Bold")
    addMapping("Fraunces", 0, 0, "Fraunces"); addMapping("Fraunces", 1, 0, "Fraunces-SemiBold")
    addMapping("Fraunces", 0, 1, "Fraunces-Italic"); addMapping("Fraunces", 1, 1, "Fraunces-SemiBold")
    addMapping("Courier Prime", 0, 0, "Courier Prime"); addMapping("Courier Prime", 1, 0, "Courier Prime-Bold")

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
        self.kicker = ParagraphStyle("kick", fontName="Nunito-ExtraBold", fontSize=8.6 * s, leading=11 * s, textColor=AMBER_D)
        self.state = ParagraphStyle("state", parent=self.body, fontName="Nunito", fontSize=10.4 * s, leading=14.6 * s, spaceAfter=3 * s)
        self.hand = ParagraphStyle("hand", fontName="Caveat", fontSize=15.5 * s, leading=19 * s, textColor=NAVY, spaceAfter=7 * s)

def para(c, text, x, y, w, style):
    p = Paragraph(text, style)
    _, h = p.wrap(w, 10000)
    p.drawOn(c, x, y - h)
    return y - h - style.spaceAfter

def para_h(text, w, style):
    return Paragraph(text, style).wrap(w, 10000)[1] + style.spaceAfter

def spaced(c, x, y, text, font, size, gap=1.2, col=None, anchor="l"):
    """Letter-spaced capitals (Bebas kickers)."""
    if col is not None:
        c.setFillColor(col)
    w = sum(pdfmetrics.stringWidth(ch, font, size) for ch in text) + gap * (len(text) - 1)
    xx = x - w / 2 if anchor == "c" else (x - w if anchor == "r" else x)
    c.saveState()
    t = c.beginText(xx, y); t.setFont(font, size); t.setCharSpace(gap); t.textOut(text); t.setCharSpace(0); c.drawText(t)
    c.restoreState()
    return w

# ------------------------------------------------------------------ art files
def art_path(kind, key):
    return os.path.join(ARTDIR, f"{kind}_{key}.jpg")

SMALL_SCENE = {4, 5, 6, 11}
def ensure_art(force=False):
    os.makedirs(ARTDIR, exist_ok=True)
    for d in range(1, 25):
        for kind, (w, h) in (("scene", (1600, 500)), ("strip", (1600, 300))):
            p = art_path(kind, d)
            if force or not os.path.exists(p):
                art.scene(d, w, h).save(p, quality=86)

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
            spaced(c, Lx.W - Lx.m, Lx.H - Lx.m + 2, header.upper(), "Bebas", 10.5 * Lx.s, 1.0, STEEL, "r")
        c.setStrokeColor(AMBER); c.setLineWidth(1.1)
        c.line(Lx.m, Lx.H - Lx.m - 6, Lx.W - Lx.m, Lx.H - Lx.m - 6)
        c.setFont("Nunito", 8 * Lx.s); c.setFillColor(SOFT)
        c.drawCentredString(Lx.W / 2, Lx.m - 16, str(self.page))
        c.drawRightString(Lx.W - Lx.m, Lx.m - 16, C.BRAND)
        snowflake(c, Lx.m + 5, Lx.m - 13, 5, AMBER)

    def title_block(self, kicker, title, y=None):
        Lx = self.L; y = y or Lx.top
        spaced(self.c, Lx.m, y - 10 * Lx.s, kicker.upper(), "Bebas", 12 * Lx.s, 1.3, AMBER_D)
        return para(self.c, esc(title), Lx.m, y - 15 * Lx.s, Lx.cw, Lx.h1)

    def link(self, key, x0, y0, x1, y1):
        self.c.linkAbsolute("", key, (x0, y0, x1, y1), thickness=0)

    def save(self):
        self.c.showPage(); self.c.save()

# ------------------------------------------------------------------ small vector icons
def snowflake(c, x, y, r, col):
    c.saveState(); c.setStrokeColor(col); c.setLineWidth(max(0.6, r * 0.16))
    for k in range(6):
        a = math.pi / 3 * k
        c.line(x, y, x + math.cos(a) * r, y + math.sin(a) * r)
        bx, by = x + math.cos(a) * r * 0.55, y + math.sin(a) * r * 0.55
        for sgn in (-1, 1):
            b = a + sgn * math.pi / 4
            c.line(bx, by, bx + math.cos(b) * r * 0.3, by + math.sin(b) * r * 0.3)
    c.restoreState()

def magpie_icon(c, x, y, s, col=INK, belly=WHITE):
    c.saveState(); c.setFillColor(col)
    p = c.beginPath(); p.moveTo(x - s * 0.1, y); p.lineTo(x - s * 0.95, y - s * 0.18); p.lineTo(x - s * 0.95, y - s * 0.3)
    p.lineTo(x - s * 0.05, y - s * 0.14); p.close(); c.drawPath(p, fill=1, stroke=0)
    c.ellipse(x - s * 0.3, y - s * 0.2, x + s * 0.3, y + s * 0.22, fill=1, stroke=0)
    c.circle(x + s * 0.25, y + s * 0.25, s * 0.13, fill=1, stroke=0)
    p = c.beginPath(); p.moveTo(x + s * 0.36, y + s * 0.28); p.lineTo(x + s * 0.55, y + s * 0.24); p.lineTo(x + s * 0.36, y + s * 0.2)
    p.close(); c.drawPath(p, fill=1, stroke=0)
    c.setFillColor(belly); c.ellipse(x - s * 0.08, y - s * 0.18, x + s * 0.24, y + s * 0.08, fill=1, stroke=0)
    c.restoreState()

def checkbox(c, x, y, s, col=STEEL):
    c.saveState(); c.setStrokeColor(col); c.setLineWidth(0.8); c.roundRect(x, y, s, s, 1.6, fill=0, stroke=1); c.restoreState()

def card(c, x, y_top, w, h, fill=PALE, stroke=RULE, r=6):
    c.saveState(); c.setFillColor(fill); c.setStrokeColor(stroke); c.setLineWidth(0.8)
    c.roundRect(x, y_top - h, w, h, r, fill=1, stroke=1); c.restoreState()

def doc_head(c, x, y, w, text, Lx):
    c.setFillColor(NAVY); c.rect(x, y - 17 * Lx.s, w, 17 * Lx.s, fill=1, stroke=0)
    spaced(c, x + 8, y - 12.5 * Lx.s, text, "Bebas", 11.5 * Lx.s, 1.1, WHITE)
    return y - 17 * Lx.s

# ------------------------------------------------------------------ register data
def load_rows():
    rows = []
    with open(os.path.join(HERE, "data", "lantern_register.csv")) as f:
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

LOG_COLS = [("Time in", 42), ("Pass", 38), ("First name", 70), ("Surname", 86), ("Home district", 96),
            ("Door", 48), ("Last till", 44), ("", 20)]

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
    add("cover", None, None, draw_cover)
    if Lx.ipad:
        add("calendar", "The calendar", 0, draw_calendar, "Advent calendar")
    add("howto", "How to play", 0, draw_howto, "Before you begin")
    add("contents", "Contents", 0, draw_contents, "Contents")
    add("rules", "House rules", 0, draw_rules, "House rules")
    if not Lx.ipad:
        add("calendar", "Your advent calendar", 0, draw_calendar, "Advent calendar")
        add("envelope", "Envelope template", 0, draw_envelope, "Set-up")
        add("labels", "Day numbers for the envelopes", 0, draw_labels, "Set-up")
    add("w1", "Window 1 — The Case", 0, draw_w1_case, "Window 1")
    add("w1letter", None, None, draw_w1_letter, "Window 1")
    add("w1plan", None, None, draw_w1_plan, "Window 1")
    add("w2", "Window 2 — The Lantern Register", 0, draw_w2_intro, "Window 2")
    seen = set()
    for i, chunk in enumerate(paginate_log(rows, Lx)):
        title = None
        for it in chunk:
            if it[0] == "band" and it[1] not in seen:
                seen.add(it[1]); title = f"{it[1]:02d}:00–{it[1]:02d}:59"; break
        add(f"log{i}", title, 1 if title else None, (lambda b, chunk=chunk: draw_log_page(b, chunk)), "Window 2 · Lantern Register")
    for cl in C.CLUES:
        d = cl["day"]
        add(f"w{d}", f"Window {d} — {cl['window']}", 0, (lambda b, d=d: draw_window(b, d)), f"Window {d}")
    add("w24", "Window 24 — The Grand Window", 0, draw_w24, "Window 24")
    add("check", "The Sealed Check", 1, draw_check, "Window 24")
    add("notes", "Detective’s notes", 0, draw_notes, "Notes")
    add("hintstop", "Hints", 0, draw_hint_stop, "Hints")
    for lv in range(3):
        for j, chunk in enumerate(hint_pages(Lx)[lv]):
            add(f"hint{lv}_{j}", H.LEVEL_NAMES[lv] if j == 0 else None, 1 if j == 0 else None,
                (lambda b, lv=lv, chunk=chunk, j=j: draw_hint_page(b, lv, chunk, j)), "Hints")
    add("thanks", "Thank you", 0, draw_thanks, "")
    return P

def build_book(fmt, path):
    rows = load_rows()
    b = Book(fmt, path, f"{C.TITLE_PLAIN} — {C.SUBTITLE}")
    b.rows = rows; b.seal = b_seal(C.KILLER); b.fmt = fmt
    b.rep = None
    plan = book_plan(rows, b.L)
    b.plan = plan
    b.pageno = {key: i + 1 for i, (key, *_r) in enumerate(plan)}
    for key, title, level, fn, header in plan:
        b.new_page(key, header, title if (title and level is not None) else None, level or 0, chrome=key != "cover")
        fn(b)
    b.save()
    return b.page

# ------------------------------------------------------------------ cover
def draw_cover(b):
    c, Lx = b.c, b.L
    p = os.path.join(ARTDIR, f"cover_{Lx.fmt}.jpg")
    if not os.path.exists(p):
        raise FileNotFoundError(f"{p} is missing: run listing/src/make_cover_art.py first")
    c.drawImage(p, 0, 0, Lx.W, Lx.H)
    t = c.beginText(); t.setTextRenderMode(3); t.setFont("Nunito", 12)
    for i, line in enumerate([C.TITLE, C.SUBTITLE, C.TAGLINE, f"{C.BRAND} · Printable advent calendar · 24 days"]):
        t.setTextOrigin(40, Lx.H - 60 - i * 16); t.textLine(line)
    c.drawText(t)

# ------------------------------------------------------------------ set-up pages
def draw_howto(b):
    c, Lx = b.c, b.L
    y = b.title_block("Before you begin", "How to play")
    for head, text in C.HOW_TO_PLAY:
        y = para(c, f"<font name='Nunito-ExtraBold' color='#A8601A'>{esc(head)}.</font> {esc(text)}", Lx.m, y, Lx.cw, Lx.body)
    y -= 6
    tips = ("<b>Printing tip.</b> The inside pages are mostly white to save ink; each window has one small "
            "night scene. Window 2, the register, is the thick one: print it single- or double-sided, black "
            "and white is fine. A highlighter and a pencil are all you need.")
    if Lx.ipad:
        tips = ("<b>On a tablet.</b> Open the calendar page and tap today’s window. Every window page has a "
                "link back to the calendar. Highlight passes in the register as you rule them out.")
    h = para_h(tips, Lx.cw - 24, Lx.small) + 18
    card(c, Lx.m, y, Lx.cw, h, fill=AMBER_L, stroke=AMBER_L)
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
        fs = (8.4 if lv == 1 else 9.6) * Lx.s
        font = "Nunito" if lv == 1 else "Nunito-Bold"
        label = ("Register " + t) if k.startswith("log") else t
        while pdfmetrics.stringWidth(label, font, fs) > colw - ind - 30:
            label = label[:-2]
        c.setFont(font, fs); c.setFillColor(INK if lv == 0 else SOFT)
        c.drawString(x0 + ind, y - fs, label)
        c.drawRightString(x0 + colw, y - fs, str(b.pageno[k]))
        b.link(k, x0, y - fs - 3, x0 + colw, y + 2)
        y -= fs * 1.62
    c.setFont("Nunito-Italic", 8.3 * Lx.s); c.setFillColor(SOFT)
    c.drawString(Lx.m, Lx.bottom, "Tap any line to jump to that page. The hint pages are at the back.")

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
    """Print: a tracker to tick off. iPad: 24 tappable windows."""
    c, Lx = b.c, b.L
    y = b.title_block("Advent calendar", "Tap today’s window" if Lx.ipad else "Your advent calendar")
    if Lx.ipad:
        y = para(c, "Each window opens its own day. Every window page has a link back here.", Lx.m, y, Lx.cw, Lx.body)
        spaced(c, Lx.m, y - 6, "TAP TODAY’S WINDOW", "Bebas", 11 * Lx.s, 1.2, STEEL)
        y -= 20
    else:
        y = para(c, "Tick off each window as you open it and write down how many passes are still in. "
                    "The check-ins on Windows 6, 12 and 18 tell you the number to expect.", Lx.m, y, Lx.cw, Lx.body)
    cols, rows_ = 4, 6
    gap = 10 * Lx.s
    cwid = (Lx.cw - gap * (cols - 1)) / cols
    ch = (y - Lx.bottom - 24 - gap * (rows_ - 1)) / rows_
    for d in range(1, 25):
        i = d - 1; cx = Lx.m + (i % cols) * (cwid + gap); cy = y - 6 - (i // cols) * (ch + gap)
        c.setFillColor(NAVY); c.roundRect(cx, cy - ch, cwid, ch, 6, fill=1, stroke=0)
        c.setFillColor(AMBER if d != 24 else AMBER_D)
        c.roundRect(cx + 6, cy - ch * 0.72, cwid - 12, ch * 0.66, 3, fill=1, stroke=0)
        c.setFillColor(NAVY); c.setFont("Bebas", ch * 0.42)
        c.drawCentredString(cx + cwid / 2, cy - ch * 0.56, str(d))
        c.setFillColor(WHITE); c.setFont("Nunito-Bold", 7.2 * Lx.s)
        c.drawCentredString(cx + cwid / 2, cy - ch * 0.86, window_date(d))
        if not Lx.ipad:
            checkbox(c, cx + 8, cy - ch + 5, 7)
            c.setFont("Nunito", 6.6 * Lx.s); c.setFillColor(WHITE)
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
    spaced(c, Lx.W / 2, y - 14, "ENVELOPE TEMPLATE · CUT ON THE SOLID LINE", "Bebas", 11 * Lx.s, 1.2, STEEL, "c")
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
    c.setFillColor(NAVY); c.setFont("Bebas", 24 * Lx.s)
    c.drawCentredString(cx, cy + 4, "QUILLON & DAUGHTERS")
    c.setFont("Nunito", 9 * Lx.s); c.drawCentredString(cx, cy - 14, "Lantern Night · do not open before the day")
    snowflake(c, cx - bw / 2 + 22, cy + bh / 2 - 22, 9, AMBER); snowflake(c, cx + bw / 2 - 22, cy - bh / 2 + 22, 9, AMBER)

def draw_labels(b):
    c, Lx = b.c, b.L
    y = b.title_block("Set-up", "Day numbers for the envelopes")
    y = para(c, "Cut out the 24 circles and stick one on each envelope. Print on sticker paper if you have it.",
             Lx.m, y, Lx.cw, Lx.body)
    spaced(c, Lx.W / 2, y - 10, "DAY NUMBERS 1 – 24", "Bebas", 11 * Lx.s, 1.2, STEEL, "c")
    y -= 18
    cols = 4; rows_ = 6
    cw = Lx.cw / cols; chh = (y - Lx.bottom - 10) / rows_
    r = min(cw, chh) * 0.4
    for d in range(1, 25):
        i = d - 1; cx = Lx.m + cw * (i % cols + 0.5); cy = y - chh * (i // cols + 0.5)
        c.setStrokeColor(RULE); c.setDash(2, 3); c.circle(cx, cy, r + 5, fill=0, stroke=1); c.setDash()
        c.setFillColor(NAVY); c.circle(cx, cy, r, fill=1, stroke=0)
        c.setStrokeColor(AMBER); c.setLineWidth(1.6); c.circle(cx, cy, r * 0.86, fill=0, stroke=1)
        c.setFillColor(AMBER); c.setFont("Bebas", r * 1.05)
        c.drawCentredString(cx, cy - r * 0.36, str(d))
        c.setFillColor(WHITE); c.setFont("Nunito-Bold", r * 0.17)
        c.drawCentredString(cx, cy - r * 0.62, "DECEMBER")

# ------------------------------------------------------------------ window helpers
def window_head(b, d, title, sub=None):
    c, Lx = b.c, b.L
    y = Lx.top
    spaced(c, Lx.m, y - 10 * Lx.s, f"WINDOW {d} OF 24", "Bebas", 13 * Lx.s, 1.4, AMBER_D)
    spaced(c, Lx.W - Lx.m, y - 10 * Lx.s, window_date(d).upper(), "Bebas", 13 * Lx.s, 1.4, STEEL, "r")
    y = para(c, esc(title), Lx.m, y - 15 * Lx.s, Lx.cw, Lx.h1)
    if Lx.ipad and "calendar" in b.pageno:
        c.setFont("Nunito-Bold", 8.5 * Lx.s); c.setFillColor(AMBER_D)
        t = "← calendar"
        c.drawRightString(Lx.W - Lx.m, y + 6, t)
        tw = pdfmetrics.stringWidth(t, "Nunito-Bold", 8.5 * Lx.s)
        b.link("calendar", Lx.W - Lx.m - tw - 4, y + 2, Lx.W - Lx.m + 2, y + 16)
    return y

def scene_img(b, d, y, h, kind="scene"):
    c, Lx = b.c, b.L
    c.saveState()
    p = c.beginPath(); p.roundRect(Lx.m, y - h, Lx.cw, h, 7); c.clipPath(p, stroke=0, fill=0)
    iw, ih = (1600, 500) if kind == "scene" else (1600, 300)
    scale = max(Lx.cw / iw, h / ih)
    dw, dh = iw * scale, ih * scale
    c.drawImage(art_path(kind, d), Lx.m + (Lx.cw - dw) / 2, y - h - (dh - h) / 2, dw, dh)
    c.restoreState()
    return y - h - 10 * Lx.s

def statement_card(b, y, title, who, text, extra=None, width=None, x=None):
    c, Lx = b.c, b.L
    x = Lx.m if x is None else x; w = width or Lx.cw
    inner = w - 24
    hh = para_h(f"<b>{esc(who)}:</b> “{esc(text)}”", inner, Lx.state)
    if extra:
        hh += para_h(f"<i>{esc(extra)}</i>", inner, Lx.small) + 2
    h = hh + 17 * Lx.s + 16
    card(c, x, y, w, h, fill=WHITE)
    yy = doc_head(c, x, y, w, title, Lx)
    yy = para(c, f"<b>{esc(who)}:</b> “{esc(text)}”", x + 12, yy - 8, inner, Lx.state)
    if extra:
        para(c, f"<i>{esc(extra)}</i>", x + 12, yy - 2, inner, Lx.small)
    return y - h - 10 * Lx.s

def question_box(b, y, d, text):
    c, Lx = b.c, b.L
    st = ParagraphStyle("q", parent=Lx.body, fontName="Nunito-Bold", fontSize=10.6 * Lx.s, leading=14.4 * Lx.s)
    inner = Lx.cw - 30
    t2 = ("Work out what today’s evidence means, then cross out every pass in the Lantern Register that "
          "doesn’t fit. Only check the passes that are still in.")
    h = para_h(esc(text), inner, st) + para_h(t2, inner, Lx.small) + 34 * Lx.s
    c.setFillColor(FROST); c.rect(Lx.m, y - h, Lx.cw, h, fill=1, stroke=0)
    c.setFillColor(AMBER); c.rect(Lx.m, y - h, 4, h, fill=1, stroke=0)
    spaced(c, Lx.m + 14, y - 13 * Lx.s, "TODAY’S QUESTION", "Bebas", 11 * Lx.s, 1.2, AMBER_D)
    yy = para(c, esc(text), Lx.m + 14, y - 17 * Lx.s, inner, st)
    yy = para(c, t2, Lx.m + 14, yy, inner, Lx.small)
    c.setFont("Nunito", 8.6 * Lx.s); c.setFillColor(STEEL)
    c.drawString(Lx.m + 14, y - h + 8, "Passes still in tonight:  ________")
    hk = f"hint0_{hint_page_of(b, d)}"
    t = f"Stuck? Hints for Window {d} start on page {b.pageno[hk]}."
    c.drawRightString(Lx.W - Lx.m - 10, y - h + 8, t)
    tw = pdfmetrics.stringWidth(t, "Nunito", 8.6 * Lx.s)
    b.link(hk, Lx.W - Lx.m - 10 - tw, y - h + 5, Lx.W - Lx.m - 10, y - h + 18)
    return y - h - 8 * Lx.s

def checkin_box(b, y, d):
    c, Lx = b.c, b.L
    n = b.counts[d]; empty = b.empty[d]
    chap = ", ".join(f"{h:02d}:00" for h in empty)
    t = (f"If you have used Windows 3 to {d}, there should be <b>{n:,} passes</b> still in"
         + (f", and the register chapters starting {chap} are now completely crossed out." if empty else ".")
         + " A few more is fine if you read a window generously: a later window will catch them. "
         "Fewer? Check the hints for the windows so far.")
    t = t.replace("<b>", "").replace("</b>", "")
    h = para_h(esc(t), Lx.cw - 30, Lx.small) + 22 * Lx.s
    c.setStrokeColor(AMBER); c.setLineWidth(1.2); c.setDash(4, 2)
    c.roundRect(Lx.m, y - h, Lx.cw, h, 6, fill=0, stroke=1); c.setDash()
    spaced(c, Lx.m + 12, y - 12 * Lx.s, "CHECK-IN · WHERE YOU ARE NOW", "Bebas", 11 * Lx.s, 1.2, AMBER_D)
    para(c, esc(t), Lx.m + 12, y - 16 * Lx.s, Lx.cw - 30, Lx.small)
    return y - h - 8 * Lx.s

# ------------------------------------------------------------------ plans and maps (vector)
LEVEL_H = {"floor": 1.0, "half": 0.62, "roof": 0.72}

def store_plan(c, x, y_top, w, h, Lx, compact=False):
    """Cross-section of Quillon's: levels from the Lower Ground to the Roof Terrace, departments with
    their till numbers, the main stairs and the lift (which stops at the five floors only)."""
    total = sum(LEVEL_H[k] for _, _, k in C.LEVELS)
    unit = h / total
    lift_w = w * 0.08; stair_w = w * 0.1; lab_w = w * (0.2 if not compact else 0.19)
    x_d0 = x + lab_w; x_d1 = x + w - lift_w - stair_w - 6
    y = y_top - h
    fs = (6.9 if compact else 7.6) * Lx.s
    for key, name, kind in C.LEVELS:                    # bottom up
        lh = LEVEL_H[kind] * unit
        fill = {"floor": WHITE, "half": FROST, "roof": PALE}[kind]
        c.setFillColor(fill); c.setStrokeColor(STEEL); c.setLineWidth(0.8)
        indent = (x_d1 - x_d0) * 0.18 if kind == "half" else 0
        c.rect(x_d0 + indent, y, x_d1 - x_d0 - indent, lh, fill=1, stroke=1)
        c.setFillColor(NAVY); c.setFont("Nunito-ExtraBold", fs)
        c.drawString(x, y + lh / 2 + 1, name)
        c.setFont("Nunito-Italic", fs * 0.86); c.setFillColor(SOFT)
        sub = {"half": "between floors", "roof": "open air, on top", "floor": ""}[kind]
        if sub:
            c.drawString(x, y + lh / 2 - fs * 0.95, sub)
        depts = [n for n in C.DEPTS if C.dept_level(n) == key]
        dw = (x_d1 - x_d0 - indent) / len(depts)
        for i, n in enumerate(depts):
            dx = x_d0 + indent + i * dw
            if i:
                c.setStrokeColor(RULE); c.line(dx, y + 2, dx, y + lh - 2)
            c.setFillColor(AMBER); c.circle(dx + 10 * Lx.s, y + lh / 2, 7.2 * Lx.s, fill=1, stroke=0)
            c.setFillColor(NAVY); c.setFont("Nunito-ExtraBold", 7.4 * Lx.s)
            c.drawCentredString(dx + 10 * Lx.s, y + lh / 2 - 2.6 * Lx.s, str(n))
            nm = C.dept_name(n)
            c.setFont("Nunito-Bold", fs); c.setFillColor(INK)
            words = nm.split(); line1, line2 = nm, ""
            if pdfmetrics.stringWidth(nm, "Nunito-Bold", fs) > dw - 24 * Lx.s and len(words) > 1:
                k = max(1, len(words) // 2); line1, line2 = " ".join(words[:k]), " ".join(words[k:])
            if line2:
                c.drawString(dx + 20 * Lx.s, y + lh / 2 + 1, line1); c.drawString(dx + 20 * Lx.s, y + lh / 2 - fs, line2)
            else:
                c.drawString(dx + 20 * Lx.s, y + lh / 2 - fs * 0.35, line1)
        y += lh
    # stairs: a zigzag through every level
    sx0 = x_d1 + 4; sx1 = sx0 + stair_w
    c.setStrokeColor(AMBER_D); c.setLineWidth(1.4)
    yy = y_top - h; up = True
    for key, name, kind in C.LEVELS:
        lh = LEVEL_H[kind] * unit
        c.line(sx0 if up else sx1, yy + 2, sx1 if up else sx0, yy + lh - 2)
        up = not up; yy += lh
    c.setFont("Nunito-Bold", 6.6 * Lx.s); c.setFillColor(AMBER_D)
    c.drawCentredString((sx0 + sx1) / 2, y_top + 3, "MAIN STAIRS")
    # lift shaft
    lx0 = sx1 + 4; lx1 = x + w
    c.setFillColor(FROST); c.setStrokeColor(STEEL); c.rect(lx0, y_top - h, lx1 - lx0, h - LEVEL_H["roof"] * unit, fill=1, stroke=1)
    yy = y_top - h
    for key, name, kind in C.LEVELS:
        lh = LEVEL_H[kind] * unit
        if kind == "floor":
            c.setFillColor(NAVY); c.circle((lx0 + lx1) / 2, yy + lh / 2, 3.2, fill=1, stroke=0)
        yy += lh
    c.setFont("Nunito-Bold", 6.6 * Lx.s); c.setFillColor(STEEL)
    c.drawCentredString((lx0 + lx1) / 2, y_top - LEVEL_H["roof"] * unit + 3, "LIFT")

def street_plan(c, x, y_top, w, h, Lx):
    """Top view of the block: four doors, the Winter Garden and the tram shelter. North is up."""
    bx0, bx1 = x + w * 0.3, x + w * 0.74
    by1, by0 = y_top - h * 0.22, y_top - h * 0.7
    c.setFillColor(FROST); c.rect(x, y_top - h, w, h, fill=1, stroke=0)
    # streets
    c.setFillColor(WHITE)
    c.rect(x, by1 + 6, w, y_top - by1 - 14, fill=1, stroke=0)          # Lantern Street
    c.rect(x, y_top - h + 6, w, by0 - (y_top - h) - 12, fill=1, stroke=0)  # Tramway Yard
    c.rect(bx1 + 10, y_top - h + 6, x + w - bx1 - 16, h - 12, fill=1, stroke=0)  # Market Square
    # the store
    c.setFillColor(NAVY); c.rect(bx0, by0, bx1 - bx0, by1 - by0, fill=1, stroke=0)
    c.setFillColor(WHITE); c.setFont("Bebas", 12 * Lx.s)
    c.drawCentredString((bx0 + bx1) / 2, (by0 + by1) / 2 + 2, "QUILLON & DAUGHTERS")
    # Winter Garden glasshouse on the west side, gate onto Tramway Yard
    gx0, gx1 = bx0 - w * 0.16, bx0
    c.setFillColor(PARK); c.setStrokeColor(GREEN); c.setLineWidth(0.8)
    c.rect(gx0, by0, gx1 - gx0, (by1 - by0) * 0.62, fill=1, stroke=1)
    c.setFillColor(GREEN); c.setFont("Nunito-Bold", 7 * Lx.s)
    c.drawCentredString((gx0 + gx1) / 2, by0 + (by1 - by0) * 0.38, "Winter")
    c.drawCentredString((gx0 + gx1) / 2, by0 + (by1 - by0) * 0.38 - 8.5 * Lx.s, "Garden")
    c.drawCentredString((gx0 + gx1) / 2, by0 + (by1 - by0) * 0.38 - 17 * Lx.s, "(glasshouse)")
    c.setFillColor(WHITE); c.rect((gx0 + gx1) / 2 - 8, by0 - 1, 16, 3, fill=1, stroke=0)
    c.setFillColor(GREEN); c.setFont("Nunito-Italic", 6.5 * Lx.s)
    c.drawCentredString((gx0 + gx1) / 2, by0 - 9, "gate")
    def door(px, py, label, side):
        c.setFillColor(AMBER); c.rect(px - 7, py - 3, 14, 6, fill=1, stroke=0)
        c.setFillColor(INK); c.setFont("Nunito-ExtraBold", 7.4 * Lx.s)
        if side == "n":
            c.drawCentredString(px, py + 6, label)
        elif side == "s":
            c.drawCentredString(px, py - 11, label)
        elif side == "e":
            c.drawString(px + 9, py - 2.5, label)
        else:
            c.drawRightString(px - 9, py + 5, label)
    door((bx0 + bx1) / 2, by1, "Arcade Door", "n")
    door((bx0 + bx1) / 2, by0, "Tram Door", "s")
    door(bx1, by0 + (by1 - by0) * 0.22, "Clock Door", "e")
    c.setFillColor(AMBER); c.rect(bx0 - 3, by0 + (by1 - by0) * 0.32, 6, 14, fill=1, stroke=0)
    c.setFillColor(WHITE); c.setFont("Nunito-ExtraBold", 7.4 * Lx.s)
    c.drawString(bx0 + 6, by0 + (by1 - by0) * 0.32 + 3, "Garden Door")
    # street names
    c.setFillColor(STEEL); c.setFont("Nunito-Bold", 8 * Lx.s)
    c.drawString(x + 8, y_top - 14 * Lx.s, "LANTERN STREET")
    c.drawString(x + 8, y_top - h + 9, "TRAMWAY YARD")
    c.saveState(); c.translate(x + w - 12, y_top - h * 0.55); c.rotate(90)
    c.drawCentredString(0, 0, "MARKET SQUARE"); c.restoreState()
    c.setFont("Nunito-Italic", 7 * Lx.s); c.setFillColor(SOFT)
    c.drawCentredString((bx0 + bx1) / 2, y_top - 26 * Lx.s, "Lantern Arcade (covered shops) across the street")
    # clock tower on the square
    c.setStrokeColor(NAVY); c.setFillColor(WHITE); c.circle(x + w * 0.88, y_top - h * 0.36, 9, fill=1, stroke=1)
    c.line(x + w * 0.88, y_top - h * 0.36, x + w * 0.88, y_top - h * 0.36 + 6)
    c.setFont("Nunito", 6.5 * Lx.s); c.setFillColor(SOFT); c.drawCentredString(x + w * 0.88, y_top - h * 0.36 - 18, "clock tower")
    # tram rails and the shelter, opposite the Tram Door
    ry = y_top - h + 26 * Lx.s
    c.setStrokeColor(STEEL); c.setLineWidth(0.7)
    c.line(x, ry, bx1 + 6, ry); c.line(x, ry - 4, bx1 + 6, ry - 4)
    sx = (bx0 + bx1) / 2
    c.setFillColor(NAVY); c.rect(sx - 26, ry - 16, 52, 7, fill=1, stroke=0)
    c.setFillColor(INK); c.setFont("Nunito-ExtraBold", 7 * Lx.s); c.drawCentredString(sx, ry - 25, "No. 7 tram shelter")
    # compass
    c.setFillColor(NAVY); c.setFont("Nunito-ExtraBold", 7 * Lx.s); c.drawCentredString(x + 12, y_top - h * 0.5, "N")
    ax, ay = x + 12, y_top - h * 0.5 + 9
    p = c.beginPath(); p.moveTo(ax, ay + 12); p.lineTo(ax - 4, ay + 2); p.lineTo(ax + 4, ay + 2); p.close()
    c.drawPath(p, fill=1, stroke=0); c.setStrokeColor(NAVY); c.line(ax, ay, ax, ay + 4)

GRID_X = 4
def city_map(c, x, y_top, w, h, Lx, route=True):
    """The city: a 4 x 4 grid of districts, the River Vell, Vell Park and tram Route 7."""
    rows = len(C.GRID); river = h * 0.09
    ch = (h - river) / rows; cw = w / GRID_X
    def cell(r, col):
        yy = y_top - r * ch - (river if r >= 1 else 0)
        return x + col * cw, yy - ch, x + (col + 1) * cw, yy
    def centre(r, col):
        x0, y0, x1, y1 = cell(r, col); return (x0 + x1) / 2, (y0 + y1) / 2
    # river
    c.setFillColor(RIVER); c.rect(x, y_top - ch - river, w, river, fill=1, stroke=0)
    c.setFillColor(STEEL); c.setFont("Nunito-Italic", 7.6 * Lx.s)
    c.drawString(x + w * 0.56, y_top - ch - river * 0.62, "River Vell")
    for r, row in enumerate(C.GRID):
        for col, dname in enumerate(row):
            x0, y0, x1, y1 = cell(r, col)
            if dname is None:
                c.setFillColor(PARK); c.setStrokeColor(GREEN)
                c.rect(x0 + 2, y0 + 2, cw - 4, ch - 4, fill=1, stroke=1)
                c.setFillColor(GREEN)
                for k in range(5):
                    c.circle(x0 + cw * (0.22 + 0.14 * k), y0 + ch * (0.3 + 0.1 * (k % 2)), 4, fill=1, stroke=0)
                c.setFont("Nunito-ExtraBold", 8.6 * Lx.s); c.drawCentredString((x0 + x1) / 2, y0 + ch * 0.62, "VELL PARK")
                continue
            c.setFillColor(WHITE); c.setStrokeColor(RULE); c.setLineWidth(0.8)
            c.rect(x0 + 2, y0 + 2, cw - 4, ch - 4, fill=1, stroke=1)
            c.setFillColor(INK); c.setFont("Nunito-Bold", 8.1 * Lx.s)
            c.drawCentredString((x0 + x1) / 2, y1 - 12 * Lx.s, dname)
            if dname == "Cathedral Close":
                cx, cy = (x0 + x1) / 2, y0 + ch * 0.35
                c.setFillColor(STEEL)
                p = c.beginPath(); p.moveTo(cx - 8, cy - 7); p.lineTo(cx + 8, cy - 7); p.lineTo(cx + 8, cy + 3)
                p.lineTo(cx, cy + 14); p.lineTo(cx - 8, cy + 3); p.close(); c.drawPath(p, fill=1, stroke=0)
                c.setFont("Nunito-Italic", 6.4 * Lx.s); c.drawCentredString(cx, cy - 16, "cathedral")
            if dname == "Saltmarket":
                cx, cy = x0 + cw * 0.28, y0 + ch * 0.36
                c.setFillColor(NAVY); c.rect(cx - 12, cy - 6, 24, 12, fill=1, stroke=0)
                c.setFillColor(AMBER); c.rect(cx - 9, cy - 3, 18, 5, fill=1, stroke=0)
                c.setFillColor(SOFT); c.setFont("Nunito-Italic", 6.4 * Lx.s); c.drawCentredString(cx, cy - 15, "Quillon’s")
    # Vell Bridge
    bx = x + cw * 1.5
    c.setFillColor(STEEL); c.rect(bx - 7, y_top - ch - river, 14, river, fill=1, stroke=0)
    if not route:
        return
    pts = []
    offs = {"Saltmarket": (0.3, -0.12)}
    for i, (stop, dname) in enumerate(C.TRAM7):
        r, col = C.POS[dname]
        cx, cy = centre(r, col)
        ox, oy = offs.get(dname, (0, -0.1))
        pts.append((cx + ox * cw, cy + oy * ch))
    c.setStrokeColor(AMBER_D); c.setLineWidth(2.6); c.setLineJoin(1)
    p = c.beginPath(); p.moveTo(*pts[0])
    for pt in pts[1:]:
        p.lineTo(*pt)
    c.drawPath(p, fill=0, stroke=1)
    for i, ((stop, dname), (px, py)) in enumerate(zip(C.TRAM7, pts)):
        c.setFillColor(WHITE); c.setStrokeColor(AMBER_D); c.setLineWidth(1.6); c.circle(px, py, 7.4 * Lx.s, fill=1, stroke=1)
        c.setFillColor(AMBER_D); c.setFont("Nunito-ExtraBold", 6.8 * Lx.s); c.drawCentredString(px, py - 2.4 * Lx.s, str(i + 1))
        c.setFillColor(AMBER_D); c.setFont("Nunito-Bold", 6.9 * Lx.s)
        c.drawCentredString(px, py - 15 * Lx.s, f"stop: {stop}")
    c.setFillColor(AMBER_D); c.setFont("Nunito-ExtraBold", 7.6 * Lx.s)
    c.drawString(x + 4, y_top - h - 11 * Lx.s, "— Route 7 tram, stops numbered in order from Quillon’s to Gasworks (the end of the line)")

# ------------------------------------------------------------------ Window 1
def draw_w1_case(b):
    c, Lx = b.c, b.L
    y = window_head(b, 1, "The Case")
    y = scene_img(b, 1, y, Lx.cw / 3.2)
    for ptxt in C.INTRO:
        y = para(c, esc(ptxt), Lx.m, y, Lx.cw, Lx.body)
    y = para(c, "What we know for certain", Lx.m, y - 2, Lx.cw, Lx.h2)
    for f in C.KNOWN_FACTS:
        snowflake(c, Lx.m + 4, y - 6 * Lx.s, 3.4, AMBER)
        y = para(c, esc(f), Lx.m + 14, y, Lx.cw - 14, Lx.small)

def draw_w1_letter(b):
    c, Lx = b.c, b.L
    spaced(c, Lx.m, Lx.top - 10 * Lx.s, "WINDOW 1 · CONTINUED", "Bebas", 13 * Lx.s, 1.4, AMBER_D)
    y = para(c, "Teodor’s letter", Lx.m, Lx.top - 15 * Lx.s, Lx.cw, Lx.h1)
    h = y - Lx.bottom - 50
    c.setFillColor(HexColor("#FBF8F1")); c.setStrokeColor(RULE)
    c.rect(Lx.m + 6, y - h, Lx.cw - 12, h, fill=1, stroke=1)
    c.setStrokeColor(HexColor("#E6E9EF")); c.setLineWidth(0.5)
    yy = y - 30
    while yy > y - h + 10:
        c.line(Lx.m + 16, yy, Lx.W - Lx.m - 16, yy); yy -= 19 * Lx.s
    yy = y - 18
    for i, line in enumerate(C.LETTER):
        st = Lx.hand
        yy = para(c, esc(line), Lx.m + 26, yy, Lx.cw - 52, st)
    magpie_icon(c, Lx.W - Lx.m - 60, y - h + 40, 26, col=NAVY)
    para(c, f"<i>{esc(C.LETTER_NOTE)}</i>", Lx.m, y - h - 8, Lx.cw, Lx.small)

def draw_w1_plan(b):
    c, Lx = b.c, b.L
    spaced(c, Lx.m, Lx.top - 10 * Lx.s, "WINDOW 1 · CONTINUED", "Bebas", 13 * Lx.s, 1.4, AMBER_D)
    y = para(c, "The store plan", Lx.m, Lx.top - 15 * Lx.s, Lx.cw, Lx.h1)
    y = para(c, "Every department has a till with the same number. Levels from the bottom up; the Half Landing "
                "and the Clock Gallery are half-levels between floors. The street plan below shows the four doors.",
             Lx.m, y, Lx.cw, Lx.small)
    ph = (y - Lx.bottom) * 0.56
    store_plan(c, Lx.m, y - 8, Lx.cw, ph, Lx)
    y = y - ph - 20
    street_plan(c, Lx.m, y, Lx.cw, y - Lx.bottom - 4, Lx)

# ------------------------------------------------------------------ Window 2: the register
def draw_w2_intro(b):
    c, Lx = b.c, b.L
    y = window_head(b, 2, "The Lantern Register")
    y = scene_img(b, 2, y, Lx.cw / 3.6)
    y = para(c, "Every Lantern Pass scanned at the doors on Christmas Eve, in the order it was scanned: "
                "2,400 shoppers, one line each. Keep this window out of its envelope from now on: every "
                "window from tomorrow is checked against it.", Lx.m, y, Lx.cw, Lx.body)
    rows = [("Time in", "when the pass was scanned at the door (24-hour clock)"),
            ("Pass", "pass number, 0001–2400"),
            ("First name, Surname", "as written on the pass form"),
            ("Home district", "as written on the pass form; every district is on the city map (Window 6)"),
            ("Door", "Arcade, Clock, Tram or Garden (the Arcade Door, Clock Door, Tram Door, Garden Door)"),
            ("Last till", "the department number of the pass’s final purchase (store plan, Window 1)"),
            ("Box", "an empty box for your own ticks")]
    for k, v in rows:
        c.setFont("Nunito-ExtraBold", 9.6 * Lx.s); c.setFillColor(NAVY)
        c.drawString(Lx.m, y - 11 * Lx.s, k)
        y = min(para(c, esc(v), Lx.m + 128 * Lx.s, y, Lx.cw - 128 * Lx.s, Lx.small), y - 16 * Lx.s)
    y = para(c, "Chapters", Lx.m, y - 6, Lx.cw, Lx.h2)
    y = para(c, "The register is split into hourly chapters. Tap a chapter to jump to it.", Lx.m, y, Lx.cw, Lx.small)
    col = 0; yy = y
    for key, title, level, _, _ in b.plan:
        if key.startswith("log") and title:
            xx = Lx.m + col * Lx.cw / 2
            c.setFont("Nunito-Bold", 10 * Lx.s); c.setFillColor(INK)
            c.drawString(xx + 6, yy - 12 * Lx.s, title)
            c.drawRightString(xx + Lx.cw / 2 - 20, yy - 12 * Lx.s, f"page {b.pageno[key]}")
            b.link(key, xx, yy - 16 * Lx.s, xx + Lx.cw / 2 - 16, yy)
            col = 1 - col
            if col == 0:
                yy -= 18 * Lx.s

def draw_log_page(b, chunk):
    c, Lx = b.c, b.L
    rh, _ = log_geometry(Lx)
    recs = [it[1] for it in chunk if it[0] == "rec"]
    scale = min(Lx.cw / sum(w for _, w in LOG_COLS), 1.4)
    cols = [(n, w * scale) for n, w in LOG_COLS]
    tw = sum(w for _, w in cols); x0 = Lx.m + (Lx.cw - tw) / 2
    y = Lx.top + 6
    spaced(c, x0, y - 13 * Lx.s, "WINDOW 2 OF 24 · LANTERN REGISTER", "Bebas", 12 * Lx.s, 1.2, AMBER_D)
    c.setFont("Nunito-Bold", 9 * Lx.s); c.setFillColor(INK)
    c.drawRightString(x0 + tw, y - 13 * Lx.s, f"times in {C.tstr(recs[0]['entry'])} – {C.tstr(recs[-1]['entry'])}")
    y -= 26 * Lx.s
    fs = 8.5 if not Lx.ipad else 10.1
    c.setFont("Nunito-ExtraBold", fs * 0.86); c.setFillColor(AMBER_D)
    x = x0
    for n, w in cols:
        c.drawString(x + 3, y - rh + 3, n.upper()); x += w
    y -= rh
    c.setStrokeColor(NAVY); c.setLineWidth(0.9); c.line(x0, y, x0 + tw, y)
    zebra = 0
    for kind, v in chunk:
        if kind == "band":
            c.setFillColor(AMBER_L); c.rect(x0, y - rh, tw, rh, fill=1, stroke=0)
            c.setFillColor(NAVY); c.setFont("Fraunces-SemiBold", fs)
            c.drawString(x0 + 6, y - rh + 3, f"Chapter · {v:02d}:00–{v:02d}:59")
            y -= rh; zebra = 0; continue
        if zebra % 2:
            c.setFillColor(PALE); c.rect(x0, y - rh, tw, rh, fill=1, stroke=0)
        zebra += 1
        vals = [C.tstr(v["entry"]), f"{v['ticket']:04d}", v["first"], v["last"], v["town"], v["gate"], str(v["stall"]), ""]
        x = x0; c.setFillColor(INK)
        for (n, w), val in zip(cols, vals):
            if n == "":
                c.setStrokeColor(RULE); c.setLineWidth(0.6)
                c.rect(x + 5, y - rh + 2.5, rh - 5, rh - 5, fill=0, stroke=1)
            else:
                c.setFont("Nunito-Bold" if n in ("Time in", "Pass") else "Nunito", fs)
                c.drawString(x + 3, y - rh + 3, val)
            x += w
        y -= rh
    c.setStrokeColor(NAVY); c.setLineWidth(0.9); c.line(x0, y, x0 + tw, y)

# ------------------------------------------------------------------ Windows 3-23
def programme(b, y, D):
    c, Lx = b.c, b.L
    w = Lx.cw * 0.5
    h = 17 * Lx.s + len(D["lines"]) * 15 * Lx.s + 10
    card(c, Lx.m, y, w, h, fill=WHITE)
    yy = doc_head(c, Lx.m, y, w, "THE BAND ON THE STEPS", Lx) - 6
    for a, t in D["lines"]:
        bold = "set" in a
        c.setFont("Nunito-ExtraBold" if bold else "Nunito", 9.6 * Lx.s); c.setFillColor(NAVY if bold else SOFT)
        c.drawString(Lx.m + 10, yy - 11 * Lx.s, a)
        c.setFont("Courier Prime-Bold" if bold else "Courier Prime", 9.8 * Lx.s)
        c.drawRightString(Lx.m + w - 10, yy - 11 * Lx.s, t)
        yy -= 15 * Lx.s
    # the statement sits beside the programme
    x2 = Lx.m + w + 10
    who, text = D["statement"]
    statement_card(b, y, "STATEMENT — THE DOORMAN", who, text, width=Lx.cw - w - 10, x=x2)
    return y - h - 10 * Lx.s

def stamp_example(b, y):
    c, Lx = b.c, b.L
    w = Lx.cw; h = 74 * Lx.s
    card(c, Lx.m, y, w, h, fill=WHITE)
    cx, cy = Lx.m + 50 * Lx.s, y - h / 2
    c.setFillColor(AMBER_L); c.roundRect(cx - 40 * Lx.s, cy - 26 * Lx.s, 80 * Lx.s, 52 * Lx.s, 4, fill=1, stroke=0)
    c.setStrokeColor(NAVY); c.setLineWidth(1.4); c.circle(cx, cy, 20 * Lx.s, fill=0, stroke=1)
    for k in range(12):
        a = math.pi / 2 - k * math.pi / 6
        c.line(cx + math.cos(a) * 16 * Lx.s, cy + math.sin(a) * 16 * Lx.s, cx + math.cos(a) * 19 * Lx.s, cy + math.sin(a) * 19 * Lx.s)
    a = math.pi / 2 - 2 * math.pi / 6           # example: the hand on 2 (ten past)
    c.setLineWidth(2); c.line(cx, cy, cx + math.cos(a) * 15 * Lx.s, cy + math.sin(a) * 15 * Lx.s)
    c.setDash(2, 2); c.setStrokeColor(SOFT); c.setLineWidth(0.6)
    c.line(cx - 24 * Lx.s, cy, cx + 24 * Lx.s, cy); c.setDash()
    para(b.c, "<b>Example stamp:</b> a pass scanned at ten past the hour (any hour). The hand points to the 2. "
              "The dotted line through 9 and 3 splits the face into an upper and a lower half.",
         Lx.m + 104 * Lx.s, y - 14, w - 116 * Lx.s, Lx.small)
    return y - h - 10 * Lx.s

def passes_swatch(b, y):
    c, Lx = b.c, b.L
    h = 60 * Lx.s
    for k, (col, lab) in enumerate(((GREEN, "0001 – 1200"), (RED, "1201 – 2400"))):
        x = Lx.m + k * 150 * Lx.s
        c.setFillColor(col); c.roundRect(x, y - h, 136 * Lx.s, h - 6, 6, fill=1, stroke=0)
        c.setFillColor(WHITE); c.setFont("Bebas", 15 * Lx.s); c.drawString(x + 10, y - 22 * Lx.s, "LANTERN PASS")
        c.setFont("Courier Prime-Bold", 12 * Lx.s); c.drawString(x + 10, y - 42 * Lx.s, lab)
        c.setStrokeColor(WHITE); c.circle(x + 112 * Lx.s, y - 28 * Lx.s, 12 * Lx.s, fill=0, stroke=1)
    return y - h - 8 * Lx.s

def draw_window(b, d):
    c, Lx = b.c, b.L
    cl = next(x for x in C.CLUES if x["day"] == d)
    D = C.DOCS[d]
    y = window_head(b, d, cl["window"])
    small = d in SMALL_SCENE
    y = scene_img(b, d, y, Lx.cw / (5.4 if small else 3.3), "strip" if small else "scene")
    if D["kind"] == "programme":
        y = programme(b, y, D)
    else:
        who, text = D["statement"]
        extra = D.get("extra")
        if d == 16:
            extra = None
        y = statement_card(b, y, D["title"], who, text, extra if d != 16 else None)
        if d == 16:
            y = statement_card(b, y, "STATEMENT — THE DOORMAN", C.DOORMAN, D["extra"].split("“")[1].rstrip("”"))
            y = stamp_example(b, y)
        if d == 20:
            y = passes_swatch(b, y)
        if d == 4:
            ph = 150 * Lx.s
            street_plan(c, Lx.m, y, Lx.cw, ph, Lx); y -= ph + 10 * Lx.s
        if d == 5:
            ph = 190 * Lx.s
            store_plan(c, Lx.m, y - 4, Lx.cw, ph, Lx, compact=True); y -= ph + 16 * Lx.s
        if d in (6, 11):
            ph = (220 if d == 6 else 236) * Lx.s
            city_map(c, Lx.m, y, Lx.cw, ph, Lx, route=True); y -= ph + (20 if d == 6 else 18) * Lx.s
    y = question_box(b, y, d, cl["note"])
    if d in C.CHECKPOINTS:
        y = checkin_box(b, y, d)
    if y < Lx.bottom - 4:
        raise RuntimeError(f"[{Lx.fmt}] Window {d} overflows the page by {Lx.bottom - y:.0f} pt")

# ------------------------------------------------------------------ Window 24, check, notes, hints
def draw_w24(b):
    c, Lx = b.c, b.L
    y = window_head(b, 24, "The Grand Window")
    y = scene_img(b, 24, y, Lx.cw / 2.4)
    for ptxt in [
        "21:30, Christmas Eve. The brass band played a fanfare, the curtain rose, and Lantern Street saw "
        "an empty window. Teodor’s Grand Window was never finished.",
        "His sketchbook was. On its last page he had drawn it: snow, a single gloved hand holding out a "
        "necklace, and a magpie taking it. ‘For the one who has been taking my stones,’ he wrote underneath. "
        "‘Everyone on Lantern Street will know her by the brooch.’",
        "If you have opened every window, one Lantern Pass is left in the register. That pass belongs to "
        "the lady with the brass magpie.",
        "Turn the page for the Sealed Check: it tells you whether you are right without printing her name "
        "anywhere in this calendar. Then open the Envelope, the separate solution file, to read how it happened."]:
        y = para(c, esc(ptxt), Lx.m, y, Lx.cw, Lx.body)
    magpie_icon(c, Lx.W / 2, y - 30, 30, col=NAVY)

def draw_check(b):
    c, Lx = b.c, b.L
    spaced(c, Lx.m, Lx.top - 10 * Lx.s, "WINDOW 24 · CONTINUED", "Bebas", 13 * Lx.s, 1.4, AMBER_D)
    y = para(c, "The Sealed Check", Lx.m, Lx.top - 15 * Lx.s, Lx.cw, Lx.h1)
    y = para(c, "Found your one remaining pass? Do this sum with its details (a phone calculator is fine). It "
                "confirms the answer without printing the killer’s name anywhere in this calendar.", Lx.m, y, Lx.cw, Lx.body)
    steps = ["Take the pass number and multiply it by 7.",
             "Count the letters in the first name and in the surname, and add both counts to the result.",
             "Look at the last three digits of the total."]
    for i, s in enumerate(steps, 1):
        c.setFillColor(AMBER); c.circle(Lx.m + 10, y - 9 * Lx.s, 9 * Lx.s, fill=1, stroke=0)
        c.setFillColor(NAVY); c.setFont("Nunito-ExtraBold", 10 * Lx.s)
        c.drawCentredString(Lx.m + 10, y - 12.5 * Lx.s, str(i))
        y = min(para(c, esc(s), Lx.m + 30 * Lx.s, y, Lx.cw - 30 * Lx.s, Lx.body), y - 24 * Lx.s)
    y -= 6
    for lab in ["Pass number × 7 =", "+ letters in first name =", "+ letters in surname =", "Last three digits ="]:
        c.setFont("Nunito-Bold", 11 * Lx.s); c.setFillColor(INK); c.drawString(Lx.m + 10, y - 16 * Lx.s, lab)
        c.setStrokeColor(NAVY); c.setLineWidth(0.9)
        c.roundRect(Lx.m + 190 * Lx.s, y - 24 * Lx.s, 140 * Lx.s, 24 * Lx.s, 4, fill=0, stroke=1)
        y -= 34 * Lx.s
    y -= 8
    bh = 96 * Lx.s
    c.setFillColor(NAVY); c.roundRect(Lx.m, y - bh, Lx.cw, bh, 10, fill=1, stroke=0)
    c.setFillColor(WHITE); c.setFont("Nunito", 11 * Lx.s)
    c.drawCentredString(Lx.W / 2, y - 26 * Lx.s, "If your last three digits are")
    c.setFont("Fraunces-SemiBold", 34 * Lx.s); c.setFillColor(AMBER)
    c.drawCentredString(Lx.W / 2, y - 62 * Lx.s, b.seal)
    c.setFont("Nunito", 11 * Lx.s); c.setFillColor(WHITE)
    c.drawCentredString(Lx.W / 2, y - 84 * Lx.s, "you have found her. Open the Envelope to read how it happened.")
    y -= bh + 14
    para(c, "Not a match? Somewhere a pass was kept or crossed out by mistake. The hints at the back show "
            "you which window to look at again, and the check-ins on Windows 6, 12 and 18 help you find where.",
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
    c.setFillColor(FROST); c.rect(Lx.m, Lx.bottom + 40, Lx.cw, Lx.top - Lx.bottom - 60, fill=1, stroke=0)
    for i in range(16):
        fx = Lx.m + 30 + (i * 53) % (Lx.cw - 40); fy = Lx.top - 60 - (i * 97) % (Lx.top - Lx.bottom - 160)
        if abs(fx - Lx.W / 2) < Lx.cw * 0.38 and Lx.H / 2 - 160 * Lx.s < fy < Lx.H / 2 + 80 * Lx.s:
            continue
        snowflake(c, fx, fy, 6, AMBER)
    magpie_icon(c, Lx.W / 2, Lx.H / 2 + 120 * Lx.s, 34 * Lx.s, col=NAVY, belly=FROST)
    spaced(c, Lx.W / 2, Lx.H / 2 + 60 * Lx.s, "STOP, DETECTIVE", "Bebas", 14 * Lx.s, 2, AMBER_D, "c")
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
        c.setFont("Nunito-ExtraBold", 10 * Lx.s); c.setFillColor(AMBER_D)
        c.drawString(Lx.m, y - 11 * Lx.s, f"Window {cid}")
        y = min(para(c, esc(H.HINTS[cid][lv]), Lx.m + 96 * Lx.s, y, Lx.cw - 96 * Lx.s, st), y - 22 * Lx.s) - 6

def draw_thanks(b):
    c, Lx = b.c, b.L
    y = b.title_block(C.BRAND, "Thank you, detective")
    for ptxt in ["Thank you for spending Advent at Quillon’s. We hope the windows, the snow and the brass magpie "
                 "kept you guessing until Christmas Eve.",
                 "Every QuietClueCo case is written and drawn by hand and checked by a computer program before it "
                 "reaches you. The program confirms that there is exactly one answer, that every window is needed, "
                 "and that the answer does not change if a window is read in a slightly different way, including "
                 "the words on the plans and maps such as straight, through, higher, between and next to.",
                 "If you enjoyed the calendar, a short review helps other detectives find us.",
                 "For personal use only. Please don’t share or resell the files. You may print as many copies as "
                 "you need for your own household or game night.",
                 "Fonts: Fraunces, Nunito, Caveat, Courier Prime and Bebas Neue (SIL Open Font License). All "
                 "illustrations are drawn with code. No AI-generated images are used."]:
        y = para(c, esc(ptxt), Lx.m, y, Lx.cw, Lx.body)

# ------------------------------------------------------------------ solution file
def build_solution(fmt, path, walk, finalists, index):
    b = Book(fmt, path, f"{C.TITLE_PLAIN} — The Envelope (solution)")
    c, Lx = b.c, b.L
    K = C.KILLER
    b.new_page("answer", "Solution", "The answer")
    c.setFillColor(NAVY); c.roundRect(Lx.m, Lx.top - 250 * Lx.s, Lx.cw, 250 * Lx.s, 12, fill=1, stroke=0)
    spaced(c, Lx.W / 2, Lx.top - 34 * Lx.s, "THE ENVELOPE · OPEN AFTER THE SEALED CHECK", "Bebas", 12 * Lx.s, 1.5, AMBER, "c")
    c.setFillColor(WHITE); c.setFont("Fraunces-SemiBold", 40 * Lx.s)
    c.drawCentredString(Lx.W / 2, Lx.top - 100 * Lx.s, f"{K['first']} {K['last']}")
    c.setFont("Nunito", 11.5 * Lx.s)
    c.drawCentredString(Lx.W / 2, Lx.top - 132 * Lx.s,
                        f"Pass {K['ticket']:04d} · {K['town']} · in at {C.tstr(K['entry'])} by the "
                        f"{C.DOOR_NAMES[K['gate']]} · last till {K['stall']} ({C.dept_name(K['stall'])})")
    c.setFont("Nunito-Italic", 10.5 * Lx.s)
    c.drawCentredString(Lx.W / 2, Lx.top - 160 * Lx.s, f"Sealed Check: {K['ticket']:04d} × 7 + {len(K['first'])} + "
                        f"{len(K['last'])} = {K['ticket'] * 7 + len(K['first']) + len(K['last'])}, last three digits {b_seal(K)}")
    c.setFont("Nunito", 10.5 * Lx.s)
    c.drawCentredString(Lx.W / 2, Lx.top - 200 * Lx.s, "In this file: what really happened · the solution day by day · "
                        "the finalists ·")
    c.drawCentredString(Lx.W / 2, Lx.top - 216 * Lx.s, "and an index showing which window rules out each of the 2,400 passes.")
    y = Lx.top - 280 * Lx.s
    y = para(c, "What really happened", Lx.m, y, Lx.cw, Lx.h2)
    for ptxt in C.EPILOGUE:
        if y - para_h(esc(ptxt), Lx.cw, Lx.body) < Lx.bottom:
            b.new_page(None, "Solution"); y = Lx.top
        y = para(c, esc(ptxt), Lx.m, y, Lx.cw, Lx.body)
    b.new_page("walk", "Solution", "Day by day")
    y = b.title_block("The solution", "Day by day")
    y = para(c, "What each window means and how many passes it rules out, in calendar order.", Lx.m, y, Lx.cw, Lx.body)
    cols = [("Day", 34), ("Window", 92), ("What it tells you", Lx.cw - 230), ("Out", 46), ("Left", 58)]
    st = ParagraphStyle("w", parent=Lx.small, spaceAfter=0)
    def head(y):
        x = Lx.m; c.setFont("Nunito-ExtraBold", 8.3 * Lx.s); c.setFillColor(AMBER_D)
        for n, w in cols:
            c.drawString(x + 4, y - 11, n.upper()); x += w
        y -= 16; c.setStrokeColor(NAVY); c.line(Lx.m, y, Lx.W - Lx.m, y); return y
    y = head(y)
    c.setFont("Nunito", 9 * Lx.s); c.setFillColor(INK)
    c.drawString(Lx.m + 130, y - 12, "Window 2: the Lantern Register"); c.drawRightString(Lx.W - Lx.m - 6, y - 12, "2,400")
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
    y = para(c, "These shoppers fit every window but one. Each is ruled out by exactly the window shown, which is "
                "how we know every window in the calendar is needed.", Lx.m, y, Lx.cw, Lx.body)
    fcols = [("Pass", 40), ("Shopper", 112), ("District", 84), ("Door", 44), ("In", 36), ("Till", 30), ("Ruled out by", Lx.cw - 346)]
    x = Lx.m; c.setFont("Nunito-ExtraBold", 8.3 * Lx.s); c.setFillColor(AMBER_D)
    for n, w in fcols:
        c.drawString(x + 3, y - 11, n.upper()); x += w
    y -= 16; c.setStrokeColor(NAVY); c.line(Lx.m, y, Lx.W - Lx.m, y)
    fs = 8.4 * Lx.s; rh = 14.5 * Lx.s
    for i, f in enumerate(finalists):
        if y - rh < Lx.bottom:
            b.new_page(None, "Solution"); y = Lx.top
        if i % 2:
            c.setFillColor(PALE); c.rect(Lx.m, y - rh, Lx.cw, rh, fill=1, stroke=0)
        r = f["rec"]
        vals = [f"{r['ticket']:04d}", f"{r['first']} {r['last']}", r["town"], r["gate"], C.tstr(r["entry"]), str(r["stall"]), f["why"]]
        x = Lx.m
        for (n, w), v in zip(fcols, vals):
            c.setFillColor(AMBER_D if (n == "Ruled out by" and f["clue"] == "KILLER") else INK)
            c.setFont("Nunito-Bold" if n in ("Pass", "Ruled out by") else "Nunito", fs)
            vv = v
            while pdfmetrics.stringWidth(vv, "Nunito", fs) > w - 5 and len(vv) > 4:
                vv = vv[:-2] + "…" if not vv.endswith("…") else vv[:-3] + "…"
            c.drawString(x + 3, y - rh + 4, vv); x += w
        y -= rh
    b.new_page("index", "Solution", "Elimination index")
    y = b.title_block("The solution", "Elimination index")
    y = para(c, "Every pass from 0001 to 2400 with the first window (in calendar order) that rules it out. If you kept "
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
                c.setFillColor(AMBER_D if v == "KILLER" else SOFT)
                c.drawString(xx + 25 * Lx.s, yy + 2, v if v == "KILLER" else f"W{v}")
                i += 1
    c.setFont("Nunito-Italic", 8 * Lx.s); c.setFillColor(SOFT)
    c.drawString(Lx.m, Lx.bottom - 4, "KILLER = the only pass that fits every window. W3 to W23 = the window that rules the pass out.")
    b.save()
    return b.page

def b_seal(K):
    return f"{(K['ticket'] * 7 + len(K['first']) + len(K['last'])) % 1000:03d}"
