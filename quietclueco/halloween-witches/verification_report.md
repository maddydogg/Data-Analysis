# Verification report: Full Moon over Morrowmere

Result: **55 of 55 checks passed** — ALL CLEAR

Answer found by the code: **Edna Elworthy**, ticket 4073, Hatherby, entered 19:23 by Orchard Gap, last stall 21.

## Checks

| # | Check | Result | Detail |
|---|---|---|---|
| 1 | Tickets 0001-6000, each exactly once | PASS |  |
| 2 | Every full name is unique | PASS |  |
| 3 | Names are letters only (no spaces, hyphens, apostrophes) | PASS |  |
| 4 | Entry times within opening hours 16:00-20:29 | PASS |  |
| 5 | Towns, gates and stalls are valid | PASS |  |
| 6 | Log is sorted by entry time | PASS |  |
| 7 | Unique answer: all 18 clues together leave exactly one visitor | PASS | survivors: ['Edna Elworthy #4073'] |
| 8 | Every clue is needed: removing any one leaves more than one visitor | PASS | Clue 1 removed -> 2 left; Clue 2 removed -> 2 left; Clue 3 removed -> 3 left; Clue 4 removed -> 2 left; Clue 5 removed -> 2 left; Clue 6 removed -> 2 left; Clue 7 removed -> 2 left; Clue 8 removed -> 2 left; Clue 9 removed -> 2 left; Clue 10 removed -> 2 left; Clue 11 removed -> 2 left; Clue 12 removed -> 2 left; Evidence A removed -> 3 left; Evidence B removed -> 3 left; Evidence C removed -> 2 left; Evidence D removed -> 3 left; Evidence E removed -> 3 left; Evidence F removed -> 3 left |
| 9 | Each alternative reading on its own gives the same single answer | PASS | Clue 2 [“at least two” read as “more than two”] -> 1; Clue 3 [“exactly once” read as “at least once”] -> 1; Clue 4 [six letters itself counted as “fewer than six”] -> 1; Clue 7 [leading zeros ignored (0472 read as 472)] -> 1; Evidence B [first and last minutes of each clear spell excluded] -> 1; Evidence C [strictly before 19:40] -> 1 |
| 10 | Every combination of readings (64 in total) gives the same answer | PASS | proof: the killer passes every clue under every reading, and each of the other 5,999 visitors fails at least one clue under every reading |
| 11 | Every clue rules out at least one finalist (a visitor who fits all the other clues) | PASS | {'1': 1, '2': 1, '3': 2, '4': 1, '5': 1, '6': 1, '7': 1, '8': 1, '9': 1, '10': 1, '11': 1, '12': 1, 'A': 2, 'B': 2, 'C': 1, 'D': 2, 'E': 2, 'F': 2} |
| 12 | Walkthrough uses all 18 clues once and ends on the killer | PASS |  |
| 13 | No step in the walkthrough rules out zero visitors | PASS | Evidence B: -3316 (2684) -> Evidence A: -1411 (1273) -> Evidence C: -349 (924) -> Evidence D: -713 (211) -> Evidence E: -137 (74) -> Evidence F: -57 (17) -> Clue 11: -1 (16) -> Clue 10: -2 (14) -> Clue 9: -2 (12) -> Clue 6: -2 (10) -> Clue 7: -1 (9) -> Clue 8: -1 (8) -> Clue 1: -1 (7) -> Clue 2: -1 (6) -> Clue 3: -2 (4) -> Clue 4: -1 (3) -> Clue 5: -1 (2) -> Clue 12: -1 (1) |
| 14 | Sealed Check: no finalist shares the killer's check number | PASS | check number 523; other visitors with the same number: 3 of 5,999 |
| 15 | Evidence D: the Book of Brews and the stall directory give exactly the stalls in the clue (rosehip + star anise, no honey) | PASS | brews ['Hearth Chai', 'Rosehip Ember']; stalls [4, 7, 12, 16, 21, 24, 31, 35] |
| 16 | Evidence D has a trap: a brew with rosehip and star anise but also honey, sold elsewhere | PASS | Moon Fair Wassail |
| 17 | Stall directory: every stall sells two different things, every brew is sold somewhere | PASS |  |
| 18 | Evidence E: exactly one Thursday round, and its villages match the clue | PASS | [['Birchfold', 'Dunwold', 'Hatherby', 'Kittlewick', 'Owlhallow', 'Wexley']] |
| 19 | Evidence B: moon-log periods are contiguous, non-overlapping and match the clear-moon windows | PASS |  |
| 20 | Evidence C: the reading book has the crescent-pin reading at the clue's time, and its dregs match Evidence D | PASS |  |
| 21 | Evidence A: the Hob Stones lie on the paths to exactly Mill Stile and Orchard Gap | PASS |  |
| 22 | Evidence E/F: the ledger says Thursday and the margin note says the same letter twice | PASS |  |
| 23 | Killer's own story is consistent (came in under the moon before the reading, bought a rosehip-and-anise brew, lives on the Thursday round) | PASS |  |
| 24 | Finalists don't point at the answer: for entrance, village, last stall, lane and entry hour the killer's value is shared by at least two finalists, is never the single most common value, and no value covers more than half the shortlist | PASS | entrance: killer's value shared by 9 of 23 finalists, most common value 12/24; village: killer's value shared by 5 of 23 finalists, most common value 8/24; last stall: killer's value shared by 3 of 23 finalists, most common value 6/24; lane: killer's value shared by 9 of 23 finalists, most common value 12/24; entry hour: killer's value shared by 8 of 23 finalists, most common value 11/24 |
| 25 | Level-3 hints keep exactly the same visitors as their clues (all 18) | PASS |  |
| 26 | Examples and facts quoted in hints and house rules are correct | PASS | Ada and Oscar pass clue 1; Bella and Yvonne fail: ok; Ruth Barlow passes clue 2 (4 and 6), Ruth Gale fails (4 and 4): ok; Ellwood has one E (passes clue 3), Elmore two, Abbott none (both fail): ok; Oscar (5) passes clue 4, Arthur (6) fails: ok; Edwards fails clue 5, Abbott passes: ok; ticket 0472 is even (fails clue 6): ok; 0472 has one zero (passes 7), 3006 two and 1234 none (fail): ok; 18:10 and 18:39 pass clue 8; 18:09 and 18:40 fail: ok; Hint 9 level 2 names exactly the villages with an H: ok; Ida and Elsie contain an I (fail clue 12): ok; Rowan Close is stalls 28-36: ok; Glossary: 18:07 has minutes 07; 0472/3006/1234 have 1/2/0 zeros: ok; Hint D names the two brews from the Book of Brews: ok; Hint A names Mill Stile and Orchard Gap: ok |
| 27 | No hint names the killer or their ticket | PASS |  |
| 28 | No borrowed brands, titles or famous witches in any text or name pool (Hocus Pocus, Sanderson, Practical Magic, Owens, Sabrina, Charmed, Halliwell, Wicked, Elphaba, Glinda, Agatha All Along, The Craft, Harry Potter, Hogwarts, Quidditch, Hermione, Discworld, Weatherwax, Kiki, Maleficent, Ursula, Winifred, Salem ...) | PASS |  |
| 29 | No famous-detective or famous-witch names in the name pools | PASS |  |
| 30 | Story characters and the killer's own names are kept out of the random name pools | PASS |  |
| 31 | Every character in the text exists in the embedded fonts | PASS | [] |
| 32 | [letter] every clue is printed word for word in the case book | PASS |  |
| 33 | [letter] all 54 hints are printed word for word | PASS |  |
| 34 | [letter] the killer's name appears exactly once in the case book (their line in the log) | PASS | 1 times |
| 35 | [letter] Visitor Log in the PDF matches the data line for line (6,000 rows) | PASS | parsed 6000 rows |
| 36 | [letter] the book has a clickable contents page and bookmarks | PASS | 24 bookmarks, 23 links on the contents page |
| 37 | [letter] Fraunces and Nunito are embedded | PASS | AAAAAA+Caveat-Medium, AAAAAA+Fraunces-Italic, AAAAAA+Fraunces-SemiBold, AAAAAA+Nunito-Bold, AAAAAA+Nunito-ExtraBold, AAAAAA+Nunito-Italic, AAAAAA+Nunito-Regular, Helvetica |
| 38 | [letter] solution file names the same killer the code found | PASS |  |
| 39 | [letter] solution walkthrough counts match the code | PASS |  |
| 40 | [a4] every clue is printed word for word in the case book | PASS |  |
| 41 | [a4] all 54 hints are printed word for word | PASS |  |
| 42 | [a4] the killer's name appears exactly once in the case book (their line in the log) | PASS | 1 times |
| 43 | [a4] Visitor Log in the PDF matches the data line for line (6,000 rows) | PASS | parsed 6000 rows |
| 44 | [a4] the book has a clickable contents page and bookmarks | PASS | 24 bookmarks, 23 links on the contents page |
| 45 | [a4] Fraunces and Nunito are embedded | PASS | AAAAAA+Caveat-Medium, AAAAAA+Fraunces-Italic, AAAAAA+Fraunces-SemiBold, AAAAAA+Nunito-Bold, AAAAAA+Nunito-ExtraBold, AAAAAA+Nunito-Italic, AAAAAA+Nunito-Regular, Helvetica |
| 46 | [a4] solution file names the same killer the code found | PASS |  |
| 47 | [a4] solution walkthrough counts match the code | PASS |  |
| 48 | [ipad] every clue is printed word for word in the case book | PASS |  |
| 49 | [ipad] all 54 hints are printed word for word | PASS |  |
| 50 | [ipad] the killer's name appears exactly once in the case book (their line in the log) | PASS | 1 times |
| 51 | [ipad] Visitor Log in the PDF matches the data line for line (6,000 rows) | PASS | parsed 6000 rows |
| 52 | [ipad] the book has a clickable contents page and bookmarks | PASS | 24 bookmarks, 23 links on the contents page |
| 53 | [ipad] Fraunces and Nunito are embedded | PASS | AAAAAA+Caveat-Medium, AAAAAA+Fraunces-Italic, AAAAAA+Fraunces-SemiBold, AAAAAA+Nunito-Bold, AAAAAA+Nunito-ExtraBold, AAAAAA+Nunito-Italic, AAAAAA+Nunito-Regular, Helvetica |
| 54 | [ipad] solution file names the same killer the code found | PASS |  |
| 55 | [ipad] solution walkthrough counts match the code | PASS |  |

## Is every clue needed?

Visitors left when all clues except the one named are applied (1 would mean the clue is redundant).

| Clue removed | Visitors left |
|---|---|
| Clue 1 | 2 |
| Clue 2 | 2 |
| Clue 3 | 3 |
| Clue 4 | 2 |
| Clue 5 | 2 |
| Clue 6 | 2 |
| Clue 7 | 2 |
| Clue 8 | 2 |
| Clue 9 | 2 |
| Clue 10 | 2 |
| Clue 11 | 2 |
| Clue 12 | 2 |
| Evidence A | 3 |
| Evidence B | 3 |
| Evidence C | 2 |
| Evidence D | 3 |
| Evidence E | 3 |
| Evidence F | 3 |

## Misreadings tested

| Clue | Alternative reading | Visitors left | Same answer? |
|---|---|---|---|
| Clue 2 | “at least two” read as “more than two” | 1 | yes |
| Clue 3 | “exactly once” read as “at least once” | 1 | yes |
| Clue 4 | six letters itself counted as “fewer than six” | 1 | yes |
| Clue 7 | leading zeros ignored (0472 read as 472) | 1 | yes |
| Evidence B | first and last minutes of each clear spell excluded | 1 | yes |
| Evidence C | strictly before 19:40 | 1 | yes |

All 64 combinations of these readings were also covered (see the proof in the checks table).

## Walkthrough (elimination curve)

| Step | Clue | Ruled out | Left |
|---|---|---|---|
| 0 | start | 0 | 6,000 |
| 1 | Evidence B | 3,316 | 2,684 |
| 2 | Evidence A | 1,411 | 1,273 |
| 3 | Evidence C | 349 | 924 |
| 4 | Evidence D | 713 | 211 |
| 5 | Evidence E | 137 | 74 |
| 6 | Evidence F | 57 | 17 |
| 7 | Clue 11 | 1 | 16 |
| 8 | Clue 10 | 2 | 14 |
| 9 | Clue 9 | 2 | 12 |
| 10 | Clue 6 | 2 | 10 |
| 11 | Clue 7 | 1 | 9 |
| 12 | Clue 8 | 1 | 8 |
| 13 | Clue 1 | 1 | 7 |
| 14 | Clue 2 | 1 | 6 |
| 15 | Clue 3 | 2 | 4 |
| 16 | Clue 4 | 1 | 3 |
| 17 | Clue 5 | 1 | 2 |
| 18 | Clue 12 | 1 | 1 |

## Finalists (fit every clue but one)

| Ticket | Visitor | Ruled out only by |
|---|---|---|
| 1707 | Alma Ashwell | Evidence B |
| 2075 | Ada Anstey | Evidence B |
| 5905 | Emma Ellwood | Evidence A |
| 5015 | Enoch Edgworth | Evidence A |
| 4409 | Olga Openshaw | Evidence C |
| 3703 | Ansel Atherton | Evidence D |
| 1065 | Oona Oxenford | Evidence D |
| 5073 | Ulla Underwood | Evidence E |
| 3209 | Eden Enright | Evidence E |
| 5207 | Una Ilsley | Evidence F |
| 4909 | Uma Napier | Evidence F |
| 1045 | Otto Ormerod | Clue 11 |
| 4201 | Elva Eckford | Clue 10 |
| 3301 | Abel Ashendon | Clue 9 |
| 5870 | Etta Eastham | Clue 6 |
| 3887 | Orson Oldfield | Clue 7 |
| 1017 | Ezra Ellingham | Clue 8 |
| 5077 | Nora Newbolt | Clue 1 |
| 3059 | Oscar Ockley | Clue 2 |
| 3069 | Arlo Ackroyd | Clue 3 |
| 4027 | Alba Arkwright | Clue 3 |
| 5307 | Augusta Applegarth | Clue 4 |
| 1037 | Ebba Edwards | Clue 5 |
| 3023 | Ivy Ireton | Clue 12 |

## Is the shortlist free of patterns?

- entrance: killer's value shared by 9 of 23 finalists, most common value 12/24
- village: killer's value shared by 5 of 23 finalists, most common value 8/24
- last stall: killer's value shared by 3 of 23 finalists, most common value 6/24
- lane: killer's value shared by 9 of 23 finalists, most common value 12/24
- entry hour: killer's value shared by 8 of 23 finalists, most common value 11/24

## Page counts

- book_letter: 138
- solution_letter: 13
- book_a4: 129
- solution_a4: 13
- book_ipad: 117
- solution_ipad: 11
