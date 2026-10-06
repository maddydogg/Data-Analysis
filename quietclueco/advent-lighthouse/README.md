# The Keeper of Candleholm — QuietClueCo advent calendar B

A Christmas murder mystery in 24 windows, one for each day from 1 to 24 December, in a cosy vintage
picture-book style (gouache and linocut textures, a mid-century travel-poster cover; no faces). Day 1 is
the case, Day 2 is the Sound Book of 2,400 travellers, Days 3–23 each bring one page of the keeper's journal
with the paper he pinned to it, and on Day 24 one line is left. 1–4 players, 10–25 minutes a day.

Same mechanics as calendar A (The Windows at Quillon's), so the two looks can be compared fairly; the story,
the visuals and the keywords are its own.

Story: Candleholm is a tiny island with one lighthouse in the Sound between the mainland and the island of
Inishvarra. In December the keeper, Ezra Tullock, finds the missing Christmas parcels for Inishvarra hidden in
his own boathouse and writes down, one day at a time, everything he learns about the stranger in a red knitted
cap. On Christmas Eve, at lighting-up time, the lamp does not come on.

## Files

| Path | What it is |
|---|---|
| `print/the-keeper-of-candleholm_print-US-Letter.pdf` | The calendar to print, US Letter (90 pages): set-up pages, envelope template, day numbers 1–24, the 24 windows (each starts on its own page), hints, Sealed Check |
| `print/the-keeper-of-candleholm_print-A4.pdf` | The same on A4 (87 pages) |
| `ipad/the-keeper-of-candleholm_iPad.pdf` | iPad version (81 pages): the first page is a calendar of 24 tappable windows; every window links back |
| `solution/…_SOLUTION_*.pdf` | The Envelope: the answer, the story, the solution day by day, the finalists and an index of all 2,400 lines |
| `delivery/` | The 4 files for Etsy: 3 calendar PDFs and `the-keeper-of-candleholm_SOLUTION.zip` |
| `listing/mockups/` | 10 listing images, 2000×2000 JPG, plus an overview sheet |
| `listing/video/` | Trailer and calendar presentation, 1080×1080, 14 s, no sound, with poster frames and storyboards |
| `listing/etsy_listing.md` | Title, description, 13 tags + 5 spares with Listadum data, phrases to check by hand |
| `listing/spoiler_check.md` / `.json` | Spoiler and format check of every mockup, every video frame, the delivery folder and the archives |
| `verification_report.md` / `.json` | Code checks of the puzzle and the PDFs |
| `out/` | Archives (not in git): `…_files-for-sale.zip`, `…_10-mockups-JPG.zip` and both videos |
| `src/` | `case.py` (story, chart, tides, almanac, clues, journal), `hints.py`, `generate.py`, `verify.py`, `art.py` (vintage drawing kit), `scenes.py` (key art and 24 vignettes), `cover.py`, `render.py`, `build.py` |
| `listing/src/` | `mockups.py`, `video.py`, `build_listing.py`, `kit.py`, `cal_listing.py` |

## Rebuild

```bash
pip install reportlab pymupdf fonttools pillow imageio-ffmpeg numpy
cd src && python3 build.py --art                 # Sound Book, checks, art, PDFs, previews
cd ../listing/src && python3 build_listing.py    # mockups, videos, delivery, archives, spoiler check
```

Both builds are deterministic and exit non-zero if any check fails.

## Answer (spoiler)

<details><summary>Show</summary>

Jonas Garvock, tally 1478, from Carrowby. First crossing 2 December at 13:38 on the Mail Boat, put ashore at
landing 15 (Ferrach Pier). Sealed Check 924.

</details>
