"""Listing video 1, the story trailer: 1080x1080, 15.0 s, 30 fps, no sound.

A film trailer for the story, not a tour of the puzzle. QuietClueCo presents; the full moon rises
over Morrowmere while paper lanterns sway; "On Moon Fair night, everyone wears the hat."; a crowd
of pointed hats drifts past and one silver crescent pin flashes; "Only one wore the silver moon.";
the apothecary's back room: a steaming cup, the door opens, the shadow of a pointed hat slides
across the wall and the candle goes out; "20:45."; a quick montage (the tipped cup in a lantern
beam, tea leaves that form a key, the standing stones under the moon, a curly signature being
written); "6,000 visitors. One killer."; the title, and the tagline "Who wore the silver moon?".

Silhouettes and objects only: no faces, no body, no blood. Old-film look throughout (letterbox,
flicker, gate weave, grain, scratches, dust). Every frame is spoiler-scanned.

    python3 video_story.py
"""
import math, os, random, subprocess
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import imageio_ffmpeg
import kit
import case_listing as CL
import poster as P

V = 1080; FPS = 30; DURATION = 15.0; N = int(round(DURATION * FPS))      # 450 frames
HERE = os.path.dirname(os.path.abspath(__file__))
MONO = os.path.join(HERE, "..", "..", "src", "fonts", "CourierPrime-Regular.ttf")
BAR = 130                                                               # letterbox bar height

T_PRESENTS, T_VILLAGE, T_CARD1, T_CROWD, T_CARD2, T_ROOM, T_TIME, T_MONTAGE, T_CARD3, T_TITLE = \
    0.0, 1.2, 3.4, 4.4, 6.2, 7.0, 9.4, 10.0, 11.6, 12.6
MONTAGE = 0.4
CUTS = [T_VILLAGE, T_CARD1, T_CROWD, T_CARD2, T_ROOM, T_TIME] + [T_MONTAGE + k * MONTAGE for k in range(4)] + [T_CARD3, T_TITLE]
WARM = (0xFF, 0xD9, 0x8A)

def ease(t):
    t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
def seg(t, a, b):
    return ease((t - a) / (b - a))
def lerp(a, b, t):
    return a + (b - a) * t

def blank(col=(0, 0, 0)):
    return Image.new("RGBA", (V, V), col + (255,))

def push(img, z, cx=V / 2, cy=V / 2):
    """Camera push-in: scale about (cx, cy) and crop back to V x V."""
    if abs(z - 1) < 1e-3:
        return img
    w = int(V * z); im = img.resize((w, w), Image.BICUBIC)
    x0 = int(cx * z - cx); y0 = int(cy * z - cy)
    return im.crop((x0, y0, x0 + V, y0 + V))

def glow_sprite(r, col, a, blur):
    s = int(r * 2 + blur * 4)
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse([s / 2 - r, s / 2 - r, s / 2 + r, s / 2 + r], fill=col + (a,))
    return im.filter(ImageFilter.GaussianBlur(blur))

def paste_c(dst, im, x, y):
    dst.alpha_composite(im, (int(x - im.width / 2), int(y - im.height / 2)))

# ---------------------------------------------------------------- assets
class Assets:
    def __init__(self):
        rng = random.Random(5)
        # the village at night
        sky = kit.Frame(V, V, P.PLUM)
        P.gradient(sky.img, (0x12, 0x0A, 0x1C), P.AUB, (0, 0, V, 800))
        P.gradient(sky.img, P.AUB, P.NIGHT, (0, 800, V, V))
        P.halftone(sky.img, (0, 0, V, 800), P.AMETHYST + (36,), 20, falloff=lambda x, y: 0.5)
        d = sky.draw()
        for _ in range(70):
            P.star(d, rng.uniform(0, V), rng.uniform(0, 620), rng.uniform(2, 5), P.MOON)
        self.sky = sky.img
        self.moon = Image.new("RGBA", (V, V), (0, 0, 0, 0)); P.moon(self.moon, V / 2, V / 2, 230)
        vil = Image.new("RGBA", (V, V), (0, 0, 0, 0)); vd = ImageDraw.Draw(vil)
        P.village(vd, 800, 0, V, 70, P.NIGHT, seed=11); vd.rectangle([0, 820, V, V], fill=P.NIGHT)
        for x in (180, 420, 700, 930):                                   # lit windows
            vd.rectangle([x, 770, x + 14, 786], fill=P.GOLD)
        self.village = vil
        self.lantern_glow = {c: glow_sprite(34, c, 120, 16) for c in (P.GOLD, P.AMETHYST, P.MOON)}
        # the crowd: three strips of figures seen from behind, at three depths
        self.strips = []
        for (s, col, rim, gap, base, n, seed) in ((70, (0x40, 0x2A, 0x58), P.GOLD, 120, 760, 15, 1),
                                                  (115, (0x26, 0x17, 0x36), P.GOLD, 210, 860, 9, 2),
                                                  (200, P.NIGHT, P.MOON, 380, 990, 5, 3)):
            im = Image.new("RGBA", (1900, V), (0, 0, 0, 0)); r2 = random.Random(seed); pins = []
            for k in range(n):
                x = 80 + k * gap + r2.uniform(-25, 25)
                pin = P.figure_from_behind(im, x, base + r2.uniform(-20, 20), s * r2.uniform(0.92, 1.08), col, rim=rim)
                pins.append(pin)
            self.strips.append((im, pins))
        crowd_bg = blank(P.PLUM); P.gradient(crowd_bg, (0x1C, 0x10, 0x28), P.AUB)
        for _ in range(26):                                              # warm bokeh of lanterns
            r = rng.uniform(14, 46); x, y = rng.uniform(0, V), rng.uniform(140, 620)
            paste_c(crowd_bg, glow_sprite(r, rng.choice((P.GOLD, WARM, P.AMETHYST)), rng.randint(60, 140), r * 0.5), x, y)
        self.crowd_bg = crowd_bg
        # the apothecary back room
        room = blank(); P.gradient(room, (0x2A, 0x1A, 0x36), (0x12, 0x0A, 0x1A))
        d = ImageDraw.Draw(room)
        d.rectangle([90, 250, 330, 880], fill=(0x0A, 0x06, 0x0E))                          # doorway
        d.rectangle([80, 240, 340, 252], fill=(0x30, 0x20, 0x3C)); d.rectangle([80, 240, 92, 880], fill=(0x30, 0x20, 0x3C))
        d.rectangle([328, 240, 340, 880], fill=(0x30, 0x20, 0x3C))
        for row, y in enumerate((300, 430, 560)):                                          # shelves of jars
            d.rectangle([540, y, 1060, y + 12], fill=(0x34, 0x22, 0x2C))
            x = 560
            while x < 1030:
                w = rng.uniform(30, 52); h = rng.uniform(50, 96)
                d.rounded_rectangle([x, y - h, x + w, y], radius=8, fill=(0x3A, 0x28, 0x4C))
                d.rectangle([x + 6, y - h * 0.6, x + w - 6, y - h * 0.4], fill=(0x6A, 0x5A, 0x6C))
                x += w + rng.uniform(8, 22)
        d.rectangle([0, 880, V, V], fill=(0x16, 0x0E, 0x1C))                                 # floor
        d.rectangle([380, 760, 1000, 800], fill=(0x3E, 0x28, 0x2E))                          # table
        for x in (410, 950):
            d.rectangle([x, 800, x + 24, 1000], fill=(0x30, 0x1E, 0x24))
        d.rounded_rectangle([600, 680, 680, 760], radius=12, fill=(0xC8, 0xBE, 0xAE))           # the cup
        d.arc([660, 696, 712, 744], -80, 80, fill=(0xC8, 0xBE, 0xAE), width=10)
        d.ellipse([604, 672, 676, 690], fill=(0x8A, 0x5A, 0x2A))
        d.rectangle([846, 650, 874, 760], fill=(0xE6, 0xDD, 0xC8))                           # candle
        self.room = room
        self.shadow = Image.new("RGBA", (V, V), (0, 0, 0, 0))
        cloak, head, brim, hat, band = P.figure_shape(V / 2, 980, 300)
        sd = ImageDraw.Draw(self.shadow)
        sd.polygon(cloak, fill=(0, 0, 0, 170)); sd.ellipse(head, fill=(0, 0, 0, 170))
        sd.ellipse(brim, fill=(0, 0, 0, 170)); sd.polygon(hat, fill=(0, 0, 0, 170))
        self.shadow = self.shadow.filter(ImageFilter.GaussianBlur(6))
        # montage: the standing stones under the moon
        st = blank(); P.gradient(st, (0x12, 0x0A, 0x1C), P.AUB)
        P.moon(st, 700, 330, 170)
        sd = ImageDraw.Draw(st)
        for x, h, w, lean in ((150, 330, 70, -0.08), (330, 450, 85, 0.05), (520, 380, 78, -0.03),
                              (700, 520, 92, 0.06), (900, 360, 74, -0.05), (1040, 280, 60, 0.04)):
            sd.polygon([(x - w, 900), (x - w * 1.1, 900 - h * 0.45), (x - w * 0.7 + lean * h, 900 - h * 0.9),
                        (x - w * 0.2 + lean * h, 900 - h), (x + w * 0.5 + lean * h, 900 - h * 0.94),
                        (x + w * 0.95, 900 - h * 0.5), (x + w, 900)], fill=P.NIGHT)
        sd.rectangle([0, 890, V, V], fill=P.NIGHT)
        self.stones = st
        mist = Image.new("RGBA", (2 * V, 260), (0, 0, 0, 0)); md = ImageDraw.Draw(mist)
        for _ in range(30):
            x, y, r = rng.uniform(0, 2 * V), rng.uniform(60, 200), rng.uniform(60, 140)
            md.ellipse([x - r * 2, y - r * 0.5, x + r * 2, y + r * 0.5], fill=P.MOON + (26,))
        self.mist = mist.filter(ImageFilter.GaussianBlur(30))
        # montage: tea leaves in the cup, seen from above, forming a key
        tea = blank((0x1A, 0x10, 0x22)); td = ImageDraw.Draw(tea)
        td.ellipse([140, 140, 940, 940], fill=(0xD8, 0xCF, 0xBE)); td.ellipse([220, 220, 860, 860], fill=(0xEE, 0xE8, 0xDA))
        td.ellipse([290, 290, 790, 790], fill=(0xE6, 0xD6, 0xB8))
        key = []
        for k in range(28):                                                  # the ring of the key
            a = 2 * math.pi * k / 28; key.append((430 + math.cos(a) * 62, 470 + math.sin(a) * 62))
        for k in range(14):                                                  # the shaft
            key.append((492 + k * 16, 470 + rng.uniform(-3, 3)))
        for x in (672, 700):                                                 # the teeth
            for k in range(4):
                key.append((x, 486 + k * 14))
        for x, y in key:
            r = rng.uniform(5, 9); td.ellipse([x - r, y - r * 0.7, x + r, y + r * 0.7], fill=(0x4A, 0x30, 0x1E))
        for _ in range(60):
            a = rng.uniform(0, 2 * math.pi); q = rng.uniform(0, 230); x, y = 540 + math.cos(a) * q, 540 + math.sin(a) * q
            r = rng.uniform(2, 5); td.ellipse([x - r, y - r, x + r, y + r], fill=(0x5A, 0x3C, 0x24))
        self.tea = tea
        # montage: the tipped cup on the table
        cup = blank((0x10, 0x09, 0x14)); cd = ImageDraw.Draw(cup)
        cd.rectangle([0, 640, V, V], fill=(0x3E, 0x28, 0x2E))
        cd.ellipse([420, 760, 900, 860], fill=(0x8A, 0x5A, 0x2A))                            # spilled brew, amber
        cd.polygon([(300, 700), (560, 640), (600, 780), (340, 820)], fill=(0xC8, 0xBE, 0xAE))  # cup on its side
        cd.ellipse([540, 630, 640, 790], fill=(0x6A, 0x60, 0x58))
        cd.ellipse([555, 650, 625, 772], fill=(0x3A, 0x26, 0x18))
        cd.arc([250, 700, 360, 800], 90, 270, fill=(0xC8, 0xBE, 0xAE), width=14)
        self.cup = cup
        m = Image.new("L", (900, 900), 0); ImageDraw.Draw(m).ellipse([150, 150, 750, 750], fill=255)
        self.beam = m.filter(ImageFilter.GaussianBlur(90))
        # montage: the ledger and a curly signature
        led = blank((0xF3, 0xEC, 0xDC)); ld = ImageDraw.Draw(led)
        for y in range(160, V, 92):
            ld.line([(0, y), (V, y)], fill=(0xC9, 0xD3, 0xE4), width=3)
        ld.line([(150, 0), (150, V)], fill=(0xE2, 0xA9, 0xA9), width=3)
        self.ledger = led
        self.hand = kit.font("hand", 120)
        self.sig = []
        for k in range(2):                                                   # two loops and a flourish
            bx = 600 + 200 * k
            self.sig += P.bez((bx - 60, 600), (bx + 80, 380), (bx - 90, 330), (bx - 30, 520), 30)
            self.sig += P.bez((bx - 30, 520), (bx + 10, 640), (bx + 120, 610), (bx + 90, 520), 20)
            self.sig += P.bez((bx + 90, 520), (bx + 70, 470), (bx + 30, 560), (bx + 150, 600), 20)
        self.sig += P.bez((950, 600), (1060, 560), (1040, 700), (860, 690), 30)
        # the title
        tit = kit.Frame(V, V, P.PLUM)
        P.gradient(tit.img, (0x12, 0x0A, 0x1C), P.AUB)
        P.halftone(tit.img, (0, 0, V, V), P.AMETHYST + (36,), 20, falloff=lambda x, y: max(0.0, 1 - math.hypot(x - V / 2, y - 330) / 700))
        P.moon(tit.img, V / 2, 330, 210)
        P.gradient(tit.img, (0x1A, 0x10, 0x26), P.NIGHT, (0, 560, V, V))
        d = tit.draw()
        for x0, y0, sz in ((180, 260, 40), (900, 200, 34), (820, 420, 28)):
            P.crow(d, x0, y0, sz, P.NIGHT, 0.3, 1 if x0 < V / 2 else -1)
        self.title_bg = tit.img
        word = kit.Frame(V, 300, (0, 0, 0)); word.img = Image.new("RGBA", (V, 300), (0, 0, 0, 0))
        P.title_word(word, "MORROWMERE", V / 2, 40, P.fit("MORROWMERE", "abril", 190, V - 120), depth=12, k=0.9)
        self.word = word
        # film textures
        self.grain = []
        for i in range(6):
            n = Image.effect_noise((V, V), 70 + i).convert("L")
            self.grain.append(Image.merge("RGBA", (n, n, n, Image.new("L", (V, V), 34))))
        vm = Image.radial_gradient("L").resize((V, V)).point(lambda v: int(min(255, max(0, v - 70) * 1.5)))
        self.vignette = Image.new("RGBA", (V, V), (0, 0, 0, 255)); self.vignette.putalpha(vm)
        self.mono = ImageFont.truetype(MONO, 92)

# ---------------------------------------------------------------- text
def text_card(t, t0, lines, src, bg=(0, 0, 0)):
    """Lines appear one after another on black: [(text, font, colour, at)]."""
    f = kit.Frame(V, V, bg)
    total = sum(fn.size * 1.3 for _, fn, _, _ in lines); y = V / 2 - total / 2
    for text, fn, col, at in lines:
        a = seg(t, t0 + at, t0 + at + 0.3)
        if a > 0:
            lay = kit.Frame(V, V, (0, 0, 0)); lay.img = Image.new("RGBA", (V, V), (0, 0, 0, 0))
            P.tracked(lay, V / 2, y + (1 - a) * 12, text, fn, col, fn.size * 0.06)
            lay.img.putalpha(lay.img.split()[3].point(lambda v: int(v * a)))
            f.img.alpha_composite(lay.img); src += lay.sources
        y += fn.size * 1.3
    return f.img

def caption(img, text, t, t0, src, col=P.GOLD):
    """Typewriter caption in the lower letterbox bar."""
    n = int(len(text) * seg(t, t0, t0 + 0.8))
    if n <= 0:
        return
    f = kit.Frame(V, V, (0, 0, 0)); f.img = img
    P.tracked(f, V / 2, V - BAR + 40, text[:n], P.hf("cinzel", 40, 700), col, 8)
    src += f.sources

# ---------------------------------------------------------------- scenes
def presents(A, t, src):
    a = seg(t, 0.15, 0.55) * (1 - seg(t, 0.95, 1.2))
    f = kit.Frame(V, V, (0, 0, 0))
    lay = kit.Frame(V, V, (0, 0, 0)); lay.img = Image.new("RGBA", (V, V), (0, 0, 0, 0))
    P.tracked(lay, V / 2, V / 2 - 70, "QUIETCLUECO", P.hf("cinzel", 84, 800), P.MOON, 14)
    P.tracked(lay, V / 2, V / 2 + 40, "PRESENTS", P.hf("cinzel", 40, 600), P.GOLD, 16)
    lay.img.putalpha(lay.img.split()[3].point(lambda v: int(v * a)))
    f.img.alpha_composite(lay.img); src += lay.sources
    return f.img

def village(A, t, src):
    p = (t - T_VILLAGE) / (T_CARD1 - T_VILLAGE)
    img = A.sky.copy()
    img.alpha_composite(A.moon, (0, int(lerp(300, -40, ease(min(1, p * 1.3))))))
    d = ImageDraw.Draw(img)
    for i, (x0, y0, s, sp) in enumerate(((-140, 300, 44, 380), (-300, 220, 32, 430), (V + 120, 380, 40, -360))):
        P.crow(d, x0 + sp * (t - T_VILLAGE), y0 + math.sin(t * 3 + i) * 10, s, P.NIGHT, math.sin(t * 13 + i * 1.7), 1 if sp > 0 else -1)
    img.alpha_composite(A.village)
    # a string of paper lanterns across the foreground, swaying
    pts = [(V * k / 40 - 40, 150 + 70 * math.sin(math.pi * k / 40)) for k in range(41)]
    d = ImageDraw.Draw(img); d.line(pts, fill=(0x08, 0x04, 0x0C), width=4)
    cols = (P.GOLD, P.AMETHYST, P.MOON)
    for k in range(1, 9):
        x, y = pts[k * 5]; ang = math.sin(t * 2.2 + k) * 0.12
        lx, ly = x + math.sin(ang) * 46, y + math.cos(ang) * 46
        c = cols[k % 3]
        paste_c(img, A.lantern_glow[c], lx, ly)
        d = ImageDraw.Draw(img)
        d.line([(x, y), (lx, ly - 22)], fill=(0x08, 0x04, 0x0C), width=3)
        d.ellipse([lx - 20, ly - 26, lx + 20, ly + 26], fill=c)
        d.rectangle([lx - 12, ly - 30, lx + 12, ly - 24], fill=(0x08, 0x04, 0x0C))
    img = push(img, 1 + 0.07 * p, V / 2, 520)
    letterbox(img)
    caption(img, "MORROWMERE  ·  31 OCTOBER", t, T_VILLAGE + 0.4, src)
    return img

def crowd(A, t, src):
    img = A.crowd_bg.copy()
    dt = t - T_CROWD
    pin_at = None
    for (im, pins), v in zip(A.strips, (50, 130, 260)):
        shift = v * dt + (0 if v != 260 else 0)
        img.alpha_composite(im, (int(-shift), 0))
        if v == 260:
            px, py = pins[2]
            pin_at = (px - shift, py)
    # the one silver crescent pin, catching the lantern light
    lay = Image.new("RGBA", (V, V), (0, 0, 0, 0))
    P.crescent_pin(lay, pin_at[0], pin_at[1], 14)
    g = seg(t, 5.45, 5.65) * (1 - seg(t, 5.75, 6.1))
    if g > 0:
        P.star(ImageDraw.Draw(lay), pin_at[0] + 3, pin_at[1], 70 * g, (0xFF, 0xF6, 0xE0, int(240 * g)))
        P.glow(lay, [pin_at[0] - 160 * g, pin_at[1] - 160 * g, pin_at[0] + 160 * g, pin_at[1] + 160 * g], (0xFF, 0xF6, 0xE0), int(120 * g), 40)
    img.alpha_composite(lay)
    img = push(img, 1 + 0.05 * seg(t, T_CROWD, T_CARD2), V / 2, 600)
    letterbox(img)
    return img

def room(A, t, src):
    img = A.room.copy()
    op = seg(t, 7.5, 7.9)                                               # the door opens: warm light
    if op > 0:
        lay = Image.new("RGBA", (V, V), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.rectangle([92, 252, 328, 880], fill=WARM + (int(150 * op),))
        ld.polygon([(330, 260), (980, 360), (980, 880), (330, 880)], fill=WARM + (int(46 * op),))
        ld.polygon([(330, 880), (90, 880), (520, V), (1080, V)], fill=WARM + (int(60 * op),))
        img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(24)))
    sh = seg(t, 7.9, 9.0)                                               # the shadow slides across the wall
    if 7.9 < t < 9.3:
        x = lerp(-420, 520, sh)
        img.alpha_composite(A.shadow, (int(x), -60))
    out = seg(t, 9.0, 9.15)                                             # the candle
    fl = (1 - out) * (0.9 + 0.1 * math.sin(t * 40))
    if fl > 0.02:
        paste_c(img, glow_sprite(150 * fl, WARM, int(110 * fl), 60), 860, 620)
        d = ImageDraw.Draw(img)
        d.polygon([(860, 640 - 44 * fl), (872, 628), (860, 646), (848, 628)], fill=(0xFF, 0xE6, 0xA8))
    else:
        d = ImageDraw.Draw(img)
        for k in range(12):                                             # a curl of smoke
            yy = 640 - k * 18 - (t - 9.15) * 60
            d.ellipse([856 + math.sin(k * 0.7 + t * 4) * 12 - 6, yy - 6, 868 + math.sin(k * 0.7 + t * 4) * 12, yy + 6], fill=(0xB8, 0xB0, 0xC0, 90))
    d = ImageDraw.Draw(img)                                             # steam over the cup
    for k in range(3):
        pts = [(625 + k * 16 + math.sin(t * 3 + j * 0.6 + k) * 10, 668 - j * 14) for j in range(9)]
        d.line(pts, fill=(0xD8, 0xD0, 0xC8), width=4, joint="curve")
    img = push(img, 1 + 0.08 * seg(t, T_ROOM, T_TIME), 640, 700)
    dark = seg(t, 9.1, 9.4)
    if dark > 0:
        img.alpha_composite(Image.new("RGBA", (V, V), (0, 0, 0, int(255 * dark))))
    letterbox(img)
    return img

def time_card(A, t, src):
    f = kit.Frame(V, V, (0, 0, 0)); d = f.draw()
    text = "20:45"; n = int(len(text) * seg(t, T_TIME + 0.05, T_TIME + 0.35))
    if n:
        d.text((V / 2, V / 2 - 30), text[:n], font=A.mono, fill=P.MOON, anchor="mm"); src.append(("drawn", "card", text[:n]))
    if t > T_TIME + 0.3:
        P.tracked(f, V / 2, V / 2 + 50, "THE APOTHECARY’S BACK ROOM", P.hf("cinzel", 34, 700), P.GOLD, 8)
        src += f.sources
    return f.img

def montage(A, t, src):
    k = min(3, int((t - T_MONTAGE) / MONTAGE)); u = (t - T_MONTAGE - k * MONTAGE) / MONTAGE
    if k == 0:                                                          # the tipped cup in a lantern beam
        m = Image.new("L", (V, V), 0)
        m.paste(A.beam, (int(lerp(-300, 140, u)), 170))
        dark = Image.eval(A.cup.convert("RGB"), lambda v: int(v * 0.12)).convert("RGBA")
        img = Image.composite(A.cup, dark, m)
    elif k == 1:                                                        # tea leaves that form a key
        img = A.tea.rotate(-20 * u, resample=Image.BICUBIC, center=(V / 2, V / 2), fillcolor=(0x1A, 0x10, 0x22))
        img = push(img, 1.15 + 0.1 * u, 540, 520)
    elif k == 2:                                                        # the standing stones under the moon
        img = A.stones.copy()
        img.alpha_composite(A.mist, (int(-u * 300), 700))
        img = push(img, 1.05 + 0.05 * u)
    else:                                                               # a curly signature being written
        img = A.ledger.copy(); d = ImageDraw.Draw(img)
        d.text((180, 470), "Signed:", font=A.hand, fill=(0x2E, 0x24, 0x40)); src.append(("drawn", "ledger", "Signed:"))
        n = max(2, int(len(A.sig) * min(1, u * 1.3)))
        d.line(A.sig[:n], fill=(0x1F, 0x2E, 0x5C), width=12, joint="curve")
        img = push(img.rotate(-4, resample=Image.BICUBIC, fillcolor=(0xF3, 0xEC, 0xDC)), 1.1)
    letterbox(img)
    return img

def title(A, t, src):
    img = A.title_bg.copy()
    f = kit.Frame(V, V, (0, 0, 0)); f.img = img
    a1 = seg(t, T_TITLE + 0.1, T_TITLE + 0.5)
    if a1 > 0:
        lay = kit.Frame(V, V, (0, 0, 0)); lay.img = Image.new("RGBA", (V, V), (0, 0, 0, 0))
        P.tracked(lay, V / 2, 560, "FULL MOON OVER", P.hf("cinzel", 66, 800), P.MOON, 10)
        lay.img.putalpha(lay.img.split()[3].point(lambda v: int(v * a1))); img.alpha_composite(lay.img); src += lay.sources
    a2 = seg(t, T_TITLE + 0.45, T_TITLE + 0.85)
    if a2 > 0:
        z = lerp(1.25, 1.0, a2)
        w = A.word.img.resize((int(V * z), int(300 * z)), Image.BICUBIC)
        w.putalpha(w.split()[3].point(lambda v: int(v * a2)))
        img.alpha_composite(w, (int(V / 2 - w.width / 2), int(640 - (w.height - 300) / 2)))
        src += A.word.sources
    a3 = seg(t, T_TITLE + 1.2, T_TITLE + 1.6)
    if a3 > 0:
        lay = kit.Frame(V, V, (0, 0, 0)); lay.img = Image.new("RGBA", (V, V), (0, 0, 0, 0))
        P.tracked(lay, V / 2, 900, "WHO WORE THE SILVER MOON?", P.hf("fell-it", 58), P.GOLD, 2)
        P.tracked(lay, V / 2, 990, "QUIETCLUECO  ·  NOW SHOWING", P.hf("oswald", 34, 500), P.MOON, 6)
        lay.img.putalpha(lay.img.split()[3].point(lambda v: int(v * a3))); img.alpha_composite(lay.img); src += lay.sources
    return push(img, 1.04 - 0.04 * seg(t, T_TITLE, DURATION))

def letterbox(img):
    d = ImageDraw.Draw(img); d.rectangle([0, 0, V, BAR], fill=(0, 0, 0)); d.rectangle([0, V - BAR, V, V], fill=(0, 0, 0))

# ---------------------------------------------------------------- the old-film look
def film(A, img, t, i):
    rng = random.Random(i * 7919)
    dx, dy = rng.uniform(-2.5, 2.5), rng.uniform(-3, 3)                     # gate weave
    out = Image.new("RGBA", (V, V), (0, 0, 0, 255)); out.alpha_composite(img.convert("RGBA"), (int(dx), int(dy)))
    fl = 1 + rng.uniform(-0.05, 0.04)                                       # flicker
    out = Image.eval(out.convert("RGB"), lambda v: min(255, int(v * fl))).convert("RGBA")
    out.alpha_composite(Image.new("RGBA", (V, V), (0x3A, 0x22, 0x10, 16)))
    out.alpha_composite(A.grain[i % len(A.grain)])
    d = ImageDraw.Draw(out)
    for _ in range(rng.randint(0, 2)):                                      # scratches
        x = rng.uniform(40, V - 40)
        d.line([(x, 0), (x + rng.uniform(-6, 6), V)], fill=(0xF0, 0xE8, 0xD8, rng.randint(50, 120)), width=rng.choice((1, 2)))
    for _ in range(rng.randint(1, 6)):                                      # dust
        x, y, r = rng.uniform(0, V), rng.uniform(0, V), rng.uniform(1.5, 5)
        d.ellipse([x - r, y - r * 0.7, x + r, y + r * 0.7], fill=(0x10, 0x0A, 0x08, rng.randint(120, 220)))
    out.alpha_composite(A.vignette)
    if any(0 <= t - c < 1 / FPS for c in CUTS):                            # splice flash
        out.alpha_composite(Image.new("RGBA", (V, V), (0xFF, 0xF4, 0xE0, 120)))
    return out

def render(A, t, i, src):
    if t < T_VILLAGE:
        img = presents(A, t, src)
    elif t < T_CARD1:
        img = village(A, t, src)
    elif t < T_CROWD:
        img = text_card(t, T_CARD1, [("ON MOON FAIR NIGHT,", P.hf("cinzel", 64, 800), P.MOON, 0.05),
                                     ("everyone wears the hat.", P.hf("fell-it", 76), P.GOLD, 0.35)], src)
    elif t < T_CARD2:
        img = crowd(A, t, src)
    elif t < T_ROOM:
        img = text_card(t, T_CARD2, [("ONLY ONE WORE", P.hf("cinzel", 72, 800), P.MOON, 0.05),
                                     ("the silver moon.", P.hf("fell-it", 92), P.GOLD, 0.3)], src)
    elif t < T_TIME:
        img = room(A, t, src)
    elif t < T_MONTAGE:
        img = time_card(A, t, src)
    elif t < T_CARD3:
        img = montage(A, t, src)
    elif t < T_TITLE:
        img = text_card(t, T_CARD3, [("6,000 VISITORS.", P.hf("cinzel", 84, 800), P.MOON, 0.05),
                                     ("ONE KILLER.", P.hf("abril", 120), P.GOLD, 0.4)], src)
    else:
        img = title(A, t, src)
    return film(A, img, t, i)

def build(outpath, poster_path=None, stills=None):
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    A = Assets(); bad = CL.forbidden()
    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{V}x{V}", "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
           "-crf", "24", "-preset", "slow", "-movflags", "+faststart", "-frames:v", str(N), outpath]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    hits_total = hit_frames = 0
    for i in range(N):
        t = i / FPS; src = []
        img = render(A, t, i, src).convert("RGB")
        h = kit.spoiler_scan(src, bad); hits_total += len(h); hit_frames += bool(h)
        if poster_path and i == int(14.4 * FPS):
            img.save(poster_path, quality=90)
        if stills is not None and i in stills:
            stills[i] = img.copy()
        proc.stdin.write(img.tobytes())
    proc.stdin.close(); proc.wait()
    return N, hits_total, hit_frames

if __name__ == "__main__":
    vid = os.path.join(HERE, "..", "video")
    picks = {int(s * FPS): None for s in (0.7, 2.6, 3.9, 5.6, 6.6, 7.6, 8.5, 9.0, 9.7, 10.2,
                                          10.6, 11.0, 11.4, 12.2, 14.4)}
    n, hits, hf_ = build(os.path.join(vid, f"{CL.SLUG}_story-trailer_1080.mp4"),
                         os.path.join(vid, f"{CL.SLUG}_story-trailer_poster.jpg"), picks)
    sheet = Image.new("RGB", (5 * 432, 3 * 432))
    for k, (i, im) in enumerate(sorted(picks.items())):
        sheet.paste(im.resize((432, 432)), ((k % 5) * 432, (k // 5) * 432))
    sheet.save(os.path.join(vid, f"{CL.SLUG}_story-trailer_storyboard.jpg"), quality=85)
    print(n, "frames; spoiler hits:", hits, "in", hf_, "frames")
