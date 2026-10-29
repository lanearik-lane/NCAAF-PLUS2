"""Match ESPN fixtures to a dated, browser-observed Hard Rock Florida board."""
import datetime as dt
import json
import re
from pathlib import Path
from zoneinfo import ZoneInfo
ET=ZoneInfo('America/New_York')

def norm(name):
    name=name.casefold().replace('&','and')
    for a,b in {'miami (fl)':'miami','north carolina state':'nc state','southeastern louisiana':'se louisiana','connecticut':'uconn','grambling state':'grambling','albany':'ualbany','st. thomas (mn)':'st thomas minnesota'}.items():
        if name==a: name=b
    name=re.sub(r'\bst\.?\b','state',name)
    return ' '.join(re.findall(r'[a-z0-9]+',name))

def board_date(text,captured):
    value=text.split(',')[0]
    if value=='Today':return captured.date()
    if value=='Tomorrow':return captured.date()+dt.timedelta(days=1)
    days=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    if value in days:return captured.date()+dt.timedelta(days=(days.index(value)-captured.weekday())%7)
    clean=re.sub(r'(\d+)(st|nd|rd|th)',r'\1',value)
    try:return dt.datetime.strptime(f'{clean} {captured.year}','%b %d %Y').date()
    except ValueError:return None

def filter_games(games,now=None):
    board=json.loads((Path(__file__).parent/'data/hardrock_fl_games.json').read_text())
    captured=dt.datetime.fromisoformat(board['captured_at'].replace('Z','+00:00')).astimezone(ET)
    now=now or dt.datetime.now(ET)
    schools={norm(t) for row in board['matchups'] for t in row['teams']}
    def school(value):
        value=norm(value)
        options=[t for t in schools if value==t or value.startswith(t+' ')]
        return max(options,key=len) if options else None
    allowed={(tuple(norm(t) for t in row['teams']),board_date(row['time'],captured)) for row in board['matchups']}
    filtered=[]
    for game in games:
        try:kickoff=dt.datetime.fromisoformat(game['kickoff'].replace('Z','+00:00')).astimezone(ET)
        except (KeyError,ValueError):continue
        if kickoff<=now:continue
        if ((school(game['away']),school(game['home'])),kickoff.date()) in allowed:
            filtered.append(game)
    return filtered,captured
