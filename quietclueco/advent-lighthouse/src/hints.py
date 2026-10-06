"""Three-level hints for every window (3-23). Facts are computed from case.py, so a hint can never
disagree with the papers; verify.py re-checks them anyway."""
import case as C

def _list(xs):
    xs = [str(x) for x in xs]
    return ", ".join(xs[:-1]) + " and " + xs[-1] if len(xs) > 1 else xs[0]
def _or(xs):
    xs = [str(x) for x in xs]
    return ", ".join(xs[:-1]) + " or " + xs[-1] if len(xs) > 1 else xs[0]

UP_LOCH = [n for n in C.LANDINGS if C.above_narrows(n)]
IN_RANGE = [v for v in C.HOMES if C.in_range(v)]
BETWEEN = [v for v in C.HOMES if C.between_heads(v)]
OTHER_BOATS = [b for b in C.BOATS if b not in C.INNER]
RISE = {d: [(a, b) for (a, ka), (b, kb) in zip(C.tide_events(d), C.tide_events(d)[1:]) if ka == "LW" and kb == "HW"]
        for d in (1, 2, 3)}
RISE_TEXT = "; ".join(f"{d} December {_or([f'{C.tstr(a)}–{C.tstr(b)}' for a, b in RISE[d]])}" for d in (1, 2, 3))
LIGHT_TEXT = ", ".join(f"{C.tstr(C.LIGHTING[d])} on the {d}{'st' if d == 1 else ('nd' if d == 2 else 'rd')}"
                       for d in (1, 2, 3))

HINTS = {
    "3": ["Think about when Ezra wrote this, and what having a tally means.",
          "A tally is given on the first crossing, and the first crossing is the line in the Sound Book. By the "
          "evening of 3 December he already had his, so that line is dated 3 December or earlier.",
          "His line is dated 1, 2 or 3 December. The Sound Book is in date order: cross out every chapter from "
          "4 December to 23 December."],
    "4": ["Read the note of the passages: which boats use the Inner Passage?",
          "The Inner Passage runs between Candleholm and the Dulse Reef. The Tender and the Pilot Cutter "
          "draw too much water for it and go round outside.",
          f"His boat was Mail or Fishing. Cross out every line whose boat is {_or(OTHER_BOATS)}."],
    "5": ["Find the Narrows on the chart, then follow Loch Tarrisk from its mouth towards its head.",
          "Higher up the loch means further from the sea than the Narrows, along the water. The Narrows Slip "
          "(12) is at the Narrows itself, not above it.",
          f"His landing is {_or(UP_LOCH)}. Cross out every line with any other landing number."],
    "6": ["Find the dashed circle around Candleholm Light on the chart.",
          "The circle shows how far the light can be seen: 12 miles. Inside the circle means within sight. "
          "Skellan sits right on the line, not inside it.",
          f"His village is {_or(IN_RANGE)}. Cross out every line from any other village."],
    "7": ["Look the letters up in the code book page: which ones start with a dash?",
          "A dash is a long flash. Look only at the first symbol of each letter: G is – – · and starts with a "
          "dash; A is · – and starts with a dot.",
          f"The surname begins with {_or(C.DASH_FIRST)}. Cross out every line whose surname begins with any "
          "other letter."],
    "8": ["Look only at the first name.",
          "Capital or small makes no difference: Agnes and Clara both contain an A.",
          "Cross out every line whose first name has no A in it."],
    "9": ["Which numbers hang on the left-hand board?",
          "Even numbers end in 0, 2, 4, 6 or 8. Tally 0472 is even.",
          "Cross out every line whose tally number ends in 1, 3, 5, 7 or 9."],
    "10": ["Use the tide table for his date. Is the water going up or down at his time?",
           "The tide is making (rising) from a low water until the next high water. On the first three days "
           "of the month that is the middle of the day.",
           f"The tide was rising on {RISE_TEXT}. Cross out every line whose time is outside the rising tide "
           "on its own date."],
    "11": ["Find Gannet Head and Selkie Ness on the chart. Which villages are on the coast between them?",
           "Follow the open coast south from Gannet Head to Selkie Ness. Villages on Loch Tarrisk, inland or on "
           "Inishvarra are not on that stretch of coast.",
           f"His village is {_or(BETWEEN)}. Cross out every line from any other village."],
    "12": ["Read the waybill carefully: where can a parcel be collected?",
           "Parcels are left only in the parcel sheds. The letter boxes take letters, not parcels.",
           f"His landing is {_or(C.PARCEL_SHEDS)}. Cross out every line with any other landing number."],
    "13": ["Count the letters of the first name.",
           "Exactly five letters: Moira, Grant and Morag count; Ruth (4) and Fergus (6) don’t.",
           "Cross out every line whose first name has fewer or more than five letters."],
    "14": ["Add up the four digits of the tally number, zeros included.",
           "Tally 0472: 0 + 4 + 7 + 2 = 13, not more than fifteen. Tally 1395: 1 + 3 + 9 + 5 = 18, more than "
           "fifteen. Exactly fifteen is not more than fifteen.",
           "Cross out every line whose four digits add up to 15 or less."],
    "15": ["Look only at the last letter of each name.",
           "Compare the last letter of the first name with the last letter of the surname: Angus Ross ends S "
           "and S (the same); Moira Bain ends A and N (different).",
           "Cross out every line whose first name and surname end with the same letter."],
    "16": ["Use the almanac: when was the lamp lit on his date? Then turn it into the 24-hour clock.",
           "Lighting-up time is in the afternoon: 3.46 p.m. is 15:46. He stepped aboard before that.",
           f"Lighting-up was at {LIGHT_TEXT}. Cross out every line whose time is at or after lighting-up on its "
           "own date."],
    "17": ["Look at the first letter of each name.",
           "The first name’s initial must come later in the alphabet: Sadie Kerr (S after K) fits; Ada Muir "
           "(A before M) and Mary Muir (the same letter) don’t.",
           "Cross out every line whose first name begins with a letter that comes earlier in the alphabet than "
           "the surname’s first letter, or with the same letter."],
    "18": ["Read all four digits of the tally number as printed.",
           "A tally always has four digits, so 0472 has a nought in front. 1395 has none.",
           "Cross out every line whose tally number has a 0 anywhere in it."],
    "19": ["Count the vowels in the surname.",
           "Count every A, E, I, O and U, even when the same one comes twice; Y never counts. Moffat has two "
           "(O, A); Lindsay has two (I, A); Ogilvie has four.",
           "Cross out every line whose surname has fewer or more than two vowels."],
    "20": ["Read the note of the tally metals.",
           "Copper tallies are numbered from 0801 to 1600.",
           "Cross out every line whose tally number is 0800 or lower, or 1601 or higher."],
    "21": ["Look only at the last letter of the first name.",
           "A, E, I, O and U are vowels; every other letter is a consonant, Y included. Angus and Mary end on a "
           "consonant; Effie and Flora don’t.",
           "Cross out every line whose first name ends in A, E, I, O or U."],
    "22": ["Look at every letter of the surname.",
           "If any letter appears twice, even far apart, a stencil was used twice: Rennison fails (N), "
           "Laidlaw fails (L, A), Barclay fails (A), Munro passes.",
           "Cross out every line whose surname uses any letter more than once."],
    "23": ["Count the letters of the first name and the surname, then add them together.",
           "Red, white, red, white: the last stripe is white when the number of stripes is even. Iona Rae has "
           "4 + 3 = 7 letters, which is odd.",
           "Cross out every line whose first name and surname together have an odd number of letters."],
}
LEVEL_NAMES = ["Level 1 — A gentle nudge", "Level 2 — A stronger push", "Level 3 — Nearly the answer"]
