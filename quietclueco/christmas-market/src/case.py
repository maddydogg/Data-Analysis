"""Snowfall at Ember Square — case data: story text, world config, clues, hints.

Everything the generator, the checker and the renderer need lives here, so the
documents, the clue predicates and the hints are all derived from one source.
"""

TITLE = "Snowfall at Ember Square"
SUBTITLE = "A Christmas Market Murder Puzzle"
BRAND = "QuietClueCo"
TAGLINE = "6,000 visitors · 18 clues · 1 killer"
PLAYERS = "1–4 players"
PLAYTIME = "90–150 minutes"
SEED = 20261223
N_VISITORS = 6000

# ---------------------------------------------------------------- the world
TOWNS = ["Emberfield", "Ashcombe", "Brambleford", "Copperwell", "Dunmoor",
         "Elderbrook", "Foxhollow", "Greyhaven", "Hartwell", "Juniper Cross",
         "Kestrel Bay", "Marrowby", "Nettlefold", "Oakhurst", "Pennywick",
         "Sloe Green"]
# visitor share per town (Emberfield is the host town)
TOWN_WEIGHTS = [26, 6, 6, 5, 6, 5, 5, 6, 5, 5, 5, 5, 5, 5, 5, 6]

GATES = ["North", "East", "South", "West"]
GATE_WEIGHTS = [30, 22, 22, 26]
GATE_SIDE = {  # what each gate opens onto (drawn on the map)
    "North": "Castle Road", "West": "Mill Lane",
    "East": "footbridge over the River Ember", "South": "footbridge over the River Ember"}
FOOTBRIDGE_GATES = {"East", "South"}

LANES = ["Holly Lane", "Gingerbread Walk", "Candle Row", "Evergreen Court"]
GOODS = {
    "punch": "Spiced apple punch", "cocoa": "Hot chocolate", "chestnut": "Roasted chestnuts",
    "almond": "Candied almonds", "ginger": "Gingerbread", "stars": "Cinnamon stars",
    "candle": "Beeswax candles", "toys": "Wooden toys", "orn": "Glass ornaments",
    "knit": "Knitted scarves", "cheese": "Farmhouse cheese", "sausage": "Grilled sausages",
    "pretzel": "Pretzels", "fudge": "Fudge", "soap": "Handmade soap", "wreath": "Wreaths",
    "cider": "Hot cider", "honey": "Honey", "stollen": "Stollen", "prints": "Art prints",
}
# stall number -> (name, lane, goods keys). Lanes: 1-9 Holly, 10-18 Gingerbread,
# 19-27 Candle Row, 28-36 Evergreen Court.
STALLS = {
    1: ("The Holly Bough", ["wreath", "candle"]),
    2: ("Frost & Fern", ["punch", "cocoa"]),
    3: ("Chestnut Corner", ["chestnut", "almond"]),
    4: ("The Tin Soldier", ["toys", "orn"]),
    5: ("Mistletoe Mugs", ["punch", "cider"]),
    6: ("Woolly Things", ["knit"]),
    7: ("Bramble Bakehouse", ["ginger", "stollen"]),
    8: ("The Honey Pot", ["honey", "candle"]),
    9: ("Starlight Glass", ["orn", "prints"]),
    10: ("Gingerbread Guild", ["ginger", "stars"]),
    11: ("The Warm Cup", ["punch", "cocoa"]),
    12: ("Pretzel Palace", ["pretzel", "sausage"]),
    13: ("Nutcracker Sweets", ["almond", "fudge"]),
    14: ("Copper Kettle Cider", ["cider", "cocoa"]),
    15: ("The Soap Barrow", ["soap", "candle"]),
    16: ("Cheese & Chutney", ["cheese", "honey"]),
    17: ("Fireside Chestnuts", ["chestnut", "cocoa"]),
    18: ("Paper Snow Prints", ["prints", "orn"]),
    19: ("Wick & Ember", ["candle", "soap"]),
    20: ("The Sleigh Bell", ["punch", "stars"]),
    21: ("Toymaker's Bench", ["toys"]),
    22: ("The Merry Kettle", ["punch", "cider"]),
    23: ("Sugarplum Fudge", ["fudge", "almond"]),
    24: ("Northern Knits", ["knit", "prints"]),
    25: ("Robin's Rest", ["punch", "stollen"]),
    26: ("Smokehouse Grill", ["sausage", "pretzel"]),
    27: ("The Bauble Box", ["orn", "wreath"]),
    28: ("Evergreen Wreaths", ["wreath", "honey"]),
    29: ("Cocoa Cabin", ["cocoa", "fudge"]),
    30: ("Stollen & Stars", ["stollen", "stars"]),
    31: ("Winter Warmers", ["punch", "cocoa"]),
    32: ("The Carved Owl", ["toys", "candle"]),
    33: ("Almond Blossom", ["almond", "ginger"]),
    34: ("Pine & Punch", ["cider", "chestnut"]),
    35: ("Lace & Linen", ["knit", "soap"]),
    36: ("The Last Lantern", ["cocoa", "stars"]),
}
def lane_of(stall):
    return LANES[(stall - 1) // 9]

COACHES = [  # departs, route, calls at (all from the Market Stop)
    ("20:15", "Route 1", ["Brambleford", "Copperwell", "Greyhaven"]),
    ("20:45", "Route 2", ["Elderbrook", "Foxhollow", "Nettlefold", "Pennywick"]),
    ("21:15", "Route 4", ["Ashcombe", "Dunmoor", "Hartwell", "Juniper Cross",
                          "Kestrel Bay", "Marrowby", "Oakhurst"]),
    ("21:40", "Route 6", ["Foxhollow", "Sloe Green", "Pennywick", "Hartwell"]),
    ("22:10", "Route 1", ["Brambleford", "Copperwell", "Greyhaven"]),
]
def coach_towns(dep):
    return [t for d, _, ts in COACHES if d == dep for t in ts]

# weather log: (from, to, condition, is_snow)
WEATHER = [
    ("16:00", "17:04", "Dry, low cloud", False),
    ("17:05", "17:30", "Light snow", True),
    ("17:31", "18:39", "Dry, cold", False),
    ("18:40", "19:55", "Steady snow", True),
    ("19:56", "21:00", "Dry, clearing", False),
]
TEMPS = [("16:00", "2°C"), ("17:00", "1°C"), ("18:00", "0°C"),
         ("19:00", "-1°C"), ("20:00", "-2°C"), ("21:00", "-3°C")]
RECEIPT_TIME = "19:48"
RECEIPT_ITEM = "punch"
COACH_TIME = "21:15"
OPEN_FROM, LAST_ENTRY = "16:00", "20:29"

def tmin(s):
    h, m = s.split(":"); return int(h) * 60 + int(m)
def tstr(m):
    return f"{m // 60:02d}:{m % 60:02d}"

SNOW_WINDOWS = [(tmin(a), tmin(b)) for a, b, _, snow in WEATHER if snow]
PUNCH_STALLS = sorted(s for s, (_, g) in STALLS.items() if RECEIPT_ITEM in g)
ROUTE_TOWNS = coach_towns(COACH_TIME)

# ---------------------------------------------------------------- names
FIRST = """Abigail Ada Agnes Albert Alfred Alice Amos Annie Archie Arthur Beatrix Bella
Bernard Bertie Bridget Cecil Celia Clara Clement Cora Cyril Daisy Dora Dorothy Edgar Edie
Edith Edmund Effie Elsie Enid Ernest Esther Ethel Evelyn Fenella Florence Frances Freda
Gilbert Greta Gwen Harold Harriet Hazel Henry Hilda Hugo Ida Imogen Iris Isla Ivor Jasper
Joan Josie Jude Kit Lena Leonard Lionel Lottie Lydia Mabel Maisie Margot Martha Maud
Mavis Milo Minnie Monty Muriel Myrtle Ned Nell Nora Olive Oscar Otto Percy Phoebe Pip
Poppy Quentin Ralph Ray Rhoda Rosa Rupert Ruth Sadie Silas Stanley Stella Sybil Teddy
Thea Tobias Una Vera Violet Wilfred Winnie Xavier Zelda Barnaby Ottilie Rowena Ivy Molly
Dolly Sidney Timothy Lily Emily Harvey Audrey Stanley""".split()
LAST = """Abbott Ainsley Barrow Bell Bennett Birch Blackwood Bramwell Brook Burrows Carver
Chandler Clay Cobb Copper Crane Cutler Darrow Dell Denny Drake Dunn Ellery Elwood Farrell
Fell Finch Garnett Gibbs Glass Goodall Grange Gull Hadley Hale Harker Hartley Hazell
Hendry Hill Hobbs Hollins Hurst Innes Jarrett Jewell Keel Kemp Kettle Kidd Lark Lennard
Linnell Mallet Marsh Mercer Merritt Miller Minns Moss Nash Neville Nuttall Oakes Parrish
Pennell Perrin Pike Pinnock Platt Pollard Pryce Quill Rainer Reeve Russell Sallow Scott
Selby Sheppard Skerritt Sparrow Starling Tanner Teller Thackery Thatcher Tidwell Tinsley
Trask Tuck Tully Varley Vesey Wadding Walker Warrender Webb Wells Wheeler Whitt Winnard
Wren Yardley Yeoman Mayhew Kennett Terrell Pettit Barrett Dennett Fennell Tennyson
Ferrand Carrell Harrell Jenner Kerrigan Sellers Tebbutt Venning Wrenn Brett Lynn Penny
Sykes Gray Hayward Lytton Tyler Pym""".split()
FIRST = sorted(set(FIRST))
LAST = sorted(set(LAST))

# ---------------------------------------------------------------- the killer
KILLER = dict(ticket=3857, first="Hazel", last="Russell", town="Marrowby",
              gate="South", entry=tmin("19:23"), stall=22)
VICTIM = "Ambrose Thorne"
INSPECTOR = "Detective Inspector Wren Ashdown"

# ---------------------------------------------------------------- clues
VOWELS = set("AEIOU")
def vowels(s, y=False):
    v = VOWELS | ({"Y"} if y else set())
    return sum(c in v for c in s.upper())
def has_double(s):
    s = s.lower(); return any(a == b for a, b in zip(s, s[1:]))
def has_repeat(s):
    s = s.lower(); return len(set(s)) < len(s)
def digit_sum(n):
    return sum(int(c) for c in str(n))
def in_windows(t, excl=False):
    return any((a < t < b) if excl else (a <= t <= b) for a, b in SNOW_WINDOWS)

R = "RECEIPT"
# Each clue: id, text shown to the player, predicate(record), alternative readings
# (plausible misreadings; the answer must survive each of them), documents it needs.
# record = dict(ticket, first, last, town, gate, entry, stall)
CLUES = [
    # ---- notebook clues (stated outright)
    dict(id="1", kind="notebook",
         text="The killer’s first name has an odd number of letters.",
         pred=lambda r: len(r["first"]) % 2 == 1, alts=[]),
    dict(id="2", kind="notebook",
         text="The killer’s surname has more letters than their first name.",
         pred=lambda r: len(r["last"]) > len(r["first"]),
         alts=[("“more” read as “at least as many”",
                lambda r: len(r["last"]) >= len(r["first"]))]),
    dict(id="3", kind="notebook",
         text="The first letter of the killer’s surname comes later in the alphabet "
              "than the first letter of their first name.",
         pred=lambda r: r["last"][0] > r["first"][0],
         alts=[("“later” read as “the same or later”",
                lambda r: r["last"][0] >= r["first"][0])]),
    dict(id="4", kind="notebook",
         text="The killer’s surname contains exactly two vowels. (Vowels are A, E, I, O "
              "and U. Y is never a vowel in this case.) Count every vowel, repeats included.",
         pred=lambda r: vowels(r["last"]) == 2,
         alts=[("Y counted as a vowel", lambda r: vowels(r["last"], True) == 2),
               ("repeated vowels counted once",
                lambda r: len({c for c in r["last"].upper() if c in VOWELS}) == 2)]),
    dict(id="5", kind="notebook",
         text="The killer’s first name ends with a consonant. (Y counts as a consonant.)",
         pred=lambda r: r["first"][-1].upper() not in VOWELS,
         alts=[("Y counted as a vowel", lambda r: r["first"][-1].upper() not in VOWELS | {"Y"})]),
    dict(id="6", kind="notebook",
         text="The killer’s ticket number is 2500 or higher.",
         pred=lambda r: r["ticket"] >= 2500,
         alts=[("“or higher” missed (strictly above 2500)", lambda r: r["ticket"] > 2500)]),
    dict(id="7", kind="notebook",
         text="The digits of the killer’s ticket number add up to an odd number.",
         pred=lambda r: digit_sum(r["ticket"]) % 2 == 1,
         alts=[]),
    dict(id="8", kind="notebook",
         text="The minutes in the killer’s entry time are an odd number "
              "(for example 18:07 or 18:31).",
         pred=lambda r: (r["entry"] % 60) % 2 == 1, alts=[]),
    dict(id="9", kind="notebook",
         text="The killer’s home town is a single word.",
         pred=lambda r: " " not in r["town"], alts=[]),
    dict(id="10", kind="notebook",
         text="The killer made their last purchase at an even-numbered stall.",
         pred=lambda r: r["stall"] % 2 == 0, alts=[]),
    dict(id="11", kind="notebook",
         text="The killer’s last purchase was not made on Holly Lane.",
         pred=lambda r: lane_of(r["stall"]) != "Holly Lane", alts=[]),
    dict(id="12", kind="notebook",
         text="The killer’s surname does not contain the letter O.",
         pred=lambda r: "o" not in r["last"].lower(), alts=[]),
    # ---- evidence clues (the player has to work them out from the documents)
    dict(id="A", kind="evidence",
         text="Which gate did the killer come in through?",
         fact="The killer came in through a gate that is reached by a footbridge: "
              "the East Gate or the South Gate.",
         docs=["Pip’s note", "Market map"],
         pred=lambda r: r["gate"] in FOOTBRIDGE_GATES,
         alts=[("only the footbridge gate nearest the carousel", lambda r: r["gate"] == "South")]),
    dict(id="B", kind="evidence",
         text="When could the killer have come in?",
         fact="It was snowing when the killer came in: entry time 17:05–17:30 or "
              "18:40–19:55 (first and last minutes included).",
         docs=["Pip’s note", "Weather log"],
         pred=lambda r: in_windows(r["entry"]),
         alts=[("first and last minutes of each snowfall excluded",
                lambda r: in_windows(r["entry"], excl=True))]),
    dict(id="C", kind="evidence",
         text="What does the time on the receipt tell you?",
         fact="The killer bought the punch at 19:48, so they came in at 19:48 or earlier.",
         docs=["Receipt"],
         pred=lambda r: r["entry"] <= tmin(RECEIPT_TIME),
         alts=[("strictly before 19:48", lambda r: r["entry"] < tmin(RECEIPT_TIME))]),
    dict(id="D", kind="evidence",
         text="Where did the killer make their last purchase?",
         fact="The killer’s last purchase was spiced apple punch, so their stall is one "
              "that sells it: " + ", ".join(map(str, PUNCH_STALLS)) + ".",
         docs=["Receipt", "Stall directory"],
         pred=lambda r: r["stall"] in PUNCH_STALLS, alts=[]),
    dict(id="E", kind="evidence",
         text="Where does the killer live?",
         fact="The killer rode the 21:15 coach home, so their home town is on Route 4: "
              + ", ".join(ROUTE_TOWNS) + ".",
         docs=["Coach driver’s statement", "Coach timetable"],
         pred=lambda r: r["town"] in ROUTE_TOWNS, alts=[]),
    dict(id="F", kind="evidence",
         text="What was unusual about the killer’s surname?",
         fact="The killer’s surname contains a double letter (the same letter twice in a "
              "row, like the SS in Moss).",
         docs=["Steward’s statement"],
         pred=lambda r: has_double(r["last"]),
         alts=[("any letter used twice, not necessarily side by side",
                lambda r: has_repeat(r["last"]))]),
]
for c in CLUES:
    c.setdefault("docs", [])
    c["label"] = ("Clue " if c["kind"] == "notebook" else "Evidence ") + c["id"]

# order used in the solution walkthrough (big sweeps first)
WALK_ORDER = ["B", "A", "C", "D", "E", "F", "9", "11", "10", "6", "7", "8",
              "1", "2", "3", "4", "5", "12"]

# ---------------------------------------------------------------- story text
INTRO = [
    "On the last night of the Ember Square Christmas Market, the snow came and went, the "
    "carousel turned, and six thousand visitors wandered between the stalls with mugs of "
    "punch warming their hands.",
    f"At 20:40 the market steward lifted the flap of the Judges’ Tent and found "
    f"{VICTIM}, head judge of the Great Gingerbread Contest for eleven years running, slumped "
    "over the judging table. His mug of mulled wine had been laced with something that was "
    "definitely not cinnamon.",
    "Tickets for the final night sold out weeks ago. Every visitor wore a numbered wristband "
    "that was scanned once at the gate on the way in and used to pay at every stall. "
    "The ticket office has handed over the complete Visitor Log: 6,000 wristbands, "
    "one line each.",
    f"{INSPECTOR} needs your help. The killer is one of those 6,000 lines. "
    "Cross out every visitor who doesn’t fit the evidence until only one remains.",
]
KNOWN_FACTS = [
    "The Visitor Log lists every visitor exactly once. No two visitors share a full name, "
    "and ticket numbers run from 0001 to 6000 with no gaps.",
    "Entry is the time the wristband was scanned at the gate. Gate is the gate it was scanned at.",
    "Last stall is the stall where the wristband made its final purchase of the night. "
    "Every visitor bought at least one thing.",
    "A crumpled receipt was found under the judging table. Forensics are certain the killer "
    "dropped it, and the till records confirm it was the killer’s last purchase of the night.",
    "Pip Calloway, who runs the carousel, saw a visitor in a red bobble hat slip out of the "
    "Judges’ Tent at about 20:05. Everyone who saw the red bobble hat that night was "
    "looking at the killer.",
]
GLOSSARY = [
    ("Letters", "Count letters only. Every name in the log is a single word with no spaces, "
                "hyphens or apostrophes. Home towns may be one word or two."),
    ("Vowels", "A, E, I, O and U. In this case Y is always a consonant."),
    ("Double letter", "The same letter twice in a row, like the LL in Bell. Letters that "
                      "repeat but are not side by side (like the two Rs in Garner) do not count."),
    ("Times", "All times are 24-hour clock on 23 December. “19:48 or earlier” includes "
              "19:48 itself. A time range such as 17:05–17:30 includes both the first and the "
              "last minute."),
    ("Minutes", "The minutes of 18:07 are 07, which is odd. The minutes of 19:40 are 40, which is even."),
    ("Ticket digits", "Add the four digits as printed: ticket 0472 gives 0+4+7+2 = 13."),
    ("Stalls", "Stall numbers, names, lanes and what each stall sells are on the market map and "
               "in the stall directory."),
]
HOW_TO_PLAY = [
    ("What you need", "A highlighter or pencil, this case file printed (or open in Goodnotes "
                      "or Notability), and a mug of something warm."),
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
    "I saw the one in the red bobble hat twice.",
    "First when they came in: they hurried over",
    "the footbridge and straight through the gate,",
    "and it was snowing right then — flakes all",
    "over that hat. Second time, about 5 past 8,",
    "slipping out of the Judges' Tent.",
    "Hope that helps.  — Pip (carousel)",
]
STEWARD = ("Marged Pryce, gate steward",
           ["At about 20:20 a visitor in a red bobble hat came to the lost-property desk "
            "asking whether anyone had handed in a green knitted mitten. Nobody had.",
            "I started a lost-property form. They didn’t give me a first name, but they "
            "spelled their surname out for me letter by letter. I remember writing it "
            "carefully because it had a double letter in it — the same letter twice, "
            "side by side.",
            "They didn’t wait for me to finish the form. They were off towards the "
            "Market Stop before I looked up."])
DRIVER = ("Owen Tully, coach driver, Ember Valley Coaches",
          ["I drove the 21:15 from the Market Stop. A passenger in a red bobble hat got on "
           "at the last moment, out of breath.",
           "They said they were going home and asked to be let off at their own town’s "
           "stop. They got off along my route, I’m sure of that, but I couldn’t tell "
           "you which stop — the coach was packed and I was watching the ice on the road."])

EPILOGUE = [
    "The visitor in the red bobble hat was Hazel Russell, a baker from Marrowby, ticket 3857.",
    "Hazel’s grandmother, Winifred, had baked the same gingerbread every Christmas for sixty "
    "years: dark treacle, a pinch of black pepper and a crust of sugar that cracked like new "
    "snow. When Winifred died, her handwritten recipe card went missing from the kitchen drawer.",
    "Three years later, Ambrose Thorne began winning the Great Gingerbread Contest with a "
    "“secret family recipe”. Dark treacle. Black pepper. A sugar crust that cracked like "
    "new snow. Hazel entered the contest three times. Three times, Ambrose marked her down for "
    "“lack of originality”.",
    "On the last night of the market she came over the South Gate footbridge at 19:23 with snow "
    "settling on her red bobble hat. At 19:48 she bought a cup of spiced apple punch at The "
    "Merry Kettle, stall 22, so that she would have a reason to be carrying a steaming mug. "
    "When the judges broke for the evening, she slipped into the tent and swapped her mug for "
    "his. Pip saw her come out at five past eight.",
    "She did not notice the receipt fall from her pocket. She did notice, twenty minutes later, "
    "that one of her green mittens was gone, and she went to the lost-property desk to ask for "
    "it, spelling out R-U-S-S-E-L-L before she thought better of it. At 21:15 she caught the "
    "Route 4 coach home to Marrowby.",
    "The mitten turned up the next morning, under the judging table. Tucked inside it was a "
    "faded recipe card in Winifred’s handwriting, the one Ambrose had kept for eleven years, "
    "and which Hazel had taken back from his coat pocket.",
    "Inspector Ashdown still thinks about that recipe card. Hazel, for what it’s worth, "
    "has told the court that the gingerbread was always better with a little more pepper.",
]
