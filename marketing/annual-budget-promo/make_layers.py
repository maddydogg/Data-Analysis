"""Design layers for the Annual Budget Etsy video (1080x1080).

Palette is taken from AnnualBudgetSpreadsheet.xlsx and from the live recording:
  DFF3EA / DCF0E6  mint section headers (lead accent)
  33566B / 325064  heading text          3E7CC0 / 4678B4  input + chart blue
  78FAA0           chart green
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, sys

OUT   = sys.argv[1] if len(sys.argv) > 1 else "layers"
FONTS = sys.argv[2] if len(sys.argv) > 2 else "fonts"
os.makedirs(OUT, exist_ok=True)

S = 1080
SCREEN = (60, 300, 960, 540)              # x, y, w, h — video goes here
WIN    = (46, 250, 1034, 854)             # window frame
BAR_H  = 50                               # window title bar

MINT_HI = (244, 251, 247)
MINT_LO = (211, 238, 225)
MINT    = (223, 243, 234)
INK     = (51, 86, 107)
MUTED   = (126, 151, 148)
RULE    = (185, 223, 205)
GREEN   = (111, 227, 154)
WIN_BAR = (233, 244, 238)
WIN_EDGE= (196, 222, 208)

def f(name, size): return ImageFont.truetype(os.path.join(FONTS, name), size)
PF700 = lambda s: f("PlayfairDisplay-700.ttf", s)
M400  = lambda s: f("Montserrat-400.ttf", s)
M500  = lambda s: f("Montserrat-500.ttf", s)
M600  = lambda s: f("Montserrat-600.ttf", s)
M700  = lambda s: f("Montserrat-700.ttf", s)

# short forms of the nine real tab names, so the whole strip fits on one row
TABS = ["Start Here", "Setup", "Transactions", "Dashboard", "50-30-20",
        "Spending", "Month View", "Bills", "Net Worth"]

def tracked_width(d, txt, fnt, tr=0.0):
    return d.textlength(txt, font=fnt) + tr * max(len(txt) - 1, 0)

def draw_tracked(d, cx, y, txt, fnt, fill, tr=0.0):
    """Centred text on a shared baseline (letter-spacing never bounces glyphs)."""
    asc, _ = fnt.getmetrics()
    x = cx - tracked_width(d, txt, fnt, tr) / 2
    for ch in txt:
        d.text((x, y + asc), ch, font=fnt, fill=fill, anchor="ls")
        x += d.textlength(ch, font=fnt) + tr

def gradient(size, top, bottom):
    img = Image.new("RGB", (1, size[1]))
    p = ImageDraw.Draw(img)
    for y in range(size[1]):
        t = y / (size[1] - 1)
        p.point((0, y), tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return img.resize(size, Image.BICUBIC)

# ---------------------------------------------------------------- tab strip geometry
def tab_layout(d):
    """Fit all nine tab pills on one row; shrink the type until they fit."""
    for size, pad, gap in ((13, 13, 7), (12, 12, 6), (11, 11, 5), (10, 10, 5)):
        fnt = M600(size)
        widths = [d.textlength(t.upper(), font=fnt) + 1.1 * (len(t) - 1) + pad * 2 for t in TABS]
        total = sum(widths) + gap * (len(TABS) - 1)
        if total <= 1012:
            x = (S - total) / 2
            boxes = []
            for t, w in zip(TABS, widths):
                boxes.append((x, w))
                x += w + gap
            return fnt, boxes, pad
    raise RuntimeError("tabs do not fit")

TAB_Y, TAB_H = 886, 32

# ---------------------------------------------------------------- background
bg = gradient((S, S), MINT_HI, MINT_LO)
d = ImageDraw.Draw(bg)

halo = Image.new("L", (S, S), 0)
ImageDraw.Draw(halo).ellipse([-40, 200, 1120, 900], fill=78)
bg.paste(Image.new("RGB", (S, S), (255, 255, 255)), (0, 0), halo.filter(ImageFilter.GaussianBlur(80)))

sh = Image.new("L", (S, S), 0)
ImageDraw.Draw(sh).rounded_rectangle([WIN[0] + 16, WIN[1] + 30, WIN[2] - 16, WIN[3] + 12], radius=26, fill=88)
bg.paste(Image.new("RGB", (S, S), (132, 172, 154)), (0, 0), sh.filter(ImageFilter.GaussianBlur(34)))

draw_tracked(d, S / 2, 44, "GOOGLE SHEETS & EXCEL  ·  INSTANT DOWNLOAD", M600(16), MUTED, tr=4.0)
draw_tracked(d, S / 2, 76, "The Annual Budget", PF700(62), INK, tr=0.5)

# window
d.rounded_rectangle(list(WIN), radius=18, fill=(255, 255, 255), outline=WIN_EDGE, width=2)
d.rounded_rectangle([WIN[0], WIN[1], WIN[2], WIN[1] + BAR_H + 18], radius=18, fill=WIN_BAR)
d.rectangle([WIN[0], WIN[1] + BAR_H - 4, WIN[2], WIN[1] + BAR_H], fill=WIN_BAR)
d.line([(WIN[0], WIN[1] + BAR_H), (WIN[2], WIN[1] + BAR_H)], fill=WIN_EDGE, width=2)
for i, cx in enumerate((WIN[0] + 26, WIN[0] + 46, WIN[0] + 66)):
    d.ellipse([cx - 5, WIN[1] + 20, cx + 5, WIN[1] + 30], fill=(198, 220, 208))
# address-style pill + "updates itself" chip
d.rounded_rectangle([WIN[0] + 92, WIN[1] + 14, WIN[0] + 520, WIN[1] + 36], radius=11, fill=(255, 255, 255))
dd = ImageDraw.Draw(bg)
dd.text((WIN[0] + 108, WIN[1] + 25), "annual-budget-2026", font=M500(13), fill=(150, 176, 168), anchor="lm")
chip_w = d.textlength("UPDATES ITSELF", font=M700(12)) + 1.6 * 13 + 26
d.rounded_rectangle([WIN[2] - 20 - chip_w, WIN[1] + 14, WIN[2] - 20, WIN[1] + 36], radius=11, fill=INK)
draw_tracked(d, WIN[2] - 20 - chip_w / 2, WIN[1] + 18, "UPDATES ITSELF", M700(12), MINT, tr=1.6)
# screen well, with a hairline so the screenshot separates from the window
d.rectangle([SCREEN[0], SCREEN[1], SCREEN[0] + SCREEN[2], SCREEN[1] + SCREEN[3]], fill=(255, 255, 255))
d.rectangle([SCREEN[0] - 1, SCREEN[1] - 1, SCREEN[0] + SCREEN[2] + 1, SCREEN[1] + SCREEN[3] + 1],
            outline=(220, 234, 227), width=1)

# inactive tab pills
fnt_tab, boxes, pad = tab_layout(d)
for (x, w), label in zip(boxes, TABS):
    d.rounded_rectangle([x, TAB_Y, x + w, TAB_Y + TAB_H], radius=TAB_H / 2,
                        fill=(255, 255, 255), outline=RULE, width=1)
    draw_tracked(d, x + w / 2, TAB_Y + 9, label.upper(), fnt_tab, (150, 176, 168), tr=1.1)

draw_tracked(d, S / 2, 950, "ONE LOG FEEDS THE WHOLE YEAR — NO TAB PER MONTH",
             M600(15), INK, tr=2.6)
draw_tracked(d, S / 2, 980, "9 tabs · every formula already written · yours to edit",
             M400(14), MUTED, tr=0.6)
d.rectangle([0, S - 5, S, S], fill=(226, 240, 232))          # progress track
bg.save(os.path.join(OUT, "bg.png"))

# ---------------------------------------------------------------- foreground
fg = Image.new("RGBA", (S, S), (0, 0, 0, 0))
x0, y0, w, h = SCREEN
mask = Image.new("L", (w, h), 255)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=6, fill=0)
corner = Image.new("RGBA", (w, h), (255, 255, 255, 255))
corner.putalpha(mask)
fg.alpha_composite(corner, (x0, y0))
glare = Image.new("L", (w, h), 0)
ImageDraw.Draw(glare).polygon([(0, 0), (int(w * 0.38), 0), (0, h)], fill=20)
gl = Image.new("RGBA", (w, h), (255, 255, 255, 255))
gl.putalpha(glare.filter(ImageFilter.GaussianBlur(30)))
fg.alpha_composite(gl, (x0, y0))
fg.save(os.path.join(OUT, "fg.png"))

# ---------------------------------------------------------------- per-scene overlays
SCENES = [
    ("Set it up once",                    "Setup"),
    ("Log it once — the year fills in",   "Transactions"),
    ("Your whole year on one screen",     "Dashboard"),
    ("See where the money actually goes", "Dashboard"),
    ("Charts build themselves",           "Dashboard"),
    ("50 / 30 / 20, checked for you",     "50-30-20"),
    ("Every category, ranked",            "Spending"),
    ("Any month on its own",              "Month View"),
    ("The true cost of every bill",       "Bills"),
    ("Savings goals and net worth",       "Net Worth"),
]
probe = ImageDraw.Draw(Image.new("RGB", (S, S)))
fnt_tab, boxes, pad = tab_layout(probe)
for i, (caption, tab) in enumerate(SCENES, 1):
    lay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    cd = ImageDraw.Draw(lay)
    size = 30 if len(caption) < 30 else 27
    draw_tracked(cd, S / 2, 178, caption, M500(size), INK + (255,), tr=0.3)
    lay.save(os.path.join(OUT, f"cap{i}.png"))

    # the lit tab pill lives on its own layer so it can outlast the caption and
    # hand over to the next tab during the cross-fade
    pill = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pill)
    x, w = boxes[TABS.index(tab)]
    pd.rounded_rectangle([x, TAB_Y, x + w, TAB_Y + TAB_H], radius=TAB_H / 2, fill=INK + (255,))
    draw_tracked(pd, x + w / 2, TAB_Y + 9, tab.upper(), fnt_tab, MINT + (255,), tr=1.1)
    pill.save(os.path.join(OUT, f"pill{i}.png"))

# progress bar: a full-width bar slid in from the left by the filter graph
bar = Image.new("RGBA", (S, 5), GREEN + (255,))
bar.save(os.path.join(OUT, "bar.png"))
print("layers ->", OUT)
