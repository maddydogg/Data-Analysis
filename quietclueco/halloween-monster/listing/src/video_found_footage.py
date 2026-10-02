"""Listing video, found-footage trailer: 1080x1080, exactly 14.9 s, 30 fps, no sound.

The night watchman's tower camera. It switches on (20:49), climbs the spiral stair by
flashlight, a lightning flash through an arrow slit, the door at the top with green light under
it, the door swings open, the beam sweeps the laboratory: shelves, the smoking goblet of potion
punch, then the curator slumped over the Baron's workbench (20:50:13). Lightning lights the
whole room for an instant, the camera drops, SIGNAL LOST, two title cards over static, then
the end card with the monster-movie poster cover. Everything is drawn with code; the body is
only ever a silhouette. Every frame is spoiler-scanned.

    python3 video_found_footage.py
"""
import math, os, random, subprocess
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageFont
import imageio_ffmpeg
import kit
import case_listing as CL
import horror_heroes as HH
from horror_heroes import hf, layer, glow, lightning, bolt_path, gradient
import trailer_concepts as TC

V = 1080; FPS = 30; DURATION = 14.9; N = int(round(DURATION * FPS))       # 447 frames
HERE = os.path.dirname(os.path.abspath(__file__))
MONO = os.path.join(HERE, "..", "..", "src", "fonts", "CourierPrime-Bold.ttf")
WHITE = (0xF4, 0xF4, 0xF4)

T_ON, T_STAIRS, T_DOOR, T_OPEN, T_LAB, T_FIND, T_DROP, T_CARDS, T_END = 0.0, 1.1, 4.5, 5.25, 6.0, 8.5, 10.05, 10.5, 12.2
FLASHES = [(3.05, 0.9), (9.15, 1.0)]

def ease(t):
    t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
def seg(t, a, b):
    return ease((t - a) / (b - a))
def lerp(a, b, t):
    return a + (b - a) * t
def flash(t):
    v = 0.0
    for t0, k in FLASHES:
        dt = t - t0
        if 0 <= dt < 0.45:
            v = max(v, k * (math.exp(-dt * 16) + (0.7 * math.exp(-(dt - 0.15) * 16) if dt > 0.15 else 0)))
    return min(1.0, v)

def dark_copy(img, k=0.06):
    return Image.eval(img.convert("RGB"), lambda v: int(v * k)).convert("RGBA")

# ---------------------------------------------------------------- precomputed scenes
class Assets:
    def __init__(self):
        rng = random.Random(1)
        # spiral stair: a tall strip the camera climbs through
        st = Image.new("RGBA", (V, 2700)); TC.stone_wall(st, (0, 0, V, 2700), (0x4C, 0x47, 0x44), 7, (150, 86))
        d = ImageDraw.Draw(st)
        for i in range(18):
            y = 2680 - i * 150; inner = 120 + (i % 2) * 30
            d.polygon([(inner, y), (V - 40, y - 60), (V - 40, y - 10), (inner, y + 45)], fill=(0x5E, 0x58, 0x54))       # tread
            d.polygon([(inner, y + 45), (V - 40, y - 10), (V - 40, y + 70), (inner, y + 110)], fill=(0x2C, 0x28, 0x26))   # riser
            d.line([(inner, y), (V - 40, y - 60)], fill=(0x7A, 0x74, 0x70), width=4)
        d.rectangle([0, 0, 120, 2700], fill=(0x30, 0x2C, 0x2A))                                                       # central column
        d.rectangle([700, 1200, 760, 1460], fill=(0x10, 0x10, 0x18))                                                   # arrow slit
        self.stairs = st; self.stairs_dark = dark_copy(st)
        self.slit = (700, 1200, 760, 1460)
        w = Image.new("RGBA", (V, V)); TC.stone_wall(w, (0, 0, V, V), (0x40, 0x3C, 0x3A), 12, (120, 70))
        self.shaft = w
        # the door at the top of the stair
        dr = Image.new("RGBA", (V, V)); TC.stone_wall(dr, (0, 0, V, V), (0x4C, 0x47, 0x44), 9, (150, 86))
        d = ImageDraw.Draw(dr)
        d.pieslice([300, 140, 780, 620], 180, 360, fill=(0x22, 0x1E, 0x1C)); d.rectangle([300, 380, 780, 1000], fill=(0x22, 0x1E, 0x1C))
        self.door_bg = dr; self.door_bg_dark = dark_copy(dr)
        # the laboratory, wider than the frame so the camera can pan
        lab = Image.new("RGBA", (1500, V)); TC.stone_wall(lab, (0, 0, 1500, V), (0x4A, 0x46, 0x44), 3, (150, 90))
        d = ImageDraw.Draw(lab)
        d.rectangle([1180, 120, 1360, 400], fill=(0x0C, 0x0E, 0x16))
        d.rectangle([1180, 255, 1360, 265], fill=(0x22, 0x20, 0x20)); d.rectangle([1266, 120, 1274, 400], fill=(0x22, 0x20, 0x20))
        for k in range(3):
            y = 300 + k * 110; d.rectangle([60, y, 420, y + 14], fill=(0x2A, 0x22, 0x1A))
            for j in range(5):
                jx = 80 + j * 68; d.rounded_rectangle([jx, y - 70, jx + 46, y], radius=8, fill=(0x3C, 0x48, 0x40))
        self.top = 720
        TC.bench(d, 220, 1360, self.top, 340, (0x3A, 0x28, 0x1C), (0x26, 0x1A, 0x12))
        TC.apparatus(d, 1060, self.top, 200, (0x24, 0x22, 0x26))
        TC.slumped(d, 600, self.top, 260, (0x16, 0x13, 0x15))
        self.goblet = (930, self.top, 110)
        TC.goblet(lab, *self.goblet, fog=False)
        self.lab = lab; self.lab_dark = dark_copy(lab)
        # flashlight: a soft ellipse sprite
        m = Image.new("L", (1100, 900), 0); ImageDraw.Draw(m).ellipse([200, 160, 900, 740], fill=255)
        self.beam = m.filter(ImageFilter.GaussianBlur(110))
        # fog puffs over the goblet (a few pre-blurred sprites)
        self.fog = []
        for k in range(4):
            f, fd = layer((300, 420)); r2 = random.Random(k)
            for i in range(16):
                x = 150 + math.sin(i * 0.8 + k) * 40 + r2.uniform(-20, 20); y = 380 - i * 22; r = r2.uniform(18, 40)
                fd.ellipse([x - r * 1.6, y - r, x + r * 1.6, y + r], fill=(0xD8, 0xF6, 0xC8, int(r2.uniform(35, 75))))
            self.fog.append(f.filter(ImageFilter.GaussianBlur(10)))
        # camcorder textures
        self.scan, sd = layer((V, V))
        for y in range(0, V, 3):
            sd.line([(0, y), (V, y)], fill=(0, 0, 0, 55))
        self.noise = [Image.effect_noise((V, V), 80 + i * 6).convert("RGBA") for i in range(6)]
        self.grain = []
        for i in range(6):
            n = Image.effect_noise((V, V), 60 + i).convert("L")
            self.grain.append(Image.merge("RGBA", (n, n, n, Image.new("L", (V, V), 30))))
        vm = Image.radial_gradient("L").resize((V, V)).point(lambda v: int(min(255, max(0, v - 60) * 1.4)))
        self.vignette = Image.new("RGBA", (V, V), (0, 0, 0, 255)); self.vignette.putalpha(vm)
        self.mono = ImageFont.truetype(MONO, 34); self.mono_big = ImageFont.truetype(MONO, 64)
        self.cover = HH.cover_monster_movie(1200, 1800)
        self.cover_img = self.cover.img.resize((380, 570), Image.LANCZOS)

# ---------------------------------------------------------------- per-frame pieces
def beam_mask(A, cx, cy, scale=1.0):
    m = Image.new("L", (V, V), 0)
    b = A.beam if scale == 1.0 else A.beam.resize((int(A.beam.width * scale), int(A.beam.height * scale)))
    m.paste(b, (int(cx - b.width / 2), int(cy - b.height / 2)))
    return m

def lit(lit_img, dark_img, mask, fl):
    out = Image.composite(lit_img, dark_img, mask)
    if fl > 0:
        out = Image.blend(out, lit_img, min(1.0, fl))
        out.alpha_composite(Image.new("RGBA", out.size, (0xE0, 0xE6, 0xFF, int(110 * fl))))
    return out

def shake(t, amp):
    return (math.sin(t * 23) * amp + math.sin(t * 7.3) * amp * 0.6, math.cos(t * 19) * amp * 0.7 + math.sin(t * 5.1) * amp * 0.5)

def stair_steps(d, phase, lightness=1.0):
    """A narrow spiral stair in perspective, climbing away from the camera and curving right,
    with the outer wall on the right and the central column on the left. phase grows as the
    camera climbs, so the steps slide towards and under the lens."""
    VPX, VPY = 470, 230
    DZ = 0.32
    def proj(z):
        xc = VPX + 420 * (1 - 1 / z) * 0.9 + 70 / z           # farther steps drift right: the stair turns
        return xc, VPY + 640 / z, 330 / z                       # centre x, front-edge y, half width
    k0 = math.floor(phase)
    steps = [0.55 + (k - phase) * DZ for k in range(k0, k0 + 16)]
    steps = [z for z in steps if z > 0.42]
    col = lambda c: tuple(int(v * lightness) for v in c)
    for z in sorted(steps, reverse=True):                       # far to near
        xc, yf, w = proj(z); xn, yn, wn = proj(z + DZ); r = 150 / z
        d.polygon([(xc - w, yf - r), (xc + w, yf - r), (xn + wn, yn), (xn - wn, yn)], fill=col((0x74, 0x6C, 0x66)))  # tread
        d.polygon([(xc - w, yf), (xc + w, yf), (xc + w, yf - r), (xc - w, yf - r)], fill=col((0x30, 0x2B, 0x29)))    # riser
        d.line([(xc - w, yf - r), (xc + w, yf - r)], fill=col((0x9A, 0x92, 0x8A)), width=max(2, int(5 / z)))         # worn nose
        d.polygon([(0, yf + 40), (xc - w, yf), (xc - w, yf - r - 40 / z), (0, yf - r - 60 / z)], fill=col((0x22, 0x1F, 0x1E)))   # central column
    return proj

def scene_stairs(A, t):
    p = seg(t, T_STAIRS, T_DOOR - 0.1)
    phase = p * 7.5
    bob = math.sin((t - T_STAIRS) * 2 * math.pi * 1.6) * 14; sx, sy = shake(t, 6)
    img = A.shaft.copy(); d = ImageDraw.Draw(img)
    proj = stair_steps(d, phase)
    zs = 0.55 + (7 - phase) * 0.32                                          # an arrow slit in the outer wall
    fl = flash(t)
    if zs > 0.5:
        xc, yf, w = proj(zs); sw, sh = 40 / zs, 180 / zs; x = min(V - 30, xc + w + 30 / zs)
        d.rectangle([x, yf - 360 / zs - sh, x + sw, yf - 360 / zs], fill=(0xE8, 0xEE, 0xFF) if fl > 0.05 else (0x10, 0x10, 0x18))
    dark = dark_copy(img)
    out = lit(img, dark, beam_mask(A, V / 2 + sx * 4, V * 0.6 + bob), fl)
    return out.rotate(sx * 0.15, resample=Image.BICUBIC)

def scene_door(A, t):
    sx, sy = shake(t, 5)
    out = lit(A.door_bg, A.door_bg_dark, beam_mask(A, V / 2 + sx * 3, V * 0.55 + sy * 3), flash(t))
    d = ImageDraw.Draw(out)
    g = 60 + 120 * seg(t, T_DOOR, T_OPEN)                              # green light under the door
    glow(out, ("ellipse", [340, 940, 740, 1060]), TC.POTION, int(g), 30)
    o = seg(t, T_OPEN, T_LAB - 0.15)                                   # the door swings inward
    if o > 0:
        glow(out, ("ellipse", [320, 320, 760, 1000]), TC.POTION, int(140 * o), 80)
    x_edge = lerp(770, 330, o)
    d = ImageDraw.Draw(out)
    d.polygon([(310, 380), (x_edge, 380 + 40 * o), (x_edge, 1000 - 30 * o), (310, 1000)], fill=(0x4A, 0x32, 0x20))
    for k in range(5):
        y = 420 + k * 120; d.line([(310, y), (x_edge, y + 30 * o)], fill=(0x2A, 0x1C, 0x10), width=10)
    d.ellipse([x_edge - 60 * (1 - o) - 16, 680, x_edge - 60 * (1 - o) + 16, 712], fill=(0x88, 0x80, 0x70))
    return out

def scene_lab(A, t):
    # camera pan and beam path: shelves -> goblet -> the body
    pan = lerp(0, 420, seg(t, T_LAB, T_FIND + 0.2))
    if t < T_LAB + 1.2:
        bx, by = lerp(240, 420, seg(t, T_LAB, T_LAB + 1.2)), 380
    elif t < T_FIND:
        bx, by = lerp(420, A.goblet[0], seg(t, T_LAB + 1.2, T_LAB + 2.0)), lerp(380, A.top - 80, seg(t, T_LAB + 1.2, T_LAB + 2.0))
    else:
        bx, by = lerp(A.goblet[0], 760, seg(t, T_FIND, T_FIND + 0.45)), lerp(A.top - 80, A.top - 20, seg(t, T_FIND, T_FIND + 0.45))
    amp = 4 if t < T_FIND else 4 + 14 * seg(t, T_FIND, T_FIND + 0.3)
    sx, sy = shake(t, amp)
    x0 = int(min(max(pan + sx, 0), 1500 - V))
    box = (x0, 0, x0 + V, V)
    out = lit(A.lab.crop(box), A.lab_dark.crop(box), beam_mask(A, bx - x0, by + sy, 1.15 if t >= T_FIND else 1.0), flash(t))
    gx, gb, gs = A.goblet                                               # the potion glows with or without the beam
    glow(out, ("ellipse", [gx - x0 - 150, gb - 170, gx - x0 + 150, gb - 20]), TC.POTION, 110, 40)
    fog = A.fog[int(t * 8) % len(A.fog)]
    out.alpha_composite(fog, (int(gx - x0 - 150), int(gb - gs * 0.8 - 400 - (t * 30) % 20)))
    fl = flash(t)
    if fl > 0.2:                                                        # lightning in the window
        lay = Image.new("RGBA", out.size, (0, 0, 0, 0))
        lightning(lay, bolt_path(1270 - x0, 125, 395, 3, 26), 4); out.alpha_composite(lay)
    return out

def static_frame(A, t, strength=1.0):
    n = A.noise[int(t * 30) % len(A.noise)].copy()
    out = Image.new("RGBA", (V, V), (0, 0, 0, 255))
    n.putalpha(int(255 * strength * 0.55)); out.alpha_composite(n)
    return out

def tracking(img, t, k):
    """VHS tracking glitch: a few horizontal bands shifted sideways."""
    if k <= 0:
        return img
    rng = random.Random(int(t * 30))
    out = img.copy()
    for _ in range(int(2 + 4 * k)):
        y = rng.randrange(0, V - 60); h = rng.randrange(8, 60); dx = int(rng.uniform(-80, 80) * k)
        band = img.crop((0, y, V, y + h)); out.paste(band, (dx, y))
    return out

def hud(f, A, t, sources):
    d = f.draw()
    if int(t * 2) % 2 == 0:
        d.ellipse([60, 66, 92, 98], fill=(0xE8, 0x22, 0x22))
    secs = 49 * 60 + 40 + int(t * 3.8)
    stamp = f"OCT 31  20:{secs // 60:02d}:{secs % 60:02d}"
    for text, xy in (("REC", (108, 58)), ("TOWER CAM 2", (60, V - 96)), (stamp, (V - 470, V - 96))):
        d.text(xy, text, font=A.mono, fill=WHITE); sources.append(("drawn", "hud", text))
    d.rectangle([V - 170, 62, V - 82, 100], outline=WHITE, width=4); d.rectangle([V - 82, 72, V - 72, 90], fill=WHITE)
    d.rectangle([V - 162, 70, V - 128 if t > 9 else V - 104, 92], fill=WHITE)
    for cx, cy, sx, sy in ((40, 40, 1, 1), (V - 40, 40, -1, 1), (40, V - 40, 1, -1), (V - 40, V - 40, -1, -1)):
        d.line([(cx, cy), (cx + sx * 60, cy)], fill=WHITE, width=4); d.line([(cx, cy), (cx, cy + sy * 60)], fill=WHITE, width=4)

def camcorder_look(A, img, t):
    r, g, b, a = img.split()
    img = Image.merge("RGBA", (ImageChops.offset(r, 3, 0), g, ImageChops.offset(b, -3, 0), a))
    img.alpha_composite(A.scan); img.alpha_composite(A.grain[int(t * 24) % len(A.grain)]); img.alpha_composite(A.vignette)
    return img

def end_card(A, t, sources):
    f = kit.Frame(V, V, (0x07, 0x06, 0x08)); e = seg(t, T_END, T_END + 0.5)
    f.img.paste(A.cover_img, (70, int(255 + (1 - e) * 40))); sources.extend(A.cover.sources)
    q = seg(t, T_END + 0.4, T_END + 1.0)
    lay = kit.Frame(V, V, (0, 0, 0)); lay.img = Image.new("RGBA", (V, V), (0, 0, 0, 0))
    lay.text((770, 230), "Storm over\nCorvenmoor", hf("abril", 74), kit.PARCH, anchor="ma", align="center")
    lay.text((770, 450), "Can you find the killer?", hf("fell-it", 54), kit.MUST, anchor="ma")
    kit.pill(lay, (770, 600), "Printable + iPad", kit.font("black", 46), kit.MUST, kit.GREEN)
    lay.text((770, 690), "6,000 suspects · 18 clues", kit.font("bold", 40), kit.PARCH, anchor="ma")
    lay.text((770, 930), CL.C.BRAND, hf("abril", 50), kit.PARCH, anchor="ma")
    lay.img.putalpha(lay.img.split()[3].point(lambda v: int(v * q)))
    f.img.alpha_composite(lay.img); sources.extend(lay.sources)
    return f.img

def render(A, t, sources):
    if t < T_STAIRS:                                                    # camera switching on
        k = 1 - seg(t, 0.3, T_STAIRS)
        base = scene_stairs(A, T_STAIRS + 0.01) if t > 0.4 else Image.new("RGBA", (V, V), (0, 0, 0, 255))
        st = static_frame(A, t, k); base = Image.blend(base, st, k * 0.8) if t > 0.4 else st
        img = tracking(base, t, k)
    elif t < T_DOOR:
        img = scene_stairs(A, t); img = tracking(img, t, 0.6 * seg(t, T_DOOR - 0.15, T_DOOR))
    elif t < T_LAB:
        img = scene_door(A, t); img = tracking(img, t, 0.8 * (1 - seg(t, T_DOOR, T_DOOR + 0.12)) + 0.7 * seg(t, T_LAB - 0.12, T_LAB))
    elif t < T_DROP:
        img = scene_lab(A, t); img = tracking(img, t, 0.5 * (1 - seg(t, T_LAB, T_LAB + 0.12)))
    elif t < T_CARDS:                                                   # the camera drops
        p = seg(t, T_DROP, T_CARDS)
        base = scene_lab(A, T_DROP).rotate(-35 * p, resample=Image.BICUBIC, center=(V / 2, V * 0.8))
        img = tracking(Image.blend(base, static_frame(A, t), p), t, 1.0)
    elif t < T_END:
        img = static_frame(A, t, 0.55)
    else:
        img = end_card(A, t, sources)
    f = kit.Frame(V, V, (0, 0, 0)); f.img = img.convert("RGBA")
    if t < T_END:
        f.img = camcorder_look(A, f.img, t)
        if t < T_CARDS:
            hud(f, A, t, sources)
        d = f.draw()
        if T_DROP + 0.1 < t < T_CARDS + 0.3 and int(t * 6) % 2 == 0:
            d.rectangle([V / 2 - 260, V / 2 - 50, V / 2 + 260, V / 2 + 50], fill=(0, 0, 0))
            d.text((V / 2, V / 2), "SIGNAL LOST", font=A.mono_big, fill=WHITE, anchor="mm"); sources.append(("drawn", "hud", "SIGNAL LOST"))
        if t >= T_CARDS:
            jx = random.Random(int(t * 30)).uniform(-4, 4)
            if t >= T_CARDS + 0.2:
                d.text((V / 2 + jx, V / 2 - 70), "6,000 VISITORS.", font=A.mono_big, fill=WHITE, anchor="mm"); sources.append(("drawn", "card", "6,000 VISITORS."))
            if t >= T_CARDS + 0.85:
                d.text((V / 2 - jx, V / 2 + 40), "ONE OF THEM IS A KILLER.", font=A.mono_big, fill=(0xF2, 0xC1, 0x4E), anchor="mm"); sources.append(("drawn", "card", "ONE OF THEM IS A KILLER."))
    if T_END - 0.15 < t < T_END + 0.2:                                 # glitch cut into the end card
        f.img = tracking(f.img, t, 1.0)
    return f.img

def build(outpath, poster=None, stills=None):
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    A = Assets(); bad = CL.forbidden()
    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{V}x{V}", "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
           "-crf", "27", "-preset", "slow", "-movflags", "+faststart", "-frames:v", str(N), outpath]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    hits_total = hit_frames = 0
    for i in range(N):
        t = i / FPS; sources = []
        img = render(A, t, sources).convert("RGB")
        h = kit.spoiler_scan(sources, bad); hits_total += len(h); hit_frames += bool(h)
        if poster and i == int(9.0 * FPS):
            img.save(poster)
        if stills is not None and i in stills:
            stills[i] = img.copy()
        proc.stdin.write(img.tobytes())
    proc.stdin.close(); proc.wait()
    return N, hits_total, hit_frames

if __name__ == "__main__":
    vid = os.path.join(HERE, "..", "video")
    picks = {int(s * FPS): None for s in (0.6, 2.4, 3.1, 5.6, 7.2, 8.9, 9.2, 10.3, 11.6, 13.8)}
    n, hits, hf_ = build(os.path.join(vid, f"{CL.SLUG}_found-footage-trailer_1080.mp4"),
                         os.path.join(vid, f"{CL.SLUG}_found-footage-trailer_poster.png"), picks)
    sheet = Image.new("RGB", (5 * 432, 2 * 432))
    for k, (i, im) in enumerate(sorted(picks.items())):
        sheet.paste(im.resize((432, 432)), ((k % 5) * 432, (k // 5) * 432))
    sheet.save(os.path.join(vid, f"{CL.SLUG}_found-footage-trailer_storyboard.png"))
    print(n, "frames; spoiler hits:", hits, "in", hf_, "frames")
