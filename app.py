import streamlit as st
import random
import pandas as pd
from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple

# --- 1. DATA MODELS ---

@dataclass
class Team:
    id: str
    name: str
    fifa_ranking: int

@dataclass
class Match:
    id: str
    home_team: Optional[Team] = None
    away_team: Optional[Team] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    home_penalties: Optional[int] = None
    away_penalties: Optional[int] = None
    is_played: bool = False
    group_id: str = ""
    winner_id: Optional[str] = None

@dataclass
class Group:
    id: str
    name: str
    teams: List[Team]

# --- 2. OFFICIAL DATA SEEDING ---

def seed_data():
    groups_config = {
        "A": [("MEX", "Mexico", 15), ("RSA", "South Africa", 59), ("KOR", "South Korea", 22), ("CZE", "Czech Republic", 47)],
        "B": [("CAN", "Canada", 38), ("BIH", "Bosnia and Herzegovina", 75), ("QAT", "Qatar", 35), ("SUI", "Switzerland", 15)],
        "C": [("BRA", "Brazil", 5), ("MAR", "Morocco", 14), ("HAI", "Haiti", 85), ("SCO", "Scotland", 51)],
        "D": [("USA", "United States", 11), ("PAR", "Paraguay", 56), ("AUS", "Australia", 24), ("TUR", "Turkey", 26)],
        "E": [("GER", "Germany", 13), ("CUW", "Curaçao", 90), ("CIV", "Ivory Coast", 38), ("ECU", "Ecuador", 30)],
        "F": [("NED", "Netherlands", 7), ("JPN", "Japan", 18), ("SWE", "Sweden", 28), ("TUN", "Tunisia", 41)],
        "G": [("BEL", "Belgium", 10), ("EGY", "Egypt", 36), ("IRN", "Iran", 20), ("NZL", "New Zealand", 91)],
        "H": [("ESP", "Spain", 3), ("CPV", "Cape Verde", 65), ("KSA", "Saudi Arabia", 56), ("URU", "Uruguay", 11)],
        "I": [("FRA", "France", 2), ("SEN", "Senegal", 17), ("IRQ", "Iraq", 58), ("NOR", "Norway", 47)],
        "J": [("ARG", "Argentina", 1), ("ALG", "Algeria", 44), ("AUT", "Austria", 22), ("JOR", "Jordan", 70)],
        "K": [("POR", "Portugal", 6), ("COD", "DR Congo", 60), ("UZB", "Uzbekistan", 64), ("COL", "Colombia", 12)],
        "L": [("ENG", "England", 4), ("CRO", "Croatia", 10), ("GHA", "Ghana", 64), ("PAN", "Panama", 43)]
    }
    teams_dict = {}
    groups = {}
    matches = {}
    for gid, t_data in groups_config.items():
        group_teams = [Team(tid, name, rank) for tid, name, rank in t_data]
        for t in group_teams: teams_dict[t.id] = t
        groups[gid] = Group(gid, f"Group {gid}", group_teams)
        for i in range(len(group_teams)):
            for j in range(i + 1, len(group_teams)):
                t1, t2 = group_teams[i], group_teams[j]
                m_id = f"{gid}_{t1.id}_{t2.id}"
                matches[m_id] = Match(m_id, t1, t2, group_id=gid)
    return teams_dict, groups, matches

# --- 3. STATE MANAGEMENT ---

def init_state():
    if 'initialized' not in st.session_state:
        teams, groups, matches = seed_data()
        st.session_state.teams = teams
        st.session_state.groups = groups
        st.session_state.matches = matches
        st.session_state.knockout = {
            "R32": [Match(f"R32_{i}") for i in range(16)],
            "R16": [Match(f"R16_{i}") for i in range(8)],
            "QF": [Match(f"QF_{i}") for i in range(4)],
            "SF": [Match(f"SF_{i}") for i in range(2)],
            "TP": [Match("TP_0")],
            "F": [Match("F_0")]
        }
        st.session_state.initialized = True

def clear_match_state(m: Match):
    """Resets a match and its associated session state keys."""
    m.is_played = False
    m.home_score = None
    m.away_score = None
    m.home_penalties = None
    m.away_penalties = None
    m.winner_id = None
    for key_prefix in ["score_h_", "score_a_", "pen_h_", "pen_a_", "played_", "winner_"]:
        st.session_state.pop(f"{key_prefix}{m.id}", None)

def sync_state():
    """Synchronizes Match objects with session_state."""
    # Sync Group Stage
    for m_id, match in st.session_state.matches.items():
        match.home_score = st.session_state.get(f"score_h_{m_id}")
        match.away_score = st.session_state.get(f"score_a_{m_id}")
        match.is_played = st.session_state.get(f"played_{m_id}", False)

    # Sync Knockout
    for round_name, matches in st.session_state.knockout.items():
        for m in matches:
            m.home_score = st.session_state.get(f"score_h_{m.id}")
            m.away_score = st.session_state.get(f"score_a_{m.id}")
            m.home_penalties = st.session_state.get(f"pen_h_{m.id}")
            m.away_penalties = st.session_state.get(f"pen_a_{m.id}")
            m.is_played = st.session_state.get(f"played_{m.id}", False)
            m.winner_id = st.session_state.get(f"winner_{m.id}")

            # Recalculate winner for knockout only
            if m.is_played and m.home_team and m.away_team:
                h, a = m.home_score, m.away_score
                if h is not None and a is not None:
                    if h > a: new_winner = m.home_team.id
                    elif a > h: new_winner = m.away_team.id
                    else:
                        ph = st.session_state.get(f"pen_h_{m.id}", 0)
                        pa = st.session_state.get(f"pen_a_{m.id}", 0)
                        new_winner = m.home_team.id if ph >= pa else m.away_team.id
                    
                    if m.winner_id != new_winner:
                        m.winner_id = new_winner
                        st.session_state[f"winner_{m.id}"] = new_winner

# --- 4. ENGINE & CASCADE RESET ---

def calculate_standings(group: Group, matches: Dict[str, Match]) -> pd.DataFrame:
    stats = {t.id: {"id": t.id, "Team": t.name, "P": 0, "W": 0, "D": 0, "L": 0, "GF": 0, "GA": 0, "GD": 0, "Pts": 0} for t in group.teams}
    for match in matches.values():
        if match.group_id == group.id and match.is_played:
            h, a = match.home_team.id, match.away_team.id
            hs, ascore = match.home_score, match.away_score
            stats[h]["P"] += 1; stats[a]["P"] += 1
            stats[h]["GF"] += hs; stats[h]["GA"] += ascore
            stats[a]["GF"] += ascore; stats[a]["GA"] += hs
            if hs > ascore: stats[h]["W"] += 1; stats[h]["Pts"] += 3; stats[a]["L"] += 1
            elif hs < ascore: stats[a]["W"] += 1; stats[a]["Pts"] += 3; stats[h]["L"] += 1
            else: stats[h]["D"] += 1; stats[a]["D"] += 1; stats[h]["Pts"] += 1; stats[a]["Pts"] += 1
    for s in stats.values(): s["GD"] = s["GF"] - s["GA"]
    return pd.DataFrame(list(stats.values())).sort_values(by=["Pts", "GD", "GF"], ascending=False).reset_index(drop=True)

def update_bracket():
    if not all(m.is_played for m in st.session_state.matches.values()): return

    all_standings = {gid: calculate_standings(g, st.session_state.matches) for gid, g in st.session_state.groups.items()}
    winners = {gid: st.session_state.teams[df.iloc[0]['id']] for gid, df in all_standings.items()}
    runners_up = {gid: st.session_state.teams[df.iloc[1]['id']] for gid, df in all_standings.items()}
    thirds = []
    for gid, df in all_standings.items():
        thirds.append({"group": gid, "team": st.session_state.teams[df.iloc[2]['id']], "Pts": df.iloc[2]['Pts'], "GD": df.iloc[2]['GD'], "GF": df.iloc[2]['GF']})
    best_thirds = sorted(thirds, key=lambda x: (x['Pts'], x['GD'], x['GF']), reverse=True)[:8]

    # R32 Mapping
    r32 = st.session_state.knockout["R32"]
    def p3(pools, used):
        for t in best_thirds:
            if t['group'] in pools and t['group'] not in used: used.add(t['group']); return t['team']
        for t in best_thirds:
            if t['group'] not in used: used.add(t['group']); return t['team']
        return None

    used_3 = set()
    mappings = [
        (runners_up["A"], runners_up["B"]), (winners["C"], runners_up["F"]), (winners["E"], p3(["A","B","C","D","F"], used_3)),
        (winners["F"], runners_up["C"]), (winners["I"], p3(["C","D","F","G","H"], used_3)), (winners["A"], p3(["C","E","F","H","I"], used_3)),
        (winners["L"], p3(["E","H","I","J","K"], used_3)), (winners["G"], p3(["A","E","H","I","J"], used_3)), (winners["D"], p3(["B","E","F","I","J"], used_3)),
        (winners["H"], runners_up["J"]), (runners_up["K"], runners_up["L"]), (winners["B"], p3(["E","F","G","I","J"], used_3)),
        (runners_up["D"], runners_up["G"]), (winners["J"], runners_up["H"]), (winners["K"], p3(["D","E","I","J","L"], used_3)),
        (runners_up["E"], runners_up["I"])
    ]
    for i, (h, a) in enumerate(mappings):
        if r32[i].home_team != h or r32[i].away_team != a:
            clear_match_state(r32[i])
            r32[i].home_team, r32[i].away_team = h, a

    # Cascading Propagation
    def propagate(prev_round, curr_round):
        for i in range(len(curr_round)):
            m1, m2 = prev_round[i*2], prev_round[i*2+1]
            h = st.session_state.teams.get(m1.winner_id) if m1.is_played else None
            a = st.session_state.teams.get(m2.winner_id) if m2.is_played else None
            if curr_round[i].home_team != h or curr_round[i].away_team != a:
                clear_match_state(curr_round[i])
                curr_round[i].home_team, curr_round[i].away_team = h, a

    propagate(r32, st.session_state.knockout["R16"])
    propagate(st.session_state.knockout["R16"], st.session_state.knockout["QF"])
    propagate(st.session_state.knockout["QF"], st.session_state.knockout["SF"])
    
    sf = st.session_state.knockout["SF"]
    wf_h = st.session_state.teams.get(sf[0].winner_id) if sf[0].is_played else None
    wf_a = st.session_state.teams.get(sf[1].winner_id) if sf[1].is_played else None
    if st.session_state.knockout["F"][0].home_team != wf_h or st.session_state.knockout["F"][0].away_team != wf_a:
        clear_match_state(st.session_state.knockout["F"][0])
        st.session_state.knockout["F"][0].home_team, st.session_state.knockout["F"][0].away_team = wf_h, wf_a

    ltp_h = (sf[0].home_team if sf[0].winner_id == sf[0].away_team.id else sf[0].away_team) if sf[0].is_played else None
    ltp_a = (sf[1].home_team if sf[1].winner_id == sf[1].away_team.id else sf[1].away_team) if sf[1].is_played else None
    if st.session_state.knockout["TP"][0].home_team != ltp_h or st.session_state.knockout["TP"][0].away_team != ltp_a:
        clear_match_state(st.session_state.knockout["TP"][0])
        st.session_state.knockout["TP"][0].home_team, st.session_state.knockout["TP"][0].away_team = ltp_h, ltp_a

# --- 5. SIMULATION ---

def simulate_match_logic(match: Match) -> Tuple[int, int]:
    diff = match.away_team.fifa_ranking - match.home_team.fifa_ranking
    goal_range = [0, 1, 2, 3, 4, 5]
    def w(adj):
        if adj > 20: return [2, 5, 10, 8, 4, 1]
        elif adj > 5: return [5, 10, 8, 4, 2, 1]
        elif adj < -20: return [15, 5, 1, 0.5, 0.1, 0]
        return [10, 8, 5, 2, 1, 0.5]
    return random.choices(goal_range, weights=w(diff))[0], random.choices(goal_range, weights=w(-diff))[0]

def simulate_knockout(m: Match):
    if not m.home_team or not m.away_team: return
    h, a = simulate_match_logic(m)
    m.home_score, m.away_score = h, a
    m.is_played = True
    if h == a:
        hp, ap = random.randint(3, 5), random.randint(3, 5)
        while hp == ap: ap = random.randint(3, 5)
        m.home_penalties, m.away_penalties = hp, ap
        m.winner_id = m.home_team.id if hp > ap else m.away_team.id
    else:
        m.home_penalties, m.away_penalties = None, None
        m.winner_id = m.home_team.id if h > a else m.away_team.id
    for prefix, val in [("score_h_", m.home_score), ("score_a_", m.away_score), ("played_", True), ("winner_", m.winner_id), ("pen_h_", m.home_penalties), ("pen_a_", m.away_penalties)]:
        st.session_state[f"{prefix}{m.id}"] = val

def run_full_sim():
    for m in st.session_state.matches.values():
        h, a = simulate_match_logic(m)
        st.session_state[f"score_h_{m.id}"], st.session_state[f"score_a_{m.id}"], st.session_state[f"played_{m.id}"] = h, a, True
    sync_state(); update_bracket()
    for r in ["R32", "R16", "QF", "SF", "TP", "F"]:
        for m in st.session_state.knockout[r]: simulate_knockout(m); sync_state(); update_bracket()
    st.rerun()

# --- 6. UI ---

def render_match(m: Match, is_ko=False):
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns([5, 2, 2, 5])
        t1, t2 = m.home_team, m.away_team
        with c1: st.markdown(f"<div style='font-weight: bold;'>{t1.name if t1 else 'TBD'}</div>", unsafe_allow_html=True)
        with c2: h = st.number_input("H", 0, 15, key=f"score_h_{m.id}", label_visibility="collapsed")
        with c3: a = st.number_input("A", 0, 15, key=f"score_a_{m.id}", label_visibility="collapsed")
        with c4: st.markdown(f"<div style='font-weight: bold; text-align: right;'>{t2.name if t2 else 'TBD'}</div>", unsafe_allow_html=True)
        
        if t1 and t2:
            is_draw = h == a
            # Penalty logic gated strictly for knockout stage
            ph, pa = 0, 0
            if is_ko and is_draw:
                st.caption("Draw! Enter Penalty Shootout score:")
                cp1, cp2 = st.columns(2)
                with cp1:
                    ph_s = st.text_input("H Pens", value=str(st.session_state.get(f"pen_h_{m.id}", 0)), key=f"ui_pen_h_{m.id}", label_visibility="collapsed")
                    ph = int(ph_s) if ph_s.isdigit() else 0
                    st.session_state[f"pen_h_{m.id}"] = ph
                with cp2:
                    pa_s = st.text_input("A Pens", value=str(st.session_state.get(f"pen_a_{m.id}", 0)), key=f"ui_pen_a_{m.id}", label_visibility="collapsed")
                    pa = int(pa_s) if pa_s.isdigit() else 0
                    st.session_state[f"pen_a_{m.id}"] = pa
            
            if st.session_state.get(f"played_{m.id}", False):
                if is_ko:
                    # Knockout display: With advancing team
                    if h > a: winner = t1
                    elif a > h: winner = t2
                    else:
                        sph, spa = st.session_state.get(f"pen_h_{m.id}", 0), st.session_state.get(f"pen_a_{m.id}", 0)
                        winner = t1 if sph > spa else t2
                    pen_txt = f" ({st.session_state.get(f'pen_h_{m.id}', 0)}) : ({st.session_state.get(f'pen_a_{m.id}', 0)}) " if h == a else " : "
                    st.markdown(f"<div style='text-align: center; color: #00c853; font-size: 0.9rem;'>✅ {h}{pen_txt}{a} ({winner.name} advances)</div>", unsafe_allow_html=True)
                else:
                    # Group stage display: Clean Match Completed status
                    st.markdown(f"<div style='text-align: center; color: #00c853; font-size: 0.9rem;'>✅ Match Completed ({h} : {a})</div>", unsafe_allow_html=True)
            else:
                if st.button("Confirm", key=f"btn_{m.id}", use_container_width=True):
                    if is_ko and is_draw and ph == pa:
                        st.error("Penalties cannot end in a draw!")
                    else:
                        st.session_state[f"played_{m.id}"] = True
                        if is_ko:
                            if h > a: win_id = t1.id
                            elif a > h: win_id = t2.id
                            else: win_id = t1.id if ph > pa else t2.id
                            st.session_state[f"winner_{m.id}"] = win_id
                        st.rerun()

def main():
    st.set_page_config(page_title="2026 World Cup Pro", layout="wide")
    init_state(); sync_state(); update_bracket()
    st.title("🏆 2026 World Cup Simulator")
    
    with st.sidebar:
        if st.button("🎲 Simulate All (Reset & Run)", use_container_width=True, type="primary"): run_full_sim()
        if st.button("🤖 Auto-Simulate Remaining", use_container_width=True):
            for m in st.session_state.matches.values():
                if not st.session_state.get(f"played_{m.id}", False):
                    h, a = simulate_match_logic(m)
                    st.session_state[f"score_h_{m.id}"], st.session_state[f"score_a_{m.id}"], st.session_state[f"played_{m.id}"] = h, a, True
            sync_state(); update_bracket()
            for r in ["R32", "R16", "QF", "SF", "TP", "F"]:
                for m in st.session_state.knockout[r]:
                    if m.home_team and m.away_team and not st.session_state.get(f"played_{m.id}", False):
                        simulate_knockout(m); sync_state(); update_bracket()
            st.rerun()
        if st.button("🔄 Reset Tournament", use_container_width=True):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()

    g_tabs = st.tabs([f"Group {gid}" for gid in st.session_state.groups.keys()])
    for i, (gid, group) in enumerate(st.session_state.groups.items()):
        with g_tabs[i]:
            c_t, c_m = st.columns([1, 1])
            with c_t:
                st.subheader("Live Standings")
                st.dataframe(calculate_standings(group, st.session_state.matches).drop(columns=['id']), hide_index=True, use_container_width=True)
            with c_m:
                st.subheader("Fixtures")
                for mid, m in st.session_state.matches.items():
                    if m.group_id == gid: render_match(m)

    if all(m.is_played for m in st.session_state.matches.values()):
        st.divider(); st.header("🏁 Knockout Stage")
        k_tabs = st.tabs(["Round of 32", "Round of 16", "Quarter-finals", "Semi-finals", "Finals"])
        for i, r in enumerate(["R32", "R16", "QF", "SF", "F"]):
            with k_tabs[i]:
                cols = st.columns(2)
                for idx, m in enumerate(st.session_state.knockout[r]):
                    with cols[idx % 2]: render_match(m, is_ko=True)
                if r == "F":
                    st.write("---"); st.subheader("🥉 Third Place Playoff")
                    c_tp = st.columns(2)
                    with c_tp[0]: render_match(st.session_state.knockout["TP"][0], is_ko=True)
                    f = st.session_state.knockout["F"][0]
                    if f.is_played:
                        st.markdown(f"<div style='background-color: #ffd700; padding: 20px; border-radius: 10px;'><h1 style='text-align: center; color: black;'>👑 WORLD CHAMPION: {st.session_state.teams[f.winner_id].name} 🏆</h1></div>", unsafe_allow_html=True)
    else: st.info("Complete the group stage to unlock knockouts.")

if __name__ == "__main__": main()
