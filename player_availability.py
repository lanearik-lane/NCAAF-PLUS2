"""Render sourced key-player availability without inventing a starting lineup."""
import datetime as dt
from html import escape
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
KEY_POSITIONS = {"QB", "RB", "WR", "TE", "OL", "OT", "OG", "C", "FB",
                 "DL", "DT", "DE", "EDG", "EDGE", "NT", "LB", "ILB",
                 "OLB", "MLB", "DB", "CB", "S", "FS", "SS"}
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

def render_key_player_status(game, rows, now=None):
    """Show reported key-position statuses for this matchup; never infer starts/snaps."""
    now = now or dt.datetime.now(dt.timezone.utc)
    game_date = game_date_et(game)
    teams = (game.get("away", ""), game.get("home", ""))
    relevant = [r for r in rows
                if r.get("Team") in teams
                and r.get("Game date") == game_date
                and str(r.get("Position", "")).upper() in KEY_POSITIONS]
    esc = escape
    heading = ("<div style='font-weight:700;color:#f59e0b;margin-bottom:5px'>"
               "KEY PLAYERS · AVAILABILITY</div>")
    note = ("<div style='color:#94a3b8;font-size:12px;margin-bottom:6px'>"
            "The source report does not identify starters or confirm snaps. "
            "Only a current OUT designation says a listed player will not play; "
            "available/probable does not confirm they will start. "
            "<a href='https://kickoffstatus.com/' target='_blank'>Kickoff Status report</a>.</div>")
    if not relevant:
        return ("<div style='padding:10px 18px;background:#0c1520;border-bottom:1px solid #1a2840;"
                "font-size:13px;line-height:1.5'>" + heading + note +
                "<span style='color:#fbbf24'>No matching player rows in the imported report. "
                "Starter and playing status: unknown.</span></div>")
    pos_order = {"QB": 0, "RB": 1, "WR": 2, "TE": 3, "OL": 4, "OT": 4,
                 "OG": 4, "C": 4, "FB": 4, "DL": 5, "DT": 5, "DE": 5,
                 "EDG": 5, "EDGE": 5, "NT": 5, "LB": 6, "ILB": 6, "OLB": 6,
                 "MLB": 6, "DB": 7, "CB": 7, "S": 7, "FS": 7, "SS": 7}
    relevant.sort(key=lambda r: (teams.index(r.get("Team")), pos_order.get(str(r.get("Position", "")).upper(), 9),
                                str(r.get("Player", "")).casefold()))
    items = []
    for row in relevant:
        status = str(row.get("Status", "Not listed"))
        label = STATUS_LABELS.get(status, "Status unknown")
        checked = str(row.get("Checked UTC", "")).strip()
        stamp_label = "report time unavailable"
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
                pass
        if status == "Out" and fresh:
            playing = "NO · current report says OUT"
        else:
            playing = "UNCONFIRMED · " + label
        pos = str(row.get("Position", "")).upper() or "—"
        items.append("<div style='padding:3px 0;color:#e2e8f0'><b>" + esc(str(row.get("Team", ""))) +
                     "</b> · " + esc(pos) + " · " + esc(str(row.get("Player", "")) or "Player not named") +
                     " — <span style='color:#38bdf8'>Playing? " + esc(playing) + "</span>"
                     " <span style='color:#64748b'>· Starter? not confirmed · " + esc(stamp_label) + "</span></div>")
    return ("<div style='padding:10px 18px;background:#0c1520;border-bottom:1px solid #1a2840;"
            "font-size:13px;line-height:1.5'>" + heading + note + "".join(items) + "</div>")
