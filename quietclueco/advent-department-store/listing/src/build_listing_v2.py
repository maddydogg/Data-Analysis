"""Build and check the second listing variant ("v2 action"): 10 mockups and 2 videos.

    cd listing/src && python3 build_listing_v2.py [--no-video]

Outputs: ../v2/mockups/*.jpg (10 + overview), ../v2/video/*.mp4 (trailer and calendar presentation, with
posters and storyboards), ../../out/v2-action/ (the mockup ZIP and both videos), ../v2/spoiler_check.md/.json.
Variant 1 (../mockups, ../video) is left untouched. The files for sale are the same for both variants.
Exits non-zero if any check fails.
"""
import json, os, re, shutil, sys, zipfile
from PIL import Image
import kit
import cal_listing as CL
import mockups_v2 as M2
import build_listing as B1
sys.path.insert(0, os.path.join(CL.CASE, "src"))
import verify as VER          # noqa: E402  (the case's stop list)

V2 = os.path.join(CL.CASE, "listing", "v2")
OUT = os.path.join(CL.CASE, "out", "v2-action")
TAG = f"{CL.SLUG}_{M2.VARIANT}"

def stop_hits(strings):
    hits = set()
    for t in strings:
        for b in VER.BANNED:
            if re.search(r"\b" + re.escape(b.lower()) + r"\b", t.lower()):
                hits.add(b)
    return sorted(hits)

def main(video=True):
    checks = []
    def ok(name, passed, detail=""):
        checks.append(dict(name=name, passed=bool(passed), detail=detail)); return passed

    bad = CL.forbidden()
    ok("Spoiler list loaded from the verification report",
       all(k in bad for k in ("killer first name", "killer surname", "killer pass", "Sealed Check number"))
       and sum(k.startswith("window") for k in bad) >= 40, f"{len(bad)} forbidden tokens")

    res, sheet, A = M2.build(os.path.join(V2, "mockups"))
    drawn = []
    for r in res:
        im = Image.open(r["path"])
        ok(f"Mockup {r['name']}: 2000x2000 JPG", im.size == (2000, 2000) and im.format == "JPEG",
           f"{os.path.getsize(r['path']) // 1024} KB")
        ok(f"Mockup {r['name']}: no spoilers in any visible text ({len(r['sources'])} sources)", not r["hits"],
           "; ".join(f"{h['label']} in {h['source']}" for h in r["hits"]))
        drawn += [t for k, _, t in r["sources"] if k == "drawn"]
    hero = " ".join(t for _, _, t in res[0]["sources"])
    need = ["THE WINDOWS", "AT QUILLON’S", "24", "DAYS", "PRINTABLE", "iPad", "ADVENT CALENDAR"]
    ok("Image 01 carries the title, 24 days, PRINTABLE and iPad", all(n in hero for n in need),
       ", ".join(n for n in need if n not in hero) or "all present")
    shown = sorted({int(m) for r in res for _, _, t in r["sources"] for m in re.findall(r"WINDOW (\d+) OF 24", t)})
    ok("Only Windows 1–3 appear in the mockups", set(shown) <= set(CL.EARLY), str(shown))

    vids = []
    if video:
        import video_v2 as VID
        out = VID.build()
        for k, (path, n, hits, hf) in out.items():
            ok(f"Video {k}: every one of {n} frames checked, no spoilers", hf == 0, f"{hf} frames with hits")
            pv = B1.probe(path)
            ok(f"Video {k}: 1080x1080, 12–15 s, no sound", pv["width"] == 1080 and pv["height"] == 1080
               and 12 <= pv["seconds"] <= 15 and not pv["audio"], json.dumps(pv))
            vids.append(path)
    else:
        vd = os.path.join(V2, "video")
        vids = [os.path.join(vd, f) for f in sorted(os.listdir(vd)) if f.endswith(".mp4")]

    import video_v2 as VID
    captions = re.findall(r'slam\(f, "([^"]+)"', open(VID.__file__).read())
    hits = stop_hits(drawn + captions)
    ok("Stop list: no borrowed brands, titles or real stores in any drawn text or caption (whole words)", not hits,
       ", ".join(hits) or f"{len(drawn) + len(captions)} strings checked")

    os.makedirs(OUT, exist_ok=True)
    for fn in os.listdir(OUT):
        os.remove(os.path.join(OUT, fn))
    z = os.path.join(OUT, f"{TAG}_10-mockups-JPG.zip")
    with zipfile.ZipFile(z, "w", zipfile.ZIP_STORED) as zf:
        for r in res:
            zf.write(r["path"], arcname=os.path.basename(r["path"]))
    with zipfile.ZipFile(z) as zf:
        n = len(zf.namelist()); bad_zip = zf.testzip()
    ok("Mockup ZIP holds the 10 images and is intact", n == 10 and bad_zip is None, f"{os.path.getsize(z) / 2 ** 20:.1f} MB")
    for v in vids:
        dst = os.path.join(OUT, os.path.basename(v)); shutil.copyfile(v, dst)
        ok(f"Archive {os.path.basename(dst)} written", os.path.getsize(dst) > 0, f"{os.path.getsize(dst) / 2 ** 20:.1f} MB")

    passed = sum(c["passed"] for c in checks)
    lines = ["# Listing assets, variant 2 (action): spoiler and format check", "",
             f"Result: **{passed} of {len(checks)} checks passed**", "",
             "Same method as variant 1: every mockup and every video frame records the text of every PDF region it "
             "places and every string it draws, and the scanner looks for the killer's name and pass, the Sealed "
             "Check number, every finalist, the level-2 and level-3 hints, the evidence and question of every "
             "window from 4 to 23, and the solution headings. Variant 2 also runs the case's stop list over every "
             "drawn string and caption.", "", "| # | Check | Result | Detail |", "|---|---|---|---|"]
    for i, c in enumerate(checks, 1):
        lines.append(f"| {i} | {c['name']} | {'PASS' if c['passed'] else 'FAIL'} | {c['detail'].replace('|', '/')} |")
    open(os.path.join(V2, "spoiler_check.md"), "w").write("\n".join(lines) + "\n")
    json.dump(dict(checks=checks), open(os.path.join(V2, "spoiler_check.json"), "w"), indent=1)
    print(f"checks {passed}/{len(checks)}")
    for c in checks:
        if not c["passed"]:
            print("FAIL", c["name"], c["detail"])
    return passed == len(checks)

if __name__ == "__main__":
    sys.exit(0 if main(video="--no-video" not in sys.argv) else 1)
