"""Listing video for the Storm & Moon Double Feature: 1080x1080, 15.0 s, 30 fps, no sound.

A double-feature night at an old cinema, drawn with code:
  0.0-2.0   the marquee lights up: QuietClueCo presents · A Double Feature · STORM & MOON
  2.0-4.0   a ticket tears along its perforation into FEATURE 1 and FEATURE 2
  4.0-7.0   the curtain opens on Feature 1: storm over the castle, lightning, the hooded figure
  7.0-10.0  Feature 2: the full moon rises over the village, crows, a pointed hat, the silver pin
  10.0-12.5 split screen: both Visitor Logs being struck through at once
  12.5-15.0 the double-feature poster (listing image 01)
Old-film look throughout (flicker, gate weave, grain, scratches, dust). Silhouettes and objects
only. Every frame is scanned for spoilers of both cases.

    python3 make_storm_layers.py && python3 video_bundle.py
"""
import math, os, random, subprocess
from PIL import Image, ImageDraw, ImageFilter
import imageio_ffmpeg
import mockups as M
import bundle as B
import kit
import poster as P

V = 1080; FPS = 30; DURATION = 15.0; N = int(round(DURATION * FPS))
HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "video_assets")
OUT = os.path.join(HERE, "..", "video")
T_MARQ, T_TICKET, T_F1, T_F2, T_SPLIT, T_END = 0.0, 2.0, 4.0, 7.0, 10.0, 12.5
CUTS = [T_TICKET, T_F1, T_F2, T_SPLIT, T_END]
BAR = 120
GOLD = B.MOON["accent"]; ORANGE = B.STORM["accent"]; CREAM = (0xF4, 0xEA, 0xD0); BLACK = (0x0B, 0x08, 0x0C)
WARM = (0xFF, 0xD9, 0x8A)

def ease(t):
    t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
def seg(t, a, b):
    return ease((t - a) / (b - a))
def lerp(a, b, t):
    return a + (b - a) * t

def push(img, z, cx=V / 2, cy=V / 2):
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

def letterbox(img):
    d = ImageDraw.Draw(img); d.rectangle([0, 0, V, BAR], fill=(0, 0, 0)); d.rectangle([0, V - BAR, V, V], fill=(0, 0, 0))

def caption(img, text, a, src, col=(0xF5, 0xC8, 0x70)):
    if a <= 0:
        return
    f = kit.Frame(V, V, (0, 0, 0)); f.img = Image.new("RGBA", (V, V), (0, 0, 0, 0))
    fnt = P.fit(text, "cinzel", 44, V - 90, 800, track=6)
    P.tracked(f, V / 2, V - BAR + 34 + (44 - fnt.size) / 2, text, fnt, col, 6)
    f.img.putalpha(f.img.split()[3].point(lambda v: int(v * a)))
    img.alpha_composite(f.img); src += f.sources

# ---------------------------------------------------------------- assets
class Assets:
    def __init__(self):
        rng = random.Random(3)
        self.M = M.Assets()
        # the marquee board and the theatre front
        front = Image.new("RGBA", (V, V)); M.two_tone(front, (0, 0, V, V))
        front.alpha_composite(Image.new("RGBA", (V, V), (0, 0, 0, 150)))
        self.front = front
        self.bulb_on = glow_sprite(13, (0xFF, 0xD2, 0x7A), 170, 8)
        self.bulbs = []
        x0, y0, x1, y1 = 70, 250, 1010, 790
        n_top = 22
        for i in range(n_top):
            self.bulbs.append((x0 + (i + 0.5) * (x1 - x0) / n_top, y0))
        for i in range(12):
            self.bulbs.append((x1, y0 + (i + 0.5) * (y1 - y0) / 12))
        for i in range(n_top):
            self.bulbs.append((x1 - (i + 0.5) * (x1 - x0) / n_top, y1))
        for i in range(12):
            self.bulbs.append((x0, y1 - (i + 0.5) * (y1 - y0) / 12))
        self.board = (x0, y0, x1, y1)
        self.title_font = P.fit("STORM & MOON", "abril", 190, x1 - x0 - 90)
        # the ticket, torn into two halves along the perforation
        tw, th = 800, 300
        tk = kit.Frame(tw, th, (0, 0, 0)); tk.img = Image.new("RGBA", (tw, th), (0, 0, 0, 0)); d = tk.draw()
        d.rounded_rectangle([0, 0, tw / 2, th], radius=22, fill=B.STORM["mid"])
        d.rounded_rectangle([tw / 2, 0, tw, th], radius=22, fill=B.MOON["mid"])
        d.rectangle([tw / 2 - 30, 0, tw / 2 + 30, th], fill=B.STORM["mid"]); d.rectangle([tw / 2, 0, tw / 2 + 30, th], fill=B.MOON["mid"])
        for sx in (0, tw):
            d.ellipse([sx - 34, th / 2 - 34, sx + 34, th / 2 + 34], fill=(0, 0, 0, 0))
        d.rectangle([14, 14, tw / 2 - 8, th - 14], outline=ORANGE, width=3)
        d.rectangle([tw / 2 + 8, 14, tw - 14, th - 14], outline=GOLD, width=3)
        for c, cx, col in ((B.CASES[0], tw / 4, ORANGE), (B.CASES[1], 3 * tw / 4, GOLD)):
            P.tracked(tk, cx, 40, "ADMIT ONE", P.hf("oswald", 28, 500), CREAM, 8)
            P.tracked(tk, cx, 80, c["feature"], P.hf("bebas", 92), col, 6)
            words = c["title"].upper().split(" ")
            l1 = " ".join(words[:-1]); l2 = words[-1]
            P.tracked(tk, cx, 180, l1, P.fit(l1, "cinzel", 30, tw / 2 - 70, 800, track=3), CREAM, 3)
            P.tracked(tk, cx, 220, l2, P.fit(l2, "cinzel", 40, tw / 2 - 70, 800, track=3), CREAM, 3)
        self.ticket_sources = tk.sources
        rng2 = random.Random(9); jag = [(tw / 2 + rng2.uniform(-7, 7), y) for y in range(0, th + 1, 12)]
        ml = Image.new("L", (tw, th), 0); ImageDraw.Draw(ml).polygon([(0, 0)] + jag + [(0, th)], fill=255)
        mr = Image.new("L", (tw, th), 0); ImageDraw.Draw(mr).polygon([(tw, 0)] + jag + [(tw, th)], fill=255)
        self.t_left = Image.new("RGBA", (tw, th), (0, 0, 0, 0)); self.t_left.paste(tk.img, (0, 0), Image.composite(tk.img.split()[3], ml, ml))
        self.t_right = Image.new("RGBA", (tw, th), (0, 0, 0, 0)); self.t_right.paste(tk.img, (0, 0), Image.composite(tk.img.split()[3], mr, mr))
        self.ticket = tk.img
        self.perf = jag
        # Feature 1: the storm layers (made by make_storm_layers.py with case 2's own drawing code)
        self.storm_bg = Image.open(os.path.join(ASSETS, "storm_bg.png")).convert("RGBA")
        self.storm_fig = Image.open(os.path.join(ASSETS, "storm_figure.png")).convert("RGBA")
        self.bolts = [Image.open(os.path.join(ASSETS, f"storm_bolt{k}.png")).convert("RGBA") for k in (0, 1)]
        # Feature 2: the moon over the village
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
        for x in (180, 420, 700, 930):
            vd.rectangle([x, 770, x + 14, 786], fill=P.GOLD)
        self.village = vil
        self.figure = Image.new("RGBA", (V, V), (0, 0, 0, 0))
        self.pin = P.figure_from_behind(self.figure, V / 2 + 8, 830, 170, P.NIGHT)
        # the two Visitor Logs
        self.logs = []
        for cs in self.M.cs:
            rows = M.log_rows(cs.L, cs.log)[:32]
            clip = (40, rows[0][0] - 22, 572, rows[-1][1] + 2)
            pg = cs.L.image(cs.log, int((clip[3] - clip[1]) * 500 / (clip[2] - clip[0])), clip=clip)
            self.logs.append((cs, pg, rows))
        # the end card: listing image 01
        self.end = M.m01_main(self.M)
        self.end_img = self.end.img.convert("RGBA").resize((V, V), Image.LANCZOS)
        # film textures
        self.grain = []
        for i in range(6):
            n = Image.effect_noise((V, V), 70 + i).convert("L")
            self.grain.append(Image.merge("RGBA", (n, n, n, Image.new("L", (V, V), 32))))
        vm = Image.radial_gradient("L").resize((V, V)).point(lambda v: int(min(200, max(0, v - 95) * 1.2)))
        self.vignette = Image.new("RGBA", (V, V), (0, 0, 0, 255)); self.vignette.putalpha(vm)

# ---------------------------------------------------------------- scenes
def marquee(A, t, src):
    img = A.front.copy(); d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = A.board
    d.rectangle([x0 - 20, y0 - 20, x1 + 20, y1 + 20], fill=(0x05, 0x03, 0x06))
    d.rectangle([x0, y0, x1, y1], outline=GOLD, width=4)
    on = int(len(A.bulbs) * seg(t, 0.05, 0.9))                         # the bulbs come on in a chase
    for i, (bx, by) in enumerate(A.bulbs):
        lit = i < on and (t < 1.0 or (i + int(t * 8)) % 7 != 0)
        if lit:
            paste_c(img, A.bulb_on, bx, by)
        ImageDraw.Draw(img).ellipse([bx - 7, by - 7, bx + 7, by + 7], fill=(0xFF, 0xE6, 0xA8) if lit else (0x3A, 0x30, 0x28))
    f = kit.Frame(V, V, (0, 0, 0)); f.img = img
    if t > 0.3:
        P.tracked(f, V / 2, y0 + 50, "QUIETCLUECO PRESENTS", P.hf("cinzel", 36, 700), CREAM, 10)
    if t > 0.55:
        P.tracked(f, V / 2, y0 + 108, "A DOUBLE FEATURE", P.hf("bebas", 96), (0xFF, 0xF1, 0xD2), 16)
    title = "STORM & MOON"
    n = int(len(title) * seg(t, 0.8, 1.6) + 0.999) if t > 0.8 else 0
    if n:
        lay = kit.Frame(V, V, (0, 0, 0)); lay.img = Image.new("RGBA", (V, V), (0, 0, 0, 0))
        full_w = A.title_font.getlength(title); x = V / 2 - full_w / 2
        ImageDraw.Draw(lay.img).text((x, y0 + 250), title[:n], font=A.title_font, fill=GOLD)
        lay.note("drawn", "text", title[:n])
        g = lay.img.filter(ImageFilter.GaussianBlur(14))
        img.alpha_composite(g); img.alpha_composite(lay.img); src += lay.sources
    if t > 1.4:
        P.tracked(f, V / 2, y1 - 80, "TONIGHT ONLY  ·  TWO MYSTERIES", P.hf("oswald", 36, 500), CREAM, 6)
    src += f.sources
    return push(img, 1 + 0.05 * seg(t, T_MARQ, T_TICKET))

def ticket(A, t, src):
    img = Image.new("RGBA", (V, V)); M.two_tone(img, (0, 0, V, V))
    img.alpha_composite(Image.new("RGBA", (V, V), (0, 0, 0, 110)))
    p = seg(t, 2.7, 3.5)
    if p <= 0:
        fr = kit.Frame(V, V, (0, 0, 0)); fr.img = img
        fr.paste(A.ticket, V / 2, V / 2 + lerp(30, 0, seg(t, T_TICKET, 2.4)), angle=-2, shadow=True, shadow_strength=170)
        d = ImageDraw.Draw(img)
    else:
        fr = kit.Frame(V, V, (0, 0, 0)); fr.img = img
        fr.paste(A.t_left, V / 2 - 95 * p, V / 2 + 40 * p, angle=-2 + 8 * p, shadow=True, shadow_strength=170)
        fr.paste(A.t_right, V / 2 + 95 * p, V / 2 + 25 * p, angle=-2 - 7 * p, shadow=True, shadow_strength=170)
    src += A.ticket_sources
    f = kit.Frame(V, V, (0, 0, 0)); f.img = img
    if t > 3.0:
        a = seg(t, 3.0, 3.4)
        lay = kit.Frame(V, V, (0, 0, 0)); lay.img = Image.new("RGBA", (V, V), (0, 0, 0, 0))
        P.tracked(lay, V / 2, 790, "TWO MYSTERIES  ·  ONE TICKET", P.hf("cinzel", 46, 800), CREAM, 10)
        lay.img.putalpha(lay.img.split()[3].point(lambda v: int(v * a))); img.alpha_composite(lay.img); src += lay.sources
    return img

def curtain(img, t):
    """Aubergine curtains drawing apart over the first feature."""
    o = seg(t, T_F1, T_F1 + 0.5)
    if o >= 1:
        return img
    w = int(V / 2 * (1 - o)) + 2
    for side in (0, 1):
        c = Image.new("RGBA", (w, V)); d = ImageDraw.Draw(c)
        for x in range(w):
            k = 0.55 + 0.45 * math.cos(x / 18.0)
            d.line([(x, 0), (x, V)], fill=(int(0x4A * k), int(0x1C * k), int(0x3A * k)))
        img.alpha_composite(c, (0 if side == 0 else V - w, 0))
    return img

def feature1(A, t, src):
    u = (t - T_F1) / (T_F2 - T_F1)
    img = A.storm_bg.copy()
    img.alpha_composite(A.storm_fig, (0, int(lerp(140, 10, ease(u)))))
    d = ImageDraw.Draw(img); rng = random.Random(int(t * FPS))             # falling rain
    for _ in range(140):
        x, y, L = rng.uniform(0, V), rng.uniform(0, V), rng.uniform(40, 90)
        d.line([(x, y), (x - L * 0.2, y + L)], fill=(0xC8, 0xD0, 0xD8, 70), width=2)
    fl = 0.0
    for t0, k in ((4.9, 0), (6.2, 1)):
        dt = t - t0
        if 0 <= dt < 0.5:
            v = math.exp(-dt * 9) + (0.6 * math.exp(-(dt - 0.12) * 10) if dt > 0.12 else 0)
            fl = max(fl, min(1, v))
            if dt < 0.3:
                img.alpha_composite(A.bolts[k])
    if fl > 0:
        img.alpha_composite(Image.new("RGBA", (V, V), (0xE0, 0xE8, 0xFF, int(120 * fl))))
    img = push(img, 1 + 0.06 * ease(u), V / 2, 520)
    img = curtain(img, t)
    letterbox(img)
    caption(img, "FEATURE 1  ·  STORM OVER CORVENMOOR", seg(t, T_F1 + 0.5, T_F1 + 0.9), src, ORANGE)
    return img

def feature2(A, t, src):
    u = (t - T_F2) / (T_SPLIT - T_F2)
    img = A.sky.copy()
    img.alpha_composite(A.moon, (0, int(lerp(300, -40, ease(min(1, u * 1.4))))))
    d = ImageDraw.Draw(img)
    for i, (x0, y0, s, sp) in enumerate(((-140, 300, 44, 380), (-300, 220, 32, 430), (V + 120, 380, 40, -360))):
        P.crow(d, x0 + sp * (t - T_F2), y0 + math.sin(t * 3 + i) * 10, s, P.NIGHT, math.sin(t * 13 + i * 1.7), 1 if sp > 0 else -1)
    up = lerp(260, 0, seg(t, T_F2 + 0.6, T_F2 + 2.0))
    img.alpha_composite(A.figure, (0, int(up)))
    img.alpha_composite(A.village)
    g = seg(t, 9.15, 9.35) * (1 - seg(t, 9.45, 9.85))
    lay = Image.new("RGBA", (V, V), (0, 0, 0, 0))
    if up < 120:
        P.crescent_pin(lay, A.pin[0], A.pin[1] + up, 11 + 5 * g)
    if g > 0:
        P.star(ImageDraw.Draw(lay), A.pin[0] + 4, A.pin[1] + up, 40 * g, (0xFF, 0xF6, 0xE0, int(230 * g)))
    img.alpha_composite(lay)
    img = push(img, 1 + 0.06 * ease(u), V / 2, 520)
    letterbox(img)
    caption(img, "FEATURE 2  ·  FULL MOON OVER MORROWMERE", seg(t, T_F2 + 0.3, T_F2 + 0.7), src, GOLD)
    return img

def split(A, t, src):
    img = Image.new("RGBA", (V, V)); M.two_tone(img, (0, 0, V, V)); M.seam(img, V / 2, 0, V, 6)
    f = kit.Frame(V, V, (0, 0, 0)); f.img = img
    pr = seg(t, T_SPLIT + 0.25, T_END - 0.2)
    for k, ((cs, pg0, rows), cx, ang) in enumerate(zip(A.logs, (V * 0.25 + 4, V * 0.75 - 4), (-1.5, 1.5))):
        pg = kit.PageImg(pg0.img.copy(), pg0.text, pg0.zoom, pg0.rect, pg0.source)
        pred, _ = M.STRIKE[cs.c["key"]]
        hits = [r for r in rows if pred(r)]
        fr = kit.Frame(pg.img.width, pg.img.height, (255, 255, 255)); fr.img = pg.img
        col = B.STORM["accent2"] if cs.c["key"] == "storm" else B.MOON["accent2"]
        for i, (y0, y1, x0, x1, *_r) in enumerate(hits):
            p = max(0.0, min(1.0, pr * len(hits) - i))
            if p > 0:
                a = pg.px(x0 - 4, (y0 + y1) / 2); b = pg.px(x1 + 4, (y0 + y1) / 2)
                kit.marker_strike(fr, a[0], a[1], b[0], (y1 - y0) * pg.zoom * 1.3, col, 170, 7 + i, p)
        f.paste_page(pg, cx, V / 2 + 20, angle=ang)
        P.tracked(f, cx, BAR + 26, cs.c["feature"], P.hf("bebas", 54), ORANGE if k == 0 else GOLD, 6)
    img = f.img; src += f.sources
    letterbox(img)
    caption(img, "TWO VISITOR LOGS  ·  12,000 SUSPECTS", seg(t, T_SPLIT + 0.2, T_SPLIT + 0.6), src)
    return img

def end_card(A, t, src):
    z = lerp(1.08, 1.0, seg(t, T_END, T_END + 1.6))
    src += A.end.sources
    return push(A.end_img.copy(), z)

# ---------------------------------------------------------------- the old-film look
def film(A, img, t, i):
    rng = random.Random(i * 7919)
    out = Image.new("RGBA", (V, V), (0, 0, 0, 255))
    out.alpha_composite(img.convert("RGBA"), (int(rng.uniform(-2.5, 2.5)), int(rng.uniform(-3, 3))))
    fl = 1 + rng.uniform(-0.05, 0.04)
    out = Image.eval(out.convert("RGB"), lambda v: min(255, int(v * fl))).convert("RGBA")
    out.alpha_composite(Image.new("RGBA", (V, V), (0x3A, 0x22, 0x10, 14)))
    out.alpha_composite(A.grain[i % len(A.grain)])
    d = ImageDraw.Draw(out)
    for _ in range(rng.randint(0, 2)):
        x = rng.uniform(40, V - 40)
        d.line([(x, 0), (x + rng.uniform(-6, 6), V)], fill=(0xF0, 0xE8, 0xD8, rng.randint(50, 120)), width=rng.choice((1, 2)))
    for _ in range(rng.randint(1, 6)):
        x, y, r = rng.uniform(0, V), rng.uniform(0, V), rng.uniform(1.5, 5)
        d.ellipse([x - r, y - r * 0.7, x + r, y + r * 0.7], fill=(0x10, 0x0A, 0x08, rng.randint(120, 220)))
    out.alpha_composite(A.vignette)
    if any(0 <= t - c < 1 / FPS for c in CUTS):
        out.alpha_composite(Image.new("RGBA", (V, V), (0xFF, 0xF4, 0xE0, 120)))
    return out

def render(A, t, i, src):
    if t < T_TICKET:
        img = marquee(A, t, src)
    elif t < T_F1:
        img = ticket(A, t, src)
    elif t < T_F2:
        img = feature1(A, t, src)
    elif t < T_SPLIT:
        img = feature2(A, t, src)
    elif t < T_END:
        img = split(A, t, src)
    else:
        img = end_card(A, t, src)
    return film(A, img, t, i)

def build(outpath, poster_path=None, stills=None):
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    A = Assets(); bad = A.M.bad
    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{V}x{V}", "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
           "-crf", "24", "-preset", "slow", "-movflags", "+faststart", "-frames:v", str(N), outpath]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    hits_total = hit_frames = 0; labels = set()
    for i in range(N):
        t = i / FPS; src = []
        img = render(A, t, i, src).convert("RGB")
        h = kit.spoiler_scan(src, bad); hits_total += len(h); hit_frames += bool(h); labels |= {x["label"] for x in h}
        if poster_path and i == int(1.9 * FPS):
            img.save(poster_path, quality=90)
        if stills is not None and i in stills:
            stills[i] = img.copy()
        proc.stdin.write(img.tobytes())
    proc.stdin.close(); proc.wait()
    return N, hits_total, hit_frames, labels

if __name__ == "__main__":
    picks = {int(s * FPS): None for s in (0.6, 1.8, 2.5, 3.4, 4.3, 5.0, 6.4, 7.8, 9.3, 10.8, 12.2, 14.4)}
    n, hits, hf_, labels = build(os.path.join(OUT, f"{B.SLUG}_double-feature-trailer_1080.mp4"),
                                 os.path.join(OUT, f"{B.SLUG}_double-feature-trailer_poster.jpg"), picks)
    sheet = Image.new("RGB", (4 * 432, 3 * 432))
    for k, (i, im) in enumerate(sorted(picks.items())):
        sheet.paste(im.resize((432, 432)), ((k % 4) * 432, (k // 4) * 432))
    sheet.save(os.path.join(OUT, f"{B.SLUG}_double-feature-trailer_storyboard.jpg"), quality=85)
    print(n, "frames; spoiler hits:", hits, "in", hf_, "frames", sorted(labels))
