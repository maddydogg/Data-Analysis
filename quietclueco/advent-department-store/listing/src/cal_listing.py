"""Settings for the listing kit: The Windows at Quillon's (advent calendar)."""
import json, os, re, sys
import kit

HERE = os.path.dirname(os.path.abspath(__file__))
CASE = os.path.abspath(os.path.join(HERE, "..", ".."))        # quietclueco/advent-department-store
SLUG = "the-windows-at-quillons"
sys.path.insert(0, os.path.join(CASE, "src"))
import case as C          # noqa: E402
import hints as H         # noqa: E402
import art                # noqa: E402
import cover as COVER     # noqa: E402

kit.set_font_dir(os.path.join(CASE, "src", "fonts"))

PDF = {"letter": os.path.join(CASE, "print", f"{SLUG}_print-US-Letter.pdf"),
       "a4": os.path.join(CASE, "print", f"{SLUG}_print-A4.pdf"),
       "ipad": os.path.join(CASE, "ipad", f"{SLUG}_iPad.pdf")}
SOLUTION = {k: os.path.join(CASE, "solution", f"{SLUG}_SOLUTION_{t}.pdf")
            for k, t in (("letter", "print-US-Letter"), ("a4", "print-A4"), ("ipad", "iPad"))}
EARLY = (1, 2, 3)          # the only windows the listing may show

def forbidden():
    rep = json.load(open(os.path.join(CASE, "verification_report.json")))
    K = rep["answer"]
    f = {"killer first name": K["first"], "killer surname": K["last"],
         "killer pass": f"{K['ticket']:04d}", "Sealed Check number": rep["seal"],
         "solution heading": "What really happened", "solution index": "Elimination index",
         "solution table": "Ruled out by"}
    for x in rep["finalists"]:
        if x["clue"] == "KILLER":
            continue
        f[f"finalist {x['name']}"] = x["name"]
        f[f"finalist pass {x['name']}"] = f"{x['ticket']:04d}"
    for cid, hs in H.HINTS.items():
        for lv in (1, 2):
            f[f"hint {cid} level {lv + 1}"] = " ".join(hs[lv].split())[:48]
    for c in C.CLUES:                       # nothing from windows 4-23 may appear in the listing
        if c["day"] > 3:
            f[f"window {c['day']} evidence"] = " ".join(C.DOCS[c["day"]]["statement"][1].split())[:48]
            f[f"window {c['day']} question"] = c["note"]
    return f

def pages():
    L = kit.Pdf(PDF["letter"]); I = kit.Pdf(PDF["ipad"])
    p = dict(cover=0,
             howto=L.find("How to play", "What this is"),
             calendar=L.find("Your advent calendar", "Tick off each window"),
             envelope=L.find("ENVELOPE TEMPLATE"),
             labels=L.find("DAY NUMBERS 1"),
             w1=L.find("WINDOW 1 OF 24"), w1letter=L.find("Teodor’s letter"), w1plan=L.find("The store plan"),
             w2=L.find("WINDOW 2 OF 24", "Chapters"), w3=L.find("WINDOW 3 OF 24"),
             rules=L.find("House rules", "Double letter"),
             hint1=L.find("A gentle nudge", "Window 3"))
    ip = dict(calendar=I.find("TAP TODAY’S WINDOW"), w1=I.find("WINDOW 1 OF 24"), w3=I.find("WINDOW 3 OF 24"))
    return L, I, p, ip

def clean_log_pages(pdf, bad):
    out = []
    for i, page in enumerate(pdf.doc):
        t = " ".join(page.get_text().split())
        if "LANTERN REGISTER" in t and "HOME DISTRICT" in t and not any(tok in t for tok in bad.values()):
            out.append(i)
    return out

def log_rows(pdf, index):
    lines = {}
    for w in pdf.words(index):
        lines.setdefault(round(w[3], 1), []).append(w)
    rows = []
    for y, ws in sorted(lines.items()):
        ws.sort(key=lambda w: w[0])
        if re.fullmatch(r"\d\d:\d\d", ws[0][4]) and len(ws) >= 7:
            rows.append((min(w[1] for w in ws), max(w[3] for w in ws), ws[0][0], ws[-1][2], ws[0][4]))
    return rows
