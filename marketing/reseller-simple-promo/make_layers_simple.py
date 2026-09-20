"""Design layers for the Simple Reseller Tracker listing video (1080x1080).

Keyed to the workbook's palette, and to the one thing in it that is not a table:
the *Profit by month* chart, drawn in `#78E3A4`. So the ground is that chart —
twelve faint bars rising along the foot of the frame at the real heights the
demo year reaches, three of them still at zero because the year is not over.
The paper is its section mint `#E0F3E8` opened up, and the pills are filled with
the chart green itself, which is what keeps this frame apart from the two other
listings in the same family.

Bars belong to this listing alone: the full tracker's frame is vertical column
bands, the invoice's is horizontal section bands, and the estimate's is a
manila docket.
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

PAPER_HI = (246, 251, 248)
PAPER_LO = (216, 235, 225)
CHART    = (120, 227, 164)      # 78E3A4 — the colour the workbook draws profit in
HAIR     = (190, 216, 202)
INK      = (27, 67, 50)
STEEL    = (46, 88, 74)
DEEP     = (18, 58, 42)
MUTED    = (118, 142, 128)
WIN_BAR  = (230, 241, 235)
WIN_BODY = (255, 255, 255)
EDGE     = (186, 212, 197)
PILL_TX  = (112, 134, 122)

# the demo year's own profit by month, which is what the bars are
MONTHS = [33.71, 106.26, 93.83, 191.00, 126.30, 70.38, 175.89, 132.64, 30.72, 0, 0, 0]

def f(name, size): return ImageFont.truetype(os.path.join(FONTS, name), size)
PF700 = lambda s: f("PlayfairDisplay-700.ttf", s)
M400  = lambda s: f("Montserrat-400.ttf", s)
M500  = lambda s: f("Montserrat-500.ttf", s)
M600  = lambda s: f("Montserrat-600.ttf", s)
M700  = lambda s: f("Montserrat-700.ttf", s)

TABS = ["Items", "Summary"]
TAB_Y, TAB_H = 886, 32

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
    fnt, tr = M600(13), 1.1
    widths = [d.textlength(t.upper(), font=fnt) + tr * (len(t) - 1) + 32 for t in TABS]
    gap = 10
    x = (S - (sum(widths) + gap * (len(TABS) - 1))) / 2
    boxes = []
    for w in widths:
        boxes.append((x, w)); x += w + gap
    return fnt, boxes, tr

# ---------------------------------------------------------------- background
bg = gradient((S, S), PAPER_HI, PAPER_LO)

# the chart, as the ground: twelve bars along the foot, at the year's own heights
lay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
ld = ImageDraw.Draw(lay)
BASE, TALL = S, 232
top_val = max(MONTHS)
slot = S / len(MONTHS)
for i, v in enumerate(MONTHS):
    h = 5 + (TALL - 5) * (v / top_val)
    x0 = i * slot + slot * 0.10
    x1 = (i + 1) * slot - slot * 0.10
    ld.rectangle([x0, BASE - h, x1, BASE], fill=CHART + (62,))
    ld.rectangle([x0, BASE - h, x1, BASE - h + 3], fill=CHART + (120,))
ld.line([(0, BASE - TALL - 46), (S, BASE - TALL - 46)], fill=HAIR + (120,))
bg = Image.alpha_composite(bg.convert("RGBA"), lay.filter(ImageFilter.GaussianBlur(0.6))).convert("RGB")
d = ImageDraw.Draw(bg)
d.line([(0, 156), (S, 156)], fill=HAIR, width=1)

draw_tracked(d, S / 2, 40, "TWO SHEETS · ITEMS · SUMMARY · GOOGLE SHEETS & EXCEL",
             M600(15), MUTED, tr=2.8)
draw_tracked(d, S / 2, 68, "Simple Reseller Tracker", PF700(54), INK, tr=0.5)

sh = Image.new("L", (S, S), 0)
ImageDraw.Draw(sh).rounded_rectangle([WIN[0] + 4, WIN[1] + 12, WIN[2] + 4, WIN[3] + 16],
                                     radius=18, fill=58)
bg.paste(Image.new("RGB", (S, S), (78, 116, 94)), (0, 0), sh.filter(ImageFilter.GaussianBlur(22)))
d = ImageDraw.Draw(bg)

d.rounded_rectangle(list(WIN), radius=18, fill=WIN_BODY, outline=EDGE, width=2)
d.rounded_rectangle([WIN[0], WIN[1], WIN[2], WIN[1] + BAR_H + 18], radius=18, fill=WIN_BAR)
d.rectangle([WIN[0], WIN[1] + BAR_H - 4, WIN[2], WIN[1] + BAR_H], fill=WIN_BAR)
d.line([(WIN[0], WIN[1] + BAR_H), (WIN[2], WIN[1] + BAR_H)], fill=EDGE, width=2)
for cx in (WIN[0] + 26, WIN[0] + 46, WIN[0] + 66):
    d.ellipse([cx - 5, WIN[1] + 20, cx + 5, WIN[1] + 30], fill=(180, 206, 190))
d.rounded_rectangle([WIN[0] + 92, WIN[1] + 14, WIN[0] + 520, WIN[1] + 36], radius=11, fill=(239, 246, 242))
d.text((WIN[0] + 108, WIN[1] + 25), "reseller-tracker-simple", font=M500(13), fill=(132, 156, 142),
       anchor="lm")
chip = "TYPE IN THE BLUE CELLS"
chip_w = d.textlength(chip, font=M700(12)) + 1.6 * (len(chip) - 1) + 26
d.rounded_rectangle([WIN[2] - 20 - chip_w, WIN[1] + 14, WIN[2] - 20, WIN[1] + 36], radius=11, fill=CHART)
draw_tracked(d, WIN[2] - 20 - chip_w / 2, WIN[1] + 18, chip, M700(12), DEEP, tr=1.6)

d.rectangle([SCREEN[0], SCREEN[1], SCREEN[0] + SCREEN[2], SCREEN[1] + SCREEN[3]], fill=WIN_BODY)
d.rectangle([SCREEN[0] - 1, SCREEN[1] - 1, SCREEN[0] + SCREEN[2] + 1, SCREEN[1] + SCREEN[3] + 1],
            outline=(198, 220, 206), width=1)

fnt_tab, boxes, TR = tab_layout(d)
for (x, w), label in zip(boxes, TABS):
    d.rounded_rectangle([x, TAB_Y, x + w, TAB_Y + TAB_H], radius=TAB_H / 2,
                        fill=(237, 245, 240), outline=EDGE, width=1)
    draw_tracked(d, x + w / 2, TAB_Y + 8, label.upper(), fnt_tab, PILL_TX, tr=TR)

draw_tracked(d, S / 2, 948, "ADD WHAT IT SOLD FOR — THE FEE AND THE PROFIT FILL THEMSELVES IN",
             M600(15), INK, tr=1.3)
draw_tracked(d, S / 2, 978,
             "eBay · Poshmark · Mercari · Depop · Vinted · Whatnot · Etsy · by month · by platform",
             M400(12), MUTED, tr=0.3)
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
    "Two sheets — type in the blue cells",
    "One row per item, sold or not",
    "Pick the platform…",
    "…and the fee and the profit fill in",
    "Profit, sales, stock — and the fees behind them",
    "Every month, totalled",
    "And which platform actually pays",
]
for i, caption in enumerate(CAPTIONS, 1):
    lay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    cd = ImageDraw.Draw(lay)
    size = 30 if len(caption) < 30 else (27 if len(caption) < 40 else 24)
    pad_w = tw(cd, caption, M500(size), 0.3) + 46
    cd.rounded_rectangle([(S - pad_w) / 2, 182, (S + pad_w) / 2, 182 + size + 22],
                         radius=(size + 22) / 2, fill=(253, 255, 254, 226), outline=HAIR + (210,))
    draw_tracked(cd, S / 2, 191, caption, M500(size), STEEL + (255,), tr=0.3)
    lay.save(os.path.join(OUT, f"cap{i}.png"))

probe = ImageDraw.Draw(Image.new("RGB", (S, S)))
fnt_tab, boxes, TR = tab_layout(probe)
for i, tab in enumerate(TABS, 1):
    pill = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pill)
    x, w = boxes[i - 1]
    pd.rounded_rectangle([x, TAB_Y, x + w, TAB_Y + TAB_H], radius=TAB_H / 2, fill=CHART + (255,))
    draw_tracked(pd, x + w / 2, TAB_Y + 9, tab.upper(), fnt_tab, DEEP + (255,), tr=TR)
    pill.save(os.path.join(OUT, f"pill{i}.png"))

Image.new("RGBA", (S, 5), (38, 132, 88, 255)).save(os.path.join(OUT, "bar.png"))
print("layers ->", OUT)
