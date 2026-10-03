"""Listing video, an old-film trailer: 1080x1080, 14.0 s, 30 fps, no sound.

A film leader counts down; "This Halloween..." on a title board; the full moon rises over the
rooftops of Morrowmere while crows cross it and a figure in a pointed hat (seen from behind)
rises into the moonlight, the crescent pin glinting; "One coven. 6,000 visitors. One killer.";
real case pages are tossed onto the table one after another; a felt-tip marker strikes rows in
the Visitor Log; "Can you find the killer?"; the poster as the end card. Flicker, gate weave,
scratches and dust over everything. All drawn with code; every frame is spoiler-scanned.

    python3 video_trailer.py
"""
import math, os, random, subprocess
from PIL import Image, ImageDraw, ImageFilter
import imageio_ffmpeg
import kit
import case_listing as CL
import poster as P
import mockups as M

V = 1080; FPS = 30; DURATION = 14.0; N = int(round(DURATION * FPS))       # 420 frames
HERE = os.path.dirname(os.path.abspath(__file__))

T_TITLE1, T_MOON, T_TITLE2, T_PAGES, T_LOG, T_TITLE3, T_END = 1.0, 2.4, 5.0, 6.4, 8.6, 11.2, 12.0
CUTS = [T_TITLE1, T_MOON, T_TITLE2, T_PAGES, T_LOG, T_TITLE3, T_END]

def ease(t):
    t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
def seg(t, a, b):
    return ease((t - a) / (b - a))
def lerp(a, b, t):
    return a + (b - a) * t

# ---------------------------------------------------------------- precomputed pieces
class Assets:
    def __init__(self):
        self.M = M.Assets()
        k = V / 1200
        # moon scene layers
        self.sky = kit.Frame(V, V, P.PLUM)
        P.gradient(self.sky.img, (0x1A, 0x10, 0x26), P.AUB, (0, 0, V, 760))
        P.gradient(self.sky.img, P.AUB, P.PLUM, (0, 760, V, V))
        P.halftone(self.sky.img, (0, 0, V, 760), P.AMETHYST + (40,), 20, falloff=lambda x, y: 0.5)
        d = self.sky.draw(); rng = random.Random(3)
        for _ in range(60):
            P.star(d, rng.uniform(0, V), rng.uniform(0, 600), rng.uniform(2, 5), P.MOON)
        self.moon = Image.new("RGBA", (V, V), (0, 0, 0, 0))
        P.moon(self.moon, V / 2, V / 2, 260)
        fg = Image.new("RGBA", (V, V), (0, 0, 0, 0)); fd = ImageDraw.Draw(fg)
        P.village(fd, 760, 0, V, 64, P.NIGHT); P.stones(fd, 220, 764, 74, P.NIGHT)
        fd.rectangle([0, 790, V, V], fill=P.NIGHT)
        self.village = fg
        self.figure = Image.new("RGBA", (V, V), (0, 0, 0, 0))
        self.pin = P.figure_from_behind(self.figure, V / 2 + 8, 830, 170, P.NIGHT)
        # title boards
        self.board = kit.Frame(V, V, (0x0B, 0x07, 0x10))
        P.deco_frame(self.board, 60, 1.1, P.GOLD)
        # pages for the table toss
        L = self.M.L; p = self.M.p
        self.toss = [L.image(p[k_], 560) for k_ in ("map", "brews", "reading")]
        self.table = kit.Frame(V, V, P.PLUM)
        P.gradient(self.table.img, P.AUB, P.NIGHT)
        P.halftone(self.table.img, (0, 0, V, V), P.AMETHYST + (46,), 24, falloff=lambda x, y: 0.5)
        # the log close-up
        idx, rows, clip = M.log_clip(self.M, 34)
        zoom = 1000 / (clip[2] - clip[0])
        self.log = L.image(idx, int((clip[3] - clip[1]) * zoom), clip=clip)
        self.log_rows = rows
        # the end card
        self.end = P.hero_poster()
        self.end_img = self.end.img.resize((V, V), Image.LANCZOS)
        # film textures
        self.grain = []
        for i in range(6):
            n = Image.effect_noise((V, V), 70 + i).convert("L")
            self.grain.append(Image.merge("RGBA", (n, n, n, Image.new("L", (V, V), 34))))
        vm = Image.radial_gradient("L").resize((V, V)).point(lambda v: int(min(255, max(0, v - 70) * 1.5)))
        self.vignette = Image.new("RGBA", (V, V), (0, 0, 0, 255)); self.vignette.putalpha(vm)

# ---------------------------------------------------------------- scenes
def leader(A, t, src):
    f = kit.Frame(V, V, (0x2A, 0x24, 0x2C)); d = f.draw()
    n = 3 if t < 0.5 else 2
    ph = (t % 0.5) / 0.5
    d.ellipse([240, 240, 840, 840], outline=P.MOON, width=8); d.ellipse([300, 300, 780, 780], outline=P.MOON, width=4)
    d.line([(V / 2, 120), (V / 2, 960)], fill=P.MOON, width=4); d.line([(120, V / 2), (960, V / 2)], fill=P.MOON, width=4)
    d.pieslice([300, 300, 780, 780], -90, -90 + 360 * ph, fill=(0x6A, 0x5E, 0x6C))
    f.text((V / 2, V / 2 + 10), str(n), P.hf("bebas", 360), P.MOON, anchor="mm")
    src += f.sources
    return f.img

def title(A, t, t0, lines, src):
    """A title board: lines = [(text, font, colour, appear_at)]."""
    f = kit.Frame(V, V, (0, 0, 0)); f.img = A.board.img.copy()
    total = sum(fn.size * 1.25 for _, fn, _, _ in lines)
    y = V / 2 - total / 2
    for text, fn, col, at in lines:
        a = seg(t, t0 + at, t0 + at + 0.25)
        if a > 0:
            lay = kit.Frame(V, V, (0, 0, 0)); lay.img = Image.new("RGBA", (V, V), (0, 0, 0, 0))
            P.tracked(lay, V / 2, y + (1 - a) * 14, text, fn, col, fn.size * 0.08)
            lay.img.putalpha(lay.img.split()[3].point(lambda v: int(v * a)))
            f.img.alpha_composite(lay.img); src += lay.sources
        y += fn.size * 1.25
    return f.img

def moon_scene(A, t, src):
    p = (t - T_MOON) / (T_TITLE2 - T_MOON)
    img = A.sky.img.copy()
    rise = lerp(330, 0, ease(p * 1.4))                        # the moon rises from behind the roofs
    img.alpha_composite(A.moon, (0, int(-110 + rise)))
    d = ImageDraw.Draw(img)
    for i, (x0, y0, s, sp) in enumerate(((-120, 260, 46, 420), (-260, 180, 34, 470), (V + 80, 330, 40, -380),
                                         (V + 220, 220, 30, -440))):
        x = x0 + sp * (t - T_MOON); y = y0 + math.sin(t * 3 + i) * 12
        P.crow(d, x, y, s, P.NIGHT, math.sin(t * 14 + i * 1.7), 1 if sp > 0 else -1)
    up = lerp(260, 0, seg(t, T_MOON + 0.5, T_MOON + 1.9))
    img.alpha_composite(A.figure, (0, int(up)))          # the figure rises from behind the roofs
    img.alpha_composite(A.village)
    g = seg(t, T_MOON + 1.9, T_MOON + 2.1) * (1 - seg(t, T_MOON + 2.2, T_MOON + 2.6))
    lay = Image.new("RGBA", (V, V), (0, 0, 0, 0))
    if up < 120:
        P.crescent_pin(lay, A.pin[0], A.pin[1] + up, 11 + 5 * g)
    if g > 0:                                                 # a small star-glint on the pin
        gd = ImageDraw.Draw(lay)
        P.star(gd, A.pin[0] + 4, A.pin[1] + up, 34 * g, (0xFF, 0xF6, 0xE0, int(230 * g)))
    img.alpha_composite(lay)
    z = 1 + 0.06 * p                                          # slow push-in
    img = img.resize((int(V * z), int(V * z)), Image.BICUBIC).crop((int((V * z - V) / 2), int((V * z - V) / 2),
                                                                    int((V * z - V) / 2) + V, int((V * z - V) / 2) + V))
    return img

def pages_scene(A, t, src):
    f = kit.Frame(V, V, (0, 0, 0)); f.img = A.table.img.copy()
    spots = [(330, 540, -8), (560, 520, 5), (780, 560, -3)]
    for i, (pg, (x, y, ang)) in enumerate(zip(A.toss, spots)):
        t0 = T_PAGES + 0.1 + i * 0.6
        a = seg(t, t0, t0 + 0.45)
        if a <= 0:
            continue
        sc = lerp(1.5, 1.0, a)
        im = pg.img.resize((int(pg.img.width * sc), int(pg.img.height * sc)), Image.BICUBIC)
        page = kit.PageImg(im, pg.text, pg.zoom, pg.rect, pg.source)
        f.paste_page(page, lerp(x + (i - 1) * 300, x, a), lerp(y - 700, y, a), angle=lerp(ang - 25, ang, a))
    src += f.sources
    drift = 18 * seg(t, T_PAGES, T_LOG)
    return f.img.crop((int(drift), 0, int(drift) + V, V)).resize((V, V))

def log_scene(A, t, src):
    f = kit.Frame(V, V, P.PLUM); f.img = A.table.img.copy()
    pg = kit.PageImg(A.log.img.copy(), A.log.text, A.log.zoom, A.log.rect, A.log.source)
    pr = seg(t, T_LOG + 0.3, T_TITLE3 - 0.3)
    M.strike_rows(pg, A.log_rows, M.rowan_close, progress=pr, seed=4)
    pan = lerp(0, max(0, pg.img.height - 900), seg(t, T_LOG, T_TITLE3))
    crop = pg.img.crop((0, int(pan), pg.img.width, int(pan) + min(900, pg.img.height)))
    f.paste_page(kit.PageImg(crop, pg.text, pg.zoom, pg.rect, pg.source), V / 2, V / 2 + 10, angle=-1)
    src += f.sources
    return f.img

def end_card(A, t, src):
    z = lerp(1.08, 1.0, seg(t, T_END, T_END + 1.4))
    im = A.end_img.resize((int(V * z), int(V * z)), Image.BICUBIC)
    o = (im.width - V) // 2
    src += A.end.sources
    return im.crop((o, o, o + V, o + V))

# ---------------------------------------------------------------- the old-film look
def film(A, img, t, i):
    rng = random.Random(i * 7919)
    dx, dy = rng.uniform(-3, 3), rng.uniform(-4, 4)                         # gate weave
    out = Image.new("RGBA", (V, V), (0, 0, 0, 255)); out.alpha_composite(img.convert("RGBA"), (int(dx), int(dy)))
    fl = 1 + rng.uniform(-0.06, 0.05)                                       # flicker
    out = Image.eval(out.convert("RGB"), lambda v: min(255, int(v * fl))).convert("RGBA")
    out.alpha_composite(Image.new("RGBA", (V, V), (0x3A, 0x22, 0x10, 18)))   # warm print tint
    out.alpha_composite(A.grain[i % len(A.grain)])
    d = ImageDraw.Draw(out)
    for _ in range(rng.randint(0, 2)):                                      # scratches
        x = rng.uniform(40, V - 40)
        d.line([(x, 0), (x + rng.uniform(-6, 6), V)], fill=(0xF0, 0xE8, 0xD8, rng.randint(60, 140)), width=rng.choice((1, 2)))
    for _ in range(rng.randint(2, 7)):                                      # dust
        x, y, r = rng.uniform(0, V), rng.uniform(0, V), rng.uniform(1.5, 5)
        d.ellipse([x - r, y - r * 0.7, x + r, y + r * 0.7], fill=(0x10, 0x0A, 0x08, rng.randint(120, 220)))
    out.alpha_composite(A.vignette)
    if any(0 <= t - c < 1 / FPS for c in CUTS):                            # splice flash
        out.alpha_composite(Image.new("RGBA", (V, V), (0xFF, 0xF4, 0xE0, 150)))
    return out

def render(A, t, i, src):
    if t < T_TITLE1:
        img = leader(A, t, src)
    elif t < T_MOON:
        img = title(A, t, T_TITLE1, [("THIS HALLOWEEN…", P.hf("cinzel", 92, 800), P.MOON, 0.1),
                                     ("in the village of Morrowmere", P.hf("fell-it", 58), P.GOLD, 0.55)], src)
    elif t < T_TITLE2:
        img = moon_scene(A, t, src)
    elif t < T_PAGES:
        img = title(A, t, T_TITLE2, [("ONE COVEN.", P.hf("cinzel", 96, 800), P.MOON, 0.05),
                                     ("6,000 VISITORS.", P.hf("cinzel", 96, 800), P.MOON, 0.4),
                                     ("ONE KILLER.", P.hf("abril", 130), P.GOLD, 0.75)], src)
    elif t < T_LOG:
        img = pages_scene(A, t, src)
    elif t < T_TITLE3:
        img = log_scene(A, t, src)
    elif t < T_END:
        img = title(A, t, T_TITLE3, [("CAN YOU", P.hf("cinzel", 96, 800), P.MOON, 0.05),
                                     ("FIND THE KILLER?", P.fit("FIND THE KILLER?", "abril", 116, 860), P.GOLD, 0.3)], src)
    else:
        img = end_card(A, t, src)
    return film(A, img, t, i)

def build(outpath, poster_path=None, stills=None):
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    A = Assets(); bad = CL.forbidden()
    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{V}x{V}", "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
           "-crf", "26", "-preset", "slow", "-movflags", "+faststart", "-frames:v", str(N), outpath]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    hits_total = hit_frames = 0
    for i in range(N):
        t = i / FPS; src = []
        img = render(A, t, i, src).convert("RGB")
        h = kit.spoiler_scan(src, bad); hits_total += len(h); hit_frames += bool(h)
        if poster_path and i == int(4.6 * FPS):
            img.save(poster_path, quality=90)
        if stills is not None and i in stills:
            stills[i] = img.copy()
        proc.stdin.write(img.tobytes())
    proc.stdin.close(); proc.wait()
    return N, hits_total, hit_frames

if __name__ == "__main__":
    vid = os.path.join(HERE, "..", "video")
    picks = {int(s * FPS): None for s in (0.3, 1.8, 3.2, 4.6, 5.9, 7.6, 9.4, 10.9, 11.8, 13.6)}
    n, hits, hf_ = build(os.path.join(vid, f"{CL.SLUG}_old-film-trailer_1080.mp4"),
                         os.path.join(vid, f"{CL.SLUG}_old-film-trailer_poster.jpg"), picks)
    sheet = Image.new("RGB", (5 * 432, 2 * 432))
    for k, (i, im) in enumerate(sorted(picks.items())):
        sheet.paste(im.resize((432, 432)), ((k % 5) * 432, (k // 5) * 432))
    sheet.save(os.path.join(vid, f"{CL.SLUG}_old-film-trailer_storyboard.jpg"), quality=85)
    print(n, "frames; spoiler hits:", hits, "in", hf_, "frames")
