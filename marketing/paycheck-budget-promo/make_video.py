"""Composite the rendered sheets into the 14.8 s listing video frames.

Usage: WORK=./work python3 make_video.py   ->  $WORK/frames/f_%04d.png
"""
import json, math, os, shutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter

import os
D = os.environ.get("WORK", os.path.dirname(os.path.abspath(__file__))+"/work")
F = D + "/fonts"
OUT = D + "/frames"
W, H = 1500, 1125
FPS = 30

# ---------------- palette (taken from the workbook itself) ----------------
BG        = (242, 240, 234)
INK       = (38, 50, 60)
DEEP      = (51, 86, 107)      # FF33566B
MUTED     = (123, 138, 153)    # FF7B8A99
MINT      = (223, 243, 234)    # FFDFF3EA
MINT_DK   = (150, 196, 176)
BLUE      = (62, 124, 192)     # FF3E7CC0
BEZEL     = (37, 45, 51)
FOOT_BG   = (229, 234, 227)

def font(name, size): return ImageFont.truetype(f"{F}/{name}.ttf", size)
MB  = lambda s: font("Montserrat-Bold", s)
MEB = lambda s: font("Montserrat-ExtraBold", s)
MSB = lambda s: font("Montserrat-SemiBold", s)
MM  = lambda s: font("Montserrat-Medium", s)
IR  = lambda s: font("Inter-Regular", s)
ISB = lambda s: font("Inter-SemiBold", s)

# ---------------- geometry ----------------
LAP = (176, 296, 1324, 1014)                 # laptop body
SCR = (202, 320, 1298, 966)                  # screen
SW, SH = SCR[2]-SCR[0], SCR[3]-SCR[1]
FOOT_Y = 1050

meta = json.load(open(D+"/screens/meta.json"))

def tracked(d, xy, text, f, fill, sp=2, anchor_center=False):
    widths = [d.textlength(c, font=f) for c in text]
    total = sum(widths) + sp*(len(text)-1)
    x, y = xy
    if anchor_center: x -= total/2
    for c, w in zip(text, widths):
        d.text((x, y), c, font=f, fill=fill)
        x += w + sp
    return total

def ease(t):  return t*t*(3-2*t)
def clamp(v, a=0.0, b=1.0): return max(a, min(b, v))

# ---------------- static background ----------------
def make_bg():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # paper grain
    import random
    random.seed(7)
    for _ in range(5200):
        x, y = random.randrange(W), random.randrange(FOOT_Y)
        v = random.randint(-6, 6)
        p = img.getpixel((x, y))
        img.putpixel((x, y), tuple(max(0, min(255, c+v)) for c in p))
    # footer
    d.rectangle([0, FOOT_Y, W, H], fill=FOOT_BG)
    fo = ISB(21)
    parts = ["WORKS IN GOOGLE SHEETS & EXCEL", "8 TABS, ZERO SET-UP", "THE MATH IS ALREADY DONE"]
    widths = []
    for p in parts:
        widths.append(sum(d.textlength(c, font=fo) for c in p) + 2*(len(p)-1))
    gap = 70
    total = sum(widths) + gap*(len(parts)-1)
    x = (W-total)/2; y = FOOT_Y + 26
    for i, p in enumerate(parts):
        tracked(d, (x, y), p, fo, (74, 90, 99), sp=2)
        x += widths[i]
        if i < len(parts)-1:
            d.rectangle([x+gap/2-4, y+8, x+gap/2+2, y+14], fill=MINT_DK)
            x += gap
    # laptop shadow
    sh = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sh).rounded_rectangle([LAP[0]+12, LAP[1]+26, LAP[2]-12, LAP[3]+34], 30, fill=90)
    sh = sh.filter(ImageFilter.GaussianBlur(26))
    img.paste(Image.new("RGB", (W, H), (120, 128, 124)), (0, 0), sh)
    # body
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(LAP, 22, fill=BEZEL)
    d.rounded_rectangle([LAP[0]+1, LAP[1]+1, LAP[2]-1, LAP[3]-1], 22, outline=(66, 76, 84), width=2)
    d.ellipse([ (LAP[0]+LAP[2])/2-3, LAP[1]+9, (LAP[0]+LAP[2])/2+3, LAP[1]+15], fill=(90, 100, 108))
    d.rectangle(SCR, fill=(255, 255, 255))
    # base
    b0, b1 = LAP[3], LAP[3]+26
    d.rounded_rectangle([130, b0, 1370, b1], 12, fill=(202, 208, 210))
    d.rounded_rectangle([130, b0, 1370, b0+9], 8, fill=(174, 182, 186))
    d.rounded_rectangle([690, b0+2, 810, b0+11], 6, fill=(158, 166, 170))
    return img

# ---------------- badges ----------------
def draw_check(d, cx, cy, r, color, w=5):
    d.line([(cx-r*0.55, cy), (cx-r*0.12, cy+r*0.45), (cx+r*0.62, cy-r*0.5)], fill=color, width=w, joint="curve")

def make_pill():
    txt = "EVERY NUMBER UPDATES ITSELF"
    f = MB(24)
    tw = ImageDraw.Draw(Image.new("RGB",(10,10))).textlength(txt, font=f)
    pw, ph = int(tw)+126, 70
    lay = Image.new("RGBA", (pw+60, ph+60), (0, 0, 0, 0))
    sh = Image.new("L", lay.size, 0)
    ImageDraw.Draw(sh).rounded_rectangle([30, 34, 30+pw, 34+ph], ph//2, fill=110)
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    lay.paste((90, 100, 96, 255), (0, 0), sh)
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle([30, 30, 30+pw, 30+ph], ph//2, fill=(255, 255, 255, 255))
    d.ellipse([56, 48, 90, 82], outline=DEEP, width=4)
    draw_check(d, 73, 65, 12, DEEP, 4)
    d.text((104, 46), txt, font=f, fill=INK)
    return lay

def make_badge():
    r = 88
    lay = Image.new("RGBA", (2*r+60, 2*r+60), (0, 0, 0, 0))
    sh = Image.new("L", lay.size, 0)
    ImageDraw.Draw(sh).ellipse([30, 36, 30+2*r, 36+2*r], fill=120)
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    lay.paste((80, 95, 100, 255), (0, 0), sh)
    circ = Image.new("RGBA", (2*r, 2*r), (0, 0, 0, 0))
    grad = Image.new("RGB", (2*r, 2*r))
    gd = ImageDraw.Draw(grad)
    for y in range(2*r):
        t = y/(2*r)
        gd.line([(0, y), (2*r, y)], fill=(int(96+(51-96)*t), int(163+(86-163)*t), int(140+(107-140)*t)))
    m = Image.new("L", (2*r, 2*r), 0)
    ImageDraw.Draw(m).ellipse([0, 0, 2*r-1, 2*r-1], fill=255)
    circ.paste(grad, (0, 0), m)
    d = ImageDraw.Draw(circ)
    d.ellipse([9, 9, 2*r-10, 2*r-10], outline=(255, 255, 255, 90), width=2)
    draw_check(d, r, r-38, 20, (255, 255, 255, 235), 6)
    for i, line in enumerate(["Sheets", "+ Excel"]):
        f = MB(30)
        d.text((r, r+2+i*34), line, font=f, fill=(255, 255, 255), anchor="ma")
    lay.paste(circ, (30, 30), circ)
    return lay

# ---------------- bullets ----------------
BULLETS = [
    ("tabs",  "8 ready-to-use tabs",            0.35),
    ("edit",  "Set it up once",                 1.70),
    ("split", "Split across Paycheck 1 & 2",    3.50),
    ("log",   "One log for everything",         5.50),
    ("bill",  "True monthly cost of each bill", 7.40),
    ("goal",  "Sinking funds & debt payoff",   10.40),
]

def draw_icon(d, kind, x, y, s, color):
    if kind == "tabs":
        for i in range(3):
            d.rounded_rectangle([x, y+i*(s/3), x+s, y+i*(s/3)+s/5], 2, fill=color)
    elif kind == "edit":
        d.line([(x, y+s), (x+s*0.72, y+s*0.28)], fill=color, width=4)
        d.polygon([(x+s*0.7, y+s*0.26), (x+s, y), (x+s*0.96, y+s*0.34)], fill=color)
        d.line([(x, y+s), (x+s*0.2, y+s*0.94)], fill=color, width=4)
    elif kind == "split":
        d.line([(x, y+s/2), (x+s*0.4, y+s/2)], fill=color, width=4)
        d.line([(x+s*0.4, y+s/2), (x+s, y+s*0.08)], fill=color, width=4)
        d.line([(x+s*0.4, y+s/2), (x+s, y+s*0.92)], fill=color, width=4)
    elif kind == "log":
        d.rounded_rectangle([x, y, x+s*0.78, y+s], 4, outline=color, width=4)
        for i in range(3):
            d.line([(x+s*0.16, y+s*0.28+i*s*0.24), (x+s*0.62, y+s*0.28+i*s*0.24)], fill=color, width=3)
    elif kind == "bill":
        d.rounded_rectangle([x, y+s*0.12, x+s, y+s], 4, outline=color, width=4)
        d.line([(x, y+s*0.42), (x+s, y+s*0.42)], fill=color, width=4)
        d.line([(x+s*0.26, y), (x+s*0.26, y+s*0.24)], fill=color, width=4)
        d.line([(x+s*0.74, y), (x+s*0.74, y+s*0.24)], fill=color, width=4)
    elif kind == "goal":
        d.ellipse([x, y, x+s, y+s], outline=color, width=4)
        d.ellipse([x+s*0.34, y+s*0.34, x+s*0.66, y+s*0.66], fill=color)

def layout_bullets():
    tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    f = MSB(25)
    rows = [BULLETS[:3], BULLETS[3:]]
    pos = {}
    y = 170
    for items in rows:
        ws = [36 + tmp.textlength(b[1], font=f) + 44 for b in items]
        x = (W-(sum(ws)-44))/2
        for b, w in zip(items, ws):
            pos[b[0]] = (x, y)
            x += w
        y += 50
    return pos, f

BPOS, BFONT = layout_bullets()

def draw_bullets(img, t):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for kind, text, t0 in BULLETS:
        if t < t0: continue
        a = ease(clamp((t-t0)/0.45))
        x, y = BPOS[kind]
        dy = int((1-a)*10)
        col = tuple(list(DEEP)+[int(255*a)])
        draw_icon(d, kind, x, y+5+dy, 24, col)
        d.text((x+36, y+dy), text, font=BFONT, fill=col)
    img.alpha_composite(lay)

# ---------------- scenes ----------------
class Page:
    """sheet image laid out on a white page the width of the screen"""
    def __init__(self, key, fit="width", variant=None):
        src = Image.open(f"{D}/screens/{key}{'_b' if variant else ''}.png").convert("RGB")
        self.src_size = src.size
        if fit == "width":
            sc = SW/src.width
        else:
            sc = min(SW/src.width, SH/src.height)
        self.scale = sc
        w, h = int(src.width*sc), int(src.height*sc)
        ph = max(h, SH)
        page = Image.new("RGB", (SW, ph), (255, 255, 255))
        page.paste(src.resize((w, h), Image.LANCZOS), ((SW-w)//2, (ph-h)//2 if h <= SH else 0))
        self.img = page
        self.ox = (SW-w)//2
        self.oy = (ph-h)//2 if h <= SH else 0

    def view(self, pan, k):
        cw, ch = SW/k, SH/k
        xo = (SW-cw)/2
        yo = pan*max(self.img.height-SH, 0) + (SH-ch)/2
        box = (xo, yo, xo+cw, yo+ch)
        v = self.img.resize((SW, SH), Image.LANCZOS, box=box)
        return v, (xo, yo, k)

    def to_view(self, pt, tf):
        xo, yo, k = tf
        return ((pt[0]*self.scale+self.ox - xo)*k, (pt[1]*self.scale+self.oy - yo)*k)

SCENES = [
    dict(key="0_Start_Here",      dur=1.5, fit="contain", pan=(0, 0),    zoom=(1.0, 1.05),
         cur=[(0.0, .18, .78), (1.0, .55, .40)]),
    dict(key="1_Setup",           dur=1.8, fit="width",   pan=(0.0, 0.55), zoom=(1.0, 1.04),
         cur=[(0.0, .70, .20), (0.55, .30, .52), (1.0, .24, .66)]),
    dict(key="3_Paycheck_Budget", dur=2.0, fit="width",   pan=(0.0, 1.0), zoom=(1.02, 1.02),
         cur=[(0.0, .28, .30), (1.0, .62, .74)]),
    dict(key="4_Transactions",    dur=1.9, fit="width",   pan=(0.05, 1.0), zoom=(1.0, 1.03),
         cur=[(0.0, .55, .25), (1.0, .40, .70)]),
    dict(key="5_Bill_Calendar",   dur=3.0, fit="contain", pan=(0.5, 0.5), zoom=(1.0, 1.0),
         special="dropdown"),
    dict(key="6_Savings",         dur=1.0, fit="contain", pan=(0.5, 0.5), zoom=(1.0, 1.04),
         cur=[(0.0, .70, .30), (1.0, .52, .60)]),
    dict(key="7_Debt",            dur=1.0, fit="contain", pan=(0.5, 0.5), zoom=(1.0, 1.04),
         cur=[(0.0, .40, .30), (1.0, .60, .62)]),
    dict(key="2_Dashboard",       dur=2.6, fit="contain", pan=(0.5, 0.5), zoom=(1.0, 1.05),
         cur=[(0.0, .20, .70), (0.45, .35, .28), (1.0, .74, .55)]),
]
for s in SCENES:
    s["page"] = Page(s["key"], s["fit"])
SCENES[4]["page_b"] = Page("5_Bill_Calendar", "contain", variant=True)

FADE = 0.22
starts, t0 = [], 0.0
for s in SCENES:
    starts.append(t0); t0 += s["dur"]
TOTAL = t0

CURSOR = [(0, 0), (0, 23), (6, 17.5), (10, 26), (14, 24), (10, 16), (17, 16)]

def draw_cursor(img, x, y, scale=1.5, alpha=255):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    pts = [(x+px*scale, y+py*scale) for px, py in CURSOR]
    d.polygon(pts, fill=(255, 255, 255, alpha), outline=(30, 38, 44, alpha))
    d.line(pts+[pts[0]], fill=(30, 38, 44, alpha), width=3, joint="curve")
    img.alpha_composite(lay)

def cursor_at(sc, u):
    pts = sc["cur"]
    for i in range(len(pts)-1):
        a, b = pts[i], pts[i+1]
        if a[0] <= u <= b[0]:
            f = ease((u-a[0])/max(b[0]-a[0], 1e-6))
            return (a[1]+(b[1]-a[1])*f)*SW, (a[2]+(b[2]-a[2])*f)*SH
    return pts[-1][1]*SW, pts[-1][2]*SH

OPTIONS = ["Weekly", "Biweekly", "Monthly", "Yearly"]

def scene_screen(sc, u):
    """returns RGBA screen image (SW x SH) for local progress u"""
    if sc.get("special") == "dropdown":
        return bill_scene(sc, u)
    k = sc["zoom"][0] + (sc["zoom"][1]-sc["zoom"][0])*ease(u)
    pan = sc["pan"][0] + (sc["pan"][1]-sc["pan"][0])*ease(u)
    v, tf = sc["page"].view(pan, k)
    v = v.convert("RGBA")
    x, y = cursor_at(sc, u)
    draw_cursor(v, x, y)
    return v

def bill_scene(sc, u):
    t = u*sc["dur"]
    open_t, pick_t, close_t = 0.55, 1.55, 1.75
    page = sc["page"] if t < close_t else sc["page_b"]
    v, tf = page.view(0.5, 1.0)
    v = v.convert("RGBA")
    ov = Image.new("RGBA", v.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    cell = meta["sheets"]["5_Bill_Calendar"]["cell"]
    cx0, cy0 = page.to_view((cell[0], cell[1]), tf)
    cx1, cy1 = page.to_view((cell[2], cell[3]), tf)
    cw = (cx1-cx0)
    # cell frame (as if selected)
    box = [cx0-26, cy0-9, cx1+26, cy1+9]
    if t > 0.35:
        d.rounded_rectangle(box, 3, outline=BLUE, width=3)
    # flash the numbers that changed
    if close_t <= t < close_t+1.1:
        a = (1-(t-close_t)/1.1)
        for key in ("cost_val", "total_val"):
            r = meta["sheets"]["5_Bill_Calendar"].get(key)
            if not r: continue
            p0 = page.to_view((r[0], r[1]), tf); p1 = page.to_view((r[2], r[3]), tf)
            bx = [p0[0]-16, p0[1]-9, p1[0]+14, p1[1]+9]
            d.rounded_rectangle(bx, 4, fill=(255, 226, 120, int(70*a)),
                                outline=(233, 170, 40, int(220*a)), width=3)
    # cursor path
    rh = 34
    dtop = box[1]-(len(OPTIONS)*rh+8)-6
    opt_y = dtop+4+2*rh+17
    if t < 0.5:
        f = ease(clamp(t/0.5))
        x = SW*0.72+(box[0]+40-SW*0.72)*f
        y = SH*0.18+((box[1]+box[3])/2-SH*0.18)*f
    elif t < 1.5:
        f = ease(clamp((t-0.62)/0.8))
        x = box[0]+40
        y = (box[1]+box[3])/2 + (opt_y-(box[1]+box[3])/2)*f
    else:
        f = ease(clamp((t-1.8)/1.0))
        x = box[0]+40+(SW*0.66-(box[0]+40))*f
        y = opt_y+(SH*0.30-opt_y)*f
    # dropdown
    if open_t <= t < close_t:
        rw, rh = 168, 34
        dx, dy = box[0], box[1]-(len(OPTIONS)*rh+8)-6
        d.rounded_rectangle([dx+2, dy+3, dx+rw+2, dy+len(OPTIONS)*rh+11], 6, fill=(30, 40, 50, 40))
        d.rounded_rectangle([dx, dy, dx+rw, dy+len(OPTIONS)*rh+8], 6,
                            fill=(255, 255, 255, 255), outline=(198, 210, 220, 255), width=2)
        hov = max(0, min(len(OPTIONS)-1, int((y-(dy+4))//rh)))
        for i, opt in enumerate(OPTIONS):
            ry = dy+4+i*rh
            if i == hov:
                d.rounded_rectangle([dx+4, ry, dx+rw-4, ry+rh-2], 4, fill=(231, 240, 250, 255))
            d.text((dx+34, ry+7), opt, font=IR(19), fill=INK)
        d.line([(dx+14, dy+4+0*rh+18), (dx+18, dy+4+22), (dx+25, dy+4+11)], fill=DEEP, width=3)
    v.alpha_composite(ov)
    draw_cursor(v, x, y)
    rip = Image.new("RGBA", v.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(rip)
    if 0.3 < t < 0.55 or 1.5 < t < 1.75:            # click ripple
        tt = (t-0.3)/0.25 if t < 0.6 else (t-1.5)/0.25
        r = 10+26*tt
        d.ellipse([x-r, y-r, x+r, y+r], outline=(62, 124, 192, int(180*(1-tt))), width=4)
    v.alpha_composite(rip)
    return v

# ---------------- render ----------------
def main():
    shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
    bg = make_bg()
    pill, badge = make_pill(), make_badge()
    title_f = MEB(74)
    n = int(round(TOTAL*FPS))
    for i in range(n):
        t = i/FPS
        si = max(j for j in range(len(SCENES)) if starts[j] <= t+1e-6)
        sc = SCENES[si]
        u = clamp((t-starts[si])/sc["dur"])
        scr = scene_screen(sc, u)
        # crossfade into next scene
        tail = starts[si]+sc["dur"]-t
        if tail < FADE and si+1 < len(SCENES):
            nx = SCENES[si+1]
            nscr = scene_screen(nx, clamp((FADE-tail)/nx["dur"]))
            scr = Image.blend(scr, nscr, ease(1-tail/FADE))
        frame = bg.copy()
        frame.paste(scr.convert("RGB"), (SCR[0], SCR[1]))
        frame = frame.convert("RGBA")
        # intro fade of the whole screen
        if t < 0.35:
            wash = Image.new("RGBA", (SW, SH), (255, 255, 255, int(255*(1-ease(t/0.35)))))
            frame.alpha_composite(wash, (SCR[0], SCR[1]))
        frame.alpha_composite(pill, (146, 856))
        frame.alpha_composite(badge, (1176, 810))
        d = ImageDraw.Draw(frame)
        d.text((W//2, 52), "Paycheck Budget Planner", font=title_f, fill=INK, anchor="ma")
        draw_bullets(frame, t)
        frame.convert("RGB").save(f"{OUT}/f_{i:04d}.png")
        if i % 60 == 0: print("frame", i, "/", n, flush=True)
    print("frames", n, "duration", TOTAL)

main()
