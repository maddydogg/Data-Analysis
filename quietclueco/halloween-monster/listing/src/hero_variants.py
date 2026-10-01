"""Five alternative hero (first) images for the Storm over Corvenmoor listing, 2000x2000.

Each one is built from real pages of the case PDF plus code-drawn graphics, and every
frame is spoiler-scanned like the other mockups.

    python3 hero_variants.py      ->  ../mockups/hero-variants/*.png + contact sheets
"""
import math, os, random
from PIL import Image, ImageDraw, ImageFilter
import kit
from kit import GREEN, CRAN, PARCH, MUST, INK, PARCH_DARK, DEEP, MONSTER, font
import mockups as M

S = 2000
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mockups", "hero-variants")

# ---------------------------------------------------------------- helpers
def gradient(f, top, bottom):
    d = f.draw()
    for y in range(S):
        t = y / S
        d.line([(0, y), (S, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip(top, bottom)))

def rain(f, n, seed, alpha=70):
    rng = random.Random(seed)
    lay = Image.new("RGBA", f.img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for _ in range(n):
        x, y = rng.uniform(0, S), rng.uniform(0, S); L = rng.uniform(30, 80)
        d.line([(x, y), (x - L * 0.15, y + L)], fill=(0xC8, 0xC2, 0xD8, int(rng.uniform(alpha * 0.4, alpha))), width=3)
    f.img.alpha_composite(lay)

def glow(f, cx, cy, r, col, a):
    lay = Image.new("RGBA", f.img.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).ellipse([cx - r, cy - r, cx + r, cy + r], fill=col + (a,))
    f.img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(r * 0.45)))

def sky_bolt(f, x, y0, y1, seed, width=12, col=(0xFF, 0xF1, 0xCC)):
    rng = random.Random(seed)
    pts = [(x, y0)]
    while pts[-1][1] < y1:
        pts.append((pts[-1][0] + rng.uniform(-70, 70), pts[-1][1] + rng.uniform(60, 110)))
    lay = Image.new("RGBA", f.img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.line(pts, fill=col + (110,), width=width * 3, joint="curve")
    lay = lay.filter(ImageFilter.GaussianBlur(14))
    ImageDraw.Draw(lay).line(pts, fill=col + (255,), width=width, joint="curve")
    f.img.alpha_composite(lay)

def monster_head(f, x, y, r):
    """Our own stitched-monster emblem (shaggy hair, copper coils, no neck bolts), PIL version."""
    d = f.draw()
    d.ellipse([x - r * 1.18, y - r * 1.18, x + r * 1.18, y + r * 1.18], fill=GREEN)
    d.ellipse([x - r * 1.08, y - r * 1.08, x + r * 1.08, y + r * 1.08], outline=MUST, width=max(3, int(r * 0.08)))
    copper = (0xC9, 0x77, 0x3A)
    for sx in (-1, 1):
        for k in range(3):
            cx, cy = x + sx * r * 0.74, y - r * 0.12 + k * r * 0.13
            d.ellipse([cx - r * 0.11, cy - r * 0.11, cx + r * 0.11, cy + r * 0.11], outline=copper, width=max(2, int(r * 0.07)))
    d.rounded_rectangle([x - r * 0.6, y - r * 0.58, x + r * 0.6, y + r * 0.78], radius=r * 0.34, fill=MONSTER)
    hair = (0x1B, 0x16, 0x26)
    tufts = [(-0.66, -0.22), (-0.7, -0.62), (-0.5, -0.78), (-0.3, -0.66), (-0.12, -0.84), (0.08, -0.7), (0.3, -0.86),
             (0.5, -0.68), (0.7, -0.6), (0.66, -0.2), (0.5, -0.36), (0.36, -0.24), (0.2, -0.38), (0.02, -0.26),
             (-0.16, -0.4), (-0.34, -0.26), (-0.5, -0.38)]
    d.polygon([(x + px * r, y + py * r) for px, py in tufts], fill=hair)
    for sx in (-1, 1):
        d.ellipse([x + sx * r * 0.22 - r * 0.09, y + r * 0.02 - r * 0.09, x + sx * r * 0.22 + r * 0.09, y + r * 0.02 + r * 0.09], fill=hair)
    d.arc([x - r * 0.26, y + r * 0.18, x + r * 0.26, y + r * 0.5], 20, 160, fill=hair, width=max(3, int(r * 0.06)))
    d.line([(x - r * 0.3, y - r * 0.16), (x + r * 0.12, y - r * 0.2)], fill=hair, width=max(2, int(r * 0.035)))
    for k in range(4):
        xx = x - r * 0.26 + k * r * 0.12
        d.line([(xx, y - r * 0.1), (xx + r * 0.02, y - r * 0.26)], fill=hair, width=max(2, int(r * 0.035)))

def castle_silhouette(f, base, col=(0x12, 0x0E, 0x19), seed=2):
    d = f.draw()
    d.rectangle([0, base, S, S], fill=col)
    d.rectangle([180, base - 260, S - 180, base], fill=col)
    for i in range(22):
        x = 180 + i * (S - 360) / 22
        d.rectangle([x, base - 300, x + (S - 360) / 44, base - 258], fill=col)
    for tx, th, tw in ((180, 560, 230), (620, 440, 190), (1000, 720, 250), (1380, 470, 190), (1820, 600, 230)):
        d.rectangle([tx - tw / 2, base - th, tx + tw / 2, base], fill=col)
        d.polygon([(tx - tw * 0.62, base - th), (tx, base - th - th * 0.5), (tx + tw * 0.62, base - th)], fill=col)
        d.rounded_rectangle([tx - tw * 0.12, base - th * 0.6, tx + tw * 0.12, base - th * 0.4], radius=12, fill=(0xF2, 0xB4, 0x5A))

def caption(f, xy, text, fnt, col, anchor="ma", align="center", shadow=True):
    if shadow:
        lay = Image.new("RGBA", f.img.size, (0, 0, 0, 0))
        ImageDraw.Draw(lay).multiline_text((xy[0] + 6, xy[1] + 8), text, font=fnt, fill=(0, 0, 0, 170), anchor=anchor, align=align,
                                           spacing=int(fnt.size * 0.12))
        f.img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(8)))
    f.text(xy, text, fnt, col, anchor=anchor, align=align, spacing=0.12)

# ---------------------------------------------------------------- the five heroes
def h1_storm(A):
    """Centred cover under a lightning sky; big, simple, survives any crop."""
    f = kit.Frame(S, S, GREEN)
    gradient(f, (0x0C, 0x09, 0x14), (0x2E, 0x24, 0x40))
    sky_bolt(f, 330, -20, 760, 3); sky_bolt(f, 1720, -20, 620, 8, width=9)
    rain(f, 420, 5)
    glow(f, S / 2, 1080, 760, MUST, 70)
    cover = A.L.image(0, 1500)
    f.paste_page(cover, S / 2, 1090, angle=0, border=False)
    kit.pill(f, (S / 2, 150), "HALLOWEEN MURDER MYSTERY", font("black", 70), CRAN, PARCH)
    d = f.draw(); d.rectangle([0, 1850, S, S], fill=DEEP)
    caption(f, (S / 2, 1868), "6,000 suspects  ·  1 killer  ·  Printable + iPad", font("black", 72), MUST, shadow=False)
    return f

def h2_desk(A):
    """Flat lay on a dark desk: cover, map, receipt and witness note, a pumpkin and a candle."""
    f = kit.Frame(S, S, (0x2A, 0x1C, 0x14))
    d = f.draw(); rng = random.Random(4)
    for i in range(0, S, 250):                                    # wooden planks
        shade = rng.randint(-8, 8)
        d.rectangle([0, i, S, i + 246], fill=(0x2E + shade, 0x1F + shade, 0x16 + shade))
        for _ in range(9):
            y = i + rng.uniform(20, 226)
            d.line([(0, y), (S, y + rng.uniform(-14, 14))], fill=(0x24, 0x18, 0x11), width=3)
    f.paste_page(A.page("map", 1000), 560, 700, angle=8)
    f.paste_page(A.page("weather", 900), 1560, 640, angle=-10)
    f.paste_page(A.page("receipt", 860), 1520, 1460, angle=6)
    f.paste_page(A.L.image(0, 1300), 900, 1180, angle=-3)
    kit.pumpkin(f, 300, 1720, 190)
    glow(f, 1820, 1150, 220, MUST, 120)
    d = f.draw()
    d.rounded_rectangle([1770, 1170, 1870, 1480], radius=14, fill=(0xEE, 0xE4, 0xCF))            # candle
    d.polygon([(1820, 1090), (1798, 1160), (1842, 1160)], fill=(0xFF, 0xC6, 0x5C))
    lens_c, lens_r = (300, 300), 170                                                             # magnifying glass
    d.line([(lens_c[0] + 120, lens_c[1] + 120), (lens_c[0] + 330, lens_c[1] + 330)], fill=(0x3A, 0x2A, 0x1C), width=46)
    d.ellipse([lens_c[0] - lens_r, lens_c[1] - lens_r, lens_c[0] + lens_r, lens_c[1] + lens_r], outline=(0xB8, 0x86, 0x3A), width=26)
    lay = Image.new("RGBA", f.img.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).ellipse([lens_c[0] - lens_r + 14, lens_c[1] - lens_r + 14, lens_c[0] + lens_r - 14, lens_c[1] + lens_r - 14], fill=(0xFF, 0xFF, 0xFF, 40))
    f.img.alpha_composite(lay)
    banner = font("display", 120)
    d.rounded_rectangle([420, 1760, 1580, 1950], radius=30, fill=GREEN)
    f.text((1000, 1790), "Can you find the killer?", kit.fit_font(f, "Can you find the killer?", "display", 110, 1080), PARCH, anchor="ma")
    return f

def h3_print_ipad(A):
    """Both formats at a glance, clean bone background."""
    f = kit.Frame(S, S, PARCH); M.paper_bg(f)
    M.headline(f, "Halloween Murder Mystery", 80, GREEN, 140)
    f.text((S / 2, 255), "Find the killer among 6,000 suspects", font("bold", 70), CRAN, anchor="ma")
    f.paste_page(A.L.image(0, 1180), 600, 1060, angle=-3)
    scr = A.I.image(A.ip["cover"], 1060)
    tab = kit.Frame(870, 1150, PARCH); tab.img = Image.new("RGBA", tab.img.size, (0, 0, 0, 0))
    kit.ipad(tab, (20, 20, 850, 1130), scr)
    f.paste(tab.img, 1440, 1100); f.sources += tab.sources
    kit.pill(f, (600, 1780), "PRINTABLE", font("black", 92), MUST, GREEN)
    kit.pill(f, (1440, 1780), "iPad", font("black", 92), CRAN, PARCH)
    f.text((S / 2, 1900), "Instant download · 1–4 players · 90–150 min", font("bold", 56), SOFT_INK, anchor="ma")
    return f

SOFT_INK = (0x4B, 0x44, 0x58)

def h4_number(A):
    """Typographic hero: the size of the puzzle is the hook."""
    f = kit.Frame(S, S, DEEP)
    gradient(f, (0x10, 0x0C, 0x18), (0x2E, 0x24, 0x40))
    rain(f, 260, 9, 50)
    sky_bolt(f, 1800, -20, 520, 12, width=8)
    big = font("display", 520)
    caption(f, (S / 2, 120), "6,000", big, MUST)
    caption(f, (S / 2, 760), "suspects.", font("display", 170), PARCH)
    caption(f, (S / 2, 990), "One wore the monster mask.", kit.fit_font(f, "One wore the monster mask.", "display-italic", 110, 1700), (0xD9, 0xD2, 0xE6))
    monster_head(f, 520, 1530, 230)
    f.paste_page(A.L.image(0, 640), 1420, 1500, angle=4)
    kit.pill(f, (S / 2, 1900), "Find the killer · Printable + iPad", font("black", 66), CRAN, PARCH)
    return f

def h5_board(A):
    """Detective evidence board: pinned pages joined by red string."""
    f = kit.Frame(S, S, (0x8A, 0x63, 0x3E))
    lay = Image.new("RGBA", f.img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay); rng = random.Random(6)
    for _ in range(9000):                                         # cork speckle
        x, y = rng.uniform(0, S), rng.uniform(0, S); r = rng.uniform(1.5, 5)
        c = rng.choice([(0x6E, 0x4C, 0x2C), (0xA4, 0x7C, 0x52), (0x7A, 0x56, 0x34)])
        d.ellipse([x - r, y - r, x + r, y + r], fill=c + (150,))
    f.img.alpha_composite(lay)
    d = f.draw(); d.rectangle([0, 0, S, 18], fill=(0x4A, 0x32, 0x1E)); d.rectangle([0, S - 18, S, S], fill=(0x4A, 0x32, 0x1E))
    items = [("map", 820, 470, 560, 5), ("receipt", 760, 1500, 520, -6), ("weather", 680, 1560, 1480, 4), ("statements", 760, 470, 1460, -4)]
    pins = []
    for key, h, x, y, a in items:
        f.paste_page(A.page(key, h), x, y, angle=a)
        pins.append((x, y - h / 2 + 30))
    mapg = A.page("map", 820)
    cover = A.L.image(0, 980)
    centre = (1000, 1000)
    lay = Image.new("RGBA", f.img.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(lay)
    for px, py in pins:
        sd.line([(px, py), centre], fill=(0xB0, 0x1E, 0x1E, 235), width=7)
    f.img.alpha_composite(lay)
    f.paste_page(cover, centre[0], centre[1] + 40, angle=-2)
    d = f.draw()
    for px, py in pins + [(centre[0], centre[1] - 430)]:
        d.ellipse([px - 22, py - 22, px + 22, py + 22], fill=(0xC0, 0x24, 0x24)); d.ellipse([px - 8, py - 14, px + 2, py - 4], fill=(0xFF, 0xB0, 0xB0))
    note = kit.Frame(430, 330, (250, 226, 160))
    note.text((215, 70), "Who wore\nthe mask?", font("hand", 92), INK, anchor="ma", align="center")
    f.paste(note.img, 1620, 1020, angle=7); f.sources += note.sources
    d.rectangle([0, 0, S, 210], fill=GREEN)
    f.text((S / 2, 40), "Halloween Murder Mystery Puzzle", kit.fit_font(f, "Halloween Murder Mystery Puzzle", "display", 120, 1860), PARCH, anchor="ma")
    return f

HEROES = [("A-storm-cover", h1_storm, "Обложка под грозой"), ("B-desk-flat-lay", h2_desk, "Дело на столе"),
          ("C-print-and-ipad", h3_print_ipad, "Печать + iPad"), ("D-big-number", h4_number, "Большая цифра 6,000"),
          ("E-evidence-board", h5_board, "Доска улик")]

def build():
    os.makedirs(OUT, exist_ok=True)
    A = M.Assets()
    out = []
    for name, fn, label in HEROES:
        f = fn(A)
        p = os.path.join(OUT, f"storm-over-corvenmoor_hero-{name}.png")
        f.save(p)
        out.append((name, label, p, kit.spoiler_scan(f.sources, A.bad), len(f.sources)))
    # contact sheet (large) and an "Etsy search" sheet at thumbnail size
    big = Image.new("RGB", (5 * 620 + 6 * 30, 620 + 160), DEEP); bd = ImageDraw.Draw(big)
    small = Image.new("RGB", (5 * 260 + 6 * 24, 260 + 110), (0xF5, 0xF5, 0xF5)); sd = ImageDraw.Draw(small)
    for i, (name, label, p, _, _) in enumerate(out):
        im = Image.open(p).convert("RGB")
        big.paste(im.resize((620, 620), Image.LANCZOS), (30 + i * 650, 120))
        bd.text((30 + i * 650 + 310, 40), f"{name[0]}  ·  {label}", font=font("bold", 40), fill=PARCH, anchor="ma")
        small.paste(im.resize((260, 260), Image.LANCZOS), (24 + i * 284, 70))
        sd.text((24 + i * 284 + 130, 20), name[0], font=font("black", 36), fill=INK, anchor="ma")
    big.save(os.path.join(OUT, "hero-variants_sheet.png"), optimize=True)
    small.save(os.path.join(OUT, "hero-variants_thumbnail-test.png"), optimize=True)
    return out

if __name__ == "__main__":
    for name, label, p, hits, n in build():
        print(name, label, f"{n} sources", "spoiler hits:", len(hits))
