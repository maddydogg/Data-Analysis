"""Ten 2000x2000 listing images for Murder at the Lantern Supper, in the old horror-film release look
of case No. 3: 01 is the one-sheet poster, the lobby cards show real pages of the kit inside a framed
card with a caption, 09 and 10 are posters. Every page shown is a real PDF region; every word drawn
by code is recorded for the spoiler scan. Only spoiler-free pages are shown: booklet fronts clipped
above the secret, the Round 1 evidence cards, the open part of the host guide."""
import math, os
from PIL import Image, ImageDraw, ImageFont
import kit
from kit import font
import poster as P
import party_art as A
import party_listing as PL

S = 2000
CONTENT = (120, 236, 1880, 1566)
NAMES = ["01-party-poster", "02-everything-in-the-kit", "03-character-booklets", "04-invitations",
         "05-round-one-evidence", "06-host-guide-host-can-play", "07-potion-menu", "08-awards-and-badges",
         "09-how-the-evening-goes", "10-what-you-get"]
INK = (0x1E, 0x1A, 0x22)

def lobby(no, caption, sub):
    f = kit.Frame(S, S, P.PLUM); img = f.img
    P.gradient(img, P.NIGHT, P.AUB)
    P.halftone(img, (0, 0, S, S), P.AMETHYST + (34,), 30, falloff=lambda x, y: 0.55)
    d = f.draw()
    d.rectangle([56, 56, S - 56, S - 56], fill=P.MOON)
    d.rectangle([76, 76, S - 76, S - 76], outline=P.AUB, width=6)
    d.rectangle([90, 90, S - 90, S - 90], outline=P.GOLD, width=3)
    for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        P.star(d, (90 if sx > 0 else S - 90) + sx * 34, (90 if sy > 0 else S - 90) + sy * 34, 14, P.GOLD)
    P.tracked(f, S / 2, 128, "MURDER AT THE LANTERN SUPPER", P.hf("cinzel", 48, 800), P.AUB, 9)
    f.text((150, 142), "QUIETCLUECO", P.hf("oswald", 30, 500), P.AMETHYST)
    f.text((S - 150, 142), f"LOBBY CARD No. {no}", P.hf("oswald", 30, 500), P.AMETHYST, anchor="ra")
    x0, y0, x1, y1 = CONTENT
    P.gradient(img, P.AUB, P.PLUM, CONTENT)
    P.halftone(img, CONTENT, P.AMETHYST + (70,), 26,
               falloff=lambda x, y: max(0.1, 1 - math.hypot(x - (x0 + x1) / 2, y - (y0 + y1) / 2) / 1100))
    d = f.draw()
    d.rectangle(CONTENT, outline=P.NIGHT, width=4)
    d.rectangle([120, 1592, 1880, 1880], fill=P.PLUM)
    d.rectangle([132, 1604, 1868, 1868], outline=P.GOLD, width=3)
    cap = P.fit(caption, "abril", 118, 1640)
    f.text((S / 2, 1632), caption, cap, P.GOLD, anchor="ma")
    f.text((S / 2, 1790), sub, P.fit(sub, "oswald", 50, 1640, 500), P.MOON, anchor="ma")
    return f

def note_card(f, text, cx, cy, angle, w=520, h=300, size=62):
    note = kit.Frame(w, h, (250, 232, 176))
    note.text((w / 2, h * 0.2), text, font("hand", size), INK, anchor="ma", align="center")
    f.paste(note.img, cx, cy, angle=angle)
    f.sources += note.sources

def png_in_phone(f, path, cx, cy, h, angle=0):
    im = Image.open(path).convert("RGBA")
    w = int(h * im.width / im.height)
    im = im.resize((w, h), Image.LANCZOS)
    pad = int(h * 0.035)
    body = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    ImageDraw.Draw(body).rounded_rectangle([0, 0, body.width - 1, body.height - 1], radius=pad * 2.2, fill=(22, 18, 26, 255))
    body.alpha_composite(im, (pad, pad))
    f.paste(body, cx, cy, angle=angle)
    f.note("png", os.path.basename(path), PHONE_TEXT.get(os.path.basename(path), ""))

PHONE_TEXT = {}

# ---------------------------------------------------------------- the ten images
def m01(G):
    return A.hero_poster()

def m02(G):
    f = lobby(2, "Everything for the party", "Host guide · 12 booklets · 11 evidence cards · invitations · badges · menu · awards")
    host = G.H.image(0, 620); player = G.P.image(0, 620)
    f.paste_page(host, 420, 640, angle=-6); f.paste_page(player, 760, 660, angle=4)
    f.paste_page(G.P.image(G.P.find("THE LANTERN SUPPER · LARKWELL HALL", "Cordelia Heatherly"), 560), 1180, 640, angle=-3)
    f.paste_page(G.P.image(G.P.find("The Potion Menu"), 560), 1560, 660, angle=5)
    f.paste_page(G.booklet_top("cordelia", 560), 470, 1220, angle=3)
    f.paste_page(G.P.image(G.P.find("ROUND 1 · CARD 1"), 600), 900, 1200, angle=-4)
    f.paste_page(G.P.image(G.P.find("My accusation"), 560), 1300, 1210, angle=3)
    f.paste_page(G.P.image(G.P.find("Best Detective"), 540), 1660, 1200, angle=-4)
    return f

def m03(G):
    f = lobby(3, "12 characters, no acting required", "6 core roles + up to 6 extra · every booklet: who you are, what to wear, what to say each round")
    for k, (cx, cy, ang) in zip(["cordelia", "marigold", "rufus", "clementine"],
                                [(440, 760, -5), (1000, 720, 3), (1560, 760, -3), (1000, 1260, 2)]):
        pg = G.booklet_top(k, 980)
        f.paste_page(pg, cx, cy, angle=ang)
    note_card(f, "Secrets stay\nin the booklet!", 420, 1330, -8, 500, 260, 60)
    note_card(f, "Each round on\nits own page", 1590, 1330, 6, 500, 260, 60)
    return f

def m04(G):
    f = lobby(4, "Invitations for every guest", "Fillable invitation · 12 character invitations · phone versions to text")
    inv = kit.Pdf(os.path.join(PL.INV, f"{PL.SLUG}_invitation_fillable_5x7.pdf"))
    chi = kit.Pdf(os.path.join(PL.INV, f"{PL.SLUG}_character_invitations_fillable_5x7.pdf"))
    f.paste_page(inv.image(0, 940), 440, 880, angle=-5)
    f.paste_page(chi.image(0, 900), 880, 920, angle=3)
    png_in_phone(f, os.path.join(PL.INV, "phone", "00_invitation.png"), 1320, 880, 1000, angle=-4)
    png_in_phone(f, os.path.join(PL.INV, "phone", "03_silas.png"), 1660, 930, 940, angle=5)
    return f

def m05(G):
    f = lobby(5, "Evidence cards, round by round", "11 cards in 3 rounds · shown here: Round 1 only")
    a = G.P.image(G.P.find("ROUND 1 · CARD 1"), 1260); b = G.P.image(G.P.find("ROUND 1 · CARD 3"), 1260)
    f.paste_page(a, 640, 900, angle=-4); f.paste_page(b, 1360, 910, angle=4)
    return f

def m06(G):
    f = lobby(6, "A host guide that lets you play too", "Casting for 6–12 guests · scripts for every round · solution sealed at the back")
    f.paste_page(G.H.image(G.H.find("Welcome to the Lantern Supper"), 1060), 470, 900, angle=-5)
    f.paste_page(G.H.image(G.H.find("Casting", "CHOOSE ROLES"), 1060), 1000, 880, angle=2)
    f.paste_page(G.H.image(G.H.find("Prologue", "Round 1"), 1060), 1530, 900, angle=-3)
    note_card(f, "No spoilers until\nthe sealed section", 1520, 1400, 5, 560, 250, 58)
    return f

def m07(G):
    f = lobby(7, "Potions, with or without a spell", "4 drinks · each with an alcohol-free version")
    f.paste_page(G.P.image(G.P.find("The Potion Menu"), 1240), 760, 900, angle=-3)
    A.green_glass(f.img, 1470, 1060, 180)
    from party_art import lantern
    lantern(f.img, 1640, 760, 70)
    return f

def m08(G):
    f = lobby(8, "Name badges and awards", "13 badges (one for the host) · Best Detective · Best Costume · and two more")
    f.paste_page(G.P.image(G.P.find("THE LANTERN SUPPER · LARKWELL HALL", "Cordelia Heatherly"), 1220), 560, 900, angle=-4)
    f.paste_page(G.P.image(G.P.find("Best Detective"), 1180), 1260, 880, angle=3)
    return f

def m09(G):
    f = kit.Frame(S, S, P.PLUM); img = f.img
    P.gradient(img, P.NIGHT, P.AUB)
    P.halftone(img, (0, 0, S, S), P.AMETHYST + (40,), 30, falloff=lambda x, y: 0.6)
    P.tracked(f, S / 2, 92, "QUIETCLUECO PRESENTS", P.hf("cinzel", 46, 700), P.MOON, 12)
    P.title_word(f, "How the evening goes", S / 2, 160, P.fit("How the evening goes", "abril", 170, S - 240), depth=14, k=1.3)
    steps = [("ARRIVE", "Potions, badges, a booklet in an envelope", "15 min"),
             ("PROLOGUE", "The host reads how Rowena was found", "5 min"),
             ("ROUND 1", "Who you are, where you were · cards 1–4", "35 min"),
             ("ROUND 2", "Secrets come out · cards 5–8", "35 min"),
             ("ROUND 3", "The last evidence · cards 9–11", "25 min"),
             ("ACCUSE", "Everyone writes who did it, and why", "10 min"),
             ("REVEAL", "The sealed solution, then the awards", "10 min")]
    y = 470; d = f.draw()
    for i, (head, text, dur) in enumerate(steps):
        cy = y + i * 196
        d.ellipse([170, cy - 70, 310, cy + 70], fill=P.GOLD)
        f.text((240, cy), str(i), P.hf("abril", 92), P.PLUM, anchor="mm")
        if i < len(steps) - 1:
            d.line([(240, cy + 72), (240, cy + 124)], fill=P.GOLD, width=6)
        f.text((370, cy - 64), head, P.hf("bebas", 92), P.MOON)
        f.text((370, cy + 20), text, P.fit(text, "oswald", 52, 1240, 400), P.MOON)
        f.text((S - 180, cy - 40), dur, P.hf("bebas", 76), P.GOLD, anchor="ra")
    P.tracked(f, S / 2, S - 140, "2–3 HOURS · 6–12 PLAYERS · THE HOST CAN PLAY", P.hf("cinzel", 44, 700), P.GOLD, 6)
    P.deco_frame(f, 36, 1.5)
    P.aged(img, 9, border=24)
    return f

def m10(G):
    f = kit.Frame(S, S, P.PLUM); img = f.img
    P.gradient(img, P.NIGHT, P.AUB)
    P.halftone(img, (0, 0, S, S), P.AMETHYST + (40,), 30, falloff=lambda x, y: 0.6)
    P.tracked(f, S / 2, 92, "QUIETCLUECO PRESENTS", P.hf("cinzel", 46, 700), P.MOON, 12)
    P.title_word(f, "What you get", S / 2, 160, P.hf("abril", 190), depth=16, k=1.4)
    lab = font("black", 44); bf = font("black", 30)
    cards = [("Host guide", "Letter", G.H.image(0, 480)), ("Host guide", "A4", kit.Pdf(PL.PDF["host_a4"]).image(0, 480)),
             ("Player kit", "Letter", G.P.image(0, 480)), ("Player kit", "A4", kit.Pdf(PL.PDF["player_a4"]).image(0, 480))]
    x = 90
    for label, fmt, thumb in cards:
        kit.pdf_file_card(f, (x, 470, x + 340, 960), thumb, f"{label}", lab, fmt, bf)
        x += 372
    kit.pdf_file_card(f, (x, 470, x + 340, 960), None, "Invitations", lab, "ZIP", bf)
    d = f.draw(); zx = x + 170
    d.rounded_rectangle([zx - 100, 560, zx + 100, 760], radius=20, fill=P.AUB)
    f.text((zx, 610), "ZIP", P.hf("abril", 96), P.GOLD, anchor="ma")
    items = ["6–12 players: 6 core roles, up to 6 extra",
             "2–3 hours, 3 rounds, no acting required",
             "The host can play: solution sealed at the back",
             "Print at home in US Letter or A4",
             "Spooky, not gory · teens and adults"]
    y = 1080
    for it in items:
        d.ellipse([140, y + 14, 172, y + 46], fill=P.GOLD)
        f.text((200, y), it, P.fit(it, "oswald", 60, 1040, 500), P.MOON); y += 108
    cx, cy, r = 1560, 1380, 300
    d = f.draw()
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=P.GOLD)
    d.ellipse([cx - r + 20, cy - r + 20, cx + r - 20, cy + r - 20], outline=P.PLUM, width=8)
    f.text((cx, cy - 170), "Exactly\none answer", P.hf("abril", 88), P.PLUM, anchor="ma", align="center")
    f.text((cx, cy + 70), "checked by code", P.hf("oswald", 54, 600), P.PLUM, anchor="ma")
    kit.tick(f, cx - 44, cy + 210, 88, P.PLUM, 12)
    P.deco_frame(f, 36, 1.5)
    P.aged(img, 7, border=24)
    return f

BUILDERS = [m01, m02, m03, m04, m05, m06, m07, m08, m09, m10]

def phone_texts():
    import case as C
    PHONE_TEXT["00_invitation.png"] = "YOU ARE INVITED TO The Lantern Supper a murder mystery party at Larkwell Hall"
    for i, k in enumerate(C.CORE + C.ADD_ORDER, 1):
        PHONE_TEXT[f"{i:02d}_{k}.png"] = f"AT THE LANTERN SUPPER YOU WILL PLAY {C.name(k)} {C.PEOPLE[k][1]} Costume: {C.PEOPLE[k][3]}"

def build(outdir, only=None):
    os.makedirs(outdir, exist_ok=True)
    phone_texts()
    G = PL.Pages(); bad = PL.forbidden(); res = []
    for i, (name, fn) in enumerate(zip(NAMES, BUILDERS), 1):
        if only and i not in only:
            continue
        f = fn(G)
        path = os.path.join(outdir, f"{PL.SLUG}_{name}.jpg")
        f.img.convert("RGB").save(path, quality=90, optimize=True, progressive=True)
        res.append(dict(name=name, path=path, sources=f.sources, hits=kit.spoiler_scan(f.sources, bad)))
        print(name, len(f.sources), "sources", len(res[-1]["hits"]), "hits")
    if not only:
        sheet = Image.new("RGB", (5 * 400, 2 * 400))
        for k, r in enumerate(res):
            sheet.paste(Image.open(r["path"]).resize((400, 400)), ((k % 5) * 400, (k // 5) * 400))
        sheet.save(os.path.join(outdir, f"{PL.SLUG}_overview.jpg"), quality=85)
    return res, G, bad

if __name__ == "__main__":
    import sys
    build(os.path.join(PL.CASE, "listing", "mockups"), only=[int(x) for x in sys.argv[1:]] or None)
