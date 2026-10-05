"""One command builds the whole party kit:  python3 build.py

checks -> poster art -> host guides and player kits (Letter, A4) -> invitations -> PDF checks -> report
-> delivery/ (the 5 files for Etsy) -> page previews.
"""
import os, sys, shutil, zipfile
from PIL import Image, ImageFont
import case as C
import verify, render, invitations

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
LISTING_SRC = os.path.join(OUT, "listing", "src")
sys.path.insert(0, LISTING_SRC)
import kit                     # noqa: E402
kit.set_font_dir(os.path.join(HERE, "fonts"))
import party_art               # noqa: E402

def make_art():
    os.makedirs(render.ART, exist_ok=True)
    for fmt, (w, h) in {"letter": (1275, 1650), "a4": (1240, 1754)}.items():
        party_art.cover_poster(w, h).img.convert("RGB").save(os.path.join(render.ART, f"cover_{fmt}.jpg"), quality=88)
    f = kit.Frame(1000, 760, party_art.PLUM)
    party_art.hall_scene(f, 0.9, (680, 210), 150, 560, (500, 540), 64)
    f.img.convert("RGB").save(os.path.join(render.ART, "invite_banner.jpg"), quality=90)
    return os.path.join(render.ART, "invite_banner.jpg")

def phone_invites(outdir, banner):
    os.makedirs(outdir, exist_ok=True)
    art = Image.open(banner)
    FH = os.path.join(LISTING_SRC, "fonts_horror")
    def f(name, size, w=None):
        fn = ImageFont.truetype(os.path.join(FH if name in ("BebasNeue-Regular.ttf", "Cinzel[wght].ttf") else os.path.join(HERE, "fonts"), name), size)
        if w:
            fn.set_variation_by_axes([w])
        return fn
    PLUM, AUB, AM, INK = (0x2B, 0x1B, 0x3D), (0x4A, 0x2C, 0x5E), (0x8E, 0x5B, 0xB5), (0x1E, 0x1A, 0x22)
    paths = [invitations.phone_png(os.path.join(outdir, "00_invitation.png"), art, [
        ("YOU ARE INVITED TO", f("Nunito-ExtraBold.ttf", 40), AM), ("The Lantern Supper", f("Fraunces-Bold.ttf", 96), PLUM),
        ("a murder mystery party at Larkwell Hall", f("Fraunces-Italic.ttf", 46), AUB),
        ("Come in costume. Bring your best alibi.", f("Nunito-Regular.ttf", 40), INK), ("LINES", f("Nunito-ExtraBold.ttf", 40), AUB)])]
    for i, k in enumerate(C.CORE + C.ADD_ORDER, 1):
        nm, role, core, costume, colour, hook = C.PEOPLE[k]
        words, lines, cur = role.split(), [], ""
        for w in words:
            if len(cur) + len(w) > 34:
                lines.append(cur); cur = w
            else:
                cur = (cur + " " + w).strip()
        lines.append(cur)
        rows = [("AT THE LANTERN SUPPER YOU WILL PLAY", f("Nunito-ExtraBold.ttf", 34), AM),
                (nm, f("Fraunces-Bold.ttf", 84 if len(nm) < 16 else 70), PLUM)]
        rows += [(ln, f("Fraunces-Italic.ttf", 44), AUB) for ln in lines]
        rows += [(f"Costume: {costume}", f("Nunito-Bold.ttf", 44), INK), (f"Your candle: {colour}", f("Nunito-Regular.ttf", 40), INK),
                 ("LINES", f("Nunito-ExtraBold.ttf", 38), AUB)]
        paths.append(invitations.phone_png(os.path.join(outdir, f"{i:02d}_{k}.png"), art, rows))
    return paths

def main():
    rep = verify.check_all()
    render.register_fonts()
    banner = make_art()
    paths = {}
    for fmt, tag in (("letter", "US-Letter"), ("a4", "A4")):
        pk = os.path.join(OUT, "print", f"{C.SLUG}_PLAYER-KIT_{tag}.pdf"); os.makedirs(os.path.dirname(pk), exist_ok=True)
        d = render.build_player(fmt, pk); paths[f"player_{fmt}"] = pk
        hg = os.path.join(OUT, "print", f"{C.SLUG}_HOST-GUIDE_{tag}.pdf")
        render.build_host(fmt, hg, d.marks); paths[f"host_{fmt}"] = hg
    inv_dir = os.path.join(OUT, "invitations"); shutil.rmtree(inv_dir, ignore_errors=True)
    inv = invitations.build_pdfs(inv_dir, banner) + phone_invites(os.path.join(inv_dir, "phone"), banner)
    open(os.path.join(inv_dir, "README.txt"), "w").write(
        "Murder at the Lantern Supper - invitations\n\n"
        "invitation_fillable_5x7.pdf: open in any PDF reader (Adobe Acrobat Reader, Preview, Edge), click a line and "
        "type the date, time, place and RSVP, then print at 5x7 in or send the PDF.\n"
        "character_invitations_fillable_5x7.pdf: one page per role. Send each guest the page for their role.\n"
        "phone/: the same invitations as PNG pictures to text or message. Add the date, time and place in your "
        "message (or write them on with any photo editor).\n")
    verify.check_pdfs(rep, paths)
    # delivery: 5 files
    dl = os.path.join(OUT, "delivery"); shutil.rmtree(dl, ignore_errors=True); os.makedirs(dl)
    for p in paths.values():
        shutil.copyfile(p, os.path.join(dl, os.path.basename(p)))
    z = os.path.join(dl, f"{C.SLUG}_INVITATIONS.zip")
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(inv_dir):
            for fn in sorted(files):
                full = os.path.join(root, fn); zf.write(full, arcname=os.path.relpath(full, inv_dir))
    names = sorted(os.listdir(dl))
    rep["checks"].append(dict(name="Delivery: 5 files (the Etsy limit), each under 20 MB", passed=len(names) == 5 and all(
        os.path.getsize(os.path.join(dl, n)) < 20 * 2 ** 20 for n in names),
        detail=", ".join(f"{n} {os.path.getsize(os.path.join(dl, n)) / 2 ** 20:.1f} MB" for n in names)))
    with zipfile.ZipFile(z) as zf:
        inside = zf.namelist()
    rep["checks"].append(dict(name="Invitations ZIP: 2 fillable PDFs, 13 phone pictures and a README, intact",
                              passed=len([n for n in inside if n.endswith(".pdf")]) == 2 and
                              len([n for n in inside if n.endswith(".png")]) == 13 and "README.txt" in inside,
                              detail=f"{len(inside)} files"))
    import pymupdf as fitz
    fields = sum(len(list(pg.widgets())) for pg in fitz.open(inv[0]))
    rep["checks"].append(dict(name="The invitation PDF has fillable fields", passed=fields >= 5, detail=f"{fields} fields"))
    passed, total = verify.write_report(rep, os.path.join(OUT, "verification_report.md"),
                                        os.path.join(OUT, "verification_report.json"))
    print(f"checks {passed}/{total}")
    for c in rep["checks"]:
        if not c["passed"]:
            print("FAIL", c["name"], "|", c["detail"][:300])
    # previews
    pv = os.path.join(OUT, "previews"); os.makedirs(pv, exist_ok=True)
    for key in ("player_letter", "host_letter"):
        doc = fitz.open(paths[key])
        for i in range(len(doc)):
            doc[i].get_pixmap(matrix=fitz.Matrix(0.6, 0.6)).save(os.path.join(pv, f"{key}_{i + 1:03d}.png"))
        print(key, len(doc), "pages")
    return passed == total

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
