"""Five style concepts for a horror-detective trailer of Storm over Corvenmoor.

The trailer beat is the same in all five: 20:50, the night watchman climbs the Laboratory
Tower and finds the curator Lucan Marsh dead at the Baron's workbench, his goblet of bubbling
potion punch still smoking; then the end card. One key frame per style, 1080x1080, drawn
with code (no photos, no generated images). No gore: the body is only ever a silhouette.

    python3 trailer_concepts.py   ->  ../video/trailer-concepts/
"""
import math, os, random
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageFont
import kit
import horror_heroes as HH
from horror_heroes import hf, layer, gradient, glow, grain, vignette, bolt_path, lightning, tracked

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "video", "trailer-concepts")
SS = 2160                 # drawn at 2x, saved at 1080
V = 1080
POTION = (0x7C, 0xE0, 0x5A)

# ---------------------------------------------------------------- shared props
def stone_wall(img, box, base, seed=1, block=(150, 90), var=10, mortar=None):
    x0, y0, x1, y1 = box; d = ImageDraw.Draw(img); rng = random.Random(seed)
    mortar = mortar or tuple(max(0, c - 18) for c in base)
    d.rectangle(box, fill=mortar)
    bw, bh = block; row = 0; y = y0
    while y < y1:
        x = x0 - (bw / 2 if row % 2 else 0)
        while x < x1:
            c = rng.randint(-var, var)
            d.rectangle([x + 5, y + 5, x + bw - 5, y + bh - 5], fill=tuple(max(0, min(255, v + c)) for v in base))
            x += bw
        y += bh; row += 1

def bench(d, x0, x1, top, h, col, leg=None):
    leg = leg or col
    d.rectangle([x0, top, x1, top + h * 0.12], fill=col)
    for lx in (x0 + h * 0.08, x1 - h * 0.2):
        d.rectangle([lx, top + h * 0.12, lx + h * 0.12, top + h], fill=leg)
    d.rectangle([x0 + h * 0.08, top + h * 0.7, x1 - h * 0.08, top + h * 0.76], fill=leg)

def apparatus(d, x, top, s, col):
    """Generic laboratory glassware and a coil on the bench (silhouettes)."""
    d.rectangle([x, top - s * 0.9, x + s * 0.12, top], fill=col)                         # retort stand
    d.line([(x + s * 0.06, top - s * 0.8), (x + s * 0.5, top - s * 0.8)], fill=col, width=int(s * 0.04))
    d.ellipse([x + s * 0.3, top - s * 0.8, x + s * 0.7, top - s * 0.4], fill=col)          # round flask
    d.rectangle([x + s * 0.44, top - s * 0.98, x + s * 0.56, top - s * 0.78], fill=col)
    d.polygon([(x + s * 0.9, top), (x + s * 1.3, top), (x + s * 1.14, top - s * 0.45), (x + s * 1.06, top - s * 0.45)], fill=col)  # cone flask
    for k in range(7):                                                                    # coil on a post
        y = top - s * 0.25 - k * s * 0.09
        d.ellipse([x + s * 1.55, y - s * 0.04, x + s * 1.85, y + s * 0.04], outline=col, width=int(s * 0.03))
    d.rectangle([x + s * 1.67, top - s * 0.25, x + s * 1.73, top], fill=col)

def slumped(d, x, top, s, col):
    """The curator slumped forward over the bench, head resting on one forearm, the other arm
    hanging down: a readable silhouette, no gore. x = front edge of his chair, top = bench top."""
    d.rectangle([x - s * 0.82, top - s * 0.5, x - s * 0.74, top + s * 1.25], fill=col)            # chair back post
    d.rectangle([x - s * 0.82, top + s * 0.42, x - s * 0.18, top + s * 0.5], fill=col)            # seat
    d.rectangle([x - s * 0.26, top + s * 0.5, x - s * 0.2, top + s * 1.25], fill=col)             # front leg
    d.polygon([(x - s * 0.66, top + s * 0.44), (x - s * 0.62, top + s * 0.05), (x - s * 0.42, top - s * 0.3),
               (x - s * 0.08, top - s * 0.46), (x + s * 0.28, top - s * 0.36), (x + s * 0.4, top - s * 0.16),
               (x + s * 0.12, top + s * 0.06), (x - s * 0.18, top + s * 0.42)], fill=col)           # torso, bent forward
    d.polygon([(x - s * 0.66, top + s * 0.3), (x - s * 0.72, top + s * 0.95), (x - s * 0.5, top + s * 0.62)], fill=col)  # coat tail
    d.polygon([(x - s * 0.36, top + s * 0.38), (x + s * 0.18, top + s * 0.42), (x + s * 0.22, top + s * 0.56),
               (x - s * 0.36, top + s * 0.56)], fill=col)                                            # thigh
    d.polygon([(x + s * 0.1, top + s * 0.46), (x + s * 0.24, top + s * 0.48), (x + s * 0.3, top + s * 1.2),
               (x + s * 0.12, top + s * 1.2)], fill=col)                                             # shin
    d.polygon([(x + s * 0.12, top + s * 1.14), (x + s * 0.42, top + s * 1.16), (x + s * 0.42, top + s * 1.25),
               (x + s * 0.1, top + s * 1.25)], fill=col)                                             # shoe
    d.rounded_rectangle([x + s * 0.18, top - s * 0.12, x + s * 1.0, top + s * 0.01], radius=s * 0.06, fill=col)  # forearm on the bench
    d.ellipse([x + s * 0.34, top - s * 0.42, x + s * 0.74, top - s * 0.06], fill=col)             # head resting on it
    d.polygon([(x - s * 0.02, top - s * 0.36), (x + s * 0.12, top - s * 0.3), (x + s * 0.02, top + s * 0.72),
               (x - s * 0.1, top + s * 0.7)], fill=col)                                              # arm hanging down
    d.ellipse([x - s * 0.13, top + s * 0.66, x + s * 0.05, top + s * 0.84], fill=col)              # hand

def goblet(img, x, base, s, glass=(0x2A, 0x26, 0x30), liquid=POTION, fog=True, seed=2, fog_down=False, glow_a=170):
    d = ImageDraw.Draw(img)
    d.polygon([(x - s * 0.3, base), (x + s * 0.3, base), (x + s * 0.06, base - s * 0.1), (x - s * 0.06, base - s * 0.1)], fill=glass)
    d.rectangle([x - s * 0.04, base - s * 0.5, x + s * 0.04, base - s * 0.08], fill=glass)
    d.chord([x - s * 0.36, base - s * 1.05, x + s * 0.36, base - s * 0.38], 0, 180, fill=glass)
    d.rectangle([x - s * 0.36, base - s * 0.75, x + s * 0.36, base - s * 0.72], fill=glass)
    glow(img, ("ellipse", [x - s * 0.9, base - s * 1.3, x + s * 0.9, base - s * 0.2]), liquid, glow_a, s * 0.3)
    d.ellipse([x - s * 0.33, base - s * 0.8, x + s * 0.33, base - s * 0.66], fill=liquid)
    if fog:
        rng = random.Random(seed); lay, ld = layer(img.size)
        for i in range(26):
            if fog_down:
                t = i / 26; fx = x + s * 0.3 + t * s * 1.4 + rng.uniform(-s * 0.1, s * 0.1); fy = base - s * 0.75 + t * t * s * 2.6
            else:
                fx = x + rng.uniform(-s * 0.4, s * 0.4) + math.sin(i) * s * 0.2; fy = base - s * 0.8 - i * s * 0.09
            r = s * rng.uniform(0.12, 0.3)
            ld.ellipse([fx - r * 1.6, fy - r, fx + r * 1.6, fy + r], fill=(0xD8, 0xF6, 0xC8, int(rng.uniform(25, 60))))
        img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(s * 0.06)))

def watchman(d, x, ground, s, col, lantern=True, raised=False):
    """Night watchman silhouette: peaked cap, greatcoat, a lantern held up or down."""
    d.rectangle([x - s * 0.2, ground - s * 0.25, x - s * 0.06, ground], fill=col)                 # legs
    d.rectangle([x + s * 0.06, ground - s * 0.25, x + s * 0.2, ground], fill=col)
    d.polygon([(x - s * 0.4, ground - s * 0.22), (x - s * 0.3, ground - s * 1.02), (x - s * 0.2, ground - s * 1.12),
               (x + s * 0.2, ground - s * 1.12), (x + s * 0.3, ground - s * 1.02), (x + s * 0.4, ground - s * 0.22)], fill=col)  # coat
    d.rectangle([x - s * 0.07, ground - s * 1.2, x + s * 0.07, ground - s * 1.1], fill=col)       # neck
    d.ellipse([x - s * 0.13, ground - s * 1.46, x + s * 0.15, ground - s * 1.16], fill=col)       # head
    d.chord([x - s * 0.15, ground - s * 1.6, x + s * 0.15, ground - s * 1.32], 180, 360, fill=col)  # cap crown
    d.polygon([(x - s * 0.15, ground - s * 1.46), (x + s * 0.3, ground - s * 1.44), (x + s * 0.15, ground - s * 1.4)], fill=col)  # brim
    if not lantern:
        return None
    if raised:
        hx, hy = x + s * 0.62, ground - s * 1.62
        d.polygon([(x + s * 0.16, ground - s * 1.08), (x + s * 0.28, ground - s * 1.0), (hx + s * 0.04, hy + s * 0.06), (hx - s * 0.06, hy)], fill=col)
    else:
        hx, hy = x + s * 0.46, ground - s * 0.6
        d.polygon([(x + s * 0.2, ground - s * 1.06), (x + s * 0.32, ground - s * 1.0), (hx + s * 0.04, hy), (hx - s * 0.06, hy)], fill=col)
    d.line([(hx, hy), (hx, hy + s * 0.08)], fill=col, width=max(2, int(s * 0.02)))
    d.rounded_rectangle([hx - s * 0.09, hy + s * 0.08, hx + s * 0.09, hy + s * 0.32], radius=s * 0.03, fill=col)   # lantern
    return (hx, hy + s * 0.2)

def finish(img, name):
    os.makedirs(OUT, exist_ok=True)
    out = img.convert("RGB").resize((V, V), Image.LANCZOS)
    p = os.path.join(OUT, f"trailer-style-{name}.png"); out.save(p, optimize=True)
    return p

# ---------------------------------------------------------------- 1. found footage
def s1_found_footage():
    sc = Image.new("RGBA", (SS, SS), (0, 0, 0, 255))
    stone_wall(sc, (0, 0, SS, SS), (0x4A, 0x46, 0x44), 3, (180, 104))
    d = ImageDraw.Draw(sc)
    d.rectangle([1500, 260, 1840, 760], fill=(0x0C, 0x0E, 0x16))                      # window
    lightning(sc, bolt_path(1680, 270, 740, 4, 40), 6)
    d = ImageDraw.Draw(sc)
    d.rectangle([1500, 500, 1840, 520], fill=(0x22, 0x20, 0x20)); d.rectangle([1662, 260, 1678, 760], fill=(0x22, 0x20, 0x20))
    for k in range(3):                                                                # shelf of jars
        y = 520 + k * 190; d.rectangle([140, y, 760, y + 22], fill=(0x2A, 0x22, 0x1A))
        for j in range(5):
            jx = 170 + j * 120; d.rounded_rectangle([jx, y - 120, jx + 80, y], radius=14, fill=(0x3C, 0x48, 0x40))
    top = 1380
    bench(d, 300, 2000, top, 520, (0x3A, 0x28, 0x1C), (0x26, 0x1A, 0x12))
    apparatus(d, 1380, top, 420, (0x24, 0x22, 0x26))
    slumped(d, 760, top, 420, (0x1A, 0x16, 0x18))
    goblet(sc, 1150, top, 240, seed=5)
    # darkness everywhere except the flashlight ellipse; the potion glows on its own
    dark = Image.eval(sc.convert("RGB"), lambda v: int(v * 0.07)).convert("RGBA")
    m = Image.new("L", sc.size, 0); ImageDraw.Draw(m).ellipse([380, 760, 1700, 1960], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(160))
    img = Image.composite(sc, dark, m)
    goblet(img, 1150, top, 240, seed=5, fog=False, glow_a=110)
    beam, bd = layer(img.size); bd.polygon([(1040, SS), (1600, SS), (1650, 1500), (700, 1400)], fill=(0xFF, 0xF6, 0xDC, 26))
    img.alpha_composite(beam.filter(ImageFilter.GaussianBlur(80)))
    # camcorder overlay
    r, g, b, a = img.split()
    img = Image.merge("RGBA", (ImageChops.offset(r, 6, 0), g, ImageChops.offset(b, -6, 0), a))
    lay, ld = layer(img.size)
    for y in range(0, SS, 6):
        ld.line([(0, y), (SS, y)], fill=(0, 0, 0, 60), width=2)
    img.alpha_composite(lay)
    grain(img, 36)
    f = kit.Frame(SS, SS, (0, 0, 0)); f.img = img; d = f.draw()
    mono = ImageFont.truetype(os.path.join(HERE, "..", "..", "src", "fonts", "CourierPrime-Bold.ttf"), 64)
    d.ellipse([110, 118, 160, 168], fill=(0xE8, 0x22, 0x22)); tracked(f, 190, 100, "REC", mono, (0xF4, 0xF4, 0xF4), 4, anchor="left")
    tracked(f, 1300, 1980, "OCT 31  20:50:13", mono, (0xF4, 0xF4, 0xF4), 2, anchor="left")
    tracked(f, 110, 1980, "TOWER CAM 2", mono, (0xF4, 0xF4, 0xF4), 2, anchor="left")
    d.rectangle([1860, 110, 2030, 170], outline=(0xF4, 0xF4, 0xF4), width=6); d.rectangle([2030, 125, 2048, 155], fill=(0xF4, 0xF4, 0xF4))
    d.rectangle([1874, 124, 1950, 156], fill=(0xF4, 0xF4, 0xF4))
    for cx, cy, sx, sy in ((80, 80, 1, 1), (SS - 80, 80, -1, 1), (80, SS - 80, 1, -1), (SS - 80, SS - 80, -1, -1)):
        d.line([(cx, cy), (cx + sx * 120, cy)], fill=(0xF4, 0xF4, 0xF4), width=8); d.line([(cx, cy), (cx, cy + sy * 120)], fill=(0xF4, 0xF4, 0xF4), width=8)
    vignette(f.img, 160)
    return f

# ---------------------------------------------------------------- 2. 1930s black-and-white trailer
def s2_old_trailer():
    sc = Image.new("RGBA", (SS, SS)); gradient(sc, (0x10, 0x10, 0x10), (0x5A, 0x5A, 0x5A))
    lightning(sc, bolt_path(560, -20, 900, 7, 70), 9, branch_seed=3)
    d = ImageDraw.Draw(sc)
    HH.castle(d, 1700, SS, (0x08, 0x08, 0x08), [(300, 520, 200), (760, 380, 170), (1500, 1000, 230), (1900, 560, 190)])
    d.rectangle([0, 1700, SS, SS], fill=(0x08, 0x08, 0x08))
    gray = Image.merge("RGBA", [sc.convert("L")] * 3 + [Image.new("L", sc.size, 255)])
    # hand-tinted: the tower window is the only colour, the green of the potion
    glow(gray, ("ellipse", [1380, 860, 1620, 1100]), POTION, 200, 50)
    ImageDraw.Draw(gray).rounded_rectangle([1474, 920, 1526, 1040], radius=18, fill=(0xB8, 0xF2, 0x8A))
    f = kit.Frame(SS, SS, (0, 0, 0)); f.img = gray; d = f.draw()
    card, cd = layer(gray.size)
    def poster_line(y, text, fnt, fill=(0xF6, 0xF2, 0xE6)):
        w = fnt.getlength(text)
        for e in range(14, 0, -1):
            cd.text((SS / 2 - w / 2 + e, y + e), text, font=fnt, fill=(0, 0, 0, 255))
        cd.text((SS / 2 - w / 2, y), text, font=fnt, fill=fill, stroke_width=4, stroke_fill=(0, 0, 0))
        f.note("drawn", "text", text)
    poster_line(1170, "AT 20:50 HE CLIMBED", hf("abril", 150))
    poster_line(1360, "THE TOWER...", hf("abril", 190))
    poster_line(1640, "WHAT HE FOUND WILL FREEZE YOUR HEART!", HH.fit("WHAT HE FOUND WILL FREEZE YOUR HEART!", "bebas", 120, 1900))
    f.img.alpha_composite(card.rotate(-4, resample=Image.BICUBIC))
    rng = random.Random(9); lay, ld = layer(f.img.size)                               # scratches and dust
    for _ in range(14):
        x = rng.uniform(0, SS); ld.line([(x, 0), (x + rng.uniform(-30, 30), SS)], fill=(255, 255, 255, int(rng.uniform(30, 90))), width=3)
    for _ in range(160):
        x, y, r = rng.uniform(0, SS), rng.uniform(0, SS), rng.uniform(2, 8)
        ld.ellipse([x - r, y - r, x + r, y + r], fill=(0, 0, 0, 160) if rng.random() < 0.6 else (255, 255, 255, 120))
    f.img.alpha_composite(lay); grain(f.img, 44)
    frame = Image.new("L", f.img.size, 0); ImageDraw.Draw(frame).rounded_rectangle([60, 60, SS - 60, SS - 60], radius=120, fill=255)
    black = Image.new("RGBA", f.img.size, (0, 0, 0, 255)); f.img = Image.composite(f.img, black, frame.filter(ImageFilter.GaussianBlur(20)))
    vignette(f.img, 200)
    return f

# ---------------------------------------------------------------- 3. modern slow burn
def s3_slow_burn():
    img = Image.new("RGBA", (SS, SS)); gradient(img, (0x0A, 0x04, 0x05), (0x1C, 0x08, 0x0A))
    d = ImageDraw.Draw(img)
    d.rectangle([1250, 320, 1850, 1180], fill=(0x40, 0x0C, 0x10))                     # tall red-lit window behind him
    glow(img, ("ellipse", [1050, 200, 2050, 1400]), (0x9A, 0x14, 0x1C), 170, 160)
    d = ImageDraw.Draw(img)
    d.rectangle([1540, 320, 1560, 1180], fill=(0x0A, 0x03, 0x04)); d.rectangle([1250, 740, 1850, 760], fill=(0x0A, 0x03, 0x04))
    top = 1360
    bench(d, 80, 2080, top, 640, (0x0C, 0x04, 0x05))
    rim, rd = layer(img.size); slumped(rd, 1360, top, 560, (0xC8, 0x30, 0x34, 255))      # red rim light on the silhouette
    img.alpha_composite(rim.filter(ImageFilter.GaussianBlur(9)))
    d = ImageDraw.Draw(img); slumped(d, 1360, top, 560, (0x05, 0x02, 0x02))
    apparatus(d, 220, top, 300, (0x10, 0x05, 0x06))
    goblet(img, 760, top, 380, glass=(0x16, 0x10, 0x12), seed=11, fog_down=True, glow_a=220)
    d = ImageDraw.Draw(img)
    d.arc([760 - 0.36 * 380, top - 1.05 * 380, 760 + 0.36 * 380, top - 0.38 * 380], 20, 160, fill=(0x8C, 0xE8, 0x70), width=6)   # rim light on the bowl
    f = kit.Frame(SS, SS, (0, 0, 0)); f.img = img; d = f.draw()
    d.rectangle([0, 0, SS, 250], fill=(0, 0, 0)); d.rectangle([0, SS - 330, SS, SS], fill=(0, 0, 0))   # letterbox
    tracked(f, SS / 2, SS - 250, "THE STORM CAME ON CUE.  SO DID MURDER.", HH.fit("THE STORM CAME ON CUE.  SO DID MURDER.", "cinzel", 64, 1980, 500, track=16), (0xEE, 0xE2, 0xDA), 16)
    tracked(f, SS / 2, 120, "20:50", hf("cinzel", 56, 400), (0xC8, 0x9C, 0x94), 20)
    grain(f.img, 16)
    return f

# ---------------------------------------------------------------- 4. comic panels
INKC = (0x12, 0x0E, 0x16)
def halftone(img, box, col, step=26, rmax=9, seed=0, fade="down"):
    x0, y0, x1, y1 = box; d = ImageDraw.Draw(img)
    for y in range(int(y0), int(y1), step):
        t = (y - y0) / max(1, y1 - y0); t = t if fade == "down" else 1 - t
        r = rmax * t
        for x in range(int(x0) + (step // 2 if (y // step) % 2 else 0), int(x1), step):
            d.ellipse([x - r, y - r, x + r, y + r], fill=col)

def panel(img, box):
    d = ImageDraw.Draw(img); d.rectangle(box, outline=INKC, width=16)

def s4_comic():
    img = Image.new("RGBA", (SS, SS), (0xF2, 0xEA, 0xD6, 255)); d = ImageDraw.Draw(img)
    g = 40; A = (g, g, SS - g, 1000); B = (g, 1000 + g, 1040, SS - g); Cc = (1040 + g, 1000 + g, SS - g, SS - g)
    # panel A: the watchman climbs the spiral stair
    pa = Image.new("RGBA", (A[2] - A[0], A[3] - A[1])); gradient(pa, (0x4A, 0x3C, 0x66), (0x1E, 0x18, 0x2C))
    pd = ImageDraw.Draw(pa)
    stone_wall(pa, (0, 0, pa.width, pa.height), (0x3C, 0x32, 0x52), 5, (170, 96), 6, mortar=(0x2A, 0x22, 0x3A))
    pd = ImageDraw.Draw(pa)
    for k in range(7):                                                             # stair steps rising to the right
        x = 380 + k * 210; y = 940 - k * 110
        pd.rectangle([x, y, x + 230, pa.height], fill=(0x24, 0x1E, 0x30), outline=INKC, width=8)
    pd.rectangle([1860, 120, 2030, 330], fill=(0xF6, 0xC8, 0x6A), outline=INKC, width=10)   # the lit door at the top
    halftone(pa, (0, 0, pa.width, pa.height), (0x10, 0x0C, 0x18), 30, 7)
    glow(pa, ("ellipse", [560, 60, 1400, 820]), (0xFF, 0xD0, 0x6A), 160, 90)
    pd = ImageDraw.Draw(pa)
    hx, hy = watchman(pd, 760, 940 - 1 * 110, 420, INKC, raised=True)
    pd.rounded_rectangle([hx - 40, hy - 40, hx + 40, hy + 60], radius=12, fill=(0xFF, 0xE0, 0x80))
    img.paste(pa, A[:2])
    # panel B: the watchman's face, eyes wide (code-drawn cartoon)
    pb = Image.new("RGBA", (B[2] - B[0], B[3] - B[1]), (0xE0, 0x9A, 0x3A, 255)); pd = ImageDraw.Draw(pb)
    for k in range(40):                                                            # speed lines
        a = k / 40 * 2 * math.pi; pd.line([(500, 520), (500 + math.cos(a) * 900, 520 + math.sin(a) * 900)], fill=(0xF6, 0xC6, 0x6A), width=14)
    pd.ellipse([210, 220, 790, 900], fill=(0xF0, 0xC8, 0xA0), outline=INKC, width=12)
    pd.chord([170, 120, 830, 420], 180, 360, fill=INKC); pd.rectangle([150, 300, 850, 350], fill=INKC)   # cap
    for ex in (390, 610):
        pd.ellipse([ex - 80, 470, ex + 80, 640], fill=(0xFF, 0xFF, 0xFF), outline=INKC, width=10)
        pd.ellipse([ex - 22, 540, ex + 22, 590], fill=INKC)
        pd.line([(ex - 90, 430), (ex + 70, 400)], fill=INKC, width=16)
    pd.ellipse([440, 740, 560, 850], fill=INKC)                                    # gasp
    img.paste(pb, B[:2])
    # panel C: the workbench, the slumped silhouette, the smoking goblet
    pc = Image.new("RGBA", (Cc[2] - Cc[0], Cc[3] - Cc[1])); gradient(pc, (0x1A, 0x2A, 0x16), (0x0A, 0x10, 0x08)); pd = ImageDraw.Draw(pc)
    lightning(pc, bolt_path(820, 0, 330, 6, 40), 6)
    pd = ImageDraw.Draw(pc)
    bench(pd, 120, 1000, 600, 420, INKC); slumped(pd, 330, 600, 330, INKC)
    goblet(pc, 840, 600, 190, glass=INKC, seed=3)
    img.paste(pc, Cc[:2])
    for bx in (A, B, Cc):
        panel(img, bx)
    f = kit.Frame(SS, SS, (0, 0, 0)); f.img = img; d = f.draw()
    d.rectangle([80, 80, 1180, 250], fill=(0xF6, 0xE8, 0x8A), outline=INKC, width=8)
    tracked(f, 630, 100, "20:50. THE NIGHT WATCHMAN", hf("bebas", 72), INKC, 3)
    tracked(f, 630, 170, "CLIMBS THE LABORATORY TOWER...", hf("bebas", 72), INKC, 3)
    sfx = kit.Frame(1000, 300, (0, 0, 0)); sfx.img = Image.new("RGBA", (1000, 300), (0, 0, 0, 0)); sd = sfx.draw()
    sfx_font = HH.fit("KRAKOOM!", "abril", 190, 880); w = sfx_font.getlength("KRAKOOM!")
    for e in range(16, 0, -1):
        sd.text((500 - w / 2 + e, 40 + e), "KRAKOOM!", font=sfx_font, fill=(0x9E, 0x24, 0x18))
    sd.text((500 - w / 2, 40), "KRAKOOM!", font=sfx_font, fill=(0xF2, 0xC1, 0x4E), stroke_width=10, stroke_fill=INKC)
    sfx.note("drawn", "text", "KRAKOOM!")
    f.img.alpha_composite(sfx.img.rotate(6, resample=Image.BICUBIC, expand=False), (1110, 1080)); f.sources += sfx.sources
    d.rectangle([1120, 1960, 2080, 2080], fill=(0xF6, 0xE8, 0x8A), outline=INKC, width=8)
    tracked(f, 1600, 1975, "THE SHOW WAS OVER.", hf("bebas", 80), INKC, 4)
    return f

# ---------------------------------------------------------------- 5. shadow theatre
def s5_shadows():
    img = Image.new("RGBA", (SS, SS)); stone_wall(img, (0, 0, SS, SS), (0x6E, 0x48, 0x24), 4, (200, 120), 8)
    glow(img, ("ellipse", [300, 600, 2000, 2400]), (0xFF, 0xB0, 0x50), 140, 300)
    sh, sd = layer(img.size); col = (0x0C, 0x06, 0x02, 235)                       # enormous shadows on the wall
    watchman(sd, 520, 1950, 1000, col, raised=True)
    bench(sd, 1100, 2200, 1400, 550, col); slumped(sd, 1480, 1400, 520, col)
    for i in range(6):                                                            # the potion's steam, a rising ghost shape
        y = 1260 - i * 120; x = 1880 + math.sin(i * 0.9) * 60
        sd.ellipse([x - 70 - i * 18, y - 60, x + 70 + i * 18, y + 60], fill=(0x0C, 0x06, 0x02, 150 - i * 18))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(img)
    d.rectangle([1640, 180, 1960, 620], fill=(0x10, 0x0C, 0x16)); lightning(img, bolt_path(1800, 190, 600, 2, 40), 6)
    d = ImageDraw.Draw(img); d.rectangle([1640, 390, 1960, 410], fill=(0x0C, 0x06, 0x02)); d.rectangle([1792, 180, 1808, 620], fill=(0x0C, 0x06, 0x02))
    d.rectangle([0, 1950, SS, SS], fill=(0x0A, 0x05, 0x02))
    goblet(img, 1880, 1950, 160, glass=(0x0A, 0x05, 0x02), seed=8, glow_a=200)   # the only colour: the real goblet
    f = kit.Frame(SS, SS, (0, 0, 0)); f.img = img
    cap = "THE LIGHTNING SHOW HAD ALREADY ENDED."
    fnt = HH.fit(cap, "cinzel", 70, 1900, 700, track=10)
    tracked(f, SS / 2, 90, "IN THE LABORATORY TOWER,", fnt, (0xFF, 0xE8, 0xC8), 10)
    tracked(f, SS / 2, 90 + fnt.size * 1.35, cap, fnt, (0xFF, 0xE8, 0xC8), 10)
    grain(f.img, 18); vignette(f.img, 150)
    return f

STYLES = [("1-found-footage", "Запись с камеры сторожа", s1_found_footage),
          ("2-1930s-trailer", "Трейлер фильма 1930-х", s2_old_trailer),
          ("3-slow-burn", "Современный медленный хоррор", s3_slow_burn),
          ("4-comic", "Комикс", s4_comic),
          ("5-shadow-theatre", "Театр теней", s5_shadows)]

def build():
    bad = HH.CL.forbidden() if hasattr(HH, "CL") else __import__("case_listing").forbidden()
    res = []
    for name, label, fn in STYLES:
        f = fn()
        res.append((name, label, finish(f.img, name), kit.spoiler_scan(f.sources, bad)))
    sheet = Image.new("RGB", (5 * 560 + 6 * 24, 560 + 120), (0x0A, 0x08, 0x0C)); sd = ImageDraw.Draw(sheet)
    for i, (name, label, p, _) in enumerate(res):
        sheet.paste(Image.open(p).resize((560, 560), Image.LANCZOS), (24 + i * 584, 96))
        sd.text((24 + i * 584 + 280, 20), name[0], font=hf("bebas", 64), fill=(0xF2, 0xEC, 0xE0), anchor="ma")
    sheet.save(os.path.join(OUT, "trailer-concepts_sheet.png"), optimize=True)
    return res

if __name__ == "__main__":
    for name, label, p, hits in build():
        print(name, "|", label, "| spoiler hits:", len(hits))
