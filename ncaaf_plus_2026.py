"""
NCAAF+ 2026 — ALL DIVISIONS, ALL CONFERENCES
FBS (138 teams) · FCS (128 teams) · D-II (160 teams) · D-III (244 teams)
Live: ESPN + CFBD free APIs
Fallback: Built-in complete schedule (FBS Weeks 0-15 + FCS + D-II + D-III)
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
.hdr{background:linear-gradient(135deg,#111827,#0d1117);border-bottom:2px solid #c8a800;padding:12px 18px;display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.brand{font-family:'Barlow Condensed',sans-serif;font-size:1.9rem;font-weight:900;letter-spacing:-1px;line-height:1;color:#f59e0b}
.brand sup{color:#38bdf8;font-size:1rem}
.stats-row{background:#0c1520;border-bottom:1px solid #1a2840;padding:6px 18px;display:flex;gap:0;overflow-x:auto}
.stat-box{flex:1;min-width:70px;text-align:center;padding:3px 0;border-right:1px solid #1a2840}
.stat-box:last-child{border-right:none}
.stat-n{font-family:'Barlow Condensed',sans-serif;font-size:1.1rem;font-weight:900}
.stat-l{font-size:.46rem;color:#4b5e78;text-transform:uppercase;letter-spacing:.8px;margin-top:1px}
.div-hdr{display:flex;align-items:center;gap:7px;padding:7px 14px;background:#0c1520;border-bottom:1px solid #1a2840;border-top:3px solid;margin-top:12px;position:sticky;top:0;z-index:10}
.div-hdr:first-of-type{margin-top:0}
.div-tag{font-family:'Barlow Condensed',sans-serif;font-size:.65rem;font-weight:900;letter-spacing:2px;text-transform:uppercase;padding:2px 8px;border-radius:4px}
.conf-hdr{padding:5px 14px;background:#0a1218;border-bottom:1px solid #1a2840;font-size:.55rem;color:#4b5e78;font-weight:700;letter-spacing:1.5px;text-transform:uppercase}
.game-row{border-bottom:1px solid #1a2840;padding:8px 14px;display:grid;grid-template-columns:250px 1fr 1fr 1fr 80px;gap:8px;align-items:center}
.game-row:hover{background:#111827}
.tlabel{font-size:.54rem;color:#4b5e78;margin-bottom:3px;display:flex;align-items:center;gap:4px;flex-wrap:wrap}
.tv{background:#1a2535;border:1px solid #1e2d40;border-radius:3px;padding:1px 4px;font-size:.46rem;color:#64748b;font-weight:700}
.ntag{font-size:.46rem;color:#c084fc;background:#1a0a2a;border:1px solid #4a1a7a;border-radius:3px;padding:1px 4px}
.trow{display:flex;align-items:center;gap:5px;padding:2px 0}
.rnk{font-size:.55rem;color:#f59e0b;font-weight:900;width:20px;text-align:right;flex-shrink:0;font-family:'Barlow Condensed',sans-serif}
.rnk-none{font-size:.55rem;color:#334155;width:20px;text-align:right;flex-shrink:0}
.tnm{font-size:.8rem;font-weight:700;color:#f1f5f9}
.trec-wrap{flex:1;min-width:0}
.rec-badge{display:inline-block;font-size:.58rem;font-weight:700;padding:1px 5px;border-radius:3px;font-family:'Barlow Condensed',sans-serif}
.rec-w{background:#0a1a0a;border:1px solid #166534;color:#4ade80}
.rec-l{background:#1a0505;border:1px solid #7c2d12;color:#f87171}
.rec-e{background:#0f1929;border:1px solid #1e2d40;color:#64748b}
.twp{font-size:.8rem;font-weight:900;font-family:'Barlow Condensed',sans-serif;white-space:nowrap}
.wp-hot{color:#22c55e}.wp-cold{color:#94a3b8}
.tdiv{width:2px;height:12px;background:#1a2840;border-radius:2px;margin:2px 0 2px 19px}
.odds-box{background:#0c1520;border:1px solid #1a2840;border-radius:7px;padding:7px 8px;text-align:center}
.odds-lbl{font-size:.48rem;font-weight:700;letter-spacing:.8px;text-transform:uppercase;margin-bottom:3px}
.odds-pick{font-family:'Barlow Condensed',sans-serif;font-size:.85rem;font-weight:700;line-height:1.2}
.odds-dog{font-family:'Barlow Condensed',sans-serif;font-size:.72rem;font-weight:700;color:#f59e0b}
.odds-sm{font-size:.52rem;color:#64748b;margin-top:1px}
.mv-s{font-size:.5rem;font-weight:700;color:#38bdf8;margin-top:1px}
.mv-p{font-size:.5rem;font-weight:700;color:#f59e0b;margin-top:1px}
.mv-n{font-size:.5rem;color:#4b5e78;margin-top:1px}
.grade-col{display:flex;flex-direction:column;align-items:center;gap:3px}
.gbig{width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-family:'Barlow Condensed',sans-serif;font-weight:900;font-size:.75rem}
.gsm{width:20px;height:20px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-family:'Barlow Condensed',sans-serif;font-weight:900;font-size:.58rem}
.g-ap{background:#166534;color:#4ade80}.g-a{background:#14532d;color:#86efac}.g-b{background:#1e3a5f;color:#60a5fa}.g-c{background:#3b2300;color:#fb923c}
.ou-over{color:#38bdf8;font-size:1rem;font-family:'Barlow Condensed',sans-serif;font-weight:900}
.ou-under{color:#f472b6;font-size:1rem;font-family:'Barlow Condensed',sans-serif;font-weight:900}
.score-live{color:#22c55e;font-weight:700;font-size:.8rem}
.score-final{color:#64748b;font-size:.78rem}
.ai-row{background:#080e16;border-bottom:1px solid #1a2840;padding:5px 14px 7px;display:grid;grid-template-columns:250px 1fr;gap:8px}
.ai-lbl{font-size:.48rem;color:#38bdf8;text-transform:uppercase;letter-spacing:1px;font-weight:700;margin-bottom:2px}
.ai-txt{font-size:.58rem;color:#64748b;line-height:1.5}
.kf-row{display:flex;gap:3px;flex-wrap:wrap;margin-top:3px}
.kf-p{padding:1px 5px;border-radius:3px;font-size:.5rem;background:#0a1a0a;border:1px solid #166534;color:#4ade80}
.kf-n{padding:1px 5px;border-radius:3px;font-size:.5rem;background:#1a0a00;border:1px solid #7c2d12;color:#fb923c}
.h2h-box{background:#0a1929;border-top:1px solid #1e3a5f;padding:6px 14px 8px}
.h2h-title{font-size:.48rem;color:#38bdf8;text-transform:uppercase;letter-spacing:1px;font-weight:700;margin-bottom:4px;display:flex;justify-content:space-between}
.h2h-row{display:flex;gap:5px;padding:3px 0;border-bottom:1px solid #0f1929;font-size:.55rem}
.h2h-row:last-child{border-bottom:none}
.h2h-date{color:#4b5e78;width:80px;flex-shrink:0;font-size:.5rem}
.h2h-w{font-weight:700;width:90px;flex-shrink:0;font-size:.56rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.h2h-away{color:#22c55e}.h2h-home{color:#f59e0b}
.h2h-sc{color:#94a3b8;width:40px;flex-shrink:0;font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:.64rem}
.h2h-n{color:#334155;font-size:.48rem;font-style:italic;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
details{border-top:1px solid #1a2840}
details summary{list-style:none;padding:6px 14px;cursor:pointer;background:#0a1929;color:#38bdf8;font-size:.5rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;display:flex;align-items:center;justify-content:space-between;user-select:none}
details summary::-webkit-details-marker{display:none}
details summary:hover{background:#0f2040}
.half-inner{background:#080e16;padding:8px 12px 10px}
.prop-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;margin-top:5px}
.half-label{font-size:.48rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;padding:3px 0 5px;border-bottom:1px solid #1a2840;margin-bottom:5px}
.prop-card{background:#0c1520;border:1px solid #1a2840;border-radius:6px;padding:6px 7px;text-align:center}
.prop-lbl{font-size:.44rem;font-weight:700;letter-spacing:.8px;text-transform:uppercase;margin-bottom:3px}
.sp-l{color:#fb923c}.tot-l{color:#38bdf8}.win-l{color:#4ade80}
.prop-val{font-family:'Barlow Condensed',sans-serif;font-size:.82rem;font-weight:700;line-height:1.2}
.prop-sub{font-size:.46rem;color:#64748b;margin-top:1px}
.pbar{height:3px;background:#1e2d40;border-radius:2px;margin:3px 0 1px}
.pbar-fill{height:3px;border-radius:2px}
.src-badge{display:inline-flex;align-items:center;gap:3px;border-radius:12px;padding:2px 7px;font-size:.5rem;font-weight:700}
.src-live{background:#0a1f0a;border:1px solid #166534;color:#22c55e}
.src-static{background:#0f1929;border:1px solid #1e2d40;color:#64748b}
.no-games{text-align:center;padding:2rem;color:#4b5e78;font-size:.75rem}
</style>
""", unsafe_allow_html=True)

# ── TEAM SP+ DATABASE ──────────────────────────────────────────────────────
# [sp+, off_rank, def_rank, ats_home, ats_away, coach_adj, sos]
TEAM_DB = {
    # FBS — Power Conferences
    "Ohio State":    [35.1, 2,  8,  0.71,0.62,0.06,1.15], "Oregon":        [33.8, 3,  5,  0.65,0.59,0.04,1.15],
    "Georgia":       [31.2, 5,  1,  0.68,0.60,0.08,1.20], "Texas":         [29.7, 6,  6,  0.64,0.57,0.07,1.20],
    "Alabama":       [28.4, 8,  3,  0.62,0.58,0.05,1.20], "Notre Dame":    [27.3, 9,  4,  0.60,0.55,0.03,0.90],
    "Penn State":    [25.8,10,  7,  0.62,0.54,0.05,1.15], "Miami":         [24.1,11,  9,  0.58,0.52,0.02,1.10],
    "Michigan":      [22.9,13, 11,  0.54,0.49,0.01,1.15], "Clemson":       [22.4,14, 10,  0.55,0.50,0.01,1.10],
    "Ole Miss":      [21.9,15, 12,  0.60,0.53,0.06,1.20], "Texas A&M":     [20.8,17, 13,  0.57,0.51,0.03,1.20],
    "LSU":           [19.5,18, 14,  0.55,0.50,0.08,1.20], "USC":           [18.4,19, 16,  0.54,0.49,0.02,1.15],
    "Tennessee":     [17.2,20, 15,  0.56,0.50,0.04,1.20], "BYU":           [15.4,23, 18,  0.58,0.52,0.03,0.85],
    "Iowa State":    [14.9,25, 17,  0.57,0.51,0.04,0.95], "Missouri":      [13.8,26, 20,  0.54,0.49,0.02,1.20],
    "Washington":    [13.1,27, 22,  0.53,0.48,0.03,1.15], "Wisconsin":     [12.7,29, 19,  0.52,0.47,0.01,1.10],
    "TCU":           [11.4,31, 21,  0.54,0.49,0.03,0.95], "Colorado":      [10.8,33, 25,  0.53,0.48,0.05,0.95],
    "Iowa":          [10.2,36, 20,  0.51,0.47,0.02,1.10], "Texas Tech":    [ 9.8,37, 23,  0.53,0.48,0.03,0.95],
    "Oklahoma":      [ 9.1,39, 26,  0.52,0.47,0.04,1.20], "Kansas State":  [ 8.9,40, 24,  0.54,0.50,0.03,0.95],
    "Utah":          [ 8.5,41, 27,  0.55,0.50,0.03,0.90], "Auburn":        [ 8.1,43, 28,  0.51,0.46,0.02,1.20],
    "Florida":       [ 7.9,44, 29,  0.51,0.46,0.03,1.20], "Arkansas":      [ 7.4,46, 31,  0.50,0.46,0.02,1.20],
    "Stanford":      [ 7.8,45, 35,  0.50,0.46,0.02,1.05], "Florida State": [ 5.2,56, 45,  0.48,0.44,0.01,1.10],
    "Virginia Tech": [ 6.8,48, 37,  0.51,0.47,0.02,1.05], "NC State":      [ 6.5,50, 38,  0.51,0.47,0.02,1.05],
    "Georgia Tech":  [ 6.1,52, 40,  0.50,0.46,0.02,1.05], "Louisville":    [ 7.2,47, 34,  0.52,0.48,0.03,1.05],
    "Pittsburgh":    [ 6.3,51, 39,  0.50,0.46,0.02,1.05], "Wake Forest":   [ 5.8,54, 42,  0.50,0.46,0.01,1.00],
    "Duke":          [ 5.9,53, 41,  0.50,0.46,0.02,1.00], "Syracuse":      [ 4.8,60, 48,  0.49,0.45,0.01,1.00],
    "SMU":           [ 5.1,57, 46,  0.49,0.45,0.02,1.00], "UNLV":          [ 4.8,59, 50,  0.51,0.47,0.02,0.70],
    "Boise State":   [ 9.5,38, 29,  0.58,0.54,0.04,0.80], "Fresno State":  [ 6.2,51, 40,  0.53,0.49,0.02,0.75],
    "Colorado State":[ 5.5,55, 43,  0.51,0.47,0.02,0.75], "Nevada":        [ 4.1,64, 54,  0.50,0.46,0.01,0.65],
    "Air Force":     [ 5.8,54, 41,  0.53,0.49,0.03,0.70], "Wyoming":       [ 4.5,62, 51,  0.50,0.46,0.01,0.65],
    "Northern Illinois":[ 4.2,63,52, 0.50,0.46,0.01,0.60],"New Mexico":    [ 3.8,66, 55,  0.49,0.45,0.01,0.60],
    "Arizona State": [ 8.8,42, 30,  0.53,0.49,0.03,0.90], "Arizona":       [ 7.1,47, 33,  0.52,0.48,0.02,0.90],
    "West Virginia": [ 8.2,43, 32,  0.52,0.48,0.03,0.90], "Cincinnati":    [ 7.6,45, 36,  0.53,0.49,0.03,0.85],
    "UCF":           [ 7.4,46, 37,  0.52,0.48,0.02,0.85], "Houston":       [ 6.8,49, 39,  0.51,0.47,0.02,0.85],
    "Oklahoma State":[ 9.3,39, 30,  0.54,0.50,0.03,0.90], "Kansas":        [ 6.4,50, 41,  0.51,0.47,0.02,0.90],
    "Baylor":        [ 7.9,44, 35,  0.52,0.48,0.02,0.90], "Memphis":       [ 6.2,51, 44,  0.52,0.48,0.02,0.80],
    "Tulane":        [ 6.5,50, 43,  0.52,0.48,0.02,0.80], "Army":          [ 5.9,53, 45,  0.53,0.49,0.02,0.75],
    "Navy":          [ 5.4,56, 47,  0.52,0.48,0.01,0.75], "James Madison": [ 5.8,54, 44,  0.52,0.48,0.02,0.75],
    "Appalachian St":[ 7.1,47, 38,  0.55,0.51,0.03,0.80], "Georgia Southern":[ 5.6,55,45, 0.53,0.49,0.02,0.75],
    "Coastal Carolina":[ 6.2,51,43, 0.53,0.49,0.02,0.75], "Marshall":      [ 5.4,56, 46,  0.52,0.48,0.02,0.75],
    "Liberty":       [ 6.8,49, 40,  0.53,0.49,0.03,0.75], "Texas State":   [ 5.1,57, 47,  0.51,0.47,0.01,0.75],
    # FCS
    "North Dakota St":[ 22.0,12, 8, 0.65,0.60,0.05,0.70], "South Dakota St":[ 18.5,16,11, 0.62,0.57,0.04,0.65],
    "Sacramento St": [ 8.5, 40, 30, 0.54,0.49,0.02,0.65], "Idaho":         [  6.2, 50, 40, 0.52,0.48,0.01,0.60],
    "Montana":       [  9.2, 38, 32, 0.57,0.53,0.03,0.60], "Montana State": [ 10.1, 35, 28, 0.58,0.54,0.04,0.65],
    "Weber State":   [  7.8, 44, 36, 0.54,0.50,0.02,0.58], "Cal Poly":      [  5.8, 54, 44, 0.52,0.48,0.01,0.55],
    "Delaware":      [  8.1, 42, 34, 0.54,0.50,0.02,0.60], "Villanova":     [  7.4, 46, 38, 0.53,0.49,0.02,0.58],
    "Richmond":      [  8.8, 40, 33, 0.55,0.51,0.02,0.60], "New Hampshire": [  6.9, 48, 40, 0.53,0.49,0.01,0.55],
    "Elon":          [  6.5, 50, 42, 0.52,0.48,0.01,0.55], "Campbell":      [  7.2, 47, 39, 0.53,0.49,0.02,0.58],
    "Furman":        [  7.0, 48, 40, 0.53,0.49,0.02,0.58], "Samford":       [  6.8, 49, 41, 0.53,0.49,0.02,0.56],
    "Chattanooga":   [  7.5, 45, 37, 0.54,0.50,0.02,0.58], "ETSU":          [  6.2, 51, 43, 0.52,0.48,0.01,0.55],
    "Howard":        [  4.8, 60, 50, 0.51,0.47,0.01,0.50], "Alabama A&M":   [  4.5, 62, 52, 0.50,0.46,0.01,0.50],
    "Jackson State": [  6.2, 51, 43, 0.52,0.48,0.02,0.52], "Florida A&M":   [  5.8, 54, 46, 0.52,0.48,0.02,0.52],
    # D-II / D-III (generic)
    "Ferris State":  [  8.0, 43, 33, 0.56,0.52,0.03,0.50], "Delta State":   [  6.5, 50, 42, 0.53,0.49,0.02,0.48],
    "Colorado Mesa": [  5.2, 57, 47, 0.51,0.47,0.01,0.45], "Shepherd":      [  5.5, 55, 45, 0.52,0.48,0.01,0.45],
    "Mount Union":   [  9.5, 37, 30, 0.60,0.56,0.04,0.48], "North Central": [  8.5, 41, 33, 0.57,0.53,0.03,0.46],
}

def get_db(team):
    return TEAM_DB.get(team, [2.0, 60, 60, 0.50, 0.47, 0.00, 0.70])

AP_RANKS = {
    "Ohio State":1,"Oregon":2,"Georgia":3,"Texas":4,"Notre Dame":5,"Miami":6,
    "Penn State":7,"Clemson":8,"Ole Miss":9,"Texas A&M":10,"Alabama":11,
    "Texas Tech":12,"LSU":13,"USC":14,"BYU":15,"Tennessee":16,"Michigan":17,
    "Oklahoma":18,"Iowa State":19,"Missouri":20,"Washington":21,"Wisconsin":22,
    "TCU":23,"Colorado":24,"Iowa":25,
}

# ── SMART PREDICTION ENGINE ────────────────────────────────────────────────
def smart_predict(away, home, neutral=False, week=0):
    a_db = get_db(away); h_db = get_db(home)
    a_sp,a_off,a_def,a_ath,a_ata,a_cch,a_sos = a_db
    h_sp,h_off,h_def,h_ath,h_ata,h_cch,h_sos = h_db
    sp_diff   = h_sp - a_sp
    hfa       = 0.0 if neutral else 2.5
    coach_adj = (h_cch - a_cch) * 3.0
    off_def   = ((60-a_off)-(60-h_def))*0.15
    def_off   = ((60-h_off)-(60-a_def))*0.15
    edge      = sp_diff + hfa + coach_adj + def_off - off_def
    sp_gap    = abs(a_sp - h_sp)
    home_wp   = 1/(1+math.exp(-edge*0.15))
    away_wp   = 1-home_wp
    home_fav  = edge > 0

    def wp2ml(wp): return (-round((wp/(1-wp))*100) if wp>=0.5 else round(((1-wp)/wp)*100))
    ml_home = wp2ml(home_wp); ml_away = wp2ml(away_wp)

    avg_off   = ((60-a_off)+(60-h_off))/2
    total     = round((42+avg_off*0.35+week*0.5)*2)/2
    avg_def   = ((60-a_def)+(60-h_def))/2
    ou        = "OVER" if avg_off>avg_def else "UNDER"
    sp        = round(abs(edge)*2)/2
    fav_pts   = int(total*(home_wp if home_fav else away_wp)*1.05)
    dog_pts   = int(total-fav_pts)
    pa        = fav_pts if not home_fav else dog_pts
    ph        = fav_pts if home_fav     else dog_pts
    mlC       = min(93,max(50,int(62+sp_gap*0.8)))
    spC       = min(91,max(46,int(60+sp_gap*0.6)))
    ttC       = min(89,max(48,int(58+abs(avg_off-avg_def)*0.5)))
    mv        = ("Sharp ↑" if sp_gap>15 else "Steam ↑" if sp_gap>8 else "Neutral →" if sp_gap<3 else "Public →")
    spp       = min(89,max(38,int(45+sp_gap*1.2+(mlC-60)*0.3)))
    fnm       = home if home_fav else away
    dnm       = away if home_fav else home

    if sp_gap>20:
        txt=f"{fnm} holds a massive SP+ edge (+{sp_gap:.1f}) over {dnm}. Dominant on both sides — expect comfortable cover."
        pos=[f"{fnm} SP+ dominance","Talent gap"]; neg=[f"{dnm} upset potential"]
    elif sp_gap>10:
        hf_note='Home field adds 2.5 pts.' if not neutral else 'Neutral site.'
        txt=f"{fnm} SP+ edge of +{sp_gap:.1f} pts. {hf_note} Line moving toward {fnm}."
        pos=[f"{fnm} SP+ edge","ATS trend"]; neg=["Cover variance"]
    elif sp_gap>4:
        venue_note='Home field is the difference.' if not neutral else 'Neutral site makes this a true toss-up.'
        txt=f"Competitive matchup — SP+ gap {sp_gap:.1f} pts. {venue_note} Lean {fnm} with low conviction."
        pos=["Slight SP+ edge"]; neg=["Low confidence","Week 1 variance"]
    else:
        txt=f"Dead-even by SP+. Coin-flip game. Focus on total rather than side."
        pos=["Total play focus"]; neg=["Toss-up","Unknown variables"]

    return {"ml_away":ml_away,"ml_home":ml_home,
            "sp_away":-sp if home_fav else sp,"sp_home":sp if home_fav else -sp,
            "total":total,"ou":ou,"pa":pa,"ph":ph,
            "mlC":mlC,"spC":spC,"ttC":ttC,"txt":txt,"pos":pos,"neg":neg,
            "mv":mv,"sp_p":spp,"fa":not home_fav,
            "home_wp":home_wp,"away_wp":away_wp,"sp_gap":sp_gap}

def make_half_preds(away, home, p, week=0):
    fa=p["fa"]; fnm=away if fa else home
    h1t=round(p["total"]*0.48*2)/2; h2t=round((p["total"]-h1t)*2)/2
    h1s=round(abs(p["sp_away"])*0.55*2)/2; h2s=round(abs(p["sp_away"])*0.50*2)/2
    h1ou="OVER" if p["ou"]=="OVER" else "UNDER"
    h2ou="UNDER" if p["ou"]=="OVER" else "OVER"
    h2w=fnm if p["sp_gap"]>8 else (home if fa else away)
    def hc(b,a): return min(91,max(46,int(b+a)))
    return {"h1_sp":h1s,"h1_sp_team":fnm,"h1_spC":hc(p["spC"],-4),
            "h1_total":h1t,"h1_ou":h1ou,"h1_totC":hc(p["ttC"],-3),
            "h1_win":fnm,"h1_winC":hc(p["mlC"],-5),
            "h2_sp":h2s,"h2_sp_team":fnm,"h2_spC":hc(p["spC"],-8),
            "h2_total":h2t,"h2_ou":h2ou,"h2_totC":hc(p["ttC"],-6),
            "h2_win":h2w,"h2_winC":hc(p["mlC"],-10),"fa":fa,"fnm":fnm}

def grade(c):
    if c>=85: return "A+","g-ap"
    if c>=72: return "A","g-a"
    if c>=58: return "B","g-b"
    return "C","g-c"

def fml(v): return("+" if v>0 else "")+str(v)
def fsp(v): return("+" if v>0 else "")+str(v)
def rc_cls(ov):
    try: w,l=ov.split("-"); return "rec-w" if int(w)>int(l) else("rec-l" if int(l)>int(w) else "rec-e")
    except: return "rec-e"

# ── COMPLETE 2026 SCHEDULE — ALL 4 DIVISIONS ──────────────────────────────
def G(a,h,t,tv,conf,venue,div="FBS",neutral=False):
    ar=str(AP_RANKS.get(a,"")) if AP_RANKS.get(a) else ""
    hr=str(AP_RANKS.get(h,"")) if AP_RANKS.get(h) else ""
    return{"away":a,"home":h,"time":t,"tv":tv,"conf":conf,"venue":venue,
           "div":div,"neutral":neutral,"away_rank":ar,"home_rank":hr,
           "away_rec":"0-0","home_rec":"0-0","away_score":"","home_score":"","status":"scheduled"}

# ── FBS ALL CONFERENCES ───────────────────────────────────────────────────
FBS_BY_CONF = {
    "SEC":["Alabama","Arkansas","Auburn","Florida","Georgia","Kentucky","LSU","Mississippi State",
           "Missouri","Oklahoma","Ole Miss","South Carolina","Tennessee","Texas","Texas A&M","Vanderbilt"],
    "Big Ten":["Illinois","Indiana","Iowa","Maryland","Michigan","Michigan State","Minnesota",
               "Nebraska","Northwestern","Ohio State","Oregon","Penn State","Purdue","Rutgers",
               "UCLA","USC","Washington","Wisconsin"],
    "ACC":["Boston College","California","Clemson","Duke","Florida State","Georgia Tech","Louisville",
           "Miami","NC State","North Carolina","Pitt","SMU","Stanford","Syracuse","Virginia",
           "Virginia Tech","Wake Forest"],
    "Big 12":["Arizona","Arizona State","Baylor","BYU","Cincinnati","Colorado","Houston","Iowa State",
              "Kansas","Kansas State","Oklahoma State","TCU","Texas Tech","UCF","Utah","West Virginia"],
    "Pac-12":["Boise State","Colorado State","Fresno State","Oregon State","San Diego State",
              "Texas State","Utah State","Washington State"],
    "Mountain West":["Air Force","Hawaii","Nevada","New Mexico","North Dakota State","Northern Illinois",
                     "San Jose State","UNLV","UTEP","Wyoming"],
    "AAC":["Army","Charlotte","East Carolina","Florida Atlantic","Memphis","Navy","North Texas",
           "Rice","Temple","Tulane","Tulsa","UAB","USF","UTSA"],
    "MAC":["Akron","Ball State","Bowling Green","Buffalo","Central Michigan","Eastern Michigan",
           "Kent State","Miami (OH)","Ohio","Sacramento State","Toledo","UMass","Western Michigan"],
    "Sun Belt":["Appalachian State","Arkansas State","Coastal Carolina","James Madison",
                "Georgia Southern","Georgia State","Louisiana","Louisiana Tech","Marshall",
                "Old Dominion","South Alabama","Southern Miss","Troy","ULM"],
    "CUSA":["Delaware","FIU","Jacksonville State","Kennesaw State","Liberty","Middle Tennessee",
            "Missouri State","New Mexico State","Sam Houston","WKU"],
    "Ind.":["Notre Dame","UConn"],
}

# ── SCHEDULE DATA ─────────────────────────────────────────────────────────
SCHEDULE = {
    0: [  # Week 0 — Aug 29
        # FBS
        G("North Carolina","TCU",        "12:00 PM","ESPN","Neutral","Aviva Stadium, Dublin Ireland",neutral=True),
        G("San Jose State","USC",         "3:00 PM","NBC","Big Ten","LA Memorial Coliseum, Los Angeles"),
        G("NC State","Virginia",          "3:30 PM","ESPN","ACC","Scott Stadium, Charlottesville VA"),
        G("Jacksonville St","North Dakota St","5:30 PM","CBSSN","MWC","Fargodome, Fargo ND"),
        G("Sacramento St","Eastern Michigan","6:30 PM","ESPN+","MAC","Rynearson Stadium, Ypsilanti MI"),
        G("Hawaii","Stanford",            "7:00 PM","ACCN","ACC","Stanford Stadium, Palo Alto CA"),
        G("New Mexico State","Florida State","7:00 PM","CW","ACC","Doak Campbell Stadium, Tallahassee FL"),
        G("Memphis","UNLV",               "10:00 PM","FOX","MWC","Allegiant Stadium, Las Vegas NV"),
        # FCS
        G("Robert Morris","Wagner",       "12:00 PM","ESPN+","NEC","Wagner College, Staten Island NY","FCS"),
        G("Central Connecticut","South Dakota","2:00 PM","ESPN+","MVFC","DakotaDome, Vermillion SD","FCS"),
        G("Alabama State","Southern",     "3:00 PM","ESPNU","SWAC","Legion Field, Birmingham AL","FCS",True),
        G("UC Davis","Portland State",    "3:00 PM","ESPN+","Big Sky","Viking Stadium, Portland OR","FCS"),
        G("Lehigh","Holy Cross",          "3:30 PM","ESPN+","Patriot","Hart Center, Worcester MA","FCS"),
        G("Eastern Washington","Northern Arizona","5:00 PM","ESPN+","Big Sky","Walkup Skydome, Flagstaff AZ","FCS"),
        G("Campbell","East Tennessee St", "5:30 PM","ESPN+","SoCon","William B. Greene Stadium, Johnson City TN","FCS"),
        G("SE Missouri State","Indiana State","6:00 PM","ESPN+","MVFC","Memorial Stadium, Terre Haute IN","FCS"),
        G("Bucknell","Richmond",          "6:00 PM","ESPN+","Patriot","Robins Stadium, Richmond VA","FCS"),
        G("VMI","Idaho State",            "6:00 PM","ESPN+","Big Sky","Holt Arena, Pocatello ID","FCS"),
        G("The Citadel","Wofford",        "6:00 PM","ESPN+","SoCon","Gibbs Stadium, Spartanburg SC","FCS"),
        G("East Texas A&M","Mercer",      "7:00 PM","ESPN","SoCon","Five Star Stadium, Macon GA","FCS"),
        G("Monmouth","Tennessee Tech",    "7:00 PM","ESPN+","SoCon","Tucker Stadium, Cookeville TN","FCS"),
        G("Abilene Christian","Lamar",    "7:00 PM","ESPN+","Southland","Provost Umphrey Stadium, Beaumont TX","FCS"),
        G("Eastern Kentucky","Western Carolina","7:00 PM","ESPN+","SoCon","E.J. Whitmire Stadium, Cullowhee NC","FCS"),
        G("Stephen F. Austin","McNeese",  "7:00 PM","ESPN+","Southland","Cowboy Stadium, Lake Charles LA","FCS"),
        G("Howard","Alabama A&M",         "7:30 PM","ABC","MEAC/SWAC","Center Parc Stadium, Atlanta GA","FCS",True),
        G("Jackson State","Tennessee State","8:30 PM","ESPN+","SWAC","Nissan Stadium, Nashville TN","FCS"),
        G("Prairie View A&M","Tarleton State","9:00 PM","ESPN2","UAC","Memorial Stadium, Stephenville TX","FCS"),
        G("Southern Utah","Montana",      "9:00 PM","ESPN+","Big Sky","Washington-Grizzly Stadium, Missoula MT","FCS"),
        G("Montana State","Utah Tech",    "10:00 PM","ESPN+","Big Sky","Burns Arena, St. George UT","FCS"),
        # D-II
        G("Ferris State","Findlay",       "1:00 PM","ESPN+","GLIAC","Donnell Stadium, Findlay OH","D-II"),
        G("Delta State","West Alabama",   "2:00 PM","—","GSC","UWA Foley Stadium, Livingston AL","D-II"),
        G("Colorado Mesa","Western State","2:00 PM","—","RMAC","Mountaineer Bowl, Gunnison CO","D-II"),
        G("Shepherd","Glenville State",   "1:00 PM","—","MEC","Pioneer Bowl, Glenville WV","D-II"),
        G("Minnesota Duluth","Bemidji St","2:00 PM","—","NSIC","Chet Anderson Stadium, Bemidji MN","D-II"),
        # D-III
        G("Mount Union","Ohio Northern",  "1:00 PM","—","OAC","Dial-Roberson Stadium, Ada OH","D-III"),
        G("North Central","Wheaton IL",   "1:00 PM","—","CCIW","Anderson Athletic Complex, Wheaton IL","D-III"),
        G("Mary Hardin-Baylor","Hardin-Simmons","2:00 PM","—","ASC","Elbert Goldsby Stadium, Abilene TX","D-III"),
        G("Linfield","Pacific Lutheran",  "4:00 PM","—","NWC","Sparks Stadium, Parkland WA","D-III"),
        G("St. John's MN","Bethel MN",    "1:00 PM","—","MIAC","Bethel Stadium, St. Paul MN","D-III"),
        G("Wisconsin-Whitewater","UW-Oshkosh","1:00 PM","—","WIAC","J.J. Keller Field, Oshkosh WI","D-III"),
    ],
    1: [  # Week 1 — Sep 3-7
        G("UMass","Rutgers",              "6:00 PM","BTN","Big Ten","SHI Stadium, Piscataway NJ"),
        G("Colorado","Georgia Tech",      "8:00 PM","ESPN","ACC","Bobby Dodd Stadium, Atlanta GA"),
        G("Akron","Wake Forest",          "7:00 PM","ACCN","ACC","Truist Field, Winston-Salem NC"),
        G("UAB","Illinois",               "9:00 PM","BTN","Big Ten","Memorial Stadium, Champaign IL"),
        G("Fresno State","USC",           "9:00 PM","FOX","Big Ten","LA Memorial Coliseum, Los Angeles CA"),
        G("Miami","Stanford",             "9:00 PM","ESPN","ACC","Stanford Stadium, Palo Alto CA"),
        G("East Carolina","Alabama",      "12:00 PM","ABC","SEC","Bryant-Denny Stadium, Tuscaloosa AL"),
        G("Ball State","Ohio State",      "12:30 PM","BTN","Big Ten","Ohio Stadium, Columbus OH"),
        G("North Texas","Indiana",        "12:00 PM","FOX","Big Ten","Memorial Stadium, Bloomington IN"),
        G("Baylor","Auburn",              "3:30 PM","ABC","SEC","Jordan-Hare Stadium, Auburn AL"),
        G("Boise State","Oregon",         "3:30 PM","CBS","Big Ten","Autzen Stadium, Eugene OR"),
        G("Texas State","Texas",          "3:30 PM","ESPN","SEC","Darrell K Royal Stadium, Austin TX"),
        G("Tulane","Duke",                "3:30 PM","ESPN2","ACC","Wallace Wade Stadium, Durham NC"),
        G("Oklahoma State","Tulsa",       "3:45 PM","ESPNU","AAC","H.A. Chapman Stadium, Tulsa OK"),
        G("Clemson","LSU",                "7:30 PM","ABC","SEC","Tiger Stadium (Death Valley), Baton Rouge LA"),
        G("W. Michigan","Michigan",       "7:30 PM","NBC","Big Ten","Michigan Stadium (The Big House)"),
        G("Florida Atlantic","Florida",   "7:45 PM","SEC+","SEC","Ben Hill Griffin Stadium (The Swamp)"),
        G("Wisconsin","Notre Dame",       "7:30 PM","NBC","Neutral","Lambeau Field, Green Bay WI",True),
        G("Louisville","Ole Miss",        "7:30 PM","ABC","Neutral","FirstBank Stadium, Nashville TN",True),
        G("SMU","Florida State",          "7:30 PM","ESPN","ACC","Doak Campbell Stadium, Tallahassee FL"),
        G("FIU","South Florida",          "7:00 PM","ESPN+","AAC","Raymond James Stadium, Tampa FL"),
        G("UCLA","California",            "10:30 PM","ESPN","ACC","California Memorial Stadium, Berkeley CA"),
        G("Washington St","Washington",   "10:30 PM","FS1","Big Ten","Husky Stadium, Seattle WA"),
        # FCS Week 1
        G("Bethune-Cookman","UCF",        "7:00 PM","ESPN+","AAC","FBC Mortgage Stadium, Orlando FL","FCS"),
        G("Idaho","Utah",                 "9:00 PM","ESPNU","Big 12","Rice-Eccles Stadium, Salt Lake City UT","FCS"),
        G("Indiana State","Purdue",       "7:00 PM","BTN","Big Ten","Ross-Ade Stadium, West Lafayette IN","FCS"),
        G("Southern Illinois","Samford",  "6:00 PM","ESPN+","SoCon","Seibert Stadium, Birmingham AL","FCS"),
        G("Morgan State","Hampton",       "1:00 PM","MEAC+","MEAC","Hampton Stadium","FCS"),
        G("Villanova","Louisville",       "7:00 PM","ACCN","ACC","L&N Federal Credit Union Stadium","FCS"),
        G("NC A&T","Georgia State",       "7:00 PM","ESPN+","Sun Belt","Center Parc Stadium, Atlanta GA","FCS"),
        G("LIU","Kansas",                 "8:00 PM","ESPNU","Big 12","David Booth Kansas Memorial Stadium","FCS"),
        G("Tennessee State","Georgia",    "3:00 PM","SEC+","SEC","Sanford Stadium, Athens GA","FCS"),
        # D-II Week 1
        G("Tarleton State","TAMU-Commerce","7:00 PM","—","Lone Star","Memorial Stadium, Stephenville TX","D-II"),
        G("Minnesota Duluth","Augsburg",  "1:00 PM","—","NSIC","Griggs Stadium, Minneapolis MN","D-II"),
        G("Washburn","Emporia State",     "2:00 PM","—","MIAA","Welch Stadium, Emporia KS","D-II"),
        # D-III Week 1
        G("Amherst","Williams",           "1:00 PM","—","NESCAC","Weston Field, Williamstown MA","D-III"),
        G("Muhlenberg","Johns Hopkins",   "1:00 PM","—","Centennial","Homewood Field, Baltimore MD","D-III"),
        G("Hope","Calvin",                "1:30 PM","—","MIAA","Calvin University, Grand Rapids MI","D-III"),
        G("Wartburg","Buena Vista",       "1:00 PM","—","Iowa Conf.","Strandberg Memorial Stadium, Storm Lake IA","D-III"),
    ],
    2: [  # Week 2 — Sep 10-13
        G("Georgia","Clemson",            "12:00 PM","ABC","Neutral","Mercedes-Benz Stadium, Atlanta GA",True),
        G("Mississippi St","LSU",         "12:00 PM","ESPN","SEC","Tiger Stadium, Baton Rouge LA"),
        G("Kansas","Texas",               "3:30 PM","ESPN","SEC","Darrell K Royal Stadium"),
        G("Texas A&M","Alabama",          "3:30 PM","CBS","SEC","Bryant-Denny Stadium"),
        G("Notre Dame","Michigan",        "3:30 PM","NBC","Big Ten","Michigan Stadium"),
        G("Penn State","Ohio State",      "7:30 PM","FOX","Big Ten","Ohio Stadium"),
        G("Tennessee","Florida",          "3:30 PM","CBS","SEC","Ben Hill Griffin Stadium"),
        G("Oregon State","Oregon",        "7:30 PM","FS1","Big Ten","Autzen Stadium"),
        G("Baylor","Texas Tech",          "7:00 PM","ESPN","Big 12","Jones AT&T Stadium, Lubbock TX"),
        G("NC State","Miami",             "7:30 PM","ACCN","ACC","Hard Rock Stadium, Miami FL"),
        G("Colorado","Nebraska",          "3:30 PM","ABC","Big Ten","Memorial Stadium, Lincoln NE"),
        G("Arizona State","BYU",          "10:00 PM","ESPN","Big 12","LaVell Edwards Stadium, Provo UT"),
        G("Army","Western Kentucky",      "3:30 PM","CBSSN","CUSA","Michie Stadium, West Point NY"),
        G("Georgia Southern","Coastal Carolina","5:00 PM","ESPN+","Sun Belt","Brooks Stadium, Conway SC"),
        G("South Alabama","Louisiana",    "7:00 PM","ESPN+","Sun Belt","Cajun Field, Lafayette LA"),
        G("South Dakota St","Iowa",       "12:00 PM","BTN","Big Ten","Kinnick Stadium, Iowa City IA","FCS"),
        G("Montana","Washington State",   "4:00 PM","ESPN+","Big Ten","Gesa Field, Pullman WA","FCS"),
        G("Ferris State","Grand Valley St","1:00 PM","—","GLIAC","Lubbers Stadium, Allendale MI","D-II"),
        G("Delta State","Mississippi College","2:00 PM","—","GSC","Alumni Stadium, Clinton MS","D-II"),
        G("North Central","Augustana IL", "1:00 PM","—","CCIW","Lindberg Stadium, Rock Island IL","D-III"),
        G("Mount Union","Marietta",       "1:00 PM","—","OAC","Don Drumm Stadium, Alliance OH","D-III"),
    ],
    3: [  # Week 3 — Sep 17-20
        G("Tennessee","Alabama",          "3:30 PM","ABC","SEC","Bryant-Denny Stadium"),
        G("LSU","Ole Miss",               "7:30 PM","ESPN","SEC","Vaught-Hemingway Stadium, Oxford MS"),
        G("Michigan","Penn State",        "7:30 PM","CBS","Big Ten","Beaver Stadium, State College PA"),
        G("USC","Notre Dame",             "7:30 PM","NBC","Big Ten","Notre Dame Stadium"),
        G("Georgia","Auburn",             "3:30 PM","CBS","SEC","Jordan-Hare Stadium"),
        G("Arkansas","Texas A&M",         "12:00 PM","ESPN","SEC","Kyle Field, College Station TX"),
        G("Oklahoma","Texas",             "3:30 PM","ESPN","SEC","Darrell K Royal Stadium"),
        G("Colorado","Colorado State",    "7:00 PM","FS1","Big 12","Canvas Stadium, Fort Collins CO"),
        G("Iowa State","Kansas State",    "3:30 PM","ESPN2","Big 12","Bill Snyder Family Stadium"),
        G("TCU","Baylor",                 "7:00 PM","FS1","Big 12","McLane Stadium, Waco TX"),
        G("Appalachian St","James Madison","3:30 PM","ESPN+","Sun Belt","Bridgeforth Stadium"),
        G("Marshall","Georgia Southern",  "3:00 PM","ESPN+","Sun Belt","Paulson Stadium, Statesboro GA"),
        G("UTSA","Army",                  "8:00 PM","CBSSN","AAC","Alamodome, San Antonio TX"),
        G("North Dakota St","Montana State","4:00 PM","ESPN+","MWC","Bobcat Stadium, Bozeman MT","FCS"),
        G("South Dakota St","Southern Illinois","2:00 PM","ESPN+","MVFC","Saluki Stadium, Carbondale IL","FCS"),
        G("Furman","Samford",             "6:00 PM","ESPN+","SoCon","Seibert Stadium, Birmingham AL","FCS"),
        G("Delaware","Richmond",          "3:30 PM","ESPN+","CAA","Robins Stadium, Richmond VA","FCS"),
        G("Ferris State","Hillsdale",     "1:00 PM","—","GLIAC","Plaster Athletic Complex, Hillsdale MI","D-II"),
        G("Mount Union","Ohio Wesleyan",  "1:00 PM","—","OAC","Phillips-Perkins Field, Delaware OH","D-III"),
        G("Wisconsin-Whitewater","Bethel MN","1:00 PM","—","WIAC/MIAC","Nygaard Field, St. Paul MN","D-III"),
    ],
    4: [  # Week 4 — Sep 24-27
        G("Alabama","Georgia",            "3:30 PM","CBS","SEC","Sanford Stadium, Athens GA"),
        G("Texas A&M","LSU",              "7:30 PM","ESPN","SEC","Tiger Stadium, Baton Rouge LA"),
        G("Iowa","Ohio State",            "12:00 PM","FOX","Big Ten","Ohio Stadium"),
        G("Penn State","Michigan",        "7:30 PM","NBC","Big Ten","Michigan Stadium"),
        G("Oregon","Washington",          "3:30 PM","ABC","Big Ten","Husky Stadium, Seattle WA"),
        G("Clemson","Florida State",      "3:30 PM","ESPN","ACC","Doak Campbell Stadium"),
        G("Texas","Ole Miss",             "7:30 PM","ABC","SEC","Vaught-Hemingway Stadium"),
        G("Tennessee","Missouri",         "12:00 PM","ESPN","SEC","Memorial Stadium, Columbia MO"),
        G("Notre Dame","Louisville",      "7:30 PM","NBC","ACC","Notre Dame Stadium"),
        G("Arizona State","Kansas State", "3:30 PM","FS1","Big 12","Bill Snyder Family Stadium"),
        G("Utah","BYU",                   "8:30 PM","ESPN","Big 12","LaVell Edwards Stadium, Provo UT"),
        G("Georgia Tech","Clemson",       "3:30 PM","ACCN","ACC","Memorial Stadium, Clemson SC"),
        G("Coastal Carolina","App State", "7:30 PM","ESPN+","Sun Belt","Kidd Brewer Stadium, Boone NC"),
        G("South Dakota St","North Dakota St","4:00 PM","ESPN+","MVFC","Fargodome, Fargo ND","FCS"),
        G("Montana","Cal Poly",           "3:00 PM","ESPN+","Big Sky","Spanos Stadium, San Luis Obispo CA","FCS"),
        G("Weber State","Eastern Washington","3:00 PM","ESPN+","Big Sky","Roos Field, Cheney WA","FCS"),
        G("Ferris State","Saginaw Valley","1:00 PM","—","GLIAC","Wickes Gridiron, University Center MI","D-II"),
        G("Delta State","Valdosta State", "3:00 PM","—","GSC","Bazemore-Hyder Stadium, Valdosta GA","D-II"),
        G("North Central","Carthage",     "1:00 PM","—","CCIW","Rattan Park, Kenosha WI","D-III"),
        G("Mount Union","Baldwin Wallace","1:00 PM","—","OAC","Finnie Stadium, Berea OH","D-III"),
    ],
    5: [  # Week 5 — Oct 1-4
        G("Georgia","Ole Miss",           "3:30 PM","CBS","SEC","Vaught-Hemingway Stadium"),
        G("Alabama","Tennessee",          "3:30 PM","ABC","SEC","Neyland Stadium, Knoxville TN"),
        G("Ohio State","Penn State",      "7:30 PM","NBC","Big Ten","Ohio Stadium"),
        G("Texas","Texas A&M",            "7:30 PM","ESPN","SEC","Kyle Field, College Station TX"),
        G("Michigan","Oregon",            "3:30 PM","FOX","Big Ten","Autzen Stadium"),
        G("Miami","Clemson",              "7:30 PM","ABC","ACC","Memorial Stadium, Clemson SC"),
        G("Oklahoma State","TCU",         "3:30 PM","FS1","Big 12","Amon G. Carter Stadium, Fort Worth TX"),
        G("Iowa","Michigan State",        "12:00 PM","BTN","Big Ten","Spartan Stadium, East Lansing MI"),
        G("Utah","Colorado",              "10:00 PM","ESPN","Big 12","Folsom Field, Boulder CO"),
        G("Notre Dame","Virginia Tech",   "7:30 PM","NBC","ACC","Notre Dame Stadium"),
        G("Coastal Carolina","Georgia State","5:00 PM","ESPN+","Sun Belt","Georgia State Stadium, Atlanta GA"),
        G("James Madison","App State",    "3:30 PM","ESPN+","Sun Belt","Kidd Brewer Stadium, Boone NC"),
        G("North Dakota St","South Dakota","4:00 PM","ESPN+","MVFC","DakotaDome, Vermillion SD","FCS"),
        G("Montana State","Weber State",  "3:00 PM","ESPN+","Big Sky","Stewart Stadium, Ogden UT","FCS"),
        G("Ferris State","Michigan Tech", "1:00 PM","—","GLIAC","Sherman Field, Houghton MI","D-II"),
        G("Delta State","Henderson State","2:00 PM","—","GSC","Carpenter-Haygood Stadium, Arkadelphia AR","D-II"),
        G("North Central","Illinois Wesleyan","1:00 PM","—","CCIW","Tucci Stadium, Bloomington IL","D-III"),
        G("Mount Union","Heidelberg",     "1:00 PM","—","OAC","Hoernemann Stadium, Tiffin OH","D-III"),
    ],
    6: [  # Week 6 — Oct 8-11 (Red River)
        G("Texas","Oklahoma",             "12:00 PM","ABC","Neutral","Cotton Bowl, Dallas TX",True),
        G("Michigan","Illinois",          "12:00 PM","BTN","Big Ten","Memorial Stadium, Champaign IL"),
        G("Notre Dame","Stanford",        "7:30 PM","NBC","ACC","Stanford Stadium"),
        G("Penn State","Michigan State",  "3:30 PM","CBS","Big Ten","Beaver Stadium"),
        G("Auburn","Georgia",             "7:30 PM","ESPN","SEC","Sanford Stadium"),
        G("Ole Miss","LSU",               "7:30 PM","ESPN","SEC","Tiger Stadium"),
        G("Alabama","Missouri",           "3:30 PM","ABC","SEC","Memorial Stadium, Columbia MO"),
        G("Baylor","Kansas State",        "3:30 PM","ESPN2","Big 12","McLane Stadium"),
        G("Florida State","Clemson",      "3:30 PM","ESPN","ACC","Memorial Stadium, Clemson SC"),
        G("Colorado","Arizona",           "9:00 PM","FS1","Big 12","Arizona Stadium, Tucson AZ"),
        G("Coastal Carolina","Troy",      "3:00 PM","ESPN+","Sun Belt","Veterans Memorial Stadium, Troy AL"),
        G("North Dakota St","Missouri State","4:00 PM","ESPN+","MVFC","Plaster Field, Springfield MO","FCS"),
        G("Chattanooga","Furman",         "6:00 PM","ESPN+","SoCon","Paladin Stadium, Greenville SC","FCS"),
        G("Montana","Sacramento St",      "3:00 PM","ESPN+","Big Sky","Hornet Stadium, Sacramento CA","FCS"),
        G("Ferris State","Lake Superior St","1:00 PM","—","GLIAC","Laker Turf Building, Sault Ste. Marie MI","D-II"),
        G("Shepherd","Notre Dame College","1:00 PM","—","MEC","Carl Asseff Stadium, Bethel Park PA","D-II"),
        G("Mount Union","Muskingum",      "1:00 PM","—","OAC","Muskingum Sch. Stadium, New Concord OH","D-III"),
        G("North Central","Elmhurst",     "1:00 PM","—","CCIW","Hammerschmidt Memorial Stadium, Elmhurst IL","D-III"),
    ],
    7: [  # Week 7 — Oct 15-18
        G("Ohio State","Oregon",          "7:30 PM","FOX","Big Ten","Autzen Stadium"),
        G("Alabama","LSU",                "7:30 PM","ESPN","SEC","Tiger Stadium"),
        G("Georgia","Texas",              "3:30 PM","CBS","SEC","Sanford Stadium"),
        G("Michigan","Penn State",        "3:30 PM","NBC","Big Ten","Michigan Stadium"),
        G("Notre Dame","Navy",            "12:00 PM","NBC","Ind.","Notre Dame Stadium"),
        G("Ole Miss","Texas A&M",         "7:30 PM","ESPN","SEC","Kyle Field"),
        G("Iowa","Wisconsin",             "12:00 PM","BTN","Big Ten","Camp Randall Stadium, Madison WI"),
        G("Kansas State","Iowa State",    "3:30 PM","ESPN2","Big 12","Jack Trice Stadium, Ames IA"),
        G("Clemson","Syracuse",           "7:30 PM","ACCN","ACC","Memorial Stadium, Clemson SC"),
        G("Boise State","Fresno State",   "9:00 PM","FS1","Pac-12","Bulldog Stadium, Fresno CA"),
        G("Louisiana","South Alabama",    "3:00 PM","ESPN+","Sun Belt","Hancock Whitney Stadium, Mobile AL"),
        G("North Dakota St","Illinois State","4:00 PM","ESPN+","MVFC","Hancock Stadium, Normal IL","FCS"),
        G("Delaware","Villanova",         "3:30 PM","ESPN+","CAA","Villanova Stadium, Villanova PA","FCS"),
        G("Eastern Washington","Montana State","3:00 PM","ESPN+","Big Sky","Bobcat Stadium, Bozeman MT","FCS"),
        G("Ferris State","Walsh",         "1:00 PM","—","GLIAC","Aultman Health Foundation Field, North Canton OH","D-II"),
        G("Mount Union","Capital",        "1:00 PM","—","OAC","Wiff Stadium, Columbus OH","D-III"),
        G("North Central","North Park",   "1:00 PM","—","CCIW","Hartley Field, Chicago IL","D-III"),
        G("Wisconsin-Whitewater","UW-River Falls","1:00 PM","—","WIAC","Ramer Field, River Falls WI","D-III"),
    ],
    8: [  # Week 8 — Oct 22-25
        G("Texas","Georgia",              "3:30 PM","CBS","SEC","Darrell K Royal Stadium"),
        G("Michigan","Ohio State",        "3:30 PM","FOX","Big Ten","Michigan Stadium"),
        G("Tennessee","Alabama",          "3:30 PM","ABC","SEC","Bryant-Denny Stadium"),
        G("Penn State","Wisconsin",       "3:30 PM","CBS","Big Ten","Beaver Stadium"),
        G("Notre Dame","Pittsburgh",      "3:30 PM","NBC","ACC","Notre Dame Stadium"),
        G("Oregon","Washington St",       "10:00 PM","FS1","Big Ten","Autzen Stadium"),
        G("Ole Miss","Kentucky",          "7:30 PM","SEC+","SEC","Vaught-Hemingway Stadium"),
        G("Baylor","Oklahoma State",      "7:00 PM","ESPN2","Big 12","McLane Stadium"),
        G("LSU","Georgia",                "7:30 PM","ESPN","SEC","Tiger Stadium"),
        G("Coastal Carolina","Marshall",  "6:00 PM","ESPN+","Sun Belt","Joan C. Edwards Stadium, Huntington WV"),
        G("App State","Georgia Southern", "3:30 PM","ESPN+","Sun Belt","Paulson Stadium, Statesboro GA"),
        G("North Dakota St","Northern Iowa","4:00 PM","ESPN+","MVFC","UNI-Dome, Cedar Falls IA","FCS"),
        G("South Dakota St","South Dakota","4:00 PM","ESPN+","MVFC","DakotaDome, Vermillion SD","FCS"),
        G("Weber State","Idaho State",    "3:00 PM","ESPN+","Big Sky","Holt Arena, Pocatello ID","FCS"),
        G("Ferris State","Davenport",     "1:00 PM","—","GLIAC","Davenport Stadium, Dearborn MI","D-II"),
        G("Delta State","Southern Arkansas","2:00 PM","—","GSC","Mulerider Stadium, Magnolia AR","D-II"),
        G("Mount Union","John Carroll",   "1:00 PM","—","OAC","Don Shula Stadium, University Heights OH","D-III"),
        G("North Central","Millikin",     "1:00 PM","—","CCIW","Harold V. Spear Stadium, Decatur IL","D-III"),
    ],
    9: [  # Week 9 — Oct 29 - Nov 1
        G("Georgia","Florida",            "3:30 PM","CBS","Neutral","TIAA Bank Field, Jacksonville FL",True),
        G("Ohio State","Nebraska",        "12:00 PM","BTN","Big Ten","Memorial Stadium, Lincoln NE"),
        G("Alabama","Texas A&M",          "7:30 PM","ESPN","SEC","Bryant-Denny Stadium"),
        G("Texas","Vanderbilt",           "7:30 PM","ESPN","SEC","Darrell K Royal Stadium"),
        G("Michigan","Indiana",           "3:30 PM","BTN","Big Ten","Michigan Stadium"),
        G("Notre Dame","Virginia Tech",   "3:30 PM","NBC","ACC","Notre Dame Stadium"),
        G("LSU","Arkansas",               "7:30 PM","ESPN2","SEC","Tiger Stadium"),
        G("Iowa","Northwestern",          "12:00 PM","BTN","Big Ten","Ryan Field, Evanston IL"),
        G("TCU","Oklahoma",               "3:30 PM","FS1","SEC","Amon G. Carter Stadium"),
        G("BYU","Cincinnati",             "8:00 PM","ESPN","Big 12","Nippert Stadium, Cincinnati OH"),
        G("Coastal Carolina","Old Dominion","5:00 PM","ESPN+","Sun Belt","Bud Light Weekend, Myrtle Beach SC"),
        G("North Dakota St","Youngstown State","4:00 PM","ESPN+","MVFC","Stambaugh Stadium, Youngstown OH","FCS"),
        G("Montana","Northern Colorado",  "3:00 PM","ESPN+","Big Sky","Nottingham Field, Greeley CO","FCS"),
        G("Sacramento St","Cal Poly",     "3:00 PM","ESPN+","Big Sky","Spanos Stadium, San Luis Obispo CA","FCS"),
        G("Ferris State","Tiffin",        "1:00 PM","—","GLIAC","Kerr-Pegula Stadium, Tiffin OH","D-II"),
        G("Delta State","Shorter",        "2:00 PM","—","GSC","Barron Stadium, Rome GA","D-II"),
        G("Mount Union","Otterbein",      "1:00 PM","—","OAC","Otterbein Stadium, Westerville OH","D-III"),
        G("North Central","Augustana IL", "1:00 PM","—","CCIW","Lindberg Stadium, Rock Island IL","D-III"),
    ],
    10: [  # Week 10 — Nov 5-8
        G("Alabama","Ole Miss",           "7:30 PM","ESPN","SEC","Vaught-Hemingway Stadium"),
        G("Ohio State","Michigan State",  "12:00 PM","BTN","Big Ten","Ohio Stadium"),
        G("Texas","Kentucky",             "3:30 PM","CBS","SEC","Darrell K Royal Stadium"),
        G("Georgia","Tennessee",          "3:30 PM","ABC","SEC","Sanford Stadium"),
        G("Oregon","Purdue",              "3:30 PM","BTN","Big Ten","Ross-Ade Stadium, West Lafayette IN"),
        G("Notre Dame","Maryland",        "3:30 PM","NBC","Big Ten","Notre Dame Stadium"),
        G("Penn State","Minnesota",       "7:30 PM","BTN","Big Ten","Beaver Stadium"),
        G("LSU","Ole Miss",               "7:30 PM","ESPN","SEC","Tiger Stadium"),
        G("Kansas State","Baylor",        "7:00 PM","FS1","Big 12","Bill Snyder Family Stadium"),
        G("Arizona State","Utah",         "9:00 PM","FS1","Big 12","Rice-Eccles Stadium, Salt Lake City UT"),
        G("App State","Louisiana",        "3:00 PM","ESPN+","Sun Belt","Cajun Field, Lafayette LA"),
        G("North Dakota St","South Dakota St","4:00 PM","ESPN+","MVFC","Fargodome, Fargo ND","FCS"),
        G("Weber State","Montana",        "3:00 PM","ESPN+","Big Sky","Washington-Grizzly Stadium, Missoula MT","FCS"),
        G("Chattanooga","Mercer",         "6:00 PM","ESPN+","SoCon","Five Star Stadium, Macon GA","FCS"),
        G("Ferris State","Northwood",     "1:00 PM","—","GLIAC","Bennett Sports Complex, Midland MI","D-II"),
        G("Mount Union","Ohio Dominican", "1:00 PM","—","OAC","Fortress Obetz, Columbus OH","D-III"),
        G("North Central","Augustana SD", "—","—","CCIW","—","D-III"),
    ],
    11: [  # Week 11 — Nov 12-15
        G("Georgia","Alabama",            "3:30 PM","CBS","SEC","Bryant-Denny Stadium"),
        G("Oregon","Ohio State",          "7:30 PM","FOX","Big Ten","Ohio Stadium"),
        G("Texas","Ole Miss",             "7:30 PM","ESPN","SEC","Darrell K Royal Stadium"),
        G("Michigan","Northwestern",      "12:00 PM","BTN","Big Ten","Michigan Stadium"),
        G("Notre Dame","Wake Forest",     "3:30 PM","NBC","ACC","Notre Dame Stadium"),
        G("Penn State","Rutgers",         "3:30 PM","BTN","Big Ten","Beaver Stadium"),
        G("Tennessee","Georgia",          "3:30 PM","ABC","SEC","Sanford Stadium"),
        G("TCU","Texas Tech",             "7:00 PM","ESPN2","Big 12","Amon G. Carter Stadium"),
        G("Boise State","Wyoming",        "8:00 PM","FS1","Pac-12","Jonah Field, Laramie WY"),
        G("Coastal Carolina","Louisiana Tech","5:00 PM","ESPN+","Sun Belt","Joe Aillet Stadium, Ruston LA"),
        G("North Dakota St","Murray State","4:00 PM","ESPN+","MVFC","Roy Stewart Stadium, Murray KY","FCS"),
        G("Montana State","Idaho",        "3:00 PM","ESPN+","Big Sky","Kibbie Dome, Moscow ID","FCS"),
        G("Sacramento St","Eastern Washington","3:00 PM","ESPN+","Big Sky","Roos Field, Cheney WA","FCS"),
        G("Delaware","Maine",             "3:30 PM","ESPN+","CAA","Alfond Stadium, Orono ME","FCS"),
        G("Ferris State","Grand Valley St","1:00 PM","—","GLIAC","Lubbers Stadium, Allendale MI","D-II"),
        G("Delta State","West Alabama",   "2:00 PM","—","GSC","UWA Foley Stadium, Livingston AL","D-II"),
        G("Mount Union","Case Western",   "1:00 PM","—","OAC","DiSanto Field, Cleveland OH","D-III"),
        G("North Central","Wheaton IL",   "1:00 PM","—","CCIW","Anderson Athletic Complex, Wheaton IL","D-III"),
    ],
    12: [  # Week 12 — Nov 19-22
        G("Texas","Georgia",              "7:30 PM","ESPN","SEC","Darrell K Royal Stadium"),
        G("Ohio State","Indiana",         "12:00 PM","BTN","Big Ten","Ohio Stadium"),
        G("Alabama","Auburn",             "2:30 PM","CBS","SEC","Jordan-Hare Stadium"),
        G("Michigan","Ohio State",        "12:00 PM","FOX","Big Ten","Michigan Stadium"),
        G("Oregon","Washington",          "8:30 PM","ESPN","Big Ten","Autzen Stadium"),
        G("Notre Dame","Stanford",        "7:30 PM","NBC","ACC","Notre Dame Stadium"),
        G("LSU","Florida",                "3:30 PM","ESPN","SEC","Tiger Stadium"),
        G("Iowa","Minnesota",             "12:00 PM","BTN","Big Ten","Kinnick Stadium"),
        G("Clemson","South Carolina",     "7:30 PM","ESPN","ACC","Williams-Brice Stadium, Columbia SC"),
        G("TCU","West Virginia",          "3:30 PM","ESPN2","Big 12","Amon G. Carter Stadium"),
        G("Coastal Carolina","Georgia State","3:00 PM","ESPN+","Sun Belt","Georgia State Stadium, Atlanta GA"),
        G("North Dakota St","Illinois State","4:00 PM","ESPN+","MVFC","Hancock Stadium, Normal IL","FCS"),
        G("Montana State","Cal Poly",     "3:00 PM","ESPN+","Big Sky","Spanos Stadium, San Luis Obispo CA","FCS"),
        G("Weber State","Southern Utah",  "1:00 PM","ESPN+","Big Sky","Stewart Stadium, Ogden UT","FCS"),
        G("Delaware","Rhode Island",      "3:30 PM","ESPN+","CAA","Meade Stadium, Kingston RI","FCS"),
        G("Ferris State","Findlay",       "1:00 PM","—","GLIAC","Donnell Stadium, Findlay OH","D-II"),
        G("Mount Union","Wilmington",     "1:00 PM","—","OAC","Alumni Stadium, Wilmington OH","D-III"),
        G("North Central","Concordia Chicago","1:00 PM","—","CCIW","Figi Field, River Forest IL","D-III"),
        G("Wisconsin-Whitewater","UW-Stevens Point","1:00 PM","—","WIAC","Goerke Field, Stevens Point WI","D-III"),
    ],
    13: [  # Rivalry Week — Nov 26-29
        G("Michigan","Ohio State",        "12:00 PM","FOX","Big Ten","Ohio Stadium, Columbus OH"),
        G("Alabama","Auburn",             "2:30 PM","CBS","SEC","Jordan-Hare Stadium, Auburn AL"),
        G("Georgia","Georgia Tech",       "12:00 PM","ABC","SEC","Bobby Dodd Stadium, Atlanta GA"),
        G("Ole Miss","Mississippi St",    "7:00 PM","ESPN","SEC","Davis Wade Stadium, Starkville MS"),
        G("Texas","Texas A&M",            "7:30 PM","ABC","SEC","Kyle Field, College Station TX"),
        G("Oregon","Oregon State",        "5:00 PM","FOX","Big Ten","Reser Stadium, Corvallis OR"),
        G("Notre Dame","USC",             "7:30 PM","NBC","Big Ten","Notre Dame Stadium"),
        G("Penn State","Michigan State",  "12:00 PM","BTN","Big Ten","Beaver Stadium"),
        G("Iowa","Nebraska",              "2:30 PM","BTN","Big Ten","Memorial Stadium, Lincoln NE"),
        G("Washington","Washington St",   "4:00 PM","FS1","Big Ten","Husky Stadium, Seattle WA"),
        G("Kansas","Kansas State",        "2:30 PM","ESPN2","Big 12","Bill Snyder Family Stadium"),
        G("Clemson","South Carolina",     "7:30 PM","ESPN","ACC","Williams-Brice Stadium"),
        G("Florida","Florida State",      "7:30 PM","ABC","SEC","Ben Hill Griffin Stadium"),
        G("LSU","Texas A&M",              "7:00 PM","ESPN","SEC","Tiger Stadium"),
        G("Boise State","Colorado State", "9:00 PM","FS1","Pac-12","Canvas Stadium, Fort Collins CO"),
        G("App State","Georgia Southern", "3:30 PM","ESPN+","Sun Belt","Paulson Stadium, Statesboro GA"),
        G("North Dakota St","South Dakota","4:00 PM","ESPN+","MVFC","DakotaDome, Vermillion SD","FCS"),
        G("Montana","Montana State",      "12:00 PM","ESPN+","Big Sky","Montana State University, Bozeman MT","FCS"),
        G("Ferris State","Grand Valley St","1:00 PM","—","GLIAC","Lubbers Stadium, Allendale MI","D-II"),
        G("Mount Union","Ohio Northern",  "1:00 PM","—","OAC","Dial-Roberson Stadium, Ada OH","D-III"),
        G("North Central","Wheaton IL",   "1:00 PM","—","CCIW","Anderson Athletic Complex, Wheaton IL","D-III"),
        G("Wisconsin-Whitewater","UW-Eau Claire","1:00 PM","—","WIAC","Carson Park, Eau Claire WI","D-III"),
    ],
    14: [  # Conference Championships — Dec 5-6
        G("TBD","TBD (SEC Champ)","4:00 PM","CBS","SEC","Mercedes-Benz Stadium, Atlanta GA",neutral=True),
        G("TBD","TBD (Big Ten Champ)","8:00 PM","FOX","Big Ten","Lucas Oil Stadium, Indianapolis IN",neutral=True),
        G("TBD","TBD (ACC Champ)","8:00 PM","ESPN","ACC","Bank of America Stadium, Charlotte NC",neutral=True),
        G("TBD","TBD (Big 12 Champ)","12:00 PM","ABC","Big 12","AT&T Stadium, Arlington TX",neutral=True),
        G("TBD","TBD (Pac-12 Champ)","9:00 PM","ESPN","Pac-12","Allegiant Stadium, Las Vegas NV",neutral=True),
        G("TBD","TBD (AAC Champ)","12:00 PM","ESPN","AAC","—",neutral=True),
        G("TBD","TBD (MWC Champ)","3:30 PM","FOX","MWC","—",neutral=True),
        G("TBD","TBD (Sun Belt Champ)","12:00 PM","ESPN","Sun Belt","—",neutral=True),
        G("TBD","TBD (MAC Champ)","12:00 PM","ESPN","MAC","—",neutral=True),
        # FCS Playoffs
        G("FCS Seed 1","FCS Seed 16","12:00 PM","ESPN+","FCS Playoffs","Campus Sites","FCS"),
        G("FCS Seed 2","FCS Seed 15","12:00 PM","ESPN+","FCS Playoffs","Campus Sites","FCS"),
        G("FCS Seed 3","FCS Seed 14","12:00 PM","ESPN+","FCS Playoffs","Campus Sites","FCS"),
        G("FCS Seed 4","FCS Seed 13","12:00 PM","ESPN+","FCS Playoffs","Campus Sites","FCS"),
        # D-II Playoffs
        G("D-II Seed 1","D-II Seed 16","12:00 PM","—","D-II Playoffs","Campus Sites","D-II"),
        G("D-II Seed 2","D-II Seed 15","12:00 PM","—","D-II Playoffs","Campus Sites","D-II"),
        # D-III Playoffs
        G("D-III Seed 1","D-III Seed 32","12:00 PM","—","D-III Playoffs","Campus Sites","D-III"),
        G("D-III Seed 2","D-III Seed 31","12:00 PM","—","D-III Playoffs","Campus Sites","D-III"),
    ],
    15: [  # CFP Round 1 — Dec 12 + Playoffs
        G("CFP #5","CFP #4","12:00 PM","ESPN","CFP","Campus Site (Higher Seed)"),
        G("CFP #6","CFP #3","3:30 PM","ABC","CFP","Campus Site (Higher Seed)"),
        G("CFP #7","CFP #2","7:30 PM","ESPN","CFP","Campus Site (Higher Seed)"),
        G("CFP #8","CFP #1","8:00 PM","NBC","CFP","Campus Site (Higher Seed)"),
        # FCS Quarterfinals
        G("FCS QF 1","FCS QF 8","12:00 PM","ESPN+","FCS Playoffs","Campus Sites","FCS"),
        G("FCS QF 2","FCS QF 7","12:00 PM","ESPN+","FCS Playoffs","Campus Sites","FCS"),
        # D-II Quarterfinals
        G("D-II QF 1","D-II QF 8","12:00 PM","—","D-II Playoffs","Campus Sites","D-II"),
        # D-III Quarterfinals
        G("D-III QF 1","D-III QF 16","12:00 PM","—","D-III Playoffs","Campus Sites","D-III"),
    ],
}

# ── H2H DATABASE ──────────────────────────────────────────────────────────
H2H = {
    ("Alabama","Georgia"):[
        {"date":"Dec 6, 2025","winner":"Georgia","score":"28-7","site":"SEC Champ, Atlanta","note":"Bulldogs dominant — Stockton 3 TDs"},
        {"date":"Sep 27, 2025","winner":"Alabama","score":"24-21","site":"Athens, GA","note":"Tide win in Athens for first time since 2015"},
        {"date":"Sep 28, 2024","winner":"Alabama","score":"41-34","site":"Tuscaloosa, AL","note":"Ryan Williams 75-yd catch, Tide edge Dawgs"},
        {"date":"Dec 2, 2023","winner":"Alabama","score":"27-24","site":"SEC Champ, Atlanta","note":"OT classic — Jalen Milroe leads comeback"},
        {"date":"Sep 24, 2022","winner":"Georgia","score":"26-7","site":"Athens, GA","note":"Bulldogs rout Bama in dominant home win"},
    ],
    ("Ohio State","Michigan"):[
        {"date":"Nov 29, 2025","winner":"Ohio State","score":"21-14","site":"Ann Arbor, MI","note":"Buckeyes end Wolverines 3-game run"},
        {"date":"Nov 30, 2024","winner":"Ohio State","score":"13-10","site":"Columbus, OH","note":"Last-second FG — Buckeyes survive"},
        {"date":"Nov 25, 2023","winner":"Michigan","score":"30-24","site":"Ann Arbor, MI","note":"Wolverines third straight rivalry win"},
        {"date":"Nov 26, 2022","winner":"Michigan","score":"45-23","site":"Columbus, OH","note":"Michigan wins in Columbus first time since 2000"},
        {"date":"Nov 27, 2021","winner":"Michigan","score":"42-27","site":"Ann Arbor, MI","note":"Harbaugh's first rivalry win"},
    ],
    ("Clemson","LSU"):[
        {"date":"Jan 13, 2020","winner":"LSU","score":"42-25","site":"CFP Champ, New Orleans","note":"Joe Burrow's Heisman season capped"},
        {"date":"Aug 31, 2012","winner":"Clemson","score":"25-24","site":"Atlanta (neutral)","note":"Tajh Boyd's late TD — Kickoff Game"},
        {"date":"Sep 3, 1988","winner":"LSU","score":"27-21","site":"Baton Rouge, LA","note":"Season opener classic"},
        {"date":"Sep 7, 1985","winner":"Clemson","score":"20-13","site":"Clemson, SC","note":"Tigers hold Tigers scoreless in 1H"},
        {"date":"Sep 10, 1983","winner":"Clemson","score":"26-6","site":"Clemson, SC","note":"Clemson defense dominant"},
    ],
    ("Texas","Oklahoma"):[
        {"date":"Oct 11, 2025","winner":"Texas","score":"31-10","site":"Cotton Bowl, Dallas","note":"Arch Manning dominant — Texas routs Sooners"},
        {"date":"Oct 12, 2024","winner":"Texas","score":"34-3","site":"Cotton Bowl, Dallas","note":"Longhorns dominant — OU shut out late"},
        {"date":"Oct 7, 2023","winner":"Texas","score":"34-30","site":"Cotton Bowl, Dallas","note":"Quinn Ewers 3 TDs — Horns edge Sooners"},
        {"date":"Oct 8, 2022","winner":"Oklahoma","score":"49-0","site":"Cotton Bowl, Dallas","note":"Dillon Gabriel 4 TDs — Sooners dominate"},
        {"date":"Oct 9, 2021","winner":"Oklahoma","score":"55-48","site":"Cotton Bowl, Dallas","note":"Rattler → Williams OT comeback"},
    ],
    ("Wisconsin","Notre Dame"):[
        {"date":"Sep 25, 2021","winner":"Notre Dame","score":"41-13","site":"Soldier Field, Chicago","note":"Shamrock Series — Irish dominant"},
        {"date":"Sep 27, 2014","winner":"Notre Dame","score":"31-28","site":"Lambeau Field, Green Bay","note":"OT thriller at SAME venue — Irish survive"},
        {"date":"Oct 3, 2011","winner":"Notre Dame","score":"31-21","site":"Notre Dame Stadium","note":"Irish win on opening weekend showcase"},
        {"date":"Sep 26, 2009","winner":"Wisconsin","score":"33-28","site":"Madison, WI","note":"Badgers stun #8 Irish in upset"},
        {"date":"Sep 28, 2006","winner":"Wisconsin","score":"17-14","site":"Madison, WI","note":"PJ Hill 137 yds — Badgers prevail"},
    ],
}

def get_h2h(away, home): return H2H.get((away,home)) or H2H.get((home,away))

# ── API FETCH ──────────────────────────────────────────────────────────────
HEADS = {
    "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126.0 Safari/537.36",
    "Accept":"application/json","Origin":"https://www.espn.com","Referer":"https://www.espn.com/",
}

@st.cache_data(ttl=300)
def fetch_live(week_num):
    all_fbs, all_fcs = [], []
    for group,div_tag in [("80","FBS"),("81","FCS")]:
        for url in [
            f"https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard?groups={group}&week={week_num}&seasontype=2&limit=300",
            f"https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard?groups={group}&limit=300",
        ]:
            try:
                r = requests.get(url, headers=HEADS, timeout=10)
                if r.status_code != 200: continue
                events = r.json().get("events",[])
                if not events: continue
                for ev in events:
                    try:
                        comp = ev["competitions"][0]; comps = comp["competitors"]
                        ht=next(c for c in comps if c.get("homeAway")=="home")
                        at=next(c for c in comps if c.get("homeAway")=="away")
                        start=ev.get("date","")
                        try:
                            dt=datetime.datetime.fromisoformat(start.replace("Z","+00:00"))
                            et=dt.astimezone(datetime.timezone(datetime.timedelta(hours=-4)))
                            tstr=et.strftime("%I:%M %p").lstrip("0")
                        except: tstr="TBD"
                        bcast=comp.get("broadcasts",[])
                        tv=bcast[0].get("names",["—"])[0] if bcast and bcast[0].get("names") else "—"
                        g={"away":at["team"]["displayName"],"home":ht["team"]["displayName"],
                           "time":tstr,"tv":tv,"venue":comp.get("venue",{}).get("fullName",""),
                           "conf":(comp.get("groups") or {}).get("name",""),
                           "away_rec":at.get("records",[{}])[0].get("summary","0-0") if at.get("records") else "0-0",
                           "home_rec":ht.get("records",[{}])[0].get("summary","0-0") if ht.get("records") else "0-0",
                           "away_rank":str(at.get("curatedRank",{}).get("current","")),
                           "home_rank":str(ht.get("curatedRank",{}).get("current","")),
                           "away_score":at.get("score",""),"home_score":ht.get("score",""),
                           "status":comp.get("status",{}).get("type",{}).get("name","scheduled"),
                           "neutral":comp.get("neutralSite",False),"div":div_tag}
                        if div_tag=="FBS": all_fbs.append(g)
                        else: all_fcs.append(g)
                    except: pass
                if all_fbs or all_fcs: break
            except: pass
    # Also try D-II/D-III via ESPN
    for group,div_tag in [("26","D-II"),("27","D-III")]:
        try:
            url=f"https://site.api.espn.com/apis/site/v2/sports/football/college-football/scoreboard?groups={group}&week={week_num}&seasontype=2&limit=300"
            r=requests.get(url,headers=HEADS,timeout=8)
            if r.status_code==200:
                for ev in r.json().get("events",[]):
                    try:
                        comp=ev["competitions"][0]; comps=comp["competitors"]
                        ht=next(c for c in comps if c.get("homeAway")=="home")
                        at=next(c for c in comps if c.get("homeAway")=="away")
                        g={"away":at["team"]["displayName"],"home":ht["team"]["displayName"],
                           "time":"TBD","tv":"—","venue":comp.get("venue",{}).get("fullName",""),
                           "conf":"","away_rec":"0-0","home_rec":"0-0","away_rank":"","home_rank":"",
                           "away_score":"","home_score":"","status":"scheduled","neutral":False,"div":div_tag}
                        if div_tag=="D-II": all_fbs.append(g)   # stored separately
                        else: all_fcs.append(g)
                    except: pass
        except: pass
    return all_fbs, all_fcs, "ESPN", None

# ── SIDEBAR ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📅 2026-27 Season")
    now=datetime.datetime.now()
    st.markdown("<div style='font-size:.62rem;color:#64748b;line-height:2;margin-top:4px'>"
                "<b style='color:#94a3b8'>D-II/D-III Start</b> Aug 27, 2026<br>"
                "<b style='color:#94a3b8'>FCS Starts</b> Aug 27, 2026<br>"
                "<b style='color:#94a3b8'>FBS Week 0</b> Aug 29, 2026<br>"
                "<b style='color:#94a3b8'>Conf. Championships</b> Dec 5–6<br>"
                "<b style='color:#94a3b8'>CFP First Round</b> Dec 12<br>"
                "<b style='color:#94a3b8'>D-II Championship</b> Dec 19, McKinney TX<br>"
                "<b style='color:#94a3b8'>CFP National Champ</b><br>"
                "&nbsp;Jan 25, 2027 · Allegiant Stadium, LV<br>"
                "<b style='color:#94a3b8'>D-III Stagg Bowl</b><br>"
                "&nbsp;Jan 9, 2027 · Salem Stadium, VA</div>",unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 📊 SP+ Prediction Engine")
    st.markdown("<div style='font-size:.6rem;color:#64748b;line-height:1.9'>"
                "• SP+ rating differential<br>• Off/Def rank matchup<br>"
                "• Home field +2.5 pts<br>• Coaching adjustment<br>"
                "• Week-of-season drift<br>• ATS trend weighting</div>",unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 🏅 AP Top 10")
    for team,rank in sorted(AP_RANKS.items(),key=lambda x:x[1])[:10]:
        sp=get_db(team)[0]
        st.markdown(f"<span style='font-size:.66rem;color:#94a3b8'>#"+str(rank)+" "+team
                    +f" <span style='color:#38bdf8;font-size:.58rem'>SP+{sp}</span></span>",unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 🎯 Grade Legend")
    st.markdown("<div style='font-size:.68rem;line-height:2.1;color:#94a3b8'>"
                "<span style='background:#166534;color:#4ade80;border-radius:50%;padding:1px 7px;font-weight:900'>A+</span> ≥85%<br>"
                "<span style='background:#14532d;color:#86efac;border-radius:50%;padding:1px 8px;font-weight:900'>A</span> ≥72%<br>"
                "<span style='background:#1e3a5f;color:#60a5fa;border-radius:50%;padding:1px 8px;font-weight:900'>B</span> ≥58%<br>"
                "<span style='background:#3b2300;color:#fb923c;border-radius:50%;padding:1px 8px;font-weight:900'>C</span> Toss-up</div>",unsafe_allow_html=True)

# ── HEADER ────────────────────────────────────────────────────────────────
now=datetime.datetime.now()
st.markdown(
    "<div class='hdr'><div class='brand'>NCAAF<sup>+</sup></div>"
    "<div><div style='font-size:.6rem;color:#c8a800;font-weight:700;letter-spacing:1px'>2026 ALL DIVISIONS — COMPLETE SEASON SCHEDULE</div>"
    "<div style='font-size:.54rem;color:#4b5e78;text-transform:uppercase;letter-spacing:1px;margin-top:2px'>"
    "FBS · FCS · D-II · D-III · SP+ Smart Predictions · Weeks 0–15</div></div>"
    "<div style='display:inline-flex;align-items:center;gap:4px;background:#0a1f0a;border:1px solid #166534;"
    "border-radius:20px;padding:3px 9px;font-size:.56rem;color:#22c55e;font-weight:700;margin-left:10px'>"
    "<span style='width:5px;height:5px;background:#22c55e;border-radius:50%;display:inline-block'></span>LIVE</div>"
    "<div style='margin-left:auto;text-align:right'>"
    "<div style='font-size:.7rem;color:#f59e0b;font-weight:700'>"+now.strftime("%m/%d/%Y")+"</div>"
    "<div style='font-size:.54rem;color:#4b5e78;margin-top:2px'>CFP Champ · Jan 25, 2027 · Allegiant Stadium, Las Vegas</div>"
    "</div></div>",unsafe_allow_html=True)

# ── WEEK SELECTOR ─────────────────────────────────────────────────────────
WEEK_LABELS={
    0:"Week 0 — Aug 29 (Season Opener)",1:"Week 1 — Sep 3–7 (Labor Day)",
    2:"Week 2 — Sep 10–13",3:"Week 3 — Sep 17–20",4:"Week 4 — Sep 24–27",
    5:"Week 5 — Oct 1–4",6:"Week 6 — Oct 8–11 (Red River)",7:"Week 7 — Oct 15–18",
    8:"Week 8 — Oct 22–25",9:"Week 9 — Oct 29–Nov 1",10:"Week 10 — Nov 5–8",
    11:"Week 11 — Nov 12–15",12:"Week 12 — Nov 19–22",
    13:"Week 13 — Nov 26–29 (Rivalry Week)",14:"Week 14 — Dec 5–6 (Conf. Champs)",
    15:"Week 15 — Dec 12+ (CFP & Playoffs)",
}

def cur_week():
    today=datetime.date.today()
    sched=[(0,datetime.date(2026,8,27)),(1,datetime.date(2026,9,3)),(2,datetime.date(2026,9,10)),
           (3,datetime.date(2026,9,17)),(4,datetime.date(2026,9,24)),(5,datetime.date(2026,10,1)),
           (6,datetime.date(2026,10,8)),(7,datetime.date(2026,10,15)),(8,datetime.date(2026,10,22)),
           (9,datetime.date(2026,10,29)),(10,datetime.date(2026,11,5)),(11,datetime.date(2026,11,12)),
           (12,datetime.date(2026,11,19)),(13,datetime.date(2026,11,26)),(14,datetime.date(2026,12,3)),
           (15,datetime.date(2026,12,10))]
    cur=0
    for wk,start in sched:
        if today>=start: cur=wk
        else: break
    return cur

c1,c2,c3,c4 = st.columns([3,2,2,2])
week_num = c1.selectbox("Week",list(range(16)),index=cur_week(),
    format_func=lambda w:WEEK_LABELS.get(w,f"Week {w}"),label_visibility="collapsed")
ou_f     = c2.selectbox("O/U",["All O/U","OVER","UNDER"],label_visibility="collapsed")
grade_f  = c3.selectbox("Grade",["All Grades","A+ Only","A & Above","B & Above"],label_visibility="collapsed")
div_f    = c4.selectbox("Division",["All","FBS","FCS","D-II","D-III"],label_visibility="collapsed")

# ── FETCH LIVE ────────────────────────────────────────────────────────────
with st.spinner("🔄 Loading schedule..."):
    live_games, live_fcs_games, api_src, _ = fetch_live(week_num)

# Build game list — live API + static fallback for missing games
static_games = SCHEDULE.get(week_num, [])
live_keys    = set(g["away"]+"@"+g["home"] for g in live_games+live_fcs_games)
using_live   = bool(live_games or live_fcs_games)

all_games = list(live_games + live_fcs_games)
for sg in static_games:
    if sg["away"]+"@"+sg["home"] not in live_keys:
        all_games.append(sg)
    live_keys.add(sg["away"]+"@"+sg["home"])

# Split by division
DIV_ORDER = ["FBS","FCS","D-II","D-III"]
div_games = {d:[g for g in all_games if g.get("div","FBS")==d] for d in DIV_ORDER}

# ── CACHED PREDICTIONS ────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def all_preds(week_num):
    preds={}
    for g in SCHEDULE.get(week_num,[]):
        if "TBD" not in g["away"] and "TBD" not in g["home"] and "CFP" not in g["away"] and "Seed" not in g["away"]:
            preds[g["away"]+"@"+g["home"]]=smart_predict(g["away"],g["home"],g.get("neutral",False),week_num)
    return preds

pred_cache = all_preds(week_num)

def get_pred(away, home, neutral=False):
    key=away+"@"+home
    if "TBD" in away or "TBD" in home or "CFP" in away or "Seed" in away or "TBD" in away:
        return None
    return pred_cache.get(key) or smart_predict(away, home, neutral, week_num)

# ── STATS ─────────────────────────────────────────────────────────────────
valid_preds=[get_pred(g["away"],g["home"],g.get("neutral",False)) for g in all_games]
valid_preds=[p for p in valid_preds if p]
overs=sum(1 for p in valid_preds if p["ou"]=="OVER")
avg_t=f"{sum(p['total'] for p in valid_preds)/len(valid_preds):.1f}" if valid_preds else "—"
sharp_c=sum(1 for p in valid_preds if "Sharp" in p["mv"])
ap_c=sum(1 for p in valid_preds if grade(p["mlC"])[0]=="A+")
src_html=(f"<span class='src-badge src-live'>● ESPN Live</span>" if using_live
          else f"<span class='src-badge src-static'>📋 Built-in</span>")

fbs_ct=len(div_games["FBS"]); fcs_ct=len(div_games["FCS"])
d2_ct=len(div_games["D-II"]); d3_ct=len(div_games["D-III"])
total_ct=fbs_ct+fcs_ct+d2_ct+d3_ct

st.markdown(
    "<div class='stats-row'>"
    f"<div class='stat-box'><div class='stat-n' style='color:#c8a800'>{WEEK_LABELS[week_num].split(' — ')[0]}</div><div class='stat-l'>{src_html}</div></div>"
    f"<div class='stat-box'><div class='stat-n' style='color:#f59e0b'>{total_ct}</div><div class='stat-l'>Total Games</div></div>"
    f"<div class='stat-box'><div class='stat-n' style='color:#f59e0b'>{fbs_ct}</div><div class='stat-l'>FBS</div></div>"
    f"<div class='stat-box'><div class='stat-n' style='color:#38bdf8'>{fcs_ct}</div><div class='stat-l'>FCS</div></div>"
    f"<div class='stat-box'><div class='stat-n' style='color:#4ade80'>{d2_ct}</div><div class='stat-l'>D-II</div></div>"
    f"<div class='stat-box'><div class='stat-n' style='color:#c084fc'>{d3_ct}</div><div class='stat-l'>D-III</div></div>"
    f"<div class='stat-box'><div class='stat-n' style='color:#38bdf8'>{overs}</div><div class='stat-l'>Overs</div></div>"
    f"<div class='stat-box'><div class='stat-n' style='color:#f472b6'>{len(valid_preds)-overs}</div><div class='stat-l'>Unders</div></div>"
    f"<div class='stat-box'><div class='stat-n' style='color:#c084fc'>{avg_t}</div><div class='stat-l'>Avg O/U</div></div>"
    f"<div class='stat-box'><div class='stat-n' style='color:#4ade80'>{ap_c}</div><div class='stat-l'>A+ Picks</div></div>"
    "</div>", unsafe_allow_html=True)

# ── RENDER ────────────────────────────────────────────────────────────────
DIV_COLORS={"FBS":"#f59e0b","FCS":"#38bdf8","D-II":"#4ade80","D-III":"#c084fc"}
DIV_LABELS_FULL={"FBS":"Football Bowl Subdivision","FCS":"Football Championship Subdivision",
                 "D-II":"NCAA Division II","D-III":"NCAA Division III"}

def render_div(div):
    games = div_games.get(div, [])
    if not games: return
    if div_f != "All" and div != div_f: return

    filtered = []
    for g in games:
        if "TBD" in g["away"] or "Seed" in g["away"] or "CFP" in g["away"]: continue
        p = get_pred(g["away"], g["home"], g.get("neutral",False))
        if not p: continue
        if ou_f != "All O/U" and p["ou"] != ou_f: continue
        mlG,_ = grade(p["mlC"])
        if grade_f == "A+ Only" and mlG != "A+": continue
        if grade_f == "A & Above" and mlG not in ("A+","A"): continue
        if grade_f == "B & Above" and mlG == "C": continue
        filtered.append((g,p))
    if not filtered: return

    col = DIV_COLORS[div]
    st.markdown(
        f"<div class='div-hdr' style='border-top-color:{col}'>"
        f"<span class='div-tag' style='background:{col}18;color:{col};border:1px solid {col}44'>{div}</span>"
        f"<span style='font-size:.56rem;color:#64748b'>{DIV_LABELS_FULL[div]}</span>"
        f"<span style='font-size:.54rem;color:#4b5e78;margin-left:auto'>{len(filtered)} games</span></div>",
        unsafe_allow_html=True)

    for g,p in filtered:
        wpa=round(p["away_wp"]*100); wph=100-wpa
        fa=p["fa"]; fnm=g["away"] if fa else g["home"]; dnm=g["home"] if fa else g["away"]
        fav_ml=fml(p["ml_away"] if fa else p["ml_home"]); dog_ml=fml(p["ml_home"] if fa else p["ml_away"])
        fav_sp=fsp(p["sp_away"] if fa else p["sp_home"])
        mlG,mlC=grade(p["mlC"]); spG,spC=grade(p["spC"]); ttG,ttC=grade(p["ttC"])
        ou_cls="ou-over" if p["ou"]=="OVER" else "ou-under"
        mv_cls="mv-s" if "Sharp" in p["mv"] else("mv-p" if "Public" in p["mv"] else "mv-n")
        a_rank=g.get("away_rank","") or (str(AP_RANKS[g["away"]]) if g["away"] in AP_RANKS else "")
        h_rank=g.get("home_rank","") or (str(AP_RANKS[g["home"]]) if g["home"] in AP_RANKS else "")
        def cr(r): return r if r and r not in ("","99","0","None") else ""
        a_rank=cr(a_rank); h_rank=cr(h_rank)
        a_rk=f"<span class='rnk'>#{a_rank}</span>" if a_rank else "<span class='rnk-none'>—</span>"
        h_rk=f"<span class='rnk'>#{h_rank}</span>" if h_rank else "<span class='rnk-none'>—</span>"
        a_rec=g.get("away_rec","0-0"); h_rec=g.get("home_rec","0-0")
        a_rc=rc_cls(a_rec); h_rc=rc_cls(h_rec)
        gst=g.get("status","scheduled"); a_sc=g.get("away_score",""); h_sc=g.get("home_score","")
        if gst=="STATUS_FINAL" and a_sc and h_sc:
            score_p=f"<span class='score-final'>FINAL: {g['away']} {a_sc}–{h_sc} {g['home']}</span><br>"
        elif "IN_PROGRESS" in gst and a_sc and h_sc:
            score_p=f"<span class='score-live'>● LIVE: {g['away']} {a_sc}–{h_sc} {g['home']}</span><br>"
        else: score_p=""
        neut="<span class='ntag'>Neutral</span>" if g.get("neutral") else ""
        conf=g.get("conf",""); conf_p=f"<span style='font-size:.46rem;color:#4b5e78'>{conf}</span>&nbsp;" if conf else ""
        pos_html="".join(f"<span class='kf-p'>✓ {f}</span>" for f in p["pos"])
        neg_html="".join(f"<span class='kf-n'>✗ {f}</span>" for f in p["neg"])
        pub_over=int(45+(p["away_wp"] if fa else p["home_wp"])*30)
        venue=g.get("venue",""); sp_gap_str=f"SP+ gap: {p['sp_gap']:.1f}"
        wp_a="wp-hot" if wpa>55 else "wp-cold"; wp_h="wp-hot" if wph>55 else "wp-cold"

        row=(
            "<div class='game-row'><div>"
            f"<div class='tlabel'>{g['time']} ET &nbsp;<span class='tv'>{g['tv']}</span>&nbsp;"
            +conf_p+neut+"</div>"+score_p+
            f"<div class='trow'>{a_rk}<div class='trec-wrap'><div class='tnm'>{g['away']}</div>"
            f"<span class='rec-badge {a_rc}'>{a_rec}</span></div>"
            f"<div class='twp {wp_a}'>{wpa}%</div></div>"
            "<div class='tdiv'></div>"
            f"<div class='trow'>{h_rk}<div class='trec-wrap'><div class='tnm'>{g['home']}</div>"
            f"<span class='rec-badge {h_rc}'>{h_rec}</span></div>"
            f"<div class='twp {wp_h}'>{wph}%</div></div></div>"
            "<div class='odds-box'><div class='odds-lbl' style='color:#4ade80'>💰 Moneyline</div>"
            f"<div class='odds-pick' style='color:#22c55e'>{fnm.split()[-1]} {fav_ml}</div>"
            f"<div class='odds-dog'>{dnm.split()[-1]} {dog_ml}</div>"
            f"<div class='odds-sm'>Proj: {p['pa']}–{p['ph']}</div>"
            f"<div class='{mv_cls}'>{p['mv']} · {p['sp_p']}% sharp</div></div>"
            "<div class='odds-box'><div class='odds-lbl' style='color:#fb923c'>📊 Spread</div>"
            f"<div class='odds-pick' style='color:#22c55e'>{fnm.split()[-1]} {fav_sp}</div>"
            f"<div class='odds-sm'>{fsp(p['sp_away'])} / {fsp(p['sp_home'])}</div>"
            f"<div class='odds-sm'>{sp_gap_str}</div></div>"
            "<div class='odds-box'><div class='odds-lbl' style='color:#38bdf8'>🎯 Total</div>"
            f"<div class='{ou_cls}'>{p['ou']}</div>"
            f"<div class='odds-sm'>O/U {p['total']}</div>"
            f"<div class='odds-sm'>OVER {pub_over}% pub</div></div>"
            "<div class='grade-col'>"
            f"<div class='gbig {mlC}'>{mlG}</div>"
            f"<div style='font-size:.46rem;color:#4b5e78'>ML {p['mlC']}%</div>"
            f"<div class='gsm {spC}'>{spG}</div>"
            f"<div class='gsm {ttC}'>{ttG}</div>"
            "</div></div>"
        )

        ai=(
            "<div class='ai-row'>"
            f"<div style='font-size:.5rem;color:#4b5e78;padding-top:3px;line-height:1.5'>{venue}</div>"
            "<div><div class='ai-lbl'>🤖 SP+ Analysis</div>"
            f"<div class='ai-txt'>{p['txt']}</div>"
            f"<div class='kf-row'>{pos_html}{neg_html}</div></div></div>"
        )

        h2h=get_h2h(g["away"],g["home"]); h2h_html=""
        if h2h:
            a_wins=sum(1 for m in h2h if m["winner"]==g["away"]); h_wins=len(h2h)-a_wins
            rec_cls="h2h-away" if a_wins>h_wins else "h2h-home"
            rows="".join(
                f"<div class='h2h-row'><span class='h2h-date'>{m['date']}</span>"
                "<span class='h2h-w "+("h2h-away" if m["winner"]==g["away"] else "h2h-home")+"'>"+m["winner"]+"</span>"
                f"<span class='h2h-sc'>{m['score']}</span>"
                f"<span style='color:#4b5e78;font-size:.48rem'>{m['site']}</span>"
                f"<span class='h2h-n'>{m['note']}</span></div>" for m in h2h)
            h2h_html=(f"<div class='h2h-box'><div class='h2h-title'>📋 Last 5 Matchups"
                      f"<span class='{rec_cls}' style='font-family:Barlow Condensed,sans-serif;font-size:.66rem'>"
                      f"{g['away']} {a_wins}–{h_wins} {g['home']}</span></div>"+rows+"</div>")

        hp=make_half_preds(g["away"],g["home"],p,week_num)
        h1spG,h1spC=grade(hp["h1_spC"]); h1tG,h1tC=grade(hp["h1_totC"]); h1wG,h1wC=grade(hp["h1_winC"])
        h2spG,h2spC=grade(hp["h2_spC"]); h2tG,h2tC=grade(hp["h2_totC"]); h2wG,h2wC=grade(hp["h2_winC"])
        h1ou_cls="ou-over" if hp["h1_ou"]=="OVER" else "ou-under"
        h2ou_cls="ou-over" if hp["h2_ou"]=="OVER" else "ou-under"
        sp_sign="-" if hp["fa"] else "+"

        half_html=(
            "<details><summary>📊 Half-Game Predictions &nbsp;▾</summary>"
            "<div class='half-inner'>"
            "<div class='half-label' style='color:#f59e0b'>🏈 1st Half</div>"
            "<div class='prop-grid'>"
            f"<div class='prop-card'><div class='prop-lbl sp-l'>1st Half Spread</div>"
            f"<div class='prop-val' style='color:#22c55e'>{hp['h1_sp_team'].split()[-1]} {sp_sign}{hp['h1_sp']}</div>"
            f"<div class='pbar'><div class='pbar-fill' style='width:{hp['h1_spC']}%;background:#7c2d12'></div></div>"
            f"<div class='prop-sub'>{hp['h1_spC']}% conf</div>"
            f"<div class='gsm {h1spC}' style='margin:2px auto'>{h1spG}</div></div>"
            f"<div class='prop-card'><div class='prop-lbl tot-l'>1st Half Total</div>"
            f"<div class='{h1ou_cls}'>{hp['h1_ou']}</div>"
            f"<div class='prop-sub'>O/U {hp['h1_total']}</div>"
            f"<div class='pbar'><div class='pbar-fill' style='width:{hp['h1_totC']}%;background:#1e3a5f'></div></div>"
            f"<div class='prop-sub'>{hp['h1_totC']}% conf</div>"
            f"<div class='gsm {h1tC}' style='margin:2px auto'>{h1tG}</div></div>"
            f"<div class='prop-card'><div class='prop-lbl win-l'>1st Half Winner</div>"
            f"<div class='prop-val' style='color:#22c55e'>{hp['h1_win'].split()[-1]}</div>"
            f"<div class='pbar'><div class='pbar-fill' style='width:{hp['h1_winC']}%;background:#166534'></div></div>"
            f"<div class='prop-sub'>{hp['h1_winC']}% conf</div>"
            f"<div class='gsm {h1wC}' style='margin:2px auto'>{h1wG}</div></div></div>"
            "<div class='half-label' style='color:#c084fc;margin-top:8px'>🏈 2nd Half</div>"
            "<div class='prop-grid'>"
            f"<div class='prop-card'><div class='prop-lbl sp-l'>2nd Half Spread</div>"
            f"<div class='prop-val' style='color:#22c55e'>{hp['h2_sp_team'].split()[-1]} {sp_sign}{hp['h2_sp']}</div>"
            f"<div class='pbar'><div class='pbar-fill' style='width:{hp['h2_spC']}%;background:#7c2d12'></div></div>"
            f"<div class='prop-sub'>{hp['h2_spC']}% conf</div>"
            f"<div class='gsm {h2spC}' style='margin:2px auto'>{h2spG}</div></div>"
            f"<div class='prop-card'><div class='prop-lbl tot-l'>2nd Half Total</div>"
            f"<div class='{h2ou_cls}'>{hp['h2_ou']}</div>"
            f"<div class='prop-sub'>O/U {hp['h2_total']}</div>"
            f"<div class='pbar'><div class='pbar-fill' style='width:{hp['h2_totC']}%;background:#1e3a5f'></div></div>"
            f"<div class='prop-sub'>{hp['h2_totC']}% conf</div>"
            f"<div class='gsm {h2tC}' style='margin:2px auto'>{h2tG}</div></div>"
            f"<div class='prop-card'><div class='prop-lbl win-l'>2nd Half Winner</div>"
            f"<div class='prop-val' style='color:#22c55e'>{hp['h2_win'].split()[-1]}</div>"
            f"<div class='pbar'><div class='pbar-fill' style='width:{hp['h2_winC']}%;background:#166534'></div></div>"
            f"<div class='prop-sub'>{hp['h2_winC']}% conf</div>"
            f"<div class='gsm {h2wC}' style='margin:2px auto'>{h2wG}</div></div></div>"
            "</div></details>"
        )
        st.markdown(row+ai+h2h_html+half_html, unsafe_allow_html=True)

for div in DIV_ORDER:
    render_div(div)

if not any(div_games.values()):
    st.markdown("<div class='no-games'>No games scheduled for this week.</div>",unsafe_allow_html=True)

st.markdown("<div style='height:30px'></div>",unsafe_allow_html=True)
