"""Hourly, polite refresh of public Kickoff Status game availability pages."""
import datetime as dt
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

ROOT = "https://kickoffstatus.com/"
DATA = Path(__file__).resolve().parents[1] / "data" / "kickoff_status_injuries.json"
UA = "NCAAF-PLUS2-Availability-Refresh/1.0 (hourly public report refresh)"
DATE_RE = re.compile(r"/games/(\d{4}-\d{2}-\d{2})-")
REPORT_RE = re.compile(r"posted\s+((?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+[A-Z][a-z]{2}\s+\d{1,2},\s+\d{1,2}:\d{2}\s+[AP]M)\s+PT", re.I)

def norm(value):
    return re.sub(r"[^a-z0-9]+", "", value.casefold())

def sides_from_title(title):
    title = re.sub(r"\s+Injury Report.*$", "", title, flags=re.I).strip()
    for sep in (" vs ", " at "):
        if sep in title:
            a, b = title.split(sep, 1)
            return a.strip(), b.strip()
    return "", ""

def report_page(session, url):
    response = session.get(url, timeout=25)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    h1 = soup.find("h1")
    title = h1.get_text(" ", strip=True) if h1 else url.rsplit("/", 2)[-2]
    sides = sides_from_title(title)
    if not all(sides):
        return None

    date_match = DATE_RE.search(urlparse(url).path)
    if not date_match:
        return None
    game_date = date_match.group(1)
    body_text = soup.get_text(" ", strip=True)
    report_match = REPORT_RE.search(body_text)
    reported = report_match.group(1) + " PT" if report_match else None
    no_report = "no report yet" in body_text.casefold() or "pending" in body_text.casefold()
    players = []
    for table in soup.find_all("table"):
        headers = [cell.get_text(" ", strip=True).casefold() for cell in table.find_all("th")]
        if not {"player", "pos", "status"}.issubset(set(headers)):
            continue
        team_heading = table.find_previous("h3")
        heading = team_heading.get_text(" ", strip=True) if team_heading else ""
        team = next((side for side in sides if norm(heading).startswith(norm(side))), None)
        if not team:
            continue
        for tr in table.find_all("tr"):
            cells = [cell.get_text(" ", strip=True) for cell in tr.find_all(["td", "th"])]
            if len(cells) < 3 or cells[0].casefold() == "player":
                continue
            player = re.sub(r"\s+#\d+\s*$", "", cells[0]).strip()
            position = cells[1].strip().upper()
            status = re.sub(r"\s+", " ", cells[2]).strip().title()
            if not player or status.casefold() in ("", "—", "-"):
                continue
            players.append({"team": team, "player": player, "position": position, "status": status})

    unique = {(p["team"], p["player"], p["position"]): p for p in players}
    coverage = "report" if unique or (report_match and not no_report) else "pending"
    return {
        "url": url,
        "game_date": game_date,
        "title": title,
        "reported": reported,
        "coverage": coverage,
        "players": sorted(unique.values(), key=lambda p: (norm(p["team"]), p["position"], norm(p["player"]))),
    }

def core(snapshot):
    return json.dumps(snapshot.get("games", []), sort_keys=True, ensure_ascii=False)

def main():
    existing = json.loads(DATA.read_text(encoding="utf-8"))
    today = dt.datetime.now(dt.timezone.utc).date()
    session = requests.Session()
    session.headers.update({"User-Agent": UA, "Accept": "text/html,application/xhtml+xml"})
    response = session.get(ROOT, timeout=25)
    response.raise_for_status()
    home = BeautifulSoup(response.text, "html.parser")
    urls = set()
    for a in home.find_all("a", href=True):
        link = urljoin(ROOT, a["href"])
        match = DATE_RE.search(urlparse(link).path)
        if not match or urlparse(link).netloc != urlparse(ROOT).netloc:
            continue
        date = dt.date.fromisoformat(match.group(1))
        if today - dt.timedelta(days=1) <= date <= today + dt.timedelta(days=8):
            urls.add(link.split("#", 1)[0])
    if not urls:
        raise RuntimeError("Kickoff Status home page returned no current-week game reports; keeping the last snapshot.")

    refreshed = []
    for index, url in enumerate(sorted(urls)):
        try:
            record = report_page(session, url)
            if record:
                refreshed.append(record)
        except requests.RequestException as exc:
            raise RuntimeError(f"Could not refresh {url}: {exc}") from exc
        if index + 1 < len(urls):
            time.sleep(0.4)

    if not refreshed:
        raise RuntimeError("No readable game reports were returned; keeping the last snapshot.")
    merged = {game["url"]: game for game in existing.get("games", [])}
    merged.update({game["url"]: game for game in refreshed})
    new_games = sorted(merged.values(), key=lambda g: (g.get("game_date", ""), g.get("url", "")))
    if core(existing) == json.dumps(new_games, sort_keys=True, ensure_ascii=False):
        print(f"Checked {len(refreshed)} report pages; no published player-status changes.")
        return
    existing["source"] = "Kickoff Status"
    existing["imported_at"] = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    existing["games"] = new_games
    DATA.write_text(json.dumps(existing, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {len(refreshed)} current game reports.")

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Availability refresh failed: {exc}", file=sys.stderr)
        raise
