"""Three-level hints for every clue. Facts inside the hints are computed from case.py,
so a hint can never disagree with the documents; verify.py re-checks them anyway."""
import case as C

WIN = " and ".join(f"{C.tstr(a)}–{C.tstr(b)}" for a, b in C.SNOW_WINDOWS)
PUNCH = ", ".join(map(str, C.PUNCH_STALLS))
ROUTE = ", ".join(C.ROUTE_TOWNS)
ONE_WORD_ROUTE = ", ".join(t for t in C.ROUTE_TOWNS if " " not in t)
HOLLY = f"stalls 1–9"
FB = " and ".join(f"the {g} Gate" for g in sorted(C.FOOTBRIDGE_GATES))

HINTS = {
    "1": ["Count only the letters of the first name. Five letters is odd; six is even.",
          "Short names are quick wins: Ida (3), Enid (4), Clara (5), Martha (6).",
          "Cross out every visitor whose first name has 2, 4, 6 or 8 letters."],
    "2": ["Compare the two names of the same visitor, letter by letter count.",
          "If the two names are the same length, the surname is NOT longer, so that visitor is out.",
          "Keep a visitor only if their surname has at least one more letter than their first name."],
    "3": ["Look only at the first letter of each name.",
          "If both names start with the same letter, the surname does not come later, so that visitor is out.",
          "Keep a visitor only if the surname’s first letter is further along A to Z than the "
          "first name’s first letter (Ada Webb: W comes after A, so Ada stays)."],
    "4": ["Only the surname matters here, and Y never counts as a vowel.",
          "Count every vowel, even repeats: Bennett has E and E, which makes two.",
          "Keep a visitor only if their surname has exactly 2 of A, E, I, O, U. "
          "One vowel is out, three or more is out."],
    "5": ["Look at the last letter of the first name.",
          "Names ending in Y (Molly, Percy) end with a consonant in this case, so they stay.",
          "Cross out every visitor whose first name ends in A, E, I, O or U."],
    "6": ["This one uses the ticket number column.",
          "2500 itself would still count.",
          "Cross out every visitor with ticket 0001 to 2499."],
    "7": ["Add the four digits of the ticket number together.",
          "Ticket 0472 gives 0+4+7+2 = 13, which is odd, so 0472 would stay.",
          "Cross out every visitor whose ticket digits add up to an even number."],
    "8": ["Look at the last two digits of the entry time.",
          "18:07 has minutes 07 (odd). 18:40 has minutes 40 (even).",
          "Cross out every visitor whose entry time ends in 0, 2, 4, 6 or 8."],
    "9": ["Some home towns in the log are two words.",
          "The two-word towns are " + ", ".join(t for t in C.TOWNS if " " in t) + ".",
          "Cross out every visitor from " + ", ".join(t for t in C.TOWNS if " " in t) + "."],
    "10": ["Use the Last stall column.",
           "Even means 2, 4, 6, 8 and so on.",
           "Cross out every visitor whose last stall number is odd."],
    "11": ["The market map and the stall directory show which stalls are on Holly Lane.",
           "Holly Lane is the row of " + HOLLY + ".",
           "Cross out every visitor whose last stall is 1, 2, 3, 4, 5, 6, 7, 8 or 9."],
    "12": ["Only the surname matters.",
           "Upper or lower case doesn’t matter: Oakes and Brook both contain an O.",
           "Cross out every visitor whose surname contains the letter O."],
    "A": ["Read Pip’s note again: what did the visitor cross on the way in?",
          "Find the footbridges on the market map. How many gates can you reach by footbridge?",
          f"The footbridges lead to {FB}. Cross out every visitor who came in through the North "
          "Gate or the West Gate."],
    "B": ["Pip says something about the weather at the moment the visitor came in.",
          "The weather log shows it snowed twice that evening.",
          f"It snowed {WIN}. Cross out every visitor whose entry time is outside both of those "
          "windows. Because the log is sorted by entry time, you can cross out whole pages."],
    "C": ["The receipt has a time on it. What does that tell you about when the killer arrived?",
          "Nobody can buy punch at a stall before they have come through the gate.",
          f"The receipt says {C.RECEIPT_TIME}. Cross out every visitor who came in at "
          f"{C.tstr(C.tmin(C.RECEIPT_TIME) + 1)} or later."],
    "D": ["The receipt shows what was bought, but the stall’s name is torn off.",
          "The receipt was the killer’s last purchase, so their Last stall must sell that item. "
          "Check the stall directory.",
          f"Only stalls {PUNCH} sell spiced apple punch. Cross out every visitor whose last "
          "stall is any other number."],
    "E": ["Read the coach driver’s statement: which coach did the visitor in the red hat take?",
          "They got off at their own town’s stop, somewhere along that coach’s route. "
          "Find the route in the coach timetable.",
          f"The 21:15 is Route 4: {ROUTE}. Cross out every visitor from any other town."],
    "F": ["Read the gate steward’s statement: what did she notice about the surname?",
          "A double letter means the same letter twice, side by side, like LL in Bell or TT in Abbott.",
          "Cross out every visitor whose surname has no double letter. Letters that repeat "
          "but are not side by side (like the two Rs in Garner) don’t count."],
}
LEVEL_NAMES = ["Level 1 — A gentle nudge", "Level 2 — A stronger push",
               "Level 3 — Nearly the answer"]
