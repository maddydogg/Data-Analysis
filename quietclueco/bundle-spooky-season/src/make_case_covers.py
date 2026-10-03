"""Re-render the two case covers for the bundle without the word "Halloween", so the bundle
cover and listing images keep working after 31 October. Uses each case's own cover code
unchanged and only swaps that one line of small print:

    python3 make_case_covers.py   ->  art/case_storm_*.jpg, art/case_moon_*.jpg
"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
QCC = os.path.dirname(os.path.dirname(HERE))
ART = os.path.join(HERE, "art")
SIZES = '(("letter", (612, 792)), ("a4", (595.28, 841.89)), ("ipad", (768, 1024)))'

STORM = f'''
import os, horror_heroes as HH
orig = HH.tracked
def tracked(fr, cx, y, text, *a, **kw):
    return orig(fr, cx, y, text.replace("A HALLOWEEN MURDER MYSTERY PUZZLE", "A MURDER MYSTERY PUZZLE"), *a, **kw)
HH.tracked = tracked
for fmt, (pw, ph) in {SIZES}:
    f = HH.cover_monster_movie(1400, round(1400 * ph / pw))
    assert not any("HALLOWEEN" in t.upper() for _, _, t in f.sources)
    f.img.convert("RGB").save(os.path.join({ART!r}, "case_storm_" + fmt + ".jpg"), quality=90)
'''
MOON = f'''
import os, kit, poster as P
kit.set_font_dir(os.path.abspath("../../src/fonts"))
swap = lambda s: s.replace("A HALLOWEEN MYSTERY IN 18 CLUES", "A MURDER MYSTERY IN 18 CLUES")
orig_t, orig_f = P.tracked, P.fit
P.tracked = lambda fr, cx, y, text, *a, **kw: orig_t(fr, cx, y, swap(text), *a, **kw)
P.fit = lambda text, *a, **kw: orig_f(swap(text), *a, **kw)
for fmt, (pw, ph) in {SIZES}:
    f = P.cover_poster(1400, round(1400 * ph / pw))
    assert not any("HALLOWEEN" in t.upper() for _, _, t in f.sources)
    f.img.convert("RGB").save(os.path.join({ART!r}, "case_moon_" + fmt + ".jpg"), quality=90)
'''

if __name__ == "__main__":
    os.makedirs(ART, exist_ok=True)
    for d, code in (("halloween-monster", STORM), ("halloween-witches", MOON)):
        subprocess.run([sys.executable, "-B", "-c", code], cwd=os.path.join(QCC, d, "listing", "src"), check=True)
    print("ok")
