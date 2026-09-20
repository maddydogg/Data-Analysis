"""Design layers for the Reseller Tracker (dark) listing video — 1080x1080.

The dark edition of the workbook `../reseller-tracker-promo` sells, so it keeps
that listing's device — vertical column bands, the sheet's own "blue columns are
yours, green ones calculate" made into the ground — and only changes key. The
colours are this edition's own: the page's `#0C1020`, its banded rows `#14182C`,
its section green `#143824` and the `#78FCA0` it writes its headers and its
chart bars in. A green glow sits behind the window, the way the other dark
listings in the shop are lit.

Same structure, dark key: that is what makes a pair read as one product in two
skins rather than as two products.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, sys

OUT   = sys.argv[1] if len(sys.argv) > 1 else "layers"
FONTS = sys.argv[2] if len(sys.argv) > 2 else "fonts"
os.makedirs(OUT, exist_ok=True)

S = 1080
SCREEN = (60, 300, 960, 540)
WIN    = (46, 250, 1034, 854)
BAR_H  = 50

BG_HI    = (22, 32, 58)
BG_LO    = (12, 16, 32)         # 0C1020 — the sheet's own page
COL_BLUE = (56, 84, 124)
COL_GRN  = (20, 56, 36)         # 143824 — its section band
HAIR     = (44, 62, 92)
ACCENT   = (120, 252, 160)      # 78FCA0 — its headers and its chart bars
DEEP     = (8, 28, 18)
TEXT     = (226, 240, 234)
MUTED    = (138, 158, 176)
WIN_BAR  = (26, 36, 60)
WIN_BODY = (12, 16, 32)
EDGE     = (52, 72, 106)
PILL_TX  = (142, 162, 182)

def f(name, size): return ImageFont.truetype(os.path.join(FONTS, name), size)
PF700 = lambda s: f("PlayfairDisplay-700.ttf", s)
M400  = lambda s: f("Montserrat-400.ttf", s)
M500  = lambda s: f("Montserrat-500.ttf", s)
M600  = lambda s: f("Montserrat-600.ttf", s)
M700  = lambda s: f("Montserrat-700.ttf", s)

TABS = ["Setup", "Inventory", "Lots", "Dashboard", "Tax Summary"]
TAB_Y, TAB_H = 886, 30

def tw(d, txt, fnt, tr=0.0):
    return d.textlength(txt, font=fnt) + tr * max(len(txt) - 1, 0)

def draw_tracked(d, cx, y, txt, fnt, fill, tr=0.0):
    asc, _ = fnt.getmetrics()
    x = cx - tw(d, txt, fnt, tr) / 2
    for ch in txt:
        d.text((x, y + asc), ch, font=fnt, fill=fill, anchor="ls")
        x += d.textlength(ch, font=fnt) + tr

def gradient(size, top, bottom):
    img = Image.new("RGB", (1, size[1])); p = ImageDraw.Draw(img)
    for y in range(size[1]):
        t = y / (size[1] - 1)
        p.point((0, y), tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return img.resize(size, Image.BICUBIC)

def tab_layout(d):
    fnt, tr = M600(12), 1.0
    widths = [d.textlength(t.upper(), font=fnt) + tr * (len(t) - 1) + 26 for t in TABS]
    gap = 8
    x = (S - (sum(widths) + gap * (len(TABS) - 1))) / 2
    boxes = []
    for w in widths:
        boxes.append((x, w)); x += w + gap
    return fnt, boxes, tr

# ---------------------------------------------------------------- background
bg = gradient((S, S), BG_HI, BG_LO)

# the light edition's columns, in this one's colours
cols = [(0, 96, COL_BLUE, 52), (96, 128, COL_GRN, 150), (300, 104, COL_BLUE, 34),
        (520, 150, COL_GRN, 110), (742, 112, COL_BLUE, 46), (854, 142, COL_GRN, 150),
        (996, 84, COL_BLUE, 36)]
lay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
ld = ImageDraw.Draw(lay)
for x, w, c, a in cols:
    ld.rectangle([x, 0, x + w, S], fill=c + (a,))
    ld.line([(x, 0), (x, S)], fill=HAIR + (80,))
    ld.line([(x + w, 0), (x + w, S)], fill=HAIR + (80,))
bg = Image.alpha_composite(bg.convert("RGBA"), lay.filter(ImageFilter.GaussianBlur(0.6))).convert("RGB")

glow = Image.new("L", (S, S), 0)
ImageDraw.Draw(glow).ellipse([90, 300, 990, 900], fill=38)
bg.paste(Image.new("RGB", (S, S), ACCENT), (0, 0), glow.filter(ImageFilter.GaussianBlur(120)))
halo = Image.new("L", (S, S), 0)
ImageDraw.Draw(halo).ellipse([-80, 80, 1160, 760], fill=26)
bg.paste(Image.new("RGB", (S, S), (70, 120, 190)), (0, 0), halo.filter(ImageFilter.GaussianBlur(110)))

d = ImageDraw.Draw(bg)
d.line([(0, 158), (S, 158)], fill=(40, 58, 86), width=1)

draw_tracked(d, S / 2, 40, "DARK EDITION  ·  EIGHT SHEETS  ·  GOOGLE SHEETS & EXCEL",
             M600(15), MUTED, tr=2.8)
draw_tracked(d, S / 2, 70, "Reseller Tracker · Dark", PF700(54), TEXT, tr=0.5)

d.rounded_rectangle(list(WIN), radius=18, fill=WIN_BODY, outline=EDGE, width=2)
d.rounded_rectangle([WIN[0], WIN[1], WIN[2], WIN[1] + BAR_H + 18], radius=18, fill=WIN_BAR)
d.rectangle([WIN[0], WIN[1] + BAR_H - 4, WIN[2], WIN[1] + BAR_H], fill=WIN_BAR)
d.line([(WIN[0], WIN[1] + BAR_H), (WIN[2], WIN[1] + BAR_H)], fill=EDGE, width=2)
for cx in (WIN[0] + 26, WIN[0] + 46, WIN[0] + 66):
    d.ellipse([cx - 5, WIN[1] + 20, cx + 5, WIN[1] + 30], fill=(62, 84, 120))
d.rounded_rectangle([WIN[0] + 92, WIN[1] + 14, WIN[0] + 520, WIN[1] + 36], radius=11, fill=(18, 26, 46))
d.text((WIN[0] + 108, WIN[1] + 25), "reseller-tracker-dark", font=M500(13), fill=(112, 134, 160),
       anchor="lm")
chip = "ONE ROW PER ITEM"
chip_w = d.textlength(chip, font=M700(12)) + 1.6 * (len(chip) - 1) + 26
d.rounded_rectangle([WIN[2] - 20 - chip_w, WIN[1] + 14, WIN[2] - 20, WIN[1] + 36], radius=11, fill=ACCENT)
draw_tracked(d, WIN[2] - 20 - chip_w / 2, WIN[1] + 18, chip, M700(12), DEEP, tr=1.6)

d.rectangle([SCREEN[0], SCREEN[1], SCREEN[0] + SCREEN[2], SCREEN[1] + SCREEN[3]], fill=WIN_BODY)
d.rectangle([SCREEN[0] - 1, SCREEN[1] - 1, SCREEN[0] + SCREEN[2] + 1, SCREEN[1] + SCREEN[3] + 1],
            outline=(48, 68, 100), width=1)

fnt_tab, boxes, TR = tab_layout(d)
for (x, w), label in zip(boxes, TABS):
    d.rounded_rectangle([x, TAB_Y, x + w, TAB_Y + TAB_H], radius=TAB_H / 2,
                        fill=(20, 30, 52), outline=EDGE, width=1)
    draw_tracked(d, x + w / 2, TAB_Y + 7, label.upper(), fnt_tab, PILL_TX, tr=TR)

draw_tracked(d, S / 2, 948, "FEES, NET PROFIT AND ROI WORK THEMSELVES OUT — PER ITEM",
             M600(15), TEXT, tr=1.4)
draw_tracked(d, S / 2, 978,
             "lots · expenses · mileage · dashboard · net profit after mileage",
             M400(13), MUTED, tr=0.4)
d.rectangle([0, S - 5, S, S], fill=(26, 40, 66))
bg.save(os.path.join(OUT, "bg.png"))

# ---------------------------------------------------------------- foreground
fg = Image.new("RGBA", (S, S), (0, 0, 0, 0))
x0, y0, w, h = SCREEN
mask = Image.new("L", (w, h), 255)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=6, fill=0)
corner = Image.new("RGBA", (w, h), WIN_BODY + (255,)); corner.putalpha(mask)
fg.alpha_composite(corner, (x0, y0))
glare = Image.new("L", (w, h), 0)
ImageDraw.Draw(glare).polygon([(0, 0), (int(w * 0.40), 0), (0, h)], fill=15)
gl = Image.new("RGBA", (w, h), (255, 255, 255, 255))
gl.putalpha(glare.filter(ImageFilter.GaussianBlur(30)))
fg.alpha_composite(gl, (x0, y0))
fg.save(os.path.join(OUT, "fg.png"))

# ---------------------------------------------------------------- captions
CAPTIONS = [
    "Your platforms and their fees — once",
    "One row per item",
    "Blue is yours. Green calculates.",
    "A box for one price? Cost per item, done.",
    "Every number, live on one dashboard",
    "Net profit, and the mileage on top",
]
for i, caption in enumerate(CAPTIONS, 1):
    lay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    cd = ImageDraw.Draw(lay)
    size = 30 if len(caption) < 30 else (27 if len(caption) < 40 else 24)
    draw_tracked(cd, S / 2, 190, caption, M500(size), TEXT + (255,), tr=0.3)
    lay.save(os.path.join(OUT, f"cap{i}.png"))

probe = ImageDraw.Draw(Image.new("RGB", (S, S)))
fnt_tab, boxes, TR = tab_layout(probe)
for i, tab in enumerate(TABS, 1):
    pill = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pill)
    x, w = boxes[i - 1]
    pd.rounded_rectangle([x, TAB_Y, x + w, TAB_Y + TAB_H], radius=TAB_H / 2, fill=ACCENT + (255,))
    draw_tracked(pd, x + w / 2, TAB_Y + 8, tab.upper(), fnt_tab, DEEP + (255,), tr=TR)
    pill.save(os.path.join(OUT, f"pill{i}.png"))

Image.new("RGBA", (S, 5), ACCENT + (255,)).save(os.path.join(OUT, "bar.png"))
print("layers ->", OUT)
