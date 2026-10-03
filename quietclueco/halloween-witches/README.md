# Full Moon over Morrowmere — QuietClueCo case No. 3

A cozy witch-village "find the killer" elimination puzzle for Halloween, set at the Moon Fair in the fictional village of Morrowmere. There are 6,000 visitors, 18 clues and one killer. It plays with 1–4 players and takes about 90–150 minutes. Spooky, not gory: the witches are ordinary villagers (herbalists, candle-makers, a tea-leaf reader), with no mockery of real beliefs and no references to real witch trials.

It is built on the same engine as case No. 2 (`../halloween-monster`), with its own story, world, clues, hints, six new documents and new artwork.

## Files

| Path | What it is |
|---|---|
| `print/full-moon-over-morrowmere_print-US-Letter.pdf` | Case book for printing, US Letter (139 pages) |
| `print/full-moon-over-morrowmere_print-A4.pdf` | Case book for printing, A4 (129 pages) |
| `ipad/full-moon-over-morrowmere_iPad.pdf` | Case book for Goodnotes / Notability, 768×1024 portrait, clickable contents and bookmarks (117 pages) |
| `solution/…_SOLUTION_*.pdf` | "The Envelope": answer, epilogue, step-by-step solution, finalists and the elimination index for all 6,000 tickets |
| `delivery/` | The 4 files to upload to Etsy: 3 case-book PDFs and `full-moon-over-morrowmere_SOLUTION.zip` |
| `listing/mockups/` | 10 listing images, 2000×2000 JPG, plus an overview sheet |
| `listing/video/` | Listing video: old-film trailer `full-moon-over-morrowmere_old-film-trailer_1080.mp4` (1080×1080, 14.0 s, 30 fps, no sound) with a poster frame and a storyboard |
| `listing/etsy_listing.md` | Title, description, price and 30 tag candidates with Listadum data (final tags not chosen yet) |
| `listing/spoiler_check.md` / `.json` | Spoiler and format check of every mockup, every video frame and the delivery folder |
| `verification_report.md` / `.json` | Code verification of the puzzle and the PDFs |
| `previews/<version>/page-NNN.png` | PNG preview of every page |
| `src/` | Generator: `case.py` (story, world, clues), `hints.py`, `generate.py`, `verify.py`, `render.py`, `build.py` |
| `listing/src/` | Listing kit: `poster.py` (poster art), `make_cover_art.py`, `mockups.py`, `video_trailer.py`, `delivery.py`, `build_listing.py` |

## Rebuild

```bash
pip install reportlab pymupdf fonttools pillow imageio-ffmpeg
cd listing/src && python3 make_cover_art.py    # cover art for Letter, A4 and iPad -> src/art/
cd ../../src && python3 build.py               # case book, solution, checks, previews
cd ../listing/src && python3 build_listing.py  # mockups, video, delivery folder, spoiler check
```

Both builds are deterministic and exit with a non-zero code if any check fails.

## The six documents

1. Fair map: the green, four lanes of stalls, four entrances, the Hob Stones in the meadow and Quell's Apothecary.
2. Stall directory: 36 stalls, their lanes and what they sell.
3. The Book of Brews: nine brews and their ingredients (with a trap brew).
4. Moon-watcher's log: when the full moon was clear and when cloud hid it.
5. Mother Meridew's reading book and Bryony's note.
6. The apothecary's day ledger and the village carrier's weekly rounds.

No weather log, receipt or bus timetable this time; the evidence works through the moon, tea-leaf dregs, recipes, the stone circle and the carrier's rounds.

## Checks added for this case

- The case-2 stop list plus the witch stop list from the brief (Hocus Pocus, Sanderson, Practical Magic, Owens, Sabrina, Charmed, Halliwell, Wicked, Elphaba, Glinda, Agatha All Along, The Craft, Harry Potter, Hogwarts, Quidditch, Hermione, Discworld, Weatherwax, Kiki, Maleficent, Ursula, Winifred, Salem) are searched as whole words in every text and both name pools. Famous fictional witches' first names are also kept out of the pools.
- Finalists don't point at the answer: the generator spreads the shortlist evenly over entrances, villages, stalls, lanes and entry hours, and `verify.py` checks that for each of these the killer's value is shared by at least two finalists, is never the single most common value, and that no value covers more than half the shortlist.

## Design notes

- Cover and listing images use an old horror-mystery one-sheet style in the case palette (plum #2B1B3D, aubergine #4A2C5E, amethyst #8E5BB5, candle gold #E3A64B, moon parchment #EDE6D6, sage #8FA382). Only silhouettes and objects appear: a full moon, a figure in a pointed hat seen from behind, crows, rooftops, the standing stones, a cauldron, a hand holding a candle and moon phases. No faces, no studio logos, no composition of any real poster. Images 02–09 are lobby cards with a real page of the case inside.
- Inside pages stay light and use Fraunces and Nunito. Poster fonts (Abril Fatface, Bebas Neue, Oswald, IM Fell, Cinzel: SIL OFL) are in `listing/src/fonts_horror/` with their licence files.
- Place and character names (Morrowmere, Full Moon over Morrowmere, Hollis Drummond, Bryony Fettle, Mother Meridew, Barnaby Quell, Tobias Wick) were checked in EverBee and a web search before use. "Moonfall" was dropped because it is a 2022 film title.

## Fix after a player test (before publication)

A test player read Bryony's note ("came over the meadow and straight through the Hob Stones") as "straight along one path". That path leads to Mill Stile, but the killer came in at Orchard Gap, so a player who kept only Mill would cross out the killer at Evidence A.

**Changes:**

- **Bryony's note** now reads: "She came in off the drove road by the stone path, through the Hob Stones, under a full moon so bright her pin flashed like a new coin." It has no "straight" and names no entrance. Evidence A is unchanged: Mill Stile or Orchard Gap.
- **Fair map.** The drove road now meets the Hob Stones at 45°, so neither branch is "straight on". Both branches after the stones are labelled ("path to Mill Stile", "path to Orchard Gap") and have matching arrowheads.
- **Level-1 hint, Evidence A:** a path can fork, so check every entrance it leads to.
- **Level-1 hint, Evidence C:** the reading time is not the time the lady came in.
- **New checks in `verify.py`:**
  - "Mill only" leaves 0 visitors, so the mistake shows at once.
  - The note has no "straight" and names no entrance.
  - The hints catch the misreading.
  - Every PDF prints the corrected note and both fork labels.
- **Still true after the fix:** the answer is unique, all 18 clues are needed, and the shortlist has no pattern.
- **Rebuilt:** the PDFs, previews, delivery folder, mockups and the presentation video. The bundle (`../bundle-spooky-season`) was rebuilt from the corrected case.

## Answer (spoiler)

<details><summary>Show</summary>

Edna Elworthy, ticket 4073, from Hatherby. She came in at 19:23 by Orchard Gap, and her last stall was 21 (The Ember Pot, Rosehip Ember). The Sealed Check number is 523.
</details>
