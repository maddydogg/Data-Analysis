# Listing assets: spoiler and format check

Result: **34 of 34 checks passed**

How the spoiler check works: every mockup and every video frame is built from real PDF regions and code-drawn text. The builder records the PDF text layer of each region it places and every string it draws, and scans all of it for the forbidden tokens: the killer's name and ticket, the Sealed Check number, every finalist's name and ticket, the start of every level-2 and level-3 hint, and the solution headings. A control run on the killer's own log page, the solution file and the check page shows that the scanner does catch them.

| # | Check | Result | Detail |
|---|---|---|---|
| 1 | Spoiler list loaded from the verification report | PASS | 95 forbidden tokens: killer name and ticket, Sealed Check number, 26 finalists (names + tickets), 36 level-2/3 hints, solution headings |
| 2 | Control test: the scanner flags the killer's log page, the solution and the check page | PASS | 8 hits in the control sources |
| 3 | Mockup 01-main: 2000x2000 PNG | PASS | (2000, 2000) |
| 4 | Mockup 01-main: no spoilers in any visible text (8 sources) | PASS |  |
| 5 | Mockup 02-whats-inside: 2000x2000 PNG | PASS | (2000, 2000) |
| 6 | Mockup 02-whats-inside: no spoilers in any visible text (8 sources) | PASS |  |
| 7 | Mockup 03-six-documents: 2000x2000 PNG | PASS | (2000, 2000) |
| 8 | Mockup 03-six-documents: no spoilers in any visible text (13 sources) | PASS |  |
| 9 | Mockup 04-inspectors-notebook: 2000x2000 PNG | PASS | (2000, 2000) |
| 10 | Mockup 04-inspectors-notebook: no spoilers in any visible text (2 sources) | PASS |  |
| 11 | Mockup 05-visitor-log-in-progress: 2000x2000 PNG | PASS | (2000, 2000) |
| 12 | Mockup 05-visitor-log-in-progress: no spoilers in any visible text (4 sources) | PASS |  |
| 13 | Mockup 06-three-levels-of-hints: 2000x2000 PNG | PASS | (2000, 2000) |
| 14 | Mockup 06-three-levels-of-hints: no spoilers in any visible text (9 sources) | PASS |  |
| 15 | Mockup 07-sealed-check: 2000x2000 PNG | PASS | (2000, 2000) |
| 16 | Mockup 07-sealed-check: no spoilers in any visible text (7 sources) | PASS |  |
| 17 | Mockup 08-print-or-ipad: 2000x2000 PNG | PASS | (2000, 2000) |
| 18 | Mockup 08-print-or-ipad: no spoilers in any visible text (5 sources) | PASS |  |
| 19 | Mockup 09-who-its-for: 2000x2000 PNG | PASS | (2000, 2000) |
| 20 | Mockup 09-who-its-for: no spoilers in any visible text (6 sources) | PASS |  |
| 21 | Mockup 10-what-you-get: 2000x2000 PNG | PASS | (2000, 2000) |
| 22 | Mockup 10-what-you-get: no spoilers in any visible text (17 sources) | PASS |  |
| 23 | Visitor Log page used in visuals contains neither the killer nor any finalist | PASS | page 60 |
| 24 | Video: every one of 438 frames checked, no spoilers | PASS | 0 frames with hits |
| 25 | Video: 1080x1080, 12-15 s, no sound | PASS | {"seconds": 14.6, "width": 1080, "height": 1080, "audio": false, "fps": "30"} |
| 26 | Delivery folder has exactly 4 files (Etsy allows 5) | PASS | snowfall-at-ember-square_SOLUTION.zip, snowfall-at-ember-square_iPad.pdf, snowfall-at-ember-square_print-A4.pdf, snowfall-at-ember-square_print-US-Letter.pdf |
| 27 | Delivery snowfall-at-ember-square_print-US-Letter.pdf is under 20 MB | PASS | 0.71 MB |
| 28 | Delivery snowfall-at-ember-square_print-A4.pdf is under 20 MB | PASS | 0.71 MB |
| 29 | Delivery snowfall-at-ember-square_iPad.pdf is under 20 MB | PASS | 0.69 MB |
| 30 | Delivery snowfall-at-ember-square_SOLUTION.zip is under 20 MB | PASS | 0.4 MB |
| 31 | Solution ZIP holds the three solution PDFs and is intact | PASS | snowfall-at-ember-square_SOLUTION_print-US-Letter.pdf, snowfall-at-ember-square_SOLUTION_print-A4.pdf, snowfall-at-ember-square_SOLUTION_iPad.pdf |
| 32 | Delivery snowfall-at-ember-square_iPad.pdf is a case book, not a solution | PASS |  |
| 33 | Delivery snowfall-at-ember-square_print-A4.pdf is a case book, not a solution | PASS |  |
| 34 | Delivery snowfall-at-ember-square_print-US-Letter.pdf is a case book, not a solution | PASS |  |

## Files

- listing/mockups/snowfall-at-ember-square_01-main.png
- listing/mockups/snowfall-at-ember-square_02-whats-inside.png
- listing/mockups/snowfall-at-ember-square_03-six-documents.png
- listing/mockups/snowfall-at-ember-square_04-inspectors-notebook.png
- listing/mockups/snowfall-at-ember-square_05-visitor-log-in-progress.png
- listing/mockups/snowfall-at-ember-square_06-three-levels-of-hints.png
- listing/mockups/snowfall-at-ember-square_07-sealed-check.png
- listing/mockups/snowfall-at-ember-square_08-print-or-ipad.png
- listing/mockups/snowfall-at-ember-square_09-who-its-for.png
- listing/mockups/snowfall-at-ember-square_10-what-you-get.png
- listing/mockups/snowfall-at-ember-square_overview.png
- listing/video/snowfall-at-ember-square_listing-video_1080.mp4
- delivery/snowfall-at-ember-square_SOLUTION.zip
- delivery/snowfall-at-ember-square_iPad.pdf
- delivery/snowfall-at-ember-square_print-A4.pdf
- delivery/snowfall-at-ember-square_print-US-Letter.pdf
