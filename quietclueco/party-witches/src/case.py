"""Murder at the Lantern Supper — a murder mystery party for 6–12 players, set in Morrowmere.

Everything the checker and the renderer need lives here: the house, the true timeline of every
character, the booklets (what each guest reads and says in each round), the evidence cards, the
host's scripts and the sealed solution. Every booklet and card line that matters to the logic
carries structured claims, so verify.py can check them against the timeline and solve the case.
"""

TITLE = "Murder at the Lantern Supper"
SUBTITLE = "A Morrowmere Murder Mystery Party"
BRAND = "QuietClueCo"
PLAYERS = "6–12 players"
PLAYTIME = "2–3 hours"
SLUG = "murder-at-the-lantern-supper"
DATE = "31 October"
HOUSE = "Larkwell Hall"
VILLAGE = "Morrowmere"
CIRCLE = "the Hearth Circle"
VICTIM = "Rowena Heatherly"
INSPECTOR = "Inspector Hollis Drummond"

# ---------------------------------------------------------------- the house
# Ground floor on a 3 x 3 grid (north at the top), the upper floor above part of it.
ROOMS = {
    "Library": ("ground", (0, 0)), "Herb Garden": ("ground", (0, 1)), "Still Room": ("ground", (0, 2)),
    "Parlour": ("ground", (1, 0)), "Great Hall": ("ground", (1, 1)), "Kitchen": ("ground", (1, 2)),
    "Cloakroom": ("ground", (2, 0)), "Porch": ("ground", (2, 1)), "Pantry": ("ground", (2, 2)),
    "Lantern Room": ("upper", (0, 2)), "Gallery": ("upper", (1, 1)), "Bell Tower": ("upper", (2, 1)),
}
OUTDOORS = {"Herb Garden"}
# doors and stairs (both ways). The Lantern Room is reached only by the stair in the Still Room.
DOORS = [
    ("Library", "Herb Garden", "French window"), ("Library", "Parlour", "door"), ("Library", "Great Hall", "door"),
    ("Herb Garden", "Great Hall", "north door"), ("Herb Garden", "Still Room", "garden door"),
    ("Still Room", "Kitchen", "inner door"), ("Still Room", "Lantern Room", "stair"),
    ("Parlour", "Great Hall", "door"), ("Parlour", "Cloakroom", "door"),
    ("Great Hall", "Kitchen", "door and serving hatch"), ("Great Hall", "Porch", "front doors"),
    ("Great Hall", "Gallery", "stair"),
    ("Kitchen", "Pantry", "door"), ("Cloakroom", "Porch", "door"),
    ("Porch", "Bell Tower", "tower stair"), ("Gallery", "Bell Tower", "across the upper landing"),
]
# who can see into which room from where (besides being in the same room)
VIEWS = [("Gallery", "Great Hall"), ("Great Hall", "Gallery"), ("Kitchen", "Great Hall"), ("Great Hall", "Kitchen"),
         ("Kitchen", "Herb Garden"), ("Library", "Herb Garden"), ("Bell Tower", "Gallery"), ("Gallery", "Bell Tower")]

SLOTS = ["21:30", "21:45", "22:00", "22:15", "22:30", "22:45"]   # each slot is the quarter hour that starts then

# ---------------------------------------------------------------- the people
# key: (name, role, core?, costume in two words, candle colour, one-line hook)
PEOPLE = {
    "cordelia": ("Cordelia Heatherly", "Rowena’s niece, who expects to inherit Larkwell Hall", True, "velvet cape", "green",
                 "Charming, impatient and sure the Hall will be hers one day."),
    "marigold": ("Marigold Fenn", "Keeper of the Still Room, the Circle’s herbalist", True, "herb apron", "amber",
                 "Knows every plant in the garden and holds the only key to the poison cabinet."),
    "silas": ("Silas Ashgrove", "Treasurer of the Hearth Circle", True, "waistcoat & pocket watch", "green",
              "Counts every penny of the lantern fund. Lately, a little too carefully."),
    "clementine": ("Clementine Reed", "Candlemaker, whose workshop is in the Hall’s coach house", True, "wax-spattered smock",
                   "green", "Makes every candle the Circle burns, and tonight she brought the best of them."),
    "rufus": ("Rufus Hawthorn", "Caretaker and bellringer of Larkwell Hall", True, "tweed & keys", "white",
              "Has looked after the Hall for thirty years and rings its bell on every feast night."),
    "isadora": ("Isadora Quince", "A mapmaker who came to Morrowmere this autumn", True, "travelling cloak", "violet",
                "A newcomer with sharp eyes, a sharper pencil and a reason for coming she hasn’t told anyone."),
    "meridew": ("Mother Meridew", "The village tea-leaf reader", False, "shawls & spoons", "blue",
                "Reads cups for anyone who asks, and remembers everything she reads."),
    "linnet": ("Linnet Fairweather", "Rowena’s goddaughter, who sings in the choir", False, "star-print dress", "gold",
               "Rowena’s favourite, and the one who found her."),
    "tamsin": ("Tamsin Rook", "Cook of Larkwell Hall", False, "flour & ladle", "white",
               "Runs the kitchen, hears every door in the house and serves the best cider on the hill."),
    "percival": ("Percival Hobb", "Clerk of the Hearth Circle", False, "spectacles & ledger", "red",
                 "Writes down everything, especially what people would rather he didn’t."),
    "ned": ("Ned Quarrie", "Fiddler of the midnight choir", False, "fiddle & cap", "red",
            "Plays at every wedding, wake and feast in the valley, and never misses a beat."),
    "bryony": ("Bryony Fettle", "The lantern girl", False, "lantern & scarf", "blue",
               "Lights every lantern in Morrowmere and notices every footprint on the way."),
}
CORE = [k for k, v in PEOPLE.items() if v[2]]
OPTIONAL = [k for k, v in PEOPLE.items() if not v[2]]
# the order extra roles are added as the guest list grows (7 guests: + the first, and so on)
ADD_ORDER = ["meridew", "linnet", "tamsin", "percival", "ned", "bryony"]
def name(k):
    return PEOPLE[k][0]
def first(k):
    return PEOPLE[k][0].split()[-1] if k == "meridew" else PEOPLE[k][0].split()[0]

KILLER = "clementine"

# The true timeline: where everyone really was in each quarter hour. Only the sealed solution
# prints it in full; verify.py checks every booklet and card against it.
TIMELINE = {
    "rowena":     ["Great Hall", "Great Hall", "Kitchen", "Lantern Room", "Still Room", "Still Room"],
    "cordelia":   ["Great Hall", "Great Hall", "Great Hall", "Gallery", "Gallery", "Great Hall"],
    "marigold":   ["Still Room", "Kitchen", "Kitchen", "Pantry", "Kitchen", "Kitchen"],
    "silas":      ["Great Hall", "Parlour", "Library", "Library", "Library", "Great Hall"],
    "clementine": ["Great Hall", "Parlour", "Great Hall", "Still Room", "Great Hall", "Great Hall"],
    "rufus":      ["Porch", "Porch", "Porch", "Bell Tower", "Bell Tower", "Porch"],
    "isadora":    ["Great Hall", "Great Hall", "Library", "Library", "Library", "Great Hall"],
    "meridew":    ["Great Hall", "Great Hall", "Library", "Library", "Library", "Great Hall"],
    "linnet":     ["Great Hall", "Great Hall", "Great Hall", "Great Hall", "Great Hall", "Still Room"],
    "tamsin":     ["Kitchen", "Kitchen", "Kitchen", "Kitchen", "Kitchen", "Kitchen"],
    "percival":   ["Porch", "Great Hall", "Great Hall", "Great Hall", "Great Hall", "Great Hall"],
    "ned":        ["Great Hall", "Great Hall", "Great Hall", "Great Hall", "Great Hall", "Great Hall"],
    "bryony":     ["Herb Garden", "Great Hall", "Great Hall", "Great Hall", "Herb Garden", "Great Hall"],
}
KILLER_ROUTE = ["Great Hall", "Herb Garden", "Still Room", "Herb Garden", "Great Hall"]   # out and back at 22:15

# ---------------------------------------------------------------- the logic of the case
# The poison went into the glass while Rowena was upstairs. Readings of "between a quarter past and
# half past ten" (the poisoner may have needed the 22:30 quarter too) are both tested.
WINDOW_READINGS = {"the quarter from 22:15 only": ["22:15"],
                   "22:15 and the 22:30 quarter as well": ["22:15", "22:30"]}
POISON_ROOM = "Still Room"
WAX_COLOUR = "green"
# place words that a player has to read off the plan, with every reasonable reading
PLACE_READINGS = {
    "across the landing from the tower door": {
        "the Gallery (the only room facing the tower door on the plan)": {"Gallery"},
        "any room on the upper floor except the tower": {"Gallery", "Lantern Room"},
        "the upper landing, Gallery or tower doorway": {"Gallery", "Bell Tower"},
    },
}

# ---------------------------------------------------------------- the evidence cards
# Each card: id, round, title, text lines; claims (structured, checked) and key (needed to solve).
# Claim types:
#   ("window",)                    the poison went in during the window (see WINDOW_READINGS)
#   ("at", who, rooms, slots)      who was in one of rooms during every listed slot
#   ("colour", who, colour)        the colour of who's lantern candle
#   ("wax", colour)                the poisoner's candle colour
#   ("route", room)                the poisoner passed through room on the way in
CARDS = [
    dict(id="1", round=1, title="The Green Glass",
         text=["At ten o’clock Rowena poured her blackberry cordial into her green glass in the Kitchen and took "
               "a sip in front of Tamsin the cook. “Perfect,” she said, and carried it to the Still Room.",
               "At a quarter past ten she climbed the stair to the Lantern Room, above the Still Room, to trim "
               "the midnight lantern. Everyone in the Kitchen heard her footsteps overhead. She left the glass on "
               "the Still Room table.",
               "At half past ten she came back down, sat by the fire and drank. At a quarter to eleven Linnet "
               "found her there, the glass empty beside her.",
               "The doctor is certain: crushed foxglove went into the glass after Rowena climbed the stair and "
               "before she came back down."],
         claims=[("window",), ("at", "rowena", {"Lantern Room"}, ["22:15"]), ("at", "rowena", {"Kitchen"}, ["22:00"])],
         key=True),
    dict(id="2", round=1, title="The Lantern Ledger",
         text=["Every guest at the Lantern Supper carries a lantern with a candle of their own colour. Bryony "
               "writes them all down at the door, as she does every year:",
               "LEDGER"],
         claims=[("colour", k, PEOPLE[k][4]) for k in PEOPLE], key=True),
    dict(id="3", round=1, title="The Choir and the Kitchen",
         text=["From ten o’clock until a quarter to eleven the midnight choir rehearsed in the Great Hall in front "
               "of the fire: Linnet, Percival and Ned on the fiddle. Bryony handed round the song sheets until "
               "half past ten, then went out to relight the garden lanterns.",
               "Tamsin never left the Kitchen all evening: she kept the cider coming through the serving hatch.",
               "Mother Meridew played cards in the Library with two partners from ten until twenty to eleven and "
               "never left the table. Ask her partners who they were.",
               "None of them could have reached the Still Room unseen."],
         claims=[("at", "linnet", {"Great Hall"}, ["22:00", "22:15", "22:30"]),
                 ("at", "percival", {"Great Hall"}, ["22:00", "22:15", "22:30", "22:45"]),
                 ("at", "ned", {"Great Hall"}, ["22:00", "22:15", "22:30", "22:45"]),
                 ("at", "bryony", {"Great Hall"}, ["22:00", "22:15"]),
                 ("at", "tamsin", {"Kitchen"}, SLOTS),
                 ("at", "meridew", {"Library"}, ["22:00", "22:15", "22:30"])],
         key=False),
    dict(id="4", round=1, title="The Still Room Floor",
         text=["Wet garden mud and crushed chamomile on the Still Room floor, in a trail from the garden door to the "
               "table and back again. Someone came through the herb garden and in at the garden door.",
               "On the table: Rowena’s green glass, empty, and a few torn shreds of foxglove leaf."],
         claims=[("route", "Herb Garden")], key=False),
    dict(id="5", round=2, title="The Practice Peal",
         text=["At a quarter past ten the bell of Larkwell Hall began the practice peal for midnight. It rang without "
               "a single break until half past ten. Every guest heard it.",
               "The bell rope hangs in the Bell Tower, and it takes two hands and a strong back to keep it going."],
         claims=[], key=False),
    dict(id="6", round=2, title="The Poison Cabinet",
         text=["The poison cabinet in the Still Room is still locked. Marigold Fenn carries the only key on her belt.",
               "Inside, the foxglove tincture bottle is full, its wax seal unbroken. Whoever poisoned Rowena did not "
               "need the key: the leaves in the glass were fresh, torn from the foxglove bed in the herb garden."],
         claims=[], key=False),
    dict(id="7", round=2, title="The Lantern Fund Book",
         text=["The Hearth Circle’s lantern fund book, found in Rowena’s desk with a ribbon at the last page. "
               "One hundred and twenty pounds are missing since midsummer. Each withdrawal is initialled S.A.",
               "In the margin, in Rowena’s hand: “Speak to S. before the Supper.”"],
         claims=[], key=False),
    dict(id="8", round=2, title="A Torn Page",
         text=["Half of a page torn from a new will, found in the Gallery desk:",
               "“…and I leave Larkwell Hall, its garden and everything in it to the Hearth Circle, to be kept as a "
               "meeting house for as long as there is a lantern to light…”",
               "The other half is missing."],
         claims=[], key=False),
    dict(id="9", round=3, title="The Rim of the Glass",
         text=["Under Inspector Drummond’s lens: a single drip of candle wax on the rim of the green glass, hard and "
               "smooth. It fell from the poisoner’s own lantern as they bent over the glass.",
               "The wax is green."],
         claims=[("wax", WAX_COLOUR)], key=True),
    dict(id="10", round=3, title="Rowena’s Speech",
         text=["Rowena’s notes for her midnight speech, folded in her pocket:",
               "“Tonight I name the next Lantern Keeper of the Hearth Circle. Not the one you expect: my daughter, "
               "Isadora Quince, who came home to me this autumn after thirty years.”"],
         claims=[], key=False),
    dict(id="11", round=3, title="A Notice to Quit",
         text=["A notice in Rowena’s writing desk, ready but unsigned:",
               "“To Clementine Reed. The lease of the coach house workshop at Larkwell Hall ends at Martinmas. "
               "The candle trade must find another home.”",
               "Pinned to it: “Sign at midnight.”"],
         claims=[], key=False),
]

# ---------------------------------------------------------------- the booklets
# For each character: who you are, your secret, and what you know and say in each round.
# Each round is a list of (text, claims). Claim types as above, plus:
#   ("saw", who_saw, whom, room, slots)   who_saw saw whom in room during every listed slot
#   ("heard", ...)                        flavour: heard, not seen; never used to rule anyone out
#   ("lie", ...)                          the killer's own false account (only the killer has one)
# Claims about a person's own whereabouts are never used to clear that person.
B = {}
B["cordelia"] = dict(
    intro=["You are Rowena’s niece, her only family in Morrowmere (as far as anyone knows). You grew up running "
           "about Larkwell Hall, and everyone has always said that one day it will be yours. You have already "
           "chosen new curtains.",
           "Lately Aunt Rowena has been strange with you: polite, distant, and twice she has stopped talking when "
           "you came into the room. Tonight she promised “an announcement at midnight”."],
    secret="Just after ten you slipped up to the Gallery to look through the papers in Rowena’s writing desk. "
           "You found half of a new will that leaves the Hall to the Hearth Circle, and you tore it in two before "
           "you could stop yourself. You are ashamed, and frightened of how it looks.",
    rounds=[
        [("Introduce yourself: the niece, the heir, and very glad to see everyone. Say how fond you were of your "
          "aunt (it’s true, mostly).", []),
         ("Where were you? Say you were in the Great Hall until about ten, “then upstairs for a little quiet”. "
          "Don’t say what you were doing.", []),
         ("What you saw: Rowena left the Great Hall for the Kitchen just before ten, humming.", [
             ("saw", "cordelia", "rowena", "Great Hall", ["21:45"])])],
        [("The torn page has been found. Admit the truth: from ten past ten you were in the Gallery, reading "
          "Rowena’s papers in the writing desk. You found the new will and tore it.", []),
         ("Your alibi: “From the Gallery I could see across the landing into the tower. Rufus was at the "
          "bell rope the whole peal, from a quarter past until it stopped at half past, and then he sat on the "
          "tower step until twenty to eleven. He never came down.”", [
             ("saw", "cordelia", "rufus", "Bell Tower", ["22:15", "22:30"])])],
        [("Rowena meant to leave the Hall to the Circle. You are hurt, but you would never have harmed her. Say so.",
          []),
         ("Ask Isadora what she really came to Morrowmere for.", [])],
    ],
    ask=["Who left the Great Hall after ten o’clock?", "Who knew about Aunt Rowena’s cordial?",
         "Silas, why did my aunt want a word with you?"],
)
B["marigold"] = dict(
    intro=["You keep the Still Room at Larkwell Hall: the drying racks, the jars, the remedies and the locked poison "
           "cabinet, whose only key hangs on your belt. You have been Rowena’s right hand for twenty years.",
           "Everyone in the Circle knows Rowena means to name the next Lantern Keeper tonight, and everyone assumes "
           "it will be you. So do you."],
    secret="At a quarter past ten you slipped into the Pantry and took a jar of the Circle’s heather honey to keep "
           "for yourself. It is a small thing, but in your position a very silly one.",
    rounds=[
        [("Introduce yourself: Keeper of the Still Room, Rowena’s oldest friend in the Circle.", []),
         ("Where were you? In the Still Room until half past nine sorting the drying racks, then in the Kitchen "
          "helping Tamsin with the cider. At about a quarter past ten you stepped into the Pantry on your own "
          "“for more cups”, and were back in the Kitchen by half past.", []),
         ("What you saw: at ten Rowena poured her blackberry cordial in the Kitchen and tasted it. It was perfectly "
          "good then.", [("saw", "marigold", "rowena", "Kitchen", ["22:00"])]),
         ("What you heard: soon after, Rowena’s footsteps on the Lantern Room stair, above the Still Room.",
          [("heard",)])],
        [("The poison cabinet card: you are relieved. The bottle is full and sealed, so your key had nothing to do "
          "with it.", []),
         ("If someone asks about the Pantry, admit you took a jar of the Circle’s heather honey. Blush.", [])],
        [("Rowena’s speech notes say she meant to name Isadora, not you. You didn’t know. Say so, and say it hurts.",
          []),
         ("You knew foxglove grows in the herb garden. So did every member of the Circle.", [])],
    ],
    ask=["Who has been in the herb garden tonight?", "Clementine, where were you during the peal?",
         "Who here knew Rowena kept her glass in the Still Room?"],
)
B["silas"] = dict(
    intro=["You are the treasurer of the Hearth Circle. You keep the lantern fund: the money that buys candles, "
           "pays for the Moon Fair and mends the Hall’s roof.",
           "You also love a game of cards, and you are very good at it."],
    secret="Since midsummer you have taken one hundred and twenty pounds from the lantern fund to pay the man who "
           "mended your own roof. You meant to put it back before anyone noticed. Rowena noticed.",
    rounds=[
        [("Introduce yourself: treasurer, card player, keeper of every penny.", []),
         ("Where were you? “At ten o’clock I sat down to cards in the Library with Isadora Quince and Mother Meridew, "
          "and we played until twenty to eleven. Isadora never left the table, and neither did I. She won twice.”",
          [("saw", "silas", "isadora", "Library", ["22:00", "22:15", "22:30"])]),
         ("Before that you were in the Parlour, talking to Clementine about the price of beeswax.", [
             ("saw", "silas", "clementine", "Parlour", ["21:45"])])],
        [("The lantern fund book has been found. Admit the money is gone, and that you took it. You meant to repay "
          "every penny. Rowena wanted a word before the Supper, and you were dreading it.", [])],
        [("You had a reason to fear Rowena, but you were at the card table the whole time. Remind everyone.", []),
         ("Ask Clementine why Rowena wanted her workshop back.", [])],
    ],
    ask=["Who went into the Still Room after ten?", "Cordelia, what were you doing upstairs?",
         "Rufus, did anyone come past the porch?"],
)
B["clementine"] = dict(
    intro=["You make every candle the Hearth Circle burns: the tall white ones for the Moon Fair, the lantern candles "
           "in everyone’s colour, the little black ones children love. Your workshop is in the coach house behind "
           "Larkwell Hall, where your mother and her mother dipped candles before you.",
           "Rowena has always been good to you. At least, she used to be."],
    secret="This week Rowena told you she wants the coach house back. You begged her at supper tonight to change "
           "her mind, and she said she would “think about it until midnight”.",
    rounds=[
        [("Introduce yourself: candlemaker, coach-house workshop, proud of tonight’s lanterns.", []),
         ("Where were you? In the Great Hall at supper, then in the Parlour talking beeswax prices with Silas. "
          "After ten you went back to the Great Hall for the singing. At about a quarter past ten you went to the "
          "Cloakroom to look for your shawl, and you were back in the Great Hall by half past.",
          [("lie", "clementine", "Cloakroom", ["22:15"])]),
         ("What you saw: Rowena carrying a green glass towards the Still Room just after ten.", [
             ("heard",)])],
        [("Say you heard the peal from the Cloakroom: it went on forever.", []),
         ("Ask Marigold who else has a key to the Still Room.", [])],
        [("The notice to quit has been found. Admit Rowena meant to take back the coach house. You were heartbroken, "
          "not angry. You still hoped she would change her mind at midnight.", []),
         ("Point out that plenty of people here had a reason to want Rowena gone.", [])],
    ],
    ask=["Marigold, who else has a key to the Still Room?", "Isadora, why did Rowena keep looking at you all night?",
         "Silas, what was in the lantern fund book?"],
)
B["rufus"] = dict(
    intro=["You are the caretaker of Larkwell Hall and its bellringer. Thirty years of fixing the gutters, oiling the "
           "locks, chasing the jackdaws out of the chimneys and ringing the bell on every feast night.",
           "Rowena is the best employer you ever had. Tonight you are in charge of the door and the bell."],
    secret="For a year you have been leaving little poems on Mother Meridew’s doorstep, unsigned. Tonight you put one "
           "in her coat pocket in the Cloakroom. If anyone mentions poems, you go very red.",
    rounds=[
        [("Introduce yourself: caretaker and bellringer, keeper of every key except the poison cabinet’s.", []),
         ("Where were you? On the Porch all evening greeting guests and keeping the lanterns lit, then “up to the "
          "tower” for the practice peal.", []),
         ("What you saw: Percival arriving at half past nine, last as usual, with his ledger under his arm.", [
             ("saw", "rufus", "percival", "Porch", ["21:30"])])],
        [("The peal card is out. Tell everyone exactly what you saw: “I rang the practice peal from a quarter past "
          "ten until half past without a break. Cordelia was sitting in the Gallery, across the landing from the "
          "tower door, the whole time. I could see her through the open door, bent over the writing desk. She was "
          "still there when I came down at twenty to eleven.”", [
             ("saw", "rufus", "cordelia", "across the landing from the tower door", ["22:15", "22:30"])])],
        [("Somebody has found your poem. Admit it was yours, and that Mother Meridew is the finest woman in the "
          "valley.", []),
         ("Say the peal was the best you ever rang. Rowena would have been proud.", [])],
    ],
    ask=["Who went out into the herb garden tonight?", "Who came down the Gallery stair, and when?",
         "Isadora, have we met before?"],
)
B["isadora"] = dict(
    intro=["You are a mapmaker. You arrived in Morrowmere this autumn to draw the valley, or so you told everyone.",
           "The truth: you were born at Larkwell Hall and sent away as a baby. Rowena Heatherly is your mother. You "
           "wrote to her in the summer, and she asked you to come home and keep it secret until the Lantern "
           "Supper."],
    secret="Rowena is your mother, and tonight she meant to tell the whole Circle. You have no idea what else she "
           "planned to announce.",
    rounds=[
        [("Introduce yourself: mapmaker, newcomer, delighted by the village.", []),
         ("Where were you? “From ten o’clock I played cards in the Library with Silas Ashgrove and Mother Meridew "
          "until twenty to eleven. Silas didn’t leave the table once; he was losing and wanted his money back.”", [
             ("saw", "isadora", "silas", "Library", ["22:00", "22:15", "22:30"])]),
         ("Before that you were in the Great Hall, watching Rowena laugh with the choir.", [])],
        [("Ask Cordelia what she found in the Gallery desk.", []),
         ("If anyone asks why you really came to Morrowmere, say “for the maps” and change the subject.", [])],
        [("Rowena’s speech has been found. Tell the truth: she was your mother, and she was going to name you "
          "Lantern Keeper. You only had her back for six weeks.", [])],
    ],
    ask=["Who was the last person to see Rowena alive?", "Marigold, what grows in the herb garden?",
         "Who here is not who they say they are? (Careful.)"],
)
B["meridew"] = dict(
    intro=["You read tea leaves for anyone who brings you a cup, and you have read Rowena’s every Halloween for forty "
           "years.",
           "This morning her leaves showed a closed door and a candle. You did not like it."],
    secret="Someone has been leaving unsigned poems on your doorstep for a year, and you rather hope it is Rufus.",
    rounds=[
        [("Introduce yourself: tea-leaf reader, Rowena’s oldest friend outside the Circle.", []),
         ("Where were you? At cards in the Library from ten until twenty to eleven with Silas and Isadora. "
          "Neither of them left the table.", [
             ("saw", "meridew", "silas", "Library", ["22:00", "22:15", "22:30"]),
             ("saw", "meridew", "isadora", "Library", ["22:00", "22:15", "22:30"])])],
        [("Tell everyone about Rowena’s leaves this morning: a closed door and a candle.", []),
         ("From the Library’s French window you could see the herb garden, but the cards were good and you never "
          "looked up.", [])],
        [("You found a poem in your coat pocket tonight. Read a line aloud and watch who goes red.", [])],
    ],
    ask=["Who brought Rowena her cordial?", "Who has a reason to fear a closed door?",
         "Rufus, do you write poetry?"],
)
B["linnet"] = dict(
    intro=["You are Rowena’s goddaughter. She taught you every song you know and sat with you through every fever "
           "you ever had.",
           "Tonight you sang in the midnight choir in the Great Hall, and at a quarter to eleven you went to fetch "
           "her for the last rehearsal."],
    secret="Rowena told you last week that she had “found someone she lost long ago”, and made you promise not to "
           "tell. You think it might be Isadora.",
    rounds=[
        [("Introduce yourself: goddaughter, singer, the one who found Rowena.", []),
         ("Tell what you found: at a quarter to eleven, Rowena by the Still Room fire, very still, her green glass "
          "empty beside her. The garden door was open and the room was cold.", [
             ("at", "rowena", {"Still Room"}, ["22:45"])]),
         ("Where were you before? Singing in the Great Hall with the choir from ten o’clock.", [])],
        [("During the second verse, after a quarter past ten, you noticed a chair by the north door was empty, "
          "with a shawl over the back. You couldn’t say whose.", [("heard",)])],
        [("Tell everyone what Rowena told you: she had found someone she lost long ago.", [])],
    ],
    ask=["Whose chair was by the north door?", "Who was Rowena going to name tonight?",
         "Who left the singing early?"],
)
B["tamsin"] = dict(
    intro=["You are the cook of Larkwell Hall. You made tonight’s supper, you kept the cider coming through the "
           "serving hatch, and you hear every door in the house.",
           "You have never liked the Still Room: it smells of things that aren’t food."],
    secret="You have been feeding the Hall’s cat Rowena’s best cream for a year. The cat is enormous.",
    rounds=[
        [("Introduce yourself: cook, cider-maker, ears of the house.", []),
         ("What you saw: at ten Rowena poured her blackberry cordial into the green glass, tasted it and said "
          "“Perfect.” Then she took it to the Still Room.", [("saw", "tamsin", "rowena", "Kitchen", ["22:00"])]),
         ("What you heard: at a quarter past ten, Rowena’s footsteps overhead on the Lantern Room stair.",
          [("heard",)])],
        [("At about a quarter past ten Marigold went into the Pantry on her own, and you heard the honey shelf "
          "creak. She came back with her apron bulging.", [("heard",)])],
        [("From the Kitchen window you saw a lantern bobbing across the herb garden at about a quarter past ten, "
          "but the window was steamed up and you couldn’t see its colour.", [("heard",)])],
    ],
    ask=["Marigold, what was in your apron?", "Who walked across the garden?", "Who was hungry enough to steal cream?"],
)
B["percival"] = dict(
    intro=["You are the clerk of the Hearth Circle. You write the minutes, keep the membership roll and know who "
           "owes what to whom.",
           "You sing tenor in the midnight choir, rather loudly."],
    secret="You have noticed the lantern fund doesn’t add up, but you haven’t said anything because Silas lent you "
           "his best fountain pen.",
    rounds=[
        [("Introduce yourself: clerk, tenor, keeper of the minutes.", []),
         ("Where were you? You arrived at half past nine and sang in the Great Hall from ten until the choir broke "
          "up.", [])],
        [("You saw Cordelia go up the Gallery stair at about ten past ten, looking over her shoulder, and all "
          "through the second verse you could see her up there at the writing desk.", [
             ("saw", "percival", "cordelia", "Gallery", ["22:15"])]),
         ("Say the lantern fund has been “a little thin” since midsummer.", [])],
        [("Read from the minutes: at the last meeting Rowena said she would “settle the matter of the coach house "
          "before winter”.", [])],
    ],
    ask=["Silas, does the lantern fund add up?", "Cordelia, what did you take from the desk?",
         "Who here owes Rowena money?"],
)
B["ned"] = dict(
    intro=["You are the fiddler of the valley. Weddings, wakes, harvests: you have played them all.",
           "Tonight you played for the midnight choir in the Great Hall."],
    secret="You once played at Clementine’s cousin’s wedding and forgot the second half of the first dance. She has "
           "never forgiven you.",
    rounds=[
        [("Introduce yourself: fiddler, never misses a beat.", []),
         ("Where were you? Playing for the choir in the Great Hall from ten until a quarter to eleven.", [])],
        [("The peal: you had to play twice as loud to be heard over it, from a quarter past to half past ten. It "
          "never stopped.", [("heard",)])],
        [("You noticed green wax on the north door handle when you went out for air at a quarter to eleven. Mention "
          "it, if anyone asks about wax.", [("heard",)])],
    ],
    ask=["Who left by the north door?", "Who carried a green lantern?", "Who sang flat? (Someone did.)"],
)
B["bryony"] = dict(
    intro=["You are the lantern girl. Every lamp in Morrowmere is lit by you, and tonight you wrote every guest’s "
           "candle colour in the lantern ledger at the door.",
           "You are thirteen and you notice things."],
    secret="You have been practising being a detective all year with Inspector Drummond’s old notebook, which you "
           "found in the lost property box.",
    rounds=[
        [("Introduce yourself: lantern girl, keeper of the lantern ledger.", []),
         ("Where were you? Lighting the garden lanterns at half past nine, then handing out song sheets in the Great "
          "Hall until half past ten.", [])],
        [("At half past ten you went out to relight the garden lanterns. There were fresh footprints across the "
          "chamomile, from the Great Hall’s north door to the Still Room’s garden door and back, past the foxglove "
          "bed next to the Library window.", [("route", "Herb Garden")])],
        [("Remind everyone of the lantern ledger: you wrote down every colour at the door.", [])],
    ],
    ask=["Who came in by the north door?", "What colour was your candle?", "Who had mud on their hem?"],
)

# ---------------------------------------------------------------- the host
HOST_INTRO = [
    "Every Halloween, when the Moon Fair on Morrowmere green has packed away its last lantern, the Hearth Circle "
    "climbs the hill to Larkwell Hall for the Lantern Supper: soup and cider by the fire, a midnight carol, and "
    "the lighting of the great lantern in the tower.",
    "This year Rowena Heatherly, the Lantern Keeper of the Circle and the owner of the Hall, promised an "
    "announcement at midnight. She never made it. At a quarter to eleven her goddaughter found her in the Still "
    "Room, a green glass of blackberry cordial empty beside her.",
    "Inspector Hollis Drummond has locked the doors. Nobody leaves Larkwell Hall until the Inspector knows who "
    "poisoned Rowena, and the Inspector is counting on you.",
]
ROUND_SCRIPTS = {
    1: ["Read aloud: “Ladies and gentlemen, I am sorry to tell you that Rowena Heatherly is dead. Someone put "
        "foxglove in her cordial tonight. Every one of you was in this house. Before we go any further, I want to "
        "know who you are, and where you were.”",
        "Read evidence cards 1–4 aloud, one by one. Then put them on the table face up, with the plan of Larkwell "
        "Hall beside them, so anyone can read them again.",
        "Everyone reads the Round 1 page of their booklet. Then introductions: the guest on the host’s left starts "
        "and it goes round the circle (or follow the order of the roles in the casting table). Each guest says who "
        "they are and where they were. The host keeps time: about a minute each.",
        "Then mingle: ask questions, compare stories, look at the cards. Around 30–40 minutes."],
    2: ["Ring a bell, clink a glass or bang a pan. Read aloud: “The bell. I keep thinking about the bell. It rang "
        "for a quarter of an hour while Rowena was upstairs. Some of you have been less than honest with me. Cards "
        "on the table, please, and new ones.”",
        "Read evidence cards 5–8 aloud, one by one. Then put them on the table face up, next to cards 1–4.",
        "Everyone reads the Round 2 page of their booklet. Secrets start to come out. Mingle and question for "
        "30–40 minutes."],
    3: ["Read aloud: “I have one more thing to show you, and two papers from Rowena’s desk. After this, I want "
        "your answer.”",
        "Read evidence cards 9–11 aloud, one by one. Then put them on the table face up with the others.",
        "Everyone reads the Round 3 page of their booklet. Last chance to question each other: about 20–30 "
        "minutes. Then hand out the accusation sheets."],
}
SOLUTION_INTRO = "The killer is Clementine Reed, the candlemaker."
SOLUTION = [
    ("Why", "Rowena meant to take back the coach house where three generations of Reed women had made candles. The "
            "notice to quit was written and waiting on her desk with a note: “Sign at midnight.” Clementine begged "
            "her at supper; Rowena said she would think about it until midnight. Clementine decided not to wait."),
    ("How", "Just after a quarter past ten, while the choir sang with their backs to the north door and the peal "
            "drowned every footstep, Clementine slipped out of the Great Hall into the herb garden. She tore a few "
            "foxglove leaves from the bed by the Library window, crossed the chamomile to the Still Room’s garden "
            "door and found the green glass alone on the table: Rowena was upstairs in the Lantern Room. She crushed "
            "the leaves into the cordial and went back the way she came. By half past ten she was in her chair by "
            "the north door again, a little mud on her hem."),
    ("The mistake", "As she bent over the glass, a drip of green wax fell from her own lantern onto the rim."),
    ("The lie", "She said she spent the peal in the Cloakroom looking for her shawl. Her shawl was over the back of "
                "her chair by the north door the whole time: Linnet saw an empty chair with a shawl on it."),
]
DEDUCTION = [
    ("Card 1, The Green Glass", "The poison went in while Rowena was upstairs: after a quarter past ten and before "
     "half past. The poisoner was in the Still Room then."),
    ("Silas and Isadora (Round 1)", "They played cards in the Library with Mother Meridew from ten until twenty to "
     "eleven, and each says the other never left the table. Nobody in this game lies about where someone else was "
     "(house rule 5), so both are cleared."),
    ("Card 3, The Choir and the Kitchen", "Linnet, Percival, Ned, Bryony, Tamsin and Mother Meridew were all in plain "
     "sight. The six extra guests are cleared in Round 1."),
    ("Rufus and Cordelia (Round 2)", "Rufus rang the peal from a quarter past to half past without a break, and saw "
     "Cordelia across the landing in the Gallery the whole time; Cordelia saw him at the rope. Each clears the "
     "other. That leaves Marigold and Clementine."),
    ("Card 9 with Card 2", "The wax on the rim is green. The lantern ledger shows three green candles: Cordelia, Silas "
     "and Clementine. Marigold’s candle was amber. Cordelia and Silas are already cleared, so the poisoner is "
     "Clementine Reed."),
]
RED_HERRINGS = [
    ("Marigold’s key", "The poison cabinet was never opened (card 6). Marigold’s trip to the Pantry was about a jar "
     "of honey."),
    ("Silas and the lantern fund", "He took the money, and Rowena knew, but he was at the card table all through the "
     "peal."),
    ("Cordelia and the will", "She tore the will in a temper in the Gallery, in full view of Rufus in the tower."),
    ("Isadora", "Rowena’s daughter and her chosen successor: she had everything to gain from Rowena alive."),
]
EPILOGUE = ("Inspector Drummond took Clementine down the hill before midnight. The Hearth Circle lit the great "
            "lantern anyway, at one in the morning, and Isadora Quince lit it.")

# ---------------------------------------------------------------- party extras
POTIONS = [
    ("Bramble Cauldron Punch", "Blackberry, apple and a cinnamon stick, served warm from a pot.",
     "Spellbound: add a splash of dark rum to each cup.", "Moonless: as it is, with a twist of orange."),
    ("Hob Hill Cider Fizz", "Cloudy apple cider over ice with ginger and a slice of pear.",
     "Spellbound: use hard cider.", "Moonless: sparkling apple juice."),
    ("Moon-Milk Nightcap", "Warm milk with honey, vanilla and a pinch of nutmeg.",
     "Spellbound: a spoon of spiced rum or brandy.", "Moonless: perfect as it is (oat milk works too)."),
    ("Ember Ginger Spritz", "Ginger beer, lime and a few dark cherries, very cold.",
     "Spellbound: a measure of gin.", "Moonless: as it is, with extra lime."),
]
POTION_NOTE = ("Decorate with lemon balm, mint or rosemary. Never use foxglove or any garden plant you are not sure "
               "of: in this story it is a poison, and in real life it is one too.")
AWARDS = [("Best Detective", "for seeing through the candle smoke"),
          ("Best Costume", "for dressing the part from hat to hem"),
          ("Best Performance", "for staying in character all night"),
          ("Most Suspicious", "for looking guilty without even trying")]
HOUSE_RULES = [
    "Everyone is a suspect. No booklet says who did it, not even the killer’s own. Read your booklet as your "
    "character’s memory: tell what it tells you, keep your secret until your booklet says to share it.",
    "You may not show anyone your booklet. You may read lines aloud.",
    "Your character only knows what is in your booklet. If someone asks you something you don’t know, say so, or "
    "invent something harmless that does not change where anyone was.",
    "The evidence cards are true. So is the plan of Larkwell Hall.",
    "Nobody lies about where other people were. People can be wrong about themselves.",
]
