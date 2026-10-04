"""Three-level hints for every window (3-23). Facts are computed from case.py, so a hint can
never disagree with the documents; verify.py re-checks them anyway."""
import case as C

BANDS = ", ".join(f"{a}–{b}" for a, b in C.BAND_SETS[:-1]) + " and " + "–".join(C.BAND_SETS[-1])
STOPS = [s for s, _ in C.TRAM7]
_a, _b = STOPS.index(C.TRAM_FROM), STOPS.index(C.TRAM_TO)
TRAM_IN = [d for _, d in C.TRAM7[_a + 1:_b]]
TRAM_OUT = [d for d in C.DISTRICTS if d not in TRAM_IN]
PARK_IN = [d for d in C.DISTRICTS if C.touches_park(d)]
PARK_OUT = [d for d in C.DISTRICTS if not C.touches_park(d)]
UP = [n for n in C.DEPTS if C.above_toy_hall(n)]
CUPS = C.CUP_DEPTS
def _list(xs):
    xs = [str(x) for x in xs]
    return ", ".join(xs[:-1]) + " and " + xs[-1] if len(xs) > 1 else xs[0]
def _or(xs):
    xs = [str(x) for x in xs]
    return ", ".join(xs[:-1]) + " or " + xs[-1] if len(xs) > 1 else xs[0]

HINTS = {
    "3": ["The doorman can’t give a time, but he says what was happening on the steps when she came in.",
          "The band’s programme shows three sets with breaks between them. Only the sets count, and the "
          "first and last minutes of each set count too.",
          f"The band played {BANDS}. Cross out every pass whose time in is outside all three sets. The "
          "register is sorted by time, so whole pages go at once."],
    "4": ["Find the tram shelter on the street plan in Window 1, then follow both ways in that the "
          "newsvendor describes. Each way ends at a door.",
          "Straight across Tramway Yard is one door; through the Winter Garden glasshouse is another. "
          "She used one of those two, and the newsvendor can’t say which, so keep both.",
          "Cross out every pass that came in by the Arcade Door or the Clock Door."],
    "5": ["Find the Toy Hall on the store plan. What is higher up in the building?",
          "Higher up than the Second Floor means everything above it on the plan, including the levels "
          "between floors and the roof. She never came back down, so her last till is up there.",
          f"Her last till is {_or(UP)}. Cross out every pass whose last till is any other number."],
    "6": ["Find Route 7 on the city map and follow it from Vell Bridge to Gasworks. Which stops lie "
          "between those two?",
          "‘Between’ means the stops in the middle, not Vell Bridge or Gasworks themselves. Each stop lies "
          "in a district.",
          f"The stops between are in {_list(TRAM_IN)}. Cross out every pass from any other district."],
    "7": ["Look only at the first name.",
          "Capital or small makes no difference: Rita and Laura both contain an R.",
          "Cross out every pass whose first name has no R in it."],
    "8": ["The wrapping desk has two racks. Which one did her parcel go in?",
          "The second rack is N to Z, and parcels are filed by surname. Look at the first letter of the "
          "surname only.",
          "Cross out every pass whose surname begins with any letter from A to M."],
    "9": ["This one uses the Pass column.",
          "Odd numbers end in 1, 3, 5, 7 or 9. Pass 0472 is even.",
          "Cross out every pass whose number ends in 0, 2, 4, 6 or 8."],
    "10": ["Read the store guide on the notice board. Whose clock is the time ‘seven o’clock’ measured by?",
           "The gallery clocks run five minutes fast, so seven o’clock by them is earlier in real time. "
           "She was already in the store by then.",
           f"The tree was lit at {C.tstr(C.TREE_REAL)} real time. Cross out every pass that came in at "
           f"{C.tstr(C.TREE_REAL + 1)} or later."],
    "11": ["Find Vell Park on the city map. Which districts are next to it?",
           "Next to the park means sharing a side with it, not just touching a corner. There are four.",
           f"The districts next to the park are {_list(PARK_IN)}. Cross out every pass from any other district."],
    "12": ["Remember the house rule about the striped cup: it was her last purchase of the night.",
           "The store guide names the only four counters that serve hot drinks in striped cups. Tins and "
           "powder don’t come in cups.",
           f"Her last till is {_or(CUPS)}. Cross out every pass whose last till is any other number."],
    "13": ["Look only at the last letter of the first name.",
           "A, E, I, O and U are vowels; Y never counts. Laura and Annie end on a vowel; Henry and Mabel don’t.",
           "Cross out every pass whose first name ends with any letter other than A, E, I, O or U."],
    "14": ["Add up the four digits of the pass number, zeros included.",
           "Pass 0472: 0 + 4 + 7 + 2 = 13, more than ten. Pass 2310: 2 + 3 + 1 + 0 = 6, not more than ten. "
           "Exactly ten is not more than ten.",
           "Cross out every pass whose four digits add up to 10 or less."],
    "15": ["Look at the surname letter by letter.",
           "A double letter is the same letter twice, side by side: the LL in Wallace counts, the two Rs in "
           "Carrier count, but the two Es in Hebden don’t (they’re apart). Capital or small makes no difference.",
           "Cross out every pass whose surname has no letter written twice side by side."],
    "16": ["Picture the little clock face on the door stamp. Which minutes point into its lower half?",
           "The lower half of a clock face is everything below a line from 9 to 3. The hand points there "
           "from a quarter past to a quarter to.",
           "The minutes run from 15 to 45. Cross out every pass whose time in has minutes 00 to 14 or 46 to 59."],
    "17": ["Count the letters in both names and compare the two counts.",
           "More letters means strictly more: Ruth (4) and Barlow (6) count; Ruth and Gale (4 and 4) don’t.",
           "Cross out every pass whose surname has the same number of letters as the first name, or fewer."],
    "18": ["Read all four digits of the pass number as printed.",
           "All different means no digit appears twice: 4825 qualifies, 1301 doesn’t (two 1s), 0402 doesn’t "
           "(two 0s).",
           "Cross out every pass whose number uses any digit more than once."],
    "19": ["Count the letters of the first name.",
           "Exactly six letters: Marina and Gertie count; Clara (5) and Harriet (7) don’t.",
           "Cross out every pass whose first name has fewer or more than six letters."],
    "20": ["The printer’s note tells you which numbers were printed on which colour.",
           "Green passes were 0001 to 1200, red passes 1201 to 2400.",
           "Cross out every pass numbered 1200 or lower."],
    "21": ["Look for the letter E in the surname, capital or small.",
           "Count every E: Lacey has one, Ellery has two, Pollard has none. Only exactly one counts.",
           "Cross out every pass whose surname has no E at all, or two or more."],
    "22": ["Look only at the first letter of each name.",
           "Initials are the first letters of the first name and the surname. Sally Sutton has the same "
           "initial twice; Maria Pell doesn’t.",
           "Cross out every pass whose first name and surname begin with the same letter."],
    "23": ["Count the letters of the first name and the surname, then add them together.",
           "Odd numbers end in 1, 3, 5, 7 or 9. Mary Pell has 4 + 4 = 8 letters, which is even.",
           "Cross out every pass whose first name and surname together have an even number of letters."],
}
LEVEL_NAMES = ["Level 1 — A gentle nudge", "Level 2 — A stronger push", "Level 3 — Nearly the answer"]
