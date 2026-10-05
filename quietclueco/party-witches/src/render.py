"""Render the party kit for Murder at the Lantern Supper (ReportLab).

    host guide   cover, welcome, how it works, before the party, casting, the evening, plan of the house,
                 round scripts, FAQ, and at the very end the SEALED SOLUTION
    player kit   cover, printing guide, house rules, plan of the house, 12 character booklets (4 pages each:
                 your character, Round 1, Round 2, Round 3), 11 evidence cards, detective's notes,
                 accusation sheets, name badges, potion menu, awards

Inside pages are light (white with moon-parchment panels) to save ink; the covers are the dark poster.
"""
import math, os
from reportlab.lib.pagesizes import LETTER, A4
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
from reportlab.pdfgen import canvas
import case as C

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")
ART = os.path.join(HERE, "art")

PLUM = HexColor("#2B1B3D"); AUB = HexColor("#4A2C5E"); AMETHYST = HexColor("#8E5BB5"); GOLD = HexColor("#E3A64B")
PARCH = HexColor("#EDE6D6"); SAGE = HexColor("#8FA382"); INK = HexColor("#1E1A22"); WHITE = HexColor("#FFFFFF")
PALE = HexColor("#F7F3EC"); RULE = HexColor("#DCD3C4"); SOFT = HexColor("#68606E"); LILAC = HexColor("#EFE7F5")
CANDLE = {"green": HexColor("#4E7A52"), "amber": HexColor("#D9902F"), "white": HexColor("#F4F1EA"),
          "violet": HexColor("#7B4FA8"), "blue": HexColor("#3E6CA8"), "red": HexColor("#B4473A"),
          "gold": HexColor("#D8B04A")}

def register_fonts():
    for name, f in [("Fraunces", "Fraunces-Regular"), ("Fraunces-SemiBold", "Fraunces-SemiBold"),
                    ("Fraunces-Bold", "Fraunces-Bold"), ("Fraunces-Italic", "Fraunces-Italic"),
                    ("Nunito", "Nunito-Regular"), ("Nunito-Bold", "Nunito-Bold"),
                    ("Nunito-ExtraBold", "Nunito-ExtraBold"), ("Nunito-Italic", "Nunito-Italic"),
                    ("Caveat", "Caveat-Medium")]:
        pdfmetrics.registerFont(TTFont(name, os.path.join(FONTS, f + ".ttf")))
    addMapping("Nunito", 0, 0, "Nunito"); addMapping("Nunito", 1, 0, "Nunito-Bold")
    addMapping("Nunito", 0, 1, "Nunito-Italic"); addMapping("Nunito", 1, 1, "Nunito-Bold")
    addMapping("Fraunces", 0, 0, "Fraunces"); addMapping("Fraunces", 1, 0, "Fraunces-SemiBold")
    addMapping("Fraunces", 0, 1, "Fraunces-Italic"); addMapping("Fraunces", 1, 1, "Fraunces-SemiBold")

FORMATS = {"letter": LETTER, "a4": A4}
def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

class L:
    def __init__(self, fmt):
        self.fmt = fmt; self.W, self.H = FORMATS[fmt]
        self.m = 54; self.cw = self.W - 2 * self.m
        self.top = self.H - self.m - 22; self.bottom = self.m + 16
        self.body = ParagraphStyle("body", fontName="Nunito", fontSize=10.5, leading=15, textColor=INK, spaceAfter=6)
        self.small = ParagraphStyle("small", parent=self.body, fontSize=9, leading=12.4, spaceAfter=4)
        self.big = ParagraphStyle("big", parent=self.body, fontSize=12, leading=17, spaceAfter=8)
        self.h1 = ParagraphStyle("h1", fontName="Fraunces-SemiBold", fontSize=26, leading=31, textColor=PLUM, spaceAfter=6)
        self.h2 = ParagraphStyle("h2", fontName="Fraunces-SemiBold", fontSize=15, leading=19, textColor=PLUM, spaceAfter=4)
        self.h3 = ParagraphStyle("h3", fontName="Nunito-ExtraBold", fontSize=11, leading=14, textColor=AUB, spaceAfter=3)
        self.kicker = ParagraphStyle("k", fontName="Nunito-ExtraBold", fontSize=8.5, leading=11, textColor=AMETHYST)
        self.say = ParagraphStyle("say", parent=self.body, fontName="Fraunces-Italic", fontSize=11.5, leading=16.5,
                                  textColor=PLUM, leftIndent=14, spaceAfter=8)

def para(c, text, x, y, w, style):
    p = Paragraph(text, style); _, h = p.wrap(w, 10000); p.drawOn(c, x, y - h); return y - h - style.spaceAfter
def para_h(text, w, style):
    return Paragraph(text, style).wrap(w, 10000)[1] + style.spaceAfter

# ---------------------------------------------------------------- small drawn icons
def crescent(c, x, y, r, col=GOLD, bg=WHITE):
    c.saveState(); c.setFillColor(col); c.circle(x, y, r, fill=1, stroke=0)
    c.setFillColor(bg); c.circle(x + r * 0.45, y + r * 0.22, r * 0.86, fill=1, stroke=0); c.restoreState()

def lantern_icon(c, x, y, h, col=PLUM, light=GOLD):
    """A hand lantern, base centre at (x, y)."""
    c.saveState(); c.setFillColor(col)
    c.rect(x - h * 0.22, y, h * 0.44, h * 0.62, fill=1, stroke=0)
    c.setFillColor(light); c.rect(x - h * 0.14, y + h * 0.08, h * 0.28, h * 0.46, fill=1, stroke=0)
    c.setFillColor(col)
    p = c.beginPath(); p.moveTo(x - h * 0.3, y + h * 0.62); p.lineTo(x, y + h * 0.84); p.lineTo(x + h * 0.3, y + h * 0.62)
    p.close(); c.drawPath(p, fill=1, stroke=0)
    c.setStrokeColor(col); c.setLineWidth(max(0.6, h * 0.05)); c.arc(x - h * 0.12, y + h * 0.8, x + h * 0.12, y + h * 1.02, 0, 180)
    c.restoreState()

def candle_icon(c, x, y, h, col):
    c.saveState(); c.setFillColor(col); c.setStrokeColor(PLUM); c.setLineWidth(max(0.4, h * 0.04))
    c.rect(x - h * 0.13, y, h * 0.26, h * 0.68, fill=1, stroke=1)
    c.setFillColor(GOLD)
    p = c.beginPath(); p.moveTo(x, y + h); p.curveTo(x + h * 0.12, y + h * 0.86, x + h * 0.08, y + h * 0.74, x, y + h * 0.74)
    p.curveTo(x - h * 0.08, y + h * 0.74, x - h * 0.12, y + h * 0.86, x, y + h); c.drawPath(p, fill=1, stroke=0)
    c.restoreState()

def glass_icon(c, x, y, h, col=HexColor("#4E7A52")):
    c.saveState(); c.setFillColor(col)
    p = c.beginPath(); p.moveTo(x - h * 0.3, y + h); p.lineTo(x + h * 0.3, y + h); p.lineTo(x + h * 0.06, y + h * 0.45)
    p.lineTo(x - h * 0.06, y + h * 0.45); p.close(); c.drawPath(p, fill=1, stroke=0)
    c.rect(x - h * 0.03, y + h * 0.1, h * 0.06, h * 0.36, fill=1, stroke=0)
    c.ellipse(x - h * 0.22, y + h * 0.04, x + h * 0.22, y + h * 0.14, fill=1, stroke=0); c.restoreState()

def bell_icon(c, x, y, h, col=PLUM):
    c.saveState(); c.setFillColor(col)
    p = c.beginPath(); p.moveTo(x - h * 0.45, y + h * 0.15); p.curveTo(x - h * 0.35, y + h * 0.3, x - h * 0.35, y + h * 0.9, x, y + h * 0.95)
    p.curveTo(x + h * 0.35, y + h * 0.9, x + h * 0.35, y + h * 0.3, x + h * 0.45, y + h * 0.15); p.close()
    c.drawPath(p, fill=1, stroke=0); c.circle(x, y + h * 0.08, h * 0.09, fill=1, stroke=0); c.restoreState()

def hat_icon(c, x, y, h, col=PLUM, band=GOLD):
    c.saveState(); c.setFillColor(col)
    c.ellipse(x - h * 0.55, y - h * 0.08, x + h * 0.55, y + h * 0.08, fill=1, stroke=0)
    p = c.beginPath(); p.moveTo(x - h * 0.28, y)
    p.curveTo(x - h * 0.18, y + h * 0.45, x - h * 0.05, y + h * 0.8, x + h * 0.22, y + h)
    p.curveTo(x + h * 0.08, y + h * 0.7, x + h * 0.2, y + h * 0.35, x + h * 0.28, y); p.close()
    c.drawPath(p, fill=1, stroke=0)
    c.setFillColor(band); c.rect(x - h * 0.27, y + h * 0.02, h * 0.54, h * 0.08, fill=1, stroke=0); c.restoreState()

def star(c, x, y, r, col=GOLD):
    c.saveState(); c.setFillColor(col); p = c.beginPath()
    for k in range(8):
        a = math.pi / 2 + math.pi * k / 4; rr = r if k % 2 == 0 else r * 0.32
        (p.moveTo if k == 0 else p.lineTo)(x + math.cos(a) * rr, y + math.sin(a) * rr)
    p.close(); c.drawPath(p, fill=1, stroke=0); c.restoreState()

def ornament(c, x, y, w, col=GOLD):
    c.saveState(); c.setStrokeColor(col); c.setLineWidth(0.8)
    c.line(x - w / 2, y, x - 10, y); c.line(x + 10, y, x + w / 2, y); star(c, x, y, 5, col); c.restoreState()

# ---------------------------------------------------------------- the document
class Doc:
    def __init__(self, fmt, path, kind):
        self.L = L(fmt); self.kind = kind; self.path = path
        self.c = canvas.Canvas(path, pagesize=(self.L.W, self.L.H))
        self.c.setTitle(f"{C.TITLE} — {kind}"); self.c.setAuthor(C.BRAND)
        self.page = 0; self.marks = {}
        self.y = None

    def new_page(self, mark=None, chrome=True, title=None):
        if self.page:
            self.c.showPage()
        self.page += 1
        if mark:
            self.marks.setdefault(mark, self.page)
            self.c.bookmarkPage(mark); self.c.addOutlineEntry(title or mark, mark, 0)
        if chrome:
            self.chrome()
        self.y = self.L.top
        return self.c

    def chrome(self):
        c, Lx = self.c, self.L
        c.setFillColor(WHITE); c.rect(0, 0, Lx.W, Lx.H, fill=1, stroke=0)
        c.setStrokeColor(RULE); c.setLineWidth(0.6)
        c.line(Lx.m, Lx.H - Lx.m + 6, Lx.W - Lx.m, Lx.H - Lx.m + 6)
        c.setFont("Fraunces-Italic", 8.5); c.setFillColor(SOFT)
        c.drawString(Lx.m, Lx.H - Lx.m + 12, C.TITLE)
        c.setFont("Nunito-ExtraBold", 7.5); c.setFillColor(AMETHYST)
        c.drawRightString(Lx.W - Lx.m, Lx.H - Lx.m + 12, self.kind.upper())
        c.setFont("Nunito", 8); c.setFillColor(SOFT)
        c.drawCentredString(Lx.W / 2, Lx.m - 22, str(self.page))
        crescent(c, Lx.W - Lx.m - 4, Lx.m - 19, 4, GOLD, WHITE)

    def h1(self, text, kicker=None):
        Lx = self.L
        if kicker:
            self.y = para(self.c, esc(kicker.upper()), Lx.m, self.y, Lx.cw, Lx.kicker)
        self.y = para(self.c, esc(text), Lx.m, self.y, Lx.cw, Lx.h1)
        ornament(self.c, Lx.m + 60, self.y + 2, 120); self.y -= 12

    def h2(self, text):
        self.need(40); self.y = para(self.c, esc(text), self.L.m, self.y, self.L.cw, self.L.h2)

    def p(self, text, style=None, raw=False, x=None, w=None):
        st = style or self.L.body
        w = w or self.L.cw; x = x if x is not None else self.L.m
        self.need(para_h(text if raw else esc(text), w, st))
        self.y = para(self.c, text if raw else esc(text), x, self.y, w, st)

    def bullets(self, items, style=None, sym="•"):
        st = style or self.L.body
        for it in items:
            t = it if isinstance(it, str) else it
            h = para_h(esc(t), self.L.cw - 16, st)
            self.need(h)
            self.c.setFillColor(AMETHYST); self.c.setFont("Nunito-ExtraBold", st.fontSize)
            self.c.drawString(self.L.m + 2, self.y - st.fontSize + 1, sym)
            self.y = para(self.c, esc(t), self.L.m + 16, self.y, self.L.cw - 16, st)

    def need(self, h):
        if self.y - h < self.L.bottom:
            self.new_page()

    def panel(self, lines, title=None, fill=PALE, style=None, edge=GOLD):
        """A parchment box with optional title; lines are paragraphs (raw markup allowed)."""
        Lx = self.L; st = style or Lx.body; pad = 12; w = Lx.cw - 2 * pad
        hs = [para_h(t, w, st) for t in lines]
        th = para_h(esc(title), w, Lx.h3) if title else 0
        h = sum(hs) + th + 2 * pad - 4
        self.need(h + 8)
        c = self.c; top = self.y
        c.setFillColor(fill); c.setStrokeColor(edge); c.setLineWidth(0.8)
        c.roundRect(Lx.m, top - h, Lx.cw, h, 7, fill=1, stroke=1)
        y = top - pad
        if title:
            y = para(c, esc(title), Lx.m + pad, y, w, Lx.h3)
        for t in lines:
            y = para(c, t, Lx.m + pad, y, w, st)
        self.y = top - h - 10

    def save(self):
        self.c.save()

# ---------------------------------------------------------------- shared pages
def cover(d, label):
    c, Lx = d.c, d.L
    d.new_page("Cover", chrome=False, title="Cover")
    c.drawImage(os.path.join(ART, f"cover_{Lx.fmt}.jpg"), 0, 0, Lx.W, Lx.H)
    c.setFillColor(GOLD); c.roundRect(Lx.W / 2 - 90, Lx.H - 92, 180, 26, 13, fill=1, stroke=0)
    c.setFillColor(PLUM); c.setFont("Nunito-ExtraBold", 12); c.drawCentredString(Lx.W / 2, Lx.H - 83, label.upper())
    t = c.beginText(); t.setTextRenderMode(3); t.setFont("Nunito", 12)
    for i, line in enumerate([C.TITLE, C.SUBTITLE, f"{C.PLAYERS} · {C.PLAYTIME} · host can play", label]):
        t.setTextOrigin(40, Lx.H - 60 - i * 16); t.textLine(line)
    c.drawText(t)

def plan_page(d, mark="Plan of Larkwell Hall"):
    """The plan of the house: ground floor and the upper floor, every door and stair marked."""
    c, Lx = d.c, d.L
    d.new_page(mark, title=mark)
    d.h1("The plan of Larkwell Hall", "Put this on the table with the evidence cards")
    cell = (Lx.cw - 30) / 3; x0 = Lx.m + 15; top = d.y - 18
    gh = min(cell * 0.78, (top - Lx.bottom - 44 - 46) / 6)
    def room_xy(r, floor="ground", ytop=top):
        rr, cc = C.ROOMS[r][1]
        return x0 + cc * cell, ytop - (rr + 1) * gh
    c.setFont("Nunito-ExtraBold", 9); c.setFillColor(AMETHYST)
    c.drawString(x0, top + 6, "GROUND FLOOR  (north at the top)")
    for r, (floor, _) in C.ROOMS.items():
        if floor != "ground":
            continue
        x, y = room_xy(r)
        c.setFillColor(HexColor("#EEF2E8") if r in C.OUTDOORS else PALE); c.setStrokeColor(PLUM); c.setLineWidth(1.4)
        if r in C.OUTDOORS:
            c.setDash(4, 3)
        c.rect(x, y, cell, gh, fill=1, stroke=1); c.setDash()
        c.setFillColor(PLUM); c.setFont("Fraunces-SemiBold", 11.5); c.drawCentredString(x + cell / 2, y + gh / 2 + 2, r)
        if r == "Herb Garden":
            c.setFont("Nunito-Italic", 7.5); c.setFillColor(SOFT)
            c.drawCentredString(x + cell / 2, y + gh / 2 - 11, "walled, open to the sky")
            c.drawCentredString(x + cell / 2, y + gh / 2 - 20, "chamomile path; foxglove bed")
            c.drawCentredString(x + cell / 2, y + gh / 2 - 29, "by the Library window")
    # doors on the ground floor (gaps with a small label)
    def door(a, b, label=None):
        (ra, ca), (rb, cb) = C.ROOMS[a][1], C.ROOMS[b][1]
        xa, ya = room_xy(a); xb, yb = room_xy(b)
        if ra == rb:                      # side by side: door on the shared vertical wall
            x = x0 + max(ca, cb) * cell; y = ya + gh / 2
            c.setStrokeColor(WHITE); c.setLineWidth(3.2); c.line(x, y - 10, x, y + 10)
            c.setStrokeColor(GOLD); c.setLineWidth(1.6); c.line(x - 4, y - 10, x + 4, y - 10); c.line(x - 4, y + 10, x + 4, y + 10)
        else:                             # one above the other: door on the shared horizontal wall
            y = top - (max(ra, rb)) * gh; x = x0 + ca * cell + cell / 2 + (14 if label == "hatch" else 0)
            c.setStrokeColor(WHITE); c.setLineWidth(3.2); c.line(x - 10, y, x + 10, y)
            c.setStrokeColor(GOLD); c.setLineWidth(1.6); c.line(x - 10, y - 4, x - 10, y + 4); c.line(x + 10, y - 4, x + 10, y + 4)
    labels = []
    for a, b, kind in C.DOORS:
        if C.ROOMS[a][0] == "ground" and C.ROOMS[b][0] == "ground":
            door(a, b)
    # stairs
    def stair(r, text, dx=0.0):
        x, y = room_xy(r)
        c.setFillColor(AUB); c.setFont("Nunito-Bold", 7.5)
        for k in range(4):
            c.rect(x + cell * (0.7 + dx) + k * 5, y + 8, 4, 6 + k * 3, fill=1, stroke=0)
        c.drawString(x + cell * (0.7 + dx) - 2, y + 30, text)
    stair("Still Room", "stair up", -0.05); stair("Great Hall", "stair up"); stair("Porch", "tower stair", -0.08)
    # upper floor
    utop = top - 3 * gh - 44
    c.setFont("Nunito-ExtraBold", 9); c.setFillColor(AMETHYST)
    c.drawString(x0, utop + 6, "UPPER FLOOR  (above the rooms below it)")
    for r, (floor, (rr, cc)) in C.ROOMS.items():
        if floor != "upper":
            continue
        x = x0 + cc * cell; y = utop - (rr + 1) * gh
        c.setFillColor(LILAC); c.setStrokeColor(PLUM); c.setLineWidth(1.4); c.rect(x, y, cell, gh, fill=1, stroke=1)
        c.setFillColor(PLUM); c.setFont("Fraunces-SemiBold", 11.5); c.drawCentredString(x + cell / 2, y + gh / 2 + 6, r)
        under = {"Lantern Room": "above the Still Room", "Gallery": "above the Great Hall, a balcony looking down into it",
                 "Bell Tower": "above the Porch; tower door opens onto the landing"}[r]
        c.setFont("Nunito-Italic", 7.3); c.setFillColor(SOFT)
        for i, ln in enumerate(_wrap(under, 34)):
            c.drawCentredString(x + cell / 2, y + gh / 2 - 8 - i * 9, ln)
    # the upper landing between the Gallery and the Bell Tower
    gx = x0 + 1 * cell; gy = utop - 2 * gh
    c.setFillColor(GOLD); c.rect(gx + cell * 0.3, gy - 6, cell * 0.4, 12, fill=1, stroke=0)
    c.setFillColor(PLUM); c.setFont("Nunito-Bold", 7.5); c.drawCentredString(gx + cell / 2, gy - 3, "upper landing")
    c.setFont("Nunito-Italic", 7.3); c.setFillColor(SOFT)
    c.drawString(x0 + 2 * cell + 6, utop - 1.5 * gh + 2, "The Lantern Room has no other door:")
    c.drawString(x0 + 2 * cell + 6, utop - 1.5 * gh - 8, "only the stair down to the Still Room.")
    c.drawString(x0 + 2 * cell + 6, utop - 2.5 * gh + 6, "From the Gallery you can see the")
    c.drawString(x0 + 2 * cell + 6, utop - 2.5 * gh - 4, "tower door across the landing.")
    # key
    ky = utop - 3 * gh - 20
    c.setStrokeColor(GOLD); c.setLineWidth(1.6); c.line(x0, ky, x0 + 16, ky)
    c.setFillColor(INK); c.setFont("Nunito", 8.5)
    c.drawString(x0 + 22, ky - 3, "door   ·   dashed: outdoors   ·   The Kitchen has a serving hatch into the Great Hall "
                                  "and a window onto the herb garden.")
    c.drawString(x0 + 22, ky - 15, "The Library’s French window and the Great Hall’s north door open onto the herb garden; "
                                   "the Still Room has its own garden door.")

def _wrap(text, n):
    out, cur = [], ""
    for w in text.split():
        if len(cur) + len(w) + 1 > n:
            out.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    return out + [cur]

def house_rules_page(d):
    d.new_page("House rules", title="House rules")
    d.h1("House rules", "Read these aloud before Round 1")
    for i, r in enumerate(C.HOUSE_RULES, 1):
        d.p(f"<font name='Nunito-ExtraBold' color='#8E5BB5'>{i}.</font> {esc(r)}", d.L.big, raw=True)
    d.y -= 6
    d.panel([esc("Each round: the host reads a short scene and puts new evidence cards on the table. Everyone reads "
                 "the page of their booklet for that round, then mingle: ask questions, compare stories, study the "
                 "cards and the plan. After Round 3, everyone writes an accusation.")], "How a round works")

# ---------------------------------------------------------------- host guide
def build_host(fmt, path, kit_marks):
    d = Doc(fmt, path, "Host Guide"); Lx = d.L
    cover(d, "Host guide")
    d.new_page("Welcome", title="Welcome, host")
    d.h1("Welcome to the Lantern Supper", "Host guide · no spoilers until the sealed section at the end")
    for t in C.HOST_INTRO:
        d.p(t, Lx.big)
    d.panel([esc(f"{C.PLAYERS} (6 core roles + up to 6 extra) · {C.PLAYTIME} · 3 rounds · teens and adults · "
                 "no acting required · the host can play"),
             esc("The host guide has no spoilers until the sealed section on the last pages. If you want to play, "
                 "print those pages separately, seal them in an envelope and don’t read them until the end.")],
            "At a glance")
    d.h2("What’s in the kit")
    d.bullets(["Host guide (this file): how to run the party, casting for 6–12 guests, scripts for every round, the "
               "plan of the house and the sealed solution.",
               "Player kit: 12 character booklets (4 pages each), 11 evidence cards, house rules, the plan of the house, "
               "detective’s notes, accusation sheets, name badges, a potion menu and 4 awards.",
               "Invitations: a fillable invitation, 12 character invitations (fillable) and phone versions to text."])
    # how it works
    d.new_page("How the game works", title="How the game works")
    d.h1("How the game works")
    steps = [("Before the party", "Choose the roles for your guest count, send invitations and character invitations, "
              "print the kit."),
             ("Prologue", "The host reads the opening. Guests read the first page of their booklet: who they are."),
             ("Round 1", "Evidence cards 1–4. Everyone says who they are and where they were."),
             ("Round 2", "Evidence cards 5–8. Secrets start to come out."),
             ("Round 3", "Evidence cards 9–11. The last pieces fall into place."),
             ("Accusation and reveal", "Everyone writes an accusation. The host opens the sealed solution and reads "
              "it aloud. Hand out the awards.")]
    for i, (t, x) in enumerate(steps):
        h = para_h(esc(x), Lx.cw - 70, Lx.body) + 22
        d.need(h)
        c = d.c; c.setFillColor(PLUM if i % 2 == 0 else AUB); c.circle(Lx.m + 16, d.y - 14, 15, fill=1, stroke=0)
        c.setFillColor(GOLD); c.setFont("Fraunces-SemiBold", 13); c.drawCentredString(Lx.m + 16, d.y - 18.5, str(i))
        d.y = para(c, esc(t), Lx.m + 44, d.y, Lx.cw - 50, Lx.h3)
        d.y = para(c, esc(x), Lx.m + 44, d.y, Lx.cw - 50, Lx.body) - 6
    d.h2("Everyone is a suspect, even the killer doesn’t know")
    d.p("No booklet says who did it. Each booklet is a character’s memory of the evening: what they will tell, and "
        "what they would rather keep quiet until their booklet says to share it. The evidence cards are true. "
        "Nobody lies about where someone else was. Put those together and exactly one guest could have poisoned "
        "Rowena’s glass. That is why the host can play too.")
    d.h2("House rules for the table")
    for i, r in enumerate(C.HOUSE_RULES, 1):
        d.p(f"<font name='Nunito-ExtraBold' color='#8E5BB5'>{i}.</font> {esc(r)}", raw=True)
    # before the party
    d.new_page("Before the party", title="Before the party")
    d.h1("Before the party")
    plan = [("Two to three weeks before", ["Decide how many guests you will have (6–12) and choose roles from the casting "
                                           "table.", "Send the invitation, then each guest their character invitation: "
                                           "who they play and what to wear. Everyone can play any role; change first "
                                           "names to suit your guests."]),
            ("One week before", ["Print the player kit: one booklet per guest (only the roles you are using), the "
                                 "evidence cards, the plan of the house, name badges, detective’s notes and accusation "
                                 "sheets (one each), the potion menu and the awards.",
                                 "Put each booklet in an envelope with the guest’s name. Put the evidence cards in "
                                 "three envelopes: Round 1 (cards 1–4), Round 2 (5–8), Round 3 (9–11).",
                                 "If you are playing too: print the sealed solution pages separately and seal them "
                                 "without reading."]),
            ("On the day", ["Lanterns, candles (battery ones are safest), a few pumpkins, something purple.",
                            "Make one or two potions from the menu, with and without alcohol.",
                            "Keep a bell, a glass and a spoon, or a pan handy to start each round."])]
    for head, items in plan:
        d.h2(head); d.bullets(items)
    d.h2("What to print from the player kit")
    rows = [("House rules and the plan of the house", "1 copy each, for the table"),
            ("Character booklets", "1 per guest, 4 pages each"), ("Evidence cards", "1 set (6 pages, cut in half)"),
            ("Detective’s notes and accusation sheet", "1 each per guest"), ("Name badges", "the roles you use"),
            ("Potion menu and awards", "1 each")]
    for a, b in rows:
        page = kit_marks.get(a.split(" and ")[0] if a.startswith("Detective") else a, None)
        d.p(f"<b>{esc(a)}</b>: {esc(b)}", raw=True)
    # casting
    d.new_page("Casting", title="Casting for 6–12 guests")
    d.h1("Casting", "Choose roles for your guest count")
    d.p("The six core roles are needed in every game. Each extra guest adds one extra role, in this order. The extra "
        "roles bring witnesses, secrets and fun, but the case can always be solved without them.")
    c = d.c; tw = Lx.cw; colw = [70] + [(tw - 70) / 12] * 12
    keys = C.CORE + C.ADD_ORDER
    y = d.y - 4; rh = 17
    c.setFillColor(PLUM); c.rect(Lx.m, y - rh, tw, rh, fill=1, stroke=0)
    c.setFillColor(WHITE); c.setFont("Nunito-ExtraBold", 7.4)
    c.drawString(Lx.m + 4, y - 12, "GUESTS")
    for j, k in enumerate(keys):
        x = Lx.m + 70 + j * colw[1]
        c.drawCentredString(x + colw[1] / 2, y - 12, C.name(k).split()[0 if k != "meridew" else 0][:9])
    y -= rh
    for n in range(6, 13):
        roles = set(C.CORE + C.ADD_ORDER[:n - 6])
        c.setFillColor(PALE if n % 2 else WHITE); c.rect(Lx.m, y - rh, tw, rh, fill=1, stroke=0)
        c.setFillColor(INK); c.setFont("Nunito-Bold", 9); c.drawString(Lx.m + 6, y - 12, f"{n} guests")
        for j, k in enumerate(keys):
            if k in roles:
                x = Lx.m + 70 + j * colw[1] + colw[1] / 2
                c.setFillColor(PLUM if k in C.CORE else AMETHYST); c.circle(x, y - rh / 2, 4.2, fill=1, stroke=0)
        y -= rh
    d.y = y - 16
    d.h2("The roles")
    for k in keys:
        nm, role, core, costume, colour, hook = C.PEOPLE[k]
        d.p(f"<b>{esc(nm)}</b> <font color='#8E5BB5'>· {'core' if core else 'extra'}</font> — {esc(role)}. "
            f"{esc(hook)} <i>Costume: {esc(costume)}.</i>", Lx.small, raw=True)
    d.panel([esc("If the host plays: take any role, core or extra. You know nothing more than your booklet, so you "
                 "can play to win. Keep the sealed solution sealed until everyone has made an accusation."),
             esc("If a guest can’t come: drop the last extra role from the list. If a core guest can’t come, the "
                 "host reads that booklet aloud at the start of each round (the host can also play a role)."),
             esc("Bigger group? Pair guests up: two guests share one booklet and play the role as a team.")],
            "Hosting tips")
    # the evening
    d.new_page("The evening", title="The evening")
    d.h1("The evening", "A suggested timetable for a 2½-hour party")
    sched = [("0:00", "Guests arrive. Potions, name badges, booklets in envelopes. Everyone reads page 1 of their booklet."),
             ("0:15", "Prologue: the host reads the opening (Round scripts)."),
             ("0:20", "Round 1 (about 35 minutes)."), ("0:55", "Supper or snack break, optional."),
             ("1:15", "Round 2 (about 35 minutes)."), ("1:50", "Round 3 (about 25 minutes)."),
             ("2:15", "Accusations: everyone fills in a sheet."), ("2:25", "The reveal, then the awards.")]
    for t, x in sched:
        d.p(f"<font name='Nunito-ExtraBold' color='#4A2C5E'>{t}</font>&nbsp;&nbsp;{esc(x)}", raw=True)
    d.h2("Setting the scene")
    d.bullets(["Lanterns and candles everywhere (battery candles near costumes and paper).",
               "A green glass on a side table with a card: “Rowena’s cordial — do not drink”.",
               "Folk fiddle music, low; a bell to start each round.",
               "Dried herbs, a bowl of apples, a few pumpkins, a purple cloth on the table.",
               "Food: a pot of soup, crusty bread, cheese, gingerbread, toffee apples."])
    d.h2("Potions")
    d.p("The potion menu in the player kit has four drinks, each with a “spellbound” (with alcohol) and a "
        "“moonless” (alcohol-free) version. " + C.POTION_NOTE)
    plan_page(d)
    # round scripts
    d.new_page("Round scripts", title="Round scripts")
    d.h1("Prologue", "Read aloud when everyone has a drink")
    for t in C.HOST_INTRO:
        d.p(f"“{t}”", Lx.say)
    d.p("Then read the house rules aloud, and ask everyone to read the first page of their booklet (“Your character”).")
    for r in (1, 2, 3):
        d.h2(f"Round {r}")
        for t in C.ROUND_SCRIPTS[r]:
            if t.startswith("Read aloud"):
                head, quote = t.split(":", 1)
                d.p(f"<b>{esc(head)}:</b>", raw=True)
                d.p(quote.strip(), Lx.say)
            else:
                d.bullets([t])
    d.h2("The accusation")
    d.bullets(["Give everyone an accusation sheet. Ten minutes, no talking.",
               "Each guest writes who poisoned Rowena, how they got to the glass, and which evidence proves it.",
               "Collect the sheets. Then open the sealed solution and read it aloud, slowly. Pause at the name."])
    d.h2("The awards")
    d.bullets([f"{a}: {b}." for a, b in C.AWARDS] + ["Best Detective goes to whoever named the killer with the best "
                                                      "reasons. Vote on the rest."])
    d.new_page("FAQ", title="Questions")
    d.h1("Questions hosts ask")
    faq = [("Can I play and host?", "Yes. Nobody’s booklet, including yours, says who did it. Just don’t read the sealed "
            "pages."),
           ("Do guests have to act?", "No. Everything a guest needs to say is in their booklet, in plain words. Hamming it "
            "up is welcome, never required."),
           ("What if someone reads ahead?", "Each round is on its own page. Ask guests to fold their booklet so only the "
            "current page shows."),
           ("What if the guests are stuck?", "Point them at the plan and at card 1: who could have been in the Still Room "
            "while Rowena was upstairs? Then ask who can vouch for whom."),
           ("Is it scary?", "Spooky, not gory: candlelight, a bell, a poisoned cordial. No blood, no weapons. Fine for "
            "teens and adults."),
           ("Do I need to print in colour?", "No. The pages are light to save ink; colour looks nicer on the cards and "
            "badges.")]
    for q, a in faq:
        d.p(f"<b>{esc(q)}</b> {esc(a)}", raw=True)
    # ---- the sealed section
    c = d.new_page("SEALED SOLUTION", chrome=False, title="SEALED SOLUTION")
    c.setFillColor(PLUM); c.rect(0, 0, Lx.W, Lx.H, fill=1, stroke=0)
    c.setFillColor(GOLD); c.setFont("Fraunces-Bold", 40); c.drawCentredString(Lx.W / 2, Lx.H * 0.62, "SEALED SOLUTION")
    c.setFillColor(PARCH); c.setFont("Nunito-ExtraBold", 18); c.drawCentredString(Lx.W / 2, Lx.H * 0.55, "STOP. HOST ONLY. READ AT THE END.")
    c.setFont("Nunito", 11.5)
    for i, ln in enumerate(["Everything after this page gives away the answer.",
                            "If you are playing too, print the remaining pages separately,",
                            "fold them, seal them in an envelope and open it after the accusations."]):
        c.drawCentredString(Lx.W / 2, Lx.H * 0.48 - i * 17, ln)
    for k in range(5):
        lantern_icon(c, Lx.W / 2 + (k - 2) * 50, Lx.H * 0.3, 30, GOLD, PARCH)
    d.new_page("Solution", title="The solution")
    d.h1(C.SOLUTION_INTRO, "The solution · read aloud")
    for head, text in C.SOLUTION:
        d.h2(head); d.p(text, Lx.big)
    d.h2("How the evidence points to her")
    for head, text in C.DEDUCTION:
        d.p(f"<b>{esc(head)}.</b> {esc(text)}", raw=True)
    d.h2("The red herrings")
    for head, text in C.RED_HERRINGS:
        d.p(f"<b>{esc(head)}.</b> {esc(text)}", raw=True)
    d.panel([esc(C.EPILOGUE)], "The end (read aloud)", fill=LILAC, style=Lx.big)
    timeline_table(d)
    d.save()
    return d

def timeline_table(d):
    Lx = d.L; c = d.c
    d.need(330)
    d.h2("Character, time and place: where everyone really was")
    names = [("rowena", "Rowena (victim)")] + [(k, C.name(k)) for k in C.CORE + C.ADD_ORDER]
    colw0 = 120; colw = (Lx.cw - colw0) / len(C.SLOTS); rh = 15
    y = d.y
    c.setFillColor(PLUM); c.rect(Lx.m, y - rh, Lx.cw, rh, fill=1, stroke=0)
    c.setFillColor(WHITE); c.setFont("Nunito-ExtraBold", 8)
    c.drawString(Lx.m + 4, y - 11, "WHO")
    for j, t in enumerate(C.SLOTS):
        c.drawCentredString(Lx.m + colw0 + j * colw + colw / 2, y - 11, t)
    y -= rh
    for i, (k, nm) in enumerate(names):
        c.setFillColor(PALE if i % 2 else WHITE); c.rect(Lx.m, y - rh, Lx.cw, rh, fill=1, stroke=0)
        c.setFillColor(INK); c.setFont("Nunito-Bold" if k == C.KILLER else "Nunito", 8.2)
        c.drawString(Lx.m + 4, y - 11, nm)
        for j, room in enumerate(C.TIMELINE[k]):
            hl = k == C.KILLER and C.SLOTS[j] == "22:15"
            if hl:
                c.setFillColor(GOLD); c.rect(Lx.m + colw0 + j * colw + 1, y - rh + 1, colw - 2, rh - 2, fill=1, stroke=0)
            c.setFillColor(INK); c.setFont("Nunito-Bold" if hl else "Nunito", 7.6)
            c.drawCentredString(Lx.m + colw0 + j * colw + colw / 2, y - 11, room)
        y -= rh
    d.y = y - 10
    d.p("Each column is the quarter hour starting at that time. Highlighted: the Still Room at a quarter past ten. "
        "Clementine said she was in the Cloakroom.", Lx.small)

# ---------------------------------------------------------------- player kit
def build_player(fmt, path):
    d = Doc(fmt, path, "Player Kit"); Lx = d.L
    cover(d, "Player kit")
    d.new_page("Printing guide", title="Printing guide")
    d.h1("Player kit", "What to print")
    d.p("Print only what your party needs. The host guide has the casting table: which roles to use for your number "
        "of guests.")
    d.bullets(["House rules and the plan of Larkwell Hall: one copy each, for the table.",
               "Character booklets: one per guest, only the roles you are using. Four pages each: Your character, "
               "Round 1, Round 2, Round 3. Fold or staple so only the current page shows.",
               "Evidence cards: one set, 11 cards, two to a page. Cut them in half and keep them in three envelopes "
               "by round.",
               "Detective’s notes and an accusation sheet: one each per guest.",
               "Name badges: the roles you are using. Potion menu and awards: one each."])
    house_rules_page(d)
    plan_page(d)
    for k in C.CORE + C.ADD_ORDER:
        booklet(d, k)
    evidence_cards(d)
    notes_page(d)
    accusation_page(d)
    badges(d)
    potion_menu(d)
    awards(d)
    d.save()
    return d

def booklet(d, k):
    Lx = d.L; c = d.c
    nm, role, core, costume, colour, hook = C.PEOPLE[k]; b = C.B[k]
    def head(sub, n):
        d.new_page(f"Booklet: {nm}" if n == 0 else None, title=f"Booklet: {nm}")
        c = d.c
        c.setFillColor(PLUM); c.roundRect(Lx.m, d.y - 46, Lx.cw, 46, 8, fill=1, stroke=0)
        c.setFillColor(GOLD); c.setFont("Fraunces-SemiBold", 20); c.drawString(Lx.m + 14, d.y - 30, nm)
        c.setFillColor(PARCH); c.setFont("Nunito-ExtraBold", 9)
        c.drawRightString(Lx.W - Lx.m - 14, d.y - 20, sub.upper())
        c.setFont("Nunito", 8.5); c.drawRightString(Lx.W - Lx.m - 14, d.y - 34,
                                                    "CORE ROLE" if core else "EXTRA ROLE")
        d.y -= 62
    head("Your character · read before Round 1", 0)
    d.p(f"<font color='#8E5BB5'><b>{esc(role)}</b></font>", Lx.big, raw=True)
    d.p(hook, Lx.say)
    for t in b["intro"]:
        d.p(t)
    y0 = d.y
    d.panel([esc(f"Costume: {costume}."), esc(f"Your lantern candle: {colour}.")], "Dress the part", fill=LILAC)
    candle_icon(c, Lx.W - Lx.m - 28, y0 - 46, 34, CANDLE[colour])
    d.panel([esc(b["secret"]), "<i>Keep this to yourself until your booklet tells you to share it.</i>"],
            "Your secret", fill=PALE)
    d.h2("Questions to ask tonight")
    d.bullets(b["ask"])
    for r in (1, 2, 3):
        head(f"Round {r} · read when the host says so", r)
        d.p(f"Round {r}", Lx.h1)
        for text, _ in b["rounds"][r - 1]:
            d.bullets([text], Lx.big, sym="◆")
        d.y -= 8
        if r == 1:
            d.panel([esc("Say who you are and where you were. Listen to everyone else. Look at evidence cards 1–4 and the "
                         "plan of the house.")], "This round", fill=PALE)
        elif r == 2:
            d.panel([esc("New evidence cards 5–8 are on the table. Some secrets come out now. Who can vouch for whom?")],
                    "This round", fill=PALE)
        else:
            d.panel([esc("Evidence cards 9–11. After this round, everyone writes an accusation. Who could have been "
                         "in the Still Room while Rowena was upstairs, and what proves it?")], "This round", fill=PALE)
        c = d.c
        c.setFont("Nunito-ExtraBold", 8.5); c.setFillColor(AMETHYST); c.drawString(Lx.m, d.y - 4, "MY NOTES")
        yy = d.y - 24
        c.setStrokeColor(RULE); c.setLineWidth(0.6)
        while yy > Lx.bottom + 8:
            c.line(Lx.m, yy, Lx.W - Lx.m, yy); yy -= 22

def evidence_cards(d):
    Lx = d.L
    for i, card in enumerate(C.CARDS):
        if i % 2 == 0:
            d.new_page("Evidence cards" if i == 0 else None, title="Evidence cards")
            c = d.c
            c.setStrokeColor(RULE); c.setDash(4, 4); c.setLineWidth(0.8)
            c.line(Lx.m - 20, Lx.H / 2, Lx.W - Lx.m + 20, Lx.H / 2); c.setDash()
            c.setFont("Nunito", 7); c.setFillColor(SOFT); c.drawCentredString(Lx.W / 2, Lx.H / 2 + 3, "cut here")
        c = d.c
        top = Lx.H - Lx.m - 14 if i % 2 == 0 else Lx.H / 2 - 18
        h = Lx.H / 2 - Lx.m - 30
        c.setFillColor(PALE); c.setStrokeColor(PLUM); c.setLineWidth(1.6)
        c.roundRect(Lx.m, top - h, Lx.cw, h, 10, fill=1, stroke=1)
        c.setStrokeColor(GOLD); c.setLineWidth(0.7); c.roundRect(Lx.m + 6, top - h + 6, Lx.cw - 12, h - 12, 7, fill=0, stroke=1)
        c.setFillColor(PLUM); c.roundRect(Lx.m + 16, top - 38, 150, 22, 11, fill=1, stroke=0)
        c.setFillColor(GOLD); c.setFont("Nunito-ExtraBold", 9.5)
        c.drawCentredString(Lx.m + 91, top - 31, f"ROUND {card['round']} · CARD {card['id']}")
        c.setFillColor(PLUM); c.setFont("Fraunces-SemiBold", 19); c.drawString(Lx.m + 180, top - 34, card["title"])
        y = top - 56; x = Lx.m + 22; w = Lx.cw - 44
        st = ParagraphStyle("card", parent=Lx.body, fontSize=12.5, leading=17.2, spaceAfter=7)
        for t in card["text"]:
            if t == "LEDGER":
                y = ledger(c, x, y, w)
                continue
            y = para(c, esc(t), x, y, w, st)
        icon = {"1": glass_icon, "9": glass_icon, "5": bell_icon}.get(card["id"])
        if icon:
            icon(c, Lx.W - Lx.m - 40, top - h + 18, 40)
        else:
            lantern_icon(c, Lx.W - Lx.m - 40, top - h + 18, 36)
        if y < top - h + 10:
            raise RuntimeError(f"[{Lx.fmt}] card {card['id']} overflows")

def ledger(c, x, y, w):
    """The lantern ledger: every guest and the colour of their candle, with a swatch."""
    keys = C.CORE + C.ADD_ORDER; colw = w / 2; rh = 17
    for i, k in enumerate(keys):
        col, row = i // 6, i % 6
        xx = x + col * colw; yy = y - row * rh
        candle_icon(c, xx + 6, yy - 14, 13, CANDLE[C.PEOPLE[k][4]])
        c.setFillColor(INK); c.setFont("Nunito-Bold", 10); c.drawString(xx + 18, yy - 11, C.name(k))
        c.setFont("Nunito", 10); c.drawString(xx + 150, yy - 11, C.PEOPLE[k][4])
    return y - 6 * rh - 8

def notes_page(d):
    Lx = d.L
    d.new_page("Detective’s notes", title="Detective’s notes")
    d.h1("Detective’s notes", "One per guest")
    c = d.c
    cols = ["Suspect", "Where at a quarter past ten?", "Who vouches for them?", "Candle", "Secret or motive"]
    widths = [0.2, 0.24, 0.22, 0.1, 0.24]
    y = d.y; rh = 44
    c.setFillColor(PLUM); c.rect(Lx.m, y - 20, Lx.cw, 20, fill=1, stroke=0)
    c.setFillColor(WHITE); c.setFont("Nunito-ExtraBold", 8)
    x = Lx.m
    for t, wf in zip(cols, widths):
        c.drawString(x + 5, y - 13, t); x += wf * Lx.cw
    y -= 20
    for i, k in enumerate(C.CORE):
        c.setFillColor(PALE if i % 2 else WHITE); c.setStrokeColor(RULE)
        c.rect(Lx.m, y - rh, Lx.cw, rh, fill=1, stroke=1)
        c.setFillColor(INK); c.setFont("Nunito-Bold", 9.5); c.drawString(Lx.m + 5, y - 16, C.name(k))
        x = Lx.m
        for wf in widths[:-1]:
            x += wf * Lx.cw; c.setStrokeColor(RULE); c.line(x, y, x, y - rh)
        y -= rh
    d.y = y - 14
    d.p("Extra guests (the choir, the cook, Mother Meridew and the lantern girl) are on evidence card 3.", Lx.small)
    d.h2("Notes")
    c = d.c
    yy = d.y
    while yy > Lx.bottom + 10:
        c.setStrokeColor(RULE); c.line(Lx.m, yy, Lx.W - Lx.m, yy); yy -= 20

def accusation_page(d):
    Lx = d.L
    d.new_page("Accusation sheet", title="Accusation sheet")
    c = d.c
    for half in (0, 1):
        top = Lx.H - Lx.m - 10 if half == 0 else Lx.H / 2 - 14
        h = Lx.H / 2 - Lx.m - 26
        c.setStrokeColor(PLUM); c.setLineWidth(1.4); c.setFillColor(WHITE); c.roundRect(Lx.m, top - h, Lx.cw, h, 9, fill=1, stroke=1)
        c.setFillColor(PLUM); c.setFont("Fraunces-SemiBold", 20); c.drawString(Lx.m + 16, top - 32, "My accusation")
        hat_icon(c, Lx.W - Lx.m - 36, top - 40, 26)
        qs = ["My name:", "Who poisoned Rowena?", "How did they get to the glass, and when?", "",
              "Which evidence proves it?", "", "Why did they do it?", ""]
        y = top - 58
        for q in qs:
            c.setFillColor(INK); c.setFont("Nunito-Bold", 10)
            if q:
                c.drawString(Lx.m + 16, y, q)
            c.setStrokeColor(RULE); c.line(Lx.m + 16 + (c.stringWidth(q, "Nunito-Bold", 10) + 8 if q else 0), y - 2,
                                           Lx.W - Lx.m - 16, y - 2)
            y -= 27
    c.setStrokeColor(RULE); c.setDash(4, 4); c.line(Lx.m - 20, Lx.H / 2, Lx.W - Lx.m + 20, Lx.H / 2); c.setDash()

def badges(d):
    Lx = d.L
    people = C.CORE + C.ADD_ORDER + ["host"]
    per = 8; bw = Lx.cw / 2 - 6; bh = (Lx.H - 2 * Lx.m - 40) / 4 - 8
    for i, k in enumerate(people):
        if i % per == 0:
            d.new_page("Name badges" if i == 0 else None, title="Name badges")
        c = d.c
        j = i % per; col, row = j % 2, j // 2
        x = Lx.m + col * (bw + 12); top = Lx.H - Lx.m - 20 - row * (bh + 8)
        c.setFillColor(WHITE); c.setStrokeColor(PLUM); c.setLineWidth(1.2); c.roundRect(x, top - bh, bw, bh, 8, fill=1, stroke=1)
        c.setFillColor(PLUM); c.roundRect(x, top - 26, bw, 26, 8, fill=1, stroke=0); c.rect(x, top - 26, bw, 10, fill=1, stroke=0)
        c.setFillColor(GOLD); c.setFont("Nunito-ExtraBold", 8.5); c.drawCentredString(x + bw / 2, top - 17, "THE LANTERN SUPPER · LARKWELL HALL")
        if k == "host":
            nm, role, colour = C.INSPECTOR, "Your host for the evening", "gold"
        else:
            nm, role, colour = C.name(k), C.PEOPLE[k][1], C.PEOPLE[k][4]
        size = 17
        while c.stringWidth(nm, "Fraunces-SemiBold", size) > bw - 60 and size > 11:
            size -= 1
        c.setFillColor(PLUM); c.setFont("Fraunces-SemiBold", size); c.drawString(x + 14, top - 26 - bh * 0.32, nm)
        st = ParagraphStyle("b", fontName="Nunito", fontSize=8.5, leading=11, textColor=SOFT)
        para(c, esc(role), x + 14, top - 26 - bh * 0.32 - 8, bw - 70, st)
        candle_icon(c, x + bw - 30, top - bh + 12, 34, CANDLE[colour])

def potion_menu(d):
    Lx = d.L
    d.new_page("Potion menu", title="Potion menu")
    c = d.c
    c.setFillColor(LILAC); c.roundRect(Lx.m, Lx.bottom, Lx.cw, Lx.top - Lx.bottom, 14, fill=1, stroke=0)
    d.y -= 20
    c.setFillColor(PLUM); c.setFont("Fraunces-Bold", 30); c.drawCentredString(Lx.W / 2, d.y - 30, "The Potion Menu")
    c.setFont("Nunito-ExtraBold", 10); c.setFillColor(AMETHYST)
    c.drawCentredString(Lx.W / 2, d.y - 50, "LARKWELL HALL · THE LANTERN SUPPER")
    ornament(c, Lx.W / 2, d.y - 64, 200); d.y -= 86
    for nm, desc, spell, moonless in C.POTIONS:
        c.setFillColor(PLUM); c.setFont("Fraunces-SemiBold", 18); c.drawCentredString(Lx.W / 2, d.y - 18, nm)
        st = ParagraphStyle("pm", fontName="Nunito", fontSize=10.5, leading=14, textColor=INK, alignment=1)
        y = para(c, esc(desc), Lx.m + 50, d.y - 26, Lx.cw - 100, st)
        st2 = ParagraphStyle("pm2", parent=st, fontName="Nunito-Italic", textColor=AUB)
        y = para(c, esc(spell + "   ·   " + moonless), Lx.m + 50, y, Lx.cw - 100, st2)
        ornament(c, Lx.W / 2, y - 4, 80, SAGE); d.y = y - 22
    st = ParagraphStyle("pn", fontName="Nunito", fontSize=8.5, leading=11.5, textColor=SOFT, alignment=1)
    para(c, esc(C.POTION_NOTE), Lx.m + 40, Lx.bottom + 46, Lx.cw - 80, st)

def awards(d):
    Lx = d.L
    for i, (a, why) in enumerate(C.AWARDS):
        if i % 2 == 0:
            d.new_page("Awards" if i == 0 else None, title="Awards")
            d.c.setStrokeColor(RULE); d.c.setDash(4, 4); d.c.line(Lx.m - 20, Lx.H / 2, Lx.W - Lx.m + 20, Lx.H / 2); d.c.setDash()
        c = d.c
        top = Lx.H - Lx.m - 10 if i % 2 == 0 else Lx.H / 2 - 14
        h = Lx.H / 2 - Lx.m - 26
        c.setFillColor(PARCH); c.setStrokeColor(GOLD); c.setLineWidth(2.4); c.roundRect(Lx.m, top - h, Lx.cw, h, 12, fill=1, stroke=1)
        c.setStrokeColor(PLUM); c.setLineWidth(0.8); c.roundRect(Lx.m + 8, top - h + 8, Lx.cw - 16, h - 16, 9, fill=0, stroke=1)
        c.setFillColor(AMETHYST); c.setFont("Nunito-ExtraBold", 10); c.drawCentredString(Lx.W / 2, top - 40, "THE HEARTH CIRCLE AWARDS")
        c.setFillColor(PLUM); c.setFont("Fraunces-Bold", 32); c.drawCentredString(Lx.W / 2, top - 82, a)
        c.setStrokeColor(RULE); c.line(Lx.m + 90, top - 150, Lx.W - Lx.m - 90, top - 150)
        c.setFont("Nunito", 9); c.setFillColor(SOFT); c.drawCentredString(Lx.W / 2, top - 164, "awarded to")
        c.line(Lx.m + 90, top - 200, Lx.W / 2 - 20, top - 200); c.line(Lx.W / 2 + 20, top - 200, Lx.W - Lx.m - 90, top - 200)
        c.drawCentredString(Lx.m + 90 + (Lx.W / 2 - 20 - Lx.m - 90) / 2, top - 214, "date")
        c.drawCentredString(Lx.W / 2 + 20 + (Lx.W - Lx.m - 90 - Lx.W / 2 - 20) / 2, top - 214, "signed by the Inspector")
        lantern_icon(c, Lx.m + 50, top - h + 24, 40); lantern_icon(c, Lx.W - Lx.m - 50, top - h + 24, 40)
    d.c.setStrokeColor(RULE); d.c.setDash(4, 4); d.c.line(Lx.m - 20, Lx.H / 2, Lx.W - Lx.m + 20, Lx.H / 2); d.c.setDash()
