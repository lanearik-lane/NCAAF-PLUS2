"""FBS-only snapshot with a separate, explicitly heuristic prediction transform."""
import json,math,re,unicodedata
from pathlib import Path
DATA=json.loads((Path(__file__).parent/'data/fbs_ratings.json').read_text())
def norm(value):
 value=unicodedata.normalize('NFKD',value).encode('ascii','ignore').decode().casefold()
 return ' '.join(re.findall(r'[a-z0-9]+',value))
def find(team):
 value=norm(team)
 aliases={'appalachian state':'app state','connecticut':'uconn','umass':'massachusetts','louisiana monroe':'ul monroe','hawaii':'hawai i','pitt':'pittsburgh'}
 for old,new in aliases.items():
  if value==old or value.startswith(old+' '):value=new+value[len(old):];break
 candidates=[name for name in DATA['teams'] if value==norm(name) or value.startswith(norm(name)+' ')]
 if not candidates:return None
 name=max(candidates,key=lambda n:len(norm(n)))
 # A missing State school must never match a different university.
 suffix=value[len(norm(name)):].strip()
 if suffix.startswith('state '):return None
 return dict(DATA['teams'][name],name=name)
def predict(base,away,home,neutral=False):
 a,h=find(away),find(home)
 if a is None or h is None:return base
 p=dict(base)
 margin=h['rating']-a['rating']+(0 if neutral else 2.8)
 total=max(0,(a['offense']+h['defense']+h['offense']+a['defense'])/2)
 hp=1/(1+math.exp(-max(-50,min(50,margin*.13))))
 def ml(w):return -round(w/(1-w)*100) if w>=.5 else round((1-w)/w*100)
 ph=round(max(0,min(total,(total+margin)/2)))
 p.update(home_wp=hp,away_wp=1-hp,fa=hp<.5,ml_home=ml(hp),ml_away=ml(1-hp),
  sp_away=round(margin*2)/2,sp_home=-round(margin*2)/2,total=round(total*2)/2,
  ph=ph,pa=round(total)-ph,mlC=min(84,round(max(hp,1-hp)*100)),spC=55,ttC=55,
  sp_gap=abs(h['rating']-a['rating']),mv='Imported FBS ratings',sp_p=0,
  rating_source='CollegeFootballRatings',rating_away=a,rating_home=h,
  txt=f"FBS ratings snapshot {DATA['source_updated']}: {away} {a['rating']:+.1f}, {home} {h['rating']:+.1f}. Rating difference and assumed home advantage set the projected margin. Adjusted offense/defense set the total. Probability conversion is heuristic, not calibrated. No actual sportsbook line is being evaluated.",
  pos=['Sourced FBS rating snapshot','Same rating scale for both teams'],
  neg=['Snapshot, not live ratings','Unvalidated probability conversion','Spread/total are projections, not value bets'])
 return p
