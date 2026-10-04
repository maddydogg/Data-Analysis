# The Windows at Quillon’s — QuietClueCo advent calendar A

A Christmas Eve murder mystery in 24 windows, one for each day from 1 to 24 December, in an anime-noir look with no faces (snow at a slant, amber shop windows, long shadows, silhouettes seen from behind). Day 1 is the case, Day 2 is the Lantern Register of 2,400 shoppers, Days 3–23 each bring one new piece of evidence that rules shoppers out, and on Day 24 one pass is left. 1–4 players, 10–25 minutes a day.

Story: on Lantern Night the department store Quillon & Daughters in the fictional city of Vellmouth stays open late. Ten minutes before the curtain rises on the Grand Window, the old window dresser Teodor Brann is found in his workshop beside a striped cup of cocoa. He had written to the police that someone with a brass magpie brooch was stealing from his windows. The murder happens while the store is open and full of shoppers, not after closing time.

## Files

| Path | What it is |
|---|---|
| `print/the-windows-at-quillons_print-US-Letter.pdf` | The calendar to print, US Letter (89 pages): set-up pages, envelope template, day numbers 1–24, the 24 windows (each starts on its own page), hints, Sealed Check |
| `print/the-windows-at-quillons_print-A4.pdf` | The same on A4 (85 pages) |
| `ipad/the-windows-at-quillons_iPad.pdf` | iPad version (77 pages): a calendar page of 24 tappable windows, every window links back |
| `solution/…_SOLUTION_*.pdf` | The Envelope: the answer, the story, the solution day by day, the finalists and an index of all 2,400 passes |
| `delivery/` | The 4 files for Etsy: 3 calendar PDFs and `the-windows-at-quillons_SOLUTION.zip` |
| `listing/mockups/` | 10 listing images, 2000×2000 JPG, plus an overview sheet |
| `listing/video/` | Trailer (13.5 s) and calendar presentation (14.0 s), 1080×1080, no sound, with poster frames and storyboards |
| `listing/etsy_listing.md` | Title, description with “how to play each day”, price note and 30 tag candidates with Listadum data |
| `listing/spoiler_check.md` / `.json` | Spoiler and format check of every mockup, every video frame, the delivery folder and the archives |
| `verification_report.md` / `.json` | Code checks of the puzzle and the PDFs |
| `out/` | Archives (not in git): `…_files-for-sale.zip`, `…_10-mockups-JPG.zip` and both videos |
| `src/` | `case.py` (story, store, city, clues), `hints.py`, `generate.py`, `verify.py`, `art.py` (night scenes), `cover.py`, `render.py`, `build.py` |
| `listing/src/` | `mockups.py`, `video.py`, `build_listing.py`, `kit.py`, `cal_listing.py` |

## Rebuild

```bash
pip install reportlab pymupdf fonttools pillow imageio-ffmpeg
cd src && python3 build.py --art                 # register, checks, art, PDFs, previews
cd ../listing/src && python3 build_listing.py    # mockups, videos, delivery, archives, spoiler check
```

Both builds are deterministic and exit non-zero if any check fails.

## Checks added for the calendar

- The windows are read in a fixed order, one a day, so the code checks the curve day by day: every day rules out at least one pass, and at least 7 passes are left after Day 19, 5 after Day 20, 3 after Day 21 and 2 after Day 22. Check-ins on Days 6, 12 and 18 print the counts the code finds.
- Plans, maps and spatial words: every reasonable reading of “straight”, “through”, “opposite” (Window 4), “higher up” and “between floors” (Window 5), “between” on the tram line and on the map (Window 6), “next to” (Window 11), “the lower half of the clock face” (Window 16) and the fast gallery clocks (Window 10) keeps the killer and gives the same single answer. Far-fetched readings that would drop the killer leave nobody, so the slip shows at once.
- The finalists don’t point at the answer: door, district, last till and hour of entry are spread so that the killer’s value is shared by at least two finalists and is never the most common, and all finalists have different names.
- The listing never shows anything from Windows 4–23: their evidence and questions are on the spoiler list, along with the killer, the finalists, the Sealed Check number and the level-2/3 hints.
- Stop list: Agatha Christie and her books, Poirot, Marple, Cluedo/Clue, Knives Out, Glass Onion, The Traitors, Orient Express (and the word Express), Home Alone, Miracle on 34th Street, real department stores (Macy’s, Harrods, Selfridges and others), A Christmas Carol names, anime franchises, the earlier stop lists and the names from case 1 (Ashcombe, Ember Square, Wren, Ambrose).

## Answer (spoiler)

<details><summary>Show</summary>

Verena Pennock, pass 2173, from Old Mint. In at 18:31 by the Tram Door, last till 20 (the Quillon Tea Room). Sealed Check 224.

</details>
