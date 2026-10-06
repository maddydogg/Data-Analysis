"""Cover for The Keeper of Candleholm: the key art set as a mid-century travel poster.

Big Josefin Sans capitals in cream with a rust offset print (a slightly misregistered second colour),
a round rust "24 DAYS" stamp, and a cream band at the foot with PRINTABLE and iPAD. Used for the PDF
covers, the main listing image and the end card of both videos. `record` is called with every string
drawn (spoiler and stop-list checks).
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import art as A
import scenes

HERE = os.path.dirname(os.path.abspath(__file__))
_f = {}
def font(name, size):
    key = (name, int(size))
    if key not in _f:
        fn = {"josefin": "JosefinSans-Bold.ttf", "josefin-semi": "JosefinSans-SemiBold.ttf",
              "fraunces": "Fraunces-SemiBold.ttf", "fraunces-i": "Fraunces-Italic.ttf",
              "nunito": "Nunito-ExtraBold.ttf"}[name]
        _f[key] = ImageFont.truetype(os.path.join(HERE, "fonts", fn), int(size))
    return _f[key]

def fit(d, text, name, size, maxw, spacing=0):
    while size > 10:
        f = font(name, size)
        if d.textlength(text, font=f) + spacing * (len(text) - 1) <= maxw:
            return f
        size -= 2
    return font(name, size)

def spaced(d, xy, text, f, fill, spacing, anchor="m"):
    """Letter-spaced text centred on xy (anchor m) or starting at xy (anchor l)."""
    w = d.textlength(text, font=f) + spacing * (len(text) - 1)
    x, y = xy
    if anchor == "m":
        x -= w / 2
    for ch in text:
        d.text((x, y), ch, font=f, fill=fill, anchor="ls")
        x += d.textlength(ch, font=f) + spacing
    return w

def poster_text(img, xy, text, f, fill=A.CREAM, offset=A.RUST, shift=None, spacing=0):
    d = ImageDraw.Draw(img)
    sh = shift if shift is not None else max(2, f.size // 22)
    spaced(d, (xy[0] + sh, xy[1] + sh), text, f, offset, spacing)
    spaced(d, xy, text, f, fill, spacing)

def stamp(img, cx, cy, r, top="24", bottom="DAYS", record=None):
    d = ImageDraw.Draw(img)
    d.ellipse([cx - r + r * 0.06, cy - r + r * 0.08, cx + r + r * 0.06, cy + r + r * 0.08], fill=A.shade(A.RUST_D, 0.7))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=A.RUST)
    d.ellipse([cx - r * 0.86, cy - r * 0.86, cx + r * 0.86, cy + r * 0.86], outline=A.CREAM, width=max(2, int(r * 0.05)))
    d.text((cx, cy + r * 0.2), top, font=font("josefin", r * 0.95), fill=A.CREAM, anchor="ms")
    spaced(d, (cx, cy + r * 0.56), bottom, font("josefin", r * 0.3), A.CREAM, r * 0.05)
    if record:
        record(f"{top} {bottom}")

def keyart_for_cover(w, h, seed=11, **kw):
    portrait = h > w * 1.1
    return scenes.keyart(w, h, seed=seed, hz_frac=0.67 if portrait else 0.66, tower=0.22 if portrait else 0.245,
                         fig_x=0.22, moon_xy=(0.88, 0.5 if portrait else 0.48), **kw)

def cover(w, h, badges=True, record=None, seed=11, art=None, players=True):
    rec = record or (lambda s: None)
    portrait = h > w * 1.1
    img = (art or keyart_for_cover(w, h, seed)).convert("RGBA")
    d = ImageDraw.Draw(img)
    m = w * 0.06
    # kicker
    k1 = "A LIGHTHOUSE MURDER MYSTERY"
    fk = fit(d, k1, "josefin-semi", w * 0.042, w - 2 * m, spacing=w * 0.006)
    y = h * (0.085 if portrait else 0.09)
    spaced(d, (w / 2, y), k1, fk, A.OCHRE_L, w * 0.006); rec(k1)
    # title
    t1, t2 = "THE KEEPER OF", "CANDLEHOLM"
    f1 = fit(d, t1, "josefin", w * 0.085, w - 2 * m, spacing=w * 0.01)
    f2 = fit(d, t2, "josefin", w * 0.2, w - 1.4 * m, spacing=w * 0.004)
    y1 = y + f1.size * 1.35
    poster_text(img, (w / 2, y1), t1, f1, spacing=w * 0.01); rec(t1)
    y2 = y1 + f2.size * 1.02
    poster_text(img, (w / 2, y2), t2, f2, spacing=w * 0.004); rec(t2)
    d = ImageDraw.Draw(img)
    k2 = "ADVENT CALENDAR"
    fk2 = fit(d, k2, "josefin", w * 0.06, w - 2 * m, spacing=w * 0.012)
    y3 = y2 + fk2.size * 1.55
    lw = d.textlength(k2, font=fk2) + w * 0.012 * (len(k2) - 1)
    for sx in (-1, 1):
        x0 = w / 2 + sx * (lw / 2 + w * 0.03)
        d.line([(x0, y3 - fk2.size * 0.35), (x0 + sx * w * 0.08, y3 - fk2.size * 0.35)], fill=A.OCHRE_L, width=max(2, int(w * 0.004)))
    spaced(d, (w / 2, y3), k2, fk2, A.OCHRE_L, w * 0.012); rec(k2)
    # the 24 DAYS stamp, over the sea on the right
    r = w * (0.11 if portrait else 0.085)
    stamp(img, w * 0.15, max(h * 0.5, y3 + r * 1.25), r, record=rec)
    # the cream band at the foot
    d = ImageDraw.Draw(img)
    bh = h * (0.085 if portrait else 0.095)
    d.rectangle([0, h - bh, w, h], fill=A.CREAM)
    d.rectangle([0, h - bh, w, h - bh + max(3, h * 0.006)], fill=A.RUST)
    if badges:
        t = "PRINTABLE  ·  iPAD" + ("  ·  1–4 PLAYERS" if players else "")
    else:
        t = "QUIETCLUECO  ·  24 DAYS  ·  2,400 TRAVELLERS  ·  1 KILLER"
    fb = fit(d, t, "josefin", bh * 0.5, w - 2 * m, spacing=w * 0.004)
    spaced(d, (w / 2, h - bh * 0.32), t, fb, A.NIGHT, w * 0.004); rec(t)
    return img.convert("RGB")

def banner(w, h, seed=11, record=None):
    """A wide title band for the top of the iPad calendar page: title on the left, the tower on the right."""
    rec = record or (lambda s: None)
    img = scenes.keyart(w, int(w * 0.62), seed=seed, hz_frac=0.62, tower=0.3, figure=False, moon_xy=None, boat_x=0.82)
    img = img.crop((0, int(img.height * 0.3), w, int(img.height * 0.3) + h)).convert("RGBA")
    shade_ = Image.new("RGBA", img.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(shade_)
    for x in range(int(w * 0.6)):
        a = int(150 * (1 - x / (w * 0.6)) ** 1.4)
        sd.line([(x, 0), (x, h)], fill=A.NIGHT + (a,))
    img.alpha_composite(shade_)
    d = ImageDraw.Draw(img)
    x = w * 0.045
    t0 = "THE KEEPER OF"
    f0 = fit(d, t0, "josefin", h * 0.16, w * 0.4)
    d.text((x, h * 0.3), t0, font=f0, fill=A.CREAM, anchor="ls"); rec(t0)
    t = "CANDLEHOLM"
    f = fit(d, t, "josefin", h * 0.3, w * 0.5)
    sh = max(2, f.size // 22)
    d.text((x + sh, h * 0.6 + sh), t, font=f, fill=A.RUST, anchor="ls"); d.text((x, h * 0.6), t, font=f, fill=A.CREAM, anchor="ls")
    rec(t)
    t2 = "MURDER MYSTERY ADVENT CALENDAR"
    f2 = fit(d, t2, "josefin-semi", h * 0.11, w * 0.5)
    d.text((x, h * 0.78), t2, font=f2, fill=A.OCHRE_L, anchor="ls"); rec(t2)
    return img.convert("RGB")

def make_pdf_covers(artdir):
    os.makedirs(artdir, exist_ok=True)
    for fmt, (w, h) in {"letter": (1275, 1650), "a4": (1240, 1754), "ipad": (1152, 1536)}.items():
        cover(w, h, badges=False).save(os.path.join(artdir, f"cover_{fmt}.jpg"), quality=90)
    banner(1536, 360).save(os.path.join(artdir, "banner_ipad.jpg"), quality=90)

if __name__ == "__main__":
    out = os.path.join(HERE, "..", "previews", "art"); os.makedirs(out, exist_ok=True)
    cover(1000, 1000).save(os.path.join(out, "cover_square.jpg"), quality=88)
    cover(850, 1100, badges=False).save(os.path.join(out, "cover_letter.jpg"), quality=88)
    im = Image.open(os.path.join(out, "cover_square.jpg")).resize((250, 250), Image.LANCZOS)
    im.save(os.path.join(out, "cover_250.png"))
