# Listing assets: Snowfall at Ember Square

| Path | What it is |
|---|---|
| `mockups/snowfall-at-ember-square_01-main.png` … `_10-what-you-get.png` | 10 listing images, 2000×2000 PNG |
| `mockups/snowfall-at-ember-square_overview.png` | All 10 images on one sheet |
| `video/snowfall-at-ember-square_listing-video_1080.mp4` | 1080×1080 video, 14.6 s, 30 fps, no sound |
| `../delivery/` | The 4 files to upload to Etsy |
| `spoiler_check.md` / `.json` | Spoiler and format checks (every mockup, every video frame) |
| `src/` | Build scripts: `kit.py` (reusable drawing and spoiler scan), `case_listing.py` (case-specific pages and words — copy this for the next case), `mockups.py`, `video.py`, `delivery.py`, `build_listing.py` |

## Rebuild

```bash
pip install pymupdf pillow imageio-ffmpeg
cd src && python3 build_listing.py
```

It exits with a non-zero code if any check fails.
