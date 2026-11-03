"""Refresh hardrock_fl_games.json from ESPN's FBS schedule for the current week.

Pulls the full FBS game slate from ESPN (same source the app uses) for the
current week's Thursday–Saturday window, writes it in the format florida_board.py
expects, and commits + pushes to GitHub so the app filter stays current.

Designed to run nightly at 12:45 AM ET via scheduled task.
"""
import datetime as dt
import json
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

ET = ZoneInfo("America/New_York")
REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = REPO_ROOT / "data" / "hardrock_fl_games.json"

HEADERS = {"User-Agent": "NCAAF-PLUS2-HardRock-Refresh/1.0"}


def week_dates_for_today():
    """Return Monday of the current NCAA football week."""
    today = dt.date.today()
    # NCAA weeks run Mon–Sun; week 0 starts Mon Aug 24 2026
    season_start = dt.date(2026, 8, 24)
    delta = (today - season_start).days
    week_num = max(0, min(15, delta // 7))
    monday = season_start + dt.timedelta(weeks=week_num)
    return monday, monday + dt.timedelta(days=6)


def fetch_fbs_games(start: dt.date, end: dt.date) -> list[dict]:
    """Fetch FBS games from ESPN for each day in range."""
    games = {}
    for days_ahead in range((end - start).days + 1):
        day = start + dt.timedelta(days=days_ahead)
        try:
            r = requests.get(
                "https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard",
                params={"groups": "80", "dates": day.strftime("%Y%m%d"), "limit": 300},
                headers=HEADERS,
                timeout=15,
            )
            r.raise_for_status()
            for event in r.json().get("events", []):
                try:
                    comp = event["competitions"][0]
                    home = next(c for c in comp["competitors"] if c["homeAway"] == "home")
                    away = next(c for c in comp["competitors"] if c["homeAway"] == "away")
                    kickoff = dt.datetime.fromisoformat(event["date"].replace("Z", "+00:00"))
                    local = kickoff.astimezone(ET)
                    if not start <= local.date() <= end:
                        continue
                    # Format time like HardRock board: "Saturday, 3:30 pm EDT"
                    day_name = local.strftime("%A")
                    time_str = local.strftime("%-I:%M %p").lower() + " EDT"
                    matchup_time = f"{day_name}, {time_str}"
                    games[event["id"]] = {
                        "teams": [
                            away["team"]["displayName"],
                            home["team"]["displayName"],
                        ],
                        "time": matchup_time,
                    }
                except (KeyError, IndexError, StopIteration, ValueError):
                    continue
        except Exception as exc:
            print(f"Warning: ESPN fetch failed for {day}: {exc}", file=sys.stderr)

    return list(games.values())


def main():
    now_et = dt.datetime.now(ET)
    start, end = week_dates_for_today()

    print(f"Fetching FBS games {start} – {end} …")
    matchups = fetch_fbs_games(start, end)
    print(f"  Found {len(matchups)} games")

    payload = {
        "captured_at": now_et.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "source": "ESPN FBS scoreboard API (auto-refreshed nightly)",
        "week_start": start.isoformat(),
        "week_end": end.isoformat(),
        "matchups": matchups,
    }

    DATA_FILE.write_text(json.dumps(payload, indent=2))
    print(f"  Wrote {DATA_FILE}")
    return len(matchups)


if __name__ == "__main__":
    count = main()
    sys.exit(0 if count > 0 else 1)
