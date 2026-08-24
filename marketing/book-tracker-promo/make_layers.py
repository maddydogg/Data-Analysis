"""Render the static design layers for the Etsy promo video (1080x1080)."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "layers"
FONTS = sys.argv[2] if len(sys.argv) > 2 else "fonts"
os.makedirs(OUT, exist_ok=True)

S = 1080
SCREEN = (96, 318, 888, 500)          # x, y, w, h of the laptop screen
BEZEL_TOP, BEZEL_BOTTOM = 300, 852
BEZEL_X0, BEZEL_X1 = 78, 1002

CREAM   = (250, 246, 239)
SAGE    = (228, 237, 227)
INK     = (28, 54, 44)
MUTED   = (110, 138, 114)
CAPTION = (44, 74, 60)
BEZEL   = (36, 38, 43)
CHIN    = (26, 28, 32)
BASE    = (66, 70, 78)
BADGE   = (47, 107, 79)

def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)

PF700 = lambda s: font("PlayfairDisplay-700.ttf", s)
PF500 = lambda s: font("PlayfairDisplay-500.ttf", s)
M400  = lambda s: font("Montserrat-400.ttf", s)
M500  = lambda s: font("Montserrat-500.ttf", s)
M600  = lambda s: font("Montserrat-600.ttf", s)
M700  = lambda s: font("Montserrat-700.ttf", s)


def text_width(draw, txt, fnt, tracking=0):
    w = draw.textlength(txt, font=fnt)
    return w + tracking * max(len(txt) - 1, 0)


def draw_tracked(draw, cx, y, txt, fnt, fill, tracking=0.0):
    """Centred text with optional letter-spacing.

    `y` is the top of the line box; every glyph is placed on a shared baseline
    so letter-spacing never makes the characters bounce.
    """
    ascent, _ = fnt.getmetrics()
    baseline = y + ascent
    total = text_width(draw, txt, fnt, tracking)
    x = cx - total / 2
    for ch in txt:
        draw.text((x, baseline), ch, font=fnt, fill=fill, anchor="ls")
        x += draw.textlength(ch, font=fnt) + tracking


def gradient(size, top, bottom):
    img = Image.new("RGB", (1, size[1]))
    d = ImageDraw.Draw(img)
    for y in range(size[1]):
        t = y / (size[1] - 1)
        d.point((0, y), tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return img.resize(size, Image.BICUBIC)


# ---------------------------------------------------------------- background
bg = gradient((S, S), CREAM, SAGE)
d = ImageDraw.Draw(bg)

# soft halo behind the laptop
halo = Image.new("L", (S, S), 0)
ImageDraw.Draw(halo).ellipse([40, 250, 1040, 940], fill=70)
halo = halo.filter(ImageFilter.GaussianBlur(70))
bg.paste(Image.new("RGB", (S, S), (255, 255, 255)), (0, 0), halo)

# drop shadow under the laptop
sh = Image.new("L", (S, S), 0)
ImageDraw.Draw(sh).rounded_rectangle([110, 700, 970, 900], radius=90, fill=95)
sh = sh.filter(ImageFilter.GaussianBlur(38))
bg.paste(Image.new("RGB", (S, S), (120, 132, 120)), (0, 0), sh)

# ---- header type
draw_tracked(d, S / 2, 58, "GOOGLE SHEETS  ·  INSTANT DOWNLOAD", M600(17), MUTED, tracking=4.2)
draw_tracked(d, S / 2, 96, "The Reading Tracker", PF700(66), INK, tracking=0.5)

# thin rule under the headline
d.line([(S / 2 - 60, 186), (S / 2 + 60, 186)], fill=(178, 197, 180), width=2)

# ---- laptop body
d.rounded_rectangle([BEZEL_X0, BEZEL_TOP, BEZEL_X1, BEZEL_BOTTOM], radius=22, fill=BEZEL)
d.rounded_rectangle([BEZEL_X0 + 1, BEZEL_TOP + 1, BEZEL_X1 - 1, BEZEL_BOTTOM - 1],
                    radius=22, outline=(70, 74, 82), width=2)
# chin
d.rounded_rectangle([BEZEL_X0, BEZEL_BOTTOM - 40, BEZEL_X1, BEZEL_BOTTOM], radius=22, fill=CHIN)
d.rectangle([BEZEL_X0, BEZEL_BOTTOM - 40, BEZEL_X1, BEZEL_BOTTOM - 28], fill=CHIN)
draw_tracked(d, S / 2, BEZEL_BOTTOM - 27, "BOOK TRACKER", M500(11), (150, 158, 152), tracking=3.0)
# camera dot
d.ellipse([S / 2 - 3, BEZEL_TOP + 7, S / 2 + 3, BEZEL_TOP + 13], fill=(78, 82, 90))
# screen well (video is overlaid here)
d.rectangle([SCREEN[0], SCREEN[1], SCREEN[0] + SCREEN[2], SCREEN[1] + SCREEN[3]], fill=(255, 255, 255))
# base
d.rounded_rectangle([BEZEL_X0 - 52, BEZEL_BOTTOM, BEZEL_X1 + 52, BEZEL_BOTTOM + 18], radius=9, fill=BASE)
d.rounded_rectangle([S / 2 - 62, BEZEL_BOTTOM, S / 2 + 62, BEZEL_BOTTOM + 7], radius=4, fill=(52, 56, 63))

# ---- footer
d.line([(150, 928), (930, 928)], fill=(196, 211, 196), width=2)
draw_tracked(d, S / 2, 950, "8 TABS  ·  DASHBOARD  ·  BOOKSHELF  ·  TRACKER  ·  TBR  ·  WISHLIST  ·  SERIES",
             M600(16), (74, 97, 81), tracking=2.4)
draw_tracked(d, S / 2, 992, "NO SETUP — JUST MAKE A COPY AND START LOGGING",
             M500(15), MUTED, tracking=2.0)
bg.save(os.path.join(OUT, "bg.png"))

# ---------------------------------------------------------------- foreground
fg = Image.new("RGBA", (S, S), (0, 0, 0, 0))
fd = ImageDraw.Draw(fg)

# rounded screen corners: paint bezel-coloured wedges over the video corners
corner = 10
x0, y0, w, h = SCREEN
x1, y1 = x0 + w, y0 + h
mask = Image.new("L", (w, h), 255)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=corner, fill=0)
wedge = Image.new("RGBA", (w, h), BEZEL + (255,))
wedge.putalpha(mask)
fg.alpha_composite(wedge, (x0, y0))

# subtle screen glare
glare = Image.new("L", (w, h), 0)
ImageDraw.Draw(glare).polygon([(0, 0), (int(w * 0.42), 0), (0, h)], fill=26)
glare = glare.filter(ImageFilter.GaussianBlur(26))
gl = Image.new("RGBA", (w, h), (255, 255, 255, 255))
gl.putalpha(glare)
fg.alpha_composite(gl, (x0, y0))

# ---- badge
bcx, bcy, r = 922, 812, 88
fd.ellipse([bcx - r - 9, bcy - r - 9, bcx + r + 9, bcy + r + 9], fill=(255, 255, 255, 235))
fd.ellipse([bcx - r, bcy - r, bcx + r, bcy + r], fill=BADGE + (255,))
fd.ellipse([bcx - r + 9, bcy - r + 9, bcx + r - 9, bcy + r - 9], outline=(214, 232, 214, 200), width=2)
stars = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
draw_tracked(fd, bcx, bcy - 50, "\u2605 \u2605 \u2605", stars, (206, 228, 206), tracking=3.0)
for i, line in enumerate(("AUTO-", "UPDATING")):
    draw_tracked(fd, bcx, bcy - 30 + i * 31, line, M700(24), (255, 255, 255), tracking=0.5)
draw_tracked(fd, bcx, bcy + 38, "DASHBOARD", M600(14), (206, 228, 206), tracking=2.4)
fg.save(os.path.join(OUT, "fg.png"))

# ---------------------------------------------------------------- captions
CAPTIONS = [
    "A dashboard that fills itself in",
    "Log a book in seconds — dropdowns do the work",
    "Every book becomes a colour-coded spine",
    "Charts and stats build themselves",
    "Edit every list — make it yours",
]
for i, txt in enumerate(CAPTIONS, 1):
    cap = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cap)
    size = 30 if len(txt) < 42 else 27
    draw_tracked(cd, S / 2, 212, txt, M500(size), CAPTION + (255,), tracking=0.4)
    cap.save(os.path.join(OUT, f"cap{i}.png"))

print("layers written to", OUT)
