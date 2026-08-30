"""Etsy listing slides for the Annual Budget spreadsheet — 2000x2000 PNGs.

Same visual system as the promo video (browser window, mint palette read out of
the workbook, Playfair + Montserrat), extended to static slides: left-aligned
editorial layout, numbered index, no laptop mockup and no sticker badges.

  usage: make_listing_slides.py <out-dir> <fonts-dir> <shots-dir> [light|dark]
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, sys

OUT   = sys.argv[1]
FONTS = sys.argv[2]
SHOTS = sys.argv[3]
THEME = (sys.argv[4] if len(sys.argv) > 4 else "light").lower()
os.makedirs(OUT, exist_ok=True)

S, M = 2000, 130

if THEME == "dark":
    BG_HI, BG_LO = (22, 31, 56), (9, 13, 26)
    INK    = (234, 243, 240)
    MUTED  = (139, 158, 190)
    ACCENT = (123, 255, 162)
    ACC_TX = (8, 20, 14)
    CARD   = (19, 28, 47)
    EDGE   = (44, 57, 92)
    RULE   = (44, 57, 92)
    WIN_BAR, WIN_BODY, DOT = (26, 35, 62), (11, 14, 25), (58, 74, 116)
    URL_TX = (104, 124, 160)
else:
    BG_HI, BG_LO = (246, 252, 249), (226, 242, 234)
    INK    = (51, 86, 107)
    MUTED  = (122, 145, 160)
    ACCENT = (223, 243, 234)
    ACC_TX = (51, 86, 107)
    CARD   = (255, 255, 255)
    EDGE   = (203, 228, 214)
    RULE   = (185, 223, 205)
    WIN_BAR, WIN_BODY, DOT = (233, 244, 238), (255, 255, 255), (198, 220, 208)
    URL_TX = (150, 176, 168)

def F(name, size): return ImageFont.truetype(os.path.join(FONTS, name), size)
PF  = lambda s: F("PlayfairDisplay-700.ttf", s)
M4  = lambda s: F("Montserrat-400.ttf", s)
M5  = lambda s: F("Montserrat-500.ttf", s)
M6  = lambda s: F("Montserrat-600.ttf", s)
M7  = lambda s: F("Montserrat-700.ttf", s)

def tracked(d, x, y, txt, fnt, fill, tr=0.0, anchor_left=True):
    asc, _ = fnt.getmetrics()
    if not anchor_left:
        w = d.textlength(txt, font=fnt) + tr * max(len(txt) - 1, 0)
        x -= w
    for ch in txt:
        d.text((x, y + asc), ch, font=fnt, fill=fill, anchor="ls")
        x += d.textlength(ch, font=fnt) + tr

def wrap(d, txt, fnt, width):
    words, lines, cur = txt.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fnt) <= width: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def para(d, x, y, txt, fnt, fill, width, lh):
    for i, line in enumerate(wrap(d, txt, fnt, width)):
        d.text((x, y + i * lh), line, font=fnt, fill=fill)
    return y + len(wrap(d, txt, fnt, width)) * lh

def gradient():
    img = Image.new("RGB", (1, S)); p = ImageDraw.Draw(img)
    for y in range(S):
        t = y / (S - 1)
        p.point((0, y), tuple(int(BG_HI[i] + (BG_LO[i] - BG_HI[i]) * t) for i in range(3)))
    return img.resize((S, S), Image.BICUBIC)

def window(shot_path, inner_w, url="annual-budget-2026", chip=None):
    """Screenshot in the same browser frame the video uses."""
    shot = Image.open(shot_path).convert("RGB")
    inner_h = round(inner_w * shot.height / shot.width)
    shot = shot.resize((inner_w, inner_h), Image.LANCZOS)
    bar = max(46, round(inner_w * 0.042))
    pad = 12
    W, H = inner_w + pad * 2, inner_h + bar + pad
    win = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(win)
    d.rounded_rectangle([0, 0, W - 1, H - 1], radius=20, fill=WIN_BODY, outline=EDGE, width=2)
    d.rounded_rectangle([0, 0, W - 1, bar + 18], radius=20, fill=WIN_BAR)
    d.rectangle([0, bar - 4, W - 1, bar], fill=WIN_BAR)
    d.line([(0, bar), (W - 1, bar)], fill=EDGE, width=2)
    r = max(4, bar // 9)
    for i in range(3):
        cx = 24 + i * (r * 4)
        d.ellipse([cx - r, bar / 2 - r, cx + r, bar / 2 + r], fill=DOT)
    uf = M5(max(14, bar // 3))
    pill_w = min(inner_w * 0.42, 520)
    d.rounded_rectangle([24 + r * 10, bar * 0.22, 24 + r * 10 + pill_w, bar * 0.78],
                        radius=bar // 4, fill=CARD if THEME == "light" else (17, 23, 42))
    d.text((24 + r * 10 + 18, bar / 2), url, font=uf, fill=URL_TX, anchor="lm")
    if chip:
        cf = M7(max(14, bar // 3))
        cw = d.textlength(chip, font=cf) + 1.6 * (len(chip) - 1) + 34
        d.rounded_rectangle([W - 24 - cw, bar * 0.22, W - 24, bar * 0.78], radius=bar // 4, fill=ACCENT)
        tracked(d, W - 24 - cw / 2 - (cw - 34) / 2, bar * 0.22 + (bar * 0.28 - cf.size) / 2 + 2,
                chip, cf, ACC_TX, tr=1.6)
    win.paste(shot, (pad, bar))
    d.rectangle([pad - 1, bar - 1, pad + inner_w, bar + inner_h], outline=EDGE, width=1)
    return win

def shadow(base, box, blur=48, alpha=58, color=None):
    sh = Image.new("L", (S, S), 0)
    ImageDraw.Draw(sh).rounded_rectangle(box, radius=26, fill=alpha)
    col = color or ((120, 152, 136) if THEME == "light" else (0, 0, 0))
    base.paste(Image.new("RGB", (S, S), col), (0, 0), sh.filter(ImageFilter.GaussianBlur(blur)))

def fit(d, txt, maker, size, width):
    """Shrink a display line until it fits the column."""
    while size > 48 and d.textlength(txt, font=maker(size)) > width:
        size -= 4
    return maker(size)

def head(d, eyebrow, title, sub=None, y=150):
    tracked(d, M, y, eyebrow, M6(28), MUTED, tr=8)
    d.text((M, y + 62), title, font=fit(d, title, PF, 118, S - 2 * M), fill=INK)
    if sub:
        return para(d, M, y + 232, sub, M4(40), MUTED, 1500, 56)
    return y + 232

def foot(d, idx, total=6):
    d.line([(M, 1858), (S - M, 1858)], fill=RULE, width=2)
    tracked(d, M, 1890, "THE ANNUAL BUDGET  ·  GOOGLE SHEETS & EXCEL", M6(24), MUTED, tr=4)
    tracked(d, S - M, 1890, f"{idx:02d} / {total:02d}", M6(24), MUTED, tr=4, anchor_left=False)

def card(d, box, radius=22):
    d.rounded_rectangle(box, radius=radius, fill=CARD, outline=EDGE, width=2)

def chip(d, x, y, text, fnt=None, pad=26, h=64):
    fnt = fnt or M6(26)
    w = d.textlength(text, font=fnt) + 2.4 * (len(text) - 1) + pad * 2
    d.rounded_rectangle([x, y, x + w, y + h], radius=h / 2, fill=ACCENT)
    tracked(d, x + pad, y + (h - fnt.size) / 2 - 2, text, fnt, ACC_TX, tr=2.4)
    return x + w

def sp(name): return os.path.join(SHOTS, f"{THEME}_{name}.png")

# ---------------------------------------------------------------- 01 hero
def slide1():
    im = gradient(); d = ImageDraw.Draw(im)
    tracked(d, M, 150, "SPREADSHEET TEMPLATE  ·  INSTANT DOWNLOAD", M6(28), MUTED, tr=8)
    d.text((M, 206), "The Annual Budget", font=fit(d, "The Annual Budget", PF, 150, S - 2 * M), fill=INK)
    para(d, M, 420, "One log feeds the whole year. No tab per month, no formulas to write.",
         M4(42), MUTED, 1500, 58)
    win = window(sp("dash"), 1560, chip="UPDATES ITSELF")
    x = (S - win.width) // 2
    y = 570
    shadow(im, [x + 30, y + 20, x + win.width - 30, y + win.height - 10])
    im.paste(win, (x, y), win)
    xx = M
    for t in ("9 TABS", "12 MONTHS ON ONE SHEET", "NO FORMULAS TO WRITE"):
        xx = chip(d, xx, y + win.height + 90, t) + 24
    foot(d, 1)
    return im

# ---------------------------------------------------------------- 02 tabs
TABS = [
    ("Start Here",          "How it works, in three steps."),
    ("Setup",               "Your year, currency, categories, accounts."),
    ("Transactions",        "Income, expense, transfer — logged once."),
    ("Annual Dashboard",    "The whole year. Nothing to fill in."),
    ("50 / 30 / 20 Rule",   "Needs, wants and savings, checked."),
    ("Spending Tracker",    "Every category, ranked by spend."),
    ("Month View",          "Any month on its own, from one dropdown."),
    ("Bill Calendar",       "Weekly to yearly bills, true monthly cost."),
    ("Savings & Net Worth", "Goals, assets, liabilities, net worth."),
]
def slide2():
    im = gradient(); d = ImageDraw.Draw(im)
    head(d, "WHAT'S INSIDE", "Nine tabs, one file",
         "Every tab reads the same transaction log — nothing is typed twice.")
    cw, ch, gap = 540, 300, 40
    x0 = (S - (cw * 3 + gap * 2)) // 2
    y0 = 620
    for i, (name, desc) in enumerate(TABS):
        cx = x0 + (i % 3) * (cw + gap)
        cy = y0 + (i // 3) * (ch + gap)
        card(d, [cx, cy, cx + cw, cy + ch])
        tracked(d, cx + 38, cy + 34, f"{i+1:02d}", M7(26), ACC_TX if THEME == "light" else ACCENT, tr=2)
        d.line([(cx + 38, cy + 78), (cx + 78, cy + 78)], fill=RULE, width=3)
        d.text((cx + 38, cy + 104), name, font=M6(34), fill=INK)
        para(d, cx + 38, cy + 166, desc, M4(26), MUTED, cw - 76, 38)
    para(d, M, 1700, "Every formula is already written — the blue cells are the only ones you fill.",
         M4(32), MUTED, 1500, 46)
    foot(d, 2)
    return im

# ---------------------------------------------------------------- 03 three steps
STEPS = [("Set up once", "Your year, currency, categories and accounts — edited in one place.", "setup"),
         ("Log it once", "Date, type, category, account, amount. Dropdowns do the typing.", "trans"),
         ("Read the year", "Months, categories, charts and totals fill themselves in.", "dash")]
def slide3():
    im = gradient(); d = ImageDraw.Draw(im)
    head(d, "HOW IT WORKS", "Three steps, then it runs itself")
    cw, gap = 570, 46
    x0 = (S - (cw * 3 + gap * 2)) // 2
    y0 = 640
    for i, (title, desc, shot) in enumerate(STEPS):
        cx = x0 + i * (cw + gap)
        win = window(sp(shot), cw - 20, url="annual-budget-2026")
        shadow(im, [cx + 24, y0 + 16, cx + cw - 24, y0 + win.height])
        im.paste(win, (cx, y0), win)
        ty = y0 + win.height + 46
        tracked(d, cx, ty, f"{i+1:02d}", M7(26), ACC_TX if THEME == "light" else ACCENT, tr=2)
        d.text((cx, ty + 44), title, font=M6(38), fill=INK)
        para(d, cx, ty + 106, desc, M4(27), MUTED, cw, 40)
    d.line([(M, 1560), (S - M, 1560)], fill=RULE, width=2)
    para(d, M, 1610, "Everything else — the dashboard, the charts, the month view, the bill calendar — "
                     "reads that one log. Nothing is entered twice.", M4(34), MUTED, 1620, 50)
    foot(d, 3)
    return im

# ---------------------------------------------------------------- 04 dashboard
QUAD = [("The year in four numbers", "Income, expenses, saved and net — year and months.", "dash"),
        ("Where the money goes",     "Each category as a share of the year.", "donut"),
        ("Income against spending",  "Twelve months side by side.", "chart"),
        ("50 / 30 / 20, checked",    "Needs, wants and savings against target.", "rule")]
def slide4():
    im = gradient(); d = ImageDraw.Draw(im)
    head(d, "THE DASHBOARD", "Your whole year at a glance")
    cw, gap = 830, 60
    x0 = (S - (cw * 2 + gap)) // 2
    y0 = 560
    for i, (title, desc, shot) in enumerate(QUAD):
        cx = x0 + (i % 2) * (cw + gap)
        cy = y0 + (i // 2) * 640
        win = window(sp(shot), cw - 20)
        shadow(im, [cx + 20, cy + 16, cx + cw - 20, cy + win.height])
        im.paste(win, (cx, cy), win)
        ty = cy + win.height + 28
        d.text((cx, ty), title, font=M6(34), fill=INK)
        para(d, cx, ty + 50, desc, M4(26), MUTED, cw, 38)
    foot(d, 4)
    return im

# ---------------------------------------------------------------- 05 details
DETAILS = [("Dropdowns, not typing", "Type, category and account are lists. Month, year and the 50/30/20 tag fill themselves."),
           ("The true cost of a bill", "Weekly, quarterly or yearly — every bill converted to a fair monthly and yearly figure."),
           ("One month, on its own",  "Pick a month and the sheet re-reads your log for it. Nothing is re-typed."),
           ("Ranked, not listed",     "Categories sorted by what they actually took, with the top one called out."),
           ("Goals and net worth",    "Savings funds fill from your transfers; assets minus liabilities, kept current.")]
def slide5():
    im = gradient(); d = ImageDraw.Draw(im)
    head(d, "THE DETAILS", "Details that save the most time")
    y = 600
    for title, desc in DETAILS:
        d.ellipse([M, y + 6, M + 22, y + 28], fill=ACCENT if THEME == "light" else ACCENT,
                  outline=RULE if THEME == "light" else None, width=2)
        d.text((M + 52, y), title, font=M6(36), fill=INK)
        para(d, M + 52, y + 54, desc, M4(27), MUTED, 760, 40)
        y += 186
    win = window(sp("bills"), 800)
    shadow(im, [1030, 620, 1870, 620 + win.height])
    im.paste(win, (1040, 600), win)
    win2 = window(sp("month"), 800)
    shadow(im, [1030, 1180, 1870, 1180 + win2.height])
    im.paste(win2, (1040, 1160), win2)
    foot(d, 5)
    return im

# ---------------------------------------------------------------- 06 what you get
GET = ["Instant download — the file is yours the moment you buy.",
       "Works in Google Sheets and in Excel.",
       "Your own categories, accounts and currency, edited on the Setup tab.",
       "Formulas are protected. Only the blue cells are yours to fill.",
       "Any year: set it once on Setup and the whole file follows.",
       "No subscription, no add-ons, no account to create."]
def slide6():
    im = gradient(); d = ImageDraw.Draw(im)
    head(d, "WHAT YOU GET", "Everything, in one file")
    y = 600
    for line in GET:
        d.rounded_rectangle([M, y + 2, M + 30, y + 32], radius=8, fill=ACCENT)
        d.line([(M + 8, y + 17), (M + 14, y + 24)], fill=ACC_TX, width=4)
        d.line([(M + 14, y + 24), (M + 24, y + 10)], fill=ACC_TX, width=4)
        para(d, M + 58, y, line, M4(32), INK, 780, 46)
        y += 118
    win = window(sp("net"), 880)
    shadow(im, [970, 620, 1880, 620 + win.height])
    im.paste(win, (980, 600), win)
    para(d, M, y + 40, "An organisation tool, not financial advice.", M4(26), MUTED, 800, 38)
    foot(d, 6)
    return im

for i, fn in enumerate((slide1, slide2, slide3, slide4, slide5, slide6), 1):
    img = fn()
    p = os.path.join(OUT, f"{THEME}_slide_{i:02d}.png")
    img.save(p)
    print("saved", p)
