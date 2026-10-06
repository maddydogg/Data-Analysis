"""QuietClueCo listing kit (calendar B, vintage look): reusable helpers for mockups and video.

Every image is built on a `Frame`, which records the text of everything placed on it: the text
layer of each PDF region that is pasted, plus every string drawn by code. The spoiler check reads
those records, so it knows exactly what a buyer could read.
"""
import math, os, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import pymupdf as fitz

# ---------------------------------------------------------------- palette (same as src/art.py)
CREAM = (243, 234, 215); PAPER = (250, 245, 234); PAPER2 = (234, 223, 198)
SEA = (35, 70, 90); SEA2 = (47, 96, 116); NIGHT = (28, 44, 60); NIGHT2 = (44, 66, 84)
RUST = (181, 69, 47); RUST_D = (132, 46, 32); OCHRE = (215, 165, 72); OCHRE_L = (240, 208, 138)
MOSS = (107, 123, 75); INK = (43, 42, 42); SLATE = (91, 102, 112); WHITE = (255, 255, 255); PENCIL = (60, 60, 66)

FONT_DIR = None
def set_font_dir(d):
    global FONT_DIR
    FONT_DIR = d

_fonts = {}
def font(name, size):
    """display = Josefin Sans Bold (poster caps); semi = Josefin SemiBold; body = Nunito; bold = Nunito
    ExtraBold; serif = Fraunces SemiBold; italic = Fraunces Italic; hand = Kalam."""
    key = (name, int(size))
    if key not in _fonts:
        fn = {"display": "JosefinSans-Bold.ttf", "semi": "JosefinSans-SemiBold.ttf", "body": "Nunito-Regular.ttf",
              "bold": "Nunito-ExtraBold.ttf", "serif": "Fraunces-SemiBold.ttf", "italic": "Fraunces-Italic.ttf",
              "hand": "Kalam-Regular.ttf", "handb": "Kalam-Bold.ttf"}[name]
        _fonts[key] = ImageFont.truetype(os.path.join(FONT_DIR, fn), int(size))
    return _fonts[key]

# ---------------------------------------------------------------- PDF pages
class Pdf:
    def __init__(self, path):
        self.path = path
        self.doc = fitz.open(path)
        self._cache = {}

    def find(self, *needles, exclude=("Tap any line to jump",)):
        for i, p in enumerate(self.doc):
            t = p.get_text()
            if all(n in t for n in needles) and not any(e in t for e in exclude):
                return i
        raise KeyError(needles)

    def image(self, index, height, clip=None):
        page = self.doc[index]
        rect = fitz.Rect(clip) if clip else page.rect
        zoom = height / rect.height
        key = (index, height, tuple(rect))
        if key not in self._cache:
            pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=rect, alpha=False)
            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples).convert("RGBA")
            text = page.get_text(clip=rect)
            self._cache[key] = (img, text, zoom, rect)
        img, text, zoom, rect = self._cache[key]
        return PageImg(img.copy(), text, zoom, rect, f"{os.path.basename(self.path)} p{index + 1}")

    def words(self, index):
        return self.doc[index].get_text("words")

class PageImg:
    def __init__(self, img, text, zoom, rect, source):
        self.img, self.text, self.zoom, self.rect, self.source = img, text, zoom, rect, source

    def px(self, x, y):
        return ((x - self.rect.x0) * self.zoom, (y - self.rect.y0) * self.zoom)

# ---------------------------------------------------------------- frames
class Frame:
    def __init__(self, w, h, bg=CREAM):
        self.img = Image.new("RGBA", (w, h), bg + (255,))
        self.sources = []
        self.w, self.h = w, h

    def note(self, kind, source, text):
        self.sources.append((kind, source, text))

    def draw(self):
        return ImageDraw.Draw(self.img)

    def paste_page(self, page, x, y, angle=0, shadow=True, scale=1.0, border=True):
        im = page.img
        if scale != 1.0:
            im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
        if border:
            b = Image.new("RGBA", (im.width + 2, im.height + 2), (205, 196, 176, 255))
            b.paste(im, (1, 1)); im = b
        self.paste(im, x, y, angle, shadow)
        self.note("pdf", page.source, page.text)

    def paste(self, im, x, y, angle=0, shadow=True, shadow_strength=95):
        if angle:
            im = im.rotate(angle, resample=Image.BICUBIC, expand=True)
        if shadow:
            s = max(8, int(min(im.size) * 0.025))
            alpha = im.split()[3]
            sh = Image.new("RGBA", (im.width + 4 * s, im.height + 4 * s), (0, 0, 0, 0))
            mask = Image.new("L", sh.size, 0)
            mask.paste(alpha.point(lambda a: shadow_strength if a > 0 else 0), (2 * s, 2 * s))
            mask = mask.filter(ImageFilter.GaussianBlur(s))
            sh.putalpha(mask)
            self.img.alpha_composite(sh, (int(x - sh.width / 2 + s * 0.5), int(y - sh.height / 2 + s * 1.1)))
        self.img.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))

    def text(self, xy, s, fnt, fill, anchor="la"):
        self.draw().text(xy, s, font=fnt, fill=fill, anchor=anchor)
        self.note("drawn", "text", s)

    def save(self, path):
        self.img.convert("RGB").save(path, optimize=True)

# ---------------------------------------------------------------- drawn elements
def grain(img, amount=14):
    n = Image.effect_noise(img.size, 60).convert("L")
    img.alpha_composite(Image.merge("RGBA", (n, n, n, Image.new("L", img.size, amount))))

def pencil_strike(frame, x0, y, x1, h, col=PENCIL, alpha=170, seed=0, progress=1.0, width=None):
    """A soft pencil line through a row, slightly wobbly. progress<1 draws it part-way (for video)."""
    rng = random.Random(seed)
    layer = Image.new("RGBA", frame.img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    xe = x0 + (x1 - x0) * progress
    pts = []
    for i in range(25):
        t = i / 24
        pts.append((x0 + (xe - x0) * t, y + math.sin(t * 5 + seed) * h * 0.06 + rng.uniform(-1, 1) * h * 0.03))
    d.line(pts, fill=col + (alpha,), width=width or max(2, int(h * 0.16)), joint="curve")
    frame.img.alpha_composite(layer)

def highlight(frame, box, col=OCHRE_L, alpha=140):
    layer = Image.new("RGBA", frame.img.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).rounded_rectangle(box, radius=6, fill=col + (alpha,))
    frame.img.alpha_composite(layer)

def pen_circle(frame, cx, cy, rx, ry, col=RUST, width=7, seed=3, progress=1.0):
    rng = random.Random(seed)
    d = frame.draw()
    turns = 1.1 * progress
    n = max(2, int(90 * turns))
    pts = []
    for i in range(n + 1):
        a = -math.pi / 2 + 2 * math.pi * turns * i / n
        wob = 1 + 0.04 * math.sin(3 * a + seed) + rng.uniform(-0.01, 0.01)
        pts.append((cx + math.cos(a) * rx * wob, cy + math.sin(a) * ry * wob))
    d.line(pts, fill=col, width=width, joint="curve")

def tick(frame, x, y, s, col=RUST, width=None, progress=1.0):
    d = frame.draw(); w = width or max(4, int(s * 0.14))
    a = (x, y); b = (x + s * 0.32, y + s * 0.38); c = (x + s * 0.95, y - s * 0.55)
    if progress <= 0.35:
        t = progress / 0.35
        d.line([a, (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)], fill=col, width=w)
    else:
        t = (progress - 0.35) / 0.65
        d.line([a, b, (b[0] + (c[0] - b[0]) * t, b[1] + (c[1] - b[1]) * t)], fill=col, width=w, joint="curve")

def envelope(w, number, col=PAPER, seal=RUST):
    """A vintage envelope with a wax seal carrying the day number. Returns RGBA."""
    h = int(w * 0.62)
    im = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = 10, 10, w + 10, h + 10
    d.rounded_rectangle((x0, y0, x1, y1), radius=10, fill=col, outline=(205, 190, 160), width=3)
    mx = (x0 + x1) / 2; my = y0 + (y1 - y0) * 0.56
    d.polygon([(x0 + 4, y0 + 4), (mx, my), (x1 - 4, y0 + 4)], fill=(236, 226, 204), outline=(205, 190, 160))
    # stamp corner
    d.rectangle((x1 - w * 0.2, y0 + h * 0.08, x1 - w * 0.06, y0 + h * 0.3), fill=(214, 196, 160), outline=SEA, width=2)
    r = h * 0.17
    d.ellipse((mx - r, my - r, mx + r, my + r), fill=seal)
    d.ellipse((mx - r * 0.78, my - r * 0.78, mx + r * 0.78, my + r * 0.78), outline=(232, 160, 130), width=3)
    d.text((mx, my + r * 0.05), str(number), font=font("display", r * 1.05), fill=CREAM, anchor="mm")
    return im

def ipad(frame, box, screen_page, bezel=(34, 36, 40)):
    x0, y0, x1, y1 = box
    d = frame.draw()
    d.rounded_rectangle(box, radius=(x1 - x0) * 0.06, fill=bezel)
    m = (x1 - x0) * 0.045
    sx0, sy0, sx1, sy1 = x0 + m, y0 + m, x1 - m, y1 - m
    im = screen_page.img.resize((int(sx1 - sx0), int(sy1 - sy0)), Image.LANCZOS)
    frame.img.alpha_composite(im, (int(sx0), int(sy0)))
    frame.note("pdf", screen_page.source, screen_page.text)

def fit_font(frame, text, name, max_size, max_width):
    size = max_size
    d = frame.draw()
    while size > 18:
        f = font(name, size)
        w = max(d.textlength(line, font=f) for line in text.split("\n"))
        if w <= max_width:
            return f
        size -= 3
    return font(name, size)

def spaced_width(d, text, f, sp):
    return d.textlength(text, font=f) + sp * (len(text) - 1)

def spaced(img, xy, text, f, fill, sp, anchor="m"):
    d = ImageDraw.Draw(img)
    w = spaced_width(d, text, f, sp)
    x, y = xy
    if anchor == "m":
        x -= w / 2
    for ch in text:
        d.text((x, y), ch, font=f, fill=fill, anchor="ls")
        x += d.textlength(ch, font=f) + sp

# ---------------------------------------------------------------- spoiler check
def spoiler_scan(sources, forbidden):
    hits = []
    for kind, src, text in sources:
        flat = " ".join(text.split())
        for label, tok in forbidden.items():
            if tok in flat:
                hits.append(dict(source=src, kind=kind, token=tok, label=label))
    return hits
