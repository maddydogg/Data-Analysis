"""Design layers for the ADHD Planner video — 1080x1080.

The product's whole argument is calm: three things not ten, no streaks to lose.
So this is the quietest frame of the listings — near-white paper, one soft mint
wash, a thin rule, and nothing else. No rings, no arcs, no sticker. The mint is
the workbook's own #E0F3EA section band and the accent its bright habit-grid
green; the type sits in the deep green those two imply.

The competitor for this product sells a giant all-in-one dashboard on a lavender
gradient with a sticker slapped over it, and explains none of the six screens it
shows. The answer here is the opposite on every axis: name the audience in the
kicker, caption every beat in the sheet's own words, and keep the crops large
enough to read.
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

PAPER   = (253, 253, 251)
BAND    = (224, 243, 234)      # E0F3EA — the sheet's own section band
GREEN   = (125, 255, 164)      # the habit grid's green
GREEN_D = (34, 148, 96)
CREAM   = (252, 250, 244)
INK     = (26, 61, 46)
MUTED   = (122, 148, 134)
RULE    = (214, 234, 223)
WIN_BAR = (246, 251, 248)
WIN_BODY= (255, 255, 255)
EDGE    = (218, 236, 226)
PILL_TX = (128, 156, 140)

def F(n, s): return ImageFont.truetype(os.path.join(FONTS, n), s)
PF700 = lambda s: F("PlayfairDisplay-700.ttf", s)
M400  = lambda s: F("Montserrat-400.ttf", s)
M500  = lambda s: F("Montserrat-500.ttf", s)
M600  = lambda s: F("Montserrat-600.ttf", s)
M700  = lambda s: F("Montserrat-700.ttf", s)

TABS = ["Today", "Tasks", "Habits"]
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
    fnt = M600(13)
    tr = 1.1
    widths = [d.textlength(t.upper(), font=fnt) + tr * (len(t) - 1) + 30 for t in TABS]
    gap = 10
    total = sum(widths) + gap * (len(TABS) - 1)
    x = (S - total) / 2
    boxes = []
    for t, w in zip(TABS, widths):
        boxes.append((x, w)); x += w + gap
    return fnt, boxes, tr

def blob(base, colour, cx, cy, r, alpha, blur):
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).ellipse([cx - r, cy - r, cx + r, cy + r], fill=alpha)
    base.paste(Image.new("RGB", (S, S), colour), (0, 0), m.filter(ImageFilter.GaussianBlur(blur)))

# ---------------------------------------------------------------- background
bg = Image.new("RGB", (S, S), PAPER)
blob(bg, BAND,  120, 1000, 640, 150, 210)      # one mint wash, low-left
blob(bg, CREAM, 990,  110, 520, 150, 190)      # a warm corner, nothing more
bg = bg.filter(ImageFilter.GaussianBlur(0.4))
d = ImageDraw.Draw(bg)

sh = Image.new("L", (S, S), 0)
ImageDraw.Draw(sh).rounded_rectangle([WIN[0] + 18, WIN[1] + 34, WIN[2] - 18, WIN[3] + 16], radius=28, fill=80)
bg.paste(Image.new("RGB", (S, S), (132, 158, 144)), (0, 0), sh.filter(ImageFilter.GaussianBlur(36)))
d = ImageDraw.Draw(bg)

d.rounded_rectangle([LEFT, 48, LEFT + 6, 168], radius=3, fill=GREEN_D)
left_tracked(d, LEFT + 34, 50, "THREE SHEETS  ·  TODAY  ·  TASKS  ·  HABITS", M600(16), MUTED, 3.4)
d.text((LEFT + 34, 82), "ADHD Planner", font=PF700(62), fill=INK)

# ---- window
d.rounded_rectangle(list(WIN), radius=18, fill=WIN_BODY, outline=EDGE, width=2)
d.rounded_rectangle([WIN[0], WIN[1], WIN[2], WIN[1] + BAR_H + 18], radius=18, fill=WIN_BAR)
d.rectangle([WIN[0], WIN[1] + BAR_H - 4, WIN[2], WIN[1] + BAR_H], fill=WIN_BAR)
d.line([(WIN[0], WIN[1] + BAR_H), (WIN[2], WIN[1] + BAR_H)], fill=EDGE, width=2)
for cx in (WIN[0] + 26, WIN[0] + 46, WIN[0] + 66):
    d.ellipse([cx - 5, WIN[1] + 20, cx + 5, WIN[1] + 30], fill=(208, 230, 218))
d.rounded_rectangle([WIN[0] + 92, WIN[1] + 14, WIN[0] + 520, WIN[1] + 36], radius=11,
                    fill=(255, 255, 255), outline=(230, 242, 235), width=1)
d.text((WIN[0] + 108, WIN[1] + 25), "adhd-planner-2026", font=M500(13), fill=(160, 182, 170), anchor="lm")
chip = "TYPE IN THE BLUE CELLS"
chip_w = d.textlength(chip, font=M700(12)) + 1.6 * (len(chip) - 1) + 26
d.rounded_rectangle([WIN[2] - 20 - chip_w, WIN[1] + 14, WIN[2] - 20, WIN[1] + 36], radius=11, fill=INK)
draw_tracked(d, WIN[2] - 20 - chip_w / 2, WIN[1] + 18, chip, M700(12), GREEN, tr=1.6)

d.rectangle([SCREEN[0], SCREEN[1], SCREEN[0] + SCREEN[2], SCREEN[1] + SCREEN[3]], fill=WIN_BODY)
d.rectangle([SCREEN[0] - 1, SCREEN[1] - 1, SCREEN[0] + SCREEN[2] + 1, SCREEN[1] + SCREEN[3] + 1],
            outline=(228, 242, 234), width=1)

fnt_tab, boxes, TR = tab_layout(d)
for (x, w), label in zip(boxes, TABS):
    d.rounded_rectangle([x, TAB_Y, x + w, TAB_Y + TAB_H], radius=TAB_H / 2,
                        fill=(255, 255, 255), outline=RULE, width=1)
    draw_tracked(d, x + w / 2, TAB_Y + 9, label.upper(), fnt_tab, PILL_TX, tr=TR)

left_tracked(d, LEFT + 26, 950, "THREE THINGS, NOT TEN — AND NOTHING BREAKS IF YOU MISS A DAY",
             M600(15), INK, 1.5)
left_tracked(d, LEFT + 26, 980, "today · tasks · habits · brain dump · dopamine menu · yours to edit",
             M400(14), MUTED, 0.6)
d.rectangle([0, S - 5, S, S], fill=(226, 242, 233))
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
# The sheet's own words. Timed against the film, so a line can change while the
# page keeps moving under it.
CAPTIONS = [
    "Three things, not ten",
    "Quick wins — two minutes each",
    "Brain dump. Dopamine menu.",
    "Break one big task into steps",
    "One row per task — set the energy",
    "Park it — nothing breaks",
    "One per day. No streaks to lose.",
]
for i, caption in enumerate(CAPTIONS, 1):
    lay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    cd = ImageDraw.Draw(lay)
    size = 30 if len(caption) < 30 else (27 if len(caption) < 40 else 24)
    cd.text((118, 190), caption, font=M500(size), fill=INK + (255,))
    lay.save(os.path.join(OUT, f"cap{i}.png"))

probe = ImageDraw.Draw(Image.new("RGB", (S, S)))
fnt_tab, boxes, TR = tab_layout(probe)
for i, tab in enumerate(TABS, 1):
    pill = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pill)
    x, w = boxes[i-1]
    pd.rounded_rectangle([x, TAB_Y, x + w, TAB_Y + TAB_H], radius=TAB_H / 2, fill=INK + (255,))
    draw_tracked(pd, x + w / 2, TAB_Y + 9, tab.upper(), fnt_tab, GREEN + (255,), tr=TR)
    pill.save(os.path.join(OUT, f"pill{i}.png"))

Image.new("RGBA", (S, 5), GREEN_D + (255,)).save(os.path.join(OUT, "bar.png"))
print("layers ->", OUT)
