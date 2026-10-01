# Verification report: Storm over Corvenmoor

Result: **49 of 49 checks passed** — ALL CLEAR

Answer found by the code: **Isabel Pettit**, ticket 2719, Gloamford, entered 19:17 via the West Gate, last booth 33.

## Checks

| # | Check | Result | Detail |
|---|---|---|---|
| 1 | Tickets 0001-6000, each exactly once | PASS |  |
| 2 | Every full name is unique | PASS |  |
| 3 | Names are letters only (no spaces, hyphens, apostrophes) | PASS |  |
| 4 | Entry times within opening hours 16:00-20:29 | PASS |  |
| 5 | Towns, gates and stalls are valid | PASS |  |
| 6 | Log is sorted by entry time | PASS |  |
| 7 | Unique answer: all 18 clues together leave exactly one visitor | PASS | survivors: ['Isabel Pettit #2719'] |
| 8 | Every clue is needed: removing any one leaves more than one visitor | PASS | Clue 1 removed -> 2 left; Clue 2 removed -> 2 left; Clue 3 removed -> 3 left; Clue 4 removed -> 2 left; Clue 5 removed -> 2 left; Clue 6 removed -> 3 left; Clue 7 removed -> 2 left; Clue 8 removed -> 2 left; Clue 9 removed -> 2 left; Clue 10 removed -> 2 left; Clue 11 removed -> 2 left; Clue 12 removed -> 2 left; Evidence A removed -> 2 left; Evidence B removed -> 3 left; Evidence C removed -> 2 left; Evidence D removed -> 3 left; Evidence E removed -> 4 left; Evidence F removed -> 4 left |
| 9 | Each alternative reading on its own gives the same single answer | PASS | Clue 3 [N itself left out (only O to Z)] -> 1; Clue 5 [Y counted as a vowel] -> 1; Clue 6 [4000 itself counted as “below”] -> 1; Clue 7 [“bigger” read as “the same or bigger”] -> 1; Evidence A [only the gargoyle gate beside the Laboratory Tower] -> 1; Evidence B [first and last minutes of each storm excluded] -> 1; Evidence C [strictly before 19:52] -> 1 |
| 10 | Every combination of readings (128 in total) gives the same answer | PASS | proof: the killer passes every clue under every reading, and each of the other 5,999 visitors fails at least one clue under every reading |
| 11 | Every clue rules out at least one finalist (a visitor who fits all the other clues) | PASS | {'1': 1, '2': 1, '3': 2, '4': 1, '5': 1, '6': 2, '7': 1, '8': 1, '9': 1, '10': 1, '11': 1, '12': 1, 'A': 1, 'B': 2, 'C': 1, 'D': 2, 'E': 3, 'F': 3} |
| 12 | Walkthrough uses all 18 clues once and ends on the killer | PASS |  |
| 13 | No step in the walkthrough rules out zero visitors | PASS | Evidence B: -3362 (2638) -> Evidence A: -1195 (1443) -> Evidence C: -221 (1222) -> Evidence D: -1004 (218) -> Evidence E: -122 (96) -> Evidence F: -50 (46) -> Clue 11: -17 (29) -> Clue 10: -10 (19) -> Clue 9: -3 (16) -> Clue 6: -4 (12) -> Clue 7: -1 (11) -> Clue 8: -3 (8) -> Clue 1: -1 (7) -> Clue 2: -1 (6) -> Clue 3: -2 (4) -> Clue 4: -1 (3) -> Clue 5: -1 (2) -> Clue 12: -1 (1) |
| 14 | Sealed Check: no finalist shares the killer's check number | PASS | check number 045; other visitors with the same number: 2 of 5,999 |
| 15 | Evidence D: the booth directory's potion-punch sellers match the clue | PASS | [5, 8, 15, 20, 24, 33] |
| 16 | Evidence E: exactly one night bus leaves at 21:20, and its towns match the clue | PASS | [['Ashwick Fen', 'Duskwater', 'Gloamford', 'Mothwell', 'Pikesmere', 'Ravensholt', 'Underfell']] |
| 17 | Evidence B: weather log periods are contiguous, non-overlapping and match the thunderstorm windows | PASS |  |
| 18 | Evidence A: gargoyles are drawn above exactly the North and West gates, and the Laboratory Tower stands beside one of them | PASS |  |
| 19 | Killer's own story is consistent (entered in a storm before buying, bought potion punch at a potion booth, lives on the night-bus route) | PASS |  |
| 20 | Level-3 hints keep exactly the same visitors as their clues (all 18) | PASS |  |
| 21 | Examples and facts quoted in hints and house rules are correct | PASS | Ida 3, Nora 4, Clara 5, Martha 6 letters: ok; Bella Beck fails clue 2, Bella Monk passes: ok; Napier passes clue 3: ok; Ada, Clara and Nancy contain an A: ok; Fairley ends in Y and passes clue 5: ok; ticket 4000 fails clue 6: ok; ticket 0472 passes clue 7; a ticket like 3003 fails it: ok; 18:29 passes clue 8, 18:30 fails: ok; Rook and Barlow contain R: ok; Hint 9 names exactly the towns after M: ok; Hint A names the gargoyle gates: ok; Hint B quotes both storm windows: ok; Hint C quotes the receipt time: ok; Glossary: 18:07 has minutes 07, ticket 0472 first digit 0 last digit 2: ok |
| 22 | No hint names the killer or their ticket | PASS |  |
| 23 | No borrowed brands or titles (Killer Isn't, Cluedo, Traitors, Christie, Sherlock, Frankenstein, Dracula, competitor titles ...) | PASS |  |
| 24 | No famous-detective or famous-monster names in the name pools | PASS |  |
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
| Clue 3 | 3 |
| Clue 4 | 2 |
| Clue 5 | 2 |
| Clue 6 | 3 |
| Clue 7 | 2 |
| Clue 8 | 2 |
| Clue 9 | 2 |
| Clue 10 | 2 |
| Clue 11 | 2 |
| Clue 12 | 2 |
| Evidence A | 2 |
| Evidence B | 3 |
| Evidence C | 2 |
| Evidence D | 3 |
| Evidence E | 4 |
| Evidence F | 4 |

## Misreadings tested

| Clue | Alternative reading | Visitors left | Same answer? |
|---|---|---|---|
| Clue 3 | N itself left out (only O to Z) | 1 | yes |
| Clue 5 | Y counted as a vowel | 1 | yes |
| Clue 6 | 4000 itself counted as “below” | 1 | yes |
| Clue 7 | “bigger” read as “the same or bigger” | 1 | yes |
| Evidence A | only the gargoyle gate beside the Laboratory Tower | 1 | yes |
| Evidence B | first and last minutes of each storm excluded | 1 | yes |
| Evidence C | strictly before 19:52 | 1 | yes |

All 128 combinations of these readings were also covered (see the proof in the checks table).

## Walkthrough (elimination curve)

| Step | Clue | Ruled out | Left |
|---|---|---|---|
| 0 | start | 0 | 6,000 |
| 1 | Evidence B | 3,362 | 2,638 |
| 2 | Evidence A | 1,195 | 1,443 |
| 3 | Evidence C | 221 | 1,222 |
| 4 | Evidence D | 1,004 | 218 |
| 5 | Evidence E | 122 | 96 |
| 6 | Evidence F | 50 | 46 |
| 7 | Clue 11 | 17 | 29 |
| 8 | Clue 10 | 10 | 19 |
| 9 | Clue 9 | 3 | 16 |
| 10 | Clue 6 | 4 | 12 |
| 11 | Clue 7 | 1 | 11 |
| 12 | Clue 8 | 3 | 8 |
| 13 | Clue 1 | 1 | 7 |
| 14 | Clue 2 | 1 | 6 |
| 15 | Clue 3 | 2 | 4 |
| 16 | Clue 4 | 1 | 3 |
| 17 | Clue 5 | 1 | 2 |
| 18 | Clue 12 | 1 | 1 |

## Finalists (fit every clue but one)

| Ticket | Visitor | Ruled out only by |
|---|---|---|
| 1317 | Tobias Sutton | Evidence B |
| 2316 | Ursula Onslow | Evidence B |
| 1745 | Lena Sallis | Evidence A |
| 1123 | Bertha Swales | Evidence C |
| 1245 | Fabian Wallis | Evidence D |
| 1618 | Miriam Tebbit | Evidence D |
| 3446 | Dorian Witton | Evidence E |
| 0543 | Magnus Witton | Evidence E |
| 2124 | Fabian Swales | Evidence E |
| 2963 | Walter Pennick | Evidence F |
| 2083 | Vera Skelton | Evidence F |
| 0606 | Cora Pickles | Evidence F |
| 1795 | Martha Wallis | Clue 11 |
| 0899 | Maisie Osgood | Clue 10 |
| 2794 | Ezra Wilmot | Clue 9 |
| 4829 | Nora Witton | Clue 6 |
| 4509 | Ursula Padley | Clue 6 |
| 3842 | Magnus Sefton | Clue 7 |
| 1243 | Dahlia Stokes | Clue 8 |
| 2385 | Bella Pellow | Clue 1 |
| 2515 | Philippa Phelps | Clue 2 |
| 0922 | Hannah Ibbott | Clue 3 |
| 2196 | Walter Jessop | Clue 3 |
| 3387 | Winnie Pocock | Clue 4 |
| 1312 | Marian Quayle | Clue 5 |
| 1234 | Lucian Tasker | Clue 12 |

## Page counts

- book_letter: 138
- solution_letter: 14
- book_a4: 130
- solution_a4: 14
- book_ipad: 117
- solution_ipad: 11
