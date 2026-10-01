"""Storm over Corvenmoor — case data: story text, world config, clues, hints.

Everything the generator, the checker and the renderer need lives here, so the
documents, the clue predicates and the hints are all derived from one source.
"""

TITLE = "Storm over Corvenmoor"
SUBTITLE = "A Halloween Monster Murder Puzzle"
BRAND = "QuietClueCo"
TAGLINE = "6,000 visitors · 18 clues · 1 killer"
PLAYERS = "1–4 players"
PLAYTIME = "90–150 minutes"
CASE_NO = "Case No. 2"
SEED = 20261031
N_VISITORS = 6000
DATE = "31 October"

# ---------------------------------------------------------------- the world
TOWNS = ["Corvenmoor", "Ashwick Fen", "Barrowdene", "Duskwater", "Eelmarsh", "Fernhollow",
         "Gloamford", "Hagstone", "Kettlewick", "Mothwell", "Owlsgate", "Pikesmere",
         "Ravensholt", "Thistle Green", "Underfell", "Wychcombe"]
# visitor share per town (Corvenmoor is the host village)
TOWN_WEIGHTS = [24, 5, 5, 6, 5, 5, 5, 6, 5, 5, 6, 5, 6, 5, 6, 7]

GATES = ["North", "East", "South", "West"]
GATE_WEIGHTS = [30, 22, 24, 24]
GARGOYLE_GATES = {"North", "West"}       # stone gargoyles carved above these two gates (drawn on the map)
LAB_GATE = "West"                         # the Laboratory Tower stands right beside this gate

LANES = ["Bat Alley", "Cauldron Court", "Lantern Walk", "Raven Row"]
GOODS = {
    "potion": "Bubbling potion punch", "soup": "Pumpkin soup", "toffee": "Toffee apples",
    "cider": "Hot spiced cider", "floss": "Candy floss", "soul": "Soul cakes",
    "bat": "Bat biscuits", "corn": "Caramel popcorn", "cocoa": "Hot chocolate",
    "pie": "Pumpkin pie", "spider": "Liquorice spiders", "mask": "Monster masks",
    "paint": "Face painting", "wand": "Glow wands", "lantern": "Paper lanterns",
    "hat": "Witch hats", "cat": "Black cat plushies", "candle": "Spooky candles",
    "fudge": "Graveyard fudge", "book": "Old storybooks",
}
# booth number -> (name, goods keys). Lanes: 1-9 Bat Alley, 10-18 Cauldron Court,
# 19-27 Lantern Walk, 28-36 Raven Row.
STALLS = {
    1: ("The Belfry", ["bat", "cocoa"]),
    2: ("Hocus Pocus Masks", ["mask", "paint"]),
    3: ("Toffee & Twist", ["toffee", "floss"]),
    4: ("The Moth Lamp", ["lantern", "candle"]),
    5: ("The Bubbling Flask", ["potion", "cider"]),
    6: ("Soul Cake Kitchen", ["soul", "pie"]),
    7: ("Nine Lives", ["cat", "hat"]),
    8: ("Dr Corven's Tonics", ["potion", "spider"]),
    9: ("Crypt Corn", ["corn", "fudge"]),
    10: ("The Great Cauldron", ["soup", "cocoa"]),
    11: ("Wand & Wick", ["wand", "candle"]),
    12: ("Spider Sweets", ["spider", "floss"]),
    13: ("The Pumpkin Pantry", ["pie", "soup"]),
    14: ("Moonlit Cider", ["cider", "toffee"]),
    15: ("The Laboratory Bar", ["potion", "cocoa"]),
    16: ("Paint the Night", ["paint", "mask"]),
    17: ("The Haunted Hat", ["hat", "cat"]),
    18: ("Fudge from the Grave", ["fudge", "soul"]),
    19: ("Lantern Lane Books", ["book", "lantern"]),
    20: ("Green Fizz", ["potion", "floss"]),
    21: ("The Glow Barrow", ["wand", "lantern"]),
    22: ("Old Bones Bakery", ["bat", "pie"]),
    23: ("Cider in the Shadows", ["cider", "corn"]),
    24: ("The Mad Scientist", ["potion", "toffee"]),
    25: ("Whisker & Broom", ["cat", "hat"]),
    26: ("Candle Crypt", ["candle", "book"]),
    27: ("The Hollow Gourd", ["soup", "soul"]),
    28: ("Raven's Rest", ["cocoa", "fudge"]),
    29: ("Mask & Mirror", ["mask", "wand"]),
    30: ("The Spider's Web", ["spider", "corn"]),
    31: ("Stitch & Bolt", ["paint", "mask"]),
    32: ("Black Cat Bakery", ["bat", "soul"]),
    33: ("The Lightning Jar", ["potion", "pie"]),
    34: ("Toffee Tombstones", ["toffee", "fudge"]),
    35: ("Lantern & Quill", ["book", "candle"]),
    36: ("The Last Cauldron", ["cider", "soup"]),
}
def lane_of(stall):
    return LANES[(stall - 1) // 9]

COACHES = [  # departs, route, calls at (all from the Castle Stop)
    ("20:30", "N1", ["Barrowdene", "Hagstone", "Owlsgate"]),
    ("21:00", "N2", ["Eelmarsh", "Fernhollow", "Kettlewick", "Thistle Green"]),
    ("21:20", "N3", ["Ashwick Fen", "Duskwater", "Gloamford", "Mothwell",
                     "Pikesmere", "Ravensholt", "Underfell"]),
    ("21:45", "N4", ["Wychcombe", "Kettlewick", "Hagstone", "Barrowdene"]),
    ("22:15", "N1", ["Barrowdene", "Hagstone", "Owlsgate"]),
]
def coach_towns(dep):
    return [t for d, _, ts in COACHES if d == dep for t in ts]

# weather log: (from, to, condition, is_thunderstorm)
WEATHER = [
    ("16:00", "17:19", "Overcast, still", False),
    ("17:20", "17:45", "Thunderstorm", True),
    ("17:46", "18:54", "Light drizzle", False),
    ("18:55", "20:10", "Thunderstorm, heavy", True),
    ("20:11", "21:00", "Clearing, damp", False),
]
TEMPS = [("16:00", "11°C"), ("17:00", "10°C"), ("18:00", "9°C"),
         ("19:00", "8°C"), ("20:00", "8°C"), ("21:00", "7°C")]
RECEIPT_TIME = "19:52"
RECEIPT_ITEM = "potion"
COACH_TIME = "21:20"
OPEN_FROM, LAST_ENTRY = "16:00", "20:29"

def tmin(s):
    h, m = s.split(":"); return int(h) * 60 + int(m)
def tstr(m):
    return f"{m // 60:02d}:{m % 60:02d}"

SNOW_WINDOWS = [(tmin(a), tmin(b)) for a, b, _, storm in WEATHER if storm]   # thunderstorm windows
PUNCH_STALLS = sorted(s for s, (_, g) in STALLS.items() if RECEIPT_ITEM in g)
ROUTE_TOWNS = coach_towns(COACH_TIME)

# ---------------------------------------------------------------- names
FIRST = """Ada Agnes Albert Alma Amos Anna Annie Arthur Augusta Barnaby Basil Beatrix Bella
Bernard Bertha Blanche Cedric Celia Clara Clement Constance Cora Cyril Dahlia Delia Dora
Dorian Edgar Edith Edmund Effie Elias Elsie Enid Esme Ezra Fabian Flora Freda Gideon Grace
Greta Gwen Hannah Harriet Hector Helena Hilda Horace Ida Imogen Iris Isaac Isabel Ivo Ivy
Jasper Jonah Josie Jude Kit Lavinia Lena Leonard Linus Lottie Lucian Lydia Mabel Magnus
Maisie Marian Martha Maud Mercy Milo Miriam Morris Myrtle Nancy Nell Nina Noel Nora Olive
Oscar Otto Pearl Percy Philippa Phoebe Pip Quentin Rhoda Rosa Rowan Ruth Sadie Selma Silas
Sybil Tabitha Thea Tobias Ursula Vera Viola Walter Willa Winnie Wilbur Xavier Zelda""".split()
LAST = """Abbott Ashby Bainbridge Barlow Beck Blythe Bowden Bramble Brock Bunting Burnell
Chalk Chilton Clegg Coates Cobbold Coyle Dabney Dawes Digby Dunstan Eccles Elwin Fairley
Fawcett Fenwick Finlow Gale Gilbey Godwin Gosling Hackett Haldane Hamblin Hawley Heskett
Hobday Hollis Hunnam Ibbott Jessop Judd Kaye Keeling Kitson Lamb Larkin Lowe Lumsden
Mabbott Maddox Meakin Mellish Monk Mosley Nancekivell Napier Nettles Newbolt Noakes
Nuttall Ockley Oddie Onslow Orme Osgood Padley Pellow Pennick Pettit Phelps Pickles Plumb
Pocock Quayle Quick Raikes Ramsay Redfern Rook Rudd Sallis Satchell Sefton Shilton
Skelton Slade Stokes Sutton Swales Tasker Tebbit Thwaite Tolley Toms Tuckey Twigg Tyson
Upton Vance Venables Wakely Wallis Webley Wedgwood Welch Wilmot Winslow Witton
Wolstenholme Yates Yelland Youll""".split()
FIRST = sorted(set(FIRST))
LAST = sorted(set(LAST))

# ---------------------------------------------------------------- the killer
KILLER = dict(ticket=2719, first="Isabel", last="Pettit", town="Gloamford",
              gate="West", entry=tmin("19:17"), stall=33)
VICTIM = "Lucan Marsh"
INSPECTOR = "Detective Inspector Morwenna Tate"
WITNESS = "Juniper Vale"
MASK = "a stitched green monster mask with copper coils above the ears"

# ---------------------------------------------------------------- clues
VOWELS = set("AEIOU")
def digit_sum(n):
    return sum(int(c) for c in str(n))
def first_digit(n):
    return int(f"{n:04d}"[0])
def last_digit(n):
    return n % 10
def in_windows(t, excl=False):
    return any((a < t < b) if excl else (a <= t <= b) for a, b in SNOW_WINDOWS)

# Each clue: id, text shown to the player, predicate(record), alternative readings
# (plausible misreadings; the answer must survive each of them), documents it needs.
# record = dict(ticket, first, last, town, gate, entry, stall)
CLUES = [
    # ---- notebook clues (stated outright)
    dict(id="1", kind="notebook",
         text="The killer’s first name has an even number of letters.",
         pred=lambda r: len(r["first"]) % 2 == 0, alts=[]),
    dict(id="2", kind="notebook",
         text="The killer’s first name and surname begin with different letters.",
         pred=lambda r: r["first"][0] != r["last"][0], alts=[]),
    dict(id="3", kind="notebook",
         text="The killer’s surname begins with a letter from N to Z.",
         pred=lambda r: r["last"][0] >= "N",
         alts=[("N itself left out (only O to Z)", lambda r: r["last"][0] >= "O")]),
    dict(id="4", kind="notebook",
         text="The killer’s first name contains the letter A (capital or small).",
         pred=lambda r: "a" in r["first"].lower(), alts=[]),
    dict(id="5", kind="notebook",
         text="The killer’s surname ends with a consonant. (Y counts as a consonant.)",
         pred=lambda r: r["last"][-1].upper() not in VOWELS,
         alts=[("Y counted as a vowel", lambda r: r["last"][-1].upper() not in VOWELS | {"Y"})]),
    dict(id="6", kind="notebook",
         text="The killer’s ticket number is below 4000.",
         pred=lambda r: r["ticket"] < 4000,
         alts=[("4000 itself counted as “below”", lambda r: r["ticket"] <= 4000)]),
    dict(id="7", kind="notebook",
         text="The last digit of the killer’s ticket number is bigger than the first digit.",
         pred=lambda r: last_digit(r["ticket"]) > first_digit(r["ticket"]),
         alts=[("“bigger” read as “the same or bigger”",
                lambda r: last_digit(r["ticket"]) >= first_digit(r["ticket"]))]),
    dict(id="8", kind="notebook",
         text="The killer came in during the first half of an hour (minutes 00 to 29).",
         pred=lambda r: (r["entry"] % 60) <= 29, alts=[]),
    dict(id="9", kind="notebook",
         text="The killer’s home town begins with a letter from A to M.",
         pred=lambda r: r["town"][0] <= "M", alts=[]),
    dict(id="10", kind="notebook",
         text="The killer’s last booth number is a multiple of 3.",
         pred=lambda r: r["stall"] % 3 == 0, alts=[]),
    dict(id="11", kind="notebook",
         text="The killer’s last purchase was not made on Lantern Walk.",
         pred=lambda r: lane_of(r["stall"]) != "Lantern Walk", alts=[]),
    dict(id="12", kind="notebook",
         text="The killer’s surname does not contain the letter R.",
         pred=lambda r: "r" not in r["last"].lower(), alts=[]),
    # ---- evidence clues (the player has to work them out from the documents)
    dict(id="A", kind="evidence",
         text="Which gate did the killer come in through?",
         fact="The killer came in under the stone gargoyles: the North Gate or the West Gate.",
         docs=["Juniper’s note", "Castle map"],
         pred=lambda r: r["gate"] in GARGOYLE_GATES,
         alts=[("only the gargoyle gate beside the Laboratory Tower", lambda r: r["gate"] == LAB_GATE)]),
    dict(id="B", kind="evidence",
         text="When could the killer have come in?",
         fact="There was a thunderstorm when the killer came in: entry time 17:20–17:45 or "
              "18:55–20:10 (first and last minutes included).",
         docs=["Juniper’s note", "Weather log"],
         pred=lambda r: in_windows(r["entry"]),
         alts=[("first and last minutes of each storm excluded",
                lambda r: in_windows(r["entry"], excl=True))]),
    dict(id="C", kind="evidence",
         text="What does the time on the receipt tell you?",
         fact=f"The killer bought the potion punch at {RECEIPT_TIME}, so they came in at "
              f"{RECEIPT_TIME} or earlier.",
         docs=["Receipt"],
         pred=lambda r: r["entry"] <= tmin(RECEIPT_TIME),
         alts=[(f"strictly before {RECEIPT_TIME}", lambda r: r["entry"] < tmin(RECEIPT_TIME))]),
    dict(id="D", kind="evidence",
         text="Where did the killer make their last purchase?",
         fact="The killer’s last purchase was bubbling potion punch, so their booth is one "
              "that sells it: " + ", ".join(map(str, PUNCH_STALLS)) + ".",
         docs=["Receipt", "Booth directory"],
         pred=lambda r: r["stall"] in PUNCH_STALLS, alts=[]),
    dict(id="E", kind="evidence",
         text="Where does the killer live?",
         fact=f"The killer rode the {COACH_TIME} night bus home, so their home town is on "
              "Route N3: " + ", ".join(ROUTE_TOWNS) + ".",
         docs=["Bus driver’s statement", "Night bus timetable"],
         pred=lambda r: r["town"] in ROUTE_TOWNS, alts=[]),
    dict(id="F", kind="evidence",
         text="What did the cloakroom attendant notice about the killer’s surname?",
         fact="The killer’s surname has exactly six letters: it filled the six boxes on the "
              "cloakroom ticket, one letter per box.",
         docs=["Cloakroom attendant’s statement"],
         pred=lambda r: len(r["last"]) == 6, alts=[]),
]
for c in CLUES:
    c.setdefault("docs", [])
    c["label"] = ("Clue " if c["kind"] == "notebook" else "Evidence ") + c["id"]

# order used in the solution walkthrough (big sweeps first)
WALK_ORDER = ["B", "A", "C", "D", "E", "F", "11", "10", "9", "6", "7", "8",
              "1", "2", "3", "4", "5", "12"]

# ---------------------------------------------------------------- story text
INTRO = [
    "Every 31 October the village of Corvenmoor throws open the gates of its old castle for "
    "Monster Night. Two hundred years ago, the story goes, Baron Aldous Corven tried to wake a "
    "stitched-together creature with a bolt of lightning in his Laboratory Tower. The village "
    "has dressed up as that creature ever since.",
    f"This year the storm came right on cue. At 20:50 the night watchman climbed the Laboratory "
    f"Tower and found {VICTIM}, curator of the castle museum and host of the famous Lightning "
    "Show, slumped over the Baron’s workbench. His goblet of bubbling potion punch had been "
    "laced with something that was definitely not on the menu.",
    "Every visitor wore a numbered wristband that was scanned once at the gate on the way in "
    "and used to pay at every booth. The castle ticket office has handed over the complete "
    "Visitor Log: 6,000 wristbands, one line each.",
    f"{INSPECTOR} needs your help. The killer is one of those 6,000 lines. "
    "Cross out every visitor who doesn’t fit the evidence until only one remains.",
]
KNOWN_FACTS = [
    "The Visitor Log lists every visitor exactly once. No two visitors share a full name, "
    "and ticket numbers run from 0001 to 6000 with no gaps.",
    "Entry is the time the wristband was scanned at the gate. Gate is the gate it was scanned at.",
    "Last booth is the booth where the wristband made its final purchase of the night. "
    "Every visitor bought at least one thing.",
    "A crumpled receipt was found on the floor of the Laboratory Tower. Forensics are certain "
    "the killer dropped it, and the till records confirm it was the killer’s last purchase of the night.",
    f"{WITNESS}, who runs the ghost-lantern parade, saw a visitor in {MASK} slip out of the "
    "Laboratory Tower at about 20:10. Hundreds of people wore monster masks that night, but only "
    "one wore that mask, and everyone who noticed it was looking at the killer.",
]
GLOSSARY = [
    ("Letters", "Count letters only. Every name in the log is a single word with no spaces, "
                "hyphens or apostrophes. Home towns may be one word or two."),
    ("Consonants", "Any letter that is not A, E, I, O or U. In this case Y is always a consonant."),
    ("From … to …", "A letter range includes both ends: “from N to Z” includes N and Z, "
                    "“from A to M” includes A and M."),
    ("Times", f"All times are 24-hour clock on {DATE}. “19:52 or earlier” includes 19:52 itself. "
              "A time range such as 17:20–17:45 includes both the first and the last minute."),
    ("Minutes", "The minutes of 18:07 are 07. The first half of an hour means minutes 00 to 29; "
                "18:29 is in the first half, 18:30 is not."),
    ("Ticket digits", "Read the four digits as printed, zeros included: ticket 0472 has first "
                      "digit 0 and last digit 2."),
    ("Booths", "Booth numbers, names, lanes and what each booth sells are on the castle map and "
               "in the booth directory."),
]
HOW_TO_PLAY = [
    ("What you need", "A highlighter or pencil, this case file printed (or open in Goodnotes "
                      "or Notability), and a bowl of something sweet."),
    ("Who plays", "One detective on their own, or up to four working together. Split the "
                  "Visitor Log between you and compare notes."),
    ("How long", "Around 90 to 150 minutes, depending on how you split the work."),
    ("How it works", "Read the case and the six documents. Clues 1–12 in the "
                     "Inspector’s Notebook are stated outright. Evidence A–F is hidden in "
                     "the documents: work out what each one tells you. Every clue and every piece "
                     "of evidence rules visitors out. Apply them to the Visitor Log in any order "
                     "until one visitor is left."),
    ("A tip", "The Visitor Log is sorted by entry time and split into hourly chapters. "
              "Some evidence lets you cross out whole pages at once."),
    ("Stuck?", "The hint pages at the back give three levels of help for every clue: a nudge, "
               "a stronger push and nearly the answer. Each level sits on its own pages, so "
               "you only see what you ask for."),
    ("Checking your answer", "Use the Sealed Check page. It tells you if you are right "
                             "without giving the answer away. Then open the Envelope "
                             "(the separate solution file) for the full story."),
]
PIP_NOTE = [
    "Inspector —",
    "I saw the one in the stitched monster",
    "mask twice. First coming in: straight in",
    "under the stone gargoyles, and the",
    "lightning flashed just as they came",
    "through. Lit those copper coils right up.",
    "Second time, about 10 past 8, slipping",
    "out of the Laboratory Tower.",
    "— Juniper (lantern parade)",
]
STEWARD = ("Hester Quill, cloakroom attendant",
           ["At about 20:25 a visitor in a stitched green monster mask came to the cloakroom "
            "to collect a coat. They had lost the paper ticket, so I asked for a name to "
            "check against my book.",
            "They didn’t give me a first name. I wrote the surname on a spare cloakroom ticket, "
            "the kind with six little boxes for the letters, and it filled the six boxes "
            "exactly: one letter in each box, not one box left empty.",
            "Before I could find the coat they said not to worry and hurried off towards the "
            "Castle Stop."])
DRIVER = ("Bartholomew Finch, driver, Corvenmoor Night Buses",
          [f"I drove the {COACH_TIME} from the Castle Stop. A passenger in a green monster mask "
           "got on at the last moment, soaked through from the storm.",
           "They said they were going home and asked to be let off at their own village’s "
           "stop. They got off along my route, I’m certain of that, but I couldn’t tell "
           "you which stop. Half the bus was dressed as monsters and the windows were "
           "fogged up."])

EPILOGUE = [
    "The visitor in the stitched monster mask was Isabel Pettit, a clockmaker from Gloamford, "
    "ticket 2719.",
    "Isabel’s grandmother, Rosalind, built clockwork toys in a cramped workshop above the "
    "Gloamford post office. In 1962 she made her finest piece: a tin creature, stitched and "
    "riveted, that sat up, opened its eyes and raised one arm whenever a light flashed. She "
    "signed it the way she signed everything, with a little brass plate inside the chest.",
    "Forty years later the creature appeared in a glass case at Corvenmoor Castle, labelled "
    "“Baron Corven’s original automaton, 1818”. Lucan Marsh had bought it at a house clearance, "
    "pried out the brass plate and built his whole Lightning Show around it. Isabel wrote to "
    "him three times. Three times he wrote back that her family story was “charming, but "
    "unsupported”.",
    "On Monster Night she came in under the gargoyles of the West Gate at 19:17, with the storm "
    "flashing over the towers. At 19:52 she bought a goblet of bubbling potion punch at The "
    "Lightning Jar, booth 33, so that nobody would look twice at someone carrying a smoking "
    "goblet up the tower stairs. During the interval before the Lightning Show she swapped "
    "her goblet for his. Juniper saw her come out at ten past eight.",
    "She did not notice the receipt fall from her pocket. She did notice, a few minutes later, "
    "that she had no coat, and she went to the cloakroom for it, spelling out P-E-T-T-I-T before "
    f"she thought better of it. At {COACH_TIME} she caught the N3 night bus home to Gloamford.",
    "The next morning the watchman found the tin creature’s chest open. The brass plate was "
    "back in its place, polished bright: R. PETTIT, GLOAMFORD, 1962. Isabel had brought it "
    "with her, kept safe for years, waiting for the night she could put it back.",
    "Inspector Tate still has a photograph of that plate. The museum has since changed the "
    "label on the glass case, and the Lightning Show now ends with a minute of quiet for a "
    "clockmaker nobody had heard of.",
]
