"""Find each FBS team's current season statistical leader at QB, RB, and WR."""
import re
from concurrent.futures import ThreadPoolExecutor

import requests
import streamlit as st

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; NCAAFPlus2/1.0)", "Accept": "application/json"}
POSITION_BY_CATEGORY = (
    ("passing", "QB", {"QB", "QUARTERBACK"}),
    ("rushing", "RB", {"RB", "HB", "RUNNING BACK"}),
    ("receiving", "WR", {"WR", "WIDE RECEIVER"}),
)

def _position(value):
    if isinstance(value, dict):
        value = value.get("abbreviation") or value.get("displayName") or value.get("name") or ""
    value = str(value).upper().strip()
    if "QUARTERBACK" in value:
        return "QB"
    if "RUNNING BACK" in value or value in ("HB", "RB"):
        return "RB"
    if "WIDE RECEIVER" in value or value == "WR":
        return "WR"
    return value

def _walk_roster(node, result):
    if isinstance(node, dict):
        position = _position(node.get("position", ""))
        athlete_id = str(node.get("id", ""))
        name = node.get("fullName") or node.get("displayName")
        if athlete_id and name and position:
            result[athlete_id] = {"name": str(name), "position": position}
        for value in node.values():
            _walk_roster(value, result)
    elif isinstance(node, list):
        for value in node:
            _walk_roster(value, result)

@st.cache_data(ttl=3600, show_spinner=False)
def team_stars(team_id):
    """Return stat-category leaders only when ESPN roster confirms their positions."""
    team_id = str(team_id or "").strip()
    if not team_id:
        return {}
    base = "https://sports.core.api.espn.com/v2/sports/football/leagues/college-football"
    leaders_url = f"{base}/seasons/2026/types/2/teams/{team_id}/leaders?lang=en&region=us"
    roster_url = f"https://site.api.espn.com/apis/site/v2/sports/football/college-football/teams/{team_id}/roster"
    try:
        leader_response = requests.get(leaders_url, headers=HEADERS, timeout=8)
        leader_response.raise_for_status()
        roster_response = requests.get(roster_url, headers=HEADERS, timeout=8)
        roster_response.raise_for_status()
        payload = leader_response.json()
        roster_payload = roster_response.json()
    except (requests.RequestException, ValueError):
        return {}
    roster = {}
    _walk_roster(roster_payload, roster)
    categories = payload.get("categories", [])
    result = {}
    for category_key, output_position, accepted_positions in POSITION_BY_CATEGORY:
        category = next((c for c in categories
                         if category_key in str(c.get("name", "")).casefold()
                         or category_key in str(c.get("displayName", "")).casefold()), None)
        if not category:
            continue
        for leader in category.get("leaders", []):
            athlete = leader.get("athlete") or {}
            athlete_id = str(athlete.get("id", ""))
            if not athlete_id:
                ref = athlete.get("$ref", "")
                match = re.search(r"/athletes/(\d+)", ref)
                athlete_id = match.group(1) if match else ""
            roster_player = roster.get(athlete_id, {})
            if roster_player.get("position") not in accepted_positions:
                continue
            name = roster_player.get("name") or athlete.get("fullName") or athlete.get("displayName")
            if name:
                result[output_position] = {
                    "name": str(name),
                    "category": category.get("displayName", category_key),
                }
                break
    return result

def load_team_stars(games):
    """Fetch unique team leaders concurrently; cache each team's results for one hour."""
    teams = {}
    for game in games:
        if game.get("div") != "FBS":
            continue
        if game.get("away_id"):
            teams[game["away"]] = str(game["away_id"])
        if game.get("home_id"):
            teams[game["home"]] = str(game["home_id"])
    ids = sorted(set(teams.values()))
    if not ids:
        return {}
    with ThreadPoolExecutor(max_workers=8) as pool:
        values = list(pool.map(team_stars, ids))
    by_id = dict(zip(ids, values))
    return {name: by_id.get(team_id, {}) for name, team_id in teams.items()}
