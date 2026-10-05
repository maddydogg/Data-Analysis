"""Settings for the listing kit of Murder at the Lantern Supper: paths, page lookup and the spoiler list."""
import os, sys
import kit

HERE = os.path.dirname(os.path.abspath(__file__))
CASE = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(CASE, "src"))
import case as C            # noqa: E402
import verify as VER        # noqa: E402
kit.set_font_dir(os.path.join(CASE, "src", "fonts"))
SLUG = C.SLUG
PDF = {"player": os.path.join(CASE, "print", f"{SLUG}_PLAYER-KIT_US-Letter.pdf"),
       "host": os.path.join(CASE, "print", f"{SLUG}_HOST-GUIDE_US-Letter.pdf"),
       "player_a4": os.path.join(CASE, "print", f"{SLUG}_PLAYER-KIT_A4.pdf"),
       "host_a4": os.path.join(CASE, "print", f"{SLUG}_HOST-GUIDE_A4.pdf")}
INV = os.path.join(CASE, "invitations")

def forbidden():
    """Everything a buyer must not be able to read in a listing image or video frame: the solution, every
    secret, every Round 2 and Round 3 booklet line and evidence card, the sealed pages."""
    f = {}
    for i, t in enumerate(VER.spoiler_tokens()):
        f[f"solution {i}"] = " ".join(t.split())[:60]
    for k, b in C.B.items():
        f[f"secret of {k}"] = " ".join(b["secret"].split())[:50]
        for r in (1, 2, 3):
            for j, (t, _) in enumerate(b["rounds"][r - 1]):
                f[f"{k} round {r} line {j + 1}"] = " ".join(t.split())[:50]
    for c in C.CARDS:
        if c["round"] >= 2:
            for j, t in enumerate(c["text"]):
                f[f"card {c['id']} line {j + 1}"] = " ".join(t.split())[:50]
    # Isadora's background is itself a Round 3 reveal (she is Rowena's daughter)
    f["isadora's background"] = " ".join(C.B["isadora"]["intro"][1].split())[:50]
    f["sealed page"] = "SEALED SOLUTION"
    f["timeline"] = "Character, time and place"
    return f

class Pages:
    def __init__(self):
        self.P = kit.Pdf(PDF["player"]); self.H = kit.Pdf(PDF["host"])

    def find(self, pdf, *needles):
        return pdf.find(*needles, exclude=("ZZZ_NEVER",))

    def booklet_top(self, key, height):
        """The 'Your character' page of a booklet, clipped above the secret."""
        idx = self.P.find(C.name(key), "YOUR CHARACTER")
        page = self.P.doc[idx]
        y = page.search_for("Your secret")[0].y0 - 10
        clip = (30, 30, page.rect.width - 30, y)
        return self.P.image(idx, int(height * (y - 30) / (page.rect.height - 60)), clip=clip)
