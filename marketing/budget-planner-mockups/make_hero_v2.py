"""Hero options v2 — built on the workbook's own palette."""
import pathlib
from PIL import Image, ImageDraw
import brand as B
from brand import (W, H, REG, MED, BLD, INK, INK_DEEP, SLATE, BLUE, MINT, MINT_SOFT,
                   AQUA_SOFT, LINE, LINE_DEEP, PAPER, PAPER_WARM, font, line_h,
                   tracked, text_w, fit_size, paper_bg, grain, sheet, fitted,
                   highlighter, bullet_rows, footer, corners, soft_shadow)

SHOTS = "/home/user/Data-Analysis/shots"
TITLE_WORDS = ["EIGHT", "TABS", "BECAME", "TWO"]
SUB = "One sheet to plan, one to log. That is the whole file."
BULLETS = ["Budget and Log", "Nothing else to learn",
           "Google Sheets and Excel", "Instant download"]
FOOT = "The simplest budget spreadsheet you will actually keep using"
BAND_Y = 1786


def title_words(d, cx, y, words, f, tracking, fill, mark=None, mark_colour=MINT):
    """Draw a tracked caps title word by word; optionally highlighter one word."""
    space = f.size * 0.42
    widths = [text_w(d, w, f, tracking) for w in words]
    total = sum(widths) + space * (len(words) - 1)
    x = cx - total / 2
    boxes = []
    for w, wd in zip(words, widths):
        boxes.append((x, x + wd))
        x += wd + space
    if mark is not None:
        x0, x1 = boxes[mark]
        asc = f.getmetrics()[0]
        highlighter(d, x0 - 18, y + asc * 0.28, x1 + 18, y + asc * 1.02, mark_colour)
    for (x0, _), w in zip(boxes, words):
        tracked(d, x0, y, w, f, fill, tracking=tracking, align="left")
    return y + line_h(f)


def open_shot(name):
    return Image.open(f"{SHOTS}/{name}").convert("RGB")


# ---------------------------------------------------------------- 1. paper grid
def hero_paper(path):
    c = paper_bg(cell=52)
    d = ImageDraw.Draw(c)
    corners(d, colours=(MINT, BLUE, BLUE, MINT))
    f = font(BLD, fit_size(d, " ".join(TITLE_WORDS), BLD, 1560))
    y = title_words(d, W / 2, 214, TITLE_WORDS, f, f.size * 0.12, INK_DEEP, mark=3)
    y += 26
    d.rectangle([W / 2 - 280, y, W / 2 + 280, y + 14], fill=MINT)
    y += 14 + 46
    fs = font(REG, 44)
    d.text((W / 2, y), SUB, font=fs, fill=SLATE, anchor="ma")
    y += line_h(fs) + 74

    shot = open_shot("light-00-dashboard.png")
    nw, nh = fitted(shot, 1420, 820)
    sheet(c, shot, (W - nw) // 2 - 60, y, (nw, nh), angle=-1.4, bw=16,
          shadow=(40, 26, 70))
    bullet_rows(d, BULLETS, 0, 1520, col_x=[268, 1092])
    footer(c, FOOT, brand_fill=SLATE)
    c.save(path)


# --------------------------------------------------------------- 2. two sheets
def hero_two_sheets(path):
    c = paper_bg(cell=52, base=PAPER, tint=MINT_SOFT, tint_box=[0, 0, W, 566])
    d = ImageDraw.Draw(c)
    d.rectangle([0, 562, W, 568], fill=MINT)
    corners(d, colours=(INK, INK, MINT, MINT))
    f = font(BLD, fit_size(d, " ".join(TITLE_WORDS), BLD, 1520))
    y = title_words(d, W / 2, 176, TITLE_WORDS, f, f.size * 0.12, INK_DEEP)
    y += 20
    d.rectangle([W / 2 - 280, y, W / 2 + 280, y + 14], fill=MINT)
    y += 14 + 40
    d.text((W / 2, y), SUB, font=font(REG, 44), fill=INK, anchor="ma")

    log = open_shot("light-07.png")
    plan = open_shot("light-00-dashboard.png")
    lw, lh = fitted(log, 940, 620)
    pw, ph = fitted(plan, 1010, 620)
    sheet(c, log, 930, 706, (lw, lh), angle=2.0, bw=13, tab="Log", tab_fill=BLUE,
          tab_text_fill="#FFFFFF", shadow=(34, 20, 52))
    sheet(c, plan, 96, 806, (pw, ph), angle=-1.5, bw=13, tab="Budget",
          shadow=(40, 24, 62))
    bullet_rows(d, BULLETS, 0, 1540, col_x=[268, 1092])
    footer(c, FOOT)
    c.save(path)


# ------------------------------------------------------------------ 3. tab bar
def hero_tab_bar(path):
    c = paper_bg(cell=52, base=PAPER_WARM)
    d = ImageDraw.Draw(c)
    corners(d, colours=(MINT, MINT, MINT, MINT))

    # the metaphor: eight tabs, two survive
    tw, th, gap, ty = 196, 74, 18, 196
    total = 8 * tw + 7 * gap
    tx = (W - total) / 2
    labels = ["Budget", "Log"]
    for i in range(8):
        x0 = tx + i * (tw + gap)
        live = i < 2
        d.rounded_rectangle([x0, ty, x0 + tw, ty + th], radius=14,
                            fill=MINT if live else "#FFFFFF",
                            outline=MINT if live else LINE_DEEP, width=2)
        if live:
            fl = font(MED, 30)
            d.text((x0 + tw / 2, ty + th / 2), labels[i], font=fl, fill=INK, anchor="mm")
        else:
            d.line([x0 + 42, ty + th / 2, x0 + tw - 42, ty + th / 2], fill=LINE_DEEP, width=4)
    d.line([0, ty + th + 2, W, ty + th + 2], fill=LINE_DEEP, width=2)

    f = font(BLD, fit_size(d, " ".join(TITLE_WORDS), BLD, 1480))
    y = title_words(d, W / 2, ty + th + 92, TITLE_WORDS, f, f.size * 0.12, INK_DEEP, mark=3)
    y += 20
    d.rectangle([W / 2 - 280, y, W / 2 + 280, y + 14], fill=MINT)
    y += 14 + 42
    fs = font(REG, 44)
    d.text((W / 2, y), SUB, font=fs, fill=SLATE, anchor="ma")
    y += line_h(fs) + 60

    shot = open_shot("light-00-dashboard.png")
    nw, nh = fitted(shot, 1360, 700)
    sheet(c, shot, (W - nw) // 2 - 14, y, (nw, nh), bw=14, shadow=(34, 20, 55))
    bullet_rows(d, BULLETS, 0, 1548, col_x=[268, 1092])
    footer(c, FOOT, brand_fill=SLATE)
    c.save(path)


# ---------------------------------------------------------------- 4. editorial
def hero_editorial(path):
    c = paper_bg(cell=52, base=PAPER, tint=AQUA_SOFT, tint_box=[0, 0, 720, H])
    d = ImageDraw.Draw(c)
    d.rectangle([716, 0, 722, H], fill=MINT)
    corners(d, colours=(INK, MINT, INK, MINT))

    x = 118
    fbig = font(BLD, 98)
    yy = 236
    for i, ln in enumerate(["EIGHT", "TABS", "BECAME", "TWO"]):
        if i == 3:
            wd = text_w(d, ln, fbig, fbig.size * 0.1)
            highlighter(d, x - 16, yy + 28, x + wd + 16, yy + 102, MINT)
        tracked(d, x, yy, ln, fbig, INK_DEEP, tracking=fbig.size * 0.1, align="left")
        yy += line_h(fbig) - 24
    yy += 24
    d.rectangle([x, yy, x + 280, yy + 14], fill=BLUE)
    yy += 14 + 42
    fs = font(REG, 37)
    for ln in ["One sheet to plan,", "one to log. That is", "the whole file."]:
        d.text((x, yy), ln, font=fs, fill=SLATE)
        yy += line_h(fs) + 2

    plan = open_shot("light-00-dashboard.png")
    log = open_shot("light-07.png")
    pw, ph = fitted(plan, 1180, 640)
    lw, lh = fitted(log, 1180, 640)
    sheet(c, plan, 812, 250, (pw, ph), angle=-1.1, bw=14, shadow=(40, 24, 62))
    sheet(c, log, 884, 990, (lw, lh), angle=1.3, bw=14, shadow=(40, 24, 58))

    bullet_rows(d, BULLETS, x, 1300, cols=1, gap=74, col_x=[x])
    footer(c, FOOT, brand_fill=SLATE)
    c.save(path)


# ---------------------------------------------------------------- 5. spotlight
def hero_spotlight(path):
    c = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(c)
    for y in range(0, H, 52):
        d.line([(0, y), (W, y)], fill="#3B5F76", width=1)
    for x in range(0, W, 52):
        d.line([(x, 0), (x, H)], fill="#3B5F76", width=1)
    c = grain(c, 4)
    d = ImageDraw.Draw(c)
    corners(d, colours=(MINT, MINT, MINT, MINT))

    fpill = font(MED, 30)
    label = "TWO SHEETS. THAT IS THE WHOLE FILE."
    pw = text_w(d, label, fpill, 6) + 76
    d.rounded_rectangle([(W - pw) / 2, 196, (W + pw) / 2, 262], radius=33, fill=MINT)
    tracked(d, W / 2, 196 + (66 - line_h(fpill)) / 2 + 2, label, fpill, INK, tracking=6)

    f = font(BLD, fit_size(d, " ".join(TITLE_WORDS), BLD, 1560))
    y = title_words(d, W / 2, 322, TITLE_WORDS, f, f.size * 0.12, "#FFFFFF")
    y += 24
    d.rectangle([W / 2 - 280, y, W / 2 + 280, y + 14], fill=MINT)
    y += 14 + 46
    fs = font(REG, 44)
    d.text((W / 2, y), SUB, font=fs, fill="#C6D8E2", anchor="ma")
    y += line_h(fs) + 66

    shot = open_shot("light-00-dashboard.png")
    nw, nh = fitted(shot, 1400, 760)
    sheet(c, shot, (W - nw) // 2 - 14, y, (nw, nh), bw=16, shadow=(46, 26, 120))
    bullet_rows(d, BULLETS, 0, 1544, col_x=[268, 1092], fill="#EAF2F6")
    footer(c, FOOT, brand_fill=MINT)
    c.save(path)


if __name__ == "__main__":
    out = pathlib.Path("hero-options-v2")
    out.mkdir(exist_ok=True)
    hero_paper(out / "v2_1_paper.png")
    hero_two_sheets(out / "v2_2_two_sheets.png")
    hero_tab_bar(out / "v2_3_tab_bar.png")
    hero_editorial(out / "v2_4_editorial.png")
    hero_spotlight(out / "v2_5_spotlight.png")
    print("done")
