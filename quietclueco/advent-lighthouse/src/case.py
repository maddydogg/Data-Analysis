"""The Keeper of Candleholm — case data for advent calendar B (the lighthouse).

Everything the generator, the checker and the renderer need lives here: the chart of the Sound
(the island, the landings, the villages, the range of the light), the tides and the almanac, the
21 daily clues (windows 3-23) with their alternative readings, the keeper's journal and the story.

Chart coordinates are nautical miles from Candleholm Light: x to the east, y to the north.
"""
import math

TITLE = "The Keeper of Candleholm"
TITLE_PLAIN = "The Keeper of Candleholm"
SUBTITLE = "A Lighthouse Murder Mystery Advent Calendar"
BRAND = "QuietClueCo"
TAGLINE = "24 days · 2,400 travellers · 1 killer"
PLAYERS = "1–4 players"
PLAYTIME = "10–25 minutes a day"
SEED = 20261223
N_ROWS = 2400
ISLAND = "Candleholm"
LIGHT = "Candleholm Light"
SOUND = "the Sound of Candleholm"
PORT = "Port Tolland"
OUTER = "Inishvarra"
LOCH = "Loch Tarrisk"
SKERRIES = "the Dulse Reef"
REGISTER = "The Sound Book"

# ---------------------------------------------------------------- the boats
# The Sound Book prints the first word only.
BOATS = ["Mail", "Fishing", "Tender", "Pilot"]
BOAT_NAMES = {"Mail": "the Mail Boat", "Fishing": "a fishing boat", "Tender": "the Lights Tender",
              "Pilot": "the Pilot Cutter"}
BOAT_WEIGHTS = [30, 25, 21, 24]
INNER = {"Mail", "Fishing"}              # the Inner Passage, between Candleholm and the Dulse Reef
INNER_WIDE = {"Mail", "Fishing", "Pilot"}  # the chart notes the Pilot Cutter may use it at high water

# ---------------------------------------------------------------- the chart
GANNET_HEAD = (8.0, 11.0)
SELKIE_NESS = (6.9, -10.2)
NARROWS = (16.0, 13.0)
RANGE = 12.0                              # Candleholm Light is visible for 12 nautical miles
SKERRY_ROCKS = [(-3.6, 0.9), (-3.1, 0.2), (-3.9, -0.4), (-3.3, -1.1), (-4.2, 0.4)]

# landing number -> (name, x, y, shore). Shores: "isle" (Candleholm), "outer" (Inishvarra),
# "north" (mainland north of the loch), "loch" (Loch Tarrisk), "south" (mainland south of the loch)
LANDINGS = {
    1: ("East Landing, Candleholm", 0.45, 0.05, "isle"),
    2: ("Boat Cove, Candleholm", -0.3, -0.45, "isle"),
    3: ("Rathvarra Slip", -7.2, -5.8, "outer"),
    4: ("Kilvarra Quay", -8.2, 4.1, "outer"),
    5: ("Ballyvarra Pier", -7.6, 11.0, "outer"),
    6: ("Ardvane Pier", 10.9, 19.3, "north"),
    7: ("Kirkwhinnie Quay", 10.1, 15.2, "north"),
    8: ("Gannet Head Steps", 8.3, 11.4, "north"),
    9: ("Lochmouth Slip", 9.9, 9.6, "loch"),
    10: ("Achnabrae Jetty", 12.4, 11.7, "loch"),
    11: ("Inverlash Pier", 13.4, 10.6, "loch"),
    12: ("Narrows Slip", 16.1, 12.4, "loch"),
    13: ("Torrandhu Jetty", 18.3, 15.2, "loch"),
    14: ("Ardlarich Slip", 20.4, 15.1, "loch"),
    15: ("Ferrach Pier", 22.4, 14.9, "loch"),
    16: ("Balnacrae Pier", 24.2, 13.6, "loch"),
    17: ("Dunloch Slip", 25.3, 11.2, "loch"),
    18: ("Lochhead Quay", 25.4, 8.8, "loch"),
    19: ("Bayle Strand", 9.7, 7.4, "south"),
    20: ("Port Tolland Quay", 9.2, 2.2, "south"),
    21: ("Carrowby Pier", 8.4, -3.0, "south"),
    22: ("Lannagh Slip", 7.7, -6.8, "south"),
    23: ("Selkie Steps", 7.0, -10.0, "south"),
    24: ("Polbrae Harbour", 7.4, -14.0, "south"),
}
LOCH_ORDER = [9, 10, 11, 12, 13, 14, 15, 16, 17, 18]      # from the mouth up to the head of the loch
NARROWS_SLIP = 12
LANDING_WEIGHTS = {1: 4, 2: 2, 3: 5, 4: 6, 5: 5, 6: 5, 7: 5, 8: 2, 9: 5, 10: 5, 11: 5, 12: 5, 13: 2, 14: 2,
                   15: 2, 16: 2, 17: 2, 18: 2, 19: 4, 20: 12, 21: 5, 22: 5, 23: 2, 24: 5}
PARCEL_SHEDS = [4, 13, 15, 16, 20]       # Christmas parcels are left only in these sheds (waybill)
POST_BOXES = [1, 9, 19, 23]              # letters only (the trap: the waybill lists them too)

MAINLAND = [(11.6, 23.0), (11.0, 20.5), (10.6, 19.3), (10.1, 17.0), (9.7, 15.2), (8.8, 12.6), (7.6, 11.0),
            (8.6, 10.2), (9.0, 9.0), (9.5, 7.6), (9.3, 5.0), (8.9, 2.2), (8.6, -0.5), (8.1, -3.0), (7.7, -5.4),
            (7.4, -6.8), (7.0, -8.8), (6.5, -10.2), (7.0, -11.0), (7.1, -14.0), (7.6, -17.5), (31.0, -17.5), (31.0, 23.0)]
LOCH_PATH = [(8.6, 9.5), (10.2, 10.2), (11.6, 10.9), (13.0, 11.3), (14.6, 12.2), (16.0, 13.0), (17.4, 14.3),
             (19.4, 14.9), (21.6, 14.6), (23.4, 13.6), (24.7, 12.0), (25.2, 10.0), (25.1, 8.4)]
INISHVARRA = [(-11.5, 15.6), (-9.0, 13.6), (-5.6, 12.8), (-3.7, 11.9), (-3.9, 10.6), (-7.0, 10.9), (-8.0, 8.5),
              (-7.8, 4.1), (-7.1, 0.0), (-6.9, -5.8), (-7.6, -9.0), (-9.5, -11.2), (-12.0, -10.4), (-13.6, -4.0),
              (-13.2, 4.0), (-12.6, 12.0)]
VIEW = (-14.5, -17.0, 27.5, 22.0)          # x0, y0, x1, y1 of the whole chart

def landing_name(n):
    return LANDINGS[n][0]

def above_narrows(n, inclusive=False):
    """Higher up Loch Tarrisk than the Narrows, following the loch from its mouth."""
    if n not in LOCH_ORDER:
        return False
    i, k = LOCH_ORDER.index(n), LOCH_ORDER.index(NARROWS_SLIP)
    return i >= k if inclusive else i > k

def north_of_narrows(n, loch_only=True):
    """Read on the chart: further north (higher up the page) than the Narrows."""
    if loch_only and n not in LOCH_ORDER:
        return False
    return LANDINGS[n][2] > NARROWS[1]

# home village -> (x, y, kind). kind: "coast" (mainland open coast), "loch" (on the shore of Loch
# Tarrisk), "inland" (mainland, away from the water), "outer" (on Inishvarra)
VILLAGES = {
    "Ardvane": (11.6, 19.4, "coast"),
    "Kirkwhinnie": (10.9, 15.0, "coast"),
    "Achnabrae": (12.6, 12.9, "loch"),
    "Inverlash": (13.5, 9.6, "loch"),
    "Torrandhu": (18.6, 16.2, "loch"),
    "Balnacrae": (24.8, 14.8, "loch"),
    "Strathcorrie": (16.5, 3.0, "inland"),
    "Bayle": (10.0, 7.6, "coast"),
    "Port Tolland": (9.6, 2.0, "coast"),
    "Carrowby": (9.0, -3.2, "coast"),
    "Lannagh": (8.3, -7.0, "coast"),
    "Polbrae": (8.0, -14.3, "coast"),
    "Kilvarra": (-8.8, 4.4, "outer"),
    "Rathvarra": (-7.8, -5.8, "outer"),
    "Ballyvarra": (-10.0, 12.4, "outer"),
    "Skellan": (-4.2, math.sqrt(RANGE ** 2 - 4.2 ** 2), "outer"),   # its dot sits right on the range circle
}
VILLAGE_WEIGHTS = {"Port Tolland": 8, "Carrowby": 4, "Lannagh": 3, "Bayle": 7, "Kilvarra": 4, "Rathvarra": 3,
                   "Ballyvarra": 8, "Skellan": 3, "Ardvane": 8, "Kirkwhinnie": 9, "Achnabrae": 8,
                   "Inverlash": 8, "Torrandhu": 7, "Balnacrae": 8, "Strathcorrie": 7, "Polbrae": 8}
HOMES = list(VILLAGES)

def dist_light(v):
    x, y, _ = VILLAGES[v]
    return math.hypot(x, y)

def in_range(v, on_line=False, limit=None):
    d = dist_light(v)
    if limit is not None:
        return d < limit
    return d <= RANGE + 0.05 if on_line else d < RANGE - 0.05

def between_heads(v, how="coast"):
    """Lives on the mainland between Gannet Head and Selkie Ness.
    coast: open-coast villages south of Gannet Head and north of Selkie (official);
    route: walking the shore from one head to the other, which goes all round Loch Tarrisk;
    line: close to the straight line between the two heads on the chart (within 2.5 miles);
    band: any mainland village between the two heads' latitudes, inland ones included."""
    x, y, kind = VILLAGES[v]
    inside = SELKIE_NESS[1] < y < GANNET_HEAD[1]
    if how == "coast":
        return kind == "coast" and inside
    if how == "route":
        return (kind == "coast" and inside) or kind == "loch"
    if how == "band":
        return kind != "outer" and inside
    if how == "line":
        (x1, y1), (x2, y2) = GANNET_HEAD, SELKIE_NESS
        t = max(0.0, min(1.0, ((x - x1) * (x2 - x1) + (y - y1) * (y2 - y1)) / ((x2 - x1) ** 2 + (y2 - y1) ** 2)))
        px, py = x1 + t * (x2 - x1), y1 + t * (y2 - y1)
        return kind != "outer" and math.hypot(x - px, y - py) <= 2.5 and 0 < t < 1
    raise ValueError(how)

# ---------------------------------------------------------------- time, tides and the almanac
DAYS = list(range(1, 24))                 # the Sound Book runs from 1 to 23 December
FIRST_BOAT, LAST_BOAT = "06:30", "18:30"
def tmin(s):
    h, m = s.split(":"); return int(h) * 60 + int(m)
def tstr(m):
    return f"{m // 60:02d}:{m % 60:02d}"
def ampm(m):
    """15:46 -> 3.46 p.m. (the almanac's style)."""
    h, mm = m // 60, m % 60
    return f"{(h - 1) % 12 + 1}.{mm:02d} {'a.m.' if h < 12 else 'p.m.'}"

HW_FIRST = tmin("04:10")                  # first high water of December (1 December, 04:10)
TIDE_PERIOD = 745                         # 12 h 25 min
HALF = 372                                # high water to low water: 6 h 12 min
def tide_events(day):
    """[(minute of the day, 'HW' or 'LW'), ...] for one December day, in order."""
    out = []
    for k in range(-4, 60):
        hw = HW_FIRST + k * TIDE_PERIOD
        for t, kind in ((hw, "HW"), (hw + HALF, "LW")):
            d, m = divmod(t, 1440)
            if d + 1 == day:
                out.append((m, kind))
    return sorted(out)

def rising(day, minute, inclusive=False, slack=0):
    """The tide is making (rising): after a low water and before the next high water."""
    for k in range(-4, 60):
        lw = HW_FIRST + k * TIDE_PERIOD - (TIDE_PERIOD - HALF)
        hw = HW_FIRST + k * TIDE_PERIOD
        t = (day - 1) * 1440 + minute
        a, b = lw - slack, hw + slack
        if (a <= t <= b) if inclusive else (a < t < b):
            return True
    return False

def near_high_water(day, minute, within=60):
    t = (day - 1) * 1440 + minute
    return any(abs(t - (HW_FIRST + k * TIDE_PERIOD)) <= within for k in range(-4, 60))

# Lighting-up time (sunset): the keeper lights the lamp then. Minutes after midnight, 1-24 December.
LIGHTING = {d: tmin(t) for d, t in zip(range(1, 25), [
    "15:46", "15:45", "15:44", "15:43", "15:42", "15:41", "15:40", "15:40", "15:39", "15:39", "15:38", "15:38",
    "15:38", "15:38", "15:38", "15:38", "15:38", "15:39", "15:39", "15:40", "15:40", "15:41", "15:41", "15:42"])}
SUNRISE = {d: tmin(t) for d, t in zip(range(1, 25), [
    "08:24", "08:26", "08:27", "08:29", "08:30", "08:32", "08:33", "08:34", "08:35", "08:37", "08:38", "08:39",
    "08:40", "08:40", "08:41", "08:42", "08:43", "08:43", "08:44", "08:44", "08:45", "08:45", "08:46", "08:46"])}
WEATHER = {1: ("Fair, light frost", "SW 3"), 2: ("Fair, cold and bright", "W 3"), 3: ("Cloudy, showers of sleet", "NW 4"),
           4: ("Fair", "N 3"), 5: ("Overcast, mild", "SW 4"), 6: ("Rain at times", "SW 5"), 7: ("Fair, hard frost", "NE 2")}
def before_lighting(day, minute, inclusive=False, twelve_hour=False):
    lt = LIGHTING[day] - (720 if twelve_hour else 0)
    return minute <= lt if inclusive else minute < lt

# ---------------------------------------------------------------- tallies
BRASS, COPPER, TIN = (1, 800), (801, 1600), (1601, 2400)
def digits(n):
    return f"{n:04d}"

# ---------------------------------------------------------------- Morse (light signals)
MORSE = {"A": "·–", "B": "–···", "C": "–·–·", "D": "–··", "E": "·", "F": "··–·", "G": "––·", "H": "····",
         "I": "··", "J": "·–––", "K": "–·–", "L": "·–··", "M": "––", "N": "–·", "O": "–––", "P": "·––·",
         "Q": "––·–", "R": "·–·", "S": "···", "T": "–", "U": "··–", "V": "···–", "W": "·––", "X": "–··–",
         "Y": "–·––", "Z": "––··"}
DASH_FIRST = sorted(k for k, v in MORSE.items() if v.startswith("–"))

# ---------------------------------------------------------------- names
FIRST = """Ada Agnes Ailie Alastair Albert Alec Alice Allan Amos Andrew Angus Annie Archie Arthur Audrey
Beatrice Bella Bernard Bertie Bessie Brodie Callum Catriona Cecil Christina Clara Colin Connor Cora Cormac
Cyril Daisy Dermot Dolina Donald Dora Dougal Duncan Edith Edna Effie Eileen Elsie Enid Eric Ernest Euan
Evelyn Fergus Fiona Finlay Flora Frances Frank Freya Gavin George Gertrude Gilbert Gordon Grace Greta Gregor
Gwen Hamish Harold Harriet Harry Hector Helen Henry Hugh Ian Iona Irene Iris Isobel Ivor Jean Jessie
Joan Johan Judith Kenneth Kirsty Lachlan Lena Leonard Lewis Lilias Lily Lorna Louisa Mabel Magnus Maisie
Malcolm Marion Martha Mary Maureen Mhairi Morag Murdo Myra Nancy Neil Nora Norman Olive Oscar Patrick Peggy
Phyllis Rachel Ranald Rhoda Robert Ronald Rory Rose Ruby Ruth Sadie Samuel Sheila Sorley Stanley Stella
Stewart Thomas Torquil Una Vera Violet Walter Wilma Aileen Bridget Cathal Davina Eilidh Ewan Fenella Fintan
Gemma Grant Ishbel Kenna Kirstin Lorne Marsali Niall Oonagh Peigi Ross Seonag Teresa Wallace Yvonne Zelda
Bryce Corrie Dunstan Elspet Fraser Gillian Innes Keir Moira Nessie Orla Quentin Roisin Shona Tavish
Vina Warren Xander Yolanda Zander
Abigail Adair Alistair Anabel Annabel Arran Barbara Blair Brendan Calum Carla Clarissa Craig Damian Darragh Dorcas
Douglas Dylan Eamon Edgar Elinor Emmet Evan Fabian Faye Felix Garth Gideon Glenn Hannah Imogen Isaac Jacob James
Janet Jasper Karen Kester Laura Leonie Lucas Lydia Marcus Mairi Martin Maxwell Meredith Michael Miriam Molly
Nathan Nicol Noreen Owen Paula Pearl Philip Rhona Robin Roland Rowan Sarah Seamus Sean Selina Simon Steven
Susan Tara Thea Tobin Valerie Vivian Wendy Alana Anson Arlo Basil Bram Carys Cerys Dara Dean Elias
Eliza Ellen Esmond Fergal Gwyneth Hollie Ingrid Jarvis Kieran Lorcan Magda Marla Morgan Nadia Odile Pascal Petra
Quinn Reuben Sabina Saul Tavis Tristan Ulric Vernon Wilfred""".split()
LAST = """Abernethy Aitken Allardyce Anstruther Baird Balfour Bannerman Barclay Beattie Birrell Blackwood Boyd
Brodie Buchan Burnett Cairns Calder Carmichael Chalmers Clunie Cochrane Colquhoun Craigie Crichton Cruickshank
Cumming Dalgleish Dalziel Dewar Dickson Doig Dunbar Duthie Elder Elphinstone Erskine Ewing Farquhar Fergusson
Fettes Finlayson Fleming Forbes Forsyth Fullarton Gemmell Gilchrist Gillespie Gourlay Graham Grieve Guthrie
Haldane Halliday Hardie Henderson Hepburn Hislop Hogg Hunter Inglis Irvine Jamieson Johnstone Kerr Kinnaird
Kirkland Laidlaw Lamont Lauder Leckie Lennox Leslie Lindsay Livingstone Lockhart Lorimer Lumsden Lyall MacAskill
MacBride MacInnes MacIver MacNab MacPhail MacRae Maitland Malloch Maxwell McCulloch McDiarmid McGillivray
McKenzie McLaren Meikle Menzies Moffat Moncrieff Muir Munro Murchison Napier Nairn Nesbitt Niven Ogilvie
Oliphant Orr Paterson Peden Pirie Pringle Purdie Rae Ramsay Rankin Riddell Ritchie Rollo Russell Rutherford
Sandeman Scobie Semple Shand Sinclair Skene Smeaton Soutar Spence Stirling Strachan Sutherland Swanson Tait
Thomson Todd Turnbull Urquhart Veitch Waddell Wardlaw Watt Weir Whyte Wishart Yeaman Young Brennan Callaghan
Carey Cassidy Connolly Costello Cullen Curran Daly Delaney Devlin Doherty Dolan Donnelly Duggan Egan Fallon
Farrell Feeney Finnegan Flanagan Flynn Gallagher Geraghty Hanlon Hennessy Hogan Keane Kearney Kehoe Kinsella
Lalor Lynch Madigan Mahon Moran Mulcahy Mulligan Nolan Nugent Phelan Quigley Quinlan Rafferty Regan Rooney
Scanlon Sheridan Tierney Toomey Whelan Ackroyd Barraclough Bottomley Charnock Dawtry Eccles Fothergill Haworth
Ingham Kitchin Lumb Metcalfe Pickles Rawcliffe Sowerby Uttley Whitaker Wolstenholme Agnew Bonar Corsar Dryburgh
Eadie Galbraith Jardine Keddie Loudon Mowat Petrie Quarrier Sangster Tosh Wylie Yule Bisset Cowie Dougan
Fyvie Gunn Kemp Lowrie Mearns Rennison Stobie Troup
Bain Bremner Buchanan Cargill Carnegie Coutts Crombie Cuthbert Dargie Dempster Donaldson Dunlop Fairbairn Fenton
Gauld Geddes Goudie Gowans Haig Hamilton Harkness Herron Imrie Jolly Kidd Kinloch Laing Lamb Logan Lyon Mackie
Mathieson Melville Milne Mitchell Morrison Murdoch Nicoll Ogg Pollock Proudfoot Rattray Reid Robb Ross Rowand
Scott Shearer Sim Simpson Small Stark Steel Storrie Taggart Thain Tough Tully Wedderburn Will Wood Wotherspoon
Brogan Canning Corrigan Coyle Crowley Dempsey Deveney Dunne Fagan Foley Gormley Hegarty Joyce Kavanagh Kenny Lavery
Loughlin Maguire McCann McGovern Mooney Mulhern Murtagh Noonan Rourke Slattery Treacy Tuohy Walsh Bancroft
Belcher Birtwistle Brierley Calvert Clegg Cockburn Dobson Dodgson Eastwood Garside Gaukroger Hardcastle Holroyd
Kershaw Lister Midgley Moxon Normanton Oddy Pogson Ramsden Robshaw Sugden Tordoff Varley Wadsworth Wilkinson Yardley
Bonnar Corbett Dalgarno Gorrie Kynoch Lennie Mavor Moncur Nimmo Orrock Pitcairn Ruthven Stoddart Torrance Yuill
Bryden Cowan Darroch Gordon Kilgour Marr Morton Norrie Proctor Rodger Smart Tolmie Wark
Doran Kirwan Bowman Dalton Tucker Dawson Gibson Coburn Kidston Machin Bulmer Burns Tolan Dunsire Cowie
Buist Comrie Gowdie Kemlo Dornan Tonner Muldoon Bain Dunn Kirk Mair Nicholson Thorburn Tennant Carson""".split()
FIRST = sorted(set(FIRST))
LAST = sorted(set(LAST))

# ---------------------------------------------------------------- the killer and the people
KILLER = dict(tally=1478, first="Jonas", last="Garvock", home="Carrowby", boat="Mail", landing=15,
              day=2, time=tmin("13:38"))
VICTIM = "Ezra Tullock"
SUPERINTENDENT = "Superintendent Alma Treleaven"
SKIPPER = "Bede Halloran"            # skipper of the Mail Boat
TALLYMAN = "Gil Corkhill"            # keeps the Sound Book at the Harbour Trust office in Port Tolland
POSTMISTRESS = "Mrs Hester Breck"
FISHERMEN = "the Drummock brothers"
PILOT = "Ottilie Marsden"            # pilot of the Pilot Cutter
COASTGUARD = "Dougie Strang"         # the coastguard lookout on Gannet Head
BAKER = "Nan Fairgrieve"
CAT = "Bosun"
MARK = "a knitted cap the red of a channel buoy, with a white bobble"
PEOPLE = [VICTIM, "Alma Treleaven", SKIPPER, TALLYMAN, "Hester Breck", "Drummock", PILOT, BAKER, COASTGUARD]

# ---------------------------------------------------------------- clue helpers
VOWELS = set("AEIOU")
def vowels(s, y=False):
    return sum(ch in (VOWELS | {"Y"} if y else VOWELS) for ch in s.upper())
def repeat_letter(s):
    s = s.upper(); return len(set(s)) < len(s)
def double_letter(s):
    s = s.upper(); return any(a == b for a, b in zip(s, s[1:]))

# ---------------------------------------------------------------- the 21 daily clues (windows 3-23)
# Each clue: day, group, window (title), note (today's question), fact (meaning: solution and
# level-3 hint), pred(record), alts: reasonable readings that must keep the killer and the same
# single answer, far: far-fetched readings that would drop the killer (they must leave nobody, so
# the slip shows). `word` tags the spatial or time words a reading is about (for the report).
# record = dict(tally, first, last, home, boat, landing, day, time)
CLUES = [
    dict(day=3, group="when", window="A Tally Already", word="already / today",
         note="By 3 December the red cap already had his tally. What does that tell you about his line in the "
              "Sound Book?",
         fact="He had his tally by the evening of 3 December, so his first crossing was on 1, 2 or 3 December.",
         pred=lambda r: r["day"] <= 3,
         alts=[("‘already’ read as ‘before today’: 1 or 2 December only", lambda r: r["day"] <= 2)],
         far=[]),
    dict(day=4, group="boat", window="The Inner Passage", word="through / between",
         note="Which boat brought him over on his first crossing?",
         fact="He came through the Inner Passage, between Candleholm and the Dulse Reef. Only the Mail Boat "
              "and the fishing boats use it, so his boat was Mail or Fishing.",
         pred=lambda r: r["boat"] in INNER,
         alts=[("the Pilot Cutter counted too (the chart says it may use the Inner Passage at high water)",
                lambda r: r["boat"] in INNER_WIDE)],
         far=[("only the fishing boats (the Mail Boat overlooked)", lambda r: r["boat"] == "Fishing")]),
    dict(day=5, group="landing", window="Up the Loch", word="higher up / above",
         note="Where was he put ashore on his first crossing?",
         fact="He was put ashore higher up Loch Tarrisk than the Narrows: following the loch from its mouth, "
              "one of the landings past the Narrows Slip (13 to 18).",
         pred=lambda r: above_narrows(r["landing"]),
         alts=[("the Narrows Slip itself counted too", lambda r: above_narrows(r["landing"], inclusive=True)),
               ("‘higher up’ read on the chart: loch landings drawn further north than the Narrows",
                lambda r: north_of_narrows(r["landing"])),
               ("‘higher up’ read as ‘further north on the chart’, anywhere at all",
                lambda r: north_of_narrows(r["landing"], loch_only=False))],
         far=[("only the very next landing above the Narrows (Torrandhu Jetty)", lambda r: r["landing"] == 13)]),
    dict(day=6, group="home", window="Within Sight of the Light", word="near / within sight",
         note="Where does he live?",
         fact="He lives within sight of the light: his village is inside the dashed circle on the chart, the 12 "
              "miles that Candleholm Light can be seen (Port Tolland, Carrowby, Lannagh, Kilvarra or Rathvarra).",
         pred=lambda r: in_range(r["home"]),
         alts=[("a village sitting right on the circle counted too", lambda r: in_range(r["home"], on_line=True))],
         far=[("‘near’ read as within half the range (6 miles)", lambda r: in_range(r["home"], limit=6.0))]),
    dict(day=7, group="name", window="A Lamp in the Boathouse",
         note="What did the hand lamp tell Ezra about his surname?",
         fact="The first letter of his surname begins with a long flash (a dash) in Morse: B, C, D, G, K, M, N, O, "
              "Q, T, X, Y or Z.",
         pred=lambda r: r["last"][0].upper() in DASH_FIRST, alts=[], far=[]),
    dict(day=8, group="name", window="The Parcel Slip",
         note="What did Mrs Breck notice about his first name?",
         fact="His first name contains the letter A.",
         pred=lambda r: "A" in r["first"].upper(), alts=[], far=[]),
    dict(day=9, group="tally", window="The Tally Boards",
         note="What does the tally board tell you about his tally number?",
         fact="He hung his tally on the left-hand board, which takes the even numbers. His tally number is even.",
         pred=lambda r: r["tally"] % 2 == 0, alts=[], far=[]),
    dict(day=10, group="when", window="On the Flood", word="rising / before high water",
         note="What was the tide doing on his first crossing?",
         fact="The tide was making (rising): his first crossing was after a low water and before the next high "
              "water on that day’s tide table.",
         pred=lambda r: rising(r["day"], r["time"]),
         alts=[("the exact minutes of low and high water counted too", lambda r: rising(r["day"], r["time"], inclusive=True)),
               ("a quarter of an hour of slack water at each end counted too",
                lambda r: rising(r["day"], r["time"], inclusive=True, slack=15))],
         far=[("‘making’ read as ‘at high water’: within an hour of high water",
               lambda r: near_high_water(r["day"], r["time"]))]),
    dict(day=11, group="home", window="Between the Heads", word="between",
         note="Where does he live?",
         fact="He lives on the mainland coast between Gannet Head and Selkie Ness: Bayle, Port Tolland, Carrowby "
              "or Lannagh.",
         pred=lambda r: between_heads(r["home"]),
         alts=[("‘between’ read along the shore, which runs all the way round Loch Tarrisk",
                lambda r: between_heads(r["home"], "route")),
               ("‘between’ read on the chart: close to the straight line from one head to the other",
                lambda r: between_heads(r["home"], "line")),
               ("‘between’ read on the chart: any mainland village between the two heads, inland too",
                lambda r: between_heads(r["home"], "band"))],
         far=[]),
    dict(day=12, group="landing", window="The Christmas Waybill",
         note="Where did he collect his parcel?",
         fact="He collected a Christmas parcel at the landing where he came ashore. Parcels are left only in the "
              "parcel sheds at landings 4, 13, 15, 16 and 20, so his landing is one of those.",
         pred=lambda r: r["landing"] in PARCEL_SHEDS,
         alts=[("any landing on the waybill, the letter boxes included",
                lambda r: r["landing"] in PARCEL_SHEDS + POST_BOXES)],
         far=[]),
    dict(day=13, group="name", window="A Card on the Nail",
         note="What does the Christmas card tell you about his first name?",
         fact="His first name has exactly five letters.",
         pred=lambda r: len(r["first"]) == 5, alts=[], far=[]),
    dict(day=14, group="tally", window="Gil’s Lucky Tallies",
         note="What does Gil’s game tell you about his tally number?",
         fact="The four digits of his tally number add up to more than 15 (16 or more).",
         pred=lambda r: sum(map(int, digits(r["tally"]))) > 15,
         alts=[("“more than fifteen” read as “fifteen or more”", lambda r: sum(map(int, digits(r["tally"]))) >= 15)],
         far=[]),
    dict(day=15, group="name", window="The Pilot’s Log",
         note="What does the pilot’s log tell you about his name?",
         fact="His first name and his surname end with different letters.",
         pred=lambda r: r["first"][-1].upper() != r["last"][-1].upper(), alts=[], far=[]),
    dict(day=16, group="when", window="Before the Lamp Was Lit", word="before / a.m. and p.m.",
         note="Was the lamp lit when he first came over?",
         fact="Not yet: his first crossing was before lighting-up time on that day (the almanac’s 3.46 p.m. is "
              "15:46 on the Sound Book’s 24-hour clock).",
         pred=lambda r: before_lighting(r["day"], r["time"]),
         alts=[("the lighting-up minute itself counted as ‘before’", lambda r: before_lighting(r["day"], r["time"], inclusive=True))],
         far=[("the almanac’s p.m. times read as morning times (3.46 read as 03:46)",
               lambda r: before_lighting(r["day"], r["time"], twelve_hour=True))]),
    dict(day=17, group="name", window="The Lost Mitten",
         note="What do the two initials on the mitten tell you?",
         fact="The first letter of his first name comes later in the alphabet than the first letter of his surname.",
         pred=lambda r: r["first"][0].upper() > r["last"][0].upper(),
         alts=[("“later” read as “later or the same letter”", lambda r: r["first"][0].upper() >= r["last"][0].upper())],
         far=[]),
    dict(day=18, group="tally", window="No Noughts",
         note="What did Gil notice about his tally?",
         fact="His tally number has no 0 in it: none of its four digits is a nought.",
         pred=lambda r: "0" not in digits(r["tally"]),
         alts=[("a nought in front doesn’t count (0472 read as 472)", lambda r: "0" not in str(r["tally"]))], far=[]),
    dict(day=19, group="name", window="The Iced Cake",
         note="What does the baker remember about his surname?",
         fact="His surname has exactly two vowels (A, E, I, O and U, counting every one; Y is never a vowel).",
         pred=lambda r: vowels(r["last"]) == 2,
         alts=[("Y counted as a vowel", lambda r: vowels(r["last"], y=True) == 2)], far=[]),
    dict(day=20, group="tally", window="Brass, Copper and Tin",
         note="What was his tally made of?",
         fact="His tally was copper, and copper tallies are numbered 0801 to 1600.",
         pred=lambda r: COPPER[0] <= r["tally"] <= COPPER[1], alts=[], far=[]),
    dict(day=21, group="name", window="A Name Called from the Jetty",
         note="What did Ezra hear at the end of his first name?",
         fact="His first name ends with a consonant (any letter other than A, E, I, O or U; Y counts as a consonant).",
         pred=lambda r: r["first"][-1].upper() not in VOWELS,
         alts=[("Y counted as a vowel", lambda r: r["first"][-1].upper() not in VOWELS | {"Y"})], far=[]),
    dict(day=22, group="name", window="The Signwriter’s Stencils",
         note="What does the signwriter tell you about his surname?",
         fact="No letter appears twice anywhere in his surname.",
         pred=lambda r: not repeat_letter(r["last"]),
         alts=[("only a double letter side by side counts as ‘twice’", lambda r: not double_letter(r["last"]))], far=[]),
    dict(day=23, group="name", window="The Striped Scarf",
         note="What does the scarf tell you about his name?",
         fact="His first name and surname together have an even number of letters.",
         pred=lambda r: (len(r["first"]) + len(r["last"])) % 2 == 0, alts=[], far=[]),
]
for c in CLUES:
    c["id"] = str(c["day"])
    c["label"] = f"Window {c['day']}"
    c.setdefault("word", None)
CHECKPOINTS = [6, 12, 18]

# ---------------------------------------------------------------- story text
INTRO = [
    f"{ISLAND} is a small green island at the mouth of {SOUND}, with one white tower, one cottage, a "
    "boathouse and a keeper. For thirty-one winters the keeper was Ezra Tullock. He lit the lamp at "
    "sunset every evening, wrote up his journal at the kitchen table every night, and shared the stove "
    "with a large ginger cat called Bosun.",
    "That December Ezra was keeping more than the light. Christmas parcels for the island of Inishvarra "
    "had gone astray for the third winter running, and on the first of the month he found where they "
    "went: under an old sail in his own boathouse.",
    "On Christmas Eve, at lighting-up time, Candleholm Light did not come on. Bede Halloran brought the "
    "Mail Boat in to the East Landing in the dusk and found Ezra at the foot of the tower stairs. Bosun "
    "was sitting beside him. The stove in the kitchen was cold, the journal lay open on the table, and "
    "the boathouse was empty.",
    f"{SUPERINTENDENT}, who looks after every light on this coast, sealed Ezra’s journal into "
    "twenty-four envelopes, one for each day, with the papers he had pinned to each page. Open one a day. "
    "By Christmas Eve, one line of the Sound Book will be left.",
]
KNOWN_FACTS = [
    "The Sound Book lists every soul who crossed the Sound of Candleholm from 1 to 23 December: 2,400 "
    "people, each exactly once, on the day of their first crossing of the month. Later crossings are not "
    "written in again: the traveller simply shows the brass, copper or tin tally they were given that first "
    "day.",
    "Each line gives the date of that first crossing and the time the traveller stepped aboard and was given "
    "a tally (24-hour clock), the tally number, the name, the home village, the boat, and the number of the "
    "landing where the boat put them ashore. Tallies are drawn from a bag, so the numbers are not in date order.",
    "When anyone in this calendar speaks of how the red cap first came over (the boat, the landing, the time, "
    "the tide), they mean that first crossing: the one in the Sound Book.",
    f"Only one soul who crossed the Sound wore {MARK}. Everything Ezra wrote about “the red cap” is about "
    "that one person, and it is a man.",
    "Ezra’s last entry, on 23 December, says the red cap was coming to Candleholm that night for the "
    "parcels. By Christmas Eve the parcels were gone, and nobody else had set foot on the island.",
    "No two people in the Sound Book share a full name. The chart in Window 1 shows every landing and every "
    "home village.",
]
GLOSSARY = [
    ("Letters", "Count letters only. Every name in the Sound Book is a single word with no spaces, hyphens or "
                "apostrophes."),
    ("Vowels", "A, E, I, O and U. In this case Y is never a vowel."),
    ("Capital or small", "A letter counts whether it is a capital or not: Rennison contains the letter N three times."),
    ("Times", "The Sound Book uses the 24-hour clock. The almanac uses a.m. and p.m.: 3.46 p.m. is 15:46. "
              "“Before” a time means strictly earlier."),
    ("Dates", "Every date is in December. A line’s date is the day of that person’s first crossing of the month."),
    ("Tally digits", "Read all four digits as printed, zeros included: tally 0472 has the digits 0, 4, 7 and 2, "
                     "which add up to 13."),
    ("Landings", "Numbered 1 to 24 on the chart in Window 1. The Sound Book gives the number only."),
    ("The chart", "North is up. Distances are in nautical miles, measured from Candleholm Light."),
]
HOW_TO_PLAY = [
    ("What this is", "A murder mystery in 24 windows. Each day from 1 to 24 December you open one window: one page "
                     "of the keeper’s journal and the paper he pinned to it. Day 1 sets the scene, Day 2 is the "
                     "Sound Book of 2,400 travellers, and Days 3 to 23 each rule some of them out. On Christmas "
                     "Eve one line is left."),
    ("Setting up", "Print the set-up pages and the 24 windows. Fold each window into its own envelope (there is "
                   "a template, or use any envelopes) and stick on the day numbers. On a tablet, just tap "
                   "today’s window on the calendar page."),
    ("Each day", "Open today’s window and read Ezra’s entry and the paper with it. Work out what it means, then "
                 "go through the travellers who are still in the Sound Book and cross out everyone who doesn’t "
                 "fit. The first few days take 20–30 minutes; later days take 5–10."),
    ("Who plays", "One detective on their own, or up to four working together. Split the Sound Book between you "
                  "and compare notes."),
    ("Check-ins", "Windows 6, 12 and 18 tell you how many lines should still be in, so you can catch a slip early."),
    ("Stuck?", "The hint pages at the back give three levels of help for every window. Each level sits on its "
               "own pages, so you only see what you ask for."),
    ("The last window", "On 24 December, open the last window. Use the Sealed Check to test your answer without "
                        "spoilers, then open the Envelope (the separate solution file)."),
]

# ---------------------------------------------------------------- the keeper's journal
# One entry a day, 1-23 December. Each window shows its own entry (Windows 1 and 2 too).
JOURNAL = {
    1: "Wind SW, light. Lamp lit 3.46 p.m. Third December running, the Christmas parcels for Inishvarra are "
       "going astray, and Mrs Breck at the post office is beside herself. This morning I found them: eleven "
       "parcels under the old sail in my boathouse, labels cut off. Someone is using Candleholm as a cupboard. "
       "I have put everything back as I found it. I mean to find out who, and to write it all down here, a day "
       "at a time.",
    2: "Bright and cold. Baked bread, mended the gallery rail, scolded Bosun for sleeping in the coal. Wrote "
       "to Gil Corkhill at the tally office in Port Tolland for a copy of his Sound Book: every soul who crosses "
       "the Sound this month gets a tally and a line in it. Whoever fills my boathouse must be in there somewhere.",
    3: "Up at two to trim the wick, and from the gallery I saw a hand lamp moving down at the boathouse. By the "
       "time I got my boots on, the boat was away. A thread of red wool on the nail by the door, the red of a "
       "channel buoy. Gil knows the cap: a red knitted cap with a white bobble. He says the fellow has his "
       "tally already this month.",
    4: "Dougie Strang keeps the coastguard lookout on Gannet Head and writes down every boat he sees through "
       "his telescope. He remembers the red cap on deck the first time he came over this month: his boat came "
       "through the Inner Passage, between us and the Dulse Reef. I have pinned the note of the passages here.",
    5: "The Drummock brothers were at the creels off the Narrows on the day the red cap first came over. They "
       "watched his boat go by, and it set him ashore somewhere higher up Loch Tarrisk than the Narrows. They "
       "didn’t see which landing. Bosun brought me a crab, which I had not asked for.",
    6: "Mrs Breck sent a fruit cake with the mail and a note. The red cap told her he can see my light from his "
       "own doorstep of a winter evening. So he lives within sight of Candleholm: inside the range of the "
       "light, which the chart shows as a dashed circle.",
    7: "Two in the morning again, and the hand lamp at the boathouse. This time it flashed a message across to a "
       "boat waiting off the Dulse Reef. I only caught the end of it, where a man signs off with the first letter "
       "of his surname. That letter began with a long flash. I have copied out the code book page.",
    8: "Gale in the night, calm by noon. Mrs Breck writes again. Last week the red cap signed for a parcel at "
       "her counter with his first name only, a quick scrawl she can’t read now, but she remembers there was "
       "an A in it. She pinned a blank slip to her letter so I could see the sort of thing.",
    9: "Gil came out on the Tender with my coal and a copy of the Sound Book. When a traveller shows a tally at "
       "the quay, his clerk hangs it on one of two boards for a minute while the line is checked. Gil saw the "
       "red cap’s tally go on the left-hand board.",
    10: "Fog till ten. Gil showed me something in the skippers’ lists: they note the tide beside the time "
        "whenever someone steps aboard and is given a tally. Beside the red cap’s first crossing it says "
        "“tide making”, which is to say rising. I have pinned up the tide table for the first week.",
    11: "Mended Bosun’s basket. Bede Halloran of the Mail Boat came up for his tea. He says the red cap lives on "
        "the mainland coast somewhere between Gannet Head and Selkie Ness. Bede didn’t know which village, "
        "and I didn’t like to ask twice.",
    12: "The Christmas waybill came out with the mail. Mrs Breck says the red cap collected a parcel the first "
        "time he came over, at the landing where he was put ashore. On the waybill she has marked where "
        "parcels can be left.",
    13: "Found a Christmas card dropped on the boathouse path, beside another thread of that red wool. No "
        "message, just a robin and a first name, and the rain has had most of it. I can still see that the "
        "name had five letters, exactly.",
    14: "Gil has a game with the tallies: add up the four digits, and a big total is lucky for a fishing trip. "
        "He can’t tell me the red cap’s number (he hands out hundreds), but he remembers saying it was a lucky "
        "one: its digits add up to more than fifteen.",
    15: "Ottilie Marsden of the Pilot Cutter lent me her log. The red cap went with her once, later in the "
        "month, and she wrote his first name and surname in it. The sea got at the page and only the tail of "
        "the last letter of each name is left, but the two tails are not the same: the names end with "
        "different letters.",
    16: "Clear and very cold. Dougie Strang at the lookout watched the red cap step aboard for his first crossing "
        "of the month. It was in daylight, he says, before I lit the lamp that evening. I have pinned the "
        "almanac here, with my lighting-up times.",
    17: "Bede found a red mitten on the Mail Boat after the red cap had been aboard, and gave it straight back to "
        "him on the quay. It had a laundry mark, two initials, first name then surname. Bede only remembers "
        "that they were the wrong way round, like a schoolboy’s: the first comes later in the alphabet than "
        "the second.",
    18: "Gil again. When the red cap’s tally was shown at the quay he noticed there wasn’t a nought on it "
        "anywhere: fishermen hate a nought, so he always looks. Put up the holly over the door.",
    19: "Nan Fairgrieve, who bakes in Port Tolland, iced a Christmas cake for the red cap with his surname on "
        "top in sugar letters. She ices forty cakes a week and can’t recall the name, but she remembers it "
        "took exactly two of her vowel letters.",
    20: "Tallies are cut in three metals so Gil can sort them at a glance: brass, copper and tin. He says the "
        "red cap’s tally is copper. Bosun has discovered the Christmas ham.",
    21: "Went over to Port Tolland on the Tender for the Christmas messages. On the quay a man called out to the "
        "red cap by his first name over the noise of the gulls. I only caught the end of it: it ended hard, on "
        "a consonant, not on a vowel.",
    22: "The signwriter in Port Tolland lettered the red cap’s surname on a sea chest. She has lost the order "
        "and can’t recall the name, but she cuts one stencil for each letter, and she didn’t have to use any "
        "stencil twice.",
    23: "Bede says the red cap wears a scarf knitted in the old way: one stripe for each letter of the wearer’s "
        "first name and surname together, red first, then white, then red again. The last stripe, at the "
        "tassel end, is white. The red cap comes tonight for the parcels. I have moved them up into the "
        "tower store room, and I shall wait for him by the stove.",
}

# ---------------------------------------------------------------- the daily papers (appendices)
# What Ezra pinned to each page. Kept here so the checker reads exactly what the player reads.
def _tide_rows(days):
    rows = []
    for d in days:
        ev = tide_events(d)
        rows.append((f"{d} Dec", "  ".join(f"{k} {tstr(m)}" for m, k in ev)))
    return rows

def _almanac_rows(days):
    return [(f"{d} Dec", WEATHER[d][0], WEATHER[d][1], ampm(SUNRISE[d]), ampm(LIGHTING[d])) for d in days]

DOCS = {
    3: dict(kind="tallyrules", title="HARBOUR TRUST — RULES OF THE SOUND BOOK",
            lines=["Every soul crossing the Sound in December is given a numbered tally on their first crossing.",
                   "The first crossing is written in the Sound Book with the date and the time. Later crossings are "
                   "not written in again: show your tally.",
                   "The Sound Book is closed each evening at 8 o’clock."]),
    4: dict(kind="passages", title="THE PASSAGES OF THE SOUND (FROM THE CHART)",
            lines=["Inner Passage: between Candleholm and the Dulse Reef. Used by the Mail Boat and the fishing "
                   "boats.",
                   "Outer Passage: west of the Dulse Reef. Used by the Lights Tender and the Pilot Cutter, which "
                   "draw too much water for the Inner Passage.",
                   "Note: at high water the Pilot Cutter may take the Inner Passage.",
                   "The Mail Boat’s round: Port Tolland, Candleholm, the Inner Passage, the Inishvarra piers, then back "
                   "across the Sound and up Loch Tarrisk."]),
    5: dict(kind="loch", title="LOCH TARRISK — LANDINGS FROM THE MOUTH UP",
            lines=["From the mouth: 9 Lochmouth Slip, 10 Achnabrae Jetty, 11 Inverlash Pier, 12 Narrows Slip (at "
                   "the Narrows), 13 Torrandhu Jetty, 14 Ardlarich Slip, 15 Ferrach Pier, 16 Balnacrae Pier, "
                   "17 Dunloch Slip, 18 Lochhead Quay (the head of the loch).",
                   "Above the Narrows the loch turns east, and then south to its head."]),
    6: dict(kind="range", title="CANDLEHOLM LIGHT — WHERE IT CAN BE SEEN",
            lines=["Range: 12 nautical miles, shown on the chart as a dashed circle around the light.",
                   "Inside the circle: Port Tolland, Carrowby, Lannagh, Kilvarra, Rathvarra.",
                   "Right on the circle: Skellan. Every other village is outside it."]),
    7: dict(kind="morse", title="LIGHT SIGNALS — THE CODE BOOK PAGE",
            lines=[" ".join(f"{k} {v}" for k, v in list(MORSE.items())[:13]),
                   " ".join(f"{k} {v}" for k, v in list(MORSE.items())[13:]),
                   "A dot (·) is a short flash, a dash (–) a long one. Read from left to right."]),
    8: dict(kind="slip", title="PORT TOLLAND POST OFFICE — PARCEL SLIP",
            lines=["Parcel for collection. Sign with your first name.",
                   "Signed: ______________   Date: ______   Clerk: H. B."]),
    9: dict(kind="boards", title="THE TALLY OFFICE — THE TWO BOARDS AT THE QUAY",
            lines=["Left-hand board: even numbers.", "Right-hand board: odd numbers.",
                   "A tally shown at the quay hangs on its board while the clerk checks the line."]),
    10: dict(kind="tides", title="TIDE TABLE — SOUND OF CANDLEHOLM, FIRST WEEK OF DECEMBER",
             rows=_tide_rows(range(1, 8)),
             lines=["HW = high water, LW = low water. 24-hour clock. The tide is making (rising) from each low water "
                    "until the next high water, and falling from high water to low water."]),
    11: dict(kind="heads", title="THE MAINLAND COAST (FROM THE CHART)",
             lines=["From north to south along the open coast: Ardvane, Kirkwhinnie, Gannet Head, the mouth of Loch "
                    "Tarrisk, Bayle, Port Tolland, Carrowby, Lannagh, Selkie Ness, Polbrae.",
                    "Achnabrae, Inverlash, Torrandhu and Balnacrae stand on the shores of Loch Tarrisk. Strathcorrie "
                    "is inland. Kilvarra, Rathvarra, Ballyvarra and Skellan are on Inishvarra, across the Sound."]),
    12: dict(kind="waybill", title="MAIL BOAT — CHRISTMAS WAYBILL",
             lines=["Christmas parcels are left only in the parcel sheds at landings 4, 13, 15, 16 and 20.",
                    "Letters only (no parcels) go in the letter boxes at landings 1, 9, 19 and 23."]),
    13: dict(kind="card", title="A CHRISTMAS CARD, PUSHED UNDER THE BOATHOUSE DOOR",
             lines=["With love at Christmas from", "_ _ _ _ _   (the rest washed away)"]),
    14: dict(kind="game", title="GIL’S TALLY GAME",
             lines=["Add the four digits of a tally, zeros included.", "Example: tally 0472: 0 + 4 + 7 + 2 = 13.",
                    "More than fifteen is lucky for a fishing trip."]),
    15: dict(kind="log", title="PILOT CUTTER — PASSENGER LOG (EXTRACT)",
             lines=["Passenger: first name and surname, ink run. The last letters of the two names are different.",
                    "Remarks: red knitted cap. Paid in coin."]),
    16: dict(kind="almanac", title="COASTAL WEATHER AND ALMANAC — FIRST WEEK OF DECEMBER",
             rows=_almanac_rows(range(1, 8)),
             lines=["Lighting-up time is sunset: the keepers light their lamps then. The almanac uses a.m. and p.m."]),
    17: dict(kind="mitten", title="LOST PROPERTY — ONE RED MITTEN",
             lines=["Laundry mark inside the cuff: two initials, first name then surname.",
                    "The first initial comes later in the alphabet than the second."]),
    18: dict(kind="noughts", title="GIL’S NOTE",
             lines=["Not a nought on it, not one. — G. C.", "(A tally always has four digits: 0472 has a nought.)"]),
    19: dict(kind="cake", title="FAIRGRIEVE’S BAKERY — ORDER BOOK",
             lines=["Christmas cake, iced, surname on top in sugar letters.",
                    "Vowel letters used: 2. (A, E, I, O, U. Y is not one of my vowels. — N. F.)"]),
    20: dict(kind="metals", title="THE TALLY OFFICE — TALLY METALS",
             lines=["Brass: 0001 to 0800.", "Copper: 0801 to 1600.", "Tin: 1601 to 2400."]),
    21: dict(kind="quay", title="EZRA’S NOTE ON VOWELS",
             lines=["Vowels are A, E, I, O and U. Y is not a vowel. A name that ends in any other letter ends on a "
                    "consonant."]),
    22: dict(kind="stencils", title="SIGNWRITER’S BILL",
             lines=["One sea chest, surname lettered in white.", "Stencils cut: one for each different letter. No "
                    "stencil used twice."]),
    23: dict(kind="scarf", title="MRS BRECK’S KNITTING PATTERN",
             lines=["One stripe for each letter of the first name and the surname together.",
                    "Stripes: red, white, red, white… The first stripe is red."]),
}

EPILOGUE = [
    "The red cap was Jonas Garvock, tally 1478, a carter from Carrowby.",
    "Jonas loaded the Christmas mail onto the boats at Port Tolland. For three winters he had taken a few "
    "parcels at a time from the sacks for Inishvarra, cut off the labels, and rowed them over to Candleholm at "
    "night, where nobody would look: the old boathouse, under a sail. In January he sold what was in them.",
    "His first crossing of December was on the 2nd: he stepped aboard the Mail Boat at Port Tolland at 13:38, "
    "on a rising tide, two hours before Ezra lit the lamp. The boat went round by Candleholm and the Inner "
    "Passage, called at Inishvarra and set him ashore at Ferrach Pier, high up Loch Tarrisk, where he collected "
    "a parcel from the shed. He showed his copper tally, 1478, on every crossing after that, and on the nights "
    "he rowed over to Candleholm he needed no tally at all.",
    "His brother-in-law, who fished out of Polbrae and asked no questions, waited off the Dulse Reef on the nights "
    "there were parcels to carry away, and Jonas signalled to him from the boathouse with a hand lamp, signing "
    "off with a G, just as Ezra saw.",
    "Ezra found the parcels on the 1st and wrote everything down. On the night of the 23rd Jonas came for the "
    "parcels and found the boathouse empty. He saw the tower door ajar and climbed to the store room. Ezra, "
    "who had been waiting by the stove in the cottage, followed him up and stood on the stairs between Jonas "
    "and the door. Jonas pushed past him in the dark and ran with the parcels, and Ezra fell.",
    "Superintendent Treleaven read the journal one page at a time, just as Ezra had written it, and on "
    "Twelfth Night the parcels went home to Inishvarra. Bede Halloran took Bosun on the Mail Boat, where he "
    "is now a ship’s cat. And every evening at lighting-up time, Candleholm Light comes on again.",
]

FINALE = [
    "Christmas Eve. At 3.42 p.m., lighting-up time, Candleholm Light did not come on.",
    "Bede Halloran saw the dark tower from the Mail Boat and brought her in to the East Landing in the dusk. "
    "He found Ezra at the foot of the tower stairs, with Bosun sitting beside him. The store room was empty. "
    "Ezra’s journal lay open on the kitchen table, at the page for the 23rd.",
    "If you have opened every window, one line is left in the Sound Book. That line belongs to the red cap.",
    "Turn the page for the Sealed Check: it tells you whether you are right without printing his name anywhere "
    "in this calendar. Then open the Envelope, the separate solution file, to read what happened.",
]
