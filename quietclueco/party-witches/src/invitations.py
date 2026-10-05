"""Invitations for Murder at the Lantern Supper.

    invitation_fillable_5x7.pdf            the party invitation; type the details into the form fields
    character_invitations_fillable_5x7.pdf one per role: who you play, what to wear (fillable details)
    phone/                                 1080 x 1920 PNGs to text: the invitation and one per role

The art is the same code-drawn poster scene as the covers; no faces, no AI images.
"""
import os, zipfile
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from PIL import Image, ImageDraw
import case as C
import render as R

INCH = 72
PAGE = (5 * INCH, 7 * INCH)

def header_art(path, W, H):
    """The hall on its hill under the moon, cropped to a banner (made once by build.py)."""
    return path

def fillable(c, name, x, y, w, h=16, size=10):
    c.acroForm.textfield(name=name, x=x, y=y, width=w, height=h, fontName="Helvetica", fontSize=size,
                         borderWidth=0, fillColor=HexColor("#FBF8F1"), textColor=HexColor("#2B1B3D"), forceBorder=False)

def invitation_page(c, art, title_lines, body, fields, footer, key):
    W, H = PAGE
    c.setFillColor(R.PLUM); c.rect(0, 0, W, H, fill=1, stroke=0)
    c.drawImage(art, 0, H * 0.46, W, H * 0.54)
    c.setFillColor(R.PARCH); c.roundRect(14, 14, W - 28, H * 0.5, 10, fill=1, stroke=0)
    c.setStrokeColor(R.GOLD); c.setLineWidth(1.2); c.roundRect(19, 19, W - 38, H * 0.5 - 10, 8, fill=0, stroke=1)
    y = H * 0.5 - 6
    for i, (t, font, size, col) in enumerate(title_lines):
        c.setFillColor(col); c.setFont(font, size); c.drawCentredString(W / 2, y - size, t); y -= size + 5
    st = R.ParagraphStyle("inv", fontName="Nunito", fontSize=8.8, leading=11.6, textColor=R.INK, alignment=1)
    y = R.para(c, R.esc(body), 34, y - 2, W - 68, st)
    for label, fname in fields:
        c.setFillColor(R.AUB); c.setFont("Nunito-ExtraBold", 7.5); c.drawString(34, y - 11, label.upper())
        lw = c.stringWidth(label.upper(), "Nunito-ExtraBold", 7.5) + 6
        c.setStrokeColor(R.RULE); c.line(34 + lw, y - 12, W - 34, y - 12)
        fillable(c, f"{key}_{fname}", 34 + lw, y - 13, W - 68 - lw, 13, 9)
        y -= 19
    c.setFillColor(R.SOFT); c.setFont("Nunito-Italic", 7.5); c.drawCentredString(W / 2, 26, footer)

def build_pdfs(outdir, art):
    os.makedirs(outdir, exist_ok=True)
    p1 = os.path.join(outdir, f"{C.SLUG}_invitation_fillable_5x7.pdf")
    c = canvas.Canvas(p1, pagesize=PAGE); c.setTitle(f"{C.TITLE} — invitation")
    invitation_page(c, art, [("YOU ARE INVITED TO", "Nunito-ExtraBold", 9, R.AMETHYST),
                             ("The Lantern Supper", "Fraunces-Bold", 22, R.PLUM),
                             ("at Larkwell Hall · a murder mystery party", "Fraunces-Italic", 10, R.AUB)],
                    "Lanterns, soup and cider by the fire, a midnight carol, and a murder to solve before the bell "
                    "rings. Come in costume. Bring your best alibi.",
                    [("For", "guest"), ("Date", "date"), ("Time", "time"), ("Place", "place"), ("RSVP to", "rsvp")],
                    "Your character and costume will follow. · Murder at the Lantern Supper", "inv")
    c.showPage(); c.save()
    p2 = os.path.join(outdir, f"{C.SLUG}_character_invitations_fillable_5x7.pdf")
    c = canvas.Canvas(p2, pagesize=PAGE); c.setTitle(f"{C.TITLE} — character invitations")
    for k in C.CORE + C.ADD_ORDER:
        nm, role, core, costume, colour, hook = C.PEOPLE[k]
        invitation_page(c, art, [("AT THE LANTERN SUPPER YOU WILL PLAY", "Nunito-ExtraBold", 7.6, R.AMETHYST),
                                 (nm, "Fraunces-Bold", 19 if len(nm) < 18 else 16, R.PLUM),
                                 (role[:58], "Fraunces-Italic", 8.6, R.AUB)],
                        f"{hook} Costume: {costume}. Your lantern candle is {colour}: bring something {colour} "
                        f"if you like. Everything else will be waiting in your envelope.",
                        [("Date", "date"), ("Time", "time"), ("Place", "place")],
                        "Murder at the Lantern Supper · a Morrowmere murder mystery party", k)
        c.showPage()
    c.save()
    return [p1, p2]

def phone_png(path, art_img, lines):
    W, H = 1080, 1920
    im = Image.new("RGB", (W, H), (0x2B, 0x1B, 0x3D))
    a = art_img.resize((W, int(W * art_img.height / art_img.width)))
    im.paste(a, (0, 0))
    d = ImageDraw.Draw(im)
    y0 = a.height - 40
    d.rounded_rectangle([50, y0, W - 50, H - 60], radius=30, fill=(0xED, 0xE6, 0xD6))
    d.rounded_rectangle([64, y0 + 14, W - 64, H - 74], radius=24, outline=(0xE3, 0xA6, 0x4B), width=4)
    from PIL import ImageFont
    def fitted(text, fnt):
        while fnt.getlength(text) > W - 220 and fnt.size > 20:
            fnt = ImageFont.truetype(fnt.path, fnt.size - 4)
        return fnt
    rows = []
    for text, fnt, col in lines:
        if text == "LINES":
            rows.append(("LINES", fnt, col, 3 * (fnt.size + 70)))
        else:
            fnt = fitted(text, fnt); rows.append((text, fnt, col, fnt.size + 34))
    total = sum(r[3] for r in rows)
    y = y0 + 14 + (H - 74 - y0 - 14 - total) / 2
    for text, fnt, col, h in rows:
        if text == "LINES":
            for lab in ("Date", "Time", "Place"):
                d.text((140, y), lab.upper(), font=fnt, fill=col)
                d.line([(140 + fnt.getlength(lab.upper()) + 20, y + fnt.size), (W - 140, y + fnt.size)], fill=(0xC9, 0xBE, 0xAA), width=3)
                y += fnt.size + 70
            continue
        w = fnt.getlength(text)
        d.text(((W - w) / 2, y), text, font=fnt, fill=col)
        y += h
    im.save(path, optimize=True)
    return path
