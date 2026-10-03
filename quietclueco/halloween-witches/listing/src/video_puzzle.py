"""Listing video 2, the puzzle presentation: 1080x1080, 15.0 s, 30 fps, no sound.

Same old-film look as the story trailer (letterbox, flicker, gate weave, grain, scratches, dust,
captions typed into the lower bar), but this one shows the product: the cover and the six case
documents landing on the table, the Inspector's Notebook being ticked, the Visitor Log being
struck through with a marker, the three levels of hints, the Sealed Check, print or iPad, and
the poster as the end card. Every page is a real PDF region; every frame is spoiler-scanned.

    python3 video_puzzle.py
"""
import math, os, random, subprocess
from PIL import Image, ImageDraw
import imageio_ffmpeg
import kit
import case_listing as CL
import poster as P
import mockups as M
import video_story as VS
from video_story import V, FPS, BAR, seg, lerp, push, letterbox, caption, text_card

DURATION = 15.0; N = int(round(DURATION * FPS))                             # 450 frames
HERE = os.path.dirname(os.path.abspath(__file__))
T_OPEN, T_DOCS, T_NOTE, T_LOG, T_HINTS, T_CHECK, T_DEVICES, T_END = 0.0, 1.4, 3.8, 5.8, 8.6, 10.2, 11.8, 13.0
CUTS = [T_DOCS, T_NOTE, T_LOG, T_HINTS, T_CHECK, T_DEVICES, T_END]
CY = (BAR + V - BAR) / 2                                                    # centre of the picture area

class Assets:
    def __init__(self):
        self.M = M.Assets(); L, I, p = self.M.L, self.M.I, self.M.p
        tab = kit.Frame(V, V, P.PLUM)
        P.gradient(tab.img, P.AUB, P.NIGHT)
        P.halftone(tab.img, (0, 0, V, V), P.AMETHYST + (46,), 24, falloff=lambda x, y: 0.5)
        self.table = tab.img
        self.cover = L.image(0, 700)
        self.docs = [L.image(p[k], 440) for k in ("map", "directory", "brews", "moon", "reading", "ledger")]
        # the notebook, clipped to the clue list
        words = L.words(p["notebook"]); yF = max(w[3] for w in words if w[4] == "F.")
        clip = (40, 70, 572, yF + 14)
        self.note = L.image(p["notebook"], 780, clip=clip)
        self.note_idx = p["notebook"]
        # the Visitor Log (a page with neither the killer nor any finalist on it)
        idx, rows, clip = M.log_clip(self.M, 40)
        zoom = 980 / (clip[2] - clip[0])
        self.log = L.image(idx, int((clip[3] - clip[1]) * zoom), clip=clip)
        self.log_rows = rows
        # level-1 hints (levels 2 and 3 stay in sealed envelopes)
        words = L.words(p["hint1"]); yE = sorted(w[1] for w in words if w[4] == "Evidence")[0]
        hc = (40, 70, 572, yE + 150)
        self.hint = L.image(p["hint1"], min(760, int(600 * (hc[3] - hc[1]) / (hc[2] - hc[0]))), clip=hc)
        # the Sealed Check, cut well above the box with the answer number
        r = CL.text_rect(L, p["check"], "If your last three digits are")
        cc = (40, 70, 572, r.y0 - 30)
        self.check = L.image(p["check"], min(700, int(600 * (cc[3] - cc[1]) / (cc[2] - cc[0]))), clip=cc)
        # print and iPad
        self.paper = L.image(p["brews"], 640)
        ih = 660; iw = ih * 0.766
        scr = I.image(self.M.ip["notebook"], int(ih * 0.91))
        M.tick_notebook(I, scr, self.M.ip["notebook"], [str(i) for i in range(1, 7)])
        tab = kit.Frame(int(iw) + 60, int(ih) + 60, P.PLUM); tab.img = Image.new("RGBA", tab.img.size, (0, 0, 0, 0))
        kit.ipad(tab, (30, 30, 30 + iw, 30 + ih), scr)
        self.tablet = tab
        # envelopes
        self.env = {}
        for key in ("2", "3", "?"):
            e = kit.Frame(360, 260, (0, 0, 0)); e.img = Image.new("RGBA", (360, 260), (0, 0, 0, 0))
            kit.envelope(e, (4, 4, 356, 256), key, P.hf("abril", 110))
            self.env[key] = e
        self.end = P.hero_poster()
        self.end_img = self.end.img.resize((V, V), Image.LANCZOS)
        # film textures (the same recipe as the story trailer)
        self.grain = []
        for i in range(6):
            n = Image.effect_noise((V, V), 70 + i).convert("L")
            self.grain.append(Image.merge("RGBA", (n, n, n, Image.new("L", (V, V), 34))))
        vm = Image.radial_gradient("L").resize((V, V)).point(lambda v: int(min(255, max(0, v - 70) * 1.5)))
        self.vignette = Image.new("RGBA", (V, V), (0, 0, 0, 255)); self.vignette.putalpha(vm)

def page(pg, img=None, text=None):
    return kit.PageImg(img if img is not None else pg.img.copy(), pg.text if text is None else text, pg.zoom, pg.rect, pg.source)

def table(A):
    f = kit.Frame(V, V, (0, 0, 0)); f.img = A.table.copy(); return f

def drop(f, pg, x, y, ang, a, dx=0, dy=-600, scale=1.5):
    """A page dropped onto the table: falls in from (x+dx, y+dy), rotating and shrinking."""
    if a <= 0:
        return
    sc = lerp(scale, 1.0, a)
    im = pg.img.resize((int(pg.img.width * sc), int(pg.img.height * sc)), Image.BICUBIC)
    f.paste_page(page(pg, im), lerp(x + dx, x, a), lerp(y + dy, y, a), angle=lerp(ang - 20, ang, a))

def env(f, A, key, x, y, a, ang=0):
    if a <= 0:
        return
    e = A.env[key]
    f.paste(e.img, lerp(V + 300, x, a), y, angle=ang); f.sources += e.sources

# ---------------------------------------------------------------- scenes
def s_docs(A, t, src):
    f = table(A)
    drop(f, A.cover, V / 2, CY, -2, VS.ease((t - T_DOCS) / 0.45), dy=-700)
    spots = [(250, 330, -7), (540, 300, 4), (830, 340, -4), (260, 700, 5), (550, 720, -3), (830, 690, 6)]
    for k, (pg, (x, y, ang)) in enumerate(zip(A.docs, spots)):
        t0 = T_DOCS + 0.65 + k * 0.22
        drop(f, pg, x, y, ang, seg(t, t0, t0 + 0.32), dx=(x - V / 2) * 0.6)
    img = push(f.img, 1 + 0.04 * seg(t, T_DOCS, T_NOTE), V / 2, CY)
    src += f.sources
    letterbox(img); caption(img, "6 CASE DOCUMENTS", t, T_DOCS + 0.7, src)
    return img

def s_note(A, t, src):
    f = table(A)
    pg = page(A.note)
    M.tick_notebook(A.M.L, pg, A.note_idx, [str(i) for i in range(1, 9)], progress=seg(t, T_NOTE + 0.3, T_LOG - 0.2))
    f.paste_page(pg, V / 2, lerp(CY + 40, CY, seg(t, T_NOTE, T_NOTE + 0.4)), angle=-1)
    img = push(f.img, 1 + 0.08 * seg(t, T_NOTE, T_LOG), 300, CY - 60)
    src += f.sources
    letterbox(img); caption(img, "18 CLUES · 12 STATED, 6 HIDDEN", t, T_NOTE + 0.2, src)
    return img

def s_log(A, t, src):
    f = table(A)
    pg = page(A.log)
    M.strike_rows(pg, A.log_rows, M.rowan_close, progress=seg(t, T_LOG + 0.3, T_HINTS - 0.2), seed=7)
    win = 760
    pan = lerp(0, max(0, pg.img.height - win), seg(t, T_LOG, T_HINTS))
    crop = pg.img.crop((0, int(pan), pg.img.width, int(pan) + min(win, pg.img.height)))
    f.paste_page(page(pg, crop), V / 2, CY, angle=-1)
    src += f.sources
    img = f.img
    letterbox(img); caption(img, "6,000 SUSPECTS · CROSS THEM OUT", t, T_LOG + 0.2, src)
    return img

def s_hints(A, t, src):
    f = table(A)
    a = seg(t, T_HINTS, T_HINTS + 0.4)
    f.paste_page(page(A.hint), lerp(-300, 50 + A.hint.img.width / 2, a), CY, angle=-2)
    env(f, A, "2", 860, 380, seg(t, T_HINTS + 0.4, T_HINTS + 0.8), 4)
    env(f, A, "3", 860, 690, seg(t, T_HINTS + 0.6, T_HINTS + 1.0), -3)
    img = f.img
    letterbox(img); caption(img, "STUCK? 3 LEVELS OF HINTS", t, T_HINTS + 0.2, src)
    return img

def s_check(A, t, src):
    f = table(A)
    a = seg(t, T_CHECK, T_CHECK + 0.4)
    f.paste_page(page(A.check), lerp(-300, 50 + A.check.img.width / 2, a), CY, angle=-1.5)
    b = seg(t, T_CHECK + 0.4, T_CHECK + 0.8)
    env(f, A, "?", 860, CY - 20 + math.sin(t * 6) * 6 * b, b, 3 * math.sin(t * 4))
    img = f.img
    letterbox(img); caption(img, "CHECK YOUR ANSWER · NO SPOILERS", t, T_CHECK + 0.2, src)
    return img

def s_devices(A, t, src):
    f = table(A)
    f.paste_page(page(A.paper), lerp(-300, 300, seg(t, T_DEVICES, T_DEVICES + 0.4)), CY, angle=2)
    f.paste(A.tablet.img, lerp(V + 300, 790, seg(t, T_DEVICES + 0.2, T_DEVICES + 0.6)), CY, angle=-2)
    f.sources += A.tablet.sources
    img = f.img
    letterbox(img); caption(img, "PRINT IT OR PLAY ON iPAD", t, T_DEVICES + 0.2, src)
    return img

def s_end(A, t, src):
    z = lerp(1.08, 1.0, seg(t, T_END, T_END + 1.4))
    im = A.end_img.resize((int(V * z), int(V * z)), Image.BICUBIC); o = (im.width - V) // 2
    src += A.end.sources
    return im.crop((o, o, o + V, o + V))

def render(A, t, i, src):
    if t < T_DOCS:
        img = text_card(t, T_OPEN, [("INSIDE THE CASE FILE", P.hf("cinzel", 70, 800), P.MOON, 0.1),
                                    ("Full Moon over Morrowmere", P.hf("fell-it", 72), P.GOLD, 0.45)], src)
    elif t < T_NOTE:
        img = s_docs(A, t, src)
    elif t < T_LOG:
        img = s_note(A, t, src)
    elif t < T_HINTS:
        img = s_log(A, t, src)
    elif t < T_CHECK:
        img = s_hints(A, t, src)
    elif t < T_DEVICES:
        img = s_check(A, t, src)
    elif t < T_END:
        img = s_devices(A, t, src)
    else:
        img = s_end(A, t, src)
    return VS.film(A, img, t, i, cuts=CUTS)

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
        if poster_path and i == int(3.6 * FPS):
            img.save(poster_path, quality=90)
        if stills is not None and i in stills:
            stills[i] = img.copy()
        proc.stdin.write(img.tobytes())
    proc.stdin.close(); proc.wait()
    return N, hits_total, hit_frames

if __name__ == "__main__":
    vid = os.path.join(HERE, "..", "video")
    picks = {int(s * FPS): None for s in (0.9, 1.9, 3.6, 4.4, 5.6, 6.6, 8.2, 9.4, 10.0, 11.4,
                                          12.6, 14.6)}
    n, hits, hf_ = build(os.path.join(vid, f"{CL.SLUG}_puzzle-presentation_1080.mp4"),
                         os.path.join(vid, f"{CL.SLUG}_puzzle-presentation_poster.jpg"), picks)
    sheet = Image.new("RGB", (4 * 432, 3 * 432))
    for k, (i, im) in enumerate(sorted(picks.items())):
        sheet.paste(im.resize((432, 432)), ((k % 4) * 432, (k // 4) * 432))
    sheet.save(os.path.join(vid, f"{CL.SLUG}_puzzle-presentation_storyboard.jpg"), quality=85)
    print(n, "frames; spoiler hits:", hits, "in", hf_, "frames")
