"""Calendar-week ESPN fixtures with per-day requests and explicit diagnostics."""
import datetime as dt
from concurrent.futures import ThreadPoolExecutor
from zoneinfo import ZoneInfo
ET = ZoneInfo('America/New_York')
GROUPS = [('80', 'FBS'), ('81', 'FCS'), ('57', 'D-II'), ('58', 'D-III')]

def week_dates(week):
    if not 0 <= week <= 15:
        raise ValueError('Week must be 0–15')
    start = dt.date(2026, 8, 24) + dt.timedelta(weeks=week)
    return start, start + dt.timedelta(days=6)

def load_week(week, get, headers=None):
    start, end = week_dates(week)
    tasks = [(group, division, start + dt.timedelta(days=i)) for group, division in GROUPS for i in range(7)]
    def fetch(task):
        group, division, day = task
        try:
            response = get('https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard',
                           params={'groups': group, 'dates': day.strftime('%Y%m%d'), 'limit': 300},
                           headers=headers, timeout=12)
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload.get('events'), list):
                raise ValueError('missing events list')
            return division, day, payload['events'], None
        except Exception as exc:
            status = getattr(getattr(exc, 'response', None), 'status_code', None)
            return division, day, [], f'HTTP {status}' if status else type(exc).__name__
    events, failures = {}, []
    successful = 0
    malformed = 0
    with ThreadPoolExecutor(max_workers=8) as pool:
        responses = list(pool.map(fetch, tasks))
    for division, day, daily_events, error in responses:
        if error:
            failures.append(f'{division} {day:%m/%d}: {error}')
            continue
        successful += 1
        for event in daily_events:
            try:
                comp = event['competitions'][0]
                home = next(c for c in comp['competitors'] if c['homeAway'] == 'home')
                away = next(c for c in comp['competitors'] if c['homeAway'] == 'away')
                kickoff = dt.datetime.fromisoformat(event['date'].replace('Z', '+00:00'))
                local = kickoff.astimezone(ET)
                if not start <= local.date() <= end:
                    continue
                broadcasts = comp.get('broadcasts') or []
                def record(c):
                    return (c.get('records') or [{}])[0].get('summary', '—')
                events.setdefault(event['id'], {'away': away['team']['displayName'], 'home': home['team']['displayName'],
                    'time': local.strftime('%a %I:%M %p'), 'kickoff': kickoff.isoformat(),
                    'tv': (broadcasts[0].get('names') or ['—'])[0] if broadcasts else '—',
                    'venue': (comp.get('venue') or {}).get('fullName', ''), 'conf': '',
                    'away_rec': record(away), 'home_rec': record(home),
                    'away_rank': str((away.get('curatedRank') or {}).get('current', '')),
                    'home_rank': str((home.get('curatedRank') or {}).get('current', '')),
                    'away_score': away.get('score', ''), 'home_score': home.get('score', ''),
                    'status': (comp.get('status') or event.get('status') or {}).get('type', {}).get('name', 'scheduled'),
                    'neutral': comp.get('neutralSite', False), 'div': division})
            except (KeyError, IndexError, ValueError, TypeError, StopIteration):
                malformed += 1
    games = sorted(events.values(), key=lambda g: g['kickoff'])
    first = [g for g in games if g['div'] in ('FBS', 'D-II')]
    second = [g for g in games if g['div'] in ('FCS', 'D-III')]
    messages = []
    if failures:
        messages.append('Some daily schedule requests failed; the displayed slate may be incomplete. ' + '; '.join(failures))
    if malformed:
        messages.append(f'Skipped {malformed} malformed event records.')
    if games and not any(g['div'] in ('D-II', 'D-III') for g in games):
        messages.append('ESPN returned no lower-division fixtures from the configured feeds; D-II/D-III coverage is unverified.')
    if not successful:
        messages.insert(0, 'All ESPN schedule requests failed.')
    return first, second, 'ESPN weekly schedule', ' '.join(messages) or None
