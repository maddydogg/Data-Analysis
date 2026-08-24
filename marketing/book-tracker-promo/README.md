# Book Tracker — Etsy listing video

A 14.9 s square (1080×1080) promo cut from a 93 s raw screen recording of the
Google Sheets book-tracker template, framed in a laptop mockup with headline,
rotating feature captions, badge and footer.

| file | what it is |
| --- | --- |
| `etsy_promo_1080.mp4` | the finished video — 1080×1080, 30 fps, 14.9 s, no audio |
| `etsy_cover_1080.jpg` | still frame from the video, usable as a listing image |
| `build.sh` | rebuilds the video from the raw recording |
| `make_layers.py` | renders the static design layers (background, mockup, captions) |
| `fetch_fonts.sh` | downloads the two Google Fonts used (Playfair Display, Montserrat) |

## What ended up in the cut

Everything from ~58 s onwards in the raw recording was dropped — it contains the
browser bar, the Android quick-settings panel, the screen-recorder toolbar and
the Google Sheets menus in Russian. The five shots that survived:

| in video | from raw | shot | caption |
| --- | --- | --- | --- |
| 0.0–3.4 s | 5.2 s | Reading dashboard, KPIs and highlights | A dashboard that fills itself in |
| 2.9–6.3 s | 41.8 s | Book Tracker, status dropdown open | Log a book in seconds — dropdowns do the work |
| 5.8–9.2 s | 23.5 s | Bookshelf, slow pan down the colour-coded spines | Every book becomes a colour-coded spine |
| 8.7–12.1 s | 15.7 s | Ratings table scrolling into the charts | Charts and stats build themselves |
| 11.6–14.9 s | 0.5 s | Setup tab, the editable dropdown lists | Edit every list — make it yours |

Shots cross-fade over 0.5 s; the video opens and closes on a white fade so it
loops cleanly in Etsy's player.

## Palette

Every colour on the frame comes from `BookTracker.xlsx` itself. Ranking the
solid fills by how many cells actually use them (`xl/styles.xml` mapped through
`cellXfs` onto the eight sheets) puts the mint first — it is the section-header
colour on every tab, so the surround is built on it:

| fill | cells | role in the workbook |
| --- | --- | --- |
| `F4F6F8` | 3106 | neutral row banding inside the tables |
| `DFF3EA` | 113 | **section headers on all 8 sheets — the lead accent** |
| `E4F3F6` | 61 | secondary pale cyan |
| `EAF5EE` | 7 | palest mint |

| role on the frame | taken from | hex |
| --- | --- | --- |
| background gradient | tint of `EAF5EE` → shade of `DFF3EA` | `F4FBF7` → `D3EEE1` |
| headline, footer, captions | heading font colour | `33566B` |
| eyebrow / secondary text | muted font colours `9AA7B4`, `6B7280` | `809894` |
| rules | mint shade | `B9DFCD` |
| badge | heading colour, ring and micro-type in the mint | `33566B` / `DFF3EA` |
| chip row under the headline | the ten book-spine fills | `C9A9F0 F4B8D0 B3DCF0 BFE8C6 F3D89A D8E6A8 F0BDB5 CDB8EC CFC4BC D6C4A6` |

Fixed copy on the frame: `GOOGLE SHEETS · INSTANT DOWNLOAD` (eyebrow),
`The Reading Tracker` (headline), `AUTO-UPDATING DASHBOARD` (badge),
`8 TABS · DASHBOARD · BOOKSHELF · TRACKER · TBR · WISHLIST · SERIES` and
`NO SETUP — JUST MAKE A COPY AND START LOGGING` (footer).

## Rebuild

```bash
./fetch_fonts.sh /tmp/promo/fonts
./build.sh /path/to/Screen_recording.webm /tmp/promo etsy_promo_1080.mp4
```

`build.sh` needs an ffmpeg binary; it uses the one shipped with the
`imageio-ffmpeg` Python package. `make_layers.py` needs Pillow.

To change the wording, edit the strings in `make_layers.py` (headline, badge and
footer live in the background/foreground sections, the five captions in
`CAPTIONS`). To re-time a shot, edit the `cut` lines in `build.sh` — the numbers
are start second and duration in the raw recording.
