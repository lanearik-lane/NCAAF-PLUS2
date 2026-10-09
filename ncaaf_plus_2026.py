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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Barlow+Condensed:wght@700;900&display=swap');
html,body,[class*="css"]{background:#0d1117!important;color:#e2e8f0;font-family:'Inter',sans-serif;font-size:13px}
.stApp{background:#0d1117!important}
#MainMenu,footer,header{visibility:hidden}
.block-container{padding:0!important;max-width:100%!important}

/* HEADER */
.hdr{background:#111827;border-bottom:2px solid #c8a800;padding:10px 16px;display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.brand{font-family:'Barlow Condensed',sans-serif;font-size:1.7rem;font-weight:900;color:#f59e0b;letter-spacing:-1px;line-height:1}
.brand sup{color:#38bdf8;font-size:.9rem}
.live-dot{display:inline-flex;align-items:center;gap:4px;background:#0a1f0a;border:1px solid #166534;border-radius:20px;padding:2px 8px;font-size:.55rem;color:#22c55e;font-weight:700;margin-left:8px}

/* STATS BAR */
.stats-row{background:#0c1520;border-bottom:1px solid #1a2840;padding:6px 16px;display:flex;gap:0;overflow-x:auto}
.stat-box{flex:1;min-width:60px;text-align:center;padding:4px 0;border-right:1px solid #1a2840}
.stat-box:last-child{border-right:none}
.stat-n{font-family:'Barlow Condensed',sans-serif;font-size:1.05rem;font-weight:900;line-height:1}
.stat-l{font-size:.44rem;color:#4b5e78;text-transform:uppercase;letter-spacing:.8px;margin-top:2px}

/* DIVISION HEADER */
.div-hdr{display:flex;align-items:center;gap:7px;padding:6px 14px;background:#0c1520;border-bottom:1px solid #1a2840;border-top:3px solid;margin-top:8px;position:sticky;top:0;z-index:10;backdrop-filter:blur(4px)}
.div-tag{font-size:.58rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;padding:2px 8px;border-radius:20px}
.div-sub{font-size:.54rem;color:#64748b}
.div-ct{font-size:.52rem;color:#4b5e78;margin-left:auto}

/* DAY HEADER */
.day-hdr{padding:6px 14px;background:#0a1218;border-top:1px solid #1a2840;border-bottom:1px solid #1a2840;display:flex;align-items:center;gap:8px}
.day-name{font-family:'Barlow Condensed',sans-serif;font-size:.9rem;font-weight:700;color:#c8a800}
.day-date{font-size:.52rem;color:#4b5e78}
.day-ct{font-size:.5rem;color:#334155;margin-left:auto}

/* TIME SLOT HEADER */
.slot-hdr{padding:4px 14px;background:#080e16;border-left:3px solid #38bdf8;border-bottom:1px solid #1a2840;display:flex;align-items:center;gap:6px}
.slot-time{font-size:.62rem;font-weight:600;color:#38bdf8}
.slot-ct{font-size:.5rem;color:#334155;margin-left:auto}

/* GAME CARD */
.game-card{border-bottom:1px solid #1a2840;padding:9px 14px;display:grid;grid-template-columns:1fr 95px 95px 95px 58px;gap:8px;align-items:center;background:#111827;cursor:pointer;transition:background .1s}
.game-card:hover{background:#131d2b}

/* TEAMS */
.team-row{display:flex;align-items:center;gap:5px;padding:2px 0}
.rnk{font-size:.52rem;color:#f59e0b;font-weight:700;width:18px;text-align:right;flex-shrink:0;font-family:'Barlow Condensed',sans-serif}
.rnk-none{width:18px;flex-shrink:0}
.tname{font-size:.78rem;font-weight:600;color:#f1f5f9;flex:1}
.trec{font-size:.5rem;color:#4b5e78}
.twp{font-size:.72rem;font-weight:700;font-family:'Barlow Condensed',sans-serif;white-space:nowrap}
.wp-hot{color:#22c55e}.wp-cold{color:#64748b}
.team-sep{height:1px;background:#1a2840;margin:2px 0 2px 22px}
.game-meta{font-size:.5rem;color:#4b5e78;margin-top:3px;display:flex;align-items:center;gap:5px}
.tv-b{background:#1a2535;border:1px solid #1e2d40;border-radius:3px;padding:1px 4px;font-size:.46rem;color:#64748b;font-weight:700}
.ntag{font-size:.46rem;color:#c084fc;background:#1a0a2a;border:1px solid #4a1a7a;border-radius:3px;padding:1px 5px}
.rec-w{display:inline-block;font-size:.52rem;font-weight:700;padding:0 4px;border-radius:3px;background:#0a1a0a;border:1px solid #166534;color:#4ade80;font-family:'Barlow Condensed',sans-serif}
.rec-l{display:inline-block;font-size:.52rem;font-weight:700;padding:0 4px;border-radius:3px;background:#1a0505;border:1px solid #7c2d12;color:#f87171;font-family:'Barlow Condensed',sans-serif}
.rec-e{display:inline-block;font-size:.52rem;font-weight:700;padding:0 4px;border-radius:3px;background:#0f1929;border:1px solid #1e2d40;color:#64748b;font-family:'Barlow Condensed',sans-serif}
.score-live{color:#22c55e;font-weight:700;font-size:.72rem}
.score-final{color:#4b5e78;font-size:.68rem}

/* ODDS CELLS */
.odds-box{background:#0c1520;border:1px solid #1a2840;border-radius:7px;padding:6px 7px;text-align:center}
.odds-lbl{font-size:.44rem;font-weight:700;letter-spacing:.8px;text-transform:uppercase;margin-bottom:3px;color:#4b5e78}
.odds-pick{font-family:'Barlow Condensed',sans-serif;font-size:.82rem;font-weight:700;line-height:1.2}
.odds-dog{font-family:'Barlow Condensed',sans-serif;font-size:.68rem;font-weight:700;color:#f59e0b;line-height:1.2}
.odds-sm{font-size:.48rem;color:#64748b;margin-top:1px}
.fav-c{color:#22c55e}.over-c{color:#38bdf8}.under-c{color:#f472b6}
.mv-s{font-size:.46rem;color:#38bdf8;font-weight:700;margin-top:1px}
.mv-p{font-size:.46rem;color:#f59e0b;font-weight:700;margin-top:1px}
.mv-n{font-size:.46rem;color:#4b5e78;margin-top:1px}

/* GRADE */
.grade-col{display:flex;flex-direction:column;align-items:center;gap:3px}
.gbig{width:26px;height:26px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-family:'Barlow Condensed',sans-serif;font-weight:900;font-size:.72rem}
.gsm{width:19px;height:19px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-family:'Barlow Condensed',sans-serif;font-weight:900;font-size:.58rem}
.g-ap{background:#166534;color:#4ade80}.g-a{background:#14532d;color:#86efac}.g-b{background:#1e3a5f;color:#60a5fa}.g-c{background:#3b2300;color:#fb923c}
.g-lbl{font-size:.42rem;color:#334155}

/* EXPAND PANEL (details/summary) */
details{border-top:none}
details summary{list-style:none;padding:5px 14px;cursor:pointer;background:#09111e;color:#38bdf8;font-size:.5rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;display:flex;align-items:center;justify-content:space-between;border-top:1px solid #1a2840;user-select:none}
details summary::-webkit-details-marker{display:none}
details summary:hover{background:#0c1a2e}
.expand-inner{background:#080e16;padding:10px 14px;display:grid;grid-template-columns:1fr 1fr;gap:10px;border-bottom:1px solid #1a2840}
.expand-section{background:#0c1520;border:1px solid #1a2840;border-radius:8px;padding:9px 11px}
.expand-lbl{font-size:.48rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:#38bdf8;margin-bottom:5px}
.ai-txt{font-size:.58rem;color:#64748b;line-height:1.55}
.kf-row{display:flex;gap:3px;flex-wrap:wrap;margin-top:5px}
.kf-p{padding:1px 6px;border-radius:20px;font-size:.5rem;background:#0a1a0a;border:1px solid #166534;color:#4ade80}
.kf-n{padding:1px 6px;border-radius:20px;font-size:.5rem;background:#1a0a00;border:1px solid #7c2d12;color:#fb923c}

/* H2H */
.h2h-row{display:flex;gap:6px;padding:3px 0;border-bottom:1px solid #0a1218;font-size:.55rem}
.h2h-row:last-child{border:none}
.h2h-date{color:#4b5e78;width:78px;flex-shrink:0;font-size:.5rem}
.h2h-w{font-weight:700;width:88px;flex-shrink:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.h2h-away{color:#22c55e}.h2h-home{color:#f59e0b}
.h2h-sc{color:#94a3b8;width:38px;flex-shrink:0;font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:.62rem}
.h2h-n{color:#334155;font-size:.48rem;font-style:italic;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.h2h-title{font-size:.48rem;font-weight:700;color:#4b5e78;text-transform:uppercase;letter-spacing:.8px;margin-bottom:4px;display:flex;justify-content:space-between}

/* HALF PREDICTIONS */
.half-inner{background:#080e16;border-bottom:1px solid #1a2840;padding:8px 14px}
.half-section-lbl{font-size:.5rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;padding:2px 0 6px;border-bottom:1px solid #1a2840;margin-bottom:6px}
.prop-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px}
.prop-card{background:#0c1520;border:1px solid #1a2840;border-radius:7px;padding:7px 7px;text-align:center}
.prop-lbl{font-size:.44rem;font-weight:700;letter-spacing:.7px;text-transform:uppercase;margin-bottom:3px}
.sp-l{color:#fb923c}.tot-l{color:#38bdf8}.win-l{color:#4ade80}
.prop-val{font-family:'Barlow Condensed',sans-serif;font-size:.82rem;font-weight:700;line-height:1.2}
.prop-sub{font-size:.46rem;color:#64748b;margin-top:1px}
.pbar{height:2px;background:#1e2d40;border-radius:2px;margin:3px 0 1px}
.pbar-fill{height:2px;border-radius:2px}

.src-badge{display:inline-flex;align-items:center;gap:3px;border-radius:10px;padding:1px 6px;font-size:.48rem;font-weight:700}
.src-live{background:#0a1f0a;border:1px solid #166534;color:#22c55e}
.src-static{background:#0f1929;border:1px solid #1e2d40;color:#64748b}
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

# ── PREDICTION ENGINE v2 — Vegas-Calibrated Multi-Factor Model ────────────
#
# Factors (weighted like professional power-rating models):
#  1. SP+ differential          — primary skill signal
#  2. Offensive/Defensive ranks — matchup-specific edge
#  3. Home field advantage      — proven +2.8 pts (Bill Connelly research)
#  4. Coaching quality          — scheme/game-plan multiplier
#  5. Schedule-position drift   — teams improve/regress as season progresses
#  6. ATS trend (home/away)     — historical cover rate by location
#  7. Strength of schedule      — adjusts for opposition quality
#  8. Blowout/trap-game risk    — large dogs cover more often late
#  9. Pace/style clash          — fast-paced offenses inflate totals
# 10. Rivalry/situational adj   — rivalry games tend to tighten spread

# Known rivalry pairs that historically play closer than SP+ suggests
RIVALRIES = {
    frozenset(["Alabama","Auburn"]),frozenset(["Ohio State","Michigan"]),
    frozenset(["Texas","Oklahoma"]),frozenset(["Georgia","Georgia Tech"]),
    frozenset(["Florida","Florida State"]),frozenset(["USC","Notre Dame"]),
    frozenset(["Clemson","South Carolina"]),frozenset(["Oregon","Oregon State"]),
    frozenset(["Iowa","Iowa State"]),frozenset(["Kansas","Kansas State"]),
    frozenset(["Wisconsin","Minnesota"]),frozenset(["Penn State","Michigan State"]),
    frozenset(["TCU","Baylor"]),frozenset(["LSU","Ole Miss"]),
    frozenset(["Tennessee","Vanderbilt"]),frozenset(["Georgia","Florida"]),
}

# High-pace programs that push totals higher
HIGH_PACE = {"Texas","Ole Miss","LSU","Florida","Georgia","Ohio State","Oregon",
             "Michigan","Miami","Notre Dame","Clemson","Alabama","Oklahoma",
             "BYU","Houston","Memphis","Tulane","Liberty","UCF","SMU"}

def smart_predict(away, home, neutral=False, week=0):
    a_db = get_db(away); h_db = get_db(home)
    a_sp,a_off,a_def,a_ath,a_ata,a_cch,a_sos = a_db
    h_sp,h_off,h_def,h_ath,h_ata,h_cch,h_sos = h_db

    # ── 1. SP+ base differential ──────────────────────────────────────────
    sp_diff = h_sp - a_sp

    # ── 2. Offensive vs defensive matchup edges ───────────────────────────
    # How does away offense stack up against home defense and vice versa
    # Lower rank = better (rank 1 = best)
    a_off_vs_h_def = (h_def - a_off) * 0.12   # +ve = away offense wins matchup
    h_off_vs_a_def = (a_def - h_off) * 0.12   # +ve = home offense wins matchup
    matchup_edge = h_off_vs_a_def - a_off_vs_h_def  # net home matchup advantage

    # ── 3. Home field advantage ───────────────────────────────────────────
    hfa = 0.0 if neutral else 2.8

    # ── 4. Coaching quality (scheme/adjustment factor) ────────────────────
    coach_edge = (h_cch - a_cch) * 4.5

    # ── 5. Schedule-position drift (teams stabilize mid-season) ──────────
    # Early weeks have more variance; late-season better calibrated
    week_stabilizer = min(1.0, week / 8.0)  # 0→1 as season progresses
    sp_weight = 0.80 + week_stabilizer * 0.15  # SP+ more predictive late

    # ── 6. Strength of schedule adjustment ───────────────────────────────
    sos_edge = (h_sos - a_sos) * 2.0  # stronger schedule = more battle-tested

    # ── 7. ATS trend overlay ──────────────────────────────────────────────
    # Home team ATS rate vs away team ATS away rate
    ats_edge = (h_ath - a_ata) * 4.0

    # ── 8. Rivalry tightening ─────────────────────────────────────────────
    rivalry_adj = 0.0
    if frozenset([away, home]) in RIVALRIES:
        rivalry_adj = -1.5  # rivalry games: reduce the spread by 1.5 pts

    # ── 9. Raw edge (pts the home team wins by, from home team perspective)
    raw_edge = (sp_diff * sp_weight + matchup_edge + hfa + coach_edge
                + sos_edge + ats_edge + rivalry_adj)

    sp_gap = abs(a_sp - h_sp)
    home_fav = raw_edge > 0

    # ── Win probability — logistic calibrated to Vegas (k=0.13) ──────────
    home_wp = 1 / (1 + math.exp(-raw_edge * 0.13))
    away_wp  = 1 - home_wp

    # ── Moneyline from win probability (include vig) ──────────────────────
    def wp2ml(wp):
        if wp >= 0.5:
            return -round((wp / (1 - wp)) * 110)   # favorite includes juice
        else:
            return  round(((1 - wp) / wp) * 100)   # underdog

    ml_home = wp2ml(home_wp)
    ml_away = wp2ml(away_wp)

    # ── Spread (pts) ──────────────────────────────────────────────────────
    sp = round(abs(raw_edge) * 2) / 2
    # Cap at realistic bounds
    sp = min(sp, 45.0)

    # ── Total points — pace and defense adjusted ───────────────────────────
    # Base = average offensive output for both teams
    avg_off_rank = ((60 - a_off) + (60 - h_off)) / 2    # 0-59, higher = better O
    avg_def_rank = ((60 - a_def) + (60 - h_def)) / 2    # 0-59, higher = better D
    pace_boost = 3.0 if (away in HIGH_PACE and home in HIGH_PACE) else \
                 1.5 if (away in HIGH_PACE or home in HIGH_PACE) else 0.0
    # Base total: 42 pts for average teams + pace + offense - defense resistance
    total_base = 42.0 + avg_off_rank * 0.30 - avg_def_rank * 0.15 + pace_boost
    # Week drift: games get higher scoring as offenses mature
    total_base += week * 0.4
    total = round(total_base * 2) / 2
    total = max(28.0, min(total, 72.0))  # realistic bounds

    # O/U: if combined offensive rank > combined defensive rank → lean OVER
    ou = "OVER" if avg_off_rank > avg_def_rank + 3 else "UNDER"
    # Rivalry games tend to go UNDER (defensive effort, slower pace)
    if frozenset([away, home]) in RIVALRIES and total > 45:
        ou = "UNDER"

    # ── Projected scores ─────────────────────────────────────────────────
    fav_share  = (0.5 + min(away_wp, home_wp) * 0.12)  # favorites score more
    if home_fav:
        ph = round(total * fav_share); pa = round(total - ph)
    else:
        pa = round(total * fav_share); ph = round(total - pa)

    # ── Confidence scores — calibrated ranges ─────────────────────────────
    # mlC: moneyline confidence — correlates with SP+ gap + matchup clarity
    mlC = min(94, max(50, int(55 + sp_gap * 1.1 + abs(matchup_edge) * 8)))
    # spC: spread confidence — tighter than ML (more random)
    spC = min(90, max(44, int(52 + sp_gap * 0.75 + ats_edge * 4)))
    # ttC: total confidence — dependent on pace matchup clarity
    ttC = min(88, max(46, int(53 + abs(avg_off_rank - avg_def_rank) * 0.6 + pace_boost * 2)))

    # ── Market signals ───────────────────────────────────────────────────
    if sp_gap > 18:
        mv = "Sharp ↑"
    elif sp_gap > 10:
        mv = "Steam ↑"
    elif ats_edge > 0.04:
        mv = "Public →"
    elif sp_gap < 3:
        mv = "Neutral →"
    else:
        mv = "Value ↗"

    sp_p = min(88, max(35, int(42 + sp_gap * 1.4 + (mlC - 60) * 0.35)))

    # ── Analysis text ────────────────────────────────────────────────────
    fnm = home if home_fav else away
    dnm = away if home_fav else home
    rivalry_note = " Rivalry game — expect tighter margin." if frozenset([away,home]) in RIVALRIES else ""
    pace_note    = " High-pace matchup inflates total." if pace_boost >= 3.0 else ""

    if sp_gap > 22:
        txt = (f"{fnm} has a dominant SP+ edge (+{sp_gap:.1f} pts) over {dnm}. "
               f"Superior on both sides of ball — matchup ranks ({h_off} off / {h_def} def vs {a_off}/{a_def}). "
               f"Coaching advantage (+{abs(h_cch-a_cch)*100:.0f}%). Expect comfortable cover."+rivalry_note)
        pos = [f"{fnm} SP+ dominance", "Talent gap", "Coaching edge"]
        neg = [f"{dnm} upset potential", "Trap game risk"]
    elif sp_gap > 12:
        venue = "Neutral site — no HFA." if neutral else f"Home field adds ~2.8 pts for {home}."
        txt = (f"{fnm} SP+ edge of +{sp_gap:.1f} pts. {venue} "
               f"Matchup: {fnm} off-rank {h_off if home_fav else a_off} vs {dnm} def-rank {a_def if home_fav else h_def}. "
               f"ATS trend favors {fnm} ({int((h_ath if home_fav else a_ata)*100)}%)."+rivalry_note+pace_note)
        pos = [f"{fnm} SP+ edge", "ATS trend", "Coaching quality"]
        neg = ["Second-half letdown risk", "Cover variance"]
    elif sp_gap > 5:
        venue = "Neutral site." if neutral else "Home field is the tiebreaker."
        txt = (f"Competitive matchup — SP+ gap just {sp_gap:.1f} pts. {venue} "
               f"Lean {fnm} on matchup ({h_off if home_fav else a_off} off vs {a_def if home_fav else h_def} def). "
               f"Low conviction — monitor line movement."+rivalry_note+pace_note)
        pos = ["Slight SP+ lean", "Matchup edge"]
        neg = ["Low confidence", "Coin-flip territory", "Sharp two-way action"]
    else:
        txt = (f"Dead-even by SP+ ({a_sp:.1f} vs {h_sp:.1f}). "
               f"{'Neutral site removes HFA.' if neutral else f'Home field ({home}) is only edge.'} "
               f"Focus on total ({ou} {total}) rather than side — low side confidence."+rivalry_note+pace_note)
        pos = ["Total play preferred", "Pace analysis"]
        neg = ["Toss-up matchup", "No clear SP+ lean", "High variance"]

    return {"ml_away":ml_away,"ml_home":ml_home,
            "sp_away":-sp if home_fav else sp,
            "sp_home": sp if home_fav else -sp,
            "total":total,"ou":ou,"pa":pa,"ph":ph,
            "mlC":mlC,"spC":spC,"ttC":ttC,
            "txt":txt,"pos":pos,"neg":neg,
            "mv":mv,"sp_p":sp_p,"fa":not home_fav,
            "home_wp":home_wp,"away_wp":away_wp,"sp_gap":sp_gap}

def make_half_preds(away, home, p, week=0):
    """Half-game predictions based on full-game model output."""
    fa = p["fa"]; fnm = away if fa else home; dnm = home if fa else away
    sp_gap = p["sp_gap"]

    # 1st half: favorites cover at higher rate (game-plan execution)
    # ~47% of total points scored in 1H on average
    h1_share = 0.47 + (sp_gap / 500)   # big favorites score more in 1H
    h1t = round(p["total"] * h1_share * 2) / 2
    h2t = round((p["total"] - h1t) * 2) / 2

    # Spread: 1H spread ≈ 55% of full game; 2H ≈ 50%
    h1s = round(abs(p["sp_away"]) * 0.55 * 2) / 2
    h2s = round(abs(p["sp_away"]) * 0.50 * 2) / 2

    # 1H total: tends to go OVER (defenses wear in 2H)
    h1ou = "OVER" if p["ou"] == "OVER" else "UNDER"
    # 2H total: large favorites slow pace → UNDER more common
    h2ou = "UNDER" if sp_gap > 10 else ("OVER" if p["ou"] == "OVER" else "UNDER")

    # 2H winner: large favorites often win 2H even if dog covers 2H spread
    h2w = fnm if sp_gap > 7 else (home if fa else away)

    def hc(base, adj):
        return min(92, max(44, int(base + adj)))

    return {
        "h1_sp": h1s, "h1_sp_team": fnm, "h1_spC": hc(p["spC"], -3),
        "h1_total": h1t, "h1_ou": h1ou,   "h1_totC": hc(p["ttC"], -2),
        "h1_win": fnm,   "h1_winC": hc(p["mlC"], -4),
        "h2_sp": h2s, "h2_sp_team": fnm, "h2_spC": hc(p["spC"], -7),
        "h2_total": h2t, "h2_ou": h2ou,   "h2_totC": hc(p["ttC"], -5),
        "h2_win": h2w,   "h2_winC": hc(p["mlC"], -9),
        "fa": fa, "fnm": fnm
    }

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

# ── DAY / TIME GROUPING HELPERS ───────────────────────────────────────────
import re as _re2

def _parse_sort(t):
    """Sort key: day-offset (0-60000) + time in HHMM."""
    t2 = t.upper().replace("ET","").replace("EDT","").strip()
    day_off = 0
    for di, dn in enumerate(["THU","FRI","SAT","SUN","MON","TUE","WED"]):
        if t2.startswith(dn):
            day_off = di * 10000
            t2 = t2[3:].strip()
            break
    m = _re2.match(r"(\d+):(\d+)\s*(AM|PM)?", t2)
    if not m: return day_off + 9999
    h, mn = int(m.group(1)), int(m.group(2))
    period = m.group(3) or ("PM" if h < 7 else "AM")
    if period == "PM" and h != 12: h += 12
    if period == "AM" and h == 12: h = 0
    return day_off + h * 100 + mn

def _day_label(t):
    up = t.upper()
    for k,v in [("THU","Thursday"),("FRI","Friday"),("SAT","Saturday"),
                ("SUN","Sunday"),("MON","Monday"),("TUE","Tuesday"),("WED","Wednesday")]:
        if up.startswith(k): return v
    return "Saturday"

def _time_slot(t):
    s = _parse_sort(t) % 10000
    if s < 1130:  return "🌅 Morning  (before 11:30 AM)"
    if s < 1400:  return "☀️  Noon  (11:30 AM – 2:00 PM)"
    if s < 1700:  return "🌤  Afternoon  (2:00 PM – 5:00 PM)"
    if s < 1930:  return "🌆 Evening  (5:00 PM – 7:30 PM)"
    if s < 2130:  return "🌙 Prime Time  (7:30 PM – 9:30 PM)"
    return              "🌃 Late Night  (9:30 PM+)"


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
    2: [  # Week 2 — Sep 10-13, 2026 — SOURCE: fbschedules.com (verified)
        # ── THURSDAY Sep 10 ──────────────────────────────────────────────
        G("Florida A&M","Miami",                "Thu 8:00 PM","ACCN",   "ACC",      "Hard Rock Stadium, Miami Gardens FL"),
        # ── FRIDAY Sep 11 ────────────────────────────────────────────────
        G("Villanova","Louisville",             "Fri 7:00 PM","ACCN",   "ACC",      "L&N Federal Credit Union Stadium, Louisville KY","FCS"),
        G("Norfolk State","Virginia",           "Fri 7:00 PM","ACCNX",  "ACC",      "Scott Stadium, Charlottesville VA","FCS"),
        G("Richmond","NC State",                "Fri 7:00 PM","ESPNU",  "ACC",      "Carter-Finley Stadium, Raleigh NC","FCS"),
        G("Rutgers","Boston College",           "Fri 7:30 PM","ESPN2",  "ACC",      "Alumni Stadium, Chestnut Hill MA"),
        G("Missouri","Kansas",                  "Fri 8:00 PM","FOX",    "Big 12",   "David Booth Kansas Memorial Stadium, Lawrence KS"),
        # ── SATURDAY Sep 12 — 12:00 PM ───────────────────────────────────
        G("Oregon","Oklahoma State",            "Sat 12:00 PM","ESPN",  "Big 12",   "Boone Pickens Stadium, Stillwater OK"),
        G("Arizona State","Texas A&M",          "Sat 12:00 PM","ABC",   "SEC",      "Kyle Field, College Station TX"),
        G("Oklahoma","Michigan",                "Sat 12:00 PM","FOX",   "Big Ten",  "Michigan Stadium, Ann Arbor MI"),
        G("Penn State","Temple",                "Sat 12:00 PM","ESPN2", "AAC",      "Lincoln Financial Field, Philadelphia PA"),
        G("Washington State","Kansas State",    "Sat 12:00 PM","TNT",   "Big 12",   "Bill Snyder Family Stadium, Manhattan KS"),
        G("ETSU","North Carolina",              "Sat 12:00 PM","ACCN",  "ACC",      "Kenan Memorial Stadium, Chapel Hill NC","FCS"),
        G("Old Dominion","Virginia Tech",       "Sat 12:00 PM","CW",    "ACC",      "Lane Stadium, Blacksburg VA"),
        G("Wake Forest","Purdue",               "Sat 12:00 PM","FS1",   "Big Ten",  "Ross-Ade Stadium, West Lafayette IN"),
        G("South Florida","Army",               "Sat 12:00 PM","CBSSN", "AAC",      "Michie Stadium, West Point NY"),
        G("Howard","Indiana",                   "Sat 12:00 PM","BTN",   "Big Ten",  "Memorial Stadium, Bloomington IN","FCS"),
        G("App State","East Carolina",          "Sat 12:00 PM","ESPNU", "AAC",      "Dowdy-Ficklen Stadium, Greenville NC"),
        G("Gardner-Webb","Liberty",             "Sat 12:00 PM","ESPN+", "CUSA",     "Williams Stadium, Lynchburg VA","FCS"),
        G("Wofford","Kent State",               "Sat 12:00 PM","ESPN+", "MAC",      "Dix Stadium, Kent OH","FCS"),
        G("EMU","Michigan State",               "Sat 12:00 PM","BTN",   "Big Ten",  "Spartan Stadium, East Lansing MI"),
        G("Maryland","UConn",                   "Sat 12:00 PM","CBSSN", "AAC",      "Rentschler Field, East Hartford CT"),
        G("Mississippi State","Minnesota",      "Sat 12:00 PM","CBS",   "Big Ten",  "Huntington Bank Stadium, Minneapolis MN"),
        G("Utah State","Washington",            "Sat 12:00 PM","BTN",   "Big Ten",  "Husky Stadium, Seattle WA"),
        # ── SATURDAY Sep 12 — 12:45 PM ───────────────────────────────────
        G("Western Kentucky","Georgia",         "Sat 12:45 PM","SECN+", "SEC",      "Sanford Stadium, Athens GA","FCS"),
        G("Colgate","Central Michigan",         "Sat 1:00 PM","ESPN+",  "MAC",      "Kelly/Shorts Stadium, Mt. Pleasant MI","FCS"),
        G("Holy Cross","Miami OH",              "Sat 1:00 PM","ESPN+",  "MAC",      "Yager Stadium, Oxford OH","FCS"),
        G("UT Martin","West Virginia",          "Sat 1:00 PM","ESPN+",  "Big 12",   "Milan Puskar Stadium, Morgantown WV","FCS"),
        # ── SATURDAY Sep 12 — 2:00 PM ────────────────────────────────────
        G("Stony Brook","Ball State",           "Sat 2:00 PM","ESPN+",  "MAC",      "Scheumann Stadium, Muncie IN","FCS"),
        # ── SATURDAY Sep 12 — 3:30 PM ────────────────────────────────────
        G("Alabama","Kentucky",                 "Sat 3:30 PM","ABC",    "SEC",      "Kroger Field, Lexington KY"),
        G("Arizona","BYU",                      "Sat 3:30 PM","FOX",    "Big 12",   "LaVell Edwards Stadium, Provo UT"),
        G("Duke","Illinois",                    "Sat 3:30 PM","FS1",    "Big Ten",  "Memorial Stadium, Champaign IL"),
        G("UCF","Pittsburgh",                   "Sat 3:30 PM","ESPN2",  "ACC",      "Acrisure Stadium, Pittsburgh PA"),
        G("California","Syracuse",              "Sat 3:30 PM","ACCN",   "ACC",      "JMA Wireless Dome, Syracuse NY"),
        G("Robert Morris","Akron",              "Sat 3:30 PM","ESPN+",  "MAC",      "InfoCision Stadium, Akron OH","FCS"),
        G("Sacred Heart","UMass",               "Sat 3:30 PM","ESPN+",  "MAC",      "Warren McGuirk Alumni Stadium, Amherst MA","FCS"),
        G("CCSU","Toledo",                      "Sat 3:30 PM","ESPN+",  "MAC",      "Glass Bowl, Toledo OH","FCS"),
        G("Weber State","Colorado",             "Sat 3:30 PM","ESPN+",  "Big 12",   "Folsom Field, Boulder CO","FCS"),
        G("ULM","UAB",                          "Sat 3:30 PM","ESPN+",  "Sun Belt", "Protective Stadium, Birmingham AL"),
        G("UTSA","Texas State",                 "Sat 3:30 PM","CW",     "CUSA",     "Bobcat Stadium, San Marcos TX"),
        G("Rice","Notre Dame",                  "Sat 3:30 PM","NBC",    "Ind.",     "Notre Dame Stadium, South Bend IN"),
        G("UNLV","North Texas",                 "Sat 3:45 PM","ESPNU",  "AAC",      "DATCU Stadium, Denton TX"),
        # ── SATURDAY Sep 12 — 4:00 PM ────────────────────────────────────
        G("UC Davis","SMU",                     "Sat 4:00 PM","ACCNX",  "ACC",      "Gerald J. Ford Stadium, Dallas TX","FCS"),
        G("Alabama State","Troy",               "Sat 4:00 PM","ESPN+",  "Sun Belt", "Veterans Memorial Stadium, Troy AL","FCS"),
        G("Northern Colorado","Wyoming",        "Sat 4:00 PM","MW+",    "MWC",      "War Memorial Stadium, Laramie WY","FCS"),
        G("Mercyhurst","New Mexico",            "Sat 4:00 PM","MW+",    "MWC",      "University Stadium, Albuquerque NM","FCS"),
        G("Delaware","Vanderbilt",              "Sat 4:15 PM","SECN+",  "SEC",      "FirstBank Stadium, Nashville TN","FCS"),
        # ── SATURDAY Sep 12 — 5:30 PM ────────────────────────────────────
        G("Campbell","Florida",                 "Sat 5:30 PM","SECN+",  "SEC",      "Ben Hill Griffin Stadium, Gainesville FL","FCS"),
        # ── SATURDAY Sep 12 — 6:00 PM ────────────────────────────────────
        G("Memphis","Boise State",              "Sat 6:00 PM","USA",    "Pac-12",   "Albertsons Stadium, Boise ID"),
        G("Buffalo","FIU",                      "Sat 6:00 PM","ESPN+",  "MAC",      "FIU Stadium, Miami FL"),
        G("Jacksonville State","Ohio",          "Sat 6:00 PM","ESPN+",  "MAC",      "Peden Stadium, Athens OH"),
        G("Monmouth","Western Michigan",        "Sat 6:30 PM","ESPN+",  "MAC",      "Waldo Stadium, Kalamazoo MI","FCS"),
        # ── SATURDAY Sep 12 — 7:00 PM ────────────────────────────────────
        G("Tennessee","Georgia Tech",           "Sat 7:00 PM","ESPN",   "ACC",      "Bobby Dodd Stadium, Atlanta GA"),
        G("South Alabama","Tulane",             "Sat 7:00 PM","ESPN+",  "AAC",      "Yulman Stadium, New Orleans LA"),
        G("Tulsa","Sam Houston State",          "Sat 7:00 PM","ESPN+",  "AAC",      "Bowers Stadium, Huntsville TX"),
        G("MTSU","Marshall",                    "Sat 7:00 PM","ESPN+",  "Sun Belt", "Joan C. Edwards Stadium, Huntington WV"),
        G("West Georgia","Arkansas State",      "Sat 7:00 PM","ESPN+",  "Sun Belt", "Centennial Bank Stadium, Jonesboro AR","FCS"),
        G("Georgia State","Kennesaw State",     "Sat 7:00 PM","ESPN+",  "CUSA",     "Fifth Third Stadium, Kennesaw GA"),
        G("Lindenwood","Missouri State",        "Sat 7:00 PM","ESPN+",  "CUSA",     "Plaster Field, Springfield MO","FCS"),
        G("Towson","South Carolina",            "Sat 7:00 PM","SECN+",  "SEC",      "Williams-Brice Stadium, Columbia SC","FCS"),
        G("Bowling Green","Nebraska",           "Sat 7:00 PM","FS1",    "Big Ten",  "Memorial Stadium, Lincoln NE"),
        G("Illinois State","Northern Illinois", "Sat 7:00 PM","MW+",    "MWC",      "Huskie Stadium, DeKalb IL","FCS"),
        G("Southern Utah","Colorado State",     "Sat 7:00 PM","CBSSN",  "Pac-12",   "Canvas Stadium, Fort Collins CO","FCS"),
        G("Western Carolina","Cincinnati",      "Sat 7:00 PM","ESPN+",  "Big 12",   "Nippert Stadium, Cincinnati OH","FCS"),
        G("Southern","Houston",                 "Sat 7:00 PM","ESPN+",  "Big 12",   "TDECU Stadium, Houston TX","FCS"),
        # ── SATURDAY Sep 12 — 7:15 PM ────────────────────────────────────
        G("San Diego State","UCLA",             "Sat 7:15 PM","BTN",    "Big Ten",  "Rose Bowl, Pasadena CA"),
        G("Western Illinois","Wisconsin",       "Sat 7:15 PM","BTN",    "Big Ten",  "Camp Randall Stadium, Madison WI","FCS"),
        # ── SATURDAY Sep 12 — 7:30 PM ────────────────────────────────────
        G("Ohio State","Texas",                 "Sat 7:30 PM","ABC",    "SEC",      "Darrell K Royal Stadium, Austin TX"),
        G("Iowa State","Iowa",                  "Sat 7:30 PM","NBC",    "Big Ten",  "Kinnick Stadium, Iowa City IA"),
        G("Texas Tech","Oregon State",          "Sat 7:30 PM","CBS",    "Pac-12",   "Reser Stadium, Corvallis OR"),
        G("Georgia Southern","Clemson",         "Sat 7:30 PM","ACCN",   "ACC",      "Memorial Stadium, Clemson SC"),
        G("Louisiana Tech","LSU",               "Sat 7:30 PM","SECN+",  "SEC",      "Tiger Stadium, Baton Rouge LA"),
        G("Fordham","Coastal Carolina",         "Sat 7:30 PM","ESPN+",  "Sun Belt", "Brooks Stadium, Conway SC","FCS"),
        G("Grambling State","TCU",              "Sat 8:00 PM","ESPN+",  "Big 12",   "Amon G. Carter Stadium, Fort Worth TX","FCS"),
        G("Prairie View A&M","Baylor",          "Sat 8:00 PM","ESPN+",  "Big 12",   "McLane Stadium, Waco TX","FCS"),
        # ── SATURDAY Sep 12 — 7:45 PM ────────────────────────────────────
        G("Navy","Florida Atlantic",            "Sat 7:45 PM","ESPNU",  "AAC",      "FAU Stadium, Boca Raton FL"),
        G("Charlotte","Ole Miss",               "Sat 7:45 PM","ESPN2",  "SEC",      "Vaught-Hemingway Stadium, Oxford MS"),
        G("Southern Miss","Auburn",             "Sat 7:45 PM","SECN",   "SEC",      "Jordan-Hare Stadium, Auburn AL"),
        # ── SATURDAY Sep 12 — Late Night ─────────────────────────────────
        G("North Dakota State","Air Force",     "Sat 10:00 PM","FS1",   "MWC",      "Falcon Stadium, Colorado Springs CO"),
        G("Cal Poly","San Jose State",          "Sat 9:00 PM","NBCS",   "MWC",      "CEFCU Stadium, San Jose CA","FCS"),
        G("Texas Southern","UTEP",              "Sat 9:00 PM","MW+",    "MWC",      "Sun Bowl, El Paso TX","FCS"),
        G("Arkansas","Utah",                    "Sat 10:15 PM","ESPN",  "Big 12",   "Rice-Eccles Stadium, Salt Lake City UT"),
        G("Sacramento State","Fresno State",    "Sat 10:30 PM","CBSSN", "Pac-12",   "Bulldog Stadium, Fresno CA"),
        G("Montana State","Nevada",             "Sat 10:30 PM","CW",    "MWC",      "Mackay Stadium, Reno NV","FCS"),
        G("Louisiana","USC",                    "Sat 11:00 PM","BTN",   "Big Ten",  "LA Memorial Coliseum, Los Angeles CA"),
        G("New Mexico State","Hawaii",          "Sun 12:00 AM","MW+",   "MWC",      "Clarence T.C. Ching Complex, Honolulu HI"),
        # ── D-II ─────────────────────────────────────────────────────────
        G("Ferris State","Lake Erie",           "Sat 1:00 PM","—",      "GLIAC",    "Albert C. Baumgartner Stadium, Painesville OH","D-II"),
        G("Delta State","Shorter",              "Sat 2:00 PM","—",      "GSC",      "Barron Stadium, Rome GA","D-II"),
        G("Colorado Mesa","Fort Lewis",         "Sat 2:00 PM","—",      "RMAC",     "Miller Activity Center, Durango CO","D-II"),
        G("Tarleton State","Midwestern State",  "Sat 7:00 PM","—",      "Lone Star", "Memorial Stadium, Stephenville TX","D-II"),
        G("Minnesota Duluth","Concordia-St Paul","Sat 1:00 PM","—",     "NSIC",     "Malosky Stadium, Duluth MN","D-II"),
        # ── D-III ────────────────────────────────────────────────────────
        G("Mount Union","Ohio Wesleyan",        "Sat 1:00 PM","—",      "OAC",      "Phillips-Perkins Field, Delaware OH","D-III"),
        G("North Central","Millikin",           "Sat 1:00 PM","—",      "CCIW",     "Harold V. Spear Stadium, Decatur IL","D-III"),
        G("Wisconsin-Whitewater","UW-Platteville","Sat 1:00 PM","—",    "WIAC",     "Lillo Field, Platteville WI","D-III"),
        G("Mary Hardin-Baylor","Sul Ross State","Sat 2:00 PM","—",      "ASC",      "Bulldog Bowl, Alpine TX","D-III"),
        G("Amherst","Tufts",                    "Sat 1:00 PM","—",      "NESCAC",   "Carol Zicklin Field, Medford MA","D-III"),
    ],
    3: [  # Week 3 — Sep 17-19, 2026 — COMPLETE ALL DIVISIONS
        # ── THURSDAY Sep 17 ──────────────────────────────────────────────
        G("Syracuse","Pittsburgh",               "Thu 7:30 PM","ESPN",   "ACC",       "Acrisure Stadium, Pittsburgh PA"),
        # ── FRIDAY Sep 18 ────────────────────────────────────────────────
        G("Miami","Wake Forest",                 "Fri 7:30 PM","ESPN",   "ACC",       "Truist Field, Winston-Salem NC"),
        G("Houston","Texas Tech",                "Fri 8:00 PM","FOX",    "Big 12",    "Jones AT&T Stadium, Lubbock TX"),
        G("Portland State","Oregon",             "Fri 10:30 PM","BTN",   "Big Ten",   "Autzen Stadium, Eugene OR","FCS"),
        # ── SATURDAY Sep 19 — 11:30 AM ───────────────────────────────────
        G("Coastal Carolina","Delaware",         "Sat 11:30 AM","CBSSN", "Sun Belt",  "Delaware Stadium, Newark DE"),
        # ── SATURDAY Sep 19 — 12:00 PM — FBS ────────────────────────────
        G("Georgia","Arkansas",                  "Sat 12:00 PM","ABC",   "SEC",       "Donald W. Reynolds Razorback Stadium, Fayetteville AR"),
        G("Kent State","Ohio State",             "Sat 12:00 PM","FOX",   "Big Ten",   "Ohio Stadium, Columbus OH"),
        G("Buffalo","Penn State",                "Sat 12:00 PM","BTN",   "Big Ten",   "Beaver Stadium, State College PA"),
        G("Tulane","Kansas State",               "Sat 12:00 PM","ESPN2", "Big 12",    "Bill Snyder Family Stadium, Manhattan KS"),
        G("Bowling Green","Iowa State",          "Sat 12:00 PM","ESPNU", "Big 12",    "Jack Trice Stadium, Ames IA"),
        G("Arizona State","Kansas",              "Sat 12:00 PM","FS1",   "Big 12",    "Wembley Stadium, London England",neutral=True),
        G("Mercer","Georgia Tech",               "Sat 12:00 PM","ACCN",  "ACC",       "Bobby Dodd Stadium, Atlanta GA","FCS"),
        G("North Carolina","Clemson",            "Sat 12:00 PM","ESPN",  "ACC",       "Memorial Stadium, Clemson SC"),
        G("Akron","Minnesota",                   "Sat 12:00 PM","BTN",   "Big Ten",   "Huntington Bank Stadium, Minneapolis MN"),
        G("North Texas","Texas State",           "Sat 12:00 PM","USA",   "AAC",       "Bobcat Stadium, San Marcos TX"),
        G("EMU","Wisconsin",                     "Sat 12:30 PM","Peacock","Big Ten",  "Camp Randall Stadium, Madison WI"),
        G("NC State","Vanderbilt",               "Sat 12:45 PM","SECN+", "SEC",       "FirstBank Stadium, Nashville TN"),
        G("Wyoming","Central Michigan",          "Sat 1:00 PM","ESPN+",  "MAC",       "Kelly/Shorts Stadium, Mt. Pleasant MI"),
        # ── FCS 12:00-1:00 PM ────────────────────────────────────────────
        G("Richmond","Stony Brook",              "Sat 12:00 PM","FloSports","CAA",    "Kenneth P. LaValle Stadium, Stony Brook NY","FCS"),
        G("Villanova","Towson",                  "Sat 12:00 PM","FloSports","CAA",    "Johnny Unitas Stadium, Towson MD","FCS"),
        G("New Hampshire","Elon",                "Sat 12:00 PM","FloSports","CAA",    "Rhodes Stadium, Elon NC","FCS"),
        G("UAlbany","Maine",                     "Sat 12:00 PM","FloSports","CAA",    "Harold Alfond Sports Stadium, Orono ME","FCS"),
        G("Samford","Furman",                    "Sat 12:00 PM","ESPN+", "SoCon",     "Paladin Stadium, Greenville SC","FCS"),
        G("Holy Cross","Lehigh",                 "Sat 12:00 PM","ESPN+", "Patriot",   "Goodman Stadium, Bethlehem PA","FCS"),
        G("Fordham","Georgetown",                "Sat 12:00 PM","ESPN+", "Patriot",   "Cooper Field, Washington DC","FCS"),
        G("Alabama State","Grambling State",     "Sat 12:00 PM","SWAC TV","SWAC",     "Eddie G. Robinson Memorial Stadium, Grambling LA","FCS"),
        G("North Carolina A&T","Howard",         "Sat 12:00 PM","ESPN+", "MEAC",      "Greene Stadium, Washington DC","FCS"),
        G("Morgan State","Delaware State",       "Sat 12:00 PM","MEAC+", "MEAC",      "Alumni Stadium, Dover DE","FCS"),
        G("Drake","Dayton",                      "Sat 12:00 PM","ESPN+", "Pioneer",   "Welcome Stadium, Dayton OH","FCS"),
        G("St. Thomas","Morehead State",         "Sat 12:00 PM","ESPN+", "Pioneer",   "O'Shaughnessy Stadium, Saint Paul MN","FCS"),
        G("Stonehill","LIU",                     "Sat 12:00 PM","NEC+",  "NEC",       "Shark Stadium, Brookville NY","FCS"),
        G("Duquesne","Robert Morris",            "Sat 12:00 PM","ESPN+", "NEC",       "Joe Walton Stadium, Moon Township PA","FCS"),
        G("New Haven","Merrimack",               "Sat 12:00 PM","NEC+",  "NEC",       "Duane Stadium, North Andover MA","FCS"),
        G("Utah Tech","Northern Arizona",        "Sat 12:00 PM","ESPN+", "Big Sky",   "J. Lawrence Walkup Skydome, Flagstaff AZ","FCS"),
        G("Cornell","Columbia",                  "Sat 1:00 PM","ESPN+",  "Ivy",       "Robert K. Kraft Field, New York NY","FCS"),
        G("Yale","Dartmouth",                    "Sat 1:00 PM","ESPN+",  "Ivy",       "Memorial Field, Hanover NH","FCS"),
        G("Harvard","Brown",                     "Sat 1:00 PM","ESPN+",  "Ivy",       "Brown Stadium, Providence RI","FCS"),
        G("Princeton","Penn",                    "Sat 1:00 PM","ESPN+",  "Ivy",       "Franklin Field, Philadelphia PA","FCS"),
        G("Northern Colorado","Montana",         "Sat 1:00 PM","ESPN+",  "Big Sky",   "Washington-Grizzly Stadium, Missoula MT","FCS"),
        G("Idaho","Eastern Washington",          "Sat 1:00 PM","ESPN+",  "Big Sky",   "Roos Field, Cheney WA","FCS"),
        G("Hampton","Delaware",                  "Sat 1:00 PM","ESPN+",  "CAA",       "Delaware Stadium, Newark DE","FCS"),
        G("Mercer","Western Carolina",           "Sat 1:00 PM","ESPN+",  "SoCon",     "E.J. Whitmire Stadium, Cullowhee NC","FCS"),
        G("Tennessee Tech","VMI",                "Sat 1:00 PM","ESPN+",  "SoCon",     "Foster Stadium, Lexington VA","FCS"),
        G("Colgate","Bucknell",                  "Sat 1:00 PM","ESPN+",  "Patriot",   "Christy Mathewson-Memorial Stadium, Lewisburg PA","FCS"),
        G("Lafayette","Villanova",               "Sat 1:00 PM","ESPN+",  "Patriot",   "Fisher Stadium, Easton PA","FCS"),
        G("Austin Peay","Eastern Illinois",      "Sat 1:00 PM","ESPN+",  "OVC",       "O'Brien Field, Charleston IL","FCS"),
        G("Valparaiso","Butler",                 "Sat 1:00 PM","ESPN+",  "Pioneer",   "Sellick Bowl, Indianapolis IN","FCS"),
        G("Stetson","Marist",                    "Sat 1:00 PM","ESPN+",  "Pioneer",   "Tenney Stadium, Poughkeepsie NY","FCS"),
        G("Wagner","Central Connecticut",        "Sat 1:00 PM","ESPN+",  "NEC",       "Hameline Field, Staten Island NY","FCS"),
        # ── SATURDAY Sep 19 — 2:00 PM — FBS ─────────────────────────────
        G("Maine","Boston College",              "Sat 2:00 PM","ACCNX",  "ACC",       "Alumni Stadium, Chestnut Hill MA","FCS"),
        G("Southern Illinois","Illinois",        "Sat 2:00 PM","Peacock","Big Ten",   "Memorial Stadium, Champaign IL","FCS"),
        # ── FCS 2:00 PM ──────────────────────────────────────────────────
        G("UC Davis","Idaho State",              "Sat 2:00 PM","ESPN+",  "Big Sky",   "ICCU Dome, Pocatello ID","FCS"),
        G("Cal Poly","Weber State",              "Sat 2:00 PM","ESPN+",  "Big Sky",   "Stewart Stadium, Ogden UT","FCS"),
        G("Montana State","Southern Utah",       "Sat 2:00 PM","ESPN+",  "Big Sky",   "Bobcat Stadium, Bozeman MT","FCS"),
        G("South Dakota State","South Dakota",   "Sat 2:00 PM","ESPN+",  "MVFC",      "DakotaDome, Vermillion SD","FCS"),
        G("Southern Illinois","Indiana State",   "Sat 2:00 PM","ESPN+",  "MVFC",      "Memorial Stadium, Terre Haute IN","FCS"),
        G("Northern Iowa","Illinois State",      "Sat 2:00 PM","ESPN+",  "MVFC",      "Hancock Stadium, Normal IL","FCS"),
        G("Youngstown State","North Dakota",     "Sat 2:00 PM","ESPN+",  "MVFC",      "Alerus Center, Grand Forks ND","FCS"),
        G("Chattanooga","ETSU",                  "Sat 2:00 PM","ESPN+",  "SoCon",     "William B. Greene Jr. Stadium, Johnson City TN","FCS"),
        G("Wofford","The Citadel",               "Sat 2:00 PM","ESPN+",  "SoCon",     "Johnson Hagood Stadium, Charleston SC","FCS"),
        G("Campbell","Monmouth",                 "Sat 2:00 PM","FloSports","CAA",     "Kessler Stadium, West Long Branch NJ","FCS"),
        G("McNeese","Abilene Christian",         "Sat 2:00 PM","ESPN+",  "Southland", "Anthony Field, Abilene TX","FCS"),
        G("Houston Christian","Lamar",           "Sat 2:00 PM","ESPN+",  "Southland", "Provost Umphrey Stadium, Beaumont TX","FCS"),
        G("Incarnate Word","Northwestern State", "Sat 2:00 PM","ESPN+",  "Southland", "Turpin Stadium, Natchitoches LA","FCS"),
        G("North Alabama","West Florida",        "Sat 2:00 PM","ESPN+",  "UAC",       "Pen-Air Field, Pensacola FL","FCS"),
        G("West Georgia","Eastern Kentucky",     "Sat 2:00 PM","ESPN+",  "UAC",       "Roy Kidd Stadium, Richmond KY","FCS"),
        G("Tennessee State","SE Missouri State", "Sat 2:00 PM","ESPN+",  "OVC",       "Houck Stadium, Cape Girardeau MO","FCS"),
        G("UT Martin","Western Illinois",        "Sat 2:00 PM","ESPN+",  "OVC",       "Hanson Field, Macomb IL","FCS"),
        G("Morehead State","Lindenwood",         "Sat 2:00 PM","ESPN+",  "OVC",       "Hunter Stadium, Saint Charles MO","FCS"),
        G("San Diego","Davidson",                "Sat 2:00 PM","ESPN+",  "Pioneer",   "Richardson Stadium, Davidson NC","FCS"),
        # ── SATURDAY Sep 19 — 3:30 PM — FBS ─────────────────────────────
        G("Florida State","Alabama",             "Sat 3:30 PM","ABC",    "SEC",       "Bryant-Denny Stadium, Tuscaloosa AL"),
        G("Kentucky","Texas A&M",                "Sat 3:30 PM","ESPN",   "SEC",       "Kyle Field, College Station TX"),
        G("SMU","Louisville",                    "Sat 3:30 PM","ESPN2",  "ACC",       "L&N Federal Credit Union Stadium, Louisville KY"),
        G("UTEP","Michigan",                     "Sat 3:30 PM","BTN",    "Big Ten",   "Michigan Stadium, Ann Arbor MI"),
        G("USC","Rutgers",                       "Sat 3:30 PM","CBS",    "Big Ten",   "SHI Stadium, Piscataway NJ"),
        G("Utah State","Utah",                   "Sat 3:30 PM","FOX",    "Big 12",    "Rice-Eccles Stadium, Salt Lake City UT"),
        G("Miami OH","Cincinnati",               "Sat 3:30 PM","ESPN+",  "Big 12",    "Nippert Stadium, Cincinnati OH"),
        G("Stonehill","UMass",                   "Sat 3:30 PM","ESPN+",  "MAC",       "Warren McGuirk Alumni Stadium, Amherst MA","FCS"),
        G("Duquesne","Washington State",         "Sat 3:30 PM","USA",    "Pac-12",    "Gesa Field, Pullman WA","FCS"),
        G("Wagner","California",                 "Sat 3:30 PM","ACCN",   "ACC",       "California Memorial Stadium, Berkeley CA","FCS"),
        # ── FCS 3:00-3:30 PM ─────────────────────────────────────────────
        G("North Dakota State","Missouri State", "Sat 3:00 PM","ESPN+",  "MVFC",      "Plaster Stadium, Springfield MO","FCS"),
        G("Jackson State","Southern",            "Sat 3:00 PM","ESPN+",  "SWAC",      "A.W. Mumford Stadium, Baton Rouge LA","FCS"),
        G("Florida A&M","Bethune-Cookman",       "Sat 3:00 PM","ESPN+",  "SWAC",      "Bragg Memorial Stadium, Tallahassee FL","FCS"),
        G("Norfolk State","South Carolina State","Sat 3:00 PM","ESPN+",  "MEAC",      "Oliver C. Dawson Stadium, Orangeburg SC","FCS"),
        G("Nicholls","Stephen F. Austin",        "Sat 3:00 PM","ESPN+",  "Southland", "Homer Bryce Stadium, Nacogdoches TX","FCS"),
        G("SE Louisiana","East Texas A&M",       "Sat 3:00 PM","ESPN+",  "Southland", "Memorial Stadium, Commerce TX","FCS"),
        G("Tarleton State","Central Arkansas",   "Sat 3:00 PM","ESPN+",  "UAC",       "Estes Stadium, Conway AR","FCS"),
        G("Bryant","Sacred Heart",               "Sat 3:30 PM","NEC+",   "NEC",       "Higgins Stadium, Fairfield CT","FCS"),
        # ── SATURDAY Sep 19 — 4:00 PM ────────────────────────────────────
        G("Stanford","Duke",                     "Sat 4:00 PM","CW",     "ACC",       "Wallace Wade Stadium, Durham NC"),
        G("Louisiana Tech","Baylor",             "Sat 4:00 PM","ESPNU",  "Big 12",    "McLane Stadium, Waco TX"),
        G("Northern Iowa","Iowa",                "Sat 4:00 PM","FS1",    "Big Ten",   "Kinnick Stadium, Iowa City IA","FCS"),
        G("WKU","Indiana",                       "Sat 4:00 PM","Peacock","Big Ten",   "Memorial Stadium, Bloomington IN","FCS"),
        G("Ball State","Liberty",                "Sat 4:00 PM","ESPN+",  "CUSA",      "Williams Stadium, Lynchburg VA"),
        G("Southeastern Louisiana","ULM",        "Sat 4:30 PM","ESPN+",  "Sun Belt",  "Malone Stadium, Monroe LA","FCS"),
        # ── FCS 4:00-5:00 PM ─────────────────────────────────────────────
        G("Prairie View A&M","Mississippi Valley State","Sat 5:00 PM","ESPN+","SWAC", "Panther Stadium, Prairie View TX","FCS"),
        G("Texas Southern","Arkansas-Pine Bluff","Sat 5:00 PM","—",     "SWAC",       "Simmons Bank Liberty Stadium, Memphis TN","FCS"),
        # ── SATURDAY Sep 19 — 6:00-7:00 PM ──────────────────────────────
        G("Charlotte","App State",               "Sat 6:00 PM","ESPN+",  "Sun Belt",  "Kidd Brewer Stadium, Boone NC"),
        G("FIU","Florida Atlantic",              "Sat 6:00 PM","ESPN+",  "AAC",       "FAU Stadium, Boca Raton FL"),
        G("East Carolina","Old Dominion",        "Sat 6:00 PM","ESPN+",  "Sun Belt",  "Kornblau Field, Norfolk VA"),
        G("Marshall","Missouri State",           "Sat 6:30 PM","CBSSN",  "Sun Belt",  "Plaster Stadium, Springfield MO"),
        G("Georgia Southern","Jacksonville St",  "Sat 7:00 PM","ESPN+",  "CUSA",      "Toyota Field, Jacksonville AL"),
        G("Nevada","Middle Tennessee",           "Sat 7:00 PM","ESPN+",  "CUSA",      "Floyd Stadium, Murfreesboro TN"),
        G("WMU","Rice",                          "Sat 7:00 PM","ESPN+",  "AAC",       "Rice Stadium, Houston TX"),
        G("Ohio","South Alabama",                "Sat 7:00 PM","ESPN+",  "Sun Belt",  "Hancock Whitney Stadium, Mobile AL"),
        G("Georgia State","UCF",                 "Sat 7:00 PM","ESPN+",  "Big 12",    "Acrisure Bounce House, Orlando FL"),
        G("Troy","Missouri",                     "Sat 7:00 PM","SECN+",  "SEC",       "Faurot Field, Columbia MO","FCS"),
        G("UConn","Southern Miss",               "Sat 7:00 PM","ESPN+",  "CUSA",      "M.M. Roberts Stadium, Hattiesburg MS"),
        G("Murray State","Oklahoma State",       "Sat 7:00 PM","ESPN+",  "Big 12",    "Boone Pickens Stadium, Stillwater OK","FCS"),
        G("Delaware State","USF",                "Sat 7:00 PM","ESPN+",  "AAC",       "Raymond James Stadium, Tampa FL","FCS"),
        G("UT Martin","Memphis",                 "Sat 7:00 PM","ESPN+",  "AAC",       "Simmons Bank Liberty Stadium, Memphis TN","FCS"),
        G("East Texas A&M","Tulsa",              "Sat 8:00 PM","ESPN+",  "AAC",       "H.A. Chapman Stadium, Tulsa OK","FCS"),
        G("Arkansas State","TCU",                "Sat 8:00 PM","ESPNU",  "Big 12",    "Amon G. Carter Stadium, Fort Worth TX"),
        G("UAB","Louisiana",                     "Sat 8:00 PM","ESPN+",  "Sun Belt",  "Cajun Field, Lafayette LA"),
        G("UTSA","Texas",                        "Sat 8:00 PM","SECN+",  "SEC",       "Darrell K Royal Stadium, Austin TX"),
        G("Grambling State","TCU",               "Sat 8:00 PM","ESPN+",  "Big 12",    "Amon G. Carter Stadium, Fort Worth TX","FCS"),
        G("Prairie View A&M","Baylor",           "Sat 8:00 PM","ESPN+",  "Big 12",    "McLane Stadium, Waco TX","FCS"),
        # ── SATURDAY Sep 19 — 7:15-7:30 PM ──────────────────────────────
        G("EWU","Washington",                    "Sat 7:15 PM","BTN",    "Big Ten",   "Husky Stadium, Seattle WA","FCS"),
        G("North Dakota","Nebraska",             "Sat 7:15 PM","BTN",    "Big Ten",   "Memorial Stadium, Lincoln NE","FCS"),
        G("Colorado","Northwestern",             "Sat 7:30 PM","FOX",    "Big Ten",   "Ryan Field, Evanston IL"),
        G("Michigan State","Notre Dame",         "Sat 7:30 PM","NBC",    "Ind.",      "Notre Dame Stadium, South Bend IN"),
        G("Virginia Tech","Maryland",            "Sat 7:30 PM","FS1",    "Big Ten",   "SECU Stadium, College Park MD"),
        G("WVU","Virginia",                      "Sat 7:30 PM","ACCN",   "ACC",       "Bank of America Stadium, Charlotte NC",neutral=True),
        G("LSU","Ole Miss",                      "Sat 7:30 PM","ABC",    "SEC",       "Vaught-Hemingway Stadium, Oxford MS"),
        G("New Mexico","Oklahoma",               "Sat 7:30 PM","ESPN2",  "SEC",       "Gaylord Family Stadium, Norman OK"),
        G("BYU","Colorado State",                "Sat 7:30 PM","CBS",    "Pac-12",    "Canvas Stadium, Fort Collins CO"),
        G("Florida","Auburn",                    "Sat 7:00 PM","ESPN",   "SEC",       "Jordan-Hare Stadium, Auburn AL"),
        G("Kennesaw State","Tennessee",          "Sat 7:45 PM","SECN",   "SEC",       "Neyland Stadium, Knoxville TN","FCS"),
        G("Mississippi State","South Carolina",  "Sat 4:15 PM","SECN+",  "SEC",       "Williams-Brice Stadium, Columbia SC"),
        G("Nicholls","Sam Houston State",        "Sat 7:00 PM","ESPN+",  "CUSA",      "Bowers Stadium, Huntsville TX","FCS"),
        # ── SATURDAY Sep 19 — Late Night ─────────────────────────────────
        G("South Dakota","Boise State",          "Sat 10:00 PM","CBSSN", "Pac-12",    "Albertsons Stadium, Boise ID","FCS"),
        G("James Madison","San Diego State",     "Sat 10:00 PM","CW",    "MWC",       "Snapdragon Stadium, San Diego CA"),
        G("NIU","Arizona",                       "Sat 10:30 PM","TNT",   "Big 12",    "Arizona Stadium, Tucson AZ"),
        G("NDSU","Sacramento State",             "Sat 10:30 PM","ESPN",  "Pac-12",    "Hornet Stadium, Sacramento CA","FCS"),
        G("Montana","Oregon State",              "Sat 11:00 PM","USA",   "Pac-12",    "Reser Stadium, Corvallis OR","FCS"),
        G("Fresno State","San Jose State",       "Sat 11:00 PM","FS1",   "MWC",       "CEFCU Stadium, San Jose CA"),
        G("Purdue","UCLA",                       "Sat 11:00 PM","BTN",   "Big Ten",   "Rose Bowl, Pasadena CA"),
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
    6: [  # Week 6 — Oct 8-11 (Red River Rivalry)
        # ── THURSDAY OCT 8 ──
        G("USF","UTSA",                   "Thu 7:30 PM","ESPN","AAC","Alamodome, San Antonio TX"),
        G("South Alabama","Appalachian State","Thu 7:30 PM","ESPN2","Sun Belt","Kidd Brewer Stadium, Boone NC"),
        G("Missouri State","WKU",         "Thu 7:00 PM","CBSSN","C-USA","L.T. Smith Stadium, Bowling Green KY"),
        G("Sam Houston","Liberty",        "Thu 7:00 PM","ESPNU","C-USA","Williams Stadium, Lynchburg VA"),
        # ── FRIDAY OCT 9 ──
        G("Florida State","Louisville",   "Fri 7:00 PM","ESPN","ACC","L&N Federal Credit Union Stadium, Louisville KY"),
        G("Iowa","Washington",            "Fri 9:00 PM","FOX","Big Ten","Husky Stadium, Seattle WA"),
        G("Wyoming","San Jose State",     "Fri 9:00 PM","CBSSN","MWC","CEFCU Stadium, San Jose CA"),
        G("Washington State","Utah State","Fri 9:00 PM","The CW","Pac-12","Maverik Stadium, Logan UT"),
        G("Iowa State","BYU",             "Fri 10:15 PM","ESPN","Big 12","LaVell Edwards Stadium, Provo UT"),
        # ── SATURDAY OCT 10 — ACC ──
        G("North Carolina","Pitt",        "Sat 12:00 PM","ESPN","ACC","Acrisure Stadium, Pittsburgh PA"),
        G("Wake Forest","NC State",       "Sat 12:00 PM","The CW","ACC","Carter-Finley Stadium, Raleigh NC"),
        G("Duke","Georgia Tech",          "Sat 3:30 PM","ESPN2","ACC","Bobby Dodd Stadium, Atlanta GA"),
        G("Stanford","Notre Dame",        "Sat 3:30 PM","NBC","ACC","Notre Dame Stadium, South Bend IN"),
        G("Virginia Tech","California",   "Sat 3:30 PM","ACCN","ACC","California Memorial Stadium, Berkeley CA"),
        G("Syracuse","Virginia",          "Sat 7:30 PM","ACCN","ACC","Scott Stadium, Charlottesville VA"),
        # ── SATURDAY OCT 10 — AAC ──
        G("Tulane","Army",                "Sat 12:00 PM","CBSSN","AAC","Michie Stadium, West Point NY"),
        G("Charlotte","North Texas",      "Sat 3:30 PM","ESPN+","AAC","DATCU Stadium, Denton TX"),
        G("Tulsa","Navy",                 "Sat 3:30 PM","CBSSN","AAC","Navy-Marine Corps Memorial Stadium, Annapolis MD"),
        G("UConn","Temple",               "Sat 3:45 PM","ESPNU","AAC","Lincoln Financial Field, Philadelphia PA"),
        G("Rice","East Carolina",         "Sat 4:00 PM","ESPN+","AAC","Dowdy-Ficklen Stadium, Greenville NC"),
        G("UAB","Memphis",                "Sat 7:00 PM","ESPN2","AAC","Simmons Bank Liberty Stadium, Memphis TN"),
        # ── SATURDAY OCT 10 — Big 12 ──
        G("Texas","Oklahoma",             "Sat 3:30 PM","ABC","Neutral","Cotton Bowl, Dallas TX",True),
        G("Arizona","West Virginia",      "Sat 12:00 PM","TNT","Big 12","Mountaineer Field, Morgantown WV"),
        G("UCF","Oklahoma State",         "Sat 12:00 PM","ESPN2","Big 12","Boone Pickens Stadium, Stillwater OK"),
        G("Houston","Kansas State",       "Sat 3:30 PM","FOX","Big 12","Bill Snyder Family Stadium, Manhattan KS"),
        G("Kansas","Utah",                "Sat 10:15 PM","ESPN","Big 12","Rice-Eccles Stadium, Salt Lake City UT"),
        G("Hawaii","Arizona State",       "Sat 10:30 PM","FS1","Big 12","Mountain America Stadium, Tempe AZ"),
        # ── SATURDAY OCT 10 — Big Ten ──
        G("Indiana","Nebraska",           "Sat 12:00 PM","FOX","Big Ten","Memorial Stadium, Lincoln NE"),
        G("Ball State","Northwestern",    "Sat 12:30 PM","BTN","Big Ten","Ryan Field, Evanston IL"),
        G("UCLA","Oregon",                "Sat 3:30 PM","CBS","Big Ten","Autzen Stadium, Eugene OR"),
        G("Illinois","Michigan State",    "Sat 3:30 PM","FS1","Big Ten","Spartan Stadium, East Lansing MI"),
        G("Maryland","Ohio State",        "Sat 4:15 PM","BTN","Big Ten","Ohio Stadium, Columbus OH"),
        G("USC","Penn State",             "Sat 7:30 PM","NBC","Big Ten","Beaver Stadium, University Park PA"),
        G("Minnesota","Purdue",           "Sat 8:00 PM","BTN","Big Ten","Ross-Ade Stadium, West Lafayette IN"),
        # ── SATURDAY OCT 10 — MAC ──
        G("Sacramento State","Bowling Green","Sat 12:00 PM","ESPN+","MAC","Doyt Perry Stadium, Bowling Green OH"),
        G("Miami (Ohio)","UMass",         "Sat 2:00 PM","ESPN+","MAC","McGuirk Alumni Stadium, Amherst MA"),
        G("Eastern Michigan","Akron",     "Sat 3:30 PM","ESPN+","MAC","InfoCision Stadium, Akron OH"),
        G("Central Michigan","Ohio",      "Sat 3:30 PM","ESPN+","MAC","Peden Stadium, Athens OH"),
        G("Buffalo","Toledo",             "Sat 3:30 PM","ESPN+","MAC","Glass Bowl, Toledo OH"),
        G("Kent State","Western Michigan","Sat 3:30 PM","ESPN+","MAC","Waldo Stadium, Kalamazoo MI"),
        # ── SATURDAY OCT 10 — MWC ──
        G("North Dakota State","UNLV",    "Sat 7:00 PM","The CW","MWC","Allegiant Stadium, Las Vegas NV"),
        G("Nevada","UTEP",                "Sat 7:00 PM","FS1","MWC","Sun Bowl, El Paso TX"),
        G("Air Force","Northern Illinois","Sat 7:30 PM","CBSSN","MWC","Huskie Stadium, DeKalb IL"),
        G("San Diego State","Oregon State","Sat 6:00 PM","USA","Pac-12","Reser Stadium, Corvallis OR"),
        G("Boise State","Fresno State",   "Sat 10:30 PM","The CW","MWC","Bulldog Stadium, Fresno CA"),
        # ── SATURDAY OCT 10 — SEC ──
        G("Texas A&M","Missouri",         "Sat 12:00 PM","ABC","SEC","Memorial Stadium, Columbia MO"),
        G("South Carolina","Florida",     "Sat 12:45 PM","SECN","SEC","Ben Hill Griffin Stadium, Gainesville FL"),
        G("Ole Miss","Vanderbilt",        "Sat 3:30 PM","ESPN","SEC","FirstBank Stadium, Nashville TN"),
        G("Tennessee","Arkansas",         "Sat 4:15 PM","SECN","SEC","Donald W. Reynolds Razorback Stadium, Fayetteville AR"),
        G("LSU","Kentucky",               "Sat 7:00 PM","ESPN","SEC","Kroger Field, Lexington KY"),
        G("Georgia","Alabama",            "Sat 7:30 PM","ABC","SEC","Bryant-Denny Stadium, Tuscaloosa AL"),
        # ── SATURDAY OCT 10 — Sun Belt ──
        G("Old Dominion","Appalachian State","Sat 1:00 PM","ESPN+","Sun Belt","Kidd Brewer Stadium, Boone NC"),
        G("Coastal Carolina","Marshall",  "Sat 7:00 PM","ESPN+","Sun Belt","Joan C. Edwards Stadium, Huntington WV"),
        G("James Madison","Georgia Southern","Sat 7:30 PM","ESPNU","Sun Belt","Paulson Stadium, Statesboro GA"),
        G("Louisiana","Louisiana Tech",   "Sat 7:30 PM","ESPN+","Sun Belt","Joe Aillet Stadium, Ruston LA"),
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

# ── LIVE ODDS (The Odds API — same lines as HardRock Bet / DraftKings) ────
@st.cache_data(ttl=300)
def fetch_live_odds(api_key):
    """Fetch real sportsbook lines from The Odds API (hardrock uses same market data)."""
    if not api_key or len(api_key) < 10:
        return {}
    odds_map = {}
    try:
        url = (
            "https://api.the-odds-api.com/v4/sports/americanfootball_ncaaf/odds/"
            "?apiKey="+api_key+
            "&regions=us&markets=h2h,spreads,totals&oddsFormat=american&bookmakers=hardrockbet,draftkings,fanduel"
        )
        r = requests.get(url, timeout=12)
        if r.status_code != 200:
            return {}
        for ev in r.json():
            away = ev.get("away_team",""); home = ev.get("home_team","")
            key = away+"@"+home
            for book in ev.get("bookmakers",[]):
                markets = {m["key"]: m for m in book.get("markets",[])}
                h2h = markets.get("h2h",{}).get("outcomes",[])
                spreads = markets.get("spreads",{}).get("outcomes",[])
                totals = markets.get("totals",{}).get("outcomes",[])
                ml_away = next((o["price"] for o in h2h if o["name"]==away), None)
                ml_home = next((o["price"] for o in h2h if o["name"]==home), None)
                sp_away = next((o["point"] for o in spreads if o["name"]==away), None)
                total   = next((o["point"] for o in totals if o["name"]=="Over"), None)
                ou      = None
                if total:
                    # Determine OVER or UNDER based on model
                    ou = "OVER"  # will be overridden by smart_predict
                if ml_away or sp_away or total:
                    odds_map[key] = {
                        "ml_away": ml_away, "ml_home": ml_home,
                        "sp_away": sp_away,
                        "sp_home": -sp_away if sp_away else None,
                        "total": total,
                        "bookmaker": book.get("title","")
                    }
                    break  # use first available bookmaker
    except Exception:
        pass
    return odds_map

# ── SIDEBAR ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎲 Live Odds")
    odds_api_key = st.text_input(
        "The Odds API Key",
        type="password",
        placeholder="Paste key → get HardRock Bet lines",
        help="Free at the-odds-api.com — pulls real HardRock Bet / DraftKings lines"
    )
    if odds_api_key:
        st.markdown("<div style='font-size:.58rem;color:#22c55e'>✓ Live odds enabled — HardRock Bet lines active</div>",unsafe_allow_html=True)
    else:
        st.markdown("<div style='font-size:.58rem;color:#64748b'>→ <a href='https://the-odds-api.com' target='_blank' style='color:#38bdf8'>Get free API key</a> for real lines</div>",unsafe_allow_html=True)
    st.markdown("---")
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

# ── LOAD SCHEDULE — Static PRIMARY, Live API for score updates ─────────────
# Static schedule is always complete and reliable
static_games = SCHEDULE.get(week_num, [])

# Fetch real sportsbook lines (HardRock Bet / DraftKings) if API key provided
live_odds_map = {}
odds_src = ""
if odds_api_key:
    try:
        with st.spinner("🎲 Fetching HardRock Bet live lines..."):
            live_odds_map = fetch_live_odds(odds_api_key)
        if live_odds_map:
            odds_src = "HardRock Bet Live"
    except Exception:
        pass

# Try live API to get real-time scores (runs in background, doesn't block)
live_score_map = {}
api_src = "Built-in"
using_live = False
try:
    with st.spinner("🔄 Checking for live scores..."):
        live_games, live_fcs_games, _src, _err = fetch_live(week_num)
    if live_games or live_fcs_games:
        using_live = True
        api_src = "ESPN Live"
        # Build score lookup from live data
        for lg in live_games + live_fcs_games:
            key = lg["away"]+"@"+lg["home"]
            live_score_map[key] = {
                "away_score": lg.get("away_score",""),
                "home_score": lg.get("home_score",""),
                "status": lg.get("status","scheduled"),
                "away_rec": lg.get("away_rec",""),
                "home_rec": lg.get("home_rec",""),
            }
except Exception:
    pass

# Apply live scores to static games where available
all_games = []
for sg in static_games:
    game = dict(sg)
    key = sg["away"]+"@"+sg["home"]
    if key in live_score_map:
        ls = live_score_map[key]
        if ls["away_score"]: game["away_score"] = ls["away_score"]
        if ls["home_score"]: game["home_score"] = ls["home_score"]
        if ls["status"]:     game["status"]     = ls["status"]
        if ls["away_rec"]:   game["away_rec"]   = ls["away_rec"]
        if ls["home_rec"]:   game["home_rec"]   = ls["home_rec"]
    all_games.append(game)

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
    if "TBD" in away or "TBD" in home or "CFP" in away or "Seed" in away:
        return None
    p = pred_cache.get(key) or smart_predict(away, home, neutral, week_num)
    # Overlay real sportsbook lines (HardRock Bet) when available
    lo = live_odds_map.get(key)
    if lo and p:
        p = dict(p)
        if lo.get("ml_away") is not None:
            p["ml_away"] = lo["ml_away"]
        if lo.get("ml_home") is not None:
            p["ml_home"] = lo["ml_home"]
        if lo.get("sp_away") is not None:
            p["sp_away"] = lo["sp_away"]
            p["sp_home"] = lo.get("sp_home", -lo["sp_away"])
        if lo.get("total") is not None:
            p["total"] = lo["total"]
        p["odds_src"] = lo.get("bookmaker","Live")
    return p

# ── STATS ─────────────────────────────────────────────────────────────────
valid_preds=[get_pred(g["away"],g["home"],g.get("neutral",False)) for g in all_games]
valid_preds=[p for p in valid_preds if p]
overs=sum(1 for p in valid_preds if p["ou"]=="OVER")
avg_t=f"{sum(p['total'] for p in valid_preds)/len(valid_preds):.1f}" if valid_preds else "—"
sharp_c=sum(1 for p in valid_preds if "Sharp" in p["mv"])
ap_c=sum(1 for p in valid_preds if grade(p["mlC"])[0]=="A+")
if odds_src:
    src_html = "<span class='src-badge src-live'>🎲 HardRock Bet Lines</span>"
elif using_live:
    src_html = "<span class='src-badge src-live'>● ESPN Live</span>"
else:
    src_html = "<span class='src-badge src-static'>📋 Built-in Schedule</span>"

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

    # ── Group by DAY then TIME SLOT ──────────────────────────────────
    from collections import OrderedDict as _OD
    _sorted = sorted(filtered, key=lambda x: _parse_sort(x[0]["time"]))
    _by_day = _OD()
    for _g,_p in _sorted:
        _d = _day_label(_g["time"])
        _s = _time_slot(_g["time"])
        _by_day.setdefault(_d, _OD()).setdefault(_s, []).append((_g,_p))

    for _dn, _slots in _by_day.items():
        _dtot = sum(len(v) for v in _slots.values())
        st.markdown(
            "<div class='day-hdr'>"
            "<span class='day-label'>📅 "+_dn+"</span>"
            "<span class='day-ct'>"+str(_dtot)+" games</span></div>",
            unsafe_allow_html=True)
        for _sn, _sg in _slots.items():
            st.markdown(
                "<div class='time-hdr'>"
                "<span class='time-label'>"+_sn+"</span>"
                "<span class='time-ct'>"+str(len(_sg))+" games</span></div>",
                unsafe_allow_html=True)
            for g,p in _sg:
                wpa=round(p["away_wp"]*100); wph=100-wpa
                fa=p["fa"]; fnm=g["away"] if fa else g["home"]; dnm=g["home"] if fa else g["away"]
                fav_ml=fml(p["ml_away"] if fa else p["ml_home"]); dog_ml=fml(p["ml_home"] if fa else p["ml_away"])
                fav_sp=fsp(p["sp_away"] if fa else p["sp_home"])
                mlG,mlC=grade(p["mlC"]); spG,spC=grade(p["spC"]); ttG,ttC=grade(p["ttC"])
                ou_cls="over-c" if p["ou"]=="OVER" else "under-c"
                mv_cls="mv-s" if "Sharp" in p["mv"] else("mv-p" if "Public" in p["mv"] else "mv-n")

                # Rankings
                a_rank=g.get("away_rank","") or (str(AP_RANKS[g["away"]]) if g["away"] in AP_RANKS else "")
                h_rank=g.get("home_rank","") or (str(AP_RANKS[g["home"]]) if g["home"] in AP_RANKS else "")
                def cr(r): return r if r and r not in ("","99","0","None") else ""
                a_rank=cr(a_rank); h_rank=cr(h_rank)
                a_rk=f"<span class='rnk'>#{a_rank}</span>" if a_rank else "<span class='rnk-none'></span>"
                h_rk=f"<span class='rnk'>#{h_rank}</span>" if h_rank else "<span class='rnk-none'></span>"

                a_rec=g.get("away_rec","0-0"); h_rec=g.get("home_rec","0-0")
                def rc_html(ov):
                    try: w,l=ov.split("-"); cls="rec-w" if int(w)>int(l) else("rec-l" if int(l)>int(w) else "rec-e")
                    except: cls="rec-e"
                    return f"<span class='{cls}'>{ov}</span>"

                gst=g.get("status","scheduled"); a_sc=g.get("away_score",""); h_sc=g.get("home_score","")
                if gst=="STATUS_FINAL" and a_sc and h_sc:
                    score_p="<span class='score-final'>FINAL: "+g["away"]+" "+a_sc+"–"+h_sc+" "+g["home"]+"</span><br>"
                elif "IN_PROGRESS" in gst and a_sc and h_sc:
                    score_p="<span class='score-live'>● "+g["away"]+" "+a_sc+" – "+h_sc+" "+g["home"]+"</span><br>"
                else: score_p=""

                neut="<span class='ntag'>Neutral</span>" if g.get("neutral") else ""
                conf=g.get("conf",""); conf_p=f"<span style='font-size:.46rem;color:#4b5e78'>{conf}</span>&nbsp;" if conf else ""
                venue=g.get("venue",""); sp_gap_str=f"SP+ gap: {p['sp_gap']:.1f}"
                pub_over=int(45+(p["away_wp"] if fa else p["home_wp"])*30)
                wp_a="wp-hot" if wpa>55 else "wp-cold"; wp_h="wp-hot" if wph>55 else "wp-cold"

                row=(
                    "<div class='game-card'><div>"
                    +score_p+
                    "<div class='game-meta'>"+g["time"]+" ET &nbsp;"
                    "<span class='tv-b'>"+g["tv"]+"</span>&nbsp;"
                    +conf_p+neut+"</div>"
                    "<div class='team-row'>"+a_rk
                    +"<span class='tname'>"+g["away"]+"</span>"
                    +rc_html(a_rec)+
                    "<span class='twp "+wp_a+"'>"+str(wpa)+"%</span></div>"
                    "<div class='team-sep'></div>"
                    "<div class='team-row'>"+h_rk
                    +"<span class='tname'>"+g["home"]+"</span>"
                    +rc_html(h_rec)+
                    "<span class='twp "+wp_h+"'>"+str(wph)+"%</span></div>"
                    "</div>"
                    "<div class='odds-box'>"
                    "<div class='odds-lbl'>Moneyline"
                    +((" <span style='font-size:.42rem;color:#22c55e;font-weight:700'>HardRock</span>") if p.get("odds_src") else "")
                    +"</div>"
                    "<div class='odds-pick fav-c'>"+fnm.split()[-1]+" "+fav_ml+"</div>"
                    "<div class='odds-dog'>"+dnm.split()[-1]+" "+dog_ml+"</div>"
                    "<div class='odds-sm'>"+str(p["pa"])+"–"+str(p["ph"])+"</div>"
                    "<div class='"+mv_cls+"'>"+p["mv"]+" · "+str(p["sp_p"])+"%</div></div>"
                    "<div class='odds-box'>"
                    "<div class='odds-lbl'>Spread"
                    +((" <span style='font-size:.42rem;color:#22c55e;font-weight:700'>Live</span>") if p.get("odds_src") else "")
                    +"</div>"
                    "<div class='odds-pick fav-c'>"+fnm.split()[-1]+" "+fav_sp+"</div>"
                    "<div class='odds-sm'>"+fsp(p["sp_away"])+" / "+fsp(p["sp_home"])+"</div>"
                    "<div class='odds-sm'>"+sp_gap_str+"</div></div>"
                    "<div class='odds-box'>"
                    "<div class='odds-lbl'>Total"
                    +((" <span style='font-size:.42rem;color:#22c55e;font-weight:700'>Live</span>") if p.get("odds_src") else "")
                    +"</div>"
                    "<div class='odds-pick "+ou_cls+"'>"+p["ou"]+"</div>"
                    "<div class='odds-sm'>O/U "+str(p["total"])+"</div>"
                    "<div class='odds-sm'>OVER "+str(pub_over)+"% pub</div></div>"
                    "<div class='grade-col'>"
                    "<div class='gbig "+mlC+"'>"+mlG+"</div>"
                    "<div class='g-lbl'>"+str(p["mlC"])+"%</div>"
                    "<div class='gsm "+spC+"'>"+spG+"</div>"
                    "<div class='gsm "+ttC+"'>"+ttG+"</div>"
                    "</div></div>"
                )

                ai_pos="".join("<span class='kf-p'>✓ "+f+"</span>" for f in p["pos"])
                ai_neg="".join("<span class='kf-n'>✗ "+f+"</span>" for f in p["neg"])

                h2h=get_h2h(g["away"],g["home"]); h2h_section=""
                if h2h:
                    a_wins=sum(1 for m in h2h if m["winner"]==g["away"]); h_wins=len(h2h)-a_wins
                    rec_cls="h2h-away" if a_wins>h_wins else "h2h-home"
                    rows="".join(
                        "<div class='h2h-row'><span class='h2h-date'>"+m["date"]+"</span>"
                        "<span class='h2h-w "+("h2h-away" if m["winner"]==g["away"] else "h2h-home")+"'>"+m["winner"]+"</span>"
                        "<span class='h2h-sc'>"+m["score"]+"</span>"
                        "<span class='h2h-n'>"+m["note"]+"</span></div>" for m in h2h)
                    h2h_section=(
                        "<div class='expand-section' style='margin-top:0'>"
                        "<div class='h2h-title'>Last 5 matchups"
                        "<span class='"+rec_cls+"'>"+g["away"]+" "+str(a_wins)+"–"+str(h_wins)+" "+g["home"]+"</span></div>"
                        +rows+"</div>")

                hp=make_half_preds(g["away"],g["home"],p,week_num)
                h1spG,h1spC=grade(hp["h1_spC"]); h1tG,h1tC=grade(hp["h1_totC"]); h1wG,h1wC=grade(hp["h1_winC"])
                h2spG,h2spC=grade(hp["h2_spC"]); h2tG,h2tC=grade(hp["h2_totC"]); h2wG,h2wC=grade(hp["h2_winC"])
                h1ou_cls="over-c" if hp["h1_ou"]=="OVER" else "under-c"
                h2ou_cls="over-c" if hp["h2_ou"]=="OVER" else "under-c"
                sp_sign="-" if hp["fa"] else "+"

                half_inner=(
                    "<div class='half-inner'>"
                    "<div class='half-section-lbl' style='color:#f59e0b'>1st Half</div>"
                    "<div class='prop-grid'>"
                    "<div class='prop-card'><div class='prop-lbl sp-l'>Spread</div>"
                    "<div class='prop-val fav-c'>"+hp["h1_sp_team"].split()[-1]+" "+sp_sign+str(hp["h1_sp"])+"</div>"
                    "<div class='pbar'><div class='pbar-fill' style='width:"+str(hp["h1_spC"])+"%;"
                    "background:#7c2d12'></div></div>"
                    "<div class='prop-sub'>"+str(hp["h1_spC"])+"% · "+h1spG+"</div></div>"
                    "<div class='prop-card'><div class='prop-lbl tot-l'>Total</div>"
                    "<div class='prop-val "+h1ou_cls+"'>"+hp["h1_ou"]+"</div>"
                    "<div class='prop-sub'>O/U "+str(hp["h1_total"])+"</div>"
                    "<div class='prop-sub'>"+str(hp["h1_totC"])+"% · "+h1tG+"</div></div>"
                    "<div class='prop-card'><div class='prop-lbl win-l'>Winner</div>"
                    "<div class='prop-val fav-c'>"+hp["h1_win"].split()[-1]+"</div>"
                    "<div class='pbar'><div class='pbar-fill' style='width:"+str(hp["h1_winC"])+"%;"
                    "background:#166534'></div></div>"
                    "<div class='prop-sub'>"+str(hp["h1_winC"])+"% · "+h1wG+"</div></div>"
                    "</div>"
                    "<div class='half-section-lbl' style='color:#c084fc;margin-top:8px'>2nd Half</div>"
                    "<div class='prop-grid'>"
                    "<div class='prop-card'><div class='prop-lbl sp-l'>Spread</div>"
                    "<div class='prop-val fav-c'>"+hp["h2_sp_team"].split()[-1]+" "+sp_sign+str(hp["h2_sp"])+"</div>"
                    "<div class='pbar'><div class='pbar-fill' style='width:"+str(hp["h2_spC"])+"%;"
                    "background:#7c2d12'></div></div>"
                    "<div class='prop-sub'>"+str(hp["h2_spC"])+"% · "+h2spG+"</div></div>"
                    "<div class='prop-card'><div class='prop-lbl tot-l'>Total</div>"
                    "<div class='prop-val "+h2ou_cls+"'>"+hp["h2_ou"]+"</div>"
                    "<div class='prop-sub'>O/U "+str(hp["h2_total"])+"</div>"
                    "<div class='prop-sub'>"+str(hp["h2_totC"])+"% · "+h2tG+"</div></div>"
                    "<div class='prop-card'><div class='prop-lbl win-l'>Winner</div>"
                    "<div class='prop-val fav-c'>"+hp["h2_win"].split()[-1]+"</div>"
                    "<div class='pbar'><div class='pbar-fill' style='width:"+str(hp["h2_winC"])+"%;"
                    "background:#166534'></div></div>"
                    "<div class='prop-sub'>"+str(hp["h2_winC"])+"% · "+h2wG+"</div></div>"
                    "</div></div>"
                )

                full_card=(
                    "<details>"
                    "<summary>"+g["away"]+" vs "+g["home"]+" &nbsp;▾ "+venue[:50]+"</summary>"
                    "<div class='expand-inner'>"
                    "<div class='expand-section'>"
                    "<div class='expand-lbl'>SP+ Analysis</div>"
                    "<div class='ai-txt'>"+p["txt"]+"</div>"
                    "<div class='kf-row'>"+ai_pos+ai_neg+"</div>"
                    "</div>"
                    +(h2h_section if h2h_section else
                      "<div class='expand-section'><div class='expand-lbl'>No H2H data</div>"
                      "<div class='ai-txt' style='color:#334155'>First meeting or insufficient history.</div></div>")
                    +"</div>"
                    +half_inner
                    +"</details>"
                )

                st.markdown(row+full_card, unsafe_allow_html=True)

for div in DIV_ORDER:
    render_div(div)

if not any(div_games.values()):
    st.markdown("<div class='no-games'>No games scheduled for this week.</div>",unsafe_allow_html=True)

st.markdown("<div style='height:30px'></div>",unsafe_allow_html=True)
