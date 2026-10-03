# Listing assets: spoiler and format check

Result: **35 of 35 checks passed**

How the spoiler check works: every mockup and every video frame is built from real PDF regions and code-drawn text. The builder records the PDF text layer of each region it places and every string it draws, and scans all of it for the forbidden tokens: the killer's name and ticket, the Sealed Check number, every finalist's name and ticket, the start of every level-2 and level-3 hint, and the solution headings. A control run on the killer's own log page, the solution file and the check page shows that the scanner does catch them.

| # | Check | Result | Detail |
|---|---|---|---|
| 1 | Spoiler list loaded from the verification report | PASS | 91 forbidden tokens: killer name and ticket, Sealed Check number, 24 finalists (names + tickets), 36 level-2/3 hints, solution headings |
| 2 | Control test: the scanner flags the killer's log page, the solution and the check page | PASS | 9 hits in the control sources |
| 3 | Mockup 01-main: 2000x2000 JPG | PASS | (2000, 2000), 1103 KB |
| 4 | Mockup 01-main: no spoilers in any visible text (8 sources) | PASS |  |
| 5 | Mockup 02-six-documents: 2000x2000 JPG | PASS | (2000, 2000), 600 KB |
| 6 | Mockup 02-six-documents: no spoilers in any visible text (17 sources) | PASS |  |
| 7 | Mockup 03-fair-map: 2000x2000 JPG | PASS | (2000, 2000), 442 KB |
| 8 | Mockup 03-fair-map: no spoilers in any visible text (7 sources) | PASS |  |
| 9 | Mockup 04-inspectors-notebook: 2000x2000 JPG | PASS | (2000, 2000), 506 KB |
| 10 | Mockup 04-inspectors-notebook: no spoilers in any visible text (6 sources) | PASS |  |
| 11 | Mockup 05-visitor-log-in-progress: 2000x2000 JPG | PASS | (2000, 2000), 536 KB |
| 12 | Mockup 05-visitor-log-in-progress: no spoilers in any visible text (7 sources) | PASS |  |
| 13 | Mockup 06-three-levels-of-hints: 2000x2000 JPG | PASS | (2000, 2000), 470 KB |
| 14 | Mockup 06-three-levels-of-hints: no spoilers in any visible text (10 sources) | PASS |  |
| 15 | Mockup 07-sealed-check: 2000x2000 JPG | PASS | (2000, 2000), 483 KB |
| 16 | Mockup 07-sealed-check: no spoilers in any visible text (10 sources) | PASS |  |
| 17 | Mockup 08-print-or-ipad: 2000x2000 JPG | PASS | (2000, 2000), 440 KB |
| 18 | Mockup 08-print-or-ipad: no spoilers in any visible text (7 sources) | PASS |  |
| 19 | Mockup 09-who-its-for: 2000x2000 JPG | PASS | (2000, 2000), 506 KB |
| 20 | Mockup 09-who-its-for: no spoilers in any visible text (12 sources) | PASS |  |
| 21 | Mockup 10-what-you-get: 2000x2000 JPG | PASS | (2000, 2000), 1165 KB |
| 22 | Mockup 10-what-you-get: no spoilers in any visible text (18 sources) | PASS |  |
| 23 | Image 01 carries the title, Find the killer, 6,000 suspects / 6 documents / 1 killer, PRINTABLE and iPad | PASS | all present |
| 24 | Visitor Log page used in visuals contains neither the killer nor any finalist | PASS | page 48 |
| 25 | Video: every one of 420 frames checked, no spoilers | PASS | 0 frames with hits |
| 26 | Video: 1080x1080, 12-15 s, no sound | PASS | {"seconds": 14.0, "width": 1080, "height": 1080, "audio": false, "fps": "30"} |
| 27 | Delivery folder has exactly 4 files (Etsy allows 5) | PASS | full-moon-over-morrowmere_SOLUTION.zip, full-moon-over-morrowmere_iPad.pdf, full-moon-over-morrowmere_print-A4.pdf, full-moon-over-morrowmere_print-US-Letter.pdf |
| 28 | Delivery full-moon-over-morrowmere_print-US-Letter.pdf is under 20 MB | PASS | 2.54 MB |
| 29 | Delivery full-moon-over-morrowmere_print-A4.pdf is under 20 MB | PASS | 2.69 MB |
| 30 | Delivery full-moon-over-morrowmere_iPad.pdf is under 20 MB | PASS | 1.73 MB |
| 31 | Delivery full-moon-over-morrowmere_SOLUTION.zip is under 20 MB | PASS | 0.39 MB |
| 32 | Solution ZIP holds the three solution PDFs and is intact | PASS | full-moon-over-morrowmere_SOLUTION_print-US-Letter.pdf, full-moon-over-morrowmere_SOLUTION_print-A4.pdf, full-moon-over-morrowmere_SOLUTION_iPad.pdf |
| 33 | Delivery full-moon-over-morrowmere_iPad.pdf is a case book, not a solution | PASS |  |
| 34 | Delivery full-moon-over-morrowmere_print-A4.pdf is a case book, not a solution | PASS |  |
| 35 | Delivery full-moon-over-morrowmere_print-US-Letter.pdf is a case book, not a solution | PASS |  |

## Files

- listing/mockups/full-moon-over-morrowmere_01-main.jpg
- listing/mockups/full-moon-over-morrowmere_02-six-documents.jpg
- listing/mockups/full-moon-over-morrowmere_03-fair-map.jpg
- listing/mockups/full-moon-over-morrowmere_04-inspectors-notebook.jpg
- listing/mockups/full-moon-over-morrowmere_05-visitor-log-in-progress.jpg
- listing/mockups/full-moon-over-morrowmere_06-three-levels-of-hints.jpg
- listing/mockups/full-moon-over-morrowmere_07-sealed-check.jpg
- listing/mockups/full-moon-over-morrowmere_08-print-or-ipad.jpg
- listing/mockups/full-moon-over-morrowmere_09-who-its-for.jpg
- listing/mockups/full-moon-over-morrowmere_10-what-you-get.jpg
- listing/mockups/full-moon-over-morrowmere_overview.jpg
- listing/video/full-moon-over-morrowmere_old-film-trailer_1080.mp4
- listing/video/full-moon-over-morrowmere_old-film-trailer_poster.jpg
- delivery/full-moon-over-morrowmere_SOLUTION.zip
- delivery/full-moon-over-morrowmere_iPad.pdf
- delivery/full-moon-over-morrowmere_print-A4.pdf
- delivery/full-moon-over-morrowmere_print-US-Letter.pdf
