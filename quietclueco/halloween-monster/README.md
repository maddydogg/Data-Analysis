# Storm over Corvenmoor — QuietClueCo case No. 2

A spooky "find the killer" elimination puzzle set on Monster Night at a castle, for Halloween. There are 6,000 visitors, 18 clues and one killer. It plays with 1–4 players and takes about 90–150 minutes.

It is built on the same engine as case No. 1 (`../christmas-market`), with its own story, world, clues, hints, documents and artwork.

## Files

| Path | What it is |
|---|---|
| `print/storm-over-corvenmoor_print-US-Letter.pdf` | Case book for printing, US Letter (138 pages) |
| `print/storm-over-corvenmoor_print-A4.pdf` | Case book for printing, A4 (130 pages) |
| `ipad/storm-over-corvenmoor_iPad.pdf` | Case book for Goodnotes / Notability, 768×1024 portrait, clickable contents and bookmarks (117 pages) |
| `solution/…_SOLUTION_*.pdf` | "The Envelope": answer, epilogue, step-by-step solution, finalists and the elimination index for all 6,000 tickets |
| `delivery/` | The 4 files to upload to Etsy: 3 case-book PDFs and `storm-over-corvenmoor_SOLUTION.zip` |
| `listing/mockups/` | 10 listing images, 2000×2000, plus an overview sheet |
| `listing/video/` | Listing video: the found-footage trailer `storm-over-corvenmoor_found-footage-trailer_1080.mp4` (1080×1080, 14.9 s, no sound) with a poster frame and storyboard; the earlier noir video and the five trailer style concepts are kept for reference |
| `listing/etsy_listing.md` | Title, 13 tags, price and description, ready to paste |
| `listing/spoiler_check.md` / `.json` | Spoiler and format check of every mockup, every video frame and the delivery folder |
| `verification_report.md` / `.json` | Code verification of the puzzle and the PDFs |
| `previews/<version>/page-NNN.png` | PNG preview of every page |
| `src/` | Generator: `case.py` (story, world, clues), `hints.py`, `generate.py`, `verify.py`, `render.py`, `build.py` |
| `listing/src/` | Listing kit: `mockups.py`, `video_found_footage.py` (trailer), `make_cover_art.py`, `horror_heroes.py`, `trailer_concepts.py`, `delivery.py`, `build_listing.py` |

## Rebuild

```bash
pip install reportlab pymupdf fonttools pillow imageio-ffmpeg
cd listing/src && python3 make_cover_art.py    # cover art for Letter, A4 and iPad -> src/art/
cd ../../src && python3 build.py               # case book, solution, checks, previews
cd ../listing/src && python3 build_listing.py  # mockups, video, delivery folder, spoiler check
```

Both builds are deterministic and exit with a non-zero code if any check fails.

## Design notes

- Cover and listing images use a 1930s monster-movie one-sheet style: a hooded figure with glowing eyes over the castle, lightning, a tilted yellow title with a red block shadow, a billing block and aged paper. The cover art is rendered for each page shape (`src/art/cover_*.jpg`, about 250 dpi for print) and placed full-bleed on page 1; the title is also there as invisible text, so the PDF stays searchable.
- Poster fonts (Abril Fatface, Bebas Neue, Oswald, IM Fell, Cinzel, UnifrakturMaguntia: SIL OFL; Special Elite: Apache 2.0) are in `listing/src/fonts_horror/` with their licence files.
- `listing/mockups/horror-heroes/` holds the five cover concepts that were compared; concept 1 was chosen.

- The monster is our own design: a stitched green mask with shaggy hair and copper coils above the ears. There are no neck bolts or flat-topped head, and no names from existing films, books or competitor listings. `verify.py` checks the text for a list of banned names.
- The place name Corvenmoor was checked against Etsy listings (via EverBee) and a web search before use.

## Answer (spoiler)

<details><summary>Show</summary>

Isabel Pettit, ticket 2719, from Gloamford. She entered at 19:17 through the West Gate, and her last booth was 33. The Sealed Check number is 045.
</details>
