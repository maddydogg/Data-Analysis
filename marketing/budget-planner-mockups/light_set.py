"""bp_light_01..10 — the tab-bar treatment, on the workbook's own palette."""
import pathlib
from PIL import Image, ImageDraw
import brand as B
from brand import (W, H, REG, MED, BLD, INK, INK_DEEP, SLATE, BLUE, MINT, MINT_SOFT,
                   AQUA_SOFT, LINE, LINE_DEEP, PAPER, PAPER_WARM, font, line_h,
                   tracked, text_w, fit_size, paper_bg, sheet, fitted, highlighter,
                   footer, corners)

SHOTS = "/home/user/Data-Analysis/shots"
OUT = pathlib.Path("light")
BAND_Y = 1786
TAB_Y, TAB_H, TAB_W, TAB_GAP = 186, 74, 196, 18
BULLETS_TOP = 1556
BULLET_GAP = 76


def shot(name):
    return Image.open(f"{SHOTS}/{name}").convert("RGB")


# ----------------------------------------------------------------- chrome
def tab_bar(d, active="Budget"):
    """Eight tabs; two are alive. The active one is filled."""
    total = 8 * TAB_W + 7 * TAB_GAP
    x = (W - total) / 2
    for i in range(8):
        x0 = x + i * (TAB_W + TAB_GAP)
        label = ["Budget", "Log"][i] if i < 2 else None
        if label:
            on = label == active
            d.rounded_rectangle([x0, TAB_Y, x0 + TAB_W, TAB_Y + TAB_H], radius=14,
                                fill=MINT if on else "#FFFFFF", outline=MINT, width=3)
            d.text((x0 + TAB_W / 2, TAB_Y + TAB_H / 2), label, font=font(MED, 30),
                   fill=INK if on else INK, anchor="mm")
        else:
            d.rounded_rectangle([x0, TAB_Y, x0 + TAB_W, TAB_Y + TAB_H], radius=14,
                                fill="#FFFFFF", outline=LINE_DEEP, width=2)
            d.line([x0 + 42, TAB_Y + TAB_H / 2, x0 + TAB_W - 42, TAB_Y + TAB_H / 2],
                   fill=LINE_DEEP, width=4)
    d.line([0, TAB_Y + TAB_H + 2, W, TAB_Y + TAB_H + 2], fill=LINE_DEEP, width=2)


def heading(c, lines, sub, mark=None, top=352, max_w=1480):
    """Tracked caps heading (1-2 lines), mint rule, subtitle. Returns bottom y."""
    d = ImageDraw.Draw(c)
    size = min(fit_size(d, ln, BLD, max_w, hi=132) for ln in lines)
    f = font(BLD, size)
    tr = size * 0.12
    y = top
    for li, ln in enumerate(lines):
        words = ln.split(" ")
        space = size * 0.42
        widths = [text_w(d, w, f, tr) for w in words]
        x = W / 2 - (sum(widths) + space * (len(words) - 1)) / 2
        for wi, (word, wd) in enumerate(zip(words, widths)):
            if mark == (li, wi):
                asc = f.getmetrics()[0]
                highlighter(d, x - 16, y + asc * 0.30, x + wd + 16, y + asc * 1.02, MINT)
            tracked(d, x, y, word, f, INK_DEEP, tracking=tr, align="left")
            x += wd + space
        y += line_h(f) - size * 0.20
    y += 30
    d.rectangle([W / 2 - 280, y, W / 2 + 280, y + 14], fill=MINT)
    y += 14 + 42
    fs = font(REG, 44)
    d.text((W / 2, y), sub, font=fs, fill=SLATE, anchor="ma")
    return y + line_h(fs)


def bullets(c, items, top=BULLETS_TOP):
    d = ImageDraw.Draw(c)
    f = font(REG, 36)
    for i, t in enumerate(items):
        col, row = i % 2, i // 2
        x = [268, 1092][col]
        y = top + row * BULLET_GAP
        my = y + (line_h(f) - 14) // 2 + 2
        d.rectangle([x, my, x + 14, my + 14], fill=MINT)
        d.text((x + 36, y), t, font=f, fill=INK)


def base(active="Budget"):
    c = paper_bg(cell=52, base=PAPER_WARM)
    d = ImageDraw.Draw(c)
    corners(d, colours=(MINT, MINT, MINT, MINT))
    tab_bar(d, active)
    return c


def finish(c, foot, path):
    footer(c, foot, brand_fill=SLATE)
    c.save(OUT / path)
    print("·", path)


def centre_sheet(c, img, top, bottom, max_w=1360, angle=0.0, bw=14):
    nw, nh = fitted(img, max_w, bottom - top)
    y = top + (bottom - top - nh) // 2
    return sheet(c, img, (W - nw) // 2 - bw, y, (nw, nh), angle=angle, bw=bw,
                 shadow=(34, 20, 55))


def sheet_and_bullets(c, img, head_bottom, items, max_w=1400, angle=0.0, bw=14, gap=96):
    """Screenshot + bullet block treated as one unit, centred in the free space."""
    top = head_bottom + 40
    nw, nh = fitted(img, max_w, (BAND_Y - 70) - top - gap - 2 * BULLET_GAP)
    total = nh + gap + 2 * BULLET_GAP
    y0 = top + max(0, ((BAND_Y - 70) - top - total) // 2)
    sheet(c, img, (W - nw) // 2 - bw, y0, (nw, nh), angle=angle, bw=bw, shadow=(34, 20, 55))
    bullets(c, items, int(y0 + nh + gap))


# ------------------------------------------------------------------- slides
def s01():
    c = base("Budget")
    y = heading(c, ["EIGHT TABS BECAME TWO"],
                "One sheet to plan, one to log. That is the whole file.", mark=(0, 3))
    sheet_and_bullets(c, shot("light-00-dashboard.png"), y,
                      ["Budget and Log", "Nothing else to learn",
                       "Google Sheets and Excel", "Instant download"], max_w=1520)
    finish(c, "The simplest budget spreadsheet you will actually keep using", "bp_light_01.png")


def s02():
    c = base("Budget")
    y = heading(c, ["SEE THE OVERSPEND", "THE DAY IT HAPPENS"],
                "Planned, actual, left and percent used — per category", mark=(0, 2))
    sheet_and_bullets(c, shot("light-02.png"), y,
                      ["20 categories", "Over budget turns red",
                       "Totals at the bottom", "Nothing to sum by hand"],
                      max_w=980, angle=-1.0)
    finish(c, "The number you actually needed to see", "bp_light_02.png")


def s03():
    c = base("Log")
    y = heading(c, ["ONE LOG FEEDS", "EVERYTHING"],
                "Date, type, category, account, amount. That is it.", mark=(1, 0))
    sheet_and_bullets(c, shot("light-07.png"), y,
                      ["Dropdowns, no typos", "500 rows ready",
                       "Blue is yours, dark calculates", "No copy-paste"], max_w=1440)
    finish(c, "Type it once, it lands everywhere", "bp_light_03.png")


def s04():
    c = base("Budget")
    d = ImageDraw.Draw(c)
    y = heading(c, ["SWITCH THE MONTH,", "THE PAGE REWRITES ITSELF"],
                "Pick a month from the list — every total follows", mark=(0, 2))
    head = shot("light-01.png")
    ix0, iy0, ix1, iy1 = centre_sheet(c, head, y + 70, y + 420, max_w=1500)
    iw, ih = ix1 - ix0, iy1 - iy0
    # ring the month picker inside the real header
    d.rounded_rectangle([ix0 + iw * 0.146, iy0 + ih * 0.325,
                         ix0 + iw * 0.330, iy0 + ih * 0.505],
                        radius=10, outline=MINT, width=5)

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    cw, ch, gp = 132, 84, 16
    total = 6 * cw + 5 * gp
    x0 = (W - total) / 2
    top = iy1 + 150
    d.text((W / 2, top - 74), "the twelve the file already knows",
           font=font(REG, 36), fill=SLATE, anchor="ma")
    f = font(MED, 32)
    for i, m in enumerate(months):
        col, row = i % 6, i // 6
        x = x0 + col * (cw + gp)
        yy = top + row * (ch + gp)
        on = m == "Sep"
        d.rounded_rectangle([x, yy, x + cw, yy + ch], radius=12,
                            fill=MINT if on else "#FFFFFF",
                            outline=MINT if on else LINE_DEEP, width=3 if on else 2)
        d.text((x + cw / 2, yy + ch / 2), m, font=f, fill=INK if on else SLATE, anchor="mm")
    bullets(c, ["A year in one file", "No new tab per month",
                "No formulas to drag", "History stays in the log"])
    finish(c, "Twelve months, one page", "bp_light_04.png")


def s05():
    c = base("Budget")
    y = heading(c, ["THE CHART DRAWS", "ITSELF"],
                "Spending by category, rebuilt every time you log", mark=(1, 0))
    sheet_and_bullets(c, shot("light-03.png"), y,
                      ["No setup", "No plugins", "Updates as you type",
                       "Reads from the log"], max_w=1140, angle=-0.9)
    finish(c, "Look at the month, not at the spreadsheet", "bp_light_05.png")


def s06():
    c = base("Budget")
    y = heading(c, ["WHAT YOUR BILLS", "REALLY COST"],
                "Weekly, monthly and yearly bills, all converted to a monthly figure",
                mark=(1, 1))
    sheet_and_bullets(c, shot("light-04.png"), y,
                      ["True monthly cost", "Due day and paid flag",
                       "Yearly bills spread out", "One honest total"], max_w=1300)
    finish(c, "The $39 gym is $169 a month", "bp_light_06.png")


def s07():
    c = base("Budget")
    d = ImageDraw.Draw(c)
    y = heading(c, ["GOALS AND DEBTS,", "SIDE BY SIDE"],
                "Progress you can see without opening a second file", mark=(0, 2))
    funds, debts = shot("light-05.png"), shot("light-06.png")
    top = y + 120
    col_w, cap_h = 800, 62
    fw, fh = fitted(funds, col_w, 620)
    dw, dh = fitted(debts, col_w, 620)
    band = max(fh, dh)
    fl = font(MED, 36)
    for cx, label in ((512, "Savings funds"), (1488, "Debt payoff")):
        d.text((cx, top), label, font=fl, fill=INK, anchor="ma")
    sheet(c, funds, 512 - fw // 2 - 13, top + cap_h + (band - fh) // 2, (fw, fh),
          bw=13, shadow=(30, 18, 50))
    sheet(c, debts, 1488 - dw // 2 - 13, top + cap_h + (band - dh) // 2, (dw, dh),
          bw=13, shadow=(30, 18, 50))
    bullets(c, ["Progress to each goal", "Smallest balance first",
                "Percent paid off", "Remaining at a glance"],
            top=int(top + cap_h + band + 130))
    finish(c, "The two tables most budget templates leave out", "bp_light_07.png")


def s08():
    c = base("Budget")
    d = ImageDraw.Draw(c)
    y = heading(c, ["YOUR MONTH IN", "FOUR NUMBERS"],
                "Income, expenses, saved, left to spend", mark=(1, 1))
    head = shot("light-01.png")
    sx0, sy0, sx1, sy1 = centre_sheet(c, head, y + 130, y + 560, max_w=1760)
    sw, sh = sx1 - sx0, sy1 - sy0
    # the four metric cards, as fractions of the header shot
    cards = [(0.123, "Income"), (0.325, "Expenses"), (0.590, "Saved"), (0.873, "Left to spend")]
    label_y = sy1 + 300
    f = font(MED, 38)
    for fx, label in cards:
        cx = sx0 + sw * fx
        card_y = sy0 + sh * 0.86
        d.ellipse([cx - 9, card_y - 9, cx + 9, card_y + 9], fill=MINT)
        d.line([cx, card_y, cx, label_y - 22], fill=MINT, width=5)
        d.text((cx, label_y), label, font=f, fill=INK, anchor="ma")
    finish(c, "Open the file, know where you stand", "bp_light_08.png")


def s09():
    c = base("Budget")
    d = ImageDraw.Draw(c)
    y = heading(c, ["SET UP IN", "TWO MINUTES"],
                "Three steps, then the file runs itself", mark=(1, 1))
    steps = [("1", "Pick your month", "Type the first day up top."),
             ("2", "Name your categories", "Your words, not ours."),
             ("3", "Log your money", "Every row lands where it belongs.")]
    top = y + 170
    gap = 288
    fnum = font(BLD, 96)
    fh_ = font(MED, 54)
    fb = font(REG, 38)
    for i, (n, title, note) in enumerate(steps):
        yy = top + i * gap
        d.ellipse([430, yy, 430 + 132, yy + 132], fill=MINT)
        d.text((496, yy + 66), n, font=fnum, fill=INK, anchor="mm")
        d.text((626, yy + 16), title, font=fh_, fill=INK_DEEP)
        d.text((626, yy + 82), note, font=fb, fill=SLATE)
        if i < 2:
            d.line([496, yy + 148, 496, yy + gap - 16], fill=LINE_DEEP, width=4)
    finish(c, "No tutorial, no template to wrestle with", "bp_light_09.png")


def s10():
    c = base("Budget")
    d = ImageDraw.Draw(c)
    y = heading(c, ["WHAT YOU GET"],
                "One file, two sheets, nothing to install", mark=(0, 2))
    panels = [
        ("IN THE DOWNLOAD", ["Budget Planner spreadsheet",
                             "Works in Google Sheets and Excel",
                             "Formulas protected", "Yours forever"]),
        ("HOW IT WORKS", ["Pick your month", "Name your categories",
                          "Log your money", "It fills itself in"]),
    ]
    top = y + 90
    pw, ph = 800, 560
    fh_ = font(MED, 36)
    fb = font(REG, 34)
    for i, (title, items) in enumerate(panels):
        x = 130 + i * (pw + 140)
        d.rounded_rectangle([x, top, x + pw, top + ph], radius=26,
                            fill="#FFFFFF", outline=MINT, width=4)
        tracked(d, x + 46, top + 44, title, fh_, INK_DEEP, tracking=5, align="left")
        d.line([x + 46, top + 106, x + pw - 46, top + 106], fill=LINE_DEEP, width=2)
        yy = top + 140
        for it in items:
            d.rectangle([x + 46, yy + 14, x + 60, yy + 28], fill=MINT)
            d.text((x + 82, yy), it, font=fb, fill=INK)
            yy += 78

    label = "INSTANT DOWNLOAD"
    fp = font(MED, 40)
    pwid = text_w(d, label, fp, 8) + 110
    py = top + ph + 210
    d.rounded_rectangle([(W - pwid) / 2, py, (W + pwid) / 2, py + 96], radius=48, fill=MINT)
    tracked(d, W / 2, py + (96 - line_h(fp)) / 2 + 2, label, fp, INK, tracking=8)
    finish(c, "No subscription, no add-ons, no account needed", "bp_light_10.png")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for fn in (s01, s02, s03, s04, s05, s06, s07, s08, s09, s10):
        fn()
