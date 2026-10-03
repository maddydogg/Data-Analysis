# Storm & Moon Double Feature — QuietClueCo bundle

A bundle of two finished cases, styled as a vintage cinema double feature. It adds no new puzzles.

- Feature 1: **Storm over Corvenmoor** (case No. 2, `../halloween-monster`)
- Feature 2: **Full Moon over Morrowmere** (case No. 3, `../halloween-witches`)

The name has no "Halloween" in it, in the file names or on the cover, so the bundle keeps selling after 31 October. Two other names were considered:

- "Midnight Double Feature" is already a film series and a podcast.
- "The Late Show Double Feature" collides with a TV show.

"Storm & Moon Double Feature" had no matches in a web search, and EverBee shows no mystery puzzles under "double feature".

## Files for sale (`delivery/`, 4 of Etsy's 5)

| File | What it is |
|---|---|
| `bundle_print-US-Letter.pdf` | Bundle cover, programme (contents), then both case books in full, without solutions (278 pages) |
| `bundle_print-A4.pdf` | The same in A4 (261 pages) |
| `bundle_iPad.pdf` | The same for iPad, 768×1024 (236 pages) |
| `bundle_SOLUTIONS.zip` | The 6 solution files: Letter, A4 and iPad for each case |

Inside the bundle PDFs:

- **Page 1** is a double-feature poster with both case covers. These are re-rendered without the word "Halloween" by `src/make_case_covers.py`.
- **Page 2** is the programme: one clickable line for every section of both cases, with PDF page numbers.
- **Bookmarks** go cover → programme → one bookmark per case, with every bookmark of that case nested under it.
- **The case books are unchanged.** Their own contents pages and links still work, and they keep their own footer page numbers. The programme page explains this.

## Listing (`listing/`)

- `mockups/`: 10 images, 2000×2000 JPG, plus an overview sheet:
  - 01 is the double-feature poster.
  - 02–09 are lobby cards with real pages of both cases.
  - 10 is "What you get".
- `etsy_listing.md`: the title, a price suggestion, the description with a "Why the double feature" section, and 26 tag candidates with Listadum data. Final tags are not chosen yet.
- `spoiler_check.md` / `.json`: checks of the images (27/27).
- No video. It will be made separately in Veo from the mockups.

## Checks

- `bundle_check.md` / `.json` — 37/37 PASS:
  - no solution content in the PDFs;
  - each killer's name appears only once, on their own line of the Visitor Log;
  - every programme link, case link and bookmark lands on the right page;
  - both case books are included whole;
  - every file is under 20 MB;
  - the ZIP is intact.
- `listing/spoiler_check.md` — 27/27 PASS. There are 0 spoiler hits for either case in any image. Tokens checked:
  - killers' names and tickets;
  - Sealed Check numbers;
  - all finalists;
  - level-2 and level-3 hints;
  - solution headings.

  A control run shows the scanner does catch them.

## Rebuild

```bash
cd src
python3 make_case_covers.py     # the two case covers without "Halloween" -> art/case_*.jpg
python3 art.py                  # bundle cover for Letter, A4, iPad -> art/cover_*.jpg
python3 build_bundle.py         # delivery/ (4 files) + bundle_check.md
cd ../listing/src && python3 build_listing.py   # 10 mockups + spoiler_check.md
```

## Answers (spoiler)

<details><summary>Show</summary>

- Storm over Corvenmoor: Isabel Pettit, ticket 2719. Sealed Check 045.
- Full Moon over Morrowmere: Edna Elworthy, ticket 4073. Sealed Check 523.
</details>
