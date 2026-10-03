"""The double-feature cover for the bundle, drawn with code (PIL) for any page shape: a vintage
cinema one-sheet with a marquee, the two case one-sheets side by side in their own palettes,
the bundle title and the billing block. No faces, no studio marks, no real film titles."""
import os, sys
from PIL import Image, ImageDraw, ImageFilter
import bundle as B

sys.path.insert(0, os.path.join(B.ROOT, "listing", "src"))
import kit      # noqa: E402
import poster as P      # noqa: E402
kit.set_font_dir(B.FONTS)

GOLD = B.MOON["accent"]; ORANGE = B.STORM["accent"]; CREAM = (0xF4, 0xEA, 0xD0)

def split_background(img, k, top=0):
    """Left half storm green, right half plum, joined by a thin gold seam."""
    W, H = img.size
    left = Image.new("RGBA", (W // 2, H)); P.gradient(left, B.STORM["dark"], B.STORM["mid"])
    right = Image.new("RGBA", (W - W // 2, H)); P.gradient(right, B.MOON["dark"], B.MOON["mid"])
    img.paste(left, (0, 0)); img.paste(right, (W // 2, 0))
    P.halftone(img, (0, top, W // 2, H), (0x9B, 0xC5, 0x3D, 26), 22 * k, falloff=lambda x, y: 0.55)
    P.halftone(img, (W // 2, top, W, H), (0x8E, 0x5B, 0xB5, 34), 22 * k, falloff=lambda x, y: 0.55)
    d = ImageDraw.Draw(img); d.rectangle([W / 2 - 3 * k, top, W / 2 + 3 * k, H], fill=GOLD)

def marquee(f, y0, h, k, title, sub):
    """A dark marquee board with two rows of bulbs and two lines of lettering."""
    W = f.img.width; d = f.draw()
    d.rectangle([0, y0, W, y0 + h], fill=(0x0B, 0x08, 0x0C))
    n = int(W / (64 * k))
    for row in (y0 + 20 * k, y0 + h - 20 * k):
        for i in range(n + 1):
            x = (i + 0.5) * W / (n + 1)
            P.glow(f.img, [x - 20 * k, row - 20 * k, x + 20 * k, row + 20 * k], (0xFF, 0xD2, 0x7A), 140, 9 * k)
            d = f.draw(); d.ellipse([x - 8 * k, row - 8 * k, x + 8 * k, row + 8 * k], fill=(0xFF, 0xE6, 0xA8))
    P.tracked(f, W / 2, y0 + 42 * k, title, P.hf("cinzel", 34 * k, 700), CREAM, 10 * k)
    fn = P.fit(sub, "bebas", 104 * k, W - 160 * k, track=14 * k)
    P.tracked(f, W / 2, y0 + 82 * k, sub, fn, (0xFF, 0xF1, 0xD2), 14 * k)

def one_sheet(img, path, cx, top, w, angle, frame_col):
    """Paste a case cover as a framed one-sheet, centred on cx with its top at `top`."""
    cov = Image.open(path).convert("RGBA")
    h = int(w * cov.height / cov.width)
    cov = cov.resize((int(w), h), Image.LANCZOS)
    b = max(6, int(w * 0.022))
    framed = Image.new("RGBA", (cov.width + 2 * b, cov.height + 2 * b), frame_col + (255,))
    framed.paste(cov, (b, b))
    fr = kit.Frame(img.width, img.height, (0, 0, 0)); fr.img = img
    fr.paste(framed, cx, top + framed.height / 2, angle=angle, shadow=True, shadow_strength=160)
    return top + framed.height

def stub(f, cx, cy, label, bg, fg, k):
    P.stub(f, cx, cy, label, bg, fg, w=280 * k, h=84 * k)

def cover(W, H):
    """The bundle cover for a page of W x H pixels."""
    k = W / 1200
    f = kit.Frame(int(W), int(H), (0, 0, 0)); img = f.img
    split_background(img, k)
    marquee(f, 0, 210 * k, k, "QUIETCLUECO PRESENTS", "A DOUBLE FEATURE")
    # the two one-sheets; sized so the title block below always fits
    title_h = 470 * k
    avail = H - 210 * k - title_h - 120 * k
    w = min(500 * k, avail / 1.32)
    top = 210 * k + 92 * k
    bottoms = []
    for c, cx, ang in ((B.CASES[0], W * 0.265, -2.2), (B.CASES[1], W * 0.735, 2.2)):
        fmt = "ipad" if H / W < 1.3 else ("a4" if H / W > 1.37 else "letter")
        bottoms.append(one_sheet(img, c["cover_art"][fmt], cx, top, w, ang, (0xF2, 0xE8, 0xD0)))
        stub(f, cx, top - 34 * k, c["feature"], c["pal"]["accent"], c["pal"]["dark"], k)
    y = max(bottoms) + 46 * k
    # title block
    big = P.fit("STORM & MOON", "abril", 190 * k, W - 120 * k)
    t = kit.Frame(int(W), int(big.size * 1.5), (0, 0, 0)); t.img = Image.new("RGBA", t.img.size, (0, 0, 0, 0))
    P.title_word(t, "STORM & MOON", W / 2, 6 * k, big, fill=GOLD, shadow=(0x5A, 0x1E, 0x10), depth=16 * k,
                 outline=(0x0B, 0x08, 0x0C), inline=CREAM, k=k)
    img.alpha_composite(t.img, (0, int(y))); f.sources += t.sources
    y += big.size * 1.12
    P.tracked(f, W / 2, y, "DOUBLE FEATURE", P.hf("cinzel", 70 * k, 800), CREAM, 18 * k)
    y += 104 * k
    d = f.draw(); d.line([(W * 0.18, y), (W * 0.82, y)], fill=GOLD, width=max(1, int(2 * k)))
    P.tracked(f, W / 2, y + 18 * k, B.TAGLINE.upper(), P.hf("oswald", 44 * k, 600), CREAM, 5 * k)
    P.tracked(f, W / 2, H - 112 * k, "TWO PRINTABLE MURDER MYSTERY PUZZLES  ·  PRINT OR PLAY ON iPAD",
              P.fit("TWO PRINTABLE MURDER MYSTERY PUZZLES  ·  PRINT OR PLAY ON iPAD", "oswald", 28 * k, W - 200 * k, 400, track=3 * k),
              CREAM, 3 * k)
    P.deco_frame(f, 30 * k, k, GOLD)
    P.aged(img, 11, border=int(18 * k))
    return f

PAGES = {"letter": (612, 792), "a4": (595.28, 841.89), "ipad": (768, 1024)}
WIDTH_PX = {"letter": 2100, "a4": 2100, "ipad": 1536}

def build(outdir):
    os.makedirs(outdir, exist_ok=True)
    out = {}
    for fmt, (pw, ph) in PAGES.items():
        W = WIDTH_PX[fmt]; H = round(W * ph / pw)
        fr = cover(W, H)
        p = os.path.join(outdir, f"cover_{fmt}.jpg")
        fr.img.convert("RGB").save(p, quality=88, optimize=True, progressive=True)
        out[fmt] = p
    return out

if __name__ == "__main__":
    print(build(os.path.join(B.HERE, "art")))
