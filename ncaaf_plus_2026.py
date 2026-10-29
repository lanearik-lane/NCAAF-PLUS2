"""NCAAF+ — Hard Rock board and market price screening."""
import datetime as dt
import os
import streamlit as st
from hardrock_data import ET, UTC, SNAPSHOT, fetch_board, hardrock_events, market, screen, timestamp
import json

st.set_page_config(page_title='NCAAF+ | Hard Rock Board', page_icon='🏈', layout='wide')
st.markdown('''<style>
.block-container {max-width:1400px;padding-top:2rem}
h1 {letter-spacing:-.04em} [data-testid="stMetricValue"] {font-size:1.8rem}
[data-testid="stDataFrame"] {font-size:16px}
</style>''', unsafe_allow_html=True)
st.title('🏈 NCAAF+ · Hard Rock Board')
st.caption('Upcoming college football • Kickoff times in Eastern Time • Monday board update at noon ET')

mode = st.radio('View', ['Hard Rock board', 'Weekly schedule'], horizontal=True)

def secret_key():
    try:
        return st.secrets.get('ODDS_API_KEY', '') or os.getenv('ODDS_API_KEY', '')
    except FileNotFoundError:
        return os.getenv('ODDS_API_KEY', '')

@st.cache_data(ttl=300, show_spinner=False)
def load_live(key):
    return fetch_board(key)

with st.sidebar:
    st.header('Board settings')
    key = st.text_input('The Odds API key', value=secret_key(), type='password')
    st.caption('Setup: add ODDS_API_KEY in Streamlit secrets and GitHub Actions secrets.')
    if st.button('Refresh board', use_container_width=True):
        load_live.clear()
    search = st.text_input('Find a team')
    min_edge = st.slider('Minimum price edge (percentage points)', 2, 10, 3) / 100
    only_picks = st.checkbox('Show price candidates only')
    st.info('Hard Rock only. Other sportsbooks are used for comparison, never substituted into this board.')

payload = None
source = 'Saved Monday snapshot'
if key and mode == 'Hard Rock board':
    try:
        with st.spinner('Loading Hard Rock games and lines…'):
            payload = load_live(key)
        source = 'Live feed · cached for up to 5 minutes'
    except (ValueError, json.JSONDecodeError) as error:
        st.warning(str(error))
if payload is None and SNAPSHOT.exists():
    try:
        payload = json.loads(SNAPSHOT.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        st.warning('Saved board could not be read. Refresh with an API key.')
if mode == 'Weekly schedule':
    from weekly_schedule import load_week, week_dates
    @st.cache_data(ttl=300)
    def schedule(week):
        import requests
        return load_week(week, requests.get)
    today = dt.datetime.now(ET).date()
    week = st.selectbox('Season week', range(16), index=max(0, min(15, (today-dt.date(2026,8,24)).days//7)))
    if st.button('Refresh weekly schedule'):
        schedule.clear()
    start, end = week_dates(week)
    st.subheader(f'College football · {start:%b %d}–{end:%b %d}')
    st.caption('ESPN fixtures; these games are not necessarily offered by Hard Rock. No grades are assigned without actual bookmaker prices.')
    with st.spinner('Loading weekly fixtures…'):
        a, b, _, error = schedule(week)
    if error:
        st.warning(error)
    fixtures = sorted(a+b, key=lambda g:g['kickoff'])
    st.dataframe([{'Kickoff (ET)': timestamp(g['kickoff']).astimezone(ET).strftime('%a %m/%d %I:%M %p'), 'Away':g['away'], 'Home':g['home'], 'Division':g['div'], 'Status':g['status']} for g in fixtures if search.casefold() in (g['away']+' '+g['home']).casefold()], hide_index=True, use_container_width=True)
    st.stop()

if payload is None:
    st.info('Add an API key to load games, or configure the Monday workflow to save a board snapshot.')
    st.stop()

now = dt.datetime.now(UTC)
fetched = timestamp(payload['fetched_at'])
st.caption(f"{source} | Retrieved {fetched.astimezone(ET):%a %b %d, %I:%M %p %Z}")
st.caption('Coverage: Hard Rock Indiana via The Odds API. State availability and late additions may differ from your app.')
st.caption('Price screening uses other sportsbooks’ moneylines with the margin removed. It does not establish a proven predictive edge or guarantee winning picks.')
if (now - fetched).total_seconds() > 1800:
    st.warning('This board is over 30 minutes old. Picks are marked PASS until fresh prices are available.')

games = hardrock_events(payload, now)
dates = sorted({timestamp(e['commence_time']).astimezone(ET).date() for e in games})
selected_dates = st.multiselect('Game dates', dates, default=dates, format_func=lambda d: d.strftime('%a, %b %d'))
rows = []
for event in games:
    kickoff = timestamp(event['commence_time']).astimezone(ET)
    if kickoff.date() not in selected_dates:
        continue
    if search.casefold() not in (event['away_team'] + ' ' + event['home_team']).casefold():
        continue
    hr = next(b for b in event['bookmakers'] if b['key'] == 'hardrockbet')
    pick = screen(event, now, min_edge)
    if (now-fetched).total_seconds() > 1800:
        pick.update(pick='PASS', grade='PASS', reason='Saved board is over 30 minutes old. Refresh for a current pick.')
    if only_picks and pick['pick'] == 'PASS':
        continue
    prices = {o['name']: o['price'] for o in market(hr, 'h2h')}
    spreads = {o['name']: o for o in market(hr, 'spreads')}
    totals = market(hr, 'totals')
    def odds(value):
        return f'{value:+g}' if isinstance(value, (float, int)) else '—'
    def spread(team):
        line = spreads.get(team, {})
        return f"{odds(line.get('point'))} ({odds(line.get('price'))})" if line else '—'
    total_text = ' / '.join(f"{o['name']} {o.get('point', '—')} ({odds(o.get('price'))})" for o in totals) or '—'
    rows.append({'Kickoff (ET)': kickoff.strftime('%a %m/%d %I:%M %p'),
                 'Away': event['away_team'], 'Home': event['home_team'],
                 'Away ML': odds(prices.get(event['away_team'])), 'Home ML': odds(prices.get(event['home_team'])),
                 'Away spread': spread(event['away_team']), 'Home spread': spread(event['home_team']),
                 'Total': total_text, 'Pick': pick['pick'], 'Signal grade': pick['grade'],
                 'Consensus win %': round(pick['probability']*100, 1) if pick['probability'] is not None else None,
                 'Edge (pp)': round(pick['edge']*100, 1) if pick['edge'] is not None else None,
                 'Comparison books': pick['books'], 'Estimated return %': round(pick['ev']*100,1) if pick['ev'] is not None else None, 'Reason': pick['reason']})

c1, c2, c3 = st.columns(3)
c1.metric('Hard Rock upcoming games', len(games))
c2.metric('Games shown', len(rows))
c3.metric('Price candidates shown', sum(r['Pick'] != 'PASS' for r in rows))
st.info('Grade A: at least 3 comparison books, ≥4 pp price edge and ≤3 pp disagreement. Grade B: at least 2 books, ≥selected edge and positive estimated return. Otherwise PASS. Grades describe price signals, not guaranteed win rates.')
board, picks = st.tabs(['All game lines', 'Price candidates & reasons'])
with board:
    if rows:
        st.dataframe(rows, hide_index=True, use_container_width=True)
    else:
        st.info('No games match these filters. An empty Hard Rock feed is never filled with another bookmaker or a built-in schedule.')
with picks:
    candidates = sorted((r for r in rows if r['Pick'] != 'PASS'), key=lambda r: r['Edge (pp)'], reverse=True)
    if not candidates:
        st.info('No qualifying price candidates. PASS is a valid result.')
    for row in candidates:
        with st.container(border=True):
            st.subheader(row['Pick'] + ' · Moneyline')
            st.write(f"Grade {row['Signal grade']} · {row['Away']} at {row['Home']} · {row['Kickoff (ET)']}")
            st.write(f"Consensus estimate: {row['Consensus win %']}% · Price edge: {row['Edge (pp)']} pp · {row['Comparison books']} comparison books")
            st.write(row['Reason'])
st.caption('Spreads and totals are quoted lines, not model picks. Player props are not supplied by this feed. Gamble responsibly.')
