"""Design layers for the Budget Planner video — 1080x1080.

This workbook is one white page with a bright green chart, so the frame is the
lightest of the listings: near-white paper, a single green sweep low-left and a
cooler one top-right, a fine grid, and the workbook's own #7DFFA4 as the accent.
No mesh of mint and cream — that belongs to the debt listing, and the blue-grey
paper belongs to the paycheck one.
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
LEFT   = 84

PAPER   = (252, 253, 251)
GREEN   = (125, 255, 164)      # 7DFFA4 — the chart's own green
GREEN_D = (38, 166, 106)
MINTBOX = (221, 244, 239)      # DDF4EF — the KPI card on the sheet
COOL    = (232, 240, 246)
INK     = (30, 58, 47)
MUTED   = (122, 146, 134)
RULE    = (214, 232, 222)
WIN_BAR = (245, 249, 246)
WIN_BODY= (255, 255, 255)
EDGE    = (216, 233, 223)
PILL_TX = (128, 154, 140)

def F(n, s): return ImageFont.truetype(os.path.join(FONTS, n), s)
PF700 = lambda s: F("PlayfairDisplay-700.ttf", s)
M400  = lambda s: F("Montserrat-400.ttf", s)
M500  = lambda s: F("Montserrat-500.ttf", s)
M600  = lambda s: F("Montserrat-600.ttf", s)
M700  = lambda s: F("Montserrat-700.ttf", s)

TABS = ["Budget", "Log"]
TAB_Y, TAB_H = 886, 32

def tw(d, txt, fnt, tr=0.0):
    return d.textlength(txt, font=fnt) + tr * max(len(txt) - 1, 0)

def draw_tracked(d, cx, y, txt, fnt, fill, tr=0.0):
    asc, _ = fnt.getmetrics()
    x = cx - tw(d, txt, fnt, tr) / 2
    for ch in txt:
        d.text((x, y + asc), ch, font=fnt, fill=fill, anchor="ls")
        x += d.textlength(ch, font=fnt) + tr

def left_tracked(d, x, y, txt, fnt, fill, tr=0.0):
    draw_tracked(d, x + tw(d, txt, fnt, tr) / 2, y, txt, fnt, fill, tr)

def tab_layout(d):
    """Two tabs only — the product is two sheets, so the strip says so."""
    fnt = M600(13)
    widths = [d.textlength(t.upper(), font=fnt) + 1.1 * (len(t) - 1) + 30 for t in TABS]
    gap = 10
    total = sum(widths) + gap * (len(TABS) - 1)
    x = (S - total) / 2
    boxes = []
    for t, w in zip(TABS, widths):
        boxes.append((x, w)); x += w + gap
    return fnt, boxes

def blob(base, colour, cx, cy, r, alpha, blur):
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).ellipse([cx - r, cy - r, cx + r, cy + r], fill=alpha)
    base.paste(Image.new("RGB", (S, S), colour), (0, 0), m.filter(ImageFilter.GaussianBlur(blur)))

# ---------------------------------------------------------------- background
bg = Image.new("RGB", (S, S), PAPER)
blob(bg, GREEN,   90, 1010, 620, 120, 200)     # green sweep, low-left
blob(bg, MINTBOX, 520, 1040, 620, 150, 210)
blob(bg, COOL,   1010,  90, 560, 190, 190)     # cool corner, top-right
bg = bg.filter(ImageFilter.GaussianBlur(0.4))

grid = Image.new("RGBA", (S, S), (0, 0, 0, 0))
gd = ImageDraw.Draw(grid)
STEP = 54
for i in range(0, S + 1, STEP):
    heavy = (i // STEP) % 4 == 0
    col = (255, 255, 255, 170) if not heavy else (176, 206, 188, 60)
    gd.line([(i, 0), (i, S)], fill=col, width=1)
    gd.line([(0, i), (S, i)], fill=col, width=1)
bg = Image.alpha_composite(bg.convert("RGBA"), grid).convert("RGB")

arc = Image.new("RGBA", (S, S), (0, 0, 0, 0))
ad = ImageDraw.Draw(arc)
ad.ellipse([760, 840, 1500, 1580], outline=GREEN_D + (60,), width=10)
ad.ellipse([840, 900, 1420, 1480], outline=GREEN_D + (34,), width=4)
ad.ellipse([880, -180, 1300, 240], outline=GREEN_D + (46,), width=7)
bg = Image.alpha_composite(bg.convert("RGBA"), arc.filter(ImageFilter.GaussianBlur(0.6))).convert("RGB")

d = ImageDraw.Draw(bg)

sh = Image.new("L", (S, S), 0)
ImageDraw.Draw(sh).rounded_rectangle([WIN[0] + 18, WIN[1] + 34, WIN[2] - 18, WIN[3] + 16], radius=28, fill=88)
bg.paste(Image.new("RGB", (S, S), (126, 158, 140)), (0, 0), sh.filter(ImageFilter.GaussianBlur(36)))

d.rounded_rectangle([LEFT, 48, LEFT + 6, 168], radius=3, fill=GREEN_D)
left_tracked(d, LEFT + 34, 50, "ONE PAGE  ·  TWO SHEETS  ·  GOOGLE SHEETS & EXCEL", M600(16), MUTED, 3.4)
d.text((LEFT + 34, 82), "Budget Planner", font=PF700(62), fill=INK)

# ---- window
d.rounded_rectangle(list(WIN), radius=18, fill=WIN_BODY, outline=EDGE, width=2)
d.rounded_rectangle([WIN[0], WIN[1], WIN[2], WIN[1] + BAR_H + 18], radius=18, fill=WIN_BAR)
d.rectangle([WIN[0], WIN[1] + BAR_H - 4, WIN[2], WIN[1] + BAR_H], fill=WIN_BAR)
d.line([(WIN[0], WIN[1] + BAR_H), (WIN[2], WIN[1] + BAR_H)], fill=EDGE, width=2)
for cx in (WIN[0] + 26, WIN[0] + 46, WIN[0] + 66):
    d.ellipse([cx - 5, WIN[1] + 20, cx + 5, WIN[1] + 30], fill=(206, 228, 214))
d.rounded_rectangle([WIN[0] + 92, WIN[1] + 14, WIN[0] + 520, WIN[1] + 36], radius=11,
                    fill=(255, 255, 255), outline=(228, 240, 232), width=1)
d.text((WIN[0] + 108, WIN[1] + 25), "budget-planner-2026", font=M500(13), fill=(158, 180, 166), anchor="lm")
chip = "TYPE IN THE BLUE CELLS"
chip_w = d.textlength(chip, font=M700(12)) + 1.6 * (len(chip) - 1) + 26
d.rounded_rectangle([WIN[2] - 20 - chip_w, WIN[1] + 14, WIN[2] - 20, WIN[1] + 36], radius=11, fill=INK)
draw_tracked(d, WIN[2] - 20 - chip_w / 2, WIN[1] + 18, chip, M700(12), GREEN, tr=1.6)

d.rectangle([SCREEN[0], SCREEN[1], SCREEN[0] + SCREEN[2], SCREEN[1] + SCREEN[3]], fill=WIN_BODY)
d.rectangle([SCREEN[0] - 1, SCREEN[1] - 1, SCREEN[0] + SCREEN[2] + 1, SCREEN[1] + SCREEN[3] + 1],
            outline=(226, 240, 232), width=1)

fnt_tab, boxes = tab_layout(d)
for (x, w), label in zip(boxes, TABS):
    d.rounded_rectangle([x, TAB_Y, x + w, TAB_Y + TAB_H], radius=TAB_H / 2,
                        fill=(255, 255, 255), outline=RULE, width=1)
    draw_tracked(d, x + w / 2, TAB_Y + 9, label.upper(), fnt_tab, PILL_TX, tr=1.1)

left_tracked(d, LEFT + 26, 950, "ONE PAGE DOES ALL OF IT — THE SECOND SHEET IS JUST THE LOG", M600(15), INK, 1.6)
left_tracked(d, LEFT + 26, 980, "plan vs actual · bills · funds · debts · all in one view", M400(14), MUTED, 0.6)
d.rectangle([0, S - 5, S, S], fill=(224, 240, 230))
bg.save(os.path.join(OUT, "bg.png"))

# ---------------------------------------------------------------- foreground
fg = Image.new("RGBA", (S, S), (0, 0, 0, 0))
x0, y0, w, h = SCREEN
mask = Image.new("L", (w, h), 255)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=6, fill=0)
corner = Image.new("RGBA", (w, h), WIN_BODY + (255,)); corner.putalpha(mask)
fg.alpha_composite(corner, (x0, y0))
fg.save(os.path.join(OUT, "fg.png"))

# ---------------------------------------------------------------- captions
# The captions are timed against the film, not against shots: the page scrolls
# through one uncut take, and the line over it changes while it moves.
CAPTIONS = [
    "Everything on one page",
    "Plan vs actual · bills · funds · debts",
    "One screen. No tab hopping.",
    "Pick a month…",
    "…and the whole page re-does itself",
    "The second sheet is just the log",
]
for i, caption in enumerate(CAPTIONS, 1):
    lay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    cd = ImageDraw.Draw(lay)
    size = 30 if len(caption) < 30 else (27 if len(caption) < 40 else 24)
    cd.text((118, 190), caption, font=M500(size), fill=INK + (255,))
    lay.save(os.path.join(OUT, f"cap{i}.png"))

probe = ImageDraw.Draw(Image.new("RGB", (S, S)))
fnt_tab, boxes = tab_layout(probe)
for i, tab in enumerate(TABS, 1):
    pill = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pill)
    x, w = boxes[i-1]
    pd.rounded_rectangle([x, TAB_Y, x + w, TAB_Y + TAB_H], radius=TAB_H / 2, fill=INK + (255,))
    draw_tracked(pd, x + w / 2, TAB_Y + 9, tab.upper(), fnt_tab, GREEN + (255,), tr=1.1)
    pill.save(os.path.join(OUT, f"pill{i}.png"))

Image.new("RGBA", (S, 5), GREEN_D + (255,)).save(os.path.join(OUT, "bar.png"))
print("layers ->", OUT)
