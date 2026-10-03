"""Build the 10 listing images for the Storm & Moon Double Feature and check them:

    python3 build_listing.py   (after ../../src/build_bundle.py)

Writes ../spoiler_check.md and ../spoiler_check.json; exits non-zero if any check fails."""
import json, os, sys
from PIL import Image
import pymupdf as fitz
import mockups as M
import bundle as B
import kit

LISTING = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main():
    checks = []
    def ok(name, passed, detail=""):
        checks.append(dict(name=name, passed=bool(passed), detail=detail))
    bad = B.forbidden()
    n_fin = sum("finalist ticket" in k for k in bad)
    ok("Spoiler list loaded for both cases", n_fin >= 40 and all(f"{c['short']}: killer surname" in bad for c in B.CASES),
       f"{len(bad)} tokens: both killers' names and tickets, both Sealed Check numbers, {n_fin} finalists, "
       f"{sum('hint' in k for k in bad)} level-2/3 hints, solution headings")
    # control: the scanner must catch the real spoilers when they are there
    for c in B.CASES:
        L = fitz.open(c["book"]["letter"]); S_ = fitz.open(c["solution"]["letter"]); K = c["report"]["answer"]
        kp = next(p.get_text() for p in L if f"{K['first']}" in p.get_text() and "FIRST NAME" in p.get_text())
        chk = next(p.get_text() for p in L if "The Sealed Check" in p.get_text() and "Ticket number" in p.get_text())
        hits = {h["label"] for h in kit.spoiler_scan([("pdf", "log", kp), ("pdf", "solution", S_[0].get_text()),
                                                      ("pdf", "check", chk)], bad)}
        want = {f"{c['short']}: killer surname", f"{c['short']}: killer ticket", f"{c['short']}: Sealed Check number"}
        ok(f"Control test ({c['title']}): the scanner flags the killer's log page, the solution and the check page",
           want <= hits, f"{len(hits)} labels hit")
    res, sheet, A = M.build()
    for r in res:
        im = Image.open(r["path"])
        ok(f"Image {r['name']}: 2000x2000 JPG", im.size == (2000, 2000) and im.format == "JPEG",
           f"{os.path.getsize(r['path']) // 1024} KB")
        ok(f"Image {r['name']}: no spoilers of either case in any visible text ({len(r['sources'])} sources)",
           not r["hits"], "; ".join(f"{h['label']} in {h['source']}" for h in r["hits"]))
    hero = " ".join(t for _, _, t in res[0]["sources"])
    need = ["STORM & MOON", "DOUBLE FEATURE", "2 CASES", "12,000 SUSPECTS", "2 KILLERS", "PRINTABLE", "iPad"]
    ok("Image 01 carries the bundle title, both cases, 2 cases / 12,000 suspects / 2 killers, PRINTABLE and iPad",
       all(n in hero for n in need) and all(c["title"] in hero for c in B.CASES), ", ".join(n for n in need if n not in hero) or "all present")
    ok("Images show no Halloween wording (the bundle should live past 31 October)",
       not any("halloween" in t.lower() for r in res for k, s, t in r["sources"] if k == "drawn"))
    for c, cs in zip(B.CASES, A.cs):
        ok(f"{c['title']}: the Visitor Log page used has neither the killer nor any finalist",
           not kit.spoiler_scan([("pdf", "log", cs.L.doc[cs.log].get_text())], bad), f"page {cs.log + 1}")
    passed = sum(c["passed"] for c in checks)
    L = [f"# Listing images: spoiler and format check — {B.NAME}", "", f"Result: **{passed} of {len(checks)} checks passed**", "",
         "Every image is built from real PDF regions and code-drawn text. The builder records the text layer of every "
         "region it places and every string it draws, and scans all of it for both cases' killer names and tickets, "
         "Sealed Check numbers, every finalist's name and ticket, the start of every level-2 and level-3 hint, and the "
         "solution headings. A control run on each killer's own log page, solution file and check page shows the "
         "scanner does catch them.", "", "| # | Check | Result | Detail |", "|---|---|---|---|"]
    for i, c in enumerate(checks, 1):
        L.append(f"| {i} | {c['name']} | {'PASS' if c['passed'] else 'FAIL'} | {c['detail'].replace('|', '/')} |")
    L += ["", "## Files", ""] + [f"- listing/mockups/{os.path.basename(r['path'])}" for r in res] + [f"- listing/mockups/{os.path.basename(sheet)}"]
    open(os.path.join(LISTING, "spoiler_check.md"), "w").write("\n".join(L) + "\n")
    json.dump(dict(checks=checks), open(os.path.join(LISTING, "spoiler_check.json"), "w"), indent=1)
    print(f"checks {passed}/{len(checks)}")
    for c in checks:
        if not c["passed"]:
            print("FAIL", c["name"], c["detail"])
    return passed == len(checks)

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
