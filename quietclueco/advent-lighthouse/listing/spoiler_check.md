# Listing assets: spoiler and format check

Result: **46 of 46 checks passed**

How it works: every mockup and every video frame is built from real PDF regions and code-drawn text. The builder records the text layer of every region it places and every string it draws, and scans it for forbidden tokens: the killer's name and tally, the Sealed Check number, every finalist's name and tally, the start of every level-2 and level-3 hint, the journal entry, the pinned papers and the question of every window from 4 to 23, and the solution headings. A control run on the killer's Sound Book page, the solution and Window 12 shows the scanner catches them. Every drawn string and video caption is also run through the case's stop list.

| # | Check | Result | Detail |
|---|---|---|---|
| 1 | Spoiler list loaded from the verification report | PASS | 193 forbidden tokens: killer name and tally, Sealed Check number, 30 finalists (names + tallies), level-2/3 hints, the journal entry, papers and question of every window from 4 to 23, solution headings |
| 2 | Control test: the scanner flags the killer's Sound Book page, the solution and a later window | PASS | 20 hits |
| 3 | Mockup 01-main: 2000x2000 JPG | PASS | 441 KB |
| 4 | Mockup 01-main: no spoilers in any visible text (6 sources) | PASS |  |
| 5 | Mockup 02-the-calendar: 2000x2000 JPG | PASS | 462 KB |
| 6 | Mockup 02-the-calendar: no spoilers in any visible text (9 sources) | PASS |  |
| 7 | Mockup 03-day-1-the-case: 2000x2000 JPG | PASS | 481 KB |
| 8 | Mockup 03-day-1-the-case: no spoilers in any visible text (7 sources) | PASS |  |
| 9 | Mockup 04-day-2-the-sound-book: 2000x2000 JPG | PASS | 635 KB |
| 10 | Mockup 04-day-2-the-sound-book: no spoilers in any visible text (6 sources) | PASS |  |
| 11 | Mockup 05-day-3-first-lead: 2000x2000 JPG | PASS | 445 KB |
| 12 | Mockup 05-day-3-first-lead: no spoilers in any visible text (7 sources) | PASS |  |
| 13 | Mockup 06-print-and-fold: 2000x2000 JPG | PASS | 430 KB |
| 14 | Mockup 06-print-and-fold: no spoilers in any visible text (9 sources) | PASS |  |
| 15 | Mockup 07-ipad-calendar: 2000x2000 JPG | PASS | 475 KB |
| 16 | Mockup 07-ipad-calendar: no spoilers in any visible text (5 sources) | PASS |  |
| 17 | Mockup 08-who-its-for: 2000x2000 JPG | PASS | 414 KB |
| 18 | Mockup 08-who-its-for: no spoilers in any visible text (9 sources) | PASS |  |
| 19 | Mockup 09-whats-inside: 2000x2000 JPG | PASS | 474 KB |
| 20 | Mockup 09-whats-inside: no spoilers in any visible text (15 sources) | PASS |  |
| 21 | Mockup 10-checked-by-code: 2000x2000 JPG | PASS | 374 KB |
| 22 | Mockup 10-checked-by-code: no spoilers in any visible text (14 sources) | PASS |  |
| 23 | Image 01 carries the title, 24 days, PRINTABLE and iPad | PASS | all present |
| 24 | Only Windows 1–3 appear in the mockups | PASS | [1, 2, 3] |
| 25 | Sound Book page used in the visuals holds neither the killer nor any finalist | PASS | page 35 |
| 26 | Video trailer: every one of 420 frames checked, no spoilers | PASS | 0 frames with hits |
| 27 | Video trailer: 1080x1080, 12–15 s, no sound | PASS | {"seconds": 14.0, "width": 1080, "height": 1080, "audio": false, "fps": "30"} |
| 28 | Video trailer: captions use evidence / lead, never the stop-listed word for it | PASS | 2,400 TRAVELLERS. 24 DAYS. ONE RED CAP.; CANDLEHOLM, DECEMBER; ON CHRISTMAS EVE THE LAMP DID NOT COME ON; SOMEONE IN A RED CAP KEPT COMING BACK; THE KEEPER WROTE EVERYTHING DOWN |
| 29 | Video presentation: every one of 420 frames checked, no spoilers | PASS | 0 frames with hits |
| 30 | Video presentation: 1080x1080, 12–15 s, no sound | PASS | {"seconds": 14.0, "width": 1080, "height": 1080, "audio": false, "fps": "30"} |
| 31 | Video presentation: captions use evidence / lead, never the stop-listed word for it | PASS | DAY 1: THE CASE, THE TOWER, THE CHART; DAY 2: THE SOUND BOOK. CROSS THEM OUT; DAYS 3–23: A JOURNAL PAGE AND A NEW LEAD EACH DAY; OPEN ONE WINDOW A DAY; PRINT AND FOLD, OR TAP ON iPAD |
| 32 | Stop list: no borrowed brands, titles, real lighthouses or earlier names in any drawn text or video caption (whole words) | PASS | 86 strings checked |
| 33 | Delivery folder has exactly 4 files (Etsy allows 5) | PASS | the-keeper-of-candleholm_SOLUTION.zip, the-keeper-of-candleholm_iPad.pdf, the-keeper-of-candleholm_print-A4.pdf, the-keeper-of-candleholm_print-US-Letter.pdf |
| 34 | Delivery the-keeper-of-candleholm_print-US-Letter.pdf is under 20 MB | PASS | 2.87 MB |
| 35 | Delivery the-keeper-of-candleholm_print-A4.pdf is under 20 MB | PASS | 2.88 MB |
| 36 | Delivery the-keeper-of-candleholm_iPad.pdf is under 20 MB | PASS | 2.93 MB |
| 37 | Delivery the-keeper-of-candleholm_SOLUTION.zip is under 20 MB | PASS | 0.32 MB |
| 38 | Solution ZIP holds the solution in all three formats and is intact | PASS | the-keeper-of-candleholm_SOLUTION_print-US-Letter.pdf, the-keeper-of-candleholm_SOLUTION_print-A4.pdf, the-keeper-of-candleholm_SOLUTION_iPad.pdf |
| 39 | Delivery the-keeper-of-candleholm_iPad.pdf is the calendar, not the solution, and never names the killer outside the register | PASS |  |
| 40 | Delivery the-keeper-of-candleholm_print-A4.pdf is the calendar, not the solution, and never names the killer outside the register | PASS |  |
| 41 | Delivery the-keeper-of-candleholm_print-US-Letter.pdf is the calendar, not the solution, and never names the killer outside the register | PASS |  |
| 42 | Drawn text never uses the word clue (evidence / lead instead) | PASS |  |
| 43 | Archive the-keeper-of-candleholm_files-for-sale.zip written | PASS | 7.2 MB |
| 44 | Archive the-keeper-of-candleholm_10-mockups-JPG.zip written | PASS | 4.5 MB |
| 45 | Archive the-keeper-of-candleholm_trailer_1080.mp4 written | PASS | 4.2 MB |
| 46 | Archive the-keeper-of-candleholm_calendar-presentation_1080.mp4 written | PASS | 3.7 MB |
