"""Design layers for the Estimate & Invoice listing video (1080x1080).

Its own ground: a manila job docket. Kraft paper with the fibre still in it, a
label band across the head where the title is written, and a folded corner
bottom right — the thing a trade actually carries the job on. The accent is the
deep teal the workbook writes its own section headers in, so the frame and the
sheet inside it agree.

Three pills, because the film walks Estimate -> Invoice -> Job Log, and the
captions are the sheet's own words, one per beat.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, sys, random

OUT   = sys.argv[1] if len(sys.argv) > 1 else "layers"
FONTS = sys.argv[2] if len(sys.argv) > 2 else "fonts"
os.makedirs(OUT, exist_ok=True)

S = 1080
SCREEN = (60, 300, 960, 540)
WIN    = (46, 250, 1034, 854)
BAR_H  = 50

PAPER_HI = (241, 231, 211)     # manila, lit from the top left
PAPER_LO = (223, 208, 180)
KRAFT    = (213, 195, 163)
INK      = (39, 46, 46)
ACCENT   = (15, 94, 82)        # 0F5E52 — the sheet's own section green
MUTED    = (127, 114, 92)
WIN_BAR  = (232, 221, 199)
WIN_BODY = (255, 255, 255)
EDGE     = (191, 173, 141)
PILL_TX  = (118, 105, 84)

def f(name, size): return ImageFont.truetype(os.path.join(FONTS, name), size)
PF700 = lambda s: f("PlayfairDisplay-700.ttf", s)
M400  = lambda s: f("Montserrat-400.ttf", s)
M500  = lambda s: f("Montserrat-500.ttf", s)
M600  = lambda s: f("Montserrat-600.ttf", s)
M700  = lambda s: f("Montserrat-700.ttf", s)

TABS = ["Estimate", "Invoice", "Job Log"]
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

# paper fibre: short pale and dark flecks, never a regular grain
random.seed(1001)
fib = Image.new("RGBA", (S, S), (0, 0, 0, 0))
fd = ImageDraw.Draw(fib)
for _ in range(2600):
    x, y = random.randrange(S), random.randrange(S)
    ln = random.randint(2, 9)
    dark = random.random() < 0.55
    c = (96, 80, 58, random.randint(8, 20)) if dark else (255, 250, 236, random.randint(10, 26))
    fd.line([(x, y), (x + ln, y + random.randint(-1, 1))], fill=c)
bg = Image.alpha_composite(bg.convert("RGBA"), fib.filter(ImageFilter.GaussianBlur(0.4))).convert("RGB")

d = ImageDraw.Draw(bg)

# the label band the title is written on, and the rule that closes it
band = Image.new("RGBA", (S, S), (0, 0, 0, 0))
bd = ImageDraw.Draw(band)
bd.rectangle([0, 0, S, 150], fill=(255, 250, 238, 46))
band = band.filter(ImageFilter.GaussianBlur(0.6))
bg = Image.alpha_composite(bg.convert("RGBA"), band).convert("RGB")
d = ImageDraw.Draw(bg)
d.line([(70, 150), (S - 70, 150)], fill=KRAFT, width=1)

d.line([(70, 154), (S - 70, 154)], fill=(236, 227, 208), width=1)

draw_tracked(d, S / 2, 44, "FOR TRADES  ·  GOOGLE SHEETS & EXCEL  ·  PRINT OR SEND AS PDF",
             M600(15), MUTED, tr=2.8)
draw_tracked(d, S / 2, 72, "Estimate & Invoice", PF700(62), INK, tr=0.5)

# the window sits on the paper, so it casts a real shadow
sh = Image.new("L", (S, S), 0)
ImageDraw.Draw(sh).rounded_rectangle([WIN[0] + 6, WIN[1] + 12, WIN[2] + 6, WIN[3] + 16],
                                     radius=18, fill=70)
bg.paste(Image.new("RGB", (S, S), (108, 92, 68)), (0, 0), sh.filter(ImageFilter.GaussianBlur(22)))
d = ImageDraw.Draw(bg)

d.rounded_rectangle(list(WIN), radius=18, fill=WIN_BODY, outline=EDGE, width=2)
d.rounded_rectangle([WIN[0], WIN[1], WIN[2], WIN[1] + BAR_H + 18], radius=18, fill=WIN_BAR)
d.rectangle([WIN[0], WIN[1] + BAR_H - 4, WIN[2], WIN[1] + BAR_H], fill=WIN_BAR)
d.line([(WIN[0], WIN[1] + BAR_H), (WIN[2], WIN[1] + BAR_H)], fill=EDGE, width=2)
for cx in (WIN[0] + 26, WIN[0] + 46, WIN[0] + 66):
    d.ellipse([cx - 5, WIN[1] + 20, cx + 5, WIN[1] + 30], fill=(198, 180, 148))
d.rounded_rectangle([WIN[0] + 92, WIN[1] + 14, WIN[0] + 520, WIN[1] + 36], radius=11, fill=(244, 236, 219))
d.text((WIN[0] + 108, WIN[1] + 25), "redline-home-repairs-2026", font=M500(13), fill=(146, 130, 104),
       anchor="lm")
chip = "EST-1001  →  INV-2003"
chip_w = d.textlength(chip, font=M700(12)) + 1.6 * (len(chip) - 1) + 26
d.rounded_rectangle([WIN[2] - 20 - chip_w, WIN[1] + 14, WIN[2] - 20, WIN[1] + 36], radius=11, fill=ACCENT)
draw_tracked(d, WIN[2] - 20 - chip_w / 2, WIN[1] + 18, chip, M700(12), (240, 248, 244), tr=1.6)

d.rectangle([SCREEN[0], SCREEN[1], SCREEN[0] + SCREEN[2], SCREEN[1] + SCREEN[3]], fill=WIN_BODY)
d.rectangle([SCREEN[0] - 1, SCREEN[1] - 1, SCREEN[0] + SCREEN[2] + 1, SCREEN[1] + SCREEN[3] + 1],
            outline=(205, 189, 158), width=1)

fnt_tab, boxes, TR = tab_layout(d)
for (x, w), label in zip(boxes, TABS):
    d.rounded_rectangle([x, TAB_Y, x + w, TAB_Y + TAB_H], radius=TAB_H / 2,
                        fill=(233, 222, 200), outline=EDGE, width=1)
    draw_tracked(d, x + w / 2, TAB_Y + 8, label.upper(), fnt_tab, PILL_TX, tr=TR)

draw_tracked(d, S / 2, 950, "ONE PAGE PER JOB — LABOUR, MATERIALS, TOTALS AND THE BALANCE DUE",
             M600(15), INK, tr=1.4)
draw_tracked(d, S / 2, 980, "rate card  ·  your cost & markup  ·  deposit  ·  quoted / invoiced / paid",
             M400(14), MUTED, tr=0.6)

# folded corner, bottom right — the docket has been in a van
fold = Image.new("RGBA", (S, S), (0, 0, 0, 0))
fl = ImageDraw.Draw(fold)
fl.polygon([(S, S - 94), (S, S), (S - 94, S)], fill=(196, 178, 146, 255))
fl.polygon([(S, S - 94), (S - 94, S), (S - 74, S - 74)], fill=(248, 240, 224, 255))
bg = Image.alpha_composite(bg.convert("RGBA"), fold.filter(ImageFilter.GaussianBlur(0.5))).convert("RGB")
d = ImageDraw.Draw(bg)
d.rectangle([0, S - 5, S, S], fill=(206, 188, 156))
bg.save(os.path.join(OUT, "bg.png"))

# ---------------------------------------------------------------- foreground
fg = Image.new("RGBA", (S, S), (0, 0, 0, 0))
x0, y0, w, h = SCREEN
mask = Image.new("L", (w, h), 255)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=6, fill=0)
corner = Image.new("RGBA", (w, h), WIN_BODY + (255,)); corner.putalpha(mask)
fg.alpha_composite(corner, (x0, y0))
glare = Image.new("L", (w, h), 0)
ImageDraw.Draw(glare).polygon([(0, 0), (int(w * 0.38), 0), (0, h)], fill=13)
gl = Image.new("RGBA", (w, h), (255, 255, 255, 255))
gl.putalpha(glare.filter(ImageFilter.GaussianBlur(30)))
fg.alpha_composite(gl, (x0, y0))
fg.save(os.path.join(OUT, "fg.png"))

# ---------------------------------------------------------------- captions
CAPTIONS = [
    "Everything for one job, on one page",
    "Labour, materials, totals — one sheet",
    "Pick the rate type. It re-prices itself.",
    "The same job, now an invoice",
    "Deposit off. Balance due, ready to send.",
    "Mark it invoiced — the job log keeps score",
]
for i, caption in enumerate(CAPTIONS, 1):
    lay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    cd = ImageDraw.Draw(lay)
    size = 30 if len(caption) < 30 else (27 if len(caption) < 40 else 24)
    pad_w = tw(cd, caption, M500(size), 0.3) + 44
    cd.rounded_rectangle([(S - pad_w) / 2, 172, (S + pad_w) / 2, 172 + size + 22],
                         radius=(size + 22) / 2, fill=(247, 240, 226, 214), outline=(206, 188, 156, 190))
    draw_tracked(cd, S / 2, 181, caption, M500(size), INK + (255,), tr=0.3)
    lay.save(os.path.join(OUT, f"cap{i}.png"))

probe = ImageDraw.Draw(Image.new("RGB", (S, S)))
fnt_tab, boxes, TR = tab_layout(probe)
for i, tab in enumerate(TABS, 1):
    pill = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pill)
    x, w = boxes[i - 1]
    pd.rounded_rectangle([x, TAB_Y, x + w, TAB_Y + TAB_H], radius=TAB_H / 2, fill=ACCENT + (255,))
    draw_tracked(pd, x + w / 2, TAB_Y + 9, tab.upper(), fnt_tab, (242, 249, 245, 255), tr=TR)
    pill.save(os.path.join(OUT, f"pill{i}.png"))

Image.new("RGBA", (S, 5), ACCENT + (255,)).save(os.path.join(OUT, "bar.png"))
print("layers ->", OUT)
