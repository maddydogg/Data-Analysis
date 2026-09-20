"""Design layers for the Reseller Tracker (UK) listing video — 1080x1080.

This is the UK edition of the workbook the `reseller-tracker-promo` listing
sells, so the frame has to read as a sibling of that one and never as a
duplicate of it. What separates them is in the file itself: the UK Dashboard
draws profit as TWO series — `#78E3A4` for profit on items and the slate
`#395668` for net profit — where the US one draws a single mint bar. So the
ground here is bar PAIRS in those two colours, and the whole frame is keyed to
the slate rather than to the mint.

Everything UK about the workbook is said in words rather than drawn: pounds,
the 6 April tax year, and HMRC's 45p a mile.

Bar pairs belong to this listing alone: the US tracker's ground is flat column
bands, the light edition's a single-series chart, the invoice's horizontal
section bands and the estimate's a manila docket.
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

PAPER_HI = (244, 248, 250)
PAPER_LO = (212, 226, 233)
LIGHT    = (120, 227, 164)      # 78E3A4 — profit on items
SLATE    = (57, 86, 104)        # 395668 — net profit
HAIR     = (182, 202, 213)
INK      = (30, 52, 66)
STEEL    = (45, 76, 96)
ACCENT   = (43, 74, 94)
MUTED    = (116, 138, 152)
WIN_BAR  = (228, 236, 241)
WIN_BODY = (255, 255, 255)
EDGE     = (182, 202, 213)
PILL_TX  = (112, 132, 146)

# the demo tax year's own two series, April to March
ITEMS = [68.38, 527.52, 490.70, 769.83, 733.48, 208.96, 0, 0, 0, 0, 0, 0]
NET   = [-105.09, 414.03, 317.72, 616.86, 588.99, 65.48, 0, 0, 0, 0, 0, 0]

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

lay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
ld = ImageDraw.Draw(lay)
BASE, TALL = S - 4, 236
top_val = max(max(ITEMS), max(NET))
slot = S / len(ITEMS)
for i, (a, b) in enumerate(zip(ITEMS, NET)):
    ha = 4 + (TALL - 4) * max(a, 0) / top_val
    hb = 4 + (TALL - 4) * max(b, 0) / top_val
    x0 = i * slot + slot * 0.13
    mid = i * slot + slot * 0.50
    x1 = (i + 1) * slot - slot * 0.13
    ld.rectangle([x0, BASE - ha, mid - 2, BASE], fill=LIGHT + (62,))
    ld.rectangle([mid + 2, BASE - hb, x1, BASE], fill=SLATE + (44,))
ld.line([(0, BASE - TALL - 40), (S, BASE - TALL - 40)], fill=HAIR + (110,))
bg = Image.alpha_composite(bg.convert("RGBA"), lay.filter(ImageFilter.GaussianBlur(0.6))).convert("RGB")
d = ImageDraw.Draw(bg)
d.line([(0, 158), (S, 158)], fill=HAIR, width=1)

draw_tracked(d, S / 2, 40, "FOR THE UK  ·  £  ·  6 APRIL TAX YEAR  ·  HMRC MILEAGE",
             M600(15), MUTED, tr=2.8)
draw_tracked(d, S / 2, 70, "Reseller Tracker · UK", PF700(56), INK, tr=0.5)

sh = Image.new("L", (S, S), 0)
ImageDraw.Draw(sh).rounded_rectangle([WIN[0] + 4, WIN[1] + 12, WIN[2] + 4, WIN[3] + 16],
                                     radius=18, fill=64)
bg.paste(Image.new("RGB", (S, S), (74, 100, 118)), (0, 0), sh.filter(ImageFilter.GaussianBlur(22)))
d = ImageDraw.Draw(bg)

d.rounded_rectangle(list(WIN), radius=18, fill=WIN_BODY, outline=EDGE, width=2)
d.rounded_rectangle([WIN[0], WIN[1], WIN[2], WIN[1] + BAR_H + 18], radius=18, fill=WIN_BAR)
d.rectangle([WIN[0], WIN[1] + BAR_H - 4, WIN[2], WIN[1] + BAR_H], fill=WIN_BAR)
d.line([(WIN[0], WIN[1] + BAR_H), (WIN[2], WIN[1] + BAR_H)], fill=EDGE, width=2)
for cx in (WIN[0] + 26, WIN[0] + 46, WIN[0] + 66):
    d.ellipse([cx - 5, WIN[1] + 20, cx + 5, WIN[1] + 30], fill=(178, 198, 210))
d.rounded_rectangle([WIN[0] + 92, WIN[1] + 14, WIN[0] + 520, WIN[1] + 36], radius=11, fill=(238, 243, 246))
d.text((WIN[0] + 108, WIN[1] + 25), "reseller-tracker-uk-2026", font=M500(13), fill=(130, 150, 164),
       anchor="lm")
chip = "06 APR 2026 — 05 APR 2027"
chip_w = d.textlength(chip, font=M700(12)) + 1.5 * (len(chip) - 1) + 26
d.rounded_rectangle([WIN[2] - 20 - chip_w, WIN[1] + 14, WIN[2] - 20, WIN[1] + 36], radius=11, fill=ACCENT)
draw_tracked(d, WIN[2] - 20 - chip_w / 2, WIN[1] + 18, chip, M700(12), (236, 244, 248), tr=1.5)

d.rectangle([SCREEN[0], SCREEN[1], SCREEN[0] + SCREEN[2], SCREEN[1] + SCREEN[3]], fill=WIN_BODY)
d.rectangle([SCREEN[0] - 1, SCREEN[1] - 1, SCREEN[0] + SCREEN[2] + 1, SCREEN[1] + SCREEN[3] + 1],
            outline=(196, 214, 224), width=1)

fnt_tab, boxes, TR = tab_layout(d)
for (x, w), label in zip(boxes, TABS):
    d.rounded_rectangle([x, TAB_Y, x + w, TAB_Y + TAB_H], radius=TAB_H / 2,
                        fill=(234, 241, 245), outline=EDGE, width=1)
    draw_tracked(d, x + w / 2, TAB_Y + 7, label.upper(), fnt_tab, PILL_TX, tr=TR)

draw_tracked(d, S / 2, 948, "EBAY · VINTED · DEPOP · ETSY · WHATNOT · CAR BOOT — FEES AND PROFIT WORK THEMSELVES OUT",
             M600(13), INK, tr=0.9)
draw_tracked(d, S / 2, 976,
             "lots · expenses · mileage at 45p · dashboard · net profit after mileage",
             M400(13), MUTED, tr=0.4)
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
    "Pounds, 6 April, HMRC mileage",
    "eBay, Vinted, Depop, Etsy — the fees are in",
    "One row per item — blue is yours, green calculates",
    "A car-boot box for one price → cost per item",
    "Your tax year, 6 April to 5 April",
    "Net profit, live",
    "And the mileage deduction on top",
]
for i, caption in enumerate(CAPTIONS, 1):
    lay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    cd = ImageDraw.Draw(lay)
    size = 30 if len(caption) < 30 else (26 if len(caption) < 42 else 23)
    pad_w = tw(cd, caption, M500(size), 0.3) + 46
    cd.rounded_rectangle([(S - pad_w) / 2, 184, (S + pad_w) / 2, 184 + size + 22],
                         radius=(size + 22) / 2, fill=(252, 254, 255, 226), outline=HAIR + (210,))
    draw_tracked(cd, S / 2, 193, caption, M500(size), STEEL + (255,), tr=0.3)
    lay.save(os.path.join(OUT, f"cap{i}.png"))

probe = ImageDraw.Draw(Image.new("RGB", (S, S)))
fnt_tab, boxes, TR = tab_layout(probe)
for i, tab in enumerate(TABS, 1):
    pill = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pill)
    x, w = boxes[i - 1]
    pd.rounded_rectangle([x, TAB_Y, x + w, TAB_Y + TAB_H], radius=TAB_H / 2, fill=ACCENT + (255,))
    draw_tracked(pd, x + w / 2, TAB_Y + 8, tab.upper(), fnt_tab, (238, 246, 250, 255), tr=TR)
    pill.save(os.path.join(OUT, f"pill{i}.png"))

Image.new("RGBA", (S, 5), ACCENT + (255,)).save(os.path.join(OUT, "bar.png"))
print("layers ->", OUT)
