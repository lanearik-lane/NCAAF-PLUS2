"""Dated import of factual availability statuses, not a live connection."""
import datetime as dt
import json
from pathlib import Path
from zoneinfo import ZoneInfo
from florida_board import norm

def load_import(games):
    snapshot=json.loads((Path(__file__).parent/'data/kickoff_status_injuries.json').read_text())
    teams=sorted({g['away'] for g in games}|{g['home'] for g in games})
    aliases={'pitt':'pittsburgh','app state':'appalachian state','ul monroe':'louisiana monroe','san josé state':'san jose state'}
    def match(name):
        value=norm(aliases.get(name.casefold(),name))
        found=[t for t in teams if norm(t)==value or norm(t).startswith(value+' ')]
        return found[0] if len(found)==1 else None
    dates={t:{dt.datetime.fromisoformat(g['kickoff'].replace('Z','+00:00')).astimezone(ZoneInfo('America/New_York')).date().isoformat() for g in games if t in (g['away'],g['home'])} for t in teams}
    rows=[];coverage={}
    for report in snapshot['games']:
        checked=''
        if report['reported']:
            try:
                stamp=dt.datetime.strptime(report['reported'].replace(' PT','')+' '+report['game_date'][:4],'%a %b %d, %I:%M %p %Y')
                checked=stamp.replace(tzinfo=ZoneInfo('America/Los_Angeles')).astimezone(dt.timezone.utc).isoformat()
            except ValueError:pass
        for player in report['players']:
            team=match(player['team'])
            if team is None or report['game_date'] not in dates[team]:continue
            position=player['position'].upper()
            unit='Offense' if position in ('QB','RB','WR','TE','OL','OT','OG','C','FB') else 'Defense' if position in ('DB','CB','S','FS','SS','LB','ILB','OLB','DL','DT','DE','NT','EDGE') else ''
            status={'Available':'Active','Not listed':'Active','GTD':'Questionable','Game Time Decision':'Questionable'}.get(player['status'],player['status'])
            rows.append({'Team':team,'Player':player['player'],'Unit':unit,'Status':status,'Impact points':0.0,'Source':'Kickoff Status · '+report['url'],'Checked UTC':checked,'Position':position,'Game date':report['game_date']})
    unique={(r['Team'],r['Player'],r['Game date']):r for r in rows}
    return list(unique.values()),snapshot
