"""Shared drawing kit for the Budget Planner Etsy mockups (2000x2000)."""
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W = H = 2000
FONT_DIR = "/home/user/.fonts/poppins"
REG = f"{FONT_DIR}/Poppins-Regular.ttf"
MED = f"{FONT_DIR}/Poppins-Medium.ttf"
BLD = f"{FONT_DIR}/Poppins-Bold.ttf"

LIGHT = dict(
    bg="#0A1340", glow="#0E1A4E", mint="#7CF89C", second="#2B5CE6",
    text="#FFFFFF", rule_h=14, band_h=82,
)
DARK = dict(
    bg="#060912", glow="#0F1424", mint="#7CF89C", second="#1B7A50",
    text="#FFFFFF", rule_h=8, band_h=82,
)


def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(draw, s, f, tracking=0):
    if not s:
        return 0
    total = sum(draw.textlength(ch, font=f) for ch in s)
    return total + tracking * (len(s) - 1)


def draw_tracked(draw, x, y, s, f, fill, tracking=0, anchor_x="center"):
    """Draw s with letter spacing. y is the TOP of the line."""
    wdt = text_w(draw, s, f, tracking)
    if anchor_x == "center":
        cx = x - wdt / 2
    elif anchor_x == "right":
        cx = x - wdt
    else:
        cx = x
    for ch in s:
        draw.text((cx, y), ch, font=f, fill=fill)
        cx += draw.textlength(ch, font=f) + tracking
    return wdt


def fit_size(draw, s, path, target_w, tracking_ratio=0.14, lo=40, hi=200):
    """Largest font size whose tracked width fits target_w."""
    best = lo
    while lo <= hi:
        mid = (lo + hi) // 2
        f = font(path, mid)
        if text_w(draw, s, f, mid * tracking_ratio) <= target_w:
            best, lo = mid, mid + 1
        else:
            hi = mid - 1
    return best


def line_h(f):
    a, d = f.getmetrics()
    return a + d


def radial_glow(base, cx, cy, radius, colour, strength=1.0):
    """Soft radial wash painted over base."""
    layer = Image.new("L", (W // 4, H // 4), 0)
    d = ImageDraw.Draw(layer)
    r = radius / 4
    d.ellipse([cx / 4 - r, cy / 4 - r, cx / 4 + r, cy / 4 + r], fill=int(255 * strength))
    layer = layer.filter(ImageFilter.GaussianBlur(r / 2.2)).resize((W, H), Image.LANCZOS)
    wash = Image.new("RGB", (W, H), colour)
    return Image.composite(wash, base, layer)


def corner_squares(draw, colour, size=62, margin=40, colours=None):
    pts = [(margin, margin), (W - margin - size, margin),
           (margin, H - margin - size), (W - margin - size, H - margin - size)]
    for i, (x, y) in enumerate(pts):
        c = colours[i % len(colours)] if colours else colour
        draw.rectangle([x, y, x + size, y + size], fill=c)


def paste_paper(canvas, shot, box, border="#FFFFFF", border_w=2, max_scale=1.4,
                shadow_blur=24, shadow_dy=10, shadow_alpha=150):
    """Fit shot inside box (x0,y0,x1,y1), keep aspect, draw border + soft shadow.
    Returns the pasted rectangle."""
    bx0, by0, bx1, by1 = box
    bw, bh = bx1 - bx0, by1 - by0
    sw, sh = shot.size
    scale = min(bw / sw, bh / sh, max_scale)
    nw, nh = max(1, int(sw * scale)), max(1, int(sh * scale))
    img = shot.resize((nw, nh), Image.LANCZOS)
    x = bx0 + (bw - nw) // 2
    y = by0 + (bh - nh) // 2

    shade = Image.new("L", (W, H), 0)
    ImageDraw.Draw(shade).rectangle(
        [x - border_w, y - border_w + shadow_dy, x + nw + border_w, y + nh + border_w + shadow_dy],
        fill=shadow_alpha)
    shade = shade.filter(ImageFilter.GaussianBlur(shadow_blur))
    canvas.paste(Image.new("RGB", (W, H), "#000000"), (0, 0), shade)

    d = ImageDraw.Draw(canvas)
    d.rectangle([x - border_w, y - border_w, x + nw + border_w - 1, y + nh + border_w - 1],
                fill=border)
    canvas.paste(img, (x, y))
    return (x, y, x + nw, y + nh)


def two_column_bullets(draw, items, top, theme, size=36, marker=14, gap_y=78,
                       left_x=250, right_x=1080, col_w=680):
    """Four bullets, two columns, square marker."""
    f = font(REG, size)
    for i, txt in enumerate(items):
        col, row = i % 2, i // 2
        x = left_x if col == 0 else right_x
        y = top + row * gap_y
        my = y + (line_h(f) - marker) // 2 + 2
        draw.rectangle([x, my, x + marker, my + marker], fill=theme["mint"])
        draw.text((x + marker + 22, y), txt, font=f, fill=theme["text"])
    rows = (len(items) + 1) // 2
    return top + rows * gap_y


def bottom_band(canvas, phrase, theme, brand="CLIPBOARDWORKS", band_y=1786):
    d = ImageDraw.Draw(canvas)
    bh = theme["band_h"]
    d.rectangle([0, band_y, W, band_y + bh], fill=theme["mint"])
    f = font(MED, 38)
    d.text((W / 2, band_y + bh / 2), phrase, font=f, fill=theme["bg"], anchor="mm")
    fb = font(MED, 30)
    draw_tracked(d, W / 2, band_y + bh + 44, brand, fb, theme["mint"], tracking=13)


def base_canvas(theme, glow_at=(1000, 900), glow_r=1150, glow_strength=1.0):
    canvas = Image.new("RGB", (W, H), theme["bg"])
    canvas = radial_glow(canvas, glow_at[0], glow_at[1], glow_r, theme["glow"], glow_strength)
    return canvas


def fitted_size(shot, max_w, max_h, max_scale=1.4):
    sw, sh = shot.size
    s = min(max_w / sw, max_h / sh, max_scale)
    return int(sw * s), int(sh * s)


def balance(y_top, y_bottom, block_heights, gaps=None):
    """Spread blocks between y_top and y_bottom with equal leftover gaps.
    Returns the y position of each block's top."""
    n = len(block_heights)
    used = sum(block_heights)
    free = (y_bottom - y_top) - used
    gap = free / (n + 1) if gaps is None else None
    ys, y = [], y_top + (gap if gaps is None else gaps[0])
    for i, h in enumerate(block_heights):
        ys.append(int(y))
        y += h + (gap if gaps is None else gaps[i + 1])
    return ys
