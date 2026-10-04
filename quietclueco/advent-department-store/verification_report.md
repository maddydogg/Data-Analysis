# Verification report: The Windows at Quillon's

Result: **76 of 76 checks passed** — ALL CLEAR

Answer found by the code: **Verena Pennock**, pass 2173, Old Mint, in at 18:31 by the Tram Door, last till 20.

## Checks

| # | Check | Result | Detail |
|---|---|---|---|
| 1 | Passes 0001-2400, each exactly once | PASS |  |
| 2 | Every full name is unique | PASS |  |
| 3 | Names are letters only (no spaces, hyphens, apostrophes) | PASS |  |
| 4 | Times in within opening hours 16:00-21:29 | PASS |  |
| 5 | Districts, doors and tills are valid | PASS |  |
| 6 | Register is sorted by time in | PASS |  |
| 7 | Unique answer: windows 3–23 together leave exactly one pass | PASS | survivors: ['Verena Pennock #2173'] |
| 8 | Every window is needed: leaving any one out leaves more than one pass | PASS | Window 3 left out -> 2 left; Window 4 left out -> 3 left; Window 5 left out -> 2 left; Window 6 left out -> 2 left; Window 7 left out -> 2 left; Window 8 left out -> 2 left; Window 9 left out -> 2 left; Window 10 left out -> 2 left; Window 11 left out -> 2 left; Window 12 left out -> 2 left; Window 13 left out -> 3 left; Window 14 left out -> 2 left; Window 15 left out -> 3 left; Window 16 left out -> 2 left; Window 17 left out -> 3 left; Window 18 left out -> 2 left; Window 19 left out -> 3 left; Window 20 left out -> 3 left; Window 21 left out -> 3 left; Window 22 left out -> 3 left; Window 23 left out -> 3 left |
| 9 | Each alternative reading on its own gives the same single answer (18 readings) | PASS | Window 3 [first and last minute of each set left out] -> 1; Window 4 [the Clock Door at the far corner of the yard counted as ‘straight across’ too] -> 1; Window 5 [the Clock Gallery is only between floors, so it doesn’t count] -> 1; Window 5 [the Roof Terrace is outdoors, not a floor of the store] -> 1; Window 6 [the two named stops counted as ‘between’ too] -> 1; Window 8 [“the second half of the alphabet” read as starting at M] -> 1; Window 10 [the five minutes forgotten (19:00 or earlier)] -> 1; Window 10 [strictly before 18:55] -> 1; Window 11 [districts that only touch the park at a corner counted as ‘next to’ too] -> 1; Window 12 [any counter that sells cocoa in any form, tins and powder included] -> 1; Window 13 [Y counted as a vowel] -> 1; Window 14 [“more than ten” read as “ten or more”] -> 1; Window 15 [any letter used twice, even apart] -> 1; Window 16 [hands lying exactly on 3 or 9 (minutes 15 and 45) left out] -> 1; Window 16 [‘lower half’ read as ‘pointing roughly down’ (minutes 20 to 40)] -> 1; Window 17 [“more letters” read as “at least as many”] -> 1; Window 18 [leading zeros ignored (0472 read as 472)] -> 1; Window 21 [“exactly once” read as “at least once”] -> 1 |
| 10 | Every combination of readings (110,592 in total) gives the same answer | PASS | proof: the killer passes every window under every reading, and each of the other 2,399 passes fails at least one window under every reading |
| 11 | Plans and spatial words (straight, through, opposite, higher, between floors, between, next to, lower half): all 20 reasonable readings keep the killer and give the same single answer | PASS | W4 [‘straight across’ = only the door directly opposite the shelter (Tram)] -> 1; W4 [both routes, plus the Clock Door at the corner of the yard] -> 1; W4 [‘the shelter opposite the store’: any door on Tramway Yard or reached from it] -> 1; W5 [everything above the Second Floor (official)] -> 1; W5 [half-landings are between floors, so they don’t count] -> 1; W5 [the Roof Terrace is outdoors, so it doesn’t count] -> 1; W5 [only full floors count: the Third Floor] -> 1; W5 [‘higher up’ taken loosely: the Second Floor itself counts too] -> 1; W6 [stops strictly between Vell Bridge and Gasworks (official)] -> 1; W6 [the two named stops included] -> 1; W6 [‘between’ read on the map, not along the route: the district on the straight line from Bridgefoot to Gasworks (Old Mint)] -> 1; W6 [‘between’ read on the map, generously: every district the straight line from Bridgefoot to Gasworks passes or grazes (Ferrygate, Old Mint, Pinchgate)] -> 1; W11 [shares a side with the park (official)] -> 1; W11 [a corner touch counts too] -> 1; W16 [minutes 15–45 (official)] -> 1; W16 [minutes 16–44 (hands on 3 or 9 left out)] -> 1; W16 [pointing roughly down: minutes 20–40] -> 1; W16 [pointing straight down only: minutes 25–35] -> 1; W10 [the five minutes forgotten: 19:00 or earlier] -> 1; W10 [the five minutes subtracted twice: 18:50 or earlier] -> 1 |
| 12 | Far-fetched readings that would drop the killer leave nobody at all, so the slip shows at once | PASS | W4 [only ‘through the Winter Garden’ (ignoring ‘straight across’)] -> 0 left; W5 [only the very next level up (the Clock Gallery)] -> 0 left |
| 13 | Every window rules out at least one finalist (a pass that fits all the other windows) | PASS | {'3': 1, '4': 2, '5': 1, '6': 1, '7': 1, '8': 1, '9': 1, '10': 1, '11': 1, '12': 1, '13': 2, '14': 1, '15': 2, '16': 1, '17': 2, '18': 1, '19': 2, '20': 2, '21': 2, '22': 2, '23': 2} |
| 14 | Calendar order uses all 21 windows once and ends on the killer on Day 23 | PASS |  |
| 15 | Every day from 3 to 23 rules out at least one pass | PASS | D3: -1261 (1139) -> D4: -646 (493) -> D5: -347 (146) -> D6: -88 (58) -> D7: -10 (48) -> D8: -8 (40) -> D9: -9 (31) -> D10: -5 (26) -> D11: -3 (23) -> D12: -2 (21) -> D13: -3 (18) -> D14: -1 (17) -> D15: -2 (15) -> D16: -1 (14) -> D17: -2 (12) -> D18: -1 (11) -> D19: -2 (9) -> D20: -2 (7) -> D21: -2 (5) -> D22: -2 (3) -> D23: -2 (1) |
| 16 | The ending stays open: at least 7 passes after Day 19, 5 after Day 20, 3 after Day 21 and 2 after Day 22 | PASS | after Day 19: 9, Day 20: 7, Day 21: 5, Day 22: 3, Day 23: 1 |
| 17 | Sealed Check: no finalist shares the killer's check number | PASS | check number 224; other passes with the same number: 3 of 2,399 |
| 18 | Window 3: the band programme prints exactly the three sets in the clue | PASS |  |
| 19 | Window 4: the newsvendor gives both routes and names no door | PASS |  |
| 20 | Window 5: the Toy Hall is on the Second Floor, the Clock Gallery is a half-landing between the Second and Third Floors, and the lift doesn’t decide anything | PASS |  |
| 21 | Window 6: the conductor names Vell Bridge and Gasworks, both on Route 7, and no district | PASS |  |
| 22 | Window 11: exactly four districts share a side with Vell Park | PASS |  |
| 23 | Window 12: the store guide names exactly the striped-cup counters, and the trap (tins, powder) points to counters outside the clue | PASS |  |
| 24 | Window 10: the store guide says the gallery clocks run five minutes fast, and the clockmaker says seven o’clock | PASS |  |
| 25 | Window 20: the printer’s note matches the clue (green 0001–1200, red 1201–2400) | PASS |  |
| 26 | Killer’s own story is consistent with every document | PASS |  |
| 27 | Finalists don't point at the answer: for door, district, last till and entry hour the killer's value is shared by at least two finalists, is never the single most common value, and no value covers more than half the shortlist | PASS | door: killer's value shared by 12 of 29 finalists, most common value 15/30; district: killer's value shared by 12 of 29 finalists, most common value 15/30; last till: killer's value shared by 12 of 29 finalists, most common value 15/30; entry hour: killer's value shared by 12 of 29 finalists, most common value 15/30 |
| 28 | Finalists all have different first names and different surnames | PASS |  |
| 29 | Level-3 hints keep exactly the same passes as their windows (all 21) | PASS |  |
| 30 | Examples and facts quoted in hints and house rules are correct | PASS | Rita and Laura contain an R: ok; 0472 is even; 0+4+7+2 = 13 > 10; 2+3+1+0 = 6: ok; Laura and Annie end on a vowel; Henry and Mabel don't: ok; Wallace and Carrier have a double letter; Hebden has two Es apart and no double: ok; Ruth Barlow passes Window 17, Ruth Gale fails: ok; 4825 has four different digits; 1301 and 0402 don't: ok; Marina and Gertie have six letters; Clara and Harriet don't: ok; Lacey has one E, Ellery two, Pollard none: ok; Sally Sutton fails Window 22, Maria Pell passes: ok; Mary Pell has an even total (8): ok; House rules: Ellery has two Es, Lacey one; 0472 digits add to 13: ok; Hint 16: a quarter past to a quarter to = minutes 15 to 45: ok |
| 31 | Names used as examples in hints are not in the register | PASS |  |
| 32 | No hint names the killer or their pass | PASS |  |
| 33 | No borrowed brands, titles, real stores or names from the earlier cases in any text or name pool | PASS |  |
| 34 | No famous-detective, Christmas-story or store-founder surnames in the name pools | PASS |  |
| 35 | Story characters and the killer's own names are kept out of the random name pools | PASS |  |
| 36 | Every character in the text exists in the embedded fonts | PASS | [] |
| 37 | [letter] each of the 24 windows starts on its own page, in order | PASS | first pages: [8, 11, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79] |
| 38 | [letter] every window’s question is printed word for word | PASS |  |
| 39 | [letter] every window’s evidence text is printed word for word | PASS | [] |
| 40 | [letter] all 63 hints are printed word for word | PASS |  |
| 41 | [letter] the killer's name appears exactly once in the calendar (their line in the register) | PASS | 1 times |
| 42 | [letter] check-ins on Windows 6, 12 and 18 print the counts the code found | PASS | {6: 58, 12: 21, 18: 11} |
| 43 | [letter] Lantern Register in the PDF matches the data line for line (2,400 rows) | PASS | parsed 2400 rows |
| 44 | [letter] the book has a clickable contents page and bookmarks | PASS | 43 bookmarks |
| 45 | [letter] set-up pages include the envelope template and day numbers 1–24 | PASS |  |
| 46 | [letter] Fraunces and Nunito are embedded | PASS |  |
| 47 | [letter] solution file names the same killer the code found | PASS |  |
| 48 | [letter] solution day-by-day counts match the code | PASS |  |
| 49 | [letter] the calendar itself has no solution pages | PASS |  |
| 50 | [a4] each of the 24 windows starts on its own page, in order | PASS | first pages: [8, 11, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76] |
| 51 | [a4] every window’s question is printed word for word | PASS |  |
| 52 | [a4] every window’s evidence text is printed word for word | PASS | [] |
| 53 | [a4] all 63 hints are printed word for word | PASS |  |
| 54 | [a4] the killer's name appears exactly once in the calendar (their line in the register) | PASS | 1 times |
| 55 | [a4] check-ins on Windows 6, 12 and 18 print the counts the code found | PASS | {6: 58, 12: 21, 18: 11} |
| 56 | [a4] Lantern Register in the PDF matches the data line for line (2,400 rows) | PASS | parsed 2400 rows |
| 57 | [a4] the book has a clickable contents page and bookmarks | PASS | 43 bookmarks |
| 58 | [a4] set-up pages include the envelope template and day numbers 1–24 | PASS |  |
| 59 | [a4] Fraunces and Nunito are embedded | PASS |  |
| 60 | [a4] solution file names the same killer the code found | PASS |  |
| 61 | [a4] solution day-by-day counts match the code | PASS |  |
| 62 | [a4] the calendar itself has no solution pages | PASS |  |
| 63 | [ipad] each of the 24 windows starts on its own page, in order | PASS | first pages: [6, 9, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70] |
| 64 | [ipad] every window’s question is printed word for word | PASS |  |
| 65 | [ipad] every window’s evidence text is printed word for word | PASS | [] |
| 66 | [ipad] all 63 hints are printed word for word | PASS |  |
| 67 | [ipad] the killer's name appears exactly once in the calendar (their line in the register) | PASS | 1 times |
| 68 | [ipad] check-ins on Windows 6, 12 and 18 print the counts the code found | PASS | {6: 58, 12: 21, 18: 11} |
| 69 | [ipad] Lantern Register in the PDF matches the data line for line (2,400 rows) | PASS | parsed 2400 rows |
| 70 | [ipad] the book has a clickable contents page and bookmarks | PASS | 41 bookmarks |
| 71 | [ipad] the calendar page has 24 tappable windows, each opening its own day | PASS | 24 link targets |
| 72 | [ipad] every window page links back to the calendar | PASS | 24 of 24 |
| 73 | [ipad] Fraunces and Nunito are embedded | PASS |  |
| 74 | [ipad] solution file names the same killer the code found | PASS |  |
| 75 | [ipad] solution day-by-day counts match the code | PASS |  |
| 76 | [ipad] the calendar itself has no solution pages | PASS |  |

## Day by day (the elimination curve)

| Day | Window | Ruled out | Left |
|---|---|---|---|
| 2 | Lantern Register | 0 | 2,400 |
| 3 | The Brass Band | 1,261 | 1,139 |
| 4 | Snow on Tramway Yard | 646 | 493 |
| 5 | The Toy Hall Stairs | 347 | 146 |
| 6 | The No. 7 Tram | 88 | 58 |
| 7 | The Glove Counter | 10 | 48 |
| 8 | Paper and Ribbon | 8 | 40 |
| 9 | The Watchmaker’s Bench | 9 | 31 |
| 10 | The Great Tree | 5 | 26 |
| 11 | Vell Park in the Snow | 3 | 23 |
| 12 | The Striped Cup | 2 | 21 |
| 13 | Carols on the Stairs | 3 | 18 |
| 14 | The Toy Train | 1 | 17 |
| 15 | The Lace Counter | 2 | 15 |
| 16 | The Door Stamp | 1 | 14 |
| 17 | The Hat Box | 2 | 12 |
| 18 | The Clock Gallery | 1 | 11 |
| 19 | Christmas Cards | 2 | 9 |
| 20 | Red and Green | 2 | 7 |
| 21 | The Linen Ledger | 2 | 5 |
| 22 | Two Initials | 2 | 3 |
| 23 | Sugared Almonds | 2 | 1 |

## Is every window needed?

| Window left out | Passes left |
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

## Misreadings tested

| Window | Alternative reading | Passes left | Same answer? |
|---|---|---|---|
| Window 3 | first and last minute of each set left out | 1 | yes |
| Window 4 | the Clock Door at the far corner of the yard counted as ‘straight across’ too | 1 | yes |
| Window 5 | the Clock Gallery is only between floors, so it doesn’t count | 1 | yes |
| Window 5 | the Roof Terrace is outdoors, not a floor of the store | 1 | yes |
| Window 6 | the two named stops counted as ‘between’ too | 1 | yes |
| Window 8 | “the second half of the alphabet” read as starting at M | 1 | yes |
| Window 10 | the five minutes forgotten (19:00 or earlier) | 1 | yes |
| Window 10 | strictly before 18:55 | 1 | yes |
| Window 11 | districts that only touch the park at a corner counted as ‘next to’ too | 1 | yes |
| Window 12 | any counter that sells cocoa in any form, tins and powder included | 1 | yes |
| Window 13 | Y counted as a vowel | 1 | yes |
| Window 14 | “more than ten” read as “ten or more” | 1 | yes |
| Window 15 | any letter used twice, even apart | 1 | yes |
| Window 16 | hands lying exactly on 3 or 9 (minutes 15 and 45) left out | 1 | yes |
| Window 16 | ‘lower half’ read as ‘pointing roughly down’ (minutes 20 to 40) | 1 | yes |
| Window 17 | “more letters” read as “at least as many” | 1 | yes |
| Window 18 | leading zeros ignored (0472 read as 472) | 1 | yes |
| Window 21 | “exactly once” read as “at least once” | 1 | yes |

## Plans and spatial words

| Window | Word | Kind | Reading | Passes left | Killer kept? |
|---|---|---|---|---|---|
| 4 | straight / through | reasonable | ‘straight across’ = only the door directly opposite the shelter (Tram) | 1 | yes |
| 4 | straight / through | reasonable | both routes, plus the Clock Door at the corner of the yard | 1 | yes |
| 4 | opposite | reasonable | ‘the shelter opposite the store’: any door on Tramway Yard or reached from it | 1 | yes |
| 4 | through | far-fetched | only ‘through the Winter Garden’ (ignoring ‘straight across’) | 0 | no |
| 5 | higher / between floors | reasonable | everything above the Second Floor (official) | 1 | yes |
| 5 | higher / between floors | reasonable | half-landings are between floors, so they don’t count | 1 | yes |
| 5 | higher / between floors | reasonable | the Roof Terrace is outdoors, so it doesn’t count | 1 | yes |
| 5 | higher / between floors | reasonable | only full floors count: the Third Floor | 1 | yes |
| 5 | higher | reasonable | ‘higher up’ taken loosely: the Second Floor itself counts too | 1 | yes |
| 5 | higher / between floors | far-fetched | only the very next level up (the Clock Gallery) | 0 | no |
| 6 | between | reasonable | stops strictly between Vell Bridge and Gasworks (official) | 1 | yes |
| 6 | between | reasonable | the two named stops included | 1 | yes |
| 6 | between | reasonable | ‘between’ read on the map, not along the route: the district on the straight line from Bridgefoot to Gasworks (Old Mint) | 1 | yes |
| 6 | between | reasonable | ‘between’ read on the map, generously: every district the straight line from Bridgefoot to Gasworks passes or grazes (Ferrygate, Old Mint, Pinchgate) | 1 | yes |
| 11 | next to | reasonable | shares a side with the park (official) | 1 | yes |
| 11 | next to | reasonable | a corner touch counts too | 1 | yes |
| 16 | lower half / below | reasonable | minutes 15–45 (official) | 1 | yes |
| 16 | lower half / below | reasonable | minutes 16–44 (hands on 3 or 9 left out) | 1 | yes |
| 16 | lower half / below | reasonable | pointing roughly down: minutes 20–40 | 1 | yes |
| 16 | lower half / below | reasonable | pointing straight down only: minutes 25–35 | 1 | yes |
| 10 | before / clocks | reasonable | the five minutes forgotten: 19:00 or earlier | 1 | yes |
| 10 | before / clocks | reasonable | the five minutes subtracted twice: 18:50 or earlier | 1 | yes |

## Finalists (fit every window but one)

| Pass | Shopper | Ruled out only by |
|---|---|---|
| 2089 | Andrea Vellacott | Window 3 |
| 1593 | Elvira Wassell | Window 4 |
| 1863 | Norine Winnell | Window 4 |
| 2197 | Mirela Norrell | Window 5 |
| 1457 | Rosina Pottell | Window 6 |
| 1507 | Hattie Roskell | Window 7 |
| 1857 | Rowena Denning | Window 8 |
| 2084 | Dorita Varrell | Window 9 |
| 1425 | Gracie Warrell | Window 10 |
| 1365 | Andrei Tyrrell | Window 11 |
| 1309 | Marina Tollett | Window 12 |
| 1729 | Carmen Willett | Window 13 |
| 1295 | Roland Purcell | Window 13 |
| 2015 | Gertie Tappell | Window 14 |
| 2357 | Teresa Pantridge | Window 15 |
| 2349 | Myrtle Northey | Window 15 |
| 1527 | Laurie Tuckett | Window 16 |
| 1347 | Bertha Tebbs | Window 17 |
| 1289 | Nerina Wells | Window 17 |
| 1217 | Orsola Sellars | Window 18 |
| 1273 | Carla Orrell | Window 19 |
| 1845 | Bruno Rossiter | Window 19 |
| 0427 | Zarina Wallace | Window 20 |
| 0729 | Margie Tarrell | Window 20 |
| 1625 | Carina Swallow | Window 21 |
| 1623 | Lorena Nuttall | Window 21 |
| 1653 | Serena Sallett | Window 22 |
| 1785 | Sorcha Sommers | Window 22 |
| 1345 | Martha Ollerton | Window 23 |
| 1865 | Tamara Quinnell | Window 23 |

## Is the shortlist free of patterns?

- door: killer's value shared by 12 of 29 finalists, most common value 15/30
- district: killer's value shared by 12 of 29 finalists, most common value 15/30
- last till: killer's value shared by 12 of 29 finalists, most common value 15/30
- entry hour: killer's value shared by 12 of 29 finalists, most common value 15/30

## Page counts

- book_letter: 89
- solution_letter: 8
- book_a4: 85
- solution_a4: 8
- book_ipad: 77
- solution_ipad: 6
