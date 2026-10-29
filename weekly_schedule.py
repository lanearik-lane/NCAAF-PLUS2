"""Explicit calendar-week ESPN fixtures, preserving division and full kickoff date."""
import datetime as dt
from zoneinfo import ZoneInfo
ET = ZoneInfo('America/New_York')

def week_dates(week):
    if not 0 <= week <= 15:
        raise ValueError('Week must be 0–15')
    start = dt.date(2026, 8, 24) + dt.timedelta(weeks=week)
    return start, start + dt.timedelta(days=6)

def load_week(week, get, headers=None):
    start, end = week_dates(week)
    events = {}
    failures = []
    for group, division in [('80','FBS'), ('81','FCS'), ('26','D-II'), ('27','D-III')]:
        try:
            response = get('https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard',
                           params={'groups':group, 'dates':f'{start:%Y%m%d}-{end:%Y%m%d}', 'limit':1000},
                           headers=headers, timeout=15)
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload.get('events'), list):
                raise ValueError('Missing events list')
            for event in payload['events']:
                comp = event['competitions'][0]
                home = next(c for c in comp['competitors'] if c['homeAway']=='home')
                away = next(c for c in comp['competitors'] if c['homeAway']=='away')
                kickoff = dt.datetime.fromisoformat(event['date'].replace('Z','+00:00'))
                local = kickoff.astimezone(ET)
                if not start <= local.date() <= end:
                    continue
                broadcasts = comp.get('broadcasts', [])
                def record(c):
                    return (c.get('records') or [{}])[0].get('summary', '—')
                events[event['id']] = {'away':away['team']['displayName'], 'home':home['team']['displayName'],
                    'time':local.strftime('%a %-I:%M %p'), 'kickoff':kickoff.isoformat(),
                    'tv':(broadcasts[0].get('names') or ['—'])[0] if broadcasts else '—',
                    'venue':comp.get('venue',{}).get('fullName',''), 'conf':'',
                    'away_rec':record(away), 'home_rec':record(home),
                    'away_rank':str(away.get('curatedRank',{}).get('current','')),
                    'home_rank':str(home.get('curatedRank',{}).get('current','')),
                    'away_score':away.get('score',''), 'home_score':home.get('score',''),
                    'status':comp.get('status',event.get('status',{})).get('type',{}).get('name','scheduled'),
                    'neutral':comp.get('neutralSite',False), 'div':division}
        except Exception:
            failures.append(division)
    games = sorted(events.values(), key=lambda g:g['kickoff'])
    first = [g for g in games if g['div'] in ('FBS','D-II')]
    second = [g for g in games if g['div'] in ('FCS','D-III')]
    error = 'Could not load divisions: '+', '.join(failures)+'. Displayed slate may be incomplete.' if failures else None
    return first, second, 'ESPN weekly schedule', error
