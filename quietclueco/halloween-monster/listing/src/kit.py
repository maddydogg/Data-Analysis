"""QuietClueCo listing kit: reusable helpers for mockups and video.

Every image is built on a `Frame`, which records the text of everything placed on it:
the text layer of each PDF region that is pasted, plus every string drawn by code.
The spoiler check reads those records, so it knows exactly what a buyer could read.
"""
import math, os, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import pymupdf as fitz

# ---------------------------------------------------------------- brand
# Halloween palette (names kept from the house template): GREEN = night violet, CRAN = burnt
# pumpkin, PARCH = bone, MUST = pumpkin.
GREEN = (0x2E, 0x24, 0x40); CRAN = (0xB4, 0x50, 0x1F); PARCH = (0xF2, 0xEC, 0xE0)
MUST = (0xE5, 0x8A, 0x2B); INK = (0x1E, 0x1B, 0x18); WHITE = (255, 255, 255)
DEEP = (0x1C, 0x16, 0x28); PARCH_DARK = (0xE4, 0xDC, 0xCD); SOFT = (0x6B, 0x62, 0x59)
MOSS = (0x5E, 0x7F, 0x35); MONSTER = (0x8D, 0xB2, 0x5A)

FONT_DIR = None
def set_font_dir(d):
    global FONT_DIR
    FONT_DIR = d

_fonts = {}
def font(name, size):
    key = (name, int(size))
    if key not in _fonts:
        files = {"display": "Fraunces-SemiBold", "display-italic": "Fraunces-Italic",
                 "body": "Nunito-Regular", "bold": "Nunito-Bold", "black": "Nunito-ExtraBold",
                 "hand": "Caveat-Medium"}
        _fonts[key] = ImageFont.truetype(os.path.join(FONT_DIR, files[name] + ".ttf"), int(size))
    return _fonts[key]

# ---------------------------------------------------------------- PDF pages
class Pdf:
    def __init__(self, path):
        self.path = path
        self.doc = fitz.open(path)
        self._cache = {}

    def find(self, *needles, exclude=("Tap any line to jump",)):
        """First page whose text contains every needle (the contents page is skipped)."""
        for i, p in enumerate(self.doc):
            t = p.get_text()
            if all(n in t for n in needles) and not any(e in t for e in exclude):
                return i
        raise KeyError(needles)

    def image(self, index, height, clip=None):
        """Render page `index` (optionally a clip rect in PDF points) to `height` px.
        Returns (PIL RGBA image, visible text)."""
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
    """A rendered PDF region that remembers its text and how to map PDF points to pixels."""
    def __init__(self, img, text, zoom, rect, source):
        self.img, self.text, self.zoom, self.rect, self.source = img, text, zoom, rect, source

    def px(self, x, y):
        return ((x - self.rect.x0) * self.zoom, (y - self.rect.y0) * self.zoom)

# ---------------------------------------------------------------- frames
class Frame:
    def __init__(self, w, h, bg):
        self.img = Image.new("RGBA", (w, h), bg + (255,))
        self.sources = []          # (kind, source, text)
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
            b = Image.new("RGBA", (im.width + 2, im.height + 2), (215, 205, 188, 255))
            b.paste(im, (1, 1)); im = b
        self.paste(im, x, y, angle, shadow)
        self.note("pdf", page.source, page.text)

    def paste(self, im, x, y, angle=0, shadow=True, shadow_strength=110):
        """Paste an RGBA image centred at (x, y), rotated by angle degrees."""
        if angle:
            im = im.rotate(angle, resample=Image.BICUBIC, expand=True)
        if shadow:
            s = max(8, int(min(im.size) * 0.03))
            alpha = im.split()[3]
            sh = Image.new("RGBA", (im.width + 4 * s, im.height + 4 * s), (0, 0, 0, 0))
            mask = Image.new("L", sh.size, 0)
            mask.paste(alpha.point(lambda a: shadow_strength if a > 0 else 0), (2 * s, 2 * s))
            mask = mask.filter(ImageFilter.GaussianBlur(s))
            sh.putalpha(mask)
            self.img.alpha_composite(sh, (int(x - sh.width / 2 + s * 0.6), int(y - sh.height / 2 + s * 1.2)))
        self.img.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))

    def text(self, xy, s, fnt, fill, anchor="la", spacing=0.18, align="left"):
        d = self.draw()
        if "\n" in s:
            d.multiline_text(xy, s, font=fnt, fill=fill, anchor=anchor, align=align,
                             spacing=int(fnt.size * spacing))
        else:
            d.text(xy, s, font=fnt, fill=fill, anchor=anchor)
        self.note("drawn", "text", s)

    def save(self, path):
        self.img.convert("RGB").save(path, optimize=True)

# ---------------------------------------------------------------- drawn elements
def snowflake(d, x, y, r, col, w=2):
    for k in range(6):
        a = math.pi / 3 * k
        dx, dy = math.cos(a) * r, math.sin(a) * r
        d.line([(x, y), (x + dx, y + dy)], fill=col, width=w)
        bx, by = x + dx * 0.55, y + dy * 0.55
        for s in (-1, 1):
            b = a + s * math.pi / 4
            d.line([(bx, by), (bx + math.cos(b) * r * 0.32, by + math.sin(b) * r * 0.32)], fill=col, width=w)

def bat(d, x, y, r, col):
    """A flying bat silhouette centred at (x, y), wingspan 2r (PIL)."""
    pts = [(0, 0.10), (-0.35, 0.42), (-0.75, 0.48), (-1.0, 0.20), (-0.82, 0.06), (-0.72, -0.08),
           (-0.64, -0.20), (-0.54, -0.06), (-0.44, -0.10), (-0.34, -0.24), (-0.24, -0.10), (-0.12, -0.12),
           (0, -0.22)]
    full = pts + [(-px, py) for px, py in reversed(pts[1:-1])]
    d.polygon([(x + px * r, y - py * r) for px, py in full], fill=col)
    d.ellipse([x - r * 0.17, y - r * 0.23, x + r * 0.17, y + r * 0.11], fill=col)
    for sx in (-1, 1):
        d.polygon([(x + sx * r * 0.15, y - r * 0.12), (x + sx * r * 0.12, y - r * 0.36), (x + sx * r * 0.02, y - r * 0.2)], fill=col)

def bolt(d, x, y, h, col):
    """Lightning bolt with its top at (x, y) (PIL, y grows downwards)."""
    w = h * 0.5
    pts = [(x + w * 0.20, y), (x - w * 0.36, y + h * 0.56), (x + w * 0.02, y + h * 0.56),
           (x - w * 0.24, y + h), (x + w * 0.46, y + h * 0.38), (x + w * 0.08, y + h * 0.38), (x + w * 0.44, y)]
    d.polygon(pts, fill=col)

def pumpkin(frame, cx, cy, r, col=MUST, face=True):
    d = frame.draw()
    d.rectangle([cx - r * 0.08, cy - r * 0.98, cx + r * 0.08, cy - r * 0.6], fill=MOSS)
    for dx, rr in ((-0.42, 0.6), (0.42, 0.6), (0, 0.66)):
        d.ellipse([cx + dx * r - rr * r, cy - r * 0.78, cx + dx * r + rr * r, cy + r * 0.78], fill=col)
    shade = tuple(int(v * 0.82) for v in col)
    for dx in (-0.36, 0.36):
        d.ellipse([cx + dx * r - r * 0.32, cy - r * 0.74, cx + dx * r + r * 0.32, cy + r * 0.74], outline=shade, width=max(2, int(r * 0.05)))
    if face:
        fc = (0x3A, 0x24, 0x10)
        for sx in (-1, 1):
            d.polygon([(cx + sx * r * 0.42, cy - r * 0.02), (cx + sx * r * 0.14, cy - r * 0.02), (cx + sx * r * 0.28, cy - r * 0.30)], fill=fc)
        mouth = [(-0.48, 0.2), (-0.3, 0.3), (-0.18, 0.2), (-0.06, 0.32), (0.06, 0.2), (0.18, 0.32), (0.3, 0.2),
                 (0.48, 0.2), (0.3, 0.52), (-0.3, 0.52)]
        d.polygon([(cx + px * r, cy + py * r) for px, py in mouth], fill=fc)

def snow_field(frame, n, seed, area=None, alpha=(60, 190), size=(6, 22)):
    """Night sky: faint stars plus a few bats. (Name kept from the house template.)"""
    rng = random.Random(seed)
    layer = Image.new("RGBA", frame.img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x0, y0, x1, y1 = area or (0, 0, frame.w, frame.h)
    for _ in range(n):
        r = rng.uniform(*size) * 0.22
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        d.ellipse([x - r, y - r, x + r, y + r], fill=PARCH + (int(rng.uniform(*alpha) * 0.8),))
    for _ in range(max(3, n // 18)):
        bat(d, rng.uniform(x0, x1), rng.uniform(y0, y1), rng.uniform(size[1] * 1.6, size[1] * 3.2),
            (0x12, 0x0D, 0x1A, int(rng.uniform(150, 230))))
    frame.img.alpha_composite(layer)

def string_lights(frame, y, sag, n, seed=1, width=None):
    d = frame.draw(); w = width or frame.w
    pts = [(w * t / 60, y + sag * math.sin(math.pi * t / 60)) for t in range(61)]
    d.line(pts, fill=(12, 20, 16), width=max(2, frame.w // 700))
    cols = [MUST, CRAN, PARCH]
    for i in range(1, n):
        t = i / n; xx = w * t; yy = y + sag * math.sin(math.pi * t) + frame.w * 0.008
        r = frame.w * 0.0075
        glow = Image.new("RGBA", frame.img.size, (0, 0, 0, 0))
        ImageDraw.Draw(glow).ellipse([xx - r * 3, yy - r * 3, xx + r * 3, yy + r * 3], fill=cols[i % 3] + (60,))
        frame.img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(r)))
        d.ellipse([xx - r, yy - r, xx + r, yy + r], fill=cols[i % 3])

def marker_strike(frame, x0, y, x1, h, col=CRAN, alpha=150, seed=0, progress=1.0):
    """A felt-tip line through a row, slightly wobbly. progress<1 draws it part-way (for video)."""
    rng = random.Random(seed)
    layer = Image.new("RGBA", frame.img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    xe = x0 + (x1 - x0) * progress
    pts = []
    steps = 24
    for i in range(steps + 1):
        t = i / steps
        xx = x0 + (xe - x0) * t
        pts.append((xx, y + math.sin(t * 6 + seed) * h * 0.08 + rng.uniform(-1, 1) * h * 0.04 + (t - 0.5) * h * 0.25))
    d.line(pts, fill=col + (alpha,), width=max(3, int(h * 0.28)), joint="curve")
    frame.img.alpha_composite(layer)

def highlight(frame, box, col=MUST, alpha=110):
    layer = Image.new("RGBA", frame.img.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).rounded_rectangle(box, radius=6, fill=col + (alpha,))
    frame.img.alpha_composite(layer)

def pen_circle(frame, cx, cy, rx, ry, col=CRAN, width=8, seed=3, progress=1.0):
    rng = random.Random(seed)
    d = frame.draw()
    turns = 1.12 * progress
    n = max(2, int(90 * turns))
    pts = []
    for i in range(n + 1):
        a = -math.pi / 2 + 2 * math.pi * turns * i / n
        wob = 1 + 0.04 * math.sin(3 * a + seed) + rng.uniform(-0.01, 0.01)
        grow = 1 + 0.06 * i / max(n, 1)
        pts.append((cx + math.cos(a) * rx * wob * grow, cy + math.sin(a) * ry * wob * grow))
    d.line(pts, fill=col, width=width, joint="curve")

def tick(frame, x, y, s, col=CRAN, width=None, progress=1.0):
    """Hand-drawn check mark with its short stroke starting at (x, y); s = size in px."""
    d = frame.draw(); w = width or max(4, int(s * 0.16))
    a = (x, y); b = (x + s * 0.32, y + s * 0.38); c = (x + s * 0.95, y - s * 0.55)
    if progress <= 0.35:
        t = progress / 0.35
        d.line([a, (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)], fill=col, width=w)
    else:
        t = (progress - 0.35) / 0.65
        d.line([a, b, (b[0] + (c[0] - b[0]) * t, b[1] + (c[1] - b[1]) * t)], fill=col, width=w, joint="curve")

def envelope(frame, box, number, label_font, col=PARCH, seal=CRAN):
    x0, y0, x1, y1 = box
    d = frame.draw()
    d.rounded_rectangle(box, radius=16, fill=col, outline=PARCH_DARK, width=4)
    mx = (x0 + x1) / 2; my = y0 + (y1 - y0) * 0.55
    d.line([(x0 + 8, y0 + 8), (mx, my), (x1 - 8, y0 + 8)], fill=PARCH_DARK, width=6)
    r = (y1 - y0) * 0.17
    d.ellipse([mx - r, my - r, mx + r, my + r], fill=seal)
    d.ellipse([mx - r * 0.72, my - r * 0.72, mx + r * 0.72, my + r * 0.72], outline=(120, 25, 38), width=4)
    d.text((mx, my), str(number), font=label_font, fill=PARCH, anchor="mm")
    frame.note("drawn", "envelope", str(number))

def pill(frame, center, text, fnt, bg, fg, padx=None, pady=None):
    d = frame.draw()
    l, t, r, b = d.textbbox((0, 0), text, font=fnt)
    padx = padx or fnt.size * 0.7; pady = pady or fnt.size * 0.38
    w, h = r - l + 2 * padx, b - t + 2 * pady
    cx, cy = center
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], radius=h / 2, fill=bg)
    d.text((cx, cy), text, font=fnt, fill=fg, anchor="mm")
    frame.note("drawn", "pill", text)
    return w, h

def mug(frame, cx, cy, s, body=CRAN, steam=PARCH):
    d = frame.draw()
    d.rounded_rectangle([cx - s * 0.5, cy - s * 0.45, cx + s * 0.4, cy + s * 0.55], radius=s * 0.12, fill=body)
    d.arc([cx + s * 0.22, cy - s * 0.25, cx + s * 0.72, cy + s * 0.3], -90, 90, fill=body, width=int(s * 0.11))
    for k in (-0.22, 0.0, 0.22):
        xs = cx - s * 0.05 + k * s
        pts = [(xs + math.sin(t / 3) * s * 0.06, cy - s * 0.55 - t * s * 0.05) for t in range(8)]
        d.line(pts, fill=steam, width=max(3, int(s * 0.05)))

def clock(frame, cx, cy, r, face=PARCH, hand=GREEN, rim=MUST):
    d = frame.draw()
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=face, outline=rim, width=int(r * 0.12))
    for k in range(12):
        a = math.pi / 6 * k
        d.line([(cx + math.cos(a) * r * 0.72, cy + math.sin(a) * r * 0.72),
                (cx + math.cos(a) * r * 0.82, cy + math.sin(a) * r * 0.82)], fill=hand, width=max(2, int(r * 0.04)))
    d.line([(cx, cy), (cx, cy - r * 0.6)], fill=hand, width=int(r * 0.08))
    d.line([(cx, cy), (cx + r * 0.45, cy + r * 0.1)], fill=hand, width=int(r * 0.08))

def people(frame, cx, cy, s, n, col=PARCH):
    d = frame.draw()
    gap = s * 0.55
    x = cx - gap * (n - 1) / 2
    for _ in range(n):
        d.ellipse([x - s * 0.17, cy - s * 0.52, x + s * 0.17, cy - s * 0.18], fill=col)
        d.pieslice([x - s * 0.3, cy - s * 0.12, x + s * 0.3, cy + s * 0.48], 180, 360, fill=col)
        x += gap

def pdf_file_card(frame, box, thumb, label, fnt, badge=None, badge_font=None):
    x0, y0, x1, y1 = box
    d = frame.draw()
    fold = (x1 - x0) * 0.16
    d.polygon([(x0, y0), (x1 - fold, y0), (x1, y0 + fold), (x1, y1), (x0, y1)], fill=WHITE, outline=PARCH_DARK)
    d.polygon([(x1 - fold, y0), (x1 - fold, y0 + fold), (x1, y0 + fold)], fill=PARCH_DARK)
    if thumb is not None:
        tw = int((x1 - x0) * 0.74)
        th = int(thumb.img.height * tw / thumb.img.width)
        th = min(th, int((y1 - y0) * 0.66))
        im = thumb.img.resize((int(thumb.img.width * th / thumb.img.height), th), Image.LANCZOS)
        frame.img.alpha_composite(im, (int((x0 + x1) / 2 - im.width / 2), int(y0 + (y1 - y0) * 0.1)))
        frame.note("pdf", thumb.source, thumb.text)
    d.text(((x0 + x1) / 2, y1 - (y1 - y0) * 0.1), label, font=fnt, fill=GREEN, anchor="mm")
    frame.note("drawn", "card", label)
    if badge:
        pill(frame, (x0 + (x1 - x0) * 0.24, y0 + (y1 - y0) * 0.06), badge, badge_font, CRAN, PARCH)

def ipad(frame, box, screen_page, bezel=(28, 30, 32)):
    """A generic tablet: dark rounded body, 3:4 screen. No logos."""
    x0, y0, x1, y1 = box
    d = frame.draw()
    r = (x1 - x0) * 0.06
    d.rounded_rectangle(box, radius=r, fill=bezel)
    m = (x1 - x0) * 0.045
    sx0, sy0, sx1, sy1 = x0 + m, y0 + m, x1 - m, y1 - m
    im = screen_page.img.resize((int(sx1 - sx0), int(sy1 - sy0)), Image.LANCZOS)
    frame.img.alpha_composite(im, (int(sx0), int(sy0)))
    frame.note("pdf", screen_page.source, screen_page.text)
    d.ellipse([x0 + m * 0.3, (y0 + y1) / 2 - 6, x0 + m * 0.3 + 12, (y0 + y1) / 2 + 6], fill=(60, 62, 66))

def fit_font(frame, text, name, max_size, max_width):
    size = max_size
    d = frame.draw()
    while size > 20:
        f = font(name, size)
        w = max(d.textbbox((0, 0), line, font=f)[2] for line in text.split("\n"))
        if w <= max_width:
            return f
        size -= 4
    return font(name, size)

# ---------------------------------------------------------------- spoiler check
def spoiler_scan(sources, forbidden):
    """sources: list of (kind, source, text); forbidden: {label: token}. Returns hits."""
    hits = []
    for kind, src, text in sources:
        flat = " ".join(text.split())
        for label, tok in forbidden.items():
            if tok in flat:
                hits.append(dict(source=src, kind=kind, token=tok, label=label))
    return hits
