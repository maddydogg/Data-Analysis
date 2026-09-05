"""Contact sheet: all ten slides at a glance."""
import sys, pathlib
from PIL import Image, ImageDraw
from brand import MED, REG, INK, SLATE, LINE_DEEP, PAPER_WARM, font, tracked, line_h

def build(src_dir, pattern, out, title):
    src = pathlib.Path(src_dir)
    files = [src / (pattern % i) for i in range(1, 11)]
    cols, rows = 5, 2
    cell, gap, pad, cap = 360, 34, 60, 46
    W = pad * 2 + cols * cell + (cols - 1) * gap
    top = 150
    H = top + rows * (cell + cap + gap) + pad
    sheet = Image.new("RGB", (W, H), PAPER_WARM)
    d = ImageDraw.Draw(sheet)
    f = font(MED, 42)
    tracked(d, W / 2, 52, title, f, INK, tracking=8)
    fc = font(REG, 26)
    for i, fp in enumerate(files):
        col, row = i % cols, i // cols
        x = pad + col * (cell + gap)
        y = top + row * (cell + cap + gap)
        im = Image.open(fp).convert("RGB").resize((cell, cell), Image.LANCZOS)
        d.rectangle([x - 1, y - 1, x + cell, y + cell], outline=LINE_DEEP, width=1)
        sheet.paste(im, (x, y))
        d.text((x + cell / 2, y + cell + 12), fp.stem, font=fc, fill=SLATE, anchor="ma")
    sheet.save(out)
    print(out, sheet.size)

if __name__ == "__main__":
    build("light", "bp_light_%02d.png", "contact_sheet_light.png", "BUDGET PLANNER · LIGHT")
