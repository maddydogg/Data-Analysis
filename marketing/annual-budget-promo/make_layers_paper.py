"""Design layers for the light couples video — paper frame (1080x1080).

Everything is drawn from the workbook's own light palette: mint section headers
DFF3EA, the pale cyan E4F3F6, near-white FBFAFD, slate type 33566B / 36576A and
the bright chart green 7BFFA2. The ground is a soft mesh of those tints with a
faint spreadsheet grid over it and a green arc sweeping out of one corner, so it
reads as paper rather than a flat fill.
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

PAPER   = (244, 250, 246)
MINT    = (205, 234, 218)      # shade of DFF3EA
CYAN    = (216, 234, 244)      # shade of E4F3F6
CREAM   = (250, 246, 235)
GREEN   = (123, 255, 162)      # 7BFFA2 — straight off the sheet
GREEN_D = (60, 186, 122)
INK     = (42, 74, 92)         # near 33566B / 36576A
MUTED   = (110, 142, 127)
RULE    = (198, 224, 209)
WIN_BAR = (240, 246, 242)
WIN_BODY= (255, 255, 255)
EDGE    = (208, 228, 216)
PILL_TX = (124, 154, 139)

def F(n, s): return ImageFont.truetype(os.path.join(FONTS, n), s)
PF700 = lambda s: F("PlayfairDisplay-700.ttf", s)
M400  = lambda s: F("Montserrat-400.ttf", s)
M500  = lambda s: F("Montserrat-500.ttf", s)
M600  = lambda s: F("Montserrat-600.ttf", s)
M700  = lambda s: F("Montserrat-700.ttf", s)

TABS = ["Start Here", "Setup", "Transactions", "Dashboard", "50-30-20",
        "Spending", "Split & Settle", "Month View", "Bills", "Net Worth"]
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
    for size, pad, gap in ((13, 13, 7), (12, 12, 6), (11, 11, 5), (10, 10, 5), (9, 9, 4)):
        fnt = M600(size)
        widths = [d.textlength(t.upper(), font=fnt) + 1.1 * (len(t) - 1) + pad * 2 for t in TABS]
        total = sum(widths) + gap * (len(TABS) - 1)
        if total <= 1012:
            x = (S - total) / 2
            boxes = []
            for t, w in zip(TABS, widths):
                boxes.append((x, w)); x += w + gap
            return fnt, boxes
    raise RuntimeError("tabs do not fit")

def blob(base, colour, cx, cy, r, alpha, blur):
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).ellipse([cx - r, cy - r, cx + r, cy + r], fill=alpha)
    base.paste(Image.new("RGB", (S, S), colour), (0, 0), m.filter(ImageFilter.GaussianBlur(blur)))

# ---------------------------------------------------------------- background
bg = Image.new("RGB", (S, S), PAPER)
blob(bg, MINT,  150,  120, 620, 210, 190)      # mint wash, top-left
blob(bg, CYAN,  980, 1000, 640, 200, 200)      # pale cyan, bottom-right
blob(bg, CREAM, 1010,  80, 430, 170, 170)      # warm corner
blob(bg, MINT,  540,  980, 520, 120, 210)

# faint spreadsheet grid — the product's own texture, barely there
grid = Image.new("RGBA", (S, S), (0, 0, 0, 0))
gd = ImageDraw.Draw(grid)
STEP = 54
for i in range(0, S + 1, STEP):
    heavy = (i // STEP) % 4 == 0
    col = (255, 255, 255, 150) if not heavy else (176, 208, 190, 70)
    gd.line([(i, 0), (i, S)], fill=col, width=1)
    gd.line([(0, i), (S, i)], fill=col, width=1)
bg = Image.alpha_composite(bg.convert("RGBA"), grid).convert("RGB")

# green arc sweeping out of the bottom-left corner
arc = Image.new("RGBA", (S, S), (0, 0, 0, 0))
ad = ImageDraw.Draw(arc)
# rings live in the two corners the type never reaches
ad.ellipse([700, -280, 1440, 460], outline=GREEN + (105,), width=9)
ad.ellipse([760, -210, 1370, 400], outline=GREEN + (55,), width=4)
ad.ellipse([840, 830, 1520, 1510], outline=GREEN + (110,), width=10)
ad.ellipse([900, -120, 1250, 230], outline=CYAN + (160,), width=6)
bg = Image.alpha_composite(bg.convert("RGBA"), arc.filter(ImageFilter.GaussianBlur(0.6))).convert("RGB")

d = ImageDraw.Draw(bg)

# soft shadow under the window
sh = Image.new("L", (S, S), 0)
ImageDraw.Draw(sh).rounded_rectangle([WIN[0] + 18, WIN[1] + 34, WIN[2] - 18, WIN[3] + 16], radius=28, fill=92)
bg.paste(Image.new("RGB", (S, S), (128, 166, 146)), (0, 0), sh.filter(ImageFilter.GaussianBlur(36)))

# ---- header, left-aligned behind a green rule
d.rounded_rectangle([LEFT, 48, LEFT + 6, 168], radius=3, fill=GREEN_D)
left_tracked(d, LEFT + 34, 50, "FOR COUPLES & HOUSEHOLDS  ·  GOOGLE SHEETS & EXCEL", M600(16), MUTED, 4.0)
d.text((LEFT + 34, 82), "The Annual Budget", font=PF700(62), fill=INK)

# ---- window
d.rounded_rectangle(list(WIN), radius=18, fill=WIN_BODY, outline=EDGE, width=2)
d.rounded_rectangle([WIN[0], WIN[1], WIN[2], WIN[1] + BAR_H + 18], radius=18, fill=WIN_BAR)
d.rectangle([WIN[0], WIN[1] + BAR_H - 4, WIN[2], WIN[1] + BAR_H], fill=WIN_BAR)
d.line([(WIN[0], WIN[1] + BAR_H), (WIN[2], WIN[1] + BAR_H)], fill=EDGE, width=2)
for cx in (WIN[0] + 26, WIN[0] + 46, WIN[0] + 66):
    d.ellipse([cx - 5, WIN[1] + 20, cx + 5, WIN[1] + 30], fill=(202, 224, 210))
d.rounded_rectangle([WIN[0] + 92, WIN[1] + 14, WIN[0] + 520, WIN[1] + 36], radius=11,
                    fill=(255, 255, 255), outline=(226, 238, 231), width=1)
d.text((WIN[0] + 108, WIN[1] + 25), "couples-budget-2026", font=M500(13), fill=(154, 180, 166), anchor="lm")
chip = "SPLITS ITSELF"
chip_w = d.textlength(chip, font=M700(12)) + 1.6 * (len(chip) - 1) + 26
d.rounded_rectangle([WIN[2] - 20 - chip_w, WIN[1] + 14, WIN[2] - 20, WIN[1] + 36], radius=11, fill=INK)
draw_tracked(d, WIN[2] - 20 - chip_w / 2, WIN[1] + 18, chip, M700(12), GREEN, tr=1.6)

d.rectangle([SCREEN[0], SCREEN[1], SCREEN[0] + SCREEN[2], SCREEN[1] + SCREEN[3]], fill=WIN_BODY)
d.rectangle([SCREEN[0] - 1, SCREEN[1] - 1, SCREEN[0] + SCREEN[2] + 1, SCREEN[1] + SCREEN[3] + 1],
            outline=(222, 238, 229), width=1)

# ---- tab strip
fnt_tab, boxes = tab_layout(d)
for (x, w), label in zip(boxes, TABS):
    d.rounded_rectangle([x, TAB_Y, x + w, TAB_Y + TAB_H], radius=TAB_H / 2,
                        fill=(255, 255, 255), outline=RULE, width=1)
    draw_tracked(d, x + w / 2, TAB_Y + 9, label.upper(), fnt_tab, PILL_TX, tr=1.1)

left_tracked(d, LEFT + 26, 950, "ONE LOG FEEDS THE WHOLE YEAR — AND SPLITS IT FAIRLY", M600(15), INK, 2.6)
left_tracked(d, LEFT + 26, 980, "10 tabs · every formula already written · yours to edit", M400(14), MUTED, 0.6)
d.rectangle([0, S - 5, S, S], fill=(222, 238, 229))
bg.save(os.path.join(OUT, "bg.png"))

# ---------------------------------------------------------------- foreground
fg = Image.new("RGBA", (S, S), (0, 0, 0, 0))
x0, y0, w, h = SCREEN
mask = Image.new("L", (w, h), 255)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=6, fill=0)
corner = Image.new("RGBA", (w, h), WIN_BODY + (255,)); corner.putalpha(mask)
fg.alpha_composite(corner, (x0, y0))
fg.save(os.path.join(OUT, "fg.png"))

# ---------------------------------------------------------------- scenes
SCENES = [
    ("Mark who paid and what's shared",   "Transactions"),
    ("Dropdowns do the typing",           "Transactions"),
    ("Your whole year on one screen",     "Dashboard"),
    ("See where the money actually goes", "Dashboard"),
    ("Charts build themselves",           "Dashboard"),
    ("50 / 30 / 20, checked for you",     "50-30-20"),
    ("Every category, ranked",            "Spending"),
    ("Split by income — who owes whom",   "Split & Settle"),
    ("Any month on its own",              "Month View"),
    ("The true cost of every bill",       "Bills"),
    ("Savings goals and net worth",       "Net Worth"),
]
probe = ImageDraw.Draw(Image.new("RGB", (S, S)))
fnt_tab, boxes = tab_layout(probe)
for i, (caption, tab) in enumerate(SCENES, 1):
    lay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    cd = ImageDraw.Draw(lay)
    cd.text((118, 186), caption, font=M500(30 if len(caption) < 30 else 27), fill=INK + (255,))
    lay.save(os.path.join(OUT, f"cap{i}.png"))

    pill = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pill)
    x, w = boxes[TABS.index(tab)]
    pd.rounded_rectangle([x, TAB_Y, x + w, TAB_Y + TAB_H], radius=TAB_H / 2, fill=INK + (255,))
    draw_tracked(pd, x + w / 2, TAB_Y + 9, tab.upper(), fnt_tab, GREEN + (255,), tr=1.1)
    pill.save(os.path.join(OUT, f"pill{i}.png"))

Image.new("RGBA", (S, 5), GREEN_D + (255,)).save(os.path.join(OUT, "bar.png"))
print("layers ->", OUT)
