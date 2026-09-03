"""Download the two OFL families the video is set in, into $WORK/fonts."""
import os, re, sys, urllib.request

WORK = os.environ.get("WORK", os.path.dirname(os.path.abspath(__file__)) + "/work")
DEST = WORK + "/fonts"
CSS = ("https://fonts.googleapis.com/css2?"
       "family=Montserrat:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700")
STYLE = {400: "Regular", 500: "Medium", 600: "SemiBold", 700: "Bold", 800: "ExtraBold"}

os.makedirs(DEST, exist_ok=True)
req = urllib.request.Request(CSS, headers={"User-Agent": "Mozilla/4.0"})   # old UA -> ttf
css = urllib.request.urlopen(req, timeout=60).read().decode()
for block in css.split("@font-face")[1:]:
    fam = re.search(r"font-family: '([^']+)'", block).group(1)
    wght = int(re.search(r"font-weight: (\d+)", block).group(1))
    url = re.search(r"url\((https://[^)]+\.ttf)\)", block).group(1)
    out = f"{DEST}/{fam}-{STYLE[wght]}.ttf"
    if os.path.exists(out):
        continue
    with urllib.request.urlopen(url, timeout=60) as r, open(out, "wb") as f:
        f.write(r.read())
    print("fetched", os.path.basename(out))
