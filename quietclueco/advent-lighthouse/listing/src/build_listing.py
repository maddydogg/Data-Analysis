"""Build every listing asset for the calendar and check it:

    cd listing/src && python3 build_listing.py [--no-video]

Outputs: ../mockups/*.jpg (10 + overview), ../video/*.mp4 (trailer and calendar presentation),
../../delivery/ (4 files for Etsy), ../../out/ (the archives), ../spoiler_check.md / .json.
Exits non-zero if any check fails.
"""
import json, os, re, shutil, subprocess, sys, zipfile
from PIL import Image
import imageio_ffmpeg
import pymupdf as fitz
import kit, mockups
import cal_listing as CL
import verify as VER          # the case stop list (src/ is on the path via cal_listing)

HERE = os.path.dirname(os.path.abspath(__file__))
LISTING = os.path.dirname(HERE)
MOCK = os.path.join(LISTING, "mockups")
VIDEO = os.path.join(LISTING, "video")
DELIV = os.path.join(CL.CASE, "delivery")
OUT = os.path.join(CL.CASE, "out")
ETSY_LIMIT_MB = 20

def probe(path):
    out = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-i", path], capture_output=True, text=True).stderr
    dur = re.search(r"Duration: (\d+):(\d+):([\d.]+)", out)
    size = re.search(r"Video: .*?, (\d+)x(\d+)", out)
    return dict(seconds=int(dur.group(1)) * 3600 + int(dur.group(2)) * 60 + float(dur.group(3)),
                width=int(size.group(1)), height=int(size.group(2)), audio="Audio:" in out,
                fps=re.search(r"([\d.]+) fps", out).group(1))

def delivery():
    shutil.rmtree(DELIV, ignore_errors=True); os.makedirs(DELIV)
    files = []
    for key in ("letter", "a4", "ipad"):
        dst = os.path.join(DELIV, os.path.basename(CL.PDF[key])); shutil.copyfile(CL.PDF[key], dst); files.append(dst)
    z = os.path.join(DELIV, f"{CL.SLUG}_SOLUTION.zip")
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for key in ("letter", "a4", "ipad"):
            zf.write(CL.SOLUTION[key], arcname=os.path.basename(CL.SOLUTION[key]))
    files.append(z)
    rep = [dict(file=os.path.basename(f), mb=round(os.path.getsize(f) / 2 ** 20, 2)) for f in files]
    with zipfile.ZipFile(z) as zf:
        inside, bad = zf.namelist(), zf.testzip()
    return rep, inside, bad

def archives(mock_paths, videos):
    os.makedirs(OUT, exist_ok=True)
    a1 = os.path.join(OUT, f"{CL.SLUG}_files-for-sale.zip")
    with zipfile.ZipFile(a1, "w", zipfile.ZIP_DEFLATED) as zf:
        for n in sorted(os.listdir(DELIV)):
            zf.write(os.path.join(DELIV, n), arcname=n)
    for fn in os.listdir(OUT):
        p = os.path.join(OUT, fn)
        if os.path.isdir(p):
            shutil.rmtree(p)
        elif fn != os.path.basename(a1):
            os.remove(p)
    a2 = os.path.join(OUT, f"{CL.SLUG}_10-mockups-JPG.zip")
    with zipfile.ZipFile(a2, "w", zipfile.ZIP_STORED) as zf:
        for p in mock_paths:
            zf.write(p, arcname=os.path.basename(p))
    vids = []
    for v in videos:
        dst = os.path.join(OUT, os.path.basename(v)); shutil.copyfile(v, dst); vids.append(dst)
    return [a1, a2] + vids

def main(video=True):
    checks = []
    def ok(name, passed, detail=""):
        checks.append(dict(name=name, passed=bool(passed), detail=detail)); return passed

    bad = CL.forbidden()
    ok("Spoiler list loaded from the verification report",
       all(k in bad for k in ("killer first name", "killer surname", "killer tally", "Sealed Check number"))
       and sum(k.startswith("finalist tally") for k in bad) >= 20 and sum(k.startswith("window") for k in bad) >= 60,
       f"{len(bad)} forbidden tokens: killer name and tally, Sealed Check number, "
       f"{sum(k.startswith('finalist tally') for k in bad)} finalists (names + tallies), level-2/3 hints, "
       f"the journal entry, papers and question of every window from 4 to 23, solution headings")
    L = kit.Pdf(CL.PDF["letter"]); S = kit.Pdf(CL.SOLUTION["letter"])
    K = CL.C.KILLER
    kp = next(i for i, p in enumerate(L.doc) if K["last"] in p.get_text() and "SURNAME" in p.get_text())
    w12 = L.find("WINDOW 12 OF 24")
    ctrl = kit.spoiler_scan([("pdf", "killer's register page", L.doc[kp].get_text()),
                             ("pdf", "solution p1", S.doc[0].get_text()),
                             ("pdf", "Window 12", L.doc[w12].get_text())], bad)
    labels = {h["label"] for h in ctrl}
    ok("Control test: the scanner flags the killer's Sound Book page, the solution and a later window",
       {"killer surname", "killer tally", "Sealed Check number", "window 12 journal"} <= labels, f"{len(ctrl)} hits")

    res, sheet, A = mockups.build(MOCK)
    for r in res:
        im = Image.open(r["path"])
        ok(f"Mockup {r['name']}: 2000x2000 JPG", im.size == (2000, 2000) and im.format == "JPEG",
           f"{os.path.getsize(r['path']) // 1024} KB")
        ok(f"Mockup {r['name']}: no spoilers in any visible text ({len(r['sources'])} sources)", not r["hits"],
           "; ".join(f"{h['label']} in {h['source']}" for h in r["hits"]))
    hero = " ".join(t for _, _, t in res[0]["sources"])
    need = ["THE KEEPER OF", "CANDLEHOLM", "24", "DAYS", "PRINTABLE", "iPAD", "ADVENT CALENDAR"]
    ok("Image 01 carries the title, 24 days, PRINTABLE and iPad", all(n.lower() in hero.lower() for n in need),
       ", ".join(n for n in need if n.lower() not in hero.lower()) or "all present")
    shown = sorted({int(m) for r in res for _, _, t in r["sources"] for m in re.findall(r"WINDOW (\d+) OF 24", t)})
    ok("Only Windows 1–3 appear in the mockups", set(shown) <= set(CL.EARLY), str(shown))
    ok("Sound Book page used in the visuals holds neither the killer nor any finalist",
       not kit.spoiler_scan([("pdf", "log", A.L.doc[A.log_page].get_text())], bad), f"page {A.log_page + 1}")

    vids = []
    if video:
        import video as VID
        out = VID.build()
        for k, (path, n, hits, hf, caps) in out.items():
            ok(f"Video {k}: every one of {n} frames checked, no spoilers", hf == 0, f"{hf} frames with hits")
            pv = probe(path)
            ok(f"Video {k}: 1080x1080, 12–15 s, no sound", pv["width"] == 1080 and pv["height"] == 1080
               and 12 <= pv["seconds"] <= 15 and not pv["audio"], json.dumps(pv))
            ok(f"Video {k}: captions use evidence / lead, never the stop-listed word for it",
               not any(re.search(r"\bclues?\b", c.lower()) for c in caps), "; ".join(caps))
            vids.append(path)
    else:
        vids = [os.path.join(VIDEO, f) for f in sorted(os.listdir(VIDEO)) if f.endswith(".mp4")]

    drawn = [t for r in res for k, _, t in r["sources"] if k == "drawn"]
    import video as VIDMOD
    captions = re.findall(r'caption\(f, "([^"]+)"', open(VIDMOD.__file__).read())
    hits = sorted({b for b in VER.BANNED for t in drawn + captions
                   if re.search(r"\b" + re.escape(b.lower()) + r"\b", t.lower())})
    ok("Stop list: no borrowed brands, titles, real lighthouses or earlier names in any drawn text or video caption (whole words)",
       not hits, ", ".join(hits) or f"{len(drawn) + len(captions)} strings checked")

    rep, inside, zbad = delivery()
    names = sorted(os.listdir(DELIV))
    ok("Delivery folder has exactly 4 files (Etsy allows 5)", len(names) == 4, ", ".join(names))
    for r in rep:
        ok(f"Delivery {r['file']} is under {ETSY_LIMIT_MB} MB", r["mb"] < ETSY_LIMIT_MB, f"{r['mb']} MB")
    ok("Solution ZIP holds the solution in all three formats and is intact",
       sorted(inside) == sorted(os.path.basename(p) for p in CL.SOLUTION.values()) and zbad is None, ", ".join(inside))
    for n in names:
        if n.endswith(".pdf"):
            t = " ".join(p.get_text() for p in fitz.open(os.path.join(DELIV, n)))
            ok(f"Delivery {n} is the calendar, not the solution, and never names the killer outside the register",
               "Elimination index" not in t and "What really happened" not in t
               and t.count(f"{K['first']} {K['last']}") <= 1)
    ok("Drawn text never uses the word clue (evidence / lead instead)",
       not any(re.search(r"\bclues?\b", t.lower()) for t in drawn + captions))
    arch = archives([r["path"] for r in res], vids)
    for a in arch:
        ok(f"Archive {os.path.basename(a)} written", os.path.getsize(a) > 0, f"{os.path.getsize(a) / 2 ** 20:.1f} MB")

    passed = sum(c["passed"] for c in checks)
    lines = ["# Listing assets: spoiler and format check", "", f"Result: **{passed} of {len(checks)} checks passed**", "",
             "How it works: every mockup and every video frame is built from real PDF regions and code-drawn text. "
             "The builder records the text layer of every region it places and every string it draws, and scans it "
             "for forbidden tokens: the killer's name and tally, the Sealed Check number, every finalist's name and "
             "tally, the start of every level-2 and level-3 hint, the journal entry, the pinned papers and the question "
             "of every window from 4 to 23, and the solution headings. A control run on the killer's Sound Book page, "
             "the solution and Window 12 shows the scanner catches them. Every drawn string and video caption is also "
             "run through the case's stop list.", "", "| # | Check | Result | Detail |", "|---|---|---|---|"]
    for i, c in enumerate(checks, 1):
        lines.append(f"| {i} | {c['name']} | {'PASS' if c['passed'] else 'FAIL'} | {c['detail'].replace('|', '/')} |")
    open(os.path.join(LISTING, "spoiler_check.md"), "w").write("\n".join(lines) + "\n")
    json.dump(dict(checks=checks, delivery=rep), open(os.path.join(LISTING, "spoiler_check.json"), "w"), indent=1)
    print(f"checks {passed}/{len(checks)}")
    for c in checks:
        if not c["passed"]:
            print("FAIL", c["name"], c["detail"])
    return passed == len(checks)

if __name__ == "__main__":
    sys.exit(0 if main(video="--no-video" not in sys.argv) else 1)
