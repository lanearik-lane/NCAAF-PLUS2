"""Hard Rock board ingestion and conservative, market-based price screening."""
import datetime as dt
import json
import statistics
import math
from pathlib import Path
from zoneinfo import ZoneInfo
import requests

ET = ZoneInfo('America/New_York')
UTC = dt.timezone.utc
SNAPSHOT = Path(__file__).parent / 'data' / 'hardrock_board.json'
BOOKS = 'hardrockbet,draftkings,fanduel,betmgm'


def timestamp(value):
    return dt.datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(UTC)


def implied(price):
    if not isinstance(price, (int, float)) or isinstance(price, bool) or not math.isfinite(price) or abs(price) < 100:
        raise ValueError('Invalid American odds')
    return -price / (-price + 100) if price < 0 else 100 / (price + 100)


def fetch_board(key):
    if not key:
        raise ValueError('Configure ODDS_API_KEY to load the Hard Rock board.')
    try:
        response = requests.get(
            'https://api.the-odds-api.com/v4/sports/americanfootball_ncaaf/odds/',
            params={'apiKey': key, 'bookmakers': BOOKS, 'markets': 'h2h,spreads,totals',
                    'oddsFormat': 'american'}, timeout=25)
    except requests.RequestException:
        raise ValueError('Odds service could not be reached. Please retry.') from None
    if response.status_code != 200:
        raise ValueError(f'Odds service returned HTTP {response.status_code}. Check API access and quota.')
    events = response.json()
    if not isinstance(events, list):
        raise ValueError('Unexpected odds response.')
    return {'fetched_at': dt.datetime.now(UTC).isoformat(), 'events': events}


def hardrock_events(payload, now=None):
    now = now or dt.datetime.now(UTC)
    found = {}
    for event in payload.get('events', []):
        try:
            if timestamp(event['commence_time']) <= now:
                continue
            book = next(b for b in event.get('bookmakers', []) if b['key'] == 'hardrockbet')
            if not any(m.get('outcomes') for m in book.get('markets', [])):
                continue
            found[event['id']] = event
        except (KeyError, ValueError, StopIteration):
            continue
    return sorted(found.values(), key=lambda e: timestamp(e['commence_time']))


def market(book, kind):
    return next((m.get('outcomes', []) for m in book.get('markets', []) if m['key'] == kind), [])


def screen(event, now=None, min_edge=0.02):
    """Compare HR prices with the median of >=2 fresh independent no-vig books.

    Consensus is a price benchmark, not a calibrated outcome prediction.
    """
    now = now or dt.datetime.now(UTC)
    hr = next((b for b in event.get('bookmakers', []) if b.get('key') == 'hardrockbet'), {})
    teams = (event['away_team'], event['home_team'])
    def fresh(book):
        try:
            age = (now - timestamp(book['last_update'])).total_seconds()
            return 0 <= age <= 1800
        except (KeyError, ValueError):
            return False
    prices = {o['name']: o['price'] for o in market(hr, 'h2h') if o.get('name') in teams}
    base = {'pick': 'PASS', 'reason': 'Need two fresh comparison books and both moneylines.',
            'probability': None, 'edge': None, 'ev': None, 'books': 0, 'price': None, 'grade': 'PASS', 'spread': None}
    if timestamp(event['commence_time']) <= now:
        return dict(base, reason='Game has started; pregame picks are closed.')
    if not fresh(hr) or set(prices) != set(teams):
        return dict(base, reason='Hard Rock moneylines missing or older than 30 minutes.')
    samples = []
    seen = set()
    for book in event['bookmakers']:
        if book['key'] == 'hardrockbet' or book['key'] in seen or not fresh(book):
            continue
        seen.add(book['key'])
        outcomes = {o['name']: o['price'] for o in market(book, 'h2h') if o.get('name') in teams}
        if set(outcomes) != set(teams):
            continue
        try:
            a, h = (implied(outcomes[t]) for t in teams)
            samples.append(a / (a + h))
        except ValueError:
            continue
    if len(samples) < 2:
        return base
    disagreement = max(samples) - min(samples)
    if disagreement > .08:
        return dict(base, reason='Comparison books disagree by over 8 percentage points; PASS.', books=len(samples))
    # Shrink comparison estimate toward the target book to temper apparent price outliers.
    try:
        ha, hh = (implied(prices[t]) for t in teams)
    except ValueError:
        return dict(base, reason='Invalid Hard Rock price.')
    away_p = .75 * statistics.median(samples) + .25 * ha / (ha + hh)
    candidates = []
    for team, p in zip(teams, (away_p, 1 - away_p)):
        try:
            breakeven = implied(prices[team])
        except ValueError:
            return dict(base, reason='Invalid Hard Rock price.')
        profit = prices[team] / 100 if prices[team] > 0 else 100 / -prices[team]
        candidates.append(dict(pick=team, probability=p, edge=p-breakeven,
                               ev=p*profit-(1-p), books=len(samples), price=prices[team], grade='PASS', spread=disagreement))
    best = max(candidates, key=lambda c: c['ev'])
    if best['edge'] < max(.02, min_edge) or best['ev'] <= 0:
        return dict(best, pick='PASS', reason='No price advantage meeting the selected edge threshold.')
    grade = 'A' if len(samples) >= 3 and best['edge'] >= .04 and disagreement <= .03 else 'B'
    return dict(best, grade=grade, reason='Price advantage versus fresh no-vig market consensus; review injuries before betting.')


def monday_due(now, schedule, manual=False):
    local = now.astimezone(ET)
    if manual:
        return True
    noon = local.replace(hour=12, minute=0, second=0, microsecond=0)
    utc_hour = noon.astimezone(UTC).hour
    return local.weekday() == 0 and schedule == f'0 {utc_hour} * * 1'


def save_snapshot(payload):
    SNAPSHOT.parent.mkdir(exist_ok=True)
    temporary = SNAPSHOT.with_suffix('.tmp')
    temporary.write_text(json.dumps(payload, indent=2), encoding='utf-8')
    temporary.replace(SNAPSHOT)


if __name__ == '__main__':
    import os
    save_snapshot(fetch_board(os.environ.get('ODDS_API_KEY', '')))
