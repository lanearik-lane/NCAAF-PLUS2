"""
NCAAF+ 2026 — Live Schedule via College Football Data API (FREE)
https://collegefootballdata.com — Free tier, no key required for basic data
Falls back to ESPN hidden API, then static schedule if both fail.

Deploy: streamlit run ncaaf_plus_2026.py
"""
import streamlit as st
import requests, math, datetime, json

st.set_page_config(page_title="NCAAF+ 2026", page_icon="🏈", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700;900&family=Inter:wght@400;500;600&display=swap');
html,body,[class*="css"]{background:#0d1117!important;color:#e2e8f0;font-family:'Inter',sans-serif}
.stApp{background:#0d1117!important}
#MainMenu,footer,header{visibility:hidden}
.block-container{padding:0!important;max-width:100%!important}
.hdr{background:linear-gradient(135deg,#111827,#0d1117);border-bottom:2px solid #c8a800;padding:14px 20px;display:flex;align-items:center;gap:14px;flex-wrap:wrap}
.brand{font-family:'Barlow Condensed',sans-serif;font-size:2rem;font-weight:900;letter-spacing:-1px;line-height:1;color:#f59e0b}
.brand sup{color:#38bdf8;font-size:1.1rem}
.api-badge{display:inline-flex;align-items:center;gap:5px;border-radius:20px;padding:3px 10px;font-size:.6rem;font-weight:700;letter-spacing:1px}
.badge-live{background:#0a1f0a;border:1px solid #166534;color:#22c55e}
.badge-fallback{background:#1a1500;border:1px solid #c8a800;color:#f59e0b}
.badge-static{background:#1a1f2a;border:1px solid #334155;color:#64748b}
.stats-row{background:#0c1520;border-bottom:1px solid #1a2840;padding:7px 20px;display:flex;gap:0}
.stat-box{flex:1;text-align:center;padding:4px 0;border-right:1px solid #1a2840}
.stat-box:last-child{border-right:none}
.stat-n{font-family:'Barlow Condensed',sans-serif;font-size:1.15rem;font-weight:900}
.stat-l{font-size:.5rem;color:#4b5e78;text-transform:uppercase;letter-spacing:1px;margin-top:1px}
.section-hdr{display:flex;align-items:center;gap:8px;padding:8px 16px;background:#0c1520;border-bottom:1px solid #1a2840;border-top:2px solid}
.sec-tag{font-family:'Barlow Condensed',sans-serif;font-size:.62rem;font-weight:900;letter-spacing:2px;text-transform:uppercase;padding:2px 8px;border-radius:4px}
.sec-sub{font-size:.58rem;color:#64748b}
.sec-ct{font-size:.58rem;color:#4b5e78;margin-left:auto}
.game-row{border-bottom:1px solid #1a2840;padding:10px 16px;display:grid;grid-template-columns:270px 1fr 1fr 1fr 90px;gap:10px;align-items:center}
.game-row:hover{background:#111827}
.tlabel{font-size:.58rem;color:#4b5e78;margin-bottom:4px;display:flex;align-items:center;gap:5px;flex-wrap:wrap}
.tv{background:#1a2535;border:1px solid #1e2d40;border-radius:3px;padding:1px 5px;font-size:.5rem;color:#64748b;font-weight:700}
.ntag{font-size:.5rem;color:#c084fc;background:#1a0a2a;border:1px solid #4a1a7a;border-radius:3px;padding:1px 5px}
.trow{display:flex;align-items:center;gap:6px;padding:3px 0}
.rnk{font-size:.58rem;color:#f59e0b;font-weight:900;width:22px;text-align:right;flex-shrink:0;font-family:'Barlow Condensed',sans-serif}
.rnk-none{font-size:.58rem;color:#334155;width:22px;text-align:right;flex-shrink:0}
.tnm{font-size:.85rem;font-weight:700;color:#f1f5f9}
.trec-wrap{display:flex;flex-direction:column;gap:2px;flex:1;min-width:0}
.rec-row{display:flex;align-items:center;gap:4px;flex-wrap:wrap}
.rec-badge{display:inline-block;font-size:.62rem;font-weight:700;padding:1px 6px;border-radius:4px;font-family:'Barlow Condensed',sans-serif}
.rec-w{background:#0a1a0a;border:1px solid #166534;color:#4ade80}
.rec-l{background:#1a0505;border:1px solid #7c2d12;color:#f87171}
.rec-e{background:#0f1929;border:1px solid #1e2d40;color:#64748b}
.ats-txt{font-size:.5rem;color:#334155}
.twp{font-size:.85rem;font-weight:900;font-family:'Barlow Condensed',sans-serif;white-space:nowrap}
.wp-hot{color:#22c55e}.wp-cold{color:#94a3b8}
.tdiv{width:3px;height:14px;background:#1a2840;border-radius:2px;margin:2px 0 2px 22px}
.odds-box{background:#0c1520;border:1px solid #1a2840;border-radius:8px;padding:8px 10px;text-align:center}
.odds-lbl{font-size:.52rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;margin-bottom:4px}
.odds-pick{font-family:'Barlow Condensed',sans-serif;font-size:.9rem;font-weight:700;line-height:1.2}
.odds-dog{font-family:'Barlow Condensed',sans-serif;font-size:.78rem;font-weight:700;color:#f59e0b;line-height:1.2}
.odds-sm{font-size:.57rem;color:#64748b;margin-top:2px}
.mv-sharp{font-size:.54rem;font-weight:700;margin-top:2px;color:#38bdf8}
.mv-public{font-size:.54rem;font-weight:700;margin-top:2px;color:#f59e0b}
.mv-neutral{font-size:.54rem;font-weight:700;margin-top:2px;color:#4b5e78}
.grade-col{display:flex;flex-direction:column;align-items:center;gap:4px}
.gbig{width:30px;height:30px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-family:'Barlow Condensed',sans-serif;font-weight:900;font-size:.8rem}
.gsm{width:22px;height:22px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-family:'Barlow Condensed',sans-serif;font-weight:900;font-size:.62rem}
.g-ap{background:#166534;color:#4ade80}.g-a{background:#14532d;color:#86efac}.g-b{background:#1e3a5f;color:#60a5fa}.g-c{background:#3b2300;color:#fb923c}
.ou-over{color:#38bdf8;font-size:1.1rem;font-family:'Barlow Condensed',sans-serif;font-weight:900}
.ou-under{color:#f472b6;font-size:1.1rem;font-family:'Barlow Condensed',sans-serif;font-weight:900}
.score-live{color:#22c55e;font-weight:700;font-family:'Barlow Condensed',sans-serif;font-size:.9rem}
.score-final{color:#64748b;font-family:'Barlow Condensed',sans-serif;font-size:.85rem}
.ai-row{background:#080e16;border-bottom:1px solid #1a2840;padding:6px 16px 8px;display:grid;grid-template-columns:270px 1fr;gap:10px}
.ai-lbl{font-size:.52rem;color:#38bdf8;text-transform:uppercase;letter-spacing:1.2px;font-weight:700;margin-bottom:3px}
.ai-txt{font-size:.62rem;color:#64748b;line-height:1.55}
.kf-row{display:flex;gap:4px;flex-wrap:wrap;margin-top:4px}
.kf-p{padding:2px 6px;border-radius:4px;font-size:.54rem;background:#0a1a0a;border:1px solid #166534;color:#4ade80}
.kf-n{padding:2px 6px;border-radius:4px;font-size:.54rem;background:#1a0a00;border:1px solid #7c2d12;color:#fb923c}
.api-info{background:#0c1520;border:1px solid #1a2840;border-radius:8px;padding:10px 14px;font-size:.62rem;color:#64748b;margin:10px 16px}
</style>
""", unsafe_allow_html=True)

# ── CONFIG ────────────────────────────────────────────────────────────────
AP_RANKS = {
    "Ohio State":1,"Oregon":2,"Georgia":3,"Texas":4,"Notre Dame":5,
    "Miami":6,"Penn State":7,"Clemson":8,"Ole Miss":9,"Texas A&M":10,
    "Alabama":11,"Texas Tech":12,"LSU":13,"USC":14,"BYU":15,
    "Tennessee":16,"Michigan":17,"Oklahoma":18,"Iowa State":19,"Missouri":20,
    "Washington":21,"Wisconsin":22,"TCU":23,"Colorado":24,"Iowa":25,
}

SNIPPETS=[
    {"t":"{a} ranks top-10 in pass efficiency. {h} secondary allowed 290+ yds in 3 of 5 — aerial mismatch.","pos":["{a} pass efficiency"],"neg":["{h} secondary"]},
    {"t":"{h} is 6-1 ATS at home. Public on {a} creating sharp value on {h} money line.",                    "pos":["Home ATS trend"],"neg":[]},
    {"t":"Total climbed 2.5 pts on OVER money. Both offenses top-15 in explosive plays (15+ yds).",          "pos":["Explosive plays","Line move UP"],"neg":[]},
    {"t":"{a} QB posts elite numbers vs zone — exactly what {h} runs 74% of snaps.",                         "pos":["{a} QB vs zone"],"neg":[]},
    {"t":"Both D-lines elite — combined 50+ sacks. Low-scoring grind expected — lean UNDER.",                "pos":["Elite pass rush","UNDER trend"],"neg":[]},
    {"t":"{h} S&P+ leads the conference. Home field adds ~3 pts. Spread reflects the talent gap.",           "pos":["{h} S&P+ edge","Home field"],"neg":["{a} road record"]},
    {"t":"Line steamed toward {h} after injury news. Reverse-line movement — sharps on {h}.",                "pos":["Reverse line move"],"neg":["Injury concern"]},
    {"t":"{a} averages 210 rush yds/game (top-5). {h} ranks 80th vs run — ground game edge is real.",       "pos":["{a} run game"],"neg":["{h} rush defense"]},
    {"t":"Neutral site removes home edge. {a} leads all-time series and is 4-1 ATS at neutral venues.",      "pos":["{a} series edge"],"neg":["Neutral venue"]},
    {"t":"Transfer portal class is elite but early-season chemistry questions linger for both units.",        "pos":["Transfer depth"],"neg":["New system install"]},
]
MOVES=["Sharp ↑","Public →","Sharp ↓","Neutral →","Steam ↑"]

def rng(s,lo,hi):
    x=math.sin(s*9301+49297)*233280; return lo+((x-math.floor(x))*(hi-lo))
def rngI(s,lo,hi): return int(round(rng(s,lo,hi)))
def fml(v): return ("+" if v>0 else "")+str(v)
def fsp(v): return ("+" if v>0 else "")+str(v)
def wpct(ml): return round((-ml)/(-ml+100)*100) if ml<0 else round(100/(ml+100)*100)
def grade(c):
    if c>=85: return "A+","g-ap"
    if c>=72: return "A","g-a"
    if c>=58: return "B","g-b"
    return "C","g-c"
def rc_cls(ov):
    try:
        w,l=ov.split("-"); return "rec-w" if int(w)>int(l) else ("rec-l" if int(l)>int(w) else "rec-e")
    except: return "rec-e"

def make_pred(away, home):
    seed=(hash(away+home)%9999)*13.7+42.0
    ar=AP_RANKS.get(away,99); hr=AP_RANKS.get(home,99)
    fa=ar<hr
    mlF=rngI(seed+1,115,285); mlD=rngI(seed+2,100,245)
    sp=round(rng(seed+3,1.5,9)*2)/2
    total=round(rng(seed+4,38,68)*2)/2
    ou="OVER" if rng(seed+5,0,1)>0.5 else "UNDER"
    pa=rngI(seed+6,14,45); ph=rngI(seed+7,14,45)
    mlC=rngI(seed+8,50,93); spC=rngI(seed+9,46,89); ttC=rngI(seed+10,48,91)
    si=int(rng(seed+11,0,len(SNIPPETS)))%len(SNIPPETS)
    sn=SNIPPETS[si]
    txt=sn["t"].replace("{a}",away).replace("{h}",home)
    pos=[p.replace("{a}",away).replace("{h}",home) for p in sn["pos"]]
    neg=[p.replace("{a}",away).replace("{h}",home) for p in sn["neg"]]
    mv=MOVES[rngI(seed+12,0,len(MOVES)-1)]
    sp_p=rngI(seed+13,42,84)
    return {"ml_away":(-mlF if fa else mlD),"ml_home":(mlD if fa else -mlF),
            "sp_away":(-sp if fa else sp),"sp_home":(sp if fa else -sp),
            "total":total,"ou":ou,"pa":pa,"ph":ph,
            "mlC":mlC,"spC":spC,"ttC":ttC,"txt":txt,"pos":pos,"neg":neg,
            "mv":mv,"sp_p":sp_p,"fa":fa}

# ── FREE API FETCH FUNCTIONS ───────────────────────────────────────────────
HEADERS = {
    "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126.0 Safari/537.36",
    "Accept":"application/json",
    "Origin":"https://www.espn.com",
    "Referer":"https://www.espn.com/",
}

def normalize_game(away, home, time_str="TBD", tv="—", venue="", conf="",
                   away_rec="0-0", home_rec="0-0",
                   away_rank="", home_rank="",
                   away_score="", home_score="",
                   status="scheduled", neutral=False):
    return {
        "away":away,"home":home,"time":time_str,"tv":tv,"venue":venue,"conf":conf,
        "away_rec":away_rec,"home_rec":home_rec,
        "away_rank":away_rank,"home_rank":home_rank,
        "away_score":away_score,"home_score":home_score,
        "status":status,"neutral":neutral,
    }

@st.cache_data(ttl=600)
def fetch_cfbd(week, year=2026):
    """College Football Data API — free, no key for public schedule data."""
    games_fbs, games_fcs = [], []
    try:
        # CFBD public schedule endpoint - no API key needed for basic data
        url = f"https://api.collegefootballdata.com/games?year={year}&week={week}&seasonType=regular"
        r = requests.get(url, headers={**HEADERS, "Accept":"application/json"}, timeout=12)
        if r.status_code == 200:
            data = r.json()
            for g in data:
                home = g.get("home_team","")
                away = g.get("away_team","")
                if not home or not away: continue
                start = g.get("start_date","")
                try:
                    dt = datetime.datetime.fromisoformat(start.replace("Z","+00:00"))
                    et = dt.astimezone(datetime.timezone(datetime.timedelta(hours=-4)))
                    time_str = et.strftime("%-I:%M %p")
                except: time_str = "TBD"
                tv = g.get("tv","—") or "—"
                venue = g.get("venue","") or ""
                conf_g = g.get("home_conference","") or ""
                h_pts = g.get("home_points")
                a_pts = g.get("away_points")
                h_score = str(h_pts) if h_pts is not None else ""
                a_score = str(a_pts) if a_pts is not None else ""
                status = "STATUS_FINAL" if h_pts is not None else "scheduled"
                div = g.get("home_division","")
                game = normalize_game(away, home, time_str, tv, venue, conf_g,
                                      away_score=a_score, home_score=h_score, status=status)
                if div == "fbs": games_fbs.append(game)
                else:            games_fcs.append(game)
            return games_fbs, games_fcs, "cfbd", None
        else:
            return [], [], "cfbd", f"HTTP {r.status_code}"
    except Exception as e:
        return [], [], "cfbd", str(e)

@st.cache_data(ttl=600)
def fetch_espn(week, year=2026):
    """ESPN hidden public API — no key needed."""
    games_fbs, games_fcs = [], []
    errors = []
    for group, label in [("80","fbs"),("81","fcs")]:
        url = (f"https://site.api.espn.com/apis/site/v2/sports/football/"
               f"college-football/scoreboard?groups={group}&week={week}"
               f"&seasontype=2&limit=200&dates={year}")
        try:
            r = requests.get(url, headers=HEADERS, timeout=12)
            if r.status_code != 200:
                errors.append(f"{label} HTTP {r.status_code}")
                continue
            data = r.json()
            for ev in data.get("events",[]):
                try:
                    comp = ev["competitions"][0]
                    competitors = comp["competitors"]
                    home_t = next(c for c in competitors if c["homeAway"]=="home")
                    away_t = next(c for c in competitors if c["homeAway"]=="away")
                    home_name = home_t["team"]["displayName"]
                    away_name = away_t["team"]["displayName"]
                    h_rec = home_t.get("records",[{}])[0].get("summary","0-0") if home_t.get("records") else "0-0"
                    a_rec = away_t.get("records",[{}])[0].get("summary","0-0") if away_t.get("records") else "0-0"
                    h_rank = str(home_t.get("curatedRank",{}).get("current",""))
                    a_rank = str(away_t.get("curatedRank",{}).get("current",""))
                    h_score = home_t.get("score","")
                    a_score = away_t.get("score","")
                    status = comp.get("status",{}).get("type",{}).get("name","scheduled")
                    venue = comp.get("venue",{}).get("fullName","")
                    bcast = comp.get("broadcasts",[])
                    tv = bcast[0].get("names",["—"])[0] if bcast and bcast[0].get("names") else "—"
                    start = ev.get("date","")
                    try:
                        dt = datetime.datetime.fromisoformat(start.replace("Z","+00:00"))
                        et = dt.astimezone(datetime.timezone(datetime.timedelta(hours=-4)))
                        time_str = et.strftime("%-I:%M %p")
                    except: time_str = "TBD"
                    neutral = comp.get("neutralSite",False)
                    game = normalize_game(away_name, home_name, time_str, tv, venue, "",
                                         a_rec, h_rec, a_rank, h_rank,
                                         a_score, h_score, status, neutral)
                    if label=="fbs": games_fbs.append(game)
                    else:            games_fcs.append(game)
                except: pass
        except Exception as e:
            errors.append(str(e))
    src = "espn"
    err = ", ".join(errors) if errors else None
    return games_fbs, games_fcs, src, err

@st.cache_data(ttl=600)
def fetch_schedule(week, year=2026):
    """Try CFBD first (truly free), fallback to ESPN hidden API."""
    fbs, fcs, src, err = fetch_cfbd(week, year)
    if fbs or fcs:
        return fbs, fcs, src, None
    # fallback
    fbs, fcs, src, err2 = fetch_espn(week, year)
    if fbs or fcs:
        return fbs, fcs, src, None
    return [], [], "none", (err or "")+" | "+(err2 or "")

# Static fallback data for when both APIs fail (Week 0 + Week 1 key games)
STATIC = {
    0:[
        normalize_game("North Carolina","TCU","12:00 PM","ESPN","Aviva Stadium, Dublin IRE","Neutral",neutral=True),
        normalize_game("San Jose State","USC","3:00 PM","NBC","LA Memorial Coliseum","Big Ten"),
        normalize_game("NC State","Virginia","3:30 PM","ESPN","Scott Stadium","ACC"),
        normalize_game("Jacksonville St","North Dakota St","5:30 PM","CBSSN","Fargodome","MWC"),
        normalize_game("Sacramento St","Eastern Michigan","6:30 PM","ESPN+","Rynearson Stadium","MAC"),
        normalize_game("Hawaii","Stanford","7:00 PM","ACCN","Stanford Stadium","ACC"),
        normalize_game("New Mexico State","Florida State","7:00 PM","CW","Doak Campbell Stadium","ACC"),
        normalize_game("Memphis","UNLV","10:00 PM","FOX","Allegiant Stadium, Las Vegas","MWC"),
    ],
    1:[
        normalize_game("East Carolina","Alabama","12:00 PM","ABC","Bryant-Denny Stadium","SEC"),
        normalize_game("Ball State","Ohio State","12:00 PM","BTN","Ohio Stadium","Big Ten"),
        normalize_game("Baylor","Auburn","3:30 PM","ABC","Jordan-Hare Stadium","SEC"),
        normalize_game("Boise State","Oregon","3:30 PM","CBS","Autzen Stadium","Big Ten"),
        normalize_game("Texas State","Texas","3:30 PM","ESPN","Darrell K Royal Stadium","SEC"),
        normalize_game("Clemson","LSU","7:30 PM","ABC","Tiger Stadium","SEC"),
        normalize_game("W. Michigan","Michigan","7:30 PM","NBC","Michigan Stadium","Big Ten"),
        normalize_game("Wisconsin","Notre Dame","7:30 PM","NBC","Lambeau Field, Green Bay","Neutral",neutral=True),
        normalize_game("Louisville","Ole Miss","7:30 PM","ABC","FirstBank Stadium, Nashville","Neutral",neutral=True),
        normalize_game("SMU","Florida State","7:30 PM","ESPN","Doak Campbell Stadium","ACC"),
        normalize_game("Colorado","Georgia Tech","7:30 PM","ESPN","Bobby Dodd Stadium","ACC"),
        normalize_game("Miami","Stanford","7:30 PM","CBS","Stanford Stadium","ACC"),
    ],
}

# ── SIDEBAR ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📅 2026-27 Season")
    now=datetime.datetime.now()
    st.markdown(
        "<div style='font-size:.63rem;color:#64748b;line-height:2.1;margin-top:4px'>"
        "<b style='color:#94a3b8'>FCS Starts</b> Aug 27, 2026<br>"
        "<b style='color:#94a3b8'>FBS Week 0</b> Aug 29, 2026<br>"
        "<b style='color:#94a3b8'>FBS Week 1</b> Sep 3–7, 2026<br>"
        "<b style='color:#94a3b8'>Conf. Championships</b> Dec 5–6<br>"
        "<b style='color:#94a3b8'>CFP First Round</b> Dec 12, 2026<br>"
        "<b style='color:#94a3b8'>CFP Semifinals</b> Jan 1, 2027<br>"
        "<b style='color:#94a3b8'>National Championship</b><br>"
        "&nbsp;Jan 25, 2027 · Allegiant Stadium</div>",unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 🏅 AP Preseason Top 10")
    for team,rank in sorted(AP_RANKS.items(),key=lambda x:x[1])[:10]:
        st.markdown("<span style='font-size:.68rem;color:#94a3b8'>#"+str(rank)+" "+team+"</span>",unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 📡 Free APIs Used")
    st.markdown(
        "<div style='font-size:.62rem;color:#64748b;line-height:1.9'>"
        "1. <b style='color:#4ade80'>College Football Data</b><br>"
        "&nbsp;&nbsp;collegefootballdata.com<br>&nbsp;&nbsp;Free · No key needed<br><br>"
        "2. <b style='color:#38bdf8'>ESPN Public API</b><br>"
        "&nbsp;&nbsp;site.api.espn.com<br>&nbsp;&nbsp;Free · No key needed<br><br>"
        "3. <b style='color:#94a3b8'>Static Fallback</b><br>"
        "&nbsp;&nbsp;Built-in Week 0–1 data<br>&nbsp;&nbsp;Always available</div>",unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 🎯 Grade Legend")
    st.markdown(
        "<div style='font-size:.7rem;line-height:2.2;color:#94a3b8'>"
        "<span style='background:#166534;color:#4ade80;border-radius:50%;padding:1px 7px;font-weight:900'>A+</span> Strong edge ≥85%<br>"
        "<span style='background:#14532d;color:#86efac;border-radius:50%;padding:1px 8px;font-weight:900'>A</span> Clear edge ≥72%<br>"
        "<span style='background:#1e3a5f;color:#60a5fa;border-radius:50%;padding:1px 8px;font-weight:900'>B</span> Moderate ≥58%<br>"
        "<span style='background:#3b2300;color:#fb923c;border-radius:50%;padding:1px 8px;font-weight:900'>C</span> Toss-up</div>",unsafe_allow_html=True)

# ── HEADER ────────────────────────────────────────────────────────────────
now=datetime.datetime.now()
st.markdown(
    "<div class='hdr'>"
    "<div class='brand'>NCAAF<sup>+</sup></div>"
    "<div><div style='font-size:.62rem;color:#c8a800;font-weight:700;letter-spacing:1px'>2026-27 LIVE SCHEDULE · FREE APIs · REAL RECORDS</div>"
    "<div style='font-size:.58rem;color:#4b5e78;text-transform:uppercase;letter-spacing:1px;margin-top:2px'>"
    "FBS · FCS · College Football Data API · ESPN API</div></div>"
    "<div style='margin-left:auto;text-align:right'>"
    "<div style='font-size:.72rem;color:#f59e0b;font-weight:700'>"+now.strftime("%A, %B %-d, %Y")+"</div>"
    "<div style='font-size:.58rem;color:#4b5e78;margin-top:2px'>CFP Championship · Jan 25, 2027 · Allegiant Stadium, Las Vegas</div>"
    "</div></div>",unsafe_allow_html=True)

# ── WEEK + FILTERS ────────────────────────────────────────────────────────
def current_week():
    today=datetime.date.today()
    schedule=[(0,datetime.date(2026,8,27)),(1,datetime.date(2026,9,3)),
               (2,datetime.date(2026,9,10)),(3,datetime.date(2026,9,17)),
               (4,datetime.date(2026,9,24)),(5,datetime.date(2026,10,1)),
               (6,datetime.date(2026,10,8)),(7,datetime.date(2026,10,15)),
               (8,datetime.date(2026,10,22)),(9,datetime.date(2026,10,29)),
               (10,datetime.date(2026,11,5)),(11,datetime.date(2026,11,12)),
               (12,datetime.date(2026,11,19)),(13,datetime.date(2026,11,26)),
               (14,datetime.date(2026,12,3)),(15,datetime.date(2026,12,10))]
    cur=0
    for wk,start in schedule:
        if today>=start: cur=wk
        else: break
    return cur

c1,c2,c3=st.columns([2,2,4])
week_num=c1.selectbox("Week",list(range(0,16)),index=current_week(),
    format_func=lambda w:("Week 0 — Aug 29" if w==0 else "Week 1 — Sep 3–7" if w==1 else f"Week {w}"),
    label_visibility="collapsed")
ou_f=c2.selectbox("O/U",["All O/U","OVER","UNDER"],label_visibility="collapsed")
grade_f=c3.selectbox("Grade",["All Grades","A+ Only","A & Above","B & Above"],label_visibility="collapsed")

# ── FETCH ─────────────────────────────────────────────────────────────────
with st.spinner("Fetching live schedule..."):
    fbs_games, fcs_games, api_src, api_err = fetch_schedule(week_num)

# If both APIs failed, use static fallback
using_static = False
if not fbs_games and not fcs_games:
    static_all = STATIC.get(week_num, [])
    fbs_games = static_all
    fcs_games = []
    using_static = True

# Badge
if using_static:
    badge = "<div class='api-badge badge-static'><span>📋</span> STATIC DATA</div>"
elif api_src=="cfbd":
    badge = "<div class='api-badge badge-live'><span style='width:6px;height:6px;background:#22c55e;border-radius:50%;display:inline-block'></span> CFBD LIVE</div>"
else:
    badge = "<div class='api-badge badge-fallback'><span style='width:6px;height:6px;background:#f59e0b;border-radius:50%;display:inline-block'></span> ESPN API</div>"

if api_err and not using_static:
    st.markdown("<div class='api-info'>⚠️ Primary API issue: "+api_err[:120]+" — using fallback data.</div>",unsafe_allow_html=True)

# ── STATS ─────────────────────────────────────────────────────────────────
all_games=fbs_games+fcs_games
preds={g["away"]+"@"+g["home"]: make_pred(g["away"],g["home"]) for g in all_games}
all_p=list(preds.values())
overs=sum(1 for p in all_p if p["ou"]=="OVER")
unders=len(all_p)-overs
avg_t=str(round(sum(p["total"] for p in all_p)/len(all_p),1)) if all_p else "—"
sharp_c=sum(1 for p in all_p if "Sharp" in p["mv"])
ap_c=sum(1 for p in all_p if grade(p["mlC"])[0]=="A+")
wk_label="Week 0" if week_num==0 else f"Week {week_num}"

st.markdown(
    "<div class='stats-row'>"
    "<div class='stat-box'><div class='stat-n' style='color:#c8a800'>"+wk_label+"</div>"
    "<div class='stat-l'>"+badge+"</div></div>"
    "<div class='stat-box'><div class='stat-n' style='color:#f59e0b'>"+str(len(all_games))+"</div><div class='stat-l'>Games</div></div>"
    "<div class='stat-box'><div class='stat-n' style='color:#38bdf8'>"+str(overs)+"</div><div class='stat-l'>Overs</div></div>"
    "<div class='stat-box'><div class='stat-n' style='color:#f472b6'>"+str(unders)+"</div><div class='stat-l'>Unders</div></div>"
    "<div class='stat-box'><div class='stat-n' style='color:#c084fc'>"+avg_t+"</div><div class='stat-l'>Avg Total</div></div>"
    "<div class='stat-box'><div class='stat-n' style='color:#38bdf8'>"+str(sharp_c)+"</div><div class='stat-l'>Sharp Plays</div></div>"
    "<div class='stat-box'><div class='stat-n' style='color:#4ade80'>"+str(ap_c)+"</div><div class='stat-l'>A+ Picks</div></div>"
    "</div>",unsafe_allow_html=True)

# ── RENDER ────────────────────────────────────────────────────────────────
def render_section(games, div_label, div_color, div_full):
    filtered=[]
    for g in games:
        p=preds.get(g["away"]+"@"+g["home"]) or make_pred(g["away"],g["home"])
        if ou_f!="All O/U" and p["ou"]!=ou_f: continue
        mlG,_=grade(p["mlC"])
        if grade_f=="A+ Only" and mlG!="A+": continue
        if grade_f=="A & Above" and mlG not in ("A+","A"): continue
        if grade_f=="B & Above" and mlG=="C": continue
        filtered.append((g,p))
    if not filtered: return

    st.markdown(
        "<div class='section-hdr' style='border-top-color:"+div_color+"'>"
        "<span class='sec-tag' style='background:"+div_color+"18;color:"+div_color+";border:1px solid "+div_color+"44'>"+div_label+"</span>"
        "<span class='sec-sub'>"+div_full+"</span>"
        "<span class='sec-ct'>"+str(len(filtered))+" games</span></div>",
        unsafe_allow_html=True)

    for g,p in filtered:
        wpa=wpct(p["ml_away"]); wph=100-wpa
        fa=p["fa"]
        fnm=g["away"] if fa else g["home"]
        dnm=g["home"] if fa else g["away"]
        fav_ml=fml(p["ml_away"] if fa else p["ml_home"])
        dog_ml=fml(p["ml_home"] if fa else p["ml_away"])
        fav_sp=fsp(p["sp_away"] if fa else p["sp_home"])
        mlG,mlC=grade(p["mlC"]); spG,spC=grade(p["spC"]); ttG,ttC=grade(p["ttC"])
        ou_cls="ou-over" if p["ou"]=="OVER" else "ou-under"
        mv_cls="mv-sharp" if "Sharp" in p["mv"] else ("mv-public" if "Public" in p["mv"] else "mv-neutral")

        # Rankings — use ESPN data if available, else AP poll
        a_rank=g.get("away_rank","") or (str(AP_RANKS[g["away"]]) if g["away"] in AP_RANKS else "")
        h_rank=g.get("home_rank","") or (str(AP_RANKS[g["home"]]) if g["home"] in AP_RANKS else "")
        def clean_rank(r): return r if r and r not in ("","99","0","None") else ""
        a_rank=clean_rank(a_rank); h_rank=clean_rank(h_rank)
        a_rk=("<span class='rnk'>#"+a_rank+"</span>") if a_rank else "<span class='rnk-none'>—</span>"
        h_rk=("<span class='rnk'>#"+h_rank+"</span>") if h_rank else "<span class='rnk-none'>—</span>"

        a_rec=g.get("away_rec","0-0"); h_rec=g.get("home_rec","0-0")
        a_rc=rc_cls(a_rec); h_rc=rc_cls(h_rec)

        # Live/final score
        status=g.get("status","scheduled")
        a_score=g.get("away_score",""); h_score=g.get("home_score","")
        if status=="STATUS_FINAL" and a_score and h_score:
            score_part="<span class='score-final'>FINAL: "+g["away"]+" "+a_score+" – "+h_score+" "+g["home"]+"</span><br>"
        elif status=="STATUS_IN_PROGRESS" and a_score and h_score:
            score_part="<span class='score-live'>● LIVE: "+g["away"]+" "+a_score+" – "+h_score+" "+g["home"]+"</span><br>"
        else:
            score_part=""

        neut=("<span class='ntag'>Neutral Site</span>") if g.get("neutral") else ""
        conf=g.get("conf","")
        conf_part=("<span style='font-size:.5rem;color:#4b5e78'>"+conf+"</span>&nbsp;") if conf else ""
        pos_html="".join("<span class='kf-p'>✓ "+f+"</span>" for f in p["pos"])
        neg_html="".join("<span class='kf-n'>✗ "+f+"</span>" for f in p["neg"])
        pub_over=rngI(1+int(p["total"]),45,74)
        venue=g.get("venue","")
        wp_a_cls="wp-hot" if wpa>55 else "wp-cold"
        wp_h_cls="wp-hot" if wph>55 else "wp-cold"

        row=(
            "<div class='game-row'><div>"
            "<div class='tlabel'>"+g["time"]+" ET &nbsp;"
            "<span class='tv'>"+g["tv"]+"</span>&nbsp;"
            +conf_part+neut+"</div>"
            +score_part+
            "<div class='trow'>"+a_rk
            +"<div class='trec-wrap'>"
            "<div class='tnm'>"+g["away"]+"</div>"
            "<div class='rec-row'>"
            "<span class='rec-badge "+a_rc+"'>"+a_rec+"</span>"
            "</div></div>"
            "<div class='twp "+wp_a_cls+"'>"+str(wpa)+"%</div></div>"
            "<div class='tdiv'></div>"
            "<div class='trow'>"+h_rk
            +"<div class='trec-wrap'>"
            "<div class='tnm'>"+g["home"]+"</div>"
            "<div class='rec-row'>"
            "<span class='rec-badge "+h_rc+"'>"+h_rec+"</span>"
            "</div></div>"
            "<div class='twp "+wp_h_cls+"'>"+str(wph)+"%</div></div></div>"
            "<div class='odds-box'>"
            "<div class='odds-lbl' style='color:#4ade80'>💰 Moneyline</div>"
            "<div class='odds-pick' style='color:#22c55e'>"+fnm.split()[-1]+" "+fav_ml+"</div>"
            "<div class='odds-dog'>"+dnm.split()[-1]+" "+dog_ml+"</div>"
            "<div class='odds-sm'>Proj: "+str(p["pa"])+"–"+str(p["ph"])+"</div>"
            "<div class='"+mv_cls+"'>"+p["mv"]+" · "+str(p["sp_p"])+"% sharp</div></div>"
            "<div class='odds-box'>"
            "<div class='odds-lbl' style='color:#fb923c'>📊 Spread</div>"
            "<div class='odds-pick' style='color:#22c55e'>"+fnm.split()[-1]+" "+fav_sp+"</div>"
            "<div class='odds-sm'>Away "+fsp(p["sp_away"])+" / Home "+fsp(p["sp_home"])+"</div>"
            "<div class='odds-sm'>O/U line: "+str(p["total"])+"</div></div>"
            "<div class='odds-box'>"
            "<div class='odds-lbl' style='color:#38bdf8'>🎯 Total</div>"
            "<div class='"+ou_cls+"'>"+p["ou"]+"</div>"
            "<div class='odds-sm'>O/U "+str(p["total"])+"</div>"
            "<div class='odds-sm'>OVER "+str(pub_over)+"% public</div></div>"
            "<div class='grade-col'>"
            "<div class='gbig "+mlC+"'>"+mlG+"</div>"
            "<div style='font-size:.5rem;color:#4b5e78'>ML "+str(p["mlC"])+"%</div>"
            "<div class='gsm "+spC+"'>"+spG+"</div>"
            "<div class='gsm "+ttC+"'>"+ttG+"</div>"
            "</div></div>"
        )
        ai=(
            "<div class='ai-row'>"
            "<div style='font-size:.55rem;color:#4b5e78;padding-top:4px;line-height:1.6'>"+venue+"</div>"
            "<div><div class='ai-lbl'>🤖 Analysis</div>"
            "<div class='ai-txt'>"+p["txt"]+"</div>"
            "<div class='kf-row'>"+pos_html+neg_html+"</div></div></div>"
        )
        st.markdown(row+ai,unsafe_allow_html=True)

if not all_games:
    st.markdown(
        "<div style='text-align:center;padding:3rem;color:#4b5e78'>"
        "<div style='font-size:2rem'>📡</div>"
        "<div style='font-size:.9rem;margin-top:8px;color:#64748b'>No games found for this week.</div>"
        "<div style='font-size:.72rem;margin-top:6px'>Try a different week or check back closer to game day.</div>"
        "</div>",unsafe_allow_html=True)
else:
    render_section(fbs_games,"FBS","#f59e0b","Football Bowl Subdivision")
    render_section(fcs_games,"FCS","#38bdf8","Football Championship Subdivision")

st.markdown("<div style='height:30px'></div>",unsafe_allow_html=True)
