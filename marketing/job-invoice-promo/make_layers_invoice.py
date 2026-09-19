"""Design layers for the Job Invoice listing video (1080x1080).

The ground is taken straight out of the workbook, as asked: its section bands
are #E0F3E8, its headers are written in the slate #3E5058 and its values in a
steel blue near #38566A. So the frame is built the way the sheet itself is —
full-width mint bands separated by paper, one of them carrying the title — and
nothing in it is a colour the file does not already use.

That band device is this listing's alone: the mesh belongs to the debt video,
the blue-grey paper to the paycheck one, the green sweeps to the budget planner,
the single mint wash to the ADHD planner, the ledger ruling to the bookkeeping
one and the manila docket to the estimate one.
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

PAPER_HI = (243, 249, 245)
PAPER_LO = (211, 229, 219)
BAND     = (224, 243, 232)      # E0F3E8 — the workbook's own section band
BAND_LN  = (183, 214, 196)
INK      = (47, 66, 72)         # deepened 3E5058, its header type
STEEL    = (56, 86, 106)        # 38566A, the colour its values are written in
ACCENT   = (45, 106, 87)
MUTED    = (120, 142, 135)
WIN_BAR  = (228, 241, 234)
WIN_BODY = (255, 255, 255)
EDGE     = (183, 211, 196)
PILL_TX  = (108, 130, 122)

def f(name, size): return ImageFont.truetype(os.path.join(FONTS, name), size)
PF700 = lambda s: f("PlayfairDisplay-700.ttf", s)
M400  = lambda s: f("Montserrat-400.ttf", s)
M500  = lambda s: f("Montserrat-500.ttf", s)
M600  = lambda s: f("Montserrat-600.ttf", s)
M700  = lambda s: f("Montserrat-700.ttf", s)

TABS   = ["Start Here", "Setup", "Invoice"]
ACTIVE = [1, 2]                  # only Setup and Invoice are ever on screen
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
    widths = [d.textlength(t.upper(), font=fnt) + tr * (len(t) - 1) + 30 for t in TABS]
    gap = 10
    x = (S - (sum(widths) + gap * (len(TABS) - 1))) / 2
    boxes = []
    for w in widths:
        boxes.append((x, w)); x += w + gap
    return fnt, boxes, tr

# ---------------------------------------------------------------- background
bg = gradient((S, S), PAPER_HI, PAPER_LO)

# the sheet's own device: full-width section bands, each closed by a hairline.
# (top, height, opacity) — the second one is the band the title is written on.
bands = [(0, 26, 150), (62, 96, 255), (188, 28, 120), (868, 132, 200), (1028, 52, 110)]
lay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
ld = ImageDraw.Draw(lay)
for top, h, alpha in bands:
    ld.rectangle([0, top, S, top + h], fill=BAND + (alpha,))
    ld.line([(0, top), (S, top)], fill=BAND_LN + (min(255, alpha + 40),))
bg = Image.alpha_composite(bg.convert("RGBA"), lay.filter(ImageFilter.GaussianBlur(0.4))).convert("RGB")
d = ImageDraw.Draw(bg)

draw_tracked(d, S / 2, 44, "SET IT UP ONCE  ·  GOOGLE SHEETS & EXCEL  ·  PRINT OR SEND AS PDF",
             M600(15), MUTED, tr=2.6)
draw_tracked(d, S / 2, 72, "Job Invoice", PF700(62), INK, tr=0.5)

# the window sits on the paper and casts a shadow the colour of the paper's dark
sh = Image.new("L", (S, S), 0)
ImageDraw.Draw(sh).rounded_rectangle([WIN[0] + 4, WIN[1] + 12, WIN[2] + 4, WIN[3] + 16],
                                     radius=18, fill=62)
bg.paste(Image.new("RGB", (S, S), (86, 118, 104)), (0, 0), sh.filter(ImageFilter.GaussianBlur(22)))
d = ImageDraw.Draw(bg)

d.rounded_rectangle(list(WIN), radius=18, fill=WIN_BODY, outline=EDGE, width=2)
d.rounded_rectangle([WIN[0], WIN[1], WIN[2], WIN[1] + BAR_H + 18], radius=18, fill=WIN_BAR)
d.rectangle([WIN[0], WIN[1] + BAR_H - 4, WIN[2], WIN[1] + BAR_H], fill=WIN_BAR)
d.line([(WIN[0], WIN[1] + BAR_H), (WIN[2], WIN[1] + BAR_H)], fill=EDGE, width=2)
for cx in (WIN[0] + 26, WIN[0] + 46, WIN[0] + 66):
    d.ellipse([cx - 5, WIN[1] + 20, cx + 5, WIN[1] + 30], fill=(180, 208, 193))
d.rounded_rectangle([WIN[0] + 92, WIN[1] + 14, WIN[0] + 520, WIN[1] + 36], radius=11, fill=(239, 247, 242))
d.text((WIN[0] + 108, WIN[1] + 25), "job-invoice-2026", font=M500(13), fill=(134, 158, 148), anchor="lm")
chip = "INV-2003  ·  JOB-1001"
chip_w = d.textlength(chip, font=M700(12)) + 1.6 * (len(chip) - 1) + 26
d.rounded_rectangle([WIN[2] - 20 - chip_w, WIN[1] + 14, WIN[2] - 20, WIN[1] + 36], radius=11, fill=ACCENT)
draw_tracked(d, WIN[2] - 20 - chip_w / 2, WIN[1] + 18, chip, M700(12), (238, 247, 242), tr=1.6)

d.rectangle([SCREEN[0], SCREEN[1], SCREEN[0] + SCREEN[2], SCREEN[1] + SCREEN[3]], fill=WIN_BODY)
d.rectangle([SCREEN[0] - 1, SCREEN[1] - 1, SCREEN[0] + SCREEN[2] + 1, SCREEN[1] + SCREEN[3] + 1],
            outline=(198, 221, 208), width=1)

fnt_tab, boxes, TR = tab_layout(d)
for (x, w), label in zip(boxes, TABS):
    d.rounded_rectangle([x, TAB_Y, x + w, TAB_Y + TAB_H], radius=TAB_H / 2,
                        fill=(236, 245, 240), outline=EDGE, width=1)
    draw_tracked(d, x + w / 2, TAB_Y + 8, label.upper(), fnt_tab, PILL_TX, tr=TR)

draw_tracked(d, S / 2, 950, "SET YOUR RATES ONCE — EVERY INVOICE PRICES ITSELF", M600(15), INK, tr=1.4)
draw_tracked(d, S / 2, 980,
             "hourly · after hours · weekend · flat rate · materials with markup · balance due",
             M400(13), MUTED, tr=0.4)
d.rectangle([0, S - 5, S, S], fill=(196, 221, 207))
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
    "Fill this in once — everything reads from here",
    "Switch a line to a flat price…",
    "…and it asks for the price, not the hours",
    "Pick the rate type — the subtotal moves with it",
    "One page per job",
    "Deposit off. Balance due, ready to send.",
]
for i, caption in enumerate(CAPTIONS, 1):
    lay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    cd = ImageDraw.Draw(lay)
    size = 30 if len(caption) < 30 else (27 if len(caption) < 40 else 24)
    pad_w = tw(cd, caption, M500(size), 0.3) + 46
    cd.rounded_rectangle([(S - pad_w) / 2, 182, (S + pad_w) / 2, 182 + size + 22],
                         radius=(size + 22) / 2, fill=(252, 254, 253, 222), outline=BAND_LN + (200,))
    draw_tracked(cd, S / 2, 191, caption, M500(size), STEEL + (255,), tr=0.3)
    lay.save(os.path.join(OUT, f"cap{i}.png"))

probe = ImageDraw.Draw(Image.new("RGB", (S, S)))
fnt_tab, boxes, TR = tab_layout(probe)
for n, idx in enumerate(ACTIVE, 1):
    pill = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pill)
    x, w = boxes[idx]
    pd.rounded_rectangle([x, TAB_Y, x + w, TAB_Y + TAB_H], radius=TAB_H / 2, fill=ACCENT + (255,))
    draw_tracked(pd, x + w / 2, TAB_Y + 9, TABS[idx].upper(), fnt_tab, (240, 248, 244, 255), tr=TR)
    pill.save(os.path.join(OUT, f"pill{n}.png"))

Image.new("RGBA", (S, 5), ACCENT + (255,)).save(os.path.join(OUT, "bar.png"))
print("layers ->", OUT)
