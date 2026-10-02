"""Five horror-film / horror-book cover concepts for Storm over Corvenmoor, each shown as a
2000x2000 hero mockup. Everything is drawn with code (no photos, no generated images) using
open-licence fonts (SIL OFL; Special Elite is Apache 2.0) stored in fonts_horror/.

  1  monster-movie poster   - 1930s lithograph one-sheet on a brick wall, NOW SHOWING marquee
  2  pulp horror paperback  - die-cut window showing the mask's eye, 3D paperback on a table
  3  modern minimal poster  - oxblood, one tower, one tiny masked figure, cinema lightbox
  4  gothic novel           - gilt cloth hardcover with blackletter title, a case page as bookmark
  5  giallo poster          - shattered red glass, bold yellow type, pasted on a wall

    python3 horror_heroes.py   ->  ../mockups/horror-heroes/
"""
import math, os, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
import kit
import case_listing as CL

HERE = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(HERE, "fonts_horror")
OUT = os.path.join(HERE, "..", "mockups", "horror-heroes")
S = 2000
CW, CH = 1200, 1800                      # cover size (2:3, like a one-sheet or a paperback)

FILES = {"bebas": "BebasNeue-Regular.ttf", "cinzel": "Cinzel[wght].ttf", "fell": "IMFeENrm28P.ttf",
         "fell-it": "IMFeENit28P.ttf", "fraktur": "UnifrakturMaguntia-Book.ttf", "oswald": "Oswald[wght].ttf",
         "elite": "SpecialElite-Regular.ttf", "abril": "AbrilFatface-Regular.ttf"}
def hf(name, size, wght=None):
    f = ImageFont.truetype(os.path.join(FD, FILES[name]), int(size))
    if wght:
        f.set_variation_by_axes([wght])
    return f

TAG = "Printable murder mystery puzzle  ·  print or play on iPad"

# ---------------------------------------------------------------- generic helpers
def layer(size):
    im = Image.new("RGBA", size, (0, 0, 0, 0)); return im, ImageDraw.Draw(im)

def gradient(img, top, bottom, x=False):
    d = ImageDraw.Draw(img); w, h = img.size
    n = w if x else h
    for i in range(n):
        t = i / max(1, n - 1)
        col = tuple(int(a + (b - a) * t) for a, b in zip(top, bottom))
        d.line([(i, 0), (i, h)] if x else [(0, i), (w, i)], fill=col)

def glow(img, shape, col, a, blur):
    lay, d = layer(img.size)
    kind, box = shape
    (d.ellipse if kind == "ellipse" else d.polygon)(box, fill=col + (a,))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(blur)))

def grain(img, amount=22, seed=1):
    n = Image.effect_noise(img.size, 60).convert("L")
    lay = Image.merge("RGBA", (n, n, n, Image.new("L", img.size, amount)))
    img.alpha_composite(lay)

def vignette(img, strength=200):
    w, h = img.size
    m = Image.radial_gradient("L").resize((w, h)).point(lambda v: int(min(255, max(0, v - 70) * 1.5) * strength / 255))
    v = Image.new("RGBA", (w, h), (0, 0, 0, 255)); v.putalpha(m)
    img.alpha_composite(v)

def tracked(fr, cx, y, text, fnt, fill, track, anchor="center", stroke=0, stroke_fill=None):
    """Letter-spaced single line. Records the text on the frame for the spoiler scan."""
    d = fr.draw()
    widths = [fnt.getlength(ch) for ch in text]
    total = sum(widths) + track * (len(text) - 1)
    x = cx - total / 2 if anchor == "center" else cx
    for ch, w in zip(text, widths):
        d.text((x, y), ch, font=fnt, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
        x += w + track
    fr.note("drawn", "text", text)
    return total

def fit(text, name, size, maxw, wght=None, track=0):
    while size > 12:
        f = hf(name, size, wght)
        if f.getlength(text) + track * (len(text) - 1) <= maxw:
            return f
        size -= 2
    return hf(name, size, wght)

def bolt_path(x, y0, y1, seed, jag=70):
    rng = random.Random(seed); pts = [(x, y0)]
    while pts[-1][1] < y1:
        pts.append((pts[-1][0] + rng.uniform(-jag, jag), pts[-1][1] + rng.uniform(jag * 0.8, jag * 1.6)))
    return pts

def lightning(img, pts, width, col=(0xFF, 0xF4, 0xD8), halo=(0xE8, 0xF0, 0xFF), branch_seed=None):
    lay, d = layer(img.size)
    d.line(pts, fill=halo + (120,), width=width * 5, joint="curve")
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(width * 4)))
    lay, d = layer(img.size)
    d.line(pts, fill=col + (255,), width=width, joint="curve")
    if branch_seed is not None:
        rng = random.Random(branch_seed)
        for _ in range(3):
            i = rng.randrange(1, len(pts) - 1)
            b = bolt_path(pts[i][0], pts[i][1], pts[i][1] + rng.uniform(120, 260), rng.randrange(999), 40)
            d.line(b, fill=col + (200,), width=max(1, width // 2), joint="curve")
    img.alpha_composite(lay)

def rain(img, n, seed, col=(0xC8, 0xC8, 0xD8), alpha=60, length=(40, 90)):
    rng = random.Random(seed); lay, d = layer(img.size); w, h = img.size
    for _ in range(n):
        x, y = rng.uniform(0, w), rng.uniform(0, h); L = rng.uniform(*length)
        d.line([(x, y), (x - L * 0.18, y + L)], fill=col + (int(rng.uniform(alpha * 0.4, alpha)),), width=2)
    img.alpha_composite(lay)

def castle(d, base, w, col, towers, lit=None):
    """Castle silhouette across width w with its ground line at y=base. towers: (x, height, width)."""
    d.rectangle([w * 0.06, base - w * 0.16, w * 0.94, base + 4], fill=col)
    for i in range(24):
        x = w * 0.06 + i * w * 0.88 / 24
        d.rectangle([x, base - w * 0.19, x + w * 0.88 / 48, base - w * 0.15], fill=col)
    for tx, th, tw in towers:
        d.rectangle([tx - tw / 2, base - th, tx + tw / 2, base], fill=col)
        d.polygon([(tx - tw * 0.64, base - th), (tx, base - th - th * 0.42), (tx + tw * 0.64, base - th)], fill=col)
        if lit:
            d.rounded_rectangle([tx - tw * 0.11, base - th * 0.66, tx + tw * 0.11, base - th * 0.5], radius=tw * 0.08, fill=lit)

# ---------------------------------------------------------------- the monster (our own design)
def monster_bust(img, cx, cy, s, body, rim=None, eyes=(0xE8, 0xF5, 0x6A), rim_blur=10, coil=(0xC9, 0x77, 0x3A)):
    """A looming hooded figure: a deep cloak hood, the stitched green mask lost in shadow, two glowing
    eyes, a stitch line across the cheek and copper coils glinting at the temples. Our own design."""
    def shape(d, col, g=0):
        d.polygon([(cx - s * 1.25 - g, cy + s * 1.6), (cx - s * 1.0 - g, cy + s * 0.7), (cx - s * 0.62 - g, cy + s * 0.2),
                   (cx + s * 0.62 + g, cy + s * 0.2), (cx + s * 1.0 + g, cy + s * 0.7), (cx + s * 1.25 + g, cy + s * 1.6)], fill=col)  # cloak
        hood = [(cx - s * 0.66 - g, cy + s * 0.5), (cx - s * 0.7 - g, cy - s * 0.1), (cx - s * 0.56 - g, cy - s * 0.56),
                (cx - s * 0.3, cy - s * 0.84 - g), (cx + s * 0.04, cy - s * 0.98 - g), (cx + s * 0.34, cy - s * 0.8 - g),
                (cx + s * 0.58 + g, cy - s * 0.5), (cx + s * 0.7 + g, cy - s * 0.06), (cx + s * 0.64 + g, cy + s * 0.5)]
        d.polygon(hood, fill=col)
    if rim:
        lay, d = layer(img.size); shape(d, rim, s * 0.025)
        img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(rim_blur)))
    lay, d = layer(img.size); shape(d, body)
    img.alpha_composite(lay)
    lay, d = layer(img.size)                                            # the face opening: the mask, barely lit
    d.ellipse([cx - s * 0.36, cy - s * 0.52, cx + s * 0.36, cy + s * 0.34], fill=(0x22, 0x30, 0x16, 255))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(s * 0.05)))
    lay, d = layer(img.size)                                            # shadow of the hood brim over the brow
    d.ellipse([cx - s * 0.5, cy - s * 0.78, cx + s * 0.5, cy - s * 0.24], fill=body + (255,))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(s * 0.03)))
    d = ImageDraw.Draw(img)
    st = rim or (0x6E, 0x8A, 0x3A)                                      # stitch line across the cheek
    d.line([(cx - s * 0.26, cy + s * 0.02), (cx - s * 0.04, cy + s * 0.12)], fill=st, width=max(2, int(s * 0.012)))
    for k in range(4):
        x = cx - s * 0.23 + k * s * 0.06; y = cy + s * 0.035 + k * s * 0.027
        d.line([(x - s * 0.012, y - s * 0.03), (x + s * 0.012, y + s * 0.03)], fill=st, width=max(2, int(s * 0.01)))
    for sx in (-1, 1):                                                  # copper coils at the temples
        for k in range(3):
            x, y = cx + sx * s * 0.31, cy - s * 0.2 + k * s * 0.06
            d.ellipse([x - s * 0.04, y - s * 0.03, x + s * 0.04, y + s * 0.03], outline=coil, width=max(2, int(s * 0.013)))
    for sx in (-1, 1):                                                  # glowing eyes
        ex, ey = cx + sx * s * 0.13, cy - s * 0.12
        glow(img, ("ellipse", [ex - s * 0.13, ey - s * 0.08, ex + s * 0.13, ey + s * 0.08]), eyes, 170, s * 0.05)
        d.polygon([(ex - s * 0.065, ey), (ex - sx * s * 0.0, ey - s * 0.024), (ex + s * 0.065, ey + s * 0.006),
                   (ex, ey + s * 0.022)], fill=eyes)

def mask_eye(img, box, seed=3):
    """Extreme close-up of one eye of the stitched green mask, lit from the side by lightning."""
    x0, y0, x1, y1 = [int(v) for v in box]; w, h = x1 - x0, y1 - y0; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    skin = Image.new("RGBA", (w, h)); gradient(skin, (0x3E, 0x54, 0x22), (0x10, 0x16, 0x0A), x=True)
    lit = Image.radial_gradient("L").resize((w, h)).point(lambda v: 255 - v)
    hi = Image.new("RGBA", (w, h), (0x9C, 0xBE, 0x62, 0)); hi.putalpha(lit.point(lambda v: int(v * 0.55)))
    skin.alpha_composite(hi)
    sd = ImageDraw.Draw(skin); rng = random.Random(seed)
    for _ in range(900):                                                # pores and texture
        px, py = rng.uniform(0, w), rng.uniform(0, h); r = rng.uniform(1, 3)
        sd.ellipse([px - r, py - r, px + r, py + r], fill=(0x0A, 0x10, 0x06, 70))
    ex, ey = w * 0.46, h * 0.56
    sd.ellipse([ex - w * 0.34, ey - h * 0.2, ex + w * 0.34, ey + h * 0.22], fill=(0x0A, 0x0C, 0x06))  # deep socket
    eye = [(ex - w * 0.26, ey + h * 0.02), (ex - w * 0.1, ey - h * 0.07), (ex + w * 0.14, ey - h * 0.06),
           (ex + w * 0.27, ey + h * 0.03), (ex + w * 0.08, ey + h * 0.1), (ex - w * 0.12, ey + h * 0.09)]
    sd.polygon(eye, fill=(0xC8, 0xBE, 0x96))
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).polygon(eye, fill=255)
    iris = Image.new("RGBA", (w, h), (0, 0, 0, 0)); idr = ImageDraw.Draw(iris); r = h * 0.085
    idr.ellipse([ex - r, ey - r * 0.98, ex + r, ey + r * 1.02], fill=(0xF2, 0xA8, 0x1C))
    idr.ellipse([ex - r * 0.6, ey - r * 0.6, ex + r * 0.6, ey + r * 0.6], fill=(0xFF, 0xD8, 0x5A))
    idr.ellipse([ex - r * 0.16, ey - r * 0.75, ex + r * 0.16, ey + r * 0.75], fill=(0x08, 0x05, 0x02))   # slit pupil
    skin.paste(iris, (0, 0), ImageChops.multiply(m, iris.split()[3]))
    gl = Image.new("RGBA", (w, h), (0, 0, 0, 0)); ImageDraw.Draw(gl).ellipse([ex - r * 2.6, ey - r * 2, ex + r * 2.6, ey + r * 2], fill=(0xFF, 0xB0, 0x30, 70))
    skin.alpha_composite(gl.filter(ImageFilter.GaussianBlur(r)))
    sd = ImageDraw.Draw(skin)
    sd.line([(ex - w * 0.3, ey - h * 0.13), (ex + w * 0.3, ey - h * 0.16)], fill=(0x08, 0x0A, 0x04), width=max(4, int(h * 0.03)))  # heavy brow
    seam = [(w * 0.04, h * 0.2), (w * 0.4, h * 0.27), (w * 0.95, h * 0.17)]
    sd.line(seam, fill=(0x12, 0x10, 0x08), width=max(3, int(h * 0.01)))
    for k in range(10):
        t = k / 9; px = w * 0.06 + t * w * 0.86; py = h * 0.2 + math.sin(t * math.pi) * h * 0.06
        sd.line([(px - w * 0.008, py - h * 0.04), (px + w * 0.008, py + h * 0.04)], fill=(0x12, 0x10, 0x08), width=max(3, int(h * 0.009)))
    for k in range(3):                                                  # a copper coil at the temple
        yy = h * 0.42 + k * h * 0.07
        sd.ellipse([w * 0.86, yy - h * 0.03, w * 0.98, yy + h * 0.03], outline=(0xC9, 0x77, 0x3A), width=max(3, int(h * 0.012)))
    shade = Image.new("RGBA", (w, h), (0, 0, 0, 0)); ImageDraw.Draw(shade).rectangle([0, 0, w, h * 0.12], fill=(0, 0, 0, 200))
    skin.alpha_composite(shade.filter(ImageFilter.GaussianBlur(h * 0.06)))
    img.alpha_composite(skin, (x0, y0))

def aged_paper(img, seed=1, border=26):
    """Old one-sheet: cream edge, fold creases, foxing, grain."""
    w, h = img.size; d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w - 1, h - 1], outline=(0xEA, 0xDF, 0xC4), width=border)
    lay, ld = layer(img.size)
    for x in (w / 2,):
        ld.line([(x, 0), (x, h)], fill=(255, 255, 255, 34), width=3)
    for y in (h / 3, 2 * h / 3):
        ld.line([(0, y), (w, y)], fill=(255, 255, 255, 30), width=3)
    rng = random.Random(seed)
    for _ in range(60):
        x, y, r = rng.uniform(0, w), rng.uniform(0, h), rng.uniform(4, 18)
        ld.ellipse([x - r, y - r, x + r, y + r], fill=(0xA0, 0x80, 0x40, 26))
    img.alpha_composite(lay)
    tint = Image.new("RGBA", img.size, (0xC8, 0xA8, 0x60, 22)); img.alpha_composite(tint)
    grain(img, 26)

def solve(A, B):
    """Solve the 8x8 linear system A x = B by Gaussian elimination (no numpy needed)."""
    n = len(B); M_ = [list(map(float, row)) + [float(b)] for row, b in zip(A, B)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M_[r][c])); M_[c], M_[p] = M_[p], M_[c]
        for r in range(n):
            if r != c:
                k = M_[r][c] / M_[c][c]
                M_[r] = [a - k * b for a, b in zip(M_[r], M_[c])]
    return [M_[i][n] / M_[i][i] for i in range(n)]

def perspective(img, quad, out_size):
    """Warp img (RGBA) so its corners land on quad [(tl), (tr), (br), (bl)] in an out_size canvas."""
    w, h = img.size
    src = [(0, 0), (w, 0), (w, h), (0, h)]
    A = []; B = []
    for (x, y), (u, v) in zip(quad, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); B.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); B.append(v)
    coeffs = solve(A, B)
    return img.transform(out_size, Image.PERSPECTIVE, tuple(coeffs), Image.BICUBIC)

def bottom_strip(f, text=TAG, bg=(0x0A, 0x08, 0x0C), fg=(0xF2, 0xEC, 0xE0)):
    d = f.draw(); d.rectangle([0, S - 110, S, S], fill=bg)
    tracked(f, S / 2, S - 92, text.upper(), hf("oswald", 48, 500), fg, 4)

# ---------------------------------------------------------------- 1. monster-movie poster
def cover_monster_movie(W=CW, H=CH):
    """The chosen cover: a 1930s monster-movie one-sheet. Drawn for any page size: k scales
    everything to the width, and the vertical layout is anchored to the top and bottom edges."""
    k = W / 1200
    f = kit.Frame(int(W), int(H), (0, 0, 0)); img = f.img
    gradient(img, (0x05, 0x0A, 0x07), (0x1C, 0x36, 0x1E))
    yT = H - 620 * k                                   # top of the title block
    lightning(img, bolt_path(170 * k, 150 * k, 760 * k, 11, 60 * k), max(2, int(7 * k)), branch_seed=2)
    lightning(img, bolt_path(1050 * k, 150 * k, 620 * k, 5, 50 * k), max(2, int(5 * k)))
    sF = min(1.0, (yT - 150 * k) / (1030 * k))
    s = 470 * k * sF; cx = W / 2; cy = 150 * k + (yT - 150 * k) * 0.43
    glow(img, ("ellipse", [cx - 420 * k, cy - 340 * k * sF, cx + 420 * k, cy + 580 * k * sF]), (0x9B, 0xC5, 0x3D), 120, 120 * k)
    monster_bust(img, cx, cy, s, (0x06, 0x0A, 0x07), rim=(0xB6, 0xE0, 0x4A), rim_blur=14 * k)
    d = ImageDraw.Draw(img); yC = H - 470 * k
    castle(d, yC, W, (0x03, 0x05, 0x04), [(150 * k, 380 * k, 120 * k), (420 * k, 300 * k, 100 * k),
                                          (800 * k, 470 * k, 130 * k), (1060 * k, 340 * k, 110 * k)], lit=(0xF2, 0xC1, 0x4E))
    d.rectangle([0, yC, W, H], fill=(0x03, 0x05, 0x04))
    tag = "6,000 VISITORS. ONE OF THEM IS A KILLER."
    tracked(f, W / 2, 70 * k, tag, fit(tag, "bebas", 76 * k, 1040 * k, track=6 * k), (0xF4, 0xEA, 0xD0), 6 * k)
    # title: yellow with a red block extrusion, tilted like a hand-painted one-sheet
    th = int(560 * k)
    t = kit.Frame(int(W), th, (0, 0, 0)); t.img = Image.new("RGBA", (int(W), th), (0, 0, 0, 0)); td = t.draw()
    lines = [("STORM OVER", hf("abril", 120 * k)), ("CORVENMOOR", fit("CORVENMOOR", "abril", 210 * k, 1080 * k))]
    y = 30 * k
    for text, fnt in lines:
        w = fnt.getlength(text)
        for e in range(int(16 * k), 0, -1):
            td.text((W / 2 - w / 2 + e, y + e), text, font=fnt, fill=(0x8E, 0x1C, 0x14))
        td.text((W / 2 - w / 2, y), text, font=fnt, fill=(0xF2, 0xC1, 0x4E), stroke_width=max(2, int(4 * k)), stroke_fill=(0x1A, 0x08, 0x05))
        t.note("drawn", "text", text)
        y += fnt.size * 1.02
    rot = t.img.rotate(4, resample=Image.BICUBIC, expand=False)
    img.alpha_composite(rot, (0, int(yT))); f.sources += t.sources
    bb = hf("oswald", 34 * k, 300)
    tracked(f, W / 2, H - 145 * k, "QUIETCLUECO PRESENTS  ·  A HALLOWEEN MURDER MYSTERY PUZZLE", bb, (0xD8, 0xCF, 0xB8), 3 * k)
    tracked(f, W / 2, H - 98 * k, "18 CLUES  ·  1–4 DETECTIVES  ·  PRINT AT HOME OR PLAY ON iPAD", bb, (0xD8, 0xCF, 0xB8), 3 * k)
    aged_paper(img, 3, border=int(26 * k))
    return f

def hero_monster_movie(cov):
    f = kit.Frame(S, S, (0x1E, 0x12, 0x10)); d = f.draw(); rng = random.Random(8)
    for row in range(0, S, 62):                                         # brick wall
        off = 0 if (row // 62) % 2 else 70
        for x in range(-140 + off, S, 140):
            c = rng.randint(-10, 10)
            d.rectangle([x + 4, row + 4, x + 136, row + 58], fill=(0x3A + c, 0x1E + c, 0x18 + c))
    glow(f.img, ("polygon", [(780, 0), (1220, 0), (1700, 2000), (300, 2000)]), (0xFF, 0xE9, 0xB8), 70, 60)
    vignette(f.img, 230)
    d = f.draw(); d.rectangle([0, 0, S, 210], fill=(0x0C, 0x08, 0x08))
    for i in range(26):                                                  # marquee bulbs
        x = 40 + i * 74
        glow(f.img, ("ellipse", [x - 22, 18, x + 22, 62]), (0xFF, 0xD2, 0x7A), 140, 10)
        d.ellipse([x - 9, 31, x + 9, 49], fill=(0xFF, 0xE6, 0xA8))
        glow(f.img, ("ellipse", [x - 22, 158, x + 22, 202]), (0xFF, 0xD2, 0x7A), 140, 10)
        d.ellipse([x - 9, 171, x + 9, 189], fill=(0xFF, 0xE6, 0xA8))
    tracked(f, S / 2, 66, "NOW SHOWING", hf("bebas", 104), (0xFF, 0xF1, 0xD2), 22)
    poster = cov.img.resize((1080, 1620), Image.LANCZOS)
    f.paste(poster, S / 2, 1050, angle=0, shadow=True); f.sources += cov.sources
    for x, y in ((S / 2 - 520, 255), (S / 2 + 520, 255)):
        tape, _ = layer((120, 46)); ImageDraw.Draw(tape).rectangle([0, 0, 120, 46], fill=(0xE8, 0xDC, 0xB0, 190))
        f.paste(tape, x, y, angle=-14 if x < S / 2 else 14, shadow=False)
    bottom_strip(f)
    return f

# ---------------------------------------------------------------- 2. pulp horror paperback
def cover_paperback():
    f = kit.Frame(CW, CH, (0x0B, 0x09, 0x0A)); img = f.img
    rng = random.Random(4); lay, d = layer(img.size)
    for _ in range(4000):
        x, y = rng.uniform(0, CW), rng.uniform(0, CH); d.point((x, y), fill=(60, 50, 50, 90))
    img.alpha_composite(lay)
    # die-cut gothic arch window
    ax0, ax1, ay0, ay1 = 250, 950, 230, 1030
    win = Image.new("RGBA", img.size, (0, 0, 0, 0))
    mask_eye(win, (ax0 - 60, ay0, ax1 + 60, ay1), 5)
    lightning(win, bolt_path(860, ay0, ay0 + 420, 3, 40), 5)
    m = Image.new("L", img.size, 0); md = ImageDraw.Draw(m)
    md.rectangle([ax0, ay0 + 350, ax1, ay1], fill=255); md.ellipse([ax0, ay0, ax1, ay0 + 700], fill=255)
    img.paste(win, (0, 0), m)
    d = ImageDraw.Draw(img)
    for k, col in ((10, (0x2A, 0x24, 0x24)), (4, (0x80, 0x70, 0x6A))):    # bevelled edge of the cut
        d.arc([ax0 - k, ay0 - k, ax1 + k, ay0 + 700 + k], 180, 360, fill=col, width=6)
        d.line([(ax0 - k, ay0 + 350), (ax0 - k, ay1 + k)], fill=col, width=6)
        d.line([(ax1 + k, ay0 + 350), (ax1 + k, ay1 + k)], fill=col, width=6)
        d.line([(ax0 - k, ay1 + k), (ax1 + k, ay1 + k)], fill=col, width=6)
    tracked(f, CW / 2, 160, "A CASE FILE OF TERROR", hf("cinzel", 50, 700), (0xC9, 0x3A, 0x2A), 10)
    d.ellipse([CW - 170, 30, CW - 50, 150], outline=(0xC9, 0xA5, 0x4A), width=5)
    tracked(f, CW - 110, 46, "No.", hf("fell-it", 30), (0xC9, 0xA5, 0x4A), 0); tracked(f, CW - 110, 72, "2", hf("cinzel", 54, 900), (0xC9, 0xA5, 0x4A), 0)
    tracked(f, CW / 2, 1080, "STORM OVER", hf("cinzel", 72, 700), (0xE6, 0xDC, 0xC6), 16)
    # foil title: red-orange gradient with a highlight band
    title = "CORVENMOOR"; fnt = fit(title, "abril", 200, 1100)
    tl, tdraw = layer(img.size); w = fnt.getlength(title)
    tdraw.text((CW / 2 - w / 2, 1180), title, font=fnt, fill=(255, 255, 255, 255))
    foil = Image.new("RGBA", img.size); gradient(foil, (0xF4, 0x8A, 0x3A), (0x9E, 0x14, 0x10))
    hl, hd = layer(img.size); hd.rectangle([0, 1250, CW, 1285], fill=(255, 230, 190, 120)); foil.alpha_composite(hl.filter(ImageFilter.GaussianBlur(8)))
    sh, sd = layer(img.size); sd.text((CW / 2 - w / 2 + 8, 1188), title, font=fnt, fill=(0, 0, 0, 230))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(3)))
    img.paste(foil, (0, 0), tl.split()[3]); f.note("drawn", "text", title)
    it = hf("fell-it", 58)
    for i, line in enumerate(["Six thousand suspects. One stitched mask.", "Find the killer before the storm ends."]):
        tracked(f, CW / 2, 1450 + i * 72, line, it, (0xE6, 0xDC, 0xC6), 0)
    tracked(f, CW / 2, 1680, "QUIETCLUECO", hf("cinzel", 44, 700), (0xC9, 0xA5, 0x4A), 14)
    vignette(img, 120); grain(img, 14)
    return f

def hero_paperback(cov):
    f = kit.Frame(S, S, (0x16, 0x10, 0x0E)); d = f.draw(); rng = random.Random(3)
    for i in range(0, S, 230):
        c = rng.randint(-6, 6)
        d.rectangle([0, i, S, i + 226], fill=(0x2A + c, 0x1C + c, 0x14 + c))
        for _ in range(8):
            y = i + rng.uniform(10, 216); d.line([(0, y), (S, y + rng.uniform(-10, 10))], fill=(0x22, 0x16, 0x10), width=3)
    glow(f.img, ("ellipse", [1450, 120, 2150, 820]), (0xFF, 0xB8, 0x5A), 110, 160)
    d = f.draw()
    d.rounded_rectangle([1700, 360, 1800, 760], radius=16, fill=(0xEE, 0xE4, 0xCF))                      # candle
    d.polygon([(1750, 270), (1726, 352), (1774, 352)], fill=(0xFF, 0xC6, 0x5C))
    quad = [(470, 250), (1500, 330), (1440, 1830), (380, 1740)]
    page_quad = [(1500, 330), (1540, 360), (1480, 1860), (1440, 1830)]                                    # page block
    sh, sd = layer(f.img.size); sd.polygon([(q[0] + 40, q[1] + 50) for q in quad], fill=(0, 0, 0, 200))
    f.img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(30)))
    pb, pd = layer(f.img.size); pd.polygon(page_quad, fill=(0xE8, 0xDE, 0xC6))
    for k in range(1, 30):
        t = k / 30; pd.line([(1500 + 40 * t, 330 + 30 * t), (1440 + 40 * t, 1830 + 30 * t)], fill=(0xC8, 0xBC, 0xA0), width=1)
    f.img.alpha_composite(pb)
    f.img.alpha_composite(perspective(cov.img, quad, f.img.size)); f.sources += cov.sources
    spine, sp = layer(f.img.size); sp.polygon([(470, 250), (520, 254), (432, 1744), (380, 1740)], fill=(255, 255, 255, 26))
    f.img.alpha_composite(spine)
    vignette(f.img, 150)
    bottom_strip(f)
    return f

# ---------------------------------------------------------------- 3. modern minimal poster
def cover_minimal():
    f = kit.Frame(CW, CH, (0, 0, 0)); img = f.img
    gradient(img, (0x46, 0x0C, 0x0E), (0x0C, 0x03, 0x04))
    rain(img, 500, 2, (0xE0, 0xC0, 0xC0), 34, (50, 110))
    lightning(img, bolt_path(760, -20, 560, 9, 30), 3, col=(0xFF, 0xF4, 0xEE), halo=(0xFF, 0xC8, 0xC8))
    d = ImageDraw.Draw(img)
    tx, tw, top, base = 760, 150, 560, 1500                                 # one tall tower
    d.rectangle([tx - tw / 2, top, tx + tw / 2, base], fill=(0x07, 0x02, 0x03))
    d.polygon([(tx - tw * 0.66, top), (tx, top - 230), (tx + tw * 0.66, top)], fill=(0x07, 0x02, 0x03))
    d.line([(tx, top - 230), (tx, top - 300)], fill=(0x07, 0x02, 0x03), width=6)
    d.rectangle([tx - 14, top + 120, tx + 14, top + 170], fill=(0xF6, 0xC8, 0x7A))
    d.rectangle([0, base, CW, CH], fill=(0x07, 0x02, 0x03))
    glow(img, ("polygon", [(tx - 40, base), (tx + 40, base), (tx + 260, base + 160), (tx - 260, base + 160)]), (0xF6, 0xC8, 0x7A), 120, 30)
    d.rectangle([tx - 34, base - 150, tx + 34, base], fill=(0xF6, 0xC8, 0x7A))                       # lit doorway
    fx, fy = tx, base                                                        # tiny figure in the doorway
    d.polygon([(fx - 16, fy - 82), (fx + 16, fy - 82), (fx + 24, fy), (fx - 24, fy)], fill=(0x05, 0x02, 0x02))
    d.rounded_rectangle([fx - 12, fy - 112, fx + 12, fy - 80], radius=5, fill=(0x8D, 0xB2, 0x5A))       # the green mask: the only green
    tracked(f, CW / 2, 120, "SOMEBODY IN THE MASK IS A KILLER.", hf("cinzel", 38, 500), (0xE8, 0xD8, 0xD0), 8)
    tracked(f, CW / 2, 1560, "STORM OVER CORVENMOOR", fit("STORM OVER CORVENMOOR", "cinzel", 86, 1080, 700, track=14), (0xF4, 0xEA, 0xE0), 14)
    tracked(f, CW / 2, 1680, "A QUIETCLUECO MURDER MYSTERY PUZZLE  ·  31 OCTOBER", hf("oswald", 30, 300), (0xC8, 0xA8, 0xA0), 6)
    grain(img, 18)
    return f

def hero_minimal(cov):
    f = kit.Frame(S, S, (0x0E, 0x0A, 0x0B))
    for x in (230, 1770):                                                    # wall sconces
        glow(f.img, ("ellipse", [x - 230, 300, x + 230, 1100]), (0xFF, 0xC8, 0x80), 70, 120)
        f.draw().rounded_rectangle([x - 26, 640, x + 26, 760], radius=10, fill=(0xC9, 0xA5, 0x4A))
    d = f.draw(); bx0, by0, bx1, by1 = 450, 110, 1550, 1780                   # cinema lightbox
    glow(f.img, ("polygon", [(bx0, by0), (bx1, by0), (bx1, by1), (bx0, by1)]), (0xFF, 0xE8, 0xD8), 90, 50)
    d = f.draw(); d.rectangle([bx0, by0, bx1, by1], fill=(0x05, 0x05, 0x06))
    poster = cov.img.resize((1000, 1500), Image.LANCZOS)
    f.img.alpha_composite(poster, (int(S / 2 - 500), int((by0 + by1) / 2 - 750))); f.sources += cov.sources
    lay, ld = layer(f.img.size); ld.rectangle([bx0 + 50, by0 + 85, bx1 - 50, by0 + 140], fill=(255, 255, 255, 18))
    f.img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(12)))
    vignette(f.img, 120)
    bottom_strip(f)
    return f

# ---------------------------------------------------------------- 4. gothic novel
GILT = (0xC9, 0xA5, 0x4A)
def cover_gothic():
    f = kit.Frame(CW, CH, (0x1C, 0x26, 0x20)); img = f.img; d = ImageDraw.Draw(img)
    lay, ld = layer(img.size)                                                # cloth weave
    for i in range(0, CW, 6):
        ld.line([(i, 0), (i, CH)], fill=(0, 0, 0, 22))
    for j in range(0, CH, 6):
        ld.line([(0, j), (CW, j)], fill=(255, 255, 255, 10))
    img.alpha_composite(lay)
    d = ImageDraw.Draw(img)
    for inset, wdt in ((50, 6), (72, 2)):
        d.rectangle([inset, inset, CW - inset, CH - inset], outline=GILT, width=wdt)
    for cx, cy in ((72, 72), (CW - 72, 72), (72, CH - 72), (CW - 72, CH - 72)):
        d.ellipse([cx - 34, cy - 34, cx + 34, cy + 34], outline=GILT, width=4)
        d.polygon([(cx, cy - 22), (cx + 22, cy), (cx, cy + 22), (cx - 22, cy)], fill=GILT)
    def emboss_text(cx, y, text, fnt):
        w = fnt.getlength(text)
        d.text((cx - w / 2 + 3, y + 3), text, font=fnt, fill=(0x0A, 0x10, 0x0C))
        d.text((cx - w / 2, y), text, font=fnt, fill=GILT); f.note("drawn", "text", text)
    emboss_text(CW / 2, 150, "Storm", hf("fraktur", 190))
    emboss_text(CW / 2, 330, "over Corvenmoor", fit("over Corvenmoor", "fraktur", 150, 1000))
    tracked(f, CW / 2, 540, "A TALE OF MURDER, LIGHTNING", hf("fell", 40), GILT, 6)
    tracked(f, CW / 2, 590, "& SIX THOUSAND SUSPECTS", hf("fell", 40), GILT, 6)
    # gilt line-art medallion: tower, lightning, bats
    mx, my, mr = CW / 2, 1100, 330
    d.ellipse([mx - mr, my - mr, mx + mr, my + mr], outline=GILT, width=6)
    d.ellipse([mx - mr + 18, my - mr + 18, mx + mr - 18, my + mr - 18], outline=GILT, width=2)
    tw, top, base = 120, my - 120, my + 250
    d.line([(mx - tw / 2, base), (mx - tw / 2, top), (mx + tw / 2, top), (mx + tw / 2, base)], fill=GILT, width=5)
    d.line([(mx - tw * 0.7, top), (mx, top - 160), (mx + tw * 0.7, top), (mx - tw * 0.7, top)], fill=GILT, width=5)
    d.rectangle([mx - 14, top + 60, mx + 14, top + 110], outline=GILT, width=4)
    for k in range(4):
        y = top + 150 + k * 50; d.line([(mx - tw / 2, y), (mx + tw / 2, y)], fill=GILT, width=2)
    d.line(bolt_path(mx + 150, my - mr + 40, top - 40, 6, 30), fill=GILT, width=6)
    d.line([(mx - mr + 40, base), (mx + mr - 40, base)], fill=GILT, width=4)
    for bx, by, br in ((mx - 190, my - 160, 38), (mx - 120, my - 220, 26), (mx + 200, my + 40, 30)):
        kit.bat(d, bx, by, br, GILT)
    tracked(f, CW / 2, 1540, "BEING A PRINTABLE CASE FILE", hf("fell", 36), GILT, 6)
    tracked(f, CW / 2, 1630, "QUIETCLUECO  ·  MMXXVI", hf("cinzel", 40, 700), GILT, 10)
    grain(img, 10)
    return f

def hero_gothic(cov, A):
    f = kit.Frame(S, S, (0x12, 0x0C, 0x0A)); d = f.draw(); rng = random.Random(9)
    for i in range(0, S, 260):
        c = rng.randint(-6, 6); d.rectangle([0, i, S, i + 256], fill=(0x26 + c, 0x18 + c, 0x10 + c))
    glow(f.img, ("ellipse", [120, 80, 900, 860]), (0xFF, 0xB8, 0x5A), 120, 170)
    d = f.draw()
    d.rounded_rectangle([420, 300, 520, 720], radius=16, fill=(0xEE, 0xE4, 0xCF))
    d.polygon([(470, 210), (446, 292), (494, 292)], fill=(0xFF, 0xC6, 0x5C))
    note = A.page("receipt", 900)                                           # a real case page tucked in as a bookmark
    f.paste_page(note, 1380, 500, angle=-12)
    quad = [(560, 360), (1530, 420), (1490, 1820), (480, 1760)]
    sh, sd = layer(f.img.size); sd.polygon([(q[0] + 40, q[1] + 50) for q in quad], fill=(0, 0, 0, 210))
    f.img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(34)))
    side, sdd = layer(f.img.size); sdd.polygon([(1530, 420), (1580, 450), (1540, 1850), (1490, 1820)], fill=(0x10, 0x18, 0x13))
    f.img.alpha_composite(side)
    f.img.alpha_composite(perspective(cov.img, quad, f.img.size)); f.sources += cov.sources
    vignette(f.img, 150)
    bottom_strip(f)
    return f

# ---------------------------------------------------------------- 5. giallo poster
def cover_giallo():
    f = kit.Frame(CW, CH, (0x08, 0x05, 0x05)); img = f.img
    cx, cy = 560, 640; rng = random.Random(12)
    angles = sorted(rng.uniform(0, 2 * math.pi) for _ in range(11))
    R = 1500
    fills = [(0xB3, 0x12, 0x18), (0x10, 0x06, 0x07), (0xD2, 0x1E, 0x22), (0x6E, 0x08, 0x0C), (0x18, 0x08, 0x08)]
    shards = []
    for i, a in enumerate(angles):
        b = angles[(i + 1) % len(angles)] + (2 * math.pi if i == len(angles) - 1 else 0)
        mid = rng.uniform(0.25, 0.5) * R
        poly = [(cx, cy), (cx + math.cos(a) * R, cy + math.sin(a) * R),
                (cx + math.cos((a + b) / 2) * mid * 2.2, cy + math.sin((a + b) / 2) * mid * 2.2), (cx + math.cos(b) * R, cy + math.sin(b) * R)]
        shards.append(poly)
        ImageDraw.Draw(img).polygon(poly, fill=fills[i % len(fills)])
    ex, ey = cx + 230, cy + 60
    eye = Image.new("RGBA", img.size, (0, 0, 0, 0)); mask_eye(eye, (ex - 760, ey - 560, ex + 760, ey + 520), 9)
    def inside(pt, poly):
        x, y = pt; c = False
        for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
            if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
                c = not c
        return c
    m = Image.new("L", img.size, 0); md = ImageDraw.Draw(m)
    for poly in shards:
        if any(inside(p, poly) for p in ((ex, ey), (ex - 160, ey), (ex + 160, ey), (ex, ey - 90))):
            md.polygon(poly, fill=255)
    eye.putalpha(ImageChops.multiply(eye.split()[3], m))
    img.alpha_composite(eye)
    d = ImageDraw.Draw(img)
    for poly in shards:                                                      # cracks
        d.line([poly[0], poly[1]], fill=(0xF6, 0xEE, 0xEE), width=4)
    for r in (60, 150, 260):
        pts = [(cx + math.cos(a) * r * rng.uniform(0.8, 1.2), cy + math.sin(a) * r * rng.uniform(0.8, 1.2)) for a in angles]
        d.line(pts + [pts[0]], fill=(0xF6, 0xEE, 0xEE), width=3)
    d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=(0xFF, 0xFF, 0xFF))
    d.rectangle([0, 1180, CW, CH], fill=(0x08, 0x05, 0x05))
    yel = (0xF5, 0xD0, 0x1A)
    tracked(f, 70, 1190, "STORM OVER", hf("bebas", 190), yel, 4, anchor="left")
    tracked(f, 70, 1360, "CORVENMOOR", fit("CORVENMOOR", "bebas", 260, 1060, track=4), yel, 4, anchor="left")
    tracked(f, 72, 1610, "WHO IS BEHIND THE MASK?", hf("oswald", 62, 700), (0xE8, 0x24, 0x2A), 6, anchor="left")
    tracked(f, 72, 1700, "6,000 SUSPECTS  ·  18 CLUES  ·  1 KILLER  ·  QUIETCLUECO", hf("oswald", 34, 400), (0xE6, 0xDC, 0xD0), 4, anchor="left")
    grain(img, 20)
    return f

def hero_giallo(cov):
    f = kit.Frame(S, S, (0x4A, 0x46, 0x44)); rng = random.Random(5)
    lay, d = layer(f.img.size)
    for _ in range(14000):
        x, y = rng.uniform(0, S), rng.uniform(0, S); c = rng.randint(40, 110)
        d.point((x, y), fill=(c, c, c, 120))
    f.img.alpha_composite(lay)
    for _ in range(6):                                                       # old torn paper scraps
        x, y = rng.uniform(0, S), rng.uniform(0, S); w, h = rng.uniform(200, 500), rng.uniform(120, 300)
        f.draw().polygon([(x, y), (x + w, y + rng.uniform(-30, 30)), (x + w + rng.uniform(-30, 30), y + h), (x, y + h)], fill=(0x8A, 0x84, 0x7A))
    poster = cov.img.resize((1150, 1725), Image.LANCZOS)
    tear = Image.new("L", poster.size, 255); td = ImageDraw.Draw(tear)
    td.polygon([(0, 0), (160, 0), (0, 120)], fill=0); td.polygon([(1150, 1725), (1000, 1725), (1150, 1610)], fill=0)
    poster.putalpha(ImageChops.multiply(poster.split()[3], tear))
    f.paste(poster, S / 2, 980, angle=-2, shadow=True, shadow_strength=150); f.sources += cov.sources
    lay, d = layer(f.img.size)
    for _ in range(30):                                                      # paste wrinkles
        y = rng.uniform(150, 1830); x = rng.uniform(450, 1550)
        d.line([(x, y), (x + rng.uniform(60, 200), y + rng.uniform(-20, 20))], fill=(255, 255, 255, 30), width=3)
    f.img.alpha_composite(lay)
    vignette(f.img, 140)
    bottom_strip(f)
    return f

# ---------------------------------------------------------------- build
def build():
    import mockups as M
    os.makedirs(OUT, exist_ok=True)
    A = M.Assets()
    covers = [("1-monster-movie-poster", "Постер монстр-муви 1930-х", cover_monster_movie, hero_monster_movie),
              ("2-pulp-paperback", "Pulp-ужастик в мягкой обложке", cover_paperback, hero_paperback),
              ("3-minimal-horror-poster", "Современный минималистичный хоррор-постер", cover_minimal, hero_minimal),
              ("4-gothic-novel", "Готический роман в тиснёной обложке", cover_gothic, lambda c: hero_gothic(c, A)),
              ("5-giallo-poster", "Итальянский детектив-хоррор (джалло)", cover_giallo, hero_giallo)]
    res = []
    for name, label, cf, hfun in covers:
        cov = cf()
        cov.save(os.path.join(OUT, f"storm-over-corvenmoor_cover-{name}.png"))
        hero = hfun(cov)
        p = os.path.join(OUT, f"storm-over-corvenmoor_hero-{name}.png")
        hero.save(p)
        res.append((name, label, p, kit.spoiler_scan(hero.sources, A.bad)))
    sheet = Image.new("RGB", (5 * 600 + 6 * 30, 600 + 140), (0x0C, 0x0A, 0x0C)); sd = ImageDraw.Draw(sheet)
    thumbs = Image.new("RGB", (5 * 260 + 6 * 24, 260 + 90), (0xF5, 0xF5, 0xF5)); th = ImageDraw.Draw(thumbs)
    for i, (name, label, p, _) in enumerate(res):
        im = Image.open(p).convert("RGB")
        sheet.paste(im.resize((600, 600), Image.LANCZOS), (30 + i * 630, 110))
        sd.text((30 + i * 630 + 300, 30), name[0], font=hf("bebas", 64), fill=(0xF2, 0xEC, 0xE0), anchor="ma")
        thumbs.paste(im.resize((260, 260), Image.LANCZOS), (24 + i * 284, 70))
        th.text((24 + i * 284 + 130, 14), name[0], font=hf("bebas", 48), fill=(0x1E, 0x1B, 0x18), anchor="ma")
    sheet.save(os.path.join(OUT, "horror-heroes_sheet.png"), optimize=True)
    thumbs.save(os.path.join(OUT, "horror-heroes_thumbnail-test.png"), optimize=True)
    return res

if __name__ == "__main__":
    for name, label, p, hits in build():
        print(name, "|", label, "| spoiler hits:", len(hits))
