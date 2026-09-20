#!/usr/bin/env bash
# Download the two Google Fonts the promo uses (OFL) into <dir>.
set -euo pipefail
DIR="${1:?target dir}"
mkdir -p "$DIR"
curl -sS -A "Mozilla/5.0" \
  "https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;700&family=Montserrat:wght@400;500;600;700&display=swap" \
  -o "$DIR/css.txt"
python3 - "$DIR" <<'PY'
import re, subprocess, sys, os
d = sys.argv[1]
css = open(os.path.join(d, "css.txt")).read()
for fam, w, url in re.findall(
        r"font-family: '([^']+)';\s*font-style: \w+;\s*font-weight: (\d+);[^}]*?src: url\((https://[^)]+\.ttf)\)", css):
    name = fam.replace(" ", "") + "-" + w + ".ttf"
    subprocess.run(["curl", "-sSL", "-o", os.path.join(d, name), url], check=True)
    print(name)
PY
