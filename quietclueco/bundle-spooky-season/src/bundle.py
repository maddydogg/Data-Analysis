"""Storm & Moon Double Feature — shared settings for the QuietClueCo bundle of case No. 2
(Storm over Corvenmoor) and case No. 3 (Full Moon over Morrowmere).

No new puzzles here: the bundle reuses the two finished case books unchanged and adds a
double-feature cover and a programme-style contents page in front of them."""
import importlib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                         # quietclueco/bundle-spooky-season
QCC = os.path.dirname(ROOT)                          # quietclueco
FONTS = os.path.join(HERE, "fonts")
HORROR = os.path.join(ROOT, "listing", "src", "fonts_horror")

NAME = "Storm & Moon Double Feature"
SLUG = "storm-and-moon-double-feature"
BRAND = "QuietClueCo"
TAGLINE = "2 cases · 12,000 suspects · 2 killers"
FMTS = {"letter": "print-US-Letter", "a4": "print-A4", "ipad": "iPad"}
OUT_NAMES = {"letter": "bundle_print-US-Letter.pdf", "a4": "bundle_print-A4.pdf", "ipad": "bundle_iPad.pdf"}
SOLUTIONS_ZIP = "bundle_SOLUTIONS.zip"

# palettes: case 2 = storm green with orange, case 3 = plum with gold
STORM = dict(dark=(0x0E, 0x1A, 0x12), mid=(0x1C, 0x36, 0x1E), accent=(0xE5, 0x8A, 0x2B), accent2=(0xB4, 0x50, 0x1F),
             light=(0xF4, 0xEA, 0xD0))
MOON = dict(dark=(0x2B, 0x1B, 0x3D), mid=(0x4A, 0x2C, 0x5E), accent=(0xE3, 0xA6, 0x4B), accent2=(0x8E, 0x5B, 0xB5),
            light=(0xED, 0xE6, 0xD6))
INK = (0x1E, 0x1B, 0x20); PARCH = (0xF3, 0xEC, 0xDF)

CASES = [
    dict(key="storm", no=2, title="Storm over Corvenmoor", short="Storm", dir="halloween-monster",
         slug="storm-over-corvenmoor", pal=STORM, feature="FEATURE 1",
         blurb="Monster Night at an old castle. A thunderstorm, a laced goblet in the Laboratory Tower "
               "and a visitor in a stitched monster mask.",
         docs=["Castle map", "Booth directory", "Receipt & witness note", "Weather log", "Night bus timetable",
               "Witness statements"]),
    dict(key="moon", no=3, title="Full Moon over Morrowmere", short="Moon", dir="halloween-witches",
         slug="full-moon-over-morrowmere", pal=MOON, feature="FEATURE 2",
         blurb="The Moon Fair in a cozy witch village. A full moon, a laced cup in the apothecary’s back "
               "room and a tall hat with a silver crescent pin.",
         docs=["Fair map", "Stall directory", "Book of Brews", "Moon-watcher’s log", "Reading book & note",
               "Shop ledger & rounds"]),
]
for c in CASES:
    d = os.path.join(QCC, c["dir"])
    c["path"] = d
    c["book"] = {f: os.path.join(d, "ipad" if f == "ipad" else "print", f"{c['slug']}_{t}.pdf") for f, t in FMTS.items()}
    c["solution"] = {f: os.path.join(d, "solution", f"{c['slug']}_SOLUTION_{t}.pdf") for f, t in FMTS.items()}
    c["cover_art"] = {f: os.path.join(HERE, "art", f"case_{c['key']}_{f}.jpg") for f in FMTS}   # no "Halloween" (make_case_covers.py)
    c["report"] = json.load(open(os.path.join(d, "verification_report.json")))

def load_hints(case):
    """Import a case's hints.py (and the case.py it needs) under a private name."""
    src = os.path.join(case["path"], "src")
    saved = {k: sys.modules.pop(k) for k in ("case", "hints") if k in sys.modules}
    sys.path.insert(0, src)
    try:
        h = importlib.import_module("hints")
        return h.HINTS
    finally:
        sys.path.remove(src)
        for k in ("case", "hints"):
            sys.modules.pop(k, None)
        sys.modules.update(saved)

def forbidden():
    """Every token that must never be visible in a listing image, for both cases."""
    f = {}
    for c in CASES:
        rep = c["report"]; K = rep["answer"]; tag = c["short"]
        f[f"{tag}: killer first name"] = K["first"]
        f[f"{tag}: killer surname"] = K["last"]
        f[f"{tag}: killer ticket"] = f"{K['ticket']:04d}"
        f[f"{tag}: Sealed Check number"] = rep["seal"]
        for x in rep["finalists"]:
            if x["clue"] == "KILLER":
                continue
            f[f"{tag}: finalist {x['name']}"] = x["name"]
            f[f"{tag}: finalist ticket {x['name']}"] = f"{x['ticket']:04d}"
        for cid, hs in load_hints(c).items():
            for lv in (1, 2):
                f[f"{tag}: hint {cid} level {lv + 1}"] = " ".join(hs[lv].split())[:48]
    f["solution heading"] = "What really happened"
    f["solution index"] = "Elimination index"
    f["solution table"] = "Ruled out by"
    return f
