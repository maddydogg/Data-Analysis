# Verification report: The Keeper of Candleholm

Result: **85 of 85 checks passed** — ALL CLEAR

Answer found by the code: **Jonas Garvock**, tally 1478, Carrowby; first crossing 2 December at 13:38 on the Mail Boat, put ashore at landing 15 (Ferrach Pier).

## Checks

| # | Check | Result | Detail |
|---|---|---|---|
| 1 | Tallies 0001-2400, each exactly once | PASS |  |
| 2 | Every full name is unique | PASS |  |
| 3 | Names are letters only (no spaces, hyphens, apostrophes) | PASS |  |
| 4 | Dates 1-23 December and times between 06:30 and 18:30 | PASS |  |
| 5 | Villages, boats and landings are all on the chart | PASS |  |
| 6 | The Sound Book is in date and time order | PASS |  |
| 7 | Every day from 1 to 23 December has first crossings (most on the first days) | PASS | 1: 552, 2: 376, 3: 216, 4: 73, 5: 67, 6: 67, 7: 57, 8: 53, 9: 49, 10: 69, 11: 55, 12: 71, 13: 52, 14: 53, 15: 49, 16: 59, 17: 41, 18: 83, 19: 64, 20: 76, 21: 81, 22: 70, 23: 67 |
| 8 | Unique answer: windows 3–23 together leave exactly one line | PASS | survivors: ['Jonas Garvock #1478'] |
| 9 | Every window is needed: leaving any one out leaves more than one line | PASS | Window 3 left out -> 2 left; Window 4 left out -> 3 left; Window 5 left out -> 2 left; Window 6 left out -> 2 left; Window 7 left out -> 2 left; Window 8 left out -> 2 left; Window 9 left out -> 2 left; Window 10 left out -> 2 left; Window 11 left out -> 2 left; Window 12 left out -> 2 left; Window 13 left out -> 3 left; Window 14 left out -> 2 left; Window 15 left out -> 3 left; Window 16 left out -> 2 left; Window 17 left out -> 3 left; Window 18 left out -> 2 left; Window 19 left out -> 3 left; Window 20 left out -> 3 left; Window 21 left out -> 3 left; Window 22 left out -> 3 left; Window 23 left out -> 3 left |
| 10 | Each alternative reading on its own keeps the killer and gives the same single answer (19 readings) | PASS | Window 3 [‘already’ read as ‘before today’: 1 or 2 December only] -> 1; Window 4 [the Pilot Cutter counted too (the chart says it may use the Inner Passage at high water)] -> 1; Window 5 [the Narrows Slip itself counted too] -> 1; Window 5 [‘higher up’ read on the chart: loch landings drawn further north than the Narrows] -> 1; Window 5 [‘higher up’ read as ‘further north on the chart’, anywhere at all] -> 1; Window 6 [a village sitting right on the circle counted too] -> 1; Window 10 [the exact minutes of low and high water counted too] -> 1; Window 10 [a quarter of an hour of slack water at each end counted too] -> 1; Window 11 [‘between’ read along the shore, which runs all the way round Loch Tarrisk] -> 1; Window 11 [‘between’ read on the chart: close to the straight line from one head to the other] -> 1; Window 11 [‘between’ read on the chart: any mainland village between the two heads, inland too] -> 1; Window 12 [any landing on the waybill, the letter boxes included] -> 1; Window 14 [“more than fifteen” read as “fifteen or more”] -> 1; Window 16 [the lighting-up minute itself counted as ‘before’] -> 1; Window 17 [“later” read as “later or the same letter”] -> 1; Window 18 [a nought in front doesn’t count (0472 read as 472)] -> 1; Window 19 [Y counted as a vowel] -> 1; Window 21 [Y counted as a vowel] -> 1; Window 22 [only a double letter side by side counts as ‘twice’] -> 1 |
| 11 | Every combination of readings (98,304 in total) gives the same answer | PASS | proof: the killer passes every window under every reading, and each of the other 2,399 lines fails at least one window under every reading |
| 12 | Spatial and time words (already, through, higher up, near, between, rising, before, a.m./p.m.): every reasonable reading keeps the killer and gives the same single answer (12 readings) | PASS | W3 [‘already’ read as ‘before today’: 1 or 2 December only] -> 1; W4 [the Pilot Cutter counted too (the chart says it may use the Inner Passage at high water)] -> 1; W5 [the Narrows Slip itself counted too] -> 1; W5 [‘higher up’ read on the chart: loch landings drawn further north than the Narrows] -> 1; W5 [‘higher up’ read as ‘further north on the chart’, anywhere at all] -> 1; W6 [a village sitting right on the circle counted too] -> 1; W10 [the exact minutes of low and high water counted too] -> 1; W10 [a quarter of an hour of slack water at each end counted too] -> 1; W11 [‘between’ read along the shore, which runs all the way round Loch Tarrisk] -> 1; W11 [‘between’ read on the chart: close to the straight line from one head to the other] -> 1; W11 [‘between’ read on the chart: any mainland village between the two heads, inland too] -> 1; W16 [the lighting-up minute itself counted as ‘before’] -> 1 |
| 13 | Far-fetched readings that would drop the killer leave nobody at all, so the slip shows at once (5 readings) | PASS | W4 [only the fishing boats (the Mail Boat overlooked)] -> 0 left; W5 [only the very next landing above the Narrows (Torrandhu Jetty)] -> 0 left; W6 [‘near’ read as within half the range (6 miles)] -> 0 left; W10 [‘making’ read as ‘at high water’: within an hour of high water] -> 0 left; W16 [the almanac’s p.m. times read as morning times (3.46 read as 03:46)] -> 0 left |
| 14 | Every window rules out at least one finalist (a line that fits all the other windows) | PASS | {'3': 1, '4': 2, '5': 1, '6': 1, '7': 1, '8': 1, '9': 1, '10': 1, '11': 1, '12': 1, '13': 2, '14': 1, '15': 2, '16': 1, '17': 2, '18': 1, '19': 2, '20': 2, '21': 2, '22': 2, '23': 2} |
| 15 | Calendar order uses all 21 windows once and ends on the killer on Day 23 | PASS |  |
| 16 | Every day from 3 to 23 rules out at least one line | PASS | D3: -1256 (1144) -> D4: -497 (647) -> D5: -547 (100) -> D6: -56 (44) -> D7: -7 (37) -> D8: -5 (32) -> D9: -3 (29) -> D10: -4 (25) -> D11: -2 (23) -> D12: -1 (22) -> D13: -3 (19) -> D14: -2 (17) -> D15: -2 (15) -> D16: -1 (14) -> D17: -2 (12) -> D18: -1 (11) -> D19: -2 (9) -> D20: -2 (7) -> D21: -2 (5) -> D22: -2 (3) -> D23: -2 (1) |
| 17 | The bulk goes on Days 3–6, then 1–3 a day is typical | PASS | Days 3–6 rule out 2,356; days 7–23: 7, 5, 3, 4, 2, 1, 3, 2, 2, 1, 2, 1, 2, 2, 2, 2, 2 |
| 18 | The ending stays open: at least 7 lines after Day 19, 5 after Day 20, 3 after Day 21 and 2 after Day 22 | PASS | after Day 19: 9, Day 20: 7, Day 21: 5, Day 22: 3, Day 23: 1 |
| 19 | Sealed Check: no finalist shares the killer's check number | PASS | check number 924; other lines with the same number: 4 of 2,399 |
| 20 | Window 3: the Harbour Trust rules say a tally is given on the first crossing and only the first crossing is written in | PASS |  |
| 21 | Window 4: the passages note puts exactly the Mail Boat and the fishing boats in the Inner Passage, and the witness names no boat | PASS |  |
| 22 | Window 5: the loch landings are listed in order from the mouth, the Narrows Slip is at the Narrows, and the loch turns south above it (so the chart reading differs from the route reading) | PASS |  |
| 23 | Window 6: the range note lists exactly the villages inside the circle, and Skellan sits on it | PASS |  |
| 24 | Window 7: the code book page prints the whole alphabet, and the killer's initial starts with a dash | PASS |  |
| 25 | Window 10: the tide table prints the same times the clue uses (first week) | PASS |  |
| 26 | Window 11: the coast note lists the open-coast villages in order from north to south | PASS |  |
| 27 | Window 12: the waybill names exactly the parcel sheds and the letter boxes | PASS |  |
| 28 | Window 16: the almanac prints lighting-up times in a.m./p.m. that match the clue | PASS |  |
| 29 | Window 20: the tally metals note matches the clue (copper 0801–1600) | PASS |  |
| 30 | Killer’s own story is consistent with every paper | PASS |  |
| 31 | The killer’s times sit well inside every window (at least 15 minutes from any tide or lighting-up boundary) | PASS |  |
| 32 | Finalists don't point at the answer: for boat, village, landing and hour the killer's value is shared by at least two finalists, is never the single most common value, and no value covers more than half the shortlist | PASS | boat: killer's value shared by 12 of 29 finalists, most common value 15/30; village: killer's value shared by 8 of 29 finalists, most common value 10/30; landing: killer's value shared by 8 of 29 finalists, most common value 10/30; hour: killer's value shared by 3 of 29 finalists, most common value 5/30 |
| 33 | Finalists all have different first names and different surnames | PASS |  |
| 34 | Level-3 hints keep exactly the same lines as their windows (all 21; the tide and lamp hints on 1–3 December, the only dates still in by then) | PASS |  |
| 35 | Examples and facts quoted in hints and house rules are correct | PASS | G starts with a dash, A with a dot: ok; Agnes and Clara contain an A: ok; 0472 is even; 0+4+7+2 = 13 (not > 15); 1395 adds to 18: ok; Moira, Grant and Morag have five letters; Ruth and Fergus don't: ok; Angus Ross ends on the same letter twice; Moira Bain doesn't: ok; 3.46 p.m. is 15:46: ok; Sadie Kerr fits Window 17; Ada Muir and Mary Muir don't: ok; 0472 has a nought; 1395 hasn't: ok; Moffat and Lindsay have two vowels; Ogilvie has four: ok; Angus and Mary end on a consonant; Effie and Flora don't: ok; Rennison, Laidlaw and Barclay repeat a letter; Munro doesn't: ok; Rennison has three Ns (house rules): ok; Iona Rae has 7 letters, odd: ok; Tally 0472 digits add up to 13 (house rules): ok |
| 36 | Names used as examples in hints are not in the Sound Book | PASS |  |
| 37 | No hint names the killer, his tally or his landing on its own | PASS |  |
| 38 | Stop list: no borrowed brands, titles, real lighthouses or islands, and no names or places from calendar A, cases 1–3 or the party game, in any text or name pool (whole words) | PASS |  |
| 39 | The word “clue” is not used anywhere in the calendar (evidence / lead instead) | PASS |  |
| 40 | No famous-detective, Christmas-story, lighthouse-history or earlier-character names in the name pools | PASS |  |
| 41 | Story characters and the killer's own names are kept out of the random name pools | PASS |  |
| 42 | Every character in the text exists in the fonts that print it | PASS | {} |
| 43 | [letter] each of the 24 windows starts on its own page, in order | PASS | first pages: [8, 13, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81] |
| 44 | [letter] every window’s question is printed word for word | PASS |  |
| 45 | [letter] all 23 journal entries are printed word for word | PASS | [] |
| 46 | [letter] every paper pinned to a window is printed word for word (the text a reader without pictures needs) | PASS | [] |
| 47 | [letter] all 63 hints are printed word for word | PASS |  |
| 48 | [letter] the killer's name appears exactly once in the calendar (his line in the Sound Book) | PASS | 1 times |
| 49 | [letter] check-ins on Windows 6, 12 and 18 print the counts the code found | PASS | {6: 44, 12: 22, 18: 11} |
| 50 | [letter] the Sound Book in the PDF matches the data line for line (2,400 lines) | PASS | parsed 2400 lines |
| 51 | [letter] the book has a clickable contents page and bookmarks | PASS | 64 bookmarks |
| 52 | [letter] set-up pages include the envelope template and day numbers 1–24 | PASS |  |
| 53 | [letter] Fraunces, Nunito and Kalam are embedded | PASS |  |
| 54 | [letter] solution file names the same killer the code found | PASS |  |
| 55 | [letter] solution day-by-day counts match the code | PASS |  |
| 56 | [letter] the calendar itself has no solution pages | PASS |  |
| 57 | [a4] each of the 24 windows starts on its own page, in order | PASS | first pages: [8, 13, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78] |
| 58 | [a4] every window’s question is printed word for word | PASS |  |
| 59 | [a4] all 23 journal entries are printed word for word | PASS | [] |
| 60 | [a4] every paper pinned to a window is printed word for word (the text a reader without pictures needs) | PASS | [] |
| 61 | [a4] all 63 hints are printed word for word | PASS |  |
| 62 | [a4] the killer's name appears exactly once in the calendar (his line in the Sound Book) | PASS | 1 times |
| 63 | [a4] check-ins on Windows 6, 12 and 18 print the counts the code found | PASS | {6: 44, 12: 22, 18: 11} |
| 64 | [a4] the Sound Book in the PDF matches the data line for line (2,400 lines) | PASS | parsed 2400 lines |
| 65 | [a4] the book has a clickable contents page and bookmarks | PASS | 63 bookmarks |
| 66 | [a4] set-up pages include the envelope template and day numbers 1–24 | PASS |  |
| 67 | [a4] Fraunces, Nunito and Kalam are embedded | PASS |  |
| 68 | [a4] solution file names the same killer the code found | PASS |  |
| 69 | [a4] solution day-by-day counts match the code | PASS |  |
| 70 | [a4] the calendar itself has no solution pages | PASS |  |
| 71 | [ipad] each of the 24 windows starts on its own page, in order | PASS | first pages: [6, 11, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73] |
| 72 | [ipad] every window’s question is printed word for word | PASS |  |
| 73 | [ipad] all 23 journal entries are printed word for word | PASS | [] |
| 74 | [ipad] every paper pinned to a window is printed word for word (the text a reader without pictures needs) | PASS | [] |
| 75 | [ipad] all 63 hints are printed word for word | PASS |  |
| 76 | [ipad] the killer's name appears exactly once in the calendar (his line in the Sound Book) | PASS | 1 times |
| 77 | [ipad] check-ins on Windows 6, 12 and 18 print the counts the code found | PASS | {6: 44, 12: 22, 18: 11} |
| 78 | [ipad] the Sound Book in the PDF matches the data line for line (2,400 lines) | PASS | parsed 2400 lines |
| 79 | [ipad] the book has a clickable contents page and bookmarks | PASS | 62 bookmarks |
| 80 | [ipad] the first page is the calendar: 24 tappable windows, each opening its own day | PASS | calendar on page 1, 24 window links (+ 1 to the cover) |
| 81 | [ipad] every window page links back to the calendar | PASS | 24 of 24 |
| 82 | [ipad] Fraunces, Nunito and Kalam are embedded | PASS |  |
| 83 | [ipad] solution file names the same killer the code found | PASS |  |
| 84 | [ipad] solution day-by-day counts match the code | PASS |  |
| 85 | [ipad] the calendar itself has no solution pages | PASS |  |

## Day by day (the elimination curve)

| Day | Window | Ruled out | Left |
|---|---|---|---|
| 2 | The Sound Book | 0 | 2,400 |
| 3 | A Tally Already | 1,256 | 1,144 |
| 4 | The Inner Passage | 497 | 647 |
| 5 | Up the Loch | 547 | 100 |
| 6 | Within Sight of the Light | 56 | 44 |
| 7 | A Lamp in the Boathouse | 7 | 37 |
| 8 | The Parcel Slip | 5 | 32 |
| 9 | The Tally Boards | 3 | 29 |
| 10 | On the Flood | 4 | 25 |
| 11 | Between the Heads | 2 | 23 |
| 12 | The Christmas Waybill | 1 | 22 |
| 13 | A Card on the Nail | 3 | 19 |
| 14 | Gil’s Lucky Tallies | 2 | 17 |
| 15 | The Pilot’s Log | 2 | 15 |
| 16 | Before the Lamp Was Lit | 1 | 14 |
| 17 | The Lost Mitten | 2 | 12 |
| 18 | No Noughts | 1 | 11 |
| 19 | The Iced Cake | 2 | 9 |
| 20 | Brass, Copper and Tin | 2 | 7 |
| 21 | A Name Called from the Jetty | 2 | 5 |
| 22 | The Signwriter’s Stencils | 2 | 3 |
| 23 | The Striped Scarf | 2 | 1 |

## Is every window needed?

| Window left out | Lines left |
|---|---|
| Window 3 | 2 |
| Window 4 | 3 |
| Window 5 | 2 |
| Window 6 | 2 |
| Window 7 | 2 |
| Window 8 | 2 |
| Window 9 | 2 |
| Window 10 | 2 |
| Window 11 | 2 |
| Window 12 | 2 |
| Window 13 | 3 |
| Window 14 | 2 |
| Window 15 | 3 |
| Window 16 | 2 |
| Window 17 | 3 |
| Window 18 | 2 |
| Window 19 | 3 |
| Window 20 | 3 |
| Window 21 | 3 |
| Window 22 | 3 |
| Window 23 | 3 |

## Readings tested

| Window | Word | Reading | Lines left | Killer kept? | Same answer? |
|---|---|---|---|---|---|
| 3 | already / today | ‘already’ read as ‘before today’: 1 or 2 December only | 1 | yes | yes |
| 4 | through / between | the Pilot Cutter counted too (the chart says it may use the Inner Passage at high water) | 1 | yes | yes |
| 5 | higher up / above | the Narrows Slip itself counted too | 1 | yes | yes |
| 5 | higher up / above | ‘higher up’ read on the chart: loch landings drawn further north than the Narrows | 1 | yes | yes |
| 5 | higher up / above | ‘higher up’ read as ‘further north on the chart’, anywhere at all | 1 | yes | yes |
| 6 | near / within sight | a village sitting right on the circle counted too | 1 | yes | yes |
| 10 | rising / before high water | the exact minutes of low and high water counted too | 1 | yes | yes |
| 10 | rising / before high water | a quarter of an hour of slack water at each end counted too | 1 | yes | yes |
| 11 | between | ‘between’ read along the shore, which runs all the way round Loch Tarrisk | 1 | yes | yes |
| 11 | between | ‘between’ read on the chart: close to the straight line from one head to the other | 1 | yes | yes |
| 11 | between | ‘between’ read on the chart: any mainland village between the two heads, inland too | 1 | yes | yes |
| 12 |  | any landing on the waybill, the letter boxes included | 1 | yes | yes |
| 14 |  | “more than fifteen” read as “fifteen or more” | 1 | yes | yes |
| 16 | before / a.m. and p.m. | the lighting-up minute itself counted as ‘before’ | 1 | yes | yes |
| 17 |  | “later” read as “later or the same letter” | 1 | yes | yes |
| 18 |  | a nought in front doesn’t count (0472 read as 472) | 1 | yes | yes |
| 19 |  | Y counted as a vowel | 1 | yes | yes |
| 21 |  | Y counted as a vowel | 1 | yes | yes |
| 22 |  | only a double letter side by side counts as ‘twice’ | 1 | yes | yes |

## Far-fetched readings (they drop the killer, so they must leave nobody)

| Window | Reading | Lines left |
|---|---|---|
| 4 | only the fishing boats (the Mail Boat overlooked) | 0 |
| 5 | only the very next landing above the Narrows (Torrandhu Jetty) | 0 |
| 6 | ‘near’ read as within half the range (6 miles) | 0 |
| 10 | ‘making’ read as ‘at high water’: within an hour of high water | 0 |
| 16 | the almanac’s p.m. times read as morning times (3.46 read as 03:46) | 0 |

## Finalists (fit every window but one)

| Tally | Traveller | Ruled out only by |
|---|---|---|
| 1258 | Johan Gauld | Window 3 |
| 1476 | Oscar Buist | Window 4 |
| 1168 | Janet Dolan | Window 4 |
| 1448 | Sarah Kershaw | Window 5 |
| 1586 | Niall Munro | Window 6 |
| 1578 | Garth Agnew | Window 7 |
| 1556 | Helen Bonar | Window 8 |
| 1189 | Lucas Baird | Window 9 |
| 1596 | Susan Mowat | Window 10 |
| 1496 | Pearl Milne | Window 11 |
| 1286 | Morag Kinloch | Window 12 |
| 1474 | Zander Gibson | Window 13 |
| 1276 | Seonag Gowans | Window 13 |
| 1532 | Eamon Calvert | Window 14 |
| 1528 | Karen Doran | Window 15 |
| 1186 | Rowan Cowan | Window 15 |
| 1456 | Grant Dewar | Window 16 |
| 1546 | Jacob Troup | Window 17 |
| 1268 | Elias Mavor | Window 17 |
| 1098 | Edgar Dickson | Window 18 |
| 1298 | Dylan Cowie | Window 19 |
| 1492 | Isaac Dunsire | Window 19 |
| 2266 | Mabel Kidston | Window 20 |
| 2386 | Tavis Kemlo | Window 20 |
| 1592 | Zelda Mahon | Window 21 |
| 1398 | Nadia Murtagh | Window 21 |
| 1558 | Craig Brennan | Window 22 |
| 1484 | James Burnett | Window 22 |
| 1498 | Gavin Bancroft | Window 23 |
| 1198 | Frank Dalton | Window 23 |

## Is the shortlist free of patterns?

- boat: killer's value shared by 12 of 29 finalists, most common value 15/30
- village: killer's value shared by 8 of 29 finalists, most common value 10/30
- landing: killer's value shared by 8 of 29 finalists, most common value 10/30
- hour: killer's value shared by 3 of 29 finalists, most common value 5/30

## Page counts

- book_letter: 90
- solution_letter: 8
- book_a4: 87
- solution_a4: 8
- book_ipad: 81
- solution_ipad: 6
