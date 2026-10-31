"""User-entered injury scenarios; impact values are assumptions, not fitted data."""
import datetime as dt
import math
WEIGHTS={'Out':1.0,'Doubtful':0.75,'Questionable':0.5,'Probable':0.1,'Active':0.0}

def apply_injuries(prediction,away,home,rows,now=None):
    p=dict(prediction)
    now=now or dt.datetime.now(dt.timezone.utc)
    losses={away:[0.0,0.0],home:[0.0,0.0]}
    notes=[]
    for row in rows:
        team=row.get('Team')
        if team not in losses:continue
        try:
            checked=dt.datetime.fromisoformat(str(row.get('Checked UTC','')).replace('Z','+00:00'))
            if checked.tzinfo is None:checked=checked.replace(tzinfo=dt.timezone.utc)
            age=(now-checked).total_seconds()
            impact=float(row['Impact points'])
            if not row.get('Source') or not row.get('Player') or not 0<=age<=86400 or not math.isfinite(impact) or not 0<=impact<=10:continue
            weight=WEIGHTS[row['Status']]
            index={'Offense':0,'Defense':1}[row['Unit']]
        except (ValueError,TypeError,KeyError):continue
        losses[team][index]+=impact*weight
        notes.append(f"{row['Player']} ({team}): {row['Status']}; {impact*weight:.2f} assumed points")
    if not notes:
        p['txt']='Injuries unverified: no current sourced injury inputs applied. '+p['txt']
        return p
    ao,ad=losses[away];ho,hd=losses[home]
    # Offense loss reduces own score; defense loss increases opponent score.
    away_delta=-ao+hd;home_delta=-ho+ad
    home_wp=max(.001,min(.999,p['home_wp']))
    margin=math.log(home_wp/(1-home_wp))/.13+home_delta-away_delta
    total=max(0,p['total']+away_delta+home_delta)
    hp=1/(1+math.exp(-max(-50,min(50,margin*.13))))
    p.update(home_wp=hp,away_wp=1-hp,fa=hp<.5,total=round(total*2)/2,
             sp_away=round(margin*2)/2,sp_home=-round(margin*2)/2)
    p['ph']=round(max(0,min(total,(total+margin)/2)))
    p['pa']=round(total)-p['ph']
    def ml(w):return -round(w/(1-w)*100) if w>=.5 else round((1-w)/w*100)
    p.update(ml_home=ml(hp),ml_away=ml(1-hp))
    # Injury assumptions must not promote an unvalidated grade.
    if p['mlC']>=0:p['mlC']=min(p['mlC'],84,round(max(hp,1-hp)*100))
    if p['spC']>=0:p['spC']=min(p['spC'],58)
    if p['ttC']>=0:p['ttC']=min(p['ttC'],58)
    p['txt']='INJURY SCENARIO: '+'; '.join(notes)+'. '+p['txt']
    p['neg']=list(p['neg'])+['Injury point values and status weights are assumptions; not a calibrated injury model.']
    return p
