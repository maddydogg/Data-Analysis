"""Ten 2000x2000 JPG listing images for the Storm & Moon Double Feature, styled as a vintage
double-feature night at an old cinema: 01 is the double-bill poster, 02-09 are lobby cards
(two-tone frame, caption panel, real pages of both cases inside), 10 is a "What you get" poster.
Every page shown is a real PDF region; every word drawn by code is recorded and scanned for
spoilers of both cases (killer names and tickets, Sealed Check numbers, finalists, level-2/3
hints, solution headings).

    python3 mockups.py   ->  ../mockups/
"""
import json, math, os, re, sys
from PIL import Image, ImageDraw, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "src"))
import bundle as B        # noqa: E402
import kit                # noqa: E402
import poster as P        # noqa: E402
kit.set_font_dir(B.FONTS)

S = 2000
OUT = os.path.join(HERE, "..", "mockups")
GOLD = B.MOON["accent"]; ORANGE = B.STORM["accent"]; CREAM = (0xF4, 0xEA, 0xD0); BLACK = (0x0B, 0x08, 0x0C)
CONTENT = (120, 236, 1880, 1566)

# ---------------------------------------------------------------- the cases' pages
NEEDLES = {
    "storm": dict(cover=None, howto=("How to play", "What you need"), rules=("House rules", "Ticket digits"),
                  map=("EVIDENCE 1", "Castle map", "CASTLE STOP"), directory=("Booth directory", "From the Monster Night programme"),
                  receipt=("The receipt", "HAPPY HALLOWEEN"), weather=("Weather log", "CORVENMOOR WEATHER STATION"),
                  coach=("Night bus timetable", "Corvenmoor Night Buses"), statements=("Witness statements", "WITNESS STATEMENT"),
                  notebook=("work these out from the documents",), hint1=("A gentle nudge", "Evidence A"),
                  check=("The Sealed Check", "Ticket number")),
    "moon": dict(cover=None, howto=("How to play", "What you need"), rules=("House rules", "Ticket digits"),
                 map=("EVIDENCE 1", "Fair map", "THE HOB STONES"), directory=("Stall directory", "From the Moon Fair programme"),
                 brews=("The Book of Brews", "WHAT GOES IN"), moon=("Moon-watcher", "THE MORROWMERE MOON-WATCH"),
                 reading=("reading book", "READINGS AT THE MOON FAIR"), ledger=("Shop ledger", "Morrowmere Village Carrier"),
                 notebook=("work these out from the documents",), hint1=("A gentle nudge", "Evidence A"),
                 check=("The Sealed Check", "Ticket number")),
}
DOC_KEYS = {"storm": ["map", "directory", "receipt", "weather", "coach", "statements"],
            "moon": ["map", "directory", "brews", "moon", "reading", "ledger"]}

class Case:
    def __init__(self, c, bad):
        self.c = c
        self.L = kit.Pdf(c["book"]["letter"]); self.I = kit.Pdf(c["book"]["ipad"]); self.A4 = kit.Pdf(c["book"]["a4"])
        self.p = {k: (0 if v is None else self.L.find(*v)) for k, v in NEEDLES[c["key"]].items()}
        self.ip = {"notebook": self.I.find("work these out from the documents")}
        stall = "LAST BOOTH" if c["key"] == "storm" else "LAST STALL"
        clean = [i for i, pg in enumerate(self.L.doc)
                 if "FIRST NAME" in pg.get_text() and stall in " ".join(pg.get_text().split())
                 and not any(tok in " ".join(pg.get_text().split()) for tok in bad.values())]
        self.log = next((i for i in clean if "18:" in self.L.doc[i].get_text()[:400]), clean[0])

    def page(self, key, h):
        return self.L.image(self.p[key], h)

def log_rows(pdf, index):
    lines = {}
    for w in pdf.words(index):
        lines.setdefault(round(w[3], 1), []).append(w)
    rows = []
    for y, ws in sorted(lines.items()):
        ws.sort(key=lambda w: w[0])
        if re.fullmatch(r"\d\d:\d\d", ws[0][4]) and len(ws) >= 7:
            stall = next((w[4] for w in reversed(ws) if w[4].isdigit() and len(w[4]) <= 2), "0")
            rows.append((min(w[1] for w in ws), max(w[3] for w in ws), ws[0][0], ws[-1][2], ws[0][4], int(stall)))
    return rows

def notebook_marks(pdf, index):
    marks = {}
    for w in pdf.words(index):
        m = re.fullmatch(r"(\d{1,2}|[A-F])\.", w[4])
        if m and w[0] < 110:
            marks[m.group(1)] = ((w[0] + w[2]) / 2, (w[1] + w[3]) / 2, w[3] - w[1])
    return marks

def tick_notebook(pdf, page, pidx, keys, col):
    marks = notebook_marks(pdf, pidx)
    fr = kit.Frame(page.img.width, page.img.height, (255, 255, 255)); fr.img = page.img
    margin = 48 if pdf.doc[pidx].rect.width == 768 else 54
    for k in keys:
        x, y, h = marks[k]
        px, py = page.px(margin + 0.5, y + 1)
        kit.tick(fr, px, py, 13 * page.zoom, col, max(3, int(1.9 * page.zoom)))

def strike_rows(page, rows, pred, col, seed=0):
    fr = kit.Frame(page.img.width, page.img.height, (255, 255, 255)); fr.img = page.img
    for i, (y0, y1, x0, x1, *_r) in enumerate(r for r in rows if pred(r)):
        a = page.px(x0 - 4, (y0 + y1) / 2); b = page.px(x1 + 4, (y0 + y1) / 2)
        kit.marker_strike(fr, a[0], a[1], b[0], (y1 - y0) * page.zoom * 1.3, col, 165, seed + i)

# stated-outright notebook clues only, so no hidden evidence is shown in use
STRIKE = {"storm": (lambda r: 19 <= r[5] <= 27, "Clue 11:\nnot Lantern Walk"),
          "moon": (lambda r: r[5] < 10 or 28 <= r[5] <= 36, "Clues 10 & 11:\ntwo digits, not\nRowan Close")}

# ---------------------------------------------------------------- shared look
def two_tone(img, box, alpha=1.0):
    x0, y0, x1, y1 = [int(v) for v in box]; mx = (x0 + x1) // 2
    P.gradient(img, B.STORM["dark"], B.STORM["mid"], (x0, y0, mx, y1)) if False else None
    left = Image.new("RGBA", (mx - x0, y1 - y0)); P.gradient(left, B.STORM["dark"], B.STORM["mid"])
    right = Image.new("RGBA", (x1 - mx, y1 - y0)); P.gradient(right, B.MOON["dark"], B.MOON["mid"])
    img.paste(left, (x0, y0)); img.paste(right, (mx, y0))
    P.halftone(img, (x0, y0, mx, y1), (0x9B, 0xC5, 0x3D, 26), 24, falloff=lambda x, y: 0.55)
    P.halftone(img, (mx, y0, x1, y1), (0x8E, 0x5B, 0xB5, 34), 24, falloff=lambda x, y: 0.55)

def seam(img, x, y0, y1, w=6):
    ImageDraw.Draw(img).rectangle([x - w / 2, y0, x + w / 2, y1], fill=GOLD)

def bulbs(f, y, n, x0=0, x1=S, r=10):
    for i in range(n):
        x = x0 + (i + 0.5) * (x1 - x0) / n
        P.glow(f.img, [x - r * 2.4, y - r * 2.4, x + r * 2.4, y + r * 2.4], (0xFF, 0xD2, 0x7A), 140, r)
        ImageDraw.Draw(f.img).ellipse([x - r, y - r, x + r, y + r], fill=(0xFF, 0xE6, 0xA8))

def lobby(no, caption, sub):
    f = kit.Frame(S, S, BLACK); img = f.img
    two_tone(img, (0, 0, S, S)); seam(img, S / 2, 0, S, 8)
    d = f.draw()
    d.rectangle([56, 56, S - 56, S - 56], fill=CREAM)
    d.rectangle([76, 76, S - 76, S - 76], outline=BLACK, width=6)
    d.rectangle([90, 90, S - 90, S - 90], outline=GOLD, width=3)
    P.tracked(f, S / 2, 124, "STORM & MOON  ·  DOUBLE FEATURE", P.hf("cinzel", 46, 800), BLACK, 9)
    f.text((150, 140), "QUIETCLUECO", P.hf("oswald", 30, 500), B.STORM["accent2"])
    f.text((S - 150, 140), f"LOBBY CARD No. {no}", P.hf("oswald", 30, 500), B.MOON["accent2"], anchor="ra")
    two_tone(img, CONTENT); seam(img, S / 2, CONTENT[1], CONTENT[3], 5)
    d = f.draw(); d.rectangle(CONTENT, outline=BLACK, width=4)
    d.rectangle([120, 1592, 1880, 1880], fill=BLACK)
    d.rectangle([132, 1604, 1868, 1868], outline=GOLD, width=3)
    cap = P.fit(caption, "abril", 118, 1640)
    f.text((S / 2, 1630), caption, cap, GOLD, anchor="ma")
    f.text((S / 2, 1790), sub, P.fit(sub, "oswald", 50, 1640, 500), CREAM, anchor="ma")
    return f

def note_card(f, text, cx, cy, angle, w=460, h=300, size=60):
    note = kit.Frame(w, h, (250, 232, 176))
    note.text((w / 2, h * 0.18), text, kit.font("hand", size), B.INK, anchor="ma", align="center")
    f.paste(note.img, cx, cy, angle=angle); f.sources += note.sources

def label(f, text, cx, y, col=CREAM, size=40):
    f.text((cx, y), text, P.hf("oswald", size, 600), col, anchor="ma")

def env_img(key, w=360, h=250):
    e = kit.Frame(w, h, (0, 0, 0)); e.img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    kit.envelope(e, (4, 4, w - 4, h - 4), key, P.hf("abril", int(h * 0.42)))
    return e

def cover_img(case, w):
    im = Image.open(case["cover_art"]["letter"]).convert("RGBA")
    return im.resize((int(w), int(w * im.height / im.width)), Image.LANCZOS)

def framed(im, border=14, col=(0xF2, 0xE8, 0xD0)):
    out = Image.new("RGBA", (im.width + 2 * border, im.height + 2 * border), col + (255,))
    out.paste(im, (border, border)); return out

def stub(f, cx, cy, text, bg, fg, w=330, h=104):
    P.stub(f, cx, cy, text, bg, fg, w=w, h=h)

# ---------------------------------------------------------------- the ten images
def m01_main(A):
    f = kit.Frame(S, S, BLACK); img = f.img
    two_tone(img, (0, 0, S, S)); seam(img, S / 2, 250, 1080, 8)
    d = f.draw(); d.rectangle([0, 0, S, 250], fill=BLACK)
    bulbs(f, 26, 30); bulbs(f, 224, 30)
    P.tracked(f, S / 2, 52, "QUIETCLUECO PRESENTS", P.hf("cinzel", 44, 700), CREAM, 12)
    P.tracked(f, S / 2, 100, "A DOUBLE FEATURE", P.hf("bebas", 116), (0xFF, 0xF1, 0xD2), 18)
    for c, cx, ang in ((B.CASES[0], 520, -2.5), (B.CASES[1], 1480, 2.5)):
        im = framed(cover_img(c, 560))
        f.paste(im, cx, 330 + im.height / 2, angle=ang, shadow=True, shadow_strength=170)
        stub(f, cx, 300, c["feature"], c["pal"]["accent"], c["pal"]["dark"], w=300, h=96)
    f.note("drawn", "cover art", B.CASES[0]["title"] + " " + B.CASES[1]["title"])
    y = 1100
    big = P.fit("STORM & MOON", "abril", 300, S - 160)
    P.title_word(f, "STORM & MOON", S / 2, y, big, fill=GOLD, shadow=(0x5A, 0x1E, 0x10), depth=20,
                 outline=BLACK, inline=CREAM, k=1.6)
    y += big.size * 1.1
    P.tracked(f, S / 2, y, "DOUBLE FEATURE", P.hf("cinzel", 104, 800), CREAM, 24)
    y += 150
    P.tracked(f, S / 2, y, "2 CASES  ·  12,000 SUSPECTS  ·  2 KILLERS", P.hf("oswald", 74, 600), CREAM, 6)
    y += 130
    stub(f, S / 2 - 260, y + 60, "PRINTABLE", ORANGE, B.STORM["dark"], w=420, h=124)
    stub(f, S / 2 + 260, y + 60, "iPad", GOLD, B.MOON["dark"], w=420, h=124)
    P.tracked(f, S / 2, S - 112, "NOW SHOWING  ·  TWO MURDER MYSTERY PUZZLES", P.hf("cinzel", 38, 700), GOLD, 7)
    P.deco_frame(f, 36, 1.5, GOLD)
    P.aged(img, 21, border=24)
    return f

def m02_two_cases(A):
    f = lobby(2, "Two cases, one ticket", "Monster Night at the castle  ·  The Moon Fair in a witch village")
    for c, cx, ang in ((B.CASES[0], 560, -2), (B.CASES[1], 1440, 2)):
        im = framed(cover_img(c, 600))
        f.paste(im, cx, 330 + im.height / 2 - 40, angle=ang, shadow=True, shadow_strength=170)
        stub(f, cx, 300, c["feature"], c["pal"]["accent"], c["pal"]["dark"], w=300, h=96)
    f.note("drawn", "cover art", B.CASES[0]["title"] + " " + B.CASES[1]["title"])
    label(f, "6,000 suspects · 18 clues · 1 killer", 560, 1440, CREAM, 42)
    label(f, "6,000 suspects · 18 clues · 1 killer", 1440, 1440, CREAM, 42)
    return f

def m03_documents(A):
    f = lobby(3, "12 case documents", "Six for each case: maps, logs, notes, timetables, recipes and ledgers")
    for side, (case, x0) in enumerate(((A.cs[0], 160), (A.cs[1], 1040))):
        keys = DOC_KEYS[case.c["key"]]
        for i, k in enumerate(keys):
            col, row = i % 3, i // 3
            cx = x0 + 135 + col * 270; cy = 560 + row * 600
            pg = case.page(k, 380)
            f.paste_page(pg, cx, cy, angle=[2, -1.5, 1.5, -2, 1, -1][i])
            label(f, case.c["docs"][i], cx, cy + 210, CREAM, 30)
    label(f, B.CASES[0]["title"], 560, 268, ORANGE, 40)
    label(f, B.CASES[1]["title"], 1440, 268, GOLD, 40)
    return f

def m04_logs(A):
    f = lobby(4, "12,000 suspects to cross out", "Two Visitor Logs, 6,000 lines each: rule visitors out clue by clue")
    for case, cx, ang in ((A.cs[0], 560, -1.5), (A.cs[1], 1440, 1.5)):
        rows = log_rows(case.L, case.log)[:46]
        clip = (40, rows[0][0] - 22, 572, rows[-1][1] + 2)
        pg = case.L.image(case.log, int((clip[3] - clip[1]) * 820 / (clip[2] - clip[0])), clip=clip)
        pred, note = STRIKE[case.c["key"]]
        strike_rows(pg, rows, pred, case.c["pal"]["accent2"] if case.c["key"] == "storm" else B.MOON["accent2"])
        f.paste_page(pg, cx, 900, angle=ang)
        note_card(f, note, cx + 210, 1380, -5 if cx < S / 2 else 5, w=430, h=290 if "\n" in note[:20] and note.count("\n") == 1 else 330, size=54)
    return f

def m05_hints(A):
    f = lobby(5, "Stuck? Three levels of help", "Level 1 shown here; levels 2 and 3 wait on their own pages")
    for case, cx, ang in ((A.cs[0], 560, -1.5), (A.cs[1], 1440, 1.5)):
        pidx = case.p["hint1"]
        ys = sorted(w[3] for w in case.L.words(pidx) if w[4] in ("Evidence", "F"))
        ends = [w[3] for w in case.L.words(pidx)]
        clip = (40, 70, 572, max(ends) + 8 if max(ends) < 720 else ys[-1] + 30)
        pg = case.L.image(pidx, int(830 * (clip[3] - clip[1]) / (clip[2] - clip[0])), clip=clip)
        if pg.img.height > 1060:
            pg = case.L.image(pidx, 1060, clip=clip)
        f.paste_page(pg, cx, 290 + pg.img.height / 2, angle=ang)
    for key, cx in (("2", 820), ("3", 1180)):
        e = env_img(key, 300, 210)
        f.paste(e.img, cx, 1440, angle=-4 if key == "2" else 4); f.sources += e.sources
    return f

def m06_check(A):
    f = lobby(6, "Check each answer, no spoilers", "The Sealed Check: a quick sum confirms your killer, no names printed")
    for case, cx, ang in ((A.cs[0], 560, -1.5), (A.cs[1], 1440, 1.5)):
        pidx = case.p["check"]
        r = case.L.doc[pidx].search_for("If your last three digits are")[0]
        clip = (40, 70, 572, r.y0 - 30)
        pg = case.L.image(pidx, int(840 * (clip[3] - clip[1]) / (clip[2] - clip[0])), clip=clip)
        f.paste_page(pg, cx, 400 + pg.img.height / 2, angle=ang)
    e = env_img("?", 440, 300)
    f.paste(e.img, S / 2, 1360, angle=3); f.sources += e.sources
    f.text((S / 2, 1110), "Digits match? Open that case’s Envelope.", P.hf("oswald", 54, 600), CREAM, anchor="ma")
    return f

def m07_devices(A):
    f = lobby(7, "Print it or play on iPad", "US Letter · A4 · iPad (Goodnotes, Notability) with tap-to-jump contents")
    pg = A.cs[0].page("notebook", 1180)
    tick_notebook(A.cs[0].L, pg, A.cs[0].p["notebook"], [str(i) for i in range(1, 8)], B.STORM["accent2"])
    f.paste_page(pg, 560, 900, angle=2)
    ih = 1160; iw = ih * 0.766
    scr = A.BI.image(1, int(ih * 0.91))                        # the bundle's programme page on the tablet
    tab = kit.Frame(int(iw) + 60, int(ih) + 60, CREAM); tab.img = Image.new("RGBA", tab.img.size, (0, 0, 0, 0))
    kit.ipad(tab, (30, 30, 30 + iw, 30 + ih), scr)
    f.paste(tab.img, 1430, 900); f.sources += tab.sources
    return f

def m08_who(A):
    f = lobby(8, "Solo or date night", "Spooky, not gory: two cozy murder mysteries to solve with a cup of tea")
    pg = A.BL.image(1, 1200)                                     # the programme page of the bundle
    f.paste_page(pg, 1390, 900, angle=1.5)
    rows = [("1–4 players", "solo, a pair or a team"), ("Two evenings", "one case per night"),
            ("90–150 min", "per case")]
    y = 330
    for i, (big, small) in enumerate(rows):
        cx = 260
        if i == 0:
            kit.people(f, cx, y + 120, 140, 3, CREAM)
        elif i == 1:
            d = f.draw()
            d.ellipse([cx - 110, y + 40, cx - 10, y + 140], fill=ORANGE)
            d.ellipse([cx + 10, y + 40, cx + 110, y + 140], fill=GOLD)
            d.ellipse([cx + 40, y + 30, cx + 130, y + 120], fill=B.MOON["mid"])
        else:
            kit.clock(f, cx, y + 90, 80, CREAM, B.MOON["dark"], GOLD)
        f.text((370, y + 30), big, P.hf("abril", 74), GOLD)
        f.text((372, y + 140), small, P.hf("oswald", 44, 400), CREAM)
        y += 400
    return f

def m09_value(A):
    f = lobby(9, "Why the double feature", "Both cases in one download, for less than buying them one by one")
    stats = [("2", "complete cases"), ("12,000", "suspects"), ("36", "clues"),
             ("12", "case documents"), ("108", "hints, 3 levels"), ("2", "Sealed Checks")]
    for i, (num, txt) in enumerate(stats):
        col, row = i % 3, i // 3
        cx = 120 + 293 + col * 587; cy = 236 + 330 + row * 600
        pal = B.STORM if col == 0 or (col == 1 and row == 0) else B.MOON
        d = f.draw()
        d.rounded_rectangle([cx - 250, cy - 230, cx + 250, cy + 230], radius=30, fill=CREAM)
        d.rounded_rectangle([cx - 236, cy - 216, cx + 236, cy + 216], radius=24, outline=pal["accent"], width=6)
        f.text((cx, cy - 170), num, P.fit(num, "abril", 190, 440), pal["dark"], anchor="ma")
        f.text((cx, cy + 90), txt, P.fit(txt, "oswald", 54, 440, 600), B.INK, anchor="ma")
    return f

def m10_get(A):
    f = kit.Frame(S, S, BLACK); img = f.img
    two_tone(img, (0, 0, S, S)); seam(img, S / 2, 0, S, 8)
    P.tracked(f, S / 2, 92, "QUIETCLUECO PRESENTS", P.hf("cinzel", 46, 700), CREAM, 12)
    P.title_word(f, "What you get", S / 2, 160, P.hf("abril", 190), fill=GOLD, shadow=(0x5A, 0x1E, 0x10),
                 depth=16, outline=BLACK, inline=CREAM, k=1.4)
    lab = kit.font("black", 46); bf = kit.font("black", 32)
    cards = [("US Letter", A.BL.image(0, 520)), ("A4", A.BA.image(0, 520)), ("iPad", A.BI.image(0, 520))]
    x = 110
    for name, thumb in cards:
        kit.pdf_file_card(f, (x, 470, x + 400, 1040), thumb, name, lab, "PDF", bf)
        x += 450
    kit.pdf_file_card(f, (x, 470, x + 400, 1040), None, "Solutions", lab, "ZIP", bf)
    e = env_img("?", 280, 200); f.paste(e.img, x + 200, 700, shadow=False); f.sources += e.sources
    f.text((x + 200, 830), "6 files, both cases", kit.font("black", 36), B.INK, anchor="ma")
    rules = A.cs[0].page("rules", 700)          # case 3’s rules quote "ticket 1234", a case-2 finalist ticket
    f.paste_page(rules, 520, 1480, angle=-2)
    f.text((520, 1862), "House rules: every term defined", P.hf("oswald", 44, 600), CREAM, anchor="ma")
    d = f.draw()
    cx, cy, r = 1420, 1470, 380
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GOLD)
    d.ellipse([cx - r + 22, cy - r + 22, cx + r - 22, cy + r - 22], outline=BLACK, width=8)
    f.text((cx, cy - 250), "Exactly one\nanswer in\neach case", P.hf("abril", 96), BLACK, anchor="ma", align="center")
    f.text((cx, cy + 128), "checked by code", P.hf("oswald", 58, 600), BLACK, anchor="ma")
    kit.tick(f, cx - 50, cy + 270, 90, BLACK, 13)
    P.deco_frame(f, 36, 1.5, GOLD)
    P.aged(img, 23, border=24)
    return f

MOCKUPS = [("01-double-feature-poster", m01_main), ("02-two-cases", m02_two_cases), ("03-twelve-documents", m03_documents),
           ("04-visitor-logs-in-progress", m04_logs), ("05-three-levels-of-hints", m05_hints),
           ("06-sealed-check", m06_check), ("07-print-or-ipad", m07_devices), ("08-who-its-for", m08_who),
           ("09-bundle-value", m09_value), ("10-what-you-get", m10_get)]

class Assets:
    def __init__(self):
        self.bad = B.forbidden()
        self.cs = [Case(c, self.bad) for c in B.CASES]
        dl = os.path.join(B.ROOT, "delivery")
        self.BL = kit.Pdf(os.path.join(dl, B.OUT_NAMES["letter"]))
        self.BA = kit.Pdf(os.path.join(dl, B.OUT_NAMES["a4"]))
        self.BI = kit.Pdf(os.path.join(dl, B.OUT_NAMES["ipad"]))

def build():
    os.makedirs(OUT, exist_ok=True)
    A = Assets(); res = []; thumbs = []
    for name, fn in MOCKUPS:
        fr = fn(A)
        path = os.path.join(OUT, f"{B.SLUG}_{name}.jpg")
        fr.img.convert("RGB").save(path, quality=90, optimize=True, progressive=True)
        res.append(dict(name=name, path=path, sources=fr.sources, hits=kit.spoiler_scan(fr.sources, A.bad)))
        thumbs.append(fr.img.convert("RGB").resize((380, 380), Image.LANCZOS))
    g = 24; W = 5 * 380 + 6 * g; H = 2 * 380 + 3 * g + 90
    sheet = Image.new("RGB", (W, H), BLACK); d = ImageDraw.Draw(sheet)
    d.text((W / 2, 20), f"{B.NAME} — listing images 1–10", font=P.hf("abril", 48), fill=CREAM, anchor="ma")
    for i, t in enumerate(thumbs):
        sheet.paste(t, (g + (i % 5) * (380 + g), 90 + g + (i // 5) * (380 + g)))
        d.text((g + (i % 5) * (380 + g) + 14, 90 + g + (i // 5) * (380 + g) + 10), str(i + 1), font=kit.font("black", 40), fill=GOLD)
    sheet_path = os.path.join(OUT, f"{B.SLUG}_overview.jpg"); sheet.save(sheet_path, quality=88)
    return res, sheet_path, A

if __name__ == "__main__":
    res, sheet, A = build()
    for r in res:
        print(r["name"], len(r["sources"]), "sources", len(r["hits"]), "hits", os.path.getsize(r["path"]) // 1024, "KB",
              [h["label"] for h in r["hits"]][:4])
