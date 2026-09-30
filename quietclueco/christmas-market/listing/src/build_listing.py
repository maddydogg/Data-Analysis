"""One command builds every listing asset for the case and checks it for spoilers:

    cd listing/src && python3 build_listing.py

Outputs: ../mockups/*.png (10 + overview), ../video/*.mp4, ../../delivery/ (4 files),
../spoiler_check.md and ../spoiler_check.json. Exits non-zero if any check fails.
"""
import json, os, re, subprocess, sys
from PIL import Image
import imageio_ffmpeg
import pymupdf as fitz
import kit, mockups, video, delivery
import case_listing as CL

HERE = os.path.dirname(os.path.abspath(__file__))
LISTING = os.path.dirname(HERE)
MOCK = os.path.join(LISTING, "mockups")
VID = os.path.join(LISTING, "video", f"{CL.SLUG}_listing-video_1080.mp4")
DELIV = os.path.join(CL.CASE, "delivery")

def probe(path):
    out = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-i", path], capture_output=True, text=True).stderr
    dur = re.search(r"Duration: (\d+):(\d+):([\d.]+)", out)
    secs = int(dur.group(1)) * 3600 + int(dur.group(2)) * 60 + float(dur.group(3))
    size = re.search(r"Video: .*?, (\d+)x(\d+)", out)
    return dict(seconds=secs, width=int(size.group(1)), height=int(size.group(2)),
                audio="Audio:" in out, fps=re.search(r"([\d.]+) fps", out).group(1))

def main():
    checks = []
    def ok(name, passed, detail=""):
        checks.append(dict(name=name, passed=bool(passed), detail=detail)); return passed

    bad = CL.forbidden()
    ok("Spoiler list loaded from the verification report",
       all(k in bad for k in ("killer first name", "killer surname", "killer ticket", "Sealed Check number"))
       and sum(k.startswith("finalist ticket") for k in bad) >= 20,
       f"{len(bad)} forbidden tokens: killer name and ticket, Sealed Check number, "
       f"{sum(k.startswith('finalist ticket') for k in bad)} finalists (names + tickets), "
       f"{sum(k.startswith('hint') for k in bad)} level-2/3 hints, solution headings")

    # control test: the scanner must catch spoilers when they are there
    L = kit.Pdf(CL.PDF["letter"]); S = kit.Pdf(CL.SOLUTION["letter"])
    kp = next(i for i, p in enumerate(L.doc) if CL.C.KILLER["last"] in p.get_text() and "FIRST NAME" in p.get_text())
    ctrl = kit.spoiler_scan([("pdf", "killer's log page", L.doc[kp].get_text()),
                             ("pdf", "solution p1", S.doc[0].get_text()),
                             ("pdf", "check page", L.doc[CL.pages()[2]["check"]].get_text())], bad)
    labels = {h["label"] for h in ctrl}
    ok("Control test: the scanner flags the killer's log page, the solution and the check page",
       {"killer surname", "killer ticket", "Sealed Check number"} <= labels, f"{len(ctrl)} hits in the control sources")

    # mockups
    res, sheet, A = mockups.build(MOCK)
    for r in res:
        im = Image.open(r["path"])
        ok(f"Mockup {r['name']}: 2000x2000 PNG", im.size == (2000, 2000) and im.format == "PNG", f"{im.size}")
        ok(f"Mockup {r['name']}: no spoilers in any visible text ({len(r['sources'])} sources)",
           not r["hits"], "; ".join(f"{h['label']} in {h['source']}" for h in r["hits"]))
    ok("Visitor Log page used in visuals contains neither the killer nor any finalist",
       not kit.spoiler_scan([("pdf", "log", A.L.doc[A.log_page].get_text())], bad), f"page {A.log_page + 1}")

    # video
    frames, n, total = video.build(VID)
    hits = [f for f in frames if f["hits"]]
    ok(f"Video: every one of {n} frames checked, no spoilers", not hits,
       f"{len(hits)} frames with hits" if hits else "0 frames with hits")
    pv = probe(VID)
    ok("Video: 1080x1080, 12-15 s, no sound", pv["width"] == 1080 and pv["height"] == 1080
       and 12 <= pv["seconds"] <= 15 and not pv["audio"], json.dumps(pv))

    # delivery
    rep, inside, zbad = delivery.build(DELIV)
    names = sorted(os.listdir(DELIV))
    ok("Delivery folder has exactly 4 files (Etsy allows 5)", len(names) == 4, ", ".join(names))
    for r in rep:
        ok(f"Delivery {r['file']} is under 20 MB", r["ok"], f"{r['mb']} MB")
    ok("Solution ZIP holds the three solution PDFs and is intact",
       sorted(inside) == sorted(os.path.basename(p) for p in CL.SOLUTION.values()) and zbad is None, ", ".join(inside))
    for name in names:
        if name.endswith(".pdf"):
            t = " ".join(p.get_text() for p in fitz.open(os.path.join(DELIV, name)))
            ok(f"Delivery {name} is a case book, not a solution", "Elimination index" not in t and "What really happened" not in t)

    passed = sum(c["passed"] for c in checks)
    lines = ["# Listing assets: spoiler and format check", "",
             f"Result: **{passed} of {len(checks)} checks passed**", "",
             "How the spoiler check works: every mockup and every video frame is built from real PDF regions "
             "and code-drawn text. The builder records the PDF text layer of each region it places and every "
             "string it draws, and scans all of it for the forbidden tokens: the killer's name and ticket, "
             "the Sealed Check number, every finalist's name and ticket, the start of every level-2 and "
             "level-3 hint, and the solution headings. A control run on the killer's own log page, the "
             "solution file and the check page shows that the scanner does catch them.", "",
             "| # | Check | Result | Detail |", "|---|---|---|---|"]
    for i, c in enumerate(checks, 1):
        lines.append(f"| {i} | {c['name']} | {'PASS' if c['passed'] else 'FAIL'} | {c['detail'].replace('|', '/')} |")
    lines += ["", "## Files", ""] + [f"- listing/mockups/{os.path.basename(r['path'])}" for r in res] + \
        [f"- listing/mockups/{os.path.basename(sheet)}", f"- listing/video/{os.path.basename(VID)}"] + \
        [f"- delivery/{n_}" for n_ in names]
    open(os.path.join(LISTING, "spoiler_check.md"), "w").write("\n".join(lines) + "\n")
    json.dump(dict(checks=checks, video=pv, delivery=rep), open(os.path.join(LISTING, "spoiler_check.json"), "w"), indent=1)
    print(f"checks {passed}/{len(checks)}")
    for c in checks:
        if not c["passed"]:
            print("FAIL", c["name"], c["detail"])
    return passed == len(checks)

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
