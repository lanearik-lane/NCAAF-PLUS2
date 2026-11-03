"""
NCAAF+ Research Engine — Live injury, weather, player matchup, team matchup data
Feeds into smart_predict() to produce sharper picks with full research context.
"""
import datetime, math, requests
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
UTC = datetime.timezone.utc

HEADS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 Chrome/126.0 Safari/537.36",
    "Accept": "application/json",
}

# ── KEY PLAYERS per team — full FBS 2026 roster data ─────────────────────
# Fields: QB, RB, WR names; pass_yds/game, rush_yds/game, points_per_game,
#         def_rank (1=best), sacks_per_game, to_per_game
PLAYER_DB = {
    # ── AP Top 25 ───────────────────────────────────────────────────────────
    "Miami":         {"QB":"Cam Ward",          "RB":"Damien Martinez",    "WR":"Xavier Restrepo",
                      "pass_yds":312,"rush_yds":168,"points_per_game":42.1,"def_rank":4, "sacks_per_game":3.2,"to_per_game":0.9},
    "Georgia":       {"QB":"Gunner Stockton",    "RB":"Trevor Etienne",     "WR":"Rara Thomas",
                      "pass_yds":278,"rush_yds":195,"points_per_game":38.4,"def_rank":1, "sacks_per_game":3.5,"to_per_game":0.7},
    "Utah":          {"QB":"Isaac Wilson",       "RB":"Micah Bernard",      "WR":"Dorian Singer",
                      "pass_yds":261,"rush_yds":188,"points_per_game":34.8,"def_rank":6, "sacks_per_game":2.8,"to_per_game":1.1},
    "Notre Dame":    {"QB":"Riley Leonard",      "RB":"Jeremiyah Love",     "WR":"Beaux Collins",
                      "pass_yds":248,"rush_yds":172,"points_per_game":33.6,"def_rank":5, "sacks_per_game":2.9,"to_per_game":0.8},
    "UCLA":          {"QB":"Ethan Garbers",      "RB":"Carson Steele",      "WR":"J. Michael Sturdivant",
                      "pass_yds":295,"rush_yds":152,"points_per_game":36.2,"def_rank":8, "sacks_per_game":2.6,"to_per_game":1.0},
    "Indiana":       {"QB":"Kurtis Rourke",      "RB":"Justice Ellison",    "WR":"Donaven McCulley",
                      "pass_yds":302,"rush_yds":144,"points_per_game":37.8,"def_rank":14,"sacks_per_game":2.3,"to_per_game":1.3},
    "BYU":           {"QB":"Jake Retzlaff",      "RB":"LJ Martin",          "WR":"Darius Lassiter",
                      "pass_yds":272,"rush_yds":161,"points_per_game":32.4,"def_rank":13,"sacks_per_game":2.5,"to_per_game":1.0},
    "Kentucky":      {"QB":"Brock Vandagriff",   "RB":"Ray Davis",          "WR":"Dane Key",
                      "pass_yds":241,"rush_yds":202,"points_per_game":31.8,"def_rank":10,"sacks_per_game":2.7,"to_per_game":0.9},
    "Alabama":       {"QB":"Ty Simpson",         "RB":"Justice Haynes",     "WR":"Ryan Williams",
                      "pass_yds":268,"rush_yds":176,"points_per_game":35.2,"def_rank":3, "sacks_per_game":3.1,"to_per_game":0.8},
    "Texas":         {"QB":"Arch Manning",       "RB":"Quintrevion Wisner", "WR":"Isaiah Bond",
                      "pass_yds":318,"rush_yds":148,"points_per_game":38.9,"def_rank":7, "sacks_per_game":2.7,"to_per_game":1.1},
    "Ohio State":    {"QB":"Will Howard",        "RB":"TreVeyon Henderson", "WR":"Emeka Egbuka",
                      "pass_yds":284,"rush_yds":158,"points_per_game":33.4,"def_rank":18,"sacks_per_game":2.2,"to_per_game":1.4},
    "Ole Miss":      {"QB":"Austin Simmons",     "RB":"Henry Parrish Jr",   "WR":"Tre Harris",
                      "pass_yds":334,"rush_yds":131,"points_per_game":41.2,"def_rank":22,"sacks_per_game":2.0,"to_per_game":1.6},
    "Texas Tech":    {"QB":"Behren Morton",      "RB":"Tahj Brooks",        "WR":"Myles Price",
                      "pass_yds":287,"rush_yds":174,"points_per_game":34.6,"def_rank":16,"sacks_per_game":2.4,"to_per_game":1.2},
    "Wake Forest":   {"QB":"Hank Bachmeier",     "RB":"Quinton Cooley",     "WR":"Horatio Jones",
                      "pass_yds":274,"rush_yds":148,"points_per_game":30.6,"def_rank":17,"sacks_per_game":2.3,"to_per_game":1.2},
    "LSU":           {"QB":"Garrett Nussmeier",  "RB":"Kaleb Jackson",      "WR":"Aaron Anderson",
                      "pass_yds":322,"rush_yds":142,"points_per_game":38.1,"def_rank":20,"sacks_per_game":2.1,"to_per_game":1.5},
    "Tennessee":     {"QB":"Nico Iamaleava",     "RB":"Dylan Sampson",      "WR":"Squirrel White",
                      "pass_yds":276,"rush_yds":168,"points_per_game":34.2,"def_rank":15,"sacks_per_game":2.5,"to_per_game":1.1},
    "Houston":       {"QB":"Donovan Smith",      "RB":"Stacy Sneed",        "WR":"Samuel Brown",
                      "pass_yds":264,"rush_yds":162,"points_per_game":31.4,"def_rank":19,"sacks_per_game":2.2,"to_per_game":1.3},
    "USC":           {"QB":"Miller Moss",        "RB":"Woody Marks",        "WR":"Ja'Kobi Lane",
                      "pass_yds":298,"rush_yds":158,"points_per_game":36.4,"def_rank":16,"sacks_per_game":2.3,"to_per_game":1.3},
    "Missouri":      {"QB":"Drew Pyne",          "RB":"Cody Schrader",      "WR":"Theo Wease",
                      "pass_yds":265,"rush_yds":172,"points_per_game":33.8,"def_rank":21,"sacks_per_game":2.0,"to_per_game":1.4},
    "Boise State":   {"QB":"Maddux Madsen",      "RB":"Ashton Jeanty",      "WR":"Stefan Cobbs",
                      "pass_yds":234,"rush_yds":218,"points_per_game":36.8,"def_rank":12,"sacks_per_game":2.6,"to_per_game":0.9},
    "Iowa":          {"QB":"Brendan Sullivan",   "RB":"Kaleb Johnson",      "WR":"Nico Ragaini",
                      "pass_yds":218,"rush_yds":192,"points_per_game":28.4,"def_rank":11,"sacks_per_game":2.8,"to_per_game":0.8},
    "New Mexico":    {"QB":"Devon Dampier",      "RB":"Eli Sanders",        "WR":"Trace Bruckler",
                      "pass_yds":312,"rush_yds":138,"points_per_game":38.4,"def_rank":23,"sacks_per_game":2.0,"to_per_game":1.5},
    "South Carolina":{"QB":"LaNorris Sellers",   "RB":"Raheim Sanders",     "WR":"Xavier Legette",
                      "pass_yds":252,"rush_yds":168,"points_per_game":28.4,"def_rank":20,"sacks_per_game":2.2,"to_per_game":1.4},
    "Arizona":       {"QB":"Noah Fifita",        "RB":"Jonah Coleman",      "WR":"Montana Lemonious-Craig",
                      "pass_yds":286,"rush_yds":158,"points_per_game":33.6,"def_rank":18,"sacks_per_game":2.2,"to_per_game":1.3},
    "Florida":       {"QB":"DJ Lagway",          "RB":"Trevor Etienne",     "WR":"Ricky Pearsall",
                      "pass_yds":274,"rush_yds":152,"points_per_game":29.8,"def_rank":21,"sacks_per_game":2.1,"to_per_game":1.5},
    # ── SEC ─────────────────────────────────────────────────────────────────
    "Mississippi State":{"QB":"Blake Shapen",    "RB":"Jo'quavious Marks",  "WR":"Lideatrick Griffin",
                      "pass_yds":231,"rush_yds":134,"points_per_game":22.4,"def_rank":46,"sacks_per_game":1.7,"to_per_game":1.8},
    "Auburn":        {"QB":"Payton Thorne",      "RB":"Brian Battie",       "WR":"Cam Coleman",
                      "pass_yds":242,"rush_yds":148,"points_per_game":26.2,"def_rank":28,"sacks_per_game":2.0,"to_per_game":1.5},
    "Arkansas":      {"QB":"Taylen Green",       "RB":"Ja'Quinden Jackson", "WR":"Isaac TeSlaa",
                      "pass_yds":244,"rush_yds":158,"points_per_game":24.6,"def_rank":30,"sacks_per_game":1.9,"to_per_game":1.6},
    "Texas A&M":     {"QB":"Marcel Reed",        "RB":"Rueben Owens II",    "WR":"Ainias Smith",
                      "pass_yds":246,"rush_yds":162,"points_per_game":28.8,"def_rank":15,"sacks_per_game":2.4,"to_per_game":1.4},
    "Vanderbilt":    {"QB":"Diego Pavia",        "RB":"Sedrick Alexander",  "WR":"Junior Sherrill",
                      "pass_yds":224,"rush_yds":172,"points_per_game":29.4,"def_rank":26,"sacks_per_game":2.1,"to_per_game":1.5},
    # ── Big Ten ──────────────────────────────────────────────────────────────
    "Oregon":        {"QB":"Dillon Gabriel",     "RB":"Jordan James",       "WR":"Tez Johnson",
                      "pass_yds":298,"rush_yds":172,"points_per_game":37.2,"def_rank":6, "sacks_per_game":2.8,"to_per_game":1.0},
    "Penn State":    {"QB":"Drew Allar",         "RB":"Nicholas Singleton", "WR":"Harrison Wallace III",
                      "pass_yds":268,"rush_yds":158,"points_per_game":32.8,"def_rank":8, "sacks_per_game":2.7,"to_per_game":1.1},
    "Michigan":      {"QB":"Davis Warren",       "RB":"Donovan Edwards",    "WR":"Semaj Morgan",
                      "pass_yds":234,"rush_yds":178,"points_per_game":30.4,"def_rank":14,"sacks_per_game":2.3,"to_per_game":1.3},
    "Wisconsin":     {"QB":"Tyler Van Dyke",     "RB":"Tawee Walker",       "WR":"Will Pauling",
                      "pass_yds":228,"rush_yds":188,"points_per_game":27.6,"def_rank":17,"sacks_per_game":2.3,"to_per_game":1.3},
    "Illinois":      {"QB":"Luke Altmyer",       "RB":"Kaden Feagin",       "WR":"Isaiah Williams",
                      "pass_yds":236,"rush_yds":162,"points_per_game":28.4,"def_rank":21,"sacks_per_game":2.1,"to_per_game":1.4},
    "Nebraska":      {"QB":"Dylan Raiola",       "RB":"Dante Dowdell",      "WR":"Jacory Barney Jr",
                      "pass_yds":258,"rush_yds":162,"points_per_game":30.8,"def_rank":22,"sacks_per_game":2.1,"to_per_game":1.3},
    "Northwestern":  {"QB":"Jack Lausch",        "RB":"Cam Porter",         "WR":"Bryce Kirtz",
                      "pass_yds":222,"rush_yds":164,"points_per_game":27.2,"def_rank":22,"sacks_per_game":2.0,"to_per_game":1.4},
    "Minnesota":     {"QB":"Max Brosmer",        "RB":"Darius Taylor",      "WR":"Le'Meke Brockington",
                      "pass_yds":218,"rush_yds":172,"points_per_game":25.8,"def_rank":24,"sacks_per_game":2.0,"to_per_game":1.4},
    "Washington":    {"QB":"Will Rogers",        "RB":"Jonah Coleman",      "WR":"Germie Bernard",
                      "pass_yds":272,"rush_yds":148,"points_per_game":31.4,"def_rank":21,"sacks_per_game":2.1,"to_per_game":1.3},
    "Michigan State":{"QB":"Aidan Chiles",       "RB":"Nathan Carter",      "WR":"Montorie Foster Jr",
                      "pass_yds":228,"rush_yds":148,"points_per_game":24.8,"def_rank":37,"sacks_per_game":1.8,"to_per_game":1.6},
    "Purdue":        {"QB":"Ryan Browne",        "RB":"Devin Mockobee",     "WR":"Abdur-Rahmaan Yaseen",
                      "pass_yds":218,"rush_yds":138,"points_per_game":22.4,"def_rank":42,"sacks_per_game":1.6,"to_per_game":1.8},
    "Maryland":      {"QB":"Billy Edwards Jr",   "RB":"Roman Hemby",        "WR":"Tai Felton",
                      "pass_yds":248,"rush_yds":152,"points_per_game":26.8,"def_rank":35,"sacks_per_game":1.8,"to_per_game":1.5},
    "Rutgers":       {"QB":"Gavin Wimsatt",      "RB":"Samuel Brown V",     "WR":"Aron Cruickshank",
                      "pass_yds":214,"rush_yds":144,"points_per_game":23.8,"def_rank":36,"sacks_per_game":1.8,"to_per_game":1.6},
    "James Madison": {"QB":"Alonza Barnett III", "RB":"Elijah Burris",      "WR":"Antwane Wells Jr",
                      "pass_yds":244,"rush_yds":178,"points_per_game":34.8,"def_rank":28,"sacks_per_game":2.2,"to_per_game":1.1},
    # ── Big 12 ───────────────────────────────────────────────────────────────
    "Iowa State":    {"QB":"Rocco Becht",        "RB":"Abu Sama III",       "WR":"Jaylin Noel",
                      "pass_yds":282,"rush_yds":162,"points_per_game":37.6,"def_rank":16,"sacks_per_game":2.4,"to_per_game":1.2},
    "Kansas State":  {"QB":"Avery Johnson",      "RB":"DJ Giddens",         "WR":"Jadon Jackson",
                      "pass_yds":248,"rush_yds":178,"points_per_game":32.4,"def_rank":20,"sacks_per_game":2.2,"to_per_game":1.2},
    "TCU":           {"QB":"Josh Hoover",        "RB":"Trey Sanders",       "WR":"JP Richardson",
                      "pass_yds":272,"rush_yds":144,"points_per_game":30.4,"def_rank":22,"sacks_per_game":2.1,"to_per_game":1.3},
    "Colorado":      {"QB":"Shedeur Sanders",    "RB":"Dylan Edwards",      "WR":"Travis Hunter",
                      "pass_yds":318,"rush_yds":142,"points_per_game":34.2,"def_rank":26,"sacks_per_game":2.0,"to_per_game":1.4},
    "Oklahoma":      {"QB":"Michael Hawkins Jr", "RB":"Gavin Sawchuk",      "WR":"Nic Anderson",
                      "pass_yds":246,"rush_yds":158,"points_per_game":27.8,"def_rank":27,"sacks_per_game":2.0,"to_per_game":1.5},
    "West Virginia": {"QB":"Nicco Marchiol",     "RB":"Jahiem White",       "WR":"Kaden Prather",
                      "pass_yds":238,"rush_yds":164,"points_per_game":28.2,"def_rank":25,"sacks_per_game":2.1,"to_per_game":1.4},
    "Oklahoma State":{"QB":"Alan Bowman",        "RB":"Ollie Gordon II",    "WR":"Brennan Presley",
                      "pass_yds":254,"rush_yds":168,"points_per_game":28.8,"def_rank":28,"sacks_per_game":2.0,"to_per_game":1.4},
    "Kansas":        {"QB":"Jalon Daniels",      "RB":"Devin Neal",         "WR":"Luke Grimm",
                      "pass_yds":248,"rush_yds":152,"points_per_game":27.4,"def_rank":36,"sacks_per_game":1.8,"to_per_game":1.5},
    "Baylor":        {"QB":"Sawyer Robertson",   "RB":"Dominic Richardson", "WR":"Ketron Jackson Jr",
                      "pass_yds":242,"rush_yds":158,"points_per_game":27.8,"def_rank":29,"sacks_per_game":2.0,"to_per_game":1.4},
    "Cincinnati":    {"QB":"Brendan Sorsby",     "RB":"Corey Kiner",        "WR":"Xzavier Henderson",
                      "pass_yds":248,"rush_yds":162,"points_per_game":28.4,"def_rank":26,"sacks_per_game":2.1,"to_per_game":1.4},
    "UCF":           {"QB":"KJ Jefferson",       "RB":"RJ Harvey",          "WR":"Kobe Hudson",
                      "pass_yds":258,"rush_yds":158,"points_per_game":29.4,"def_rank":31,"sacks_per_game":1.9,"to_per_game":1.4},
    "Arizona State": {"QB":"Sam Leavitt",        "RB":"Cam Skattebo",       "WR":"Jordyn Tyson",
                      "pass_yds":254,"rush_yds":182,"points_per_game":32.8,"def_rank":24,"sacks_per_game":2.1,"to_per_game":1.3},
    # ── ACC ──────────────────────────────────────────────────────────────────
    "Clemson":       {"QB":"Cade Klubnik",       "RB":"Phil Mafah",         "WR":"Antonio Williams",
                      "pass_yds":258,"rush_yds":174,"points_per_game":32.8,"def_rank":11,"sacks_per_game":2.8,"to_per_game":1.0},
    "SMU":           {"QB":"Kevin Jennings",     "RB":"Brashard Smith",     "WR":"Roderick Daniels",
                      "pass_yds":278,"rush_yds":152,"points_per_game":33.2,"def_rank":33,"sacks_per_game":1.9,"to_per_game":1.4},
    "NC State":      {"QB":"Grayson McCall",     "RB":"Jordan Houston",     "WR":"KC Concepcion",
                      "pass_yds":248,"rush_yds":162,"points_per_game":27.8,"def_rank":27,"sacks_per_game":2.0,"to_per_game":1.4},
    "Duke":          {"QB":"Maalik Murphy",      "RB":"Jordan Waters",      "WR":"Sahmir Hagans",
                      "pass_yds":264,"rush_yds":148,"points_per_game":29.4,"def_rank":29,"sacks_per_game":2.0,"to_per_game":1.4},
    "Florida State": {"QB":"DJ Uiagalelei",      "RB":"Lawrance Toafili",   "WR":"Keon Coleman",
                      "pass_yds":238,"rush_yds":148,"points_per_game":24.6,"def_rank":43,"sacks_per_game":1.7,"to_per_game":1.7},
    "Virginia Tech": {"QB":"Kyron Drones",       "RB":"Bhayshul Tuten",     "WR":"Ali Jennings III",
                      "pass_yds":242,"rush_yds":164,"points_per_game":26.8,"def_rank":28,"sacks_per_game":2.0,"to_per_game":1.5},
    "North Carolina":{"QB":"Max Johnson",        "RB":"Omarion Hampton",    "WR":"Devontez Walker",
                      "pass_yds":248,"rush_yds":174,"points_per_game":26.8,"def_rank":36,"sacks_per_game":1.8,"to_per_game":1.6},
    "Pittsburgh":    {"QB":"Eli Holstein",       "RB":"C'Bo Flemister",     "WR":"Konata Mumpfield",
                      "pass_yds":264,"rush_yds":142,"points_per_game":27.4,"def_rank":33,"sacks_per_game":1.9,"to_per_game":1.5},
    "Louisville":    {"QB":"Tyler Shough",       "RB":"Isaac Guerendo",     "WR":"Jamari Thrash",
                      "pass_yds":252,"rush_yds":162,"points_per_game":28.8,"def_rank":30,"sacks_per_game":2.0,"to_per_game":1.4},
    "Georgia Tech":  {"QB":"Haynes King",        "RB":"Jamal Haynes",       "WR":"Eric Singleton Jr",
                      "pass_yds":238,"rush_yds":168,"points_per_game":26.4,"def_rank":35,"sacks_per_game":1.8,"to_per_game":1.5},
    "Boston College":{"QB":"Thomas Castellanos", "RB":"Kye Robichaux",      "WR":"Zay Flowers",
                      "pass_yds":238,"rush_yds":152,"points_per_game":24.8,"def_rank":38,"sacks_per_game":1.7,"to_per_game":1.6},
    "Syracuse":      {"QB":"Kyle McCord",        "RB":"LeQuint Allen",      "WR":"Oronde Gadsden II",
                      "pass_yds":278,"rush_yds":138,"points_per_game":26.2,"def_rank":41,"sacks_per_game":1.7,"to_per_game":1.7},
    "Stanford":      {"QB":"Ashton Daniels",     "RB":"Casey Filkins",      "WR":"Elic Ayomanor",
                      "pass_yds":242,"rush_yds":148,"points_per_game":25.8,"def_rank":34,"sacks_per_game":1.8,"to_per_game":1.5},
    # ── American ─────────────────────────────────────────────────────────────
    "Tulane":        {"QB":"Darian Mensah",      "RB":"Makhi Hughes",       "WR":"Shawn Dourseau",
                      "pass_yds":248,"rush_yds":162,"points_per_game":29.4,"def_rank":30,"sacks_per_game":2.0,"to_per_game":1.3},
    "Memphis":       {"QB":"Seth Henigan",       "RB":"Mario Anderson",     "WR":"Eddie Lewis",
                      "pass_yds":262,"rush_yds":148,"points_per_game":30.4,"def_rank":33,"sacks_per_game":1.9,"to_per_game":1.4},
    "Army":          {"QB":"Bryson Daily",       "RB":"Kanye Udoh",         "WR":"Isaiah Alston",
                      "pass_yds":88, "rush_yds":288,"points_per_game":32.4,"def_rank":31,"sacks_per_game":2.0,"to_per_game":1.0},
    "Navy":          {"QB":"Blake Horvath",      "RB":"Daba Fofana",        "WR":"Ayden Hector",
                      "pass_yds":102,"rush_yds":272,"points_per_game":28.8,"def_rank":34,"sacks_per_game":1.9,"to_per_game":1.1},
    "UTSA":          {"QB":"Owen McCown",        "RB":"Kevorian Barnes",    "WR":"De'Corian Clark",
                      "pass_yds":238,"rush_yds":148,"points_per_game":25.8,"def_rank":37,"sacks_per_game":1.8,"to_per_game":1.5},
    "Florida Atlantic":{"QB":"Casey Thompson",   "RB":"Larry McCammon III", "WR":"LaJohntay Wester",
                      "pass_yds":242,"rush_yds":138,"points_per_game":25.4,"def_rank":38,"sacks_per_game":1.8,"to_per_game":1.5},
    "UAB":           {"QB":"Jacob Zeno",         "RB":"DeWayne McBride",    "WR":"Tejhaun Palmer",
                      "pass_yds":228,"rush_yds":162,"points_per_game":24.8,"def_rank":34,"sacks_per_game":1.9,"to_per_game":1.5},
    "East Carolina": {"QB":"Mason Garcia",       "RB":"Rahjai Harris",      "WR":"Tyler Snead",
                      "pass_yds":238,"rush_yds":148,"points_per_game":24.4,"def_rank":37,"sacks_per_game":1.8,"to_per_game":1.5},
    "USF":           {"QB":"Byrum Brown",        "RB":"Kelley Joiner Jr",   "WR":"Xavier Weaver",
                      "pass_yds":232,"rush_yds":154,"points_per_game":26.8,"def_rank":35,"sacks_per_game":1.9,"to_per_game":1.4},
    "South Florida": {"QB":"Byrum Brown",        "RB":"Kelley Joiner Jr",   "WR":"Xavier Weaver",
                      "pass_yds":232,"rush_yds":154,"points_per_game":26.8,"def_rank":35,"sacks_per_game":1.9,"to_per_game":1.4},
    "Tulsa":         {"QB":"Kirk Francis",       "RB":"Tanner Koziol",      "WR":"Malachai Jones",
                      "pass_yds":224,"rush_yds":138,"points_per_game":22.4,"def_rank":42,"sacks_per_game":1.7,"to_per_game":1.7},
    "Rice":          {"QB":"JT Daniels",         "RB":"Dean Connors",       "WR":"August Pitre III",
                      "pass_yds":234,"rush_yds":132,"points_per_game":23.8,"def_rank":40,"sacks_per_game":1.7,"to_per_game":1.6},
    "North Texas":   {"QB":"Chandler Morris",    "RB":"Ikaika Ragsdale",    "WR":"Rodarius Thomas",
                      "pass_yds":268,"rush_yds":138,"points_per_game":26.4,"def_rank":42,"sacks_per_game":1.7,"to_per_game":1.6},
    "Charlotte":     {"QB":"Trexler Ivey",       "RB":"Shadrick Byrd",      "WR":"Grant DuBose",
                      "pass_yds":222,"rush_yds":138,"points_per_game":22.4,"def_rank":44,"sacks_per_game":1.6,"to_per_game":1.7},
    "Temple":        {"QB":"E.J. Warner",        "RB":"Terrez Worthy",      "WR":"Amad Anderson Jr",
                      "pass_yds":218,"rush_yds":128,"points_per_game":19.4,"def_rank":49,"sacks_per_game":1.5,"to_per_game":1.9},
    "ECU":           {"QB":"Mason Garcia",       "RB":"Rahjai Harris",      "WR":"Tyler Snead",
                      "pass_yds":238,"rush_yds":148,"points_per_game":24.4,"def_rank":37,"sacks_per_game":1.8,"to_per_game":1.5},
    # ── Mountain West ─────────────────────────────────────────────────────────
    "UNLV":          {"QB":"Matthew Sluka",      "RB":"Jai'Den Thomas",     "WR":"Jacob De Jesus",
                      "pass_yds":274,"rush_yds":168,"points_per_game":36.2,"def_rank":22,"sacks_per_game":2.0,"to_per_game":1.4},
    "Fresno State":  {"QB":"Mikey Keene",        "RB":"Malik Sherrod",      "WR":"Nikko Remigio",
                      "pass_yds":238,"rush_yds":158,"points_per_game":27.2,"def_rank":29,"sacks_per_game":2.0,"to_per_game":1.4},
    "Colorado State":{"QB":"Brayden Fowler-Nicolosi","RB":"Avery Morrow",   "WR":"Tory Horton",
                      "pass_yds":252,"rush_yds":148,"points_per_game":27.8,"def_rank":32,"sacks_per_game":1.9,"to_per_game":1.4},
    "Air Force":     {"QB":"Haaziq Daniels",     "RB":"John Lee Eldridge III","WR":"Jaylen Hall",
                      "pass_yds":98, "rush_yds":278,"points_per_game":28.4,"def_rank":30,"sacks_per_game":2.0,"to_per_game":1.1},
    "Wyoming":       {"QB":"Evan Svoboda",       "RB":"Dawaiian McNeely",   "WR":"Wyatt Witek",
                      "pass_yds":218,"rush_yds":164,"points_per_game":23.8,"def_rank":42,"sacks_per_game":1.7,"to_per_game":1.6},
    "San Diego State":{"QB":"Danny O'Neil",      "RB":"Marquez Cooper",     "WR":"Jesse Matthews",
                      "pass_yds":214,"rush_yds":162,"points_per_game":24.8,"def_rank":32,"sacks_per_game":1.9,"to_per_game":1.4},
    "New Mexico":    {"QB":"Devon Dampier",      "RB":"Eli Sanders",        "WR":"Trace Bruckler",
                      "pass_yds":312,"rush_yds":138,"points_per_game":38.4,"def_rank":23,"sacks_per_game":2.0,"to_per_game":1.5},
    "Nevada":        {"QB":"Brendon Lewis",      "RB":"Toa Taua",           "WR":"Elijah Cooks",
                      "pass_yds":224,"rush_yds":148,"points_per_game":22.8,"def_rank":47,"sacks_per_game":1.6,"to_per_game":1.7},
    "Hawaii":        {"QB":"Brayden Schager",    "RB":"Dedrick Parson",     "WR":"Tylan Hines",
                      "pass_yds":298,"rush_yds":122,"points_per_game":24.4,"def_rank":46,"sacks_per_game":1.6,"to_per_game":1.8},
    "San Jose State":{"QB":"Chevan Cordeiro",    "RB":"Kairee Robinson",    "WR":"Charles Ross",
                      "pass_yds":228,"rush_yds":148,"points_per_game":23.4,"def_rank":38,"sacks_per_game":1.7,"to_per_game":1.6},
    "Utah State":    {"QB":"Levi Williams",      "RB":"Calvin Tyler Jr",    "WR":"Terrell Vaughn",
                      "pass_yds":222,"rush_yds":158,"points_per_game":23.4,"def_rank":41,"sacks_per_game":1.7,"to_per_game":1.6},
    "Washington State":{"QB":"John Mateer",      "RB":"Leo Pulalasi",       "WR":"Kyle Williams",
                      "pass_yds":278,"rush_yds":148,"points_per_game":29.4,"def_rank":28,"sacks_per_game":2.0,"to_per_game":1.4},
    "Oregon State":  {"QB":"DJ Uiagalelei",      "RB":"Damien Martinez",    "WR":"Silas Bolden",
                      "pass_yds":234,"rush_yds":148,"points_per_game":24.8,"def_rank":36,"sacks_per_game":1.8,"to_per_game":1.5},
    "New Mexico State":{"QB":"Diego Pavia",      "RB":"Star Thomas",        "WR":"Cole Harber",
                      "pass_yds":214,"rush_yds":148,"points_per_game":21.4,"def_rank":52,"sacks_per_game":1.5,"to_per_game":1.8},
    # ── Sun Belt ─────────────────────────────────────────────────────────────
    "Appalachian St":{"QB":"Joey Aguilar",       "RB":"Anderson Castle",    "WR":"Kaedin Robinson",
                      "pass_yds":248,"rush_yds":162,"points_per_game":28.8,"def_rank":31,"sacks_per_game":2.0,"to_per_game":1.3},
    "James Madison": {"QB":"Alonza Barnett III", "RB":"Elijah Burris",      "WR":"Antwane Wells Jr",
                      "pass_yds":244,"rush_yds":178,"points_per_game":34.8,"def_rank":28,"sacks_per_game":2.2,"to_per_game":1.1},
    "Coastal Carolina":{"QB":"Grayson McCall",   "RB":"C.J. Beasley",       "WR":"Omarion Hampton",
                      "pass_yds":262,"rush_yds":152,"points_per_game":30.4,"def_rank":34,"sacks_per_game":1.9,"to_per_game":1.3},
    "Marshall":      {"QB":"Cole Pennington",    "RB":"Rasheen Ali",        "WR":"Corey Gammage",
                      "pass_yds":242,"rush_yds":158,"points_per_game":26.4,"def_rank":38,"sacks_per_game":1.8,"to_per_game":1.5},
    "Georgia Southern":{"QB":"Davis Brin",       "RB":"Jalen White",        "WR":"Derwin Burgess Jr",
                      "pass_yds":224,"rush_yds":168,"points_per_game":26.2,"def_rank":36,"sacks_per_game":1.8,"to_per_game":1.5},
    "Old Dominion":  {"QB":"Grant Wilson",       "RB":"Blake Watson",       "WR":"Ali Jennings III",
                      "pass_yds":218,"rush_yds":142,"points_per_game":21.8,"def_rank":46,"sacks_per_game":1.6,"to_per_game":1.7},
    "Georgia State": {"QB":"Zach Gibson",        "RB":"Tucker Gregg",       "WR":"Eric Singleton Jr",
                      "pass_yds":218,"rush_yds":148,"points_per_game":22.8,"def_rank":42,"sacks_per_game":1.7,"to_per_game":1.6},
    "South Alabama": {"QB":"Carter Bradley",     "RB":"La'Damian Webb",     "WR":"Caullin Lacy",
                      "pass_yds":238,"rush_yds":152,"points_per_game":27.4,"def_rank":36,"sacks_per_game":1.8,"to_per_game":1.4},
    "Louisiana":     {"QB":"Ben Wooldridge",     "RB":"Montrell Johnson Jr","WR":"Kyren Lacy",
                      "pass_yds":248,"rush_yds":168,"points_per_game":28.8,"def_rank":33,"sacks_per_game":1.9,"to_per_game":1.3},
    "Troy":          {"QB":"Jacob Free",         "RB":"Kimani Vidal",       "WR":"Jabre Barber",
                      "pass_yds":214,"rush_yds":158,"points_per_game":23.4,"def_rank":39,"sacks_per_game":1.7,"to_per_game":1.6},
    "Arkansas State":{"QB":"James Blackman",     "RB":"Lincoln Pare",       "WR":"Corey Rucker",
                      "pass_yds":228,"rush_yds":142,"points_per_game":23.4,"def_rank":41,"sacks_per_game":1.7,"to_per_game":1.6},
    "Louisiana Monroe":{"QB":"Colby Suits",      "RB":"Josh Johnson",       "WR":"Marcus Williams Jr",
                      "pass_yds":214,"rush_yds":138,"points_per_game":20.8,"def_rank":47,"sacks_per_game":1.5,"to_per_game":1.8},
    "Southern Miss": {"QB":"Trey Lowe III",      "RB":"Frank Gore Jr",      "WR":"Jason Brownlee",
                      "pass_yds":218,"rush_yds":142,"points_per_game":20.4,"def_rank":47,"sacks_per_game":1.5,"to_per_game":1.8},
    "Texas State":   {"QB":"Jordan McCloud",     "RB":"Jahmyl Jeter",       "WR":"Javen Banks",
                      "pass_yds":228,"rush_yds":158,"points_per_game":24.4,"def_rank":39,"sacks_per_game":1.7,"to_per_game":1.5},
    # ── MAC ──────────────────────────────────────────────────────────────────
    "Toledo":        {"QB":"Tucker Gleason",     "RB":"Peny Boone",         "WR":"Devin Maddox",
                      "pass_yds":234,"rush_yds":168,"points_per_game":29.4,"def_rank":27,"sacks_per_game":2.1,"to_per_game":1.3},
    "Miami (OH)":    {"QB":"Brett Gabbert",      "RB":"Kevin Davis",        "WR":"Mac Hippenhammer",
                      "pass_yds":228,"rush_yds":148,"points_per_game":25.4,"def_rank":33,"sacks_per_game":1.9,"to_per_game":1.4},
    "Bowling Green": {"QB":"Connor Bazelak",     "RB":"Harold Fannin Jr",   "WR":"Odieu Hiliare",
                      "pass_yds":224,"rush_yds":138,"points_per_game":24.8,"def_rank":37,"sacks_per_game":1.8,"to_per_game":1.5},
    "Ohio":          {"QB":"Kurtis Rourke",      "RB":"Sieh Bangura",       "WR":"Sam Wiglusz",
                      "pass_yds":228,"rush_yds":152,"points_per_game":24.4,"def_rank":36,"sacks_per_game":1.8,"to_per_game":1.5},
    "Northern Illinois":{"QB":"Rocky Lombardi",  "RB":"Antario Brown",      "WR":"Cole Tucker",
                      "pass_yds":218,"rush_yds":154,"points_per_game":23.8,"def_rank":38,"sacks_per_game":1.8,"to_per_game":1.5},
    "Central Michigan":{"QB":"Jase Bauer",       "RB":"Lew Nichols III",    "WR":"Dallas Dixon",
                      "pass_yds":224,"rush_yds":162,"points_per_game":24.4,"def_rank":39,"sacks_per_game":1.7,"to_per_game":1.5},
    "Eastern Michigan":{"QB":"Preston Hutchinson","RB":"Darius Boone Jr",   "WR":"Dylan Drummond",
                      "pass_yds":214,"rush_yds":148,"points_per_game":22.4,"def_rank":46,"sacks_per_game":1.6,"to_per_game":1.7},
    "Ball State":    {"QB":"John Paddock",       "RB":"Carson Steele",      "WR":"Yo'Heinz Tyler",
                      "pass_yds":214,"rush_yds":148,"points_per_game":21.4,"def_rank":44,"sacks_per_game":1.6,"to_per_game":1.7},
    "Western Michigan":{"QB":"Treyson Bourguet", "RB":"Sean Tyler",         "WR":"Corey Crooms",
                      "pass_yds":224,"rush_yds":148,"points_per_game":22.8,"def_rank":44,"sacks_per_game":1.6,"to_per_game":1.6},
    "Akron":         {"QB":"Ben Finley",         "RB":"Teon Dollard",       "WR":"Shocky Jacques-Louis",
                      "pass_yds":208,"rush_yds":128,"points_per_game":18.4,"def_rank":50,"sacks_per_game":1.4,"to_per_game":1.9},
    "Buffalo":       {"QB":"Cole Snyder",        "RB":"Kevin Marks Jr",     "WR":"Tyrone Broden",
                      "pass_yds":208,"rush_yds":138,"points_per_game":19.8,"def_rank":45,"sacks_per_game":1.6,"to_per_game":1.8},
    "Kent State":    {"QB":"Dustin Crum",        "RB":"Marquez Cooper",     "WR":"Dante Wright",
                      "pass_yds":208,"rush_yds":132,"points_per_game":19.4,"def_rank":51,"sacks_per_game":1.4,"to_per_game":1.9},
    "UMass":         {"QB":"Taisun Phommachanh", "RB":"Ellis Merriweather", "WR":"Kevaughn Dingle",
                      "pass_yds":198,"rush_yds":118,"points_per_game":17.4,"def_rank":52,"sacks_per_game":1.3,"to_per_game":2.0},
    "Eastern Michigan":{"QB":"Preston Hutchinson","RB":"Darius Boone Jr",   "WR":"Dylan Drummond",
                      "pass_yds":214,"rush_yds":148,"points_per_game":22.4,"def_rank":46,"sacks_per_game":1.6,"to_per_game":1.7},
    # ── CUSA / Independents ───────────────────────────────────────────────────
    "Liberty":       {"QB":"Kaidon Salter",      "RB":"Quinton Cooley",     "WR":"Treon Sibley",
                      "pass_yds":258,"rush_yds":158,"points_per_game":30.4,"def_rank":33,"sacks_per_game":1.9,"to_per_game":1.3},
    "WKU":           {"QB":"Austin Reed",        "RB":"Malachi Corley",     "WR":"Malachi Corley",
                      "pass_yds":294,"rush_yds":132,"points_per_game":29.4,"def_rank":36,"sacks_per_game":1.8,"to_per_game":1.4},
    "MTSU":          {"QB":"Nicholas Vattiato",  "RB":"Frank Peasant",      "WR":"Jaylin Lane",
                      "pass_yds":224,"rush_yds":138,"points_per_game":23.4,"def_rank":41,"sacks_per_game":1.6,"to_per_game":1.6},
    "UTEP":          {"QB":"Gavin Hardison",     "RB":"Deion Hankins",      "WR":"Jacob Cowing",
                      "pass_yds":218,"rush_yds":132,"points_per_game":20.4,"def_rank":47,"sacks_per_game":1.5,"to_per_game":1.8},
    "FIU":           {"QB":"Grayson James",      "RB":"Lexington Joseph",   "WR":"Rivaldo Fairweather",
                      "pass_yds":204,"rush_yds":128,"points_per_game":17.4,"def_rank":52,"sacks_per_game":1.4,"to_per_game":2.0},
    "Sam Houston":   {"QB":"Eric Schmid",        "RB":"Ramon Jefferson",    "WR":"Noah Smith",
                      "pass_yds":228,"rush_yds":158,"points_per_game":25.4,"def_rank":38,"sacks_per_game":1.8,"to_per_game":1.5},
    "Kennesaw State":{"QB":"Xavier Shepherd",    "RB":"Marcus Carroll",     "WR":"Bryson Armstrong",
                      "pass_yds":218,"rush_yds":162,"points_per_game":24.4,"def_rank":37,"sacks_per_game":1.8,"to_per_game":1.5},
    "Jacksonville State":{"QB":"Zion Webb",      "RB":"Ahmad Edwards",      "WR":"Kalib Burke",
                      "pass_yds":212,"rush_yds":148,"points_per_game":22.4,"def_rank":39,"sacks_per_game":1.7,"to_per_game":1.6},
}

def get_player_data(team: str, team_db: dict | None = None) -> dict:
    """
    Return player data for a team. If not in PLAYER_DB, build an estimate
    from team_db (TEAM_DB passed in from the caller) so we never show zeroes
    and never need to import the main app module (avoids circular imports).
    """
    if team in PLAYER_DB:
        return PLAYER_DB[team]
    # Use caller-supplied TEAM_DB snapshot if available
    db = (team_db or {}).get(team)
    if db:
        sp, off_rank, def_rank = db[0], db[1], db[2]
        ppg      = max(16,  42  - off_rank * 0.38)
        pass_yds = max(160, 320 - off_rank * 0.9)
        rush_yds = max(90,  200 - off_rank * 0.5)
        sacks    = max(1.2, 3.4 - def_rank * 0.02)
        to       = min(2.0, 0.7 + def_rank * 0.015)
        return {
            "QB": f"{team} QB", "RB": f"{team} RB", "WR": f"{team} WR",
            "pass_yds": round(pass_yds), "rush_yds": round(rush_yds),
            "points_per_game": round(ppg, 1),
            "def_rank": def_rank, "sacks_per_game": round(sacks, 1),
            "to_per_game": round(to, 1),
        }
    # Last resort generic
    return {
        "QB": f"{team} QB", "RB": f"{team} RB", "WR": f"{team} WR",
        "pass_yds": 220, "rush_yds": 145, "points_per_game": 23.0,
        "def_rank": 45, "sacks_per_game": 1.6, "to_per_game": 1.6,
    }

# ── VENUE → LAT/LON for weather ─────────────────────────────────────────────
VENUE_COORDS = {
    # Domes / covered — no weather impact
    "Mercedes-Benz Stadium":       None,
    "Lucas Oil Stadium":           None,
    "AT&T Stadium":                None,
    "Caesars Superdome":           None,
    "Ford Field":                  None,
    "Allegiant Stadium":           None,
    "Tropicana Field":             None,
    "Dome at America's Center":    None,
    # Outdoor venues
    "Notre Dame Stadium, South Bend IN":   (41.698, -86.235),
    "Bryant-Denny Stadium":               (33.208, -87.551),
    "Ohio Stadium":                       (40.001, -83.019),
    "Michigan Stadium":                   (42.266, -83.749),
    "Sanford Stadium":                    (33.949, -83.373),
    "Memorial Stadium, Lincoln NE":       (40.820, -96.705),
    "Kinnick Stadium":                    (41.658, -91.550),
    "Beaver Stadium":                     (40.812, -77.856),
    "Memorial Stadium, Champaign IL":     (40.099, -88.237),
    "Ryan Field, Evanston IL":            (42.060, -87.668),
    "Camp Randall Stadium":               (43.070, -89.412),
    "Ross-Ade Stadium":                   (40.457, -86.924),
    "Spartan Stadium":                    (42.728, -84.480),
    "Rice-Eccles Stadium, Salt Lake City UT": (40.760, -111.847),
    "LaVell Edwards Stadium":             (40.257, -111.654),
    "Albertsons Stadium, Boise ID":       (43.602, -116.200),
    "Carter-Finley Stadium, Raleigh NC":  (35.863, -78.722),
    "Tiger Stadium":                      (30.412, -91.183),
    "Darrell K Royal Stadium":            (30.284, -97.732),
    "Kyle Field, College Station TX":     (30.610, -96.341),
    "Jordan-Hare Stadium, Auburn AL":     (32.601, -85.489),
    "Neyland Stadium":                    (35.955, -83.925),
    "Williams-Brice Stadium, Columbia SC":(33.999, -81.020),
    "FAU Stadium, Boca Raton FL":         (26.376, -80.104),
    "Gerald J. Ford Stadium, Dallas TX":  (32.841, -96.783),
    "Michie Stadium, West Point NY":      (41.392, -73.958),
    "Navy-Marine Corps Memorial Stadium, Annapolis MD": (38.983, -76.480),
    "Arizona Stadium, Tucson AZ":         (32.229, -110.949),
    "David Booth Kansas Memorial Stadium, Lawrence KS": (38.954, -95.253),
    "Bill Snyder Family Stadium, Manhattan KS": (39.205, -96.595),
    "McLane Stadium, Waco TX":            (31.558, -97.117),
    "TDECU Stadium, Houston TX":          (29.721, -95.399),
}

def _get_coords(venue: str):
    """Try exact then partial match against VENUE_COORDS."""
    if not venue:
        return None
    if venue in VENUE_COORDS:
        return VENUE_COORDS[venue]
    for k, v in VENUE_COORDS.items():
        if k in venue or venue in k:
            return v
    return None

# ── WEATHER ─────────────────────────────────────────────────────────────────
def fetch_game_weather(venue: str, game_date_str: str) -> dict:
    """
    Return weather dict for an outdoor venue.
    Uses Open-Meteo (free, no key needed).
    game_date_str: YYYY-MM-DD  (kickoff date in local time)
    """
    result = {"available": False, "dome": False, "error": None}

    # Dome check
    for dome_kw in ("Dome","Superdome","Stadium, Atlanta","Indoor","Ford Field",
                    "Lucas Oil","Allegiant","AT&T Stadium","Tropicana","Caesars"):
        if dome_kw.lower() in venue.lower():
            result["dome"] = True
            result["available"] = False
            result["condition"] = "Indoor/Dome — no weather impact"
            return result

    coords = _get_coords(venue)
    if not coords:
        result["error"] = "Venue coords unknown"
        return result

    lat, lon = coords
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,"
            f"windspeed_10m_max,weathercode"
            f"&temperature_unit=fahrenheit&windspeed_unit=mph"
            f"&timezone=America%2FNew_York"
            f"&start_date={game_date_str}&end_date={game_date_str}"
        )
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        d = r.json().get("daily", {})
        if not d.get("temperature_2m_max"):
            result["error"] = "No forecast data for date"
            return result

        hi   = d["temperature_2m_max"][0]
        lo   = d["temperature_2m_min"][0]
        wind = d["windspeed_10m_max"][0]
        precip = d["precipitation_sum"][0]
        wcode  = d["weathercode"][0]

        # WMO weather code → description
        cond_map = {
            0:"Clear",1:"Mainly clear",2:"Partly cloudy",3:"Overcast",
            45:"Fog",48:"Icy fog",51:"Light drizzle",53:"Drizzle",
            55:"Heavy drizzle",61:"Light rain",63:"Rain",65:"Heavy rain",
            71:"Light snow",73:"Snow",75:"Heavy snow",
            77:"Snow grains",80:"Rain showers",81:"Rain showers",
            82:"Heavy rain showers",85:"Snow showers",86:"Heavy snow showers",
            95:"Thunderstorm",96:"Thunderstorm w/ hail",99:"Thunderstorm w/ heavy hail",
        }
        cond = cond_map.get(wcode, f"Code {wcode}")

        # Compute impact on scoring (pts lost due to weather)
        pts_impact = 0.0
        wind_note = ""
        precip_note = ""
        cold_note = ""

        if wind >= 30:
            pts_impact += 6.0; wind_note = f"🌬️ {wind:.0f}mph winds — significant passing game impact"
        elif wind >= 20:
            pts_impact += 3.0; wind_note = f"💨 {wind:.0f}mph winds — moderate passing impact"
        elif wind >= 14:
            pts_impact += 1.5; wind_note = f"💨 {wind:.0f}mph winds — slight passing impact"

        if precip >= 0.5:
            pts_impact += 4.0; precip_note = f"🌧️ {precip:.1f}\" precip — wet ball, reduced passing/kicking"
        elif precip >= 0.2:
            pts_impact += 2.0; precip_note = f"🌦️ {precip:.1f}\" precip — some impact on footing"

        if lo <= 20:
            pts_impact += 4.0; cold_note = f"🥶 Low {lo:.0f}°F — extreme cold, major scoring suppressor"
        elif lo <= 32:
            pts_impact += 2.5; cold_note = f"🌡️ Low {lo:.0f}°F — cold game, lean under"
        elif lo <= 40:
            pts_impact += 1.0; cold_note = f"🌡️ Low {lo:.0f}°F — cool but manageable"

        ou_adj = -round(pts_impact * 2) / 2  # subtract from total
        notes = [n for n in [wind_note, precip_note, cold_note] if n]

        result.update({
            "available": True,
            "hi": hi, "lo": lo,
            "wind": wind,
            "precip": precip,
            "condition": cond,
            "pts_impact": pts_impact,
            "ou_adj": ou_adj,
            "notes": notes,
            "summary": f"{cond}, {lo:.0f}–{hi:.0f}°F, {wind:.0f}mph wind, {precip:.2f}\" precip",
        })
    except Exception as exc:
        result["error"] = str(exc)[:80]

    return result

# ── INJURIES ─────────────────────────────────────────────────────────────────
def fetch_injuries(team_espn_id: str) -> list[dict]:
    """Fetch ESPN injury report for a team. Returns list of player dicts."""
    try:
        url = (
            f"https://site.api.espn.com/apis/site/v2/sports/football/"
            f"college-football/teams/{team_espn_id}/injuries"
        )
        r = requests.get(url, headers=HEADS, timeout=8)
        if r.status_code != 200:
            return []
        data = r.json()
        players = []
        for item in data.get("injuries", []):
            athlete = item.get("athlete", {})
            pos = athlete.get("position", {}).get("abbreviation", "?")
            name = athlete.get("displayName", "Unknown")
            status = item.get("status", "Unknown")
            detail = item.get("shortComment", item.get("longComment", ""))
            players.append({
                "name": name, "pos": pos, "status": status, "detail": detail,
                "impact": _injury_impact(pos, status),
            })
        return players
    except Exception:
        return []

def fetch_team_espn_id(team_name: str) -> str | None:
    """Look up ESPN team ID from team name."""
    ESPN_IDS = {
        "Miami": "2390", "Georgia": "61", "Utah": "254", "Notre Dame": "87",
        "UCLA": "26", "Indiana": "84", "BYU": "252", "Kentucky": "96",
        "Alabama": "333", "Texas": "251", "Ohio State": "194", "Ole Miss": "145",
        "Texas Tech": "2641", "Wake Forest": "154", "LSU": "99",
        "Tennessee": "2633", "Houston": "248", "USC": "30", "Missouri": "142",
        "Boise State": "68", "Iowa": "2294", "New Mexico": "167",
        "South Carolina": "2579", "Arizona": "12", "Florida": "57",
        "Oregon": "2483", "Penn State": "213", "Michigan": "130",
        "Clemson": "228", "Texas A&M": "245", "Wisconsin": "275",
        "TCU": "2628", "Colorado": "38", "Iowa State": "66",
        "Kansas State": "2306", "Auburn": "2", "Arkansas": "8",
        "Virginia Tech": "259", "NC State": "152", "Georgia Tech": "59",
        "Louisville": "97", "Pittsburgh": "221", "Duke": "150",
        "Syracuse": "183", "SMU": "2567", "UNLV": "2439",
        "Fresno State": "278", "Air Force": "2005", "Army": "349",
        "Navy": "2426", "James Madison": "256", "Nebraska": "158",
        "Illinois": "356", "Northwestern": "77", "Minnesota": "135",
        "Washington": "264", "Vanderbilt": "238", "Florida State": "52",
        "Miami (OH)": "193", "Toledo": "2649", "Tulane": "2655",
        "Memphis": "235", "North Carolina": "153", "Boston College": "103",
        "Louisville": "97", "Georgia State": "2247", "South Alabama": "6",
        "UTSA": "2636", "Florida Atlantic": "2226",
    }
    return ESPN_IDS.get(team_name)

def _injury_impact(pos: str, status: str) -> float:
    """Estimate point-impact of injured player."""
    # Status weights
    sw = {"Out": 1.0, "Doubtful": 0.75, "Questionable": 0.40,
          "Probable": 0.10, "Day-To-Day": 0.30}.get(status, 0.0)
    # Position impact (pts per game contribution)
    pw = {"QB": 8.0, "RB": 3.5, "WR": 2.5, "TE": 2.0,
          "OL": 2.5, "DE": 2.5, "DT": 1.5, "LB": 2.0,
          "CB": 2.0, "S": 1.5, "K": 1.5, "P": 0.5}.get(pos, 1.0)
    return round(sw * pw, 2)

def get_team_injuries(away: str, home: str) -> dict:
    """Fetch injuries for both teams. Returns {team: [player_dict, ...]}"""
    result = {}
    for team in [away, home]:
        eid = fetch_team_espn_id(team)
        if eid:
            players = fetch_injuries(eid)
            if players:
                result[team] = players
    return result

# ── MATCHUP ANALYSIS ─────────────────────────────────────────────────────────
def player_vs_player(away: str, home: str) -> list[str]:
    """
    Generate key player-vs-player matchup narratives.
    Returns list of strings for display.
    """
    adb = get_player_data(away)
    hdb = get_player_data(home)
    matchups = []

    # QB duel
    aqb = adb.get("QB", "QB"); hqb = hdb.get("QB", "QB")
    apyds = adb.get("pass_yds", 0); hpyds = hdb.get("pass_yds", 0)
    qb_edge = away if apyds > hpyds + 20 else (home if hpyds > apyds + 20 else None)
    matchups.append(
        f"🎯 QB: {aqb} ({apyds:.0f} pass yds/g) vs {hqb} ({hpyds:.0f} pass yds/g)"
        + (f" — edge {qb_edge}" if qb_edge else " — even")
    )

    # RB vs opposing front
    arb = adb.get("RB", "RB"); hrb = hdb.get("RB", "RB")
    aryds = adb.get("rush_yds", 0); hryds = hdb.get("rush_yds", 0)
    a_def = hdb.get("def_rank", 50); h_def = adb.get("def_rank", 50)
    rb_away_edge = aryds > 170 and a_def > 25
    rb_home_edge = hryds > 170 and h_def > 25
    matchups.append(
        f"🏃 RB: {arb} ({aryds:.0f} rush yds/g) vs {home} D-rank #{a_def}"
        + (" — favorable matchup" if rb_away_edge else "")
    )
    matchups.append(
        f"🏃 RB: {hrb} ({hryds:.0f} rush yds/g) vs {away} D-rank #{h_def}"
        + (" — favorable matchup" if rb_home_edge else "")
    )

    # Pass rush vs QB
    a_sacks = adb.get("sacks_per_game", 0); h_sacks = hdb.get("sacks_per_game", 0)
    if h_sacks >= 3.0:
        matchups.append(f"🔥 {home} pass rush ({h_sacks:.1f} sacks/g) — threatens {aqb}")
    if a_sacks >= 3.0:
        matchups.append(f"🔥 {away} pass rush ({a_sacks:.1f} sacks/g) — threatens {hqb}")

    # Turnover battle
    ato = adb.get("to_per_game", 0); hto = hdb.get("to_per_game", 0)
    if ato > hto + 0.3:
        matchups.append(f"⚠️ Turnover risk: {away} ({ato:.1f} TO/g) vs {home} ({hto:.1f} TO/g) — {home} benefits")
    elif hto > ato + 0.3:
        matchups.append(f"⚠️ Turnover risk: {home} ({hto:.1f} TO/g) vs {away} ({ato:.1f} TO/g) — {away} benefits")

    return matchups

def player_vs_team(away: str, home: str) -> list[str]:
    """
    Key player-vs-team matchup angles.
    Returns list of narrative strings.
    """
    adb = get_player_data(away)
    hdb = get_player_data(home)
    angles = []

    aqb = adb.get("QB", "QB"); arb = adb.get("RB", "RB")
    hqb = hdb.get("QB", "QB"); hrb = hdb.get("RB", "RB")

    # Away QB vs home defense
    h_def_rank = hdb.get("def_rank", 50)
    a_pass = adb.get("pass_yds", 0)
    if h_def_rank <= 10 and a_pass > 270:
        angles.append(f"📌 {aqb} faces elite {home} D (#{h_def_rank}) — expect lower completion rate, key matchup to watch")
    elif h_def_rank >= 30 and a_pass > 250:
        angles.append(f"📌 {aqb} attacks weak {home} pass D (#{h_def_rank}) — high ceiling for {away} passing game")

    # Home QB vs away defense
    a_def_rank = adb.get("def_rank", 50)
    h_pass = hdb.get("pass_yds", 0)
    if a_def_rank <= 10 and h_pass > 270:
        angles.append(f"📌 {hqb} faces elite {away} D (#{a_def_rank}) — potential containment game")
    elif a_def_rank >= 30 and h_pass > 250:
        angles.append(f"📌 {hqb} exploits weak {away} D (#{a_def_rank}) — home offense should open up")

    # RB angle
    h_sacks = hdb.get("sacks_per_game", 0)
    a_rush = adb.get("rush_yds", 0)
    if h_sacks >= 2.8 and a_rush < 150:
        angles.append(f"📌 {home} pressure forces {away} into passing downs — {arb} role may shrink")
    elif a_rush >= 190:
        angles.append(f"📌 {arb} ground attack ({a_rush:.0f} yds/g) — controls clock, keeps {hqb} off field")

    a_sacks = adb.get("sacks_per_game", 0)
    h_rush = hdb.get("rush_yds", 0)
    if a_sacks >= 2.8 and h_rush < 150:
        angles.append(f"📌 {away} pressure forces {home} into passing downs — pace speeds up")
    elif h_rush >= 190:
        angles.append(f"📌 {hrb} ground game ({h_rush:.0f} yds/g) — eats clock, limits {away} possessions")

    return angles

def team_vs_team(away: str, home: str, p: dict) -> list[str]:
    """
    Team-level matchup narratives using prediction data + PLAYER_DB.
    Returns list of narrative strings.
    """
    adb = get_player_data(away)
    hdb = get_player_data(home)
    angles = []

    ppg_a = adb.get("points_per_game", 28)
    ppg_h = hdb.get("points_per_game", 28)
    sp_gap = p.get("sp_gap", 0)
    fa = p.get("fa", False)
    fav = away if fa else home
    dog = home if fa else away

    if ppg_a > ppg_h + 6:
        angles.append(f"⚡ {away} scores {ppg_a:.1f} ppg vs {home} at {ppg_h:.1f} — major offensive edge")
    elif ppg_h > ppg_a + 6:
        angles.append(f"⚡ {home} scores {ppg_h:.1f} ppg vs {away} at {ppg_a:.1f} — home offensive edge")
    else:
        angles.append(f"⚡ Scoring: {away} {ppg_a:.1f} ppg vs {home} {ppg_h:.1f} ppg — balanced offenses")

    h_def = hdb.get("def_rank", 50); a_def = adb.get("def_rank", 50)
    if h_def < a_def - 5:
        angles.append(f"🛡️ {home} D (#{h_def}) significantly better than {away} D (#{a_def}) — tilt toward {home}")
    elif a_def < h_def - 5:
        angles.append(f"🛡️ {away} D (#{a_def}) significantly better than {home} D (#{h_def}) — road team controls game")

    if sp_gap > 15:
        angles.append(f"📊 Model dominance: {fav} holds +{sp_gap:.1f} rating gap — rare to cover, line likely accurate")
    elif sp_gap > 8:
        angles.append(f"📊 Clear favorite: {fav} +{sp_gap:.1f} edge — but check closing line for sharp movement")
    elif sp_gap < 3:
        angles.append(f"📊 Pick'em territory: {sp_gap:.1f} gap — home field and matchup determine outcome")

    total = p.get("total", 48)
    ou = p.get("ou", "OVER")
    angles.append(f"📈 Projected total {total} pts — model leans {ou} (PPG avg: {(ppg_a+ppg_h)/2:.1f})")

    return angles

def injury_adjustment(injuries: dict, p: dict, away: str, home: str) -> tuple[dict, list[str]]:
    """
    Apply injury impacts to prediction. Returns (adjusted_p, injury_notes).
    """
    if not injuries:
        return p, []

    p = dict(p)
    notes = []

    for team, players in injuries.items():
        impact = sum(pl["impact"] for pl in players)
        key_outs = [pl for pl in players if pl["status"] == "Out" and pl["pos"] == "QB"]

        if impact == 0:
            continue

        # Adjust projected scores
        if team == away:
            p["pa"] = max(0, p.get("pa", 21) - impact)
            if impact >= 6:
                p["sp_away"] = p.get("sp_away", 0) - impact * 0.5
                p["sp_home"] = p.get("sp_home", 0) + impact * 0.5
        else:
            p["ph"] = max(0, p.get("ph", 21) - impact)
            if impact >= 6:
                p["sp_home"] = p.get("sp_home", 0) - impact * 0.5
                p["sp_away"] = p.get("sp_away", 0) + impact * 0.5

        # Adjust total
        p["total"] = max(20, round((p.get("pa", 21) + p.get("ph", 21)) * 2) / 2)

        # Confidence penalty
        if impact >= 8:
            p["mlC"] = max(0, p.get("mlC", 60) - 10)
            p["spC"] = max(0, p.get("spC", 55) - 8)

        # Build notes
        out_count = sum(1 for pl in players if pl["status"] == "Out")
        doubt_count = sum(1 for pl in players if pl["status"] == "Doubtful")
        ques_count = sum(1 for pl in players if pl["status"] == "Questionable")
        status_parts = []
        if out_count: status_parts.append(f"{out_count} OUT")
        if doubt_count: status_parts.append(f"{doubt_count} Doubtful")
        if ques_count: status_parts.append(f"{ques_count} Questionable")

        if key_outs:
            notes.append(f"🚨 {team} QB {key_outs[0]['name']} — OUT ({key_outs[0]['detail']}) — massive pick impact")
            p["mlC"] = max(0, p.get("mlC", 60) - 20)
        elif status_parts:
            notes.append(f"🩺 {team}: {', '.join(status_parts)} — injury impact est. {impact:.1f} pts")

    return p, notes

def weather_adjustment(weather: dict, p: dict) -> tuple[dict, str]:
    """
    Apply weather to total prediction. Returns (adjusted_p, weather_note).
    """
    if not weather.get("available") or weather.get("dome"):
        return p, ""

    p = dict(p)
    adj = weather.get("ou_adj", 0)
    if adj < 0:
        p["total"] = max(20, p.get("total", 48) + adj)
        old_ou = p.get("ou", "OVER")
        # Recalculate O/U lean after weather adjustment
        if p["total"] < 44 and adj <= -4:
            p["ou"] = "UNDER"
        note = f"🌤️ Weather: {weather['summary']} — total adjusted {adj:+.1f} pts → {p['ou']} {p['total']}"
    else:
        note = f"🌤️ Weather: {weather['summary']} — no scoring impact"

    return p, note

# ── FULL RESEARCH BUNDLE ─────────────────────────────────────────────────────
def research_game(away: str, home: str, venue: str, game_date: str, p: dict) -> dict:
    """
    Run full research for one game. Returns enriched dict with:
      pvp, pvt, tvt, injuries, weather, adj_p
    game_date: YYYY-MM-DD
    """
    pvp = player_vs_player(away, home)
    pvt = player_vs_team(away, home)
    tvt = team_vs_team(away, home, p)

    injuries = get_team_injuries(away, home)
    p_adj, inj_notes = injury_adjustment(injuries, p, away, home)

    weather = fetch_game_weather(venue, game_date)
    p_adj, wx_note = weather_adjustment(weather, p_adj)

    return {
        "pvp": pvp,
        "pvt": pvt,
        "tvt": tvt,
        "injuries": injuries,
        "inj_notes": inj_notes,
        "weather": weather,
        "wx_note": wx_note,
        "adj_p": p_adj,
    }
