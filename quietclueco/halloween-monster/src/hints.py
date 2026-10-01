"""Three-level hints for every clue. Facts inside the hints are computed from case.py,
so a hint can never disagree with the documents; verify.py re-checks them anyway."""
import case as C

WIN = " and ".join(f"{C.tstr(a)}–{C.tstr(b)}" for a, b in C.SNOW_WINDOWS)
POTION = ", ".join(map(str, C.PUNCH_STALLS))
ROUTE = ", ".join(C.ROUTE_TOWNS)
LANTERN = "booths 19–27"
GG = " and ".join(f"the {g} Gate" for g in sorted(C.GARGOYLE_GATES))
NOT_GG = " or ".join(f"the {g} Gate" for g in C.GATES if g not in C.GARGOYLE_GATES)
LATE_TOWNS = ", ".join(t for t in C.TOWNS if t[0] > "M")

HINTS = {
    "1": ["Count only the letters of the first name. Four letters is even; five is odd.",
          "Quick checks: Ida (3), Nora (4), Clara (5), Martha (6).",
          "Cross out every visitor whose first name has 3, 5, 7 or 9 letters."],
    "2": ["Look only at the first letter of each name.",
          "Bella Beck starts both names with B, so she would be out. Bella Monk would stay.",
          "Cross out every visitor whose first name and surname start with the same letter."],
    "3": ["Only the first letter of the surname matters.",
          "N counts: a surname starting with N, like Napier, stays in.",
          "Cross out every visitor whose surname starts with any letter from A to M."],
    "4": ["Look for the letter A anywhere in the first name, at the start or in the middle.",
          "Capital or small makes no difference: Ada, Clara and Nancy all contain an A.",
          "Cross out every visitor whose first name has no letter A in it."],
    "5": ["Look at the last letter of the surname.",
          "Surnames ending in Y, like Fairley, end with a consonant in this case, so they stay.",
          "Cross out every visitor whose surname ends in A, E, I, O or U."],
    "6": ["This one uses the ticket number column.",
          "Ticket 4000 itself is not below 4000.",
          "Cross out every visitor with ticket 4000 to 6000."],
    "7": ["Compare two digits of the ticket number: the very first and the very last.",
          "Read the number with its zeros: ticket 0472 starts with 0 and ends with 2, and 2 is "
          "bigger than 0, so 0472 would stay. If the two digits are equal, the last one is not bigger.",
          "Cross out every visitor whose ticket’s last digit is smaller than or equal to its first digit."],
    "8": ["Look at the last two digits of the entry time.",
          "18:29 is in the first half of the hour. 18:30 is not.",
          "Cross out every visitor whose entry minutes are 30 or more (anything from :30 to :59)."],
    "9": ["Only the first letter of the home town matters.",
          "The towns that start with a letter after M are " + LATE_TOWNS + ".",
          "Cross out every visitor from " + LATE_TOWNS + "."],
    "10": ["Use the Last booth column.",
           "Multiples of 3 are 3, 6, 9, 12, 15 and so on, up to 36.",
           "Keep a visitor only if their last booth is 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33 or 36."],
    "11": ["The castle map and the booth directory show which booths are on Lantern Walk.",
           "Lantern Walk is the row of " + LANTERN + ".",
           "Cross out every visitor whose last booth is 19, 20, 21, 22, 23, 24, 25, 26 or 27."],
    "12": ["Only the surname matters.",
           "Upper or lower case doesn’t matter: Rook and Barlow both contain an R.",
           "Cross out every visitor whose surname contains the letter R."],
    "A": ["Read Juniper’s note again: what was above the gate the visitor came through?",
          "Find the gargoyles on the castle map. How many gates have them?",
          f"Gargoyles sit above {GG}. Cross out every visitor who came in through {NOT_GG}."],
    "B": ["Juniper says something about the weather at the moment the visitor came in.",
          "Lightning means a thunderstorm. The weather log shows there were two that evening.",
          f"The storms were {WIN}. Cross out every visitor whose entry time is outside both of "
          "those windows. Because the log is sorted by entry time, you can cross out whole pages."],
    "C": ["The receipt has a time on it. What does that tell you about when the killer arrived?",
          "Nobody can buy anything at a booth before they have come through the gate.",
          f"The receipt says {C.RECEIPT_TIME}. Cross out every visitor who came in at "
          f"{C.tstr(C.tmin(C.RECEIPT_TIME) + 1)} or later."],
    "D": ["The receipt shows what was bought, but the booth’s name is torn off.",
          "The receipt was the killer’s last purchase, so their Last booth must sell that item. "
          "Check the booth directory.",
          f"Only booths {POTION} sell bubbling potion punch. Cross out every visitor whose last "
          "booth is any other number."],
    "E": ["Read the bus driver’s statement: which bus did the visitor in the monster mask take?",
          "They got off at their own village’s stop, somewhere along that bus’s route. "
          "Find the route in the night bus timetable.",
          f"The {C.COACH_TIME} is Route N3: {ROUTE}. Cross out every visitor from any other town."],
    "F": ["Read the cloakroom attendant’s statement: what did the surname fit into?",
          "One letter per box, six boxes, no box left empty.",
          "Cross out every visitor whose surname does not have exactly 6 letters."],
}
LEVEL_NAMES = ["Level 1 — A gentle nudge", "Level 2 — A stronger push",
               "Level 3 — Nearly the answer"]
