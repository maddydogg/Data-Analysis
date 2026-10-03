"""Full Moon over Morrowmere — case data: story text, world config, clues, hints.

Everything the generator, the checker and the renderer need lives here, so the
documents, the clue predicates and the hints are all derived from one source.
"""

TITLE = "Full Moon over Morrowmere"
SUBTITLE = "A Halloween Witch Village Murder Puzzle"
BRAND = "QuietClueCo"
TAGLINE = "6,000 visitors · 18 clues · 1 killer"
PLAYERS = "1–4 players"
PLAYTIME = "90–150 minutes"
CASE_NO = "Case No. 3"
SEED = 20261031
N_VISITORS = 6000
DATE = "31 October"

# ---------------------------------------------------------------- the world
TOWNS = ["Morrowmere", "Ashcott Heath", "Birchfold", "Brackenhythe", "Dunwold", "Fernley",
         "Hatherby", "Kittlewick", "Larkspur Green", "Nettlebarrow", "Owlhallow", "Pennyholt",
         "Rushcombe", "Thornby Cross", "Wexley", "Yarrowby"]
# visitor share per village (Morrowmere is the host village)
TOWN_WEIGHTS = [24, 6, 6, 5, 6, 5, 6, 5, 6, 5, 6, 5, 6, 5, 6, 5]

# the log prints the first word of each entrance; the map shows the full names
GATES = ["Bramble", "Mill", "Church", "Orchard"]
GATE_NAMES = {"Bramble": "Bramble Gate", "Mill": "Mill Stile", "Church": "Church Lychgate",
              "Orchard": "Orchard Gap"}
GATE_WEIGHTS = [30, 22, 24, 24]
STONE_GATES = {"Mill", "Orchard"}          # the footpaths to these two run through the Hob Stones (map)

LANES = ["Sage Walk", "Thimble Lane", "Bellflower Row", "Rowan Close"]

# the Book of Brews: brew key -> (name, ingredients)
BREWS = {
    "harvest": ("Harvest Moon Cup", ["apple", "cinnamon", "star anise", "honey"]),
    "rosehip": ("Rosehip Ember", ["rosehip", "star anise", "ginger"]),
    "cocoa": ("Midnight Cocoa", ["cocoa", "chilli", "vanilla"]),
    "hedgerow": ("Hedgerow Cordial", ["elderberry", "blackberry", "rosehip", "honey"]),
    "mint": ("Silver Mint Tisane", ["peppermint", "lemon balm", "honey"]),
    "chai": ("Hearth Chai", ["black tea", "cardamom", "star anise", "rosehip", "clove"]),
    "posset": ("Pumpkin Posset", ["pumpkin", "nutmeg", "cream"]),
    "moonmilk": ("Lavender Moon Milk", ["milk", "lavender", "honey", "vanilla"]),
    "wassail": ("Moon Fair Wassail", ["apple", "rosehip", "star anise", "honey"]),
}
CRAFTS = {
    "gingerbread": "Moon gingerbread", "candle": "Beeswax candles", "lantern": "Paper lanterns",
    "jam": "Bramble jam", "toffee": "Treacle toffee", "honey": "Honeycomb", "charm": "Charm bags",
    "amulet": "Moon amulets", "broom": "Besom brooms", "herbs": "Dried herb bundles",
    "tea": "Loose-leaf tea", "hat": "Felt pointed hats", "crystal": "Polished stones",
    "tarot": "Card readings", "soap": "Herb soap",
}
GOODS = {**{k: v[0] for k, v in BREWS.items()}, **CRAFTS}
# stall number -> (name, goods keys). Lanes: 1-9 Sage Walk, 10-18 Thimble Lane,
# 19-27 Bellflower Row, 28-36 Rowan Close.
STALLS = {
    1: ("The Copper Kettle", ["harvest", "gingerbread"]),
    2: ("Wick & Wax", ["candle", "lantern"]),
    3: ("The Hedge Pantry", ["hedgerow", "jam"]),
    4: ("Ember & Thorn", ["rosehip", "toffee"]),
    5: ("Moonmilk Dairy", ["moonmilk", "honey"]),
    6: ("Charms of the Green", ["charm", "amulet"]),
    7: ("The Spice Cart", ["chai", "gingerbread"]),
    8: ("Besom Corner", ["broom", "herbs"]),
    9: ("The Cauldron Kitchen", ["posset", "cocoa"]),
    10: ("Silver Leaf Teas", ["mint", "tea"]),
    11: ("The Lantern Loft", ["lantern", "candle"]),
    12: ("The Wandering Barrow", ["rosehip", "jam"]),
    13: ("Wassail Wagon", ["wassail", "toffee"]),
    14: ("The Felt Hat Stall", ["hat", "charm"]),
    15: ("Thimble & Spoon", ["cocoa", "gingerbread"]),
    16: ("The Hearthstone", ["chai", "posset"]),
    17: ("Amulets & Acorns", ["amulet", "crystal"]),
    18: ("The Bee Bole", ["honey", "moonmilk"]),
    19: ("Bellflower Brews", ["wassail", "harvest"]),
    20: ("The Card Table", ["tarot", "candle"]),
    21: ("The Ember Pot", ["rosehip", "cocoa"]),
    22: ("Herb & Hearth Soaps", ["soap", "herbs"]),
    23: ("The Treacle Jar", ["toffee", "jam"]),
    24: ("The Painted Wagon", ["chai", "mint"]),
    25: ("Starlight Stones", ["crystal", "amulet"]),
    26: ("The Pumpkin Pot", ["posset", "harvest"]),
    27: ("Owl & Oak", ["broom", "lantern"]),
    28: ("Rowan Remedies", ["herbs", "soap"]),
    29: ("The Midnight Mug", ["cocoa", "moonmilk"]),
    30: ("Bramble & Berry", ["jam", "hedgerow"]),
    31: ("The Brass Kettle", ["rosehip", "honey"]),
    32: ("Moon Wassail", ["wassail", "gingerbread"]),
    33: ("Candlemaker's Corner", ["candle", "tarot"]),
    34: ("The Mint Pot", ["mint", "hedgerow"]),
    35: ("Hearth & Home", ["chai", "toffee"]),
    36: ("The Last Lantern", ["lantern", "harvest"]),
}
def lane_of(stall):
    return LANES[(stall - 1) // 9]

# the carrier's weekly rounds (parcels left at the Apothecary go out on the round named)
ROUNDS = [
    ("Monday", ["Ashcott Heath", "Fernley", "Larkspur Green", "Yarrowby"]),
    ("Tuesday", ["Brackenhythe", "Dunwold", "Nettlebarrow", "Pennyholt", "Thornby Cross"]),
    ("Wednesday", ["Birchfold", "Fernley", "Rushcombe", "Wexley", "Yarrowby"]),
    ("Thursday", ["Birchfold", "Dunwold", "Hatherby", "Kittlewick", "Owlhallow", "Wexley"]),
    ("Friday", ["Ashcott Heath", "Hatherby", "Larkspur Green", "Pennyholt", "Rushcombe"]),
    ("Saturday", ["Brackenhythe", "Kittlewick", "Nettlebarrow", "Owlhallow", "Thornby Cross"]),
]
CARRIER_DAY = "Thursday"
def round_towns(day):
    return [t for d, ts in ROUNDS if d == day for t in ts]

# the moon-watcher's log: (from, to, sky, moon_visible)
MOON_LOG = [
    ("16:00", "17:39", "Moon below the hills", False),
    ("17:40", "17:51", "Moonrise, hidden behind Hob Hill", False),
    ("17:52", "18:20", "Full moon, clear and bright", True),
    ("18:21", "19:04", "Cloud bank, moon hidden", False),
    ("19:05", "20:16", "Full moon, clear and bright", True),
    ("20:17", "21:00", "Thick cloud, light drizzle", False),
]
READING_TIME = "19:40"
DREGS = dict(has=["rosehip", "star anise"], lacks="honey")
OPEN_FROM, LAST_ENTRY = "16:00", "20:29"

def tmin(s):
    h, m = s.split(":"); return int(h) * 60 + int(m)
def tstr(m):
    return f"{m // 60:02d}:{m % 60:02d}"

MOON_WINDOWS = [(tmin(a), tmin(b)) for a, b, _, vis in MOON_LOG if vis]
DREG_BREWS = sorted(k for k, (_, ing) in BREWS.items()
                    if all(i in ing for i in DREGS["has"]) and DREGS["lacks"] not in ing)
DREG_STALLS = sorted(s for s, (_, g) in STALLS.items() if any(b in g for b in DREG_BREWS))
ROUTE_TOWNS = round_towns(CARRIER_DAY)

# ---------------------------------------------------------------- names
# Pools avoid famous fictional witches and the people in the story.
FIRST = """Ada Abel Alba Alma Amos Anna Annie Arthur Augusta Annabel Effie Elsie Ella Etta Edgar
Edmund Eleanor Enid Ezra Elva Eden Ida Ivy Iris Isla Inez Ivo Olive Opal Orla Oscar Otto Oona Osric
Una Uma Ulla Enoch Ebba Emma Ansel Arlo Olga Orson Basil Beatrix Bella Bernard Bertha Blanche Cedric Celia Clara Clement Constance Cora Cyril
Dahlia Delia Dora Dorian Fabian Flora Freda Gideon Grace Greta Gwen Hannah Harriet Hector Helena
Horace Jasper Jonah Josie Jude Kit Lavinia Lena Leonard Linus Lottie Lucian Lydia Mabel Magnus
Maisie Marian Martha Maud Mercy Milo Miriam Morris Myrtle Nell Nina Noel Nora Pearl Percy Philippa
Pip Quentin Rhoda Rosa Ruth Sadie Selma Thea Vera Viola Walter Willa Wilbur""".split()
LAST = """Abbott Ashby Ainsworth Applegarth Arkwright Ashdown Atherton Allsop Aske Ashworth Ackroyd
Ebdon Eckford Edwards Ellwood Elstob Enright Eastham Ewart Eskdale Elmore Ibbott Ingram Ireton
Isherwood Oakley Ockley Oddie Onslow Orme Osgood Otway Oldroyd Ormerod Overton Upton Underwood
Uttley Usworth Edgworth Elgood Elphick Ellingham Ambler Anstey Arkell Ashwell
Ashendon Oxenford Oldfield Openshaw Ulverton Ilsley Inchley Bainbridge Barlow Beck Blythe Bowden Brock Bunting Burnell Chalk Chilton Clegg
Coates Cobbold Dabney Dawes Digby Dunstan Fairley Fawcett Fenwick Finlow Gale Gilbey Godwin
Gosling Hackett Haldane Hamblin Hawley Heskett Hobday Jessop Judd Kaye Keeling Kitson Lamb Larkin
Lowe Lumsden Maddox Meakin Mellish Monk Napier Nettles Newbolt Noakes Nuttall Padley Pellow
Pennick Phelps Pickles Plumb Pocock Quayle Raikes Ramsay Redfern Rook Rudd Sallis Satchell Sefton
Shilton Skelton Slade Stokes Sutton Swales Tasker Thwaite Tolley Twigg Tyson Vance Venables Wakely
Wallis Webley Welch Wilmot Winslow Witton Yates Yelland""".split()
FIRST = sorted(set(FIRST))
LAST = sorted(set(LAST))

# ---------------------------------------------------------------- the killer
KILLER = dict(ticket=4073, first="Edna", last="Elworthy", town="Hatherby",
              gate="Orchard", entry=tmin("19:23"), stall=21)
VICTIM = "Barnaby Quell"
INSPECTOR = "Inspector Hollis Drummond"
WITNESS = "Bryony Fettle"
READER = "Mother Meridew"
SHOPBOY = "Tobias Wick"
WATCHER = "Hazel Thorne"
CARRIER = "Jory Pell"
MARK = "a tall pointed hat with a silver crescent-moon pin"
SHOP = "Quell’s Apothecary"

# ---------------------------------------------------------------- clues
VOWELS = set("AEIOU")
def zeros(n):
    return f"{n:04d}".count("0")
def in_windows(t, excl=False):
    return any((a < t < b) if excl else (a <= t <= b) for a, b in MOON_WINDOWS)

# Each clue: id, text shown to the player, predicate(record), alternative readings
# (plausible misreadings; the answer must survive each of them), documents it needs.
# record = dict(ticket, first, last, town, gate, entry, stall)
CLUES = [
    # ---- notebook clues (stated outright)
    dict(id="1", kind="notebook",
         text="The killer’s first name begins with a vowel (A, E, I, O or U).",
         pred=lambda r: r["first"][0].upper() in VOWELS, alts=[]),
    dict(id="2", kind="notebook",
         text="The killer’s surname is at least two letters longer than their first name.",
         pred=lambda r: len(r["last"]) >= len(r["first"]) + 2,
         alts=[("“at least two” read as “more than two”",
                lambda r: len(r["last"]) >= len(r["first"]) + 3)]),
    dict(id="3", kind="notebook",
         text="The killer’s surname contains the letter E exactly once (capital or small).",
         pred=lambda r: r["last"].upper().count("E") == 1,
         alts=[("“exactly once” read as “at least once”", lambda r: "E" in r["last"].upper())]),
    dict(id="4", kind="notebook",
         text="The killer’s first name has fewer than six letters.",
         pred=lambda r: len(r["first"]) < 6,
         alts=[("six letters itself counted as “fewer than six”", lambda r: len(r["first"]) <= 6)]),
    dict(id="5", kind="notebook",
         text="The killer’s surname does not end in S.",
         pred=lambda r: not r["last"].upper().endswith("S"), alts=[]),
    dict(id="6", kind="notebook",
         text="The killer’s ticket number is odd.",
         pred=lambda r: r["ticket"] % 2 == 1, alts=[]),
    dict(id="7", kind="notebook",
         text="The killer’s ticket number has exactly one 0 among its four digits.",
         pred=lambda r: zeros(r["ticket"]) == 1,
         alts=[("leading zeros ignored (0472 read as 472)", lambda r: str(r["ticket"]).count("0") == 1)]),
    dict(id="8", kind="notebook",
         text="The killer came in at minutes 10 to 39 of an hour.",
         pred=lambda r: 10 <= r["entry"] % 60 <= 39, alts=[]),
    dict(id="9", kind="notebook",
         text="The killer’s home village contains the letter H (capital or small).",
         pred=lambda r: "H" in r["town"].upper(), alts=[]),
    dict(id="10", kind="notebook",
         text="The killer’s last stall has a two-digit number.",
         pred=lambda r: r["stall"] >= 10, alts=[]),
    dict(id="11", kind="notebook",
         text="The killer’s last purchase was not made on Rowan Close.",
         pred=lambda r: lane_of(r["stall"]) != "Rowan Close", alts=[]),
    dict(id="12", kind="notebook",
         text="The killer’s first name does not contain the letter I.",
         pred=lambda r: "I" not in r["first"].upper(), alts=[]),
    # ---- evidence clues (the player has to work them out from the documents)
    dict(id="A", kind="evidence",
         text="Which entrance did the killer come in by?",
         fact="The killer walked through the Hob Stones on the way in. Only the footpaths to "
              "Mill Stile and Orchard Gap pass through the stones, so the entrance was Mill or Orchard.",
         docs=["Bryony’s note", "Fair map"],
         pred=lambda r: r["gate"] in STONE_GATES, alts=[]),
    dict(id="B", kind="evidence",
         text="When could the killer have come in?",
         fact="The full moon was out when the killer came in: entry time 17:52–18:20 or "
              "19:05–20:16 (first and last minutes included).",
         docs=["Bryony’s note", "Moon-watcher’s log"],
         pred=lambda r: in_windows(r["entry"]),
         alts=[("first and last minutes of each clear spell excluded",
                lambda r: in_windows(r["entry"], excl=True))]),
    dict(id="C", kind="evidence",
         text="What does Mother Meridew’s reading book tell you about the time?",
         fact=f"Mother Meridew read the killer’s cup at {READING_TIME}, so the killer came in at "
              f"{READING_TIME} or earlier.",
         docs=["Reading book"],
         pred=lambda r: r["entry"] <= tmin(READING_TIME),
         alts=[(f"strictly before {READING_TIME}", lambda r: r["entry"] < tmin(READING_TIME))]),
    dict(id="D", kind="evidence",
         text="Where did the killer make their last purchase?",
         fact="The dregs held rosehip and star anise but no honey, so the brew was "
              + " or ".join(BREWS[b][0] for b in DREG_BREWS) + ". The killer’s last stall is one "
              "that sells it: " + ", ".join(map(str, DREG_STALLS)) + ".",
         docs=["Reading book", "Book of Brews", "Stall directory"],
         pred=lambda r: r["stall"] in DREG_STALLS, alts=[]),
    dict(id="E", kind="evidence",
         text="Where does the killer live?",
         fact=f"The killer’s parcel went home with the {CARRIER_DAY} carrier, which passes their "
              "door, so their village is on the Thursday round: " + ", ".join(ROUTE_TOWNS) + ".",
         docs=["Shop ledger", "Carrier’s rounds"],
         pred=lambda r: r["town"] in ROUTE_TOWNS, alts=[]),
    dict(id="F", kind="evidence",
         text="What did Tobias notice about how the killer signed the ledger?",
         fact="The killer signed with two initials, the same letter twice, so their first name "
              "and surname begin with the same letter.",
         docs=["Shop ledger"],
         pred=lambda r: r["first"][0].upper() == r["last"][0].upper(), alts=[]),
]
for c in CLUES:
    c.setdefault("docs", [])
    c["label"] = ("Clue " if c["kind"] == "notebook" else "Evidence ") + c["id"]

# order used in the solution walkthrough (big sweeps first)
WALK_ORDER = ["B", "A", "C", "D", "E", "F", "11", "10", "9", "6", "7", "8",
              "1", "2", "3", "4", "5", "12"]

# ---------------------------------------------------------------- story text
INTRO = [
    "Every 31 October the village of Morrowmere holds its Moon Fair on the green. The Hearth "
    "Circle, the village’s old coven of herbalists, candle-makers and tea-leaf readers, hangs a "
    "lantern over every stall, the cauldrons of spiced brew bubble until late, and anyone who "
    "owns a pointed hat wears it.",
    f"This year the full moon rose right on cue. At 20:45 {SHOPBOY}, the shop boy at "
    f"{SHOP} on the edge of the green, found his master, {VICTIM}, slumped in the back room. "
    "Quell owned the shop and chaired the fair committee. His cup of brew had been laced with "
    "something from the locked cabinet that was certainly not on the menu.",
    "Every visitor wore a numbered moon token on a ribbon. It was scanned once at the entrance "
    "on the way in and used to pay at every stall. The fair committee has handed over the "
    "complete Visitor Log: 6,000 tokens, one line each.",
    f"{INSPECTOR} needs your help. The killer is one of those 6,000 lines. "
    "Cross out every visitor who doesn’t fit the evidence until only one remains.",
]
KNOWN_FACTS = [
    "The Visitor Log lists every visitor exactly once. No two visitors share a full name, "
    "and ticket numbers run from 0001 to 6000 with no gaps.",
    "Entry is the time the token was scanned at the entrance. Entrance is where it was scanned: "
    "Bramble Gate, Mill Stile, Church Lychgate or Orchard Gap. The log prints the first word only "
    "(Bramble, Mill, Church, Orchard).",
    "Last stall is the stall where the token made its final purchase of the night. "
    "Every visitor bought at least one thing.",
    f"{READER} reads the tea leaves of anyone who brings her a cup from the fair. The token "
    "records confirm that the cup the killer brought her was the killer’s last purchase of the night.",
    f"{WITNESS}, who lights the lanterns in the meadow, saw a visitor in {MARK}. Hundreds of "
    "people wore pointed hats that night, but only one wore that pin, and everyone who noticed it "
    "was looking at the killer.",
]
GLOSSARY = [
    ("Letters", "Count letters only. Every name in the log is a single word with no spaces, "
                "hyphens or apostrophes. Home villages may be one word or two."),
    ("Vowels", "A, E, I, O and U. In this case Y is never a vowel."),
    ("Longer", "“At least two letters longer” means the surname has two or more letters more than "
               "the first name: Ruth (4) and Barlow (6) count; Ruth and Gale (4 and 4) do not."),
    ("Capital or small", "A letter counts whether it is a capital or not: Ellwood contains the "
                         "letter E once, Elmore twice."),
    ("Times", f"All times are 24-hour clock on {DATE}. “19:40 or earlier” includes 19:40 itself. "
              "A range such as 17:52–18:20 includes both the first and the last minute."),
    ("Minutes", "The minutes of 18:07 are 07. “Minutes 10 to 39” includes :10 and :39."),
    ("Ticket digits", "Read all four digits as printed, zeros included: ticket 0472 has one 0, "
                      "ticket 3006 has two, ticket 1234 has none. An odd number ends in 1, 3, 5, 7 or 9."),
    ("Stalls", "Stall numbers, names, lanes and what each stall sells are on the fair map and in "
               "the stall directory. What goes into each brew is in the Book of Brews."),
]
HOW_TO_PLAY = [
    ("What you need", "A highlighter or pencil, this case file printed (or open in Goodnotes "
                      "or Notability), and a cup of something warm."),
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
NOTE = [
    "Inspector —",
    "I saw the lady with the silver moon pin",
    "on her tall hat. She came over the meadow",
    "and straight through the Hob Stones, and",
    "the full moon was out so bright her pin",
    "flashed like a new coin as she came in.",
    "Later, about twenty past eight, she",
    "slipped out of Mr Quell’s back door.",
    "— Bryony (lantern girl)",
]
# Mother Meridew's reading book: (time, sitter, the cup, the leaves showed)
READINGS = [
    ("19:10", "Two sisters in green shawls", "Silver Mint Tisane, honeyed. The leaves clumped.",
     "A ladder and a bell"),
    ("19:25", "The miller’s lad", "Harvest Moon Cup. Honey again, clumped.", "A horseshoe, a cloud"),
    (READING_TIME, "A lady in a tall hat with a silver crescent pin",
     "Rosehip skins and broken star anise. No honey: the leaves lay loose.",
     "A key. A closed door. A bird flying home."),
    ("19:55", "A gentleman with a fiddle case", "Midnight Cocoa. No leaves worth the name.", "Nothing to read"),
    ("20:10", "A young couple in matching scarves", "Hedgerow Cordial, honeyed.", "Two rings and a road"),
]
LEDGER = [
    ("16:20", "Dried sage, three bundles", "£4.50"),
    ("17:05", "Lavender soap", "£2.00"),
    ("18:40", "Elderflower syrup, one bottle", "£6.00"),
    ("20:05", "PARCEL TO SEND: one bundle in brown paper and string, for the lady in the tall hat "
              "with the silver crescent pin. To go home with the carrier on Thursday: “he goes "
              "right past my door,” she said. Carrier’s fee paid in coins.", "£1.50"),
]
LEDGER_NOTE = ["She signed with her initials only:", "the same curly letter, twice.",
               "I couldn’t make out which letter.", "— T.W."]

EPILOGUE = [
    "The lady in the tall hat was Edna Elworthy, a bookbinder from Hatherby, ticket 4073.",
    "For three generations the Elworthy women kept the herb shop on the edge of Morrowmere "
    "green. Edna’s grandmother, Ottilie, wrote every remedy she ever made into a fat green "
    "notebook, and the whole Hearth Circle came to her for advice. When Edna’s mother grew ill "
    "and fell behind with the rent, Barnaby Quell bought the building, gave the family a month "
    "to leave, and opened his own shop under their old painted sign.",
    "He kept the green notebook too. It had been left in a drawer during the move, and when Edna "
    "asked for it back, Quell said it came with the shop. For years his best-selling remedies "
    "were Ottilie’s, copied out word for word.",
    "On Moon Fair night Edna came across the meadow and through the Hob Stones at 19:23, under a "
    "bright full moon, and in at Orchard Gap. She bought a cup of Rosehip Ember at The Ember Pot, "
    "stall 21, and at 19:40 she sat down with Mother Meridew, who read a key, a closed door and "
    "a bird flying home in her cup.",
    "At five past eight she walked into the shop and asked Tobias to send a parcel home with "
    "Thursday’s carrier. While he went to find string, she slipped into the back room, where "
    "Quell’s own cup stood cooling beside the green notebook. She left by the back door at "
    "twenty past eight. Bryony saw her go.",
    "The parcel reached Hatherby on Thursday morning. Inside, wrapped in brown paper, was "
    "Ottilie’s green notebook. Edna had signed for it the way her grandmother signed every page: "
    "E.E., in curly letters.",
    "Inspector Drummond kept a copy of the ledger page. The Hearth Circle has since painted over "
    "Quell’s sign, and at the next Moon Fair they lit one extra lantern for the Elworthy women.",
]
