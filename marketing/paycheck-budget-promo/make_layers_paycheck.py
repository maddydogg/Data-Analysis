"""Design layers for the Paycheck Budget video — 1080x1080, same paper frame as
the other listings, but keyed to this workbook's own palette: the mint section
headers DFF3EA, the pale blue E7ECFA and cyan E4F3F6 of its cards, slate type
33566B and the blue 3E7CC0 its input cells are written in. The debt video's
green never appears here, so the two listings read as siblings, not twins.
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

PAPER   = (246, 249, 252)
MINT    = (223, 243, 234)      # DFF3EA
CYAN    = (224, 240, 245)      # E4F3F6
BLUEW   = (231, 236, 250)      # E7ECFA
CREAM   = (250, 247, 238)
ACC     = (62, 124, 192)       # 3E7CC0 — the workbook's input blue
ACC_D   = (41, 92, 150)
INK     = (43, 74, 92)         # near 33566B
MUTED   = (124, 143, 158)      # near 7B8A99
RULE    = (206, 220, 234)
WIN_BAR = (242, 246, 250)
WIN_BODY= (255, 255, 255)
EDGE    = (212, 226, 238)
PILL_TX = (128, 150, 168)

def F(n, s): return ImageFont.truetype(os.path.join(FONTS, n), s)
PF700 = lambda s: F("PlayfairDisplay-700.ttf", s)
M400  = lambda s: F("Montserrat-400.ttf", s)
M500  = lambda s: F("Montserrat-500.ttf", s)
M600  = lambda s: F("Montserrat-600.ttf", s)
M700  = lambda s: F("Montserrat-700.ttf", s)

TABS = ["Start Here", "Setup", "Dashboard", "Paycheck Budget",
        "Transactions", "Bill Calendar", "Savings", "Debt"]
TAB_Y, TAB_H = 886, 30

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
    """Eight tabs is two more than the other listings carry, so the strip is
    allowed to run smaller before it gives up."""
    for size, pad, gap, tr in ((12, 12, 6, 1.0), (11, 10, 5, 0.9), (10, 9, 5, 0.8),
                               (9, 8, 4, 0.6), (8, 7, 4, 0.5), (8, 6, 3, 0.3)):
        fnt = M600(size)
        widths = [d.textlength(t.upper(), font=fnt) + tr * (len(t) - 1) + pad * 2 for t in TABS]
        total = sum(widths) + gap * (len(TABS) - 1)
        if total <= 1012:
            x = (S - total) / 2
            boxes = []
            for t, w in zip(TABS, widths):
                boxes.append((x, w)); x += w + gap
            return fnt, boxes, tr
    raise RuntimeError("tabs do not fit")

def blob(base, colour, cx, cy, r, alpha, blur):
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).ellipse([cx - r, cy - r, cx + r, cy + r], fill=alpha)
    base.paste(Image.new("RGB", (S, S), colour), (0, 0), m.filter(ImageFilter.GaussianBlur(blur)))

# ---------------------------------------------------------------- background
bg = Image.new("RGB", (S, S), PAPER)
blob(bg, BLUEW, 130,  110, 640, 215, 195)      # pale blue wash, top-left
blob(bg, MINT,  980, 1010, 660, 205, 200)      # mint, bottom-right
blob(bg, CREAM, 1030,  70, 420, 150, 175)      # warm corner
blob(bg, CYAN,  520,  990, 540, 130, 210)

grid = Image.new("RGBA", (S, S), (0, 0, 0, 0))
gd = ImageDraw.Draw(grid)
STEP = 54
for i in range(0, S + 1, STEP):
    heavy = (i // STEP) % 4 == 0
    col = (255, 255, 255, 150) if not heavy else (178, 198, 222, 70)
    gd.line([(i, 0), (i, S)], fill=col, width=1)
    gd.line([(0, i), (S, i)], fill=col, width=1)
bg = Image.alpha_composite(bg.convert("RGBA"), grid).convert("RGB")

arc = Image.new("RGBA", (S, S), (0, 0, 0, 0))
ad = ImageDraw.Draw(arc)
ad.ellipse([700, -280, 1440, 460], outline=ACC + (70,), width=9)
ad.ellipse([760, -210, 1370, 400], outline=ACC + (38,), width=4)
ad.ellipse([840, 830, 1520, 1510], outline=ACC + (72,), width=10)
ad.ellipse([900, -120, 1250, 230], outline=MINT + (200,), width=6)
bg = Image.alpha_composite(bg.convert("RGBA"), arc.filter(ImageFilter.GaussianBlur(0.6))).convert("RGB")

d = ImageDraw.Draw(bg)

sh = Image.new("L", (S, S), 0)
ImageDraw.Draw(sh).rounded_rectangle([WIN[0] + 18, WIN[1] + 34, WIN[2] - 18, WIN[3] + 16], radius=28, fill=92)
bg.paste(Image.new("RGB", (S, S), (140, 158, 180)), (0, 0), sh.filter(ImageFilter.GaussianBlur(36)))

d.rounded_rectangle([LEFT, 48, LEFT + 6, 168], radius=3, fill=ACC)
left_tracked(d, LEFT + 34, 50, "PAYCHECK 1  ·  PAYCHECK 2  ·  GOOGLE SHEETS & EXCEL", M600(16), MUTED, 3.4)
d.text((LEFT + 34, 82), "Paycheck Budget", font=PF700(62), fill=INK)

# ---- window
d.rounded_rectangle(list(WIN), radius=18, fill=WIN_BODY, outline=EDGE, width=2)
d.rounded_rectangle([WIN[0], WIN[1], WIN[2], WIN[1] + BAR_H + 18], radius=18, fill=WIN_BAR)
d.rectangle([WIN[0], WIN[1] + BAR_H - 4, WIN[2], WIN[1] + BAR_H], fill=WIN_BAR)
d.line([(WIN[0], WIN[1] + BAR_H), (WIN[2], WIN[1] + BAR_H)], fill=EDGE, width=2)
for cx in (WIN[0] + 26, WIN[0] + 46, WIN[0] + 66):
    d.ellipse([cx - 5, WIN[1] + 20, cx + 5, WIN[1] + 30], fill=(206, 222, 236))
d.rounded_rectangle([WIN[0] + 92, WIN[1] + 14, WIN[0] + 520, WIN[1] + 36], radius=11,
                    fill=(255, 255, 255), outline=(228, 238, 246), width=1)
d.text((WIN[0] + 108, WIN[1] + 25), "paycheck-budget-2026", font=M500(13), fill=(158, 176, 192), anchor="lm")
chip = "DOES THE MATH"
chip_w = d.textlength(chip, font=M700(12)) + 1.6 * (len(chip) - 1) + 26
d.rounded_rectangle([WIN[2] - 20 - chip_w, WIN[1] + 14, WIN[2] - 20, WIN[1] + 36], radius=11, fill=INK)
draw_tracked(d, WIN[2] - 20 - chip_w / 2, WIN[1] + 18, chip, M700(12), MINT, tr=1.6)

d.rectangle([SCREEN[0], SCREEN[1], SCREEN[0] + SCREEN[2], SCREEN[1] + SCREEN[3]], fill=WIN_BODY)
d.rectangle([SCREEN[0] - 1, SCREEN[1] - 1, SCREEN[0] + SCREEN[2] + 1, SCREEN[1] + SCREEN[3] + 1],
            outline=(224, 236, 246), width=1)

fnt_tab, boxes, TR = tab_layout(d)
for (x, w), label in zip(boxes, TABS):
    d.rounded_rectangle([x, TAB_Y, x + w, TAB_Y + TAB_H], radius=TAB_H / 2,
                        fill=(255, 255, 255), outline=RULE, width=1)
    draw_tracked(d, x + w / 2, TAB_Y + 8, label.upper(), fnt_tab, PILL_TX, tr=TR)

left_tracked(d, LEFT + 26, 950, "TWO PAYCHECKS, TWELVE CATEGORIES — THE MATH IS ALREADY DONE", M600(15), INK, 1.7)
left_tracked(d, LEFT + 26, 980, "8 tabs · budget by paycheck, not by month · yours to edit", M400(14), MUTED, 0.6)
d.rectangle([0, S - 5, S, S], fill=(224, 236, 246))
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
    ("Set it up once — paychecks, categories, funds", "Setup"),
    ("Your month at a glance",                        "Dashboard"),
    ("Where the money actually went",                 "Dashboard"),
    ("Plan each category by paycheck",                "Paycheck Budget"),
    ("Log it once — everything else fills in",        "Transactions"),
    ("Accounts come from a list you set",             "Transactions"),
    ("So do the categories",                          "Transactions"),
    ("Weekly bills, shown as a monthly cost",         "Bill Calendar"),
    ("Sinking funds, with a target each",             "Savings"),
    ("Debts, smallest balance first",                 "Debt"),
]
probe = ImageDraw.Draw(Image.new("RGB", (S, S)))
fnt_tab, boxes, TR = tab_layout(probe)
for i, (caption, tab) in enumerate(SCENES, 1):
    lay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    cd = ImageDraw.Draw(lay)
    size = 30 if len(caption) < 30 else (27 if len(caption) < 40 else 24)
    cd.text((118, 190), caption, font=M500(size), fill=INK + (255,))
    lay.save(os.path.join(OUT, f"cap{i}.png"))

    pill = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pill)
    x, w = boxes[TABS.index(tab)]
    pd.rounded_rectangle([x, TAB_Y, x + w, TAB_Y + TAB_H], radius=TAB_H / 2, fill=INK + (255,))
    draw_tracked(pd, x + w / 2, TAB_Y + 8, tab.upper(), fnt_tab, MINT + (255,), tr=TR)
    pill.save(os.path.join(OUT, f"pill{i}.png"))

Image.new("RGBA", (S, 5), ACC + (255,)).save(os.path.join(OUT, "bar.png"))
print("layers ->", OUT)
