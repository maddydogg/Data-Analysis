"""Cover art for The Windows at Quillon's: the store at night in the snow, drawn with code (art.py),
with the title set in Bebas Neue and Oswald. Used for the PDF covers and the main listing image."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import art

HERE = os.path.dirname(os.path.abspath(__file__))
HORROR = os.path.join(os.path.dirname(HERE), "listing", "src", "fonts_horror")
FONTS = os.path.join(HERE, "fonts")
_f = {}
def font(name, size):
    key = (name, int(size))
    if key not in _f:
        files = {"bebas": ("BebasNeue-Regular.ttf", None), "oswald": ("Oswald[wght].ttf", 400),
                 "oswald-b": ("Oswald[wght].ttf", 600), "fraunces-i": ("Fraunces-Italic.ttf", None)}
        fn, wgt = files[name]
        d = FONTS if name.startswith("fraunces") else HORROR
        f = ImageFont.truetype(os.path.join(d, fn), int(size))
        if wgt:
            f.set_variation_by_axes([wgt])
        _f[key] = f
    return _f[key]

def spaced_text(d, xy, text, fnt, fill, spacing, anchor="mm"):
    """Letter-spaced text centred on xy."""
    widths = [d.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + spacing * (len(text) - 1)
    x = xy[0] - total / 2 if anchor[0] == "m" else xy[0]
    for ch, w in zip(text, widths):
        d.text((x, xy[1]), ch, font=fnt, fill=fill, anchor="l" + anchor[1])
        x += w + spacing
    return total

def cover(w, h, badges=False, seed=7, record=None):
    """The cover: storefront, title block at the top, tagline band at the bottom.
    record(s) is called with every string drawn (for the spoiler check)."""
    rec = record or (lambda s: None)
    im = art.storefront(w, h, seed=seed, windows=5, figure_at=0.5).convert("RGBA")
    # a dark band behind the title so it reads at thumbnail size
    band = Image.new("RGBA", im.size, (0, 0, 0, 0)); bd = ImageDraw.Draw(band)
    for y in range(int(h * 0.44)):
        a = int(235 * (1 - y / (h * 0.44)) ** 0.8)
        bd.line([(0, y), (w, y)], fill=art.NIGHT0 + (a,))
    im.alpha_composite(band)
    d = ImageDraw.Draw(im)
    u = w / 1000
    spaced_text(d, (w / 2, h * 0.038), "QUIETCLUECO PRESENTS", font("oswald", 26 * u), art.FROST, 6 * u); rec("QUIETCLUECO PRESENTS")
    t1, t2 = "THE WINDOWS", "AT QUILLON’S"
    f1 = font("bebas", 150 * u)
    while d.textlength(t2, font=f1) > w * 0.9:
        f1 = font("bebas", f1.size - 4)
    # amber glow behind the title
    g = Image.new("RGBA", im.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    gd.text((w / 2, h * 0.135), t1, font=f1, fill=art.AMBER + (170,), anchor="mm")
    gd.text((w / 2, h * 0.23), t2, font=f1, fill=art.AMBER + (170,), anchor="mm")
    im.alpha_composite(g.filter(ImageFilter.GaussianBlur(14 * u)))
    d = ImageDraw.Draw(im)
    d.text((w / 2, h * 0.135), t1, font=f1, fill=art.SNOW, anchor="mm"); rec(t1)
    d.text((w / 2, h * 0.23), t2, font=f1, fill=art.AMBER, anchor="mm"); rec(t2)
    spaced_text(d, (w / 2, h * 0.3), "A CHRISTMAS EVE MURDER MYSTERY", font("oswald", 34 * u), art.SNOW, 4 * u)
    rec("A CHRISTMAS EVE MURDER MYSTERY")
    spaced_text(d, (w / 2, h * 0.338), "ADVENT CALENDAR", font("oswald-b", 44 * u), art.AMBER, 10 * u); rec("ADVENT CALENDAR")
    # bottom band: the promise
    by = h * 0.885
    d.rectangle([0, by - 46 * u, w, by + 46 * u], fill=art.NIGHT0 + (235,))
    d.line([(0, by - 46 * u), (w, by - 46 * u)], fill=art.AMBER, width=max(2, int(3 * u)))
    spaced_text(d, (w / 2, by), "24 DAYS · 24 WINDOWS · 1 KILLER", font("bebas", 64 * u), art.SNOW, 5 * u)
    rec("24 DAYS · 24 WINDOWS · 1 KILLER")
    if badges:
        for k, (txt, x) in enumerate((("PRINTABLE", w * 0.27), ("iPad", w * 0.73))):
            f = font("bebas", 58 * u) if k == 0 else font("oswald-b", 50 * u)
            tw = d.textlength(txt, font=f) + 60 * u
            y0 = h * 0.79
            d.rounded_rectangle([x - tw / 2, y0 - 38 * u, x + tw / 2, y0 + 38 * u], radius=38 * u,
                                fill=art.AMBER if k == 0 else art.SNOW)
            d.text((x, y0 + 2 * u), txt, font=f, fill=art.NIGHT0, anchor="mm"); rec(txt)
    else:
        spaced_text(d, (w / 2, h * 0.965), "PRINTABLE · iPAD · ONE WINDOW A DAY, 1–24 DECEMBER",
                    font("oswald", 22 * u), art.FROST, 3 * u)
        rec("PRINTABLE · iPAD · ONE WINDOW A DAY, 1–24 DECEMBER")
    return im.convert("RGB")

def make_pdf_covers(outdir):
    os.makedirs(outdir, exist_ok=True)
    for fmt, (w, h) in {"letter": (1275, 1650), "a4": (1240, 1754), "ipad": (1152, 1536)}.items():
        cover(w, h).save(os.path.join(outdir, f"cover_{fmt}.jpg"), quality=88)

if __name__ == "__main__":
    make_pdf_covers(os.path.join(HERE, "art"))
    cover(2000, 2000, badges=True).save(os.path.join(HERE, "..", "previews", "art", "cover_square.jpg"), quality=88)
    print("ok")
