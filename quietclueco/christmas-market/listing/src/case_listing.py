"""Case-specific settings for the listing kit: Snowfall at Ember Square.
For a new case, copy this file and change the paths, the page finders and the words."""
import json, os, re, sys
import kit

HERE = os.path.dirname(os.path.abspath(__file__))
CASE = os.path.abspath(os.path.join(HERE, "..", ".."))        # quietclueco/christmas-market
SLUG = "snowfall-at-ember-square"
sys.path.insert(0, os.path.join(CASE, "src"))
import case as C          # noqa: E402  (story, clues)
import hints as H         # noqa: E402

kit.set_font_dir(os.path.join(CASE, "src", "fonts"))

PDF = {
    "letter": os.path.join(CASE, "print", f"{SLUG}_print-US-Letter.pdf"),
    "a4": os.path.join(CASE, "print", f"{SLUG}_print-A4.pdf"),
    "ipad": os.path.join(CASE, "ipad", f"{SLUG}_iPad.pdf"),
}
SOLUTION = {k: os.path.join(CASE, "solution", f"{SLUG}_SOLUTION_{t}.pdf")
            for k, t in (("letter", "print-US-Letter"), ("a4", "print-A4"), ("ipad", "iPad"))}

# ---------------------------------------------------------------- words on the visuals
WORDS = dict(
    title="Snowfall at\nEmber Square",
    hook="Find the\nkiller",
    promise=["6,000 suspects", "6 documents", "1 killer"],
    badges=["PRINTABLE", "iPad"],
    brand=C.BRAND,
    players=C.PLAYERS, time=C.PLAYTIME,
)

# ---------------------------------------------------------------- spoiler list
def forbidden():
    rep = json.load(open(os.path.join(CASE, "verification_report.json")))
    K = rep["answer"]
    f = {"killer first name": K["first"], "killer surname": K["last"],
         "killer ticket": f"{K['ticket']:04d}", "Sealed Check number": rep["seal"],
         "solution heading": "What really happened", "solution index": "Elimination index",
         "solution table": "Ruled out by"}
    for x in rep["finalists"]:
        if x["clue"] == "KILLER":
            continue
        f[f"finalist {x['name']}"] = x["name"]
        f[f"finalist ticket {x['name']}"] = f"{x['ticket']:04d}"
    for cid, hs in H.HINTS.items():
        for lv in (1, 2):   # level 2 and level 3 (0-based 1, 2)
            chunk = " ".join(hs[lv].split())[:48]
            f[f"hint {cid} level {lv + 1}"] = chunk
    return f

# ---------------------------------------------------------------- pages
def pages():
    L = kit.Pdf(PDF["letter"]); I = kit.Pdf(PDF["ipad"])
    p = dict(
        cover=0,
        howto=L.find("How to play", "What you need"),
        case=L.find("The case", "What we know for certain"),
        rules=L.find("House rules", "Double letter"),
        map=L.find("EVIDENCE 1", "Market map", "River Ember"),
        directory=L.find("Stall directory", "From the market programme"),
        receipt=L.find("The receipt", "MERRY CHRISTMAS"),
        weather=L.find("Weather log", "EMBERFIELD WEATHER STATION"),
        coach=L.find("Coach timetable", "Ember Valley Coaches"),
        statements=L.find("Witness statements", "WITNESS STATEMENT"),
        notebook=L.find("work these out from the documents"),
        logintro=L.find("TICKET OFFICE EXPORT"),
        hint1=L.find("A gentle nudge", "Evidence A"),
        check=L.find("The Sealed Check", "Ticket number"),
    )
    ip = dict(map=I.find("EVIDENCE 1", "Market map", "River Ember"),
              notebook=I.find("work these out from the documents"),
              cover=0)
    return L, I, p, ip

def clean_log_pages(pdf, bad):
    """Visitor Log pages whose whole text contains none of the forbidden tokens."""
    out = []
    for i, page in enumerate(pdf.doc):
        t = " ".join(page.get_text().split())
        if "FIRST NAME" in t and "LAST STALL" in t and not any(tok in t for tok in bad.values()):
            out.append(i)
    return out

def log_rows(pdf, index):
    """(y_top, y_bottom, x0, x1, entry 'HH:MM', last stall) for every visitor row on a log page, in PDF points."""
    lines = {}
    for w in pdf.words(index):
        lines.setdefault(round(w[3], 1), []).append(w)
    rows = []
    for y, ws in sorted(lines.items()):
        ws.sort(key=lambda w: w[0])
        if re.fullmatch(r"\d\d:\d\d", ws[0][4]) and len(ws) >= 7:
            stall = next((w[4] for w in reversed(ws) if w[4].isdigit() and len(w[4]) <= 2), "0")
            rows.append((min(w[1] for w in ws), max(w[3] for w in ws), ws[0][0], ws[-1][2], ws[0][4], int(stall)))
    return rows

def notebook_marks(pdf, index):
    """Positions (x, y centre) of the clue numbers '1.'..'12.' and 'A.'..'F.' on the notebook page."""
    marks = {}
    for w in pdf.words(index):
        m = re.fullmatch(r"(\d{1,2}|[A-F])\.", w[4])
        if m and w[0] < 110:
            marks[m.group(1)] = ((w[0] + w[2]) / 2, (w[1] + w[3]) / 2, w[3] - w[1])
    return marks

def text_rect(pdf, index, needle):
    r = pdf.doc[index].search_for(needle)
    return r[0] if r else None
