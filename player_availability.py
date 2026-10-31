"""Render sourced key-player availability without inventing a starting lineup."""
import datetime as dt
import re
import unicodedata
from html import escape
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")

def norm_player(value):
    value = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode().casefold()
    return " ".join(re.findall(r"[a-z0-9]+", value))

KEY_POSITIONS = {"QB", "RB", "WR"}
STATUS_LABELS = {
    "Out": "OUT · report says will not play",
    "Doubtful": "Doubtful · not confirmed",
    "Questionable": "Questionable · not confirmed",
    "Probable": "Probable · not a lineup confirmation",
    "Game Time Decision": "Game-time decision · not confirmed",
    "Game-Time Decision": "Game-time decision · not confirmed",
    "GTD": "Game-time decision · not confirmed",
    "Available": "Available · not a lineup confirmation",
    "Not listed": "Not listed · status unknown",
    "Active": "Availability not confirmed by lineup",
}

def game_date_et(game):
    try:
        kickoff = dt.datetime.fromisoformat(game["kickoff"].replace("Z", "+00:00"))
        return kickoff.astimezone(ET).date().isoformat()
    except (KeyError, ValueError, TypeError):
        return ""

def render_key_player_status(game, rows, star_players=None, now=None):
    """Show each team's QB, RB, and WR season leader availability."""
    now = now or dt.datetime.now(dt.timezone.utc)
    game_date = game_date_et(game)
    teams = (game.get("away", ""), game.get("home", ""))
    star_players = star_players or {}
    relevant = [r for r in rows
                if r.get("Team") in teams
                and r.get("Game date") == game_date
                and str(r.get("Position", "")).upper() in KEY_POSITIONS]
    by_player = {(r.get("Team"), norm_player(r.get("Player", "")),
                  str(r.get("Position", "")).upper()): r for r in relevant}
    esc = escape
    heading = ("<div style='font-weight:700;color:#f59e0b;margin-bottom:5px'>"
               "STAR PLAYERS · QB / RB / WR</div>")
    note = ("<div style='color:#94a3b8;font-size:12px;margin-bottom:6px'>"
            "Showing each team's season leader at QB, RB, and WR. Check the current report before treating a player as ready; projections and depth charts do not confirm participation. "
            "<a href='https://cfbfantasyzone.com/depth-charts' target='_blank'>CFB Fantasy Zone depth charts</a> · "
            "<a href='https://www.on3.com/news/' target='_blank'>On3 news</a> · "
            "<a href='https://cfbvibes.com/injuries/' target='_blank'>CFB Vibes injury reports</a> · "
            "<a href='https://draftedge.com/cfb/' target='_blank'>DraftEdge projections</a> · "
            "<a href='https://kickoffstatus.com/' target='_blank'>Kickoff Status reports</a>.</div>")
    items = []
    for team in teams:
        leaders = star_players.get(team, {})
        for pos in ("QB", "RB", "WR"):
            player = leaders.get(pos)
            if not player:
                continue
            player_name = player.get("name", "") if isinstance(player, dict) else str(player)
            row = by_player.get((team, norm_player(player_name), pos))
            stamp_label = "availability unknown"
            if row:
                status = str(row.get("Status", "Not listed"))
                label = STATUS_LABELS.get(status, "Status unknown")
                checked = str(row.get("Checked UTC", "")).strip()
                fresh = False
                if checked:
                    try:
                        stamp = dt.datetime.fromisoformat(checked.replace("Z", "+00:00"))
                        if stamp.tzinfo is None:
                            stamp = stamp.replace(tzinfo=dt.timezone.utc)
                        age = now - stamp.astimezone(dt.timezone.utc)
                        fresh = 0 <= age.total_seconds() <= 24 * 3600
                        stamp_label = stamp.astimezone(ET).strftime("%b %-d %I:%M %p ET")
                        if not fresh:
                            stamp_label += " · older than 24h or future-dated"
                    except ValueError:
                        stamp_label = "report time unavailable"
                if status == "Out" and fresh:
                    playing = "NO · current report says OUT"
                else:
                    playing = "UNCONFIRMED · " + label
            else:
                playing = "UNCONFIRMED · no matching current report row"
            items.append("<div style='padding:3px 0;color:#e2e8f0'><b>" + esc(team) +
                         "</b> · " + esc(pos) + " · " + esc(player_name) +
                         " — <span style='color:#38bdf8'>Playing? " + esc(playing) + "</span>"
                         " <span style='color:#64748b'>· Starter? not confirmed · " + esc(stamp_label) + "</span></div>")
    if not items:
        items.append("<span style='color:#fbbf24'>Season statistical leaders were unavailable; no unverified player names shown.</span>")
    return ("<div style='padding:10px 18px;background:#0c1520;border-bottom:1px solid #1a2840;"
            "font-size:13px;line-height:1.5'>" + heading + note + "".join(items) + "</div>")
