"""Design layers for the dark-theme Annual Budget video (1080x1080).

Palette sampled from the recording itself: sheet background #0B0E19, panels
#141729, accent green #7BFFA2, white type. The frame sits a shade lighter and
bluer than the sheet so the screen reads as a window on a page.
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

BG_HI   = (22, 31, 56)
BG_LO   = (9, 13, 26)
ACCENT  = (123, 255, 162)
TEXT    = (234, 243, 240)
MUTED   = (139, 158, 190)
WIN_BAR = (26, 35, 62)
WIN_BODY= (11, 14, 25)
EDGE    = (44, 57, 92)
PILL_TX = (147, 164, 194)

def f(name, size): return ImageFont.truetype(os.path.join(FONTS, name), size)
PF700 = lambda s: f("PlayfairDisplay-700.ttf", s)
M400  = lambda s: f("Montserrat-400.ttf", s)
M500  = lambda s: f("Montserrat-500.ttf", s)
M600  = lambda s: f("Montserrat-600.ttf", s)
M700  = lambda s: f("Montserrat-700.ttf", s)

TABS = ["Start Here", "Setup", "Transactions", "Dashboard", "50-30-20",
        "Spending", "Month View", "Bills", "Net Worth"]
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
    for size, pad, gap in ((13, 13, 7), (12, 12, 6), (11, 11, 5), (10, 10, 5)):
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

# ---------------------------------------------------------------- background
bg = gradient((S, S), BG_HI, BG_LO)
d = ImageDraw.Draw(bg)

# green glow behind the window, so the dark screen sits in light
glow = Image.new("L", (S, S), 0)
ImageDraw.Draw(glow).ellipse([80, 300, 1000, 900], fill=42)
bg.paste(Image.new("RGB", (S, S), ACCENT), (0, 0), glow.filter(ImageFilter.GaussianBlur(120)))
halo = Image.new("L", (S, S), 0)
ImageDraw.Draw(halo).ellipse([-60, 120, 1140, 820], fill=30)
bg.paste(Image.new("RGB", (S, S), (90, 120, 200)), (0, 0), halo.filter(ImageFilter.GaussianBlur(110)))

draw_tracked(d, S / 2, 44, "GOOGLE SHEETS & EXCEL  ·  INSTANT DOWNLOAD", M600(16), MUTED, tr=4.0)
draw_tracked(d, S / 2, 76, "The Annual Budget", PF700(62), TEXT, tr=0.5)

# window
d.rounded_rectangle(list(WIN), radius=18, fill=WIN_BODY, outline=EDGE, width=2)
d.rounded_rectangle([WIN[0], WIN[1], WIN[2], WIN[1] + BAR_H + 18], radius=18, fill=WIN_BAR)
d.rectangle([WIN[0], WIN[1] + BAR_H - 4, WIN[2], WIN[1] + BAR_H], fill=WIN_BAR)
d.line([(WIN[0], WIN[1] + BAR_H), (WIN[2], WIN[1] + BAR_H)], fill=EDGE, width=2)
for cx in (WIN[0] + 26, WIN[0] + 46, WIN[0] + 66):
    d.ellipse([cx - 5, WIN[1] + 20, cx + 5, WIN[1] + 30], fill=(58, 74, 116))
d.rounded_rectangle([WIN[0] + 92, WIN[1] + 14, WIN[0] + 520, WIN[1] + 36], radius=11, fill=(17, 23, 42))
d.text((WIN[0] + 108, WIN[1] + 25), "annual-budget-2026", font=M500(13), fill=(104, 124, 160), anchor="lm")
chip_w = d.textlength("UPDATES ITSELF", font=M700(12)) + 1.6 * 13 + 26
d.rounded_rectangle([WIN[2] - 20 - chip_w, WIN[1] + 14, WIN[2] - 20, WIN[1] + 36], radius=11, fill=ACCENT)
draw_tracked(d, WIN[2] - 20 - chip_w / 2, WIN[1] + 18, "UPDATES ITSELF", M700(12), (8, 20, 14), tr=1.6)

d.rectangle([SCREEN[0], SCREEN[1], SCREEN[0] + SCREEN[2], SCREEN[1] + SCREEN[3]], fill=WIN_BODY)
d.rectangle([SCREEN[0] - 1, SCREEN[1] - 1, SCREEN[0] + SCREEN[2] + 1, SCREEN[1] + SCREEN[3] + 1],
            outline=(38, 50, 82), width=1)

fnt_tab, boxes = tab_layout(d)
for (x, w), label in zip(boxes, TABS):
    d.rounded_rectangle([x, TAB_Y, x + w, TAB_Y + TAB_H], radius=TAB_H / 2,
                        fill=(19, 26, 46), outline=EDGE, width=1)
    draw_tracked(d, x + w / 2, TAB_Y + 9, label.upper(), fnt_tab, PILL_TX, tr=1.1)

draw_tracked(d, S / 2, 950, "ONE LOG FEEDS THE WHOLE YEAR — NO TAB PER MONTH", M600(15), TEXT, tr=2.6)
draw_tracked(d, S / 2, 980, "9 tabs · every formula already written · yours to edit", M400(14), MUTED, tr=0.6)
d.rectangle([0, S - 5, S, S], fill=(26, 36, 62))
bg.save(os.path.join(OUT, "bg.png"))

# ---------------------------------------------------------------- foreground
fg = Image.new("RGBA", (S, S), (0, 0, 0, 0))
x0, y0, w, h = SCREEN
mask = Image.new("L", (w, h), 255)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=6, fill=0)
corner = Image.new("RGBA", (w, h), WIN_BODY + (255,)); corner.putalpha(mask)
fg.alpha_composite(corner, (x0, y0))
glare = Image.new("L", (w, h), 0)
ImageDraw.Draw(glare).polygon([(0, 0), (int(w * 0.40), 0), (0, h)], fill=16)
gl = Image.new("RGBA", (w, h), (255, 255, 255, 255))
gl.putalpha(glare.filter(ImageFilter.GaussianBlur(30)))
fg.alpha_composite(gl, (x0, y0))
fg.save(os.path.join(OUT, "fg.png"))

# ---------------------------------------------------------------- scenes
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
fnt_tab, boxes = tab_layout(probe)
for i, (caption, tab) in enumerate(SCENES, 1):
    lay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    cd = ImageDraw.Draw(lay)
    draw_tracked(cd, S / 2, 178, caption, M500(30 if len(caption) < 30 else 27), TEXT + (255,), tr=0.3)
    lay.save(os.path.join(OUT, f"cap{i}.png"))

    pill = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pill)
    x, w = boxes[TABS.index(tab)]
    pd.rounded_rectangle([x, TAB_Y, x + w, TAB_Y + TAB_H], radius=TAB_H / 2, fill=ACCENT + (255,))
    draw_tracked(pd, x + w / 2, TAB_Y + 9, tab.upper(), fnt_tab, (8, 20, 14, 255), tr=1.1)
    pill.save(os.path.join(OUT, f"pill{i}.png"))

Image.new("RGBA", (S, 5), ACCENT + (255,)).save(os.path.join(OUT, "bar.png"))
print("layers ->", OUT)
