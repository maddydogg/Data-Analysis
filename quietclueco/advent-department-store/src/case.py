"""The Windows at Quillon's — case data for the advent calendar.

Everything the generator, the checker and the renderer need lives here: the store, the
city, the 21 daily clues (windows 3-23) with their alternative readings, and the story.
"""

TITLE = "The Windows at Quillon’s"
TITLE_PLAIN = "The Windows at Quillon's"
SUBTITLE = "A Christmas Eve Murder Mystery Advent Calendar"
BRAND = "QuietClueCo"
TAGLINE = "24 windows · 2,400 shoppers · 1 killer"
PLAYERS = "1–4 players"
PLAYTIME = "10–25 minutes a day"
CASE_NO = "Advent Calendar"
SEED = 20261224
N_PASSES = 2400
DATE = "Christmas Eve"
STORE = "Quillon & Daughters"
STORE_SHORT = "Quillon’s"
CITY = "Vellmouth"

# ---------------------------------------------------------------- the store
# Department = till number = the window that shows it. Levels from the bottom up.
LEVELS = [
    ("LG", "Lower Ground", "floor"),
    ("G", "Ground Floor", "floor"),
    ("HL", "Half Landing", "half"),        # between the Ground and First floors
    ("1", "First Floor", "floor"),
    ("2", "Second Floor", "floor"),
    ("CG", "Clock Gallery", "half"),       # between the Second and Third floors
    ("3", "Third Floor", "floor"),
    ("R", "Roof Terrace", "roof"),
]
LEVEL_ORDER = [k for k, _, _ in LEVELS]
LEVEL_NAME = {k: n for k, n, _ in LEVELS}
LEVEL_KIND = {k: t for k, _, t in LEVELS}
DEPTS = {
    1: ("Food Hall", "LG", ["fresh bread", "cheese", "drinking chocolate (tins of powder)", "fruit"]),
    2: ("Hampers & Wine", "LG", ["Christmas hampers", "wine", "port"]),
    3: ("The Sweet Shop", "LG", ["sugared almonds", "toffee", "cocoa tins", "candy canes"]),
    4: ("Perfumery", "G", ["perfume", "soap", "bath salts"]),
    5: ("Gloves & Scarves", "G", ["gloves", "scarves", "muffs"]),
    6: ("Watches & Jewellery", "G", ["watches", "necklaces", "brooches"]),
    7: ("Stationery & Cards", "G", ["Christmas cards", "pens", "diaries"]),
    8: ("Gift Wrapping", "HL", ["wrapping paper", "ribbon", "gift tags"]),
    9: ("The Lantern Bar", "HL", ["hot cocoa", "coffee", "mince pies"]),
    10: ("Ladies’ Fashion", "1", ["coats", "dresses", "evening wear"]),
    11: ("Menswear", "1", ["suits", "ties", "overcoats"]),
    12: ("Shoes", "1", ["boots", "shoes", "slippers"]),
    13: ("Hats & Umbrellas", "1", ["hats", "umbrellas", "walking sticks"]),
    14: ("Toy Hall", "2", ["dolls", "train sets", "rocking horses"]),
    15: ("Books", "2", ["novels", "atlases", "diaries"]),
    16: ("Games & Puzzles", "2", ["jigsaws", "board games", "playing cards"]),
    17: ("Music Boxes", "2", ["music boxes", "records", "snow globes"]),
    18: ("Clocks", "CG", ["clocks", "barometers", "watch straps"]),
    19: ("Silverware", "CG", ["cutlery", "candlesticks", "photo frames"]),
    20: ("The Quillon Tea Room", "3", ["hot cocoa", "tea", "scones"]),
    21: ("Home & Linen", "3", ["blankets", "towels", "cushions"]),
    22: ("Christmas Decorations", "3", ["baubles", "tinsel", "hot cocoa and cider (cart)"]),
    23: ("Haberdashery", "3", ["thread", "buttons", "lace"]),
    24: ("Roof Terrace", "R", ["roast chestnuts", "hot cocoa", "toffee apples"]),
}
def dept_name(n):
    return DEPTS[n][0]
def dept_level(n):
    return DEPTS[n][1]
TOY_HALL = 14
CUP_DEPTS = [9, 20, 22, 24]        # serve hot drinks to take away in striped paper cups (store guide)
COCOA_ANY = [1, 3, 9, 20, 22, 24]  # anything with cocoa or chocolate in it, cups or not (trap reading)

def above_toy_hall(n, halves=True, roof=True):
    lv = LEVEL_ORDER.index(dept_level(n))
    if lv <= LEVEL_ORDER.index("2"):
        return False
    if not halves and LEVEL_KIND[dept_level(n)] == "half":
        return False
    if not roof and LEVEL_KIND[dept_level(n)] == "roof":
        return False
    return True

# doors (the register prints the first word)
DOORS = ["Arcade", "Clock", "Tram", "Garden"]
DOOR_NAMES = {"Arcade": "Arcade Door", "Clock": "Clock Door", "Tram": "Tram Door", "Garden": "Garden Door"}
DOOR_WEIGHTS = [32, 26, 22, 20]
DOOR_STREET = {"Arcade": "Lantern Street", "Clock": "Market Square", "Tram": "Tramway Yard",
               "Garden": "inside the Winter Garden glasshouse (its gate opens on Tramway Yard)"}
TRAM_SIDE = {"Tram", "Garden"}            # from the tram shelter: straight across the yard, or through the Winter Garden
TRAM_SIDE_WIDE = {"Tram", "Garden", "Clock"}   # misreading: the Clock Door at the corner of the yard counts too

# ---------------------------------------------------------------- the city
# 4 x 4 grid, row 0 is the north bank, the River Vell runs between rows 0 and 1.
GRID = [
    ["Tanners’ Reach", "Saltmarket", "Cathedral Close", "Bellfounders"],
    ["Lamplight Quay", "Bridgefoot", "Ferrygate", "Rope Walk"],
    ["Larchwood", None, "Old Mint", "Furnace Row"],          # None = Vell Park
    ["Coldharbour", "Hollin Fields", "Pinchgate", "Gasworks"],
]
PARK = (2, 1)
DISTRICTS = [d for row in GRID for d in row if d]
DISTRICT_WEIGHTS = {"Saltmarket": 14, "Cathedral Close": 7}
POS = {d: (r, c) for r, row in enumerate(GRID) for c, d in enumerate(row) if d}
def touches_park(d, corners=False):
    r, c = POS[d]; pr, pc = PARK
    dr, dc = abs(r - pr), abs(c - pc)
    return (dr + dc == 1) or (corners and dr == 1 and dc == 1)
# tram No. 7, stops in order (each stop lies in the district named after the colon)
TRAM7 = [("Quillon’s", "Saltmarket"), ("Vell Bridge", "Bridgefoot"), ("Ferrygate", "Ferrygate"),
         ("Old Mint", "Old Mint"), ("Hollin Fields", "Hollin Fields"), ("Pinchgate", "Pinchgate"),
         ("Furnace Row", "Furnace Row"), ("Gasworks", "Gasworks")]
TRAM_FROM, TRAM_TO = "Vell Bridge", "Gasworks"
def tram_between(d, inclusive=False):
    stops = [s for s, _ in TRAM7]; dists = [x for _, x in TRAM7]
    a, b = stops.index(TRAM_FROM), stops.index(TRAM_TO)
    rng = range(a, b + 1) if inclusive else range(a + 1, b)
    return d in [dists[i] for i in rng]

# ---------------------------------------------------------------- time
OPEN_FROM, LAST_ENTRY = "16:00", "21:29"
CURTAIN = "21:30"
def tmin(s):
    h, m = s.split(":"); return int(h) * 60 + int(m)
def tstr(m):
    return f"{m // 60:02d}:{m % 60:02d}"
BAND_SETS = [("17:00", "17:40"), ("18:20", "19:05"), ("19:50", "20:30")]
BAND = [(tmin(a), tmin(b)) for a, b in BAND_SETS]
def in_band(t, excl=False):
    return any((a < t < b) if excl else (a <= t <= b) for a, b in BAND)
GALLERY_FAST = 5                       # the Clock Gallery clocks run five minutes fast
TREE_BY_GALLERY = "19:00"              # the great tree was lit at seven by the gallery clocks
TREE_REAL = tmin(TREE_BY_GALLERY) - GALLERY_FAST     # 18:55 real time
def lower_half(minute, edges=True):
    """Minute hand pointing into the lower half of a clock face (below the 3–9 line)."""
    return (15 <= minute <= 45) if edges else (15 < minute < 45)

# ---------------------------------------------------------------- names
# Pools: vintage first names and surnames; the people in the story are kept out.
FIRST = """Ada Agnes Alma Amos Anna Annie Arthur Audrey Beatrix Bella Bernard Bertha Blanche Bruno
Carla Cecil Celia Clara Clement Cora Cyril Daisy Dora Doris Edgar Edith Effie Elsie Enid Ernest Esther
Ethel Felix Flora Frances Freda Gerald Gertie Gilbert Grace Greta Gwen Harold Hattie Hazel Hector
Henry Herbert Hilary Ida Ines Irene Iris Isla Ivor Jack Josie Judith Laura Laurie Lena Leon Lilian
Lorena Lorna Lottie Louisa Lucia Mabel Maisie Marcus Marina Marnie Martha Maud Mavis Mercy Milo
Minnie Miriam Morris Myrtle Nerina Nina Noel Nora Norma Olive Oscar Otto Pearl Percy Philippa
Rhoda Rita Robert Rosina Ruth Sadie Selma Serena Sorcha Stella Teresa Thea Thora Una Vera Viola
Walter Wilfred Willa Wilbur Winnie Arlene Andrei Carmen Doreen Esmond Gloria Harriet Ingrid Mirela
Orla Petra Roland Sabine Tamsin Ursel Valery Wendell Xenia Yvette Zelie Nadia Ottoline Rupert
Sabrine Tobias Ulric Vesna Wanda Yolande Zora Carina Dorita Elvira Margie Marcia Norine Orsola
Roxane Tamara Zarina Cherie Rowena Andrea Gracie""".split()
LAST = """Abney Allard Amory Anstey Archer Ashby Bagnall Barnet Baxter Beckett Blackmore Bolton
Bramall Brierley Brough Bullock Carrick Chadwick Collier Corrigan Cotterill Croft Dallow Darnell
Dawlish Denning Dobbs Dunning Eastwick Ellery Elwes Fairbank Farrow Fennell Finney Garnett Gilchrist
Goodall Gorringe Hadley Halliday Hammond Harker Hassall Hebden Hollins Horrocks Huxley Iddon Innes
Jarrett Jessop Kaye Kellett Kimber Lacey Lambert Lattimer Liddell Lockett Lomas Maddock Marriott
Mellor Merrick Moffatt Mossop Naylor Neill Nettleton Newall Noakes Nuttall Oddie Ogden Ollerton
Orrell Osborne Parrish Pell Pennell Perrott Pettit Pollitt Potter Prentice Pursell Quayle Quinnell
Radley Ramsell Rawlins Redmayne Rennie Rimmer Rossiter Rowell Russett Sallis Sanderell Scarrott
Seddon Sellick Sherratt Skerritt Sommers Spiller Stannard Stebbing Sutcliffe Swallow Tebb Tennant
Thackray Tillott Toller Towell Tuckett Turrell Tyrrell Unsworth Upcott Varley Vassall Venning
Wallace Warrell Webb Weller Wellbank Whittle Willett Winnell Wollaston Woodall Yarrow Yelland
Youell Zeller Nevill Norrell Pennick Pollard Purcell Rolland Sellars Tollett Vellacott Wardell
Woollard Yardley Neville Pottell Roskell Sallett Tarrell Upsall Varrell Wyllie Ollett Rummell
Sennett Tappell Usher Vossell Wassell Yewell Zennor Rushden Ormside Shipden Northey Pantridge
Tebbs Wells Penny Sturdevan Whitlowe Vintner""".split()
FIRST = sorted(set(FIRST))
LAST = sorted(set(LAST))

# ---------------------------------------------------------------- the killer and the people
KILLER = dict(ticket=2173, first="Verena", last="Pennock", town="Old Mint",
              gate="Tram", entry=tmin("18:31"), stall=20)
VICTIM = "Teodor Brann"
INSPECTOR = "Inspector Rhea Linfoot"
FINDER = "Lark Emery"            # junior window dresser who found him
NEWSVENDOR = "Pim Haskett"
DOORMAN = "Albie Crane"
TOYCLERK = "Nell Varney"
CONDUCTOR = "Sid Kettle"
WRAPPER = "Dot Fairley"
CLOCKMAKER = "Augustin Pryce"
TEAROOM = "Mrs Haddow"
MARK = "a little brass magpie brooch on her coat collar"
PEOPLE = [VICTIM, "Rhea Linfoot", FINDER, NEWSVENDOR, DOORMAN, TOYCLERK, CONDUCTOR, WRAPPER, CLOCKMAKER,
          "Haddow"]

# ---------------------------------------------------------------- clue helpers
VOWELS = set("AEIOU")
def digits(n):
    return f"{n:04d}"
def double_letter(s):
    s = s.upper(); return any(a == b for a, b in zip(s, s[1:]))
def repeat_letter(s):
    s = s.upper(); return len(set(s)) < len(s)

# ---------------------------------------------------------------- the 21 daily clues (windows 3-23)
# Each clue: day, window title, doc (what the page shows), note (the detective's question),
# fact (what the clue means, for the solution and level-3 hint), pred(record), alts:
# plausible misreadings that are also tested (the answer must survive each of them).
# record = dict(ticket, first, last, town, gate, entry, stall)
CLUES = [
    dict(day=3, group="entry", window="The Brass Band",
         note="The doorman says the lady with the magpie brooch came in while the band was playing. "
              "When could she have come in?",
         fact="She came in during one of the band’s three sets: 17:00–17:40, 18:20–19:05 or 19:50–20:30 "
              "(first and last minutes included).",
         pred=lambda r: in_band(r["entry"]),
         alts=[("first and last minute of each set left out", lambda r: in_band(r["entry"], excl=True))]),
    dict(day=4, group="gate", window="Snow on Tramway Yard",
         note="Which door did she use?",
         fact="From the tram shelter she went straight across Tramway Yard to the Tram Door, or through "
              "the Winter Garden to the Garden Door. Her door was Tram or Garden.",
         pred=lambda r: r["gate"] in TRAM_SIDE,
         alts=[("the Clock Door at the far corner of the yard counted as ‘straight across’ too",
                lambda r: r["gate"] in TRAM_SIDE_WIDE)]),
    dict(day=5, group="stall", window="The Toy Hall Stairs",
         note="Where in the store did she make her last purchase?",
         fact="She went up from the Toy Hall (Second Floor) and never came back down, so her last till "
              "is higher up than the Toy Hall: the Clock Gallery (18, 19), the Third Floor (20–23) or the "
              "Roof Terrace (24).",
         pred=lambda r: above_toy_hall(r["stall"]),
         alts=[("the Clock Gallery is only between floors, so it doesn’t count",
                lambda r: above_toy_hall(r["stall"], halves=False)),
               ("the Roof Terrace is outdoors, not a floor of the store",
                lambda r: above_toy_hall(r["stall"], roof=False))]),
    dict(day=6, group="town", window="The No. 7 Tram",
         note="Where does she live?",
         fact=f"She lives in a district whose stop on the No. 7 lies between {TRAM_FROM} and {TRAM_TO}: "
              "Ferrygate, Old Mint, Hollin Fields, Pinchgate or Furnace Row.",
         pred=lambda r: tram_between(r["town"]),
         alts=[("the two named stops counted as ‘between’ too", lambda r: tram_between(r["town"], inclusive=True))]),
    dict(day=7, group="name", window="The Glove Counter",
         note="What does the glove counter remember about her name?",
         fact="Her first name contains the letter R.",
         pred=lambda r: "R" in r["first"].upper(), alts=[]),
    dict(day=8, group="name", window="Paper and Ribbon",
         note="What does the wrapping desk tell you about her surname?",
         fact="Her parcel went in the N–Z rack, so her surname begins with a letter from N to Z.",
         pred=lambda r: r["last"][0].upper() >= "N",
         alts=[("“the second half of the alphabet” read as starting at M",
                lambda r: r["last"][0].upper() >= "M")]),
    dict(day=9, group="ticket", window="The Watchmaker’s Bench",
         note="What does the repair docket tell you about her pass?",
         fact="Her pass number is odd.",
         pred=lambda r: r["ticket"] % 2 == 1, alts=[]),
    dict(day=10, group="entry", window="The Great Tree",
         note="She was already in the store when the great tree was lit. What does that tell you?",
         fact="The tree was lit at seven o’clock by the Clock Gallery clocks, which run five minutes fast: "
              "18:55 real time. She came in at 18:55 or earlier.",
         pred=lambda r: r["entry"] <= TREE_REAL,
         alts=[("the five minutes forgotten (19:00 or earlier)", lambda r: r["entry"] <= tmin(TREE_BY_GALLERY)),
               ("strictly before 18:55", lambda r: r["entry"] < TREE_REAL)]),
    dict(day=11, group="town", window="Vell Park in the Snow",
         note="Where does she live?",
         fact="Her district is next to Vell Park: it shares a side with the park on the city map "
              "(Bridgefoot, Larchwood, Old Mint or Hollin Fields).",
         pred=lambda r: touches_park(r["town"]),
         alts=[("districts that only touch the park at a corner counted as ‘next to’ too",
                lambda r: touches_park(r["town"], corners=True))]),
    dict(day=12, group="stall", window="The Striped Cup",
         note="Where did she buy the cup of cocoa?",
         fact="The striped paper cup by Teodor’s sketchbook was her last purchase. Only four counters serve "
              "hot drinks in striped cups: 9, 20, 22 and 24. Her last till is one of them.",
         pred=lambda r: r["stall"] in CUP_DEPTS,
         alts=[("any counter that sells cocoa in any form, tins and powder included",
                lambda r: r["stall"] in COCOA_ANY)]),
    dict(day=13, group="name", window="Carols on the Stairs",
         note="What did the carol singer notice about her name?",
         fact="Her first name ends with a vowel: A, E, I, O or U (Y never counts).",
         pred=lambda r: r["first"][-1].upper() in VOWELS,
         alts=[("Y counted as a vowel", lambda r: r["first"][-1].upper() in VOWELS | {"Y"})]),
    dict(day=14, group="ticket", window="The Toy Train",
         note="What does the toy-train ticket tell you about her pass number?",
         fact="The four digits of her pass number add up to more than ten (11 or more).",
         pred=lambda r: sum(map(int, digits(r["ticket"]))) > 10,
         alts=[("“more than ten” read as “ten or more”", lambda r: sum(map(int, digits(r["ticket"]))) >= 10)]),
    dict(day=15, group="name", window="The Lace Counter",
         note="What did the monogram order say about her surname?",
         fact="Her surname has a double letter: the same letter twice, side by side.",
         pred=lambda r: double_letter(r["last"]),
         alts=[("any letter used twice, even apart", lambda r: repeat_letter(r["last"]))]),
    dict(day=16, group="entry", window="The Door Stamp",
         note="What does the clock stamp on her pass tell you?",
         fact="At the door every pass is stamped with a little clock face. On hers the minute hand pointed "
              "into the lower half of the face: minutes 15 to 45.",
         pred=lambda r: lower_half(r["entry"] % 60),
         alts=[("hands lying exactly on 3 or 9 (minutes 15 and 45) left out",
                lambda r: lower_half(r["entry"] % 60, edges=False)),
               ("‘lower half’ read as ‘pointing roughly down’ (minutes 20 to 40)",
                lambda r: 20 <= r["entry"] % 60 <= 40)]),
    dict(day=17, group="name", window="The Hat Box",
         note="What did the milliner see on the hat-box label?",
         fact="Her surname has more letters than her first name.",
         pred=lambda r: len(r["last"]) > len(r["first"]),
         alts=[("“more letters” read as “at least as many”", lambda r: len(r["last"]) >= len(r["first"]))]),
    dict(day=18, group="ticket", window="The Clock Gallery",
         note="What did Mr Pryce notice about her pass number?",
         fact="All four digits of her pass number are different.",
         pred=lambda r: len(set(digits(r["ticket"]))) == 4,
         alts=[("leading zeros ignored (0472 read as 472)",
                lambda r: len(set(str(r["ticket"]))) == len(str(r["ticket"])))]),
    dict(day=19, group="name", window="Christmas Cards",
         note="What does the card signature tell you?",
         fact="Her first name has exactly six letters.",
         pred=lambda r: len(r["first"]) == 6, alts=[]),
    dict(day=20, group="ticket", window="Red and Green",
         note="What colour was her pass?",
         fact="Passes 0001–1200 were green and 1201–2400 were red. Hers was red, so her pass number is "
              "1201 or higher.",
         pred=lambda r: r["ticket"] >= 1201, alts=[]),
    dict(day=21, group="name", window="The Linen Ledger",
         note="What does the linen ledger tell you about her surname?",
         fact="Her surname contains the letter E exactly once (capital or small).",
         pred=lambda r: r["last"].upper().count("E") == 1,
         alts=[("“exactly once” read as “at least once”", lambda r: "E" in r["last"].upper())]),
    dict(day=22, group="name", window="Two Initials",
         note="What did the engraver notice about her initials?",
         fact="Her first name and surname begin with different letters.",
         pred=lambda r: r["first"][0].upper() != r["last"][0].upper(), alts=[]),
    dict(day=23, group="name", window="Sugared Almonds",
         note="What does the sweet counter tell you about her name?",
         fact="Her first name and surname together have an odd number of letters.",
         pred=lambda r: (len(r["first"]) + len(r["last"])) % 2 == 1, alts=[]),
]
for c in CLUES:
    c["id"] = str(c["day"])
    c["label"] = f"Window {c['day']}"
CHECKPOINTS = [6, 12, 18]
WALK_ORDER = [c["id"] for c in CLUES]          # the calendar fixes the order: one window a day

# ---------------------------------------------------------------- story text
INTRO = [
    f"Every December, {STORE} on Lantern Street, the grandest department store in {CITY}, "
    "unveils one new Christmas window each evening. Twenty-four windows, one a day, and on Christmas "
    "Eve, at half past nine, the curtain rises on the Grand Window.",
    "Christmas Eve is Lantern Night. The store stays open late, the brass band plays on the steps, and "
    "every shopper is given a numbered Lantern Pass at the door. The pass is scanned on the way in and "
    "used to pay at every till. That night 2,400 passes were handed out.",
    f"At 21:20, ten minutes before the curtain, {FINDER}, the junior window dresser, found {VICTIM} "
    "in the window workshop on the Third Floor. Teodor had dressed every window at Quillon’s for "
    "thirty-one years. He was slumped over his sketchbook, and beside him stood a striped paper cup of "
    "cocoa that had been laced with something that was never on any menu.",
    f"{INSPECTOR} sealed what she found into twenty-four envelopes, in the order she found it. "
    "Open one window a day. By Christmas Eve, one Lantern Pass will be left.",
]
KNOWN_FACTS = [
    "The Lantern Register lists every pass issued on Lantern Night exactly once: passes 0001–2400, no "
    "gaps, and no two shoppers share a full name.",
    "Time in is when the pass was scanned at the door. Door is where it was scanned: the Arcade Door, "
    "the Clock Door, the Tram Door or the Garden Door (the register prints the first word only).",
    "Home district is the district written on the pass form. Every district is on the city map.",
    "Last till is the department where the pass made its final purchase of the night. Every pass bought "
    "at least one thing. Department numbers are on the store plan.",
    "Whoever carried the striped cup of cocoa up to Teodor bought it with their own pass, and it was "
    "their last purchase of the night.",
    f"Only one shopper wore {MARK}. Every witness who mentions the brooch was looking at the killer.",
]
GLOSSARY = [
    ("Letters", "Count letters only. Every name in the register is a single word with no spaces, hyphens "
                "or apostrophes."),
    ("Vowels", "A, E, I, O and U. In this case Y is never a vowel."),
    ("Capital or small", "A letter counts whether it is a capital or not: Ellery contains the letter E "
                         "twice, Lacey once."),
    ("Times", "All times are 24-hour clock on Christmas Eve, real time unless a window says otherwise. "
              "“18:55 or earlier” includes 18:55. A range such as 17:00–17:40 includes both ends."),
    ("Minutes", "The minutes of 18:07 are 07."),
    ("Pass digits", "Read all four digits as printed, zeros included: pass 0472 has the digits 0, 4, 7 "
                    "and 2, which add up to 13."),
    ("Double letter", "The same letter twice, side by side: the LL in Wallace, the NN in Tennant."),
    ("Floors", "The store has five floors (Lower Ground, Ground, First, Second, Third), two half-landings "
               "between floors (the Half Landing and the Clock Gallery) and the Roof Terrace on top. "
               "The store plan shows where every department is."),
    ("Tram stops", "A stop belongs to the district it is drawn in on the city map."),
]
HOW_TO_PLAY = [
    ("What this is", "A murder mystery in 24 windows. Each day from 1 to 24 December you open one "
                     "window: a page with one new piece of evidence. Day 1 sets the scene, Day 2 is the "
                     "Lantern Register of 2,400 shoppers, and Days 3 to 23 each rule some of them out. "
                     "On Christmas Eve one pass is left."),
    ("Setting up", "Print the Set-up pages and the 24 windows. Fold each window into its own envelope "
                   "(there is a template, or use any envelopes) and stick on the day numbers. On a tablet, "
                   "just tap today’s window on the calendar page."),
    ("Each day", "Open today’s window, read the evidence and work out what it means. Then go through "
                 "the shoppers who are still in on the register and cross out everyone who doesn’t fit. "
                 "The first few days take 20–30 minutes; later days take 5–10."),
    ("Who plays", "One detective on their own, or up to four working together. Split the register "
                  "between you and compare notes."),
    ("Check-ins", "Windows 6, 12 and 18 tell you how many passes should still be in, so you can catch a "
                  "slip early."),
    ("Stuck?", "The hint pages at the back give three levels of help for every window. Each level sits "
               "on its own pages, so you only see what you ask for."),
    ("The last window", "On 24 December, open the Grand Window. Use the Sealed Check to test your answer "
                        "without spoilers, then open the Envelope (the separate solution file)."),
]
LETTER = [
    "21 December",
    "Dear Inspector Linfoot,",
    "You will think me a foolish old man. For three weeks someone has been taking the real stones "
    "out of the necklace in my Jewel Window and leaving paste behind. Nobody else has noticed. Glass "
    "and diamonds look the same from the pavement, but they do not look the same to me.",
    "Each time, I have seen the same thing on the shop floor: a little brass magpie, pinned to a coat "
    "collar. I have never seen the face above it. I only ever see the brooch catch the light.",
    "I have told nobody at Quillon’s. On Christmas Eve, when the curtain rises on the Grand Window, I "
    "mean to show the whole of Lantern Street what I have seen. Until then I am putting it all into my "
    "windows, one a day, where a careful eye can read it.",
    "If anything should happen to me before then, look at the windows.",
    "Yours, with apologies for the fuss,",
    "Teodor Brann, Window Dresser",
]
LETTER_NOTE = ("Teodor posted this on 21 December. It reached me on the 27th, three days after we found "
               "him. — R.L.")

# ---------------------------------------------------------------- the daily documents
# Free text shown on each window page (statements, labels, logs). Kept here so the checker can
# read exactly what the player reads.
DOCS = {
    3: dict(kind="programme", title="LANTERN NIGHT — THE BAND ON THE STEPS",
            lines=[("First set", "17:00 – 17:40"), ("Mince pies for the band", "17:40 – 18:20"),
                   ("Second set", "18:20 – 19:05"), ("Tea in the staff canteen", "19:05 – 19:50"),
                   ("Third set", "19:50 – 20:30"), ("Instruments packed away", "from 20:30")],
            statement=(DOORMAN, "I couldn’t tell you which door she used — I go up and down the steps all "
                       "night — but I remember the brass magpie on her collar going past me while the band was playing. I "
                       "remember because the big drum made her jump.")),
    4: dict(kind="statement", title="STATEMENT — THE NEWSPAPER STAND AT THE TRAM SHELTER",
            statement=(NEWSVENDOR, "She got down off the No. 7 at the shelter opposite the store, bought an evening paper "
                       "and crossed Tramway Yard. Then I lost her in the snow. She went in either straight "
                       "across, or through the Winter Garden — one or the other, I’d swear to that much."),
            extra="The street plan is in Window 1."),
    5: dict(kind="statement", title="STATEMENT — TOY HALL, SECOND FLOOR",
            statement=(TOYCLERK, "Brass magpie on her collar, bought nothing, looked at the train set for "
                       "a minute. Then she went up the main stairs. I watched them all evening, waiting for "
                       "my relief: she never came back down before the curtain."),
            extra="So her last purchase of the night was made somewhere higher up than the Toy Hall. "
                  "The store plan is in Window 1."),
    6: dict(kind="tram", title="VELLMOUTH TRAMWAYS — CONDUCTOR’S NOTE, ROUTE 7",
            statement=(CONDUCTOR, "Lady with a brass bird on her collar. Asked me to wake her if she "
                       "dozed off: she said she gets off somewhere between Vell Bridge and Gasworks, but she "
                       "didn’t say which stop."),
            extra="Route 7 and its stops are on the city map on this page."),
    7: dict(kind="ticket", title="GLOVES & SCARVES — ALTERATION TICKET",
            statement=("The glove counter", "She left a pair of grey kid gloves to be taken in, and I "
                       "wrote her first name on the ticket. The ticket has gone, but I remember the R — I "
                       "always make a fuss of my capital and small Rs."),
            extra="The R could have been anywhere in her first name."),
    8: dict(kind="rack", title="GIFT WRAPPING — PARCELS TO COLLECT",
            statement=(WRAPPER, "Every parcel left with us is filed by the customer’s surname, in one of "
                       "two racks: A to M, or N to Z. Hers — the lady with the magpie — went in the second "
                       "rack. She never came back for it.")),
    9: dict(kind="docket", title="WATCHES & JEWELLERY — REPAIR DOCKET",
            statement=("The watch repairer", "She brought in a little silver watch for a new glass. I copied "
                       "her pass number onto the docket — the corner’s torn off now, but it was an odd "
                       "number, I remember thinking so.")),
    10: dict(kind="tree", title="NOTICE BOARD — THE GREAT TREE",
             statement=("Store guide, page 2", "Every clock in the Clock Gallery is set five minutes fast, "
                        "so that nobody is ever late for the Grand Window."),
             extra=(CLOCKMAKER + ": “The great tree was lit at seven o’clock by my gallery clocks. The lady "
                    "with the brass magpie was already down there in the crowd, watching.”")),
    11: dict(kind="map", title="VELLMOUTH TRAMWAYS — LOST PROPERTY",
             statement=("Lost property office", "A woman’s scarf left on the No. 7, with a laundry tag "
                        "pinned inside: ‘Return to the lady with the magpie brooch. Lives next to the "
                        "park.’"),
             extra="Vell Park is the green square on the city map."),
    12: dict(kind="cups", title="STORE GUIDE — HOT DRINKS ON LANTERN NIGHT",
             statement=("Store guide", "Hot drinks to take away are served in our red-and-white striped "
                        "paper cups at four counters only: the Lantern Bar (9), the Quillon Tea Room (20), "
                        "the cider and cocoa cart in Christmas Decorations (22) and the Roof Terrace (24)."),
             extra="Cocoa tins (Sweet Shop, 3) and drinking chocolate powder (Food Hall, 1) are sold in their "
                   "own boxes, never in cups."),
    13: dict(kind="statement", title="STATEMENT — CAROL SINGERS ON THE MAIN STAIRS",
             statement=("The choir’s alto", "She told us her name when we sang for her, and we made up a "
                        "verse. It rhymed because her first name ended on a vowel — we sang it long, "
                        "‘ah’ or ‘ee’ or ‘oh’. Nothing with a Y, I’m certain.")),
    14: dict(kind="ticket", title="TOY HALL — TICKET FOR THE TOY TRAIN RIDE",
             statement=("The toy train guard", "She paid for a ride for a little boy who’d lost his "
                        "mother in the crowd. I punch the pass number into the ticket. The holes are torn "
                        "through, but I added the digits for the lucky-number game: they came to more "
                        "than ten.")),
    15: dict(kind="order", title="HABERDASHERY — MONOGRAM ORDER",
             statement=("The lace counter", "She ordered a handkerchief with her surname stitched in "
                        "full. I remember charging her for a double letter — two the same, side by "
                        "side, take longer.")),
    16: dict(kind="stamp", title="THE DOOR STAMP",
             statement=("Door rules", "Every pass is stamped at the door with a little clock face showing "
                        "the minute hand at the time of entry (the hour is not shown)."),
             extra=(DOORMAN + ": “I saw the stamp when she held her pass up to the scanner: the minute hand "
                    "pointed into the lower half of the face.”")),
    17: dict(kind="label", title="HATS & UMBRELLAS — HAT-BOX LABEL",
             statement=("The milliner", "I wrote her name on the hat-box label myself. Her surname "
                        "took up more room than her first name — more letters, I mean, not bigger ones.")),
    18: dict(kind="statement", title="STATEMENT — THE CLOCK GALLERY",
             statement=(CLOCKMAKER, "She stopped to set her watch by my clocks and I told her they run "
                        "fast. She laughed and showed me her pass: ‘Look, not one number twice — that’s "
                        "lucky.’ All four digits different, she meant.")),
    19: dict(kind="card", title="STATIONERY & CARDS — A CHRISTMAS CARD",
             statement=("The card counter", "She wrote a card at the counter and signed it with her "
                        "first name, then blotted it. I didn’t read it, but the blotter kept the shape of "
                        "it: six letters, exactly.")),
    20: dict(kind="pass", title="LANTERN PASSES — PRINTER’S NOTE",
             statement=("The printer", "We printed 2,400 passes for Lantern Night: numbers 0001 to 1200 on "
                        "green card, 1201 to 2400 on red."),
             extra=(DOORMAN + ": “Her pass was red. I noticed it when she held it up to the scanner, because "
                    "it matched the band’s coats.”")),
    21: dict(kind="ledger", title="HOME & LINEN — DELIVERY LEDGER",
             statement=("The linen ledger", "She ordered a blanket to be sent on. The clerk spelled her "
                        "surname back to her and she said: ‘Only one E. People always add a second.’")),
    22: dict(kind="engraving", title="SILVERWARE — ENGRAVING ORDER",
             statement=("The engraver", "Two initials on a little silver frame, first name then surname. "
                        "Two different letters — I charge extra for flourishes on each.")),
    23: dict(kind="almonds", title="THE SWEET SHOP — A BAG OF SUGARED ALMONDS",
             statement=("The sweet counter", "She wanted almonds to spell out a name on a Christmas cake: "
                        "one almond for every letter of her first name and surname together. I counted them "
                        "into the bag myself, and the last one had no partner — an odd number.")),
}

EPILOGUE = [
    "The lady with the brass magpie was Verena Pennock, a maker of costume jewellery from Old Mint, "
    "pass 2173.",
    "Verena made paste: glass stones so good that only an expert could tell them from diamonds. That "
    "autumn a buyer offered her a great deal of money for real stones, no questions asked. Every few "
    "days in December she came to Quillon’s, waited until the Jewel Window was being tidied, and swapped "
    "one more diamond in the necklace for one of her own.",
    "Teodor noticed. He knew every stone in his windows the way other people know their own "
    "handwriting. He saw the magpie brooch three times, never the face above it, and he decided to say "
    "so in the Grand Window: a snowy window with a magpie stealing a necklace from a gloved hand.",
    "On Lantern Night Verena came in at 18:31 by the Tram Door, straight off the No. 7 from Old Mint, "
    "while the band was playing its second set. She watched the great tree being lit, went up through "
    "the Toy Hall, and at the Tea Room she bought one striped cup of cocoa. Her red pass paid for it. "
    "It was the last thing she bought.",
    "She took the cup to the workshop door with the Tea Room’s compliments. Teodor, busy with his "
    "magpie, drank it without looking up.",
    "Inspector Linfoot found the rest in Teodor’s windows, one a day, just as he had promised. The "
    "Grand Window opened a week late, exactly as he had drawn it. Lantern Street has never been so "
    "crowded.",
]
