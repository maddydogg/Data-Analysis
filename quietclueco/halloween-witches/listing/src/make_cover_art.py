"""Render the cover (an old horror-mystery one-sheet, see poster.py) at the exact page shape of each
case-book format and save it where src/render.py picks it up:

    python3 make_cover_art.py   ->  ../../src/art/cover_{letter,a4,ipad}.jpg

Run it before src/build.py whenever the cover changes.
"""
import os
import kit
import poster

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.abspath(os.path.join(HERE, "..", "..", "src", "art"))
PAGES = {"letter": (612, 792), "a4": (595.28, 841.89), "ipad": (768, 1024)}   # points
WIDTH_PX = {"letter": 2100, "a4": 2100, "ipad": 1536}                        # about 250 dpi for print

kit.set_font_dir(os.path.abspath(os.path.join(HERE, "..", "..", "src", "fonts")))

def build():
    os.makedirs(ART, exist_ok=True)
    out = {}
    for fmt, (pw, ph) in PAGES.items():
        W = WIDTH_PX[fmt]; H = round(W * ph / pw)
        f = poster.cover_poster(W, H)
        p = os.path.join(ART, f"cover_{fmt}.jpg")
        f.img.convert("RGB").save(p, quality=90, optimize=True, progressive=True)
        out[fmt] = (p, W, H, round(W / (pw / 72)), [t for _, _, t in f.sources])
    return out

if __name__ == "__main__":
    for fmt, (p, W, H, dpi, texts) in build().items():
        print(fmt, f"{W}x{H}px", f"~{dpi} dpi", os.path.getsize(p) // 1024, "KB")
