"""Brand kit taken straight from the Budget Planner workbook palette."""
import math, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W = H = 2000
FDIR = "/home/user/.fonts/poppins"
REG, MED, BLD = f"{FDIR}/Poppins-Regular.ttf", f"{FDIR}/Poppins-Medium.ttf", f"{FDIR}/Poppins-Bold.ttf"

# straight out of xl/styles.xml
INK        = "#33566B"   # sheet headings
INK_DEEP   = "#24404F"   # a step darker, for big type
GRAPHITE   = "#3A4652"
SLATE      = "#7B8A99"   # secondary text
BLUE       = "#3E7CC0"   # the cells you type in
MINT       = "#70F8A0"   # chart bars, accent rules
MINT_SOFT  = "#DFF3EA"   # highlighted totals
AQUA_SOFT  = "#E4F3F6"
LINE       = "#E4EBF2"
LINE_DEEP  = "#D5E2ED"
PAPER      = "#FBFCFD"
PAPER_WARM = "#F6F9FB"


def font(path, size):
    return ImageFont.truetype(path, size)


def line_h(f):
    a, d = f.getmetrics()
    return a + d


def text_w(d, s, f, tracking=0):
    if not s:
        return 0
    return sum(d.textlength(c, font=f) for c in s) + tracking * (len(s) - 1)


def tracked(d, x, y, s, f, fill, tracking=0, align="center"):
    w = text_w(d, s, f, tracking)
    cx = x - w / 2 if align == "center" else (x - w if align == "right" else x)
    for ch in s:
        d.text((cx, y), ch, font=f, fill=fill)
        cx += d.textlength(ch, font=f) + tracking
    return w


def fit_size(d, s, path, target_w, tr=0.14, lo=36, hi=240):
    best = lo
    while lo <= hi:
        mid = (lo + hi) // 2
        if text_w(d, s, font(path, mid), mid * tr) <= target_w:
            best, lo = mid, mid + 1
        else:
            hi = mid - 1
    return best


def grain(img, amount=5, seed=7):
    """Faint noise so the flat fills stop looking like a screenshot of a fill."""
    rnd = random.Random(seed)
    small = Image.new("L", (W // 3, H // 3))
    small.putdata([128 + rnd.randint(-amount * 6, amount * 6) for _ in range(small.width * small.height)])
    noise = small.resize((W, H), Image.BILINEAR).filter(ImageFilter.GaussianBlur(0.6))
    return Image.blend(img, Image.composite(Image.new("RGB", (W, H), "#FFFFFF"), img, noise), 0.055)


def paper_bg(cell=52, grid=LINE, base=PAPER, tint=None, tint_box=None, grain_amt=5):
    """Spreadsheet paper: hairline cell grid, optional tinted zone."""
    img = Image.new("RGB", (W, H), base)
    d = ImageDraw.Draw(img)
    if tint and tint_box:
        d.rectangle(tint_box, fill=tint)
    for x in range(0, W, cell):
        d.line([(x, 0), (x, H)], fill=grid, width=1)
    for y in range(0, H, cell):
        d.line([(0, y), (W, y)], fill=grid, width=1)
    return grain(img, grain_amt)


def soft_shadow(canvas, box, blur=34, dy=18, alpha=58, colour="#33566B", radius=0):
    layer = Image.new("L", (W, H), 0)
    dd = ImageDraw.Draw(layer)
    x0, y0, x1, y1 = box
    if radius:
        dd.rounded_rectangle([x0, y0 + dy, x1, y1 + dy], radius=radius, fill=alpha)
    else:
        dd.rectangle([x0, y0 + dy, x1, y1 + dy], fill=alpha)
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    canvas.paste(Image.new("RGB", (W, H), colour), (0, 0), layer)


def fitted(shot, max_w, max_h, max_scale=1.4):
    sw, sh = shot.size
    s = min(max_w / sw, max_h / sh, max_scale)
    return int(sw * s), int(sh * s)


def sheet(canvas, shot, x, y, size, angle=0.0, border="#FFFFFF", bw=10,
          shadow=(38, 20, 62), tab=None, tab_fill=MINT, tab_text_fill=INK):
    """A screenshot as a physical sheet: white margin, optional tab, optional tilt."""
    x, y = int(x), int(y)
    nw, nh = int(size[0]), int(size[1])
    img = shot.resize((nw, nh), Image.LANCZOS)
    pad = bw
    tab_h = 0 if not tab else 58
    card = Image.new("RGB", (nw + pad * 2, nh + pad * 2 + tab_h), border)
    cd = ImageDraw.Draw(card)
    if tab:
        cd.rectangle([0, 0, card.width, tab_h], fill=tab_fill)
        f = font(MED, 30)
        tracked(cd, card.width / 2, (tab_h - line_h(f)) / 2 + 2, tab.upper(), f,
                tab_text_fill, tracking=6)
    card.paste(img, (pad, pad + tab_h))
    cd.rectangle([pad - 1, pad + tab_h - 1, pad + nw, pad + tab_h + nh], outline=LINE_DEEP, width=1)

    blur, dy, alpha = shadow
    if angle:
        card = card.convert("RGBA")
        pad_img = Image.new("RGBA", (card.width + 8, card.height + 8), (0, 0, 0, 0))
        pad_img.paste(card, (4, 4))
        card = pad_img.rotate(angle, expand=True, resample=Image.BICUBIC)
        mask = card.split()[3]
        sh = mask.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * alpha / 255))
        canvas.paste(Image.new("RGB", card.size, INK), (x, y + dy), sh)
        canvas.paste(card, (x, y), card)
        ox = (card.width - nw) // 2
        oy = (card.height - nh) // 2
        return (x + ox, y + oy, x + ox + nw, y + oy + nh)
    soft_shadow(canvas, (x, y, x + card.width, y + card.height), blur, dy, alpha)
    canvas.paste(card, (x, y))
    return (x + pad, y + pad + tab_h, x + pad + nw, y + pad + tab_h + nh)


def highlighter(d, x0, y0, x1, y1, colour=MINT, skew=6):
    """Marker-pen swipe behind a word — hand-made, not a rectangle."""
    d.polygon([(x0 - skew, y1), (x0 + 2, y0 + 4), (x1 + skew, y0), (x1 - 2, y1 - 3)], fill=colour)


def bullet_rows(d, items, x, top, gap=76, size=36, fill=INK, marker=MINT, cols=2,
                col_x=None, marker_shape="square"):
    f = font(REG, size)
    for i, t in enumerate(items):
        c, r = (i % cols, i // cols) if cols > 1 else (0, i)
        px = (col_x[c] if col_x else x + c * 780)
        py = top + r * gap
        my = py + (line_h(f) - 14) // 2 + 2
        if marker_shape == "square":
            d.rectangle([px, my, px + 14, my + 14], fill=marker)
        else:
            d.ellipse([px, my - 1, px + 15, my + 14], fill=marker)
        d.text((px + 36, py), t, font=f, fill=fill)
    return top + ((len(items) + cols - 1) // cols) * gap


def footer(canvas, phrase, band_y=1786, band_h=82, band_fill=MINT, phrase_fill=INK,
           brand_fill=SLATE, brand="CLIPBOARDWORKS"):
    d = ImageDraw.Draw(canvas)
    d.rectangle([0, band_y, W, band_y + band_h], fill=band_fill)
    d.text((W / 2, band_y + band_h / 2), phrase, font=font(MED, 38), fill=phrase_fill, anchor="mm")
    tracked(d, W / 2, band_y + band_h + 44, brand, font(MED, 30), brand_fill, tracking=13)


def corners(d, size=62, margin=40, colours=(MINT, MINT, MINT, MINT)):
    pts = [(margin, margin), (W - margin - size, margin),
           (margin, H - margin - size), (W - margin - size, H - margin - size)]
    for (x, y), c in zip(pts, colours):
        d.rectangle([x, y, x + size, y + size], fill=c)
