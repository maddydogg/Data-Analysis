"""Three-level hints for every clue. Facts inside the hints are computed from case.py,
so a hint can never disagree with the documents; verify.py re-checks them anyway."""
import case as C

WIN = " and ".join(f"{C.tstr(a)}–{C.tstr(b)}" for a, b in C.MOON_WINDOWS)
DREG_NAMES = " and ".join(C.BREWS[b][0] for b in C.DREG_BREWS)
DREG_STALLS = ", ".join(map(str, C.DREG_STALLS[:-1])) + " and " + str(C.DREG_STALLS[-1])
ROUTE = ", ".join(C.ROUTE_TOWNS[:-1]) + " and " + C.ROUTE_TOWNS[-1]
H_TOWNS = [t for t in C.TOWNS if "H" in t.upper()]
NO_H_TOWNS = [t for t in C.TOWNS if "H" not in t.upper()]
STONES = " and ".join(C.GATE_NAMES[g] for g in C.GATES if g in C.STONE_GATES)
NOT_STONES = " or ".join(g for g in C.GATES if g not in C.STONE_GATES)

HINTS = {
    "1": ["Look only at the first letter of the first name.",
          "A, E, I, O and U are vowels; Y never counts. Ada and Oscar stay; Bella and Yvonne would go.",
          "Cross out every visitor whose first name begins with any letter other than A, E, I, O or U."],
    "2": ["Count the letters in both names and compare the two counts.",
          "Ruth (4) and Barlow (6): exactly two letters longer, which counts, so Ruth Barlow would stay. "
          "Ruth Gale (4 and 4) would go.",
          "Cross out every visitor whose surname is shorter than the first name, the same length, "
          "or only one letter longer."],
    "3": ["Look for the letter E in the surname, capital or small.",
          "Count every E: Ellwood has one, Elmore has two, Abbott has none. Only exactly one counts.",
          "Cross out every visitor whose surname has no E at all, or has two or more."],
    "4": ["Count the letters of the first name.",
          "Fewer than six means five letters or fewer. Oscar (5) stays; Arthur (6) would go.",
          "Cross out every visitor whose first name has 6 or more letters."],
    "5": ["Only the last letter of the surname matters.",
          "Edwards ends in S, so it would go. Abbott ends in T, so it would stay.",
          "Cross out every visitor whose surname ends in S."],
    "6": ["This one uses the ticket number column.",
          "Odd numbers end in 1, 3, 5, 7 or 9. Ticket 0472 is even.",
          "Cross out every visitor whose ticket number ends in 0, 2, 4, 6 or 8."],
    "7": ["Count the zeros in the ticket number.",
          "Read all four printed digits: 0472 has one zero, 3006 has two, 1234 has none.",
          "Cross out every visitor whose ticket has no 0 at all, or has two or more zeros."],
    "8": ["Look at the last two digits of the entry time.",
          "18:10 and 18:39 count. 18:09 and 18:40 do not.",
          "Cross out every visitor whose entry minutes are 00 to 09 or 40 to 59."],
    "9": ["Look for the letter H anywhere in the home village, capital or small.",
          "The villages with an H in them are " + ", ".join(H_TOWNS) + ".",
          "Cross out every visitor from " + ", ".join(NO_H_TOWNS) + "."],
    "10": ["Use the Last stall column.",
           "Two-digit stall numbers run from 10 to 36.",
           "Cross out every visitor whose last stall is 1, 2, 3, 4, 5, 6, 7, 8 or 9."],
    "11": ["The fair map and the stall directory show which stalls are on Rowan Close.",
           "Rowan Close is the lane of stalls 28–36.",
           "Cross out every visitor whose last stall is 28, 29, 30, 31, 32, 33, 34, 35 or 36."],
    "12": ["Only the first name matters.",
           "Capital or small makes no difference: Ida and Elsie both contain an I.",
           "Cross out every visitor whose first name contains the letter I."],
    "A": ["Read Bryony’s note again: what did the visitor walk through on the way in? Then follow that "
          "path on the fair map. A path can fork, so check every entrance it leads to, not just one.",
          "Find the Hob Stones on the fair map. Which footpaths run through them?",
          f"Only the paths to {STONES} run through the Hob Stones. Cross out every visitor who "
          f"came in by {NOT_STONES}."],
    "B": ["Bryony says something about the sky at the moment the visitor came in.",
          "The moon-watcher’s log shows when the full moon could be seen and when cloud hid it. "
          "There were two clear spells.",
          f"The full moon was out {WIN}. Cross out every visitor whose entry time is outside both "
          "spells. The log is sorted by entry time, so whole pages can go at once."],
    "C": ["Mother Meridew’s book gives the time of the reading, not the time the lady came in. "
          "What does the reading time tell you about when she must have arrived?",
          "Nobody can sit for a reading at the fair before they have come in.",
          f"The reading was at {C.READING_TIME}. Cross out every visitor who came in at "
          f"{C.tstr(C.tmin(C.READING_TIME) + 1)} or later."],
    "D": ["Mother Meridew wrote down what was left in the cup. Which brews could leave those dregs?",
          "Check the Book of Brews: the brew must contain rosehip and star anise, and no honey. "
          "Then find the stalls that sell it in the stall directory.",
          f"Only {DREG_NAMES} fit. They are sold at stalls {DREG_STALLS}. Cross out every visitor "
          "whose last stall is any other number."],
    "E": ["Read the shop ledger: how was the parcel going home?",
          "The carrier goes right past her door on that day’s round. Find the round in the "
          "carrier’s timetable.",
          f"The {C.CARRIER_DAY} round calls at {ROUTE}. Cross out every visitor from any other village."],
    "F": ["Read Tobias’s note beside the ledger: how did she sign?",
          "Initials are the first letters of the first name and the surname.",
          "Cross out every visitor whose first name and surname begin with different letters."],
}
LEVEL_NAMES = ["Level 1 — A gentle nudge", "Level 2 — A stronger push",
               "Level 3 — Nearly the answer"]
