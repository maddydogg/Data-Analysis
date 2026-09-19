"""Design layers for the Reseller Tracker listing video (1080x1080).

Keyed to the workbook's palette, and to the one sentence it prints under its own
title: *Blue columns are yours, green ones calculate.* So the ground is columns
— wide, faint vertical bands alternating the sheet's input blue `#F0F3FA` and
its computed mint `#E0F3E8`, closed by hairlines, the way the sheet codes its
own. The accent is the steel blue its input cells are written in, which is what
separates this frame from the mint-and-green one the invoice listing uses.

Columns are this listing's device alone: horizontal section bands belong to the
invoice video, the manila docket to the estimate one, the ledger ruling to the
bookkeeping one, the mesh to debt, the sweeps to the budget planner and the
single mint wash to the ADHD planner.
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

PAPER_HI = (247, 250, 249)
PAPER_LO = (219, 233, 228)
COL_BLUE = (232, 238, 250)      # F0F3FA — the columns the seller fills in
COL_MINT = (224, 243, 232)      # E0F3E8 — the columns the sheet works out
HAIR     = (198, 216, 210)
INK      = (44, 62, 70)
STEEL    = (46, 93, 122)        # 2E5D7A — the colour its inputs are written in
ACCENT   = (38, 86, 116)
MUTED    = (121, 141, 140)
WIN_BAR  = (231, 239, 238)
WIN_BODY = (255, 255, 255)
EDGE     = (188, 209, 205)
PILL_TX  = (110, 130, 130)

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
bg = gradient((S, S), PAPER_HI, PAPER_LO)

# the sheet's own coding, made into the ground: (x, width, colour, opacity)
cols = [(0, 96, COL_BLUE, 200), (96, 128, COL_MINT, 150), (300, 104, COL_BLUE, 120),
        (520, 150, COL_MINT, 130), (742, 112, COL_BLUE, 170), (854, 142, COL_MINT, 200),
        (996, 84, COL_BLUE, 130)]
lay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
ld = ImageDraw.Draw(lay)
for x, w, c, a in cols:
    ld.rectangle([x, 0, x + w, S], fill=c + (a,))
    ld.line([(x, 0), (x, S)], fill=HAIR + (110,))
    ld.line([(x + w, 0), (x + w, S)], fill=HAIR + (110,))
bg = Image.alpha_composite(bg.convert("RGBA"), lay.filter(ImageFilter.GaussianBlur(0.5))).convert("RGB")
d = ImageDraw.Draw(bg)

# one horizontal rule under the head, the way the sheet closes a header row
d.line([(0, 156), (S, 156)], fill=HAIR, width=1)

draw_tracked(d, S / 2, 40, "EBAY · POSHMARK · MERCARI · DEPOP · ETSY · VINTED · WHATNOT",
             M600(14), MUTED, tr=2.4)
draw_tracked(d, S / 2, 70, "Reseller Tracker", PF700(60), INK, tr=0.5)

sh = Image.new("L", (S, S), 0)
ImageDraw.Draw(sh).rounded_rectangle([WIN[0] + 4, WIN[1] + 12, WIN[2] + 4, WIN[3] + 16],
                                     radius=18, fill=60)
bg.paste(Image.new("RGB", (S, S), (84, 110, 122)), (0, 0), sh.filter(ImageFilter.GaussianBlur(22)))
d = ImageDraw.Draw(bg)

d.rounded_rectangle(list(WIN), radius=18, fill=WIN_BODY, outline=EDGE, width=2)
d.rounded_rectangle([WIN[0], WIN[1], WIN[2], WIN[1] + BAR_H + 18], radius=18, fill=WIN_BAR)
d.rectangle([WIN[0], WIN[1] + BAR_H - 4, WIN[2], WIN[1] + BAR_H], fill=WIN_BAR)
d.line([(WIN[0], WIN[1] + BAR_H), (WIN[2], WIN[1] + BAR_H)], fill=EDGE, width=2)
for cx in (WIN[0] + 26, WIN[0] + 46, WIN[0] + 66):
    d.ellipse([cx - 5, WIN[1] + 20, cx + 5, WIN[1] + 30], fill=(182, 203, 200))
d.rounded_rectangle([WIN[0] + 92, WIN[1] + 14, WIN[0] + 520, WIN[1] + 36], radius=11, fill=(240, 245, 245))
d.text((WIN[0] + 108, WIN[1] + 25), "reseller-tracker-2026", font=M500(13), fill=(136, 155, 155),
       anchor="lm")
chip = "ONE ROW PER ITEM"
chip_w = d.textlength(chip, font=M700(12)) + 1.6 * (len(chip) - 1) + 26
d.rounded_rectangle([WIN[2] - 20 - chip_w, WIN[1] + 14, WIN[2] - 20, WIN[1] + 36], radius=11, fill=ACCENT)
draw_tracked(d, WIN[2] - 20 - chip_w / 2, WIN[1] + 18, chip, M700(12), (238, 246, 250), tr=1.6)

d.rectangle([SCREEN[0], SCREEN[1], SCREEN[0] + SCREEN[2], SCREEN[1] + SCREEN[3]], fill=WIN_BODY)
d.rectangle([SCREEN[0] - 1, SCREEN[1] - 1, SCREEN[0] + SCREEN[2] + 1, SCREEN[1] + SCREEN[3] + 1],
            outline=(200, 218, 214), width=1)

fnt_tab, boxes, TR = tab_layout(d)
for (x, w), label in zip(boxes, TABS):
    d.rounded_rectangle([x, TAB_Y, x + w, TAB_Y + TAB_H], radius=TAB_H / 2,
                        fill=(238, 244, 243), outline=EDGE, width=1)
    draw_tracked(d, x + w / 2, TAB_Y + 7, label.upper(), fnt_tab, PILL_TX, tr=TR)

draw_tracked(d, S / 2, 948, "FEES, NET PROFIT AND ROI WORK THEMSELVES OUT — PER ITEM",
             M600(15), INK, tr=1.4)
draw_tracked(d, S / 2, 978,
             "lots · expenses · mileage · where to buy · net profit after mileage",
             M400(13), MUTED, tr=0.4)
d.rectangle([0, S - 5, S, S], fill=(198, 216, 212))
bg.save(os.path.join(OUT, "bg.png"))

# ---------------------------------------------------------------- foreground
fg = Image.new("RGBA", (S, S), (0, 0, 0, 0))
x0, y0, w, h = SCREEN
mask = Image.new("L", (w, h), 255)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=6, fill=0)
corner = Image.new("RGBA", (w, h), WIN_BODY + (255,)); corner.putalpha(mask)
fg.alpha_composite(corner, (x0, y0))
glare = Image.new("L", (w, h), 0)
ImageDraw.Draw(glare).polygon([(0, 0), (int(w * 0.38), 0), (0, h)], fill=12)
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
    "It tells you where to buy",
    "Every figure the tax return needs",
    "Net profit — and the mileage on top",
]
for i, caption in enumerate(CAPTIONS, 1):
    lay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    cd = ImageDraw.Draw(lay)
    size = 30 if len(caption) < 30 else (27 if len(caption) < 40 else 24)
    pad_w = tw(cd, caption, M500(size), 0.3) + 46
    cd.rounded_rectangle([(S - pad_w) / 2, 182, (S + pad_w) / 2, 182 + size + 22],
                         radius=(size + 22) / 2, fill=(253, 254, 254, 224), outline=HAIR + (210,))
    draw_tracked(cd, S / 2, 191, caption, M500(size), STEEL + (255,), tr=0.3)
    lay.save(os.path.join(OUT, f"cap{i}.png"))

probe = ImageDraw.Draw(Image.new("RGB", (S, S)))
fnt_tab, boxes, TR = tab_layout(probe)
for i, tab in enumerate(TABS, 1):
    pill = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pill)
    x, w = boxes[i - 1]
    pd.rounded_rectangle([x, TAB_Y, x + w, TAB_Y + TAB_H], radius=TAB_H / 2, fill=ACCENT + (255,))
    draw_tracked(pd, x + w / 2, TAB_Y + 8, tab.upper(), fnt_tab, (240, 247, 250, 255), tr=TR)
    pill.save(os.path.join(OUT, f"pill{i}.png"))

Image.new("RGBA", (S, 5), ACCENT + (255,)).save(os.path.join(OUT, "bar.png"))
print("layers ->", OUT)
