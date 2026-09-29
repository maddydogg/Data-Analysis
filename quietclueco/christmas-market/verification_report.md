# Verification report: Snowfall at Ember Square

Result: **49 of 49 checks passed** — ALL CLEAR

Answer found by the code: **Hazel Russell**, ticket 3857, Marrowby, entered 19:23 via the South Gate, last stall 22.

## Checks

| # | Check | Result | Detail |
|---|---|---|---|
| 1 | Tickets 0001-6000, each exactly once | PASS |  |
| 2 | Every full name is unique | PASS |  |
| 3 | Names are letters only (no spaces, hyphens, apostrophes) | PASS |  |
| 4 | Entry times within opening hours 16:00-20:29 | PASS |  |
| 5 | Towns, gates and stalls are valid | PASS |  |
| 6 | Log is sorted by entry time | PASS |  |
| 7 | Unique answer: all 18 clues together leave exactly one visitor | PASS | survivors: ['Hazel Russell #3857'] |
| 8 | Every clue is needed: removing any one leaves more than one visitor | PASS | Clue 1 removed -> 2 left; Clue 2 removed -> 2 left; Clue 3 removed -> 2 left; Clue 4 removed -> 3 left; Clue 5 removed -> 2 left; Clue 6 removed -> 3 left; Clue 7 removed -> 2 left; Clue 8 removed -> 2 left; Clue 9 removed -> 2 left; Clue 10 removed -> 2 left; Clue 11 removed -> 2 left; Clue 12 removed -> 2 left; Evidence A removed -> 2 left; Evidence B removed -> 4 left; Evidence C removed -> 2 left; Evidence D removed -> 3 left; Evidence E removed -> 4 left; Evidence F removed -> 3 left |
| 9 | Each alternative reading on its own gives the same single answer | PASS | Clue 2 [“more” read as “at least as many”] -> 1; Clue 3 [“later” read as “the same or later”] -> 1; Clue 4 [Y counted as a vowel] -> 1; Clue 4 [repeated vowels counted once] -> 1; Clue 5 [Y counted as a vowel] -> 1; Clue 6 [“or higher” missed (strictly above 2500)] -> 1; Evidence A [only the footbridge gate nearest the carousel] -> 1; Evidence B [first and last minutes of each snowfall excluded] -> 1; Evidence C [strictly before 19:48] -> 1; Evidence F [any letter used twice, not necessarily side by side] -> 1 |
| 10 | Every combination of readings (768 in total) gives the same answer | PASS | proof: the killer passes every clue under every reading, and each of the other 5,999 visitors fails at least one clue under every reading |
| 11 | Every clue rules out at least one finalist (a visitor who fits all the other clues) | PASS | {'1': 1, '2': 1, '3': 1, '4': 2, '5': 1, '6': 2, '7': 1, '8': 1, '9': 1, '10': 1, '11': 1, '12': 1, 'A': 1, 'B': 3, 'C': 1, 'D': 2, 'E': 3, 'F': 2} |
| 12 | Walkthrough uses all 18 clues once and ends on the killer | PASS |  |
| 13 | No step in the walkthrough rules out zero visitors | PASS | Evidence B: -3235 (2765) -> Evidence A: -1555 (1210) -> Evidence C: -60 (1150) -> Evidence D: -912 (238) -> Evidence E: -147 (91) -> Evidence F: -28 (63) -> Clue 9: -12 (51) -> Clue 11: -8 (43) -> Clue 10: -18 (25) -> Clue 6: -7 (18) -> Clue 7: -9 (9) -> Clue 8: -1 (8) -> Clue 1: -1 (7) -> Clue 2: -1 (6) -> Clue 3: -1 (5) -> Clue 4: -2 (3) -> Clue 5: -1 (2) -> Clue 12: -1 (1) |
| 14 | Sealed Check: no finalist shares the killer's check number | PASS | check number 011; other visitors with the same number: 7 of 5,999 |
| 15 | Evidence D: the stall directory's punch sellers match the clue | PASS | [2, 5, 11, 20, 22, 25, 31] |
| 16 | Evidence E: exactly one coach leaves at 21:15, and its towns match the clue | PASS | [['Ashcombe', 'Dunmoor', 'Hartwell', 'Juniper Cross', 'Kestrel Bay', 'Marrowby', 'Oakhurst']] |
| 17 | Evidence B: weather log periods are contiguous, non-overlapping and match the snow windows | PASS |  |
| 18 | Evidence A: footbridges drawn at exactly the East and South gates | PASS |  |
| 19 | Killer's own story is consistent (entered before buying, bought punch at a punch stall, lives on the 21:15 route) | PASS |  |
| 20 | Level-3 hints keep exactly the same visitors as their clues (all 18) | PASS |  |
| 21 | Examples and facts quoted in hints and house rules are correct | PASS | Ida 3, Enid 4, Clara 5, Martha 6 letters: ok; Bennett has exactly two vowels: ok; Molly and Percy end in Y and pass clue 5: ok; ticket 0472 digits sum to 13: ok; 18:07 odd minutes, 18:40 even: ok; Oakes and Brook contain O: ok; Bell and Abbott have double letters; Garner repeats R but has no double letter: ok; Ada Webb passes clue 3: ok; Hint 9 names exactly the two-word towns: ok; Hint A names the footbridge gates: ok; Hint B quotes both snow windows: ok; Hint C quotes the receipt time: ok; Glossary example Garner is not a visitor surname (it is only an example): ok |
| 22 | No hint names the killer or their ticket | PASS |  |
| 23 | No borrowed brands or titles (Killer Isn't, Clue/Cluedo, Traitors, Christie, Sherlock, ...) | PASS |  |
| 24 | No famous-detective surnames in the name pool | PASS |  |
| 25 | Every character in the text exists in the embedded fonts | PASS | [] |
| 26 | [letter] every clue is printed word for word in the case book | PASS |  |
| 27 | [letter] all 54 hints are printed word for word | PASS |  |
| 28 | [letter] the killer's name appears exactly once in the case book (their line in the log) | PASS | 1 times |
| 29 | [letter] Visitor Log in the PDF matches the data line for line (6,000 rows) | PASS | parsed 6000 rows |
| 30 | [letter] the book has a clickable contents page and bookmarks | PASS | 24 bookmarks, 23 links on the contents page |
| 31 | [letter] Fraunces and Nunito are embedded | PASS | AAAAAA+Caveat-Medium, AAAAAA+CourierPrime-Bold, AAAAAA+CourierPrime-Regular, AAAAAA+Fraunces-Italic, AAAAAA+Fraunces-SemiBold, AAAAAA+Nunito-Bold, AAAAAA+Nunito-ExtraBold, AAAAAA+Nunito-Italic, AAAAAA+Nunito-Regular, Helvetica |
| 32 | [letter] solution file names the same killer the code found | PASS |  |
| 33 | [letter] solution walkthrough counts match the code | PASS |  |
| 34 | [a4] every clue is printed word for word in the case book | PASS |  |
| 35 | [a4] all 54 hints are printed word for word | PASS |  |
| 36 | [a4] the killer's name appears exactly once in the case book (their line in the log) | PASS | 1 times |
| 37 | [a4] Visitor Log in the PDF matches the data line for line (6,000 rows) | PASS | parsed 6000 rows |
| 38 | [a4] the book has a clickable contents page and bookmarks | PASS | 24 bookmarks, 23 links on the contents page |
| 39 | [a4] Fraunces and Nunito are embedded | PASS | AAAAAA+Caveat-Medium, AAAAAA+CourierPrime-Bold, AAAAAA+CourierPrime-Regular, AAAAAA+Fraunces-Italic, AAAAAA+Fraunces-SemiBold, AAAAAA+Nunito-Bold, AAAAAA+Nunito-ExtraBold, AAAAAA+Nunito-Italic, AAAAAA+Nunito-Regular, Helvetica |
| 40 | [a4] solution file names the same killer the code found | PASS |  |
| 41 | [a4] solution walkthrough counts match the code | PASS |  |
| 42 | [ipad] every clue is printed word for word in the case book | PASS |  |
| 43 | [ipad] all 54 hints are printed word for word | PASS |  |
| 44 | [ipad] the killer's name appears exactly once in the case book (their line in the log) | PASS | 1 times |
| 45 | [ipad] Visitor Log in the PDF matches the data line for line (6,000 rows) | PASS | parsed 6000 rows |
| 46 | [ipad] the book has a clickable contents page and bookmarks | PASS | 24 bookmarks, 23 links on the contents page |
| 47 | [ipad] Fraunces and Nunito are embedded | PASS | AAAAAA+Caveat-Medium, AAAAAA+CourierPrime-Bold, AAAAAA+CourierPrime-Regular, AAAAAA+Fraunces-Italic, AAAAAA+Fraunces-SemiBold, AAAAAA+Nunito-Bold, AAAAAA+Nunito-ExtraBold, AAAAAA+Nunito-Italic, AAAAAA+Nunito-Regular, Helvetica |
| 48 | [ipad] solution file names the same killer the code found | PASS |  |
| 49 | [ipad] solution walkthrough counts match the code | PASS |  |

## Is every clue needed?

Visitors left when all clues except the one named are applied (1 would mean the clue is redundant).

| Clue removed | Visitors left |
|---|---|
| Clue 1 | 2 |
| Clue 2 | 2 |
| Clue 3 | 2 |
| Clue 4 | 3 |
| Clue 5 | 2 |
| Clue 6 | 3 |
| Clue 7 | 2 |
| Clue 8 | 2 |
| Clue 9 | 2 |
| Clue 10 | 2 |
| Clue 11 | 2 |
| Clue 12 | 2 |
| Evidence A | 2 |
| Evidence B | 4 |
| Evidence C | 2 |
| Evidence D | 3 |
| Evidence E | 4 |
| Evidence F | 3 |

## Misreadings tested

| Clue | Alternative reading | Visitors left | Same answer? |
|---|---|---|---|
| Clue 2 | “more” read as “at least as many” | 1 | yes |
| Clue 3 | “later” read as “the same or later” | 1 | yes |
| Clue 4 | Y counted as a vowel | 1 | yes |
| Clue 4 | repeated vowels counted once | 1 | yes |
| Clue 5 | Y counted as a vowel | 1 | yes |
| Clue 6 | “or higher” missed (strictly above 2500) | 1 | yes |
| Evidence A | only the footbridge gate nearest the carousel | 1 | yes |
| Evidence B | first and last minutes of each snowfall excluded | 1 | yes |
| Evidence C | strictly before 19:48 | 1 | yes |
| Evidence F | any letter used twice, not necessarily side by side | 1 | yes |

All 768 combinations of these readings were also covered (see the proof in the checks table).

## Walkthrough (elimination curve)

| Step | Clue | Ruled out | Left |
|---|---|---|---|
| 0 | start | 0 | 6,000 |
| 1 | Evidence B | 3,235 | 2,765 |
| 2 | Evidence A | 1,555 | 1,210 |
| 3 | Evidence C | 60 | 1,150 |
| 4 | Evidence D | 912 | 238 |
| 5 | Evidence E | 147 | 91 |
| 6 | Evidence F | 28 | 63 |
| 7 | Clue 9 | 12 | 51 |
| 8 | Clue 11 | 8 | 43 |
| 9 | Clue 10 | 18 | 25 |
| 10 | Clue 6 | 7 | 18 |
| 11 | Clue 7 | 9 | 9 |
| 12 | Clue 8 | 1 | 8 |
| 13 | Clue 1 | 1 | 7 |
| 14 | Clue 2 | 1 | 6 |
| 15 | Clue 3 | 1 | 5 |
| 16 | Clue 4 | 2 | 3 |
| 17 | Clue 5 | 1 | 2 |
| 18 | Clue 12 | 1 | 1 |

## Finalists (fit every clue but one)

| Ticket | Visitor | Ruled out only by |
|---|---|---|
| 2818 | Emily Wadding | Evidence B |
| 3475 | Mavis Tanner | Evidence B |
| 5062 | Mabel Tidwell | Evidence B |
| 3514 | Edgar Nuttall | Evidence A |
| 3785 | Kit Miller | Evidence C |
| 5329 | Agnes Linnell | Evidence D |
| 5318 | Sybil Wadding | Evidence D |
| 3855 | Ethel Farrell | Evidence E |
| 5026 | Abigail Bramwell | Evidence E |
| 5433 | Daisy Ferrand | Evidence E |
| 3859 | Bridget Chandler | Evidence F |
| 4366 | Bernard Starling | Evidence F |
| 2753 | Leonard Skerritt | Clue 9 |
| 3374 | Edith Winnard | Clue 11 |
| 4814 | Ethel Tebbutt | Clue 10 |
| 0601 | Emily Jarrett | Clue 6 |
| 1666 | Cyril Perrin | Clue 6 |
| 4334 | Oscar Parrish | Clue 7 |
| 2702 | Ralph Sheppard | Clue 8 |
| 5408 | Esther Jarrett | Clue 1 |
| 2764 | Beatrix Innes | Clue 2 |
| 3420 | Ned Garnett | Clue 3 |
| 5303 | Gilbert Kerrigan | Clue 4 |
| 4878 | Silas Wheeler | Clue 4 |
| 5196 | Elsie Lennard | Clue 5 |
| 3440 | Cecil Pinnock | Clue 12 |

## Page counts

- book_letter: 138
- solution_letter: 13
- book_a4: 129
- solution_a4: 13
- book_ipad: 117
- solution_ipad: 11
