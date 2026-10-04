# Listing assets: spoiler and format check

Result: **42 of 42 checks passed**

How it works: every mockup and every video frame is built from real PDF regions and code-drawn text. The builder records the text layer of every region it places and every string it draws, and scans it for forbidden tokens: the killer's name and pass, the Sealed Check number, every finalist's name and pass, the start of every level-2 and level-3 hint, the evidence and question of every window from 4 to 23, and the solution headings. A control run on the killer's register page, the solution and Window 12 shows the scanner catches them.

| # | Check | Result | Detail |
|---|---|---|---|
| 1 | Spoiler list loaded from the verification report | PASS | 149 forbidden tokens: killer name and pass, Sealed Check number, 30 finalists (names + passes), level-2/3 hints, the evidence and question of every window from 4 to 23, solution headings |
| 2 | Control test: the scanner flags the killer's register page, the solution and a later window | PASS | 16 hits |
| 3 | Mockup 01-main: 2000x2000 JPG | PASS | 855 KB |
| 4 | Mockup 01-main: no spoilers in any visible text (8 sources) | PASS |  |
| 5 | Mockup 02-the-calendar: 2000x2000 JPG | PASS | 351 KB |
| 6 | Mockup 02-the-calendar: no spoilers in any visible text (9 sources) | PASS |  |
| 7 | Mockup 03-day-1-the-case: 2000x2000 JPG | PASS | 432 KB |
| 8 | Mockup 03-day-1-the-case: no spoilers in any visible text (5 sources) | PASS |  |
| 9 | Mockup 04-day-2-the-register: 2000x2000 JPG | PASS | 472 KB |
| 10 | Mockup 04-day-2-the-register: no spoilers in any visible text (5 sources) | PASS |  |
| 11 | Mockup 05-day-3-first-clue: 2000x2000 JPG | PASS | 360 KB |
| 12 | Mockup 05-day-3-first-clue: no spoilers in any visible text (6 sources) | PASS |  |
| 13 | Mockup 06-print-and-fold: 2000x2000 JPG | PASS | 368 KB |
| 14 | Mockup 06-print-and-fold: no spoilers in any visible text (8 sources) | PASS |  |
| 15 | Mockup 07-ipad-calendar: 2000x2000 JPG | PASS | 265 KB |
| 16 | Mockup 07-ipad-calendar: no spoilers in any visible text (4 sources) | PASS |  |
| 17 | Mockup 08-who-its-for: 2000x2000 JPG | PASS | 372 KB |
| 18 | Mockup 08-who-its-for: no spoilers in any visible text (9 sources) | PASS |  |
| 19 | Mockup 09-whats-inside: 2000x2000 JPG | PASS | 367 KB |
| 20 | Mockup 09-whats-inside: no spoilers in any visible text (19 sources) | PASS |  |
| 21 | Mockup 10-checked-by-code: 2000x2000 JPG | PASS | 278 KB |
| 22 | Mockup 10-checked-by-code: no spoilers in any visible text (14 sources) | PASS |  |
| 23 | Image 01 carries the title, 24 days, PRINTABLE and iPad | PASS | all present |
| 24 | Only Windows 1–3 appear in the mockups | PASS | [1, 2, 3] |
| 25 | Register page used in the visuals holds neither the killer nor any finalist | PASS | page 25 |
| 26 | Video trailer: every one of 405 frames checked, no spoilers | PASS | 0 frames with hits |
| 27 | Video trailer: 1080x1080, 12–15 s, no sound | PASS | {"seconds": 13.5, "width": 1080, "height": 1080, "audio": false, "fps": "30"} |
| 28 | Video presentation: every one of 420 frames checked, no spoilers | PASS | 0 frames with hits |
| 29 | Video presentation: 1080x1080, 12–15 s, no sound | PASS | {"seconds": 14.0, "width": 1080, "height": 1080, "audio": false, "fps": "30"} |
| 30 | Delivery folder has exactly 4 files (Etsy allows 5) | PASS | the-windows-at-quillons_SOLUTION.zip, the-windows-at-quillons_iPad.pdf, the-windows-at-quillons_print-A4.pdf, the-windows-at-quillons_print-US-Letter.pdf |
| 31 | Delivery the-windows-at-quillons_print-US-Letter.pdf is under 20 MB | PASS | 5.54 MB |
| 32 | Delivery the-windows-at-quillons_print-A4.pdf is under 20 MB | PASS | 5.56 MB |
| 33 | Delivery the-windows-at-quillons_iPad.pdf is under 20 MB | PASS | 5.43 MB |
| 34 | Delivery the-windows-at-quillons_SOLUTION.zip is under 20 MB | PASS | 0.32 MB |
| 35 | Solution ZIP holds the solution in all three formats and is intact | PASS | the-windows-at-quillons_SOLUTION_print-US-Letter.pdf, the-windows-at-quillons_SOLUTION_print-A4.pdf, the-windows-at-quillons_SOLUTION_iPad.pdf |
| 36 | Delivery the-windows-at-quillons_iPad.pdf is the calendar, not the solution, and never names the killer outside the register | PASS |  |
| 37 | Delivery the-windows-at-quillons_print-A4.pdf is the calendar, not the solution, and never names the killer outside the register | PASS |  |
| 38 | Delivery the-windows-at-quillons_print-US-Letter.pdf is the calendar, not the solution, and never names the killer outside the register | PASS |  |
| 39 | Archive the-windows-at-quillons_files-for-sale.zip written | PASS | 13.7 MB |
| 40 | Archive the-windows-at-quillons_10-mockups-JPG.zip written | PASS | 4.0 MB |
| 41 | Archive the-windows-at-quillons_trailer_1080.mp4 written | PASS | 18.6 MB |
| 42 | Archive the-windows-at-quillons_calendar-presentation_1080.mp4 written | PASS | 8.7 MB |
