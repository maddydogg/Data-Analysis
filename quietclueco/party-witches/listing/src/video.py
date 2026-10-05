"""Two listing videos for Murder at the Lantern Supper: 1080x1080, 30 fps, no sound, drawn with code.

trailer       13.5 s  an old-film trailer: film leader, "This Halloween…", the guests' lanterns climbing the hill
                      to Larkwell Hall under the full moon, "Twelve guests. One green glass. One killer.", the green
                      glass glinting by candlelight, kit pages tossed onto the table, "Who poisoned the Lantern
                      Keeper?", the poster as the end card.
presentation  14.0 s  the kit itself: the poster, the invitations, the character booklets, the Round 1 evidence
                      cards and the host guide, the potions, badges and awards, "What you get".

Flicker, gate weave, scratches and dust as in case No. 3. Every frame is a kit.Frame: the spoiler scan reads
every caption and every page region shown; only spoiler-free pages appear.
"""
import math, os, random, subprocess
from PIL import Image, ImageDraw
import imageio_ffmpeg
import kit
import poster as P
import party_art as A
import party_listing as PL
import mockups as M

V = 1080; FPS = 30
VID = os.path.join(PL.CASE, "listing", "video")

def ease(t):
    t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
def seg(t, a, b):
    return ease((t - a) / (b - a))
def lerp(a, b, t):
    return a + (b - a) * t

class Assets:
    def __init__(self):
        self.G = PL.Pages()
        M.phone_texts()
        # the hill scene without lanterns (they are animated) and without crows (animated too)
        self.scene = kit.Frame(V, V, P.PLUM)
        A.hall_scene(self.scene, 0.9, (720, 260), 170, 640, (540, 600), 70, crows=False, path=False)
        self.path = []
        for i in range(60):
            t = i / 59
            self.path.append((540 + math.sin(t * 3.4 + 0.4) * V * 0.16 * t - V * 0.02,
                              620 + (640 + 300 - 600) * t ** 1.3))
        self.board = kit.Frame(V, V, (0x0B, 0x07, 0x10))
        P.deco_frame(self.board, 60, 1.1, P.GOLD)
        # the glass by candlelight
        self.glass = kit.Frame(V, V, P.PLUM)
        P.gradient(self.glass.img, P.NIGHT, P.AUB)
        P.halftone(self.glass.img, (0, 0, V, V), P.AMETHYST + (50,), 22, falloff=lambda x, y: 0.5)
        d = self.glass.draw(); d.rectangle([0, 760, V, V], fill=(0x24, 0x16, 0x33))
        A.lantern(self.glass.img, 250, 640, 70); A.lantern(self.glass.img, 860, 610, 54)
        A.green_glass(self.glass.img, 560, 700, 180)
        # table for pages
        self.table = kit.Frame(V, V, P.PLUM)
        P.gradient(self.table.img, P.AUB, P.NIGHT)
        P.halftone(self.table.img, (0, 0, V, V), P.AMETHYST + (46,), 24, falloff=lambda x, y: 0.5)
        G = self.G
        self.toss = [kit.Pdf(os.path.join(PL.INV, f"{PL.SLUG}_invitation_fillable_5x7.pdf")).image(0, 560),
                     G.booklet_top("cordelia", 620), G.P.image(G.P.find("ROUND 1 · CARD 1"), 600)]
        self.booklets = [G.booklet_top(k, 640) for k in ("cordelia", "marigold", "rufus", "clementine")]
        self.inv = kit.Pdf(os.path.join(PL.INV, f"{PL.SLUG}_invitation_fillable_5x7.pdf")).image(0, 640)
        self.cards = [G.P.image(G.P.find("ROUND 1 · CARD 1"), 700), G.P.image(G.P.find("ROUND 1 · CARD 3"), 700)]
        self.hostp = [G.H.image(G.H.find("Welcome to the Lantern Supper"), 640), G.H.image(G.H.find("Casting", "CHOOSE ROLES"), 640)]
        self.extras = [G.P.image(G.P.find("The Potion Menu"), 620), G.P.image(G.P.find("THE LANTERN SUPPER · LARKWELL HALL", "Cordelia Heatherly"), 600),
                       G.P.image(G.P.find("Best Detective"), 600)]
        self.end = A.hero_poster(); self.end_img = self.end.img.resize((V, V), Image.LANCZOS)
        self.get = M.m10(G); self.get_img = self.get.img.resize((V, V), Image.LANCZOS)
        self.grain = []
        for i in range(6):
            n = Image.effect_noise((V, V), 70 + i).convert("L")
            self.grain.append(Image.merge("RGBA", (n, n, n, Image.new("L", (V, V), 30))))
        vm = Image.radial_gradient("L").resize((V, V)).point(lambda v: int(min(255, max(0, v - 70) * 1.5)))
        self.vignette = Image.new("RGBA", (V, V), (0, 0, 0, 255)); self.vignette.putalpha(vm)

# ---------------------------------------------------------------- scenes
def leader(A_, t, src):
    f = kit.Frame(V, V, (0x2A, 0x24, 0x2C)); d = f.draw()
    n = 3 if t < 0.5 else 2; ph = (t % 0.5) / 0.5
    d.ellipse([240, 240, 840, 840], outline=P.MOON, width=8); d.ellipse([300, 300, 780, 780], outline=P.MOON, width=4)
    d.line([(V / 2, 120), (V / 2, 960)], fill=P.MOON, width=4); d.line([(120, V / 2), (960, V / 2)], fill=P.MOON, width=4)
    d.pieslice([300, 300, 780, 780], -90, -90 + 360 * ph, fill=(0x6A, 0x5E, 0x6C))
    f.text((V / 2, V / 2 + 10), str(n), P.hf("bebas", 360), P.MOON, anchor="mm")
    src += f.sources; return f.img

def title(A_, t, t0, lines, src):
    f = kit.Frame(V, V, (0, 0, 0)); f.img = A_.board.img.copy()
    total = sum(fn.size * 1.3 for _, fn, _, _ in lines); y = V / 2 - total / 2
    for text, fn, col, at in lines:
        a = seg(t, t0 + at, t0 + at + 0.25)
        if a > 0:
            lay = kit.Frame(V, V, (0, 0, 0)); lay.img = Image.new("RGBA", (V, V), (0, 0, 0, 0))
            P.tracked(lay, V / 2, y + (1 - a) * 14, text, fn, col, fn.size * 0.06)
            lay.img.putalpha(lay.img.split()[3].point(lambda v: int(v * a)))
            f.img.alpha_composite(lay.img); src += lay.sources
        y += fn.size * 1.3
    return f.img

def hill_scene(A_, t, t0, t1, src):
    p = (t - t0) / (t1 - t0)
    img = A_.scene.img.copy()
    lay = Image.new("RGBA", (V, V), (0, 0, 0, 0))
    n = len(A_.path)
    for j in range(7):                                  # seven lanterns climbing the path, nearest last
        u = (1 - ((p * 0.55 + j / 7) % 1.0))
        x, y = A_.path[int(u * (n - 1))]
        r = 4 + 9 * u
        P.glow(lay, [x - r * 3, y - r * 3, x + r * 3, y + r * 3], P.GOLD, 110, r)
        ImageDraw.Draw(lay).ellipse([x - r, y - r, x + r, y + r], fill=A.WINDOW + (255,))
    img.alpha_composite(lay)
    d = ImageDraw.Draw(img)
    for i, (x0, y0, s, sp) in enumerate(((-120, 220, 40, 400), (-260, 150, 30, 460), (V + 80, 300, 36, -380))):
        x = x0 + sp * (t - t0); y = y0 + math.sin(t * 3 + i) * 10
        P.crow(d, x, y, s, P.NIGHT, math.sin(t * 14 + i * 1.7), 1 if sp > 0 else -1)
    z = 1 + 0.07 * p
    o = int((V * z - V) / 2)
    return img.resize((int(V * z), int(V * z)), Image.BICUBIC).crop((o, o, o + V, o + V))

def glass_scene(A_, t, t0, t1, src):
    p = (t - t0) / (t1 - t0)
    img = A_.glass.img.copy()
    g = math.sin(min(1, max(0, (p - 0.35) / 0.4)) * math.pi)
    if g > 0:
        lay = Image.new("RGBA", (V, V), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        P.star(d, 520, 500, 60 * g, (0xFF, 0xF6, 0xE0, int(230 * g)))
        img.alpha_composite(lay)
    z = 1 + 0.12 * ease(p); o = int((V * z - V) / 2)
    return img.resize((int(V * z), int(V * z)), Image.BICUBIC).crop((o, o + 30, o + V, o + V + 30))

def pages_scene(A_, t, t0, pages, spots, src, step=0.55):
    f = kit.Frame(V, V, (0, 0, 0)); f.img = A_.table.img.copy()
    for i, (pg, (x, y, ang)) in enumerate(zip(pages, spots)):
        a = seg(t, t0 + 0.1 + i * step, t0 + 0.1 + i * step + 0.45)
        if a <= 0:
            continue
        sc = lerp(1.4, 1.0, a)
        im = pg.img.resize((int(pg.img.width * sc), int(pg.img.height * sc)), Image.BICUBIC)
        f.paste_page(kit.PageImg(im, pg.text, pg.zoom, pg.rect, pg.source), lerp(x + (i - 1) * 260, x, a),
                     lerp(y - 700, y, a), angle=lerp(ang - 22, ang, a))
    src += f.sources
    return f

def caption(f, text, t, t0):
    a = seg(t, t0, t0 + 0.3)
    if a <= 0:
        return
    lay = kit.Frame(V, V, (0, 0, 0)); lay.img = Image.new("RGBA", (V, V), (0, 0, 0, 0)); d = lay.draw()
    d.rectangle([0, V - 150, V, V - 50], fill=P.PLUM + (230,))
    d.line([(0, V - 150), (V, V - 150)], fill=P.GOLD + (255,), width=4)
    P.tracked(lay, V / 2, V - 132, text, P.fit(text, "bebas", 70, V - 140, track=4), P.GOLD, 4)
    lay.img.putalpha(lay.img.split()[3].point(lambda v: int(v * a)))
    f.img.alpha_composite(lay.img); f.sources += lay.sources

def end_card(img_full, frame_src, t, t0, src):
    z = lerp(1.08, 1.0, seg(t, t0, t0 + 1.4))
    im = img_full.resize((int(V * z), int(V * z)), Image.BICUBIC); o = (im.width - V) // 2
    src += frame_src
    return im.crop((o, o, o + V, o + V))

def film(A_, img, t, i, cuts, strength=1.0):
    rng = random.Random(i * 7919)
    dx, dy = rng.uniform(-3, 3) * strength, rng.uniform(-4, 4) * strength
    out = Image.new("RGBA", (V, V), (0, 0, 0, 255)); out.alpha_composite(img.convert("RGBA"), (int(dx), int(dy)))
    fl = 1 + rng.uniform(-0.06, 0.05) * strength
    out = Image.eval(out.convert("RGB"), lambda v: min(255, int(v * fl))).convert("RGBA")
    out.alpha_composite(Image.new("RGBA", (V, V), (0x3A, 0x22, 0x10, int(18 * strength))))
    out.alpha_composite(A_.grain[i % len(A_.grain)])
    d = ImageDraw.Draw(out)
    for _ in range(rng.randint(0, 2) if strength > 0.5 else 0):
        x = rng.uniform(40, V - 40)
        d.line([(x, 0), (x + rng.uniform(-6, 6), V)], fill=(0xF0, 0xE8, 0xD8, rng.randint(60, 140)), width=rng.choice((1, 2)))
    for _ in range(rng.randint(2, 7) if strength > 0.5 else rng.randint(0, 2)):
        x, y, r = rng.uniform(0, V), rng.uniform(0, V), rng.uniform(1.5, 5)
        d.ellipse([x - r, y - r * 0.7, x + r, y + r * 0.7], fill=(0x10, 0x0A, 0x08, rng.randint(120, 220)))
    if strength >= 1:
        out.alpha_composite(A_.vignette)
    else:
        v = A_.vignette.copy(); v.putalpha(v.split()[3].point(lambda a: int(a * 0.45)))
        out.alpha_composite(v)
    if any(0 <= t - c < 1 / FPS for c in cuts):
        out.alpha_composite(Image.new("RGBA", (V, V), (0xFF, 0xF4, 0xE0, 150)))
    return out

# ---------------------------------------------------------------- the trailer
TR = dict(N=405, cuts=[1.0, 2.4, 5.0, 6.4, 8.4, 10.8, 12.0])
def trailer(A_, t, i, src):
    if t < 1.0:
        img = leader(A_, t, src)
    elif t < 2.4:
        img = title(A_, t, 1.0, [("THIS HALLOWEEN…", P.hf("cinzel", 92, 800), P.MOON, 0.1),
                                  ("the Hearth Circle sits down to supper", P.hf("fell-it", 52), P.GOLD, 0.55)], src)
    elif t < 5.0:
        img = hill_scene(A_, t, 2.4, 5.0, src)
    elif t < 6.4:
        img = title(A_, t, 5.0, [("TWELVE GUESTS.", P.hf("cinzel", 88, 800), P.MOON, 0.05),
                                  ("ONE GREEN GLASS.", P.hf("cinzel", 88, 800), P.MOON, 0.4),
                                  ("ONE KILLER.", P.hf("abril", 130), P.GOLD, 0.75)], src)
    elif t < 8.4:
        img = glass_scene(A_, t, 6.4, 8.4, src)
    elif t < 10.8:
        img = pages_scene(A_, t, 8.4, A_.toss, [(330, 540, -8), (560, 520, 5), (790, 560, -3)], src, 0.6).img
    elif t < 12.0:
        img = title(A_, t, 10.8, [("WHO POISONED", P.hf("cinzel", 92, 800), P.MOON, 0.05),
                                   ("THE LANTERN KEEPER?", P.fit("THE LANTERN KEEPER?", "abril", 112, 900), P.GOLD, 0.3)], src)
    else:
        img = end_card(A_.end_img, A_.end.sources, t, 12.0, src)
    return film(A_, img, t, i, TR["cuts"])

# ---------------------------------------------------------------- the kit presentation
PR = dict(N=420, cuts=[2.0, 4.6, 7.2, 9.8, 12.0])
def presentation(A_, t, i, src):
    if t < 2.0:
        img = end_card(A_.end_img, A_.end.sources, t, -0.6, src)
    elif t < 4.6:
        f = pages_scene(A_, t, 2.0, [A_.inv], [(400, 500, -5)], src)
        for j, (name, x, y, ang) in enumerate((("00_invitation.png", 760, 480, 4), ("03_silas.png", 900, 560, -3))):
            if t > 2.5 + j * 0.4:
                M.png_in_phone(f, os.path.join(PL.INV, "phone", name), x, y + 600 * (1 - seg(t, 2.5 + j * 0.4, 2.9 + j * 0.4)), 640, ang)
        caption(f, "INVITATIONS TO PRINT OR TEXT", t, 2.2)
        src += f.sources
        img = f.img
    elif t < 7.2:
        f = pages_scene(A_, t, 4.6, A_.booklets, [(260, 470, -6), (520, 440, 3), (780, 470, -2), (540, 640, 4)], src, 0.4)
        caption(f, "12 CHARACTER BOOKLETS", t, 4.8)
        src += f.sources; img = f.img
    elif t < 9.8:
        f = pages_scene(A_, t, 7.2, A_.cards + A_.hostp, [(300, 430, -4), (420, 640, 3), (720, 430, 4), (800, 620, -3)], src, 0.4)
        caption(f, "EVIDENCE CARDS · HOST GUIDE", t, 7.4)
        src += f.sources; img = f.img
    elif t < 12.0:
        f = pages_scene(A_, t, 9.8, A_.extras, [(300, 480, -5), (560, 520, 3), (800, 480, -3)], src, 0.45)
        caption(f, "POTIONS · NAME BADGES · AWARDS", t, 10.0)
        src += f.sources; img = f.img
    else:
        img = end_card(A_.get_img, A_.get.sources, t, 12.0, src)
    return film(A_, img, t, i, PR["cuts"], strength=0.6)

# ---------------------------------------------------------------- encode
def encode(A_, fn, spec, outpath, poster_at, picks):
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    bad = PL.forbidden(); N = spec["N"]
    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{V}x{V}", "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
           "-crf", "24", "-preset", "slow", "-movflags", "+faststart", "-frames:v", str(N), outpath]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    hits = hit_frames = 0; stills = {}
    for i in range(N):
        t = i / FPS; src = []
        img = fn(A_, t, i, src).convert("RGB")
        h = kit.spoiler_scan(src, bad); hits += len(h); hit_frames += bool(h)
        if i == int(poster_at * FPS):
            img.save(outpath.replace("_1080.mp4", "_poster.jpg"), quality=90)
        if i in picks:
            stills[i] = img
        proc.stdin.write(img.tobytes())
    proc.stdin.close(); proc.wait()
    sheet = Image.new("RGB", (4 * 360, 3 * 360))
    for k, (i, im) in enumerate(sorted(stills.items())):
        sheet.paste(im.resize((360, 360)), ((k % 4) * 360, (k // 4) * 360))
    sheet.save(outpath.replace("_1080.mp4", "_storyboard.jpg"), quality=85)
    return N, hits, hit_frames

def build(only=None):
    A_ = Assets(); out = {}
    if only in (None, "trailer"):
        p = os.path.join(VID, f"{PL.SLUG}_old-film-trailer_1080.mp4")
        out["trailer"] = (p,) + encode(A_, trailer, TR, p, 3.6, {int(s * FPS) for s in
                                       (0.3, 1.8, 3.0, 4.4, 5.9, 7.2, 8.0, 9.4, 10.4, 11.4, 12.4, 13.3)})
    if only in (None, "presentation"):
        p = os.path.join(VID, f"{PL.SLUG}_kit-presentation_1080.mp4")
        out["presentation"] = (p,) + encode(A_, presentation, PR, p, 13.5, {int(s * FPS) for s in
                                            (1.0, 2.8, 3.8, 5.2, 6.4, 7.8, 9.0, 10.4, 11.4, 12.4, 13.2, 13.9)})
    return out

if __name__ == "__main__":
    import sys
    for k, v in build(sys.argv[1] if len(sys.argv) > 1 else None).items():
        print(k, v)
