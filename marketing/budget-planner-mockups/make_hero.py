"""Five hero treatments for bp_light_01 — pick one, the whole set follows it."""
import pathlib
from PIL import Image, ImageDraw
import mockup_kit as K
from mockup_kit import (W, H, LIGHT, REG, MED, BLD, font, draw_tracked, fit_size,
                        line_h, corner_squares, paste_paper, two_column_bullets,
                        bottom_band, base_canvas, fitted_size, balance)

SHOTS = "/home/user/Data-Analysis/shots"
T = LIGHT
TITLE = "EIGHT TABS BECAME TWO"
SUB = "One sheet to plan, one to log. That is the whole file."
BULLETS = ["Budget and Log", "Nothing else to learn",
           "Google Sheets and Excel", "Instant download"]
FOOT = "The simplest budget spreadsheet you will actually keep using"

BAND_Y = 1786          # top of the mint band
BULLET_GAP = 78
BULLETS_H = 2 * BULLET_GAP


def head_block(canvas, top, title, sub, target_w=1700, rule_w=560, rule_colour=None):
    d = ImageDraw.Draw(canvas)
    size = fit_size(d, title, BLD, target_w)
    f = font(BLD, size)
    draw_tracked(d, W / 2, top, title, f, T["text"], tracking=size * 0.14)
    y = top + line_h(f) + 38
    d.rectangle([W / 2 - rule_w / 2, y, W / 2 + rule_w / 2, y + T["rule_h"]],
                fill=rule_colour or T["mint"])
    y += T["rule_h"] + 50
    fs = font(REG, 44)
    d.text((W / 2, y), sub, font=fs, fill="#C9D4F5", anchor="ma")
    return y + line_h(fs)


def place_shot_and_bullets(canvas, shot, head_bottom, max_w=1520, **paper_kw):
    """Balance screenshot + bullet block in the space between head and band."""
    room = (BAND_Y - 60) - (head_bottom + 40)
    nw, nh = fitted_size(shot, max_w, room - BULLETS_H - 120)
    ys = balance(head_bottom, BAND_Y - 46, [nh, BULLETS_H])
    x = (W - nw) // 2
    paste_paper(canvas, shot, (x, ys[0], x + nw, ys[0] + nh), **paper_kw)
    d = ImageDraw.Draw(canvas)
    two_column_bullets(d, BULLETS, ys[1], T, gap_y=BULLET_GAP)
    return ys


def hero_classic(path):
    c = base_canvas(T, glow_at=(1000, 900), glow_r=1200)
    corner_squares(ImageDraw.Draw(c), T["mint"])
    y = head_block(c, 214, TITLE, SUB)
    shot = Image.open(f"{SHOTS}/light-00-dashboard.png").convert("RGB")
    place_shot_and_bullets(c, shot, y)
    bottom_band(c, FOOT, T)
    c.save(path)


def hero_framed(path):
    c = base_canvas(T, glow_at=(1000, 820), glow_r=1080, glow_strength=0.9)
    d = ImageDraw.Draw(c)
    d.rectangle([71, 71, W - 72, BAND_Y - 40], outline=T["mint"], width=3)
    corner_squares(d, T["mint"])
    y = head_block(c, 226, TITLE, SUB, target_w=1560, rule_w=480)
    shot = Image.open(f"{SHOTS}/light-00-dashboard.png").convert("RGB")
    place_shot_and_bullets(c, shot, y, max_w=1420,
                           border=T["mint"], border_w=6)
    bottom_band(c, FOOT, T)
    c.save(path)


def hero_stacked(path):
    c = base_canvas(T, glow_at=(1000, 950), glow_r=1250)
    d = ImageDraw.Draw(c)
    corner_squares(d, T["mint"], colours=[T["mint"], T["second"], T["second"], T["mint"]])
    y = head_block(c, 210, TITLE, SUB)
    back = Image.open(f"{SHOTS}/light-07.png").convert("RGB")
    front = Image.open(f"{SHOTS}/light-00-dashboard.png").convert("RGB")
    nw, nh = fitted_size(front, 1400, 900)
    ys = balance(y, BAND_Y - 46, [nh + 70, BULLETS_H])
    x = (W - nw) // 2
    paste_paper(c, back, (x + 78, ys[0], x + nw + 78, ys[0] + nh),
                shadow_alpha=110, shadow_blur=28)
    paste_paper(c, front, (x - 78, ys[0] + 70, x + nw - 78, ys[0] + nh + 70))
    two_column_bullets(d, BULLETS, ys[1], T, gap_y=BULLET_GAP)
    bottom_band(c, FOOT, T)
    c.save(path)


def hero_panel(path):
    c = base_canvas(T, glow_at=(1000, 1300), glow_r=1150, glow_strength=0.75)
    d = ImageDraw.Draw(c)
    d.rectangle([0, 0, W, 640], fill=T["glow"])
    d.rectangle([0, 640, W, 646], fill=T["mint"])
    corner_squares(d, T["mint"])
    size = fit_size(d, TITLE, BLD, 1640)
    f = font(BLD, size)
    draw_tracked(d, W / 2, 214, TITLE, f, T["text"], tracking=size * 0.14)
    yy = 214 + line_h(f) + 34
    d.rectangle([W / 2 - 280, yy, W / 2 + 280, yy + T["rule_h"]], fill=T["mint"])
    fs = font(REG, 44)
    d.text((W / 2, yy + T["rule_h"] + 44), SUB, font=fs, fill="#C9D4F5", anchor="ma")

    shot = Image.open(f"{SHOTS}/light-00-dashboard.png").convert("RGB")
    nw, nh = fitted_size(shot, 1460, 800)
    chips_h = 2 * 96
    ys = balance(700, BAND_Y - 46, [nh, chips_h])
    x = (W - nw) // 2
    paste_paper(c, shot, (x, ys[0], x + nw, ys[0] + nh))

    fb = font(REG, 36)
    for i, txt in enumerate(BULLETS):
        col, row = i % 2, i // 2
        tw = d.textlength(txt, font=fb)
        cx = 250 if col == 0 else 1035
        cy = ys[1] + row * 96
        d.rounded_rectangle([cx, cy, cx + tw + 100, cy + 68], radius=34,
                            outline=T["mint"], width=3)
        d.rectangle([cx + 34, cy + 27, cx + 48, cy + 41], fill=T["mint"])
        d.text((cx + 68, cy + 34), txt, font=fb, fill=T["text"], anchor="lm")
    bottom_band(c, FOOT, T)
    c.save(path)


def hero_bigtype(path):
    c = base_canvas(T, glow_at=(1300, 1250), glow_r=1250)
    d = ImageDraw.Draw(c)
    corner_squares(d, T["mint"])
    y = 196
    for i, ln in enumerate(["EIGHT TABS", "BECAME TWO"]):
        size = fit_size(d, ln, BLD, 1560, lo=60, hi=230)
        f = font(BLD, size)
        draw_tracked(d, W / 2, y, ln, f, T["text"] if i == 0 else T["mint"],
                     tracking=size * 0.12)
        y += line_h(f) - 12
    y += 40
    d.rectangle([W / 2 - 280, y, W / 2 + 280, y + T["rule_h"]], fill=T["second"])
    y += T["rule_h"] + 46
    fs = font(REG, 44)
    d.text((W / 2, y), SUB, font=fs, fill="#C9D4F5", anchor="ma")
    y += line_h(fs)
    shot = Image.open(f"{SHOTS}/light-00-dashboard.png").convert("RGB")
    place_shot_and_bullets(c, shot, y, max_w=1340)
    bottom_band(c, FOOT, T)
    c.save(path)


if __name__ == "__main__":
    out = pathlib.Path("hero-options")
    out.mkdir(exist_ok=True)
    hero_classic(out / "hero_1_classic.png")
    hero_framed(out / "hero_2_framed.png")
    hero_stacked(out / "hero_3_stacked.png")
    hero_panel(out / "hero_4_panel.png")
    hero_bigtype(out / "hero_5_bigtype.png")
    print("done")
