"""Render the Feature 1 (Storm over Corvenmoor) scene layers for the bundle video with case 2's own
drawing code (horror_heroes.py), unchanged: the castle at night, the hooded figure and two
lightning bolts, as 1080x1080 PNG layers in video_assets/.

    python3 make_storm_layers.py
"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "video_assets")
CASE2 = os.path.join(HERE, "..", "..", "..", "halloween-monster", "listing", "src")

CODE = f'''
import os
from PIL import Image, ImageDraw
import horror_heroes as HH
V = 1080; out = {OUT!r}
bg = Image.new("RGBA", (V, V)); HH.gradient(bg, (0x05, 0x0A, 0x07), (0x1C, 0x36, 0x1E))
HH.rain(bg, 260, 4, alpha=40)
d = ImageDraw.Draw(bg)
HH.castle(d, 840, V, (0x03, 0x05, 0x04), [(140, 330, 105), (380, 260, 90), (720, 410, 115), (950, 300, 100)],
          lit=(0xF2, 0xC1, 0x4E))
d.rectangle([0, 840, V, V], fill=(0x03, 0x05, 0x04))
bg.save(os.path.join(out, "storm_bg.png"))
fig = Image.new("RGBA", (V, V), (0, 0, 0, 0))
HH.glow(fig, ("ellipse", [540 - 250, 430 - 210, 540 + 250, 430 + 380]), (0x9B, 0xC5, 0x3D), 110, 80)
HH.monster_bust(fig, 540, 520, 200, (0x06, 0x0A, 0x07), rim=(0xB6, 0xE0, 0x4A), rim_blur=10)
fig.save(os.path.join(out, "storm_figure.png"))
for k, (x, y1, seed, w) in enumerate(((190, 620, 11, 7), (900, 520, 5, 6))):
    b = Image.new("RGBA", (V, V), (0, 0, 0, 0))
    HH.lightning(b, HH.bolt_path(x, 130, y1, seed, 55), w, branch_seed=k + 2)
    b.save(os.path.join(out, f"storm_bolt{{k}}.png"))
print("ok")
'''

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    subprocess.run([sys.executable, "-B", "-c", CODE], cwd=CASE2, check=True)
