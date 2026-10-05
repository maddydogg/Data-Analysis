# Listing assets: spoiler and format check

Result: **43 of 43 checks passed**

How it works: every mockup and every video frame is built from real PDF regions and code-drawn text. The builder records the text layer of every region it places and every string it draws, and scans it for forbidden tokens: the killer's name and pass, the Sealed Check number, every finalist's name and pass, the start of every level-2 and level-3 hint, the evidence and question of every window from 4 to 23, and the solution headings. A control run on the killer's register page, the solution and Window 12 shows the scanner catches them. Every drawn string and video caption is also run through the case's stop list.

| # | Check | Result | Detail |
|---|---|---|---|
| 1 | Spoiler list loaded from the verification report | PASS | 149 forbidden tokens: killer name and pass, Sealed Check number, 30 finalists (names + passes), level-2/3 hints, the evidence and question of every window from 4 to 23, solution headings |
| 2 | Control test: the scanner flags the killer's register page, the solution and a later window | PASS | 16 hits |
| 3 | Mockup 01-main: 2000x2000 JPG | PASS | 851 KB |
| 4 | Mockup 01-main: no spoilers in any visible text (10 sources) | PASS |  |
| 5 | Mockup 02-the-calendar: 2000x2000 JPG | PASS | 752 KB |
| 6 | Mockup 02-the-calendar: no spoilers in any visible text (8 sources) | PASS |  |
| 7 | Mockup 03-day-1-the-case: 2000x2000 JPG | PASS | 818 KB |
| 8 | Mockup 03-day-1-the-case: no spoilers in any visible text (6 sources) | PASS |  |
| 9 | Mockup 04-day-2-the-register: 2000x2000 JPG | PASS | 818 KB |
| 10 | Mockup 04-day-2-the-register: no spoilers in any visible text (6 sources) | PASS |  |
| 11 | Mockup 05-day-3-first-clue: 2000x2000 JPG | PASS | 723 KB |
| 12 | Mockup 05-day-3-first-clue: no spoilers in any visible text (7 sources) | PASS |  |
| 13 | Mockup 06-print-and-fold: 2000x2000 JPG | PASS | 718 KB |
| 14 | Mockup 06-print-and-fold: no spoilers in any visible text (9 sources) | PASS |  |
| 15 | Mockup 07-ipad-calendar: 2000x2000 JPG | PASS | 756 KB |
| 16 | Mockup 07-ipad-calendar: no spoilers in any visible text (5 sources) | PASS |  |
| 17 | Mockup 08-who-its-for: 2000x2000 JPG | PASS | 917 KB |
| 18 | Mockup 08-who-its-for: no spoilers in any visible text (9 sources) | PASS |  |
| 19 | Mockup 09-whats-inside: 2000x2000 JPG | PASS | 841 KB |
| 20 | Mockup 09-whats-inside: no spoilers in any visible text (15 sources) | PASS |  |
| 21 | Mockup 10-checked-by-code: 2000x2000 JPG | PASS | 667 KB |
| 22 | Mockup 10-checked-by-code: no spoilers in any visible text (14 sources) | PASS |  |
| 23 | Image 01 carries the title, 24 days, PRINTABLE and iPad | PASS | all present |
| 24 | Only Windows 1–3 appear in the mockups | PASS | [1, 2, 3] |
| 25 | Register page used in the visuals holds neither the killer nor any finalist | PASS | page 25 |
| 26 | Video trailer: every one of 405 frames checked, no spoilers | PASS | 0 frames with hits |
| 27 | Video trailer: 1080x1080, 12–15 s, no sound | PASS | {"seconds": 13.5, "width": 1080, "height": 1080, "audio": false, "fps": "30"} |
| 28 | Video presentation: every one of 420 frames checked, no spoilers | PASS | 0 frames with hits |
| 29 | Video presentation: 1080x1080, 12–15 s, no sound | PASS | {"seconds": 14.0, "width": 1080, "height": 1080, "audio": false, "fps": "30"} |
| 30 | Stop list: no borrowed brands, titles or real stores in any drawn text or video caption (whole words) | PASS | 95 strings checked |
| 31 | Delivery folder has exactly 4 files (Etsy allows 5) | PASS | the-windows-at-quillons_SOLUTION.zip, the-windows-at-quillons_iPad.pdf, the-windows-at-quillons_print-A4.pdf, the-windows-at-quillons_print-US-Letter.pdf |
| 32 | Delivery the-windows-at-quillons_print-US-Letter.pdf is under 20 MB | PASS | 5.65 MB |
| 33 | Delivery the-windows-at-quillons_print-A4.pdf is under 20 MB | PASS | 5.67 MB |
| 34 | Delivery the-windows-at-quillons_iPad.pdf is under 20 MB | PASS | 5.53 MB |
| 35 | Delivery the-windows-at-quillons_SOLUTION.zip is under 20 MB | PASS | 0.32 MB |
| 36 | Solution ZIP holds the solution in all three formats and is intact | PASS | the-windows-at-quillons_SOLUTION_print-US-Letter.pdf, the-windows-at-quillons_SOLUTION_print-A4.pdf, the-windows-at-quillons_SOLUTION_iPad.pdf |
| 37 | Delivery the-windows-at-quillons_iPad.pdf is the calendar, not the solution, and never names the killer outside the register | PASS |  |
| 38 | Delivery the-windows-at-quillons_print-A4.pdf is the calendar, not the solution, and never names the killer outside the register | PASS |  |
| 39 | Delivery the-windows-at-quillons_print-US-Letter.pdf is the calendar, not the solution, and never names the killer outside the register | PASS |  |
| 40 | Archive the-windows-at-quillons_files-for-sale.zip written | PASS | 13.9 MB |
| 41 | Archive the-windows-at-quillons_10-mockups-JPG.zip written | PASS | 7.7 MB |
| 42 | Archive the-windows-at-quillons_trailer_1080.mp4 written | PASS | 18.4 MB |
| 43 | Archive the-windows-at-quillons_calendar-presentation_1080.mp4 written | PASS | 11.7 MB |
