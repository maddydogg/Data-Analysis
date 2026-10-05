"""Cover and key art for the "v2 action" listing variant of The Windows at Quillon's.

Key art: Quillon's towering over Lantern Street in a steep low angle and a dutch tilt, every window
burning amber, manga focus lines pulling the eye to the doors, snow streaking past, and a figure
seen from behind sprinting towards the store, coat flaring, rim-lit by the windows. The cover sets
the title over it like an anime title card, with a round "24 DAYS" stamp, PRINTABLE and iPad badges.
Drawn entirely with code; every string drawn is passed to `record` for the spoiler check.
"""
import os, sys
from PIL import Image, ImageDraw, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
CASE = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(CASE, "src"))
import art                      # noqa: E402
import action as X              # noqa: E402
import kit                      # noqa: E402
kit.set_font_dir(os.path.join(CASE, "src", "fonts"))

def store_corner(cv, seed=11, clock=None):
    """Quillon's seen from the pavement, looking up at its corner: the long Lantern Street front comes
    towards the camera on the left, the side front runs away to the right. Returns the street line."""
    w, h = cv.W, cv.H
    ql = X.Quad((-w * 0.32, h * 0.06), (w * 0.64, h * 0.33), (w * 0.67, h * 0.86), (-w * 0.4, h * 0.97))
    qr = X.Quad((w * 0.64, h * 0.33), (w * 1.25, h * 0.4), (w * 1.27, h * 0.84), (w * 0.67, h * 0.86))
    X.tower(cv, qr, cols=5, rows=6, seed=seed + 1, lit=0.25, face=X.NIGHT0, trim=X.INK, amber_bias=0.4)
    X.tower(cv, ql, cols=8, rows=7, seed=seed, lit=0.36)
    cv.d.line(cv.P([(w * 0.64, h * 0.33), (w * 0.67, h * 0.86)]), fill=X.STEEL, width=3 * cv.ss)   # the corner catches the lamp
    if clock:
        X.wall_clock(cv, w * 0.645, h * 0.31, w * 0.07, *clock)
    return ql, qr

def keyart(w, h, seed=11, runner_phase=0.0, runner=True, lines=True, snow_shift=0.0, grain=14, ss=2, clock=None):
    """The key frame without type. Returns RGB."""
    cv = art.Canvas(w, h, ss=ss)
    art.sky(cv, X.NIGHT0, X.NIGHT2)
    cv.glow(w * 0.62, h * 0.5, w * 0.5, X.AMBER, alpha=55)
    X.focus_lines(cv, w * 0.62, h * 0.5, n=120, r_in=(0.22, 0.4), col=X.SNOW, alpha=(14, 50), width=(1.5, 6), seed=seed)
    ql, qr = store_corner(cv, seed=seed, clock=clock)
    # the pavement: snow, lit amber in front of every display window
    cv.d.polygon(cv.P([(-w * 0.4, h * 0.97), (w * 0.67, h * 0.86), (w * 1.27, h * 0.84), (w * 1.3, h * 1.2), (-w * 0.4, h * 1.2)]), fill=X.NIGHT1)
    L = cv.layer(); ld = ImageDraw.Draw(L)
    for k in range(8):
        a, b = ql(k / 8 + 0.03, 0.985), ql((k + 1) / 8 - 0.03, 0.985)
        ld.polygon(cv.P([a, b, (b[0] + w * 0.05, h * 1.1), (a[0] - w * 0.12, h * 1.1)]), fill=X.AMBER + (60,))
    cv.img.alpha_composite(L.filter(ImageFilter.GaussianBlur(10 * cv.ss)))
    if lines:
        X.focus_lines(cv, w * 0.62, h * 0.55, n=90, r_in=(0.42, 0.55), col=X.SNOW, alpha=(25, 90), width=(1.5, 6), seed=seed + 2)
        X.focus_lines(cv, w * 0.62, h * 0.55, n=26, r_in=(0.45, 0.58), col=X.AMBER, alpha=(40, 110), width=(2, 7), seed=seed + 1)
    X.streaks(cv, int(w * h / 9000), angle=-58, length=(w * 0.02, w * 0.09), alpha=(40, 150), width=(1, 2.6),
              seed=seed + int(snow_shift * 1000))
    if runner:
        rx, rb, rh = w * 0.3, h * 0.995, h * 0.5
        X.runner(cv, rx, rb, rh, phase=runner_phase)
        X.kicked_snow(cv, rx - rh * 0.1, rb - rh * 0.02, rh, seed=seed)
    art.snow(cv, int(w * h / 1400), seed=seed + 3, angle=-30)
    return cv.finish(grain=grain, vignette=0.45, seed=seed)

def cover(w, h, badges=True, record=None, seed=11, art_img=None):
    rec = record or (lambda s: None)
    im = (art_img or keyart(w, h, seed=seed)).convert("RGBA")
    u = w / 1000
    # dark wash behind the title so it reads at thumbnail size
    band = Image.new("RGBA", im.size, (0, 0, 0, 0)); bd = ImageDraw.Draw(band)
    for y in range(int(h * 0.46)):
        bd.line([(0, y), (w, y)], fill=X.NIGHT0 + (int(200 * (1 - y / (h * 0.46)) ** 1.4),))
    im.alpha_composite(band)
    d = ImageDraw.Draw(im)
    small = kit.font("bold", 26 * u)
    d.text((w / 2, h * 0.026), "QUIETCLUECO  ·  A CHRISTMAS EVE MURDER MYSTERY", font=small, fill=X.FROST, anchor="mm")
    rec("QUIETCLUECO  ·  A CHRISTMAS EVE MURDER MYSTERY")
    f1 = kit.font("display", 205 * u)
    X.slam_text(im, (w * 0.5, h * 0.145), "THE WINDOWS", f1, fill=X.SNOW, angle=4, shadow=X.AMBER_D, glow=None); rec("THE WINDOWS")
    X.slam_text(im, (w * 0.5, h * 0.305), "AT QUILLON’S", f1, fill=X.AMBER, angle=4, shadow=X.NIGHT0,
                glow=X.AMBER); rec("AT QUILLON’S")
    X.badge(im, (w * 0.5, h * 0.42), "MURDER MYSTERY ADVENT CALENDAR", kit.font("display", 50 * u), bg=X.SNOW, fg=X.NIGHT0, angle=4)
    rec("MURDER MYSTERY ADVENT CALENDAR")
    # the hook, bottom left over the street
    X.tape(im, h * 0.905, 6, "2,400 SHOPPERS  ·  1 KILLER  ·  OPEN ONE WINDOW A DAY", kit.font("display", 46 * u), seed=seed)
    rec("2,400 SHOPPERS  ·  1 KILLER  ·  OPEN ONE WINDOW A DAY")
    X.seal(im, (w * 0.83, h * 0.6), 128 * u, "ONE A DAY", "24", "DAYS", kit.font("display", 34 * u),
           kit.font("display", 160 * u), angle=-10)
    rec("ONE A DAY"); rec("24"); rec("DAYS")
    if badges:
        X.badge(im, (w * 0.715, h * 0.805), "PRINTABLE", kit.font("display", 64 * u), bg=X.AMBER, fg=X.NIGHT0, angle=6)
        X.badge(im, (w * 0.915, h * 0.79), "iPad", kit.font("black", 46 * u), bg=X.SNOW, fg=X.NIGHT0, angle=6)
        rec("PRINTABLE"); rec("iPad")
    return im.convert("RGB")

def cover_portrait(w, h, record=None, seed=11):
    """For a PDF cover (portrait page): the same key art and title, no badges."""
    rec = record or (lambda s: None)
    im = keyart(w, h, seed=seed).convert("RGBA"); u = w / 1000
    band = Image.new("RGBA", im.size, (0, 0, 0, 0)); bd = ImageDraw.Draw(band)
    for y in range(int(h * 0.42)):
        bd.line([(0, y), (w, y)], fill=X.NIGHT0 + (int(225 * (1 - y / (h * 0.42)) ** 1.1),))
    im.alpha_composite(band)
    d = ImageDraw.Draw(im)
    d.text((w / 2, h * 0.035), "QUIETCLUECO  ·  A CHRISTMAS EVE MURDER MYSTERY", font=kit.font("bold", 24 * u), fill=X.FROST, anchor="mm")
    f1 = kit.font("display", 190 * u)
    X.slam_text(im, (w * 0.5, h * 0.12), "THE WINDOWS", f1, fill=X.SNOW, angle=4, shadow=X.AMBER_D)
    X.slam_text(im, (w * 0.5, h * 0.235), "AT QUILLON’S", f1, fill=X.AMBER, angle=4, shadow=X.NIGHT0, glow=X.AMBER)
    X.badge(im, (w * 0.5, h * 0.32), "MURDER MYSTERY ADVENT CALENDAR", kit.font("display", 46 * u), bg=X.SNOW, fg=X.NIGHT0, angle=4)
    X.tape(im, h * 0.93, 6, "2,400 SHOPPERS  ·  1 KILLER  ·  OPEN ONE WINDOW A DAY", kit.font("display", 42 * u), seed=seed)
    X.seal(im, (w * 0.8, h * 0.7), 115 * u, "ONE A DAY", "24", "DAYS", kit.font("display", 32 * u), kit.font("display", 140 * u))
    for s in ("THE WINDOWS", "AT QUILLON’S", "MURDER MYSTERY ADVENT CALENDAR"):
        rec(s)
    return im.convert("RGB")

if __name__ == "__main__":
    out = os.path.join(CASE, "listing", "v2", "preview"); os.makedirs(out, exist_ok=True)
    keyart(1000, 1000).save(os.path.join(out, "keyart.jpg"), quality=88)
    cover(2000, 2000).save(os.path.join(out, "cover.jpg"), quality=88)
    print("ok")
